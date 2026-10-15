"""
Expanded metals coverage (11 metals) and the facility-vs-compute value split.

WHAT THIS MODULE DOES
---------------------
1. Holds per-MW metal intensities broken down by data-center COMPONENT, so every
   tonne can be attributed either to the FACILITY / campus-shell infrastructure
   (cooling, electrical distribution, backup power, building structure, near-site
   power connections) or to the COMPUTE equipment housed inside (servers / chips /
   racks and networking / storage).
2. Holds the price basis for each metal: LIVE via Metals.Dev where that provider
   carries the metal, otherwise a dated STATIC benchmark (labelled as such).
3. Computes quantities and contained-metal values for a given IT capacity (MW)
   and build-type multipliers, and returns them as plain dicts for the API / UI.

PRIMARY SOURCE FOR THE COMPONENT TABLE
--------------------------------------
World Economic Forum / Kearney, "From Minerals to Megawatts" (Dec 2025), Figure 4,
"Data centre component breakdown by mineral (kgs per MW)", attributed to Bank of
America Securities, IEA and Kearney analysis. Verified by direct PDF extraction:
https://reports.weforum.org/docs/WEF_From_Minerals_to_Megawatts_2025.pdf
The figure is based on a 2024 fleet mix of ~76% conventional (CPU) / ~24%
accelerated (GPU) capacity. Values printed as "<0.1" are entered here as 0.05
(the midpoint of 0-0.1); they are immaterial to every total. See SOURCES.md 14.

METAL PRIORITY (why these 11)
-----------------------------
Ranked by significance to data-center infrastructure, combining mass per MW
(from the WEF table plus the tool's structural-steel benchmark) and value /
supply-criticality (WEF's "value chain contribution to global demand" row: data
centres are ~6% of global gallium demand, ~1.2% of tin, ~0.9% of copper, ~0.6% of
gold, ~0.5% of cobalt, ~0.4% of silver by 2035):

  bulk / structural & power:  steel (iron), copper, aluminum
  equipment & batteries:      nickel, lead, tin
  electronics (high value):   silver, gold
  battery / semiconductor:    cobalt, lithium, gallium

Considered but NOT modelled (honest omissions):
  * zinc -- used for galvanising structural steel and cable tray, but no citable
    per-MW or per-sq-ft data-center figure was found (WEF Fig. 4 omits it). Zinc
    IS on Metals.Dev, so it can be switched on if a source turns up.
  * germanium, rare-earth elements -- listed by WEF but at ~0.1-3 kg/MW and with no
    free price feed; immaterial to value.
  * platinum / palladium -- on Metals.Dev, but no data-center intensity source.
  * silicon and graphite -- in the WEF table but not metals (graphite is still
    shown in the existing battery-backup panel).
  * stainless steel -- handled as a build-type-specific QUANTITY only (see
    build_types.py); not priced, because the per-MW figure is a low-confidence
    derivation.

AVOIDING DOUBLE-COUNTING
------------------------
* Copper keeps the tool's existing, cross-validated headline of 26 t/MW incl.
  near-site power connections (SOURCES.md 3). WEF's five components sum to
  ~11.6 t/MW; the remaining ~14.4 t/MW is attributed to near-site power
  connections (facility side).
* Aluminum keeps 11.3 t/MW (= the WEF component sum, SOURCES.md 5).
* Steel: the tool's building-steel benchmark (0.016 t/sq ft, which its source
  says already covers "structural framing, cooling systems and heavy equipment
  support") is the FACILITY steel line. WEF's equipment "iron" for cooling /
  backup / electrical (~42 t/MW) overlaps with that benchmark in an unknowable
  proportion, so it is NOT added. Only WEF's server + networking iron (~5.8 t/MW:
  chassis, racks, enclosures) is added, on the COMPUTE side, because a
  building-area steel benchmark clearly does not include server hardware.
* Battery metals (lithium, cobalt, nickel, lead) for the facility side come from
  WEF's backup-power component -- the same numbers already shown in the
  battery-backup (UPS) panel. They are now also priced here, as contained metal.

VALUATION BASIS -- READ THIS
----------------------------
Values are CONTAINED-METAL values: tonnes x a spot / reference price for the
refined metal. That is the "today's commodity terms" lens the tool already uses
for copper and aluminum. It is NOT recoverable scrap value (recovery of gold or
gallium from boards is partial and costly) and NOT the price of the product the
metal sits in (battery-grade nickel sulphate, lithium carbonate, GaN wafers).
"""

# Components, and which side of the facility / compute split each falls on.
FACILITY_COMPONENTS = ("cooling", "electrical", "backup")
COMPUTE_COMPONENTS = ("servers", "networking")

