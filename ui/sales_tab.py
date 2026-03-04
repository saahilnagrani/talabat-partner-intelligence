"""
Tab 1: Sales Acquisition Agent UI.
"""
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from data.seed import MARKET_BENCHMARKS, get_leads
from agents.sales_agent import run_sales_agent
from tools.sales_tools import score_lead
from ui.components import (
    render_thinking_box,
    render_tool_call_card,
    render_email_card,
    render_score_badge,
)

ALL_AREAS = list(MARKET_BENCHMARKS.keys())
ALL_CUISINES = [
    "Lebanese", "Indian", "Pakistani", "Italian", "American",
    "Japanese", "Korean", "Filipino", "Thai", "Vietnamese",
    "Mexican", "Persian", "Emirati", "Chinese",
]


def _render_leads_table(scored_leads: list[dict]) -> str:
    """Render leads as a sortable HTML table with per-row score popup."""
    NUMERIC = [3, 4, 5, 6, 8]  # column indices that sort numerically

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
            f'<div class="tt-row"><span>Orders</span><span>{bd["order_volume_potential"]:.1f} / 30</span></div>'
            f'<div class="tt-row"><span>Ticket size</span><span>{bd["ticket_size_quality"]:.1f} / 25</span></div>'
            f'<div class="tt-row"><span>Brand rating</span><span>{bd["brand_quality_rating"]:.1f} / 20</span></div>'
            f'<div class="tt-row"><span>Delivery gap</span><span>{bd["delivery_gap_opportunity"]:.0f} / 15</span></div>'
            f'<div class="tt-row"><span>Platform gap</span><span>{bd["platform_exclusivity"]:.0f} / 10</span></div>'
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
      .leads-tbl {{
        width:100%; border-collapse:collapse;
        font-size:0.85em; color:#e0e0e0;
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
        document.querySelectorAll('.score-tip.open').forEach(function(e) {{ e.classList.remove('open'); }});
        if (!wasOpen) {{
          tip.classList.add('open');
          setTimeout(function() {{
            document.addEventListener('click', function close(e) {{
              if (!tip.contains(e.target) && e.target !== btn) {{
                tip.classList.remove('open');
                document.removeEventListener('click', close);
              }}
            }});
          }}, 0);
        }}
      }}
    </script>"""


def render():
    st.markdown(
        "### 🎯 Sales Acquisition Agent\n"
        "Scores restaurant leads, selects top prospects, and writes personalised outreach emails. "
        "Watch the agent reason through each lead in real time."
    )

    # Controls
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

    area_filter = ", ".join(selected_areas) if selected_areas else "all"
    cuisine_filter = ", ".join(selected_cuisines) if selected_cuisines else "all"

    # Live leads preview table
    all_leads = get_leads()
    filtered = [
        l for l in all_leads
        if (not selected_areas or l.area in selected_areas)
        and (not selected_cuisines or l.cuisine_type in selected_cuisines)
    ]

    st.markdown(f"**{len(filtered)} lead{'s' if len(filtered) != 1 else ''} matching filters**")
    if filtered:
        scored_leads = sorted(
            [{"lead": l, "score": score_lead(l.lead_id)} for l in filtered],
            key=lambda x: x["score"]["score"],
            reverse=True,
        )
        row_height = 38
        table_height = 46 + len(scored_leads) * row_height + 20
        components.html(_render_leads_table(scored_leads), height=table_height, scrolling=False)
    else:
        st.warning("No leads match the current filters.")

    run_btn = st.button("🚀 Run Sales Agent", use_container_width=True, key="run_sales", disabled=not filtered)

    if not run_btn:
        st.info("Configure your filters above and click **Run Sales Agent** to start.")
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

    pending_calls: dict[str, dict] = {}  # tool_use_id -> {name, inputs}
    collected_emails: list[dict] = []
    collected_scores: list[dict] = []

    with st.spinner("Agent is running…"):
        for event in run_sales_agent(
            area_filter=area_filter,
            cuisine_filter=cuisine_filter,
            min_score=min_score,
            num_emails=num_emails,
        ):
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

                # Render tool card
                call_info = pending_calls.pop(tid, {"name": name, "inputs": {}})
                with tool_area:
                    render_tool_call_card(call_info["name"], call_info["inputs"], result)

                # Collect structured results
                if name == "write_outreach_email" and isinstance(result, dict) and "body" in result:
                    collected_emails.append(result)
                if name == "score_lead" and isinstance(result, dict) and "score" in result:
                    collected_scores.append(result)

            elif event.type == "complete":
                st.success("✅ Agent complete!")

            elif event.type == "error":
                st.error(f"Agent error: {event.data}")
                return

    # -----------------------------------------------------------------------
    # Results
    # -----------------------------------------------------------------------
    if collected_scores:
        st.divider()
        st.markdown("#### Lead Scores")
        df = pd.DataFrame([
            {
                "Restaurant": s.get("restaurant_name", s.get("lead_id")),
                "Score": s.get("score", 0),
                "Monthly GMV (AED)": f"AED {s.get('estimated_monthly_gmv_aed', 0):,.0f}",
                "Reasoning": s.get("reasoning", "")[:80] + "…",
            }
            for s in sorted(collected_scores, key=lambda x: x.get("score", 0), reverse=True)
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    if collected_emails:
        st.divider()
        st.markdown(f"#### Generated Outreach Emails ({len(collected_emails)})")
        for i, email in enumerate(collected_emails, 1):
            with st.expander(
                f"📧 Email {i}: {email.get('restaurant_name', 'Unknown')} — {email.get('subject', '')[:60]}",
                expanded=(i == 1),
            ):
                render_email_card(email)
    elif not collected_emails and run_btn:
        st.warning("No emails were generated. Try lowering the minimum score threshold.")
