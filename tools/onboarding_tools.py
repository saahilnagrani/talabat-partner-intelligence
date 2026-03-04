"""
Tool functions and schemas for the Onboarding Agent.
"""
from datetime import datetime, timedelta
from data.seed import get_partner_by_id, get_partners, MARKET_BENCHMARKS


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

SUCCESS_MANAGERS = {
    "JBR": "Sarah Johnson",
    "Dubai Marina": "Sarah Johnson",
    "DIFC": "Ahmed Al-Mansoori",
    "Downtown Dubai": "Ahmed Al-Mansoori",
    "Business Bay": "Ahmed Al-Mansoori",
    "Deira": "Priya Menon",
    "Bur Dubai": "Priya Menon",
    "Jumeirah": "Sarah Johnson",
    "Al Barsha": "Priya Menon",
    "Discovery Gardens": "Priya Menon",
    "Silicon Oasis": "Priya Menon",
    "Jumeirah Lake Towers": "Ahmed Al-Mansoori",
}

PROMO_TEMPLATES = {
    "high_demand": {
        "name": "Free Delivery Week",
        "description": "7-day free delivery promo to drive first-order volume",
        "estimated_incremental_orders": 45,
        "cost_to_restaurant_aed": 0,
    },
    "premium": {
        "name": "10% Off First 3 Orders",
        "description": "Discount on first 3 orders per customer — drives repeat behaviour",
        "estimated_incremental_orders": 30,
        "cost_to_restaurant_aed": 200,
    },
    "competitive": {
        "name": "Beat The Competition Bundle",
        "description": "Free delivery + 15% off for users who haven't ordered from this cuisine in 30 days",
        "estimated_incremental_orders": 55,
        "cost_to_restaurant_aed": 150,
    },
    "default": {
        "name": "Launch Visibility Boost",
        "description": "Featured placement in app for 14 days + free delivery for first 100 orders",
        "estimated_incremental_orders": 40,
        "cost_to_restaurant_aed": 0,
    },
}

MENU_DATA = {
    # Golden Spoon Kitchen — Indian, JLT — rushed start, several gaps
    "partner_001": {
        "items_uploaded": 8,
        "photos_uploaded": 4,           # 4 of 8 items have photos
        "pricing_gaps": 3,              # 3 items with no price set
        "missing_categories": ["Beverages", "Desserts", "Snacks"],
        "halal_cert_submitted": False,  # Not submitted yet
    },
    # Beirut Bites — Lebanese, Al Barsha — decent start, a few gaps
    "partner_002": {
        "items_uploaded": 15,
        "photos_uploaded": 11,          # 4 missing photos
        "pricing_gaps": 2,
        "missing_categories": ["Beverages"],
        "halal_cert_submitted": False,  # Still pending
    },
    # Wok This Way — Chinese, Deira — most complete, submitted halal cert proactively
    "partner_003": {
        "items_uploaded": 22,
        "photos_uploaded": 20,          # 2 missing photos
        "pricing_gaps": 0,              # All pricing complete
        "missing_categories": [],
        "halal_cert_submitted": True,
    },
}

CUISINE_COMPLEXITY = {
    "Italian": "medium", "Japanese": "high", "Indian": "low", "Pakistani": "low",
    "Lebanese": "low", "Filipino": "low", "American": "low", "Thai": "medium",
    "Korean": "medium", "Mexican": "medium", "Emirati": "high", "Persian": "medium",
    "Vietnamese": "medium", "Chinese": "low", "Turkish": "low", "Yemeni": "low",
}


def get_partner_profile(partner_id: str) -> dict:
    """Fetch a partner's full profile."""
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}
    return partner.model_dump(mode="json")


def get_onboarding_template(cuisine_type: str, area: str) -> dict:
    """Return base onboarding template based on cuisine and area."""
    complexity = CUISINE_COMPLEXITY.get(cuisine_type, "medium")
    premium_area = area in ("DIFC", "Downtown Dubai", "Dubai Marina", "JBR")

    if complexity == "high" or premium_area:
        go_live_days = 10
        menu_setup_days = 4
        photography_days = 3
    elif complexity == "medium":
        go_live_days = 7
        menu_setup_days = 2
        photography_days = 2
    else:
        go_live_days = 5
        menu_setup_days = 1
        photography_days = 1

    return {
        "cuisine_type": cuisine_type,
        "area": area,
        "complexity": complexity,
        "is_premium_area": premium_area,
        "estimated_go_live_days": go_live_days,
        "menu_setup_days": menu_setup_days,
        "photography_days": photography_days,
        "requires_taste_test": cuisine_type in ("Emirati", "Japanese"),
        "requires_halal_certification": True,
        "note": f"{'Premium area — enhanced setup recommended' if premium_area else 'Standard setup applicable'}. {cuisine_type} cuisine complexity: {complexity}.",
    }


