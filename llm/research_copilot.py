import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import json
from datetime import datetime
import dotenv

dotenv.load_dotenv()


# ============================================================================
# MARKET RESEARCH SYNTHESIZER - SIMPLIFIED VERSION
# ============================================================================

class MarketResearchSynthesizer:
    """
    Synthesizes market research data into comprehensive structured reports
    Uses simple JSON prompting instead of structured output schemas
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        self.client = genai.Client(api_key=self.api_key)
    
    async def generate_report(
        self,
        product_name: str,
        category: str,
        search_results: List[Dict],
        scraped_news: List[Dict],
        trends_results: Dict
    ) -> Dict[str, Any]:
        """
        Generate comprehensive market research report
        
        Args:
            product_name: Name of the product being researched
            category: Product category
            search_results: Cleaned Google search results
            scraped_news: Cleaned and scraped news articles
            trends_results: Google Trends data
        
        Returns:
            Dictionary with complete market research report
        """
        
        prompt = self._build_research_prompt(
            product_name=product_name,
            category=category,
            search_results=search_results,
            scraped_news=scraped_news,
            trends_results=trends_results
        )
        
        try:
            response = await self.client.aio.models.generate_content(
                model="gemini-flash-latest",  # Use fast model
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=8000,
                ),
            )
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            report = json.loads(response_text)
            
            # Add metadata
            report['product_name'] = product_name
            report['category'] = category
            report['report_date'] = datetime.now().strftime("%Y-%m-%d")
            
            return report
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON response: {str(e)}\n\nResponse: {response_text[:500]}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate research report: {str(e)}")
    
    def _build_research_prompt(
        self,
        product_name: str,
        category: str,
        search_results: List[Dict],
        scraped_news: List[Dict],
        trends_results: Dict
    ) -> str:
        """Build the comprehensive research prompt"""
        
        return f"""You are a senior SaaS market research analyst. Analyze the data and create a comprehensive market research report for {product_name}.

# DATA SOURCES

## Search Results
{json.dumps(search_results, indent=2)[:5000]}

## News Articles  
{json.dumps(scraped_news, indent=2)[:5000]}

## Trends Data
{json.dumps(trends_results, indent=2)}

# TASK

Generate a JSON report with this EXACT structure:

{{
  "executive_summary": {{
    "overview": "2-3 sentence overview of {product_name}",
    "market_position": "Current market standing",
    "key_strengths": ["strength 1", "strength 2", "strength 3"],
    "primary_challenges": ["challenge 1", "challenge 2"],
    "strategic_recommendation": "One clear recommendation"
  }},
  
  "pricing_analysis": {{
    "tiers": [
      {{
        "name": "Free/Basic/Pro/Enterprise",
        "price_per_user": "$X/month or null",
        "key_features": ["feature 1", "feature 2"],
        "participant_limit": 100,
        "meeting_duration": "40 minutes"
      }}
    ],
    "value_proposition": "How pricing positions the product",
    "competitive_positioning": "Premium/mid-market/budget",
    "key_differentiators": ["differentiator 1", "differentiator 2"]
  }},
  
  "competitive_landscape": {{
    "main_competitors": [
      {{
        "name": "Competitor Name",
        "market_position": "Leader/Challenger/Niche",
        "key_advantages": ["advantage 1", "advantage 2"],
        "weaknesses": ["weakness 1", "weakness 2"],
        "search_interest_score": 85.5
      }}
    ],
    "market_leader": "Company name",
    "competitive_advantages": ["advantage 1", "advantage 2"],
    "competitive_threats": ["threat 1", "threat 2"],
    "switching_drivers": {{
      "Choose {product_name}": "Reason customers choose it",
      "Switch away": "Reason customers leave"
    }}
  }},
  
  "product_intelligence": {{
    "core_capabilities": [
      {{
        "category": "Core Features/AI/Security/etc",
        "features": ["feature 1", "feature 2"],
        "competitive_edge": "How this beats competitors"
      }}
    ],
    "unique_differentiators": ["unique feature 1", "unique feature 2"],
    "integration_ecosystem": ["integration 1", "integration 2"],
    "limitations": ["limitation 1", "limitation 2"]
  }},
  
  "recent_developments": [
    {{
      "category": "Product Launch/Partnership/Funding/etc",
      "title": "Brief title",
      "description": "What happened",
      "impact": "Why it matters",
      "date": "2024-01-15 or null"
    }}
  ],
  
  "market_trends": {{
    "search_trend": "rising/stable/declining",
    "market_momentum": "Assessment of momentum",
    "growth_indicators": ["indicator 1", "indicator 2"],
    "risk_indicators": ["risk 1", "risk 2"]
  }},
  
  "strategic_insights": {{
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "opportunities": ["opportunity 1", "opportunity 2"],
    "threats": ["threat 1", "threat 2"],
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
  }}
}}

