from pydantic import BaseModel, Field
from typing import Optional


class UserRoleCreate(BaseModel):
    role_name: str = Field(..., alias="roleName")
    role_access_level: int = Field(..., alias="roleAccessLevel")

    class Config:
        populate_by_name = True


class UserRoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, alias="roleName")
    role_access_level: Optional[int] = Field(None, alias="roleAccessLevel")

    class Config:
        populate_by_name = True


class UserRoleResponse(BaseModel):
    status: str
    message: str
    data: dict

    class Config:
        from_attributes = True


class UserRoleListResponse(BaseModel):
    status: str
    message: str
    data: list
    total: int

    class Config:
        from_attributes = True
