import streamlit as st
import asyncio
import json
import time
from graph.graph import build_graph

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Research Copilot",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS — dark premium theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Root overrides ── */
:root {
    --bg-primary: #0d1117;
    --bg-card: #161b22;
    --bg-card-hover: #1c2333;
    --accent: #58a6ff;
    --accent-glow: rgba(88,166,255,.15);
    --green: #3fb950;
    --orange: #d29922;
    --red: #f85149;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --border: #30363d;
}

/* Force dark background */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Main container */
.main .block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero h1 {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #58a6ff 0%, #bc8cff 50%, #f778ba 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: .3rem;
}
.hero p {
    color: var(--text-secondary);
    font-size: 1.05rem;
    margin-top: 0;
}

/* ── Query box ── */
div[data-testid="stTextInput"] input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    font-size: 1rem !important;
    transition: border-color .2s;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
} 

/* ── Primary button ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #58a6ff, #bc8cff) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2.5rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: .3px;
    transition: transform .15s, box-shadow .2s;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px var(--accent-glow) !important;
}

/* ── Stage cards ── */
.stage-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: border-color .3s, box-shadow .3s;
    min-height: 180px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.stage-card.active {
    border-color: var(--accent);
    box-shadow: 0 0 24px var(--accent-glow);
}
.stage-card.done {
    border-color: var(--green);
    box-shadow: 0 0 16px rgba(63,185,80,.12);
}
.stage-icon {
    font-size: 2.4rem;
    margin-bottom: .5rem;
}
.stage-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: .25rem;
}
.stage-desc {
    font-size: .82rem;
    color: var(--text-secondary);
    line-height: 1.4;
}
.stage-badge {
    display: inline-block;
    margin-top: .7rem;
    padding: 3px 14px;
    border-radius: 20px;
    font-size: .75rem;
    font-weight: 600;
    letter-spacing: .3px;
}
.badge-waiting  { background: #21262d; color: var(--text-secondary); }
.badge-running  { background: rgba(88,166,255,.15); color: var(--accent); }
.badge-done     { background: rgba(63,185,80,.15); color: var(--green); }

/* ── Report section cards ── */
.report-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 1rem;
}
.report-section h3 {
    margin-top: 0;
    font-size: 1.2rem;
    color: var(--accent);
}
.report-section ul { padding-left: 1.2rem; }
.report-section li { color: var(--text-primary); margin-bottom: .3rem; }

/* ── Metric badge ── */
.metric-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: .82rem;
    font-weight: 600;
    margin: 2px 4px;
}
.metric-green  { background: rgba(63,185,80,.15); color: var(--green); }
.metric-orange { background: rgba(210,153,34,.15); color: var(--orange); }
.metric-red    { background: rgba(248,81,73,.15);  color: var(--red); }
.metric-blue   { background: rgba(88,166,255,.15); color: var(--accent); }

/* ── SWOT grid ── */
.swot-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
    min-height: 140px;
}
.swot-card h4 { margin-top: 0; font-size: 1rem; }
.swot-card ul { padding-left: 1rem; margin-top: .5rem; }
.swot-card li { font-size: .88rem; color: var(--text-primary); margin-bottom: .25rem; }

/* ── Competitor card ── */
.comp-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
}
.comp-card h4 { margin-top: 0; color: var(--text-primary); }
.comp-card .pos { font-size: .8rem; color: var(--text-secondary); }

/* ── Pricing tier card ── */
.tier-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.3rem;
    text-align: center;
    min-height: 200px;
}
.tier-card h4 {
    margin-top: 0;
    color: var(--accent);
    font-size: 1.05rem;
}
.tier-price {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: .5rem 0;
}

