from sqlalchemy.orm import Session
from common.models import User
from common.utils.emails import send_activation_email
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from common.utils.auth import create_activation_token
from authentication.schemas import (
    UserLogin,
    RefreshTokenRequest,
    ActivateAccountRequest,
    ResendActivationLinkRequest,
)
from common.utils.auth import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)


def check_existing_user(user, db):
    existing_user = db.query(User).filter_by(email=user.email).first()
    if existing_user:
        if not verify_password(user.password, existing_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if existing_user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your account has been deactivated. Please contact support.",
            )

        if not existing_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your account is not active. Please activate your account.",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return existing_user


def login(user: UserLogin, db: Session):
    # Validate user
    db_user = check_existing_user(user, db)

    access_token = create_access_token(data={"sub": db_user.id})
    refresh_token = create_refresh_token(data={"sub": db_user.id})

    user_dict = db_user.to_dict(
        only=(
            "id",
            "email",
            "first_name",
            "last_name",
            "age",
            "address",
            "city",
            "country",
            "pin_code",
            "profile_photo",
            "is_superuser",
            "is_parent",
        )
    )

    content = {
        "status": status.HTTP_200_OK,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "data": user_dict,
    }
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


def refresh(request: RefreshTokenRequest, db: Session):
    try:
        payload = verify_token(request.token, token_type="refresh")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        new_access_token = create_access_token(data={"sub": user_id})
        content = {
            "status": status.HTTP_200_OK,
            "token_type": "access",
            "token": new_access_token,
        }
        return JSONResponse(content=content, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


def activate_account(request: ActivateAccountRequest, db: Session):
    payload = verify_token(request.token, token_type="activation")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid activation token",
        )

    db_user = db.query(User).filter_by(id=user_id).first()
    if db_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account has been deactivated. Please contact support.",
        )

    if db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account is already active. Please login.",
        )

    db_user.is_active = True
    db.commit()

    content = {
        "status": status.HTTP_200_OK,
        "message": "Account activated successfully. You can now login.",
    }
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


def resend_activation_link(request: ResendActivationLinkRequest, db: Session):
    db_user = db.query(User).filter_by(email=request.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email does not exist",
        )

    if db_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account has been deactivated. Please contact support.",
        )

    if db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account is already active. Please login.",
        )

    activation_token = create_activation_token({"sub": db_user.id})
    send_activation_email(db_user, activation_token)

    content = {
        "status": status.HTTP_200_OK,
        "message": "Activation link sent to your email.",
    }
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)
