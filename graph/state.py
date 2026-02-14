from typing import TypedDict, List, Dict, Optional


class ResearchState(TypedDict):
    # Raw input
    query: str

    # Parsed idea
    product_name: Optional[str]
    category: Optional[str]
    keywords: List[str]

    # Discovery
    official_site: Optional[str]
    competitors: List[str]

    # Meta
    confidence: Dict[str, str]
    errors: List[str]
