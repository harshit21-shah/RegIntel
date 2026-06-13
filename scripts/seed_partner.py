"""Seed a design partner tenant, admin user, and client profile."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import uuid
from pathlib import Path

from sqlalchemy import select

from services.api.auth.passwords import hash_password
from services.api.db import AsyncSessionLocal
from services.api.models import ClientProfile, Tenant, User
from services.graph.sync_profiles import sync_client_profile

logger = logging.getLogger(__name__)


async def seed_partner(
    *,
    tenant_name: str,
    admin_email: str,
    password: str,
    profile: dict[str, object],
) -> None:
    async with AsyncSessionLocal() as session:
        tenant_result = await session.execute(select(Tenant).where(Tenant.name == tenant_name))
        tenant = tenant_result.scalar_one_or_none()
        if tenant is None:
            tenant = Tenant(id=uuid.uuid4(), name=tenant_name, plan="pro")
            session.add(tenant)
            await session.flush()

        user_result = await session.execute(select(User).where(User.email == admin_email))
        user = user_result.scalar_one_or_none()
        if user is None:
            session.add(
                User(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    email=admin_email,
                    hashed_password=hash_password(password),
                    role="consultant",
                )
            )

        profile_name = str(profile["name"])
        existing_profile = await session.execute(
            select(ClientProfile).where(
                ClientProfile.tenant_id == tenant.id,
                ClientProfile.name == profile_name,
            )
        )
        client = existing_profile.scalar_one_or_none()
        if client is None:
            client = ClientProfile(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                name=profile_name,
                naics_codes=list(profile.get("naics_codes", [])),
                states_of_operation=list(profile.get("states_of_operation", [])),
                product_categories=list(profile.get("product_categories", [])),
                supply_chain_jurisdictions=list(profile.get("supply_chain_jurisdictions", [])),
            )
            session.add(client)

        await session.commit()
        await session.refresh(client)
        await sync_client_profile(client)
        logger.info("Partner tenant=%s profile=%s admin=%s", tenant.id, client.id, admin_email)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a RegIntel design partner")
    parser.add_argument("--tenant-name", required=True)
    parser.add_argument("--admin-email", required=True)
    parser.add_argument("--password", default="RegIntel-Partner-2025!")
    parser.add_argument("--profile-json", required=True, help="Path to profile JSON file")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    profile = json.loads(Path(args.profile_json).read_text(encoding="utf-8"))
    await seed_partner(
        tenant_name=args.tenant_name,
        admin_email=args.admin_email,
        password=args.password,
        profile=profile,
    )


if __name__ == "__main__":
    asyncio.run(main())
