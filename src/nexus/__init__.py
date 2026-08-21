"""NEXUS — a persistent, provenance-aware personal AI operating system.

This top-level package re-exports the stable public API of the currently
implemented subsystems (memory and retrieval). See ``docs/ARCHITECTURE.md`` for
the full intended system and ``README.md`` for status and usage.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .memory import (
    InMemoryRelationRepository,
    InMemoryRepository,
    MemoryRecord,
    MemoryRelation,
    MemoryRelationRepository,
    MemoryRelationType,
    MemoryRepository,
    MemorySource,
    MemoryStatus,
    MemoryType,
    Project,
)
from .retrieval import (
    RepositoryRetrievalEngine,
    RetrievalEngine,
    RetrievalQuery,
    RetrievalResult,
)

try:
    __version__ = version("nexus-ai-os")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0"

__all__ = [
    "InMemoryRelationRepository",
    "InMemoryRepository",
    "MemoryRecord",
    "MemoryRelation",
    "MemoryRelationRepository",
    "MemoryRelationType",
    "MemoryRepository",
    "MemorySource",
    "MemoryStatus",
    "MemoryType",
    "Project",
    "RepositoryRetrievalEngine",
    "RetrievalEngine",
    "RetrievalQuery",
    "RetrievalResult",
    "__version__",
]
