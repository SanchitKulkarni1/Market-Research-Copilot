import asyncio
import time
from typing import Dict, Any
from datetime import datetime

from graph.state import ResearchState
from llm.queryparser import ResearchPlanGenerator
from tools.serp import run_full_market_research

from cleaners.google_engine import clean_serpapi_google_response
from cleaners.google_news import clean_google_news
from cleaners.google_trends import clean_google_trends

from tools.webscrapping import extract_text_async, fallback_missing_link
from llm.research_copilot import MarketResearchSynthesizer


# ==========================================================
# Helper Logger
# ==========================================================

def log_step(state: ResearchState, payload: Dict[str, Any]):
    state.setdefault("execution_log", []).append(payload)


# ==========================================================
# 1️⃣ PARSE QUERY NODE (Planner)
# ==========================================================

async def parse_query_node(state: ResearchState) -> ResearchState:
    start = time.perf_counter()

    try:
        plan_generator = ResearchPlanGenerator()
        parsed = await plan_generator.generate(state["query"])

        state["product_name"] = parsed.product_name
        state["category"] = parsed.category
        state["search_questions"] = parsed.search_questions
        state["news_questions"] = parsed.news_questions
        state["trends_comparison"] = parsed.trends_comparison

        latency = time.perf_counter() - start

        log_step(state, {
            "node": "parse_query",
            "latency_seconds": latency,
            "plan": {
                "product_name": parsed.product_name,
                "category": parsed.category,
                "search_questions": parsed.search_questions,
                "news_questions": parsed.news_questions,
                "trends_comparison": parsed.trends_comparison
            }
        })

    except Exception as e:
        state.setdefault("errors", []).append(str(e))

    return state


# ==========================================================
# Plan Adapter
# ==========================================================

class PlanAdapter:
    def __init__(self, state: ResearchState):
        self.search_questions = state.get("search_questions", [])
        self.news_questions = state.get("news_questions", [])
        self.trends_comparison = state.get("trends_comparison", "")


# ==========================================================
# 2️⃣ DISCOVER VIA SERP NODE (Tool Calls)
# ==========================================================

async def discover_via_serp_node(state: ResearchState) -> ResearchState:
    start = time.perf_counter()

    if not state.get("search_questions"):
        state.setdefault("errors", []).append("No search questions generated")
        return state

    try:
        plan = PlanAdapter(state)
        research_results = await run_full_market_research(plan)

        state["google_results"] = research_results["google_results"]
        state["news_results"] = research_results["news_results"]
        state["trends_results"] = research_results["trends_results"]

        latency = time.perf_counter() - start

        log_step(state, {
            "node": "discover_via_serp",
            "latency_seconds": latency,
            "tool_calls": {
                "google_search_queries": state.get("search_questions"),
                "news_queries": state.get("news_questions"),
                "trends_query": state.get("trends_comparison")
            },
            "results_summary": {
                "google_batches": len(state.get("google_results", [])),
                "news_batches": len(state.get("news_results", []))
            }
        })

    except Exception as e:
        state.setdefault("errors", []).append(f"SerpAPI Error: {str(e)}")

    return state


# ==========================================================
# 3️⃣ CLEAN DATA NODE
# ==========================================================

async def clean_data_node(state: ResearchState) -> ResearchState:
    start = time.perf_counter()

    try:
        cleaned_google = [
            clean_serpapi_google_response(r)
            for r in state.get("google_results", [])
        ]
        state["google_results"] = cleaned_google

        cleaned_news = [
            clean_google_news(r, state.get("news_questions", []))
            for r in state.get("news_results", [])
        ]
        state["news_results"] = cleaned_news

        if state.get("trends_results"):
            state["trends_results"] = clean_google_trends(state["trends_results"])

        latency = time.perf_counter() - start

        log_step(state, {
            "node": "clean_data",
            "latency_seconds": latency,
            "post_clean_counts": {
                "google_results": len(state.get("google_results", [])),
                "news_results": len(state.get("news_results", []))
            }
        })

    except Exception as e:
        state.setdefault("errors", []).append(f"Cleaning Error: {str(e)}")

    return state


# ==========================================================
# 4️⃣ SCRAPE NEWS NODE
# ==========================================================

async def scrape_news_node(state: ResearchState) -> ResearchState:
    start = time.perf_counter()

    try:
        raw_news_items = state.get("news_results", [])
        flat_news = []

        for item in raw_news_items:
            if isinstance(item, list):
                flat_news.extend(item)
            elif isinstance(item, dict):
                flat_news.append(item)

        tasks = []
        for news in flat_news:
            link = news.get("link")
            tasks.append(
                extract_text_async(link) if link else fallback_missing_link()
            )

        scraped_contents = await asyncio.gather(*tasks)

        final_scraped_data = [
            {
                "title": news.get("title", "Unknown Title"),
                "content": content[:6000] if content else "No readable text found."
            }
            for news, content in zip(flat_news, scraped_contents)
        ]

        state["scraped_news"] = final_scraped_data

        latency = time.perf_counter() - start

        log_step(state, {
            "node": "scrape_news",
            "latency_seconds": latency,
            "articles_scraped": len(final_scraped_data)
        })

    except Exception as e:
        state.setdefault("errors", []).append(f"Scraping Node Error: {str(e)}")

    return state


