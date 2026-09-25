from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime
import json
import logging

from .database import get_db
from .models import Alert, Incident, IncidentAlert
from .schemas import IncidentResponse, IncidentListResponse, IncidentStatusUpdate, CorrelationRunResponse, CorrelationRuleResponse, IncidentAlertResponse, SeverityLevel, IncidentStatus, AlertResponse
from services.correlation.engine import correlate_alerts
from services.correlation.rules import RULES

router = APIRouter(prefix="/api/v1", tags=["incidents"])
logger = logging.getLogger(__name__)

@router.get("/correlation-rules", response_model=List[CorrelationRuleResponse])
async def get_correlation_rules():
    return [{"rule_id": r.rule_id, "rule_name": r.name, "severity": getattr(r, "severity", None), "time_window_minutes": getattr(r, "time_window_minutes", None), "description": getattr(r, "description", None)} for r in RULES]

@router.post("/correlations/run", response_model=CorrelationRunResponse)
async def run_correlation(db: AsyncSession = Depends(get_db)):
    # 1. Fetch alerts
    result = await db.execute(select(Alert).where(Alert.status.notin_(['resolved', 'false_positive'])))
    alerts_raw = result.scalars().all()
    
    # 3. Run correlation engine
    candidates = correlate_alerts(alerts_raw)
    
    incidents_created = 0
    incidents_updated = 0
    standalone_incidents_created = 0
    duplicates_skipped = 0
    
    for candidate in candidates:
        # check if incident_key already exists
        res = await db.execute(select(Incident).where(Incident.incident_key == candidate.incident_key))
        existing_incident = res.scalar_one_or_none()
        
        if existing_incident:
            # check if any new alerts need to be linked
            new_alerts_count = 0
            for alert_id in candidate.alert_ids:
                link_res = await db.execute(select(IncidentAlert).where(and_(IncidentAlert.incident_id == existing_incident.id, IncidentAlert.alert_id == alert_id)))
                link = link_res.scalar_one_or_none()
                if not link:
                    new_link = IncidentAlert(incident_id=existing_incident.id, alert_id=alert_id)
                    db.add(new_link)
                    new_alerts_count += 1
            
            if new_alerts_count > 0:
                await db.flush()
                alerts_res = await db.execute(select(Alert).join(IncidentAlert).where(IncidentAlert.incident_id == existing_incident.id))
                linked_alerts = alerts_res.scalars().all()
                
                existing_incident.alert_count = len(linked_alerts)
                if linked_alerts:
                    existing_incident.confidence_score = sum(a.confidence_score or 0.0 for a in linked_alerts) / len(linked_alerts)
                
                sev_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                if sev_order.get(candidate.severity, 0) > sev_order.get(existing_incident.severity, 0):
                    existing_incident.severity = candidate.severity
                    
                existing_incident.affected_users = list(set((existing_incident.affected_users or []) + candidate.affected_users))
                existing_incident.affected_ips = list(set((existing_incident.affected_ips or []) + candidate.affected_ips))
                existing_incident.first_seen = min(existing_incident.first_seen, candidate.first_seen)
                existing_incident.last_seen = max(existing_incident.last_seen, candidate.last_seen)
                existing_incident.priority_score = max(existing_incident.priority_score, candidate.priority_score)
                incidents_updated += 1
            else:
                duplicates_skipped += 1
        else:
            new_incident = Incident(
                incident_key=candidate.incident_key,
                title=candidate.title,
                description=candidate.description,
                severity=candidate.severity,
                confidence_score=candidate.confidence_score,
                priority_score=candidate.priority_score,
                alert_count=len(candidate.alert_ids),
                affected_users=candidate.affected_users,
                affected_ips=candidate.affected_ips,
                first_seen=candidate.first_seen,
                last_seen=candidate.last_seen,
                status="open"
            )
            db.add(new_incident)
            await db.flush()
            for alert_id in candidate.alert_ids:
                new_link = IncidentAlert(incident_id=new_incident.id, alert_id=alert_id)
                db.add(new_link)
                
            if candidate.correlation_rule == 'CORR-005':
                standalone_incidents_created += 1
            else:
                incidents_created += 1
                
    await db.commit()
    
    return CorrelationRunResponse(
        alerts_scanned=len(alerts_raw),
        incident_candidates=len(candidates),
        incidents_created=incidents_created,
        incidents_updated=incidents_updated,
        standalone_incidents_created=standalone_incidents_created,
        duplicates_skipped=duplicates_skipped,
        rules_evaluated=len(RULES)
    )

@router.get("/incidents", response_model=IncidentListResponse)
async def list_incidents(
    severity: Optional[SeverityLevel] = None,
    status: Optional[IncidentStatus] = None,
    min_priority: Optional[int] = Query(None, ge=0, le=100),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    query = select(Incident)
    if severity:
        query = query.where(Incident.severity == severity.value)
    if status:
        query = query.where(Incident.status == status.value)
    if min_priority is not None:
        query = query.where(Incident.priority_score >= min_priority)
        
    query = query.order_by(Incident.priority_score.desc()).limit(limit)
    res = await db.execute(query)
    incidents = res.scalars().all()
    
    count_query = select(func.count(Incident.id))
    if severity:
        count_query = count_query.where(Incident.severity == severity.value)
    if status:
        count_query = count_query.where(Incident.status == status.value)
    if min_priority is not None:
        count_query = count_query.where(Incident.priority_score >= min_priority)
    total_res = await db.execute(count_query)
    total = total_res.scalar()
    
    return IncidentListResponse(incidents=list(incidents), total=total)

@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = res.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.get("/incidents/{incident_id}/alerts", response_model=List[AlertResponse])
async def get_incident_alerts(incident_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = res.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    query = select(Alert).join(IncidentAlert).where(IncidentAlert.incident_id == incident_id).order_by(Alert.created_at.desc())
    alerts_res = await db.execute(query)
    alerts = alerts_res.scalars().all()
    return list(alerts)

@router.patch("/incidents/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(incident_id: int, status_update: IncidentStatusUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = res.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    incident.status = status_update.status.value
    await db.commit()
    await db.refresh(incident)
    return incident
