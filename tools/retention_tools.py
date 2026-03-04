"""
Tool functions and schemas for the Retention Agent.
"""
from datetime import datetime
from data.seed import get_partners, get_partner_by_id
import config


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _orders_trend_score(trend_pct: float) -> float:
    """Convert order trend % to a 0-35 score."""
    if trend_pct >= 10:
        return 35.0
    elif trend_pct >= 0:
        return 20.0 + (trend_pct / 10) * 15
    elif trend_pct >= -15:
        return 10.0 + ((trend_pct + 15) / 15) * 10
    else:
        return max(0, 10.0 + (trend_pct + 15) / 25 * 10)


def _completion_rate_score(rate: float) -> float:
    """Convert completion rate % to a 0-20 score."""
    if rate >= 95:
        return 20.0
    elif rate >= 90:
        return 15.0
    elif rate >= 85:
        return 8.0
    elif rate >= 80:
        return 4.0
    else:
        return 0.0


def _engagement_score(days_since_login: int) -> float:
    """Convert days since last portal login to a 0-20 score."""
    if days_since_login <= 2:
        return 20.0
    elif days_since_login <= 7:
        return 15.0
    elif days_since_login <= 14:
        return 8.0
    elif days_since_login <= 30:
        return 3.0
    else:
        return 0.0


def _support_health_score(tickets_open: int) -> float:
    """Convert number of open support tickets to a 0-15 score."""
    if tickets_open == 0:
        return 15.0
    elif tickets_open <= 2:
        return 10.0
    elif tickets_open <= 5:
        return 4.0
    elif tickets_open <= 8:
        return 1.0
    else:
        return 0.0


def _promo_activity_score(last_promo_date) -> float:
    """Convert last promo participation date to a 0-10 score."""
    if last_promo_date is None:
        return 0.0
    if isinstance(last_promo_date, str):
        try:
            last_promo_date = datetime.fromisoformat(last_promo_date.replace("Z", ""))
        except Exception:
            return 5.0
    days_ago = (datetime.now() - last_promo_date).days
    if days_ago <= 14:
        return 10.0
    elif days_ago <= 30:
        return 7.0
    elif days_ago <= 60:
        return 3.0
    else:
        return 0.0


def _risk_label(score: float) -> str:
    if score <= config.RISK_CRITICAL_THRESHOLD:
        return "critical"
    elif score <= config.RISK_HIGH_THRESHOLD:
        return "high"
    elif score <= config.RISK_MEDIUM_THRESHOLD:
        return "medium"
    return "healthy"


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

def get_all_partners(risk_filter: str = "all") -> list[dict]:
    """Return filtered list of active partners."""
    partners = get_partners()
    # Exclude new partners from retention analysis
    partners = [p for p in partners if p.status != "new"]
    if risk_filter == "critical":
        partners = [p for p in partners if p.status == "critical"]
    elif risk_filter == "at_risk":
        partners = [p for p in partners if p.status in ("at_risk", "critical")]
    return [p.model_dump(mode="json") for p in partners]


def calculate_health_score(partner_id: str) -> dict:
    """Calculate a multi-signal health/churn-risk score for a partner."""
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}

    trend_s = _orders_trend_score(partner.orders_trend_pct)
    completion_s = _completion_rate_score(partner.completion_rate)
    engagement_s = _engagement_score(partner.days_since_login)
    support_s = _support_health_score(partner.support_tickets_open)
    promo_s = _promo_activity_score(partner.last_promo_date)

    total = trend_s + completion_s + engagement_s + support_s + promo_s

    risk_factors = []
    if partner.orders_trend_pct < -10:
        risk_factors.append(f"Orders declining {abs(partner.orders_trend_pct):.1f}% MoM — urgent")
    elif partner.orders_trend_pct < 0:
        risk_factors.append(f"Orders trending down {abs(partner.orders_trend_pct):.1f}% MoM")
    if partner.completion_rate < 85:
        risk_factors.append(f"Low completion rate ({partner.completion_rate:.1f}%) — operational issues")
    elif partner.completion_rate < 90:
        risk_factors.append(f"Below-average completion rate ({partner.completion_rate:.1f}%)")
    if partner.days_since_login > 30:
        risk_factors.append(f"Inactive on portal for {partner.days_since_login} days — disengaged")
    elif partner.days_since_login > 14:
        risk_factors.append(f"Hasn't logged into portal in {partner.days_since_login} days")
    if partner.support_tickets_open > 5:
        risk_factors.append(f"{partner.support_tickets_open} unresolved support tickets — frustrated partner")
    elif partner.support_tickets_open > 2:
        risk_factors.append(f"{partner.support_tickets_open} open support tickets")
    if promo_s == 0:
        risk_factors.append("Not participated in any promotions in 60+ days")
    if partner.active_menu_items < 10:
        risk_factors.append(f"Only {partner.active_menu_items} active menu items — poor selection hurts conversion")

    return {
        "partner_id": partner_id,
        "partner_name": partner.name,
        "health_score": round(total, 1),
        "risk_level": _risk_label(total),
        "score_breakdown": {
            "orders_trend (35%)": round(trend_s, 1),
            "completion_rate (20%)": round(completion_s, 1),
            "portal_engagement (20%)": round(engagement_s, 1),
            "support_health (15%)": round(support_s, 1),
            "promo_activity (10%)": round(promo_s, 1),
        },
        "risk_factors": risk_factors,
        "gmv_aed_last_30d": partner.gmv_aed_last_30d,
    }


