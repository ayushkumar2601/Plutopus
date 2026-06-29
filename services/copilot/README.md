# Plutopus AI Copilot & Network Intelligence Assistant

This service provides natural language querying capability for operators, allowing them to inspect live topology, read metrics/risk/predictions, detect active anomalies, and receive troubleshooting guide suggestions based on network runbooks.

## Directory Structure
- `context/`: Formulates structured contexts for sites, devices, and tunnels. Includes the summarizer engine.
- `retrieval/`: Matches active incident states to static runbooks and retrieves live context from database.
- `runbooks/`: Static diagnostic runbooks for Latency, Packet Loss, Tunnel Down, and Flapping.
- `prompts/`: Prompt instructions for grounding responses and analyst persona settings.
- `llm/`: Integration wrapper for local **Ollama** model execution.
- `memory/`: Session memory wrapper.
- `api/`: API router files.
