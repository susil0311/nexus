"""Auth API routes: login, refresh, /me, logout."""
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.models import User
from app.schemas.schemas import LoginRequest, TokenResponse, UserResponse
from app.services.audit_service import log_action

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email + password and receive a JWT."""
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    expires_in = settings.JWT_EXPIRY_MINUTES * 60
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email},
        expires_delta=timedelta(seconds=expires_in),
    )

    # update last_login
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(last_login=datetime.now(timezone.utc))
    )
    await db.commit()

    await log_action(
        db=db,
        user_id=user.id,
        action="login",
        entity="user",
        entity_id=user.id,
        old_value=None,
        new_value=None,
        ip=request.client.host if request.client else None,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


# ---------------------------------------------------------------------------
# POST /api/auth/login (form-based for OAuth2 clients / Swagger UI)
# ---------------------------------------------------------------------------

@router.post("/token", response_model=TokenResponse, include_in_schema=False)
async def login_form(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """OAuth2 password flow endpoint (used by Swagger UI)."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    expires_in = settings.JWT_EXPIRY_MINUTES * 60
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email},
        expires_delta=timedelta(seconds=expires_in),
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


# ---------------------------------------------------------------------------
# POST /api/auth/refresh
# ---------------------------------------------------------------------------

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
) -> TokenResponse:
    """Issue a new token for the authenticated user (sliding window refresh)."""
    expires_in = settings.JWT_EXPIRY_MINUTES * 60
    token = create_access_token(
        data={
            "sub": str(current_user.id),
            "role": current_user.role.value,
            "email": current_user.email,
        },
        expires_delta=timedelta(seconds=expires_in),
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.model_validate(current_user),
    )


# ---------------------------------------------------------------------------
# GET /api/auth/me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


# ---------------------------------------------------------------------------
# POST /api/auth/logout
# ---------------------------------------------------------------------------

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Stateless JWT logout – client discards the token.
    Logs the action for audit trail.
    """
    await log_action(
        db=db,
        user_id=current_user.id,
        action="logout",
        entity="user",
        entity_id=current_user.id,
        old_value=None,
        new_value=None,
        ip=request.client.host if request.client else None,
    )
