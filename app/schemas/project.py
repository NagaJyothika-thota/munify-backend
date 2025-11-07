from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date
from decimal import Decimal
from pydantic import ConfigDict


class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    user_id: int
    project_title: str
    project_category: Literal["Water", "Sanitation", "Roads", "Energy", "Other"]
    project_stage: Literal["planning", "initiated", "in_progress"]
    description: str
    location: str  # state, city, ward
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    # Financials
    total_project_cost: Decimal
    funding_required: Decimal
    funds_secured: Optional[Decimal] = Decimal('0')
    funding_gap: Optional[Decimal] = Decimal('0')  # auto-calculated
    
    # Media and disclosures
    media: Optional[str] = None  # JSON: banner_image, photos, videos
    disclosures_summary: Optional[str] = None
    
    # Admin validation
    admin_validation_checklist: Optional[str] = None  # JSON: pass/fail + comments
    
    # Status and metadata
    status: Optional[Literal["draft", "pending_validation", "active", "closed", "rejected"]] = "draft"
    notes: Optional[str] = None
    municipality_id: str


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    project_title: Optional[str] = None
    project_category: Optional[Literal["Water", "Sanitation", "Roads", "Energy", "Other"]] = None
    project_stage: Optional[Literal["planning", "initiated", "in_progress"]] = None
    description: Optional[str] = None
    location: Optional[str] = None
    municipality_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_project_cost: Optional[Decimal] = None
    funding_required: Optional[Decimal] = None
    funds_secured: Optional[Decimal] = None
    funding_gap: Optional[Decimal] = None
    media: Optional[str] = None
    disclosures_summary: Optional[str] = None
    admin_validation_checklist: Optional[str] = None
    status: Optional[Literal["draft", "pending_validation", "active", "closed", "rejected"]] = None
    notes: Optional[str] = None


class Project(BaseModel):
    """Schema for project response"""
    id: int
    user_id: int
    project_title: str
    project_category: Literal["Water", "Sanitation", "Roads", "Energy", "Other"]
    project_stage: Literal["planning", "initiated", "in_progress"]
    description: str
    location: str
    municipality_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_project_cost: Decimal
    funding_required: Decimal
    funds_secured: Decimal
    funding_gap: Decimal
    media: Optional[str] = None
    disclosures_summary: Optional[str] = None
    admin_validation_checklist: Optional[str] = None
    status: Literal["draft", "pending_validation", "active", "closed", "rejected"]
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)