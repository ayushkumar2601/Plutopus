import pytest
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/telemetry/src")))

from normalizers import normalize_metric, normalize_event

def test_normalize_valid_metric():
    payload = {
        "target_id": "int-br01-mpls",
        "name": "utilization",
        "value": 45.2,
        "timestamp": "2026-06-29T21:00:00+00:00"
    }
    res = normalize_metric(payload)
    assert res is not None
    assert res["target_id"] == "int-br01-mpls"
    assert res["name"] == "utilization"
    assert res["value"] == 45.2
    assert isinstance(res["timestamp"], datetime)

def test_normalize_invalid_metric():
    # Missing value
    payload = {
        "target_id": "int-br01-mpls",
        "name": "utilization"
    }
    assert normalize_metric(payload) is None

def test_normalize_valid_event():
    payload = {
        "device_id": "dev-br01-edge",
        "severity": "critical",
        "message": "Keepalive loss detected",
        "timestamp": "2026-06-29T21:00:00+00:00"
    }
    res = normalize_event(payload)
    assert res is not None
    assert res["device_id"] == "dev-br01-edge"
    assert res["severity"] == "critical"
    assert res["message"] == "Keepalive loss detected"
    assert isinstance(res["timestamp"], datetime)

def test_normalize_invalid_event():
    # Missing device_id
    payload = {
        "severity": "warning",
        "message": "Flapping link"
    }
    assert normalize_event(payload) is None
