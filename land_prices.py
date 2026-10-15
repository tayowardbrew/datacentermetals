"""
Granular land-price comparables, auto-detected from a drawn parcel's location.

Replaces the old five-bucket US-region dropdown with a lookup that resolves, in
order of preference:

  1. METRO / COUNTY tier -- a real, publicly-quoted data-center-land transaction
     $/acre for a named hotspot (Northern Virginia, Phoenix, Columbus, etc.).
     These are power-ready / entitled DC-land market figures.

  2. STATE tier -- USDA NASS 2025 farm real-estate value $/acre. This is a
     government-surveyed AGRICULTURAL figure used as an honest raw-land FLOOR /
     PROXY. It is NOT industrial or data-center land and will understate DC-ready
     land by a wide margin; it is labelled as such everywhere it surfaces.

  3. NATIONAL fallback -- the national industrial-land proxy, used only as a last
     resort where there is no state figure (Alaska, Hawaii and DC, which USDA does
     not survey) or for non-US coordinates. Always labelled with the actual state /
     county so the user still sees WHERE the parcel is.

The old generic directional buckets (northeast / south / midwest / west) have been
retired: a US parcel is now always described and benchmarked at STATE + COUNTY
(or district / parish / borough / independent city) level.

Every figure here has a real source documented in SOURCES.md (entries 6a / 6b).
Nothing is fabricated: the state table is the USDA NASS published table verbatim,
and the metro figures are quoted transactions from named trade-press articles.

The raw-vs-DC-land gap is enormous (Virginia farmland ~$6,100/acre vs Loudoun
County DC land ~$6.3M/acre in Nov 2025, ~1,000x). We therefore always expose
WHICH tier a figure came from so the UI can be honest about what it represents.
"""

from estimator import LAND_PRICE_USD_PER_ACRE
from geocode import state_abbr, US_STATE_NAMES

# --- STATE tier: USDA NASS 2025 farm real-estate value, USD/acre ---------------
# Source: USDA NASS, "Land Values 2025 Summary" (released 1 Aug 2025), table
# "Farm Real Estate Average Value per Acre - Regions, States, and United States".
# https://www.nass.usda.gov/Publications/Todays_Reports/reports/land0825.pdf (free)
# AGRICULTURAL raw-land PROXY / floor -- NOT DC or industrial land. AK & HI are not
# surveyed by USDA, so they have no state figure (they fall through to region).
USDA_FARM_RE_USD_PER_ACRE_2025 = {
    "AL": 4150, "AZ": 4180, "AR": 4250, "CA": 13700, "CO": 2290, "CT": 14400,
    "DE": 9550, "FL": 8700, "GA": 4720, "ID": 4580, "IL": 8930, "IN": 8850,
    "IA": 9790, "KS": 3100, "KY": 5480, "LA": 3850, "ME": 3350, "MD": 9750,
    "MA": 14900, "MI": 6800, "MN": 6790, "MS": 3580, "MO": 5000, "MT": 1230,
    "NE": 4250, "NV": 1200, "NH": 6500, "NJ": 16600, "NM": 725, "NY": 4300,
    "NC": 5470, "ND": 2360, "OH": 9350, "OK": 2540, "OR": 3780, "PA": 8490,
    "RI": 22500, "SC": 4740, "SD": 2970, "TN": 6150, "TX": 2970, "UT": 3500,
    "VT": 4400, "VA": 6100, "WA": 3710, "WV": 3520, "WI": 6420, "WY": 1000,
}
USDA_NATIONAL_AVG_2025 = 4350  # US average farm real estate value per acre, 2025
USDA_SOURCE = "USDA NASS, Land Values 2025 Summary (1 Aug 2025) -- agricultural raw-land proxy, not DC land."

