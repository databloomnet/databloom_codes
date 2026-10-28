# server.py
#
# Public, read-only MCP server over the curated AI Argue dataset (streamlit/data/debates.db).
# Streamable HTTP on 127.0.0.1:8000/mcp, stateless with JSON responses; Nginx fronts it at
# https://apps.databloom.net/mcp. Never touches web_runs.db and has no write tools.
#
# mcp 2.x renamed FastMCP to MCPServer (mcp.server.mcpserver); the API is otherwise the same shape.

import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp_types import ToolAnnotations

DB_PATH = (Path(__file__).resolve().parent / ".." / "streamlit" / "data" / "debates.db").resolve()

HOST = "127.0.0.1"
PORT = 8000
PUBLIC_HOST = "apps.databloom.net"

REPO = "https://github.com/databloomnet/databloom_codes/blob/main"
LINKS = {
    "preregistration_batch1": REPO + "/docs/ai-argue-preregistration-2026-10-27.md",
    "preregistration_batch2": REPO + "/docs/ai-argue-preregistration-batch2-2026-10-27.md",
    "preregistration_batch3": REPO + "/docs/ai-argue-preregistration-batch3-2026-10-28.md",
    "results": REPO + "/docs/ai-argue-results-2026-10-27.md",
    "app": "https://apps.databloom.net/ai-argue",
}

# The weaker of the two debater models, for wordcap_effect.
WEAKER_MODEL = "claude-haiku-4-5-20251001"
IDENTICAL_CONDITIONS = ("S1", "S1-inv", "S1-rev")

SUMMARY_COLUMNS = [
    "run_id", "batch_id", "condition", "rep", "timestamp_utc", "proposition",
    "model_a", "model_b", "model_j", "words_a", "words_b", "first_speaker", "winner", "status",
]

COLUMN_MEANINGS = {
    "run_id": "Unique id of one debate run (UUID). Pass it to get_debate.",
    "batch_id": "Pre-registered batch: batch1, batch2 or batch3.",
    "condition": "Experimental cell within the batch (S1, C0a, C0b, H1a, H1b, S1-inv, S1-rev).",
    "rep": "Repetition number within the condition, starting at 1.",
    "timestamp_utc": "When the debate finished (ISO 8601, UTC).",
    "proposition": "The proposition debated.",
    "model_a": "Debater in seat A: argues FOR the proposition.",
    "model_b": "Debater in seat B: argues AGAINST the proposition.",
    "first_speaker": "Which seat spoke first: 'A' in batches 1–2, 'B' in batch 3.",
    "model_j": "Judge model.",
    "words_a": "Word budget per statement for seat A.",
    "words_b": "Word budget per statement for seat B.",
    "words_j_guidelines": "Word budget for the judge's opening guidelines.",
    "words_j_ruling": "Word budget for the judge's final ruling.",
    "rounds": "Number of debate rounds (one statement from each seat per round, first_speaker first).",
    "temperature": "Sampling temperature ('default' = provider default).",
    "winner": "'A', 'B', or 'unparsed' (the ruling lacked a WINNER: line).",
    "ruling_text": "The judge's full ruling.",
    "transcript_json": "Every statement in speaking order: judge guidelines, A/B per round (first_speaker first), ruling; plus token usage.",
    "judge_prompt_hash": "Hash of the judge prompt, to confirm all runs used the same one.",
    "judge_disclosed_word_limits": "1 if the judge was told both debaters' word limits.",
    "tokens_in": "Total input tokens across all calls in the debate.",
    "tokens_out": "Total output tokens across all calls in the debate.",
    "status": "'ok' or an error status.",
    "source": "'batch' for scripted runs.",
}

LATEST_SQL = """
    SELECT * FROM (
        SELECT *, ROW_NUMBER() OVER (
            PARTITION BY batch_id, condition, rep ORDER BY timestamp_utc DESC
        ) AS rn
        FROM debates
    ) WHERE rn = 1
"""

SEAT_CONVENTION = "A argues FOR, B argues AGAINST. A spoke first in batches 1–2; in batch 3, B spoke first (see first_speaker)."

STAT_NAMES = ["seat_bias", "judge_stability", "wordcap_effect", "model_strength_matrix"]

INSTRUCTIONS = (
    "Read-only access to the AI Argue dataset from databloom.net: LLM debates judged by an LLM. "
    "Seat A argues FOR the proposition; seat B argues AGAINST. A spoke first in batches 1–2; "
    "in batch 3, B spoke first (see first_speaker). "
    "Start with dataset_info, then list_debates / get_debate for individual debates and "
    "query_stats for the headline aggregations."
)

