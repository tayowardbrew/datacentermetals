# Sources & Benchmark Assumptions

Every numeric assumption used by the Data Center Site Value Estimator is documented
below with the figure used, the source, a URL, and the date it was last verified.
Where I could not find a strong primary source, that is stated explicitly rather than
presenting a guess as fact.

**Last verified for all entries below: 2026-09-23** (entries 9-11 added and verified 2026-09-30; entry 6 rebuilt granular and entries 5, 12, 13 added/revised and verified 2026-10-01; steel & copper re-verified 2026-10-01; entries 5 and 12 upgraded to the WEF/Kearney "From Minerals to Megawatts" Dec 2025 source, verified by direct PDF download and extraction, 2026-10-01; entry 6 moved to state + county granularity and entries 14-17 added and verified 2026-10-15).

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
- **Re-verified 2026-10-01:** the 0.014-0.018 metric-tons/sq ft building-space band
  was re-confirmed against multiple 2026 sources (Data Centre Magazine; impactECI;
  Discovery Alert, "Data Centers Steel Demand 2025"; constructionbids.ai 2026 report),
  which independently restate ~30-40 lb/sq ft (~0.015-0.020 t/sq ft) and the ~50,000 t
  for a 250 MW / 1.5M sq ft facility. 0.016 holds; retained unchanged. Note (per Tayo's
  materials question): liquid-cooled AI facilities add stainless-steel piping/manifolds
  that push the *high* end higher, but no clean separate stainless-per-MW figure was
  found (see the stainless-steel note after entry 12), so stainless is folded into
  this steel band rather than modelled separately.
- **Cross-check (per-MW basis):** World Economic Forum / Kearney, "From Minerals to
  Megawatts" (Dec 2025), Figure 4, gives "iron" (the closest proxy to structural/
  building steel) summing to **≈47.7 t/MW** across all five components (cooling
  ~18,000 + servers ~5,100 + backup ~14,000 + electrical ~9,900 + networking ~660
  kg/MW). This is a different basis (per-MW, whole-facility iron incl. equipment)
  from this tool's per-sq-ft building-steel coefficient, so it is NOT used to
  replace 0.016 t/sq ft, but it is a useful order-of-magnitude cross-check: at this
  tool's own 250 W/sq ft power density, 0.016 t/sq ft implies ~64 t/MW of building
  steel alone, which is in the same broad range as WEF's 47.7 t/MW whole-facility
  iron figure (the WEF figure additionally includes equipment-level iron in
  servers/backup, which this tool's building-steel line does not attempt to
  capture, so the two are not expected to match exactly).
  - URL: https://reports.weforum.org/docs/WEF_From_Minerals_to_Megawatts_2025.pdf

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
- **Re-verified 2026-10-01 (two independent sources):**
  1. The Copper Development Association (via Fastmarkets, 27 Aug 2026) gives
     **20-40 tonnes of copper per MW for modern liquid-cooled data centers**, and
     separate 2026 reporting gives **10-15 t/MW traditional / 25-30 t/MW
     AI-focused**.
  2. **World Economic Forum / Kearney, "From Minerals to Megawatts"** (Dec 2025),
     **Figure 4** (source: Bank of America Securities/IEA/Kearney) — summing copper
     across all five facility components (cooling ~3,600 + servers ~2,000 + backup
     ~2,200 + electrical ~3,500 + networking ~280 kg/MW) gives **≈11.6 t/MW**,
     independently derived from first principles rather than the Chicago case
     study, and landing within 3% of this tool's 12 t/MW facility-only figure.
  - Both the tool's 12 t/MW (facility-only lower bound) and 26 t/MW (headline,
    incl. near-site power) sit squarely inside these two independently-sourced
    2025/2026 ranges, so both figures were retained unchanged. This is the
    strongest cross-validation any figure in this model has.
- **URLs (re-verification):**
  - https://www.fastmarkets.com/insights/data-center-boom-reshapes-us-metals-industry-changing-demand-supply-flows-indefinitely/
  - https://reports.weforum.org/docs/WEF_From_Minerals_to_Megawatts_2025.pdf

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

## 5. Aluminum intensity — WEF/Kearney whole-facility per-MW figure (v3)

- **Figure used:** **11.3 tonnes of aluminum per MW** of implied IT power, priced
  live via Metals.Dev. This is a whole-facility sum across five components from a
  single reputable source (see below), not an invented or bottom-up figure.
- **Source:** World Economic Forum, in collaboration with Kearney, **"From Minerals
  to Megawatts: Building Resilience for EVs, Data Centres and Power Grids"** —
  WHITE PAPER, **December 2025**. **Figure 4, "Data centre component breakdown by
  mineral (kgs per MW)."** Chart attribution: **"Source: Bank of America
  Securities, IEA and Kearney analysis."** Free, publicly downloadable PDF;
  independently verified by downloading and extracting the report text directly
  (not just a secondary citation of it).
- **URL:** https://reports.weforum.org/docs/WEF_From_Minerals_to_Megawatts_2025.pdf
  (free PDF) / https://www.weforum.org/stories/2025/12/securing-data-centre-materials/
  (story page)
