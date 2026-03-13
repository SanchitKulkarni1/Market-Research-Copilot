import time
from datetime import datetime

from graph.graph import build_graph


async def run_pipeline(query: str):
    """
    Run the complete market research pipeline including evaluation.
    Evaluation is now integrated into the graph as the final node.
    """
    graph = build_graph()

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

    start_time = time.perf_counter()

    # Run the entire graph (all nodes including evaluation)
    final_state = await graph.ainvoke(initial_state)

    latency = time.perf_counter() - start_time

    # Extract results from final state
    metrics = final_state.get("metrics")
    run_id = final_state.get("run_id")
    eval_latency = final_state.get("eval_latency", 0)

    print(f"\n📊 Pipeline Summary:")
    print(f"  Run ID: {run_id}")
    print(f"  Total Latency: {latency:.2f}s")
    print(f"  Eval Latency: {eval_latency:.2f}s")
    print(f"  Metrics Generated: {bool(metrics)}")
    print(f"  Report Generated: {bool(final_state.get('report'))}")
    print(f"  Errors: {len(final_state.get('errors', []))}\n")

    return {
        "run_id": run_id,
        "final_state": final_state,
        "metrics": metrics,
        "latency": latency,
        "eval_latency": eval_latency,
    }