# Public ITS (Bus + Rail): synthesis of research into sizing logic and storyline

Prepared 2026-11-07 from the research files in `research/` (numbers below cite the file that holds the source URL).

## 1. Scope used in the model

Public ITS = software, hardware and services bought by public transit agencies and operators for:
- Roadway: fixed-route bus, BRT, trolleybus, paratransit (Berg Insight's "buses and trams" scope is used as the Europe/North America anchor, so tram onboard ITS sits here).
- Railway: metro, light rail, commuter/regional and mainline passenger rail (freight carved out).

Functional domains: (A) operations and fleet management; (B) passenger information; (C) safety, security and surveillance; (D) asset, telematics and condition monitoring; (E) train control and signalling (rail only).
Adjacent and excluded from the core number: fare collection and ticketing (shown as a memo line), roadway traffic management and tolling, rolling stock, civil works.

## 2. 2025 base-year sizing (USD, ECB 2025 average 1.13 USD/EUR)

| Block | Anchor | 2025 value | Confidence |
|---|---|---|---|
| Bus ITS Europe | Berg Insight 10th ed. EUR 2.55bn (fare-inclusive) less 20% ex-fare haircut | USD 2.3bn core (2.9 incl. fare) | High on anchor, medium on haircut (file 17_gap) |
| Bus ITS North America | Berg EUR 1.22bn less 20% | USD 1.1bn core (1.4 incl. fare) | Same |
| Bus ITS rest of world | Berg EU+NA scaled by GMI APTS regional mix (EU+NA = 73.9% of global) | USD 1.2bn core (1.5 incl. fare) | Low (file 17_gap; gap-fill 37 to refine with fleet x intensity) |
| Rail control and signalling, passenger only | UNIFE WRMS 2026 rail control EUR 24.9bn x 74% passenger share (region-weighted) | USD 20.9bn (urban 6.3, mainline/commuter 14.6) | High on anchor, medium on carve-out (file 21_gap) |
| Rail ITS other than signalling (PIS, onboard CCTV/APC, train tracking, condition monitoring, trackside detection) | GMI APTS rail share ex-ticketing + analyst build | USD 3.2bn | Low-medium |
| Core total | | USD 28.7bn (transit-operator core 14.1bn + mainline/commuter signalling 14.6bn) | |
| Memo: fare collection (adjacent) | TechSci / Fortune | USD 10-17bn | n/a |

Headline for the deck: the market is about USD 29bn, but 73% of it is rail signalling, a closed four-player oligopoly (three ex-China). Half of the total is mainline and commuter signalling bought by infrastructure managers; the transit-operator core (bus ITS, urban signalling, other rail ITS) is about USD 14bn and the pool open to an asset-light entrant (software and services in bus and other rail ITS) is USD 4.2bn (North America 0.9, Europe 1.9).

Cross-checks: GMI APTS global USD 6.83bn (all modes, fare-inclusive) vs our bus + rail-other ex-fare USD 7.8bn; NTD "communication and information systems" capex USD 1.90bn (rail 1.50, bus 0.37) vs our US rail CCS + bus core of roughly USD 2.6-3.0bn (NTD is capex only, excludes opex-funded SaaS and maintenance); vendor revenue sum for rail CCS EUR 17bn = ~80% of the UNIFE anchor (file 22_gap).

## 3. Growth to 2031 (base / low / high)

| Block | Base CAGR | Drivers | Evidence |
|---|---|---|---|
| Bus Europe | 5.3% (3.5 / 7.0) | ZEB fleet turnover (60% of EU city-bus registrations zero-emission in 2025), Clean Vehicles Directive 2026-30, UK bus settlement, ITxPT-driven refresh, AI enforcement | Berg 10th ed.; ACEA; files 02, 07, 13 |
| Bus North America | 5.0% (2.5 / 8.0) | 24k buses reach useful-life benchmark 2026-31, CAD/AVL systems of 2005-2012 vintage due, AI bus-lane enforcement (MTA 2,000 buses), APC/TSP whitespace; drag from federal reauthorisation gap | Berg (NA grew 11.5% p.a. 2022-25); NTD; files 04, 06, 25_gap |
| Bus rest of world | 9% (6 / 11) | China smart-bus retrofits, India 41k buses/yr procurement need with bundled telematics, Gulf greenfield networks, LatAm e-bus | GMI APAC 10.1%; files 05, 07 |
| Rail signalling (passenger) | 4.9% blended (3.4 / 6.4); Europe 5.0%, China 3.5%, North America 5.5% | ERTMS mandate (EUR 85-100bn total cost, only 10% of TEN-T equipped), CBTC resignalling of legacy metros (NYC USD 5.4bn 2025-29, London, Paris, Toronto), DB EUR 6.3bn framework, FRMCS from 2027; slippage risk (UK CP7 ETCS cut 35%, DB stretch-out) | UNIFE realised 5.7% p.a.; SCI 4.6%; files 03, 07, 14, 21_gap |
| Rail other ITS | 7% (5 / 9) | Rolling-stock renewal carrying PIS/CCTV, predictive maintenance going fleet-wide (HMAX on all new Hitachi trains from 2027), cyber directives, obstacle detection for GoA4 | files 09, 13 |

Component mix shifts toward software (GMI: software 9.7% CAGR vs hardware 7.7%).
Result (nominal USD at constant 2025 FX): market USD 28.7bn (2025) to USD 39.2bn (2031), 5.3% CAGR (low 3.6%, high 7.0%); open software-and-services pool USD 4.2bn to USD 6.3bn, 7.0% CAGR; two-thirds of the increase sits in signalling.

## 4. Competitive dynamics

- Rail signalling: a four-player oligopoly (three ex-China): Siemens Mobility, Hitachi Rail (incl. Thales GTS, EUR 1.66bn, 2024), Alstom, CRSC (China only) each hold 13-22%; ex-China the big three hold about two-thirds. Backlog cover 3.4-5.4 years; 25-30 year service tails; SIL-4 certification. Alstom profit warning (Nov 2026) is the first plausible carve-out source.
- Bus ITS: Modaxo/Constellation (Trapeze, Vontas, Routeward ex-Conduent USD 164m 2026, TripSpark, TransLoc; 3,500+ customers, never sells), Hitachi Rail (Clever Devices, >USD 220m revenue, 8 of top-10 NA agencies, July 2026), INIT (EUR 330m, 10% EBIT), Cubic (distressed, ~USD 2.1bn debt), IVU (EUR 150m, 52% recurring), Equans, GMV, Avail, Luminator, Hanover; SaaS challengers Swiftly (200+ agencies), Optibus (USD 1.3bn valuation 2022), Via (NYSE, USD 434m revenue), Spare, Hayden AI (AI enforcement, 2,500 buses).
- Dynamics: strategic consolidation at 0.4-2x revenue for integrators (Conduent transit 0.44x; Thales GTS 1.0x revenue and 13.7x EBIT; Clever Devices USD 302m plus USD 45m debt repaid = ~1.4-1.6x projected 2026 revenue per Hitachi's Q1 FY2026 results; Alstom Signaling NA ~2.1x; Iteris 1.8x) vs 5-6x LTM revenue for SaaS (Via); Cubic was taken private at 15.7x NTM EBITDA (USD 70 offer; closed at USD 75, ~USD 3.0bn EV) and is now distressed; hardware-to-software unbundling (ITxPT, cloud CAD/AVL overlays); incumbents moving to 10-20 year service contracts.

Whitespace measured (research/33_gap): 616 of 977 US bus agencies (63%, 21% of full-size buses) publish no real-time feed; in the 50-249-bus tier Avail is the leading publisher (32 of 149 agencies) and 36 agencies have no feed; Swiftly is measurably an overlay on legacy CAD/AVL at 26+ agencies.

## 5. Risks and barriers to entry

Procurement cycles (2-4 years award-to-live; LA Metro 2016-2028), incumbency and 15-25 year system lives, Buy America/BABA for hardware, SIL-4 and ERA/FRA certification in rail, funding risk (IIJA advance appropriations lapsed; CR implies -20% transit; ERTMS "significantly behind schedule"), cybersecurity compliance (TSA rule USD 1.26bn/10 years on passenger rail), agency capacity, tariffs, supplier failure (Proterra), leverage (Cubic), SaaS eligibility for 80/20 capital grants.

## 6. Investment thesis for a new entrant

Recommendation: buy-and-build in North America. Acquire a founder- or employee-owned mid-market CAD/AVL or scheduling vendor (Avail, ETA, Passio/Ecolane, GIRO, Hanover, Luminator; revenues to confirm) at 1-2.5x revenue, re-platform to cloud, add enforcement and zero-emission energy modules, bolt on APC/PIS/enforcement specialists at 1-2x revenue, and sell into the 195 agencies with 50-999 buses; exit to a strategic (Hitachi, Siemens, Modaxo, Via). The exit multiple is the thesis: the Clever Devices precedent (~1.6x revenue) returns only ~1.2x gross MOIC on the illustrative bridge, whereas an IVU-like software re-rating (12x EBITDA, ~2.6x revenue) returns ~2.1x; the recurring, software-led mix is therefore the central thing to believe and to diligence (model Thesis sheet). Why North America: dated refresh wave (24,100 buses past useful life by 2031, 2004-12 CAD/AVL cohort), open mid-tier, highest per-vehicle spend, one procurement code; Europe second. Avoid leveraged hardware integrators and rail signalling cores; SaaS-wedge build (5-6x, loss-making) and carve-outs (Alstom digital, Cubic CTS) are the alternatives.
