from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database.dependencies import get_database
from authentication.schemas import UserBase
from typing import Annotated, Optional
from common.utils.auth import get_current_active_user
from apps.child import utils
from apps.child.schemas import ChildrenList, ChildCreate, ChildOut, ChildUpdate
from datetime import date


router = APIRouter(tags=["Child"])


@router.get("/", response_model=ChildrenList)
def read_own_children(
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
    name: Optional[str] = None,
    age: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_database),
):
    return utils.read_own_children(current_user, name, age, start_date, end_date, db)


@router.post("/", response_model=ChildOut)
def add_child(
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
    user: ChildCreate,
    db: Session = Depends(get_database),
):
    return utils.add_child(current_user, user, db)


@router.patch("/", response_model=ChildUpdate)
def update_child(
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
    child_id: int,
    user: ChildUpdate,
    db: Session = Depends(get_database),
):
    return utils.update_child(current_user, child_id, user, db)
