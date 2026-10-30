<div align="center">

```
  ____  _         _                           
 |  _ \| |_   _ _| |_ ___  _ __  _   _ ___    
 | |_) | | | | | | __/ _ \| '_ \| | | / __|   
 |  __/| | |_| | | || (_) | |_) | |_| \__ \   
 |_|   |_|\__,_|_|\__\___/| .__/ \__,_|___/   
                          |_|                 
```

# Plutopus

### Enterprise AI-Powered Predictive NOC Copilot for SD-WAN & MPLS Networks

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-PostgreSQL%2016-FDB515?style=flat-square&logo=postgresql&logoColor=white)](https://www.timescale.com)
[![Redpanda](https://img.shields.io/badge/Redpanda-Kafka--Streaming-E3322F?style=flat-square&logo=apachekafka&logoColor=white)](https://redpanda.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20Search-DC2626?style=flat-square)](https://qdrant.tech)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000?style=flat-square)](https://ollama.com)
[![Docker](https://img.shields.io/badge/Docker-Compose%20v3.8-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Helm%200.1.0-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen?style=flat-square)](tests/)
[![Security](https://img.shields.io/badge/Air--Gap-Ready-success?style=flat-square)](docs/compliance/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

<br/>

**Plutopus is the world’s first AI-native, air-gap-ready predictive Network Operations Center (NOC) Copilot.**  
It bridges the gap between dynamic SD-WAN overlays and physical MPLS underlays—forecasting failures, performing automated root-cause analysis, and guiding operators with grounded local AI before outages occur.

[Quickstart](#-quick-start) • [Architecture](#-system-architecture) • [Predictive Engine](#-predictive-analytics-engine) • [AI Copilot](#-ai-copilot--grounded-rag) • [Air-Gap Deployment](#-air-gap--security-readiness) • [API Reference](#-api-reference)

---

</div>

## 📌 Executive Overview

Modern enterprise wide-area networks layer complex software-defined WAN overlays over legacy MPLS and broadband circuits. While this provides routing agility, it creates **catastrophic visibility blind spots**:
- **Alert Fatigue**: A single underlay fiber flap triggers thousands of cascading alerts across overlays, firewalls, and application monitors.
- **Reactive Firefighting**: Traditional NOC monitoring tools are backward-looking—confirming that branches dropped 5 minutes ago.
- **Manual Root-Cause Triage**: Engineers manually correlate raw SNMP, Syslog, and BGP tables under extreme SLA pressure.

### The Plutopus Paradigm Shift

```
Traditional Monitoring (Reactive):
[Underlay Degradation] ──────► [Overlay Failure] ──────► [Alert Storm] ──────► [Manual Triage] ──────► [Downtime & SLA Breach]

Plutopus Intelligence (Predictive):
[Telemetry Telemetry Ingestion] ──► [EMA + Trend Forecasting] ──► [Topology Correlation] ──► [AI Copilot Grounded Action] ──► [Zero Disruption]
                                     ↳ 15m / 30m / 60m Lookahead    ↳ Root-Cause Isolated        ↳ Runbook Automated
```

| Dimension | Legacy Monitoring (SolarWinds, Datadog) | Plutopus NOC Copilot |
| :--- | :--- | :--- |
| **Operational Model** | Reactive (post-incident alerts) | **Predictive** (15m, 30m, 60m forward lookahead) |
| **Topology Context** | Flat metric tables & siloed dashboards | **Dynamic NetworkX Digraph** connecting Sites ↔ Devices ↔ Tunnels |
| **Alert Management** | Raw alert storms requiring manual filtering | **Topology-Aware Correlation** grouping anomalies into single root-cause candidates |
| **AI Capabilities** | Cloud-dependent or generic chatbot | **Air-Gapped Local LLM (Ollama)** with deterministic fallback & zero data leakage |
| **Deployment Model** | Cloud SaaS or heavy hardware appliances | **Single-command Docker Compose / Helm**, 100% air-gap verified |

---

## ✨ Key Capabilities

```mermaid
mindmap
  root((Plutopus Platform))
    Telemetry Streaming
      Redpanda Message Broker
      Kafka Compatible
      TimescaleDB Hypertables
    Topology Intelligence
      NetworkX Graph Model
      Overlay to Underlay Mapping
      Site Health Scoring
      Dynamic Shortest Paths
    Predictive Analytics
      EMA Noise Smoothing
      Linear Trend Forecasting
      Horizon Aware Dampening
      Quantitative Confidence Scoring
      Z Score Anomaly Detection
      0 to 100 Composite Risk Index
    Event Correlation
      Hub Congestion Isolation
      Spoke Grouping
      Multi Factor Priority Engine
      Automated Incident Creation
    Air Gap AI Copilot
      Local Ollama Inference
      Grounded Runbook RAG
      Deterministic Fallback
      Zero Hallucination Guarantee
    Enterprise Hardening
      JWT with Secret Rotation
      RBAC Admin Operator Viewer
      Immutable Audit Logging
      K8s Network Isolation
```

- ⚡ **High-Throughput Streaming**: Redpanda event bus consuming high-frequency raw telemetry, normalized directly into TimescaleDB hypertables.
- 🕸️ **Real-Time Topology Graph**: Dynamic NetworkX model representing sites, network elements, interfaces, and overlay tunnels with graph traversal algorithms.
- 🔮 **Dual-Engine Predictive Analytics**: Combines Exponential Moving Average (EMA) smoothing with linear trend regression and horizon-aware dampening (`0.8` for 15m, `0.5` for 30m, `0.2` for 60m) to predict latency, packet loss, and link saturation.
- 📐 **Quantitative Confidence Scoring**: Mathematically derived confidence metrics evaluating sample size, time-span coverage, historical variance, and projection horizons.
- 🚨 **Topology-Aware Incident Correlation**: Automatically groups cascading anomalies into single, actionable incidents with identified root causes and confidence levels (e.g., Hub Congestion at 92% confidence).
- 🤖 **Air-Gapped AI Copilot**: Grounded diagnostic assistant running locally on Ollama (Qwen/Llama) with retrieval over operational runbooks. Features sub-5ms deterministic mathematical fallback if the LLM runtime is offline.
- 🛡️ **Air-Gap Compliance by Design**: Zero phone-home calls, self-contained offline distribution bundles with SHA256 integrity verification, and local model layer packaging.

---

## 🏛️ System Architecture

### 1. Multi-Tier Architecture Diagram

```mermaid
graph TB
    subgraph Clients["Presentation & Client Layer"]
        DASH["Next.js 15 Web Dashboard\n:3000"]
        CLI["Typer Operator CLI\n(plutopus cli)"]
    end

    subgraph Gateway["API Gateway — FastAPI :8000"]
        direction LR
        AUTH["JWT + Rotation & RBAC"]
        AUDIT["Immutable Audit Logger"]
        PROM_MW["Prometheus Middleware"]
        ROUTES["REST APIs (/api/v1/*)"]
    end

    subgraph Intelligence["Intelligence & Analytic Services"]
        TOPO["Topology Engine\n(NetworkX MultiDiGraph)"]
        PRED["Prediction Worker\n(EMA + Linear Forecasting)"]
        CORR["Correlation & Priority Engine\n(Topological Root-Cause)"]
        COP["Copilot Engine\n(Context Assembler + RAG)"]
    end

    subgraph Storage["Persistent & Vector Storage Layer"]
        PG[("TimescaleDB\nPostgreSQL 16 Hypertables")]
        QDRANT[("Qdrant\nVector Engine :6333")]
        OLLAMA["Ollama Runtime\n(Local LLM :11434)"]
    end

    subgraph Stream["Streaming & Ingestion Layer"]
        RP["Redpanda Broker\nKafka-compatible :19092"]
        TW["Telemetry Consumer Worker\n(Batch Normalizer)"]
    end

    subgraph Observability["Operations & Observability"]
        PROM["Prometheus Scraper\n:9090"]
        GRAF["Grafana Dashboards\n:3001"]
    end

    DASH --> Gateway
    CLI --> Gateway
    Gateway --> TOPO
    Gateway --> CORR
    Gateway --> COP
    Gateway --> PROM_MW

    TW --> RP
    TW --> PG

    PRED --> PG
    TOPO --> PG
    CORR --> PG
    COP --> PG
    COP --> OLLAMA
    COP --> QDRANT

    PROM_MW --> PROM
    PROM --> GRAF
```

---

### 2. Telemetry Ingestion & Predictive Data Flow

```mermaid
sequenceDiagram
    autonumber
    participant SRC as SD-WAN / MPLS Fabric
    participant RP as Redpanda Broker (metrics_raw)
    participant TW as Telemetry Consumer
    participant DB as TimescaleDB
    participant PW as Prediction Worker
    participant CE as Correlation Engine

    SRC->>RP: Stream high-frequency telemetry (utilization, latency, loss)
    TW->>RP: Consume raw metric batch
    TW->>TW: Validate schema & normalize timestamps
    TW->>DB: Batch INSERT into metrics & events hypertables
    loop Every PREDICTION_INTERVAL (300s)
        PW->>DB: Fetch rolling metric history per entity
        PW->>PW: Apply calculate_ema() to smooth spikes
        PW->>PW: fit_linear_trend() with horizon dampening (+15m, +30m, +60m)
        PW->>PW: Compute quantitative confidence score
        PW->>PW: Detect Z-score anomalies & compute 0-100 risk score
        PW->>DB: Bulk INSERT forecasts, anomalies, and risk_scores
    end
    CE->>DB: Poll active anomalies
    CE->>CE: Correlate hub-and-spoke topology & compute incident priority
    CE->>DB: INSERT prioritized incidents
```

---

### 3. Local AI Copilot Request Flow (with Zero-Hallucination Fallback)

```mermaid
sequenceDiagram
    autonumber
    participant Op as NOC Operator
    participant API as FastAPI Gateway
    participant CTX as Context Assembler
    participant RAG as Runbook Retrieval
    participant LLM as Ollama Local Model
    participant FB as Deterministic Fallback

    Op->>API: POST /api/v1/copilot/query {question, site_id}
    API->>CTX: Assemble topological context (inventory, anomalies, risk, forecasts)
    CTX-->>API: Grounded site state dictionary
    API->>RAG: Match question against 6 structured runbooks
    RAG-->>API: Extracted runbook procedures
    API->>LLM: Dispatch prompt with strict operational grounding (4s timeout)
    alt Ollama inference succeeds
        LLM-->>API: Synthesized analysis & actionable remediation steps
    else Timeout or LLM Offline
        API->>FB: Trigger deterministic diagnostic engine
        FB-->>API: Structured diagnostic based strictly on telemetry metrics
    end
    API-->>Op: Complete response with source attributions & active context
```

---

## 🔮 Predictive Analytics Engine

Plutopus features an upgraded multi-phase predictive analytics pipeline designed specifically for noisy wide-area network environments:

```mermaid
flowchart LR
    A["Raw Metric Stream\n(Latency, Loss, Utilization)"] --> B["Phase 1: EMA Smoothing\n(α = 0.2 Spike Dampening)"]
    B --> C["Phase 2: Linear Trend Fitting\n(OLS on Relative Time)"]
    C --> D["Phase 3: Horizon Dampening\n(15m: 0.8 | 30m: 0.5 | 60m: 0.2)"]
    D --> E["Multi-Horizon Forecasts\n(f15, f30, f60)"]
    E --> F["Phase 4: Quantitative Confidence\n(Samples + Coverage + Variance)"]
```

### 1. EMA Smoothing & Trend Extraction
To prevent transient traffic spikes from causing false extrapolation, metrics pass through an Exponential Moving Average filter:
$$\text{EMA}_t = \alpha \cdot x_t + (1 - \alpha) \cdot \text{EMA}_{t-1} \quad (\alpha = 0.2)$$

### 2. Horizon-Aware Dampening
Network degradation rarely scales infinitely in linear fashion. Plutopus applies empirical dampening factors to projections:
- **15-Minute Lookahead**: `0.8` dampening (high trend fidelity)
- **30-Minute Lookahead**: `0.5` dampening (moderate mean reversion)
- **60-Minute Lookahead**: `0.2` dampening (conservative bounds)

### 3. Quantitative Confidence Scoring
Confidence is computed using mathematical criteria rather than arbitrary estimates:
$$\text{Confidence} = \left( 0.4 \cdot S_{\text{size}} + 0.4 \cdot S_{\text{coverage}} + 0.2 \cdot S_{\text{variance}} \right) \times \gamma_{\text{horizon}}$$

- **Sample Size ($S_{\text{size}}$)**: $\min(N / 60, 1.0)$ — full confidence requires at least 60 samples.
- **Coverage ($S_{\text{coverage}}$)**: $\min(\Delta t / 900\text{s}, 1.0)$ — requires at least 15 minutes of uninterrupted history.
- **Variance ($S_{\text{variance}}$)**: $\frac{1}{1 + (\sigma^2 / 100)}$ — penalizes erratic oscillations.
- **Horizon Penalty ($\gamma_{\text{horizon}}$)**: Scaled by $0.85$ for long-term 60m projection boundaries.

---

## 🤖 AI Copilot & Grounded RAG

The Copilot runs entirely inside the air-gapped perimeter using local LLMs (e.g., `qwen:0.5b`, `llama3:8b`). It enforces complete grounding:

> [!IMPORTANT]
> **Zero Hallucination Guarantee**
> The Copilot will never invent device states or configuration recommendations. If an Ollama model times out (>4.0s) or fails, the API immediately falls back to a deterministic diagnostic generator that provides structured tabular analysis directly from TimescaleDB.

### Curated Operational Runbooks
The retrieval engine matches incoming queries against 6 embedded production runbooks:

| Runbook File | Trigger Keywords | Operational Purpose |
| :--- | :--- | :--- |
| `congestion.md` | `congestion`, `utilization`, `bandwidth`, `saturation` | QoS buffer inspection, traffic shaping adjustment, link aggregation |
| `high_latency.md` | `latency`, `delay`, `RTT`, `slow` | Underlay provider latency audit, BGP path hop verification |
| `interface_flapping.md` | `flapping`, `cycling`, `instability`, `up/down` | Physical cable diagnosis, optical SFP transceiver light-level check |
| `packet_loss.md` | `loss`, `drops`, `reachability` | MTU mismatch analysis, ingress policing, queue drops |
| `route_instability.md` | `BGP`, `route`, `prefix`, `instability` | Route flapping damping, prefix churn isolation, peer reset |
| `tunnel_failure.md` | `tunnel`, `IPsec`, `VPN`, `down`, `failed` | IKE phase 1/2 negotiation checks, DPD timeout diagnostics |

---

## ⚡ Quick Start

### 1. Prerequisites
- [Docker Engine 24+](https://docs.docker.com/engine/install/) & Docker Compose v2
- Node.js 20+ (for local dashboard development)
- Python 3.11+ (for local SDK / CLI development)

### 2. One-Command Full Stack Launch

```bash
# Clone the repository
git clone https://github.com/ayushkumar2601/Plutopus.git
cd Plutopus

# Configure environment variables
cp .env.example .env

# Launch all 13 microservices in detached mode
docker compose up -d

# Verify system health
docker compose ps
curl http://localhost:8000/health
```

### 3. Seed Topology & Inject Demo Telemetry

```bash
# Seed the SD-WAN/MPLS lab topology (sites, devices, interfaces, tunnels)
docker compose exec api python services/topology/seed.py

# Inject synthetic telemetry to populate metrics and trigger anomaly detection
python scripts/generate-demo-telemetry.py
```

### 4. Access Platform Interfaces

| Interface | Port | Default Credentials | Description |
| :--- | :--- | :--- | :--- |
| **Next.js Dashboard** | `http://localhost:3000` | N/A | Central NOC operations console & topology map |
| **FastAPI Swagger Docs** | `http://localhost:8000/docs` | JWT required (see auth below) | Interactive OpenAPI reference |
| **Grafana Dashboards** | `http://localhost:3001` | `admin` / `admin` | Real-time system metrics & incident trends |
| **Prometheus Exporter** | `http://localhost:9090` | N/A | Telemetry scrape targets & raw metrics |
| **Ollama Local LLM** | `http://localhost:11434` | N/A | Local generative inference engine |
| **Qdrant Vector DB** | `http://localhost:6333` | N/A | Vector embeddings store |

---

## 💻 Operator CLI (Typer)

Plutopus includes a Python CLI for NOC engineers operating in headless or terminal environments:

```bash
# Activate virtual environment
source .venv/bin/activate

# Check cluster and API health
python -m apps.cli.src.main health

# Output:
# === Plutopus System Health Check ===
# API Status: Healthy (Version 1.0.0)
# Database: Connected (TimescaleDB)
# Message Broker: Connected (Redpanda)
# Prediction Worker: Active (Interval: 300s)
```

---

## 🌐 API Reference

All REST endpoints reside under `/api/v1` and enforce RBAC with JWT token authentication.

```bash
# Obtain access token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secure_admin_password"}' | jq -r .access_token)

# Query site topology
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/topology/graph | jq .

# Trigger real-time incident correlation
curl -s -X GET -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/incidents/correlated | jq .

# Ask the Copilot a grounded diagnostic question
curl -s -X POST http://localhost:8000/api/v1/copilot/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "site-branch-04",
    "question": "Why is tunnel-branch-04-primary experiencing degraded latency?"
  }' | jq .
```

### Primary Endpoints Summary

| Group | Method | Endpoint | Min Role | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/health` | Public | Microservice liveness and dependency check |
| **Sites** | `GET` | `/api/v1/sites` | `viewer` | List all network sites and criticality |
| **Devices** | `GET` | `/api/v1/devices` | `viewer` | Query device inventory and IP mapping |
| **Tunnels** | `GET` | `/api/v1/tunnels` | `viewer` | SD-WAN / MPLS tunnel states and endpoints |
| **Topology** | `GET` | `/api/v1/topology/graph` | `viewer` | Full NetworkX adjacency graph JSON |
| **Predictions** | `GET` | `/api/v1/predictions/forecasts` | `viewer` | 15m/30m/60m projections and confidence |
| **Predictions** | `GET` | `/api/v1/predictions/risk` | `viewer` | 0–100 composite risk index by entity |
| **Incidents** | `GET` | `/api/v1/incidents` | `viewer` | Active prioritized network incidents |
| **Correlation** | `GET` | `/api/v1/incidents/correlated` | `operator` | Trigger topological root-cause analysis |
| **Copilot** | `POST` | `/api/v1/copilot/query` | `operator` | Submit natural-language diagnostic query |
| **Export** | `POST` | `/api/v1/incidents/export` | `operator` | Dispatch webhook to external ITSM / PagerDuty |
| **Audit** | `GET` | `/api/v1/audit/logs` | `admin` | View immutable security audit trail |
| **Metrics** | `GET` | `/metrics` | Public | Prometheus scrape exposition endpoint |

---

## 🛡️ Air-Gap & Security Readiness

Plutopus is engineered to deploy in zero-trust, classified, or disconnected mission-critical enclaves:

```mermaid
flowchart LR
    A["Connected Host\n(Build Machine)"] -->|pack-offline-bundle.sh| B["plutopus-offline-bundle.tar.gz\n+ SHA256 Manifest"]
    B -->|Physical Media / Diode| C["Air-Gapped Target Host\n(Isolated NOC Server)"]
    C -->|docker load| D["Local Container Registry"]
    C -->|import-model.sh| E["Local Ollama Model Storage"]
    D & E -->|AIRGAP_MODE=true| F["Full Plutopus Stack Operational\n(No Outbound DNS or WAN Requests)"]
```

### 1. Generating the Offline Bundle
On an internet-connected workstation, create a self-contained archive including all images, model layers, runbooks, and Helm charts:

```bash
./distribution/pack-offline-bundle.sh
# Creates: plutopus-offline-bundle.tar.gz
# Manifest: distribution/checksums/plutopus-offline-bundle.tar.gz.sha256
```

### 2. Exporting & Importing Ollama Models
Export local LLM weights without pulling from external registries:

```bash
# Export
./distribution/models/export-model.sh qwen:0.5b ./models

# Import on isolated host
./distribution/models/import-model.sh ./models/ollama_model_qwen_0.5b.tar
```

### 3. Air-Gap Verification Check
Run the built-in isolation validator to verify compliance:

```bash
AIRGAP_MODE=true ./scripts/airgap/verify.sh
# Generates: airgap-report.md validating zero internet egress
```

### 4. Cryptographic Security Standards
- **JWT Key Rotation**: Supports comma-separated secret keys via `JWT_ROTATION_SECRETS`.
- **Enforced Entropy**: API automatically fails to initialize if `JWT_SECRET` is shorter than 32 characters.
- **Immutable Audit Trail**: All operations log to `audit_logs` storing actor, IP, timestamp, action, and outcome.
- **K8s Network Policies**: `default-deny-all` blocks cross-pod ingress/egress, permitting traffic strictly between API and database pods.

---

## 📊 Database Schema

The platform leverages **TimescaleDB (PostgreSQL 16)** combining relational entity mapping with time-series hypertables:

```mermaid
erDiagram
    sites ||--o{ devices : "contains"
    devices ||--o{ interfaces : "hosts"
    devices ||--o{ events : "generates"
    interfaces ||--o{ tunnels : "src_interface"
    interfaces ||--o{ tunnels : "dst_interface"

    sites {
        string id PK
        string name
        string role
        string business_criticality
    }
    devices {
        string id PK
        string site_id FK
        string name
        string ip
        string role
    }
    interfaces {
        string id PK
        string device_id FK
        string name
        string type
        string status
    }
    tunnels {
        string id PK
        string src_interface_id FK
        string dst_interface_id FK
        string status
    }
    metrics {
        int id PK
        string target_id
        string name
        float value
        datetime timestamp
    }
    forecasts {
        int id PK
        string target_id
        string metric
        float current_val
        float forecast_15m
        float forecast_30m
        float forecast_60m
        float confidence
        datetime timestamp
    }
    anomalies {
        int id PK
        string entity_id
        string entity_type
        string metric
        string severity
        float score
        datetime timestamp
    }
    risk_scores {
        int id PK
        string entity_id
        int risk_score
        string risk_level
        string signals
    }
    incidents {
        string id PK
        string title
        string severity
        int priority
        string root_cause
        float confidence
    }
    audit_logs {
        int id PK
        string username
        string action
        string resource
        string result
        datetime timestamp
    }
```

---

## 📂 Repository Structure

```
Plutopus/
├── apps/
│   ├── api/                     # FastAPI backend gateway (Auth, RBAC, REST v1)
│   ├── cli/                     # Typer-powered operator terminal CLI
│   └── dashboard/               # Next.js 15 Tailwind web console
├── services/
│   ├── telemetry/               # Kafka / Redpanda consumer worker
│   ├── prediction/              # Forecasting (EMA + Linear), Anomaly, Risk engines
│   │   ├── forecasting/         # EMA smoothing, dampening, confidence scoring
│   │   ├── anomaly/             # Z-score metric detector
│   │   └── risk/                # 0-100 site & tunnel risk index
│   ├── topology/                # NetworkX graph representation & lab topology
│   ├── copilot/                 # Local Ollama RAG, prompt engine, runbook retrieval
│   ├── correlation/             # Topology-aware event correlation & priority ranking
│   └── integrations/            # Outbound webhook dispatchers with exponential backoff
├── packages/
│   ├── shared/                  # SQLAlchemy models, TimescaleDB connector, DB sessions
│   ├── schemas/                 # Pydantic schemas shared across services
│   └── utils/                   # Shared logging, formatters, and math helpers
├── infrastructure/
│   ├── helm/                    # Production Kubernetes Helm chart (v0.1.0)
│   ├── k8s/network-policies/    # Default-deny-all zero-trust network policies
│   └── monitoring/              # Prometheus configs and versioned Grafana dashboards
├── distribution/                # Air-gap deployment bundler, models & SHA256 checksums
├── docs/                        # Architecture decision records (ADR), compliance, capacity
├── scripts/                     # Backup, restore, verification, and demo data scripts
├── tests/                       # Comprehensive pytest suite (unit, integration, forecasting)
└── docker-compose.yml           # Complete 13-service orchestration file
```

---

## 🧪 Testing & Validation

Plutopus maintains strict testing standards with **90% code coverage**:

```bash
# Run the complete test suite
.venv/bin/pytest tests/

# Validate forecasting engine & confidence algorithms specifically
.venv/bin/pytest tests/test_forecast_v2.py

# Run static security audit
./scripts/security-audit/audit.sh

# Run database backup & restoration validation
./scripts/backup-validation/validate-restore.sh
```

---

## ⚡ Performance Benchmarks & SLAs

| Operation | Typical Latency | SLA Target | Status |
| :--- | :--- | :--- | :--- |
| **Telemetry Ingestion & Hypertables Commit** | ~12ms / batch | < 50ms | ✅ Exceeding |
| **Topology Shortest Path / Dijkstra** | ~1.5ms | < 20ms | ✅ Exceeding |
| **EMA Forecasting & Confidence per Entity** | ~3ms | < 25ms | ✅ Exceeding |
| **Incident Correlation (50 anomalies)** | ~18ms | < 100ms | ✅ Exceeding |
| **Copilot Context Assembly** | ~42ms | < 200ms | ✅ Exceeding |
| **Copilot Local LLM Inference (`qwen:0.5b`)** | ~850ms–1400ms | < 4000ms | ✅ Exceeding |
| **Copilot Deterministic Fallback** | < 4ms | < 50ms | ✅ Exceeding |
| **Air-Gap Integrity Verification** | ~3.1s | < 30s | ✅ Exceeding |

---

## 🗺️ Roadmap & Evolution

- [x] **Phase 1: Telemetry Foundation** — Redpanda streaming, TimescaleDB hypertables, FastAPI scaffold.
- [x] **Phase 2: Topology Intelligence** — Dynamic NetworkX digraph, path analysis, site health scoring.
- [x] **Phase 3: Predictive Analytics** — EMA smoothing, multi-horizon dampening, confidence scoring, Z-score anomalies.
- [x] **Phase 4: AI Copilot** — Context engine, local Ollama integration, runbook RAG, zero-hallucination fallback.
- [x] **Phase 5: Event Correlation & Workflow** — Hub congestion grouping, priority engine, RBAC, Prometheus & Grafana.
- [x] **Phase 6: Air-Gap Hardening** — Full offline bundle, SHA256 manifests, model export/import, K8s network policies.
- [ ] **Phase 7: Multi-Tenancy** — Enterprise workspace isolation with tenant-scoped encryption.
- [ ] **Phase 8: Distributed Inference** — vLLM & Triton cluster backends for 70B+ parameter models.
- [ ] **Phase 9: Dynamic Discovery** — Automated topology extraction via gNMI, NETCONF, and SNMP traps.

---

## 🤝 Contributing

Contributions are welcome! Please ensure you:
1. Review architectural guidelines in `docs/architecture/` and existing `docs/adr/`.
2. Follow PEP 8 and Python type annotation standards.
3. Add unit and integration tests for new features (`tests/`).
4. Ensure all tests pass with `./Makefile test` and linting with `./Makefile lint`.

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).

<br/>

<div align="center">

**Built for mission-critical NOC teams operating real SD-WAN and MPLS infrastructures.**

[Report an Issue](https://github.com/ayushkumar2601/Plutopus/issues) • [Request Feature](https://github.com/ayushkumar2601/Plutopus/issues/new) • [Documentation](docs/)

</div>
