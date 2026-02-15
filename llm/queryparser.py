import os
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ValidationInfo
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
    search_questions: List[str] = Field(
        ..., description="3-5 comprehensive search queries for Google Search API covering features, competitors, and comparisons",
        min_items=3, max_items=5
    )
    news_questions: List[str] = Field(
        ..., description="2-3 short keyword queries for Google News API",
        min_items=2, max_items=3
    )
    trends_comparison: str = Field(
        ..., description="Comma-separated list of 3-5 products/terms to compare in Google Trends (will be used as single query)"
    )

    # 1. Changed to @field_validator and added @classmethod
    @field_validator('trends_comparison')
    @classmethod
    def validate_trends_comparison(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("trends_comparison cannot be empty")
        
        # Split by comma and validate
        terms = [term.strip() for term in v.split(',')]
        
        if len(terms) < 3:
            raise ValueError("trends_comparison must have at least 3 terms")
        if len(terms) > 5:
            raise ValueError("trends_comparison must have at most 5 terms")
        
        if any(not term for term in terms):
            raise ValueError("trends_comparison contains empty terms")
        
        return v

    # 2. Changed to @field_validator, added @classmethod, and updated signature
    @field_validator('search_questions', 'news_questions')
    @classmethod
    def validate_non_empty(cls, v: List[str], info: ValidationInfo) -> List[str]:
        if any(not q.strip() for q in v):
            # 3. Changed field.name to info.field_name
            raise ValueError(f"{info.field_name} contains empty questions")
        return v


class ResearchPlanGenerator:
    """Generates structured research plans for market analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        self.client = genai.Client(api_key=self.api_key)
    
    async def generate(self, query: str) -> ParsedQuery:
        """Generate a comprehensive research plan from a user query."""
        
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        prompt = self._build_prompt(query)
        
        try:
            response = await self.client.aio.models.generate_content(
                model="gemini-2.5-flash",  # Updated to latest model
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,  # Increased for more comprehensive output
                    response_mime_type="application/json",
                    response_schema=ParsedQuery,
                ),
            )
            
            parsed: ParsedQuery = response.parsed
            self._validate_parsed_output(parsed)
            print("==" *20)
            print("✅ Successfully generated and the parsed the query:")
            print(parsed)
            print("==" *20)
            return parsed
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate research plan: {str(e)}")
    
    def _build_prompt(self, query: str) -> str:
        """Build the prompt for the LLM."""
        return f"""You are a senior market research strategist specializing in SaaS product analysis.

Parse this query and generate a comprehensive research plan optimized for SerpAPI:

Query: "{query}"

Your task:
1. Extract product_name (null if unclear or too vague)
2. Identify category (e.g., CRM, Analytics, Communication, etc. - null if unclear)
3. Generate targeted search queries for different SerpAPI engines

Requirements for each query type:

search_questions (3-5) - For Google Search API (engine="google"):
- Mix of product research AND competitive analysis queries
- Include at least one direct comparison query (ProductA vs ProductB)
- Include at least one alternatives/competitors query
- Include product-specific features, pricing, or capabilities query
- Format: Natural search phrases (2-8 words)
- Examples:
  * "Slack enterprise features pricing"
  * "Notion vs Coda comparison"
  * "HubSpot alternatives for startups"
  * "Salesforce integration capabilities"
  * "best CRM software 2024"
- Avoid: Question marks, full sentences, navigational queries (login, download)
- Balance: 40% product-focused, 60% competitive/comparison-focused

news_questions (2-3) - For Google News API (engine="google_news"):
- Short keyword queries (2-4 words max)
- Focus on: funding, acquisition, launch, partnership, controversy, updates
- Examples:
  * "Notion funding round"
  * "Figma Adobe acquisition"
  * "OpenAI partnership announcement"
  * "Stripe layoffs news"
- Avoid: Full sentences, dates, complex phrases

trends_comparison (1 string) - For Google Trends API (engine="google_trends"):
- SINGLE comma-separated string of 3-5 competing products or related terms
- This will be used as ONE query parameter: q="Term1,Term2,Term3,Term4,Term5"
- Format: "ProductA,ProductB,ProductC,ProductD,ProductE"
- Rules:
  * MUST include the main product being researched (if identified)
  * Include 2-4 direct competitors or alternatives
  * Use SHORT names (brand names, not full company names)
  * NO spaces around commas
  * NO "vs" or other words - ONLY product names separated by commas
- Examples:
  * "Zoom,Microsoft Teams,Google Meet,Webex,Slack"
  * "Notion,Coda,Obsidian,Roam Research,Evernote"
  * "Salesforce,HubSpot,Pipedrive,Zoho CRM,Monday.com"
  * "Figma,Sketch,Adobe XD,InVision,Framer"
  * "Shopify,WooCommerce,BigCommerce,Magento,Wix"
- Selection criteria:
  * Choose the most well-known/searched competitors in the same category
  * Prioritize direct competitors over tangential alternatives
  * If main product unknown, choose 5 market leaders in the identified category

Critical rules:
- trends_comparison is a SINGLE STRING, not a list
- Format for trends: "Product1,Product2,Product3,Product4,Product5" (exactly like this)
- Must have 3-5 comma-separated terms in trends_comparison
- ALL queries must be concise and keyword-optimized
- Think like you're typing into a search box, not asking a question
- Optimize for extracting structured data from SERP results

Return strict JSON matching the schema."""

    def _validate_parsed_output(self, parsed: ParsedQuery) -> None:
        """Validate the parsed output meets minimum requirements."""
        if not parsed.search_questions:
            raise ValueError("Missing search questions")
        
        # Validate trends comparison format
        trends_terms = parsed.trends_comparison.split(',')
        if len(trends_terms) < 3 or len(trends_terms) > 5:
            raise ValueError("trends_comparison must have 3-5 comma-separated terms")
        
        # Check for minimum quality
        all_questions = (
            parsed.search_questions + 
            parsed.news_questions
        )
        
        if len(all_questions) < 4:
            raise ValueError("Insufficient number of research questions generated")
        
        # Validate at least one comparison query exists
        has_comparison = any(
            'vs' in q.lower() or 'alternative' in q.lower() or 
            'competitor' in q.lower() or 'best' in q.lower() 
            for q in parsed.search_questions
        )
        
        if not has_comparison:
            raise ValueError("search_questions must include at least one comparison or alternatives query")