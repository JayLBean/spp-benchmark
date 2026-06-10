"""EvoPrompt-GA on gpt-oss-20b (faithful reimplementation).

Why a reimplementation and not the upstream repo: beeevita/EvoPrompt is pinned to
the pre-1.0 ``openai`` SDK, a GPU Alpaca task model, and ``auth.yaml`` — none of which
run on this stack. This driver reuses upstream's *exact* assets so the comparison
stays honest:
  - initial population  = upstream ``data/cls/<ds>/prompts.txt`` + ``prompts_auto.txt``
  - GA operator prompt  = upstream ``data/template_ga.py`` templates_2["cls"]
  - selection/update     = Algorithm 2 (roulette-wheel parents, top-N truncation)

Inference is 0-shot (instruction + input only). EvoPrompt's 1-shot-per-class demos
existed to keep Alpaca-7b in-label; gpt-oss-20b stays in-label from the instruction
alone, and the demos only inflated its reasoning (latency). The same 0-shot wrapper
scores the spp arm, so the deviation is symmetric and the comparison stays fair.

Both the task model (classification) and the optimizer (crossover+mutation) are the
SAME local model via scripts/llm_client.py — the fairness invariant for the spp arm.

Presets (search cost ~= init_cap*dev + N*T*dev classification calls @ ~2.6s/call):
  smoke    N=4  T=2  dev=20  init_cap=6   (wiring check, one task)
  default  N=8  T=6  dev=80  init_cap=10  (≈2.5 h/task — the launch config)
  faithful N=10 T=10 dev=200 init_cap=20  (≈6 h/task — paper-scale protocol)
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_client import classify, complete, map_parallel  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"
RESULTS = ROOT / "results" / "evoprompt"
UPSTREAM = ROOT / "evoprompt" / "upstream"

# EvoPrompt dataset-dir names (upstream) keyed by our task name.
UPSTREAM_DS = {"ag_news": "agnews", "sst5": "sst-5", "trec": "trec"}

# upstream data/template_ga.py -> templates_2["cls"] (one-shot operator demo + slots)
GA_TEMPLATE = """Please follow the instruction step-by-step to generate a better prompt.
1. Crossover the following prompts and generate a new prompt:
Prompt 1: Rewrite the input text into simpler text.
Prompt 2: Rewrite my complex sentence in simpler terms, but keep the meaning.
2. Mutate the prompt generated in Step 1 and generate a final prompt bracketed with <prompt> and </prompt>.

1. Crossover Prompt: Rewrite the complex text into simpler text while keeping its meaning.
2. <prompt>Transform the provided text into simpler language, maintaining its essence.</prompt>

Please follow the instruction step-by-step to generate a better prompt.
1. Crossover the following prompts and generate a new prompt:
Prompt 1: <prompt1>
Prompt 2: <prompt2>
2. Mutate the prompt generated in Step 1 and generate a final prompt bracketed with <prompt> and </prompt>.

