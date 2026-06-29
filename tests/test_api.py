import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../packages/shared/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/api/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/topology")))

from plutopus_shared.db import get_db, Base
from seed import seed_topology
from main import app

DB_FILE = "test_api.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# Setup local SQLite test db file
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Remove old test db if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_topology(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    
    # Cleanup DB file
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except Exception:
            pass

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}

def test_api_v1_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}

def test_api_get_sites():
    res = client.get("/api/v1/sites/")
    assert res.status_code == 200
    assert len(res.json()) == 4

def test_api_get_devices():
    res = client.get("/api/v1/devices/")
    assert res.status_code == 200
    assert len(res.json()) == 4

def test_api_get_tunnels():
    res = client.get("/api/v1/tunnels/")
    assert res.status_code == 200
    assert len(res.json()) == 6

def test_api_get_topology():
    res = client.get("/api/v1/topology/")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "links" in data
    # 4 sites + 4 devices = 8 nodes
    assert len(data["nodes"]) == 8
    # 4 device-site links + 6 tunnels = 10 links
    assert len(data["links"]) == 10
