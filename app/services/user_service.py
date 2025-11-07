import httpx
from fastapi import HTTPException, status
from app.core.config import settings


def create_user_in_perdix(payload: dict) -> tuple:
    base_url = settings.PERDIX_BASE_URL.rstrip("/")
    url = f"{base_url}/api/users"

    if not settings.PERDIX_JWT:
        # Configuration issue on our side; not a Perdix error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perdix JWT is not configured")

    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"JWT {settings.PERDIX_JWT}",
        "origin": settings.PERDIX_ORIGIN,
        "page_uri": settings.PERDIX_PAGE_URI,
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        # Network/transport error, not a Perdix application response
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    # Return raw Perdix response body and status for the caller to forward
    try:
        body = response.json()
        return body, response.status_code, True
    except ValueError:
        return response.text, response.status_code, False


def update_user_roles_in_perdix(user_payload: dict) -> tuple:
    base_url = settings.PERDIX_BASE_URL.rstrip("/")
    url = f"{base_url}/api/users"

    if not settings.PERDIX_JWT:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perdix JWT is not configured")

    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"JWT {settings.PERDIX_JWT}",
        "origin": settings.PERDIX_ORIGIN,
        "page_uri": "Page/Engine/management.UserRoles",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.put(url, headers=headers, json=user_payload)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    try:
        body = response.json()
        return body, response.status_code, True
    except ValueError:
        return response.text, response.status_code, False


def _build_user_create_payload(payload) -> dict:
    return {
        "roleCode": "A",
        "activated": True,
        "userState": "ACTIVE",
        "userType": "A",
        "bankName": "Witfin",
        "validUntil": "2035-09-22",
        "accessType": "BRANCH",
        "imeiNumber": "",
        "langKey": "en",
        "userRoles": [],
        "userBranches": [],
        "userName": getattr(payload, "full_name", None) if hasattr(payload, "full_name") else payload.get("fullName"),
        "login": getattr(payload, "login", None) if hasattr(payload, "login") else payload.get("login"),
        "password": getattr(payload, "password", None) if hasattr(payload, "password") else payload.get("password"),
        "confirmPassword": getattr(payload, "confirm_password", None) if hasattr(payload, "confirm_password") else payload.get("confirmPassword"),
        "email": str(getattr(payload, "email", None)) if hasattr(payload, "email") else payload.get("email"),
        "mobileNumber": getattr(payload, "mobile_number", None) if hasattr(payload, "mobile_number") else payload.get("mobileNumber"),
        "branchId": 12,
        "branchName": "Head Office",
        "changePasswordOnLogin": True,
    }


def _build_role_update_payload(created_body: dict, payload) -> dict:
    mobile_number = getattr(payload, "mobile_number", None) if hasattr(payload, "mobile_number") else payload.get("mobileNumber")
    return {
        "id": (created_body or {}).get("id"),
        "version": (created_body or {}).get("version", 0),
        "login": getattr(payload, "login", None) if hasattr(payload, "login") else payload.get("login"),
        "password": None,
        "userName": getattr(payload, "full_name", None) if hasattr(payload, "full_name") else payload.get("fullName"),
        "changePasswordOnLogin": True,
        "firstName": None,
        "lastName": None,
        "email": str(getattr(payload, "email", None)) if hasattr(payload, "email") else payload.get("email"),
        "langKey": "en",
        "roleCode": "A",
        "activated": True,
        "roles": None,
        "branchSetCode": None,
        "bankName": "Witfin",
        "branchName": "Head Office",
        "agentAmtLimit": None,
        "imeiNumber": "",
        "branchId": 12,
        "branchCode": None,
        "userState": "ACTIVE",
        "activeBranch": "Head Office",
        "activeBranchId": None,
        "userType": "A",
        "mobileNumber": str(mobile_number) if mobile_number is not None else None,
        "landlineNumber": None,
        "validUntil": "2035-09-22",
        "lastPasswordUpdatedOn": (created_body or {}).get("lastPasswordUpdatedOn"),
        "accessType": "BRANCH",
        "customerId": None,
        "villageName": None,
        "editCheckerAccess": False,
        "agentAllVillageAccess": False,
        "urnNo": None,
        "agentId": None,
        "employeeId": None,
        "mobileNumber2": None,
        "userRoles": getattr(payload, "user_roles", None) if hasattr(payload, "user_roles") else payload.get("userRoles"),
        "userBranches": [
            {
                "id": None,
                "version": 0,
                "userId": getattr(payload, "login", None) if hasattr(payload, "login") else payload.get("login"),
                "branchId": 12,
            }
        ],
        "partnerCode": None,
        "otp": None,
        "otpPurpose": None,
        "allowedDevices": [],
        "userAccountLockStatus": None,
        "accountLockedAt": None,
        "accountLockReason": None,
        "imeiOverrideRequired": False,
        "mfaToken": None,
        "mfaTokenExpired": None,
        "mfaRequired": False,
        "photoImageId": None,
        "externalSystemCode": None,
        "apiUser": False,
        "hsmUserId": None,
    }


def register_user_with_optional_roles(payload) -> tuple:
    # Build user creation payload and call Perdix
    create_payload = _build_user_create_payload(payload)
    body, status_code, is_json = create_user_in_perdix(create_payload)

    # If creation failed or no roles provided, return the creation response
    roles = getattr(payload, "user_roles", None) if hasattr(payload, "user_roles") else (payload.get("userRoles") if isinstance(payload, dict) else None)
    if status_code not in (200, 201) or not roles:
        return body, status_code, is_json

    # Build roles payload and call update
    role_update_payload = _build_role_update_payload(body if isinstance(body, dict) else {}, payload)
    role_body, role_status, role_is_json = update_user_roles_in_perdix(role_update_payload)

    if role_status not in (200, 201):
        return role_body, role_status, role_is_json

    return {
        "status": "success",
        "message": "User created and roles assigned",
        "user": body,
        "rolesUpdate": role_body,
    }, 201, True


