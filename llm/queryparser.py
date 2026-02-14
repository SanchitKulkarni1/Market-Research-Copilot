import os
from typing import Optional, List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import dotenv

dotenv.load_dotenv()  

class ParsedQuery(BaseModel):
    product_name: Optional[str] = Field(
        None, description="Product name or null if unclear"
    )
    category: Optional[str] = Field(
        None, description="Product category or null if unclear"
    )
    keywords: List[str] = Field(
        ..., description="5–7 search keywords"
    )


async def parse_query(query: str) -> ParsedQuery:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = f"""
You are parsing a SaaS product research query.

Query:
"{query}"

Extract:
- product_name (null if unclear)
- category (null if unclear)
- 5–7 search keywords

Respond in strict JSON.
"""

    response = await client.aio.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=512,
            response_mime_type="application/json",
            response_schema=ParsedQuery,
        ),
    )

    parsed: ParsedQuery = response.parsed

    if not parsed.keywords or len(parsed.keywords) < 3:
        raise ValueError("Insufficient keywords extracted")

    return parsed
