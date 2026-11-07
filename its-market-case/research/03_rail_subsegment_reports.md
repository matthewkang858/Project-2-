# 03 - Railway ITS sub-segment market sizing

**Topic:** Railway ITS sub-segment market sizing (signalling & train control, traffic management, "railway management system", asset management / predictive maintenance, trackside detection, passenger information, onboard CCTV, telematics / connectivity, digital twins), plus deployment statistics (ETCS, CBTC, PTC) and the resignalling cycle.

**Prepared:** 2026-11-07 (research sub-agent). **Scope reminder:** Public ITS = software, hardware and services sold to public transit operators / agencies. RAILWAY = metro, light rail / tram, commuter / regional and mainline passenger rail. Freight rail is adjacent and is flagged wherever a source bundles it (UNIFE, SCI Verkehr, PTC, wayside detection and most vendor "railway signalling" reports all include freight).

**Method / limitations (read first):**
- All figures below were captured from WebSearch result snippets. Direct WebFetch of primary pages (unife.org, railwaygazette.com, railwaypro.com, railmarket.com, uitp.org, federalregister.gov, railroads.dot.gov, marketsandmarkets.com, gminsights.com, fortunebusinessinsights.com, wrms.study, indexbox.io, railtarget.cz/.eu, masstransitmag.com) was blocked by the session network policy (ENOTFOUND) on two attempts, and the shared WebSearch budget for this run was exhausted after 28 queries. Pages were therefore NOT read in full; figures are as quoted in search snippets and should be verified against the page before being used as load-bearing numbers in the model. Items marked "VERIFY" are the highest priority for a second pass.
- Currency conversions (EUR to USD) in the "Key takeaways" section are my own arithmetic and are labelled as such; they are not from any source.

---

## 1. Key takeaways

1. **The rail "control, command and signalling" (CCS) market is roughly EUR 20-22bn a year globally and is the right anchor for the railway signalling / train-control block of the ITS model.** UNIFE's 10th World Rail Market Study (2024) puts "train control" at EUR 22.3bn (average annual volume, 2021-2023, 66 countries; secondary report of the study) and SCI Verkehr's CCS study (reported March 2026) puts the global CCS market at ~EUR 20bn, with Europe accounting for nearly half. These two independent sources agree within ~10%. At ~EUR 20-22bn, CCS is ~10-11% of the EUR 201.8bn total rail supply market (my arithmetic). Both figures INCLUDE freight rail and both include trackside + onboard + related services.
2. **The top-end cluster of vendor "railway signalling system" reports (USD 19.6-23.6bn for 2025: GMI, Fortune, MRFR, Next Move, Dataintelo, R&M) is consistent with UNIFE / SCI; the low cluster (USD 4-13bn: Wise Guy, Future Market Report, IMARC, Global Growth Insights, MRI, Reanin, 24marketreports) reflects narrower scopes (equipment-only or excluding services / onboard).** Converting EUR 20-22bn at ~USD 1.08-1.10 per EUR gives ~USD 22-24bn (my arithmetic), which lands on the top cluster. Recommend anchoring 2025 global CCS at ~USD 21-23bn and treating anything below USD 15bn as a sub-scope.
3. **Growth: total rail supply market grows ~3% p.a. real (UNIFE: 3.0% to EUR 240.8bn in 2027-29 per the 2024 edition; 3.2% to EUR 266.8bn in 2029-31 per the 2026 edition), but CCS grows faster: SCI Verkehr 4.6% p.a. (2023-2028, nominal, from a EUR 19.3bn base) and vendor signalling reports 5-9% p.a.** A defensible 2025-2031 CAGR for public-rail CCS is ~5-7% (mid-point of SCI and the better vendor reports), i.e. ~EUR 20bn (2025) to ~EUR 27-30bn (2031) if the SCI base is rolled forward (my arithmetic; low confidence until verified).
4. **Drivers are modernisation, not new lines, in the mature markets:** SCI Verkehr says the main European driver is modernisation of the existing network (ETCS, digital interlockings, FRMCS) whereas China is still driven by new infrastructure; one secondary snippet says ~90% of the European CCS market in 2025 is modernisation / maintenance vs ~10% new infrastructure (unverified, low confidence). Train control systems are ~40% of CCS volume (SCI). UNIFE's 2026 edition says Western Europe grew slowly as pandemic stimulus expired, Asia Pacific remains the largest region, Latin America is fastest-growing at 5.5%, and India is expected to offset a Chinese slowdown.
5. **Deployment pipeline is large and policy-mandated in Europe:** ERTMS is operational on only ~12,400 km of the TEN-T network (~10% of its length) at end-2024 with a further ~28,000 km planned by 2030; only ~19% of the EU fleet (~8,730 vehicles) has ETCS onboard, with ~18,000 vehicles (40% of fleet) expected by 2030. Only 20 of 200+ cross-border links have ERTMS on both sides. This is a multi-year, regulation-driven demand backlog for both trackside and onboard CCS.
6. **US: PTC is a finished mandate (57,536 route-miles at full implementation, Dec 2020; ~59,000 route-miles by the Oct 2024 FRA rulemaking), so the US mainline opportunity is now maintenance, software upgrades and interoperability, not greenfield.** PTC covers freight Class I, Amtrak and commuter railroads; the public-transit share is the commuter-rail slice. Federal funding >USD 716m to passenger railroads and ~USD 2.6bn in grants / loans is cited by FRA.
7. **Urban rail (metro / LRT) is roughly one-third to one-half of signalling spend, and grows faster than mainline.** GMI: mainline ~47% share (2024); Dataintelo: urban 34.2% share growing 10.1% vs mainline 8.8%; Wise Guy: urban larger than mainline. CBTC is the dominant urban technology (72% of automated-metro route-km per a secondary citation of UITP; ~40% of signalling by one vendor). CBTC market estimates cluster at USD 4-5bn (2025) growing to USD 7-8bn (2030), ~8-9% CAGR.
8. **The replacement cycle is real and front-loaded in the UK / Europe / North America:** signalling equipment life averages ~30 years (Rail Engineer); relay interlockings 40-45 years, computer-based interlockings only 20-25 years (Sydney Trains); Network Rail must renew 63% of its signalling assets over CP6-CP8 (15 years); MBTA / CTPS use 25-35 year lives. Electronic obsolescence (18-month component cycles inside 30-year systems) is now the trigger more often than wear-out. This supports a 25-30 year resignalling cycle assumption with a shorter 20-25 year cycle for electronic / software-based systems.
9. **Adjacent software layers are sized by vendors at: "railway management system" USD 55.5bn (2025) to 76.0bn (2030), 6.5% CAGR (MarketsandMarkets; rail traffic management is the largest solution segment, Europe the largest region at USD 19.3bn); rail asset management USD 12.8bn to 17.6bn, 6.6% (MarketsandMarkets); railway telematics USD 6.9bn to 10.0bn, 7.6% (Mordor); railway PIS ~USD 9.5bn (2023) to 19.9bn (2030), 11.75% (Verified Market Research); digital twin railway USD 1.7bn to 3.2bn, 13.3% (TBRC); TCMS USD 4.5bn to 6.5bn, 7.5% (Mordor).** These overlap heavily with each other and with CCS (e.g. "railway management system" includes traffic management AND asset management AND PIS AND security), so they must NOT be summed. Use them only as relative-size and growth-rate indicators for the segmentation framework.
10. **Gaps that still need a second pass:** UNIFE segment-level CCS figure and regional EUR volumes for the 2026 (11th) edition; SCI Verkehr primary document (and the 90% modernisation claim); UITP's 2025 automated-metro km actual; ERA EU-wide ETCS km (not just TEN-T); PTC locomotive count and total programme cost; trackside detection (hot box / WILD / obstacle detection) sizing (not found); standalone onboard rail CCTV sizing (not found); vendor revenue triangulation (Siemens Mobility, Alstom, Hitachi Rail, Wabtec); resignalling cost benchmarks (NYCT CBTC USD per mile, Network Rail CP7). Mordor, Technavio and Precedence signalling reports were not surfaced.

---

## 2. Findings table

Confidence key: **high** = primary source or consistent across 2+ independent sources; **medium** = single secondary source; **low** = inferred, unclear scope, or outlier.

### 2a. UNIFE World Rail Market Study (WRMS) - total market and segments

