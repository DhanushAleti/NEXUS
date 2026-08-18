"""Retrieval engine contracts and repository-backed implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from nexus.memory.repository import MemoryRepository

from .models import RetrievalQuery, RetrievalResult


class RetrievalEngine(ABC):
    """Abstract contract for NEXUS retrieval implementations."""

    @abstractmethod
    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        """Retrieve memories relevant to the supplied query."""
        raise NotImplementedError


class RepositoryRetrievalEngine(RetrievalEngine):
    """Retrieve memory candidates from a memory repository.

    Repository filtering remains the responsibility of the memory repository.
    Relevance scoring and ranking are intentionally deferred to later layers.
    """

    def __init__(self, repository: MemoryRepository) -> None:
        self._repository = repository

    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        """Retrieve repository candidates matching query constraints."""

        memories = self._repository.list(
            memory_type=query.memory_type,
            status=query.status,
            project_id=query.project_id,
        )

        return [
            RetrievalResult(
                memory=memory,
                score=0.0,
            )
            for memory in memories[: query.limit]
        ]
