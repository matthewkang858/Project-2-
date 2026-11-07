# Public ITS (Bus + Rail) written case: working plan

Deliverable: 5-6 slides (incl. Executive Summary) + Excel model, due Monday 9 AM ET.
Scope: software, hardware and services sold to public transit agencies/operators in Roadway (bus) and Railway segments.

## 1. Segmentation framework (proposed)

Three axes, plus geography and customer tier:

| Axis | Buckets |
|---|---|
| Mode | Roadway (fixed-route bus, BRT, paratransit/demand-response) ; Railway (urban rail: metro/LRT/streetcar ; mainline passenger: commuter/regional/intercity) |
| Functional domain | (A) Operations & fleet management (CAD/AVL, scheduling, dispatch, yard) ; (B) Passenger information (real-time feeds, onboard & wayside displays, apps) ; (C) Safety, security & surveillance (onboard/wayside video, AI incident detection, collision avoidance, enforcement) ; (D) Asset, telematics & condition monitoring (vehicle health, predictive maintenance, trackside detectors) ; (E) Train control & signaling (CBTC, ETCS/ERTMS, PTC, interlockings, ATO; rail only) |
| Component layer | Hardware (on-vehicle: AVL/MDT units, cameras, APC sensors, displays, routers ; wayside/trackside: stop displays, detectors, signaling equipment) ; Software (licenses/SaaS for A-E) ; Services (integration/installation, maintenance & support, managed/hosted services, consulting) |
| Geography | North America ; Europe ; Asia-Pacific ; Rest of World (LatAm, MEA) |
| Customer tier | Tier 1 (>1,000 vehicles / major rail operators) ; Tier 2 (250-1,000) ; Tier 3 (<250, long tail) ; contracted operators (Keolis, Transdev, Arriva, National Express, First) |

Adjacent but out of scope (flag only): fare collection/ticketing & AFC, roadway traffic management/tolling, rolling stock, infrastructure civil works, consumer MaaS apps.

## 2. Model architecture (Excel)

1. README: structure, color legend (blue inputs / black formulas / green links), sources.
2. Inputs: fleet & network counts by region x mode (buses, metro/LRT vehicles, commuter/mainline cars, signalled route-km); penetration rates by domain; replacement cycles; unit economics (hardware $/vehicle, software $/vehicle/yr, services % of hardware+software); recurring vs one-off split.
3. Top-down triangulation: third-party estimates with scope definitions and scope adjustments -> scope-matched 2025 range.
4. Bottom-up build: installed base x penetration x unit price / replacement cycle + recurring software/services, by mode x domain x component x region -> 2025 market.
5. Forecast 2025-2031: driver-based (fleet growth, penetration gains, software mix shift, mandates e.g. ETCS/CBTC resignalling waves, ZEB fleet turnover, funding cycle), base / upside / downside.
6. Competitive landscape: vendor table (revenue, segments, ownership, geography, est. share).
7. Contract benchmarks: award table with derived $/vehicle and $/km.
8. Chart data feeding the deck.

## 3. Slide storyline (6 slides)

1. Executive summary: market size & growth headline, segment mix, what drives it, who wins, where a new entrant should play, key risks.
2. Market definition, segmentation & 2025 size: framework diagram + size by mode x component x region, with top-down vs bottom-up triangulation.
3. Growth drivers & outlook to 2031: driver tree with quantified impact, forecast chart with scenarios, segment-level CAGRs.
4. Competitive dynamics & key players: landscape map (scale vs breadth), consolidation/M&A, business-model shift (hardware -> SaaS), share concentration by sub-segment.
5. Risks & barriers to entry: matrix (likelihood x impact) with mitigants; procurement, Buy America, cybersecurity, funding cliff, incumbency, certification.
6. Investment thesis for a new entrant: where to play / how to win, entry archetypes (build, buy, roll-up, adjacency), what we would need to believe, key diligence questions.

## 4. Research tracks (running)

- Track A (bus/top-down): top-down ITS reports, bus sub-segments, US fleet base, bus vendors, contract benchmarks, NTD data pull.
- Track B (rail/intl): rail sub-segments, global fleet base, international drivers, rail vendors, operator capital plans, industry studies.
- Track C (cross-cutting): US funding, deals & valuations, risks/barriers, tech trends, business models & pricing, investment theses.
- Then: claim verification pass on load-bearing numbers; synthesis; model; deck.
