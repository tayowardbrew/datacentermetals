# Data Center Site Value Estimator

Estimate the implied power capacity, materials intensity, construction cost and total
implied value of a candidate data center parcel by **searching for a location, then
drawing the parcel on satellite imagery** (or entering raw coordinates and a footprint).
A free location-search box flies the map to any address/area/city; you then draw the
parcel and the tool **auto-detects the state/county and suggests a land comparable** you
can confirm or override.

The tool estimates:

- **Footprint area** from a parcel you **draw on the map** (polygon or rectangle),
  computed geodesically (spherical-excess area, correct at scale), or from a manual
  square-footage entry.
- **Implied power capacity (MW)** from a sourced watts-per-square-foot power density.
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
- **Live copper price** via the [Metals.Dev](https://metals.dev/) API (free tier).
- **Land value** via a **granular, auto-detected and confirmable comparable**: a real
  quoted data-center-land $/acre for named hotspots (Northern Virginia, Phoenix,
  Columbus, Chicago…), falling back to the state USDA agricultural raw-land floor, then
  to a broad regional proxy — with the tier always shown and an honest raw-vs-DC-land
  caveat. Optional secondary [RentCast](https://developers.rentcast.io/) AVM lookup.
- **Location search** above the map (free [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/),
  no API key): type an address/area/city, pick a result, the map flies there.
- **Total implied site value today** = land value + priced materials + shell cost,
  broken down line by line.
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

## Honesty about scope (read this before trusting a number)

This is a **portfolio MVP**, not a production appraisal tool. It is deliberately precise
about what each number is:

| Line item            | What it actually is |
|----------------------|---------------------|
| Footprint area       | **Geodesically computed** from the drawn parcel (correct at scale), or a manual entry. |
| Power capacity (MW)  | An **assumption** from a fixed W/sq ft density (mid-range of a sourced band). |
| Shell cost           | A **benchmark-derived** figure (sourced % of a sourced $/MW build), **excluding** the power/M&E chain to avoid double-counting. |
| Steel / copper tonnage | **Researched benchmarks** (material-intensity figures), not measured; both re-verified against 2026 sources. |
| Aluminum tonnage     | A **reputable-secondary benchmark** (WEF/Kearney Dec 2025, whole-facility, 11.3 t/MW). |
| Copper / aluminum price | A **genuine live API call** to Metals.Dev (when a key is configured). |
| Steel price          | A **static benchmark** — steel is not on the Metals.Dev free tier. Labeled as such. |
| Battery (UPS) metals | **Two figures**: WEF/Kearney headline (real fleet mix) + our own 5-min-ride-through lower-bound cross-check; small at UPS scale; **not priced**. |
| Rack count / cooling | **Indicative rules of thumb** (white-space ratio, sq ft/rack, kW/rack cooling bands), not an engineering design. |
| Land value           | A **granular auto-detected comparable** (metro DC-land transaction → state USDA ag proxy → region proxy), tier shown; **not a parcel-level appraisal**. |
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
- **(d) Stainless steel as a separate line.** Researched but **not** separately modelled:
  no citable stainless-per-MW figure was found, so it is folded into the steel band
  rather than invented (see SOURCES.md entry 12).
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
| `METALS_DEV_API_KEY` | Optional  | Live copper/aluminum spot prices from Metals.Dev (free tier, no card). Without it, copper cost is excluded from the total and clearly labeled. |
| `RENTCAST_API_KEY`   | Optional  | Secondary parcel-value AVM lookup from RentCast. Without it, the regional land proxy is used (which is the primary approach regardless). |

**Both keys are optional.** The app is designed to run and produce a full, honest
estimate with neither key configured — it degrades gracefully with a clear "no API key
configured" message rather than crashing. This has been verified end to end.

### How to plug in a real Metals.Dev key later

1. Sign up at <https://metals.dev/> (free tier, no credit card).
2. Copy the API key from your dashboard.
3. `export METALS_DEV_API_KEY=the_key` (or put it in `.env` and load it).
4. Restart the server. The copper line will switch from "excluded / NO KEY" to a
   **LIVE PRICE** figure and be included in the total automatically.

Same pattern for `RENTCAST_API_KEY`.

---

## Project structure

```
tayo-datacenter-estimator/
├── app.py              # Flask server: page + /api/estimate, /api/geocode, /api/detect-location
├── estimator.py        # Pure calculation logic + benchmark constants + input validation
├── geometry.py         # Geodesic polygon-area calc for drawn parcels (no network)
├── capacity.py         # Indicative rack-count + cooling-method logic (no network)
├── geocode.py          # OpenStreetMap Nominatim forward + reverse geocoding (rate-limited)
├── land_prices.py      # Granular land comparables: metro DC-land / state USDA / region
├── metals_client.py    # Metals.Dev live-price client (graceful no-key handling)
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
{ "polygon": [[41.8781,-87.6298],[41.8781,-87.6250],[41.8820,-87.6250],[41.8820,-87.6298]], "region": "national" }
```

```json
{ "lat": 41.8781, "lng": -87.6298, "sqft": 500000, "region": "national" }
```

When a `polygon` is supplied it takes priority: the server recomputes its enclosed area
geodesically (it does not trust a browser-sent number) and derives the lat/lng from the
polygon centroid. An optional `land_comp` object (the confirmed/overridden land
comparable) sets the land $/acre; if absent the server reverse-geocodes the centroid and
picks the comparable itself. `region` (one of `national`, `northeast`, `west`, `south`,
`midwest`) is the last-resort land fallback. Returns a JSON breakdown of quantities,
per-line values (incl. aluminum), battery-metal quantities, shell cost, rack capacity /
cooling, price provenance, the detected `land_comp`, and the total. Invalid input returns
HTTP 400 with a clear message.

`GET /api/geocode?q=<text>` forward-geocodes a free-text query (via Nominatim) to
candidate places for the search box. `POST /api/detect-location` with a `polygon` (or
`lat`/`lng`) reverse-geocodes the centroid and returns the auto-detected land comparable
for the user to confirm or override.

`GET /api/health` reports status, whether each API key is configured, and the geocoder.

---

## What this is NOT

- It does **not** scrape LoopNet, CoStar, Crexi, or any real-estate listing site — those
  terms of service prohibit it. Land pricing comes only from published market-research
  averages (cited in `SOURCES.md`) and the optional RentCast API.
- It does **not** fabricate live data. Anything that is a static or assumed figure is
  labeled as such in both the UI and `SOURCES.md`.
