from uuid import uuid4

import pytest

from nexus.memory import (
    InMemoryRepository,
    MemoryRecord,
    MemorySource,
    MemoryStatus,
    MemoryType,
)


def make_memory(
    memory_type: MemoryType = MemoryType.FACT,
    *,
    project_id=None,
    content: str = "Test memory.",
) -> MemoryRecord:
    return MemoryRecord(
        memory_type=memory_type,
        content=content,
        source=MemorySource.USER,
        project_id=project_id,
    )


def test_create_and_get_memory():
    repository = InMemoryRepository()
    memory = make_memory()

    created = repository.create(memory)

    assert created == memory
    assert repository.get(memory.id) == memory


def test_get_missing_memory_returns_none():
    repository = InMemoryRepository()

    assert repository.get(uuid4()) is None


def test_create_duplicate_memory_is_rejected():
    repository = InMemoryRepository()
    memory = make_memory()

    repository.create(memory)

    with pytest.raises(ValueError, match="already exists"):
        repository.create(memory)


def test_list_returns_all_memories():
    repository = InMemoryRepository()

    first = make_memory(content="First memory.")
    second = make_memory(content="Second memory.")

    repository.create(first)
    repository.create(second)

    memories = repository.list()

    assert memories == [first, second]


def test_list_filters_by_memory_type():
    repository = InMemoryRepository()

    fact = make_memory(MemoryType.FACT)
    decision = make_memory(MemoryType.DECISION)

    repository.create(fact)
    repository.create(decision)

    memories = repository.list(memory_type=MemoryType.DECISION)

    assert memories == [decision]


def test_list_filters_by_status():
    repository = InMemoryRepository()

    active = make_memory()
    archived = make_memory()

    repository.create(active)
    repository.create(archived)

    repository.archive(archived.id)

    assert repository.list(status=MemoryStatus.ACTIVE) == [active]

    archived_result = repository.list(status=MemoryStatus.ARCHIVED)

    assert len(archived_result) == 1
    assert archived_result[0].id == archived.id
    assert archived_result[0].status == MemoryStatus.ARCHIVED


def test_list_filters_by_project():
    repository = InMemoryRepository()

    project_a = uuid4()
    project_b = uuid4()

    memory_a = make_memory(project_id=project_a)
    memory_b = make_memory(project_id=project_b)

    repository.create(memory_a)
    repository.create(memory_b)

    assert repository.list(project_id=project_a) == [memory_a]
    assert repository.list(project_id=project_b) == [memory_b]


def test_list_combines_filters():
    repository = InMemoryRepository()

    project_id = uuid4()

    matching = make_memory(
        MemoryType.DECISION,
        project_id=project_id,
        content="Matching memory.",
    )

    wrong_type = make_memory(
        MemoryType.FACT,
        project_id=project_id,
    )

    wrong_project = make_memory(
        MemoryType.DECISION,
        project_id=uuid4(),
    )

    repository.create(matching)
    repository.create(wrong_type)
    repository.create(wrong_project)

    result = repository.list(
        memory_type=MemoryType.DECISION,
        project_id=project_id,
    )

    assert result == [matching]


def test_update_replaces_existing_memory():
    repository = InMemoryRepository()

    memory = make_memory(content="Original content.")
    repository.create(memory)

    updated = memory.model_copy(
        update={"content": "Updated content."}
    )

    result = repository.update(updated)

    assert result.content == "Updated content."
    assert repository.get(memory.id).content == "Updated content."


def test_update_missing_memory_is_rejected():
    repository = InMemoryRepository()
    memory = make_memory()

    with pytest.raises(KeyError, match="Memory not found"):
        repository.update(memory)


def test_archive_changes_status():
    repository = InMemoryRepository()
    memory = make_memory()

    repository.create(memory)

    archived = repository.archive(memory.id)

    assert archived.status == MemoryStatus.ARCHIVED
    assert repository.get(memory.id).status == MemoryStatus.ARCHIVED


def test_archive_missing_memory_is_rejected():
    repository = InMemoryRepository()

    with pytest.raises(KeyError, match="Memory not found"):
        repository.archive(uuid4())


def test_delete_removes_memory():
    repository = InMemoryRepository()
    memory = make_memory()

    repository.create(memory)
    repository.delete(memory.id)

    assert repository.get(memory.id) is None
    assert repository.list() == []


def test_delete_missing_memory_is_rejected():
    repository = InMemoryRepository()

    with pytest.raises(KeyError, match="Memory not found"):
        repository.delete(uuid4())


def test_get_returns_isolated_memory_copy():
    repository = InMemoryRepository()

    memory = make_memory(content="Original content.")
    repository.create(memory)

    retrieved = repository.get(memory.id)
    retrieved.content = "Accidental mutation."

    stored = repository.get(memory.id)

    assert stored.content == "Original content."


def test_create_does_not_expose_internal_state():
    repository = InMemoryRepository()

    memory = make_memory(content="Original content.")
    repository.create(memory)

    memory.content = "Changed outside repository."

    stored = repository.get(memory.id)

    assert stored.content == "Original content."


def test_update_replaces_repository_state_explicitly():
    repository = InMemoryRepository()

    memory = make_memory(content="Original content.")
    repository.create(memory)

    updated = memory.model_copy(
        update={"content": "Explicitly updated content."}
    )

    repository.update(updated)

    assert repository.get(memory.id).content == "Explicitly updated content."
