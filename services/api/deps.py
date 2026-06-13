"""Shared API dependencies: auth, tenant context, role checks."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.auth.jwt import decode_token
from services.api.config import Settings, get_settings
from services.api.db import get_db
from services.api.exceptions import ForbiddenError
from services.api.models import Tenant, User
from services.api.services.rate_limit import bulk_limit, check_rate_limit, query_limit

DEFAULT_TENANT_NAME = "default-local"
_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    user: User | None
    tenant: Tenant
    role: str


async def get_or_create_default_tenant(db: AsyncSession) -> Tenant:
    result = await db.execute(select(Tenant).where(Tenant.name == DEFAULT_TENANT_NAME))
    tenant = result.scalar_one_or_none()
    if tenant is not None:
        return tenant
    tenant = Tenant(id=uuid.uuid4(), name=DEFAULT_TENANT_NAME, plan="pro")
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


async def set_rls_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> None:
    """Set Postgres session variable for row-level security policies."""
    await db.execute(
        text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )


async def get_auth_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> AuthContext:
    user: User | None = None

    if credentials is not None:
        try:
            payload = decode_token(credentials.credentials)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token required",
            )
        user_id = uuid.UUID(str(payload["sub"]))
        tenant_id = uuid.UUID(str(payload["tenant_id"]))
        user_row = await db.execute(select(User).where(User.id == user_id))
        user = user_row.scalar_one_or_none()
        if user is None or user.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        tenant_row = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = tenant_row.scalar_one()
        await set_rls_tenant(db, tenant.id)
        request.state.tenant_id = str(tenant.id)
        return AuthContext(user=user, tenant=tenant, role=user.role)

    if settings.require_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if x_tenant_id:
        try:
            tenant_uuid = uuid.UUID(x_tenant_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid X-Tenant-Id header",
            ) from exc
        tenant_row = await db.execute(select(Tenant).where(Tenant.id == tenant_uuid))
        header_tenant = tenant_row.scalar_one_or_none()
        if header_tenant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
        await set_rls_tenant(db, header_tenant.id)
        request.state.tenant_id = str(header_tenant.id)
        return AuthContext(user=None, tenant=header_tenant, role="admin")

    default_tenant = await get_or_create_default_tenant(db)
    await set_rls_tenant(db, default_tenant.id)
    request.state.tenant_id = str(default_tenant.id)
    return AuthContext(user=None, tenant=default_tenant, role="admin")


async def get_tenant_from_header(
    auth: AuthContext = Depends(get_auth_context),
) -> Tenant:
    return auth.tenant


def require_roles(*roles: str) -> Callable[..., Awaitable[AuthContext]]:
    allowed = set(roles)

    async def _check(
        request: Request,
        auth: AuthContext = Depends(get_auth_context),
    ) -> AuthContext:
        if auth.role not in allowed:
            raise ForbiddenError(
                f"Requires one of roles: {', '.join(sorted(allowed))}",
                request_id=getattr(request.state, "request_id", None),
            )
        return auth

    return _check


async def enforce_query_rate_limit(
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> AuthContext:
    await check_rate_limit(
        tenant_id=str(auth.tenant.id),
        bucket="query",
        limit=query_limit(),
        request_id=getattr(request.state, "request_id", None),
    )
    return auth


async def enforce_bulk_rate_limit(
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> AuthContext:
    await check_rate_limit(
        tenant_id=str(auth.tenant.id),
        bucket="bulk",
        limit=bulk_limit(),
        request_id=getattr(request.state, "request_id", None),
    )
    return auth
