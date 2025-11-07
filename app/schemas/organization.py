from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class OrganizationCreate(BaseModel):
    bank_id: int = Field(..., alias="bankId")
    parent_branch_id: int = Field(..., alias="parentBranchId")
    branch_name: str = Field(..., alias="branchName")
    branch_mail_id: EmailStr = Field(..., alias="branchMailId")
    pin_code: int = Field(..., alias="pinCode")
    branch_open_date: str = Field(..., alias="branchOpenDate")
    cash_limit: int = Field(default=0, alias="cashLimit")
    finger_print_device_type: str = Field(default="SAGEM", alias="fingerPrintDeviceType")

    class Config:
        populate_by_name = True


class OrganizationUpdate(BaseModel):
    bank_id: Optional[int] = Field(None, alias="bankId")
    parent_branch_id: Optional[int] = Field(None, alias="parentBranchId")
    branch_name: Optional[str] = Field(None, alias="branchName")
    branch_mail_id: Optional[EmailStr] = Field(None, alias="branchMailId")
    pin_code: Optional[int] = Field(None, alias="pinCode")
    branch_open_date: Optional[str] = Field(None, alias="branchOpenDate")
    cash_limit: Optional[int] = Field(None, alias="cashLimit")
    finger_print_device_type: Optional[str] = Field(None, alias="fingerPrintDeviceType")

    class Config:
        populate_by_name = True


class OrganizationResponse(BaseModel):
    status: str
    message: str
    data: dict

    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    status: str
    message: str
    data: list
    total: int

    class Config:
        from_attributes = True
