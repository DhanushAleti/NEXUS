"""Tests for deterministic retrieval scoring."""

from nexus.memory import MemoryRecord, MemorySource, MemoryType
from nexus.retrieval.scoring import (
    explain_lexical_relevance,
    lexical_relevance_score,
    tokenize,
)


def make_memory(content: str) -> MemoryRecord:
    return MemoryRecord(
        memory_type=MemoryType.FACT,
        content=content,
        source=MemorySource.USER,
    )


def test_tokenize_normalizes_case() -> None:
    assert tokenize("PostgreSQL DATABASE") == {
        "postgresql",
        "database",
    }


def test_tokenize_ignores_punctuation() -> None:
    assert tokenize("NEXUS, memory; system.") == {
        "nexus",
        "memory",
        "system",
    }


def test_lexical_score_returns_full_match() -> None:
    memory = make_memory("NEXUS uses PostgreSQL for structured memory.")

    assert lexical_relevance_score(
        "NEXUS PostgreSQL",
        memory,
    ) == 1.0


def test_lexical_score_returns_partial_match() -> None:
    memory = make_memory("NEXUS uses PostgreSQL for structured memory.")

    assert lexical_relevance_score(
        "NEXUS Redis",
        memory,
    ) == 0.5


def test_lexical_score_returns_zero_when_no_tokens_match() -> None:
    memory = make_memory("NEXUS uses PostgreSQL.")

    assert lexical_relevance_score(
        "Redis database",
        memory,
    ) == 0.0


def test_lexical_score_is_case_insensitive() -> None:
    memory = make_memory("PostgreSQL is used by NEXUS.")

    assert lexical_relevance_score(
        "postgresql nexus",
        memory,
    ) == 1.0


def test_lexical_score_uses_unique_query_tokens() -> None:
    memory = make_memory("NEXUS uses PostgreSQL.")

    assert lexical_relevance_score(
        "NEXUS NEXUS PostgreSQL",
        memory,
    ) == 1.0


def test_lexical_score_returns_zero_for_empty_query() -> None:
    memory = make_memory("NEXUS uses PostgreSQL.")

    assert lexical_relevance_score("", memory) == 0.0


def test_explain_lexical_relevance_reports_matches_and_missing_tokens() -> None:
    memory = make_memory("NEXUS uses PostgreSQL for structured memory.")

    explanation = explain_lexical_relevance(
        "NEXUS PostgreSQL Redis",
        memory,
    )

    assert explanation.query_tokens == {
        "nexus",
        "postgresql",
        "redis",
    }
    assert explanation.matched_tokens == {
        "nexus",
        "postgresql",
    }
    assert explanation.missing_tokens == {"redis"}
    assert explanation.score == 2 / 3


def test_explain_lexical_relevance_handles_empty_query() -> None:
    memory = make_memory("NEXUS uses PostgreSQL.")

    explanation = explain_lexical_relevance("", memory)

    assert explanation.query_tokens == frozenset()
    assert explanation.matched_tokens == frozenset()
    assert explanation.missing_tokens == frozenset()
    assert explanation.score == 0.0


def test_lexical_score_remains_compatible_with_explanation() -> None:
    memory = make_memory("NEXUS uses PostgreSQL for structured memory.")

    explanation = explain_lexical_relevance("NEXUS PostgreSQL", memory)

    assert lexical_relevance_score("NEXUS PostgreSQL", memory) == explanation.score
