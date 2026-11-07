# 16 — FTA National Transit Database (NTD) data pull and US agency tiering

**Research date:** 2026-11-07 | **Topic:** download of the latest FTA NTD annual tables and computation of (1) US agencies by active bus-fleet tier, (2) rail vehicles by mode and the top-20 rail operators, (3) capital expenses by category and mode for the latest three report years, (4) the top-50 bus agencies by fleet, plus supporting tables (agency universe, fuel mix, fleet age, opex pool, ITS-proxy capex intensity by tier).

**Scope note.** All figures are United States public transit agencies that report to the NTD (includes Puerto Rico and other territories). Base year = **NTD report year 2025** (agency fiscal years ending in 2025; FTA published these tables on data.transportation.gov on 5–14 Oct 2026, i.e. this is the newest available edition). Prior years 2022–2024 are used for trend. "Bus" (Roadway) = NTD modes MB motorbus, CB commuter bus, RB bus rapid transit, TB trolleybus; demand response (DR), vanpool (VP) and publico (PB) are shown separately. "Rail" (Railway) = HR heavy rail (metro), LR light rail, SR streetcar, CR commuter rail, YR hybrid rail, MG monorail/automated guideway, plus CC cable car, IP inclined plane, AR Alaska Railroad and TR aerial tramway (the last four are immaterial and are flagged). Freight rail is not in the NTD.

**Method and data provenance.** transit.dot.gov (the NTD home) and apta.com are blocked by the session network policy (HTTP 403 on first attempt and on a retry at the end of the work), and the per-turn web-search budget was already exhausted, so no web searches could be run for this topic. The same NTD products are federated on the USDOT open-data portal (data.transportation.gov / datahub.transportation.gov, Socrata), which is reachable. Fifteen tables were downloaded as full CSV exports (`https://data.transportation.gov/api/views/<id>/rows.csv?accessType=DOWNLOAD`) into a fresh folder, `/home/user/Project-2-/its-market-case/data/ntd/`, and parsed row counts were checked against the API's `count(*)` for the six load-bearing tables (all match: RVI 35,625; Vehicles 10,858; Capital Expenses 17,285; Capital Use 5,193; Capex time series 155,408; Agency Information 2,897). Download script: `/home/user/Project-2-/its-market-case/model/scripts/ntd_download.sh`. Analysis script (run with `python3 -I`, inputs treated as untrusted data): `/home/user/Project-2-/its-market-case/model/scripts/ntd_tiering.py`. Outputs: 21 CSVs in `/home/user/Project-2-/its-market-case/data/` (index in section 9). The 2023 and 2024 *Revenue Vehicle Inventory* raw files exist on Socrata only as "href" entries pointing to transit.dot.gov Excel downloads (blocked), so the 2022–2024 fleet trend uses the FTA-built "2022–2025 Vehicles (Type Count by Agency)" table instead; its 2025 full-size-bus total (65,239) exactly equals the active count computed from the 2025 Revenue Vehicle Inventory, which confirms that table counts *active* vehicles and that the two sources are consistent.

**Confidence legend.** high = primary source (NTD tables, counts verified against the API) or consistent across two independent NTD tables; medium = my own aggregation that involves a scope or definition choice; low = inferred.

---

## 1. Key takeaways

1. **The US bus (roadway) customer universe is 977 agencies operating 65,239 active full-size buses (FY2025), and it is a steep pyramid: 10 agencies with 1,000+ buses hold 29% of the fleet, 46 agencies with 250–999 hold 31%, 149 with 50–249 hold 23%, and 772 agencies with 1–49 buses hold only 16%.** The top-50 agencies own 58% of all active full-size buses, the top-100 own 72%, the top-200 own 84%. If cutaways/vans used in fixed-route bus modes are included, the fixed-route bus-mode fleet is 73,112 active vehicles at 1,223 agencies, with the same tier shape.
2. **The fleet is flat.** Active full-size buses were 65,642 (2022) → 65,629 (2023) → 64,753 (2024) → 65,239 (2025); the number of agencies with any full-size bus fell from 1,027 to 977, and the 1,000+ tier shrank from 12 to 10 agencies (Maryland MTA at 976 and Denver RTD at 968 now sit just below the line). Growth in ITS spend therefore has to come from penetration, refresh and price/mix, not fleet growth.
3. **US rail (railway) is 80 operators and 23,666 active rail passenger vehicles (ex-locomotives) plus 923 locomotives (FY2025): 12,946 heavy-rail cars (17 operators, of which MTA New York City Transit alone has 6,840 = 53%), 7,406 commuter-rail cars (27 operators; 3,734 self-propelled + 3,672 coaches) with 865 locomotives, 2,527 light-rail vehicles (22 operators), 418 streetcars (25 operators), and 302 vehicles across monorail/AGT, hybrid rail, aerial tram, Alaska Railroad, cable car and inclined plane.** The top-20 rail operators hold 88% of active rail vehicles; the top-10 hold 73%.
4. **Transit capital expenditure reached $32.35B in FY2025 (rail $21.68B, bus $9.20B, demand response/vanpool $1.05B, ferry $0.42B), up from $27.39B (2023) and $29.35B (2024); the 2015–2025 CAGR is 5.2% (bus 6.2%, rail 4.7%).** Passenger-vehicle (rolling stock) capex jumped to $8.80B in 2025 from $5.15B in 2023, with bus rolling stock $4.24B (+75% in two years) — a bus replacement wave that pulls on-vehicle ITS hardware (AVL/MDT, cameras, APC, displays) with it.
5. **The NTD's closest ITS proxy, the "Communication & Information Systems" capital category, was $1.90B in FY2025 ($2.17B in 2023, $2.24B in 2024), i.e. 5.9% of all capex; rail took $1.50B (heavy rail $1.01B, commuter rail $0.26B, light rail $0.19B, streetcar $0.03B) and bus modes $0.37B (motorbus $370M).** Per the NTD definition the category covers radio, cab signaling/train control, AVL, automated dispatching, vehicle guidance, PA systems *and* computers/software supporting scheduling, planning, maintenance and customer service — so it is wider than vehicle ITS in back-office IT and narrower in that operating-funded SaaS subscriptions and maintenance contracts are excluded. 91% of the rail amount and 98% of the bus amount is for existing service (replacement/rehab), not expansion.
6. **ITS-proxy capex intensity rises with agency size and then plateaus: bus-mode Comm & Info capex per active full-size bus (3-year average 2023–25) is ~$2.1k/yr in the 1–49 tier, ~$6.5k in 50–249, ~$7.7k in 250–999 and ~$5.8k in the 1000+ tier; the fleet-weighted average is ~$5.7k per bus per year (2025; ~$5.9k 3-year average).** Only 264 of the 977 bus agencies recorded any bus-mode Comm & Info capex in 2025 (96 of 772 small agencies, 116 of 149 mid-size, 42 of 46 large, 10 of 10 mega), which indicates long replacement cycles and lumpy procurement rather than zero spend. Rail Comm & Info capex is ~$63k per active rail vehicle (2025; 3-year average ~$70k), dominated by signaling/train-control programmes; the three largest spenders (NYCT $322M, WMATA $308M, BART $149M) were 41% of the 2025 total and 328 of 2,247 capex-reporting agencies had any Comm & Info capex.
7. **The spend pools around ITS are large: FY2025 operating expenses were $70.1B (bus $34.4B, rail $26.5B, DR/VP $7.9B, ferry $1.3B), of which "Services" (purchased professional/technical services, where hosted software and maintenance contracts sit) were $6.9B (9.8%).** Fare-collection equipment capex, an adjacent category, was $521M in 2025 (bus $94M, rail $423M).
8. **Agency universe for go-to-market: 2,850 distinct NTD reporters in FY2025, but only 520 "Full Reporters" (urban, ≥30 vehicles or fixed guideway) matter for ITS: they operate 102,231 of 126,079 vehicles in maximum service, 415 of them run full-size buses and 79 of the 80 rail operators are Full Reporters.** FTA's own Transit Asset Management tiers put 158 agencies in Tier I (78 rail, 52 with ≥101 fixed-route VOMS, 28 non-fixed-route) and 2,691 in Tier II.
9. **Fleet composition flags for ITS demand: 53.6% of active full-size buses are diesel, 23.8% CNG, 13.4% hybrid, 4.4% battery-electric (2,848), 0.3% hydrogen (202), 0.8% trolleybus; average bus age is 8.3 years against a 12–14-year ULB, while heavy-rail cars average 22.3 years, light-rail 20.1, commuter coaches 28.6 and self-propelled commuter cars 19.4** — the rail fleet is old and rolling-stock replacement (with onboard CBTC/PTC, CCTV, passenger information) is a multi-year driver.

