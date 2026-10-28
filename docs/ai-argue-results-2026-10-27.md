# AI Argue: results, batches 1–3

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

## Batch 3 (2026-10-28): speaking order versus role

Pre-registration: `ai-argue-preregistration-batch3-2026-10-28.md`. Same as S1 (original proposition, Haiku vs Haiku, 25 words each), but **B (against) speaks first and A (for) speaks second.**

| Cell | First speaker | Second speaker | First won | Second won |
|---|---|---|---|---|
| S1-rev | B (against) | A (for) | 5 | **15** |

- **Pre-registered reading: an order effect.** A won 15/20, which meets the "A ≥ 15" threshold. Fair coin: p ≈ 0.04, two-sided.
- **Robustness:** rep 17 was unparsed and re-run once (result B). The original ruling began "A presented the stronger case", so counting it gives 16–4. Both counts meet the threshold.

## Combined reading, batches 1–3

- **The judge rewards the last word.** Across all 60 identical-debater debates (S1, S1-inv, S1-rev), the second speaker won **55**.
- **Role may add a little.** When speaking last and arguing *against* were the same side, the last speaker won 40/40. When they were separated, it won 15/20 (75%). These batches can't size the role contribution precisely.
- **Content is ruled out** by batch 2: flipping the proposition changed nothing.
- **Only a 4× word budget overcame it:** Haiku with 100 words won 9/10 while speaking first (H1a).

## Exploratory observation (not pre-registered)

At equal budgets, the **weaker model did better from the disfavored seat than the stronger one**. Haiku won 3 of 10 from seat A against Sonnet (C0b), while Sonnet won 0 of 10 from seat A against Haiku (C0a). Put the other way round, seat B won 10/10 when Haiku held it and only 7/10 when Sonnet did.

- **Small and not statistically reliable.** Fisher's exact two-sided p ≈ 0.21. One of the three wins is a re-run; in the sensitivity count it's 2 of 10.
- **Possible explanations:**
  1. Chance.
  2. Argument style. In all three of Haiku's wins, the judge's ruling says Sonnet (B) committed to an objective "correct answer" (minimize deaths) and Haiku won by attacking that premise. A more ambitious claim may give the opponent more to rebut.
  3. An interaction between model and seat that this design can't isolate.
- **Test it** with more reps of exactly this matchup in a later batch.

## Robustness

- 11 batch-1 rulings skipped the `WINNER:` line. All of them opened "B wins." Per the pre-registration they were re-run once (10 B, 1 A). Classifying the originals by their opener instead changes only C0b, from 3–7 to 2–8. No conclusion changes.

## Limits (state these in any writeup)

- **Order and role:** batches 1–2 couldn't separate speaking second from arguing against. Batch 3 did: order dominates. Role may still contribute (40/40 when combined, 15/20 when separated); sizing that needs more reps.
- One judge (gpt-5-mini), one proposition family, one judge prompt. The prompt discloses word limits to the judge. Small n per cell.
- These are known LLM-as-judge biases (position, verbosity), independently reproduced here. The strength of the seat effect is the observation, not the existence of the bias.
