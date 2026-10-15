"""
Core estimation logic for the Data Center Site Value Estimator.

All benchmark figures below are documented in SOURCES.md with their sources and
last-verified dates. Keep the two in sync: if you change a number here, update
SOURCES.md.

Nothing in this module makes network calls; live commodity pricing lives in
metals_client.py and land AVM lookups in land_value.py, so the pure calculation
logic stays testable and deterministic.
"""

from dataclasses import dataclass, field, asdict

from capacity import estimate_capacity
from metals_mix import (
    compute_metals,
    BASE_STEEL_TONNES_PER_SQFT,
    COPPER_TONNES_PER_MW_HEADLINE,
)

# --- Benchmark assumptions (see SOURCES.md for provenance) ---

# Power density (watts per square foot of building space). Mid-range of the
# 200-400 W/sq ft modern-facility band. Source: TierPoint / Cadence.
POWER_DENSITY_W_PER_SQFT = 250.0

# Steel intensity (metric tons per square foot). Midpoint of 0.014-0.018.
# Source: Data Centre Magazine / impactECI.
STEEL_TONNES_PER_SQFT = BASE_STEEL_TONNES_PER_SQFT  # 0.016; single source of truth in metals_mix.py

# Copper intensity (tonnes per MW). Lower bound = facility-only rule of thumb;
# default = including near-site power connections (anchored on Microsoft's
# ~80 MW Chicago site ~= 27 t/MW). Source: BloombergNEF / BHP, corroborated
# independently by WEF/Kearney Dec 2025 Figure 4 (facility-only sum ~11.6 t/MW,
# within 3% of the 12 t/MW figure here). See SOURCES.md entry 3.
COPPER_TONNES_PER_MW_FACILITY = 12.0
COPPER_TONNES_PER_MW_WITH_GRID = COPPER_TONNES_PER_MW_HEADLINE  # 26.0; see metals_mix.py

# Concrete intensity (cubic meters per MW). Midpoint of 500-1,000.
# Source: impactECI / Cushman & Wakefield. Shown as a physical quantity only,
# NOT priced into the total (see SOURCES.md).
CONCRETE_M3_PER_MW = 750.0
# Rough density to also express concrete as tonnes for context (~2.4 t/m3).
CONCRETE_TONNES_PER_M3 = 2.4

# --- Aluminum intensity (tonnes per MW) ----------------------------------------
# Source: World Economic Forum / Kearney, "From Minerals to Megawatts" white paper
# (Dec 2025), Figure 4, "Data centre component breakdown by mineral (kgs per MW)" —
# attributed to Bank of America Securities / IEA / Kearney analysis. Summing
# aluminum across all five components (cooling ~6,700 + servers ~2,700 + backup
# ~1,200 + electrical ~460 + networking ~260 kg/MW) gives ~11.3 t/MW. This replaced
# an earlier bottom-up (rack-frame + cooling-CDU only) lower-bound estimate once
# this better-sourced, reputable whole-facility figure was found; see SOURCES.md
# entry 5 for the full component table and the superseded bottom-up cross-check.
ALUMINUM_TONNES_PER_MW = 11.3

