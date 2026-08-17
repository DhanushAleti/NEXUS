# NEXUS — Architecture

## System Overview

NEXUS is composed of six primary subsystems:

1. Ingestion
2. Memory
3. Knowledge / Project State
4. Retrieval
5. Context Compiler
6. Agent Runtime

## High-Level Flow

User / Artifact
      |
      v
  Ingestion
      |
      v
 Normalization
      |
      +----------------+
      |                |
      v                v
 Structured Memory   Artifacts
      |
      v
 Project State
      |
      v
 Retrieval
      |
      v
 Context Compiler
      |
      v
 Agent / LLM
      |
      v
 Result / Action
      |
      v
 Evaluation + Feedback
      |
      v
 Memory Update

## 1. Ingestion Layer

Responsible for converting external information into normalized internal records.

Potential inputs:

- Markdown
- text
- source code
- Git history
- structured project metadata
- future connectors

The ingestion layer should preserve provenance.

## 2. Memory Layer

Memory is divided conceptually into:

### Episodic Memory

Records of events and experiences.

Examples:

- completed experiment;
- failed build;
- architectural decision;
- meeting;
- task completion.

### Semantic Memory

Generalized knowledge.

Examples:

- project constraints;
- technical definitions;
- known relationships;
- stable facts.

### Procedural Memory

Knowledge about how to perform recurring actions.

Examples:

- deployment process;
- development workflow;
- testing procedure.

## 3. Project State

Project state represents the current structured state of a project.

Example entities:

- Project
- Goal
- Task
- Decision
- Component
- Dependency
- Milestone
- Artifact

The state model must support temporal changes.

## 4. Retrieval

Retrieval should combine multiple signals.

Potential signals:

- semantic similarity;
- project relevance;
- temporal relevance;
- entity relationships;
- explicit metadata;
- source reliability.

The initial implementation should remain simple enough to evaluate.

## 5. Context Compiler

The Context Compiler transforms a user request into a bounded context package.

Input:

- user query;
- active project;
- current state.

Output:

- relevant memories;
- relevant decisions;
- project state;
- relevant artifacts;
- uncertainty;
- provenance.

The Context Compiler should enforce a context budget.

## 6. Agent Runtime

The agent runtime will eventually execute controlled actions.

Initial agents:

- Research Agent
- Coding Agent
- Planning Agent

Agents should operate through explicit tools and permission boundaries.

## 7. Feedback

Agent results can produce new information.

However, model-generated output must not automatically become trusted memory.

Memory writes should have provenance and confidence metadata.

## Architectural Principle

NEXUS should be designed around explicit state and evidence rather than relying
entirely on model context windows.
