# sst5 — spp seed brief

Seed for `/spp-init`. The benchmark harness already built the labeled data;
this brief just gives the consultation its starting facts.

## Task

Fine-grained sentiment of a movie-review sentence on a 5-point scale. The hard part is the *degree* boundaries — terrible vs bad, good vs great, and the okay/neutral middle — not polarity. This is where prompt wording earns its keep.

- **Output:** one label per row (single-field, K=1). **Metric:** accuracy.
- **Classes (5):**

  | label | meaning |
  |---|---|
  | `terrible` | strongly negative |
  | `bad` | mildly negative |
  | `okay` | neutral / mixed |
  | `good` | mildly positive |
  | `great` | strongly positive |

## Data (already prepared — do NOT re-label, do NOT re-split here)

- **`baseline.csv`** — 1000 labeled rows, UNSPLIT. This is spp's pool; spp carves its own dev/train. Columns: `row_id,text,label`.
- **`test_holdout.csv`** — 1000 rows, the SHARED SACRED test. Identical rows the EvoPrompt arm scored on. Register this as spp's test set so the comparison is apples-to-apples; never let the loop see it.

## Reference (NOT a target)

Paper Alpaca-7b accuracy (EvoPrompt, ICLR 2024): manual 42.9, APE 46.32, EvoPrompt 49.91. Our task model is gpt-oss-20b, so absolute numbers differ — only the same-model EvoPrompt vs spp comparison on the shared test set is meaningful.

## Scoring spp's final prompt

```sh
python scripts/score_prompt.py --task sst5 --prompt-file <spp_prompt.txt>
```
