# AI Argue: pre-registration, batch 3 (speaking order versus role)

**Status: FINAL, 2026-10-28.** Locked before any batch-3 run. Follows batches 1 and 2 (`ai-argue-preregistration-2026-10-27.md`, `ai-argue-preregistration-batch2-2026-10-27.md`).

## Why

In batches 1 and 2, with identical debaters, the side arguing **against** the proposition won 40 of 40. That side always **spoke second**, so batches 1 and 2 can't tell whether the judge rewards the last word (speaking order) or the against role. Batch 2 already ruled out content. Batch 3 reverses the speaking order and keeps the roles.

## Design

- Proposition: **"there is no correct answer to the trolley problem"** (batch 1's original).
- One cell, **S1-rev**: Haiku 4.5 against Haiku 4.5, 25 words each, **20 reps**.
- **Seat B (against) speaks first; seat A (for) speaks second.** Seat labels keep their meaning: A always argues *for* and B always argues *against*. The new column `first_speaker` records the order (`"A"` in batches 1–2, `"B"` here).
- Everything else as in batch 2: 3 rounds, judge `gpt-5-mini`, judge guidelines 30 words and ruling 100 words, provider-default temperature, word limits disclosed, forced-binary ruling, and the batch-2 parser (WINNER line, plus the "A wins"/"B wins" fallback).
- The judge prompt changes only where it describes the speaking order, so `judge_prompt_hash` will differ from batches 1–2. That's expected.
- Config: `streamlit/scripts/batch3.json`, `batch_id = batch3`.

## Decision rule (set before running)

| Result | Reading |
|---|---|
| A wins ≥ 15 of 20 | **Order effect.** The judge rewards whoever speaks second, the last word. Batches 1–2 are a "last speaker" bias. |
| B wins ≥ 15 of 20 | **Role effect.** The judge rewards the side arguing *against*, whatever the order. Batches 1–2 are an "against" bias. |
| Anything else | **Mixed or weaker.** Speaking order and role each contribute, or the effect shrinks when they're separated. Report the split as it is. |

With 20 reps, 15 or more either way is well outside chance for a fair coin (p ≈ 0.04, two-sided).

## Stopping rule

Exactly 20 reps. An `unparsed` or `error` result is re-run once. Publish whatever the result is.

## Budget

About $0.15, the same as batch 2.