- **Derivation:** Figure 4 breaks the facility into five components, each with its
  own aluminum figure (kg/MW): cooling systems ~6,700, servers/chips ~2,700, backup
  power ~1,200, electrical systems ~460, networking/storage ~260. Summed: **≈
  11,320 kg/MW ≈ 11.3 t/MW**, which is the single coefficient used
  (`ALUMINUM_TONNES_PER_MW` in `estimator.py`). The chart's own total-mass
  cross-check ("Total minerals and metals mass per MW: ~60-75 metric tons") is
  consistent with this component sum once all tracked metals are added.
- **Superseded approach (kept here for the audit trail):** an earlier version of
  this tool used a bottom-up estimate (≈45 kg per rack frame + ≈300 kg/MW of
  cooling-CDU aluminum, from Huaxiao-alloy vendor material-selection guides),
  explicitly labelled a lower-confidence lower bound because no clean per-MW
  benchmark existed at the time. That figure (for context, roughly 2-8 t/MW
  depending on rack density) is **retired** now that the better-sourced,
  reputable-secondary WEF/Kearney whole-facility figure has been found and
  verified — it was materially lower because it only covered two of the five
  components WEF's figure captures (rack frames + cooling CDU only, missing
  servers/chips, backup-power and electrical-system aluminum).
- **Honesty note:** WEF/Kearney is a **reputable secondary source** (a
  consultancy/forum white paper synthesising Bank of America Securities + IEA
  analysis), not a primary engineering material-takeoff — but it is dated, named,
  freely downloadable, and gives a self-consistent, component-level breakdown
  across the exact five areas (cooling, servers, backup, electrical, networking)
  this tool's capacity model already distinguishes. This is now the
  **best-sourced aluminum figure available** for this model and is used as the
  primary (not bottom-up/lower-bound) aluminum coefficient.

## 6. Land value — GRANULAR, auto-detected per-acre comparable (v2)

> **v3 (2026-10-15): state + county granularity.** The generic directional buckets
> (northeast / south / midwest / west) are retired. Every US parcel is now
> described and benchmarked at **state + county** (or district / parish / borough /
> independent city) level: the user sees and can edit the detected State + County,
> and the comparable is resolved from them (county DC-land transaction, else the
> state USDA figure). AK, HI and DC, which USDA does not survey, fall back to the
> national industrial proxy but keep their real state / county label. The UI also
> shows the state's raw-land value relative to the US average (USDA 2025, US avg
> $4,350/ac) and any quoted DC-land comps elsewhere in the same state.

The old five-bucket US-region dropdown has been replaced by an auto-detected,
confirmable land comparable resolved in three tiers from the drawn parcel's
reverse-geocoded location (state + county/metro). The tier used is always shown in
the UI so the figure is never presented as more precise than it is.

### Tier 1 — METRO / COUNTY (real quoted data-center-land transactions)

For named data-center hotspots, a real $/acre figure from a publicly-quoted
transaction (power-ready / entitled DC land). Every figure below was found on a
freely-accessible public page. "implied" = total deal price ÷ acreage from the
same article (treat as market-tier indicative, not exact unit land value).

  | Location | $/acre | Deal / basis | Source (publisher, date) |
  |----------|-------:|--------------|--------------------------|
  | Loudoun County, VA | 6,300,000 | SDC Capital 97 ac for $615.05M, Nov 2025 (county record) | Northern Virginia Magazine / DataCenterDynamics, Nov 2025 |
  | Prince William County, VA | 3,750,000 | Amazon ~189 ac for ~$700M, Gainesville (implied) | CoStar, 2025 |
  | Phoenix / Maricopa, AZ | 1,300,000 | Microsoft 100 ac $131M+ (Goodyear); Amazon 220 ac $277M | CoStar / DataCenterDynamics, 2025 |
  | Buckeye, AZ (exurb) | 136,000 | Arizona Land 160 ac $21.7M, Mar 2025 (implied) | DataCenterDynamics, 2025 |
  | New Albany / Columbus, OH | 741,000 | Google 85 ac $63M, Jun 2025 (implied) | DataCenterDynamics, 2025 |
  | Lamar County, GA (Atlanta exurb) | 274,000 | Amazon 984 ac ~$270M, Aug 2025 (implied) | Atlanta Journal-Constitution, 2025 |
  | Monroe County, GA (Atlanta exurb) | 61,600 | Google 950 ac $58.5M, Sep 2025 (implied) | DataCenterDynamics, 2025 |
  | Santa Clara / Silicon Valley, CA | 6,000,000 | ~$6M-7M+/ac quotes | Datacenters.com (secondary aggregator) |
  | Dallas-Fort Worth, TX | 540,000 | ~$498k-581k/ac industrial listings (no clean free DC transaction found) | LandSearch, 2025-26 |
  | Chicago metro, IL | 234,000 | ~$5.40-5.59/sf DC land weighted avg | Cushman & Wakefield DC Development Cost Guide 2025 (public) |
  | Hillsboro, OR | 1,000,000 | industrial/DC land $250k -> $1M+/ac | Hillsboro Herald / Oregon Center for Public Policy, 2026 |

