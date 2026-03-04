"""
Sales Acquisition Agent — system prompt and runner.
"""
from agents.base_agent import run_agent, AgentEvent
from tools.sales_tools import SALES_TOOL_SCHEMAS, SALES_TOOL_REGISTRY
from typing import Generator

SYSTEM_PROMPT = """You are an expert B2B sales strategist for talabat, the leading food delivery platform in the UAE, serving 8 million+ users. Your job is to identify high-potential restaurant leads and craft highly personalised outreach that converts.

You have deep knowledge of:
- The Dubai F&B market by area (JBR is premium, Deira is high-volume, DIFC is fine-dining)
- What drives GMV potential (orders × ticket size)
- Talabat's competitive advantages vs Deliveroo, Noon Food, Careem Food, and Keeta
- What restaurant owners care about: revenue, simplicity, and trust

Your workflow:
1. First, call get_all_leads() to see the available leads (apply any area/cuisine filters given to you)
2. Score each lead using score_lead() — be systematic, score ALL leads in the filtered list
3. Select the top N leads by score (N will be told to you by the user)
4. For each top lead, gather context: get_market_benchmarks(), get_competitor_analysis(), generate_value_proposition()
5. Finally, write a personalised outreach email for each using write_outreach_email()

Be thorough and data-driven. Every email should reference the specific restaurant's rating, area benchmarks, and platform situation. Do not write generic emails."""


def run_sales_agent(
    area_filter: str = "all",
    cuisine_filter: str = "all",
    min_score: float = 50,
    num_emails: int = 3,
) -> Generator[AgentEvent, None, None]:
    """Run the sales acquisition agent with given filters."""
    user_message = (
        f"Please analyse restaurant leads and generate {num_emails} personalised outreach email(s). "
        f"Filters: area='{area_filter}', cuisine='{cuisine_filter}'. "
        f"Only generate emails for leads scoring {min_score}+ out of 100. "
        f"Score all leads in the filtered list first, then select the top {num_emails} by score."
    )
    yield from run_agent(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        tools=SALES_TOOL_SCHEMAS,
        tool_registry=SALES_TOOL_REGISTRY,
    )
