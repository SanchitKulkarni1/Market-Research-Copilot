import asyncio
import json
import time
from graph.graph import build_graph

async def main():
    # Compile the latest graph
    graph = build_graph()

    # Match initial_state to ResearchState definition
    initial_state = {
        "query": "do research for zoom - a video conferencing tool",
        
        "product_name": None,
        "category": None,
        "keywords": [],
        "search_questions": [],
        "news_questions": [],
        "trends_comparison": "",

        "google_results": [],
        "news_results": [],
        "trends_results": {},
        "scraped_news": [],

        "confidence": {},
        "errors": [],
        "report": None
    }

    print("\n" + "="*80)
    print("🚀 MARKET RESEARCH PIPELINE")
    print("="*80)
    print(f"Query: {initial_state['query']}")
    print("-"*80 + "\n")
    
    start_time = time.perf_counter()
    
    # Run the graph
    final_state = await graph.ainvoke(initial_state)
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # 1. Print Errors
    if final_state.get("errors"):
        print("\n" + "="*80)
        print("❌ ERRORS")
        print("="*80)
        for error in final_state["errors"]:
            print(f"  • {error}")
        print("-"*80)

    # 2. Handle and Print the Final Report
    report = final_state.get("report")
    if report:
        print("\n" + "="*80)
        print("📊 FINAL MARKET RESEARCH REPORT")
        print("="*80 + "\n")
        
        # Convert to dict (handle both Pydantic and regular dict)
        if hasattr(report, 'model_dump'):
            report_dict = report.model_dump()
        else:
            report_dict = report
        
        # Pretty print with proper formatting
        print(json.dumps(report_dict, indent=2))
        
        print("\n" + "-"*80)
        
        # Save a copy as a file automatically
        with open("final_report.json", "w") as f:
            json.dump(report_dict, f, indent=2)
        print("💾 Report saved to 'final_report.json'")
        print("-"*80)
    else:
        print("\n" + "="*80)
        print("⚠️  NO REPORT GENERATED")
        print("="*80)
        print("Check errors above for details.")
        print("-"*80)

    # 3. Execution Summary
    print("\n" + "="*80)
    print("⏱️  EXECUTION SUMMARY")
    print("="*80)
    print(f"Total Time: {elapsed_time:.2f} seconds")
    print(f"Status: {'✅ Success' if report else '❌ Failed'}")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())