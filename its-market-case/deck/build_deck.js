// Build the Public ITS case deck (v2) from the model export (deck_data.json).
const path = require('path');
const fs = require('fs');
const { applyTheme } = require('/root/.claude/skills/synced/bb6fd365-1a5f-4ed0-b47d-20358f3d4f02_a1537756-83aa-4e42-aa0d-dabc2bc599e7/pptx/scripts/apply_theme.js');
const F = require('./frame.js');
const D = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'model', 'deck_data.json'), 'utf8'));
const HEX = F.HEX;

const bn = (v, d = 1) => '$' + v.toFixed(d) + 'bn';
const pct = (v, d = 1) => (v * 100).toFixed(d) + '%';
const S = D.segments, FS = D.forecast_seg, FT = D.forecast_total, FC = D.forecast_contest, SC = D.forecast_scen, SAM = D.forecast_sam, OP = D.open, TI = D.tiers, AP = D.apps, SE = D.sens, TH = D.thesis;
const total25 = D.total_2025, total31 = FT.values[6];
const ccsShare = D.ccs_2025 / total25;
const busTot = S['Bus'].total, railOther = S['Rail other'].total, ccsUrban = S['Rail CCS urban'].total, ccsMain = S['Rail CCS mainline'].total;
const sam25 = OP.open.total, sam31 = SAM.values[6];
const core25 = TI.core.total;
// colours: segment palette constant across slides
const COL_BUS = HEX.accent2, COL_SIG = HEX.dk1, COL_OTH = HEX.accent3, COL_GREY = HEX.accent5;

