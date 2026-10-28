# AI Argue: results, batches 1 and 2

*2026-10-27. Pre-registrations: `ai-argue-preregistration-2026-10-27.md` (batch 1, plus Amendment 1) and `ai-argue-preregistration-batch2-2026-10-27.md`. The data is `streamlit/data/debates.db`, latest row per rep.*

Setup for every debate: 3 rounds. Seat **A** argues *for* the proposition and speaks first; seat **B** argues *against*. Judge: gpt-5-mini, forced binary verdict. Debaters: Claude Haiku 4.5 and Sonnet 4.5. 80 debates in total, with no errors.

## Results

| Cell | Proposition | A seat | B seat | A won | B won |
|---|---|---|---|---|---|
| S1 | no correct answer… | Haiku 25w | Haiku 25w | 0 | **20** |
| S1-inv | **is** a correct answer… | Haiku 25w | Haiku 25w | 0 | **20** |
| C0a | no correct answer… | Sonnet 25w | Haiku 25w | 0 | **10** |
| C0b | no correct answer… | Haiku 25w | Sonnet 25w | 3 | **7** |
| H1a | no correct answer… | **Haiku 100w** | Sonnet 25w | **9** | 1 |
| H1b | no correct answer… | Sonnet 25w | **Haiku 100w** | 0 | **10** |

## Findings

1. **The judge picks seat B.** With identical debaters, B won **40 of 40**: 20 of 20 under each wording of the proposition. Inverting the proposition changed which *content* B argued, and B still won every time. Under batch 2's pre-registered rule (B ≥ 15/20), this is a **seat/order effect**, not a content effect. Under a fair coin, 20/20 has p ≈ 2×10⁻⁶ per batch.
2. **Seat outweighs model strength.** At equal budgets, seat B won 17 of 20 Sonnet-versus-Haiku debates. Haiku, the weaker model, won 13 of 20 (65%), mostly because it sat in B for half of them.
3. **Only a 4× word budget beat the seat.** Haiku with 100 words against Sonnet's 25 won **9 of 10 from seat A**, the seat that otherwise almost never wins. Lead hypothesis (pre-registered: Haiku ≥ 60% with the bigger budget): **met**, 19 of 20 (95%), against 65% at equal budgets.

## Robustness

- 11 batch-1 rulings skipped the `WINNER:` line. All of them opened "B wins." Per the pre-registration they were re-run once (10 B, 1 A). Classifying the originals by their opener instead changes only C0b, from 3–7 to 2–8. No conclusion changes.

## Limits (state these in any writeup)

- **"Seat B" combines two things:** speaking second (last before the judge rules) and holding the *against* role. These batches can't separate them. Separating them needs a code change that lets B speak first, which would be batch 3.
- One judge (gpt-5-mini), one proposition family, one judge prompt. The prompt discloses word limits to the judge. Small n per cell.
- These are known LLM-as-judge biases (position, verbosity), independently reproduced here. The strength of the seat effect is the observation, not the existence of the bias.
