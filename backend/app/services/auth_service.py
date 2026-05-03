"""
Authentication helpers for password hashing and JWT access tokens.
"""

from datetime import datetime, timedelta, timezone
import hashlib
from uuid import UUID

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.user import User


ALGORITHM = "HS256"
PASSWORD_HASH_PREFIX = "bcrypt-sha256$"

bearer_scheme = HTTPBearer(auto_error=False)


def normalize_email(email: str) -> str:
    """Normalize emails for unique lookup."""
    return email.strip().lower()


def hash_password(password: str) -> str:
    digest = _password_digest(password)
    hashed = bcrypt.hashpw(digest, bcrypt.gensalt(rounds=12)).decode("utf-8")
    return f"{PASSWORD_HASH_PREFIX}{hashed}"


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash.startswith(PASSWORD_HASH_PREFIX):
        return False
    stored_hash = password_hash.removeprefix(PASSWORD_HASH_PREFIX).encode("utf-8")
    return bcrypt.checkpw(_password_digest(password), stored_hash)


def _password_digest(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).digest()


def create_access_token(
    *,
    user_id: UUID,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


async def authenticate_user(
    db: AsyncSession,
    *,
    email: str,
    password: str,
) -> User | None:
    user = await db.scalar(select(User).where(User.email == normalize_email(email)))
    if user is None or not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticacion requerido",
        )

    settings = get_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    try:
        parsed_user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    user = await db.get(User, parsed_user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    return user