---

## 2. Findings table

| # | Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Active full-size buses (Bus, Articulated, Over-the-road, Double-decker, Trolleybus), all NTD reporters | 65,239 | vehicles | FY2025 | US | Bus | NTD 2025 Revenue Vehicle Inventory | https://datahub.transportation.gov/d/ifzt-j53d | high | Total fleet incl. inactive/contingency = 69,423. Split: 53,033 standard, 6,010 articulated, 5,491 over-the-road, 535 trolleybus, 170 double-deck. Matches the FTA "Vehicles (Type Count by Agency)" 2025 figure exactly. |
| 2 | Active revenue vehicles in fixed-route bus modes MB/CB/RB/TB, any vehicle type (incl. cutaways/vans) | 73,112 | vehicles | FY2025 | US | Bus | NTD 2025 Revenue Vehicle Inventory | https://datahub.transportation.gov/d/ifzt-j53d | high | 64,227 are full-size buses; 1,012 full-size buses are operated in non-bus modes (mostly DR). |
| 3 | Agencies with ≥1 active full-size bus | 977 | agencies | FY2025 | US | Bus | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | 1,223 agencies operate any vehicle in a fixed-route bus mode. |
| 4 | Bus tier 1,000+: agencies / buses / share | 10 / 19,145 / 29.3% | agencies; vehicles; % | FY2025 | US | Bus | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | NYCT, NJ Transit, CTA, LA Metro, MTA Bus, SEPTA, WMATA, MBTA, Houston METRO, King County Metro. |
| 5 | Bus tier 250–999: agencies / buses / share | 46 / 20,411 / 31.3% | agencies; vehicles; % | FY2025 | US | Bus | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | Average 444 buses per agency. |
| 6 | Bus tier 50–249: agencies / buses / share | 149 / 15,142 / 23.2% | agencies; vehicles; % | FY2025 | US | Bus | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | Average 102 buses per agency. |
| 7 | Bus tier 1–49: agencies / buses / share | 772 / 10,541 / 16.2% | agencies; vehicles; % | FY2025 | US | Bus | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | 79% of bus agencies; average 14 buses. |
| 8 | Bus concentration: top-10 / top-20 / top-50 / top-100 / top-200 share of active full-size buses | 29.3 / 40.8 / 58.2 / 71.8 / 83.5 | % | FY2025 | US | Bus | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | |
| 9 | Active full-size bus fleet trend | 65,642 → 65,629 → 64,753 → 65,239 | vehicles | 2022–2025 | US | Bus | NTD 2022–2025 Vehicles (Type Count by Agency) | https://datahub.transportation.gov/d/nimp-626k | high | Agencies with buses 1,027 → 1,006 → 998 → 977; 1,000+ tier 12 → 12 → 10 → 10 agencies. |
| 10 | Active rail passenger vehicles ex-locomotives / locomotives / rail operators | 23,666 / 923 / 80 | vehicles; vehicles; operators | FY2025 | US | Rail | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | Total incl. inactive = 24,519 ex-loco. |
| 11 | Heavy rail (metro) cars / operators | 12,946 / 17 | vehicles; operators | FY2025 | US | Rail – metro | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | NYCT 6,840 (52.8%), CTA 1,708, WMATA 1,202, BART 971, MBTA 460, PATH 422, SEPTA 339, MARTA 262. |
| 12 | Commuter rail cars (self-propelled + coaches) / locomotives / operators | 7,406 / 865 / 27 | vehicles; vehicles; operators | FY2025 | US | Rail – commuter | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | 3,734 self-propelled (12 operators) + 3,672 coaches (24 operators); locomotives at 23 operators. Alaska Railroad (42 coaches, 58 locos) shown separately. |
| 13 | Light rail vehicles / operators | 2,527 / 22 | vehicles; operators | FY2025 | US | Rail – LRT | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | 2,518 LRVs + 9 vintage trolleys in LR mode. LA Metro 320, SFMTA 208, Sound Transit 207, Denver RTD 201, MBTA 192, DART 162. |
| 14 | Streetcar vehicles / operators | 418 / 25 | vehicles; operators | FY2025 | US | Rail – streetcar | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | 338 LRV-type + 80 vintage trolleys; SEPTA 159 is the largest. |
| 15 | Other rail: monorail/AGT, hybrid rail, aerial tram, Alaska RR coaches, cable car, inclined plane | 117 / 92 / 73 / 42 / 39 / 6 | vehicles | FY2025 | US | Rail – other | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | Immaterial for ITS sizing; flagged. |
| 16 | Top-20 rail operators' share of active rail vehicles (ex-loco) | 88.0 | % | FY2025 | US | Rail | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | Top-10 = 73.4%. List in section 4. |
| 17 | Total transit capital expenses | 27.39 / 29.35 / 32.35 | US$ B | 2023 / 2024 / 2025 | US | All modes | NTD 2022–2025 Capital Expenses (by Capital Use) | https://datahub.transportation.gov/d/fphd-jyyj | high | 2025 total cross-checks exactly to the 2025 Capital Use file ($32.347B). |
| 18 | Capital expenses, bus modes (MB/CB/RB/TB) | 6.01 / 7.44 / 9.20 | US$ B | 2023 / 2024 / 2025 | US | Bus | NTD 2022–2025 Capital Expenses | https://datahub.transportation.gov/d/fphd-jyyj | high | Rail: 20.52 / 20.60 / 21.68; DR/VP: 0.53 / 0.93 / 1.05; ferry 0.32 / 0.39 / 0.42. |
| 19 | Capex "Communication & Information Systems" (ITS proxy), all modes | 2.167 / 2.244 / 1.904 | US$ B | 2023 / 2024 / 2025 | US | All modes | NTD 2022–2025 Capital Expenses | https://datahub.transportation.gov/d/fphd-jyyj | high | 7.9% / 7.6% / 5.9% of total capex. 2022: $2.11B. |
| 20 | Comm & Info capex, bus modes | 405 / 386 / 372 | US$ M | 2023 / 2024 / 2025 | US | Bus | NTD 2022–2025 Capital Expenses | https://datahub.transportation.gov/d/fphd-jyyj | high | Motorbus 403 / 380 / 370; BRT, commuter bus, trolleybus <$5M each. 4.0% of bus capex in 2025. |
| 21 | Comm & Info capex, rail modes | 1,739 / 1,830 / 1,497 | US$ M | 2023 / 2024 / 2025 | US | Rail | NTD 2022–2025 Capital Expenses | https://datahub.transportation.gov/d/fphd-jyyj | high | 2025: HR 1,008; CR 259; LR 186; SR 35; AR 5; YR 3; MG 1. 6.9% of rail capex. |
| 22 | Comm & Info capex 2025 split existing service vs expansion | Rail 1,362 vs 135; Bus 364 vs 8 | US$ M | 2025 | US | Rail; Bus | NTD 2022–2025 Capital Expenses | https://datahub.transportation.gov/d/fphd-jyyj | high | Replacement/rehab dominates (91% rail, 98% bus). |
| 23 | Comm & Info capex concentration | 328 of 2,247 agencies >0; top-10 = 65%; top-25 = 83% | agencies; % | 2025 | US | All modes | NTD 2022–2025 Capital Expenses (computed) | https://datahub.transportation.gov/d/fphd-jyyj | high | NYCT $322M, WMATA $308M, BART $149M, LIRR $83M, SEPTA $82M, MD MTA $79M, LA Metro $67M (of which $60M bus), Valley Metro Rail $54M, MBTA $52M, Sound Transit $45M. |
| 24 | Bus-mode Comm & Info capex per active full-size bus, by tier (3-yr avg 2023–25) | 1–49: 2,057; 50–249: 6,487; 250–999: 7,650; 1000+: 5,817 | US$ per bus per year | 2023–2025 | US | Bus | NTD RVI + Capital Expenses (computed) | https://datahub.transportation.gov/d/fphd-jyyj | medium | 2025-only: 2,239 / 5,357 / 7,072 / 6,425. Fleet-weighted 2025 average $5.7k. Only 264 of 977 bus agencies had any such capex in 2025 (lumpy). |
| 25 | Rail-mode Comm & Info capex per active rail vehicle (ex-loco) | 63,300 (2025); ~70,000 (3-yr avg) | US$ per vehicle per year | 2023–2025 | US | Rail | NTD RVI + Capital Expenses (computed) | https://datahub.transportation.gov/d/fphd-jyyj | medium | By operator size (3-yr avg): 1000+ vehicles $68k; 500–999 $80k; 100–499 $61k; 1–99 $115k (small operators building new lines). Includes signaling/train control. |
| 26 | Passenger-vehicle (rolling stock) capex | 5.15 / 7.17 / 8.80 | US$ B | 2023 / 2024 / 2025 | US | All modes | NTD 2022–2025 Capital Expenses | https://datahub.transportation.gov/d/fphd-jyyj | high | Bus 2.43 / 3.04 / 4.24; rail 2.36 / 3.40 / 3.77. |
| 27 | Fare collection equipment capex (adjacent) | 360 / 404 / 521 | US$ M | 2023 / 2024 / 2025 | US | All modes | NTD 2022–2025 Capital Expenses | https://datahub.transportation.gov/d/fphd-jyyj | high | 2025: rail 423, bus 94. Out of core ITS scope; flagged. |
| 28 | Total capex time series | 19.48 (2015) → 24.42 (2019) → 26.79 (2022) → 32.36 (2025) | US$ B | 2015–2025 | US | All modes | NTD 2025 Capital Expenditures Time Series 3.1 | https://datahub.transportation.gov/d/8ffu-2anj | high | 10-yr CAGR 5.2%; bus 5.07 → 9.21 (6.2%); rail 13.73 → 21.68 (4.7%). Nominal dollars. |
| 29 | Operating expenses, all modes / bus / rail / DR+VP | 70.1 / 34.4 / 26.5 / 7.9 | US$ B | FY2025 | US | All | NTD 2022–2025 Operating Expenses (by Function) | https://datahub.transportation.gov/d/dkxx-zjd6 | high | 2022: 53.7 / 26.8 / 20.1 / 5.9. |
| 30 | Operating "Services" expense (purchased professional/technical services) | 6.90 (9.8% of opex); bus 3.24; rail 3.17 | US$ B; % | FY2025 | US | All | NTD 2022–2025 Operating Expenses (by Type) | https://datahub.transportation.gov/d/j5uj-anzx | high | Where hosted software/maintenance contracts are booked; not separable from other services. |
| 31 | NTD reporters (distinct NTD IDs) / Full Reporters / Full Reporters' VOMS | 2,850 / 520 / 102,231 of 126,079 | agencies; vehicles | FY2025 | US | All | NTD 2025 Reporter Agency Information | https://datahub.transportation.gov/d/jm7a-9hsy | high | 2,897 rows; 16 rural intercity operators appear under several state sponsors. 415 Full Reporters run full-size buses; 79 of 80 rail operators are Full Reporters. |
| 32 | FTA TAM tiers: Tier I rail / Tier I fixed-route (≥101 VOMS) / Tier I non-fixed-route / Tier II | 78 / 52 / 28 / 2,691 | agencies | FY2025 | US | All | NTD 2025 Reporter Agency Information | https://datahub.transportation.gov/d/jm7a-9hsy | high | |
| 33 | Active full-size bus fuel mix: diesel / CNG / hybrid diesel / battery-electric / hydrogen / trolleybus | 53.6 / 23.8 / 13.4 / 4.4 / 0.3 / 0.8 | % of 65,239 | FY2025 | US | Bus | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | BEB 2,848 active at 238 agencies; FCEB 202 at 18 agencies. |
| 34 | Weighted average fleet age: bus / articulated / heavy-rail car / LRV / commuter coach / commuter self-propelled / locomotive | 8.3 / 8.5 / 22.3 / 20.1 / 28.6 / 19.4 / 26.0 | years | FY2025 | US | Bus; Rail | NTD 2022–2025 Vehicles (Age Distribution) | https://datahub.transportation.gov/d/6abt-uhgq | high | Weighted by vehicles across agencies. |
| 35 | Top-50 bus agencies by active full-size buses (list) | NYCT 4,583; NJ Transit 2,542; CTA 2,012; LA Metro 1,999; MTA Bus 1,396; SEPTA 1,358; WMATA 1,349; MBTA 1,317; Houston METRO 1,305; King County Metro 1,284 … #50 Hampton Roads Transit 272 | vehicles | FY2025 | US | Bus | NTD 2025 RVI (computed) | https://datahub.transportation.gov/d/ifzt-j53d | high | Full list with sub-types, ZEBs, age, VOMS, UPT and ITS-proxy capex in `ntd_2025_top50_bus_agencies.csv`. |

