"""
Tab 2: Onboarding Agent UI.
"""
from __future__ import annotations
import json
from datetime import datetime, date, timedelta
from itertools import groupby

import streamlit as st
from fpdf import FPDF

from data.seed import get_partners
from agents.onboarding_agent import run_onboarding_agent
from storage import (
    load_onboarding_plans,
    save_onboarding_plan,
    clear_onboarding_plans,
)
from ui.components import (
    render_thinking_box,
    render_tool_call_card,
    render_onboarding_timeline,
)
from auth import get_current_user

# ---------------------------------------------------------------------------
# Available promo options (mirrors PROMO_TEMPLATES in onboarding_tools.py)
# ---------------------------------------------------------------------------
PROMO_OPTIONS: dict[str, str] = {
    "Free Delivery Week": (
        "7-day free delivery promo to drive first-order volume."
    ),
    "10% Off First 3 Orders": (
        "Discount on first 3 orders per customer — drives repeat behaviour."
    ),
    "Beat The Competition Bundle": (
        "Free delivery + 15% off for users who haven't ordered from this cuisine in 30 days."
    ),
    "Launch Visibility Boost": (
        "Featured placement in app for 14 days + free delivery for first 100 orders."
    ),
}


# ---------------------------------------------------------------------------
# PDF export helper
# ---------------------------------------------------------------------------

