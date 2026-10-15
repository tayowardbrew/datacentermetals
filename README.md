# Data Center Site Value Estimator

Estimate the implied power capacity, materials intensity, construction cost and total
implied value of a candidate data center parcel by **searching for a location, then
drawing the parcel on satellite imagery** (or entering raw coordinates and a footprint).
A free location-search box flies the map to any address/area/city; you then draw the
parcel and the tool **auto-detects the state and county and suggests a land comparable**
you can confirm or override.

The tool estimates:

- **Footprint area** from a parcel you **draw on the map** (polygon or rectangle),
  computed geodesically (spherical-excess area, correct at scale), or from a manual
  square-footage entry.
- **Three build-type modes** (Hyperscale campus, Modular / prefab, Liquid-cooled AI),
  each with its own power density and **facility metals mix** (copper, aluminum,
  structural steel, concrete and stainless multipliers vs the baseline), selectable as
  cards with a "+" panel explaining how each differs. The choice changes the metals
  tonnage, not just the label. Multipliers are hedged and sourced in SOURCES.md 15.
- **Implied power capacity (MW)** from the build type's watts-per-square-foot density,
  **or a stated capacity** (MW of IT load, or GWh/yr of IT energy) via the
  **power / capacity layer**, which then drives every per-MW quantity while the
  parcel-based figure is kept alongside as a cross-check. Outputs annual IT and
  facility energy (GWh/yr) and an indicative annual power cost at the parcel state's
  industrial tariff (US EIA).
- **Shell / base-building construction cost**, derived as the sourced shell/core share
  (~14%, Turner & Townsend) of an all-in $/MW build cost — **deliberately excluding the
  power / electrical / mechanical chain** (already captured by the MW / copper / steel
  figures) to avoid double-counting.
- **Steel tonnage** from a sourced material-intensity benchmark (0.016 t/sq ft,
  re-verified against multiple 2026 sources).
- **Copper tonnage** (facility-only and including near-site power connections) from
  a sourced tonnes-per-MW benchmark, anchored on a real disclosed project and
  re-verified against the Copper Development Association's 2026 20-40 t/MW range.
- **Aluminum tonnage** (11.3 t/MW, priced live) from the World Economic Forum /
  Kearney **"From Minerals to Megawatts"** white paper (Dec 2025), a whole-facility
  figure sourced to Bank of America Securities / IEA / Kearney analysis.
- **Battery-backup (UPS) metals** (lithium, nickel, cobalt, lead, graphite) — a
  **headline** figure from the same WEF/Kearney report (reflecting the real
  installed fleet mix, still part Li-ion/part lead-acid) shown alongside the tool's
  own **lower-bound cross-check** (a 5-minute-ride-through calculation using IEA /
  Argonne BatPaC cathode intensity, ~3-4x below the headline). Shown as physical
  quantities (small at UPS scale) to connect the build to the battery-metals / PGM
  mining angle. Not priced into the total.
- **Rack capacity & cooling method (indicative):** an estimated rack count (from a
  sourced white-space ratio and sq ft/rack) and the cooling method typical at the
  implied kW/rack density (air → rear-door → direct-to-chip → immersion).
- **Concrete volume/tonnage** as a context line item (shown, not priced).
- **11 metals with a facility vs compute split:** steel, copper, aluminum, nickel,
  lead, tin, silver, gold, cobalt, lithium and gallium, each split between the
  facility (cooling, power distribution, backup, structure, near-site connections)
  and the compute equipment (servers, chips, racks, networking), from the WEF/Kearney
  component table (SOURCES.md 14). Valued as contained metal.
