# ADR 0003: Why Redpanda

## Context & Problem
High-frequency telemetry ingestion requires a streaming message broker that handles huge throughput with extremely low latency. Traditional Apache Kafka has heavy operational complexity (JVM runtime, Zookeeper/KRaft configuration).

## Decision
Choose **Redpanda** as the event streaming backbone.

## Consequences
- **Kafka Compatibility**: Drop-in replacement for Apache Kafka APIs.
- **Performance**: Written in C++, utilizes thread-per-core architectures for maximum throughput.
- **Developer Simplicity**: Single binary deployment, no JVM memory tuning required.
