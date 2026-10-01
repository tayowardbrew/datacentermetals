# Data Center Site Value Estimator

Estimate the implied power capacity, materials intensity, construction cost and total
implied value of a candidate data center parcel by **drawing it on satellite imagery**
(or entering raw coordinates and a footprint) — no street address required, so it works
for genuinely empty land.

The tool estimates:

- **Footprint area** from a parcel you **draw on the map** (polygon or rectangle),
  computed geodesically (spherical-excess area, correct at scale), or from a manual
  square-footage entry.
- **Implied power capacity (MW)** from a sourced watts-per-square-foot power density.
- **Shell / base-building construction cost**, derived as the sourced shell/core share
  (~14%, Turner & Townsend) of an all-in $/MW build cost — **deliberately excluding the
  power / electrical / mechanical chain** (already captured by the MW / copper / steel
  figures) to avoid double-counting.
- **Steel tonnage** from a sourced material-intensity benchmark.
- **Copper tonnage** (facility-only and including near-site power connections) from
  a sourced tonnes-per-MW benchmark, anchored on a real disclosed project.
- **Rack capacity & cooling method (indicative):** an estimated rack count (from a
  sourced white-space ratio and sq ft/rack) and the cooling method typical at the
  implied kW/rack density (air → rear-door → direct-to-chip → immersion).
- **Concrete volume/tonnage** as a context line item (shown, not priced).
- **Live copper price** via the [Metals.Dev](https://metals.dev/) API (free tier).
- **Land value** via a **regional-average commercial/industrial price-per-acre proxy**
  (generic industrial land, not hyperscaler-premium), with an optional secondary
  [RentCast](https://developers.rentcast.io/) AVM lookup.
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
| Steel / copper tonnage | **Researched benchmarks** (material-intensity figures), not measured. |
| Copper price         | A **genuine live API call** to Metals.Dev (when a key is configured). |
| Steel price          | A **static benchmark** — steel is not on the Metals.Dev free tier. Labeled as such. |
| Rack count / cooling | **Indicative rules of thumb** (white-space ratio, sq ft/rack, kW/rack cooling bands), not an engineering design. |
| Land value           | A **regional-average proxy** (generic industrial land), explicitly **not a parcel-level appraisal**. |
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
- **(b) True parcel-level land appraisal.** The current version uses a **regional-average
  price-per-acre proxy**, not real appraisal or parcel-level assessment data. A real
  appraisal would require parcel records, comparables, zoning, and power/water
  availability — none of which a raw coordinate provides.
- **(c) Aluminum as a priced material.** The Metals.Dev integration already fetches the
  live aluminum price, but no defensible aluminum-tonnes-per-MW intensity figure was
  found at citable quality, so aluminum is left out of the headline model rather than
  invented. Ready to add once a source exists.
- **(d) Sensitivity / range outputs.** Currently single-point mid-range estimates; a
  future version could show low/high bands from the sourced ranges.

---

## Running it locally

Requirements: Python 3.9+.

```bash
cd tayo-datacenter-estimator

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
├── app.py              # Flask server: serves the page + /api/estimate JSON endpoint
├── estimator.py        # Pure calculation logic + benchmark constants + input validation
├── geometry.py         # Geodesic polygon-area calc for drawn parcels (no network)
├── capacity.py         # Indicative rack-count + cooling-method logic (no network)
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
polygon centroid. `region` is one of `national`, `northeast`, `west`, `south`, `midwest`.
Returns a JSON breakdown of quantities, per-line values, shell cost, rack capacity /
cooling, price provenance, and the total. Invalid input (out-of-range coordinates,
non-positive square footage, a degenerate polygon, unknown region) returns HTTP 400 with
a clear message.

`GET /api/health` reports status and whether each API key is configured.

---

## What this is NOT

- It does **not** scrape LoopNet, CoStar, Crexi, or any real-estate listing site — those
  terms of service prohibit it. Land pricing comes only from published market-research
  averages (cited in `SOURCES.md`) and the optional RentCast API.
- It does **not** fabricate live data. Anything that is a static or assumed figure is
  labeled as such in both the UI and `SOURCES.md`.
