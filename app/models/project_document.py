from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProjectDocument(Base):
    __tablename__ = "perdix_mp_project_documents"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Logical reference to project using project_reference_id.
    # NOTE: No database-level foreign key on purpose, because documents can
    # be created at draft stage before a row exists in perdix_mp_projects.
    project_id = Column(String(255), nullable=False, index=True)
    
    # Foreign key to file
    file_id = Column(
        BigInteger,
        ForeignKey("perdix_mp_files.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Document details
    document_type = Column(String(100), nullable=False)  # dpr, feasibility_study, compliance_certificate, budget_approval, tender_rfp
    version = Column(Integer, default=1, nullable=False)
    access_level = Column(String(50), default='public', nullable=False)
    
    # Uploader information
    uploaded_by = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=True)
    created_by = Column(String(255), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    updated_by = Column(String(255), nullable=True)
        
    
    file = relationship("PerdixFile", foreign_keys=[file_id])
    
    # Add check constraint for access_level
    __table_args__ = (
        CheckConstraint(
            "access_level IN ('public', 'restricted', 'private')",
            name='check_project_document_access_level'
        ),
    )

