from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from decimal import Decimal

from app.core.database import get_db
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationListResponse,
    PerdixOrgDetailResponse,
)
from app.services.organization_service import (
    create_organization_with_local_details,
    create_organization_in_perdix,
    update_organization_in_perdix,
    update_organization_in_perdix_raw,
    update_organization_with_local_details,
    get_organizations_from_perdix,
    get_org_detail_by_org_id,
)
from app.core.logging import get_logger

logger = get_logger("api.organizations")

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_organization(
    # Perdix API fields (required)
    bank_id: int = Form(..., alias="bankId"),
    parent_branch_id: int = Form(..., alias="parentBranchId"),
    branch_name: str = Form(..., alias="branchName"),
    branch_mail_id: str = Form(..., alias="branchMailId"),
    pin_code: int = Form(..., alias="pinCode"),
    branch_open_date: str = Form(..., alias="branchOpenDate"),
    cash_limit: int = Form(default=0, alias="cashLimit"),
    finger_print_device_type: str = Form(default="SAGEM", alias="fingerPrintDeviceType"),
    # Extra fields stored in local DB
    org_type: Optional[str] = Form(None, alias="orgType"),
    pan_number: Optional[str] = Form(None, alias="panNumber"),
    gst_number: Optional[str] = Form(None, alias="gstNumber"),
    state: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    type_of_lender: Optional[str] = Form(None, alias="lenderType"),
    annual_budget_size: Optional[str] = Form(None, alias="annualBudgetSize"),
    designation: Optional[str] = Form(None),
    created_by: Optional[str] = Form(None, alias="createdBy"),
    updated_by: Optional[str] = Form(None, alias="updatedBy"),
    # File uploads
    pan_document: Optional[UploadFile] = File(None, alias="panDocument"),
    gst_document: Optional[UploadFile] = File(None, alias="gstDocument"),
    # Database session and user context
    db: Session = Depends(get_db),
    uploaded_by: Optional[str] = Header(None, alias="X-User-Id"),
):
    """
    Create a new organization (branch in Perdix) with optional PAN and GST document uploads.

    Accepts multipart/form-data with the following fields:
    - Perdix API fields: bankId, parentBranchId, branchName, branchMailId, pinCode, 
      branchOpenDate, cashLimit, fingerPrintDeviceType
    - Local DB fields: orgType, panNumber, gstNumber, state, district, lenderType, 
      annualBudgetSize, designation, createdBy, updatedBy
    - File uploads: panDocument (optional), gstDocument (optional)

    Flow:
    1. Upload PAN and GST documents (if provided) to storage
    2. Save extra organization details in local DB (perdix_mp_org_details) with file IDs
    3. Call Perdix branch API to actually create the organization
    4. If Perdix call fails, local DB insert is rolled back and uploaded files are deleted.
    """
    try:
        # Convert annual_budget_size from string to Decimal if provided
        annual_budget_size_decimal = None
        if annual_budget_size:
            try:
                annual_budget_size_decimal = Decimal(annual_budget_size)
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid annualBudgetSize format"
                )
        
        # Create OrganizationCreate payload from form data
        payload = OrganizationCreate(
            bank_id=bank_id,
            parent_branch_id=parent_branch_id,
            branch_name=branch_name,
            branch_mail_id=branch_mail_id,
            pin_code=pin_code,
            branch_open_date=branch_open_date,
            cash_limit=cash_limit,
            finger_print_device_type=finger_print_device_type,
            org_type=org_type,
            pan_number=pan_number,
            gst_number=gst_number,
            state=state,
            district=district,
            type_of_lender=type_of_lender,
            annual_budget_size=annual_budget_size_decimal,
            designation=designation,
            created_by=created_by,
            updated_by=updated_by,
        )
        
        # Call service with file uploads
        body, status_code, is_json = create_organization_with_local_details(
            payload=payload,
            db=db,
            pan_document=pan_document,
            gst_document=gst_document,
            uploaded_by=uploaded_by,
        )
        
        return JSONResponse(
            content=body if is_json else {"raw": body},
            status_code=status_code,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create organization: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}",
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
def update_organization_raw(payload: dict, db: Session = Depends(get_db)):
    """
    Update organization (branch) using raw payload from frontend.
    
    Flow (same pattern as create):
    1. Update extra organization details in local DB (perdix_mp_org_details) if org_id exists and fields are provided
    2. Call Perdix branch API to update the organization (with filtered payload - only Perdix fields)
    3. If Perdix call fails, local DB update is rolled back.
    
    Payload can include:
    - Required Perdix fields: id, version, branchCode, bankId, branchName, etc.
    - Optional local fields: panNumber, gstNumber, state, district, lenderType, annualBudgetSize, updatedBy
    
    Local fields (panNumber, gstNumber, state, district, lenderType, etc.) are:
    - Updated in our local database (perdix_mp_org_details)
    - NOT sent to Perdix API (filtered out)
    
    Perdix fields are sent as-is to Perdix API.
    """
    try:
        body, status_code, is_json = update_organization_with_local_details(payload, db)
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


@router.get("/org-details/{org_id}", response_model=PerdixOrgDetailResponse, status_code=status.HTTP_200_OK)
def get_org_detail_by_id(org_id: int, db: Session = Depends(get_db)):
    """
    Get organization details from perdix_mp_org_details table by org_id.
    
    Args:
        org_id: The organization ID to fetch details for
        db: Database session
        
    Returns:
        PerdixOrgDetailResponse: The organization detail record
    """
    try:
        org_detail = get_org_detail_by_org_id(org_id, db)
        return org_detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization details: {str(e)}"
        )
