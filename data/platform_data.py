"""
Existing talabat platform restaurant data (simulated for demo purposes).

Used for:
  1. Competition density scoring in lead scoring (sales_tools.py)
  2. Coverage heatmap on the Sales tab
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Dubai area lat/lon centroids (approximate)
# ---------------------------------------------------------------------------
AREA_COORDS: dict[str, tuple[float, float]] = {
    "JBR":               (25.0777, 55.1302),
    "Dubai Marina":      (25.0802, 55.1390),
    "DIFC":              (25.2131, 55.2796),
    "Downtown Dubai":    (25.1972, 55.2744),
    "Business Bay":      (25.1866, 55.2611),
    "Deira":             (25.2698, 55.3246),
    "Bur Dubai":         (25.2532, 55.2988),
    "Al Barsha":         (25.1126, 55.1938),
    "Discovery Gardens": (25.0348, 55.1548),
    "Silicon Oasis":     (25.1186, 55.3804),
    "Jumeirah":          (25.2152, 55.2388),
    "Palm Jumeirah":     (25.1124, 55.1390),
}

# ---------------------------------------------------------------------------
# Restaurants already live on talabat (simulated platform data)
# Spread across 12 areas and 14 cuisines to create realistic density gaps.
# ---------------------------------------------------------------------------
PLATFORM_RESTAURANTS: list[dict] = [
    # JBR — Italian, American, Japanese saturated
    {"name": "Bella Napoli",          "cuisine_type": "Italian",   "area": "JBR"},
    {"name": "The Burger Lab",        "cuisine_type": "American",  "area": "JBR"},
    {"name": "Sakura Bites",          "cuisine_type": "Japanese",  "area": "JBR"},
    {"name": "Ocean Grill",           "cuisine_type": "American",  "area": "JBR"},
    {"name": "Pasta Fresca",          "cuisine_type": "Italian",   "area": "JBR"},

    # Dubai Marina — Japanese, Korean, American strong
    {"name": "Sushi Garden",          "cuisine_type": "Japanese",  "area": "Dubai Marina"},
    {"name": "Seoul Kitchen",         "cuisine_type": "Korean",    "area": "Dubai Marina"},
    {"name": "Marina Burgers",        "cuisine_type": "American",  "area": "Dubai Marina"},
    {"name": "Chopsticks Express",    "cuisine_type": "Chinese",   "area": "Dubai Marina"},
    {"name": "K-BBQ House",           "cuisine_type": "Korean",    "area": "Dubai Marina"},

    # DIFC — Japanese, Italian, high-ticket
    {"name": "Nobu Next Door",        "cuisine_type": "Japanese",  "area": "DIFC"},
    {"name": "Cipriani",              "cuisine_type": "Italian",   "area": "DIFC"},
    {"name": "Zuma Lite",             "cuisine_type": "Japanese",  "area": "DIFC"},

    # Downtown Dubai — American, Indian, Italian
    {"name": "Cheesecake Bistro",     "cuisine_type": "American",  "area": "Downtown Dubai"},
    {"name": "Punjabi Dhaba",         "cuisine_type": "Indian",    "area": "Downtown Dubai"},
    {"name": "Trattoria Downtown",    "cuisine_type": "Italian",   "area": "Downtown Dubai"},
    {"name": "Spice Route",           "cuisine_type": "Indian",    "area": "Downtown Dubai"},

    # Business Bay — Indian, Pakistani, American
    {"name": "Karachi Darbar Bay",    "cuisine_type": "Pakistani", "area": "Business Bay"},
    {"name": "Curry House",           "cuisine_type": "Indian",    "area": "Business Bay"},
    {"name": "Bay Burgers",           "cuisine_type": "American",  "area": "Business Bay"},
    {"name": "Biryani Bros",          "cuisine_type": "Pakistani", "area": "Business Bay"},

    # Deira — Indian, Pakistani, Filipino saturated
    {"name": "Golden Dosa",           "cuisine_type": "Indian",    "area": "Deira"},
    {"name": "Lahore Tikka House",    "cuisine_type": "Pakistani", "area": "Deira"},
    {"name": "Manila Express",        "cuisine_type": "Filipino",  "area": "Deira"},
    {"name": "Bombay Palace",         "cuisine_type": "Indian",    "area": "Deira"},
    {"name": "Pinoy Kitchen",         "cuisine_type": "Filipino",  "area": "Deira"},
    {"name": "Karachi Nights",        "cuisine_type": "Pakistani", "area": "Deira"},

    # Bur Dubai — Indian, Pakistani, Lebanese
    {"name": "Kebab & More",          "cuisine_type": "Lebanese",  "area": "Bur Dubai"},
    {"name": "Dum Biryani House",     "cuisine_type": "Indian",    "area": "Bur Dubai"},
    {"name": "Peshwari Flavours",     "cuisine_type": "Pakistani", "area": "Bur Dubai"},

    # Al Barsha — Indian, American, Korean
    {"name": "Barsha Grill",          "cuisine_type": "American",  "area": "Al Barsha"},
    {"name": "Spice of India",        "cuisine_type": "Indian",    "area": "Al Barsha"},
    {"name": "K-Street Barsha",       "cuisine_type": "Korean",    "area": "Al Barsha"},

    # Discovery Gardens — Filipino, Indian (underserved for other cuisines)
    {"name": "Kubo Restaurant",       "cuisine_type": "Filipino",  "area": "Discovery Gardens"},
    {"name": "Tindahan ni Aling",     "cuisine_type": "Filipino",  "area": "Discovery Gardens"},
    {"name": "Garden Biryani",        "cuisine_type": "Indian",    "area": "Discovery Gardens"},

    # Silicon Oasis — Indian, Pakistani (tech workers; American/Korean gap)
    {"name": "Oasis Grill",           "cuisine_type": "Indian",    "area": "Silicon Oasis"},
    {"name": "Tech Park Karahi",      "cuisine_type": "Pakistani", "area": "Silicon Oasis"},

    # Jumeirah — Lebanese, Italian (Western and Lebanese presence)
    {"name": "Baalbeck Express",      "cuisine_type": "Lebanese",  "area": "Jumeirah"},
    {"name": "Fratello",              "cuisine_type": "Italian",   "area": "Jumeirah"},
    {"name": "Mezze & Co",            "cuisine_type": "Lebanese",  "area": "Jumeirah"},

    # Palm Jumeirah — Japanese, Italian, American (premium areas)
    {"name": "Nobu Palm",             "cuisine_type": "Japanese",  "area": "Palm Jumeirah"},
    {"name": "Aqua by the Sea",       "cuisine_type": "American",  "area": "Palm Jumeirah"},
    {"name": "La Piazza Palm",        "cuisine_type": "Italian",   "area": "Palm Jumeirah"},
]


def get_competition_count(area: str, cuisine_type: str) -> int:
    """Return the number of same-cuisine restaurants already on talabat in the given area."""
    return sum(
        1 for r in PLATFORM_RESTAURANTS
        if r["area"] == area and r["cuisine_type"] == cuisine_type
    )