# --- METRO / COUNTY tier: real quoted data-center / industrial land $/acre -------
# Each entry is a genuine figure quoted on a free public page (see SOURCES.md 6b).
# Matched on (state_code, substring found in the Nominatim county/city name).
# "usd_per_acre" is the power-ready / market DC-land figure; "note" carries the deal.
# Ordered most-specific first within a state.
METRO_COMPS = [
    # --- Virginia (the most-documented DC market in the US) ---
    {
        "state": "VA", "match": ["loudoun"],
        "label": "Loudoun County, VA (data-center land)",
        "usd_per_acre": 6_300_000,
        "source": "Northern Virginia Magazine / DataCenterDynamics, Nov 2025: SDC Capital bought 97 ac for $615.05M (~$6.3M/ac, county record).",
    },
    {
        "state": "VA", "match": ["prince william"],
        "label": "Prince William County, VA (data-center land)",
        "usd_per_acre": 3_750_000,
        "source": "CoStar, 2025: Amazon ~189 ac for ~$700M in Gainesville (~$3.75M/ac implied).",
    },
    {
        "state": "VA", "match": ["fairfax", "fauquier", "stafford", "ashburn"],
        "label": "Northern Virginia DC corridor",
        "usd_per_acre": 3_750_000,
        "source": "Northern Virginia DC market, 2025 trade-press transactions (Loudoun ~$6.3M/ac, Prince William ~$3.75M/ac). NoVa-corridor indicative.",
    },
    # --- Arizona (Phoenix / Maricopa) ---
    {
        "state": "AZ", "match": ["goodyear", "maricopa", "phoenix", "mesa", "chandler", "tempe", "gilbert", "glendale", "peoria", "scottsdale"],
        "label": "Phoenix / Maricopa County, AZ (power-ready DC land)",
        "usd_per_acre": 1_300_000,
        "source": "CoStar / DataCenterDynamics, 2025: Microsoft 100 ac $131M+ (Goodyear, ~$1.31M/ac); Amazon 220 ac $277M (~$1.26M/ac).",
    },
    {
        "state": "AZ", "match": ["buckeye"],
        "label": "Buckeye, AZ (exurban DC land)",
        "usd_per_acre": 136_000,
        "source": "DataCenterDynamics, Mar 2025: Arizona Land 160 ac $21.7M in Buckeye (~$136k/ac implied). Far-exurb raw land is far cheaper (~$25k/ac).",
    },
    # --- Ohio (Columbus / New Albany) ---
    {
        "state": "OH", "match": ["new albany", "licking", "franklin"],
        "label": "New Albany / Columbus, OH (data-center land)",
        "usd_per_acre": 741_000,
        "source": "DataCenterDynamics, Jun 2025: Google 85 ac $63M in New Albany (~$741k/ac implied). Amazon's 112-ac New Albany deal implied ~$195k/ac.",
    },
    # --- Georgia (Atlanta metro -- note deals are exurban, understate intown) ---
    {
        "state": "GA", "match": ["lamar"],
        "label": "Lamar County, GA (Atlanta exurb DC land)",
        "usd_per_acre": 274_000,
        "source": "Atlanta Journal-Constitution, Aug 2025: Amazon 984 ac ~$270M in Lamar County (~$274k/ac implied, exurban).",
    },
    {
        "state": "GA", "match": ["monroe"],
        "label": "Monroe County, GA (Atlanta exurb DC land)",
        "usd_per_acre": 61_600,
        "source": "DataCenterDynamics, Sep 2025: Google 950 ac $58.5M in Monroe County (~$61.6k/ac implied, far exurb / raw).",
    },
    # --- California (Silicon Valley) ---
    {
        "state": "CA", "match": ["santa clara", "san jose", "sunnyvale", "mountain view", "silicon valley"],
        "label": "Santa Clara / Silicon Valley, CA (DC land)",
        "usd_per_acre": 6_000_000,
        "source": "Datacenters.com (secondary aggregator): Silicon Valley DC land ~$6M-7M+/ac. Directional; among the most expensive US markets.",
    },
    # --- Texas (Dallas-Fort Worth -- weakest citable DC-land data) ---
    {
        "state": "TX", "match": ["dallas", "tarrant", "fort worth", "denton", "collin"],
        "label": "Dallas-Fort Worth, TX (industrial land)",
        "usd_per_acre": 540_000,
        "source": "LandSearch listing averages, 2025-26: DFW industrial land ~$498k-581k/ac. General industrial (no clean free DC-transaction figure found for DFW).",
    },
    # --- Illinois (Chicago metro) ---
    {
        "state": "IL", "match": ["cook", "chicago", "dupage", "will", "kane", "lake"],
        "label": "Chicago metro, IL (data-center land)",
        "usd_per_acre": 234_000,
        "source": "Cushman & Wakefield, Data Center Development Cost Guide 2025 (public): Chicago DC land ~$5.40-5.59/sf (~$235k-244k/ac weighted avg).",
    },
    # --- Oregon (Hillsboro) ---
    {
        "state": "OR", "match": ["hillsboro", "washington county"],
        "label": "Hillsboro, OR (data-center land)",
        "usd_per_acre": 1_000_000,
        "source": "Hillsboro Herald / Oregon Center for Public Policy, 2026: industrial/DC land escalated $250k -> $1M+/ac.",
    },
]

