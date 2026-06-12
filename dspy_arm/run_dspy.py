"""DSPy arm — MIPROv2 few-shot prompt optimization on gpt-5-nano.

The third comparison arm, run honestly in DSPy's natural FEW-SHOT regime: MIPROv2 jointly
optimizes the instruction AND bootstraps in-context demonstrations. EvoPrompt and spp ran
0-shot; DSPy uses demos because that is its design strength — if it wins via demos, that is
a signal worth incorporating, not hiding. Same task model (gpt-5-nano), same dev signal,
the SAME 1000/500-row sacred test the other arms scored.

Fairness / honesty knobs:
  - typed Literal[...] output signature pins predictions to the label set (a free-form
    label field drifts to invented strings like 'person_name').
  - LM cache is OFF, so every counted call is a real billed API call — token/dollar totals
    match the dashboard and are comparable to the no-cache EvoPrompt/spp arms.
  - starting instruction = the shared seed (prompt_v0), the same starting point the other
    arms had; MIPROv2 proposes alternatives from there.

gpt-5-nano (reasoning model) needs temperature=1.0, a high max_tokens cap (cap only, billed
for actual), and reasoning_effort; set in run_dspy.sh via dspy.LM kwargs.

Results -> results/dspy_gpt5nano/<task>/result.json with a `usage` block in the shape
scripts/cost_report.py reads, so the dollar axis applies automatically.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Literal

import dspy

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"
BASELINES = ROOT / "baselines"
RESULTS = ROOT / "results" / "dspy_gpt5nano"


def _read_jsonl(p: Path) -> list[dict]:
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def _examples(rows: list[dict]) -> list[dspy.Example]:
    return [dspy.Example(text=r["text"], label=r["label"]).with_inputs("text") for r in rows]


def _seed_instruction(task: str) -> str:
    """The shared starting prompt (prompt_v0), minus the HTML provenance comment."""
    text = (BASELINES / task / "prompt_v0.md").read_text()
    lines = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith(("<!--", "-->", "<"))
    ]
    return lines[-1] if lines else f"Classify the {task} input."


def _signature(classes: list[str], instruction: str) -> type[dspy.Signature]:
    label_type = Literal[tuple(classes)]  # type: ignore[valid-type]
    return dspy.Signature(
        {
            "text": (str, dspy.InputField()),
            "label": (label_type, dspy.OutputField()),
        },
        instruction,
    )


def _usage_totals(lm: dspy.LM) -> dict:
    calls = len(lm.history)
    in_tok = sum((h.get("usage") or {}).get("prompt_tokens", 0) for h in lm.history)
    out_tok = sum((h.get("usage") or {}).get("completion_tokens", 0) for h in lm.history)
    return {
        "calls": calls,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "total_tokens": in_tok + out_tok,
    }


def _accuracy(example: dspy.Example, pred: dspy.Prediction, trace: object = None) -> bool:
    return bool(example.label == getattr(pred, "label", None))


def run_task(task: str, auto: str = "medium", demos: int = 4, seed: int = 5) -> dict:
    meta = json.loads((FIXTURES / task / "metadata.json").read_text())
    classes = meta["classes"]
    instruction = _seed_instruction(task)

    # train (demo source) from the baseline pool; val (trial eval) = the shared dev signal;
    # test = the sacred holdout. Only train+val are ever used to optimize.
    pool = _read_jsonl(BASELINES.parent / "fixtures" / task / "dev.jsonl")
    train = _examples(pool[:120])
    val = _examples(pool[120:200]) if len(pool) >= 200 else _examples(pool[: len(pool) // 2])
    test = _examples(_read_jsonl(FIXTURES / task / "test.jsonl"))

    lm = dspy.settings.lm
    lm.history.clear()
    t0 = time.time()

    program = dspy.Predict(_signature(classes, instruction))
    tp = dspy.MIPROv2(metric=_accuracy, auto=auto, num_threads=8)
    compiled = tp.compile(
        program,
        trainset=train,
        valset=val,
        max_bootstrapped_demos=demos,
        max_labeled_demos=demos,
        requires_permission_to_run=False,
    )
    compile_usage = _usage_totals(lm)
    compile_calls = compile_usage["calls"]

    evaluator = dspy.Evaluate(devset=test, metric=_accuracy, num_threads=8, display_progress=False)
    score = evaluator(compiled)
    test_acc = float(score) / 100 if float(score) > 1 else float(score)

    usage = _usage_totals(lm)  # cumulative: compile + test
    elapsed = round(time.time() - t0, 1)

    out_dir = RESULTS / task
    out_dir.mkdir(parents=True, exist_ok=True)
    compiled.save(str(out_dir / "compiled_program.json"))
    result = {
        "task": task,
        "arm": "dspy_gpt5nano",
        "optimizer": f"MIPROv2(auto={auto}, demos={demos}, few-shot)",
        "model": "gpt-5-nano",
        "seed_instruction": instruction,
        "n_classes": len(classes),
        "classes": classes,
        "test_n": len(test),
        "best_test_acc": round(test_acc, 4),
        "elapsed_sec": elapsed,
        "usage": usage,
        "usage_breakdown": {
            "compile": compile_usage,
            "test_calls": usage["calls"] - compile_calls,
        },
    }
    (out_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    cost = usage["input_tokens"] / 1e6 * 0.05 + usage["output_tokens"] / 1e6 * 0.40
    print(
        f"[{task}] DONE test_acc={result['best_test_acc']} | calls={usage['calls']} "
        f"(compile {compile_calls} + test {usage['calls'] - compile_calls}) | "
        f"tok in={usage['input_tokens']:,} out={usage['output_tokens']:,} | "
        f"${cost:.2f} | {elapsed / 60:.1f} min"
    )
    return result


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tasks", nargs="+")
    ap.add_argument("--auto", default="medium", choices=["light", "medium", "heavy"])
    ap.add_argument("--demos", type=int, default=4)
    args = ap.parse_args(argv)
    for task in args.tasks:
        run_task(task, auto=args.auto, demos=args.demos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