def get_order_trend_analysis(partner_id: str) -> dict:
    """Return detailed order trend data for a partner."""
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}

    trend = partner.orders_trend_pct
    current = partner.monthly_orders
    prev_month = int(current / (1 + trend / 100))
    two_months_ago = int(prev_month / (1 + trend / 100))

    if trend < -20:
        primary_cause = "Severe operational issues likely — very high cancellation rate or poor ratings driving platform demotion"
        trend_category = "severe_decline"
    elif trend < -10:
        primary_cause = "Significant volume loss — likely combination of menu staleness, poor photos, and lack of promotions"
        trend_category = "moderate_decline"
    elif trend < 0:
        primary_cause = "Gradual erosion — increased local competition or seasonal demand shift"
        trend_category = "slight_decline"
    else:
        primary_cause = "Stable or growing"
        trend_category = "stable"

    return {
        "partner_id": partner_id,
        "current_monthly_orders": current,
        "prev_month_orders": prev_month,
        "two_months_ago_orders": two_months_ago,
        "trend_pct_mom": trend,
        "trend_category": trend_category,
        "likely_cause": primary_cause,
        "completion_rate": partner.completion_rate,
        "avg_rating": partner.rating,
        "rating_context": "Below platform average — likely affecting search ranking" if partner.rating < 4.0 else "Acceptable rating",
    }


def get_engagement_metrics(partner_id: str) -> dict:
    """Return portal engagement and promotional activity data."""
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}

    from datetime import timedelta
    last_promo_days = None
    if partner.last_promo_date:
        last_promo_days = (datetime.now() - partner.last_promo_date).days

    engagement_level = (
        "active" if partner.days_since_login <= 3
        else "moderate" if partner.days_since_login <= 14
        else "disengaged"
    )

    return {
        "partner_id": partner_id,
        "days_since_portal_login": partner.days_since_login,
        "engagement_level": engagement_level,
        "last_promo_days_ago": last_promo_days,
        "promo_participation": "active" if last_promo_days and last_promo_days <= 30 else "inactive",
        "open_support_tickets": partner.support_tickets_open,
        "support_health": "critical" if partner.support_tickets_open > 7 else "concerning" if partner.support_tickets_open > 3 else "ok",
        "active_menu_items": partner.active_menu_items,
        "menu_health": "thin" if partner.active_menu_items < 15 else "adequate",
        "insight": (
            f"Partner hasn't logged in for {partner.days_since_login} days and hasn't run a promotion in "
            f"{last_promo_days or '60+'} days. {partner.support_tickets_open} open tickets suggest unresolved frustration."
            if engagement_level == "disengaged"
            else f"Partner is {'actively engaged' if engagement_level == 'active' else 'moderately engaged'} with the platform."
        ),
    }


