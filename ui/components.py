"""
Reusable Streamlit UI components for the talabat AI Agent demo.
"""
from __future__ import annotations
import streamlit as st


TALABAT_ORANGE = "#FF6000"
TALABAT_DARK = "#1a1a1a"


def inject_css():
    """Inject global CSS styling into the Streamlit app."""
    st.markdown(
        f"""
        <style>
            /* Primary button styling */
            .stButton > button {{
                background-color: {TALABAT_ORANGE};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                padding: 0.5rem 1.5rem;
                transition: background-color 0.2s;
            }}
            .stButton > button:hover {{
                background-color: #e55500;
                color: white;
            }}

            /* Thinking stream terminal */
            .thinking-box {{
                background: {TALABAT_DARK};
                color: #00d4aa;
                padding: 14px 18px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 0.8em;
                line-height: 1.5;
                max-height: 240px;
                overflow-y: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
                border: 1px solid #333;
            }}

            /* Tool call cards */
            .tool-call-header {{
                color: {TALABAT_ORANGE};
                font-weight: 600;
                font-size: 0.9em;
            }}

            /* Risk badges */
            .badge-critical {{
                background: #dc3545; color: white;
                padding: 3px 10px; border-radius: 12px;
                font-size: 0.78em; font-weight: 600;
            }}
            .badge-high {{
                background: #fd7e14; color: white;
                padding: 3px 10px; border-radius: 12px;
                font-size: 0.78em; font-weight: 600;
            }}
            .badge-medium {{
                background: #ffc107; color: #1a1a1a;
                padding: 3px 10px; border-radius: 12px;
                font-size: 0.78em; font-weight: 600;
            }}
            .badge-healthy {{
                background: #28a745; color: white;
                padding: 3px 10px; border-radius: 12px;
                font-size: 0.78em; font-weight: 600;
            }}

            /* Metric cards */
            .metric-card {{
                background: #f8f9fa;
                border-left: 4px solid {TALABAT_ORANGE};
                padding: 12px 16px;
                border-radius: 4px;
                margin-bottom: 8px;
            }}

            /* Email card */
            .email-subject {{
                font-size: 1.05em;
                font-weight: 600;
                color: {TALABAT_DARK};
                margin-bottom: 6px;
            }}

            /* Timeline */
            .timeline-item {{
                border-left: 3px solid #dee2e6;
                padding: 0 0 16px 20px;
                position: relative;
                margin-left: 10px;
            }}
            .timeline-dot {{
                width: 12px; height: 12px;
                border-radius: 50%;
                position: absolute;
                left: -7px; top: 4px;
            }}
            .timeline-day {{
                font-size: 0.75em; color: #6c757d;
                font-weight: 600; text-transform: uppercase;
            }}
            .timeline-title {{
                font-weight: 600; font-size: 0.95em;
                margin: 2px 0;
            }}
            .timeline-desc {{
                font-size: 0.85em; color: #495057;
            }}

            /* Section header */
            .section-header {{
                border-bottom: 2px solid {TALABAT_ORANGE};
                padding-bottom: 6px;
                margin-bottom: 16px;
                font-size: 1.1em;
                font-weight: 700;
                color: {TALABAT_DARK};
            }}

            /* Hide only the hamburger rerun/settings menu and footer branding */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            [data-testid="stHeader"] {{
                background: transparent !important;
                border-bottom: none !important;
            }}

            /* Full-width tabs with larger font */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 0px;
                border-bottom: 2px solid {TALABAT_ORANGE};
            }}
            .stTabs [data-baseweb="tab"] {{
                flex: 1;
                justify-content: center;
                font-size: 1rem;
                font-weight: 600;
                padding: 0.6rem 1rem;
                border-radius: 0;
            }}
            .stTabs [aria-selected="true"] {{
                color: {TALABAT_ORANGE} !important;
                border-bottom: 3px solid {TALABAT_ORANGE} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """Render the talabat branded header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f'<h2 style="color:{TALABAT_ORANGE}; margin:0 0 4px 0; font-size:1.75em; font-weight:700;">'
            f'🍔 talabat Partner Intelligence</h2>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<p style="text-align:right; color:#999; font-size:0.8em; margin-top:10px;">'
            'Powered by Claude Sonnet</p>',
            unsafe_allow_html=True,
        )
    st.divider()


def render_thinking_box(text: str) -> str:
    """Return HTML for the agent thinking stream box."""
    escaped = text.replace("<", "&lt;").replace(">", "&gt;")
    return f'<div class="thinking-box">{escaped}</div>'


