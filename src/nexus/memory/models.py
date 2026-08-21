"""Core NEXUS domain models: memory records, their enums, and projects."""

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
