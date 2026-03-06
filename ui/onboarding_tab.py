"""
Tab 2: Onboarding Agent UI.
"""
from __future__ import annotations
import json
from datetime import datetime, date, timedelta
from itertools import groupby

import streamlit as st
from fpdf import FPDF

from data.seed import get_partners, register_graduated_partner
from agents.onboarding_agent import run_onboarding_agent
from storage import (
    load_onboarding_plans,
    save_onboarding_plan,
    clear_onboarding_plans,
)
from ui.components import render_onboarding_timeline
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

def _safe_text(s: str) -> str:
    """Replace/strip characters unsupported by FPDF's built-in Latin-1 fonts."""
    s = (
        str(s)
        .replace("\u2014", "-")   # em dash —
        .replace("\u2013", "-")   # en dash –
        .replace("\u2019", "'")   # right single quotation mark '
        .replace("\u2018", "'")   # left single quotation mark '
        .replace("\u201c", '"')   # left double quotation mark "
        .replace("\u201d", '"')   # right double quotation mark "
        .replace("\u2022", "*")   # bullet •
        .replace("\u00a0", " ")   # non-breaking space
    )
    # Drop any remaining character outside the Latin-1 range (emoji, symbols, etc.)
    return s.encode("latin-1", errors="ignore").decode("latin-1")


