// Public ITS case deck, v2: restyled to the reference house format
// (breadcrumb tracker, two-tone action titles, full-width exhibit header bars,
// one exhibit per slide, impact-rated driver and risk tables, competitive grid).
// Writes the main deck (cover + 6 slides) and a separate appendix deck.
const path = require('path');
const fs = require('fs');
const pptxgen = require('pptxgenjs');
const React = require('react');
const RDS = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa6');
const { applyTheme } = require('/root/.claude/skills/synced/bb6fd365-1a5f-4ed0-b47d-20358f3d4f02_a1537756-83aa-4e42-aa0d-dabc2bc599e7/pptx/scripts/apply_theme.js');

const D = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'model', 'deck_data.json'), 'utf8'));

// ---------------------------------------------------------------- palette and fonts
const K = {
  navy: '0B2447', lblue: '1FB4E6', mblue: '0070B8', pale: 'DDEFFA', paler: 'F1F8FD',
  green: '17994A', dgreen: '0E4A1F', lgreen: 'EAF4EC',
  grey: '6D6E71', dgrey: '3B3B3D', lgrey: 'EEEEEE', mgrey: 'BFC0C2',
  purple: '4B2C6F', lpurple: 'ECE4F3', red: 'E31E24', black: '000000', white: 'FFFFFF',
  teal: '12867A', slate: '1F5E99',
  sMain: '0B2447', sUrban: '1B4F8A', sOther: '0F7EC2', sBus: '26A9E0',
};
const HEAD = 'Arial Narrow', BODY = 'Arial';
const THEME = {
  name: 'Public ITS Case v2', headFontFace: HEAD, bodyFontFace: BODY,
  colors: { dk1: K.navy, lt1: 'FFFFFF', dk2: K.grey, lt2: K.lgrey, accent1: K.navy, accent2: K.lblue, accent3: K.mblue, accent4: K.green, accent5: K.grey, accent6: K.red, hlink: K.mblue, folHlink: K.grey },
};
const CW = 13.03; // content width (right navy bar starts here)

// ---------------------------------------------------------------- numbers from the model
const bn = (v, d = 1) => '$' + v.toFixed(d) + 'B';
const pct = (v, d = 1) => (v * 100).toFixed(d) + '%';
const S = D.segments, FT = D.forecast_total, SC = D.forecast_scen, SAM = D.forecast_sam, OP = D.open, TI = D.tiers, TH = D.thesis;
const total25 = D.total_2025, total31 = FT.values[6];
const ccsShare = D.ccs_2025 / total25;
const yrs = D.years.map(String);
const ccsRows = D.forecast_rows.slice(4, 10); // passenger signalling by region
const urb25 = D.market_rows.filter(r => r.block === 'Rail CCS urban').map(r => r.total);
const mai25 = D.market_rows.filter(r => r.block === 'Rail CCS mainline').map(r => r.total);
const urbanSeries = yrs.map((_, t) => ccsRows.reduce((a, r, i) => a + r.values[t] * urb25[i] / (urb25[i] + mai25[i]), 0));
const ccsSeries = D.forecast_seg['Rail CCS'].values;
const mainSeries = ccsSeries.map((v, t) => v - urbanSeries[t]);
const busSeries = D.forecast_seg['Bus'].values;
const othSeries = D.forecast_seg['Rail other'].values;
const cg = (s) => Math.pow(s[6] / s[0], 1 / 6) - 1;
const geoOf = (blk, geo) => D.market_rows.filter(r => r.block === blk && r.geo === geo).reduce((a, r) => a + r.total, 0);

// ---------------------------------------------------------------- icons
async function iconData(name, color = '#FFFFFF') {
  const C = fa[name] || fa.FaCircle;
  const svg = RDS.renderToStaticMarkup(React.createElement(C, { color, size: 256 }));
  const png = await sharp(Buffer.from(svg)).resize(256, 256, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toBuffer();
  return 'image/png;base64,' + png.toString('base64');
}

// ---------------------------------------------------------------- deck scaffolding
function newDeck(title) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.theme = { headFontFace: HEAD, bodyFontFace: BODY };
  pres.author = 'Matthew Kang';
  pres.title = title;
  pres.defineSlideMaster({
    title: 'CONTENT', background: { color: 'FFFFFF' },
    objects: [
      { rect: { x: CW, y: 0, w: 13.333 - CW, h: 7.5, fill: { color: K.navy }, line: { color: K.navy } } },
      { rect: { x: 9.9, y: 0.14, w: 2.95, h: 0.34, fill: { color: 'FFFFFF' }, line: { color: K.red, width: 1.25 } } },
      { text: { text: 'PRELIMINARY – FOR DISCUSSION', options: { x: 9.9, y: 0.14, w: 2.95, h: 0.34, fontFace: BODY, fontSize: 11, bold: true, color: K.red, align: 'center', valign: 'middle', margin: 0 } } },
      { text: { text: 'PUBLIC ITS MARKET CASE', options: { x: 0.4, y: 6.9, w: 2.2, h: 0.28, fontFace: HEAD, fontSize: 13, bold: true, color: K.navy, margin: 0 } } },
      { text: { text: 'Matthew Kang  |  November 2026', options: { x: 0.4, y: 7.16, w: 2.2, h: 0.2, fontFace: BODY, fontSize: 8, color: K.grey, margin: 0 } } },
      { text: { text: 'DISCUSSION DRAFT', options: { x: 10.25, y: 6.98, w: 2.0, h: 0.36, fontFace: HEAD, fontSize: 16, bold: true, color: K.red, align: 'right', margin: 0 } } },
      { placeholder: { options: { name: 'title', type: 'title', x: 0.45, y: 0.6, w: 12.4, h: 1.15, fontFace: HEAD, fontSize: 26, bold: true, color: K.navy, valign: 'top', align: 'left', margin: 0 }, text: '' } },
      { placeholder: { options: { name: 'source', type: 'body', x: 2.7, y: 6.84, w: 7.45, h: 0.56, fontFace: BODY, fontSize: 8, color: '333333', valign: 'bottom', align: 'left', margin: 0 }, text: '' } },
    ],
    slideNumber: { x: 12.35, y: 7.02, w: 0.55, h: 0.3, fontFace: BODY, fontSize: 11, bold: true, color: '000000', align: 'right' },
  });
  pres.defineSlideMaster({
    title: 'COVER', background: { color: 'FFFFFF' },
    objects: [
      { rect: { x: CW, y: 0, w: 13.333 - CW, h: 7.5, fill: { color: K.navy }, line: { color: K.navy } } },
      { text: { text: 'DISCUSSION DRAFT', options: { x: 10.25, y: 6.98, w: 2.0, h: 0.36, fontFace: HEAD, fontSize: 16, bold: true, color: K.red, align: 'right', margin: 0 } } },
    ],
  });
  return pres;
}

const T = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11, color: K.navy, valign: 'top' }, o));
const R = (s, x, y, w, h, fill, line) => s.addShape('rect', { x, y, w, h, fill: { color: fill }, line: { color: line || fill, width: line ? 1 : 0.5 } });

