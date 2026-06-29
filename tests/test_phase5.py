import pytest
import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# 1. Add api and topology paths first
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/api/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/topology")))
from main import app

# 2. Add other paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/correlation")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/integrations")))

from plutopus_shared.db import get_db, Base
from plutopus_shared.models import Site, Device, Interface, Tunnel, Metric, Event, Forecast, Anomaly, RiskScore, Incident
from seed import seed_topology
from core.auth import create_access_token
from engine import EventCorrelationEngine
from prioritization import AlertPrioritizationEngine
from webhooks import WebhookIntegrationService
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
    
    # Configure business criticality to test prioritization weights
    hub = db.query(Site).filter(Site.id == "site-hub").first()
    if hub:
        hub.business_criticality = "mission_critical"
    branch = db.query(Site).filter(Site.id == "site-branch-06").first()
    if branch:
        branch.business_criticality = "high"

    # Seed overlapping anomalies to trigger correlation
    now = datetime.utcnow()
    db.add(Anomaly(
        entity_id="tun-br06-hub-mpls",
        entity_type="tunnel",
        metric="latency",
        severity="critical",
        score=4.5,
        description="High Z-score spike on hub link tunnel"
    ))
    db.add(Anomaly(
        entity_id="site-branch-06",
        entity_type="site",
        metric="latency",
        severity="critical",
        score=3.8,
        description="High latency observed at branch 06"
    ))
    db.add(Anomaly(
        entity_id="site-branch-05",
        entity_type="site",
        metric="latency",
        severity="critical",
        score=3.5,
        description="High latency observed at branch 05"
    ))
    db.add(Anomaly(
        entity_id="site-branch-06",
        entity_type="site",
        metric="utilization",
        severity="warning",
        score=2.8,
        description="High link utilization at branch 06"
    ))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_event_correlation():
    db = TestingSessionLocal()
    try:
        engine = EventCorrelationEngine(db)
        correlated = engine.run_correlation()
        assert len(correlated) > 0
        assert "hub link" in correlated[0]["title"].lower()
        
        # Check database entry
        incident = db.query(Incident).filter(Incident.root_cause == "tun-br06-hub-mpls").first()
        assert incident is not None
        assert incident.status == "active"
    finally:
        db.close()

def test_alert_prioritization():
    # Priority for mission critical site
    res_crit = AlertPrioritizationEngine.calculate_priority(
        risk_score=95,
        confidence=0.92,
        time_to_impact_mins=10,
        business_criticality="mission_critical",
        affected_nodes_count=4
    )
    assert res_crit["priority"] >= 80
    assert res_crit["level"] == "critical"

    # Priority for low site
    res_low = AlertPrioritizationEngine.calculate_priority(
        risk_score=20,
        confidence=0.80,
        time_to_impact_mins=90,
        business_criticality="low",
        affected_nodes_count=1
    )
    assert res_low["priority"] < 35
    assert res_low["level"] == "low"

def test_jwt_auth_and_rbac():
    # Generate admin token
    admin_token = create_access_token("admin_user", "admin")
    
    # Try calling secured incidents endpoint without token (should fail with 401)
    res_fail = client.get("/api/v1/incidents")
    assert res_fail.status_code == 401

    # Call with admin token (should succeed with 200)
    res_ok = client.get(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_ok.status_code == 200

    # Generate viewer token
    viewer_token = create_access_token("viewer_user", "viewer")

    # Try calling trigger correlation (requires operator/admin, should fail with 403)
    res_forbidden = client.get(
        "/api/v1/incidents/correlated",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res_forbidden.status_code == 403

    # Call trigger correlation with admin token (should succeed with 200)
    res_correlated = client.get(
        "/api/v1/incidents/correlated",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_correlated.status_code == 200
    assert len(res_correlated.json()) > 0
    assert res_forbidden.status_code == 403

def test_outbound_webhook_retry():
    # Dispatch webhook to invalid listener URL, verify retry execution logs false safely
    payload = {"event": "test"}
    success = WebhookIntegrationService.dispatch_webhook("http://localhost:54321/invalid", payload, retries=2, backoff=0.01)
    assert success is False

def test_prometheus_endpoint():
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "api_requests_total" in res.text

def test_incidents_detail_and_export(monkeypatch):
    admin_token = create_access_token("admin", "admin")
    
    # 1. Fetch listing with status filter
    res = client.get("/api/v1/incidents?status=active", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    inc_list = res.json()
    assert len(inc_list) > 0
    inc_id = inc_list[0]["id"]
    
    # 2. Fetch specific incident by ID
    res_det = client.get(f"/api/v1/incidents/{inc_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_det.status_code == 200
    assert res_det.json()["id"] == inc_id

    # 3. Fetch non-existent incident
    res_bad = client.get("/api/v1/incidents/invalid-incident-uuid", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_bad.status_code == 404

    # 4. Export incident with mock success
    monkeypatch.setattr(WebhookIntegrationService, "dispatch_webhook", lambda *a, **k: True)
    res_exp = client.post(
        "/api/v1/incidents/export",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"incident_id": inc_id, "target_url": "http://localhost:54321/web"}
    )
    assert res_exp.status_code == 200
    assert res_exp.json()["status"] == "exported"

    # 5. Export non-existent incident
    res_exp_bad = client.post(
        "/api/v1/incidents/export",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"incident_id": "invalid-uuid", "target_url": "http://localhost:54321/web"}
    )
    assert res_exp_bad.status_code == 404

def test_inbound_webhooks():
    # 1. Valid inbound alert webhook
    res = client.post(
        "/api/v1/incidents/integrations/webhook",
        json={
            "source": "solarwinds",
            "message": "Chassis fan failure warning",
            "severity": "warning",
            "device_id": "dev-br01-edge"
        }
    )
    assert res.status_code == 200
    assert res.json()["status"] == "received"

    # 2. Invalid device target
    res_bad = client.post(
        "/api/v1/incidents/integrations/webhook",
        json={
            "source": "solarwinds",
            "message": "General failure",
            "severity": "critical",
            "device_id": "nonexistent-device"
        }
    )
    assert res_bad.status_code == 404

