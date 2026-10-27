# AI Argue: pre-registration, batch 2 (seat versus content)

**Status: FINAL, 2026-10-27.** Locked before any batch-2 run. Follows batch 1 (`ai-argue-preregistration-2026-10-27.md`, Amendment 1).

## Why

In batch 1, with identical debaters (Haiku against Haiku, 25 words each), seat B won 20 of 20. Seat B was the *against* side, the second speaker, and the side asserting that the trolley problem has a correct answer. The judge's reasons repeatedly praised B's "clear, action-guiding principle". Batch 2 separates **seat** (B, against, second) from **content** (the decisive side) by inverting the proposition, which puts the decisive side in seat A.

## Design

- Proposition: **"there is a correct answer to the trolley problem"**. A now argues *for* a correct answer; B argues there is none.
- One cell, **S1-inv**: Haiku 4.5 against Haiku 4.5, 25 words each, **20 reps**.
- Everything else as in batch 1: 3 rounds, judge `gpt-5-mini`, judge guidelines 30 words and ruling 100 words, provider-default temperature, word limits disclosed, forced-binary ruling.
- Parsing: the `WINNER:` line, with the fallback from batch-1 Amendment 1 (a ruling opening "A wins"/"B wins").
- Config: `streamlit/scripts/batch2.json`, `batch_id = batch2`.

## Decision rule (set before running)

| Result | Reading |
|---|---|
| B wins ≥ 15 of 20 | **Seat/order effect.** The judge favors the second speaker or the against side, whatever the content. |
| A wins ≥ 15 of 20 | **Content effect.** The judge favors the decisive "there is a correct answer" side, whatever the seat. |
| Anything else | **Mixed.** Both contribute, and batch 1's B dominance is partly content. Report the split as it is. |

With 20 reps, 15 or more is well outside what an unbiased coin produces (p ≈ 0.02, one-sided).

## Stopping rule

Exactly 20 reps. An `unparsed` or `error` result is re-run once. Publish whatever the result is.

## Budget

About $0.15, based on batch 1's S1 cost.
