"""Read-only agent tools for graph, vector, and clause lookup."""

from __future__ import annotations

from typing import Any, cast

from services.graph.builder import GraphBuilder
from services.retrieval.search import ClauseRetriever
from services.retrieval.types import RetrievedClause


async def graph_query(cypher: str, **params: object) -> list[dict[str, object]]:
    builder = GraphBuilder()
    driver = builder._driver()
    try:
        async with driver.session() as session:
            result = await session.run(cypher, **cast(Any, params))
            records = await result.data()
            return records
    finally:
        await driver.close()


async def vector_search(
    query: str, *, top_k: int = 5, jurisdiction: str = "US"
) -> list[RetrievedClause]:
    retriever = ClauseRetriever()
    return await retriever.search(query, top_k=top_k, jurisdiction=jurisdiction)


async def fetch_clause(clause_id: str) -> str | None:
    builder = GraphBuilder()
    return await builder.fetch_clause_text(clause_id)
