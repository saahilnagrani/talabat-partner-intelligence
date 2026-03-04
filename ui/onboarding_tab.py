"""
Tab 2: Onboarding Agent UI.
"""
from __future__ import annotations
import streamlit as st
from data.seed import get_partners
from agents.onboarding_agent import run_onboarding_agent
from ui.components import (
    render_thinking_box,
    render_tool_call_card,
    render_onboarding_timeline,
)


def render():
    st.markdown(
        "### 📋 Onboarding Agent\n"
        "Generates a personalised milestone-based onboarding plan for a new restaurant partner, "
        "targeting first order within 7 days and 100 orders by day 30."
    )

    # Get new partners for the selector
    all_partners = get_partners()
    new_partners = [p for p in all_partners if p.status == "new"]

    if not new_partners:
        st.warning("No new partners found in the dataset.")
        return

    partner_options = {f"{p.name} ({p.cuisine_type}, {p.area})": p.partner_id for p in new_partners}
    selected_label = st.selectbox("Select a new partner to onboard", options=list(partner_options.keys()))
    partner_id = partner_options[selected_label]

    # Preview selected partner
    selected_partner = next((p for p in new_partners if p.partner_id == partner_id), None)
    if selected_partner:
        cols = st.columns(4)
        cols[0].metric("Menu Items", selected_partner.active_menu_items)
        cols[1].metric("Cuisine", selected_partner.cuisine_type)
        cols[2].metric("Area", selected_partner.area)
        cols[3].metric("Current Orders/mo", selected_partner.monthly_orders)

    run_btn = st.button("📋 Generate Onboarding Plan", use_container_width=True, key="run_onboarding")

    if not run_btn:
        st.info("Select a partner above and click **Generate Onboarding Plan** to start.")
        return

    # -----------------------------------------------------------------------
    # Agent execution
    # -----------------------------------------------------------------------
    st.divider()
    st.markdown("#### Agent Reasoning")
    thinking_placeholder = st.empty()
    thinking_text = ""

    st.markdown("#### Tool Calls")
    tool_area = st.container()

    pending_calls: dict[str, dict] = {}
    onboarding_plan: dict | None = None

    with st.spinner("Building onboarding plan…"):
        for event in run_onboarding_agent(partner_id=partner_id):
            if event.type == "thinking":
                thinking_text += event.data
                thinking_placeholder.markdown(
                    render_thinking_box(thinking_text),
                    unsafe_allow_html=True,
                )

            elif event.type == "tool_call":
                tid = event.data.get("tool_use_id", "")
                pending_calls[tid] = {
                    "name": event.data["name"],
                    "inputs": event.data["inputs"],
                }

            elif event.type == "tool_result":
                tid = event.data.get("tool_use_id", "")
                result = event.data.get("result", {})
                name = event.data["name"]

                call_info = pending_calls.pop(tid, {"name": name, "inputs": {}})
                with tool_area:
                    render_tool_call_card(call_info["name"], call_info["inputs"], result)

                if name == "build_onboarding_plan" and isinstance(result, dict) and "milestones" in result:
                    onboarding_plan = result

            elif event.type == "complete":
                st.success("✅ Onboarding plan ready!")

            elif event.type == "error":
                st.error(f"Agent error: {event.data}")
                return

    # -----------------------------------------------------------------------
    # Results
    # -----------------------------------------------------------------------
    if onboarding_plan:
        st.divider()
        st.markdown(f"### {onboarding_plan.get('plan_title', 'Onboarding Plan')}")

        # Metrics row
        mc = st.columns(4)
        mc[0].metric("Go-Live Target", f"Day {onboarding_plan.get('go_live_target_days', 7)}")
        mc[1].metric("Day-1 Orders", onboarding_plan.get("expected_day_1_orders", "—"))
        mc[2].metric("Day-7 Orders", onboarding_plan.get("expected_day_7_orders", "—"))
        mc[3].metric(
            "30-Day GMV",
            f"AED {onboarding_plan.get('expected_30d_gmv_aed', 0):,.0f}",
        )

        # Manager + promo
        col1, col2 = st.columns(2)
        col1.info(f"👤 **Success Manager:** {onboarding_plan.get('assigned_success_manager', 'TBD')}")
        col2.success(f"🎁 **Launch Promo:** {onboarding_plan.get('first_promo_recommendation', 'TBD')}")

        # Blockers — hard stops
        blockers = onboarding_plan.get("menu_blockers", [])
        if blockers:
            st.warning("**🔴 Menu Blockers — must resolve before go-live:**\n" + "\n".join(f"- {b}" for b in blockers))

        # Warnings — important but not blocking
        warnings = onboarding_plan.get("menu_warnings", [])
        if warnings:
            st.info("**⚠️ Additional Issues (not blocking, but important):**\n" + "\n".join(f"- {w}" for w in warnings))

        # Timeline
        st.divider()
        render_onboarding_timeline(onboarding_plan)

        # Legend
        st.markdown(
            '<div style="font-size:0.8em;color:#666;margin-top:8px;">'
            '🟠 talabat &nbsp;|&nbsp; 🔵 Restaurant &nbsp;|&nbsp; 🟣 Both &nbsp;|&nbsp; 🔴 BLOCKING = critical path milestone'
            '</div>',
            unsafe_allow_html=True,
        )

        # Export
        import json
        st.download_button(
            label="⬇️ Export Plan as JSON",
            data=json.dumps(onboarding_plan, indent=2, default=str),
            file_name=f"onboarding_plan_{partner_id}.json",
            mime="application/json",
        )
