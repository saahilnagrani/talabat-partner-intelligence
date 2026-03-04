"""
Tool functions and schemas for the Sales Acquisition Agent.
"""
from data.seed import get_leads, get_lead_by_id, MARKET_BENCHMARKS, COMPETITOR_DATA


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

def get_all_leads(area: str = None, cuisine: str = None) -> list[dict]:
    """Return filtered list of restaurant leads."""
    leads = get_leads()
    if area and area.lower() != "all":
        leads = [l for l in leads if area.lower() in l.area.lower()]
    if cuisine and cuisine.lower() != "all":
        leads = [l for l in leads if cuisine.lower() in l.cuisine_type.lower()]
    return [l.model_dump(mode="json") for l in leads]


def score_lead(lead_id: str) -> dict:
    """Score a lead 0-100 and return detailed breakdown with reasoning."""
    lead = get_lead_by_id(lead_id)
    if not lead:
        return {"error": f"Lead {lead_id} not found"}

    # Weighted scoring formula
    order_score = min(lead.estimated_monthly_orders / 1000 * 30, 30)
    ticket_score = min(lead.avg_ticket_aed / 140 * 25, 25)
    rating_score = (lead.google_rating / 5) * 20
    no_delivery_bonus = 15 if not lead.has_delivery else 5
    no_platform_bonus = 10 if lead.current_platform is None else 3

    total = order_score + ticket_score + rating_score + no_delivery_bonus + no_platform_bonus

    reasoning_parts = []
    if not lead.has_delivery:
        reasoning_parts.append("No delivery presence — maximum acquisition potential")
    else:
        reasoning_parts.append(f"Already on delivery ({lead.current_platform}) but can be won over")
    if lead.current_platform is None:
        reasoning_parts.append("Not on any platform — talabat would be first-mover advantage")
    reasoning_parts.append(f"Google rating {lead.google_rating}/5 with {lead.num_reviews} reviews indicates {'strong' if lead.google_rating >= 4.5 else 'good'} brand quality")
    reasoning_parts.append(f"Estimated {lead.estimated_monthly_orders} monthly orders × AED {lead.avg_ticket_aed} ticket = AED {lead.estimated_monthly_orders * lead.avg_ticket_aed:,.0f} GMV potential")

    return {
        "lead_id": lead_id,
        "restaurant_name": lead.name,
        "score": round(total, 1),
        "breakdown": {
            "order_volume_potential": round(order_score, 1),
            "ticket_size_quality": round(ticket_score, 1),
            "brand_quality_rating": round(rating_score, 1),
            "delivery_gap_opportunity": round(no_delivery_bonus, 1),
            "platform_exclusivity": round(no_platform_bonus, 1),
        },
        "estimated_monthly_gmv_aed": lead.estimated_monthly_orders * lead.avg_ticket_aed,
        "reasoning": " | ".join(reasoning_parts),
    }


def get_market_benchmarks(area: str, cuisine_type: str) -> dict:
    """Return Dubai area benchmarks and cuisine context."""
    area_data = MARKET_BENCHMARKS.get(area, MARKET_BENCHMARKS.get("Business Bay"))
    return {
        "area": area,
        "cuisine_type": cuisine_type,
        "area_avg_monthly_orders": area_data["avg_monthly_orders"],
        "area_avg_ticket_aed": area_data["avg_ticket_aed"],
        "top_cuisines_in_area": area_data["top_cuisines"],
        "cuisine_is_top_performer": cuisine_type in area_data["top_cuisines"],
        "insight": f"In {area}, top-performing partners average {area_data['avg_monthly_orders']} orders/month at AED {area_data['avg_ticket_aed']} average ticket. {cuisine_type} is {'a top cuisine' if cuisine_type in area_data['top_cuisines'] else 'underrepresented'} in this area.",
    }


def get_competitor_analysis(current_platform: str) -> dict:
    """Return talabat's competitive advantages vs the restaurant's current platform."""
    competitor = COMPETITOR_DATA.get(current_platform, COMPETITOR_DATA[None])
    return {
        "current_platform": current_platform or "None (no delivery)",
        "their_commission_pct": competitor["commission_pct"],
        "their_weaknesses": competitor["weaknesses"],
        "talabat_advantages": competitor["talabat_advantages"],
        "key_pitch_angle": competitor["talabat_advantages"][0] if competitor["talabat_advantages"] else "Best platform in UAE",
    }


