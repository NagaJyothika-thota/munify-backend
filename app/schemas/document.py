from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    file_name: str


class DocumentCreate(DocumentBase):
    pass


class DocumentInDB(DocumentBase):
    id: int
    project_id: int  # Changed from listing_id to project_id
    uploaded_by: Optional[int] = None
    file_url: Optional[str] = None
    file_hash: Optional[str] = None
    version: int
    created_at: datetime

    class Config:
        from_attributes = True


class Document(DocumentInDB):
    pass


class DocumentResponse(BaseModel):
    status: str
    message: str
    data: Document

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    status: str
    message: str
    data: List[Document]
    total: int

    class Config:
        from_attributes = True