function crumb(s, items) {
  let x = 0;
  items.forEach((it, i) => {
    const w = 0.7 + it.text.length * 0.088;
    s.addShape(i === 0 ? 'homePlate' : 'chevron', { x, y: 0.17, w, h: 0.34, fill: { color: it.color }, line: { color: it.color } });
    T(s, it.text, { x: x + (i === 0 ? 0.42 : 0.3), y: 0.17, w: w - 0.55, h: 0.34, fontFace: HEAD, fontSize: 12, bold: true, color: 'FFFFFF', valign: 'middle' });
    x += w - 0.12;
  });
}
function title(s, lead, rest, leadColor) {
  s.addText([{ text: lead, options: { color: leadColor || K.lblue } }, { text: rest, options: { color: K.navy } }], { placeholder: 'title', lineSpacingMultiple: 0.9 });
}
function hbar(s, text, x, w, color, y = 1.86, h = 0.48, size = 16) {
  R(s, x, y, w, h, color);
  T(s, text, { x: x + 0.15, y, w: w - 0.3, h, fontFace: HEAD, fontSize: size, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
}
function source(s, text) { s.addText(text, { placeholder: 'source' }); }
// paragraph builder: runs = [[text, bold], ...]
function paras(list, o = {}) {
  const out = [];
  list.forEach((runs, pi) => {
    runs.forEach((r, ri) => {
      const opt = { bold: !!r[1] };
      if (r[2]) opt.color = r[2];
      if (ri === 0 && o.bullet !== false) { opt.bullet = { indent: 12 }; }
      if (ri === runs.length - 1 && pi < list.length - 1) opt.breakLine = true;
      if (ri === 0 && o.paraSpaceAfter !== undefined) opt.paraSpaceAfter = o.paraSpaceAfter;
      out.push({ text: r[0], options: opt });
    });
  });
  return out;
}
function pill(s, x, y, w, h, text, o = {}) {
  s.addShape('roundRect', { x, y, w, h, rectRadius: h / 2, fill: { color: o.fill || 'FFFFFF' }, line: { color: o.line || K.navy, width: o.lw || 1.5 } });
  T(s, text, { x: x + 0.05, y, w: w - 0.1, h, fontFace: o.font || HEAD, fontSize: o.size || 12, bold: o.bold !== false, color: o.color || K.navy, align: 'center', valign: 'middle' });
}
function iconTile(s, img, x, y, d, fill, rounded) {
  s.addShape(rounded ? 'roundRect' : 'rect', Object.assign({ x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } }, rounded ? { rectRadius: 0.08 } : {}));
  s.addImage({ data: img, x: x + d * 0.22, y: y + d * 0.22, w: d * 0.56, h: d * 0.56 });
}

const SRC_MAIN = 'Berg Insight (2026), UNIFE World Rail Market Study 2026, SCI Verkehr (2026), Global Market Insights (2026), FTA National Transit Database RY2025, company filings, analysis';

(async () => {
  const ic = {};
  for (const n of ['FaChartPie', 'FaArrowTrendUp', 'FaChessKnight', 'FaTriangleExclamation', 'FaBullseye', 'FaTrainSubway', 'FaTrain', 'FaBus', 'FaChargingStation', 'FaLandmark', 'FaHourglassHalf', 'FaFileContract', 'FaShieldHalved', 'FaArrowTrendDown', 'FaMapLocationDot', 'FaPuzzlePiece', 'FaHandHoldingDollar', 'FaLayerGroup', 'FaMagnifyingGlassChart', 'FaSackDollar']) ic[n] = await iconData(n);

  // ====================================================================== MAIN DECK
  const pres = newDeck('Public ITS Market: Roadway (Bus) and Railway');
  const SEC = 'Main deck';
  pres.addSection({ title: SEC });

  // ---------------------------------------------------------------- cover
  let s = pres.addSlide({ masterName: 'COVER', sectionTitle: SEC });
  R(s, 0, 2.3, CW, 2.1, K.navy);
  T(s, 'PUBLIC INTELLIGENT TRANSPORTATION SYSTEMS', { x: 0.7, y: 2.5, w: 11.9, h: 0.9, fontFace: HEAD, fontSize: 40, bold: true, color: 'FFFFFF', valign: 'middle' });
  T(s, 'ROADWAY (BUS) AND RAILWAY: MARKET ASSESSMENT AND INVESTMENT THESIS', { x: 0.7, y: 3.4, w: 11.8, h: 0.7, fontFace: HEAD, fontSize: 24, bold: true, color: K.lblue, valign: 'middle' });
  T(s, 'Written case  |  Matthew Kang  |  November 2026', { x: 0.7, y: 4.65, w: 9, h: 0.4, fontSize: 15, color: K.navy });
  T(s, 'Companion files: Public_ITS_Market_Model.xlsx (model) and Public_ITS_Market_Case_Appendix.pptx (supporting analysis)', { x: 0.7, y: 5.1, w: 11, h: 0.3, fontSize: 10.5, color: K.grey });

  // ---------------------------------------------------------------- 1. executive summary
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'EXECUTIVE SUMMARY', color: K.lblue }]);
  title(s, 'Executive Summary: ', 'A ~' + bn(total25, 0) + ' market growing ~5% a year, with a ~' + bn(OP.open.total, 0) + ' software and services pool best entered via buy-and-build in North America');
  R(s, 0.45, 1.9, 12.4, 0.42, K.navy);
  T(s, 'TOPIC', { x: 0.6, y: 1.9, w: 2.5, h: 0.42, fontSize: 12.5, bold: true, color: 'FFFFFF', valign: 'middle' });
  T(s, 'KEY FINDINGS', { x: 3.45, y: 1.9, w: 9, h: 0.42, fontSize: 12.5, bold: true, color: 'FFFFFF', valign: 'middle' });
  const ex = [
    ['FaChartPie', 'MARKET SIZE AND SEGMENTATION', [
      [['Public ITS for bus and passenger rail is ~' + bn(total25) + ' (2025, ex-fare). ', true], [pct(ccsShare, 0) + ' is rail signalling, and half the market is mainline signalling bought by rail infrastructure managers, not transit agencies']],
      [['The transit-operator core is ~' + bn(TI.core.total, 0) + '; '], ['only ~' + bn(OP.open.total) + ' (software and services in bus and other rail ITS) is open to an asset-light entrant', true]]]],
    ['FaArrowTrendUp', 'GROWTH TO 2031', [
      [['Base case ' + pct(FT.cagr) + ' a year to ~' + bn(total31, 0) + ' by 2031 ', true], ['(low ' + pct(SC.Low.cagr) + ', high ' + pct(SC.High.cagr) + '), driven by mandated modernisation: ERTMS rollout, metro resignalling and bus platforms reaching end of life']],
      [['The open software and services pool grows fastest, ~' + pct(SAM.cagr, 0) + ' a year to ~' + bn(SAM.values[6]), true], [', as value shifts from onboard hardware to cloud software']]]],
    ['FaChessKnight', 'COMPETITIVE DYNAMICS', [
      [['Signalling is a closed four-player oligopoly ', true], ['(Siemens, Hitachi, Alstom, CRSC) with 3-5 years of backlog and 25-30 year service tails']],
      [['Bus ITS is consolidating into strategics at ~0.4-1.6x revenue ', true], ['(Modaxo ~33%, Hitachi/Clever ~13% of North America), while SaaS challengers overlay legacy systems']]]],
    ['FaTriangleExclamation', 'RISKS AND BARRIERS', [
      [['The barrier is tenure, not rebid odds: ', true], ['systems come up for decision only every ~16 years, but incumbents won just 4 of 18 competitive rebids']],
      [['Near-term risks are the US funding reset ', true], ['(FY2027 federal transit -5% to -22% vs FY2026) '], ['and European signalling slippage', true]]]],
    ['FaBullseye', 'INVESTMENT THESIS', [
      [['Buy a founder-owned North American mid-market bus ITS vendor at 1-2.5x revenue, ', true], ['move it to cloud and add AI enforcement and zero-emission modules']],
      [['Returns hinge on earning a software multiple ', true], ['(~2.6x revenue) rather than the ~1.6x Hitachi paid for Clever Devices']]]],
  ];
  let y = 2.36;
  const rh = 0.8;
  ex.forEach(([icn, lab, bl], i) => {
    R(s, 0.45, y, 2.75, rh - 0.04, '1E9FE0');
    iconTile(s, ic[icn], 0.58, y + 0.15, 0.46, '1E9FE0');
    s.addShape('roundRect', { x: 0.58, y: y + 0.15, w: 0.46, h: 0.46, rectRadius: 0.06, fill: { type: 'none' }, line: { color: 'FFFFFF', width: 1.25 } });
    T(s, lab, { x: 1.14, y, w: 2.0, h: rh - 0.04, fontFace: HEAD, fontSize: 14, bold: true, color: 'FFFFFF', valign: 'middle' });
    T(s, paras(bl, { paraSpaceAfter: 3 }), { x: 3.4, y: y + 0.02, w: 9.4, h: rh - 0.06, fontSize: 11, color: '1A1A1A', valign: 'middle' });
    if (i < ex.length - 1) s.addShape('line', { x: 0.45, y: y + rh - 0.02, w: 12.4, h: 0, line: { color: K.navy, width: 1.25, dashType: 'sysDot' } });
    y += rh;
  });
  s.addShape('roundRect', { x: 0.45, y: 6.4, w: 12.4, h: 0.42, rectRadius: 0.21, fill: { color: K.navy }, line: { color: K.navy } });
  T(s, [{ text: 'Verdict: ', options: { bold: true, color: K.lblue } }, { text: 'attractive as a buy-and-build in bus ITS software and services; not a levered buy-out of a hardware integrator, and not in rail signalling', options: { color: 'FFFFFF' } }], { x: 0.7, y: 6.4, w: 11.9, h: 0.42, fontSize: 12, valign: 'middle', align: 'center' });
  source(s, 'Sources: ' + SRC_MAIN + '; see Public_ITS_Market_Model.xlsx');

  // ---------------------------------------------------------------- 2. market size: funnel + segment table
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'MARKET SIZE AND SEGMENTATION', color: K.lblue }, { text: 'ADDRESSABLE MARKET', color: K.navy }]);
  title(s, 'Market Size: ', 'A ~' + bn(total25, 0) + ' market, but half is mainline signalling bought by infrastructure managers; only ~' + bn(OP.open.total, 0) + ' of software and services is open to entrants');
  hbar(s, 'EST. ADDRESSABLE MARKET FUNNEL, 2025, BILLIONS USD', 0, 6.45, K.navy);
  hbar(s, 'MARKET BY SEGMENT AND REGION, 2025, BILLIONS USD', 6.51, CW - 6.51, K.navy);
  s.addShape('line', { x: 6.48, y: 2.45, w: 0, h: 4.3, line: { color: K.navy, width: 1.5 } });
  // funnel
  const fx = 0.45, fTop = 3.0, fBot = 0.45, fy0 = 2.66, fh = 0.79, nL = 5, cx = fx + fTop / 2;
  const wAt = k => fTop - (fTop - fBot) * k / nL;
  const fills = ['EEF4FA', 'E2ECF6', 'D3E3F2', 'C2D8EE', K.lblue];
  for (let k = 0; k < nL; k++) {
    const w0 = wAt(k), w1 = wAt(k + 1), yk = fy0 + k * fh, inset = (w0 - w1) / 2;
    s.addShape('custGeom', { x: cx - w0 / 2, y: yk, w: w0, h: fh, fill: { color: fills[k] }, line: { color: fills[k], width: 0.5 }, points: [{ x: 0, y: 0 }, { x: w0, y: 0 }, { x: w0 - inset, y: fh }, { x: inset, y: fh }, { close: true }] });
  }
  for (let k = 0; k < nL; k++) {
    const w0 = wAt(k), yk = fy0 + k * fh;
    s.addShape('ellipse', { x: cx - w0 / 2, y: yk - 0.07, w: w0, h: 0.14, fill: { color: k === nL - 1 ? K.navy : K.mblue }, line: { color: K.navy, width: 0.5 } });
  }
  s.addShape('ellipse', { x: cx - fBot / 2, y: fy0 + nL * fh - 0.05, w: fBot, h: 0.1, fill: { color: '9ED8F2' }, line: { color: '9ED8F2' } });
  const levels = [
    ['$40-60B', 'Global ITS market', 'Incl. road traffic management, tolling, aviation'],
    [bn(total25), 'Public ITS: bus + passenger rail', 'Case scope; software, hardware, services; ex-fare'],
    [bn(TI.core.total), 'Transit-operator core', 'Excl. ' + bn(S['Rail CCS mainline'].total) + ' mainline signalling (infrastructure buyers)'],
    [bn(D.contestable_2025), 'Contestable pool', 'Excl. all signalling (SIL-4, four suppliers)'],
    [bn(OP.open.total), 'Open software and services', 'Asset-light SAM; N. America ' + bn(OP.open.na) + ', Europe ' + bn(OP.open.eu)],
  ];
  levels.forEach(([v, lab, desc], k) => {
    const lx = cx + wAt(k) / 2 + 0.14, ly = fy0 + k * fh - 0.17;
    T(s, v, { x: lx, y: ly, w: 6.3 - lx, h: 0.32, fontFace: HEAD, fontSize: 21, bold: true, color: k === nL - 1 ? K.mblue : K.mblue });
    T(s, lab, { x: lx, y: ly + 0.31, w: 6.35 - lx, h: 0.2, fontSize: 11, bold: true, color: K.navy });
    T(s, desc, { x: lx, y: ly + 0.5, w: 6.35 - lx, h: 0.2, fontSize: 8.5, italic: true, color: '333333' });
  });
  s.addShape('ellipse', { x: 0.15, y: 5.45, w: 1.28, h: 1.28, fill: { color: 'FFFFFF' }, line: { color: K.black, width: 1.5 } });
  T(s, '~' + pct(OP.open.total / total25, 0), { x: 0.15, y: 5.58, w: 1.28, h: 0.36, fontFace: HEAD, fontSize: 21, bold: true, color: K.mblue, align: 'center' });
  T(s, 'OF CASE SCOPE OPEN TO A NEW ENTRANT', { x: 0.25, y: 5.93, w: 1.08, h: 0.6, fontFace: HEAD, fontSize: 10, bold: true, color: K.black, align: 'center' });
  s.addShape('line', { x: 1.43, y: 6.2, w: cx - fBot / 2 - 1.43 + 0.15, h: 0, line: { color: K.black, width: 1.25, endArrowType: 'triangle' } });
  // segment x region heat table
  const geos = ['North America', 'Europe', 'Asia-Pacific', 'Rest of world'];
  const segs = [['Bus and tram ITS', 'Bus'], ['Urban signalling (metro, LRT)', 'Rail CCS urban'], ['Mainline and commuter signalling', 'Rail CCS mainline'], ['Other rail ITS (PIS, CCTV, monitoring)', 'Rail other']];
  const heat = v => v < 0.6 ? 'F3F9FD' : v < 1.2 ? 'DDEFFA' : v < 2.5 ? 'B5DDF3' : v < 5 ? '74C3EC' : '1F8FD0';
  const hc = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 11, color: '1A1A1A', valign: 'middle', align: 'center', margin: 0.04 }, o) });
  const hh = t => hc(t, { bold: true, color: 'FFFFFF', fill: { color: K.navy }, fontSize: 10 });
  const rows = [[hh('Segment'), hh('N. America'), hh('Europe'), hh('Asia-Pac.'), hh('Rest of world'), hh('Total'), hh('HW / SW / Svc')]];
  segs.forEach(([lab, blk]) => {
    const vals = geos.map(g => geoOf(blk, g));
    const sg = S[blk];
    rows.push([hc(lab, { align: 'left', bold: true, color: K.navy, fontSize: 10.5 })].concat(vals.map(v => hc('$' + v.toFixed(1), { fill: { color: heat(v) }, color: v >= 5 ? 'FFFFFF' : '1A1A1A', bold: v >= 5 }))).concat([hc('$' + sg.total.toFixed(1), { bold: true, fill: { color: K.lgrey } }), hc(Math.round(sg.hw / sg.total * 100) + ' / ' + Math.round(sg.sw / sg.total * 100) + ' / ' + Math.round(sg.svc / sg.total * 100), { fontSize: 10 })]));
  });
  rows.push([hc('Total', { align: 'left', bold: true, color: K.navy })].concat(geos.map(g => hc('$' + D.geos[g].total.toFixed(1) + ' (' + pct(D.geos[g].share, 0) + ')', { bold: true, fill: { color: K.lgrey }, fontSize: 10 }))).concat([hc('$' + total25.toFixed(1), { bold: true, fill: { color: K.navy }, color: 'FFFFFF' }), hc(pct(D.components.Hardware.share, 0).replace('%', '') + ' / ' + pct(D.components.Software.share, 0).replace('%', '') + ' / ' + pct(D.components.Services.share, 0).replace('%', ''), { bold: true, fontSize: 10, fill: { color: K.lgrey } })]));
  s.addTable(rows, { x: 6.68, y: 2.6, w: 6.2, colW: [1.82, 0.72, 0.68, 0.7, 0.72, 0.68, 0.88], rowH: [0.42, 0.5, 0.5, 0.5, 0.5, 0.48], fontFace: BODY, border: { type: 'solid', pt: 0.75, color: 'FFFFFF' }, autoPage: false });
  s.addShape('roundRect', { x: 6.68, y: 5.68, w: 6.2, h: 1.02, rectRadius: 0.1, fill: { color: K.paler }, line: { color: K.mblue, width: 1.25 } });
  T(s, paras([
    [['Buyer lens: ', true, K.mblue], ['mainline signalling (' + pct(S['Rail CCS mainline'].share, 0) + ' of value) is bought by DB InfraGO, Network Rail, RFI and Amtrak; transit agencies buy the ~' + bn(TI.core.total, 0) + ' core']],
    [['Component lens: ', true, K.mblue], ['hardware is still ' + pct(D.components.Hardware.share, 0) + ' of value, but software grows fastest as onboard systems move to cloud']],
  ], { paraSpaceAfter: 4 }), { x: 6.85, y: 5.74, w: 5.9, h: 0.92, fontSize: 10.5, color: '1A1A1A', valign: 'middle' });
  source(s, 'Note: Figures may not sum due to rounding; HW / SW / Svc = hardware / software / services share of each segment (%). Nominal USD at 2025 average FX (1.13 USD/EUR). Sources: ' + SRC_MAIN);

  // ---------------------------------------------------------------- 3. growth to 2031 + drivers
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'MARKET GROWTH', color: K.lblue }, { text: 'GROWTH DRIVERS TO 2031', color: K.green }]);
  title(s, 'Market Growth: ', 'Public ITS grows ~5% a year to ~' + bn(total31, 0) + ' by 2031, led by mandated signalling modernisation; the open software and services pool grows fastest at ~' + pct(SAM.cagr, 0), K.green);
  hbar(s, 'PUBLIC ITS MARKET BY SEGMENT, GLOBAL, 2025-2031E, BILLIONS USD', 0, 8.15, K.dgreen);
  hbar(s, 'KEY GROWTH DRIVERS AND HEADWINDS', 8.21, CW - 8.21, K.dgreen);
  const ser = [['Mainline and commuter signalling', mainSeries, K.sMain], ['Urban signalling', urbanSeries, K.sUrban], ['Other rail ITS', othSeries, K.sOther], ['Bus and tram ITS', busSeries, K.sBus]];
  const ch = { x: 1.95, y: 2.5, w: 5.3, h: 3.35 }, lay = { x: 0.02, y: 0.13, w: 0.96, h: 0.87 }, vmax = 42;
  s.addChart(pres.ChartType.bar, ser.map(([n, v]) => ({ name: n, labels: yrs, values: v.map(x => +x.toFixed(2)) })), {
    x: ch.x, y: ch.y, w: ch.w, h: ch.h, barDir: 'col', barGrouping: 'stacked', barGapWidthPct: 40, layout: lay,
    catAxisHidden: true, valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: vmax, valGridLine: { style: 'none' }, catGridLine: { style: 'none' },
    showLegend: false, showValue: true, dataLabelPosition: 'ctr', dataLabelColor: 'FFFFFF', dataLabelFontFace: HEAD, dataLabelFontSize: 11, dataLabelFontBold: true, dataLabelFormatCode: '"$"0.0',
    chartColors: ser.map(x => x[2]), plotArea: { fill: { color: 'FFFFFF' } },
  });
  const px = ch.x + lay.x * ch.w, pw = lay.w * ch.w, py = ch.y + lay.y * ch.h, ph = lay.h * ch.h, band = pw / 7;
  const yv = v => py + ph * (1 - v / vmax);
  FT.values.forEach((v, i) => T(s, '$' + v.toFixed(1) + 'B', { x: px + band * i, y: yv(v) - 0.32, w: band, h: 0.3, fontFace: HEAD, fontSize: 15, bold: true, color: K.navy, align: 'center', valign: 'bottom' }));
  const yb = py + ph + 0.03;
  R(s, px, yb, pw, 0.28, K.black);
  yrs.forEach((t, i) => T(s, i === 0 ? t : t + 'E', { x: px + band * i, y: yb, w: band, h: 0.28, fontSize: 11, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' }));
  R(s, px, yb + 0.28, pw, 0.32, 'E9EEF3', K.black);
  SAM.values.forEach((v, i) => T(s, '$' + v.toFixed(1) + 'B', { x: px + band * i, y: yb + 0.28, w: band, h: 0.32, fontSize: 11, bold: true, color: K.navy, align: 'center', valign: 'middle' }));
  T(s, 'Open software and services pool', { x: 0.3, y: yb + 0.26, w: 1.6, h: 0.36, fontSize: 9.5, bold: true, color: K.navy, align: 'right', valign: 'middle' });
  // legend (top series first) and CAGR pills
  const legY = [3.0, 3.72, 4.44, 5.16];
  const legOrder = [3, 2, 1, 0];
  T(s, '2025-31E CAGR:', { x: 7.3, y: 2.45, w: 0.85, h: 0.3, fontFace: HEAD, fontSize: 11, bold: true, color: K.navy, align: 'center', valign: 'bottom' });
  pill(s, 7.33, yv(total31) - 0.3, 0.8, 0.28, pct(FT.cagr), { line: K.black, size: 12 });
  legOrder.forEach((si, k) => {
    const [n, v, col] = ser[si];
    const ly = legY[k];
    T(s, n, { x: 0.3, y: ly - 0.02, w: 1.6, h: 0.42, fontSize: 10.5, bold: true, color: col === K.sBus ? '1B8CC4' : col, valign: 'bottom' });
    s.addShape('line', { x: 0.3, y: ly + 0.44, w: 1.6, h: 0, line: { color: col, width: 3 } });
    pill(s, 7.33, ly + 0.12, 0.8, 0.28, pct(cg(v)), { line: col, size: 12, color: col === K.sBus ? '1B8CC4' : col });
  });
  // drivers panel
  const drv = [
    ['FaTrainSubway', 'ERTMS / ETCS mandate (Europe)', 'EUR 85-100B left to deploy; only ~10% of the TEN-T network equipped at end-2024', 'HIGH', K.green],
    ['FaTrain', 'Legacy metro resignalling (CBTC)', 'NYC $5.4B of CBTC in 2025-29; ~90% of European signalling spend is modernisation', 'HIGH', K.green],
    ['FaBus', 'Bus platform refresh cycle', '~12K US buses on 2009-16 CAD/AVL platforms hit 15-20 years by 2031', 'HIGH', K.green],
    ['FaChargingStation', 'Zero-emission buses, AI enforcement', '60% of new EU city buses are zero-emission; NYC lane cameras on 1,900+ buses', 'MID', K.mblue],
    ['FaLandmark', 'Headwind: funding reset, ETCS delays', 'FY2027 US federal transit -5% to -22% vs FY2026; UK CP7 ETCS budget cut 35%', 'MID', K.grey],
  ];
  drv.forEach(([icn, h, st, lvl, col], i) => {
    const ry = 2.5 + i * 0.83;
    iconTile(s, ic[icn], 8.35, ry + 0.06, 0.62, i === 4 ? K.grey : K.green);
    T(s, h, { x: 9.1, y: ry + 0.02, w: 2.95, h: 0.26, fontSize: 10.5, bold: true, color: K.navy, valign: 'top' });
    T(s, st, { x: 9.1, y: ry + 0.28, w: 2.95, h: 0.5, fontSize: 9.5, color: '1A1A1A', valign: 'top' });
    R(s, 12.12, ry + 0.12, 0.78, 0.5, col);
    T(s, lvl, { x: 12.12, y: ry + 0.12, w: 0.78, h: 0.5, fontFace: HEAD, fontSize: 15, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
    if (i < drv.length - 1) s.addShape('line', { x: 8.35, y: ry + 0.79, w: 4.55, h: 0, line: { color: K.mgrey, width: 0.75 } });
  });
  T(s, 'Impact on 2025-31 growth', { x: 10.9, y: 6.64, w: 2.0, h: 0.18, fontSize: 7.5, italic: true, color: K.grey, align: 'right' });
  source(s, 'Note: Base case shown, nominal USD at 2025 FX; low case ' + bn(SC.Low.values[6]) + ' (' + pct(SC.Low.cagr) + ' CAGR), high case ' + bn(SC.High.values[6]) + ' (' + pct(SC.High.cagr) + '). Sources: European Commission ERTMS Work Plan (2026), MTA 2025-29 Capital Program, ACEA, FTA, Network Rail CP7, ' + SRC_MAIN);

  // ---------------------------------------------------------------- 4. competitive landscape grid
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'COMPETITIVE LANDSCAPE', color: K.lblue }, { text: 'PLAYER GROUPS', color: K.navy }]);
  title(s, 'Competitive Landscape: ', 'Signalling is a closed four-player oligopoly; bus ITS is consolidating at ~0.4-1.6x revenue while SaaS challengers unbundle it');
  hbar(s, 'COMPETITIVE SUMMARY: PUBLIC ITS PLAYER GROUPS AND IMPLICATIONS FOR A NEW ENTRANT', 0, CW, K.navy);
  const cols = [
    ['SIGNALLING MAJORS', 'Siemens, Hitachi (incl. Thales GTS), Alstom, CRSC',
      'Each holds 13-22% of a ~$21B passenger signalling market; backlog 3-5x revenue',
      ['SIL-4 certified systems; 25-30 year service tails', 'Multi-year frameworks (e.g., DB EUR 6.3B)'],
      ['Project execution risk (Alstom 2026 profit warning)', 'Tied to slow, publicly funded ETCS rollout'],
      ['Closed core: compete only in adjacencies (condition monitoring, cyber, connectivity)']],
    ['BUS ITS CONSOLIDATORS', 'Modaxo (Trapeze, Vontas, Routeward); Hitachi (Clever Devices)',
      'Modaxo ~33% and Hitachi/Clever ~13% of the North American bus ITS pool',
      ['Largest installed base; 15-20 year customer tenure', 'Permanent capital: Modaxo never sells'],
      ['1990s-era CAD/AVL architectures', 'Incumbents lost 8 of 8 tracked competitive CAD/AVL rebids'],
      ['Natural exit buyers, not targets (Hitachi paid ~1.6x revenue for Clever)']],
    ['LISTED INTEGRATORS', 'INIT, IVU (Cubic: private, distressed)',
      'INIT EUR 330M (~9% of N. America, ~6% of Europe); IVU EUR 150M, 52% recurring',
      ['Full stack: CAD/AVL, APC, scheduling, fare', 'Service contracts of up to 20 years'],
      ['Hardware and project mix compresses margins (INIT FY26 EBIT cut)', 'Cubic: ~11x leverage, rated CC'],
      ['Set the exit benchmark: 1.0x (INIT) to 2.6x (IVU) revenue, rising with recurring mix']],
    ['MID-MARKET PRIVATES', 'Avail, GIRO, Hanover, ETA, Passio, Luminator',
      'Fragmented: ~29% of the N. America pool sits outside the top five owners',
      ['Sticky mid-tier agency relationships', 'Hanover: GBP 93M revenue, +28%, 17% margin'],
      ['Sub-scale R&D and ageing code', 'Key-person and succession risk'],
      ['Most actionable acquisition targets for a buy-and-build platform']],
    ['SAAS / AI CHALLENGERS', 'Swiftly, Optibus, Via, Hayden AI',
      'Swiftly: real-time for ~12% of US buses; Via $434M revenue at 5.6x EV/revenue',
      ['Cloud overlays need little hardware', 'AI enforcement is self-funding via citations'],
      ['Loss-making at scale (Via adj. EBITDA -8%)', 'Subscriptions fit poorly with 80/20 capital grants'],
      ['Partner or overlay model; later-stage targets only at 5x+ revenue']],
  ];
  const gx = 0.35, lw = 1.5, gw = 2.18, gg = 0.04, gy = 2.44;
  const rowsG = [['MARKET POSITION', 0.66, K.navy, 'FFFFFF', '1A1A1A'], ['KEY STRENGTHS', 0.8, K.slate, K.pale, '1A1A1A'], ['KEY WEAKNESSES', 0.8, K.purple, K.lpurple, '1A1A1A'], ['IMPLICATION FOR A NEW ENTRANT', 0.72, K.black, K.grey, 'FFFFFF']];
  cols.forEach((c, j) => {
    const x = gx + lw + gg + j * (gw + gg);
    R(s, x, gy, gw, 0.6, K.navy);
    T(s, c[0], { x: x + 0.06, y: gy + 0.04, w: gw - 0.12, h: 0.26, fontFace: HEAD, fontSize: 12.5, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
    T(s, c[1], { x: x + 0.06, y: gy + 0.29, w: gw - 0.12, h: 0.29, fontSize: 8, color: '9FD7F3', align: 'center', valign: 'middle' });
  });
  let ry = gy + 0.64;
  rowsG.forEach(([lab, h, lc, cc, tc], ri) => {
    if (ri === 3) {
      cols.forEach((c, j) => { const x = gx + lw + gg + j * (gw + gg); s.addShape('triangle', { x: x + gw / 2 - 0.3, y: ry - 0.02, w: 0.6, h: 0.2, flipV: true, fill: { color: K.navy }, line: { color: K.navy } }); });
      ry += 0.2;
    }
    R(s, gx, ry, lw, h, lc);
    T(s, lab, { x: gx + 0.08, y: ry, w: lw - 0.14, h, fontFace: HEAD, fontSize: 12.5, bold: true, color: 'FFFFFF', valign: 'middle' });
    cols.forEach((c, j) => {
      const x = gx + lw + gg + j * (gw + gg);
      R(s, x, ry, gw, h, cc, ri === 0 ? K.mgrey : undefined);
      let body;
      if (ri === 0) body = [{ text: c[2], options: { bold: true } }];
      else body = paras((ri === 1 ? c[3] : ri === 2 ? c[4] : c[5]).map(t => [[t, ri === 3]]), { bullet: ri !== 3 });
      T(s, body, { x: x + 0.07, y: ry + 0.02, w: gw - 0.12, h: h - 0.04, fontSize: 9.5, color: tc, valign: 'middle' });
    });
    ry += h + 0.04;
  });
  source(s, 'Note: Shares are indicative, based on filed vendor revenue against the model pools. Sources: company reports and statutory filings (Siemens, Hitachi, Alstom, CRSC, INIT, IVU, Via, Conduent, Companies House), Berg Insight, deal announcements, trading data as of 6 Nov 2026, GTFS-Realtime feed census, agency board records, analysis');

  // ---------------------------------------------------------------- 5. risks and barriers
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'RISKS AND BARRIERS TO ENTRY', color: K.lblue }, { text: 'IMPACT ON A NEW ENTRANT', color: K.grey }]);
  title(s, 'Risks and Barriers: ', 'Long system lives and slow procurement are structural barriers; near-term risks are the US funding reset and hardware leverage', K.grey);
  T(s, 'BARRIERS AND RISKS', { x: 0.45, y: 1.86, w: 5.9, h: 0.34, fontFace: HEAD, fontSize: 17, bold: true, color: K.navy, align: 'center', valign: 'bottom' });
  T(s, 'LIKELY IMPACT ON A NEW ENTRANT', { x: 6.95, y: 1.86, w: 5.95, h: 0.34, fontFace: HEAD, fontSize: 17, bold: true, color: K.navy, align: 'center', valign: 'bottom' });
  R(s, 0.45, 2.24, 5.9, 0.06, K.black); R(s, 6.95, 2.24, 5.95, 0.06, K.black);
  const rk = [
    ['FaHourglassHalf', 'Incumbency and long system lives', 'Systems reach a decision point only every ~16 years, and most renewals are sole-sourced extensions', 'HIGH', K.green,
      [[['Only ~1/16 of the installed base comes up for decision each year']], [['However, incumbents won just 4 of 18 competitive rebids (0 of 8 in bus CAD/AVL): '], ['challengers usually win when a rebid happens', true]]]],
    ['FaFileContract', 'Slow, formal public procurement', '2-4 years from award to go-live; bid protests; Buy America requires >70% US content for hardware', 'HIGH/ MID', K.teal,
      [[['Long sales cycles favour vendors with reference fleets and live pilots']], [['Software-led entry and cooperative purchasing (NASPO, Sourcewell) shorten the path', true]]]],
    ['FaShieldHalved', 'Rail certification and signalling oligopoly', 'SIL-4 and ERA/FRA approvals; 10-30 year frameworks; four suppliers hold ~73% of signalling', 'HIGH', K.green,
      [[['Signalling cores are effectively closed to new entrants']], [['Adjacencies remain contestable: ', true], ['condition monitoring, cybersecurity, onboard connectivity']]]],
    ['FaLandmark', 'US funding reset and ETCS slippage', 'IIJA advance appropriations ($4.25B/yr) lapsed Sep 2026; FY2027 scenarios -5% to -22%; EU ETCS behind schedule', 'MID', K.mblue,
      [[['Formula funds that pay for system refresh are the most durable federal line', true]], [['Agencies in states without rescue packages (PA, WA, OR) may defer purchases']]]],
    ['FaArrowTrendDown', 'Execution and leverage in hardware-heavy models', 'Cubic (~11x leverage at LBO) now rated CC; Alstom, INIT and Kapsch issued 2026 profit warnings', 'MID', K.mblue,
      [[['Project-heavy integrators do not support LBO leverage', true]], [['Underwrite on recurring revenue; leave hardware to OEM and manufacturing partners']]]],
  ];
  rk.forEach(([icn, h, desc, lvl, col, bl], i) => {
    const ry2 = 2.36 + i * 0.86, rh2 = 0.8;
    R(s, 0.45, ry2, 0.85, rh2, K.dgrey);
    s.addImage({ data: ic[icn], x: 0.45 + 0.2, y: ry2 + (rh2 - 0.45) / 2, w: 0.45, h: 0.45 });
    R(s, 1.33, ry2, 5.02, rh2, K.lgrey);
    T(s, [{ text: h, options: { bold: true, breakLine: true, fontSize: 12 } }, { text: desc, options: { fontSize: 10.5 } }], { x: 1.45, y: ry2 + 0.03, w: 4.82, h: rh2 - 0.06, color: '1A1A1A', valign: 'middle' });
    s.addShape('chevron', { x: 6.42, y: ry2 + 0.2, w: 0.22, h: 0.4, fill: { color: K.grey }, line: { color: K.grey } });
    s.addShape('chevron', { x: 6.58, y: ry2 + 0.2, w: 0.22, h: 0.4, fill: { color: K.dgrey }, line: { color: K.dgrey } });
    R(s, 6.95, ry2, 1.05, rh2, col);
    T(s, lvl, { x: 6.95, y: ry2, w: 1.05, h: rh2, fontFace: HEAD, fontSize: 16, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
    R(s, 8.03, ry2, 4.87, rh2, K.lgrey);
    T(s, paras(bl, { paraSpaceAfter: 2 }), { x: 8.13, y: ry2 + 0.03, w: 4.7, h: rh2 - 0.06, fontSize: 10, color: '1A1A1A', valign: 'middle' });
  });
  R(s, 0.45, 6.68, 5.9, 0.06, K.black); R(s, 6.95, 6.68, 5.95, 0.06, K.black);
  source(s, 'Sources: agency board records (LA Metro, TfL, CTA, MARTA, Miami-Dade), 2016-26 award dataset (39 decision points), INIT annual report 2025, FTA Federal Register notices, H.R. 8870, EC ERTMS Work Plan (2026), Fitch, analysis');

  // ---------------------------------------------------------------- 6. investment thesis
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'INVESTMENT THESIS', color: K.lblue }, { text: 'NEW ENTRANT', color: K.navy }]);
  title(s, 'Investment Thesis: ', 'Enter via buy-and-build in North American bus ITS software; returns depend on re-rating a ~1.6x-revenue integrator into a 2.5x+ software asset');
  hbar(s, 'INVESTMENT THESIS FOR A NEW ENTRANT', 0, CW, K.navy);
  s.addShape('roundRect', { x: 0.35, y: 2.48, w: 3.75, h: 4.25, rectRadius: 0.12, fill: { color: K.navy }, line: { color: K.navy } });
  s.addImage({ data: ic.FaBullseye, x: 0.6, y: 2.66, w: 0.5, h: 0.5 });
  T(s, 'OUR RECOMMENDATION', { x: 1.22, y: 2.68, w: 2.75, h: 0.46, fontFace: HEAD, fontSize: 17, bold: true, color: 'FFFFFF', valign: 'middle' });
  T(s, 'Acquire a founder-owned North American mid-market bus ITS vendor at 1-2.5x revenue, move it to cloud, add AI enforcement and zero-emission modules, and grow recurring revenue above 50%.', { x: 0.6, y: 3.25, w: 3.3, h: 1.35, fontSize: 12, bold: true, color: 'FFFFFF' });
  T(s, [{ text: 'Avoid: ', options: { bold: true, color: K.lblue } }, { text: 'signalling cores and levered hardware roll-ups', options: { color: 'FFFFFF' } }], { x: 0.6, y: 4.6, w: 3.3, h: 0.42, fontSize: 11 });
  T(s, 'ILLUSTRATIVE GROSS MOIC, 5-YEAR HOLD', { x: 0.6, y: 5.15, w: 3.3, h: 0.25, fontFace: HEAD, fontSize: 12, bold: true, color: K.lblue });
  const mo = [['Integrator exit (1.6x revenue)', TH.moica, K.mgrey], ['Software re-rating (' + TH.evrev.toFixed(1) + 'x revenue)', TH.moic, K.lblue]];
  mo.forEach(([lab, v, col], i) => {
    const by = 5.48 + i * 0.58;
    T(s, lab, { x: 0.6, y: by, w: 3.3, h: 0.2, fontSize: 9, color: 'FFFFFF' });
    R(s, 0.6, by + 0.22, 2.5 * v / 2.2, 0.26, col);
    T(s, v.toFixed(1) + 'x', { x: 0.65 + 2.5 * v / 2.2, y: by + 0.2, w: 0.6, h: 0.3, fontFace: HEAD, fontSize: 14, bold: true, color: 'FFFFFF', valign: 'middle' });
  });
  const th = [
    ['FaMapLocationDot', 'WHERE TO PLAY', [[['~' + bn(OP.open.total) + ' open software and services pool ', true], ['(North America ' + bn(OP.open.na) + '), growing ~' + pct(SAM.cagr, 0) + ' a year']], [['Wedges beside incumbents: real-time and cloud CAD/AVL overlays, AI enforcement and safety video, zero-emission scheduling and energy management']]]],
    ['FaBus', 'WHY NORTH AMERICA FIRST', [[['Dated refresh wave: ', true], ['~12K buses on 2009-16 platforms reach 15-20 years by 2031']], [['Open mid-tier: ', true], ['195 agencies with 50-999 buses hold 55% of the fleet; 63% of US bus agencies publish no real-time feed']]]],
    ['FaPuzzlePiece', 'HOW TO WIN', [[['Coexist, then displace: ', true], ['sell modules on top of legacy systems and win end-of-life rebids, where challengers take 14 of 18']], [['Use cooperative purchasing and OEM hardware partners; structure subscriptions to fit 80/20 capital grants']]]],
    ['FaHandHoldingDollar', 'RETURNS AND EXIT', [[['Buyers: Hitachi, Siemens, Modaxo, Via. '], ['The Clever precedent (~1.6x revenue) returns only ~' + TH.moica.toFixed(1) + 'x', true]], [['A software re-rating (~' + TH.evrev.toFixed(1) + 'x revenue) returns ~' + TH.moic.toFixed(1) + 'x, ', true], ['so recurring mix above 50% is the key diligence question']]]],
  ];
  th.forEach(([icn, lab, bl], i) => {
    const ty = 2.48 + i * 1.07, th2 = 1.02;
    R(s, 4.3, ty, 2.25, th2, '1E9FE0');
    s.addImage({ data: ic[icn], x: 4.42, y: ty + (th2 - 0.42) / 2, w: 0.42, h: 0.42 });
    T(s, lab, { x: 4.95, y: ty, w: 1.55, h: th2, fontFace: HEAD, fontSize: 14, bold: true, color: 'FFFFFF', valign: 'middle' });
    T(s, paras(bl, { paraSpaceAfter: 3 }), { x: 6.7, y: ty + 0.02, w: 6.15, h: th2 - 0.04, fontSize: 10.5, color: '1A1A1A', valign: 'middle' });
    if (i < th.length - 1) s.addShape('line', { x: 4.3, y: ty + th2 + 0.025, w: 8.6, h: 0, line: { color: K.navy, width: 1.25, dashType: 'sysDot' } });
  });
  source(s, 'Note: Value bridge is illustrative ($60M revenue entry at 2.0x, 15% margin, 2.5x leverage, $40M bolt-ons at 1.5x, 8% organic growth, 22% exit margin), not a valuation. Sources: Hitachi Q1 FY2026 results, NTD RY2025, GTFS-Realtime feed census, award dataset, trading data, analysis');

  const out = path.join(__dirname, 'Public_ITS_Market_Case.pptx');
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log('wrote', out);

  // ====================================================================== APPENDIX DECK
  const ap = newDeck('Public ITS Market Case: Appendix');
  const AS = 'Appendix';
  ap.addSection({ title: AS });
  s = ap.addSlide({ masterName: 'COVER', sectionTitle: AS });
  R(s, 0, 2.3, CW, 2.1, K.navy);
  T(s, 'APPENDIX: SUPPORTING ANALYSIS', { x: 0.7, y: 2.5, w: 11.8, h: 0.9, fontFace: HEAD, fontSize: 44, bold: true, color: 'FFFFFF', valign: 'middle' });
  T(s, 'PUBLIC ITS MARKET CASE: ROADWAY (BUS) AND RAILWAY', { x: 0.7, y: 3.4, w: 11.8, h: 0.7, fontFace: HEAD, fontSize: 24, bold: true, color: K.lblue, valign: 'middle' });
  T(s, 'A1 Segmentation framework  |  A2 Top-down triangulation  |  A3 Growth bridge and scenarios  |  A4 Shares and multiples  |  A5 Bus unit economics and incumbency', { x: 0.7, y: 4.65, w: 11.8, h: 0.4, fontSize: 12.5, color: K.navy });

  // A1 segmentation framework
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A1 SEGMENTATION FRAMEWORK', color: K.navy }]);
  title(s, 'Segmentation Framework: ', 'Public ITS is cut by mode, functional domain and component layer; fare collection and road traffic management are excluded');
  hbar(s, 'PUBLIC ITS SEGMENTATION: MODE x FUNCTIONAL DOMAIN x COMPONENT LAYER', 0, CW, K.navy);
  const fc = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 10, color: '1A1A1A', valign: 'middle', margin: 0.06 }, o) });
  const fh2 = t => fc(t, { bold: true, color: 'FFFFFF', fill: { color: K.navy }, fontSize: 11, align: 'center' });
  const fl = t => fc(t, { bold: true, color: 'FFFFFF', fill: { color: '1E9FE0' }, fontFace: HEAD, fontSize: 12.5 });
  const fw = [
    [fh2('Functional domain'), fh2('Roadway (bus, BRT, paratransit)'), fh2('Railway (metro, LRT, commuter, mainline passenger)')],
    [fl('A. Operations and fleet management'), fc('Hardware: onboard computer, MDT, radio | Software: CAD/AVL, scheduling, dispatch | Services: integration, hosting'), fc('Hardware: train tracking, control-centre systems | Software: traffic and crew management, timetabling')],
    [fl('B. Passenger information'), fc('Hardware: onboard and stop displays, annunciators | Software: real-time prediction, GTFS-Realtime, apps'), fc('Hardware: platform and onboard displays, PA | Software: real-time and disruption information')],
    [fl('C. Safety, security and surveillance'), fc('Hardware: cameras, collision sensors | Software: AI incident detection, bus-lane enforcement'), fc('Hardware: onboard and station CCTV, intrusion sensors | Software: video analytics, obstacle detection')],
    [fl('D. Asset, telematics and condition monitoring'), fc('Hardware: APC, vehicle-health telematics | Software: asset, energy and charge management'), fc('Hardware: APC, trackside detectors (hot box, wheel impact) | Software: predictive maintenance, digital twins')],
    [fl('E. Train control and signalling'), fc('Not applicable (transit signal priority is a road adjacency)', { color: K.grey, italic: true }), fc('Hardware: interlockings, wayside and onboard ETCS / CBTC / PTC | Software: ATO, ATS | Services: 25-30 year maintenance')],
    [fc('Adjacent, excluded', { bold: true, color: 'FFFFFF', fill: { color: K.grey }, fontFace: HEAD, fontSize: 12.5 }), fc('Fare collection and ticketing ($10-17B), road traffic management and tolling', { fill: { color: K.lgrey } }), fc('Fare collection, rolling stock and TCMS, civil works, freight rail', { fill: { color: K.lgrey } })],
  ];
  s.addTable(fw, { x: 0.45, y: 2.48, w: 12.4, colW: [2.6, 4.9, 4.9], rowH: [0.36, 0.52, 0.52, 0.52, 0.52, 0.52, 0.48], border: { type: 'solid', pt: 0.75, color: 'C7D3DA' }, autoPage: false });
  T(s, paras([[['Geography: ', true, K.mblue], ['North America, Europe, Asia-Pacific (China split out for signalling), rest of world']], [['Customer tier (US bus): ', true, K.mblue], ['1,000+ buses (10 agencies, 29% of fleet), 250-999 (46, 31%), 50-249 (149, 23%), under 50 (772, 16%)']]], { paraSpaceAfter: 3 }), { x: 0.45, y: 6.22, w: 12.4, h: 0.55, fontSize: 10.5, color: '1A1A1A' });
  source(s, 'Sources: FTA NTD RY2025 (agency tiers), analysis');

  // A2 top-down triangulation
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A2 TOP-DOWN TRIANGULATION', color: K.navy }]);
  title(s, 'Top-Down Triangulation: ', 'Bus is anchored on Berg Insight and signalling on UNIFE; umbrella ITS reports are 6-10x too broad for this scope');
  hbar(s, 'THIRD-PARTY MARKET ESTIMATES: WHAT EACH INCLUDES AND HOW THE MODEL USES IT', 0, CW, K.navy);
  const tc = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 10, color: '1A1A1A', valign: 'middle', margin: 0.05 }, o) });
  const th3 = t => tc(t, { bold: true, color: 'FFFFFF', fill: { color: K.navy }, fontSize: 10.5 });
  const fit = (t, c) => tc(t, { bold: true, color: 'FFFFFF', fill: { color: c }, align: 'center', fontFace: HEAD, fontSize: 12 });
  const td = [
    [th3('Source'), th3('2025 value'), th3('What it includes'), th3('Fit'), th3('How the model uses it')],
    [tc('Global ITS reports (MarketsandMarkets, Precedence, Grand View, Mordor)', { bold: true }), tc('$40-60B'), tc('Road traffic management (~38%), tolling, parking, aviation, maritime; public transport only ~11-17%'), fit('LOW', K.grey), tc('Context only')],
    [tc('Berg Insight, Public Transport ITS, 10th ed. (2026)', { bold: true }), tc('EUR 2.55B Europe + EUR 1.22B N. America'), tc('Onboard, stop, depot and back-office systems for buses and trams; fare payment named in scope'), fit('HIGH', K.green), tc('Bus anchor, less a 20% ex-fare haircut (sensitivity 0-25%: $4.3-5.8B)')],
    [tc('Global Market Insights, APTS (2026)', { bold: true }), tc('$6.8B'), tc('Location, dispatch, passenger information, fare, analytics across bus, rail, air, water'), fit('MID', K.mblue), tc('Component, application and regional mix; rest-of-world scaling')],
    [tc('UNIFE World Rail Market Study 2026 (Bain)', { bold: true }), tc('EUR 24.9B rail control'), tc('Control-command and signalling, trackside and onboard, freight included; maintenance booked separately'), fit('HIGH', K.green), tc('Signalling anchor, carved to passenger rail (74%) by region')],
    [tc('SCI Verkehr CCS study (2026)', { bold: true }), tc('~EUR 20B'), tc('Train control and signalling incl. after-sales; Europe ~half; ~90% of European volume is modernisation'), fit('HIGH', K.green), tc('Low-case signalling anchor; growth cross-check (4.6%)')],
    [tc('Vendor revenue sum (Siemens, Hitachi, CRSC, Alstom, Wabtec, others)', { bold: true }), tc('~EUR 17B'), tc('Reported signalling revenue of the top suppliers'), fit('CHECK', K.teal), tc('Covers ~80% of the UNIFE anchor, which validates it')],
    [tc('FTA NTD communication and information capex', { bold: true }), tc('$1.9B (US)'), tc('US agency capex on radio, train control, AVL, dispatch, operations software; capex only'), fit('CHECK', K.teal), tc('US floor; NA bus bottom-up explains ~' + pct(D.bottom_up['Bottom-up as share of top-down'], 0) + ' of top-down')],
  ];
  s.addTable(td, { x: 0.45, y: 2.48, w: 12.4, colW: [2.9, 1.75, 4.1, 0.75, 2.9], rowH: [0.36, 0.56, 0.56, 0.5, 0.56, 0.5, 0.5, 0.5], border: { type: 'solid', pt: 0.75, color: 'C7D3DA' }, autoPage: false });
  source(s, 'Sources: Berg Insight (2026), Global Market Insights (2026), UNIFE (2026), SCI Verkehr (2026), company reports, FTA NTD RY2025, analysis');

  // A3 growth bridge and scenarios
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A3 GROWTH BRIDGE AND SCENARIOS', color: K.green }]);
  title(s, 'Growth Bridge: ', 'Two-thirds of the ~' + bn(total31 - total25, 0) + ' increase to 2031 is signalling; 2031 ranges from ' + bn(SC.Low.values[6], 0) + ' to ' + bn(SC.High.values[6], 0) + ' on funding and ETCS delivery', K.green);
  hbar(s, 'GROWTH BRIDGE 2025 TO 2031E, BASE CASE, BILLIONS USD', 0, 7.0, K.dgreen);
  hbar(s, 'SCENARIOS, 2031E', 7.06, CW - 7.06, K.dgreen);
  const br = D.bridge.filter(b => b.delta !== null && b.delta !== undefined);
  const brL = br.map(b => b.label.replace('Bus and tram ITS: ', 'Bus: ').replace(' (CBTC) resignalling and new lines', '').replace(' (ETCS, interlockings, PTC)', '').replace(' (PIS, CCTV/APC, condition monitoring, detection)', ''));
  s.addChart(ap.ChartType.bar, [
    { name: 'Bus and tram ITS', labels: brL, values: br.map(b => b.label.startsWith('Bus') ? +b.delta.toFixed(2) : 0) },
    { name: 'Rail signalling', labels: brL, values: br.map(b => b.label.includes('signalling') ? +b.delta.toFixed(2) : 0) },
    { name: 'Other rail ITS', labels: brL, values: br.map(b => b.label.startsWith('Other') ? +b.delta.toFixed(2) : 0) },
  ], { x: 0.35, y: 2.5, w: 6.6, h: 3.6, barDir: 'bar', barGrouping: 'clustered', barOverlapPct: 100, catAxisOrientation: 'maxMin', showValue: true, dataLabelPosition: 'outEnd', dataLabelColor: K.navy, dataLabelFontFace: HEAD, dataLabelFontBold: true, dataLabelFontSize: 12, dataLabelFormatCode: '+"$"0.0;;', showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 10, valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisLabelFontFace: BODY, catAxisLabelFontSize: 10.5, catAxisLabelColor: '1A1A1A', valAxisMinVal: 0, valAxisMaxVal: 6.0, barGapWidthPct: 35, chartColors: [K.sBus, K.sMain, K.sOther] });
  T(s, bn(total25) + ' (2025)  +  ' + bn(total31 - total25) + '  =  ' + bn(total31) + ' (2031E)', { x: 0.35, y: 6.2, w: 6.6, h: 0.35, fontFace: HEAD, fontSize: 16, bold: true, color: K.navy, align: 'center' });
  const sc = [['LOW', SC.Low, K.grey, 'US bus 2.5% (funding at extension levels, -20%); signalling -1.5pp (ETCS and CP7 slippage)'], ['BASE', SC.Base, K.green, 'Berg bus paths (NA 5.0%, Europe 5.3%); signalling between SCI 4.6% and UNIFE realised 5.7%'], ['HIGH', SC.High, K.mblue, 'US bus 8% (below the 11.5% realised 2022-25); signalling +1.5pp (FRMCS, GoA4 conversions early)']];
  sc.forEach(([lab, v, col, why], i) => {
    const sy = 2.55 + i * 1.3;
    R(s, 7.2, sy, 1.2, 1.15, col);
    T(s, lab, { x: 7.2, y: sy + 0.1, w: 1.2, h: 0.35, fontFace: HEAD, fontSize: 16, bold: true, color: 'FFFFFF', align: 'center' });
    T(s, bn(v.values[6]), { x: 7.2, y: sy + 0.45, w: 1.2, h: 0.35, fontFace: HEAD, fontSize: 18, bold: true, color: 'FFFFFF', align: 'center' });
    T(s, pct(v.cagr) + ' CAGR', { x: 7.2, y: sy + 0.8, w: 1.2, h: 0.25, fontSize: 9.5, bold: true, color: 'FFFFFF', align: 'center' });
    R(s, 8.45, sy, 4.45, 1.15, K.lgrey);
    T(s, why, { x: 8.58, y: sy, w: 4.2, h: 1.15, fontSize: 10.5, color: '1A1A1A', valign: 'middle' });
  });
  source(s, 'Note: Nominal USD at 2025 FX. Sources: Public_ITS_Market_Model.xlsx (Forecast sheet), Berg Insight, UNIFE, SCI Verkehr, FTA, analysis');

  // A4 shares and multiples
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A4 SHARES AND MULTIPLES', color: K.navy }]);
  title(s, 'Shares and Multiples: ', 'Four suppliers hold ~73% of signalling and five owners ~71% of North American bus ITS; strategics paid 0.4-1.6x revenue');
  hbar(s, 'INDICATIVE 2025 SHARE OF POOL, % OF VALUE', 0, 7.6, K.navy);
  hbar(s, 'EV / REVENUE, TRANSACTIONS AND TRADING', 7.66, CW - 7.66, K.navy);
  const shOpt = (yy, colors) => ({ x: 0.35, y: yy, w: 7.1, h: 1.55, barDir: 'bar', barGrouping: 'percentStacked', showValue: true, dataLabelPosition: 'ctr', dataLabelColor: 'FFFFFF', dataLabelFontFace: HEAD, dataLabelFontBold: true, dataLabelFontSize: 12, dataLabelFormatCode: '0%', showLegend: true, legendPos: 'b', legendFontFace: BODY, legendFontSize: 9.5, valAxisHidden: true, catAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, barGapWidthPct: 15, chartColors: colors });
  T(s, 'World passenger signalling (~' + bn(D.ccs_2025, 0) + ')', { x: 0.45, y: 2.45, w: 7, h: 0.28, fontSize: 11, bold: true, color: K.navy });
  s.addChart(ap.ChartType.bar, [['Hitachi Rail 21%', 0.21], ['Siemens Mobility 20%', 0.20], ['CRSC 19%', 0.19], ['Alstom 13%', 0.13], ['Others 27%', 0.27]].map(([n, v]) => ({ name: n, labels: ['x'], values: [v] })), shOpt(2.72, [K.navy, K.sUrban, K.sOther, K.sBus, K.mgrey]));
  T(s, 'North America bus ITS (Berg pool EUR 1.22B)', { x: 0.45, y: 4.42, w: 7, h: 0.28, fontSize: 11, bold: true, color: K.navy });
  s.addChart(ap.ChartType.bar, [['Modaxo 33%', 0.33], ['Hitachi / Clever 13%', 0.13], ['INIT 9%', 0.09], ['Cubic 9%, Luminator 7%', 0.16], ['Long tail and SaaS 29%', 0.29]].map(([n, v]) => ({ name: n, labels: ['x'], values: [v] })), shOpt(4.69, [K.navy, K.sUrban, K.sOther, K.sBus, K.mgrey]));
  s.addChart(ap.ChartType.bar, [{ name: 'EV/revenue', labels: ['Conduent transit to Modaxo (2026)', 'Thales GTS to Hitachi (2024)', 'INIT (trading)', 'Clever Devices to Hitachi (2026)', 'Iteris to Almaviva (2024)', 'Alstom Signaling NA to Knorr (2024)', 'IVU (trading)', 'Via (trading, LTM)'], values: [0.44, 1.0, 1.0, 1.6, 1.8, 2.1, 2.6, 5.6] }],
    { x: 7.75, y: 2.5, w: 5.15, h: 4.2, barDir: 'bar', catAxisOrientation: 'maxMin', showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"x"', dataLabelFontFace: HEAD, dataLabelFontBold: true, dataLabelFontSize: 12, dataLabelColor: K.navy, showLegend: false, valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisLabelFontFace: BODY, catAxisLabelFontSize: 10, catAxisLabelColor: '1A1A1A', valAxisMinVal: 0, valAxisMaxVal: 6.6, barGapWidthPct: 35, chartColors: [K.mblue] });
  source(s, 'Note: Clever Devices = $302M consideration plus $45M debt repaid on projected 2026 revenue of $220M. Sources: company reports, Hitachi Q1 FY2026 results, Companies House filings, Berg Insight, trading data as of 6 Nov 2026, analysis');

  // A5 bus unit economics and incumbency
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A5 BUS UNIT ECONOMICS AND INCUMBENCY', color: K.navy }]);
  title(s, 'Unit Economics and Incumbency: ', 'Bus platforms are replaced every ~16-19 years at ~$24K per bus; incumbents keep accounts by extension, not by winning rebids');
  hbar(s, 'INCUMBENCY, 2016-2026 DECISION POINTS', 0, 4.3, K.navy);
  hbar(s, 'PRICE POINTS FROM PUBLIC AWARDS, 2019-2026', 4.36, CW - 4.36, K.navy);
  const tiles = [['4 of 18', 'competitive rebids won by the incumbent (0 of 8 in bus CAD/AVL)'], ['~16 years', 'median tenure before an incumbent system reaches a decision point'], ['64%', 'of 39 decision points kept the incumbent, mostly via extensions or sole-source renewals']];
  tiles.forEach(([big, lab], i) => {
    const ty = 2.5 + i * 1.4;
    s.addShape('roundRect', { x: 0.4, y: ty, w: 3.75, h: 1.28, rectRadius: 0.1, fill: { color: K.paler }, line: { color: K.mblue, width: 1.25 } });
    T(s, big, { x: 0.55, y: ty + 0.1, w: 3.45, h: 0.55, fontFace: HEAD, fontSize: 30, bold: true, color: K.mblue });
    T(s, lab, { x: 0.55, y: ty + 0.66, w: 3.45, h: 0.55, fontSize: 10.5, color: '1A1A1A' });
  });
  const pc = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 9.5, color: '1A1A1A', valign: 'middle', margin: 0.05 }, o) });
  const ph2 = t => pc(t, { bold: true, color: 'FFFFFF', fill: { color: K.navy }, fontSize: 10.5 });
  const pp = [
    [ph2('Item'), ph2('Price point'), ph2('Cycle'), ph2('Examples')],
    [pc('CAD/AVL full replacement', { bold: true }), pc('$18-29K per bus (median $24K)'), pc('15-21 yrs'), pc('MARTA, TfL, TTC, CapMetro, Marin')],
    [pc('Mid-life refresh', { bold: true }), pc('$2.5-17K per bus'), pc('8-13 yrs'), pc('WMATA, SMART, OCTA')],
    [pc('Vendor maintenance and hosting', { bold: true }), pc('$1.7-3.3K per bus-year'), pc('Annual'), pc('CTA, Miami-Dade, AC Transit')],
    [pc('Overlay SaaS (real-time, analytics)', { bold: true }), pc('$0.2-2.0K per bus-year'), pc('Annual'), pc('Swiftly, Optibus')],
    [pc('Onboard video / APC', { bold: true }), pc('~$11K / ~$7.3K per bus'), pc('~10-12 yrs'), pc('CapMetro, Marin')],
    [pc('AI enforcement cameras', { bold: true }), pc('$20-30K per bus-year (citation-funded)'), pc('Service'), pc('LA Metro, AC Transit, MTA')],
    [pc('Metro CBTC resignalling', { bold: true }), pc('$4-30M per route-km (NYC $20-45M)'), pc('25-30 yrs'), pc('BART, TTC, MARTA, NYC')],
    [pc('Mainline ETCS trackside', { bold: true }), pc('EUR 0.5-0.85M per km'), pc('25-30 yrs'), pc('RFI, European Commission')],
  ];
  s.addTable(pp, { x: 4.5, y: 2.48, w: 8.4, colW: [2.55, 2.75, 1.0, 2.1], rowH: [0.34, 0.42, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4], border: { type: 'solid', pt: 0.75, color: 'C7D3DA' }, autoPage: false });
  T(s, [{ text: 'Wedge: ', options: { bold: true, color: K.mblue } }, { text: 'an incumbent platform costs a mid-size agency ~$4-4.5K per bus-year all-in, against $0.5-1.0K for an overlay SaaS', options: {} }], { x: 4.5, y: 6.42, w: 8.4, h: 0.32, fontSize: 10.5, color: '1A1A1A' });
  source(s, 'Sources: agency board records via Legistar and data.ny.gov (228 awards), TfL, European Commission, analysis');

  const out2 = path.join(__dirname, 'Public_ITS_Market_Case_Appendix.pptx');
  await ap.writeFile({ fileName: out2 });
  await applyTheme(out2, THEME);
  console.log('wrote', out2);
})();
