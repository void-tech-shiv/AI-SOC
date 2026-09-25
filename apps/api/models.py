from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import JSON
import datetime

Base = declarative_base()

class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source = Column(String, index=True)
    event_type = Column(String, index=True)
    severity = Column(String, index=True)
    username = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    message = Column(String)
    raw_event = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('timestamp', 'source', 'event_type', 'ip_address', 'message', name='uq_synthetic_log_identity'),
    )

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("security_logs.id"), index=True)
    rule_id = Column(String, index=True)
    rule_name = Column(String)
    title = Column(String)
    description = Column(String)
    severity = Column(String, index=True)
    confidence_score = Column(Float)
    evidence = Column(JSON)
    status = Column(String, index=True, default="open")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('log_id', 'rule_id', name='uq_alert_log_rule'),
    )
