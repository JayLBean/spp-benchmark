<task>
Examine the movie-review sentence provided and classify its sentiment into exactly one of five ordinal categories, ordered from most negative to most positive: terrible < bad < okay < good < great.
</task>

<rules>
- great — sustained, unqualified enthusiasm: superlatives, "one of the best", "a triumph", or multiple strong positives.
- good — mildly positive: praise that is single-note, qualified, or carries reservations. Do not force a mild positive up to great.
- okay — neutral or mixed: lukewarm, noncommittal, faintly dismissive, or explicitly balanced (genuine praise AND genuine fault). Do not force a mild or mixed review to a pole.
- bad — mildly negative: a specific weakness or disappointment in an otherwise competent film.
- terrible — strongly negative: pervasive or unredeemed failure — fails broadly, no redeeming notes, or strongly repellent.
</rules>

<output_format>
Respond with exactly one word — the category in lowercase (terrible, bad, okay, good, or great) — and nothing else. No punctuation, no explanation.
</output_format>
