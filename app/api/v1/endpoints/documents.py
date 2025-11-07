from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.schemas.document import Document, DocumentResponse, DocumentListResponse
from app.models.document import Document as DocumentModel
from app.models.project import Project as ProjectModel
from app.services.storage import LocalStorageService


router = APIRouter()
storage = LocalStorageService()


@router.get("/", response_model=DocumentListResponse, status_code=status.HTTP_200_OK)
def list_documents(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all documents for a specific project"""
    query = db.query(DocumentModel).filter(DocumentModel.project_id == project_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"status": "success", "message": "Documents fetched successfully", "data": items, "total": total}


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    mime_type: str = Form(None),
    watermark_flag: str = Form("no"),
    visibility_policy: str = Form("open"),
    uploaded_by_user_id: int = Form(1),
    db: Session = Depends(get_db),
):
    """Upload a document for a project"""
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # determine next version for this filename
    base_name = file.filename
    current_max = db.query(func.coalesce(func.max(DocumentModel.version), 0)).filter(
        DocumentModel.project_id == project_id,
        DocumentModel.file_name == base_name,
    ).scalar()
    next_version = int(current_max) + 1

    file_bytes = await file.read()
    storage_path, sha256_hash = storage.save_file(project_id, base_name, file_bytes, next_version)

    db_doc = DocumentModel(
        project_id=project_id,
        uploaded_by=uploaded_by_user_id,
        file_name=base_name,
        file_url=storage_path,
        file_hash=sha256_hash,
        version=next_version,
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    return {"status": "success", "message": "Document uploaded successfully", "data": db_doc}


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    db_document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    db.delete(db_document)
    db.commit()


