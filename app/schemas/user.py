from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.party import Party

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str  # ADMIN, SELLER, BUYER
    party_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class ExternalUserRegistration(BaseModel):
    full_name: str = Field(..., alias="fullName")
    login: str
    password: str
    confirm_password: str = Field(..., alias="confirmPassword")
    email: EmailStr
    mobile_number: int = Field(..., alias="mobileNumber")
    user_roles: Optional[List[dict]] = Field(default=None, alias="userRoles")

    class Config:
        populate_by_name = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    party_id: Optional[int] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class UserResponse(BaseModel):
    status: str
    message: str
    data: User

    class Config:
        from_attributes = True


class UserWithParty(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    party: Optional[Party] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    status: str
    message: str
    data: List[User]
    total: int

    class Config:
        from_attributes = True


class UserAndPartyResponse(BaseModel):
    status: str
    message: str
    data: UserWithParty

    class Config:
        from_attributes = True
