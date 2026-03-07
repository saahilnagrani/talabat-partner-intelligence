"""
Talabat platform restaurant data (programmatically generated, seeded for reproducibility).

Used for:
  1. Competition density scoring in lead scoring (sales_tools.py)
  2. Coverage heatmap on the Sales tab
  3. Full RestaurantPartner objects for the Retention tab portfolio
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Dubai area lat/lon centroids (approximate)
# ---------------------------------------------------------------------------
AREA_COORDS: dict[str, tuple[float, float]] = {
    "JBR":                   (25.0777, 55.1302),
    "Dubai Marina":          (25.0802, 55.1390),
    "DIFC":                  (25.2131, 55.2796),
    "Downtown Dubai":        (25.1972, 55.2744),
    "Business Bay":          (25.1866, 55.2611),
    "Deira":                 (25.2698, 55.3246),
    "Bur Dubai":             (25.2532, 55.2988),
    "Al Barsha":             (25.1126, 55.1938),
    "Discovery Gardens":     (25.0348, 55.1548),
    "Silicon Oasis":         (25.1186, 55.3804),
    "Jumeirah":              (25.2152, 55.2388),
    "Jumeirah Lake Towers":  (25.0693, 55.1408),
    "Palm Jumeirah":         (25.1124, 55.1390),
}

# ---------------------------------------------------------------------------
# Name-building blocks
# ---------------------------------------------------------------------------
_SUFFIXES: list[str] = [
    "Kitchen", "House", "Grill", "Express", "Palace", "Corner",
    "Bites", "Lounge", "Cafe", "Restaurant", "Diner", "Spot",
    "Hub", "Bar & Grill", "Eatery",
]

_CUISINE_PREFIXES: dict[str, list[str]] = {
    "Lebanese":   ["Beirut", "Cedar", "Salam", "Levant", "Al Shouf", "Tripoli",
                   "Al Balad", "Byblos", "Phoenicia", "Tyre", "Al Hamra", "Fakhreddine"],
    "Indian":     ["Bombay", "Delhi", "Spice", "Masala", "Taj", "Punjab",
                   "Goa", "Rajasthan", "Kerala", "Mumbai", "Amritsar", "Jaipur"],
    "Pakistani":  ["Karachi", "Lahore", "Islamabad", "Peshawar", "Multan",
                   "Rawalpindi", "Quetta", "Sialkot", "Al Habib", "Pak"],
    "Italian":    ["Napoli", "Roma", "Milano", "Venezia", "Firenze", "Sicilia",
                   "Torino", "Bologna", "La Stella", "Trattoria", "Osteria", "Bella"],
    "American":   ["Brooklyn", "Texas", "Liberty", "All-Star", "Classic",
                   "Big Easy", "Smokehouse", "Grill Masters", "Freedom", "Brew & Bite"],
    "Japanese":   ["Sakura", "Kyoto", "Tokyo", "Osaka", "Sushi", "Ramen",
                   "Wasabi", "Zen", "Fuji", "Edo", "Namba", "Shibuya"],
    "Korean":     ["Seoul", "Busan", "Gangnam", "K-Street", "Hangang",
                   "Incheon", "Daegu", "Jeju", "K-BBQ", "Hongdae"],
    "Filipino":   ["Pinoy", "Manila", "Cebu", "Davao", "Tindahan", "Kubo",
                   "Lutong", "Maynila", "Mindanao", "Tagalog"],
    "Chinese":    ["Dragon", "Jade", "Golden", "Chopsticks", "Wok", "Panda",
                   "Shanghai", "Beijing", "Chengdu", "Canton", "Orient"],
    "Thai":       ["Bangkok", "Chiang Mai", "Thai Orchid", "Lotus", "Siam",
                   "Phuket", "Pad Thai", "Jasmine", "Mango", "Sukhothai"],
    "Vietnamese": ["Saigon", "Hanoi", "Pho", "Ho Chi Minh", "Hue", "Da Nang",
                   "Lemongrass", "Bun Bo", "Banh Mi", "Vietnam"],
    "Mexican":    ["Cancun", "Aztec", "Taco", "Fiesta", "Jalisco", "Oaxaca",
                   "Puebla", "Mariachi", "Hacienda", "Amigo"],
    "Persian":    ["Tehran", "Shiraz", "Isfahan", "Tabriz", "Kebab", "Persia",
                   "Safavid", "Chelo", "Dizi", "Al Irani"],
    "Emirati":    ["Al Fanar", "Damask", "Bait Al", "Harees", "Majlis",
                   "Rigag", "Aseeda", "Luqaimat", "Al Arabi", "Karak"],
}

# ---------------------------------------------------------------------------
# Area targets and cuisine distributions
# ---------------------------------------------------------------------------
_AREA_TARGET_COUNTS: dict[str, int] = {
    "Deira":                130,
    "Bur Dubai":            105,
    "Business Bay":          95,
    "Dubai Marina":          90,
    "Jumeirah Lake Towers":  85,
    "Downtown Dubai":        80,
    "Al Barsha":             80,
    "Jumeirah":              75,
    "JBR":                   70,
    "Silicon Oasis":         60,
    "Discovery Gardens":     60,
    "DIFC":                  55,
    "Palm Jumeirah":         45,
}

_AREA_CUISINE_WEIGHTS: dict[str, dict[str, int]] = {
    "Deira": {
        "Indian": 30, "Pakistani": 25, "Filipino": 15, "Lebanese": 10,
        "Chinese": 8, "American": 5, "Italian": 4, "Japanese": 3,
    },
    "Bur Dubai": {
        "Indian": 28, "Pakistani": 22, "Lebanese": 15, "Filipino": 12,
        "American": 8, "Chinese": 8, "Italian": 4, "Korean": 3,
    },
    "Business Bay": {
        "Indian": 20, "Pakistani": 18, "American": 18, "Italian": 15,
        "Lebanese": 10, "Japanese": 10, "Korean": 5, "Thai": 4,
    },
    "Dubai Marina": {
        "Japanese": 18, "Korean": 15, "American": 15, "Italian": 14,
        "Lebanese": 10, "Chinese": 10, "Thai": 8, "Vietnamese": 5, "Filipino": 5,
    },
    "Jumeirah Lake Towers": {
        "Indian": 18, "American": 16, "Italian": 15, "Lebanese": 14,
        "Korean": 12, "Japanese": 10, "Pakistani": 8, "Chinese": 7,
    },
    "Downtown Dubai": {
        "Italian": 20, "American": 18, "Indian": 15, "Japanese": 12,
        "Lebanese": 10, "Korean": 8, "Thai": 7, "Persian": 5, "Emirati": 5,
    },
    "Al Barsha": {
        "Indian": 22, "American": 18, "Korean": 12, "Filipino": 12,
        "Pakistani": 10, "Lebanese": 10, "Chinese": 8, "Thai": 8,
    },
    "Jumeirah": {
        "Lebanese": 22, "Italian": 18, "American": 14, "Japanese": 12,
        "Thai": 10, "Emirati": 8, "Persian": 8, "Vietnamese": 8,
    },
    "JBR": {
        "Italian": 22, "American": 20, "Japanese": 15, "Lebanese": 12,
        "Korean": 10, "Thai": 8, "Mexican": 7, "Vietnamese": 6,
    },
    "Silicon Oasis": {
        "Indian": 28, "Pakistani": 22, "American": 15, "Korean": 12,
        "Filipino": 10, "Chinese": 8, "Lebanese": 5,
    },
    "Discovery Gardens": {
        "Filipino": 30, "Indian": 25, "Pakistani": 20,
        "Vietnamese": 10, "Chinese": 8, "Lebanese": 7,
    },
    "DIFC": {
        "Japanese": 22, "Italian": 20, "American": 15, "Lebanese": 12,
        "Korean": 10, "Thai": 8, "Persian": 8, "Emirati": 5,
    },
    "Palm Jumeirah": {
        "Japanese": 22, "Italian": 20, "American": 18, "Lebanese": 12,
        "Korean": 10, "Thai": 8, "Emirati": 5, "Mexican": 5,
    },
}


# ---------------------------------------------------------------------------
# PLATFORM_RESTAURANTS — generated once, deterministic (seed=42)
# ---------------------------------------------------------------------------

def _build_platform_restaurants() -> list[dict]:
    """Generate ~1030 restaurant entries deterministically, each with a lat/lon."""
    import random as _r
    rng = _r.Random(42)
    entries: list[dict] = []
    seen_names: set[str] = set()

    for area, target in _AREA_TARGET_COUNTS.items():
        lat_c, lon_c = AREA_COORDS[area]   # area centroid
        weights_map = _AREA_CUISINE_WEIGHTS.get(area, {})
        cuisine_pool = [c for c, w in weights_map.items() for _ in range(w)]
        for i in range(target):
            cuisine = rng.choice(cuisine_pool)
            prefix  = rng.choice(_CUISINE_PREFIXES.get(cuisine, ["Local"]))
            suffix  = rng.choice(_SUFFIXES)
            name    = f"{prefix} {suffix}"
            if name in seen_names:
                name = f"{prefix} {suffix} {area.split()[0]}"
            if name in seen_names:
                name = f"{name} {i + 1}"
            seen_names.add(name)

            # Spread each restaurant within ±1.5 km of its area centroid.
            # 1° lat ≈ 111 km  →  ±0.0135°   (using ±0.027° total range)
            # 1° lon ≈  98 km  →  ±0.0153°   (using ±0.031° total range at Dubai lat)
            h_lat = int(hashlib.md5(f"{name}_lat".encode()).hexdigest()[:4], 16)  # 0–65535
            h_lon = int(hashlib.md5(f"{name}_lon".encode()).hexdigest()[:4], 16)
            lat   = round(lat_c + (h_lat / 65535 - 0.5) * 0.027, 5)
            lon   = round(lon_c + (h_lon / 65535 - 0.5) * 0.031, 5)

            entries.append({
                "name": name, "cuisine_type": cuisine, "area": area,
                "lat": lat, "lon": lon,
            })

    return entries


PLATFORM_RESTAURANTS: list[dict] = _build_platform_restaurants()


# ---------------------------------------------------------------------------
# Helper: competition density (used by sales_tools.py)
# ---------------------------------------------------------------------------

def get_competition_count(area: str, cuisine_type: str) -> int:
    """Return the number of same-cuisine restaurants already on talabat in the given area."""
    return sum(
        1 for r in PLATFORM_RESTAURANTS
        if r["area"] == area and r["cuisine_type"] == cuisine_type
    )


# ---------------------------------------------------------------------------
# get_platform_partners — full RestaurantPartner objects for Retention tab
# ---------------------------------------------------------------------------

_ACCOUNT_MANAGERS: list[str] = [
    "Sarah Al-Rashid", "Mohammed Hadi", "Priya Sharma",
    "James O'Brien",   "Fatima Al-Zaabi", "Ravi Krishnan",
]


def _det(seed: str, lo: float, hi: float) -> float:
    """Deterministic float in [lo, hi] derived from seed string via MD5."""
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    return lo + (h / 0xFFFFFFFF) * (hi - lo)


def _det_int(seed: str, lo: int, hi: int) -> int:
    return int(_det(seed, lo, hi))


_PLATFORM_PARTNERS_CACHE: list | None = None


def get_platform_partners() -> list:
    """Return a list of RestaurantPartner objects for every PLATFORM_RESTAURANTS entry.

    Data is generated deterministically from each restaurant's name+area+index seed,
    so the same partners are returned on every app restart.
    Cached after first call.
    """
    global _PLATFORM_PARTNERS_CACHE
    if _PLATFORM_PARTNERS_CACHE is not None:
        return _PLATFORM_PARTNERS_CACHE

    # Import here to avoid circular import at module level
    from data.models import RestaurantPartner  # noqa: PLC0415

    base_date = datetime(2022, 1, 1)
    partners = []

    for i, r in enumerate(PLATFORM_RESTAURANTS):
        s = f"{r['name']}_{r['area']}_{i}"   # unique seed per entry

        monthly_orders = _det_int(s + "_ord", 60, 1400)
        avg_ticket     = round(_det(s + "_tkt", 35.0, 180.0), 1)
        gmv            = round(monthly_orders * avg_ticket, 0)
        rating         = round(_det(s + "_rat", 3.2, 5.0), 1)
        completion     = round(_det(s + "_cmp", 88.0, 99.5), 1)
        trend          = round(_det(s + "_trn", -35.0, 30.0), 1)
        days_login     = _det_int(s + "_lgn", 0, 60)
        tickets        = _det_int(s + "_tkt2", 0, 8)
        menu_items     = _det_int(s + "_mnu", 8, 80)
        days_joined    = _det_int(s + "_jnd", 30, 1100)
        joined_date    = base_date + timedelta(days=days_joined)

        promo_roll = _det(s + "_prm", 0.0, 1.0)
        if promo_roll < 0.4:
            last_promo = None
        else:
            last_promo = datetime.now() - timedelta(days=_det_int(s + "_prd", 3, 120))

        mgr_idx = _det_int(s + "_mgr", 0, len(_ACCOUNT_MANAGERS) - 1)

        # Derive status by approximating the 5-signal health score
        health = (
            max(0.0, min(35.0, 35.0 * (1.0 - abs(min(trend, 0.0)) / 35.0)))    +
            max(0.0, min(20.0, (completion - 85.0) / 15.0 * 20.0))              +
            max(0.0, min(20.0, max(0.0, (30.0 - days_login) / 30.0 * 20.0)))   +
            max(0.0, min(15.0, (1.0 - tickets / 8.0) * 15.0))                   +
            (0.0 if last_promo is None else 10.0)
        )
        if health < 28:
            status = "critical"
        elif health < 52:
            status = "at_risk"
        else:
            status = "healthy"

        partners.append(RestaurantPartner(
            partner_id           = f"plat_{i:04d}",
            name                 = r["name"],
            cuisine_type         = r["cuisine_type"],
            area                 = r["area"],
            joined_date          = joined_date,
            monthly_orders       = monthly_orders,
            avg_ticket_aed       = avg_ticket,
            completion_rate      = completion,
            rating               = rating,
            active_menu_items    = menu_items,
            last_promo_date      = last_promo,
            account_manager      = _ACCOUNT_MANAGERS[mgr_idx],
            orders_trend_pct     = trend,
            days_since_login     = days_login,
            support_tickets_open = tickets,
            gmv_aed_last_30d     = gmv,
            status               = status,
            source_lead_id       = None,
            recently_onboarded   = False,
        ))

    _PLATFORM_PARTNERS_CACHE = partners
    return partners
