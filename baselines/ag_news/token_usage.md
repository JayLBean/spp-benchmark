# Token usage — spp arm, ag_news (gpt-5-nano)

Cumulative gpt-5-nano task-model tokens consumed by the spp loop, in the same
shape as `../../scripts/cost_report.py` so it is directly comparable to the
EvoPrompt arm. spp's "optimizer cost" (Claude subagent tokens + human time)
lives elsewhere and is not billed here — only gpt-5-nano task-model tokens.

Cost axis (the honest one): gpt-5-nano list pricing **$0.05/1M input + $0.40/1M
output**. Output is 8× input, so dollars — not raw token count — is the fair
cross-arm comparator.

**Comparison target — EvoPrompt arm (same model, gpt-5-nano):**

| arm | calls | input_tokens | output_tokens | total_tokens | cost (USD) | test_acc |
|---|---:|---:|---:|---:|---:|---:|
| evoprompt_gpt5nano | 4,288 | 394,645 | 400,068 | 794,713 | $0.18 | 0.869 |

(EvoPrompt's GA did not beat its seed: best_prompt == the shared seed, test 0.870.
ag_news is near-saturated, so the realistic spp target is matching ~0.87 without
overfitting, not a large gain.)

## spp per-run ledger

| run | stage | calls | input_tokens | output_tokens | total_tokens | cumulative_total |
|---|---|---:|---:|---:|---:|---:|
| dryrun | infer | 3 | 352 | 30 | 382 | 382 |
| run_01 | infer | 160 | 19,341 | 4,993 | 24,334 | 24,716 |
| run_02 | infer | 160 | 59,501 | 4,032 | 63,533 | 88,249 |
| run_03 | infer | 160 | 42,061 | 3,713 | 45,774 | 134,023 |
| run_04 | infer | 160 | 50,701 | 3,712 | 54,413 | 188,436 |
| finalize_test | infer | 1,000 | 258,896 | 26,580 | 285,476 | 473,912 |
| run_05 (R&D) | infer | 160 | 81,261 | 3,840 | 85,101 | 559,013 |
| run_05_v03med (R&D) | infer | 80 | 20,871 | 9,568 | 30,439 | 589,452 |

> **run_05 rows are post-finalize R&D**, not part of the shipped arm: an exploration of
> few-shot + sharper rules (regressed: dev 0.8625) and a CoT lever via reasoning_effort=medium
> (marginal: dev 0.9250, within noise, breaks the `low` apples-to-apples). Both rejected; the
> selected prompt and the shipped-arm total below are unchanged. Exploration added 240 calls /
> 115,540 tokens / ~$0.01.

## spp cumulative total

Final, at /spp-finalize (4-iteration search loop + sacred-test scoring), gpt-5-nano
task-model tokens only. Loop search = 643 calls / 188,436 tok; sacred-test scoring =
1,000 calls / 285,476 tok. Cost at gpt-5-nano list pricing **$0.05/1M input + $0.40/1M
output**.

| arm | calls | input_tokens | output_tokens | total_tokens | **cost (USD)** | test_acc |
|---|---:|---:|---:|---:|---:|---:|
| **spp_gpt5nano** | **1,643** | **430,852** | **43,060** | **473,912** | **$0.04** | **0.876** |
| dspy_gpt5nano (MIPROv2 few-shot) | 2,071 | 1,327,021 | 205,039 | 1,532,060 | $0.15 | 0.881 |
| evoprompt_gpt5nano | 4,288 | 394,645 | 400,068 | 794,713 | $0.18 | 0.869 |

Cost: spp 430,852×$0.05/1M + 43,060×$0.40/1M = $0.0215 + $0.0172 = **$0.0388 ≈ $0.04**;
DSPy 1,327,021×$0.05/1M + 205,039×$0.40/1M = $0.0664 + $0.0820 = **$0.148 ≈ $0.15**;
EvoPrompt 394,645×$0.05/1M + 400,068×$0.40/1M = **$0.180**.

### Dashboard verification (OpenAI usage, Jun 12 2026)

The **loop** portion is verified exactly against the OpenAI usage dashboard:

| metric | dashboard | spp loop ledger | match |
|---|---:|---:|:--:|
| total requests | 643 | 643 (dryrun 3 + run_01..04 640) | ✓ |
| total tokens (headline) | 171,956 | 171,956 **input** tokens | ✓ |
| total spend | $0.02 | $0.0152 (→ $0.02) | ✓ |

**Key nuance (same as the sst5 arm):** the dashboard's headline **"Total tokens" counts INPUT
tokens only** (171,956 = the loop's input). Output tokens — which for gpt-5-nano include the
reasoning tokens — are billed separately and are folded into the $ figure; they are *not* in the
171,956 headline. No prompt caching was in play (the prompt is below gpt-5-nano's 1024-token cache
threshold).

The **finalize** sacred-test pass (1,000 requests, +258,896 input / +26,580 output, ≈ $0.02) was
captured at the API layer by the run's usage-tee and will add to the dashboard once it propagates;
the full shipped arm is therefore **1,643 requests / 430,852 input / $0.04** (loop $0.02 verified +
finalize $0.02 measured). The 240 post-finalize **R&D** calls (run_05 exploration) are excluded from
the shipped-arm total and tracked separately above.

**Read (the efficiency axis):** On accuracy, the three arms are within a **single standard error**
of each other (test SE ≈ 0.0104 on 1,000 rows): DSPy 0.881, spp 0.876, EvoPrompt 0.869 — the
spp↔DSPy 0.5-pt gap is **statistically tied**. The separation is in **cost**: spp **$0.04** vs DSPy
**$0.15** (~3.8×) vs EvoPrompt **$0.18** (~4.6×). So spp is *not* worse than DSPy — it matches DSPy's
accuracy within noise at roughly a quarter of the dollar cost, and beats EvoPrompt outright on both
axes. spp is **input-heavy / output-light** (one static six-section prompt replayed per row; 43k
output) while EvoPrompt is **output-heavy** (GA population × generations + per-call reasoning; 400k
output) and DSPy is **input-heavy** (24 demo candidates × bootstrapped few-shot search; 1.33M input).
spp converged in just 4 short iterations because the seed was already near the saturation ceiling, so
the loop's job was to add the one categorical rule (science→Tech) that moved the needle and then stop.
(Per cost_report.py's framing, spp additionally offloads the optimization *reasoning* to Claude
subagents + the human, which this gpt-5-nano-only ledger does not bill at all.)
