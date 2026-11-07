"""Build the Public ITS market model (Excel, live formulas) with openpyxl.
Run: python3 build_model.py  -> writes Public_ITS_Market_Model.xlsx next to this script.
All hard-coded inputs live on the Inputs sheet (blue) with a source note; every other sheet is formula-driven.
"""
import csv, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), 'data')
OUT = os.path.join(HERE, 'Public_ITS_Market_Model.xlsx')

F_BASE = 'Arial'
BLUE = Font(name=F_BASE, size=10, color='0000FF')
BLACK = Font(name=F_BASE, size=10, color='000000')
GREEN = Font(name=F_BASE, size=10, color='008000')
BOLD = Font(name=F_BASE, size=10, bold=True)
TITLE = Font(name=F_BASE, size=14, bold=True, color='1B2A41')
H2 = Font(name=F_BASE, size=11, bold=True, color='1B2A41')
HDR = Font(name=F_BASE, size=10, bold=True, color='FFFFFF')
NOTE = Font(name=F_BASE, size=9, italic=True, color='4F6D7A')
HDR_FILL = PatternFill('solid', fgColor='1B2A41')
SUB_FILL = PatternFill('solid', fgColor='EEF2F5')
KEY_FILL = PatternFill('solid', fgColor='FFFF00')
THIN = Side(style='thin', color='C7D3DA')
BOX = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')

FMT_BN = '#,##0.00;(#,##0.00);-'
FMT_M = '#,##0;(#,##0);-'
FMT_PCT = '0.0%;(0.0%);-'
FMT_X = '0.0x'
FMT_INT = '#,##0'

wb = Workbook()
R = {}  # named input registry -> absolute reference

