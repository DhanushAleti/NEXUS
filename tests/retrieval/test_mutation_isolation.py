"""Retrieval must return results isolated from repository internal state."""

from nexus.memory import InMemoryRepository, MemoryRecord, MemorySource, MemoryType
from nexus.retrieval import RepositoryRetrievalEngine, RetrievalQuery


def make_memory(content: str) -> MemoryRecord:
    return MemoryRecord(
        memory_type=MemoryType.FACT,
        content=content,
        source=MemorySource.USER,
    )


def test_mutating_result_memory_does_not_corrupt_repository() -> None:
    repository = InMemoryRepository()
    stored = repository.create(make_memory("NEXUS uses PostgreSQL."))

    engine = RepositoryRetrievalEngine(repository)

    results = engine.retrieve(RetrievalQuery(text="PostgreSQL"))

    assert len(results) == 1

    results[0].memory.content = "Mutated content."
    results[0].memory.metadata["tampered"] = True

    reloaded = repository.get(stored.id)

    assert reloaded is not None
    assert reloaded.content == "NEXUS uses PostgreSQL."
    assert reloaded.metadata == {}


def test_mutating_result_memory_does_not_leak_across_retrievals() -> None:
    repository = InMemoryRepository()
    repository.create(make_memory("NEXUS uses PostgreSQL."))

    engine = RepositoryRetrievalEngine(repository)
    query = RetrievalQuery(text="PostgreSQL")

    first = engine.retrieve(query)
    first[0].memory.content = "Mutated content."

    second = engine.retrieve(query)

    assert second[0].memory.content == "NEXUS uses PostgreSQL."