# --- Battery-backup (UPS) metals ----------------------------------------------
# New-build hyperscale/colo UPS is now predominantly lithium-ion; legacy sites (and
# much of the installed base) still use VRLA lead-acid, often alongside Li-ion.
# This is the line most connected to the battery-metals / PGM mining thesis.
# CRUCIAL honesty point: data-center UPS only provides minutes of ride-through
# before generators start, so the battery ENERGY per MW is small versus grid-scale
# storage, and so is the implied metal tonnage. We make that explicit rather than
# overstating it, and we give TWO figures rather than one:
#
#   (a) HEADLINE, top-down: WEF/Kearney "From Minerals to Megawatts" (Dec 2025),
#       Figure 4, backup-power component, kg/MW (source: Bank of America
#       Securities / IEA / Kearney analysis). This reflects the REAL fleet mix
#       (mostly Li-ion, with lead-acid still present) and real-world redundancy/
#       runtime assumptions, not just a single ride-through calc.
#   (b) LOWER-BOUND cross-check, bottom-up: a 5-minute full-load ride-through
#       calc (standard sizing; see SOURCES.md entry 12), de-rated for UPS
#       efficiency (~95%) and usable depth-of-discharge (~90%), x NMC811 cathode
#       intensity (IEA/ICCT/Argonne BatPaC). This comes out ~3-4x BELOW the WEF
#       headline, consistent with WEF assuming a longer effective runtime /
#       N+1 redundancy / blended fleet rather than a bare 5-minute minimum.
#
# Both are shown; neither is priced into the total (see note in estimate_site()).
WEF_BACKUP_LITHIUM_KG_PER_MW = 30.0
WEF_BACKUP_NICKEL_KG_PER_MW = 220.0
WEF_BACKUP_COBALT_KG_PER_MW = 40.0
WEF_BACKUP_LEAD_KG_PER_MW = 240.0
WEF_BACKUP_GRAPHITE_KG_PER_MW = 290.0
WEF_BACKUP_ALUMINUM_KG_PER_MW = 1_200.0
WEF_BACKUP_COPPER_KG_PER_MW = 2_200.0

# UPS energy sizing: 5 minutes full-load ride-through (standard), de-rated for UPS
# efficiency (~95%) and usable depth-of-discharge (~90%):
#   kWh/MW = 1000 kW * (5/60) h / (0.95 * 0.90) ~= 97.5 kWh per MW of IT load.
UPS_RIDE_THROUGH_MIN = 5.0
UPS_EFFICIENCY = 0.95
UPS_USABLE_DOD = 0.90
UPS_KWH_PER_MW = 1000.0 * (UPS_RIDE_THROUGH_MIN / 60.0) / (UPS_EFFICIENCY * UPS_USABLE_DOD)

# NMC811 cathode critical-metal intensity (kg per kWh of battery capacity).
# Source: IEA / ICCT / Argonne BatPaC (see SOURCES.md entry 12). NMC811 = 80% Ni.
BATTERY_LI_KG_PER_KWH = 0.10
BATTERY_NI_KG_PER_KWH = 0.65
BATTERY_CO_KG_PER_KWH = 0.081
# LFP alternative (increasingly common for DC UPS): lithium only, no Ni/Co.
BATTERY_LI_KG_PER_KWH_LFP = 0.09

# Static steel price (USD per metric ton). NOT a live quote: steel is not on the
# Metals.Dev free tier. Generic US structural/HRC benchmark. Source: SOURCES.md.
STATIC_STEEL_PRICE_USD_PER_TONNE = 900.0

# Shell / base-building construction cost, EXCLUDING the IT power chain /
# electrical / mechanical plant — i.e. land improvement, foundation, structural
# core & shell and architecture only. The power/M&E side is already captured via
# the MW / copper / steel figures, so including M&E here would double-count.
#
# We DON'T hard-code a bare $/sq ft (the only shell-only $/sq ft figures come from
# weak, mutually-inconsistent blog sources). Instead we price shell cost directly
# per MW of IT capacity, anchored on the shell-and-core cost band for an air-cooled
# facility (~$1.0-2.1M/MW; JLL's single-tenant ~50 MW air-cooled shell-and-core
# figure sits near ~$1.5M/MW, and this is ~12-15% of a ~$10-14M/MW all-in hard
# cost). 1.5 = a defensible mid-band default. See SOURCES.md entry 9.
SHELL_COST_USD_PER_MW = 1_500_000.0