def setw(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

def hdr(ws, row, labels, col=1):
    for j, t in enumerate(labels):
        c = ws.cell(row=row, column=col + j, value=t)
        c.font = HDR; c.fill = HDR_FILL; c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = BOX

def title(ws, text, sub=None):
    ws['A1'] = text; ws['A1'].font = TITLE
    if sub:
        ws['A2'] = sub; ws['A2'].font = NOTE

# ----------------------------------------------------------------------------
# README
# ----------------------------------------------------------------------------
ws = wb.active; ws.title = 'README'
title(ws, 'Public Intelligent Transportation Systems (ITS) market model: Roadway (bus) and Railway', 'Written case support model. Base year 2025, forecast to 2031. Currency USD unless stated. Prepared November 2026.')
readme = [
    ('Purpose', 'Top-down sizing of the Public ITS market (software, hardware, services sold to public transit agencies/operators), segmentation, 2025-2031 forecast with scenarios, bottom-up cross-check on North America, competitive and deal reference tables, risk register.'),
    ('Scope', 'Roadway = bus, BRT, trolleybus, paratransit (Berg Insight anchor covers buses and trams, so tram onboard ITS sits in Roadway). Railway = metro, light rail, commuter/regional and mainline passenger rail; freight carved out. Functional domains: operations and fleet management; passenger information; safety, security and surveillance; asset, telematics and condition monitoring; train control and signalling (rail). Fare collection/ticketing, roadway traffic management/tolling, rolling stock and civils are adjacent and excluded (fare shown as a memo).'),
    ('Sheets', 'Inputs (all assumptions, blue, with sources) -> TopDown (third-party estimates and scope reconciliation) -> Market_2025 (segment x component x geography) -> Forecast (2025-2031, scenario selector on Inputs) -> BottomUp_NA (NTD fleet x unit economics cross-check) -> Drivers -> Competitors -> Deals_Comps -> Benchmarks (contract awards) -> Risks.'),
    ('Colour legend', 'Blue text = hard-coded input or scenario lever; black = formula; green = link to another sheet; yellow fill = key levers (scenario selector, ex-fare haircut, FX).'),
    ('How to use', 'Change Inputs!scenario (1 = Low, 2 = Base, 3 = High) to flex the Forecast. Every market number traces to an Inputs cell; the source column on Inputs names the document and the research note (research/NN_*.md) that holds the URL.'),
    ('Key sources', 'Berg Insight, Public Transport ITS in Europe and North America, 10th ed. (Mar 2026); Global Market Insights, Advanced Public Transportation System market (Aug 2026); UNIFE World Rail Market Study 2026 (Bain) abstract; SCI Verkehr CCS market study (Mar 2026); FTA National Transit Database report year 2025 (data.transportation.gov, Oct 2026); UITP Global Metro Figures 2024; European Commission Third ERTMS Work Plan (Feb 2026); company reports (INIT, IVU, Via, Alstom, Siemens, Hitachi, Wabtec, CRSC); agency board documents for contract awards.'),
    ('Caveats', 'Berg values are fare-inclusive and are haircut by an explicit assumption; the passenger/freight and urban/mainline carve-outs of rail signalling are analyst proxies built from traffic and network data (research/21_gap_*.md); rest-of-world bus ITS is scaled from GMI regional mix (low confidence). Derived figures are labelled DERIVED on Inputs.'),
]
r = 4
for k, v in readme:
    ws.cell(row=r, column=1, value=k).font = BOLD
    c = ws.cell(row=r, column=2, value=v); c.font = BLACK; c.alignment = WRAP
    ws.row_dimensions[r].height = 15 * max(1, len(v) // 110 + 1)
    r += 1
setw(ws, [18, 140])

# ----------------------------------------------------------------------------
# INPUTS
# ----------------------------------------------------------------------------
wi = wb.create_sheet('Inputs')
title(wi, 'Inputs and assumptions', 'Blue = hard-coded input. Yellow = key lever. Each row names its source; research/NN_*.md files hold the URLs.')
setw(wi, [46, 14, 14, 110])
hdr(wi, 4, ['Input', 'Value', 'Unit', 'Source / note'])
row = [5]

def section(text):
    c = wi.cell(row=row[0], column=1, value=text); c.font = H2
    for j in range(1, 5):
        wi.cell(row=row[0], column=j).fill = SUB_FILL
    row[0] += 1

def inp(key, label, value, unit, source, fmt=None, key_lever=False, derived=False):
    r0 = row[0]
    wi.cell(row=r0, column=1, value=label).font = BLACK
    c = wi.cell(row=r0, column=2, value=value)
    c.font = BLACK if derived else BLUE
    if fmt: c.number_format = fmt
    if key_lever: c.fill = KEY_FILL
    wi.cell(row=r0, column=3, value=unit).font = BLACK
    s = wi.cell(row=r0, column=4, value=source); s.font = NOTE; s.alignment = WRAP
    R[key] = "Inputs!$B$%d" % r0
    row[0] += 1
    return R[key]

section('General')
inp('fx', 'USD per EUR (2025 average)', 1.13, 'USD/EUR', 'ECB annual average reference rate 2025 (research/21_gap, section Method). 2024: 1.0824.', '0.0000', key_lever=True)
inp('scenario', 'Scenario selector (1 = Low, 2 = Base, 3 = High)', 2, 'index', 'Drives the Forecast sheet CAGRs via CHOOSE().', '0', key_lever=True)
inp('base_year', 'Base year', 2025, 'year', 'Latest full year with Berg, GMI, UNIFE and NTD data.', '0')
inp('haircut', 'Ex-fare haircut applied to Berg bus/tram values', 0.20, '% of value', 'Berg definition names automated fare collection and journey planners inside public transport ITS; no application split published. Haircut 15-25% bracketed by GMI electronic-payment share (14.7%) and ticketing application share (24.2%). research/17_gap section 2.', FMT_PCT, key_lever=True)

section('Roadway (bus and tram) anchor: Berg Insight 10th edition, March 2026 (fare-inclusive, EUR bn, 2025)')
inp('berg_eu', 'Europe public transport ITS for buses and trams, 2025', 2.55, 'EUR bn', 'Berg Insight summary PDF p.2: EUR 2.55bn (2025) to EUR 3.30bn (2030), 5.3% CAGR; on-board computer penetration 90.3% to 93.9%. research/01, 17_gap.', FMT_BN)
inp('berg_eu_cagr', 'Europe CAGR 2025-2030 (Berg)', 0.053, '%', 'Same source.', FMT_PCT)
inp('berg_na', 'North America public transport ITS for buses and trams, 2025', 1.22, 'EUR bn', 'Berg summary p.2: EUR 1.22bn (2025) to EUR 1.56bn (2030), 5.0% CAGR; penetration 91.9% to 94.1%. Realised NA growth 2022-25 was 11.5% p.a. (EUR 0.88bn to 1.22bn). research/17_gap table 3.1.', FMT_BN)
inp('berg_na_cagr', 'North America CAGR 2025-2030 (Berg)', 0.050, '%', 'Same source.', FMT_PCT)
inp('gmi_sh_na', 'GMI APTS regional share: North America', 0.443, '% of global', 'Global Market Insights APTS report (base 2025, USD 6,830m): NA 44.3%, Europe 29.6%, APAC 17.2%, LatAm 5.0%, MEA 3.9%. research/17_gap section 4.', FMT_PCT)
inp('gmi_sh_eu', 'GMI APTS regional share: Europe', 0.296, '% of global', 'Same.', FMT_PCT)
inp('gmi_sh_apac', 'GMI APTS regional share: Asia-Pacific', 0.172, '% of global', 'Same.', FMT_PCT)
inp('gmi_sh_latam', 'GMI APTS regional share: Latin America', 0.050, '% of global', 'Same.', FMT_PCT)
inp('gmi_sh_mea', 'GMI APTS regional share: Middle East and Africa', 0.039, '% of global', 'Same.', FMT_PCT)
inp('row_scale', 'DERIVED: rest-of-world bus ITS as multiple of Berg EU+NA', '=(%s+%s+%s)/(%s+%s)' % (R['gmi_sh_apac'], R['gmi_sh_latam'], R['gmi_sh_mea'], R['gmi_sh_na'], R['gmi_sh_eu']), 'x', 'Scales Berg EU+NA to the rest of the world using GMI regional mix (26.1% / 73.9%). Low confidence: GMI mix is all-mode APTS. Cross-check: ~1.3-1.6m non-US/EU transit buses (China 630k) at a much lower per-bus intensity (research/05, 37_gap).', '0.000', derived=True)
inp('row_apac_share', 'Share of rest-of-world bus ITS in Asia-Pacific', '=%s/(%s+%s+%s)' % (R['gmi_sh_apac'], R['gmi_sh_apac'], R['gmi_sh_latam'], R['gmi_sh_mea']), '%', 'DERIVED from GMI regional shares (APAC / (APAC + LatAm + MEA)).', FMT_PCT, derived=True)
inp('bus_hw', 'Bus ITS component mix 2025: hardware', 0.468, '% of value', 'GMI APTS component split 2025: hardware 46.8%, software 33.0%, services 20.1%. research/17_gap 4.1.', FMT_PCT)
inp('bus_sw', 'Bus ITS component mix 2025: software', 0.330, '% of value', 'Same.', FMT_PCT)
inp('bus_sw_2031', 'Bus ITS software share 2031 (mix shift)', 0.352, '% of value', 'GMI implied 2031 mix 44.6 / 35.2 / 20.1 (software CAGR 9.7% vs hardware 7.7%). Services held at 20.1%.', FMT_PCT)
inp('bus_cagr_eu_l', 'Bus Europe CAGR 2025-31: Low', 0.035, '%', 'Low = Berg Europe 2021-22 realised growth plus ZEB slowdown; Base = Berg 10th ed. 5.3%; High = Berg 9th ed. 6.3% plus enforcement/AI upside. research/01, 02, 13.', FMT_PCT)
inp('bus_cagr_eu_b', 'Bus Europe CAGR 2025-31: Base', 0.053, '%', 'Berg 10th edition.', FMT_PCT)
inp('bus_cagr_eu_h', 'Bus Europe CAGR 2025-31: High', 0.070, '%', 'See Low.', FMT_PCT)
inp('bus_cagr_na_l', 'Bus North America CAGR 2025-31: Low', 0.025, '%', 'Low = federal reauthorisation gap (CR without IIJA advance appropriations = -20% transit funding), fiscal-cliff agencies deferring refresh; Base = Berg 5.0%; High = 8.0% (Berg 9th ed. 8.8%; realised 11.5% 2022-25). research/06, 25_gap.', FMT_PCT)
inp('bus_cagr_na_b', 'Bus North America CAGR 2025-31: Base', 0.050, '%', 'Berg 10th edition.', FMT_PCT)
inp('bus_cagr_na_h', 'Bus North America CAGR 2025-31: High', 0.080, '%', 'See Low.', FMT_PCT)
inp('bus_cagr_row_l', 'Bus rest of world CAGR 2025-31: Low', 0.060, '%', 'GMI APAC APTS CAGR 10.1%, LatAm/MEA ~8%; China bus fleet shrinking 2-4% p.a. but retrofitting smart-bus systems; India procurement need 41k buses/yr. research/05, 07, 17_gap.', FMT_PCT)
inp('bus_cagr_row_b', 'Bus rest of world CAGR 2025-31: Base', 0.090, '%', 'Blend of GMI APAC/LatAm/MEA.', FMT_PCT)
inp('bus_cagr_row_h', 'Bus rest of world CAGR 2025-31: High', 0.110, '%', 'See Low.', FMT_PCT)

section('Railway: control, command and signalling (CCS) anchor: UNIFE World Rail Market Study 2026 (Bain)')
inp('unife_cc', 'World rail control market, average 2023-2025 (treated as 2025)', 24.9, 'EUR bn', 'UNIFE WRMS 2026 abstract: rail control EUR 24.9bn p.a. (2023-25), 11.3% of EUR 220.6bn total; EUR 22.3bn in WRMS 2024 (2021-23). Includes freight, trackside and onboard; excludes maintenance services (UNIFE books those in services). SCI Verkehr sizes CCS at ~EUR 20bn (2025) incl. after-sales = Low case. research/21_gap A1-A3.', FMT_BN)
inp('unife_cc_low', 'Low-case CCS anchor (SCI Verkehr 2025)', 20.0, 'EUR bn', 'SCI Verkehr CCS press release, March 2026. research/21_gap A2.', FMT_BN)
inp('ccs_cagr_delta_low', 'CCS CAGR scenario delta: Low (vs base)', -0.015, 'pp', 'Low reflects ERTMS slippage (EC: significantly behind schedule), UK CP7 ETCS cut (GBP 1.54bn to 0.99bn), DB strategy reset; High reflects FRMCS wave from 2027, CBTC GoA4 conversions. UNIFE realised rail-control growth 5.7% p.a. (2021-23 to 2023-25); SCI 4.6%. research/21_gap takeaway 8.', FMT_PCT)
inp('ccs_cagr_delta_high', 'CCS CAGR scenario delta: High (vs base)', 0.015, 'pp', 'See above.', FMT_PCT)
inp('ccs_hw', 'Rail CCS component mix: hardware', 0.46, '% of value', 'GMI railway signalling: solutions 76% / services 24% (services growing >10%); Alstom Services 24% of sales; CBTC awards carry 25-year maintenance tails ~10% of capex. HW/SW split inside solutions is an analyst assumption (urban CBTC software-heavier). research/21_gap section E.', FMT_PCT)
inp('ccs_sw', 'Rail CCS component mix: software', 0.24, '% of value', 'Same.', FMT_PCT)
rail_regions = ['Europe', 'China', 'APAC ex-China', 'North America', 'CIS/Eurasia', 'Rest of world']
ccs_share = [0.46, 0.21, 0.11, 0.13, 0.04, 0.05]
pax_share = [0.83, 0.80, 0.77, 0.46, 0.40, 0.64]
urban_share = [0.16, 0.45, 0.29, 0.57, 0.50, 0.63]
ccs_cagr_base = [0.050, 0.035, 0.065, 0.055, 0.020, 0.055]
ccs_share_src = 'SCI 2026: Europe almost half of ~EUR 20bn; China >65% of Asia; SCI world rail market regional weights (NA 13%); GMI NA 27% kept as sensitivity. research/21_gap section B.'
pax_src = 'Passenger share of CCS by region: Europe from Eurostat train-km (83% passenger) ; China HSR + metro ; NA = commuter/Amtrak share of PTC plus 100% of urban CBTC ; CIS freight-dominant. research/21_gap section C (analyst proxy, low-medium confidence).'
urban_src = 'Urban (metro + LRT) share of passenger CCS from km x unit-cost bottom-up on UITP network km and research/12 unit costs; cross-checked with GMI CBTC USD 4.9bn. research/21_gap section D.'
cagr_src = 'Nominal USD at constant 2025 FX. Regional base CAGRs: Europe 5.0% = midpoint of SCI 4.6% nominal (2023-28) and UNIFE realised 5.7% real (2021-23 to 2023-25), below vendor reports (6-9%) given ERTMS slippage (ERTMS, DSD EUR 6.3bn, CP7), China new-build decelerating (investment -8.9% in 2024), APAC ex-China metro build-out (India ~1,000 km under construction), NA CBTC programmes (MTA USD 5.4bn 2025-29, BART, WMATA), CIS flat, RoW Gulf/LatAm metros. research/03, 07, 14, 21_gap.'
for i, reg in enumerate(rail_regions):
    inp('ccs_sh_%d' % i, 'CCS regional share: %s' % reg, ccs_share[i], '% of world CCS', ccs_share_src if i == 0 else 'See Europe row.', FMT_PCT)
for i, reg in enumerate(rail_regions):
    inp('pax_%d' % i, 'Passenger share of CCS: %s' % reg, pax_share[i], '%', pax_src if i == 0 else 'See Europe row.', FMT_PCT)
for i, reg in enumerate(rail_regions):
    inp('urb_%d' % i, 'Urban (metro/LRT) share of passenger CCS: %s' % reg, urban_share[i], '%', urban_src if i == 0 else 'See Europe row.', FMT_PCT)
for i, reg in enumerate(rail_regions):
    inp('ccs_g_%d' % i, 'Passenger CCS base CAGR 2025-31: %s' % reg, ccs_cagr_base[i], '%', cagr_src if i == 0 else 'See Europe row.', FMT_PCT)

section('Railway: ITS other than signalling (passenger information, onboard CCTV/APC, train tracking, condition monitoring, trackside detection)')
inp('gmi_apts', 'GMI APTS global market 2025', 6.83, 'USD bn', 'GMI: USD 6,830.1m (2025) to 15,528.2m (2035), 8.8% CAGR. research/17_gap section 4.', FMT_BN)
inp('gmi_rail_share', 'GMI APTS mode share: railways', 0.305, '%', 'GMI mode split: roadways 47.6%, railways 30.5%, airways 14.6%, waterways 7.3%.', FMT_PCT)
inp('gmi_ticketing', 'GMI APTS application share: ticketing (removed)', 0.242, '%', 'GMI application split: traffic management 30.1%, fleet management 25.2%, ticketing 24.2%, information dissemination 11.2%, passenger safety 9.3%.', FMT_PCT)
inp('rail_pis', 'DERIVED: rail passenger information, onboard and station systems', '=%s*%s*(1-%s)' % (R['gmi_apts'], R['gmi_rail_share'], R['gmi_ticketing']), 'USD bn', 'GMI APTS x railway share x (1 - ticketing). Medium-low confidence.', FMT_BN, derived=True)
inp('rail_cm', 'Rail asset condition monitoring and predictive-maintenance platforms (sold to operators)', 1.0, 'USD bn', 'Analyst assumption. Umbrella vendor figures (MarketsandMarkets rail asset management USD 12.8bn) include EAM/ERP and OEM services; OEM platforms (Hitachi HMAX ~2,500 trains, Siemens Railigent X, Alstom HealthHub, Konux ~6,000 assets) are mostly monetised inside service contracts. Low confidence. research/03, 09, 13.', FMT_BN)
inp('rail_td', 'Trackside detection and wayside monitoring (hot box, WILD, obstacle/intrusion detection)', 0.6, 'USD bn', 'Analyst assumption anchored on Frauscher (acquired by Wabtec for ~USD 792m), voestalpine, Sensonic, Rail Vision; axle counters counted in CCS. Low confidence. research/03, 22_gap.', FMT_BN)
inp('ro_hw', 'Rail other ITS component mix: hardware', 0.45, '% of value', 'Analyst assumption between GMI APTS (46.8% hardware) and rail CCS (46%).', FMT_PCT)
inp('ro_sw', 'Rail other ITS component mix: software', 0.30, '% of value', 'Same.', FMT_PCT)
ro_share = [0.40, 0.18, 0.15, 0.17, 0.03, 0.07]
for i, reg in enumerate(rail_regions):
    inp('ro_sh_%d' % i, 'Rail other ITS regional share: %s' % reg, ro_share[i], '%', 'Analyst assumption weighted by passenger rail fleets (UITP metro cars: APAC 58%, Europe 16%; EU mainline 160k vehicles; NTD 23.7k US rail cars) and spend intensity (NTD rail comm & info USD 1.5bn). research/05, 16.' if i == 0 else 'See Europe row.', FMT_PCT)
inp('ro_cagr_l', 'Rail other ITS CAGR 2025-31: Low', 0.05, '%', 'Low = rolling-stock renewal slips; Base = 7% (M&M rail asset mgmt 6.6%, Mordor rail telematics 7.6%, PIS 11.8% VMR tempered); High = predictive maintenance fleet-wide, GoA4 obstacle detection. research/03, 13.', FMT_PCT)
inp('ro_cagr_b', 'Rail other ITS CAGR 2025-31: Base', 0.07, '%', 'See Low.', FMT_PCT)
inp('ro_cagr_h', 'Rail other ITS CAGR 2025-31: High', 0.09, '%', 'See Low.', FMT_PCT)

section('Memo: adjacent fare collection (not in totals)')
inp('fare_low', 'Electronic fare collection market 2025: low estimate', 10.36, 'USD bn', 'TechSci (USD 10.36bn 2025, 11.3% CAGR to 2031). research/02.', FMT_BN)
inp('fare_high', 'Electronic fare collection market 2025: high estimate', 16.68, 'USD bn', 'Fortune Business Insights (USD 16.68bn 2025, 15.6% CAGR). research/02.', FMT_BN)

section('North America bottom-up cross-check (FTA NTD report year 2025, StatCan 2024)')
inp('us_buses', 'US active full-size buses (standard, articulated, over-the-road, double-deck, trolleybus)', 65239, 'vehicles', 'NTD 2025 Revenue Vehicle Inventory, data.transportation.gov; 977 agencies. research/16 (data/ntd_2025_bus_agency_tiers.csv).', FMT_INT)
inp('us_bus_modes_all', 'US active fixed-route bus-mode vehicles incl. cutaways/vans', 73112, 'vehicles', 'NTD 2025 RVI, modes MB/CB/RB/TB. research/16.', FMT_INT)
inp('ca_buses', 'Canada urban transit buses', 17783, 'vehicles', 'Statistics Canada urban transit industry 2024 (NAICS 485110). research/04.', FMT_INT)
inp('us_rail_cars', 'US active rail passenger vehicles (ex-locomotives)', 23666, 'vehicles', 'NTD 2025 RVI: heavy rail 12,946; commuter rail 7,406; light rail 2,527; streetcar 418; other 369. research/16.', FMT_INT)
inp('ntd_ci_bus', 'NTD communication and information systems capex, bus modes, 2025', 370.0, 'USD m', 'NTD 2025 capital expenses by capital use (fphd-jyyj): MB 370.0m; CB/RB/TB <3m. 2022-24: 344 / 403 / 380. research/16 (data/ntd_capex_comm_info_by_mode_year.csv).', FMT_M)
inp('ntd_ci_rail', 'NTD communication and information systems capex, rail modes, 2025', 1497.0, 'USD m', 'NTD 2025: HR 1,008m, CR 259m, LR 186m, SR 35m, other 9m. research/16.', FMT_M)
inp('ntd_ci_total', 'NTD communication and information systems capex, all modes, 2025', 1902.0, 'USD m', 'NTD 2025; 5.9% of USD 32.35bn total transit capex; 4-year average USD 2.11bn. research/14, 16.', FMT_M)
inp('ntd_fare_capex', 'NTD fare collection equipment capex, 2025 (adjacent)', 521.0, 'USD m', 'NTD 2025: bus 94m, rail 423m. research/16.', FMT_M)
inp('cad_full', 'CAD/AVL full-system replacement per bus', 27000, 'USD/bus', 'Board-document awards 2021-26: median USD 24.2k per vehicle (MARTA 18.1k, Brampton 18.3k, Marin 18.8k, CapMetro 20.0k, TfL 23.1k, Metrolinx 25.4k, TTC 25.7k, Kitsap 28.2k); USD 42-45k where radio/VoIP and 5-year hosting are bundled (Santa Monica, LA Metro). research/31_gap, 35_gap.', FMT_INT)
inp('cad_cycle', 'Realised CAD/AVL full-replacement cycle', 17, 'years', 'Median 19 years across 7 dated pairs (LA Metro 2004-25, CapMetro 2006-25, Santa Monica 2002-21, Phoenix 2001-16, AC Transit 1999-2015); incumbent-held systems reach a decision point after a median 16 years (n=23). research/31_gap, 35_gap.', '0')
inp('midlife', 'Mid-life refresh per bus (IVN/APC/touchscreen/radio upgrades)', 10000, 'USD/bus', 'WMATA 2023-26 USD 13.4k/bus; SMART 2023 USD 17.4k; OCTA cumulative USD 10.3k; Phoenix 2018 USD 15.6k; NJ Transit 2026 USD 2.5k. Range 2.5-17k every 8-13 years. research/31_gap.', FMT_INT)
inp('midlife_cycle', 'Mid-life refresh cycle', 10, 'years', 'research/31_gap takeaway 2.', '0')
inp('video_per_bus', 'Onboard video system per bus (retrofit)', 11000, 'USD/bus', 'CapMetro/Luminator USD 2.96m/272 buses and Golden Gate/Apollo USD 0.9m/80 = USD 11k; Broward 2020 USD 14.5k; camera-only swaps USD 2.8-5k. research/35_gap, 31_gap.', FMT_INT)
inp('video_cycle', 'Onboard video replacement cycle', 10, 'years', 'Agency TAM useful lives 5-10 years for cameras/DVRs; retrofits observed at 8-12 years. research/31_gap.', '0')
inp('apc_per_bus', 'Automatic passenger counting per equipped bus (turnkey)', 7300, 'USD/bus', 'Marin/UTA USD 502,875 / 69 vehicles = USD 7.3k (sensors 5.0k, install, certification, software); AC Transit USD 8.2k per newly equipped bus. research/35_gap.', FMT_INT)
inp('apc_cycle', 'APC replacement cycle', 12, 'years', 'Refreshed with vehicle or mid-life; 12 years assumed.', '0')
inp('apc_cov', 'Share of fleet with APC', 0.60, '%', 'USDOT ITS Deployment Tracking Survey 2023: APC at 54% of fixed-route bus agencies, 60% of large-urban agencies, 85% of the large-metro panel (unconfirmed detail, research/15, 90_verification c27).', FMT_PCT)
inp('rec_per_bus', 'Recurring CAD/AVL vendor maintenance and hosting per bus per year', 2200, 'USD/bus/yr', 'Median USD 2.2k across renewals: CTA USD 3.3k (USD 43.4m/7 yrs/1,870 buses), GCRTA 2.9k, Miami-Dade 2.6k, AC Transit 2.2k (incl. Azure hosting USD 0.5-0.7k), NORTA 1.8-2.1k, SORTA 1.7k, MARTA 1.0k; TfL iBus2 all-in ~USD 2.3k. research/31_gap, 35_gap, 12.', FMT_INT)
inp('saas_per_bus', 'Overlay SaaS and scheduling software per bus per year', 800, 'USD/bus/yr', 'Real-time/analytics SaaS USD 0.5-1.0k for 300-650-bus fleets (AC Transit 546-829, MARTA 926, NCTD 493), USD 1.4-2.0k for sub-150-bus fleets with several modules; HASTUS licence/support USD 0.2-0.8k. research/31_gap, 35_gap.', FMT_INT)
inp('wayside_adder', 'Wayside PIS, depot, control-centre and back-office adder', 0.15, '% of onboard and recurring', 'Analyst assumption; stop displays, yard systems, scheduling servers. The 31_gap bottom-up puts wayside PIS inside its USD 0.53bn capex half.', FMT_PCT)
inp('refresh_cohort', 'US buses on 2009-2016 CAD/AVL platforms reaching 15-20 years in 2026-31', 12000, 'buses', 'TriMet (2009, INIT, 668), Denver RTD (2011, INIT, 968), NJ Transit (2013, Clever, 2,542), Miami-Dade (2013, 845), Broward (2015, 459), AC Transit (2015, 630), Phoenix (2016, 800+), TTC (2016-18, 2,300), King County (2016, 1,450), TransLink (2016). research/31_gap takeaway 9.', FMT_INT)
inp('ulb_wave', 'US full-size buses reaching useful-life benchmark 2026-2031', 24143, 'vehicles', 'NTD 2025 RVI fleet age vs agency ULB (12 or 14 years). research/04 takeaway 8.', FMT_INT)
inp('ulb_backlog', 'US full-size buses already past useful-life benchmark (2025)', 12644, 'vehicles', 'Same.', FMT_INT)
inp('zeb_stock', 'US full-size zero-emission buses funded/ordered/delivered (July 2025)', 8116, 'vehicles', 'CALSTART Zeroing in on ZEBs 2025/26: +16% y/y; ~2,850 battery-electric active in NTD 2025. research/04.', FMT_INT)

section('US federal transit funding (FTA, USD bn): history and FY2027 scenarios')
inp('fta_2022', 'Total FTA appropriations FY2022', 20.51, 'USD bn', 'Statute (49 USC 5338) plus IIJA Division J advance appropriations (USD 4.25bn/yr), per FTA Federal Register apportionment notices. research/25_gap table 2.1.', FMT_BN)
inp('fta_2023', 'Total FTA appropriations FY2023', 21.43, 'USD bn', 'Same.', FMT_BN)
inp('fta_2024', 'Total FTA appropriations FY2024', 20.86, 'USD bn', 'Same.', FMT_BN)
inp('fta_2025', 'Total FTA appropriations FY2025', 20.94, 'USD bn', 'Same.', FMT_BN)
inp('fta_2026', 'Total FTA appropriations FY2026 (computed from P.L. 119-75)', 20.96, 'USD bn', 'USD 14.642bn formula + 1.70 CIG + 0.15 WMATA + 0.21 TIG + 4.25 Division J. research/25_gap.', FMT_BN)
inp('fta_2027_house', 'FY2027 scenario: House BUILD America 250 Act (H.R. 8870) as authorised', 20.0, 'USD bn', 'USD 16.87bn Mass Transit Account + 3.0 CIG authorised + 0.15 WMATA; 18.7 if CIG appropriated at FY2026 rate. No Low-No, no advance appropriations. Stalled as of Nov 2026. research/25_gap.', FMT_BN)
inp('fta_2027_ext', 'FY2027 scenario: flat extension without IIJA advance appropriations', 16.7, 'USD bn', 'Surface Transportation Extension Act 2026 (P.L. 119-103) continues FY2026 levels to 11 Dec 2026 but not the USD 4.25bn Division J tranche. research/25_gap.', FMT_BN)
inp('fta_2027_req', "FY2027 scenario: President's request", 16.3, 'USD bn', 'FY2027 Budget Appendix: USD 14.95bn formula limitation, CIG 1.215, no TIG/ASAP. research/25_gap.', FMT_BN)

section('Bus pool by application (GMI APTS application mix, ex-ticketing) and haircut sensitivity')
inp('app_ops', 'GMI application share: traffic/operations management + fleet management', 0.553, '% of APTS', 'GMI application split: traffic management 30.1% (in an APTS context = operations/headway control), fleet management 25.2%, ticketing 24.2%, information dissemination 11.2%, passenger safety 9.3%. research/17_gap 4.3.', FMT_PCT)
inp('app_info', 'GMI application share: public information dissemination', 0.112, '% of APTS', 'Same.', FMT_PCT)
inp('app_safety', 'GMI application share: passenger safety and security', 0.093, '% of APTS', 'Same.', FMT_PCT)
inp('haircut_alt1', 'Haircut sensitivity: alternative 1', 0.0, '%', 'No haircut (Berg fare-inclusive).', FMT_PCT)
inp('haircut_alt2', 'Haircut sensitivity: alternative 2', 0.15, '%', 'GMI electronic-payment technology share 14.7%.', FMT_PCT)
inp('haircut_alt3', 'Haircut sensitivity: alternative 3', 0.25, '%', 'GMI ticketing application share 24.2%.', FMT_PCT)

section('Illustrative buy-and-build value bridge (thesis sheet; analyst assumptions, blue)')
inp('vb_rev0', 'Entry: platform revenue (founder-owned mid-market bus ITS / scheduling vendor)', 60, 'USD m', 'Illustrative; private mid-market vendors (Avail, GIRO, Hanover, ETA, Passio) are USD 20-100m revenue businesses (research/08, 32_gap).', FMT_M)
inp('vb_mult0', 'Entry: EV / revenue', 2.0, 'x', 'Integrator band 1.0-2.6x revenue (INIT 1.0x, IVU 2.6x, Knorr-Alstom NA ~2.1x). research/26_gap.', FMT_X)
inp('vb_margin0', 'Entry: EBITDA margin', 0.15, '%', 'INIT EBITDA margin 14.9% (2025); mid-market integrators 10-18%. research/17.', FMT_PCT)
inp('vb_g', 'Organic revenue growth p.a. (hold period)', 0.08, '%', 'Above the NA bus base (5%) on SaaS overlay cross-sell, enforcement/ZEB modules and long-tail wins; below Via/INIT 24-29%.', FMT_PCT)
inp('vb_bolt', 'Bolt-on revenue acquired over the hold (cumulative)', 40, 'USD m', 'Two to three point-solution bolt-ons (APC, PIS, enforcement) at 1-2x revenue.', FMT_M)
inp('vb_boltmult', 'Bolt-on EV / revenue', 1.5, 'x', 'Modaxo-Conduent 0.44x to Knorr-Alstom 2.1x.', FMT_X)
inp('vb_hold', 'Hold period', 5, 'years', '', '0')
inp('vb_margin1', 'Exit: EBITDA margin (after cloud re-platforming and mix shift)', 0.22, '%', 'IVU 14% EBIT / ~18% EBITDA with 52% recurring; Trimble segments 20-34%; target 22%.', FMT_PCT)
inp('vb_mult1', 'Exit: EV / EBITDA', 14, 'x', 'IVU 15.2x, Trimble 12.0x, Cubic LBO 15.7x; strategic buyers (Hitachi, Siemens, Modaxo, Via). research/26_gap.', FMT_X)
inp('vb_lev', 'Net debt at entry as multiple of EBITDA', 2.5, 'x', 'Deliberately modest: Cubic failed at ~11x. research/10, 26_gap.', FMT_X)

INPUT_LAST_ROW = row[0]

# ----------------------------------------------------------------------------
# TOPDOWN: third-party estimates and reconciliation
# ----------------------------------------------------------------------------
wt = wb.create_sheet('TopDown')
title(wt, 'Top-down estimates: what third parties publish, what each includes, and how the model reconciles them', 'Values as published (not converted). Scope flags explain why the numbers differ by an order of magnitude.')
setw(wt, [34, 12, 10, 12, 10, 9, 44, 22, 34])
hdr(wt, 4, ['Source and report', 'Base value', 'Base year', 'Forecast value', 'Forecast yr', 'CAGR', 'Scope (what is inside)', 'Fit to our scope', 'Use in model / research file'])
td = [
    ('Global ITS umbrella (MarketsandMarkets, Precedence, Mordor, Grand View, IMARC)', '41-58', '2025', '60-90', '2030', '5-11%', 'Roadway traffic management (ATMS ~38%), tolling, parking, commercial vehicles, aviation, maritime, plus APTS ~11-17%', 'Poor: 6-10x too wide', 'Context only (research/01, 17_gap)'),
    ('Berg Insight, Public Transport ITS in Europe and North America, 10th ed. (Mar 2026)', 'EUR 2.55 (EU) + 1.22 (NA)', '2025', 'EUR 3.30 + 1.56', '2030', '5.3% / 5.0%', 'On-vehicle, stop, depot and back-office systems for buses and trams; passenger information; fare payment and journey planners named in definition; 86 vendor profiles', 'Best fit for Roadway EU/NA (fare-inclusive)', 'Roadway anchor less ex-fare haircut (Inputs)'),
    ('Global Market Insights, Advanced Public Transportation System (Aug 2026)', 'USD 6.83', '2025', 'USD 15.5', '2035', '8.8%', 'Vehicle location/dispatch, passenger information, fare collection, traffic-management tools, analytics across bus, rail, air, water; public operators 48.8% of end use', 'Partial: all modes, fare-inclusive, private fleets', 'Component, mode, application and regional mix; RoW scaling; rail PIS carve (Inputs)'),
    ('UNIFE World Rail Market Study 2026 (Bain): rail control segment', 'EUR 24.9', '2023-25 avg', '+3.2% p.a. total market', '2029-31', '5.7% realised', 'Control-command and signalling, trackside and onboard, 66 countries, freight included, maintenance in separate services segment (EUR 84.1bn)', 'Good for Railway signalling after passenger carve-out', 'Rail CCS anchor (Inputs); carve-out in research/21_gap'),
    ('SCI Verkehr, CCS market study (Mar 2026)', 'EUR ~20', '2025', 'Europe fastest-growing to 2030', '2030', '4.6% (2023-28)', 'Digital train control, train protection, signalling; OE plus after-sales; Europe almost half; ~90% of European volume is modernisation', 'Good (low case)', 'Low-case CCS anchor; modernisation share (Drivers)'),
    ('Vendor railway signalling reports (GMI 19.6, Fortune, MRFR, SkyQuest 16.5, IMARC 11.6)', 'USD 11.6-23.6', '2025', 'USD 19-42', '2033-34', '5.9-8.9%', 'Signalling equipment and services, freight included; narrower reports exclude services or onboard', 'Medium', 'Growth cross-check (research/03)'),
    ('MarketsandMarkets, railway management system', 'USD 55.5', '2025', 'USD 76.0', '2030', '6.5%', 'Umbrella: traffic management, asset management, PIS, security, analytics; overlaps CCS', 'Poor: overlaps and double counts', 'Growth signal only'),
    ('MarketsandMarkets, passenger information systems', 'USD 35.6', '2025', 'USD 68.6', '2031', '11.6%', 'Rail, road, air PIS incl. station infrastructure, global build-out', 'Poor: too wide', 'Growth signal only (research/02)'),
    ('Electronic fare collection (TechSci; Fortune)', 'USD 10.4-16.7', '2025', 'USD 19.7 (TechSci)', '2031', '11-16%', 'AFC, validators, account-based ticketing, open payments', 'Adjacent (excluded)', 'Memo line only'),
    ('Via Transportation S-1: TAM for public transportation solution providers', 'USD 250', '2024', 'n/a', 'n/a', '~5%', 'Includes operated service (microtransit, paratransit, school, NEMT) in NA + Europe; SAM USD 82bn excludes fleets >250 vehicles', 'Not comparable (services-inclusive)', 'Thesis context only (research/18)'),
    ('FTA NTD communication and information systems capital expense', 'USD 1.90', '2025', 'USD 2.11 (4-yr avg)', '2022-25', 'flat', 'US agencies capex on radio, cab signalling/train control, AVL, dispatching, PA, operations software; rail 79%; capex only, no SaaS/maintenance opex', 'Good floor for US', 'Bottom-up cross-check (BottomUp_NA)'),
]
r = 5
for rec in td:
    for j, v in enumerate(rec):
        c = wt.cell(row=r, column=j + 1, value=v); c.font = BLACK; c.alignment = WRAP; c.border = BOX
    wt.row_dimensions[r].height = 58
    r += 1
r += 1
wt.cell(row=r, column=1, value='Reconciliation chain used in the model (USD bn, 2025)').font = H2; r += 1
chain = [
    ('Berg EU + NA bus/tram ITS, fare-inclusive', '=(%s+%s)*%s' % (R['berg_eu'], R['berg_na'], R['fx'])),
    ('less ex-fare haircut', '=-(%s+%s)*%s*%s' % (R['berg_eu'], R['berg_na'], R['fx'], R['haircut'])),
    ('plus rest-of-world bus ITS (scaled, ex-fare)', '=(%s+%s)*%s*%s*(1-%s)' % (R['berg_eu'], R['berg_na'], R['fx'], R['row_scale'], R['haircut'])),
    ('Roadway core (subtotal)', '=SUM(B%d:B%d)' % (r, r + 2)),
    ('Rail CCS passenger (UNIFE anchor x regional passenger shares)', "=Market_2025!B%d"),  # placeholder filled later
    ('Rail other ITS', "=Market_2025!B%d"),
    ('Public ITS core total', None),
]
chain_rows = {}
for lab, f in chain:
    wt.cell(row=r, column=1, value=lab).font = BOLD if ('subtotal' in lab or 'core total' in lab) else BLACK
    chain_rows[lab] = r
    if f and not f.startswith('=Market'):
        c = wt.cell(row=r, column=2, value=f); c.font = BLACK; c.number_format = FMT_BN
    r += 1
TD_CHAIN = chain_rows

# ----------------------------------------------------------------------------
# MARKET_2025
# ----------------------------------------------------------------------------
wm = wb.create_sheet('Market_2025')
title(wm, 'Public ITS market 2025: segment x component x geography (USD bn, core scope ex-fare)', 'All cells are formulas on Inputs. Geography columns aggregate rail regions into four reporting geographies.')
setw(wm, [44, 12, 12, 12, 12, 16, 3, 30, 12, 12, 12, 12, 12])
hdr(wm, 4, ['Segment / region', 'Total', 'Hardware', 'Software', 'Services', 'Reporting geography'])
fx = R['fx']; hc = R['haircut']
rows_m = []  # (label, total_formula, hw_share_ref, sw_share_ref, geo, block)
bus_eu = '=%s*%s*(1-%s)' % (R['berg_eu'], fx, hc)
bus_na = '=%s*%s*(1-%s)' % (R['berg_na'], fx, hc)
bus_row_tot = '(%s+%s)*%s*%s*(1-%s)' % (R['berg_eu'], R['berg_na'], fx, R['row_scale'], hc)
rows_m.append(('Roadway: bus and tram ITS, Europe', bus_eu, R['bus_hw'], R['bus_sw'], 'Europe', 'Bus'))
rows_m.append(('Roadway: bus and tram ITS, North America', bus_na, R['bus_hw'], R['bus_sw'], 'North America', 'Bus'))
rows_m.append(('Roadway: bus ITS, Asia-Pacific', '=%s*%s' % (bus_row_tot, R['row_apac_share']), R['bus_hw'], R['bus_sw'], 'Asia-Pacific', 'Bus'))
rows_m.append(('Roadway: bus ITS, rest of world (LatAm, MEA)', '=%s*(1-%s)' % (bus_row_tot, R['row_apac_share']), R['bus_hw'], R['bus_sw'], 'Rest of world', 'Bus'))
geo_map = {'Europe': 'Europe', 'China': 'Asia-Pacific', 'APAC ex-China': 'Asia-Pacific', 'North America': 'North America', 'CIS/Eurasia': 'Rest of world', 'Rest of world': 'Rest of world'}
for i, reg in enumerate(rail_regions):
    pax = '%s*%s*%s*%s' % (R['unife_cc'], R['ccs_sh_%d' % i], R['pax_%d' % i], fx)
    rows_m.append(('Railway: urban (metro/LRT) signalling, %s' % reg, '=%s*%s' % (pax, R['urb_%d' % i]), R['ccs_hw'], R['ccs_sw'], geo_map[reg], 'Rail CCS urban'))
for i, reg in enumerate(rail_regions):
    pax = '%s*%s*%s*%s' % (R['unife_cc'], R['ccs_sh_%d' % i], R['pax_%d' % i], fx)
    rows_m.append(('Railway: mainline and commuter passenger signalling, %s' % reg, '=%s*(1-%s)' % (pax, R['urb_%d' % i]), R['ccs_hw'], R['ccs_sw'], geo_map[reg], 'Rail CCS mainline'))
ro_tot = '(%s+%s+%s)' % (R['rail_pis'], R['rail_cm'], R['rail_td'])
for i, reg in enumerate(rail_regions):
    rows_m.append(('Railway: other ITS (PIS, CCTV/APC, tracking, condition monitoring, detection), %s' % reg, '=%s*%s' % (ro_tot, R['ro_sh_%d' % i]), R['ro_hw'], R['ro_sw'], geo_map[reg], 'Rail other'))
r = 5
first = r
block_rows = {}
for lab, tf, hw, sw, geo, blk in rows_m:
    wm.cell(row=r, column=1, value=lab).font = BLACK
    c = wm.cell(row=r, column=2, value=tf); c.font = GREEN; c.number_format = FMT_BN
    c = wm.cell(row=r, column=3, value='=B%d*%s' % (r, hw)); c.font = BLACK; c.number_format = FMT_BN
    c = wm.cell(row=r, column=4, value='=B%d*%s' % (r, sw)); c.font = BLACK; c.number_format = FMT_BN
    c = wm.cell(row=r, column=5, value='=B%d-C%d-D%d' % (r, r, r)); c.font = BLACK; c.number_format = FMT_BN
    wm.cell(row=r, column=6, value=geo).font = BLACK
    wm.cell(row=r, column=8, value=blk).font = NOTE  # helper column H for SUMIF
    block_rows.setdefault(blk, []).append(r)
    r += 1
last = r - 1
wm.cell(row=r, column=1, value='Public ITS core total').font = BOLD
for col in 'BCDE':
    c = wm['%s%d' % (col, r)]; c.value = '=SUM(%s%d:%s%d)' % (col, first, col, last); c.font = BOLD; c.number_format = FMT_BN
TOTAL_ROW = r
r += 2
# Summary by mode/block
wm.cell(row=r, column=1, value='Summary by segment (USD bn)').font = H2; r += 1
hdr(wm, r, ['Segment', 'Total', 'Hardware', 'Software', 'Services', 'Share of total']); r += 1
seg_rows = {}
for blk, lab in [('Bus', 'Roadway: bus and tram ITS'), ('Rail CCS urban', 'Railway: urban signalling (CBTC etc.)'), ('Rail CCS mainline', 'Railway: mainline and commuter signalling'), ('Rail other', 'Railway: other ITS')]:
    wm.cell(row=r, column=1, value=lab).font = BLACK
    for j, col in enumerate('BCDE'):
        c = wm['%s%d' % (col, r)]
        c.value = '=SUMIF($H$%d:$H$%d,"%s",%s$%d:%s$%d)' % (first, last, blk, col, first, col, last)
        c.font = BLACK; c.number_format = FMT_BN
    c = wm['F%d' % r]; c.value = '=B%d/$B$%d' % (r, TOTAL_ROW); c.number_format = FMT_PCT; c.font = BLACK
    seg_rows[blk] = r
    r += 1
wm.cell(row=r, column=1, value='Total').font = BOLD
for col in 'BCDE':
    c = wm['%s%d' % (col, r)]; c.value = '=SUM(%s%d:%s%d)' % (col, r - 4, col, r - 1); c.font = BOLD; c.number_format = FMT_BN
c = wm['F%d' % r]; c.value = '=B%d/$B$%d' % (r, TOTAL_ROW); c.number_format = FMT_PCT
SEG_TOTAL_ROW = r
r += 1
wm.cell(row=r, column=1, value='of which contestable, software-led pool (bus ITS + rail other ITS)').font = BOLD
c = wm['B%d' % r]; c.value = '=B%d+B%d' % (seg_rows['Bus'], seg_rows['Rail other']); c.font = BOLD; c.number_format = FMT_BN
c = wm['F%d' % r]; c.value = '=B%d/$B$%d' % (r, TOTAL_ROW); c.number_format = FMT_PCT
CONTEST_ROW = r
r += 1
wm.cell(row=r, column=1, value='of which rail signalling (closed oligopoly)').font = BLACK
c = wm['B%d' % r]; c.value = '=B%d+B%d' % (seg_rows['Rail CCS urban'], seg_rows['Rail CCS mainline']); c.number_format = FMT_BN
c = wm['F%d' % r]; c.value = '=B%d/$B$%d' % (r, TOTAL_ROW); c.number_format = FMT_PCT
CCS_ROW = r
r += 2
# Summary by component
wm.cell(row=r, column=1, value='Summary by component (USD bn)').font = H2; r += 1
hdr(wm, r, ['Component', 'Value', 'Share']); r += 1
COMP_ROWS = {}
for lab, col in [('Hardware', 'C'), ('Software', 'D'), ('Services', 'E')]:
    wm.cell(row=r, column=1, value=lab).font = BLACK
    c = wm['B%d' % r]; c.value = '=%s%d' % (col, TOTAL_ROW); c.number_format = FMT_BN; c.font = BLACK
    c = wm['C%d' % r]; c.value = '=B%d/$B$%d' % (r, TOTAL_ROW); c.number_format = FMT_PCT; c.font = BLACK
    COMP_ROWS[lab] = r
    r += 1
r += 1
# Summary by geography
wm.cell(row=r, column=1, value='Summary by reporting geography (USD bn)').font = H2; r += 1
hdr(wm, r, ['Geography', 'Total', 'of which bus', 'of which rail signalling', 'of which rail other', 'Share of total']); r += 1
GEO_ROWS = {}
for geo in ['North America', 'Europe', 'Asia-Pacific', 'Rest of world']:
    wm.cell(row=r, column=1, value=geo).font = BLACK
    c = wm['B%d' % r]; c.value = '=SUMIF($F$%d:$F$%d,"%s",$B$%d:$B$%d)' % (first, last, geo, first, last); c.number_format = FMT_BN; c.font = BLACK
    c = wm['C%d' % r]; c.value = '=SUMIFS($B$%d:$B$%d,$F$%d:$F$%d,"%s",$H$%d:$H$%d,"Bus")' % (first, last, first, last, geo, first, last); c.number_format = FMT_BN; c.font = BLACK
    c = wm['D%d' % r]; c.value = '=SUMIFS($B$%d:$B$%d,$F$%d:$F$%d,"%s",$H$%d:$H$%d,"Rail CCS urban")+SUMIFS($B$%d:$B$%d,$F$%d:$F$%d,"%s",$H$%d:$H$%d,"Rail CCS mainline")' % (first, last, first, last, geo, first, last, first, last, first, last, geo, first, last); c.number_format = FMT_BN; c.font = BLACK
    c = wm['E%d' % r]; c.value = '=SUMIFS($B$%d:$B$%d,$F$%d:$F$%d,"%s",$H$%d:$H$%d,"Rail other")' % (first, last, first, last, geo, first, last); c.number_format = FMT_BN; c.font = BLACK
    c = wm['F%d' % r]; c.value = '=B%d/$B$%d' % (r, TOTAL_ROW); c.number_format = FMT_PCT; c.font = BLACK
    GEO_ROWS[geo] = r
    r += 1
wm.cell(row=r, column=1, value='Total').font = BOLD
for col in 'BCDE':
    c = wm['%s%d' % (col, r)]; c.value = '=SUM(%s%d:%s%d)' % (col, r - 4, col, r - 1); c.font = BOLD; c.number_format = FMT_BN
r += 2
wm.cell(row=r, column=1, value='Memo (not in totals)').font = H2; r += 1
wm.cell(row=r, column=1, value='Roadway bus/tram ITS incl. fare collection (Berg scope, EU + NA + RoW)').font = BLACK
c = wm['B%d' % r]; c.value = '=(%s+%s)*%s*(1+%s)' % (R['berg_eu'], R['berg_na'], fx, R['row_scale']); c.number_format = FMT_BN; c.font = GREEN; r += 1
wm.cell(row=r, column=1, value='Electronic fare collection market (adjacent), range').font = BLACK
c = wm['B%d' % r]; c.value = '=%s' % R['fare_low']; c.number_format = FMT_BN; c.font = GREEN
c = wm['C%d' % r]; c.value = '=%s' % R['fare_high']; c.number_format = FMT_BN; c.font = GREEN; r += 1
wm.cell(row=r, column=1, value='Rail CCS incl. freight (UNIFE anchor, USD)').font = BLACK
c = wm['B%d' % r]; c.value = '=%s*%s' % (R['unife_cc'], fx); c.number_format = FMT_BN; c.font = GREEN; r += 1
wm.cell(row=r, column=1, value='Helper column H holds the block tag used by SUMIF.').font = NOTE
r += 2
wm.cell(row=r, column=1, value='Investor view 1: two-tier market (who buys)').font = H2; r += 1
hdr(wm, r, ['Tier', 'Total', 'Hardware', 'Software', 'Services', 'Share of total']); r += 1
TIER_ROWS = {}
wm.cell(row=r, column=1, value='Transit-operator ITS core (bus and tram ITS + urban signalling + other rail ITS)').font = BLACK
for j, col in enumerate('BCDE'):
    c = wm['%s%d' % (col, r)]; c.value = '=%s%d+%s%d+%s%d' % (col, seg_rows['Bus'], col, seg_rows['Rail CCS urban'], col, seg_rows['Rail other']); c.font = BLACK; c.number_format = FMT_BN
c = wm['F%d' % r]; c.value = '=B%d/$B$%d' % (r, TOTAL_ROW); c.number_format = FMT_PCT
TIER_ROWS['core'] = r; r += 1
wm.cell(row=r, column=1, value='Mainline and commuter passenger signalling (infrastructure-manager and railway buyers)').font = BLACK
for j, col in enumerate('BCDE'):
    c = wm['%s%d' % (col, r)]; c.value = '=%s%d' % (col, seg_rows['Rail CCS mainline']); c.font = BLACK; c.number_format = FMT_BN
c = wm['F%d' % r]; c.value = '=B%d/$B$%d' % (r, TOTAL_ROW); c.number_format = FMT_PCT
TIER_ROWS['mainline'] = r; r += 1
wm.cell(row=r, column=1, value='Public ITS, brief scope (both tiers)').font = BOLD
for j, col in enumerate('BCDE'):
    c = wm['%s%d' % (col, r)]; c.value = '=%s%d+%s%d' % (col, r - 2, col, r - 1); c.font = BOLD; c.number_format = FMT_BN
TIER_ROWS['total'] = r; r += 2

wm.cell(row=r, column=1, value='Investor view 2: openness to a new entrant (USD bn)').font = H2; r += 1
hdr(wm, r, ['Tier', 'Total', 'North America', 'Europe', 'Asia-Pacific', 'Rest of world']); r += 1
OPEN_ROWS = {}
def geo_sum(blocks, comps):
    # sum over market rows of block in blocks and component columns comps for a geography (SUMIFS per component)
    parts = []
    for b in blocks:
        for col in comps:
            parts.append('SUMIFS($%s$%d:$%s$%d,$F$%d:$F$%d,"GEO",$H$%d:$H$%d,"%s")' % (col, first, col, last, first, last, first, last, b))
    return '+'.join(parts)
geos4 = ['North America', 'Europe', 'Asia-Pacific', 'Rest of world']
for key, lab, blocks, comps in [('closed', 'Closed: signalling cores (urban and mainline), SIL-4 certified, 3-4 suppliers', ['Rail CCS urban', 'Rail CCS mainline'], 'BCDE'[1:]), ('held', 'Incumbent-held, displaceable at refresh: onboard and wayside hardware in bus and other rail ITS', ['Bus', 'Rail other'], 'C'), ('open', 'Open: software and services in bus and other rail ITS (asset-light SAM)', ['Bus', 'Rail other'], 'DE')]:
    wm.cell(row=r, column=1, value=lab).font = BLACK
    for j, geo in enumerate(geos4):
        f = '=' + geo_sum(blocks, comps).replace('"GEO"', '"%s"' % geo)
        c = wm.cell(row=r, column=3 + j, value=f); c.font = BLACK; c.number_format = FMT_BN
    c = wm['B%d' % r]; c.value = '=SUM(C%d:F%d)' % (r, r); c.font = BOLD; c.number_format = FMT_BN
    OPEN_ROWS[key] = r; r += 1
wm.cell(row=r, column=1, value='Total (ties to core total)').font = BOLD
for col in 'BCDEF':
    c = wm['%s%d' % (col, r)]; c.value = '=SUM(%s%d:%s%d)' % (col, r - 3, col, r - 1); c.font = BOLD; c.number_format = FMT_BN
OPEN_ROWS['total'] = r; r += 2

wm.cell(row=r, column=1, value='Investor view 3: bus and tram ITS pool by application (GMI application mix applied ex-ticketing)').font = H2; r += 1
hdr(wm, r, ['Application', 'Value', 'Share of bus pool']); r += 1
APP_ROWS = {}
den = '(%s+%s+%s)' % (R['app_ops'], R['app_info'], R['app_safety'])
for key, lab, ref in [('ops', 'Operations and fleet management (CAD/AVL, scheduling, dispatch, headway control)', R['app_ops']), ('info', 'Passenger information', R['app_info']), ('safety', 'Safety, security and surveillance (video, enforcement, incident detection)', R['app_safety'])]:
    wm.cell(row=r, column=1, value=lab).font = BLACK
    c = wm['B%d' % r]; c.value = '=B%d*%s/%s' % (seg_rows['Bus'], ref, den); c.font = BLACK; c.number_format = FMT_BN
    c = wm['C%d' % r]; c.value = '=B%d/B%d' % (r, seg_rows['Bus']); c.number_format = FMT_PCT
    APP_ROWS[key] = r; r += 1
r += 1
wm.cell(row=r, column=1, value='Sensitivity: bus and tram ITS pool (global, USD bn) by ex-fare haircut').font = H2; r += 1
hdr(wm, r, ['Haircut', 'Bus pool', 'Note']); r += 1
SENS_ROWS = {}
for key, ref, note in [('h0', R['haircut_alt1'], 'Berg fare-inclusive'), ('h15', R['haircut_alt2'], 'GMI electronic-payment share'), ('h20', R['haircut'], 'Base case'), ('h25', R['haircut_alt3'], 'GMI ticketing application share')]:
    c = wm['A%d' % r]; c.value = '=%s' % ref; c.number_format = FMT_PCT; c.font = GREEN
    c = wm['B%d' % r]; c.value = '=(%s+%s)*%s*(1+%s)*(1-%s)' % (R['berg_eu'], R['berg_na'], fx, R['row_scale'], ref); c.font = BLACK; c.number_format = FMT_BN
    wm.cell(row=r, column=3, value=note).font = NOTE
    SENS_ROWS[key] = r; r += 1

# fill TopDown chain links
wt['B%d' % TD_CHAIN['Rail CCS passenger (UNIFE anchor x regional passenger shares)']] = '=Market_2025!B%d' % CCS_ROW
wt['B%d' % TD_CHAIN['Rail other ITS']] = '=Market_2025!B%d' % seg_rows['Rail other']
wt['B%d' % TD_CHAIN['Public ITS core total']] = '=B%d+B%d+B%d' % (TD_CHAIN['Roadway core (subtotal)'], TD_CHAIN['Rail CCS passenger (UNIFE anchor x regional passenger shares)'], TD_CHAIN['Rail other ITS'])
for k in ['Rail CCS passenger (UNIFE anchor x regional passenger shares)', 'Rail other ITS', 'Public ITS core total']:
    wt['B%d' % TD_CHAIN[k]].number_format = FMT_BN; wt['B%d' % TD_CHAIN[k]].font = GREEN if k != 'Public ITS core total' else BOLD

# ----------------------------------------------------------------------------
# FORECAST
# ----------------------------------------------------------------------------
wf = wb.create_sheet('Forecast')
title(wf, 'Forecast 2025-2031 by segment and region (USD bn, core scope)', 'Active CAGR = CHOOSE(Inputs!scenario, Low, Base, High). Change the selector on Inputs to flex.')
setw(wf, [50, 9, 9, 9, 10, 3, 9, 9, 9, 9, 9, 9, 9, 3, 10, 12])
years = list(range(2025, 2032))
hdr(wf, 4, ['Segment / region', 'Low', 'Base', 'High', 'Active CAGR', '', *[str(y) for y in years], '', 'Block', '2025 source row'])
r = 5
ffirst = r
f_rows = []
# bus rows
bus_specs = [
    ('Roadway: bus and tram ITS, Europe', 5, R['bus_cagr_eu_l'], R['bus_cagr_eu_b'], R['bus_cagr_eu_h'], 'Bus'),
    ('Roadway: bus and tram ITS, North America', 6, R['bus_cagr_na_l'], R['bus_cagr_na_b'], R['bus_cagr_na_h'], 'Bus'),
    ('Roadway: bus ITS, Asia-Pacific', 7, R['bus_cagr_row_l'], R['bus_cagr_row_b'], R['bus_cagr_row_h'], 'Bus'),
    ('Roadway: bus ITS, rest of world', 8, R['bus_cagr_row_l'], R['bus_cagr_row_b'], R['bus_cagr_row_h'], 'Bus'),
]
specs = list(bus_specs)
for i, reg in enumerate(rail_regions):
    specs.append(('Railway: passenger signalling (urban + mainline), %s' % reg, None, '=%s+%s' % (R['ccs_g_%d' % i], R['ccs_cagr_delta_low']), '=%s' % R['ccs_g_%d' % i], '=%s+%s' % (R['ccs_g_%d' % i], R['ccs_cagr_delta_high']), 'Rail CCS', (block_rows['Rail CCS urban'][i], block_rows['Rail CCS mainline'][i])))
for i, reg in enumerate(rail_regions):
    specs.append(('Railway: other ITS, %s' % reg, block_rows['Rail other'][i], R['ro_cagr_l'], R['ro_cagr_b'], R['ro_cagr_h'], 'Rail other'))
for spec in specs:
    lab, src_row, lo, ba, hi, blk = spec[:6]
    wf.cell(row=r, column=1, value=lab).font = BLACK
    for j, ref in enumerate([lo, ba, hi]):
        c = wf.cell(row=r, column=2 + j, value=ref if str(ref).startswith('=') else '=%s' % ref); c.font = GREEN; c.number_format = FMT_PCT
    c = wf.cell(row=r, column=5, value='=CHOOSE(%s,B%d,C%d,D%d)' % (R['scenario'], r, r, r)); c.font = BLACK; c.number_format = FMT_PCT
    if src_row is None:
        u, m = spec[6]
        c = wf.cell(row=r, column=7, value='=Market_2025!B%d+Market_2025!B%d' % (u, m))
    else:
        c = wf.cell(row=r, column=7, value='=Market_2025!B%d' % src_row)
    c.font = GREEN; c.number_format = FMT_BN
    for k in range(1, 7):
        c = wf.cell(row=r, column=7 + k, value='=$G%d*(1+$E%d)^(%s%d-$G$4)' % (r, r, get_column_letter(7 + k), 4)); c.font = BLACK; c.number_format = FMT_BN
    wf.cell(row=r, column=15, value=blk).font = NOTE
    r += 1
flast = r - 1
# year header numeric for exponent: ensure row 4 year cells are numbers
for k, y in enumerate(years):
    wf.cell(row=4, column=7 + k, value=y)
wf.cell(row=r, column=1, value='Public ITS core total').font = BOLD
for k in range(7):
    col = get_column_letter(7 + k)
    c = wf['%s%d' % (col, r)]; c.value = '=SUM(%s%d:%s%d)' % (col, ffirst, col, flast); c.font = BOLD; c.number_format = FMT_BN
FT_TOTAL = r
c = wf['E%d' % r]; c.value = '=(M%d/G%d)^(1/6)-1' % (r, r); c.number_format = FMT_PCT; c.font = BOLD
r += 2
wf.cell(row=r, column=1, value='Summary by segment (USD bn)').font = H2; r += 1
hdr(wf, r, ['Segment', '', '', '', 'CAGR 25-31', '', *[str(y) for y in years]]); r += 1
FSEG = {}
for blk, lab in [('Bus', 'Roadway: bus and tram ITS'), ('Rail CCS', 'Railway: passenger signalling'), ('Rail other', 'Railway: other ITS')]:
    wf.cell(row=r, column=1, value=lab).font = BLACK
    for k in range(7):
        col = get_column_letter(7 + k)
        c = wf['%s%d' % (col, r)]; c.value = '=SUMIF($O$%d:$O$%d,"%s",%s$%d:%s$%d)' % (ffirst, flast, blk, col, ffirst, col, flast); c.font = BLACK; c.number_format = FMT_BN
    c = wf['E%d' % r]; c.value = '=(M%d/G%d)^(1/6)-1' % (r, r); c.number_format = FMT_PCT; c.font = BLACK
    FSEG[blk] = r
    r += 1
wf.cell(row=r, column=1, value='Total').font = BOLD
for k in range(7):
    col = get_column_letter(7 + k)
    c = wf['%s%d' % (col, r)]; c.value = '=SUM(%s%d:%s%d)' % (col, r - 3, col, r - 1); c.font = BOLD; c.number_format = FMT_BN
c = wf['E%d' % r]; c.value = '=(M%d/G%d)^(1/6)-1' % (r, r); c.number_format = FMT_PCT; c.font = BOLD
FSEG_TOTAL = r; r += 1
wf.cell(row=r, column=1, value='Contestable pool (bus + rail other)').font = BOLD
for k in range(7):
    col = get_column_letter(7 + k)
    c = wf['%s%d' % (col, r)]; c.value = '=%s%d+%s%d' % (col, FSEG['Bus'], col, FSEG['Rail other']); c.font = BOLD; c.number_format = FMT_BN
c = wf['E%d' % r]; c.value = '=(M%d/G%d)^(1/6)-1' % (r, r); c.number_format = FMT_PCT; c.font = BOLD
FCONTEST = r; r += 2

wf.cell(row=r, column=1, value='Open software and services SAM (bus + other rail ITS software and services; bus mix shifts to software)').font = BOLD
for k in range(7):
    col = get_column_letter(7 + k)
    t = '(%s$4-$G$4)/6' % col
    bus_sw_t = '(%s+(%s-%s)*%s)' % (R['bus_sw'], R['bus_sw_2031'], R['bus_sw'], t)
    bus_svc = '(1-%s-%s)' % (R['bus_hw'], R['bus_sw'])
    c = wf['%s%d' % (col, r)]; c.value = '=%s%d*(%s+%s)+%s%d*(1-%s)' % (col, FSEG['Bus'], bus_sw_t, bus_svc, col, FSEG['Rail other'], R['ro_hw']); c.font = BOLD; c.number_format = FMT_BN
c = wf['E%d' % r]; c.value = '=(M%d/G%d)^(1/6)-1' % (r, r); c.number_format = FMT_PCT; c.font = BOLD
FSAM = r; r += 2
wf.cell(row=r, column=1, value='Growth bridge 2025 to 2031, base case (USD bn): what the increase is made of').font = H2; r += 1
hdr(wf, r, ['Step', 'Delta', 'Running total', 'CAGR', 'Note']); r += 1
BRIDGE = {}
wf.cell(row=r, column=1, value='2025 market').font = BOLD
c = wf['C%d' % r]; c.value = '=G%d' % FSEG_TOTAL; c.font = BOLD; c.number_format = FMT_BN
BRIDGE['start'] = r; r += 1
bridge_steps = [
    ('Bus and tram ITS: Europe', '=M%d-G%d' % (ffirst, ffirst), '=E%d' % ffirst, 'ZEB turnover, ITxPT refresh, UK bus settlement'),
    ('Bus and tram ITS: North America', '=M%d-G%d' % (ffirst + 1, ffirst + 1), '=E%d' % (ffirst + 1), '24k buses past useful life, 2004-12 CAD/AVL cohort, AI enforcement'),
    ('Bus ITS: rest of world', '=M%d-G%d+M%d-G%d' % (ffirst + 2, ffirst + 2, ffirst + 3, ffirst + 3), '=E%d' % (ffirst + 2), 'China smart-bus retrofits, India e-bus procurement, Gulf networks'),
    ('Urban signalling (CBTC) resignalling and new lines', '=' + '+'.join('Market_2025!B%d*((1+E%d)^6-1)' % (block_rows['Rail CCS urban'][i], ffirst + 4 + i) for i in range(6)), '', 'NYC USD 5.4bn 2025-29, London, Paris, Toronto, Copenhagen GoA4, Asian metro build-out'),
    ('Mainline and commuter signalling (ETCS, interlockings, PTC)', '=' + '+'.join('Market_2025!B%d*((1+E%d)^6-1)' % (block_rows['Rail CCS mainline'][i], ffirst + 4 + i) for i in range(6)), '', 'ERTMS EUR 85-100bn remaining cost, DB EUR 6.3bn frameworks, FRMCS from 2027'),
    ('Other rail ITS (PIS, CCTV/APC, condition monitoring, detection)', '=M%d-G%d' % (FSEG['Rail other'], FSEG['Rail other']), '=E%d' % FSEG['Rail other'], 'Rolling-stock renewal, predictive maintenance fleet-wide, cyber'),
]
for lab, f, cg, note in bridge_steps:
    wf.cell(row=r, column=1, value=lab).font = BLACK
    c = wf['B%d' % r]; c.value = f; c.font = BLACK; c.number_format = FMT_BN
    c = wf['C%d' % r]; c.value = '=C%d+B%d' % (r - 1, r); c.font = BLACK; c.number_format = FMT_BN
    if cg:
        c = wf['D%d' % r]; c.value = cg; c.font = GREEN; c.number_format = FMT_PCT
    wf.cell(row=r, column=5, value=note).font = NOTE
    BRIDGE[lab] = r; r += 1
wf.cell(row=r, column=1, value='2031 market (check vs forecast total)').font = BOLD
c = wf['C%d' % r]; c.value = '=C%d' % (r - 1); c.font = BOLD; c.number_format = FMT_BN
c = wf['D%d' % r]; c.value = '=ROUND(C%d-M%d,6)' % (r, FSEG_TOTAL); c.font = NOTE; c.number_format = '0.000000'
wf.cell(row=r, column=5, value='D = difference to Forecast total, should be 0').font = NOTE
BRIDGE['end'] = r; r += 2

wf.cell(row=r, column=1, value='Summary by geography (USD bn)').font = H2; r += 1
hdr(wf, r, ['Geography', '', '', '', 'CAGR 25-31', '', *[str(y) for y in years]]); r += 1
# geography tags per forecast row: derive from label
geo_of_row = {}
rr = ffirst
for spec in specs:
    lab = spec[0]
    g = 'Rest of world'
    if 'Europe' in lab: g = 'Europe'
    elif 'North America' in lab: g = 'North America'
    elif 'Asia-Pacific' in lab or 'China' in lab: g = 'Asia-Pacific'
    geo_of_row[rr] = g
    wf.cell(row=rr, column=16, value=g).font = NOTE
    rr += 1
FGEO = {}
for geo in ['North America', 'Europe', 'Asia-Pacific', 'Rest of world']:
    wf.cell(row=r, column=1, value=geo).font = BLACK
    for k in range(7):
        col = get_column_letter(7 + k)
        c = wf['%s%d' % (col, r)]; c.value = '=SUMIF($P$%d:$P$%d,"%s",%s$%d:%s$%d)' % (ffirst, flast, geo, col, ffirst, col, flast); c.font = BLACK; c.number_format = FMT_BN
    c = wf['E%d' % r]; c.value = '=(M%d/G%d)^(1/6)-1' % (r, r); c.number_format = FMT_PCT; c.font = BLACK
    FGEO[geo] = r
    r += 1
r += 1
wf.cell(row=r, column=1, value='Summary by component (USD bn): bus mix shifts to software per Inputs; rail mixes held constant').font = H2; r += 1
hdr(wf, r, ['Component', '', '', '', 'CAGR 25-31', '', *[str(y) for y in years]]); r += 1
FCOMP = {}
# bus software share by year: linear from bus_sw to bus_sw_2031; bus hw share = 1 - sw - services(0.201 constant = 1-bus_hw-bus_sw)
for lab in ['Hardware', 'Software', 'Services']:
    wf.cell(row=r, column=1, value=lab).font = BLACK
    for k in range(7):
        col = get_column_letter(7 + k)
        t = '(%s$4-$G$4)/6' % col
        bus_sw_t = '(%s+(%s-%s)*%s)' % (R['bus_sw'], R['bus_sw_2031'], R['bus_sw'], t)
        bus_svc = '(1-%s-%s)' % (R['bus_hw'], R['bus_sw'])
        if lab == 'Software':
            f = '=%s%d*%s+%s%d*%s+%s%d*%s' % (col, FSEG['Bus'], bus_sw_t, col, FSEG['Rail CCS'], R['ccs_sw'], col, FSEG['Rail other'], R['ro_sw'])
        elif lab == 'Services':
            f = '=%s%d*%s+%s%d*(1-%s-%s)+%s%d*(1-%s-%s)' % (col, FSEG['Bus'], bus_svc, col, FSEG['Rail CCS'], R['ccs_hw'], R['ccs_sw'], col, FSEG['Rail other'], R['ro_hw'], R['ro_sw'])
        else:
            f = '=%s%d*(1-%s-%s)+%s%d*%s+%s%d*%s' % (col, FSEG['Bus'], bus_sw_t, bus_svc, col, FSEG['Rail CCS'], R['ccs_hw'], col, FSEG['Rail other'], R['ro_hw'])
        c = wf['%s%d' % (col, r)]; c.value = f; c.font = BLACK; c.number_format = FMT_BN
    c = wf['E%d' % r]; c.value = '=(M%d/G%d)^(1/6)-1' % (r, r); c.number_format = FMT_PCT; c.font = BLACK
    FCOMP[lab] = r
    r += 1
wf.cell(row=r, column=1, value='Check: components sum to total (should be 0)').font = NOTE
for k in range(7):
    col = get_column_letter(7 + k)
    c = wf['%s%d' % (col, r)]; c.value = '=ROUND(SUM(%s%d:%s%d)-%s%d,6)' % (col, FCOMP['Hardware'], col, FCOMP['Services'], col, FSEG_TOTAL); c.font = NOTE; c.number_format = '0.000000'
r += 2
wf.cell(row=r, column=1, value='Scenario comparison (totals computed independently of the selector, USD bn)').font = H2; r += 1
hdr(wf, r, ['Scenario', '', '', '', 'CAGR 25-31', '', *[str(y) for y in years]]); r += 1
FSCEN = {}
for sidx, sname, scol in [(1, 'Low', 'B'), (2, 'Base', 'C'), (3, 'High', 'D')]:
    wf.cell(row=r, column=1, value=sname).font = BLACK
    for k in range(7):
        col = get_column_letter(7 + k)
        c = wf['%s%d' % (col, r)]; c.value = '=SUMPRODUCT($G$%d:$G$%d,(1+$%s$%d:$%s$%d)^(%s$4-$G$4))' % (ffirst, flast, scol, ffirst, scol, flast, col); c.font = BLACK; c.number_format = FMT_BN
    c = wf['E%d' % r]; c.value = '=(M%d/G%d)^(1/6)-1' % (r, r); c.number_format = FMT_PCT; c.font = BLACK
    FSCEN[sname] = r
    r += 1
wf.cell(row=r, column=1, value='Contestable pool by scenario (bus + rail other)').font = NOTE; r += 1
for sidx, sname, scol in [(1, 'Low', 'B'), (2, 'Base', 'C'), (3, 'High', 'D')]:
    wf.cell(row=r, column=1, value='Contestable: ' + sname).font = BLACK
    for k in range(7):
        col = get_column_letter(7 + k)
        c = wf['%s%d' % (col, r)]
        c.value = '=SUMPRODUCT(($O$%d:$O$%d<>"Rail CCS")*$G$%d:$G$%d*(1+$%s$%d:$%s$%d)^(%s$4-$G$4))' % (ffirst, flast, ffirst, flast, scol, ffirst, scol, flast, col)
        c.font = BLACK; c.number_format = FMT_BN
    c = wf['E%d' % r]; c.value = '=(M%d/G%d)^(1/6)-1' % (r, r); c.number_format = FMT_PCT; c.font = BLACK
    FSCEN['Contestable ' + sname] = r
    r += 1

# ----------------------------------------------------------------------------
# BOTTOM-UP NA
# ----------------------------------------------------------------------------
wb_ = wb.create_sheet('BottomUp_NA')
title(wb_, 'North America bottom-up cross-check: fleet x unit economics vs top-down', 'NTD report year 2025 (US) plus Statistics Canada 2024. Shows how much of the Berg-based top-down number a hardware-plus-core-software build explains.')
setw(wb_, [58, 16, 14, 70])
hdr(wb_, 4, ['Item', 'Value', 'Unit', 'Formula / note'])
r = 5
def brow(lab, f, unit, note, fmt=FMT_M, font=BLACK, bold=False):
    global r
    wb_.cell(row=r, column=1, value=lab).font = BOLD if bold else BLACK
    c = wb_.cell(row=r, column=2, value=f); c.font = font; c.number_format = fmt
    wb_.cell(row=r, column=3, value=unit).font = BLACK
    n = wb_.cell(row=r, column=4, value=note); n.font = NOTE; n.alignment = WRAP
    r += 1
    return r - 1
b_fleet = brow('North American full-size transit bus fleet (US active + Canada)', '=%s+%s' % (R['us_buses'], R['ca_buses']), 'vehicles', 'Inputs', FMT_INT, GREEN)
b_cad = brow('CAD/AVL full replacement, annualised', '=%s/%s' % (R['cad_full'], R['cad_cycle']), 'USD/bus/yr', 'USD 27k / 17 years (research/31_gap, 35_gap)', FMT_INT)
b_mid = brow('Mid-life refresh, annualised', '=%s/%s' % (R['midlife'], R['midlife_cycle']), 'USD/bus/yr', 'USD 10k / 10 years', FMT_INT)
b_vid = brow('Onboard video, annualised', '=%s/%s' % (R['video_per_bus'], R['video_cycle']), 'USD/bus/yr', 'USD 11k / 10 years', FMT_INT)
b_apc = brow('APC, annualised x coverage', '=%s/%s*%s' % (R['apc_per_bus'], R['apc_cycle'], R['apc_cov']), 'USD/bus/yr', 'USD 7.3k / 12 years x 60% coverage', FMT_INT)
b_capex = brow('Capex intensity per bus (sum of the four)', '=B%d+B%d+B%d+B%d' % (b_cad, b_mid, b_vid, b_apc), 'USD/bus/yr', 'sum', FMT_INT, bold=True)
b_rec = brow('Recurring vendor maintenance and hosting per bus', '=%s' % R['rec_per_bus'], 'USD/bus/yr', 'Inputs (median of 2023-26 renewals)', FMT_INT, GREEN)
b_saas = brow('Overlay SaaS and scheduling software per bus', '=%s' % R['saas_per_bus'], 'USD/bus/yr', 'Inputs', FMT_INT, GREEN)
b_int = brow('Onboard capex plus recurring intensity per bus', '=B%d+B%d+B%d' % (b_capex, b_rec, b_saas), 'USD/bus/yr', 'sum', FMT_INT)
b_all = brow('All-in intensity incl. wayside, depot and back-office adder', '=B%d*(1+%s)' % (b_int, R['wayside_adder']), 'USD/bus/yr', 'x (1 + adder)', FMT_INT, bold=True)
b_bu = brow('Bottom-up North America bus ITS spend', '=B%d*B%d/1e6' % (b_fleet, b_all), 'USD m', 'fleet x all-in intensity', FMT_M, bold=True)
b_td = brow('Top-down North America bus ITS, core (Berg ex-fare)', '=Market_2025!B6*1000', 'USD m', 'Market_2025', FMT_M, GREEN)
b_ratio = brow('Bottom-up as share of top-down', '=B%d/B%d' % (b_bu, b_td), '%', 'Residual = demand-response/paratransit fleets (not in the full-size bus count), enforcement cameras (USD 20-30k per bus-year on equipped buses), wayside PIS, Canadian programmes and fare content not fully removed. The research/31_gap bottom-up with all those items lands at USD 0.6-1.6bn (mid 1.0bn).', FMT_PCT, bold=True)
b_split = brow('Capex share of bottom-up intensity', '=B%d/B%d' % (b_capex, b_int), '%', 'research/31_gap: roughly 50% capex / 50% recurring', FMT_PCT)
r += 1
wb_.cell(row=r, column=1, value='NTD capital-expense floor (US only, capex only)').font = H2; r += 1
b_ntd = brow('NTD communication and information systems capex, bus modes 2025', '=%s' % R['ntd_ci_bus'], 'USD m', 'Inputs', FMT_M, GREEN)
b_ntd_pb = brow('per active full-size bus', '=B%d*1e6/%s' % (b_ntd, R['us_buses']), 'USD/bus/yr', 'NTD definition includes radio, AVL, dispatching, PA, operations software; excludes opex-funded SaaS and maintenance', FMT_INT)
b_us_td = brow('Top-down US share of North America bus ITS core (fleet-weighted)', '=B%d*%s/B%d' % (b_td, R['us_buses'], b_fleet), 'USD m', 'top-down NA x US fleet share', FMT_M)
brow('NTD bus capex floor as share of US top-down', '=B%d/B%d' % (b_ntd, b_us_td), '%', 'Capex-only proxy explains roughly a third; rest is opex-funded recurring, services and non-vehicle systems', FMT_PCT)
r += 1
wb_.cell(row=r, column=1, value='Rail (US) cross-check').font = H2; r += 1
b_rail = brow('NTD communication and information systems capex, rail modes 2025', '=%s' % R['ntd_ci_rail'], 'USD m', 'Includes cab signalling and train control; heavy rail 1,008m', FMT_M, GREEN)
brow('per active rail passenger vehicle', '=B%d*1e6/%s' % (b_rail, R['us_rail_cars']), 'USD/car/yr', 'NTD; dominated by signalling programmes (NYCT, WMATA, BART = 41% of total)', FMT_INT)
b_na_ccs = brow('Top-down North America passenger rail signalling (model)', '=(Market_2025!B%d+Market_2025!B%d)*1000' % (block_rows['Rail CCS urban'][3], block_rows['Rail CCS mainline'][3]), 'USD m', 'Market_2025 North America rows (US + Canada, incl. Amtrak/commuter)', FMT_M, GREEN)
brow('NTD rail capex as share of top-down NA signalling', '=B%d/B%d' % (b_rail, b_na_ccs), '%', 'Consistent once Canada (TTC, Metrolinx, STM), Amtrak and opex-funded maintenance are added', FMT_PCT)
r += 1
wb_.cell(row=r, column=1, value='Replacement wave (US buses)').font = H2; r += 1
b_wave = brow('Buses reaching useful-life benchmark 2026-2031', '=%s' % R['ulb_wave'], 'vehicles', 'Inputs (NTD RVI age vs agency ULB)', FMT_INT, GREEN)
b_back = brow('Buses already past benchmark (2025 backlog)', '=%s' % R['ulb_backlog'], 'vehicles', 'Inputs', FMT_INT, GREEN)
b_py = brow('Implied replacement candidates per year 2026-2031', '=(B%d+B%d)/6' % (b_wave, b_back), 'vehicles/yr', 'wave plus backlog over six years (vs ~4.5-4.9k heavy-duty deliveries/yr)', FMT_INT)
brow('Factory-fit onboard ITS pool per year', '=B%d*(%s+%s*%s)/1e6' % (b_py, R['video_per_bus'], R['apc_per_bus'], R['apc_cov']), 'USD m/yr', 'candidates x (video + APC x coverage); CAD/AVL units are transferred or bought under the platform contract', FMT_M, bold=True)
brow('Share of US fleet replaced over 2026-2031 at that pace', '=B%d*6/%s' % (b_py, R['us_buses']), '%', 'remaining ~45% of fleet addressed by mid-life retrofit', FMT_PCT)
b_coh = brow('Buses on 2009-2016 CAD/AVL platforms reaching 15-20 years in 2026-31', '=%s' % R['refresh_cohort'], 'buses', 'Inputs (research/31_gap)', FMT_INT, GREEN)
brow('Implied CAD/AVL full-replacement awards 2026-31 from that cohort', '=B%d*%s/1e6' % (b_coh, R['cad_full']), 'USD m', 'cohort x full replacement price (research/31_gap: USD 0.30-0.48bn at USD 25-40k)', FMT_M, bold=True)
brow('Incumbent win rate at competitive rebids of incumbent-held ITS systems (2016-26)', '=4/18', '%', '4 of 18 competitive rebids kept the incumbent; 0 of 8 in bus CAD/AVL; 64% of all 39 decision points stayed with the incumbent because 21 were extensions or sole-source renewals. research/35_gap.', FMT_PCT, bold=True)
r += 1
wb_.cell(row=r, column=1, value='US agency tiers by active full-size bus fleet (NTD 2025)').font = H2; r += 1
hdr(wb_, r, ['Tier', 'Agencies', 'Buses', 'Share of buses / comm and info capex per bus (3-yr avg, USD)']); r += 1
tiers = []
with open(os.path.join(DATA, 'ntd_2025_bus_tier_comm_info_capex_intensity.csv')) as fh:
    for rec in csv.DictReader(fh):
        if rec['tier_active_fullsize_bus'].startswith('0'): continue
        tiers.append(rec)
tfirst = r
for rec in tiers:
    wb_.cell(row=r, column=1, value=rec['tier_active_fullsize_bus']).font = BLACK
    c = wb_.cell(row=r, column=2, value=int(float(rec['agencies']))); c.font = BLUE; c.number_format = FMT_INT
    c = wb_.cell(row=r, column=3, value=int(float(rec['active_fullsize_bus']))); c.font = BLUE; c.number_format = FMT_INT
    c = wb_.cell(row=r, column=4, value='=TEXT(C%d/SUM($C$%d:$C$%d),"0.0%%")&" of fleet; USD "&TEXT(%s,"#,##0")&" per bus-year"' % (r, tfirst, tfirst + len(tiers) - 1, rec['capex_per_active_bus_avg_2023_2025_usd'])); c.font = BLACK
    r += 1
wb_.cell(row=r, column=1, value='Total').font = BOLD
c = wb_.cell(row=r, column=2, value='=SUM(B%d:B%d)' % (tfirst, r - 1)); c.font = BOLD; c.number_format = FMT_INT
c = wb_.cell(row=r, column=3, value='=SUM(C%d:C%d)' % (tfirst, r - 1)); c.font = BOLD; c.number_format = FMT_INT
wb_.cell(row=r, column=4, value='Source: NTD 2025 RVI (data/ntd_2025_bus_tier_comm_info_capex_intensity.csv). Top-50 agencies hold 58% of buses; 773 agencies have fewer than 50.').font = NOTE
r += 2
wb_.cell(row=r, column=1, value='Fuel mix of active US full-size buses (NTD 2025): diesel 53.6%, CNG 23.8%, hybrid 13.4%, battery-electric 4.4%, trolleybus 0.8%, hydrogen 0.3%, other 3.7%.').font = NOTE

# ----------------------------------------------------------------------------
# DRIVERS
# ----------------------------------------------------------------------------
wd = wb.create_sheet('Drivers')
title(wd, 'Growth drivers and headwinds to 2031, with the quantified evidence behind the CAGR assumptions', 'Direction: + tailwind, - headwind. Impact: H/M/L on the segment named.')
setw(wd, [34, 16, 9, 8, 56, 40])
hdr(wd, 4, ['Driver', 'Segment', 'Direction', 'Impact', 'Quantified evidence', 'Source (research file)'])
drivers = [
    ('Fleet replacement wave', 'Bus NA', '+', 'H', '24,143 US full-size buses reach useful-life benchmark 2026-31 on top of 12,644 already past it; bus rolling-stock capex USD 4.24bn in 2025 (+75% in two years); each new bus is a factory-fit for CAD/AVL, APC, cameras, signs', 'NTD 2025 (04, 16)'),
    ('Legacy CAD/AVL end of life', 'Bus NA/EU', '+', 'H', 'Systems installed 2004-2012 now replaced (LA Metro ATMS I 2004 to ATMS II 2025, USD 129.8m; TfL iBus 2009 to iBus2 2024, GBP 160m); ~12,000 US buses on 2009-16 platforms (TriMet, Denver, NJ Transit, Miami-Dade, Broward, AC Transit, Phoenix, TTC, King County, TransLink) reach 15-20 years in 2026-31 = USD 0.3-0.5bn of full-replacement awards; only 6% of 75+ surveyed agencies would strongly recommend their CAD/AVL (vendor-cited survey)', '11, 12, 13, 31_gap'),
    ('Zero-emission bus turnover', 'Bus EU/NA', '+', 'M', 'EU: 60% of city-bus registrations zero-emission in 2025 (11,607 BEBs, +48%); Clean Vehicles Directive 65% clean share 2026-30; US: 8,116 full-size ZEBs funded/ordered (+16%); e-bus ITS sub-market EUR 150m (2024) growing 21-27% p.a.', '05, 07, 17_gap'),
    ('AI enforcement and safety video', 'Bus', '+', 'M', 'MTA ACE from 123 (2019) to 1,900+ buses (2026), USD 141m contract, target 2,000+ by 2027; Hayden AI 2,500+ buses, 11 US agencies; FRA inward/outward cameras on lead locomotives by Oct 2027; self-funding via citations (NYC >400k tickets in five months)', '12, 13'),
    ('US federal funding reset', 'Bus/rail NA', '-', 'H', 'IIJA advance appropriations (USD 4.25bn/yr) lapsed 30 Sep 2026; extension to 11 Dec 2026 implies ~20% transit and ~82% rail cut while it runs; House bill -14% vs IIJA, no Low-No; FY2027 request -22%; formula funds (5307 +10% in House bill) favour refresh over expansion', '06, 25_gap'),
    ('State fiscal-cliff packages', 'Bus/rail NA', '+/-', 'M', 'Illinois USD 1.5bn/yr (NITA), Bay Area ~USD 1bn/yr for 14 years (RM, Nov 2026), NY MTA USD 68.4bn 2025-29 plan; Pennsylvania unresolved (SEPTA USD 192m structural deficit, capital raided for operations)', '06'),
    ('ERTMS/ETCS mandate', 'Rail EU', '+', 'H', 'EUR 75-85bn trackside + EUR 10-15bn onboard remaining to complete TEN-T; only ~10% (12,400 km) equipped and 19% of fleet fitted at end-2024; core km still to equip by 2030: 21,940 (Poland 3,742, Italy 2,993, Germany 2,694); EC unit cost ~EUR 850k/km incl. interlockings; non-US resignalling pipeline 2026-31 EUR 35.8bn base (EUR 20.6-54.7bn), 55-60% committed; EC: significantly behind schedule', '07, 36_gap'),
    ('Legacy metro resignalling (CBTC)', 'Rail urban', '+', 'H', 'NYC: 85% of subway still fixed-block; USD 5.4bn CBTC in 2025-29 plan (USD 20-45m per route-km); London Piccadilly/Bakerloo, Paris RER NExTEO EUR 300m framework, Toronto Line 2, Sydney, Copenhagen GoA4; SCI: ~90% of European CCS volume is modernisation', '12, 14, 21_gap'),
    ('Rail funding stretch-outs', 'Rail EU', '-', 'M', 'Network Rail CP7 ETCS portfolio cut from GBP 1.54bn to GBP 0.99bn; DB withdrew its 2024 ETCS migration strategy (summer 2025) citing vehicle fitment and federal funding uncertainty; China urban-rail investment -8.9% (2024)', '07, 14'),
    ('FRMCS / 5G telecom migration', 'Rail', '+', 'M', 'GSM-R end of support ~2035; FRMCS first edition in 2027 CCS TSI; DB migration 2026-35; SNCF Frequentis by 2030; onboard retrofit and ETCS Baseline 3 re-certification >= EUR 100k per vehicle', '13'),
    ('Predictive maintenance and digital twins', 'Rail other', '+', 'M', 'Hitachi HMAX on ~2,500 trains, on all new rolling stock from 2027; Siemens Railigent X; Alstom HealthHub inside 15-30 year service contracts; Konux ~6,000 assets', '09, 13'),
    ('Cybersecurity directives', 'Bus/rail', '+', 'M', 'TSA SDs renewed annually; proposed rule USD 3.09bn over 10 years, USD 1.26bn on passenger rail; TfL 2024 attack GBP 29m + GBP 10m lost income; UK DfT writes IEC 62443/TS 50701 into tenders', '06, 11'),
    ('Ridership recovery and service planning', 'Bus/rail', '+', 'L', 'US ridership 81% of 2019 in 2025 (+6%), still rising; demand-response trips +14% in 2024; real-time accuracy and scheduling tools in demand', '04, 06'),
    ('Agency capacity and procurement friction', 'All', '-', 'M', 'FTA staff -30% (791 to 553); 2-4 year award-to-live cycles; Buy America/BABA documentation for hardware; LA Metro needed USD 10.8m of outside programme support', '06, 11'),
    ('Asia-Pacific and Gulf build-out', 'Rail/bus RoW', '+', 'M', 'India ~1,000 km metro under construction, Kavach 5,000 route-km/yr target, CESL 17k e-buses tendered with bundled telematics; Riyadh Metro 176 km; China 5,833 km metro under construction but slowing', '05, 07'),
]
r = 5
for rec in drivers:
    for j, v in enumerate(rec):
        c = wd.cell(row=r, column=j + 1, value=v); c.font = BLACK; c.alignment = WRAP; c.border = BOX
    wd.row_dimensions[r].height = 62
    r += 1
r += 1
wd.cell(row=r, column=1, value='US federal transit funding series (FTA, USD bn)').font = H2; r += 1
hdr(wd, r, ['Fiscal year', 'FTA total', 'vs FY2026', '', 'Note']); r += 1
fy = [('FY2022', R['fta_2022']), ('FY2023', R['fta_2023']), ('FY2024', R['fta_2024']), ('FY2025', R['fta_2025']), ('FY2026', R['fta_2026']), ('FY2027 House bill (as authorised)', R['fta_2027_house']), ('FY2027 flat extension, no advance appropriations', R['fta_2027_ext']), ("FY2027 President's request", R['fta_2027_req'])]
f26 = None
for lab, ref in fy:
    wd.cell(row=r, column=1, value=lab).font = BLACK
    c = wd.cell(row=r, column=2, value='=%s' % ref); c.font = GREEN; c.number_format = FMT_BN
    if lab == 'FY2026': f26 = r
    r += 1
for rr in range(r - 8, r):
    c = wd.cell(row=rr, column=3, value='=B%d/$B$%d-1' % (rr, f26)); c.number_format = FMT_PCT; c.font = BLACK
wd.cell(row=r - 3, column=5, value='Scenario A: -5% vs FY2026 but -14% vs IIJA average (APTA)').font = NOTE
wd.cell(row=r - 2, column=5, value='Scenario B: current law if extensions continue; drives the Low case for North America').font = NOTE
wd.cell(row=r - 1, column=5, value='Scenario C: CIG cut 63%, no Low-No').font = NOTE

# ----------------------------------------------------------------------------
# COMPETITORS
# ----------------------------------------------------------------------------
wc = wb.create_sheet('Competitors')
title(wc, 'Key players: revenue, ownership, segment focus and recent moves', 'Revenue is the latest disclosed figure for the relevant unit; derived figures are marked. Shares are indicative against the model pools.')
setw(wc, [26, 14, 24, 30, 16, 12, 44, 30])
hdr(wc, 4, ['Company / unit', 'HQ', 'Ownership', 'Segment focus', 'Revenue (latest)', 'Margin', 'Position and 2024-26 moves', 'Source (research file)'])
comps = [
    ('Siemens Mobility (Rail Infrastructure)', 'Germany', 'Siemens AG (listed)', 'Rail signalling, interlockings, CBTC, software (Hacon, Sqills, Railigent X)', 'EUR ~4.1bn rail infra (derived); Mobility EUR 12.4bn', '8.8% (Mobility)', '~20% of world CCS; 44% of DB EUR 6.3bn DSD frameworks; buying MERMEC signalling/diagnostics (~EUR 430m revenue, 2026); backlog EUR 52bn', '09, 22_gap'),
    ('Hitachi Rail (incl. ex-Thales GTS, Clever Devices)', 'Japan/UK/Italy', 'Hitachi Ltd (listed)', 'Signalling, CBTC, mainline, HMAX digital, bus CAD/AVL (Clever)', 'JPY 1,321bn = EUR 7.8bn Mobility; ~52-60% signalling', '8.2% adj. EBITA', 'Largest signalling house; Thales GTS EUR 1.66bn (2024); Clever Devices (Jul 2026, >USD 220m revenue, 8 of top-10 NA agencies); backlog 5.4x revenue', '09, 22_gap'),
    ('Alstom Signalling', 'France', 'Alstom (listed)', 'CBTC (Urbalis), ETCS, interlockings, Mastria, HealthHub', 'EUR 2.7bn signalling; backlog EUR 9.8bn', 'double-digit (signalling); group 6.1%, H1 FY26/27 ~(4)%', '~13% of world CCS; 36% of CBTC projects by count; Nov 2026 profit warning and EUR 2bn deleveraging review incl. inorganic options', '09, 22_gap, 26_gap'),
    ('CRSC (China Railway Signal & Communication)', 'China', 'State-controlled (listed HK/SH)', 'Domestic HSR and metro train control', 'RMB 34.6bn = EUR 4.3bn; overseas 6.8%', '30% gross (control systems)', '~19% of world CCS, ~40% of Chinese urban-rail control; CASCO JV with Alstom (EUR 758m sales)', '22_gap'),
    ('Wabtec Digital Intelligence', 'US', 'Wabtec (listed)', 'PTC, locomotive electronics, Frauscher detection, inspection', 'USD 1.03bn (+31%)', '23% group adj. EBITDA', 'Freight-weighted; Frauscher ~USD 792m (2025), Evident USD 1.79bn, Dellner; PTC installed base on ~24,600 locomotives', '09, 22_gap'),
    ('KB Signaling (Knorr-Bremse)', 'US/Germany', 'Knorr-Bremse (listed)', 'North American conventional wayside signalling', 'EUR ~0.3bn', '~16% EBIT', 'Ex-Alstom Signaling NA bought for USD 690m (Sep 2024); MBTA, LA, Chicago', '22_gap'),
    ('Stadler / CAF Signalling', 'Switzerland / Spain', 'Listed', 'CBTC for own rolling-stock customers', 'Stadler Signalling CHF 118m; CAF n/d', 'n/d', 'New entrants via rolling-stock pull: Stadler MARTA USD 500m CBTC (2024); CAF Helsinki', '22_gap'),
    ('Modaxo (Constellation Software)', 'Canada', 'Constellation (listed), permanent capital', 'Bus CAD/AVL, scheduling, paratransit, fare (Trapeze, Vontas, Routeward, TripSpark, TransLoc, Routematch)', 'n/d (Conduent transit unit USD 371m at purchase)', 'n/d', '3,500+ customers, 33+ brands; bought Conduent Public Transit for USD 164m (Oct 2026, ~0.44x revenue); "never sells"', '08, 10, 18'),
    ('INIT SE', 'Germany', 'Listed (Xetra)', 'Integrated bus ITS, cloud, APC (iris, DILAX)', 'EUR 330m (+24%); 2026 guide EUR 380-410m', '9.9% EBIT (2025); FY26 cut to EUR 33-37m', 'Both regions; NA largest region (EUR 131m); TfL iBus2 GBP 160m; 2026 segments: Integrated Systems, Cloud, Passenger Intelligence', '08, 17, 26_gap'),
    ('Cubic Transportation Systems', 'US', 'Veritas / Evergreen (Elliott) since 2021', 'Fare systems, Umo, NextBus real-time', 'FY2019 USD 850m (last public)', '9.1% op. margin (FY2019)', 'LBO at 15.7x NTM EBITDA; ~USD 2.1bn debt, 2025 recap, Jan 2026 interest deferral; lost Miami/Sacramento to Masabi', '10, 26_gap'),
    ('IVU Traffic Technologies', 'Germany', 'Listed', 'Scheduling, dispatch, ticketing software (DACH)', 'EUR 150m; 2026 >EUR 160m', '12.4% EBIT', '52% recurring; trades 2.6x revenue / 15x EBITDA: market pays for software mix', '08, 26_gap'),
    ('Equans (Ineo), GMV, Indra, ETRA', 'France / Spain', 'Bouygues; private; listed', 'Bus and tram ITS integration in France, Iberia, LatAm, US (GMV Syncromatics)', 'n/d', 'n/d', 'Equans: Metrolinx, Brampton; GMV: LADOT USD 43m renewal', '08, 12'),
    ('Avail Technologies, GIRO, Hanover, Luminator, ETA, Passio', 'US / Canada / UK', 'Avail ESOP; GIRO founder-led; Hanover founder-owned; Luminator Audax PE (since 2014)', 'Mid-market CAD/AVL, scheduling (HASTUS), displays, onboard hardware', 'Hanover GBP 92.8m (2025, +28%, 362 staff; Companies House); others aggregator estimates only (+/-50%): Avail ~USD 25m, GIRO USD 25-115m, Passio USD 3-25m, ETA ~USD 6m', 'Hanover 17% operating margin, 58% gross', 'Ageing private assets = bolt-on pipeline; Luminator repositioning from hardware to digital (Sep 2026)', '08, 32_gap'),
    ('Swiftly', 'US', 'VC/growth (Cove Hill, JMI)', 'Real-time, analytics, now cloud CAD/AVL', 'n/d (200+ agencies)', 'n/d', 'Overlay on legacy CAD/AVL at 100+ agencies; cites survey that only 6% strongly recommend their CAD/AVL', '08, 13'),
    ('Optibus', 'Israel', 'VC (Insight, Bessemer, Pitango)', 'Scheduling, planning, EV scheduling, real-time suite', 'est. USD 60-75m ARR', 'n/d', 'USD 1.3bn valuation (2022); Carahsoft public-sector channel', '08, 10'),
    ('Via Transportation', 'US', 'NYSE (IPO Sep 2025)', 'On-demand, paratransit, planning (Remix), Citymapper', 'USD 434m (+29%); ARR USD 543m', '40% gross; adj. EBITDA ~breakeven Q4 2026', 'EV ~USD 2.75bn = 5.6x LTM revenue; 821 customers; targets fleets <250 vehicles', '10, 18, 26_gap'),
    ('Hayden AI', 'US', 'VC (TPG Rise, Drawdown)', 'AI bus-lane and bus-stop enforcement cameras', 'n/d', 'n/d', '2,500+ buses, 11 US agencies, MTA USD 141m contract; ~USD 400m post-money (2024)', '10, 13'),
    ('Samsara / Geotab (entrants)', 'US / Canada', 'Listed / private', 'Horizontal fleet telematics and safety video', 'Samsara USD 2.1bn ARR', 'n/d', 'Entering public fleets from municipal side; on CAD/AVL bidder lists (Vermont)', '13'),
]
r = 5
for rec in comps:
    for j, v in enumerate(rec):
        c = wc.cell(row=r, column=j + 1, value=v); c.font = BLACK; c.alignment = WRAP; c.border = BOX
    wc.row_dimensions[r].height = 64
    r += 1
r += 1
wc.cell(row=r, column=1, value='Indicative share arithmetic (formulas on Inputs; derived, directional only)').font = H2; r += 1
hdr(wc, r, ['Pool', 'Pool size (USD bn)', 'Vendor', 'Vendor revenue (USD bn)', 'Indicative share', '', 'Note']); r += 1
sh = [
    ('North America bus ITS core', '=Market_2025!B6', 'Clever Devices (Hitachi)', 0.22, 'Projected 2026 revenue; includes some rail/fare work'),
    ('North America bus ITS core', '=Market_2025!B6', 'INIT North America', '=0.131*%s' % R['fx'], 'EUR 130.8m 2025 NA revenue; includes fare'),
    ('Berg NA pool, fare-inclusive (EUR 1.22bn)', '=%s*%s' % (R['berg_na'], R['fx']), 'Modaxo (Trapeze legacy + Conduent transit)', '=0.402*%s' % R['fx'], 'research/32_gap share arithmetic on filed revenue with in-scope factors: Modaxo 33%, Clever/Hitachi 13%, INIT 9%, Cubic NA 9%, Luminator 7%; owner-level top-5 71%, 18 vendors = 92% of pool'),
    ('Berg Europe pool, fare-inclusive (EUR 2.55bn)', '=%s*%s' % (R['berg_eu'], R['fx']), 'INIT Europe (largest identifiable vendor)', '=0.156*%s' % R['fx'], 'research/32_gap: largest vendor 6%; top-5 21%, top-10 30%; 24 identifiable vendors cover 40%, leaving ~EUR 1.5bn to national integrators and the long tail'),
    ('World passenger rail signalling', '=Market_2025!B%d' % CCS_ROW, 'Siemens Mobility Rail Infrastructure', '=4.1*%s' % R['fx'], 'Derived ~33% of Mobility; includes electrification and freight'),
    ('World passenger rail signalling', '=Market_2025!B%d' % CCS_ROW, 'Alstom Signalling', '=2.7*%s' % R['fx'], 'FY2025/26; includes freight'),
    ('World passenger rail signalling', '=Market_2025!B%d' % CCS_ROW, 'Hitachi Rail signalling and systems', '=7.8*0.55*%s' % R['fx'], '~52-60% of Mobility sector revenue'),
]
for lab, pool, vend, rev, note in sh:
    wc.cell(row=r, column=1, value=lab).font = BLACK
    c = wc.cell(row=r, column=2, value=pool); c.font = GREEN; c.number_format = FMT_BN
    wc.cell(row=r, column=3, value=vend).font = BLACK
    c = wc.cell(row=r, column=4, value=rev); c.font = BLUE if not str(rev).startswith('=') else BLACK; c.number_format = FMT_BN
    c = wc.cell(row=r, column=5, value='=D%d/B%d' % (r, r)); c.number_format = FMT_PCT; c.font = BLACK
    wc.cell(row=r, column=7, value=note).font = NOTE
    r += 1

# ----------------------------------------------------------------------------
# DEALS AND COMPS
# ----------------------------------------------------------------------------
wdl = wb.create_sheet('Deals_Comps')
title(wdl, 'Transactions and trading multiples', 'Disclosed values only; multiples derived where revenue/EBITDA are public. Observed trading data as of 6 Nov 2026 (research/26_gap).')
setw(wdl, [16, 30, 26, 16, 14, 14, 44, 18])
hdr(wdl, 4, ['Date', 'Target', 'Acquirer / investor', 'Value', 'EV/Revenue', 'EV/EBITDA', 'Note', 'Source file'])
deals = [
    ('May 2021', 'Cubic Corp (take-private)', 'Veritas Capital / Evergreen (Elliott)', 'USD ~2.8bn EV at the USD 70 offer; closed at USD 75/share, ~USD 3.0bn', '~1.9x FY2020 sales (at 2.8bn); ~2.0x at 3.0bn', '15.7x NTM at USD 70 (Raymond James); ~16.5x at close', 'USD 1.8bn funded debt (~11x FY2020 adj. EBITDA); 2025 recap; three straight quarterly interest deferrals to Jul 2026; Fitch CC (Aug 2026), Moody\'s Ca on term loans; Cubic UK lost TfL contract (Jul 2025)', '10, 18, 26_gap, 32_gap, 90_verification c26'),
    ('May 2024', 'Thales Ground Transportation Systems', 'Hitachi Rail', 'EUR 1,660m', '~0.7x FY2025 ex-GTS revenue (EUR 2.3bn); standalone Thales GTS revenue at signing not retrievable', 'n/d', 'Ex-GTS generated JPY 391bn (EUR 2.3bn) at 11.4% EBITA in FY2025; remedy sale of mainline units to MERMEC', '09, 22_gap'),
    ('Sep 2024', 'Alstom Signaling North America', 'Knorr-Bremse', 'USD 690m', '~2.1x (EUR 300m revenue at 1.08)', 'n/d', '~EUR 300m revenue, ~16% EBIT; conventional wayside', '22_gap'),
    ('Dec 2025', 'Frauscher (train detection)', 'Wabtec', 'USD ~792m', 'n/d', 'n/d', 'Axle counters and wheel sensors', '09, 22_gap'),
    ('Jul 2025', 'Evident Inspection Technologies', 'Wabtec', 'USD 1,788m', 'n/d', '15.9x CY24', 'Adjacent inspection', '10'),
    ('May 2026', 'MERMEC signalling and diagnostics businesses', 'Siemens Mobility', 'undisclosed', 'n/d', 'n/d', '~EUR 430m FY25 revenue, 1,700 staff', '22_gap'),
    ('Jul 2026', 'Clever Devices', 'Hitachi Rail', 'undisclosed', 'n/d', 'n/d', 'Projected 2026 revenue >USD 220m (the USD 220m figure is revenue, not price); 8 of top-10 NA agencies', '08, 10, 34_gap'),
    ('Oct 2026', 'Conduent Public Transit (Novvan, Routeward)', 'Modaxo / Constellation Software', 'USD 164m', '~0.44x', 'n/d', 'Unit revenue USD 371m (2025) incl. fare collection; 2,000 staff', '08, 18'),
    ('Jan 2025', 'Flowbird', 'EasyPark Group (Arrive)', 'undisclosed', 'n/d', 'n/d', 'Fare and parking (adjacent)', '10'),
    ('2024', 'Safe Fleet (incl. Seon)', 'Clarience / Genstar', 'undisclosed', 'n/d', 'n/d', 'Onboard video', '08'),
    ('Sep 2025', 'Via Transportation IPO', 'Public markets (NYSE)', 'USD 3.65bn headline', '~10.8x trailing at IPO; 5.6x LTM (USD 492m) / 6.3x FY2025 (USD 434m) now', 'n.m.', 'FY2025 revenue USD 434m (+29%), adj. EBITDA -8%; EV ~USD 2.75bn (6 Nov 2026)', '10, 26_gap'),
    ('May 2022', 'Optibus Series D', 'Insight, Bessemer, Pitango', 'USD 100m at USD 1.3bn', 'n/d (est. 15-20x ARR)', 'n.m.', 'First public-transport unicorn', '10'),
    ('Jul 2024', 'Hayden AI Series C', 'TPG Rise Fund', 'USD 90m (~USD 400m post)', 'n/d', 'n.m.', 'AI enforcement', '10'),
    ('May 2025', 'Swiftly growth round', 'Cove Hill, JMI', 'undisclosed', 'n/d', 'n.m.', 'Acquired Hopthru (2024), TextMarks (2026)', '08'),
    ('Sep 2024', 'INIT acquires DILAX', 'INIT SE', 'undisclosed', 'n/d', 'n/d', '~EUR 20m revenue APC specialist', '08'),
    ('Nov 2024', 'Iteris', 'Almaviva', 'USD ~335m', '~1.9x', 'n/d', 'Adjacent roadway ITS', '10'),
]
r = 5
for rec in deals:
    for j, v in enumerate(rec):
        c = wdl.cell(row=r, column=j + 1, value=v); c.font = BLACK; c.alignment = WRAP; c.border = BOX
    wdl.row_dimensions[r].height = 42
    r += 1
r += 1
wdl.cell(row=r, column=1, value='Trading multiples, observed 6 Nov 2026 (EV / LTM)').font = H2; r += 1
hdr(wdl, r, ['Bucket', 'Company', 'EV/Revenue', 'EV/EBITDA', 'Growth', 'Margin', 'Read-across', '']); r += 1
tm = [
    ('Transit ITS integrator', 'INIT SE (EV EUR 0.38bn)', '1.0x', '7.0x', '+24% (2025)', '9.9% EBIT', 'De-rated after Nov 2026 EBIT cut; project/hardware mix'),
    ('Transit ITS software', 'IVU Traffic Technologies (EV EUR 0.43bn)', '2.6x', '15.2x', '+10%', '12.4% EBIT', 'Software premium inside the integrator bucket (52% recurring)'),
    ('Transit SaaS', 'Via Transportation', '5.6x', 'n.m.', '+27-29%', '-8% adj. EBITDA', 'Loss-making growth; 18% below IPO price'),
    ('Horizontal fleet SaaS', 'Samsara', '12.3x', 'n.m.', '+30%', 'n/d', 'Ceiling for software multiples'),
    ('Rail OEM / signalling', 'Siemens AG', '3.1x', '17.9x', 'n/d', '8.3% (Mobility)', 'Valued on backlog and margin quality'),
    ('Rail OEM / signalling', 'Alstom', '0.33x', '4.2x (stale)', 'n/d', '~1% FY guidance', 'Distressed; carve-out candidate'),
    ('Rail OEM / signalling', 'Wabtec', '4.4x', '19.0x', 'n/d', '23.2% adj. EBITDA', 'Freight-weighted; Transit segment 13.5% margin'),
    ('Rail OEM / signalling', 'Hitachi Ltd', '1.7x', '10.6x', 'n/d', '8.2% (Mobility EBITA)', 'Group multiple'),
    ('Software consolidator', 'Constellation Software (Modaxo parent)', '4.4x', '22.7x', '+19% (M&A-led)', 'n/d', 'Permanent-capital buyer at 0.4-1x revenue'),
    ('Adjacent enforcement/tolling', 'Verra Mobility', '1.2x', '3.1x', 'flat', '42% adj. EBITDA', 'Customer-concentration shock (Avis)'),
    ('Adjacent tolling/traffic', 'Kapsch TrafficCom', '0.4x', 'n.m.', '-19%', '1.8% EBIT', 'Covenant breach, standstill'),
]
for rec in tm:
    for j, v in enumerate(rec):
        c = wdl.cell(row=r, column=j + 1, value=v); c.font = BLACK; c.alignment = WRAP; c.border = BOX
    r += 1

# ----------------------------------------------------------------------------
# BENCHMARKS (contract awards)
# ----------------------------------------------------------------------------
wbm = wb.create_sheet('Benchmarks')
title(wbm, 'Public contract awards 2003-2026: unit-economics benchmarks', 'From research/12 and gap-fill 31/35 (data/contract_benchmarks.csv). Value per unit computed where fleet or km disclosed.')
setw(wbm, [7, 30, 8, 22, 44, 26, 12, 8, 10, 24, 14, 50])
hdr(wbm, 4, ['Year', 'Agency', 'Country', 'Segment', 'Product / scope', 'Vendor', 'Value USD m', 'Term (yrs)', 'Units', 'Unit type', 'USD per unit', 'Source URL'])
r = 5
with open(os.path.join(DATA, 'contract_benchmarks.csv')) as fh:
    recs = list(csv.DictReader(fh))
def num(x):
    try: return float(x)
    except: return None
recs.sort(key=lambda d: (-(num(d['year']) or 0)))
for d in recs:
    vals = [num(d['year']), d['agency'], d['country'], d['segment'], d['product'], d['vendor'], num(d['value_usd_m']), num(d['term_years']), num(d['units']), d['unit_type'], None, d['source_url']]
    for j, v in enumerate(vals):
        c = wbm.cell(row=r, column=j + 1, value=v); c.font = BLUE if j in (0, 6, 7, 8) else BLACK; c.alignment = WRAP
        if j == 0: c.number_format = '0'
        if j == 6: c.number_format = '#,##0.0'
        if j == 8: c.number_format = FMT_INT
    c = wbm.cell(row=r, column=11, value='=IF(AND(ISNUMBER(G%d),ISNUMBER(I%d),I%d>0),G%d*1000000/I%d,"")' % (r, r, r, r, r)); c.font = BLACK; c.number_format = FMT_INT
    wbm.row_dimensions[r].height = 30
    r += 1
BENCH_LAST = r - 1
r += 1
wbm.cell(row=r, column=1, value='Summary statistics by segment (clean single-scope rows with disclosed units)').font = H2; r += 1
hdr(wbm, r, ['', 'Segment', '', 'Rows with unit value', '', '', 'Median USD/unit', '', 'Min', 'Max']); r += 1
for seg in ['Roadway (bus)', 'Railway (metro)', 'Railway (mainline)', 'Railway (commuter)']:
    wbm.cell(row=r, column=2, value=seg).font = BLACK
    c = wbm.cell(row=r, column=4, value='=COUNTIFS($D$5:$D$%d,"%s",$K$5:$K$%d,">0")' % (BENCH_LAST, seg, BENCH_LAST)); c.font = BLACK; c.number_format = FMT_INT
    c = wbm.cell(row=r, column=7, value='=IFERROR(MEDIAN(IF(($D$5:$D$%d="%s")*($K$5:$K$%d>0),$K$5:$K$%d)),"")' % (BENCH_LAST, seg, BENCH_LAST, BENCH_LAST)); c.font = BLACK; c.number_format = FMT_INT
    c = wbm.cell(row=r, column=9, value='=IFERROR(MIN(IF(($D$5:$D$%d="%s")*($K$5:$K$%d>0),$K$5:$K$%d)),"")' % (BENCH_LAST, seg, BENCH_LAST, BENCH_LAST)); c.font = BLACK; c.number_format = FMT_INT
    c = wbm.cell(row=r, column=10, value='=IFERROR(MAX(IF(($D$5:$D$%d="%s")*($K$5:$K$%d>0),$K$5:$K$%d)),"")' % (BENCH_LAST, seg, BENCH_LAST, BENCH_LAST)); c.font = BLACK; c.number_format = FMT_INT
    r += 1
wbm.cell(row=r, column=2, value='Unit types differ across rows (vehicles, route-km, track-km, stations); read the unit-type column before comparing. Array formulas above are entered as CSE in Excel; LibreOffice evaluates them natively.').font = NOTE
# mark array formulas for the MEDIAN/MIN/MAX cells
from openpyxl.worksheet.formula import ArrayFormula
for rr in range(r - 4, r):
    for col in ['G', 'I', 'J']:
        cell = wbm['%s%d' % (col, rr)]
        cell.value = ArrayFormula('%s%d' % (col, rr), cell.value)

# ----------------------------------------------------------------------------
# RISKS
# ----------------------------------------------------------------------------
wr = wb.create_sheet('Risks')
title(wr, 'Risk register and barriers to entry', 'Likelihood and impact scored 1-5 (analyst judgement); score = likelihood x impact. Mitigants are what a new entrant can do.')
setw(wr, [30, 10, 8, 8, 8, 56, 44, 14])
hdr(wr, 4, ['Risk / barrier', 'Type', 'Likelihood', 'Impact', 'Score', 'Evidence', 'Mitigant for a new entrant', 'Source file'])
risks = [
    ('Tenure: incumbent-held systems reach a decision point only after a median 16 years', 'Barrier', 5, 5, '64% of 39 decision points (2016-26) stayed with the incumbent, but 21 of those were extensions or sole-source renewals; at competitive rebids incumbents won only 4 of 18 (0 of 8 in bus CAD/AVL). LA Metro ATMS 2004-25; TfL iBus 2009-24; INIT contracts up to 20 years; Modaxo never sells', 'The barrier is tenure, not rebid odds: coexist-then-displace with overlays; buy an installed base to own the service tail; be pilot-ready (2-6 bidders per RFP, pilots before award)', '11, 17, 18, 35_gap'),
    ('Public procurement cycle and protests', 'Barrier', 5, 4, '2-4 years award-to-live; 2 CFR 200 competition rules; LA Metro 2016 plan to 2028 go-live; awards subject to protest', 'Cooperative purchasing (Sourcewell, state contracts), distributors (Carahsoft), pilot-to-scale', '11'),
    ('Rail safety certification and four-player signalling oligopoly (three ex-China)', 'Barrier', 5, 5, 'SIL-4, ERA/FRA type approval, 25-30 year service tails; Siemens, Hitachi, Alstom, CRSC each 13-22% of world CCS, big three ~two-thirds ex-China; 10-30 year frameworks', 'Avoid signalling cores; target adjacencies (condition monitoring, cyber, telecom migration, onboard)', '09, 12, 22_gap'),
    ('US federal funding reset', 'Market', 4, 4, 'IIJA advance appropriations lapsed; CR implies ~20% transit cut; House bill -14%; FTA staff -30%', 'Sell opex-light SaaS with fast payback; weight toward formula-funded refresh and state-funded agencies', '06, 25_gap'),
    ('SaaS eligibility under 80/20 capital grants', 'Market', 3, 3, '49 USC 5302 capital definition covers leasing and preventive maintenance; FTA declined to add SaaS guidance (2025); House bill would add explicit SaaS clause', 'Structure subscriptions as leases/preventive maintenance; track H.R. 8870', '17, 25_gap'),
    ('ERTMS and resignalling slippage', 'Market', 4, 3, 'EC: deployment significantly behind schedule; UK CP7 ETCS cut 35%; DB withdrew 2024 migration strategy; Kavach dates slipped', 'Phase revenue on committed frameworks, not plans', '07, 14'),
    ('Buy America / BABA for hardware', 'Barrier', 4, 3, '>70% domestic content and US final assembly for rolling-stock-related equipment; 55% for manufactured products; OIG scrutiny', 'Software-led entry; US contract manufacturing partner (INIT runs two Virginia plants)', '11'),
    ('Cybersecurity compliance and incidents', 'Both', 4, 3, 'TSA rule USD 1.26bn/10 years on passenger rail; TfL 2024 GBP 39m impact; TTC 2021 ransomware took down CAD/AVL', 'Certify early (ISO 27001, SOC 2, IEC 62443); sell cyber as a service line', '06, 11'),
    ('Agency capacity and long tail', 'Market', 4, 3, '772 US agencies with <50 buses hold 16% of fleet; FTA and agency staffing shortages; LA Metro paid USD 10.8m for programme support', 'Low-touch, hosted, templated delivery; state-level deals', '04, 11'),
    ('Hardware tariffs and supply', 'Market', 3, 2, '2025-26 tariff whipsaw (China 145% to 10%; steel 50%); INIT margin miss partly tariff-driven', 'Asset-light; hardware partners carry inventory risk', '11'),
    ('Leverage in hardware-heavy integrators', 'Investment', 3, 4, 'Cubic LBO ~11x EBITDA debt; Moody\'s B3 (2021) to Caa2/Ca; Fitch CC (Aug 2026) after a third straight quarterly interest deferral; Cubic UK lost the TfL revenue-collection contract (Jul 2025); Alstom profit warning; Kapsch standstill', 'Do not lever project businesses; underwrite on recurring revenue only', '10, 26_gap'),
    ('Supplier failure and counterparty scrutiny', 'Market', 2, 3, 'Proterra Chapter 11 (2023), Nova Bus US exit; tenders now weigh financial capacity and escrow', 'Balance-sheet strength, continuity terms, escrowed code', '11'),
    ('Political re-labelling of projects', 'Market', 3, 2, 'Grant conditions enjoined (Nov 2025); Low-No pivot to low-emission; DEI/climate labels removed', 'Position on safety, efficiency and reliability outcomes', '06'),
]
r = 5
rfirst = r
for rec in risks:
    lab, typ, L, I, ev, mit, src = rec
    wr.cell(row=r, column=1, value=lab).font = BLACK
    wr.cell(row=r, column=2, value=typ).font = BLACK
    c = wr.cell(row=r, column=3, value=L); c.font = BLUE
    c = wr.cell(row=r, column=4, value=I); c.font = BLUE
    c = wr.cell(row=r, column=5, value='=C%d*D%d' % (r, r)); c.font = BLACK
    for j, v in [(6, ev), (7, mit), (8, src)]:
        c = wr.cell(row=r, column=j, value=v); c.font = BLACK; c.alignment = WRAP
    for j in range(1, 9): wr.cell(row=r, column=j).border = BOX
    wr.row_dimensions[r].height = 48
    r += 1

# ----------------------------------------------------------------------------
# THESIS: illustrative buy-and-build bridge and target long-list
# ----------------------------------------------------------------------------
wth = wb.create_sheet('Thesis')
title(wth, 'Investment thesis support: illustrative buy-and-build value bridge and target long-list', 'Illustrative only; inputs on the Inputs sheet (blue). Not a valuation.')
setw(wth, [56, 16, 12, 70])
hdr(wth, 4, ['Item', 'Value', 'Unit', 'Formula / note'])
r = 5
def trow(lab, f, unit, note, fmt=FMT_M, bold=False, font=BLACK):
    global r
    wth.cell(row=r, column=1, value=lab).font = BOLD if bold else BLACK
    c = wth.cell(row=r, column=2, value=f); c.font = font; c.number_format = fmt
    wth.cell(row=r, column=3, value=unit).font = BLACK
    n = wth.cell(row=r, column=4, value=note); n.font = NOTE; n.alignment = WRAP
    r += 1; return r - 1
t_rev0 = trow('Entry revenue', '=%s' % R['vb_rev0'], 'USD m', 'Inputs', FMT_M, font=GREEN)
t_ev0 = trow('Entry enterprise value', '=B%d*%s' % (t_rev0, R['vb_mult0']), 'USD m', 'revenue x EV/revenue')
t_ebitda0 = trow('Entry EBITDA', '=B%d*%s' % (t_rev0, R['vb_margin0']), 'USD m', 'revenue x margin')
t_debt0 = trow('Net debt at entry', '=B%d*%s' % (t_ebitda0, R['vb_lev']), 'USD m', 'EBITDA x leverage')
t_eq0 = trow('Equity invested at entry', '=B%d-B%d' % (t_ev0, t_debt0), 'USD m', 'EV - net debt', bold=True)
t_bolt = trow('Bolt-on acquisitions (EV paid)', '=%s*%s' % (R['vb_bolt'], R['vb_boltmult']), 'USD m', 'bolt-on revenue x multiple; assumed equity-funded')
t_rev1 = trow('Exit revenue', '=B%d*(1+%s)^%s+%s' % (t_rev0, R['vb_g'], R['vb_hold'], R['vb_bolt']), 'USD m', 'organic compounding plus bolt-on revenue')
t_ebitda1 = trow('Exit EBITDA', '=B%d*%s' % (t_rev1, R['vb_margin1']), 'USD m', 'exit revenue x exit margin')
t_ev1 = trow('Exit enterprise value', '=B%d*%s' % (t_ebitda1, R['vb_mult1']), 'USD m', 'EBITDA x EV/EBITDA')
t_evrev = trow('Implied exit EV / revenue', '=B%d/B%d' % (t_ev1, t_rev1), 'x', 'cross-check against SaaS 5-6x and integrator 1-2.6x bands', FMT_X)
t_debt1 = trow('Net debt at exit (assumes cash flow repays half of entry debt)', '=B%d*0.5' % t_debt0, 'USD m', 'simplifying assumption')
t_eq1 = trow('Equity value at exit', '=B%d-B%d' % (t_ev1, t_debt1), 'USD m', 'EV - net debt', bold=True)
t_moic = trow('Gross MOIC (exit equity / (entry equity + bolt-on EV))', '=B%d/(B%d+B%d)' % (t_eq1, t_eq0, t_bolt), 'x', 'before fees and carry', FMT_X, bold=True)
trow('Gross IRR', '=B%d^(1/%s)-1' % (t_moic, R['vb_hold']), '%', 'over the hold period', FMT_PCT, bold=True)
r += 1
wth.cell(row=r, column=1, value='Target long-list (private mid-market bus ITS vendors; revenue to be confirmed in diligence)').font = H2; r += 1
hdr(wth, r, ['Company', 'Ownership / stage', 'Fit', 'What is known (research file)']); r += 1
targets = [
    ('Avail Technologies (US)', 'Employee-owned (ESOP, 67% moving to 100%); new CEO 2025', 'CAD/AVL and ITS for mid-size US agencies; largest real-time feed footprint among NA vendors (GTFS-RT census); won TARC 2023', 'Founded 1999; PennDOT statewide contract; aggregator revenue estimate ~USD 25m (+/-50%) (08, 32_gap, 33_gap)'),
    ('GIRO (Canada)', 'Founder-led since the 1970s', 'HASTUS scheduling in 30+ countries; licence/support USD 0.2-0.8k per bus-year plus USD 1.4-4.6k upgrades every 7-10 years', 'Aggregator revenue estimates USD 25-115m, unreliable (08, 32_gap)'),
    ('Hanover Displays (UK)', 'Founder-owned (D G Williams), 40 years', 'Onboard displays and signage in 80+ countries; the best filed P&L in the set; hardware channel partner or bolt-on', 'Turnover GBP 92.8m (2025, +28% after +28% and +23%), operating profit GBP 15.7m (17%), gross margin 58%, 362 staff (Companies House, 32_gap)'),
    ('ETA Transit Systems (US)', 'Private, founder-owned', 'CAD/AVL and real-time for small and mid-size agencies', 'Founded 2003; revenue n/d (08)'),
    ('Passio Technologies / Ecolane (US)', 'Private (Transit Technologies LLC)', 'Real-time and paratransit software for the long tail', 'Passio 23 providers / 66 feeds in GTFS-RT census (33_gap)'),
    ('Luminator Technology Group (US)', 'Audax Private Equity with BNP Paribas Developpement (since Apr 2014)', 'Displays, video and infotainment; repositioning to digital partner (Sep 2026); ~7% of the NA pool (32_gap)', 'Group revenue n/d; Nordic arm LTG Sweden SEK 280m (+63%) (32_gap)'),
]
for rec in targets:
    for j, v in enumerate(rec):
        c = wth.cell(row=r, column=j + 1, value=v); c.font = BLACK; c.alignment = WRAP; c.border = BOX
    wth.row_dimensions[r].height = 34
    r += 1

# ----------------------------------------------------------------------------
# final: fonts on headers, freeze panes, save
# ----------------------------------------------------------------------------
for s in wb.worksheets:
    s.freeze_panes = 'A5' if s.title not in ('README',) else None
    s.sheet_view.showGridLines = False
wb.save(OUT)
print('saved', OUT)
# export registry for the deck builder
import json
json.dump({'inputs': R, 'market_total_row': TOTAL_ROW, 'seg_rows': seg_rows, 'contest_row': CONTEST_ROW, 'ccs_row': CCS_ROW, 'comp_rows': COMP_ROWS, 'geo_rows': GEO_ROWS,
           'tier_rows': TIER_ROWS, 'open_rows': OPEN_ROWS, 'app_rows': APP_ROWS, 'sens_rows': SENS_ROWS,
           'thesis': {'rev0': t_rev0, 'ev0': t_ev0, 'eq0': t_eq0, 'bolt': t_bolt, 'rev1': t_rev1, 'ebitda1': t_ebitda1, 'ev1': t_ev1, 'evrev': t_evrev, 'eq1': t_eq1, 'moic': t_moic},
           'forecast': {'seg': FSEG, 'seg_total': FSEG_TOTAL, 'contest': FCONTEST, 'sam': FSAM, 'bridge': BRIDGE, 'geo': FGEO, 'comp': FCOMP, 'scen': FSCEN, 'first': ffirst, 'last': flast}},
          open(os.path.join(HERE, 'model_map.json'), 'w'), indent=1)