- **URLs (metro tier):**
  - https://northernvirginiamag.com/news/2025/11/06/ (Loudoun $615M / 97 ac)
  - https://www.datacenterdynamics.com/en/news/sdc-capital-partners-buys-97-acres-in-loudoun-county-for-615m/
  - https://www.costar.com/article/419227157/ (Amazon $700M Prince William)
  - https://www.datacenterfrontier.com/site-selection/article/11428233/ (PWC ~$900k/ac, 2021 benchmark)
  - https://www.datacenterdynamics.com/en/news/arizona-land-buys-160-acres-in-buckeye-area/
  - https://www.datacenterdynamics.com/en/news/google-acquires-85-acres-in-new-albany-ohio/
  - https://www.ajc.com/business/2025/08/amazons-data-center-division-pays-270m/ (Lamar County GA)
  - https://www.datacenterdynamics.com/en/news/google-purchases-950-acres-in-monroe-county-georgia/
  - https://cushwake.cld.bz/Data-Center-Development-Cost-Guide-2025 (Chicago + national DC-land $/sf)
  - https://ocpp.org/2026/03/12/oregons-data-center-boom (Hillsboro)

### Tier 2 — STATE (USDA agricultural raw-land floor / proxy)

Where there is no metro figure, the tool uses the state's **USDA NASS farm
real-estate value per acre** as an honest raw-land FLOOR. This is an AGRICULTURAL
figure, explicitly NOT industrial or data-center land, labelled "agricultural
raw-land floor (USDA 2025)" with a mandatory DC-premium caveat in the UI.

- **Source:** USDA NASS, **"Land Values 2025 Summary"** (released 1 Aug 2025), table
  "Farm Real Estate Average Value per Acre — Regions, States, and United States".
  Free government survey. All 48 contiguous states are tabulated in
  `land_prices.py`; US average $4,350/acre, cropland avg $5,830/acre. **Alaska and
  Hawaii are not surveyed by USDA** and fall through to the Tier-3 region proxy.
- **URL:** https://www.nass.usda.gov/Publications/Todays_Reports/reports/land0825.pdf
- Representative values (full table in `land_prices.py`): CA 13,700 · VA 6,100 ·
  OH 9,350 · TX 2,970 · AZ 4,180 · IL 8,930 · IA 9,790 · OR 3,780 · WA 3,710 ·
  NM 725 · WY 1,000. (USD/acre, 2025.)

### Tier 3 — REGION (broad industrial proxy, last resort)

The original national/northeast/west/south/midwest industrial-land proxies
(national 150,000 · northeast 400,000 · west 250,000 · south 120,000 · midwest
100,000 USD/acre; CBRE industrial land research) are retained ONLY as a final
fallback for locations with no state or metro figure (e.g. AK/HI, non-US).

- **Source (region tier):** CBRE industrial & logistics land research, via Commercial
  Property Executive ("CBRE report describes industrial land boom") and CBRE North
  America Data Center Trends.
- **URLs:**
  - https://www.commercialsearch.com/news/cbre-report-describes-industrial-land-boom/
  - https://www.cbre.com/insights/books/north-america-data-center-trends-h2-2025

### Honesty note (IMPORTANT) — the raw-vs-DC-land gap

Land pricing remains by far the noisiest input, and the gap between raw/agricultural
land and power-ready DC land is enormous: Virginia farmland averages **~$6,100/acre
(USDA 2025)** while Loudoun County DC land sold for **~$6.3M/acre (Nov 2025)** — a
~1,000x premium driven by power availability and entitlement, not dirt. The tool
therefore (a) always labels which tier a figure came from, (b) attaches an explicit
DC-premium caveat to the agricultural-proxy tier citing the real VA example, and
(c) lets the user confirm the detected comparable or override it (search a different
area, or type a $/acre directly) rather than forcing a single number. The metro-tier
figures ARE power-ready DC-land market figures; the state tier is a raw-land floor
and is never presented as a DC-land value. Granular free data is strong for Northern
Virginia, Phoenix, Columbus and Chicago; weaker (listing averages only) for
Dallas-Fort Worth; and only the agricultural proxy exists for markets like Salt Lake
City, Omaha/Council Bluffs and Quincy WA — stated honestly in the UI when it applies.

## 7. Live commodity prices — copper, aluminum, nickel, lead, silver, gold

- **Source:** Metals.Dev API, `https://api.metals.dev/v1/latest` (free tier, no
  credit card). One call returns every supported symbol: base metals (copper,
  aluminum, lead, nickel, zinc) and precious metals (gold, silver, platinum,
  palladium). The tool reads copper, aluminum, nickel, lead, silver and gold
  with `unit=mt` (USD per metric tonne) and normalises by the response's own
  `unit` field, since precious metals default to troy ounces.
- **Not on Metals.Dev** (checked against https://metals.dev/symbols, 2026-10-15):
  tin, cobalt, lithium, gallium, steel. These use dated static benchmarks (entry
  14) rather than a second, unrelated price provider.
- **URLs:** https://metals.dev/docs · https://metals.dev/symbols
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

- **Figure used:** Shell / core-and-shell + architecture = **$1.5M per MW of IT
  capacity**, multiplied by the tool's implied MW. (The implied $/sq ft therefore
  floats with the power-density assumption; at 250 W/sq ft it works out to roughly
  $375/sq ft of shell.) $1.5M/MW sits in the middle of the sourced shell-and-core
  band and is ~12% of a typical all-in hard cost — consistent with the shell/core
  share benchmarks below.
