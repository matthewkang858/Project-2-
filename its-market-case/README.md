# Public ITS (Roadway/Bus and Railway) market case

Deliverables for the written case: market size and segmentation, drivers and estimates to 2031, risks and barriers, competitive dynamics, investment thesis for a new entrant.

## Deliverables

| File | What it is |
|---|---|
| `deck/Public_ITS_Market_Case.pptx` | Six content slides plus cover: executive summary, market definition and size, growth drivers and outlook, competitive dynamics, risks and barriers, investment thesis. Built from the model export so every number ties to the workbook. |
| `model/Public_ITS_Market_Model.xlsx` | Live-formula model: Inputs (all assumptions with sources), TopDown (third-party estimates and scope reconciliation), Market_2025 (segment x component x geography, two-tier and openness views, bus pool by application, haircut sensitivity), Forecast (2025-2031 with scenario selector, open-pool SAM, growth bridge), BottomUp_NA (NTD fleet x unit economics), Drivers, Competitors, Deals_Comps, Benchmarks (122 contract awards), Risks, Thesis (illustrative buy-and-build bridge, target long-list). |
| `01_synthesis.md` | The sizing logic and storyline in prose, with the research file that holds each source. |
| `00_case_plan.md` | Segmentation framework, model architecture and slide storyline used to organise the work. |
| `research/` | 18 research sweeps, gap-fill notes and `90_verification.md` (30 load-bearing claims re-checked against sources: 25 verified, 3 scope caveats, 2 corrected). Every figure carries its URL. |
| `data/` | Derived tables: FTA NTD 2025 agency tiers, fleets, communication and information capex by mode and year; contract benchmarks; (raw NTD downloads are not committed). |

## Regenerating

```bash
cd model && python3 build_model.py                      # writes the workbook from build_model.py inputs
python3 <xlsx-skill>/scripts/recalc.py Public_ITS_Market_Model.xlsx   # LibreOffice recalculation (0 errors expected)
python3 export_values.py                                # writes deck_data.json from the recalculated workbook
cd ../deck && npm install && NODE_PATH=$PWD/node_modules node build_deck.js   # writes the deck
```

Change `Inputs!scenario` (1 Low, 2 Base, 3 High), the ex-fare haircut or the FX rate in the workbook to flex the numbers; rebuild the deck after re-exporting.

## Headline numbers (base case, USD, ECB 2025 average 1.13 USD/EUR)

- 2025 market, brief scope: ~$28.7bn (bus and tram ITS $4.6bn; urban signalling $6.3bn; mainline and commuter signalling $14.6bn; other rail ITS $3.2bn). Transit-operator core ~$14.1bn; open software-and-services pool $4.2bn. Fare collection ($10-17bn) is adjacent and excluded.
- 2031: ~$39.2bn, 5.3% CAGR (low 3.6%, high 7.0%), nominal USD at constant 2025 FX; open pool $4.2bn to $6.3bn (7.0%).
- Hardware 46% / software 26% / services 28%; Europe 50%, Asia-Pacific 31%, North America 12%, rest of world 7%.
- Deck: cover plus six content slides (executive summary counted as one of the six); drop the cover if the firm counts it.
