from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List


ZOOM_OWNED_DOMAINS = [
    "zoom.com",
    "news.zoom.com"
]

LOW_SIGNAL_KEYWORDS = [
    "how to",
    "tips",
    "getting started",
    "guide",
    "review",
    "best webcam",
    "fatigue",
    "zoom camera",
    "top tips",
    "accessibility"
]

HIGH_SIGNAL_KEYWORDS = [
    "ban",
    "regulation",
    "security",
    "outage",
    "investor",
    "earnings",
    "stock",
    "market",
    "ai",
    "acquisition",
    "lawsuit",
    "government",
    "expands",
    "financial"
]


def is_recent(iso_date: str, months: int = 12) -> bool:
    article_date = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    cutoff = datetime.now(timezone.utc) - timedelta(days=30 * months)
    return article_date >= cutoff


def clean_google_news(data: Dict[str, Any]) -> Dict[str, Any]:

    news = data.get("news_results", [])
    cleaned_news = []

    for item in news:
        title = item.get("title", "").lower()
        link = item.get("link", "")
        iso_date = item.get("iso_date")
        source_name = item.get("source", {}).get("name")

        if not iso_date:
            continue

        # 1️⃣ Remove old content
        if not is_recent(iso_date, months=12):
            continue

        # 2️⃣ Remove Zoom-owned content
        if any(domain in link for domain in ZOOM_OWNED_DOMAINS):
            continue

        # 3️⃣ Remove low-signal tutorial content
        if any(keyword in title for keyword in LOW_SIGNAL_KEYWORDS):
            continue

        # 4️⃣ Keep only high-signal strategic content
        signal_score = sum(keyword in title for keyword in HIGH_SIGNAL_KEYWORDS)

        if signal_score == 0:
            continue

        cleaned_news.append({
            "title": item.get("title"),
            "source": source_name,
            "link": link,
            "date": iso_date,
            "signal_score": signal_score
        })

    # Sort by signal strength
    cleaned_news = sorted(
        cleaned_news,
        key=lambda x: x["signal_score"],
        reverse=True
    )

    # Limit to top 15
    cleaned_news = cleaned_news[:15]

    return {
        "strategic_news": cleaned_news,
        "links": [item["link"] for item in cleaned_news]
    }
    
