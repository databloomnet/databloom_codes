# AI Argue v1: build brief for Claude Code

*2026-10-27. Written by the databloom-apps planning thread. The full spec is in the Brand project (`ai-argue-app-v1-spec-20261027`); the experimental design is `brand/ai-argue-experiment-spec.md`. This file covers only what to build, in order.*

**Ground rules:** read `CLAUDE.md` first, especially the walle section. walle runs **Python 3.11**, so no 3.12-only syntax. Never open or print any `.env` file. Don't change the page's `url_path="ai-argue"`, because databloom.net links to it.

---

## Part 1: OpenAI fix (do first, deploy alone)

`streamlit/pages/010_ai-argue.py` `call_llm()` passes `max_tokens=` to `client.chat.completions.create`. The gpt-5 family rejects that parameter. Fix:

- For OpenAI calls, use `max_completion_tokens` (gpt-4o-mini accepts it too).
- gpt-5 models are reasoning models. Hidden reasoning tokens count against `max_completion_tokens`, so a 1000-token cap can return an **empty** message. For model ids starting `gpt-5`, pass `reasoning_effort="minimal"`. If output is still empty, raise the cap to 4000.
- Do not pass `temperature` to gpt-5 models; they reject non-default values.
- Grep the other pages (`005`–`008`) for any OpenAI `chat.completions.create(... max_tokens=...)` and fix those the same way. `chatting.py` already uses `max_completion_tokens`.
- Test locally with gpt-5-mini as A, B and J, then commit, push and deploy:
  `ssh walle 'cd ~/apps && git pull && sudo systemctl restart streamlit'`

## Part 2: extract the debate engine (no UI change)

Create `streamlit/ai_argue_core.py`. It must have no `import streamlit`.

- `run_debate(proposition, model_a, model_b, model_j, words_a, words_b, words_j1, words_j8, rounds=3) -> dict` returns the guidelines, every statement, the ruling text, the parsed `winner`, and the per-call token usage.
- Move the prompt text into it unchanged, **except** add this to the end of the judge's final-turn prompt: `End your response with a final line exactly "WINNER: A" or "WINNER: B".` Parse that line into `winner` (`"A"`, `"B"`, or `"unparsed"`).
- `judge_prompt_hash` is the sha256 of the judge's system prompt plus both judge turn templates, computed before word limits are filled in.
- Retry once on API error. If it fails again, return `status="error"`.
- Rewire `010_ai-argue.py` to call it. The page should look and behave the same as now.

## Part 3: persistence

- SQLite at `streamlit/data/debates.db`, table `debates`, one row per debate:
  `run_id` (uuid), `batch_id`, `condition`, `rep`, `timestamp_utc`, `proposition`, `model_a`, `model_b`, `model_j`, `words_a`, `words_b`, `words_j_guidelines`, `words_j_ruling`, `rounds`, `temperature` (text, `"default"`), `winner`, `ruling_text`, `transcript_json`, `judge_prompt_hash`, `judge_disclosed_word_limits` (always 1: the system prompt states both limits to all parties), `tokens_in`, `tokens_out`, `status`, `source` (`"batch"` or `"web"`).
- **There are two databases with the same schema.**
  - `data/debates.db` is **curated**. Only the batch script writes to it; it's committed to git and is the dataset analysis and MCP use.
  - `data/web_runs.db` is the **visitor log**. The page appends one row per finished debate run on the site (`source="web"`). It is **gitignored** (add `streamlit/data/web_runs.db*` to `.gitignore`), so walle writing to it never conflicts with `git pull`. Open it with `PRAGMA journal_mode=WAL`, since several Streamlit sessions may write at once. Create the table if it's missing.
  - Log only what's in the schema: no IP, no session id, no user agent.
  - Add one caption under the Run button: "Debates run here are logged anonymously for research."
  - v1 doesn't display web runs on the site. Reading them is `ssh walle` + sqlite, or a later "visitor runs" tab, once there's a moderation decision (free-text propositions shown publicly need one).
  - Back up by copying it from walle when wanted, e.g. `scp walle:~/apps/streamlit/data/web_runs.db .`. It's semi-permanent: it survives restarts and deploys, but not replacement of the instance.

## Part 4: batch script

`streamlit/scripts/run_batch.py --config <yaml|json>` runs on poe (the Mac), not walle.

- The config lists conditions: id, models, word budgets, and reps. The script runs them sequentially, writes one row per debate as it goes, prints progress, and can be resumed (it skips reps already in the db for that `batch_id`).
- `--dry-run --price` runs **one** debate and prints tokens and estimated cost for the full batch, without writing to the db.

## Part 5: page tabs

Wrap the existing page in `st.tabs(["Run a debate", "Explore results", "Analysis"])`:

- **Explore results:** read `data/debates.db` read-only (`?mode=ro` URI), show a filterable dataframe of the spec's columns, and offer CSV download.
- **Analysis:** leave a placeholder ("first results coming") until the data exists. The charts come in tomorrow's session.

Deploy after Parts 2–5. Commit `data/debates.db` once the first batch has run.

## Not today

The MCP server, the dashboard charts, and the batch tab in the UI. The MCP server is the next session.
