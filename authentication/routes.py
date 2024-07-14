from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database.dependencies import get_database
from fastapi.responses import JSONResponse
from authentication import utils
from authentication.schemas import (
    UserLogin,
    RefreshTokenRequest,
    LoginOut,
    ActivateAccountRequest,
    ResendActivationLinkRequest,
)


router = APIRouter(tags=["Auth"])


@router.post("/login/", response_model=LoginOut)
def login(user: UserLogin, db: Session = Depends(get_database)):
    return utils.login(user, db)


@router.post("/refresh/", response_class=JSONResponse)
def refresh(request: RefreshTokenRequest, db: Session = Depends(get_database)):
    return utils.refresh(request, db)


@router.post("/activate/", response_class=JSONResponse)
def activate_account(
    request: ActivateAccountRequest, db: Session = Depends(get_database)
):
    return utils.activate_account(request, db)


@router.post("/activate/resend/", response_class=JSONResponse)
def resend_activation_link(
    request: ResendActivationLinkRequest, db: Session = Depends(get_database)
):
    return utils.resend_activation_link(request, db)
