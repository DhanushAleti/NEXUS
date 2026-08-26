"""Deterministic relevance scoring for retrieval candidates."""

from __future__ import annotations

from dataclasses import dataclass
import re

from nexus.memory import MemoryRecord

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class RelevanceExplanation:
    """Explain how lexical relevance was calculated."""

    query_tokens: frozenset[str]
    matched_tokens: frozenset[str]
    missing_tokens: frozenset[str]
    score: float


def tokenize(text: str) -> set[str]:
    """Return normalized lexical tokens from text."""
    return {
        token.lower()
        for token in _TOKEN_PATTERN.findall(text)
        if token
    }


def explain_lexical_relevance(
    query: str,
    memory: MemoryRecord,
) -> RelevanceExplanation:
    """Return a deterministic explanation of lexical relevance."""
    query_tokens = frozenset(tokenize(query))

    if not query_tokens:
        return RelevanceExplanation(
            query_tokens=frozenset(),
            matched_tokens=frozenset(),
            missing_tokens=frozenset(),
            score=0.0,
        )

    memory_tokens = frozenset(tokenize(memory.content))
    matched_tokens = query_tokens & memory_tokens
    missing_tokens = query_tokens - memory_tokens
    score = len(matched_tokens) / len(query_tokens)

    return RelevanceExplanation(
        query_tokens=query_tokens,
        matched_tokens=matched_tokens,
        missing_tokens=missing_tokens,
        score=score,
    )


def lexical_relevance_score(
    query: str,
    memory: MemoryRecord,
) -> float:
    """Return lexical query coverage for a memory.

    The score is the fraction of unique query tokens appearing in the
    memory content. An empty query produces a zero score.
    """
    return explain_lexical_relevance(query, memory).score