- **Why priced per MW, not a bare $/sq ft:** the only shell-only $/sq ft figures I
  could find were from secondary trade/blog sources that disagreed badly with each
  other ($80-160/sq ft vs $250-400/sq ft, reflecting different definitions of
  "shell"). The better-sourced quantities are (a) the shell-and-core cost *per MW*
  and (b) the shell/core *share* of total construction cost from recognised
  benchmark houses, so the tool prices shell cost per implied MW within that band.
- **Range in the literature:**
  - **Shell-and-core cost per MW:** ~**$1.0-2.1M/MW** for an air-cooled facility.
    JLL's figure for a single-tenant ~50 MW air-cooled build puts **shell-and-core
    at ~$11.3M per MW is a SCOPE ERROR to avoid** — see the honesty note; the widely
    quoted ~$11.3M/MW is a *total* construction figure, and the shell-and-core slice
    of that is the ~12-15% / ~$1.0-2.1M/MW band used here.
  - **Shell/core share of total construction (hard) cost:** ~9-20%. Turner &
    Townsend put core/shell + architecture at **14% for an air-cooled facility and
    9% for a liquid-cooled AI facility** (the rest being mechanical ~22-33% and
    electrical ~48-54%, plus ~10% GC fees). Global Data Center Hub's synthesis puts
    shell-and-site at ~12-15% of hard cost ≈ $1.0-2.1M/MW. $1.5M/MW is the mid-band.
  - All-in air-cooled hard cost for context: ~$10-14M/MW (AI/liquid builds run far
    higher, $17-25M/MW).
- **Source:** Turner & Townsend, *Data Centre Construction Cost Index 2025 /
  2025-2026* (air- vs liquid-cooled percentage split) for the 14%/9% shell share;
  Global Data Center Hub cost synthesis (citing JLL) for the shell-and-site $/MW
  band and the all-in anchor.
- **URLs:**
  - https://reports.turnerandtownsend.com/data-centre-construction-cost-index-2025/data-centre-cost-trends
  - https://www.turnerandtownsend.com/insights/data-centre-construction-cost-index-2025-2026/
  - https://www.globaldatacenterhub.com/p/what-a-data-center-actually-costs
- **Honesty note (IMPORTANT):** This cost line **deliberately EXCLUDES the IT power
  chain, electrical and mechanical plant**, because those are already captured in
  this tool via the implied-MW / copper / steel figures — bundling M&E (the dominant
  ~70-85% of construction cost) into the shell line would double-count. The T&T "core/
  shell + architecture" category is a share of *construction hard cost* (it excludes
  land, soft costs and IT equipment), which is exactly the shell-vs-M&E separation
  wanted here, though note it bundles architecture in with structural shell, so it is
  marginally broader than pure structural shell. **Scope caveat (corrected after an
  independent review):** the commonly-cited JLL ~$11.3M/MW figure is a *shell-and-
  core per-MW* number for a specific single-tenant ~50 MW air-cooled facility in some
  write-ups and a *total* figure in others — the figure's scope is reported
  inconsistently across secondary sources. To avoid that ambiguity the tool does NOT
  take a percentage of it; it prices shell cost directly at $1.5M/MW within the
  sourced ~$1.0-2.1M/MW shell-and-core band. The $/MW figure is configurable in
  `estimator.py` (`SHELL_COST_USD_PER_MW`).

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

## 12. Battery-backup (UPS) metals — lithium, nickel, cobalt, lead, graphite (v3)

