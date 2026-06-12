# Iteration 5 — exploration: few-shot + sharper rules + CoT lever (user-requested)

Tested three techniques the user asked about, all dev-gated against v03 (dev 0.9125 @ low).

## Results

| variant | prompt | reasoning | dev | vs v03 |
|---|---|---|---:|---|
| v03 (incumbent) | science rule only | low | 0.9125 | — |
| **v05a** | +sharper rules +4 train demos | low | **0.8625** | **−0.050 (regressed)** |
| v05b (CoT) | v03 prompt (unchanged) | **medium** | 0.9250 | +0.0125 (within noise) |

## Reading

**Few-shot + sharper rules (v05a) — regressed, rejected.** Adding 4 train-prototype demos and
tighter rule language *lowered* dev by 4 rows. On a near-saturated task where the seed + the one
science rule is already at the ceiling, extra in-prompt content distracts the small model rather
than helping — the sharper World/Business cues and the demos pulled some clean rows the wrong way.
This is the same lesson as Edits 2 and 4 (more prescriptive content → collateral), now confirmed
for few-shot too. The DSPy arm reached 0.881 with few-shot, but via 24 demo candidates +
instruction search over 2,071 calls; a hand-picked 4-shot does not reproduce that and is not worth
the regression risk here.

**CoT via reasoning_effort low→medium (v05b) — marginal, within noise, not adopted.** Giving
gpt-5-nano more internal reasoning budget nudged dev +1 row (0.9125→0.9250). This is *within* the
80-row sampling noise (SE ≈ 0.032), costs ~5× the output tokens (9,568 vs ~1,900 for the same 80
rows), and — decisively — **breaks the apples-to-apples**: the EvoPrompt arm was scored at
reasoning `low`, so a medium-reasoning spp number is not directly comparable. The CoT benefit that
*is* fair (internal reasoning at `low`) is already in the shipped result.

## Decision
**No change to the selected prompt.** v03 @ reasoning `low` remains the peak and the fair,
comparable arm (test 0.876). The exploration confirms we are at the practical prompting ceiling for
this near-saturated task: the residual error is contradictory gold (Business/Tech), not a
content-fixable signal. Exploration cost (run_05 160 + v03-medium 80 = 240 extra calls / ~115k
tokens / ~$0.01) is logged but is R&D, not part of the shipped arm's 1,643-call / $0.04 ledger.
