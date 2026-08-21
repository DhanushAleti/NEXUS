"""Directed relationship model connecting two NEXUS memory records."""

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