| Claim | Value | Unit | Year / period | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Total rail supply market, 10th WRMS (2024 ed.) | 201.8 | EUR bn, avg annual | 2021-2023 | World (66 countries, 99% of rail traffic) | All (infra, rail control, rolling stock, services, turnkey) | Railway Gazette / UNIFE | https://www.railwaygazette.com/innotrans/2024/09/24/global-trends-driving-rail-market-growth-unife-study-confirms/ | high | Railway Gazette: "during this period the total market volume averaged EUR 201.8bn". Includes freight. Some outlets describe it as a point-in-time figure; the average-annual reading is the precise one. |
| Prior edition (9th, 2022) total | 176.5 | EUR bn, avg annual | 2019-2021 | World | All | RailTarget (10th WRMS article) | https://www.railtarget.eu/business/10th-world-rail-market-study-reports-27-annual-growth-and-positive-outlook-for-the-decade-9296.html | medium | |
| Historic growth 2019-21 to 2021-23 | 2.7 | % p.a. | 2019-21 to 2021-23 | World | All | UNIFE press release | https://www.unife.org/news/policymakers-and-industry-give-vote-of-confidence-as-global-rail-supply-market-continues-to-expand-despite-geopolitical-tensions/ | high | Also in RailTarget and Railway Gazette. |
| Forecast total market 2027-2029 (10th ed.) | 240.8 | EUR bn, avg annual | 2027-2029 | World | All | UNIFE / Railway Gazette | https://www.unife.org/news/policymakers-and-industry-give-vote-of-confidence-as-global-rail-supply-market-continues-to-expand-despite-geopolitical-tensions/ | high | "around 3% p.a. in real terms"; UNIFE quote: industry set to grow by over EUR 40bn annually by 2029. |
| Services segment (10th ed.) | 77.1 | EUR bn | 2021-2023 (implied) | World | Services | Railway Supply | https://www.railway.supply/global-railway-market-report-2024-unifes-key-insights/ | medium | Single secondary source; segment figures sum to ~201.9 so period = 2021-23 average. VERIFY against UNIFE abstract. |
| Rolling stock segment (10th ed.) | 63.3 | EUR bn | 2021-2023 (implied) | World | Rolling stock | Railway Supply | https://www.railway.supply/global-railway-market-report-2024-unifes-key-insights/ | medium | |
| Infrastructure segment (10th ed.) | 38.1 | EUR bn | 2021-2023 (implied) | World | Infrastructure | Railway Supply | https://www.railway.supply/global-railway-market-report-2024-unifes-key-insights/ | medium | |
| **Rail control / train control segment (10th ed.)** | **22.3** | EUR bn | 2021-2023 (implied) | World | Rail control (CCS) | Railway Supply | https://www.railway.supply/global-railway-market-report-2024-unifes-key-insights/ | medium | Single secondary source for this number; consistent with SCI Verkehr EUR 19.3-20bn. Includes freight, trackside + onboard. ~11% of total (my arithmetic). VERIFY. |
| Turnkey project management segment (10th ed.) | 1.1 | EUR bn | 2021-2023 (implied) | World | Turnkey | Railway Supply | https://www.railway.supply/global-railway-market-report-2024-unifes-key-insights/ | medium | |
| Regional forecast growth: Western Europe | 3.7 | % p.a. | to 2027-29 | Western Europe | All | UNIFE / Railway Gazette | https://www.railwaygazette.com/innotrans/2024/09/24/global-trends-driving-rail-market-growth-unife-study-confirms/ | high | |
| Regional forecast growth: Eastern Europe | 3.6 | % p.a. | to 2027-29 | Eastern Europe | All | UNIFE / Railway Gazette | https://www.railwaygazette.com/innotrans/2024/09/24/global-trends-driving-rail-market-growth-unife-study-confirms/ | high | |
| Regional forecast growth: CIS | 0.7 | % p.a. | to 2027-29 | CIS | All | UNIFE / Railway Gazette | https://www.railwaygazette.com/innotrans/2024/09/24/global-trends-driving-rail-market-growth-unife-study-confirms/ | high | |
| Accessible market for EU suppliers (10th ed.) | 59 | % of world market | 2024 ed. | World | All | UNIFE | https://www.unife.org/news/global-rail-booms-as-closed-markets-now-cost-eu-industry-e97-billion-per-year/ | high | 61% in 2022 ed., 70% in 2008 ed. |
| **Total rail supply market, 11th WRMS (2026 ed., with Bain & Company)** | **221** | EUR bn, avg annual | 2023-2025 | World (66 countries) | All | UNIFE press release / Railway Gazette / RailTarget | https://www.unife.org/news/global-rail-booms-as-closed-markets-now-cost-eu-industry-e97-billion-per-year/ | high | Launched at InnoTrans 22 Sep 2026; digital modular format; segments: infrastructure, CCS, rolling stock, services, turnkey. Search summary attributes preparation to Bain & Company. |
| Historic growth 2021-23 to 2023-25 (11th ed.) | 4.6 | % p.a. | 2021-23 to 2023-25 | World | All | UNIFE | https://www.unife.org/news/global-rail-booms-as-closed-markets-now-cost-eu-industry-e97-billion-per-year/ | high | Reflects post-Covid recovery. |
| **Forecast total market 2029-2031 (11th ed.)** | **266.8** | EUR bn, avg annual | 2029-2031 | World | All | UNIFE / Railway Gazette / IndexBox | https://www.railwaygazette.com/business/2026/10/09/world-rail-market-study-predicts-continuing-growth-following-covid-rebound/ | high | 3.2% p.a. real growth. Also: https://www.indexbox.io/blog/world-rail-market-study-global-rail-market-to-grow-32-annually-to-2668bn-by-2029-31/ |
| Accessible market for EU suppliers (11th ed.) | 56 | % | 2026 ed. | World | All | UNIFE | https://www.unife.org/news/global-rail-booms-as-closed-markets-now-cost-eu-industry-e97-billion-per-year/ | high | Closed markets cost EU industry EUR 97bn/yr. |
| Largest region (11th ed.) | Asia Pacific | - | 2023-2025 | APAC | All | RailTarget | https://www.railtarget.cz/business/global-rail-market-266-billion-eu-access-unife-12712.html | medium | No EUR volume captured. |
| Fastest-growing region (11th ed.) | 5.5 | % p.a. | to 2029-31 | Latin America | All | RailTarget | https://www.railtarget.cz/business/global-rail-market-266-billion-eu-access-unife-12712.html | medium | |
| Western Europe grew slowly; India offsets China slowdown | qualitative | - | 2023-25 | W. Europe / India / China | All | Railway Gazette | https://www.railwaygazette.com/business/2026/10/09/world-rail-market-study-predicts-continuing-growth-following-covid-rebound/ | medium | |
| 11th ed. CCS segment size | NOT FOUND | - | - | - | CCS | wrms.study | https://www.wrms.study/study | - | Paywalled (DVV Media). GAP. |

### 2b. SCI Verkehr - control command and signalling (CCS)

| Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Global CCS market | ~20 | EUR bn | 2025 (reported Mar 2026) | World | CCS (trackside + onboard, incl. freight) | Railway PRO (reporting SCI Verkehr) | https://www.railwaypro.com/wp/europe-the-largest-market-for-digital-train-control-and-signalling/ | medium | Independent of UNIFE; consistent with EUR 22.3bn. |
| Europe share of global CCS | nearly half (~50) | % | 2025 | Europe | CCS | Railway PRO / RailMarket | https://railmarket.com/news/business/53444-europe-leads-global-rail-signalling-market | medium | Europe overtook China as largest CCS market. |
| Train control systems share of CCS | ~40 | % of CCS volume | 2025 | World | Train control (ETCS/CBTC/ATP) | Railway PRO | https://www.railwaypro.com/wp/europe-the-largest-market-for-digital-train-control-and-signalling/ | medium | Largest product segment. |
| European CCS market share driven by modernisation / maintenance of existing network | ~90 (vs ~10 new infrastructure) | % | 2025 | Europe | CCS | search snippet citing SCI Verkehr coverage | https://www.railwaypro.com/wp/europe-the-largest-market-for-digital-train-control-and-signalling/ | low | Appeared in one search summary; a second search could not confirm the 90% figure. VERIFY. Directionally consistent with SCI's "modernisation more important than expansion in Europe". |
| Drivers to 2030 | ETCS, digital signalling, FRMCS | qualitative | to 2030 | Europe | CCS | Railway PRO | https://www.railwaypro.com/wp/europe-the-largest-market-for-digital-train-control-and-signalling/ | medium | China still driven by new lines. |
| Earlier SCI CCS study: global market | 19.3 | EUR bn | 2023 | World | CCS | RailMarket (reporting SCI Verkehr) | https://railmarket.com/news/technology-innovation/16494-unveiling-the-future-sci-verkehr-s-insights-into-rail-control-and-signaling-market-trends | medium | |
| Earlier SCI CCS study: growth | 4.6 | % p.a. | 2023-2028 | World | CCS | RailMarket | https://railmarket.com/news/technology-innovation/16494-unveiling-the-future-sci-verkehr-s-insights-into-rail-control-and-signaling-market-trends | medium | Nominal (assumed). |
| SCI Verkehr CCS study product page | - | - | - | - | CCS | SCI Verkehr shop | https://www.sci.de/shop/products?productid=41&L=1 | - | Paid study; 2019 flyer at https://sci.de/fileadmin/user_upload/MC_Studien_Flyer/Flyer_MC_CCS_2019_de.pdf |

### 2c. Vendor reports - railway signalling / train control (global)

| Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Railway signaling system market | 18.2 (2024); 19.6 (2025); 42.4 (2034) | USD bn | 2024 / 2025 / 2034 | World | Signalling (solutions + services) | Global Market Insights | https://www.gminsights.com/pressrelease/railway-signaling-system-market | medium | CAGR 8.9% 2025-34. ETCS ~31% share 2024 growing >8.5%; mainline ~47% share 2024; US = 85% of North America at USD 4.2bn 2024. Offering split = solutions vs services (no HW/SW split). |
| Railway signalling system market | 23.64 | USD bn | 2025 | World | Signalling | Fortune Business Insights | https://www.fortunebusinessinsights.com/railway-signalling-system-market-103658 | medium | Forecast year/value not captured. |
| Global Railway Signaling Market Intelligence Report 2026-2031 | 19.85 (2025); 28.24 (2031) | USD bn | 2025 / 2031 | World | Signalling incl. train control (ATP, ATO, CBTC, ETCS) | Yahoo Finance (Research and Markets) | https://finance.yahoo.com/technology/articles/global-railway-signaling-market-intelligence-160400701.html | medium | CAGR 6.05%. Train control = largest and fastest-growing segment. Only report with an explicit 2031 endpoint. |
| Railway signaling system market | 12.8 (2021); 21.7 (2031) | USD bn | 2021 / 2031 | World | Signalling | Allied Market Research (EIN press release, Jul 2025) | https://www.einnews.com/pr_news/832587422/railway-signaling-system-market-to-reach-21-7-billion-by-2031-at-a-5-5-cagr-size-share-trends-demands-and-growth | medium | CAGR 5.5% 2022-31. Old base year. |
| Railway signaling system market | 21,378.6 (2025); 34,964.3 (2035) | USD m | 2025 / 2035 | World | Signalling | Market Research Future | https://www.marketresearchfuture.com/reports/railway-signaling-system-market-13919 | medium | CAGR 5.0%. ~USD 19.8bn 2024. |
| Railway signaling system market | 11.6 (2025); 19.4 (2034) | USD bn | 2025 / 2034 | World | Signalling | IMARC | https://www.imarcgroup.com/railway-signaling-system-market | medium | CAGR 5.69%; mainline largest application. Narrower scope than GMI. |
| Railway signaling market | 12.91 (2025); 13.75 (2026) | USD bn | 2025 / 2026 | World | Signalling (CBTC, PTC, ATC) | Global Growth Insights | https://www.globalgrowthinsights.com/market-reports/railway-signaling-market-117220 | low | CAGR 6.5% to 2035. |
| Railway signaling system market | 10,987 (2025) | USD m | 2025 | World | Signalling | Global Growth Insights (2nd report) | https://www.globalgrowthinsights.com/market-reports/railway-signaling-system-market-110216 | low | CAGR 7.92% to 2033; CBTC ~40% of market. |
| Railway signaling system market | 13.42 (2025) | USD bn | 2025 | World | Signalling | Market Research Intellect | https://www.marketresearchintellect.com/product/railway-signaling-system-market/ | low | CAGR 4.7% to 2035. |
| Railway signalling market | 17.19 (2025) | USD bn | 2025 | World | Signalling | Research and Markets | https://www.researchandmarkets.com/report/railway-signalling | medium | Forecast to 2032. |
| Railway signaling system market | 21.22 (2025); 32.49 (2030) | USD bn | 2025 / 2030 | World | Signalling | Next Move Strategy Consulting | https://www.nextmsc.com/report/railway-signaling-system-market-at3550 | low | CAGR 8.9% 2025-30. |
| Railway signaling system market | ~24.2 (2030) | USD bn | 2030 | World | Signalling | Lucintel | https://www.lucintel.com/railway-signaling-system-market.aspx | low | CAGR 6.7% 2024-30. |
| Railway signaling system market | 22.5 (2025) | USD bn | 2025 | World | Signalling | Value Market Research | https://www.valuemarketresearch.com/report/railway-signaling-system-market | low | |
| Railway signalling system market | 15.3 (2024) | USD bn | 2024 | World | Signalling (HW/SW/services split) | SkyQuest | https://www.skyquestt.com/report/railway-signalling-system-market | low | Only vendor found with HW/SW/services segmentation; shares not captured. |
| Railway signaling system market | 12.2 (2024) | USD bn | 2024 | World | Signalling | Towards Automotive | https://www.towardsautomotive.com/insights/railway-signaling-system-market-sizing | low | CAGR 13.91% to 2034 (outlier). |
| Railway signaling system market | 13,542.2 (2024) | USD m | 2024 | World | Signalling | Cognitive Market Research | https://www.cognitivemarketresearch.com/railway-signaling-system-market-report | low | |
| Railway signaling market | 21.6 (2025) | USD bn | 2025 | World | Signalling | Dataintelo | https://dataintelo.com/report/railway-signaling-market | low | Urban rail 34.2% share, 10.1% CAGR; mainline 8.8% CAGR. |
| Rail signaling and train control systems market | ~21.6 (2025) | USD bn | 2025 | World | Signalling | Verified Market Reports | https://www.verifiedmarketreports.com/product/rail-signaling-and-train-control-systems-market/ | low | |
| Rail signalling systems market | 4.1 (2025); 8.6 (2033) | USD bn | 2025 / 2033 | World | Signalling (narrow) | Future Market Report | https://www.futuremarketreport.com/industry-report/rail-signalling-systems-market | low | CAGR ~9.6%. Narrow scope. |
| Rail signalling systems market | 7.38 (2025); 7.07 (2024) | USD bn | 2025 | World | Signalling (narrow) | Wise Guy Reports | https://www.wiseguyreports.com/reports/rail-signalling-systems-market | low | CAGR ~4.4%. |
| Railway signalling & train control systems market | 9,954 (2025); 18,090 (2032) | USD m | 2025 / 2032 | World | Signalling | 24marketreports | https://www.24marketreports.com/automotive-and-transportation/global-railway-signalling-train-control-systems-market | low | |
| Train signalling system market | 10.2 (2025) | USD bn | 2025 | World | Signalling | Reanin | https://www.reanin.com/reports/train-signalling-system-market | low | |
| Train signalling system market | 2.13 (2024); 3.09 (2031) | USD bn | 2024 / 2031 | World | Signalling (very narrow) | Verified Market Research | https://www.verifiedmarketresearch.com/product/train-signalling-system-market/ | low | CAGR 5.22%. Likely equipment-only. |
| Railway signalling interlocking systems market | 3.4 (2025); 5.0 (2035) | USD bn | 2025 / 2035 | World | Interlocking | Wise Guy Reports | https://www.wiseguyreports.com/reports/railway-signalling-interlocking-systems-market | low | CAGR 3.9%. Only interlocking-specific figure found. |
| Train control and management system (TCMS, onboard) | 4.5 (2025); 6.46 (2030) | USD bn | 2025 / 2030 | World | Onboard TCMS | Mordor Intelligence | https://www.mordorintelligence.com/industry-reports/train-control-and-management-system-market | medium | CAGR 7.51%. Rolling-stock electronics; partly overlaps onboard CCS. |
| ETCS onboard equipment market | 3.8 (2025); 7.2 (2034) | USD bn | 2025 / 2034 | World | ETCS onboard | Dataintelo | https://dataintelo.com/report/etcs-onboard-equipment-market | low | |

### 2d. Urban (metro / LRT) vs mainline split, and CBTC

| Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Mainline share of railway signalling market | ~47 | % | 2024 | World | Mainline signalling | Global Market Insights | https://www.gminsights.com/industry-analysis/railway-signaling-system-market | medium | Implies urban + other ~53%. Mainline includes freight. |
| Mainline = largest application | qualitative | - | 2024/25 | World | Mainline | IMARC | https://www.imarcgroup.com/railway-signaling-system-market | low | |
| Urban rail share of railway signalling | 34.2 | % | 2025 | World | Urban signalling | Dataintelo | https://dataintelo.com/report/railway-signaling-market | low | Urban CAGR 10.1% vs mainline 8.8%. |
| Urban rail larger than mainline (equipment) | qualitative | - | 2023 | World | Urban vs mainline equipment | Wise Guy Reports | https://www.wiseguyreports.com/reports/urban-and-main-line-rail-signalling-equipment-market | low | Contradicts GMI/IMARC. |
| Urban + mainline rail signalling equipment market | 11.5 | USD bn | 2024 | World | Equipment | Exactitude Consultancy | https://exactitudeconsultancy.com/reports/62555/global-urban-and-main-line-rail-signalling-equipment-market | low | Equipment-only scope. |
| Urban + mainline rail signalling equipment market; urban-only | 39.03 total; 13.0 urban | USD bn | 2025 | World | Equipment | Archive Market Research | https://www.archivemarketresearch.com/reports/urban-and-main-line-rail-signalling-equipment-106553 | low | Total looks too high vs UNIFE; urban ~33% of total. |
| Urban rail signalling systems market | 15.0 | USD bn | 2025 | World | Urban signalling | Dataintelo | https://dataintelo.com/report/global-urban-rail-signalling-systems-market | low | |
| CBTC market | 5.03 (2025); 7.88 (2030) | USD bn | 2025 / 2030 | World | CBTC | The Business Research Company | https://www.thebusinessresearchcompany.com/report/communication-based-train-control-system-global-market-report | medium | CAGR 9.4%; North America largest region (per TBRC). |
| CBTC market | 5.0 (2025); 7.36 (2030) | USD bn | 2025 / 2030 | World | CBTC | Market Research Forecast | https://www.marketresearchforecast.com/reports/communication-based-train-control-cbtc-system-29120 | low | CAGR 8%. |
| CBTC market | 4.5 (2025) | USD bn | 2025 | World | CBTC | Verified Market Reports | https://www.verifiedmarketreports.com/product/communication-based-train-control-cbtc-system-market/ | low | |
| CBTC market | 3.8 (2025); ~9.7 (2034) | USD bn | 2025 / 2034 | World | CBTC | Dataintelo | https://dataintelo.com/report/global-communications-based-train-control-cbtc-market | low | |
| CBTC market | 2,465.1 (2025) | USD m | 2025 | World | CBTC | Global Growth Insights | https://www.globalgrowthinsights.com/market-reports/communications-based-train-control-cbtc-market-109768 | low | |
| CBTC market | 1.54 (2025) | USD bn | 2025 | World | CBTC | Report Prime | https://www.reportprime.com/communications-based-train-control-cbtc-r77 | low | Narrow. |
| CBTC market | 1.38 (2025) | USD bn | 2025 | World | CBTC | Market Research Intellect | https://www.marketresearchintellect.com/product/communications-based-train-control-cbtc-market/ | low | Narrow. |
| Europe CBTC market | 750.3 | USD m | 2025 | Europe | CBTC | Global Market Insights | https://www.gminsights.com/industry-analysis/europe-communication-based-train-control-market | medium | Forecast to 2035. |
| CBTC share of railway signalling | ~40 | % | 2025 | World | CBTC | Global Growth Insights | https://www.globalgrowthinsights.com/market-reports/railway-signaling-system-market-110216 | low | |

### 2e. Deployment statistics - CBTC / automated metro, ETCS / ERTMS, PTC

| Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CBTC share of automated-metro route-km | 72 | % | ~2024/25 | World | CBTC / GoA4 metro | Railway News wiki citing UITP | https://railwaynews.net/wiki/what-is-cbtc-communications-based-train-control-explained | low | Secondary citation of UITP; not confirmed in UITP brief itself. |
| UITP Statistics Brief: metro automation (Apr 2025 PDF) | - | - | 2025 | World | GoA4 metro | UITP | https://www.uitp.org/wp-content/uploads/sites/7/2025/04/Statistics-Brief-Metro-automation_final_web03.pdf | - | Fetch blocked. GAP: 2025 actual km. |
| Automated metro lines forecast | 789 -> 2,200 | km | "today" -> 2025 | World | GoA4 metro | IRJ (citing UITP) | https://www.railjournal.com/passenger/metros/uitp-forecasts-2200km-of-automated-metros-by-2025/ | medium | Older UITP forecast; later UITP estimate >2,300 km for 2025 (unconfirmed). |
| Fully automated metro milestone | 1,000 km; 63 FAO lines; 42 cities; 19 countries | km / count | ~2018-19 | World | GoA4 metro | Railway International (citing UITP) | https://railway-international.com/news/around-the-world-1000-km-of-fully-automated-metros | medium | Dated. |
| Thales CBTC on automated metro lines | ~250 | km | ~2023 | World | CBTC | Railway Technology | https://www.railway-technology.com/features/around-world-driverless-metro-lines/ | low | Market leader for FAO lines, followed by Siemens (Thales GTS now part of Hitachi Rail). |
| Metro lines with CBTC worldwide | >160 lines; >35,000 km | count / km | 2025 | World | CBTC | Market Growth Reports | https://www.marketgrowthreports.com/market-reports/communications-based-train-control-cbtc-market-107995 | low | Km figure implausibly high vs other sources; do not use. |
| Metro systems deploying CBTC | >100 systems; >3,000 route-km | count / km | 2025 | World | CBTC | Strategic Market Research | https://www.strategicmarketresearch.com/market-report/communication-based-train-control-market | low | Order-of-magnitude different from above; do not combine. |
| China urban CBTC | ~7,200 route-km; 150-170 lines | km / count | 2025 | China | CBTC | cbtcbook.com (practitioner blog) | https://cbtcbook.com/blog/chinese-metro-cbtc-50-cities/ | low | Blog title: "50 cities, 11,000+ route-km in 25 years". |
| ERTMS operational on TEN-T network | ~12,400 (~10% of TEN-T length) | km | end-2024 | EU / TEN-T | ETCS trackside | Railway PRO | https://www.railwaypro.com/wp/etcs-on-european-corridors-three-corridors-are-lagging/ | medium | Further ~28,000 km planned on TEN-T to 2030. Only 9 km commissioned 2022-24 on one lagging corridor. |
| EU fleet with ETCS onboard | ~19% (~8,730 vehicles) | % / vehicles | late-2024 | EU | ETCS onboard | UNIFE | https://www.unife.org/news/unlocking-the-future-of-ertms-in-europe/ | medium | Also https://www.railwaypro.com/wp/only-19-of-vehicles-are-equipped-with-onboard-etcs-in-the-eu/ |
| EU fleet with ETCS onboard, 2030 estimate | 18,000 vehicles (~40% of fleet) | vehicles / % | 2030 | EU | ETCS onboard | Railway PRO | https://www.railwaypro.com/wp/only-19-of-vehicles-are-equipped-with-onboard-etcs-in-the-eu/ | medium | |
| Cross-border links with ERTMS both sides | 20 of 200+ | count | ~2024/25 | EU | ETCS | EC ERTMS coordinator (via IRJ / Railway PRO) | https://www.railjournal.com/analysis/struggling-to-join-the-dots-on-the-etcs-route-map/ | medium | |
| ETCS 2030 target on Core Network Corridors | 40,875 (69% of revised CNC) | km | 2030 | EU | ETCS trackside | EC ERTMS 2nd Work Plan (2023) | https://transport.ec.europa.eu/system/files/2023-09/ERTMS_work_plan-second_edition.pdf | high (primary, but 2023 vintage) | EC state-of-play pages: https://transport.ec.europa.eu/transport-modes/rail/ertms/state-play_en |
| PTC full implementation | 57,536 route-miles (~41% of ~140,000 US route-miles) | route-miles | Dec 2020 | USA | PTC | FRA press release | https://railroads.dot.gov/newsroom/press-releases/federal-railroad-administration-announces-landmark-achievement-full | high | Covers Class I freight, Amtrak, commuter railroads. Also https://www.ttnews.com/articles/railroads-achieve-full-positive-train-control-implementation-fra-says |
| PTC governing operations | nearly 59,000 route-miles | route-miles | Oct 2024 | USA | PTC | Federal Register NPRM | https://www.federalregister.gov/documents/2024/10/28/2024-24559/positive-train-control-systems | high | |
| BNSF PTC | ~17,000 miles installed vs ~15,000 mandated; MRL lines completed 9 Dec 2025 | miles | 2025 | USA (BNSF) | PTC (freight) | BNSF | https://bnsf.com/news-media/railtalk/safety/ptc-2025.html | high | FREIGHT - out of public-transit scope; shows continued post-mandate expansion. |
| Federal PTC funding to passenger railroads | >716 | USD m | cumulative to 2021 | USA | PTC (passenger) | FRA PTC flyer 2021 | https://railroads.dot.gov/sites/fra.dot.gov/files/2021-11/PTC%20Flyer_2021.pdf | high | Plus ~USD 2.6bn grants and loans overall (FRA). Total programme cost and locomotive count NOT captured - GAP. |
| PTC market | 1.65 (2025); ~3.1 (2033) | USD bn | 2025 / 2033 | World (US-centric) | PTC | Straits Research | https://straitsresearch.com/report/positive-train-control-market | low | CAGR 8.31%. |
| PTC market | ~2.5 (2030) | USD bn | 2030 | World | PTC | IndustryARC | https://www.industryarc.com/Research/positive-train-control-systems-market-research-800508 | low | CAGR 7.4% 2024-30. |
| PTC market | 9.15 (2025) | USD bn | 2025 | World | PTC | Data Insights Market | https://www.datainsightsmarket.com/reports/positive-train-control-827410 | low | Internally inconsistent; discard. |

### 2f. Asset life / resignalling cycle

| Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Average signalling equipment life | ~30 | years | - | UK | Signalling | Rail Engineer | https://www.railengineer.co.uk/a-signalling-exposition/ | medium | Renewal usually forced by obsolescence. |
| Relay interlocking design life | 40-45 | years | 2023 | Australia (Sydney Trains) | Interlocking | Asset Management Council | https://amcouncil.win/2023/08/29/sydney-trains-management-of-assessing-condition-of-railway-signalling-systems-development-of-a-roadmap-for-life-extension-and-renewals/ | medium | |
| Computer-based interlocking life | 20-25 | years | 2023 | Australia (Sydney Trains) | CBI | Asset Management Council | https://amcouncil.win/2023/08/29/sydney-trains-management-of-assessing-condition-of-railway-signalling-systems-development-of-a-roadmap-for-life-extension-and-renewals/ | medium | Most expected to reach life expiry within a decade. |
| Interlocking scheme life assumption (Network Rail analysis) | 35 | years | 2023 | UK | Interlocking | ORR independent report on NR conventional signalling & obsolescence | https://www.orr.gov.uk/sites/default/files/2023-12/nr-conventional-signalling-and-obsolescence-management-report.pdf | high (primary) | Report recommends building obsolescence risk into remaining-life data. |
| Network Rail signalling renewal need | 63% of signalling assets over CP6-CP8 (15 years) | % | 2019-2034 | UK | Signalling | Modern Railways | https://www.modernrailways.com/article/signalling-still-crisis | medium | Renewals deferred in late 1990s pushed burden into later control periods. |
| Transit signal unit useful life | 25 | years | - | USA (Boston MPO / MBTA) | Transit signals | CTPS PMT ch.5 | https://www.ctps.org/data/pdf/studies/transit/pmt/PMT_Ch5.pdf | high (primary) | MBTA uses 35-yr general life cycle for rapid transit / LRT. |
| Component vs system life mismatch | ~18 months vs 30+ years | - | 2024 | - | Signalling electronics | arXiv 2402.08343 | https://arxiv.org/pdf/2402.08343 | medium | Electronic parts enter EOL after 5-10 years (vendor blog: https://www.aivon.com/blog/pcb-knowledge/designing-for-obsolescence-strategies-for-long-life-railway-signaling-pcbs/). |

### 2g. Railway management system, traffic management, asset management, predictive maintenance

| Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Railway management system market | 55.49 (2025); 76.00 (2030) | USD bn | 2025 / 2030 | World | RMS (ops mgmt, traffic mgmt, asset mgmt, in-train, PIS, network mgmt, security & surveillance) | MarketsandMarkets (press release 1 Dec 2025) | https://www.marketsandmarkets.com/PressReleases/railway-management-system.asp | medium | CAGR 6.5%. Solutions > services; rail traffic management = largest solution; Europe = largest region. Also https://www.prnewswire.com/news-releases/railway-management-system-market-76-00-billion-by-2030--marketsandmarkets-302628881.html |
| Europe railway management system | 19,260.8 (2025); 24,777.8 (2030) | USD m | 2025 / 2030 | Europe | RMS | MarketsandMarkets | https://www.marketsandmarkets.com/Market-Reports/geography/railway-management-system-market/europe | medium | CAGR 5.2%. |
| UK railway management system | 3.69 (2025); 4.94 (2030) | USD bn | 2025 / 2030 | UK | RMS | MarketsandMarkets | https://www.marketsandmarkets.com/Market-Reports/geography/railway-management-system-market/UK | medium | CAGR 6.0%. |
| UAE railway management system | 1.10 (2025); 1.44 (2030) | USD bn | 2025 / 2030 | UAE | RMS | MarketsandMarkets | https://www.marketsandmarkets.com/Market-Reports/geography/railway-management-system-market/UAE | medium | CAGR 5.5%. |
| Railway management system market (alt.) | 54.4 (2026); 76.41 (2030) | USD bn | 2026 / 2030 | World | RMS | Research and Markets | https://www.researchandmarkets.com/reports/5766882/railway-management-system-market-report | low | CAGR 8.9%; do not combine with M&M. |
| Railway management system market | 59.79 (2025); 95.14 (2030) | USD bn | 2025 / 2030 | World | RMS | Mordor Intelligence (via Barchart) | https://www.barchart.com/story/news/33630457/railway-management-system-market-to-reach-usd-9514-billion-by-2030-driven-by-demand-for-digital-rail-operations-and-passenger-experience-mordor-intelligence | low | CAGR 9.73%; APAC fastest at 10.1%. |
| Railway management system market | 48.06 (2025) | USD bn | 2025 | World | RMS | Research Nester | https://www.researchnester.com/reports/railway-management-system-market/6104 | low | >8.5% CAGR to 2035. |
| Rail asset management market | 12.79 (2025); 17.59 (2030) | USD bn | 2025 / 2030 | World | Asset mgmt (condition monitoring, predictive maintenance, security, planning & scheduling + services; rolling stock + infrastructure) | MarketsandMarkets (Jul 2025) | https://www.marketsandmarkets.com/Market-Reports/rail-asset-management-market-222416351.html | medium | CAGR 6.6%. Key players Siemens, Alstom, Hitachi, Wabtec, IBM. Also https://aijourn.com/rail-asset-management-market-worth-17-59-billion-by-2030-marketsandmarkets/ |
| North America rail asset management | 3,453.9 (2025); 4,714.8 (2030) | USD m | 2025 / 2030 | North America | Asset mgmt | MarketsandMarkets | https://www.marketsandmarkets.com/Market-Reports/geography/rail-asset-management-market/North-America | medium | CAGR 6.4%. APAC share 38.1% in 2025. |
| Rail asset management market | 11.6 (2025); 12.5 (2026); 16.68 (2030) | USD bn | 2025-2030 | World | Asset mgmt | The Business Research Company | https://www.thebusinessresearchcompany.com/report/rail-asset-management-global-market-report | low | CAGR 7.5% 2026-30. |
| Railway predictive maintenance market | 12.4 (2025); 28.9 (2034) | USD bn | 2025 / 2034 | World | Predictive maintenance | Dataintelo | https://dataintelo.com/report/railway-predictive-maintenance-market | low | CAGR 9.8%. |
| Railway predictive maintenance market | 4.1 (2024); 17.4 (2033) | USD bn | 2024 / 2033 | World | Predictive maintenance | Growth Market Reports | https://growthmarketreports.com/report/railway-predictive-maintenance-market | low | CAGR 16.7%. |
| Predictive maintenance rail market | 1.26 (2024); 5.18 (2033) | USD bn | 2024 / 2033 | World | Predictive maintenance (narrow) | Growth Market Reports | https://growthmarketreports.com/report/predictive-maintenance-rail-market | low | CAGR 19.8%. |
| Rail predictive maintenance AI market | 8.2 (2025); 35.7 (2034) | USD bn | 2025 / 2034 | World | PdM AI | Marketintelo | https://marketintelo.com/report/rail-predictive-maintenance-ai-market | low | CAGR 17.3%. |
| Rail maintenance management system market | 14.72 (2025); 23.5 (2030) | USD bn | 2025 / 2030 | World | Maintenance mgmt software | Research and Markets | https://www.researchandmarkets.com/reports/5980339/rail-maintenance-management-system-market-report | low | CAGR 9.5%. |
| Railway infrastructure maintenance services | ~112 (2025); ~128 (2030) | USD bn | 2025 / 2030 | World | Maintenance services (not ITS) | Research and Markets | https://www.researchandmarkets.com/reports/5980337/railway-infrastructure-maintenance-services | low | CAGR 2.7%. Context only; mostly civil / track. |

### 2h. Passenger information, security / CCTV, telematics / connectivity, digital twin, ATO, trackside detection

| Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Railway passenger information system market | 9.45 (2023); 19.93 (2030) | USD bn | 2023 / 2030 | World | Rail PIS | Verified Market Research | https://www.verifiedmarketresearch.com/product/railway-passenger-information-system-market/ | low | CAGR 11.75% 2024-30. |
| Railway PIS growth | 11.7 | % CAGR | 2025-2031 | World | Rail PIS (onboard + in-station) | Lucintel | https://www.lucintel.com/railway-passenger-information-system-market.aspx | low | |
| Railway PIS market | 1.33 (2025); 3.02 (2035) | USD bn | 2025 / 2035 | World | Rail PIS (narrow) | Market Research Intellect | https://www.marketresearchintellect.com/product/railway-passenger-information-system-market/ | low | CAGR 8.5%. |
| Automated passenger counting + information system market | 14.80 (2030) | USD bn | 2030 | World (all modes) | APC + PIS | MarketsandMarkets | https://www.marketsandmarkets.com/Market-Reports/automatic-passenger-counting-information-system-market-17856390.html | medium | CAGR 8.8% 2025-30. Blends bus + rail; APC + PIS. |
| Passenger information system market (all modes) | 29.85 (2023); 74.06 (2030) | USD bn | 2023 / 2030 | World (all modes) | PIS | Grand View Research | https://www.grandviewresearch.com/press-release/global-passenger-information-system-market | medium | CAGR 14.1% 2024-30; segments on-board / in-station. |
| PIS market growth (all modes) | 11.2 / 11.9 | % CAGR | 2024-30 / 2023-30 | World | PIS | Maximize Market Research / Market Research Future | https://www.maximizemarketresearch.com/market-report/global-passenger-information-system-market/22104/ ; https://www.marketresearchfuture.com/reports/passenger-information-system-market-2112 | low | |
| Railway safety and security market | 31.60 (2025) | USD bn | 2025 | World | Rail security (incl. video surveillance) | Emergen Research | https://www.emergenresearch.com/industry-report/railway-safety-and-security-market | low | Onboard deployment 8.9% CAGR to 2035; video surveillance 10.2% CAGR to 2035. No standalone onboard CCTV figure found. |
| Railway platform security market | 2.48 (2025); 3.6 (2030) | USD bn | 2025 / 2030 | World | Platform security | The Business Research Company (via openPR) | https://www.openpr.com/news/4635822/railway-platform-security-market-research-reveals-strong-7-9 | low | CAGR 7.9%. |
| Railway cybersecurity market | 14.31 (2025); 20.39 (2030) | USD bn | 2025 / 2030 | World | Rail cybersecurity | Mordor Intelligence | https://www.mordorintelligence.com/industry-reports/railway-cybersecurity-market | medium | CAGR 7.34%; onboard systems fastest at 11.24%. |
| Intelligent rail transit market | 59.01 (2026) | USD bn | 2026 | World | Intelligent rail transit (incl. video surveillance cameras) | Coherent Market Insights | https://www.coherentmarketinsights.com/industry-reports/intelligent-rail-transit-market | low | CAGR 6.8% to 2033. |
| Railway telematics market | 6.94 (2025); 10.02 (2030) | USD bn | 2025 / 2030 | World | Rail telematics | Mordor Intelligence | https://www.mordorintelligence.com/industry-reports/railway-telematics-market | medium | CAGR 7.62%. |
| Railway telematics market | 5.32 (2026); 7.29 (2030) | USD bn | 2026 / 2030 | World | Rail telematics | The Business Research Company | https://www.thebusinessresearchcompany.com/report/railway-telematics-global-market-report | low | CAGR 8.2%. |
| Railway telematics market | ~7.17 (2025) | USD bn | 2025 | World | Rail telematics | Expert Market Research | https://www.expertmarketresearch.com/reports/railway-telematics-market | low | |
| Railway telematics market | >9.9 (2025) | USD bn | 2025 | World | Rail telematics | Global Market Insights | https://www.gminsights.com/industry-analysis/railway-telematics-market | low | |
| Railway telematics market | 12.8 (2025); 28.6 (2034) | USD bn | 2025 / 2034 | World | Rail telematics | Dataintelo | https://dataintelo.com/report/railway-telematics-market | low | High outlier. |
| FRMCS market | 416 (2025); 1,073 (2032) | USD m | 2025 / 2032 | World | FRMCS | WIN MarketResearch | https://winmarketresearch.com/home/goods/detail/id/4433253.html | low | CAGR 14.7%. |
| FRMCS market | 419.02 (2025); 1,451.15 (2034) | USD m | 2025 / 2034 | World | FRMCS | Statifacts | https://www.statifacts.com/outlook/future-railway-mobile-communication-system-market | low | Consistent with WIN. |
| 5G FRMCS market | 1,000 (2025); 2,037 (2032) | USD m | 2025 / 2032 | World | 5G FRMCS | QYResearch (via openPR) | https://www.openpr.com/news/4413633/5g-frmcs-market-forecast-2026-2032-next-generation-railway | low | |
| FRMCS market (outlier) | 8.7 (2025); 15.4 (2034) | USD bn | 2025 / 2034 | World | FRMCS | Dataintelo | https://dataintelo.com/report/frmcs-market | low | ~20x other estimates; discard. |
| Railway communication equipment market | 682.1 (2025); 1,059.3 (2035) | USD m | 2025 / 2035 | World | Rail comms equipment (GSM-R 52.8% share) | Future Market Insights | https://www.futuremarketinsights.com/reports/railway-communication-equipment-market | low | CAGR 4.5%. |
| Digital twin railway market | 1.69 (2025); 3.15 (2030) | USD bn | 2025 / 2030 | World | Digital twin | The Business Research Company | https://www.thebusinessresearchcompany.com/report/digital-twin-railway-market-report | medium | CAGR 13.3% 2026-30. |
| Digital twin railway market | 4.8 (2025); 18.6 (2034) | USD bn | 2025 / 2034 | World | Digital twin | Dataintelo | https://dataintelo.com/report/digital-twin-railway-market | low | CAGR 16.2%. |
| Railway digital twin market growth | 29.36 | % CAGR | 2024-2030 | World | Digital twin | MarkNtel Advisors | https://www.marknteladvisors.com/research-library/railway-digital-twin-market.html | low | Outlier. |
| Digital railway market | 82.76 (2025); 127.54 (2030) | USD bn | 2025 / 2030 | World | Digital railway (umbrella) | MarketsandMarkets | https://www.prnewswire.com/news-releases/digital-railway-market-worth-127-54-billion-by-2030---exclusive-report-by-marketsandmarkets-302482163.html | medium | CAGR 9.0%. Umbrella; overlaps RMS, asset mgmt, PIS, signalling. Do not sum. |
| Digital railway market | 58.83 (2025); 65.33 (2026); 97.97 (2030) | USD bn | 2025-2030 | World | Digital railway | The Business Research Company | https://www.thebusinessresearchcompany.com/report/digital-railway-global-market-report | low | CAGR 10.7%. |
| Digital railway market growth | 9.4 | % CAGR | 2025-2035 | World | Digital railway | Future Market Insights | https://www.futuremarketinsights.com/reports/digital-railway-market | low | |
| Automatic train operation (ATO) system market | 9.6 (2024); 15.1 (2030) | USD bn | 2024 / 2030 | World | ATO | Strategic Market Research | https://www.strategicmarketresearch.com/market-report/automatic-train-operation-system-market | low | CAGR 7.8%. |
| ATO system market growth | 11.1 | % CAGR | 2025-2031 | World | ATO | Lucintel | https://www.lucintel.com/automatic-train-operation-system-market.aspx | low | |
| Autonomous train market | 9.84 (2025) | USD bn | 2025 | World | Autonomous train (incl. freight) | Fortune Business Insights | https://www.fortunebusinessinsights.com/autonomous-train-market-105494 | low | 8.9% CAGR to 2034; Europe 37.30% share; GoA4 11.0% CAGR. |
| Autonomous train market | 14.38 (2025) | USD bn | 2025 | World | Autonomous train | Straits Research | https://straitsresearch.com/report/autonomous-train-market | low | 4.98% CAGR 2026-34; GoA4 6.86%. |
| Autonomous train market | 12.23 (2024) | USD bn | 2024 | World | Autonomous train | Global Market Insights | https://www.gminsights.com/industry-analysis/autonomous-train-market | low | 6.9% CAGR 2025-34. |
| Autonomous train: passenger share; GoA mix | 61.37% passenger; GoA2 largest; GoA4 fastest (5.16%) | % | 2025 | World | Autonomous train | Mordor Intelligence | https://www.mordorintelligence.com/industry-reports/autonomous-train-market | low | 5.14% CAGR 2026-31. |
| Mainline ATO (GoA3-4) market | 2.9 -> 11.7 | USD bn | 2026 -> 2036 | World | Mainline ATO | Future Market Insights (via openPR) | https://www.openpr.com/news/4621084/mainline-rail-ato-goa3-4-market-advances-as-siemens | low | CAGR 15.0%. |
| Axle counter market | 0.94 (2025); 1.41 (2032) | USD bn | 2025 / 2032 | World | Axle counters (trackside detection) | Report Prime | https://www.reportprime.com/axle-counter-r7206 | low | CAGR 5.15%. Separate "axle counter systems" figure USD 1.58bn 2025: https://www.reportprime.com/axle-counter-systems-r7379 |
| Railway digital signal axle counters | 660 (2025); 1,020 (2032) | USD m | 2025 / 2032 | World | Axle counters | MarketResearchReports.com | https://www.marketresearchreports.com/reports/global-railway-digital-signal-axle-counters-market-strategic-research-report | low | CAGR 6.6%. |
| Train section axle counters | 699 (2025); 1,019 (2032) | USD m | 2025 / 2032 | World | Axle counters | MarketResearchReports.com | https://www.marketresearchreports.com/reports/global-train-section-axle-counters-market-strategic-research-report | low | CAGR 5.7%. |
| Vacancy detection axle counting systems | 1,023 (2025); 2,500 (2035) | USD m | 2025 / 2035 | World | Axle counters | Wise Guy Reports | https://www.wiseguyreports.com/reports/vacancy-detection-axle-counting-system-market | low | CAGR 9.3%. |
| Digital axle counter market; Europe | 1.2 total; 0.60 Europe | USD bn | 2025 | World / Europe | Axle counters | Verified Market Reports | https://www.verifiedmarketreports.com/product/digital-axle-counter-market/ | low | |
| Train section axle counters (outlier) | 10.96 (2025) | USD bn | 2025 | World | Axle counters | Data Insights Reports | https://www.datainsightsreports.com/reports/train-section-axle-counters-346465 | low | ~10x others; discard. |
| Hot box / hot wheel detectors, WILD, obstacle / intrusion detection | NOT FOUND | - | - | - | Trackside detection | - | - | - | GAP. Search budget exhausted before dedicated queries ran. |
| Onboard rail CCTV (standalone) | NOT FOUND | - | - | - | Onboard CCTV | - | - | - | GAP. Only bundled security figures found (Emergen, Coherent). |

