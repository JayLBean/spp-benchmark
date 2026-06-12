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
tokens only. Directly comparable to the EvoPrompt arm above.

| arm | calls | input_tokens | output_tokens | total_tokens | test_acc |
|---|---:|---:|---:|---:|---:|
| **spp_gpt5nano** | **1,803** | **697,609** | **166,658** | **864,267** | **0.579** |
| evoprompt_gpt5nano | 4,368 | 289,403 | 494,455 | 783,858 | 0.561 |

**Read:** spp reaches **higher test accuracy (0.579 vs 0.561, +1.8 pts; +2.2 over the
shared seed 0.557) with 2.4× fewer task-model calls (1,803 vs 4,368).** Total tokens are
~10% higher (864k vs 784k) because spp's six-section refined prompt carries more input
per call, concentrated in the one-time 1,000-row test scoring (436k input there alone);
spp's *search* cost only 337k over 5 iterations vs EvoPrompt's population×generations
search. Per cost_report.py's framing, spp additionally offloads the optimization
reasoning to Claude subagents + the human, which this gpt-5-nano-only ledger does not
bill.
