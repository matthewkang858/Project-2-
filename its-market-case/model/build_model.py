"""Build the Public ITS market model (live-formula Excel workbook) with openpyxl.

Run:  python3 build_model.py   -> writes Public_ITS_Market_Model.xlsx next to this script.
Then recalculate it with LibreOffice (recalc.py) and run export_values.py to write deck_data.json.

Four sheets, one per quantitative slide:
  README   how to read the model, calculation chain, slide map, sources (text only)
  Market   2025 market size and funnel                       (slide 3, slide 2, appendix A2)
  Growth   market growth 2025-2031E, low / base / high       (slide 4, slide 2, appendix A3)
  Returns  illustrative buy-and-build value bridge           (slide 7, slide 2, appendix A4)

Colours: blue = hard-coded input, black = formula on the same sheet, green = formula that links to another sheet.
The font colour of every number cell is chosen from its content (number -> blue; formula with '!' -> green; other formula -> black),
so the colour code cannot drift from the cell contents.
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter, column_index_from_string

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'Public_ITS_Market_Model.xlsx')

# ----------------------------------------------------------------------------
# Styles (same objects as the previous builder)
# ----------------------------------------------------------------------------
F_BASE = 'Arial'
BLUE = Font(name=F_BASE, size=10, color='0000FF')
BLACK = Font(name=F_BASE, size=10, color='000000')
GREEN = Font(name=F_BASE, size=10, color='008000')
BOLD = Font(name=F_BASE, size=10, bold=True, color='000000')
TITLE = Font(name=F_BASE, size=14, bold=True, color='1B2A41')
H2 = Font(name=F_BASE, size=11, bold=True, color='1B2A41')
HDR = Font(name=F_BASE, size=10, bold=True, color='FFFFFF')
NOTE = Font(name=F_BASE, size=9, italic=True, color='4F6D7A')
HDR_FILL = PatternFill('solid', fgColor='1B2A41')
SUB_FILL = PatternFill('solid', fgColor='EEF2F5')
THIN = Side(style='thin', color='C7D3DA')
BOX = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')
TOP = Alignment(vertical='top')
HDR_ALIGN = Alignment(wrap_text=True, vertical='center')

# Number formats by unit
F_BN = '0.00'        # USD B or EUR B inputs (also USD per EUR) and the Growth sheet
F_BN3 = '0.000'      # Market build and funnel rows: a third decimal, so the slides' one-decimal rounding can be read off (6.246 -> $6.2)
F_M = '0.0'          # USD M
F_X = '0.00"x"'      # multiples
F_X1 = '0.0"x"'      # gross MOIC rows, shown at the precision the slides print
F_INT = '0'          # years and index
F_PCT = '0.0%'       # shares and CAGRs (stored as fractions)
F_PCT0 = '0%'        # share of increase
F_CHK = '0.000'      # checks


def number_font(value, bold=False):
    """Blue for a hard-coded number, green for a cross-sheet formula, black for a same-sheet formula."""
    if isinstance(value, str) and value.startswith('='):
        font = GREEN if '!' in value else BLACK
    else:
        font = BLUE
    return Font(name=F_BASE, size=10, color=font.color.rgb, bold=True) if bold else font


class Sheet:
    """Thin wrapper that writes cells in the house style."""

    def __init__(self, ws, widths, wrap_cols=()):
        self.ws = ws
        self.wrap_cols = set(wrap_cols)
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
        ws.sheet_view.showGridLines = False

    def text(self, ref, value, font=BLACK, border=True):
        c = self.ws[ref]
        c.value = value
        c.font = font
        col = ''.join(ch for ch in ref if ch.isalpha())
        c.alignment = WRAP if col in self.wrap_cols else TOP
        if border:
            c.border = BOX
        return c

    def num(self, ref, value, fmt, bold=False):
        c = self.ws[ref]
        c.value = value
        c.font = number_font(value, bold)
        c.number_format = fmt
        c.alignment = TOP
        c.border = BOX
        return c

    def title(self, text, note):
        self.ws['A1'] = text
        self.ws['A1'].font = TITLE
        self.ws['A2'] = note
        self.ws['A2'].font = NOTE

    def header(self, row, labels, text_fmt_cols=()):
        for j, t in enumerate(labels):
            c = self.ws.cell(row=row, column=j + 1, value=t)
            c.font = HDR
            c.fill = HDR_FILL
            c.alignment = HDR_ALIGN
            c.border = BOX
            if get_column_letter(j + 1) in text_fmt_cols:
                c.number_format = '@'

    def section(self, row, text, last_col):
        for j in range(1, column_index_from_string(last_col) + 1):
            self.ws.cell(row=row, column=j).fill = SUB_FILL
        c = self.ws.cell(row=row, column=1, value=text)
        c.font = H2

    def finish(self, freeze='B5', paper='A4'):
        # Row heights are left to the LibreOffice recalculation, which sets each row to fit its wrapped text.
        if freeze:
            self.ws.freeze_panes = freeze
        # Print: landscape, one page wide
        ps = self.ws.page_setup
        ps.orientation = 'landscape'
        ps.paperSize = self.ws.PAPERSIZE_A3 if paper == 'A3' else self.ws.PAPERSIZE_A4
        ps.fitToWidth, ps.fitToHeight = 1, 0
        self.ws.sheet_properties.pageSetUpPr.fitToPage = True


wb = Workbook()

# ----------------------------------------------------------------------------
# Sheet: Market (2025 market size and funnel)
# ----------------------------------------------------------------------------
wsm = wb.active
wsm.title = 'Market'
M = Sheet(wsm, {'A': 64, 'B': 11, 'C': 10, 'D': 95, 'E': 12, 'F': 26, 'G': 18}, wrap_cols='ADF')
M.title('Market: 2025 market size and funnel',
        'Feeds slides 2, 3 and 7 and appendix A2. USD billions, 2025, nominal at 2025 average FX, excluding fare collection. '
        'Read top to bottom: A. Inputs > B. Build > C. Funnel > D. Checks.')
M.header(4, ['Item', 'Value', 'Unit', 'Source or method', 'Confidence', 'On slide', 'Deck key'])


def item(S, r, label, value, unit, source, conf, slide, key, fmt, bold=False):
    """One row of the Item | Value | Unit | Source or method | Confidence | On slide | Deck key layout."""
    S.text('A%d' % r, label, BOLD if bold else BLACK)
    S.num('B%d' % r, value, fmt, bold)
    S.text('C%d' % r, unit)
    S.text('D%d' % r, source)
    S.text('E%d' % r, conf)
    S.text('F%d' % r, slide)
    S.text('G%d' % r, key)


M.section(5, 'A. INPUTS', 'G')
market_inputs = [
    (6, 'USD per EUR, 2025 average', 1.13, 'USD/EUR',
     'ECB euro reference rate, 2025 annual average (research note 21)',
     'HIGH', 'Not shown (used in rows 25, 26, 29)', 'fx', F_BN),
    (7, 'Bus and tram ITS, Europe, 2025 (fare-inclusive)', 2.55, 'EUR B',
     'Berg Insight, Public Transport ITS in Europe and North America, 10th ed. (Mar 2026), summary p.2 (research notes 01, 17 (gap))',
     'HIGH', 'A2', 'berg_eu', F_BN),
    (8, 'Bus and tram ITS, North America, 2025 (fare-inclusive)', 1.22, 'EUR B',
     'Same source as row 7',
     'HIGH', 'A2', 'berg_na', F_BN),
    (9, 'Fare-collection share removed from Berg values', 0.20, 'share',
     'Analyst judgement inside a bracket: GMI electronic-payment share (14.7%) to GMI ticketing application share (24.2%) (research note 17 (gap), section 2)',
     'MID', 'A2', 'haircut', F_PCT),
    (10, 'Rest-of-world share of global bus ITS', 0.261, 'share',
     'GMI APTS (Aug 2026) regional split, 2025: Asia-Pacific 17.2% + Latin America 5.0% + Middle East and Africa 3.9%. '
     'All-mode mix applied to bus, hence LOW (research note 17 (gap), section 4)',
     'LOW', 'A2', 'row_share', F_PCT),
    (11, 'World rail control (signalling) market, 2023-25 average, treated as 2025', 24.9, 'EUR B',
     'UNIFE World Rail Market Study 2026 (Bain) abstract; includes freight, trackside and onboard (research note 21)',
     'HIGH', 'A2', 'unife', F_BN),
    (12, 'Passenger share of rail control (freight removed)', 0.74, 'share',
     'Analyst carve-out matrix built from regional train-km and network data (Eurostat, UITP): passenger EUR 18.5B of EUR 24.9B (74.3%); tested at 73-76% (research note 21)',
     'MID', 'A2', 'pax_share', F_PCT),
    (13, 'Urban (metro, light rail) share of passenger signalling', 0.30, 'share',
     'Analyst carve-out matrix, network km × unit cost: urban EUR 5.6B of passenger EUR 18.5B (30%); '
     "GMI's CBTC-only market (USD 4.9B) sits below the result, as it should (research note 21)",
     'MID', 'A2', 'urban_share', F_PCT),
    (14, 'Advanced public transportation systems (APTS), all modes, 2025', 6.83, 'USD B',
     'Global Market Insights, APTS market report (Aug 2026) (research note 17 (gap), section 4)',
     'MID', 'A2', 'gmi_apts', F_BN),
    (15, 'Railway share of APTS', 0.305, 'share',
     'GMI mode split: roadways 47.6%, railways 30.5%, airways 14.6%, waterways 7.3%',
     'MID', 'Not shown (used in row 32)', 'gmi_rail', F_PCT),
    (16, 'Ticketing share of APTS (removed)', 0.242, 'share',
     'GMI application split: ticketing 24.2%',
     'MID', 'Not shown (used in row 32)', 'gmi_ticketing', F_PCT),
    (17, 'Rail condition-monitoring platforms sold to operators', 1.0, 'USD B',
     'Analyst estimate. OEM platforms (Hitachi HMAX, Siemens Railigent X, Alstom HealthHub) are mostly monetised inside service contracts (research notes 09, 13)',
     'LOW', 'A2 (in words)', 'rail_cm', F_BN),
    (18, 'Trackside detection and wayside monitoring', 0.6, 'USD B',
     'Analyst estimate anchored on Frauscher (bought by Wabtec), voestalpine and others; axle counters stay in signalling (research notes 03, 22)',
     'LOW', 'A2 (in words)', 'rail_td', F_BN),
    (19, 'Bus ITS hardware share of value, 2025', 0.468, 'share',
     'GMI APTS component split, 2025: hardware 46.8%, software 33.0%, services 20.1% (research note 17 (gap), section 4.1)',
     'MID', 'A2; S3 lens (in words)', 'bus_hw_2025', F_PCT),
    (20, 'Other rail ITS hardware share of value', 0.45, 'share',
     'Analyst assumption, just below GMI APTS (46.8%) and passenger rail signalling (~46%): condition-monitoring platforms are '
     'mostly sold inside service contracts (row 17)',
     'LOW', 'A2; S3 lens (in words)', 'ro_hw', F_PCT),
    (21, 'Umbrella global ITS market, low end (context; not used in any calculation)', 40, 'USD B',
     'MarketsandMarkets, Grand View Research, Precedence Research, Mordor Intelligence, 2025 estimates (research note 01)',
     'MID', 'S3 funnel top', 'global_its_low', F_BN),
    (22, 'Umbrella global ITS market, high end (context; not used in any calculation)', 60, 'USD B',
     'Same sources as row 21',
     'MID', 'S3 funnel top', 'global_its_high', F_BN),
]
for r, label, v, unit, src, conf, slide, key, fmt in market_inputs:
    item(M, r, label, v, unit, src, conf, slide, key, fmt)

M.section(24, 'B. BUILD: SEGMENT ROWS', 'G')
market_build = [
    (25, 'Bus and tram ITS, Europe', '=B7*B6*(1-B9)',
     'Berg Europe × FX × (1 − fare share)', 'A2; S3 lens, S7 (in words)', 'bus_eu', False),
    (26, 'Bus and tram ITS, North America', '=B8*B6*(1-B9)',
     'Berg North America × FX × (1 − fare share)', 'A2; S3 lens, S7 (in words)', 'bus_na', False),
    (27, 'Bus ITS, rest of world', '=(B25+B26)*B10/(1-B10)',
     'Europe + North America, grossed up so the rest of the world is the row 10 share of the total', 'A2; S3 lens (in words)', 'bus_row', False),
    (28, 'Bus and tram ITS, total', '=SUM(B25:B27)',
     'Sum of rows 25-27', 'S3 table', 'bus', True),
    (29, 'Passenger rail signalling', '=B11*B6*B12',
     'UNIFE × FX × passenger share', 'Not shown (used in rows 30, 31, 34, 43)', 'sig', False),
    (30, 'Urban signalling (metro, light rail)', '=B29*B13',
     'Passenger signalling × urban share', 'S3 table; A2', 'urban', False),
    (31, 'Mainline and commuter signalling', '=B29-B30',
     'The rest of passenger signalling', 'S3 table; A2', 'mainline', False),
    (32, 'Other rail ITS: passenger information, CCTV, tracking (GMI, ex-ticketing)', '=B14*B15*(1-B16)',
     'GMI APTS × railway share × (1 − ticketing share)', 'Not shown (used in row 33)', 'ro_gmi', False),
    (33, 'Other rail ITS, total', '=B32+B17+B18',
     'GMI part + condition monitoring + trackside detection', 'S3 table; A2', 'ro', True),
    (34, 'Public ITS market, 2025', '=B28+B29+B33',
     'Bus + passenger signalling + other rail ITS', 'S2, S3, A2', 'market', True),
]
for r, label, f, method, slide, key, bold in market_build:
    item(M, r, label, f, 'USD B', method, None, slide, key, F_BN3, bold)

M.section(36, 'C. FUNNEL AND SHARES', 'G')
market_funnel = [
    (37, 'Transit-operator core (market less mainline signalling)', '=B34-B31', 'USD B',
     'Mainline signalling is bought mainly by rail infrastructure managers rather than transit agencies (in North America, '
     'commuter railroads run by transit agencies also buy it)', 'S3 funnel', 'core', F_BN3, False),
    (38, 'Contestable pool (core less urban signalling)', '=B37-B30', 'USD B',
     'Urban signalling is a closed, safety-certified oligopoly', 'S3 funnel', 'contestable', F_BN3, False),
    (39, 'Hardware in bus and other rail ITS', '=B28*B19+B33*B20', 'USD B',
     'Bus × bus hardware share + other rail × other rail hardware share', 'Not shown (used in row 40)', 'hardware', F_BN3, False),
    (40, 'Open software and services pool', '=B38-B39', 'USD B',
     'Contestable pool less hardware', 'S2, S3, A2', 'open', F_BN3, True),
    (41, 'Open pool: North American bus software and services', '=B26*(1-B19)', 'USD B',
     'Bus North America × (1 − bus hardware share)', 'S7; A2', 'open_na_bus', F_BN3, False),
    (42, 'Open pool as share of market', '=B40/B34', 'share',
     'Open pool ÷ market', 'S3 circle', 'open_share', F_PCT, False),
    (43, 'Signalling as share of market', '=B29/B34', 'share',
     'Passenger signalling ÷ market', 'S2 (in words: "nearly three-quarters")', 'sig_share', F_PCT, False),
    (44, 'Mainline signalling as share of market', '=B31/B34', 'share',
     'Mainline signalling ÷ market', 'S2, S3 title (in words: "half")', 'mainline_share', F_PCT, False),
]
for r, label, f, unit, method, slide, key, fmt, bold in market_funnel:
    item(M, r, label, f, unit, method, None, slide, key, fmt, bold)

M.section(46, 'D. CHECKS (all should be 0)', 'G')
market_checks = [
    (47, 'Check: segments add up to the market', '=B28+B30+B31+B33-B34',
     'Bus + urban + mainline + other rail − market'),
    (48, 'Check: core plus mainline equals the market', '=B37+B31-B34',
     'Core + mainline − market'),
    (49, 'Check: open pool equals software and services of bus and other rail', '=B28*(1-B19)+B33*(1-B20)-B40',
     'Bus × (1 − bus hardware share) + other rail × (1 − other rail hardware share) − open pool'),
]
for r, label, f, method in market_checks:
    M.text('A%d' % r, label)
    M.num('B%d' % r, f, F_CHK)
    M.text('C%d' % r, 'USD B')
    M.text('D%d' % r, method)
M.finish()

# ----------------------------------------------------------------------------
# Sheet: Growth (market growth 2025-2031E, low / base / high)
# ----------------------------------------------------------------------------
wsg = wb.create_sheet('Growth')
gw = {'A': 46, 'I': 12, 'J': 12, 'K': 12, 'L': 10, 'M': 10, 'N': 10, 'O': 11, 'P': 11, 'Q': 95, 'R': 20, 'S': 24, 'T': 18}
gw.update({c: 9 for c in 'BCDEFGH'})
G = Sheet(wsg, gw, wrap_cols='AQS')
YC = 'BCDEFGH'                       # year columns: 2025 ... 2031E
YEARS = ['2025', '2026E', '2027E', '2028E', '2029E', '2030E', '2031E']
G.title('Growth: market growth 2025-2031E, low / base / high',
        'Feeds slide 4, slide 2, slide 3 (in words) and appendix A3. USD billions, nominal at constant 2025 FX. Each segment is one row: '
        '2025 value (green, from Market) > base path using the base CAGR (column M) > 2031E low and high (columns O-P). '
        'CAGR inputs are blue in columns L-N.')
G.header(4, ['Segment'] + YEARS + ['CAGR 2025-31E (from path)', 'Increase 2025-31E', 'Share of increase', 'CAGR low',
                                   'CAGR base (input)', 'CAGR high', 'Low 2031E', 'High 2031E', 'Source or basis',
                                   'Confidence', 'On slide', 'Deck key'], text_fmt_cols=YC)

G.text('A5', 'Years from 2025')
G.num('B5', 0, F_INT)
for i in range(1, 7):
    G.num('%s5' % YC[i], '=%s5+1' % YC[i - 1], F_INT)
G.text('Q5', 'Index: years since 2025 (2025 = 0); drives every growth exponent on this sheet')
G.text('R5', 'n/a (index)')

G.section(6, 'A. SEGMENT ROWS', 'T')
segments = [
    (7, 'Bus and tram ITS, Europe', '=Market!B25', (0.035, 0.053, 0.070),
     "Base: Berg Insight 10th ed. forecast, 2025-30 (5.3%). Low: the zero-emission transition slows ITS spend. "
     "High: the 9th edition's pace (6.3%) plus AI enforcement (research notes 01, 02, 13)",
     'HIGH base; MID range', 'A3', 'bus_eu_path'),
    (8, 'Bus and tram ITS, North America', '=Market!B26', (0.025, 0.050, 0.080),
     'Base: Berg Insight 10th ed. (5.0%). Low: FY2027 federal funding reset (federal transit funding about 20% lower if '
     'IIJA advance appropriations are not continued) and agencies facing fiscal cliffs defer refresh. High: a partial return '
     'toward the 11.5% a year realised in 2022-25 (research notes 06, 17 (gap), 25)',
     'HIGH base; MID range', 'A3', 'bus_na_path'),
    (9, 'Bus ITS, rest of world', '=Market!B27', (0.06, 0.09, 0.11),
     'Base: GMI APTS Asia-Pacific forecast (10.1%) blended with slower Latin America (7.2%) and Middle East and Africa (5.8%); the GMI-weighted blend is 9.0%. '
     'Low: rest-of-world bus grows nearer the global market (all-mode GMI rates may overstate bus). High: slightly '
     'above the GMI Asia-Pacific rate. The range is analyst judgement (research notes 05, 07, 17 (gap))',
     'MID', 'A3', 'bus_row_path'),
    (10, 'Passenger rail signalling (urban and mainline)', '=Market!B29', (0.035, 0.050, 0.065),
     "Base: just above SCI Verkehr's 4.6% nominal CCS forecast (2023-28) and in line with UNIFE's ~3.2% a year real "
     "outlook plus inflation (UNIFE's realised rail-control growth was 5.7% a year in real terms, 2021-23 to 2023-25). "
     "Low: ETCS slippage, UK CP7 ETCS cut (GBP 1.54B to 0.99B), DB strategy reset. High: FRMCS from 2027, "
     "driverless-metro conversions (research notes 21, 36)",
     'MID', 'S2 (in words); S4 chart; A3', 'sig_path'),
    (11, 'Other rail ITS', '=Market!B33', (0.05, 0.07, 0.09),
     'Between MarketsandMarkets rail asset management (6.6%) and Mordor rail telematics (7.6%). Low: rolling-stock '
     'renewal slips. High: fleet-wide predictive maintenance (research notes 03, 13)',
     'MID', 'S4 chart; A3', 'ro_path'),
]
for r, label, link, (lo, base, hi), basis, conf, slide, key in segments:
    G.text('A%d' % r, label)
    G.num('B%d' % r, link, F_BN)
    for i in range(1, 7):
        G.num('%s%d' % (YC[i], r), '=$B%d*(1+$M%d)^%s$5' % (r, r, YC[i]), F_BN)
    G.num('I%d' % r, '=(H%d/B%d)^(1/$H$5)-1' % (r, r), F_PCT)
    G.num('J%d' % r, '=H%d-B%d' % (r, r), F_BN)
    if r in (10, 11):
        G.num('K%d' % r, '=J%d/$J$12' % r, F_PCT0)
    else:
        G.text('K%d' % r, None)
    G.num('L%d' % r, lo, F_PCT)
    G.num('M%d' % r, base, F_PCT)
    G.num('N%d' % r, hi, F_PCT)
    G.num('O%d' % r, '=$B%d*(1+L%d)^$H$5' % (r, r), F_BN)
    G.num('P%d' % r, '=$B%d*(1+N%d)^$H$5' % (r, r), F_BN)
    G.text('Q%d' % r, basis)
    G.text('R%d' % r, conf)
    G.text('S%d' % r, slide)
    G.text('T%d' % r, key)

# Row 12: market total
G.text('A12', 'Public ITS market', BOLD)
for c in YC:
    G.num('%s12' % c, '=SUM(%s7:%s11)' % (c, c), F_BN, bold=True)
G.num('I12', '=(H12/B12)^(1/$H$5)-1', F_PCT, bold=True)
G.num('J12', '=H12-B12', F_BN, bold=True)
G.text('K12', None)
G.num('L12', '=(O12/$B$12)^(1/$H$5)-1', F_PCT, bold=True)
G.num('M12', '=I12', F_PCT, bold=True)
G.num('N12', '=(P12/$B$12)^(1/$H$5)-1', F_PCT, bold=True)
G.num('O12', '=SUM(O7:O11)', F_BN, bold=True)
G.num('P12', '=SUM(P7:P11)', F_BN, bold=True)
G.text('Q12', 'Sum of segment rows; low and high CAGRs are implied by the 2031E totals')
G.text('R12', None)
G.text('S12', 'S2, S4, A3')
G.text('T12', 'market_path')

G.section(14, 'B. BUS TOTAL AND OPEN SOFTWARE AND SERVICES POOL', 'T')
# Row 15: bus, all regions
G.text('A15', 'Bus and tram ITS, all regions')
for c in YC:
    G.num('%s15' % c, '=SUM(%s7:%s9)' % (c, c), F_BN)
G.num('I15', '=(H15/B15)^(1/$H$5)-1', F_PCT)
G.num('J15', '=H15-B15', F_BN)
G.num('K15', '=J15/$J$12', F_PCT0)
G.text('Q15', 'Sum of rows 7-9')
G.text('S15', 'S4 chart; A3')
G.text('T15', 'bus_path')
# Row 16: bus hardware share, straight line from 2025 to the 2031E input
G.text('A16', 'Bus ITS hardware share of value (2031E input in blue)')
G.num('B16', '=Market!B19', F_PCT)
for c in 'CDEFG':
    G.num('%s16' % c, '=$B16+($H16-$B16)*%s$5/$H$5' % c, F_PCT)
G.num('H16', 0.446, F_PCT)
G.text('Q16', '2031E input: GMI implied 2031 mix 44.6 / 35.2 / 20.1 (software grows 9.7% a year against hardware '
              '7.7%); straight line from 2025 (research note 17 (gap))')
G.text('R16', 'MID')
G.text('S16', 'S2, S3 lens (in words)')
G.text('T16', 'bus_hw_path')
# Row 17: other rail hardware share, held flat
G.text('A17', 'Other rail ITS hardware share of value')
G.num('B17', '=Market!B20', F_PCT)
for c in 'CDEFGH':
    G.num('%s17' % c, '=$B17', F_PCT)
G.text('Q17', "Held flat: GMI's mix shift is not applied to condition monitoring and detection")
G.text('S17', 'Not shown (used in row 18)')
# Row 18: open pool
G.text('A18', 'Open software and services pool', BOLD)
for c in YC:
    G.num('%s18' % c, '=%s15*(1-%s16)+%s11*(1-%s17)' % (c, c, c, c), F_BN, bold=True)
G.num('I18', '=(H18/B18)^(1/$H$5)-1', F_PCT, bold=True)
G.num('J18', '=H18-B18', F_BN, bold=True)
G.text('Q18', 'Bus × (1 − bus hardware share) + other rail × (1 − other rail hardware share)')
G.text('S18', 'S2, S4')
G.text('T18', 'open_path')
# Row 19: memo, North American bus slice
G.text('A19', 'Memo: open pool, North American bus')
for c in YC:
    G.num('%s19' % c, '=%s8*(1-%s16)' % (c, c), F_BN)
G.num('I19', '=(H19/B19)^(1/$H$5)-1', F_PCT)
G.text('Q19', 'North American bus slice of the open pool; grows more slowly than the global pool (column I)')
G.text('S19', 'Not shown (memo)')
G.text('T19', 'open_na_bus_path')

G.section(21, 'C. CHECKS (all should be 0)', 'T')
G.text('A22', 'Check: 2025 total in row 12 equals the Market sheet total (Market!B34)')
G.num('B22', '=B12-Market!B34', F_CHK)
G.text('A23', 'Check: 2025 open pool in row 18 equals the Market sheet open pool (Market!B40)')
G.num('B23', '=B18-Market!B40', F_CHK)
G.text('A24', 'Check: segment increases add up to the market increase')
G.num('J24', '=SUM(J7:J11)-J12', F_CHK)
G.finish(paper='A3')

# ----------------------------------------------------------------------------
# Sheet: Returns (illustrative buy-and-build value bridge)
# ----------------------------------------------------------------------------
wsr = wb.create_sheet('Returns')
T = Sheet(wsr, {'A': 64, 'B': 11, 'C': 10, 'D': 95, 'E': 12, 'F': 26, 'G': 18}, wrap_cols='ADF')
T.title('Returns: illustrative buy-and-build value bridge',
        'Feeds slide 7, slide 2, slide 5 (in words) and appendix A4. Illustrative, not a valuation. USD millions unless stated. '
        'Gross MOIC = exit equity ÷ equity invested; modest entry debt, half repaid by exit.')
T.header(4, ['Item', 'Value', 'Unit', 'Source or method', 'Confidence', 'On slide', 'Deck key'])

T.section(5, 'A. INPUTS', 'G')
returns_inputs = [
    (6, 'Entry revenue', 60, 'USD M',
     'Illustrative. Privately held North American mid-market bus ITS vendors (Avail, GIRO, ETA, Passio) range from under '
     'USD 10M to about USD 115M of revenue (GIRO about USD 115M, Avail about USD 25M); none files accounts, so all are '
     'aggregator estimates that vary widely (research notes 08, 32)',
     'ASSUMPTION', 'A4', 'rev0', F_M),
    (7, 'Entry EV / revenue', 2.0, 'x',
     "Below IVU's software multiple, inside the INIT-to-IVU trading band (rows 40 and 42; check row 46) and above the "
     'Clever precedent (row 15); see memo rows 34-36 (research note 26)',
     'MID', 'S2, S7 (in words); A4', 'entry_mult', F_X),
    (8, 'Entry EBITDA margin', 0.15, 'share',
     'INIT EBITDA margin, 14.9% (FY2025 annual report; research note 08)',
     'MID', 'Not shown (used in row 20)', 'margin0', F_PCT),
    (9, 'Entry leverage: net debt at entry, multiple of entry EBITDA', 2.5, 'x EBITDA',
     "Deliberately modest; Cubic's 2021 buyout, at ~11x EBITDA of funded debt, is now distressed (research notes 10, 26)",
     'MID', 'A4 (assumptions); S2, S5, S6, S7 (in words)', 'leverage', F_X),
    (10, 'Share of entry debt repaid by exit', 0.5, 'share',
     'Simplifying assumption: half of the entry debt is repaid from operating cash flow over the hold',
     'ASSUMPTION', 'A4 (assumptions, in words: "half")', 'debt_repaid', F_PCT),
    (11, 'Organic revenue growth a year', 0.08, 'share',
     'Above the North American bus market (5.0%) on module cross-sell; well below Via and INIT (24-29%) (research note 26)',
     'MID', 'A4 (assumptions)', 'growth', F_PCT),
    (12, 'Bolt-on revenue acquired over the hold', 40, 'USD M',
     'Two or three point-solution bolt-ons (passenger counting, passenger information, enforcement)',
     'ASSUMPTION', 'A4 (assumptions)', 'bolt_rev', F_M),
    (13, 'Bolt-on EV / revenue', 1.5, 'x',
     'Between Modaxo-Conduent (row 39) and the Clever precedent (row 15) (research note 34)',
     'MID', 'A4 (assumptions)', 'bolt_mult', F_X),
    (14, 'Hold period', 5, 'years',
     'Standard private-equity hold',
     'MID', 'S7 MOIC header; A4', 'hold', F_INT),
    (15, 'Exit A EV / revenue: Clever Devices precedent', 1.58, 'x',
     "Hitachi paid USD 302M plus USD 45M of debt repaid, on Clever's projected 2026 revenue of USD 220M: "
     '(302 + 45) / 220 = 1.58x (Hitachi Q1 FY2026 results, subsequent-events note; research note 34)',
     'HIGH', 'S2, S7, A4 (prints "1.6x")', 'exit_a_mult', F_X),
    (16, 'Exit B EV / revenue: IVU trading multiple', 2.60, 'x',
     'IVU Traffic Technologies EV / LTM revenue, 2.60x at 6 Nov 2026; 51.8% recurring revenue (stockanalysis; '
     'IVU Q3 2026 report; research note 26)',
     'HIGH', 'S2, S7, A4', 'exit_b_mult', F_X),
]
for r, label, v, unit, src, conf, slide, key, fmt in returns_inputs:
    item(T, r, label, v, unit, src, conf, slide, key, fmt)

T.section(18, 'B. VALUE BRIDGE', 'G')
returns_bridge = [
    (19, 'Entry enterprise value', '=B6*B7', 'USD M',
     'Entry revenue × entry EV / revenue', 'Not shown (used in row 22)', 'ev0', F_M, False),
    (20, 'Entry EBITDA', '=B6*B8', 'USD M',
     'Entry revenue × entry EBITDA margin', 'Not shown (used in row 21)', 'ebitda0', F_M, False),
    (21, 'Net debt at entry (USD M)', '=B20*B9', 'USD M',
     'Entry EBITDA × entry leverage (row 9)', 'Not shown (used in rows 22, 26, 34)', 'debt0', F_M, False),
    (22, 'Equity at entry', '=B19-B21', 'USD M',
     'Entry enterprise value − net debt at entry', 'Not shown (used in row 24)', 'eq0', F_M, False),
    (23, 'Bolt-on cost (equity-funded)', '=B12*B13', 'USD M',
     'Bolt-on revenue × bolt-on EV / revenue', 'Not shown (used in rows 24, 34)', 'bolt_cost', F_M, False),
    (24, 'Total equity invested', '=B22+B23', 'USD M',
     'Equity at entry + bolt-on cost', 'Not shown (used in rows 28, 30, 33)', 'eq_in', F_M, True),
    (25, 'Exit revenue', '=B6*(1+B11)^B14+B12', 'USD M',
     'Entry revenue × (1 + organic growth) ^ hold + bolt-on revenue', 'A4', 'rev1', F_M, False),
    (26, 'Net debt at exit', '=B21*(1-B10)', 'USD M',
     'Net debt at entry × (1 − share repaid)', 'Not shown (used in rows 28, 30, 33, 35, 36)', 'debt1', F_M, False),
    (27, 'Exit A: enterprise value', '=B25*B15', 'USD M',
     'Exit revenue × exit A EV / revenue', 'Not shown (used in rows 28, 35)', 'ev_a', F_M, False),
    (28, 'Exit A: gross MOIC (x)', '=(B27-B26)/B24', 'x',
     '(Exit A enterprise value − net debt at exit) ÷ total equity invested', 'S7, A4; S2 (in words)', 'moic_a', F_X1, True),
    (29, 'Exit B: enterprise value', '=B25*B16', 'USD M',
     'Exit revenue × exit B EV / revenue', 'Not shown (used in rows 30, 36)', 'ev_b', F_M, False),
    (30, 'Exit B: gross MOIC (x)', '=(B29-B26)/B24', 'x',
     '(Exit B enterprise value − net debt at exit) ÷ total equity invested', 'S7, A4', 'moic_b', F_X1, True),
]
for r, label, f, unit, method, slide, key, fmt, bold in returns_bridge:
    item(T, r, label, f, unit, method, None, slide, key, fmt, bold)

T.section(32, 'C. MEMO: BREAK-EVEN AND ENTRY-PRICE SENSITIVITY', 'G')
returns_memo = [
    (33, 'Break-even exit EV / revenue (MOIC = 1.0x)', '=(B24+B26)/B25', 'x',
     'Exit multiple at which exit equity equals equity invested: (total equity invested + net debt at exit) ÷ exit revenue',
     'Not shown (memo)', 'breakeven_mult', F_X),
    (34, 'Equity invested if entry is at the Clever multiple', '=B6*B15-B21+B23', 'USD M',
     'Entry revenue × exit A multiple (row 15) − net debt at entry + bolt-on cost', 'Not shown (used in rows 35, 36)',
     'eq_in_at_a', F_M),
    (35, 'Exit A MOIC if entry is at the Clever multiple (x)', '=(B27-B26)/B34', 'x',
     '(Exit A enterprise value − net debt at exit) ÷ equity invested at the Clever entry multiple', 'A4',
     'moic_a_at_a', F_X1),
    (36, 'Exit B MOIC if entry is at the Clever multiple (x)', '=(B29-B26)/B34', 'x',
     '(Exit B enterprise value − net debt at exit) ÷ equity invested at the Clever entry multiple', 'A4',
     'moic_b_at_a', F_X1),
]
for r, label, f, unit, method, slide, key, fmt in returns_memo:
    item(T, r, label, f, unit, method, None, slide, key, fmt)

T.section(38, 'D. EXIT BENCHMARKS, EV / REVENUE', 'G')
benchmarks = [
    (39, 'Conduent transit to Modaxo (2026)', 0.44,
     "Modaxo paid USD 164M for Conduent's public transit business, on 2025 revenue of USD 371M (Conduent 8-K, Oct 2026; "
     'research note 34)', 'bm_conduent'),
    (40, 'INIT (trading, 6 Nov 2026)', 0.98,
     'EV / LTM revenue (stockanalysis; research note 26)', 'bm_init'),
    (41, 'Clever Devices to Hitachi (2026)', '=B15',
     'Exit A input', 'bm_clever'),
    (42, 'IVU (trading, 6 Nov 2026)', '=B16',
     'Exit B input', 'bm_ivu'),
    (43, 'Via (trading, LTM revenue, 6 Nov 2026)', 5.61,
     'EV / LTM revenue; loss-making (stockanalysis; research note 26)', 'bm_via'),
]
BM_SLIDE = {'bm_conduent': 'A4; S5, S7 (in words)', 'bm_init': 'A4; S2, S5, S7 (in words)', 'bm_clever': 'A4; S5, S7 (in words)',
            'bm_ivu': 'A4; S2, S5, S7 (in words)', 'bm_via': 'A4; S5, S7 (in words)'}
for r, label, v, src, key in benchmarks:
    item(T, r, label, v, 'x', src, 'HIGH', BM_SLIDE.get(key, 'A4'), key, F_X)

T.section(45, 'E. CHECKS (all should be 0)', 'G')
T.text('A46', 'Check: entry multiple sits inside the INIT-IVU trading band (0 = yes)')
T.num('B46', '=IF(AND(B7>=B40,B7<=B42),0,1)', F_CHK)
T.text('C46', 'check')
T.text('D46', '0 if INIT multiple ≤ entry EV / revenue ≤ IVU multiple, otherwise 1')
T.finish()

# ----------------------------------------------------------------------------
# Sheet: README (text only, no formulas). Inserted first.
# ----------------------------------------------------------------------------
wsd = wb.create_sheet('README', 0)
D = Sheet(wsd, {'A': 26, 'B': 90, 'C': 60}, wrap_cols='ABC')
D.title('Public ITS market model: bus and passenger rail, 2025-2031E',
        'Supports the written case deck (Public_ITS_Market_Case.pptx) and its appendix. Prepared November 2026. '
        'USD billions, nominal, at 2025 average FX, excluding fare collection, unless a row says otherwise.')
row = [4]


def rd_section(text):
    D.section(row[0], text, 'C')
    row[0] += 1


def rd_line(label, body):
    D.text('A%d' % row[0], label, BOLD)
    D.text('B%d' % row[0], body)
    row[0] += 1


def rd_table(headers, rows):
    for j, h in enumerate(headers):
        c = wsd.cell(row=row[0], column=j + 1, value=h)
        c.font = HDR
        c.fill = HDR_FILL
        c.alignment = HDR_ALIGN
        c.border = BOX
    row[0] += 1
    for vals in rows:
        for j, v in enumerate(vals):
            D.text('%s%d' % ('ABC'[j], row[0]), v)
        row[0] += 1


rd_section('1. How to read this model')
rd_line('Layout', 'One sheet per quantitative slide: Market (slide 3), Growth (slide 4), Returns (slide 7). '
                  'Slide 2 summarises all three; slides 5 and 6 carry no numbers.')
rd_line('Reading order', 'Each sheet reads top to bottom, from blue inputs through black formulas to its checks (every '
                         'check should equal 0). Market: A. Inputs > B. Build > C. Funnel > D. Checks. Growth: one row '
                         'per segment, with the CAGR inputs in blue in columns L-N, then the bus total and open pool, '
                         'then checks. Returns: A. Inputs > B. Value bridge > C. Memo > D. Exit benchmarks > E. Checks.')
rd_line('Colours', 'Blue = hard-coded input; black = formula on the same sheet; green = link to another sheet.')
rd_line('Confidence', 'HIGH = published figure used as stated; MID = published figure re-scoped, or a judgement inside '
                      'a sourced bracket; LOW = analyst estimate. Growth rows with a published base and an analyst '
                      'range show both (for example HIGH base; MID range). ASSUMPTION = an illustrative deal input on the '
                      'Returns sheet, chosen for the value bridge rather than estimated from data.')
rd_line('Slide link', "Column 'On slide' shows where each number appears. The decks read these cells directly (column "
                      "'Deck key' names each one), so no slide number is retyped.")
rd_line('Scenarios', 'Low, base and high CAGRs sit side by side on Growth (columns L-N). There is no scenario selector: '
                     'change any blue cell and every case recalculates.')
row[0] += 1

rd_section('2. Calculation chain')
chain = [
    'Bus and tram ITS = Berg Insight Europe and North America (EUR) × USD per EUR × (1 − fare-collection share); '
    "rest of world added in proportion to GMI's regional mix.",
    'Rail signalling = UNIFE world rail control (EUR) × USD per EUR × passenger share, split into urban (metro, light '
    'rail) and mainline and commuter.',
    'Other rail ITS = GMI APTS × railway share × (1 − ticketing share) + condition monitoring + trackside detection '
    '(two analyst estimates).',
    'Funnel: market − mainline signalling = transit-operator core; core − urban signalling = contestable pool; '
    'contestable pool − bus and other-rail hardware = open software and services pool.',
    "Forecast: each 2025 segment row × (1 + CAGR) ^ years, in low, base and high; the bus hardware share falls in a "
    "straight line to GMI's implied 2031 mix, which lifts the open pool's growth.",
    "Returns: buy below a software multiple with modest debt, add bolt-ons, exit at the Clever precedent (Returns row "
    "15) or at IVU's multiple (row 16); gross MOIC = exit equity ÷ equity invested.",
]
for i, t in enumerate(chain, 1):
    rd_line(str(i), t)
row[0] += 1

rd_section('3. Slide map')
rd_table(['Slide', 'Sheet and rows', 'What it shows'], [
    ('S2 Executive summary', 'Market B34, B40, B43-B44 (in words); Growth rows 12 and 18, rows 10 and 16 (in words); '
     'Returns B15, B16; B7, B9, B28, B40, B42 (in words)',
     'Market, growth, open pool, exit multiples'),
    ('S3 Market size', 'Market B21:B22 (funnel top), B28, B30, B31, B33, B34 (table), B37, B38, B40, B42 (funnel), '
     'B44 (title, in words), B19:B20 and B25:B27 (lens, in words); Growth row 16 (lens, in words)',
     'Funnel, segment table, share of scope that is open'),
    ('S4 Market growth', 'Growth rows 10, 11, 12, 15, 18', 'Segment chart, total CAGR, open pool'),
    ('S5 Competitive, S6 Risks', 'Returns B39:B43 (S5, in words); Returns B9 (S5, S6, in words)',
     "Words only: S5 compares the exit benchmarks in words and S5 and S6 contrast the case's modest debt with a highly "
     "levered buyout; other sources are cited in each slide's source line"),
    ('S7 Thesis', 'Returns B14:B16, B28, B30; B7, B9, B39:B43 (in words); Market B41; B25:B26 (in words)',
     'Exit multiples, MOIC, North American bus software and services'),
    ('A2 Market build', 'Market rows 7-41', 'Sizing chain'),
    ('A3 Growth scenarios', 'Growth rows 7-12 and 15', 'Bridge and low/base/high table'),
    ('A4 Exit multiples and returns', 'Returns rows 6-43', 'Benchmarks, value bridge, entry sensitivity'),
    ('A5 Incumbency', 'none', 'Cited counts from an ITS award dataset (agency board records, 2016-26), the 2009-16 CAD/AVL refresh cohort and '
     'FTA NTD RY2025 fleet tiers (research notes 35, 31, 16)'),
])
row[0] += 1

rd_section('4. Sources')
rd_table(['Research note (on request)', 'Source', 'Used for'], [
    ('01, 17 (gap)', 'Berg Insight, Public Transport ITS in Europe and North America, 10th ed. (Mar 2026)',
     'Bus and tram ITS, Europe and North America; bus growth rates (5.3%, 5.0%)'),
    ('17 (gap)', 'Global Market Insights, Advanced Public Transportation Systems (Aug 2026)',
     'Rest-of-world bus mix; other rail ITS; bus hardware share and its 2031 shift'),
    ('15, 21', 'UNIFE World Rail Market Study 2026 (Bain), abstract', 'World rail control, EUR 24.9B'),
    ('21', 'Analyst carve-out matrix (Eurostat train-km, UITP network km, unit costs)',
     'Passenger share 74% (EUR 18.5B of 24.9B), urban share 30% (EUR 5.6B of 18.5B)'),
    ('21, 90', 'SCI Verkehr CCS studies: Worldwide Market Trends 2023 and 2026 (Mar 2026)',
     'Signalling growth bracket (4.6% nominal, 2023-28, from the 2023 study); "Europe almost half of world signalling" '
     'and cross-check (~EUR 20B), from the 2026 study'),
    ('01', 'Umbrella ITS reports (MarketsandMarkets, Grand View Research, Precedence Research, Mordor Intelligence)',
     'Funnel top, $40-60B, context only'),
    ('03, 13', 'MarketsandMarkets rail asset management; Mordor rail telematics', 'Other rail ITS growth, 7%'),
    ('25', "FTA apportionment notices; H.R. 8870; FY2027 President's Budget", 'North American bus low case'),
    ('34', 'Hitachi Q1 FY2026 results, subsequent-events note', 'Exit A, 1.58x (Clever Devices)'),
    ('26', 'stockanalysis.com (6 Nov 2026); IVU Q3 2026 report', 'Exit B, 2.60x (IVU); INIT 0.98x; Via 5.61x'),
    ('34', 'Conduent 8-K (Oct 2026)', 'Conduent transit to Modaxo, 0.44x'),
    ('21', 'ECB euro reference rate, 2025 average', 'USD per EUR, 1.13'),
])
D.finish(freeze=None)

wb.properties.creator = 'Matthew Kang'
wb.properties.lastModifiedBy = 'Matthew Kang'
wb.properties.title = 'Public ITS market model'
wb.save(OUT)
print('saved', OUT)
