# Plutopus Master Project Documentation

This document serves as the single source of truth for the current state, active phase, features implemented, and developer notes for the Plutopus platform.

---

## Current Project Phase
- **Phase 4: AI Copilot & Network Intelligence Assistant (Completed)**
- **Progress Percentage**: 100%

---

## Current System State

### What is Working
- **Shared Schemas**: Pydantic schemas (`HealthResponse`, `ApiResponse`, `ErrorResponse`) created under `packages/schemas`.
- **FastAPI API**: App structure bootstrapped in `apps/api` with Swagger docs enabled. Fully supports `/api/v1/predictions` and `/api/v1/copilot` endpoints.
- **Next.js Dashboard**: Dynamic pages at `/dashboard/predictions` and `/dashboard/copilot` (featuring conversation streams, suggested question tags, active incident summaries, and references).
- **Typer CLI**: Bootstrapped CLI in `apps/cli` with support for `plutopus health` commands.
- **Docker Stack**: Multi-container stack configured in `docker-compose.yml` linking API, Dashboard, PostgreSQL (TimescaleDB), Qdrant, Redpanda, Ollama, and `copilot-worker`.
- **Telemetry Worker**: Consumes raw data from `metrics_raw` and `events_raw` topics, normalizes the data, and inserts it into PostgreSQL/TimescaleDB.
- **Prediction Worker**: A scheduled background worker in `services/prediction/src/worker.py` running linear forecasts, Z-score anomalies, and 0-100 site/tunnel risk indexes.
- **Copilot Services (`services/copilot/`)**: Integrates with local **Ollama** using prompt templates, matches telemetry to troubleshooting markdown runbooks, holds session history, and executes deterministic fallbacks if offline.
- **Mock Streamer**: Simulated telemetry data generator in `scripts/generate-demo-telemetry.py`.
- **Test Suite**: Automated tests verifying normalizations, APIs, predictions, and Copilot context retrievals. Achieved **93.0% average coverage** for Copilot modules.

### What is Not Working / Not Implemented Yet
- **Phase 5 Features**: Advanced predictive tuning, ticketing system integrations (reserved for subsequent sprints).

---

## Log of Changes

### Phase 4 Implementation (2026-06-29)
1. Created `services/copilot/` directory structuring `context/`, `retrieval/`, `runbooks/`, `prompts/`, `llm/`, and `memory/`.
2. Seeded 6 troubleshooting markdown runbooks for high latency, packet loss, tunnel failure, congestion, interface flapping, and route instability.
3. Implemented `CopilotContextEngine` to extract site/tunnel context structures.
4. Implemented `CopilotIncidentSummarizer` translating database metrics to plain English summaries.
5. Built Ollama integrations with custom JSON payloads and configured fallback mechanisms.
6. Exposed endpoints: `/api/v1/copilot/chat`, `/api/v1/copilot/explain`, and `/api/v1/copilot/incident-summary`.
7. Created the Next.js Copilot dashboard at `/dashboard/copilot` featuring live query tags, recent incident cards, and source citations.
8. Added `copilot-worker` service to the Docker stack.
9. Added tests verifying copilot modules (achieved 93.0% coverage).
10. Synchronized all commits to main.
