# 21 - Gap fill: scope-matched 2025 rail CCS (control-command-signalling) carve-out matrix

**Prepared:** 2026-11-07 (research sub-agent, gap-fill pass on the rail block of the sizing model).
**Purpose:** Replace the unsourced passenger/freight, urban/mainline, regional and hardware/software/services splits that files 03 and 15 flag as the weakest link, with a documented proxy chain that starts from two primary anchors (UNIFE WRMS rail control, SCI Verkehr CCS) and ends in a 2025 passenger-rail CCS matrix (segment x component x geography) in EUR and USD with a tested 2025-31 CAGR range.
**Scope reminder:** Public ITS = software, hardware and services sold to public transit operators/agencies. RAILWAY = metro/subway, light rail/tram, commuter/regional and mainline passenger rail. Freight rail is adjacent: every CCS total used here (UNIFE, SCI, GMI, SkyQuest, IMARC) INCLUDES freight and is carved out explicitly below. Fare collection and road traffic management are out of scope and not touched by this file.

**Method and network notes**
- The session's shared WebSearch budget was exhausted before this task started (every search call returned the "limit reached" message), so no web searches were run. All evidence below comes from direct fetches (curl / WebFetch) of primary documents whose URLs were known or discoverable from the UNIFE/SCI/EC/UITP sites, plus the sibling research files. Blocked hosts: railroads.dot.gov (ENOTFOUND - FRA PTC pages could not be read; FRA figures are taken from sibling file 03 and Wikipedia), railwaypro.com, bts.gov, fortunebusinessinsights.com, alliedmarketresearch.com, databridgemarketresearch.com (403). Mordor Intelligence railway-signalling, Technavio and Precedence pages either 404 or returned JavaScript shells / generic listings with no numbers (gap). marketresearchfuture.com returned an unrelated report under the guessed ID.
- Every figure carries the URL that was actually read. Confidence: high = primary source or 2+ independent sources agree; medium = single secondary source; low = inferred / analyst assumption. Every analyst assumption is listed in the **Assumption register** (section H) with its evidence trail and a range for the model.
- FX: all USD conversions use the ECB 2025 annual average reference rate **USD 1.1300 per EUR** (2024: 1.0824; 2023: 1.0813) - https://data-api.ecb.europa.eu/service/data/EXR/A.USD.EUR.SP00.A?format=csvdata&startPeriod=2023 (high).

---

## 1. Key takeaways

1. **New primary anchor: UNIFE WRMS 2026 (11th edition, Bain) puts world "rail control" at EUR 24.9bn per year (average 2023-2025), up from EUR 22.3bn (2021-23), EUR 16.8bn (2017-19) and EUR 15.1bn (2015-17).** That is 11.3% of the EUR 220.6bn total rail supply market and an implied +5.7% p.a. real growth 2021-23 to 2023-25 (vs +4.6% for the whole market); UNIFE's abstract says "rail control recorded the strongest growth" in Western Europe. Source: 2026 abstract PDF (high). The sizing model should move its rail-CCS base from EUR 22.3bn to EUR 24.9bn (2025 real terms) and keep SCI's ~EUR 20bn (2025) as the low case.
2. **The two anchors differ in scope, not in substance.** SCI Verkehr's CCS studies count OE plus after-sales but - per the 2019 methodology extract - "only take into consideration stationary / track-side systems"; UNIFE's rail-control segment covers trackside and onboard rail control but books maintenance in its separate EUR 84.1bn services segment. A full "hardware + software + services, trackside + onboard" scope therefore sits at EUR 24-30bn; EUR 24.9bn is used as the all-in base and flagged as such (medium).
3. **No vendor publishes a passenger/freight split, so one is built from traffic and network data.** Europe: EU-27 train-km are 83% passenger / 17% goods (Eurostat 2025: 3,124.6m vs 632.6m thousand train-km) and 81/18 in the EC Statistical Pocketbook 2025 (2023); UK 94/6, Switzerland 89/11, Norway 84/16, Turkey 53/47, Germany 78/22, Poland 70/28. China: HSR (>50,000 km, passenger-dedicated CTCS-3) and metro (8,788 km, 43% of world metro km) drive CCS; 2019 traffic was 1,471bn pkm vs 3,018bn tkm. North America: PTC covers ~57,500-59,000 route-miles, of which Amtrak-owned track is ~623-730 miles and commuter rail ~8,718 track-miles (NTD), i.e. passenger is <10% of PTC mileage but ~45% of CCS spend because of urban CBTC (NYC alone USD 5.4bn 2025-29). Japan: rail carries 0.84% of goods movement (passenger-dominant). India: 13,198 passenger vs 11,724 freight trains per day. Russia/CIS: freight-dominant.
4. **Reconciled 2025 matrix (base, EUR 24.9bn all-in CCS incl. freight): passenger rail CCS = EUR 18.5bn (USD 20.9bn), i.e. 74% of CCS; freight = EUR 6.4bn (26%).** Passenger splits into urban (metro + LRT) EUR 5.6bn (22% of CCS) and mainline/commuter passenger EUR 12.9bn (52%). By region (passenger CCS, EUR bn): Europe 9.5; China 4.2; APAC ex-China 2.1; North America 1.5; CIS/Eurasia 0.4; RoW 0.8. Low case (SCI EUR 20bn base): passenger EUR 14.8bn (USD 16.8bn).
5. **Component split (passenger CCS, base): hardware EUR 8.4bn (46%), software EUR 4.5bn (24%), services EUR 5.5bn (30%).** Anchors: GMI railway signalling "solutions 76% / services 24%" (2024, services growing >10% vs 8.5%); Alstom Services 24% of sales and 38% of backlog; Siemens Mobility Customer Services 17% of revenue; SCI metro after-sales 52-56% of 2026-30 vehicle volume; CBTC awards carry 25-year maintenance tails at ~10% of capex (file 12). The HW/SW split inside "solutions" is an analyst assumption (urban CBTC more software-heavy than mainline ETCS trackside).
6. **Regional split of CCS (freight-inclusive) used: Europe 46%, China 21%, APAC ex-China 11%, North America 13%, CIS/Eurasia 4%, RoW 5%.** Evidence: SCI 2026 "Europe almost half of ~EUR 20bn", "China >65% of Asia", Europe ahead of China; SCI world market 2024-26 Europe 34% / Asia 32% / North America 13% / CIS 12.5%; SCI 2019 CRSC 23% global share on a purely domestic base; GMI 2024 Europe 37% / APAC 23% / North America ~27% (US USD 4.2bn) / LatAm 8% / MEA 6%. GMI's higher North America and lower Asia weights are shown as a sensitivity (North America EUR 6.7bn vs EUR 3.2bn base).
7. **Urban (metro + LRT) CCS is ~EUR 5.5-6.5bn globally, cross-checked three ways:** (a) km x unit-cost bottom-up on UITP's 20,453 metro km and 15,812 LRT km with file-12 unit costs = EUR 5.6bn; (b) GMI's CBTC market USD 4.91bn in 2025 (= EUR 4.3bn; metros 82%, commuter 14%, high-speed 4%; North America USD 639m) plus non-CBTC urban scope; (c) US NTD rail "communication & information" capex USD 1.50bn (heavy rail 1.01, commuter 0.26, light rail 0.19) for 2025.
8. **Growth: a 2025-31 passenger-CCS CAGR of 4.0% (low) / 5.5% (base) / 7.0% (high) nominal is consistent with every benchmark that can be sourced:** UNIFE accessible rail control ~3.2% p.a. real (2021-23 to 2027-29, via Alstom URD) and total market 3.2% real to 2029-31; UNIFE's own realised rail-control growth 5.7% p.a. (2021-23 to 2023-25); SCI CCS 4.6% (2023-28); R&M 6.05% (2025-31, sibling file 03); IMARC 5.9% (2025-34); GMI CBTC 6.8%; M&M railway management 6.5%; Mordor TCMS 7.5%; SkyQuest 7.9%; GMI signalling 8.9% (outlier). Passenger CCS should outgrow freight CCS: SCI (Sept 2026) says freight-related rail segments are "under severe pressure worldwide" while passenger and urban rail drive growth and Europe is the fastest-growing CCS region. Base EUR 18.5bn becomes EUR 23.4bn (4%), 25.5bn (5.5%) or 27.7bn (7%) in 2031 (USD 26.4bn / 28.8bn / 31.3bn at 1.13).
9. **Modernisation, not expansion, is the European demand engine:** SCI's 2026 chart shows ~90% of Europe's 2025 CCS volume is modernisation/maintenance of the existing network vs ~10% new infrastructure; China is ~40/60. Germany alone spent EUR 2.0bn on command-and-control technology in 2025 (EUR 1.3bn in 2024), 13% of DB's existing-network capex (sibling file 14) - roughly one-sixth of Europe's modelled EUR 11.5bn CCS market.
10. **Vendor revenue triangulation supports the EUR 22-26bn all-in anchor:** Siemens Mobility Rail Infrastructure ~EUR 4.1bn (incl. electrification), Alstom Signalling EUR 2.7bn (ex-services), Hitachi Rail signalling & systems ~EUR 4.4bn, CRSC ~EUR 4-4.5bn (domestic), Wabtec Digital Intelligence ~EUR 0.9bn, plus CASCO, Nippon Signal/Kyosan, KB Signaling, MERMEC (~EUR 0.43bn), Stadler/CAF signalling and a long tail (sibling file 09).

---

## 2. Section A - Anchors and their exact scope

