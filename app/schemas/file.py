"""
File Schemas - Request/Response models for file operations
"""
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class FileUploadRequest(BaseModel):
    """Request schema for file upload"""
    organization_id: str = Field(..., description="Organization ID")
    file_category: Literal["KYC", "Project", "Additional"] = Field(
        ..., 
        description="File category: KYC, Project, or Additional"
    )
    document_type: str = Field(
        ..., 
        description="Document type (e.g., PAN, GST, DPR, commitment)"
    )
    project_reference_id: Optional[str] = Field(
        None,
        description="Project reference ID (required for Project/Additional categories)"
    )
    access_level: Literal["public", "restricted", "private"] = Field(
        "private",
        description="File access level"
    )


class FileAccessUpdate(BaseModel):
    """Request schema for updating file access level"""
    access_level: Literal["public", "restricted", "private"] = Field(
        ...,
        description="New access level"
    )


class FileResponse(BaseModel):
    """Response schema for file metadata"""
    id: int
    organization_id: str
    uploaded_by: str
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    storage_path: str
    checksum: str
    access_level: str
    download_count: int
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: datetime
    updated_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """Response schema for file upload"""
    status: str
    message: str
    data: FileResponse


class FileMetadataResponse(BaseModel):
    """Response schema for file metadata"""
    status: str
    data: FileResponse


class FileDeleteResponse(BaseModel):
    """Response schema for file deletion"""
    status: str
    message: str


class FileAccessUpdateResponse(BaseModel):
    """Response schema for access level update"""
    status: str
    message: str
    data: FileResponse


class PresignedUrlResponse(BaseModel):
    """Response schema for presigned URL"""
    status: str
    data: dict
    
    class PresignedUrlData(BaseModel):
        url: str
        expires_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

