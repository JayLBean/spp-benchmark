<!--
prompt_v0.md — the SHARED STARTING PROMPT for trec (spp-bm).

This is the EXACT prompt the EvoPrompt arm started from (its manual_init, the best
upstream human prompt — also the baseline EvoPrompt was measured against:
manual_init_test_acc = 0.828, and EvoPrompt's GA did not beat it).

It is intentionally a bare 0-shot instruction with NO label definitions, NO worked
examples, NO disambiguation rules — that is what makes the spp-vs-EvoPrompt comparison
apples-to-apples. Whatever structure spp's loop adds (six-section form, categorical
label rules, etc.) is spp's measured contribution, started from the same seed EvoPrompt
had. Do not pre-enrich this prompt.
-->

Determine the type of the given question and choose from Description, Entity, Expression, Human, Location and Number.
