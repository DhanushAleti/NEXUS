from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from nexus.memory.relationships import (
    MemoryRelation,
    MemoryRelationType,
)


def make_relation(**overrides):
    values = {
        "relation_type": MemoryRelationType.RELATED_TO,
        "source_memory_id": uuid4(),
        "target_memory_id": uuid4(),
    }
    values.update(overrides)
    return MemoryRelation(**values)


def test_memory_relation_has_generated_id():
    relation = make_relation()

    assert isinstance(relation.id, UUID)


def test_memory_relation_defaults():
    relation = make_relation()

    assert relation.confidence == 1.0
    assert relation.metadata == {}


def test_memory_relation_stores_source_and_target():
    source_id = uuid4()
    target_id = uuid4()

    relation = make_relation(
        source_memory_id=source_id,
        target_memory_id=target_id,
    )

    assert relation.source_memory_id == source_id
    assert relation.target_memory_id == target_id


def test_memory_relation_supports_all_canonical_types():
    for relation_type in MemoryRelationType:
        relation = make_relation(relation_type=relation_type)

        assert relation.relation_type == relation_type


def test_memory_relation_rejects_self_relationship():
    memory_id = uuid4()

    with pytest.raises(
        ValidationError,
        match="source_memory_id and target_memory_id must differ",
    ):
        make_relation(
            source_memory_id=memory_id,
            target_memory_id=memory_id,
        )


def test_memory_relation_confidence_must_be_between_zero_and_one():
    with pytest.raises(ValidationError):
        make_relation(confidence=1.5)

    with pytest.raises(ValidationError):
        make_relation(confidence=-0.1)


def test_memory_relation_rejects_naive_created_at():
    naive_timestamp = datetime(2026, 8, 17, 12, 0)  # noqa: DTZ001

    with pytest.raises(
        ValidationError,
        match="Datetime must be timezone-aware",
    ):
        make_relation(created_at=naive_timestamp)


def test_memory_relation_accepts_timezone_aware_created_at():
    timestamp = datetime(
        2026,
        8,
        17,
        12,
        0,
        tzinfo=UTC,
    )

    relation = make_relation(created_at=timestamp)

    assert relation.created_at == timestamp


def test_memory_relation_rejects_extra_fields():
    with pytest.raises(ValidationError):
        make_relation(
            unexpected_field="should fail",
        )


def test_memory_relation_metadata_is_preserved():
    relation = make_relation(
        metadata={
            "reason": "same project",
            "origin": "test",
        }
    )

    assert relation.metadata == {
        "reason": "same project",
        "origin": "test",
    }