### A1. UNIFE World Rail Market Study rail-control series (primary, all freight-inclusive, trackside + onboard, excluding maintenance services)

| Edition | Period | Total market EUR bn p.a. | Rail control EUR bn p.a. | Rail control share | Other segments (EUR bn) | Source URL | Confidence |
|---|---|---|---|---|---|---|---|
| 5th (2014) | 2011-13 (approx.) | ~150 | n/a (chart only) | - | - | https://www.unife.org/wp-content/uploads/2021/03/WORLD-RAIL-MARKET-STUDY-EXECUTIVE-SUMMARY.pdf | medium |
| 7th (2018, Roland Berger) | 2015-17 | 163.2 | 15.1 | 9.3% | services 63.8; rolling stock 52.6; infrastructure 31.2; turnkey 0.6; forecast EUR 192bn (2021-23) | https://www.unife.org/wp-content/uploads/2021/03/World-rail-market-sturdy.pdf | high |
| 8th (2020, Roland Berger) | 2017-19 | 177.2 | 16.8 | 9.5% | services 65.0; rolling stock 61.9; infrastructure 32.6; turnkey 1.0; forecast +2.3% to ~EUR 204bn (2025, V-case) | https://www.unife.org/wp-content/uploads/2021/04/Forecast-2020-to-2025.pdf | high |
| 9th (2022, Roland Berger) | 2019-21 | 176.5 | not published free; services + rolling stock + infrastructure = "approximately 89%" -> rail control + turnkey ~11% -> ~EUR 18-19bn (derived) | ~10-11% | forecast 3.0% p.a. to EUR 211bn (2025-27); APAC infra + rail control +1.6%, W. Europe +4.1% | https://www.unife.org/news/global-rail-supply-industry-resurgent-despite-crises/ | low (derived) |
| 10th (2024, Bain) | 2021-23 (2023 real values) | 201.8 | 22.3 | 11.1% | services 77.1; rolling stock 63.3; infrastructure 38.1; turnkey 1.1; forecast +3.0% real to EUR 240.8bn (2027-29) | https://www.unife.org/wp-content/uploads/2024/07/Abstract_UNIFE_World_Rail_Market_Study.pdf | high |
| **11th (2026, Bain)** | **2023-25** | **220.6** | **24.9** | **11.3%** | services 84.1; rolling stock 68.8; infrastructure 41.7; turnkey 1.2; +4.6% p.a. real 2021-23 to 2023-25; forecast +3.2% real to EUR 266.8bn (2029-31); accessible market ~EUR 124bn = 56%; "rail control recorded the strongest growth" (Western Europe) | https://www.unife.org/wp-content/uploads/2026/07/UNIFE-Rail-Market-Study-2026-Abstract.pdf | high |