---

## 3. Reconciliation notes for the sizing model

**Anchor for "Rail control / signalling & train control" (the core hardware + software + services block):**
- Primary-ish anchors: UNIFE EUR 22.3bn (2021-23 avg; medium) and SCI Verkehr EUR 19.3bn (2023) / ~EUR 20bn (2025) (medium). Both are global, both include freight, both include trackside + onboard + engineering / maintenance services.
- My arithmetic (not from a source): EUR 20-22bn x ~1.08-1.10 USD/EUR = ~USD 22-24bn. This matches the upper cluster of vendor estimates (GMI USD 19.6bn 2025; MRFR 21.4bn; Next Move 21.2bn; Dataintelo 21.6bn; Fortune 23.6bn; R&M "Intelligence Report" 19.85bn).
- Public-transit carve-out (to be done in the model): remove freight. GMI says mainline is ~47% of signalling (mainline includes passenger AND freight). SCI says Europe ~50% of CCS and is modernisation-driven (mostly passenger / mixed-traffic networks); North America CCS is PTC- and freight-heavy (GMI: US USD 4.2bn 2024). A reasonable working assumption is that urban (metro / LRT) ~35-45% + mainline passenger / commuter ~30-40% + freight ~20-30% of global CCS, but NO source gives this split directly - flag as analyst assumption.
- Growth: SCI 4.6% nominal (2023-28); R&M Intelligence Report 6.05% (2025-31); GMI 8.9% (2025-34, likely optimistic); UNIFE total market 3.0-3.2% real. Suggested model range for public-rail CCS 2025-2031: base 5-6%, low 4%, high 7-8%.
- Illustrative roll-forward (my arithmetic, low confidence): EUR 20bn (2025) at 4.6% -> ~EUR 26bn (2031); at 6% -> ~EUR 28bn (2031).

**Urban vs mainline:** use GMI 47% mainline / ~53% urban-plus-other as the central case, cross-checked against Dataintelo (urban 34%) and Archive (urban ~33% of a too-large total). Urban grows ~1-2 pts faster than mainline in every source that splits them (Dataintelo 10.1% vs 8.8%).

**CBTC:** central 2025 estimate USD 4.5-5.0bn (TBRC, Market Research Forecast, Verified Market Reports), 2030 USD 7.4-7.9bn, CAGR ~8-9%. Narrow estimates (USD 1.4-2.5bn) are probably onboard / equipment-only. Europe CBTC USD 0.75bn (GMI) implies Europe is ~15% of global CBTC, i.e. CBTC demand is Asia- (China-) and North-America-weighted.

**Replacement cycle:** 25-30 years for electromechanical / general signalling; 20-25 years for computer-based interlocking and electronic / software systems (obsolescence-driven); 35-45 years for relay interlockings. Network Rail's 63%-in-15-years renewal need and Sydney Trains' "most CBIs expire within a decade" both support a front-loaded renewal wave in the 2025-2035 window.

**Adjacent software layers (do NOT add to CCS):** RMS USD 55.5bn (M&M) is an umbrella that already contains traffic management, asset management, PIS and security; rail asset management USD 12.8bn (M&M) overlaps RMS; digital railway USD 82.8bn (M&M) overlaps everything. Use these for growth rates (6.5-9%) and relative segment weights (traffic management largest; Europe largest region ~35% of RMS = 19.3 / 55.5, my arithmetic).

**Freight flags:** UNIFE, SCI, all vendor signalling reports, PTC and axle counters include freight. PIS, CBTC, onboard CCTV and platform security are essentially passenger-only. Autonomous-train reports include freight (Mordor: passenger 61.37%).

---

## 4. Company notes (from search snippets only; no annual reports read this run)

| Company | Note | Source URL |
|---|---|---|
| Alstom, Siemens | Named top companies in railway management system market (MarketsandMarkets). | https://www.marketsandmarkets.com/ResearchInsight/railway-management-system-market.asp |
| Siemens, Alstom, Hitachi, Wabtec, IBM | Named top companies in rail asset management market (MarketsandMarkets). | https://www.marketsandmarkets.com/ResearchInsight/rail-asset-management-market.asp |
| Fujitsu, Hitachi Rail, PRASA, Huawei, Thales | Case studies featured in Research and Markets RMS report. | https://www.globenewswire.com/news-release/2026/03/02/3247144/0/en/76-bn-railway-management-system-solutions-market-global-forecast-to-2030-with-case-studies-featuring-fujitsu-hitachi-rail-prasa-huawei-thales.html |
| Thales (GTS, now Hitachi Rail) | ~250 km of CBTC-equipped automated metro lines; market leader for fully automated lines, followed by Siemens. | https://www.railway-technology.com/features/around-world-driverless-metro-lines/ |
| Siemens Mobility | First Nordic ATO-over-ETCS demonstration drive in Finland (mainline GoA3-4 context). | https://www.openpr.com/news/4621084/mainline-rail-ato-goa3-4-market-advances-as-siemens |
| BNSF | ~17,000 miles PTC installed vs ~15,000 mandated (freight; shows post-mandate expansion). | https://bnsf.com/news-media/railtalk/safety/ptc-2025.html |

