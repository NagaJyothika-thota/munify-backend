import uuid
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.invitation import Invitation
from app.schemas.invitation import InvitationCreate
from app.core.config import settings


def generate_invitation_token(db: Session, length_bytes: int = 9, max_attempts: int = 5) -> str:
    """Generate a short, URL-safe unique token (~12 chars with 9 bytes entropy).

    Ensures uniqueness by checking the database and retrying on collisions.
    """
    for _ in range(max_attempts):
        token = secrets.token_urlsafe(length_bytes)
        exists = db.query(Invitation.id).filter(Invitation.token == token).first()
        if not exists:
            return token
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Could not generate unique invitation token. Please try again."
    )


def create_invitation(payload: InvitationCreate, db: Session) -> dict:
    """Create a new invitation and return invitation details"""
    
    # Check if invitation already exists for this email
    existing_invitation = db.query(Invitation).filter(Invitation.email == payload.email).first()
    if existing_invitation and not existing_invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invitation already exists for this email"
        )
    
    # Generate token and expiry (7 days from now)
    token = generate_invitation_token(db)
    expiry = datetime.utcnow() + timedelta(days=7)
    
    # Create invitation record
    invitation = Invitation(
        organization_id=payload.organization_id,
        organization_type_id=payload.organization_type_id,
        full_name=payload.full_name,
        user_id=payload.user_id,
        email=payload.email,
        mobile_number=str(payload.mobile_number),
        role_id=payload.role_id,
        role_name=payload.role_name,
        token=token,
        expiry=expiry,
        is_used=False
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # Generate invitation link
    invite_link = f"{settings.FRONTEND_ORIGIN}/register?token={token}"
    
    return {
        "id": invitation.id,
        "organization_id": invitation.organization_id,
        "organization_type_id": invitation.organization_type_id,
        "full_name": invitation.full_name,
        "user_id": invitation.user_id,
        "email": invitation.email,
        "mobile_number": invitation.mobile_number,
        "role_id": invitation.role_id,
        "role_name": invitation.role_name,
        "token": invitation.token,
        "expiry": invitation.expiry,
        "is_used": invitation.is_used,
        "created_at": invitation.created_at,
        "updated_at": invitation.updated_at,
        "invite_link": invite_link
    }


def validate_invitation_token(token: str, db: Session) -> dict:
    """Validate invitation token and return invitation details"""
    
    invitation = db.query(Invitation).filter(Invitation.token == token).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invitation token"
        )
    
    if invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has already been used"
        )
    
    if datetime.utcnow() > invitation.expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    invite_link = f"{settings.FRONTEND_ORIGIN}/register?token={invitation.token}"
    return {
        "id": invitation.id,
        "organization_id": invitation.organization_id,
        "organization_type_id": invitation.organization_type_id,
        "full_name": invitation.full_name,
        "user_id": invitation.user_id,
        "email": invitation.email,
        "mobile_number": invitation.mobile_number,
        "role_id": invitation.role_id,
        "role_name": invitation.role_name,
        "token": invitation.token,
        "expiry": invitation.expiry,
        "is_used": invitation.is_used,
        "created_at": invitation.created_at,
        "updated_at": invitation.updated_at,
        "invite_link": invite_link,
    }


def mark_invitation_used(token: str, db: Session) -> bool:
    """Mark invitation as used after successful registration"""
    
    invitation = db.query(Invitation).filter(Invitation.token == token).first()
    
    if not invitation:
        return False
    
    invitation.is_used = True
    invitation.updated_at = datetime.utcnow()
    db.commit()
    
    return True


def get_invitations(skip: int = 0, limit: int = 100, db: Session = None) -> dict:
    """Get list of invitations with pagination"""
    
    query = db.query(Invitation)
    total = query.count()
    invitations = query.offset(skip).limit(limit).all()
    
    invitation_list = []
    for invitation in invitations:
        invite_link = f"{settings.FRONTEND_ORIGIN}/register?token={invitation.token}"
        invitation_list.append({
            "id": invitation.id,
            "organization_id": invitation.organization_id,
            "organization_type_id": invitation.organization_type_id,
            "full_name": invitation.full_name,
            "user_id": invitation.user_id,
            "email": invitation.email,
            "mobile_number": invitation.mobile_number,
            "role_id": invitation.role_id,
            "role_name": invitation.role_name,
            "token": invitation.token,
            "expiry": invitation.expiry,
            "is_used": invitation.is_used,
            "created_at": invitation.created_at,
            "updated_at": invitation.updated_at,
            "invite_link": invite_link
        })
    
    return {
        "status": "success",
        "message": "Invitations fetched successfully",
        "data": invitation_list,
        "total": total
    }


def resend_invitation(invitation_id: int, db: Session) -> dict:
    """Resend invitation by generating new token and extending expiry"""
    
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    if invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot resend used invitation"
        )
    
    # Generate new token and extend expiry
    invitation.token = generate_invitation_token(db)
    invitation.expiry = datetime.utcnow() + timedelta(days=7)
    invitation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(invitation)
    
    invite_link = f"{settings.FRONTEND_ORIGIN}/register?token={invitation.token}"
    
    return {
        "id": invitation.id,
        "organization_id": invitation.organization_id,
        "organization_type_id": invitation.organization_type_id,
        "full_name": invitation.full_name,
        "user_id": invitation.user_id,
        "email": invitation.email,
        "mobile_number": invitation.mobile_number,
        "role_id": invitation.role_id,
        "role_name": invitation.role_name,
        "token": invitation.token,
        "expiry": invitation.expiry,
        "is_used": invitation.is_used,
        "created_at": invitation.created_at,
        "updated_at": invitation.updated_at,
        "invite_link": invite_link
    }
