"""Token-cost report per arm — the efficiency axis of the comparison.

Two sources, in priority order:
  1. EXACT — result.json carries a ``usage`` block (runs made after token
     instrumentation: the spp scorer, and any re-run of EvoPrompt).
  2. ESTIMATED — reconstructed from run.log: call counts are EXACT (parsed from the
     log structure), token counts are estimated (input ~ chars/4 over the actual
     prompts; output from observed gpt-oss reasoning length per call type).

The honest framing this report exists to make: EvoPrompt spends its ENTIRE optimization
budget on the gpt-oss task model (population x dev, every iteration). spp spends gpt-oss
only on loop dev-scoring + final test, and offloads the reasoning to Claude subagents +
the human. So compare gpt-oss task-model tokens directly; spp's "optimizer cost" lives
elsewhere (Claude tokens + human time), which this report flags but cannot bill here.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_evoprompt import FIXTURES, GA_TEMPLATE, _init_prompts  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TASKS = ["ag_news", "sst5", "trec"]

# Observed gpt-oss output tokens per call type (reasoning + answer), 0-shot.
CLS_OUT = 146  # classification call
GEN_OUT = 250  # GA crossover+mutation generation call
CHARS_PER_TOK = 4  # rough o200k input estimate


def _est_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOK)


def _reconstruct(task: str) -> dict | None:
    log = ROOT / "results" / "evoprompt" / task / "run.log"
    if not log.exists():
        return None
    lines = log.read_text().splitlines()
    head = next((ln for ln in lines if "preset=" in ln), "")
    m = re.search(r"N=(\d+) T=(\d+) dev=(\d+) \| (\d+) init", head)
    if not m:
        return None
    n, _t, dev, n_init = (int(x) for x in m.groups())
    offspring = sum(int(x) for x in re.findall(r"\+(\d+) offspring", "\n".join(lines)))
    iters = len(re.findall(r"^\[.*\] iter ", "\n".join(lines), re.M))
    test_done = "DONE best_test" in "\n".join(lines)
    test_n = json.loads((FIXTURES / task / "metadata.json").read_text())["splits"]["shared_test"]

    # exact call counts
    cls_search = (n_init + offspring) * dev
    gen_calls = iters * n  # N crossover attempts per iteration
    cls_test = 2 * test_n if test_done else 0  # best + manual-init on test

    # token estimate from actual prompts
    sample_instr = _init_prompts(task)[:n_init]
    avg_instr = sum(_est_tokens(p) for p in sample_instr) / max(1, len(sample_instr))
    texts = [
        json.loads(line)["text"]
        for line in (FIXTURES / task / "dev.jsonl").read_text().splitlines()[:50]
    ]
    avg_text = sum(_est_tokens(t) for t in texts) / len(texts)
    cls_in = avg_instr + avg_text + 6  # + "\n\nSentence: .. \nLabel:" scaffolding
    gen_in = _est_tokens(GA_TEMPLATE) + 2 * avg_instr

    cls_calls = cls_search + cls_test
    in_tok = round(cls_calls * cls_in + gen_calls * gen_in)
    out_tok = cls_calls * CLS_OUT + gen_calls * GEN_OUT
    return {
        "source": "estimated",
        "complete": test_done,
        "calls": cls_calls + gen_calls,
        "calls_breakdown": {
            "cls_search": cls_search,
            "gen": gen_calls,
            "cls_test": cls_test,
        },
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "total_tokens": in_tok + out_tok,
    }


def _arm_usage(arm: str, task: str) -> dict | None:
    p = ROOT / "results" / arm / task / "result.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    if d.get("usage"):
        u = dict(d["usage"])
        u["source"] = "exact"
        return u
    return None


def main() -> int:
    print("EvoPrompt arm — gpt-oss-20b token cost (search + test scoring)\n")
    hdr = f"{'task':<10}{'src':<11}{'calls':>8}{'in_tok':>12}{'out_tok':>12}{'total':>12}"
    print(hdr)
    print("-" * len(hdr))
    grand = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for task in TASKS:
        u = _arm_usage("evoprompt", task) or _reconstruct(task)
        if not u:
            print(f"{task:<10}{'(not started)':<11}")
            continue
        tag = u["source"] + ("" if u.get("complete", True) else "*")
        print(
            f"{task:<10}{tag:<11}{u['calls']:>8,}{u['input_tokens']:>12,}"
            f"{u['output_tokens']:>12,}{u['total_tokens']:>12,}"
        )
        for k in grand:
            grand[k] += u[k]
    print("-" * len(hdr))
    print(
        f"{'TOTAL':<10}{'':<11}{grand['calls']:>8,}{grand['input_tokens']:>12,}"
        f"{grand['output_tokens']:>12,}{grand['total_tokens']:>12,}"
    )
    print("\n* = task still running (partial). 'estimated': calls exact, tokens ~4 chars/tok in,")
    print(
        f"  observed out ({CLS_OUT}/cls, {GEN_OUT}/gen). spp arm reports EXACT usage when scored."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
