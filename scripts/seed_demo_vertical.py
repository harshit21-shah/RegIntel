"""Seed a complete demo vertical: Title 21 food-labeling change → graph → brief.

This makes a freshly deployed instance demo the full RegIntel flow out of the box:
a detected change event, multi-hop graph traversal to affected client profiles,
and a citation-backed verified brief on the dashboard — without depending on a
live LLM call at boot time (the interactive triage/query paths still run live).

Idempotent: safe to re-run. Reuses already-tested helpers (GraphBuilder,
ingest_parsed_document, sync_client_profile, seed_business_categories) so the
amount of novel, untested code is minimal.

Run after `scripts/seed_demo.py` (which creates the default tenant + admin):

    python scripts/seed_demo_vertical.py
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select

from services.agents.prompts.disclaimers import REGINTEL_DISCLAIMER
from services.api.db import AsyncSessionLocal
from services.api.deps import get_or_create_default_tenant
from services.api.models import Brief, BriefCitation, ChangeEvent, ClientProfile
from services.graph.builder import GraphBuilder
from services.graph.seed import seed_business_categories
from services.graph.sync_profiles import sync_client_profile
from services.ingestion.models import ParsedClause, ParsedDocument
from services.retrieval.embeddings import ecfr_source_url, ingest_parsed_document

logger = logging.getLogger(__name__)

REGULATION_ID = "ecfr-21-101"  # matches APPLIES_TO edges in services/graph/seed.py
DOCUMENT_ID = "ecfr-title21-101-demo"
VERSION_HASH = "demo-21cfr101-v2"

CLAUSE_NUTRITION = "ecfr:21:101:101.9"
CLAUSE_ALLERGEN = "ecfr:21:101:101.22"
CLAUSE_SUPPLEMENT = "ecfr:21:101:101.36"

# Verbatim-style text adapted from public-domain 21 CFR. The allergen cross-ref
# [ecfr:21:101:101.22] in the nutrition clause makes the graph show a REFERENCES hop.
DEMO_DOCUMENT = ParsedDocument(
    document_id=DOCUMENT_ID,
    source="ecfr",
    title="21 CFR Part 101 — Food Labeling",
    regulation_id=REGULATION_ID,
    agency="FDA",
    jurisdiction="US",
    effective_date=date(2026, 1, 1),
    version_hash=VERSION_HASH,
    clauses=[
        ParsedClause(
            clause_id=CLAUSE_NUTRITION,
            text=(
                "Nutrition information relating to food shall be provided for all "
                "products intended for human consumption and offered for sale. The "
                "declaration of nutrition information shall include the number of "
                "calories, and the amounts of total fat, saturated fat, trans fat, "
                "cholesterol, sodium, total carbohydrate, dietary fiber, total sugars, "
                "added sugars, protein, vitamin D, calcium, iron, and potassium per "
                "serving. Added sugars must be declared as a separate line item and "
                "expressed as a percent of the Daily Reference Value. Allergen source "
                "labeling for declared ingredients is governed by [ecfr:21:101:101.22]."
            ),
            parent_id=None,
            section_number="101.9",
            title="Nutrition labeling of food",
        ),
        ParsedClause(
            clause_id=CLAUSE_ALLERGEN,
            text=(
                "The label of a food to which any spice, flavoring, coloring, or "
                "chemical preservative has been added shall declare such ingredient. "
                "Where a major food allergen is present, the common or usual name of "
                "the food source shall be declared in the ingredient list or in a "
                "separate 'Contains' statement immediately following the ingredient "
                "list, in type size no smaller than the ingredient list."
            ),
            parent_id=None,
            section_number="101.22",
            title="Foods; labeling of spices, flavorings, colorings and chemical preservatives",
        ),
        ParsedClause(
            clause_id=CLAUSE_SUPPLEMENT,
            text=(
                "Nutrition labeling for dietary supplements shall be presented in a "
                "'Supplement Facts' panel. The panel shall list the serving size, the "
                "names and quantitative amounts of dietary ingredients, and the percent "
                "of Daily Value where one has been established."
            ),
            parent_id=None,
            section_number="101.36",
            title="Nutrition labeling of dietary supplements",
        ),
    ],
)

# Acme Foods Inc. (311412) is created by seed_demo.py; these add breadth to the
# affected-clients traversal so the demo shows more than one matched profile.
ADDITIONAL_PROFILES = [
    {
        "name": "Coastal Catch Seafood Co.",
        "naics_codes": ["311710"],
        "states_of_operation": ["CA", "WA"],
        "product_categories": ["frozen seafood", "canned tuna"],
        "supply_chain_jurisdictions": ["MX", "CL"],
    },
    {
        "name": "Harvest Valley Dairy",
        "naics_codes": ["311511"],
        "states_of_operation": ["WI", "MN"],
        "product_categories": ["fluid milk", "yogurt"],
        "supply_chain_jurisdictions": [],
    },
]

CHANGE_NEW_TEXT = (
    "Added sugars must be declared as a separate line item and expressed as a "
    "percent of the Daily Reference Value. Manufacturers with annual food sales "
    "of $10 million or more must comply by January 1, 2026."
)
CHANGE_OLD_TEXT = (
    "Total sugars must be declared. A separate declaration of added sugars is "
    "recommended but not required."
)


async def _ensure_profiles(session, tenant_id: uuid.UUID) -> list[ClientProfile]:
    profiles: list[ClientProfile] = []
    for spec in ADDITIONAL_PROFILES:
        result = await session.execute(
            select(ClientProfile).where(
                ClientProfile.tenant_id == tenant_id,
                ClientProfile.name == spec["name"],
            )
        )
        profile = result.scalar_one_or_none()
        if profile is None:
            profile = ClientProfile(id=uuid.uuid4(), tenant_id=tenant_id, **spec)
            session.add(profile)
            await session.flush()
            logger.info("Created demo profile: %s", spec["name"])
        profiles.append(profile)
    return profiles


async def _ensure_change_event(session) -> ChangeEvent:
    result = await session.execute(
        select(ChangeEvent).where(
            ChangeEvent.document_id == DOCUMENT_ID,
            ChangeEvent.clause_id == CLAUSE_NUTRITION,
        )
    )
    change = result.scalar_one_or_none()
    if change is not None:
        return change
    change = ChangeEvent(
        id=uuid.uuid4(),
        document_id=DOCUMENT_ID,
        clause_id=CLAUSE_NUTRITION,
        change_type="MODIFIED",
        severity="SUBSTANTIVE",
        old_text=CHANGE_OLD_TEXT,
        new_text=CHANGE_NEW_TEXT,
        effective_date=date(2026, 1, 1),
        source="ecfr",
    )
    session.add(change)
    await session.flush()
    logger.info("Created demo change event for %s", CLAUSE_NUTRITION)
    return change


def _demo_obligations() -> list[dict[str, object]]:
    return [
        {
            "text": (
                "Declare added sugars as a separate line item on the Nutrition Facts "
                "panel, expressed as a percent of the Daily Reference Value."
            ),
            "deadline": "2026-01-01",
            "citation_clause_ids": [CLAUSE_NUTRITION],
        },
        {
            "text": (
                "Ensure each major food allergen is named in the ingredient list or a "
                "'Contains' statement immediately following it."
            ),
            "deadline": None,
            "citation_clause_ids": [CLAUSE_ALLERGEN],
        },
    ]


def _demo_citations() -> list[dict[str, str]]:
    nutrition = DEMO_DOCUMENT.clauses[0]
    allergen = DEMO_DOCUMENT.clauses[1]
    return [
        {
            "clause_id": CLAUSE_NUTRITION,
            "source_url": ecfr_source_url(DEMO_DOCUMENT, nutrition),
            "excerpt": nutrition.text[:480],
        },
        {
            "clause_id": CLAUSE_ALLERGEN,
            "source_url": ecfr_source_url(DEMO_DOCUMENT, allergen),
            "excerpt": allergen.text[:480],
        },
    ]


async def _ensure_brief(session, *, client_id: uuid.UUID, change_id: uuid.UUID) -> None:
    existing = await session.execute(
        select(Brief).where(
            Brief.client_id == client_id,
            Brief.change_event_id == change_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        logger.info("Demo brief already exists for client %s", client_id)
        return

    brief = Brief(
        id=uuid.uuid4(),
        client_id=client_id,
        change_event_id=change_id,
        title="Added-Sugars Declaration Now Mandatory on Nutrition Facts Panel",
        change_summary=(
            "FDA's 21 CFR 101.9 now requires added sugars to be declared as a "
            "separate line item with a percent Daily Reference Value. Manufacturers "
            "with annual food sales of $10 million or more must comply by January 1, "
            "2026. This affects frozen and ready-to-eat product labels."
        ),
        severity="SUBSTANTIVE",
        obligations=_demo_obligations(),
        recommended_actions=[
            "Audit current Nutrition Facts panels for an explicit added-sugars line.",
            "Update label artwork and re-print packaging ahead of the Jan 1, 2026 deadline.",
            "Confirm allergen 'Contains' statements meet the 21 CFR 101.22 placement rule.",
        ],
        confidence=Decimal("0.94"),
        status="COMPLETE",
        disclaimer=REGINTEL_DISCLAIMER,
        generated_at=datetime.now(tz=UTC),
    )
    session.add(brief)
    await session.flush()
    for citation in _demo_citations():
        session.add(BriefCitation(id=uuid.uuid4(), brief_id=brief.id, **citation))
    logger.info("Created demo brief %s for client %s", brief.id, client_id)


async def seed_demo_vertical() -> None:
    # 1. Graph topology: business categories + APPLIES_TO edges for food NAICS.
    await seed_business_categories()

    # 2. Title 21 clauses into Neo4j (Clause-[:PART_OF]->Regulation, REFERENCES) and Qdrant.
    builder = GraphBuilder()
    await builder.upsert_document(DEMO_DOCUMENT)
    embedded = await ingest_parsed_document(DEMO_DOCUMENT)
    logger.info("Embedded %d demo clauses to Qdrant", embedded)

    async with AsyncSessionLocal() as session:
        tenant = await get_or_create_default_tenant(session)

        # 3. Anchor client (Acme Foods, 311412) created by seed_demo.py.
        acme_result = await session.execute(
            select(ClientProfile).where(
                ClientProfile.tenant_id == tenant.id,
                ClientProfile.name == "Acme Foods Inc.",
            )
        )
        acme = acme_result.scalar_one_or_none()

        # 4. Additional affected profiles, then sync everything to the graph.
        extra_profiles = await _ensure_profiles(session, tenant.id)
        await session.commit()

        all_profiles = ([acme] if acme is not None else []) + extra_profiles
        for profile in all_profiles:
            await sync_client_profile(profile)

        # 5. Change event + a verified, citation-backed brief for the anchor client.
        change = await _ensure_change_event(session)
        if acme is not None:
            await _ensure_brief(session, client_id=acme.id, change_id=change.id)
        await session.commit()

    logger.info("Demo vertical seed complete.")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_demo_vertical())
    print("Demo vertical seeded: Title 21 food-labeling change + affected clients + brief.")


if __name__ == "__main__":
    main()
