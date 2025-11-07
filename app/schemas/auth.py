from pydantic import BaseModel, Field


class ChangePasswordWithOTP(BaseModel):
    """Schema for changing password with OTP verification."""
    otp: str = Field(..., description="OTP code received by user")
    userId: str = Field(..., description="User ID")
    newPassword: str = Field(..., description="New password")
    confirmPassword: str = Field(..., description="Confirm new password")

    class Config:
        populate_by_name = True


