"""System prompt, TinyFish goal templates, and default platform URLs."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Default rental platform URLs (used when frontend provides none)
# ---------------------------------------------------------------------------

DEFAULT_PLATFORM_URLS: list[str] = [
    "https://www.nhatot.com/thue-phong-tro",
    "https://batdongsan.com.vn/cho-thue",
]

# ---------------------------------------------------------------------------
# System prompt for the main claw agent
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
## RentAgent VN — AI-Powered Rental Assistant

You are an expert rental assistant for the Vietnamese market. You help users \
find apartments, rooms, and houses for rent across Vietnam — primarily in \
Ho Chi Minh City and Hanoi.

### What you can do
- **Search listings** across multiple platforms using the `search_rentals` tool.
- **Research neighbourhoods** using `research_area` (safety, amenities, reviews).
- **Draft landlord messages** via `contact_landlord` (stub — tells the user \
  how to reach the landlord directly with phone/Zalo).
- **Schedule recurring scans** via the built-in cron tool.

### How `search_rentals` works
- You provide a natural-language `query` describing what the user wants.
- The tool automatically searches across all configured platform URLs.
- Keep the query focused: describe the property (area, bedrooms, budget, \
  special requirements) in plain Vietnamese or English.
- If the user mentions preferences during conversation (e.g. "I prefer high \
  floors" or "must have a balcony"), pass these as the `user_preference` \
  parameter so results are filtered better.
- **The tool runs in the background** — it returns immediately with a job ID. \
  Results are delivered to this chat automatically when ready (typically \
  3–8 minutes). After calling the tool, let the user know that results \
  are on the way and they can continue chatting in the meantime.

### Vietnamese rental market context
- Prices are in VND per month. Common shorthand:
  - "5 trieu" or "5tr" = 5,000,000 VND/month
  - "15 trieu" = 15,000,000 VND/month
- Deposits are typically 1-3 months rent.
- Major cities: Ho Chi Minh City (Saigon), Hanoi, Da Nang.
- Districts: "Quan 1", "Quan 7", "Binh Thanh", "Thu Duc", "Ba Dinh", etc.
- Common platforms: nhatot.com, batdongsan.com.vn, Facebook rental groups.

### How to present results
- Show a **ranked shortlist** (top 5-8 listings), not a raw data dump.
- For each listing include: title, price, location, size, bedrooms, and \
  landlord contact (phone/Zalo).
- Highlight listings that match the user's stated and inferred preferences.
- If landlord contact info is available, show it directly — the user can \
  reach out via Zalo (https://zalo.me/<phone>) or phone.

### Important
- Do NOT invent or fabricate listings. Only present data returned by tools.
- If no listings match, say so honestly and suggest broadening criteria.
- When the user provides URLs (Facebook groups, forum links), note that \
  those URLs are configured at the platform level — your job is to write \
  a good search query.
"""

# ---------------------------------------------------------------------------
# TinyFish goal templates — used by the scrape workflow to build goals
# per-platform. The {query} and {user_preference} placeholders are filled
# at runtime.
# ---------------------------------------------------------------------------

LISTING_SCHEMA_SAMPLE = """\
## Output format

Return ONLY a JSON object — no markdown fences, no explanation, no extra text.

The top-level key MUST be "listings" (not "rentals", "results", "data", or \
anything else). Use ONLY the exact field names shown below.

Example (one listing):

{"listings": [{
  "title": "2PN ban công · Q7 · 12tr/tháng",
  "description": "Căn hộ 2 phòng ngủ, 1 WC, có ban công thoáng mát, full nội thất, gần Lotte Mart",
  "price_vnd": 12000000.0,
  "price_display": "12 triệu/tháng",
  "deposit_vnd": 24000000.0,
  "address": "123 Nguyễn Hữu Thọ, Quận 7, TP.HCM",
  "district": "Quan 7",
  "city": "Ho Chi Minh",
  "area_sqm": 65.0,
  "bedrooms": 2,
  "bathrooms": 1,
  "listing_url": "https://example.com/listing/123",
  "thumbnail_url": "https://example.com/img.jpg",
  "posted_date": "2026-02-28",
  "source_platform": "nhatot.com",
  "landlord_name": "Anh Minh",
  "landlord_phone": "0901234567",
  "landlord_zalo": "0901234567",
  "landlord_facebook_url": "https://www.facebook.com/profile.php?id=100001234567",
  "landlord_contact_method": "phone,zalo"
}]}

Field guide (use these EXACT keys):
- title          : Short headline — room type · district · price (e.g. "Studio · Bình Thạnh · 4tr")
- description    : 1-2 sentence summary (size, furniture, notable features)
- price_vnd      : Monthly rent as float. Convert shorthand: 5tr = 5000000.0,
   15 triệu = 15000000.0. null if unknown
- price_display  : Price as written in the post (e.g. "5tr/tháng")
- deposit_vnd    : Deposit as float. null if not mentioned
- address        : Street address or location description
- district       : District name (e.g. "Binh Thanh", "Quan 7")
- city           : City name, default "Ho Chi Minh"
- area_sqm       : Area in m² as float. null if unknown
- bedrooms       : Number of bedrooms (integer). Extract from "1PN"=1, "2PN"=2. null if unknown
- bathrooms      : Number of bathrooms (integer). null if unknown
- listing_url    : Permalink to this specific post or listing page
- thumbnail_url  : First image URL. null if none
- posted_date    : Date posted (YYYY-MM-DD). null if unknown
- source_platform: "facebook", "nhatot.com", "batdongsan.com.vn", etc.
- landlord_name  : Name of the poster / landlord. null if unknown
- landlord_phone : Vietnamese mobile number (09xx/03xx/07xx/08xx/05xx). null if not found
- landlord_zalo  : Zalo number (often same as phone). null if not found
- landlord_facebook_url : Facebook profile URL of the poster. null if not available
- landlord_contact_method : Comma-separated — "phone", "zalo", "messenger"

CRITICAL RULES:
- If a value is unknown or not mentioned, set it to null. NEVER use \
placeholder text like "Không đề cập", "Chưa rõ", "N/A", or "Liên hệ".
- Do NOT add extra fields (no "id", "note", "group", "rooms", "contact", \
"location", "area", "price"). Use ONLY the field names listed above.
- Return valid JSON only."""


