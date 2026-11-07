"""Read the recalculated model (cached values) and export the numbers the deck uses to deck_data.json."""
import json, os
from openpyxl import load_workbook
HERE = os.path.dirname(os.path.abspath(__file__))
wb = load_workbook(os.path.join(HERE, 'Public_ITS_Market_Model.xlsx'), data_only=True)
m = json.load(open(os.path.join(HERE, 'model_map.json')))
ws = wb['Market_2025']; wf = wb['Forecast']; wbu = wb['BottomUp_NA']
def row(sheet, r, cols): return [sheet.cell(r, c).value for c in cols]
out = {}
out['market_rows'] = [{'label': ws.cell(r,1).value, 'total': ws.cell(r,2).value, 'hw': ws.cell(r,3).value, 'sw': ws.cell(r,4).value, 'svc': ws.cell(r,5).value, 'geo': ws.cell(r,6).value, 'block': ws.cell(r,8).value} for r in range(5, m['market_total_row'])]
out['total_2025'] = ws.cell(m['market_total_row'], 2).value
out['segments'] = {k: {'total': ws.cell(r,2).value, 'hw': ws.cell(r,3).value, 'sw': ws.cell(r,4).value, 'svc': ws.cell(r,5).value, 'share': ws.cell(r,6).value} for k, r in m['seg_rows'].items()}
out['contestable_2025'] = ws.cell(m['contest_row'], 2).value
out['ccs_2025'] = ws.cell(m['ccs_row'], 2).value
out['components'] = {k: {'value': ws.cell(r,2).value, 'share': ws.cell(r,3).value} for k, r in m['comp_rows'].items()}
out['geos'] = {k: {'total': ws.cell(r,2).value, 'bus': ws.cell(r,3).value, 'ccs': ws.cell(r,4).value, 'other': ws.cell(r,5).value, 'share': ws.cell(r,6).value} for k, r in m['geo_rows'].items()}
years = list(range(2025, 2032))
f = m['forecast']
out['years'] = years
out['forecast_seg'] = {k: {'cagr': wf.cell(r,5).value, 'values': [wf.cell(r,c).value for c in range(7,14)]} for k, r in f['seg'].items()}
out['forecast_total'] = {'cagr': wf.cell(f['seg_total'],5).value, 'values': [wf.cell(f['seg_total'],c).value for c in range(7,14)]}
out['forecast_contest'] = {'cagr': wf.cell(f['contest'],5).value, 'values': [wf.cell(f['contest'],c).value for c in range(7,14)]}
out['forecast_geo'] = {k: {'cagr': wf.cell(r,5).value, 'values': [wf.cell(r,c).value for c in range(7,14)]} for k, r in f['geo'].items()}
out['forecast_comp'] = {k: {'cagr': wf.cell(r,5).value, 'values': [wf.cell(r,c).value for c in range(7,14)]} for k, r in f['comp'].items()}
out['forecast_scen'] = {k: {'cagr': wf.cell(r,5).value, 'values': [wf.cell(r,c).value for c in range(7,14)]} for k, r in f['scen'].items()}
out['forecast_rows'] = [{'label': wf.cell(r,1).value, 'low': wf.cell(r,2).value, 'base': wf.cell(r,3).value, 'high': wf.cell(r,4).value, 'values': [wf.cell(r,c).value for c in range(7,14)]} for r in range(f['first'], f['last']+1)]
bu = {}
for r in range(5, 45):
    lab = wbu.cell(r,1).value
    if lab and wbu.cell(r,2).value is not None: bu[lab] = wbu.cell(r,2).value
out['bottom_up'] = bu
wi = wb['Inputs']
inputs = {}
for k, ref in m['inputs'].items():
    r = int(ref.split('$')[-1]); inputs[k] = wi.cell(r, 2).value
out['inputs'] = inputs
json.dump(out, open(os.path.join(HERE, 'deck_data.json'), 'w'), indent=1, default=str)
print('exported', len(out['market_rows']), 'rows; total 2025 =', round(out['total_2025'],2), '; 2031 base =', round(out['forecast_total']['values'][-1],2), '; bottom-up NA ratio =', round(bu.get('Bottom-up as share of top-down', 0),3))
