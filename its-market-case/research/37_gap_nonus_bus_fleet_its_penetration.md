# 37 — Gap fill: non-US / non-EU bus demand base and ITS penetration (RoW roadway block)

**Prepared 2026-11-07** for the Public ITS (Roadway bus + Railway) CDD-style case. Companion data file: `/home/user/Project-2-/its-market-case/data/nonus_bus_fleets_by_country.csv` (20 country rows; transit-only vs registered fleet, year, scope, source URL, confidence, notes).

**Method and caveats.** The shared WebSearch budget for this turn was already exhausted when this task started (every query returned "budget used up"), so this note is built entirely from **direct fetches of primary sources through the session proxy** (curl with a browser User-Agent, PDFs converted with `pdftotext`, xlsx/CSV parsed with `python3 -I`) plus the figures already sourced in research files 01/02/04/05/07/12/16. The Berg Insight 10th-edition summary PDF **now returns HTTP 200** and was read in full (6 pages; text in the scratchpad). Hosts that were still unreachable or empty in this run: researchandmarkets.com, giiresearch.com, marketresearch.com (403), globenewswire.com (403), xxgk.mot.gov.cn 2025 bulletin (connection drop; the 2024 bulletin loaded), atuc.es, semovi.cdmx.gob.mx, mit.gov.it, stat.molit.go.kr, molit.go.kr, seoulsolution.kr, data.ibb.gov.tr, tih.hk, kmb.hk (report moved), iett.istanbul content pages (HTTP 500), ntu.org.br (JS single-page app, no document links), anav.it/dati-imprese, its.go.kr, c40.org (403). Every number below carries the URL it was read from; figures taken from earlier research files are labelled "(file NN)". Nothing is extrapolated without the label **DERIVED**. FX conventions: 1.10 USD/EUR (as in file 01) and 83 INR/USD (assumption) are used only in DERIVED lines.

---

## 1. Key takeaways

1. **The Berg Insight 10th-edition summary PDF is now readable and gives the full scope definition, but it does NOT publish a hardware/software/services split, a CAD/AVL-vs-PIS-vs-APC-vs-video split, installed-base unit counts or vendor share percentages — those sit only in the paid 315-page report and its Excel dataset.** The definition is broad: "systems installed in public transport vehicles as well as at terminals, stops, depots and similar... also back-office IT systems which ensure that public transport services can be planned, scheduled and managed... [and] solutions providing travellers with updated information", with "automated fare collection systems using contactless cards or NFC-enabled handsets for account-based ticketing" and "advanced mobility analytics software" cited as state-of-the-art examples. The market value (Europe EUR 2.55bn → 3.30bn, 2025-30, 5.3% CAGR; North America EUR 1.22bn → 1.56bn, 5.0%; combined EUR 3.8bn → 4.9bn, 5.2%) is explicitly "for buses and trams", and the penetration metric is "on-board computers with GPS location functionality and wireless communications in buses and trams" (Europe 90.3% → 93.9%; NA 91.9% → 94.1%). Fleet base is "registered buses and coaches" (0.85m Europe, 1.1m NA, 2023) — i.e. the denominator includes coaches, school buses and private operators, not just transit fleets. The 9th edition (read for comparison) used 0.86m / 1.0m (2021) and forecast NA penetration of 97.7% by 2027, which the 10th edition has restated down to 94.1% by 2030 — a quiet downgrade of NA coverage assumptions.
2. **Per-vehicle intensity depends entirely on the denominator.** Berg's EUR 3.77bn over 1.95m registered buses & coaches is EUR 1,933 per registered vehicle (Europe EUR 3,000; NA EUR 1,109, DERIVED). Re-based on *transit* fleets the same value is EUR 6.7-8.6k per European transit bus (0.85m × 35-45% transit share) and EUR 10-15k per North American full-size transit bus (US 65,239 + Canada 16,145, with/without 40,218 US cutaways) — 2-3x the NTD capital-only proxy of USD 5.8k per full-size bus (file 04/16) and 4-6x London iBus2's ~USD 2.3k per bus per year for CAD/AVL + PIS as a service (file 12). The gap is explained by Berg's inclusion of back-office IT, scheduling, stop/terminal/depot equipment, fare-collection-related on-board systems and services, plus coach/intercity telematics. **Recommendation: do not transfer Berg's per-registered-bus figure to RoW transit fleets; use a tiered USD-per-transit-bus intensity with explicit scope (section 5).**
3. **New primary fleet anchors close four of the eight country gaps in file 05 and partially close the rest.** Poland: 12,811 urban-transport buses (+233 trolleybuses, 3,007 trams) at 31 Dec 2025 vs 109,253 registered buses (GUS) — only 11.7% of registered buses are urban-transit. Spain: 14,333 urban + metropolitan buses in the 24 OMM metropolitan areas (2024) vs 64,097 registered (ACEA) — 22%. Japan: 64,570 scheduled-route (乗合) buses and 2,434 operators in FY2023 (MLIT via Nihon Bus Kyokai; 54,474 in FY2022, 57,914 in FY2020), of which the JBA member survey counts 45,416 general route buses (31 Mar 2025). Hong Kong: 5,868 licensed franchised buses (May 2026) out of 13,830 registered buses of all classes. Singapore: 18,357 registered buses (2025), of which 6,222 are in the >70-passenger class that corresponds to the ~5,800-bus public fleet. Mexico: INEGI registers 181,109 public-service and 303,048 private "camiones para pasajeros" (2023), but the organised urban systems INEGI tracks in 8 metropolitan areas operate only ~8,200 buses plus 429 CDMX trolleybuses (Aug 2026). Italy remains an estimate (ASSTRA: ~40,000 road + rail vehicles at 140 members covering 95% of the urban market). South Korea, Türkiye and Brazil national transit fleets are still unsourced (city-level only: Seoul 7,383; Istanbul ~6,700; São Paulo >13,000).
4. **ITS penetration outside Europe/NA is bimodal: near-universal in the city-state/high-income Asian and Gulf networks and in formal BRT systems, mandated-but-thin in India, and unmeasured in China.** Evidence captured: Spain — 100% SAE (CAD/AVL) coverage on urban buses in every OMM area and 97-100% on most metropolitan fleets (Granada 24%), 100% e-ticketing on buses almost everywhere, but real-time stop panels at only 3-51% of stops and traffic-signal priority at a handful of intersections (OMM 2024-25 Tables 26-27). Japan — 80.0% of general route buses carry digital tachographs and 89.7% drive recorders (JBA survey, Mar 2025), cashless fare share 88.4% of fare value at operators with ≥30 buses (FY2023, MLIT) with 18 operators/29 routes piloting fully cashless buses in FY2024; bus-location adoption itself not retrievable. Korea — Seoul's TOPIS BMS/BIS "collects, processes, and analyzes bus location information in real-time" for the whole fleet and evaluates operators on it (qualitative; national BIS coverage not sourced). India — vehicle location tracking + emergency button mandated for *all* public service vehicles since the MoRTH notification of 28 Nov 2016 (AIS-140), with a Rs 463.90 crore state-wise VLT monitoring-platform scheme (Rs 213.88 crore released, 33 States/UTs funded, 8 monitoring centres live) and a Rs 175 crore "Strengthening ITS in Public Transport" scheme (FY2022-23 to 2025-26, 70:30 central share) that implies only ~USD 36 per SRTU bus per year of central ITS money (DERIVED) — i.e. compliance-grade tracking, not CAD/AVL. China — 74.1% of the 658,100 public buses were battery-electric at end-2024 (87.5% new-energy at end-2025 per file 05), but no MOT statistic on GPS dispatch or e-payment coverage could be retrieved; penetration is inferred (low confidence). Latin America — Santiago's DTPM publishes GPS positioning data for the complete bus fleet; São Paulo runs >13,000 buses on 1,340 lines under SPTrans contracts; Mexico's organised systems are small. Gulf — Riyadh Bus (842 buses, RATP Dev/SAPTCO, Darb account-based ticketing) and Dubai RTA (~1,442 buses) are greenfield, fully instrumented networks.
5. **Per-bus ITS contract benchmarks outside Europe/NA are scarce in public sources, and the Indian e-bus model explicitly keeps ITS out of the per-km price.** CESL's Grand Challenge case study states that the 12-year gross-cost per-km quote covers bus capex, charging, O&M, staff, energy and financing, while "Cities will incur... operational expenditure on revenue collection (using conductors), Intelligent Transport systems for vehicle tracking and ticketing and contract management expenditure" — so the Indian e-bus wave (5,450 buses at L1 Tata Motors in 2022; 10,900 + 6,230 tendered 2025-26, file 07) adds buses with AIS-140-grade on-board units but leaves CAD/AVL, PIS and AFC as separate city procurements. Singapore LTA, Hong Kong KMB and Riyadh Bus contract values were not disclosed in any reachable primary page; the only non-Western per-bus benchmark available remains the fleet-level inference in section 5.
6. **Recommended regional per-bus intensity (USD per transit bus per year, all-in ITS incl. back-office and services; DERIVED, low-to-medium confidence):** Europe and North America — keep Berg top-down (equivalent to EUR 3.0k / 1.1k per registered bus-coach, or ~EUR 7-9k / 10-15k per transit bus); high-income APAC (Japan, Korea, Singapore, Hong Kong, Taiwan, Australia/NZ) USD 2,500-4,000; Gulf greenfield USD 4,000-6,000; China USD 700-1,200; India USD 250-600; formal Latin American systems (São Paulo, Bogotá, Santiago, Mexico City BRT) USD 1,000-2,000 with informal fleets at ~0; Türkiye/Mexico/other emerging USD 300-800. Applied to the sourced fleets this yields an indicative RoW bus ITS block of roughly **USD 0.9-1.6bn in 2025 (DERIVED)** versus Berg's ~USD 4.1bn for Europe + North America, with China alone USD 0.45-0.75bn of it.

