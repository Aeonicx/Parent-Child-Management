from sqlalchemy.orm import Session
from common.models import User
from apps.parent.schemas import ParentCreate, ParentProfileUpdate
from common.utils.emails import send_activation_email
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status, Request, UploadFile
from common.utils.auth import get_password_hash, create_activation_token
from authentication.schemas import UserBase
import shutil, uuid, os


def check_existing_user(user, db):
    """
    Check if the user already exists in the database.

    This function queries the database to see if a user with the given email exists.
    It then checks various conditions to determine if the account is in a proper
    state for further actions. If any condition fails, an HTTPException is raised
    with an appropriate error message.

    Parameters:
    - user: The user object containing user details.
    - db: The database session instance to perform queries.

    Raises:
    - HTTPException: If the user already exists with various states such as deleted,
                      not active or not a parent user.
    """
    # Query the database for a user with the given email
    existing_user = db.query(User).filter_by(email=user.email).first()

    if existing_user:
        # Check if the user's account is marked as deleted
        if existing_user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an account with us. Your account has been deactivated. Please contact support.",
            )

        # Check if the user's account is not active
        if not existing_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an account with us. Your account is not active. Please activate your account.",
            )

        # Check if the user is not marked as a parent user
        if not existing_user.is_parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_USER,
                detail="You already have an account with us. You are not a parent user. Please contact support.",
            )

        # If none of the above, the user exists and is an active, non-deleted parent user
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )


def register(user: ParentCreate, db: Session):
    # Check if user already exists
    check_existing_user(user, db)

    hashed_password = get_password_hash(user.password)
    parent = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hashed_password,
        is_parent=True,
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)

    # Generate an activation token (here we use a UUID for simplicity)
    activation_token = create_activation_token({"sub": parent.id})
    print(activation_token)

    # Send activation email
    send_activation_email(parent, activation_token)

    content = {
        "status": status.HTTP_201_CREATED,
        "message": "Your account has been created. Please check your email to activate your account.",
    }
    return JSONResponse(content=content, status_code=status.HTTP_201_CREATED)


def update_parent_profile(
    request: Request,
    current_user: UserBase,
    first_name: str,
    last_name: str,
    age: int,
    address: str,
    city: str,
    country: str,
    pin_code: str,
    profile_photo: UploadFile,
    db: Session,
):
    parent = current_user
    if first_name is not None:
        parent.first_name = first_name
    if last_name is not None:
        parent.last_name = last_name
    if age is not None:
        parent.age = age
    if address is not None:
        parent.address = address
    if city is not None:
        parent.city = city
    if country is not None:
        parent.country = country
    if pin_code is not None:
        parent.pin_code = pin_code

    if profile_photo is not None:
        # Ensure the photos directory exists
        os.makedirs("media/profile", exist_ok=True)

        # Generate a unique filename and define the path
        photo_filename = f"{uuid.uuid4()}.jpg"
        photo_path = f"media/profile/{photo_filename}"

        # Save the uploaded file
        with open(photo_path, "wb") as buffer:
            shutil.copyfileobj(profile_photo.file, buffer)

        parent.profile_photo = photo_path

    db.commit()
    db.refresh(parent)

    base_url = (
        str(request.url.scheme)
        + "://"
        + str(request.url.hostname)
        + (f":{request.url.port}" if request.url.port else "")
    )
    # Construct the photo URL
    profile_photo_url = (
        f"{base_url}/{parent.profile_photo}" if parent.profile_photo else None
    )

    parent_data = parent.to_dict(
        only=(
            "id",
            "first_name",
            "last_name",
            "age",
            "address",
            "city",
            "country",
            "pin_code",
        )
    )
    parent_data["profile_photo"] = profile_photo_url

    content = {
        "status": status.HTTP_201_CREATED,
        "message": "Profile updated successfully.",
        "data": parent_data,
    }
    return JSONResponse(content=content, status_code=status.HTTP_201_CREATED)


def get_parent_profile(
    request: Request,
    current_user: UserBase,
    db: Session,
):

    base_url = (
        str(request.url.scheme)
        + "://"
        + str(request.url.hostname)
        + (f":{request.url.port}" if request.url.port else "")
    )
    # Construct the photo URL
    profile_photo_url = (
        f"{base_url}/{current_user.profile_photo}"
        if current_user.profile_photo
        else None
    )

    data = current_user.to_dict(
        only=(
            "id",
            "first_name",
            "last_name",
            "age",
            "address",
            "city",
            "country",
            "pin_code",
            "is_superuser",
        )
    )
    data["profile_photo"] = profile_photo_url

    content = {
        "status": status.HTTP_201_CREATED,
        "message": "Profile updated successfully.",
        "data": data,
    }
    return JSONResponse(content=content, status_code=status.HTTP_201_CREATED)
