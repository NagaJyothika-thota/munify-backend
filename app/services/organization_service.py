import httpx
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


def create_organization_in_perdix(payload: OrganizationCreate) -> tuple:
    """Create a new organization (branch) in Perdix system"""
    base_url = settings.PERDIX_BASE_URL.rstrip("/")
    url = f"{base_url}/api/branch"
    
    if not settings.PERDIX_JWT:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perdix JWT is not configured")
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"JWT {settings.PERDIX_JWT}",
        "origin": settings.PERDIX_ORIGIN,
        "page_uri": "Page/Engine/management.BranchMaintenance",
        "referer": f"{settings.PERDIX_ORIGIN}/perdix-client/",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    
    organization_payload = {
        "bankId": payload.bank_id,
        "parentBranchId": payload.parent_branch_id,
        "branchName": payload.branch_name,
        "branchMailId": str(payload.branch_mail_id),
        "pinCode": payload.pin_code,
        "branchOpenDate": payload.branch_open_date,
        "cashLimit": payload.cash_limit,
        "fingerPrintDeviceType": payload.finger_print_device_type
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=organization_payload)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    
    try:
        return response.json(), response.status_code, True
    except ValueError:
        return response.text, response.status_code, False


def update_organization_in_perdix(organization_id: int, payload: OrganizationUpdate) -> tuple:
    """Update an existing organization (branch) in Perdix system"""
    base_url = settings.PERDIX_BASE_URL.rstrip("/")
    url = f"{base_url}/api/branch"
    
    if not settings.PERDIX_JWT:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perdix JWT is not configured")
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"JWT {settings.PERDIX_JWT}",
        "origin": settings.PERDIX_ORIGIN,
        "page_uri": "Page/Engine/management.BranchMaintenance",
        "referer": f"{settings.PERDIX_ORIGIN}/perdix-client/",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    
    # Build update payload with only provided fields
    organization_payload = {"id": organization_id}
    if payload.bank_id is not None:
        organization_payload["bankId"] = payload.bank_id
    if payload.parent_branch_id is not None:
        organization_payload["parentBranchId"] = payload.parent_branch_id
    if payload.branch_name is not None:
        organization_payload["branchName"] = payload.branch_name
    if payload.branch_mail_id is not None:
        organization_payload["branchMailId"] = str(payload.branch_mail_id)
    if payload.pin_code is not None:
        organization_payload["pinCode"] = payload.pin_code
    if payload.branch_open_date is not None:
        organization_payload["branchOpenDate"] = payload.branch_open_date
    if payload.cash_limit is not None:
        organization_payload["cashLimit"] = payload.cash_limit
    if payload.finger_print_device_type is not None:
        organization_payload["fingerPrintDeviceType"] = payload.finger_print_device_type
    # Add fields that are computed/server-side and not from frontend
    # Always include branchCode = id as per Perdix behavior in sample payloads
    organization_payload["branchCode"] = organization_id
    # Set version default to 0 if not provided from frontend
    organization_payload["version"] = 2
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.put(url, headers=headers, json=organization_payload)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    
    try:
        return response.json(), response.status_code, True
    except ValueError:
        return response.text, response.status_code, False


def update_organization_in_perdix_raw(payload: dict) -> tuple:
    """Update organization (branch) in Perdix using the exact frontend payload (no server-side mutation)."""
    base_url = settings.PERDIX_BASE_URL.rstrip("/")
    url = f"{base_url}/api/branch"

    if not settings.PERDIX_JWT:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perdix JWT is not configured")

    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"JWT {settings.PERDIX_JWT}",
        "origin": settings.PERDIX_ORIGIN,
        "page_uri": "Page/Engine/management.BranchMaintenance",
        "referer": f"{settings.PERDIX_ORIGIN}/perdix-client/",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.put(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    try:
        return response.json(), response.status_code, True
    except ValueError:
        return response.text, response.status_code, False


def get_organizations_from_perdix() -> tuple:
    """Get all organizations (branches) from Perdix system"""
    base_url = settings.PERDIX_BASE_URL.rstrip("/")
    url = f"{base_url}/api/branch"
    
    if not settings.PERDIX_JWT:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perdix JWT is not configured")
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"JWT {settings.PERDIX_JWT}",
        "origin": settings.PERDIX_ORIGIN,
        "referer": f"{settings.PERDIX_ORIGIN}/perdix-client/",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    
    try:
        return response.json(), response.status_code, True
    except ValueError:
        return response.text, response.status_code, False
