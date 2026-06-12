# spp REPORT — sst5 / gpt-5-nano

**Task:** fine-grained sentiment of a movie-review sentence on a 5-point ordinal scale
(terrible < bad < okay < good < great). Single-label, K=1, English. Metric: accuracy.
**Model under test:** `gpt-5-nano` (OpenAI, reasoning_effort "low"), locked.
**Plan:** `config/plan.md` v3. **Date:** 2026-06-12.
**Benchmark arm comparison:** spp vs EvoPrompt, same model, same seed, same sacred test.

---

## 1. Headline result

| arm | **test accuracy** (1000 sacred rows) | calls | tokens | **cost (USD)** |
|---|---:|---:|---:|---:|
| shared seed (manual-init) | 0.557 | — | — | — |
| EvoPrompt (gpt-5-nano) | 0.561 | 4,368 | 783,858 | $0.21 |
| **spp (gpt-5-nano)** | **0.579** | **1,803** | 864,267 | **$0.10** |

**spp wins a clean sweep: +1.8 accuracy points (0.579 vs 0.561; +2.2 over the shared seed
0.557), 2.4× fewer task-model calls (1,803 vs 4,368), and ~2.1× cheaper ($0.10 vs $0.21).**
0/1000 parse failures. Raw *token count* is a misleading axis — spp's total (864k) edges
above EvoPrompt's (784k) — but output tokens cost 8× input and the arms have opposite
profiles: spp is input-heavy / output-light (one static six-section prompt replayed per
row; 167k output), EvoPrompt is output-heavy (GA population × generations + reasoning;
494k output). On the metric that bills — dollars — spp is half the cost. The spp $0.10
figure was verified against the OpenAI dashboard (1,803 requests and 697,609 input tokens
both match exactly; total spend $0.10 to the cent). Pricing: $0.05/1M input, $0.40/1M
output; no caching (prompt below the 1024-token threshold).

---

## 2. Methodology (apples-to-apples controls)

