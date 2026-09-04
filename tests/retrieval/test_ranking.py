"""Tests for deterministic retrieval ranking."""

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


def test_retrieval_ranks_higher_scores_first() -> None:
    repository = InMemoryRepository()

    low = repository.create(
        make_memory("Python is a programming language.")
    )
    high = repository.create(
        make_memory("Python PostgreSQL are used by NEXUS.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(text="Python PostgreSQL")
    )

    assert len(results) == 2
    assert results[0].score > results[1].score
    assert [result.memory.id for result in results] == [high.id, low.id]


def test_equal_scores_have_deterministic_memory_id_order() -> None:
    repository = InMemoryRepository()

    first = make_memory("PostgreSQL database.")
    second = make_memory("PostgreSQL database.")

    repository.create(first)
    repository.create(second)

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(text="PostgreSQL")
    )

    result_ids = [str(result.memory.id) for result in results]

    assert result_ids == sorted(result_ids)


def test_ranking_happens_before_limit() -> None:
    repository = InMemoryRepository()

    first = repository.create(
        make_memory("Python PostgreSQL database.")
    )
    second = repository.create(
        make_memory("Python.")
    )
    repository.create(
        make_memory("Redis cache.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="Python PostgreSQL",
            limit=1,
        )
    )

    assert len(results) == 1
    assert results[0].memory.id == first.id
    assert results[0].score > 0.0
    assert results[0].memory.id != second.id


def test_retrieval_is_repeatable() -> None:
    repository = InMemoryRepository()

    repository.create(
        make_memory("Python PostgreSQL.")
    )
    repository.create(
        make_memory("Python database.")
    )
    repository.create(
        make_memory("PostgreSQL database.")
    )

    engine = RepositoryRetrievalEngine(repository)
    query = RetrievalQuery(text="Python PostgreSQL")

    first_run = engine.retrieve(query)
    second_run = engine.retrieve(query)

    first_ids = [result.memory.id for result in first_run]
    second_ids = [result.memory.id for result in second_run]

    assert first_ids == second_ids
