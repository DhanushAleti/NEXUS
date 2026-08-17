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



def test_valid_temporal_interval_is_accepted():
    start = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
    end = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)

    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="A fact with a valid temporal interval.",
        source=MemorySource.USER,
        valid_from=start,
        valid_until=end,
    )

    assert memory.valid_from == start
    assert memory.valid_until == end


def test_open_ended_temporal_interval_is_accepted():
    start = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)

    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="A currently valid fact.",
        source=MemorySource.USER,
        valid_from=start,
    )

    assert memory.valid_from == start
    assert memory.valid_until is None


def test_temporal_interval_with_equal_bounds_is_accepted():
    timestamp = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)

    memory = MemoryRecord(
        memory_type=MemoryType.EVENT,
        content="A point-in-time event.",
        source=MemorySource.SYSTEM,
        valid_from=timestamp,
        valid_until=timestamp,
    )

    assert memory.valid_from == timestamp
    assert memory.valid_until == timestamp


def test_invalid_temporal_interval_is_rejected():
    start = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)
    end = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)

    with pytest.raises(
        ValidationError,
        match="valid_until cannot be earlier than valid_from",
    ):
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Invalid temporal interval.",
            source=MemorySource.USER,
            valid_from=start,
            valid_until=end,
        )


def test_naive_valid_from_is_rejected():
    naive_timestamp = datetime(2026, 8, 10, 12, 0)  # noqa: DTZ001

    with pytest.raises(
        ValidationError,
        match="Datetime must be timezone-aware",
    ):
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Naive valid_from test.",
            source=MemorySource.USER,
            valid_from=naive_timestamp,
        )


def test_naive_valid_until_is_rejected():
    naive_timestamp = datetime(2026, 8, 10, 12, 0)  # noqa: DTZ001

    with pytest.raises(
        ValidationError,
        match="Datetime must be timezone-aware",
    ):
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Naive valid_until test.",
            source=MemorySource.USER,
            valid_until=naive_timestamp,
        )
