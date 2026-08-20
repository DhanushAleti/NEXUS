# NEXUS Retrieval Contract Inspection

Generated: Wed Aug 19 21:36:30 IST 2026

Commit: 99578d7

## Git Status
?? inspection/

## Repository Tree
src/nexus/__init__.py
src/nexus/__pycache__/__init__.cpython-313.pyc
src/nexus/context/__init__.py
src/nexus/ingestion/__init__.py
src/nexus/memory/__init__.py
src/nexus/memory/__pycache__/__init__.cpython-313.pyc
src/nexus/memory/__pycache__/models.cpython-313.pyc
src/nexus/memory/__pycache__/relationship_repository.cpython-313.pyc
src/nexus/memory/__pycache__/relationships.cpython-313.pyc
src/nexus/memory/__pycache__/repository.cpython-313.pyc
src/nexus/memory/models.py
src/nexus/memory/relationship_repository.py
src/nexus/memory/relationships.py
src/nexus/memory/repository.py
src/nexus/retrieval/__init__.py
src/nexus/retrieval/__pycache__/__init__.cpython-313.pyc
src/nexus/retrieval/__pycache__/engine.cpython-313.pyc
src/nexus/retrieval/__pycache__/models.cpython-313.pyc
src/nexus/retrieval/__pycache__/scoring.cpython-313.pyc
src/nexus/retrieval/engine.py
src/nexus/retrieval/models.py
src/nexus/retrieval/scoring.py

## Test Tree
tests/__pycache__/test_smoke.cpython-313-pytest-9.1.1.pyc
tests/memory/__pycache__/test_models.cpython-313-pytest-9.1.1.pyc
tests/memory/__pycache__/test_relationship_repository.cpython-313-pytest-9.1.1.pyc
tests/memory/__pycache__/test_relationships.cpython-313-pytest-9.1.1.pyc
tests/memory/__pycache__/test_repository.cpython-313-pytest-9.1.1.pyc
tests/memory/test_models.py
tests/memory/test_relationship_repository.py
tests/memory/test_relationships.py
tests/memory/test_repository.py
tests/retrieval/__pycache__/test_engine_ranking.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_engine.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_models.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_no_match.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_ranking.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_repository_engine.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_retrieval_models.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_scoring.cpython-313-pytest-9.1.1.pyc
tests/retrieval/test_engine_ranking.py
tests/retrieval/test_engine.py
tests/retrieval/test_no_match.py
tests/retrieval/test_ranking.py
tests/retrieval/test_repository_engine.py
tests/retrieval/test_retrieval_models.py
tests/retrieval/test_scoring.py
tests/test_smoke.py

---
# models.py
---
from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class MemoryType(str, Enum):
    """Canonical categories of information stored by NEXUS."""

    EVENT = "event"
    FACT = "fact"
    DECISION = "decision"
    TASK = "task"
    GOAL = "goal"
    ARTIFACT = "artifact"


class MemorySource(str, Enum):
    """Origin of a memory."""

    USER = "user"
    FILE = "file"
    GIT = "git"
    WEB = "web"
    TOOL = "tool"
    AGENT = "agent"
    SYSTEM = "system"
    INFERRED = "inferred"


class MemoryStatus(str, Enum):
    """Lifecycle state of a memory."""

    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    DISPUTED = "disputed"


