import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi.testclient import TestClient
from apps.api.main import app

# Ensure tables are created (app startup handles this)
client = TestClient(app)

print("--- 1. POST /api/v1/detections/run ---")
res_det = client.post("/api/v1/detections/run")
print(res_det.json())

print("--- 2. GET /api/v1/alerts ---")
res_alerts = client.get("/api/v1/alerts")
alerts_data = res_alerts.json()
print("Total alerts:", alerts_data.get("total", 0))

print("--- 3. POST /api/v1/correlations/run ---")
res_corr = client.post("/api/v1/correlations/run")
print(res_corr.status_code)
print(res_corr.json())

print("--- 4. GET /api/v1/incidents ---")
res_incidents = client.get("/api/v1/incidents")
print(res_incidents.status_code)
print(res_incidents.json())