Vendor revenue triangulation (Siemens Mobility rail infrastructure, Alstom Signalling, Hitachi Rail / Thales GTS, Wabtec Digital Intelligence) was NOT completed - search budget exhausted. GAP.

---

## 5. Gaps / next-pass list

1. UNIFE WRMS 2026 (11th ed.): CCS segment EUR volume, services segment, regional EUR volumes and 2029-31 growth by segment and region (paywalled at wrms.study; abstract on unife.org - fetch blocked).
2. UNIFE WRMS 2024 (10th ed.): confirm EUR 22.3bn rail control and the segment table against the UNIFE abstract (currently single secondary source, railway.supply); confirm Bain attribution for the 2024 edition (only the 2026 edition was explicitly attributed to Bain in snippets).
3. SCI Verkehr CCS study: obtain primary (sci.de) figures, publication date, 2030 forecast, regional table, and verify the "90% modernisation" claim.
4. UITP Statistics Brief on metro automation (Apr 2025): actual km of GoA4 lines, CBTC share, 2030 pipeline.
5. ERA / EC: EU-wide ETCS km in service (not just TEN-T), 2025 update; ETCS trackside and onboard unit costs (EUR per km, EUR per vehicle); Digitale Schiene Deutschland programme cost.
6. PTC: total programme cost (AAR), locomotives equipped, annual maintenance spend; commuter-rail share.
7. Trackside detection sizing: hot box / hot wheel detectors, WILD, obstacle / intrusion detection (no results captured).
8. Standalone onboard rail CCTV market (only bundled security figures found).
9. Resignalling cost benchmarks: NYCT CBTC USD per route-mile and MTA 2025-29 capital plan signals line; Network Rail CP7 signalling renewals budget; London Underground 4LM.
10. China urban rail operating mileage (China Association of Metros) and signalling renewal wave timing for lines opened 2005-2015.
11. Mordor Intelligence, Technavio and Precedence Research railway signalling reports (not surfaced by searches run).
12. Vendor revenue triangulation (Siemens Mobility, Alstom, Hitachi Rail, Wabtec, CRSC, Stadler Signalling, Hitachi/Thales) to bottom-up check the EUR 20-22bn CCS anchor.

---

## 6. Full source list (URLs seen in search results this run)

UNIFE / WRMS
- https://www.unife.org/news/global-rail-booms-as-closed-markets-now-cost-eu-industry-e97-billion-per-year/
- https://www.unife.org/news/policymakers-and-industry-give-vote-of-confidence-as-global-rail-supply-market-continues-to-expand-despite-geopolitical-tensions/
- https://www.unife.org/news-resources/wrms/
- https://www.unife.org/news/eu-rail-industry-looks-global-at-innotrans-amid-growing-trade-tensions/
- https://www.unife.org/news/unlocking-the-future-of-ertms-in-europe/
- https://www.unife.org/publication/world-rail-market-study-executive-summary-forecast-2020-to-2025/
- https://www.wrms.study/study
- https://www.railwaygazette.com/innotrans/2024/09/24/global-trends-driving-rail-market-growth-unife-study-confirms/
- https://www.railwaygazette.com/business/2026/10/09/world-rail-market-study-predicts-continuing-growth-following-covid-rebound/
- https://www.railway.supply/global-railway-market-report-2024-unifes-key-insights/
- https://www.railway.supply/share-of-world-rail-market-open-to-eu-suppliers-falls-to-56-from-59/
- https://www.railtarget.cz/business/global-rail-market-266-billion-eu-access-unife-12712.html
- https://www.railtarget.eu/business/10th-world-rail-market-study-reports-27-annual-growth-and-positive-outlook-for-the-decade-9296.html
- https://www.railtarget.cz/business/10th-world-rail-market-study-reports-27-annual-growth-and-positive-outlook-for-the-decade-9296.html
- https://railmarket.com/news/insights/63486-rail-market-grows-as-eu-access-narrows
- https://www.railwaypro.com/wp/global-rail-market-is-growing-but-closed-markets-are-costing/
- https://www.railwaypro.com/wp/rail-supply-market-continues-to-expand-despite-geopolitical-tensions/
- https://www.therailagenda.com/p/world-rail-market-grows-european
- https://www.indexbox.io/blog/world-rail-market-study-global-rail-market-to-grow-32-annually-to-2668bn-by-2029-31/
- https://www.rolandberger.com/en/Insights/Publications/UNIFE-World-Rail-Market-2020.html
- https://en.wikipedia.org/wiki/Union_des_Industries_Ferroviaires_Europ%C3%A9ennes

SCI Verkehr
- https://www.railwaypro.com/wp/europe-the-largest-market-for-digital-train-control-and-signalling/
- https://railmarket.com/news/business/53444-europe-leads-global-rail-signalling-market
- https://railmarket.com/news/technology-innovation/16494-unveiling-the-future-sci-verkehr-s-insights-into-rail-control-and-signaling-market-trends
- https://www.sci.de/shop/products?productid=41&L=1
- https://sci.de/fileadmin/user_upload/MC_Studien_Flyer/Flyer_MC_CCS_2019_de.pdf
- https://www.masstransitmag.com/rail/press-release/12238597/sci-verkehr-gmbh-control-command-and-signalling-in-rail-business-modern-systems-improve-safety-and-efficiency-worldwide

Signalling vendor reports
- https://www.gminsights.com/pressrelease/railway-signaling-system-market
- https://www.gminsights.com/industry-analysis/railway-signaling-system-market
- https://www.fortunebusinessinsights.com/railway-signalling-system-market-103658
- https://finance.yahoo.com/technology/articles/global-railway-signaling-market-intelligence-160400701.html
- https://www.einnews.com/pr_news/832587422/railway-signaling-system-market-to-reach-21-7-billion-by-2031-at-a-5-5-cagr-size-share-trends-demands-and-growth
- https://www.marketresearchfuture.com/reports/railway-signaling-system-market-13919
- https://www.imarcgroup.com/railway-signaling-system-market
- https://www.globalgrowthinsights.com/market-reports/railway-signaling-market-117220
- https://www.globalgrowthinsights.com/market-reports/railway-signaling-system-market-110216
- https://www.marketresearchintellect.com/product/railway-signaling-system-market/
- https://www.researchandmarkets.com/report/railway-signalling
- https://www.researchandmarkets.com/reports/6174873/railway-signaling-system-market-opportunity
- https://www.nextmsc.com/report/railway-signaling-system-market-at3550
- https://www.lucintel.com/railway-signaling-system-market.aspx
- https://www.valuemarketresearch.com/report/railway-signaling-system-market
- https://www.skyquestt.com/report/railway-signalling-system-market
- https://www.towardsautomotive.com/insights/railway-signaling-system-market-sizing
- https://www.cognitivemarketresearch.com/railway-signaling-system-market-report
- https://dataintelo.com/report/railway-signaling-market
- https://www.verifiedmarketreports.com/product/rail-signaling-and-train-control-systems-market/
- https://www.verifiedmarketreports.com/product/railway-signaling-system-market/
- https://www.futuremarketreport.com/industry-report/rail-signalling-systems-market
- https://www.wiseguyreports.com/reports/rail-signalling-systems-market
- https://www.wiseguyreports.com/reports/railway-signalling-interlocking-systems-market
- https://www.24marketreports.com/automotive-and-transportation/global-railway-signalling-train-control-systems-market
- https://www.reanin.com/reports/train-signalling-system-market
- https://www.verifiedmarketresearch.com/product/train-signalling-system-market/
- https://www.marknteladvisors.com/research-library/railway-signaling-system-market.html
- https://straitsresearch.com/report/railway-signaling-system-market
- https://www.mordorintelligence.com/industry-reports/train-control-and-management-system-market
- https://dataintelo.com/report/etcs-onboard-equipment-market
- https://dataintelo.com/report/train-control-and-management-systemtcms-market

Urban vs mainline / CBTC
- https://www.wiseguyreports.com/reports/urban-and-main-line-rail-signalling-equipment-market
- https://dataintelo.com/report/global-urban-rail-signalling-systems-market
- https://www.intelmarketresearch.com/urbanmain-line-rail-signalling-equipment-market-11319
- https://www.archivemarketresearch.com/reports/urban-and-main-line-rail-signalling-equipment-106553
- https://www.archivemarketresearch.com/reports/urban-rail-signalling-systems-134953
- https://www.datainsightsmarket.com/reports/urban-rail-signalling-systems-140607
- https://exactitudeconsultancy.com/reports/62555/global-urban-and-main-line-rail-signalling-equipment-market
- https://www.thebusinessresearchcompany.com/report/communication-based-train-control-system-global-market-report
- https://www.marketresearchforecast.com/reports/communication-based-train-control-cbtc-system-29120
- https://www.verifiedmarketreports.com/product/communication-based-train-control-cbtc-system-market/
- https://dataintelo.com/report/global-communications-based-train-control-cbtc-market
- https://www.globalgrowthinsights.com/market-reports/communications-based-train-control-cbtc-market-109768
- https://www.reportprime.com/communications-based-train-control-cbtc-r77
- https://www.marketresearchintellect.com/product/communications-based-train-control-cbtc-market/
- https://www.gminsights.com/industry-analysis/europe-communication-based-train-control-market
- https://www.researchandmarkets.com/reports/6219586/europe-communication-based-train-control-market
- https://www.researchandmarkets.com/reports/5954804/communication-based-train-control-system-market
- https://www.datainsightsreports.com/reports/communication-based-train-control-market-7720
- https://www.marketgrowthreports.com/market-reports/communications-based-train-control-cbtc-market-107995
- https://www.strategicmarketresearch.com/market-report/communication-based-train-control-market

