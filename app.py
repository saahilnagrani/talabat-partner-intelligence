"""
talabat Partner Intelligence — AI Agent Demo
Main Streamlit application entry point.
"""
import streamlit as st
from config import get_api_key
from ui.components import inject_css, render_header
from auth import get_current_user, show_login_form, logout, get_display_name
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

    # 6. Logged-in user + sign-out
    current_user = get_current_user()
    if current_user:
        st.divider()
        display = get_display_name(current_user)
        st.markdown(f"**Signed in as:** {display}")
        if st.button("Sign out", key="signout", use_container_width=True):
            logout()

    # 7. Version + Changelog
    st.divider()
    with st.expander("📋 v2.14 — Changelog", expanded=False):
        st.markdown(
            "**v2.14** — Login persistence fixed: CookieController.refresh() called after rerun so JS cookie data is actually read on page refresh\\n\\n"
            "**v2.13** — PDF export emoji crash fixed (Latin-1 catch-all strips emoji from all fields · GO LIVE title cleaned)\\n\\n"
            "**v2.12** — Reasoning & tool-call display removed from all tabs (to be redesigned) · "
            "Onboarding: generate goes straight to plan history (no inline display) · "
            "History card now shows all plan details: KPIs, manager, promo dropdown with description, "
            "blockers, warnings, timeline, export buttons · "
            "Newest plan auto-expanded on generation · "
            "PDF rebuilt with explicit widths (fixes horizontal-space crash) · "
            "PDF now includes promo + description, full milestone descriptions, go-live banner · "
            "Promo dropdown is per-plan-entry with live description caption\n\n"
            "**v2.11** — Login now persists across page refresh (cookie hydration fix) · "
            "Agent reasoning always renders in right sidebar (onboarding + sales) · "
            "Onboarding timeline text visible on dark theme · "
            "PDF export unicode crash fixed (em-dash + smart quotes) · PDF button always visible in history · "
            "Export buttons reordered: PDF first, JSON second · "
            "Timeline: Photography >= Day 2, QA >= Day 3 · "
            "New Go Live +7 milestone card · 30-Day Review now at Go Live +30 · "
            "Tab font size increased\n\n"
            "**v2.10** — Fix Python 3.9 crash (str | None in dataclass) · Reasoning toggle now persists across reruns · "
            "Supabase errors surfaced in Onboarding tab · Area metric tooltip for long names · "
            "Agent Reasoning headers deferred until agent starts · Score badge text colour fixed for medium scores\n\n"
            "**v2.9** — Concurrent Quick & Batch generation (threading) · Login persists across refresh · "
            "Right-panel reasoning toggle in all tabs · Onboarding plans saved to Supabase · "
            "Collapsible leads table · Full email subject in history · Batch button inline with lead count · "
            "Timeline sorted by day + coloured cards · PDF export for onboarding plans · "
            "Promo description tooltip · Promo override selector\n\n"
            "**v2.8** — Filters locked during Quick Outreach generation · Supabase errors surfaced in UI\n\n"
            "**v2.7** — Realistic menu data for new partners · Blockers vs warnings split in onboarding\n\n"
            "**v2.6** — Restored sidebar toggle & GitHub icon\n\n"
            "**v2.5** — Transparent header (no Streamlit branding)\n\n"
            "**v2.2** — User login (alice/bob) · Supabase-persistent "
            "email history · per-user isolation\n\n"
            "**v2.1** — ⚡ Quick Outreach · 📬 Email history grouped "
            "by date · Gmail & Outlook launch buttons\n\n"
            "**v2.0** — Sortable leads table · Score tooltips (ℹ) · "
            "Full-width tabs · One-line header\n\n"
            "**v1.0** — Initial release: Sales · Onboarding · "
            "Retention agent tabs"
        )

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
render_header()

if not get_api_key():
    st.warning(
        "⚠️ No Anthropic API key found. "
        "Add it in the sidebar or set `ANTHROPIC_API_KEY` in your `.env` file to run the agents."
    )

# ---------------------------------------------------------------------------
# Login gate — show login form if not authenticated
# ---------------------------------------------------------------------------
if not get_current_user():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        show_login_form()
    st.stop()

# ---------------------------------------------------------------------------
# Tabs (only rendered when authenticated)
# ---------------------------------------------------------------------------
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
