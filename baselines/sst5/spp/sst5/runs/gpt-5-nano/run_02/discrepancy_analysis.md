# Discrepancy analysis — run_02 (prompt_v02)

Dev accuracy 0.5125 (41/80), up from 0.4625. Rows by ID only. Edit 1 helped the
good→great cluster (8→5); Edit 2 (terrible) did not bite; Edit 3 fixed some middle
cases but over-pulled some `bad` into `okay`.

## Failure clusters

### Cluster D — negative extreme avoidance (terrible → bad), primary field `label`
- Members (7): sst5_base_0384, sst5_base_0597, sst5_base_0988, sst5_base_0391, sst5_base_0686, + 2.
- Shared property: comprehensively negative reviews phrased with **restraint/understatement** ("lacks both purpose and pulse", "fails at both endeavors") still get `bad`. The model treats `terrible` as requiring overt vitriol. Edit 2 named the rule but not the anti-understatement cue.
- Proposed edit → **Edit 4** (strengthens Edit 2).

### Cluster E — mixed reviews with a net lean mis-routed to okay (bad → okay), primary field `label`
- Members (5): sst5_base_0194, sst5_base_0740, sst5_base_0838, sst5_base_0689, sst5_base_0552.
- Shared property: "praise BUT fault" reviews whose **net verdict is negative** are landing on `okay`. Edit 3's "explicitly balanced → okay" was too permissive — it ignored net lean.
- Proposed edit → **Edit 5** (refines Edit 3).

### Cluster F — middle still collapsing negative (okay → bad), primary field `label`
- Members (7): sst5_base_0344, sst5_base_0154, sst5_base_0802, sst5_base_0891, sst5_base_0083, + 2.
- Shared property: faintly dismissive but not condemnatory reviews → `bad`. Partly Edit 3's target; reinforced by Edit 5's neutral-lean clarification.

### Minor (not separately targeted): good→okay (4), great→good (4) — residual fine-boundary noise; revisit if persistent.

## Proposed rule edits

**Edit 4 — negative-extreme anti-understatement** (target `label`; strengthens Edit 2, addresses Cluster D):
Add to the `terrible` clause: across-the-board negativity counts as **terrible even when stated calmly or with understatement** — if the review says the film fails broadly, has no redeeming element, or lacks purpose/point as a whole, choose `terrible`, not `bad`. `bad` is for a film with a *specific* flaw but some merit. Categorical: keys on breadth of failure vs tone.

**Edit 5 — net-lean tie-break for mixed reviews** (target `label`; refines Edit 3, addresses Cluster E):
Amend the `okay` clause: a review that pairs praise with fault takes the side of its **net verdict** — net-negative → `bad`, net-positive → `good`. Reserve `okay` for reviews that are genuinely neutral, noncommittal, or evenly balanced with no clear lean. Categorical: keys on net sentiment of a mixed review.

Both edits are categorical refinements of existing rules; neither references an individual row.
