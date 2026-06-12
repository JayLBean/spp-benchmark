# Token usage — spp arm, sst5 (gpt-5-nano)

Cumulative gpt-5-nano task-model tokens consumed by the spp loop, in the same
shape as `../../scripts/cost_report.py` so it is directly comparable to the
EvoPrompt arm. spp's "optimizer cost" (Claude subagent tokens + human time)
lives elsewhere and is not billed here — only gpt-5-nano task-model tokens.

**Comparison target — EvoPrompt arm (same model, gpt-5-nano):**

| arm | calls | input_tokens | output_tokens | total_tokens | test_acc |
|---|---:|---:|---:|---:|---:|
| evoprompt_gpt5nano | 4,368 | 289,403 | 494,455 | 783,858 | 0.561 |

## spp per-run ledger

| run | stage | calls | input_tokens | output_tokens | total_tokens | cumulative_total |
|---|---|---:|---:|---:|---:|---:|
| dryrun | infer | 3 | 251 | 222 | 473 | 473 |
| run_01 | infer | 160 | 13,486 | 12,754 | 26,240 | 26,713 |
| run_02 | infer | 160 | 42,446 | 14,673 | 57,119 | 83,832 |
| run_03 | infer | 160 | 56,686 | 16,273 | 72,959 | 156,791 |
| run_04 | infer | 160 | 69,646 | 15,245 | 84,891 | 241,682 |
| run_05 | infer | 160 | 79,086 | 16,239 | 95,325 | 337,007 |
| finalize_test | infer | 1,000 | 436,008 | 91,252 | 527,260 | 864,267 |

## spp cumulative total

Final, at /spp-finalize (search loop + sacred-test scoring), gpt-5-nano task-model
tokens only. **Verified against the OpenAI dashboard (Jun 12):** total requests 1,803 ✓
and input tokens 697,609 ✓ both match exactly; total spend **$0.10** matches the
cost computed below. (The dashboard's "Total tokens" headline shows *input* tokens;
completion/reasoning output tokens are billed separately and are included in the $ cost.)

| arm | calls | input_tokens | output_tokens | total_tokens | **cost (USD)** | test_acc |
|---|---:|---:|---:|---:|---:|---:|
| **spp_gpt5nano** | **1,803** | **697,609** | **166,658** | **864,267** | **$0.10** | **0.579** |
| evoprompt_gpt5nano | 4,368 | 289,403 | 494,455 | 783,858 | $0.21 | 0.561 |

Cost uses gpt-5-nano list pricing **$0.05/1M input, $0.40/1M output** (the $0.10 spp figure
reproduces the dashboard's spend to the cent; no prompt caching was in play — spp's
~430-token system prompt is below gpt-5-nano's 1024-token cache threshold).

**Read (the efficiency axis, corrected):** spp wins a clean sweep —
**+1.8 accuracy points (0.579 vs 0.561), 2.4× fewer task-model calls (1,803 vs 4,368),
and ~2.1× cheaper ($0.10 vs $0.21).** Raw *token count* is the misleading metric here:
spp's total (864k) edges above EvoPrompt's (784k), but output tokens cost 8× input, and
the two arms have opposite profiles — spp is **input-heavy / output-light** (one rich,
static six-section prompt replayed per row; 167k output) while EvoPrompt is
**output-heavy** (population × generations of GA text + per-call reasoning; 494k output).
On the metric that bills — dollars — spp is half the cost. (Per cost_report.py's framing,
spp additionally offloads the optimization *reasoning* to Claude subagents + the human,
which this gpt-5-nano-only ledger does not bill at all.)