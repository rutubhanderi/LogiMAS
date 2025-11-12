from sqlalchemy import Column, String, BigInteger, Numeric, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from ..database import Base


class AgentAuditLog(Base):
    """Agent audit log model for AI decision tracking"""
    __tablename__ = "agent_audit_logs"
    __table_args__ = {"schema": "public"}
    
    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    agent_name = Column(String, nullable=False)
    decision_json = Column(JSONB)
    confidence = Column(Numeric)
    timestamp = Column(DateTime(timezone=True), default=datetime.now)
    input_context = Column(JSONB)
    
    def __repr__(self):
        return f"<AgentAuditLog(agent={self.agent_name}, timestamp={self.timestamp})>"
