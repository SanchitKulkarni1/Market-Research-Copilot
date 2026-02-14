import os
import httpx
import asyncio
from typing import List, Dict, Any

SERP_API_KEY = os.getenv("SERP_API_KEY")
BASE_URL = "https://serpapi.com/search.json"


async def fetch_serp(params: Dict[str, Any], client: httpx.AsyncClient, sem: asyncio.Semaphore) -> Dict[str, Any]:
    """Fetches data from SerpApi, using a Semaphore to limit concurrency."""
    async with sem:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()

# google search
async def run_google_search(questions: List[str], client: httpx.AsyncClient, sem: asyncio.Semaphore) -> List[Dict]:
    tasks = []
    for q in questions:
        params = {
            "engine": "google",
            "q": q,
            "api_key": SERP_API_KEY
        }
        tasks.append(fetch_serp(params, client, sem))

    return await asyncio.gather(*tasks)

# google news
async def run_news_search(questions: List[str], client: httpx.AsyncClient, sem: asyncio.Semaphore) -> List[Dict]:
    tasks = []
    for q in questions:
        params = {
            "engine": "google_news",
            "q": q,
            "api_key": SERP_API_KEY
        }
        tasks.append(fetch_serp(params, client, sem))

    return await asyncio.gather(*tasks)

# google trends (UPDATED for a single comparison API hit)
async def run_trends_search(comparison_query: str, client: httpx.AsyncClient, sem: asyncio.Semaphore) -> Dict[str, Any]:
    """Takes a single comma-separated string and makes ONE API call."""
    if not comparison_query or not comparison_query.strip():
        print("⚠️ Warning: Trends query is empty. Skipping Trends API call.")
        return {}
    params = {
        "engine": "google_trends",
        "q": comparison_query,    # e.g., "Zoom,Microsoft Teams,Google Meet"
        "date": "today 12-m",        # Added the 12-month date parameter from your curl
        "data_type": "TIMESERIES",
        "api_key": SERP_API_KEY
    }
    
    # We do not need asyncio.gather here because it's only 1 request
    return await fetch_serp(params, client, sem)

# --- MAIN EXECUTION PIPELINE ---

async def run_full_market_research(plan) -> Dict[str, Any]:
    """Runs all research queries concurrently but safely."""
    
    MAX_CONCURRENT_REQUESTS = 5
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Gather all the categories matching your updated ParsedQuery schema
        results = await asyncio.gather(
            run_google_search(plan.search_questions, client, sem),
            run_news_search(plan.news_questions, client, sem),
            run_trends_search(plan.trends_comparison, client, sem), 
        )

    return {
        "google_results": results[0],        # List[Dict]
        "news_results": results[1],          # List[Dict]
        "trends_results": results[2],        # Dict (Single API response containing the comparison)
    }