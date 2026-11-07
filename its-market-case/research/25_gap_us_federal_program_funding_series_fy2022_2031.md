# 25 — US federal transit funding series by program, FY2022–FY2031 (gap-fill for the demand model)

**Scope of this file.** Program-level FTA funding (apportioned / appropriated) for FY2022–FY2026 and FY2027–FY2031 under three scenarios (House BUILD America 250 Act; flat extension without IIJA advance appropriations; FY2027 President's request), a reconciliation of FY2025 Section 5307 "available" vs "apportioned", current reauthorization status (as of 7 Nov 2026), the SGR-backlog dollar figure, and FTA's written position on software / SaaS capital eligibility. Everything else in the US drivers story (state fiscal-cliff packages, ridership, ZEBs, PTASP/TSA, ITS JPO) stays in file 06.

**Research conditions (important for confidence grading).** The WebSearch budget for this run was exhausted before this task started, and WebFetch could not resolve any host. All evidence below therefore comes from documents downloaded directly (curl through the session proxy) from **govinfo.gov, federalregister.gov (API), transportation.house.gov, enotrans.org, masstransitmag.com and fhwa.dot.gov** and parsed locally. The following hosts were blocked by network policy (HTTP 403 or tunnel reset) and could not be used: transportation.gov (DOT IIJA authorization table PDF; FTA FY2027 CJ PDF), transit.dot.gov (FY2026 apportionment tables, SGR backlog PDF, SaaS FAQ, Circular 5010.1E), transportation.org (AASHTO June 2026 analysis), congress.gov / crsreports.congress.gov, cbo.gov, apta.com, web.archive.org (Wayback), gao.gov, bts.gov. Primary substitutes were found for each blocked document except the FTA January 2025 backlog PDF and the FTA SaaS FAQ (see Gaps).

---

## 1. Key takeaways

1. **FY2022–FY2026 program series is now fully sourced from statute and the FTA Federal Register apportionment notices.** 49 U.S.C. 5338(a) (as amended by IIJA) fixes Mass Transit Account contract authority per program per year (e.g., Section 5307: $6.408B FY2022 → $7.026B FY2026; Section 5337: $3.516B → $3.850B incl. the $300M/yr Rail Vehicle Replacement set-aside; 5339(a): $604M → $662M), and IIJA Division J added a flat **$4.25B/yr of advance appropriations** every year FY2022–FY2026 ($1.6B CIG, $950M SGR, $1.05B Low-No, $50M 5310, $350M ASAP, $50M electric ferry, $200M rural ferry). Total FTA appropriations were **$20.51B (FY2022), $21.43B (FY2023), $20.86B (FY2024), $20.94B (FY2025)** per the FR notices and **≈$20.96B (FY2026)** computed from P.L. 119-75 ($14.642B formula limitation, $1.70B CIG, $150M WMATA, $211.4M TIG, $7.5M TA) plus the $4.25B Division J tranche.
2. **No FY2026 Federal Register apportionment notice has been published** (the Federal Register API lists the FY2025 notice, published 15 Sept 2025, as the latest). FY2026 program amounts in this file are therefore statutory/appropriated amounts; "apportioned" figures for FY2026 are estimated using the FY2025 takedown structure and flagged as such.
3. **The FY2025 5307 "apportioned" ($7,394.7M) vs "available" ($6,851.7M) gap is fully reconciled**: $6,851.7M is the Section 5338(a)(2)(C) contract-authority line; FTA deducts 0.75% oversight ($51.4M), 0.75% State Safety Oversight ($51.4M) and the $30M Passenger Ferry set-aside, then **adds** Section 5340 High-Density ($372.4M) and Growing-States ($301.1M) formula funds and $2.3M of reapportioned lapsed funds. The model should use the $7.39B apportioned figure as what agencies can obligate and must **not** add the separately authorized $792M of 5340 on top of it.
4. **House bill (H.R. 8870, BUILD America 250) is the only reauthorization text that exists and it is stalled.** It authorizes $16.868B (FY2027) → $18.157B (FY2031) of Mass Transit Account funds ($87.59B over five years) plus $3.0B/yr of General-Fund CIG subject to appropriation ($15B) and $150M/yr WMATA — $103.3B total. Program design: 5307 **$7.745B in FY2027 (+10.2% vs FY2026 IIJA level)**, 5337 **$4.64B (−3.3% vs FY2026 MTA + advance; +20.5% vs MTA-only)**, 5339 consolidated bus/ferry **$1.695B (−23% vs FY2026 incl. Low-No advance; +47% vs MTA-only)**, **no Low-No program, no Rail Vehicle Replacement program, no advance appropriations**, $400M/yr ASAP set-aside inside 5307. The amendment in the nature of a substitute (18 May 2026) carries identical authorization numbers to the introduced bill. As of 7 Nov 2026 there is **no reported ("rh") print on govinfo, no House floor vote, no Senate Banking transit title**, and Eno (4 Sept 2026) judged the House's curtailed September schedule had "likely kill[ed] [the] chance of enacting surface reauthorization this year"; CBO's full cost estimate followed on 2 Oct 2026.
5. **The current-law fallback is the Surface Transportation Extension Act of 2026 (P.L. 119-103, Division C, 2 Sept 2026)**: programs continue at FY2026 levels pro-rated by an "extension fraction" of 72/365 (Oct 1–Dec 11, 2026, ≈19.7%); Mass Transit Account programs get 72/365 × FY2026 contract authority; General-Fund programs "not less than" the same fraction; **nothing continues the $4.25B/yr Division J advance appropriations**. No later public law (checked through P.L. 119-136, 22 Oct 2026) extends surface programs beyond 11 Dec 2026, so a further short-term extension is required by that date.
6. **The FY2027 President's request (Budget Appendix, govinfo) is a reauthorization placeholder for formula programs and a deep cut elsewhere**: a $14.95B Transit Formula Grants obligation limitation (+2.1% vs $14.642B, of which $308M is a "legislative proposal"), all FY2027 formula obligations booked as "Surface Transportation Reauthorization Activities" with **no program split**, **CIG $1.215B (vs $3.30B in FY2026 incl. $1.6B advance; −63%)**, **$0** for Transit Infrastructure Grants (vs $2.05B advance + transfers), **$0** ASAP, $150M WMATA. Total ≈ $16.3B vs ≈$20.96B enacted FY2026 (≈ −22%), consistent with APTA's −23%. For model purposes the $14.95B can be allocated pro-rata to the FY2026 statutory program shares (table in §4.3), clearly labelled as a derived allocation.
7. **Scenario spread for the model (FY2027, all FTA, USD B)**: House bill ≈ $20.0B (16.87 MTA + 3.0 CIG authorized + 0.15 WMATA) but only ≈ $18.7B if CIG is appropriated at the FY2026 $1.7B rate; flat full-year extension without advance appropriations ≈ $16.7B (14.642 + 1.70 CIG at CR rate + 0.15 WMATA + ≈0.2 TIG/TA); President's request ≈ $16.3B. Versus FY2026 enacted (≈$20.96B) that is roughly **−5% / −20% / −22%**; versus the IIJA five-year average the House bill's $87.6B guaranteed is **−14%** per APTA (file 06).
8. **SGR backlog**: the FTA January 2025 "Transit State of Good Repair National Backlog Analysis" PDF (2022 data) could not be retrieved (transit.dot.gov blocked; Wayback has a snapshot dated 2026-03-30 but web.archive.org is also blocked). The latest retrievable official figure is the **25th C&P Report to Congress (Feb 2024, 2018 data): $101.4B SGR backlog in 2018, growing to $106.2B by 2038 if 2014–2018 spending ($13.5B/yr) is sustained; $20.3B/yr needed to eliminate it by 2038**. The 24th C&P (2016 data) gave $105B with the split guideway $23.8B / facilities $11.0B / systems $30.6B / stations $19.9B / vehicles $20.0B, and the backlog = 14% of bus asset value vs 10% of rail asset value.
9. **SaaS / cloud capital eligibility — the statutory signal is strong, FTA's written FAQ could not be retrieved.** Current 49 U.S.C. 5302(4) defines "capital project" to include "(E) preventive maintenance" and "(F) leasing equipment or a facility", and every FTA apportionment notice since IIJA lists eligible 5307 capital as including "computer hardware and software" and states that "all preventive maintenance … costs are considered capital costs." H.R. 8870 §3002 would add a new subparagraph **"(O) software, contracted or wholly owned, that is related to the delivery of public transportation services, including software as a service and cloud-based software"** to the capital-project definition — i.e., Congress's drafters judged current law ambiguous enough to need an explicit SaaS/cloud clause. In its Jan 2025 Third-Party Contracting Guidance notice (C 4220.1G) FTA **declined** a transit agency's request to add guidance on "the eligibility of SaaS licensing for Federal funds", data ownership and cybersecurity responsibilities, calling them beyond the circular's scope. Net: a subscription-model entrant can today reach 80/20 formula capital money only by fitting SaaS into the preventive-maintenance/leasing/"software" buckets agency by agency; the House bill would remove that ambiguity if enacted.

---

## 2. Deliverable table — program × fiscal year (USD millions)

### 2.1 FY2022–FY2026 actual (statute + FTA apportionment notices)

Columns: "Auth/approp." = Mass Transit Account contract authority under 49 U.S.C. 5338(a) (or General-Fund appropriation where noted) **plus** the IIJA Division J advance appropriation for that program; "Apportioned" = amount FTA actually apportioned/allocated after oversight takedowns, set-asides and 5340 add-ons, as printed in the FR notice. FY2026 apportioned values are **estimates** (no FY2026 notice exists) using FY2025 takedown ratios.

| Program | FY2022 | FY2023 | FY2024 | FY2025 | FY2026 | Of which IIJA advance approp. (each yr) | Source |
|---|---|---|---|---|---|---|---|
| **5307 Urbanized Area formula — auth. (5338(a)(2)(C))** | 6,408.3 | 6,542.2 | 6,713.0 | 6,851.7 | 7,025.8 | 0 | 49 USC 5338 [S1]; FR notices [S2–S5] |
| 5307 — apportioned to UZAs (after takedowns, + 5340, + reapportioned) | 6,920.9 | 7,060.1 | 7,245.0 | 7,394.7 | ≈7,581 (est.) | 0 | FR notices [S2–S5]; FY2026 est. (§3) |
| **5340 Growing States / High-Density — auth.** (apportioned inside 5307 and 5311 lines above/below) | 741.0 | 756.5 | 776.3 | 792.3 | 812.5 | 0 | 49 USC 5338(a)(2)(O) [S1]; FY2022 notice table [S2] |
| **5337 State of Good Repair — auth. incl. $300M RVR** (MTA) | 3,515.5 | 3,587.8 | 3,680.9 | 3,755.7 | 3,850.5 | 0 | [S1] |
| 5337 — total available incl. $950M advance | 4,465.5 | 4,537.8 | 4,630.9 | 4,705.7 | 4,800.5 | 950 | FY2022 notice 5-yr table [S2]; [S3–S5] |
| 5337 — apportioned formula (after oversight/OIG, less $300M RVR) | 4,111.5 | 4,183.7 | 4,275.3 | 4,349.9 | ≈4,446 (est.) | — | [S2–S5] |
|   of which High-Intensity Fixed Guideway | 3,994.3 | 4,063.7 | 4,153.4 | 4,225.9 | ≈4,320 (est.) | — | [S2–S5] |
|   of which High-Intensity Motorbus | 117.2 | 119.9 | 121.8 | 123.9 | ≈126 (est.) | — | [S2–S5] |
| **5337(f) Rail Vehicle Replacement (competitive set-aside)** | 300.0 | 300.0 | 300.0 | 300.0 | 300.0 | 0 | [S1]; [S2–S5] |
| **5339(a) Bus & Bus Facilities formula — auth.** | 604.0 | 616.6 | 632.7 | 645.8 | 662.2 | 0 | [S1] |
| 5339(a) — apportioned (after 0.75% oversight, + reapportioned) | 601.2 | 613.2 | 630.3 | 643.9 | 657.2 (FY2022-notice table) | 0 | [S2–S5] |
| **5339(b) Bus competitive — available for allocation** (MTA after oversight & Low-No takedown; FY2022/23 incl. $175M/$90M TIG add-ons) | 372.3 (+175 TIG) | 469.4 | 390.0 | 398.1 | 408.2 (FY2022-notice table) | 0 | [S2–S5] |
| **5339(c) Low-No — available for allocation** (MTA $71.6–78.5M + $1.05B advance, after 2% takedown; FY2022/23 incl. $75M/$50M TIG) | 1,100.6 (+75 TIG) | 1,151.7 | 1,104.0 | 1,105.5 | 1,107.5 (FY2022-notice table); $1,029.0 net IIJA for FY2026 per Jan-2026 award notice | 1,050 | [S2–S5]; [S9] |
| **5310 Enhanced Mobility — appropriated (MTA + $50M advance)** | 421.2 | 429.0 | 438.9 | 446.9 | 457.0 (computed) | 50 | [S1]; [S2–S5] |
| 5310 — apportioned | 422.0 | 428.0 | 438.2 | 443.9 | ≈454 (est.) | — | [S2–S5] |
| **5311 Rural — auth. (incl. RTAP, ADTAP, Tribal, 5311(b)(3))** | 875.3 | 893.6 | 916.9 | 935.8 | 959.6 | 0 | [S1] |
| 5311 — formula portion available | 785.1 | 804.2 | 825.2 | 842.3 | ≈864 (est.) | 0 | [S2–S5] |
| 5311 — apportioned incl. 5340 Growing States | 893.7 | 914.6 | 938.7 | 956.6 (notice table internally inconsistent — see §3.2) | ≈980 (est.) | — | [S2–S5] |
| **5305 Metropolitan & statewide planning — auth.** | 184.6 | 188.5 | 193.4 | 197.4 | 202.4 | 0 | [S1] |
| **CIG (5309) — General Fund appropriation** | 2,248.0 | 2,200.0 (+425 for FFGA projects) | 2,200.0 | 2,205.0 | 1,700.0 | — | [S2–S5]; P.L. 119-75 [S7]; Appendix [S8] |
| CIG — total incl. $1.6B advance (before 1% oversight) | 3,848.0 | 3,810.0 (+425) | 3,805.0 | 3,805.0 | 3,300.0 | 1,600 | [S2–S5]; [S8] |
| **All Stations Accessibility (ASAP) — advance approp.** | 350.0 | 350.0 | 350.0 | 350.0 | 350.0 | 350 | [S2–S5]; Appendix [S8] |
| **Ferry programs — advance approp.** (electric/low-emitting ferry + rural ferry) | 250.0 | 267.5 | 250.0 | 250.0 | 250.0 | 50 + 200 | [S3–S5] |
| **WMATA (PRIIA §601) — GF** | 150.0 | 150.0 | 150.0 | 150.0 | 150.0 | 0 | [S2–S5]; [S7] |
| **Transit Infrastructure Grants — GF discretionary add-ons (ferry, bus testing, research, CPF/CDS, etc.)** | 504.3 | 542.0 | 253.4 | 45.6 | 211.4 | 0 | [S2–S5]; [S7] |
| **Mass Transit Account total (5338(a)(1))** | 13,355.0 | 13,634.0 | 13,990.0 | 14,279.0 | 14,642.0 | 0 | [S1]; [S7] |
| **IIJA Division J advance appropriations total** | 4,250.0 | 4,250.0 | 4,250.0 | 4,250.0 | 4,250.0 | 4,250 | [S2–S5]; [S8] |
| **TOTAL FTA appropriated (all sources)** | 20,514.8 | 21,432.4 | 20,855.9 | 20,937.1 | ≈20,960.9 (computed) | — | [S2–S5]; [S7] |

Notes: (i) FY2023 TIG included $360.5M of Community Project Funding and the Consolidated Appropriations Act 2023 added $425M for CIG projects with existing FFGAs, which is why FY2023 is the series peak. (ii) FY2024 TIG = $252.39M + $1M added by the Further Consolidated Appropriations Act 2024. (iii) FY2026 TIG ($211.4M) includes $147.9M CPF/CDS, $25M ferry, $20M rural ferry, $15M operating assistance for transit security (10 highest-ridership recipients), $2M AIM, $1.5M bus testing; P.L. 119-75 also repurposed $40.8M of Division J oversight balances. (iv) Appendix obligations by program (Transit Formula Grants account, FY2025 actual / FY2026 est.): UZA 9,853 / 10,050; SGR 3,846 / 3,923; 5339(a) 611 / 623; bus competitive 444 / 453; 5311 1,182 / 1,207; 5310 419 / 427; planning 60 / 61 — these are obligations (incl. prior-year carryover), not apportionments [S8].

### 2.2 FY2027–FY2031 — three scenarios (USD millions, authorization / request levels)

**Scenario A — House BUILD America 250 Act (H.R. 8870 §3023, introduced text 19 May 2026 = ANS text 18 May 2026).** Mass Transit Account contract authority; CIG is General Fund "authorized to be appropriated".

| Program (House bill nomenclature) | FY2027 | FY2028 | FY2029 | FY2030 | FY2031 | 5-yr | Source |
|---|---|---|---|---|---|---|---|
| 5305 Planning | 222.93 | 225.82 | 228.76 | 231.73 | 234.75 | 1,144.0 | [S10]/[S11] |
| **5307 Urbanized Area** (incl. new $400M/yr ASAP set-aside; STIC 3%→5%; $125M urban ferry set-aside) | 7,745.47 | 7,869.92 | 7,996.36 | 8,124.82 | 8,255.34 | 39,991.9 | [S10]/[S11] §3021, §3023 |
| 5310 Enhanced Mobility (incl. $10M ICAM) | 447.30 | 453.10 | 459.00 | 465.00 | 471.00 | 2,295.4 | [S10] |
| 5311 Rural | 1,007.62 | 1,023.74 | 1,040.12 | 1,056.76 | 1,073.67 | 5,201.9 | [S10] |
| 5312 Innovation/research | 45.24 | 45.96 | 46.70 | 47.44 | 48.20 | 233.5 | [S10] |
| 5314 Technical assistance & workforce | 20.50 | 20.81 | 21.12 | 21.43 | 21.76 | 105.6 | [S10] |
| 5318 Bus testing | 7.00 | 7.11 | 7.21 | 7.32 | 7.43 | 36.1 | [S10] |
| 5324 Emergency relief | 25.00 | 25.00 | 25.00 | 25.00 | 25.00 | 125.0 | [S10] |
| 5334 Administrative expenses | 132.70 | 135.40 | 138.10 | 140.80 | 143.60 | 690.6 | [S10] |
| 5335 NTD | 6.24 | 6.34 | 6.44 | 6.54 | 6.64 | 32.2 | [S10] |
| **5337 State of Good Repair** (Rail Vehicle Replacement competitive program eliminated, §3022) | 4,640.0 | 4,645.0 | 4,650.0 | 4,655.0 | 4,660.0 | 23,250.0 | [S10]; [S11] §3022 |
| **5339 Buses, Bus Facilities & Ferries** (Low-No subsection eliminated; $336M state/territory floor, remainder 62% formula / 38% competitive) | 1,695.0 | 1,863.71 | 2,014.89 | 2,149.55 | 2,295.51 | 10,018.7 | [S10] §3024; [S12] |
|   derived: formula side (floor + 62%) | 1,178.6 | 1,283.2 | 1,376.9 | 1,460.4 | 1,550.9 | 6,850.0 | computed |
|   derived: competitive side (38%) | 516.4 | 580.5 | 638.0 | 689.1 | 744.6 | 3,168.7 | computed |
| 5340 Growing States / High-Density | 873.0 | 883.1 | 893.3 | 903.6 | 914.1 | 4,467.1 | [S10] |
| **Mass Transit Account total (5338(a)(1))** | 16,868.0 | 17,205.0 | 17,527.0 | 17,835.0 | 18,157.0 | 87,592.0 | [S10]; sums verified |
| **CIG (5338(b)) — GF, subject to appropriation** | 3,000.0 | 3,000.0 | 3,000.0 | 3,000.0 | 3,000.0 | 15,000.0 | [S10] |
| WMATA (PRIIA §601(f) extended through 2031, §3109) | 150.0 | 150.0 | 150.0 | 150.0 | 150.0 | 750.0 | [S11] §3109 |
| IIJA-style advance appropriations | 0 | 0 | 0 | 0 | 0 | 0 | [S10] (none in bill); file 06 CRS |
| **Total authorized** | 20,018.0 | 20,355.0 | 20,677.0 | 20,985.0 | 21,307.0 | 103,342.0 | computed; = APTA "$103.3B authorized / $87.6B guaranteed" |

**Scenario B — Flat extension of FY2026 levels without advance appropriations (current law mechanics of P.L. 119-103 Division C, annualized).** FY2027 amounts = FY2026 49 U.S.C. 5338 levels × 365/365 if extended for a full year (the enacted extension only covers 72/365 of the year through 11 Dec 2026). Shown flat FY2027–FY2031 (the model may index); General-Fund items shown at the FY2026 enacted rate that a continuing resolution carries forward.

| Program | FY2027 (full-year equivalent) | FY2028–FY2031 (flat) | Enacted so far (72/365 fraction, Oct 1–Dec 11 2026) | Source |
|---|---|---|---|---|
| 5307 | 7,025.8 | 7,025.8 | 1,386.0 | [S1]; [S6] §3101(b)(1)(B) |
| 5340 | 812.5 | 812.5 | 160.3 | [S1]; [S6] |
| 5337 incl. $300M RVR (MTA only) | 3,850.5 | 3,850.5 | 759.6 | [S1]; [S6] |
| 5339(a) | 662.2 | 662.2 | 130.6 | [S1]; [S6] |
| 5339(b)+(c) MTA only (Low-No falls to $78.5M) | 490.4 | 490.4 | 96.7 | [S1]; [S6] |
| 5310 (MTA only) | 407.0 | 407.0 | 80.3 | [S1]; [S6] |
| 5311 | 959.6 | 959.6 | 189.3 | [S1]; [S6] |
| 5305 | 202.4 | 202.4 | 39.9 | [S1]; [S6] |
| Mass Transit Account total | 14,642.0 | 14,642.0 | 2,888.3 | [S1]; [S6] |
| CIG — GF (CR carries FY2026 rate $1.70B; authorization "not less than" 72/365 × $3.0B) | 1,700.0 | 1,700.0 | 335.3 (CR rate) | [S6] §3101(b)(2); [S7] |
| WMATA | 150.0 | 150.0 | 29.6 | [S6]; [S7] |
| TIG / TA (GF, CR rate) | ≈218.9 | ≈218.9 | ≈43.2 | [S7] |
| **IIJA advance appropriations (SGR $950M, Low-No $1,050M, CIG $1,600M, ASAP $350M, 5310 $50M, ferries $250M)** | **0** | **0** | **0** | [S6] (not continued); file 06 UCS/NACo |
| **Total** | ≈16,711 | ≈16,711 | ≈3,296 | computed |

**Scenario C — FY2027 President's Budget request (Budget Appendix FY2027, DOT/FTA, govinfo).** One-year request only; FY2028–FY2031 not specified (model: hold flat or index — flagged assumption).

| Account / program | FY2025 actual | FY2026 est. (enacted) | FY2027 request | Source |
|---|---|---|---|---|
| Transit Formula Grants — contract authority (MTA) | 14,279 | 14,642 | **14,950** (incl. $308M "legislative proposal, not subject to PAYGO") | Appendix 069-8350 [S8] |
| Transit Formula Grants — obligation limitation (Transportation Trust Funds) | 15,660 | 15,942 | 16,250 | [S8] |
| Formula program split in FY2027 | itemized (UZA 9,853; SGR 3,846; 5339(a) 611; bus comp. 444; 5311 1,182; 5310 419; planning 60 …) | itemized (10,050; 3,923; 623; 453; 1,207; 427; 61 …) | **not itemized — all $17,358M of FY2027 obligations booked as "Surface Transportation Reauthorization Activities"** | [S8] |
| Derived pro-rata allocation of $14,950M using FY2026 5338 shares (illustrative; not in the request) | — | — | 5307 7,173.6; 5340 829.5; 5337 3,931.5; 5339(a) 676.1; 5339(b)+(c) 500.7; 5310 415.6; 5311 979.8; 5305 206.7; admin 150.5 | computed from [S1] |
| Capital Investment Grants — new BA (GF) | 2,205 | 1,700 | **1,215** | [S8]; [S7] |
| CIG — IIJA advance appropriation | 1,600 | 1,600 | **0** | [S8] |
| CIG — total budget authority | 3,805 | 3,300 | 1,215 | [S8] |
| Transit Infrastructure Grants (Division J advance: SGR $950M, Low-No $1,050M, 5310 $50M + transfers) — BA | 2,096 | 2,221 | **0** ("no additional resources requested") | [S8] |
| All Stations Accessibility — advance approp. | 350 | 350 | **0** | [S8] |
| WMATA | 150 | 150 | 150 | [S8] |
| Technical assistance & training (obligations) | 5 | 5 | 5 | [S8] |
| **Approx. total FTA new budget authority** | ≈20,937 (FR notice) | ≈20,961 (computed) | **≈16,320** | computed; APTA "$16.3B, −23%" (file 06) |

**Scenario comparison, FY2027 (USD B):** IIJA-equivalent FY2026 ≈ 20.96 → House bill 20.02 authorized (18.72 if CIG stays at $1.7B appropriation) → flat extension w/o advance ≈ 16.71 → President's request ≈ 16.32. Formula-only (MTA) view: 14.64 → 16.87 (+15.2%) / 14.64 (0%) / 14.95 (+2.1%). The large swing is entirely in the $4.25B/yr advance-appropriation tranche (SGR, Low-No, CIG, ASAP) and in CIG new BA.

---

## 3. Reconciliations and data notes

### 3.1 FY2025 Section 5307: $6,851.7M "available" vs $7,394.7M "apportioned" (FR 2025-17784, Table "Urbanized Area Formula Program—FY 2025")

| Step | USD |
|---|---|
| Total appropriation (49 U.S.C. 5338(a)(2)(C) contract authority for 5307) | 6,851,662,142 |
| less Oversight deduction (0.75%) | (51,387,466) |
| less State Safety Oversight program (0.75%) | (51,387,466) |
| less Passenger Ferry Grant set-aside | (30,000,000) |
| plus Section 5340 High-Density States formula | 372,387,459 |
| plus Section 5340 Growing States formula (5307 share; the 5311 share is apportioned to rural) | 301,096,803 |
| plus reapportioned lapsed funds | 2,344,574 |
| **Total apportioned to urbanized areas** | **7,394,716,046** |

Check: 6,851,662,142 − 132,774,932 + 675,828,836 = 7,394,716,046 (exact). Interpretation for the model: the FTA 5307 program page and most trade sources quote the $7.39B because it is the amount in FTA's Table 3 that designated recipients can obligate; $6.85B is the statutory 5307 line before 5340 formula factors. Use one or the other consistently; the authorized 5340 amount ($792.3M in FY2025) is already inside the $7.39B (5307 share) and the $956.6M 5311 apportionment (rural share). The same structure applies in FY2022 ($6,408.3M → $6,920.9M), FY2023 ($6,542.2M → $7,060.1M) and FY2024 ($6,713.0M → $7,245.0M).

### 3.2 Other data-quality flags
- **FY2025 5311 table in FR 2025-17784 is internally inconsistent**: it prints Total appropriation $842,263,842, oversight ($469,244), 5340 Growing States $18,829,480, reapportioned $229,376 and Total apportioned $956,643,454; the components sum to $860.9M, not $956.6M. FY2024's equivalent entries were ($4,584,538) and $117,577,660, so the FY2025 figures look like typographical drops of a leading digit. The stated total ($956.6M) is consistent with the FY2022–FY2024 trend and is used here.
- **FY2026 "apportioned" values are estimates**: 5307 ≈ $7,581M (= $7,025.8M − 0.75% − 0.75% − $30M + $381.9M HD + ≈$308.8M GS share using the FY2025 5307/5311 split); SGR ≈ $4,446M (= ($4,800.5M − $300M RVR) × (1 − 1.2%)). Replace with FTA Table 1/3/13 FY2026 values when transit.dot.gov is reachable.
- **FY2026 Low-No**: IIJA FY2026 Low-No = $1,029.0M net of the 2% takedown; FTA pulled part of it forward into the Jan 2026 combined FY2025/FY2026 award ($1,630.3M Low-No to 103 projects + $397.7M bus to 62 projects = $2,027.9M, 165 projects; total Low-No available incl. prior-year balances $2,140.8M) and awarded a further $388.3M of FY2026 bus funds to 34 projects in Mar 2026 [S9]. This is why the later FY2026 NOFO quoted in file 06 was only $610M — most FY2026 Low-No money was already committed.
- **IIJA five-year totals quoted by FTA**: $108.15B total FTA authorization = $69.9B Mass Transit Account + $21.25B advance appropriations + $17B General Fund authorizations (incl. $15B CIG); 5307 $33.5B; 5337 $18.39B incl. $1.5B RVR + $4.75B advance; 5339 $5.5B + $5.25B Low-No advance; 5310 $1.9B + $0.25B advance; 5311 $4.6B; 5340 $3.879B [S2–S5]. APTA's "$119.9B IIJA baseline" used to score the House bill (file 06) is larger than $108.15B and is presumably an inflation-indexed or appropriations-based baseline — treat the −14% as APTA's number, not reproducible from statute here.

---

## 4. Reauthorization status as of 7 November 2026

| Item | Status | Source |
|---|---|---|
| H.R. 8870 BUILD America 250 Act | Text released 17 May 2026 ($474B per Eno; ≈$580B per Mass Transit/T&I incl. GF); ANS dated 18 May 2026 (11:16 pm); introduced 19 May 2026; T&I markup 21–22 May 2026, approved (62-2 / 61-2 per file 06 sources). Transit title authorization numbers in the ANS are identical to the introduced text. **No reported ("rh") print exists on govinfo (HTTP 404)**, i.e., no House report filed; no House floor vote found. | govinfo BILLS-119hr8870ih [S10]; T&I ANS PDF [S12]; Eno timeline [S13]; Mass Transit [S14] |
| House floor outlook | Eno, 28 Aug 2026: "no sign of surface bill"; 4 Sept 2026: House leadership cut the pre-election September session short, "likely killing chance of enacting surface reauthorization this year"; 2 Oct 2026: CBO released its full cost estimate of the House bill (cbo.gov blocked — figures not captured). | Eno [S13] |
| Senate | No Senate Banking Committee transit title, and no EPW/Commerce bill, appears on Eno's reauthorization tracker or in any document retrieved; file 06 (Holland & Knight, July 2026) likewise reported no Senate action. | [S13]; file 06 |
| Extension | P.L. 119-103, Continuing Appropriations and Extensions Act, 2027 (H.R. 6500, enacted 2 Sept 2026): Division A CR + Division C "Surface Transportation Extension Act of 2026" — covered laws (incl. 49 U.S.C. ch. 53) continue through **11 Dec 2026**; MTA programs authorized at 72/365 × FY2026 amounts; GF programs "not less than" 72/365 × FY2026; obligation limitation pro-rated the same way; advance appropriations not addressed (they lapse). | govinfo PLAW-119publ103 [S6] |
| Further extension | None: public laws 119-104 through 119-136 (latest enacted 22 Oct 2026) are all unrelated. A further CR/extension is required by 11 Dec 2026. | govinfo PLAW-119publ104…136 [S15] |
| FY2027 appropriations | No full-year THUD act; CR at FY2026 rates to 11 Dec 2026. | [S6] |
| FY2027 President's request | $14.95B formula limitation; CIG $1.215B; no advance appropriations; formula programs not itemized. | Budget Appendix [S8] |

Implication for the 2025–2031 model: FY2027 federal transit money will almost certainly be a CR/extension patchwork through at least the first quarter of FY2027, with formula programs flat in nominal terms and the $4.25B advance tranche gone unless a full reauthorization restores it (the House bill does not). Formula-funded SGR-type ITS refresh (CAD/AVL, APC, onboard video, PIDs, signalling renewal) remains the durable demand pool; Low-No/CIG-linked ITS packages are the exposed pool.

---

## 5. SGR backlog and SaaS / software capital eligibility (drivers-section inputs)

### 5.1 SGR backlog
- **FTA, Transit State of Good Repair National Backlog Analysis (Jan 2025, 2022 data, 2022$)** — not retrievable in this run (transit.dot.gov 403; Wayback snapshot exists at `http://web.archive.org/web/20260330232150/https://www.transit.dot.gov/sites/fta.dot.gov/files/2025-01/Transit-State-of-Good-Repair-National-Backlog-Analysis_0.pdf` but web.archive.org connections were reset). **Dollar total still open.**
- **DOT/FHWA/FTA, 25th C&P Report to Congress (submitted 22 Feb 2024; 2018 data)**: transit SGR backlog **$101.4B in 2018, rising to $106.2B by 2038** under "Sustain 2014–2018 Spending" ($13.5B/yr); the **SGR Benchmark requires $20.3B/yr** (50% above 2014–18 spending) to eliminate the backlog by 2038; average asset condition 3.4 (2018) → 3.5 (benchmark) or 3.3 (sustain) [S16].
- **24th C&P (2016 data)**: backlog **$105B** = guideway $23.8B + facilities $11.0B + systems $30.6B + stations $19.9B + vehicles $20.0B; 89% of the $984B transit asset base in SGR; backlog = 14% of fixed-route bus asset value and 10% of rail asset value; 82% of the bus backlog is in vehicles and facilities [S17]. Systems (signals/communications/ITS-type assets) are the single largest backlog category — directly relevant to the rail signalling and communications demand pool.
- Prior editions quoted in file 06 ($85.9B 23rd C&P / $98.8B) remain consistent with this trajectory.

### 5.2 FTA's written position on software, SaaS and preventive maintenance
- **Statute (49 U.S.C. 5302(4), 2023 ed.)**: "capital project" includes "(E) preventive maintenance" and "(F) leasing equipment or a facility for use in public transportation" (plus rolling stock, facilities, equipment, etc.). No explicit "software" or "subscription" term [S18].
- **FTA apportionment notices (FY2022–FY2025, identical language)**: eligible 5307 activities include "capital investments in new and existing fixed guideway systems including rolling stock, overhaul and rebuilding of vehicles, track, signals, communications, and computer hardware and software. All preventive maintenance and some Americans with Disabilities Act complementary paratransit service costs are considered capital costs." [S2], [S4].
- **FTA, Third Party Contracting Guidance (Circular 4220.1G) notice, FR 2025-00992, 16 Jan 2025**: a transit authority asked FTA to expand the circular's SaaS guidance — "shared data ownership in SaaS agreements, the eligibility of SaaS licensing for Federal funds, and detailed clarification about the respective cybersecurity responsibilities of the customer and the SaaS vendor," plus data-portability requirements and model clauses. "FTA Response: FTA declines to make these revisions … The guidance in the Circular section acknowledges these data issues at a high level, while not being unnecessarily prescriptive, and allows recipients and their vendors to make these determinations for themselves." [S19]. (This confirms C 4220.1G contains a SaaS section, but the circular itself is on transit.dot.gov and could not be read.)
- **H.R. 8870 §3002 (House bill)** would add to the 5302 capital-project definition: "(O) software, contracted or wholly owned, that is related to the delivery of public transportation services, including software as a service and cloud-based software." The T&I section-by-section describes this as "clarify[ing] that certain software is eligible as a capital project for purposes of Federal transit law." §3115 also orders a GAO assessment of federally funded ADA paratransit software and technologies [S10], [S11].
- **Model implication**: today SaaS subscriptions reach 80% federal capital share only through the preventive-maintenance / leasing / "computer hardware and software" eligibility routes (agency-by-agency, with FTA explicitly declining to issue detailed SaaS eligibility guidance in Jan 2025); the House bill would make SaaS/cloud expressly capital-eligible. Keep a "SaaS eligibility clarified (Y/N)" switch in the model; it mainly affects the subscription-model entrant's addressable share of 5307/5337/5339 formula dollars rather than the dollar totals above.

---

## 6. Findings table

| # | Claim | Value | Unit | Year | Geography | Segment | Source name | URL | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Mass Transit Account contract authority (5338(a)(1)) | 13,355 / 13,634 / 13,990 / 14,279 / 14,642 | USD M | FY2022–26 | US | Transit | 49 U.S.C. 5338 (2023 ed., govinfo) | https://www.govinfo.gov/content/pkg/USCODE-2023-title49/html/USCODE-2023-title49-subtitleIII-chap53-sec5338.htm | high | Statute; FY2026 also in P.L. 119-75 |
| 2 | Section 5307 contract authority | 6,408.3 / 6,542.2 / 6,713.0 / 6,851.7 / 7,025.8 | USD M | FY2022–26 | US | Bus+rail | 49 U.S.C. 5338(a)(2)(C) | same | high | |
| 3 | Section 5307 apportioned to UZAs | 6,920.9 / 7,060.1 / 7,245.0 / 7,394.7 | USD M | FY2022–25 | US | Bus+rail | FR 2022-09143; 2023-07761; 2024-11934; 2025-17784 | https://www.govinfo.gov/content/pkg/FR-2025-09-15/html/2025-17784.htm (and FY-specific URLs in §7) | high | After takedowns, + 5340 |
| 4 | FY2025 5307 reconciliation components | −51.39 / −51.39 / −30.0 / +372.39 / +301.10 / +2.34 | USD M | FY2025 | US | Bus+rail | FR 2025-17784 | https://www.govinfo.gov/content/pkg/FR-2025-09-15/html/2025-17784.htm | high | Sums exactly |
| 5 | Section 5337 SGR contract authority (incl. $300M RVR) | 3,515.5 / 3,587.8 / 3,680.9 / 3,755.7 / 3,850.5 | USD M | FY2022–26 | US | Rail-heavy | 49 U.S.C. 5338(a)(2)(L) | USCODE link above | high | |
| 6 | SGR total available incl. $950M advance | 4,465.5 / 4,537.8 / 4,630.9 / 4,705.7 / 4,800.5 | USD M | FY2022–26 | US | Rail-heavy | FR 2022-09143 five-year table; FR FY2023–25 notices | https://www.govinfo.gov/content/pkg/FR-2022-04-28/html/2022-09143.htm | high | |
| 7 | SGR apportioned (HIFG / HIMB) | 4,111.5 (3,994.3/117.2); 4,183.7 (4,063.7/119.9); 4,275.3 (4,153.4/121.8); 4,349.9 (4,225.9/123.9) | USD M | FY2022–25 | US | Rail / BRT-bus | FR notices | as above | high | After oversight, OIG, $300M RVR |
| 8 | 5339(a) bus formula authorized / apportioned | 604.0/601.2; 616.6/613.2; 632.7/630.3; 645.8/643.9; 662.2/657.2 | USD M | FY2022–26 | US | Bus | 49 U.S.C. 5338; FR notices | as above | high | FY2026 apportioned from FY2022-notice 5-yr table |
| 9 | 5339(b) bus competitive available | 372.3(+175 TIG) / 469.4 / 390.0 / 398.1 / 408.2 | USD M | FY2022–26 | US | Bus | FR notices | as above | high | |
| 10 | 5339(c) Low-No available (incl. $1.05B advance) | 1,100.6(+75) / 1,151.7 / 1,104.0 / 1,105.5 / 1,107.5 | USD M | FY2022–26 | US | Bus | FR notices; FR 2026-00643 | https://www.govinfo.gov/content/pkg/FR-2026-01-15/html/2026-00643.htm | high | FY2026 IIJA net $1,029.0M |
| 11 | IIJA Division J advance appropriations by program (each year) | CIG 1,600; SGR 950; Low-No 1,050; 5310 50; ASAP 350; e-ferry 50; rural ferry 200 (=4,250) | USD M | FY2022–26 | US | Transit | FR 2024-11934; FR 2025-17784; Budget Appendix FY2027 | https://www.govinfo.gov/content/pkg/FR-2024-05-31/html/2024-11934.htm | high | FY2023 rural ferry $217.5M per FY2023 notice |
| 12 | Total FTA appropriations incl. advance | 20,514.8 / 21,432.4 / 20,855.9 / 20,937.1 | USD M | FY2022–25 | US | Transit | FR notices | as above | high | |
| 13 | FY2026 enacted: formula limitation; CIG; WMATA; TIG; TA | 14,642.0; 1,700.0; 150.0; 211.4; 7.5 | USD M | FY2026 | US | Transit | P.L. 119-75 (govinfo) | https://www.govinfo.gov/content/pkg/PLAW-119publ75/html/PLAW-119publ75.htm | high | + $4,250M Div. J → ≈$20,961M computed |
| 14 | No FY2026 FR apportionment notice published | latest = FY2025 (15 Sept 2025) | — | as of 7 Nov 2026 | US | Transit | Federal Register API (FTA documents) | https://www.federalregister.gov/api/v1/documents.json?conditions[term]="Apportionments, Allocations, and Program Information"&conditions[agencies][]=federal-transit-administration | high | |
| 15 | House bill MTA totals FY2027–31 | 16,868 / 17,205 / 17,527 / 17,835 / 18,157 (=87,592) | USD M | FY2027–31 | US | Transit | H.R. 8870 §3023 (govinfo ih) + T&I ANS | https://www.govinfo.gov/content/pkg/BILLS-119hr8870ih/html/BILLS-119hr8870ih.htm ; https://transportation.house.gov/uploadedfiles/ans_to_hr_x_build_america_250_act.pdf | high | Program lines sum exactly |
| 16 | House bill 5307 | 7,745.5 / 7,869.9 / 7,996.4 / 8,124.8 / 8,255.3 (=39,991.9) | USD M | FY2027–31 | US | Bus+rail | H.R. 8870 §3023 | as above | high | +10.2% vs FY2026 |
| 17 | House bill 5337 | 4,640 / 4,645 / 4,650 / 4,655 / 4,660 | USD M | FY2027–31 | US | Rail-heavy | H.R. 8870 §3023 | as above | high | RVR eliminated (§3022) |
| 18 | House bill 5339 (bus, facilities, ferries) | 1,695.0 / 1,863.7 / 2,014.9 / 2,149.6 / 2,295.5 | USD M | FY2027–31 | US | Bus | H.R. 8870 §3023–3024 | as above | high | $336M floor; 62/38 split; no Low-No |
| 19 | House bill CIG | 3,000/yr GF, subject to appropriation | USD M | FY2027–31 | US | Rail/BRT | H.R. 8870 §3023(b) | as above | high | |
| 20 | House bill ASAP set-aside in 5307 | 400/yr | USD M | FY2027–31 | US | Rail | H.R. 8870 §3021 | as above | high | |
| 21 | House bill adds SaaS/cloud software to "capital project" | new 5302 subpara. (O) | — | 2026 | US | Software | H.R. 8870 §3002; T&I section-by-section | https://transportation.house.gov/uploadedfiles/build_america_250_act_section_by_section.pdf | high | |
| 22 | H.R. 8870 status | no reported print; no floor vote; Eno 4 Sept 2026 "likely killing chance … this year"; CBO estimate 2 Oct 2026 | — | 2026 | US | All | govinfo (BILLS-119hr8870rh 404); Eno tracker | https://enotrans.org/surface-reauthorization/ | medium | Eno article bodies subscriber-only |
| 23 | Extension to 11 Dec 2026; fraction 72/365; no advance approps continued | P.L. 119-103 Div. C | — | FY2027 | US | All | govinfo PLAW-119publ103 | https://www.govinfo.gov/content/pkg/PLAW-119publ103/html/PLAW-119publ103.htm | high | Enacted 2 Sept 2026 |
| 24 | No further extension through P.L. 119-136 (22 Oct 2026) | none | — | as of 7 Nov 2026 | US | All | govinfo PLAW-119publ104–136 | https://www.govinfo.gov/content/pkg/PLAW-119publ136/html/PLAW-119publ136.htm | high | Titles checked individually |
| 25 | FY2027 request: formula limitation / CIG / TIG / ASAP / WMATA | 14,950 / 1,215 / 0 / 0 / 150 | USD M | FY2027 | US | Transit | Budget of the US Government FY2027, Appendix (DOT) | https://www.govinfo.gov/content/pkg/BUDGET-2027-APP/pdf/BUDGET-2027-APP.pdf (pp. ~911–917) | high | Formula programs not itemized for 2027 |
| 26 | FY2025 actual / FY2026 est. formula obligations by program | UZA 9,853/10,050; SGR 3,846/3,923; 5339(a) 611/623; bus comp. 444/453; 5311 1,182/1,207; 5310 419/427 | USD M | FY2025–26 | US | Transit | Budget Appendix FY2027 | same | high | Obligations incl. carryover |
| 27 | Low-No/Bus awards Jan 2026 (FY2025 + part FY2026) | 2,027.9 total: 1,630.3 Low-No (103 projects) + 397.7 bus (62) | USD M | FY2025–26 | US | Bus | FR 2026-00643 | https://www.govinfo.gov/content/pkg/FR-2026-01-15/html/2026-00643.htm | high | |
| 28 | FY2026 bus competitive awards Mar 2026 | 388.3 (34 projects) | USD M | FY2026 | US | Bus | FR 2026-05152 | https://www.govinfo.gov/content/pkg/FR-2026-03-17/html/2026-05152.htm | high | |
| 29 | Transit SGR backlog (25th C&P, 2018 data) | 101.4 (2018) → 106.2 (2038 sustain); benchmark 20.3/yr vs 13.5/yr spend | USD B | 2018 | US | Bus+rail | FHWA/FTA 25th C&P Executive Summary | https://www.fhwa.dot.gov/policy/25cpr/pdf/CP25_LittleBook.pdf | high | Not the Jan 2025 FTA analysis |
| 30 | Transit SGR backlog (24th C&P, 2016 data) and split | 105 = guideway 23.8 + facilities 11.0 + systems 30.6 + stations 19.9 + vehicles 20.0; 14% of bus / 10% of rail asset value | USD B | 2016 | US | Bus+rail | FHWA/FTA 24th C&P ch. 6 | https://www.fhwa.dot.gov/policy/24cpr/pdf/Chapter6.pdf | high | |
| 31 | FTA capital eligibility: "computer hardware and software"; all preventive maintenance = capital | text | — | FY2022–25 | US | Software | FR 2022-09143; FR 2024-11934 | https://www.govinfo.gov/content/pkg/FR-2024-05-31/html/2024-11934.htm | high | |
| 32 | FTA declined to add SaaS eligibility guidance to C 4220.1G | text | — | Jan 2025 | US | Software | FR 2025-00992 | https://www.govinfo.gov/content/pkg/FR-2025-01-16/html/2025-00992.htm | high | |
| 33 | 49 U.S.C. 5302(4) capital project incl. preventive maintenance and leasing | text | — | 2023 ed. | US | Software | USCODE | https://www.govinfo.gov/content/pkg/USCODE-2023-title49/html/USCODE-2023-title49-subtitleIII-chap53-sec5302.htm | high | |
| 34 | APTA FY27 House-bill shares CIG/SGR/Bus | 3.0 / 4.64 / 1.7 ≈ 32/50/18% | USD B | FY2027 | US | Transit | Mass Transit (APTA scoring) | https://www.masstransitmag.com/management/article/55381563/how-aptas-recommendations-fared-in-house-tis-surface-transportation-reauthorization-legislation | medium | Secondary |
| 35 | House bill total / transit guaranteed | ≈$580B five-year; $87.5B transit (Larsen) | USD B | FY2027–31 | US | All | Mass Transit (T&I approval, 22 May 2026) | https://www.masstransitmag.com/management/article/55381249/house-ti-committee-approves-build-america-250-act-for-surface-transportation-reauthorization | medium | Eno quotes $474B (HTF-only basis) |
| 36 | FY2025 5311 table arithmetic inconsistency | components sum 860.9 vs stated 956.6 | USD M | FY2025 | US | Rural bus | FR 2025-17784 | as above | high | Likely typos; use stated total |

---

## 7. Sources (all read directly in this run unless noted)

- [S1] 49 U.S.C. 5338 — Authorizations (2023 ed.), govinfo: https://www.govinfo.gov/content/pkg/USCODE-2023-title49/html/USCODE-2023-title49-subtitleIII-chap53-sec5338.htm
- [S2] FTA, Notice of Transit Program Changes, Authorized Funding Levels and Implementation of IIJA and FY2022 Apportionments (FR Doc. 2022-09143, 28 Apr 2022): https://www.govinfo.gov/content/pkg/FR-2022-04-28/html/2022-09143.htm
- [S3] FTA, FY2023 Apportionments, Allocations and Program Information (FR Doc. 2023-07761, 14 Apr 2023): https://www.govinfo.gov/content/pkg/FR-2023-04-14/html/2023-07761.htm
- [S4] FTA, FY2024 Apportionments, Allocations, and Program Information (FR Doc. 2024-11934, 31 May 2024): https://www.govinfo.gov/content/pkg/FR-2024-05-31/html/2024-11934.htm
- [S5] FTA, FY2025 Apportionments, Allocations, and Program Information (FR Doc. 2025-17784, 15 Sept 2025): https://www.govinfo.gov/content/pkg/FR-2025-09-15/html/2025-17784.htm
- [S6] P.L. 119-103, Continuing Appropriations and Extensions Act, 2027 (incl. Division C, Surface Transportation Extension Act of 2026), 2 Sept 2026: https://www.govinfo.gov/content/pkg/PLAW-119publ103/html/PLAW-119publ103.htm
- [S7] P.L. 119-75, Consolidated Appropriations Act, 2026 (FTA title): https://www.govinfo.gov/content/pkg/PLAW-119publ75/html/PLAW-119publ75.htm
- [S8] Budget of the U.S. Government, FY2027 — Appendix (Department of Transportation, Federal Transit Administration accounts), govinfo: https://www.govinfo.gov/content/pkg/BUDGET-2027-APP/pdf/BUDGET-2027-APP.pdf (substitute for the blocked FTA FY2027 CJ at transportation.gov)
- [S9] FTA, Announcement of FY2025 Bus and FY2025/2026 Low-No project selections (FR Doc. 2026-00643, 15 Jan 2026): https://www.govinfo.gov/content/pkg/FR-2026-01-15/html/2026-00643.htm ; FY2026 Bus selections (FR Doc. 2026-05152, 17 Mar 2026): https://www.govinfo.gov/content/pkg/FR-2026-03-17/html/2026-05152.htm
- [S10] H.R. 8870, BUILD America 250 Act, introduced text (BILLS-119hr8870ih), govinfo: https://www.govinfo.gov/content/pkg/BILLS-119hr8870ih/html/BILLS-119hr8870ih.htm (reported version BILLS-119hr8870rh returns 404)
- [S11] House T&I Committee, BUILD America 250 Act section-by-section (PDF): https://transportation.house.gov/uploadedfiles/build_america_250_act_section_by_section.pdf
- [S12] House T&I Committee, Amendment in the Nature of a Substitute to H.R. ___ (BUILD America 250 Act), dated 18 May 2026: https://transportation.house.gov/uploadedfiles/ans_to_hr_x_build_america_250_act.pdf
- [S13] Eno Center for Transportation, "Road to Reauthorization" tracker (summary last updated 19 May 2026; article list through 9 Oct 2026): https://enotrans.org/surface-reauthorization/
- [S14] Mass Transit, "House T&I Committee approves BUILD America 250 Act…" (May 2026): https://www.masstransitmag.com/management/article/55381249/house-ti-committee-approves-build-america-250-act-for-surface-transportation-reauthorization ; "How APTA's recommendations fared…": https://www.masstransitmag.com/management/article/55381563/how-aptas-recommendations-fared-in-house-tis-surface-transportation-reauthorization-legislation
- [S15] govinfo Public Laws 119-104 … 119-136 (titles checked; none transportation-related): e.g., https://www.govinfo.gov/content/pkg/PLAW-119publ136/html/PLAW-119publ136.htm
- [S16] US DOT (FHWA/FTA), Status of the Nation's Highways, Bridges, and Transit: Conditions & Performance, 25th Edition (2024; 2018 data) — Executive Summary: https://www.fhwa.dot.gov/policy/25cpr/pdf/CP25_LittleBook.pdf ; index: https://www.fhwa.dot.gov/policy/25cpr/
- [S17] US DOT, C&P Report 24th Edition, Chapter 6 (Infrastructure Conditions; 2016 data): https://www.fhwa.dot.gov/policy/24cpr/pdf/Chapter6.pdf
- [S18] 49 U.S.C. 5302 — Definitions (2023 ed.): https://www.govinfo.gov/content/pkg/USCODE-2023-title49/html/USCODE-2023-title49-subtitleIII-chap53-sec5302.htm
- [S19] FTA, Third Party Contracting Guidance (C 4220.1G) — notice of availability and response to comments (FR Doc. 2025-00992, 16 Jan 2025): https://www.govinfo.gov/content/pkg/FR-2025-01-16/html/2025-00992.htm
- Federal Register API (document index used to locate FTA notices): https://www.federalregister.gov/api/v1/documents.json?conditions[term]=%22Apportionments,%20Allocations,%20and%20Program%20Information%22&conditions[agencies][]=federal-transit-administration
- Wayback availability record for the FTA Jan 2025 backlog PDF (snapshot 2026-03-30; content not retrievable here): https://archive.org/wayback/available?url=transit.dot.gov/sites/fta.dot.gov/files/2025-01/Transit-State-of-Good-Repair-National-Backlog-Analysis_0.pdf

Blocked (not read): DOT IIJA Authorization Table PDF (transportation.gov — replaced by 49 U.S.C. 5338 and the FR notices' five-year tables); FTA FY2027 Budget Estimates CJ (transportation.gov — replaced by the Budget Appendix); AASHTO June 2026 analysis (transportation.org); CRS R48644/R48728 (congress.gov); CBO cost estimate (cbo.gov); FTA FY2026 Tables 1/3/12 (transit.dot.gov); FTA Jan 2025 SGR backlog PDF and SaaS FAQ / C 5010.1E (transit.dot.gov; Wayback reset); APTA.

---

## 8. Gaps / open items
1. Dollar total of FTA's January 2025 SGR National Backlog Analysis (2022$) — PDF unreachable; Wayback snapshot identified (timestamp 20260330232150). Interim: 25th C&P $101.4B (2018).
2. FTA's own SaaS FAQ / C 5010.1E wording on SaaS as capital (preventive maintenance or leased equipment) — unreachable; statutory and circular-notice evidence captured instead.
3. FY2026 program-level *apportioned* amounts (FTA Tables 1/3/13) — estimated here from statute; replace when transit.dot.gov is accessible.
4. CBO score of H.R. 8870 (2 Oct 2026) and the AASHTO June 2026 analysis — not read (hosts blocked); the House bill's authorization numbers were taken directly from the bill/ANS text instead.
5. Exact IIJA Division J per-year ferry amounts for FY2022 (FY2023 notice shows $217.5M rural ferry vs $200M in FY2024–25) — minor.
6. APTA's $119.9B "IIJA baseline" for the −14% comparison cannot be reproduced from statute ($108.15B); treat as APTA's basis.
