# AI Argue batch 3: build brief for Claude Code (speaking order)

*2026-10-28. Read `CLAUDE.md` first: Python 3.11 on walle, never read `.env`. The pre-registration is `docs/ai-argue-preregistration-batch3-2026-10-28.md`; the config is `streamlit/scripts/batch3.json`, already written.*

**Goal:** let seat B (against) speak first, while A still argues *for* and B still argues *against*, and record the order. **Nothing in batches 1–2 may change:** their prompts, hash and rows must be identical after this change.

## 1. `streamlit/ai_argue_core.py`

- Add `first_speaker="A"` to `run_debate()` and `make_prompts()`. Allowed values: `"A"` (the default, today's behaviour) or `"B"`.
- When `first_speaker == "A"`, every prompt string must be **byte-identical** to today's, so `judge_prompt_hash()` for the default is unchanged. Assert this in a quick test against the hash stored in batch-1 rows (`f6159b17b91ac9cf…`).
- When `first_speaker == "B"`, rewrite only the order-describing lines of the baseline prompt (steps 5–7): B makes the first statement, against the proposition; A makes the next statement, in favor; repeat for six statements. Roles, word limits and judge instructions stay the same. In the round loop, B's turn comes before A's. The transcript records statements in actual speaking order.
- `judge_prompt_hash` should hash the template for the order actually used, so batch 3 gets its own hash.
- Return `first_speaker` in the result dict.

## 2. `streamlit/ai_argue_store.py`

- Add a column `first_speaker TEXT` to the schema.
- **Migration:** on connect, if the column is missing, run `ALTER TABLE debates ADD COLUMN first_speaker TEXT DEFAULT 'A'`. Existing rows read as `'A'`, which is correct for batches 1–2. Apply it to both `debates.db` and `web_runs.db` (the visitor log gets it when the web page next writes).
- Make `make_row()` include `first_speaker`.

## 3. `streamlit/scripts/run_batch.py`

- Pass an optional per-condition or `defaults` key `first_speaker` (default `"A"`) through to `run_debate()`. Include it in `--dry-run` output.

## 4. `streamlit/pages/010_ai-argue.py`

- No UI change. The page keeps `first_speaker="A"`.

## 5. `mcp/server.py`

- Add `first_speaker` to `SUMMARY_COLUMNS` and `COLUMN_MEANINGS`: "Which seat spoke first: 'A' in batches 1–2, 'B' in batch 3."
- Fix the seat-convention text in `INSTRUCTIONS`, `dataset_info`, and the docstrings: "A argues FOR, B argues AGAINST. A spoke first in batches 1–2; in batch 3, B spoke first (see first_speaker)."
- Add `"S1-rev"` to `IDENTICAL_CONDITIONS`.
- Add a `LINKS` entry for the batch-3 pre-registration.

## 6. Test, commit, push. Don't run the batch.

- Unit check: the default-order hash equals `f6159b17b91ac9cf…`, and a `first_speaker="B"` dry-run transcript starts B, A, B, A…
- `python scripts/run_batch.py --config scripts/batch3.json --dry-run --price`, then show the transcript order.
- Commit the code changes **together with** the batch-3 pre-registration and config, then push. Jeremy runs the batch.
