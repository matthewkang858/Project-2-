# Public ITS (Roadway/Bus and Railway) market case

Deliverables for the written case: market size and segmentation, drivers and estimates to 2031, risks and barriers, competitive dynamics, investment thesis for a new entrant.

## Deliverables

| File | What it is |
|---|---|
| `deck/Public_ITS_Market_Case.pptx` | Cover plus six content slides in house format (breadcrumb tracker, two-tone action titles, one exhibit per slide): executive summary, market size funnel and segment table, growth to 2031 with drivers, competitive grid, risks and barriers, investment thesis. The six slides carry 37 numbers, all read from `model/deck_data.json` at build time and none typed into the builder. Slides 5 (competitive landscape) and 6 (risks and barriers) carry no numbers and make their points in words. |
| `deck/Public_ITS_Market_Case_Appendix.pptx` | Supporting slides kept out of the six-slide limit: A1 segmentation framework, A2 market build (one published anchor and one or two adjustments per segment), A3 growth scenarios (2025-31 bridge and low / base / high CAGRs by segment), A4 exit multiples and returns (EV / revenue benchmarks and the illustrative value bridge), A5 incumbency and entry window (decision points on incumbent-held systems, US fleet by agency size). |
| `model/Public_ITS_Market_Model.xlsx` | Live-formula model, four sheets: README (how to read it, calculation chain, slide map, sources), Market (2025 market size and funnel), Growth (2025-2031E, low / base / high side by side), Returns (illustrative buy-and-build value bridge and exit benchmarks). 47 inputs, each with its source and confidence (HIGH / MID / LOW); 160 formulas; every slide number traces to one cell, at most one sheet away from its inputs. Each sheet ends with integrity checks that must all equal 0. |
| `model/claims_register.md` | Every quantity word and factual claim on the slides (C01-C57), the figure and source behind it, and the build guard that checks it; followed by likely questions and answers on the simplified model. |
| `model/build_model.py`, `model/export_values.py`, `deck/build_deck_v3.js`, `deck/apply_theme.js`, `deck/fix_paragraphs.py` | Build scripts: workbook, model export, both decks, the theme palette writer the deck builder calls, and a post-processing step for the decks that fixes paragraph properties and sets document properties to the author (see Regenerating). |
| `summary/Public_ITS_Research_Summary.docx` | Word summary of all research conducted for the case, with sources, confidence and the numbers carried into the model and deck. Built from `summary/content.json` by `summary/build_summary.js`. |
| `01_synthesis.md` | The sizing logic and storyline in prose, with the research file that holds each source. |
| `00_case_plan.md` | Segmentation framework, model architecture and slide storyline used to organise the work (the original working plan; the as-built model is the four-sheet workbook above). |
| `research/` | 18 research sweeps, 12 gap-fill notes (31-37 plus 17/21/22/25/26) and `90_verification.md` (30 load-bearing claims re-checked against sources: 25 verified, 3 scope caveats, 2 corrected; plus post-verification updates on the Clever Devices price and the MTA ACE contract). Every figure carries its URL. |
| `data/` | Derived tables: FTA NTD 2025 agency tiers, fleets, communication and information capex by mode and year; 228 contract-award benchmarks; GTFS-Realtime vendor census (agency-level, by tier, feed migrations); non-US bus fleets by country; rail resignalling pipeline (raw NTD and MobilityData downloads are not committed; the download and tiering scripts are in `model/scripts/`). |

## Regenerating

Run from the `its-market-case` folder, in this order:

```bash
cd model && python3 build_model.py                       # 1. writes Public_ITS_Market_Model.xlsx
python3 <xlsx-skill>/scripts/recalc.py Public_ITS_Market_Model.xlsx 90   # 2. LibreOffice recalculation (expect "total_errors": 0)
python3 export_values.py                                 # 3. writes deck_data.json from the recalculated workbook
cd ../deck && npm install && NODE_PATH=$PWD/node_modules node build_deck_v3.js   # 4. reads ../model/deck_data.json; writes main deck and appendix
python3 fix_paragraphs.py Public_ITS_Market_Case.pptx Public_ITS_Market_Case_Appendix.pptx   # 5-6. one paragraph-property block per paragraph (bullet fix); author in document properties
```

