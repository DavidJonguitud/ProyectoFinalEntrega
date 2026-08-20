from datetime import UTC, datetime, timedelta
from typing import Any

from bcrypt import checkpw, gensalt, hashpw
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.core.config import settings

reusable_oauth = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")


def hash_password(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str | Any, expires_delta: int | None = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(UTC) + expires_delta
    else:
        expires_delta = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str | Any, expires_delta: int | None = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(UTC) + expires_delta
    else:
        expires_delta = datetime.now(UTC) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_REFRESH_SECRET_KEY, settings.ALGORITHM
    )
    return encoded_jwt


def decode_user_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])


def create_project_invitation_token(
    project_id: int, invited_email: str, expiration_days: int = 2
) -> str:
    expire = datetime.now(UTC) + timedelta(days=expiration_days)

    to_encode = {
        "exp": expire,
        "sub": invited_email,
        "project_id": project_id,
        "token_type": "invitation",
    }

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
