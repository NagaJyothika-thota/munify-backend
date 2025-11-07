from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse, OrganizationListResponse
from app.services.organization_service import (
    create_organization_in_perdix,
    update_organization_in_perdix,
    update_organization_in_perdix_raw,
    get_organizations_from_perdix
)

router = APIRouter()


@router.post("/organizations", status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate):
    """Create a new organization (branch in Perdix)"""
    try:
        body, status_code, is_json = create_organization_in_perdix(payload)
        return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )


@router.put("/organizations/{organization_id}", status_code=status.HTTP_200_OK)
def update_organization(organization_id: int, payload: OrganizationUpdate):
    """Update an existing organization (branch in Perdix)"""
    try:
        body, status_code, is_json = update_organization_in_perdix(organization_id, payload)
        return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update organization: {str(e)}"
        )


@router.put("/organizations", status_code=status.HTTP_200_OK)
def update_organization_raw(payload: dict):
    """Update organization (branch) using raw payload from frontend (must include id, version, branchCode, etc.)."""
    try:
        body, status_code, is_json = update_organization_in_perdix_raw(payload)
        return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update organization: {str(e)}"
        )


@router.get("/organizations", status_code=status.HTTP_200_OK)
def get_organizations():
    """Get all organizations (branches from Perdix)"""
    try:
        body, status_code, is_json = get_organizations_from_perdix()
        return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organizations: {str(e)}"
        )
