"""
Tab 1: Sales Acquisition Agent UI.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import threading
import time
import uuid
from dataclasses import dataclass, field as dc_field
from datetime import datetime, date, timedelta
from itertools import groupby
from data.seed import MARKET_BENCHMARKS, get_leads, get_lead_by_id, register_runtime_partner, mark_lead_converted, add_batch_leads
from data.models import RestaurantPartner
from data.platform_data import PLATFORM_RESTAURANTS, AREA_COORDS, get_competition_count
from agents.sales_agent import run_sales_agent, run_sales_agent_for_lead
from tools.sales_tools import score_lead
import plotly.express as px
from ui.components import (
    render_email_card,
    render_score_badge,
)
from auth import get_current_user
from storage import load_history, save_email, clear_history

ALL_AREAS = list(MARKET_BENCHMARKS.keys())
ALL_CUISINES = [
    "Lebanese", "Indian", "Pakistani", "Italian", "American",
    "Japanese", "Korean", "Filipino", "Thai", "Vietnamese",
    "Mexican", "Persian", "Emirati", "Chinese",
]


# ---------------------------------------------------------------------------
# Module-level concurrent generation task store (shared across reruns)
# ---------------------------------------------------------------------------

@dataclass
class _GenTask:
    task_id: str
    label: str        # e.g. "⚡ Nando's" or "🚀 Batch (JLT, Indian, min 50)"
    user_id: str
    kind: str         # "quick" | "batch"
    status: str = "running"          # "running" | "done" | "error"
    events: list = dc_field(default_factory=list)
    emails: list = dc_field(default_factory=list)
    scores: list = dc_field(default_factory=list)
    error: str | None = None


_TASKS: dict[str, _GenTask] = {}
_TASKS_LOCK = threading.Lock()


def _generation_worker(task_id: str, generator) -> None:
    """Background thread: run agent generator, accumulate events thread-safely."""
    try:
        for event in generator:
            with _TASKS_LOCK:
                _TASKS[task_id].events.append(event)
                if event.type == "tool_result":
                    res  = event.data.get("result", {})
                    name = event.data.get("name", "")
                    if name == "write_outreach_email" and isinstance(res, dict) and "body" in res:
                        _TASKS[task_id].emails.append(res)
                    if name == "score_lead" and isinstance(res, dict) and "score" in res:
                        _TASKS[task_id].scores.append(res)
        with _TASKS_LOCK:
            _TASKS[task_id].status = "done"
    except Exception as e:
        with _TASKS_LOCK:
            _TASKS[task_id].status = "error"
            _TASKS[task_id].error = str(e)


# ---------------------------------------------------------------------------
# Supabase-backed history helpers
# ---------------------------------------------------------------------------

def _ensure_history_loaded(user_id: str) -> None:
    if "email_history_cache" not in st.session_state:
        st.session_state.email_history_cache = load_history(user_id)


def _append_email(user_id: str, email: dict, source: str) -> None:
    ts = datetime.now()
    entry = {"email": email, "timestamp": ts, "source": source}
    st.session_state.email_history_cache.insert(0, entry)
    save_email(user_id, email, source, ts)


def _clear_history(user_id: str) -> None:
    st.session_state.email_history_cache = []
    clear_history(user_id)


# ---------------------------------------------------------------------------
# Lead → Partner conversion (cross-tab lifecycle bridge)
# ---------------------------------------------------------------------------

def _convert_lead_to_partner(lead_id: str) -> None:
    """Convert a RestaurantLead into a RestaurantPartner (status='new').

    Creates the partner in session state and registers it in the seed runtime
    registry so onboarding agent tool calls can resolve it by partner_id.
    Sets _lifecycle_banner to guide the user to the Onboarding tab.
    """
    lead = get_lead_by_id(lead_id)
    if lead is None:
        st.error(f"Lead {lead_id} not found.")
        return

    # Guard: prevent duplicate conversions
    already_converted = {
        p.source_lead_id
        for p in st.session_state.get("_converted_partners", [])
    }
    if lead_id in already_converted:
        st.warning(f"**{lead.name}** has already been converted to a partner.")
        return

    partner_id = f"converted_{lead_id}"
    new_partner = RestaurantPartner(
        partner_id=partner_id,
        name=lead.name,
        cuisine_type=lead.cuisine_type,
        area=lead.area,
        joined_date=datetime.now(),
        monthly_orders=0,
        avg_ticket_aed=lead.avg_ticket_aed,
        completion_rate=100.0,
        rating=lead.google_rating,
        active_menu_items=0,
        last_promo_date=None,
        account_manager="TBD",
        orders_trend_pct=0.0,
        days_since_login=0,
        support_tickets_open=0,
        gmv_aed_last_30d=0.0,
        status="new",
        source_lead_id=lead_id,
        recently_onboarded=False,
    )

    st.session_state._converted_partners.append(new_partner)
    register_runtime_partner(new_partner)

    st.session_state._lifecycle_banner = {
        "type": "conversion",
        "name": lead.name,
        "partner_id": partner_id,
        "lead_id": lead_id,
    }
    mark_lead_converted(lead_id)
    st.rerun()


# ---------------------------------------------------------------------------
# Leads table
# ---------------------------------------------------------------------------

def _render_leads_table(scored_leads: list[dict]) -> str:
    """Render leads as a sortable HTML table with per-row score popup."""
    NUMERIC = [3, 4, 5, 6, 8]

    rows = ""
    for item in scored_leads:
        l = item["lead"]
        s = item["score"]
        bd = s["breakdown"]
        score_val = s["score"]

        score_color = (
            "#28a745" if score_val >= 75 else
            "#FF6000" if score_val >= 50 else
            "#6c757d"
        )
        breakdown_html = (
            f'<div class="tt-row"><span>Orders</span><span>{bd["order_volume_potential"]:.1f} / 25</span></div>'
            f'<div class="tt-row"><span>Ticket size</span><span>{bd["ticket_size_quality"]:.1f} / 20</span></div>'
            f'<div class="tt-row"><span>Brand rating</span><span>{bd["brand_quality_rating"]:.1f} / 20</span></div>'
            f'<div class="tt-row"><span>Delivery gap</span><span>{bd["delivery_gap_opportunity"]:.0f} / 15</span></div>'
            f'<div class="tt-row"><span>Platform gap</span><span>{bd["platform_exclusivity"]:.0f} / 10</span></div>'
            f'<div class="tt-row"><span>Competition</span><span>{bd.get("competition_density", 0):.0f} / 10</span></div>'
            f'<hr class="tt-div"/>'
            f'<div class="tt-total"><span>Total</span><span>{score_val:.0f} / 100</span></div>'
        )
        platform = l.current_platform or "—"

        rows += f"""
        <tr>
          <td>{l.name}</td>
          <td>{l.area}</td>
          <td>{l.cuisine_type}</td>
          <td style="text-align:right" data-sort="{l.estimated_monthly_orders}">{l.estimated_monthly_orders:,}</td>
          <td style="text-align:right" data-sort="{l.avg_ticket_aed}">AED {l.avg_ticket_aed:.0f}</td>
          <td style="text-align:right" data-sort="{l.google_rating}">{l.google_rating} ⭐</td>
          <td style="text-align:right" data-sort="{l.num_reviews}">{l.num_reviews:,}</td>
          <td>{platform}</td>
          <td style="text-align:center;white-space:nowrap" data-sort="{score_val:.1f}">
            <span style="font-weight:700;color:{score_color}">{score_val:.0f}</span>
            <span class="info-btn" onclick="toggleTip(this)">ℹ</span>
            <div class="score-tip">{breakdown_html}</div>
          </td>
        </tr>"""

    headers = [
        ("Restaurant", "text-align:left"),
        ("Area", "text-align:left"),
        ("Cuisine", "text-align:left"),
        ("Est. Orders/mo", "text-align:right"),
        ("Avg Ticket", "text-align:right"),
        ("Rating", "text-align:right"),
        ("Reviews", "text-align:right"),
        ("Platform", "text-align:left"),
        ("Score /100", "text-align:center"),
    ]
    header_cells = "".join(
        f'<th style="{sty}" onclick="sortCol({i})">{label}'
        f'<span class="sort-icon" id="si-{i}"></span></th>'
        for i, (label, sty) in enumerate(headers)
    )

    return f"""
    <style>
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", sans-serif;
        margin: 0;
      }}
      .leads-tbl {{
        width:100%; border-collapse:collapse;
        font-size:0.9em; color:#e0e0e0;
        font-family: inherit;
      }}
      .leads-tbl th {{
        background:#2a2a2a; color:#aaa; font-weight:600;
        padding:8px 12px; text-align:left;
        border-bottom:1px solid #444; white-space:nowrap;
        cursor:pointer; user-select:none;
      }}
      .leads-tbl th:hover {{ color:#FF6000; }}
      .sort-icon {{ color:#FF6000; font-size:0.8em; margin-left:3px; }}
      .leads-tbl td {{
        padding:7px 12px; border-bottom:1px solid #2a2a2a;
        vertical-align:middle; position:relative;
      }}
      .leads-tbl tr:hover td {{ background:#1e1e1e; }}
      .info-btn {{
        cursor:pointer; color:#888; font-size:0.85em;
        padding:1px 4px; border-radius:3px; margin-left:2px;
      }}
      .info-btn:hover {{ color:#FF6000; }}
      .score-tip {{
        display:none; position:absolute; right:0; top:calc(100% + 2px);
        background:#2a2a2a; border:1px solid #555; border-radius:8px;
        padding:10px 14px; z-index:9999; min-width:190px;
        box-shadow:0 6px 20px rgba(0,0,0,0.7); font-size:0.88em;
      }}
      .score-tip.open {{ display:block; }}
      .score-tip.above {{ top:auto; bottom:calc(100% + 2px); }}
      .tt-row {{
        display:flex; justify-content:space-between; gap:20px;
        padding:3px 0; color:#bbb;
      }}
      .tt-row span:last-child {{ font-weight:600; color:#e0e0e0; }}
      .tt-div {{ border:none; border-top:1px solid #444; margin:6px 0; }}
      .tt-total {{
        display:flex; justify-content:space-between; gap:20px;
        padding:3px 0; font-weight:700; color:#FF6000;
      }}
    </style>

    <table id="leads-tbl" class="leads-tbl">
      <thead><tr>{header_cells}</tr></thead>
      <tbody>{rows}</tbody>
    </table>

    <script>
      var _sortDir = {{}};
      function sortCol(idx) {{
        var tbl = document.getElementById('leads-tbl');
        var tbody = tbl.tBodies[0];
        var rows = Array.from(tbody.rows);
        var numeric = {NUMERIC};
        _sortDir[idx] = (_sortDir[idx] === 'asc') ? 'desc' : 'asc';
        var asc = _sortDir[idx] === 'asc';
        document.querySelectorAll('.sort-icon').forEach(function(e) {{ e.textContent = ''; }});
        document.getElementById('si-' + idx).textContent = asc ? ' ▲' : ' ▼';
        rows.sort(function(a, b) {{
          var av = a.cells[idx].dataset.sort !== undefined
            ? a.cells[idx].dataset.sort
            : a.cells[idx].textContent.trim();
          var bv = b.cells[idx].dataset.sort !== undefined
            ? b.cells[idx].dataset.sort
            : b.cells[idx].textContent.trim();
          if (numeric.indexOf(idx) !== -1) {{ return asc ? +av - +bv : +bv - +av; }}
          return asc ? av.localeCompare(bv) : bv.localeCompare(av);
        }});
        rows.forEach(function(r) {{ tbody.appendChild(r); }});
      }}
      function toggleTip(btn) {{
        var tip = btn.nextElementSibling;
        var wasOpen = tip.classList.contains('open');
        document.querySelectorAll('.score-tip.open').forEach(function(e) {{
          e.classList.remove('open');
          e.classList.remove('above');
        }});
        if (!wasOpen) {{
          tip.classList.add('open');
          var rect = tip.getBoundingClientRect();
          var vh = window.innerHeight || document.documentElement.clientHeight;
          if (rect.bottom > vh) {{
            tip.classList.add('above');
          }}
          setTimeout(function() {{
            document.addEventListener('click', function close(e) {{
              if (!tip.contains(e.target) && e.target !== btn) {{
                tip.classList.remove('open');
                tip.classList.remove('above');
                document.removeEventListener('click', close);
              }}
            }});
          }}, 0);
        }}
      }}
    </script>"""


# ---------------------------------------------------------------------------
# Active task renderer (polling-based, works in right panel or inline)
# ---------------------------------------------------------------------------

def _render_active_tasks(user_id: str) -> None:
    """Poll in-progress generation tasks; save emails on completion.

    Shows a minimal status indicator while running. Thinking and tool-call
    details are intentionally omitted (to be redesigned later).
    """
    active_ids = st.session_state.get("_active_task_ids", [])
    if not active_ids:
        return

    still_running_ids: list[str] = []

    for task_id in active_ids:
        with _TASKS_LOCK:
            task = _TASKS.get(task_id)
            if task is None:
                continue
            snap_emails  = list(task.emails)
            snap_scores  = list(task.scores)
            snap_status  = task.status
            snap_error   = task.error
            snap_label   = task.label
            snap_uid     = task.user_id
            snap_kind    = task.kind

        icon = "⏳" if snap_status == "running" else ("✅" if snap_status == "done" else "❌")
        with st.expander(f"{icon} {snap_label}", expanded=(snap_status == "running")):
            if snap_status == "running":
                st.caption("Generating… emails will appear in history when complete.")
            elif snap_status == "error":
                st.error(f"Generation failed: {snap_error}")

            # Batch lead-score table (shown once done)
            if snap_scores and snap_status == "done":
                df = pd.DataFrame([
                    {
                        "Restaurant": s.get("restaurant_name", s.get("lead_id", "")),
                        "Score": s.get("score", 0),
                        "GMV/mo (AED)": f"AED {s.get('estimated_monthly_gmv_aed', 0):,.0f}",
                    }
                    for s in sorted(snap_scores, key=lambda x: x.get("score", 0), reverse=True)
                ])
                st.markdown("**Lead Scores**")
                st.dataframe(df, use_container_width=True, hide_index=True)

        # Handle completion / cleanup
        if snap_status == "done":
            for email in snap_emails:
                _append_email(snap_uid, email, snap_kind)
            with _TASKS_LOCK:
                _TASKS.pop(task_id, None)
        elif snap_status == "error":
            with _TASKS_LOCK:
                _TASKS.pop(task_id, None)
        else:
            still_running_ids.append(task_id)

    st.session_state["_active_task_ids"] = still_running_ids

    if still_running_ids:
        time.sleep(1.5)
        st.rerun()


# ---------------------------------------------------------------------------
# History rendering
# ---------------------------------------------------------------------------

def _render_history(user_id: str):
    """Render the persisted outreach email history grouped by date."""
    history = st.session_state.get("email_history_cache", [])
    if not history:
        return

    st.divider()
    hcol1, hcol2 = st.columns([6, 1])
    hcol1.markdown("### 📬 Outreach History")
    if hcol2.button("🗑 Clear", key="clear_history"):
        _clear_history(user_id)
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
            e = item["email"]
            src = item["source"]
            badge = "⚡ Quick" if src == "quick" else "🤖 Batch"
            ts = item["timestamp"].strftime("%H:%M")
            key_suffix = f"_{item['timestamp'].isoformat()}"
            with st.expander(
                f"{badge} · {ts} · {e.get('restaurant_name', '')} — {e.get('subject', '')}",
                expanded=False,
            ):
                render_email_card(e, key_suffix=key_suffix)


# ---------------------------------------------------------------------------
# Coverage grid computation (cached)
# ---------------------------------------------------------------------------

# Flat-Earth constants for Dubai (~25°N)
_LAT_KM = 111.0                                          # km per degree latitude
_LON_KM = 40075.0 * np.cos(np.radians(25.15)) / 360.0  # ≈ 100.9 km per degree longitude


@st.cache_data(show_spinner=False)
def _compute_coverage_grid(
    radius_km: float,
    cuisine_filter: tuple,
    grid_n: int = 70,
) -> pd.DataFrame:
    """Return a DataFrame of {lat, lon, count} for the coverage choropleth.

    For each grid cell over Dubai, count = number of platform restaurants whose
    location is within *radius_km* of that cell.  Uses a flat-Earth Euclidean
    approximation (< 0.1% error for distances < 50 km in Dubai).

    Results are cached by (radius_km, cuisine_filter) so repeated slider
    interactions at the same radius are instant.
    """
    restaurants = [
        r for r in PLATFORM_RESTAURANTS
        if (not cuisine_filter or r["cuisine_type"] in cuisine_filter)
    ]
    if not restaurants:
        return pd.DataFrame(columns=["lat", "lon", "count"])

    r_lats = np.array([r["lat"] for r in restaurants], dtype=np.float32)
    r_lons = np.array([r["lon"] for r in restaurants], dtype=np.float32)

    # Regular grid covering the Dubai metro area
    g_lats = np.linspace(24.95, 25.35, grid_n, dtype=np.float32)
    g_lons = np.linspace(55.05, 55.45, grid_n, dtype=np.float32)
    gla, glo = np.meshgrid(g_lats, g_lons)
    gla = gla.ravel()   # shape (grid_n², )
    glo = glo.ravel()

    # Vectorized distance: (N_grid, N_restaurants) — in-place to minimise peak RAM
    dlat_km = (gla[:, None] - r_lats[None, :]) * _LAT_KM   # (N, M) float32
    dlon_km = (glo[:, None] - r_lons[None, :]) * _LON_KM
    dlat_km **= 2
    dlon_km **= 2
    dlat_km += dlon_km                                       # reuse array: dist² (N, M)
    within = dlat_km <= (radius_km ** 2)                     # bool (N, M)
    counts = within.sum(axis=1).astype(np.int16)             # (N,)

    df = pd.DataFrame({"lat": gla, "lon": glo, "count": counts})
    return df[df["count"] > 0].reset_index(drop=True)       # drop empty cells


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render():
    user_id = get_current_user()
    _ensure_history_loaded(user_id)

    # Cross-tab lifecycle banner — shown after a lead is converted
    banner = st.session_state.get("_lifecycle_banner")
    if banner and banner.get("type") == "conversion":
        st.success(
            f"✅ **{banner['name']}** has been converted to a new partner. "
            "Switch to the **📋 Partner Onboarding** tab to generate their onboarding plan."
        )
        st.session_state._lifecycle_banner = None

    # Surface any Supabase errors
    supabase_err = st.session_state.get("_supabase_error")
    if supabase_err:
        st.warning(f"⚠️ **Supabase error** (history may not persist): `{supabase_err}`")

    st.markdown(
        "### 🎯 Sales Acquisition Agent\n"
        "Scores restaurant leads, selects top prospects, and writes personalised outreach emails. "
        "Watch the agent reason through each lead in real time."
    )

    # -------------------------------------------------------------------
    # Mark as Converted — lifecycle bridge (TOP of page, before filters)
    # -------------------------------------------------------------------
    all_leads_top = get_leads()
    if all_leads_top:
        lead_names_top = {l.name: l.lead_id for l in all_leads_top}
        st.markdown("**✅ Mark as Converted** — move a signed lead into the onboarding queue")
        tc1, tc2 = st.columns([4, 1])
        with tc1:
            top_chosen = st.selectbox(
                "Lead to convert:",
                options=list(lead_names_top.keys()),
                key="conv_lead_select",
                label_visibility="collapsed",
            )
        with tc2:
            top_conv_btn = st.button(
                "Convert →",
                key="conv_btn",
                use_container_width=True,
                type="secondary",
            )
        converted_lead_ids = {
            p.source_lead_id
            for p in st.session_state.get("_converted_partners", [])
        }
        already_names = [l.name for l in all_leads_top if l.lead_id in converted_lead_ids]
        if already_names:
            st.caption(f"Already converted: {', '.join(already_names)}")

        # Lead summary card — shown for the selected lead
        selected_lead = next((l for l in all_leads_top if l.name == top_chosen), None)
        if selected_lead:
            comp_count = get_competition_count(selected_lead.area, selected_lead.cuisine_type)
            if comp_count == 0 and not selected_lead.has_delivery:
                angle = f"First mover in {selected_lead.area} with zero delivery presence — high urgency pitch"
            elif comp_count == 0:
                angle = f"Exclusive cuisine in {selected_lead.area}, already delivery-ready — easy win"
            elif comp_count <= 2:
                angle = (
                    f"Low competition in {selected_lead.area} — "
                    "position as the premium alternative to existing players"
                )
            else:
                angle = (
                    f"High competition in {selected_lead.area} — "
                    "lead with talabat's reach, brand visibility, and commission advantage"
                )
            st.info(
                f"📍 **{selected_lead.area}** · {selected_lead.cuisine_type} · "
                f"⭐ {selected_lead.google_rating} ({selected_lead.num_reviews:,} reviews)\n\n"
                f"📦 Est. **{selected_lead.estimated_monthly_orders:,}** orders/mo · "
                f"AED {selected_lead.avg_ticket_aed:.0f} avg ticket\n\n"
                f"🏆 Competition: **{comp_count}** same-cuisine restaurant"
                f"{'s' if comp_count != 1 else ''} already on talabat in {selected_lead.area}\n\n"
                f"💡 **Angle:** {angle}"
            )

        if top_conv_btn:
            _convert_lead_to_partner(lead_names_top[top_chosen])
    st.divider()

    with st.container():
        # -------------------------------------------------------------------
        # Filters
        # -------------------------------------------------------------------
        col1, col2 = st.columns(2)
        with col1:
            selected_areas = st.multiselect(
                "Filter by Dubai area",
                options=ALL_AREAS,
                default=[],
                placeholder="All areas",
            )
            selected_cuisines = st.multiselect(
                "Filter by cuisine",
                options=ALL_CUISINES,
                default=[],
                placeholder="All cuisines",
            )
        with col2:
            min_score = st.slider("Minimum lead score", min_value=0, max_value=90, value=50, step=5)
            num_emails = st.slider("Number of emails to generate", min_value=1, max_value=5, value=3)

        area_filter    = ", ".join(selected_areas) if selected_areas else "all"
        cuisine_filter = ", ".join(selected_cuisines) if selected_cuisines else "all"

        # -------------------------------------------------------------------
        # Dubai Coverage Map — proper delivery-radius coverage choropleth
        # -------------------------------------------------------------------
        with st.expander("🗺️ Dubai Coverage Map", expanded=False):
            radius_km = st.slider(
                "Delivery radius per restaurant (km)",
                min_value=1, max_value=10, value=3, step=1,
                help="Each restaurant is assumed to deliver within this radius. "
                     "The map counts how many restaurants can reach each point.",
            )
            cuisine_key = tuple(sorted(selected_cuisines))
            grid_df = _compute_coverage_grid(radius_km, cuisine_key)
            if grid_df.empty:
                st.caption("No platform restaurants match the selected cuisine filter.")
            else:
                fig = px.density_map(
                    grid_df,
                    lat="lat", lon="lon", z="count",
                    radius=14,
                    color_continuous_scale="RdYlGn",
                    zoom=9,
                    center={"lat": 25.15, "lon": 55.22},
                    height=420,
                    opacity=0.85,
                )
                fig.update_layout(
                    margin={"r": 0, "t": 0, "l": 0, "b": 0},
                    paper_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                )
                st.plotly_chart(fig, use_container_width=True)
                cuisine_label = ", ".join(selected_cuisines) if selected_cuisines else "all cuisines"
                n_shown = len([
                    r for r in PLATFORM_RESTAURANTS
                    if not selected_cuisines or r["cuisine_type"] in selected_cuisines
                ])
                st.caption(
                    f"**{n_shown}** restaurants · **{radius_km} km** delivery radius · "
                    f"{cuisine_label} — brighter = more restaurants covering that point"
                )

        # -------------------------------------------------------------------
        # Lead count + Run Sales Agent button on the same row (#7)
        # -------------------------------------------------------------------
        all_leads = get_leads()
        filtered = [
            l for l in all_leads
            if (not selected_areas or l.area in selected_areas)
            and (not selected_cuisines or l.cuisine_type in selected_cuisines)
        ]

        cnt_col, add_col, btn_col = st.columns([3, 1.5, 1.5])
        cnt_col.markdown(f"**{len(filtered)} lead{'s' if len(filtered) != 1 else ''} matching filters**")
        add_btn = add_col.button("➕ Add 10 Leads", use_container_width=True, key="add_leads_btn")
        run_btn = btn_col.button("🚀 Run Sales Agent", use_container_width=True, key="run_sales")

        if add_btn:
            added = add_batch_leads(10)
            st.success(f"Added {added} new lead{'s' if added != 1 else ''} to the pipeline.")
            st.rerun()

        if not filtered:
            st.warning("No leads match the current filters.")
            _render_history(user_id)
            return

        # -------------------------------------------------------------------
        # Leads table — collapsible (#5)
        # -------------------------------------------------------------------
        scored_leads = sorted(
            [{"lead": l, "score": score_lead(l.lead_id)} for l in filtered],
            key=lambda x: x["score"]["score"],
            reverse=True,
        )
        row_height   = 38
        table_height = 46 + len(scored_leads) * row_height + 20
        lead_options = {item["lead"].name: item["lead"].lead_id for item in scored_leads}

        # -------------------------------------------------------------------
        # Leads table — collapsible
        # -------------------------------------------------------------------
        with st.expander(f"📊 Leads table ({len(scored_leads)} leads)", expanded=True):
            components.html(_render_leads_table(scored_leads), height=table_height, scrolling=False)

        # -------------------------------------------------------------------
        # Quick Outreach — single lead
        # -------------------------------------------------------------------
        st.markdown("---")
        st.markdown("**⚡ Quick Outreach** — generate an email for one lead instantly")

        qcol1, qcol2 = st.columns([4, 1])
        with qcol1:
            chosen_name = st.selectbox(
                "Lead:",
                options=list(lead_options.keys()),
                key="quick_lead_select",
                label_visibility="collapsed",
            )
        with qcol2:
            quick_btn = st.button("✉️ Generate", key="quick_btn", use_container_width=True)

        # -------------------------------------------------------------------
        # Fire off Quick generation
        # -------------------------------------------------------------------
        if quick_btn:
            task_id = str(uuid.uuid4())
            with _TASKS_LOCK:
                _TASKS[task_id] = _GenTask(task_id, f"⚡ {chosen_name}", user_id, "quick")
            threading.Thread(
                target=_generation_worker,
                args=(task_id, run_sales_agent_for_lead(lead_options[chosen_name])),
                daemon=True,
            ).start()
            st.session_state.setdefault("_active_task_ids", []).append(task_id)
            st.rerun()

        # -------------------------------------------------------------------
        # Fire off Batch generation
        # -------------------------------------------------------------------
        if run_btn:
            task_id = str(uuid.uuid4())
            label = f"🚀 Batch ({area_filter}, {cuisine_filter}, min {min_score})"
            with _TASKS_LOCK:
                _TASKS[task_id] = _GenTask(task_id, label, user_id, "batch")
            threading.Thread(
                target=_generation_worker,
                args=(task_id, run_sales_agent(
                    area_filter=area_filter,
                    cuisine_filter=cuisine_filter,
                    min_score=min_score,
                    num_emails=num_emails,
                )),
                daemon=True,
            ).start()
            st.session_state.setdefault("_active_task_ids", []).append(task_id)
            st.rerun()

        # -------------------------------------------------------------------
        # Active generation tasks + Outreach History
        # -------------------------------------------------------------------
        _render_active_tasks(user_id)
        _render_history(user_id)
