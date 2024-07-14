from pydantic import BaseModel, Field, root_validator, validator
from typing import Optional
import re


class ParentBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    is_active: bool
    is_superuser: bool
    age: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    pin_code: Optional[str] = None
    profile_photo: Optional[str] = None


class ParentOut(ParentBase):
    id: int

    class Config:
        from_attributes = True


class ParentCreate(BaseModel):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    email: str = Field(..., example="example@gmail.com")
    password: str = Field(..., example="StrongPassword@1234")

    @validator("first_name")
    def validate_first_name(cls, value):
        if value:
            if not re.match(r"^[A-Za-z ]+$", value) and len(value) < 3:
                raise ValueError(
                    "First name should contains only alphabetic characters and spaces and must be at least 3 characters long"
                )
        return value

    @validator("last_name")
    def validate_last_name(cls, value):
        if value:
            if not re.match(r"^[A-Za-z ]+$", value) and len(value) < 3:
                raise ValueError(
                    "Last name should contains only alphabetic characters and spaces and must be at least 3 characters long"
                )
        return value

    @validator("email")
    def validate_email(cls, value):
        if value:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                raise ValueError("Invalid email address")
        return value

    @validator("password")
    def validate_password(cls, value):
        if value:
            if len(value) < 8:
                raise ValueError("Password must be at least 8 characters long")

            if not re.match(
                r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
                value,
            ):
                raise ValueError(
                    "Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character"
                )
        return value

    @root_validator(pre=True)
    def validate_fields(cls, values):
        first_name = values.get("first_name")
        last_name = values.get("last_name")
        email = values.get("email")
        password = values.get("password")

        if not first_name:
            raise ValueError("First name is required")

        if not last_name:
            raise ValueError("Last name is required")

        if not email:
            raise ValueError("Email is required")

        if not password:
            raise ValueError("Password is required")

        return values


class ParentProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    pin_code: Optional[str] = None

    @validator("first_name")
    def validate_first_name(cls, value):
        if value:
            if not re.match(r"^[A-Za-z ]+$", value) and len(value) < 3:
                raise ValueError(
                    "First name should contains only alphabetic characters and spaces and must be at least 3 characters long"
                )
        return value

    @validator("last_name")
    def validate_last_name(cls, value):
        if value:
            if not re.match(r"^[A-Za-z ]+$", value) and len(value) < 3:
                raise ValueError(
                    "Last name should contains only alphabetic characters and spaces and must be at least 3 characters long"
                )
        return value

    @validator("age")
    def validate_age(cls, value):
        # Ensure that the age is a positive integer
        if value:
            if int(value) <= 0:
                raise ValueError("Age must be a positive integer")
        return value
