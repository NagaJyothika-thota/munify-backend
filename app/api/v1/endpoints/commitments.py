from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.commitment import Commitment, CommitmentCreate, CommitmentUpdate, CommitmentResponse, CommitmentListResponse
from app.services.commitment_service import CommitmentService


router = APIRouter()


@router.get("/", response_model=CommitmentListResponse, status_code=status.HTTP_200_OK)
def list_commitments(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all commitments for a specific project"""
    service = CommitmentService(db)
    result = service.get_commitments_by_project(project_id, skip, limit)
    return {
        "status": "success", 
        "message": "Commitments fetched successfully", 
        "data": result["items"], 
        "total": result["total"]
    }


@router.post("/", response_model=CommitmentResponse, status_code=status.HTTP_201_CREATED)
def create_commitment(payload: CommitmentCreate, db: Session = Depends(get_db)):
    """Create a new commitment for a project"""
    service = CommitmentService(db)
    db_commitment = service.create_commitment(payload)
    return {"status": "success", "message": "Commitment created successfully", "data": db_commitment}


@router.get("/{commitment_id}", response_model=CommitmentResponse, status_code=status.HTTP_200_OK)
def get_commitment(commitment_id: int, db: Session = Depends(get_db)):
    """Get a specific commitment by ID"""
    service = CommitmentService(db)
    db_commitment = service.get_commitment_by_id(commitment_id)
    return {"status": "success", "message": "Commitment fetched successfully", "data": db_commitment}


@router.put("/{commitment_id}", response_model=CommitmentResponse, status_code=status.HTTP_200_OK)
def update_commitment(commitment_id: int, payload: CommitmentUpdate, db: Session = Depends(get_db)):
    """Update an existing commitment"""
    service = CommitmentService(db)
    db_commitment = service.update_commitment(commitment_id, payload)
    return {"status": "success", "message": "Commitment updated successfully", "data": db_commitment}


@router.delete("/{commitment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_commitment(commitment_id: int, db: Session = Depends(get_db)):
    """Delete a commitment"""
    service = CommitmentService(db)
    service.delete_commitment(commitment_id)


