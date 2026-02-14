from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from graph.nodes import parse_query_node, discover_via_serp_node


def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("parse_query", parse_query_node)
    builder.add_node("discover_serp", discover_via_serp_node)

    builder.set_entry_point("parse_query")
    builder.add_edge("parse_query", "discover_serp")
    builder.add_edge("discover_serp", END)

    return builder.compile()
