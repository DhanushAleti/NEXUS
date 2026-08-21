# NEXUS

**A persistent, provenance-aware personal AI operating system.**

NEXUS is a research project investigating whether a persistent, structured,
provenance-aware world model lets an AI system reliably reconstruct the current
state of a user's work and continue long-horizon tasks with less irrelevant
context and fewer unsupported claims than conversation history or naive vector
retrieval.

See [`docs/THESIS.md`](docs/THESIS.md) for the research question and
[`docs/PRD.md`](docs/PRD.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), and
[`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) for the product, architecture, and
evaluation plan.

## Implementation status

The full architecture (`docs/ARCHITECTURE.md`) spans six subsystems: ingestion,
memory, project state, retrieval, a context compiler, and an agent runtime. This
repository currently implements the **foundation layers** that the rest of the
system builds on:

| Subsystem            | Status         | Module |
|----------------------|----------------|--------|
| Memory records       | Implemented    | `nexus.memory.models` |
| Memory repository    | Implemented    | `nexus.memory.repository` |
| Relationships        | Implemented    | `nexus.memory.relationships` |
| Relationship repo    | Implemented    | `nexus.memory.relationship_repository` |
| Retrieval            | Implemented (lexical) | `nexus.retrieval` |
| Ingestion            | Planned (placeholder package) | `nexus.ingestion` |
| Context compiler     | Planned (placeholder package) | `nexus.context` |
| Project state / agents | Not started | — |

Everything present is fully typed (`mypy --strict` clean) and covered by tests.
The placeholder packages are intentional reservations for deferred research
work, not partially-built code.

## Domain model

A **`MemoryRecord`** is the canonical unit of stored information. It carries:

- `id` (UUID, auto-generated) — identity; equality is by field value.
- `memory_type` — one of `event`, `fact`, `decision`, `task`, `goal`, `artifact`.
- `content` — non-blank text (leading/trailing whitespace is stripped).
- `source` / `source_ref` — provenance (`user`, `file`, `git`, `web`, `tool`,
  `agent`, `system`, `inferred`).
- `confidence` — float in `[0.0, 1.0]` (default `1.0`).
- `status` — lifecycle: `active`, `superseded`, `archived`, `disputed`.
- `created_at`, `observed_at`, `valid_from`, `valid_until` — timestamps.
- `project_id`, `supersedes`, `tags`, `metadata` — association and extension.

Invariants enforced at construction (and on assignment):

- Content must not be blank; it is normalized (stripped).
- All datetimes must be **timezone-aware** (naive datetimes are rejected).
- `valid_until` must not be earlier than `valid_from` (equal bounds allowed,
  modelling a point in time; open-ended intervals allowed).
- Tags are lowercased, trimmed, de-duplicated, and order-preserving.
- Unknown fields are rejected (`extra="forbid"`).

A **`MemoryRelation`** is a directed edge between two memory records with a
`relation_type` (`related_to`, `derived_from`, `contradicts`, `supports`,
`references`). Source and target must differ (no self-relations); `created_at`
must be timezone-aware; `confidence` is in `[0.0, 1.0]`.

## Repository semantics

Both `InMemoryRepository` (records) and `InMemoryRelationRepository` (relations)
share the same contract:

- **Duplicate ids** on `create` raise `ValueError`.
- **Missing ids** on `get` return `None`; on `update`/`archive`/`delete` raise
  `KeyError`.
- **`list(...)`** applies its filters with **AND** semantics and returns results
  in **insertion order** — deterministic and reproducible.
- **Mutation isolation**: records/relations are stored and returned as deep
  copies, including nested `tags`/`metadata`. Mutating an object you passed in,
  or one you got back, never changes repository state.
- Relations are identified **only by id**: two relations with the same source,
  target, and type but different ids are distinct (logical duplicates allowed).

The abstract base classes `MemoryRepository` and `MemoryRelationRepository`
define these contracts so alternative backends can be added without changing
callers.

## Retrieval semantics

`RepositoryRetrievalEngine.retrieve(query)` takes a validated `RetrievalQuery`
and returns a list of `RetrievalResult` (`memory` + `score`). The pipeline is:

1. **Candidate generation** — `repository.list(...)` applies the query's
   metadata filters (`memory_type`, `status`, `project_id`).
2. **Scoring** — each candidate gets a **lexical relevance score**: the fraction
   of the query's unique tokens that appear in the memory content
   (case-insensitive, `[A-Za-z0-9_]` tokens). Range `[0.0, 1.0]`.
3. **No-match filtering** — candidates scoring `0.0` are dropped
   (fail-closed: no lexical evidence ⇒ not returned).
4. **Ranking** — descending score, ties broken by ascending stringified UUID.
   The ordering is therefore **deterministic**: identical queries against
   identical state always return the same order.
5. **Limit** — the top `limit` results are returned (`limit` defaults to 10 and
   must be `> 0`). Ranking happens **before** the limit is applied.

`RetrievalQuery.text` must be non-blank. An empty repository, a query with no
matches, or an over-constrained filter all return `[]` rather than raising.

## Public API

```python
from nexus import (
    MemoryRecord, MemoryType, MemorySource, MemoryStatus, Project,
    MemoryRepository, InMemoryRepository,
    MemoryRelation, MemoryRelationType,
    MemoryRelationRepository, InMemoryRelationRepository,
    RetrievalQuery, RetrievalResult, RetrievalEngine, RepositoryRetrievalEngine,
)

repo = InMemoryRepository()
repo.create(MemoryRecord(
    memory_type=MemoryType.FACT,
    content="NEXUS stores memories in PostgreSQL.",
    source=MemorySource.USER,
))

engine = RepositoryRetrievalEngine(repo)
results = engine.retrieve(RetrievalQuery(text="PostgreSQL"))
for result in results:
    print(result.score, result.memory.content)
```

## Setup & development

Requires Python ≥ 3.11.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Validate:

```bash
pytest -q          # test suite
mypy               # strict type check of the package (config in pyproject.toml)
ruff check .       # lint
```

## Limitations (current implementation)

- **Retrieval is lexical, not semantic.** Scoring is token-overlap only; there
  are no embeddings or vector search. Tokenization is ASCII-oriented
  (`[A-Za-z0-9_]`), so non-ASCII words are only partially matched.
- **Retrieval has no temporal filtering yet.** `MemoryRecord` models temporal
  validity (`valid_from`/`valid_until` with boundary semantics), but
  `RetrievalQuery` filters on metadata only. Temporal retrieval is planned
  (PRD §5) and deliberately not implemented to avoid inventing unspecified
  point-in-time / interval-overlap semantics.
- **No cross-repository referential integrity.** A relation may reference memory
  ids that do not exist in a `MemoryRepository`; endpoint existence is the
  caller's responsibility (see `docs/ARCHITECTURE.md`).
- **Storage is in-memory only.** Persistence backends, ingestion, the context
  compiler, project state, and the agent runtime are not yet implemented.

## License

MIT.
