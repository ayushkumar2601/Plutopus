# Production Readiness Review (PRR) - Plutopus

This review documents the security posture, operational procedures, backup policies, and monitoring metrics for deploying Plutopus as a pilot platform in a Production Network Operations Center (NOC).

---

## 1. Security & Hardening Posture
- **Access Controls**: Role-Based Access Control (RBAC) is enforced at the API gateway layer via JWT access tokens. Users carry one of three distinct roles: `admin`, `operator`, or `viewer`.
- **CORS & Headers**: Strict CORS origin configuration is defined using environment variables (`BACKEND_CORS_ORIGINS`). Content Security Policy (CSP) and Secure Transport headers are enforced.
- **Input Validation**: All FastAPI controllers leverage Pydantic models to validate incoming JSON payloads, preventing injection attacks.

---

## 2. Observability & Monitoring
- **Prometheus Exporter**: Extends standard Prometheus metrics mapping:
  - `api_requests_total`: Tracks requests by path, method, and HTTP status code.
  - `api_request_latency_seconds`: Tracks latencies across API router gateways.
  - `incidents_generated_total`: Monitors alarm correlation frequency.
  - `webhook_delivery_total`: Tracks status of outbound exports.
- **Grafana Dashboard Layouts**: Exported configurations are versioned under `infrastructure/monitoring/grafana/dashboards/`.

---

## 3. High Availability & Recovery
- **Database Backups**: Automated backups are scheduled via `scripts/backup.sh` mapping outputs to persistent volumes.
- **Service Recovery**: Docker Compose configurations feature `restart: unless-stopped` with health and liveness checks ensuring automatic container recovery.
