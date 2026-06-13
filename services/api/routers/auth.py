"""Authentication endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.auth.jwt import create_access_token, create_refresh_token, decode_token
from services.api.auth.passwords import hash_password, verify_password
from services.api.config import Settings, get_settings
from services.api.db import get_db
from services.api.deps import AuthContext, get_auth_context
from services.api.models import Tenant, User
from services.api.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    tenant = Tenant(id=uuid.uuid4(), name=body.tenant_name, plan="pro")
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    db.add(tenant)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access = create_access_token(
        user_id=user.id,
        tenant_id=tenant.id,
        role=user.role,
        email=user.email,
    )
    refresh = create_refresh_token(user_id=user.id, tenant_id=tenant.id)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.jwt_access_expire_minutes * 60,
        tenant_id=tenant.id,
        role=user.role,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
        email=user.email,
    )
    refresh = create_refresh_token(user_id=user.id, tenant_id=user.tenant_id)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.jwt_access_expire_minutes * 60,
        tenant_id=user.tenant_id,
        role=user.role,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    try:
        payload = decode_token(body.refresh_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = uuid.UUID(str(payload["sub"]))
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access = create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
        email=user.email,
    )
    new_refresh = create_refresh_token(user_id=user.id, tenant_id=user.tenant_id)
    return TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
        expires_in=settings.jwt_access_expire_minutes * 60,
        tenant_id=user.tenant_id,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
async def me(auth: AuthContext = Depends(get_auth_context)) -> UserResponse:
    if auth.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    return UserResponse(
        user_id=auth.user.id,
        email=auth.user.email,
        role=auth.user.role,
        tenant_id=auth.tenant.id,
    )
