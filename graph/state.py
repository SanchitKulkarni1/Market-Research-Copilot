from typing import TypedDict, List, Dict, Optional


class ResearchState(TypedDict):
    # Raw input
    query: str

    # Parsed idea
    product_name: Optional[str]
    category: Optional[str]
    keywords: List[str]
    search_questions: List[str]
    news_questions: List[str]
    trends_comparison: str

    # Discovery
    google_results: Optional[List[Dict]]
    news_results: Optional[List[Dict]]
    trends_results: Optional[Dict]

    # Meta
    confidence: Dict[str, str]
    errors: List[str]
