# 17 — Gap fill: top-down bridge from global ITS to public-transit bus ITS (Berg scope resolution + GMI APTS segmentation)

**Research date:** 2026-11-07 | **Topic:** resolve the two scope problems blocking top-down reconciliation — (1) what Berg Insight's EUR 2.55bn Europe / EUR 1.22bn North America "public transport ITS" values include (fare collection? journey planners?) and how the series has evolved edition by edition; (2) capture Global Market Insights' APTS segmentation in full (component × technology × application × mode × deployment × end-use × region) and carve a scope-matched "core public-transit roadway ITS ex-fare" number — then draw the chain global ITS → roadway → APTS → bus and deliver a reconciliation table and a recommended segment × component × geography table for 2025 with 2031 values.

**Research conditions.** The shared WebSearch budget for this run was already exhausted when this agent started (every WebSearch call returned "budget used up"), so **everything below was read directly with `curl` through the session proxy using a browser User-Agent**. Hosts that answered: media.berginsight.com (10th-edition summary PDF, 6 pages, read in full), berginsight.com (the site is a Gatsby build — press-release bodies were retrieved from its `/page-data/<slug>/page-data.json` and static-query JSON files, which hold the full text of every post from 2018 onward), erticonetwork.com, telematicswire.net, giiresearch.com, researchandmarkets.com, gminsights.com (APTS page, full text), precedenceresearch.com, mordorintelligence.com, grandviewresearch.com (report page and Horizon databook pages), imarcgroup.com, futuremarketinsights.com, technavio.com, prnewswire.com, statista.com. Hosts that refused or hid content: marketsandmarkets.com (403), alliedmarketresearch.com (403), fortunebusinessinsights.com (403), marketresearch.com (403), globenewswire.com (403), databridgemarketresearch.com (403), slideshare.net (JavaScript shell — the 2015 Berg deck could not be read), statista.com (chart values pay-walled; only the page shell loaded), and GMI's/Mordor's/IMARC's ITS or APTS sub-pages at every slug tried (404). Confidence key: **high** = primary document read directly or consistent across 2+ independent sources; **medium** = single secondary source; **low** = inferred or unclear scope. Every number labelled **DERIVED** is this agent's arithmetic on sourced inputs and is not a published figure.

---

## 1. Key takeaways

1. **Berg's definition includes fare payment and journey planners — with one important caveat.** The verbatim scope (10th ed. summary, p.2): *"Berg Insight's definition of ITS for public transport includes systems installed in public transport vehicles as well as at terminals, stops, depots and similar. Included are also back-office IT systems which ensure that public transport services can be planned, scheduled and managed to achieve efficient operations. An important part of ITS for public transport further comprises solutions providing travellers with updated information about routes, departure times, possible disturbances and connecting services. The history of these different types of solutions dates back several decades and current state-of-the-art solutions include for example real-time intermodal and multi-operator journey planners, automated fare collection systems using contactless cards or NFC-enabled handsets for account-based ticketing, and advanced mobility analytics software."* AFC and journey planners are thus named as examples of "these different types of solutions", the report has a "2.3.3 Fare payment" section and a "Fare Payment Technologies" figure inside the technology chapter, it profiles pure ticketing vendors (Masabi, FAIRTIQ, Ridango, Snapper, Ticketer, Flowbird, Scheidt & Bachmann, Kentkart), and Berg's own 2018 release attributes the forecast's "particularly strong growth" to "integrated journey planning and fare payment solutions". **Verdict: file 08's assertion is supported (AFC and journey planners are inside the EUR 2.55bn / EUR 1.22bn values).** The caveat: Berg never publishes an application split, and two phrasings ("Conduent … is *also* an international provider of fare collection systems"; "modern ticketing *and* ITS solutions") show Berg treats large fare-system integration as a sibling business, so the EUR values most plausibly carry on-vehicle/stop-level fare equipment and ticketing back-office but not the full value of mega fare-system programmes (Clipper, OMNY, Oyster). Confidence on "fare inside": medium-high; on "how much": low — the model needs an assumed ex-fare haircut (recommended 15–25%, central 20%, taken from GMI's ticketing/electronic-payment mix, Section 4.4).

2. **The full Berg series (six editions, 2014–2030) is now captured from primary text** (Section 3). Europe: EUR 1.03bn (2014) → 1.40 (2017) → 1.56 (2018) → 2.12 (2021) → 2.15 (2022) → 2.55 (2025) → 3.30 (2030F). North America: EUR 0.95bn (2017) → 1.07 (2018) → 0.76 (2021, rebased down) → 0.88 (2022) → 1.22 (2025) → 1.56 (2030F). Combined 2025 EUR 3.77bn (Berg rounds to 3.8), 2030F EUR 4.86bn (rounded 4.9), 5.2% CAGR. **DERIVED 2031 at Berg's own CAGRs: Europe EUR 3.48bn, NA EUR 1.64bn, combined EUR 5.11bn (USD 5.62bn at 1.10).**

3. **Berg's successive forecasts have been accurate for Europe and badly wrong (both ways) for North America.** The Dec-2018 edition forecast Europe 2022 at EUR 1.96bn; the Mar-2024 edition reported 2022 at EUR 2.15bn (+9.7%). The same 2018 edition forecast North America 2022 at EUR 1.37bn; the 2024 edition reported EUR 0.88bn (−35.8%), after the Sep-2022 edition had cut the NA base from EUR 1.07bn (2018) to EUR 0.76bn (2021). NA then grew 11.5% p.a. 2022–25 against an 8.8% forecast. Successive NA forecast CAGRs: 7.5% → 7.3% → 8.1% → 8.8% → 5.0%; Europe: 7.2% → 7.0% → 6.8% → 5.8% → 6.3% → 5.3%. Use 5–6% for Europe with high confidence; treat NA as 5% ± 3pp.

4. **Per-equipped-vehicle economics show Berg's values are broad-scope numbers, not CAD/AVL hardware numbers.** Berg's penetration (90.3% EU / 91.9% NA) is stated for "buses and trams" in public transport, not for the 0.85m / 1.1m registered bus-and-coach parcs (coaches do not carry CAD/AVL; applying 90% to the whole parc is a scope error). Using transit-only denominators from files 05 and 16 (Europe 226k–380k PT buses/trams depending on the VDV/UTPF/DfT/ING ratio used; North America 84.6k–92.4k full-size transit buses, LRVs and streetcars), **DERIVED annual market value per equipped vehicle is EUR 7,500–12,500 in Europe and EUR 14,400–15,700 in North America** (EUR 6,400 if US demand-response vans are added). The NTD bus-mode "communications & information" capex of ~USD 5.7k per active full-size bus per year (file 16) explains only a third of the NA figure — consistent with fare equipment, back-office software, hosting and multi-year service/maintenance being inside Berg's number.

5. **GMI's APTS report is the only public source with a seven-way segmentation of public-transit ITS, and every dimension reconciles arithmetically to USD 6,830.1m (2025) and USD 15,528.2m (2035).** Component: hardware 46.8% / software 33.0% / services 20.1%. Technology: real-time passenger information 30.7%, AVL 26.5%, CAD 17.6%, electronic payment 14.7%, station PIS 10.5%. Application: traffic management 30.1%, fleet management 25.2%, ticketing 24.2%, public-information dissemination 11.2%, passenger safety 9.3%. Mode: roadways 47.6%, railways 30.5%, airways 14.6%, waterways 7.3%. Deployment: on-premise 43.7% / cloud 36.0% / hybrid 20.3%. End use: public transit operators 48.8%, government bodies 26.3%, private fleet operators 24.9%. Region: North America 44.3% (USD 3,024.4m), Europe 29.6% (2,022.4m), Asia Pacific 17.2% (1,172.1m), Latin America 5.0% (344.2m), MEA 3.9% (267.1m); US USD 2.4bn (8% CAGR). Implied 2025–35 CAGRs: software 9.7%, AVL 9.8%, railways 9.7%, APAC 10.1%, cloud 9.2%; hardware 7.7%, roadways 8.0%, NA 7.9%.

6. **GMI's APTS and Berg's public-transport ITS cannot both be "the market" — they measure different things.** Berg EU+NA bus/tram (USD 4.15bn at 1.10) is 61% of GMI's *global, all-mode, fare-inclusive* APTS, and Berg Europe (USD 2.81bn, bus+tram only) is 139% of GMI Europe (USD 2.02bn, all modes). GMI's vendor-share statement (Siemens Mobility >15%; Alstom, Conduent, Cubic, Siemens, Thales = 50%; top-10 = 65.5%) shows its APTS is weighted toward rail-signalling/systems houses and large fare integrators, while Berg counts the aftermarket bus/tram ITS vendor base (Trapeze, INIT, Clever, Conduent, Cubic, Avail, Vontas, IVU, Equans, RATP Smart Systems, Vix, Flowbird, Ticketer…). **Recommendation: anchor the Roadway EU and NA sizes on Berg; use GMI only for (a) component / technology / application mix, (b) growth-rate cross-check, (c) rest-of-world scaling. Never average the two.**

