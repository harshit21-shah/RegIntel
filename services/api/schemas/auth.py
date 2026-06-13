"""Auth request/response schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    tenant_name: str = Field(min_length=2, max_length=120)
    role: str = Field(default="consultant", pattern="^(admin|consultant|viewer)$")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    tenant_id: UUID
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    role: str
    tenant_id: UUID