Derived (my arithmetic): rail control growth 15.1 -> 16.8 = +5.5% p.a. (2015-17 to 2017-19); 16.8 -> 22.3 = +7.3% p.a. (to 2021-23, nominal/real mix across editions); 22.3 -> 24.9 = **+5.7% p.a. real** (2021-23 to 2023-25, both in the 2026 edition's real terms because UNIFE states the 4.6% total growth "excluding inflation"). Accessible rail control (Alstom URD reproduction of WRMS 2024, sibling file 15): EUR 15.7bn (2021-23) -> 19.0bn (2027-29) = +3.2% p.a.; accessible = 70% of total rail control.

UNIFE definition (2026 abstract): "full rail supply value chain, including infrastructure, rail control (control command and signalling), rolling stock, services, and turnkey management"; 66 focus countries = ~99% of global rail supply demand; non-focus countries extrapolated on passenger-km, tonne-km and transportation units. The 2026 edition sells "Forecast Control Command and Signalling" as a separate EUR 780 data module (regional breakdowns inside) - the regional CCS volumes therefore exist but are paywalled (gap).

### A2. SCI Verkehr CCS studies (primary press material)

| Item | Value | Scope / notes | Source URL | Confidence |
|---|---|---|---|---|
| Global CCS market volume 2025 | ~EUR 20bn | "Sales of CCS in Europe account for almost half of the global market volume of approximately EUR 20 billion"; digital train control, train protection and signalling | https://www.sci.de/fileadmin/user_upload/pressemitteilungen/2026/PM_SCI_CCS_EN.pdf | high |
| Europe share | "almost half" (~45-48%) | Europe largest region, ahead of China; fastest-growing region to 2030 | same | high |
| Europe volume split | ~90% modernisation/maintenance of existing network, ~10% new infrastructure | chart "Market volume CCS 2025"; China ~40% / ~60% | same | medium (chart read) |
| China share of Asia | >65% | growth from HSR and metro expansion "at a slower pace than in the past decade"; 5G-based train communication | same | high |
| Train control systems share | 40% of global CCS | "most important product group globally" | same | high |
| Metro / commuter | "dynamic"; "very high costs contribute significantly to the market volume" | qualitative | same | high |
| Growth pattern | new development/modernisation grows faster than renewal/maintenance in all regions except Asia | qualitative | same | high |
| 2019 study scope | "This study only takes into consideration stationary / track-side systems" | i.e. onboard excluded; data annex shows "Market size OE/AS per product segment / per transport mode" and "Regional share of new development market" | https://sci.de/fileadmin/user_upload/MC_Studien_Flyer/Flyer_MC_CCS_2019_de.pdf | high |
| 2018 world market, new development & upgrade | ~EUR 8,750m | product shares: electronic interlocking ~40%, ETCS/CTCS/CBTC ~25%, conventional train control ~15%, other ~15%, operational telematics ~5% (chart; text confirms 40% and 15%) | same | medium |
| 2018 Western Europe CCS total (OE + after-sales) | EUR 6,582m p.a., +3.0% CAGR 2018-23 | HSR new development 390m, HSR maintenance/renewal 193m, metro maintenance/renewal 170m; CR new +2.9%, metro new +2.8%, LRT maintenance +2.1%; "market volume for maintenance and renewal makes up a major share"; ETCS ~10% of W. Europe new development | same | high |
| 2018 operational telematics / train communication | EUR 850m global; new development ~EUR 370m: Asia 45%, Western Europe 30%, North America 10%, Africa/ME, Eastern Europe, other ~5% each; suppliers CRSC 35%, then Kapsch, Huawei, Nokia, others | OEM telematics +5.5% p.a. | same | medium |
| 2018 Western Europe supplier shares (new development 2014-18) | Siemens ~40% (PR: ">35%"), then Thales, Alstom, Bombardier, Hitachi | | same; https://www.sci.de/en/data-trends/document/etcs-technology-close-to-a-breakthrough-regarding-comprehensive-utilisation-the-european-market-for | high |
| CRSC global share 2018 | 23% (<5% international) | largest supplier globally on domestic base | SCI 2019 PR (same URL) | high |
| ETCS market growth | almost +5% p.a. 2018-23 | DB planned EUR 570m to 2023; ~EUR 1bn/yr needed; DK ~EUR 700m, NO ~EUR 800m, BE ~EUR 500m programmes | SCI 2019 PR | high (dated) |
| Earlier SCI CCS base | EUR 19.3bn (2023), +4.6% p.a. 2023-28 | sibling file 03 (railmarket.com blocked) | https://railmarket.com/news/technology-innovation/16494-unveiling-the-future-sci-verkehr-s-insights-into-rail-control-and-signaling-market-trends | medium (not re-read) |
| SCI world rail market 2024-26 by region | Europe EUR 77.7bn (4.4% CAGR 2025-30); Asia 73.9 (3.0%); North America 29.9 (4.2%); CIS 28.5 (2.9%); Africa/ME 9.0 (6.1%); S/C America 4.5 (5.2%); Australia 4.5 (4.5%); world >EUR 275bn by 2030 at 3.9% | "impetus for growth comes primarily from rail passenger transport"; "rail freight transport and the related product segments are under severe pressure worldwide"; digitalisation boost "particularly evident in systems technology" | https://www.sci.de/fileadmin/user_upload/pressemitteilungen/2026/PM_MC_Weltmarkt_EN.pdf | high |
| SCI metro vehicles 2026 | EUR 17.6bn (2025) -> 22.9bn (2030), 5.4%; after-sales 52% of Europe and 56% of North America 2026-30 volume; ~850 vehicles in explicitly automated projects + ~550 linked to CBTC/signalling scope 2025-30 | adjacent (vehicles) | https://www.sci.de/fileadmin/user_upload/pressemitteilungen/2026/PM_SCI_Metro_EN.pdf | high |

### A3. Scope reconciliation (why EUR 20bn and EUR 24.9bn are both right)

| Scope element | UNIFE rail control (EUR 24.9bn) | SCI CCS (~EUR 20bn) | Vendor "railway signalling" reports |
|---|---|---|---|
| Trackside equipment (interlockings, train control, telecoms, detection) | yes | yes | yes |
| Onboard CCS (ETCS/CBTC/PTC onboard units) | yes (ERTMS "trackside and onboard" named as growth area) | excluded in 2019 methodology; 2026 scope not stated (flag) | usually yes |
| Installation / engineering / project management | yes (capex) | yes (OE) | inside "solutions" |
| Maintenance / after-sales services | no - sits in UNIFE "services" EUR 84.1bn | yes (after-sales) | "services" 24% (GMI) |
| Freight rail | yes | yes | yes |
| Rolling-stock TCMS (train control & management) | no (rolling stock) | no | separate (Mordor USD 4.5bn) |

Analyst conclusion (medium): the all-in "HW + SW + services, trackside + onboard" market is EUR 24-30bn; EUR 24.9bn is used as the base and EUR 20bn as the low case. Vendor top-cluster USD 18-24bn converts to EUR 16-21bn at 1.13 (2025), i.e. between the two anchors.

---

## 3. Section B - Regional split of freight-inclusive CCS

| Evidence | Europe | China | APAC ex-China | North America | CIS / Eurasia | RoW (LatAm, MEA, Africa, Australia) | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| SCI CCS 2026 | "almost half" | >65% of Asia; smaller than Europe | <35% of Asia | n/a | n/a | n/a | SCI CCS 2026 PR | high (qualitative) |
| SCI world rail supply 2024-26 (all segments) | 34% (77.7/228) | within Asia 32% | within Asia | 13% | 12.5% | 8% (Africa/ME 4%, S/C America 2%, Australia 2%) | SCI world 2026 PR | high |
| SCI CCS 2019 (2018) | W. Europe EUR 6.6bn of a global market that was then ~EUR 17-18bn (derived) = ~37-39%; telematics new-build W. Europe 30% | Asia "biggest regional market"; CRSC 23% global (domestic) -> China >=23% | telematics Asia 45% total | telematics 10% | n/a | ~15% | SCI 2019 flyer + PR | medium |
| GMI railway signalling 2024 (USD 18.2bn) | 37% | within APAC 23% (fastest, ~11% CAGR) | within APAC | ~26-27% (US USD 4.2bn = 85% of North America) | n/a | LatAm 8%, MEA 6% | https://www.gminsights.com/pressrelease/railway-signaling-system-market | medium |
| GMI CBTC 2025 (USD 4.91bn) | n/a | CRSC 25.1% share (largest) | n/a | USD 639m (13%); US 540m | n/a | n/a | https://www.gminsights.com/industry-analysis/communication-based-train-control-market | medium |
| UNIFE accessible market 2021-23 (all segments, EUR 119.2bn) | Europe ex-CIS 59.9 (50%) | not accessible | within Asia/Pacific 18.9 (16%) | within Americas 33.4 (28%) | within Africa/ME/CIS 7 | | Alstom URD via sibling file 15 | medium |
| UITP metro km 2023 (urban proxy) | 2,834 km (14%) | 8,788 km (43%) | 4,169 km (20%) | 1,618 km (8%) | 1,270 km (6%) | 1,774 km (9%) | UITP Global Metro Figures 2024 | high |
| **Chosen 2025 split (analyst)** | **46%** | **21%** | **11%** | **13%** | **4%** | **5%** | assumption A1 | low-medium |

Rationale: SCI is the only source that sizes CCS regionally from a project database and is European-domiciled; its "almost half" for Europe and ">65% of Asia" for China are taken literally (Europe 46%, Asia 32% = China 21% + APAC ex-China 11%, matching SCI's 32% Asia weight in total rail supply). North America at 13% equals SCI's North American weight in total rail supply and is cross-checked bottom-up (US transit rail Comm & Info capex USD 1.5bn + freight/Amtrak signalling & PTC ~USD 1.5-2.5bn ~ USD 3.0-4.0bn ~ EUR 2.7-3.5bn; see section C). GMI's 27% for North America (EUR 6.7bn) is kept as the high sensitivity; GMI visibly under-counts closed Chinese demand.

---

## 4. Section C - Passenger vs freight proxy, by region

| Region | Traffic / network evidence | Passenger share of MAINLINE CCS used | Source URLs | Confidence |
|---|---|---|---|---|
| Europe (EU-27 + UK/CH/NO/TR) | EU-27 train-km 2025: passenger 3,124.6m, goods 632.6m, total 3,757.2m -> 83.2% / 16.8% (Eurostat rail_tf_trainmv, updated 29 Oct 2026). EC Pocketbook 2025 table 2.4.15 (2023): EU-27 3,712m train-km, 81% passenger / 18% freight; DE 1,121 (78/22), FR 419 (87/13), IT 400 (87/13), ES 212 (89/11), PL 263 (70/28), NL 144 (94/6), AT 174 (76/24), SE 164 (78/22), CH 240 (89/11), NO 50 (84/16), UK 527 (94/6), TR 46 (53/47). EU-27 passenger train-km grew +3.4% in 2024 and +1.6% in 2025. Freight locomotives are a material share of ETCS onboard retrofits (Europe-specific drag), and freight trains use the same trackside ETCS/interlockings | **80%** (range 75-85%) | https://ec.europa.eu/eurostat/databrowser/view/rail_tf_trainmv/default/table (API: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/rail_tf_trainmv?format=JSON&lang=en) ; https://transport.ec.europa.eu/facts-funding/studies-data/eu-transport-figures-statistical-pocketbook/statistical-pocketbook-2025_en (pb2025-section24.xlsx) | high (data) / low-medium (spend attribution) |
| China | Network 162,000 km (2024) / 165,000 km (2025); HSR >50,000 km (passenger-dedicated, CTCS); 4.31bn passenger trips (2024); 2019: 1,470.66bn pkm vs 3,018bn tkm; urban rail 11,000.9 km / 310 lines / 45 cities (Dec 2024, Wikipedia - flagged "failed verification"); UITP: China metro 8,788 km (2023) = 43% of world. SCI: China CCS ~60% new infrastructure (HSR + metro expansion). Freight runs mainly on conventional mixed lines | **70%** (range 60-80%) | https://en.wikipedia.org/wiki/Rail_transport_in_China ; https://en.wikipedia.org/wiki/High-speed_rail_in_China ; https://en.wikipedia.org/wiki/Urban_rail_transit_in_China ; UITP GMF 2024 | medium (data) / low (attribution) |
| APAC ex-China | Japan: 30,625 km network (27,311 km in Wikipedia network table), rail carries 0.84% of goods movement, 260bn pkm vs 21bn tkm (2013-14) -> ~95% passenger. India: 69,181 route-km (Mar 2024); 13,198 passenger trains/day vs 11,724 freight trains/day (2023-24); 6.9bn passengers, 1,588m t freight; Kavach is a mixed-traffic overlay (~USD 61k/km, 85k/loco - file 12); metro 881 km. Korea 4,837 km (passenger-dominant; metro 926 km). Australia 32,924 km (heavy-haul freight dominant outside Sydney/Melbourne/Brisbane passenger ETCS/CBTC). SE Asia new lines mostly passenger. Weighted ~70% | **70%** (range 60-80%) | https://en.wikipedia.org/wiki/Rail_transport_in_Japan ; https://en.wikipedia.org/wiki/Indian_Railways ; https://en.wikipedia.org/wiki/List_of_countries_by_rail_transport_network_size | medium / low |
| North America | PTC mandate covered 57,536 route-miles at full implementation (Dec 2020; ~59,000 by 2024 rulemaking) across Class I freight, Amtrak and commuter railroads (sibling file 03; FRA site blocked). Freight railroads operate ~139,679 route-miles (2011). Amtrak network 21,400 route-miles but owns only ~623 miles of track (730 miles incl. yards; NEC 363 of 457 miles, Keystone 104 miles); commuter rail 8,718 track-miles (NTD, file 14). PTC cost US$6-22bn "most all of it borne by U.S. freight railroads"; commuter PTC >US$2bn (Wikipedia). NTD rail Comm & Info capex 2025: USD 1.50bn (heavy rail 1.01, commuter 0.26, light rail 0.19, streetcar 0.03) - file 16. Passenger therefore <10% of mainline PTC mileage but a much higher spend share because commuter/intercity programmes (LIRR/MNR USD 428m, MBTA USD 900m, Caltrain, Brightline) run at USD 0.3-1.4m/km (file 12) | **25%** of mainline (range 15-35%); plus urban CBTC = 100% passenger -> **45%** of all North American CCS | https://en.wikipedia.org/wiki/Positive_train_control ; https://en.wikipedia.org/wiki/Amtrak ; https://en.wikipedia.org/wiki/Rail_transport_in_the_United_States ; https://datahub.transportation.gov/d/fphd-jyyj (via file 16) | medium (data) / low (attribution) |
| CIS / Eurasia | Russia 92,000 km, "one of the most freight-dominant railways in the world" (619m t, 56bn pkm 2023 per infobox); Kazakhstan 16,636 km, Ukraine 19,787 km freight-heavy; Eurasia metro 1,270 km (Moscow, St Petersburg, Istanbul etc.) | **25%** of mainline (range 15-35%) | https://en.wikipedia.org/wiki/Rail_transport_in_Russia ; UITP GMF 2024 | low |
| RoW (LatAm, MENA, Africa, Australia) | Mixed: Gulf passenger metros (Riyadh, Doha, Dubai) and Etihad Rail freight; LatAm metros (1,080 km) vs freight concessions; Africa freight + new passenger lines (Egypt, Morocco); Australia heavy-haul freight | **45%** of mainline (range 35-55%) | SCI world 2026 PR; UITP GMF 2024 | low |

---

## 5. Section D - Urban (metro + LRT) vs mainline split

**Installed base (UITP, high):** metro 20,453 km double track, 202 agglomerations, 831 lines, 158,871 cars, 58.0bn trips (end-2023): Asia-Pacific 12,957 km (63%; China 8,788, Japan 973, Korea 926, India 881), Europe 2,834 (14%; Spain 532), North America 1,618 (8%), Eurasia 1,270 (6%; Russia 646), Latin America 1,080 (5%), MENA 681 (3%), Africa 13. ~800 km/yr opened 2010-23 (84% in Asia-Pacific); North America opened only 134 km in 14 years. Source: https://www.uitp.org/wp-content/uploads/sites/7/2025/08/20250822_Global-Metro-Figures_Statistics-Brief_WEB.pdf. LRT/tram (end-2021): 15,812 km, 403 cities, 36,864 vehicles: Europe 9,129 km (58%), Eurasia 3,449 (22%), North America 1,659 (10%), Asia-Pacific 1,183 (7%), MENA 245, Latin America 100, Africa 47; network +1%/yr. Source: https://www.uitp.org/wp-content/uploads/sites/7/2025/04/Statistics_Brief_-LTR-update.pdf.

**Unit costs (sibling file 12, high):** brownfield metro CBTC USD 4-30m per route-km (BART 4.0, MARTA 6.5, Berlin 5.5, TTC 10.8, NYC 20-45); greenfield Asian metro USD 1.3-1.8m/km; mainline ETCS L2 trackside EUR 0.46-0.79m/km (Italy), EUR 1.3-1.4m per track-km in dense nodes; onboard ETCS EUR 245-665k per vehicle; PTC overlay USD 0.31-0.39m/km; maintenance ~10% of capex over 25 years; conventional resignalling ~USD 1.2m/km.

**Bottom-up urban CCS proxy (analyst arithmetic, low-medium):** annualised resignalling (unit cost / 25-30-year cycle) + maintenance + new lines:
- Europe: 2,834 km x (EUR 5m/km / 25 yr + EUR 0.05m/km maintenance) + ~100 km/yr new x EUR 5m + LRT 9,129 km x EUR 0.03m = **EUR 1.5bn** (13% of Europe's EUR 11.5bn).
- North America: 1,618 km x (USD 15m/km / 30 yr + 0.05) + LRT 1,659 km x USD 0.05m = USD 0.97bn = **EUR 0.86bn** (27% of North America's EUR 3.2bn); cross-check NTD heavy-rail + light-rail Comm & Info capex USD 1.20bn (2025), MTA signals USD 5.4bn over 2025-29 (USD 1.1bn/yr).
- China: 8,788 km x (EUR 1.5m/km / 25 yr + 0.03) + ~750 km/yr new x EUR 1.5m = **EUR 1.9bn** (37% of China's EUR 5.2bn).
- APAC ex-China: 4,169 km x EUR 0.10m + ~150 km/yr new x EUR 1.5m = **EUR 0.6bn** (22%).
- CIS/Eurasia: 1,270 km x EUR 0.10m + EUR 0.05bn LRT = **EUR 0.2bn** (18%).
- RoW: 1,774 km x EUR 0.12m + ~100 km/yr new x EUR 3m = **EUR 0.5bn** (40%).
- **World urban CCS ~EUR 5.6bn = 22% of EUR 24.9bn.** Cross-checks: GMI CBTC USD 4.91bn (2025) = EUR 4.3bn for the CBTC core alone (metros USD 4.03bn = 82%, commuter 14%, high-speed 4%; basic CBTC USD 3.14bn, I-CBTC 36%; GoA2 USD 2.70bn, GoA3 22%, GoA4 15%, GoA1 8%; ~1,300 km of new metro lines entered service in 2024; historic CAGR 5.5% 2022-25; forecast 6.8% to USD 9.44bn 2035; North America USD 639m -> 1.32bn 2035, US 540m -> 1.12bn, Canada 15.5% of North America; CRSC 25.1% share, top-5 incl. Alstom, Siemens, Hitachi, CASCO = 80%). GMI signalling end-use: mainline 47% in 2024, remainder urban + freight. Archive Market Research (file 03): urban ~33% of signalling equipment (low). Range for the model: urban 20-28% of CCS.

---

## 6. Section E - Component split (hardware / software / services) evidence

| Source | Split published | Scope | URL | Confidence |
|---|---|---|---|---|
| Global Market Insights, railway signalling 2024 | Solutions ~76% / Services ~24%; services CAGR >10% vs solutions 8.5%; ETCS 31% of technology; PTC >10% CAGR; on-premises dominant deployment; top-7 (Alstom, Thales, Hitachi, Cisco, Nokia, Belden, Siemens) 47%; Alstom >14% | USD 18.2bn (2024), 19.6bn (2025), 42.4bn (2034), 8.9% | https://www.gminsights.com/pressrelease/railway-signaling-system-market | medium |
| SkyQuest, railway signalling (Nov 2025) | segmented by offering = hardware / software / services (values paid, not in free text); train type = mainline / urban / freight / high-speed; demand type = new installation / retrofit | USD 15.27bn (2024), 16.47bn (2025), 30.27bn (2033), 7.9% | https://www.skyquestt.com/report/railway-signalling-system-market | medium (sizes) / gap (split) |
| IMARC, railway signalling (Jun 2026) | Solutions > services; CBTC largest technology; mainline largest train type; North America largest region | USD 11.6bn (2025) -> 19.4bn (2034), ~5.9% derived | https://www.imarcgroup.com/railway-signaling-system-market | medium |
| MarketsandMarkets, railway management system (Dec 2025) | Solutions > services; services fastest CAGR 7.4%; rail traffic management largest solution; Europe largest region | USD 55.49bn (2025) -> 76.00bn (2030), 6.5% (umbrella incl. traffic mgmt, asset mgmt, PIS, security - do not add to CCS) | https://www.prnewswire.com/news-releases/railway-management-system-market-76-00-billion-by-2030--marketsandmarkets-302628881.html | medium |
| Mordor, TCMS (onboard) | hardware-led onboard control; USD 4.50bn (2025) -> ~6.5bn (2030), 7.5% | rolling-stock electronics, partly overlaps onboard CCS | https://www.mordorintelligence.com/industry-reports/train-control-and-management-system-market | medium |
| GMI CBTC 2025 | I-CBTC and GoA3/4 "accelerate software and integration revenue components faster than wayside hardware volumes" | qualitative | GMI CBTC URL above | medium |
| SCI 2019 (W. Europe) | maintenance & renewal "a major share" of EUR 6.6bn; HSR maintenance 193m vs new 390m; metro maintenance 170m | OE vs after-sales (trackside) | SCI 2019 flyer | medium |
| SCI metro 2026 | after-sales 52% (Europe) / 56% (North America) of 2026-30 metro-vehicle volume | vehicles, indicative of lifecycle weighting in mature markets | SCI metro PR | high |
| OEM disclosures (file 09) | Alstom Services 24% of sales (EUR 4.7bn) and 38% of backlog; Siemens Mobility Customer Services 17% of revenue / 29% of backlog (EUR 15bn of 52bn); Wabtec services + transit aftermarket 43%; Hitachi ~60% "signalling & systems" | group-level, not CCS-specific | sibling file 09 | high (data) |
| Contract evidence (file 12) | maintenance tails 10% of capex over 25 years (NYC G line), 20-25-year terms standard (Oslo, Santiago, SBB, OBB) | CBTC/ETCS awards | sibling file 12 | high |
| DB 2025 | command-and-control capex EUR 2.0bn (2024: 1.3bn) = 13% of EUR 14.9bn existing-network capex; +EUR 0.2bn ETCS Corridor A; 64 interlockings replaced | capex only (hardware + software + installation) | https://ir.deutschebahn.com/fileadmin/Deutsch/2026/DB_GB25_e_web_01.pdf (via file 14) | high (not re-read here) |

**Chosen component split (assumption A5):** urban CCS = HW 40% / SW 30% / services 30%; mainline CCS = HW 48% / SW 22% / services 30%; blended passenger = HW 46% / SW 24% / services 30%. Services 30% sits between GMI's narrow "services" 24% and the OEM/lifecycle evidence (24-56%); it is the share of annual spend, not of contract value at award. Ranges for the model: HW 40-50%, SW 20-30%, services 25-35%.

---

## 7. Section F - Reconciled 2025 matrix

### F1. Base case (UNIFE all-in anchor EUR 24.9bn = USD 28.1bn; freight-inclusive CCS)

| Region | CCS incl. freight EUR bn | Urban (metro+LRT) EUR bn | Mainline/commuter passenger EUR bn | Freight EUR bn (OUT) | **Passenger CCS EUR bn** | **Passenger CCS USD bn** | Passenger % |
|---|---|---|---|---|---|---|---|
| Europe | 11.45 | 1.49 | 7.97 | 1.99 | **9.46** | **10.69** | 83% |
| China | 5.23 | 1.93 | 2.31 | 0.99 | **4.24** | **4.79** | 81% |
| APAC ex-China | 2.74 | 0.60 | 1.50 | 0.64 | **2.10** | **2.37** | 77% |
| North America | 3.24 | 0.87 | 0.59 | 1.77 | **1.46** | **1.66** | 45% |
| CIS / Eurasia | 1.00 | 0.18 | 0.20 | 0.61 | **0.38** | **0.43** | 38% |
| RoW | 1.25 | 0.50 | 0.34 | 0.41 | **0.83** | **0.94** | 67% |
| **World** | **24.90** | **5.58 (22%)** | **12.90 (52%)** | **6.42 (26%)** | **18.48 (74%)** | **20.88** | **74%** |

### F2. Passenger CCS by region x component (base, EUR bn / USD bn at 1.13)

| Region | Hardware EUR | Software EUR | Services EUR | Total EUR | Hardware USD | Software USD | Services USD | Total USD |
|---|---|---|---|---|---|---|---|---|
| Europe | 4.42 | 2.20 | 2.84 | 9.46 | 5.00 | 2.49 | 3.21 | 10.69 |
| China | 1.88 | 1.09 | 1.27 | 4.24 | 2.13 | 1.23 | 1.44 | 4.79 |
| APAC ex-China | 0.96 | 0.51 | 0.63 | 2.10 | 1.08 | 0.58 | 0.71 | 2.37 |
| North America | 0.63 | 0.39 | 0.44 | 1.46 | 0.72 | 0.44 | 0.50 | 1.66 |
| CIS / Eurasia | 0.17 | 0.10 | 0.12 | 0.38 | 0.19 | 0.11 | 0.13 | 0.43 |
| RoW | 0.36 | 0.22 | 0.25 | 0.83 | 0.41 | 0.25 | 0.28 | 0.94 |
| **World** | **8.43 (46%)** | **4.51 (24%)** | **5.54 (30%)** | **18.48** | **9.52** | **5.09** | **6.26** | **20.88** |

Segment x component (base, EUR bn): urban 5.58 = HW 2.23 / SW 1.67 / services 1.67; mainline+commuter passenger 12.90 = HW 6.19 / SW 2.84 / services 3.87.

### F3. Low case (SCI anchor EUR 20.0bn = USD 22.6bn), same shares

| Region | CCS incl. freight | Urban | Mainline passenger | Freight (OUT) | Passenger EUR bn | Passenger USD bn |
|---|---|---|---|---|---|---|
| Europe | 9.20 | 1.20 | 6.40 | 1.60 | 7.60 | 8.59 |
| China | 4.20 | 1.55 | 1.85 | 0.79 | 3.41 | 3.85 |
| APAC ex-China | 2.20 | 0.48 | 1.20 | 0.51 | 1.69 | 1.90 |
| North America | 2.60 | 0.70 | 0.47 | 1.42 | 1.18 | 1.33 |
| CIS / Eurasia | 0.80 | 0.14 | 0.16 | 0.49 | 0.31 | 0.35 |
| RoW | 1.00 | 0.40 | 0.27 | 0.33 | 0.67 | 0.76 |
| **World** | **20.00** | **4.48** | **10.37** | **5.15** | **14.85** | **16.78** |
Component split (low): HW 6.8 / SW 3.6 / services 4.5 (EUR bn).

### F4. Sensitivities the model should carry
- Regional shares at GMI 2024 weights (Europe 37%, North America 27%, APAC 23%, LatAm 8%, MEA 6%) on EUR 24.9bn: Europe 9.2, North America 6.7, APAC 5.7, LatAm 2.0, MEA 1.5 -> passenger CCS ~EUR 17.0bn (North America passenger ~EUR 3.0bn). North America is the single most uncertain cell (EUR 1.5-3.0bn passenger).
- Mainline passenger share in Europe 75-85% moves world passenger CCS by +/- EUR 0.5bn; North America 15-35% by +/- EUR 0.25bn.
- Urban share 20-28% of CCS moves urban passenger CCS between EUR 5.0bn and 7.0bn (all passenger, so total passenger CCS changes only via the mainline passenger share applied to the remainder: 73-76%).
- Services 25-35% moves passenger services between EUR 4.6bn and 6.5bn.

---

## 8. Section G - 2025-31 growth test (passenger rail CCS, base EUR 18.5bn)

| Benchmark | CAGR | Period / scope | 2031 value if applied to EUR 18.5bn | Source | Confidence |
|---|---|---|---|---|---|
| UNIFE accessible rail control (WRMS 2024 via Alstom URD) | 3.2% real | 2021-23 -> 2027-29, accessible (ex-China) | EUR 22.3bn | sibling file 15 (Alstom URD) | medium |
| UNIFE total market (WRMS 2026) | 3.2% real | 2023-25 -> 2029-31, all segments | EUR 22.3bn | UNIFE 2026 abstract | high |
| UNIFE realised rail control | 5.7% real | 2021-23 -> 2023-25 | EUR 25.8bn | derived from UNIFE 2024/2026 abstracts | high (derived) |
| SCI CCS | 4.6% nominal | 2023-28, global CCS | EUR 24.2bn | sibling file 03 (railmarket.com) | medium |
| SCI world rail supply | 3.9% (Europe 4.4%, North America 4.2%, Asia 3.0%) | 2025-30 | EUR 23.3bn | SCI world 2026 PR | high |
| Research & Markets "Intelligence Report" | 6.05% | 2025-31 | EUR 26.3bn | sibling file 03 (not re-verified; R&M page under the guessed ID returned a different report) | low |
| IMARC | 5.9% (derived) | 2025-34 | EUR 26.1bn | IMARC | medium |
| GMI CBTC | 6.8% | 2026-35 (urban) | EUR 27.4bn | GMI CBTC | medium |
| M&M railway management system | 6.5% (services 7.4%) | 2025-30 (umbrella) | EUR 27.0bn | PR Newswire | medium |
| Mordor TCMS | 7.5% | 2025-30 (onboard) | EUR 28.5bn | Mordor | medium |
| SkyQuest railway signalling | 7.9% | 2026-33 | EUR 29.2bn | SkyQuest | medium |
| GMI railway signalling | 8.9% | 2025-34 | EUR 30.8bn | GMI | medium (outlier) |
| **Model range (analyst)** | **low 4.0% / base 5.5% / high 7.0% nominal** | 2025-31 | **EUR 23.4 / 25.5 / 27.7bn = USD 26.4 / 28.8 / 31.3bn** | assumption A6 | low-medium |

Why passenger CCS can sit above the UNIFE 3.2% total-market rate: (i) rail control is the fastest-growing UNIFE segment (5.7% p.a. realised); (ii) SCI expects Europe (46% of CCS, 83% passenger) to be the fastest-growing CCS region to 2030 and says freight segments are under severe pressure; (iii) urban CCS (22%) grows 6-7% (GMI CBTC); (iv) ERTMS backlog (ETCS on only ~10-17% of TEN-T, 19% of EU fleet - file 03/15) and NYC/Toronto/Paris/London resignalling waves are regulation- or capacity-driven and multi-year. Why not above 7%: the 3-5% real UNIFE/SCI envelope for the whole market, long approval cycles, DB's withdrawn ETCS migration strategy (file 14) and Alstom's execution problems (file 09).

---

## 9. Findings table

| # | Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | World rail control (CCS) market, WRMS 11th ed. | 24.9 | EUR bn, avg annual | 2023-2025 | World (66 countries) | Rail control, trackside+onboard, incl. freight | UNIFE WRMS 2026 abstract (Bain) | https://www.unife.org/wp-content/uploads/2026/07/UNIFE-Rail-Market-Study-2026-Abstract.pdf | high | 11.3% of EUR 220.6bn total; "rail control recorded the strongest growth" |
| 2 | World rail supply market and segments, 11th ed. | 220.6 total; services 84.1; rolling stock 68.8; infrastructure 41.7; turnkey 1.2 | EUR bn | 2023-2025 | World | All | UNIFE WRMS 2026 abstract | same as #1 | high | +4.6% p.a. real vs 2021-23; forecast +3.2% to EUR 266.8bn 2029-31; accessible ~EUR 124bn = 56% |
| 3 | World rail control, 10th ed. | 22.3 | EUR bn, avg annual, 2023 real | 2021-2023 | World | Rail control | UNIFE WRMS 2024 abstract | https://www.unife.org/wp-content/uploads/2024/07/Abstract_UNIFE_World_Rail_Market_Study.pdf | high | total 201.8; services 77.1; RS 63.3; infra 38.1; turnkey 1.1 |
| 4 | World rail control, 8th ed. | 16.8 | EUR bn p.a. | 2017-2019 | World (65 countries) | Rail control | UNIFE WRMS 2020 exec summary (Roland Berger) | https://www.unife.org/wp-content/uploads/2021/04/Forecast-2020-to-2025.pdf | high | total 177.2; services 65.0; RS 61.9; infra 32.6; turnkey 1.0; +3.6% p.a.; forecast 2.3% to ~EUR 204bn 2025 |
| 5 | World rail control, 7th ed. | 15.1 | EUR bn p.a. | 2015-2017 | World | Rail control | UNIFE WRMS 2018 exec summary | https://www.unife.org/wp-content/uploads/2021/03/World-rail-market-sturdy.pdf | high | total 163.2; services 63.8; RS 52.6; infra 31.2; turnkey 0.6; +1.2% p.a.; forecast EUR 192bn 2021-23 |
| 6 | Rail control + turnkey share, 9th ed. | ~11 | % of EUR 176.5bn | 2019-2021 | World | Rail control | UNIFE PR 20 Sep 2022 | https://www.unife.org/news/global-rail-supply-industry-resurgent-despite-crises/ | low (derived) | services+RS+infra "approximately 89%"; APAC infra & rail control +1.6%, W. Europe +4.1%; +39,000 km track; >1.7m km |
| 7 | Realised rail-control growth | 5.7 | % p.a. real | 2021-23 to 2023-25 | World | Rail control | derived from #1 and #3 | - | high (derived) | (24.9/22.3)^0.5-1 |
| 8 | Accessible rail control (WRMS 2024) | 15.7 -> 19.0 | EUR bn p.a. | 2021-23 -> 2027-29 | World accessible | Rail control | Alstom URD 2025/26 reproducing UNIFE | https://www.alstom.com/sites/alstom.com/files/2026/05/28/20260528_URD_Alstom_EN.pdf (via file 15) | medium | ~3.2% p.a.; accessible = 70% of total |
| 9 | Global CCS market volume | ~20 | EUR bn | 2025 | World | CCS incl. freight | SCI Verkehr CCS 2026 PR | https://www.sci.de/fileadmin/user_upload/pressemitteilungen/2026/PM_SCI_CCS_EN.pdf | high | Europe "almost half"; train control 40%; China >65% of Asia |
| 10 | Europe CCS modernisation vs new | ~90 / ~10 | % | 2025 | Europe | CCS | SCI CCS 2026 PR chart | same as #9 | medium | China ~40 / ~60 |
| 11 | SCI CCS study scope (2019) | trackside only | - | 2019 | World | CCS | SCI CCS 2019 extract | https://sci.de/fileadmin/user_upload/MC_Studien_Flyer/Flyer_MC_CCS_2019_de.pdf | high | "only takes into consideration stationary / track-side systems"; 8 regions, 11 focus countries; OE/AS by product and transport mode in data annex |
| 12 | World CCS new development & upgrade | ~8,750 | EUR m | 2018 (avg) | World | CCS trackside OE | SCI CCS 2019 extract | same as #11 | medium | interlocking ~40%, ETCS/CTCS/CBTC ~25%, conventional ~15%, other ~15%, telematics ~5% |
| 13 | Western Europe CCS market | 6,582; +3.0 | EUR m p.a.; % CAGR 2018-23 | 2018 | Western Europe | CCS OE + after-sales | SCI CCS 2019 extract | same as #11 | high | HSR new 390, HSR maint 193, metro maint 170; CR new +2.9%, metro new +2.8%, LRT maint +2.1% |
| 14 | Operational telematics / train communication | 850 global; 370 new development | EUR m | 2018 | World | Telematics | SCI CCS 2019 extract | same as #11 | medium | new-dev regional: Asia 45%, W. Europe 30%, North America 10%; suppliers CRSC 35%, Kapsch, Huawei, Nokia |
| 15 | Siemens share of European CCS; CRSC global share | >35; 23 | % | 2018 | Europe; World | CCS | SCI CCS 2019 PR | https://www.sci.de/en/data-trends/document/etcs-technology-close-to-a-breakthrough-regarding-comprehensive-utilisation-the-european-market-for | high (dated) | ETCS +~5% p.a. 2018-23; DB EUR 570m to 2023; ~EUR 1bn/yr needed |
| 16 | SCI world rail supply by region | Europe 77.7 (4.4%); Asia 73.9 (3.0%); North America 29.9 (4.2%); CIS 28.5 (2.9%); Africa/ME 9.0 (6.1%); S/C America 4.5 (5.2%); Australia 4.5 (4.5%) | EUR bn avg 2024-26 (CAGR 2025-30) | 2024-2026 | Regions | All rail supply | SCI world market 2026 PR | https://www.sci.de/fileadmin/user_upload/pressemitteilungen/2026/PM_MC_Weltmarkt_EN.pdf | high | >EUR 275bn by 2030 at 3.9%; passenger drives growth; freight "under severe pressure" |
| 17 | Metro vehicle market; after-sales share | 17.6 -> 22.9 (5.4%); Europe 52%, North America 56% after-sales | EUR bn; % | 2025-2030 | World; regions | Metro vehicles (adjacent) | SCI metro 2026 PR | https://www.sci.de/fileadmin/user_upload/pressemitteilungen/2026/PM_SCI_Metro_EN.pdf | high | ~850 automated-project vehicles + ~550 CBTC-linked 2025-30 |
| 18 | EU-27 train-km passenger vs goods | 3,124,567 vs 632,588 (total 3,757,155) | thousand train-km | 2025 | EU-27 | Rail traffic | Eurostat rail_tf_trainmv (API) | https://ec.europa.eu/eurostat/databrowser/view/rail_tf_trainmv/default/table | high | 83.2% / 16.8%; 2024 passenger 3,076,782; 2023 2,975,158; updated 2026-10-29 |
| 19 | Country train-km passenger / goods 2024 | DE 904,985/247,613; FR 388,441/53,802; IT 349,079/50,936; ES 190,135/24,130; AT 138,522/41,590; SE 132,762/37,218; CH 214,936/26,648; NO 42,288/6,939; TR 24,491/22,749; PL goods 71,564; UK (2019) 560,519/33,941 | thousand train-km | 2024 | Countries | Rail traffic | Eurostat rail_tf_trainmv | same as #18 | high | |
| 20 | EU-27 train-km and passenger/freight shares (pocketbook) | 3,712; 81 / 18 | million train-km; % | 2023 | EU-27 | Rail traffic | EC Statistical Pocketbook 2025, table 2.4.15 | https://transport.ec.europa.eu/facts-funding/studies-data/eu-transport-figures-statistical-pocketbook/statistical-pocketbook-2025_en | high | DE 1,121 (78/22); FR 419 (87/13); IT 400 (87/13); ES 212 (89/11); PL 263 (70/28); NL 144 (94/6); AT 174 (76/24); SE 164 (78/22); CH 240 (89/11); NO 50 (84/16); UK 527 (94/6); TR 46 (53/47) |
| 21 | World metro network by region | total 20,453; Asia-Pacific 12,957; Europe 2,834; North America 1,618; Eurasia 1,270; Latin America 1,080; MENA 681; Africa 13 | km double track | end-2023 | World | Metro | UITP Global Metro Figures 2024 | https://www.uitp.org/wp-content/uploads/sites/7/2025/08/20250822_Global-Metro-Figures_Statistics-Brief_WEB.pdf | high | 202 cities, 831 lines, 158,871 cars, 58.0bn trips; China 8,788 km (43%); Japan 973; Korea 926; India 881; Russia 646; Spain 532; >800 km/yr opened 2010-23, 84% in APAC |
| 22 | World LRT network by region | total 15,812; Europe 9,129; Eurasia 3,449; North America 1,659; Asia-Pacific 1,183; MENA 245; Latin America 100; Africa 47 | km | end-2021 | World | LRT/tram | UITP Tram & LRT brief | https://www.uitp.org/wp-content/uploads/sites/7/2025/04/Statistics_Brief_-LTR-update.pdf | high | 403 cities; 36,864 vehicles; +1%/yr |
| 23 | Railway signalling market (GMI) | 18.2 (2024); 19.6 (2025); 42.4 (2034); 8.9% | USD bn; % | 2024-2034 | World | Signalling incl. freight | Global Market Insights | https://www.gminsights.com/pressrelease/railway-signaling-system-market | medium | solutions 76% / services 24%; ETCS 31%; mainline 47%; Europe 37%; APAC 23% (11% CAGR); LatAm 8%; MEA 6%; US USD 4.2bn = 85% of North America; Alstom >14%; top-5 43% |
| 24 | CBTC market (GMI) | 4.91 (2025); 5.21 (2026); 9.44 (2035); 6.8% | USD bn; % | 2025-2035 | World | Urban CBTC | Global Market Insights | https://www.gminsights.com/industry-analysis/communication-based-train-control-market | medium | metros USD 4.03bn (82%); commuter 14%; HSR 4%; GoA2 USD 2.70bn; GoA3 22%; GoA4 15%; I-CBTC 36%; North America USD 639m, US 540m; CRSC 25.1%; top-5 80%; 5.5% historic 2022-25 |
| 25 | Railway signalling market (SkyQuest) | 15.27 (2024); 16.47 (2025); 30.27 (2033); 7.9% | USD bn; % | 2024-2033 | World | Signalling | SkyQuest | https://www.skyquestt.com/report/railway-signalling-system-market | medium | offering = hardware/software/services (values paid); train types mainline/urban/freight/high-speed |
| 26 | Railway signalling market (IMARC) | 11.6 (2025); 19.4 (2034) | USD bn | 2025-2034 | World | Signalling | IMARC | https://www.imarcgroup.com/railway-signaling-system-market | medium | ~5.9% derived; solutions largest; CBTC largest tech; mainline largest; North America largest region |
| 27 | Railway management system market (M&M) | 55.49 (2025); 76.00 (2030); 6.5% | USD bn; % | 2025-2030 | World | Umbrella (traffic mgmt, asset mgmt, PIS, security) | MarketsandMarkets via PR Newswire | https://www.prnewswire.com/news-releases/railway-management-system-market-76-00-billion-by-2030--marketsandmarkets-302628881.html | medium | solutions > services; services 7.4% CAGR; rail traffic management largest; Europe largest; do not add to CCS |
| 28 | TCMS market (Mordor) | 4.50 (2025); ~6.5 (2030); 7.5% | USD bn; % | 2025-2030 | World | Onboard TCMS | Mordor Intelligence | https://www.mordorintelligence.com/industry-reports/train-control-and-management-system-market | medium | |
| 29 | ECB USD/EUR annual average | 1.1300 (2025); 1.0824 (2024); 1.0813 (2023) | USD per EUR | 2023-2025 | - | FX | ECB SDW | https://data-api.ecb.europa.eu/service/data/EXR/A.USD.EUR.SP00.A?format=csvdata&startPeriod=2023 | high | |
| 30 | PTC implementation cost | US$6-22bn "most all of it borne by U.S. freight railroads"; commuter PTC (up to 25 services) >US$2bn | USD | 2010s | USA | PTC | Wikipedia (Positive train control) | https://en.wikipedia.org/wiki/Positive_train_control | low-medium | 41 railroads; 4 met 2018 deadline, 37 extended to 2020; all complete 29 Dec 2020 |
| 31 | PTC route-miles at full implementation | 57,536 | route-miles | Dec 2020 | USA | PTC | FRA via sibling file 03 | https://railroads.dot.gov/newsroom/press-releases/federal-railroad-administration-announces-landmark-achievement-full | high (not re-read; host blocked) | ~41% of ~140,000 US route-miles |
| 32 | Amtrak network and owned track | 21,400 route-miles network; ~623 miles owned (730 incl. yards); NEC 363 of 457 miles; Keystone 104 miles | miles | 2024-25 | USA | Intercity passenger | Wikipedia (Amtrak) | https://en.wikipedia.org/wiki/Amtrak | medium | BNSF hosts 6.3m Amtrak train-miles |
| 33 | US freight route-miles | 139,679 | route-miles | 2011 | USA | Freight | Wikipedia (Rail transport in the US) | https://en.wikipedia.org/wiki/Rail_transport_in_the_United_States | medium | 6 Class I railroads (2024) |
| 34 | US commuter rail track-miles | 8,718 | track-miles | 2025 | USA | Commuter rail | NTD via sibling file 14 | https://data.transportation.gov/resource/fzbb-f6kc.csv | high | HR 2,369; LR 1,883; SR 400 |
| 35 | US transit rail "Communication & Information" capex | 1.50 (HR 1.01; CR 0.26; LR 0.19; SR 0.03); all modes 1.90 | USD bn | FY2025 | USA | Transit rail train control/comms/IT | NTD via sibling file 16 | https://datahub.transportation.gov/d/fphd-jyyj | high | category includes cab signalling and train control; 2023: 2.17, 2024: 2.24 (all modes) |
| 36 | NYC MTA subway signals plan | 5.4 | USD bn | 2025-2029 | USA (NYC) | Metro CBTC | GMI CBTC citing Streetsblog; sibling file 12 | https://www.gminsights.com/industry-analysis/communication-based-train-control-market | high | 75+ miles |
| 37 | China rail network and traffic | 162,000 km (2024) / 165,000 km (2025); HSR >50,000 km; 4.31bn passenger trips (2024); 1,470.66bn pkm and 3,018bn tkm (2019) | km; trips; pkm; tkm | 2019-2025 | China | Mainline | Wikipedia (Rail transport in China; HSR in China; network list) | https://en.wikipedia.org/wiki/Rail_transport_in_China ; https://en.wikipedia.org/wiki/High-speed_rail_in_China ; https://en.wikipedia.org/wiki/List_of_countries_by_rail_transport_network_size | medium | NRA bulletin not reachable |
| 38 | China urban rail | 11,000.88 km; 310 lines; 45 cities | km | Dec 2024 | China | Urban rail | Wikipedia (Urban rail transit in China) | https://en.wikipedia.org/wiki/Urban_rail_transit_in_China | low | page flags "failed verification"; UITP metro-only 8,788 km (2023) |
| 39 | Japan rail | 30,625 km; rail = 0.84% of goods movement; 260bn pkm vs 21bn tkm (2013-14) | km; %; pkm/tkm | 2013-2020s | Japan | Mainline | Wikipedia (Rail transport in Japan) | https://en.wikipedia.org/wiki/Rail_transport_in_Japan | medium | passenger-dominant |
| 40 | India rail | 69,181 route-km (Mar 2024); 13,198 passenger vs 11,724 freight trains/day (2023-24); 6.905bn passengers; 1,588m t | km; trains/day | 2023-24 | India | Mainline | Wikipedia (Indian Railways) | https://en.wikipedia.org/wiki/Indian_Railways | medium | |
| 41 | Russia rail | 92,000 km; freight-dominant (619m t; 56bn pkm 2023 per infobox) | km | 2023 | Russia | Mainline | Wikipedia (Rail transport in Russia) | https://en.wikipedia.org/wiki/Rail_transport_in_Russia | low-medium | |
| 42 | Other network lengths | Canada 49,422; Australia 32,924; Brazil 29,817; Japan 27,311; Mexico 23,389; Ukraine 19,787; Argentina 17,866; Kazakhstan 16,636; Turkey 13,919; Indonesia 8,260; South Korea 4,837 | km | various | Countries | Mainline | Wikipedia network-size list | https://en.wikipedia.org/wiki/List_of_countries_by_rail_transport_network_size | low-medium | mixed vintages |
| 43 | DB command-and-control capex | 2.0 (2024: 1.3); 13% of 14.9 existing-network capex; +0.2 ETCS Corridor A; 64 interlockings replaced | EUR bn | 2025 | Germany | Mainline CCS | DB 2025 Integrated Report via sibling file 14 | https://ir.deutschebahn.com/fileadmin/Deutsch/2026/DB_GB25_e_web_01.pdf | high (not re-read here) | 2026 federal digitalisation line EUR 2.5bn |
| 44 | Unit costs (resignalling) | metro CBTC brownfield USD 4-30m/km; greenfield Asia USD 1.3-1.8m/km; ETCS L2 trackside EUR 0.46-0.79m/km; onboard ETCS EUR 245-665k/vehicle; PTC USD 0.31-0.39m/km; maintenance ~10% of capex / 25 yrs | various | 2019-2026 | World | CCS | sibling file 12 | research/12_contract_benchmarks.md | high | used only as weights |
| 45 | OEM services shares | Alstom Services 24% of sales / 38% of backlog; Siemens Mobility Customer Services 17% / 29%; Wabtec services + transit aftermarket 43%; Hitachi ~60% signalling & systems | % | FY2025 | Global | OEM | sibling file 09 | research/09_rail_competitors.md | high | |
| 46 | Alstom / Siemens / Hitachi signalling revenue | Alstom Signalling EUR 2,702m (FY25/26); Siemens Mobility EUR 12.44bn (Rail Infrastructure ~33% = ~EUR 4.1bn); Hitachi Rail >EUR 7bn (~60% signalling & systems); Wabtec Digital Intelligence USD 1.03bn; MERMEC businesses ~EUR 430m; CRSC CNY 34.4bn (2017) | EUR/USD/CNY | 2025 | Global | Vendors | sibling file 09 | same | high / low (CRSC dated) | used for triangulation |

---

## 10. Vendor revenue triangulation (company profiles, short - full profiles in file 09)

| Company | HQ | Ownership | CCS-relevant revenue (2025) | Notes for the matrix | Source |
|---|---|---|---|---|---|
| Siemens Mobility | Munich, DE | Siemens AG | Rail Infrastructure ~EUR 4.1bn (33% of EUR 12.44bn; includes electrification and rail software); Customer Services 17% | #1 in European CCS (>35% share per SCI 2019); DB, Infrabel, Berlin, Copenhagen GoA4 | file 09; Siemens fact sheets |
| Alstom | Saint-Ouen, FR | listed (CDPQ 17.5%) | Signalling EUR 2,702m; Signalling orders 3,445m; backlog 9,756m | ex-services; Urbalis CBTC, Atlas ETCS; RFI ETCS frameworks; Nov-2026 profit warning / disposals review | file 09; Alstom FY25/26 PR |
| Hitachi Rail (incl. ex-Thales GTS) | London / Tokyo | Hitachi Ltd | ~EUR 4.4bn signalling & systems (~60% of >EUR 7bn) | SelTrac on 150+ lines; mainline ETCS; OBB EUR 1.3bn interlocking framework | file 09 |
| CRSC | Beijing, CN | state-owned, listed | CNY 34.4bn (2017, dated); 23% of global CCS (2018, SCI); 25.1% of CBTC (2025, GMI) | <5% international; defines the "closed" China cell | SCI 2019 PR; GMI CBTC |
| Wabtec | Pittsburgh, US | listed | Digital Intelligence USD 1.03bn (2025); PTC I-ETMS on most of ~24,600 locomotives | freight-weighted; sets North America freight CCS | file 09; Wabtec 10-K |
| Knorr-Bremse / KB Signaling | Munich, DE | listed | n/d (ex-Alstom NA conventional signalling) | MBTA, LA, Chicago wayside; UK framework | file 09 |
| MERMEC / Siemens | Monopoli, IT | private / sold to Siemens 2026 | ~EUR 430m (acquired businesses) | ETCS RBC, CBI, diagnostics | file 09 |
| Stadler Signalling, CAF Signalling, Nippon Signal, Kyosan, CASCO | CH / ES / JP / JP / CN | various | n/d | challengers; CASCO (Alstom JV) is in GMI's CBTC top-5 | file 09; GMI CBTC |

Sum of disclosed/derived CCS-type revenues of the named players ~EUR 17-19bn (with electrification and systems noise) plus Chinese non-CRSC, Japanese, Korean and tail suppliers -> EUR 22-26bn, consistent with the EUR 24.9bn anchor (low-medium).

---

## 11. Section H - Assumption register (every analyst assumption, with range)

| ID | Assumption | Base value | Range | Evidence trail | Confidence |
|---|---|---|---|---|---|
| A0 | 2025 all-in CCS base (HW+SW+services, trackside+onboard, incl. freight) | EUR 24.9bn (UNIFE 2023-25 avg, 2025 real terms) | EUR 20bn (SCI) - 27bn (UNIFE rolled to 2025 at 5.7%) | section A3; vendor triangulation section 10 | medium |
| A1 | Regional shares of CCS | Europe 46 / China 21 / APAC ex-China 11 / North America 13 / CIS 4 / RoW 5 | North America 10-27; Europe 37-48; China 15-25 | section B (SCI 2026, SCI 2019, SCI world, GMI, UITP) | low-medium |
| A2 | Urban (metro+LRT) share of each region's CCS | Europe 13 / China 37 / APAC ex-China 22 / North America 27 / CIS 18 / RoW 40 (world 22%) | world 20-28% | section D bottom-up vs GMI CBTC USD 4.91bn and NTD | low-medium |
| A3 | Passenger share of mainline CCS | Europe 80 / China 70 / APAC ex-China 70 / North America 25 / CIS 25 / RoW 45 | +/-10 pts each | section C (Eurostat, EC pocketbook, Wikipedia country pages, PTC/Amtrak/NTD) | low-medium (Europe medium) |
| A4 | Freight share of world CCS (result) | 26% | 22-32% | consistent with GMI mainline 47% + urban ~25% -> freight ~28% | low-medium |
| A5 | Component split | urban HW 40/SW 30/services 30; mainline HW 48/SW 22/services 30; blended HW 46/SW 24/services 30 | HW 40-50; SW 20-30; services 25-35 | section E (GMI 76/24, OEM services shares, lifecycle contract tails) | low-medium |
| A6 | Passenger CCS CAGR 2025-31 (nominal) | 5.5% | 4.0-7.0% | section G | low-medium |
| A7 | Scope: UNIFE rail control treated as all-in (incl. services) | - | services could add up to +20-25% if UNIFE excludes them entirely | section A3 | medium |
| A8 | Urban unit-cost annualisation (25-30-yr cycle, maintenance 0.03-0.05 EUR m/km/yr) | - | +/-30% | file 12 unit costs | low |

---

## 12. Gaps (what a second pass or a paid purchase would close)

1. UNIFE WRMS 2026 "Forecast Control Command and Signalling" module (EUR 780): regional CCS volumes 2023-25 and 2026-31 - the single purchase that would replace assumption A1 with primary data.
2. SCI Verkehr CCS 2026 full study (regional volumes by product group and transport mode - the data annex has "market size OE/AS per transport mode", i.e. HSR / conventional / metro / LRT, which would also replace A2 and part of A3).
3. FRA PTC statistics by railroad class (route-miles and locomotives for Class I vs Amtrak vs commuter) - railroads.dot.gov is blocked in this session; the ~8% passenger mileage share is inferred from Amtrak-owned track and NTD commuter track-miles.
4. China passenger vs freight train-km (National Railway Administration statistical bulletin) and MOT urban-rail km 2025 - not reachable; HSR-km and pkm/tkm used instead.
5. Train-km for Japan, Korea, India, Australia (UIC Railisa / national yearbooks) - UIC synopsis PDFs 404; network km and train counts used.
6. A vendor report that publishes the hardware/software/services split numerically (SkyQuest and Fortune hold it behind paywalls; Technavio/Precedence/Mordor signalling pages returned no numbers).
7. Class I railroad signals & communications capex (STB R-1 schedule) to firm up the North America freight CCS cell.
8. Research & Markets 6.05% CAGR and SCI EUR 19.3bn/4.6% (2023-28) are sibling-sourced and were not re-verified here (railmarket.com blocked; R&M page ID returned a different report).
9. UNIFE WRMS 2022 (9th edition) rail-control volume for 2019-21 (only derivable as ~11% of EUR 176.5bn).

---

## 13. Source list (all read directly in this pass unless marked "via sibling file")

UNIFE
- https://www.unife.org/wp-content/uploads/2026/07/UNIFE-Rail-Market-Study-2026-Abstract.pdf (11th ed. abstract; rail control EUR 24.9bn)
- https://www.unife.org/wp-content/uploads/2024/07/Abstract_UNIFE_World_Rail_Market_Study.pdf (10th ed. abstract; EUR 22.3bn)
- https://www.unife.org/wp-content/uploads/2021/04/Forecast-2020-to-2025.pdf (8th ed. executive summary; EUR 16.8bn)
- https://www.unife.org/wp-content/uploads/2021/03/World-rail-market-sturdy.pdf (7th ed. executive summary; EUR 15.1bn)
- https://www.unife.org/wp-content/uploads/2021/03/WORLD-RAIL-MARKET-STUDY-EXECUTIVE-SUMMARY.pdf (5th ed.)
- https://www.unife.org/wp-content/uploads/2021/05/World-Markets-Factsheet-May.pdf (2021 factsheet on WRMS 2020)
- https://www.unife.org/news-resources/wrms/ ; https://www.unife.org/publication/world-rail-market-study-executive-summary-forecast-2020-to-2025/
- https://www.unife.org/news/global-rail-supply-industry-resurgent-despite-crises/ (2022 PR)
- https://www.unife.org/news/policymakers-and-industry-give-vote-of-confidence-as-global-rail-supply-market-continues-to-expand-despite-geopolitical-tensions/ (2024 PR)
- https://www.unife.org/news/global-rail-booms-as-closed-markets-now-cost-eu-industry-e97-billion-per-year/ (2026 PR)
- https://www.railwaygazette.com/business/2026/10/09/world-rail-market-study-predicts-continuing-growth-following-covid-rebound/
- https://www.rolandberger.com/en/Insights/Publications/UNIFE-World-Rail-Market-2020.html (page reachable; no figures beyond the UNIFE summary)

SCI Verkehr
- https://www.sci.de/fileadmin/user_upload/pressemitteilungen/2026/PM_SCI_CCS_EN.pdf (CCS 2026)
- https://sci.de/fileadmin/user_upload/MC_Studien_Flyer/Flyer_MC_CCS_2019_de.pdf (CCS 2019 extract)
- https://www.sci.de/en/data-trends/document/etcs-technology-close-to-a-breakthrough-regarding-comprehensive-utilisation-the-european-market-for (CCS 2019 PR)
- https://www.sci.de/fileadmin/user_upload/pressemitteilungen/2026/PM_MC_Weltmarkt_EN.pdf (world market 2026)
- https://www.sci.de/fileadmin/user_upload/pressemitteilungen/2026/PM_SCI_Metro_EN.pdf (metro vehicles 2026)
- https://railmarket.com/news/technology-innovation/16494-unveiling-the-future-sci-verkehr-s-insights-into-rail-control-and-signaling-market-trends (via sibling file 03; blocked here)

Traffic, network and FX statistics
- https://ec.europa.eu/eurostat/databrowser/view/rail_tf_trainmv/default/table and API https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/rail_tf_trainmv?format=JSON&lang=en
- https://transport.ec.europa.eu/facts-funding/studies-data/eu-transport-figures-statistical-pocketbook/statistical-pocketbook-2025_en (pb2025-section24.xlsx, table 2.4.15)
- https://www.uitp.org/wp-content/uploads/sites/7/2025/08/20250822_Global-Metro-Figures_Statistics-Brief_WEB.pdf
- https://www.uitp.org/wp-content/uploads/sites/7/2025/04/Statistics_Brief_-LTR-update.pdf
- https://data-api.ecb.europa.eu/service/data/EXR/A.USD.EUR.SP00.A?format=csvdata&startPeriod=2023
- https://en.wikipedia.org/wiki/Positive_train_control ; https://en.wikipedia.org/wiki/Amtrak ; https://en.wikipedia.org/wiki/Rail_transport_in_the_United_States
- https://en.wikipedia.org/wiki/Rail_transport_in_China ; https://en.wikipedia.org/wiki/High-speed_rail_in_China ; https://en.wikipedia.org/wiki/Urban_rail_transit_in_China
- https://en.wikipedia.org/wiki/Rail_transport_in_Japan ; https://en.wikipedia.org/wiki/Indian_Railways ; https://en.wikipedia.org/wiki/Rail_transport_in_Russia ; https://en.wikipedia.org/wiki/List_of_countries_by_rail_transport_network_size
- https://railroads.dot.gov/newsroom/press-releases/federal-railroad-administration-announces-landmark-achievement-full (via sibling file 03; blocked here)
- https://datahub.transportation.gov/d/fphd-jyyj and https://data.transportation.gov/resource/fzbb-f6kc.csv (NTD via sibling files 14/16)
- https://ir.deutschebahn.com/fileadmin/Deutsch/2026/DB_GB25_e_web_01.pdf (via sibling file 14)

Vendor market reports
- https://www.gminsights.com/pressrelease/railway-signaling-system-market ; https://www.gminsights.com/industry-analysis/railway-signaling-system-market
- https://www.gminsights.com/industry-analysis/communication-based-train-control-market
- https://www.skyquestt.com/report/railway-signalling-system-market
- https://www.imarcgroup.com/railway-signaling-system-market
- https://www.prnewswire.com/news-releases/railway-management-system-market-76-00-billion-by-2030--marketsandmarkets-302628881.html
- https://www.mordorintelligence.com/industry-reports/train-control-and-management-system-market
- Not usable (403 / 404 / JS shell): fortunebusinessinsights.com, alliedmarketresearch.com, databridgemarketresearch.com, mordorintelligence.com railway-signalling URLs, technavio.com, precedenceresearch.com, marketresearchfuture.com, market.us, verifiedmarketresearch.com, thebusinessresearchcompany.com, futuremarketinsights.com, researchandmarkets.com/reports/5939431

Sibling research files used: 03_rail_subsegment_reports.md, 09_rail_competitors.md, 12_contract_benchmarks.md, 14_operator_capital_plans.md, 15_industry_studies.md, 16_ntd_data_pull.md (all under research/).
