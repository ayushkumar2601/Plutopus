import pytest
from fastapi.testclient import TestClient
import sys
import os

# Adjust paths to make sure we can import main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from main import app

client = TestClient(app)

def test_root_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_v1_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
