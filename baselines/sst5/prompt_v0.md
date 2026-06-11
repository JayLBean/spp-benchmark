<!--
prompt_v0.md — the SHARED STARTING PROMPT for sst5 (spp-bm).

This is the EXACT prompt the EvoPrompt arm started from (its manual_init, the best
upstream human prompt — the baseline EvoPrompt was measured against:
manual_init_test_acc = 0.557; EvoPrompt's GA evolved a different prompt to 0.561).

It is intentionally a bare 0-shot instruction with NO label definitions, NO worked
examples, NO disambiguation rules — that is what makes the spp-vs-EvoPrompt comparison
apples-to-apples. Whatever structure spp's loop adds (six-section form, categorical
label rules, etc.) is spp's measured contribution, started from the same seed EvoPrompt
had. Do not pre-enrich this prompt.
-->

Examine the comment provided and classify it into one of five categories: terrible, bad, okay, good, or great.
