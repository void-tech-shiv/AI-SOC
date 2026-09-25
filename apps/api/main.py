import os
import random
import asyncio
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv, find_dotenv
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from apps.api.models import Base, SecurityLog
from apps.api.schemas import SecurityLogCreate, SecurityLogResponse, SecurityLogListResponse
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from apps.api.database import (
    engine,
    get_db,
    check_db_connection,
    db_configured,
)

app = FastAPI(title="AI SOC Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from apps.api.detection import router as detection_router
app.include_router(detection_router)

@app.on_event("startup")
async def startup():
    from apps.api.database import db_connected
    db_connected = await check_db_connection()
    if db_connected and engine:
        print("Database connected successfully.")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        print("Starting without DB connection.")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/v1/status")
async def api_status():
    # 6. Make /api/v1/status use the same DB check logic dynamically
    is_connected = await check_db_connection()
    return {
        "status": "operational",
        "message": "AI-SOC Backend is running smoothly",
        "database_configured": db_configured,
        "database_connected": is_connected
    }

@app.get("/api/metrics", response_model=dict)
@app.get("/api/v1/metrics", response_model=dict)
async def get_metrics():
    threats = [
        {"id": "TH-001", "type": "Malware Detection", "confidence": random.uniform(85.0, 99.9), "timestamp": datetime.now().isoformat()},
        {"id": "TH-002", "type": "Phishing Attempt", "confidence": random.uniform(60.0, 80.0), "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat()},
        {"id": "TH-003", "type": "Anomalous Login", "confidence": random.uniform(90.0, 98.5), "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat()},
        {"id": "TH-004", "type": "Data Exfiltration", "confidence": random.uniform(70.0, 95.0), "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat()}
    ]
    
    system_load = {
        "cpu_usage_percent": random.uniform(30.0, 85.0),
        "memory_usage_percent": random.uniform(40.0, 75.0),
        "network_traffic_mbps": random.uniform(100.0, 1000.0),
        "active_connections": random.randint(500, 5000)
    }
    
    events = [
        {"event_id": "EVT-1042", "description": "Unusual outbound traffic spike detected on port 443", "severity": "High"},
        {"event_id": "EVT-1043", "description": "Multiple failed SSH login attempts from unknown IP", "severity": "Medium"},
        {"event_id": "EVT-1044", "description": "Database access patterns deviate from baseline", "severity": "High"}
    ]
    
    active_tasks = random.randint(12, 45)
    
    return {
        "threat_confidence_scores": threats,
        "system_load": system_load,
        "anomalous_events_detected": events,
        "active_ai_analysis_tasks": active_tasks
    }

@app.post("/api/v1/logs", response_model=SecurityLogResponse)
async def create_log(log_in: SecurityLogCreate, db: AsyncSession = Depends(get_db)):
    db_log = SecurityLog(**log_in.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

from apps.api.schemas import SecurityLogCreate, SecurityLogResponse, SecurityLogListResponse, SeverityLevel

@app.get("/api/v1/logs", response_model=SecurityLogListResponse)
async def list_logs(
    severity: SeverityLevel = Query(None),
    event_type: str = None,
    source: str = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(SecurityLog)
    if severity:
        query = query.filter(SecurityLog.severity == severity)
    if event_type:
        query = query.filter(SecurityLog.event_type == event_type)
    if source:
        query = query.filter(SecurityLog.source == source)
    
    query = query.order_by(SecurityLog.timestamp.desc()).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    return {"logs": logs, "total": len(logs)}

@app.get("/api/v1/logs/{log_id}", response_model=SecurityLogResponse)
async def get_log(log_id: int, db: AsyncSession = Depends(get_db)):
    query = select(SecurityLog).filter(SecurityLog.id == log_id)
    result = await db.execute(query)
    log = result.scalars().first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