---

## 3. Bus (roadway) agency tiering

### 3.1 FY2025 tiers — definition A: active full-size buses, any mode (primary)

| Tier (active full-size buses) | Agencies | Share of agencies | Active buses | Share of buses | Avg buses/agency |
|---|---|---|---|---|---|
| 1,000+ | 10 | 1.0% | 19,145 | 29.3% | 1,915 |
| 250–999 | 46 | 4.7% | 20,411 | 31.3% | 444 |
| 50–249 | 149 | 15.3% | 15,142 | 23.2% | 102 |
| 1–49 | 772 | 79.0% | 10,541 | 16.2% | 14 |
| **Total** | **977** | 100% | **65,239** | 100% | 67 |

Definition B (all active vehicles in fixed-route bus modes MB/CB/RB/TB, including cutaways and vans): 1,000+: 10 agencies / 19,267 vehicles; 250–999: 47 / 20,971; 50–249: 177 / 17,521; 1–49: 989 / 15,353; total 1,223 agencies / 73,112 vehicles. Definitions C (full-size buses in bus modes only) and D (total incl. inactive) are in `ntd_2025_bus_agency_tiers.csv`.

### 3.2 Tier trend 2022–2025 (FTA Vehicles Type Count table; active full-size buses)

| Tier | 2022 agencies / buses | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| 1,000+ | 12 / 21,239 | 12 / 20,963 | 10 / 18,994 | 10 / 19,145 |
| 250–999 | 44 / 18,849 | 43 / 18,581 | 44 / 19,579 | 46 / 20,411 |
| 50–249 | 149 / 15,059 | 147 / 15,357 | 149 / 15,627 | 149 / 15,142 |
| 1–49 | 822 / 10,495 | 804 / 10,728 | 795 / 10,553 | 772 / 10,541 |
| **Total** | **1,027 / 65,642** | **1,006 / 65,629** | **998 / 64,753** | **977 / 65,239** |

