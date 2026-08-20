"""Tests for retrieval no-match behavior."""

from nexus.memory import (
    InMemoryRepository,
    MemoryRecord,
    MemorySource,
    MemoryType,
)
from nexus.retrieval import RepositoryRetrievalEngine, RetrievalQuery


def make_memory(content: str) -> MemoryRecord:
    return MemoryRecord(
        memory_type=MemoryType.FACT,
        content=content,
        source=MemorySource.USER,
    )


def test_no_matching_memory_returns_empty_result() -> None:
    repository = InMemoryRepository()

    repository.create(
        make_memory("NEXUS uses PostgreSQL.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(text="Redis")
    )

    assert results == []


def test_matching_memory_is_returned() -> None:
    repository = InMemoryRepository()

    memory = repository.create(
        make_memory("NEXUS uses PostgreSQL.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(text="PostgreSQL")
    )

    assert len(results) == 1
    assert results[0].memory.id == memory.id
    assert results[0].score > 0.0


def test_unrelated_memories_are_not_returned() -> None:
    repository = InMemoryRepository()

    matching = repository.create(
        make_memory("NEXUS uses PostgreSQL.")
    )
    repository.create(
        make_memory("NEXUS uses Redis.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(text="PostgreSQL")
    )

    assert [result.memory.id for result in results] == [
        matching.id,
    ]


def test_empty_repository_returns_empty_result() -> None:
    repository = InMemoryRepository()

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(text="PostgreSQL")
    )

    assert results == []


def test_limit_is_applied_after_zero_score_filtering() -> None:
    repository = InMemoryRepository()

    first = repository.create(
        make_memory("Python PostgreSQL database.")
    )
    repository.create(
        make_memory("Redis cache.")
    )
    second = repository.create(
        make_memory("Python PostgreSQL.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="Python PostgreSQL",
            limit=1,
        )
    )

    assert len(results) == 1
    assert results[0].memory.id == second.id
