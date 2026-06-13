"""Seed BusinessCategory nodes and APPLIES_TO edges for food manufacturing."""

from __future__ import annotations

import logging

from neo4j import AsyncGraphDatabase

from services.api.config import Settings, get_settings

logger = logging.getLogger(__name__)

FOOD_MANUFACTURING_CATEGORIES = [
    ("311412", "Frozen Specialty Food Manufacturing"),
    ("311511", "Fluid Milk Manufacturing"),
    ("311999", "All Other Miscellaneous Food Manufacturing"),
    ("311615", "Poultry Processing"),
    ("311710", "Seafood Product Preparation and Packaging"),
]

REGULATION_APPLICABILITY = [
    ("ecfr-21-101", ["311412", "311511", "311999", "311710"]),
    ("ecfr-21-1", ["311412", "311511", "311999", "311615", "311710"]),
    ("ca-hsc-food-retail", ["311412", "311511", "311999"]),
]


async def seed_business_categories(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    try:
        async with driver.session() as session:
            for naics_code, description in FOOD_MANUFACTURING_CATEGORIES:
                await session.run(
                    """
                    MERGE (bc:BusinessCategory {naics_code: $naics_code})
                    SET bc.description = $description
                    """,
                    naics_code=naics_code,
                    description=description,
                )

            for regulation_id, naics_codes in REGULATION_APPLICABILITY:
                for naics_code in naics_codes:
                    await session.run(
                        """
                        MERGE (r:Regulation {regulation_id: $regulation_id})
                        MERGE (bc:BusinessCategory {naics_code: $naics_code})
                        MERGE (r)-[rel:APPLIES_TO]->(bc)
                        SET rel.confidence = 1.0, rel.source = 'manual_seed'
                        """,
                        regulation_id=regulation_id,
                        naics_code=naics_code,
                    )

            for state in ["US-CA", "US-TX", "US-NY"]:
                await session.run(
                    "MERGE (j:Jurisdiction {code: $code})",
                    code=state,
                )
    finally:
        await driver.close()
    logger.info("Seeded business categories and applicability edges")
