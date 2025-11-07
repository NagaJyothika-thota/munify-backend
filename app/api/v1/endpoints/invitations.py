from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.invitation import InvitationCreate, InvitationResponse, InvitationValidate, InvitationListResponse
from app.services.invitation_service import (
    create_invitation,
    validate_invitation_token,
    mark_invitation_used,
    get_invitations,
    resend_invitation
)

router = APIRouter()


@router.post("/invite", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def create_invite(payload: InvitationCreate, db: Session = Depends(get_db)):
    """Create a new invitation"""
    try:
        invitation_data = create_invitation(payload, db)
        return invitation_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invitation: {str(e)}"
        )


@router.get("/validate/{token}", response_model=InvitationResponse, status_code=status.HTTP_200_OK)
def validate_invite(token: str, db: Session = Depends(get_db)):
    """Validate invitation token"""
    try:
        invitation_data = validate_invitation_token(token, db)
        return invitation_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate invitation: {str(e)}"
        )


@router.get("/", response_model=InvitationListResponse, status_code=status.HTTP_200_OK)
def get_invites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of invitations with pagination"""
    try:
        invitations_data = get_invitations(skip, limit, db)
        return invitations_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invitations: {str(e)}"
        )


@router.post("/{invitation_id}/resend", response_model=InvitationResponse, status_code=status.HTTP_200_OK)
def resend_invite(invitation_id: int, db: Session = Depends(get_db)):
    """Resend invitation with new token"""
    try:
        invitation_data = resend_invitation(invitation_id, db)
        return invitation_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend invitation: {str(e)}"
        )


@router.post("/{token}/mark-used", status_code=status.HTTP_200_OK)
def mark_invite_used(token: str, db: Session = Depends(get_db)):
    """Mark invitation as used (called after successful registration)"""
    try:
        success = mark_invitation_used(token, db)
        if success:
            return {"status": "success", "message": "Invitation marked as used"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark invitation as used: {str(e)}"
        )
