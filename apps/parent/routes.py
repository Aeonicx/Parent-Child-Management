from fastapi import APIRouter, Depends, Request, File, UploadFile, Form
from sqlalchemy.orm import Session
from core.database.dependencies import get_database
from apps.parent import utils
from apps.parent.schemas import ParentOut, ParentCreate, ParentProfileUpdate
from typing import Annotated
from authentication.schemas import UserBase
from common.utils.auth import get_current_active_user
from typing import Optional


router = APIRouter(tags=["Parent"])


@router.post("/register/", response_model=ParentOut)
def register(user: ParentCreate, db: Session = Depends(get_database)):
    return utils.register(user, db)


@router.patch("/profile/", response_model=ParentOut)
def update_parent_profile(
    request: Request,
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    pin_code: Optional[str] = Form(None),
    profile_photo: UploadFile = File(None),
    db: Session = Depends(get_database),
):

    return utils.update_parent_profile(
        request,
        current_user,
        first_name,
        last_name,
        age,
        address,
        city,
        country,
        pin_code,
        profile_photo,
        db,
    )


@router.get("/profile/", response_model=ParentOut)
def get_parent_profile(
    request: Request,
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
    db: Session = Depends(get_database),
):
    return utils.get_parent_profile(request, current_user, db)
