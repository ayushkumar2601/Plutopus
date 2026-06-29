# Compliance Readiness Documentation - Plutopus

This document specifies the operational compliance parameters for running the Plutopus platform in regulated air-gapped environments.

---

## 1. System Logging and Audit Trails (AU-2)
- **Immutable Log Store**: The `audit_logs` database table persists all identity events, credential verifications, and export tasks.
- **Log Parameters**: Tracks timestamp, unique username, specific task action, resource ID, request status, and source IP address.

---

## 2. Boundary Protection and Isolation (SC-7)
- **Network Isolation Policies**: Establishes egress constraints and limits SQL database connections exclusively to Authorized API Gateway pods.
- **Air-Gap Operational Mode**: When the `AIRGAP_MODE=true` environment flag is active, outbound updates, telemetry metrics feeds, and remote AI model downloads are disabled.

---

## 3. Data Protection (MP-6)
- **Encryption in Transit**: All endpoints should be bound to TLS 1.3 reverse proxy ingress points (e.g. Nginx Ingress Controller).
- **Data Backups (CP-9)**: Database state dumps are written to secure local directories and validated daily.