def generate_value_proposition(lead_id: str, score_data: dict) -> dict:
    """Generate personalised value proposition bullets for a lead."""
    lead = get_lead_by_id(lead_id)
    if not lead:
        return {"error": f"Lead {lead_id} not found"}

    monthly_gmv = lead.estimated_monthly_orders * lead.avg_ticket_aed
    talabat_net = monthly_gmv * (1 - 0.17)  # after 17% commission estimate

    bullets = []

    if not lead.has_delivery:
        bullets.append(f"Unlock a new revenue stream: AED {monthly_gmv:,.0f}/month in delivery GMV with zero upfront investment in logistics")
    else:
        bullets.append(f"Diversify from a single platform — reduce dependency risk and reach talabat's 8M+ UAE users")

    bullets.append(f"Based on {lead.area} benchmarks, similar {lead.cuisine_type} restaurants on talabat average {MARKET_BENCHMARKS.get(lead.area, {}).get('avg_monthly_orders', 350)} orders/month")
    bullets.append(f"Your {lead.google_rating}⭐ rating and {lead.num_reviews} reviews give you a head-start — talabat's algorithm surfaces top-rated restaurants prominently")
    bullets.append("Free professional menu photography + AED 5,000 launch promotion budget included")
    bullets.append("Dedicated account manager (not a call centre) — direct line for support")

    return {
        "lead_id": lead_id,
        "restaurant_name": lead.name,
        "value_prop_bullets": bullets,
        "estimated_net_monthly_revenue_aed": round(talabat_net, 0),
        "headline": f"Help {lead.name} generate AED {monthly_gmv:,.0f}/month in new delivery revenue",
    }


def write_outreach_email(lead_id: str, value_prop: dict, benchmark_data: dict, competitor_data: dict) -> dict:
    """
    Compose a personalised outreach email using all gathered data.
    Returns the email as a structured dict.
    """
    lead = get_lead_by_id(lead_id)
    if not lead:
        return {"error": f"Lead {lead_id} not found"}

    platform_line = (
        f"I noticed {lead.name} isn't on any delivery platform yet"
        if lead.current_platform is None
        else f"I noticed {lead.name} is currently on {lead.current_platform}"
    )

    delivery_line = (
        "you're not yet offering delivery"
        if not lead.has_delivery
        else f"you're doing delivery through {lead.current_platform}"
    )

    subject = f"Partnership opportunity for {lead.name} — {lead.area}'s top {lead.cuisine_type} destination"

    body = f"""Hi {lead.owner_name},

I came across {lead.name} while researching the best {lead.cuisine_type} restaurants in {lead.area} — your {lead.google_rating}-star rating and {lead.num_reviews} reviews really stood out.

{platform_line}. I'm reaching out from talabat because I think there's a significant opportunity for you.

Here's what I've seen from similar {lead.cuisine_type} restaurants in {lead.area} after joining talabat:
• Average of {benchmark_data.get('area_avg_monthly_orders', 350)} orders/month within 60 days of going live
• AED {benchmark_data.get('area_avg_ticket_aed', 65)} average ticket (your dine-in suggests you could exceed this)
• {lead.cuisine_type} is {'one of the top-performing cuisines' if benchmark_data.get('cuisine_is_top_performer') else 'an underserved category'} in {lead.area} on our platform — meaning less competition for top search results

{f"Since {delivery_line}, we can get you live with zero logistics setup — we handle drivers, tracking, and customer support." if not lead.has_delivery else f"If you're open to it, we can offer you a better commercial arrangement than {lead.current_platform} — our commission structure is meaningfully lower, and we have a significantly larger customer base in the UAE."}

What I'd like to offer as a starting point:
✓ Free professional menu photography session
✓ AED 5,000 in launch promotions (free delivery + discount campaigns)
✓ Dedicated account manager — not a ticket queue
✓ Full analytics dashboard to track performance

Would you be open to a 20-minute call this week? I'd love to show you what talabat's top {lead.cuisine_type} partners in {lead.area} are achieving.

Best regards,
[Your Name]
Business Development Manager, talabat
📱 +971 50 XXX XXXX"""

    personalization_signals = [
        f"Google rating {lead.google_rating}/5 with {lead.num_reviews} reviews cited",
        f"Area-specific benchmark: {lead.area} avg {benchmark_data.get('area_avg_monthly_orders')} orders/month",
        f"Cuisine context: {lead.cuisine_type} performance in {lead.area}",
        f"Platform status: {'no delivery presence' if not lead.has_delivery else f'on {lead.current_platform}'}",
        f"Personalised revenue potential: AED {lead.estimated_monthly_orders * lead.avg_ticket_aed:,.0f}/month",
    ]

    return {
        "lead_id": lead_id,
        "restaurant_name": lead.name,
        "owner_name": lead.owner_name,
        "owner_email": lead.owner_email,
        "subject": subject,
        "body": body,
        "personalization_signals": personalization_signals,
        "estimated_open_rate_pct": 34 if lead.google_rating >= 4.5 else 28,
        "recommended_send_time": "Tuesday or Wednesday, 9-11am UAE time",
        "follow_up_days": 3,
    }


