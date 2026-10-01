"""
Indicative rack-capacity and cooling-method estimation.

Given a building footprint (gross sq ft) and the implied IT power (MW) that
estimator.py already derives from the power-density benchmark, this module gives:

  (a) a rough rack count, from a white-space ratio and a rack footprint, and the
      implied average power per rack; and
  (b) an indicative cooling method, from a simple tiered rule keyed on the implied
      power density per rack.

These are deliberately labelled INDICATIVE rules of thumb, not an engineering
design. Every constant below is documented in SOURCES.md with its source and the
honest caveat that real facilities vary widely. Nothing here is priced into the
site value — it is a capacity/characterisation layer on top of the value model.
"""

from dataclasses import dataclass, field, asdict

# --- Benchmark assumptions (see SOURCES.md for provenance) ---

# Fraction of GROSS building area that becomes usable "white space" (raised-floor
# / IT hall). The remainder is electrical rooms, cooling plant, offices, loading,
# circulation. RICS Construction Journal: net white space is generally 40-50% of
# gross internal area (excluding office blocks). 0.45 = midpoint. See SOURCES.md.
WHITE_SPACE_FRACTION = 0.45

# Floor area consumed PER RACK of WHITE SPACE, including its share of aisles /
# hot-cold-aisle spacing (not just the ~2.6 sq ft cabinet footprint — the aisle
# allowance dominates). ~20 sq ft/rack is the standard planning default (range
# 15-25 for air-cooled). NOTE: this is sq ft of WHITE SPACE per rack, so it is
# applied AFTER the white-space ratio, not to gross area. See SOURCES.md.
SQFT_WHITE_SPACE_PER_RACK = 20.0

# Cooling-method tiers keyed on implied average power per rack (kW/rack).
# Thresholds anchored on ASHRAE TC 9.9 (~20 kW is the air→liquid transition; H1
# high-density class >20 kW) with higher bands from vendor/trade consensus
# (Schneider, Vertiv, Introl). Indicative bands, not hard specs. See SOURCES.md.
# (lower_bound_kw_inclusive, label, description)
COOLING_TIERS = [
    (
        0.0,
        "Air cooling (CRAC/CRAH)",
        "Traditional perimeter air cooling with raised floor and hot-aisle/"
        "cold-aisle containment. The air-cooling comfort zone, below ~20 kW/rack "
        "(ASHRAE TC 9.9).",
    ),
    (
        20.0,
        "Air at its ceiling: containment + rear-door heat exchangers",
        "Around the ~20-30 kW/rack band air cooling reaches its practical ceiling; "
        "full containment plus in-row or rear-door (air-side) heat exchangers are "
        "used, and ASHRAE begins recommending liquid above ~20 kW/rack.",
    ),
    (
        30.0,
        "Direct-to-chip liquid cooling",
        "Around ~30-50 kW/rack direct-to-chip (cold-plate) liquid cooling becomes "
        "the norm; air alone becomes airflow-limited past ~40-50 kW/rack.",
    ),
    (
        50.0,
        "Direct-to-chip and/or immersion liquid cooling",
        "Dense AI/HPC GPU clusters (>~50 kW/rack): direct-to-chip liquid at scale "
        "and/or immersion cooling; air is insufficient above ~80-100 kW/rack.",
    ),
]


@dataclass
class CapacityEstimate:
    white_space_fraction: float = WHITE_SPACE_FRACTION
    white_space_sqft: float = 0.0
    sqft_per_rack: float = SQFT_WHITE_SPACE_PER_RACK
    estimated_racks: int = 0
    avg_kw_per_rack: float = 0.0
    cooling_method: str = ""
    cooling_detail: str = ""
    notes: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def cooling_for_density(kw_per_rack):
    """Return (label, detail) for the highest tier whose threshold is met."""
    chosen = COOLING_TIERS[0]
    for tier in COOLING_TIERS:
        if kw_per_rack >= tier[0]:
            chosen = tier
    return chosen[1], chosen[2]


def estimate_capacity(sqft, implied_mw):
    """
    Build the indicative capacity/cooling estimate.

    sqft: gross building footprint (sq ft).
    implied_mw: IT power already derived by estimator.py from the W/sq ft density.
    """
    cap = CapacityEstimate()
    cap.white_space_sqft = sqft * WHITE_SPACE_FRACTION
    cap.estimated_racks = int(cap.white_space_sqft // SQFT_WHITE_SPACE_PER_RACK)

    total_kw = implied_mw * 1000.0
    if cap.estimated_racks > 0:
        cap.avg_kw_per_rack = total_kw / cap.estimated_racks
    else:
        cap.avg_kw_per_rack = 0.0

    cap.cooling_method, cap.cooling_detail = cooling_for_density(cap.avg_kw_per_rack)

    cap.notes.append(
        "Rack count and cooling method are INDICATIVE rules of thumb (see SOURCES.md), "
        "not an engineering design. Rack count assumes ~"
        f"{WHITE_SPACE_FRACTION:.0%} of gross area is white space at ~"
        f"{SQFT_WHITE_SPACE_PER_RACK:.0f} sq ft/rack incl. aisles. The cooling tier is "
        "keyed on the implied average kW/rack."
    )
    return cap
