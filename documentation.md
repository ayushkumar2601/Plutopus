# Plutopus Master Project Documentation

This document serves as the single source of truth for the current state, active phase, features implemented, and developer notes for the Plutopus platform.

---

## Current Project Phase
- **Phase 5: Workflow Automation & Production Readiness (Completed)**
- **Progress Percentage**: 100%

---

## Current System State

### What is Working
- **Shared Schemas**: Pydantic schemas (`HealthResponse`, `ApiResponse`, `ErrorResponse`) created under `packages/schemas`.
- **FastAPI API**: App structure bootstrapped in `apps/api` with Swagger docs enabled. Fully supports predictions, copilot, and `/api/v1/incidents` controllers with JWT/RBAC role checks.
- **Next.js Dashboard**: Dynamic pages at `/dashboard/predictions`, `/dashboard/copilot`, and `/dashboard/incidents` (featuring root-cause candidates, priority scores, playbooks, and export triggers).
- **Typer CLI**: Bootstrapped CLI in `apps/cli` with support for `plutopus health` commands.
- **Docker Stack**: Multi-container stack configured in `docker-compose.yml` linking API, Dashboard, PostgreSQL (TimescaleDB), Qdrant, Redpanda, Ollama, Prometheus, Grafana, `prediction-worker`, and `copilot-worker`.
- **Telemetry Worker**: Consumes raw data from `metrics_raw` and `events_raw` topics, normalizes the data, and inserts it into PostgreSQL/TimescaleDB.
- **Prediction Worker**: A scheduled background worker in `services/prediction/src/worker.py` running linear forecasts, Z-score anomalies, and 0-100 site/tunnel risk indexes.
- **Copilot Services (`services/copilot/`)**: Integrates with local Ollama using prompts and matches troubleshooting runbooks.
- **Event Correlation & Prioritization**: Topology-aware correlation engine aggregating spoke anomalies into root-cause incident records. Computes priority index (0-100) based on node impact, criticality, and lead time.
- **Integrations & Webhooks**: Supports outbound JSON dispatch webhooks with exponential backoff retries.
- **Backup & Recovery**: Scripts at `scripts/backup.sh` and `scripts/restore.sh` automating TimescaleDB snapshots.
- **Kubernetes Helm Charts**: Charts versioned under `infrastructure/helm/` supporting single-command deployments.
- **Observability Metrics**: Prometheus endpoint at `/metrics` exporting API performance statistics.
- **Test Suite**: Automated tests verifying all normalizations, APIs, predictions, Copilot dialogues, and correlation pipelines. Achieved **94.1% average coverage** for Phase 5 modules.

---

## Log of Changes

### Phase 5 Implementation (2026-06-29)
1. Created first-class `Incident` database model and added business criticality fields.
2. Built `services/correlation/` engine grouping overlapping spoke alerts using topology NetworkX dependencies.
3. Implemented prioritizations weighting risk, node impact, and business criticalities.
4. Built outbound webhook retry delivery pipeline with exponential backoff.
5. Implemented HS256 JWT auth token signatures and role check guards (`admin`, `operator`, `viewer`).
6. Exposed endpoint: `/metrics` using `prometheus_client` exporter.
7. Registered Grafana system health layout configurations.
8. Created `backup.sh` and `restore.sh` database utilities.
9. Structured `infrastructure/helm/` charts.
10. Added 15+ integration tests achieving 94.1% coverage for Phase 5 files.
11. Synchronized all commits to main.