class MemoryRecord(BaseModel):
    """Canonical NEXUS memory record."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: UUID = Field(default_factory=uuid4)

    memory_type: MemoryType
    content: str = Field(min_length=1)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    observed_at: datetime | None = None

    valid_from: datetime | None = None
    valid_until: datetime | None = None

    source: MemorySource
    source_ref: str | None = None

    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    project_id: UUID | None = None

    status: MemoryStatus = MemoryStatus.ACTIVE

    supersedes: UUID | None = None

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        """Reject whitespace-only memory content."""

        if not value.strip():
            raise ValueError("Memory content cannot be blank.")

        return value.strip()

    @field_validator("created_at", "observed_at", "valid_from", "valid_until")
    @classmethod
    def datetime_must_be_timezone_aware(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        """Reject naive datetimes."""

        if value is not None and value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware.")

        return value

    @model_validator(mode="after")
    def validate_temporal_bounds(self) -> MemoryRecord:
        """Ensure valid_until is not earlier than valid_from."""

        if (
            self.valid_from is not None
            and self.valid_until is not None
            and self.valid_until < self.valid_from
        ):
            raise ValueError(
                "valid_until cannot be earlier than valid_from."
            )

        return self

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str]) -> list[str]:
        """Normalize tags and remove duplicates while preserving order."""

        normalized: list[str] = []
        seen: set[str] = set()

        for tag in value:
            cleaned = tag.strip().lower()

            if cleaned and cleaned not in seen:
                normalized.append(cleaned)
                seen.add(cleaned)

        return normalized


class Project(BaseModel):
    """A project represented inside the NEXUS world model."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: UUID = Field(default_factory=uuid4)

    name: str = Field(min_length=1)

    description: str = ""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    status: str = "active"

    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        """Reject whitespace-only project names."""

        if not value.strip():
            raise ValueError("Project name cannot be blank.")

        return value.strip()

---
# relationships.py
---
from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class MemoryRelationType(str, Enum):
    """Canonical relationship types between NEXUS memories."""

    RELATED_TO = "related_to"
    DERIVED_FROM = "derived_from"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    REFERENCES = "references"


class MemoryRelation(BaseModel):
    """A directed relationship between two NEXUS memory records."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    id: UUID = Field(default_factory=uuid4)

    relation_type: MemoryRelationType

    source_memory_id: UUID
    target_memory_id: UUID

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("created_at")
    @classmethod
    def datetime_must_be_timezone_aware(
        cls,
        value: datetime,
    ) -> datetime:
        """Reject naive relationship timestamps."""

        if value.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware.")

        return value

    @model_validator(mode="after")
    def source_and_target_must_differ(self) -> MemoryRelation:
        """Prevent a memory from relating to itself."""

        if self.source_memory_id == self.target_memory_id:
            raise ValueError(
                "source_memory_id and target_memory_id must differ."
            )

        return self

---
# repository.py
---
from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from uuid import UUID

from .models import MemoryRecord, MemoryStatus, MemoryType


class MemoryRepository(ABC):
    """Abstract interface for NEXUS memory storage."""

    @abstractmethod
    def create(self, memory: MemoryRecord) -> MemoryRecord:
        """Store a new memory and return a copy of it."""

    @abstractmethod
    def get(self, memory_id: UUID) -> MemoryRecord | None:
        """Return a copy of a memory by ID, or None if absent."""

    @abstractmethod
    def list(
        self,
        *,
        memory_type: MemoryType | None = None,
        status: MemoryStatus | None = None,
        project_id: UUID | None = None,
    ) -> list[MemoryRecord]:
        """Return copies of memories matching the supplied filters."""

    @abstractmethod
    def update(self, memory: MemoryRecord) -> MemoryRecord:
        """Replace an existing memory."""

    @abstractmethod
    def archive(self, memory_id: UUID) -> MemoryRecord:
        """Archive an existing memory."""

    @abstractmethod
    def delete(self, memory_id: UUID) -> None:
        """Permanently delete a memory."""


class InMemoryRepository(MemoryRepository):
    """In-memory repository with explicit mutation boundaries."""

    def __init__(self) -> None:
        self._memories: dict[UUID, MemoryRecord] = {}

    def create(self, memory: MemoryRecord) -> MemoryRecord:
        """Store a new memory."""

        if memory.id in self._memories:
            raise ValueError(f"Memory already exists: {memory.id}")

        self._memories[memory.id] = deepcopy(memory)

        return deepcopy(memory)

    def get(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve an isolated copy of a memory by ID."""

        memory = self._memories.get(memory_id)

        if memory is None:
            return None

        return deepcopy(memory)

    def list(
        self,
        *,
        memory_type: MemoryType | None = None,
        status: MemoryStatus | None = None,
        project_id: UUID | None = None,
    ) -> list[MemoryRecord]:
        """Return isolated copies matching all supplied filters."""

        memories = list(self._memories.values())

        if memory_type is not None:
            memories = [
                memory
                for memory in memories
                if memory.memory_type == memory_type
            ]

        if status is not None:
            memories = [
                memory
                for memory in memories
                if memory.status == status
            ]

        if project_id is not None:
            memories = [
                memory
                for memory in memories
                if memory.project_id == project_id
            ]

        return deepcopy(memories)

    def update(self, memory: MemoryRecord) -> MemoryRecord:
        """Replace an existing memory."""

        if memory.id not in self._memories:
            raise KeyError(f"Memory not found: {memory.id}")

        self._memories[memory.id] = deepcopy(memory)

        return deepcopy(memory)

    def archive(self, memory_id: UUID) -> MemoryRecord:
        """Mark a memory as archived."""

        memory = self._memories.get(memory_id)

        if memory is None:
            raise KeyError(f"Memory not found: {memory_id}")

        memory = deepcopy(memory)
        memory.status = MemoryStatus.ARCHIVED

        self._memories[memory_id] = memory

        return deepcopy(memory)

    def delete(self, memory_id: UUID) -> None:
        """Permanently delete a memory."""

        if memory_id not in self._memories:
            raise KeyError(f"Memory not found: {memory_id}")

        del self._memories[memory_id]