7. **Scope-matched GMI carve-out ("core public-transit roadway ITS ex-fare", DERIVED):** global APTS USD 6,830m → roadways USD 3,250m → remove private-fleet operators (USD 1,551m lower bound if all private-fleet revenue is roadway, USD 2,442m if proportional; midpoint USD 1,996m) → remove ticketing (−24.2%) = **USD 1.18–1.85bn (mid USD 1.51bn)**; additionally removing GMI's "traffic management" application (−30.1%) gives USD 0.71–1.12bn, but that application in an APTS context is operations/headway control (there is no ATMS line in GMI's technology split), so the ex-ticketing-only carve is the scope-matched one. Regionally: NA roadway-public-ex-ticketing ≈ USD 819m and US ≈ USD 650m versus Berg NA USD 1.34bn; Europe ≈ USD 548m versus Berg Europe USD 2.81bn. The gap is the Berg-vs-GMI scope difference in point 6, not a demand signal.

8. **The APTS share of global ITS is not published as a percentage by any umbrella vendor reachable without search.** Precedence, Mordor, Grand View, IMARC, Allied and FMI all carry an APTS / "public transport systems" / "public transportation management" line in their taxonomies, but disclose only the ATMS or traffic-management share (Mordor ATMS 38.05% of ITS; Precedence ATMS 31% of roadway ITS and 27% of railway ITS; Technavio traffic management USD 22.86bn in 2024; FMI traffic management 30% of applications and railways 40% of modes). **DERIVED APTS share = GMI APTS USD 6.83bn ÷ each vendor's 2025 global ITS: 11–17% (MarketsandMarkets 16.1%, Precedence 16.5%, Mordor 14.5%, IMARC 13.2%, Grand View 11.7%, FMI 11.3%).** The chain for the deck is therefore: global ITS USD 41–60bn (vendor range) → roadway 39–48% (Grand View 39.0% / Horizon 46.1%, Precedence 48%; Mordor 61.5% and Allied ~33% are outliers) → APTS ≈ 11–17% of all ITS → bus/roadway APTS 47.6% of APTS → public-sector buyers ~75% → Berg-scope bus/tram EU+NA USD 4.15bn + RoW.

