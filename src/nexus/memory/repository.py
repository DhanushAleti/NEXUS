"""Storage contracts and in-memory implementation for memory records."""

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
        """Return copies of memories matching the filters, in insertion order."""

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
    """In-memory repository with explicit mutation boundaries.

    Records are stored and returned as deep copies, so neither the record
    passed to ``create``/``update`` nor any record returned by ``get``/``list``
    shares mutable state with repository internals. ``list`` preserves insertion
    order, giving deterministic, reproducible results.
    """

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
