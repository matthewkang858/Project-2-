"""Export the recalculated model to deck_data.json, the only source of numbers for the deck builder.

Run after build_model.py and the LibreOffice recalculation (recalc.py):  python3 export_values.py [workbook] [output]

Keys are discovered from the workbook itself; no cell address is written in this script.
  - Market, Bottom-up and Returns: every row with text in the 'Deck key' column becomes a scalar key (value from the 'Value' column).
  - Growth: every row with text in the 'Deck key' column becomes a row object built from the year columns and the
    CAGR / increase / share / low / base / high columns (a field is included only if its cell holds a number).
  - checks: every row on any sheet whose column-A label starts with "Check:".
The script exits non-zero and writes nothing if a key is duplicated or missing, a keyed cell is empty or not numeric,
a formula cell holds an error (or has no cached value because the workbook was not recalculated), or a check is not 0.
"""
import json
import os
import sys
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
WORKBOOK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'Public_ITS_Market_Model.xlsx')
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'deck_data.json')

SCALAR_SHEETS = ('Market', 'Bottom-up', 'Returns')
ROW_SHEET = 'Growth'
KEY_HEADER = 'Deck key'
VALUE_HEADER = 'Value'
FIRST_YEAR_HEADER = '2025'
# Growth column headers -> row-object field names
ROW_FIELDS = {
    'CAGR 2025-31E (from path)': 'cagr',
    'Increase 2025-31E': 'increase',
    'Share of increase': 'share_of_increase',
    'CAGR low': 'cagr_low',
    'CAGR base (input)': 'cagr_base',
    'CAGR high': 'cagr_high',
    'Low 2031E': 'low_2031',
    'High 2031E': 'high_2031',
}
N_YEARS = 7
CHECK_TOLERANCE = 1e-9
ERRORS = ('#DIV/0!', '#N/A', '#NAME?', '#NULL!', '#NUM!', '#REF!', '#VALUE!', 'Err:')
# Keys the deck builder reads. A missing one fails the export rather than the deck build.
REQUIRED = [
    'fx', 'berg_eu', 'berg_na', 'haircut', 'row_share', 'unife', 'pax_share', 'urban_share', 'gmi_apts', 'gmi_rail',
    'gmi_ticketing', 'rail_cm', 'rail_td', 'bus_hw_2025', 'ro_hw', 'global_its_low', 'global_its_high',
    'bus_eu', 'bus_na', 'bus_row', 'bus', 'sig', 'urban', 'mainline', 'ro_gmi', 'ro', 'market',
    'core', 'contestable', 'hardware', 'open', 'open_na_bus', 'open_share', 'sig_share', 'mainline_share',
    'bus_eu_path', 'bus_na_path', 'bus_row_path', 'sig_path', 'ro_path', 'market_path', 'bus_path', 'bus_hw_path',
    'open_path', 'open_na_bus_path',
    'rev0', 'entry_mult', 'margin0', 'leverage', 'debt_repaid', 'growth', 'bolt_rev', 'bolt_mult', 'hold',
    'exit_a_mult', 'exit_b_mult', 'ev0', 'ebitda0', 'debt0', 'eq0', 'bolt_cost', 'eq_in', 'rev1', 'debt1', 'ev_a',
    'moic_a', 'ev_b', 'moic_b', 'breakeven_mult', 'eq_in_at_a', 'moic_a_at_a', 'moic_b_at_a',
    'bm_conduent', 'bm_init', 'bm_clever', 'bm_ivu', 'bm_via',
    'bu_total', 'bu_topdown', 'bu_ratio',
]

problems = []


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def header_row(ws):
    """Return (row number, {header text: column index}) for the row that holds the 'Deck key' header."""
    for r in range(1, 11):
        heads = {ws.cell(r, c).value: c for c in range(1, ws.max_column + 1) if isinstance(ws.cell(r, c).value, str)}
        if KEY_HEADER in heads:
            return r, heads
    problems.append('%s: no "%s" header found' % (ws.title, KEY_HEADER))
    return None, {}


def number_at(ws, r, c, key):
    v = ws.cell(r, c).value
    if not is_num(v):
        problems.append('%s!%s%d (%s): expected a number, found %r' % (ws.title, get_column_letter(c), r, key, v))
        return None
    return v


try:
    wb_f = load_workbook(WORKBOOK, data_only=False)   # formulas, to locate formula cells
    wb_v = load_workbook(WORKBOOK, data_only=True)    # cached values from the recalculation
except FileNotFoundError:
    sys.exit('export_values: workbook not found: %s' % WORKBOOK)

# 1. Every formula cell must hold a cached, non-error value
for ws_f in wb_f.worksheets:
    ws_v = wb_v[ws_f.title]
    for line in ws_f.iter_rows():
        for cf in line:
            if isinstance(cf.value, str) and cf.value.startswith('='):
                v = ws_v[cf.coordinate].value
                if v is None:
                    problems.append('%s!%s: formula has no cached value (recalculate the workbook first)'
                                    % (ws_f.title, cf.coordinate))
                elif isinstance(v, str) and v.startswith(ERRORS):
                    problems.append('%s!%s: formula error %s' % (ws_f.title, cf.coordinate, v))

