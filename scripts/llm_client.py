"""Shared LLM client for spp-bm — talks to the local oMLX OpenAI-compatible server.

Both the EvoPrompt arm and any ad-hoc scoring go through this one wrapper so the
*task model* is provably identical across frameworks (the fairness invariant).

gpt-oss specifics this wrapper handles:
  - gpt-oss is a reasoning model: it emits chain-of-thought into a separate
    ``reasoning_content`` field and the actual answer into ``content``. Even at
    ``reasoning_effort="low"`` it spends ~40-80 tokens reasoning, so a tiny
    ``max_tokens`` starves the answer (finish_reason="length", empty content).
    We budget enough tokens and, if content still comes back empty, retry once
    with a larger budget.
  - The label is recovered from ``content`` by matching against the task's label
    space (exact, then case-insensitive, then substring), so stray punctuation or
    a trailing sentence does not break scoring.
"""

from __future__ import annotations

import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from openai import OpenAI

BASE_URL = os.environ.get("OMLX_BASE_URL", "http://127.0.0.1:8000/v1")
API_KEY = os.environ.get("OMLX_API_KEY", "jaywell06")
MODEL = os.environ.get("OMLX_MODEL", "gpt-oss-20b-MXFP4-Q8")

# oMLX effectively serializes requests on a single model instance; a tiny pool
# buys ~25% from request overlap, beyond that it is wasted threads.
MAX_WORKERS = int(os.environ.get("OMLX_WORKERS", "3"))

_client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


@dataclass(frozen=True)
class Completion:
    content: str
    reasoning: str
    output_tokens: int
    finish_reason: str


def complete(
    prompt: str,
    *,
    max_tokens: int = 256,
    temperature: float = 0.0,
    reasoning_effort: str = "low",
    retries: int = 3,
) -> Completion:
    """One chat completion. Retries on transient errors and on empty content."""
    last_exc: Exception | None = None
    budget = max_tokens
    for attempt in range(retries):
        try:
            resp = _client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=budget,
                temperature=temperature,
                extra_body={"reasoning_effort": reasoning_effort},
            )
            choice = resp.choices[0]
            msg = choice.message
            content = (msg.content or "").strip()
            reasoning = getattr(msg, "reasoning_content", "") or ""
            # Empty content + length stop => reasoning ate the budget. Grow it.
            if not content and choice.finish_reason == "length":
                budget = min(budget * 2, 1024)
                continue
            usage = resp.usage
            return Completion(
                content=content,
                reasoning=reasoning,
                output_tokens=getattr(usage, "output_tokens", 0) or 0,
                finish_reason=choice.finish_reason or "",
            )
        except Exception as exc:  # noqa: BLE001 — network/server transients
            last_exc = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"completion failed after {retries} retries: {last_exc}")


def match_label(content: str, label_space: list[str]) -> str | None:
    """Recover a canonical label from free-text content. None if no match."""
    if not content:
        return None
    text = content.strip()
    lower = text.lower()
    by_lower = {lab.lower(): lab for lab in label_space}
    # 1) exact (case-insensitive)
    if lower in by_lower:
        return by_lower[lower]
    # 2) the content is a single token / short phrase containing exactly one label
    hits = [lab for lab in label_space if re.search(rf"\b{re.escape(lab)}\b", text, re.IGNORECASE)]
    if len(hits) == 1:
        return hits[0]
    # 3) first label that appears, if multiple (take earliest position)
    positions = [
        (m.start(), lab)
        for lab in label_space
        if (m := re.search(rf"\b{re.escape(lab)}\b", text, re.IGNORECASE))
    ]
    if positions:
        return min(positions)[1]
    return None


def classify(prompt: str, label_space: list[str], **kw: object) -> tuple[str | None, Completion]:
    """Run a classification prompt and map the answer onto the label space."""
    comp = complete(prompt, **kw)  # type: ignore[arg-type]
    return match_label(comp.content, label_space), comp


def map_parallel(fn, items, workers: int = MAX_WORKERS):
    """Order-preserving parallel map with a small worker pool."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


if __name__ == "__main__":
    label, comp = classify(
        "Classify the sentiment as positive or negative. Reply with only the label.\n\n"
        "Text: a beautifully observed, miraculously unsentimental comedy-drama.\nLabel:",
        ["positive", "negative"],
    )
    print(
        f"label={label!r} content={comp.content!r} "
        f"tokens={comp.output_tokens} finish={comp.finish_reason}"
    )
