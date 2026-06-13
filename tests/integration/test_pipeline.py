"""Integration tests for the agent pipeline graph path."""

from __future__ import annotations

from services.agents.pipeline import build_pipeline_graph


def test_pipeline_graph_compiles() -> None:
    graph = build_pipeline_graph()
    compiled = graph.compile()
    assert compiled is not None


def test_pipeline_graph_has_verification_gate() -> None:
    graph = build_pipeline_graph()
    node_names = set(graph.nodes.keys())
    expected = {
        "change_detector",
        "relevance_agent",
        "impact_analysis",
        "verification",
        "brief_generation",
    }
    assert expected.issubset(node_names)