def identify_root_cause(partner_id: str, health_data: dict) -> dict:
    """Identify the primary root cause of a partner's decline."""
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}

    risk_factors = health_data.get("risk_factors", [])
    score_breakdown = health_data.get("score_breakdown", {})

    # Determine primary root cause by lowest scoring dimension
    scores = {
        "order_trend": score_breakdown.get("orders_trend (35%)", 35),
        "completion": score_breakdown.get("completion_rate (20%)", 20),
        "engagement": score_breakdown.get("portal_engagement (20%)", 20),
        "support": score_breakdown.get("support_health (15%)", 15),
        "promo": score_breakdown.get("promo_activity (10%)", 10),
    }

    # Normalize to percentage of max possible
    max_scores = {"order_trend": 35, "completion": 20, "engagement": 20, "support": 15, "promo": 10}
    pct_scores = {k: (scores[k] / max_scores[k]) * 100 for k in scores}
    worst_dimension = min(pct_scores, key=pct_scores.get)

    root_cause_map = {
        "order_trend": {
            "root_cause": "Volume decline",
            "explanation": f"Orders have dropped {abs(partner.orders_trend_pct):.1f}% MoM. This is the primary driver — driven by poor search ranking, lack of promotions, or increased local competition.",
            "urgency": "immediate",
        },
        "completion": {
            "root_cause": "Operational breakdown",
            "explanation": f"Completion rate of {partner.completion_rate:.1f}% is below healthy threshold. Cancellations and rejections are damaging the partner's ranking and customer trust.",
            "urgency": "immediate",
        },
        "engagement": {
            "root_cause": "Partner disengagement",
            "explanation": f"Owner hasn't logged in for {partner.days_since_login} days. Disengagement often precedes active churn — partner may be exploring alternatives.",
            "urgency": "high",
        },
        "support": {
            "root_cause": "Unresolved operational frustrations",
            "explanation": f"{partner.support_tickets_open} open tickets indicate the partner is struggling and feeling unsupported. Unresolved issues erode trust quickly.",
            "urgency": "high",
        },
        "promo": {
            "root_cause": "Visibility and demand loss",
            "explanation": "Partner has stopped participating in promotions, causing reduced visibility in the app and lower order volume. Often the first sign of disengagement.",
            "urgency": "medium",
        },
    }

    root = root_cause_map[worst_dimension]
    return {
        "partner_id": partner_id,
        "partner_name": partner.name,
        "primary_root_cause": root["root_cause"],
        "explanation": root["explanation"],
        "urgency": root["urgency"],
        "secondary_factors": risk_factors[:3],
        "worst_scoring_dimension": worst_dimension,
        "all_dimension_health_pct": {k: round(v, 0) for k, v in pct_scores.items()},
    }


def generate_retention_actions(partner_id: str, root_cause: dict) -> dict:
    """Generate specific, prioritised retention actions based on root cause."""
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}

    cause = root_cause.get("primary_root_cause", "")
    urgency = root_cause.get("urgency", "medium")

    actions = []

    if cause == "Operational breakdown" or partner.completion_rate < 85:
        actions.append({
            "action_type": "operations_review",
            "description": f"Schedule urgent operational review for {partner.name}: audit order acceptance flow, tablet connectivity, kitchen capacity vs peak hours. Target: completion rate above 92% within 14 days.",
            "urgency_days": 1,
            "expected_impact": "Restoring completion rate to 92%+ typically lifts monthly orders by 15-20% through improved search ranking",
        })

    if partner.support_tickets_open > 3:
        actions.append({
            "action_type": "call",
            "description": f"Dedicated support call to resolve all {partner.support_tickets_open} open tickets. Escalate any technical issues same-day. Acknowledge partner frustration and commit to resolution SLA.",
            "urgency_days": 1 if urgency == "immediate" else 2,
            "expected_impact": "Resolving outstanding tickets reduces churn probability by ~35% in first 30 days post-resolution",
        })

    if partner.days_since_login > 14:
        actions.append({
            "action_type": "call",
            "description": f"Personal check-in call from account manager to {partner.name}'s owner. Agenda: understand pain points, share performance data, re-engage with platform roadmap. Use partner's language — not a sales call.",
            "urgency_days": 2,
            "expected_impact": "Re-engagement call within 48h of detecting disengagement reduces 60-day churn risk by 28%",
        })

    if partner.orders_trend_pct < -10:
        actions.append({
            "action_type": "promo_offer",
            "description": f"Activate 'Recovery Promo' for {partner.name}: 10-day free delivery campaign + featured placement in {partner.area} feed. Co-funded AED 2,000 from talabat retention budget.",
            "urgency_days": 3,
            "expected_impact": f"Recovery promos typically reverse a -{abs(partner.orders_trend_pct):.0f}% trend to +5-10% within 30 days for {partner.cuisine_type} restaurants",
        })

    if partner.active_menu_items < 15:
        actions.append({
            "action_type": "menu_audit",
            "description": f"Menu audit: {partner.name} has only {partner.active_menu_items} active items. Schedule menu improvement session — add beverages, seasonal specials, and combo deals. Target 20+ items with photos.",
            "urgency_days": 5,
            "expected_impact": "Expanding from <15 to 20+ menu items increases average basket size by AED 12-18 and improves search ranking",
        })

    if not actions:
        actions.append({
            "action_type": "email",
            "description": f"Send performance summary email to {partner.name} with personalised benchmarks, top-performing menu item data, and invitation to join the next promotion cycle.",
            "urgency_days": 7,
            "expected_impact": "Proactive engagement maintains partner health and prevents future churn",
        })

    # Determine priority
    health_score = root_cause.get("all_dimension_health_pct", {})
    avg_health = sum(health_score.values()) / max(len(health_score), 1) if health_score else 50
    priority = "critical" if avg_health < 40 else "high" if avg_health < 60 else "medium"

    return {
        "partner_id": partner_id,
        "partner_name": partner.name,
        "priority": priority,
        "recommended_actions": actions,
        "total_actions": len(actions),
        "most_urgent_action": actions[0]["description"] if actions else "",
        "action_within_days": actions[0]["urgency_days"] if actions else 7,
    }


