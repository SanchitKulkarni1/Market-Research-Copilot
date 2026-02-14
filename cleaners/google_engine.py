import json
from typing import Dict, Any, List
from urllib.parse import urlparse


MAX_ORGANIC = 5


def clean_serpapi_google_response(data: Dict[str, Any]) -> Dict[str, Any]:

    cleaned = {}

    # --------------------------------
    # 1. Total Results
    # --------------------------------
    search_info = data.get("search_information", {})
    if search_info.get("total_results"):
        cleaned["total_results"] = search_info["total_results"]

    # --------------------------------
    # 2. Organic Results (LIMITED)
    # --------------------------------
    organic_results = data.get("organic_results", [])[:MAX_ORGANIC]

    cleaned_organic = []
    organic_links = []
    domains = []

    for result in organic_results:
        link = result.get("link")
        if not link:
            continue

        domain = urlparse(link).netloc

        cleaned_organic.append({
            "position": result.get("position"),
            "title": result.get("title"),
            "snippet": result.get("snippet"),
            "link": link,
            "domain": domain
        })

        organic_links.append(link)
        domains.append(domain)

    if cleaned_organic:
        cleaned["organic_results"] = cleaned_organic
        cleaned["links"] = list(set(organic_links))
        cleaned["domains"] = list(set(domains))

    # --------------------------------
    # 3. AI Overview (Flattened)
    # --------------------------------
    ai_overview = data.get("ai_overview", {})
    text_blocks = ai_overview.get("text_blocks", [])

    ai_summary = []

    for block in text_blocks:
        if block.get("type") == "paragraph":
            ai_summary.append(block.get("snippet"))
        elif block.get("type") == "list":
            for item in block.get("list", []):
                ai_summary.append(item.get("snippet"))

    if ai_summary:
        cleaned["ai_overview"] = " ".join(ai_summary)

    # --------------------------------
    # 4. Related Questions
    # --------------------------------
    related_questions = data.get("related_questions", [])
    cleaned_questions = []

    for q in related_questions[:5]:
        snippet = q.get("snippet") or extract_ai_snippet(q)
        cleaned_questions.append({
            "question": q.get("question"),
            "snippet": snippet
        })

    if cleaned_questions:
        cleaned["related_questions"] = cleaned_questions

    # --------------------------------
    # 5. Related Searches
    # --------------------------------
    related_searches = data.get("related_searches", [])
    cleaned_searches = [
        item.get("query")
        for item in related_searches[:8]
        if item.get("query")
    ]

    if cleaned_searches:
        cleaned["related_searches"] = cleaned_searches

    return cleaned


def extract_ai_snippet(question_obj: Dict[str, Any]) -> str:
    text_blocks = question_obj.get("text_blocks", [])
    snippets = []

    for block in text_blocks:
        if block.get("type") == "paragraph":
            snippets.append(block.get("snippet"))
        elif block.get("type") == "list":
            for item in block.get("list", []):
                snippets.append(item.get("snippet"))

    return " ".join(snippets) if snippets else None
