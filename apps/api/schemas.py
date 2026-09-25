from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'

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
