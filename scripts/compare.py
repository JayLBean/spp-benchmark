"""Compare arms on the shared sacred test set.

Reads results/<arm>/<task>/result.json for each arm and prints a table. The EvoPrompt
arm also carries a manual-init reference (best upstream prompt, unoptimized).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ["ag_news", "sst5", "trec"]


def _load(arm: str, task: str) -> dict | None:
    p = ROOT / "results" / arm / task / "result.json"
    return json.loads(p.read_text()) if p.exists() else None


def main() -> int:
    rows = []
    for task in TASKS:
        evo = _load("evoprompt", task)
        spp = _load("spp", task)
        rows.append(
            {
                "task": task,
                "manual_init": (evo or {}).get("manual_init_test_acc"),
                "evoprompt": (evo or {}).get("best_test_acc"),
                "spp": (spp or {}).get("test_acc"),
            }
        )
    w = 12
    print(f"{'task':<10}{'manual-init':<{w}}{'EvoPrompt':<{w}}{'spp':<{w}}{'spp-EvoP':<{w}}")
    print("-" * (10 + 4 * w))
    for r in rows:
        delta = (
            f"{r['spp'] - r['evoprompt']:+.4f}"
            if r["spp"] is not None and r["evoprompt"] is not None
            else "—"
        )

        def fmt(x: float | None) -> str:
            return f"{x:.4f}" if x is not None else "—"

        print(
            f"{r['task']:<10}{fmt(r['manual_init']):<{w}}{fmt(r['evoprompt']):<{w}}"
            f"{fmt(r['spp']):<{w}}{delta:<{w}}"
        )
    print("\nAll arms scored 0-shot on the identical shared test set with gpt-oss-20b.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
