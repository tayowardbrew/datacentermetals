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

# --- Benchmark assumptions (see SOURCES.md for provenance) ---

# Power density (watts per square foot of building space). Mid-range of the
# 200-400 W/sq ft modern-facility band. Source: TierPoint / Cadence.
POWER_DENSITY_W_PER_SQFT = 250.0

# Steel intensity (metric tons per square foot). Midpoint of 0.014-0.018.
# Source: Data Centre Magazine / impactECI.
STEEL_TONNES_PER_SQFT = 0.016

# Copper intensity (tonnes per MW). Lower bound = facility-only rule of thumb;
# default = including near-site power connections (anchored on Microsoft's
# ~80 MW Chicago site ~= 27 t/MW). Source: BloombergNEF / BHP.
COPPER_TONNES_PER_MW_FACILITY = 12.0
COPPER_TONNES_PER_MW_WITH_GRID = 26.0

# Concrete intensity (cubic meters per MW). Midpoint of 500-1,000.
# Source: impactECI / Cushman & Wakefield. Shown as a physical quantity only,
# NOT priced into the total (see SOURCES.md).
CONCRETE_M3_PER_MW = 750.0
# Rough density to also express concrete as tonnes for context (~2.4 t/m3).
CONCRETE_TONNES_PER_M3 = 2.4

# Static steel price (USD per metric ton). NOT a live quote: steel is not on the
# Metals.Dev free tier. Generic US structural/HRC benchmark. Source: SOURCES.md.
STATIC_STEEL_PRICE_USD_PER_TONNE = 900.0

# Shell / base-building construction cost, EXCLUDING the IT power chain /
# electrical / mechanical plant — i.e. land improvement, foundation, structural
# core & shell and architecture only. The power/M&E side is already captured via
# the MW / copper / steel figures, so including M&E here would double-count.
#
# Rather than hard-code a bare $/sq ft (which only weak, mutually-inconsistent
# blog sources give for shell-only), we derive shell cost from the well-sourced
# RELATIONSHIP: Turner & Townsend's cost split puts core/shell + architecture at
# ~14% of total construction (hard) cost for an air-cooled facility, with
# mechanical+electrical the remaining majority. We apply that 14% to a sourced
# all-in build cost of ~$11M per MW of IT capacity (JLL). See SOURCES.md.
TOTAL_BUILD_COST_USD_PER_MW = 11_000_000.0
SHELL_SHARE_OF_BUILD = 0.14