GOAL_FACEBOOK_GROUP = """\
## Objective
Extract rental listings from this Facebook group page.

## Context
User is looking for: {query}
{preference_line}

## Steps
1. Scroll down to load at least 15 posts.
2. For EACH post that IS a rental listing (skip discussions, questions, \
memes, and non-rental content), extract the listing details from the post text.
3. For each poster, capture their Facebook profile URL as landlord_facebook_url.

## Stop when ANY of these is true:
- You have extracted 15 rental listings.
- You have scrolled through 30 posts.
- No more content loads after scrolling.

## Guardrails
- Do NOT click on individual posts or navigate away from the group feed.
- Do NOT invent or fabricate any data not present in the post.
- Do NOT add extra fields not listed in the schema below.

## Edge cases
- If a post mentions price in shorthand (e.g. "5tr", "5 triệu"), convert: \
5tr = 5000000.0 for price_vnd, keep "5tr/tháng" for price_display.
- If a post contains multiple units at different prices, create one listing \
per unit.
- "1PN" means bedrooms=1, "2PN" means bedrooms=2, "Studio" means bedrooms=0.
- Most Facebook posts will NOT have all fields. Set missing fields to null. \
It is normal for thumbnail_url, deposit_vnd, area_sqm, bathrooms, and \
posted_date to be null for Facebook posts.

{schema_block}"""


GOAL_NHATOT = """\
## Objective
Search for rental listings on this Nha Tot page.

## Context
User is looking for: {query}
{preference_line}

## Steps
1. If there is a search box, type the search query. Otherwise, browse \
the current listing page.
2. Wait for results to load.
3. Extract the first 15 listings from the results page.

## Guardrails
- Do NOT click on individual listings — extract from the results page only.
- Do NOT add extra fields not listed in the schema below.
- Set source_platform to "nhatot.com" for all listings.

{schema_block}"""


GOAL_BATDONGSAN = """\
## Objective
Search for rental listings on this Bat Dong San page.

## Context
User is looking for: {query}
{preference_line}

## Steps
1. If there is a search/filter interface, use it to narrow down results.
2. Wait for results to load.
3. Extract the first 15 listings from the results.

## Guardrails
- Do NOT add extra fields not listed in the schema below.
- Set source_platform to "batdongsan.com.vn" for all listings.

{schema_block}"""


GOAL_GENERIC = """\
## Objective
Extract rental listings from this webpage.

## Context
User is looking for: {query}
{preference_line}

## Steps
1. Scroll down to load more content if the page uses infinite scroll.
2. Look for rental property listings. Extract up to 15 listings, then stop.

## Guardrails
- Do NOT add extra fields not listed in the schema below.

{schema_block}"""


# ---------------------------------------------------------------------------
# Helper to pick the right goal template for a URL
# ---------------------------------------------------------------------------

_DOMAIN_TEMPLATES: dict[str, str] = {
    "facebook.com": GOAL_FACEBOOK_GROUP,
    "fb.com": GOAL_FACEBOOK_GROUP,
    "nhatot.com": GOAL_NHATOT,
    "batdongsan.com.vn": GOAL_BATDONGSAN,
}


def build_goal(url: str, query: str, user_preference: str | None = None) -> str:
    """Build a TinyFish goal string for the given URL and user query.

    Selects the appropriate template based on domain and fills in
    placeholders.
    """
    from urllib.parse import urlparse

    domain = urlparse(url).hostname or ""
    domain = domain.removeprefix("www.").removeprefix("m.")

    template = GOAL_GENERIC
    for pattern, tmpl in _DOMAIN_TEMPLATES.items():
        if pattern in domain:
            template = tmpl
            break

    preference_line = ""
    if user_preference:
        preference_line = f"User preferences: {user_preference}"

    return template.format(
        query=query,
        preference_line=preference_line,
        schema_block=LISTING_SCHEMA_SAMPLE,
    )
