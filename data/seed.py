"""
Deterministic Dubai restaurant dataset for the talabat AI demo.
All data is simulated for demo purposes.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from data.models import RestaurantLead, RestaurantPartner

# ---------------------------------------------------------------------------
# LEADS — 20 prospective restaurants not yet on talabat
# ---------------------------------------------------------------------------

_LEADS_RAW = [
    # JBR / Dubai Marina — high ticket, affluent
    dict(lead_id="lead_001", name="Maison Tariq", cuisine_type="Lebanese",
         area="JBR", estimated_monthly_orders=420, avg_ticket_aed=88,
         google_rating=4.7, num_reviews=312, has_delivery=False, current_platform=None,
         owner_name="Tariq Al-Hassan", owner_phone="+971501234561", owner_email="tariq@maisontariq.ae",
         notes="Popular dinner spot, long queues on weekends. Owner mentioned delivery interest last month."),

    dict(lead_id="lead_002", name="Tokyo Bay Kitchen", cuisine_type="Japanese",
         area="Dubai Marina", estimated_monthly_orders=350, avg_ticket_aed=125,
         google_rating=4.8, num_reviews=567, has_delivery=True, current_platform="Deliveroo",
         owner_name="Kenji Nakamura", owner_phone="+971502234562", owner_email="kenji@tokyobay.ae",
         notes="High-end omakase + casual rolls. Currently on Deliveroo but complained about high fees last week."),

    dict(lead_id="lead_003", name="La Piccola Roma", cuisine_type="Italian",
         area="JBR", estimated_monthly_orders=330, avg_ticket_aed=110,
         google_rating=4.5, num_reviews=445, has_delivery=True, current_platform="Deliveroo",
         owner_name="Marco Rossini", owner_phone="+971503234563", owner_email="marco@lapiccolaRoma.ae",
         notes="Authentic Neapolitan pizza. Deliveroo exclusive but contract expires next month."),

    dict(lead_id="lead_004", name="The American Table", cuisine_type="American",
         area="Dubai Marina", estimated_monthly_orders=380, avg_ticket_aed=95,
         google_rating=4.5, num_reviews=321, has_delivery=True, current_platform="Deliveroo",
         owner_name="Jake Williams", owner_phone="+971504234564", owner_email="jake@americantable.ae",
         notes="Gourmet burgers and steaks. Owner actively looking for a second delivery platform."),

    dict(lead_id="lead_005", name="Seoul Bites", cuisine_type="Korean",
         area="Dubai Marina", estimated_monthly_orders=390, avg_ticket_aed=72,
         google_rating=4.4, num_reviews=289, has_delivery=True, current_platform="Careem Food",
         owner_name="Min-Ji Park", owner_phone="+971505234565", owner_email="minji@seoulbites.ae",
         notes="Korean BBQ and fried chicken. On Careem Food but volume is low — owner frustrated with poor discoverability."),

    # Deira / Bur Dubai — high volume, budget-friendly
    dict(lead_id="lead_006", name="Karachi Darbar Express", cuisine_type="Pakistani",
         area="Bur Dubai", estimated_monthly_orders=780, avg_ticket_aed=42,
         google_rating=4.3, num_reviews=2341, has_delivery=True, current_platform=None,
         owner_name="Imran Qureshi", owner_phone="+971506234566", owner_email="imran@karachidarbar.ae",
         notes="Institution in Bur Dubai. No delivery at all — owner skeptical but open to conversation."),

    dict(lead_id="lead_007", name="Punjab Da Dhaba", cuisine_type="Indian",
         area="Deira", estimated_monthly_orders=920, avg_ticket_aed=38,
         google_rating=4.5, num_reviews=1834, has_delivery=True, current_platform="Noon Food",
         owner_name="Gurpreet Singh", owner_phone="+971507234567", owner_email="gurpreet@punjabdhaba.ae",
         notes="Best butter chicken in Deira. On Noon Food but wants better analytics and a larger customer base. Huge review base."),

    dict(lead_id="lead_008", name="Spice of Persia", cuisine_type="Persian",
         area="Deira", estimated_monthly_orders=340, avg_ticket_aed=55,
         google_rating=4.4, num_reviews=456, has_delivery=False, current_platform=None,
         owner_name="Ali Tehrani", owner_phone="+971508234568", owner_email="ali@spiceofpersia.ae",
         notes="Family-run restaurant. No delivery presence. Very loyal dine-in crowd."),

    dict(lead_id="lead_009", name="Lahori Karahi House", cuisine_type="Pakistani",
         area="Bur Dubai", estimated_monthly_orders=650, avg_ticket_aed=38,
         google_rating=4.2, num_reviews=1456, has_delivery=True, current_platform="Keeta, Noon Food",
         owner_name="Zafar Iqbal", owner_phone="+971509234569", owner_email="zafar@lahorikarahi.ae",
         notes="24-hour restaurant. High late-night volume. On both Keeta and Noon Food but order quality inconsistent. Owner open to switching primary platform."),

    dict(lead_id="lead_010", name="Al Bait Al Qadim", cuisine_type="Emirati",
         area="Deira", estimated_monthly_orders=210, avg_ticket_aed=95,
         google_rating=4.9, num_reviews=189, has_delivery=False, current_platform=None,
         owner_name="Fatima Al-Rashidi", owner_phone="+971510234570", owner_email="fatima@albaitalqadim.ae",
         notes="Rare authentic Emirati cuisine. No delivery. Pride of place — needs careful approach."),

    # Business Bay / DIFC — premium, corporate
    dict(lead_id="lead_011", name="Via Roma Ristorante", cuisine_type="Italian",
         area="DIFC", estimated_monthly_orders=280, avg_ticket_aed=145,
         google_rating=4.6, num_reviews=423, has_delivery=False, current_platform=None,
         owner_name="Luca Ferrari", owner_phone="+971511234571", owner_email="luca@viaromadifc.ae",
         notes="Fine dining in DIFC. No delivery currently — sees it as beneath brand. Needs tailored pitch."),

    dict(lead_id="lead_012", name="Hana Omakase", cuisine_type="Japanese",
         area="DIFC", estimated_monthly_orders=290, avg_ticket_aed=135,
         google_rating=4.7, num_reviews=234, has_delivery=False, current_platform=None,
         owner_name="Hana Watanabe", owner_phone="+971512234572", owner_email="hana@hanaomakase.ae",
         notes="Exclusive 12-seat omakase. Could do premium delivery for lunch sets."),

    dict(lead_id="lead_013", name="Burger District", cuisine_type="American",
         area="Business Bay", estimated_monthly_orders=450, avg_ticket_aed=58,
         google_rating=4.4, num_reviews=673, has_delivery=True, current_platform="Deliveroo",
         owner_name="Sara Mitchell", owner_phone="+971513234573", owner_email="sara@burgerdistrict.ae",
         notes="Craft burgers. High corporate lunch demand. Deliveroo contract up for renewal."),

    dict(lead_id="lead_014", name="Pho Saigon", cuisine_type="Vietnamese",
         area="Business Bay", estimated_monthly_orders=260, avg_ticket_aed=65,
         google_rating=4.6, num_reviews=198, has_delivery=False, current_platform=None,
         owner_name="Linh Nguyen", owner_phone="+971514234574", owner_email="linh@phosaigon.ae",
         notes="Authentic Vietnamese. No delivery. Owner expressed interest in expanding."),

    dict(lead_id="lead_015", name="El Patron Mexican Grill", cuisine_type="Mexican",
         area="Downtown Dubai", estimated_monthly_orders=220, avg_ticket_aed=78,
         google_rating=4.7, num_reviews=178, has_delivery=False, current_platform=None,
         owner_name="Carlos Vega", owner_phone="+971515234575", owner_email="carlos@elpatron.ae",
         notes="Only authentic Mexican in Downtown. No delivery. Huge potential with tourist crowd."),

    # Scattered areas — value segment
    dict(lead_id="lead_016", name="Taste of Manila", cuisine_type="Filipino",
         area="Discovery Gardens", estimated_monthly_orders=510, avg_ticket_aed=35,
         google_rating=4.6, num_reviews=892, has_delivery=True, current_platform="Careem Food, Deliveroo",
         owner_name="Maria Santos", owner_phone="+971516234576", owner_email="maria@tasteofmanila.ae",
         notes="Huge Filipino expat community nearby. On Careem Food and Deliveroo but neither has strong coverage in Discovery Gardens. Wants better reach."),

    dict(lead_id="lead_017", name="Naan Stop Curry", cuisine_type="Indian",
         area="Silicon Oasis", estimated_monthly_orders=430, avg_ticket_aed=40,
         google_rating=4.3, num_reviews=567, has_delivery=False, current_platform=None,
         owner_name="Rahul Sharma", owner_phone="+971517234577", owner_email="rahul@naanstopcurry.ae",
         notes="Tech park area — huge lunch delivery potential. No delivery setup at all."),

    dict(lead_id="lead_018", name="Bangkok Street Food", cuisine_type="Thai",
         area="Al Barsha", estimated_monthly_orders=360, avg_ticket_aed=52,
         google_rating=4.5, num_reviews=412, has_delivery=True, current_platform="Deliveroo",
         owner_name="Somchai Wiriyaporn", owner_phone="+971518234578", owner_email="somchai@bangkokstreet.ae",
         notes="Casual Thai. Deliveroo rating 3.8 due to packaging issues. Owner wants fresh start."),

    dict(lead_id="lead_019", name="Lotus Thai Bistro", cuisine_type="Thai",
         area="Al Barsha", estimated_monthly_orders=280, avg_ticket_aed=48,
         google_rating=4.3, num_reviews=234, has_delivery=False, current_platform=None,
         owner_name="Nattawut Charoenwong", owner_phone="+971519234579", owner_email="nat@lotusthai.ae",
         notes="Smaller Thai restaurant. No delivery. Could be quick win — low complexity."),

    dict(lead_id="lead_020", name="Casa Mia Trattoria", cuisine_type="Italian",
         area="Jumeirah", estimated_monthly_orders=290, avg_ticket_aed=115,
         google_rating=4.6, num_reviews=289, has_delivery=False, current_platform=None,
         owner_name="Antonio Marino", owner_phone="+971520234580", owner_email="antonio@casamia.ae",
         notes="Family-run Italian in Jumeirah. No delivery. Very popular with local families."),
]

# ---------------------------------------------------------------------------
# PARTNERS — 30 existing talabat partners
# ---------------------------------------------------------------------------

def _dt(days_ago: int) -> datetime:
    return datetime.now() - timedelta(days=days_ago)

_PARTNERS_RAW = [
    # --- NEW (3) — just joined, in onboarding ---
    dict(partner_id="partner_001", name="Golden Spoon Kitchen", cuisine_type="Indian",
         area="Jumeirah Lake Towers", joined_date=_dt(3), monthly_orders=12, avg_ticket_aed=52,
         completion_rate=88.0, rating=4.1, active_menu_items=8, last_promo_date=None,
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=0.0,
         days_since_login=1, support_tickets_open=2, gmv_aed_last_30d=624, status="new"),

    dict(partner_id="partner_002", name="Beirut Bites", cuisine_type="Lebanese",
         area="Al Barsha", joined_date=_dt(5), monthly_orders=28, avg_ticket_aed=68,
         completion_rate=91.0, rating=4.3, active_menu_items=15, last_promo_date=None,
         account_manager="Sarah Johnson", orders_trend_pct=0.0,
         days_since_login=0, support_tickets_open=1, gmv_aed_last_30d=1904, status="new"),

    dict(partner_id="partner_003", name="Wok This Way", cuisine_type="Chinese",
         area="Deira", joined_date=_dt(7), monthly_orders=45, avg_ticket_aed=44,
         completion_rate=93.0, rating=4.2, active_menu_items=22, last_promo_date=None,
         account_manager="Priya Menon", orders_trend_pct=0.0,
         days_since_login=2, support_tickets_open=0, gmv_aed_last_30d=1980, status="new"),

    # --- HEALTHY (12) — strong performance ---
    dict(partner_id="partner_004", name="Zaiqa Restaurant", cuisine_type="Pakistani",
         area="Bur Dubai", joined_date=_dt(420), monthly_orders=1240, avg_ticket_aed=41,
         completion_rate=95.2, rating=4.6, active_menu_items=48, last_promo_date=_dt(8),
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=12.3,
         days_since_login=1, support_tickets_open=0, gmv_aed_last_30d=50840, status="healthy"),

    dict(partner_id="partner_005", name="Ravi's Indian Kitchen", cuisine_type="Indian",
         area="Deira", joined_date=_dt(680), monthly_orders=980, avg_ticket_aed=38,
         completion_rate=94.8, rating=4.5, active_menu_items=62, last_promo_date=_dt(3),
         account_manager="Priya Menon", orders_trend_pct=8.7,
         days_since_login=0, support_tickets_open=1, gmv_aed_last_30d=37240, status="healthy"),

    dict(partner_id="partner_006", name="Il Forno Pizzeria", cuisine_type="Italian",
         area="JBR", joined_date=_dt(520), monthly_orders=620, avg_ticket_aed=88,
         completion_rate=96.1, rating=4.7, active_menu_items=35, last_promo_date=_dt(12),
         account_manager="Sarah Johnson", orders_trend_pct=15.2,
         days_since_login=2, support_tickets_open=0, gmv_aed_last_30d=54560, status="healthy"),

    dict(partner_id="partner_007", name="Yakiniku House", cuisine_type="Japanese",
         area="Dubai Marina", joined_date=_dt(310), monthly_orders=480, avg_ticket_aed=135,
         completion_rate=95.5, rating=4.8, active_menu_items=42, last_promo_date=_dt(6),
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=22.1,
         days_since_login=1, support_tickets_open=0, gmv_aed_last_30d=64800, status="healthy"),

    dict(partner_id="partner_008", name="Shawarma King", cuisine_type="Lebanese",
         area="Jumeirah", joined_date=_dt(890), monthly_orders=1580, avg_ticket_aed=28,
         completion_rate=93.7, rating=4.4, active_menu_items=24, last_promo_date=_dt(4),
         account_manager="Priya Menon", orders_trend_pct=5.4,
         days_since_login=0, support_tickets_open=2, gmv_aed_last_30d=44240, status="healthy"),

    dict(partner_id="partner_009", name="The Grill House", cuisine_type="American",
         area="Business Bay", joined_date=_dt(445), monthly_orders=720, avg_ticket_aed=72,
         completion_rate=94.2, rating=4.5, active_menu_items=38, last_promo_date=_dt(9),
         account_manager="Sarah Johnson", orders_trend_pct=9.8,
         days_since_login=3, support_tickets_open=1, gmv_aed_last_30d=51840, status="healthy"),

    dict(partner_id="partner_010", name="Manila Express", cuisine_type="Filipino",
         area="Discovery Gardens", joined_date=_dt(560), monthly_orders=890, avg_ticket_aed=33,
         completion_rate=92.8, rating=4.3, active_menu_items=44, last_promo_date=_dt(14),
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=18.6,
         days_since_login=1, support_tickets_open=0, gmv_aed_last_30d=29370, status="healthy"),

    dict(partner_id="partner_011", name="Biryani Palace", cuisine_type="Indian",
         area="Silicon Oasis", joined_date=_dt(730), monthly_orders=1100, avg_ticket_aed=45,
         completion_rate=94.0, rating=4.6, active_menu_items=56, last_promo_date=_dt(5),
         account_manager="Priya Menon", orders_trend_pct=7.2,
         days_since_login=2, support_tickets_open=1, gmv_aed_last_30d=49500, status="healthy"),

    dict(partner_id="partner_012", name="Thai Garden", cuisine_type="Thai",
         area="Al Barsha", joined_date=_dt(380), monthly_orders=560, avg_ticket_aed=55,
         completion_rate=93.5, rating=4.4, active_menu_items=38, last_promo_date=_dt(10),
         account_manager="Sarah Johnson", orders_trend_pct=11.3,
         days_since_login=1, support_tickets_open=0, gmv_aed_last_30d=30800, status="healthy"),

    dict(partner_id="partner_013", name="Sushi Suzuki", cuisine_type="Japanese",
         area="DIFC", joined_date=_dt(290), monthly_orders=310, avg_ticket_aed=165,
         completion_rate=97.2, rating=4.9, active_menu_items=28, last_promo_date=_dt(7),
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=28.4,
         days_since_login=0, support_tickets_open=0, gmv_aed_last_30d=51150, status="healthy"),

    dict(partner_id="partner_014", name="Mandi Masters", cuisine_type="Yemeni",
         area="Deira", joined_date=_dt(610), monthly_orders=760, avg_ticket_aed=48,
         completion_rate=91.8, rating=4.5, active_menu_items=18, last_promo_date=_dt(11),
         account_manager="Priya Menon", orders_trend_pct=6.8,
         days_since_login=2, support_tickets_open=1, gmv_aed_last_30d=36480, status="healthy"),

    dict(partner_id="partner_015", name="Pasta Fresca", cuisine_type="Italian",
         area="Downtown Dubai", joined_date=_dt(420), monthly_orders=440, avg_ticket_aed=98,
         completion_rate=95.8, rating=4.6, active_menu_items=32, last_promo_date=_dt(6),
         account_manager="Sarah Johnson", orders_trend_pct=13.7,
         days_since_login=1, support_tickets_open=0, gmv_aed_last_30d=43120, status="healthy"),

    # --- AT RISK (10) — declining or disengaging ---
    dict(partner_id="partner_016", name="Dosa Corner", cuisine_type="Indian",
         area="Bur Dubai", joined_date=_dt(580), monthly_orders=420, avg_ticket_aed=32,
         completion_rate=88.5, rating=4.1, active_menu_items=14, last_promo_date=_dt(45),
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=-8.2,
         days_since_login=12, support_tickets_open=3, gmv_aed_last_30d=13440, status="at_risk"),

    dict(partner_id="partner_017", name="Mediterranean Mezze", cuisine_type="Lebanese",
         area="Jumeirah", joined_date=_dt(340), monthly_orders=280, avg_ticket_aed=75,
         completion_rate=89.8, rating=4.0, active_menu_items=18, last_promo_date=_dt(38),
         account_manager="Priya Menon", orders_trend_pct=-12.4,
         days_since_login=15, support_tickets_open=2, gmv_aed_last_30d=21000, status="at_risk"),

    dict(partner_id="partner_018", name="Seoul Flavours", cuisine_type="Korean",
         area="Al Barsha", joined_date=_dt(260), monthly_orders=190, avg_ticket_aed=62,
         completion_rate=87.2, rating=3.9, active_menu_items=20, last_promo_date=_dt(52),
         account_manager="Sarah Johnson", orders_trend_pct=-15.8,
         days_since_login=18, support_tickets_open=4, gmv_aed_last_30d=11780, status="at_risk"),

    dict(partner_id="partner_019", name="Noodle Bar", cuisine_type="Chinese",
         area="Business Bay", joined_date=_dt(480), monthly_orders=350, avg_ticket_aed=55,
         completion_rate=90.1, rating=4.2, active_menu_items=22, last_promo_date=_dt(30),
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=-7.5,
         days_since_login=10, support_tickets_open=2, gmv_aed_last_30d=19250, status="at_risk"),

    dict(partner_id="partner_020", name="Bombay Kitchen", cuisine_type="Indian",
         area="Discovery Gardens", joined_date=_dt(650), monthly_orders=510, avg_ticket_aed=36,
         completion_rate=86.4, rating=3.8, active_menu_items=12, last_promo_date=_dt(60),
         account_manager="Priya Menon", orders_trend_pct=-10.3,
         days_since_login=22, support_tickets_open=5, gmv_aed_last_30d=18360, status="at_risk"),

    dict(partner_id="partner_021", name="Tacos & Co", cuisine_type="Mexican",
         area="Dubai Marina", joined_date=_dt(210), monthly_orders=160, avg_ticket_aed=68,
         completion_rate=88.9, rating=4.0, active_menu_items=16, last_promo_date=_dt(42),
         account_manager="Sarah Johnson", orders_trend_pct=-9.6,
         days_since_login=14, support_tickets_open=2, gmv_aed_last_30d=10880, status="at_risk"),

    dict(partner_id="partner_022", name="Pita & More", cuisine_type="Lebanese",
         area="Deira", joined_date=_dt(720), monthly_orders=620, avg_ticket_aed=29,
         completion_rate=87.6, rating=4.0, active_menu_items=10, last_promo_date=_dt(35),
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=-6.9,
         days_since_login=8, support_tickets_open=3, gmv_aed_last_30d=17980, status="at_risk"),

    dict(partner_id="partner_023", name="Zing Burger", cuisine_type="American",
         area="Silicon Oasis", joined_date=_dt(390), monthly_orders=290, avg_ticket_aed=48,
         completion_rate=89.5, rating=4.1, active_menu_items=14, last_promo_date=_dt(48),
         account_manager="Priya Menon", orders_trend_pct=-11.2,
         days_since_login=16, support_tickets_open=2, gmv_aed_last_30d=13920, status="at_risk"),

    dict(partner_id="partner_024", name="Curry Leaf", cuisine_type="Indian",
         area="JBR", joined_date=_dt(470), monthly_orders=240, avg_ticket_aed=65,
         completion_rate=88.0, rating=3.9, active_menu_items=18, last_promo_date=_dt(55),
         account_manager="Sarah Johnson", orders_trend_pct=-13.8,
         days_since_login=20, support_tickets_open=4, gmv_aed_last_30d=15600, status="at_risk"),

    dict(partner_id="partner_025", name="Sakura Ramen", cuisine_type="Japanese",
         area="Jumeirah Lake Towers", joined_date=_dt(305), monthly_orders=210, avg_ticket_aed=72,
         completion_rate=87.8, rating=4.0, active_menu_items=16, last_promo_date=_dt(40),
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=-8.9,
         days_since_login=13, support_tickets_open=3, gmv_aed_last_30d=15120, status="at_risk"),

    # --- CRITICAL (5) — severe decline, urgent intervention needed ---
    dict(partner_id="partner_026", name="Al Khaleej Restaurant", cuisine_type="Emirati",
         area="Deira", joined_date=_dt(940), monthly_orders=180, avg_ticket_aed=82,
         completion_rate=78.4, rating=3.5, active_menu_items=8, last_promo_date=_dt(90),
         account_manager="Priya Menon", orders_trend_pct=-28.5,
         days_since_login=42, support_tickets_open=8, gmv_aed_last_30d=14760, status="critical"),

    dict(partner_id="partner_027", name="Punjabi Rasoi", cuisine_type="Indian",
         area="Bur Dubai", joined_date=_dt(810), monthly_orders=240, avg_ticket_aed=38,
         completion_rate=75.2, rating=3.4, active_menu_items=6, last_promo_date=_dt(120),
         account_manager="Sarah Johnson", orders_trend_pct=-32.1,
         days_since_login=55, support_tickets_open=11, gmv_aed_last_30d=9120, status="critical"),

    dict(partner_id="partner_028", name="Casa Mexicana", cuisine_type="Mexican",
         area="DIFC", joined_date=_dt(280), monthly_orders=85, avg_ticket_aed=95,
         completion_rate=80.1, rating=3.6, active_menu_items=10, last_promo_date=_dt(75),
         account_manager="Ahmed Al-Mansoori", orders_trend_pct=-24.8,
         days_since_login=35, support_tickets_open=6, gmv_aed_last_30d=8075, status="critical"),

    dict(partner_id="partner_029", name="Dragon Palace", cuisine_type="Chinese",
         area="Al Barsha", joined_date=_dt(680), monthly_orders=310, avg_ticket_aed=44,
         completion_rate=77.6, rating=3.3, active_menu_items=9, last_promo_date=_dt(100),
         account_manager="Priya Menon", orders_trend_pct=-35.4,
         days_since_login=48, support_tickets_open=9, gmv_aed_last_30d=13640, status="critical"),

    dict(partner_id="partner_030", name="Istanbul Grill", cuisine_type="Turkish",
         area="Business Bay", joined_date=_dt(520), monthly_orders=145, avg_ticket_aed=68,
         completion_rate=79.8, rating=3.7, active_menu_items=7, last_promo_date=_dt(85),
         account_manager="Sarah Johnson", orders_trend_pct=-22.3,
         days_since_login=38, support_tickets_open=7, gmv_aed_last_30d=9860, status="critical"),
]

# ---------------------------------------------------------------------------
# Market benchmarks — avg orders/ticket per area + cuisine
# ---------------------------------------------------------------------------

MARKET_BENCHMARKS = {
    "JBR": {"avg_monthly_orders": 410, "avg_ticket_aed": 92, "top_cuisines": ["Italian", "American", "Japanese"]},
    "Dubai Marina": {"avg_monthly_orders": 380, "avg_ticket_aed": 88, "top_cuisines": ["Japanese", "American", "Korean"]},
    "DIFC": {"avg_monthly_orders": 260, "avg_ticket_aed": 148, "top_cuisines": ["Japanese", "Italian", "American"]},
    "Downtown Dubai": {"avg_monthly_orders": 295, "avg_ticket_aed": 112, "top_cuisines": ["American", "Italian", "Mexican"]},
    "Business Bay": {"avg_monthly_orders": 420, "avg_ticket_aed": 72, "top_cuisines": ["American", "Vietnamese", "Indian"]},
    "Deira": {"avg_monthly_orders": 710, "avg_ticket_aed": 41, "top_cuisines": ["Indian", "Pakistani", "Lebanese"]},
    "Bur Dubai": {"avg_monthly_orders": 680, "avg_ticket_aed": 38, "top_cuisines": ["Pakistani", "Indian", "Filipino"]},
    "Jumeirah": {"avg_monthly_orders": 340, "avg_ticket_aed": 85, "top_cuisines": ["Lebanese", "Italian", "American"]},
    "Al Barsha": {"avg_monthly_orders": 390, "avg_ticket_aed": 52, "top_cuisines": ["Thai", "Indian", "Korean"]},
    "Discovery Gardens": {"avg_monthly_orders": 550, "avg_ticket_aed": 34, "top_cuisines": ["Filipino", "Indian", "Pakistani"]},
    "Silicon Oasis": {"avg_monthly_orders": 460, "avg_ticket_aed": 42, "top_cuisines": ["Indian", "American", "Pakistani"]},
    "Jumeirah Lake Towers": {"avg_monthly_orders": 380, "avg_ticket_aed": 68, "top_cuisines": ["Indian", "Japanese", "Lebanese"]},
}

COMPETITOR_DATA = {
    "Deliveroo": {
        "commission_pct": 30,
        "platform_fee_aed": 0,
        "avg_delivery_time_min": 35,
        "analytics_dashboard": "Basic",
        "marketing_support": "Paid only",
        "weaknesses": ["High commission (30% vs talabat's 15-18%)", "Limited UAE market coverage", "No Arabic interface", "Poor customer support response times"],
        "talabat_advantages": ["Lower commission", "Larger UAE customer base", "Arabic-first platform", "Dedicated account manager", "Free launch promotions"],
    },
    "Noon Food": {
        "commission_pct": 20,
        "platform_fee_aed": 0,
        "avg_delivery_time_min": 42,
        "analytics_dashboard": "Basic",
        "marketing_support": "Noon-app cross-promotions only",
        "weaknesses": ["Smaller food-delivery customer base vs talabat", "Primarily known as e-commerce — less food discovery intent", "Limited restaurant density outside central Dubai", "Weaker delivery logistics network"],
        "talabat_advantages": ["5x larger active food-delivery customer base in UAE", "Food-first platform — higher intent and repeat order rates", "Superior delivery SLA and logistics coverage", "Dedicated restaurant success team", "Exclusive Ramadan and National Day campaigns"],
    },
    "Careem Food": {
        "commission_pct": 22,
        "platform_fee_aed": 0,
        "avg_delivery_time_min": 38,
        "analytics_dashboard": "Basic",
        "marketing_support": "Limited to Careem Super App",
        "weaknesses": ["Food ordering is secondary to ride-hailing on Careem app", "Lower food discovery and browse behaviour", "Smaller restaurant catalogue vs talabat", "Less localised UAE food content and curation"],
        "talabat_advantages": ["Largest restaurant catalogue in UAE", "Food-native platform — customers open talabat specifically to order food", "8M+ UAE users vs Careem Food's smaller food-ordering subset", "Better merchant analytics and reporting", "Free professional menu photography"],
    },
    "Keeta": {
        "commission_pct": 18,
        "platform_fee_aed": 0,
        "avg_delivery_time_min": 30,
        "analytics_dashboard": "Moderate",
        "marketing_support": "Aggressive subsidy campaigns (unsustainable)",
        "weaknesses": ["Relatively new to UAE — limited brand trust and customer base", "Heavy reliance on subsidies to drive orders — volume may drop", "Limited coverage outside central Dubai", "Uncertain long-term market commitment"],
        "talabat_advantages": ["Established UAE brand with 15+ years of trust", "Stable, sustainable order volume without artificial subsidies", "Pan-UAE coverage including suburbs and emerging areas", "Stronger corporate and B2B ordering channel", "Local team with deep UAE market expertise"],
    },
    None: {
        "commission_pct": 0,
        "platform_fee_aed": 0,
        "avg_delivery_time_min": None,
        "analytics_dashboard": "None",
        "marketing_support": "None",
        "weaknesses": ["Zero delivery revenue", "Limited to walk-ins only", "No digital presence for delivery", "Missing entire delivery-native customer segment"],
        "talabat_advantages": ["Instant access to 8M+ UAE app users", "Turn-key delivery logistics", "No upfront tech investment", "Free menu photography", "Launch promotion budget"],
    },
}

# ---------------------------------------------------------------------------
# Public accessors
# ---------------------------------------------------------------------------

_leads_cache: list[RestaurantLead] | None = None
_partners_cache: list[RestaurantPartner] | None = None

# IDs of leads that have been converted to partners — filtered out of get_leads()
_converted_lead_ids: set[str] = set()

# ---------------------------------------------------------------------------
# Extra leads pool — used by "Add 10 Leads" button
# ---------------------------------------------------------------------------

_EXTRA_LEADS_POOL = [
    dict(lead_id="lead_021", name="Naan Stop", cuisine_type="Indian", area="Palm Jumeirah",
         estimated_monthly_orders=520, avg_ticket_aed=72, google_rating=4.4, num_reviews=310,
         has_delivery=False, current_platform=None,
         owner_name="Vikram Nair", owner_phone="+971 50 211 3344", owner_email="vikram@naanstop.ae"),
    dict(lead_id="lead_022", name="Seoul Bites", cuisine_type="Korean", area="Silicon Oasis",
         estimated_monthly_orders=380, avg_ticket_aed=85, google_rating=4.6, num_reviews=195,
         has_delivery=False, current_platform=None,
         owner_name="Ji-Young Park", owner_phone="+971 55 322 4455", owner_email="jy@seoulbites.ae"),
    dict(lead_id="lead_023", name="Taco Loco", cuisine_type="Mexican", area="JBR",
         estimated_monthly_orders=610, avg_ticket_aed=68, google_rating=4.3, num_reviews=420,
         has_delivery=True, current_platform="Deliveroo",
         owner_name="Carlos Mendez", owner_phone="+971 50 433 5566", owner_email="carlos@tacoloco.ae"),
    dict(lead_id="lead_024", name="Pho Saigon", cuisine_type="Vietnamese", area="Downtown Dubai",
         estimated_monthly_orders=445, avg_ticket_aed=76, google_rating=4.5, num_reviews=280,
         has_delivery=False, current_platform=None,
         owner_name="Linh Nguyen", owner_phone="+971 55 544 6677", owner_email="linh@phosaigon.ae"),
    dict(lead_id="lead_025", name="Al Reef Mandi", cuisine_type="Emirati", area="Deira",
         estimated_monthly_orders=820, avg_ticket_aed=58, google_rating=4.7, num_reviews=710,
         has_delivery=False, current_platform=None,
         owner_name="Abdullah Al Reef", owner_phone="+971 50 655 7788", owner_email="info@alreefmandi.ae"),
    dict(lead_id="lead_026", name="Thai Garden", cuisine_type="Thai", area="Al Barsha",
         estimated_monthly_orders=390, avg_ticket_aed=80, google_rating=4.4, num_reviews=245,
         has_delivery=False, current_platform=None,
         owner_name="Somchai Wongsri", owner_phone="+971 55 766 8899", owner_email="somchai@thaigarden.ae"),
    dict(lead_id="lead_027", name="Persia Palace", cuisine_type="Persian", area="Business Bay",
         estimated_monthly_orders=470, avg_ticket_aed=95, google_rating=4.5, num_reviews=330,
         has_delivery=True, current_platform="Noon Food",
         owner_name="Dariush Ahmadi", owner_phone="+971 50 877 9900", owner_email="dariush@persiapalace.ae"),
    dict(lead_id="lead_028", name="Ramen Kaito", cuisine_type="Japanese", area="Discovery Gardens",
         estimated_monthly_orders=290, avg_ticket_aed=82, google_rating=4.6, num_reviews=175,
         has_delivery=False, current_platform=None,
         owner_name="Kaito Yamamoto", owner_phone="+971 55 988 0011", owner_email="kaito@ramenkaito.ae"),
    dict(lead_id="lead_029", name="Casa Manila", cuisine_type="Filipino", area="Silicon Oasis",
         estimated_monthly_orders=510, avg_ticket_aed=62, google_rating=4.3, num_reviews=390,
         has_delivery=False, current_platform=None,
         owner_name="Maria Santos", owner_phone="+971 50 099 1122", owner_email="maria@casamanila.ae"),
    dict(lead_id="lead_030", name="Beirut By Night", cuisine_type="Lebanese", area="DIFC",
         estimated_monthly_orders=350, avg_ticket_aed=130, google_rating=4.7, num_reviews=220,
         has_delivery=False, current_platform=None,
         owner_name="Nader Khalil", owner_phone="+971 55 100 2233", owner_email="nader@beirutbynight.ae"),
    dict(lead_id="lead_031", name="Tandoori Tales", cuisine_type="Indian", area="Jumeirah",
         estimated_monthly_orders=430, avg_ticket_aed=88, google_rating=4.4, num_reviews=305,
         has_delivery=True, current_platform="Keeta",
         owner_name="Priya Mehta", owner_phone="+971 50 211 3345", owner_email="priya@tandooritales.ae"),
    dict(lead_id="lead_032", name="Dragon Palace", cuisine_type="Chinese", area="Bur Dubai",
         estimated_monthly_orders=680, avg_ticket_aed=74, google_rating=4.2, num_reviews=480,
         has_delivery=True, current_platform="Deliveroo",
         owner_name="Wei Zhang", owner_phone="+971 55 322 4456", owner_email="wei@dragonpalace.ae"),
    dict(lead_id="lead_033", name="La Cantine", cuisine_type="Italian", area="Business Bay",
         estimated_monthly_orders=390, avg_ticket_aed=110, google_rating=4.6, num_reviews=260,
         has_delivery=False, current_platform=None,
         owner_name="Marco Ricci", owner_phone="+971 50 433 5567", owner_email="marco@lacantine.ae"),
    dict(lead_id="lead_034", name="Smoke & Oak BBQ", cuisine_type="American", area="Silicon Oasis",
         estimated_monthly_orders=470, avg_ticket_aed=92, google_rating=4.5, num_reviews=315,
         has_delivery=False, current_platform=None,
         owner_name="Jake Turner", owner_phone="+971 55 544 6678", owner_email="jake@smokeoak.ae"),
    dict(lead_id="lead_035", name="Kimchi Republic", cuisine_type="Korean", area="JBR",
         estimated_monthly_orders=320, avg_ticket_aed=78, google_rating=4.4, num_reviews=195,
         has_delivery=False, current_platform=None,
         owner_name="Soo-Jin Lee", owner_phone="+971 50 655 7789", owner_email="soojin@kimchirepublic.ae"),
    dict(lead_id="lead_036", name="Empanada House", cuisine_type="Mexican", area="Al Barsha",
         estimated_monthly_orders=350, avg_ticket_aed=65, google_rating=4.3, num_reviews=220,
         has_delivery=False, current_platform=None,
         owner_name="Sofia Reyes", owner_phone="+971 55 766 8890", owner_email="sofia@empanadahouse.ae"),
    dict(lead_id="lead_037", name="Shwarma Hub", cuisine_type="Lebanese", area="Discovery Gardens",
         estimated_monthly_orders=760, avg_ticket_aed=48, google_rating=4.6, num_reviews=580,
         has_delivery=False, current_platform=None,
         owner_name="Bassam Turki", owner_phone="+971 50 877 9901", owner_email="bassam@shwarmahub.ae"),
    dict(lead_id="lead_038", name="Udon World", cuisine_type="Japanese", area="Jumeirah",
         estimated_monthly_orders=310, avg_ticket_aed=88, google_rating=4.5, num_reviews=185,
         has_delivery=False, current_platform=None,
         owner_name="Hiroshi Tanaka", owner_phone="+971 55 988 0012", owner_email="hiroshi@udonworld.ae"),
    dict(lead_id="lead_039", name="Pakwan Express", cuisine_type="Pakistani", area="Palm Jumeirah",
         estimated_monthly_orders=290, avg_ticket_aed=72, google_rating=4.3, num_reviews=210,
         has_delivery=True, current_platform="Careem Food",
         owner_name="Imran Qureshi", owner_phone="+971 50 099 1123", owner_email="imran@pakwanexpress.ae"),
    dict(lead_id="lead_040", name="Mama Africa Kitchen", cuisine_type="Emirati", area="Bur Dubai",
         estimated_monthly_orders=410, avg_ticket_aed=60, google_rating=4.4, num_reviews=295,
         has_delivery=False, current_platform=None,
         owner_name="Fatima Al Marri", owner_phone="+971 55 100 2234", owner_email="fatima@mamaafrica.ae"),
    dict(lead_id="lead_041", name="Pad Thai Corner", cuisine_type="Thai", area="DIFC",
         estimated_monthly_orders=280, avg_ticket_aed=98, google_rating=4.5, num_reviews=165,
         has_delivery=False, current_platform=None,
         owner_name="Arisa Pongpat", owner_phone="+971 50 211 3346", owner_email="arisa@padthaicorner.ae"),
    dict(lead_id="lead_042", name="Char Siu Noodles", cuisine_type="Chinese", area="Dubai Marina",
         estimated_monthly_orders=360, avg_ticket_aed=82, google_rating=4.4, num_reviews=240,
         has_delivery=False, current_platform=None,
         owner_name="Tony Chan", owner_phone="+971 55 322 4457", owner_email="tony@charsiun.ae"),
    dict(lead_id="lead_043", name="Gulshan Biryani", cuisine_type="Pakistani", area="Jumeirah",
         estimated_monthly_orders=540, avg_ticket_aed=70, google_rating=4.6, num_reviews=445,
         has_delivery=False, current_platform=None,
         owner_name="Hassan Gulshan", owner_phone="+971 50 433 5568", owner_email="hassan@gulshan.ae"),
    dict(lead_id="lead_044", name="Filipino Fiesta", cuisine_type="Filipino", area="Al Barsha",
         estimated_monthly_orders=460, avg_ticket_aed=65, google_rating=4.3, num_reviews=330,
         has_delivery=True, current_platform="Noon Food",
         owner_name="Rosario Cruz", owner_phone="+971 55 544 6679", owner_email="rosario@filipinofiesta.ae"),
    dict(lead_id="lead_045", name="Khoresh House", cuisine_type="Persian", area="Deira",
         estimated_monthly_orders=390, avg_ticket_aed=78, google_rating=4.4, num_reviews=265,
         has_delivery=False, current_platform=None,
         owner_name="Reza Sadeghi", owner_phone="+971 50 655 7790", owner_email="reza@khoreshhouse.ae"),
    dict(lead_id="lead_046", name="Little Tokyo Ramen", cuisine_type="Japanese", area="Business Bay",
         estimated_monthly_orders=340, avg_ticket_aed=92, google_rating=4.6, num_reviews=210,
         has_delivery=False, current_platform=None,
         owner_name="Yuki Sato", owner_phone="+971 55 766 8891", owner_email="yuki@littletokyo.ae"),
    dict(lead_id="lead_047", name="Masala Bay", cuisine_type="Indian", area="Silicon Oasis",
         estimated_monthly_orders=480, avg_ticket_aed=68, google_rating=4.4, num_reviews=360,
         has_delivery=False, current_platform=None,
         owner_name="Rohit Sharma", owner_phone="+971 50 877 9902", owner_email="rohit@masalabay.ae"),
    dict(lead_id="lead_048", name="Viet Pho House", cuisine_type="Vietnamese", area="Bur Dubai",
         estimated_monthly_orders=370, avg_ticket_aed=70, google_rating=4.5, num_reviews=240,
         has_delivery=False, current_platform=None,
         owner_name="Tuan Pham", owner_phone="+971 55 988 0013", owner_email="tuan@vietphohouse.ae"),
    dict(lead_id="lead_049", name="Smash & Stack", cuisine_type="American", area="Palm Jumeirah",
         estimated_monthly_orders=560, avg_ticket_aed=105, google_rating=4.5, num_reviews=385,
         has_delivery=True, current_platform="Deliveroo",
         owner_name="Ryan Collins", owner_phone="+971 50 099 1124", owner_email="ryan@smashstack.ae"),
    dict(lead_id="lead_050", name="Golden Wok", cuisine_type="Chinese", area="Downtown Dubai",
         estimated_monthly_orders=490, avg_ticket_aed=88, google_rating=4.3, num_reviews=310,
         has_delivery=True, current_platform="Keeta",
         owner_name="Ling Wei", owner_phone="+971 55 100 2235", owner_email="ling@goldenwok.ae"),
]

_extra_leads_index: int = 0  # tracks which pool entry to serve next


def mark_lead_converted(lead_id: str) -> None:
    """Mark a lead as converted so it is excluded from get_leads() output."""
    _converted_lead_ids.add(lead_id)


def add_batch_leads(n: int = 10) -> int:
    """Append the next *n* leads from the extra pool to the live leads list.

    Cycles through the pool if exhausted.  Returns the count actually added
    (may be < n if the pool is smaller than n).
    """
    global _extra_leads_index, _leads_cache
    if _leads_cache is None:
        get_leads()  # ensure cache is initialised

    pool_size = len(_EXTRA_LEADS_POOL)
    if pool_size == 0:
        return 0

    added = 0
    for _ in range(n):
        entry = _EXTRA_LEADS_POOL[_extra_leads_index % pool_size]
        _extra_leads_index += 1
        # Avoid duplicates — skip if lead_id already in cache
        existing_ids = {l.lead_id for l in _leads_cache}
        if entry["lead_id"] not in existing_ids:
            _leads_cache.append(RestaurantLead(**entry))
            added += 1
        elif pool_size <= n:
            break  # entire pool exhausted and all already added

    return added

# ---------------------------------------------------------------------------
# Runtime registries — populated by the UI layer (no Streamlit import needed)
# These allow agent tool calls to resolve dynamically created partners.
# ---------------------------------------------------------------------------

_runtime_partners: dict[str, "RestaurantPartner"] = {}    # converted leads (status="new")
_graduated_partners: dict[str, "RestaurantPartner"] = {}  # partners marked as live


def register_runtime_partner(partner: "RestaurantPartner") -> None:
    """Register a partner created from a converted lead so agents can resolve it."""
    _runtime_partners[partner.partner_id] = partner


def register_graduated_partner(partner: "RestaurantPartner") -> None:
    """Register a graduated (live) partner so the retention agent can see it."""
    _graduated_partners[partner.partner_id] = partner


def get_graduated_partners() -> list["RestaurantPartner"]:
    """Return all partners that have been marked as live this session."""
    return list(_graduated_partners.values())


def get_leads() -> list[RestaurantLead]:
    global _leads_cache
    if _leads_cache is None:
        _leads_cache = [RestaurantLead(**d) for d in _LEADS_RAW]
    # Filter out leads that have been converted to partners this session
    return [l for l in _leads_cache if l.lead_id not in _converted_lead_ids]


def get_partners() -> list[RestaurantPartner]:
    global _partners_cache
    if _partners_cache is None:
        _partners_cache = [RestaurantPartner(**d) for d in _PARTNERS_RAW]
    return _partners_cache


def get_lead_by_id(lead_id: str) -> RestaurantLead | None:
    return next((l for l in get_leads() if l.lead_id == lead_id), None)


def get_partner_by_id(partner_id: str) -> RestaurantPartner | None:
    result = next((p for p in get_partners() if p.partner_id == partner_id), None)
    if result:
        return result
    # Fall back to runtime registries for dynamically created/graduated partners
    return _runtime_partners.get(partner_id) or _graduated_partners.get(partner_id)