- `export_values.py` must run after the recalculation: it reads cached values, and it refuses to write `deck_data.json` if a formula has no value or returns an error, a key is missing or duplicated, or any check is not 0.
- `build_deck_v3.js` checks the slide claims guards (`model/claims_register.md`) before it writes anything, and stops with the failing claim named if the model no longer supports a slide's wording. `DECK_DATA=<file>` and `DECK_OUT=<folder>` point it at another export or output folder, for example to test a guard on a copy.
- `build_deck_v3.js` uses `deck/apply_theme.js` (a local copy, no external path) to write the palette into the theme part after saving.
- Word summary: `cd summary && node build_summary.js` (needs the `docx` npm package), then `soffice --headless --convert-to pdf Public_ITS_Research_Summary.docx` for the PDF.

## How to flex the model

Change any blue input on the Market, Growth or Returns sheet, then recalculate, re-export and rebuild the decks (steps 2-6 above).
- Low, base and high CAGRs sit side by side for each segment on Growth (columns L-N), with the 2031E low and high values in columns O-P. Every case recalculates at once, and there is no scenario selector.
- Each input row names its source and confidence, and column "On slide" shows where the number appears.
- If a change makes a slide's wording untrue (for example, signalling moves out of "nearly three-quarters" of the market), the deck build stops on that claim. Update the wording in `deck/build_deck_v3.js` and `model/claims_register.md` together.

## Headline numbers (base case, USD, ECB 2025 average 1.13 USD/EUR)

From `model/deck_data.json`:
- 2025 market, brief scope: $28.6B (~$29B), excluding fare collection. Mainline and commuter signalling $14.6B; urban signalling $6.2B; bus and tram ITS $4.6B; other rail ITS $3.2B. Signalling is nearly three-quarters of the market (72.8%) and mainline signalling about half (50.9%).
- Funnel: transit-operator core $14.0B > contestable pool $7.8B > open software-and-services pool $4.2B (~15% of scope), of which North American bus software and services $0.6B.
- 2031: $39.3B, 5.4% CAGR (low $35.7B at 3.7%, high $43.2B at 7.1%), nominal USD at constant 2025 FX. By segment: bus and tram ITS 6.3%, rail signalling 5.0%, other rail ITS 7.0%. Signalling is two-thirds of the 2025-31 increase of $10.7B. The open pool grows from $4.2B to $6.3B (7.0%), faster than the market.
- Illustrative returns (5-year hold, entry at 2.0x revenue): exit at the Clever Devices precedent (1.58x revenue) gives 1.2x gross MOIC; exit at IVU's trading multiple (2.60x revenue) gives 2.0x. Break-even exit is 1.32x revenue; entering at the Clever multiple instead gives 1.4x / 2.4x.
- Deck: cover plus six content slides (executive summary counted as one of the six); the appendix is a separate file. Titles use Arial Narrow (rendered with the metric-compatible Liberation Sans Narrow in QA).

## What changed in the simplified model

The workbook went from 12 sheets (about 122 inputs, 925 formulas, up to four hops from a slide number to its input) to 4 sheets (README, Market, Growth, Returns; 47 inputs, 160 formulas, one hop). The main deck now carries 37 numbers, none typed into the deck builder, against 209 before (90 of them typed). Headline changes:

