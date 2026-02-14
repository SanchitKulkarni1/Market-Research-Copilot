import asyncio
import json
import time  # 1. Import the time module
from graph.graph import build_graph


async def main():
    graph = build_graph()

    initial_state = {
        "query": "do research for zoom - a video conferencing tool",
        
        "product_name": None,
        "category": None,
        "keywords": [],
        
        "search_questions": [],
        "news_questions": [],
        "trends_comparison": "",
        "finance_queries": [],

        "official_site": None,
        "competitors": [],

        "google_results": [],
        "news_results": [],
        "trends_results": {},
        "finance_results": [],

        "confidence": {},
        "errors": [],
    }

    print("Running market research pipeline... This may take a few seconds.")
    
    # 2. Start the timer right before invoking the graph
    start_time = time.perf_counter()
    
    final_state = await graph.ainvoke(initial_state)
    
    # 3. Stop the timer right after the graph finishes
    end_time = time.perf_counter()
    
    # 4. Calculate total elapsed time
    elapsed_time = end_time - start_time

    # Print any errors first
    if final_state.get("errors"):
        print("\n=== ERRORS ===")
        print(json.dumps(final_state["errors"], indent=2))
        return

    # Pretty-print the cleaned results
    print("\n=== CLEANED GOOGLE SEARCH RESULTS ===")
    print(json.dumps(final_state.get("google_results", []), indent=2))

    print("\n=== CLEANED NEWS RESULTS ===")
    print(json.dumps(final_state.get("scraped_news", []), indent=2))

    print("\n=== CLEANED TRENDS RESULTS ===")
    print(json.dumps(final_state.get("trends_results", {}), indent=2))

    # 5. Print the final execution time clearly at the bottom
    print(f"\n⏱️ Total Pipeline Execution Time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())