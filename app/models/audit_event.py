from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    entity_type = Column(Text)
    entity_id = Column(Integer)
    action = Column(Text)
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


