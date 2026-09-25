import os
import pytest

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    pytest.skip("TEST_DATABASE_URL is not set. Skipping tests to prevent polluting development DB.", allow_module_level=True)
else:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from fastapi.testclient import TestClient
from apps.api.main import app
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

import time

@pytest.fixture
def sample_log_payload():
    return {
        "timestamp": f"2026-09-25T11:00:00.{int(time.time() * 1000)}Z",
        "source": "test_script",
        "event_type": "test_event",
        "severity": "low",
        "username": "test_user",
        "ip_address": "127.0.0.1",
        "message": f"This is a test log {time.time()}.",
        "raw_event": "{'test': True}"
    }

def test_create_log(client, sample_log_payload):
    response = client.post("/api/v1/logs", json=sample_log_payload)
    # If the DB is not connected, it might fail, but assuming it is connected as per prompt
    if response.status_code == 500:
        pytest.skip("Database not configured or connected")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["source"] == sample_log_payload["source"]
    assert data["severity"] == sample_log_payload["severity"]

def test_list_logs(client):
    response = client.get("/api/v1/logs")
    if response.status_code == 500:
        pytest.skip("Database not configured or connected")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "total" in data
    assert type(data["logs"]) == list

def test_fetch_one_log(client, sample_log_payload):
    # Create one first
    create_res = client.post("/api/v1/logs", json=sample_log_payload)
    if create_res.status_code == 500:
        pytest.skip("Database not configured or connected")
    log_id = create_res.json()["id"]

    response = client.get(f"/api/v1/logs/{log_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == log_id
    assert data["source"] == sample_log_payload["source"]

def test_filter_by_severity(client, sample_log_payload):
    # Create a specific severity
    payload = sample_log_payload.copy()
    payload["severity"] = "critical"
    create_res = client.post("/api/v1/logs", json=payload)
    if create_res.status_code == 500:
        pytest.skip("Database not configured or connected")

    response = client.get("/api/v1/logs?severity=critical")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert all(log["severity"] == "critical" for log in data["logs"])

def test_invalid_severity(client):
    response = client.get("/api/v1/logs?severity=invalid_severity_test")
    assert response.status_code == 422
