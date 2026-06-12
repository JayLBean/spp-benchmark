# Discrepancy analysis — run_03 (prompt_v03, science rule only)

**Partition reviewed:** dev (80) + train (80). Best result so far: dev 0.9125, train 0.8875
(v01→v02→v03 dev = 0.8875 → 0.8750 → 0.9125).

## Remaining error structure

dev 7/80 errors; train 9/80. Two kinds:

**(a) Noisy / contradictory gold — NOT patchable.**
- World→Sports: "Roddick … Davis Semis" (gold World).
- World→Tech: "New dinosaur uncovered in Brazil" (gold World) — a science story gold-labeled
  World, the *inverse* of the science rule; Tech→World: "carbon-monoxide students" (gold Tech).
  These two contradict each other, so no science-rule tightening can win both.
- Business→Sports: "City … Jets West Side stadium financing" (gold Business).
These are gold-label noise at ±1–2 rows; chasing them is overfitting. Left to the model's prior.

**(b) Tech→Business cluster — the one genuine categorical signal left (dev 4, train 2).**
gold=Tech, pred=Business: "AOL Aims to Lead Internet Travel Purchases", "…Apple Computer …in
court", "IBM To Spin Off PC Unit", "Proxim, Symbol settle in patent case". All are *computing/
internet* companies whose news peg is a corporate event; AG News labels them Tech. The earlier
Edit 2 tried to address this but coupled it with a "purely financial → Business" clause that
mis-fired ("Renault F1 **launches**…" → Business). **Diagnosis:** the collateral came from the
Business-pushing half, not the Tech-pulling half.

## Proposed edit → for the isolated rule-edit stage
- **Edit 4:** add to prompt_v03 a *Tech-pulling-only* line — "when the article's main subject is a
  computing, internet, software, telecom, or consumer-electronics company, product, or service,
  choose Tech even when the news peg is a corporate event (acquisition, spin-off, lawsuit,
  settlement, product launch)." **No** "financial → Business" clause (that was the source of the
  v02 collateral). This narrows the rule to the half that helped and drops the half that hurt.

Edit selection driven by dev signal + the v02 failure analysis; categorical (company *class*,
not named rows). Forwarded to the score-blind auditor. If v04 does not beat v03 on dev, v03 is
the peak and the loop stops.
