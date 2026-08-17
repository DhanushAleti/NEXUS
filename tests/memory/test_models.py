from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from nexus.memory import (
    MemoryRecord,
    MemorySource,
    MemoryStatus,
    MemoryType,
    Project,
)


def test_memory_record_has_generated_id():
    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="NEXUS uses PostgreSQL.",
        source=MemorySource.USER,
    )

    assert isinstance(memory.id, UUID)


def test_memory_record_defaults():
    memory = MemoryRecord(
        memory_type=MemoryType.EVENT,
        content="A test event occurred.",
        source=MemorySource.SYSTEM,
    )

    assert memory.status == MemoryStatus.ACTIVE
    assert memory.confidence == 1.0
    assert memory.tags == []
    assert memory.metadata == {}


def test_memory_record_normalizes_content():
    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="   PostgreSQL is the database.   ",
        source=MemorySource.USER,
    )

    assert memory.content == "PostgreSQL is the database."


def test_blank_content_is_rejected():
    with pytest.raises(ValidationError):
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="   ",
            source=MemorySource.USER,
        )


def test_confidence_must_be_between_zero_and_one():
    with pytest.raises(ValidationError):
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Invalid confidence.",
            source=MemorySource.USER,
            confidence=1.5,
        )


def test_tags_are_normalized_and_deduplicated():
    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="PostgreSQL is used.",
        source=MemorySource.USER,
        tags=[" Database ", "database", "AI", "ai", ""],
    )

    assert memory.tags == ["database", "ai"]


def test_project_has_generated_id():
    project = Project(
        name="NEXUS",
        description="Personal AI operating system.",
    )

    assert isinstance(project.id, UUID)


def test_project_name_cannot_be_blank():
    with pytest.raises(ValidationError):
        Project(name="   ")


def test_observed_at_accepts_timezone_aware_datetime():
    timestamp = datetime.now(UTC)

    memory = MemoryRecord(
        memory_type=MemoryType.EVENT,
        content="Experiment completed.",
        source=MemorySource.SYSTEM,
        observed_at=timestamp,
    )

    assert memory.observed_at == timestamp


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Unexpected field test.",
            source=MemorySource.USER,
            unknown_field="should fail",
        )
