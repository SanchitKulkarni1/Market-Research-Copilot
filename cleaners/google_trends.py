from typing import Dict, Any


def clean_google_trends(data: Dict[str, Any]) -> Dict[str, Any]:

    timeline = data.get("interest_over_time", {}).get("timeline_data", [])
    averages = data.get("interest_over_time", {}).get("averages", [])

    if not timeline:
        return {}

    # Remove partial last week if exists
    if timeline[-1].get("partial_data"):
        timeline = timeline[:-1]

    # Build per-query lists
    query_series = {}

    for week in timeline:
        for item in week["values"]:
            query = item["query"]
            value = item["extracted_value"]

            if query not in query_series:
                query_series[query] = []

            query_series[query].append(value)

    summary = {}

    for query, values in query_series.items():
        summary[query] = {
            "average": round(sum(values) / len(values), 2),
            "max": max(values),
            "min": min(values),
            "latest": values[-1],
            "trend_direction": (
                "upward" if values[-1] > values[0]
                else "downward" if values[-1] < values[0]
                else "stable"
            )
        }

    return {
        "trend_summary": summary
    }
