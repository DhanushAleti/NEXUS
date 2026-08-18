from __future__ import annotations

from abc import ABC, abstractmethod

from .models import RetrievalQuery, RetrievalResult


class RetrievalEngine(ABC):
    """Abstract contract for NEXUS retrieval implementations."""

    @abstractmethod
    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        """Retrieve memories relevant to the supplied query."""
