"""Tests for repository-backed retrieval."""

from uuid import uuid4

from nexus.memory import (
    InMemoryRepository,
    MemoryRecord,
    MemorySource,
    MemoryStatus,
    MemoryType,
)
from nexus.retrieval import RepositoryRetrievalEngine, RetrievalQuery


def make_memory(
    content: str,
    *,
    memory_type: MemoryType = MemoryType.FACT,
    status: MemoryStatus = MemoryStatus.ACTIVE,
    project_id=None,
) -> MemoryRecord:
    return MemoryRecord(
        memory_type=memory_type,
        content=content,
        source=MemorySource.USER,
        status=status,
        project_id=project_id,
    )


def test_repository_engine_retrieves_memories() -> None:
    repository = InMemoryRepository()
    first = repository.create(make_memory("First memory."))
    second = repository.create(make_memory("Second memory."))

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(RetrievalQuery(text="memory"))

    assert [result.memory.id for result in results] == [
        first.id,
        second.id,
    ]


def test_repository_engine_respects_limit() -> None:
    repository = InMemoryRepository()
    first = repository.create(make_memory("First memory."))
    repository.create(make_memory("Second memory."))

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="memory",
            limit=1,
        )
    )

    assert [result.memory.id for result in results] == [second.id]


def test_repository_engine_passes_memory_type_filter() -> None:
    repository = InMemoryRepository()

    fact = repository.create(
        make_memory(
            "A fact.",
            memory_type=MemoryType.FACT,
        )
    )
    repository.create(
        make_memory(
            "A decision.",
            memory_type=MemoryType.DECISION,
        )
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="fact",
            memory_type=MemoryType.FACT,
        )
    )

    assert [result.memory.id for result in results] == [fact.id]


def test_repository_engine_passes_status_filter() -> None:
    repository = InMemoryRepository()

    active = repository.create(
        make_memory(
            "Active memory.",
            status=MemoryStatus.ACTIVE,
        )
    )
    repository.create(
        make_memory(
            "Archived memory.",
            status=MemoryStatus.ARCHIVED,
        )
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="memory",
            status=MemoryStatus.ACTIVE,
        )
    )

    assert [result.memory.id for result in results] == [active.id]


def test_repository_engine_passes_project_filter() -> None:
    repository = InMemoryRepository()

    project_id = uuid4()

    project_memory = repository.create(
        make_memory(
            "Project memory.",
            project_id=project_id,
        )
    )
    repository.create(
        make_memory(
            "Other project memory.",
            project_id=uuid4(),
        )
    )

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(
            text="memory",
            project_id=project_id,
        )
    )

    assert [result.memory.id for result in results] == [project_memory.id]


def test_repository_engine_ranks_relevant_memories_deterministically() -> None:
    repository = InMemoryRepository()

    low = repository.create(make_memory("Python."))
    high = repository.create(make_memory("Python PostgreSQL."))

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(
        RetrievalQuery(text="Python PostgreSQL")
    )

    assert [result.memory.id for result in results] == [
        high.id,
        low.id,
    ]


def test_repository_engine_initial_score_is_neutral() -> None:
    repository = InMemoryRepository()
    repository.create(make_memory("Memory."))

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(RetrievalQuery(text="memory"))

    assert len(results) == 1
    assert results[0].score == 1.0
