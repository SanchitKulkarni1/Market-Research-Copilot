# 🔬 Market Research Copilot

AI-powered competitive intelligence platform that generates comprehensive market research reports. Built with **LangGraph**, **Gemini**, and **SerpAPI**, wrapped in a sleek **Streamlit** UI.

---

## ✨ What It Does

Enter a product query (e.g. *"do research for Zoom - a video conferencing tool"*) and the copilot runs a 3-stage pipeline:

| Stage | What Happens |
|-------|-------------|
| 🧠 **Planner** | Parses the query, extracts product name & category, generates targeted search questions |
| ⚙️ **Executor** | Runs Google Search, News & Trends APIs → cleans data → scrapes full article text |
| 📊 **Summarizer** | Synthesizes everything into a structured market research report via Gemini |

The final report covers **Executive Summary**, **Pricing Analysis**, **Competitive Landscape**, **Product Intelligence**, **Recent Developments**, **Market Trends**, and a full **SWOT Analysis**.

---

## 🏗️ Architecture

```
Market-Research-Copilot/
├── app.py                  # Streamlit UI (dark theme, stage progress, report rendering)
├── main.py                 # CLI entry point (async pipeline runner)
├── graph/
│   ├── state.py            # ResearchState TypedDict — shared pipeline state
│   ├── graph.py            # LangGraph StateGraph definition (5 nodes, linear flow)
│   └── nodes.py            # Node functions: parse_query, discover_serp, clean_data, scrape_news, generate_report
├── llm/
│   ├── queryparser.py      # Gemini-powered query → research plan generator (structured output)
│   └── research_copilot.py # Gemini-powered data → market research report synthesizer
├── tools/
│   ├── serp.py             # Async SerpAPI client (Google Search, News, Trends)
│   └── webscrapping.py     # Async web scraper using Trafilatura
├── cleaners/
│   ├── google_engine.py    # Cleans raw Google Search API responses
│   ├── google_news.py      # Cleans raw Google News API responses
│   └── google_trends.py    # Cleans raw Google Trends API responses
├── final_report.json       # Latest generated report (auto-saved)
└── .env                    # API keys (GOOGLE_API_KEY, SERP_API_KEY)
```

### Pipeline Flow

```
parse_query → discover_serp → clean_data → scrape_news → generate_report → END
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- [Google AI API Key](https://aistudio.google.com/apikey) (Gemini)
- [SerpAPI Key](https://serpapi.com/)

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install streamlit langgraph google-genai httpx trafilatura pydantic python-dotenv
```

### 3. Configure Environment

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
SERP_API_KEY=your_serpapi_key_here
```

### 4. Run the App

**Streamlit UI** (recommended):

```bash
streamlit run app.py
```

**CLI mode**:

```bash
python main.py
```

---

## 🖥️ UI Features

- **Dark premium theme** with gradient accents and glassmorphic cards
- **Stage-wise progress tracking** — watch Planner → Executor → Summarizer animate through Waiting → Running → Complete
- **Structured report rendering** — Executive Summary, Pricing Tiers, Competitor Cards, SWOT Quadrants, Timeline
- **Download options** — Export as JSON or Markdown

---

## 📊 Sample Output

The report JSON contains these sections:

| Section | Description |
|---------|-------------|
| `executive_summary` | Overview, market position, strengths, challenges, recommendation |
| `pricing_analysis` | Tier breakdown with prices, features, participant limits |
| `competitive_landscape` | Competitors with advantages, weaknesses, search interest scores |
| `product_intelligence` | Core capabilities, differentiators, integrations, limitations |
| `recent_developments` | Product launches, partnerships, funding — with impact analysis |
| `market_trends` | Search trend direction, growth indicators, risk indicators |
| `strategic_insights` | Full SWOT analysis + actionable recommendations |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM | [Gemini 3.0 Flash](https://ai.google.dev/) (query parsing + report synthesis) |
| Search APIs | [SerpAPI](https://serpapi.com/) (Google Search, News, Trends) |
| Web Scraping | [Trafilatura](https://github.com/adbar/trafilatura) |
| Frontend | [Streamlit](https://streamlit.io/) |
| Schema Validation | [Pydantic](https://docs.pydantic.dev/) |
| HTTP Client | [httpx](https://www.python-httpx.org/) (async) |

---

*Built with ❤️ by Sanchit Kulkarni*