This line connects the build to the battery-metals / PGM mining angle (directly
relevant given Tayo's Sibanye-Stillwater background). It is shown as a PHYSICAL
QUANTITY and is NOT priced into the total (no clean battery-grade live spot price on
the Metals.Dev free tier; LME nickel metal exists on the free tier but battery
nickel sulfate is a different product, so pricing it would mislead). The tool now
shows **two figures side by side** so the sizing assumption is visible rather than
hidden behind a single number.

### (a) HEADLINE — WEF/Kearney top-down, real fleet mix

- **Figures used (kg per MW of implied IT power), from the backup-power component
  of the same Figure 4 used for aluminum (entry 5):** **Lithium ≈ 30, Nickel ≈ 220,
  Cobalt ≈ 40, Lead ≈ 240, Graphite ≈ 290.** (The backup-power component in the same
  chart also carries Aluminum ≈1,200 and Copper ≈2,200 kg/MW, context only — not
  separately added to this tool's aluminum/copper totals, which already use their
  own whole-facility WEF figures.)
- **Source:** World Economic Forum / Kearney, **"From Minerals to Megawatts"**
  (Dec 2025), **Figure 4**, "Backup power" component. Attribution: "Source: Bank of
  America Securities, IEA and Kearney analysis." Verified by direct PDF download
  and text extraction (not a secondary citation).
  - URL: https://reports.weforum.org/docs/WEF_From_Minerals_to_Megawatts_2025.pdf
- **Why this is the headline figure:** unlike a ride-through calculation, it
  reflects the **actual installed fleet** — the explicit presence of **both lithium
  (~30 kg/MW) and lead (~240 kg/MW) in the same line confirms the real-world fleet
  is still mixed Li-ion + lead-acid**, not fully converted, which the tool's own
  5-minute Li-ion-only calculation (below) cannot capture. It also implicitly bakes
  in real-world redundancy (N+1), spare capacity and a longer effective runtime
  than a bare minimum ride-through.

### (b) LOWER-BOUND CROSS-CHECK — our own 5-minute-ride-through calculation

Retained alongside the WEF headline (rather than replaced) because it makes the
*sizing assumption* transparent, and comes out **~3-4x below** the WEF figure —
which is itself informative (it isolates how much of the WEF number is "real fleet
redundancy/mix" versus "bare minimum physics").

- **Battery chemistry assumption:** new-build hyperscale/colocation UPS is now
  predominantly **lithium-ion**; much of the installed base still runs VRLA
  lead-acid (confirmed independently by the WEF lead figure above). This
  cross-check models the lithium-ion (NMC811) case AND an LFP alternative (lithium
  only, no Ni/Co, increasingly common for DC UPS). Source: DataCenterDynamics, "The
  race to reduce UPS runtime"; Vertiv, "Advantages of Using Lithium-Ion Batteries in
  UPS"; Open Compute Project, "Power uninterrupted: choosing the right battery
  backup."
  - URLs: https://www.datacenterdynamics.com/en/opinions/the-race-to-reduce-ups-runtime/ ·
    https://www.opencompute.org/blog/power-uninterrupted-choosing-the-right-battery-backup-system-for-edge-applications
- **UPS energy sizing:** **5-minute full-load ride-through** (standard; many modern
  designs 5-10 min, enough to start generators and complete the automatic transfer
  switch sequence), de-rated for UPS efficiency (~95%) and usable depth-of-discharge
  (~90%): **≈ 97.5 kWh of battery per MW of IT load**. Source: industry sizing rule
  (kWh = load_kW × runtime_min/60 ÷ (UPS_eff × usable_DoD)), with the 5-15 min
  runtime band from coloprice.com "Backup Power in Data Centers" and
  DataCenterDynamics as above.
  - URL: https://coloprice.com/guides/data-center-generator-backup-power/
- **NMC811 cathode critical-metal intensity (kg per kWh of battery capacity):**
  **Lithium ≈ 0.10, Nickel ≈ 0.65, Cobalt ≈ 0.081** (NMC811 = 80% Ni / 10% Mn /
  10% Co); LFP ≈ 0.09 kg Li/kWh and no Ni/Co. Source: IEA (Global EV Outlook /
  Global Supply Chains of EV Batteries) and ICCT battery-outlook figures (NMC811
  ≈ 0.10 kg Li, ≈ 0.65 kg Ni/kWh; ~2.1 kg/kWh total critical materials),
  corroborated by Argonne National Laboratory BatPaC (NMC811 ≈ 0.09 kg Li/kWh).
  - URLs: https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries ·
    https://iea.blob.core.windows.net/assets/961cfc6c-6a8c-42bb-a3ef-57f3657b7aca/GlobalSupplyChainsofEVBatteries.pdf ·
    https://publications.anl.gov/anlpubs/2023/08/183571.pdf (BatPaC)
- **Resulting per-MW figures (NMC811):** ≈ 9.8 kg Li, ≈ 63 kg Ni, ≈ 7.9 kg Co per
  MW of IT load (i.e. ~1 t Li, ~6 t Ni, ~0.8 t Co for a 100 MW campus) — consistent
  with being ~3-4x below the WEF headline's ~30 kg Li/MW.
- The EV-battery intensity figures are applied to a stationary UPS pack as a
  first-order proxy (cathode chemistry is comparable); this cross-application is
  stated rather than hidden.

### Honesty note (IMPORTANT, applies to both figures)

These tonnages are deliberately **small**, and the tool says so prominently.
Data-center UPS only bridges **minutes** to generator start, so the battery energy
per MW is tiny versus grid-scale BESS (measured in MWh, i.e. 1,000s of kWh/MW). The
battery-metal content is shown to make the mining linkage explicit, NOT to imply
data-center UPS is a major battery-metals sink — it would be **orders of magnitude
larger** for a grid-scale BESS co-located with a data center, which is a different
(and much bigger) thesis. Battery metals are NOT priced into the site total.

### Stainless steel — considered, NOT separately modelled (honest omission)

Per Tayo's materials question, stainless steel (liquid-cooling piping, manifolds,
some equipment) was researched. No clean, citable **stainless-tonnes-per-MW** or
per-sq-ft figure of usable quality was found — sources note only that liquid-cooled
AI builds add stainless piping/manifolds that raise the *upper* end of the overall
steel intensity band. Rather than invent a stainless coefficient, it is folded into
the existing steel band (entry 2, re-verified) and called out here as a known,
deliberate omission, not an oversight.

## 13. Geocoding (location search + reverse-geocode for land detection)

- **Service:** **OpenStreetMap Nominatim** — free, no API key. Used for (a) the
  location search box above the map (forward geocode a typed address/area/city to
  candidate places), and (b) reverse-geocoding the drawn parcel's centroid to its
  state + county/metro so the granular land comparable can be auto-detected.
- **URL / policy:** https://nominatim.openstreetmap.org/ ·
  https://operations.osmfoundation.org/policies/nominatim/
- **Usage-policy compliance:** the Nominatim usage policy (max 1 request/second,
  identifying User-Agent, no bulk hammering) is respected by: a descriptive
  User-Agent + Referer on every call; proxying through the Flask backend so the
  browser never calls Nominatim directly; a client-side debounce (450 ms) that only
  fires at ≥3 characters; and a process-wide ≥1s-between-calls throttle backstop in
  `geocode.py`. No paid geocoder (Google Places, Mapbox) is used — consistent with
  the project's no-paid-API rule.
- **Honesty note:** reverse geocoding uses Nominatim's `zoom=10` (county/city level)
  and the state → USPS-code mapping is done locally in `geocode.py` (Nominatim does
  not reliably return the postal abbreviation). Non-US coordinates fall through to
  the national region proxy (the land dataset is US-specific), stated in the UI.

## 14. Expanded metals coverage (11 metals) and the facility vs compute split

- **Component intensities (kg per MW):** World Economic Forum / Kearney, **"From
  Minerals to Megawatts"** (Dec 2025), **Figure 4**, "Data centre component
  breakdown by mineral (kgs per MW)", attributed to Bank of America Securities,
  IEA and Kearney analysis. Verified again by direct PDF download and text
  extraction on 2026-10-15. Basis: a 2024 split of ~76% conventional (CPU) and
  ~24% accelerated (GPU) capacity.
  - URL: https://reports.weforum.org/docs/WEF_From_Minerals_to_Megawatts_2025.pdf

  | Metal (kg/MW) | Cooling | Electrical | Backup | Servers | Networking |
  |---|---|---|---|---|---|
  | Copper | 3,600 | 3,500 | 2,200 | 2,000 | 280 |
  | Aluminum | 6,700 | 460 | 1,200 | 2,700 | 260 |
  | Iron | 18,000 | 9,900 | 14,000 | 5,100 | 660 |
  | Nickel | 130 | 70 | 220 | 35 | 15 |
  | Lead | 10 | — | 240 | 15 | — |
  | Tin | 0.1 | 5 | 2 | 120 | 10 |
  | Silver | <0.1 | 1 | 0.5 | 5 | 0.5 |
  | Gold | <0.1 | 0.2 | <0.1 | 1 | <0.1 |
  | Cobalt | — | — | 40 | 2 | 1 |
  | Lithium | — | — | 30 | — | — |
  | Gallium | — | — | — | 2 | 0.3 |

  "<0.1" is entered as 0.05; "—" (not listed) as 0. Germanium, rare earths,
  graphite and silicon are also in the figure but are not modelled as priced
  metals (tiny quantities and/or no free price feed; graphite stays in the UPS
  panel).
- **Why these 11 (priority):** mass per MW (steel/iron, aluminum, copper, then
  nickel, lead, tin) plus value / supply-criticality from the same figure's
  "value chain contribution to global demand (2035)" row: data centres ≈ 6.0%
  of global gallium demand, 2.4% germanium, 1.2% tin, 0.9% copper, 0.6% gold,
  0.5% cobalt, 0.4% silver, 0.3% nickel and aluminum, 0.1% lithium.
- **Facility vs compute:** cooling + electrical + backup (+ building structure and
  near-site power connections) = FACILITY / campus shell infrastructure;
  servers + networking = COMPUTE equipment.
- **Double-counting rules:** copper keeps the existing 26 t/MW headline (entry 3);
  WEF's five components sum to ~11.6 t/MW and the ~14.4 t/MW remainder is
  attributed to near-site power connections (facility). Aluminum keeps 11.3 t/MW
  (= the WEF sum, entry 5). Steel keeps the 0.016 t/sq ft building benchmark
  (re-expressed as 64 t/MW at 250 W/sq ft) on the facility side; WEF's
  cooling/electrical/backup equipment iron (~42 t/MW) is **not** added, because
  the building-steel source says it already covers cooling systems and equipment
  support and the overlap cannot be separated. Only WEF's server + networking
  iron (~5.8 t/MW: chassis, racks) is added, on the compute side.
- **Static prices (metals not on Metals.Dev), checked 2026-10-15:**
  - **Tin $54,900/t** — LME tin settlement, 8 Sep 2026 (via cbonds LME tin index /
    Westmetall). https://cbonds.com/indexes/181087/ · https://www.westmetall.com/en/markdaten.php
  - **Cobalt ~$53,600/t** — cobalt metal, Rotterdam, 2 Oct 2026; China domestic
    was ~$39,000/t on 30 Sep 2026 (via critical-minerals-news.com, citing SMM).
    https://critical-minerals-news.com/cobalt-price/
  - **Lithium ~$105,100/t contained Li** — derived from battery-grade lithium
    carbonate **$19,750/t** (Benchmark Mineral Intelligence, CIF Asia, 2 Sep 2026)
    ÷ 18.8% lithium content of Li2CO3. https://axis-intelligence.com/lithium-price/
    **Caveat:** WEF does not state whether its lithium figure is contained Li or
    carbonate-equivalent; contained Li is assumed. If it is LCE, the lithium value
    is overstated ~5x (immaterial to the total either way: ~$3k/MW).
  - **Gallium $433/kg** — China FOB export price, 30 Sep 2026 (rare-earth-mining.com,
    citing SMM / USGS). Split market: China domestic ~$229/kg; European
    high-purity spot has traded far higher. https://rare-earth-mining.com/gallium-price/
  - **Steel $900/t** — unchanged (entry 8).
- **Valuation basis (IMPORTANT):** values are **contained metal** (tonnes × refined
  metal spot/reference price). This is the tool's existing "today's commodity
  terms" lens. It is **not** recoverable scrap value (recovering gold or gallium
  from boards is partial and costly) and **not** the price of the product the
  metal sits in (nickel sulphate, lithium carbonate, GaN wafers).