# --- WEF / Kearney Fig. 4: kg of metal per MW, by component --------------------
# Blank cells in the figure (metal not listed for that component) are 0.
WEF_KG_PER_MW = {
    "copper":   {"cooling": 3_600, "electrical": 3_500, "backup": 2_200, "servers": 2_000, "networking": 280},
    "aluminum": {"cooling": 6_700, "electrical": 460,   "backup": 1_200, "servers": 2_700, "networking": 260},
    "iron":     {"cooling": 18_000, "electrical": 9_900, "backup": 14_000, "servers": 5_100, "networking": 660},
    "nickel":   {"cooling": 130,   "electrical": 70,    "backup": 220,   "servers": 35,    "networking": 15},
    "lead":     {"cooling": 10,    "electrical": 0,     "backup": 240,   "servers": 15,    "networking": 0},
    "tin":      {"cooling": 0.1,   "electrical": 5,     "backup": 2,     "servers": 120,   "networking": 10},
    "silver":   {"cooling": 0.05,  "electrical": 1,     "backup": 0.5,   "servers": 5,     "networking": 0.5},
    "gold":     {"cooling": 0.05,  "electrical": 0.2,   "backup": 0.05,  "servers": 1,     "networking": 0.05},
    "cobalt":   {"cooling": 0,     "electrical": 0,     "backup": 40,    "servers": 2,     "networking": 1},
    "lithium":  {"cooling": 0,     "electrical": 0,     "backup": 30,    "servers": 0,     "networking": 0},
    "gallium":  {"cooling": 0,     "electrical": 0,     "backup": 0,     "servers": 2,     "networking": 0.3},
}

# Tool's existing whole-site headline copper (SOURCES.md 3), incl. near-site power.
COPPER_TONNES_PER_MW_HEADLINE = 26.0

# Tool's existing building-steel benchmark, re-expressed per MW at the baseline
# 250 W/sq ft density: 0.016 t/sq ft / 250 W/sq ft = 64 t/MW. Identical to the old
# per-sq-ft calculation for the baseline build type; per-MW so that build-type
# density changes and a user-stated MW (power layer) flow through consistently.
BASE_STEEL_TONNES_PER_SQFT = 0.016
BASE_POWER_DENSITY_W_PER_SQFT = 250.0
BUILDING_STEEL_TONNES_PER_MW = BASE_STEEL_TONNES_PER_SQFT / BASE_POWER_DENSITY_W_PER_SQFT * 1e6


def _kg(metal, comps):
    return sum(WEF_KG_PER_MW[metal][c] for c in comps)


# --- Metal registry: display order = significance ranking ----------------------
# price: ("live", "<metals.dev key>")  or  ("static", usd_per_tonne, source_text)
# Static prices were checked 2026-10-15; they are NOT live and say so in the UI.
TROY_OZ_PER_TONNE = 32_150.7466

METALS = [
    {
        "key": "steel", "label": "Steel (structural + equipment)", "symbol": "Fe",
        "role": "Building frame, equipment supports, server chassis and racks.",
        "price": ("static", 900.0,
                  "STATIC benchmark $900/t (US structural / HRC, 2024-25 range $700-1,100). "
                  "Steel is not on Metals.Dev. See SOURCES.md 8."),
    },
    {
        "key": "copper", "label": "Copper", "symbol": "Cu",
        "role": "Power distribution, switchgear, cabling, busbars, cooling coils.",
        "price": ("live", "copper"),
    },
    {
        "key": "aluminum", "label": "Aluminum", "symbol": "Al",
        "role": "Cooling coils and fins, busway, server and rack enclosures.",
        "price": ("live", "aluminum"),
    },
    {
        "key": "nickel", "label": "Nickel", "symbol": "Ni",
        "role": "UPS battery cathodes, stainless and alloy components in cooling.",
        "price": ("live", "nickel"),
    },
    {
        "key": "lead", "label": "Lead", "symbol": "Pb",
        "role": "Lead-acid (VRLA) UPS batteries still in the installed fleet.",
        "price": ("live", "lead"),
    },
    {
        "key": "tin", "label": "Tin", "symbol": "Sn",
        "role": "Solder on every circuit board in servers and network gear.",
        "price": ("static", 54_900.0,
                  "STATIC benchmark $54,900/t (LME tin settlement, 8 Sep 2026, via "
                  "cbonds / Westmetall). Tin is not on Metals.Dev."),
    },
    {
        "key": "silver", "label": "Silver", "symbol": "Ag",
        "role": "Contacts, conductive pastes and plating in electronics and switchgear.",
        "price": ("live", "silver"),
    },
    {
        "key": "gold", "label": "Gold", "symbol": "Au",
        "role": "Connector plating and bond wires in chips and boards.",
        "price": ("live", "gold"),
    },
    {
        "key": "cobalt", "label": "Cobalt", "symbol": "Co",
        "role": "Li-ion UPS battery cathodes (NMC chemistries).",
        "price": ("static", 53_600.0,
                  "STATIC benchmark ~$53,600/t (cobalt metal, Rotterdam, 2 Oct 2026, via "
                  "critical-minerals-news.com; China domestic was lower, ~$39k/t). "
                  "Cobalt is not on Metals.Dev."),
    },
    {
        "key": "lithium", "label": "Lithium", "symbol": "Li",
        "role": "Li-ion UPS batteries replacing lead-acid in new builds.",
        "price": ("static", 105_100.0,
                  "STATIC benchmark ~$105,100/t contained lithium, derived from "
                  "battery-grade lithium carbonate $19,750/t (Benchmark Mineral "
                  "Intelligence, CIF Asia, 2 Sep 2026) / 18.8% Li content. Assumes the "
                  "WEF figure is lithium content, not carbonate equivalent (not stated "
                  "in the source). Lithium is not on Metals.Dev."),
    },
    {
        "key": "gallium", "label": "Gallium", "symbol": "Ga",
        "role": "GaN / GaAs power and RF semiconductors in servers and networking.",
        "price": ("static", 433_000.0,
                  "STATIC benchmark $433/kg (China FOB export price, 30 Sep 2026, via "
                  "rare-earth-mining.com citing SMM). Gallium trades in split markets: "
                  "China domestic ~$229/kg, European high-purity spot far higher. "
                  "Gallium is not on Metals.Dev."),
    },
]