# RULES

1. Extract REAL data from the sources - don't make things up
2. Use exact prices, numbers, and facts from search results
3. If information is missing, use null or empty arrays
4. Focus on actionable insights
5. Keep descriptions concise but informative
6. Return ONLY valid JSON, no markdown, no explanations

Generate the report now as pure JSON:"""

    def export_to_json(self, report: Dict[str, Any], filepath: str):
        """Export report to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✅ Report exported to {filepath}")
    
    def export_to_markdown(self, report: Dict[str, Any], filepath: str):
        """Export report to Markdown file"""
        md = self._generate_markdown(report)
        with open(filepath, 'w') as f:
            f.write(md)
        print(f"✅ Report exported to {filepath}")
    
    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        """Convert report to formatted Markdown"""
        
        product_name = report.get('product_name', 'Unknown Product')
        category = report.get('category', 'Unknown Category')
        report_date = report.get('report_date', datetime.now().strftime("%Y-%m-%d"))
        
        exec_summary = report.get('executive_summary', {})
        pricing = report.get('pricing_analysis', {})
        competitive = report.get('competitive_landscape', {})
        product = report.get('product_intelligence', {})
        developments = report.get('recent_developments', [])
        trends = report.get('market_trends', {})
        insights = report.get('strategic_insights', {})
        
        md = f"""# {product_name} - Market Research Report
**Category:** {category}  
**Report Date:** {report_date}

---

## Executive Summary

### Overview
{exec_summary.get('overview', 'N/A')}

### Market Position
{exec_summary.get('market_position', 'N/A')}

### Key Strengths
{self._list_to_md(exec_summary.get('key_strengths', []))}

### Primary Challenges
{self._list_to_md(exec_summary.get('primary_challenges', []))}

### Strategic Recommendation
{exec_summary.get('strategic_recommendation', 'N/A')}

---

## Pricing Analysis

### Value Proposition
{pricing.get('value_proposition', 'N/A')}

### Competitive Positioning
{pricing.get('competitive_positioning', 'N/A')}

### Pricing Tiers

{self._pricing_tiers_to_md(pricing.get('tiers', []))}

### Key Differentiators
{self._list_to_md(pricing.get('key_differentiators', []))}

---

## Competitive Landscape

**Market Leader:** {competitive.get('market_leader', 'N/A')}

### Main Competitors

{self._competitors_to_md(competitive.get('main_competitors', []))}

### Our Competitive Advantages
{self._list_to_md(competitive.get('competitive_advantages', []))}

### Competitive Threats
{self._list_to_md(competitive.get('competitive_threats', []))}

### Switching Drivers
{self._dict_to_md(competitive.get('switching_drivers', {}))}

---

## Product Intelligence

### Core Capabilities

{self._capabilities_to_md(product.get('core_capabilities', []))}

### Unique Differentiators
{self._list_to_md(product.get('unique_differentiators', []))}

### Integration Ecosystem
{self._list_to_md(product.get('integration_ecosystem', []))}

### Known Limitations
{self._list_to_md(product.get('limitations', []))}

---

## Recent Strategic Developments

{self._developments_to_md(developments)}

---

## Market Trends & Momentum

**Search Trend:** {trends.get('search_trend', 'N/A')}  
**Market Momentum:** {trends.get('market_momentum', 'N/A')}

### Growth Indicators
{self._list_to_md(trends.get('growth_indicators', []))}

### Risk Indicators
{self._list_to_md(trends.get('risk_indicators', []))}

---

## Strategic Insights (SWOT Analysis)

### Strengths
{self._list_to_md(insights.get('strengths', []))}

### Weaknesses
{self._list_to_md(insights.get('weaknesses', []))}

### Opportunities
{self._list_to_md(insights.get('opportunities', []))}

### Threats
{self._list_to_md(insights.get('threats', []))}

### Strategic Recommendations
{self._list_to_md(insights.get('recommendations', []))}

---

*Report generated by Market Research Copilot*
"""
        return md
    
    # Helper methods for Markdown formatting
    def _list_to_md(self, items: List[str]) -> str:
        if not items:
            return "- N/A"
        return "\n".join(f"- {item}" for item in items)
    
    def _dict_to_md(self, items: Dict[str, str]) -> str:
        if not items:
            return "- N/A"
        return "\n".join(f"- **{k}**: {v}" for k, v in items.items())
    
    def _pricing_tiers_to_md(self, tiers: List[Dict]) -> str:
        if not tiers:
            return "No pricing information available.\n"
        
        md = ""
        for tier in tiers:
            md += f"\n#### {tier.get('name', 'Unknown Tier')}\n"
            if tier.get('price_per_user'):
                md += f"**Price:** {tier['price_per_user']}\n"
            if tier.get('participant_limit'):
                md += f"**Participants:** {tier['participant_limit']}\n"
            if tier.get('meeting_duration'):
                md += f"**Duration:** {tier['meeting_duration']}\n"
            md += "\n**Features:**\n"
            md += self._list_to_md(tier.get('key_features', []))
            md += "\n"
        return md
    
    def _competitors_to_md(self, competitors: List[Dict]) -> str:
        if not competitors:
            return "No competitor information available.\n"
        
        md = ""
        for comp in competitors:
            md += f"\n#### {comp.get('name', 'Unknown Competitor')}\n"
            md += f"**Market Position:** {comp.get('market_position', 'N/A')}\n\n"
            if comp.get('search_interest_score'):
                md += f"**Search Interest Score:** {comp['search_interest_score']}\n\n"
            md += "**Advantages:**\n"
            md += self._list_to_md(comp.get('key_advantages', []))
            md += "\n\n**Weaknesses:**\n"
            md += self._list_to_md(comp.get('weaknesses', []))
            md += "\n"
        return md
    
    def _capabilities_to_md(self, capabilities: List[Dict]) -> str:
        if not capabilities:
            return "No capability information available.\n"
        
        md = ""
        for cap in capabilities:
            md += f"\n#### {cap.get('category', 'Unknown Category')}\n"
            md += self._list_to_md(cap.get('features', []))
            if cap.get('competitive_edge'):
                md += f"\n\n*Competitive Edge:* {cap['competitive_edge']}"
            md += "\n"
        return md
    
    def _developments_to_md(self, developments: List[Dict]) -> str:
        if not developments:
            return "No recent developments available.\n"
        
        md = ""
        for dev in developments:
            md += f"\n### {dev.get('title', 'Unknown Development')}\n"
            md += f"**Category:** {dev.get('category', 'N/A')}\n"
            if dev.get('date'):
                md += f"**Date:** {dev['date']}\n"
            md += f"\n{dev.get('description', 'N/A')}\n\n"
            md += f"**Impact:** {dev.get('impact', 'N/A')}\n"
            md += "\n---\n"
        return md