- **Notable result to sanity-check:** gold is the second-largest metal by value
  after copper (~1.35 kg/MW, almost all in server boards; ~$170k/MW at ~$3,900/oz).
  An independent order-of-magnitude check (high-grade server boards carry roughly
  100-300 g Au per tonne of board; a MW of servers carries on the order of 1-2 t of
  board) gives a few hundred g to ~1 kg/MW, so the WEF figure is plausible but at
  the high end. Not adjusted.
- **Considered, not modelled:** zinc (galvanising; no citable per-MW or per-sq-ft
  data-center figure found, and absent from WEF Fig. 4, though it is on
  Metals.Dev), platinum/palladium (on Metals.Dev, no intensity source),
  germanium and rare earths (≤3 kg/MW, no free price).

## 15. Build-type profiles (hyperscale campus, modular / prefab, liquid-cooled AI)

No primary engineering source compares metals mix across build types. The
**hyperscale campus** profile is the tool's existing, cross-validated baseline.
The other two use multipliers on **facility-side** copper / aluminum / structural
steel (compute-side intensities are not varied) plus concrete, stainless and
density, built from secondary sources, derivations and explicit judgement calls.
They are directional, not measured take-offs. The archetypes are described
generically in the UI and code; the research started from publicly reported
practices of leading Western hyperscale builders, which are deliberately not
named.

