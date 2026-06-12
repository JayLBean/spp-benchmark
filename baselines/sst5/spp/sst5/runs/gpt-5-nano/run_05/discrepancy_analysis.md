# Discrepancy analysis — run_05 (prompt_v05) — TERMINAL

Dev accuracy 0.5875, DOWN from prompt_v04's 0.600. Edit 8 (terrible tie-break)
**over-corrected**: terrible recall went 0.30→1.00 but `bad` recall collapsed
0.76→0.38 (7 bad→terrible, plus bad→okay leakage) and train fell 0.55→0.475.

The ordinal tie-break "no redeeming quality → terrible" was categorical and
auditor-approved, but empirically the model now over-applies `terrible` to ordinary
`bad` reviews. Net dev regressed → Edit 8 is rejected by the dev signal.

## Stop decision
- Dev trajectory: v01 0.4625 → v02 0.5125 → v03 0.5750 → v04 0.6000 → v05 0.5875.
- Peak at **prompt_v04 (dev 0.600)**, regression at v05.
- Remaining v04 errors are (a) structural — gpt-5-nano resists the `terrible`
  extreme; three categorical attempts (Edits 2, 4, 8) either failed to move it or
  over-corrected — and (b) genuinely ambiguous — the `good` class splits to
  great/okay/bad at the dev-noise level (80 rows, SE≈0.055). Additional categorical
  rules would chase dev noise, risking baseline overfitting.
- **No prompt_v06 produced. Loop terminates. Selected best-dev prompt: prompt_v04.**