mcp = MCPServer(name="ai-argue", title="AI Argue dataset", instructions=INSTRUCTIONS)
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)


def _connect():
    conn = sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _latest_rows(conn):
    return [dict(r) for r in conn.execute(LATEST_SQL + " ORDER BY batch_id, condition, rep")]


def _tally(rows):
    out = {"n": len(rows), "A": 0, "B": 0, "unparsed": 0}
    for r in rows:
        key = r["winner"] if r["winner"] in ("A", "B") else "unparsed"
        out[key] += 1
    return out


def _binom_two_sided(k, n):
    """Exact two-sided binomial p-value against a fair coin."""
    if n == 0:
        return None
    probs = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in probs if p <= probs[k] * (1 + 1e-9)))


@mcp.tool(annotations=READ_ONLY)
def dataset_info() -> dict:
    """Describe the AI Argue dataset. Call this first.

    Returns: row counts (raw and latest-per-rep), each batch with its proposition, each
    condition with its models, word budgets and verdict tally, the meaning of every column,
    the seat convention, and links to the pre-registrations and results writeup.

    Seat convention: A argues FOR, B argues AGAINST. A spoke first in batches 1–2; in
    batch 3, B spoke first (see first_speaker). The judge must name one winner.

    Some batch-1 rulings omitted the WINNER: line ('unparsed') and were re-run once, as the
    pre-registration specified, so a few (batch_id, condition, rep) keys have two rows. Every
    analysis uses only the latest row per key; raw_rows counts all of them.
    """
    with closing(_connect()) as conn:
        raw = conn.execute("SELECT COUNT(*) FROM debates").fetchone()[0]
        latest = _latest_rows(conn)
    batches = {}
    for r in latest:
        b = batches.setdefault(r["batch_id"], {"proposition": r["proposition"], "conditions": {}})
        c = b["conditions"].setdefault(r["condition"], {
            "model_a": r["model_a"], "words_a": r["words_a"],
            "model_b": r["model_b"], "words_b": r["words_b"],
            "model_j": r["model_j"], "rounds": r["rounds"], "first_speaker": r["first_speaker"], "rows": [],
        })
        c["rows"].append(r)
    for b in batches.values():
        for c in b["conditions"].values():
            c["verdicts"] = _tally(c.pop("rows"))
    return {
        "raw_rows": raw,
        "latest_rows": len(latest),
        "rule": "latest row per (batch_id, condition, rep) by timestamp_utc",
        "seat_convention": {
            "A": "argues FOR the proposition",
            "B": "argues AGAINST the proposition",
            "order": "A spoke first in batches 1–2; in batch 3, B spoke first (see first_speaker).",
        },
        "batches": batches,
        "columns": COLUMN_MEANINGS,
        "stats_available": STAT_NAMES,
        "links": LINKS,
    }


@mcp.tool(annotations=READ_ONLY)
def list_debates(
    batch_id: str | None = None,
    condition: str | None = None,
    model: str | None = None,
    judge: str | None = None,
    winner: str | None = None,
    limit: int = 50,
    include_history: bool = False,
) -> dict:
    """List debates as summary rows (no transcripts or rulings; use get_debate for those).

    Filters (all optional, combined with AND):
      batch_id: exact, e.g. 'batch1', 'batch2' or 'batch3'.
      condition: exact, e.g. 'S1', 'S1-inv', 'S1-rev', 'C0a', 'C0b', 'H1a', 'H1b'.
      model: case-insensitive substring matched against EITHER seat, e.g. 'haiku' or
             'claude-sonnet-4-5-20250929'.
      judge: case-insensitive substring of the judge model, e.g. 'gpt-5-mini'.
      winner: 'A', 'B' or 'unparsed'.
      limit: max rows returned, default 50, capped at 200.
      include_history: False (default) returns only the latest row per (batch_id, condition,
             rep), the rows every analysis uses. True also returns superseded rows (rulings
             that were unparsed and re-run).

    A argues FOR, B argues AGAINST. A spoke first in batches 1–2; in batch 3, B spoke first (see first_speaker).
    Returns {"total_matching", "returned", "rows"}, ordered by batch, condition, rep, time.
    """
    limit = max(1, min(int(limit), 200))
    where, params = [], []
    if batch_id:
        where.append("batch_id = ?")
        params.append(batch_id)
    if condition:
        where.append("condition = ?")
        params.append(condition)
    if model:
        where.append("(LOWER(model_a) LIKE ? OR LOWER(model_b) LIKE ?)")
        params += ["%" + model.lower() + "%"] * 2
    if judge:
        where.append("LOWER(model_j) LIKE ?")
        params.append("%" + judge.lower() + "%")
    if winner:
        where.append("winner = ?")
        params.append(winner)
    source = "debates" if include_history else "(" + LATEST_SQL + ")"
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    with closing(_connect()) as conn:
        total = conn.execute("SELECT COUNT(*) FROM " + source + clause, params).fetchone()[0]
        cur = conn.execute(
            "SELECT " + ", ".join(SUMMARY_COLUMNS) + " FROM " + source + clause
            + " ORDER BY batch_id, condition, rep, timestamp_utc LIMIT ?",
            params + [limit],
        )
        rows = [dict(r) for r in cur]
    return {"total_matching": total, "returned": len(rows), "rows": rows}


