import os
import pytest

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    pytest.skip("TEST_DATABASE_URL is not set. Skipping detection integration tests.", allow_module_level=True)
else:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from fastapi.testclient import TestClient
from apps.api.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_run_detections_twice(client):
    # First run
    res1 = client.post("/api/v1/detections/run")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["alerts_created"] > 0

    # Second run
    res2 = client.post("/api/v1/detections/run")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["alerts_created"] == 0
    assert data2["duplicates_skipped"] > 0

def test_get_alerts(client):
    res = client.get("/api/v1/alerts")
    assert res.status_code == 200
    assert "alerts" in res.json()

def test_get_alert_by_id_and_patch(client):
    res = client.get("/api/v1/alerts?limit=1")
    assert res.status_code == 200
    alerts = res.json().get("alerts", [])
    if alerts:
        alert_id = alerts[0]["id"]
        
        # GET /api/v1/alerts/{id}
        res2 = client.get(f"/api/v1/alerts/{alert_id}")
        assert res2.status_code == 200
        
        # PATCH alert status
        res3 = client.patch(f"/api/v1/alerts/{alert_id}/status", json={"status": "investigating"})
        assert res3.status_code == 200
        assert res3.json()["status"] == "investigating"

def test_get_nonexistent_alert(client):
    res = client.get("/api/v1/alerts/999999")
    assert res.status_code == 404

def test_patch_invalid_status(client):
    res = client.get("/api/v1/alerts?limit=1")
    alerts = res.json().get("alerts", [])
    if alerts:
        alert_id = alerts[0]["id"]
        res = client.patch(f"/api/v1/alerts/{alert_id}/status", json={"status": "invalid_status"})
        assert res.status_code == 422

def test_filtering(client):
    res1 = client.get("/api/v1/alerts?severity=high")
    assert res1.status_code == 200
    res1_c = client.get("/api/v1/alerts?severity=critical")
    assert res1_c.status_code == 200
    res2 = client.get("/api/v1/alerts?status=open")
    assert res2.status_code == 200
    res3 = client.get("/api/v1/alerts?rule_id=DET-001")
    assert res3.status_code == 200
