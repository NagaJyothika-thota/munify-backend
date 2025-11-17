from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from passlib.context import CryptContext
from app.core.config import settings
from app.services.user_service import register_user_with_optional_roles, get_users_from_perdix, get_user_from_perdix_by_login, update_user_in_perdix
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/perdix", status_code=status.HTTP_200_OK)
def get_perdix_users(
    branch_name: Optional[str] = Query(None, description="Filter users by branch name"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(10, ge=1, le=100, description="Number of items per page")
):
    """Get users list from Perdix API with pagination and optional branch filter"""
    body, status_code, is_json = get_users_from_perdix(branch_name=branch_name, page=page, per_page=per_page)
    
    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=body if isinstance(body, str) else body.get("message", "Failed to fetch users from Perdix")
        )
    
    return {
        "status": "success",
        "message": "Users fetched from Perdix successfully",
        "data": body if is_json else {"raw": body}
    }

@router.get("/perdix/{login}", status_code=status.HTTP_200_OK)
def get_perdix_user_by_login(login: str):
    """Get single user details from Perdix by login/username"""
    body, status_code, is_json = get_user_from_perdix_by_login(login)

    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=body if isinstance(body, str) else body.get("message", "Failed to fetch user from Perdix")
        )

    return {
        "status": "success",
        "message": "User fetched from Perdix successfully",
        "data": body if is_json else {"raw": body}
    }

@router.get("/perdix/userid/{userid}", status_code=status.HTTP_200_OK)
def get_perdix_user_by_userid(userid: str):
    """Alias: Get Perdix user by userId (mapped to login)"""
    body, status_code, is_json = get_user_from_perdix_by_login(userid)

    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=body if isinstance(body, str) else body.get("message", "Failed to fetch user from Perdix")
        )

    return {
        "status": "success",
        "message": "User fetched from Perdix successfully",
        "data": body if is_json else {"raw": body}
    }

@router.put("/perdix", status_code=status.HTTP_200_OK)
def update_perdix_user(payload: dict):
    """Forward user update to Perdix (PUT /api/users)"""
    body, status_code, is_json = update_user_in_perdix(payload)
    return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)
