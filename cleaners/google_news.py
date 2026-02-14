import re
from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from urllib.parse import urlparse

# UNIVERSAL SaaS LOW-SIGNAL KEYWORDS
LOW_SIGNAL_KEYWORDS = [
    "how to", "tips", "getting started", "guide", "review", 
    "tutorial", "walkthrough", "top tips", "accessibility", "troubleshoot",
    "patch notes", "bug fix", "security patch", "update available","mirror less"
]

# UNIVERSAL SaaS HIGH-SIGNAL KEYWORDS
HIGH_SIGNAL_KEYWORDS = [
    "ban", "regulation", "security breach", "outage", "investor", "earnings", 
    "stock", "market", "ai", "acquisition", "lawsuit", "government", 
    "expands", "financial", "revenue", "profit", "launches", "announces",
    "partnership", "integration", "enterprise", "valuation"
]

# IRRELEVANT PRODUCTS (to filter out wrong "Zoom" mentions)
IRRELEVANT_PRODUCTS = ["vivo", "oppo", "samsung", "xiaomi", "realme", "iphone", "pixel"]

# LOW-QUALITY DOMAINS (optional - add known clickbait/spam sources)
BLACKLIST_DOMAINS = ["indiatvnews.com"]

# PRE-COMPILE REGEX FOR SPEED AND EXACT WORD MATCHING (\b)
LOW_SIGNAL_REGEX = [re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE) for kw in LOW_SIGNAL_KEYWORDS]
HIGH_SIGNAL_REGEX = [re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE) for kw in HIGH_SIGNAL_KEYWORDS]


def is_recent(iso_date: str, months: int = 12) -> bool:
    try:
        article_date = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        cutoff = datetime.now(timezone.utc) - timedelta(days=30 * months)
        return article_date >= cutoff
    except ValueError:
        return False


def clean_google_news(data: Dict[str, Any], news_questions: List[str]) -> List[Dict[str, str]]:
    # 1. Dynamically identify Product Name (e.g., "spotify", "zoom")
    all_words = re.findall(r'\w+', " ".join(news_questions).lower())
    if not all_words:
        return []
    
    product_name = Counter(all_words).most_common(1)[0][0]
    
    # 2. Dynamically build owned domains to filter out official press releases
    owned_domains = [
        f"{product_name}.com", 
        f"news.{product_name}.com", 
        f"newsroom.{product_name}.com", 
        f"blog.{product_name}.com",
        f"press.{product_name}.com"
    ]

    categorized_links = {q: [] for q in news_questions}
    seen_titles = set()
    seen_urls = set()  # Additional URL-based dedup
    
    # Safely handle both flat lists and nested clusters from SERP APIs
    news_items = data.get("news_results", []) if isinstance(data, dict) else data
    flat_news = [item for cluster in news_items for item in (cluster.get('strategic_news', []) if isinstance(cluster, dict) and 'strategic_news' in cluster else [cluster])]

    for item in flat_news:
        title = item.get("title", "")
        lower_title = title.lower()
        link = item.get("link", "")
        iso_date = item.get("iso_date")

        if not iso_date or not title or not link:
            continue

        # --- HARD FILTERS ---
        # Must contain the dynamically extracted product name
        if product_name not in lower_title:
            continue
            
        # Must be recent
        if not is_recent(iso_date, months=12):
            continue
            
        # Must NOT be an owned domain
        if any(domain in link for domain in owned_domains):
            continue
        
        # Must NOT be from blacklisted domains
        if any(domain in link for domain in BLACKLIST_DOMAINS):
            continue
        
        # Must NOT mention irrelevant products (filters out Vivo, Samsung, etc.)
        if any(prod in lower_title for prod in IRRELEVANT_PRODUCTS):
            continue
            
        # Must NOT contain low-signal tutorial/review keywords (Exact Match)
        if any(regex.search(lower_title) for regex in LOW_SIGNAL_REGEX):
            continue

        # URL-based deduplication (exact match)
        if link in seen_urls:
            continue

        # Title-based deduplication: Strip punctuation and use first 5 words
        clean_slug = re.sub(r'[^\w\s]', '', lower_title)
        title_slug = " ".join(clean_slug.split()[:5])
        if title_slug in seen_titles:
            continue

        # --- SCORING & CATEGORIZATION ---
        # Base score from universal strategic keywords (weighted higher now)
        base_signal = sum(1 for regex in HIGH_SIGNAL_REGEX if regex.search(lower_title))
        
        best_category = None
        highest_score = -1

        for question in news_questions:
            # Extract intent keywords specific to this question (ignoring the product name)
            intent_keywords = [w for w in re.findall(r'\w+', question.lower()) if w != product_name]
            
            # Match intent words using exact word boundaries
            intent_matches = sum(1 for kw in intent_keywords if re.search(rf'\b{re.escape(kw)}\b', lower_title))
            
            # Weight intent matches heavily, plus add the base signal score
            total_score = (intent_matches * 3) + (base_signal * 4)  # Increased base_signal weight

            if total_score > highest_score:
                highest_score = total_score
                best_category = question

        # Only add if it scored at least some points and found a category
        if highest_score > 0 and best_category:
            categorized_links[best_category].append({
                "title": title,
                "link": link,
                "signal_score": highest_score
            })
            seen_titles.add(title_slug)
            seen_urls.add(link)

    # Sort each category internally by highest score
    for q in categorized_links:
        categorized_links[q].sort(key=lambda x: x['signal_score'], reverse=True)

    # --- ROUND-ROBIN EXTRACTION (Top 5 with source diversity) ---
    final_news = []
    category_keys = list(categorized_links.keys())
    source_counts = Counter()
    max_per_source = 2  # Limit to 2 articles from same domain

    while len(final_news) < 5:
        added_in_round = False
        for key in category_keys:
            if len(final_news) >= 5:
                break
            if categorized_links[key]: 
                # Pop the top-scoring item from this category
                top_item = categorized_links[key].pop(0)
                
                # Check source diversity
                domain = urlparse(top_item["link"]).netloc
                if source_counts[domain] >= max_per_source:
                    continue  # Skip this one, try next category
                
                # Append ONLY the title and link to the final output
                final_news.append({
                    "title": top_item["title"],
                    "link": top_item["link"]
                })
                source_counts[domain] += 1
                added_in_round = True
        
        # Break if we've exhausted all matched links
        if not added_in_round:
            break 

    return final_news