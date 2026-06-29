# Plutopus Master Project Documentation

This document serves as the single source of truth for the current state, active phase, features implemented, and developer notes for the Plutopus platform.

---

## Current Project Phase
- **Phase 1: Foundation & Telemetry (Completed)**
- **Progress Percentage**: 100%

---

## Current System State

### What is Working
- **Shared Schemas**: Pydantic schemas (`HealthResponse`, `ApiResponse`, `ErrorResponse`) created under `packages/schemas`.
- **FastAPI API**: App structure bootstrapped in `apps/api` with Swagger docs enabled and versioned `GET /api/v1/health` + root `GET /health` endpoints. Added `/api/v1/sites`, `/api/v1/devices`, `/api/v1/tunnels`, `/api/v1/metrics`, `/api/v1/events`, and `/api/v1/topology` endpoints.
- **Next.js Dashboard**: React 19 / Next.js 15 application initialized in `apps/dashboard` with Tailwind CSS, TypeScript, and `shadcn/ui` pre-configured. Created dynamic view pages at `/dashboard`, `/topology` (SVG graph), and `/dashboard/metrics` (utilization and latency graph sparklines).
- **Typer CLI**: Bootstrapped CLI in `apps/cli` with support for `plutopus health` commands.
- **Docker Stack**: Multi-container stack configured in `docker-compose.yml` linking API, Dashboard, PostgreSQL (TimescaleDB), Qdrant, Redpanda, Ollama, and `telemetry-worker`. Added a `redpanda-init` container to provision topics on startup.
- **Telemetry Worker**: Consumes raw data from `metrics_raw` and `events_raw` topics, normalizes the data, and inserts it into PostgreSQL/TimescaleDB.
- **Mock Streamer**: Simulated telemetry data generator in `scripts/generate-demo-telemetry.py` streams SNMP metrics/Syslog alerts into Redpanda.
- **Lab Topology**: Scaffolding data defined in `services/topology/topology.yaml` representing a Spoke-Hub network topology.
- **Topology Seeding**: Seeding tool in `services/topology/seed.py` dynamically writes topology mappings to database tables. Accessible via `make seed-topology`.
- **Pre-commit & Developer Tooling**: Unified `Makefile` tasks and `.pre-commit-config.yaml` configured.
- **Test Suite**: Automated tests verifying topology loading, seeding, normalizers, and API controllers. Achieved **90% coverage**.

### What is Not Working / Not Implemented Yet
- **Phase 2 & Beyond Features**: Ingestion of real production physical network elements (SNMP/gNMI collector daemon), Predictive Analytics, AI Copilots, Qdrant/Ollama integration (reserved for subsequent phases).

---

## Log of Changes

### Phase 1 Scaffolding (2026-06-29)
1. Created `packages/schemas` containing shared Pydantic models.
2. Initialized Next.js 15 inside `apps/dashboard`. Added `shadcn` and a custom CSS loading indicator.
3. Created FastAPI server in `apps/api` with routing v1 structure and `/health` route.
4. Created Typer CLI in `apps/cli` with `health` command connected to HTTP client.
5. Created Dockerfiles for API, Dashboard, CLI and root `docker-compose.yml` file.
6. Created docs folder with Architecture overview, roadmap, and ADRs.
7. Defined lab topology YAML in `services/topology/topology.yaml`.
8. Created database tables mapping nodes, sites, tunnels, events, and metrics.
9. Implemented topology seed script `seed.py` and connected it to the Makefile as `make seed-topology`.
10. Added Redpanda initial topics creator script `init-redpanda.sh` and linked it as a startup helper container.
11. Built telemetry worker consuming `metrics_raw` and `events_raw` from Redpanda and saving to database.
12. Added Telegraf configuration for SNMP/Syslog data streams.
13. Created mock network generator stream `generate-demo-telemetry.py`.
14. Implemented dashboard charts and topology graph visualizations.
15. Created comprehensive test suite with 90% code coverage.