---

## 2. Berg Insight 10th edition — what the now-reachable summary PDF actually contains

Source: https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf (fetched 2026-11-07, HTTP 200, 6 pages, 3.1 MB). 9th edition for comparison: https://media.berginsight.com/2024/03/15160825/bi-its9-ps.pdf (HTTP 200).

| Item | 10th edition (Mar 2026) | 9th edition (Mar 2024) | Confidence |
|---|---|---|---|
| Scope definition (verbatim) | "Berg Insight's definition of ITS for public transport includes systems installed in public transport vehicles as well as at terminals, stops, depots and similar. Included are also back-office IT systems which ensure that public transport services can be planned, scheduled and managed to achieve efficient operations. An important part of ITS for public transport further comprises solutions providing travellers with updated information about routes, departure times, possible disturbances and connecting services." State-of-the-art examples: "real-time intermodal and multi-operator journey planners, automated fare collection systems using contactless cards or NFC-enabled handsets for account-based ticketing, and advanced mobility analytics software." | Identical wording | High |
| Modes named | "local and regional buses and trolleybuses, regional and suburban rail transport, metros and trams, and local waterborne passenger transport services" (as modes of public transport); **market value is stated "for buses and trams"** | Same | High |
| Market value Europe | EUR 2.55bn (2025) → EUR 3.30bn (2030), CAGR 5.3% | EUR 2.15bn (2022) → EUR 2.92bn (2027), CAGR 6.3% | High |
| Market value North America | EUR 1.22bn (2025) → EUR 1.56bn (2030), CAGR 5.0% | EUR 0.88bn (2022) → EUR 1.34bn (2027), CAGR 8.8% | High |
| Combined | EUR 3.8bn (2025) → EUR 4.9bn (2030), CAGR 5.2% (back page) | EUR 3.03bn (2022) → EUR 4.26bn (2027), CAGR 7.1% | High |
| Penetration metric | "on-board computers with GPS location functionality and wireless communications in buses and trams": Europe 90.3% (2025) → 93.9% (2030), "varying considerably between regional markets"; NA 91.9% (2025) → 94.1% (2030) | Europe 91.0% (2022) → 94.1% (2027); NA 92.5% (2022) → 97.7% (2027) | High (note NA restated down) |
| Fleet base | "registered buses and coaches in Europe and North America reached 0.85 million vehicles and 1.1 million vehicles respectively" (2023) | 0.86m / 1.0m (2021) | High |
| Demand context | ~60bn (Europe) and ~12bn (NA) PT journeys/yr pre-COVID; economic value of PT services EUR 160-175bn/yr Europe, EUR 100-115bn NA | EUR 145-155bn / EUR 80-90bn | High |
| Segment split (HW/SW/services; CAD-AVL/PIS/APC/video) | **Not in the summary.** TOC has 3.1.1 Market value forecast, 3.1.2 Regional markets, 3.1.3 Major vendors; chapter 2 lists the application taxonomy (vehicle/roadside/back-office/traveller/GNSS/network segments; planning & scheduling, CAD, traffic signal priority, depot management, passenger information, entertainment, fare payment, driver management incl. video-based driver monitoring, vehicle diagnostics, on-board security) but no values | Same structure | n/a (gap) |
| Installed base units / vendor share % | **Not in the summary** (only qualitative leadership statements) | Same | n/a (gap) |
| Vendors named as leaders | Trapeze Group (Modaxo) and INIT (both regions); Clever Devices and Conduent (NA leaders; Conduent also fare collection); Cubic, Avail (major NA shares); Siemens Mobility (software, both regions); Equans, RATP Smart Systems (France); Vix, Flowbird, Ticketer (UK); IVU (DACH); GMV, Indra, Grupo ETRA (Spain); Thales; Atron; FARA, Pilotfish, Icomera, Consat; Swarco, Kontron Transportation; OEMs Volvo, Daimler, Scania, Iveco, Gillig, New Flyer | Same list minus Icomera | High |
| Profiles | 86 aftermarket ITS providers (incl. new "International" entries Hitachi Rail, Streamax, GIRO; and Leonardo, Optibus, Kentkart, Umovity, Ridango, FAIRTIQ, Masabi, Moovit, Swiftly, Zonar, Powerfleet, CalAmp, Luminator, Accenture, Transit Technologies, TransLoc/TripSpark/Vontas (Modaxo), ZF Bus Connect); 10 OEM profiles; 30 new executive interviews; 315 pages; author Caspar Jansson; EUR 1,800 single-user licence | — | High |
| Market drivers cited | ITxPT and APTA standards programmes; smart-city initiatives; electrification; integration and fare-collection technology; cybersecurity (3.4.10); OEM-installed OBUs as a value-chain question ("What impact will standard installed OBUs from the OEMs have on the market?") | Same | High |