def check_menu_readiness(partner_id: str) -> dict:
    """Check menu readiness for a new partner, using per-partner data where available."""
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}

    # Use per-partner menu data if available; fall back to derived estimate for others
    m = MENU_DATA.get(partner_id)
    if m:
        items              = m["items_uploaded"]
        photos_complete    = m["photos_uploaded"]
        pricing_gaps       = m["pricing_gaps"]
        missing_categories = m["missing_categories"]
        halal_submitted    = m["halal_cert_submitted"]
    else:
        items              = partner.active_menu_items
        photos_complete    = max(0, items - 3)
        pricing_gaps       = 2 if items < 15 else 0
        missing_categories = (
            ["Beverages", "Desserts"] if items < 10 else
            ["Beverages"] if items < 20 else []
        )
        halal_submitted    = True  # assume existing partners are already compliant

    missing_photos  = items - photos_complete
    readiness_score = min(100, int((items / 20) * 60 + (photos_complete / max(items, 1)) * 40))

    blockers = []   # hard stops — must be resolved before go-live
    warnings = []   # important but not blocking

    # --- BLOCKERS ---
    if items < 10:
        blockers.append(
            "Fewer than 10 menu items — customers expect at least 10+ options before go-live"
        )
    if pricing_gaps > 0:
        blockers.append(
            f"{pricing_gaps} pricing gap{'s' if pricing_gaps > 1 else ''} detected "
            "— all pricing must be complete before QA approval"
        )
    if not halal_submitted:
        blockers.append(
            f"Halal certification not submitted — required for {partner.cuisine_type} "
            "cuisine in UAE and must be uploaded on Day 1"
        )

    # --- WARNINGS (not blocking) ---
    if missing_photos > 0:
        warnings.append(
            f"{missing_photos} item{'s' if missing_photos > 1 else ''} missing photos "
            "— photos increase conversion by 25%, add before go-live if possible"
        )
    if missing_categories:
        cats = " and ".join(missing_categories)
        warnings.append(
            f"Missing menu categories: {cats} — recommended to populate before go-live"
        )

    recommendation = (
        "Critical gaps must be resolved before go-live — see blockers above."
        if blockers else
        "Menu is nearly ready — add missing photos to maximise conversion."
    )

    return {
        "partner_id": partner_id,
        "menu_items_uploaded": items,
        "menu_items_with_photos": photos_complete,
        "menu_items_missing_photos": missing_photos,
        "pricing_gaps": pricing_gaps,
        "missing_categories": missing_categories,
        "halal_cert_submitted": halal_submitted,
        "readiness_score_pct": readiness_score,
        "blockers": blockers,
        "warnings": warnings,
        "recommendation": recommendation,
    }


def get_area_demand_forecast(area: str, cuisine_type: str) -> dict:
    """Forecast order volume for new partner based on area + cuisine."""
    benchmarks = MARKET_BENCHMARKS.get(area, MARKET_BENCHMARKS.get("Business Bay"))
    base_orders = benchmarks["avg_monthly_orders"]
    is_top_cuisine = cuisine_type in benchmarks["top_cuisines"]

    day1_orders = 8 if is_top_cuisine else 5
    day7_orders = 35 if is_top_cuisine else 22
    day30_orders = int(base_orders * (1.1 if is_top_cuisine else 0.7))
    avg_ticket = benchmarks["avg_ticket_aed"]

    return {
        "area": area,
        "cuisine_type": cuisine_type,
        "cuisine_demand_level": "high" if is_top_cuisine else "medium",
        "forecasted_day_1_orders": day1_orders,
        "forecasted_day_7_orders": day7_orders,
        "forecasted_day_30_orders": day30_orders,
        "forecasted_30d_gmv_aed": day30_orders * avg_ticket,
        "peak_hours": "12:00-14:00 and 19:00-21:30 UAE time",
        "insight": f"{cuisine_type} is {'a top-3 cuisine in ' + area + ' — strong built-in demand' if is_top_cuisine else 'not a top cuisine in ' + area + ' — focus on differentiation and promo to build initial volume'}",
    }


