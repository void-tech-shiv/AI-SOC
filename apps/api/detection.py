import os
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update

from apps.api.models import SecurityLog, Alert
from apps.api.schemas import (
    AlertResponse, AlertListResponse, AlertStatusUpdate,
    DetectionRunResponse, DetectionRuleResponse,
    SeverityLevel, AlertStatus
)
from services.detection.engine import evaluate_log, get_detection_rules, RULE_REGISTRY

# Using a dummy dependency so I don't import from main.py and cause circular imports
# This will be overridden or imported
from apps.api.database import get_db

router = APIRouter(tags=["Detection"])

@router.get("/api/v1/detection-rules", response_model=List[DetectionRuleResponse])
async def list_detection_rules():
    return get_detection_rules()

@router.post("/api/v1/detections/run", response_model=DetectionRunResponse)
async def run_detections(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SecurityLog).order_by(SecurityLog.id))
    logs = result.scalars().all()
    
    logs_scanned = len(logs)
    detections_matched = 0
    alerts_created = 0
    duplicates_skipped = 0
    rules_evaluated = 0
    
    existing_alerts_res = await db.execute(select(Alert.log_id, Alert.rule_id))
    existing_alerts = set((row[0], row[1]) for row in existing_alerts_res.all())
    
    for log in logs:
        findings, eval_count = evaluate_log(log)
        detections_matched += len(findings)
        rules_evaluated += eval_count
        
        for finding in findings:
            if (log.id, finding.rule_id) in existing_alerts:
                duplicates_skipped += 1
                continue
                
            new_alert = Alert(
                log_id=log.id,
                rule_id=finding.rule_id,
                rule_name=finding.rule_name,
                title=finding.title,
                description=finding.description,
                severity=finding.severity,
                confidence_score=finding.confidence_score,
                evidence=finding.evidence
            )
            db.add(new_alert)
            existing_alerts.add((log.id, finding.rule_id))
            alerts_created += 1
            
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database integrity error during batch commit.")
                
    return DetectionRunResponse(
        logs_scanned=logs_scanned,
        detections_matched=detections_matched,
        alerts_created=alerts_created,
        duplicates_skipped=duplicates_skipped,
        rules_evaluated=rules_evaluated
    )

@router.get("/api/v1/alerts", response_model=AlertListResponse)
async def list_alerts(
    severity: SeverityLevel = Query(None),
    status: AlertStatus = Query(None),
    rule_id: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    query = select(Alert)
    
    if severity:
        query = query.filter(Alert.severity == severity.value)
    if status:
        query = query.filter(Alert.status == status.value)
    if rule_id:
        query = query.filter(Alert.rule_id == rule_id)
        
    query = query.order_by(Alert.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return AlertListResponse(alerts=alerts, total=len(alerts))

@router.get("/api/v1/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).filter(Alert.id == alert_id))
    alert = result.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/api/v1/alerts/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: int,
    status_update: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Alert).filter(Alert.id == alert_id))
    alert = result.scalars().first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = status_update.status.value
    await db.commit()
    await db.refresh(alert)
    
    return alert