METAL_KEYS = [m["key"] for m in METALS]


def base_tonnes_per_mw():
    """
    Baseline (multiplier = 1) tonnes per MW for each metal, split facility/compute.
    Returns {metal: {"facility": t/MW, "compute": t/MW}}.
    """
    out = {}
    for m in METAL_KEYS:
        if m == "steel":
            fac = BUILDING_STEEL_TONNES_PER_MW
            comp = _kg("iron", COMPUTE_COMPONENTS) / 1000.0
        elif m == "copper":
            comp = _kg("copper", COMPUTE_COMPONENTS) / 1000.0
            fac = COPPER_TONNES_PER_MW_HEADLINE - comp  # incl. near-site power
        else:
            fac = _kg(m, FACILITY_COMPONENTS) / 1000.0
            comp = _kg(m, COMPUTE_COMPONENTS) / 1000.0
        out[m] = {"facility": fac, "compute": comp}
    return out


def resolve_price(metal_def, live_prices):
    """Return (usd_per_tonne or None, kind, source_text) for one metal."""
    price = metal_def["price"]
    if price[0] == "static":
        return price[1], "static", price[2]
    key = price[1]
    p = (live_prices or {}).get(key)
    if p is None:
        return None, "unavailable", (
            f"Live {metal_def['label'].lower()} price unavailable (Metals.Dev); "
            "excluded from the total, tonnage still shown."
        )
    return p, "live", f"LIVE ${p:,.2f}/t via Metals.Dev."


def compute_metals(mw, facility_multipliers=None, live_prices=None,
                   live_source=None):
    """
    Quantities and contained-metal values for `mw` of IT capacity.

    facility_multipliers: {metal: factor} applied to the FACILITY-side intensity
      only (build-type effect; compute-side intensities are not varied by build
      type because no source quantifies that -- see build_types.py).
    live_prices: {metal_key: usd_per_tonne} from metals_client.

    Returns a dict:
      {
        "metals": [ {key, label, symbol, role, facility_t, compute_t, total_t,
                     usd_per_t, price_kind, price_source,
                     facility_usd, compute_usd, total_usd, priced} ... ],
        "facility_metals_usd", "compute_metals_usd", "metals_usd",
        "priced_count", "excluded": [labels...]
      }
    """
    mults = facility_multipliers or {}
    base = base_tonnes_per_mw()
    rows = []
    fac_usd = comp_usd = 0.0
    excluded = []
    for md in METALS:
        k = md["key"]
        f_t = base[k]["facility"] * mw * float(mults.get(k, 1.0))
        c_t = base[k]["compute"] * mw
        price, kind, src = resolve_price(md, live_prices)
        if kind == "live" and live_source:
            src = f"LIVE ${price:,.2f}/t via {live_source}."
        priced = price is not None
        f_v = f_t * price if priced else 0.0
        c_v = c_t * price if priced else 0.0
        fac_usd += f_v
        comp_usd += c_v
        if not priced:
            excluded.append(md["label"])
        rows.append({
            "key": k, "label": md["label"], "symbol": md["symbol"], "role": md["role"],
            "facility_t": f_t, "compute_t": c_t, "total_t": f_t + c_t,
            "usd_per_t": price, "price_kind": kind, "price_source": src,
            "facility_usd": f_v, "compute_usd": c_v, "total_usd": f_v + c_v,
            "priced": priced,
        })
    return {
        "metals": rows,
        "facility_metals_usd": fac_usd,
        "compute_metals_usd": comp_usd,
        "metals_usd": fac_usd + comp_usd,
        "priced_count": sum(1 for r in rows if r["priced"]),
        "excluded": excluded,
    }
