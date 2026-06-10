"""Score a single prompt on a task's shared sacred test set.

This is the spp arm's scorer and the apples-to-apples bridge: it reuses the EXACT
0-shot inference wrapper and label matching the EvoPrompt arm uses (run_evoprompt),
on the EXACT same test rows (fixtures/<task>/test.jsonl == baselines/<task>/
test_holdout.csv), with the same task model. So an spp prompt and an EvoPrompt
prompt are judged identically; only the prompt differs.

Usage:
  python scripts/score_prompt.py --task sst5 --prompt-file my_spp_prompt.txt
  python scripts/score_prompt.py --task trec --prompt "Classify the question ..."
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_evoprompt import FIXTURES, _read_jsonl, evaluate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def score(task: str, prompt: str, *, label: str = "spp") -> dict:
    meta = json.loads((FIXTURES / task / "metadata.json").read_text())
    classes = meta["classes"]
    test = _read_jsonl(FIXTURES / task / "test.jsonl")
    acc = evaluate(prompt, test, classes)
    res = {
        "task": task,
        "arm": label,
        "test_n": len(test),
        "test_acc": round(acc, 4),
        "prompt": prompt,
        "classes": classes,
    }
    outdir = ROOT / "results" / label / task
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "result.json").write_text(json.dumps(res, indent=2) + "\n")
    return res


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["ag_news", "sst5", "trec"])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--prompt", help="prompt text inline")
    g.add_argument("--prompt-file", help="path to a file containing the prompt")
    ap.add_argument("--label", default="spp", help="arm label (results/<label>/<task>/)")
    args = ap.parse_args(argv)
    prompt = args.prompt or Path(args.prompt_file).read_text().strip()
    res = score(args.task, prompt, label=args.label)
    print(f"[{res['arm']}] {res['task']} test_acc={res['test_acc']} (n={res['test_n']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
