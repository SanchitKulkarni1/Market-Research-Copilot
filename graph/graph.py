from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from graph.nodes import (
    clean_data_node, 
    parse_query_node, 
    discover_via_serp_node, 
    scrape_news_node,
    generate_report_node,
    evaluate_report_node  
)


def build_graph():
    builder = StateGraph(ResearchState)

    # Add all nodes
    builder.add_node("parse_query", parse_query_node)
    builder.add_node("discover_serp", discover_via_serp_node)
    builder.add_node("clean_data", clean_data_node)
    builder.add_node("scrape_news", scrape_news_node)
    builder.add_node("generate_report", generate_report_node)
    builder.add_node("evaluate_report", evaluate_report_node)  

    # Define edges (flow)
    builder.set_entry_point("parse_query")
    builder.add_edge("parse_query", "discover_serp")
    builder.add_edge("discover_serp", "clean_data")
    builder.add_edge("clean_data", "scrape_news")
    builder.add_edge("scrape_news", "generate_report")
    builder.add_edge("generate_report", "evaluate_report")  # ✅ Added
    builder.add_edge("evaluate_report", END)  # ✅ Added

    return builder.compile()