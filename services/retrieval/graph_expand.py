"""Expand retrieval candidates via Neo4j graph neighbors."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from neo4j import AsyncGraphDatabase

from services.api.config import Settings, get_settings
from services.retrieval.types import RetrievedClause

logger = logging.getLogger(__name__)

EXPAND_CYPHER = """
MATCH (seed:Clause {clause_id: $clause_id})
RETURN seed.clause_id AS clause_id, 0 AS hops, seed.text AS text,
       seed.section_number AS section_number, seed.title AS title
UNION
MATCH (seed:Clause {clause_id: $clause_id})-[:REFERENCES]->(c:Clause)
RETURN c.clause_id AS clause_id, 1 AS hops, c.text AS text,
       c.section_number AS section_number, c.title AS title
UNION
MATCH (seed:Clause {clause_id: $clause_id})-[:PART_OF]->(sr:Regulation)
      -[:AMENDS|REFERENCES*1..2]-(rel:Regulation)<-[:PART_OF]-(c:Clause)
RETURN c.clause_id AS clause_id, 2 AS hops, c.text AS text,
       c.section_number AS section_number, c.title AS title
"""


@dataclass(frozen=True)
class GraphClause:
    clause_id: str
    text: str
    hop_distance: int
    section_number: str
    title: str | None
    source_url: str


def _source_url(section_number: str) -> str:
    return f"https://www.ecfr.gov/current/title-21/section-{section_number}"


async def expand_from_clause(
    clause_id: str,
    *,
    settings: Settings | None = None,
) -> list[GraphClause]:
    settings = settings or get_settings()
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    clauses: list[GraphClause] = []
    seen: set[str] = set()
    try:
        async with driver.session() as session:
            result = await session.run(EXPAND_CYPHER, clause_id=clause_id)
            async for record in result:
                cid = str(record["clause_id"])
                if cid in seen or not record.get("text"):
                    continue
                seen.add(cid)
                section = str(record.get("section_number") or "")
                clauses.append(
                    GraphClause(
                        clause_id=cid,
                        text=str(record["text"]),
                        hop_distance=int(record.get("hops") or 0),
                        section_number=section,
                        title=str(record["title"]) if record.get("title") else None,
                        source_url=_source_url(section) if section else "",
                    )
                )
    except Exception:
        logger.exception("Graph expansion failed for %s", clause_id)
    finally:
        await driver.close()
    return clauses


def graph_clauses_to_retrieved(
    graph_clauses: list[GraphClause],
    *,
    regulation_id: str = "",
) -> list[RetrievedClause]:
    return [
        RetrievedClause(
            clause_id=item.clause_id,
            text=item.text,
            score=max(0.1, 1.0 - (item.hop_distance * 0.2)),
            regulation_id=regulation_id,
            source_url=item.source_url,
            section_number=item.section_number,
            title=item.title,
            hop_distance=item.hop_distance,
        )
        for item in graph_clauses
    ]


def merge_retrieved(
    *groups: list[RetrievedClause],
) -> list[RetrievedClause]:
    merged: dict[str, RetrievedClause] = {}
    for group in groups:
        for clause in group:
            existing = merged.get(clause.clause_id)
            if existing is None or clause.score > existing.score:
                merged[clause.clause_id] = clause
    return sorted(merged.values(), key=lambda item: item.score, reverse=True)
