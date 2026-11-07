# 32 — Gap fill: bus-ITS vendor revenue, mix and ownership from statutory registries and rating-agency disclosures

**Prepared:** 7 November 2026 (research sub-agent). **Purpose:** replace the "guesswork" behind the competitive section's share arithmetic with filed numbers. The brief named ~15 bus-ITS vendors for which the case had no hard revenue (Trapeze/Modaxo, Cubic CTS, Luminator, Vix, Ticketer, Flowbird, Hanover, Equans, GMV, Avail, plus the Nordic and German specialists) and asked for revenue, growth, EBIT, geography, hardware/software/services mix, employees, ownership, a fare-collection flag, and an estimate of each vendor's share of Berg Insight's EUR 1.22bn North America and EUR 2.55bn Europe pools (2025, bus+tram, fare-inclusive — see file 17).

**What was done (read before using the numbers).** Twenty-one UK Companies House filings were downloaded as PDFs and OCR-processed (the accounts are 1-bit scans with no text layer; tesseract 5.3.4 at 200 dpi — figures were read from the KPI tables and notes, and cross-checked where two statements of the same number exist in a filing). Nordic registry pages (allabolag.se for Sweden, proff.no for Norway) were read directly, including the five-year series embedded in allabolag's page data. SEC filings (Conduent 10-K FY2021/FY2023/FY2024/FY2025, 10-Q Q3-2026, the 21 May 2026 and 6 Oct 2026 8-Ks with the Modaxo pro forma; SPX 10-K FY2025; Mobileye 10-K FY2025; Via 10-K FY2025) were fetched from sec.gov with a declared user-agent and read as text. Rating-agency coverage of Cubic was reconstructed from the Prospect News issuer index (full chronology of Moody's/Fitch actions 2021–Oct 2026), Moody's 15 Apr 2021 rating action (full text via Yahoo Finance), Octus (Fitch 13 Aug 2026 downgrade to CC, quoted), S&P/LCD via Yahoo Finance and Mobility Payments. Indra's FY2025 release, GMV's 2025 annual report, Bouygues' FY2025 release (Equans) and Constellation's Q4-2025 financial report were read in full. **Not reachable:** fitchratings.com and moodys.com research pages (JavaScript-only; six guessed RAC URLs all returned the app shell), northdata.com (rate-limited after the first request), bundesanzeiger/unternehmensregister (not attempted after northdata failed), datacvr.virk.dk (blocked), audaxprivateequity.com and verif.com (not in the session allow-list), krak.dk/cbonds (JS challenge). The WebSearch budget for the turn ran out before the HaCon/DILAX/Vix-group/Ticketer searches, so those rely on the filings themselves. D&B/ZoomInfo-type figures are used **only** where no filing exists (Avail, Passio, ETA, Swiftly, Optibus global, Spare, GIRO, Luminator group) and are labelled low confidence; two calibration cases show how wrong they can be (Vix: aggregator USD 226m vs filed USD 81.5m; Hanover: aggregator USD 53–60m vs filed GBP 92.8m).

**Confidence key:** high = primary filing/registry read directly, or two independent sources agree; medium = single secondary source or primary source with a scope caveat; low = aggregator estimate or derived with stated assumptions. Every derived figure shows its formula. FX = ECB reference rates of 6 Nov 2026 (EUR 1 = USD 1.1165, GBP 0.83415, SEK 11.026, NOK 10.526, DKK 7.4752, CHF 0.9143, AUD 1.625, CAD 1.5705; https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml).

**Data files written:** `/home/user/Project-2-/its-market-case/data/vendor_revenue_statutory_registry.csv` (51 vendor/entity rows with every field below), `/home/user/Project-2-/its-market-case/data/vendor_share_berg_pools_2025.csv` (42 pool-attribution rows with the assumption behind each), `/home/user/Project-2-/its-market-case/data/conduent_transit_solutions_revenue_2019_2025.csv`.

---

## 1. Key takeaways

1. **The UK registry alone yields hard revenue for nine of the brief's vendors, and it reshuffles the picture.** Cubic Transportation Systems Ltd turned over **GBP 177.1m** in FY Sep-2025 (−3%; operating profit GBP 15.4m, 9% margin vs 20% a year earlier; 1,101 staff) and discloses that the TfL Revenue Collection Contract is ~50% of its revenue, was **lost in the July 2025 re-tender** (contract ends Aug-2026 plus up to 18 months' transition, legal action ongoing) and that backlog fell from GBP 259m to GBP 157m. Hanover Displays' group turnover is **GBP 92.8m** (2025, +27.8% after +28.3% and +22.6%; operating profit GBP 15.7m, 17%; 362 staff; gross margin 58%) — the fastest-growing hardware name in the set and far larger than aggregators suggest. Vix Technology's group (Vix AFC Ltd, reports in USD) is **USD 81.5m** (FY Jun-2025, −2.6%; EBITDA USD 0.9m; LBT −USD 7.9m; 294 staff; Europe 67% / North America 26% / APAC 7%), controlled by Duncan Saville's ICM Mobility Group — one-third of the USD 226m that ZoomInfo/RocketReach publish. Ticketer (Corvia Ltd) is **GBP 26.4m** (−2%; ARR GBP 16.3m, +13%; adjusted EBITDA GBP 6.4m, +45%; 87 staff; owned by Tenzing Private Equity since 2018). Flowbird Transport Ltd (ex-Parkeon/Wayfarer, now Arrive AS) is **GBP 23.0m** (−8%; EBITDA GBP 5.2m; 162 staff). Masabi Group is **GBP 41.9m** (+12%; recurring GBP 31.0m, 74%; 90% North America; near break-even). Trapeze's two UK companies total **GBP 27.4m** (Trapeze Group (UK) GBP 11.1m FY2024, 98 staff; Trapeze ITS U.K. GBP 16.4m FY2025, +36%, 55 staff, 75% of sales to the rest of Europe/Ireland) and both name Modaxo Europe A/S (Denmark) → Constellation Software as the chain of control. Icomera UK is GBP 21.9m (FY2024, −7%, 94 staff, ~80% share of connected UK rail vehicles). Optibus' UK-headed sub-group is USD 23.6m (2024, 182 staff, operating loss). GMV NSL Ltd (GBP 11.6m) is a space-engineering business, not ITS.

2. **Conduent's transit unit is now fully disclosed, 2019–2025, from the 10-Ks and the Modaxo pro forma.** Transit Solutions revenue: USD 254m (2019) → 248 → 262 → 226 → 237 → **341 (2024) → 371 (2025, +8.8%)**; the 6 Oct 2026 8-K pro forma removes USD 371m / 341m / 237m of revenue and USD 298m of 2025 cost of services, USD 41m SG&A and USD 14m D&A — i.e. the unit ran at roughly a **USD 18m pre-tax loss (−5%) in 2025**. Modaxo paid USD 164m base price (USD 140m cash at close, holdbacks of 10 + 12, USD 15m cash transferred) — **0.44x revenue**. The Transportation segment including tolling lost USD 12m (2025) and USD 25m (2024) at segment-profit level.

3. **Cubic's post-LBO numbers remain undisclosed, but the rating chronology is now complete and damning.** Prospect News' issuer index lists sixteen agency actions on Atlas CC Acquisition Corp./Cubic: Moody's B3 (Apr-2021, leverage >9x on USD ~2bn rated debt, LTM revenue USD 1.47bn, ~60% transit) → cuts Nov-2022 and Oct-2024 → term loan C corrected to Caa2 (Jul-2025) → default designation appended (Aug-2025 and again Feb-2026) → loans rated B1/Caa2/Ca (Aug-2025) → "lowers Cubic" again on 26 Oct 2026; Fitch B (Apr-2021) → negative outlook (Jul-2023) → cut (Feb-2025) → CCC- (9 Jul 2025) → RD/upgrade to CCC+ with new loans B+/CCC+/CCC- (Aug-2025) → action (9 Feb 2026) → **CC on 13 Aug 2026** after the July 2026 interest deferral on the second-out term loans B and C, "the third straight quarterly deferral", treated as a distressed debt exchange; S&P B- → CCC+ (Feb-2025, "onerous debt burden", ~USD 2bn of debt) → **SD on 2 Feb 2026**. The July 2025 recap (USD 275m liquidity, USD 170m sponsor equity, USD 370m debt reduction) was followed in Sep-2026 by a USD 175m out-of-court injection (USD 100m lenders, USD 75m Veritas). The only hard CTS data point is the UK subsidiary above (GBP 177m, losing its anchor contract).

4. **Nordic registries give filed revenue for the whole Scandinavian cluster** (EUR at 6 Nov 2026 rates): Icomera AB parent SEK 439.6m / EUR 39.9m (2025, −10%; 108 staff; includes intra-group sales), Consat Telematics SEK 278.9m / EUR 25.3m (+37%; 104 staff; a group block of SEK 370.7m also appears), LTG Sweden AB — the former Mobitec AB, now Luminator's Nordic arm — SEK 279.5m / EUR 25.4m (FY Feb-2025, +63%; only 28 staff), AB Thoreb SEK 141.3m / EUR 12.8m, Hogia Public Transport Systems + Products SEK 171.7m / EUR 15.6m, Pilotfish SEK 38.3m / EUR 3.5m, FARA AS (Modaxo) NOK 222.1m / EUR 21.1m (2024, +17%, EBIT ≈ 0, negative equity), Saga Tenix NOK 22.6m / EUR 2.1m (loss-making). Trapeze Group Sweden AB is dormant; the Nordic Trapeze business runs through Modaxo Europe A/S (Aarhus; DKK 47.5m revenue, 36–45 staff per CVR aggregators — low confidence because datacvr was blocked).

