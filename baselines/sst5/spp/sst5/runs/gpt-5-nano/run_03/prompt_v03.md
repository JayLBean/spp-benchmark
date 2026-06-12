<task>
Examine the movie-review sentence provided and classify its sentiment into exactly one of five ordinal categories, ordered from most negative to most positive: terrible < bad < okay < good < great.
</task>
<rules>
- great — sustained, unqualified enthusiasm: superlatives, "one of the best", "a triumph", or multiple strong positives.
- good — mildly positive: praise that is single-note, qualified, or carries reservations. Do not force a mild positive up to great. A mixed review that nets positive (genuine praise outweighing its faults) also lands here.
- okay — genuinely neutral: lukewarm, noncommittal, faintly dismissive, or evenly balanced with no clear lean. Reserve okay for reviews with no net verdict either way; if a mixed review leans positive choose good, if it leans negative choose bad.
- bad — mildly negative: a specific weakness or disappointment in an otherwise competent film, or a mixed review that nets negative. Use bad only when the film retains some merit.
- terrible — strongly or broadly negative: pervasive or unredeemed failure — fails broadly, has no redeeming element, or lacks purpose/point as a whole. Across-the-board negativity counts as terrible EVEN when stated calmly or with understatement; do not soften it to bad. Reserve bad for a specific flaw amid some merit.
</rules>
<output_format>
Respond with exactly one word — the category in lowercase (terrible, bad, okay, good, or great) — and nothing else. No punctuation, no explanation.
</output_format>