| | Hyperscale campus | Modular / prefab | Liquid-cooled AI |
|---|---|---|---|
| Power density (W/sq ft) | 250 (entry 1) | 200 — judgement, low | 800 — sourced band 600-1,200, medium |
| Copper (facility) | ×1.0 — high | ×1.0 (0.9-1.1) — no source, low | ×1.5 (1.3-2.0) — trade press, medium-low |
| Aluminum (facility) | ×1.0 — medium | ×1.1 (1.0-1.2) — judgement, low | ×0.8 (0.7-1.0) — judgement, low |
| Structural steel per MW | ×1.0 — medium-high | ×1.25 (1.1-1.4) — derived, low-medium | ×0.55 (0.4-0.7) — derived, low-medium |
| Concrete per MW | ×1.0 | ×0.5 (0.4-0.7) — low-medium | ×0.7 (0.5-0.9) — low |
| Stainless pipework | ~0 | ~0 | +1.5 t/MW (0.5-5) — derived, low; quantity only |
| Shell $/MW | $1.5M (entry 9) | $1.3M — ~13% lower first cost, low | $1.5M — see below, medium-low |
| PUE | 1.2 — judgement | 1.3 — judgement, low | 1.15 — medium-low |

**Evidence:**
- *Copper, AI:* trade-press figures of 20-40 t/MW for modern liquid-cooled vs
  8-15 t/MW traditional (Copper Development Association via Fastmarkets, entry 3),
  and 15-21 vs up to 47 t/MW (attributed to BHP analysis). These mix inside-the-
  fence and near-site scope, so the midpoint ×1.5 is applied with a wide range.
  Rack busbars themselves are small (~0.2 t/MW per the GPU vendor's 800 V DC
  material, which also says next-generation 800 V DC distribution can cut
  distribution copper by up to ~45%; that would pull AI copper back to ~×1.1-1.3).
  One press source says immersion cooling uses 40-60% more copper than air,
  supporting the upper half of the range for immersion sites.
  - https://blog.copper.org/data-centers/the-copper-advantage-in-high-density-data-center-cooling
  - https://www.bhp.com/news/bhp-insights/2025/01/why-ai-tools-and-data-centres-are-driving-copper-demand
  - https://developer.nvidia.com/blog/nvidia-800-v-hvdc-architecture-will-power-the-next-Generation-of-ai-factories
  - https://investinglive.com/news/the-500000-ton-typo-why-data-center-copper-math-doesnt-add-up-20260113/
  - https://www.woodmac.com/es/news/opinion/data-centres-copper-and-the-power-paradox/
- *Aluminum:* cooling is ~55% of in-facility aluminum (WEF Fig. 4); liquid cooling
  removes ~70-90% of heat from air, so fewer air-handler coils, but dry coolers
  still use aluminum fins. No source quantifies the per-archetype change.
