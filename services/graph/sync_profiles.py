"""Mirror Postgres client profiles into Neo4j."""

from __future__ import annotations

import logging

from neo4j import AsyncGraphDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.config import Settings, get_settings
from services.api.models import ClientProfile

logger = logging.getLogger(__name__)


async def sync_client_profile(
    profile: ClientProfile,
    *,
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    try:
        async with driver.session() as session:
            await session.run(
                """
                MERGE (cp:ClientProfile {client_id: $client_id})
                SET cp.name = $name
                """,
                client_id=str(profile.id),
                name=profile.name,
            )
            await session.run(
                """
                MATCH (cp:ClientProfile {client_id: $client_id})
                OPTIONAL MATCH (cp)-[r:CLASSIFIED_AS|OPERATES_IN]->()
                DELETE r
                """,
                client_id=str(profile.id),
            )
            for naics in profile.naics_codes:
                await session.run(
                    """
                    MATCH (cp:ClientProfile {client_id: $client_id})
                    MERGE (bc:BusinessCategory {naics_code: $naics_code})
                    MERGE (cp)-[:CLASSIFIED_AS]->(bc)
                    """,
                    client_id=str(profile.id),
                    naics_code=naics,
                )
            for state in profile.states_of_operation:
                await session.run(
                    """
                    MATCH (cp:ClientProfile {client_id: $client_id})
                    MERGE (j:Jurisdiction {code: $code})
                    MERGE (cp)-[:OPERATES_IN]->(j)
                    """,
                    client_id=str(profile.id),
                    code=f"US-{state}",
                )
    finally:
        await driver.close()


async def sync_client_profile_by_id(db: AsyncSession, client_id: object) -> ClientProfile | None:
    result = await db.execute(select(ClientProfile).where(ClientProfile.id == client_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        return None
    await sync_client_profile(profile)
    return profile


async def sync_all_profiles(db: AsyncSession, settings: Settings | None = None) -> int:
    result = await db.execute(select(ClientProfile))
    profiles = result.scalars().all()
    for profile in profiles:
        await sync_client_profile(profile, settings=settings)
    logger.info("Synced %d client profiles to Neo4j", len(profiles))
    return len(profiles)
