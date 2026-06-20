# spp-bm — Supervised Prompt Producer benchmark

A fair, single-task-model benchmark comparing three prompt-optimization methods —
**spp** (human-in-the-loop), **EvoPrompt** (genetic search), and **DSPy** (MIPROv2
few-shot) — on three public text-classification tasks. Every arm is scored on the
**same task model**, from the **same seed prompt**, on the **same sacred test rows**, and
compared in the one unit that is fair across them: **dollars**.

- **Live site:** <https://jaylbean.github.io/spp-benchmark/> — the full report plus
  per-task **loop logs** documenting every spp iteration and the human-in-the-loop gate
  exchange.
- **Full report (source of truth):** [`BENCHMARK_REPORT.md`](BENCHMARK_REPORT.md) — accuracy,
  cost, token breakdowns, and the fairness ledger.

## Headline result

Test accuracy and total gpt-5-nano spend (search + scoring) per arm. **Bold = best on that
task.** SE ≈ 0.010 (1,000 rows) / 0.014 (500 rows).

| Task | Seed | EvoPrompt | DSPy (few-shot) | **spp** |
|---|---:|---:|---:|---:|
| AG News | 0.870 | 0.869 / $0.18 | **0.881** / $0.15 | 0.876 / **$0.04** |
| SST-5 | 0.557 | 0.561 / $0.21 | **0.580** / $0.19 | 0.579 / **$0.10** |
| TREC | 0.828 | 0.804 / $0.24 | 0.874 / $0.18 | **0.924** / **$0.11** |
| Mean acc | 0.752 | 0.745 | 0.778 | **0.793** |

spp posts the highest mean accuracy and the lowest task-model cost on every task, wins TREC
outright (+5 over the nearest arm), and matches DSPy's *few-shot* accuracy with *zero*
demonstrations on AG News and SST-5. The honest caveat: this cost counts **task-model spend
only** — spp shifts its optimizer cost onto Claude subagents and a human, which is not billed
here. See [`BENCHMARK_REPORT.md`](BENCHMARK_REPORT.md) §4 for the full fairness ledger.

## The fairness invariant

Everything that could hand one method an unearned edge is held constant; the only free
variable is **who writes the prompt**.

- **One task model, scored one way.** Every arm is evaluated through the *same* model and the
  *same* label-matching wrapper. The published numbers use **gpt-5-nano** (OpenAI,
  `reasoning_effort=low`, `temperature=1.0`). The harness also drives a local
  OpenAI-compatible server (e.g. `gpt-oss-20b` via oMLX) — the rule is the same either way:
  *one* task-model surface shared by all arms.
- **One sacred test set.** The same held-out rows score every arm; no arm trains or searches
  on them.
- **One starting point.** All three arms begin from the *identical* seed prompt
  (`baselines/<task>/prompt_v0.md` = EvoPrompt's `manual_init`).

Published paper numbers (Alpaca-7b / text-davinci-003) are **reference only** — see EvoPrompt,
Guo et al., ICLR 2024 (arXiv:2309.08532).

## Tasks

| Task | Kind | #classes | Shared test | Baseline pool | Metric |
|------|------|---------:|------------:|--------------:|--------|
| AG News | topic | 4 | 1,000 | 1,000 | accuracy |
| SST-5 | fine-grained sentiment | 5 | 1,000 | 1,000 | accuracy |
| TREC | question type (coarse) | 6 | 500 | 1,000 | accuracy |

Label names follow EvoPrompt's verbalizers. The shared test is stratified from each HF *test*
split; the baseline pool is stratified from each HF *train* split, disjoint from the test by
construction. EvoPrompt's dev (200) is a subset of the baseline pool, so the search-based arms
draw training-side data from one shared pool.

## The three arms

**1. EvoPrompt (automated, 0-shot).** Evolves a prompt against the dev set with a genetic
algorithm, scores the best on the sacred test.

**2. spp (human-in-the-loop, 0-shot).** A person runs the spp plugin loop seeded by
`baselines/<task>/SEED.md`, fed `baseline.csv` (unsplit), with `test_holdout.csv` registered
as the sacred test. Each iteration sharpens one categorical rule under information isolation.
The final prompt is scored once on the sacred test. The full per-iteration trace is in the
[loop logs](https://jaylbean.github.io/spp-benchmark/loop-logs/).

**3. DSPy (automated, few-shot).** MIPROv2, bootstrapping up to four in-context
demonstrations — its design strength, included honestly. This is the one arm that is few-shot;
the asymmetry is disclosed in the report.

## Repository layout

```
BENCHMARK_REPORT.md     the canonical three-way report (accuracy, cost, tokens, fairness ledger)
site/                   the Quarto source for the live benchmark site
scripts/
  llm_client.py         shared task-model client (the one task-model surface)
  build_fixtures.py     HF -> fixtures/ + baselines/ (deterministic, seed=5)
  run_evoprompt.py      EvoPrompt-GA arm (faithful reimpl; 0-shot; presets)
  score_prompt.py       score ANY prompt on a task's sacred test (the spp arm)
  compare.py            final accuracy table across arms
  cost_report.py        per-arm token/cost ledger
dspy_arm/               DSPy MIPROv2 few-shot arm (run_dspy.sh launcher)
fixtures/<task>/        dev.jsonl, test.jsonl, metadata.json, evoprompt/{dev,test}.txt
baselines/<task>/       baseline.csv (UNSPLIT), test_holdout.csv (shared test), SEED.md,
                        spp/<task>/ (per-run plan, iterations, REPORT.md, frozen prompt)
results/<arm>/<task>/   result.json (+ checkpoint.json for evoprompt)
evoprompt/upstream/     vendored beeevita/EvoPrompt (gitignored; init prompts + GA template)
```

## Setup

```sh
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt

# Task model — published runs use OpenAI gpt-5-nano:
export OMLX_BASE_URL=https://api.openai.com/v1
export OMLX_API_KEY=$OPENAI_API_KEY
export OMLX_MODEL=gpt-5-nano
export OMLX_REASONING=low

# Fixtures (already built; re-run only to regenerate):
git clone --depth 1 https://github.com/beeevita/EvoPrompt.git evoprompt/upstream
HF_DATASETS_CACHE=$PWD/data/hf_cache ./.venv/bin/python scripts/build_fixtures.py
```

## Reproduce the arms

```sh
# EvoPrompt (0-shot):
./.venv/bin/python scripts/run_evoprompt.py --tasks ag_news sst5 trec --preset default

# DSPy (few-shot) — uses a dedicated OPENAI_API_KEY_DSPY from a gitignored .env:
bash dspy_arm/run_dspy.sh ag_news sst5 trec --auto medium --demos 4

# spp: run the plugin loop, then score the final prompt on the sacred test:
./.venv/bin/python scripts/score_prompt.py --task trec --prompt-file <spp_prompt.txt> --label spp

# Compare accuracy + cost across arms:
./.venv/bin/python scripts/compare.py
EVOPROMPT_ARM=<arm> ./.venv/bin/python scripts/cost_report.py
```

## Caveat: expect saturation

Strong instruction-following models sit near the ceiling on AG News, so there is little
headroom to separate the arms there. **SST-5 and TREC** carry the genuine signal —
fine-grained degree boundaries and answer-type subtleties are where prompt wording, and the
spp loop, can actually move the number.
