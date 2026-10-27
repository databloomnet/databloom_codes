# AI Argue: pre-registration, batch 1

**Status: FINAL, 2026-10-27.** Locked before any batch-1 run. The commit timestamp of this file is the record. Changes after the first run go in a dated amendment section below, never as edits to this text.
Design reference: `brand/ai-argue-experiment-spec.md` (Sept 25).

## Fixed parameters (all conditions)

- Proposition: **"there is no correct answer to the trolley problem"**, the same wording as the site's preset. The earlier wording, "there is no solution…", was rejected because it is false on its face, since pulling the lever is a solution. "Optimal" and "good" were also rejected, because they hand B a utilitarian 'good enough' answer. "Correct" targets the real dispute: whether the dilemma has a right answer at all.
- Rounds: 3 (six statements). Judge guidelines: 30 words. Judge ruling: 100 words.
- Temperature: provider default for every seat (gpt-5 models don't accept a temperature setting).
- The judge sees both word limits; the system prompt discloses them to all parties. `judge_disclosed_word_limits = 1`.
- The ruling is forced-binary: the judge must end with `WINNER: A` or `WINNER: B`. Ties are not allowed.
- Party A argues **for** the proposition and speaks first; B argues **against**. Position is counterbalanced by swapping which model sits in A.
- Judge model: `gpt-5-mini`. It is from a different family than both debaters, so judge self-preference is not a confound.
- Config: `streamlit/scripts/batch1.json`, `batch_id = batch1`.
- `judge_prompt_hash`: recorded per row. A prompt change means a new batch.

## Hypotheses and conditions

| Cond | Question | A | B | Reps |
|---|---|---|---|---|
| S1 | Judge stability (Exp 1) | Haiku, 25w | Haiku, 25w | 20 |
| C0a / C0b | Baseline at equal budget | Sonnet 25w vs Haiku 25w, swapped | | 10 + 10 |
| H1a / H1b | Lead: weaker model with a longer budget | Haiku 100w vs Sonnet 25w, swapped | | 10 + 10 |

**H1 (lead):** with 100 words against Sonnet's 25, Haiku wins at least 60% of H1 debates.
**Read against C0:** the effect of the budget is Haiku's H1 win rate minus its C0 win rate. A 60% H1 result means something different if Haiku already wins 50% at equal budgets.
**S1:** report the A/B split. Under a stable judge with symmetric inputs, the split is driven by position and side only, so a large deviation from 50/50 is itself the finding.

## Stopping rule

Run exactly the reps listed. No early stopping and no added reps after seeing results. Debates that end with `unparsed` or `error` are re-run once and reported in a count. Publish whatever the result is, including null results.

## Budget

About 60 debates. Price one with `--dry-run --price` before the run. If the full batch costs more than the credit available, cut all reps proportionally rather than dropping a cell.

---

## Amendment 1, 2026-10-27 (written after batch 1 ran, before any re-run)

**What happened.** 11 of 60 rulings came back `unparsed`. The judge (gpt-5-mini) skipped the required final `WINNER:` line. All 11 open with "B wins.", so none of the verdicts is ambiguous.

**What we do.** Follow the stopping rule as written: re-run each unparsed rep once with `run_batch.py --rerun-failed`. Re-runs are parsed with a fallback added to `parse_winner()` before they ran. If there's no `WINNER:` line, a ruling whose first line opens "A wins"/"B wins" counts as that verdict. For each rep, the latest row is the result.

**What we report.** The primary result is the original parsed rows plus the re-runs. As a sensitivity check, we also report the original 11 rulings classified by their "B wins." opener (all B). If the two disagree, both appear in the writeup.

**Known confound, found in the results.** Seat B is three things at once: the *against* side, the second speaker, and, for this proposition, the side asserting a correct answer exists. Batch 1 can't separate these. Batch 2 (`ai-argue-preregistration-batch2-2026-10-27.md`) tests it.

