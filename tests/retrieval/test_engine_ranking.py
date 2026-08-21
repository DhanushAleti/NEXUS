"""Tests for retrieval scoring and ranking."""

from nexus.memory import InMemoryRepository, MemoryRecord, MemorySource, MemoryType
from nexus.retrieval import RepositoryRetrievalEngine, RetrievalQuery


def make_memory(content: str) -> MemoryRecord:
    return MemoryRecord(
        memory_type=MemoryType.FACT,
        content=content,
        source=MemorySource.USER,
    )


def test_engine_ranks_higher_relevance_first() -> None:
    repository = InMemoryRepository()

    low = repository.create(
        make_memory("NEXUS uses Python.")
    )
    high = repository.create(
        make_memory("NEXUS uses Python and PostgreSQL.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="Python PostgreSQL",
        )
    )

    assert [result.memory.id for result in results] == [
        high.id,
        low.id,
    ]


def test_engine_returns_relevance_scores() -> None:
    repository = InMemoryRepository()

    memory = repository.create(
        make_memory("NEXUS uses PostgreSQL.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="NEXUS PostgreSQL",
        )
    )

    assert len(results) == 1
    assert results[0].memory.id == memory.id
    assert results[0].score == 1.0


def test_engine_applies_limit_after_ranking() -> None:
    repository = InMemoryRepository()

    repository.create(
        make_memory("Python.")
    )
    high = repository.create(
        make_memory("Python PostgreSQL database.")
    )
    middle = repository.create(
        make_memory("Python PostgreSQL.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="Python PostgreSQL database",
            limit=2,
        )
    )

    assert [result.memory.id for result in results] == [
        high.id,
        middle.id,
    ]


def test_engine_orders_equal_scores_deterministically() -> None:
    repository = InMemoryRepository()

    first = repository.create(
        make_memory("Python.")
    )
    second = repository.create(
        make_memory("Python.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="Python",
        )
    )

    expected = sorted(
        [first.id, second.id],
        key=str,
    )

    assert [result.memory.id for result in results] == expected


def test_engine_returns_zero_score_for_non_matching_memory() -> None:
    repository = InMemoryRepository()

    repository.create(
        make_memory("PostgreSQL database.")
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="Redis",
        )
    )

    assert results == []
