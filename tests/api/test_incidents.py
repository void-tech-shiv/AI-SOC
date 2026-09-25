import os
import pytest

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    pytest.skip("TEST_DATABASE_URL is not set. Skipping incident integration tests.", allow_module_level=True)
else:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from fastapi.testclient import TestClient
from apps.api.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_run_correlation(client):
    # Ensure there are some alerts first
    res_det = client.post("/api/v1/detections/run")
    assert res_det.status_code == 200
    
    # Run correlation
    res_corr = client.post("/api/v1/correlations/run")
    assert res_corr.status_code == 200
    data_corr = res_corr.json()
    assert data_corr["incidents_created"] >= 0
    assert "standalone_incidents_created" in data_corr

def test_get_incidents(client):
    res = client.get("/api/v1/incidents")
    assert res.status_code == 200
    assert "incidents" in res.json()
    assert "total" in res.json()

def test_get_incident_by_id_and_patch(client):
    res = client.get("/api/v1/incidents?limit=1")
    assert res.status_code == 200
    incidents = res.json().get("incidents", [])
    if incidents:
        incident_id = incidents[0]["id"]
        
        # GET /api/v1/incidents/{id}
        res2 = client.get(f"/api/v1/incidents/{incident_id}")
        assert res2.status_code == 200
        
        # PATCH incident status
        res3 = client.patch(f"/api/v1/incidents/{incident_id}/status", json={"status": "investigating"})
        assert res3.status_code == 200
        assert res3.json()["status"] == "investigating"

def test_get_incident_alerts(client):
    res = client.get("/api/v1/incidents?limit=1")
    assert res.status_code == 200
    incidents = res.json().get("incidents", [])
    if incidents:
        incident_id = incidents[0]["id"]
        
        # GET alerts for incident
        res2 = client.get(f"/api/v1/incidents/{incident_id}/alerts")
        assert res2.status_code == 200
        assert isinstance(res2.json(), list)

def test_filtering(client):
    res1 = client.get("/api/v1/incidents?severity=high")
    assert res1.status_code == 200
    res2 = client.get("/api/v1/incidents?status=open")
    assert res2.status_code == 200
    res3 = client.get("/api/v1/incidents?min_priority=50")
    assert res3.status_code == 200
