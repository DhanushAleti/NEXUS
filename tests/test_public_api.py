"""Pin the intentional public API surface of the nexus package.

Regression guard for previously-missing exports: the abstract repositories and
the relation repository were reachable only via deep module paths, and the
top-level package exported nothing.
"""

import nexus


def test_top_level_exports_are_importable() -> None:
    from nexus import (
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
        RepositoryRetrievalEngine,
        RetrievalEngine,
        RetrievalQuery,
        RetrievalResult,
    )

    # Reference each so linters treat the imports as used.
    assert all(
        symbol is not None
        for symbol in (
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
            RepositoryRetrievalEngine,
            RetrievalEngine,
            RetrievalQuery,
            RetrievalResult,
        )
    )


def test_memory_package_exports_repositories() -> None:
    # Previously these were importable only via deep module paths.
    from nexus.memory import (
        InMemoryRelationRepository,
        MemoryRelationRepository,
        MemoryRepository,
    )

    assert issubclass(InMemoryRelationRepository, MemoryRelationRepository)
    assert MemoryRepository is not None


def test_all_is_defined_and_sorted() -> None:
    assert "__version__" in nexus.__all__
    exported = [name for name in nexus.__all__ if not name.startswith("_")]
    assert exported == sorted(exported)

    for name in nexus.__all__:
        assert hasattr(nexus, name), f"nexus.__all__ lists missing attr: {name}"


def test_version_is_a_nonempty_string() -> None:
    assert isinstance(nexus.__version__, str)
    assert nexus.__version__
