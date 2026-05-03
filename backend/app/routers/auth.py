"""
Authentication endpoints for user registration and login.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthTokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    normalize_email,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new local CoolAgent user account."""
    email = normalize_email(payload.email)
    existing = await db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        )

    now = datetime.now(timezone.utc)
    user = User(
        id=uuid.uuid4(),
        email=email,
        full_name=payload.full_name.strip() if payload.full_name else None,
        password_hash=hash_password(payload.password),
        role="technician",
        is_active=True,
        is_verified=False,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    await db.flush()
    return user


@router.post("/login", response_model=AuthTokenResponse)
async def login_user(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Validate credentials and return a bearer access token."""
    user = await authenticate_user(
        db,
        email=payload.email,
        password=payload.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password incorrectos",
        )

    user.last_login_at = datetime.now(timezone.utc)
    user.updated_at = user.last_login_at
    await db.flush()

    settings = get_settings()
    token = create_access_token(user_id=user.id, email=user.email)
    return AuthTokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=user,
    )


@router.get("/me", response_model=UserResponse)
async def read_me(
    current_user: User = Depends(get_current_user),
):
    """Return the authenticated user's profile."""
    return current_user
