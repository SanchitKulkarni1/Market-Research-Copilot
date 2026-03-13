import asyncio
import json
import time
from graph.graph import build_graph


async def main():
    query = "do research for zoom - a video conferencing tool"

    print("\n" + "=" * 60)
    print("🚀 Starting Market Research Pipeline")
    print("=" * 60)
    print(f"Query: {query}\n")

    # Build graph
    graph = build_graph()

    # Initial state
    initial_state = {
        "query": query,
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
        "execution_log": [],
        "confidence": {},
        "errors": [],
        "report": None,
        "metrics": None,
        "run_id": None,
        "eval_latency": None,
    }

    # Run the entire graph (includes evaluation)
    start_time = time.perf_counter()
    final_state = await graph.ainvoke(initial_state)
    total_latency = time.perf_counter() - start_time

    # Extract results
    report = final_state.get("report")
    metrics = final_state.get("metrics")
    eval_latency = final_state.get("eval_latency", 0)
    run_id = final_state.get("run_id")
    errors = final_state.get("errors", [])

    # Display execution log
    print("\n" + "=" * 60)
    print("📋 Execution Log")
    print("=" * 60)
    for log in final_state.get("execution_log", []):
        node = log.get("node", "Unknown")
        lat = log.get("latency_seconds", 0)
        print(f"  {node:25s} → {lat:.2f}s")

    # Display metrics
    if metrics:
        print("\n" + "=" * 60)
        print("📊 Evaluation Metrics")
        print("=" * 60)
        print(json.dumps(metrics, indent=2))
        print(f"\n  Evaluation Time: {eval_latency:.2f}s")
        print(f"  Run ID: {run_id}")
    else:
        print("\n⚠️  No metrics generated")

    # Display report
    if report:
        report_dict = report.model_dump() if hasattr(report, "model_dump") else report
        print("\n" + "=" * 60)
        print("📊 FINAL REPORT")
        print("=" * 60)
        print(json.dumps(report_dict, indent=2))
    else:
        print("\n⚠️  No report generated")

    # Display errors
    if errors:
        print("\n" + "=" * 60)
        print("⚠️  ERRORS")
        print("=" * 60)
        for err in errors:
            print(f"  - {err}")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Pipeline Complete")
    print("=" * 60)
    print(f"  Total Time: {total_latency:.2f}s")
    print(f"  Status: {'✅ Success' if report else '❌ Failed'}")
    print(f"  Errors: {len(errors)}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())