"""
Data-center BUILD TYPE profiles: three generic archetypes that change the metals
MIX per MW (not just power density), and so change the metals-tonnage estimate.

The archetypes are deliberately generic. The research behind them started from
the publicly reported practices of leading Western hyperscale builders, but no
company is named here or in the UI; the profiles describe build approaches.

HOW A PROFILE FEEDS THE ESTIMATE
--------------------------------
* power_density_w_per_sqft -- converts a drawn parcel's area to implied IT MW
  (only used when the user has NOT stated a capacity in the power layer).
* facility_multipliers     -- scale the FACILITY-side per-MW intensity of copper,
  aluminum and structural steel (metals_mix.py). Compute-side intensities
  (servers / networking) are NOT varied: no source quantifies how server metal
  content differs by building type, and the WEF baseline already reflects a
  CPU/GPU fleet mix.
* concrete_multiplier      -- scales concrete m3/MW (context line, not priced).
* stainless_t_per_mw       -- welded stainless coolant pipework, a QUANTITY only
  (not priced; low-confidence derivation).
* shell_cost_usd_per_mw    -- shell / core cost per MW.
* pue                      -- power usage effectiveness, for the power layer's
  facility-energy figure.

CONFIDENCE -- READ BEFORE TRUSTING THE MULTIPLIERS
--------------------------------------------------
No primary engineering source compares the metals mix across build types. The
hyperscale campus profile IS the tool's existing, cross-validated baseline. For
the other two, the multipliers below are a mix of (a) secondary/trade-press
figures, (b) values derived from density changes, and (c) explicit judgement
calls. Each one carries its confidence and basis; see SOURCES.md entry 15. They
are directional estimates, not measured material take-offs, and the UI says so.
"""

BUILD_TYPES = {
    "hyperscale": {
        "key": "hyperscale",
        "name": "Hyperscale campus",
        "icon": "campus",
        "tagline": "Large multi-hall campus, built on site, mostly air or hybrid cooled.",
        "detail": [
            "The reference case: the tool's baseline benchmarks describe this kind of build.",
            "Lots of floor area per MW goes to moving air, so it uses more building and "
            "more aluminium in air-handler coils.",
            "Cooling pipework is ordinary carbon steel, so there is little stainless.",
        ],
        "typical": "~10-40 kW per rack; 24-36 months to energise.",
        # Baseline: 250 W/sq ft, mid of the sourced 200-400 band (SOURCES.md 1).
        "power_density_w_per_sqft": 250.0,
        "facility_multipliers": {"copper": 1.0, "aluminum": 1.0, "steel": 1.0},
        "concrete_multiplier": 1.0,
        "stainless_t_per_mw": 0.0,
        "shell_cost_usd_per_mw": 1_500_000.0,
        # Owner-operated hyperscale averages ~1.10-1.15, colocation ~1.58+ (2025
        # global industry survey, SOURCES.md 15). 1.2 sits between the two for a hybrid hyperscale/colo campus.
        "pue": 1.2,
        # Indicative compute-hardware capex per MW: no reliable public figure for
        # a mixed CPU/GPU campus fleet, so none is shown (see SOURCES.md 16).
        "compute_capex_usd_per_mw": None,
        "confidence": {
            "copper": "high (baseline, cross-validated)",
            "aluminum": "medium (baseline, WEF/Kearney)",
            "steel": "medium-high (baseline)",
            "concrete": "medium (baseline range)",
            "density": "medium",
        },
    },
    "modular": {
        "key": "modular",
        "name": "Modular / prefab",
        "icon": "modular",
        "tagline": "Factory-built, steel-framed power and cooling modules set on site pads.",
        "detail": [
            "The electrical and cooling equipment inside is much the same, so copper "
            "per MW barely changes.",
            "Steel module frames replace much of the poured concrete shell: site "
            "concrete falls sharply and steel rises somewhat.",
            "Faster to deliver and usually cheaper per MW, at some cost in "
            "efficiency.",
        ],
        "typical": "Similar rack densities; ~12-18 months to deliver.",
        # Judgement (low confidence): dense inside each module, spread out on site.
        "power_density_w_per_sqft": 200.0,
        # copper: no source quantifies a difference (judgement, range 0.9-1.1).
        # aluminum: enclosures/panels sometimes aluminium, unquantified (range 1.0-1.2).
        # steel: steel frames replace concrete shell; a power/cooling vendor's
        #   steel-frame modular life-cycle study (tonnages not public); derived
        #   range 1.1-1.4.
        "facility_multipliers": {"copper": 1.0, "aluminum": 1.1, "steel": 1.25},
        # Same vendor study: >50% lower embodied carbon, mostly from less concrete
        # (range 0.4-0.7).
        "concrete_multiplier": 0.5,
        "stainless_t_per_mw": 0.0,
        # Prefab power/cooling modules quoted at ~13%+ lower first cost; applied to
        # the shell line as a hedged ~13% reduction (low confidence).
        "shell_cost_usd_per_mw": 1_300_000.0,
        # No source found for prefab-specific PUE; judgement between hyperscale
        # (~1.1-1.2) and the global average (1.54, 2025 industry survey).
        "pue": 1.3,
        "compute_capex_usd_per_mw": None,
        "confidence": {
            "copper": "low (no source; judgement)",
            "aluminum": "low (judgement)",
            "steel": "low-medium (derived from a vendor study)",
            "concrete": "low-medium (same vendor study)",
            "density": "low (judgement)",
        },
    },
    "ai_liquid": {
        "key": "ai_liquid",
        "name": "Liquid-cooled AI",
        "icon": "liquid",
        "tagline": "Dense GPU halls with direct-to-chip liquid cooling and heavy power distribution.",
        "detail": [
            "Far more current per MW means more copper in switchgear, busway and "
            "cabling, plus copper cold plates.",
            "Power is packed into much less floor area, so building steel and "
            "concrete per MW fall even though each square foot is built heavier.",
            "Air-handler aluminium shrinks, and welded stainless coolant pipework "
            "is added.",
        ],
        "typical": "~100-230 kW per rack at the high end; liquid removes most of the heat.",
        # Sourced: ~1,200 W/sq ft on a 1.2 GW / ~1M sq ft liquid-cooled project;
        # 600-1,200 band, 800 chosen as a mid value (medium confidence).
        "power_density_w_per_sqft": 800.0,
        # copper: trade-press figures 20-40 vs 8-15 t/MW (a copper industry
        #   association) and 15-21 vs up to 47 t/MW (a mining major's analysis);
        #   these mix inside-the-fence and near-site scope (SOURCES.md 15).
        #   1.5x (range 1.3-2.0), med-low. Next-gen 800 V DC distribution could cut
        #   distribution copper by up to ~45%, pulling this back toward 1.1-1.3.
        # aluminum: liquid removes 70-90% of heat, fewer air coils; dry coolers still
        #   use aluminium fins. 0.8 (range 0.7-1.0), judgement.
        # steel: floor area per MW falls 2.5-5x but slabs/frames are heavier per
        #   sq ft (racks 4,000-8,000 lb). 0.55 per MW (range 0.4-0.7), derived.
        "facility_multipliers": {"copper": 1.5, "aluminum": 0.8, "steel": 0.55},
        # Thicker slabs but much less area; equipment-yard foundations still scale
        # with MW. 0.7 (range 0.5-0.9), judgement.
        "concrete_multiplier": 0.7,
        # Derived: a 100 MW AI campus needs ~50,000-200,000 linear ft of 1/2"-4"
        # welded stainless pipe (industry estimate) at ~2-5 lb/ft for Schedule 10S
        # => ~0.5-5 t/MW; 1.5 t/MW midpoint. LOW confidence, quantity only.
        "stainless_t_per_mw": 1.5,
        # Cost-consultancy index (SOURCES.md 9): core/shell is ~9% of a liquid-cooled AI build vs ~14%
        # air-cooled, but of a higher all-in cost (~$14M+/MW vs ~$11M/MW), which
        # lands at a similar shell $/MW. Kept at the baseline $1.5M/MW (hedged).
        "shell_cost_usd_per_mw": 1_500_000.0,
        # Liquid cooling allows lower PUE; hyperscale AI builds report ~1.1-1.2.
        "pue": 1.15,
        # Indicative compute hardware (servers + networking) capex for a current
        # rack-scale GPU build: ~$26.1M per MW (2026 independent research cost
        # model of a 1 GW hyperscaler-owned AI campus; SOURCES.md 16). Shown as a
        # REFERENCE ONLY, never added to the commodity-basis total.
        "compute_capex_usd_per_mw": 26_100_000.0,
        "confidence": {
            "copper": "medium-low (trade press, mixed scope)",
            "aluminum": "low (judgement)",
            "steel": "low-medium (derived from density)",
            "concrete": "low (judgement)",
            "density": "medium",
        },
    },
}

DEFAULT_BUILD_TYPE = "hyperscale"


def get_build_type(key):
    """Return the profile for `key` (case-insensitive), or raise KeyError."""
    k = (key or DEFAULT_BUILD_TYPE).strip().lower()
    return BUILD_TYPES[k]


def public_profiles():
    """Profiles for the UI: copy, icon, and the numbers that drive the estimate."""
    out = []
    for bt in BUILD_TYPES.values():
        out.append({
            "key": bt["key"],
            "name": bt["name"],
            "icon": bt["icon"],
            "tagline": bt["tagline"],
            "detail": bt["detail"],
            "typical": bt["typical"],
            "power_density_w_per_sqft": bt["power_density_w_per_sqft"],
            "facility_multipliers": bt["facility_multipliers"],
            "concrete_multiplier": bt["concrete_multiplier"],
            "stainless_t_per_mw": bt["stainless_t_per_mw"],
            "pue": bt["pue"],
            "shell_cost_usd_per_mw": bt["shell_cost_usd_per_mw"],
            "compute_capex_usd_per_mw": bt["compute_capex_usd_per_mw"],
            "confidence": bt["confidence"],
        })
    return out
