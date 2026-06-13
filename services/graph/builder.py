"""Neo4j knowledge graph builder."""

from __future__ import annotations

import logging

from neo4j import AsyncDriver, AsyncGraphDatabase

from services.api.config import Settings, get_settings
from services.graph.cross_references import CrossReference, extract_cross_references
from services.ingestion.models import ParsedDocument

logger = logging.getLogger(__name__)


class GraphBuilder:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def _driver(self) -> AsyncDriver:
        return AsyncGraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_user, self.settings.neo4j_password),
        )

    async def upsert_document(self, document: ParsedDocument) -> int:
        refs = []
        for clause in document.clauses:
            refs.extend(extract_cross_references(clause.clause_id, clause.text))

        driver = self._driver()
        try:
            async with driver.session() as session:
                await session.run(
                    """
                    MERGE (a:Agency {agency_id: $agency_id})
                    SET a.name = $agency_name, a.jurisdiction = $jurisdiction
                    """,
                    agency_id=document.agency,
                    agency_name=document.agency,
                    jurisdiction=document.jurisdiction,
                )
                await session.run(
                    """
                    MERGE (j:Jurisdiction {code: $jurisdiction_code})
                    """,
                    jurisdiction_code=(
                        "US" if document.jurisdiction == "US" else document.jurisdiction
                    ),
                )
                await session.run(
                    """
                    MERGE (r:Regulation {regulation_id: $regulation_id})
                    SET r.title = $title,
                        r.agency = $agency,
                        r.jurisdiction = $jurisdiction,
                        r.source = $source,
                        r.effective_date = date($effective_date)
                    WITH r
                    MATCH (a:Agency {agency_id: $agency})
                    MERGE (r)-[:ISSUED_BY]->(a)
                    WITH r
                    MATCH (j:Jurisdiction {code: $jurisdiction_code})
                    MERGE (r)-[:ENFORCED_IN]->(j)
                    """,
                    regulation_id=document.regulation_id,
                    title=document.title,
                    agency=document.agency,
                    jurisdiction=document.jurisdiction,
                    source=document.source,
                    effective_date=document.effective_date.isoformat(),
                    jurisdiction_code=(
                        "US" if document.jurisdiction == "US" else document.jurisdiction
                    ),
                )

                for clause in document.clauses:
                    await session.run(
                        """
                        MATCH (r:Regulation {regulation_id: $regulation_id})
                        MERGE (c:Clause {clause_id: $clause_id})
                        SET c.text = $text,
                            c.version_hash = $version_hash,
                            c.effective_date = date($effective_date)
                        MERGE (c)-[:PART_OF]->(r)
                        """,
                        regulation_id=document.regulation_id,
                        clause_id=clause.clause_id,
                        text=clause.text,
                        version_hash=document.version_hash,
                        effective_date=document.effective_date.isoformat(),
                    )

                for ref in refs:
                    await self._upsert_reference(session, ref)

        finally:
            await driver.close()

        logger.info(
            "Graph upsert complete for %s (%d clauses)", document.document_id, len(document.clauses)
        )
        return len(document.clauses)

    async def _upsert_reference(self, session: object, ref: CrossReference) -> None:
        if ref.relationship == "AMENDS":
            await session.run(  # type: ignore[attr-defined]
                """
                MATCH (source:Clause {clause_id: $source_clause_id})-[:PART_OF]->(sr:Regulation)
                MERGE (target:Regulation {regulation_id: $target_regulation_id})
                MERGE (sr)-[rel:AMENDS]->(target)
                SET rel.detected_at = datetime(), rel.confidence = $confidence
                """,
                source_clause_id=ref.source_clause_id,
                target_regulation_id=ref.target_regulation_id,
                confidence=ref.confidence,
            )
        elif ref.target_clause_id:
            await session.run(  # type: ignore[attr-defined]
                """
                MATCH (source:Clause {clause_id: $source_clause_id})
                MERGE (target:Clause {clause_id: $target_clause_id})
                MERGE (source)-[rel:REFERENCES]->(target)
                SET rel.confidence = $confidence
                """,
                source_clause_id=ref.source_clause_id,
                target_clause_id=ref.target_clause_id,
                confidence=ref.confidence,
            )

    async def fetch_clause_text(self, clause_id: str) -> str | None:
        driver = self._driver()
        try:
            async with driver.session() as session:
                result = await session.run(
                    "MATCH (c:Clause {clause_id: $clause_id}) RETURN c.text AS text",
                    clause_id=clause_id,
                )
                record = await result.single()
                return str(record["text"]) if record else None
        finally:
            await driver.close()
