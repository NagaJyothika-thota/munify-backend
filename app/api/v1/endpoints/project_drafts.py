from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.project_draft import (
    ProjectDraftCreate, 
    ProjectDraftUpdate, 
    ProjectDraftResponse, 
    ProjectDraftListResponse
)
from app.schemas.project import ProjectResponse
from app.services.project_draft_service import ProjectDraftService
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_draft(
    draft_data: ProjectDraftCreate, 
    db: Session = Depends(get_db),
    user_id: Optional[str] = None  # TODO: Get from authenticated user context
):
    """Create a new project draft"""
    try:
        service = ProjectDraftService(db)
        draft = service.create_draft(draft_data, user_id=user_id)
        draft_response = ProjectDraftResponse.model_validate(draft)
        return {
            "status": "success",
            "message": "Project draft created successfully",
            "data": draft_response
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project draft: {str(e)}"
        )


@router.get("/", response_model=ProjectDraftListResponse, status_code=status.HTTP_200_OK)
def get_drafts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),  # TODO: Get from auth context
    db: Session = Depends(get_db)
):
    """Get list of project drafts"""
    try:
        service = ProjectDraftService(db)
        drafts, total = service.get_drafts(user_id=user_id, skip=skip, limit=limit)
        drafts_response = [ProjectDraftResponse.model_validate(draft) for draft in drafts]
        return {
            "status": "success",
            "message": "Drafts fetched successfully",
            "data": drafts_response,
            "total": total
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch drafts: {str(e)}"
        )


@router.get("/{draft_id}", response_model=dict, status_code=status.HTTP_200_OK)
def get_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[str] = None  # TODO: Get from authenticated user context
):
    """Get draft by ID"""
    try:
        service = ProjectDraftService(db)
        draft = service.get_draft_by_id(draft_id, user_id=user_id)
        draft_response = ProjectDraftResponse.model_validate(draft)
        return {
            "status": "success",
            "message": "Draft fetched successfully",
            "data": draft_response
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch draft: {str(e)}"
        )


@router.put("/{draft_id}", response_model=dict, status_code=status.HTTP_200_OK)
def update_draft(
    draft_id: int,
    draft_data: ProjectDraftUpdate,
    db: Session = Depends(get_db),
    user_id: Optional[str] = None  # TODO: Get from authenticated user context
):
    """Update an existing draft"""
    try:
        service = ProjectDraftService(db)
        draft = service.update_draft(draft_id, draft_data, user_id=user_id)
        draft_response = ProjectDraftResponse.model_validate(draft)
        return {
            "status": "success",
            "message": "Draft updated successfully",
            "data": draft_response
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update draft: {str(e)}"
        )


@router.delete("/{draft_id}", status_code=status.HTTP_200_OK)
def delete_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[str] = None  # TODO: Get from authenticated user context
):
    """Delete a draft"""
    try:
        service = ProjectDraftService(db)
        service.delete_draft(draft_id, user_id=user_id)
        return {
            "status": "success",
            "message": "Draft deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete draft: {str(e)}"
        )


@router.post("/{draft_id}/submit", response_model=dict, status_code=status.HTTP_201_CREATED)
def submit_draft(
    draft_id: int,
    draft_data: Optional[ProjectDraftUpdate] = None,  # Optional: allows updating draft before submission
    db: Session = Depends(get_db),
    user_id: Optional[str] = None  # TODO: Get from authenticated user context
):
    """Submit draft - converts draft to project using existing project creation API
    
    This endpoint:
    1. Optionally updates draft with provided data (if draft_data is provided)
    2. Validates draft exists and user has access
    3. Validates all required fields are present
    4. Creates project using existing project creation API
    5. Deletes draft after successful project creation
    
    If draft_data is provided, the draft will be updated before validation and submission.
    This allows fixing validation errors and resubmitting in a single call.
    
    If project creation fails, the draft is preserved for retry.
    """
    try:
        draft_service = ProjectDraftService(db)
        
        # If draft_data is provided, update the draft first
        # This allows users to fix validation errors and resubmit in one call
        if draft_data is not None:
            draft_service.update_draft(draft_id, draft_data, user_id=user_id)
        
        # Use the service method which handles all error scenarios
        project = draft_service.submit_draft(draft_id, user_id=user_id)
        
        # Return created project
        project_response = ProjectResponse.model_validate(project)
        return {
            "status": "success",
            "message": "Draft submitted and project created successfully",
            "data": project_response
        }
    except HTTPException:
        # Re-raise HTTPExceptions (validation errors, not found, etc.)
        raise
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit draft: {str(e)}"
        )

