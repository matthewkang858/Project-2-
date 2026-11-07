# 04 — US and Canada bottom-up demand base for public transit ITS (agencies, fleets, spend)

**Research date:** 2026-11-07 | **Scope:** installed base and spend of US and Canadian public transit operators (bus/roadway and rail) that an ITS vendor sells into: number and size of agencies, revenue vehicles by mode, fleet composition and age, route/track/station counts, operating and capital spend (including the NTD "Communication & Information Systems" capital category), funding sources, ridership trends 2015–2025, zero-emission bus counts, and Canadian equivalents.

**Method and caveats.** The session's web-search budget was exhausted before this task started, and the session network policy blocks direct fetches of transit.dot.gov, apta.com and cutaactu.ca (ENOTFOUND / 403). All US figures below were therefore pulled directly from the **FTA National Transit Database (NTD) annual datasets as federated on the USDOT open-data portal (data.transportation.gov / datahub.transportation.gov, Socrata API)**, which the policy allows. The **2025 report year** (agency fiscal years ending in 2025, published Oct 2026) is the latest and is used as the base year; 2022–2024 are shown for trend. Row counts of every downloaded dataset were verified against the API's `count(*)` (all match). Canadian figures come from Statistics Canada tables (CSV downloads) and Transport Canada's *Transportation in Canada 2024*. Zero-emission bus counts come from CALSTART's *Zeroing in on ZEBs* March 2025 and March 2026 report PDFs (downloaded from calstart.org). **APTA Fact Book and CUTA Fact Book could not be opened** (hosts blocked); see Gaps. Nothing is estimated where a source was not seen; every number carries its dataset URL. Confidence: **high** = primary source (NTD/StatCan/CALSTART) or consistent across 2+ sources; **medium** = single secondary source or my own aggregation involving a scope choice; **low** = inferred / scope unclear.

Mode codes (NTD): MB motorbus, CB commuter bus, RB bus rapid transit, TB trolleybus, DR demand response, VP vanpool, HR heavy rail (metro/subway), LR light rail, SR streetcar, CR commuter rail, YR hybrid rail, MG monorail/automated guideway, FB ferry. "Bus" group = MB+CB+RB+TB; "Rail" group = HR+LR+SR+CR+YR+MG+CC+IP+AR+TR; "DR/VP" = DR+VP+DT+JT+PB.

---

## 1. Key takeaways

1. **The addressable US customer universe is ~2,700 NTD-reporting agencies, but the ITS-relevant core is ~520 urban Full Reporters** (agencies operating ≥30 vehicles or fixed-guideway/rail). In report year 2025 the NTD vehicle file lists 2,696 reporters: 520 Full, 620 Reduced (502 urban + 118 tribal), 1,112 Rural, 429 Reduced-Asset, 15 planning/building. Full Reporters hold **144,836 of 191,482 revenue vehicles (75.6%)** and **59,263 of 65,239 full-size buses (90.8%)**, and accounted for **$31.5B of the $32.3B of 2025 capital expenses and 100% of the $1.90B "Communication & Information Systems" capital spend** (Reduced/Rural reporters do not itemise capex).
2. **US revenue fleet (all NTD reporters, FY2025): 191,482 vehicles.** Bus-type: 53,033 standard buses + 6,010 articulated + 5,491 over-the-road + 170 double-deck + 535 trolleybuses = **65,239 full-size buses**, plus 40,218 cutaways, 18,649 vans, 15,318 minivans, 21,212 automobiles and 5,856 SUVs (mostly demand-response/vanpool). Rail: **12,946 heavy-rail cars, 2,884 LRVs, 3,715 commuter-rail coaches + 3,797 self-propelled cars + 923 locomotives, 109 AGT, 89 vintage trolleys.** The fleet is flat-to-slightly-up since 2022 (166,095 → 191,482, but the growth is almost entirely automobiles/SUVs/minivans in demand-response; full-size bus count moved 65,642 → 65,239).
3. **Bus demand is extremely concentrated: 10 agencies own 29% of full-size buses, the top 20 own 41%, the top 50 own 58%, the top 100 own 72%.** Only **56 agencies have ≥250 full-size buses** (10 with ≥1,000), 59 have 100–249, 90 have 50–99, and **773 agencies have fewer than 50** (16% of the fleet). By vehicles operated in maximum service (all modes), 20 agencies have ≥1,000 VOMS (43,770 VOMS = 35% of 126,079), 70 have 250–999, 88 have 100–249, 164 have 50–99 and 2,354 have <50. Rail is even more concentrated: **17 heavy-rail operators (NYCT alone 6,840 of 12,946 cars), 22–38 light-rail/streetcar operators, 27 commuter-rail operators.**
4. **The NTD's own ITS proxy — "Communication & Information Systems" capital expense — was $1.90B in FY2025 (avg $2.11B/yr 2022–2025), i.e. 5.9% of total transit capex ($32.3B).** NTD defines the category as "two-way radio systems..., cab signaling and train control equipment in rail systems, automatic vehicle locator systems, automated dispatching systems, vehicle guidance systems, telephones..., public address systems [and] computers... and associated software that support transit operations such as... scheduling, planning, vehicle maintenance...". Rail took **$1.50B (79%; HR $1.01B, CR $0.26B, LR $0.19B, SR $0.04B)** and bus **$0.37B (MB $370M; CB/RB/TB <$3M combined)**, demand-response $23M, ferry $11M. Bus ITS capex is therefore **~$5.8k per active full-size bus per year** (4-yr avg ~$6.0k) and rail **~$61k per active rail car (ex-locomotives) or ~$105k per track mile** per year (figures include signaling/train control). Only **328 of 2,221 capex-reporting agencies recorded any Communication & Information capex in 2025**, and the top 3 (NYCT $322M, WMATA $308M, BART $149M) were 41% of the total. Caveat: this is capital only; recurring SaaS/maintenance contracts sit in operating "services" ($6.9B across all modes in 2025, 9.8% of opex) and are not separately identifiable.
5. **Total spend pool: FY2025 operating expenses $70.1B (bus $34.4B, rail $26.5B, DR/VP $7.9B, ferry $1.3B), up 38% vs 2019; capital expenses $32.3B (rail $21.7B, bus $9.2B, DR/VP $1.0B), up 21% vs 2022.** Funds expended on capital were 39.5% federal ($12.8B), 22.4% state, 22.5% local, 6.6% agency-levied taxes and 9.1% directly generated; funds expended on operations ($75.1B incl. reconciling items) were only 13.5% federal, 23.8% fares/directly generated, 25.1% state, 29.4% local. Federal funds reported by agencies fell from **$31.3B (2022, pandemic relief routed via §5307) to $22.9B (2025: §5307 $11.2B, §5309 $5.6B, §5311 $1.0B, other federal $3.7B).**
6. **Ridership has recovered to 81.5% of 2019 (8.05B unlinked trips in FY2025 vs 9.88B in 2019; +5.0% y/y)**, bus to 84.2% (3.98B), rail to 78.7% (3.83B; heavy rail 79%, commuter rail 77%, light rail 77%), BRT to 115% (74.8M), demand response to 95%, commuter bus only 50%. Service supply has not fully returned either: VOMS 126,079 in 2025 vs 138,162 in 2019 (bus 51,388 vs 57,953; rail 17,336 vs 17,901), while bus vehicle revenue miles are back to 95% of 2019 (1.51B vs 1.60B). The implication for ITS is that agencies are buying productivity/real-time information tools against a smaller active fleet, with the installed base (191k vehicles) still larger than the operated peak.
7. **Fleet composition is still diesel-led but with a meaningful alt-fuel installed base: of 63,760 active full-size buses in bus modes, 53.7% diesel, 24.3% CNG, 13.7% diesel-hybrid, 4.4% battery-electric (2,795), 0.8% trolleybus (535), 0.3% hydrogen (202), 1.5% "other", 0.9% gasoline, 0.3% propane.** CALSTART counts **8,116 full-size ZEBs funded/ordered/delivered/deployed as of July 2025 (BEB 7,261, FCEB 855; +16% y/y; FCEB +49%)** plus **1,398 small ZEBs**, vs 7,028 full-size (6,453 BEB / 575 FCEB) and 1,165 small a year earlier; California holds 2,623 (32%), then New York 829, Washington 521, Florida 519, Illinois 230, Texas 218. The CALSTART pipeline equals 12.4% of the NTD full-size fleet but only ~3,000 ZEBs were active in NTD at FY2025, i.e. roughly 5,000 are still on order/in delivery — each a factory-fit opportunity for telematics, charge management and onboard ITS. CALSTART's March 2025 edition projected >15,000 full-size ZEBs by 2030 at the then-14% growth rate.
8. **Replacement cycle creates a predictable hardware refresh wave.** The standard bus fleet averages 8.3 years (NTD-reported), 25.6% of standard buses are ≥12 years old and **20.8% of active standard buses are at or beyond the agency's own useful-life benchmark** (ULB mix: 14 years 46%, 12 years 39%); 12,644 full-size buses were already past ULB at FY2025 and a further **24,143 reach ULB during 2026–2031 (3.5–5.0k per year)**. Rail: heavy-rail cars average 22.3 years (47% ≥25 years; 1,725 cars reach ULB 2026–2031 on top of a 1,044 backlog), commuter-rail coaches 28.6 years (86% ≥16 years), LRVs 20.1 years, streetcars 46 years. New vehicles are the main channel for factory-installed onboard ITS (CAD/AVL, APC, cameras, displays), so 2026–2031 bus deliveries of roughly 4–5k/yr are the volume base for onboard hardware; mid-life retrofits address the ~50k buses that will not be replaced in the period.
9. **The bus OEM channel is a duopoly: Gillig 35.3% and New Flyer/Flyer Industries 32.0% of active full-size buses, then Nova 7.8%, MCI 5.9%, NABI 4.6%, ElDorado 2.9%, Prevost 1.5%; in electric/hydrogen buses New Flyer 42%, Gillig 21%, Proterra 15%, BYD 13%.** Rail cars: Bombardier(Alstom) 3,931 + Alstom 1,962 + Kawasaki 3,513 of 12,946 heavy-rail cars; Siemens 1,293 and Kinki Sharyo 760 of 2,527 LRVs; Bombardier 2,794, Kawasaki 1,317, Sumitomo 667, Hyundai Rotem 432 of 8,208 commuter-rail cars; Stadler 78 of 92 hybrid-rail cars. OEM spec-sheets and "pre-wired" partnerships are therefore a decisive route to market for onboard hardware.
10. **Canada adds roughly one-eighth to the North American base: Statistics Canada's urban transit industry (NAICS 485110) operated 17,783 urban transit buses and 4,554 "other rolling stock" (22,411 vehicles) across 111 companies in 2024, with C$15.95B operating expenses, C$13.55B operating revenue, C$15.39B capital expenditure (C$1.47B rolling stock, C$13.92B other) and 75,742 employees.** Ridership was 1.59B trips in 2024 (84.2% of 2019's 1.89B; Transport Canada reports the same ratio) and 1.55B in 2025 (82.2%); revenue excluding subsidies C$4.02B in 2025 (97% of 2019). VIA Rail carried 4.4M passengers in 2024 (88% of 2019). Canadian ZEB counts and the CUTA fact book could not be retrieved (gap).