# National DC-land default (Cushman & Wakefield 2025), used as context only.
CW_NATIONAL_DC_LAND_USD_PER_ACRE_2024 = 213_000  # midpoint of ~$191k-235k/ac
CW_NATIONAL_DC_LAND_SOURCE = (
    "Cushman & Wakefield, Data Center Development Cost Guide 2025 (public): US DC "
    "land for 50+ ac parcels ~$5.40/sf in 2024 (~$191k-235k/ac weighted avg)."
)


def _match_metro(state_code, county, city):
    """Return a METRO_COMPS entry if the place (county / city) matches one."""
    if not state_code:
        return None
    hay = " ".join(x.lower() for x in (county or "", city or "") if x)
    if not hay:
        return None
    for entry in METRO_COMPS:
        if entry["state"] != state_code:
            continue
        if any(tok in hay for tok in entry["match"]):
            return entry
    return None


def place_label(state_code=None, county=None, city=None, state_name=None):
    """Human-readable 'County, ST' style label for a US place (no directions)."""
    state_name = state_name or US_STATE_NAMES.get(state_code or "", None)
    parts = [p for p in (county or city, state_name) if p]
    return ", ".join(parts) if parts else "Unknown location"


def state_context(state_code):
    """
    State-level benchmark context, so a parcel is compared against ITS state rather
    than a broad directional bucket: the state's USDA raw-land value relative to
    the US average, plus any quoted DC-land comparables elsewhere in the same state
    (useful for the override step when the parcel sits in an emerging market).
    """
    if not state_code:
        return None
    ag = USDA_FARM_RE_USD_PER_ACRE_2025.get(state_code)
    in_state = [
        {"label": e["label"], "usd_per_acre": float(e["usd_per_acre"])}
        for e in METRO_COMPS if e["state"] == state_code
    ]
    return {
        "state_code": state_code,
        "state_name": US_STATE_NAMES.get(state_code),
        "usda_ag_usd_per_acre": float(ag) if ag else None,
        "usda_ag_vs_us_avg": (ag / USDA_NATIONAL_AVG_2025) if ag else None,
        "in_state_dc_land_comps": in_state,
    }