# Broad commercial/industrial land price proxies (USD per acre).
# Generic industrial land proxy, NOT power-ready data-center-premium land.
# Source: CBRE industrial land research. See SOURCES.md for the honesty caveat.
# NOTE: US parcels are now described and benchmarked at STATE + COUNTY level (see
# land_prices.py); only the "national" entry is still used, as the last-resort
# fallback (non-US coordinates, or AK / HI / DC which USDA does not survey). The
# directional keys are kept solely so old API callers passing `region` still work.
LAND_PRICE_USD_PER_ACRE = {
    "national": 150_000.0,
    "northeast": 400_000.0,
    "west": 250_000.0,
    "south": 120_000.0,
    "midwest": 100_000.0,
}

VALID_REGIONS = set(LAND_PRICE_USD_PER_ACRE.keys())

SQFT_PER_ACRE = 43_560.0


class ValidationError(ValueError):
    """Raised for invalid user input."""


def validate_inputs(lat, lng, sqft, region):
    """Validate and coerce inputs. Raises ValidationError with a clear message."""
    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        raise ValidationError("Latitude and longitude must be numbers.")

    if not (-90.0 <= lat <= 90.0):
        raise ValidationError("Latitude must be between -90 and 90.")
    if not (-180.0 <= lng <= 180.0):
        raise ValidationError("Longitude must be between -180 and 180.")

    try:
        sqft = float(sqft)
    except (TypeError, ValueError):
        raise ValidationError("Square footage must be a number.")
    if sqft <= 0:
        raise ValidationError("Square footage must be greater than zero.")
    if sqft > 50_000_000:
        raise ValidationError(
            "Square footage looks implausibly large (>50M sq ft). "
            "Please double-check the input."
        )

    region = (region or "national").strip().lower()
    if region not in VALID_REGIONS:
        raise ValidationError(
            f"Region must be one of: {', '.join(sorted(VALID_REGIONS))}."
        )

    return lat, lng, sqft, region


