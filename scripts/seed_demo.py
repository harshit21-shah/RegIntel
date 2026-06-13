"""Seed a demo client profile for local development."""

from __future__ import annotations

import asyncio
import logging
import uuid

from sqlalchemy import select

from services.api.auth.passwords import hash_password
from services.api.db import AsyncSessionLocal
from services.api.deps import get_or_create_default_tenant
from services.api.models import ClientProfile, User
from services.graph.sync_profiles import sync_client_profile

logger = logging.getLogger(__name__)

DEMO_PROFILE_NAME = "Acme Foods Inc."
DEMO_ADMIN_EMAIL = "admin@regintel.dev"
DEMO_ADMIN_PASSWORD = "RegIntel-Demo-2025!"


async def seed_demo_profile() -> uuid.UUID:
    async with AsyncSessionLocal() as session:
        tenant = await get_or_create_default_tenant(session)

        admin_result = await session.execute(select(User).where(User.email == DEMO_ADMIN_EMAIL))
        if admin_result.scalar_one_or_none() is None:
            session.add(
                User(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    email=DEMO_ADMIN_EMAIL,
                    hashed_password=hash_password(DEMO_ADMIN_PASSWORD),
                    role="admin",
                )
            )
            logger.info("Created demo admin user: %s", DEMO_ADMIN_EMAIL)

        result = await session.execute(
            select(ClientProfile).where(
                ClientProfile.tenant_id == tenant.id,
                ClientProfile.name == DEMO_PROFILE_NAME,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            logger.info("Demo profile already exists: %s", existing.id)
            await sync_client_profile(existing)
            return existing.id

        profile = ClientProfile(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            name=DEMO_PROFILE_NAME,
            naics_codes=["311412"],
            states_of_operation=["CA", "TX"],
            product_categories=["frozen seafood", "ready-to-eat meals"],
            supply_chain_jurisdictions=["MX"],
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        await sync_client_profile(profile)
        logger.info("Created demo profile: %s", profile.id)
        return profile.id


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    profile_id = asyncio.run(seed_demo_profile())
    print(f"Demo profile ID: {profile_id}")
    print(f"Demo admin: {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PASSWORD}")


if __name__ == "__main__":
    main()
