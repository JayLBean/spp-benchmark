# Discrepancy analysis — run_02 (prompt_v02, +Edit 1 +Edit 2)

**Partition reviewed:** dev (80) + train (80), compared against run_01.

## What the two edits did

| | dev | train |
|---|---|---|
| v01 acc | 0.8875 | 0.8750 |
| v02 acc | 0.8750 | 0.8750 |
| net | **−1 row** | 0 (fixed 4, broke 4) |

**Edit 1 (Tech = science AND technology):** clean win. Fixed "Global Warming" on dev and 3
science/nature rows on train (whale, fossil/Nessie, hominids → Tech). One-directional, no
attributable breakage. **Keep.**

**Edit 2 (tech/internet company → classify by primary subject):** net-negative. The
"corporate-event" language over-triggered the `Business` label on non-tech rows:
- "Renault F1 Team **launches** Bijoux Racing" → Business (gold Sports) — the word "launches".
- "Local residents due for tax refund" → World (gold Business).
- Tech→Business count did **not** fall (3→4): the boundary gold is too noisy (the Amazon A9
  counter-example already showed gold is inconsistent), so a sharper rule just adds collateral
  without netting the intended fixes.
**Revert.** The Business/Tech boundary is genuine gold noise; pushing on it trades errors rather
than removing them, and risks overfitting the 80-row dev.

## Proposed edit → for the isolated rule-edit stage
- **Edit 3:** produce prompt_v03 = prompt_v01's framing + **only** the Cluster-A science rule
  (Tech covers science/research/nature/space/medicine/internet, not gadgets-only). Drop the
  company-subject rule entirely. Keep the four-class label sketch as concise, non-prescriptive
  definitions so the model is not pushed toward Business on any "deal/launch" keyword.

This is an edit *selection* driven by the dev signal (which categorical edit survives), not a
row-specific patch. Forwarded to the score-blind auditor.
