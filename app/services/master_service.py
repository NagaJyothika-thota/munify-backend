import httpx
from fastapi import HTTPException, status
from app.core.config import settings


def fetch_roles_from_perdix() -> tuple:
    base = settings.PERDIX_ORIGIN.rstrip("/")
    path = "/management/user-management/allRoles.php"
    url = f"{base}{path}"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": settings.PERDIX_JWT,
        "origin": settings.PERDIX_ORIGIN,
        "referer": f"{settings.PERDIX_ORIGIN}/perdix-client/",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers)
            # Debug: log the response for troubleshooting
            print(f"Perdix API Response Status: {response.status_code}")
            print(f"Perdix API Response Headers: {dict(response.headers)}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    try:
        return response.json(), response.status_code, True
    except ValueError:
        return response.text, response.status_code, False


