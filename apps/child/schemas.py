from pydantic import BaseModel, Field, root_validator, validator
from typing import Optional
from typing import List
from datetime import datetime
import re


class ChildBase(BaseModel):
    parent_id: int
    name: str
    age: int
    additional_info: Optional[str] = None
    created_at: Optional[datetime]


class ChildOut(ChildBase):
    id: int

    class Config:
        from_attributes = True


class ChildrenList(BaseModel):
    status: int
    data: List[ChildOut]


class ChildCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    age: int = Field(..., example=3)
    additional_info: Optional[str] = Field(..., example="Example additional info")

    @validator("name")
    def validate_name(cls, value):
        if value:
            if not re.match(r"^[A-Za-z ]+$", value) and len(value) < 3:
                raise ValueError(
                    "Name should contains only alphabetic characters and spaces and must be at least 3 characters long"
                )
        return value

    @validator("age")
    def validate_age(cls, value):
        # Ensure that the age is a positive integer
        if value:
            if int(value) <= 0:
                raise ValueError("Age must be a positive integer")

        return value

    @root_validator(pre=True)
    def validate_fields(cls, values):
        name = values.get("name")
        age = values.get("age")

        if not name:
            raise ValueError("Name is required")

        if not age:
            raise ValueError("Age is required")

        return values


class ChildUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    additional_info: Optional[str] = None

    @validator("name")
    def validate_name(cls, value):
        if value:
            if not re.match(r"^[A-Za-z ]+$", value) and len(value) < 3:
                raise ValueError(
                    "Name should contains only alphabetic characters and spaces and must be at least 3 characters long"
                )
        return value

    @validator("age")
    def validate_age(cls, value):
        # Ensure that the age is a positive integer
        if value:
            if int(value) <= 0:
                raise ValueError("Age must be a positive integer")

        return value


