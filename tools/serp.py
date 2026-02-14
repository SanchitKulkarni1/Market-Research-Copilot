import os
import requests
from urllib.parse import urlparse

SERP_API_KEY = os.getenv("SERP_API_KEY")


def extract_domain(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "").lower()


def serp_discover(
    keywords: list[str],
    product_name: str,
    category: str,
    max_competitors: int = 5,
):
    # 🔒 Narrow intent: add category explicitly
    query = f"{product_name} {category} alternatives"

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
        "num": 15,
    }

    res = requests.get("https://serpapi.com/search.json", params=params)
    res.raise_for_status()

    organic = res.json().get("organic_results", [])

    official_site = None
    competitors: list[str] = []
    seen_domains = set()

    for r in organic:
        link = r.get("link")
        if not link:
            continue

        domain = extract_domain(link)

        

        # ❌ duplicates
        if domain in seen_domains:
            continue

        seen_domains.add(domain)

        # ✅ first valid domain → official site
        if official_site is None:
            official_site = f"https://{domain}"
            continue

        # ❌ same product domain variants (zoom.com vs zoom.us)
        if official_site.replace("https://", "") in domain:
            continue

        competitors.append(domain)

        if len(competitors) >= max_competitors:
            break

    return official_site, competitors
