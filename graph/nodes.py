import asyncio


from graph.state import ResearchState
from llm.queryparser import ResearchPlanGenerator
from tools.serp import run_full_market_research 

# Import your cleaner functions 
from cleaners.google_engine import clean_serpapi_google_response
from cleaners.google_news import clean_google_news
from cleaners.google_trends import clean_google_trends

from tools.webscrapping import extract_text_async, fallback_missing_link


async def parse_query_node(state: ResearchState) -> ResearchState:
    try:
        # 2. FIXED: Created an instance of the class and called .generate()
        plan_generator = ResearchPlanGenerator()
        parsed = await plan_generator.generate(state["query"])
        
        state["product_name"] = parsed.product_name
        state["category"] = parsed.category
        
        state["search_questions"] = parsed.search_questions
        state["news_questions"] = parsed.news_questions
        state["trends_comparison"] = parsed.trends_comparison 
                
    except Exception as e:
        state.setdefault("errors", []).append(str(e))

    return state


class PlanAdapter:
    def __init__(self, state: ResearchState):
        self.search_questions = state.get("search_questions", [])
        self.news_questions = state.get("news_questions", [])
        self.trends_comparison = state.get("trends_comparison", "") 


async def discover_via_serp_node(state: ResearchState) -> ResearchState:
    if not state.get("search_questions"):
        state.setdefault("errors", []).append("No search questions generated for Serp discovery")
        return state

    try:
        plan = PlanAdapter(state)
        research_results = await run_full_market_research(plan)
        
        # Storing RAW results first
        state["google_results"] = research_results["google_results"]
        state["news_results"] = research_results["news_results"]
        state["trends_results"] = research_results["trends_results"]
        
    except Exception as e:
        state.setdefault("errors", []).append(f"SerpAPI Error: {str(e)}")

    return state


async def clean_data_node(state: ResearchState) -> ResearchState:
    """Takes the raw API results from the state and overwrites them with cleaned data."""
    try:
        # 1. Clean Google Search Results (List of Dicts)
        cleaned_google = []
        for raw_google_response in state.get("google_results", []):
            cleaned_google.append(clean_serpapi_google_response(raw_google_response))
        state["google_results"] = cleaned_google

        # 2. Clean Google News Results (List of Dicts)
        cleaned_news = []
        for raw_news_response in state.get("news_results", []):
            cleaned_news.append(clean_google_news(raw_news_response, state.get("news_questions", [])))
        state["news_results"] = cleaned_news

        # 3. Clean Google Trends Results (Single Dict)
        raw_trends = state.get("trends_results")
        if raw_trends:
            state["trends_results"] = clean_google_trends(raw_trends)
            
    except Exception as e:
        state.setdefault("errors", []).append(f"Cleaning Error: {str(e)}")

    return state


async def scrape_news_node(state: ResearchState) -> ResearchState:
    """Takes cleaned news links, scrapes the web content asynchronously, and saves to state."""
    try:
        raw_news_items = state.get("news_results", [])
        
        # --- THE FIX: FLATTEN THE LIST ---
        # This guarantees we only have a clean list of dictionaries, 
        # preventing the 'list object has no attribute get' error.
        flat_news = []
        for item in raw_news_items:
            if isinstance(item, list):
                flat_news.extend(item)
            elif isinstance(item, dict):
                flat_news.append(item)
        
        # Build a list of asynchronous scraping tasks
        tasks = []
        for news in flat_news:  # <-- We iterate over flat_news now
            link = news.get("link")
            if link:
                tasks.append(extract_text_async(link))
            else:
                tasks.append(fallback_missing_link())
                
        # Execute all scraping tasks concurrently
        scraped_contents = await asyncio.gather(*tasks)
        
        # --- Keep ONLY title and content ---
        final_scraped_data = []
        for news, content in zip(flat_news, scraped_contents):  # <-- zip with flat_news
            final_scraped_data.append({
                "title": news.get("title", "Unknown Title"),
                "content": content[:6000] if content else "No readable text found."
            })
            
        # Store the strictly filtered data in the new state key
        state["scraped_news"] = final_scraped_data
        
    except Exception as e:
        state.setdefault("errors", []).append(f"Scraping Node Error: {str(e)}")

    return state