from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SettlementLog(Base):
    __tablename__ = "settlement_logs"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"), nullable=False)
    proof_url = Column(Text)
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships


