"""
Power / capacity layer: an explicit IT-capacity input that feeds the metals
estimate, complementary to (and cross-checked against) the parcel-size estimate.

WHY
---
The parcel route infers MW from drawn area x a power-density assumption, which is
the weakest-sourced step in the model (SOURCES.md 1). Often the user already knows
the planned capacity (from a utility filing, a press release, a grid-queue entry).
This layer lets them state it directly, in MW of IT capacity (the app's existing
unit convention) or as annual energy in GWh/yr, and:

  * uses the STATED capacity, when given, to drive every per-MW quantity (metals,
    concrete, shell cost, rack density);
  * keeps the parcel-implied MW alongside it and reports the implied W/sq ft, so a
    parcel that is implausibly small or large for the stated capacity is flagged;
  * converts capacity <-> annual energy (GWh/yr) using a utilization assumption
    and the build type's PUE, and prices that energy at the parcel STATE's
    average industrial electricity tariff (context only, never in site value).

ASSUMPTIONS (see SOURCES.md 17)
-------------------------------
* Utilization default 67%: the California Energy Commission's 2024 IEPR data-
  center forecast assumes data-center peak load is ~67% of requested capacity,
  based on existing data centers. We use it as the AVERAGE utilization of
  nameplate IT capacity, which is a simplification (annual average sits at or
  below peak). Published observed load factors range from >52% to ~90%, so the
  value is user-adjustable.
* IT energy (GWh/yr) = MW x 8,760 h x utilization / 1,000.
* Facility energy = IT energy x PUE (from the build type).
* State industrial tariff: US EIA Electric Power Monthly, Table 5.6.B, average
  price to industrial customers by state, year-to-date through July 2026
  (cents/kWh). Large data centers often contract below the state industrial
  average, so this is an indicative benchmark only.
"""

HOURS_PER_YEAR = 8_760.0
DEFAULT_UTILIZATION = 0.67
MIN_UTILIZATION, MAX_UTILIZATION = 0.10, 1.00
MAX_STATED_MW = 10_000.0  # 10 GW: well above any single announced campus phase

VALID_UNITS = ("mw", "gwh")

# EIA Electric Power Monthly Table 5.6.B, industrial sector, YTD through July 2026,
# cents per kWh. US total: 9.03. Source file:
# https://www.eia.gov/electricity/monthly/xls/table_5_06_b.xlsx
EIA_INDUSTRIAL_CENTS_PER_KWH_2026YTD = {
    "AK": 24.02, "AL": 7.93, "AR": 6.82, "AZ": 7.66, "CA": 20.74, "CO": 9.6, "CT": 18.5, "DC": 20.98,
    "DE": 11.73, "FL": 9.21, "GA": 7.99, "HI": 37.59, "IA": 7.38, "ID": 8.14, "IL": 10.24, "IN": 9.15,
    "KS": 8.3, "KY": 7.5, "LA": 6.65, "MA": 19.99, "MD": 15.28, "ME": 15.61, "MI": 9.33, "MN": 9.75,
    "MO": 8.62, "MS": 7.66, "MT": 6.83, "NC": 7.91, "ND": 8.18, "NE": 8.65, "NH": 18.21, "NJ": 15.18,
    "NM": 5.21, "NV": 8.43, "NY": 10.24, "OH": 10.32, "OK": 6.69, "OR": 8.33, "PA": 10.93, "RI": 21.86,
    "SC": 7.85, "SD": 9.46, "TN": 6.82, "TX": 6.72, "UT": 8.58, "VA": 10.08, "VT": 12.93, "WA": 7.15,
    "WI": 9.39, "WV": 8.55, "WY": 8.78,
}
EIA_US_INDUSTRIAL_CENTS_PER_KWH_2026YTD = 9.03
EIA_SOURCE = (
    "US EIA Electric Power Monthly, Table 5.6.B (industrial sector, average price, "
    "YTD through July 2026)."
)


class PowerInputError(ValueError):
    """Raised for invalid power-layer input."""


