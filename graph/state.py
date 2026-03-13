from typing import TypedDict, Optional, List, Dict, Any


class ResearchState(TypedDict):
    # Input
    query: str
    
    # Plan (from parse_query)
    product_name: Optional[str]
    category: Optional[str]
    keywords: Optional[List[str]]
    search_questions: Optional[List[str]]
    news_questions: Optional[List[str]]
    trends_comparison: Optional[str]
    
    # Tool Results (from discover_serp)
    google_results: Optional[List[Any]]
    news_results: Optional[List[Any]]
    trends_results: Optional[Dict[str, Any]]
    
    # Scraped Content (from scrape_news)
    scraped_news: Optional[List[Dict[str, str]]]
    
    # Final Output (from generate_report)
    report: Optional[Dict[str, Any]]
    
    # Evaluation Results (from evaluate_report) ✅ NEW
    metrics: Optional[Dict[str, Any]]
    run_id: Optional[str]
    eval_latency: Optional[float]
    
    # Metadata
    execution_log: Optional[List[Dict[str, Any]]]
    confidence: Optional[Dict[str, Any]]
    errors: Optional[List[str]]