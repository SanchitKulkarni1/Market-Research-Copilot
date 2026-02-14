import asyncio
from graph.graph import build_graph


async def main():
    graph = build_graph()

    initial_state = {
        "query": "do research for zoom - a video conferencing tool",
        "product_name": None,
        "category": None,
        "keywords": [],
        "official_site": None,
        "competitors": [],
        "confidence": {},
        "errors": [],
    }

    final_state = await graph.ainvoke(initial_state)
    print(final_state)


if __name__ == "__main__":
    asyncio.run(main())
