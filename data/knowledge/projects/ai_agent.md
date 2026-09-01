# Personal AI Agent — System Specifications

## Architecture Overview

The Personal AI Agent is a **local-first personal executive assistant** designed to operate primarily on local hardware with limited computational resources.

The system prioritizes privacy, deterministic processing, local inference, and controlled use of LLMs rather than sending personal data to external AI services.

## Hardware Target

* **RAM:** 16 GB
* **GPU:** Integrated Intel graphics / approximately 4 GB shared VRAM
* **Execution:** Local machine, including overnight/background processing
* **Primary constraint:** Efficient CPU/RAM usage and lightweight local models

## Core AI Stack

* **Local LLM Runtime:** Ollama
* **Primary Model:** Lightweight local LLM suitable for the available hardware
* **Embeddings:** `nomic-embed-text`
* **Architecture:** Hybrid deterministic + LLM processing

The model selection should remain configurable rather than being hard-coded to a single model, allowing smaller or better-performing models to be tested as the system evolves.

## Email Triage Pipeline

The email-processing system uses a **two-stage hybrid classification architecture**:

### Stage 1 — Deterministic Engine

Rules and scoring are applied before an LLM is invoked.

Examples of signals include:

* Marketing indicators
* `unsubscribe` links
* Promotional senders
* Newsletter headers
* Urgency indicators
* Financial/banking indicators
* Automated notification patterns

Strong deterministic signals can immediately classify an email without an LLM call, reducing latency and local compute usage.

### Stage 2 — LLM Fact Extraction

Emails that cannot be confidently classified by deterministic rules are passed to a local LLM.

The LLM extracts structured facts and contextual information used by the final classification layer.

## Knowledge & RAG

The Personal Knowledge subsystem provides local retrieval over personal documents.

Knowledge categories include:

* `university/`
* `career/`
* `projects/`
* `reference/`

The system uses embeddings and local retrieval to provide relevant context to the agent without requiring cloud-based knowledge storage.

## Knowledge Storage

Current persistent vector storage:

```text
data/knowledge/vector_store.json
```

The storage layer is intentionally simple and local-first, allowing the architecture to evolve toward a more specialized vector database if the dataset grows.

## Design Principles

1. **Local-first:** Keep personal information on the local machine whenever possible.
2. **Privacy by default:** Avoid unnecessary external API calls.
3. **Deterministic before probabilistic:** Use rules and scoring before invoking an LLM.
4. **Small models where possible:** Minimize resource consumption.
5. **Structured outputs:** Prefer machine-readable facts and classifications.
6. **Human control:** Sensitive actions should require explicit approval.
7. **Modular architecture:** Models, retrieval, classification, memory, and tools should remain independently replaceable.
8. **Observable decisions:** Important classifications and agent actions should be traceable and explainable.
