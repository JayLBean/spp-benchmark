# Loop termination — EARLY_STOP

**Task:** ag_news · **Model:** gpt-5-nano · **Stopped at:** iteration 4 of MAX 10

## Reason

Single clear dev peak at **prompt_v03** with both subsequent categorical attempts at the only
remaining boundary (Business/Tech) net-regressing dev. The remaining error mass is **contradictory
gold** (telecom corporate news → Business, but IBM/Apple corporate news → Tech), not a
prompt-fixable signal. Continuing iterates on ±1-row noise over an 80-row dev → overfitting.
EARLY_STOP, selecting the best-dev prompt.

## Selected prompt: `run_03/prompt_v03.md`

The bare EvoPrompt seed reframed into the six-section structure plus **one** clean, one-directional
categorical rule: **Tech = science AND technology** (research, nature, space, medicine, internet),
not gadgets-only — so science/nature stories framed as world news land in Tech.

## Dev trajectory

| iter | prompt | edit | dev | train | decision |
|---|---|---|---:|---:|---|
| 1 | v01 | bare seed + output directive | 0.8875 | 0.8750 | baseline |
| 2 | v02 | +Edit 1 (science→Tech) +Edit 2 (company-subject) | 0.8750 | 0.8750 | Edit 2 collateral → revert |
| 3 | v03 | Edit 1 only (drop Edit 2) | **0.9125** | 0.8875 | **best — selected** |
| 4 | v04 | +Edit 4 (narrow Tech-pull) | 0.9000 | 0.8875 | regress (contradictory gold) → reject |

## Methodology integrity

- Every edit (1–4) reviewed by the **score-blind auditor** → all **categorical**; **0 row-specific,
  0 unclear, 0 overrides**.
- **No few-shot examples** added (apples-to-apples with EvoPrompt's seed preserved — the only
  added content is categorical class-boundary language).
- **Overfit guard never tripped** (train − dev never exceeded 0.15; dev ran *above* train).
- **Sacred test never read** during the loop (runner hard-refusal enforced).

## Search cost (loop only, gpt-5-nano task-model tokens)

dryrun + run_01..04 = 643 calls / 188,436 tokens (see `token_usage.md`). Sacred-test scoring is
added at `/spp-finalize`.

## Next

`/spp-finalize` — score prompt_v03 on the sacred test (1000 rows) exactly once; G5 then G6.
