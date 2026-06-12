#!/usr/bin/env bash
# DSPy arm launcher — MIPROv2 few-shot on gpt-5-nano. Uses the DEDICATED DSPy key
# (OPENAI_API_KEY_DSPY) so its spend is isolated on the dashboard. Key read from .env
# (gitignored, never committed).
#
# Usage: bash dspy_arm/run_dspy.sh ag_news sst5 trec   [--auto medium] [--demos 4]
set -euo pipefail
cd "$(dirname "$0")/.."
set -a
source .env
set +a

# Point the OpenAI SDK / litellm at the dedicated DSPy key explicitly.
export OPENAI_API_KEY="$OPENAI_API_KEY_DSPY"

# gpt-5-nano (reasoning model) request shape is set on dspy.LM below.
exec ./.venv/bin/python - "$@" <<'PY'
import os, sys
import dspy

# reasoning model: temperature must be 1.0; high max_tokens is a CAP (billed for actual);
# cache OFF so every counted call is a real billed API call (matches the dashboard and the
# no-cache EvoPrompt/spp arms).
lm = dspy.LM(
    "openai/gpt-5-nano",
    api_key=os.environ["OPENAI_API_KEY"],
    temperature=1.0,
    max_tokens=16000,
    reasoning_effort="low",
    cache=False,
)
dspy.configure(lm=lm)

sys.path.insert(0, "dspy_arm")
from run_dspy import main
raise SystemExit(main(sys.argv[1:]))
PY
