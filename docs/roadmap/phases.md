# Plutopus Phases & Roadmap

This document outlines the development lifecycle of the Plutopus Predictive NOC Copilot.

---

## Phase 1: Foundation & Telemetry
- Establish monorepo structure, shared schemas, and base application boundaries.
- Set up Docker environment (TimescaleDB, Redpanda, Qdrant, Ollama).
- Build the telemetry collector service for SNMP/gNMI ingest.
- Implement event-driven streams inside Redpanda.

## Phase 2: Topology & Network Intelligence
- Implement the Topology Service to build global routing graphs.
- Track tunnels, physical lines, and state switches.
- Display an interactive topology graph map in the Next.js Dashboard.
- Correlate alarms directly to nodes on the map.

## Phase 3: Predictive Analytics
- Write prediction engines that monitor telemetry streams in real time.
- Implement forecasting models for packet loss, jitter, and link latency.
- Fire alerts into Redpanda before the degradation threshold is hit.

## Phase 4: AI Copilot
- Connect LangChain/LlamaIndex agents to local Ollama runtimes.
- Index vendor datasheets and standard CLI manuals inside Qdrant.
- Implement conversation UI inside Next.js.
- Allow querying: *"What caused the latency spike on Site-B tunnel at 3 PM?"*

## Phase 5: Workflow Automation
- Implement safe diagnostic check loops (pings, trace-routes via agents).
- Orchestrate webhook triggers to dynamically switch paths if degradation is predicted.
- Slack, MS Teams, and email alerting channels.

## Phase 6: Air-Gapped Platform
- Bundle everything into an offline-installable package.
- Support single-command offline deployments on private servers.
- Model pruning and performance optimization on CPU/FPGA hardware.
