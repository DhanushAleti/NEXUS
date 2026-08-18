"""Pydantic models for the retrieval domain."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from nexus.memory import MemoryRecord, MemoryStatus, MemoryType


class RetrievalQuery(BaseModel):
    """A validated query submitted to the retrieval layer."""

    model_config = ConfigDict(extra="forbid")

    text: str
    project_id: UUID | None = None
    memory_type: MemoryType | None = None
    status: MemoryStatus | None = None
    limit: int = Field(default=10, gt=0)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Retrieval query text cannot be blank")

        return value


class RetrievalResult(BaseModel):
    """A memory returned by retrieval together with its relevance score."""

    model_config = ConfigDict(extra="forbid")

    memory: MemoryRecord
    score: float
