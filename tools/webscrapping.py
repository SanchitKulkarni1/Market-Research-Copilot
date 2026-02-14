# tools/webscrapping.py
import asyncio
import trafilatura

def extract_text_sync(url: str) -> str:
    """The synchronous Trafilatura logic."""
    downloaded = trafilatura.fetch_url(url)
    
    if not downloaded:
        return "Failed to fetch content or blocked by site."
        
    text = trafilatura.extract(
        downloaded,
        include_links=False,
        include_images=False
    )
    
    return text if text else "No readable text found."

async def extract_text_async(url: str) -> str:
    """Runs the Trafilatura extraction in a background thread to prevent blocking."""
    try:
        return await asyncio.to_thread(extract_text_sync, url)
    except Exception as e:
        return f"Scraping failed: {str(e)}"

async def fallback_missing_link() -> str:
    """Helper for when a URL is missing."""
    return "No link provided."