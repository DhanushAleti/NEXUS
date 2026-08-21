from uuid import UUID, uuid4

import pytest

from nexus.memory.relationship_repository import (
    InMemoryRelationRepository,
)
from nexus.memory.relationships import MemoryRelation, MemoryRelationType


def make_relation(
    relation_type: MemoryRelationType = MemoryRelationType.RELATED_TO,
    *,
    relation_id: UUID | None = None,
    source_memory_id: UUID | None = None,
    target_memory_id: UUID | None = None,
) -> MemoryRelation:
    """Create a valid MemoryRelation for repository tests."""
    source_id = source_memory_id or uuid4()
    target_id = target_memory_id or uuid4()

    if source_id == target_id:
        target_id = uuid4()

    return MemoryRelation(
        id=relation_id or uuid4(),
        relation_type=relation_type,
        source_memory_id=source_id,
        target_memory_id=target_id,
    )


def test_create_and_get_relationship():
    repository = InMemoryRelationRepository()
    relation = make_relation()

    created = repository.create(relation)
    retrieved = repository.get(relation.id)

    assert created == relation
    assert retrieved == relation


def test_duplicate_relationship_id_is_rejected():
    repository = InMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)

    with pytest.raises(
        ValueError,
        match="Relationship already exists",
    ):
        repository.create(relation)


def test_get_missing_relationship_returns_none():
    repository = InMemoryRelationRepository()

    assert repository.get(uuid4()) is None


def test_delete_removes_relationship():
    repository = InMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)
    repository.delete(relation.id)

    assert repository.get(relation.id) is None
    assert repository.list() == []


def test_delete_missing_relationship_is_rejected():
    repository = InMemoryRelationRepository()

    with pytest.raises(
        KeyError,
        match="Relationship not found",
    ):
        repository.delete(uuid4())


def test_create_does_not_expose_internal_state():
    repository = InMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)

    relation.metadata["outside_mutation"] = True

    stored = repository.get(relation.id)

    assert stored is not None
    assert stored.metadata == {}


def test_get_returns_isolated_relationship_copy():
    repository = InMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)

    retrieved = repository.get(relation.id)

    assert retrieved is not None

    retrieved.metadata["mutated"] = True

    stored = repository.get(relation.id)

    assert stored is not None
    assert stored.metadata == {}


def test_list_returns_isolated_relationship_copies():
    repository = InMemoryRelationRepository()
    relation = make_relation()

    repository.create(relation)

    result = repository.list()

    assert len(result) == 1

    result[0].metadata["mutated"] = True

    stored = repository.get(relation.id)

    assert stored is not None
    assert stored.metadata == {}


def test_list_preserves_insertion_order():
    repository = InMemoryRelationRepository()

    first = make_relation()
    second = make_relation()
    third = make_relation()

    repository.create(first)
    repository.create(second)
    repository.create(third)

    result = repository.list()

    assert [relation.id for relation in result] == [
        first.id,
        second.id,
        third.id,
    ]


def test_list_filters_by_relation_type():
    repository = InMemoryRelationRepository()

    related = make_relation(
        MemoryRelationType.RELATED_TO,
    )
    supports = make_relation(
        MemoryRelationType.SUPPORTS,
    )
    contradicts = make_relation(
        MemoryRelationType.CONTRADICTS,
    )

    repository.create(related)
    repository.create(supports)
    repository.create(contradicts)

    result = repository.list(
        relation_type=MemoryRelationType.SUPPORTS,
    )

    assert result == [supports]


def test_list_filters_by_source_memory_id():
    repository = InMemoryRelationRepository()

    source_id = uuid4()

    matching = make_relation(
        source_memory_id=source_id,
    )
    non_matching = make_relation()

    repository.create(matching)
    repository.create(non_matching)

    result = repository.list(
        source_memory_id=source_id,
    )

    assert result == [matching]


def test_list_filters_by_target_memory_id():
    repository = InMemoryRelationRepository()

    target_id = uuid4()

    matching = make_relation(
        target_memory_id=target_id,
    )
    non_matching = make_relation()

    repository.create(matching)
    repository.create(non_matching)

    result = repository.list(
        target_memory_id=target_id,
    )

    assert result == [matching]


def test_list_combines_filters_with_and_semantics():
    repository = InMemoryRelationRepository()

    source_id = uuid4()
    target_id = uuid4()

    matching = make_relation(
        MemoryRelationType.SUPPORTS,
        source_memory_id=source_id,
        target_memory_id=target_id,
    )

    wrong_type = make_relation(
        MemoryRelationType.RELATED_TO,
        source_memory_id=source_id,
        target_memory_id=target_id,
    )

    wrong_source = make_relation(
        MemoryRelationType.SUPPORTS,
        source_memory_id=uuid4(),
        target_memory_id=target_id,
    )

    wrong_target = make_relation(
        MemoryRelationType.SUPPORTS,
        source_memory_id=source_id,
        target_memory_id=uuid4(),
    )

    repository.create(matching)
    repository.create(wrong_type)
    repository.create(wrong_source)
    repository.create(wrong_target)

    result = repository.list(
        relation_type=MemoryRelationType.SUPPORTS,
        source_memory_id=source_id,
        target_memory_id=target_id,
    )

    assert result == [matching]