def get_similar_partner_benchmarks(cuisine_type: str, area: str) -> dict:
    """Get P50/P90 benchmarks from similar existing talabat partners."""
    similar = [
        p for p in get_partners()
        if p.cuisine_type == cuisine_type and p.status == "healthy"
    ]

    if not similar:
        similar = [p for p in get_partners() if p.status == "healthy"]

    orders_list = sorted([p.monthly_orders for p in similar])
    n = len(orders_list)
    p50 = orders_list[n // 2] if orders_list else 400
    p90 = orders_list[int(n * 0.9)] if orders_list else 900

    similar_area = [p for p in similar if area in p.area]
    avg_time_to_first_order_days = 2 if similar_area else 3

    return {
        "cuisine_type": cuisine_type,
        "area": area,
        "sample_size": len(similar),
        "p50_monthly_orders": p50,
        "p90_monthly_orders": p90,
        "avg_time_to_first_order_days": avg_time_to_first_order_days,
        "avg_time_to_100_orders_days": 18,
        "best_in_class_example": f"Top {cuisine_type} partners in UAE average {p90} orders/month by month 6",
        "insight": f"Median {cuisine_type} partner achieves {p50} orders/month. Top performers reach {p90}+. First order typically arrives within {avg_time_to_first_order_days} days of go-live.",
    }


def recommend_launch_promo(partner_id: str, area_demand: dict) -> dict:
    """Recommend the best launch promotion for this partner."""
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}

    demand_level = area_demand.get("cuisine_demand_level", "medium")
    avg_ticket = partner.avg_ticket_aed

    if demand_level == "high" and avg_ticket > 80:
        promo = PROMO_TEMPLATES["premium"]
    elif demand_level == "high":
        promo = PROMO_TEMPLATES["high_demand"]
    elif avg_ticket > 100:
        promo = PROMO_TEMPLATES["premium"]
    else:
        promo = PROMO_TEMPLATES["default"]

    return {
        "partner_id": partner_id,
        "recommended_promo": promo["name"],
        "description": promo["description"],
        "estimated_incremental_orders_first_30d": promo["estimated_incremental_orders"],
        "cost_to_restaurant_aed": promo["cost_to_restaurant_aed"],
        "talabat_co_funding_aed": 5000,
        "rationale": f"Given {'high' if demand_level == 'high' else 'moderate'} local demand and AED {avg_ticket} avg ticket, this promo maximises first-month volume while building repeat behaviour.",
    }


def assign_success_manager(area: str) -> dict:
    """Assign the right success manager based on geographic coverage."""
    manager = SUCCESS_MANAGERS.get(area, "Ahmed Al-Mansoori")
    return {
        "area": area,
        "assigned_success_manager": manager,
        "onboarding_sla_days": 7,
        "first_checkin_day": 3,
        "go_live_review_day": 7,
        "30_day_review_day": 30,
        "contact_channel": "WhatsApp + Email",
    }


def build_onboarding_plan(partner_id: str, all_data: dict) -> dict:
    """
    Assemble the final structured onboarding plan from all gathered data.
    Returns a complete milestone-based plan.
    """
    partner = get_partner_by_id(partner_id)
    if not partner:
        return {"error": f"Partner {partner_id} not found"}

    template = all_data.get("template", {})
    menu = all_data.get("menu_readiness", {})
    demand = all_data.get("demand_forecast", {})
    promo = all_data.get("promo", {})
    manager_info = all_data.get("manager", {})
    go_live_days = template.get("estimated_go_live_days", 7)

    milestones = [
        {
            "day": 1,
            "title": "Contract & Account Setup",
            "description": "Sign partnership agreement, create talabat partner portal account, submit business license + halal certificate",
            "owner": "both",
            "blocking": True,
        },
        {
            "day": 1,
            "title": "Assign Success Manager",
            "description": f"{manager_info.get('assigned_success_manager', 'TBD')} introduced via WhatsApp. Onboarding call scheduled.",
            "owner": "talabat",
            "blocking": False,
        },
        {
            "day": 2,
            "title": "Menu Upload",
            "description": f"Upload all {partner.active_menu_items} menu items with descriptions and pricing. Ensure categories are complete.",
            "owner": "restaurant",
            "blocking": True,
        },
        {
            "day": template.get("photography_days", 2),
            "title": "Professional Menu Photography",
            "description": "talabat photographer visits for complimentary food photography session. Items with photos convert 25% better.",
            "owner": "talabat",
            "blocking": False,
        },
        {
            "day": template.get("menu_setup_days", 3),
            "title": "Menu QA & Approval",
            "description": "talabat team reviews menu for completeness, pricing, and policy compliance. Final approval to go live.",
            "owner": "talabat",
            "blocking": True,
        },
        {
            "day": go_live_days - 1,
            "title": "Test Order & Operational Walkthrough",
            "description": "Place a test order to verify tablet, printer, and acceptance flow. Confirm packaging and delivery handoff process.",
            "owner": "both",
            "blocking": True,
        },
        {
            "day": go_live_days,
            "title": "GO LIVE 🚀",
            "description": f"Restaurant is live on talabat. Launch promo activated: {promo.get('recommended_promo', 'Free Delivery Week')}. Target: {demand.get('forecasted_day_1_orders', 8)} orders on day 1.",
            "owner": "both",
            "blocking": False,
        },
        {
            "day": go_live_days + 3,
            "title": "First Performance Check-in",
            "description": "Success manager reviews first orders, addresses any operational issues, checks customer ratings.",
            "owner": "talabat",
            "blocking": False,
        },
        {
            "day": 30,
            "title": "30-Day Business Review",
            "description": f"Full performance review: orders vs forecast ({demand.get('forecasted_day_30_orders', 150)} target), rating trend, GMV analysis. Plan month 2 strategy.",
            "owner": "both",
            "blocking": False,
        },
    ]

    return {
        "partner_id": partner_id,
        "partner_name": partner.name,
        "cuisine_type": partner.cuisine_type,
        "area": partner.area,
        "plan_title": f"{partner.name} — talabat Onboarding Plan",
        "milestones": milestones,
        "go_live_target_days": go_live_days,
        "assigned_success_manager": manager_info.get("assigned_success_manager", "TBD"),
        "first_promo_recommendation": promo.get("recommended_promo", "Free Delivery Week"),
        "promo_description": promo.get("description", ""),
        "expected_day_1_orders": demand.get("forecasted_day_1_orders", 8),
        "expected_day_7_orders": demand.get("forecasted_day_7_orders", 35),
        "expected_30d_gmv_aed": demand.get("forecasted_30d_gmv_aed", 15000),
        "menu_blockers": menu.get("blockers", []),
        "menu_warnings": menu.get("warnings", []),
    }


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

