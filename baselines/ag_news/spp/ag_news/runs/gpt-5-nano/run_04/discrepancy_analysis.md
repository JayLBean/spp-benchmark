# Discrepancy analysis — run_04 (prompt_v04, +narrow Tech-pull rule) — TERMINAL

**Partition reviewed:** dev (80) + train (80). dev 0.90 (−1 vs v03's 0.9125); train 0.8875 (flat).

## Why v04 regressed — the Business/Tech boundary is contradictory gold

v03→v04 dev: fixed 1 (Apple→Tech), broke 2:
- "Renault F1 Team **launches** Bijoux Racing" → Business (gold Sports) — the rule's "(product
  launch)" example bled onto a sports launch. Same collateral class as the v02 Edit-2 failure.
- "Cingular keeps some AT&T execs" → Tech (gold **Business**) — a *telecom* company story that
  gold labels Business, the **opposite** of "IBM/Apple corporate event → Tech".

The two gold labels are mutually contradictory: IBM PC spin-off → Tech, but Cingular corporate
news → Business. **No categorical rule can satisfy both.** This is the irreducible gold noise the
plan (§2, §10) flagged at the Business/Tech boundary. Two independent rule attempts at this
boundary — Edit 2 (run_02) and Edit 4 (run_04) — both net-regressed dev. The boundary is not a
prompt-fixable signal; it is label noise.

## Loop decision: EARLY_STOP, select prompt_v03

- dev trajectory: v01 0.8875 → v02 0.8750 → v03 **0.9125** → v04 0.9000. Clear single peak at v03.
- The only remaining categorical signal (Business/Tech corporate events) has been shown to be
  contradictory gold; further iteration would chase ±1-row noise on an 80-row dev = overfitting,
  exactly what the plan's overfit guard and the methodology defend against.
- The clean, one-directional **science→Tech** rule (v03) is the measured contribution and
  generalizes; it is retained as the selected prompt.

No few-shot examples were ever added; every edit was auditor-categorical; the overfit guard
(train−dev > 0.15) never tripped (max gap was dev 0.9125 − train 0.8875 = +0.025, dev *above*
train, the opposite of overfitting). Sacred test untouched.
