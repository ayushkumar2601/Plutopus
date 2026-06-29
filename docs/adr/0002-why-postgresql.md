# ADR 0002: Why PostgreSQL & TimescaleDB

## Context & Problem
Plutopus stores relational metadata (topology nodes, alerts, settings) alongside high-frequency time-series telemetry (latency, packet loss, bandwidth metrics). Running separate databases for relational and telemetry data adds operational overhead.

## Decision
Choose **PostgreSQL** with the **TimescaleDB** extension.

## Consequences
- **Unified Engine**: Keep relational and time-series data together, queryable via standard SQL.
- **Hypertables**: TimescaleDB automatically partitions tables by time chunks, ensuring rapid write/read performance.
- **Compression**: Native columnar compression reduces database footprint on disk.
