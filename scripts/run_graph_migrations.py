"""Apply versioned Neo4j Cypher migrations."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from neo4j import AsyncGraphDatabase

from services.api.config import get_settings

logger = logging.getLogger(__name__)


async def run_migrations() -> None:
    settings = get_settings()
    migrations_dir = Path(__file__).resolve().parent.parent / "graph" / "migrations"
    migration_files = sorted(migrations_dir.glob("*.cypher"))

    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )

    async with driver.session() as session:
        await session.run("""
            MERGE (m:_MigrationMeta {id: 'singleton'})
            ON CREATE SET m.applied = []
            """)

        for path in migration_files:
            version = path.stem
            result = await session.run(
                "MATCH (m:_MigrationMeta {id: 'singleton'}) RETURN m.applied AS applied"
            )
            record = await result.single()
            applied: list[str] = record["applied"] if record else []

            if version in applied:
                logger.info("Skipping already applied migration: %s", version)
                continue

            cypher = path.read_text(encoding="utf-8")
            for statement in (s.strip() for s in cypher.split(";") if s.strip()):
                await session.run(statement)

            await session.run(
                """
                MATCH (m:_MigrationMeta {id: 'singleton'})
                SET m.applied = m.applied + $version
                """,
                version=version,
            )
            logger.info("Applied Neo4j migration: %s", version)

    await driver.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_migrations())


if __name__ == "__main__":
    main()
