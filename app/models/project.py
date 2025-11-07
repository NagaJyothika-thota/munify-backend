from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Core project fields (P1, required)
    project_title = Column(Text, nullable=False)
    project_category = Column(String(50), nullable=False)  # Water | Sanitation | Roads | Energy | Other
    project_stage = Column(String(50), nullable=False)  # planning | initiated | in_progress
    description = Column(Text, nullable=False)
    location = Column(Text, nullable=False)  # state, city, ward
    municipality_id = Column(String(191), nullable=True)
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Financials (P1, required)
    total_project_cost = Column(Numeric(18, 2), nullable=False)
    funding_required = Column(Numeric(18, 2), nullable=False)
    funds_secured = Column(Numeric(18, 2), default=0)
    funding_gap = Column(Numeric(18, 2), default=0)  # auto-calculated
    
    # Media and disclosures
    media = Column(Text)  # JSON: banner_image, photos, videos
    disclosures_summary = Column(Text)
    
    # Admin validation
    admin_validation_checklist = Column(Text)  # JSON: pass/fail + comments
    
    # Status and metadata
    status = Column(String(50), default="draft")  # draft | pending_validation | active | closed | rejected
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    commitments = relationship("Commitment", back_populates="project", cascade="all, delete-orphan")
    access_grants = relationship("AccessGrant", back_populates="project", cascade="all, delete-orphan")
    allocations = relationship("Allocation", back_populates="project", cascade="all, delete-orphan")