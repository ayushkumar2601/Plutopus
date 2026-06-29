# ADR 0001: Why FastAPI

## Context & Problem
We require a modern backend framework that allows rapid development, handles async workloads, auto-documents endpoints, and integrates seamlessly with Pydantic for schema validations.

## Decision
Choose **FastAPI** as the main backend framework.

## Consequences
- **High Performance**: ASGI-native, built on Starlette, matching NodeJS and Go speeds.
- **Auto Documentation**: Exposes OpenAPI spec and Swagger UI out of the box.
- **Type Safety**: Full integration with Pydantic enables shared schema packages to compile and validate payload contracts automatically.
