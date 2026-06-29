# Plutopus Master Project Documentation

This document serves as the single source of truth for the current state, active phase, features implemented, and developer notes for the Plutopus platform.

---

## Current Project Phase
- **Phase 2: Topology & Network Intelligence (Completed)**
- **Progress Percentage**: 100%

---

## Current System State

### What is Working
- **Shared Schemas**: Pydantic schemas (`HealthResponse`, `ApiResponse`, `ErrorResponse`) created under `packages/schemas`.
- **FastAPI API**: App structure bootstrapped in `apps/api` with Swagger docs enabled and versioned `GET /api/v1/health` + root `GET /health` endpoints. Added `/api/v1/sites`, `/api/v1/devices`, `/api/v1/tunnels`, `/api/v1/metrics`, `/api/v1/events`, and `/api/v1/topology` endpoints.
- **FastAPI v2 Topology APIs**: Built `/api/v1/topology/graph` (networkx representation), `/api/v1/topology/sites/{id}` (site detail and status), `/api/v1/topology/devices/{id}` (device interface and status), `/api/v1/topology/path` (shortest path calculation between sites), `/api/v1/topology/neighbors`, and `/api/v1/topology/intelligence`.
- **Next.js Dashboard**: React 19 / Next.js 15 application initialized in `apps/dashboard` with Tailwind CSS, TypeScript, and `shadcn/ui` pre-configured. Created dynamic view pages at `/dashboard`, `/topology` (interactive SVG graph with site/device details sidepanel and path calculation), `/dashboard/metrics` (utilization and latency graph sparklines), `/dashboard/sites` (site health summaries), and `/inventory/*` registries.
- **Typer CLI**: Bootstrapped CLI in `apps/cli` with support for `plutopus health` commands.
- **Docker Stack**: Multi-container stack configured in `docker-compose.yml` linking API, Dashboard, PostgreSQL (TimescaleDB), Qdrant, Redpanda, Ollama, and `telemetry-worker`. Added a `redpanda-init` container to provision topics on startup.
- **Telemetry Worker**: Consumes raw data from `metrics_raw` and `events_raw` topics, normalizes the data, and inserts it into PostgreSQL/TimescaleDB.
- **Mock Streamer**: Simulated telemetry data generator in `scripts/generate-demo-telemetry.py` streams SNMP metrics/Syslog alerts into Redpanda.
- **Lab Topology**: Scaffolding data defined in `services/topology/topology.yaml` expanded to 7 sites (Hub + Branch-01..06) with dual tunnels and back-ups.
- **Topology Seeding**: Seeding tool in `services/topology/seed.py` dynamically writes topology mappings to database tables. Accessible via `make seed-topology`.
- **Graph Engine & Repo**: Implemented `services/topology/graph` (using NetworkX) and `services/topology/repository` (for entity relational queries).
- **Intelligence & Health Engines**: Implemented `services/topology/intelligence` (for degree and criticality centrality) and `services/topology/health` (for deriving site/tunnel state statuses).
- **Metrics Correlation**: Added `plutopus_shared/correlation` mapping metrics to sites, devices, and tunnels.
- **Pre-commit & Developer Tooling**: Unified `Makefile` tasks and `.pre-commit-config.yaml` configured.
- **Test Suite**: Automated tests verifying topology loading, seeding, normalizers, API controllers, and Phase 2 Graph/Health structures. Achieved **86% coverage**.

### What is Not Working / Not Implemented Yet
- **Phase 3 & Beyond Features**: Predictive Analytics, AI Copilots, Qdrant/Ollama integration (reserved for subsequent phases).

---

## Log of Changes

### Phase 2 Implementation (2026-06-29)
1. Expanded `topology.yaml` from 4 to 7 sites (Hub + 6 spokes) with backup links and dual tunnels.
2. Built `TopologyGraphEngine` using NetworkX for topology node-link mapping.
3. Created `TopologyRepository` for database query modeling.
4. Created `TopologyIntelligenceService` and `TopologyHealthEngine` to calculate centrality, criticality, and live health metrics.
5. Extended APIs: `/api/v1/topology/graph`, `/api/v1/topology/sites/{id}`, `/api/v1/topology/devices/{id}`, `/api/v1/topology/path`, `/api/v1/topology/neighbors`, and `/api/v1/topology/intelligence`.
6. Created React pages for inventories `/inventory/sites`, `/inventory/devices` and site health summaries `/dashboard/sites`.
7. Upgraded `/topology` map to be interactive with detail nodes select sidepanels and BGP path discovery checks.
8. Implemented metrics correlation layer in the shared database library.
9. Added Phase 2 test suite achieving 86% total coverage.
10. Composed all files to GitHub repository.
