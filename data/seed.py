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
         google_rating=4.4, num_reviews=289, has_delivery=True, current_platform="Zomato",
         owner_name="Min-Ji Park", owner_phone="+971505234565", owner_email="minji@seoulbites.ae",
         notes="Korean BBQ and fried chicken. Frustrated with Zomato's customer service."),

    # Deira / Bur Dubai — high volume, budget-friendly
    dict(lead_id="lead_006", name="Karachi Darbar Express", cuisine_type="Pakistani",
         area="Bur Dubai", estimated_monthly_orders=780, avg_ticket_aed=42,
         google_rating=4.3, num_reviews=2341, has_delivery=True, current_platform=None,
         owner_name="Imran Qureshi", owner_phone="+971506234566", owner_email="imran@karachidarbar.ae",
         notes="Institution in Bur Dubai. No delivery at all — owner skeptical but open to conversation."),

    dict(lead_id="lead_007", name="Punjab Da Dhaba", cuisine_type="Indian",
         area="Deira", estimated_monthly_orders=920, avg_ticket_aed=38,
         google_rating=4.5, num_reviews=1834, has_delivery=True, current_platform="Zomato",
         owner_name="Gurpreet Singh", owner_phone="+971507234567", owner_email="gurpreet@punjabadhaba.ae",
         notes="Best butter chicken in Deira. On Zomato but wants better analytics. Huge review base."),

    dict(lead_id="lead_008", name="Spice of Persia", cuisine_type="Persian",
         area="Deira", estimated_monthly_orders=340, avg_ticket_aed=55,
         google_rating=4.4, num_reviews=456, has_delivery=False, current_platform=None,
         owner_name="Ali Tehrani", owner_phone="+971508234568", owner_email="ali@spiceofpersia.ae",
         notes="Family-run restaurant. No delivery presence. Very loyal dine-in crowd."),

    dict(lead_id="lead_009", name="Lahori Karahi House", cuisine_type="Pakistani",
         area="Bur Dubai", estimated_monthly_orders=650, avg_ticket_aed=38,
         google_rating=4.2, num_reviews=1456, has_delivery=True, current_platform="Zomato",
         owner_name="Zafar Iqbal", owner_phone="+971509234569", owner_email="zafar@lahorikarahi.ae",
         notes="24-hour restaurant. High late-night volume. Zomato order quality inconsistent."),

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
         google_rating=4.6, num_reviews=892, has_delivery=True, current_platform="Zomato",
         owner_name="Maria Santos", owner_phone="+971516234576", owner_email="maria@tasteofmanila.ae",
         notes="Huge Filipino expat community nearby. Zomato coverage inconsistent in this area."),

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
    "Zomato": {
        "commission_pct": 22,
        "platform_fee_aed": 0,
        "avg_delivery_time_min": 40,
        "analytics_dashboard": "Basic",
        "marketing_support": "Limited",
        "weaknesses": ["Smaller UAE customer base vs talabat", "Less brand trust in UAE", "Inconsistent delivery coverage", "Limited corporate ordering features"],
        "talabat_advantages": ["3x larger customer base in UAE", "Superior delivery logistics", "Corporate/B2B ordering platform", "Better analytics and insights", "Exclusive promotions on Ramadan/UAE events"],
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


def get_leads() -> list[RestaurantLead]:
    global _leads_cache
    if _leads_cache is None:
        _leads_cache = [RestaurantLead(**d) for d in _LEADS_RAW]
    return _leads_cache


def get_partners() -> list[RestaurantPartner]:
    global _partners_cache
    if _partners_cache is None:
        _partners_cache = [RestaurantPartner(**d) for d in _PARTNERS_RAW]
    return _partners_cache


def get_lead_by_id(lead_id: str) -> RestaurantLead | None:
    return next((l for l in get_leads() if l.lead_id == lead_id), None)


def get_partner_by_id(partner_id: str) -> RestaurantPartner | None:
    return next((p for p in get_partners() if p.partner_id == partner_id), None)
