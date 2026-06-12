# spp plan — ag_news

**Created:** 2026-06-12

**Designer session:** spp-init-ag_news-20260612

**Plan version:** v2

---

## 1. Task overview

**Task mode:** classification

**One-sentence description:** Classify a short English news article (title + first sentences) into exactly one of four topics — World, Sports, Business, or Tech — emitting one label per row.

**Audience for the prompt's output:** A benchmark accuracy scorer (spp-vs-EvoPrompt arm comparison on a shared sacred test set). The "downstream consumer" is the accuracy metric itself.

**Problem statement** (2–3 sentences):
AG News topic classification is near-saturated — a bare 0-shot instruction (the shared seed) already lands ~0.87 on gpt-5-nano, and EvoPrompt's GA did not improve on it. The genuine remaining error mass is concentrated at one boundary: Business vs Tech (a software-company earnings story reads as either), with smaller World/Business spillover on economic-policy and trade stories. spp's job is to refine the seed prompt — without seeing the sacred test — so those boundary calls are pinned by categorical rules that generalize, matching ~0.87 without overfitting the dev split.

---

## 2. Output schema and per-field definitions

**Output schema** (JSON Schema draft 2020-12; mirrors `schema.json`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ag_news output schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["label"],
  "properties": {
    "label": {
      "type": "string",
      "enum": ["World", "Sports", "Business", "Tech"],
      "description": "The single news topic of the article's main subject."
    }
  }
}
```

**Per-field definitions:**

- **`label`:** the single topic class for the news article. Per-class meanings (from `schema.json` labelDefinitions / SEED.md):
  - `World` — international affairs, politics, conflict, disasters, general news.
  - `Sports` — any sport, athlete, team, match, or league.
  - `Business` — companies, markets, finance, economy, earnings, trade, jobs.
  - `Tech` — science and technology: gadgets, software, research, space, internet.
  - Positive examples: clear-cut cases ("Fernando's fourth-place finish at the Chinese Grand Prix" → `Sports`; "PeopleSoft fires CEO as software maker battles a hostile takeover" → topic depends on framing, see borderline).
  - Borderline examples: a tech-company *business event* (earnings, M&A, CEO firing) is the chief ambiguity — Business (the corporate event) vs Tech (the company's domain).
  - Edge cases: economic-policy / trade stories that are also geopolitical (World vs Business); science with a defense or political angle (Tech vs World). No "uncertain" class — the model is forced to pick the closest of the four.

**Known borderline cases:**
**Business vs Tech** is the dominant genuine ambiguity (corporate event at a tech company). Secondary fuzzy boundaries: **World vs Business** (trade/economic policy, oil, currencies as geopolitics) and **Tech vs World** (space programs, science with a national-security angle). These are exactly where prompt wording earns accuracy; the loop's discrepancy stage is expected to concentrate here.

---

## 3. Success criteria

**Production decision rule:**
The emitted `label` is compared for exact equality against the gold label; the row scores 1 if equal, 0 otherwise. Accuracy = mean over rows.

**Headline success criterion:**
Accuracy on the sacred test set (1000 rows, `test_holdout.csv`) **≥ 0.869** — the same-model EvoPrompt arm's test accuracy (whose best prompt is the shared seed itself, test 0.870). ag_news is near-saturated, so the realistic, honest target is *matching* ~0.87 without overfitting, not a large gain; any clean improvement is upside. The optimization target during the loop is dev accuracy; the test number is read only once at finalization.

**Acceptable trade-offs:**
Token efficiency is a reported axis (dollars, the honest comparator) but not a gate: spp may spend more input tokens per call (richer prompt) so long as it makes far fewer total task-model calls than EvoPrompt's population search. Matching accuracy at a fraction of EvoPrompt's search calls/cost is a win; a clean accuracy gain is upside. No precision/recall asymmetry — accuracy weights all four classes equally (the baseline and test are exactly balanced).

---

## 4. Per-field metrics, aggregate strategy, and floors

**Aggregate strategy:**

- **`AGGREGATE_STRATEGY`:** macro
- **`AGGREGATE_WEIGHTS`:** n/a (single field)
- **`AGGREGATE_RATIONALE`:** Single-output classification (K=1); the aggregate is the identity on the lone field's metric. "macro" is the trivial choice over one field.

**Per-field metrics:**

- **Field `label`:**
  - `METRIC_NAME`: accuracy
  - `METRIC_RATIONALE`: The benchmark fixes the metric as accuracy (SEED.md, schema.json, fixtures metadata). It is the mechanically correct comparator against the EvoPrompt arm, which also reports accuracy. Plain accuracy is unambiguous here: the test set is exactly class-balanced (250/250/250/250), so accuracy and macro-F1 coincide closely and accuracy is the headline number both arms are scored on.
  - `METRIC_INDEPENDENCE_NOTE`: Accuracy is computed by exact string match of the predicted label against the frozen gold label — fully deterministic, no LLM in the scoring path (DESIGN.md §5). The gold labels are the bring-your-own baseline + sacred holdout; no judge metric.

**Per-field floors:**
None. (Single metric, single field; the headline accuracy criterion in §3 governs.)

---

## 5. Model and lock-in posture

**Production model identifier:** `gpt-5-nano`

**Production model family:** openai

**Lock-in posture:** locked

**Cross-model fragility plan:**
The prompt is optimized for `gpt-5-nano` only; this is a single-model benchmark arm. We will not swap models. If a different model were ever targeted, the correct response is to re-run `/spp-loop` against it from the same seed. Any gpt-5-specific handling (reasoning_effort, max_completion_tokens, omitted temperature) is an API-call concern in the runner (scripts/inference.py, which already branches on reasoning models), not prompt content, so the frozen prompt itself stays model-portable text.

---

## 6. Baseline

**Data source:** `baseline.csv` (1000 labeled rows, columns `row_id,text,label`), already prepared by the benchmark harness. Bring-your-own-labels path — labels are treated as GOLD; no re-labeling. The sacred test is the separate `test_holdout.csv` (1000 rows), the identical rows the EvoPrompt arm scored on.

**Preprocess mapping:** `row_id → id`, `text → input`, `label → label`; rename-only, no content change (data already canonical in substance). Written to `spp/ag_news/data/baseline.csv` during `/spp-baseline`.

**Target baseline size:** 1000 rows available; the loop's working splits subsample a stratified train (80) + dev (80) from this pool (see §7). The remaining 840 rows are an unused labeled reserve.

**Class balance target:** preserve production/test prevalence — the baseline is **exactly balanced** (World 250, Sports 250, Business 250, Tech 250) and the sacred test is identically balanced (250/250/250/250), so dev/train are stratified to 20 rows per class each, and dev-accuracy estimates test-accuracy honestly.

**Language coverage:** monolingual (English).

**Label provenance:** Upstream AG News gold labels (Zhang et al. 2015; label names follow EvoPrompt verbalizers), identical provenance to the rows the EvoPrompt arm used. `baseline-quality` audits these labels (G2) but does not re-label.

**Label synthesis:** none (labels human-provided / already present).

**Status:** complete
<!-- Existing-baseline (bring-your-own gold) path: labels imported, audited
     not relabeled. Canonical baseline written to spp/ag_news/data/baseline.csv
     (rename-only row_id→id, text→input, label→label). -->

**Baseline-quality review** (audit-of-existing-labels mode, K=1 field `label`):
Reviewed the 1000-row imported gold baseline. Checks run:
- **Integrity:** 1000/1000 valid enum labels; 0 invalid; 0 empty inputs; 0 duplicate ids; 0 duplicate input texts; **0 exact-text overlap with the sacred test set** (no leakage).
- **§3.4 class balance vs sacred test:** baseline is exactly balanced (World/Sports/Business/Tech = 250 each) and the sacred test is identically balanced (250 each) — a perfect prevalence match; the stratified 20/class dev will track test prevalence exactly.
- **§3.1 drift / §3.5 spot-check:** stratified sample (4/class, seed 20260612) eyeballed against the §2 topic definitions; all sampled labels plausible (World = international/political incl. China labor & Rwanda; Sports = clear; Business = markets/IPO/earnings; Tech = telecom/sensors/science). Telecom items (Time Warner broadband, Verizon spectrum) carry the AG News Tech verbalizer — the known Business/Tech boundary, not a defect.
- **§3.6 provenance:** upstream AG News gold (Zhang et al. 2015; EvoPrompt verbalizers), identical provenance to the rows the EvoPrompt arm scored.

Known characteristic (not a defect): the Business/Tech boundary (corporate events at tech/telecom companies) and the World/Business boundary (trade & economic policy) are inherently fuzzy in AG News. These are the *shared* gold labels both arms are measured against; re-labeling is forbidden (would break apples-to-apples) and unnecessary — the loop's job is to refine the prompt to match this fixed gold, not to fix the gold. **Verdict: ready.**

---

## 7. Splits

**Split ratios:** train 7% / dev 7% / test 86%
<!-- Proportions of spp's labeled working corpus (train 80 + dev 80 from the
     1000-row baseline pool + test 1000 external holdout = 1160 rows):
     80/1160≈7, 80/1160≈7, 1000/1160≈86; sums to 100. dev=80 matches the
     EvoPrompt arm's effective dev split size (run.log dev=80) for an
     apples-to-apples dev-scoring unit. The TEST partition is the external
     sacred holdout (test_holdout.csv), NOT carved from baseline; train+dev are
     stratified (20/class each, balanced) subsamples of the 1000-row baseline
     pool; the other 840 baseline rows are an unused reserve. -->

**Random seed:** 20260612

**Stratification key:** `label` (balanced — 20 rows per class in each of dev and train; dev prevalence matches the test set exactly so dev-accuracy tracks test-accuracy).

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
     loop stalls on the Business/Tech boundary. -->

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

- **Headroom.** ag_news is near-saturated (seed ≈ 0.87; EvoPrompt's GA found nothing better). The honest goal is to *match* ~0.87 with a structured prompt while spending far fewer calls/dollars; a clean gain on the Business/Tech boundary is upside, not a promise. Overfitting the small dev (80 rows) is the chief risk — the overfit guard and dev-plateau stop are the defenses.
- **Few-shot examples.** Whether the loop adds worked examples (and from which partition — only train, never dev/test) is left to the discrepancy/rule-edit stages. If examples are added they come from the train split exclusively.
- **Reasoning-token cost.** gpt-5-nano at reasoning_effort "low" still spends reasoning tokens that count as output; the exact per-call output cost is unknown until the dry-run and is recorded in `token_usage.md`.
- **max_completion_tokens ceiling.** Must be generous enough that low-effort reasoning does not exhaust the budget and return empty content; the dry-run validates the chosen ceiling (loop_spec sets 2000).

---

## 11. Plan revision log

| Date | Plan version | Reason | By |
|---|---|---|---|
| 2026-06-12 | v1 | Initial plan via /spp-init (bring-your-own-labels path; gpt-5-nano arm; 4-class balanced) | spp-init-ag_news-20260612 |
| 2026-06-12 | v1 | **G1 approved** by user (phrase: "approved, proceed to baseline") — gate event, no contract change | user |
| 2026-06-12 | v2 | /spp-baseline: canonicalized baseline (rename-only id/input/label) + baseline-quality audit of imported gold labels → verdict **ready**; added §6 baseline-quality review; BASELINE_STATUS → complete | spp-baseline-ag_news-20260612 |
| 2026-06-12 | v2 | **G2 approved** by user (phrase: "approved, proceed to splits") — gate event | user |
| 2026-06-12 | v2 | /spp-baseline: generated splits.json (stratified, seed 20260612): train 80 / dev 80 from baseline pool (20/class each, balanced, disjoint), test = external sacred holdout (1000 rows, test_holdout.csv); verified 0 baseline↔test id overlap | spp-baseline-ag_news-20260612 |
| 2026-06-12 | v2 | **G3 approved** by user (phrase: "approved, start the loop") — gate event | user |
| 2026-06-12 | v2 | /spp-loop: built run_01/prompt_v01.md (bare seed + output-format directive only, no defs/examples) + run_infer.py driver (usage-tee, hard-refuses test ids). gpt-5 reasoning-model handling already in scripts/inference.py — no patch needed. G4 dry-run on 3 train rows: 3/3 calls (no 400), 3/3 parse, exact token capture (352 in / 30 out) | spp-loop-ag_news-20260612 |
| 2026-06-12 | v2 | **G4 approved** by user (phrase: "approved, run iteration 1") — gate event | user |
| 2026-06-12 | v2 | /spp-loop ran 4 iterations (4 edits proposed, all auditor-categorical, 0 overrides, overfit guard never tripped — dev ran above train). dev: v01 0.8875 → v02 0.8750 (Edit 2 company-rule collateral, reverted) → v03 **0.9125** (science→Tech rule only) → v04 0.9000 (narrow Tech-pull rule regressed — Business/Tech gold is contradictory). EARLY_STOP, selected best-dev **prompt_v03**. Search cost 643 calls / 188,436 gpt-5-nano tokens. Sacred test untouched | spp-loop-ag_news-20260612 |
| 2026-06-12 | v2 | **G5 approved** by user (phrase: "approved, score the test set") — gate event | user |
| 2026-06-12 | v2 | /spp-finalize: one-time sanctioned read of the sacred test (1000 rows) via the EvoPrompt-identical bridge (scripts/score_prompt.py). Scored prompt_v03 → **test accuracy 0.876** (vs EvoPrompt 0.869, seed 0.870), 0/1000 parse failures. dev 0.9125→test 0.876 (−0.036, within dev noise → clean generalization). Logged finalize tokens (1000 calls / 285,476) → cumulative 1,643 calls / 473,912 tok / **$0.04**. Wrote test_eval.json, test_results.json, REPORT.md | spp-finalize-ag_news-20260612 |
| 2026-06-12 | v2 | Post-finalize exploration (user-requested, dev-gated, R&D not part of shipped arm): prompt_v05 = sharper rules + 4 train-split few-shot demos @ reasoning low → dev 0.8625 (regressed); CoT lever v03 @ reasoning medium → dev 0.925 (within noise, ~5× output cost, breaks `low` apples-to-apples). Both rejected; v03 unchanged. Confirmed at the practical prompting ceiling | spp-finalize-ag_news-20260612 |
| 2026-06-12 | v2 | Dashboard reconciliation (OpenAI usage, Jun 12): loop verified exactly — 643 requests ✓, 171,956 input tokens ✓ (headline = input-only), $0.02 ✓. Added DSPy arm to comparison (0.881 / $0.15): on 1000-row test SE≈0.0104 the three arms are within ~1 SE (tied on accuracy); spp wins on cost ($0.04 vs DSPy $0.15 vs EvoPrompt $0.18). Updated token_usage.md + REPORT.md §1 | spp-finalize-ag_news-20260612 |
| 2026-06-12 | v2 | **G5 + G6 approved** by user (phrases: "approved, score the test set"; "approved, freeze the prompt"). Froze prompt_v03 → runs/gpt-5-nano/PROMPT_FROZEN_v01.md (SHA-256 9b7a1fd9…baf96, hash-verified byte-identical). **Run complete.** Result: spp test 0.876 beats EvoPrompt 0.869 (+0.7) and seed 0.870 (+0.6) at $0.04 (4.6× cheaper); statistically tied with DSPy 0.881 at ~3.8× lower cost | user |
