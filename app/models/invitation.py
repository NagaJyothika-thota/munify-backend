from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=False)  # Foreign key to organizations table
    organization_type_id = Column(Integer, nullable=False)  # Foreign key to organization_types table
    full_name = Column(String(255), nullable=False)
    user_id = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    mobile_number = Column(String(20), nullable=False)
    role_id = Column(Integer, nullable=False)
    role_name = Column(String(100), nullable=False)
    
    token = Column(String(255), unique=True, index=True, nullable=False)
    expiry = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships (optional - for future joins)
    # organization = relationship("Organization", foreign_keys=[organization_id])
    # organization_type = relationship("OrganizationType", foreign_keys=[organization_type_id])
