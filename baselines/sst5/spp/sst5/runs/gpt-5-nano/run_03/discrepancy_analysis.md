# Discrepancy analysis — run_03 (prompt_v03)

Dev accuracy 0.575 (46/80), up from 0.5125. Rows by ID only. Edits 4–5 helped net
(good/great over-rating largely gone), but two clusters dominate now.

## Failure clusters

### Cluster G — positive extreme over-corrected (great → good), primary field `label`
- Members (6): sst5_base_0816, sst5_base_0752, sst5_base_0558, sst5_base_0480, sst5_base_0087, sst5_base_0272.
- Shared property: clearly enthusiastic single-clause praise ("nothing short of wonderful", "a glorious spectacle", "highly engaging", "wildly entertaining", "sparkling") is being demoted to `good`. The "reserve great for *multiple* superlatives" framing set the bar too high and now hurts `great` recall.
- Proposed edit → **Edit 6** (loosens Edit 1).

### Cluster H — faint dismissal mis-routed to bad (okay → bad), primary field `label`
- Members (7): sst5_base_0397, sst5_base_0083, sst5_base_0802, sst5_base_0131, sst5_base_0032, sst5_base_0344, + 1.
- Shared property: mild putdowns that call a film slight/routine/unremarkable ("barely", "routine and rather silly", "an easy watch except…") without asserting real failure are landing on `bad`. The net-lean rule (Edit 5) over-read faint dismissiveness as net-negative.
- Proposed edit → **Edit 7** (refines the okay/bad boundary).

### Persistent (carried, not separately re-edited): terrible→bad (6) — gpt-5-nano deeply resists the `terrible` extreme even with the anti-understatement clause; partially structural to the model. good→great (3), bad→okay (3): residual boundary noise within tolerance.

## Proposed rule edits

**Edit 6 — great threshold loosening** (target `label`; loosens Edit 1, addresses Cluster G):
Amend the `great` clause: a **single clear, strong positive** (wonderful, glorious, superb, highly engaging, wildly entertaining, sparkling) qualifies as `great`; it need not stack multiple superlatives. `good` remains for *mild or qualified* praise. Categorical: keys on strength (not count) of the positive signal.

**Edit 7 — okay floor against faint dismissal** (target `label`; refines Edit 5, addresses Cluster H):
Amend the `okay`/`bad` boundary: a **faint or dismissive remark that calls a film slight, routine, or unremarkable but does not assert an actual failure or strong disappointment** stays `okay`. Choose `bad` only when the review asserts a real weakness the film does not overcome. Categorical: keys on whether real failure is asserted vs mere faint praise.

Both are categorical boundary refinements; neither references an individual row.
