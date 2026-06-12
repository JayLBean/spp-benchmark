# Auditor review — run_02 (edits proposed from run_01 discrepancy)

**Information available to the auditor:** prompt diff v01→v02; run_01 discrepancy_analysis.md;
plan.md §2 (label definitions & known borderline cases); prior auditor reviews (none).
**Information withheld (non-negotiable):** any v02 scores — the auditor has not seen and cannot
see how v02 performs. Verdict is on the *nature* of each edit, not its effect on the metric.

## Edit 1 — "Tech = science AND technology (research, nature, space, medicine, internet), not only gadgets"

**Verdict: categorical.**
The edit restates a class *definition* — it widens the model's reading of the `Tech` label to the
full AG News Sci/Tech scope, which plan.md §2 already defines ("Science and technology: gadgets,
software, research, space, internet"). It names no specific dev/train row, no entity, no title. It
would change the label of *any* science/nature/discovery story, seen or unseen. This is a
generalizing convention edit, exactly the kind the methodology permits.

## Edit 2 — "tech/internet/software company: classify by primary subject (product→Tech, pure financial event→Business)"

**Verdict: categorical.**
The edit encodes a *boundary convention* between two classes (the Business/Tech ambiguity plan.md
§2 flags explicitly as "the chief ambiguity"). It is phrased as a general decision procedure —
"primary subject is the product/technology → Tech; company incidental to a financial story →
Business" — applicable to any company story, not a list of named companies. It names no row. The
discrepancy analysis is candid that the gold is noisy here (the Amazon A9 counter-example) and that
the rule is expected to *net*-help rather than resolve every case; that honesty is consistent with a
categorical edit (it does not secretly target specific rows to force the score up).

## Cross-check: were any row-specific patches smuggled in?

No. The discrepancy analysis explicitly *excluded* the noise rows (Davis Cup→World, carbon-monoxide
students→Tech, mixed World/Business trade rows) from the edits and left them to the model's prior.
The two edits touch only `<rules>` class-boundary language; `<task>` and `<output_format>` are
unchanged except for adding the four-class framing. No example rows were added (no few-shot from any
partition).

## Gate decision

Both edits **categorical** → **0 row-specific, 0 unclear**. The per-iteration auditor gate
**auto-advances**; the loop proceeds to score prompt_v02 on dev+train. No human halt required.
