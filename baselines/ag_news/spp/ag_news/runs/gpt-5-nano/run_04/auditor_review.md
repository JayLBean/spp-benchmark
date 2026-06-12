# Auditor review — run_04 (Edit 4: Tech-pulling-only company rule)

**Available:** prompt diff v03→v04; run_03 discrepancy_analysis.md; plan.md §2; prior auditor
reviews (run_02, run_03). **Withheld:** all scores.

## Edit 4 — "computing/internet/software/telecom/electronics company event → Tech"

The diff adds one `<rules>` line that pulls computing/internet/software/telecom/electronics
company stories to `Tech` when the news peg is a corporate event. It deliberately omits the
"purely financial → Business" half that the run_02 analysis blamed for collateral.

1. **Categorical?** Yes. It is scoped to a *class of companies* (computing/internet/software/
   telecom/electronics), not to AOL, Apple, or IBM by name. It would relabel any story whose
   subject is such a company on a corporate-event peg, seen or unseen. plan.md §2 names the
   Business/Tech corporate-event ambiguity as "the chief ambiguity", so an edit here is on-target
   for a real boundary, not a dev artifact.

2. **Row-specific smuggling?** No named row, no few-shot example. The edit names company
   *categories* and event *types*, both general.

3. **Is the asymmetry (Tech-pull, no Business-push) a hidden row patch?** No — it is a principled
   narrowing learned from a *categorical* failure mode (the Business-push clause keyed on the word
   "launch" and mis-fired on a sports launch). Dropping a clause that over-generalizes is itself
   categorical.

## Gate decision
**Categorical**, 0 row-specific, 0 unclear. Gate **auto-advances**; score prompt_v04 on dev+train.
Per the loop's stop rule, v04 is retained only if it beats v03 (0.9125) on dev; otherwise v03 is
the selected peak.