@mcp.tool(annotations=READ_ONLY)
def get_debate(run_id: str) -> dict:
    """Get one debate in full: every column, the judge's ruling text, and the parsed transcript.

    run_id comes from list_debates. transcript.statements is in speaking order: the judge's
    guidelines (step 'guidelines', round 0), then A and B for each round (first_speaker
    first), then the ruling.
    A argues FOR, B argues AGAINST. A spoke first in batches 1–2; in batch 3, B spoke first (see first_speaker).
    is_latest is False if this row was superseded by a re-run of the same rep (only the
    latest row counts in the analyses).
    """
    with closing(_connect()) as conn:
        row = conn.execute("SELECT * FROM debates WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            return {"error": "No debate with run_id " + repr(run_id) + ". Use list_debates to find ids."}
        row = dict(row)
        newer = conn.execute(
            "SELECT COUNT(*) FROM debates WHERE batch_id IS ? AND condition IS ? AND rep IS ?"
            " AND timestamp_utc > ?",
            (row["batch_id"], row["condition"], row["rep"], row["timestamp_utc"]),
        ).fetchone()[0]
    row["transcript"] = json.loads(row.pop("transcript_json") or "null")
    row["is_latest"] = newer == 0
    return row


def _seat_bias(rows):
    by_cond = {}
    for r in rows:
        by_cond.setdefault((r["batch_id"], r["condition"]), []).append(r)
    conditions = []
    for (batch, cond), rs in sorted(by_cond.items()):
        t = _tally(rs)
        conditions.append({
            "batch_id": batch, "condition": cond,
            "model_a": rs[0]["model_a"], "words_a": rs[0]["words_a"],
            "model_b": rs[0]["model_b"], "words_b": rs[0]["words_b"],
            "first_speaker": rs[0]["first_speaker"],
            "a_wins": t["A"], "b_wins": t["B"], "unparsed": t["unparsed"], "n": t["n"],
        })
    ident = _tally([r for r in rows if r["condition"] in IDENTICAL_CONDITIONS])
    return {
        "description": "A/B wins per condition (latest row per rep). " + SEAT_CONVENTION,
        "conditions": conditions,
        "identical_debaters": {
            "conditions": list(IDENTICAL_CONDITIONS),
            "a_wins": ident["A"], "b_wins": ident["B"], "unparsed": ident["unparsed"], "n": ident["n"],
            "b_share": round(ident["B"] / ident["n"], 3) if ident["n"] else None,
            "p_two_sided_fair_coin": _binom_two_sided(ident["B"], ident["A"] + ident["B"]),
        },
    }


def _judge_stability(rows):
    out = []
    for cond in IDENTICAL_CONDITIONS:
        rs = [r for r in rows if r["condition"] == cond]
        if not rs:
            continue
        t = _tally(rs)
        out.append({
            "batch_id": rs[0]["batch_id"], "condition": cond, "proposition": rs[0]["proposition"],
            "model_a": rs[0]["model_a"], "model_b": rs[0]["model_b"], "judge": rs[0]["model_j"],
            "first_speaker": rs[0]["first_speaker"],
            "a_wins": t["A"], "b_wins": t["B"], "unparsed": t["unparsed"], "n": t["n"],
            "b_share": round(t["B"] / t["n"], 3) if t["n"] else None,
            "p_two_sided_fair_coin": _binom_two_sided(t["B"], t["A"] + t["B"]),
        })
    return {
        "description": "Verdict distributions when both seats hold the same model and budget. "
                       "S1-inv inverts the proposition, so seat B argues the opposite content "
                       "from S1. S1-rev keeps S1's proposition but B speaks first. "
                       "A fair judge should be near 50/50 in each.",
        "conditions": out,
    }


def _wordcap_effect(rows):
    cells = {}
    for r in rows:
        if r["model_a"] == r["model_b"] or WEAKER_MODEL not in (r["model_a"], r["model_b"]):
            continue
        seat = "A" if r["model_a"] == WEAKER_MODEL else "B"
        own = r["words_a"] if seat == "A" else r["words_b"]
        other = r["words_b"] if seat == "A" else r["words_a"]
        budget = "equal (C0)" if own == other else "{:g}x (H1)".format(own / other)
        c = cells.setdefault((budget, seat), {
            "budget": budget, "weaker_model_seat": seat, "weaker_model_words": own,
            "opponent_words": other, "conditions": set(), "wins": 0, "n": 0,
        })
        c["conditions"].add(r["condition"])
        c["n"] += 1
        c["wins"] += r["winner"] == seat
    by_seat = sorted(cells.values(), key=lambda c: (c["weaker_model_words"], c["weaker_model_seat"]))
    totals = {}
    for c in by_seat:
        c["conditions"] = sorted(c["conditions"])
        c["win_rate"] = round(c["wins"] / c["n"], 3)
        t = totals.setdefault(c["budget"], {"budget": c["budget"], "wins": 0, "n": 0})
        t["wins"] += c["wins"]
        t["n"] += c["n"]
    for t in totals.values():
        t["win_rate"] = round(t["wins"] / t["n"], 3)
    return {
        "description": "Win rate of the weaker model against the stronger one, at equal word "
                       "budgets versus a larger budget for the weaker model, split by its seat. "
                       "Unparsed verdicts count as non-wins.",
        "weaker_model": WEAKER_MODEL,
        "by_budget": list(totals.values()),
        "by_budget_and_seat": by_seat,
    }


def _model_strength_matrix(rows):
    cells = {}
    for r in rows:
        for seat in ("A", "B"):
            model = r["model_" + seat.lower()]
            words = r["words_" + seat.lower()]
            c = cells.setdefault((model, words, seat), {
                "model": model, "words": words, "seat": seat, "wins": 0, "n": 0,
            })
            c["n"] += 1
            c["wins"] += r["winner"] == seat
    out = sorted(cells.values(), key=lambda c: (c["model"], c["words"], c["seat"]))
    for c in out:
        c["win_rate"] = round(c["wins"] / c["n"], 3)
    return {
        "description": "Each debate contributes one appearance per seat. Win rate = wins / n for "
                       "that model at that per-statement word budget in that seat. Includes "
                       "same-model debates (S1, S1-inv, S1-rev). Unparsed verdicts count as non-wins.",
        "cells": out,
    }


STATS = {
    "seat_bias": _seat_bias,
    "judge_stability": _judge_stability,
    "wordcap_effect": _wordcap_effect,
    "model_strength_matrix": _model_strength_matrix,
}


@mcp.tool(annotations=READ_ONLY)
def query_stats(name: str) -> dict:
    """Run a named aggregation over the latest row per (batch_id, condition, rep).

    name is one of:
      seat_bias: A and B wins per condition, plus combined totals for the identical-debater
          conditions (S1, S1-inv and S1-rev) with a fair-coin p-value.
      judge_stability: verdict distributions for S1, S1-inv and S1-rev separately (same model
          in both seats; the proposition is inverted in S1-inv; B speaks first in S1-rev).
      wordcap_effect: the weaker model's (Haiku's) win rate against Sonnet at equal word
          budgets (C0a/C0b) versus a 4x budget (H1a/H1b), split by the seat it held.
      model_strength_matrix: model x per-statement word budget x seat -> wins, n, win_rate.

    A argues FOR, B argues AGAINST. A spoke first in batches 1–2; in batch 3, B spoke first (see first_speaker).
    An unknown name returns {"error", "valid_names"}.
    """
    fn = STATS.get(name)
    if fn is None:
        return {"error": "Unknown stat " + repr(name) + ".", "valid_names": STAT_NAMES}
    with closing(_connect()) as conn:
        rows = _latest_rows(conn)
    return {"name": name, **fn(rows)}


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=HOST,
        port=PORT,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[PUBLIC_HOST, HOST + ":" + str(PORT), "localhost:" + str(PORT)],
            allowed_origins=["https://" + PUBLIC_HOST, "http://127.0.0.1:*", "http://localhost:*"],
        ),
    )