Deployment statistics
- https://www.uitp.org/wp-content/uploads/sites/7/2025/04/Statistics-Brief-Metro-automation_final_web03.pdf
- https://www.railjournal.com/passenger/metros/uitp-forecasts-2200km-of-automated-metros-by-2025/
- https://www.railway-technology.com/features/around-world-driverless-metro-lines/
- https://railway-international.com/news/around-the-world-1000-km-of-fully-automated-metros
- https://en.wikipedia.org/wiki/List_of_driverless_train_systems
- https://railwaynews.net/wiki/what-is-cbtc-communications-based-train-control-explained
- https://cbtcbook.com/blog/chinese-metro-cbtc-50-cities/
- https://transport.ec.europa.eu/system/files/2023-09/ERTMS_work_plan-second_edition.pdf
- https://transport.ec.europa.eu/transport-modes/rail/ertms/state-play_en
- https://www.railwaypro.com/wp/only-19-of-vehicles-are-equipped-with-onboard-etcs-in-the-eu/
- https://www.railwaypro.com/wp/etcs-on-european-corridors-three-corridors-are-lagging/
- https://irg-rail.eu/download/5/1073/20245IRG-railNetworkaccesschallengesfollowingthedeploymentofERTMS.pdf
- https://www.railjournal.com/analysis/struggling-to-join-the-dots-on-the-etcs-route-map/
- https://corridor-nsrm.eu/ertms-information-day-2025-advancing-connectivity-across-europe/
- https://railroads.dot.gov/newsroom/press-releases/federal-railroad-administration-announces-landmark-achievement-full
- https://www.federalregister.gov/documents/2024/10/28/2024-24559/positive-train-control-systems
- https://railroads.dot.gov/sites/fra.dot.gov/files/2022-12/2022_12%20PTC%20FAQs_final.pdf
- https://railroads.dot.gov/sites/fra.dot.gov/files/2021-11/PTC%20Flyer_2021.pdf
- https://www.ttnews.com/articles/railroads-achieve-full-positive-train-control-implementation-fra-says
- https://www.roadsbridges.com/positive-train-control/news/10653616/fra-announces-full-implementation-of-positive-train-control
- https://bnsf.com/news-media/railtalk/safety/ptc-2025.html
- https://straitsresearch.com/report/positive-train-control-market
- https://www.verifiedmarketresearch.com/product/positive-train-control-market/
- https://www.industryarc.com/Research/positive-train-control-systems-market-research-800508
- https://www.datainsightsmarket.com/reports/positive-train-control-827410

Asset life / resignalling cycle
- https://www.railengineer.co.uk/a-signalling-exposition/
- https://amcouncil.win/2023/08/29/sydney-trains-management-of-assessing-condition-of-railway-signalling-systems-development-of-a-roadmap-for-life-extension-and-renewals/
- https://www.orr.gov.uk/sites/default/files/2023-12/nr-conventional-signalling-and-obsolescence-management-report.pdf
- https://www.modernrailways.com/article/signalling-still-crisis
- https://www.ctps.org/data/pdf/studies/transit/pmt/PMT_Ch5.pdf
- https://arxiv.org/pdf/2402.08343
- https://international-railway-safety-council.com/the-evolution-of-computer-based-railway-signalling-interlocking-systems/
- https://www.aivon.com/blog/pcb-knowledge/designing-for-obsolescence-strategies-for-long-life-railway-signaling-pcbs/

Railway management / asset management / maintenance
- https://www.marketsandmarkets.com/Market-Reports/railway-management-system-market-193193339.html
- https://www.marketsandmarkets.com/PressReleases/railway-management-system.asp
- https://www.prnewswire.com/news-releases/railway-management-system-market-76-00-billion-by-2030--marketsandmarkets-302628881.html
- https://www.marketsandmarkets.com/Market-Reports/geography/railway-management-system-market/europe
- https://www.marketsandmarkets.com/Market-Reports/geography/railway-management-system-market/UK
- https://www.marketsandmarkets.com/Market-Reports/geography/railway-management-system-market/UAE
- https://www.marketsandmarkets.com/ResearchInsight/railway-management-system-market.asp
- https://www.globenewswire.com/news-release/2026/03/02/3247144/0/en/76-bn-railway-management-system-solutions-market-global-forecast-to-2030-with-case-studies-featuring-fujitsu-hitachi-rail-prasa-huawei-thales.html
- https://www.researchandmarkets.com/reports/5766882/railway-management-system-market-report
- https://www.researchandmarkets.com/reports/5977897/railway-management-system-market-global
- https://www.barchart.com/story/news/33630457/railway-management-system-market-to-reach-usd-9514-billion-by-2030-driven-by-demand-for-digital-rail-operations-and-passenger-experience-mordor-intelligence
- https://www.researchnester.com/reports/railway-management-system-market/6104
- https://www.marketsandmarkets.com/Market-Reports/rail-asset-management-market-222416351.html
- https://www.marketsandmarkets.com/Market-Reports/geography/rail-asset-management-market/North-America
- https://www.marketsandmarkets.com/ResearchInsight/rail-asset-management-market.asp
- https://aijourn.com/rail-asset-management-market-worth-17-59-billion-by-2030-marketsandmarkets/
- https://www.researchandmarkets.com/reports/5188154/rail-asset-management-market-by-offering
- https://www.thebusinessresearchcompany.com/report/rail-asset-management-global-market-report
- https://dataintelo.com/report/railway-predictive-maintenance-market
- https://growthmarketreports.com/report/railway-predictive-maintenance-market
- https://growthmarketreports.com/report/predictive-maintenance-rail-market
- https://marketintelo.com/report/rail-predictive-maintenance-ai-market
- https://www.researchandmarkets.com/reports/5980339/rail-maintenance-management-system-market-report
- https://www.researchandmarkets.com/reports/5980337/railway-infrastructure-maintenance-services
- https://www.gminsights.com/industry-analysis/railway-maintenance-machinery-market

PIS / security / telematics / digital twin / ATO / trackside detection
- https://www.verifiedmarketresearch.com/product/railway-passenger-information-system-market/
- https://www.lucintel.com/railway-passenger-information-system-market.aspx
- https://www.marketresearchintellect.com/product/railway-passenger-information-system-market/
- https://www.marketsandmarkets.com/Market-Reports/automatic-passenger-counting-information-system-market-17856390.html
- https://www.grandviewresearch.com/press-release/global-passenger-information-system-market
- https://www.grandviewresearch.com/industry-analysis/passenger-information-system-market
- https://www.maximizemarketresearch.com/market-report/global-passenger-information-system-market/22104/
- https://www.marketresearchfuture.com/reports/passenger-information-system-market-2112
- https://www.nextmsc.com/report/passenger-information-system-market
- https://www.emergenresearch.com/industry-report/railway-safety-and-security-market
- https://www.openpr.com/news/4635822/railway-platform-security-market-research-reveals-strong-7-9
- https://www.mordorintelligence.com/industry-reports/railway-cybersecurity-market
- https://www.coherentmarketinsights.com/industry-reports/intelligent-rail-transit-market
- https://www.grandviewresearch.com/industry-analysis/connected-rail-market-report
- https://www.futuremarketinsights.com/reports/smart-railways-market
- https://www.mordorintelligence.com/industry-reports/railway-telematics-market
- https://www.thebusinessresearchcompany.com/report/railway-telematics-global-market-report
- https://www.expertmarketresearch.com/reports/railway-telematics-market
- https://www.gminsights.com/industry-analysis/railway-telematics-market
- https://dataintelo.com/report/railway-telematics-market
- https://www.researchandmarkets.com/report/railway-telematics
- https://winmarketresearch.com/home/goods/detail/id/4433253.html
- https://www.statifacts.com/outlook/future-railway-mobile-communication-system-market
- https://www.openpr.com/news/4413633/5g-frmcs-market-forecast-2026-2032-next-generation-railway
- https://dataintelo.com/report/frmcs-market
- https://www.futuremarketinsights.com/reports/railway-communication-equipment-market
- https://en.wikipedia.org/wiki/FRMCS
- https://www.thebusinessresearchcompany.com/report/digital-twin-railway-market-report
- https://dataintelo.com/report/digital-twin-railway-market
- https://www.marknteladvisors.com/research-library/railway-digital-twin-market.html
- https://www.prnewswire.com/news-releases/digital-railway-market-worth-127-54-billion-by-2030---exclusive-report-by-marketsandmarkets-302482163.html
- https://www.thebusinessresearchcompany.com/report/digital-railway-global-market-report
- https://www.futuremarketinsights.com/reports/digital-railway-market
- https://www.researchandmarkets.com/reports/5767641/digital-railway-market-report
- https://www.strategicmarketresearch.com/market-report/automatic-train-operation-system-market
- https://www.lucintel.com/automatic-train-operation-system-market.aspx
- https://www.fortunebusinessinsights.com/autonomous-train-market-105494
- https://straitsresearch.com/report/autonomous-train-market
- https://www.mordorintelligence.com/industry-reports/autonomous-train-market
- https://www.gminsights.com/industry-analysis/autonomous-train-market
- https://www.openpr.com/news/4621084/mainline-rail-ato-goa3-4-market-advances-as-siemens
- https://en.wikipedia.org/wiki/Automatic_train_operation
- https://www.reportprime.com/axle-counter-r7206
- https://www.reportprime.com/axle-counter-systems-r7379
- https://www.marketresearchreports.com/reports/global-railway-digital-signal-axle-counters-market-strategic-research-report
- https://www.marketresearchreports.com/reports/global-train-section-axle-counters-market-strategic-research-report
- https://www.wiseguyreports.com/reports/vacancy-detection-axle-counting-system-market
- https://www.verifiedmarketreports.com/product/digital-axle-counter-market/
- https://www.verifiedmarketreports.com/product/axle-counter-systems-market/
- https://www.datainsightsreports.com/reports/train-section-axle-counters-346465
- https://www.promarketreports.com/reports/axle-counter-systems-30992
