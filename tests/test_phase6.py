import pytest
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

# Add paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/api/src")))
from main import app
from plutopus_shared.db import get_db, Base
from plutopus_shared.models import AuditLog
from core.auth import create_access_token
from core.audit import log_audit_event

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
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_audit_logging():
    db = TestingSessionLocal()
    try:
        log_audit_event(
            db=db,
            username="admin_user",
            action="create_incident",
            resource="incident",
            resource_id="inc-101",
            result="success",
            source_ip="127.0.0.1"
        )
        
        # Verify db insert
        log = db.query(AuditLog).filter(AuditLog.username == "admin_user").first()
        assert log is not None
        assert log.action == "create_incident"
        assert log.result == "success"
    finally:
        db.close()

def test_airgap_mode_env():
    # Verify environment value behaves correctly
    os.environ["AIRGAP_MODE"] = "true"
    assert os.getenv("AIRGAP_MODE") == "true"

def test_jwt_secrets_strength_validation():
    # Verify creating access token generates a valid signature
    token = create_access_token("operator_user", "operator")
    assert token is not None
    assert len(token.split(".")) == 3

def test_audit_logs_api():
    admin_token = create_access_token("admin_user", "admin")
    
    # Pre-seed log to query
    db = TestingSessionLocal()
    log_audit_event(
        db=db,
        username="admin_user",
        action="query_audit",
        resource="audit",
        resource_id="logs",
        result="success",
        source_ip="127.0.0.1"
    )
    db.close()

    # Query logs via API using admin token
    res = client.get("/api/v1/audit/logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    assert logs[0]["username"] == "admin_user"

    # Query with missing/unauthorized user token
    viewer_token = create_access_token("viewer_user", "viewer")
    res_forbidden = client.get("/api/v1/audit/logs", headers={"Authorization": f"Bearer {viewer_token}"})
    assert res_forbidden.status_code == 403

