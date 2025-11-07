from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.master_service import fetch_roles_from_perdix


router = APIRouter()


@router.get("/roles")
def get_roles():
    body, status_code, is_json = fetch_roles_from_perdix()
    return JSONResponse(content=body if is_json else {"raw": body}, status_code=status_code)