5. **Ownership is settled for every name in the brief except one nuance.** Luminator Technology Group is owned by **Audax Private Equity with BNP Paribas Développement, acquired from Levine Leichtman on 7–8 April 2014** (LLCP release; Mergr); no source links Gemspring Capital to Luminator (Gemspring's 2026 deals are GoldenSource, Comoto, TRG, Vista), and PitchBook's "Blackstone" tag is unconfirmed. Vix = ICM Mobility Group (Duncan Saville, ultimate controlling party per the FY2025 accounts). Ticketer = Tenzing (via Ishtar Topco/Bidco). Flowbird = Arrive AS (ex-EasyPark; Vitruvian/Verdane/Searchlight). Hanover = founder-director D G Williams. Trapeze/FARA/Conduent-transit = Modaxo/Constellation. Clever Devices = Hitachi Rail (closed 1 Jul 2026, >USD 220m projected 2026 revenue, 600+ staff). Icomera = Equans/Bouygues. Avail = employee-owned (ESOP). Masabi = no single controlling party (Accel-KKR growth round 2022).

6. **Mix evidence by vendor type is now filed, not inferred.** Fare/ticketing integrators are services-heavy: Cubic UK goods 20% / services 80% (77% recognised over time); Vix group systems 12% / services 23% / goods 41% / other 24%; Ticketer goods 38% / services 62% with ARR = 62% of revenue; Masabi recurring 74%. Software houses: Trapeze Group (UK) gross margin 88%, revenue "typically paid annually in advance"; IVU 51.8% recurring (file 08). Hardware: Hanover gross margin 58%, Flowbird UK 32%, Trapeze ITS UK 48%. Conduent transit cost of services = 80% of revenue. These support a component split for the model in which fare and systems-integration revenue is 60–80% services/recurring, scheduling software 50–90% recurring, and display/on-board hardware 100% goods with 30–60% gross margins.

7. **Share arithmetic (Section 5): North America is concentrated, Europe is not.** With documented in-scope factors and regional splits, the 18 identifiable North American vendors absorb **92% of Berg's EUR 1.22bn** NA pool, top-5 = **64%** and top-10 = **84%**; consolidating Modaxo's two franchises (Trapeze legacy est. EUR 251m + Conduent transit EUR 151m = **EUR 402m, 33%**) lifts the owner-level top-5 to **71%** (Modaxo, Clever/Hitachi 13%, INIT 9%, Cubic NA ~9%, Luminator ~7%). In Europe the 24 identifiable vendors cover only **40% of the EUR 2.55bn** pool; the largest (INIT EUR 156m) is **6%**, Trapeze/Modaxo Europe ~5%, IVU ~4.5%, Hanover ~3%, Flowbird ~2.5%; top-5 = **21%**, top-10 = **30%**, leaving a EUR 1.5bn residual for Equans/Ineo, RATP Smart Systems, Siemens Mobility, Kontron, Swarco, Hitachi (ex-Thales ticketing), Conduent Europe, Ridango, Kentkart, national integrators and OEM telematics. The NA allocation hitting 92% with only 18 names is itself a cross-check: it says either the Trapeze-legacy and Cubic assumptions (both low confidence) are on the high side or Berg's NA number excludes more mega-fare revenue than assumed — the model should carry Trapeze NA at USD 250–450m and Cubic NA in-scope at 15–35%.

8. **Growth and profitability are bifurcated by business model.** Growing at double digits: Hanover (+28%), Trapeze ITS UK (+36%), Vix UK (+15%), Masabi (+12%), Consat (+37%), LTG Sweden (+63%), FARA (+17%), Conduent transit (+9%), INIT NA (+34%, file 08). Flat or shrinking: Cubic UK (−3%), Ticketer (−2%, but ARR +13%), Flowbird UK (−8%), Icomera UK (−7%), Icomera AB (−10%), Vix group (−3%). Operating margins: Hanover 17%, Flowbird UK 15%, Ticketer 13% (adj. EBITDA 24%), Trapeze ITS UK 10%, Cubic UK 9%, Vix UK 8%, Consat 7%, Hogia 7%, Trapeze UK 5%, Icomera UK 4%; loss-making: Vix group, Optibus UK group (−12%), Conduent transit (≈−5%), Saga Tenix, Pilotfish (break-even), Masabi (−1%).

9. **Aggregator calibration.** Where a filing exists, modelled aggregator revenue was wrong by −45% (Hanover, Datanyze/Growjo) to +178% (Vix, ZoomInfo/RocketReach); registry-derived aggregators (Endole for Hanover and Masabi Ltd) matched the filings. Treat the Avail (USD 24.5m), GIRO (USD 115.5m, but Owler/Glassdoor say 25–100m), Swiftly (USD 8–12m, inconsistent with 145–181 staff), Optibus (USD 59.6m), Spare (USD 25.7m, 2023), Passio (USD 3–25m) and ETA (USD 5.6m) numbers as ±50% at best.

10. **For the investment thesis:** (a) the two largest NA franchises changed hands in 2026 at very different prices — Conduent transit at 0.44x revenue (loss-making, fare-heavy, 2,000 staff) versus Clever Devices (undisclosed, profitable CAD/AVL leader) — so a new entrant's exit multiple depends on mix, not just scale; (b) the UK shows that fare-collection incumbents can lose anchor contracts (Cubic/TfL) while subscription models (Ticketer ARR +13%, Masabi recurring +9%) hold; (c) Europe's EUR 1.5bn unallocated long tail is the entry space — no European vendor exceeds 6% of the pool; (d) hardware is not dead — Hanover's 28% growth and 17% margin on destination signs is the best filed P&L in the set.

---

## 2. Findings table

| # | Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Cubic Transportation Systems Ltd turnover | 177,070 (183,148 prior) | GBP k | FY to 30 Sep 2025 | UK 162,171 / Europe 3,575 / RoW 11,324 | Fare collection + ITS/TMS (adjacent-fare heavy) | Companies House full accounts (OCR) | https://find-and-update.company-information.service.gov.uk/company/01381707/filing-history | high | −3%; goods 34,739 / services 142,331; over time 136,363 |
| 2 | Cubic TS Ltd operating profit / PBT | 15,392 / 15,445 (37,454 / 36,040) | GBP k | FY2025 | UK | as above | same | same | high | Op margin 9% vs 20%; backlog 157,023 vs 259,135 |
| 3 | Cubic TS Ltd employees | 1,101 (1,089) | heads | FY2025 | UK | as above | same | same | high | Wages 57,659k |
| 4 | TfL Revenue Collection Contract share and loss | ~50% of revenue; lost Jul-2025; ends Aug-2026 + ≤18-month transition | — | 2025–27 | London | Fare collection | same | same | high | Legal action on procurement ongoing |
| 5 | Trapeze Group (UK) Ltd turnover | 11,053 (10,895; 2022: 9,170) | GBP k | FY2024 | UK 10,170 / rest of Europe 883 | Scheduling/ops software | Companies House (OCR) | https://find-and-update.company-information.service.gov.uk/company/04160790/filing-history | high | EBITDA 1,765k; op profit 525k; 98 staff (120); parent Modaxo Europe A/S |
| 6 | Trapeze ITS U.K. Ltd turnover | 16,353 (11,992; 2023: 7,108) | GBP k | FY2025 | UK 371 / rest of Europe 12,306 / RoW 3,676 | AVL/RTPI software | Companies House (OCR) | https://find-and-update.company-information.service.gov.uk/company/06960657/filing-history | high | +36.4%; EBITA 1,616k; 55 staff; NTA Ireland and LTA Singapore roll-outs |
| 7 | Vix AFC Ltd group revenue | 81.5 (83.6) | USD m | FY to 30 Jun 2025 | Europe 54.9 / NA 20.9 / APAC 5.7 | AFC + ITS/RTPI (adjacent-fare) | Companies House group accounts (OCR) | https://find-and-update.company-information.service.gov.uk/company/02649163/filing-history | high | LBT −7.9; EBITDA 0.9 (underlying ~3.0); 294 staff; parent ICM Mobility Group (Duncan Saville) |
| 8 | Vix revenue mix | Systems 10.1 / services 18.5 / goods 33.6 / other 19.3 | USD m | FY2025 | Global | as above | same | same | high | Unsatisfied performance obligations 186.6 (154.3 services) |
| 9 | Vix Technology UK Ltd revenue | 30,593 (26,657) | GBP k | FY Jun-2025 | UK 30,326 | Fare (Pulse) + RTI/ITS (Beacon) | Companies House (OCR) | https://find-and-update.company-information.service.gov.uk/company/03039051/filing-history | high | +14.8%; op profit 2,511k (8%); 130 staff; TfL Countdown 3 RTPI win Mar-2025 |
| 10 | Corvia Ltd (Ticketer) turnover / ARR | 26,353 (26,865) / 16.3 (14.4) | GBP k / GBP m | FY2025 | UK 100% | Bus ETMs (adjacent-fare) + fleet/RTPI | Companies House (OCR) | https://find-and-update.company-information.service.gov.uk/company/07011600/filing-history | high | Goods 10,058 / services 16,295; adj. EBITDA 6.4m (4.4m); 87 staff; 400+ customers; ultimate parent Tenzing PE 1 GP LLP |
| 11 | Hanover Displays group turnover | 92,819 (72,608; 2023: 56,611) | GBP k | FY2025 | Not disclosed (UK, FR, ES, DE, IT, AU, HK, US) | PIS hardware | Companies House group accounts (OCR) | https://find-and-update.company-information.service.gov.uk/company/01876684/filing-history | high | +27.8%; op profit 15,727k; gross margin 58.2%; 362 staff; controlled by D G Williams |
| 12 | Flowbird Transport Ltd revenue | 22,978 (24,875) | GBP k | FY2025 | UK 16,056 / Europe 3,787 / AU 1,996 / US 897 / RoW 242 | Bus ticketing (adjacent-fare) | Companies House (OCR) | https://find-and-update.company-information.service.gov.uk/company/01232487/filing-history | high | −8%; EBITDA 5,197k; 162 staff; parent Wayfarer Group → Arrive AS (Norway) |
| 13 | Masabi Group revenue | 41,856 (37,463) | GBP k | FY2025 | NA 37,591 / RoW 4,265 | Fare SaaS (adjacent-fare) | Companies House group accounts (OCR) | https://find-and-update.company-information.service.gov.uk/company/04260927/filing-history | high | Recurring 30,977 (+8.7%); LBT −468; 103 contracts; no single controlling party |
| 14 | Icomera UK Ltd turnover | 21,872 (23,453) | GBP k | FY2024 | UK 21,090 | Connectivity (rail-heavy) | Companies House (OCR) | https://find-and-update.company-information.service.gov.uk/company/06089258/filing-history | high | Op profit 901k; 94 staff; ultimate parent Bouygues |
| 15 | Optibus Transportation Ltd group turnover | 23,590 (21,860) | USD k | FY2024 | UK 10,435 / Europe 8,230 / S. America 4,805 / Asia 120 | Scheduling SaaS | Companies House group accounts (OCR) | https://find-and-update.company-information.service.gov.uk/company/11494674/filing-history | high | Operating loss −2,706k; 182 staff; excludes Israel/NA |
| 16 | GMV NSL Ltd turnover | 11,605 (10,379) | GBP k | FY2025 | UK 3,609 / Europe 7,961 | Space engineering (not ITS) | Companies House (OCR) | https://find-and-update.company-information.service.gov.uk/company/03645072/filing-history | high | Exclude from bus-ITS pools |
| 17 | INIT UK / Omnibus Solutions / Optibus Ltd / Ticketer Ltd / Luminator UK / Swiftly Ltd | No P&L filed (small/dormant/new) | — | FY2025 | UK | — | Companies House | https://find-and-update.company-information.service.gov.uk/company/07234994 ; /03609069 ; /10339585 ; /07006670 ; /16382962 ; /17497874 | high | Ticketer Ltd dormant; Clever Devices UK (14595806) dissolved Jun-2024 |
| 18 | Icomera AB (parent) net sales | 439,569 (489,937) | SEK k | FY2025 | Sweden parent | Connectivity | allabolag.se | https://www.allabolag.se/foretag/icomera-ab/g%C3%B6teborg/internet-konsulter-operat%C3%B6rer/2K1OR8WI5YFHL | high | 2021–25: 341.3 / 373.7 / 450.5 / 489.9 / 439.6; 108 staff; EBIT 9.5m |
| 19 | Consat Telematics AB net sales | 278,936 (204,158) | SEK k | FY2025 | Sweden | CAD/AVL, PIS | allabolag.se | https://www.allabolag.se/foretag/consat-telematics-ab/partille/konsulter/2K2QFETI5YF3I | high | 2021–25: 178.3 / 191.0 / 242.1 / 204.2 / 278.9; EBIT 20.5m; 104 staff (55); group block 370.7m |
| 20 | LTG Sweden AB (ex-Mobitec AB, Luminator) net sales | 279,528 (171,604) | SEK k | FY to Feb-2025 | Sweden/Nordics | PIS displays | allabolag.se | https://www.allabolag.se/foretag/ltg-sweden-ab/herrljunga/elektronik-komponenter/2K1J9NTI5YDXD | high | FY21–25: 186.5 / 173.3 / 134.1 / 171.6 / 279.5; EBIT −20.7m; 28 staff; parent DRI Europa AB |
| 21 | AB Thoreb net sales | 141,272 (135,405) | SEK k | FY2025 | Sweden | On-board computers/CAD | allabolag.se | https://www.allabolag.se/foretag/ab-thoreb/v%C3%A4stra-fr%C3%B6lunda/transportf%C3%B6rmedling/2JZH7VXI5YI2J | high | 2021–25: 118.6 / 111.2 / 148.8 / 135.4 / 141.3; 31 staff; wider group block 271.3m / 106 staff |
| 22 | Hogia Public Transport Systems AB / Products AB net sales | 113,074 (110,328) / 58,641 (64,477) | SEK k | FY2025 | Sweden/Nordics | PT scheduling/RTPI | allabolag.se | https://www.allabolag.se/foretag/hogia-public-transport-systems-aktiebolag/stenungsund/datautveckling-systemutveckling-programutveckling/2K1CUV4I5YDOJ | high | PTS 2021–25: 84.9 / 92.3 / 101.9 / 110.3 / 113.1; 25 + 38 staff |
| 23 | Pilotfish Networks AB net sales | 38,286 (78,588 for 15-month FY2024) | SEK k | FY2025 | Sweden | Vehicle gateways | allabolag.se | https://www.allabolag.se/foretag/pilotfish-networks-ab/g%C3%B6teborg/internet-konsulter-operat%C3%B6rer/2K1N9AYI5YFHL | high | 12 staff |
| 24 | FARA AS (Modaxo) operating revenue | 222,113 (190,559) | NOK k | FY2024 | Norway | Ticketing + RTPI | proff.no | https://www.proff.no/selskap/fara-as/trondheim/dataprogramvare-og-utvikling/IGCW3PJ009O | high | 2020–24: 202.4 / 182.5 / 153.0 / 190.6 / 222.1; EBIT 984k; equity −14.5m; 41 staff |
| 25 | Saga Tenix AS operating revenue | 22,571 | NOK k | FY2025 | Norway | Telematics | proff.no | https://www.proff.no/selskap/saga-tenix-as/blomsterdalen/tekniske-konsulenter/IGFHJ5Q01OU | high | EBIT −12,845k; 11 staff |
| 26 | Modaxo Europe A/S (ex-Trapeze Group Europe) revenue / staff | 47,522 / 45 (gross profit 29,698 / 36 staff per krak) | DKK k | n/d | Denmark | Trapeze European holding/sales | degulesider.dk / krak.dk (CVR 28655843) | https://www.degulesider.dk/trapeze+group+aarhus+v/66529710/firma | low | Year not stated; datacvr blocked |
| 27 | Trapeze Germany GmbH (Berlin) revenue | 9,755 (13,032) | EUR k | FY2023 (FY2022) | Germany | ITS software | implisense (Bundesanzeiger extract, via search summary) | https://implisense.com/en/companies/trapeze-germany-gmbh-berlin-DEDPK2MDTK54 | medium | Trapeze Group Deutschland GmbH (Braunschweig) now Modaxo Group Germany GmbH |
| 28 | Trapeze Switzerland GmbH headcount | ~250 | heads | 2025 | Neuhausen (European HQ) | ITS | SIG Areal tenant profile / jobs.ch | https://www.sigareal.ch/de/gewerbe/mieterportraits/trapeze-switzerland-gmbh/ | medium | No revenue published |
| 29 | MENTZ GmbH revenue | 25.4 (23.8) | EUR m | 2024 (2023) | Germany | Journey planning | implisense/viaductus (via search summary) | https://implisense.com/en/companies/mentz-gmbh-muenchen-DE806I0XL686 | low | Staff 170–300 depending on source |
| 30 | Scheidt & Bachmann group revenue / staff | 528.7 / 3,461 | EUR m / heads | 2024 | Global (export 63.7%) | FCS + signalling + parking + energy | weltmarktfuehrerindex.de | https://www.weltmarktfuehrerindex.de/profil/scheidt-bachmann | medium | FCS division not split |
| 31 | ATRON electronic GmbH staff / balance sheet | 97 / EUR 24.0m | heads / EUR m | 2023 | Germany | Ticketing + ITS | implisense (via search summary) | https://app.implisense.com/en/companies/atron-electronic-gmbh-markt-schwaben--DE4M3XWTC300 | low | Revenue class EUR 10–50m |
| 32 | Conduent Transit Solutions revenue series | 254 / 248 / 262 / 226 / 237 / 341 / 371 | USD m | 2019–2025 | Global (NA core) | Fare mgmt + fleet mgmt | SEC 10-K FY2021, FY2023, FY2025 | https://www.sec.gov/Archives/edgar/data/1677703/000167770326000024/cndt-20251231.htm | high | FY2025 10-K restates 2023 to 233; tolling 327/318/327/328/317/244/238 |
| 33 | Conduent transit pro forma P&L 2025 | Revenue 371; cost of services 298; SG&A 41; D&A 14 → pre-tax ≈ −18 | USD m | 2025 | Global | as above | 8-K 6 Oct 2026 Ex. 99.2 | https://www.sec.gov/Archives/edgar/data/1677703/000167770326000123/ex992transitproforma.htm | high | Removed revenue 341 (2024), 237 (2023) |
| 34 | Modaxo–Conduent price mechanics | 164 base; 140 cash at close; 10 NTA + 12 special holdback; 15 cash transferred; net proceeds 125 | USD m | 1 Oct 2026 | — | — | same 8-K | same | high | 0.44x 2025 revenue |
| 35 | Conduent Transportation segment profit | −12 (2025) / −25 (2024) on revenue 609 / 586 | USD m | 2024–25 | — | Transit + tolling | 10-K FY2025 | as #32 | high | Incl. tolling |
| 36 | Cubic LTM revenue / transit share / leverage at LBO | 1.47bn / ~60% / >9x | USD / % / x | Dec-2020 / 2021 | Global | Fare + ITS + defence | Moody's RAC 15 Apr 2021 (Yahoo Finance) | https://finance.yahoo.com/news/atlas-cc-acquisition-corp-moodys-225211573.html | high | B3 CFR; ~USD 2bn rated debt; backlog 3.7bn |
| 37 | Cubic rating chronology 2021–2026 | 16 actions (see takeaway 3) | — | 2021–Oct 2026 | — | — | Prospect News issuer index | https://www.prospectnews.com/cgi-bin/issuerresponse.pl?first=A&issuer=79223 | high (dates/headlines) | Latest: Moody's lowers Cubic 26 Oct 2026 |
| 38 | Fitch downgrade to CC | 13 Aug 2026; third straight quarterly interest deferral treated as DDE | — | 2026 | — | — | Octus | https://octus.com/resources/articles/cubic-corp-agrees-on-out-of-court-deal/ | medium | USD 175m new capital (100 lenders + 75 Veritas) |
| 39 | S&P to SD | 2 Feb 2026 after Jan-27 interest deferral | — | 2026 | — | — | LCD/S&P via Yahoo Finance | https://finance.yahoo.com/news/us-leveraged-loan-default-rate-182449374.html | medium | Earlier CCC+ (Feb-2025, "onerous debt burden") per Mobility Payments |
| 40 | Clever Devices projected revenue / staff | >220 / 600+ | USD m / heads | 2026 | NA (8 of 10 largest agencies) | CAD/AVL, PIS | Hitachi Rail completion release | https://www.cleverdevices.com/news/hitachi-rail-completes-acquisition-of-clever-devices-expanding-its-portfolio-of-multi-modal-transport-solutions/ | high | Price undisclosed; closed 1 Jul 2026 |
| 41 | Via revenue by geography / customer type | US 309.7 / DE 83.5 / other 41.1; government 406.4 / commercial 27.9 | USD m | 2025 | — | On-demand platform + services | Via 10-K FY2025 | https://www.sec.gov/Archives/edgar/data/1603015/000160301526000008/via-20251231.htm | high | Total 434.3 (337.6); >90% government |
| 42 | Moovit revenue (Mobileye "Other") | 39 | USD m | FY2025 | Global | Consumer app/MaaS | Mobileye 10-K | https://www.sec.gov/Archives/edgar/data/1910139/000110465926014300/mbly-20251227x10k.htm | high | Mobileye segment 1,855 |
| 43 | Genfare revenue | Not disclosed; D&M segment 746.9 (619.2; 618.9) | USD m | 2025 | NA | Fare hardware | SPX 10-K FY2025 | https://www.sec.gov/Archives/edgar/data/88205/000008820526000008/spxc-20251231.htm | high | Not allocable |
| 44 | Indra Mobility revenue | 398 (+10%) | EUR m | 2025 | Global | Tolling/traffic/fare/rail | Indra FY2025 PR | https://www.indragroup.com/cms-content/2026/02/260225-PR-Indra-Group-Results-2025-2.pdf | high | Q4 +32% |
| 45 | GMV group revenue / EBITDA / staff | 510.25 / 43.65 / 3,880 | EUR m / heads | 2025 | 75% international | ITS division not split | GMV Annual Report 2025 | https://www.gmv.com/es/docs/annual-report-2025 | high | ITS "far exceeded goals"; record US sales (Westchester County) |
| 46 | Equans sales / COPA | 18.7bn / 820 | EUR | 2025 | Global | Ineo Systrans not split | Bouygues FY2025 release (Nasdaq) | https://www.nasdaq.com/press-release/bouygues-very-robust-2025-results-and-free-cash-flow-record-level-2026-02-26 | high | −2% sales |
| 47 | Luminator ownership | Audax Private Equity + BNP Paribas Développement, from LLCP, 7–8 Apr 2014 | — | 2014 | Plano, TX | PIS/video hardware | LLCP release; Mergr | https://www.llcp.com/levine-leichtman-capital-partners-sells-luminator-technology-group/ ; https://mergr.com/audax-private-equity-acquires-luminator-technology-group | high | No Gemspring link found |
| 48 | Luminator revenue / staff (aggregators) | 189–311 / 850–963 | USD m / heads | 2025–26 | Global | as above | Growjo, Datanyze, RocketReach, PitchBook | https://growjo.com/company/Luminator_Technology_Group ; https://www.datanyze.com/companies/luminator-technology-group/23249507 | low | Fallback only |
| 49 | Avail Technologies revenue / staff | 24.5 / 140–155 | USD m / heads | 2025–26 | US | CAD/AVL | ZoomInfo, Growjo, RocketReach | https://www.zoominfo.com/c/avail-technologies-inc/1155457838 | low | ESOP-owned |
| 50 | GIRO revenue / staff | 115.5 (Owler 25–100) / 621–842 | USD m / heads | 2026 | Global | Scheduling | Datanyze, RocketReach, PitchBook | https://www.datanyze.com/companies/giro/50075133 | low | — |
| 51 | Swiftly revenue / staff | 8.4–11.9 / 108–181 | USD m / heads | 2025 | NA | SaaS | Latka, ZoomInfo, PitchBook | https://getlatka.com/companies/goswift.ly | low | Headcount implies more |
| 52 | Optibus revenue / staff (global) | 59.6 (2024) / 346 | USD m / heads | 2024–25 | Global | SaaS | Latka, ZoomInfo | https://getlatka.com/companies/optibus | low | UK sub-group filed at 23.6 |
| 53 | Spare Labs revenue / staff | 25.7 (2023; ZoomInfo 48.7) / 81–300 | USD m / heads | 2023–25 | NA | Demand-response SaaS | Latka, ZoomInfo, Tracxn, PitchBook | https://getlatka.com/companies/sparelabs.com | low | C$42m Series B Sep-2024 |
| 54 | Passio / ETA Transit revenue | 3–25 / 5.6 | USD m | 2025–26 | US | CAD/AVL | ZoomInfo, RocketReach, Cience | https://www.zoominfo.com/c/passio-technologies/356022765 ; https://rocketreach.co/eta-transit-systems-profile_b5e6817ef42e58e0 | low | — |
| 55 | Aggregator error calibration | Vix +178% (226 vs 81.5 USD m); Hanover −40–45% (USD 52.8–59.7m vs GBP 92.8m) | % | 2025 | — | — | ZoomInfo/RocketReach vs filings; Datanyze/Growjo vs filings | https://www.zoominfo.com/c/vix-technology-sa/346091796 ; https://growjo.com/company/Hanover_Displays | high | Registry-derived Endole matched filings |
| 56 | Constellation disclosure of Modaxo | None (six operating segments aggregated into one reportable segment) | — | FY2025 | — | — | CSU Q4-2025 financial report | https://www.csisoftware.com/wp-content/uploads/2026/04/Q4-2025-Shareholder-Report.pdf | high | Conduent PPA will appear in FY2026 MD&A |
| 57 | Berg NA pool share — Modaxo (Trapeze legacy + Conduent transit) | 402 of 1,220 = 33% (range ~27–39%) | EUR m / % | 2025 | North America | Bus+tram ITS incl. fare | DERIVED (Section 5) | this file | low | Trapeze legacy USD 350m assumption |
| 58 | Berg NA pool concentration | top-5 64% (vendor) / 71% (owner); top-10 84% / 86%; 92% allocated to 18 names | % | 2025 | North America | as above | DERIVED | this file | low-medium | See sensitivity |
| 59 | Berg Europe pool concentration | largest vendor 6% (INIT); top-5 21%; top-10 30%; 40% allocated to 24 names | % | 2025 | Europe | as above | DERIVED | this file | low-medium | EUR 1.5bn residual long tail |

---

## 3. Vendor revenue, mix and ownership table (statutory and parent disclosures)

Latest filed year; EUR conversions at ECB 6 Nov 2026 rates. "Fare flag" = share of revenue that is fare collection/ticketing (ADJACENT scope). Full field set in `vendor_revenue_statutory_registry.csv`.

| Vendor (entity) | FY | Revenue (local) | EUR m | Prior yr | Growth | Op. profit / EBIT (margin) | EBITDA | Staff | Geography of revenue | Mix (goods / services / recurring) | Ownership | Fare flag | Conf. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cubic Transportation Systems Ltd (UK) | Sep-25 | GBP 177.1m | 212.3 | 183.1 | −3.3% | 15.4m (8.7%) | n/d | 1,101 | UK 92% / Europe 2% / RoW 6% | Goods 20% / services 80%; over-time 77% | Cubic Corp → Veritas + Elliott | FARE-HEAVY (TfL RCC ~50%) | high |
| Trapeze Group (UK) Ltd | Dec-24 | GBP 11.05m | 13.3 | 10.9 | +1.5% | 0.53m (4.7%) | 1.77m | 98 | UK 92% / Europe 8% | Software consultancy & supply; GM 88%; paid annually in advance | Modaxo Europe A/S → CSU | No | high |
| Trapeze ITS U.K. Ltd | Dec-25 | GBP 16.35m | 19.6 | 12.0 | +36.4% | 1.59m (9.7%); EBITA 1.62m | n/d | 55 | UK 2% / rest of Europe 75% / RoW 22% | AVL/RTPI software & services; GM 48% | Modaxo (DK) → CSU | No | high |
| Vix AFC Ltd (group) | Jun-25 | USD 81.5m | 73.0 | 83.6 | −2.6% | LBT −7.9m | 0.9m (underlying ~3.0m) | 294 | Europe 67% / NA 26% / APAC 7% | Systems 12% / services 23% / goods 41% / other 24% | ICM Mobility Group (D. Saville) | FARE + ITS | high |
| Vix Technology UK Ltd | Jun-25 | GBP 30.6m | 36.7 | 26.7 | +14.8% | 2.5m (8.2%) | n/d | 130 | UK 99% | Mixed AFC + RTI; "higher proportion of software and support" | Vix AFC → ICM | FARE + RTPI | high |
| Corvia Ltd (Ticketer) | Dec-25 | GBP 26.35m | 31.6 | 26.9 | −1.9% | 3.46m (13.1%) | adj. 6.4m (24%) | 87 | UK 100% | Goods 38% / services 62%; ARR GBP 16.3m (62%) | Tenzing PE (Ishtar Topco) | FARE-HEAVY (ETMs) | high |
| Hanover Displays Ltd (group) | Dec-25 | GBP 92.8m | 111.3 | 72.6 | +27.8% | 15.7m (16.9%) | n/d | 362 | Undisclosed (prejudicial); subs FR/ES/DE/IT/AU/HK + US plant | Hardware; GM 58% | Founder D G Williams | No | high |
| Flowbird Transport Ltd (UK) | Dec-25 | GBP 23.0m | 27.5 | 24.9 | −7.6% | 3.44m (15.0%) | 5.2m | 162 | UK 70% / Europe 16% / AU 9% / US 4% / RoW 1% | GM 32%; ticketing & information systems | Arrive AS (ex-EasyPark) | FARE-HEAVY | high |
| Masabi Group Ltd | Dec-25 | GBP 41.9m | 50.2 | 37.5 | +11.7% | LBT −0.47m | n/d | n/d | NA 90% / RoW 10% | Recurring 74% / deployment 26% | No single controller (Accel-KKR) | FARE (SaaS) | high |
| Icomera UK Ltd | Dec-24 | GBP 21.9m | 26.2 | 23.5 | −6.7% | 0.90m (4.1%) | n/d | 94 | UK 96% | Connectivity; rail-heavy | Equans → Bouygues | No | high |
| Optibus Transportation Ltd (UK sub-group) | Dec-24 | USD 23.6m | 21.1 | 21.9 | +7.9% | −2.7m (−11.5%) | n/d | 182 | UK 44% / Europe 35% / LatAm 20% / Asia 1% | SaaS; GM 91% | Optibus Ltd (IL, VC) | No | high |
| Icomera AB (SE parent) | Dec-25 | SEK 439.6m | 39.9 | 489.9 | −10.3% | 9.5m (2.2%) | 15.1m | 108 | Parent incl. intra-group | Connectivity | Equans → Bouygues | No | high |
| Consat Telematics AB | Dec-25 | SEK 278.9m | 25.3 | 204.2 | +36.6% | 20.5m (7.4%) | 23.4m | 104 | Nordics | CAD/AVL + PIS | Private (Consat) | No | high |
| LTG Sweden AB (ex-Mobitec; Luminator) | Feb-25 | SEK 279.5m | 25.4 | 171.6 | +62.9% | −20.7m (−7.4%) | n/d | 28 | Nordics/Europe | PIS hardware | Luminator (Audax + BNP PD) | No | high |
| AB Thoreb | Dec-25 | SEK 141.3m | 12.8 | 135.4 | +4.3% | −5.8m | 1.1m | 31 | Sweden | On-board computers | Private | No | high |
| Hogia PTS AB + PTP AB | Dec-25 | SEK 171.7m | 15.6 | 174.8 | −1.8% | PTS 8.4m (7.4%) | — | 63 | Nordics | PT software | Hogia AB | No | high |
| Pilotfish Networks AB | Dec-25 | SEK 38.3m | 3.5 | 78.6 (15 mo.) | n/m | 0.5m | 3.9m | 12 | Sweden | Gateways | Private | No | high |
| FARA AS (Modaxo) | Dec-24 | NOK 222.1m | 21.1 | 190.6 | +16.6% | 1.0m (0.4%) | 15.7m | 41 | Norway | Ticketing + RTPI | Modaxo → CSU | Mixed | high |
| Saga Tenix AS | Dec-25 | NOK 22.6m | 2.1 | n/d | — | −12.8m | −8.0m | 11 | Norway | Telematics | Private | No | high |
| Modaxo Europe A/S (DK; ex-Trapeze Group Europe) | n/d | DKK 47.5m | 6.4 | n/d | — | n/d | n/d | 36–45 | Denmark | Holding/sales | CSU | No | low |
| Trapeze Germany GmbH (Berlin) | Dec-23 | EUR 9.8m | 9.8 | 13.0 | −25% | n/d | n/d | n/d | Germany | ITS | CSU | No | medium |
| Trapeze Switzerland GmbH | — | n/d | — | — | — | — | — | ~250 | European HQ | ITS/CAD-AVL | CSU | No | medium (staff) |
| MENTZ GmbH | Dec-24 | EUR 25.4m | 25.4 | 23.8 | +6.7% | n/d | n/d | 170–300 | DE-centric | Journey planning | Family | No | low |
| Scheidt & Bachmann (group) | Dec-24 | EUR 528.7m | 528.7 | n/d | — | n/d | n/d | 3,461 | Export 64% | FCS not split | Family | FARE (division) | medium |
| ATRON electronic GmbH | Dec-23 | EUR 10–50m class | — | — | — | — | — | 97 | DE/AT | Ticketing + ITS | Private | Mixed | low |
| Conduent Transit Solutions (→ Novvan/Routeward) | Dec-25 | USD 371m | 332.3 | 341 | +8.8% | ≈ −18m pre-tax (−5%) | n/d | ~2,000 | NA core + EU/AU/ME/LatAm | Cost of services 80% | Modaxo (USD 164m, 1 Oct 2026) | FARE-HEAVY + fleet mgmt | high |
| Cubic Corp / CTS (group) | Sep | USD 1.47bn LTM Dec-20; later n/d | — | — | — | n/d | n/d | n/d | ~60% transit, ~40% defence (2021) | Fare systems + operations | Veritas + Elliott; CC / SD / Caa | FARE-HEAVY | medium |
| Clever Devices (Hitachi MMS) | 2026E | >USD 220m | >197 | n/d | — | n/d | n/d | 600+ | NA | CAD/AVL, PIS, APC, cloud | Hitachi Rail (1 Jul 2026) | No | high |
| Via Transportation | Dec-25 | USD 434.3m | 389.0 | 337.6 | +28.6% | n/d (net loss −96.4m, file 26) | — | n/d | US 71% / DE 19% / other 10%; government 94% | Platform + tech-enabled services | NYSE: VIA | No | high |
| Indra Mobility | Dec-25 | EUR 398m | 398 | 362 | +10% | ~6% EBIT margin (secondary) | — | n/d | Global | Tolling/traffic/fare/rail | IBEX-listed | Mixed | high |
| GMV (group; ITS not split) | Dec-25 | EUR 510.3m | 510.3 | 454 (derived) | +12.3% | — | 43.65m | 3,880 | 75% international | ITS ~10% of FTE (file 08) | Family | No (ITS) | high |
| Equans (Ineo Systrans not split) | Dec-25 | EUR 18.7bn | 18,700 | 19.1bn | −2% | COPA 820m (4.4%) | — | n/d | Global | — | Bouygues | No | high |
| Luminator (group, aggregator) | — | USD 189–311m | 169–279 | — | — | — | — | 850–963 | 85+ countries | PIS/video/lighting | Audax + BNP PD (2014) | No | low |
| Avail / GIRO / Swiftly / Optibus / Spare / Passio / ETA (aggregators) | — | USD 24.5 / 115.5 / 8–12 / 59.6 / 25.7 / 3–25 / 5.6m | 22 / 103 / 9–11 / 53 / 23 / 3–22 / 5 | — | — | — | — | 145 / 620–840 / 108–181 / 346 / 81–300 / 10–39 / 26–28 | NA / global / NA / global / NA / US / US | Software | ESOP / private / VC / VC / VC / private / private | No | low |

---

## 4. Rating-agency record on Cubic Corporation (Atlas CC Acquisition Corp.), 2021–2026

| Date | Agency | Action (Prospect News headline unless stated) | Detail / source |
|---|---|---|---|
| 15 Apr 2021 | Moody's | Assigns B3 CFR, B3 1L, Ba3 TLC; stable | LTM revenue USD 1.47bn; ~USD 2bn rated debt; pro forma leverage >9x, not <7x before 2023; ~60% revenue from fare/traffic management, ~40% defence; backlog USD 3.7bn; FCF >USD 175m "with margin expansion" (full text: https://finance.yahoo.com/news/atlas-cc-acquisition-corp-moodys-225211573.html) |
| 16 Apr 2021 | Fitch | Gives Cubic B | https://www.prospectnews.com/cgi-bin/issuerresponse.pl?first=A&issuer=79223 |
| 29 Nov 2022 | Moody's | Snips Cubic | same index |
| 24 Jul 2023 | Fitch | Changes outlook to negative | same |
| 22 Jul 2024 | Fitch | Cuts Cubic loans | same |
| 16 Oct 2024 | Moody's | Cuts Atlas CC Acquisition | same |
| Feb 2025 | S&P | B- → CCC+, negative; "onerous debt burden", capital structure "unsustainable", ~USD 2bn debt at FY Sep-2024 | https://www.mobility-payments.com/2025/02/17/ratings-agency-downgrades-cubics-credit-rating-warning-of-onerous-debt-burden/ |
| 14 Feb 2025 | Fitch | Cuts Cubic, Atlas | Prospect News |
| 3 Jul 2025 | — | Recap: USD 275m new liquidity, USD 170m sponsor equity, USD 370m debt reduction, maturities to May 2029 | Octus; files 10/26 |
| 9 Jul 2025 | Fitch | Trims Cubic, Atlas → CCC- (from B-) | cbonds headline https://cbonds.com/news/3485289/ |
| 24 Jul 2025 | Moody's | Corrects Cubic TLC to Caa2 | Prospect News |
| 1 Aug 2025 | Moody's | Appends Atlas default rating | Prospect News |
| 21 Aug 2025 | Fitch | Gives Cubic loans B+, CCC+, CCC- (post-DDE: RD → CCC+) | Prospect News; NewsyList |
| 27 Aug 2025 | Moody's | Rates Cubic loans B1, Caa2, Ca | Prospect News |
| 2 Feb 2026 | S&P | CCC+ → SD after lenders deferred the 27 Jan interest payment to 28 Apr (PIK premium, revolver draws halted, monthly reporting) | LCD via Yahoo https://finance.yahoo.com/news/us-leveraged-loan-default-rate-182449374.html |
| 9 Feb 2026 | Fitch / Moody's | "Fitch acts on Cubic"; "Moody's appends Cubic default rating" | Prospect News |
| 13 Aug 2026 | Fitch | → CC: deferral of 27 Jul 2026 interest on second-out TLB/TLC = third straight quarterly deferral, treated as DDE; grace period to 30 Sep 2026 absent consent | Octus https://octus.com/resources/articles/cubic-corp-agrees-on-out-of-court-deal/ |
| Sep 2026 | — | Out-of-court deal: USD 175m (USD 100m lenders, USD 75m Veritas), unanimous consent | Octus |
| 26 Oct 2026 | Moody's | Lowers Cubic, rates loans B2 | Prospect News |

Post-2021 revenue, EBITDA and debt figures from the agency commentaries could not be read (Fitch/Moody's pages are JavaScript applications; six guessed RAC URLs returned the shell). The last hard numbers remain FY2020 (sales USD 1,476m; CTS USD 841m, file 26) and Moody's April 2021 LTM USD 1.47bn.

---

## 5. Share of Berg's 2025 pools (DERIVED)

**Method.** Pool = Berg Insight 10th ed. (Mar 2026): Europe EUR 2,550m, North America EUR 1,220m, bus+tram public-transport ITS, fare-inclusive but with mega-AFC programmes most plausibly outside (file 17). For each vendor: regional gross revenue (filed where available, assumption otherwise) × an in-scope factor (share of that revenue that is bus/tram ITS incl. on-vehicle fare equipment and ticketing back-office; excludes mega-AFC operations, rail-only, tolling/traffic, parking, defence, aerospace, service operations). Every factor and split is stated in `vendor_share_berg_pools_2025.csv`. Currency at ECB 6 Nov 2026. Figures are 2025 (or latest filed year) in EUR m.

### 5.1 North America (pool EUR 1,220m)

| Rank | Vendor | Gross regional revenue | In-scope factor | Attributed | Share | Basis (abridged) | Conf. |
|---|---|---|---|---|---|---|---|
| 1 | Trapeze / Vontas / TripSpark / TransLoc / Routematch (Modaxo legacy) | 313.5 | 0.80 | 250.8 | 20.6% | ASSUMPTION USD 350m (~2,000 NA staff × USD 175k; range 250–450) | low |
| 2 | Clever Devices (Hitachi MMS) | 161.2 | 0.95 | 153.2 | 12.6% | >USD 220m 2026E → USD 200m 2025E × 90% NA | medium |
| 3 | Conduent Transit (Novvan + Routeward; Modaxo from Oct-2026) | 232.6 | 0.65 | 151.2 | 12.4% | USD 371m × 70% NA; 65% in scope (fleet mgmt + bus-level fare) | medium-low |
| 4 | INIT North America | 130.8 | 0.85 | 111.2 | 9.1% | AR2025 EUR 130.8m; 15% treated as rail/other AFC | high/medium |
| 5 | Cubic CTS (NA bus-level: Umo, NextBus legacy, validators, back-office) | 434.5 | 0.25 | 108.6 | 8.9% | USD 1.47bn × 60% transit × 55% NA; 25% in scope | low |
| 6 | Luminator (NA) | 123.2 | 0.70 | 86.2 | 7.1% | USD 250m midpoint × 55% NA; ex aerospace/rail | low |
| 7 | Via (US platform portion) | 277.4 | 0.20 | 55.5 | 4.5% | US USD 309.7m; 20% software/platform | low |
| 8 | Masabi (NA) | 45.1 | 1.00 | 45.1 | 3.7% | Filed GBP 37.6m | high |
| 9 | GIRO (NA) | 51.7 | 0.80 | 41.4 | 3.4% | USD 115.5m × 50% NA | low |
| 10 | Avail | 21.9 | 1.00 | 21.9 | 1.8% | USD 24.5m | low |
| 11 | Spare (NA) | 19.6 | 1.00 | 19.6 | 1.6% | USD 25.7m × 85% | low |
| 12 | Vix (NA) | 18.7 | 1.00 | 18.7 | 1.5% | Filed USD 20.9m | high |
| 13 | Hanover (NA) | 16.7 | 0.95 | 15.9 | 1.3% | GBP 92.8m × 15% NA (assumption) | low |
| 14 | GMV ITS (NA) | 15.3 | 0.90 | 13.8 | 1.1% | EUR 510m × 10% ITS × 30% NA | low |
| 15 | Optibus (NA) | 13.3 | 1.00 | 13.3 | 1.1% | USD 59.6m × 25% | low |
| 16 | Swiftly | 10.7 | 1.00 | 10.7 | 0.9% | USD 11.9m | low |
| 17 | ETA Transit | 5.0 | 1.00 | 5.0 | 0.4% | USD 5.6m | low |
| 18 | Passio | 4.5 | 1.00 | 4.5 | 0.4% | USD 5m | low |
| | **Allocated** | | | **1,126.6** | **92.3%** | Residual EUR 93m: Genfare (SPX, n/d), Siemens/HaCon NA, Icomera NA, Connexionz, Safe Fleet/Seon video, Apollo, Hayden AI, Kontron, Transit app, OEM telematics | |
| | **Top-5 (vendor)** | | | 775 | **63.5%** | | |
| | **Top-10 (vendor)** | | | 1,025 | **84.0%** | | |
| | **Modaxo consolidated (rows 1+3)** | | | **402.0** | **33.0%** | Range 27–39% on Trapeze USD 250–450m | low |
| | **Top-5 (owner: Modaxo, Clever, Cubic, INIT, Luminator)** | | | 861 | **70.6%** | | |
| | **Top-10 (owner)** | | | 1,044 | **85.6%** | | |

**Sensitivity (NA).** Trapeze legacy at USD 250m and Cubic in-scope at 15%: allocated falls to EUR 1,012m (83%), Modaxo 27%, owner top-5 61%. Trapeze at USD 450m and Cubic at 35%: allocated EUR 1,241m (102% — exceeds the pool), which is the signal that Berg's NA value excludes most mega-AFC revenue and/or that Trapeze NA is below USD 450m. **Model recommendation:** Modaxo 27–39% (central 33%), Clever/Hitachi 12–14%, INIT 9–10%, Cubic bus-level 6–10%, Luminator 5–8%; long tail (everything below 2%) ≈ 10–15%.

### 5.2 Europe (pool EUR 2,550m)

| Rank | Vendor | Gross regional revenue | In-scope factor | Attributed | Share | Basis (abridged) | Conf. |
|---|---|---|---|---|---|---|---|
| 1 | INIT (DE + Europe ex-DE) | 173.7 | 0.90 | 156.3 | 6.1% | AR2025 DE 95.7 + EU ex-DE 78.0 | high/medium |
| 2 | Trapeze / Modaxo Europe | 145.1 | 0.85 | 123.3 | 4.8% | Filed UK 32.9 + DE 9.8 + DK 6.4 + FARA 21.1; ASSUMED CH 55 (250 staff × EUR 220k) + other units 20 | low-medium |
| 3 | IVU Traffic Technologies | 134.7 | 0.85 | 114.5 | 4.5% | EUR 149.7m × 90% Europe | medium |
| 4 | Hanover Displays (UK + Europe) | 83.5 | 0.95 | 79.3 | 3.1% | GBP 92.8m × 75% (assumption) | medium-low |
| 5 | Flowbird Transport UK + Flowbird SAS transport | 63.8 | 1.00 | 63.8 | 2.5% | Filed UK/EU GBP 19.8m + ASSUMED FR transport EUR 40m | medium/low |
| 6 | Cubic Transportation Systems Ltd (UK) | 212.3 | 0.25 | 53.1 | 2.1% | Filed GBP 177.1m; 25% bus/tram-level (TfL RCC and TMS outside) | low |
| 7 | Scheidt & Bachmann FCS (bus-level, Europe) | 119.0 | 0.40 | 47.6 | 1.9% | EUR 528.7m × 30% FCS × 75% Europe; 40% bus-level | low |
| 8 | Vix (Europe) | 49.2 | 0.90 | 44.2 | 1.7% | Filed USD 54.9m | high/medium |
| 9 | Indra Mobility (Europe bus share) | 199.0 | 0.20 | 39.8 | 1.6% | EUR 398m × 50% Europe; 20% bus ITS | low |
| 10 | Luminator Europe (LTG Sweden + DE/IT) | 40.4 | 0.90 | 36.3 | 1.4% | Filed SEK 279.5m + assumed EUR 15m | medium-low |
| 11 | Ticketer (Corvia) | 31.6 | 1.00 | 31.6 | 1.2% | Filed GBP 26.35m | high |
| 12 | HaCon (Siemens) | 58.5 | 0.50 | 29.2 | 1.1% | ASSUMED 500 staff × EUR 130k × 90% EU; 50% bus/multimodal | low |
| 13 | GMV ITS (Europe) | 30.6 | 0.90 | 27.6 | 1.1% | EUR 510m × 10% × 60% | low |
| 14 | Consat Telematics | 25.3 | 1.00 | 25.3 | 1.0% | Filed SEK 278.9m | high |
| 15 | MENTZ | 25.4 | 0.90 | 22.9 | 0.9% | EUR 25.4m (2024) | low-medium |
| 16 | Via (Germany + other Europe platform portion) | 96.9 | 0.20 | 19.4 | 0.8% | USD 83.5m + 60% × 41.1m; 20% platform | low |
| 17 | Icomera (bus share) | 46.2 | 0.40 | 18.5 | 0.7% | AB external ~50% of SEK 440m + UK GBP 21.9m; 40% bus | low |
| 18 | ATRON electronic | 17.5 | 1.00 | 17.5 | 0.7% | ASSUMED 97 staff × EUR 180k | low |
| 19 | Optibus (UK + Europe) | 16.7 | 1.00 | 16.7 | 0.7% | Filed USD 18.7m (2024) | high |
| 20 | Hogia PTS + PTP | 15.6 | 1.00 | 15.6 | 0.6% | Filed SEK 171.7m | high |
| 21 | Thoreb | 12.8 | 1.00 | 12.8 | 0.5% | Filed SEK 141.3m | high |
| 22 | Masabi (Europe/RoW) | 5.1 | 1.00 | 5.1 | 0.2% | Filed GBP 4.3m | high |
| 23 | Pilotfish | 3.5 | 1.00 | 3.5 | 0.1% | Filed SEK 38.3m | high |
| 24 | Saga Tenix | 2.1 | 1.00 | 2.1 | 0.1% | Filed NOK 22.6m | high |
| | **Allocated** | | | **1,006.0** | **39.5%** | Residual EUR 1,544m (60%): Equans/Ineo Systrans (France leader per Berg; not disclosed), RATP Smart Systems, Siemens Mobility ITS, Kontron, Swarco, Hitachi Rail (ex-Thales ticketing), Conduent Europe (~EUR 50–100m of the USD 371m), Ridango, Kentkart, PSI Transcom, Dysten, R&G, Tri Star, Telia, Trivector, Italian/Spanish/French integrators, OEM telematics (Volvo, Daimler, Scania, Iveco), mega-AFC programmes if Berg counts them | |
| | **Top-5** | | | 537 | **21.1%** | | |
| | **Top-10** | | | 758 | **29.7%** | | |

**Reading.** Even with generous assumptions no European vendor exceeds ~6% of Berg's pool, and the ten largest identifiable vendors hold under a third of it. The NA pool, by contrast, is a three-owner market (Modaxo, Hitachi/Clever, INIT) plus a distressed Cubic. This is the quantitative basis for the "concentrated NA / fragmented Europe" statement in the competitive section and for the entry thesis that a European software platform can scale through the long tail without displacing a dominant incumbent.

---

## 6. Hardware / software / services mix evidence by vendor type (for the component split)

| Vendor type | Evidence (filed) | Implied component mix |
|---|---|---|
| Fare-system integrator / operator | Cubic UK goods 20% / services 80%, 77% over-time; Vix group goods 41% / services + systems 35% / other 24%, 80% at a point in time; Conduent transit cost of services 80% of revenue | Hardware 20–40%, services/operations 50–70%, software thin; gross margins 30–40% |
| Bus ticketing SaaS/ETM vendor | Ticketer goods 38% / services 62%, ARR 62% of revenue, adj. EBITDA 24%; Masabi recurring 74%, deployment 26%; Flowbird UK GM 32% | Hardware 25–40%, recurring software/services 60–75% |
| Scheduling / ops software | Trapeze Group (UK) GM 88%, paid annually in advance; IVU 51.8% recurring (file 08); Optibus UK GM 91% but operating loss | Software/licence 50–90%, services remainder, no hardware |
| CAD/AVL + RTPI systems | Trapeze ITS UK GM 48%, EBITA 10%; INIT (file 08) project + 20-year service contracts; Clever "capex systems + maintenance + CleverCloud" | Hardware 30–45%, software 20–30%, services/maintenance 30–40% |
| Display / on-board hardware | Hanover GM 58%, op margin 17%; LTG Sweden EBIT negative; Thoreb EBIT negative | 100% goods; margins depend on scale |
| Connectivity | Icomera UK op margin 4%, Icomera AB 2% | Hardware + managed service, low margin |

These are consistent with GMI's 46.8 / 33.0 / 20.1 hardware/software/services split (file 17) at the market level only if fare-system operations are classed as services; for a core bus-ITS definition the filed mixes point to hardware 35–45%, software 25–35%, services 25–35%.

---

## 7. Assumptions and currency conversions (all derived numbers)

- FX: ECB reference rates 6 Nov 2026 — EUR 1 = USD 1.1165, GBP 0.83415, SEK 11.026, NOK 10.526, DKK 7.4752, CHF 0.9143, AUD 1.625, CAD 1.5705. GBP figures from UK accounts converted at 0.83415 (e.g. Cubic UK 177.07 / 0.83415 = EUR 212.3m); SEK at 11.026 (Consat 278.936 / 11.026 = EUR 25.3m); NOK at 10.526 (FARA 222.113 / 10.526 = EUR 21.1m); USD at 1.1165 (Conduent 371 / 1.1165 = EUR 332.3m).
- Clever Devices 2025 revenue = USD 200m (assumes ~10% growth into the ">USD 220m" 2026 projection).
- Trapeze legacy NA = USD 350m (Modaxo ~3,500 staff pre-Conduent (file 08) less ~550 identified European staff (CH 250, UK 153, DE ~65–100, DK ~40, FARA 41) and ~100 other → ~2,000–2,300 NA; × USD 150–200k revenue/employee → USD 300–460m; central 350).
- Conduent transit NA share 70%; in-scope 65% (fleet management ~30% fully in scope + bus-level share of fare).
- Cubic CTS global = 60% × USD 1.47bn (Moody's 2021); NA 55%; bus/tram-level in-scope 25%.
- Luminator group = USD 250m (midpoint of aggregator range 189–311); NA 55%; in-scope 70%.
- Via platform share 20% of revenue (the 10-K describes software plus tech-enabled service operations; most revenue is operations).
- Hanover geography undisclosed: UK+Europe 75%, NA 15%, RoW 10%.
- GMV ITS division = 10% of group (400+ of 3,880 FTE); Europe 60% / NA 30%.
- Scheidt & Bachmann FCS = 30% of group; Europe 75%; bus-level 40%.
- Indra Mobility: Europe 50%, bus ITS 20%.
- HaCon = 500 staff × EUR 130k; ATRON = 97 staff × EUR 180k; Trapeze Switzerland = 250 staff × EUR 220k; Flowbird SAS transport = EUR 40m.
- Icomera AB external sales = 50% of parent revenue (rest intra-group); bus share 40%.
- In-scope factors of 0.85–0.95 for INIT, IVU, Trapeze, Clever, Vix, Hanover, MENTZ remove rail-only, airport, logistics or non-transit revenue.

---

## 8. Gaps and what would close them

1. **Cubic post-2021 financials** (revenue, EBITDA, debt by tranche, CTS share): only obtainable from the Fitch/Moody's/S&P rating-action commentaries (paywalled JS sites) or lender presentations; the chronology is complete, the numbers are not.
2. **Trapeze/Modaxo global and NA revenue**: Constellation does not disclose; the Conduent purchase-price allocation will appear in CSU's FY2026 MD&A (Feb/Mar 2027). The Swiss GmbH publishes no revenue. Bundesanzeiger filings for Trapeze Group Deutschland/Modaxo Group Germany GmbH (HRB 206607) and Trapeze-Elgeba GmbH were not retrieved (northdata rate-limited after one call).
3. **Luminator group revenue**: no statutory consolidation found; only LTG Sweden AB is filed. Audax's portfolio page is outside the session allow-list.
4. **Equans/Ineo Systrans, RATP Smart Systems, Siemens Mobility ITS, Kontron, Swarco**: no revenue — the EUR 1.5bn European residual is dominated by these.
5. **HaCon and DILAX Bundesanzeiger accounts**: not retrieved (search budget exhausted; DILAX is now inside INIT Germany revenue in any case).
6. **Hanover's geographic split** is withheld by the directors; **Vix's** UK/Brussels split within Europe and **Masabi's** customer counts by country are not disclosed.
7. **Genfare revenue** is not separable from SPX's Detection & Measurement segment.
8. **Hitachi FY2026 (Mar-2027) segment disclosure** of Clever Devices is not yet published; the >USD 220m figure is a deal-announcement projection.
9. **Flowbird SAS (France)** FY2024 turnover (EUR 212m) comes from a search summary of verif.com (host not allowed); the transport/parking split is unknown.
10. **Trapeze Group (UK) Ltd FY2025 accounts** were not yet on the register (last filed FY2024).
11. The Nordic figures for Icomera AB and Consat are parent-company accounts; consolidated group figures (which would remove intra-group sales and add foreign subsidiaries) were not retrieved.

---

## 9. Source list

**UK Companies House (accounts downloaded as PDF and OCR-read)**
- Cubic Transportation Systems Limited (01381707), full accounts to 30 Sep 2025, filed 14 Oct 2026 — https://find-and-update.company-information.service.gov.uk/company/01381707/filing-history
- Trapeze Group (UK) Limited (04160790), full accounts FY2024 (filed 24 Sep 2025) and FY2023 — https://find-and-update.company-information.service.gov.uk/company/04160790/filing-history
- Trapeze ITS U.K. Ltd (06960657), full accounts FY2025, filed 29 Oct 2026 — https://find-and-update.company-information.service.gov.uk/company/06960657/filing-history
- Vix AFC Limited (02649163), group accounts to 30 Jun 2025, filed 11 Jul 2026 — https://find-and-update.company-information.service.gov.uk/company/02649163/filing-history
- Vix Technology UK Limited (03039051), full accounts to 30 Jun 2025, filed 19 Apr 2026 — https://find-and-update.company-information.service.gov.uk/company/03039051/filing-history
- Corvia Limited (07011600), full accounts FY2025, filed 23 Jul 2026 — https://find-and-update.company-information.service.gov.uk/company/07011600/filing-history ; Ticketer Limited (07006670) dormant accounts — https://find-and-update.company-information.service.gov.uk/company/07006670/filing-history
- Hanover Displays Limited (01876684), group accounts FY2025, filed 2 Oct 2026 — https://find-and-update.company-information.service.gov.uk/company/01876684/filing-history
- Flowbird Transport Limited (01232487), full accounts FY2025, filed 1 Oct 2026 — https://find-and-update.company-information.service.gov.uk/company/01232487/filing-history ; Flowbird Smart City UK Limited (04869035) — https://find-and-update.company-information.service.gov.uk/company/04869035
- Masabi Group Limited (04260927), group accounts FY2025, filed 4 Aug 2026 — https://find-and-update.company-information.service.gov.uk/company/04260927/filing-history ; Masabi Limited (04431819) small-company accounts — https://find-and-update.company-information.service.gov.uk/company/04431819/filing-history
- Icomera UK Limited (06089258), full accounts FY2024, filed 23 Dec 2025 — https://find-and-update.company-information.service.gov.uk/company/06089258/filing-history
- Optibus Transportation Limited (11494674), group accounts FY2024, filed 1 Oct 2026 — https://find-and-update.company-information.service.gov.uk/company/11494674/filing-history ; Optibus Ltd (10339585) — https://find-and-update.company-information.service.gov.uk/company/10339585/filing-history
- GMV NSL Limited (03645072), full accounts FY2025 — https://find-and-update.company-information.service.gov.uk/company/03645072/filing-history
- INIT Innovations in Transportation Limited (07234994) — https://find-and-update.company-information.service.gov.uk/company/07234994/filing-history ; Omnibus Solutions Limited (03609069) — https://find-and-update.company-information.service.gov.uk/company/03609069/filing-history
- Luminator UK Ltd (16382962) — https://find-and-update.company-information.service.gov.uk/company/16382962 ; CleverDevices Ltd (14595806, dissolved) — https://find-and-update.company-information.service.gov.uk/company/14595806 ; Swiftly Ltd (17497874) — https://find-and-update.company-information.service.gov.uk/company/17497874 ; Mobitec Ltd (07328553, micro) — https://find-and-update.company-information.service.gov.uk/company/07328553

**Nordic registries**
- icomera AB — https://www.allabolag.se/foretag/icomera-ab/g%C3%B6teborg/internet-konsulter-operat%C3%B6rer/2K1OR8WI5YFHL
- Consat Telematics AB — https://www.allabolag.se/foretag/consat-telematics-ab/partille/konsulter/2K2QFETI5YF3I
- LTG Sweden AB — https://www.allabolag.se/foretag/ltg-sweden-ab/herrljunga/elektronik-komponenter/2K1J9NTI5YDXD
- AB Thoreb — https://www.allabolag.se/foretag/ab-thoreb/v%C3%A4stra-fr%C3%B6lunda/transportf%C3%B6rmedling/2JZH7VXI5YI2J ; Thoreb ITvehicle AB — https://www.allabolag.se/foretag/thoreb-itvehicle-ab/%C3%B6stersund/bilar/2K1OLK8I5YCZW
- Hogia Public Transport Systems AB — https://www.allabolag.se/foretag/hogia-public-transport-systems-aktiebolag/stenungsund/datautveckling-systemutveckling-programutveckling/2K1CUV4I5YDOJ ; Hogia Public Transport Products AB — https://www.allabolag.se/foretag/hogia-public-transport-products-ab/stenungsund/internet-konsulter-operat%C3%B6rer/2K1HAVXI5YFHL
- Pilotfish Networks AB — https://www.allabolag.se/foretag/pilotfish-networks-ab/g%C3%B6teborg/internet-konsulter-operat%C3%B6rer/2K1N9AYI5YFHL
- Trapeze Group Sweden AB — https://www.allabolag.se/foretag/trapeze-group-sweden-ab/v%C3%A4stra-fr%C3%B6lunda/konsulter/2K3KBJVI5YF3I
- FARA AS — https://www.proff.no/selskap/fara-as/trondheim/dataprogramvare-og-utvikling/IGCW3PJ009O (and /regnskap/ five-year table)
- Saga Tenix AS — https://www.proff.no/selskap/saga-tenix-as/blomsterdalen/tekniske-konsulenter/IGFHJ5Q01OU
- Modaxo Europe A/S (CVR 28655843) — https://www.degulesider.dk/trapeze+group+aarhus+v/66529710/firma ; https://www.krak.dk/trapeze+group+aarhus+v/66529710/firma ; https://erhvervplus.dk/erhvervsbasen/trapeze-group-europe-holding-a-s-196584

**German / Swiss (secondary extractions)**
- Trapeze Germany GmbH — https://implisense.com/en/companies/trapeze-germany-gmbh-berlin-DEDPK2MDTK54 ; Modaxo Group Germany GmbH (HRB 206607) — https://www.northdata.com/Modaxo%20Group%20Germany%20GmbH,%20Braunschweig/HRB%20206607 ; Trapeze-Elgeba — https://www.wer-zu-wem.de/firma/trapeze-elgeba.html ; Trapeze Switzerland GmbH — https://www.northdata.com/Trapeze%20Switzerland%20GmbH,%20Neuhausen%20am%20Rheinfall/CHE-114.963.678 ; https://www.sigareal.ch/de/gewerbe/mieterportraits/trapeze-switzerland-gmbh/ ; https://www.jobs.ch/de/firmen/34121-trapeze-switzerland-gmbh/
- MENTZ GmbH — https://implisense.com/en/companies/mentz-gmbh-muenchen-DE806I0XL686 ; https://www.viaductus.de/firma/DE-D2601-HRB-91898-mentz-gmbh-muenchen ; https://www.wer-zu-wem.de/firma/mentz-dv.html
- ATRON electronic GmbH — https://app.implisense.com/en/companies/atron-electronic-gmbh-markt-schwaben--DE4M3XWTC300 ; https://www.wer-zu-wem.de/firma/atron-electronic.html
- Scheidt & Bachmann — https://www.weltmarktfuehrerindex.de/profil/scheidt-bachmann ; https://www.scheidt-bachmann.de/en/company/about-us

**SEC EDGAR**
- Conduent 10-K FY2025 — https://www.sec.gov/Archives/edgar/data/1677703/000167770326000024/cndt-20251231.htm ; 10-K FY2024 — https://www.sec.gov/Archives/edgar/data/1677703/000167770325000029/cndt-20241231.htm ; 10-K FY2023 — https://www.sec.gov/Archives/edgar/data/1677703/000167770324000037/cndt-20231231.htm ; 10-K FY2021 — https://www.sec.gov/Archives/edgar/data/1677703/000167770322000015/cndt-20211231.htm ; 10-Q Q3-2026 — https://www.sec.gov/Archives/edgar/data/1677703/000167770326000154/cndt-20260930.htm ; 8-K 21 May 2026 Ex. 99.1 — https://www.sec.gov/Archives/edgar/data/1677703/000167770326000069/exhibit991cndtdouglastrans.htm ; 8-K 6 Oct 2026 Ex. 99.1 — https://www.sec.gov/Archives/edgar/data/1677703/000167770326000123/ex991transitpressrelease.htm ; Ex. 99.2 pro forma — https://www.sec.gov/Archives/edgar/data/1677703/000167770326000123/ex992transitproforma.htm
- SPX Technologies 10-K FY2025 — https://www.sec.gov/Archives/edgar/data/88205/000008820526000008/spxc-20251231.htm
- Mobileye 10-K FY2025 — https://www.sec.gov/Archives/edgar/data/1910139/000110465926014300/mbly-20251227x10k.htm
- Via Transportation 10-K FY2025 — https://www.sec.gov/Archives/edgar/data/1603015/000160301526000008/via-20251231.htm

**Rating agencies and credit press (Cubic)**
- Moody's rating action 15 Apr 2021 (full text) — https://finance.yahoo.com/news/atlas-cc-acquisition-corp-moodys-225211573.html ; Moody's issuer page (not readable) — https://www.moodys.com/credit-ratings/Atlas-CC-Acquisition-Corp-credit-rating-867623358
- Prospect News issuer index, Atlas CC Acquisition Corp. — https://www.prospectnews.com/cgi-bin/issuerresponse.pl?first=A&issuer=79223
- Octus, "Cubic Corp. Agrees on Out-of-Court Deal With Lenders, Will Receive $175M in Capital" — https://octus.com/resources/articles/cubic-corp-agrees-on-out-of-court-deal/
- cbonds (Fitch B- → CCC-, 9 Jul 2025, headline) — https://cbonds.com/news/3485289/
- Mobility Payments, 17 Feb 2025 (S&P CCC+) — https://www.mobility-payments.com/2025/02/17/ratings-agency-downgrades-cubics-credit-rating-warning-of-onerous-debt-burden/
- LCD/S&P via Yahoo Finance (SD, Feb 2026) — https://finance.yahoo.com/news/us-leveraged-loan-default-rate-182449374.html
- Briefs.co digest (Jul 2026) — https://www.briefs.co/news/cubic-corp-seeks-fresh-financing-a-year-after-prior-restruct/ ; NewsyList (Fitch RD → CCC+) — https://www.newsylist.com/cubic-corporation-rating-change-fitch-downgrade-upgrade-ccc/ ; PitchBook credit wrap 4 Sep 2025 — https://files.pitchbook.com/website/files/pdf/September_4_2025_US_Credit_Markets_Weekly_Wrap.pdf

**Parent / company disclosures**
- Hitachi Rail / Clever Devices completion — https://www.cleverdevices.com/news/hitachi-rail-completes-acquisition-of-clever-devices-expanding-its-portfolio-of-multi-modal-transport-solutions/ ; https://www.hitachi.com/en/press/articles/2026/07/0702a/ ; https://www.metro-magazine.com/news/hitachi-rail-completes-acquisition-of-intelligent-transportation-systems-provider-clever-devices
- Indra FY2025 results — https://www.indragroup.com/cms-content/2026/02/260225-PR-Indra-Group-Results-2025-2.pdf ; https://www.indragroup.com/en/fy-2025-results ; https://www.investing.com/news/company-news/indra-fy25-slides-defense-orders-surge-guidance-beaten-across-metrics-93CH-4525423
- GMV Annual Report 2025 — https://www.gmv.com/es/docs/annual-report-2025 ; non-financial report — https://www.gmv.com/es/docs/informe-no-financiero-2025
- Bouygues FY2025 results (Equans) — https://www.nasdaq.com/press-release/bouygues-very-robust-2025-results-and-free-cash-flow-record-level-2026-02-26 ; https://www.bouygues.com/wp-content/uploads/2026/02/press-release.pdf
- Constellation Software Q4-2025 financial report — https://www.csisoftware.com/wp-content/uploads/2026/04/Q4-2025-Shareholder-Report.pdf
- Luminator ownership — https://www.llcp.com/levine-leichtman-capital-partners-sells-luminator-technology-group/ ; https://mergr.com/audax-private-equity-acquires-luminator-technology-group ; https://www.audaxprivateequity.com/portfolio/luminator-technology-group (not reachable) ; https://pitchbook.com/profiles/company/51352-12
- Flowbird / Arrive — https://www.automotiveworld.com/news/easypark-group-closes-acquisition-of-flowbird-group-to-become-a-leading-global-mobility-platform-provider/ ; https://www.verif.com/en/company/FLOWBIRD-68d9c6a2129923033806a52a/ (not reachable; FY2024 EUR 212.0m via search summary) ; https://craft.co/flowbird-group
- Vix / ICM — https://pitchbook.com/profiles/company/55759-96 ; https://www.icm.limited/ ; https://www.marketscreener.com/insider/DUNCAN-SAVILLE-A07I6P/

**Aggregator fallbacks (low confidence)**
- Luminator — https://growjo.com/company/Luminator_Technology_Group ; https://www.datanyze.com/companies/luminator-technology-group/23249507 ; https://rocketreach.co/luminator-technology-group-profile_b5c697dcf42e0c98 ; https://www.glassdoor.com/Overview/Working-at-Luminator-Technology-Group-EI_IE1179492.11,37.htm
- Avail — https://www.zoominfo.com/c/avail-technologies-inc/1155457838 ; https://growjo.com/company/Avail_Technologies ; https://rocketreach.co/avail-technologies-inc-profile_b5c10e78f42e08be ; https://www.pabusinesscentral.com/articles/avail-technologies-inc/
- GIRO — https://www.datanyze.com/companies/giro/50075133 ; https://www.owler.com/company/giroinc ; https://pitchbook.com/profiles/company/179534-71 ; https://rocketreach.co/giro-profile_b5c6afc5f42e0cf1
- Swiftly — https://getlatka.com/companies/goswift.ly ; https://www.zoominfo.com/c/swiftly-inc/433493203 ; https://pitchbook.com/profiles/company/228874-51 ; https://leadiq.com/c/swiftly-inc/5a1d9dac23000059008d8a58
- Optibus — https://getlatka.com/companies/optibus ; https://www.zoominfo.com/c/optibus-ltd/405371534 ; https://www.owler.com/company/optibus1
- Spare — https://getlatka.com/companies/sparelabs.com ; https://www.zoominfo.com/c/spare-labs-inc/435375703 ; https://tracxn.com/d/companies/sparelabs/__ZiUiHdgMbRxpl9EcQkz4QqPligc4W9dswgQkiv7jK2E ; https://pitchbook.com/profiles/company/223351-93
- Passio — https://www.zoominfo.com/c/passio-technologies/356022765 ; https://www.datanyze.com/companies/passio-technologies/356022765 ; https://www.cience.com/company/passio-technologies/-1856305115728229878
- ETA Transit — https://rocketreach.co/eta-transit-systems-profile_b5e6817ef42e58e0 ; https://www.zoominfo.com/c/eta-transit-systems-inc/346139554
- Vix (aggregator) — https://www.zoominfo.com/c/vix-technology-sa/346091796 ; https://craft.co/vix-technology ; https://rocketreach.co/vix-technology-profile_b5e68d54f42e5899
- Hanover (aggregator) — https://open.endole.co.uk/insight/company/01876684-hanover-displays-limited ; https://growjo.com/company/Hanover_Displays ; https://www.datanyze.com/companies/hanover-displays/45747047
- Masabi (aggregator) — https://open.endole.co.uk/insight/company/04431819-masabi-limited ; https://pomanda.com/company/04431819/masabi-limited

**FX** — ECB euro reference rates, 6 Nov 2026 — https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml

**Sibling files reused:** 08 (INIT regional split, IVU, Modaxo headcount, Berg vendor ranking), 10 (Cubic deal terms), 17 (Berg pool definition and values), 26 (Cubic FY2020 10-K and 2021 LBO data, Via net loss).
