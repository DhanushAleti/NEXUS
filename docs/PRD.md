# NEXUS — Product Requirements Document

## 1. Product Vision

NEXUS is a personal AI infrastructure system that maintains an evolving representation
of a user's digital work environment.

It should allow an AI agent to answer:

> "What is happening with this project, what happened previously, and what should
> happen next?"

without requiring the user to manually reconstruct the context.

## 2. Primary User

The initial target user is a technically sophisticated individual working across
multiple long-running projects, repositories, documents, experiments, and research
tasks.

## 3. Primary Problem

Users repeatedly lose context between AI sessions.

The information may exist somewhere in:

- conversations;
- files;
- repositories;
- notes;
- experiment results;
- project documents;
- decisions;
- task lists.

The problem is not merely information storage.

The problem is reconstructing the correct current state from distributed information.

## 4. Core Jobs To Be Done

### Job 1 — Resume Work

"Continue the project from where I left off."

### Job 2 — Understand State

"What is the current state of this project?"

### Job 3 — Recover Decisions

"Why did we choose this architecture?"

### Job 4 — Find Relevant Context

"What information do I actually need to solve this problem?"

### Job 5 — Identify Next Action

"What is the highest-value next step?"

## 5. V1 Capabilities

### Memory

- Create memory records.
- Store timestamps.
- Store provenance.
- Store memory type.
- Store confidence.
- Retrieve memories.

### Project State

- Projects.
- Goals.
- Tasks.
- Decisions.
- Components.
- Dependencies.
- Status.

### Retrieval

- Semantic retrieval.
- Metadata filtering.
- Temporal filtering.
- Project filtering.
- Relevance ranking.

### Context Compilation

Given a task, construct a compact context package containing:

- relevant project state;
- relevant memories;
- relevant decisions;
- relevant artifacts;
- unresolved tasks.

### Evaluation

Run controlled benchmark tasks against defined baselines.

## 6. V1 Non-Goals

The first version will not attempt:

- unrestricted autonomous computer control;
- complete email automation;
- complete browser automation;
- generalized AGI behavior;
- automatic storage of every user interaction;
- perfect semantic understanding.

## 7. Product Principle

NEXUS should optimize for:

> Correct context, not maximum context.

## 8. Trust Model

The system should distinguish:

- observed facts;
- imported facts;
- user-provided facts;
- model-generated inferences;
- uncertain information.

AI-generated inferences should not silently become facts.

## 9. V1 Success Condition

V1 is successful when the system can reliably reconstruct a synthetic multi-session
project and demonstrate measurable improvement over the predefined baselines.
