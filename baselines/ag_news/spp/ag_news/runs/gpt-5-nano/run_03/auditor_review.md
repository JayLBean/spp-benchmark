# Auditor review — run_03 (Edit 3: keep science rule, revert company-subject rule)

**Available:** prompt diff v02→v03; run_02 discrepancy_analysis.md; plan.md §2; prior auditor
review (run_02). **Withheld:** all v02/v03 scores.

## Edit 3 — revert the company-subject rule; retain the science clarification

The diff removes the `<rules>` line about technology-company corporate events and softens the
Business/Tech definitions back to plain class descriptions; it retains the "Tech = science AND
technology" clarification. Two questions for a score-blind auditor:

1. **Is the retained edit categorical?** Yes — "Tech covers science/research/nature/space/
   medicine/internet" is a class-definition restatement, consistent with plan.md §2's `Tech`
   definition. Generalizes to any science story, names no row.

2. **Is the *reversion* legitimate, or is it score-chasing a row set?** The reversion drops a
   rule that the discrepancy analysis judged to cause *categorical* collateral (a Business
   keyword-trigger on "deal/launch" language that misfires on Sports and general rows). Removing a
   rule that over-generalizes is itself a categorical action — it does not encode any specific
   row, and the resulting prompt is *simpler* (fewer prescriptive clauses), which is the opposite
   of overfitting. The decision of *which* categorical edit to keep is the loop's to make on the
   dev signal; the auditor's concern — that no edit smuggles in row-specific patches — is
   satisfied: v03 contains zero row references and zero few-shot examples.

## Gate decision
Edit **categorical**, reversion **legitimate** (simplifying, no row targeting). **0 row-specific,
0 unclear.** Gate **auto-advances**; score prompt_v03 on dev+train.
