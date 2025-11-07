from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PartyBase(BaseModel):
    type: str
    legal_name: str
    registration_number: Optional[str] = None
    pan: Optional[str] = None
    gstn: Optional[str] = None
    status: Optional[str] = "PENDING"


class PartyCreate(PartyBase):
    pass


class PartyUpdate(BaseModel):
    legal_name: Optional[str] = None
    registered_numbers: Optional[str] = None
    contacts: Optional[str] = None
    party_type: Optional[str] = None
    status: Optional[str] = None


class PartyInDB(PartyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Party(PartyInDB):
    pass


class PartyResponse(BaseModel):
    status: str
    message: str
    data: Party

    class Config:
        from_attributes = True


class PartyListResponse(BaseModel):
    status: str
    message: str
    data: List[Party]
    total: int

    class Config:
        from_attributes = True


