# Auditor review — run_05 (Edit 5: sharper rules + 4 train-split few-shot demos; CoT via reasoning_effort)

**Available:** prompt diff v03→v05; plan.md §2 + §10 (few-shot deferred: "examples from the
train split exclusively"); prior auditor reviews. **Withheld:** all scores.

## Edit 5a — sharper rule descriptions
Tightens the four class definitions with categorical disambiguation cues (World absorbs
*governmental/geopolitical* trade; Tech explicitly includes space agencies/telecom). Restates class
boundaries, names no row. The cues lean on the *science→Tech* direction proven safe in run_03 and
avoid the Business-pushing language that caused the run_02/run_04 collateral. **Categorical.**

## Edit 5b — 4 few-shot exemplars (one per class)
The demos are drawn from the **train** split (ids 0192/0162/0146/0617), never dev or test — verified
against splits.json. They are *prototypical* class anchors (a conflict story=World, an NBA game=Sports,
a casino capex=Business, a NASA Mars mission=Tech), each illustrating a class *definition*, not
patching a specific dev/test failure. The Tech demo deliberately reinforces the generalizing
science→Tech rule. This is the §10-sanctioned train-only few-shot path.

**Row-specific-patch check:** the demos are not dev/test rows and were chosen as class prototypes, not
to flip named evaluation rows. No dev/test leakage (train-sourced). **Categorical (train-prototype
few-shot), permitted.**

## Edit 5c — CoT lever: reasoning_effort low→medium (tested separately)
This is a *runner/model-config* knob, not prompt content — outside the auditor's prompt-edit remit. Noted
for transparency: it is tested on dev as a fairness-flagged side experiment (EvoPrompt's arm used `low`),
not a prompt edit. No row targeting.

## Gate decision
Edits 5a/5b **categorical**, 0 row-specific, 0 unclear. Gate **auto-advances**; score prompt_v05 on
dev+train (reasoning low = the fair arm) and additionally on dev at reasoning medium (CoT lever). Per
the loop's stop rule, v05 is retained only if it beats v03 (dev 0.9125); otherwise v03 stays the peak.