def _build_pdf(plan: dict) -> bytes:
    """Generate a clean PDF summary of the onboarding plan."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Calculate usable page width explicitly to avoid cell(0,...) crashes
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin

    orange = (255, 96, 0)

    # ---- Header ----
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*orange)
    pdf.cell(usable_w, 10, "talabat Partner Onboarding Plan", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(usable_w, 6, _safe_text(plan.get("plan_title", "")), ln=True)
    pdf.ln(4)

    # ---- Key Metrics ----
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*orange)
    pdf.cell(usable_w, 7, "Key Metrics", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    label_w = 55
    val_w = usable_w - label_w
    metrics = [
        ("Go-Live Target",  f"Day {plan.get('go_live_target_days', 7)}"),
        ("Day-1 Orders",    str(plan.get("expected_day_1_orders", ""))),
        ("Day-7 Orders",    str(plan.get("expected_day_7_orders", ""))),
        ("30-Day GMV",      f"AED {plan.get('expected_30d_gmv_aed', 0):,.0f}"),
        ("Success Manager", plan.get("assigned_success_manager", "TBD")),
    ]
    for label, value in metrics:
        pdf.cell(label_w, 6, f"{label}:", border=0)
        pdf.cell(val_w, 6, _safe_text(value), ln=True)
    pdf.ln(2)

    # ---- Launch Promo ----
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*orange)
    pdf.cell(usable_w, 7, "Launch Promotion", ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(label_w, 6, "Promo:", border=0)
    pdf.cell(val_w, 6, _safe_text(plan.get("first_promo_recommendation", "TBD")), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    promo_desc = _safe_text(plan.get("promo_description", ""))
    if promo_desc:
        pdf.multi_cell(usable_w, 5, promo_desc)
    pdf.ln(2)

    # ---- Blockers ----
    blockers = plan.get("menu_blockers", [])
    if blockers:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(180, 0, 0)
        pdf.cell(usable_w, 7, "Menu Blockers (must resolve before go-live)", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        for b in blockers:
            pdf.multi_cell(usable_w, 6, _safe_text(f"  * {b}"))
        pdf.ln(2)

    # ---- Warnings ----
    warnings = plan.get("menu_warnings", [])
    if warnings:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(180, 120, 0)
        pdf.cell(usable_w, 7, "Additional Issues (not blocking)", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        for w in warnings:
            pdf.multi_cell(usable_w, 6, _safe_text(f"  * {w}"))
        pdf.ln(2)

    # ---- Onboarding Timeline ----
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*orange)
    pdf.cell(usable_w, 7, "Onboarding Timeline", ln=True)
    pdf.ln(1)

    milestones = sorted(plan.get("milestones", []), key=lambda m: m.get("day", 0))
    for m in milestones:
        is_golive = "GO LIVE" in m.get("title", "")

        if is_golive:
            # Orange banner for go-live
            pdf.set_fill_color(*orange)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 10)
            label = _safe_text(f"  Day {m['day']}  |  {m.get('title', '')}")
            pdf.cell(usable_w, 8, label, border=0, fill=True, ln=True)
            pdf.set_text_color(60, 60, 60)
            pdf.set_font("Helvetica", "", 9)
            if m.get("description"):
                pdf.multi_cell(usable_w, 5, _safe_text(f"  {m['description']}"))
        else:
            # Day header line
            owner = m.get("owner", "").upper()
            blocking_tag = "  |  BLOCKING" if m.get("blocking") else ""
            header = _safe_text(f"Day {m['day']}  |  {owner}{blocking_tag}")
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(130, 130, 130)
            pdf.cell(usable_w, 5, header, ln=True)
            # Title
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(usable_w, 5, _safe_text(m.get("title", "")), ln=True)
            # Description
            if m.get("description"):
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(usable_w, 4, _safe_text(m["description"]))

        pdf.ln(2)

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


# ---------------------------------------------------------------------------
# Partner graduation (cross-tab lifecycle bridge to Retention)
# ---------------------------------------------------------------------------

def _graduate_partner(partner_id: str, partner_name: str, partner_obj) -> None:
    """Mark a new partner as live, making them visible in the Retention tab.

    Adds the partner_id to _graduated_partner_ids in session state and
    registers the partner object in the seed runtime registry so the
    retention agent's get_all_partners() tool call can include them.
    Sets _lifecycle_banner to guide the user to the Retention tab.
    """
    graduated_ids = st.session_state.get("_graduated_partner_ids", set())
    if partner_id in graduated_ids:
        st.info(f"**{partner_name}** has already been marked as live.")
        return

    graduated_ids.add(partner_id)
    st.session_state._graduated_partner_ids = graduated_ids

    if partner_obj is not None:
        register_graduated_partner(partner_obj)

    st.session_state._lifecycle_banner = {
        "type": "graduation",
        "name": partner_name,
        "partner_id": partner_id,
        "lead_id": None,
    }
    st.rerun()


def _render_plan_history(user_id: str, newest_expanded: bool = False) -> None:
    """Render saved onboarding plans grouped by date.

    Args:
        newest_expanded: If True the first (most recent) plan is auto-expanded.
    """
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
    first_item = True  # track whether to auto-expand

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

            # Auto-expand the most recently generated plan
            should_expand = newest_expanded and first_item
            first_item = False

            with st.expander(
                f"📋 {ts} · {p.get('partner_name', '')} — {p.get('plan_title', '')}",
                expanded=should_expand,
            ):
                # 1. KPI metrics
                mc = st.columns(4)
                mc[0].metric("Go-Live Target", f"Day {p.get('go_live_target_days', 7)}")
                mc[1].metric("Day-1 Orders", p.get("expected_day_1_orders", "—"))
                mc[2].metric("Day-7 Orders", p.get("expected_day_7_orders", "—"))
                mc[3].metric("30-Day GMV", f"AED {p.get('expected_30d_gmv_aed', 0):,.0f}")

                # 2. Success manager
                st.info(f"👤 **Success Manager:** {p.get('assigned_success_manager', 'TBD')}")

                # 3. Launch promo dropdown (per-entry override, keyed by timestamp)
                promo_key = f"promo_hist_{key_ts}"
                saved_promo = p.get("first_promo_recommendation", list(PROMO_OPTIONS)[0])
                current_promo = st.session_state.get(promo_key, saved_promo)
                if current_promo not in PROMO_OPTIONS:
                    current_promo = list(PROMO_OPTIONS)[0]

                chosen_promo = st.selectbox(
                    "🎁 Launch Promo",
                    options=list(PROMO_OPTIONS.keys()),
                    index=list(PROMO_OPTIONS.keys()).index(current_promo),
                    key=promo_key,
                )
                st.caption(PROMO_OPTIONS[chosen_promo])

                # 4. Blockers
                blockers = p.get("menu_blockers", [])
                if blockers:
                    st.warning(
                        "**🔴 Menu Blockers — must resolve before go-live:**\n"
                        + "\n".join(f"- {b}" for b in blockers)
                    )

                # 5. Warnings
                warnings = p.get("menu_warnings", [])
                if warnings:
                    st.info(
                        "**⚠️ Additional Issues (not blocking, but important):**\n"
                        + "\n".join(f"- {w}" for w in warnings)
                    )

                # 6. Timeline + legend
                render_onboarding_timeline(p)
                st.markdown(
                    '<div style="font-size:0.8em;color:#666;margin-top:8px;">'
                    '🟠 talabat &nbsp;|&nbsp; 🔵 Restaurant &nbsp;|&nbsp;'
                    ' 🟣 Both &nbsp;|&nbsp; 🔴 BLOCKING = critical path milestone'
                    '</div>',
                    unsafe_allow_html=True,
                )

                # 7. Export buttons — build PDF with the chosen promo override
                st.divider()
                p_for_export = {
                    **p,
                    "first_promo_recommendation": chosen_promo,
                    "promo_description": PROMO_OPTIONS[chosen_promo],
                }
                dl1, dl2 = st.columns(2)
                try:
                    dl1.download_button(
                        label="⬇️ Export as PDF",
                        data=_build_pdf(p_for_export),
                        file_name=f"onboarding_plan_{p.get('partner_id', 'plan')}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{key_ts}",
                    )
                except Exception as e:
                    dl1.warning(f"PDF unavailable: {e}")
                dl2.download_button(
                    label="⬇️ Export as JSON",
                    data=json.dumps(p_for_export, indent=2, default=str),
                    file_name=f"onboarding_plan_{p.get('partner_id', 'plan')}.json",
                    mime="application/json",
                    key=f"dl_json_{key_ts}",
                )

                # 8. Mark as Live — persistent lifecycle button
                plan_partner_id = p.get("partner_id", "") or item.get("partner_id", "")
                graduated_ids = st.session_state.get("_graduated_partner_ids", set())
                if plan_partner_id and plan_partner_id not in graduated_ids:
                    st.markdown("---")
                    live_col, _ = st.columns([2, 3])
                    if live_col.button(
                        "🚀 Mark as Live → Retention",
                        key=f"go_live_hist_{key_ts}",
                        use_container_width=True,
                        type="primary",
                    ):
                        _graduate_partner(
                            plan_partner_id,
                            p.get("partner_name", plan_partner_id),
                            None,
                        )
                elif plan_partner_id in graduated_ids:
                    st.success("✅ Live in Retention portfolio")


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render():
    user_id = get_current_user()
    _ensure_plans_loaded(user_id)

    # Cross-tab lifecycle banner — show when a lead was just converted in Sales tab
    banner = st.session_state.get("_lifecycle_banner")
    if banner and banner.get("type") == "conversion":
        st.info(
            f"🔗 **{banner['name']}** was just converted from a lead and is ready to onboard. "
            "Select them from the dropdown below (look for the **[From Lead]** tag)."
        )
        st.session_state._lifecycle_banner = None

    if supabase_err := st.session_state.get("_supabase_error"):
        st.warning(f"⚠️ Supabase error (history may not persist): {supabase_err}")

    st.markdown(
        "### 📋 Onboarding Agent\n"
        "Generates a personalised milestone-based onboarding plan for a new restaurant partner, "
        "targeting first order within 7 days and 100 orders by day 30."
    )

    # Partner selector — merge static seed new partners with dynamically converted leads
    seed_new_partners = [p for p in get_partners() if p.status == "new"]
    converted_partners = st.session_state.get("_converted_partners", [])
    new_partners = seed_new_partners + converted_partners  # IDs never collide

    if not new_partners:
        st.warning("No new partners found in the dataset.")
        return

    def _partner_label(p) -> str:
        base = f"{p.name} ({p.cuisine_type}, {p.area})"
        return f"{base}  [From Lead]" if getattr(p, "source_lead_id", None) else base

    partner_options = {_partner_label(p): p.partner_id for p in new_partners}
    selected_label = st.selectbox("Select a new partner to onboard", options=list(partner_options.keys()))
    partner_id = partner_options[selected_label]

    # Preview selected partner metrics (search across merged list)
    selected_partner = next((p for p in new_partners if p.partner_id == partner_id), None)
    if selected_partner:
        cols = st.columns(4)
        cols[0].metric("Menu Items", selected_partner.active_menu_items)
        cols[1].metric("Cuisine", selected_partner.cuisine_type)
        cols[2].metric("Area", selected_partner.area, help=selected_partner.area)
        cols[3].metric("Current Orders/mo", selected_partner.monthly_orders)

    run_btn = st.button("📋 Generate Onboarding Plan", use_container_width=True, key="run_onboarding")

    if not run_btn:
        st.info("Select a partner above and click **Generate Onboarding Plan** to start.")
        _render_plan_history(user_id, newest_expanded=True)
        return

    # -----------------------------------------------------------------------
    # Agent execution — run silently, extract plan from tool results
    # -----------------------------------------------------------------------
    onboarding_plan: dict | None = None

    with st.spinner("Building onboarding plan…"):
        for event in run_onboarding_agent(partner_id=partner_id):
            if event.type == "tool_result":
                name = event.data.get("name", "")
                result = event.data.get("result", {})
                if (
                    name == "build_onboarding_plan"
                    and isinstance(result, dict)
                    and "milestones" in result
                ):
                    onboarding_plan = result
            elif event.type == "error":
                st.error(f"Agent error: {event.data}")
                _render_plan_history(user_id)
                return

    if onboarding_plan:
        _save_plan_to_cache(user_id, onboarding_plan)
        st.success("✅ Plan generated — expand the card below to view details and mark as live.")
    else:
        st.warning("Agent completed but no plan was produced.")

    # Always render history; newest_expanded=True so new plan is open
    _render_plan_history(user_id, newest_expanded=True)
