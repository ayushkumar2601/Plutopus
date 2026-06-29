# Platform Scaling & Capacity Planning - Plutopus

This guide details resources, CPU, Memory, and Storage guidelines for running Plutopus at scale.

---

## Resource Requirements Matrix

| Device Scale | CPU (Cores) | Memory (RAM) | Storage (SSD) | Telemetry Worker Replicas | Prediction Workers |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **100 Devices** | 4 Cores | 8 GiB | 50 GiB | 1 | 1 |
| **500 Devices** | 8 Cores | 16 GiB | 250 GiB | 2 | 2 |
| **1000 Devices** | 16 Cores | 32 GiB | 500 GiB | 4 | 4 |
| **5000 Devices** | 32 Cores | 64 GiB | 2.5 TiB | 8 | 8 |

---

## Workload Sizing & Scaling Recommendations

### Telemetry Workers
- **Bottle Neck**: Network I/O and Redpanda offset commits.
- **Scaling Threshold**: Increase replicas by 1 for every 500 metrics/sec.

### Prediction Workers
- **Bottle Neck**: Memory size during linear regressions and CPU during multi-step forecasts.
- **Scaling Threshold**: Scale out when queue delay for predictions exceeds 2 minutes.

### Database Layer (TimescaleDB)
- Enforce standard postgres table partitioning. For 5000+ devices, configure TimescaleDB chunk sizes of 1 day to keep indexes in memory.
