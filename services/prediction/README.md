# Plutopus Predictive Analytics Engine

This service implements time-series forecasting, statistical anomaly detection, tunnel/site risk scoring, and explainable correlation signals.

## Directory Structure
- `forecasting/`: Code for statistical metric forecasting (15m, 30m, 60m windows).
- `anomaly/`: Time-series anomaly classifiers (Z-score thresholds).
- `risk/`: Scores tunnels and sites on a 0-100 hazard scale.
- `correlation/`: Mappings indicating which telemetry streams contribute most to elevated risk levels (the explainability signals layer).
- `models/`: Placeholders for trained scikit-learn or statistical forecast objects.
- `api/`: Endpoint controller definitions (mirrored to FastAPI main).