/* ── Timeline ── */
.timeline-item {
    background: var(--bg-card);
    border-left: 3px solid var(--accent);
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.2rem;
    margin-bottom: .8rem;
}
.timeline-item h4 { margin: 0 0 .3rem; color: var(--text-primary); font-size: .95rem; }
.timeline-item .meta { font-size: .78rem; color: var(--text-secondary); margin-bottom: .4rem;}
.timeline-item p { font-size: .88rem; color: var(--text-primary); margin: .3rem 0; }

/* ── Divider ── */
.section-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

/* Hide default Streamlit footer & menu */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }

/* Streamlit status widget tweaks */
[data-testid="stStatusWidget"] {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🔬 Market Research Copilot</h1>
    <p>AI-powered competitive intelligence — powered by Gemini &amp; SerpAPI</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# STAGE DEFINITIONS
# ─────────────────────────────────────────────────────────────
STAGES = [
    {
        "icon": "🧠",
        "title": "Planner",
        "desc": "Parsing your query, extracting product name & category, generating targeted search questions",
        "nodes": ["parse_query"],
    },
    {
        "icon": "⚙️",
        "title": "Executor",
        "desc": "Running Google Search, News & Trends APIs, cleaning data, scraping full article text",
        "nodes": ["discover_serp", "clean_data", "scrape_news"],
    },
    {
        "icon": "📊",
        "title": "Summarizer",
        "desc": "Synthesizing all data into a structured market research report via Gemini",
        "nodes": ["generate_report"],
    },
]


def render_stage_cards(statuses: dict):
    """Render the 3 stage cards with current statuses."""
    cols = st.columns(3, gap="large")
    for i, (col, stage) in enumerate(zip(cols, STAGES)):
        status = statuses.get(stage["title"], "waiting")
        card_cls = "active" if status == "running" else ("done" if status == "done" else "")
        badge_cls = f"badge-{status}"
        badge_label = {"waiting": "⏳ WAITING", "running": "🔄 RUNNING", "done": "✅ COMPLETE"}[status]

        # Arrow connector between cards
        with col:
            st.markdown(f"""
            <div class="stage-card {card_cls}">
                <div class="stage-icon">{stage['icon']}</div>
                <div class="stage-title">{stage['title']}</div>
                <div class="stage-desc">{stage['desc']}</div>
                <span class="stage-badge {badge_cls}">{badge_label}</span>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# REPORT RENDERING HELPERS
# ─────────────────────────────────────────────────────────────
def render_executive_summary(data: dict):
    es = data.get("executive_summary", {})
    st.markdown("""<div class="report-section"><h3>📋 Executive Summary</h3></div>""", unsafe_allow_html=True)

    st.markdown(f"**Overview** — {es.get('overview', 'N/A')}")
    st.markdown(f"**Market Position** — {es.get('market_position', 'N/A')}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 💪 Key Strengths")
        for s in es.get("key_strengths", []):
            st.markdown(f"- {s}")
    with c2:
        st.markdown("##### ⚠️ Primary Challenges")
        for c in es.get("primary_challenges", []):
            st.markdown(f"- {c}")

    st.info(f"**Strategic Recommendation:** {es.get('strategic_recommendation', 'N/A')}")


def render_pricing(data: dict):
    pricing = data.get("pricing_analysis", {})
    st.markdown("""<div class="report-section"><h3>💰 Pricing Analysis</h3></div>""", unsafe_allow_html=True)

    st.markdown(f"**Value Proposition** — {pricing.get('value_proposition', 'N/A')}")
    st.markdown(f"**Competitive Positioning** — `{pricing.get('competitive_positioning', 'N/A')}`")

    tiers = pricing.get("tiers", [])
    if tiers:
        cols = st.columns(min(len(tiers), 4))
        for col, tier in zip(cols, tiers):
            with col:
                price = tier.get("price_per_user", "N/A")
                features_html = "".join(f"<li>{f}</li>" for f in tier.get("key_features", []))
                extras = ""
                if tier.get("participant_limit"):
                    extras += f"<div style='font-size:.78rem;color:#8b949e;margin-top:.4rem;'>👥 {tier['participant_limit']} participants</div>"
                if tier.get("meeting_duration"):
                    extras += f"<div style='font-size:.78rem;color:#8b949e;'>⏱ {tier['meeting_duration']}</div>"

                st.markdown(f"""
                <div class="tier-card">
                    <h4>{tier.get('name','Tier')}</h4>
                    <div class="tier-price">{price}</div>
                    <ul style="text-align:left;font-size:.85rem;color:#e6edf3;">{features_html}</ul>
                    {extras}
                </div>
                """, unsafe_allow_html=True)

    diffs = pricing.get("key_differentiators", [])
    if diffs:
        st.markdown("##### Key Differentiators")
        for d in diffs:
            st.markdown(f'<span class="metric-badge metric-blue">{d}</span>', unsafe_allow_html=True)


def render_competitive_landscape(data: dict):
    comp = data.get("competitive_landscape", {})
    st.markdown("""<div class="report-section"><h3>🏆 Competitive Landscape</h3></div>""", unsafe_allow_html=True)

    st.markdown(f"**Market Leader:** `{comp.get('market_leader', 'N/A')}`")

    competitors = comp.get("main_competitors", [])
    if competitors:
        cols = st.columns(min(len(competitors), 3))
        for col, c in zip(cols, competitors):
            with col:
                advs = "".join(f"<li>{a}</li>" for a in c.get("key_advantages", []))
                weaks = "".join(f"<li>{w}</li>" for w in c.get("weaknesses", []))
                score = c.get("search_interest_score", "")
                score_html = f'<span class="metric-badge metric-orange">🔍 {score}</span>' if score else ""
                st.markdown(f"""
                <div class="comp-card">
                    <h4>{c.get('name','Competitor')}</h4>
                    <div class="pos">{c.get('market_position','')} {score_html}</div>
                    <p style='font-size:.82rem;color:#3fb950;margin:.5rem 0 .2rem;font-weight:600;'>Advantages</p>
                    <ul style="font-size:.85rem;padding-left:1rem;">{advs}</ul>
                    <p style='font-size:.82rem;color:#f85149;margin:.5rem 0 .2rem;font-weight:600;'>Weaknesses</p>
                    <ul style="font-size:.85rem;padding-left:1rem;">{weaks}</ul>
                </div>
                """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### ✅ Our Competitive Advantages")
        for a in comp.get("competitive_advantages", []):
            st.markdown(f"- {a}")
    with c2:
        st.markdown("##### 🚨 Competitive Threats")
        for t in comp.get("competitive_threats", []):
            st.markdown(f"- {t}")

    drivers = comp.get("switching_drivers", {})
    if drivers:
        st.markdown("##### 🔄 Switching Drivers")
        for k, v in drivers.items():
            st.markdown(f"- **{k}:** {v}")


def render_product_intelligence(data: dict):
    prod = data.get("product_intelligence", {})
    st.markdown("""<div class="report-section"><h3>🔍 Product Intelligence</h3></div>""", unsafe_allow_html=True)

    caps = prod.get("core_capabilities", [])
    if caps:
        for cap in caps:
            with st.expander(f"🔹 {cap.get('category', 'Capability')}", expanded=True):
                for f in cap.get("features", []):
                    st.markdown(f"- {f}")
                edge = cap.get("competitive_edge")
                if edge:
                    st.caption(f"*Competitive Edge:* {edge}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 🌟 Unique Differentiators")
        for d in prod.get("unique_differentiators", []):
            st.markdown(f'<span class="metric-badge metric-green">{d}</span>', unsafe_allow_html=True)
    with c2:
        st.markdown("##### 🔗 Integration Ecosystem")
        for i in prod.get("integration_ecosystem", []):
            st.markdown(f'<span class="metric-badge metric-blue">{i}</span>', unsafe_allow_html=True)

    limitations = prod.get("limitations", [])
    if limitations:
        st.markdown("##### ⚠️ Known Limitations")
        for l in limitations:
            st.markdown(f"- {l}")


def render_recent_developments(data: dict):
    devs = data.get("recent_developments", [])
    st.markdown("""<div class="report-section"><h3>📰 Recent Developments</h3></div>""", unsafe_allow_html=True)

    if not devs:
        st.caption("No recent developments available.")
        return

    for dev in devs:
        date = dev.get("date", "")
        date_html = f'<span style="color:#58a6ff;font-weight:600;">{date}</span> · ' if date else ""
        st.markdown(f"""
        <div class="timeline-item">
            <h4>{dev.get('title','Development')}</h4>
            <div class="meta">{date_html}{dev.get('category','')}</div>
            <p>{dev.get('description','')}</p>
            <p style="font-size:.82rem;color:#3fb950;"><strong>Impact:</strong> {dev.get('impact','')}</p>
        </div>
        """, unsafe_allow_html=True)


def render_market_trends(data: dict):
    trends = data.get("market_trends", {})
    st.markdown("""<div class="report-section"><h3>📈 Market Trends & Momentum</h3></div>""", unsafe_allow_html=True)

    trend_dir = trends.get("search_trend", "stable")
    trend_colors = {"rising": "metric-green", "stable": "metric-orange", "declining": "metric-red"}
    trend_icons = {"rising": "📈", "stable": "➡️", "declining": "📉"}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'**Search Trend:** <span class="metric-badge {trend_colors.get(trend_dir, "metric-orange")}">{trend_icons.get(trend_dir, "➡️")} {trend_dir.upper()}</span>', unsafe_allow_html=True)
    with c2:
        st.markdown(f"**Momentum:** {trends.get('market_momentum', 'N/A')}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 🟢 Growth Indicators")
        for g in trends.get("growth_indicators", []):
            st.markdown(f"- {g}")
    with c2:
        st.markdown("##### 🔴 Risk Indicators")
        for r in trends.get("risk_indicators", []):
            st.markdown(f"- {r}")


def render_swot(data: dict):
    insights = data.get("strategic_insights", {})
    st.markdown("""<div class="report-section"><h3>📊 Strategic Insights (SWOT)</h3></div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        items = "".join(f"<li>{s}</li>" for s in insights.get("strengths", []))
        st.markdown(f"""
        <div class="swot-card" style="border-left:3px solid #3fb950;">
            <h4 style="color:#3fb950;">💪 Strengths</h4>
            <ul>{items}</ul>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        items = "".join(f"<li>{s}</li>" for s in insights.get("weaknesses", []))
        st.markdown(f"""
        <div class="swot-card" style="border-left:3px solid #f85149;">
            <h4 style="color:#f85149;">⚠️ Weaknesses</h4>
            <ul>{items}</ul>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        items = "".join(f"<li>{s}</li>" for s in insights.get("opportunities", []))
        st.markdown(f"""
        <div class="swot-card" style="border-left:3px solid #58a6ff;">
            <h4 style="color:#58a6ff;">🚀 Opportunities</h4>
            <ul>{items}</ul>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        items = "".join(f"<li>{s}</li>" for s in insights.get("threats", []))
        st.markdown(f"""
        <div class="swot-card" style="border-left:3px solid #d29922;">
            <h4 style="color:#d29922;">🛡️ Threats</h4>
            <ul>{items}</ul>
        </div>
        """, unsafe_allow_html=True)

    recs = insights.get("recommendations", [])
    if recs:
        st.markdown("##### 🎯 Strategic Recommendations")
        for i, r in enumerate(recs, 1):
            st.markdown(f"**{i}.** {r}")


def render_full_report(report: dict):
    """Render the full market research report."""
    product = report.get("product_name", "Product")
    category = report.get("category", "")
    date = report.get("report_date", "")

    st.markdown(f"""
    <div style="text-align:center;margin:2rem 0 1rem;">
        <h2 style="color:#e6edf3;font-size:2rem;margin-bottom:.2rem;">{product} — Market Research Report</h2>
        <p style="color:#8b949e;font-size:.9rem;">{category} · {date}</p>
    </div>
    <hr class="section-divider">
    """, unsafe_allow_html=True)

    render_executive_summary(report)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    render_pricing(report)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    render_competitive_landscape(report)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    render_product_intelligence(report)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    render_recent_developments(report)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    render_market_trends(report)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    render_swot(report)

    # Footer
    st.markdown("""
    <hr class="section-divider">
    <p style="text-align:center;color:#8b949e;font-size:.82rem;padding:1rem 0;">
        Report generated by <strong style="color:#58a6ff;">Market Research Copilot</strong> · Powered by Gemini &amp; SerpAPI
    </p>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# PIPELINE RUNNER
# ─────────────────────────────────────────────────────────────
async def run_pipeline(query: str):
    """
    Run the LangGraph pipeline with stage-wise progress tracking.
    Uses st.status() expanders for each stage and updates a
    placeholder for the stage-card visualization.
    """
    graph = build_graph()

    initial_state = {
        "query": query,
        "product_name": None,
        "category": None,
        "keywords": [],
        "search_questions": [],
        "news_questions": [],
        "trends_comparison": "",
        "google_results": [],
        "news_results": [],
        "trends_results": {},
        "scraped_news": [],
        "confidence": {},
        "errors": [],
        "report": None,
    }

    # We'll track which stage we're in based on node callbacks
    stage_statuses = {"Planner": "waiting", "Executor": "waiting", "Summarizer": "waiting"}
    node_to_stage = {}
    for stage in STAGES:
        for node in stage["nodes"]:
            node_to_stage[node] = stage["title"]

    # Stage cards placeholder
    cards_placeholder = st.empty()
    with cards_placeholder.container():
        render_stage_cards(stage_statuses)

    # Detailed progress area
    progress_area = st.container()

    start_time = time.perf_counter()

    # ── Stage 1: Planner ──
    stage_statuses["Planner"] = "running"
    with cards_placeholder.container():
        render_stage_cards(stage_statuses)

    with progress_area:
        with st.status("🧠 **Planner** — Analyzing your query...", expanded=True) as planner_status:
            st.write("Extracting product name and category...")
            st.write("Generating targeted search questions for Google Search, News & Trends...")

            # Run parse_query
            try:
                from graph.nodes import parse_query_node
                initial_state = await parse_query_node(initial_state)
            except Exception as e:
                initial_state.setdefault("errors", []).append(str(e))

            if initial_state.get("product_name"):
                st.write(f"✅ Product identified: **{initial_state['product_name']}**")
            if initial_state.get("category"):
                st.write(f"✅ Category: **{initial_state['category']}**")
            if initial_state.get("search_questions"):
                st.write(f"✅ Generated **{len(initial_state['search_questions'])}** search questions")
            if initial_state.get("news_questions"):
                st.write(f"✅ Generated **{len(initial_state['news_questions'])}** news queries")

            planner_status.update(label="🧠 **Planner** — Complete", state="complete", expanded=False)

    stage_statuses["Planner"] = "done"
    with cards_placeholder.container():
        render_stage_cards(stage_statuses)

    # ── Stage 2: Executor ──
    stage_statuses["Executor"] = "running"
    with cards_placeholder.container():
        render_stage_cards(stage_statuses)

    with progress_area:
        with st.status("⚙️ **Executor** — Collecting market data...", expanded=True) as executor_status:
            # discover_serp
            st.write("🔍 Querying Google Search, News & Trends APIs...")
            try:
                from graph.nodes import discover_via_serp_node
                initial_state = await discover_via_serp_node(initial_state)
            except Exception as e:
                initial_state.setdefault("errors", []).append(str(e))

            google_count = len(initial_state.get("google_results", []))
            news_count = len(initial_state.get("news_results", []))
            st.write(f"✅ Retrieved **{google_count}** search results, **{news_count}** news results")

            # clean_data
            st.write("🧹 Cleaning and structuring raw API data...")
            try:
                from graph.nodes import clean_data_node
                initial_state = await clean_data_node(initial_state)
            except Exception as e:
                initial_state.setdefault("errors", []).append(str(e))
            st.write("✅ Data cleaned and normalized")

            # scrape_news
            st.write("🌐 Scraping full article content from news sources...")
            try:
                from graph.nodes import scrape_news_node
                initial_state = await scrape_news_node(initial_state)
            except Exception as e:
                initial_state.setdefault("errors", []).append(str(e))

            scraped_count = len(initial_state.get("scraped_news", []))
            st.write(f"✅ Scraped **{scraped_count}** full articles")

            executor_status.update(label="⚙️ **Executor** — Complete", state="complete", expanded=False)

    stage_statuses["Executor"] = "done"
    with cards_placeholder.container():
        render_stage_cards(stage_statuses)

    # ── Stage 3: Summarizer ──
    stage_statuses["Summarizer"] = "running"
    with cards_placeholder.container():
        render_stage_cards(stage_statuses)

    with progress_area:
        with st.status("📊 **Summarizer** — Generating market research report...", expanded=True) as summarizer_status:
            st.write("Sending all collected data to Gemini for synthesis...")
            st.write("Generating: Executive Summary, Pricing, Competitors, Product Intelligence, Trends, SWOT...")

            try:
                from graph.nodes import generate_report_node
                initial_state = await generate_report_node(initial_state)
            except Exception as e:
                initial_state.setdefault("errors", []).append(str(e))

            if initial_state.get("report"):
                st.write("✅ Comprehensive market research report generated!")
            else:
                st.write("⚠️ Report generation encountered issues.")

            summarizer_status.update(label="📊 **Summarizer** — Complete", state="complete", expanded=False)

    stage_statuses["Summarizer"] = "done"
    with cards_placeholder.container():
        render_stage_cards(stage_statuses)

    elapsed = time.perf_counter() - start_time

    # ── Execution summary ──
    with progress_area:
        c1, c2, c3 = st.columns(3)
        c1.metric("⏱ Total Time", f"{elapsed:.1f}s")
        c2.metric("📄 Status", "✅ Success" if initial_state.get("report") else "❌ Failed")
        c3.metric("⚠️ Errors", len(initial_state.get("errors", [])))

    # Save report
    report = initial_state.get("report")
    if report:
        with open("final_report.json", "w") as f:
            json.dump(report, f, indent=2)

    return initial_state


# ─────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────

# Query input
query = st.text_input(
    "🔎 Enter your research query",
    placeholder="e.g. do research for zoom - a video conferencing tool",
    label_visibility="collapsed",
)

# Center the button
_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    run_clicked = st.button("🚀 Run Research", use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# Pipeline execution
if run_clicked and query:
    final_state = asyncio.run(run_pipeline(query))
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    report = final_state.get("report")
    if report:
        render_full_report(report)

        # Download buttons
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "📥 Download JSON Report",
                data=json.dumps(report, indent=2),
                file_name="market_research_report.json",
                mime="application/json",
                use_container_width=True,
            )
        with c2:
            # Generate markdown for download
            from llm.research_copilot import MarketResearchSynthesizer
            synth = MarketResearchSynthesizer()
            md_content = synth._generate_markdown(report)
            st.download_button(
                "📥 Download Markdown Report",
                data=md_content,
                file_name="market_research_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
    else:
        st.error("❌ Failed to generate report. Check errors above for details.")

        errors = final_state.get("errors", [])
        if errors:
            with st.expander("🔍 Error Details", expanded=True):
                for err in errors:
                    st.code(err)

elif run_clicked and not query:
    st.warning("Please enter a research query to get started.")