### 3.3 ITS-proxy capex intensity by bus tier (bus-mode "Communication & Information Systems" capex)

| Tier | Agencies | Active buses | Agencies with bus Comm&Info capex in 2025 | Comm&Info capex 2025 ($M) | 3-yr avg 2023–25 ($M/yr) | $ per bus 2025 | $ per bus 3-yr avg |
|---|---|---|---|---|---|---|---|
| 1,000+ | 10 | 19,145 | 10 | 123.0 | 111.4 | 6,425 | 5,817 |
| 250–999 | 46 | 20,411 | 42 | 144.3 | 156.1 | 7,072 | 7,650 |
| 50–249 | 149 | 15,142 | 116 | 81.1 | 98.2 | 5,357 | 6,487 |
| 1–49 | 772 | 10,541 | 96 | 23.6 | 21.7 | 2,239 | 2,057 |
| **All bus agencies** | **977** | **65,239** | **264** | **372.1** | **387.4** | **5,703** | **5,938** |

Reading: a large agency spends on the order of $6–8k per bus per year of capital on communications/IT (lumpy: a CAD/AVL replacement lands every 10–15 years), and the long tail of small agencies spends ~$2k, and only one in eight of them in any given year. Source: computed from https://datahub.transportation.gov/d/fphd-jyyj and https://datahub.transportation.gov/d/ifzt-j53d (medium confidence: category is wider than vehicle ITS and excludes operating-funded SaaS).

---

## 4. Rail (railway) fleet by mode and the top-20 operators (FY2025)

| Mode | Operators | Active vehicles ex-locomotives | Total incl. inactive | Active locomotives | Vehicle types |
|---|---|---|---|---|---|
| HR Heavy rail (metro) | 17 | 12,946 | 13,122 | – | heavy-rail passenger cars |
| CR Commuter rail | 27 | 7,406 | 7,911 | 865 | 3,734 self-propelled cars (12 operators) + 3,672 coaches (24) |
| LR Light rail | 22 | 2,527 | 2,661 | – | 2,518 LRVs + 9 vintage trolleys |
| SR Streetcar | 25 | 418 | 442 | – | 338 LRV-type + 80 vintage trolleys |
| MG Monorail / AGT | 6 | 117 | 126 | – | 109 AGT + 8 monorail |
| YR Hybrid rail | 6 | 92 | 96 | – | DMU/EMU + LRV |
| TR Aerial tramway | 2 | 73 | 73 | – | flagged, not ITS-relevant |
| AR Alaska Railroad | 1 | 42 | 42 | 58 | flagged |
| CC Cable car | 1 | 39 | 40 | – | flagged |
| IP Inclined plane | 3 | 6 | 6 | – | flagged |
| **All rail** | **80** | **23,666** | **24,519** | **923** | |

Top-20 rail operators by active rail vehicles (ex-locomotives):

