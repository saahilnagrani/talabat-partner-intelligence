"""
Tab 3: Retention Agent UI.
"""
import streamlit as st
import pandas as pd
from data.seed import get_partners
from tools.retention_tools import calculate_health_score
from agents.retention_agent import run_retention_agent
from ui.components import (
    render_retention_action_card,
    render_risk_badge,
)


def _get_all_active_partners():
    """Return the full list of active partners — seed + graduated converted partners."""
    seed_active = [p for p in get_partners() if p.status != "new"]
    graduated_ids = st.session_state.get("_graduated_partner_ids", set())
    graduated = [
        p for p in st.session_state.get("_converted_partners", [])
        if p.partner_id in graduated_ids
    ]
    return seed_active + graduated, graduated_ids


def _get_partner_summary_df():
    """Build a quick health-score summary table for the portfolio overview.

    Merges static seed partners (non-new) with any partners graduated from
    the Onboarding tab this session.
    """
    all_active, graduated_ids = _get_all_active_partners()
    rows = []
    for p in all_active:
        h = calculate_health_score(p.partner_id)
        is_recently_onboarded = p.partner_id in graduated_ids
        rows.append({
            "Partner": f"{p.name} 🆕" if is_recently_onboarded else p.name,
            "Area": p.area,
            "Cuisine": p.cuisine_type,
            "Health Score": h.get("health_score", 0),
            "Risk": h.get("risk_level", "healthy"),
            "Orders Trend": f"{p.orders_trend_pct:+.1f}%",
            "Completion Rate": f"{p.completion_rate:.1f}%",
            "GMV/mo (AED)": f"{p.gmv_aed_last_30d:,.0f}",
            "partner_id": p.partner_id,
        })
    return pd.DataFrame(rows)


def render():
    # Cross-tab lifecycle banner — shown after a partner is marked as live in Onboarding tab
    banner = st.session_state.get("_lifecycle_banner")
    if banner and banner.get("type") == "graduation":
        st.success(
            f"🚀 **{banner['name']}** has completed onboarding and is now live in the portfolio! "
            "They appear below with a 🆕 tag."
        )
        st.session_state._lifecycle_banner = None

    st.markdown(
        "### 🛡️ Retention Agent\n"
        "Analyses the partner portfolio using a 5-signal health score, identifies at-risk restaurants, "
        "determines root causes, and generates specific intervention plans."
    )

    # Portfolio overview (always shown)
    with st.expander("📊 Portfolio Health Overview", expanded=True):
        df = _get_partner_summary_df()
        total = len(df)
        critical_count = (df["Risk"] == "critical").sum()
        at_risk_count = (df["Risk"].isin(["at_risk", "high", "medium"])).sum()

        # GMV at risk from declining partners — include graduated partners in the pool
        all_active, graduated_ids = _get_all_active_partners()
        at_risk_partners = [p for p in all_active if p.status in ("at_risk", "critical")]
        total_gmv_at_risk = sum(p.gmv_aed_last_30d for p in at_risk_partners)

        mc = st.columns(4)
        mc[0].metric("Total Active Partners", total)
        mc[1].metric("Critical Risk", critical_count, delta=f"-{critical_count} urgent", delta_color="inverse")
        mc[2].metric("At Risk", at_risk_count, delta=f"-{at_risk_count} need attention", delta_color="inverse")
        mc[3].metric("GMV at Risk/mo", f"AED {total_gmv_at_risk:,.0f}")

        # Color-coded table
        def risk_color(val):
            colors = {
                "critical": "background-color: #f8d7da; color: #721c24;",
                "high": "background-color: #fde8d8; color: #7d3a00;",
                "medium": "background-color: #fff3cd; color: #664d03;",
                "healthy": "background-color: #d1edda; color: #155724;",
            }
            return colors.get(val, "")

        display_df = df.drop(columns=["partner_id"])
        styled = display_df.style.applymap(risk_color, subset=["Risk"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    st.divider()

    # Controls
    col1, col2 = st.columns(2)
    with col1:
        risk_filter = st.selectbox(
            "Focus on",
            options=["at_risk", "critical", "all"],
            format_func=lambda x: {
                "at_risk": "At-Risk & Critical partners",
                "critical": "Critical partners only",
                "all": "All partners",
            }[x],
        )
    with col2:
        max_partners = st.slider("Max partners to analyse in depth", min_value=1, max_value=10, value=5)

    run_btn = st.button("🛡️ Run Retention Agent", use_container_width=True, key="run_retention")

    if not run_btn:
        st.info("Select a filter above and click **Run Retention Agent** to analyse at-risk partners.")
        return

    # -----------------------------------------------------------------------
    # Agent execution — run silently, extract results from tool_result events
    # -----------------------------------------------------------------------
    retention_actions: list[dict] = []
    revenue_at_risk: dict[str, dict] = {}

    with st.spinner(f"Analysing {'at-risk' if risk_filter != 'all' else 'all'} partners…"):
        for event in run_retention_agent(risk_filter=risk_filter, max_partners=max_partners):
            if event.type == "tool_result":
                result = event.data.get("result", {})
                name = event.data.get("name", "")

                if name == "generate_retention_actions" and isinstance(result, dict) and "recommended_actions" in result:
                    retention_actions.append(result)

                if name == "calculate_revenue_at_risk" and isinstance(result, dict) and "partner_id" in result:
                    revenue_at_risk[result["partner_id"]] = result

            elif event.type == "complete":
                st.success("✅ Retention analysis complete!")

            elif event.type == "error":
                st.error(f"Agent error: {event.data}")
                return

    # -----------------------------------------------------------------------
    # Results
    # -----------------------------------------------------------------------
    if retention_actions:
        st.divider()

        # Summary metrics
        total_rev_at_risk = sum(
            revenue_at_risk.get(a.get("partner_id", ""), {}).get("monthly_gmv_aed", 0)
            for a in retention_actions
        )
        total_commission = total_rev_at_risk * 0.17

        st.markdown(f"#### Retention Plans — {len(retention_actions)} Partners Analysed")

        sc = st.columns(3)
        sc[0].metric("Partners Analysed", len(retention_actions))
        sc[1].metric("Total GMV at Risk/mo", f"AED {total_rev_at_risk:,.0f}")
        sc[2].metric("Talabat Revenue at Risk/mo", f"AED {total_commission:,.0f}")

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_actions = sorted(
            retention_actions,
            key=lambda x: priority_order.get(x.get("priority", "low"), 3),
        )

        st.divider()
        for action in sorted_actions:
            pid = action.get("partner_id", "")
            rev_data = revenue_at_risk.get(pid)
            with st.container():
                render_retention_action_card(action, rev_data)
                st.divider()
    else:
        st.info("The agent completed but no specific retention actions were collected. Try selecting 'Critical partners only'.")
