#!/usr/bin/env bash
# EvoPrompt re-baseline on gpt-5-nano (OpenAI). The key is read from .env (gitignored,
# never committed). Results land in results/evoprompt_gpt5nano/ so the oss run at
# results/evoprompt/ is preserved.
#
# Usage: bash scripts/run_gpt5nano.sh ag_news sst5 trec
set -euo pipefail
cd "$(dirname "$0")/.."
set -a
source .env            # provides OPENAI_API_KEY
set +a

export OMLX_BASE_URL=https://api.openai.com/v1
export OMLX_API_KEY="$OPENAI_API_KEY"
export OMLX_MODEL=gpt-5-nano
export OMLX_REASONING=low   # calibrated on TREC: 0.76 vs 0.40 minimal / 0.80 medium
export OMLX_WORKERS=8       # OpenAI parallelizes; oMLX (oss) did not
export EVOPROMPT_ARM=evoprompt_gpt5nano

exec ./.venv/bin/python scripts/run_evoprompt.py --tasks "$@" --preset default