---

## 2. US agency universe (NTD reporters)

### 2.1 Reporter counts

| Reporter type (NTD) | FY2024 Reporter Agency Information file (2,914 rows) | FY2025 Vehicles table (2,696 agencies) | Notes |
|---|---|---|---|
| Full Reporter (Urban) | 524 | 520 | ≥30 VOMS or fixed-guideway; itemise capex, report all ITS-relevant data |
| Reduced Reporter (Urban) | 496 | 502 | <30 VOMS, no fixed guideway |
| Reduced Reporter (Tribe) | 132 | 118 | |
| Rural Reporter | 1,218 | 1,112 | §5311 subrecipients (reported via states) |
| State Reporter | 54 | n/a | states reporting on behalf of rural subrecipients |
| Reduced Asset Reporter | 444 | 429 | asset-only (TAM) reporters |
| Group Plan Sponsor | 26 | n/a | |
| Planning / Building / Separate Service | 20 | 15 | |
| Organization type (2024): local government unit 1,335; private non-profit 620; independent public authority 436; tribe 138; private for-profit 111; MPO/COG 80; area agency on aging 49; state DOT 36; university 24 | | | |

Sources: NTD 2024 Reporter Agency Information (https://datahub.transportation.gov/d/ccvf-fykn); NTD 2022–2025 Vehicles (Type Count by Agency) (https://datahub.transportation.gov/d/nimp-626k); NTD 2025 Time Series 2.2 agency table (https://datahub.transportation.gov/d/ectq-t3k3: 2,572 distinct agencies, of which 520 Full / 502 Reduced-urban / 118 Reduced-tribe / 1,108 Rural active with a 2025 report). Confidence high.

### 2.2 Agencies by mode operated (FY2025, from Revenue Vehicle Inventory / annual service file)

| Mode | Agencies with fleets (RVI 2025) | Agencies reporting annual service (2025) |
|---|---|---|
| Demand response (DR) | 2,331 | 1,942 |
| Motorbus (MB) | 1,183 | 1,155 |
| Commuter bus (CB) | 154 | 153 |
| Vanpool (VP) | 109 | 112 |
| Ferry (FB) | 41 | 41 |
| Commuter rail (CR) | 27 | 27 |
| Streetcar (SR) | 25 | 25 |
| Light rail (LR) | 22 | 22 |
| Bus rapid transit (RB) | 20 | 20 |
| Heavy rail (HR) | 17 | 16 |
| Hybrid rail (YR) | 6 | 6 |
| Monorail/AGT (MG) | 6 | 6 |
| Trolleybus (TB) | 4 | 4 |

Sources: NTD 2025 Revenue Vehicle Inventory (https://datahub.transportation.gov/d/ifzt-j53d); NTD 2022–2025 Service by Mode and Time Period, Annual Total rows (https://datahub.transportation.gov/d/wwdp-t4re). Confidence high.

### 2.3 Distribution of agencies by bus fleet size (FY2025, total revenue vehicles held)

Full-size buses = standard bus + articulated + over-the-road + double-deck + trolleybus (65,239 vehicles, 978 agencies with ≥1):

| Fleet-size bucket | Agencies | Full-size buses | Share of fleet |
|---|---|---|---|
| ≥1,000 | 10 | 19,145 | 29.3% |
| 250–999 | 46 | 20,411 | 31.3% |
| 100–249 | 59 | 8,940 | 13.7% |
| 50–99 | 90 | 6,202 | 9.5% |
| 10–49 | 380 | 9,030 | 13.8% |
| 1–9 | 393 | 1,511 | 2.3% |
| **Top 10 / 20 / 50 / 100 / 200 share** | | | **29.3% / 40.8% / 58.2% / 71.8% / 83.5%** |

All bus-type vehicles incl. cutaways, vans, minivans, school buses (139,486 vehicles, 2,591 agencies):

| Fleet-size bucket | Agencies | Vehicles | Share |
|---|---|---|---|
| ≥1,000 | 17 | 35,272 | 25.3% |
| 250–999 | 81 | 39,406 | 28.3% |
| 100–249 | 125 | 18,241 | 13.1% |
| 50–99 | 240 | 16,507 | 11.8% |
| 10–49 | 1,110 | 25,503 | 18.3% |
| 1–9 | 1,018 | 4,557 | 3.3% |
| **Top 10 / 20 / 50 / 100 share** | | | **18.6% / 27.4% / 42.0% / 53.9%** |

Agencies by vehicles operated in maximum service (all modes, FY2025): ≥1,000 VOMS 20 agencies (43,770 VOMS); 250–999: 70 (32,537); 100–249: 88 (13,155); 50–99: 164 (11,502); 10–49: 957 (20,669); <10: 1,397 (4,446). Total revenue vehicles (all modes): top 20 agencies 37.3%, top 50 51.3%, top 100 62.3% of 191,482.

**Top 20 US agencies by full-size bus fleet (FY2025 total fleet; all-bus-type incl. cutaways; total revenue vehicles all modes; agency VOMS):**

| # | Agency | State | Full-size buses | All bus-type | Total rev. vehicles | VOMS |
|---|---|---|---|---|---|---|
| 1 | MTA New York City Transit | NY | 4,583 | 5,651 | 12,491 | 10,226 |
| 2 | New Jersey Transit | NJ | 2,542 | 3,018 | 4,541 | 3,432 |
| 3 | Chicago Transit Authority | IL | 2,012 | 2,012 | 3,720 | 2,575 |
| 4 | LA Metro | CA | 1,999 | 3,103 | 3,680 | 2,747 |
| 5 | MTA Bus Company | NY | 1,396 | 1,396 | 1,396 | 1,179 |
| 6 | SEPTA | PA | 1,358 | 1,745 | 2,654 | 1,933 |
| 7 | WMATA | DC | 1,349 | 1,910 | 3,339 | 2,608 |
| 8 | MBTA | MA | 1,317 | 1,715 | 3,223 | 2,199 |
| 9 | Houston METRO | TX | 1,305 | 1,915 | 2,124 | 1,717 |
| 10 | King County Metro | WA | 1,284 | 2,919 | 2,996 | 2,417 |
| 11 | Maryland MTA | MD | 976 | 1,422 | 1,948 | 1,814 |
| 12 | Denver RTD | CO | 968 | 1,327 | 1,660 | 1,053 |
| 13 | SFMTA (Muni) | CA | 861 | 1,012 | 1,307 | 783 |
| 14 | Miami-Dade | FL | 791 | 1,096 | 1,631 | 1,342 |
| 15 | Pittsburgh Regional Transit | PA | 698 | 854 | 1,038 | 758 |
| 16 | TriMet | OR | 668 | 969 | 6,794 | 851 |
| 17 | Metro Transit (Minneapolis) | MN | 650 | 650 | 767 | 632 |
| 18 | Pace (Chicago suburbs) | IL | 646 | 1,829 | 3,030 | 972 |
| 19 | AC Transit | CA | 630 | 854 | 854 | 637 |
| 20 | San Diego MTS | CA | 603 | 757 | 1,101 | 769 |

(Next: DART 586, MARTA 535, Valley Metro/Phoenix 513, UTA 492, Honolulu 485, RTC S. Nevada 452, CapMetro 449, VTA 448, OCTA 446, VIA San Antonio 445.) Source: NTD 2022–2025 Vehicles (Type Count by Agency), FY2025 rows (https://datahub.transportation.gov/d/nimp-626k). Confidence high (my aggregation of primary data; Pace appears twice in the all-bus list because it files two NTD IDs).

---

## 3. US revenue vehicle fleet

### 3.1 Revenue vehicles by type, all NTD reporters (total fleet held at FY end)

| Vehicle type | 2022 | 2023 | 2024 | 2025 | Agencies with ≥1 (2025) |
|---|---|---|---|---|---|
| Bus (standard) | 53,038 | 53,070 | 52,470 | 53,033 | 951 |
| Articulated bus | 5,792 | 5,868 | 5,954 | 6,010 | 90 |
| Over-the-road bus | 6,028 | 5,946 | 5,630 | 5,491 | 113 |
| Double-deck bus | 221 | 210 | 164 | 170 | 9 |
| Trolleybus | 563 | 535 | 535 | 535 | 4 |
| **Full-size bus subtotal** | **65,642** | **65,629** | **64,753** | **65,239** | **978** |
| Cutaway | 39,302 | 38,965 | 39,560 | 40,218 | 2,111 |
| Van | 18,150 | 19,041 | 19,925 | 18,649 | 1,395 |
| Minivan | 12,144 | 13,039 | 14,572 | 15,318 | 1,321 |
| Automobile | 4,771 | 6,381 | 9,695 | 21,212 | 261 |
| SUV | 3,267 | 3,913 | 4,616 | 5,856 | 251 |
| School bus | 61 | 61 | 65 | 62 | 16 |
| Heavy rail passenger car | 11,452 | 12,038 | 12,315 | 12,946 | 17 |
| Light rail vehicle | 2,747 | 2,818 | 2,856 | 2,884 | 38 |
| Commuter rail passenger coach | 3,750 | 3,736 | 3,777 | 3,715 | 26 |
| Commuter rail self-propelled car | 3,281 | 3,343 | 3,666 | 3,797 | 16 |
| Locomotive | 899 | 899 | 929 | 923 | 24 |
| Automated guideway vehicle | 114 | 114 | 114 | 109 | 5 |
| Vintage/historic trolley | 72 | 72 | 79 | 89 | 11 |
| Aerial tram / monorail / cable car / inclined plane | 73 / 8 / 37 / 6 | 73 / 8 / 39 / 6 | 73 / 8 / 40 / 6 | 73 / 8 / 39 / 6 | 2 / 1 / 1 / 3 |
| Ferryboat | 273 | 267 | 269 | 281 | 41 |
| Other | 46 | 57 | 64 | 58 | 10 |
| **Total revenue vehicles** | **166,095** | **170,499** | **177,382** | **191,482** | 2,646 |
| Reporting agencies in file | 2,779 | 2,671 | 2,712 | 2,696 | |

By reporter type, FY2025 total revenue vehicles / full-size buses: Full 144,836 / 59,263; Reduced 20,163 / 2,347; Rural 22,447 / 2,799; Reduced Asset 3,947 / 284; Planning 89 / 11. NTD notes the "streetcar" vehicle-type column is unused (streetcar fleets are recorded as LRVs/vintage trolleys under mode SR). Source: https://datahub.transportation.gov/d/nimp-626k. Confidence high.

### 3.2 Active fleet by mode and vehicle type (FY2025 Revenue Vehicle Inventory; active = available for revenue service incl. spares)

| Primary mode | Vehicle type | Active | Total held |
|---|---|---|---|
| MB | Bus | 50,677 | 53,838 |
| MB | Articulated bus | 5,447 | 5,847 |
| MB | Over-the-road bus | 2,592 | 2,664 |
| MB | Cutaway / van / minivan / double-deck | 5,175 / 335 / 86 / 153 | 5,468 / 347 / 89 / 154 |
| CB | Over-the-road bus / bus / cutaway / articulated | 2,898 / 976 / 667 / 99 | 3,290 / 1,051 / 720 / 100 |
| RB | Articulated / bus | 464 / 72 | 469 / 80 |
| TB | Trolleybus | 535 | 535 |
| DR | Cutaway / automobile / van / minivan / SUV / bus | 34,376 / 21,203 / 13,292 / 10,315 / 2,686 / 1,308 | 36,899 / 21,396 / 13,996 / 11,013 / 2,717 / 1,376 |
| VP | Van / minivan / SUV | 4,988 / 4,911 / 3,151 | 5,977 / 5,956 / 4,451 |
| HR | Heavy rail car | 12,946 | 13,122 |
| LR | LRV (+9 vintage) | 2,518 | 2,648 |
| SR | LRV / vintage trolley | 338 / 80 | 352 / 90 |
| CR | Self-propelled car / coach / locomotive | 3,734 / 3,672 / 865 | 3,802 / 4,109 / 978 |
| YR | Self-propelled / LRV / coach | 63 / 28 / 1 | |
| MG / AR / TR / CC / IP | | 117 / 100 / 73 / 39 / 6 | |
| FB | Ferryboat | 281 | 298 |
| **Active vehicles by mode group** | Bus modes (MB+CB+RB+TB) 70,308; DR 83,254; VP 13,050; HR 12,946; CR 8,271; LR 2,527; SR 418; other rail 335; ferry 281 | | |

35,625 fleet records; 34,339 dedicated fleets; 56 records flagged "automated vehicles". Source: https://datahub.transportation.gov/d/ifzt-j53d. Confidence high.

### 3.3 Bus fleet composition by fuel (active full-size buses in bus modes, FY2025)

| Fuel type | Active full-size buses | Share |
|---|---|---|
| Diesel | 34,245 | 53.7% |
| Compressed natural gas | 15,482 | 24.3% |
| Hybrid diesel-electric | 8,735 | 13.7% |
| Battery electric | 2,795 | 4.4% |
| Electric propulsion (trolleybus) | 535 | 0.8% |
| Hydrogen fuel cell | 202 | 0.3% |
| Gasoline / hybrid gasoline | 621 | 1.0% |
| Propane | 190 | 0.3% |
| Other | 953 | 1.5% |
| **Total** | **63,760** | 100% |

All active vehicles in bus + DR + VP modes (166,612): gasoline 56.0% (light-duty DR/VP fleet), diesel 22.2%, CNG 10.4%, hybrid diesel 5.2%, battery electric 2.1% (3,504), propane 1.3%, hybrid gasoline 1.1%. Energy cross-check (FY2025 Fuel & Energy table, bus group): 300.8M gal diesel, 193.9M gal CNG, 15.7M gal biodiesel, 8.2M gal gasoline, 108.5M kWh battery-electric, 47.9M kWh trolley, 0.6M kg hydrogen. Sources: RVI (https://datahub.transportation.gov/d/ifzt-j53d); Fuel & Energy (https://datahub.transportation.gov/d/8ehq-7his). Confidence high.

**Zero-emission buses (CALSTART, US only, "funded, ordered, delivered or deployed"):**

| Metric | As of July 2024 (March 2025 report) | As of July 2025 (March 2026 report) | Growth |
|---|---|---|---|
| Full-size ZEBs (Class 7/8, ≥30 ft) | 7,028 | 8,116 | +16% (+1,088) |
| of which battery-electric | 6,453 | 7,261 | +13% |
| of which fuel-cell electric | 575 | 855 | +49% |
| Small ZEBs (public transit, private, airport, university) | 1,165 (BEB 1,156 / FCEB 9) | 1,398 (BEB 1,389 / FCEB 9) | +20% |
| Top states, full-size | CA 2,285; NY 779; FL 516; WA 356; MA 292 | CA 2,623 (1,933 BEB + 690 FCEB); NY 829; WA 521; FL 519; IL 230; TX 218 | |
| Other data points | 2023→2024 +14%; projection >15,000 full-size ZEBs by 2030 at 14% CAGR; ~60% of transit fleets have ≤10 ZEBs; FY2024 Low-No awards funded ~600 ZEBs = 48% of buses awarded | California ~one-third of all full-size ZEBs; agencies "moving from pilots to long-term strategies"; growth spreading to Southeast/Midwest | |

Sources: CALSTART, *Zeroing in on ZEBs* March 2025 (https://calstart.org/wp-content/uploads/2025/03/20250305-ZIO-ZEB-March-2025_Final.pdf) and March 2026 (https://calstart.org/wp-content/uploads/2026/03/ZIO-ZEB-March-2026.pdf); landing page https://calstart.org/zio-zebs/. Confidence high. Note the March 2026 PDF's state table prints a BEB grand total of "7,621", which is inconsistent with its own Table 1 (7,261) and with 7,261 + 855 = 8,116; 7,261 is used here. Reconciliation: NTD shows 2,997 active battery/hydrogen full-size buses at FY2025 vs CALSTART's 8,116 pipeline, i.e. ~5,100 ZEBs funded/ordered but not yet active (medium confidence on the differencing; the two sources differ in timing and definitions).

### 3.4 Fleet age and useful-life benchmarks (FY2025)

| Vehicle type | Vehicles (age file) | NTD-reported avg age (yrs) | 0–5 yrs | 6–11 yrs | 12–15 yrs | 16+ yrs | Dominant agency ULBs | Share of active at/over own ULB |
|---|---|---|---|---|---|---|---|---|
| Bus (standard) | 54,161 | 8.3 | 31.2% | 43.2% | 18.5% | 7.1% | 14y 46%, 12y 39%, 15y 7% | 20.8% |
| Articulated bus | 6,072 | 8.5 | 25.9% | 46.1% | 21.6% | 6.4% | 12y 48%, 14y 45% | 20.7% |
| Over-the-road bus | 5,230 | 8.1 | 32.0% | 48.8% | 10.9% | 8.3% | 14y 61%, 12y 19% | 15.9% |
| Trolleybus | 535 | 8.9 | 3.7% | 89.2% | 0% | 7.1% | 13y 52%, 18y 40% | 0% |
| Cutaway | 42,716 | 5.7 | 45.6% | 48.0% | 5.0% | 1.5% | 10y 59%, 5y 15%, 7y 10% | 25.6% |
| Van / minivan | 17,046 / 13,921 | 5.0 / 5.3 | 57.5% / 49.6% | 35.9% / 44.5% | 4.3% / 4.7% | 2.3% / 1.2% | 8y ~53% | 32.7% / 36.7% |
| Heavy rail car | 12,946 | 22.3 | 16.1% | 15.1% | 5.2% | 63.6% | 40y 40%, 30y 14%, 34y 13% | 9.9% |
| Light rail vehicle | 2,891 | 20.1 | 10.7% | 22.3% | 12.1% | 54.9% | 31y 47%, 30y 34%, 25y 12% | 16.2% |
| Commuter rail coach | 3,885 | 28.6 | 2.5% | 2.4% | 8.9% | 86.1% | 30y 34%, 25y 21%, 39y 18% | 21.7% |
| Commuter rail self-propelled | 3,790 | 19.4 | 8.3% | 18.1% | 24.2% | 49.4% | 35y 47%, 39y 23% | 17.4% |
| Commuter rail locomotive | 952 | 26.0 | 4.9% | 6.4% | 18.2% | 70.5% | 30y 33%, 25y 26% | 27.2% |
| Streetcar fleet (mode SR, ex-locos) | 418 active | 46.1 (wtd by manufacture year) | | | | 67% ≥25y | | |

Standard-bus age bands 2022→2025: share ≥12 years 23.6% → 23.8% → 24.3% → 25.6%; average 7.8 → 8.0 → 8.1 → 8.3 years (fleet is ageing slowly). Full-size bus active fleet by manufacture year (cumulative share): built ≤2013 25%, ≤2016 47%, ≤2019 69%, ≤2022 87.5%; 2023: 3,516; 2024: 2,876; 2025 (partial year): 937.

**Replacement wave — full-size buses (MB/CB/RB/TB) reaching their agency-reported ULB:** already past ULB at FY2025: 12,644; 2026: 3,458; 2027: 3,462; 2028: 4,090; 2029: 3,980; 2030: 4,156; 2031: 4,997 (2026–2031 total 24,143); 2032: 3,915; after 2032: 21,466. **Rail cars (ex-locomotives):** HR past ULB 1,044, reaching ULB 2026–31 1,725, later 7,812; CR 1,375 / 932 / 4,602; LR 317 / 475 / 1,735; SR 221 / 51 / 146; YR 0 / 10 / 82.

Sources: NTD 2022–2025 Vehicles (Age Distribution) (https://datahub.transportation.gov/d/6abt-uhgq); RVI 2025 (https://datahub.transportation.gov/d/ifzt-j53d). Confidence high for distributions; medium for "at/over ULB" (uses manufacture year, ignores rebuild year, excludes records with blank ULB).

### 3.5 OEM installed base (active vehicles, FY2025 RVI)

| Segment | Manufacturer shares |
|---|---|
| Full-size buses (63,760 active) | Gillig 35.3%; New Flyer of America 29.6% + Flyer Industries 2.4%; Nova Bus 7.8%; MCI 5.9%; NABI 4.6%; ElDorado National 2.9% (+EBC 0.3%); Prevost 1.5%; Orion 1.1%; Proterra 0.8%; BYD 0.7%; unspecified 4.7% |
| Electric/hydrogen full-size buses (3,539 active incl. trolleybus) | New Flyer 42.4%; Gillig 20.6%; Proterra 15.1%; BYD 12.5%; unspecified 5.0%; Nova 1.2%; others <1% each |
| Heavy rail cars (12,946) | Bombardier 3,931; Kawasaki 3,513; Alstom 1,962; Budd 505; Pullman-Standard 502; other 694 |
| Light rail vehicles (2,527) | Siemens 1,293; Kinki Sharyo 760; Breda 183; CAF 171; ABB 53; Bombardier 32 |
| Commuter rail cars ex-locos (8,208) | Bombardier 2,794; Kawasaki 1,317; Sumitomo 667; Budd 542; Hyundai Rotem 432; unspecified 504 |
| Hybrid rail (92) | Stadler 78; Siemens 8 |

Source: https://datahub.transportation.gov/d/ifzt-j53d. Confidence high (manufacturer names as reported; Bombardier is now Alstom).

---

## 4. Network, stations and service

### 4.1 Directional route miles, track miles, stations (FY2025)

| Mode | Directional route miles (TS 2.1) | Track miles | Grade crossings | Track under performance restriction (mi) | Stations (facility inventory, by type) |
|---|---|---|---|---|---|
| Motorbus (MB) | 196,210 | — | — | — | 428 at-grade + 229 platform + 149 elevated + 48 underground fixed-guideway stations (bus facilities) |
| Commuter bus (CB) | 21,878 | — | — | — | 38 |
| BRT (RB) | 458 (2019: 264) | — | — | — | 149 exclusive-platform + 109 platform + 35 at-grade = 293 |
| Trolleybus (TB) | 432 | — | — | — | |
| Heavy rail (HR) | 1,716 | 2,369 | 141 | 47 | 490 underground + 371 elevated + 222 at-grade = 1,083 |
| Light rail (LR) | 1,726 (2015: 1,469) | 1,883 | 1,430 | 244 | 559 at-grade + 206 platform + 152 exclusive platform + 107 elevated + 67 underground = 1,091 |
| Streetcar (SR) | 260 | 400 | 435 | 20 | 330 platform + 10 underground (+ at-grade) |
| Commuter rail (CR) | 8,190 | 8,718 | 3,860 | 93 | 947 at-grade + 166 platform + 137 exclusive + 128 elevated + 14 underground = 1,392 |
| Hybrid rail (YR) | 197 | 228 | 304 | 0 | 61 |
| Monorail/AGT (MG) | 31 | 36 | 0 | 1 | 51 elevated |
| Alaska RR (AR) | 960 (service file) | 574 | 124 | 7 | |
| Ferry (FB) | 1,248 | — | — | — | 238 terminals |
| **Rail total** | **13,093** | **14,208** | | | |

Note: TS 2.1 motorbus DRM shows an anomaly in 2023 (333,480) and 2024 (361,117) vs ~196–209k in all other years; treat 2025 (196,210) as representative. Sources: NTD 2025 Time Series 2.1 by mode (https://datahub.transportation.gov/d/npsm-38gk); Track & Roadway by Mode (https://datahub.transportation.gov/d/fzbb-f6kc); Stations & Facilities by Mode and Age (https://datahub.transportation.gov/d/wfz2-eft6); Service by Mode (https://datahub.transportation.gov/d/wwdp-t4re). Confidence high (station counts medium: facility rows list multiple modes and were attributed to the first mode listed).

Rail guideway age (FY2025 guideway age distribution, miles): at-grade ballast 10,412 mi of which 36% pre-1940s, 16% 1980s, 12% 1990s, 14% 2000s, 10% 2010s, 5% 2020s; bored/blasted tunnel 253 mi (11% pre-1940s, 19% 1980s, 22% 1990s); in-street embedded 1,128 mi (26% 2000s, 32% 2010s). Source: https://datahub.transportation.gov/d/j9q7-53ae. Confidence high.

### 4.2 Ridership (unlinked passenger trips, millions, all NTD reporters, TS 2.1)

| Mode | 2015 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2025 vs 2019 | 2025 vs 2024 |
|---|---|---|---|---|---|---|---|---|---|---|
| Motorbus (MB) | 5,025.9 | 4,489.5 | 3,157.4 | 2,266.3 | 2,806.8 | 3,314.1 | 3,657.2 | 3,792.5 | 84.5% | +3.7% |
| Commuter bus (CB) | 100.8 | 92.6 | 42.9 | 24.1 | 37.1 | 44.4 | 45.6 | 46.6 | 50.3% | +2.2% |
| BRT (RB) | 55.7 | 65.2 | 45.3 | 36.3 | 43.4 | 64.3 | 71.4 | 74.8 | 114.7% | +4.8% |
| Trolleybus (TB) | 89.7 | 76.2 | 54.6 | 29.7 | 44.7 | 52.4 | 63.0 | 64.4 | 84.5% | |
| **Bus group** | **5,272.2** | **4,723.5** | 3,300.2 | 2,356.5 | 2,932.0 | 3,475.2 | 3,837.3 | **3,978.3** | **84.2%** | +3.7% |
| Heavy rail (HR) | 3,860.1 | 3,790.4 | 1,777.9 | 1,607.2 | 2,261.1 | 2,597.4 | 2,824.4 | 3,002.7 | 79.2% | +6.3% |
| Light rail (LR) | 478.7 | 479.0 | 331.5 | 176.7 | 262.3 | 314.2 | 343.4 | 369.1 | 77.1% | +7.5% |
| Streetcar (SR) | 50.0 | 52.6 | 38.0 | 16.6 | 27.6 | 36.3 | 37.5 | 40.0 | 76.0% | |
| Commuter rail (CR) | 490.8 | 506.0 | 259.3 | 148.1 | 263.6 | 320.2 | 363.8 | 388.9 | 76.9% | +6.9% |
| Hybrid rail / MG | 7.5 / 24.0 | 8.9 / 15.7 | | | | | 5.9 / 12.8 | 5.9 / 12.9 | | |
| **Rail group** | **4,923.6** | **4,864.7** | 2,431.8 | 1,960.4 | 2,835.1 | 3,293.3 | 3,597.1 | **3,827.8** | **78.7%** | +6.4% |
| Demand response (DR) | 164.9 | 156.3 | 114.7 | 90.8 | 113.0 | 130.0 | 139.7 | 148.0 | 94.7% | |
| Vanpool (VP) | 38.0 | 35.3 | 24.9 | 16.3 | 19.5 | 22.5 | 23.6 | 24.2 | 68.6% | |
| Ferry (FB) | 71.4 | 85.6 | 57.9 | 40.1 | 55.9 | 64.5 | 69.5 | 72.5 | 84.7% | |
| **All modes** | **10,495.9** | **9,879.9** | 5,937.8 | 4,469.2 | 5,959.0 | 6,988.4 | 7,669.1 | **8,050.8** | **81.5%** | **+5.0%** |

Cross-check (monthly modal time series, urban full reporters only, calendar years): all modes 9,073M (2019) → 7,424M (2025) = 81.8%; bus 4,572 → 3,837; rail 4,271 → 3,394; Jan–Aug 2026 5,626M. Sources: https://datahub.transportation.gov/d/npsm-38gk; https://datahub.transportation.gov/d/5ti2-5uiv. Confidence high.

### 4.3 Service supply: vehicles operated in maximum service (VOMS) and vehicle revenue miles (VRM, millions)

| Mode | VOMS 2015 | VOMS 2019 | VOMS 2021 | VOMS 2023 | VOMS 2024 | VOMS 2025 | VRM 2019 | VRM 2025 |
|---|---|---|---|---|---|---|---|---|
| MB | 51,759 | 53,022 | 47,934 | 46,679 | 47,326 | 48,156 | 2,027.2 | 1,950.6 |
| CB | 4,167 | 4,183 | 2,717 | 2,747 | 2,648 | 2,547 | 145.8 | 97.6 |
| RB | 300 | 338 | 337 | 352 | 378 | 393 | 12.6 | 16.8 |
| TB | 391 | 410 | 366 | 298 | 308 | 292 | 9.8 | 8.7 |
| **Bus group** | **56,617** | **57,953** | 51,354 | 50,076 | 50,660 | **51,388** | 2,195.4 | 2,073.7 |
| DR | 44,774 | 46,778 | 39,225 | 42,116 | 44,449 | 45,716 | 1,198.5 | 1,163.9 |
| VP | 13,487 | 13,947 | 9,070 | 10,454 | 10,878 | 11,429 | 230.6 | 201.1 |
| HR | 9,428 | 9,601 | 9,484 | 9,032 | 9,263 | 9,117 | 698.3 | 704.5 |
| LR | 1,530 | 1,704 | 1,376 | 1,393 | 1,550 | 1,509 | 121.4 | 120.7 |
| SR | 212 | 258 | 224 | 213 | 213 | 221 | 6.9 | 6.0 |
| CR | 6,278 | 6,050 | 5,446 | 5,728 | 5,752 | 6,171 | 352.8 | 361.1 |
| **Rail group** | **17,783** | **17,901** | 16,744 | 16,676 | 17,095 | **17,336** | 1,185.6 | 1,198.5 |
| **All modes** | **134,599** | **138,162** | 117,037 | 119,834 | 123,518 | **126,079** | | |

Source: https://datahub.transportation.gov/d/npsm-38gk. Confidence high. (VOMS in the Service-by-Mode file sums to the same 48,156 for MB; the Vehicles table "agency_voms" sums to 126,079.)

---

## 5. Spend: operating expenses, capital expenses, funding

### 5.1 Operating expenses by mode ($ millions, all NTD reporters, TS 2.1)

| Mode | 2015 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 | 2025 vs 2019 |
|---|---|---|---|---|---|---|---|---|
| MB | 20,445 | 23,642 | 23,618 | 25,180 | 28,017 | 30,121 | 32,510 | +37.5% |
| CB / RB / TB | 1,067 / 137 / 262 | 1,180 / 219 / 288 | 902 / 268 / 293 | 996 / 276 / 313 | 1,049 / 317 / 312 | 1,119 / 354 / 353 | 1,125 / 406 / 355 | |
| **Bus group** | **21,912** | **25,328** | 25,080 | 26,765 | 29,696 | 31,947 | **34,395** | **+35.8%** |
| HR | 8,950 | 9,328 | 9,362 | 9,696 | 11,074 | 12,272 | 12,844 | +37.7% |
| LR | 1,833 | 2,463 | 2,379 | 2,582 | 2,936 | 3,392 | 3,608 | +46.5% |
| SR | 147 | 234 | 218 | 247 | 276 | 300 | 319 | |
| CR | 5,734 | 6,547 | 6,503 | 7,239 | 8,270 | 8,883 | 9,338 | +42.6% |
| YR / MG | 87 / 82 | 112 / 71 | 118 / 63 | 138 / 69 | 148 / 82 | 154 / 83 | 163 / 86 | |
| **Rail group** | **16,944** | **18,886** | 18,717 | 20,114 | 22,934 | 25,243 | **26,527** | **+40.5%** |
| DR / VP | 4,707 / 168 | 5,490 / 176 | 4,955 / 128 | 5,692 / 154 | 6,624 / 176 | 7,066 / 191 | 7,748 / 196 | |
| Ferry | 641 | 828 | 815 | 959 | 1,078 | 1,174 | 1,253 | |
| **All modes** | **44,409** | **50,734** | 49,706 | 53,696 | 60,517 | 65,628 | **70,119** | **+38.2%** |

FY2025 opex by function ($M): vehicle operations 31,574; vehicle maintenance 11,653; facility (non-vehicle) maintenance 8,516; general administration 15,051; reduced-reporter lump 3,325. Bus: 17,834 / 5,964 / 1,644 / 7,477 / 1,477; Rail: 9,328 / 4,901 / 6,617 / 5,675 / 6. FY2025 opex by object class ($M, all modes): operator wages 8,775; other salaries 13,401; fringe 13,856; **services 6,902 (bus 3,239; rail 3,172)**; fuel & lube 1,732; other materials 3,271; utilities 1,891; casualty & liability 2,510; **purchased transportation 10,243 (bus 4,061; rail 2,137; DR/VP 3,825)**; misc 807. Sources: https://datahub.transportation.gov/d/npsm-38gk; Operating Expenses by Function (https://datahub.transportation.gov/d/dkxx-zjd6); by Type (https://datahub.transportation.gov/d/j5uj-anzx). Confidence high.

Fare revenue (TS 2.1, $M): all modes 13,721 (2019) → 10,528 (2025); bus 4,438 → 3,019; rail 8,641 → 6,745. Confidence high.

### 5.2 Capital expenses by capital-use category ($ millions, all NTD reporters)

| Category | 2022 | 2023 | 2024 | 2025 | 2025 Bus | 2025 Rail | 2025 DR/VP | 2025 Ferry |
|---|---|---|---|---|---|---|---|---|
| Guideway | 10,811.6 | 11,055.6 | 10,304.3 | 10,945.0 | 857.9 | 10,087.0 | 0 | 0 |
| Passenger stations | 4,426.9 | 4,116.3 | 4,501.2 | 4,520.3 | 673.7 | 3,732.2 | 0 | 114.4 |
| Administrative buildings | 660.3 | 664.6 | 615.9 | 779.2 | 469.7 | 288.1 | 18.7 | 2.7 |
| Maintenance buildings | 1,861.0 | 2,206.4 | 2,358.2 | 2,697.7 | 1,653.7 | 963.3 | 56.3 | 24.3 |
| Revenue (passenger) vehicles | 4,958.0 | 5,153.5 | 7,171.8 | 8,803.9 | 4,237.5 | 3,765.8 | 545.0 | 255.5 |
| Service (other) vehicles | 236.5 | 300.0 | 344.9 | 652.8 | 126.6 | 520.9 | 3.6 | 1.6 |
| Fare collection equipment | 342.9 | 359.9 | 403.8 | 521.0 | 94.5 | 422.8 | 3.1 | 0.7 |
| **Communication & information systems** | **2,108.7** | **2,167.1** | **2,244.0** | **1,903.7** | **372.5** | **1,497.3** | **22.8** | **11.0** |
| Other (shelters, signs, furniture, equipment) | 971.2 | 752.5 | 562.5 | 678.3 | 269.6 | 405.5 | 3.1 | 0 |
| Reduced-reporter lump sum | 408.7 | 609.6 | 844.4 | 845.7 | 444.8 | 1.4 | 394.5 | 5.1 |
| **Total** | **26,785.7** | **27,385.5** | **29,351.1** | **32,347.5** | **9,200.6** | **21,684.4** | **1,047.1** | **415.3** |

Bus-group totals by year: 5,337 / 6,013 / 7,438 / 9,201 (comm & info 353.5 / 405.1 / 386.3 / 372.5). Rail-group totals: 20,774 / 20,524 / 20,598 / 21,684 (comm & info 1,735.0 / 1,739.3 / 1,829.8 / 1,497.3). Form split: F-20 existing-service rehabilitation/replacement vs expansion is reported separately (not aggregated here).

**Communication & Information Systems capex by mode, 2025 ($M) and 2022–2025 cumulative:** HR 1,007.8 (4,277.0); MB 370.0 (1,496.8); CR 259.4 (1,113.0); LR 186.3 (1,256.2); SR 35.0 (112.4); DR 22.8 (71.1); FB 11.0 (31.8); AR 4.9; YR 2.6; RB 1.5 (10.7); MG 1.4; CB 0.9 (9.6); TB 0.1; VP 0.1. **Top agencies 2025 ($M):** NYCT 322.3; WMATA 308.3; BART 149.4; LIRR 82.8; SEPTA 82.1; Maryland MTA 78.7; LA Metro 66.8; Valley Metro Rail 53.7; MBTA 51.8; Sound Transit 44.7; MARTA 37.3; NJ Transit 35.1; UTA 29.5; DART 28.9; King County Metro 24.4; CTA 24.1; Metra 22.1; Metro-North 21.1; Honolulu 20.6; TriMet 18.6; OCTA 18.3; KC Streetcar 17.1; Houston METRO 16.0; CapMetro 14.3; PATH 14.1. 328 of 2,221 agencies with capex rows reported any amount; all $1,903.6M came from Full Reporters.

**NTD definition of the category (verbatim from the dataset dictionary):** "Systems for exchanging information including two-way radio systems for communications between dispatchers and vehicle operators, cab signaling and train control equipment in rail systems, automatic vehicle locator systems, automated dispatching systems, vehicle guidance systems, telephones, facsimile machines and public address systems. Systems for processing data, including computers, monitors, printers, scanners, data storage devices, and associated software that support transit operations such as general office, accounting, scheduling, planning, vehicle maintenance, non-vehicle maintenance..." Guideway explicitly "does not include... communication systems (e.g., cab signaling and train control)". Fare collection equipment (incl. "automated fare boxes and related software") is a separate category — so the NTD category is a close match to the case's ITS scope **including** rail signaling/train control and back-office IT, **excluding** fare collection.

Derived intensities (my calculation, medium confidence): bus comm & info capex ≈ $5,842 per active full-size bus (2025) / ≈ $5,950 (4-yr avg); rail ≈ $60.8k per active rail car ex-locomotives (2025) / ≈ $69.1k (4-yr avg), ≈ $105k per track mile; HR ≈ $77.8k per car, LR ≈ $73.7k, CR ≈ $31.4k. Comm & info = 4.0% of bus capex, 6.9% of rail capex, 5.9% of all capex. Sources: Capital Expenses by Capital Use (https://datahub.transportation.gov/d/fphd-jyyj; API https://data.transportation.gov/resource/fphd-jyyj.csv; column definitions from https://data.transportation.gov/api/views/fphd-jyyj.json). Confidence high for the numbers; note the category is capital-only (operating-funded software subscriptions and maintenance contracts are excluded) and includes IT hardware/software beyond ITS (office, accounting).

### 5.3 Funding sources — funds expended ($ billions)

| Year | Expense type | Fares & other directly generated | Taxes/fees levied by agency | Local | State | Federal | Total |
|---|---|---|---|---|---|---|---|
| 2022 | Capital | 1.03 | 3.00 | 6.43 | 7.09 | 9.22 | 26.77 |
| 2022 | Operations | 11.57 | 3.35 | 11.07 | 9.42 | 22.05 | 57.45 |
| 2023 | Capital | 1.07 | 2.45 | 6.72 | 6.88 | 10.25 | 27.38 |
| 2023 | Operations | 15.70 | 4.29 | 16.88 | 17.82 | 10.27 | 64.96 |
| 2024 | Capital | 2.30 | 2.46 | 7.64 | 5.61 | 11.34 | 29.35 |
| 2024 | Operations | 16.87 | 5.58 | 18.33 | 18.10 | 12.16 | 71.05 |
| **2025** | **Capital** | 2.93 | 2.12 | 7.29 | 7.24 | **12.78 (39.5%)** | **32.35** |
| **2025** | **Operations** | 17.87 (23.8%) | 6.18 | 22.05 | 18.86 | **10.14 (13.5%)** | **75.09** |

Federal funds by program as reported by agencies ($B): 2022 §5307 urbanized formula 23.76, §5309 capital 5.13, §5311 rural 1.05, other FTA 0.48, other DOT 0.27, other federal 0.61, total 31.30; 2023: 13.00 / 5.09 / 1.08 / 0.42 / 0.25 / 0.69 / 20.54; 2024: 13.62 / 4.83 / 1.00 / 0.56 / 0.66 / 2.84 / 23.51; **2025: 11.23 / 5.59 / 0.99 / 0.51 / 0.92 / 3.68 / 22.91.** (The 2022 §5307 spike is COVID relief flowing through the formula program.) Sources: Funding Sources by Expense Type (https://datahub.transportation.gov/d/4tmr-gwuu); Funding Sources (Federal) (https://datahub.transportation.gov/d/qpjk-b3zw). Confidence high.

---

## 6. Canada

| Metric | 2019 | 2022 | 2023 | 2024 | 2025 | Source |
|---|---|---|---|---|---|---|
| Urban transit systems (NAICS 485110): number of companies | 96 | 101 | 102 | 111 | | StatCan 23-10-0081 |
| Urban transit buses operated | 17,291 | 17,087 | 17,397 | 17,783 | | StatCan 23-10-0086 |
| Other rolling stock (rail cars etc.) | 3,802 | 4,032 | 3,952 | 4,554 | | StatCan 23-10-0086 |
| Total vehicles, urban transit systems | 21,212 | 21,179 | 21,405 | 22,411 | | StatCan 23-10-0086 |
| Urban transit buses, all bus industries incl. non-bus industries | 20,527 | 20,894 | 21,624 | 22,786 | | StatCan 23-10-0086 |
| Total operating revenue (C$M) | 10,929 | 12,366 | 13,252 | 13,555 | | StatCan 23-10-0081 |
| Operating funding / subsidies (C$M) | 4,172 | 8,501 | 8,672 | 8,658 | | StatCan 23-10-0081 |
| Capital funding (C$M) | n/a | n/a | 10,666 | 12,891 | | StatCan 23-10-0081 |
| Total operating expenses (C$M) | 12,178 | 13,978 | 15,064 | 15,954 | | StatCan 23-10-0081 |
| of which human resources / vehicle energy / vehicle maintenance / other / depreciation (C$M, 2024) | | | | 8,211 / 886 / 1,273 / 2,571 / 3,014 | | StatCan 23-10-0081 |
| Total capital expenditures (C$M) | 9,047 | 10,569 | 12,437 | 15,389 | | StatCan 23-10-0082 |
| of which purchase of buses & rolling stock / other capex (C$M) | 2,369 / 6,678 | 993 / 9,577 | 1,474 / 10,962 | 1,473 / 13,916 | | StatCan 23-10-0082 |
| Employees (total / drivers / mechanics) | | 67,566 / 33,075 / 5,457 | 71,650 / 35,170 / 5,822 | 75,742 / 36,824 / 6,438 | | StatCan 23-10-0083 |
| Passenger trips, urban transit (millions, sum of monthly) | 1,888.7 | 1,161.3 | 1,461.6 | 1,590.4 | 1,552.6 | StatCan 23-10-0251 |
| Revenue excl. subsidies (C$M, sum of monthly) | 4,146.9 | 2,769.9 | 3,526.1 | 3,872.2 | 4,022.9 | StatCan 23-10-0251 |
| Ridership vs 2019 | 100% | 61.5% | 77.4% | 84.2% | 82.2% | derived |
| VIA Rail passengers | | | ~4.1M | 4.4M (+7%; 88% of 2019) | | Transport Canada 2024 |

Transport Canada (Transportation in Canada 2024): "Canadians took roughly 1.6 billion trips on public transit [in 2024] — an increase from 1.5 billion in 2023 and representing 84.2% of pre-pandemic levels... In December 2024, revenues rose by 25.5% over the same month in 2023." Sources: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310008601 (equipment), ...pid=2310008101 (financial performance), ...pid=2310008201 (capital expenditures), ...pid=2310008301 (employment), ...pid=2310025101 (monthly revenue and trips); https://tc.canada.ca/en/corporate-services/transparency/corporate-management-reporting/transportation-canada-annual-reports/transportation-canada-2024/modal-overviews. Confidence high for StatCan values (note "urban transit systems" NAICS 485110 includes rail operations of integrated agencies; "other rolling stock" is not broken out by rail mode; 2025 monthly series sums Jan–Dec 2025). Jan–Aug 2026 trips: 1,000.9M.

---

## 7. How to use this in the bottom-up model (analyst notes)

- **Installed base inputs (US, FY2025):** full-size buses 65,239 (active 63,760; VOMS bus group 51,388); cutaways/vans/minivans in DR ~58k + VP ~13k (light-duty telematics only); heavy rail 12,946 cars / 1,716 DRM / 2,369 track mi / ~1,083 stations; light rail + streetcar 2,884 LRV + 89 vintage / 1,986 DRM / 2,283 track mi / ~1,400 stations; commuter + hybrid rail 7,512 cars + 923 locomotives / 8,387 DRM / 8,946 track mi / ~1,450 stations; BRT 393 VOMS / 458 DRM / ~290 stations. Canada: 17,783 urban buses + 4,554 other rolling stock.
- **Customer-count inputs:** 520 Full Reporters; 56 agencies with ≥250 full-size buses (sweet spot for enterprise CAD/AVL, APC, video); 149 with 50–249; 773 with <50 (SaaS/light-touch); 17 HR, 22 LR, 25 SR, 27 CR operators.
- **Spend anchors:** NTD comm & info capex $1.90B (2025; $2.11B 4-yr avg) = capital ITS/IT incl. train control; bus share $0.37B, rail $1.50B. Add operating-funded software/services (not separable; "services" object class $6.9B total). Revenue-vehicle capex $8.8B (2025) sets the factory-fit channel; 24,143 full-size buses reach ULB 2026–2031.
- **Growth context:** ridership +5% y/y and 81.5% of 2019; opex +38% since 2019; federal share of ops back to 13.5% (from 38% in 2022); capital federal share ~40%.

---

## 8. Findings table

| Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| NTD reporting agencies in Vehicles table | 2,696 (520 Full, 620 Reduced, 1,112 Rural, 429 Reduced Asset, 15 other) | agencies | FY2025 | US | All | FTA NTD Vehicles (Type Count by Agency) | https://datahub.transportation.gov/d/nimp-626k | high | Reduced = 502 urban + 118 tribal |
| NTD Reporter Agency Information rows | 2,914 (524 Full, 496 Reduced urban, 132 Reduced tribe, 1,218 Rural, 54 State, 444 Reduced Asset, 26 Group Plan Sponsor) | agencies | FY2024 | US | All | FTA NTD Reporter Agency Information | https://datahub.transportation.gov/d/ccvf-fykn | high | organization types listed in §2.1 |
| Total revenue vehicles, all reporters | 191,482 | vehicles | FY2025 | US | All | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | 166,095 in 2022 |
| Full-size buses (bus+artic+OTR+DD+trolley) | 65,239 | vehicles | FY2025 | US | Roadway | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | 53,033 standard; 6,010 artic; 5,491 OTR; 170 DD; 535 TB |
| Cutaways / vans / minivans / automobiles / SUVs | 40,218 / 18,649 / 15,318 / 21,212 / 5,856 | vehicles | FY2025 | US | Roadway (DR/VP mostly) | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | automobiles jumped from 9,695 in 2024 |
| Heavy rail passenger cars | 12,946 (17 agencies; NYCT 6,840) | vehicles | FY2025 | US | Railway | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | |
| Light rail vehicles | 2,884 (38 agencies incl. SR) | vehicles | FY2025 | US | Railway | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | 2,518 active in LR mode + 338 in SR |
| Commuter rail coaches / self-propelled / locomotives | 3,715 / 3,797 / 923 | vehicles | FY2025 | US | Railway | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | 27 CR agencies |
| Full Reporters' share of revenue vehicles / full-size buses | 75.6% / 90.8% | % | FY2025 | US | All | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | 144,836 / 59,263 |
| Agencies with ≥1,000 / 250–999 / 100–249 / 50–99 / 10–49 / 1–9 full-size buses | 10 / 46 / 59 / 90 / 380 / 393 | agencies | FY2025 | US | Roadway | FTA NTD Vehicles (my aggregation) | https://datahub.transportation.gov/d/nimp-626k | high | fleet shares 29.3/31.3/13.7/9.5/13.8/2.3% |
| Top 10 / 20 / 50 / 100 agencies' share of full-size buses | 29.3% / 40.8% / 58.2% / 71.8% | % | FY2025 | US | Roadway | FTA NTD Vehicles (my aggregation) | https://datahub.transportation.gov/d/nimp-626k | high | |
| Top 20 / 50 share of all revenue vehicles | 37.3% / 51.3% | % | FY2025 | US | All | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | |
| Agencies with ≥1,000 VOMS | 20 (43,770 VOMS of 126,079) | agencies | FY2025 | US | All | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | |
| Largest bus fleet | MTA NYCT 4,583 full-size buses (12,491 revenue vehicles) | vehicles | FY2025 | US | Roadway | FTA NTD Vehicles | https://datahub.transportation.gov/d/nimp-626k | high | |
| Active full-size buses by fuel | diesel 53.7%, CNG 24.3%, hybrid 13.7%, BEB 4.4% (2,795), trolley 0.8%, H2 0.3% (202) | % of 63,760 | FY2025 | US | Roadway | FTA NTD Revenue Vehicle Inventory | https://datahub.transportation.gov/d/ifzt-j53d | high | bus modes MB/CB/RB/TB |
| Full-size ZEBs funded/ordered/delivered/deployed | 8,116 (BEB 7,261; FCEB 855); +16% y/y | buses | Jul 2025 | US | Roadway | CALSTART Zeroing in on ZEBs, March 2026 | https://calstart.org/wp-content/uploads/2026/03/ZIO-ZEB-March-2026.pdf | high | small ZEBs 1,398 |
| Full-size ZEBs prior year | 7,028 (BEB 6,453; FCEB 575); +14%; >15,000 projected by 2030 | buses | Jul 2024 | US | Roadway | CALSTART Zeroing in on ZEBs, March 2025 | https://calstart.org/wp-content/uploads/2025/03/20250305-ZIO-ZEB-March-2025_Final.pdf | high | CA 2,285; NY 779; FL 516; WA 356; MA 292 |
| ZEBs by state | CA 2,623; NY 829; WA 521; FL 519; IL 230; TX 218 | buses | Jul 2025 | US | Roadway | CALSTART March 2026 | https://calstart.org/wp-content/uploads/2026/03/ZIO-ZEB-March-2026.pdf | high | |
| Standard bus average age / share ≥12 yrs / share at or over own ULB | 8.3 yrs / 25.6% / 20.8% | yrs, % | FY2025 | US | Roadway | FTA NTD Vehicles (Age Distribution); RVI | https://datahub.transportation.gov/d/6abt-uhgq | high/medium | ULB mix 14y 46%, 12y 39% |
| Full-size buses reaching ULB 2026–2031 | 24,143 (3,458 / 3,462 / 4,090 / 3,980 / 4,156 / 4,997) plus 12,644 already past ULB | buses | 2026–2031 | US | Roadway | FTA NTD RVI (my calculation) | https://datahub.transportation.gov/d/ifzt-j53d | medium | manufacture year + reported ULB |
| Heavy rail car average age / share ≥16 yrs | 22.3 yrs / 63.6% | yrs, % | FY2025 | US | Railway | FTA NTD Age Distribution | https://datahub.transportation.gov/d/6abt-uhgq | high | CR coach 28.6; LRV 20.1; CR MU 19.4 |
| Bus OEM share of active full-size buses | Gillig 35.3%; New Flyer 32.0%; Nova 7.8%; MCI 5.9%; NABI 4.6% | % | FY2025 | US | Roadway | FTA NTD RVI | https://datahub.transportation.gov/d/ifzt-j53d | high | electric: New Flyer 42%, Gillig 21%, Proterra 15%, BYD 13% |
| Rail track miles | HR 2,369; LR 1,883; SR 400; CR 8,718; YR 228; MG 36; AR 574 (total 14,208) | miles | FY2025 | US | Railway | FTA NTD Track & Roadway | https://datahub.transportation.gov/d/fzbb-f6kc | high | grade crossings CR 3,860, LR 1,430 |
| Directional route miles | MB 196,210; CB 21,878; RB 458; HR 1,716; LR 1,726; SR 260; CR 8,190 | miles | FY2025 | US | All | FTA NTD TS 2.1 | https://datahub.transportation.gov/d/npsm-38gk | high | MB 2023–24 values anomalous |
| Rail stations | HR ~1,083; LR ~1,091; CR ~1,392; BRT ~293 | facilities | FY2025 | US | Railway/BRT | FTA NTD Stations & Facilities | https://datahub.transportation.gov/d/wfz2-eft6 | medium | attributed to first mode listed |
| Unlinked passenger trips, all modes | 8,050.8M (81.5% of 2019's 9,879.9M; +5.0% y/y) | trips | FY2025 | US | All | FTA NTD TS 2.1 | https://datahub.transportation.gov/d/npsm-38gk | high | |
| Bus group / rail group ridership vs 2019 | 3,978M (84.2%) / 3,828M (78.7%) | trips | FY2025 | US | Roadway / Railway | FTA NTD TS 2.1 | https://datahub.transportation.gov/d/npsm-38gk | high | HR 79.2%, CR 76.9%, LR 77.1%, RB 114.7% |
| Calendar-year ridership, urban full reporters | 7,424M (2025) vs 9,073M (2019); Jan–Aug 2026 5,626M | trips | 2019–2026 | US | All | FTA NTD Monthly Modal Time Series | https://datahub.transportation.gov/d/5ti2-5uiv | high | |
| VOMS all modes / bus / rail | 126,079 / 51,388 / 17,336 (2019: 138,162 / 57,953 / 17,901) | vehicles | FY2025 | US | All | FTA NTD TS 2.1 | https://datahub.transportation.gov/d/npsm-38gk | high | |
| Operating expenses, all modes | $70.1B (bus $34.4B; rail $26.5B; DR/VP $7.9B; ferry $1.3B); +38% vs 2019 | USD | FY2025 | US | All | FTA NTD TS 2.1 / Opex by Function | https://datahub.transportation.gov/d/npsm-38gk | high | |
| Opex "services" and "purchased transportation" | $6.9B / $10.2B | USD | FY2025 | US | All | FTA NTD Opex by Type | https://datahub.transportation.gov/d/j5uj-anzx | high | bus services $3.24B, rail $3.17B |
| Capital expenses, all reporters | $32.35B (rail $21.68B; bus $9.20B; DR/VP $1.05B; ferry $0.42B) | USD | FY2025 | US | All | FTA NTD Capital Expenses by Capital Use | https://datahub.transportation.gov/d/fphd-jyyj | high | 2022 $26.79B |
| Communication & Information Systems capex | $1,903.7M (rail $1,497.3M; bus $372.5M; DR $22.8M; ferry $11.0M); 2022–25 avg $2,105.9M | USD | FY2025 | US | All | FTA NTD Capital Expenses by Capital Use | https://datahub.transportation.gov/d/fphd-jyyj | high | NTD definition incl. radio, CAD/AVL, cab signaling & train control, PA, ops software |
| Comm & info capex by rail mode | HR $1,007.8M; CR $259.4M; LR $186.3M; SR $35.0M | USD | FY2025 | US | Railway | FTA NTD Capital Expenses by Capital Use | https://datahub.transportation.gov/d/fphd-jyyj | high | |
| Comm & info capex by bus mode | MB $370.0M; RB $1.5M; CB $0.9M; TB $0.1M | USD | FY2025 | US | Roadway | FTA NTD Capital Expenses by Capital Use | https://datahub.transportation.gov/d/fphd-jyyj | high | |
| Top comm & info spenders | NYCT $322M; WMATA $308M; BART $149M; LIRR $83M; SEPTA $82M; MD MTA $79M; LA Metro $67M | USD | FY2025 | US | All | FTA NTD Capital Expenses by Capital Use | https://datahub.transportation.gov/d/fphd-jyyj | high | 328 of 2,221 agencies reported any |
| Comm & info capex intensity | ≈$5.8k per active full-size bus; ≈$61k per rail car; ≈$105k per track mile | USD/yr | FY2025 | US | Roadway / Railway | derived from NTD | https://datahub.transportation.gov/d/fphd-jyyj | medium | includes signaling and back-office IT |
| Revenue vehicle capex | $8.80B (bus $4.24B; rail $3.77B) | USD | FY2025 | US | All | FTA NTD Capital Expenses by Capital Use | https://datahub.transportation.gov/d/fphd-jyyj | high | 2022 $4.96B |
| Fare collection equipment capex | $521M (rail $423M; bus $95M) | USD | FY2025 | US | All (adjacent) | FTA NTD Capital Expenses by Capital Use | https://datahub.transportation.gov/d/fphd-jyyj | high | adjacent scope |
| Funds expended on capital by source | federal $12.78B (39.5%), state $7.24B, local $7.29B, agency taxes $2.12B, directly generated $2.93B; total $32.35B | USD | FY2025 | US | All | FTA NTD Funding Sources by Expense Type | https://datahub.transportation.gov/d/4tmr-gwuu | high | |
| Funds expended on operations by source | federal $10.14B (13.5%), state $18.86B, local $22.05B, agency taxes $6.18B, fares/directly generated $17.87B; total $75.09B | USD | FY2025 | US | All | FTA NTD Funding Sources by Expense Type | https://datahub.transportation.gov/d/4tmr-gwuu | high | federal was $22.05B in 2022 |
| Federal funds by program | §5307 $11.23B; §5309 $5.59B; §5311 $0.99B; other FTA $0.51B; other DOT $0.92B; other federal $3.68B; total $22.91B (2022: $31.30B) | USD | FY2025 | US | All | FTA NTD Funding Sources (Federal) | https://datahub.transportation.gov/d/qpjk-b3zw | high | |
| Canada urban transit buses / other rolling stock / total vehicles | 17,783 / 4,554 / 22,411 | vehicles | 2024 | Canada | All | Statistics Canada Table 23-10-0086-01 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310008601 | high | 2019: 17,291 / 3,802 / 21,212 |
| Canada urban transit companies / opex / operating revenue | 111 / C$15.95B / C$13.55B | n, CAD | 2024 | Canada | All | Statistics Canada Table 23-10-0081-01 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310008101 | high | operating funding C$8.66B; capital funding C$12.89B |
| Canada urban transit capital expenditures | C$15.39B (rolling stock C$1.47B; other C$13.92B) | CAD | 2024 | Canada | All | Statistics Canada Table 23-10-0082-01 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310008201 | high | 2019 C$9.05B |
| Canada urban transit employees | 75,742 (36,824 drivers; 6,438 mechanics) | employees | 2024 | Canada | All | Statistics Canada Table 23-10-0083-01 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310008301 | high | |
| Canada urban transit ridership | 1,590M (2024; 84.2% of 2019); 1,553M (2025; 82.2%) | trips | 2024–2025 | Canada | All | Statistics Canada Table 23-10-0251-01; Transport Canada | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310025101 | high | revenue excl. subsidies C$4.02B 2025 |
| VIA Rail passengers | 4.4M (+7% y/y; 88% of 2019) | passengers | 2024 | Canada | Railway (intercity) | Transport Canada, Transportation in Canada 2024 | https://tc.canada.ca/en/corporate-services/transparency/corporate-management-reporting/transportation-canada-annual-reports/transportation-canada-2024/modal-overviews | high | |

---

## 9. Gaps (not obtained)

1. **APTA Public Transportation Fact Book (2024/2025 editions)** — apta.com blocked; APTA fleet/ridership/capital figures could not be cross-checked. NTD primary data used instead (APTA's Fact Book is itself NTD-derived; APTA's 8.1B 2025 ridership figure cited in research file 06 is consistent with NTD's 8.05B FY2025).
2. **CUTA Canadian Transit Fact Book** (agency-level Canadian fleets, ridership, spend by mode) — cutaactu.ca blocked; StatCan industry aggregates used instead. Canadian rail vehicle counts by mode (subway/LRT/commuter) are not separable from StatCan's "other rolling stock".
3. **Canadian zero-emission bus counts** (CUTA/ZETF) — housing-infrastructure.canada.ca failed TLS via the proxy; CALSTART covers the US only.
4. **NTD National Transit Summaries & Trends (NTST) 2023/2024 PDF** — transit.dot.gov blocked; headline counts above are reproduced from the underlying datasets instead.
5. **FTA default useful-life benchmarks and NTD Policy Manual text** — not fetched; ULB figures use agency-reported ULBs from the RVI.
6. **Operating-funded ITS spend** (SaaS subscriptions, maintenance contracts) is not identifiable in NTD; only the capital category is.
7. **Agency-level APC/CAD-AVL/camera penetration** — NTD does not collect it (only a "event data recorders" flag with sparse reporting and an "automated vehicles" flag on 56 fleet records).
8. Metro Magazine "Top 100 Fleets" cross-check not performed (not needed; NTD agency-level counts are primary).

---

## 10. Source list

- FTA National Transit Database, 2022–2025 NTD Annual Data — Vehicles (Type Count by Agency): https://datahub.transportation.gov/d/nimp-626k (API: https://data.transportation.gov/resource/nimp-626k.csv)
- FTA NTD, 2022–2025 Vehicles (Age Distribution): https://datahub.transportation.gov/d/6abt-uhgq
- FTA NTD, 2025 Revenue Vehicle Inventory: https://datahub.transportation.gov/d/ifzt-j53d
- FTA NTD, 2022–2025 Capital Expenses (by Capital Use): https://datahub.transportation.gov/d/fphd-jyyj (column definitions: https://data.transportation.gov/api/views/fphd-jyyj.json)
- FTA NTD, 2022–2025 Funding Sources (by Expense Type): https://datahub.transportation.gov/d/4tmr-gwuu
- FTA NTD, 2022–2025 Funding Sources (Federal): https://datahub.transportation.gov/d/qpjk-b3zw
- FTA NTD, 2022–2025 Operating Expenses (by Function): https://datahub.transportation.gov/d/dkxx-zjd6
- FTA NTD, 2022–2025 Operating Expenses (by Type): https://datahub.transportation.gov/d/j5uj-anzx
- FTA NTD, 2022–2025 Track & Roadway (by Mode): https://datahub.transportation.gov/d/fzbb-f6kc
- FTA NTD, 2022–2025 Track & Roadway (Guideway Age Distribution): https://datahub.transportation.gov/d/j9q7-53ae
- FTA NTD, 2022–2025 Stations and Facilities (by Mode and Age): https://datahub.transportation.gov/d/wfz2-eft6
- FTA NTD, 2022–2025 Service (by Mode and Time Period): https://datahub.transportation.gov/d/wwdp-t4re
- FTA NTD, 2022–2025 Fuel and Energy: https://datahub.transportation.gov/d/8ehq-7his
- FTA NTD, 2025 Service Data and Operating Expenses by Mode (Time Series 2.1): https://datahub.transportation.gov/d/npsm-38gk
- FTA NTD, 2025 Service Data and Operating Expenses by Agency (Time Series 2.2): https://datahub.transportation.gov/d/ectq-t3k3
- FTA NTD, 2024 Reporter Agency Information: https://datahub.transportation.gov/d/ccvf-fykn
- FTA NTD, Monthly Modal Time Series: https://datahub.transportation.gov/d/5ti2-5uiv
- USDOT open-data catalog listing of NTD datasets: https://data.transportation.gov/api/catalog/v1?q=National%20Transit%20Database
- CALSTART, Zeroing in on Zero-Emission Buses, March 2026 edition (data as of July 2025): https://calstart.org/wp-content/uploads/2026/03/ZIO-ZEB-March-2026.pdf
- CALSTART, Zeroing in on Zero-Emission Buses, March 2025 edition (data as of July 2024): https://calstart.org/wp-content/uploads/2025/03/20250305-ZIO-ZEB-March-2025_Final.pdf
- CALSTART ZIO-ZEB landing page: https://calstart.org/zio-zebs/
- Statistics Canada, Table 23-10-0086-01 Canadian passenger bus and urban transit industries, equipment operated: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310008601
- Statistics Canada, Table 23-10-0081-01 Financial performance of the passenger bus and urban transit industries: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310008101
- Statistics Canada, Table 23-10-0082-01 Capital expenditures: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310008201
- Statistics Canada, Table 23-10-0083-01 Employment and compensation: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310008301
- Statistics Canada, Table 23-10-0251-01 Passenger bus and urban transit statistics, monthly: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310025101
- Transport Canada, Transportation in Canada 2024 — Modal overviews: https://tc.canada.ca/en/corporate-services/transparency/corporate-management-reporting/transportation-canada-annual-reports/transportation-canada-2024/modal-overviews

Working files (scratch, not deliverables): downloaded CSV/PDF sources and analysis scripts are in /tmp/claude-0/-home-user-Project-2-/993f4a78-282b-5e57-93b8-c5cadbfd3ba8/scratchpad/ntdfleet/ (raw/ and scripts/).
