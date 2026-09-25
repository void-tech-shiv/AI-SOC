from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base
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
