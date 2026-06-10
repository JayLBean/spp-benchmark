# ag_news — spp seed brief

Seed for `/spp-init`. The benchmark harness already built the labeled data;
this brief just gives the consultation its starting facts.

## Task

News topic classification. Each row is a news article (title + first sentences). Assign exactly one topic. Boundaries are usually clear; Business vs Tech is the main genuine ambiguity (a software-company earnings story can read as either).

- **Output:** one label per row (single-field, K=1). **Metric:** accuracy.
- **Classes (4):**

  | label | meaning |
  |---|---|
  | `World` | international / political news |
  | `Sports` | sports |
  | `Business` | business, finance, markets |
  | `Tech` | science and technology |

## Data (already prepared — do NOT re-label, do NOT re-split here)

- **`baseline.csv`** — 1000 labeled rows, UNSPLIT. This is spp's pool; spp carves its own dev/train. Columns: `row_id,text,label`.
- **`test_holdout.csv`** — 1000 rows, the SHARED SACRED test. Identical rows the EvoPrompt arm scored on. Register this as spp's test set so the comparison is apples-to-apples; never let the loop see it.

## Reference (NOT a target)

Paper Alpaca-7b accuracy (EvoPrompt, ICLR 2024): manual 70.63, APE 71.76, EvoPrompt 73.82. Our task model is gpt-oss-20b, so absolute numbers differ — only the same-model EvoPrompt vs spp comparison on the shared test set is meaningful.

## Scoring spp's final prompt

```sh
python scripts/score_prompt.py --task ag_news --prompt-file <spp_prompt.txt>
```
