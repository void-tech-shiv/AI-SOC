from pydantic import BaseModel, ConfigDict
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
