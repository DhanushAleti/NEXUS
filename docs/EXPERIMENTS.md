# NEXUS — Experimental Protocol

## Objective

Determine whether persistent structured memory and context compilation improve
long-horizon project continuation.

## Experimental Setup

Create synthetic multi-session projects.

Each project should contain:

- project objective;
- architecture;
- decisions;
- constraints;
- implementation progress;
- failures;
- completed tasks;
- unfinished tasks;
- irrelevant information;
- contradictory historical information where appropriate.

## Session Structure

Each project will be distributed across multiple sessions.

Example:

### Session 1

Project creation and initial architecture.

### Session 2

Implementation of component A.

### Session 3

Failure discovered in component B.

### Session 4

Architecture decision changed.

### Session 5

New task requiring knowledge from previous sessions.

### Session 6

Continuation request.

## Evaluation Prompt

The system receives a continuation task without being given the complete history.

It must:

1. Identify the current project state.
2. Identify relevant previous decisions.
3. Identify unfinished work.
4. Identify relevant constraints.
5. Propose the next action.
6. Avoid unsupported claims.

## Baselines

### A — No Persistent Memory

Only the immediate prompt is provided.

### B — Conversation History

The available conversation history is provided directly.

### C — Naive RAG

Documents are embedded and retrieved using similarity search.

### D — Structured Memory

Structured records are retrieved without the Context Compiler.

### E — NEXUS

Structured memory + project state + provenance + context compilation.

## Metrics

### State Reconstruction Accuracy

Percentage of required project-state facts correctly recovered.

### Retrieval Precision

Relevant retrieved items divided by all retrieved items.

### Retrieval Recall

Relevant retrieved items recovered divided by all relevant items.

### Unsupported Claim Rate

Number of claims not supported by available evidence divided by total factual claims.

### Task Completion Rate

Percentage of continuation tasks completed correctly.

### Context Efficiency

Useful information obtained per context token.

### Long-Horizon Consistency

Consistency of project understanding as session count increases.

## Evaluation Rules

Evaluation criteria must be defined before final comparison.

Changing metrics after observing results requires recording the change and its reason.

All benchmark datasets and experiment configurations should be version controlled.

Results should include failures, not only successful runs.