| Headline | Previous model | New model | Why it moved |
|---|---|---|---|
| 2025 market | 28.68 ($28.7B) | 28.61 ($28.6B; executive summary still ~$29B) | Passenger share 74% and urban share 30% taken from the research/21_gap world matrix, replacing regional blends of 74.23% and 30.11% |
| Urban signalling | 6.29 ($6.3B) | 6.25 ($6.2B) | World-level urban share |
| Mainline and commuter signalling | 14.60 | 14.57 ($14.6B) | Same |
| Transit-operator core | 14.08 ($14.1B) | 14.04 ($14.0B) | Urban signalling |
| Open pool: North America (slide 7) | 0.88 (bus + rail; $0.9B) | 0.59 (bus only; $0.6B) | Redefined to the thesis market; drops the analyst 17% North American share of other rail ITS |
| Open pool: Europe | 1.93 ($1.9B) | Not computed | The six other-rail regional shares are cut |
| 2031 base | 39.16 ($39.2B) | 39.31 ($39.3B; ~$39B) | One signalling rate of 5.0% replaces six regional rates that blended to 4.85% |
| Market CAGR 2025-31 | 5.33% (5.3%) | 5.44% (5.4%; ~5%) | Same, plus the slightly lower 2025 base |
| Low / high 2031 | 35.54 (3.6%) / 43.01 (7.0%) | 35.68 (3.7%) / 43.17 (7.1%) | Signalling low 3.5% and high 6.5% (was a blend −/+ 1.5pp) |
| Segment CAGRs | bus 6.3%, urban 4.7%, mainline 4.9%, other rail 7.0% | bus 6.3%, signalling 5.0%, other rail 7.0% | The urban/mainline split was computed only in the deck script; signalling is now forecast as one block |
| Increase 2025-31 / signalling share | 10.49 / 66% | 10.70 / 66% | "Two-thirds" holds |
| Exit B EV / revenue | 2.64x (12x EBITDA × 22% margin) | 2.60x (IVU observed) | One sourced input replaces two assumptions |
| Exit A EV / revenue | 1.60x | 1.58x (prints 1.6x) | Observed (302 + 45) / 220 rather than a rounded figure |
| Gross MOIC A / B | 1.23x / 2.08x (1.2x / 2.1x) | 1.21x / 2.04x (1.2x / 2.0x) | Exit B at IVU's multiple; exit A at 1.58x |
| New memo rows | n/a | Break-even exit 1.32x revenue; entry at the Clever multiple gives 1.45x / 2.43x | Answers "why pay more than Hitachi did?" |

Unchanged: bus and tram ITS (4.61), other rail ITS (3.18), contestable pool (7.79), open pool (4.20 in 2025, 6.30 in 2031, 6.99% a year), and the signalling and mainline shares of the market (72.8%, 50.9%).

### Removed from the model and where it now lives

| Removed | Now lives in |
|---|---|
| TopDown sheet: third-party estimates and a reconciliation that linked back into Market_2025 | README sheet, section 4 (Sources); appendix A2; research/01, 17_gap |
| Market_2025 detail: 22 region × segment rows, hidden SUMIF tags, "Investor view 1-3" blocks, application mix, haircut sensitivity, signalling component split, region table | Deleted. The regional derivation behind the 74% passenger and 30% urban shares is in research/21_gap (world matrix) |
| Forecast sheet: 16 rows, CHOOSE scenario selector, geography and component forecasts, SUMPRODUCT scenario rows | Replaced by the Growth sheet: 5 segment rows with low, base and high side by side |
| BottomUp_NA: fleet × unit economics, NTD capex floor, rail check, replacement wave, agency tiers | research/16, 31_gap, 35_gap; data/ntd_*.csv. The deck reads the agency tiers for A5 from data/ntd_2025_bus_agency_tiers.csv |
| Drivers sheet and the FTA funding series | Slide 4 text; research/06, 07, 13, 14, 25_gap, 36_gap |
| Competitors sheet (indicative vendor shares) | research/22_gap, 32_gap; data/vendor_share_berg_pools_2025.csv |
| Deals_Comps sheet | Five benchmarks on Returns rows 39-43; the rest in data/deal_multiples_verified.csv and research/10, 26_gap, 34_gap |
| Benchmarks sheet (228 contract awards) | data/contract_benchmarks.csv; data/its_award_dataset_2018_2026.csv; research/35_gap |
| Risks sheet | Slide 6 text; research/11 |
| Thesis: exit EBITDA margin (22%), exit EV/EBITDA (12x), IRR rows, target long-list | Exit B is now IVU's observed 2.60x revenue; long-list in research/18 |
| Unused or duplicate inputs (about 75): base year, duplicate Berg CAGRs, the SCI EUR 20B "low-case anchor" that no formula used, fare-collection memo, NTD and unit-cost inputs, ZEB and cohort counts, GMI regional sub-shares, 24 regional signalling parameters, 6 other-rail regional shares, bus software share | The research files above |
