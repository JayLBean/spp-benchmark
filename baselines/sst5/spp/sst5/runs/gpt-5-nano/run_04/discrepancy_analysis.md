# Discrepancy analysis — run_04 (prompt_v04)

Dev accuracy 0.60 (48/80), up from 0.575. Rows by ID only. Edit 6 recovered `great`
(recall 0.83), Edit 7 eased okay→bad. Per-class recall: bad 0.76, good 0.55,
great 0.83, okay 0.47, **terrible 0.30**.

## Failure clusters

### Cluster I — negative extreme still avoided (terrible → bad), primary field `label`
- Members (7): sst5_base_0988, sst5_base_0391, sst5_base_0560, sst5_base_0686, sst5_base_0492, sst5_base_0437, + 1.
- Shared property: broadly negative reviews with **no redeeming quality named** are still labeled `bad`. Edits 2 and 4 (definition + anti-understatement) did not move this — the model has a standing prior against the extreme label. Needs a decision-rule nudge, not another definition.
- Proposed edit → **Edit 8** (ordinal tie-break, single focused change to limit oscillation).

### Residual (genuinely ambiguous SST-5 boundaries; not separately edited to avoid oscillation):
- good splits in all directions — good→great (4), good→okay (3), good→bad (3); recall 0.55. No single categorical rule fixes this without harming neighbors (the Edit-1/Edit-6 good↔great trade-off is already near its sweet spot).
- okay→bad (4), bad→good (3): faint-dismissal / mixed-lean noise within tolerance after Edits 5/7.

## Proposed rule edit

**Edit 8 — terrible ordinal tie-break** (target `label`; addresses Cluster I):
Add a decision rule (not a new definition): **when a review is negative and names no redeeming quality at all, prefer `terrible` over `bad`.** `bad` should carry at least one acknowledged merit or a single localized flaw; a wholly negative verdict with nothing positive defaults to `terrible`. Categorical: keys on presence/absence of any acknowledged merit, applies to any negative review.

Single-edit iteration to isolate the effect on the `terrible`/`bad` boundary and limit cross-class oscillation.
