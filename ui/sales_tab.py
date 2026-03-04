"""
Tab 1: Sales Acquisition Agent UI.
"""
import streamlit as st
from data.seed import MARKET_BENCHMARKS
from agents.sales_agent import run_sales_agent
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

    run_btn = st.button("🚀 Run Sales Agent", use_container_width=True, key="run_sales")

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
        import pandas as pd
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
