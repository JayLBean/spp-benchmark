# EARLY_STOP — sst5 / gpt-5-nano

**Reason:** dev-accuracy peaked and the next iteration regressed; remaining errors are
structural (model-level `terrible` avoidance) or within dev-sample noise. Stopping is
the anti-baseline-overfitting call (auditor kept every applied edit categorical; the
dev signal rejected the one that over-corrected).

**Iterations run:** 5 of MAX_ITERATIONS 10.

**Dev-accuracy trajectory (prompt_vNN on the 80-row stratified dev split):**

| prompt | dev acc | train acc | note |
|---|---|---|---|
| v01 | 0.4625 | 0.4875 | bare seed + output-format directive |
| v02 | 0.5125 | 0.5500 | + categorical degree-calibration rules (Edits 1–3) |
| v03 | 0.5750 | 0.5750 | + anti-understatement terrible, net-lean tie-break (Edits 4–5) |
| **v04** | **0.6000** | 0.5500 | + great-threshold loosen, okay-floor (Edits 6–7) — **SELECTED** |
| v05 | 0.5875 | 0.4750 | + terrible ordinal tie-break (Edit 8) — over-corrected, rejected |

**Selected prompt (best dev):** `run_04/prompt_v04.md` (dev 0.600).
**Overfit guard:** never triggered (max train−dev gap = +0.05 at v04, well under 0.15).
**Auditor:** all 8 edits across 5 iterations verdicted `categorical`; zero overrides used.

PROMPT_FROZEN_v01 will be set to prompt_v04 at /spp-finalize after G5/G6.
Sacred test set has NOT been read at loop termination.
