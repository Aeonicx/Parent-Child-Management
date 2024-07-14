from pydantic import BaseModel, Field, root_validator, validator
from typing import Optional
from apps.parent.schemas import ParentOut
import re


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    age: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    pin_code: Optional[str] = None
    profile_photo: Optional[str] = None

    is_active: bool
    is_parent: bool
    is_superuser: bool
    is_deleted: bool

    class Config:
        from_attributes = True


class LoginOut(BaseModel):
    access_token: str
    refresh_token: str
    data: ParentOut


class UserLogin(BaseModel):
    email: str = Field(..., example="example@gmail.com")
    password: str = Field(..., example="StrongPassword@1234")

    @validator("email")
    def validate_email(cls, value):
        if value:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                raise ValueError("Invalid email address")
        return value

    @root_validator(pre=True)
    def validate_fields(cls, values):
        email = values.get("email")
        password = values.get("password")

        if not email:
            raise ValueError("Email is required")

        if not password:
            raise ValueError("Password is required")

        return values


class RefreshTokenRequest(BaseModel):
    token: str


class ActivateAccountRequest(BaseModel):
    token: str


class ResendActivationLinkRequest(BaseModel):
    email: str = Field(..., example="example@gmail.com")

    @validator("email")
    def validate_email(cls, value):
        if value:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                raise ValueError("Invalid email address")
        return value