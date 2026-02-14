from graph.state import ResearchState
from llm.queryparser import parse_query
from tools.serp import serp_discover


async def parse_query_node(state: ResearchState) -> ResearchState:
    try:
        parsed = await parse_query(state["query"])
        state["product_name"] = parsed.product_name
        state["category"] = parsed.category
        state["keywords"] = parsed.keywords
    except Exception as e:
        state["errors"].append(str(e))

    return state


def discover_via_serp_node(state: ResearchState) -> ResearchState:
    if not state["keywords"]:
        state["errors"].append("No keywords for Serp discovery")
        return state

    try:
        site, competitors = serp_discover(
            keywords=state["keywords"],
            product_name=state["product_name"],
            category=state["category"],
)
        state["official_site"] = site
        state["competitors"] = competitors
    except Exception as e:
        state["errors"].append(str(e))

    return state
