from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CommitmentBase(BaseModel):
    amount: Decimal
    status: Optional[str] = "ACTIVE"


class CommitmentCreate(CommitmentBase):
    project_id: int
    party_id: int
    user_id: int


class CommitmentUpdate(BaseModel):
    amount: Optional[Decimal] = None
    status: Optional[str] = None


class CommitmentInDB(CommitmentBase):
    id: int
    project_id: int
    party_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Commitment(CommitmentInDB):
    pass


class CommitmentResponse(BaseModel):
    status: str
    message: str
    data: Commitment

    class Config:
        from_attributes = True


class CommitmentListResponse(BaseModel):
    status: str
    message: str
    data: List[Commitment]
    total: int

    class Config:
        from_attributes = True


