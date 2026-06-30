# Plutopus Platform User Guideline & Testing Documentation

Welcome to the **Plutopus** User Guideline and Testing Documentation. Plutopus is an air-gap-ready Network Operations Intelligence Platform that combines telemetry ingestion, topology awareness, predictive analytics, incident correlation, and an AI copilot to help network teams detect, understand, and respond to issues before they impact operations.

This document provides step-by-step guidelines for **NOC Operators**, **Developers**, and **Administrators** to run, test, and use the platform.

---

## Table of Contents
1. [Prerequisites & System Requirements](#1-prerequisites--system-requirements)
2. [Quick Start & Setup Guide](#2-quick-start--setup-guide)
3. [Testing the Platform](#3-testing-the-platform)
4. [Using the Platform — Step-by-Step Operator Guide](#4-using-the-platform--step-by-step-operator-guide)
5. [Developer Guide](#5-developer-guide)
6. [Administrator Guide](#6-administrator-guide)
7. [Air-Gap Deployment & Verification](#7-air-gap-deployment--verification)
8. [Troubleshooting & Support](#8-troubleshooting--support)

---

## 1. Prerequisites & System Requirements

Before setting up Plutopus, ensure your system meets the following specifications:

- **Operating System**: macOS, Linux, or Windows (WSL2 recommended).
- **Docker Engine**: Version 24+ and Docker Compose v2.
- **Python**: Version 3.9+ (required for local development/testing only).
- **Node.js**: Version 20+ (required for local dashboard development only).
- **Hardware Profile**: 
  - Minimum: 4 CPU Cores, 8 GiB RAM.
  - Recommended (with local LLM): 8 CPU Cores, 16 GiB RAM (especially on M-series Mac or with GPU support).

---

## 2. Quick Start & Setup Guide

Follow these steps to deploy the entire Plutopus stack locally using Docker Compose.

### Step 2.1: Clone the Repository
Open a terminal and clone the repository:
```bash
git clone https://github.com/ayushkumar2601/Plutopus.git
cd Plutopus
```

### Step 2.2: Configure Environment Variables
Copy the template `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Open [.env](file:///Users/ayush/Desktop/pluto/.env.example) and ensure the environment variables are correctly defined.
> [!IMPORTANT]
> The `JWT_SECRET` variable must contain a cryptographically secure key of at least **32 characters** (256 bits). If the key is too short, the API service will throw a `ValueError` at startup and fail to boot.

Example:
```env
JWT_SECRET=super_secret_minimum_32_character_compliance_key_12345
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/plutopus
REDPANDA_BROKERS=redpanda:9092
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen:0.5b
AIRGAP_MODE=false
```

### Step 2.3: Spin Up the Infrastructure
Boot all 13 microservices in the background:
```bash
docker compose up -d
```
Check the status of the containers to ensure everything starts cleanly:
```bash
docker compose ps
```

### Step 2.4: Seed the Network Topology
Initialize the database schemas and insert the default laboratory WAN network topology:
```bash
make seed-topology
```
*Note: This runs the topology seeder script [seed.py](file:///Users/ayush/Desktop/pluto/services/topology/seed.py), which populates sites, devices, interfaces, and tunnels.*

### Step 2.5: Generate Synthetic Telemetry
To simulate active network telemetry, run the generator script:
```bash
python3 scripts/generate-demo-telemetry.py
```
This script publishes simulated usage metrics (latency, packet loss, interface utilization) to the Redpanda queue, which are then consumed, normalized, and stored by the telemetry service in TimescaleDB.

### Step 2.6: Access the Interfaces
Once started, the services expose endpoints locally:
- **Dashboard UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Grafana Metrics Dashboard**: [http://localhost:3001](http://localhost:3001) (Credentials: `admin`/`admin`)
- **Prometheus Scraper UI**: [http://localhost:9090](http://localhost:9090)

---

## 3. Testing the Platform

Plutopus features a comprehensive test suite (45 tests across 9 phases achieving ~90% coverage) using `pytest`.

### Step 3.1: Set Up Local Virtual Environment
If you want to run tests locally outside containers:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Install shared packages and applications in editable mode
pip install -e packages/shared
pip install -e packages/schemas
pip install -e apps/api
pip install -e apps/cli
```

### Step 3.2: Run All Tests
Execute the test suites using the Makefile:
```bash
make test
```
Or directly using `pytest`:
```bash
pytest tests/
```

### Step 3.3: Run with Coverage Report
To audit test coverage across the API and intelligence services:
```bash
pytest --cov=apps/api --cov=services/ --cov-report=term-missing tests/
```

### Step 3.4: Run Specific Phase Suites
You can run specific test phase files targeting distinct components:
- **API Endpoints**: `pytest tests/test_api.py -v`
- **Topology Engine**: `pytest tests/test_phase2.py -v`
- **Prediction Worker**: `pytest tests/test_phase3.py -v`
- **AI Copilot & Fallback**: `pytest tests/test_phase4.py -v`
- **Incident Correlation & Webhooks**: `pytest tests/test_phase5.py -v`
- **Audit Logging & Security Hardening**: `pytest tests/test_phase6.py -v`

### Step 3.5: Run Code Quality Checks
Format the code to comply with style rules:
```bash
make format
```
Verify lint compliance (Ruff, Mypy, ESLint):
```bash
make lint
```

---

## 4. Using the Platform — Step-by-Step Operator Guide

This section describes how a NOC Operator interacts with the user interfaces to monitor network topology and resolve issues.

### Step 4.1: Authentication & Roles
To test Role-Based Access Control (RBAC):
1. **Acquire a JWT token** by authenticating via `POST /api/v1/auth/token` on the API docs page (`http://localhost:8000/docs`).
2. **Review your Role Claims**:
   - `viewer`: Can read topology, metrics, and incident summaries.
   - `operator`: Can trigger live incident correlations, run Copilot queries, and dispatch webhooks.
   - `admin`: Can view audit logs and manage platform components.
3. Accessing a route without the appropriate permissions returns a `403 Forbidden` response.

### Step 4.2: Inspecting the Interactive Topology Graph
1. Navigate to the **Topology** page on the Dashboard (`http://localhost:3000/topology`).
2. View the graphical rendering of the network, which connects sites (Hub, Branch 01, Branch 02, etc.), devices, interfaces, and active tunnels.
3. Hover over nodes to inspect real-time Health Scores. Site health aggregates the severity of recent anomalies and interface failures (ranging from `0` to `100`).

### Step 4.3: Analyzing Predictions & Anomaly Detections
1. Open the **Predictions** menu (`http://localhost:3000/dashboard/predictions`).
2. Review the **Forecasting Horizon**:
   - The linear regression forecaster plots metric values 15m, 30m, and 60m into the future.
   - Any predicted threshold breach (e.g., interface utilization exceeding 90%) displays a prediction card with confidence metrics.
3. Review **Active Anomalies**:
   - Detections with higher Z-scores are classified as `warning` or `critical`.
   - Each anomaly lists the source interface/tunnel and metric type (`latency`, `packet_loss`, `utilization`).

### Step 4.4: Correlating Incidents & Reviewing Root Cause
1. Go to the **Incidents** board (`http://localhost:3000/dashboard/incidents`).
2. The `EventCorrelationEngine` groups related raw alerts. You will see:
   - **Correlated Hub Congestion**: Occurs when a Hub tunnel is degraded and multiple branch sites simultaneously register metrics drift. The Hub is marked as the root cause (Confidence: 92%).
   - **Local Site Degradation**: Occurs when multiple anomalies appear within a single site.
3. Trigger a manual correlation run (requires `operator` role):
   ```bash
   curl -X GET -H "Authorization: Bearer <your-jwt-token>" http://localhost:8000/api/v1/incidents/correlated
   ```
4. Prioritized incident ranks (`0` to `100`) reflect risk score, scope, time-to-impact, and business criticality.

### Step 4.5: Chatting with the AI Copilot
1. Select the **Copilot** interface (`http://localhost:3000/dashboard/copilot`).
2. Ask a question regarding a specific site, for example: `"Is Branch 01 experiencing link degradation?"` or `"Explain the root cause of the current high latency."`
3. **How Copilot retrieves context**:
   - It queries TimescaleDB to fetch site inventory, active anomalies, risk scores, and telemetry forecasts.
   - It searches local markdown runbooks (located in `services/copilot/runbooks/`) for matched keywords.
4. **Offline Fallback Behavior**:
   - If the local Ollama LLM is unavailable or times out, the Copilot automatically calls `generate_fallback_response()`.
   - You will see a structured, deterministic diagnostics report outlining actual anomalies, topology paths, and active warnings without any LLM hallucination.

### Step 4.6: Exporting Incidents via Webhooks
1. Operators can dispatch incident data to external ticketing systems.
2. Trigger an outbound webhook export:
   ```bash
   curl -X POST -H "Authorization: Bearer <your-jwt-token>" \
     -H "Content-Type: application/json" \
     -d '{"incident_id": "inc-123", "target_url": "http://your-noc-webhook-receiver/alerts"}' \
     http://localhost:8000/api/v1/incidents/export
   ```
3. The platform retries failed deliveries using exponential backoff.

---

## 5. Developer Guide

Developers extending Plutopus should follow these operational instructions:

### Step 5.1: Create a New REST Endpoint
1. **Define Schema**: Create a Pydantic model in `packages/schemas/src/plutopus_schemas/` for validation.
2. **Implement Endpoint Router**: Write the route handler inside `apps/api/src/api/v1/endpoints/`.
3. **Apply Auth & RBAC**: Wrap the handler with `RoleChecker` dependency.
4. **Log the Action**: If modifying resources, insert an audit log event:
   ```python
   from plutopus_shared.db import write_audit_log
   write_audit_log(db, username=user.username, action="create_link", resource="tunnels", resource_id=tunnel.id, result="success")
   ```
5. **Register Router**: Update `apps/api/src/api/v1/router.py`.

### Step 5.2: Adding a Copilot Runbook
1. Create a markdown runbook detailing the network mitigation procedure (e.g., `services/copilot/runbooks/bgp_instability.md`).
2. In `services/copilot/retrieval/__init__.py`, update `get_relevant_runbooks()` to parse the user query for keywords:
   ```python
   if any(k in query_lower for k in ["bgp", "route", "peer"]):
       matched_files.append("bgp_instability.md")
   ```
3. Run `make test` to verify the runbook engine parses and returns the file during queries.

---

## 6. Administrator Guide

Platform administrators manage deployment pipelines, backups, database updates, and compliance tasks.

### Step 6.1: Database Backups
Execute a manual backup of TimescaleDB (uses compression & pg_dump custom format):
```bash
./scripts/backup.sh
```
*Backups are saved to `./backups/backup_YYYYMMDD_HHMMSS.sql`.*

### Step 6.2: Database Restoration
To restore a database snapshot:
```bash
./scripts/restore.sh ./backups/backup_YYYYMMDD_HHMMSS.sql
```
*Note: Make sure to validate the restored snapshot using the validation report tool:*
```bash
python3 scripts/backup-validation/validate.py
```

### Step 6.3: Upgrade Protocols
To perform system schema migrations:
1. Trigger the upgrade script:
   ```bash
   ./scripts/upgrade/upgrade.sh
   ```
   *This automatically creates a pre-upgrade backup file (`./backups/pre_upgrade_backup.sql`) before applying schema migrations.*
2. Check logs to ensure schema was updated cleanly.
3. If database errors arise, rollback to the pre-upgrade snapshot immediately:
   ```bash
   ./scripts/upgrade/rollback.sh
   ```

### Step 6.4: Running Security Audits
To inspect static security issues, packages compliance, and vulnerability logs:
```bash
./scripts/security-audit/audit.sh
```
This outputs a summary of findings to `security-audit-report.md`.

---

## 7. Air-Gap Deployment & Verification

Plutopus is designed to operate in fully offline, isolated enclaves.

### Step 7.1: Build the Offline Bundle (Connected Environment)
On an internet-connected build machine, compile all Docker images, scripts, Helm templates, and LLM assets:
```bash
./distribution/pack-offline-bundle.sh
```
This generates `plutopus-offline-bundle.tar.gz` and writes its checksum to `distribution/checksums/plutopus-offline-bundle.tar.gz.sha256`.

### Step 7.2: Import Model Layer on Target Host (Air-Gapped Environment)
1. Transfer the `.tar.gz` archive to your air-gapped machine.
2. Validate file integrity:
   ```bash
   sha256sum -c distribution/checksums/plutopus-offline-bundle.tar.gz.sha256
   ```
3. Extract the contents:
   ```bash
   tar -xzf plutopus-offline-bundle.tar.gz
   ```
4. Load the Docker images:
   ```bash
   docker load -i distribution/docker-images/plutopus_images.tar
   ```
5. Import the pre-downloaded Ollama LLM weight models:
   ```bash
   ./distribution/models/import-model.sh ./distribution/models/ollama_model_qwen_0.5b.tar
   ```

### Step 7.3: Boot Platform in Air-Gap Mode
1. Edit [.env](file:///Users/ayush/Desktop/pluto/.env.example) and set:
   ```env
   AIRGAP_MODE=true
   ```
2. Start the services:
   ```bash
   docker compose up -d
   ```

### Step 7.4: Run Isolation Auditing Script
Confirm the host is fully air-gapped and does not reach out to public network gateways:
```bash
./scripts/airgap/verify.sh
```
This script validates that:
- `AIRGAP_MODE` is enabled.
- External DNS/HTTP requests are blocked (timeout behaves as expected).
- Ollama uses only local storage volumes.
- It writes results to `airgap-report.md`.

---

## 8. Troubleshooting & Support

| Symptom | Cause | Solution |
|---|---|---|
| **API gateway fails to start with value errors** | `JWT_SECRET` is less than 32 characters. | Update `.env` and set `JWT_SECRET` to a string with at least 32 characters. |
| **Copilot returns structured context logs without text explanation** | Ollama LLM container is offline or connection timed out (4s). | Ensure the Ollama service is running (`docker compose logs ollama`). The platform safely uses the deterministic context fallback. |
| **No topology graphs rendering in the Dashboard** | The database has not been initialized with site coordinates. | Run `make seed-topology` in the project root to insert topology nodes. |
| **Telemetry metrics values not changing on Dashboard charts** | The simulated telemetry generator script is stopped. | Run `python3 scripts/generate-demo-telemetry.py` to stream continuous synthetic metrics. |
