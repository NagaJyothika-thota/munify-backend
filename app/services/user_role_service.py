import httpx
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate


def create_user_role_in_perdix(payload: UserRoleCreate) -> tuple:
    """Create a new user role in Perdix system"""
    base = settings.PERDIX_ORIGIN.rstrip("/")
    url = f"{base}/management/user-management/updateRole.php"
    
    if not settings.PERDIX_JWT:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perdix JWT is not configured")
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"JWT {settings.PERDIX_JWT}",
        "origin": settings.PERDIX_ORIGIN,
        "referer": f"{settings.PERDIX_ORIGIN}/perdix-client/",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    
    role_payload = {
        "role_name": payload.role_name,
        "role_access_level": payload.role_access_level,
        "team_code": None
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.put(url, headers=headers, json=role_payload)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    
    try:
        return response.json(), response.status_code, True
    except ValueError:
        return response.text, response.status_code, False


def update_user_role_in_perdix(role_id: int, payload: UserRoleUpdate) -> tuple:
    """Update an existing user role in Perdix system"""
    base = settings.PERDIX_ORIGIN.rstrip("/")
    url = f"{base}/management/user-management/updateRole.php"
    
    if not settings.PERDIX_JWT:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Perdix JWT is not configured")
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "authorization": f"JWT {settings.PERDIX_JWT}",
        "origin": settings.PERDIX_ORIGIN,
        "referer": f"{settings.PERDIX_ORIGIN}/perdix-client/",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    
    # Build update payload with role_id and team_code as required by Perdix
    role_payload = {
        "role_id": role_id,
        "role_name": payload.role_name,
        "role_access_level": payload.role_access_level,
        "team_code": None
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.put(url, headers=headers, json=role_payload)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    
    try:
        return response.json(), response.status_code, True
    except ValueError:
        return response.text, response.status_code, False


def get_user_roles_from_perdix() -> tuple:
    """Get all user roles from Perdix system"""
    base = settings.PERDIX_ORIGIN.rstrip("/")
    url = f"{base}/management/user-management/allRoles.php"
    
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
