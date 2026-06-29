# ADR 0005: Why Monorepo

## Context & Problem
Plutopus contains multiple microservices, CLI tools, frontends, and configuration scripts. Fragmenting them into separate git repos causes dependency drift, painful schema updates, and fragmented developer workflows.

## Decision
Choose a unified **Monorepo** structure.

## Consequences
- **Single Source of Truth**: Atomic commits update schemas, API backend, and CLI concurrently.
- **Shared Code/Contracts**: Common structures (`packages/schemas`) can be referenced locally across services easily.
- **Unified DX**: Shared Makefile, pre-commit configuration, and docker-compose configurations.
