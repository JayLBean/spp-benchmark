# Discrepancy analysis — run_01 (prompt_v01, bare seed)

Dev accuracy 0.4625 (37/80). Field: `label` (K=1). Rows referenced by ID only.
Disagreements cluster on **degree/intensity calibration**, not polarity — exactly
the SST-5 hard boundaries (terrible/bad, good/great, and the okay middle).

## Failure clusters

### Cluster A — positive-pole over-rating (good → great), primary field `label`
- Members (8): sst5_base_0243, sst5_base_0774, sst5_base_0441, sst5_base_0462, sst5_base_0848, sst5_base_0134, + 2 more.
- Shared property: reviews that are positive but **measured or single-note** (one nice attribute, a qualified compliment, plain approval) are being rated `great`. The model treats any clear positive as top-tier.
- Proposed edit → **Edit 1**.

### Cluster B — negative-pole under-rating (terrible → bad), primary field `label`
- Members (7): sst5_base_0686, sst5_base_0988, sst5_base_0574, sst5_base_0391, sst5_base_0597, sst5_base_0437, + 1 more.
- Shared property: reviews expressing **comprehensive / unredeemed failure** ("lacks both purpose and pulse", "fails at both", "goes nowhere") are softened to `bad`. The model reserves `terrible` too narrowly.
- Proposed edit → **Edit 2**.

### Cluster C — the mixed/lukewarm middle collapses to a pole (okay → bad or good), primary field `label`
- Members (11): okay→bad — sst5_base_0802, sst5_base_0131, sst5_base_0083, sst5_base_0032, sst5_base_0400, sst5_base_0344, sst5_base_0906 (and okay→good — sst5_base_0397, sst5_base_0373, sst5_base_0687, + 1).
- Shared property: **mildly dismissive, noncommittal, or explicitly balanced** reviews (faint negatives like "routine and rather silly", "barely"; "an easy watch except…") are pushed to a pole instead of the neutral/mixed `okay`.
- Proposed edit → **Edit 3**.

### Minor boundary noise (not separately targeted this iteration)
- bad→okay (5: sst5_base_0552, 0194, 0151, 0689, 0838): "but"-structured mixed-leaning-negative reviews. Partially addressed by Edit 3's balance clause.
- great→good (3), good→okay (3): residual fine-boundary noise; revisit if it persists.

## Proposed rule edits

**Edit 1 — positive-pole intensity rule** (target field `label`; addresses Cluster A):
Add a `<rules>` clause: reserve **great** for sustained, unqualified enthusiasm
(superlatives, "one of the best", "triumph", multiple strong positives); rate a
review **good** when the praise is mild, single-note, or carries reservations.
Categorical: keys on intensity/quantity of praise, applies to any positive review.

**Edit 2 — negative-pole intensity rule** (target field `label`; addresses Cluster B):
Add a clause: use **terrible** for pervasive or unredeemed failure (the work fails
broadly, has no redeeming notes, or is strongly repellent); use **bad** for a
specific weakness/disappointment in an otherwise competent film. Categorical: keys
on breadth/redeemability of the negativity, applies to any negative review.

**Edit 3 — neutral/mixed middle rule** (target field `label`; addresses Cluster C):
Add a clause: choose **okay** when a review is lukewarm, noncommittal, faintly
dismissive, or explicitly balanced (genuine praise *and* genuine fault). Do not
force a mild or mixed review to a pole. Categorical: keys on lukewarm/mixed
rhetoric, applies to any borderline-middle review.

All three edits are categorical degree-calibration rules derived from the cluster's
shared rhetorical property; none names or targets an individual row.