(async () => {
  const { pres, C } = F.newDeck();
  const T = (slide, text, o) => slide.addText(text, Object.assign({ isTextBox: true, margin: 0, fontSize: 10, color: HEX.dk1, valign: 'top', fontFace: 'Calibri' }, o));
  const lines = (arr) => arr.map((t, i) => ({ text: t.text !== undefined ? t.text : t, options: Object.assign({ breakLine: i < arr.length - 1 }, t.options || {}) }));
  const cell = (text, o = {}) => ({ text, options: Object.assign({ fontSize: 9.5, color: HEX.dk1, valign: 'top', margin: 0.04 }, o) });
  const hcell = (text, o = {}) => ({ text, options: Object.assign({ fontSize: 9.5, bold: true, color: 'FFFFFF', fill: { color: HEX.dk1 }, valign: 'middle', margin: 0.04 }, o) });
  const tbl = (slide, rows, o) => slide.addTable(rows, Object.assign({ fontFace: 'Calibri', fontSize: 9.5, border: { type: 'solid', pt: 0.5, color: 'C7D3DA' }, autoPage: false }, o));
  const dots = (n) => '●'.repeat(n) + '○'.repeat(5 - n);
  const panel = (slide, x, y, w, h, color) => slide.addShape('rect', { x, y, w, h, fill: { color: color || HEX.lt2 }, line: { color: color || HEX.lt2 } });
  const SEC = 'Public ITS market case';
  pres.addSection({ title: SEC });

  // ------------------------------------------------------------------ cover
  let s = pres.addSlide({ masterName: 'COVER', sectionTitle: SEC });
  s.addText('Public Intelligent Transportation Systems', { placeholder: 'title' });
  s.addText('Roadway (bus) and railway software, hardware and services\nMarket size and segmentation, growth to 2031, competitive dynamics, risks and barriers, investment thesis for a new entrant\n\nWritten case submission  |  November 2026  |  Matthew Kang  |  Model: Public_ITS_Market_Model.xlsx', { placeholder: 'body' });

  // ------------------------------------------------------------------ 1. Executive summary
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('The investable pool in Public ITS is ~' + bn(sam25, 0) + ' of software and services growing ~' + pct(SAM.cagr, 0) + ' inside a ~' + bn(total25, 0) + ', mostly closed market; we would enter via buy-and-build in North America', { placeholder: 'title' });
  s.addText('Executive summary', { placeholder: 'tracker' });
  panel(s, 0.45, 1.4, 12.45, 0.62);
  T(s, [{ text: 'Verdict: ', options: { bold: true, color: HEX.accent2 } }, { text: 'attractive as a growth-equity or buy-and-build play in bus ITS software and services, not as a control buy-out of a hardware integrator and not in rail signalling. Priority: North America mid-market bus ITS, re-platformed to cloud, with enforcement and zero-emission modules; Europe as the second step.', options: { color: HEX.dk1 } }], { x: 0.6, y: 1.47, w: 12.15, h: 0.5, fontSize: 10.5 });
  const msgs = [
    ['Market size and segmentation', 'Public ITS for bus and passenger rail is ~' + bn(total25) + ' in 2025 (nominal USD, ex-fare). Rail signalling is ' + bn(D.ccs_2025) + ' (' + pct(ccsShare, 0) + '), half of it mainline systems bought by infrastructure managers rather than transit agencies. The transit-operator core (bus ITS ' + bn(busTot) + ', urban signalling ' + bn(ccsUrban) + ', other rail ITS ' + bn(railOther) + ') is ~' + bn(core25, 0) + '; the open software-and-services pool is ' + bn(sam25) + ' (North America ' + bn(OP.open.na) + ', Europe ' + bn(OP.open.eu) + ').'],
    ['Growth to 2031', 'Base case ' + pct(FT.cagr) + ' CAGR to ~' + bn(total31, 0) + ' (range ' + pct(SC.Low.cagr) + ' to ' + pct(SC.High.cagr) + '), modernisation-led: EUR 85-100bn of remaining ERTMS deployment cost, CBTC resignalling of legacy metros (NYC $5.4bn 2025-29), 24,000 US buses reaching end of life, zero-emission turnover and AI enforcement. Two-thirds of the increase sits in signalling; the open pool grows fastest, ' + pct(SAM.cagr) + ' to ~' + bn(sam31, 0) + '.'],
    ['Competitive dynamics', 'Signalling is a four-player oligopoly (Siemens, Hitachi incl. Thales GTS, Alstom, CRSC in China) with 3-5 years of backlog and 25-30 year service tails. Bus ITS is consolidating into strategics at 0.4-2x revenue: Modaxo now holds ~33% of the North American pool and Hitachi (Clever Devices) ~13%, while Europe is fragmented (no vendor above 6%). SaaS challengers (Swiftly, Optibus, Via, Hayden AI) overlay legacy CAD/AVL and trade at 5-6x revenue.'],
    ['Risks and barriers', 'The barrier is tenure, not rebid odds: incumbent-held systems reach a decision point only after a median 16 years, but incumbents then win just 4 of 18 competitive rebids (0 of 8 in bus CAD/AVL). Procurement (2-4 years), Buy America for hardware and SIL-4 certification in rail are structural. The near-term risk is funding: IIJA advance appropriations lapsed in September 2026 (FY2027 scenarios -5% to -22% vs FY2026) and ERTMS is behind schedule. Leverage on a hardware-heavy integrator has already failed once (Cubic, Fitch CC).'],
    ['Investment thesis', 'Buy a founder-owned North American mid-market bus ITS or scheduling vendor at 1-2.5x revenue, re-platform it to cloud, add enforcement and zero-emission energy modules, and sell into the 195 agencies with 50-999 buses that Modaxo and Hitachi have not locked up; exit to a strategic (Hitachi, Siemens, Modaxo, Via) at ~3x revenue. Avoid signalling cores and levered hardware roll-ups.'],
  ];
  let y = 2.18;
  msgs.forEach(([h, b]) => {
    T(s, h, { x: 0.45, y, w: 1.95, h: 0.86, fontSize: 10.5, bold: true, color: HEX.dk1 });
    T(s, b, { x: 2.5, y, w: 6.15, h: 0.86, fontSize: 9.5, color: HEX.dk1 });
    s.addShape('line', { x: 0.45, y: y + 0.9, w: 8.2, h: 0, line: { color: 'C7D3DA', width: 0.5 } });
    y += 0.94;
  });
  panel(s, 8.95, 2.18, 3.95, 4.6);
  T(s, 'The market in four numbers', { x: 9.1, y: 2.26, w: 3.65, h: 0.28, fontSize: 10.5, bold: true, color: HEX.dk1 });
  const stats = [
    [bn(total25, 0), '2025 Public ITS, bus + passenger rail, brief scope (ex-fare); ' + pct(ccsShare, 0) + ' is rail signalling'],
    [bn(core25, 0), 'transit-operator core: bus ITS, urban signalling, other rail ITS'],
    [bn(sam25) + ' to ' + bn(sam31)], ['open software-and-services pool 2025 to 2031, ' + pct(SAM.cagr) + ' CAGR'],
    [bn(total31, 0) + ' / ' + pct(FT.cagr)], ['2031 base case and CAGR (low ' + pct(SC.Low.cagr) + ', high ' + pct(SC.High.cagr) + ')'],
  ];
  let sy = 2.6;
  [[stats[0][0], stats[0][1]], [stats[1][0], stats[1][1]], [stats[2][0], stats[3][0]], [stats[4][0], stats[5][0]]].forEach(([big, lab]) => {
    s.addText(big, { x: 9.1, y: sy, w: 3.7, h: 0.42, fontSize: 20, bold: true, color: HEX.accent2, margin: 0, isTextBox: true });
    s.addText(lab, { x: 9.1, y: sy + 0.4, w: 3.7, h: 0.4, fontSize: 9, color: HEX.dk2, margin: 0, isTextBox: true, valign: 'top' });
    sy += 0.84;
  });
  T(s, [{ text: 'What has to be true: ', options: { bold: true, color: HEX.dk1 } }, { text: 'agencies fund subscriptions from operating budgets or leases; the 2026-31 refresh windows open on schedule with federal formula funding at 85-100% of IIJA levels; enforcement, safety video and electrification add budget lines rather than cannibalise core ITS.', options: {} }], { x: 9.1, y: 5.98, w: 3.7, h: 0.78, fontSize: 8.5, color: HEX.dk1 });
  s.addText('Source: model built on Berg Insight (Mar 2026), UNIFE World Rail Market Study 2026, SCI Verkehr (Mar 2026), Global Market Insights (Aug 2026), FTA NTD RY2025, company reports; Public_ITS_Market_Model.xlsx.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 2. Market definition and size
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('Public ITS is ~' + bn(total25, 0) + ' in 2025, but half is mainline signalling bought by infrastructure managers; the transit-operator core is ~' + bn(core25, 0) + ' and the open software-and-services pool ~' + bn(sam25, 0), { placeholder: 'title' });
  s.addText('Market size', { placeholder: 'tracker' });
  F.panelHeader(s, '2025 market by segment and geography (USD bn, nominal, core scope ex-fare)', 0.45, 1.4, 6.35);
  const segs = [['Bus and tram ITS  ' + bn(busTot), 'Bus'], ['Urban signalling (CBTC)  ' + bn(ccsUrban), 'Rail CCS urban'], ['Mainline and commuter signalling  ' + bn(ccsMain), 'Rail CCS mainline'], ['Other rail ITS  ' + bn(railOther), 'Rail other']];
  const geoOf = (blk, geo) => D.market_rows.filter(r => r.block === blk && r.geo === geo).reduce((a, r) => a + r.total, 0);
  const geoSeries = [['North America', HEX.dk1], ['Europe', HEX.accent3], ['Asia-Pacific', HEX.accent2], ['Rest of world', HEX.accent5]];
  s.addChart(pres.ChartType.bar, geoSeries.map(([g]) => ({ name: g, labels: segs.map(x => x[0]), values: segs.map(x => +geoOf(x[1], g).toFixed(2)) })), Object.assign({}, F.chartBase, {
    x: 0.45, y: 1.75, w: 6.35, h: 2.45, barDir: 'bar', barGrouping: 'stacked', catAxisOrientation: 'maxMin', showValue: true, dataLabelPosition: 'ctr', dataLabelColor: 'FFFFFF', dataLabelFontSize: 8, dataLabelFormatCode: '0.0;;', showLegend: true, legendPos: 'b', valAxisLabelFormatCode: '0', valAxisMaxVal: 16, catAxisLabelFontSize: 8.5, barGapWidthPct: 45, chartColors: geoSeries.map(x => x[1]) }));
  const openRows = [[hcell('Openness to a new entrant (USD bn)'), hcell('Global', { align: 'right' }), hcell('N. America', { align: 'right' }), hcell('Europe', { align: 'right' }), hcell('APAC', { align: 'right' }), hcell('RoW', { align: 'right' })],
    [cell('Closed: signalling cores (SIL-4, four suppliers)', { bold: true }), cell(bn(OP.closed.total), { align: 'right' }), cell(bn(OP.closed.na), { align: 'right' }), cell(bn(OP.closed.eu), { align: 'right' }), cell(bn(OP.closed.apac), { align: 'right' }), cell(bn(OP.closed.row), { align: 'right' })],
    [cell('Incumbent-held: onboard and wayside hardware', { bold: true }), cell(bn(OP.held.total), { align: 'right' }), cell(bn(OP.held.na), { align: 'right' }), cell(bn(OP.held.eu), { align: 'right' }), cell(bn(OP.held.apac), { align: 'right' }), cell(bn(OP.held.row), { align: 'right' })],
    [cell('Open: software and services (SaaS overlay; ' + pct(SAM.cagr) + ' CAGR)', { bold: true, color: HEX.accent2 }), cell(bn(OP.open.total), { bold: true, align: 'right', color: HEX.accent2 }), cell(bn(OP.open.na), { align: 'right', bold: true }), cell(bn(OP.open.eu), { align: 'right', bold: true }), cell(bn(OP.open.apac), { align: 'right', bold: true }), cell(bn(OP.open.row), { align: 'right', bold: true })],
  ];
  openRows.forEach((row, i) => row.forEach(c => { c.options.fontSize = 9; }));
  tbl(s, openRows, { x: 0.45, y: 4.3, w: 6.35, colW: [3.5, 0.55, 0.7, 0.55, 0.5, 0.55], rowH: [0.24, 0.25, 0.25, 0.25] });
  T(s, [{ text: 'Two-tier view: ', options: { bold: true } }, { text: 'transit-operator core (bus ITS + urban signalling + other rail ITS) ' + bn(core25) + ' (' + pct(TI.core.share, 0) + '); mainline and commuter signalling ' + bn(ccsMain) + ' (' + pct(TI.mainline.share, 0) + ') is in the brief scope (trackside and signalling equipment) but is bought by DB InfraGO, Network Rail, RFI, Adif, Amtrak and commuter railroads, so ITS analysts (Berg, GMI) leave it out and quote $4-7bn.', options: {} }], { x: 0.45, y: 5.45, w: 6.35, h: 0.72, fontSize: 9, color: HEX.dk1 });
  T(s, [{ text: 'Sensitivity: ', options: { bold: true } }, { text: 'ex-fare haircut on Berg 0 / 15 / 20 / 25% gives a bus pool of ' + bn(SE.h0.bus_pool) + ' / ' + bn(SE.h15.bus_pool) + ' / ' + bn(SE.h20.bus_pool) + ' / ' + bn(SE.h25.bus_pool) + ' (20% is an assumption bracketed by GMI payment and ticketing shares); a North America bottom-up from board-document unit costs (83k buses x ~$' + (D.bottom_up['All-in intensity incl. wayside, depot and back-office adder'] / 1000).toFixed(1) + 'k per bus-year) explains ~' + pct(D.bottom_up['Bottom-up as share of top-down'], 0) + ' of the top-down bus figure; paratransit fleets, enforcement cameras and residual fare content make up the rest.', options: {} }], { x: 0.45, y: 6.22, w: 6.35, h: 0.62, fontSize: 8.5, color: HEX.dk2 });
  F.panelHeader(s, 'Segmentation framework: mode x functional domain x component layer (each cell sized in the model)', 7.05, 1.4, 5.85);
  const fw = [
    [hcell('Functional domain'), hcell('Roadway (bus, BRT, paratransit)'), hcell('Railway (metro, LRT, commuter, mainline passenger)')],
    [cell('A. Operations and fleet management', { bold: true }), cell('HW: onboard computer, MDT, radio | SW: CAD/AVL, scheduling, dispatch'), cell('HW: train tracking, control-centre systems | SW: traffic and crew management')],
    [cell('B. Passenger information', { bold: true }), cell('HW: onboard and stop displays | SW: real-time prediction, apps'), cell('HW: platform and onboard displays | SW: real-time and disruption information')],
    [cell('C. Safety, security and surveillance', { bold: true }), cell('HW: cameras, collision sensors | SW: AI incident detection, lane enforcement'), cell('HW: onboard and station CCTV | SW: analytics, obstacle detection')],
    [cell('D. Asset, telematics and condition monitoring', { bold: true }), cell('HW: APC, vehicle-health telematics | SW: asset, energy and charge management'), cell('HW: APC, trackside detectors | SW: predictive maintenance, digital twins')],
    [cell('E. Train control and signalling', { bold: true }), cell('n/a (transit signal priority is an adjacency)'), cell('HW: interlockings, wayside and onboard ETCS/CBTC/PTC | SW: ATO, ATS | SVC: 25-30 year maintenance')],
    [cell('Adjacent, excluded', { bold: true, color: HEX.dk2 }), cell('Fare collection and ticketing ($10-17bn), traffic management and tolling', { color: HEX.dk2 }), cell('Fare collection, rolling stock and TCMS, civil works, freight rail', { color: HEX.dk2 })],
  ];
  fw.forEach((row, i) => row.forEach(c => { if (i > 0) c.options.fontSize = 8.5; }));
  tbl(s, fw, { x: 7.05, y: 1.72, w: 5.85, colW: [1.35, 2.25, 2.25], rowH: [0.26, 0.36, 0.36, 0.36, 0.36, 0.46, 0.36] });
  const segRows = [[hcell('Segment'), hcell('2025', { align: 'right' }), hcell('Mix', { align: 'right' }), hcell('Anchor and carve-out')],
    [cell('Bus and tram ITS'), cell(bn(busTot), { align: 'right' }), cell(pct(S.Bus.share, 0), { align: 'right' }), cell('Berg EU EUR 2.55bn + NA EUR 1.22bn less 20% fare; RoW on GMI mix; ops ' + bn(AP.ops.value) + ' / info ' + bn(AP.info.value) + ' / safety ' + bn(AP.safety.value))],
    [cell('Urban signalling'), cell(bn(ccsUrban), { align: 'right' }), cell(pct(S['Rail CCS urban'].share, 0), { align: 'right' }), cell('UNIFE rail control EUR 24.9bn x passenger share (74%) x urban share (UITP km x unit cost); GMI CBTC $4.9bn check')],
    [cell('Mainline and commuter signalling'), cell(bn(ccsMain), { align: 'right' }), cell(pct(S['Rail CCS mainline'].share, 0), { align: 'right' }), cell('Remainder of passenger signalling; SCI ~EUR 20bn low case; vendor revenue sum EUR 17bn')],
    [cell('Other rail ITS'), cell(bn(railOther), { align: 'right' }), cell(pct(S['Rail other'].share, 0), { align: 'right' }), cell('GMI rail APTS ex-ticketing $1.6bn + condition monitoring and detection (analyst estimates)')],
    [cell('Total; hardware / software / services', { bold: true }), cell(bn(total25), { bold: true, align: 'right' }), cell('100%', { bold: true, align: 'right' }), cell(pct(D.components.Hardware.share, 0) + ' / ' + pct(D.components.Software.share, 0) + ' / ' + pct(D.components.Services.share, 0) + '; geography: Europe ' + pct(D.geos.Europe.share, 0) + ', APAC ' + pct(D.geos['Asia-Pacific'].share, 0) + ', NA ' + pct(D.geos['North America'].share, 0) + ', RoW ' + pct(D.geos['Rest of world'].share, 0), { bold: true })],
  ];
  segRows.forEach((row, i) => row.forEach(c => { if (i > 0) c.options.fontSize = 8.5; }));
  tbl(s, segRows, { x: 7.05, y: 4.62, w: 5.85, colW: [1.3, 0.5, 0.4, 3.65], rowH: [0.24, 0.36, 0.36, 0.26, 0.36, 0.36] });
  s.addText('Source: Berg Insight 10th ed. (2026); UNIFE WRMS 2026; SCI Verkehr CCS (2026); GMI APTS (2026); Eurostat, UITP; FTA NTD RY2025. Model: Market_2025, TopDown, BottomUp_NA.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 3. Growth drivers and outlook
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('The market grows ~' + pct(FT.cagr, 0) + ' a year to ~' + bn(total31, 0) + ' by 2031; two-thirds of the increase is mandated signalling modernisation, while the open software-and-services pool grows fastest, ~' + pct(SAM.cagr, 0) + ' to ~' + bn(sam31, 0), { placeholder: 'title' });
  s.addText('Growth and outlook', { placeholder: 'tracker' });
  F.panelHeader(s, 'What the 2025 to 2031 increase is made of, base case (USD bn, nominal at constant 2025 FX)', 0.45, 1.4, 6.2);
  const br = D.bridge.filter(b => b.delta !== null && b.delta !== undefined);
  const brLabels = br.map(b => b.label.replace('Bus and tram ITS: ', 'Bus ITS: ').replace(' (CBTC) resignalling and new lines', '').replace(' (ETCS, interlockings, PTC)', '').replace(' (PIS, CCTV/APC, condition monitoring, detection)', ''));
  const brBus = br.map(b => b.label.startsWith('Bus') ? +b.delta.toFixed(2) : 0);
  const brSig = br.map(b => b.label.includes('signalling') ? +b.delta.toFixed(2) : 0);
  const brOth = br.map(b => b.label.startsWith('Other') ? +b.delta.toFixed(2) : 0);
  s.addChart(pres.ChartType.bar, [
    { name: 'Bus and tram ITS', labels: brLabels, values: brBus },
    { name: 'Rail signalling', labels: brLabels, values: brSig },
    { name: 'Other rail ITS', labels: brLabels, values: brOth },
  ], Object.assign({}, F.chartBase, { x: 0.45, y: 1.75, w: 6.2, h: 2.75, barDir: 'bar', barGrouping: 'stacked', catAxisOrientation: 'maxMin', showValue: true, dataLabelPosition: 'inEnd', dataLabelColor: 'FFFFFF', dataLabelFontSize: 8.5, dataLabelFormatCode: '+0.0;;', showLegend: true, legendPos: 'b', valAxisLabelFormatCode: '0.0', valAxisMinVal: 0, valAxisMaxVal: 5.5, catAxisLabelFontSize: 8.5, barGapWidthPct: 40, chartColors: [COL_BUS, COL_SIG, COL_OTH] }));
  T(s, [{ text: bn(total25) + ' (2025) to ' + bn(total31) + ' (2031). ', options: { bold: true } }, { text: 'Base CAGRs: bus Europe ' + pct(D.forecast_rows[0].base) + ', bus North America ' + pct(D.forecast_rows[1].base) + ', bus rest of world ' + pct(D.forecast_rows[2].base) + '; passenger signalling ' + pct(FS['Rail CCS'].cagr) + ' (Europe ' + pct(D.forecast_rows[4].base) + ', China ' + pct(D.forecast_rows[5].base) + ', North America ' + pct(D.forecast_rows[7].base) + '); other rail ITS ' + pct(FS['Rail other'].cagr) + '; software ' + pct(D.forecast_comp.Software.cagr) + ' vs hardware ' + pct(D.forecast_comp.Hardware.cagr) + '; open software and services ' + pct(SAM.cagr) + '.', options: {} }], { x: 0.45, y: 4.55, w: 6.2, h: 0.55, fontSize: 8.5, color: HEX.dk1 });
  const scRows = [[hcell('Scenario'), hcell('2031', { align: 'right' }), hcell('CAGR', { align: 'right' }), hcell('Open pool 2031', { align: 'right' }), hcell('What the model assumes')],
    [cell('Low'), cell(bn(SC.Low.values[6]), { align: 'right' }), cell(pct(SC.Low.cagr), { align: 'right' }), cell(bn(SC['Contestable Low'].values[6] * (sam25 / FC.values[0])), { align: 'right' }), cell('US bus 2.5% (funding at extension levels, -20%), Europe bus 3.5%, signalling -1.5pp (ERTMS and CP7 slippage), other rail 5%')],
    [cell('Base', { bold: true }), cell(bn(SC.Base.values[6]), { bold: true, align: 'right' }), cell(pct(SC.Base.cagr), { bold: true, align: 'right' }), cell(bn(sam31), { bold: true, align: 'right' }), cell('Berg bus trajectories (NA 5.0%, Europe 5.3%), signalling between SCI 4.6% and UNIFE realised 5.7%, committed frameworks deliver')],
    [cell('High'), cell(bn(SC.High.values[6]), { align: 'right' }), cell(pct(SC.High.cagr), { align: 'right' }), cell(bn(SC['Contestable High'].values[6] * (sam25 / FC.values[0])), { align: 'right' }), cell('US bus 8% (below the 11.5% realised 2022-25), Europe bus 7%, signalling +1.5pp (FRMCS, GoA4 early), other rail 9%')],
  ];
  scRows.forEach((row, i) => row.forEach(c => { if (i > 0) c.options.fontSize = 9; }));
  tbl(s, scRows, { x: 0.45, y: 5.15, w: 6.2, colW: [0.6, 0.65, 0.55, 0.95, 3.45], rowH: [0.24, 0.45, 0.45, 0.45] });
  T(s, 'Open-pool scenario values scale the base-case software and services share to the contestable-pool scenarios.', { x: 0.45, y: 6.62, w: 6.2, h: 0.22, fontSize: 7.5, color: HEX.dk2 });
  F.panelHeader(s, 'Drivers and headwinds behind the forecast (▲ tailwind, ▼ headwind; H/M = impact)', 6.9, 1.4, 6.0);
  const drv = [[hcell('Driver'), hcell('Segment'), hcell('Effect', { align: 'center' }), hcell('Strongest evidence')],
    [cell('ERTMS/ETCS mandate', { bold: true }), cell('Rail Europe'), cell('▲ H', { align: 'center', color: HEX.accent2, bold: true }), cell('EUR 85-100bn remaining TEN-T deployment cost; ~10% of km and 19% of fleet equipped at end-2024; non-US resignalling pipeline 2026-31 EUR 36bn base case, 55-60% committed')],
    [cell('Legacy metro resignalling', { bold: true }), cell('Rail urban'), cell('▲ H', { align: 'center', color: HEX.accent2, bold: true }), cell('NYC 85% fixed-block: $5.4bn CBTC in the 2025-29 plan at $20-45m per km; ~90% of European signalling volume is modernisation')],
    [cell('Bus fleet and system end of life', { bold: true }), cell('Bus NA/EU'), cell('▲ H', { align: 'center', color: HEX.accent2, bold: true }), cell('24,100 US buses reach their useful-life benchmark 2026-31; ~12,000 buses on 2009-16 CAD/AVL platforms hit 15-20 years = $0.3-0.5bn of full-replacement awards (LA Metro $130m, TfL GBP 160m precedents)')],
    [cell('Digital interlocking frameworks', { bold: true }), cell('Rail Europe'), cell('▲ M', { align: 'center', color: HEX.accent2, bold: true }), cell('DB EUR 6.3bn digital interlocking and ETCS volume contract (2025); OBB EUR 2.6bn; SBB CHF 1.4bn with 25-year maintenance')],
    [cell('Zero-emission turnover', { bold: true }), cell('Bus'), cell('▲ M', { align: 'center', color: HEX.accent2, bold: true }), cell('BEB registrations 60% of EU city buses in 2025 (+48%); Clean Vehicles Directive 65% clean (half zero-emission) 2026-30; 8,100 US ZEBs funded')],
    [cell('AI enforcement and safety video', { bold: true }), cell('Bus'), cell('▲ M', { align: 'center', color: HEX.accent2, bold: true }), cell('MTA ACE from 123 to 1,900+ buses ($141m contract); 11 US agencies on Hayden AI; FRA locomotive cameras by Oct 2027; self-funding via citations')],
    [cell('US federal funding reset', { bold: true }), cell('Bus/rail NA'), cell('▼ H', { align: 'center', color: HEX.dk2, bold: true }), cell('IIJA advance appropriations ($4.25bn/yr) lapsed Sep 2026; FY2027 scenarios -5% (House bill) / -20% (extension) / -22% (request) vs FY2026')],
    [cell('Rail budget stretch-outs', { bold: true }), cell('Rail EU/China'), cell('▼ M', { align: 'center', color: HEX.dk2, bold: true }), cell('Network Rail CP7 ETCS cut from GBP 1.54bn to 0.99bn; DB withdrew its ETCS migration strategy (2025); China urban-rail investment -8.9% (2024)')],
  ];
  drv.forEach((row, i) => row.forEach(c => { if (i > 0 && !c.options.align) c.options.fontSize = 9; }));
  tbl(s, drv, { x: 6.9, y: 1.72, w: 6.0, colW: [1.4, 0.8, 0.55, 3.25], rowH: [0.24, 0.58, 0.58, 0.58, 0.58, 0.58, 0.58, 0.58, 0.58] });
  s.addText('Source: model Forecast and Drivers sheets; EC Third ERTMS Work Plan (2026); MTA 2025-29 Capital Program; FTA NTD RY2025; ACEA; CALSTART; Network Rail CP7 plan (2026); DB; FTA apportionment notices; H.R. 8870.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 4. Competitive dynamics
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('Rail signalling is a four-player oligopoly (three ex-China) protected by backlog and certification; bus ITS is consolidating into strategics at 0.4-2x revenue while SaaS challengers unbundle the stack', { placeholder: 'title' });
  s.addText('Competitive dynamics', { placeholder: 'tracker' });
  F.panelHeader(s, 'Landscape by segment', 0.45, 1.4, 7.75);
  const land = [[hcell('Segment (2025 pool)'), hcell('Scale leaders'), hcell('Challengers and specialists'), hcell('Structure')],
    [cell('Rail signalling, passenger (' + bn(D.ccs_2025, 0) + ')', { bold: true }), cell('Siemens Mobility (rail infrastructure ~EUR 4.1bn), Hitachi Rail (EUR 7.8bn, >50% signalling incl. Thales GTS), Alstom Signalling (EUR 2.7bn), CRSC (EUR 4.3bn, China)'), cell('Wabtec (PTC, Frauscher), KB Signaling, Stadler and CAF (own-fleet pull), MERMEC (to Siemens), Nippon Signal, Kyosan'), cell('Each 13-22% of world CCS; big three ~two-thirds ex-China; backlog 3.4-5.4x revenue; 10-30 year frameworks; SIL-4')],
    [cell('Other rail ITS (' + bn(railOther) + ')', { bold: true }), cell('OEM platforms: Hitachi HMAX, Siemens Railigent X, Alstom HealthHub; Nokia (FRMCS)'), cell('Konux, Sensonic, Icomera, Nomad (Alstom), Televic, Dilax (INIT), Rail Vision'), cell('Value captured inside OEM service contracts; independents in detection, connectivity, PIS')],
    [cell('Bus integrated systems (' + bn(busTot) + ')', { bold: true }), cell('Modaxo/Constellation (Trapeze, Vontas, Routeward; 3,500+ customers), Hitachi Rail (Clever Devices, 8 of top-10 NA agencies, >$220m), INIT (EUR 330m), Cubic'), cell('IVU (DACH), Equans and GMV (France, Iberia, LatAm), Avail, Luminator, Hanover, Passio, ETA'), cell('Owner-level top five = 71% of the NA pool; Europe top five = 21%, no vendor above 6%; growth is refresh (90%+ of buses equipped); incumbents win 4 of 18 competitive rebids')],
    [cell('Bus SaaS and AI layers', { bold: true }), cell('Via (NYSE, $434m FY2025 revenue), Optibus ($1.3bn valuation 2022), Swiftly (200+ agencies), Hayden AI (2,500 buses)'), cell('Spare, Transit app, Moovit (Mobileye), Masabi (fare); Samsara and Geotab from municipal fleets'), cell('Subscription, little hardware; overlay legacy CAD/AVL at 100+ agencies; exits to strategics or IPO')],
  ];
  land.forEach((row, i) => row.forEach(c => { if (i > 0) c.options.fontSize = 9; }));
  tbl(s, land, { x: 0.45, y: 1.72, w: 7.75, colW: [1.4, 2.4, 1.9, 2.05], rowH: [0.24, 0.74, 0.5, 0.78, 0.6] });
  // share bars
  F.panelHeader(s, 'Indicative 2025 shares of the two pools that matter (vendor revenue vs pools)', 0.45, 4.95, 7.75);
  const shareOpts = (x, y, w, h, colors) => Object.assign({}, F.chartBase, { x, y, w, h, barDir: 'bar', barGrouping: 'percentStacked', showValue: true, dataLabelPosition: 'ctr', dataLabelColor: 'FFFFFF', dataLabelFontSize: 8, dataLabelFormatCode: '0%', showLegend: true, legendPos: 'b', legendFontSize: 8, valAxisHidden: true, catAxisHidden: true, valGridLine: { style: 'none' }, barGapWidthPct: 20, chartColors: colors });
  s.addChart(pres.ChartType.bar, [
    { name: 'Hitachi Rail (incl. Thales GTS) 21%', labels: ['World passenger signalling'], values: [0.21] },
    { name: 'Siemens Mobility 20%', labels: ['World passenger signalling'], values: [0.20] },
    { name: 'CRSC 19%', labels: ['World passenger signalling'], values: [0.19] },
    { name: 'Alstom 13%', labels: ['World passenger signalling'], values: [0.13] },
    { name: 'Others (Wabtec, KB, CAF, Stadler, Japanese) 27%', labels: ['World passenger signalling'], values: [0.27] },
  ], shareOpts(0.45, 5.45, 3.85, 1.38, [HEX.dk1, HEX.accent3, HEX.accent6, HEX.accent4, HEX.accent5]));
  s.addChart(pres.ChartType.bar, [
    { name: 'Modaxo (Trapeze, Vontas, Routeward) 33%', labels: ['North America bus ITS'], values: [0.33] },
    { name: 'Hitachi / Clever Devices 13%', labels: ['North America bus ITS'], values: [0.13] },
    { name: 'INIT 9%', labels: ['North America bus ITS'], values: [0.09] },
    { name: 'Cubic 9%, Luminator 7%', labels: ['North America bus ITS'], values: [0.16] },
    { name: 'Mid-market, long tail and SaaS 29%', labels: ['North America bus ITS'], values: [0.29] },
  ], shareOpts(4.35, 5.45, 3.85, 1.38, [HEX.dk1, HEX.accent3, HEX.accent6, HEX.accent4, HEX.accent2]));
  T(s, 'World passenger signalling (' + bn(D.ccs_2025, 0) + ')', { x: 0.5, y: 5.28, w: 3.8, h: 0.2, fontSize: 8.5, bold: true, color: HEX.dk1 });
  T(s, 'North America bus ITS (Berg pool EUR 1.22bn, filed vendor revenue)', { x: 4.4, y: 5.28, w: 3.8, h: 0.2, fontSize: 8.5, bold: true, color: HEX.dk1 });
  F.panelHeader(s, 'Four dynamics, and who buys', 8.45, 1.4, 4.45);
  s.addText(lines([
    { text: 'Strategic consolidation at low multiples. ', options: { bold: true } }, 'Hitachi-Thales GTS (EUR 1.66bn), Hitachi-Clever (2026), Modaxo-Conduent transit ($164m, 0.4x), Siemens-MERMEC, Wabtec-Frauscher, Knorr-Alstom NA. Sponsors absent since Cubic; Modaxo never sells.',
    { text: 'Hardware-to-software unbundling. ', options: { bold: true } }, 'ITxPT, cloud CAD/AVL (Swiftly 2026) and real-time overlays (Optibus) thin the onboard stack; INIT now reports Cloud and Passenger Intelligence units; Luminator repositions to digital.',
    { text: 'Services and long contracts are the moat. ', options: { bold: true } }, 'INIT contracts up to 20 years (~EUR 1bn obligations at end-2025); Alstom services mid-teens margin vs 6% group; 25-year CBTC maintenance tails. Integrators 9-12% EBIT; SaaS ~40% gross margin, near-zero EBITDA.',
    { text: 'Natural acquirers of a new entrant: ', options: { bold: true } }, 'Hitachi Rail, Siemens Mobility, Modaxo/Constellation, Via; Alstom (0.3x sales, EUR 2bn deleveraging review incl. inorganic options) is a possible carve-out source rather than a buyer.',
  ]), { x: 8.6, y: 1.8, w: 4.2, h: 2.95, fontSize: 9, color: HEX.dk1, valign: 'top', margin: 0, isTextBox: true, paraSpaceAfter: 4 });
  F.panelHeader(s, 'EV / revenue, x (transactions and trading, Nov 2026)', 8.45, 4.95, 4.45);
  s.addChart(pres.ChartType.bar, [{ name: 'EV/revenue', labels: ['Conduent transit to Modaxo (2026)', 'Thales GTS to Hitachi (FY25 rev.)', 'INIT (trading)', 'Alstom Signaling NA to Knorr', 'IVU (trading)', 'Via (trading, LTM)'], values: [0.44, 0.7, 1.0, 2.1, 2.6, 5.6] }],
    Object.assign({}, F.chartBase, { x: 8.45, y: 5.28, w: 4.45, h: 1.55, barDir: 'bar', catAxisOrientation: 'maxMin', showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"x"', dataLabelFontSize: 8, showLegend: false, valAxisHidden: true, valGridLine: { style: 'none' }, catAxisLabelFontSize: 7.5, barGapWidthPct: 35, valAxisMaxVal: 7, chartColors: [HEX.accent3] }));
  s.addText('Source: company reports and statutory filings (Siemens, Hitachi, Alstom, CRSC, Wabtec, INIT, IVU, Via, Conduent, Companies House, Nordic registries), Berg Insight, deal releases, trading data 6 Nov 2026; shares indicative; Cubic LBO 15.7x NTM EBITDA excluded.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 5. Risks and barriers
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('Barriers to entry are structural (incumbency, procurement, certification); the near-term risks to the forecast are the US funding reset and European signalling slippage', { placeholder: 'title' });
  s.addText('Risks and barriers', { placeholder: 'tracker' });
  F.panelHeader(s, 'Risk register (●●●●● = likelihood x impact 20-25, ●●●● 16-19, ●●● 10-15, ●● <10; analyst scoring)', 0.45, 1.4, 7.6);
  const rk = [[hcell('Risk / barrier'), hcell('Type'), hcell('Severity', { align: 'center' }), hcell('Strongest evidence')],
    [cell('Tenure: systems reach a decision point only after a median 16 years', { bold: true }), cell('Barrier'), cell(dots(5), { align: 'center', color: HEX.accent2 }), cell('39 decision points 2016-26: 64% stayed with the incumbent, mostly by extension; at competitive rebids incumbents won 4 of 18 (0 of 8 in bus CAD/AVL)')],
    [cell('Rail certification and four-player signalling (three ex-China)', { bold: true }), cell('Barrier'), cell(dots(5), { align: 'center', color: HEX.accent2 }), cell('SIL-4, ERA and FRA approvals; two qualified CBTC suppliers on the NYC subway; 10-30 year frameworks')],
    [cell('Procurement cycle and protests', { bold: true }), cell('Barrier'), cell(dots(4), { align: 'center', color: HEX.accent2 }), cell('2-4 years award-to-live; LA Metro plan (2016) to go-live (2028); $10.8m programme-support consultant')],
    [cell('US federal funding reset', { bold: true }), cell('Market'), cell(dots(4), { align: 'center', color: HEX.accent2 }), cell('FY2027 scenarios -5% / -20% / -22% vs FY2026; FTA staff -30%; SEPTA structural deficit $192m')],
    [cell('Buy America / BABA for hardware', { bold: true }), cell('Barrier'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('>70% domestic content and US final assembly; INIT runs two Virginia plants to comply')],
    [cell('ERTMS and resignalling slippage', { bold: true }), cell('Market'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('EC: significantly behind schedule; CP7 ETCS cut 35%; DB withdrew migration strategy')],
    [cell('Cybersecurity compliance and incidents', { bold: true }), cell('Both'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('TSA rule $1.26bn/10 years on passenger rail; TfL 2024 attack GBP 39m; TTC 2021 ransomware took down CAD/AVL')],
    [cell('Leverage on hardware-heavy integrators', { bold: true }), cell('Investment'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('Cubic ~11x debt/EBITDA at LBO, three straight interest deferrals, Fitch CC (Aug 2026); Alstom profit warning')],
    [cell('Long tail and agency capacity', { bold: true }), cell('Market'), cell(dots(3), { align: 'center', color: HEX.accent2 }), cell('772 US agencies with <50 buses hold 16% of the fleet; enterprise CAD/AVL depends on ~70-90 accounts (NTD tiers)')],
    [cell('SaaS eligibility under 80/20 capital grants', { bold: true }), cell('Market'), cell(dots(2), { align: 'center', color: HEX.accent2 }), cell('Capital definition covers leasing and preventive maintenance; FTA declined SaaS guidance (2025); House bill adds a SaaS clause')],
  ];
  rk.forEach((row, i) => row.forEach(c => { if (i > 0 && !c.options.align) c.options.fontSize = 9.5; }));
  tbl(s, rk, { x: 0.45, y: 1.72, w: 7.6, colW: [2.05, 0.75, 0.75, 4.05], rowH: [0.24, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47, 0.47] });
  F.panelHeader(s, 'Barrier height by entry route (analyst score, 1 low to 5 high)', 8.3, 1.4, 4.6);
  s.addChart(pres.ChartType.bar, [{ name: 'Barrier', labels: ['Rail signalling cores', 'Bus integrated systems (hardware + CAD/AVL core)', 'Rail adjacencies (monitoring, cyber, connectivity)', 'Bus software overlay / SaaS'], values: [5, 4, 3, 2] }],
    Object.assign({}, F.chartBase, { x: 8.3, y: 1.72, w: 4.6, h: 1.65, barDir: 'bar', catAxisOrientation: 'maxMin', showValue: true, dataLabelPosition: 'outEnd', dataLabelFontSize: 8.5, showLegend: false, valAxisHidden: true, valGridLine: { style: 'none' }, catAxisLabelFontSize: 8, barGapWidthPct: 35, valAxisMaxVal: 6, chartColors: [HEX.dk1] }));
  F.panelHeader(s, 'What the barriers mean for an entrant', 8.3, 3.55, 4.6);
  const imp = [
    ['Displacement is a decade-long game, but rebids favour the challenger', 'Only ~1/16th of the installed base reaches a decision point each year, and most renewals are sole-sourced; when a system is competitively rebid the incumbent usually loses. Coexist and take modules first; buy an installed base to own the service tail.'],
    ['Hardware-led entry needs a US manufacturing partner', 'Buy America, tariffs and inventory risk make pure hardware unattractive; partner for onboard units and leave hardware margin to the OEM channel (Gillig and New Flyer build two-thirds of US buses).'],
    ['Funding mechanics shape the product', 'Capital grants pay 80% of hardware and perpetual licences; subscriptions come from local operating budgets unless structured as leases or preventive maintenance.'],
    ['Rail cores are closed; adjacencies are not', 'Signalling, ATO and FRMCS need SIL-4 and 10-15 year programmes; condition monitoring, cyber, onboard connectivity and detection are contestable with the same buyers.'],
  ];
  let iy = 3.92;
  imp.forEach(([h, b]) => {
    T(s, h, { x: 8.45, y: iy, w: 4.3, h: 0.22, fontSize: 9.5, bold: true, color: HEX.accent2 });
    T(s, b, { x: 8.45, y: iy + 0.22, w: 4.3, h: 0.5, fontSize: 8.5, color: HEX.dk1 });
    iy += 0.74;
  });
  s.addText('Source: agency board documents (LA Metro Legistar, TfL), INIT annual report 2025, TSA NPRM (Nov 2024), DOT OIG audit (Jul 2024), FTA Federal Register notices, EC ERTMS Work Plan (2026), Network Rail CP7 plan, NTD RY2025; model Risks sheet.', { placeholder: 'source' });

  // ------------------------------------------------------------------ 6. Investment thesis
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  s.addText('Enter via buy-and-build in North America: a mid-market bus ITS platform at 1-2.5x revenue, moved to cloud with enforcement and zero-emission modules, exited to a strategic at ~3x', { placeholder: 'title' });
  s.addText('Investment thesis', { placeholder: 'tracker' });
  F.panelHeader(s, 'Recommendation and why North America first', 0.45, 1.4, 7.9);
  s.addText(lines([
    { text: 'Recommended route: ', options: { bold: true, color: HEX.accent2 } }, { text: 'acquire a founder- or employee-owned North American CAD/AVL or scheduling vendor (installed base, 5-20 year service tails, procurement credibility) at integrator multiples, then layer a subscription real-time, analytics and enforcement stack on top and bolt on APC, PIS or enforcement specialists at 1-2x revenue.', options: {} },
    { text: 'Why North America: ', options: { bold: true, color: HEX.accent2 } }, { text: '(1) the refresh is dated: ~12,000 buses on 2009-16 CAD/AVL platforms and 24,100 past useful life by 2031; (2) the top is concentrated (Modaxo 33%, Hitachi 13%) but the mid-tier is open: 195 agencies with 50-999 buses hold 55% of the fleet and incumbents win only 4 of 18 competitive rebids; (3) per-vehicle spend is highest (EUR 14-16k vs EUR 7-13k per equipped bus-year in Europe) and formula funding favours refresh; (4) one procurement code, versus 20 national markets in Europe where no vendor exceeds 6%: the second platform, entered by bolt-on.', options: {} },
  ]), { x: 0.6, y: 1.74, w: 7.65, h: 1.45, fontSize: 8.8, color: HEX.dk1, valign: 'top', margin: 0, isTextBox: true, paraSpaceAfter: 2 });
  F.panelHeader(s, 'Illustrative value bridge (model: Thesis sheet)', 8.6, 1.4, 4.3);
  const vb = [[hcell('Step'), hcell('USD m', { align: 'right' }), hcell('Assumption')],
    [cell('Entry EV'), cell(TH.ev0.toFixed(0), { align: 'right' }), cell('$' + TH.rev0 + 'm revenue at 2.0x; 15% margin; 2.5x debt')],
    [cell('Bolt-ons (EV)'), cell(TH.bolt.toFixed(0), { align: 'right' }), cell('$40m revenue at 1.5x (APC, PIS, enforcement)')],
    [cell('Exit revenue'), cell(TH.rev1.toFixed(0), { align: 'right' }), cell('8% organic + bolt-ons over 5 years')],
    [cell('Exit EV'), cell(TH.ev1.toFixed(0), { align: 'right' }), cell('22% margin, 14x EBITDA = ' + TH.evrev.toFixed(1) + 'x revenue')],
    [cell('Gross MOIC', { bold: true }), cell(TH.moic.toFixed(1) + 'x', { bold: true, align: 'right' }), cell('on entry equity + bolt-on EV; ~' + pct(Math.pow(TH.moic, 1 / 5) - 1, 0) + ' IRR', { bold: true })],
  ];
  vb.forEach((row, i) => row.forEach(c => { if (i > 0) c.options.fontSize = 8.5; }));
  tbl(s, vb, { x: 8.6, y: 1.72, w: 4.3, colW: [0.95, 0.6, 2.75], rowH: [0.22, 0.24, 0.24, 0.24, 0.24, 0.24] });
  F.panelHeader(s, 'Where to play: four wedges that sit beside the incumbent stack, sized from the model', 0.45, 3.3, 12.45);
  const cards = [
    ['Operations, real-time and cloud CAD/AVL overlay', bn(AP.ops.value) + ' bus operations pool (' + pct(AP.ops.share, 0) + ' of bus ITS); open software and services NA ' + bn(OP.open.na) + ', Europe ' + bn(OP.open.eu), 'Legacy systems rated poorly (6% strongly recommend); overlays at 100+ agencies; module displacement at refresh'],
    ['Safety, security and AI enforcement', bn(AP.safety.value) + ' bus safety pool plus citation-funded enforcement growing fastest', 'MTA 1,900+ buses, 11 US agencies, UK type approval; adjacent to onboard video refresh ($9-25k per bus) and the FRA camera mandate'],
    ['Scheduling, demand-response and zero-emission energy management', 'Inside the ' + bn(AP.ops.value) + ' operations pool; e-bus ITS EUR 150m (2024) growing 21-27% p.a.', 'EU city buses 60% zero-emission in new registrations; Optibus and Via show agencies buy planning as SaaS'],
    ['Rail adjacencies: condition monitoring, detection, cyber', bn(railOther) + ' other rail ITS, of which ~' + bn(railOther * (1 - D.inputs.ro_hw)) + ' software and services, ' + pct(FS['Rail other'].cagr) + ' CAGR', 'OEMs monetise inside service contracts, leaving independents (Konux, Sensonic, Icomera); TSA and IEC 62443 create recurring cyber spend'],
  ];
  let cx = 0.45;
  cards.forEach(([h, p, w]) => {
    panel(s, cx, 3.64, 3.0, 1.34);
    T(s, h, { x: cx + 0.1, y: 3.68, w: 2.8, h: 0.36, fontSize: 9.5, bold: true, color: HEX.dk1 });
    T(s, p, { x: cx + 0.1, y: 4.04, w: 2.8, h: 0.4, fontSize: 8.5, color: HEX.accent2, bold: true });
    T(s, w, { x: cx + 0.1, y: 4.44, w: 2.8, h: 0.52, fontSize: 8.5, color: HEX.dk1 });
    cx += 3.15;
  });
  F.panelHeader(s, 'Entry routes compared (✔ recommended) and target long-list', 0.45, 5.1, 7.9);
  const arch = [[hcell('Route'), hcell('For'), hcell('Against'), hcell('Entry value')],
    [cell('✔ Buy a founder-owned mid-market incumbent, re-platform, bolt on', { bold: true, color: HEX.accent2 }), cell('Installed base and service tails; procurement credibility. Targets: Hanover (GBP 93m, +28%, 17% margin), Avail (ESOP), GIRO, ETA, Passio, Luminator (Audax)'), cell('Ageing code; project, Buy America and key-person risk'), cell('1.0-2.6x revenue')],
    [cell('Build or scale a SaaS wedge (Swiftly, Optibus, Hayden AI)'), cell('Asset-light, 40%+ gross margin, coexists with incumbents'), cell('Slow land-and-expand; losses to scale; SaaS funding friction'), cell('5-6x revenue, loss-making')],
    [cell('Carve-out from a stressed strategic (Alstom digital, Cubic CTS)'), cell('Scale at distressed prices'), cell('Separation, leverage history, concentration'), cell('0.3-1x revenue')],
  ];
  arch.forEach((row, i) => row.forEach(c => { if (i > 0) c.options.fontSize = 8.5; }));
  tbl(s, arch, { x: 0.45, y: 5.38, w: 7.9, colW: [2.3, 3.1, 1.6, 0.9], rowH: [0.22, 0.36, 0.26, 0.26] });
  F.panelHeader(s, 'What to diligence first', 8.6, 5.1, 4.3);
  s.addText(lines([
    '1. Rebid retention by agency tier: the 2016-26 award set (4 of 18 competitive rebids kept the incumbent, median tenure 16 years) extended to the target customer list.',
    '2. Per-vehicle economics of SaaS vs capex awards (TfL iBus2 ~$2.3k per bus-year is the clean benchmark).',
    '3. Target customer exposure to FY2027 funding scenarios and fiscal-cliff agencies.',
    '4. Exit map: which strategics would buy at what multiple, given Modaxo never sells.',
  ]), { x: 8.72, y: 5.44, w: 4.1, h: 1.3, fontSize: 8.5, color: HEX.dk1, valign: 'top', margin: 0, isTextBox: true, paraSpaceAfter: 2 });
  s.addText('Source: model Market_2025, Forecast, Thesis, Competitors and Deals_Comps sheets; NTD RY2025 tiers; Via S-1 and 8-K; INIT annual report 2025; Modaxo, Hitachi, Swiftly, Optibus and Hayden AI releases; TfL iBus2 award. Value bridge is illustrative, not a valuation.', { placeholder: 'source' });

  const out = path.join(__dirname, 'Public_ITS_Market_Case.pptx');
  await pres.writeFile({ fileName: out });
  await applyTheme(out, F.THEME);
  console.log('wrote', out);
})();
