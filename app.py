"""
talabat Partner Intelligence — AI Agent Demo
Main Streamlit application entry point.
"""
import streamlit as st
from config import get_api_key
from ui.components import inject_css, render_header
import ui.sales_tab as sales_tab
import ui.onboarding_tab as onboarding_tab
import ui.retention_tab as retention_tab

st.set_page_config(
    page_title="talabat AI Agent Demo",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    # 1. About
    st.markdown("## 📖 About This Tool")
    st.markdown(
        "This demo showcases an AI-powered **B2B Partner Intelligence Platform** for talabat, "
        "reflecting the core responsibilities of the **Senior PM - AI** role:\n\n"
        "🎯 **Sales Acquisition** — scores leads, writes personalised outreach\n\n"
        "📋 **Partner Onboarding** — builds milestone-based onboarding plans\n\n"
        "🛡️ **Retention** — analyses churn signals and generates interventions"
    )

    # 2. Built with
    st.divider()
    st.markdown("**Built with:**")
    st.markdown(
        "- Claude Sonnet (Anthropic)\n"
        "- Streamlit\n"
        "- Python tool_use API (agentic loop)"
    )
    st.caption("*All restaurant data is simulated for demo purposes.*")

    # 3+4. Model / Pattern
    st.divider()
    st.markdown("**Model:** `claude-sonnet-4-6`")
    st.markdown("**Pattern:** Tool-use agentic loop")

    # 5. Configuration
    st.divider()
    st.markdown("## ⚙️ Configuration")
    env_key = get_api_key()
    if env_key:
        st.success("✅ API key loaded")
        api_key = env_key
    else:
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Get your key from console.anthropic.com",
        )
        if api_key:
            import os
            os.environ["ANTHROPIC_API_KEY"] = api_key

    # 6. Version
    st.divider()
    st.caption("v2.1 — Quick Outreach · Email History · Gmail/Outlook")

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
render_header()

if not get_api_key():
    st.warning(
        "⚠️ No Anthropic API key found. "
        "Add it in the sidebar or set `ANTHROPIC_API_KEY` in your `.env` file to run the agents."
    )

tab1, tab2, tab3 = st.tabs([
    "🎯 Sales Acquisition",
    "📋 Partner Onboarding",
    "🛡️ Retention",
])

with tab1:
    sales_tab.render()

with tab2:
    onboarding_tab.render()

with tab3:
    retention_tab.render()