def _build_pdf(plan: dict) -> bytes:
    """Generate a clean PDF summary of the onboarding plan."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    orange = (255, 96, 0)

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*orange)
    pdf.cell(0, 10, "talabat Partner Onboarding Plan", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, plan.get("plan_title", ""), ln=True)
    pdf.ln(4)

    # Key metrics
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*orange)
    pdf.cell(0, 7, "Key Metrics", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    metrics = [
        ("Go-Live Target",  f"Day {plan.get('go_live_target_days', 7)}"),
        ("Day-1 Orders",    str(plan.get("expected_day_1_orders", ""))),
        ("Day-7 Orders",    str(plan.get("expected_day_7_orders", ""))),
        ("30-Day GMV",      f"AED {plan.get('expected_30d_gmv_aed', 0):,.0f}"),
        ("Success Manager", plan.get("assigned_success_manager", "TBD")),
        ("Launch Promo",    plan.get("first_promo_recommendation", "TBD")),
    ]
    for label, value in metrics:
        pdf.cell(60, 6, f"{label}:", border=0)
        pdf.cell(0, 6, value, ln=True)
    pdf.ln(4)

    # Blockers
    blockers = plan.get("menu_blockers", [])
    if blockers:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(180, 0, 0)
        pdf.cell(0, 7, "Menu Blockers (must resolve before go-live)", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        for b in blockers:
            pdf.multi_cell(0, 6, f"  \u2022 {b}")
        pdf.ln(2)

    # Warnings
    warnings = plan.get("menu_warnings", [])
    if warnings:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(180, 120, 0)
        pdf.cell(0, 7, "Additional Issues (not blocking)", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        for w in warnings:
            pdf.multi_cell(0, 6, f"  \u2022 {w}")
        pdf.ln(2)

    # Milestone table
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*orange)
    pdf.cell(0, 7, "Onboarding Milestones", ln=True)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(50, 50, 50)
    pdf.cell(15, 6, "Day",   border=1, fill=True)
    pdf.cell(30, 6, "Owner", border=1, fill=True)
    pdf.cell(15, 6, "Block", border=1, fill=True)
    pdf.cell(0,  6, "Milestone", border=1, fill=True, ln=True)

    milestones = sorted(plan.get("milestones", []), key=lambda m: m.get("day", 0))
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(40, 40, 40)
    pdf.set_fill_color(250, 250, 250)
    for m in milestones:
        blocking = "Yes" if m.get("blocking") else ""
        pdf.cell(15, 6, str(m.get("day", "")),                  border=1)
        pdf.cell(30, 6, m.get("owner", "").capitalize(),         border=1)
        pdf.cell(15, 6, blocking,                                border=1)
        pdf.cell(0,  6, m.get("title", "")[:70],                 border=1, ln=True)

    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# Onboarding plan history helpers
# ---------------------------------------------------------------------------

def _ensure_plans_loaded(user_id: str) -> None:
    if "onboarding_plan_cache" not in st.session_state:
        st.session_state.onboarding_plan_cache = load_onboarding_plans(user_id)


def _save_plan_to_cache(user_id: str, plan: dict) -> None:
    ts = datetime.now()
    entry = {"plan": plan, "partner_id": plan.get("partner_id", ""), "timestamp": ts}
    st.session_state.onboarding_plan_cache.insert(0, entry)
    save_onboarding_plan(user_id, plan.get("partner_id", ""), plan, ts)


def _render_plan_history(user_id: str) -> None:
    """Render saved onboarding plans grouped by date."""
    history = st.session_state.get("onboarding_plan_cache", [])
    if not history:
        return

    st.divider()
    hcol1, hcol2 = st.columns([6, 1])
    hcol1.markdown("### 📋 Plan History")
    if hcol2.button("🗑 Clear", key="clear_plans"):
        st.session_state.onboarding_plan_cache = []
        clear_onboarding_plans(user_id)
        st.rerun()

    today = date.today()
    for dt_date, group in groupby(history, key=lambda x: x["timestamp"].date()):
        if dt_date == today:
            label = "Today"
        elif dt_date == today - timedelta(days=1):
            label = "Yesterday"
        else:
            label = dt_date.strftime("%d %B %Y")
        st.markdown(f"**{label}**")
        for item in list(group):
            p = item["plan"]
            ts = item["timestamp"].strftime("%H:%M")
            key_ts = item["timestamp"].isoformat()
            with st.expander(
                f"📋 {ts} · {p.get('partner_name', '')} — {p.get('plan_title', '')}",
                expanded=False,
            ):
                mc = st.columns(4)
                mc[0].metric("Go-Live Target", f"Day {p.get('go_live_target_days', 7)}")
                mc[1].metric("Day-1 Orders", p.get("expected_day_1_orders", "—"))
                mc[2].metric("Day-7 Orders", p.get("expected_day_7_orders", "—"))
                mc[3].metric("30-Day GMV", f"AED {p.get('expected_30d_gmv_aed', 0):,.0f}")
                render_onboarding_timeline(p)
                dl1, dl2 = st.columns(2)
                dl1.download_button(
                    label="⬇️ Export as JSON",
                    data=json.dumps(p, indent=2, default=str),
                    file_name=f"onboarding_plan_{p.get('partner_id', 'plan')}.json",
                    mime="application/json",
                    key=f"dl_json_{key_ts}",
                )
                try:
                    dl2.download_button(
                        label="⬇️ Export as PDF",
                        data=_build_pdf(p),
                        file_name=f"onboarding_plan_{p.get('partner_id', 'plan')}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{key_ts}",
                    )
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render():
    user_id = get_current_user()
    _ensure_plans_loaded(user_id)

    # Bug 3 fix: surface Supabase errors in the onboarding tab
    if supabase_err := st.session_state.get("_supabase_error"):
        st.warning(f"⚠️ Supabase error (history may not persist): {supabase_err}")

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
        # Bug 5 fix: show full area name on hover instead of truncating
        cols[2].metric("Area", selected_partner.area, help=selected_partner.area)
        cols[3].metric("Current Orders/mo", selected_partner.monthly_orders)

    # Bug 2 fix: reasoning toggle lives outside the run_btn guard so it persists across reruns
    show_r = st.session_state.get("_show_reasoning", False)
    _, toggle_col = st.columns([5, 1])
    if toggle_col.button(
        "✕ Reasoning" if show_r else "🔍 Reasoning",
        key="toggle_r_onboarding",
        use_container_width=True,
    ):
        st.session_state["_show_reasoning"] = not show_r
        st.rerun()

    run_btn = st.button("📋 Generate Onboarding Plan", use_container_width=True, key="run_onboarding")

    if not run_btn:
        st.info("Select a partner above and click **Generate Onboarding Plan** to start.")
        _render_plan_history(user_id)
        return

    # -----------------------------------------------------------------------
    # Layout: split or full-width depending on reasoning panel state
    # -----------------------------------------------------------------------
    if show_r:
        col_main, col_panel = st.columns([3, 1])
    else:
        col_main = st.container()
        col_panel = None

    # -----------------------------------------------------------------------
    # Agent execution — reasoning renders in panel or inline
    # -----------------------------------------------------------------------
    reasoning_target = col_panel if col_panel else st.container()

    # Bug 6 fix: defer headers until the agent actually starts emitting events
    thinking_placeholder = None
    thinking_text = ""
    tool_area = None
    headers_rendered = False

    def _ensure_headers():
        nonlocal thinking_placeholder, tool_area, headers_rendered
        if headers_rendered:
            return
        headers_rendered = True
        with reasoning_target:
            if show_r:
                st.markdown("**🧠 Agent Reasoning**")
            else:
                st.divider()
                st.markdown("#### Agent Reasoning")
            thinking_placeholder = st.empty()
            if not show_r:
                st.markdown("#### Tool Calls")
            tool_area = st.container()

    pending_calls: dict[str, dict] = {}
    onboarding_plan: dict | None = None

    with st.spinner("Building onboarding plan…"):
        for event in run_onboarding_agent(partner_id=partner_id):
            if event.type == "thinking":
                _ensure_headers()
                thinking_text += event.data
                thinking_placeholder.markdown(
                    render_thinking_box(thinking_text),
                    unsafe_allow_html=True,
                )

            elif event.type == "tool_call":
                _ensure_headers()
                tid = event.data.get("tool_use_id", "")
                pending_calls[tid] = {
                    "name": event.data["name"],
                    "inputs": event.data["inputs"],
                }

            elif event.type == "tool_result":
                _ensure_headers()
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
    if not onboarding_plan:
        _render_plan_history(user_id)
        return

    # Persist the plan
    _save_plan_to_cache(user_id, onboarding_plan)

    with col_main:
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

        # Manager + promo override
        col1, col2 = st.columns(2)
        col1.info(f"👤 **Success Manager:** {onboarding_plan.get('assigned_success_manager', 'TBD')}")

        promo_key = f"promo_override_{partner_id}"
        current_promo = st.session_state.get(
            promo_key,
            onboarding_plan.get("first_promo_recommendation", list(PROMO_OPTIONS)[0]),
        )
        if current_promo not in PROMO_OPTIONS:
            current_promo = list(PROMO_OPTIONS)[0]

        chosen_promo = col2.selectbox(
            "🎁 Launch Promo:",
            options=list(PROMO_OPTIONS.keys()),
            index=list(PROMO_OPTIONS.keys()).index(current_promo),
            key=promo_key,
        )
        # Patch plan so exports reflect override
        onboarding_plan["first_promo_recommendation"] = chosen_promo
        onboarding_plan["promo_description"] = PROMO_OPTIONS[chosen_promo]

        # Promo description via popover ℹ
        with col2.popover("ℹ Description"):
            st.markdown(PROMO_OPTIONS[chosen_promo])

        # Blockers — hard stops
        blockers = onboarding_plan.get("menu_blockers", [])
        if blockers:
            st.warning(
                "**🔴 Menu Blockers — must resolve before go-live:**\n"
                + "\n".join(f"- {b}" for b in blockers)
            )

        # Warnings — important but not blocking
        warnings = onboarding_plan.get("menu_warnings", [])
        if warnings:
            st.info(
                "**⚠️ Additional Issues (not blocking, but important):**\n"
                + "\n".join(f"- {w}" for w in warnings)
            )

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

        # Export buttons
        st.divider()
        ex1, ex2 = st.columns(2)
        ex1.download_button(
            label="⬇️ Export Plan as JSON",
            data=json.dumps(onboarding_plan, indent=2, default=str),
            file_name=f"onboarding_plan_{partner_id}.json",
            mime="application/json",
        )
        try:
            ex2.download_button(
                label="⬇️ Export Plan as PDF",
                data=_build_pdf(onboarding_plan),
                file_name=f"onboarding_plan_{partner_id}.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            ex2.warning(f"PDF export unavailable: {e}")

    _render_plan_history(user_id)
