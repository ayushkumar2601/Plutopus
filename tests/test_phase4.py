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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/copilot")))

from plutopus_shared.db import get_db, Base
from plutopus_shared.models import Site, Device, Interface, Tunnel, Metric, Event, Forecast, Anomaly, RiskScore
from seed import seed_topology
from context.engine import CopilotContextEngine
from context.summarizer import CopilotIncidentSummarizer
from retrieval import CopilotRetrievalService
from memory import CopilotMemoryManager
from llm import call_ollama, generate_fallback_response
from prompts import SYSTEM_PROMPT, ANALYST_TEMPLATE
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
    
    # Seed predictions and risks for site and tunnels
    now = datetime.utcnow()
    db.add(RiskScore(
        entity_id="site-branch-06",
        entity_type="site",
        risk_score=90,
        risk_level="high",
        signals=json.dumps([{"metric": "degraded_tunnels", "impact": 60}]),
        timestamp=now
    ))
    db.add(RiskScore(
        entity_id="tun-br06-hub-mpls",
        entity_type="tunnel",
        risk_score=85,
        risk_level="high",
        signals=json.dumps([{"metric": "packet_loss", "impact": 40}]),
        timestamp=now
    ))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_context_engine():
    db = TestingSessionLocal()
    try:
        ctx_eng = CopilotContextEngine(db)
        
        site_ctx = ctx_eng.get_site_context("site-branch-06")
        assert site_ctx["site_id"] == "site-branch-06"
        assert site_ctx["risk_score"] == 90
        assert site_ctx["risk_level"] == "high"

        tun_ctx = ctx_eng.get_tunnel_context("tun-br06-hub-mpls")
        assert tun_ctx["tunnel_id"] == "tun-br06-hub-mpls"
        assert tun_ctx["risk_score"] == 85
    finally:
        db.close()

def test_incident_summarizer():
    db = TestingSessionLocal()
    try:
        summarizer = CopilotIncidentSummarizer(db)
        
        site_summary = summarizer.summarize_site_incident("site-branch-06")
        assert "Site Summary" in site_summary
        assert "90" in site_summary
        
        tun_summary = summarizer.summarize_tunnel_incident("tun-br06-hub-mpls")
        assert "Tunnel Summary" in tun_summary
        assert "85" in tun_summary
    finally:
        db.close()

def test_retrieval_and_parsing():
    runbooks = CopilotRetrievalService.get_relevant_runbooks("latency check on mpls link")
    assert "high_latency.md" in runbooks
    
    site_id, tunnel_id = CopilotRetrievalService.extract_entity_ids("why is site-branch-06 offline?")
    assert site_id == "site-branch-06"
    assert tunnel_id is None

def test_memory_manager():
    mem = CopilotMemoryManager()
    mem.add_message("session-abc", "user", "hello")
    mem.add_message("session-abc", "copilot", "hi there")
    
    hist = mem.get_history("session-abc")
    assert len(hist) == 2
    assert hist[0]["role"] == "user"
    assert hist[0]["content"] == "hello"

def test_llm_and_safety_fallback():
    # Verify fallback response builder
    context = {"site_id": "site-01", "name": "Site 01", "risk_score": 80, "risk_level": "high"}
    fallback = generate_fallback_response("Why is site-01 at risk?", context, "High latency runbook info")
    assert "Fallback Grounded Mode" in fallback
    assert "Site `site-01`" in fallback
    assert "High latency runbook info" in fallback

def test_copilot_api_endpoints():
    # Chat endpoint
    res_chat = client.post("/api/v1/copilot/chat", json={"query": "Why is site-branch-06 at risk?"})
    assert res_chat.status_code == 200
    data_chat = res_chat.json()
    assert "answer" in data_chat
    assert "confidence" in data_chat

    # Explain endpoint
    res_explain = client.post("/api/v1/copilot/explain", json={"site_id": "site-branch-06"})
    assert res_explain.status_code == 200
    data_explain = res_explain.json()
    assert data_explain["entity_id"] == "site-branch-06"
    assert data_explain["risk_score"] == 90

    # Incident summary endpoint
    res_summary = client.post("/api/v1/copilot/incident-summary")
    assert res_summary.status_code == 200
    data_summary = res_summary.json()
    assert data_summary["count"] == 1
    assert "branch office 06" in data_summary["summary"].lower()

def test_additional_copilot_coverage():
    # 1. Chat with tunnel query
    res = client.post("/api/v1/copilot/chat", json={"query": "Why is tun-br06-hub-mpls offline?"})
    assert res.status_code == 200
    assert "tun-br06-hub-mpls" in res.json()["sources"][0]

    # 2. Chat with generic query
    res_gen = client.post("/api/v1/copilot/chat", json={"query": "Hello network analyst!"})
    assert res_gen.status_code == 200
    assert "Global Network Registry" in res_gen.json()["sources"]

    # 3. Explain tunnel endpoint
    res_exp = client.post("/api/v1/copilot/explain", json={"tunnel_id": "tun-br06-hub-mpls"})
    assert res_exp.status_code == 200
    assert res_exp.json()["entity_id"] == "tun-br06-hub-mpls"

    # 4. Explain empty bad request
    res_bad = client.post("/api/v1/copilot/explain", json={})
    assert res_bad.status_code == 400

    # 5. Summarizer invalid entities
    db = TestingSessionLocal()
    try:
        summarizer = CopilotIncidentSummarizer(db)
        assert "not found" in summarizer.summarize_site_incident("invalid-site")
        assert "not found" in summarizer.summarize_tunnel_incident("invalid-tunnel")
        
        # Site with no risk signals (healthy site)
        assert "None" in summarizer.summarize_site_incident("site-hub")
    finally:
        db.close()

    # 6. Fallback response for tunnel context
    tun_ctx = {"tunnel_id": "tun-01", "status": "down", "risk_score": 100, "risk_level": "high", "metrics": {"latency": 150, "packet_loss": 10}}
    fallback = generate_fallback_response("Is tunnel 01 down?", tun_ctx, "Re-negotiate IKE SA")
    assert "Tunnel `tun-01`" in fallback
    assert "Re-negotiate IKE SA" in fallback

    # 7. Keyword mappings checks
    assert "packet_loss.md" in CopilotRetrievalService.get_relevant_runbooks("packet loss burst")
    assert "tunnel_failure.md" in CopilotRetrievalService.get_relevant_runbooks("tunnel is down")
    assert "congestion.md" in CopilotRetrievalService.get_relevant_runbooks("congestion on wan link")
    assert "interface_flapping.md" in CopilotRetrievalService.get_relevant_runbooks("interface flap detected")
    assert "route_instability.md" in CopilotRetrievalService.get_relevant_runbooks("routing instability alert")