- *Steel and concrete, AI:* floor area per MW falls 2.5-5× while slabs and frames
  are heavier per sq ft (racks 4,000-8,000 lb; slabs 12-18" vs 6-8").
  - https://www.datacenterknowledge.com/build-design/heavy-compute-ai-data-centers-have-a-weight-problem
  - https://www.giatecscientific.com/education/data-center-concrete-challenges/
- *Steel and concrete, modular:* a power/cooling vendor's steel-frame modular
  life-cycle study reports >50% lower embodied carbon, mainly from replacing the
  concrete shell with steel frames (tonnages behind a registration wall).
  - https://www.vertiv.com/en-us/about/news-and-insights/articles/white-papers/how-steel-frame-modular-construction-cuts-data-center-embodied-carbon-by-more-than-half/
- *Modular cost / speed:* prefab power and cooling modules quoted at ≥13% lower
  first cost and substantially faster delivery (12-18 vs 24-36 months).
  - https://www.apc.com/salestools/WTOL-7NGRBS/WTOL-7NGRBS_R3_EN.pdf
  - https://www.datacentres.com/news/factory-built-and-fast-modular-construction-cuts-data-centre-delivery-times-by-4-slot1-2026-09-02
- *AI density:* ~1,200 W/sq ft on a 1.2 GW, ~1M sq ft liquid-cooled project; rack-
  scale GPU systems at 120-140 kW/rack.
  - https://www.greshamsmith.com/projects/confidential-hyperscale-ai-data-center/
  - https://newsletter.semianalysis.com/p/gb200-hardware-architecture-and-component
- *Stainless, AI:* an industry estimate that a 100 MW AI campus needs ~50,000-
  200,000 linear ft of 1/2"-4" welded stainless pipe; at ~2-5 lb/ft (Schedule 10S)
  that is ~45-450 t per 100 MW → 0.5-5 t/MW, 1.5 used. Low confidence; shown as a
  quantity only.
  - https://www.titanfittings.com/articles/data-center-liquid-cooling-fittings
- *Shell $/MW, AI:* Turner & Townsend put core/shell at ~9% of a liquid-cooled AI
  build vs ~14% air-cooled (entry 9), but of a higher all-in cost (~$14M+/MW vs
  ~$11M/MW), landing at a similar shell $/MW, so the baseline $1.5M/MW is kept.
- *PUE:* global average 1.54 (sixth flat year); owner-operated hyperscale
  ~1.10-1.15; colocation/enterprise ~1.58-1.80 (Uptime Institute Global Data
  Center Survey 2025, via trade press).
  - https://mgrid.org/2025/10/01/uptime-institute-data-center-pue-stagnation-2025-liquid-cooling/

## 16. Compute hardware capex reference (liquid-cooled AI only; NOT in the total)

- **Figure:** ~$26.1M per MW for servers ($21.2B) + networking ($4.9B) in a 1 GW
  AI campus (total capex $37.9B; facility $11.4B), modelled for a hyperscaler-
  owned campus with current rack-scale GPU servers, 5-year IT life.
- **Source:** Epoch AI, "AI data center cost breakdown" data insight (14 May 2026).
  https://epoch.ai/data-insights/ai-datacenter-cost-breakdown
- **Why reference-only:** the tool values everything on a contained-commodity basis;
  equipment purchase cost is a different basis, depreciates over ~5 years, and is
  usually financed separately from the site. It is shown for scale only, and only
  for the AI build type (no reliable public figure was found for a mixed CPU/GPU
  campus fleet or for modular builds).

## 17. Power / capacity layer (MW ⇄ GWh/yr, state electricity tariff)

- **Unit convention:** MW of IT capacity is primary (matches the existing app);
  GWh/yr of IT energy is accepted as an alternative input and shown as an output.
- **Utilization (default 67%, user-adjustable 10-100%):** the California Energy
  Commission's 2024 IEPR data-center forecast assumes peak data-center load ≈ 67%
  of requested capacity, based on existing data centers. Used here as the average
  utilization, which is a simplification (annual average is at or below peak).
  Published observed load factors range from >52% (Texas hyperscale profiles) to
  ~90% (some academic models).
  - https://www.energy.ca.gov/sites/default/files/2025-03/Data_Center_Forecast_Final_ada.pdf
- **Formulae:** IT GWh/yr = MW × 8,760 × utilization ÷ 1,000; facility GWh/yr = IT
  GWh × PUE (build type, entry 15).
- **State tariff:** US EIA Electric Power Monthly, Table 5.6.B, average price of
  electricity to **industrial** customers by state, **YTD through July 2026**
  (US 9.03 c/kWh; e.g. VA 10.08, TX 6.72, AZ 7.66, OH 10.32). YTD used rather
  than a single month to damp seasonality. Large data centers often contract
  below the state industrial average, so the annual-cost line is indicative and
  never in the site value.
  - https://www.eia.gov/electricity/monthly/xls/table_5_06_b.xlsx
- **Consistency check:** when a capacity is stated, the tool reports the implied
  W/sq ft on the parcel and flags it if the stated MW is >1.5× or <0.67× the
  parcel-implied MW at the selected build type's density.
