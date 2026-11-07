// Build the 6-slide Public ITS case deck from the model export (deck_data.json).
const path = require('path');
const fs = require('fs');
const { applyTheme } = require('/root/.claude/skills/synced/bb6fd365-1a5f-4ed0-b47d-20358f3d4f02_a1537756-83aa-4e42-aa0d-dabc2bc599e7/pptx/scripts/apply_theme.js');
const F = require('./frame.js');
const D = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'model', 'deck_data.json'), 'utf8'));
const HEX = F.HEX;

const bn = (v, d = 1) => '$' + v.toFixed(d) + 'bn';
const pct = (v, d = 1) => (v * 100).toFixed(d) + '%';
const S = D.segments, FS = D.forecast_seg, FT = D.forecast_total, FC = D.forecast_contest, SC = D.forecast_scen;
const total25 = D.total_2025, total31 = FT.values[6];
const contest25 = D.contestable_2025, contest31 = FC.values[6];
const ccsShare = D.ccs_2025 / total25;
const busTot = S['Bus'].total, railOther = S['Rail other'].total, ccsUrban = S['Rail CCS urban'].total, ccsMain = S['Rail CCS mainline'].total;

(async () => {
  const { pres, C } = F.newDeck();
  const SRC = { fontSize: 8 };

  // helpers ------------------------------------------------------------
  const T = (slide, text, o) => slide.addText(text, Object.assign({ isTextBox: true, margin: 0, fontSize: 10, color: HEX.dk1, valign: 'top', fontFace: 'Calibri' }, o));
  const lines = (arr) => arr.map((t, i) => Object.assign({ text: t.text !== undefined ? t.text : t, options: Object.assign({ breakLine: i < arr.length - 1 }, t.options || {}) }));
  const cell = (text, o = {}) => ({ text, options: Object.assign({ fontSize: 9, color: HEX.dk1, valign: 'top', margin: 0.04 }, o) });
  const hcell = (text, o = {}) => ({ text, options: Object.assign({ fontSize: 9, bold: true, color: 'FFFFFF', fill: { color: HEX.dk1 }, valign: 'middle', margin: 0.04 }, o) });
  const tbl = (slide, rows, o) => slide.addTable(rows, Object.assign({ fontFace: 'Calibri', fontSize: 9, border: { type: 'solid', pt: 0.5, color: 'C7D3DA' }, autoPage: false }, o));
  const dots = (n) => '●'.repeat(n) + '○'.repeat(5 - n);
  const panel = (slide, x, y, w, h) => slide.addShape('rect', { x, y, w, h, fill: { color: HEX.lt2 }, line: { color: HEX.lt2 } });

  pres.addSection({ title: 'Public ITS market case' });
  const SEC = 'Public ITS market case';

  // ------------------------------------------------------------------ cover
  let s = pres.addSlide({ masterName: 'COVER', sectionTitle: SEC });
  s.addText('Public Intelligent Transportation Systems', { placeholder: 'title' });
  s.addText('Roadway (bus) and railway software, hardware and services\nMarket size, growth to 2031, competitive dynamics, risks and investment thesis for a new entrant\n\nWritten case  |  November 2026  |  Matthew Kang', { placeholder: 'body' });

  // ------------------------------------------------------------------ 1. Executive summary
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('Executive summary: a ~' + bn(total25, 0) + ' market growing ~' + pct(FT.cagr, 0) + ' a year, dominated by closed rail signalling; the attractive entry point is the ~' + bn(contest25, 0) + ' software-led pool', { placeholder: 'title' });
  s.addText('Executive summary', { placeholder: 'tracker' });
  const msgs = [
    ['Market size and segmentation', 'Public ITS for bus and passenger rail was ~' + bn(total25) + ' in 2025 (core scope, ex-fare collection). Rail control and signalling is ' + bn(D.ccs_2025) + ' (' + pct(ccsShare, 0) + '), bus and tram ITS ' + bn(busTot) + ', other rail ITS (passenger information, onboard video and counting, condition monitoring, detection) ' + bn(railOther) + '. Hardware is still ' + pct(D.components.Hardware.share, 0) + ' of value; Europe ' + pct(D.geos.Europe.share, 0) + ', Asia-Pacific ' + pct(D.geos['Asia-Pacific'].share, 0) + ', North America ' + pct(D.geos['North America'].share, 0) + '.'],
    ['Growth to 2031', 'Base case ' + pct(FT.cagr) + ' CAGR to ~' + bn(total31, 0) + ' (range ' + pct(SC.Low.cagr) + ' to ' + pct(SC.High.cagr) + '). Growth is modernisation-led, not expansion-led: EUR 85-100bn of unfunded ERTMS scope, CBTC resignalling of legacy metros (NYC $5.4bn 2025-29), 24,000 US buses reaching end of life by 2031, zero-emission turnover (60% of EU city-bus registrations) and AI enforcement. Software outgrows hardware; the contestable pool grows ' + pct(FC.cagr) + ' to ~' + bn(contest31, 0) + '.'],
    ['Competitive dynamics', 'Signalling is a four-player oligopoly (Siemens, Hitachi incl. Thales GTS, Alstom, CRSC in China) with 3-5 years of backlog and 25-30 year service tails. Bus ITS is consolidating into strategics (Hitachi bought Clever Devices, Modaxo bought Conduent transit at ~0.4x revenue) while SaaS challengers (Swiftly, Optibus, Via, Hayden AI) overlay legacy CAD/AVL and trade at 5-6x revenue.'],
    ['Risks and barriers', 'Incumbency (15-25 year system lives, contracts up to 20 years), 2-4 year procurement cycles, Buy America for hardware and SIL-4 certification in rail are structural. The near-term risk is funding: IIJA advance appropriations lapsed in September 2026 (-14% to -22% federal transit scenarios) and ERTMS is behind schedule. Leverage on hardware-heavy integrators has already failed once (Cubic).'],
    ['Investment thesis for a new entrant', 'Enter asset-light through a software or AI wedge that coexists with the incumbent stack (real-time and analytics, scheduling and demand-response, enforcement and safety video, charge management, rail condition monitoring), sell first to the under-250-vehicle tier and contracted operators via cooperative channels, and plan the exit to a strategic or permanent-capital buyer. Avoid signalling cores and leveraged hardware roll-ups.'],
  ];
  let y = 1.42;
  msgs.forEach(([h, b]) => {
    T(s, h, { x: 0.45, y, w: 2.1, h: 0.95, fontSize: 10.5, bold: true, color: HEX.dk1 });
    T(s, b, { x: 2.65, y, w: 6.05, h: 0.95, fontSize: 9.5, color: HEX.dk1 });
    s.addShape('line', { x: 0.45, y: y + 1.0, w: 8.25, h: 0, line: { color: 'C7D3DA', width: 0.5 } });
    y += 1.08;
  });
  panel(s, 9.0, 1.42, 3.9, 5.3);
  T(s, 'The market in four numbers', { x: 9.2, y: 1.55, w: 3.5, h: 0.3, fontSize: 10.5, bold: true, color: HEX.dk1 });
  const stats = [
    [bn(total25, 0), '2025 Public ITS market, bus + passenger rail, software, hardware and services (ex-fare)'],
    [bn(total31, 0), '2031 base case, ' + pct(FT.cagr) + ' CAGR (low ' + pct(SC.Low.cagr) + ', high ' + pct(SC.High.cagr) + ')'],
    [pct(ccsShare, 0), 'of 2025 value is rail control and signalling, held by four suppliers with 3-5 year backlogs'],
    [bn(contest25, 0) + ' to ' + bn(contest31, 0), 'contestable software-led pool (bus ITS + non-signalling rail ITS), ' + pct(FC.cagr) + ' CAGR'],
  ];
  let sy = 1.95;
  stats.forEach(([big, lab]) => { F.stat(s, big, lab, 9.2, sy, 3.5, { size: 22 }); sy += 1.2; });
  s.addText('Source: model built on Berg Insight (Mar 2026), UNIFE World Rail Market Study 2026, SCI Verkehr (Mar 2026), Global Market Insights (Aug 2026), FTA National Transit Database RY2025, company reports; see Public_ITS_Market_Model.xlsx.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 2. Market definition and size
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('Public ITS is a ~' + bn(total25, 0) + ' market in 2025; ' + pct(ccsShare, 0) + ' is rail signalling, so the software-led pool open to new entrants is ~' + bn(contest25, 0), { placeholder: 'title' });
  s.addText('Market size', { placeholder: 'tracker' });
  F.panelHeader(s, 'Segmentation framework: mode x functional domain x component layer', 0.45, 1.4, 6.35);
  const fw = [
    [hcell('Functional domain'), hcell('Roadway (bus, BRT, paratransit)'), hcell('Railway (metro, LRT, commuter, mainline passenger)')],
    [cell('A. Operations and fleet management', { bold: true }), cell('HW: onboard computer/AVL, MDT, radio | SW: CAD/AVL, scheduling, dispatch | SVC: integration, hosting'), cell('HW: train tracking, control-centre systems | SW: traffic management, crew and timetable planning')],
    [cell('B. Passenger information', { bold: true }), cell('HW: onboard and stop displays, annunciators | SW: real-time prediction, GTFS-RT, apps'), cell('HW: platform and onboard displays, PA | SW: real-time information, disruption management')],
    [cell('C. Safety, security and surveillance', { bold: true }), cell('HW: cameras, DVRs, collision-avoidance sensors | SW: AI incident detection, bus-lane enforcement'), cell('HW: onboard and station CCTV, intrusion sensors | SW: analytics, obstacle detection')],
    [cell('D. Asset, telematics and condition monitoring', { bold: true }), cell('HW: APC sensors, vehicle-health telematics | SW: asset management, energy and charge management'), cell('HW: APC, onboard sensors, trackside detectors (hot box, WILD) | SW: predictive maintenance, digital twins')],
    [cell('E. Train control and signalling', { bold: true }), cell('n/a (transit signal priority is a roadway adjacency)'), cell('HW: interlockings, wayside and onboard ETCS/CBTC/PTC | SW: ATO, ATS | SVC: 25-30 year maintenance')],
    [cell('Adjacent, excluded', { bold: true, color: HEX.dk2 }), cell('Fare collection and ticketing ($10-17bn), traffic management and tolling, rolling stock', { color: HEX.dk2 }), cell('Fare collection, rolling stock and TCMS, civil works, freight rail', { color: HEX.dk2 })],
  ];
  fw.forEach((row, i) => row.forEach(c => { if (i > 0) c.options.fontSize = 8.5; }));
  tbl(s, fw, { x: 0.45, y: 1.72, w: 6.35, colW: [1.4, 2.475, 2.475], rowH: [0.26, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46] });
  T(s, 'How the number is built: bus anchored on Berg Insight (Europe EUR 2.55bn, North America EUR 1.22bn, less a 20% haircut for fare content) and scaled to rest of world on GMI regional mix; signalling anchored on UNIFE rail control (EUR 24.9bn) carved to passenger rail (74%) by region, cross-checked with SCI Verkehr (~EUR 20bn) and a vendor revenue sum (~EUR 17bn); component mix from GMI; US floor from NTD communication and information capex ($1.9bn). A North America bottom-up (83k buses x ~$6.5k per bus-year) explains ~' + pct(D.bottom_up['Bottom-up as share of top-down'], 0) + ' of the top-down bus figure; the rest is opex-funded services and non-vehicle systems.', { x: 0.45, y: 5.3, w: 6.35, h: 1.1, fontSize: 8.5, color: HEX.dk2 });
  // chart: stacked by segment and component
  const segs = [['Bus and tram ITS', 'Bus'], ['Rail signalling: urban', 'Rail CCS urban'], ['Rail signalling: mainline and commuter', 'Rail CCS mainline'], ['Rail other ITS', 'Rail other']];
  const chartData = [
    { name: 'Hardware', labels: segs.map(x => x[0]), values: segs.map(x => +S[x[1]].hw.toFixed(2)) },
    { name: 'Software', labels: segs.map(x => x[0]), values: segs.map(x => +S[x[1]].sw.toFixed(2)) },
    { name: 'Services', labels: segs.map(x => x[0]), values: segs.map(x => +S[x[1]].svc.toFixed(2)) },
  ];
  F.panelHeader(s, '2025 market by segment and component layer (USD bn, core scope)', 7.05, 1.4, 5.85);
  s.addChart(pres.ChartType.bar, chartData, Object.assign({}, F.chartBase, { x: 7.05, y: 1.75, w: 5.85, h: 2.7, barDir: 'bar', barGrouping: 'stacked', showValue: true, dataLabelPosition: 'ctr', dataLabelColor: 'FFFFFF', dataLabelFontSize: 8, dataLabelFormatCode: '0.0', showLegend: true, legendPos: 'b', valAxisHidden: false, valAxisLabelFormatCode: '0', catAxisLabelFontSize: 8.5, valAxisMaxVal: 16, barGapWidthPct: 60, chartColors: [HEX.dk1, HEX.accent2, HEX.accent4] }));
  const segRows = [[hcell('Segment'), hcell('2025', { align: 'right' }), hcell('Share', { align: 'right' }), hcell('What sits inside')],
    [cell('Bus and tram ITS'), cell(bn(busTot), { align: 'right' }), cell(pct(S.Bus.share, 0), { align: 'right' }), cell('CAD/AVL, scheduling, PIS, APC, video; Europe $2.3bn, NA $1.1bn, RoW $1.2bn')],
    [cell('Rail signalling, urban'), cell(bn(ccsUrban), { align: 'right' }), cell(pct(S['Rail CCS urban'].share, 0), { align: 'right' }), cell('CBTC and ATO on 20,000 km metro, 16,000 km LRT; GMI sizes CBTC at $4.9bn')],
    [cell('Rail signalling, mainline and commuter'), cell(bn(ccsMain), { align: 'right' }), cell(pct(S['Rail CCS mainline'].share, 0), { align: 'right' }), cell('ETCS/ERTMS, interlockings, PTC; Europe ~60% of passenger signalling')],
    [cell('Rail other ITS'), cell(bn(railOther), { align: 'right' }), cell(pct(S['Rail other'].share, 0), { align: 'right' }), cell('PIS, onboard CCTV/APC, condition monitoring, trackside detection')],
    [cell('Total core scope', { bold: true }), cell(bn(total25), { bold: true, align: 'right' }), cell('100%', { bold: true, align: 'right' }), cell('Hardware ' + pct(D.components.Hardware.share, 0) + ', software ' + pct(D.components.Software.share, 0) + ', services ' + pct(D.components.Services.share, 0), { bold: true })],
    [cell('By geography', { color: HEX.dk2 }), cell('', {}), cell('', {}), cell([['Europe','Europe'], ['Asia-Pacific','APAC'], ['North America','NA'], ['Rest of world','RoW']].map(([g, a]) => a + ' ' + bn(D.geos[g].total) + ' (' + pct(D.geos[g].share, 0) + ')').join('; '), { color: HEX.dk2 })],
  ];
  segRows.forEach((row, i) => row.forEach(c => { if (i > 0) c.options.fontSize = 8.5; }));
  tbl(s, segRows, { x: 7.05, y: 4.55, w: 5.85, colW: [1.7, 0.6, 0.5, 3.05], rowH: [0.24, 0.3, 0.3, 0.3, 0.3, 0.27, 0.27] });
  s.addText('Source: Berg Insight Public Transport ITS in Europe and North America 10th ed.; UNIFE WRMS 2026 abstract; SCI Verkehr CCS study 2026; Global Market Insights APTS 2026; Eurostat and UITP network data for passenger and urban carve-outs; FTA NTD RY2025. Model sheets Market_2025 and TopDown.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 3. Growth drivers and outlook
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('Mandated modernisation and fleet turnover carry the market to ~' + bn(total31, 0) + ' by 2031 (' + pct(FT.cagr) + ' CAGR); software grows fastest and the contestable pool reaches ~' + bn(contest31, 0), { placeholder: 'title' });
  s.addText('Growth and outlook', { placeholder: 'tracker' });
  F.panelHeader(s, 'Public ITS market 2025-2031, base case (USD bn)', 0.45, 1.4, 5.7);
  const yrs = D.years.map(String);
  const fcData = [
    { name: 'Bus and tram ITS', labels: yrs, values: FS.Bus.values.map(v => +v.toFixed(2)) },
    { name: 'Rail signalling (passenger)', labels: yrs, values: FS['Rail CCS'].values.map(v => +v.toFixed(2)) },
    { name: 'Rail other ITS', labels: yrs, values: FS['Rail other'].values.map(v => +v.toFixed(2)) },
  ];
  s.addChart([
    { type: pres.ChartType.bar, data: fcData, options: { barDir: 'col', barGrouping: 'stacked', showValue: false, chartColors: [HEX.accent2, HEX.dk1, HEX.accent4], barGapWidthPct: 45 } },
    { type: pres.ChartType.line, data: [{ name: 'Total', labels: yrs, values: FT.values.map(v => +v.toFixed(1)) }], options: { chartColors: [HEX.accent3], lineSize: 1.5, lineDataSymbol: 'circle', lineDataSymbolSize: 5, showValue: true, dataLabelPosition: 't', dataLabelFormatCode: '0.0', dataLabelFontSize: 8.5, dataLabelColor: HEX.dk1 } },
  ], Object.assign({}, F.chartBase, { x: 0.45, y: 1.75, w: 5.7, h: 2.95, showLegend: true, legendPos: 'b', valAxisLabelFormatCode: '0', valAxisMaxVal: 45, catAxisLabelFontSize: 8.5 }));
  const scRows = [[hcell('Scenario'), hcell('2031', { align: 'right' }), hcell('CAGR', { align: 'right' }), hcell('Contestable 2031', { align: 'right' }), hcell('What has to be true')],
    [cell('Low'), cell(bn(SC.Low.values[6]), { align: 'right' }), cell(pct(SC.Low.cagr), { align: 'right' }), cell(bn(SC['Contestable Low'].values[6]), { align: 'right' }), cell('US funding at CR levels (-20%), ERTMS keeps slipping, fiscal-cliff agencies defer refresh')],
    [cell('Base', { bold: true }), cell(bn(SC.Base.values[6]), { bold: true, align: 'right' }), cell(pct(SC.Base.cagr), { bold: true, align: 'right' }), cell(bn(SC['Contestable Base'].values[6]), { bold: true, align: 'right' }), cell('Berg and SCI/UNIFE trajectories hold; formula funding sustains refresh; committed frameworks deliver')],
    [cell('High'), cell(bn(SC.High.values[6]), { align: 'right' }), cell(pct(SC.High.cagr), { align: 'right' }), cell(bn(SC['Contestable High'].values[6]), { align: 'right' }), cell('North America repeats its 2022-25 pace (11% p.a.), FRMCS and GoA4 conversions start early, AI enforcement scales')],
  ];
  tbl(s, scRows, { x: 0.45, y: 4.8, w: 5.7, colW: [0.55, 0.6, 0.55, 0.95, 3.05], rowH: [0.24, 0.42, 0.42, 0.42] });
  T(s, 'Segment CAGRs (base): bus ' + pct(FS.Bus.cagr) + ', rail signalling ' + pct(FS['Rail CCS'].cagr) + ', rail other ' + pct(FS['Rail other'].cagr) + '; software ' + pct(D.forecast_comp.Software.cagr) + ' vs hardware ' + pct(D.forecast_comp.Hardware.cagr) + '.', { x: 0.45, y: 6.45, w: 5.7, h: 0.3, fontSize: 8.5, color: HEX.dk2 });
  F.panelHeader(s, 'Drivers and headwinds behind the forecast', 6.4, 1.4, 6.5);
  const drv = [[hcell('Driver'), hcell('Segment'), hcell('Effect', { align: 'center' }), hcell('Quantified evidence')],
    [cell('ERTMS/ETCS mandate', { bold: true }), cell('Rail Europe'), cell('+ H', { align: 'center' }), cell('EUR 75-85bn trackside and EUR 10-15bn onboard to complete TEN-T; only ~10% of km and 19% of fleet equipped at end-2024; DB EUR 6.3bn framework, RFI EUR 2.7bn for 4,220 km')],
    [cell('Legacy metro resignalling', { bold: true }), cell('Rail urban'), cell('+ H', { align: 'center' }), cell('NYC still 85% fixed-block: $5.4bn CBTC in 2025-29 plan at $20-45m per km; London, Paris RER, Toronto, Sydney, Copenhagen GoA4; ~90% of European CCS volume is modernisation')],
    [cell('Bus fleet and system end of life', { bold: true }), cell('Bus NA/EU'), cell('+ H', { align: 'center' }), cell('24,100 US buses reach useful-life benchmark 2026-31 plus 12,600 already past it; CAD/AVL systems of 2004-2012 vintage being replaced (LA Metro $130m, TfL GBP 160m)')],
    [cell('Zero-emission turnover', { bold: true }), cell('Bus'), cell('+ M', { align: 'center' }), cell('60% of EU city-bus registrations zero-emission in 2025 (+48%); Clean Vehicles Directive 65% 2026-30; 8,100 US ZEBs funded; charge and energy management joins the scheduling stack')],
    [cell('AI enforcement and safety video', { bold: true }), cell('Bus'), cell('+ M', { align: 'center' }), cell('MTA ACE from 123 to 1,900+ buses ($141m contract), 11 US agencies on Hayden AI; FRA locomotive cameras by Oct 2027; citation revenue makes it self-funding')],
    [cell('FRMCS, predictive maintenance, cyber', { bold: true }), cell('Rail'), cell('+ M', { align: 'center' }), cell('GSM-R end of support ~2035, FRMCS in 2027 TSI; Hitachi HMAX on all new trains from 2027; TSA cyber rule $1.26bn over 10 years on passenger rail')],
    [cell('US federal funding reset', { bold: true }), cell('Bus/rail NA'), cell('- H', { align: 'center' }), cell('IIJA advance appropriations ($4.25bn/yr) lapsed Sep 2026; House bill -14% vs IIJA with no Low-No; FY2027 request -22%; formula funds (+10%) favour refresh over expansion')],
    [cell('Rail budget stretch-outs', { bold: true }), cell('Rail Europe/China'), cell('- M', { align: 'center' }), cell('Network Rail CP7 ETCS cut from GBP 1.54bn to 0.99bn; DB withdrew its ETCS migration strategy (2025); China urban-rail investment -8.9% in 2024')],
  ];
  tbl(s, drv, { x: 6.4, y: 1.72, w: 6.5, colW: [1.45, 0.85, 0.5, 3.7], rowH: [0.24, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55] });
  s.addText('Source: model Forecast and Drivers sheets; European Commission Third ERTMS Work Plan (Feb 2026); MTA 2025-29 Capital Program; FTA NTD RY2025; ACEA; CALSTART; Network Rail CP7 plan (Mar 2026); DB; APTA; FTA apportionment notices and H.R. 8870.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 4. Competitive dynamics
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('Rail signalling is a four-player oligopoly protected by backlog and certification; bus ITS is consolidating into strategics while SaaS challengers unbundle the legacy stack', { placeholder: 'title' });
  s.addText('Competitive dynamics', { placeholder: 'tracker' });
  F.panelHeader(s, 'Landscape by segment', 0.45, 1.4, 7.75);
  const land = [[hcell('Segment (2025 pool)'), hcell('Scale leaders'), hcell('Challengers and specialists'), hcell('Structure and share evidence')],
    [cell('Rail signalling, passenger (' + bn(D.ccs_2025, 0) + ')', { bold: true }), cell('Siemens Mobility (rail infra ~EUR 4.1bn), Hitachi Rail (EUR 7.8bn Mobility, >50% signalling, incl. Thales GTS), Alstom Signalling (EUR 2.7bn), CRSC (EUR 4.3bn, China)'), cell('Wabtec (PTC, Frauscher), KB Signaling (ex-Alstom NA), Stadler and CAF signalling (own-fleet pull), MERMEC (to Siemens), Nippon Signal, Kyosan'), cell('Each of the four holds 13-22% of world CCS; big three ~two-thirds ex-China; backlog 3.4-5.4x revenue; 10-30 year frameworks (DB, OBB, SBB); SIL-4 and ERA/FRA approval')],
    [cell('Rail other ITS (' + bn(railOther) + ')', { bold: true }), cell('OEM platforms: Hitachi HMAX, Siemens Railigent X, Alstom HealthHub; Nokia (FRMCS)'), cell('Konux, Sensonic, Icomera, Nomad (Alstom), Televic, Dilax (INIT), Teleste, Rail Vision'), cell('Value captured inside OEM service contracts; independents in detection, connectivity, PIS and perception AI')],
    [cell('Bus integrated systems (' + bn(busTot) + ')', { bold: true }), cell('Modaxo/Constellation (Trapeze, Vontas, Routeward ex-Conduent; 3,500+ customers), Hitachi Rail (Clever Devices, 8 of top-10 NA agencies, >$220m), INIT (EUR 330m), Cubic (Umo/NextBus)'), cell('IVU (DACH), Equans and GMV (France, Iberia, LatAm), Avail, Luminator, Hanover, Passio, ETA, Pilotfish, Consat'), cell('Top five hold ~50-60% of the NA pool; 90%+ of EU/NA buses already equipped so growth is refresh and upsell; incumbents retain accounts for 15-20 years but lose end-of-life rebids (TfL, LA Metro)')],
    [cell('Bus SaaS and AI layers', { bold: true }), cell('Via (NYSE, $434m revenue), Optibus ($1.3bn valuation), Swiftly (200+ agencies), Hayden AI (2,500 buses)'), cell('Spare, Transit app, Moovit (Mobileye), Masabi (fare), Samsara and Geotab entering from municipal fleets'), cell('Subscription, little or no hardware; overlay legacy CAD/AVL at 100+ agencies; venture marks peaked 2021-22, exits now to strategics or IPO')],
  ];
  tbl(s, land, { x: 0.45, y: 1.72, w: 7.75, colW: [1.45, 2.3, 1.95, 2.05], rowH: [0.24, 1.15, 0.7, 1.25, 0.95] });
  F.panelHeader(s, 'Four dynamics reshaping the market', 8.45, 1.4, 4.45);
  s.addText(lines([
    { text: 'Strategic consolidation at low multiples. ', options: { bold: true } }, 'Hitachi-Thales GTS (EUR 1.66bn, ~1x revenue), Hitachi-Clever Devices (2026), Modaxo-Conduent transit ($164m, ~0.4x), Siemens-MERMEC, Wabtec-Frauscher ($792m), Knorr-Alstom NA ($690m). Sponsors are largely absent; Modaxo never sells.',
    { text: 'Hardware to software unbundling. ', options: { bold: true } }, 'ITxPT standards, cloud CAD/AVL (Swiftly 2026) and real-time overlays (Optibus) cut onboard content; INIT now reports Cloud and Passenger Intelligence units; Luminator repositions from hardware to digital.',
    { text: 'Services and long contracts as the moat. ', options: { bold: true } }, 'INIT contracts up to 20 years (EUR 1bn obligations), Alstom services mid-teens margin vs 6% group, 25-year CBTC maintenance tails; integrators earn 9-12% EBIT, SaaS ~40% gross margin but near-zero EBITDA.',
    { text: 'Valuation gap. ', options: { bold: true } }, 'Integrators 1.0-2.6x revenue (INIT, IVU), transit SaaS 5.6x (Via), Cubic LBO at 15.7x EBITDA ended in a 2025 recap; Alstom (0.3x sales) is a possible carve-out source.',
  ]), { x: 8.6, y: 1.8, w: 4.2, h: 3.25, fontSize: 9, color: HEX.dk1, valign: 'top', margin: 0, isTextBox: true, paraSpaceAfter: 4 });
  const dl = [[hcell('Transaction / comp'), hcell('Value', { align: 'right' }), hcell('Multiple', { align: 'right' })],
    [cell('Thales GTS to Hitachi (2024)'), cell('EUR 1.66bn', { align: 'right' }), cell('~1.0x rev', { align: 'right' })],
    [cell('Conduent transit to Modaxo (2026)'), cell('$164m', { align: 'right' }), cell('0.44x rev', { align: 'right' })],
    [cell('Alstom Signaling NA to Knorr (2024)'), cell('$690m', { align: 'right' }), cell('~2.2x rev', { align: 'right' })],
    [cell('Cubic take-private (2021)'), cell('~$3.0bn EV', { align: 'right' }), cell('15.7x EBITDA', { align: 'right' })],
    [cell('Via (trading, Nov 2026)'), cell('EV $2.75bn', { align: 'right' }), cell('5.6x rev', { align: 'right' })],
    [cell('INIT / IVU (trading)'), cell('EUR 0.36bn / 0.46bn', { align: 'right' }), cell('1.0x / 2.6x rev', { align: 'right' })],
  ];
  tbl(s, dl, { x: 8.45, y: 5.15, w: 4.45, colW: [2.25, 1.2, 1.0], rowH: [0.21, 0.21, 0.21, 0.21, 0.21, 0.21, 0.21] });
  s.addText('Source: company reports (Siemens, Hitachi, Alstom, CRSC, Wabtec, INIT, IVU, Via 8-K/10-Q), Berg Insight vendor ranking, deal announcements, trading data 6 Nov 2026; model Competitors and Deals_Comps sheets. Shares are indicative.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 5. Risks and barriers
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('Barriers to entry are structural (incumbency, procurement, certification); the near-term risk to the forecast is the US funding reset and European signalling slippage', { placeholder: 'title' });
  s.addText('Risks and barriers', { placeholder: 'tracker' });
  F.panelHeader(s, 'Risk register (severity = likelihood x impact, analyst scoring)', 0.45, 1.4, 7.6);
  const rk = [[hcell('Risk / barrier'), hcell('Type'), hcell('Severity', { align: 'center' }), hcell('Evidence')],
    [cell('Incumbency and 15-25 year system lives', { bold: true }), cell('Barrier'), cell(dots(5), { align: 'center', color: HEX.accent2 }), cell('LA Metro ATMS 2004-2025, TfL iBus 2009-2024; INIT contracts up to 20 years and rates new-entrant risk low; Modaxo never sells; Clever serves 8 of the 10 largest NA agencies')],
    [cell('Rail certification and three-player signalling', { bold: true }), cell('Barrier'), cell(dots(5), { align: 'center', color: HEX.accent2 }), cell('SIL-4, ERA and FRA approvals, 25-30 year service tails; only two qualified CBTC suppliers on NYC subway; 10-30 year frameworks')],
    [cell('Procurement cycle and protests', { bold: true }), cell('Barrier'), cell(dots(4), { align: 'center', color: HEX.accent2 }), cell('2-4 years award-to-live under 2 CFR 200; LA Metro plan (2016) to go-live (2028); awards subject to protest; $10.8m programme-support consultant')],
    [cell('US federal funding reset', { bold: true }), cell('Market'), cell(dots(4), { align: 'center', color: HEX.accent2 }), cell('IIJA advance appropriations lapsed; extension implies ~20% transit cut; House bill -14%; FY2027 request -22%; FTA staff -30%; SEPTA/PRT deficits unresolved')],
    [cell('Buy America / BABA for hardware', { bold: true }), cell('Barrier'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('>70% domestic content and US final assembly; 55% for manufactured products; OIG questioned $30.8m at SEPTA; INIT runs two Virginia plants to comply')],
    [cell('ERTMS and resignalling slippage', { bold: true }), cell('Market'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('EC: deployment significantly behind schedule; CP7 ETCS cut 35%; DB withdrew migration strategy; Kavach dates slipped twice')],
    [cell('Cybersecurity compliance and incidents', { bold: true }), cell('Both'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('TSA proposed rule $1.26bn/10 years on passenger rail; TfL 2024 attack GBP 39m; TTC 2021 ransomware took down CAD/AVL; IEC 62443 written into UK tenders')],
    [cell('SaaS eligibility under 80/20 capital grants', { bold: true }), cell('Market'), cell(dots(2), { align: 'center', color: HEX.accent2 }), cell('Capital definition covers leasing and preventive maintenance; FTA declined SaaS guidance (2025); House bill would add an explicit SaaS clause')],
    [cell('Leverage on hardware-heavy integrators', { bold: true }), cell('Investment'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('Cubic: ~11x debt/EBITDA at LBO, 2025 recap, Jan 2026 interest deferral; Alstom profit warning; Kapsch standstill')],
    [cell('Long tail and agency capacity', { bold: true }), cell('Market'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('773 US agencies with <50 buses hold 16% of fleet; enterprise CAD/AVL economics depend on ~70-90 accounts; staffing shortages at agencies and FTA')],
  ];
  tbl(s, rk, { x: 0.45, y: 1.72, w: 7.6, colW: [1.9, 0.7, 0.75, 4.25], rowH: [0.24, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47] });
  F.panelHeader(s, 'What the barriers mean for an entrant', 8.3, 1.4, 4.6);
  const imp = [
    ['Displacement is a decade-long game', 'Win-rates at end-of-life rebids are real (TfL to INIT, LA Metro to Clever) but each year only a handful of large accounts come up. Plan on coexisting with the incumbent stack and taking modules, not the core, first.'],
    ['Hardware-led entry needs a US manufacturing partner', 'Buy America, tariffs and inventory risk make a pure-play hardware entry unattractive; partner or acquire for onboard units and leave hardware margin to the OEM channel (Gillig and New Flyer build two-thirds of US buses).'],
    ['Funding mechanics shape the product', 'Capital grants pay 80% of hardware and perpetual licences; subscriptions come from local operating budgets unless structured as leases or preventive maintenance, so pricing and contract form matter as much as features.'],
    ['Rail cores are closed; adjacencies are not', 'Signalling, ATO and FRMCS cores need SIL-4 and 10-15 year programmes; condition monitoring, cyber, onboard connectivity and detection are contestable and sold to the same operators.'],
  ];
  let iy = 1.8;
  imp.forEach(([h, b]) => {
    T(s, h, { x: 8.45, y: iy, w: 4.3, h: 0.25, fontSize: 9.5, bold: true, color: HEX.accent2 });
    T(s, b, { x: 8.45, y: iy + 0.26, w: 4.3, h: 0.9, fontSize: 9, color: HEX.dk1 });
    iy += 1.2;
  });
  s.addText('Source: agency board documents (LA Metro Legistar, TfL), INIT annual report 2025 risk section, TSA NPRM (Nov 2024), DOT OIG audit (Jul 2024), FTA Federal Register notices, EC ERTMS Work Plan (2026), Network Rail CP7 plan, NTD RY2025; model Risks sheet.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 6. Investment thesis
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('A new entrant should enter asset-light through a software or AI wedge in the ~' + bn(contest25, 0) + ' contestable pool, coexist with incumbents, and exit to a strategic; avoid signalling cores and leveraged hardware', { placeholder: 'title' });
  s.addText('Investment thesis', { placeholder: 'tracker' });
  F.panelHeader(s, 'Where to play: four wedges that sit beside the incumbent stack', 0.45, 1.4, 12.45);
  const cards = [
    ['Real-time, analytics and cloud CAD/AVL overlay', 'Bus ops and passenger information; ~$2.5bn of the bus pool is software and services', 'Legacy systems rated poorly (6% strongly recommend); overlays already at 100+ agencies; incremental module displacement at refresh'],
    ['AI enforcement and safety video', 'Fastest-scaling bus hardware+software category; self-funding via citations', 'MTA 1,900+ buses, 11 US agencies, UK type approval; adjacent to onboard video refresh ($9-25k per bus) and FRA camera mandate'],
    ['Scheduling, demand-response and ZEB energy management', 'Planning software plus charge management joins the stack as fleets electrify', 'EU city buses 60% zero-emission in new registrations; Optibus and Via show agencies buy planning as SaaS; e-bus ITS growing 21-27% p.a.'],
    ['Rail condition monitoring, detection and cyber', 'Contestable rail adjacencies (~$3bn pool, 7% growth) sold to the same operators', 'OEMs monetise inside service contracts, leaving independents (Konux, Sensonic, Icomera); TSA and IEC 62443 create recurring cyber spend'],
  ];
  let cx = 0.45;
  cards.forEach(([h, p, w]) => {
    panel(s, cx, 1.75, 3.0, 1.75);
    T(s, h, { x: cx + 0.12, y: 1.82, w: 2.76, h: 0.42, fontSize: 9.5, bold: true, color: HEX.dk1 });
    T(s, p, { x: cx + 0.12, y: 2.24, w: 2.76, h: 0.45, fontSize: 8.5, color: HEX.accent2, bold: true });
    T(s, w, { x: cx + 0.12, y: 2.7, w: 2.76, h: 0.78, fontSize: 8.5, color: HEX.dk1 });
    cx += 3.15;
  });
  F.panelHeader(s, 'How to enter: archetypes compared', 0.45, 3.65, 7.9);
  const arch = [[hcell('Archetype'), hcell('Example'), hcell('For'), hcell('Against'), hcell('Entry value')],
    [cell('Build or scale a SaaS wedge', { bold: true }), cell('Swiftly, Optibus, Hayden AI'), cell('Asset-light, 40%+ gross margin, coexists with incumbents, long tail reachable via cooperative contracts'), cell('Slow land-and-expand, losses to scale (Via -8% EBITDA), SaaS funding friction'), cell('5-6x revenue (Via); exits to strategics')],
    [cell('Buy a founder-owned mid-market incumbent and re-platform', { bold: true }), cell('Avail, GIRO, Hanover, ETA, Passio'), cell('Installed base and 5-20 year service tails at 1-2.6x revenue; immediate procurement credibility'), cell('Hardware and project risk, ageing code, Buy America, key-person risk'), cell('1.0-2.6x revenue / 7-15x EBITDA')],
    [cell('Carve-out from a stressed strategic', { bold: true }), cell('Alstom digital assets, Cubic CTS'), cell('Scale at distressed prices; Alstom targets EUR 2bn of disposals'), cell('Complex separation, leverage history, customer concentration'), cell('0.3-1x revenue')],
    [cell('Roll-up of point solutions', { bold: true }), cell('Modaxo model'), cell('Fragmented long tail of private vendors'), cell('Modaxo and Hitachi already consolidating; permanent-capital competition for targets'), cell('0.4-1x revenue')],
  ];
  tbl(s, arch, { x: 0.45, y: 3.97, w: 7.9, colW: [1.7, 1.25, 2.0, 1.95, 1.0], rowH: [0.24, 0.62, 0.62, 0.5, 0.5] });
  F.panelHeader(s, 'What you need to believe, and what to diligence', 8.6, 3.65, 4.3);
  s.addText(lines([
    { text: 'Need to believe', options: { bold: true, color: HEX.accent2 } },
    { text: '1. Agencies will fund subscriptions from operating budgets or lease structures as incumbents move to 10-20 year service deals.', options: { bullet: false } },
    '2. Refresh windows open on schedule: 24k US buses and the 2004-2012 CAD/AVL cohort by 2031, with federal formula funding at 85-100% of IIJA levels.',
    '3. AI enforcement, safety video and electrification keep adding new budget lines rather than cannibalising core ITS spend.',
    { text: 'Diligence questions', options: { bold: true, color: HEX.accent2 } },
    '1. Win-rate and tenure at rebids by tier (target: a sourced retention rate, not anecdotes).',
    '2. True per-vehicle economics of SaaS vs capex awards (TfL iBus2 at ~$2.3k per bus-year is the clean benchmark).',
    '3. Exposure to the FY2027 funding scenarios and to fiscal-cliff agencies in the customer base.',
    '4. Exit map: which strategics (Hitachi, Siemens, Modaxo, Via) would buy, and at what multiple, given Modaxo never sells.',
  ]), { x: 8.72, y: 3.98, w: 4.1, h: 2.8, fontSize: 8.5, color: HEX.dk1, valign: 'top', margin: 0, isTextBox: true, paraSpaceAfter: 3 });
  s.addText('Source: model Market_2025, Forecast, Competitors, Deals_Comps and Risks sheets; Via S-1 and 8-K, INIT 2025 annual report, Modaxo and Hitachi announcements, Swiftly, Optibus and Hayden AI releases, TfL iBus2 award.', { placeholder: 'source' });

  const out = path.join(__dirname, 'Public_ITS_Market_Case.pptx');
  await pres.writeFile({ fileName: out });
  await applyTheme(out, F.THEME);
  console.log('wrote', out);
})();
