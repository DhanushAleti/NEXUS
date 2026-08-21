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


class InMemoryRelationRepository(MemoryRelationRepository):
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
