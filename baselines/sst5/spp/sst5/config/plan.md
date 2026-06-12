# spp plan — sst5

**Created:** 2026-06-12

**Designer session:** spp-init-sst5-20260612

**Plan version:** v3

---

## 1. Task overview

**Task mode:** classification

**One-sentence description:** Rate the sentiment degree of a single movie-review sentence on a 5-point ordinal scale (terrible < bad < okay < good < great), emitting exactly one label per row.

**Audience for the prompt's output:** A benchmark accuracy scorer (spp-vs-EvoPrompt arm comparison on a shared sacred test set). The "downstream consumer" is the accuracy metric itself.

**Problem statement** (2–3 sentences):
Fine-grained sentiment is hard not because of polarity but because of *degree* boundaries — terrible vs. bad, good vs. great, and the okay/neutral middle. A bare 0-shot instruction (the shared seed) leaves those boundaries to the model's priors and lands near 0.557 accuracy on gpt-5-nano. spp's job is to refine that seed prompt — without seeing the sacred test — so the degree boundaries are pinned by categorical rules that generalize.

---

## 2. Output schema and per-field definitions

**Output schema** (JSON Schema draft 2020-12; mirrors `schema.json`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "sst5 output schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["label"],
  "properties": {
    "label": {
      "type": "string",
      "enum": ["terrible", "bad", "okay", "good", "great"],
      "description": "Sentiment degree of a movie-review sentence, ordered terrible<bad<okay<good<great."
    }
  }
}
```

**Per-field definitions:**

- **`label`:** the single sentiment-degree class for the review sentence. Per-class meanings (from `schema.json` labelDefinitions / SEED.md):
  - `terrible` — strongly negative: harsh condemnation, no redeeming notes.
  - `bad` — mildly negative: disappointed, weak, but not scathing.
  - `okay` — neutral or mixed: balanced, lukewarm, or noncommittal.
  - `good` — mildly positive: favorable with reservations.
  - `great` — strongly positive: enthusiastic praise.
  - Positive examples: clear-cut cases ("a sensitive, moving, brilliantly constructed work." → `great`; "a frankenstein-monster of a film that doesn't know what it wants to be." → `bad`).
  - Borderline examples: degree calls the loop must learn — strong-vs-mild on each pole (`terrible`/`bad`, `good`/`great`) and the mixed middle (`okay`).
  - Edge cases: sarcasm, faint praise, and mixed reviews that lean slightly one way; no "uncertain" class — the model is forced to pick the closest of the five.

**Known borderline cases:**
The terrible/bad and good/great splits (intensity, not direction) and the okay middle (mixed reviews) are the known fuzzy boundaries. These are exactly where prompt wording earns accuracy; the loop's discrepancy stage is expected to concentrate here.

---

## 3. Success criteria

**Production decision rule:**
The emitted `label` is compared for exact equality against the gold label; the row scores 1 if equal, 0 otherwise. Accuracy = mean over rows.

**Headline success criterion:**
Accuracy on the sacred test set (1000 rows, `test_holdout.csv`) **> 0.561** — the same-model EvoPrompt arm's best test accuracy. Secondary bar: beat the shared seed's manual-init test accuracy of 0.557. The optimization target during the loop is dev accuracy; the test number is read only once at finalization.

**Acceptable trade-offs:**
Token efficiency is a reported axis but not a gate: spp may spend more input tokens per call (richer prompt) so long as it makes far fewer total task-model calls than EvoPrompt's population search. A modest accuracy gain (even +1–2 points) at a fraction of EvoPrompt's search calls is a win; a large accuracy gain at comparable cost is also a win. No precision/recall asymmetry — accuracy weights all five classes by prevalence.

---

## 4. Per-field metrics, aggregate strategy, and floors

**Aggregate strategy:**

- **`AGGREGATE_STRATEGY`:** macro
- **`AGGREGATE_WEIGHTS`:** n/a (single field)
- **`AGGREGATE_RATIONALE`:** Single-output classification (K=1); the aggregate is the identity on the lone field's metric. "macro" is the trivial choice over one field.

**Per-field metrics:**

- **Field `label`:**
  - `METRIC_NAME`: accuracy
  - `METRIC_RATIONALE`: The benchmark fixes the metric as accuracy (SEED.md, schema.json). It is the mechanically correct comparator against the EvoPrompt arm, which also reports accuracy. Plain accuracy (not macro-F1) is deliberate: the test set is prevalence-distributed and accuracy is the headline number both arms are scored on.
  - `METRIC_INDEPENDENCE_NOTE`: Accuracy is computed by exact string match of the predicted label against the frozen gold label — fully deterministic, no LLM in the scoring path (DESIGN.md §5). The gold labels are the bring-your-own baseline + sacred holdout; no judge metric.

**Per-field floors:**
None. (Single metric, single field; the headline accuracy criterion in §3 governs.)

---

## 5. Model and lock-in posture

**Production model identifier:** `gpt-5-nano`

**Production model family:** openai

**Lock-in posture:** locked

**Cross-model fragility plan:**
The prompt is optimized for `gpt-5-nano` only; this is a single-model benchmark arm. We will not swap models. If a different model were ever targeted, the correct response is to re-run `/spp-loop` against it from the same seed. Any gpt-5-specific handling (reasoning_effort, max_completion_tokens, omitted temperature) is an API-call concern in the runner, not prompt content, so the frozen prompt itself stays model-portable text.

---

## 6. Baseline

**Data source:** `baseline.csv` (1000 labeled rows, columns `row_id,text,label`), already prepared by the benchmark harness. Bring-your-own-labels path — labels are treated as GOLD; no re-labeling. The sacred test is the separate `test_holdout.csv` (1000 rows), the identical rows the EvoPrompt arm scored on.

**Preprocess mapping:** `row_id → id`, `text → input`, `label → label`; rename-only, no content change (data already canonical in substance). Written to `spp/sst5/data/baseline.csv` during `/spp-baseline`.

**Target baseline size:** 1000 rows available; the loop's working splits subsample a stratified train (80) + dev (80) from this pool (see §7). The remaining ~840 rows are an unused labeled reserve.

**Class balance target:** preserve production/test prevalence — baseline is imbalanced (good 271, bad 260, okay 190, great 151, terrible 128) and the sacred test is similarly imbalanced, so dev/train are stratified *proportionally* so dev-accuracy estimates test-accuracy honestly.

**Language coverage:** monolingual (English).

**Label provenance:** Upstream SST-5 gold labels, mapped to the 5 degree names by the benchmark harness; identical provenance as the rows the EvoPrompt arm used. `baseline-quality` audits these labels (G2) but does not re-label.

**Label synthesis:** none (labels human-provided / already present).

**Status:** complete
<!-- Existing-baseline (bring-your-own gold) path: labels imported, audited
     not relabeled. Canonical baseline written to spp/sst5/data/baseline.csv. -->

**Baseline-quality review** (audit-of-existing-labels mode, K=1 field `label`):
Reviewed the 1000-row imported gold baseline. Checks run:
- **Integrity:** 1000/1000 valid enum labels; 0 empty inputs; 0 duplicate ids; 0 duplicate input texts; **0 exact-text overlap with the sacred test set** (no leakage).
- **§3.4 class balance vs sacred test:** baseline prevalence tracks the test set within ±4pp on every class (terrible +0.2, bad −2.6, okay +1.4, good +4.0, great −3.0 pp) — representative; stratified-proportional dev/train will inherit this match.
- **§3.1 drift / §3.5 spot-check:** stratified sample (4/class, seed 20260612) eyeballed against the §2 degree definitions; all sampled labels plausible (terrible = scathing, bad = moderate-negative, okay = mixed/noncommittal, good = positive-with-reservations, great = enthusiastic).
- **§3.6 provenance:** upstream SST-5 gold mapped to the 5 degree names by the benchmark harness; identical provenance to the rows the EvoPrompt arm scored.

Known characteristic (not a defect): the terrible/bad and good/great intensity boundaries and the okay middle are inherently subjective in SST-5. These are the *shared* gold labels both arms are measured against; re-labeling is forbidden (would break apples-to-apples) and unnecessary — the loop's job is to refine the prompt to match this fixed gold, not to fix the gold. **Verdict: ready.**

---

## 7. Splits

**Split ratios:** train 7% / dev 7% / test 86%
<!-- Proportions of spp's labeled working corpus (train 80 + dev 80 from
     baseline + test 1000 external holdout = 1160 rows): 80/1160≈7,
     80/1160≈7, 1000/1160≈86; sums to 100. dev=80 matches the EvoPrompt
     arm's dev split size for an apples-to-apples dev-scoring unit. The TEST
     partition is the external sacred holdout (test_holdout.csv), NOT carved
     from baseline; train+dev are stratified-proportional subsamples of the
     1000-row baseline pool; the other ~840 baseline rows are an unused
     reserve. -->

**Random seed:** 20260612

**Stratification key:** `label` (proportional to baseline prevalence; dev sized to match test prevalence so dev-accuracy tracks test-accuracy).

**Sacred test set acknowledgment:** acknowledged

---

## 8. Loop scope and stop criteria

**spp scope:** full
<!-- Full Phase 1 + 1.5 + 2 + 3. Phase 1 labeling is skipped (bring-your-own
     gold labels, audited not relabeled), but Phase 3's sacred-test discipline
     is fully in force — the external holdout is the whole point of the
     apples-to-apples comparison. -->

**MAX_ITERATIONS:** 10

**Dev plateau threshold:** < 0.01 dev-accuracy improvement for 3 consecutive iterations.

**Overfitting early-stop guard:** train accuracy − dev accuracy > 0.15 for 2 consecutive iterations triggers EARLY_STOP.

**Auditor configuration:** per-iteration, no-score-access

**Adversary:** off
<!-- Single-model accuracy benchmark with abundant real labeled data; synthetic
     adversarial rows add cost without a clear win, and the comparison is about
     refining the seed on real dev. Can flip on later via a §11 revision if the
     loop stalls on a specific degree boundary. -->

---

## 9. Decision rules at HITL gates

| Gate | Approval phrase | Notes |
|---|---|---|
| G1 — plan approval | `approved, proceed to baseline` | |
| G2 — baseline review | `approved, proceed to splits` | |
| G3 — split confirmation | `approved, start the loop` | |
| G4 — dry-run gate | `approved, run iteration 1` | |
| G5 — finalization | `approved, score the test set` | |
| G6 — production decision | `approved, freeze the prompt` | |

---

## 10. Open questions / known unknowns

- **Dev size.** Resolved at G1 (v2): dev=80 / train=80 (160 task-model calls/iteration), dev sized to match the EvoPrompt arm's dev=80 unit. Stratified proportional to baseline prevalence. Token usage tracked as a reported footnote, not a design constraint (comparison is held fair by the shared sacred test set).
- **Few-shot examples.** Whether the loop adds worked examples (and from which partition — only train, never dev/test) is left to the discrepancy/rule-edit stages. If examples are added they come from the train split exclusively.
- **Reasoning-token cost.** gpt-5-nano at reasoning_effort "low" still spends reasoning tokens that count as output; the exact per-call output cost is unknown until the dry-run and will be recorded in `token_usage.md`.
- **max_completion_tokens ceiling.** Must be generous enough that low-effort reasoning does not exhaust the budget and return empty content; the dry-run validates the chosen ceiling (200 → may be too small; see loop_spec).

---

## 11. Plan revision log

| Date | Plan version | Reason | By |
|---|---|---|---|
| 2026-06-12 | v1 | Initial plan via /spp-init (bring-your-own-labels path; gpt-5-nano arm) | spp-init-sst5-20260612 |
| 2026-06-12 | v2 | G1 pre-approval revision: dev 100→80 to match EvoPrompt's dev split size; train 100→80 (symmetric, keeps overfit guard); §7 ratios 7/7/86; both stratified-proportional | spp-init-sst5-20260612 |
| 2026-06-12 | v2 | **G1 approved** by user (phrase: "approved, proceed to baseline") — gate event, no contract change | user |
| 2026-06-12 | v3 | /spp-baseline: canonicalized baseline (rename-only id/input/label) + baseline-quality audit of imported gold labels → verdict **ready**; added §6 BASELINE_QUALITY_NOTE; BASELINE_STATUS → complete | spp-baseline-sst5-20260612 |
| 2026-06-12 | v3 | **G2 approved** by user (phrase: "approved, proceed to splits") — gate event | user |
| 2026-06-12 | v3 | /spp-baseline: generated splits.json (stratified-proportional, seed 20260612): train 80 / dev 80 from baseline pool, test = external sacred holdout (1000 rows, test_holdout.csv) | spp-baseline-sst5-20260612 |
| 2026-06-12 | v3 | **G3 approved** by user (phrase: "approved, start the loop") — gate event | user |
| 2026-06-12 | v3 | /spp-loop: patched scripts/inference.py for gpt-5 reasoning models (max_completion_tokens, omit temperature, reasoning_effort low); built run_01/prompt_v01.md (bare seed + output-format directive only); G4 dry-run on 3 train rows passed (3/3 parse) | spp-loop-sst5-20260612 |
| 2026-06-12 | v3 | **G4 approved** by user (phrase: "approved, run iteration 1") — gate event | user |
| 2026-06-12 | v3 | /spp-loop ran 5 iterations (8 edits, all auditor-categorical, 0 overrides, overfit guard never tripped); dev peaked at prompt_v04 (0.600); EARLY_STOP, selected prompt_v04 | spp-loop-sst5-20260612 |
| 2026-06-12 | v3 | **G5 approved** by user (phrase: "approved, score the test set") — gate event | user |
| 2026-06-12 | v3 | /spp-finalize: scored prompt_v04 on sacred test (1000 rows) → **test accuracy 0.579** (vs EvoPrompt 0.561, seed 0.557); 0 parse failures; 1803 total calls / 864,267 gpt-5-nano tokens | spp-finalize-sst5-20260612 |
| 2026-06-12 | v3 | **G6 approved** by user (phrase: "approved, freeze the prompt") — froze prompt_v04 → PROMPT_FROZEN_v01.md (SHA-256 16873a41…7676c); wrote REPORT.md. Run complete. | user |
