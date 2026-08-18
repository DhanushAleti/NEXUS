import pytest

from nexus.memory import MemoryRecord, MemorySource, MemoryType
from nexus.retrieval import (
    RetrievalEngine,
    RetrievalQuery,
    RetrievalResult,
)


def make_memory(content: str) -> MemoryRecord:
    return MemoryRecord(
        memory_type=MemoryType.FACT,
        content=content,
        source=MemorySource.USER,
    )


class StubRetrievalEngine(RetrievalEngine):
    def __init__(self, results: list[RetrievalResult]) -> None:
        self._results = results

    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        return self._results[: query.limit]


def test_retrieval_engine_is_abstract():
    with pytest.raises(TypeError):
        RetrievalEngine()


def test_retrieval_engine_contract_accepts_query_and_returns_results():
    memory = make_memory("NEXUS uses structured memory.")

    result = RetrievalResult(
        memory=memory,
        score=0.9,
    )

    engine = StubRetrievalEngine([result])

    query = RetrievalQuery(
        text="structured memory",
    )

    retrieved = engine.retrieve(query)

    assert retrieved == [result]


def test_retrieval_engine_respects_query_limit_in_stub():
    first = RetrievalResult(
        memory=make_memory("First memory."),
        score=0.9,
    )
    second = RetrievalResult(
        memory=make_memory("Second memory."),
        score=0.8,
    )

    engine = StubRetrievalEngine([first, second])

    query = RetrievalQuery(
        text="memory",
        limit=1,
    )

    retrieved = engine.retrieve(query)

    assert retrieved == [first]


def test_retrieval_results_preserve_engine_order():
    first = RetrievalResult(
        memory=make_memory("First memory."),
        score=0.2,
    )
    second = RetrievalResult(
        memory=make_memory("Second memory."),
        score=0.9,
    )

    engine = StubRetrievalEngine([first, second])

    query = RetrievalQuery(text="memory")

    retrieved = engine.retrieve(query)

    assert [result.memory.content for result in retrieved] == [
        "First memory.",
        "Second memory.",
    ]