| # | Operator | State | HR | LR | SR | CR | Other | Rail vehicles ex-loco | Locos | Cum. share |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | MTA New York City Transit | NY | 6,840 | – | – | – | – | 6,840 | – | 28.9% |
| 2 | Chicago Transit Authority | IL | 1,708 | – | – | – | – | 1,708 | – | 36.1% |
| 3 | MTA Metro-North Railroad | NY | – | – | – | 1,218 | – | 1,218 | 60 | 41.3% |
| 4 | MTA Long Island Rail Road | NY | – | – | – | 1,213 | – | 1,213 | 41 | 46.4% |
| 5 | WMATA | DC | 1,202 | – | – | – | – | 1,202 | – | 51.5% |
| 6 | NJ Transit | NJ | – | 72 | – | 1,105 | 20 (YR) | 1,197 | 201 | 56.5% |
| 7 | MBTA | MA | 460 | 192 | – | 444 | – | 1,096 | 90 | 61.2% |
| 8 | Metra (NIRCRC) | IL | – | – | – | 1,018 | – | 1,018 | 177 | 65.5% |
| 9 | BART | CA | 971 | – | – | – | 16 (YR) + 4 (MG) | 991 | – | 69.6% |
| 10 | SEPTA | PA | 339 | – | 159 | 396 | – | 894 | 15 | 73.4% |
| 11 | Connecticut DOT | CT | – | – | – | 703 | – | 703 | 28 | 76.4% |
| 12 | PATH | NY | 422 | – | – | – | – | 422 | – | 78.2% |
| 13 | LA Metro | CA | 98 | 320 | – | – | – | 418 | – | 79.9% |
| 14 | Denver RTD | CO | – | 201 | – | 132 | – | 333 | – | 81.4% |
| 15 | Maryland Transit Administration | MD | 86 | 53 | – | 177 | – | 316 | 48 | 82.7% |
| 16 | SFMTA (City & County of San Francisco) | CA | – | 208 | 44 | – | 39 (CC) | 291 | – | 83.9% |
| 17 | Sound Transit | WA | – | 207 | 8 | 63 | – | 278 | 14 | 85.1% |
| 18 | MARTA | GA | 262 | – | 3 | – | – | 265 | – | 86.2% |
| 19 | Metrolink (SCRRA) | CA | – | – | – | 229 | – | 229 | 56 | 87.2% |
| 20 | DART | TX | – | 162 | 4 | 25 | – | 191 | 11 | 88.0% |

"Other" components are read from `ntd_2025_top20_rail_operators.csv` (YR/MG/CC columns). Source: https://datahub.transportation.gov/d/ifzt-j53d (high confidence).

---

## 5. Capital expenses by category and mode, FY2023–FY2025 (US$ million)

| Report year | Mode group | Guideway | Stations | Admin bldgs | Maint. bldgs | Passenger vehicles | Other vehicles | Fare collection | Comm & Info Systems | Other | Reduced-reporter (not itemised) | **Total** | Comm&Info % of total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023 | Bus | 492 | 433 | 329 | 1,103 | 2,426 | 59 | 112 | 405 | 267 | 387 | **6,013** | 6.7% |
| 2023 | Rail | 10,564 | 3,540 | 312 | 1,045 | 2,358 | 239 | 247 | 1,739 | 480 | 0 | **20,524** | 8.5% |
| 2023 | DR / vanpool | 0 | 0 | 22 | 31 | 242 | 2 | 1 | 16 | 5 | 213 | **532** | 2.9% |
| 2023 | Ferry | 0 | 143 | 1 | 27 | 127 | 0 | 0 | 7 | 0 | 10 | **317** | 2.2% |
| 2023 | **All modes** | 11,056 | 4,116 | 665 | 2,206 | 5,153 | 300 | 360 | 2,167 | 753 | 610 | **27,386** | 7.9% |
| 2024 | Bus | 845 | 508 | 297 | 1,403 | 3,044 | 95 | 135 | 386 | 247 | 477 | **7,438** | 5.2% |
| 2024 | Rail | 9,459 | 3,897 | 267 | 922 | 3,400 | 245 | 266 | 1,830 | 311 | 0 | **20,598** | 8.9% |
| 2024 | DR / vanpool | 0 | 0 | 49 | 17 | 477 | 5 | 2 | 20 | 4 | 356 | **930** | 2.1% |
| 2024 | Ferry | 0 | 97 | 3 | 16 | 250 | 0 | 1 | 8 | 0 | 11 | **386** | 2.1% |
| 2024 | **All modes** | 10,304 | 4,501 | 616 | 2,358 | 7,172 | 345 | 404 | 2,244 | 563 | 844 | **29,351** | 7.6% |
| 2025 | Bus | 858 | 674 | 470 | 1,654 | 4,238 | 127 | 94 | 372 | 270 | 445 | **9,201** | 4.0% |
| 2025 | Rail | 10,087 | 3,732 | 288 | 963 | 3,766 | 521 | 423 | 1,497 | 406 | 1 | **21,684** | 6.9% |
| 2025 | DR / vanpool | 0 | 0 | 19 | 56 | 545 | 4 | 3 | 23 | 3 | 394 | **1,047** | 2.2% |
| 2025 | Ferry | 0 | 114 | 3 | 24 | 255 | 2 | 1 | 11 | 0 | 5 | **415** | 2.7% |
| 2025 | **All modes** | 10,945 | 4,520 | 779 | 2,698 | 8,804 | 653 | 521 | 1,904 | 678 | 846 | **32,347** | 5.9% |

All values are from `ntd_capex_by_year_modegroup_category.csv` (US$ million, rounded; rows may differ from totals by ±1 because of rounding). Source: https://datahub.transportation.gov/d/fphd-jyyj (high confidence; 2025 total and Comm&Info cross-check exactly to the independent 2025 Capital Use file https://datahub.transportation.gov/d/8rr7-fd8y).

Comm & Info Systems capex by individual mode (US$ M): Heavy rail 1,113 / 1,191 / 1,008 (2023/24/25); Commuter rail 316 / 294 / 259; Light rail 279 / 294 / 186; Streetcar 21 / 37 / 35; Motorbus 403 / 380 / 370; BRT 0.3 / 1.4 / 1.5; Commuter bus 1.6 / 5.0 / 0.9; Trolleybus 0.1 / 0.1 / 0.1; Demand response 14 / 20 / 23; Ferry 7 / 8 / 11.

Long-run capex (Time Series 3.1, US$ B, nominal): all modes 19.5 (2015), 19.7, 19.9, 21.6, 24.4 (2019), 23.5, 24.2, 26.8 (2022), 27.4, 29.4, 32.4 (2025); bus 5.1 (2015) → 9.2 (2025); rail 13.7 → 21.7. Source: https://datahub.transportation.gov/d/8ffu-2anj.