# Regional average commercial/industrial land price (USD per acre).
# Generic industrial land proxy, NOT power-ready data-center-premium land.
# Source: CBRE industrial land research. See SOURCES.md for the honesty caveat.
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
    acres: float = 0.0

    # Values (USD)
    land_value_usd: float = 0.0
    steel_cost_usd: float = 0.0
    copper_cost_usd: float = 0.0
    material_cost_usd: float = 0.0
    shell_cost_usd: float = 0.0
    total_site_value_usd: float = 0.0

    # Capacity / cooling (indicative) — populated from capacity.py
    capacity: dict = field(default_factory=dict)

    # Metadata / labels / honesty flags
    google_maps_url: str = ""
    notes: list = field(default_factory=list)
    price_sources: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def estimate_site(lat, lng, sqft, region, copper_price_usd_per_tonne,
                  copper_price_source, aluminum_price_usd_per_tonne=None,
                  aluminum_price_source=None):
    """
    Build the full site estimate.

    copper_price_usd_per_tonne may be None if no live price is available
    (e.g. no API key). In that case the copper cost line is reported as
    unavailable rather than fabricated, and it is excluded from the total.
    """
    lat, lng, sqft, region = validate_inputs(lat, lng, sqft, region)

    est = Estimate(lat=lat, lng=lng, sqft=sqft, region=region)

    # Physical quantities
    est.implied_mw = (sqft * POWER_DENSITY_W_PER_SQFT) / 1_000_000.0
    est.steel_tonnes = sqft * STEEL_TONNES_PER_SQFT
    est.copper_tonnes_facility = est.implied_mw * COPPER_TONNES_PER_MW_FACILITY
    est.copper_tonnes_with_grid = est.implied_mw * COPPER_TONNES_PER_MW_WITH_GRID
    est.concrete_m3 = est.implied_mw * CONCRETE_M3_PER_MW
    est.concrete_tonnes = est.concrete_m3 * CONCRETE_TONNES_PER_M3
    est.acres = sqft / SQFT_PER_ACRE

    # Land value (regional proxy)
    per_acre = LAND_PRICE_USD_PER_ACRE[region]
    est.land_value_usd = est.acres * per_acre
    est.price_sources["land"] = (
        f"Regional average proxy ({region}): ${per_acre:,.0f}/acre. "
        "NOT a parcel-level appraisal. See SOURCES.md."
    )

    # Steel cost (static price, clearly labeled)
    est.steel_cost_usd = est.steel_tonnes * STATIC_STEEL_PRICE_USD_PER_TONNE
    est.price_sources["steel"] = (
        f"STATIC benchmark ${STATIC_STEEL_PRICE_USD_PER_TONNE:,.0f}/tonne "
        "(steel not on Metals.Dev free tier). Not a live quote."
    )

    # Copper cost (live price if available). Use the with-grid tonnage as the
    # headline priced figure.
    if copper_price_usd_per_tonne is not None:
        est.copper_cost_usd = est.copper_tonnes_with_grid * copper_price_usd_per_tonne
        est.price_sources["copper"] = (
            f"LIVE price ${copper_price_usd_per_tonne:,.2f}/tonne "
            f"via {copper_price_source}."
        )
    else:
        est.copper_cost_usd = 0.0
        est.price_sources["copper"] = (
            f"Live copper price unavailable ({copper_price_source}). "
            "Copper cost excluded from total."
        )
        est.notes.append(
            "Copper cost could not be priced (no live price available), so it is "
            "excluded from the total site value. Configure METALS_DEV_API_KEY to "
            "include it."
        )

    # Aluminum: price is fetched if available, but no defensible intensity figure
    # is modeled in v1 (see SOURCES.md), so it is reported for reference only.
    if aluminum_price_usd_per_tonne is not None:
        est.price_sources["aluminum"] = (
            f"LIVE price ${aluminum_price_usd_per_tonne:,.2f}/tonne "
            f"via {aluminum_price_source} (reference only; no v1 intensity figure)."
        )

    # Shell / base-building construction cost (excludes the power/M&E chain, which
    # is already captured by the MW / copper / steel figures — including M&E here
    # would double-count). Derived as the sourced shell share (~14%) of a sourced
    # all-in $/MW build cost, applied to the implied MW. Labelled as a benchmark-
    # derived figure, not a live quote.
    shell_cost_per_mw = TOTAL_BUILD_COST_USD_PER_MW * SHELL_SHARE_OF_BUILD
    est.shell_cost_usd = est.implied_mw * shell_cost_per_mw
    implied_shell_per_sqft = (
        est.shell_cost_usd / sqft if sqft else 0.0
    )
    est.price_sources["shell"] = (
        f"BENCHMARK: shell / core & shell + architecture only, derived as "
        f"{SHELL_SHARE_OF_BUILD:.0%} (Turner & Townsend cost split) of a "
        f"${TOTAL_BUILD_COST_USD_PER_MW/1e6:,.0f}M/MW all-in build cost (JLL) = "
        f"${shell_cost_per_mw/1e6:,.2f}M/MW (~${implied_shell_per_sqft:,.0f}/sq ft "
        f"here). EXCLUDES the IT power / electrical / mechanical chain to avoid "
        f"double-counting with the copper/steel/MW figures. See SOURCES.md."
    )

    # Indicative rack-capacity and cooling characterisation (not priced).
    est.capacity = estimate_capacity(sqft, est.implied_mw).to_dict()

    # Totals. Headline total = land + priced materials (steel + copper) + shell
    # base-building cost.
    est.material_cost_usd = est.steel_cost_usd + est.copper_cost_usd
    est.total_site_value_usd = (
        est.land_value_usd + est.material_cost_usd + est.shell_cost_usd
    )

    est.google_maps_url = f"https://www.google.com/maps?q={lat},{lng}"

    return est
