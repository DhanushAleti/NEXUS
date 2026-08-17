# NEXUS — Project Thesis

## Working Title

NEXUS: A Persistent AI Operating System for Long-Horizon Human-AI Collaboration

## Thesis

Current AI assistants are primarily conversation-centric. They can answer individual
questions effectively, but they struggle to maintain an accurate, evolving understanding
of a user's projects, decisions, knowledge, files, tasks, and unfinished work across
long periods of time.

NEXUS investigates whether a persistent, structured, provenance-aware world model can
enable an AI system to reliably reconstruct the current state of a user's work and
continue long-horizon tasks with less irrelevant context and fewer hallucinations.

## Core Research Question

Can a persistent structured world model combining episodic memory, semantic knowledge,
project state, provenance, and context-aware retrieval outperform conversation history
and naive vector retrieval on long-horizon task continuation?

## Hypothesis

A persistent structured memory system with explicit project state, provenance,
temporal information, and context-aware retrieval will:

1. Improve project-state reconstruction accuracy.
2. Improve long-horizon task completion.
3. Reduce irrelevant retrieved context.
4. Reduce unsupported claims about previous work.
5. Improve token efficiency compared with naive context injection.

## Falsifiability

The hypothesis will be considered unsupported if NEXUS does not demonstrate measurable
improvements over predefined baselines across the selected evaluation tasks.

No post-hoc modification of evaluation criteria will be permitted without recording
the change and its justification.

## Core Principles

### 1. Provenance

Stored information should retain where it came from whenever practical.

### 2. Temporal Awareness

The system should distinguish between historical and current information.

### 3. Explicit Uncertainty

The system should not treat uncertain or inferred information as established fact.

### 4. Minimal Necessary Context

The context compiler should retrieve the smallest useful context rather than dumping
all available information into the model.

### 5. Reproducibility

Experiments should be repeatable from a clean environment.

### 6. Fail-Closed Behavior

When the system lacks sufficient evidence, it should prefer uncertainty over invention.

### 7. Measurable Progress

Every major architectural improvement should have an associated evaluation.

## Initial Benchmark

NEXUS will initially evaluate multi-session project continuation.

An artificial project will be introduced over multiple sessions. Each session will
contain decisions, implementation changes, constraints, discoveries, and unfinished
tasks.

At a later session, the system will be asked to reconstruct the current project state
and continue the work.

Performance will be compared against multiple baselines.

## Initial Baselines

- Baseline A: No persistent memory.
- Baseline B: Full conversation history.
- Baseline C: Naive vector retrieval.
- Baseline D: Structured memory without context compilation.
- NEXUS: Structured memory + project state + provenance + context compiler.

## Initial Metrics

- State reconstruction accuracy.
- Relevant-memory retrieval precision.
- Relevant-memory recall.
- Task completion rate.
- Unsupported-claim rate.
- Context token count.
- Long-horizon consistency.

## Non-Goals for V0

NEXUS is not initially intended to:

- autonomously control the user's entire computer;
- replace every productivity application;
- store unlimited personal information;
- claim perfect memory;
- operate without permission boundaries;
- optimize for maximum model autonomy.

The first goal is scientific validation of the core memory and context architecture.