Trade-press addendum (IoT Business News, 24 Mar 2026, https://iotbusinessnews.com/2026/03/24/berg-insight-sees-steady-growth-for-public-transport-its-in-europe-and-north-america-through-2030/): Berg "flags structural changes around Trapeze, noting it is part of Modaxo Group and recently announced a rebrand and separation of its European businesses to ebblo, Grampian Solutions, Naviquate and Nexfeld" — relevant for the competitive-dynamics chapter (file 08).

**Implication for the top-down matrix.** Berg's EUR 3.8bn is a *public-transport ITS* number that already bundles on-board, wayside, depot and back-office spend (and probably ticketing-related on-board hardware), for buses and trams only, in two regions. It cannot be decomposed into component segments from public material; the component split must come from the GMI/MarketsandMarkets/Mordor shares already captured in file 02 (hardware ~47% of PIS; CAD USD 1.2bn and AVL USD 1.8bn global in 2025) or from the NTD capital-vs-service structure (file 16).

---

## 3. Non-US bus fleet table by country (transit-only vs registered)

Full detail, URLs and notes are in `/home/user/Project-2-/its-market-case/data/nonus_bus_fleets_by_country.csv`. Transit-only = buses operated in scheduled urban/regional public service; registered = all buses & coaches (incl. coaches, school, private, minibuses where the statistic includes them).

| Country | Transit-only buses | Year / scope | Registered buses & coaches | Transit share | New in this run? | Confidence |
|---|---|---|---|---|---|---|
| China | 658,100 (end-2024); 630,100 (end-2025, file 05) | MOT public buses & trolleybuses; BEV 74.1% (2024), NEV 87.5% (2025) | n/a (operator count) | — | 2024 bulletin fetched | High |
| India | 147,032 SRTU (FY22, file 05); ~65,000 organised city buses (CSE, file 05) | MoRTH SRTU review; DTC ~6,300 (4,538 electric, Apr-2026); Karnataka 26,054 | 14.5 lakh (2026, CSE) | ~10% | ITS section of SRTU review read | High |
| Japan | 64,570 乗合 buses, 2,434 operators (FY2023); 54,474 (FY2022); 57,914 (FY2020); JBA survey 45,416 general route + 5,393 highway + 1,691 airport (Mar-2025) | MLIT via Nihon Bus Kyokai 2025 | n/s | — | **Yes** | High (figures) / medium (transit-only definition; FY2023 series jump unexplained) |
| South Korea | Seoul 7,383 (Jan-2026, file 05); national n/s | 승합 (vans+buses) registrations 666k (end-2024, e-나라지표) | — | — | Partial | Low |
| Hong Kong | 5,868 franchised buses licensed (May-2026; 6,111 registered) | TD digest Table 4.1S | 13,830 all bus classes registered (franchised + non-franchised public 6,981 + private 858) | 42% | **Yes** | High |
| Singapore | ~5,800 public buses (file 05); 6,222 buses >70 pax (2025) | LTA Annual Vehicle Statistics 2025 | 18,357 (2025, excl. tax-exempt) | ~32% | **Yes** | Medium |
| Australia | NSW ~8,000 PT buses (file 05); 41,864 commercial-use buses (2021, incl. school/charter) | BIC | 103,760 medium+large (file 05) | — | No | Medium |
| Canada | 16,145 (2023, CUTA via file 05) | in Berg NA scope | — | — | No | Low-medium |
| Germany | 35,401 (VDV 2023, file 05) | in Berg Europe scope | 85,559 (ACEA 2024) | 41% | No | High |
| France | 17,864 UTPF networks (64% coverage → ~28k, DERIVED) | in Berg Europe scope | 94,542 | 19-29% | No | High |
| United Kingdom | ~34,600 GB local buses (England 30,558 Mar-2025) | in Berg Europe scope | 125,650 | 28% | No | High |
| Italy | ~36,000 (DERIVED from ASSTRA "ca 40,000 mezzi gomma e ferro", 140 members = 95% of urban market) | in Berg Europe scope | 101,303 | ~36% | Partial | Low |
| Spain | 14,333 in 24 OMM metropolitan areas (2024: 6,352 urban-capital + 1,283 other urban + 6,698 metropolitan) | in Berg Europe scope | 64,097 | 22% (OMM areas only) | **Yes** | High |
| Poland | 12,811 urban buses + 233 trolleybuses (31 Dec 2025; 12,512 buses in 2024); 3,389 alt-fuel (26.5%) | in Berg Europe scope; enterprises >9 staff | 109,253 (GUS 2025; 102,647 in 2024); ACEA 80,564 (2024) | 11.7% | **Yes** | High |
| Türkiye | Istanbul: IETT 4,012 + ÖHO 2,157 + Otobüs A.Ş. 544 (Wikipedia, 2012-23 vintages); national n/s | — | 713,400 incl. minibuses (EC Pocketbook 2023, file 05) | — | Partial | Low |
| Brazil | São Paulo >13,000 (SPTrans); national n/s | — | n/s (28,723 buses built 2025, file 05) | — | Partial | Medium (SP) |
| Mexico | ~8,192 buses in weekday operation in INEGI ETUP organised systems (8 metro areas, Aug-2026) + 429 CDMX trolleybuses | INEGI ETUP | 487,243 "camiones para pasajeros" (2023: público 181,109; particular 303,048; oficial 3,086) | 1.7% (formal systems only) | **Yes** | Medium |
| Chile | Santiago fleet n/s; DTPM publishes GPS positioning for the complete fleet | — | — | — | Partial | Low |
| Saudi Arabia | Riyadh Bus 842 (672 operating, 53 routes) | RCRC/SAPTCO (file 05/07), Wikipedia | — | — | No | High |
| UAE | Dubai RTA ~1,442 buses, 107 routes | Wikipedia | — | — | **Yes** | Medium |

**Non-US transit bus base (DERIVED, updated from file 05):** China 630-660k + India ~150k (SRTU; 65k organised urban) + Japan ~45-65k + EU/UK transit (DE 35.4k, FR ~28k, GB 34.6k, IT ~36k, ES ≥14.3k, PL 12.8k, other EU ~60-100k) ≈ 220-260k + Korea (≥7.4k Seoul; national unsourced, likely 35-45k) + HK/SG 11.7k + Australia 8-42k + Canada 16.1k + LatAm formal (SP 13k, Bogotá 2.2k trunk, CDMX ~8.2k, Santiago n/s) + Gulf ~3-4k → **1.25-1.5 million**, of which China is ~45-50% — consistent with the 1.3-1.6m range in file 05 but now with eight additional sourced national anchors.

---

## 4. ITS penetration by function — evidence and confidence

| Geography | AVL / CAD (on-board unit + dispatch) | Passenger information (on-board / at stops / app) | APC | CCTV / video / safety telematics | E-ticketing / AFC | Source(s) | Confidence |
|---|---|---|---|---|---|---|---|
| Spain (24 OMM areas, 2024) | **100%** of urban buses in every area with SAE "plenamente operativos"; other urban 97-100%; metropolitan 100% in most areas, 97% Barcelona, 24% Granada (2019 data) | Real-time panels at 3-51% of urban stops (Zaragoza 51%, Valencia 39%, Santander 29%, Málaga 27%, Madrid 16%, Barcelona 16%, Sevilla 10%, Jaén 0%); 0-12% of metropolitan stops; operator/ATP apps in all areas | n/s | n/s | **100%** of bus fleet with e-ticketing in all areas except Bahía de Cádiz (0%); rail modes 0-100% | OMM Informe 2024-25 Tables 26-27 | High |
| Spain — TSP | Signal-priority intersections: Barcelona 118, Gipuzkoa 82, Madrid 76, Alicante 42; most cities 0-6 | — | — | — | — | OMM Table 27 | High |
| Poland (urban transport, 2025) | n/s (no national ITS statistic; GUS reports fleet, alt-fuel share 26.5%, 82% of inventory in daily traffic) | n/s | n/s | n/s | n/s | GUS 2025 | Gap |
| Japan (route buses) | Bus-location adoption rate n/s (MLIT survey page not reachable); **digital tachograph on 80.0% of general route buses** (36,329 of 45,416 surveyed, Mar-2025; 85.9% across all bus types) | Multilingual bus-location systems promoted under the inbound-tourism programme (JBA) | n/s | **Drive recorders on 89.7% of general route buses** (40,717 of 45,416; 89.3% all types) | **88.4% cashless share of fare value** at operators with ≥30 buses (FY2023, MLIT survey); 18 operators/29 routes ran fully-cashless pilots in FY2024, continued FY2025 | Nihon Bus Kyokai 2025 (pp. 21, 41-43) | High (figures), gap (AVL) |
| South Korea | Seoul TOPIS BMS/BIS "collects, processes, and analyzes bus location information in real-time", "evaluates transportation companies", integrated with subway arrival data (all Seoul buses); BIS first deployed Bucheon Dec-2000; quasi-public bus system in 6 metro cities (Seoul 2004, Daegu 2006, Busan 2007, Daejeon, Gwangju, Incheon) | BIS/BIT stop terminals (Seoul) | n/s | n/s | n/s (T-money nationwide not re-sourced here) | TOPIS English site; ko.wikipedia | Medium (qualitative); national coverage gap |
| China | **n/s** — no MOT statistic on GPS dispatch or e-payment coverage retrievable; proxy: BEV 74.1% of 658,100 buses (end-2024), NEV 87.5% of 630,100 (end-2025); 80,100 routes; 20,400 km bus lanes | n/s | n/s | n/s | n/s | MOT 2024 bulletin; gov.cn; file 05 | Low (inferred: NEV fleets carry OEM telematics; e-payment ubiquitous in large cities — not evidenced here) |
| India | **Mandated**: VLT device + emergency button in all public service vehicles (MoRTH notification 28 Nov 2016, AIS-140); state-wise VLT monitoring platforms scheme (15 Jan 2020) Rs 463.90 crore, Rs 213.88 crore released, 33 States/UTs, 8 monitoring centres operational (Bihar, HP, Puducherry, Uttarakhand, Chhattisgarh, Mizoram, Sikkim, WB); "Strengthening ITS in Public Transport System" Rs 175 crore, FY23-26, 70:30 — covers GPS/GSM tracking, reservation/ticketing, fare integration, PIS, PMU | PIS funded under the Rs 175 crore scheme (no coverage stat) | n/s | Nirbhaya-fund CCTV/panic-button projects approved for AP, UPSRTC, BMTC, TSRTC | ETM/e-ticketing n/s | MoRTH SRTU review pp. 71-73 | High (mandate/outlays); low (actual coverage) |
| India e-bus GCC | AIS-140-grade OBU inside bus spec; **CAD/AVL, PIS, ticketing ITS are city opex outside the per-km price** | — | — | — | — | CESL Grand Challenge case study | High |
| Hong Kong | Franchised bus real-time arrival (ETA) services; Government subsidy scheme for real-time bus-arrival display panels and seats at stops | Subsidised stop panels (TD page) | n/s | n/s | Octopus (not re-sourced) | TD franchised-bus page | Medium |
| Singapore | LTA-owned fleet under Bus Contracting Model; new buses "feature passenger info display system" (LTA media replies 2020, 2022 — titles only) | On-board PIDS on new buses; 300+ stops got new PIDS (2021 release title) | n/s | n/s | n/s | LTA newsroom titles | Low-medium |
| Latin America | Santiago: DTPM publishes positioning of "la flota completa de buses" (100% GPS); São Paulo SPTrans >13,000 buses, 1,340 lines, 6.8m pax/weekday under contract; Mexico ETUP systems ~8.2k buses | n/s | n/s | n/s | bip! (Santiago), Bilhete Único (SP) not re-sourced | DTPM; SPTrans; INEGI | Medium (qualitative) |
| Gulf | Riyadh Bus 842 buses, 2,900+ stops, Darb account-based ticketing, Wi-Fi + smart ticketing (RCRC, file 07); Dubai RTA ~1,442 buses | Yes (greenfield) | n/s | CCTV on Riyadh metro cars/stations (file 07) | Darb / nol | Wikipedia; RCRC (file 07) | High (fleet), medium (ITS) |
| Türkiye (Istanbul) | IETT "Otobüsüm Nerede" real-time bus-location app (IETT site) | App | n/s | n/s | Istanbulkart (not re-sourced) | iett.istanbul | Low-medium |
| Italy, Mexico (informal), Brazil (ex-SP), Korea (national), Australia | n/s | n/s | n/s | n/s | n/s | — | Gap |

**Reading for the model.** Where a formal contracting authority exists (Spain's ATPs, Seoul, Santiago, São Paulo, Singapore, Hong Kong, Riyadh, Dubai, Japan's larger operators), on-board AVL/e-ticketing penetration is effectively 95-100% — the same saturation Berg reports for Europe/NA — and growth is replacement plus content (PIS at stops, APC, video, TSP) rather than first-time adoption. Where fleets are state-owned SRTUs or informal concessions (India outside the metro e-bus programmes, Mexico's peseros, Brazil's smaller cities, Türkiye outside Istanbul), penetration of compliance tracking may be high on paper (AIS-140) but CAD/AVL, APC and video penetration is low and funded project-by-project.

---

## 5. Per-bus ITS spend: benchmarks, cross-checks and recommended regional assumptions

### 5.1 Anchors actually sourced

| Anchor | Value | Scope | Source | Confidence |
|---|---|---|---|---|
| Berg EU+NA per *registered* bus & coach | EUR 3.77bn / 1.95m = **EUR 1,933** (Europe EUR 3,000; NA EUR 1,109) (DERIVED) | All PT ITS value incl. back-office, wayside, services; denominator incl. coaches/school buses | Berg 10th ed. | High inputs / medium ratio |
| Berg per *transit* bus (DERIVED) | Europe EUR 6.7-8.6k (0.85m × 35-45%); NA EUR 10.0-15.1k (121k incl. US cutaways / 81k full-size + Canada) | Same numerator over transit fleets (file 04/05) | Berg; NTD; CUTA | Low-medium (numerator wider than on-board ITS) |
| NTD "Communication & Information Systems" capex per full-size bus | **USD 5.8k/yr** (2025; USD 2.1k small agencies, 6.5-7.7k mid/large) | Capital only; excludes SaaS/maintenance opex; includes office IT | file 04/16 | Medium |
| London iBus2 | **~USD 2.3k per bus per year** (GBP 160m / 10 yrs / 8,797 buses) | CAD/AVL + on-board PIS incl. service | file 12 | Medium |
| LA Metro ATMS II | USD 44.7k per vehicle over 4-year contract ≈ USD 11k/yr | Cloud CAD/AVL + radio + disruption mgmt + RTPI | file 12 | Medium-high |
| Bus CAD/AVL full-system capex | USD 15-45k per vehicle every 15-20 years ≈ USD 1-3k/yr | Hardware + software + integration | file 12 | Medium-high |
| India central ITS subsidy | Rs 175 crore / 4 yrs ≈ USD 5.3m/yr ÷ 147k SRTU buses ≈ **USD 36 per bus per year** (70% share → ~USD 51 total scheme spend) (DERIVED) | GPS/GSM tracking, ticketing, PIS, PMU | MoRTH SRTU review | Medium (floor only) |
| India VLT platform (one-off) | Rs 463.90 crore (~USD 56m) for 33 States/UTs monitoring centres; device cost borne by vehicle owners | AIS-140 back-end only | MoRTH SRTU review | High |
| India e-bus GCC | ITS (tracking, ticketing) explicitly excluded from the per-km price; FAME II subsidy INR 55 lakh or 40% per 12 m bus (≈ INR 4.2-4.9/km realised) | Grand Challenge, 5,450 buses, 2022 | CESL case study | High |
| Singapore LTA, Hong Kong KMB, Riyadh Bus contract values | **Not disclosed** in reachable primary pages | — | — | Gap |

### 5.2 Recommended USD-per-transit-bus-per-year assumptions (DERIVED; analyst assumptions anchored to the rows above)

| Region block | Transit fleet basis (sourced) | Penetration assumption | Intensity USD/bus/yr (all-in ITS incl. back-office & services) | Indicative 2025 block (DERIVED) | Rationale / confidence |
|---|---|---|---|---|---|
| Europe (Berg) | ~0.85m registered; 300-380k transit | 90% OBU (Berg) | Use Berg: EUR 2.55bn (= EUR 3.0k per registered; EUR 6.7-8.6k per transit bus) | EUR 2.55bn | High (Berg) |
| North America (Berg) | 1.1m registered; ~81-121k transit | 92% OBU (Berg) | Use Berg: EUR 1.22bn (= EUR 1.1k per registered; EUR 10-15k per transit bus); cross-check NTD USD 5.8k capex + opex | EUR 1.22bn | High (Berg); medium reconciliation |
| High-income APAC (JP, KR, SG, HK, TW, AU/NZ) | JP 45-65k; KR ≥7.4k Seoul (national ~35-45k unsourced); HK 5.9k; SG 5.8k; AU 8-42k | AVL/e-ticketing 90-100%; APC/video partial (JP drive recorders 90%) | **2,500-4,000** | ~75-100k sourced buses → USD 0.19-0.40bn | Low-medium: mature, fragmented (Japan 2,434 operators, 96% SMEs) with lower price points than NA; Korea centralised BMS lowers per-bus cost |
| Gulf greenfield (KSA, UAE, Qatar) | Riyadh 842; Dubai 1,442; Doha >900 (file 05) | ~100% | **4,000-6,000** | ~3.2k buses → USD 0.013-0.019bn | Low: bundled in O&M concessions; small fleets, premium specs |
| China | 630-658k | NEV 87.5%; GPS/e-payment assumed near-universal in cities (not evidenced) | **700-1,200** | USD 0.44-0.79bn | Low: domestic vendors (Streamax, Hikvision-class pricing), no per-bus contract evidence; replacement cycle as fleet shrinks 3-4%/yr |
| India | 147k SRTU + 65k organised urban (overlapping); DTC 6.3k, Karnataka 26k | AIS-140 VLT mandated; CAD/AVL/PIS funded project-by-project (central ITS subsidy ≈ USD 36/bus/yr) | **250-600** | ~150-210k buses → USD 0.04-0.13bn | Low-medium: compliance tracking dominant; e-bus GCC excludes ITS so city procurements are incremental |
| Latin America formal systems | SP >13k; Bogotá 2.2k trunk; CDMX ~8.2k; Santiago n/s (6.8k e-buses region, file 05) | 100% GPS in Santiago; SP contracted | **1,000-2,000** (formal); ~0 (informal) | ~30-60k formal buses → USD 0.03-0.12bn | Low: fleet totals incomplete (NTU/ANTP unreachable) |
| Türkiye / Mexico / other EM (ex-formal) | Istanbul ~6.7k; MX public-service registrations 181k (mostly informal/intercity) | Low outside metros | **300-800** | n/q | Low |
| **RoW total (ex Berg regions)** | — | — | — | **~USD 0.9-1.6bn (2025)** vs Berg EU+NA ≈ USD 4.1bn | DERIVED, low confidence; China 50% of RoW |

Cross-check against Berg's EUR 1,900 per registered bus: the RoW intensities above are deliberately **below** Berg's per-registered-vehicle figure for China/India/EM (where fleets are large, prices are local and back-office scope is thin) and **above** it for high-income APAC/Gulf transit fleets (where the denominator is transit-only and scope matches Berg's bus+tram definition). Against NTD's USD 5.8k per full-size bus (capital only, large-agency-weighted), the high-income APAC assumption of USD 2.5-4k all-in is conservative and consistent with iBus2-style service pricing (USD 2.3k) plus APC/video/PIS content.

---

## 6. Findings table

| # | Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Berg scope definition (buses & trams; vehicles + terminals/stops/depots + back-office + traveller info) | verbatim quote in §2 | — | 2026 | Europe + NA | Bus/tram ITS | Berg Insight 10th ed. summary | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf | High | Fare-collection and analytics software cited as examples |
| 2 | PT ITS market Europe | 2.55 → 3.30 | EUR bn | 2025 → 2030 | Europe | Bus/tram ITS | Berg 10th ed. | same | High | CAGR 5.3% |
| 3 | PT ITS market North America | 1.22 → 1.56 | EUR bn | 2025 → 2030 | NA | Bus/tram ITS | Berg 10th ed. | same | High | CAGR 5.0%; combined 3.8 → 4.9, 5.2% |
| 4 | OBU (GPS + wireless) penetration | EU 90.3 → 93.9; NA 91.9 → 94.1 | % of buses & trams | 2025 → 2030 | EU / NA | CAD/AVL | Berg 10th ed. | same | High | 9th ed. had NA 92.5 (2022) → 97.7 (2027) |
| 5 | Registered buses & coaches | 0.85 (EU); 1.1 (NA) | million | 2023 | EU / NA | Fleet base | Berg 10th ed. | same | High | 9th ed.: 0.86 / 1.0 (2021) |
| 6 | Economic value of PT services | EU 160-175; NA 100-115 | EUR bn/yr | 2025/26 | EU / NA | Demand context | Berg 10th ed. | same | High | 60bn / 12bn journeys pre-COVID |
| 7 | Berg summary contains no HW/SW/services, application or vendor-share split and no installed-base units | n/a | — | 2026 | EU / NA | — | Berg 10th ed. TOC | same | High | Only in paid report/Excel |
| 8 | Berg 9th ed. values | EU 2.15 → 2.92 (6.3%); NA 0.88 → 1.34 (8.8%); EU pen. 91.0 → 94.1; NA 92.5 → 97.7 | EUR bn / % | 2022 → 2027 | EU / NA | Bus/tram ITS | Berg 9th ed. summary | https://media.berginsight.com/2024/03/15160825/bi-its9-ps.pdf | High | |
| 9 | Trapeze European businesses rebranded/separated to ebblo, Grampian Solutions, Naviquate, Nexfeld | — | — | 2026 | Europe | Competitive | IoT Business News citing Berg | https://iotbusinessnews.com/2026/03/24/berg-insight-sees-steady-growth-for-public-transport-its-in-europe-and-north-america-through-2030/ | Medium | |
| 10 | China public buses & trolleybuses | 658,100 (-24,500 y/y); BEV 487,500 = 74.1% (+4.7 pp) | vehicles | end-2024 | China | Bus | MOT Statistical Bulletin 2024 | https://xxgk.mot.gov.cn/jigou/zhghs/202506/t20250610_4170228.html | High | Urban rail vehicles 72,300; taxis 1.352m; 80,100 bus routes; 1.7526m route-km; 20,400 km bus lanes |
| 11 | China bus ridership | 38.67bn (+1.6%); urban rail 32.21bn (+9.6%) | trips | 2024 | China | Demand | MOT 2024 bulletin | same | High | Total urban passenger trips 106.8bn |
| 12 | China public buses (prior year) | 682,500; 81.2% NEV; 79,800 routes; 41.6bn trips | vehicles | end-2023 | China | Bus | gov.cn (MOT) | https://english.www.gov.cn/news/202408/01/content_WS66aaf8eac6d0868f4e8e9a76.html | High | |
| 13 | China public buses | 630,100; NEV 87.5% | vehicles | end-2025 | China | Bus | MOT 2025 bulletin (file 05; host unreachable this run) | https://xxgk.mot.gov.cn/jigou/zhghs/202606/t20260618_4207752.html | High (file 05) | |
| 14 | India: VLT + emergency button mandated for all public service vehicles | notification 28 Nov 2016 | — | 2016 | India | AVL (compliance) | MoRTH SRTU review 2019-22, p.72 | https://morth.gov.in/backend/documents/uploaded/Review%20of%20the%20performance%20of%20State%20Road%20Transport%20Undertakings%20for%202019-20%20to%202021-22.pdf | High | Device fitting is vehicle owner's responsibility |
| 15 | India state-wise VLT platform scheme (Nirbhaya) | Rs 463.90 crore total; Rs 213.88 crore released; 33 States/UTs; 8 monitoring centres live | INR | 2020-22 | India | AVL back-end | MoRTH SRTU review p.72-73 | same | High | Bihar, HP, Puducherry, Uttarakhand, Chhattisgarh, Mizoram, Sikkim, WB operational |
| 16 | India "Strengthening ITS in Public Transport System" scheme | Rs 175 crore; FY2022-23 to 2025-26; 70% central share (was 50%) | INR | 2022-26 | India | ITS (GPS tracking, ticketing, fare integration, PIS, PMU) | MoRTH SRTU review p.71-72 | same | High | DERIVED ≈ USD 36 per SRTU bus per year |
| 17 | India Nirbhaya safety projects (CCTV/panic) approved | AP, UPSRTC, BMTC, TSRTC | — | 2022 | India | Video/safety | MoRTH SRTU review p.72 | same | High | |
| 18 | CESL Grand Challenge: ITS excluded from GCC per-km price | "Cities will incur... Intelligent Transport systems for vehicle tracking and ticketing" | — | 2022 | India | Contract structure | CESL GC case study p.8 | https://www.convergence.co.in/public/images/electric_bus/Grand-Challenge-Case-Study-Final-Web-Version.pdf | High | 5,450 e-buses, 5 cities, 12-yr GCC, Tata Motors L1 all lots |
| 19 | FAME II e-bus subsidy | INR 55 lakh or 40% per 12 m bus (INR 45 lakh 9 m) ≈ INR 6.55/km eligibility; realised INR 35.6-41.1 lakh (4.2-4.9/km) | INR | 2022 | India | E-bus funding | CESL GC case study p.15 | same | High | Efficiency mandate 1.3 kWh/km 12 m AC |
| 20 | Delhi DTC fleet | ~6,300 buses: 4,538 electric, 1,759 CNG; 37 depots | buses | Apr-2026 | India | Bus | Wikipedia DTC | https://en.wikipedia.org/wiki/Delhi_Transport_Corporation | Medium | |
| 21 | Karnataka state + Bengaluru bus fleet | 26,054 | buses | Oct-2025 | India | Bus | Wikipedia BMTC citing News First | https://en.wikipedia.org/wiki/Bangalore_Metropolitan_Transport_Corporation | Medium | BMTC e-buses via GCC |
| 22 | Japan scheduled-route (乗合) buses and operators | 64,570 vehicles; 2,434 operators; 73.17% utilisation; 3,788,564k passengers; JPY 882.8bn revenue | mixed | FY2023 | Japan | Bus | Nihon Bus Kyokai, 日本のバス事業 2025, p.2 (MLIT data) | https://www.bus.or.jp/cms/wp-content/themes/bus/images/about/publication/2025HPUP.pdf | High | FY2022 54,474 / 2,397 ops; FY2021 56,457; FY2020 57,914; series jump FY2023 unexplained in footnotes |
| 23 | Japan JBA survey base | 45,416 general route + 5,393 highway + 1,691 airport + 28,017 charter + 4,243 contract = 84,760 surveyed buses | buses | 31 Mar 2025 | Japan | Bus | JBA 2025 p.41-43 | same | High | |
| 24 | Japan digital tachograph penetration | 36,329 / 45,416 = 80.0% general route; 72,819 / 84,760 = 85.9% all | % | Mar-2025 | Japan | Telematics (safety) | JBA 2025 p.43 | same | High | +9,776 units y/y |
| 25 | Japan drive recorder penetration | 40,717 / 45,416 = 89.7% general route; 75,659 / 84,760 = 89.3% all | % | Mar-2025 | Japan | Video | JBA 2025 p.43 | same | High | |
| 26 | Japan cashless fare share | 88.4% of fare value at operators with ≥30 buses | % | FY2023 | Japan | AFC | JBA 2025 p.21 (MLIT survey) | same | High | Fully-cashless pilots: 18 operators / 29 routes (FY2024) |
| 27 | Poland urban transport bus inventory | 12,811 buses (2024: 12,512); 233 trolleybuses; 3,007 trams; alt-fuel buses 3,389 | vehicles | 31 Dec 2025 | Poland | Bus | GUS Transport – wyniki działalności w 2025 r., Table 63 | https://stat.gov.pl/download/gfx/portalinformacyjny/pl/defaultaktualnosci/5511/9/25/1/transport_wyniki_dzialalnosci_w_2025_r.zip | High | Enterprises >9 employees; 82% of inventory in daily traffic; 735.4m veh-km; 3,333m passengers |
| 28 | Poland registered buses | 109,253 (2025); 102,647 (2024) | vehicles | 31 Dec 2025 | Poland | Fleet base | GUS Table 12 | same | High | incl. trolleybuses; 2,309 new buses registered 2025 |
| 29 | Poland intercity scheduled buses (non-urban enterprises >9 staff) | 14,192 (2024: 13,660) | buses | 2025 | Poland | Bus (intercity) | GUS Table 57 | same | High | 177 alt-fuel |
| 30 | Spain bus fleet in 24 OMM metropolitan areas | 14,333 (urban capital 6,352; other urban 1,283; metropolitan 6,698); Madrid 4,240; Barcelona 3,034; A Coruña 1,631 | buses | 2024 | Spain | Bus | OMM Informe 2024-25 Table 15 | https://observatoriomovilidad.es/wp-content/uploads/2026/03/InformeOMM-2024-25-261028.pdf | High | Metropolitan fleet -10% y/y; urban +4%; 12.1% electric, 73.4% Euro VI |
| 31 | Spain SAE (CAD/AVL) coverage | 100% urban buses in all areas; metropolitan 97-100% (Granada 24%) | % of vehicles | 2024 | Spain | CAD/AVL | OMM Table 26 | same | High | |
| 32 | Spain e-ticketing coverage | 100% of bus fleet in all areas except Bahía de Cádiz (0%) | % | 2024 | Spain | AFC | OMM Table 26 | same | High | Excludes Cercanías |
| 33 | Spain real-time stop information | 3-51% of urban stops; Madrid 803 stops (16.4%), Barcelona 1,055 (16.2%), Zaragoza 468 (51.2%) | % stops | 2024 | Spain | PIS (wayside) | OMM Table 27 | same | High | TSP intersections: Barcelona 118, Gipuzkoa 82, Madrid 76 |
| 34 | Italy ASSTRA sector data | 140 member companies; 95% urban / 75% extra-urban market share; ~40,000 vehicles (road + rail); ~5.0bn passengers; ~1.6bn km; ~100,000 staff; EUR 9.0bn production value | mixed | 2025 | Italy | Bus/rail PT | ASSTRA Dati del settore | https://www.asstra.it/centro-studi-e-dati-del-settore/dati-del-settore | Medium | Fleet reports not downloadable; ART 2025 report has no fleet count |
| 35 | Hong Kong franchised buses | 5,868 licensed / 6,111 registered (May-2026); 5,793 / 6,117 (Dec-2025) | vehicles | 2026 | Hong Kong | Bus | TD Monthly Traffic & Transport Digest Aug-2026, Table 4.1S | https://www.td.gov.hk/filemanager/en/content_5440/2608_e.pdf | High | Non-franchised public buses 6,981 reg.; private buses 858 |
| 36 | Hong Kong real-time bus arrival panels subsidy scheme | stops with seats and real-time display panels listed | — | 2026 | Hong Kong | PIS | TD franchised buses page | https://www.td.gov.hk/en/transport_in_hong_kong/public_transport/buses/index.html | Medium | |
| 37 | KMB fleet | >4,000 buses, 420+ routes (4,001 in 2021) | buses | 2021-23 | Hong Kong | Bus | Wikipedia KMB | https://en.wikipedia.org/wiki/Kowloon_Motor_Bus | Medium | 2.53m daily riders (2023) |
| 38 | Singapore bus population | 18,357 total; 6,222 with >70 passenger capacity; 6,954 in 10-15 seats | buses | 2025 | Singapore | Fleet base | LTA Annual Vehicle Statistics 2025 MVP01-10 | https://www.lta.gov.sg/content/dam/ltagov/who_we_are/statistics_and_publications/statistics/pdf/MVP01-10_Bus_by_Pax.pdf | High | Excludes tax-exempt buses |
| 39 | Singapore on-board PIDS on new buses; PIDS at 300+ stops | — | — | 2020-22 | Singapore | PIS | LTA newsroom (release titles) | https://www.lta.gov.sg/content/ltagov/en/newsroom.html | Low | Titles only |
| 40 | Seoul TOPIS BMS/BIS | real-time collection/analysis of bus location for all buses; operator evaluation; integrated with subway arrival info | — | 2026 | South Korea | CAD/AVL + PIS | TOPIS English site | https://topis.seoul.go.kr/openEngBms.do | Medium | Qualitative |
| 41 | Korea registered vehicles | 26,298k total; 승합 (vans + buses) 666k | thousand | end-2024 | South Korea | Fleet base | e-나라지표 (MOLIT) | https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1257 | High | 승합 class is not a transit denominator |
| 42 | Korea BIS history / quasi-public bus system | BIS first in Bucheon Dec-2000; quasi-public system Seoul 2004, Daegu 2006, Busan 2007, Daejeon, Gwangju, Incheon | — | — | South Korea | ITS adoption | ko.wikipedia | https://ko.wikipedia.org/wiki/%EB%B2%84%EC%8A%A4_%EC%A0%95%EB%B3%B4_%EC%8B%9C%EC%8A%A4%ED%85%9C ; https://ko.wikipedia.org/wiki/%EC%8B%9C%EB%82%B4%EB%B2%84%EC%8A%A4 | Low-medium | |
| 43 | Mexico registered buses (camiones para pasajeros) | 487,243 (público 181,109; particular 303,048; oficial 3,086); 2022: 473,111 | vehicles | 2023 | Mexico | Fleet base | INEGI VMRC open data | https://www.inegi.org.mx/contenidos/programas/vehiculosmotor/datosabiertos/vmrc_anual_csv.zip | High | CDMX público only 2,834 |
| 44 | Mexico organised urban systems fleet | ~8,192 buses in weekday operation + 429 trolleybuses (CDMX): Monterrey IMA routes 2,392; Optibús León 1,383; Qrobús 935; Metrobús 778; RTP 675; Transmetro 374; RUTA Puebla 352; Binnibus Oaxaca 278; Mexibús 256 | buses | Aug-2026 | Mexico | Bus/BRT | INEGI ETUP open data | https://www.inegi.org.mx/contenidos/programas/transporteurbano/datosabiertos/conjunto_de_datos_etup_mensual_csv.zip | High | 8 metropolitan areas only |
| 45 | São Paulo SPTrans | >13,000 buses; 1,340 lines (151 night); 6.8m passengers/weekday | mixed | 2026 | Brazil | Bus | SPTrans | https://www.sptrans.com.br/sptrans/ | High | |
| 46 | ANTP SIMOB covers bus fleet for 533 municipalities >60k inhabitants | — | — | 2014 base | Brazil | Data source | ANTP | https://www.antp.org.br/sistema-de-informacoes-da-mobilidade/apresentacao.html | Medium | Report PDFs not reachable |
| 47 | Santiago: GPS positioning data published for the complete bus fleet | 100% | — | 2026 | Chile | AVL | DTPM Datos y Servicios | https://www.dtpm.cl/index.php/homepage/sistema-de-transportes/datos-y-servicios | High | DTPM: largest e-bus fleet outside China |
| 48 | Istanbul bus fleet | IETT 4,012; 2,157 private public buses (ÖHO, 144 double-deckers); Otobüs A.Ş. 544 (2012) | buses | mixed | Türkiye | Bus | Wikipedia Public transport in Istanbul | https://en.wikipedia.org/wiki/Public_transport_in_Istanbul | Low-medium | Dated |
| 49 | IETT real-time bus app "Otobüsüm Nerede" | exists | — | 2026 | Türkiye | PIS | IETT | https://iett.istanbul/ | Medium | |
| 50 | Dubai RTA bus fleet | ~1,442 buses; 107 routes; ~7m riders/month | buses | 2023 | UAE | Bus | Wikipedia RTA | https://en.wikipedia.org/wiki/Roads_and_Transport_Authority_(Dubai) | Medium | |
| 51 | Riyadh Bus | 842 buses, 86 routes, 2,860 stops at completion; 672 buses / 53 routes operating; RATP Dev–SAPTCO; Darb ticketing | mixed | 2023-25 | Saudi Arabia | Bus/BRT | Wikipedia Riyadh Bus | https://en.wikipedia.org/wiki/Riyadh_Bus | Medium | Consistent with RCRC/SAPTCO (file 05/07) |
| 52 | Berg per registered bus & coach | EUR 1,933 (EU 3,000; NA 1,109) | EUR/vehicle/yr | 2025 | EU / NA | Intensity | DERIVED from Berg 10th ed. | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf | Medium | |
| 53 | Berg per transit bus | EU EUR 6.7-8.6k; NA EUR 10-15k | EUR/vehicle/yr | 2025 | EU / NA | Intensity | DERIVED (Berg ÷ file 04/05 fleets) | — | Low-medium | Numerator wider than on-board ITS |
| 54 | Recommended RoW intensities | APAC-high 2,500-4,000; Gulf 4,000-6,000; China 700-1,200; India 250-600; LatAm formal 1,000-2,000; other EM 300-800 | USD/transit bus/yr | 2025 | RoW | Intensity | DERIVED (analyst assumption) | — | Low | See §5.2 |
| 55 | Indicative RoW bus ITS block | ~0.9-1.6 | USD bn | 2025 | RoW ex EU/NA | Bus ITS | DERIVED | — | Low | China ~50% |

---

## 7. Gaps remaining (and the fastest route to close them)

1. **Berg component split / installed base / vendor shares** — not public; requires the paid report (EUR 1,800) or allowing researchandmarkets.com / giiresearch.com to read the list of tables (the GII listing in file 01 showed only the headline numbers).
2. **China ITS penetration statistics** (GPS dispatch coverage, mobile-payment share, smart-dispatch cities) — MOT bulletins carry no ITS line; needs WebSearch on MOT/China Urban Public Transport Association releases or the 2025 bulletin re-fetch.
3. **South Korea national transit bus count and BIS coverage** — KOSIS/MOLIT statistics are JS-only through the proxy; Seoul Solution pages (BMS case study) were unreachable; a WebSearch for MOLIT "버스정보시스템 구축 현황" would close it.
4. **Japan bus-location adoption rate** — MLIT survey page not found by URL guessing; JBA 2025 covers tachograph/drive-recorder/cashless only.
5. **Italy TPL bus fleet** — ASSTRA/ANAV reports and MIT Conto Nazionale unreachable; ART 2025 report has no fleet figure; a WebSearch for "parco autobus TPL ASSTRA" remains the route.
6. **Brazil national urban bus fleet** — NTU Anuário and ANTP SIMOB documents not reachable (NTU site is a JS app without document links).
7. **Türkiye national transit fleet** — TÜİK portal JS-only; IETT content pages HTTP 500; IBB open data blocked.
8. **Per-bus contract values outside Europe/NA** (LTA Common Fleet Management System, KMB, Riyadh Bus O&M, Transjakarta, Seoul BMS) — none disclosed on reachable primary pages; trade press (search) needed.
9. **Mexico informal fleets** (CDMX concessions) — SEMOVI unreachable; INEGI covers only formal systems.
10. **Australia transit-only fleet** — unchanged from file 05 (NSW ~8,000 only).

---

## 8. Source list (all fetched 2026-11-07 unless marked "file NN")

**Berg Insight and coverage**
- Berg Insight, Public Transport ITS in Europe and North America, 10th ed. summary: https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf
- Berg Insight, 9th ed. summary: https://media.berginsight.com/2024/03/15160825/bi-its9-ps.pdf
- Berg Insight product page (no additional data): https://www.berginsight.com/public-transport-its-in-europe-and-north-america/
- IoT Business News on 10th ed.: https://iotbusinessnews.com/2026/03/24/berg-insight-sees-steady-growth-for-public-transport-its-in-europe-and-north-america-through-2030/
- Unreachable: https://www.researchandmarkets.com/reports/4908109/public-transport-its-in-europe-and-north ; https://www.giiresearch.com/report/ber1994825-public-transport-its-europe-north-america-10th.html ; https://www.marketresearch.com/Berg-Insight-v2702/Public-Transport-Europe-North-America-44459804/ (403)

**China**
- MOT 2024 Statistical Bulletin: https://xxgk.mot.gov.cn/jigou/zhghs/202506/t20250610_4170228.html
- gov.cn (MOT, Aug 2024): https://english.www.gov.cn/news/202408/01/content_WS66aaf8eac6d0868f4e8e9a76.html
- MOT 2025 bulletin (file 05; unreachable this run): https://xxgk.mot.gov.cn/jigou/zhghs/202606/t20260618_4207752.html

**India**
- MoRTH, Review of the performance of SRTUs 2019-20 to 2021-22: https://morth.gov.in/backend/documents/uploaded/Review%20of%20the%20performance%20of%20State%20Road%20Transport%20Undertakings%20for%202019-20%20to%202021-22.pdf
- CESL, Grand Challenge for Electric Bus Deployment — Outcomes and Lessons: https://www.convergence.co.in/public/images/electric_bus/Grand-Challenge-Case-Study-Final-Web-Version.pdf
- ITDP, Rollout of Electric Buses in India (no ITS data): https://itdp.org/wp-content/uploads/2022/05/Rollout-of-Electric-Buses-in-India_Vaishali-Singh.pptx.pdf
- Wikipedia DTC: https://en.wikipedia.org/wiki/Delhi_Transport_Corporation ; Wikipedia BMTC: https://en.wikipedia.org/wiki/Bangalore_Metropolitan_Transport_Corporation
- CSE/CITIES Forum (file 05): https://www.cseindia.org/urban-bus-transport-systems-in-dire-straits-in-india-says-new-cse-cities-forum-study-13205

**Japan**
- Nihon Bus Kyokai, 日本のバス事業 2025: https://www.bus.or.jp/cms/wp-content/themes/bus/images/about/publication/2025HPUP.pdf (publications index: https://www.bus.or.jp/about/publication/)
- MLIT page reached was 自家用有償旅客運送 (not bus-location): https://www.mlit.go.jp/jidosha/jidosha_tk3_000012.html

**South Korea**
- Seoul TOPIS (English) BMS: https://topis.seoul.go.kr/openEngBms.do ; home: https://topis.seoul.go.kr/eng/english.jsp
- e-나라지표 자동차등록현황: https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1257
- ko.wikipedia 버스 정보 시스템: https://ko.wikipedia.org/wiki/%EB%B2%84%EC%8A%A4_%EC%A0%95%EB%B3%B4_%EC%8B%9C%EC%8A%A4%ED%85%9C ; 시내버스: https://ko.wikipedia.org/wiki/%EC%8B%9C%EB%82%B4%EB%B2%84%EC%8A%A4
- Unreachable: https://www.ktdb.go.kr/ (redirect only), https://stat.molit.go.kr/, https://kosis.kr/statHtml/statHtml.do?orgId=116&tblId=DT_MLTM_5498&language=en (JS), https://www.seoulsolution.kr/en/content/bus-management-system-bms, https://www.bus.or.kr/

**Hong Kong / Singapore**
- TD Monthly Traffic and Transport Digest Aug-2026: https://www.td.gov.hk/filemanager/en/content_5440/2608_e.pdf ; franchised buses page: https://www.td.gov.hk/en/transport_in_hong_kong/public_transport/buses/index.html
- Wikipedia KMB: https://en.wikipedia.org/wiki/Kowloon_Motor_Bus
- LTA Annual Vehicle Statistics 2025, Bus population by passenger capacity: https://www.lta.gov.sg/content/dam/ltagov/who_we_are/statistics_and_publications/statistics/pdf/MVP01-10_Bus_by_Pax.pdf ; by age: https://www.lta.gov.sg/content/dam/ltagov/who_we_are/statistics_and_publications/statistics/pdf/MVP01-3-4_Bus_by_age.pdf ; newsroom: https://www.lta.gov.sg/content/ltagov/en/newsroom.html

**Europe (new)**
- GUS, Transport – wyniki działalności w 2025 r. (tables zip): https://stat.gov.pl/download/gfx/portalinformacyjny/pl/defaultaktualnosci/5511/9/25/1/transport_wyniki_dzialalnosci_w_2025_r.zip ; EN PDF: https://stat.gov.pl/download/gfx/portalinformacyjny/en/defaultaktualnosci/3323/6/21/1/transport_activity_results_in_2025.pdf ; Road transport in Poland 2024-2025: https://stat.gov.pl/download/gfx/portalinformacyjny/en/defaultaktualnosci/3323/5/9/1/road_transport_in_poland_in_the_years_2024_and_2025.pdf
- Observatorio de la Movilidad Metropolitana, Informe 2024-25: https://observatoriomovilidad.es/wp-content/uploads/2026/11/InformeOMM-2024-25-261028.pdf ; ticketing monograph: https://observatoriomovilidad.es/wp-content/uploads/2026/03/2025-V-Monografia-Ticketing-web.pdf
- ASSTRA Dati del settore: https://www.asstra.it/centro-studi-e-dati-del-settore/dati-del-settore
- ANAV report Sept-2026 (no fleet data): https://anav.it/wp-content/uploads/2026/09/anav-report-settembre.pdf
- ART Relazione annuale 2025 (no fleet count): https://www.autorita-trasporti.it/wp-content/uploads/2025/09/2025-Relazione-Art.pdf
- ISTAT Ambiente urbano (2016, not used): https://www.istat.it/wp-content/uploads/2016/11/Ambiente-Urbano.pdf
- Europe fleet rows reused from file 05: ACEA Vehicles on European Roads 2026 https://www.acea.auto/files/ACEA_Report-%E2%80%93-Vehicles_on_European_roads_2026.pdf ; VDV Statistik 2023 https://www.vdv.de/vdv-statistik-2023.pdfx ; UTPF https://www.utpf-mobilites.fr/documentation/le-parc-des-vehicules-des-services-urbains-au-1er-janvier-2024 ; DfT https://www.gov.uk/government/statistics/annual-bus-statistics-year-ending-march-2025/annual-bus-statistics-year-ending-march-2025 ; EC Pocketbook mirror https://www.its-knihovna.cz/CDV/media/ITS-Knihovna/Projekty%20a%20studie/eu-transport-in-figures-MI0125038ENN.pdf

**Latin America**
- INEGI VMRC open data: https://www.inegi.org.mx/contenidos/programas/vehiculosmotor/datosabiertos/vmrc_anual_csv.zip (programme page https://www.inegi.org.mx/programas/vehiculosmotor/)
- INEGI ETUP open data: https://www.inegi.org.mx/contenidos/programas/transporteurbano/datosabiertos/conjunto_de_datos_etup_mensual_csv.zip (programme page https://www.inegi.org.mx/programas/transporteurbano/)
- SPTrans: https://www.sptrans.com.br/sptrans/
- ANTP SIMOB: https://www.antp.org.br/sistema-de-informacoes-da-mobilidade/apresentacao.html
- DTPM Santiago: https://www.dtpm.cl/index.php/homepage/sistema-de-transportes/datos-y-servicios ; https://www.dtpm.cl/index.php/homepage/sistema-de-transportes/buses
- Wikipedia Transportation in Mexico City: https://en.wikipedia.org/wiki/Transportation_in_Mexico_City
- Unreachable: https://www.ntu.org.br/novo/ (JS app), https://semovi.cdmx.gob.mx/, https://www.c40.org/ (403), https://ebusradar.org/ (JS app, no data in HTML)

**Gulf / Türkiye**
- Wikipedia Riyadh Bus: https://en.wikipedia.org/wiki/Riyadh_Bus ; Wikipedia RTA Dubai: https://en.wikipedia.org/wiki/Roads_and_Transport_Authority_(Dubai)
- RCRC / SAPTCO (file 05/07): https://www.rcrc.gov.sa/en/projects/riyadh-public-transport-project-2/ ; https://saptco.com.sa/pdf/profiles/PTC.pdf
- IETT: https://iett.istanbul/ ; Wikipedia Public transport in Istanbul: https://en.wikipedia.org/wiki/Public_transport_in_Istanbul ; Wikipedia İETT: https://en.wikipedia.org/wiki/%C4%B0ETT
- Unreachable: https://veriportali.tuik.gov.tr/ (JS), https://data.ibb.gov.tr/

**US/NA intensity anchors (earlier files)**
- NTD Capital Expenses by Capital Use (file 04/16): https://datahub.transportation.gov/d/fphd-jyyj
- Contract benchmarks incl. iBus2 and LA Metro ATMS II (file 12): `/home/user/Project-2-/its-market-case/research/12_contract_benchmarks.md` and `/home/user/Project-2-/its-market-case/data/contract_benchmarks.csv`