# ==========================================================
# 5️⃣ GENERATE REPORT NODE (Final LLM)
# ==========================================================

async def generate_report_node(state: ResearchState) -> ResearchState:
    start = time.perf_counter()

    if not state.get("scraped_news") and not state.get("google_results"):
        state.setdefault("errors", []).append("Insufficient data to generate report.")
        return state

    try:
        synthesizer = MarketResearchSynthesizer()

        report = await synthesizer.generate_report(
            product_name=state.get("product_name") or "Target Product",
            category=state.get("category") or "SaaS",
            search_results=state.get("google_results", []),
            scraped_news=state.get("scraped_news", []),
            trends_results=state.get("trends_results", {})
        )

        state["report"] = report

        latency = time.perf_counter() - start

        log_step(state, {
            "node": "generate_report",
            "latency_seconds": latency,
            "report_generated": True
        })

    except Exception as e:
        state.setdefault("errors", []).append(f"Report Generation Error: {str(e)}")

    return state


# ==========================================================
# 6️⃣ EVALUATE REPORT NODE (DeepEval Metrics)
# ==========================================================

async def evaluate_report_node(state: ResearchState) -> ResearchState:
    """Evaluate the generated report using DeepEval metrics and store results"""
    start = time.perf_counter()
    
    print("\n" + "=" * 60)
    print("🧪 [Evaluation Node] Starting DeepEval metrics...")
    print("=" * 60)
    
    # Skip evaluation if no report was generated
    if not state.get("report"):
        print("⚠️ [Evaluation Node] No report found, skipping evaluation")
        state.setdefault("errors", []).append("No report to evaluate")
        return state
    
    try:
        from evaluator import evaluate_run
        from opik_logger import push_metrics_to_opik
        from mongo_logger import store_raw_trace
        
        # Calculate total pipeline latency from execution log
        total_latency = sum(
            log.get("latency_seconds", 0) 
            for log in state.get("execution_log", [])
        )
        
        # Prepare trace for evaluation
        run_trace = {
            "query": state["query"],
            "timestamp": datetime.utcnow().isoformat(),
            "plan": {
                "product_name": state.get("product_name"),
                "category": state.get("category"),
                "search_questions": state.get("search_questions"),
                "news_questions": state.get("news_questions"),
                "trends_comparison": state.get("trends_comparison"),
            },
            "execution_log": state.get("execution_log", []),
            "google_results": state.get("google_results", []),
            "news_results": state.get("news_results", []),
            "trends_results": state.get("trends_results", {}),
            "report": state.get("report"),
            "latency_seconds": total_latency,
        }
        
        print(f"  📝 Query: {state['query']}")
        print(f"  ⏱️  Total pipeline latency: {total_latency:.2f}s")
        
        # 1️⃣ Store raw trace in MongoDB
        print("  💾 Storing trace in MongoDB...")
        try:
            run_id = store_raw_trace(run_trace)
            state["run_id"] = run_id
            print(f"  ✅ Stored trace: {run_id}")
        except Exception as mongo_error:
            print(f"  ⚠️ MongoDB storage failed: {mongo_error}")
            import traceback
            traceback.print_exc()
            # Generate fallback run_id
            import uuid
            run_id = str(uuid.uuid4())
            state["run_id"] = run_id
            print(f"  ⚠️ Using fallback run_id: {run_id}")
        
        # 2️⃣ Run DeepEval metrics
        print("  📊 Running DeepEval metrics...")
        eval_start = time.perf_counter()
        
        metrics = evaluate_run(run_trace)
        
        eval_latency = time.perf_counter() - eval_start
        
        # Store metrics in state
        state["metrics"] = metrics
        state["eval_latency"] = eval_latency
        
        print(f"  ✅ Evaluation complete! Time: {eval_latency:.2f}s")
        
        # 3️⃣ Push metrics to Opik
        print("  🔭 Pushing metrics to Opik...")
        try:
            push_metrics_to_opik(run_id, metrics, total_latency)
        except Exception as opik_error:
            print(f"  ⚠️ Opik push failed: {opik_error}")
            import traceback
            traceback.print_exc()
        
        # Log evaluation step
        log_step(state, {
            "node": "evaluate_report",
            "latency_seconds": time.perf_counter() - start,
            "run_id": run_id,
            "metrics_summary": {
                name: data.get("score") if isinstance(data, dict) else data
                for name, data in metrics.items()
            },
            "eval_latency": eval_latency
        })
        
        print("=" * 60)
        print("✅ [Evaluation Node] Complete!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        error_msg = f"Evaluation Node Error: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        print("Traceback:")
        traceback.print_exc()
        state.setdefault("errors", []).append(error_msg)
        
        # Ensure these are set even on error
        if "metrics" not in state:
            state["metrics"] = None
        if "eval_latency" not in state:
            state["eval_latency"] = None
        if "run_id" not in state:
            state["run_id"] = None
    
    return state