**NTD definition of "Communication & Information Systems" (verbatim, 2025 Database File Dictionary and the Socrata column description):** "Systems for exchanging information including two-way radio systems for communications between dispatchers and vehicle operators, cab signaling and train control equipment in rail systems, automatic vehicle locator systems, automated dispatching systems, vehicle guidance systems, telephones, facsimile machines and public address systems. Systems for processing data, including computers, monitors, printers, scanners, data storage devices, and associated software that support transit operations such as general office, accounting, scheduling, planning, vehicle maintenance, non-vehicle maintenance, and customer service functions." Fare collection equipment is a separate category ("turnstiles, fare boxes…, automated fare boxes and related software, money changers and fare dispensing machines"). Sources: https://datahub.transportation.gov/d/eu97-reg7 ; https://data.transportation.gov/api/views/fphd-jyyj.json.

---

## 6. Top-50 bus agencies by active full-size buses (FY2025)

| # | Agency | State | Active full-size buses | of which articulated | BEB+FCEB | Avg age (yrs) | Bus-mode Comm&Info capex 2025 ($M) | Cum. share |
|---|---|---|---|---|---|---|---|---|
| 1 | MTA New York City Transit | NY | 4,583 | 1,017 | 77 | 8.4 | 0.5 | 7.0% |
| 2 | New Jersey Transit | NJ | 2,542 | 172 | 8 | 9.7 | 1.8 | 10.9% |
| 3 | Chicago Transit Authority | IL | 2,012 | 282 | 23 | 10.7 | 10.5 | 14.0% |
| 4 | LA Metro | CA | 1,999 | 270 | 59 | 9.2 | 60.0 | 17.1% |
| 5 | MTA Bus Company | NY | 1,396 | 145 | 0 | 7.9 | 2.7 | 19.2% |
| 6 | SEPTA | PA | 1,358 | 186 | 1 | 9.0 | 4.4 | 21.3% |
| 7 | WMATA | DC | 1,349 | 70 | 4 | 8.4 | 2.8 | 23.4% |
| 8 | MBTA | MA | 1,317 | 114 | 2 | 8.2 | 1.4 | 25.4% |
| 9 | Houston METRO | TX | 1,305 | 100 | 20 | 8.8 | 14.5 | 27.4% |
| 10 | King County Metro | WA | 1,284 | 576 | 58 | 9.8 | 24.4 | 29.3% |
| 11 | Maryland Transit Administration | MD | 976 | 49 | 0 | 6.6 | 0.2 | 30.8% |
| 12 | Denver RTD | CO | 968 | 116 | 39 | 8.3 | 5.7 | 32.3% |
| 13 | SFMTA | CA | 861 | 224 | 12 | 8.7 | 0.4 | 33.6% |
| 14 | Miami-Dade Transit | FL | 791 | 53 | 69 | 6.6 | 1.7 | 34.9% |
| 15 | Pittsburgh Regional Transit | PA | 698 | 149 | 23 | 7.2 | 1.6 | 35.9% |
| 16 | TriMet | OR | 668 | 31 | 34 | 8.4 | 16.7 | 37.0% |
| 17 | Metro Transit (Minneapolis) | MN | 650 | 196 | 0 | 8.2 | 9.6 | 37.9% |
| 18 | Pace Suburban Bus | IL | 646 | 0 | 1 | 9.1 | 8.3 | 38.9% |
| 19 | AC Transit | CA | 630 | 87 | 58 | 8.0 | 3.9 | 39.9% |
| 20 | San Diego MTS | CA | 603 | 125 | 25 | 8.2 | 0.2 | 40.8% |
| 21 | DART | TX | 586 | 0 | 0 | 9.7 | 18.8 | 41.7% |
| 22 | MARTA | GA | 535 | 18 | 6 | 8.7 | 11.9 | 42.5% |
| 23 | City of Phoenix | AZ | 513 | 100 | 0 | 6.6 | 1.2 | 43.3% |
| 24 | Utah Transit Authority | UT | 492 | 25 | 38 | 7.7 | 2.7 | 44.1% |
| 25 | Honolulu (TheBus) | HI | 485 | 117 | 17 | 11.2 | 0.6 | 44.8% |
| 26 | RTC Southern Nevada | NV | 452 | 250 | 11 | 6.1 | 0.0 | 45.5% |
| 27 | CapMetro Austin | TX | 449 | 31 | 67 | 8.8 | 14.1 | 46.2% |
| 28 | Santa Clara VTA | CA | 448 | 75 | 0 | 9.5 | 8.3 | 46.9% |
| 29 | OCTA | CA | 446 | 36 | 20 | 6.7 | 4.8 | 47.6% |
| 30 | VIA Metropolitan Transit | TX | 445 | 19 | 8 | 7.3 | 0.8 | 48.3% |
| 31 | Montgomery County MD (Ride On) | MD | 400 | 16 | 39 | 8.9 | 0.0 | 48.9% |
| 32 | Milwaukee County Transit | WI | 384 | 0 | 14 | 6.9 | 0.9 | 49.5% |
| 33 | Broward County Transit | FL | 373 | 36 | 0 | 6.9 | 1.2 | 50.0% |
| 34 | Foothill Transit | CA | 357 | 24 | 52 | 9.1 | 3.2 | 50.6% |
| 35 | City of Los Angeles (LADOT) | CA | 346 | 0 | 83 | 9.7 | 0.0 | 51.1% |
| 36 | Fairfax County (Connector) | VA | 344 | 0 | 12 | 8.3 | 0.2 | 51.6% |
| 37 | Valley Metro RPTA | AZ | 331 | 25 | 0 | 7.5 | 0.4 | 52.1% |
| 38 | SamTrans | CA | 329 | 54 | 32 | 11.0 | 0.0 | 52.7% |
| 39 | Centro (CNYRTA) | NY | 328 | 0 | 0 | 6.6 | 0.6 | 53.2% |
| 40 | North County Transit District | CA | 324 | 0 | 36 | 8.5 | 1.6 | 53.7% |
| 41 | Westchester County (Bee-Line) | NY | 324 | 78 | 13 | 8.6 | 1.7 | 54.2% |
| 42 | CDTA Albany | NY | 321 | 48 | 8 | 6.7 | 0.7 | 54.6% |
| 43 | Greater Cleveland RTA | OH | 316 | 39 | 0 | 7.2 | 1.2 | 55.1% |
| 44 | Bi-State Development (Metro St. Louis) | MO | 311 | 14 | 39 | 8.0 | 4.5 | 55.6% |
| 45 | SORTA (Cincinnati Metro) | OH | 306 | 0 | 0 | 6.8 | 1.8 | 56.1% |
| 46 | City of Detroit (DDOT) | MI | 292 | 15 | 4 | 7.9 | 0.5 | 56.5% |
| 47 | LYNX (Central Florida RTA) | FL | 292 | 29 | 7 | 6.4 | 0.6 | 57.0% |
| 48 | COTA Columbus | OH | 281 | 0 | 50 | 6.7 | 0.8 | 57.4% |
| 49 | Nassau County (NICE) | NY | 273 | 5 | 6 | 5.2 | 0.2 | 57.8% |
| 50 | Hampton Roads Transit | VA | 272 | 0 | 0 | 6.1 | 0.4 | 58.2% |