- **Live metal prices** via the [Metals.Dev](https://metals.dev/) API (free tier):
  copper, aluminum, nickel, lead, silver, gold. Tin, cobalt, lithium, gallium and
  steel are not on Metals.Dev and use dated, labelled static benchmarks.
- **Land value** via a **granular, auto-detected and confirmable comparable** at
  **state + county** level: a real quoted data-center-land $/acre for named counties
  (Loudoun, Prince William, Maricopa, Franklin/Licking…), falling back to the state USDA
  agricultural raw-land floor (AK/HI/DC: national proxy) — with the tier always shown,
  the state's raw-land value vs the US average, and an honest raw-vs-DC-land caveat.
  The detected State + County are editable. Optional secondary
  [RentCast](https://developers.rentcast.io/) AVM lookup.
- **Location search** above the map (free [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/),
  no API key): type an address/area/city, pick a result, the map flies there.
- **Total implied site value today** = land value + shell cost + priced metals,
  **split into (a) facility / campus infrastructure** (land + shell + facility-side
  metals) **and (b) compute equipment** (metals contained in the servers, chips,
  racks and networking), broken down line by line. For the Liquid-cooled AI type a
  compute-hardware purchase-cost reference (~$26M/MW) is shown for scale, outside
  the total.
- A **shareable link**: the drawn parcel is encoded into the page URL, so opening the
  same link on another device reproduces the identical parcel and estimate (no account
  or backend state needed). Plus a **Google Maps link** and an **inline satellite view**
  (Leaflet + free Esri World Imagery tiles, no API key).

Every benchmark figure is documented in [`SOURCES.md`](./SOURCES.md) with its source,
URL, and last-verified date.

---

## Why this matters (the commercial angle)

An early, defensible estimate of a data center site's implied materials-and-land value
can support a **collateral-value argument for asset-backed debt** raised against the
site *before or during* construction — when there is no completed, income-producing
asset to underwrite yet, but there is a parcel and a known build spec. This tool takes a
**commodities / materials-intensity lens** (steel, copper, and their live prices) and
applies it to **AI / data-center infrastructure**, extending the same analytical frame
used for agri-commodities trade finance and EV/battery-metals gigafactory analysis into
the data-center buildout.

---

## Understanding the Controls (plain-language glossary)

- **Latitude / Longitude** — the exact map coordinates of the parcel. Auto-filled when you draw a shape on the map or use the place search; you normally never type these by hand.
- **Square Footage** — size of the building footprint, in square feet. Used to estimate power capacity when you haven't entered a planned capacity directly (see below).
- **US State / US County** — auto-detected from where you drew the parcel. Used to pick the right regional land-price comp and state electricity tariff. You can type to override if auto-detect gets it wrong.
- **Build Type cards** (Hyperscale campus / Modular-prefab / Liquid-cooled AI) — pick which kind of data center this is. This changes the *entire metals mix* per MW, not just power density — e.g. a liquid-cooled AI build uses more copper (denser power/cooling gear) but less building steel (far more power fits in less floor area) than a hyperscale campus. Press the "+" on each card to see exactly how it differs, with sourcing/confidence notes.
- **Planned IT Capacity** (optional, MW or GWh/yr) — fill this in only if you already know the real planned power capacity (e.g. from a press release or utility filing). If left blank, the tool estimates capacity from your square footage and the selected build type's power density instead. If you provide BOTH a capacity and a parcel, the tool cross-checks them and flags it if the stated capacity looks implausible for that parcel size (see Avg Utilization below for the related unit conversion).
- **Avg Utilization** (default 67%) — what percentage of maximum rated capacity the facility actually draws on average over a year (a data center never runs flat-out every second — there's downtime, maintenance, lighter-load periods). This is what converts a peak MW figure into a realistic annual GWh/yr energy figure, which then feeds the metals and cost totals. Adjustable if you think a specific site runs harder or lighter than that.
- **Place Search** — a text box to jump the map to a location instead of scrolling/zooming manually. Doesn't affect the estimate itself, just navigation.
- **Land Comp Override** — lets you manually type in a known $/acre land value for a specific area if you have a better number than the tool's own automatic three-tier lookup (real metro-level deals → state-level USDA proxy → generic regional fallback, see Land Value section below).

---

## Honesty about scope (read this before trusting a number)

This is a **portfolio MVP**, not a production appraisal tool. It is deliberately precise
about what each number is:

| Line item            | What it actually is |
|----------------------|---------------------|
| Footprint area       | **Geodesically computed** from the drawn parcel (correct at scale), or a manual entry. |
| Power capacity (MW)  | An **assumption** from the build type's W/sq ft density, **or the user's stated capacity** (MW or GWh/yr) when given. |
| Build-type metals mix | **Directional multipliers** on facility copper / aluminum / steel / concrete. Baseline is sourced; most others are secondary-source or judgement calls (confidence shown in SOURCES.md 15). |
| Annual energy (GWh/yr) | MW x 8,760 h x an **adjustable utilization assumption** (default 67%) x PUE. |
| Power cost           | **Indicative**: state industrial average tariff (US EIA). Not in the site value. |
| Shell cost           | A **benchmark-derived** figure (sourced % of a sourced $/MW build), **excluding** the power/M&E chain to avoid double-counting. |
| Steel / copper tonnage | **Researched benchmarks** (material-intensity figures), not measured; both re-verified against 2026 sources. |
| Other metal tonnage  | **Reputable-secondary component table** (WEF/Kearney Dec 2025, Fig. 4), split facility vs compute. |
| Copper, aluminum, nickel, lead, silver, gold price | A **genuine live API call** to Metals.Dev (when a key is configured). |
| Steel, tin, cobalt, lithium, gallium price | **Static, dated benchmarks** — not on Metals.Dev. Labelled STATIC. |
| Metal values         | **Contained metal** (tonnes x refined-metal price), not scrap-recovery value or battery-grade product price. |
| Compute value        | Metals contained in the compute equipment; equipment purchase cost is shown as a reference only, outside the total. |
| Battery (UPS) metals | **Two figures**: WEF/Kearney headline (real fleet mix) + our own 5-min-ride-through lower-bound cross-check; small at UPS scale; headline quantities valued as contained metal in the metals table. |
| Rack count / cooling | **Indicative rules of thumb** (white-space ratio, sq ft/rack, kW/rack cooling bands), not an engineering design. |
| Land value           | A **state + county comparable** (county DC-land transaction → state USDA ag proxy → national proxy), tier shown; **not a parcel-level appraisal**. |
| Location detection   | **Free OpenStreetMap Nominatim** forward + reverse geocoding (debounced, rate-limited per policy). |
| RentCast AVM         | An **optional** secondary live lookup; coverage for raw coordinates is uncertain. |
| Concrete             | Shown for context only; **not priced into the total**. |

The UI badges every figure (ASSUMPTION / BENCHMARK / LIVE PRICE / STATIC PRICE /
REGIONAL PROXY) so no number is presented as more solid than it is.

---

## Roadmap / Not Yet Built

These are deliberately **not** attempted in this version and are called out honestly:

- **(a) *Automated* plot-size detection from satellite imagery via computer vision.**
  Still not attempted — automatic parcel-boundary detection is a multi-day build. The
  tool now supports **user-drawn** parcels (polygon/rectangle) with geodesic area
  computation, plus manual square-footage input, but it does not yet detect the
  footprint for you.
- **(b) True parcel-level land appraisal.** The land figure is now **granular and
  auto-detected** (real quoted DC-land transactions for named hotspots, else the state
  USDA agricultural raw-land floor, else a broad region proxy) and user-confirmable, but
  it is still **not a parcel-level appraisal**. A real appraisal would require parcel
  records, comparables, zoning, and power/water availability — none of which a raw
  coordinate provides. Granular free DC-land data is strong for Northern Virginia,
  Phoenix, Columbus and Chicago; weaker (listing averages) for Dallas-Fort Worth; and
  only the agricultural proxy exists for some markets (Salt Lake City, Omaha, Quincy WA).
- **(c) Aluminum precision.** Resolved: aluminum is now priced from a
  reputable-secondary whole-facility benchmark (WEF/Kearney, Dec 2025, 11.3 t/MW,
  sourced to Bank of America Securities/IEA/Kearney) — a clear upgrade over an
  earlier bottom-up lower-bound estimate used before that source was found.
- **(d) Stainless steel as a separate line.** Still no citable stainless-per-MW figure.
  For the Liquid-cooled AI build type only, a low-confidence derived quantity
  (~1.5 t/MW of coolant pipework) is shown, not priced (SOURCES.md 15); otherwise it
  stays folded into the steel band (SOURCES.md 12).
- **(f) Build-type metals multipliers from primary data.** The modular and AI
  multipliers are directional (secondary sources and judgement calls). A real
  material take-off per archetype would replace them.
- **(e) Sensitivity / range outputs.** Currently single-point mid-range estimates; a
  future version could show low/high bands from the sourced ranges.

---

## Running it locally

Requirements: Python 3.9+.

```bash
cd datacentermetals

# 1. Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. (Optional) configure API keys — the app runs fine WITHOUT them
cp .env.example .env
#   then edit .env and paste your keys, and load them:
export $(grep -v '^#' .env | xargs)   # Linux/macOS
#   (or just: export METALS_DEV_API_KEY=your_key_here)

# 3. Run the server
python app.py
#   then open http://127.0.0.1:5000
```

Change the port with `PORT=8080 python app.py`.

### Environment variables

| Variable             | Required? | Purpose |
|----------------------|-----------|---------|
| `METALS_DEV_API_KEY` | Optional  | Live copper, aluminum, nickel, lead, silver and gold prices from Metals.Dev (free tier, no card). Without it, those metals' values are excluded from the total (tonnage still shown) and clearly labeled; static-priced metals are unaffected. |
| `RENTCAST_API_KEY`   | Optional  | Secondary parcel-value AVM lookup from RentCast. Without it, the regional land proxy is used (which is the primary approach regardless). |

**Both keys are optional.** The app is designed to run and produce a full, honest
estimate with neither key configured — it degrades gracefully with a clear "no API key
configured" message rather than crashing. This has been verified end to end.

### How to plug in a real Metals.Dev key later

1. Sign up at <https://metals.dev/> (free tier, no credit card).
2. Copy the API key from your dashboard.
3. `export METALS_DEV_API_KEY=the_key` (or put it in `.env` and load it).
4. Restart the server. The live-priced metals will switch from "NO PRICE / excluded" to
   **LIVE** figures and be included in the total automatically.

Same pattern for `RENTCAST_API_KEY`.

---

## Project structure

```
datacentermetals/
├── app.py              # Flask server: page + /api/estimate, /api/geocode, /api/detect-location, /api/build-types
├── estimator.py        # Pure calculation logic + benchmark constants + input validation
├── metals_mix.py       # 11-metal per-MW intensities by component, facility vs compute split, price basis
├── build_types.py      # The three build-type profiles (density, metals-mix multipliers, PUE)
├── power.py            # Power / capacity layer: MW <-> GWh/yr, state industrial tariffs (EIA)
├── geometry.py         # Geodesic polygon-area calc for drawn parcels (no network)
├── capacity.py         # Indicative rack-count + cooling-method logic (no network)
├── geocode.py          # OpenStreetMap Nominatim forward + reverse geocoding (rate-limited)
├── land_prices.py      # State + county land comparables: county DC-land / state USDA / national
├── metals_client.py    # Metals.Dev live-price client, all supported metals (graceful no-key handling)
├── land_value.py       # Optional RentCast AVM client (graceful no-key handling)
├── static/
│   └── index.html      # Single-page frontend (Leaflet + Leaflet.draw + Esri tiles, no build step)
├── requirements.txt
├── .env.example        # Documents the two optional environment variables
├── SOURCES.md          # Every benchmark figure with source, URL, and verified date
└── README.md
```

## API

`POST /api/estimate` with JSON body. Either supply a drawn **polygon** (primary) or a
manual **lat/lng/sqft** (fallback):

```json
{ "polygon": [[41.8781,-87.6298],[41.8781,-87.6250],[41.8820,-87.6250],[41.8820,-87.6298]],
  "state": "IL", "county": "Cook County", "build_type": "ai_liquid" }
```

```json
{ "lat": 41.8781, "lng": -87.6298, "sqft": 500000, "state": "IL",
  "build_type": "hyperscale", "capacity_value": 120, "capacity_unit": "mw", "utilization": 0.67 }
```

Optional fields: `state` (USPS code or name) and `county` (describe / benchmark the
parcel at state + county level; detected automatically if omitted), `build_type`
(`hyperscale` default, `modular`, `ai_liquid`), `capacity_value` + `capacity_unit`
(`mw` or `gwh` = GWh/yr of IT energy) for the power layer, and `utilization`
(0.1-1.0, default 0.67).

When a `polygon` is supplied it takes priority: the server recomputes its enclosed area
geodesically (it does not trust a browser-sent number) and derives the lat/lng from the
polygon centroid. An optional `land_comp` object (the confirmed/overridden land
comparable) sets the land $/acre; if absent the server reverse-geocodes the centroid and
picks the comparable itself (from `state`/`county` if given, else by reverse-geocoding).
The old `region` field is still accepted for backward compatibility but no longer used
by the UI. Returns a JSON breakdown of quantities, the 11-row `metals` table (facility /
compute tonnes and values, price basis), `facility_value_usd` / `compute_value_usd`,
the `power` block (driving MW, parcel MW, GWh/yr, state tariff), `build_type`,
battery-metal quantities, shell cost, rack capacity / cooling, price provenance, the
detected `land_comp` and `location`, and the total. Invalid input returns HTTP 400 with
a clear message.

`GET /api/build-types` returns the three build-type profiles (copy and the numbers that
drive the estimate).

`GET /api/geocode?q=<text>` forward-geocodes a free-text query (via Nominatim) to
candidate places for the search box. `POST /api/detect-location` with a `polygon` (or
`lat`/`lng`) reverse-geocodes the centroid and returns the auto-detected land comparable
for the user to confirm or override; with `state` (+ optional `county`) it resolves the
comparable for that place directly, without geocoding.

`GET /api/health` reports status, whether each API key is configured, and the geocoder.

---

## What this is NOT

- It does **not** scrape LoopNet, CoStar, Crexi, or any real-estate listing site — those
  terms of service prohibit it. Land pricing comes only from published market-research
  averages (cited in `SOURCES.md`) and the optional RentCast API.
- It does **not** fabricate live data. Anything that is a static or assumed figure is
  labeled as such in both the UI and `SOURCES.md`.
