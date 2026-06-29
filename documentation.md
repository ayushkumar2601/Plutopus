# Plutopus Master Project Documentation

This document serves as the single source of truth for the current state, active phase, features implemented, and developer notes for the Plutopus platform.

---

## Current Project Phase
- **Phase 6: Air-Gap Readiness, Security Hardening & Platform Scale (Completed)**
- **Progress Percentage**: 100%

---

## Current System State

### What is Working
- **Shared Schemas**: Pydantic schemas (`HealthResponse`, `ApiResponse`, `ErrorResponse`) created under `packages/schemas`.
- **FastAPI API**: App structure bootstrapped in `apps/api` with Swagger docs enabled. Fully supports predictions, copilot, audit logs, and `/api/v1/incidents` controllers with JWT/RBAC role checks.
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
- **Test Suite**: Automated tests verifying all normalizations, APIs, predictions, Copilot dialogues, correlation pipelines, and audit logs. Achieved **90.0% average coverage** for Phase 6 modules.

---

## Log of Changes

### Phase 6 Implementation (2026-06-29)
1. Created `AuditLog` database model to store immutable operation logs.
2. Built `distribution/pack-offline-bundle.sh` assembling images, charts, and configurations.
3. Created `scripts/airgap/verify.sh` verifying isolated environments and generating `airgap-report.md`.
4. Implemented `export-model.sh` and `import-model.sh` model packaging scripts.
5. Added rotation secrets ring decoding loop and cookie session authorization checks in `auth.py`.
6. Enforced minimum 32-character secret length checks in auth layer.
7. Structured Kubernetes default-deny and internal-allow network policies in `infrastructure/k8s/network-policies/`.
8. Created capacity planning docs, operational guidelines, disaster recovery runbooks, database upgrade/rollback scripts, backup validation automation, and compliance reports.
