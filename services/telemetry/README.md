# Telemetry Service

This microservice is responsible for ingesting, processing, and storing real-time telemetry from SD-WAN and MPLS network endpoints into TimescaleDB and Redpanda.

## Tech Stack
- Python 3.12
- FastAPI
- TimescaleDB (PostgreSQL)
- Redpanda (Kafka compatibility)
