# Plutopus Master Project Documentation

This document serves as the single source of truth for the current state, active phase, features implemented, and developer notes for the Plutopus platform.

---

## Current Project Phase
- **Phase 3: Predictive Analytics Engine (Completed)**
- **Progress Percentage**: 100%

---

## Current System State

### What is Working
- **Shared Schemas**: Pydantic schemas (`HealthResponse`, `ApiResponse`, `ErrorResponse`) created under `packages/schemas`.
- **FastAPI API**: App structure bootstrapped in `apps/api` with Swagger docs enabled. Fully supports `/api/v1/predictions` (metric forecasts), `/api/v1/predictions/sites` (site risk scores), `/api/v1/predictions/tunnels` (tunnel risk scores), `/api/v1/anomalies` (Z-score triggers), `/api/v1/risk` (historic risk registry), and `/api/v1/forecast` (latest forecast metrics).
- **Next.js Dashboard**: Dynamic pages at `/dashboard/predictions` (predictive summary overview), `/dashboard/predictions/site/[id]` (site metric projections and explaining signals), and `/dashboard/predictions/tunnel/[id]` (tunnel path forecasts and risk timelines).
- **Typer CLI**: Bootstrapped CLI in `apps/cli` with support for `plutopus health` commands.
- **Docker Stack**: Multi-container stack configured in `docker-compose.yml` linking API, Dashboard, PostgreSQL (TimescaleDB), Qdrant, Redpanda, Ollama, and `prediction-worker`.
- **Telemetry Worker**: Consumes raw data from `metrics_raw` and `events_raw` topics, normalizes the data, and inserts it into PostgreSQL/TimescaleDB.
- **Prediction Worker**: A scheduled background worker in `services/prediction/src/worker.py` running linear forecasts, Z-score anomalies, and 0-100 site/tunnel risk indexes. Runs every 5 minutes (default configuration).
- **Mock Streamer**: Simulated telemetry data generator in `scripts/generate-demo-telemetry.py` extended to simulate Congestion, Latency Drift, Packet Loss Burst, Tunnel Failure, Interface Flapping, and Traffic Surge.
- **Lab Topology**: Scaffolding data defined in `services/topology/topology.yaml` expanded to 7 sites (Hub + Branch-01..06) with dual tunnels and back-ups.
- **Graph Engine & Repo**: Implemented `services/topology/graph` (using NetworkX) and `services/topology/repository` (for entity relational queries).
- **Metrics Correlation**: Added `plutopus_shared/correlation` mapping metrics to sites, devices, and tunnels.
- **Test Suite**: Automated tests verifying topology loading, seeding, normalizers, API controllers, and Phase 3 forecasting pipelines. Achieved **90.8% average coverage** for prediction modules.

### What is Not Working / Not Implemented Yet
- **Phase 4 Features**: AI Copilots, Qdrant/Ollama integration (reserved for subsequent phases).

---

## Log of Changes

### Phase 3 Implementation (2026-06-29)
1. Added `Anomaly`, `RiskScore`, and `Forecast` models to the shared database package.
2. Built `services/prediction/` layout featuring `forecasting`, `anomaly`, `risk`, and `correlation` engines.
3. Implemented Z-score anomaly classifiers and linear trend metric forecasting (15m, 30m, 60m).
4. Created 0-100 site and tunnel risk scoring pipelines with explainable contributors.
5. Extended APIs: `/api/v1/predictions`, `/api/v1/predictions/sites`, `/api/v1/predictions/tunnels`, `/api/v1/anomalies`, `/api/v1/risk`, and `/api/v1/forecast`.
6. Created React dashboard pages for predictions overview, site details, and tunnel details.
7. Extended the demo generator script with 6 real-world failure injection scenarios.
8. Added test suite achieving 90.8% average coverage for Phase 3 modules.
9. Synchronized changes to git and pushed to GitHub main.
