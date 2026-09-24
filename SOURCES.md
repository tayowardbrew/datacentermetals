# Sources & Benchmark Assumptions

Every numeric assumption used by the Data Center Site Value Estimator is documented
below with the figure used, the source, a URL, and the date it was last verified.
Where I could not find a strong primary source, that is stated explicitly rather than
presenting a guess as fact.

**Last verified for all entries below: 2026-09-23**

> Note on primary vs secondary sources: several of these benchmarks originate in
> paywalled or subscription industry reports (BloombergNEF, Cushman & Wakefield,
> CBRE). Where the primary report itself is not publicly readable, the most
> authoritative public source that quotes the figure is cited, and the underlying
> report is named so the figure can be traced.

---

## 1. Power density — watts per square foot

- **Figure used:** 250 W/sq ft (configurable in code; sits in the middle of the
  cited 200-400 W/sq ft modern range).
- **Range in the literature:** 200-400 W/sq ft for modern facilities; >300 W/sq ft
  is considered high-density. AI-optimised facilities can run several times higher
  per rack, but per-*building-square-foot* averages remain in the low-to-mid
  hundreds of watts.
- **Source:** TierPoint, "Navigating Data Center Power Density in the Age of HPC and
  AI"; corroborated by Cadence, "Data Center Power Density: Modern Data Center
  Design."
- **URLs:**
  - https://www.tierpoint.com/blog/data-center-power-density/
  - https://cadencenow.com/data-center-power-density-modern-data-center-design/
- **Honesty note:** This is an industry-consensus range from vendor/engineering
  commentary, not a single peer-reviewed primary study. Power density is highly
  design-dependent (rack density, cooling type, redundancy), so this is the
  weakest-provenance figure in the model and is flagged as such in the UI. 250 was
  chosen as a defensible mid-range default; the user can reason about sensitivity by
  noting the 200-400 band.

## 2. Steel intensity — metric tons per square foot

- **Figure used:** 0.016 metric tons/sq ft (midpoint of the 0.014-0.018 range).
- **Range in the literature:** 0.014-0.018 metric tons/sq ft of building space,
  driven by structural framing, cooling systems and heavy equipment support.
- **Source:** Data Centre Magazine, "The Role of Steel in Today's Data Centre
  Industry" (the figure as aggregated and restated by impactECI, "Data Center
  Infrastructure at Scale").
- **URLs:**
  - https://datacentremagazine.com/articles/the-role-of-steel-in-todays-data-centre-industry
  - https://impacteci.substack.com/p/data-center-infrastructure-at-scale
- **Cross-check:** impactECI states a 250 MW / 1.5M sq ft facility uses ~50,000
  metric tons of steel, which implies ~0.033 t/sq ft at the whole-campus level
  (i.e. the higher end when land/site works are included). The 0.014-0.018 figure
  is for building space specifically, which is what this tool estimates from
  building square footage, so 0.016 is the appropriate coefficient.

## 3. Copper intensity — tonnes per MW

- **Figures used:**
  - 12 tonnes/MW — facility-only (conservative / lower bound).
  - 26 tonnes/MW — including near-site power connections (default headline figure).
- **Anchor data point:** Microsoft's ~$500M, ~80 MW Chicago data center used
  ~2,177 tonnes of copper during construction ≈ 27 tonnes/MW. Broader industry
  estimates place large AI data center copper use at roughly 27-33 tonnes/MW of
  installed capacity.
- **Source:** BloombergNEF, "Tracking Copper in Data Centers 2025-2035: Supply
  Crunch" (BNEF), as reported by Mining.com and Bloomberg; corroborated by BHP
  Insights on copper and data centers.
- **URLs:**
  - https://www.mining.com/ai-data-centers-to-worsen-copper-shortage-bnef/
  - https://about.bnef.com/insights/clean-energy/how-data-centers-are-fueling-global-copper-crunch/
  - https://www.bhp.com/news/bhp-insights/2025/01/why-ai-tools-and-data-centres-are-driving-copper-demand
- **Honesty note:** The Microsoft Chicago figure is the most concrete public
  data point (a single disclosed real project). The 12 tonnes/MW facility-only
  figure is the lower bound used in the brief and is a reasonable
  facility-vs-total split, but I could NOT find a Microsoft primary document that
  explicitly separates "facility-only" from "including power connections" for the
  Chicago site — the ~2,177 t / ~27 t/MW total is what is disclosed publicly. The
  12 t/MW lower bound is therefore presented as an industry rule-of-thumb range
  endpoint, not a Microsoft-disclosed split. Default headline uses 26 t/MW.

## 4. Concrete intensity — cubic meters per MW (bonus line item)

