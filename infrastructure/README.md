# Plutopus Infrastructure Scaffolding

This directory contains configuration files and deployment scripts for local, staging, and production environments.

## Directory Structure
- `docker/`: Dockerfiles for microservices and applications.
- `compose/`: Environment-specific docker-compose overlays.
- `database/`: Database initialization scripts, migration policies, and backup configurations.
- `monitoring/`: Configuration files for Prometheus, Grafana, and vector agents.

## Port Mappings
- **FastAPI Backend (API)**: `8000`
- **Next.js Dashboard**: `3000`
- **TimescaleDB**: `5432`
- **Qdrant**: `6333` (HTTP) / `6334` (gRPC)
- **Redpanda**: `19092` (Kafka API) / `18082` (Proxy)
- **Ollama**: `11434`