out = {'_meta': {'source': 'model/Public_ITS_Market_Model.xlsx',
                 'units': 'USD B for market keys (berg_eu, berg_na and unife in EUR B; fx in USD per EUR); '
                          'USD M for rev0, ebitda0, bolt_rev, bolt_cost, ev*, eq*, debt*, rev1; '
                          'fractions for shares and CAGRs; x for *_mult, leverage (x EBITDA), moic_*, bm_*; years for hold',
                 'years': [], 'cells': {}}}


def add(key, value, cell):
    if key in out:
        problems.append('duplicate key %s (%s and %s)' % (key, out['_meta']['cells'][key], cell))
        return
    out[key] = value
    out['_meta']['cells'][key] = cell


# 2. Scalar keys (Market, Bottom-up, Returns)
for name in SCALAR_SHEETS:
    if name not in wb_v.sheetnames:
        problems.append('sheet %s missing' % name)
        continue
    ws = wb_v[name]
    hr, heads = header_row(ws)
    if hr is None:
        continue
    kc, vc = heads[KEY_HEADER], heads.get(VALUE_HEADER)
    if vc is None:
        problems.append('%s: no "%s" header found' % (name, VALUE_HEADER))
        continue
    for r in range(hr + 1, ws.max_row + 1):
        key = ws.cell(r, kc).value
        if isinstance(key, str) and key.strip():
            key = key.strip()
            add(key, number_at(ws, r, vc, key), '%s!%s%d' % (name, get_column_letter(vc), r))

# 3. Row objects (Growth)
if ROW_SHEET not in wb_v.sheetnames:
    problems.append('sheet %s missing' % ROW_SHEET)
else:
    ws = wb_v[ROW_SHEET]
    hr, heads = header_row(ws)
    if hr is not None:
        y0 = heads.get(FIRST_YEAR_HEADER)
        missing = [h for h in ROW_FIELDS if h not in heads]
        if y0 is None or missing:
            problems.append('%s: header row lacks %s' % (ROW_SHEET, ([FIRST_YEAR_HEADER] if y0 is None else []) + missing))
        else:
            years = [ws.cell(hr, c).value for c in range(y0, y0 + N_YEARS)]
            if not all(isinstance(y, str) for y in years):
                problems.append('%s: year headers must be text, found %r' % (ROW_SHEET, years))
            out['_meta']['years'] = [str(y) for y in years]
            last = max(heads[h] for h in ROW_FIELDS)
            kc = heads[KEY_HEADER]
            for r in range(hr + 1, ws.max_row + 1):
                key = ws.cell(r, kc).value
                if not (isinstance(key, str) and key.strip()):
                    continue
                key = key.strip()
                obj = {'values': [number_at(ws, r, c, key) for c in range(y0, y0 + N_YEARS)]}
                for h, field in ROW_FIELDS.items():
                    v = ws.cell(r, heads[h]).value
                    if is_num(v):
                        obj[field] = v
                add(key, obj, '%s!%s%d:%s%d' % (ROW_SHEET, get_column_letter(y0), r, get_column_letter(last), r))

# 4. Checks: every row whose column-A label starts with "Check:"; value = first numeric cell in the row
out['checks'] = []
for ws in wb_v.worksheets:
    for r in range(1, ws.max_row + 1):
        label = ws.cell(r, 1).value
        if not (isinstance(label, str) and label.startswith('Check:')):
            continue
        cell = next((ws.cell(r, c) for c in range(2, ws.max_column + 1) if is_num(ws.cell(r, c).value)), None)
        if cell is None:
            problems.append('%s row %d: check "%s" has no numeric value' % (ws.title, r, label))
            continue
        out['checks'].append({'sheet': ws.title, 'cell': cell.coordinate, 'label': label, 'value': cell.value})
        if abs(cell.value) > CHECK_TOLERANCE:
            problems.append('%s!%s: check failed (%s = %r)' % (ws.title, cell.coordinate, label, cell.value))
if not out['checks']:
    problems.append('no checks found')

# 5. Required keys
for k in REQUIRED:
    if k not in out:
        problems.append('missing key %s' % k)

if problems:
    sys.stderr.write('export_values: FAILED, deck_data.json not written\n  ' + '\n  '.join(problems) + '\n')
    sys.exit(1)

with open(OUTPUT, 'w') as fh:
    json.dump(out, fh, indent=1)
    fh.write('\n')
n_keys = len([k for k in out if k not in ('_meta', 'checks')])
gp = out['market_path']
print('exported %d keys and %d checks to %s; 2025 market = %.2f, 2031E = %.2f (CAGR %.2f%%), open pool = %.2f'
      % (n_keys, len(out['checks']), os.path.relpath(OUTPUT, os.getcwd()), out['market'], gp['values'][-1],
         gp['cagr'] * 100, out['open']))
