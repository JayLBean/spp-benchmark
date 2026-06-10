# spp-bm — Supervised Prompt Producer benchmark

Head-to-head: **spp** (human-in-the-loop) vs **EvoPrompt** (automated evolutionary
prompt optimization) on three canonical text-classification datasets, both scored on
the **same local task model**.

## The fairness invariant

The *task model* is identical across every arm: **gpt-oss-20b** served locally by oMLX
(OpenAI-compatible, `http://127.0.0.1:8000/v1`). Only *who writes the prompt* varies.
Every arm is scored 0-shot through the **same wrapper** (`scripts/llm_client.py` +
`run_evoprompt.evaluate`) on the **same sacred test rows**. Published paper numbers
(Alpaca-7b / text-davinci-003) are **reference only** — see EvoPrompt, Guo et al.,
ICLR 2024 (arXiv:2309.08532).

## Tasks

| Task | Kind | #classes | shared test | baseline pool | metric |
|------|------|---------:|------------:|--------------:|--------|
| AG News | topic | 4 | 1,000 | 1,000 | accuracy |
| SST-5 | fine-grained sentiment | 5 | 1,000 | 1,000 | accuracy |
| TREC | question type (coarse) | 6 | 500 | 1,000 | accuracy |

Label names follow EvoPrompt's verbalizers. The shared test is stratified from each
HF *test* split; the baseline pool is stratified from each HF *train* split, disjoint
from the test by construction. EvoPrompt's dev (200) is a subset of the baseline pool,
so both arms draw training-side data from one shared pool.

## Layout

```
scripts/
  llm_client.py      shared oMLX client (the one task-model surface)
  build_fixtures.py  HF -> fixtures/ + baselines/ (deterministic, seed=5)
  run_evoprompt.py   EvoPrompt-GA arm (faithful reimpl; 0-shot; presets)
  score_prompt.py    score ANY prompt on a task's sacred test (the spp arm)
  make_seed.py       baselines/<task>/SEED.md briefs for /spp-init
  compare.py         final table across arms
fixtures/<task>/     dev.jsonl, test.jsonl, metadata.json, evoprompt/{dev,test}.txt
baselines/<task>/    baseline.csv (UNSPLIT), test_holdout.csv (shared test), SEED.md
results/<arm>/<task>/ result.json (+ run.log, checkpoint.json for evoprompt)
evoprompt/upstream/  vendored beeevita/EvoPrompt (gitignored; init prompts + GA template)
```

## Setup

```sh
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
export OMLX_BASE_URL=http://127.0.0.1:8000/v1 OMLX_API_KEY=jaywell06 \
       OMLX_MODEL=gpt-oss-20b-MXFP4-Q8
# fixtures (already built; re-run only to regenerate)
git clone --depth 1 https://github.com/beeevita/EvoPrompt.git evoprompt/upstream
HF_DATASETS_CACHE=$PWD/data/hf_cache ./.venv/bin/python scripts/build_fixtures.py
```

## The three arms

**1. EvoPrompt (automated).** Evolves a prompt against the dev set, scores the best on
the sacred test. ~2.5 h/task at the `default` preset (gpt-oss reasons ~150 tok/call and
oMLX serializes at ~2.6s/call — the search cost sets wall-clock).

```sh
./.venv/bin/python scripts/run_evoprompt.py --tasks ag_news sst5 trec --preset default
```

**2. spp (human-in-the-loop).** In the spp plugin, run `/spp-init` seeded by
`baselines/<task>/SEED.md`, feed `baseline.csv` (unsplit), and register
`test_holdout.csv` as the sacred test. Run the loop. Then score spp's final prompt on
the identical test set:

```sh
./.venv/bin/python scripts/score_prompt.py --task sst5 --prompt-file <spp_prompt.txt>
```

**3. Compare.**

```sh
./.venv/bin/python scripts/compare.py
```

## Caveat: expect saturation

gpt-oss-20b is far stronger than the paper's Alpaca-7b, so absolute accuracies land
well above the paper. AG News may sit near ceiling (little headroom to separate the
arms); **SST-5 and TREC** carry the genuine signal — fine-grained degree boundaries and
answer-type subtleties are where prompt wording, and the spp loop, can actually move
the number.
