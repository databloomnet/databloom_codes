# AI Argue: how to run a batch (the recipe)

*Written 2026-10-28 from batches 1 and 2. Follow these steps for every new experiment.*

## How the data is organised

- Everything lives in **one table, `debates`**, in `streamlit/data/debates.db`. There is one row per debate, and each row holds the setup, the outcome and the full transcript.
- **`batch_id`** groups rows into one pre-registered experiment. **`condition`** is a cell within that batch, and **`rep`** is the repetition within the cell.
- **`winner`** is the result: `A`, `B` or `unparsed`.
- **The table is append-only.** New experiments add rows under a new `batch_id`. Old rows are never edited or deleted.
- **Analyses use the latest row per `(batch_id, condition, rep)`.** A rerun replaces its original in the counts, but the original stays in the table.
- Only `scripts/run_batch.py`, run on poe, writes to `debates.db`. Website visitors' debates go to `web_runs.db` on walle instead.

## The two batches so far

| | Batch 1 | Batch 2 |
|---|---|---|
| Question | Can a weaker model win with more words? Plus judge stability | Is batch 1's seat-B bias about seat, or about content? |
| Pre-registration | `docs/ai-argue-preregistration-2026-10-27.md` (+ Amendment 1) | `docs/ai-argue-preregistration-batch2-2026-10-27.md` |
| Config | `streamlit/scripts/batch1.json` | `streamlit/scripts/batch2.json` |
| Proposition | "there is no correct answer to the trolley problem" | "there **is** a correct answer to the trolley problem" |
| Conditions | S1 (Haiku 25 vs Haiku 25, 20 reps), C0a/C0b (Sonnet vs Haiku, 25/25, 10 each), H1a/H1b (Haiku 100 vs Sonnet 25, 10 each) | S1-inv (Haiku 25 vs Haiku 25, 20 reps) |
| Judge | gpt-5-mini | gpt-5-mini |
| Debates | 60 (+11 reruns) | 20 |
| Estimated cost | $0.50 | ~$0.15 |
| Result | B won 20/20 in S1. Haiku with 100 words won 19/20 | B won 20/20, so it's a seat effect, not content |

Results: `docs/ai-argue-results-2026-10-27.md`.

## The recipe

Run commands from the folder named. zsh doesn't treat `#` as a comment when you paste commands, so don't paste lines with trailing comments.

**1. Pre-register: write the plan before running**
- Copy the batch-2 pre-registration to `docs/ai-argue-preregistration-batchN-YYYY-MM-DD.md`.
- Fill in: the question, the fixed parameters, the conditions table, the reps, the decision rule (what result means what), the stopping rule and the budget. Mark it **FINAL** with the date.

**2. Configure**
- Copy `streamlit/scripts/batch2.json` to `streamlit/scripts/batchN.json`.
- Set a **new `batch_id`**, the proposition, the judge in `defaults`, and one entry per condition (`id`, models, `words_a`/`words_b`, `reps`).
- The config can vary: models, word budgets, proposition, judge, judge word limits, rounds and reps. Anything else, such as who speaks first or hiding the word limits from the judge, needs a code change in `ai_argue_core.py` **and** a new column so the data records it. Do that change before step 3.

**3. Commit the plan (this is the proof it came first)**
```
cd ~/Dropbox/projects/databloom_codes
git add docs/ai-argue-preregistration-batchN-*.md streamlit/scripts/batchN.json
git commit -m "Batch N pre-registration"
git push
```

**4. Price it** (one sample debate, nothing written)
```
cd ~/Dropbox/projects/databloom_codes/streamlit
source .venv/bin/activate
python scripts/run_batch.py --config scripts/batchN.json --dry-run --price
```
If it costs more than your credit balance, cut reps in **every** cell proportionally. Don't drop a cell.

**5. Run it**
- **Pause Dropbox** so it doesn't sync the database mid-write.
- Run:
  ```
  caffeinate -i python scripts/run_batch.py --config scripts/batchN.json
  ```
- If anything came back `unparsed` or `error`, rerun those once:
  ```
  caffeinate -i python scripts/run_batch.py --config scripts/batchN.json --rerun-failed
  ```
- **Resume Dropbox.**

The script can be resumed: Ctrl-C partway through, run the same command again, and it skips reps already done.

**6. Check it**
```
cd ~/Dropbox/projects/databloom_codes/streamlit/data
sqlite3 -header -column debates.db "select condition, sum(winner='A') as a_wins, sum(winner='B') as b_wins, count(*) as n from (select *, row_number() over (partition by batch_id, condition, rep order by timestamp_utc desc) as rn from debates where batch_id = 'batchN') where rn = 1 group by condition"
```

**7. Ship it**
```
cd ~/Dropbox/projects/databloom_codes
git add streamlit/data/debates.db
git commit -m "Batch N results"
git push
ssh walle 'cd ~/apps && git pull && sudo systemctl restart streamlit && sudo systemctl restart databloom-mcp'
```
The Explore tab and the MCP server both read the new rows after the pull and restart.

**8. Write it up**
- Add the results to the results doc (or a new one), measured against the pre-registered decision rule.
- If anything deviated from the plan, add a dated **amendment** to the pre-registration. Never edit the original text.
- Message static (`databloomnet-primary/_to_static/`) if the public writeup page should change.

## Things that won't update by themselves

- **The MCP server's reports.** `judge_stability` only reads conditions listed in `IDENTICAL_CONDITIONS` in `mcp/server.py` (currently `S1`, `S1-inv`). `wordcap_effect` assumes `WEAKER_MODEL` is Haiku. New rows appear automatically in `list_debates`, `get_debate`, `dataset_info` and `seat_bias`. For the other two, edit those constants.
- **The `dataset_info` links.** If you add a pre-registration, add its link to `LINKS` in `mcp/server.py`.
- **The Analysis tab and charts.** They don't pick up new batches until they're updated.
