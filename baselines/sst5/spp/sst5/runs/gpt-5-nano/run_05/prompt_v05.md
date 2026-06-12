<task>
Examine the movie-review sentence provided and classify its sentiment into exactly one of five ordinal categories, ordered from most negative to most positive: terrible < bad < okay < good < great.
</task>
<rules>
- great — strong, unqualified enthusiasm. A single clear, strong positive (e.g. wonderful, glorious, superb, highly engaging, wildly entertaining, sparkling) is enough; it need not stack multiple superlatives. Superlatives, "one of the best", or "a triumph" also qualify.
- good — mildly positive: praise that is single-note, qualified, or carries reservations. Do not force a mild positive up to great. A mixed review that nets positive (genuine praise outweighing its faults) also lands here.
- okay — genuinely neutral: lukewarm, noncommittal, faintly dismissive, or evenly balanced with no clear lean. A faint or dismissive remark that calls a film slight, routine, or unremarkable — but does not assert an actual failure or strong disappointment — stays here. Reserve okay for reviews with no net verdict either way; if a mixed review leans positive choose good, if it leans negative choose bad.
- bad — mildly negative: a specific weakness or disappointment in an otherwise competent film, or a mixed review that nets negative. Choose bad only when the review asserts a real weakness the film does not overcome, while the film retains some merit.
- terrible — strongly or broadly negative: pervasive or unredeemed failure — fails broadly, has no redeeming element, or lacks purpose/point as a whole. Across-the-board negativity counts as terrible EVEN when stated calmly or with understatement; do not soften it to bad. Reserve bad for a specific flaw amid some merit.
</rules>
<tie_breaks>
- terrible vs bad: when a review is negative and names NO redeeming quality at all, prefer terrible over bad. bad must carry at least one acknowledged merit or a single localized flaw; a wholly negative verdict with nothing positive defaults to terrible.
</tie_breaks>
<output_format>
Respond with exactly one word — the category in lowercase (terrible, bad, okay, good, or great) — and nothing else. No punctuation, no explanation.
</output_format>