def render_tool_call_card(name: str, inputs: dict, result: dict | None = None):
    """Render a single tool call as a Streamlit expander."""
    icon = "✅" if result and "error" not in result else "🔧"
    label = f"{icon} `{name}`"
    with st.expander(label, expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Inputs**")
            st.json(inputs)
        with col2:
            if result is not None:
                st.markdown("**Result**")
                st.json(result)


def render_risk_badge(risk_level: str) -> str:
    """Return HTML for a colored risk badge."""
    labels = {"critical": "CRITICAL", "high": "HIGH RISK", "medium": "MEDIUM", "healthy": "HEALTHY"}
    label = labels.get(risk_level, risk_level.upper())
    return f'<span class="badge-{risk_level}">{label}</span>'


def render_score_badge(score: float) -> str:
    """Return HTML badge for a numeric score."""
    if score >= 75:
        color = "#28a745"
    elif score >= 55:
        color = "#ffc107"
    else:
        color = "#dc3545"
    return f'<span style="background:{color};color:{"white" if score < 75 or score >= 55 else "#1a1a1a"};padding:3px 10px;border-radius:12px;font-size:0.78em;font-weight:600;">{score:.0f}/100</span>'


def render_email_card(email: dict, key_suffix: str = ""):
    """Render a generated outreach email in a styled card."""
    import urllib.parse

    st.markdown(
        f'<div class="email-subject">📧 {email.get("subject", "Outreach Email")}</div>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Est. Open Rate", f"{email.get('estimated_open_rate_pct', 30)}%")
    col2.metric("Send Time", email.get("recommended_send_time", "Tue/Wed 9-11am")[:15])
    col3.metric("Follow-up in", f"{email.get('follow_up_days', 3)} days")

    st.markdown("**Email Body**")
    st.text_area(
        label="",
        value=email.get("body", ""),
        height=300,
        key=f"email_{email.get('lead_id', 'unknown')}_{email.get('restaurant_name', '')}{key_suffix}",
        label_visibility="collapsed",
    )

    signals = email.get("personalization_signals", [])
    if signals:
        st.markdown("**Personalisation signals used:**")
        for sig in signals:
            st.markdown(f"  • {sig}")

    # Launch buttons
    to  = email.get("owner_email", "")
    su  = urllib.parse.quote(email.get("subject", ""))
    bdy = urllib.parse.quote(email.get("body", ""))
    gmail_url   = f"https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(to)}&su={su}&body={bdy}"
    outlook_url = f"mailto:{to}?subject={urllib.parse.quote(email.get('subject', ''))}&body={bdy}"
    st.markdown("**Send via:**")
    c1, c2 = st.columns(2)
    c1.link_button("📧 Open in Gmail",   gmail_url,   use_container_width=True)
    c2.link_button("📨 Open in Outlook", outlook_url, use_container_width=True)


def render_onboarding_timeline(plan: dict):
    """Render a visual milestone timeline for an onboarding plan."""
    milestones = plan.get("milestones", [])
    if not milestones:
        st.info("No milestones found in plan.")
        return

    owner_colors = {
        "talabat": "#FF6000",
        "restaurant": "#0066cc",
        "both": "#6f42c1",
    }

    st.markdown('<div class="section-header">Onboarding Timeline</div>', unsafe_allow_html=True)

    for m in milestones:
        owner = m.get("owner", "both")
        color = owner_colors.get(owner, "#999")
        blocking_tag = " 🔴 BLOCKING" if m.get("blocking") else ""
        is_golive = "GO LIVE" in m.get("title", "")

        if is_golive:
            st.markdown(
                f'<div style="background:#FF6000;color:white;padding:10px 16px;border-radius:8px;'
                f'font-weight:700;font-size:1em;margin:8px 0;">🚀 Day {m["day"]}: {m["title"]}</div>'
                f'<p style="margin:4px 0 16px 8px;font-size:0.85em;color:#495057">{m.get("description","")}</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="timeline-item">'
                f'<div class="timeline-dot" style="background:{color};"></div>'
                f'<div class="timeline-day">Day {m["day"]} • {owner.upper()}{blocking_tag}</div>'
                f'<div class="timeline-title">{m.get("title","")}</div>'
                f'<div class="timeline-desc">{m.get("description","")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_retention_action_card(action_data: dict, revenue_data: dict | None = None):
    """Render a retention action plan for a partner."""
    risk_level = action_data.get("priority", "medium")
    partner_name = action_data.get("partner_name", "Unknown")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"#### {partner_name} "
            + render_risk_badge(risk_level),
            unsafe_allow_html=True,
        )
    with col2:
        if revenue_data:
            monthly = revenue_data.get("monthly_gmv_aed", 0)
            st.markdown(
                f'<div style="text-align:right;">'
                f'<small style="color:#999;">GMV at risk</small><br>'
                f'<strong style="color:#dc3545;">AED {monthly:,.0f}/mo</strong>'
                f'</div>',
                unsafe_allow_html=True,
            )

    actions = action_data.get("recommended_actions", [])
    action_icons = {
        "call": "📞",
        "email": "📧",
        "promo_offer": "🎁",
        "menu_audit": "📋",
        "operations_review": "⚙️",
        "executive_escalation": "🚨",
    }
    for i, act in enumerate(actions, 1):
        icon = action_icons.get(act.get("action_type", ""), "•")
        urgency = act.get("urgency_days", 7)
        urgency_color = "#dc3545" if urgency <= 1 else "#fd7e14" if urgency <= 3 else "#ffc107"
        st.markdown(
            f'<div style="border-left:3px solid {urgency_color};padding:8px 14px;'
            f'margin:6px 0;background:#fafafa;border-radius:0 6px 6px 0;">'
            f'<strong>{icon} Action {i}</strong> '
            f'<span style="color:{urgency_color};font-size:0.8em;font-weight:600;">'
            f'Within {urgency} day{"s" if urgency != 1 else ""}</span><br>'
            f'<span style="font-size:0.88em;">{act.get("description","")}</span><br>'
            f'<span style="font-size:0.8em;color:#6c757d;">Expected: {act.get("expected_impact","")}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
