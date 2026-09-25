# AI-SOC Platform

An AI-Powered Cybersecurity Operations Platform for educational purposes.

## Overview

**CURRENTLY IMPLEMENTED:**
- synthetic security log ingestion
- Neon PostgreSQL storage
- deterministic detection engine
- DET-001 through DET-005
- security alert generation and management
- deterministic incident correlation
- incident priority scoring
- incident management
- alert-to-incident relationships

**FUTURE:**
- SOC dashboard
- AI/RAG investigation
- human-approved remediation recommendations

## Services
- `apps/web`: Next.js Frontend
- `apps/api`: FastAPI Backend

## Database Setup
The platform uses Neon PostgreSQL for the database.
You must have a `.env` file at the root of the project with a valid `DATABASE_URL`.
Example:
`DATABASE_URL=postgresql://user:password@endpoint/dbname`

## Backend Startup
Run the backend server using uvicorn:
```bash
python -m uvicorn apps.api.main:app --reload --host 127.0.0.1 --port 8000
```

## Seed Command
To generate and insert synthetic security logs, run the seed script:
```bash
$env:PYTHONPATH="."; python apps/api/seed_logs.py
```

## APIs
The backend exposes the following API endpoints:

**Log APIs**
- `GET /api/v1/logs`: Fetch logs.
- `GET /api/v1/logs/{id}`: Fetch log by ID.

**Detection APIs**
- `POST /api/v1/detections/run`: Run detection rules over logs to generate alerts.
- `GET /api/v1/detection-rules`: List all loaded detection rules.

**Alert APIs**
- `GET /api/v1/alerts`: Fetch alerts (supports filtering by severity, status, rule_id).
- `GET /api/v1/alerts/{id}`: Fetch alert by ID.
- `PATCH /api/v1/alerts/{id}/status`: Update alert status.

**Correlation APIs**
- `GET /api/v1/correlation-rules`: List all loaded correlation rules.
- `POST /api/v1/correlations/run`: Run correlation rules over unassigned alerts.

**Incident APIs**
- `GET /api/v1/incidents`: Fetch incidents.
- `GET /api/v1/incidents/{id}`: Fetch incident by ID.
- `PATCH /api/v1/incidents/{id}/status`: Update incident status.

## Current Status
- Phase 1: Foundation (COMPLETE)
- Phase 2: Log Ingestion (COMPLETE)
- Phase 3: Detection Engine + Alerts (COMPLETE)
- Phase 4: Incident Correlation (COMPLETE)
- Phase 5: Dashboard (NOT STARTED)
- Phase 6: AI Investigator / RAG (NOT STARTED)
