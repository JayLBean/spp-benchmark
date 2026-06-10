"""Emit baselines/<task>/SEED.md — a one-page brief to seed spp's /spp-init.

Pulls label space / sizes / paper reference from fixtures/<task>/metadata.json so the
brief never drifts from the actual fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"
BASELINES = ROOT / "baselines"

DESCRIPTIONS = {
    "ag_news": (
        "News topic classification. Each row is a news article (title + first sentences). "
        "Assign exactly one topic. Boundaries are usually clear; Business vs Tech is the "
        "main genuine ambiguity (a software-company earnings story can read as either)."
    ),
    "sst5": (
        "Fine-grained sentiment of a movie-review sentence on a 5-point scale. The hard part "
        "is the *degree* boundaries — terrible vs bad, good vs great, and the okay/neutral "
        "middle — not polarity. This is where prompt wording earns its keep."
    ),
    "trec": (
        "Question classification: what *type of answer* the question expects (not its topic). "
        "'What is the capital of France?' -> Location (the answer is a place). Expression is "
        "rare (abbreviations/definitions) and easy to miss; Entity vs Description is subtle."
    ),
}

LABEL_GLOSS = {
    "trec": {
        "Description": "answer is a definition/description/manner/reason",
        "Entity": "answer is a thing (animal, color, product, ...)",
        "Expression": "answer is an abbreviation or its expansion",
        "Human": "answer is a person or group",
        "Location": "answer is a place",
        "Number": "answer is a count, date, distance, money, ...",
    },
    "sst5": {
        "terrible": "strongly negative",
        "bad": "mildly negative",
        "okay": "neutral / mixed",
        "good": "mildly positive",
        "great": "strongly positive",
    },
    "ag_news": {
        "World": "international / political news",
        "Sports": "sports",
        "Business": "business, finance, markets",
        "Tech": "science and technology",
    },
}


def make(task: str) -> Path:
    meta = json.loads((FIXTURES / task / "metadata.json").read_text())
    classes = meta["classes"]
    gloss = LABEL_GLOSS[task]
    ref = meta["paper_reference_alpaca7b"]
    lines = [
        f"# {task} — spp seed brief",
        "",
        "Seed for `/spp-init`. The benchmark harness already built the labeled data;",
        "this brief just gives the consultation its starting facts.",
        "",
        "## Task",
        "",
        DESCRIPTIONS[task],
        "",
        f"- **Output:** one label per row (single-field, K=1). **Metric:** {meta['metric']}.",
        f"- **Classes ({meta['n_classes']}):**",
        "",
        "  | label | meaning |",
        "  |---|---|",
        *[f"  | `{c}` | {gloss[c]} |" for c in classes],
        "",
        "## Data (already prepared — do NOT re-label, do NOT re-split here)",
        "",
        f"- **`baseline.csv`** — {meta['splits']['baseline_pool']} labeled rows, UNSPLIT. "
        "This is spp's pool; spp carves its own dev/train. Columns: `row_id,text,label`.",
        f"- **`test_holdout.csv`** — {meta['splits']['shared_test']} rows, the SHARED SACRED "
        "test. Identical rows the EvoPrompt arm scored on. Register this as spp's test set so "
        "the comparison is apples-to-apples; never let the loop see it.",
        "",
        "## Reference (NOT a target)",
        "",
        f"Paper Alpaca-7b accuracy (EvoPrompt, ICLR 2024): manual {ref['manual']}, "
        f"APE {ref['APE']}, EvoPrompt {ref['EvoPrompt_best']}. Our task model is "
        "gpt-oss-20b, so absolute numbers differ — only the same-model EvoPrompt vs spp "
        "comparison on the shared test set is meaningful.",
        "",
        "## Scoring spp's final prompt",
        "",
        "```sh",
        f"python scripts/score_prompt.py --task {task} --prompt-file <spp_prompt.txt>",
        "```",
        "",
    ]
    out = BASELINES / task / "SEED.md"
    out.write_text("\n".join(lines))
    return out


if __name__ == "__main__":
    for task in ["ag_news", "sst5", "trec"]:
        print("wrote", make(task))