9. **Recommended 2025 Roadway (bus+tram) sizing (DERIVED, USD at 1.10 USD/EUR):** Europe USD 2,805m, North America USD 1,342m, rest of world USD 1,465m (Berg EU+NA scaled by GMI's regional mix, which puts EU+NA at 73.9% of global), **global USD 5.61bn (fare-inclusive) / USD 4.49bn (ex-fare at −20%)**; 2031: Europe USD 3,824m (5.3%), NA USD 1,799m (5.0%), RoW USD 2,452m (9.0%, GMI APAC/LatAm/MEA blended), **global USD 8.07bn (6.3% CAGR) / USD 6.46bn ex-fare.** Component mix from GMI: hardware 46.8%, software 33.0%, services 20.1% in 2025 shifting to 44.6 / 35.2 / 20.1 by 2031. Every cell is flagged in Section 6.

10. **Near-term growth is lower than headline CAGRs.** GMI's own history: USD 5,757.0m (2022) → 6,446.6m (2024) → 6,830.1m (2025) → 7.3bn (2026F) = 5.8–6.9% p.a. before the 8.8% 2026–35 CAGR kicks in; Berg's 10th edition cut both regional CAGRs to 5.0–5.3% from 6.3–8.8% in the 9th. The electric-bus ITS sub-market (Berg "Connected Infrastructure for Electric Buses") is the fast lane: Europe EUR 110.4m (2024) → 359.1m (2029) at 27%, NA EUR 39.7m → 101.6m at 21% — still under 5% of the total.

---

## 2. Berg Insight — scope resolution (what is inside EUR 2.55bn / EUR 1.22bn)

### 2.1 Verbatim scope statements (10th edition summary PDF, March 2026; identical text on GII and Research and Markets listings)

- Definition (p.2): quoted in full in takeaway 1. Source: https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf ; https://www.giiresearch.com/report/ber1994825-public-transport-its-europe-north-america-10th.html ; https://www.researchandmarkets.com/reports/4908109/public-transport-its-in-europe-and-north
- Market statement (p.2): *"The total market value of public transport ITS for buses and trams in Europe is forecasted to grow at a compound annual growth rate (CAGR) of 5.3 percent from € 2.55 billion in 2025 to reach € 3.30 billion by 2030. The penetration of on-board computers with GPS location functionality and wireless communications in buses and trams in Europe is estimated to increase from 90.3 percent in 2025 to 93.9 percent in 2030, however varying considerably between regional markets. In North America, the total market value of public transport ITS is forecasted to grow at a CAGR of 5.0 percent from € 1.22 billion in 2025 to reach € 1.56 billion in 2030 and the penetration rate is estimated to increase from 91.9 percent in 2025 to 94.1 percent in 2030."*
- Product page (p.5): *"The total market value of public transport ITS for buses and trams in these two regions is forecasted to grow at a compound annual growth rate of 5.2 percent from € 3.8 billion in 2025 to reach € 4.9 billion by 2030."* 315 pages, 86 vendor profiles, 30 executive interviews, author Caspar Jansson, EUR 1,800 single-user licence.
- Fleet/context (p.2): 0.85m registered buses and coaches in Europe and 1.1m in North America (2023); ~60bn (Europe) and ~12bn (NA) public-transport journeys per year pre-pandemic; economic value of public transport services EUR 160–175bn (Europe) and EUR 100–115bn (NA) per year.
- Modes named in the context paragraph: local and regional buses and trolleybuses, regional and suburban rail, metros and trams, local waterborne — **but the valued market is explicitly "for buses and trams"** (metro/heavy rail are excluded from the value).

### 2.2 Evidence for and against fare collection / journey planners being inside the value

| # | Evidence | Direction | Source |
|---|---|---|---|
| 1 | Definition names "real-time intermodal and multi-operator journey planners, automated fare collection systems using contactless cards or NFC-enabled handsets for account-based ticketing, and advanced mobility analytics software" as examples of "these different types of solutions" | Inside | 10th ed. PDF p.2 |
| 2 | TOC chapter 2 "ITS Technologies and Solutions": 2.3 Traveller management → 2.3.1 Passenger information, 2.3.2 Entertainment, **2.3.3 Fare payment**; Figure 2.5 "Examples of a multi-modal app journey planner and EMV payment solution"; Figure 2.7 "Fare Payment Technologies" | Inside | 10th ed. PDF p.3; GII TOC |
| 3 | Chapter 3 forecast structure is 3.1.1 Market value forecast / 3.1.2 Regional markets / 3.1.3 Major vendors — **no application split published** | Unknown split | 10th ed. PDF p.3 |
| 4 | Vendor profiles include ticketing-centric companies: FAIRTIQ, Ridango, Scheidt & Bachmann, Masabi, Snapper Services, Ticketer, Flowbird, Vix, Kentkart, Cubic, Conduent | Inside | 10th ed. PDF p.3 |
| 5 | Dec-2018 release, CEO Johan Fagerberg/analyst quote: *"Passenger-facing solutions such as integrated journey planning and fare payment solutions have already reached a relatively high degree of maturity and will experience a particularly strong growth in the coming few years"* — given as the rationale for the forecast | Inside | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--33-billion-by-2022/ |
| 6 | Sep-2022 release, analyst Caspar Jansson: *"Many operators have for example installed new contactless ticketing solutions and passenger counting systems over the last two years"* cited as market activity | Inside | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--39-billion-by-2026/ |
| 7 | 10th ed. p.2: *"The development of ITS has in recent years focused on increasing the level of integration and utilising technology advancements in fare collection solutions."* | Inside | 10th ed. PDF p.2 |
| 8 | Vendor paragraph: *"Clever Devices and Conduent hold leading positions on the North American public transport ITS market, and the latter is **also** an international provider of fare collection systems."* — "also" frames fare collection as a distinct business line | Partly outside (large AFC programmes) | 10th ed. PDF p.2 |
| 9 | TOC 3.4.8 *"The pandemic accelerated uptake of modern ticketing **and** ITS solutions"* — ticketing framed as a sibling of ITS | Partly outside | 10th ed. PDF p.3 |
| 10 | Per-equipped-vehicle value EUR 7.5–12.5k (EU) and EUR 14–16k (NA) per year (Section 3.4) is 1.5–3× the NTD on-board/comms capex intensity (~EUR 5.2k per bus-year, file 16) | Inside (scope must be broad) | DERIVED |
| 11 | Berg's related product "Connected Infrastructure for Electric Buses" (3rd ed.) is sold separately and values e-bus ITS at EUR 150m (2024) — i.e. charging-management ITS is carved out of (or is a small subset of) the main series | Neutral | https://www.berginsight.com/the-its-market-for-electric-buses-in-europe-and-north-america-to-reach--461-million-by-2029/ |

**Verdict.** Journey planners / traveller information: inside (high confidence — it is a named pillar of the definition). Automated fare collection: inside the definition and the vendor universe (medium-high confidence); the value most plausibly includes on-vehicle validators/ETMs, stop-level TVMs where sold with ITS, and ticketing back-office/account-based platforms, but Berg's framing of fare *system* integration as a sibling business and the absence of any application split mean the share cannot be read from Berg. **For the model: treat Berg as fare-inclusive and apply an explicit ex-fare haircut of 15–25% (central 20%).** The 20% sits between GMI's electronic-payment technology share (14.7%) and its ticketing application share (24.2%) (Section 4.4). Sensitivity: at 0% haircut the Roadway EU+NA 2025 size is USD 4.15bn; at 20% USD 3.32bn; at 25% USD 3.11bn (all at 1.10 USD/EUR).

### 2.3 Installed-base and split data points available from Berg

- Penetration of on-board computers with GPS + wireless in buses and trams: Europe 90.3% (2025) → 93.9% (2030); NA 91.9% → 94.1% (10th ed.). Earlier editions: Europe 91.5% (2021) → 95.1% (2026) (8th ed., per file 01; the 8th-edition release body retrieved here does not restate it — the figure comes from the 2022 reseller listing cited in file 01). Jan-2020 release: *"The penetration rate of on-board computers featuring GPS location functionality and wireless communications is now at very high levels in both North America and Western Europe"* (no number).
- **Berg publishes no unit counts of equipped buses/trams in the free summaries and no onboard-hardware / back-office-software / services split.** The report's chapter 1.2 "Bus fleets and public transport utilisation" and chapter 3.1 hold this in the paid Excel dataset. Every installed-base number in Section 3.4 is therefore DERIVED from Berg penetration × sibling-file fleet counts.
- Electric-bus fleet (Berg blog "Smart and secure: How digitalization is transforming public transport", 7 Apr 2025, berginsight.com news corpus): battery-electric bus fleet in Europe >30,000 vehicles in 2024 (growing >40% p.a. over five years); North America ~10,000.

---

## 3. Berg series by edition, 2014–2031

### 3.1 Edition table (EUR bn, nominal; base year value → forecast year value; vendor CAGR)

| Release (edition) | Europe base | Europe forecast | EU CAGR | North America base | NA forecast | NA CAGR | Combined base → forecast (DERIVED sum) | Source |
|---|---|---|---|---|---|---|---|---|
| Aug 2015 (edition not stated in article) | 1.03 (2014) | 1.46 (2019) | 7.2% | n/a in source | n/a | n/a | 1.03 → 1.46 (Europe only) | https://erticonetwork.com/public-transport-its-in-europe-is-a-billion-euro-market/ |
| 21 Dec 2018 (6th ed.) | 1.40 (2017) | 1.96 (2022) | 7.0% | 0.95 (2017) | 1.37 (2022) | 7.5% | 2.35 → 3.33 ("€3.3bn by 2022"), 7.2% | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--33-billion-by-2022/ |
| 21 Jan 2020 (7th ed.) | 1.56 (2018) | 2.16 (2023) | 6.8% | 1.07 (2018) | 1.52 (2023) | 7.3% | 2.63 → 3.68 ("€3.7bn by 2023"), 6.9% | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--37-billion-by-2023/ ; syndicated https://iotbusinessnews.com/2020/01/22/79095-the-public-transport-its-market-in-europe-and-north-america-to-reach-e-3-7-billion-by-2023/ |
| 28 Sep 2022 (8th ed.) | 2.12 (2021) | 2.81 (2026) | 5.8% | 0.76 (2021) | 1.12 (2026) | 8.1% | 2.88 → 3.93 ("€3.9bn by 2026"), 6.4% | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--39-billion-by-2026/ |
| 15 Mar 2024 (9th ed.) | 2.15 (2022) | 2.92 (2027) | 6.3% | 0.88 (2022) | 1.34 (2027) | 8.8% | 3.03 → 4.26 ("€4.3bn by 2027"), 7.1% | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--43-billion-by-2027/ ; https://telematicswire.net/berg-insight-reveals-surging-growth-in-public-transport-its-market/ |
| 23 Mar 2026 (10th ed.) | 2.55 (2025) ("2.6" in release) | 3.30 (2030) | 5.3% | 1.22 (2025) ("1.2" in release) | 1.56 (2030) | 5.0% | 3.77 → 4.86 ("€3.8bn → €4.9bn", 5.2%) | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf ; https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--49-billion-by-2030/ |

Edition numbering: the 10th edition is dated March 2026 and the cadence is biennial, so 9th = 2024, 8th = 2022, 7th = 2020, 6th = 2018 (high confidence from the 10th-ed. "tenth consecutive report" statement and dates); the 2015 release is therefore the 3rd or 4th edition (low confidence; Berg's own site holds no posts before 2018 and the 2015 Slideshare deck could not be read).

### 3.2 Forecast accuracy and revisions (DERIVED from the table)

| Check | Earlier forecast | Later actual / implied | Variance |
|---|---|---|---|
| Europe 2022 | EUR 1.96bn (2018 ed.) | EUR 2.15bn (2024 ed. base) | +9.7% |
| North America 2022 | EUR 1.37bn (2018 ed.) | EUR 0.88bn (2024 ed. base) | −35.8% |
| Europe 2023 | EUR 2.16bn (2020 ed.) | EUR 2.28bn (interpolated 2022→2025) | +5.6% |
| North America 2023 | EUR 1.52bn (2020 ed.) | EUR 0.98bn (interpolated) | −35.5% |
| Europe 2026 | EUR 2.81bn (2022 ed.) | EUR 2.69bn (10th ed. path) | −4.3% |
| North America 2026 | EUR 1.12bn (2022 ed.) | EUR 1.28bn (10th ed. path) | +14.4% |
| Europe 2027 | EUR 2.92bn (2024 ed.) | EUR 2.83bn (10th ed. path) | −3.1% |
| North America 2027 | EUR 1.34bn (2024 ed.) | EUR 1.345bn (10th ed. path) | 0.0% |

Realised CAGRs across base-year points (mixed editions, so partly definitional): Europe 2014→2017 10.8%, 2017→2018 11.4%, 2018→2021 10.8%, 2021→2022 1.4%, 2022→2025 5.9%, 2014→2025 8.6%. North America 2017→2018 12.6%, 2018→2021 −10.8% (rebasing in the 8th edition), 2021→2022 15.8%, 2022→2025 11.5%, 2017→2025 3.2%. Interpretation: Europe's series is stable and has grown 6–11% p.a. in nominal EUR; the NA series was cut by roughly a third in the 2022 edition (pandemic ridership collapse plus, probably, a scope/exchange-rate re-estimate — Berg values the NA market in EUR) and has since outgrown forecasts.

### 3.3 Annual path 2025–2031 on the 10th edition (DERIVED; EUR bn, Europe 5.3%, NA 5.0%)

| Year | Europe | North America | EU+NA | USD at 1.05 | USD at 1.10 | USD at 1.15 |
|---|---|---|---|---|---|---|
| 2025 | 2.550 | 1.220 | 3.770 | 3.96 | 4.15 | 4.34 |
| 2026 | 2.685 | 1.281 | 3.966 | 4.16 | 4.36 | 4.56 |
| 2027 | 2.827 | 1.345 | 4.173 | 4.38 | 4.59 | 4.80 |
| 2028 | 2.977 | 1.412 | 4.390 | 4.61 | 4.83 | 5.05 |
| 2029 | 3.135 | 1.483 | 4.618 | 4.85 | 5.08 | 5.31 |
| 2030 | 3.301 | 1.557 | 4.858 | 5.10 | 5.34 | 5.59 |
| 2031 | 3.476 | 1.635 | 5.111 | 5.37 | 5.62 | 5.88 |

FX: no exchange-rate source was fetched in this run; 1.10 USD/EUR is the illustrative rate already used in file 01 and the model should replace it with its own documented 2025 average rate. The three columns bracket the plausible 2025 range.

Electric-bus ITS sub-series (Berg "Connected Infrastructure for Electric Buses", EUR m): Europe 12.7 (2019) → 62.4 (2024F) at 37.5% [Dec-2020 release]; 57.1 (2022) → 297.2 (2027F) at 39% [May-2023 release]; 110.4 (2024) → 359.1 (2029F) at 27% [Aug-2025 release]. North America 2.7 (2019) → 11.8 (2024F) at 34.2%; 15.5 (2022) → 58.2 (2027F) at 30%; 39.7 (2024) → 101.6 (2029F) at 21%. Sources: https://www.berginsight.com/the-its-market-for-electric-buses-in-europe-and-north-america-to-reach-75-million-by-2024/ ; https://www.berginsight.com/the-its-market-for-electric-buses-in-europe-and-north-america-to-reach--355-million-by-2027/ ; https://www.berginsight.com/the-its-market-for-electric-buses-in-europe-and-north-america-to-reach--461-million-by-2029/ . Combined e-bus ITS EUR 150m (2024) ≈ 4% of the EU+NA total — a growth kicker, not a size driver.

### 3.4 EUR per equipped vehicle (DERIVED; 2025 market value ÷ (transit fleet × Berg penetration))

Berg's penetration is stated for public-transport "buses and trams", so the denominator must be the transit fleet, not the registered bus-and-coach parc. Fleet inputs are from sibling files 05 and 16.

| Case | Fleet basis | Vehicles | × penetration | Equipped | EUR per equipped vehicle-year |
|---|---|---|---|---|---|
| Europe A | ING estimate ~200,000 buses in European public transport (file 05) + ~20,350 LRT/tram vehicles (UITP, file 05) + 5,390 trolleybuses (UITP) | 225,740 | 90.3% | 203,800 | **12,510** |
| Europe B | 33% of 852,180 ACEA EU+EFTA+UK buses & coaches (midpoint of VDV 41%, SDES/UTPF 19–29%, DfT ~28% transit shares in file 05) + trams + trolleybuses | 306,960 | 90.3% | 277,200 | **9,200** |
| Europe C | 41% (German VDV ratio 35,401/85,559) of 852,180 + trams + trolleybuses | 378,540 | 90.3% | 341,800 | **7,460** |
| Europe D (scope error, for reference) | full 0.85m registered buses & coaches | 850,000 | 90.3% | 767,550 | 3,320 |
| North America A | NTD 65,239 active full-size buses (FY2025, file 16) + 16,145 Canadian transit buses (CUTA 2023, file 05) + 2,945 US LRVs/streetcars (file 16) + 233 TTC streetcars | 84,560 | 91.9% | 77,700 | **15,700** |
| North America B | NTD 73,112 fixed-route bus-mode vehicles incl. cutaways + Canada 16,145 + rail 3,178 | 92,440 | 91.9% | 84,950 | **14,360** |
| North America C | + US demand-response fleet (NTD 191,482 total revenue vehicles) + Canada 16,145 | 207,630 | 91.9% | 190,800 | 6,390 |
| North America D (scope error) | full 1.1m registered buses & coaches | 1,100,000 | 91.9% | 1,010,900 | 1,210 |

Reference: NTD bus-mode "communications & information" capital expense per active full-size bus, fleet-weighted, 2025 = USD 5,703 (file 16) ≈ EUR 5,185 at 1.10 — capex only, lumpy, excludes software subscriptions, hosting, maintenance and fare equipment bought under other object classes. The NA per-vehicle value of EUR 14–16k is therefore only reconcilable if Berg's number carries fare equipment, back-office and services (and/or Canadian fare/ITS programmes); the Europe figure (EUR 7.5–12.5k) is similarly broad. Recommended model use: Europe EUR 9–10k and North America EUR 14–15k per equipped bus/tram per year as the fare-inclusive revenue intensity, cut by the ex-fare haircut for the core-scope intensity.

### 3.5 Vendor-ranking statements by edition (qualitative, for the competitive slide)

- 2018: Trapeze and INIT (both regions); IVU (German-speaking Europe, expanding to NA); Clever Devices and Conduent (NA leaders; Conduent also fare collection); Routematch, Cubic, Avail (notable NA shares); ENGIE Ineo and RATP Smart Systems (France); Vix (UK).
- 2020: as 2018 plus "the former [Trapeze] is about to expand into Europe"; Volvo Group named as OEM player; ITxPT-labelled solutions a "clear trend" in mature markets (analyst Adam Björkman).
- 2022: Trapeze "has expanded into Europe with an acquisition"; Cubic and Avail (NA); Volvo and Daimler (OEM); Scania, Iveco, Gillig, New Flyer offer conventional OEM telematics; US Bipartisan Infrastructure Law "up to US$108 billion" for public transport 2022–26 cited as driver.
- 2024: same list; Canadian CAD 2.75bn (EUR 2.0bn) e-bus/charging programme 2021–26 cited; electrification named as the investment theme.
- 2026: Trapeze and INIT (both regions); Clever Devices and Conduent (NA leaders); Cubic, Avail and "the Modaxo brand Vontas" (notable NA shares); Siemens Mobility (software, both regions); Equans and RATP Smart Systems (France); Vix, Flowbird, Ticketer (UK); IVU (DACH); GMV, Indra, Grupo ETRA, Thales, Atron, FARA, Pilotfish, Icomera, Consat, Swarco, Kontron; Volvo, Daimler (OEM).

---

## 4. Global Market Insights — APTS market, full segmentation (edition published August 2026, base year 2025, forecast 2026–2035, USD)

Source for every figure in this section: https://www.gminsights.com/industry-analysis/advanced-public-transportation-system-apts-market (full page text read 2026-11-07); reseller listings https://www.giiresearch.com/report/gmi2019151-advanced-public-transportation-system-apts-market.html and https://www.researchandmarkets.com/reports/6234264/advanced-public-transportation-system-apts (hardware 47%, public transit operators 49%, US USD 2.4bn at 8%). Scope statement (verbatim): *"It covers the hardware, software, and services used to operate and coordinate public transport: vehicle-location and dispatch systems, passenger information, fare collection, traffic-management tools, multimodal interfaces, and associated analytics across bus, rail, airside, and waterborne networks."* Headline: USD 6.8bn (2025; USD 6,830.1m in the share paragraph) → USD 7.3bn (2026) → USD 15.5bn (2035), CAGR 8.8% (2026–35); history USD 5,757.0m (2022) → 6,446.6m (2024). "Implied CAGR" and "2031" columns are DERIVED (2031 = 2025 × (2035/2025)^0.6); segment values sum to the total in every dimension (checked: 6,830.2 / 15,528.2 with rounding).

### 4.1 By component
| Segment | 2025 USD m | Share | 2035 USD m | GMI CAGR | Implied CAGR | 2031 USD m (DERIVED) |
|---|---|---|---|---|---|---|
| Hardware (sensors, display panels, communication devices, onboard computers; GII: ticketing validation devices, on-board units, passenger displays) | 3,198.6 | 46.8% | 6,712.8 | ~7.95% | 7.69% | 4,990 |
| Software (fleet-management platforms, passenger-information systems, traffic-control and analytics) | 2,256.7 | 33.0% | 5,705.1 | ~9.98% | 9.72% | 3,937 |
| Services (implementation and managed services; INIT hosted ITCS for VGF Frankfurt cited) | 1,374.9 | 20.1% | 3,110.3 | ~8.77% | 8.51% | 2,244 |
| Total | 6,830.1 | 100% | 15,528.2 | 8.8% (2026–35) | 8.56% (2025–35) | 11,180 |

### 4.2 By technology
| Segment | 2025 USD m | Share | 2035 USD m | GMI CAGR | Implied CAGR | 2031 (DERIVED) |
|---|---|---|---|---|---|---|
| Real-time passenger information systems | 2,099.6 | 30.7% | 4,431.8 | n/s | 7.76% | 3,287 |
| Automatic vehicle location (AVL) | 1,806.6 | 26.5% | 4,604.1 | ~10.06% | 9.81% | 3,167 |
| Computer-aided dispatch (CAD) | 1,204.8 | 17.6% | 2,816.8 | n/s | 8.86% | 2,006 |
| Electronic payment systems | 1,002.0 | 14.7% | 2,215.9 | n/s | 8.26% | 1,613 |
| Station-level passenger information | 717.2 | 10.5% | 1,459.7 | n/s | 7.36% | 1,099 |

### 4.3 By application
| Segment | 2025 USD m | Share | 2035 USD m | GMI CAGR | Implied CAGR | 2031 (DERIVED) |
|---|---|---|---|---|---|---|
| Traffic management | 2,052.5 | 30.1% | 4,476.8 | n/s | 8.11% | 3,277 |
| Fleet management | 1,724.6 | 25.2% | 3,951.9 | n/s | 8.65% | 2,836 |
| Ticketing solutions | 1,655.6 | 24.2% | 3,686.4 | n/s | 8.33% | 2,676 |
| Public information dissemination | 764.3 | 11.2% | 1,942.6 | ~10.07% | 9.78% | 1,338 |
| Passenger safety and security | 633.2 | 9.3% | 1,470.5 | n/s | 8.79% | 1,050 |

### 4.4 By mode of transportation
| Segment | 2025 USD m | Share | 2035 USD m | GMI CAGR | Implied CAGR | 2031 (DERIVED) |
|---|---|---|---|---|---|---|
| Roadways | 3,249.8 | 47.6% | 6,984.6 | n/s | 7.95% | 5,143 |
| Railways ("signaling and digital-control modernization"; Hitachi Rail Digital Rail Germany EUR 6.3bn programme cited) | 2,079.8 | 30.5% | 5,225.2 | ~9.91% | 9.65% | 3,615 |
| Airways | 999.9 | 14.6% | 2,351.0 | n/s | 8.93% | 1,670 |
| Waterways | 500.7 | 7.3% | 967.4 | n/s | 6.81% | 743 |

### 4.5 By deployment mode
| Segment | 2025 USD m | Share | 2035 USD m | GMI CAGR | Implied CAGR | 2031 (DERIVED) |
|---|---|---|---|---|---|---|
| On-premise | 2,985.5 | 43.7% | 6,476.8 | n/s | 8.05% | 4,751 |
| Cloud | 2,457.5 | 36.0% | 5,944.2 | ~9.49% | 9.23% | 4,175 |
| Hybrid | 1,387.2 | 20.3% | 3,107.2 | n/s | 8.40% | 2,251 |

### 4.6 By end use
| Segment | 2025 USD m | Share | 2035 USD m | GMI CAGR | Implied CAGR | 2031 (DERIVED) |
|---|---|---|---|---|---|---|
| Public transit operators | 3,335.2 | 48.8% | 7,498.6 | 8.7% (GII) | 8.44% | 5,423 |
| Government bodies (regional traffic management, integrated-ticketing mandates) | 1,796.3 | 26.3% | 3,913.1 | n/s | 8.10% | 2,866 |
| Private fleet operators (subscription routing/scheduling/demand-responsive) | 1,698.7 | 24.9% | 4,116.5 | ~9.53% | 9.25% | 2,889 |

### 4.7 By region
| Region | 2025 USD m | Share | 2035 USD m | GMI CAGR | Implied CAGR | 2031 (DERIVED) |
|---|---|---|---|---|---|---|
| North America | 3,024.4 | 44.3% | 6,472.2 | ~8.16% | 7.90% | 4,774 |
| Europe | 2,022.4 | 29.6% | 4,830.8 | ~9.36% | 9.10% | 3,410 |
| Asia Pacific | 1,172.1 | 17.2% | 3,068.4 | ~10.36% | 10.10% | 2,088 |
| Latin America | 344.2 | 5.0% | 689.5 | ~7.44% | 7.19% | 522 |
| Middle East & Africa | 267.1 | 3.9% | 467.4 | ~5.98% | 5.76% | 374 |
| United States (sub-region) | 2,400 | 35.1% of global / 79.4% of NA | n/s | 8% (2026–35) | — | 3,808 (DERIVED at 8%) |

### 4.8 Vendor-share statements (GMI)
- "Siemens Mobility led with over 15% market share in 2025."
- "Top 5 players … Alstom, Conduent Transportation, Cubic Transportation, Siemens Mobility, Thales … collectively held a market share of 50% in 2025."
- "The ten leading suppliers account for 65.5% of the USD 6,830.1 million 2025 market, leaving 34.5% to other providers."
- Other named participants: Hitachi Rail (acquired Thales GTS May 2024), INIT SE (FY2025 revenue EUR 330m; London iBus Next Generation, MARTA Better Breeze), Trapeze, Indra (London ticketing GBP 587m, extendable >GBP 987m; Riyadh), Masabi, Vix, Bytemark, Clever Devices, Genfare, Scheidt & Bachmann (Pittsburgh farebox modernisation), Spare Labs, Optibus, Moovit, Swiftly, Via (2025 revenue USD 434.3m, 821 customers). Context quoted: Siemens Mobility FY2025 revenue EUR 12.4bn; Alstom FY2024/25 EUR 18.5bn; SEPTA Key 2.0 USD 211m award to Cubic (Jan 2025).
- Reading: a market in which Siemens, Alstom and Thales/Hitachi hold ~35–40% is a rail-systems-and-fare-integrator market, which is why GMI's "railways" line grows fastest and why its per-region values do not line up with Berg's aftermarket bus/tram universe.

### 4.9 Scope-matched carve-out: "core public-transit roadway ITS ex-fare" (DERIVED)

| Step | Logic | Global | North America | US | Europe | APAC | LatAm | MEA |
|---|---|---|---|---|---|---|---|---|
| 0 | GMI APTS 2025 (USD m) | 6,830.1 | 3,024.4 | 2,400.0 | 2,022.4 | 1,172.1 | 344.2 | 267.1 |
| 1 | × roadways 47.58% (global mode share applied to every region — GMI gives no region × mode) | 3,249.8 | 1,439.0 | 1,141.9 | 962.3 | 557.7 | 163.8 | 127.1 |
| 2 | × public-sector buyers 75.13% (remove private fleet operators proportionally; lower bound if all private-fleet revenue is roadway = 1,551 global) | 2,441.5 (range 1,551–2,442; mid 1,996) | 1,081.1 | 857.9 | 722.9 | 419.0 | 123.0 | 95.5 |
| 3a | × ex-ticketing 75.76% (remove ticketing application 24.24%) = **scope-matched core roadway public-transit ITS** | **1,849.7 (range 1,175–1,850; mid 1,512)** | **819.1** | **650.0** | **547.7** | **317.4** | **93.2** | **72.3** |
| 3b | alternative: × ex-electronic-payment 85.33% (technology view) | 2,083.4 (range 1,324–2,083) | 922.5 | 732.1 | 616.9 | 357.5 | 105.0 | 81.5 |
| 3c | strict: × ex-ticketing & ex-traffic-management 45.71% | 1,116.0 (range 709–1,116) | 494.2 | 392.2 | 330.5 | 191.5 | 56.2 | 43.6 |

Why 3a is the scope-matched line: GMI's technology split (RTPI, AVL, CAD, EPS, station PIS) contains no roadside traffic-management line, so its "traffic management" *application* is AVL/CAD applied to transit operations control (headway management, dispatch), which is in scope; only ticketing/electronic payment is adjacent. Line 3c is shown because the task asked for it; it should be read as a floor.

### 4.10 Reconciliation to Berg (DERIVED; USD at 1.10)

| Comparison | Berg (bus + tram, fare-inclusive) | GMI | Ratio |
|---|---|---|---|
| EU + NA vs global APTS (all modes, all buyers) | USD 4.15bn | USD 6.83bn | 60.7% |
| North America (bus+tram) vs NA APTS (all modes) | USD 1.34bn | USD 3.02bn | 44.4% |
| North America (bus+tram, US+Canada) vs US APTS (all modes) | USD 1.34bn | USD 2.40bn | 55.9% |
| Europe (bus+tram) vs Europe APTS (all modes) | USD 2.81bn | USD 2.02bn | 138.7% |
| NA bus+tram vs GMI NA core roadway public-transit ex-ticketing (line 3a) | USD 1.34bn | USD 0.82bn | 164% |
| Europe bus+tram vs GMI Europe line 3a | USD 2.81bn | USD 0.55bn | 512% |

Conclusion: the two sources diverge by a factor of 1.6× (NA) to 5× (Europe) on the like-for-like bus line, far more than any FX or fare haircut explains. Berg counts the aftermarket vendor base bottom-up by region (86 profiled vendors, 30 interviews, Europe-weighted); GMI's region values are top-down allocations of a global number dominated by rail-systems revenue and skewed to North America (44%). For a Europe + North America bus case, Berg is the defensible anchor; GMI contributes mix and rest-of-world scaling only.

---

## 5. Umbrella chain: global ITS → roadway → APTS → bus (what each vendor discloses)

| Vendor (edition) | Global ITS 2025 | Forecast | Roadway / mode share | Public-transport (APTS) disclosure | Other shares | Source | Confidence |
|---|---|---|---|---|---|---|---|
| Grand View Research (2026–33 ed.) | USD 58.3bn (2026: 62.7bn) | USD 128.2bn (2033), 10.8% | Roadway 39.0% (2025); NA 34.9%; US largest country | "APTS … expected to register the highest CAGR" in both roadway and railway system types; ATMS largest; smart ticketing fastest railway application; no % | Offering: hardware largest; services fastest | https://www.grandviewresearch.com/industry-analysis/intelligent-transportation-systems-industry | High (page read) |
| Grand View Horizon databook (2024 base) | USD 54,479.5m (2024) | USD 90,389.7m (2030), 9.2% | Roadway USD 25,107.7m = 46.09% (2024); NA USD 19,184.1m = 35.2%, roadway 48.71% of NA; APAC USD 24,009.1m by 2030 | Segment tree is mode × offering only (roadway hardware: interface boards, sensors, surveillance cameras, telecom networks, monitoring/detection; software: visualization, video detection management, **transit management software**; services: cloud, business, professional) — no APTS line in the databook | — | https://www.grandviewresearch.com/horizon/outlook/intelligent-transportation-system-market-size/global ; https://www.grandviewresearch.com/horizon/outlook/intelligent-transportation-system-market/north-america ; https://www.grandviewresearch.com/horizon/outlook/intelligent-transportation-system-market-size/global/scope | High |
| Mordor Intelligence (2026–31 ed.) | USD 47.01bn (2025); 52.60bn (2026) | USD 83.10bn (2031), 9.58% | Roadways 61.45% (2025); maritime 6.35% (fastest, 12.86%) | Type: ATMS 38.05% (2025); CVIS fastest 15.12%; "ATIS, ATPS, and APTS see moderate growth"; application "Public Transport and Ticketing" listed; no % | Hardware 48.55%; software 13.84% CAGR; cloud 53.55%; NA 27.65%; APAC 10.16% CAGR | https://www.mordorintelligence.com/industry-reports/intelligent-transport-systems-market | High |
| Precedence Research (2026–35 ed.) | USD 41.42bn (2025); 44.23bn (2026) | USD 77.80bn (2035), 6.51% | Roadway ~48% (2025); NA ~43%; US USD 12.49bn (2025) → 23.63bn (2035) | Roadway system type: ATMS 31%, **APTS fastest at 8.8% CAGR**; railway system type: ATMS 27%, **APTS 9.8% CAGR**; overall ATMS ~33%; traffic-management application ~34% | Roadway hardware 46%; railway hardware 45.6%; services fastest | https://www.precedenceresearch.com/intelligent-transportation-system-market | High |
| IMARC (2026–34 ed.) | USD 51.8bn (2025) | USD 101.2bn (2034), 7.49% | Roadways largest mode (no %) | Product segment "Public Transport Systems" listed; network-management systems (ATMS, road user charging, congestion charging) largest; intelligent traffic control largest application; passenger-information and ticketing management applications listed; no % | Hardware largest offering; software incl. "transit management system" | https://www.imarcgroup.com/intelligent-transport-systems-market | High |
| Future Market Insights (2025–35 ed.) | USD 60.4bn (2025) | USD 137.8bn (2035), 8.6% | **Railways 40%** (largest mode, "metros and freight corridors") | Application "Public Transportation Management" listed; traffic management 30% of applications; no % for public transport | Government buyers 55% of end use; India ITS 10% CAGR, "real-time bus tracking systems deployed in 23 metropolitan regions by 2025" | https://www.futuremarketinsights.com/reports/intelligent-transportation-system-market | Medium |
| MarketsandMarkets (Aug-2025 ed., via PR Newswire) | USD 42.55bn (2025) | USD 55.36bn (2030), 5.4% | Roadways largest mode; APAC to dominate | Information-management application fastest; no APTS line in release | — | https://www.prnewswire.com/news-releases/intelligent-transportation-system-market-worth-55-36-billion-by-2030---exclusive-report-by-marketsandmarkets-302535668.html | High (release) |
| Allied Market Research (2023–32 ed., via PR Newswire) | USD 48.36bn (2022) | USD 98.02bn (2032), 7.5% | Roadways "nearly one-third" (2022), 8.3% CAGR; APAC one-third of revenue | Application taxonomy includes "Advanced Public Transportation System"; "other" application ~one-fourth (largest, 9.1% CAGR); no APTS % | Hardware "half" of revenue (2022), 7.8% CAGR | https://www.prnewswire.com/news-releases/intelligent-transportation-system-its-market-to-reach-98-02-billion-globally-by-2032-at-7-5-cagr-allied-market-research-302003300.html | High (release) |
| Technavio (2026–30 ed.) | not stated (increment only) | +USD 49.18bn 2025–30, 9.6% | — | ATMS largest type; traffic-management application USD 22.86bn (2024); no APTS % | "Market opportunities USD 77.20bn" | https://www.technavio.com/report/intelligent-transport-system-market-industry-analysis | Medium |
| Statista "ITS market by segment 2020–2031" | pay-walled (values masked as "**") | — | — | Chart is by service/hardware/software, not by application | — | https://www.statista.com/statistics/1339654/global-intelligent-transportation-systems-market-size-by-segment | n/a (gap) |

DERIVED APTS share of global ITS (GMI APTS USD 6.83bn ÷ vendor total): MarketsandMarkets 16.1%, Precedence 16.5%, Mordor 14.5%, IMARC 13.2%, Grand View 11.7%, FMI 11.3% (Fortune BI USD 31.14bn from file 01 → 21.9%, outlier). Use **~14% (range 11–17%)** as the APTS-of-ITS share on the bridge slide, labelled as a cross-vendor derivation.

Bridge (2025, DERIVED, USD): global ITS ~USD 42–58bn → roadway ITS ~39–48% ≈ USD 17–28bn → APTS ≈ 11–17% of all ITS ≈ USD 6.8bn (GMI, all modes) → roadway APTS 47.6% ≈ USD 3.25bn → public-sector roadway APTS ≈ USD 1.6–2.4bn → ex-ticketing ≈ USD 1.2–1.9bn (GMI basis) **versus** Berg EU+NA bus/tram USD 4.15bn fare-inclusive / USD 3.32bn ex-fare — the Berg figure is the one to carry, with the GMI chain shown as the top-down cross-check that under-counts the bus aftermarket.

---

## 6. Recommended segment × component × geography table (2025 and 2031; USD m; every cell DERIVED unless marked)

Basis: Roadway Europe and North America = Berg 10th edition (published, EUR) converted at 1.10; Roadway rest of world = Berg EU+NA scaled by GMI's regional mix (EU+NA = 73.9% of global APTS → RoW = 26.1%; RoW 2031 grown at the GMI APAC/LatAm/MEA blended implied CAGR of 8.96%); component split = GMI global APTS mix (2025: HW 46.8% / SW 33.0% / SVC 20.1%; 2031: 44.6 / 35.2 / 20.1); ex-fare = −20% haircut (Section 2.2). Railway line = GMI "railways" mode (global, includes signalling/digital-control modernisation and airside/waterborne excluded) allocated by GMI regional shares — a placeholder for the rail workstream (files 03/09) to override.

| Segment | Geography | 2025 total | of which hardware | software | services | 2025 ex-fare (−20%) | 2031 total | 2031 hardware | software | services | 2031 ex-fare | CAGR 25–31 | Basis / flag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Roadway (bus+tram) | Europe | **2,805** | 1,314 | 927 | 565 | 2,244 | **3,824** | 1,706 | 1,346 | 772 | 3,059 | 5.3% | Berg EUR 2.55bn → 3.476bn (2031 extrapolated one year at 5.3%); FX 1.10; mix GMI |
| Roadway (bus+tram) | North America | **1,342** | 628 | 443 | 270 | 1,074 | **1,799** | 802 | 633 | 363 | 1,439 | 5.0% | Berg EUR 1.22bn → 1.635bn; FX 1.10; mix GMI |
| Roadway (bus+tram) | Rest of world | 1,465 | 686 | 484 | 295 | 1,172 | 2,452 | 1,094 | 863 | 495 | 1,961 | 9.0% | Berg EU+NA × (26.1/73.9) from GMI regional mix; growth = GMI APAC/LatAm/MEA blend; low confidence |
| **Roadway (bus+tram)** | **Global** | **5,612** | 2,628 | 1,854 | 1,130 | **4,490** | **8,075** | 3,601 | 2,842 | 1,631 | **6,460** | **6.3%** | Sum of above |
| Railway (GMI proxy) | North America | 921 | 431 | 304 | 185 | n/a | 1,601 | 714 | 564 | 323 | n/a | 9.7% | GMI railways USD 2,079.8m × NA 44.3%; placeholder |
| Railway (GMI proxy) | Europe | 616 | 288 | 203 | 124 | n/a | 1,070 | 477 | 377 | 216 | n/a | 9.7% | × Europe 29.6%; placeholder |
| Railway (GMI proxy) | Rest of world | 543 | 254 | 179 | 109 | n/a | 944 | 421 | 332 | 190 | n/a | 9.7% | × RoW 26.1%; placeholder |
| Railway (GMI proxy) | Global | 2,080 (published) | 974 | 687 | 419 | n/a | 3,615 | 1,612 | 1,273 | 729 | n/a | 9.65% | GMI railways 2,079.8 → 5,225.2 (2035); 2031 interpolated |

Sanity check on rest-of-world (DERIVED, low confidence): the non-EU/NA transit bus parc is ~1.0–1.2m vehicles (China 630,100 public buses/trolleybuses end-2025; India ~147,000 SRTU buses; Japan 57,914 route buses; Australia ~42,000; LatAm and MENA city fleets — file 05). At EUR 1,000–1,500 per vehicle-year (a tenth of the Europe intensity, reflecting mandated low-cost GPS/AVL in China and India), RoW is EUR 1.0–1.8bn ≈ USD 1.1–2.0bn, bracketing the USD 1.47bn used above.

Alternative anchors the model may show as a range: GMI roadways × public-sector share = USD 1.55–2.44bn global (fare-inclusive) — i.e. a top-down global bus number 2.3–3.6× smaller than the Berg-based USD 5.6bn; the deck should show the Berg-based figure as the base case and disclose the GMI-based figure as the low case with the scope explanation in Section 4.10.

---

## 7. Findings table

| Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Berg definition of public-transport ITS | vehicles + terminals/stops/depots + back-office planning/scheduling/management IT + traveller information; examples incl. journey planners, AFC, analytics | text | 2026 | EU+NA | Bus+tram | Berg Insight 10th ed. summary | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf | high | verbatim in Section 2.1 |
| Public transport ITS market, Europe | 2.55 → 3.30 | EUR bn | 2025 → 2030 | Europe | Bus+tram | Berg 10th ed. | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf | high | 5.3% CAGR |
| Public transport ITS market, North America | 1.22 → 1.56 | EUR bn | 2025 → 2030 | North America | Bus+tram | Berg 10th ed. | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf | high | 5.0% CAGR |
| Public transport ITS, EU+NA combined | 3.8 → 4.9 | EUR bn | 2025 → 2030 | EU+NA | Bus+tram | Berg 10th ed. product page | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf | high | 5.2% CAGR; exact sum 3.77 → 4.86 |
| On-board computer penetration (GPS + wireless) | EU 90.3 → 93.9; NA 91.9 → 94.1 | % of PT buses/trams | 2025 → 2030 | EU; NA | On-board units | Berg 10th ed. | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf | high | "varying considerably between regional markets" |
| Registered buses & coaches | 0.85 (EU); 1.1 (NA) | million | 2023 | EU; NA | Fleet context | Berg 10th ed. | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf | high | parc, not transit fleet |
| Economic value of public transport services | 160–175 (EU); 100–115 (NA) | EUR bn p.a. | c.2025 | EU; NA | Context | Berg 10th ed. | https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf | high | ITS ≈ 1.5% (EU) / 1.1% (NA) of PT service value (DERIVED) |
| Public transport ITS, Europe (9th ed.) | 2.15 → 2.92 | EUR bn | 2022 → 2027 | Europe | Bus+tram | Berg release 15 Mar 2024 | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--43-billion-by-2027/ | high | 6.3% CAGR; also Telematics Wire |
| Public transport ITS, NA (9th ed.) | 0.88 → 1.34 | EUR bn | 2022 → 2027 | North America | Bus+tram | Berg release 15 Mar 2024 | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--43-billion-by-2027/ | high | 8.8% CAGR |
| Public transport ITS, Europe (8th ed.) | 2.12 → 2.81 | EUR bn | 2021 → 2026 | Europe | Bus+tram | Berg release 28 Sep 2022 | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--39-billion-by-2026/ | high | 5.8% CAGR |
| Public transport ITS, NA (8th ed.) | 0.76 → 1.12 | EUR bn | 2021 → 2026 | North America | Bus+tram | Berg release 28 Sep 2022 | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--39-billion-by-2026/ | high | 8.1% CAGR; BIL "up to US$108bn" for transit 2022–26 cited |
| Public transport ITS, Europe (7th ed.) | 1.56 → 2.16 | EUR bn | 2018 → 2023 | Europe | Bus+tram | Berg release 21 Jan 2020 | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--37-billion-by-2023/ | high | 6.8% CAGR |
| Public transport ITS, NA (7th ed.) | 1.07 → 1.52 | EUR bn | 2018 → 2023 | North America | Bus+tram | Berg release 21 Jan 2020 | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--37-billion-by-2023/ | high | 7.3% CAGR |
| Public transport ITS, Europe (6th ed.) | 1.40 → 1.96 | EUR bn | 2017 → 2022 | Europe | Bus+tram | Berg release 21 Dec 2018 | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--33-billion-by-2022/ | high | 7.0% CAGR |
| Public transport ITS, NA (6th ed.) | 0.95 → 1.37 | EUR bn | 2017 → 2022 | North America | Bus+tram | Berg release 21 Dec 2018 | https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--33-billion-by-2022/ | high | 7.5% CAGR; Routematch named |
| Public transport ITS, Europe (2015 release) | 1.03 → 1.46 | EUR bn | 2014 → 2019 | Europe | Bus (+tram) | ERTICO citing Berg | https://erticonetwork.com/public-transport-its-in-europe-is-a-billion-euro-market/ | high | 7.2% CAGR; Swarco and Volvo named |
| Electric-bus ITS market | EU 110.4 → 359.1 (27%); NA 39.7 → 101.6 (21%) | EUR m | 2024 → 2029 | EU; NA | E-bus ITS | Berg release 28 Aug 2025 | https://www.berginsight.com/the-its-market-for-electric-buses-in-europe-and-north-america-to-reach--461-million-by-2029/ | high | earlier eds.: EU 12.7 (2019), 57.1 (2022); NA 2.7 (2019), 15.5 (2022) |
| Battery-electric bus fleet | >30,000 (EU); ~10,000 (NA) | vehicles | 2024 | EU; NA | Fleet | Berg blog 7 Apr 2025 (site news corpus) | https://www.berginsight.com/news/ | medium | ">40% annual growth" in Europe over five years |
| EUR per equipped vehicle-year | EU 7,460–12,510; NA 14,360–15,700 | EUR | 2025 | EU; NA | Bus+tram | DERIVED (Berg value ÷ fleet × penetration) | see Section 3.4 | low-medium | fleet inputs from files 05 and 16 |
| Berg 2031 extrapolation | EU 3.48; NA 1.64; total 5.11 | EUR bn | 2031 | EU+NA | Bus+tram | DERIVED at Berg CAGRs | Section 3.3 | medium | USD 5.62bn at 1.10 |
| GMI APTS market size | 6.8 (6,830.1) → 7.3 → 15.5 | USD bn | 2025 → 2026 → 2035 | Global | APTS all modes | GMI | https://www.gminsights.com/industry-analysis/advanced-public-transportation-system-apts-market | high | 8.8% CAGR 2026–35; history 5,757.0 (2022), 6,446.6 (2024) |
| GMI component split | HW 3,198.6; SW 2,256.7; SVC 1,374.9 | USD m | 2025 | Global | APTS | GMI | same | high | 2035: 6,712.8 / 5,705.1 / 3,110.3 |
| GMI technology split | RTPI 2,099.6; AVL 1,806.6; CAD 1,204.8; EPS 1,002.0; station PIS 717.2 | USD m | 2025 | Global | APTS | GMI | same | high | 2035: 4,431.8 / 4,604.1 / 2,816.8 / 2,215.9 / 1,459.7 |
| GMI application split | traffic mgmt 2,052.5; fleet mgmt 1,724.6; ticketing 1,655.6; PID 764.3; safety 633.2 | USD m | 2025 | Global | APTS | GMI | same | high | 2035: 4,476.8 / 3,951.9 / 3,686.4 / 1,942.6 / 1,470.5 |
| GMI mode split | roadways 3,249.8; railways 2,079.8; airways 999.9; waterways 500.7 | USD m | 2025 | Global | APTS | GMI | same | high | 2035: 6,984.6 / 5,225.2 / 2,351.0 / 967.4; railways ~9.91% CAGR |
| GMI deployment split | on-prem 2,985.5; cloud 2,457.5; hybrid 1,387.2 | USD m | 2025 | Global | APTS | GMI | same | high | 2035: 6,476.8 / 5,944.2 / 3,107.2 |
| GMI end-use split | transit operators 3,335.2; government 1,796.3; private fleets 1,698.7 | USD m | 2025 | Global | APTS | GMI | same | high | 2035: 7,498.6 / 3,913.1 / 4,116.5 |
| GMI regional split | NA 3,024.4; EU 2,022.4; APAC 1,172.1; LatAm 344.2; MEA 267.1 | USD m | 2025 | Regions | APTS | GMI | same | high | 2035: 6,472.2 / 4,830.8 / 3,068.4 / 689.5 / 467.4 |
| GMI US APTS | 2.4 | USD bn | 2025 | US | APTS | GMI via GII / R&M | https://www.giiresearch.com/report/gmi2019151-advanced-public-transportation-system-apts-market.html | high | 8% CAGR 2026–35 |
| GMI vendor shares | Siemens Mobility >15%; top-5 50%; top-10 65.5% | % | 2025 | Global | APTS | GMI | https://www.gminsights.com/industry-analysis/advanced-public-transportation-system-apts-market | medium | top-5: Alstom, Conduent, Cubic, Siemens, Thales |
| GMI core roadway public-transit ex-ticketing carve-out | 1,175–1,850 (mid 1,512) | USD m | 2025 | Global | Bus ITS ex-fare | DERIVED | Section 4.9 | low | NA 819; US 650; EU 548 |
| Grand View ITS | 58.3 → 128.2; roadway 39.0%; NA 34.9% | USD bn; % | 2025 → 2033 | Global | All ITS | Grand View Research | https://www.grandviewresearch.com/industry-analysis/intelligent-transportation-systems-industry | high | APTS fastest-growing system type (roadway and railway) |
| Grand View Horizon ITS | 54,479.5 → 90,389.7; roadway 25,107.7 (46.09%); NA 19,184.1 (35.2%) | USD m | 2024 → 2030 | Global; NA | All ITS | Grand View Horizon | https://www.grandviewresearch.com/horizon/outlook/intelligent-transportation-system-market-size/global | high | NA roadway 48.71% |
| Mordor ITS | 47.01 (2025) → 52.60 (2026) → 83.10 (2031); ATMS 38.05%; roadways 61.45%; HW 48.55%; cloud 53.55%; NA 27.65% | USD bn; % | 2025–2031 | Global | All ITS | Mordor Intelligence | https://www.mordorintelligence.com/industry-reports/intelligent-transport-systems-market | high | APTS "moderate growth", no % |
| Precedence ITS | 41.42 (2025) → 77.80 (2035); roadway 48%; ATMS 31% of roadway, APTS 8.8% CAGR; railway ATMS 27%, APTS 9.8% CAGR; NA 43%; US 12.49bn | USD bn; % | 2025–2035 | Global | All ITS | Precedence Research | https://www.precedenceresearch.com/intelligent-transportation-system-market | high | |
| IMARC ITS | 51.8 → 101.2 | USD bn | 2025 → 2034 | Global | All ITS | IMARC | https://www.imarcgroup.com/intelligent-transport-systems-market | high | "Public Transport Systems" product segment; no % |
| FMI ITS | 60.4 → 137.8; railways 40%; traffic mgmt 30%; government 55% | USD bn; % | 2025 → 2035 | Global | All ITS | Future Market Insights | https://www.futuremarketinsights.com/reports/intelligent-transportation-system-market | medium | "Public Transportation Management" application; no % |
| MarketsandMarkets ITS | 42.55 → 55.36 | USD bn | 2025 → 2030 | Global | All ITS | M&M via PR Newswire | https://www.prnewswire.com/news-releases/intelligent-transportation-system-market-worth-55-36-billion-by-2030---exclusive-report-by-marketsandmarkets-302535668.html | high | 5.4% CAGR; roadways largest; APAC to dominate |
| MarketsandMarkets APC + PIS | 9.70 → 14.80 | USD bn | 2025 → 2030 | Global | APC + PIS | M&M via PR Newswire | https://www.prnewswire.com/news-releases/automated-passenger-counting-and-information-system-market-worth-14-80-billion-by-2030---exclusive-report-by-marketsandmarkets-302501027.html | high | 8.8% CAGR; railways largest PIS application share 2025; APAC fastest; regions covered NA/EU/APAC/RoW (NA and APAC values not in release) |
| Allied ITS | 48.36 → 98.02; roadways ~1/3; hardware ~1/2; APAC ~1/3 | USD bn; % | 2022 → 2032 | Global | All ITS | Allied via PR Newswire | https://www.prnewswire.com/news-releases/intelligent-transportation-system-its-market-to-reach-98-02-billion-globally-by-2032-at-7-5-cagr-allied-market-research-302003300.html | high | APTS is an application segment; "other" ~1/4; no APTS % |
| Technavio ITS | +49.18 (2025–30), 9.6%; traffic management 22.86 (2024) | USD bn | 2024–2030 | Global | All ITS | Technavio | https://www.technavio.com/report/intelligent-transport-system-market-industry-analysis | medium | ATMS largest type |
| APTS share of global ITS | 11–17 (central ~14) | % | 2025 | Global | APTS | DERIVED (GMI ÷ vendor totals) | Section 5 | low-medium | no vendor publishes it |
| Recommended Roadway global size | 5,612 (fare-incl.) / 4,490 (ex-fare) → 8,075 / 6,460 | USD m | 2025 → 2031 | Global | Bus+tram | DERIVED | Section 6 | low-medium | EU 2,805 → 3,824; NA 1,342 → 1,799; RoW 1,465 → 2,452 |

---

## 8. Company notes surfaced in this workstream (share statements only — profiles are in files 08/09)

| Company | Statement | Source |
|---|---|---|
| Siemens Mobility | ">15% share" of GMI's USD 6.83bn APTS market (2025); FY2025 revenue EUR 12.4bn, 11% organic service growth; "prominent vendor of software in both Europe and North America" (Berg) | GMI APTS page; Berg 10th ed. |
| Alstom, Conduent Transportation, Cubic Transportation Systems, Thales (with Siemens) | top-5 = 50% of GMI APTS 2025; Alstom FY24/25 revenue EUR 18.5bn; Conduent transit unit sold to Modaxo (file 08); Cubic SEPTA Key 2.0 USD 211m (Jan 2025); Thales GTS → Hitachi Rail (May 2024) | GMI APTS page |
| Trapeze Group (Modaxo), INIT | "significant installed bases in both regions" in every Berg edition 2018–2026; INIT FY2025 revenue EUR 330m (GMI) | Berg releases; GMI |
| Clever Devices, Conduent | NA leaders in every Berg edition; Conduent "also an international provider of fare collection systems" | Berg releases |
| Cubic, Avail Technologies, Vontas (Modaxo), Routematch (2018 only) | "notable/major market shares in North America" | Berg releases |
| IVU | dominant in German-speaking Europe; "expanded to North America" (2018) | Berg releases |
| Equans (ENGIE Ineo), RATP Smart Systems | leaders in France | Berg 2018, 2026 |
| Vix, Flowbird, Ticketer | major UK providers (fare-centric) | Berg 2026 |
| Indra | London ticketing GBP 587m (extendable >GBP 987m); Riyadh six lines / 176 km / 85 stations / >800 buses | GMI APTS page |
| Via Transportation | 2025 revenue USD 434.3m, 821 customers, 30+ countries | GMI APTS page |

---

## 9. Gaps and what would close them

1. **Berg application split (fare vs CAD/AVL vs PIS vs back-office vs services) and equipped-vehicle unit counts** exist only in the paid report/Excel (EUR 1,800). Buying it would replace the assumed 20% ex-fare haircut and the DERIVED per-vehicle values with published ones.
2. **The 2015 Slideshare deck ("Berg Insight ITS in public transport") and any 2016/2017 release** could not be read (JavaScript shell; Berg's site holds no posts before Dec 2018), so the 2014–2017 Europe link relies on the ERTICO article and the North American series starts in 2017.
3. **No umbrella vendor publishes APTS as a percentage of ITS on a free page**; the 11–17% share is a cross-vendor derivation. MarketsandMarkets, Allied and Fortune pages are 403 to this session; Statista is pay-walled.
4. **MarketsandMarkets APC & PIS regional values** (North America, APAC) are not in the PR Newswire release; file 02 holds the Europe (USD 3,152.3m, 2025) and US values from the vendor's own regional pages, which this session could not reach.
5. **GMI region × mode and region × application cross-tabs** are not public, so regional carve-outs apply global shares (Section 4.9) and the rail rows in Section 6 are placeholders.
6. **FX**: 1.10 USD/EUR is illustrative; the model needs a documented 2025 average (the three-column sensitivity in Section 3.3 brackets it).
7. **Rest-of-world bus ITS** has no direct source; the USD 1.47bn is a GMI-mix scaling of Berg and the fleet × intensity check uses assumed EUR 1,000–1,500 per vehicle.

---

## 10. Source list (all read directly on 2026-11-07 unless marked "link only")

**Berg Insight (primary)**
- https://media.berginsight.com/2026/03/23160541/bi-its10-ps.pdf — Public Transport ITS in Europe and North America, 10th ed. summary (6 pp.)
- https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--49-billion-by-2030/ — release 23 Mar 2026 (body via site page-data JSON)
- https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--43-billion-by-2027/ — release 15 Mar 2024
- https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--39-billion-by-2026/ — release 28 Sep 2022
- https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--37-billion-by-2023/ — release 21 Jan 2020
- https://www.berginsight.com/the-public-transport-its-market-in-europe-and-north-america-to-reach--33-billion-by-2022/ — release 21 Dec 2018
- https://www.berginsight.com/the-its-market-for-electric-buses-in-europe-and-north-america-to-reach--461-million-by-2029/ ; https://www.berginsight.com/the-its-market-for-electric-buses-in-europe-and-north-america-to-reach--355-million-by-2027/ ; https://www.berginsight.com/the-its-market-for-electric-buses-in-europe-and-north-america-to-reach-75-million-by-2024/ — e-bus ITS releases
- https://www.berginsight.com/public-transport-its-in-europe-and-north-america — report page; https://www.berginsight.com/news/ — news corpus (incl. 7 Apr 2025 blog on e-bus fleets)
- https://www.giiresearch.com/report/ber1994825-public-transport-its-europe-north-america-10th.html ; https://www.researchandmarkets.com/reports/4908109/public-transport-its-in-europe-and-north — reseller listings reproducing the 10th-ed. executive summary and TOC
- https://erticonetwork.com/public-transport-its-in-europe-is-a-billion-euro-market/ — ERTICO, 24 Aug 2015
- https://telematicswire.net/berg-insight-reveals-surging-growth-in-public-transport-its-market/ — Telematics Wire, 19 Mar 2024
- https://iotbusinessnews.com/2020/01/22/79095-the-public-transport-its-market-in-europe-and-north-america-to-reach-e-3-7-billion-by-2023/ — link only (cited inside Berg's site)
- https://www.slideshare.net/slideshow/berg-insight-its-in-public-transport/51763906 — not readable (JavaScript shell)

**Global Market Insights (APTS)**
- https://www.gminsights.com/industry-analysis/advanced-public-transportation-system-apts-market
- https://www.giiresearch.com/report/gmi2019151-advanced-public-transportation-system-apts-market.html
- https://www.researchandmarkets.com/reports/6234264/advanced-public-transportation-system-apts

**Umbrella ITS vendors**
- https://www.grandviewresearch.com/industry-analysis/intelligent-transportation-systems-industry
- https://www.grandviewresearch.com/horizon/outlook/intelligent-transportation-system-market-size/global ; https://www.grandviewresearch.com/horizon/outlook/intelligent-transportation-system-market/north-america ; https://www.grandviewresearch.com/horizon/outlook/intelligent-transportation-system-market-size/global/scope
- https://www.mordorintelligence.com/industry-reports/intelligent-transport-systems-market
- https://www.precedenceresearch.com/intelligent-transportation-system-market
- https://www.imarcgroup.com/intelligent-transport-systems-market
- https://www.futuremarketinsights.com/reports/intelligent-transportation-system-market
- https://www.technavio.com/report/intelligent-transport-system-market-industry-analysis
- https://www.prnewswire.com/news-releases/intelligent-transportation-system-market-worth-55-36-billion-by-2030---exclusive-report-by-marketsandmarkets-302535668.html
- https://www.prnewswire.com/news-releases/automated-passenger-counting-and-information-system-market-worth-14-80-billion-by-2030---exclusive-report-by-marketsandmarkets-302501027.html
- https://www.prnewswire.com/news-releases/intelligent-transportation-system-its-market-to-reach-98-02-billion-globally-by-2032-at-7-5-cagr-allied-market-research-302003300.html
- https://www.statista.com/statistics/1339654/global-intelligent-transportation-systems-market-size-by-segment — pay-walled
- Blocked (403/404): marketsandmarkets.com, alliedmarketresearch.com, fortunebusinessinsights.com, marketresearch.com, globenewswire.com, databridgemarketresearch.com, gminsights.com ITS page, mordorintelligence.com and imarcgroup.com APTS pages

**Sibling-file inputs used for derivations**
- File 05 (global bottom-up): ACEA 852,180 EU+EFTA+UK buses & coaches (2024); VDV 35,401 buses vs 85,559 registered (Germany); UTPF 17,864 / SDES 27,826 vs 94,542 (France); DfT 30,558 England local buses / GB ~34,600 vs 125,650; ING ~200,000 buses in European public transport; UITP ~20,350 European LRT vehicles and 5,390 trolleybuses; CUTA 16,145 Canadian transit buses; China MOT 630,100 public buses; MoRTH 147,032 SRTU buses.
- File 16 (NTD): 65,239 active full-size buses, 73,112 fixed-route bus-mode vehicles, 191,482 total revenue vehicles, 2,527 LRVs + 418 streetcars (FY2025); bus-mode Comm & Info capex USD 5,703 per active full-size bus (2025) — https://datahub.transportation.gov/d/ifzt-j53d ; https://datahub.transportation.gov/d/fphd-jyyj
- File 01: vendor totals for Fortune BI (USD 31.14bn, 2025) and the 1.10 USD/EUR illustrative rate.
