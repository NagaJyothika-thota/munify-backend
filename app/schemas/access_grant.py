from pydantic import BaseModel
from typing import Optional, List


class AccessGrantBase(BaseModel):
    granted_to_party_id: int
    permission: str
    granted_via: Optional[str] = "open"
    expires_at: Optional[str] = None


class AccessGrantCreate(AccessGrantBase):
    pass


class AccessGrantInDB(AccessGrantBase):
    id: int
    project_id: int  # Changed from listing_id to project_id

    class Config:
        from_attributes = True


class AccessGrant(AccessGrantInDB):
    pass


class AccessGrantResponse(BaseModel):
    status: str
    message: str
    data: AccessGrant

    class Config:
        from_attributes = True


class AccessGrantListResponse(BaseModel):
    status: str
    message: str
    data: List[AccessGrant]
    total: int

    class Config:
        from_attributes = True


