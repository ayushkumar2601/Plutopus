# ADR 0004: Why Ollama

## Context & Problem
Enterprises monitoring private core networks (SD-WAN/MPLS) cannot leak sensitive topology mappings, network alerts, or logs to external third-party cloud LLM APIs (e.g., OpenAI). The AI runtime must run locally and under air-gapped environments.

## Decision
Choose **Ollama** as the local LLM runtime container.

## Consequences
- **Security & Privacy**: Zero network data leaves the self-hosted environment.
- **Ease of Hosting**: Easily runs state-of-the-art open models (Llama 3, Qwen, Mistral) in a unified Docker interface.
- **Hardware Acceleration**: Automatic GPU/CPU orchestration.
