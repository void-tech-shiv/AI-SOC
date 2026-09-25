from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'

class AlertStatus(str, Enum):
    open = 'open'
    investigating = 'investigating'
    resolved = 'resolved'
    false_positive = 'false_positive'

class SecurityLogCreate(BaseModel):
    timestamp: datetime
    source: str
    event_type: str
    severity: SeverityLevel
    username: Optional[str] = None
    ip_address: Optional[str] = None
    message: str
    raw_event: str

class SecurityLogResponse(SecurityLogCreate):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SecurityLogListResponse(BaseModel):
    logs: List[SecurityLogResponse]
    total: int

class AlertBase(BaseModel):
    log_id: int
    rule_id: str
    rule_name: str
    title: str
    description: str
    severity: SeverityLevel
    confidence_score: float
    evidence: dict
    status: AlertStatus = AlertStatus.open

class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int

class AlertStatusUpdate(BaseModel):
    status: AlertStatus

class DetectionRunResponse(BaseModel):
    logs_scanned: int
    detections_matched: int
    alerts_created: int
    duplicates_skipped: int
    rules_evaluated: int

class DetectionRuleResponse(BaseModel):
    rule_id: str
    rule_name: str


class IncidentStatus(str, Enum):
    open = 'open'
    investigating = 'investigating'
    contained = 'contained'
    resolved = 'resolved'
    false_positive = 'false_positive'

class IncidentBase(BaseModel):
    incident_key: str
    title: str
    description: str
    severity: SeverityLevel
    priority_score: int
    status: IncidentStatus = IncidentStatus.open
    confidence_score: float
    first_seen: datetime
    last_seen: datetime
    alert_count: int
    affected_users: List[str]
    affected_ips: List[str]
    summary: Optional[str] = None

class IncidentResponse(IncidentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class IncidentListResponse(BaseModel):
    incidents: List[IncidentResponse]
    total: int

class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus

class CorrelationRunResponse(BaseModel):
    alerts_scanned: int
    incident_candidates: int
    incidents_created: int
    incidents_updated: int
    standalone_incidents_created: int
    duplicates_skipped: int
    rules_evaluated: int = Field(description="registered specific rules evaluated per run")

class CorrelationRuleResponse(BaseModel):
    rule_id: str
    rule_name: str

class IncidentAlertResponse(BaseModel):
    incident_id: int
    alert_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