def lookup_land_comp_for_place(state_code=None, county=None, city=None,
                               state_name=None, country_code="us"):
    """
    Resolve a land comparable directly from a US state (+ optional county /
    district / city). This is what the UI's State + County fields call when the
    user edits the auto-detected location, and what /api/estimate uses when a
    state is supplied without a confirmed comparable.

    Returns a plain dict (JSON-serialisable) describing the chosen comparable and,
    importantly, which TIER it came from so the UI can label it honestly:

      {
        "usd_per_acre": float | None,
        "tier": "metro" | "state" | "national",
        "label": str,
        "source": str,
        "is_dc_land": bool,         # True only for the metro tier (power-ready DC land)
        "dc_premium_note": str,     # honest raw-vs-DC-land caveat for non-metro tiers
        "detected": {state, state_code, county, city, country_code},
        "place": "Loudoun County, Virginia",
        "state_context": {...},     # see state_context()
      }
    """
    if state_code and len(state_code) > 2:
        state_code = state_abbr(state_code)
    state_code = (state_code or "").upper() or None
    if state_code and not state_name:
        state_name = US_STATE_NAMES.get(state_code)

    detected = {
        "state": state_name,
        "state_code": state_code,
        "county": county or None,
        "city": city or None,
        "country_code": country_code,
    }
    place = place_label(state_code, county, city, state_name)
    ctx = state_context(state_code)

    def _result(**kw):
        kw.update({"detected": detected, "place": place, "state_context": ctx})
        return kw

    # Non-US / unknown state: national proxy, honestly labelled.
    if country_code != "us" or not state_code or state_code not in US_STATE_NAMES:
        return _result(
            usd_per_acre=LAND_PRICE_USD_PER_ACRE["national"],
            tier="national",
            label="National industrial-land proxy",
            source=(
                "Outside the US state/county dataset -- using the national "
                "industrial-land proxy. Not a parcel-level appraisal."
            ),
            is_dc_land=False,
            dc_premium_note="",
        )

    # 1) Metro / county tier: a real quoted DC-land transaction.
    metro = _match_metro(state_code, county, city)
    if metro:
        return _result(
            usd_per_acre=float(metro["usd_per_acre"]),
            tier="metro",
            label=metro["label"],
            source=metro["source"],
            is_dc_land=True,
            dc_premium_note=(
                "This is a power-ready / entitled data-center-land market figure "
                "from a quoted transaction, not a raw-land proxy."
            ),
        )

    # 2) State tier: USDA agricultural raw-land proxy (a floor, clearly labelled).
    if state_code in USDA_FARM_RE_USD_PER_ACRE_2025:
        ag = USDA_FARM_RE_USD_PER_ACRE_2025[state_code]
        county_note = (
            f" No quoted data-center-land transaction is on file for {county}, so "
            f"the {state_name} state figure is used." if county else ""
        )
        return _result(
            usd_per_acre=float(ag),
            tier="state",
            label=f"{place} -- {state_name} agricultural raw-land floor (USDA 2025)",
            source=USDA_SOURCE + county_note,
            is_dc_land=False,
            dc_premium_note=(
                "Raw/agricultural land is a FLOOR. Entitled, power-connected "
                "data-center land in active markets trades roughly 20x-1,000x "
                "higher (e.g. Virginia farmland ~$6,100/acre vs Loudoun County "
                "data-center land ~$6.3M/acre, Nov 2025). Use the override to "
                "search a specific data-center market if this parcel is one."
            ),
        )

    # 3) National fallback: AK / HI / DC (not surveyed by USDA). Still labelled with
    #    the real state + county, never a directional bucket.
    return _result(
        usd_per_acre=LAND_PRICE_USD_PER_ACRE["national"],
        tier="national",
        label=f"{place} -- national industrial-land proxy (no {state_name} state figure)",
        source=(
            f"USDA NASS does not publish a farm real-estate value for {state_name}, "
            "and no quoted DC-land transaction is on file, so the national "
            "industrial-land proxy is used. Not a parcel-level appraisal."
        ),
        is_dc_land=False,
        dc_premium_note="",
    )


def lookup_land_comp(reverse_result):
    """
    Resolve a land comparable from a ReverseResult (geocode.reverse_geocode) by
    delegating to lookup_land_comp_for_place() with the detected state + county.
    Non-US coordinates (or a failed lookup) fall through to the national proxy.
    """
    rev = reverse_result
    if not getattr(rev, "ok", False):
        return lookup_land_comp_for_place(country_code=None)
    return lookup_land_comp_for_place(
        state_code=getattr(rev, "state_code", None),
        county=getattr(rev, "county", None),
        city=getattr(rev, "city", None),
        state_name=getattr(rev, "state", None),
        country_code=getattr(rev, "country_code", None),
    )
