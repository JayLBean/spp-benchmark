# spp-bm — Supervised Prompt Producer benchmark

Head-to-head comparison of **spp** (human-in-the-loop) against **EvoPrompt**
(automated evolutionary prompt optimization) on three canonical text-classification
datasets, both scored on the **same local task model**.

## The fairness invariant

The *task model* is identical across every arm: **gpt-oss-20b** served locally by
oMLX (OpenAI-compatible, `http://127.0.0.1:8000/v1`). Only *who writes the prompt*
varies. Published paper numbers (Alpaca-7b / text-davinci-003) are **reference only**,
never the target — see EvoPrompt, Guo et al., ICLR 2024 (arXiv:2309.08532).

## Tasks

| Task | Kind | #classes | Test | Metric |
|------|------|---------:|-----:|--------|
| AG News | topic | 4 | 7,600 | accuracy |
| SST-5 | fine-grained sentiment | 5 | 2,210 | accuracy |
| TREC | question type (coarse) | 6 | 500 | accuracy |

## Layout

- `scripts/llm_client.py` — shared oMLX client (the one task-model surface).
- `fixtures/<task>/` — `dev.jsonl`, `test.jsonl`, `metadata.json`.
- `evoprompt/` — EvoPrompt arm (upstream vendored under `upstream/`, patched to oMLX).
- `results/evoprompt/<task>/` — best prompt + dev curve + final test accuracy.
- `baselines/<task>/` — `baseline.csv` (unsplit, for spp) + `SEED.md` + shared `test_holdout.csv`.

## Three arms

1. **Collect** — fixtures + metadata (Phase 1).
2. **EvoPrompt on gpt-oss-20b** — automated baseline, scored on the sacred test (Phase 2).
3. **spp on gpt-oss-20b** — human-in-the-loop, scored on the *same* test set (Phase 3 preps inputs).

## Env

```sh
export OMLX_BASE_URL=http://127.0.0.1:8000/v1
export OMLX_API_KEY=jaywell06
export OMLX_MODEL=gpt-oss-20b-MXFP4-Q8
```