- **Figure used:** 750 m³/MW (midpoint of the 500-1,000 range).
- **Range in the literature:** 500-1,000 m³ of concrete per MW; ~750,000 metric
  tons for a 250 MW facility.
- **Source:** impactECI, "Data Center Infrastructure at Scale" (aggregating
  Cushman & Wakefield "Data Center Development Cost Guide 2025" and industry
  construction sources).
- **URL:** https://impacteci.substack.com/p/data-center-infrastructure-at-scale
- **Honesty note:** Concrete is included as a physical-quantity line item only.
  It is NOT priced into the total site value, because concrete is a low-value,
  locally-sourced commodity with no clean live spot price via the metals API, and
  including a fabricated concrete price would undermine the tool's honesty. Shown
  as tonnage/volume for context only.

## 5. Aluminum intensity — tonnes per MW (bonus line item)

- **Figure used:** Not modeled as a headline figure in v1.
- **Honesty note:** I did NOT find a single well-sourced, widely-cited
  aluminum-tonnes-per-MW benchmark of the same quality as the copper figure.
  Aluminum is used in busways, cabling and structural elements, but published
  per-MW intensity figures vary too widely to cite responsibly. Rather than invent
  one, aluminum is left out of v1 as a headline material. The Metals.Dev
  integration DOES fetch the live aluminum price (it is on the free tier), so the
  code is ready to add an aluminum line item the moment a defensible intensity
  figure is sourced. Flagged in the Roadmap.

## 6. Land value — regional average per acre

- **Approach:** Regional average commercial/industrial land price per acre, used
  as a proxy because a coordinate-only parcel has no address for a parcel-level
  appraisal. Clearly labeled in the UI as "regional average proxy, not a
  parcel-level appraisal."
- **Figures used (USD per acre, generic industrial/commercial land, NOT the
  frothy premiums paid specifically for power-ready data center land):**

  | US region              | Assumed $/acre | Basis |
  |------------------------|---------------:|-------|
  | National average       |        150,000 | CBRE industrial land research (50-100 acre parcels >$100k/acre; smaller parcels higher) |
  | Northeast / Mid-Atlantic |      400,000 | Northern NJ / Northern Virginia among highest major markets |
  | West                   |        250,000 | High-cost coastal + inland industrial |
  | South                  |        120,000 | Texas/Southeast, ample land, lower cost |
  | Midwest                |        100,000 | Lower-cost industrial land |

- **Source:** CBRE industrial & logistics land research, as reported by Commercial
  Property Executive ("CBRE report describes industrial land boom") and CBRE North
  America Data Center Trends; regional spread corroborated by industry reporting.
- **URLs:**
  - https://www.commercialsearch.com/news/cbre-report-describes-industrial-land-boom/
  - https://www.cbre.com/insights/books/north-america-data-center-trends-h2-2025
- **Honesty note (IMPORTANT):** Land pricing is by far the noisiest input. Public
  sources give wildly different numbers ($3,500/acre raw rural land vs
  $3-8M/acre for power-ready Northern Virginia data center land). The figures above
  are deliberately set to GENERIC industrial/commercial land averages, NOT the
  extreme premiums that hyperscalers pay for shovel-ready powered sites, because
  the tool estimates a generic parcel's value, not a competitively-bid data center
  land deal. These are order-of-magnitude regional proxies and are labeled as such.
  A serious appraisal would require parcel-level data (Roadmap item). If a user
  wants the "what a data center developer would pay" figure instead, that is a
  different and much higher number, and is intentionally not the default to avoid
  overclaiming.

## 7. Live commodity prices — copper, aluminum

- **Source:** Metals.Dev API, `https://api.metals.dev/v1/latest` (free tier, no
  credit card). Industrial metals on free tier: copper, aluminum, lead, nickel,
  zinc. Returned in metric tonnes (USD) by default.
- **URL:** https://metals.dev/docs
- **Honesty note:** Steel does NOT have a clean live spot price on the Metals.Dev
  free tier. Steel cost is therefore computed from a documented static price per
  tonne (see below), clearly labeled in the UI as a static benchmark, not a live
  quote. Copper (and optionally aluminum) is the genuine live-price line item.

## 8. Static steel price (fallback, clearly labeled)

- **Figure used:** $900/metric ton (hot-rolled coil / structural steel, generic
  US benchmark; configurable).
- **Source:** General market range for US structural/HRC steel in 2024-2025
  ($700-1,100/ton depending on product and date).
- **Honesty note:** This is a static, manually-maintained benchmark, NOT a live
  quote, because steel is not on the metals API free tier. It is labeled as such
  everywhere it appears. A user should update it against a current source (e.g.
  SteelBenchmarker, CME HRC futures) before relying on the steel line item.