@dataclass
class Estimate:
    """Structured result of a site estimate. Serialisable to JSON via to_dict()."""

    lat: float
    lng: float
    sqft: float
    region: str

    # Derived physical quantities
    implied_mw: float = 0.0
    steel_tonnes: float = 0.0
    copper_tonnes_facility: float = 0.0
    copper_tonnes_with_grid: float = 0.0
    concrete_m3: float = 0.0
    concrete_tonnes: float = 0.0
    aluminum_tonnes: float = 0.0
    acres: float = 0.0

    # Battery-backup (UPS) metals — physical quantities (not priced). Reported in
    # kg because the tonnage at UPS scale is small; a grid-BESS note is attached.
    # HEADLINE figures are WEF/Kearney Dec 2025 (top-down, real fleet mix); the
    # "_lowerbound" figures are our own 5-min-ride-through bottom-up cross-check.
    battery_lithium_kg: float = 0.0
    battery_nickel_kg: float = 0.0
    battery_cobalt_kg: float = 0.0
    battery_lead_kg: float = 0.0
    battery_graphite_kg: float = 0.0
    ups_battery_kwh_lowerbound: float = 0.0
    battery_lithium_kg_lowerbound: float = 0.0
    battery_nickel_kg_lowerbound: float = 0.0
    battery_cobalt_kg_lowerbound: float = 0.0
    battery_lithium_kg_lfp_lowerbound: float = 0.0

    # Values (USD)
    land_value_usd: float = 0.0
    steel_cost_usd: float = 0.0
    copper_cost_usd: float = 0.0
    aluminum_cost_usd: float = 0.0
    material_cost_usd: float = 0.0
    shell_cost_usd: float = 0.0
    total_site_value_usd: float = 0.0

    # Expanded metals coverage (11 metals) with the facility / compute split.
    # Each row: tonnes and contained-metal value on each side + price provenance.
    metals: list = field(default_factory=list)
    metals_excluded: list = field(default_factory=list)
    nickel_cost_usd: float = 0.0
    lead_cost_usd: float = 0.0
    other_metals_cost_usd: float = 0.0

    # Value split. FACILITY = campus / shell infrastructure (land + shell +
    # metals in cooling, electrical, backup power, structure and near-site power
    # connections). COMPUTE = metals contained in the servers / chips / racks and
    # networking housed inside. total_site_value_usd = facility + compute.
    facility_metals_usd: float = 0.0
    compute_metals_usd: float = 0.0
    facility_value_usd: float = 0.0
    compute_value_usd: float = 0.0

    # Capacity / cooling (indicative) — populated from capacity.py
    capacity: dict = field(default_factory=dict)

    # Metadata / labels / honesty flags
    google_maps_url: str = ""
    notes: list = field(default_factory=list)
    price_sources: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def estimate_site(lat, lng, sqft, region="national", live_prices=None,
                  live_price_source=None, live_price_message=None,
                  land_price_per_acre_override=None,
                  land_comp_label=None, land_comp_source=None):
    """
    Build the full site estimate.

    live_prices: {metal_key: usd_per_tonne} from metals_client (may be empty if
    no API key / network). Any live-priced metal without a price is reported as
    unavailable rather than fabricated, and excluded from the total; its tonnage
    is still shown. Metals Metals.Dev does not carry use dated static benchmarks.

    land_price_per_acre_override, when supplied (from the granular, auto-detected
    and user-confirmed land comparable), replaces the broad-region proxy for the
    land-value line. land_comp_label / land_comp_source describe its provenance.
    """
    lat, lng, sqft, region = validate_inputs(lat, lng, sqft, region)

    est = Estimate(lat=lat, lng=lng, sqft=sqft, region=region)

    # Physical quantities
    est.implied_mw = (sqft * POWER_DENSITY_W_PER_SQFT) / 1_000_000.0
    mw = est.implied_mw
    est.copper_tonnes_facility = mw * COPPER_TONNES_PER_MW_FACILITY
    est.concrete_m3 = est.implied_mw * CONCRETE_M3_PER_MW
    est.concrete_tonnes = est.concrete_m3 * CONCRETE_TONNES_PER_M3
    est.acres = sqft / SQFT_PER_ACRE

    # Capacity / cooling is computed up front (used by capacity-dependent notes).
    cap = estimate_capacity(sqft, est.implied_mw)
    est.capacity = cap.to_dict()

    # Aluminum: WEF/Kearney Dec 2025 whole-facility per-MW figure (reputable
    # secondary, named attribution). Priced live via Metals.Dev when available.
    # Expanded metals (metals_mix.py): 11 metals, each split facility / compute.
    mix = compute_metals(mw, live_prices=live_prices, live_source=live_price_source)
    est.metals = mix["metals"]
    est.metals_excluded = mix["excluded"]
    by = {r["key"]: r for r in mix["metals"]}
    est.steel_tonnes = by["steel"]["total_t"]
    est.copper_tonnes_with_grid = by["copper"]["total_t"]
    est.aluminum_tonnes = by["aluminum"]["total_t"]

    # Battery-backup (UPS) metals.
    #  (a) HEADLINE: WEF/Kearney Dec 2025 top-down kg/MW (real fleet mix, incl.
    #      lead-acid still present alongside lithium-ion).
    est.battery_lithium_kg = est.implied_mw * WEF_BACKUP_LITHIUM_KG_PER_MW
    est.battery_nickel_kg = est.implied_mw * WEF_BACKUP_NICKEL_KG_PER_MW
    est.battery_cobalt_kg = est.implied_mw * WEF_BACKUP_COBALT_KG_PER_MW
    est.battery_lead_kg = est.implied_mw * WEF_BACKUP_LEAD_KG_PER_MW
    est.battery_graphite_kg = est.implied_mw * WEF_BACKUP_GRAPHITE_KG_PER_MW
    #  (b) LOWER-BOUND cross-check: our own 5-min-ride-through bottom-up calc,
    #      lithium-ion (NMC811) only. Shown to make the sizing assumption visible;
    #      comes out ~3-4x below the WEF headline (see constant comments above).
    est.ups_battery_kwh_lowerbound = est.implied_mw * UPS_KWH_PER_MW
    est.battery_lithium_kg_lowerbound = est.ups_battery_kwh_lowerbound * BATTERY_LI_KG_PER_KWH
    est.battery_nickel_kg_lowerbound = est.ups_battery_kwh_lowerbound * BATTERY_NI_KG_PER_KWH
    est.battery_cobalt_kg_lowerbound = est.ups_battery_kwh_lowerbound * BATTERY_CO_KG_PER_KWH
    est.battery_lithium_kg_lfp_lowerbound = est.ups_battery_kwh_lowerbound * BATTERY_LI_KG_PER_KWH_LFP

    # Land value. Prefer the granular, auto-detected + user-confirmed comparable
    # (state agricultural proxy, or a metro/county data-center-land figure where one
    # exists) when supplied; otherwise fall back to the broad-region proxy.
    if land_price_per_acre_override is not None:
        per_acre = float(land_price_per_acre_override)
        est.land_value_usd = est.acres * per_acre
        est.price_sources["land"] = (
            f"{land_comp_label or 'Detected comparable'}: ${per_acre:,.0f}/acre. "
            f"{land_comp_source or ''} NOT a parcel-level appraisal. See SOURCES.md."
        ).strip()
    else:
        per_acre = LAND_PRICE_USD_PER_ACRE[region]
        est.land_value_usd = est.acres * per_acre
        est.price_sources["land"] = (
            f"Industrial-land proxy ({region}): ${per_acre:,.0f}/acre. No state / "
            "county comparable was available. NOT a parcel-level appraisal. "
            "See SOURCES.md."
        )

    # Per-metal costs (contained-metal value; facility + compute combined). Legacy
    # per-metal fields are kept for API compatibility.
    est.steel_cost_usd = by["steel"]["total_usd"]
    est.copper_cost_usd = by["copper"]["total_usd"]
    est.aluminum_cost_usd = by["aluminum"]["total_usd"]
    est.nickel_cost_usd = by["nickel"]["total_usd"]
    est.lead_cost_usd = by["lead"]["total_usd"]
    est.other_metals_cost_usd = sum(
        r["total_usd"] for r in mix["metals"]
        if r["key"] not in ("steel", "copper", "aluminum", "nickel", "lead")
    )
    for r in mix["metals"]:
        est.price_sources[r["key"]] = r["price_source"]
    if est.metals_excluded:
        est.notes.append(
            "No live price was available for: " + ", ".join(est.metals_excluded) +
            f" ({live_price_message or 'Metals.Dev unavailable'}). Their tonnage is "
            "shown but their value is excluded from the total. Configure "
            "METALS_DEV_API_KEY to include them."
        )

    # Shell / base-building construction cost (excludes the power/M&E chain, which
    # is already captured by the MW / copper / steel figures — including M&E here
    # would double-count). Priced directly per implied MW on the sourced shell-and-
    # core cost band, labelled as a benchmark figure, not a live quote.
    est.shell_cost_usd = est.implied_mw * SHELL_COST_USD_PER_MW
    implied_shell_per_sqft = est.shell_cost_usd / sqft if sqft else 0.0
    est.price_sources["shell"] = (
        f"BENCHMARK: shell / core & shell + architecture only, priced at "
        f"${SHELL_COST_USD_PER_MW/1e6:,.1f}M per implied MW (within the ~$1.0-2.1M/MW "
        f"shell-and-core band; ~{SHELL_COST_USD_PER_MW/12_500_000:.0%} of a typical "
        f"all-in hard cost; ~${implied_shell_per_sqft:,.0f}/sq ft here). EXCLUDES the "
        f"IT power / electrical / mechanical chain to avoid double-counting with the "
        f"copper / steel / MW figures. See SOURCES.md."
    )

    # Battery-backup (UPS) metals provenance. The physical quantities below are the
    # backup-power slice of the expanded metals table; that table prices them as
    # CONTAINED METAL (refined-metal reference price), which is not the price of
    # battery-grade products (nickel sulphate, lithium carbonate). This panel keeps
    # both the top-down headline and the bottom-up lower-bound cross-check so the
    # sizing assumption is visible.
    est.price_sources["battery"] = (
        f"HEADLINE (WEF/Kearney 'From Minerals to Megawatts', Dec 2025, Fig. 4; "
        f"source: Bank of America Securities/IEA/Kearney): Li {est.battery_lithium_kg:,.0f} kg, "
        f"Ni {est.battery_nickel_kg:,.0f} kg, Co {est.battery_cobalt_kg:,.0f} kg, "
        f"Pb {est.battery_lead_kg:,.0f} kg, graphite {est.battery_graphite_kg:,.0f} kg "
        f"(real fleet mix: mostly Li-ion, lead-acid still present). LOWER-BOUND cross-check "
        f"(our own {UPS_RIDE_THROUGH_MIN:.0f}-min ride-through calc, Li-ion NMC811 only, "
        f"~{UPS_KWH_PER_MW:.0f} kWh/MW, IEA/ICCT/Argonne BatPaC intensity): Li "
        f"{est.battery_lithium_kg_lowerbound:,.0f} kg, Ni {est.battery_nickel_kg_lowerbound:,.0f} kg, "
        f"Co {est.battery_cobalt_kg_lowerbound:,.0f} kg (LFP alt: Li "
        f"{est.battery_lithium_kg_lfp_lowerbound:,.0f} kg, no Ni/Co) — the lower-bound comes out "
        f"~3-4x below the WEF headline, consistent with WEF assuming a longer effective runtime / "
        f"N+1 redundancy / blended fleet rather than a bare 5-minute minimum. Small at "
        f"data-center-UPS scale, far larger for grid-scale BESS co-located with a data center. "
        f"Headline quantities are priced as contained metal in the metals table. See SOURCES.md."
    )
    est.notes.append(
        "Battery-backup (UPS) metal quantities are small because data-center UPS "
        "only bridges minutes to generator start — unlike grid-scale BESS. Two "
        "figures are shown (WEF/Kearney top-down headline + our own bottom-up "
        "lower-bound cross-check) to make the sizing assumption visible. Their "
        "contained-metal value is included in the expanded metals table (headline "
        "basis), not as battery-grade product value."
    )

    # Aluminum provenance context (tonnage basis).
    est.price_sources["aluminum_qty"] = (
        f"{est.aluminum_tonnes:,.1f} t = {est.aluminum_tonnes / mw if mw else 0:.1f} t/MW x "
        f"{mw:,.1f} MW. Whole-facility figure (cooling + servers + backup + "
        f"electrical + networking) from WEF/Kearney 'From Minerals to Megawatts' "
        f"(Dec 2025), Fig. 4. See SOURCES.md."
    )

    # Totals. Headline total = land + shell base-building cost + contained-metal
    # value of all priced metals. Concrete (and stainless, where modelled) are
    # physical-quantity context lines and are NOT priced into the total.
    #
    # Split: FACILITY (campus / shell infrastructure) = land + shell + facility-side
    # metals; COMPUTE (equipment housed inside) = compute-side metals.
    est.material_cost_usd = mix["metals_usd"]
    est.facility_metals_usd = mix["facility_metals_usd"]
    est.compute_metals_usd = mix["compute_metals_usd"]
    est.facility_value_usd = (
        est.land_value_usd + est.shell_cost_usd + est.facility_metals_usd
    )
    est.compute_value_usd = est.compute_metals_usd
    est.total_site_value_usd = est.facility_value_usd + est.compute_value_usd

    est.google_maps_url = f"https://www.google.com/maps?q={lat},{lng}"

    return est
