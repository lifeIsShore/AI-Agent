# Personal AI Agent — System Specifications

## Architecture Overview
The Personal AI Agent is a local-first executive assistant designed for low resource footprint (16GB RAM CPU).
- **Core Brain:** Qwen 2.5 1.5B (Local via Ollama)
- **Embeddings:** nomic-embed-text
- **Triage Pipeline:** Two-stage hybrid engine (Deterministic Rules + Fact Extraction LLM)
- **Knowledge Storage:** JSON-backed persistent vector store (`data/knowledge/vector_store.json`)
