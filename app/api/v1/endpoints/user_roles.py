from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate, UserRoleResponse, UserRoleListResponse
from app.services.user_role_service import (
    create_user_role_in_perdix,
    update_user_role_in_perdix,
    get_user_roles_from_perdix
)

router = APIRouter()


@router.post("/roles", status_code=status.HTTP_201_CREATED)
def create_user_role(payload: UserRoleCreate):
    """Create a new user role"""
    try:
        body, status_code, is_json = create_user_role_in_perdix(payload)
        return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user role: {str(e)}"
        )


@router.put("/roles/{role_id}", status_code=status.HTTP_200_OK)
def update_user_role(role_id: int, payload: UserRoleUpdate):
    """Update an existing user role"""
    try:
        body, status_code, is_json = update_user_role_in_perdix(role_id, payload)
        return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )


@router.get("/roles", status_code=status.HTTP_200_OK)
def get_user_roles():
    """Get all user roles"""
    try:
        body, status_code, is_json = get_user_roles_from_perdix()
        return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user roles: {str(e)}"
        )