Agency short names are mine; the CSV carries the legal NTD reporter names and NTD IDs, plus total fleet, cutaways, bus-mode VOMS and unlinked trips, buses at/past ULB, the 2022 fleet and 2023–25 Comm & Info capex. MTA NYCT + MTA Bus together operate 5,979 active full-size buses (9.2% of the US fleet). Source: https://datahub.transportation.gov/d/ifzt-j53d (high confidence).

---

## 7. Agency universe, fuel mix, fleet age and opex pool (FY2025)

**Reporter types (2025 Reporter Agency Information, 2,850 distinct NTD IDs):** Full Reporters 520 (102,231 VOMS; 415 with active full-size buses; 79 with rail); Reduced Reporters 643 (7,776 VOMS; 239 with buses); Rural Reporters 1,162 (16,072 VOMS; 273 with buses; 1 with rail); Reduced Asset Reporters 428 (49 with buses); State Reporters 54; Group Plan Sponsors 26; Planning 8; Building 7; Separate Service 2. TAM tiers: Tier I (Rail) 78 agencies / 53,671 VOMS; Tier I (Fixed Route VOMS) 52 / 19,805; Tier I (Non-Fixed Route VOMS) 28 / 10,628; Tier II 2,691 / 41,975. Source: https://datahub.transportation.gov/d/jm7a-9hsy.

**Active full-size bus fuel mix:** diesel 34,936 (53.6%, 719 agencies); CNG 15,513 (23.8%, 182); hybrid diesel 8,735 (13.4%, 184); battery-electric 2,848 (4.4%, 238 agencies); gasoline 1,193 (1.8%); "other" 999 (1.5%, 3 agencies); trolleybus electric 535 (0.8%, 4); hydrogen 202 (0.3%, 18); propane 199 (0.3%). Source: https://datahub.transportation.gov/d/ifzt-j53d.

**Weighted average fleet age (years, 2025):** bus 8.33 (54,161 vehicles in the age table), articulated bus 8.48, over-the-road bus 8.11, double-deck 8.20, trolleybus 8.92, cutaway 5.71, van 5.04; heavy-rail car 22.26, light-rail vehicle 20.11, commuter coach 28.58, commuter self-propelled car 19.38, locomotive 25.96, automated guideway 40.66. Source: https://datahub.transportation.gov/d/6abt-uhgq. (Age table vehicle counts are totals incl. inactive and differ slightly from RVI active counts.)

**Operating expenses (US$ B):** 2022 53.7 (bus 26.8, rail 20.1, DR/VP 5.9, ferry 1.0); 2023 60.5; 2024 65.6; 2025 70.1 (bus 34.4, rail 26.5, DR/VP 7.9, ferry 1.3). "Services" object class: 5.0 (2022) → 6.9 (2025), 9.8% of opex; bus 3.24, rail 3.17. Sources: https://datahub.transportation.gov/d/dkxx-zjd6 ; https://datahub.transportation.gov/d/j5uj-anzx.

---

## 8. Implications for the sizing model (how to use these tables)

- **Installed base inputs (US):** 65,239 active full-size buses (73,112 fixed-route bus-mode vehicles incl. cutaways; 191,482 revenue vehicles of all kinds); 12,946 metro cars; 2,527 LRVs + 418 streetcars; 7,406 commuter-rail cars + 865 locomotives; 80 rail operators; 977 bus agencies (520 Full Reporters are the realistic ITS buyers). Fleet growth assumption for bus should be ~0% (2022–25 CAGR −0.2%).
- **Customer tiers for the bottom-up:** Tier 1 (1,000+ buses or large rail) = 10 bus agencies + ~10 rail operators; Tier 2 (250–999) = 46 bus agencies; Tier 3 (50–249) = 149; long tail (<50) = 772 agencies with 16% of buses. Rail: 8 operators with 1,000+ vehicles hold 65% of rail cars.
- **Spend anchors:** the Comm & Info capital category ($1.9–2.2B/yr; bus ~$0.37–0.41B, rail ~$1.5–1.8B) is an *upper bound on capital-funded ITS + IT* and a *lower bound on total ITS spend* because operating-funded SaaS/maintenance (inside $6.9B of "Services" opex) is excluded. Unit anchors: ~$5.7–5.9k per bus per year (capital, fleet-weighted), ~$63–70k per rail vehicle per year (capital, dominated by signaling/train control).
- **Replacement-wave signals:** bus rolling-stock capex $4.24B in 2025 (vs $2.43B in 2023) and 8.3-year average bus age imply ~5,000–6,000 bus deliveries a year, each of which carries new onboard ITS; rail car age (20–29 years) points to continued rolling-stock and resignalling programmes at the large operators.
- **Adjacent flags:** fare collection capex $521M (2025) and roadway traffic management are outside the core scope; demand-response software (DR mode, 8,705 capex rows, $23M Comm & Info capex) is a separate paratransit-scheduling niche.

---

## 9. Output file index

Raw downloads (untrusted data, fresh folder): `/home/user/Project-2-/its-market-case/data/ntd/` — 15 CSVs named `<table>__<socrata id>.csv` (see `ntd_download.sh` for the id list).

Derived CSVs in `/home/user/Project-2-/its-market-case/data/`:

| File | Content |
|---|---|
| `ntd_2025_bus_agency_tiers.csv` | Task (1): agencies and buses per tier under four fleet definitions (A–D) |
| `ntd_2022_2025_bus_agency_tiers_by_year.csv` | Task (1) trend: tiers per report year 2022–2025 |
| `ntd_2025_bus_fleet_by_agency.csv` | All 2,644 vehicle-reporting agencies with bus counts by sub-type, tier, ZEBs, age, VOMS, UPT, Comm&Info capex |
| `ntd_2025_bus_tier_comm_info_capex_intensity.csv` | Bus-mode Comm&Info capex and $/bus by tier |
| `ntd_2025_rail_vehicles_by_mode.csv` | Task (2): active/total rail vehicles and locomotives by mode |
| `ntd_2025_rail_vehicles_by_mode_and_type.csv` | Task (2): mode x vehicle type, with ADA counts and operator counts |
| `ntd_2025_top20_rail_operators.csv` | Task (2): top-20 rail operators with per-mode fleet |
| `ntd_2025_rail_fleet_by_operator_all.csv` | All 80 rail operators with per-mode fleet, locomotives, Comm&Info capex, size tier |
| `ntd_2025_rail_tier_comm_info_capex_intensity.csv` | Rail-mode Comm&Info capex and $/vehicle by operator size |
| `ntd_capex_by_year_mode_category.csv` | Task (3): long table year x mode x category (2022–2025) |
| `ntd_capex_by_year_modegroup_category.csv` | Task (3): wide table year x mode group x category |
| `ntd_capex_comm_info_by_mode_year.csv` | Comm&Info and total capex by individual mode, 2022–2025 |
| `ntd_2025_capex_existing_vs_expansion_by_modegroup.csv` | 2025 capex by use type (existing vs expansion vs reduced-reporter) |
| `ntd_2025_top100_agencies_comm_info_capex.csv` | Top-100 agencies by 2025 Comm&Info capex (bus/rail split, 2023–25 sum) |
| `ntd_capex_time_series_2015_2025_by_modegroup.csv` | Total / rolling stock / facilities / other capex by mode group, 2015–2025 |
| `ntd_2025_top50_bus_agencies.csv` | Task (4): top-50 bus agencies with full attribute set |
| `ntd_2025_agency_universe.csv` | Reporter-type counts, VOMS, bus/rail operator counts |
| `ntd_2025_agency_tam_tiers.csv` | FTA TAM tier counts |
| `ntd_2025_bus_fuel_mix.csv` | Active full-size buses by fuel type |
| `ntd_2022_2025_fleet_age_by_vehicle_type.csv` | Weighted average age by vehicle type and year |
| `ntd_2022_2025_opex_by_modegroup.csv` | Operating expenses, services and purchased transportation by mode group |

Scripts: `/home/user/Project-2-/its-market-case/model/scripts/ntd_download.sh`, `/home/user/Project-2-/its-market-case/model/scripts/ntd_tiering.py` (run: `python3 -I ntd_tiering.py <raw_dir> <out_dir>`).

---

## 10. Gaps and caveats

- **No web searches could be run** for this topic (the per-turn WebSearch budget was exhausted before this task started), and **transit.dot.gov and apta.com are blocked** (HTTP 403, including on retry). Consequently no APTA Fact Book or NTD "National Transit Summaries and Trends" cross-check was possible; all numbers come from the primary NTD tables on data.transportation.gov. The 2023 and 2024 raw Revenue Vehicle Inventory Excel files (transit.dot.gov only) were not obtained; the 2022–2025 trend relies on FTA's own multi-year vehicle-count table, which reconciles exactly to the 2025 RVI.
- "Communication & Information Systems" is an ITS *proxy*: it includes cab signaling/train control (large for rail) and general office IT, and excludes operating-funded software subscriptions and maintenance contracts. Capex is lumpy at agency level; use 3-year averages.
- NTD report year 2025 mixes agency fiscal years (most end 30 June 2025; MTA NYC ends 31 December). Dollars are nominal.
- Reduced and Rural reporters do not itemise capex (shown as "Reduced-reporter" column, $845M in 2025), so small-agency ITS capex is understated in the tiered intensity table.
- Multi-mode fleets in the RVI (e.g. "DR/DO, MB/DO") are assigned to a mode by vehicle type (bus tiering) or by first rail mode listed (rail); the choice affects <2% of vehicles.
- Canada is not covered by the NTD; see research file 04 for Canadian fleet figures.

## 11. Source list

- FTA NTD, 2025 NTD Annual Data – Revenue Vehicle Inventory (35,625 rows; updated 2026-10-05): https://datahub.transportation.gov/d/ifzt-j53d (API: https://data.transportation.gov/resource/ifzt-j53d.csv)
- FTA NTD, 2022–2025 NTD Annual Data – Vehicles (Type Count by Agency) (10,858 rows; updated 2026-10-14): https://datahub.transportation.gov/d/nimp-626k
- FTA NTD, 2022–2025 NTD Annual Data – Vehicles (Age Distribution): https://datahub.transportation.gov/d/6abt-uhgq
- FTA NTD, 2022–2025 NTD Annual Data – Capital Expenses (by Capital Use) (17,285 rows; updated 2026-10-14): https://datahub.transportation.gov/d/fphd-jyyj (column definitions: https://data.transportation.gov/api/views/fphd-jyyj.json)
- FTA NTD, 2025 NTD Annual Data – Capital Use (5,193 rows): https://datahub.transportation.gov/d/8rr7-fd8y
- FTA NTD, 2025 NTD Annual Data – Capital Expenditures (Time Series 3.1, 2015–2025; 155,408 rows): https://datahub.transportation.gov/d/8ffu-2anj
- FTA NTD, 2025 NTD Annual Data – Reporter Agency Information (2,897 rows): https://datahub.transportation.gov/d/jm7a-9hsy
- FTA NTD, 2024 NTD Annual Data – Reporter Agency Information (2,914 rows): https://datahub.transportation.gov/d/ccvf-fykn
- FTA NTD, 2025 NTD Annual Data – Operating Expenses: https://datahub.transportation.gov/d/4ucy-dac3
- FTA NTD, 2022–2025 NTD Annual Data – Operating Expenses (by Function): https://datahub.transportation.gov/d/dkxx-zjd6
- FTA NTD, 2022–2025 NTD Annual Data – Operating Expenses (by Type): https://datahub.transportation.gov/d/j5uj-anzx
- FTA NTD, 2025 NTD Annual Data – Service: https://datahub.transportation.gov/d/74ek-quhs
- FTA NTD, 2022–2025 NTD Annual Data – Service (by Mode and Time Period): https://datahub.transportation.gov/d/wwdp-t4re
- FTA NTD, 2022–2025 NTD Annual Data – Track & Roadway (by Mode): https://datahub.transportation.gov/d/fzbb-f6kc
- FTA NTD, 2025 Database File Dictionary: https://datahub.transportation.gov/d/eu97-reg7
- USDOT Socrata metadata catalog (used to find dataset ids): https://data.transportation.gov/api/views/metadata/v1
- Blocked (HTTP 403, first attempt and retry): https://www.transit.dot.gov/ntd/data-product/2023-annual-database-revenue-vehicle-inventory ; https://www.transit.dot.gov/ntd/data-product/2024-annual-database-revenue-vehicle-inventory ; https://www.apta.com/research-technical-resources/transit-statistics/public-transportation-fact-book/
