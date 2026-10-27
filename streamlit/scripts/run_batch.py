# run_batch.py
#
# Run an AI Argue batch and write one row per debate to data/debates.db.
# Runs on the Mac (poe), not walle.
#
#   python scripts/run_batch.py --config scripts/batch1.json
#   python scripts/run_batch.py --config scripts/batch1.json --dry-run --price
#
# Config (JSON, or YAML if PyYAML is installed):
#   {
#     "batch_id": "batch1",
#     "proposition": "...",
#     "rounds": 3,
#     "defaults": {"model_j": "gpt-5-mini", "words_j1": 30, "words_j8": 100},
#     "conditions": [
#       {"id": "S1", "model_a": "...", "model_b": "...", "words_a": 25, "words_b": 25, "reps": 20},
#       ...
#     ]
#   }
# Any condition key can also go in "defaults"; a condition overrides it.
#
# Resumable: reps already in the db for this batch_id are skipped.
# --rerun-failed re-runs, once, any rep whose only row ended "error" or "unparsed".

import argparse
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_argue_core import run_debate  # noqa: E402
import ai_argue_store  # noqa: E402

REQUIRED_KEYS = ["id", "proposition", "model_a", "model_b", "model_j",
                 "words_a", "words_b", "words_j1", "words_j8", "rounds", "reps"]

# USD per million tokens (input, output). Estimates only; check current pricing pages.
PRICES = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5-nano": (0.05, 0.40),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
}


def load_config(path):
    text = Path(path).read_text()
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            sys.exit("YAML config needs PyYAML (pip install pyyaml), or use a .json config.")
        config = yaml.safe_load(text)
    else:
        config = json.loads(text)

    base = {"proposition": config.get("proposition"), "rounds": config.get("rounds", 3)}
    base.update(config.get("defaults", {}))
    conditions = []
    for cond in config["conditions"]:
        merged = {**base, **cond}
        missing = [k for k in REQUIRED_KEYS if merged.get(k) in (None, "")]
        if missing:
            sys.exit(f"Condition {cond.get('id')!r} is missing: {', '.join(missing)}")
        conditions.append(merged)
    return config["batch_id"], conditions


def price(model):
    for prefix, p in PRICES.items():
        if model.startswith(prefix):
            return p
    return None


def debate_args(cond):
    return dict(
        proposition=cond["proposition"],
        model_a=cond["model_a"], model_b=cond["model_b"], model_j=cond["model_j"],
        words_a=cond["words_a"], words_b=cond["words_b"],
        words_j1=cond["words_j1"], words_j8=cond["words_j8"],
        rounds=cond["rounds"],
    )


def estimate_batch_cost(sample, sample_cond, conditions):
    """Estimate each condition's cost from the per-call token usage of one sample debate.

    Each call's tokens are priced at the model in that seat for the condition. A and B output
    tokens are scaled by the word-budget ratio to the sample; input tokens are not scaled.
    """
    total = 0.0
    lines = []
    for cond in conditions:
        per_debate = 0.0
        for u in sample["usage"]:
            step = u["step"]
            if step in ("guidelines", "ruling"):
                model, scale = cond["model_j"], 1.0
            elif step == "A":
                model, scale = cond["model_a"], cond["words_a"] / sample_cond["words_a"]
            else:
                model, scale = cond["model_b"], cond["words_b"] / sample_cond["words_b"]
            p = price(model)
            if p is None:
                print(f"  (no price for {model}; counted as $0)")
                continue
            per_debate += (u["tokens_in"] * p[0] + u["tokens_out"] * scale * p[1]) / 1_000_000
        cond_cost = per_debate * cond["reps"]
        total += cond_cost
        lines.append(f"  {cond['id']:<8} {cond['reps']:>3} reps x ${per_debate:.4f} = ${cond_cost:.2f}")
    return total, lines


def dry_run(conditions, show_price):
    cond = conditions[0]
    print(f"Dry run: one debate for condition {cond['id']} (nothing is written to the db)")
    t0 = time.time()
    result = run_debate(**debate_args(cond))
    print(f"status={result['status']} winner={result['winner']} ({time.time() - t0:.0f}s)")
    if result["error"]:
        print(f"error: {result['error']}")
    for s in result["statements"]:
        print(f"  [{s['step']} r{s['round']}] {s['text']}")
    print("Token usage:")
    for u in result["usage"]:
        print(f"  {u['step']:<10} r{u['round']}  {u['model']:<28} in={u['tokens_in']:>5} out={u['tokens_out']:>5}")
    print(f"  total in={result['tokens_in']} out={result['tokens_out']}")

    if show_price:
        total, lines = estimate_batch_cost(result, cond, conditions)
        n = sum(c["reps"] for c in conditions)
        print(f"Estimated cost for the full batch ({n} debates):")
        print("\n".join(lines))
        print(f"  TOTAL ~ ${total:.2f}")


def run(batch_id, conditions, rerun_failed):
    conn = ai_argue_store.connect(ai_argue_store.CURATED_DB)
    existing = ai_argue_store.rows_for_batch(conn, batch_id)

    todo = []
    for cond in conditions:
        for rep in range(1, cond["reps"] + 1):
            rows = existing.get((cond["id"], rep), [])
            if not rows:
                todo.append((cond, rep))
            elif rerun_failed and len(rows) == 1 and (rows[0][0] == "error" or rows[0][1] == "unparsed"):
                todo.append((cond, rep))

    print(f"Batch {batch_id}: {len(todo)} debates to run "
          f"({sum(c['reps'] for c in conditions)} planned, {len(existing)} reps already in the db)")

    counts = {}
    for i, (cond, rep) in enumerate(todo, 1):
        t0 = time.time()
        result = run_debate(**debate_args(cond))
        ai_argue_store.insert_row(conn, ai_argue_store.make_row(
            result, source="batch", batch_id=batch_id, condition=cond["id"], rep=rep))
        outcome = result["status"] if result["status"] == "error" else result["winner"]
        counts[outcome] = counts.get(outcome, 0) + 1
        print(f"[{i}/{len(todo)}] {cond['id']} rep {rep}: {outcome} "
              f"(tokens in={result['tokens_in']} out={result['tokens_out']}, {time.time() - t0:.0f}s)", flush=True)

    conn.close()
    print(f"Done. Outcomes this run: {counts}")


def main():
    parser = argparse.ArgumentParser(description="Run an AI Argue batch into data/debates.db")
    parser.add_argument("--config", required=True, help="batch config (.json, or .yaml with PyYAML)")
    parser.add_argument("--dry-run", action="store_true", help="run one debate, write nothing")
    parser.add_argument("--price", action="store_true", help="with --dry-run: estimate the full batch's cost")
    parser.add_argument("--rerun-failed", action="store_true",
                        help="re-run once any rep whose only row ended error/unparsed")
    args = parser.parse_args()

    load_dotenv()
    batch_id, conditions = load_config(args.config)

    if args.price and not args.dry_run:
        parser.error("--price needs --dry-run")
    if args.dry_run:
        dry_run(conditions, args.price)
    else:
        run(batch_id, conditions, args.rerun_failed)


if __name__ == "__main__":
    main()
