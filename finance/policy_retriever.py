from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
POLICY_DIR = PROJECT_ROOT / "data" / "finance" / "policies"


@dataclass(frozen=True)
class PolicyChunk:
    source: str
    text: str
    score: int


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower()))


def retrieve_policy(query: str, top_k: int = 3) -> list[PolicyChunk]:
    """Small deterministic lexical retriever used for the finance-policy layer.

    It is intentionally simple for Phase 2. The same documents can later be
    ingested into the project's existing hybrid FAISS/BM25 RAG stack.
    """
    query_tokens = _tokens(query)
    chunks: list[PolicyChunk] = []

    for path in sorted(POLICY_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for paragraph in paragraphs:
            score = len(query_tokens & _tokens(paragraph))
            if score:
                chunks.append(PolicyChunk(path.name, paragraph, score))

    chunks.sort(key=lambda item: (-item.score, item.source))
    return chunks[:top_k]