ONBOARDING_TOOL_SCHEMAS = [
    {
        "name": "get_partner_profile",
        "description": "Fetch full profile of a new talabat restaurant partner including cuisine, area, menu items, and current status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID, e.g. 'partner_001'"},
            },
            "required": ["partner_id"],
        },
    },
    {
        "name": "get_onboarding_template",
        "description": "Get the base onboarding template for a cuisine type and area. Returns estimated go-live timeline, complexity level, and key requirements.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cuisine_type": {"type": "string", "description": "Cuisine type of the restaurant"},
                "area": {"type": "string", "description": "Dubai area of the restaurant"},
            },
            "required": ["cuisine_type", "area"],
        },
    },
    {
        "name": "check_menu_readiness",
        "description": "Check how ready the restaurant's menu is for going live — items uploaded, photos, pricing gaps, and missing categories. Returns blockers that must be resolved before go-live.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID to check menu readiness for"},
            },
            "required": ["partner_id"],
        },
    },
    {
        "name": "get_area_demand_forecast",
        "description": "Forecast order volume for a new restaurant based on area and cuisine. Returns day-1, day-7, and day-30 order forecasts and GMV estimate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "area": {"type": "string", "description": "Dubai area"},
                "cuisine_type": {"type": "string", "description": "Cuisine type"},
            },
            "required": ["area", "cuisine_type"],
        },
    },
    {
        "name": "get_similar_partner_benchmarks",
        "description": "Get P50 and P90 benchmarks from similar existing talabat partners in the same cuisine. Shows what's achievable and typical time-to-first-order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cuisine_type": {"type": "string", "description": "Cuisine type to benchmark against"},
                "area": {"type": "string", "description": "Dubai area for localised benchmarks"},
            },
            "required": ["cuisine_type", "area"],
        },
    },
    {
        "name": "recommend_launch_promo",
        "description": "Recommend the best launch promotion for a new partner based on their profile and area demand level.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
                "area_demand": {"type": "object", "description": "Area demand forecast dict from get_area_demand_forecast"},
            },
            "required": ["partner_id", "area_demand"],
        },
    },
    {
        "name": "assign_success_manager",
        "description": "Assign the correct success manager to the partner based on their Dubai area. Returns manager name and check-in schedule.",
        "input_schema": {
            "type": "object",
            "properties": {
                "area": {"type": "string", "description": "Dubai area of the restaurant"},
            },
            "required": ["area"],
        },
    },
    {
        "name": "build_onboarding_plan",
        "description": (
            "Assemble the complete onboarding plan from all gathered data. "
            "Call this as the FINAL step after collecting: template, menu_readiness, demand_forecast, promo, and manager data. "
            "Returns a full milestone-based onboarding plan with day-by-day actions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "string", "description": "Partner ID"},
                "all_data": {
                    "type": "object",
                    "description": "Dict containing: template (from get_onboarding_template), menu_readiness, demand_forecast, promo, manager keys with their respective data dicts.",
                },
            },
            "required": ["partner_id", "all_data"],
        },
    },
]

ONBOARDING_TOOL_REGISTRY = {
    "get_partner_profile": get_partner_profile,
    "get_onboarding_template": get_onboarding_template,
    "check_menu_readiness": check_menu_readiness,
    "get_area_demand_forecast": get_area_demand_forecast,
    "get_similar_partner_benchmarks": get_similar_partner_benchmarks,
    "recommend_launch_promo": recommend_launch_promo,
    "assign_success_manager": assign_success_manager,
    "build_onboarding_plan": build_onboarding_plan,
}