- **Same seed.** Both arms start from the identical bare instruction in `prompt_v0.md`
  ("Examine the comment provided and classify it into one of five categories: terrible,
  bad, okay, good, or great."). spp's iteration-1 prompt added only a bare-label
  output-format directive (operational parseability for the exact-match scorer) — no
  label definitions, no examples. All semantic structure was earned by the loop.
- **Same baseline pool.** The 1000-row `baseline.csv` gold labels (audited, not
  relabeled — verdict `ready`, 0 leakage with test, balance within ±4pp of test).
- **Same sacred test.** `test_holdout.csv` (1000 rows) — the identical rows EvoPrompt
  scored. Read exactly once, at finalization, after gates G1–G5.
- **spp internal splits.** train 80 / dev 80, stratified-proportional to baseline
  prevalence (so dev-accuracy tracks test-accuracy); the remaining ~840 baseline rows
  were an unused reserve. dev=80 matches EvoPrompt's dev unit.

### Optimization loop (Phase 2)

5 iterations, then EARLY_STOP (dev peaked, next iteration regressed). 8 rule edits, every
one verdicted **`categorical`** by the score-blind auditor (zero overrides; overfit guard
never tripped). The edits were degree-calibration rules on the SST-5 hard boundaries:

| prompt | dev acc | edit(s) added |
|---|---:|---|
| v01 | 0.4625 | bare seed + output directive |
| v02 | 0.5125 | categorical degree rules: good/great over-rating, bad/terrible under-rating, okay-middle collapse (Edits 1–3) |
| v03 | 0.5750 | anti-understatement terrible, net-lean tie-break for mixed reviews (Edits 4–5) |
| **v04** | **0.6000** | great-threshold loosen (single strong positive), okay-floor vs faint dismissal (Edits 6–7) — **SELECTED** |
| v05 | 0.5875 | terrible ordinal tie-break (Edit 8) — over-corrected `bad`→`terrible`, rejected by dev |

**Information isolation upheld throughout:** the rule-edit subagent saw the prompt +
discrepancy (row-IDs only) + label defs — never row content or scores; the auditor saw
the prompt diff + discrepancy + label defs — never scores. The discrepancy artifacts
reference dev rows by ID only.

---

## 3. Test-set breakdown (prompt_v04, 1000 rows)

**Accuracy 0.579.** Per-class recall: bad 0.808 · good 0.649 · great 0.547 · okay 0.318 ·
terrible 0.341.

Confusion (row = true, col = pred; labels bad, good, great, okay, terrible):
```
bad       [231,   5,   0,  28,  22]
good      [  8, 150,  47,  25,   1]
great     [  2,  77,  99,   2,   1]
okay      [ 77,  35,   2,  56,   6]
terrible  [ 79,   0,   0,   4,  43]
```

- **Strong:** `bad` (recall 0.81) and `good` (0.65) — the high-prevalence classes the
  loop's net-lean and faint-dismissal rules targeted.
- **Hard (structural):** `terrible` (0.34) and `okay` (0.32). gpt-5-nano systematically
  under-uses the `terrible` extreme (79 terrible→bad) — three categorical edits could not
  move it without over-correcting (`v05` proved the over-correction). The `okay` middle
  splits to the poles. These are the known-subjective SST-5 boundaries flagged in the
  baseline audit; they are model-and-task limits, not labeling defects.
- **good/great** confusion (77 great→good, 47 good→great) is the residual positive-pole
  noise — the loop reached the good↔great sweet spot but cannot fully separate them.

**Generalization:** dev 0.600 → test 0.579, a −0.021 gap well within the 80-row dev
sampling noise (SE ≈ 0.055). The categorical-only auditor discipline delivered a prompt
that generalized rather than fitting the dev split.

---

## 4. The frozen prompt

`PROMPT_FROZEN_v01.md` = `run_04/prompt_v04.md`.
SHA-256: `16873a41f6b7cc3c119c9be6b6882a12702f9153773f64733eb6fa8341a7676c`
Verify: `shasum -a 256 PROMPT_FROZEN_v01.md`

Six-section structure (`<task>`, `<rules>`, `<tie_breaks>` absent at v04, `<output_format>`)
encoding categorical degree-calibration rules for the five classes. Model-portable text —
the gpt-5 API specifics (reasoning_effort, max_completion_tokens, omitted temperature)
live in the runner, not the prompt.

---

## 5. Token / efficiency footnote

spp gpt-5-nano ledger (search + finalize), in `token_usage.md`:

| phase | calls | tokens |
|---|---:|---:|
| dry-run (G4) | 3 | 473 |
| loop search (5 iters × train+dev 160) | 800 | 336,534 |
| finalize test scoring (1000) | 1,000 | 527,260 |
| **total** | **1,803** | **864,267** |

spp made **59% fewer task-model calls** than EvoPrompt (1,803 vs 4,368) at **~half the
dollar cost** ($0.10 vs $0.21, gpt-5-nano list pricing; spp's figure reproduces the OpenAI
dashboard spend to the cent). Raw total tokens are ~10% higher because the refined prompt
is input-heavier per call — almost entirely in the 1,000-row test pass (436k input tokens
there) — but input is 8× cheaper than output, and spp emits far fewer output tokens (167k
vs EvoPrompt's 494k), so spp is cheaper where it counts. The optimization *reasoning* was
additionally offloaded to Claude subagents + the human (not billed in this gpt-5-nano
ledger), per `scripts/cost_report.py`'s framing.

---

## 6. Limitations / acknowledged risks

- **Dev split is 80 rows** (SE ≈ 0.055). The v03/v04/v05 dev differences (0.575/0.600/0.588)
  are within noise; v04 was selected as the dev-argmax. The dev→test consistency (−0.021)
  supports the selection, but a larger dev would tighten the estimate.
- **`terrible`/`okay` recall is low** (0.34/0.32) — a structural gpt-5-nano limit, not
  fixable by categorical prompt rules at this iteration budget. A different model, or
  few-shot exemplars from the train split (a deferred §10 open question), could help; both
  are out of scope for this single-model, seed-faithful arm.
- **Single model, locked.** No cross-model claim. Re-running `/spp-loop` against another
  model is the documented response to a model swap.

---

## 7. Provenance

- Plan/contract: `config/plan.md` v3, `config/loop_spec.md`.
- Per-iteration artifacts: `runs/gpt-5-nano/run_01..05/` (prompt, results, eval,
  discrepancy_analysis, auditor_review).
- Termination: `runs/gpt-5-nano/EARLY_STOP.md`.
- Test eval: `runs/gpt-5-nano/finalize/test_eval.json`, `test_results.json`.
- Gates G1–G5 approved by the user; recorded in `config/plan.md` §11.
