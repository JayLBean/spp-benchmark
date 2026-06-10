"""Build benchmark fixtures for AG News, SST-5, TREC from HuggingFace.

Design (deterministic, seed=5):
  - Label names use EvoPrompt's canonical verbalizers (utils.py) so the spp arm,
    the EvoPrompt arm, and the paper all speak the same label vocabulary.
  - SHARED SACRED TEST  (fixtures/<task>/test.jsonl + baselines/<task>/test_holdout.csv):
    a stratified sample from the HF *test* split. Both arms score on these exact rows.
  - BASELINE POOL  (baselines/<task>/baseline.csv): a stratified sample from the HF
    *train* split, UNSPLIT — this is what spp consumes; spp carves its own dev there.
    Disjoint from the test split by construction.
  - EVOPROMPT DEV  (fixtures/<task>/evoprompt/dev.txt): a 200-row stratified subset OF
    the baseline pool, so both frameworks draw training-side data from one shared pool.
  - EvoPrompt-format files are `text\tlabel_idx` where idx = verbalizers.index(name).

HF label -> EvoPrompt verbalizer mapping is by NAME, never by raw index (the HF index
order differs from EvoPrompt's), which is the one subtle correctness point here.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from datasets import load_dataset

SEED = 5
ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"
BASELINES = ROOT / "baselines"

# EvoPrompt's canonical verbalizers (upstream utils.py: get_dataset_verbalizers).
VERBALIZERS = {
    "ag_news": ["World", "Sports", "Business", "Tech"],
    "sst5": ["terrible", "bad", "okay", "good", "great"],
    "trec": ["Description", "Entity", "Expression", "Human", "Location", "Number"],
}

# Paper Table 1 reference numbers (Alpaca-7b accuracy) — REFERENCE ONLY, not a target.
PAPER_REF = {
    "ag_news": {"manual": 70.63, "APE": 71.76, "EvoPrompt_best": 73.82},
    "sst5": {"manual": 42.90, "APE": 46.32, "EvoPrompt_best": 49.91},
    "trec": {"manual": 50.60, "APE": 58.73, "EvoPrompt_best": 64.00},
}

# Shared sacred test size and baseline-pool size per task.
TEST_N = {"ag_news": 1000, "sst5": 1000, "trec": 500}  # trec test is 500 total => all
POOL_N = {"ag_news": 1000, "sst5": 1000, "trec": 1000}
DEV_N = 200

TREC_COARSE_TO_EVO = {
    "ABBR": "Expression",
    "DESC": "Description",
    "ENTY": "Entity",
    "HUM": "Human",
    "LOC": "Location",
    "NUM": "Number",
}


def _load(task: str) -> tuple[list[dict], list[dict]]:
    """Return (train_records, test_records) as {text, label} with EvoPrompt names."""
    if task == "ag_news":
        names = ["World", "Sports", "Business", "Tech"]  # Sci/Tech -> Tech (idx 3)
        tr = load_dataset("fancyzhx/ag_news", split="train")
        te = load_dataset("fancyzhx/ag_news", split="test")
        to_rec = lambda r: {"text": r["text"].strip(), "label": names[r["label"]]}
        return [to_rec(r) for r in tr], [to_rec(r) for r in te]
    if task == "sst5":
        names = VERBALIZERS["sst5"]  # SetFit label 0..4 aligns terrible..great
        tr = load_dataset("SetFit/sst5", split="train")
        te = load_dataset("SetFit/sst5", split="test")
        to_rec = lambda r: {"text": r["text"].strip(), "label": names[int(r["label"])]}
        return [to_rec(r) for r in tr], [to_rec(r) for r in te]
    if task == "trec":
        tr = load_dataset("SetFit/TREC-QC", split="train")
        te = load_dataset("SetFit/TREC-QC", split="test")
        to_rec = lambda r: {
            "text": r["text"].strip(),
            "label": TREC_COARSE_TO_EVO[r["label_coarse_original"]],
        }
        return [to_rec(r) for r in tr], [to_rec(r) for r in te]
    raise ValueError(task)


def _stratified(records: list[dict], n: int, seed: int, exclude: set[str]) -> list[dict]:
    """Deterministic class-proportional sample of size n, skipping excluded texts."""
    import random

    rng = random.Random(seed)
    by_class: dict[str, list[dict]] = {}
    for r in records:
        if r["text"] in exclude or not r["text"]:
            continue
        by_class.setdefault(r["label"], []).append(r)
    for v in by_class.values():
        rng.shuffle(v)
    if n >= sum(len(v) for v in by_class.values()):
        out = [r for v in by_class.values() for r in v]
        rng.shuffle(out)
        return out
    classes = sorted(by_class)
    total = sum(len(by_class[c]) for c in classes)
    quota = {c: round(n * len(by_class[c]) / total) for c in classes}
    # fix rounding drift
    while sum(quota.values()) > n:
        quota[max(quota, key=quota.get)] -= 1
    while sum(quota.values()) < n:
        quota[min(quota, key=quota.get)] += 1
    out = [r for c in classes for r in by_class[c][: quota[c]]]
    rng.shuffle(out)
    return out


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r[c] for c in cols})


def _write_evo(path: Path, rows: list[dict], verbalizers: list[str]) -> None:
    """EvoPrompt format: text<TAB>label_idx."""
    path.parent.mkdir(parents=True, exist_ok=True)
    idx = {name: i for i, name in enumerate(verbalizers)}
    with path.open("w") as f:
        for r in rows:
            text = r["text"].replace("\t", " ").replace("\n", " ")
            f.write(f"{text}\t{idx[r['label']]}\n")


def build(task: str) -> dict:
    verb = VERBALIZERS[task]
    train, test = _load(task)

    test_rows = _stratified(test, TEST_N[task], SEED, exclude=set())
    for i, r in enumerate(test_rows, 1):
        r["row_id"] = f"{task}_test_{i:04d}"
    test_texts = {r["text"] for r in test_rows}

    pool = _stratified(train, POOL_N[task], SEED, exclude=test_texts)
    for i, r in enumerate(pool, 1):
        r["row_id"] = f"{task}_base_{i:04d}"

    dev = _stratified(pool, DEV_N, SEED + 1, exclude=set())

    # canonical jsonl
    _write_jsonl(FIXTURES / task / "test.jsonl", [_pick(r) for r in test_rows])
    _write_jsonl(FIXTURES / task / "dev.jsonl", [_pick(r) for r in dev])
    # EvoPrompt-format
    _write_evo(FIXTURES / task / "evoprompt" / "dev.txt", dev, verb)
    _write_evo(FIXTURES / task / "evoprompt" / "test.txt", test_rows, verb)
    # spp inputs
    _write_csv(BASELINES / task / "baseline.csv", pool, ["row_id", "text", "label"])
    _write_csv(BASELINES / task / "test_holdout.csv", test_rows, ["row_id", "text", "label"])

    dist = _dist(pool)
    meta = {
        "task": task,
        "hf_source": {
            "ag_news": "fancyzhx/ag_news",
            "sst5": "SetFit/sst5",
            "trec": "SetFit/TREC-QC",
        }[task],
        "license": {"ag_news": "custom non-commercial research (Zhang et al. 2015)",
                    "sst5": "CC-derived (Socher et al. 2013)",
                    "trec": "research use (Li & Roth 2002)"}[task],
        "classes": verb,
        "n_classes": len(verb),
        "metric": "accuracy",
        "splits": {
            "shared_test": len(test_rows),
            "baseline_pool": len(pool),
            "evoprompt_dev": len(dev),
        },
        "baseline_pool_class_dist": dist,
        "paper_reference_alpaca7b": PAPER_REF[task],
        "notes": "Label names follow EvoPrompt verbalizers. Paper numbers are "
        "Alpaca-7b reference only, NOT the target for gpt-oss-20b runs.",
    }
    (FIXTURES / task / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def _pick(r: dict) -> dict:
    return {"row_id": r["row_id"], "text": r["text"], "label": r["label"]}


def _dist(rows: list[dict]) -> dict:
    d: dict[str, int] = {}
    for r in rows:
        d[r["label"]] = d.get(r["label"], 0) + 1
    return dict(sorted(d.items()))


if __name__ == "__main__":
    for task in ["ag_news", "sst5", "trec"]:
        m = build(task)
        print(f"[{task}] test={m['splits']['shared_test']} "
              f"pool={m['splits']['baseline_pool']} dev={m['splits']['evoprompt_dev']} "
              f"classes={m['n_classes']} dist={m['baseline_pool_class_dist']}")
