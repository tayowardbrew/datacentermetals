# Sources & Benchmark Assumptions

Every numeric assumption used by the Data Center Site Value Estimator is documented
below with the figure used, the source, a URL, and the date it was last verified.
Where I could not find a strong primary source, that is stated explicitly rather than
presenting a guess as fact.

**Last verified for all entries below: 2026-09-23** (entries 9-11 added and verified 2026-09-30).

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

## 9. Shell / base-building construction cost (excludes power / electrical / mechanical)

- **Figure used:** Shell / core-and-shell + architecture = **14% of total
  construction (hard) cost**, applied to an all-in build cost of **$11M per MW of
  IT capacity**. That gives ~**$1.54M/MW** of shell cost, which the tool multiplies
  by the implied MW. (The implied $/sq ft therefore floats with the power-density
  assumption; at 250 W/sq ft it works out to roughly $385/sq ft of shell.)
- **Why a % of total, not a bare $/sq ft:** the only shell-only $/sq ft figures I
  could find were from secondary trade/blog sources that disagreed badly with each
  other ($80-160/sq ft vs $250-400/sq ft, reflecting different definitions of
  "shell"). The well-sourced quantity is the *relationship* — the shell/core share
  of total construction cost from a recognised benchmark house — so the tool uses
  that against a sourced all-in $/MW anchor instead of hard-coding a weak $/sq ft.
- **Range in the literature:** shell/powered-shell portion ~9-20% of total
  construction cost. Turner & Townsend put core/shell + architecture at **14% for an
  air-cooled facility and 9% for a liquid-cooled AI facility** (the rest being
  mechanical ~22-33% and electrical ~48-54%, plus ~10% GC fees). The 14% air-cooled
  figure is used as the default. All-in build cost anchor: ~$10-12M/MW US standard
  build (JLL ~$11.3M/MW global average 2026); AI/liquid builds run far higher
  ($17-25M/MW).
- **Source:** Turner & Townsend, *Data Centre Construction Cost Index 2025 /
  2025-2026* (cost-trends section, with the explicit air- vs liquid-cooled
  percentage split) for the 14%/9% shell share; JLL *2026 Global Data Center
  Outlook* for the ~$11.3M/MW all-in anchor.
- **URLs:**
  - https://reports.turnerandtownsend.com/data-centre-construction-cost-index-2025/data-centre-cost-trends
  - https://www.turnerandtownsend.com/insights/data-centre-construction-cost-index-2025-2026/
  - JLL $11.3M/MW figure (cited via Global Data Center Hub synthesis): https://www.globaldatacenterhub.com/p/what-a-data-center-actually-costs
- **Honesty note (IMPORTANT):** This cost line **deliberately EXCLUDES the IT power
  chain, electrical and mechanical plant**, because those are already captured in
  this tool via the implied-MW / copper / steel figures — bundling M&E into the
  shell line would double-count. The 14% T&T figure is "core/shell + architecture"
  as a share of *construction hard cost* (it excludes land, soft costs and IT
  equipment), which is exactly the shell-vs-M&E separation wanted here, though note
  it bundles architecture in with structural shell, so it is marginally broader than
  pure structural shell. The $11.3M/MW all-in anchor is a JLL figure reached via a
  secondary synthesis source, not the JLL report directly — flagged as secondary.
  Both the % and the $/MW anchor are configurable in `estimator.py`.

## 10. Rack capacity — white-space ratio, sq ft per rack, implied kW/rack

- **Figures used:**
  - **White space = 45% of gross building area** (midpoint of a sourced 40-50%
    band). Racks are counted from white space, not gross area.
  - **20 sq ft of white space per rack** (standard planning default incl. aisle
    allowance; range 15-25 for air-cooled).
  - **Average kW/rack is then implied** by dividing the tool's implied total IT
    power by the estimated rack count — it is a *derived* figure, not an input, so
    it is internally consistent with the power-density assumption.
- **Range in the literature:**
  - White space as a share of gross internal area: **40-50%** (RICS), with external
    plant/support space often 30%+ of GIA on top.
  - sq ft per rack: 12-25 (12-15 for dense/liquid layouts, 15-25 air-cooled);
    ~50 racks per 1,000 sq ft of white space.
  - Observed operating rack density for context: Uptime Institute modal **~11
    kW/rack (2026 survey)**; AFCOM reports a much higher self-selected-member
    *design* average **~27 kW/rack (2026)**; high-density AI racks 50-130 kW. The
    Uptime vs AFCOM gap is definitional (operating vs design, broad vs AI-leaning
    population), not an error.
