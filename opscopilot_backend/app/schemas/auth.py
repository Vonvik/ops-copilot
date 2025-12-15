from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints

NewPassword = Annotated[str, StringConstraints(min_length=8)]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenIn(BaseModel):
    refresh_token: str


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: NewPassword
