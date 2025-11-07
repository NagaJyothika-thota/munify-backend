from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class AccessGrant(Base):
    __tablename__ = "access_grants"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    granted_to_party_id = Column(Integer, ForeignKey("parties.id"), nullable=False)
    permission = Column(String(50), nullable=False)  # view, download
    expires_at = Column(DateTime(timezone=True), nullable=True)
    granted_via = Column(String(50), default="open")  # open, club, bilateral
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="access_grants")


