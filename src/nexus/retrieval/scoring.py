"""Deterministic relevance scoring for retrieval candidates."""

from __future__ import annotations

import re

from nexus.memory import MemoryRecord

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> set[str]:
    """Return normalized lexical tokens from text."""
    return {
        token.lower()
        for token in _TOKEN_PATTERN.findall(text)
        if token
    }


def lexical_relevance_score(query: str, memory: MemoryRecord) -> float:
    """Return lexical query coverage for a memory.

    The score is the fraction of unique query tokens appearing in the
    memory content. An empty query produces a zero score.
    """
    query_tokens = tokenize(query)

    if not query_tokens:
        return 0.0

    memory_tokens = tokenize(memory.content)

    return len(query_tokens & memory_tokens) / len(query_tokens)
