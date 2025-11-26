from sqlalchemy import Column, BigInteger, String, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProjectFavorite(Base):
    __tablename__ = "perdix_mp_project_favorites"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Foreign key to project (references project_reference_id)
    project_reference_id = Column(String(255), ForeignKey("perdix_mp_projects.project_reference_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Organization and user information
    organization_id = Column(String(255), nullable=False)
    # Note: user_id references invitations.user_id but cannot have FK constraint since user_id is not unique in invitations
    # Validation is done in service layer instead
    user_id = Column(String(255), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=True)
    created_by = Column(String(255), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    # Relationship to Project (using project_reference_id as foreign key)
    project = relationship(
        "Project",
        foreign_keys=[project_reference_id],
        primaryjoin="ProjectFavorite.project_reference_id == Project.project_reference_id",
        viewonly=True
    )
    
    # Unique constraint: one user can favorite a project only once (using project_reference_id and user_id)
    __table_args__ = (
        UniqueConstraint('project_reference_id', 'user_id', name='uq_project_favorite_project_user'),
    )

