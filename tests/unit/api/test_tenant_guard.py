"""Tenant isolation guard tests."""

from __future__ import annotations

import uuid

import pytest

from services.api.exceptions import NotFoundError
from services.api.models import ClientProfile, Tenant
from services.api.services.tenant_guard import assert_brief_accessible, get_tenant_profile


@pytest.mark.asyncio
async def test_get_tenant_profile_returns_owned_profile(
    postgres_available: bool,
) -> None:
    if not postgres_available:
        pytest.skip("Postgres not available")

    from services.api.db import AsyncSessionLocal

    tenant_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    async with AsyncSessionLocal() as db:
        db.add(Tenant(id=tenant_id, name=f"tenant-{tenant_id}", plan="pro"))
        db.add(
            ClientProfile(
                id=profile_id,
                tenant_id=tenant_id,
                name="Acme Foods",
                naics_codes=["311"],
                states_of_operation=["CA"],
                product_categories=["snacks"],
                supply_chain_jurisdictions=["US"],
            )
        )
        await db.commit()

        profile = await get_tenant_profile(db, client_id=profile_id, tenant_id=tenant_id)
        assert profile.name == "Acme Foods"


@pytest.mark.asyncio
async def test_get_tenant_profile_rejects_cross_tenant(
    postgres_available: bool,
) -> None:
    if not postgres_available:
        pytest.skip("Postgres not available")

    from services.api.db import AsyncSessionLocal

    owner_tenant = uuid.uuid4()
    other_tenant = uuid.uuid4()
    profile_id = uuid.uuid4()
    async with AsyncSessionLocal() as db:
        db.add(Tenant(id=owner_tenant, name="owner", plan="pro"))
        db.add(Tenant(id=other_tenant, name="other", plan="pro"))
        db.add(
            ClientProfile(
                id=profile_id,
                tenant_id=owner_tenant,
                name="Acme Foods",
                naics_codes=["311"],
                states_of_operation=["CA"],
                product_categories=["snacks"],
                supply_chain_jurisdictions=["US"],
            )
        )
        await db.commit()

        with pytest.raises(NotFoundError):
            await get_tenant_profile(
                db,
                client_id=profile_id,
                tenant_id=other_tenant,
                request_id="req-123",
            )


@pytest.mark.asyncio
async def test_assert_brief_accessible_requires_tenant_match(
    postgres_available: bool,
) -> None:
    if not postgres_available:
        pytest.skip("Postgres not available")

    from datetime import date

    from services.api.db import AsyncSessionLocal
    from services.api.models import Brief, ChangeEvent

    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    profile_id = uuid.uuid4()
    change_id = uuid.uuid4()
    brief_id = uuid.uuid4()

    async with AsyncSessionLocal() as db:
        db.add(Tenant(id=tenant_id, name="owner", plan="pro"))
        db.add(Tenant(id=other_tenant, name="other", plan="pro"))
        db.add(
            ClientProfile(
                id=profile_id,
                tenant_id=tenant_id,
                name="Acme Foods",
                naics_codes=["311"],
                states_of_operation=["CA"],
                product_categories=["snacks"],
                supply_chain_jurisdictions=["US"],
            )
        )
        db.add(
            ChangeEvent(
                id=change_id,
                document_id="ecfr-21-101",
                clause_id="ecfr:21:101:101.1",
                change_type="MODIFIED",
                severity="SUBSTANTIVE",
                source="ecfr",
                effective_date=date(2025, 1, 1),
            )
        )
        db.add(
            Brief(
                id=brief_id,
                client_id=profile_id,
                change_event_id=change_id,
                title="Test brief",
                change_summary="Summary",
                severity="SUBSTANTIVE",
                obligations=[],
                recommended_actions=[],
                confidence=0.95,
                status="COMPLETE",
                disclaimer="Not legal advice.",
            )
        )
        await db.commit()

        await assert_brief_accessible(db, brief_id=brief_id, tenant_id=tenant_id)

        with pytest.raises(NotFoundError):
            await assert_brief_accessible(db, brief_id=brief_id, tenant_id=other_tenant)
