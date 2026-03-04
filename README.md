# talabat Partner Intelligence — AI Agent Demo

> An AI-powered B2B partner management platform built to showcase the core workflows of talabat's **Senior PM - AI** role.

**[Live Demo →](https://talabat-partner-intelligence.streamlit.app/)**

---

## What This Demo Does

Three AI agent workflows powered by **Claude Sonnet** (Anthropic) with a **tool-use agentic loop**:

### 🎯 Sales Acquisition Agent
Scores a pipeline of prospective restaurant partners, filters by area/cuisine/score, and writes personalised outreach emails — complete with AED revenue projections, competitor gap analysis, and value propositions tailored to each lead.

### 📋 Partner Onboarding Agent
Takes a new restaurant partner and generates a milestone-based onboarding plan targeting **first order in 7 days** and **100 orders by day 30** — factoring in cuisine type, area demand, menu readiness, and similar-partner benchmarks.

### 🛡️ Retention & Churn Prevention Agent
Analyses a portfolio of 30 active partners across 5 health signals (order trends, completion rate, engagement, support tickets, promo participation), identifies root causes for at-risk partners, and generates specific intervention plans.

---

## Architecture

```
Streamlit UI  →  Agent Runner (base_agent.py)  →  Claude Sonnet API
                        ↓
               Tool-use agentic loop
               (Claude calls tools, gets results, iterates)
                        ↓
               Tool functions (sales / onboarding / retention)
                        ↓
               Deterministic seed data (20 leads, 30 partners)
```

**Pattern:** Claude receives a system prompt + user goal, then iteratively calls predefined Python functions (tools) until it constructs a complete response. All reasoning is streamed to the UI in real time.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI Framework | Streamlit |
| AI Model | Claude Sonnet 4.6 (Anthropic) |
| Agent Pattern | Tool-use agentic loop |
| Data Validation | Pydantic v2 |
| Visualization | Plotly |
| Language | Python 3.9+ |

---

## Run Locally

```bash
# 1. Clone and install dependencies
git clone https://github.com/saahilnagrani/talabat-partner-intelligence
cd talabat-partner-intelligence
pip install -r requirements.txt

# 2. Set your Anthropic API key
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env

# 3. Run the app
streamlit run app.py
```

Get an API key at [console.anthropic.com](https://console.anthropic.com).

---

## Project Structure

```
├── app.py                  # Streamlit entry point
├── config.py               # Model config, thresholds, constants
├── agents/
│   ├── base_agent.py       # Core agentic loop (streaming + tool execution)
│   ├── sales_agent.py      # Sales workflow runner
│   ├── onboarding_agent.py # Onboarding workflow runner
│   └── retention_agent.py  # Retention workflow runner
├── tools/
│   ├── sales_tools.py      # Lead scoring, outreach generation
│   ├── onboarding_tools.py # Plan building, forecasts, promo logic
│   └── retention_tools.py  # Health scoring, root cause, interventions
├── ui/
│   ├── components.py       # Reusable Streamlit components + CSS
│   ├── sales_tab.py        # Sales tab UI
│   ├── onboarding_tab.py   # Onboarding tab UI
│   └── retention_tab.py    # Retention tab UI
└── data/
    ├── models.py           # Pydantic data models
    └── seed.py             # Deterministic test dataset (20 leads, 30 partners)
```

---

*All restaurant data is simulated for demo purposes.*