def calculate_revenue_at_risk(partner_id: str) -> dict:
    """Calculate how much GMV talabat would lose if this partner churns."""
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}

    monthly_gmv = partner.gmv_aed_last_30d
    annual_gmv = monthly_gmv * 12
    talabat_commission = monthly_gmv * 0.17
    annual_commission = annual_gmv * 0.17

    # Predicted churn days based on severity
    if partner.orders_trend_pct < -25:
        predicted_churn_days = 30
    elif partner.orders_trend_pct < -15:
        predicted_churn_days = 60
    elif partner.orders_trend_pct < 0:
        predicted_churn_days = 90
    else:
        predicted_churn_days = 120

    return {
        "partner_id": partner_id,
        "partner_name": partner.name,
        "monthly_gmv_aed": monthly_gmv,
        "annual_gmv_aed": annual_gmv,
        "monthly_talabat_revenue_aed": round(talabat_commission, 0),
        "annual_talabat_revenue_aed": round(annual_commission, 0),
        "predicted_churn_days": predicted_churn_days,
        "risk_level": "critical" if predicted_churn_days <= 30 else "high" if predicted_churn_days <= 60 else "medium",
        "replacement_cost_estimate_aed": monthly_gmv * 3,  # ~3 months GMV to acquire/onboard replacement
        "insight": f"Losing {partner.name} would cost talabat AED {talabat_commission:,.0f}/month in commission revenue. Replacing this partner takes ~3 months and costs an estimated AED {monthly_gmv * 3:,.0f} in acquisition + onboarding investment.",
    }


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

RETENTION_TOOL_SCHEMAS = [
    {
        "name": "get_all_partners",
        "description": "Get the list of active talabat restaurant partners. Filter by risk level: 'all' (default), 'at_risk' (declining), or 'critical' (severe decline). Excludes new/onboarding partners.",
        "input_schema": {
            "type": "object",
            "properties": {
                "risk_filter": {
                    "type": "string",
                    "description": "Filter: 'all', 'at_risk', or 'critical'",
                    "enum": ["all", "at_risk", "critical"],
                },
            },
        },
    },
    {
        "name": "calculate_health_score",
        "description": "Calculate a multi-signal health score (0-100) for a partner. Higher = healthier. Combines order trend, completion rate, portal engagement, support health, and promo activity. Returns risk level and all risk factors.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID to score"},
            },
            "required": ["partner_id"],
        },
    },
    {
        "name": "get_order_trend_analysis",
        "description": "Get detailed order trend data for a partner — month-over-month change, trend category (decline/stable/growth), and likely root cause of the trend.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
            },
            "required": ["partner_id"],
        },
    },
    {
        "name": "get_engagement_metrics",
        "description": "Get portal engagement data: days since login, promo participation, open support tickets, and menu health. Identifies disengagement signals.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
            },
            "required": ["partner_id"],
        },
    },
    {
        "name": "identify_root_cause",
        "description": "Identify the primary root cause of a partner's decline based on their health score data. Returns the main issue, explanation, and urgency level.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
                "health_data": {"type": "object", "description": "Health score dict from calculate_health_score"},
            },
            "required": ["partner_id", "health_data"],
        },
    },
    {
        "name": "generate_retention_actions",
        "description": "Generate specific, prioritised retention intervention actions for an at-risk partner based on their root cause analysis. Returns actionable steps with urgency timelines and expected impact.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
                "root_cause": {"type": "object", "description": "Root cause dict from identify_root_cause"},
            },
            "required": ["partner_id", "root_cause"],
        },
    },
    {
        "name": "calculate_revenue_at_risk",
        "description": "Calculate the GMV and talabat commission revenue at risk if this partner churns. Returns monthly and annual figures plus predicted churn timeline.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
            },
            "required": ["partner_id"],
        },
    },
]

RETENTION_TOOL_REGISTRY = {
    "get_all_partners": get_all_partners,
    "calculate_health_score": calculate_health_score,
    "get_order_trend_analysis": get_order_trend_analysis,
    "get_engagement_metrics": get_engagement_metrics,
    "identify_root_cause": identify_root_cause,
    "generate_retention_actions": generate_retention_actions,
    "calculate_revenue_at_risk": calculate_revenue_at_risk,
}
