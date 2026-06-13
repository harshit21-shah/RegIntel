"""Pydantic schemas for client profile endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProfileCreate(BaseModel):
    name: str
    naics_codes: list[str] = Field(default_factory=list)
    states_of_operation: list[str] = Field(default_factory=list)
    product_categories: list[str] = Field(default_factory=list)
    supply_chain_jurisdictions: list[str] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    name: str | None = None
    naics_codes: list[str] | None = None
    states_of_operation: list[str] | None = None
    product_categories: list[str] | None = None
    supply_chain_jurisdictions: list[str] | None = None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    client_id: UUID = Field(alias="id")
    name: str
    naics_codes: list[str]
    states_of_operation: list[str]
    product_categories: list[str]
    supply_chain_jurisdictions: list[str]
    created_at: datetime
    updated_at: datetime


class ProfileListResponse(BaseModel):
    items: list[ProfileResponse]
    page: int
    page_size: int
    total: int
