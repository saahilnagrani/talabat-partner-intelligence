from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime


class RestaurantLead(BaseModel):
    lead_id: str
    name: str
    cuisine_type: str
    area: str
    estimated_monthly_orders: int
    avg_ticket_aed: float
    google_rating: float
    num_reviews: int
    has_delivery: bool
    current_platform: Optional[str] = None
    owner_name: str
    owner_phone: str
    owner_email: str
    notes: str = ""


class RestaurantPartner(BaseModel):
    partner_id: str
    name: str
    cuisine_type: str
    area: str
    joined_date: datetime
    monthly_orders: int
    avg_ticket_aed: float
    completion_rate: float
    rating: float
    active_menu_items: int
    last_promo_date: Optional[datetime] = None
    account_manager: str
    orders_trend_pct: float
    days_since_login: int
    support_tickets_open: int
    gmv_aed_last_30d: float
    status: Literal["new", "healthy", "at_risk", "critical"] = "healthy"
    source_lead_id: Optional[str] = None   # set when created via "Mark as Converted" in Sales tab
    recently_onboarded: bool = False        # set True when "Mark as Live" is clicked in Onboarding tab


class OutreachEmail(BaseModel):
    lead_id: str
    restaurant_name: str
    subject: str
    body: str
    personalization_signals: List[str]
    estimated_open_rate: float
    recommended_send_time: str
    follow_up_days: int


class OnboardingMilestone(BaseModel):
    day: int
    title: str
    description: str
    owner: Literal["talabat", "restaurant", "both"]
    blocking: bool


class OnboardingPlan(BaseModel):
    partner_id: str
    partner_name: str
    plan_title: str
    milestones: List[OnboardingMilestone]
    go_live_target_days: int
    assigned_success_manager: str
    first_promo_recommendation: str
    expected_day1_orders: int
    expected_30d_gmv_aed: float


class RetentionStep(BaseModel):
    action_type: Literal[
        "call", "email", "promo_offer", "menu_audit",
        "operations_review", "executive_escalation"
    ]
    description: str
    urgency_days: int
    expected_impact: str


class RetentionAction(BaseModel):
    partner_id: str
    partner_name: str
    risk_score: float
    risk_factors: List[str]
    recommended_actions: List[RetentionStep]
    priority: Literal["critical", "high", "medium", "low"]
    predicted_churn_days: int
    revenue_at_risk_aed: float
