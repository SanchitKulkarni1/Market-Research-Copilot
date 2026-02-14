from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

async def is_valid_competitor(product: str, category: str, domain: str) -> bool:
    prompt = f"""
Is the company at domain "{domain}" a direct competitor to "{product}"
in the category "{category}"?

Answer ONLY true or false.
"""

    response = await client.aio.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=10,
        ),
    )

    return "true" in response.text.lower()
