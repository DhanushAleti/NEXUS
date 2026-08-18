"""Retrieval engine contracts and repository-backed implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from nexus.memory.repository import MemoryRepository

from .models import RetrievalQuery, RetrievalResult
from .scoring import lexical_relevance_score


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
    """Retrieve, score, and rank memories from a memory repository."""

    def __init__(self, repository: MemoryRepository) -> None:
        self._repository = repository

    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        """Retrieve, score, rank, and limit relevant memories."""

        memories = self._repository.list(
            memory_type=query.memory_type,
            status=query.status,
            project_id=query.project_id,
        )

        results = [
            RetrievalResult(
                memory=memory,
                score=lexical_relevance_score(
                    query.text,
                    memory,
                ),
            )
            for memory in memories
        ]

        relevant = [
            result
            for result in results
            if result.score > 0.0
        ]

        ranked = sorted(
            relevant,
            key=lambda result: (-result.score, str(result.memory.id)),
        )

        return ranked[: query.limit]
