# trec — spp seed brief

Seed for `/spp-init`. The benchmark harness already built the labeled data;
this brief just gives the consultation its starting facts.

## Task

Question classification: what *type of answer* the question expects (not its topic). 'What is the capital of France?' -> Location (the answer is a place). Expression is rare (abbreviations/definitions) and easy to miss; Entity vs Description is subtle.

- **Output:** one label per row (single-field, K=1). **Metric:** accuracy.
- **Classes (6):**

  | label | meaning |
  |---|---|
  | `Description` | answer is a definition/description/manner/reason |
  | `Entity` | answer is a thing (animal, color, product, ...) |
  | `Expression` | answer is an abbreviation or its expansion |
  | `Human` | answer is a person or group |
  | `Location` | answer is a place |
  | `Number` | answer is a count, date, distance, money, ... |

## Data (already prepared — do NOT re-label, do NOT re-split here)

- **`baseline.csv`** — 1000 labeled rows, UNSPLIT. This is spp's pool; spp carves its own dev/train. Columns: `row_id,text,label`.
- **`test_holdout.csv`** — 500 rows, the SHARED SACRED test. Identical rows the EvoPrompt arm scored on. Register this as spp's test set so the comparison is apples-to-apples; never let the loop see it.

## Reference (NOT a target)

Paper Alpaca-7b accuracy (EvoPrompt, ICLR 2024): manual 50.6, APE 58.73, EvoPrompt 64.0. Our task model is gpt-oss-20b, so absolute numbers differ — only the same-model EvoPrompt vs spp comparison on the shared test set is meaningful.

## Scoring spp's final prompt

```sh
python scripts/score_prompt.py --task trec --prompt-file <spp_prompt.txt>
```