1. """

# gpt-oss-20b reasons ~150 tokens per call regardless of reasoning_effort and oMLX
# serializes (~2.6s/call), so the search cost is what sets wall-clock. We run 0-shot
# (no per-class demos): gpt-oss stays in-label from the instruction alone, demos only
# inflated reasoning. The SAME 0-shot wrapper scores the spp arm later -> apples-to-apples.
PRESETS = {
    "smoke": dict(N=4, T=2, dev=20, init_cap=6),
    "default": dict(N=8, T=6, dev=80, init_cap=10),
    "faithful": dict(N=10, T=10, dev=200, init_cap=20),
}


@dataclass
class TaskResult:
    task: str
    preset: str
    config: dict
    best_prompt: str
    best_dev_acc: float
    best_test_acc: float
    manual_init_prompt: str
    manual_init_test_acc: float
    n_classes: int
    classes: list[str]
    elapsed_sec: float


def _read_jsonl(p: Path) -> list[dict]:
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def _init_prompts(task: str) -> list[str]:
    ds = UPSTREAM_DS[task]
    out: list[str] = []
    for fname in ("prompts.txt", "prompts_auto.txt"):
        f = UPSTREAM / "data" / "cls" / ds / fname
        if f.exists():
            out += [ln.strip() for ln in f.read_text().splitlines() if ln.strip()]
    # dedupe, keep order
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def eval_prompt_text(instruction: str, text: str) -> str:
    """0-shot inference wrapper. Reused verbatim to score the spp arm (fairness)."""
    return f"{instruction}\n\nSentence: {text}\nLabel:"


def evaluate(instruction: str, rows: list[dict], classes: list[str]) -> float:
    """Accuracy of `instruction` over `rows` (0-shot)."""

    def one(r: dict) -> int:
        prompt = eval_prompt_text(instruction, r["text"])
        label, _ = classify(prompt, classes, max_tokens=320)
        return int(label == r["label"])

    hits = map_parallel(one, rows)
    return sum(hits) / len(rows)


def _parse_prompt(text: str) -> str | None:
    m = re.findall(r"<prompt>(.*?)</prompt>", text, re.DOTALL)
    if m:
        return m[-1].strip()
    # fallback: a bare line after "2." if the model dropped the tags
    return None


def crossover_mutate(p1: str, p2: str) -> str | None:
    q = GA_TEMPLATE.replace("<prompt1>", p1).replace("<prompt2>", p2)
    comp = complete(q, max_tokens=512, reasoning_effort="low")
    return _parse_prompt(comp.content)


def _roulette(pop: list[str], fit: dict[str, float], rng: random.Random) -> str:
    total = sum(fit[p] for p in pop)
    if total <= 0:
        return rng.choice(pop)
    r = rng.uniform(0, total)
    acc = 0.0
    for p in pop:
        acc += fit[p]
        if acc >= r:
            return p
    return pop[-1]


def run_task(task: str, preset: str, seed: int = 5) -> TaskResult:
    cfg = PRESETS[preset]
    N, T, dev_n = cfg["N"], cfg["T"], cfg["dev"]
    rng = random.Random(seed)
    t0 = time.time()

    meta = json.loads((FIXTURES / task / "metadata.json").read_text())
    classes = meta["classes"]
    dev = _read_jsonl(FIXTURES / task / "dev.jsonl")[:dev_n]
    test = _read_jsonl(FIXTURES / task / "test.jsonl")

    outdir = RESULTS / task
    outdir.mkdir(parents=True, exist_ok=True)
    ckpt = outdir / "checkpoint.json"

    def log(msg: str) -> None:
        line = f"[{task}] {msg}"
        print(line, flush=True)
        (outdir / "run.log").open("a").write(line + "\n")

    # ---- init population: score upstream prompts on dev, keep top-N ----
    inits = _init_prompts(task)[: cfg["init_cap"]]
    log(
        f"preset={preset} N={N} T={T} dev={dev_n} | {len(inits)} init prompts, "
        f"{len(classes)} classes"
    )
    fit: dict[str, float] = {}
    for i, p in enumerate(inits):
        fit[p] = evaluate(p, dev, classes)
        log(f"  init {i + 1}/{len(inits)} dev={fit[p]:.4f} :: {p[:70]}")
    population = sorted(inits, key=lambda p: fit[p], reverse=True)[:N]
    manual_init = population[0]  # best upstream prompt = the 'human/manual' reference
    ckpt.write_text(json.dumps({"stage": "init", "fit": fit}, indent=2))

    # ---- GA iterations (Algorithm 2) ----
    for t in range(1, T + 1):
        offspring: list[str] = []
        for _ in range(N):
            a = _roulette(population, fit, rng)
            b = _roulette(population, fit, rng)
            child = crossover_mutate(a, b)
            if child and child not in fit:
                offspring.append(child)
        for c in offspring:
            fit[c] = evaluate(c, dev, classes)
        merged = population + offspring
        population = sorted(merged, key=lambda p: fit[p], reverse=True)[:N]
        best = population[0]
        log(f"iter {t}/{T} best_dev={fit[best]:.4f} (+{len(offspring)} offspring) :: {best[:70]}")
        ckpt.write_text(
            json.dumps(
                {
                    "stage": f"iter{t}",
                    "best_dev": fit[best],
                    "best_prompt": best,
                    "population": [(p, fit[p]) for p in population],
                },
                indent=2,
            )
        )

    best = population[0]
    log(f"scoring best on test (n={len(test)}) ...")
    best_test = evaluate(best, test, classes)
    log("scoring manual-init on test ...")
    manual_test = evaluate(manual_init, test, classes)

    res = TaskResult(
        task=task,
        preset=preset,
        config=cfg,
        best_prompt=best,
        best_dev_acc=round(fit[best], 4),
        best_test_acc=round(best_test, 4),
        manual_init_prompt=manual_init,
        manual_init_test_acc=round(manual_test, 4),
        n_classes=len(classes),
        classes=classes,
        elapsed_sec=round(time.time() - t0, 1),
    )
    (outdir / "result.json").write_text(json.dumps(asdict(res), indent=2) + "\n")
    log(
        f"DONE best_test={res.best_test_acc} manual_test={res.manual_init_test_acc} "
        f"({res.elapsed_sec / 60:.1f} min)"
    )
    return res


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", nargs="+", default=["ag_news", "sst5", "trec"])
    ap.add_argument("--preset", choices=list(PRESETS), default="default")
    ap.add_argument("--seed", type=int, default=5)
    args = ap.parse_args(argv)
    summary = []
    for task in args.tasks:
        r = run_task(task, args.preset, args.seed)
        summary.append((task, r.best_test_acc, r.manual_init_test_acc))
    print("\n=== SUMMARY (test accuracy) ===")
    for task, best, manual in summary:
        print(f"  {task:8s} EvoPrompt={best:.4f}  manual-init={manual:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
