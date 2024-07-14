import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from common.constants import SECRET_KEY
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.orm import Session
from core.database.dependencies import get_database
from common.models import User
from authentication.schemas import UserBase

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCOUNT_ACTIVATION_TOKEN_EXPIRE_HOURS = 24
REFRESH_TOKEN_EXPIRE_DAYS = 30


# Configure the OAuth2PasswordBearer
# oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="token")


# Configure the password context to use pbkdf2_sha256
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_activation_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            hours=ACCOUNT_ACTIVATION_TOKEN_EXPIRE_HOURS
        )
    to_encode.update({"exp": expire, "token_type": "activation"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("token_type") != token_type:
            raise Exception("Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


def extract_token(request: Request) -> str:
    authorization: str = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authorization header missing or invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Annotated[str, Depends(extract_token)], db: Session = Depends(get_database)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token, token_type="access")
        token_type: str = payload.get("token_type")

        if token_type != "access":
            raise credentials_exception

        if not (user_id := payload.get("sub")):
            raise credentials_exception

        if not (user := db.query(User).filter_by(id=int(user_id)).first()):
            raise credentials_exception

        return user

    except Exception as e:
        raise credentials_exception from e


def get_current_active_user(
    current_user: Annotated[UserBase, Depends(get_current_user)]
):

    if current_user.is_deleted or not current_user.is_active:
        raise HTTPException(
            status_code=401, detail="User is not permitted to perform this action"
        )

    return current_user
