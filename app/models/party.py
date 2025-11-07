from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Party(Base):
    __tablename__ = "parties"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False, index=True)  # MUNICIPAL, BUYER, ADMIN
    legal_name = Column(String(191), nullable=False, index=True)
    registration_number = Column(String(191), unique=True)
    pan = Column(Text)
    gstn = Column(Text)
    status = Column(String(20), default="PENDING")  # ACTIVE, BLOCKED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="party")
    # listings = relationship("Listing", back_populates="seller")  # Removed - Listing table deleted