# ---------------------------------------------------------------------------
# Tool schemas (JSON schema format for Claude API)
# ---------------------------------------------------------------------------

SALES_TOOL_SCHEMAS = [
    {
        "name": "get_all_leads",
        "description": (
            "Fetch the list of restaurant leads (prospective talabat partners). "
            "Optionally filter by Dubai area (e.g. 'JBR', 'Deira') or cuisine type (e.g. 'Italian', 'Indian'). "
            "Returns lead IDs, names, areas, order estimates, ratings, and current platform info."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "area": {"type": "string", "description": "Dubai area to filter by, e.g. 'JBR', 'Dubai Marina', 'Deira'. Use 'all' or omit for no filter."},
                "cuisine": {"type": "string", "description": "Cuisine type to filter by, e.g. 'Italian', 'Indian'. Use 'all' or omit for no filter."},
            },
        },
    },
    {
        "name": "score_lead",
        "description": (
            "Score a specific restaurant lead from 0 to 100 based on GMV potential, ticket quality, "
            "brand strength, delivery gap, and platform exclusivity opportunity. "
            "Returns the overall score, a breakdown by factor, and detailed reasoning. "
            "Call this for each lead you want to evaluate."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "string", "description": "The lead ID to score, e.g. 'lead_001'"},
            },
            "required": ["lead_id"],
        },
    },
    {
        "name": "get_market_benchmarks",
        "description": (
            "Get Dubai market benchmarks for a specific area and cuisine type. "
            "Returns average monthly orders, average ticket size, top cuisines in the area, "
            "and an insight about how this cuisine performs in that location."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "area": {"type": "string", "description": "Dubai area, e.g. 'JBR', 'DIFC', 'Deira'"},
                "cuisine_type": {"type": "string", "description": "Cuisine type, e.g. 'Italian', 'Indian'"},
            },
            "required": ["area", "cuisine_type"],
        },
    },
    {
        "name": "get_competitor_analysis",
        "description": (
            "Get talabat's competitive advantages against the restaurant's current delivery platform. "
            "Pass None if the restaurant has no delivery platform. "
            "Returns the competitor's weaknesses and talabat's key advantages to use in the pitch."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "current_platform": {
                    "type": "string",
                    "description": "Current platform: 'Deliveroo', 'Zomato', or null/None if no platform",
                    "enum": ["Deliveroo", "Zomato", "None"],
                },
            },
            "required": ["current_platform"],
        },
    },
    {
        "name": "generate_value_proposition",
        "description": (
            "Generate personalised value proposition bullets for a lead based on their profile. "
            "Returns 5 tailored bullet points and a revenue headline. "
            "Use after scoring and benchmarking to craft the pitch angle."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "string", "description": "Lead ID to generate value prop for"},
                "score_data": {"type": "object", "description": "Score data dict returned by score_lead"},
            },
            "required": ["lead_id", "score_data"],
        },
    },
    {
        "name": "write_outreach_email",
        "description": (
            "Compose a fully personalised outreach email for a lead using all gathered context. "
            "Returns the email subject, body, personalisation signals used, open rate estimate, "
            "and follow-up timing recommendation. Call this as the final step for each selected lead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "string", "description": "Lead ID to write the email for"},
                "value_prop": {"type": "object", "description": "Value prop dict from generate_value_proposition"},
                "benchmark_data": {"type": "object", "description": "Benchmark dict from get_market_benchmarks"},
                "competitor_data": {"type": "object", "description": "Competitor dict from get_competitor_analysis"},
            },
            "required": ["lead_id", "value_prop", "benchmark_data", "competitor_data"],
        },
    },
]

SALES_TOOL_REGISTRY = {
    "get_all_leads": get_all_leads,
    "score_lead": score_lead,
    "get_market_benchmarks": get_market_benchmarks,
    "get_competitor_analysis": get_competitor_analysis,
    "generate_value_proposition": generate_value_proposition,
    "write_outreach_email": write_outreach_email,
}