---
# relationship_repository.py
---
from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from uuid import UUID

from .relationships import MemoryRelation, MemoryRelationType


class MemoryRelationRepository(ABC):
    """Abstract interface for NEXUS memory relationship storage."""

    @abstractmethod
    def create(self, relation: MemoryRelation) -> MemoryRelation:
        """Store a new relationship and return a copy of it."""
        raise NotImplementedError

    @abstractmethod
    def get(self, relation_id: UUID) -> MemoryRelation | None:
        """Return a copy of a relationship by ID, or None if absent."""
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        *,
        relation_type: MemoryRelationType | None = None,
        source_memory_id: UUID | None = None,
        target_memory_id: UUID | None = None,
    ) -> list[MemoryRelation]:
        """Return copies matching all supplied filters."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, relation_id: UUID) -> None:
        """Permanently delete a relationship."""
        raise NotImplementedError


class InMemoryMemoryRelationRepository(MemoryRelationRepository):
    """In-memory relationship repository with explicit mutation boundaries."""

    def __init__(self) -> None:
        self._relations: dict[UUID, MemoryRelation] = {}

    def create(self, relation: MemoryRelation) -> MemoryRelation:
        """Store a new relationship."""
        if relation.id in self._relations:
            raise ValueError(f"Relationship already exists: {relation.id}")

        self._relations[relation.id] = deepcopy(relation)
        return deepcopy(relation)

    def get(self, relation_id: UUID) -> MemoryRelation | None:
        """Retrieve an isolated copy of a relationship by ID."""
        relation = self._relations.get(relation_id)

        if relation is None:
            return None

        return deepcopy(relation)

    def list(
        self,
        *,
        relation_type: MemoryRelationType | None = None,
        source_memory_id: UUID | None = None,
        target_memory_id: UUID | None = None,
    ) -> list[MemoryRelation]:
        """Return isolated copies matching all supplied filters."""
        relations = list(self._relations.values())

        if relation_type is not None:
            relations = [
                relation
                for relation in relations
                if relation.relation_type == relation_type
            ]

        if source_memory_id is not None:
            relations = [
                relation
                for relation in relations
                if relation.source_memory_id == source_memory_id
            ]

        if target_memory_id is not None:
            relations = [
                relation
                for relation in relations
                if relation.target_memory_id == target_memory_id
            ]

        return deepcopy(relations)

    def delete(self, relation_id: UUID) -> None:
        """Permanently delete a relationship."""
        if relation_id not in self._relations:
            raise KeyError(f"Relationship not found: {relation_id}")

        del self._relations[relation_id]

---
# Memory Tests
---

## tests/memory/test_models.py
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

## tests/memory/test_relationship_repository.py
from uuid import UUID, uuid4

import pytest

from nexus.memory.relationship_repository import (
    InMemoryMemoryRelationRepository,
)
from nexus.memory.relationships import MemoryRelation, MemoryRelationType


def make_relation(
    relation_type: MemoryRelationType = MemoryRelationType.RELATED_TO,
    *,
    relation_id: UUID | None = None,
    source_memory_id: UUID | None = None,
    target_memory_id: UUID | None = None,
) -> MemoryRelation:
    """Create a valid MemoryRelation for repository tests."""
    source_id = source_memory_id or uuid4()
    target_id = target_memory_id or uuid4()

    if source_id == target_id:
        target_id = uuid4()

    return MemoryRelation(
        id=relation_id or uuid4(),
        relation_type=relation_type,
        source_memory_id=source_id,
        target_memory_id=target_id,
    )


def test_create_and_get_relationship():
    repository = InMemoryMemoryRelationRepository()
    relation = make_relation()

    created = repository.create(relation)
    retrieved = repository.get(relation.id)

    assert created == relation
    assert retrieved == relation


def test_duplicate_relationship_id_is_rejected():
    repository = InMemoryMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)

    with pytest.raises(
        ValueError,
        match="Relationship already exists",
    ):
        repository.create(relation)


def test_get_missing_relationship_returns_none():
    repository = InMemoryMemoryRelationRepository()

    assert repository.get(uuid4()) is None


def test_delete_removes_relationship():
    repository = InMemoryMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)
    repository.delete(relation.id)

    assert repository.get(relation.id) is None
    assert repository.list() == []


def test_delete_missing_relationship_is_rejected():
    repository = InMemoryMemoryRelationRepository()

    with pytest.raises(
        KeyError,
        match="Relationship not found",
    ):
        repository.delete(uuid4())


def test_create_does_not_expose_internal_state():
    repository = InMemoryMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)

    relation.metadata["outside_mutation"] = True

    stored = repository.get(relation.id)

    assert stored is not None
    assert stored.metadata == {}


def test_get_returns_isolated_relationship_copy():
    repository = InMemoryMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)

    retrieved = repository.get(relation.id)

    assert retrieved is not None

    retrieved.metadata["mutated"] = True

    stored = repository.get(relation.id)

    assert stored is not None
    assert stored.metadata == {}


def test_list_returns_isolated_relationship_copies():
    repository = InMemoryMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)

    result = repository.list()

    assert len(result) == 1

    result[0].metadata["mutated"] = True

    stored = repository.get(relation.id)

    assert stored is not None
    assert stored.metadata == {}


def test_list_preserves_insertion_order():
    repository = InMemoryMemoryRelationRepository()

    first = make_relation()
    second = make_relation()
    third = make_relation()

    repository.create(first)
    repository.create(second)
    repository.create(third)

    result = repository.list()

    assert [relation.id for relation in result] == [
        first.id,
        second.id,
        third.id,
    ]


def test_list_filters_by_relation_type():
    repository = InMemoryMemoryRelationRepository()

    related = make_relation(
        MemoryRelationType.RELATED_TO,
    )
    supports = make_relation(
        MemoryRelationType.SUPPORTS,
    )
    contradicts = make_relation(
        MemoryRelationType.CONTRADICTS,
    )

    repository.create(related)
    repository.create(supports)
    repository.create(contradicts)

    result = repository.list(
        relation_type=MemoryRelationType.SUPPORTS,
    )

    assert result == [supports]


def test_list_filters_by_source_memory_id():
    repository = InMemoryMemoryRelationRepository()

    source_id = uuid4()

    matching = make_relation(
        source_memory_id=source_id,
    )
    non_matching = make_relation()

    repository.create(matching)
    repository.create(non_matching)

    result = repository.list(
        source_memory_id=source_id,
    )

    assert result == [matching]


def test_list_filters_by_target_memory_id():
    repository = InMemoryMemoryRelationRepository()

    target_id = uuid4()

    matching = make_relation(
        target_memory_id=target_id,
    )
    non_matching = make_relation()

    repository.create(matching)
    repository.create(non_matching)

    result = repository.list(
        target_memory_id=target_id,
    )

    assert result == [matching]


def test_list_combines_filters_with_and_semantics():
    repository = InMemoryMemoryRelationRepository()

    source_id = uuid4()
    target_id = uuid4()

    matching = make_relation(
        MemoryRelationType.SUPPORTS,
        source_memory_id=source_id,
        target_memory_id=target_id,
    )

    wrong_type = make_relation(
        MemoryRelationType.RELATED_TO,
        source_memory_id=source_id,
        target_memory_id=target_id,
    )

    wrong_source = make_relation(
        MemoryRelationType.SUPPORTS,
        source_memory_id=uuid4(),
        target_memory_id=target_id,
    )

    wrong_target = make_relation(
        MemoryRelationType.SUPPORTS,
        source_memory_id=source_id,
        target_memory_id=uuid4(),
    )

    repository.create(matching)
    repository.create(wrong_type)
    repository.create(wrong_source)
    repository.create(wrong_target)

    result = repository.list(
        relation_type=MemoryRelationType.SUPPORTS,
        source_memory_id=source_id,
        target_memory_id=target_id,
    )

    assert result == [matching]

## tests/memory/test_relationships.py
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

## tests/memory/test_repository.py
from uuid import uuid4

import pytest

from nexus.memory import (
    InMemoryRepository,
    MemoryRecord,
    MemorySource,
    MemoryStatus,
    MemoryType,
)


def make_memory(
    memory_type: MemoryType = MemoryType.FACT,
    *,
    project_id=None,
    content: str = "Test memory.",
) -> MemoryRecord:
    return MemoryRecord(
        memory_type=memory_type,
        content=content,
        source=MemorySource.USER,
        project_id=project_id,
    )


def test_create_and_get_memory():
    repository = InMemoryRepository()
    memory = make_memory()

    created = repository.create(memory)

    assert created == memory
    assert repository.get(memory.id) == memory


def test_get_missing_memory_returns_none():
    repository = InMemoryRepository()

    assert repository.get(uuid4()) is None


def test_create_duplicate_memory_is_rejected():
    repository = InMemoryRepository()
    memory = make_memory()

    repository.create(memory)

    with pytest.raises(ValueError, match="already exists"):
        repository.create(memory)


def test_list_returns_all_memories():
    repository = InMemoryRepository()

    first = make_memory(content="First memory.")
    second = make_memory(content="Second memory.")

    repository.create(first)
    repository.create(second)

    memories = repository.list()

    assert memories == [first, second]


def test_list_filters_by_memory_type():
    repository = InMemoryRepository()

    fact = make_memory(MemoryType.FACT)
    decision = make_memory(MemoryType.DECISION)

    repository.create(fact)
    repository.create(decision)

    memories = repository.list(memory_type=MemoryType.DECISION)

    assert memories == [decision]


def test_list_filters_by_status():
    repository = InMemoryRepository()

    active = make_memory()
    archived = make_memory()

    repository.create(active)
    repository.create(archived)

    repository.archive(archived.id)

    assert repository.list(status=MemoryStatus.ACTIVE) == [active]

    archived_result = repository.list(status=MemoryStatus.ARCHIVED)

    assert len(archived_result) == 1
    assert archived_result[0].id == archived.id
    assert archived_result[0].status == MemoryStatus.ARCHIVED


def test_list_filters_by_project():
    repository = InMemoryRepository()

    project_a = uuid4()
    project_b = uuid4()

    memory_a = make_memory(project_id=project_a)
    memory_b = make_memory(project_id=project_b)

    repository.create(memory_a)
    repository.create(memory_b)

    assert repository.list(project_id=project_a) == [memory_a]
    assert repository.list(project_id=project_b) == [memory_b]


def test_list_combines_filters():
    repository = InMemoryRepository()

    project_id = uuid4()

    matching = make_memory(
        MemoryType.DECISION,
        project_id=project_id,
        content="Matching memory.",
    )

    wrong_type = make_memory(
        MemoryType.FACT,
        project_id=project_id,
    )

    wrong_project = make_memory(
        MemoryType.DECISION,
        project_id=uuid4(),
    )

    repository.create(matching)
    repository.create(wrong_type)
    repository.create(wrong_project)

    result = repository.list(
        memory_type=MemoryType.DECISION,
        project_id=project_id,
    )

    assert result == [matching]


def test_update_replaces_existing_memory():
    repository = InMemoryRepository()

    memory = make_memory(content="Original content.")
    repository.create(memory)

    updated = memory.model_copy(
        update={"content": "Updated content."}
    )

    result = repository.update(updated)

    assert result.content == "Updated content."
    assert repository.get(memory.id).content == "Updated content."


def test_update_missing_memory_is_rejected():
    repository = InMemoryRepository()
    memory = make_memory()

    with pytest.raises(KeyError, match="Memory not found"):
        repository.update(memory)


def test_archive_changes_status():
    repository = InMemoryRepository()
    memory = make_memory()

    repository.create(memory)

    archived = repository.archive(memory.id)

    assert archived.status == MemoryStatus.ARCHIVED
    assert repository.get(memory.id).status == MemoryStatus.ARCHIVED


def test_archive_missing_memory_is_rejected():
    repository = InMemoryRepository()

    with pytest.raises(KeyError, match="Memory not found"):
        repository.archive(uuid4())


def test_delete_removes_memory():
    repository = InMemoryRepository()
    memory = make_memory()

    repository.create(memory)
    repository.delete(memory.id)

    assert repository.get(memory.id) is None
    assert repository.list() == []


def test_delete_missing_memory_is_rejected():
    repository = InMemoryRepository()

    with pytest.raises(KeyError, match="Memory not found"):
        repository.delete(uuid4())


def test_get_returns_isolated_memory_copy():
    repository = InMemoryRepository()

    memory = make_memory(content="Original content.")
    repository.create(memory)

    retrieved = repository.get(memory.id)
    retrieved.content = "Accidental mutation."

    stored = repository.get(memory.id)

    assert stored.content == "Original content."


def test_create_does_not_expose_internal_state():
    repository = InMemoryRepository()

    memory = make_memory(content="Original content.")
    repository.create(memory)

    memory.content = "Changed outside repository."

    stored = repository.get(memory.id)

    assert stored.content == "Original content."


def test_update_replaces_repository_state_explicitly():
    repository = InMemoryRepository()

    memory = make_memory(content="Original content.")
    repository.create(memory)

    updated = memory.model_copy(
        update={"content": "Explicitly updated content."}
    )

    repository.update(updated)

    assert repository.get(memory.id).content == "Explicitly updated content."

---
# Retrieval Directory
---
src/nexus/retrieval/models.py
src/nexus/retrieval/scoring.py
src/nexus/retrieval/__init__.py
src/nexus/retrieval/__pycache__/scoring.cpython-313.pyc
src/nexus/retrieval/__pycache__/models.cpython-313.pyc
src/nexus/retrieval/__pycache__/engine.cpython-313.pyc
src/nexus/retrieval/__pycache__/__init__.cpython-313.pyc
src/nexus/retrieval/engine.py

---
# Retrieval Tests
---
tests/retrieval/test_engine.py
tests/retrieval/__pycache__/test_repository_engine.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_retrieval_models.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_ranking.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_engine_ranking.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_scoring.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_no_match.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_engine.cpython-313-pytest-9.1.1.pyc
tests/retrieval/__pycache__/test_models.cpython-313-pytest-9.1.1.pyc
tests/retrieval/test_scoring.py
tests/retrieval/test_repository_engine.py
tests/retrieval/test_ranking.py
tests/retrieval/test_retrieval_models.py
tests/retrieval/test_engine_ranking.py
tests/retrieval/test_no_match.py
