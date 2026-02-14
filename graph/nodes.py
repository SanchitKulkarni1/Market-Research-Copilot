from graph.state import ResearchState
from llm.queryparser import parse_query
from tools.serp import run_full_market_research 

async def parse_query_node(state: ResearchState) -> ResearchState:
    try:
        parsed = await parse_query(state["query"])
        state["product_name"] = parsed.product_name
        state["category"] = parsed.category
        
        # CORRECTED: Matched names to your Pydantic schema
        state["search_questions"] = parsed.search_questions
        state["news_questions"] = parsed.news_questions
        state["trends_comparison"] = parsed.trends_comparison 
                
    except Exception as e:
        state.setdefault("errors", []).append(str(e))

    return state


class PlanAdapter:
    def __init__(self, state: ResearchState):
        # CORRECTED: Matched variable names and string defaults
        self.search_questions = state.get("search_questions", [])
        self.news_questions = state.get("news_questions", [])
        self.trends_comparison = state.get("trends_comparison", "") # Default to string



async def discover_via_serp_node(state: ResearchState) -> ResearchState:

    if not state.get("search_questions"):
        state.setdefault("errors", []).append("No search questions generated for Serp discovery")
        return state

    try:
        plan = PlanAdapter(state)
        research_results = await run_full_market_research(plan)
        
        state["google_results"] = research_results["google_results"]
        state["news_results"] = research_results["news_results"]
        state["trends_results"] = research_results["trends_results"]
        
    except Exception as e:
        state.setdefault("errors", []).append(f"SerpAPI Error: {str(e)}")

    return state