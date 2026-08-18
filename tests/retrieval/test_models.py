from uuid import uuid4

import pytest
from pydantic import ValidationError

from nexus.memory import (
    MemoryRecord,
    MemorySource,
    MemoryStatus,
    MemoryType,
)
from nexus.retrieval import RetrievalQuery, RetrievalResult


def make_memory(
    memory_type: MemoryType = MemoryType.FACT,
    *,
    project_id=None,
    content: str = "PostgreSQL is used by NEXUS.",
) -> MemoryRecord:
    return MemoryRecord(
        memory_type=memory_type,
        content=content,
        source=MemorySource.USER,
        project_id=project_id,
    )


def test_retrieval_query_defaults():
    query = RetrievalQuery(text="  PostgreSQL  ")

    assert query.text == "PostgreSQL"
    assert query.project_id is None
    assert query.memory_type is None
    assert query.status is None
    assert query.limit == 10


def test_retrieval_query_accepts_explicit_constraints():
    project_id = uuid4()

    query = RetrievalQuery(
        text="database architecture",
        project_id=project_id,
        memory_type=MemoryType.DECISION,
        status=MemoryStatus.ACTIVE,
        limit=25,
    )

    assert query.text == "database architecture"
    assert query.project_id == project_id
    assert query.memory_type == MemoryType.DECISION
    assert query.status == MemoryStatus.ACTIVE
    assert query.limit == 25


def test_blank_retrieval_query_is_rejected():
    with pytest.raises(
        ValidationError,
        match="Retrieval query text cannot be blank",
    ):
        RetrievalQuery(text="   ")


def test_retrieval_query_requires_positive_limit():
    with pytest.raises(ValidationError):
        RetrievalQuery(
            text="database",
            limit=0,
        )


def test_retrieval_query_rejects_extra_fields():
    with pytest.raises(ValidationError):
        RetrievalQuery(
            text="database",
            unsupported_field=True,
        )


def test_retrieval_result_contains_memory_and_score():
    memory = make_memory()

    result = RetrievalResult(
        memory=memory,
        score=0.75,
    )

    assert result.memory == memory
    assert result.score == 0.75


def test_retrieval_result_accepts_negative_score():
    memory = make_memory()

    result = RetrievalResult(
        memory=memory,
        score=-1.5,
    )

    assert result.score == -1.5


def test_retrieval_result_rejects_extra_fields():
    memory = make_memory()

    with pytest.raises(ValidationError):
        RetrievalResult(
            memory=memory,
            score=0.75,
            unsupported_field=True,
        )