- **Source:**
  - White-space ratio: **RICS Construction Journal, Robert Nicholson MRICS (10 Jul
    2024)** — "net data hall / white space is generally 40-50% of gross internal
    area, excluding office blocks." (Best-sourced figure here — professional body,
    named chartered author.)
  - sq ft/rack and racks/1,000 sq ft: Obel Insights, "Data Center Capacity Math"
    (industry rule of thumb; secondary trade source).
  - Density context: Uptime Institute Global Data Center Survey and AFCOM State of
    the Data Center 2026, reported via Data Center Knowledge.
- **URLs:**
  - https://ww3.rics.org/uk/en/journals/construction-journal/data-centre-demand-retrofit.html
  - https://obelinf.com/blog/data-center-capacity-math-kw-per-square-foot-vs-kw-per-rack/
  - https://www.datacenterknowledge.com/ai-data-centers/ai-drives-data-center-uncertainty-in-uptime-s-2026-survey
  - https://www.datacenterknowledge.com/data-center-construction/afcom-rack-density-and-build-outs-surge-as-ai-overhauls-data-center-design
- **Honesty note:** The RICS white-space ratio is well-sourced; the sq ft/rack
  figure is a widely-consistent industry rule of thumb from a trade source, flagged
  as such. The rack count is INDICATIVE: real layouts vary with cabinet size,
  density, aisle width and liquid-vs-air design. The sq ft/rack figure is applied to
  *white space* (after the 40-50% ratio), not to gross area directly. The 2026
  Uptime/AFCOM density numbers are shown only as context and are reported via trade
  press rather than the (paywalled) primary survey PDFs.

## 11. Cooling method by rack density (indicative tiered rule)

- **Figures used (defensible bands, keyed on the implied average kW/rack):**

  | Implied density | Typical cooling |
  |-----------------|-----------------|
  | < ~20 kW/rack   | Air cooling (CRAC/CRAH), raised floor, hot/cold-aisle containment |
  | ~20-30 kW/rack  | Air at its ceiling: full containment + rear-door heat exchangers / in-row |
  | ~30-50 kW/rack  | Direct-to-chip (cold-plate) liquid cooling |
  | > ~50 kW/rack   | Direct-to-chip at scale and/or immersion (dense AI/HPC) |

- **Range in the literature:** the air-to-liquid transition is cited anywhere from
  ~20 kW (ASHRAE, conservative) to 40-50 kW (airflow hard limit); immersion
  threshold ~50 kW+; air hard ceiling ~80-100 kW/rack.
- **Source:**
  - **ASHRAE TC 9.9** (governing thermal-guidelines body): air becomes insufficient
    beyond ~20-25 kW/rack; the H1 high-density class (>20 kW) was added in the 5th
    edition (2021); direct liquid cooling recommended above ~20-30 kW/rack. The
    ~20 kW threshold is the most authoritative single number here.
  - **Schneider Electric White Paper #282**, "Capital Cost Analysis of Immersive
    Liquid-Cooled vs Air-Cooled Large Data Centres" (2020): capex parity ~10 kW,
    liquid saves ~10% at 20 kW, ~14% at 40 kW — the canonical cost-crossover
    citation.
  - Higher-band edges (30/50 kW) from vendor/trade consensus (Schneider, Vertiv,
    Introl, NRI Globe).
- **URLs:**
  - https://www.simscale.com/blog/ashrae-90-4-data-center-standards/
  - https://greencalculus.com/standards/ashrae-tc-9-9-thermal-guidelines/
  - https://www.prnewswire.com/news-releases/schneider-electric-releases-white-paper-on-capital-cost-comparison-of-data-centre-liquid-cooling-vs-traditional-air-cooling-301086834.html
  - https://nriglobe.com/technology/ai-data-center-cooling-methods-2026-air-direct-to-chip-liquid-immersion-pue-nvidia-gb200-rack-density-explained/
- **Honesty note:** The ~20 kW ASHRAE air→liquid threshold is the best-anchored
  number (reached via secondary explainers, since the TC 9.9 guidelines themselves
  are paywalled). The higher band edges (30, 50 kW) are defensible industry
  consensus assembled from several vendor/trade sources, NOT one definitive
  standard, and are presented as rule-of-thumb bands, not hard specs. The cooling
  method is labelled INDICATIVE throughout the UI. A separately-researched Vertiv
  liquid-cooling white paper was deliberately NOT cited because its internal
  thresholds could not be verified from the source document.
