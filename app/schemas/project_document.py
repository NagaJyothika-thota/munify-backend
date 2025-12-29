"""
Project Document Schemas - Request/Response models for project document operations
"""
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.schemas.file import FileResponse


class ProjectDocumentResponse(BaseModel):
    """Response schema for project document with file details"""
    id: int
    project_id: str
    file_id: int
    document_type: str
    version: int
    access_level: str
    uploaded_by: str
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    # File details from perdix_mp_files
    file: Optional['FileResponse'] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProjectFileUploadResponse(BaseModel):
    """Response schema for project file upload"""
    status: str
    message: str
    data: dict
    
    class ProjectFileUploadData(BaseModel):
        file_id: int
        project_document_id: int
        document_type: str
        project_reference_id: str
    
    model_config = ConfigDict(from_attributes=True)


class ProjectFileDeleteResponse(BaseModel):
    """Response schema for project file deletion"""
    status: str
    message: str

