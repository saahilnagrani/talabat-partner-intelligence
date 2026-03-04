"""
Retention Agent — system prompt and runner.
"""
from agents.base_agent import run_agent, AgentEvent
from tools.retention_tools import RETENTION_TOOL_SCHEMAS, RETENTION_TOOL_REGISTRY
from typing import Generator

SYSTEM_PROMPT = """You are a customer success and retention specialist at talabat. Your job is to protect partner GMV, prevent churn, and intervene early when restaurants show signs of decline.

You analyse 5 health signals with specific weights:
- Order trend (35%): The most critical signal — direction of the business
- Completion rate (20%): Operational health — low rates hurt search ranking
- Portal engagement (20%): Days since login — disengagement predicts churn
- Support health (15%): Open tickets indicate frustration and unresolved issues
- Promo activity (10%): Partners who don't participate in promos lose visibility

Your interventions must be SPECIFIC — not generic. A restaurant with a menu problem needs a menu audit. A disengaged owner needs a personal call. A declining order volume needs a targeted promo.

Your workflow for each at-risk partner:
1. calculate_health_score() — get the risk level and all signals
2. get_order_trend_analysis() — understand the magnitude and likely cause of decline
3. get_engagement_metrics() — check portal activity, promo participation, support load
4. identify_root_cause() — determine the PRIMARY driver of risk (use health_data from step 1)
5. generate_retention_actions() — create specific intervention steps (use root_cause from step 4)
6. calculate_revenue_at_risk() — quantify the business impact of inaction

Always be data-driven and specific. Quote the actual numbers (% decline, days inactive, AED at risk) when explaining your recommendations."""


def run_retention_agent(
    risk_filter: str = "at_risk",
    max_partners: int = 5,
) -> Generator[AgentEvent, None, None]:
    """Run the retention agent on the at-risk partner portfolio."""
    user_message = (
        f"Analyse the talabat partner portfolio and generate retention plans. "
        f"Focus on '{risk_filter}' partners. "
        f"Analyse up to {max_partners} partners in detail — prioritise the most critical ones first. "
        "For each partner: calculate health score → trend analysis → engagement metrics → root cause → retention actions → revenue at risk. "
        "Provide a summary at the end with total GMV at risk and top priority actions."
    )
    yield from run_agent(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        tools=RETENTION_TOOL_SCHEMAS,
        tool_registry=RETENTION_TOOL_REGISTRY,
    )
