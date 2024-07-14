from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from common.models import Child
from authentication.schemas import UserBase
from apps.child.schemas import ChildCreate, ChildUpdate
from fastapi import HTTPException, status
from datetime import date, datetime, time
from common.scheduler import schedule_job
from common.utils.emails import send_admin_email
from common.models import User


def read_own_children(
    current_user: UserBase,
    name: str,
    age: int,
    start_date: date,
    end_date: date,
    db: Session,
):
    query = db.query(Child).filter_by(parent=current_user)

    if name:
        query = query.filter(Child.name.ilike(f"%{name}%"))  # Case-insensitive search

    if age:
        query = query.filter(Child.age == age)

    if start_date:
        start_datetime = datetime.combine(start_date, time.min)  # Set time to 00:00:00
        query = query.filter(Child.created_at >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(end_date, time.max)  # Set time to 23:59:59
        query = query.filter(Child.created_at <= end_datetime)

    children = query.all()

    return {
        "status": status.HTTP_200_OK,
        "data": children,
    }


def add_child(current_user: UserBase, user: ChildCreate, db: Session):
    child = Child(
        parent=current_user,
        name=user.name,
        age=user.age,
        additional_info=user.additional_info,
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    admins = (
        db.query(User)
        .filter_by(is_superuser=True, is_active=True, is_deleted=False)
        .all()
    )
    admin_emails = [admin.email for admin in admins]

    # Send mail to admin when a new child is added
    schedule_job(
        300, send_admin_email, (child.name, child.parent.first_name, admin_emails)
    )

    content = {
        "status": status.HTTP_201_CREATED,
        "message": "Your child details have been added.",
        "data": child.to_dict(
            only=("id", "name", "age", "additional_info", "created_at")
        ),
    }
    return JSONResponse(content=content, status_code=status.HTTP_201_CREATED)


def update_child(current_user: UserBase, child_id: int, user: ChildUpdate, db: Session):
    child = (
        db.query(Child)
        .filter_by(id=child_id, parent=current_user, is_deleted=False)
        .first()
    )
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Child not found"
        )

    child.name = user.name if user.name else child.name
    child.age = user.age if user.age else child.age
    child.additional_info = (
        user.additional_info if user.additional_info else child.additional_info
    )
    db.commit()
    db.refresh(child)

    content = {
        "status": status.HTTP_200_OK,
        "message": "Your child details have been updated.",
        "data": child.to_dict(
            only=("id", "name", "age", "additional_info", "created_at", "updated_at")
        ),
    }
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)