def parse_power_inputs(value, unit, utilization):
    """
    Validate the optional stated capacity. Returns (value or None, unit, util).
    An empty / missing value means "no stated capacity; use the parcel".
    """
    unit = (unit or "mw").strip().lower()
    if unit not in VALID_UNITS:
        raise PowerInputError("Capacity unit must be 'mw' or 'gwh'.")

    if utilization in (None, ""):
        util = DEFAULT_UTILIZATION
    else:
        try:
            util = float(utilization)
        except (TypeError, ValueError):
            raise PowerInputError("Utilization must be a number.")
        if util > 1.0:  # accept a percentage too
            util /= 100.0
        if not (MIN_UTILIZATION <= util <= MAX_UTILIZATION):
            raise PowerInputError("Utilization must be between 10% and 100%.")

    if value in (None, ""):
        return None, unit, util
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise PowerInputError("Stated capacity must be a number.")
    if v <= 0:
        raise PowerInputError("Stated capacity must be greater than zero.")
    mw = v if unit == "mw" else v * 1000.0 / (HOURS_PER_YEAR * util)
    if mw > MAX_STATED_MW:
        raise PowerInputError(
            "Stated capacity looks implausibly large (>10 GW of IT load). "
            "Please double-check the value and unit."
        )
    return v, unit, util


def stated_to_mw(value, unit, util):
    if value is None:
        return None
    return value if unit == "mw" else value * 1000.0 / (HOURS_PER_YEAR * util)


def it_gwh_per_year(mw, util):
    return mw * HOURS_PER_YEAR * util / 1000.0


def build_power_layer(parcel_mw, sqft, stated_value, stated_unit, util, pue,
                      state_code=None):
    """
    Assemble the power-layer block returned to the UI.

    Returns a dict with the MW that DRIVES the metals estimate, both the parcel-
    and stated-capacity figures, annual energy and an indicative state power cost.
    """
    stated_mw = stated_to_mw(stated_value, stated_unit, util)
    basis = "stated" if stated_mw is not None else "parcel"
    driving_mw = stated_mw if stated_mw is not None else parcel_mw

    it_gwh = it_gwh_per_year(driving_mw, util)
    fac_gwh = it_gwh * pue

    cents = EIA_INDUSTRIAL_CENTS_PER_KWH_2026YTD.get((state_code or "").upper())
    tariff_label = None
    if cents is not None:
        tariff_label = f"{state_code.upper()} industrial average"
    annual_cost = fac_gwh * 1e6 * cents / 100.0 if cents is not None else None

    out = {
        "basis": basis,
        "driving_mw": driving_mw,
        "parcel_mw": parcel_mw,
        "stated_mw": stated_mw,
        "stated_value": stated_value,
        "stated_unit": stated_unit if stated_value is not None else None,
        "utilization": util,
        "pue": pue,
        "it_gwh_per_year": it_gwh,
        "facility_gwh_per_year": fac_gwh,
        "avg_facility_mw": fac_gwh * 1000.0 / HOURS_PER_YEAR,
        "tariff_cents_per_kwh": cents,
        "tariff_label": tariff_label,
        "us_avg_tariff_cents_per_kwh": EIA_US_INDUSTRIAL_CENTS_PER_KWH_2026YTD,
        "annual_power_cost_usd": annual_cost,
        "tariff_source": EIA_SOURCE if cents is not None else None,
        "implied_w_per_sqft": (stated_mw * 1e6 / sqft) if (stated_mw and sqft) else None,
        "stated_vs_parcel": (stated_mw / parcel_mw) if (stated_mw and parcel_mw) else None,
        "check": None,
    }

    ratio = out["stated_vs_parcel"]
    if ratio is not None:
        w = out["implied_w_per_sqft"]
        if ratio > 1.5:
            out["check"] = (
                f"The stated capacity is {ratio:.1f}x what this parcel supports at the "
                f"selected build type's density (it implies ~{w:,.0f} W/sq ft). The "
                "parcel may be too small, or the site is multi-storey / denser than "
                "assumed. Metals follow the stated capacity."
            )
        elif ratio < 0.67:
            out["check"] = (
                f"The stated capacity is only {ratio:.2f}x what this parcel could hold "
                f"at the selected density (~{w:,.0f} W/sq ft): the parcel has spare "
                "room, or this is an early phase. Metals follow the stated capacity."
            )
        else:
            out["check"] = (
                f"Stated capacity is consistent with the parcel ({ratio:.2f}x the "
                f"parcel-implied MW, ~{w:,.0f} W/sq ft)."
            )
    return out
