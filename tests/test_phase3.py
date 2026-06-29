import pytest
import os
import sys
import json
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# 1. Add api and topology paths first, then import API app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/api/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/topology")))
from main import app

# 2. Add other paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../packages/shared/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/topology")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/prediction")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/prediction/src")))

from plutopus_shared.db import get_db, Base
from plutopus_shared.models import Site, Device, Interface, Tunnel, Metric, Event, Forecast, Anomaly, RiskScore
from seed import seed_topology
from forecasting import forecast_metric, fit_linear_trend
from anomaly import detect_anomaly, calculate_z_score
from risk import calculate_tunnel_risk, calculate_site_risk
from correlation import RiskCorrelationEngine

# Import prediction worker to run the pipeline
from worker import run_prediction_pipeline

from sqlalchemy.pool import StaticPool

# Setup local SQLite test db in-memory shared pool
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_topology(db)
    
    # Add historical metrics to trigger forecasts/anomalies in worker
    now = datetime.utcnow()
    # Add 10 metrics for int-br01-mpls utilization
    for i in range(9):
        db.add(Metric(
            target_id="int-br01-mpls",
            name="utilization",
            value=30.0 + i * 2.0,
            timestamp=now
        ))
        db.add(Metric(
            target_id="tun-br01-hub-mpls",
            name="latency",
            value=40.0 + i,
            timestamp=now
        ))
        db.add(Metric(
            target_id="tun-br01-hub-mpls",
            name="packet_loss",
            value=0.1,
            timestamp=now
        ))
    
    # 10th records (sharp anomalies)
    db.add(Metric(target_id="int-br01-mpls", name="utilization", value=99.0, timestamp=now))
    db.add(Metric(target_id="tun-br01-hub-mpls", name="latency", value=250.0, timestamp=now))
    db.add(Metric(target_id="tun-br01-hub-mpls", name="packet_loss", value=8.5, timestamp=now))
    
    # Seed critical device warning
    db.add(Event(device_id="dev-br01-edge", severity="critical", message="Power supply failure detected.", timestamp=now))
        
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_forecasting_logic():
    # Linear fit test
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [10.0, 20.0, 30.0, 40.0, 50.0]
    alpha, beta = fit_linear_trend(x, y)
    assert beta == 10.0
    assert alpha == 0.0

    # Projection test
    hist_vals = [50.0, 55.0, 60.0]
    hist_times = [1000.0, 2000.0, 3000.0]
    res = forecast_metric(hist_vals, hist_times, 3000.0)
    assert res["current"] == 60.0
    assert res["forecast_15m"] > 60.0
    assert res["confidence"] == 0.85

def test_anomaly_detection_logic():
    # Normal state check
    hist = [10.0, 11.0, 10.5, 9.8, 10.2]
    assert calculate_z_score(10.1, hist) < 1.0
    
    # Anomaly spike check
    anom = detect_anomaly("intf-01", "interface", "utilization", 85.0, hist)
    assert anom is not None
    assert anom["severity"] == "critical"
    assert "spike" in anom["description"]

def test_risk_calculations():
    # Tunnel low risk
    r_low = calculate_tunnel_risk("tun-01", 20.0, 0.0, 40.0)
    assert r_low["risk_score"] == 0
    assert r_low["risk_level"] == "low"
    
    # Tunnel high risk
    r_high = calculate_tunnel_risk("tun-01", 150.0, 8.0, 95.0)
    assert r_high["risk_score"] > 50
    assert "packet_loss" in r_high["signals"]
    assert "high_latency" in r_high["signals"]

    # Site risk aggregation
    site_r = calculate_site_risk("site-01", [80, 40], 5, False)
    assert site_r["risk_score"] > 30
    assert "alarm_events_spike" in site_r["signals"]

def test_explainability_correlation():
    contributions = RiskCorrelationEngine.get_contributing_signals(
        "tunnel", 80, ["packet_loss", "high_latency"]
    )
    assert len(contributions) == 2
    assert contributions[0]["metric"] == "packet_loss"
    assert contributions[0]["impact"] == 40

def test_prediction_worker_pipeline():
    # Execute one iteration of background pipeline using test session
    db = TestingSessionLocal()
    try:
        run_prediction_pipeline(db)
        
        # Check that forecast runs were persisted
        f_count = db.query(Forecast).count()
        assert f_count > 0
        
        # Check that risk score evaluations were persisted
        r_count = db.query(RiskScore).count()
        assert r_count > 0
    finally:
        db.close()

def test_prediction_api_endpoints():
    # Verify predictions fetch
    res = client.get("/api/v1/predictions")
    assert res.status_code == 200
    assert len(res.json()) > 0
    
    # Verify site predictions fetch
    res_sites = client.get("/api/v1/predictions/sites")
    assert res_sites.status_code == 200
    
    # Verify tunnel predictions fetch
    res_tunnels = client.get("/api/v1/predictions/tunnels")
    assert res_tunnels.status_code == 200
    
    # Verify anomalies fetch
    res_anom = client.get("/api/v1/anomalies")
    assert res_anom.status_code == 200
    
    # Verify risk logs fetch
    res_risk = client.get("/api/v1/risk")
    assert res_risk.status_code == 200
    
    # Verify specific forecast lookup
    res_forecast = client.get("/api/v1/forecast?target_id=int-br01-mpls&metric=utilization")
    assert res_forecast.status_code == 200
    assert res_forecast.json()["target_id"] == "int-br01-mpls"

def test_pipeline_exception_handling():
    class MockSession:
        def query(self, *args, **kwargs):
            raise Exception("Mock query failure")
        def rollback(self):
            pass
            
    run_prediction_pipeline(MockSession())
