// Public ITS case deck, v3: the simplified case. Same house format as v2 (breadcrumb tracker,
// two-tone action titles, full-width exhibit header bars, one exhibit per slide, impact-rated
// driver and risk tables, competitive grid), with far fewer numbers.
//
// Every figure on the main slides is a formatted key of model/deck_data.json, which
// model/export_values.py writes from the workbook (sheets Market, Growth, Returns). This script
// does no arithmetic on model values beyond rounding for display and the chart-geometry scaling
// (bar lengths, label positions). The only typed figures in the whole build are the CITED block
// (appendix A2 cross-checks line and A5) and the NTD agency-tier shares read from data/, each with its source.
// Guards C01-C59 (the claims register, model/claims_register.md) stop the build if any
// model-backed wording on a slide stops being true.
//
// Writes the main deck (cover + 6 slides) and a separate appendix deck (cover + A1-A6).
// Usage:  NODE_PATH=$PWD/node_modules node build_deck_v3.js
//         DECK_DATA=<path to a deck_data.json> overrides the model export (used for guard tests);
//         DECK_OUT=<dir> writes the two decks somewhere other than this folder.
// Then:   python3 fix_paragraphs.py Public_ITS_Market_Case.pptx Public_ITS_Market_Case_Appendix.pptx
const path = require('path');
const fs = require('fs');
// company logos (deck/logos/<slug>.png, parent companies only; see logos/SOURCES.md): fit each inside a box, keeping its shape
const LOGO_DIR = path.join(__dirname, 'logos');
function pngSize(file) { const b = fs.readFileSync(file); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
function logoFit(s, slug, x, y, w, h) {
  const file = path.join(LOGO_DIR, slug + '.png');
  if (!fs.existsSync(file)) throw new Error('missing logo: ' + file);
  const { w: pw, h: ph } = pngSize(file), r = Math.min(w / pw, h / ph);
  s.addImage({ path: file, x: x + (w - pw * r) / 2, y: y + (h - ph * r) / 2, w: pw * r, h: ph * r });
}
const pptxgen = require('pptxgenjs');
const React = require('react');
const RDS = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa6');
const { applyTheme } = require('./apply_theme.js'); // writes the palette into the theme part after pptxgenjs saves

const DATA_PATH = process.env.DECK_DATA ? path.resolve(process.env.DECK_DATA) : path.join(__dirname, '..', 'model', 'deck_data.json');
const OUT_DIR = process.env.DECK_OUT ? path.resolve(process.env.DECK_OUT) : __dirname;
const D = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));

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

// ---------------------------------------------------------------- model export: presence checks
// Every key the slides read must exist and be numeric; a missing key stops the build here,
// before any formatter runs.
const SCALARS = [
  // sheet Market
  'berg_eu', 'berg_na', 'haircut', 'row_share', 'unife', 'pax_share', 'urban_share', 'gmi_apts', 'bus_hw_2025', 'ro_hw',
  'global_its_low', 'global_its_high', 'bus_eu', 'bus_na', 'bus_row', 'bus', 'urban', 'mainline', 'ro', 'market',
  'core', 'contestable', 'open', 'open_na_bus', 'open_share', 'sig_share', 'mainline_share',
  // sheet Returns
  'rev0', 'entry_mult', 'leverage', 'debt_repaid', 'growth', 'bolt_rev', 'bolt_mult', 'hold', 'exit_a_mult', 'exit_b_mult',
  'rev1', 'moic_a', 'moic_b', 'moic_a_at_a', 'moic_b_at_a', 'bm_conduent', 'bm_init', 'bm_clever', 'bm_ivu', 'bm_via',
];
const SCEN = ['cagr_low', 'cagr_base', 'cagr_high'];
const ROWS = { // sheet Growth: row key -> fields the slides read
  market_path: ['values', 'cagr', 'increase', 'low_2031', 'high_2031'],
  sig_path: ['values', 'cagr', 'increase', 'share_of_increase', 'low_2031', 'high_2031'].concat(SCEN),
  ro_path: ['values', 'cagr', 'increase'].concat(SCEN),
  bus_path: ['values', 'cagr', 'increase'],
  bus_eu_path: SCEN, bus_na_path: SCEN, bus_row_path: SCEN,
  bus_hw_path: ['values'],
  open_path: ['values', 'cagr'],
};
{
  const bad = [];
  const isNum = v => typeof v === 'number' && Number.isFinite(v);
  SCALARS.forEach(k => { if (!isNum(D[k])) bad.push(k); });
  Object.entries(ROWS).forEach(([k, fields]) => {
    if (!D[k] || typeof D[k] !== 'object') { bad.push(k); return; }
    fields.forEach(f => {
      const v = D[k][f];
      if (f === 'values' ? !(Array.isArray(v) && v.length === 7 && v.every(isNum)) : !isNum(v)) bad.push(k + '.' + f);
    });
  });
  if (!D._meta || !Array.isArray(D._meta.years) || D._meta.years.length !== 7) bad.push('_meta.years');
  if (!Array.isArray(D.checks) || !D.checks.length) bad.push('checks');
  if (bad.length) { console.error('MODEL EXPORT IS MISSING KEYS (' + DATA_PATH + ')\n  ' + bad.join('\n  ')); process.exit(1); }
}

// ---------------------------------------------------------------- formatters (no arithmetic on model values beyond rounding)
const bn0 = v => '$' + Math.round(v) + 'B';            // ~$29B
const bn1 = v => '$' + v.toFixed(1) + 'B';              // $28.6B
const n1 = v => '$' + v.toFixed(1);                     // $14.6 (table cells)
const p0 = v => Math.round(v * 100) + '%';             // ~5%
const p1 = v => (v * 100).toFixed(1) + '%';            // 5.4%
const x1 = v => v.toFixed(1) + 'x';                     // 1.6x
const eur = (v, d) => 'EUR ' + v.toFixed(d) + 'B';      // EUR 2.55B
const usd0 = v => String(Math.round(v));                // 60, 128
const Y = D._meta.years;                                // ["2025", "2026E", ..., "2031E"]
const MP = D.market_path, SP = D.sig_path, RP = D.ro_path, BP = D.bus_path, OP = D.open_path;

// ---------------------------------------------------------------- appendix-only cited figures (not model outputs)
// Each line names its source. Used on A5, in the A2 cross-checks line and in guards C39, C40, C55.
const CITED = {
  dp_extended: 21,   // research/35_gap table 2.1: 21 of the 25 retentions had no documented full rebid (15 extension, sole source, cooperative buy, renewal or modification; 6 procurement method not stated)
  dp_rebid_kept: 4,  // research/35_gap: incumbent won 4 of 18 competitive rebids
  dp_rebid_lost: 14, // research/35_gap: challenger won 14 of 18 competitive rebids
  dp_total: 39,      // research/35_gap: 39 decision points on incumbent-held ITS accounts, 2016-2026
  tenure_median: 16, tenure_n: 23, // research/35_gap takeaway 2: median tenure at decision point, n=23
  refresh_cohort: 12000, // research/31_gap takeaway 9: ~12,000 buses on 2009-16 CAD/AVL platforms (US and Canada)
  sci_vs_unife_words: 'about four-fifths', // research/21_gap: SCI ~EUR 20B vs UNIFE EUR 24.9B = 80%
  gmi_cbtc: 4.91,    // research/21_gap: GMI CBTC USD 4.91B (2025); used only in a guard
};

// NTD agency tiers (A5): rows of data/ntd_2025_bus_agency_tiers.csv whose definition starts with "A:"
// (active full-size buses, FTA NTD RY2025 Revenue Vehicle Inventory). Minimal CSV splitter that
// respects quotes, since the definition field contains commas.
function readCsv(file) {
  const split = line => {
    const out = []; let cur = '', q = false;
    for (const ch of line) {
      if (ch === '"') q = !q;
      else if (ch === ',' && !q) { out.push(cur); cur = ''; }
      else cur += ch;
    }
    out.push(cur);
    return out;
  };
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/).filter(l => l.trim());
  const head = split(lines[0]);
  return lines.slice(1).map(l => { const c = split(l), o = {}; head.forEach((h, i) => { o[h] = c[i]; }); return o; });
}
const TIER_LABEL = { '4: 1000+': '1,000+ buses', '3: 250-999': '250-999 buses', '2: 50-249': '50-249 buses', '1: 1-49': 'Under 50 buses' };
const NTD = readCsv(path.join(__dirname, '..', 'data', 'ntd_2025_bus_agency_tiers.csv'))
  .filter(r => r.definition.startsWith('A:') && TIER_LABEL[r.tier])
  .map(r => ({ tier: r.tier, agencies: +r.agencies, pct: +r.share_of_vehicles_pct }));
const tierPct = t => { const r = NTD.find(x => x.tier === t); return r ? r.pct : NaN; };

// ---------------------------------------------------------------- claims register and build guards (C01-C59)
// One entry per claim in model/claims_register.md, with the register's Slide and Wording cells verbatim
// (figures inside the quotes come from the formatters). `check` is the exact condition from the
// register; claims with check === null are cited facts (research files), listed for traceability.
const r1 = v => parseFloat(v.toFixed(1)); // the value as n1()/bn1() prints it
const CLAIMS = [
  ['C01', 'S2', '"nearly three-quarters is rail signalling"', () => D.sig_share >= 0.70 && D.sig_share < 0.75],
  ['C02', 'S2, S3 title, S3 funnel, S3 table', '"half is mainline signalling bought mainly by rail infrastructure managers" (S2, S3 title) / "Less mainline signalling: mainly rail infrastructure managers" (S3 funnel) / "Infrastructure managers (Amtrak, DB InfraGO, Network Rail, RFI)" (S3 table)', () => D.mainline_share >= 0.45 && D.mainline_share <= 0.55],
  ['C03', 'S2, S4 title, S4 strip', '"The open software and services pool outgrows the market" (S2) / "Software and services outgrow the market: ~7% a year vs ~5% overall" (S4 callout) / "the open software and services pool grows faster" (S4 title)', () => OP.cagr > MP.cagr],
  ['C04', 'S4 title, S2', '"mostly from signalling modernisation" (S4 title) / "driven mostly by the ETCS mandate and metro resignalling" (S2)', () => SP.share_of_increase > 0.5],
  ['C05', 'Q&A only (was S3 lens)', '"Europe is the largest region, with almost half of world signalling spend" (briefing answer, no longer on a slide)', () => D.bus_eu > D.bus_na && D.bus_eu > D.bus_row],
  ['C06', 'A2 open pool line', '"GMI: ' + p0(D.bus_hw_2025) + ' hardware" / "' + p0(D.ro_hw) + ' hardware, analyst" (A2: hardware is just under half of bus and other rail ITS)', () => D.bus_hw_2025 >= 0.40 && D.bus_hw_2025 < 0.50 && D.ro_hw >= 0.40 && D.ro_hw < 0.50],
  ['C07', 'S2', '"gains share from hardware" (S2)', () => D.bus_hw_path.values[6] < D.bus_hw_path.values[0]],
  ['C08', 'S4 legend and pill', '"Bus and tram ITS" / "Faster than the market, led by rest of world" (legend label and tag) / "' + p1(BP.cagr) + '" (CAGR pill)', () => BP.cagr > MP.cagr && D.bus_row_path.cagr > MP.cagr && D.bus_eu_path.cagr < D.bus_row_path.cagr && D.bus_na_path.cagr < D.bus_row_path.cagr],
  ['C09', 'S2, S4 legend and pill', '"Rail signalling" / "Just below the market" (S4 legend label and tag) / "' + p1(SP.cagr) + '" (S4 CAGR pill) / "as it excludes signalling" (S2)', () => SP.cagr < MP.cagr && MP.cagr - SP.cagr < 0.01],
  ['C10', 'S4 legend and pill', '"Other rail ITS" / "Faster than the market (condition monitoring)" (legend label and tag) / "' + p1(RP.cagr) + '" (CAGR pill)', () => RP.cagr > MP.cagr],
  ['C11', 'S4 driver 1, S2', '"EU law requires one digital signalling standard (ETCS) on main rail lines, but most are not yet fitted, leaving tens of billions of euros of work" (S4) / "the ETCS mandate" (S2)', null],
  ['C12', 'S4 driver 2', '"New York, Paris, Toronto and Hong Kong are funding metro resignalling"', null],
  ['C13', 'S4 driver 2', '"most European signalling spend goes to existing lines"', null],
  ['C14', 'S2, S4 driver 3, S7, A5', '"A large cohort of CAD/AVL platforms installed in 2009-16 at major US and Canadian agencies reaches a replace-or-extend decision by 2031" (S4) / "bus platform refresh" (S2) / "Dated refresh wave: CAD/AVL platforms installed 2009-16 at major agencies reach a replace-or-extend decision by 2031" (S7) / "Refresh wave: CAD/AVL platforms installed in 2009-16 now serve about ' + CITED.refresh_cohort.toLocaleString('en-US') + ' buses in the US and Canada" (A5)', null],
  ['C15', 'S4 driver 4', '"Most new European city buses are now electric"', null],
  ['C16', 'S4 driver 4', '"camera-based bus-lane enforcement is scaling across US cities"', null],
  ['C17', 'S2, S4, S6', '"Near-term risks: the US federal funding reset in FY2027" (S2) / "US federal transit funding may fall in FY2027 after IIJA advance appropriations lapsed" (S4) / "With IIJA advance appropriations lapsed, FY2027 federal transit funding may fall" (S6)', null],
  ['C18', 'S4 driver 5', '"the UK cut its ETCS budget"', null],
  ['C19', 'S2, S3 funnel, S3 lens, S5, S6', '"Signalling is a closed oligopoly (Siemens, Hitachi, Alstom, CRSC)" (S2) / "Less urban signalling: safety-certified, closed oligopoly" (S3 funnel) / "Software and services are open to a new entrant because transit agencies buy them from many vendors, while signalling is locked up by certified majors on multi-year frameworks" (S3 lens) / "Signalling is a closed oligopoly" (S5 title) / "together hold most of world signalling" (S6)', null],
  ['C20', 'S5', '"Together hold most of world signalling, with multi-year order books"', null],
  ['C21', 'S2, S5 title', '"North American bus ITS is consolidating around Modaxo and Hitachi"', null],
  ['C22', 'S5', '"Modaxo owns the largest North American installed base, and Hitachi is number two after buying Clever" / "Largest installed bases" (S5)', null],
  ['C23', 'S5, A4', '"INIT is the largest listed bus ITS pure play, while IVU is smaller and majority recurring" / "LISTED PURE PLAYS" (S5 column header) / "IVU\'s ~' + x1(D.bm_ivu) + ', a multiple earned by software-led, majority-recurring revenue" (A4 title)', null],
  ['C24', 'S2, S3 table, S5, S5 title, S7', '"a fragmented long tail of privately held vendors remains" / "Buy a privately held North American mid-market bus ITS vendor" (S2) / "Modaxo, Hitachi, INIT, IVU and a fragmented long tail" (S3) / "leaving a private long tail to buy" (S5 title) / "A fragmented long tail of privately held specialists"; "Sticky agency relationships"; "Mostly sub-scale, with some still founder-led (GIRO, ETA), so succession is open"; "ACQUISITION TARGETS: Buy one as the platform, then bolt on others"; "Where to focus: buy a mid-market private, add SaaS / AI, and exit at a software multiple" (S5 focus callout) / "Acquire a privately held North American mid-market bus ITS vendor" (S7)', null],
  ['C25', 'S2, S5', '"cloud challengers overlay legacy systems" (S2) / "LA Metro and many other US agencies already run cloud overlays on legacy CAD/AVL" (S5)', null],
  ['C26', 'S2, S3 table, S5, S6', '"protected by safety certification and long maintenance tails" (S2) / "Signalling majors under multi-year frameworks" (S3 table) / "long maintenance tails, multi-year frameworks (e.g., DB)"; "Full stack (CAD/AVL, scheduling, fare) plus long-term service contracts" (S5) / "long frameworks protect the signalling majors" (S6)', null],
  ['C27', 'S5', '"each kept for a system generation"', null],
  ['C28', 'S5', '"Modaxo buys and never sells"', null],
  ['C29', 'S5', '"Avail and Passio lead real-time feeds at smaller US agencies"', null],
  ['C30', 'S5', '"Sold beside the incumbent on short contracts" / "AI enforcement can be funded from fines"', null],
  ['C31', 'S5, S6', '"Slow, publicly funded ETCS rollout and execution risk", "Hardware and project mix squeezes margins" (S5) / "Alstom and INIT cut profit guidance" (S6)', null],
  ['C32', 'S5, A5', '"legacy installs exposed at rebid" (S5) / "In bus CAD/AVL, incumbents lost every competitive rebid in the sample, but every winner was an established vendor (Clever, INIT, Equans, Vontas)" (A5)', null],
  ['C33', 'S2, S5, S6, S7', '"not a highly levered buyout of a hardware integrator" (S2 verdict) / "Cubic also competes" (A6 group label) / "Cubic\'s highly levered buyout is now distressed"; "Project-heavy integrators do not support high buyout leverage" (S6) / "Avoid: signalling cores and highly levered buyouts of hardware integrators" (S7)', () => D.leverage <= 3],
  ['C34', 'S5', '"Via and Optibus still report losses"', null],
  ['C35', 'S5, S7', '"subscriptions fit federal capital grants poorly" (S5) / "Structure subscriptions to fit federal capital-grant rules" (S7)', null],
  ['C36', 'S5', '"EXIT BENCHMARK: Value the exit off INIT and IVU: valuations rise with recurring mix" (S5 focus callout)', () => D.bm_init < D.bm_ivu],
  ['C37', 'S5', '"scaled players are priced as SaaS"', () => D.bm_via > 2 * D.bm_ivu],
  ['C38', 'S2, S6 title, S6, A5', '"installed systems are rarely rebid" (S2) / "Long system lives and slow procurement favour buying an installed base" (S6 title) / "Installed systems are rarely rebid, typically only after well over a decade"; "Only a small slice of the installed base is rebid each year" (S6) / "Systems are ~' + CITED.tenure_median + ' years old at a decision point" (A5 title)', null],
  ['C39', 'S2, S6, A5', '"challengers usually win when they are" (rebid; S2) / "Challengers usually win when a competitive rebid happens" (S6) / "challengers win most competitive rebids" (A5 title) / "Competitive rebids: challengers won most" (A5 bracket)', () => CITED.dp_rebid_lost > CITED.dp_rebid_kept],
  ['C40', 'S6, A5', '"Most renewals skip a competitive rebid" (S6) / "Kept without a documented rebid" (A5 bar, ' + CITED.dp_extended + ')', () => CITED.dp_extended > CITED.dp_rebid_kept],
  ['C41', 'S6', '"Multi-year award-to-go-live, bid protests" / "Long sales cycles favour vendors with reference fleets and live pilots"', null],
  ['C42', 'S6', '"Buy America documentation for hardware"', null],
  ['C43', 'S6', '"Software-led entry and cooperative purchasing (NASPO, Sourcewell) shorten the path"', null],
  ['C44', 'S6', '"Formula funds for system refresh are the most durable federal line"', null],
  ['C45', 'S6', '"Agencies in PA, WA and OR, where state rescue funding stalled, may defer purchases"', null],
  ['C46', 'S2, S4, S5, S6', '"ETCS slippage in Europe" (S2) / "Headwind: funding reset, ETCS slippage" (S4) / "Slow, publicly funded ETCS rollout" (S5) / "EU ETCS rollout is behind schedule" (S6)', null],
  ['C47', 'S7, A5', '"mid-size agencies run over half the US fleet" (S7, A5 title) / "Open mid-size tier and available targets" (S7) / "Mid-size (50-999 buses): over half the fleet and the core customers" (A5)', () => tierPct('2: 50-249') + tierPct('3: 250-999') > 50],
  ['C48', 'S2 title, S7', '"best entered via buy-and-build in North America" (S2 title) / "the most actionable slice of the open pool"; "national procurement regimes split Europe\'s larger pool, limiting cross-border synergies" (S7)', () => D.bus_eu > D.bus_na],
  ['C49', 'S2, S7, A4', '"the ~' + x1(D.exit_a_mult) + ' Hitachi paid for Clever barely returns capital" (S2) / "At the Clever precedent the platform barely returns its capital" (S7) / "The Clever precedent (~' + x1(D.bm_clever) + ' revenue) barely returns capital" (A4 title)', () => D.moic_a >= 1.0 && D.moic_a < 1.3],
  ['C50', 'S7', '"An IVU-like, majority-recurring mix roughly doubles the equity invested"', () => D.moic_b >= 1.85 && D.moic_b <= 2.2],
  ['C51', 'S2, S7, S7 title, A4', '"below a software multiple" (S2, S7) / "well above the ~' + x1(D.exit_a_mult) + ' paid for Clever" (S7 title) / "entry between the INIT and IVU multiples" (S7 note) / "Entry: between INIT and IVU, below IVU\'s software multiple" (A4)', () => D.bm_init <= D.entry_mult && D.entry_mult < D.bm_ivu && D.exit_b_mult >= 1.5 * D.exit_a_mult],
  ['C52', 'S5, S7', '"The consolidators bid against us for targets, and Hitachi may buy at exit while Modaxo sets the floor" (S5 context callout) / "Likely exit buyers are Hitachi, Siemens and Via, while Modaxo sets the floor price" (S7)', () => D.bm_conduent < Math.min(D.bm_init, D.bm_clever, D.bm_ivu, D.bm_via)],
  ['C53', 'A3 title, S4 legend', '"Two-thirds of the increase to 2031 is signalling" / "2031 ranges from ~' + bn0(MP.low_2031) + ' to ~' + bn0(MP.high_2031) + ', mostly on the pace of signalling modernisation" (A3 title) / "Just below the market, but its pace is the swing factor" (S4 rail signalling legend)', () => SP.share_of_increase >= 0.62 && SP.share_of_increase <= 0.70 && SP.high_2031 - SP.low_2031 > 0.5 * (MP.high_2031 - MP.low_2031)],
  ['C54', 'A2 cross-checks line', '"SCI Verkehr\'s independent signalling estimate is about four-fifths of UNIFE\'s"', null],
  ['C55', 'A2 cross-checks line', '"GMI\'s CBTC-only market sits below our urban signalling, which also covers light rail"', () => D.urban > CITED.gmi_cbtc],
  ['C56', 'A4', '"half repaid by exit"', () => D.debt_repaid === 0.5],
  ['C57', 'S3', 'Rounding integrity: the S3 segment cells must add up to the total, and the open column ($2.5 + $1.7) to the funnel\'s open pool ($4.2), as printed', () => Math.abs(r1(D.mainline) + r1(D.urban) + r1(D.bus) + r1(D.ro) - r1(D.market)) < 0.051 && Math.abs(r1(D.open_bus) + r1(D.open_ro) - r1(D.open)) < 0.051 && Math.abs(r1(D.bus) + r1(D.ro) - r1(D.contestable)) < 0.051],
  ['C58', 'A2 bottom-up line', '"buses and vehicles \u00D7 price per unit across 11 spending pools gives ' + bn1(D.bu_total / 1000) + ' for North American bus ITS, ' + p0(D.bu_ratio) + ' of the top-down ' + bn1(D.bu_topdown / 1000) + '"', () => D.bu_ratio > 0.75 && D.bu_ratio < 1.25],
  ['C59', 'A6', 'Player directory: each parent, its subsidiaries and brands, and its owner, as listed on A6', null],
];
const failures = [];
function guard(id, cond, detail) { if (!cond) failures.push(id + ': ' + detail); }
CLAIMS.forEach(([id, slide, wording, check]) => {
  if (!check) return;
  let ok = false;
  try { ok = !!check(); } catch (e) { ok = false; }
  guard(id, ok, '"' + wording + '" (' + slide + ') is no longer supported by the model export');
});
// Model integrity: every "Check:" row of the workbook must be 0.
D.checks.forEach(c => guard('MODEL', typeof c.value === 'number' && Math.abs(c.value) <= 1e-9, c.sheet + '!' + c.cell + ' ' + c.label + ' = ' + c.value));
// The NTD tier file must give all four tiers.
guard('NTD', NTD.length === 4 && NTD.every(r => Number.isFinite(r.pct)), 'data/ntd_2025_bus_agency_tiers.csv must hold four definition-A tiers');
if (CLAIMS.length !== 59 || CLAIMS.some(([id], i) => id !== 'C' + String(i + 1).padStart(2, '0'))) failures.push('REGISTER: claims must run C01-C59 in order');
if (failures.length) { console.error('GUARD FAILURES (' + DATA_PATH + ')\n' + failures.join('\n')); process.exit(1); }
console.log('guards: ' + CLAIMS.length + ' claims registered, ' + CLAIMS.filter(c => c[3]).length + ' model or data guards checked, ' + D.checks.length + ' model checks at 0; all pass');

// ---------------------------------------------------------------- icons
async function iconData(name, color = '#FFFFFF') {
  const C = fa[name] || fa.FaCircle;
  const svg = RDS.renderToStaticMarkup(React.createElement(C, { color, size: 256 }));
  const png = await sharp(Buffer.from(svg)).resize(256, 256, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toBuffer();
  return 'image/png;base64,' + png.toString('base64');
}

// ---------------------------------------------------------------- deck scaffolding
// Page number box. The main deck uses the master slide number; the appendix deck prints its own
// page codes (A1-A6) in the same place, so its pages match the A-codes the main deck cross-refers to.
const SLIDE_NO = { x: 12.35, y: 7.02, w: 0.55, h: 0.3, fontFace: BODY, fontSize: 11, bold: true, color: '000000', align: 'right' };
const pageCode = (s, code) => s.addText(code, Object.assign({}, SLIDE_NO, { isTextBox: true, margin: [7.2, 7.2, 3.6, 3.6], valign: 'top' }));
function newDeck(title, numbered = true) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.theme = { headFontFace: HEAD, bodyFontFace: BODY };
  pres.author = 'Matthew Kang';
  pres.company = '';
  pres.subject = title;
  pres.title = title;
  pres.defineSlideMaster({
    title: 'CONTENT', background: { color: 'FFFFFF' },
    objects: [
      { rect: { x: CW, y: 0, w: 13.333 - CW, h: 7.5, fill: { color: K.navy }, line: { color: K.navy } } },
      { rect: { x: 9.9, y: 0.14, w: 2.95, h: 0.34, fill: { color: 'FFFFFF' }, line: { color: K.red, width: 1.25 } } },
      { text: { text: 'PRELIMINARY: FOR DISCUSSION', options: { x: 9.9, y: 0.14, w: 2.95, h: 0.34, fontFace: BODY, fontSize: 11, bold: true, color: K.red, align: 'center', valign: 'middle', margin: 0 } } },
      { text: { text: 'PUBLIC ITS MARKET CASE', options: { x: 0.4, y: 6.9, w: 2.2, h: 0.28, fontFace: HEAD, fontSize: 13, bold: true, color: K.navy, margin: 0 } } },
      { text: { text: 'Matthew Kang  |  November 2026', options: { x: 0.4, y: 7.16, w: 2.2, h: 0.2, fontFace: BODY, fontSize: 8, color: K.grey, margin: 0 } } },
      { text: { text: 'DISCUSSION DRAFT', options: { x: 10.25, y: 6.98, w: 2.0, h: 0.36, fontFace: HEAD, fontSize: 16, bold: true, color: K.red, align: 'right', margin: 0 } } },
      { placeholder: { options: { name: 'title', type: 'title', x: 0.45, y: 0.6, w: 12.4, h: 1.15, fontFace: HEAD, fontSize: 26, bold: true, color: K.navy, valign: 'top', align: 'left', margin: 0 }, text: '' } },
      { placeholder: { options: { name: 'source', type: 'body', x: 2.7, y: 6.84, w: 7.45, h: 0.56, fontFace: BODY, fontSize: 8, color: '333333', valign: 'bottom', align: 'left', margin: 0 }, text: '' } },
    ],
    ...(numbered ? { slideNumber: SLIDE_NO } : {}),
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
// simple bracket: a horizontal rule with end ticks pointing down (over a bar) or a vertical rule
// with end ticks pointing left (beside bars)
function bracketH(s, x0, x1, y, tick, color) {
  const ln = { color, width: 1.25 };
  s.addShape('line', { x: x0, y, w: x1 - x0, h: 0, line: ln });
  s.addShape('line', { x: x0, y, w: 0, h: tick, line: ln });
  s.addShape('line', { x: x1, y, w: 0, h: tick, line: ln });
}
function bracketV(s, x, y0, y1, tick, color) {
  const ln = { color, width: 1.25 };
  s.addShape('line', { x, y: y0, w: 0, h: y1 - y0, line: ln });
  s.addShape('line', { x: x - tick, y: y0, w: tick, h: 0, line: ln });
  s.addShape('line', { x: x - tick, y: y1, w: tick, h: 0, line: ln });
}

(async () => {
  const ic = {};
  for (const n of ['FaChartPie', 'FaArrowTrendUp', 'FaChessKnight', 'FaTriangleExclamation', 'FaBullseye', 'FaTrainSubway', 'FaTrain', 'FaBus', 'FaChargingStation', 'FaLandmark', 'FaHourglassHalf', 'FaFileContract', 'FaShieldHalved', 'FaArrowTrendDown', 'FaMapLocationDot', 'FaPuzzlePiece', 'FaHandHoldingDollar']) ic[n] = await iconData(n);

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

  // ---------------------------------------------------------------- S2 executive summary (7 numbers)
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'EXECUTIVE SUMMARY', color: K.lblue }]);
  title(s, 'Executive Summary: ', 'A ~' + bn0(D.market) + ' market growing ~' + p0(MP.cagr) + ' a year, with a ~' + bn0(D.open) + ' software and services pool best entered via buy-and-build in North America');
  R(s, 0.45, 1.9, 12.4, 0.42, K.navy);
  T(s, 'TOPIC', { x: 0.6, y: 1.9, w: 2.5, h: 0.42, fontSize: 12.5, bold: true, color: 'FFFFFF', valign: 'middle' });
  T(s, 'KEY FINDINGS', { x: 3.45, y: 1.9, w: 9, h: 0.42, fontSize: 12.5, bold: true, color: 'FFFFFF', valign: 'middle' });
  const ex = [
    ['FaChartPie', 'MARKET SIZE AND SEGMENTATION', [
      [['Public ITS for bus and passenger rail is ~' + bn0(D.market) + ' (2025, ex-fare), ', true], ['but nearly three-quarters is rail signalling and half is mainline signalling bought mainly by rail infrastructure managers']],
      [['Only ~' + bn0(D.open) + ' is open to an asset-light entrant: ', true], ['software and services in bus and other rail ITS']]]],
    ['FaArrowTrendUp', 'GROWTH TO 2031', [
      [['~' + p0(MP.cagr) + ' a year to ~' + bn0(MP.values[6]) + ' by 2031, ', true], ['driven mostly by the ETCS mandate and metro resignalling, plus bus platform refresh']],
      [['The open software and services pool outgrows the market at ~' + p0(OP.cagr) + ' a year, ', true], ['as it excludes signalling and gains share from hardware']]]],
    ['FaChessKnight', 'COMPETITIVE DYNAMICS', [
      [['Signalling is a closed oligopoly ', true], ['(Siemens, Hitachi, Alstom, CRSC) protected by safety certification and long maintenance tails']],
      [['North American bus ITS is consolidating around Modaxo and Hitachi, ', true], ['but cloud challengers overlay legacy systems, and a fragmented long tail of privately held vendors remains']]]],
    ['FaTriangleExclamation', 'RISKS AND BARRIERS', [
      [['The barrier is tenure, not rebid odds: ', true], ['installed systems are rarely rebid, but challengers usually win when they are']],
      [['Near-term risks: ', true], ['the US federal funding reset in FY2027 and ETCS slippage in Europe']]]],
    ['FaBullseye', 'INVESTMENT THESIS', [
      [['Buy a privately held North American mid-market bus ITS vendor below a software multiple, ', true], ['move it to cloud and add AI enforcement and zero-emission modules']],
      [['Returns hinge on a software exit multiple ', true], ['(~' + x1(D.exit_b_mult) + ' revenue, like IVU), while the ~' + x1(D.exit_a_mult) + ' Hitachi paid for Clever barely returns capital']]]],
  ];
  let y = 2.36;
  const rhs = [0.84, 0.74, 0.84, 0.74, 0.84]; // per-row heights: three-line rows and two-line rows (growth, risks)
  ex.forEach(([icn, lab, bl], i) => {
    const rh = rhs[i];
    R(s, 0.45, y, 2.75, rh - 0.04, '1E9FE0');
    iconTile(s, ic[icn], 0.58, y + rh / 2 - 0.25, 0.46, '1E9FE0');
    s.addShape('roundRect', { x: 0.58, y: y + rh / 2 - 0.25, w: 0.46, h: 0.46, rectRadius: 0.06, fill: { type: 'none' }, line: { color: 'FFFFFF', width: 1.25 } });
    T(s, lab, { x: 1.14, y, w: 2.0, h: rh - 0.04, fontFace: HEAD, fontSize: 14, bold: true, color: 'FFFFFF', valign: 'middle' });
    T(s, paras(bl, { paraSpaceAfter: 3 }), { x: 3.4, y: y + 0.02, w: 9.4, h: rh - 0.06, fontSize: 11, color: '1A1A1A', valign: 'middle' });
    if (i < ex.length - 1) s.addShape('line', { x: 0.45, y: y + rh - 0.02, w: 12.4, h: 0, line: { color: K.navy, width: 1.25, dashType: 'sysDot' } });
    y += rh;
  });
  s.addShape('roundRect', { x: 0.45, y: 6.4, w: 12.4, h: 0.42, rectRadius: 0.21, fill: { color: K.navy }, line: { color: K.navy } });
  T(s, [{ text: 'Verdict: ', options: { bold: true, color: K.lblue } }, { text: 'attractive only as a software-led buy-and-build in bus ITS, not a highly levered buyout of a hardware integrator, and not in rail signalling', options: { color: 'FFFFFF' } }], { x: 0.7, y: 6.4, w: 11.9, h: 0.42, fontSize: 12, valign: 'middle', align: 'center' });
  source(s, 'Model: sheets Market, Growth and Returns. Sources: Berg Insight (2026), UNIFE World Rail Market Study 2026, SCI Verkehr (2026), Global Market Insights (2026), Hitachi Q1 FY2026 results, IVU trading data as of 6 Nov 2026, agency award records, analysis');

  // ---------------------------------------------------------------- S3 market size: funnel + who-buys table (10 numbers)
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'MARKET SIZE AND SEGMENTATION', color: K.lblue }, { text: 'ADDRESSABLE MARKET', color: K.navy }]);
  title(s, 'Market Size: ', 'A ~' + bn0(D.market) + ' market, but half is mainline signalling bought mainly by rail infrastructure managers, and only ~' + bn0(D.open) + ' of software and services is open to entrants');
  hbar(s, 'EST. ADDRESSABLE MARKET FUNNEL, 2025, BILLIONS USD', 0, 6.45, K.navy);
  hbar(s, 'WHO BUYS EACH SEGMENT, AND CAN AN ENTRANT COMPETE?', 6.51, CW - 6.51, K.navy);
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
    ['$' + usd0(D.global_its_low) + '-' + usd0(D.global_its_high) + 'B', 'Global ITS market', 'Umbrella reports add road traffic, tolling and aviation'],
    [bn1(D.market), 'Public ITS: bus + passenger rail', 'Case scope: hardware, software and services, ex-fare'],
    [bn1(D.core), 'Transit-operator core', 'Less mainline signalling: mainly rail infrastructure managers'],
    [bn1(D.contestable), 'Contestable pool', 'Less urban signalling: safety-certified, closed oligopoly'],
    [bn1(D.open), 'Open software and services', 'Less bus and rail hardware: the asset-light entry point'],
  ];
  levels.forEach(([v, lab, desc], k) => {
    const lx = cx + wAt(k) / 2 + 0.14, ly = fy0 + k * fh - 0.17;
    T(s, v, { x: lx, y: ly, w: 6.3 - lx, h: 0.32, fontFace: HEAD, fontSize: 21, bold: true, color: K.mblue });
    T(s, lab, { x: lx, y: ly + 0.3, w: 6.35 - lx, h: 0.2, fontSize: 11, bold: true, color: K.navy });
    T(s, desc, { x: lx, y: ly + 0.48, w: 6.42 - lx, h: 0.28, fontSize: 8.5, italic: true, color: '333333' });
  });
  s.addShape('ellipse', { x: 0.15, y: 5.45, w: 1.28, h: 1.28, fill: { color: 'FFFFFF' }, line: { color: K.black, width: 1.5 } });
  T(s, '~' + p0(D.open_share), { x: 0.15, y: 5.58, w: 1.28, h: 0.36, fontFace: HEAD, fontSize: 21, bold: true, color: K.mblue, align: 'center' });
  T(s, 'OF CASE SCOPE OPEN TO A NEW ENTRANT', { x: 0.25, y: 5.93, w: 1.08, h: 0.6, fontFace: HEAD, fontSize: 10, bold: true, color: K.black, align: 'center' });
  s.addShape('line', { x: 1.43, y: 6.2, w: cx - fBot / 2 - 1.43 + 0.15, h: 0, line: { color: K.black, width: 1.25, endArrowType: 'triangle' } });
  // who buys each segment
  const hc = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 9.5, color: '1A1A1A', valign: 'middle', align: 'left', margin: [0.03, 0.05, 0.03, 0.05] }, o) });
  const hh = t => hc(t, { bold: true, color: 'FFFFFF', fill: { color: K.navy }, fontSize: 10, align: 'center' });
  // open column: NO for signalling, else the segment's software and services in $B, so the column sums to the funnel's open pool
  const open = t => t === 'NO'
    ? hc(t, { bold: true, color: 'FFFFFF', fill: { color: K.grey }, fontSize: 9, align: 'center' })
    : { text: [{ text: n1(t), options: { fontSize: 11.5, bold: true, breakLine: true } }, { text: 'software + services', options: { fontSize: 8, bold: true } }], options: { fontFace: BODY, color: 'FFFFFF', fill: { color: K.green }, align: 'center', valign: 'middle', margin: [0.03, 0.04, 0.03, 0.04] } };
  const segRow = (lab, v, buyers, supply, o) => [hc(lab, { bold: true, color: K.navy, fontSize: 10 }), hc(n1(v), { bold: true, align: 'center', fontSize: 10.5 }), hc(buyers), hc(supply), open(o)];
  const sRows = [
    [hh('Segment'), hh('2025, $B'), hh('Main buyers'), hh('Supply side'), hh('Open to an entrant, $B')],
    segRow('Mainline and commuter signalling', D.mainline, 'Infrastructure managers (Amtrak, DB InfraGO, Network Rail, RFI)', 'Signalling majors under multi-year frameworks', 'NO'),
    segRow('Urban signalling (metro, light rail)', D.urban, 'Metro and light rail agencies', 'Signalling majors with safety-certified systems', 'NO'),
    segRow('Bus and tram ITS', D.bus, 'Transit agencies and bus operators', 'Modaxo, Hitachi, INIT, IVU and a fragmented long tail', D.open_bus),
    segRow('Other rail ITS (passenger info, CCTV, monitoring)', D.ro, 'Rail and metro operators', 'Rolling-stock suppliers and specialists', D.open_ro),
    [hc('Total', { bold: true, color: K.navy, fill: { color: K.lgrey }, fontSize: 10 }), hc(n1(D.market), { bold: true, align: 'center', fill: { color: K.navy }, color: 'FFFFFF', fontSize: 10.5 }), hc('', { fill: { color: K.lgrey } }), hc('', { fill: { color: K.lgrey } }), hc(n1(D.open), { bold: true, align: 'center', fill: { color: K.green }, color: 'FFFFFF', fontSize: 11 })],
  ];
  s.addTable(sRows, { x: 6.68, y: 2.5, w: 6.2, colW: [1.55, 0.57, 1.6, 1.5, 0.98], rowH: [0.4, 0.66, 0.5, 0.5, 0.66, 0.36], fontFace: BODY, border: { type: 'solid', pt: 0.75, color: 'FFFFFF' }, autoPage: false });
  s.addShape('roundRect', { x: 6.68, y: 5.78, w: 6.2, h: 0.92, rectRadius: 0.1, fill: { color: K.paler }, line: { color: K.mblue, width: 1.25 } });
  // one line that sums up the table (guards C19, C26)
  T(s, paras([
    [['Software and services are open to a new entrant ', true, K.mblue], ['because transit agencies buy them from many vendors, while signalling is locked up by certified majors on multi-year frameworks']],
  ]), { x: 6.85, y: 5.82, w: 5.9, h: 0.86, fontSize: 11.5, color: '1A1A1A', valign: 'middle' });
  source(s, 'Note: 2025, nominal USD at 2025 average FX, excluding fare collection. Figures may not sum due to rounding. Sizing chain in appendix A2. Model: sheet Market. Sources: Berg Insight (2026), UNIFE World Rail Market Study 2026, SCI Verkehr (2026), Global Market Insights (2026), umbrella ITS reports (MarketsandMarkets, Grand View Research, Precedence Research, Mordor Intelligence), analysis');

  // ---------------------------------------------------------------- S4 growth to 2031 + drivers (6 numbers)
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'MARKET GROWTH', color: K.lblue }, { text: 'GROWTH DRIVERS TO 2031', color: K.green }]);
  title(s, 'Market Growth: ', 'Public ITS grows ~' + p0(MP.cagr) + ' a year to ~' + bn0(MP.values[6]) + ' by 2031, mostly from signalling modernisation, while the open software and services pool grows faster, at ~' + p0(OP.cagr), K.green);
  hbar(s, 'PUBLIC ITS MARKET BY SEGMENT, GLOBAL, 2025-2031E, BILLIONS USD', 0, 8.15, K.dgreen);
  hbar(s, 'KEY GROWTH DRIVERS AND HEADWINDS', 8.21, CW - 8.21, K.dgreen);
  // bottom to top: signalling, other rail, bus
  const ser = [['Rail signalling', SP.values, K.sMain], ['Other rail ITS', RP.values, K.sOther], ['Bus and tram ITS', BP.values, K.sBus]];
  const ch = { x: 1.95, y: 2.5, w: 5.3, h: 3.35 }, lay = { x: 0.02, y: 0.13, w: 0.96, h: 0.87 }, vmax = 46;
  s.addChart(pres.ChartType.bar, ser.map(([n, v]) => ({ name: n, labels: Y, values: v })), {
    x: ch.x, y: ch.y, w: ch.w, h: ch.h, barDir: 'col', barGrouping: 'stacked', barGapWidthPct: 40, layout: lay,
    catAxisHidden: true, valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: vmax, valGridLine: { style: 'none' }, catGridLine: { style: 'none' },
    showLegend: false,
    // each segment's value inside its bar, white, whole billions ($21B)
    showValue: true, dataLabelPosition: 'ctr', dataLabelColor: 'FFFFFF', dataLabelFontSize: 9, dataLabelFontBold: true, dataLabelFormatCode: '"$"0"B"',
    chartColors: ser.map(x => x[2]), plotArea: { fill: { color: 'FFFFFF' } },
  });
  // chart geometry: plot-area position of each year band and of a value on the axis
  const px = ch.x + lay.x * ch.w, pw = lay.w * ch.w, py = ch.y + lay.y * ch.h, ph = lay.h * ch.h, band = pw / 7;
  const yv = v => py + ph * (1 - v / vmax);
  // market total above every year: 2025 and 2031E larger, the years between smaller
  MP.values.forEach((v, i) => { const end = i === 0 || i === 6; T(s, bn1(v), { x: px + band * i - 0.1, y: yv(v) - (end ? 0.32 : 0.28), w: band + 0.2, h: end ? 0.3 : 0.26, fontFace: HEAD, fontSize: end ? 15 : 12.5, bold: true, color: K.navy, align: 'center', valign: 'bottom' }); });
  const yb = py + ph + 0.03;
  R(s, px, yb, pw, 0.28, K.black);
  Y.forEach((t, i) => T(s, t, { x: px + band * i, y: yb, w: band, h: 0.28, fontSize: 11, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' }));
  R(s, px, yb + 0.28, pw, 0.32, 'E9EEF3', K.black);
  [0, 6].forEach(i => T(s, bn1(OP.values[i]), { x: px + band * i, y: yb + 0.28, w: band, h: 0.32, fontSize: 11, bold: true, color: K.navy, align: 'center', valign: 'middle' }));
  s.addShape('line', { x: px + band + 0.08, y: yb + 0.44, w: band * 5 - 0.16, h: 0, line: { color: K.navy, width: 1.5, endArrowType: 'triangle' } });
  s.addShape('roundRect', { x: 0.25, y: yb + 0.29, w: 1.7, h: 0.3, rectRadius: 0.06, fill: { color: K.green }, line: { color: K.green } });
  T(s, 'Software and services', { x: 0.27, y: yb + 0.29, w: 1.66, h: 0.3, fontSize: 9.5, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
  // callout above the shorter early bars: the open pool outgrows the market (guard C03)
  T(s, [{ text: 'Software and services outgrow the market: ', options: { bold: true } }, { text: '~' + p0(OP.cagr) + ' a year vs ~' + p0(MP.cagr) + ' overall' }], { x: px + 0.04, y: 2.45, w: band * 5 - 0.08, h: 0.52, fontSize: 11, color: 'FFFFFF', fill: { color: K.green }, valign: 'middle', margin: 0.08 });
  // CAGR pills: market at the 2031E total, open pool on its strip
  T(s, '2025-31E CAGR:', { x: 7.3, y: 2.45, w: 0.85, h: 0.3, fontFace: HEAD, fontSize: 11, bold: true, color: K.navy, align: 'center', valign: 'bottom' });
  pill(s, 7.33, yv(MP.values[6]) - 0.3, 0.8, 0.28, p1(MP.cagr), { line: K.black, size: 12 });
  pill(s, 7.33, yb + 0.3, 0.8, 0.28, p1(OP.cagr), { line: K.navy, size: 12 });
  s.addShape('ellipse', { x: 7.2, y: yb + 0.2, w: 1.06, h: 0.48, fill: { type: 'none' }, line: { color: K.green, width: 2.5 } });
  // legend, top series first; the segment CAGRs sit in pills on the 2031E bar (guards C08-C10)
  const leg = [
    ['Bus and tram ITS', K.navy, K.sBus, 'Faster than the market, led by rest of world'],
    ['Other rail ITS', K.navy, K.sOther, 'Faster than the market (condition monitoring)'],
    ['Rail signalling', K.navy, K.sMain, 'Just below the market, but its pace is the swing factor'],
  ];
  const legY = [3.05, 3.95, 4.85];
  leg.forEach(([n, tc, lc, tag], k) => {
    const ly = legY[k];
    T(s, n, { x: 0.3, y: ly - 0.02, w: 1.6, h: 0.42, fontSize: 10.5, bold: true, color: tc, valign: 'bottom' });
    s.addShape('line', { x: 0.3, y: ly + 0.44, w: 1.6, h: 0, line: { color: lc, width: 3 } });
    T(s, tag, { x: 0.3, y: ly + 0.49, w: 1.6, h: 0.4, fontSize: 8.5, italic: true, color: K.grey });
  });
  // segment CAGR pills beside each segment of the 2031E bar, tied to it by a short leader (guards C08-C10)
  const s31 = SP.values[6], r31 = RP.values[6], bar = band / 1.4, barR = px + band * 6 + band / 2 + bar / 2 + 0.03;
  [[BP.cagr, yv(MP.values[6]), yv(s31 + r31), K.sBus, '1B8CC4'], [RP.cagr, yv(s31 + r31), yv(s31), K.sOther, K.sOther], [SP.cagr, yv(s31), yv(0), K.sMain, K.sMain]].forEach(([c, ya, yz, lc, tc]) => {
    const m = (ya + yz) / 2;
    s.addShape('line', { x: barR, y: m, w: 7.33 - barR, h: 0, line: { color: lc, width: 1 } });
    pill(s, 7.33, m - 0.13, 0.8, 0.26, p1(c), { line: lc, size: 11, color: tc });
  });
  // drivers panel
  const drv = [
    ['FaTrainSubway', 'Tailwind: EU train-control mandate (ETCS)', 'EU law requires one digital signalling standard (ETCS) on main rail lines, but most are not yet fitted, leaving tens of billions of euros of work', '\u25B2 HIGH', K.green],
    ['FaTrain', 'Tailwind: Metro resignalling (CBTC)', 'New York, Paris, Toronto and Hong Kong are funding metro resignalling, and most European signalling spend goes to existing lines', '\u25B2 HIGH', K.green],
    ['FaBus', 'Tailwind: Bus platform refresh cycle', 'A large cohort of CAD/AVL platforms installed in 2009-16 at major US and Canadian agencies reaches a replace-or-extend decision by 2031', '\u25B2 HIGH', K.green],
    ['FaChargingStation', 'Tailwind: Electric buses, AI enforcement', 'Most new European city buses are now electric, and camera-based bus-lane enforcement is scaling across US cities', '\u25B2 MID', K.green],
    ['FaLandmark', 'Headwind: funding reset, ETCS slippage', 'US federal transit funding may fall in FY2027 after IIJA advance appropriations lapsed, and the UK cut its ETCS budget', '\u25BC MID', K.red],
  ];
  drv.forEach(([icn, h, st, lvl, col], i) => {
    const ry = 2.5 + i * 0.83;
    iconTile(s, ic[icn], 8.35, ry + 0.06, 0.62, i === 4 ? K.grey : K.green);
    T(s, h, { x: 9.1, y: ry + 0.01, w: 3.0, h: 0.24, fontSize: 10.5, bold: true, color: K.navy, valign: 'top' });
    T(s, st, { x: 9.1, y: ry + 0.25, w: 3.0, h: 0.52, fontSize: 9.5, color: '1A1A1A', valign: 'top' });
    R(s, 12.16, ry + 0.12, 0.74, 0.5, col);
    T(s, lvl, { x: 12.16, y: ry + 0.12, w: 0.74, h: 0.5, fontFace: HEAD, fontSize: 15, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
    if (i < drv.length - 1) s.addShape('line', { x: 8.35, y: ry + 0.79, w: 4.55, h: 0, line: { color: K.mgrey, width: 0.75 } });
  });
  T(s, '\u25B2 raises and \u25BC lowers 2025-31 growth. HIGH or MID is the size of the effect on its segment', { x: 8.35, y: 6.64, w: 4.55, h: 0.18, fontSize: 7.5, italic: true, color: K.grey, align: 'right' });
  source(s, 'Note: Base case, nominal USD at constant 2025 FX. Low and high cases in appendix A3. Model: sheet Growth. Sources: European Commission ERTMS Work Plan (2026), MTA 2025-29 Capital Program, MTR, Sustainable Bus (DVV Media), FTA, H.R. 8870, Network Rail CP7, Berg Insight (2026), UNIFE World Rail Market Study 2026, SCI Verkehr (2023, 2026), Global Market Insights (2026), analysis');

  // ---------------------------------------------------------------- S5 competitive landscape grid (0 numbers)
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'COMPETITIVE LANDSCAPE', color: K.lblue }, { text: 'PLAYER GROUPS', color: K.navy }]);
  title(s, 'Competitive Landscape: ', 'Signalling is a closed oligopoly, while North American bus ITS is consolidating around Modaxo and Hitachi, leaving a private long tail to buy');
  hbar(s, 'COMPETITIVE SUMMARY: PUBLIC ITS PLAYER GROUPS AND IMPLICATIONS FOR A NEW ENTRANT', 0, CW, K.navy);
  // five groups: the first two are context (grey headers), the last three are where an entrant focuses (framed, then one callout)
  const cols = [
    ['SIGNALLING MAJORS', ['siemens', 'hitachi', 'alstom', 'crsc'],
      'Together hold most of world signalling, with multi-year order books',
      'Safety-certified systems, long maintenance tails, multi-year frameworks (e.g., DB)',
      'Slow, publicly funded ETCS rollout and execution risk'],
    ['BUS ITS CONSOLIDATORS', ['modaxo', 'hitachi'],
      'Modaxo owns the largest North American installed base, and Hitachi is number two after buying Clever',
      'Largest installed bases, each kept for a system generation. Modaxo buys and never sells',
      'Ageing CAD/AVL architectures, with legacy installs exposed at rebid'],
    ['LISTED PURE PLAYS', ['init', 'ivu'],
      'INIT is the largest listed bus ITS pure play, while IVU is smaller and majority recurring',
      'Full stack (CAD/AVL, scheduling, fare) plus long-term service contracts',
      'Hardware and project mix squeezes margins'],
    ['MID-MARKET PRIVATES', ['avail', 'giro', 'eta', 'passio'],
      'A fragmented long tail of privately held specialists',
      'Sticky agency relationships. Avail and Passio lead real-time feeds at smaller US agencies',
      'Mostly sub-scale, with some still founder-led (GIRO, ETA), so succession is open'],
    ['SAAS / AI CHALLENGERS', ['swiftly', 'optibus', 'via', 'haydenai'],
      'LA Metro and many other US agencies already run cloud overlays on legacy CAD/AVL',
      'Sold beside the incumbent on short contracts. AI enforcement can be funded from fines',
      'Via and Optibus still report losses, and subscriptions fit federal capital grants poorly'],
  ];
  const gx = 0.35, lw = 1.5, gw = 2.18, gg = 0.04, gy = 2.46, hT = 0.34, hL = 0.72;
  const colX = j => gx + lw + gg + j * (gw + gg);
  const rowsG = [['MARKET POSITION', 0.74, K.navy, 'FFFFFF'], ['KEY STRENGTHS', 0.62, K.slate, K.pale], ['KEY WEAKNESSES', 0.56, K.purple, K.lpurple]];
  cols.forEach((c, j) => {
    const x = colX(j), focus = j >= 2;
    // group title (grey for context groups, navy for focus groups), then a white strip with the parents' logos
    R(s, x, gy, gw, hT, focus ? K.navy : K.grey);
    T(s, c[0], { x: x + 0.06, y: gy, w: gw - 0.12, h: hT, fontFace: HEAD, fontSize: 12.5, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
    R(s, x, gy + hT, gw, hL, 'FFFFFF', focus ? K.navy : K.mgrey);
    const n = c[1].length, nc = 2, nr = Math.ceil(n / nc), pad = 0.08;
    const sw = (gw - pad * (nc + 1)) / nc, sh = n > 2 ? (hL - pad * (nr + 1)) / nr : Math.min(0.34, hL - 2 * pad);
    const y0 = gy + hT + (n > 2 ? pad : (hL - sh) / 2);
    c[1].forEach((slug, k) => logoFit(s, slug, x + pad + (k % nc) * (sw + pad) + 0.06, y0 + Math.floor(k / nc) * (sh + pad), sw - 0.12, sh));
  });
  let ry = gy + hT + hL + 0.04;
  rowsG.forEach(([lab, h, lc, cc], ri) => {
    R(s, gx, ry, lw, h, lc);
    T(s, lab, { x: gx + 0.08, y: ry, w: lw - 0.14, h, fontFace: HEAD, fontSize: 12.5, bold: true, color: 'FFFFFF', valign: 'middle' });
    cols.forEach((c, j) => {
      const x = colX(j);
      R(s, x, ry, gw, h, cc, ri === 0 ? K.mgrey : undefined);
      T(s, c[2 + ri], { x: x + 0.07, y: ry + 0.02, w: gw - 0.12, h: h - 0.04, fontSize: 10, bold: ri === 0, color: j >= 2 ? '1A1A1A' : '4A4A4A', valign: 'middle' });
    });
    ry += h + 0.04;
  });
  // frame the three focus groups so the eye goes there
  const frX = colX(2) - 0.04, frW = colX(4) + gw + 0.04 - frX, frY = gy - 0.04, frH = ry - 0.04 + 0.04 - frY;
  s.addShape('rect', { x: frX, y: frY, w: frW, h: frH, fill: { type: 'none' }, line: { color: K.lblue, width: 2.25 } });
  // chevrons into the bottom band
  const cbY = ry + 0.12, cbH = 0.86;
  cols.forEach((c, j) => { const x = colX(j); s.addShape('triangle', { x: x + gw / 2 - 0.25, y: ry + 0.01, w: 0.5, h: 0.1, flipV: true, fill: { color: j >= 2 ? K.navy : K.mgrey }, line: { color: j >= 2 ? K.navy : K.mgrey } }); });
  R(s, gx, cbY, lw, cbH, K.black);
  T(s, 'IMPLICATION FOR A NEW ENTRANT', { x: gx + 0.08, y: cbY, w: lw - 0.14, h: cbH, fontFace: HEAD, fontSize: 12.5, bold: true, color: 'FFFFFF', valign: 'middle' });
  // context callout under the first two groups
  const ctxX = colX(0), ctxW = colX(1) + gw - ctxX;
  R(s, ctxX, cbY, ctxW, cbH, K.lgrey);
  T(s, [{ text: 'Context, not targets: ', options: { bold: true, color: K.dgrey } }, { text: 'signalling is closed, so compete only in adjacencies (monitoring, cyber, connectivity). The consolidators bid against us for targets, and Hitachi may buy at exit while Modaxo sets the floor.', options: { color: '3B3B3D' } }], { x: ctxX + 0.1, y: cbY + 0.04, w: ctxW - 0.2, h: cbH - 0.08, fontSize: 10, valign: 'middle' });
  // focus callout under the three groups that matter: one line, then each group's role under its column
  const focX = colX(2), focW = colX(4) + gw - focX;
  R(s, focX, cbY, focW, cbH, K.navy);
  T(s, 'Where to focus: buy a mid-market private, add SaaS / AI, and exit at a software multiple', { x: focX + 0.1, y: cbY + 0.03, w: focW - 0.2, h: 0.3, fontSize: 11, bold: true, color: 'FFFFFF', valign: 'middle' });
  [['EXIT BENCHMARK', 'Value the exit off INIT and IVU: valuations rise with recurring mix'],
   ['ACQUISITION TARGETS', 'Buy one as the platform, then bolt on others'],
   ['PARTNERS OR RIVALS', 'Overlay, partner or buy capability. Scaled players price as SaaS']].forEach(([role, txt], k) => {
    const x = colX(2 + k);
    T(s, [{ text: role, options: { bold: true, color: K.lblue, breakLine: true } }, { text: txt, options: { color: 'FFFFFF' } }], { x: x + 0.08, y: cbY + 0.34, w: gw - 0.14, h: cbH - 0.38, fontSize: 9.5, valign: 'top' });
  });
  source(s, 'Note: Positions are qualitative, from filed vendor revenue, agency award records and trading data. Multiples in appendix A4. Logos show parent companies, with subsidiaries and brands in appendix A6. Sources: company reports and statutory filings, Berg Insight, deal announcements, GTFS-Realtime feed census, agency board records, trading data as of 6 Nov 2026, analysis');

  // ---------------------------------------------------------------- S6 risks and barriers (0 numbers)
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'RISKS AND BARRIERS TO ENTRY', color: K.lblue }, { text: 'IMPACT ON A NEW ENTRANT', color: K.grey }]);
  title(s, 'Risks and Barriers: ', 'Long system lives and slow procurement favour buying an installed base, and near-term risks are the US funding reset and ETCS slippage', K.grey);
  T(s, 'BARRIERS AND RISKS', { x: 0.45, y: 1.86, w: 5.9, h: 0.34, fontFace: HEAD, fontSize: 17, bold: true, color: K.navy, align: 'center', valign: 'bottom' });
  T(s, 'LIKELY IMPACT ON A NEW ENTRANT', { x: 6.95, y: 1.86, w: 5.95, h: 0.34, fontFace: HEAD, fontSize: 17, bold: true, color: K.navy, align: 'center', valign: 'bottom' });
  R(s, 0.45, 2.24, 5.9, 0.06, K.black); R(s, 6.95, 2.24, 5.95, 0.06, K.black);
  const rk = [
    ['FaHourglassHalf', 'Incumbency and long system lives', 'Installed systems are rarely rebid, typically only after well over a decade. Most renewals skip a competitive rebid', 'HIGH', K.green,
      [[['Only a small slice of the installed base is rebid each year']], [['Challengers usually win when a competitive rebid happens', true]]]],
    ['FaFileContract', 'Slow, formal public procurement', 'Multi-year award-to-go-live, bid protests and Buy America documentation for hardware', 'HIGH', K.green,
      [[['Long sales cycles favour vendors with reference fleets and live pilots']], [['Software-led entry and cooperative purchasing (NASPO, Sourcewell) shorten the path', true]]]],
    ['FaShieldHalved', 'Rail certification and signalling oligopoly', 'SIL-4 and ERA/FRA approvals and long frameworks protect the signalling majors, which together hold most of world signalling', 'HIGH', K.green,
      [[['Signalling cores are effectively closed to new entrants']], [['Adjacencies remain contestable: condition monitoring, cybersecurity, onboard connectivity', true]]]],
    ['FaLandmark', 'US funding reset and ETCS slippage', 'With IIJA advance appropriations lapsed, FY2027 federal transit funding may fall, and EU ETCS rollout is behind schedule', 'MID', K.mblue,
      [[['Agencies in PA, WA and OR, where state rescue funding stalled, may defer purchases']], [['Formula funds for system refresh are the most durable federal line', true]]]],
    ['FaArrowTrendDown', 'Execution and leverage in hardware-heavy models', "Cubic's highly levered buyout is now distressed. Alstom and INIT cut profit guidance", 'MID', K.mblue,
      [[['Project-heavy integrators do not support high buyout leverage']], [['Underwrite on recurring revenue and leave hardware to OEM partners', true]]]],
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
  source(s, "Note: Evidence on incumbency and rebids in appendix A5. Sources: agency board records (LA Metro, TfL, CTA, MARTA, Miami-Dade), 2016-26 ITS award dataset, FTA notices, H.R. 8870, FY2027 President's Budget, European Commission ERTMS Work Plan (2026), company reports, analysis");

  // ---------------------------------------------------------------- S7 investment thesis (6 numbers)
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SEC });
  crumb(s, [{ text: 'INVESTMENT THESIS', color: K.lblue }, { text: 'NEW ENTRANT', color: K.navy }]);
  title(s, 'Investment Thesis: ', 'Buy and build in North American bus ITS software, but returns need a software exit multiple (~' + x1(D.exit_b_mult) + ' revenue), well above the ~' + x1(D.exit_a_mult) + ' paid for Clever');
  hbar(s, 'INVESTMENT THESIS FOR A NEW ENTRANT', 0, CW, K.navy);
  s.addShape('roundRect', { x: 0.35, y: 2.48, w: 3.75, h: 4.25, rectRadius: 0.12, fill: { color: K.navy }, line: { color: K.navy } });
  s.addImage({ data: ic.FaBullseye, x: 0.6, y: 2.66, w: 0.5, h: 0.5 });
  T(s, 'OUR RECOMMENDATION', { x: 1.22, y: 2.68, w: 2.75, h: 0.46, fontFace: HEAD, fontSize: 17, bold: true, color: 'FFFFFF', valign: 'middle' });
  T(s, 'Acquire a privately held North American mid-market bus ITS vendor below a software multiple, move it to cloud, add AI enforcement and zero-emission modules, and make recurring revenue the majority of sales.', { x: 0.6, y: 3.25, w: 3.3, h: 1.35, fontSize: 12, bold: true, color: 'FFFFFF' });
  T(s, [{ text: 'Avoid: ', options: { bold: true, color: K.lblue } }, { text: 'signalling cores and highly levered buyouts of hardware integrators', options: { color: 'FFFFFF' } }], { x: 0.6, y: 4.6, w: 3.3, h: 0.42, fontSize: 11 });
  T(s, 'ILLUSTRATIVE GROSS MOIC, ' + usd0(D.hold) + '-YEAR HOLD', { x: 0.6, y: 5.15, w: 3.3, h: 0.25, fontFace: HEAD, fontSize: 12, bold: true, color: K.lblue });
  const mo = [['Exit at the Clever multiple (' + x1(D.exit_a_mult) + ' revenue)', D.moic_a, K.mgrey], ["Exit at IVU's multiple (" + x1(D.exit_b_mult) + ' revenue)', D.moic_b, K.lblue]];
  mo.forEach(([lab, v, col], i) => {
    const by = 5.48 + i * 0.58;
    T(s, lab, { x: 0.6, y: by, w: 3.3, h: 0.2, fontSize: 9, color: 'FFFFFF' });
    R(s, 0.6, by + 0.22, 2.5 * v / 2.2, 0.26, col); // bar length: chart geometry
    T(s, x1(v), { x: 0.65 + 2.5 * v / 2.2, y: by + 0.2, w: 0.6, h: 0.3, fontFace: HEAD, fontSize: 14, bold: true, color: 'FFFFFF', valign: 'middle' });
  });
  const th = [
    ['FaMapLocationDot', 'WHERE TO PLAY', [[['North American bus software and services (~' + bn1(D.open_na_bus) + '), ', true], ['the most actionable slice of the open pool']], [['Wedges beside incumbents: ', true], ['real-time and cloud CAD/AVL overlays, AI enforcement and safety video, zero-emission scheduling and energy management']]]],
    ['FaBus', 'WHY NORTH AMERICA FIRST', [[['Dated refresh wave: ', true], ['CAD/AVL platforms installed 2009-16 at major agencies reach a replace-or-extend decision by 2031']], [['Open mid-size tier and available targets: ', true], ["mid-size agencies run over half the US fleet, while national procurement regimes split Europe's larger pool, limiting cross-border synergies"]]]],
    ['FaPuzzlePiece', 'HOW TO WIN', [[['Coexist, then displace: ', true], ['sell modules on top of legacy systems and win end-of-life rebids once reference fleets exist']], [['Sell through existing channels: ', true], ['cooperative purchasing and OEM hardware partners. Structure subscriptions to fit federal capital-grant rules']]]],
    ['FaHandHoldingDollar', 'RETURNS AND EXIT', [[['At the Clever precedent the platform barely returns its capital. ', true], ['Likely exit buyers are Hitachi, Siemens and Via, while Modaxo sets the floor price']], [['An IVU-like, majority-recurring mix roughly doubles the equity invested, ', true], ['so recurring revenue is the first diligence question']]]],
  ];
  th.forEach(([icn, lab, bl], i) => {
    const ty = 2.48 + i * 1.07, th2 = 1.02;
    R(s, 4.3, ty, 2.25, th2, '1E9FE0');
    s.addImage({ data: ic[icn], x: 4.42, y: ty + (th2 - 0.42) / 2, w: 0.42, h: 0.42 });
    T(s, lab, { x: 4.95, y: ty, w: 1.55, h: th2, fontFace: HEAD, fontSize: 14, bold: true, color: 'FFFFFF', valign: 'middle' });
    T(s, paras(bl, { paraSpaceAfter: 3 }), { x: 6.7, y: ty + 0.02, w: 6.15, h: th2 - 0.04, fontSize: 10.5, color: '1A1A1A', valign: 'middle' });
    if (i < th.length - 1) s.addShape('line', { x: 4.3, y: ty + th2 + 0.025, w: 8.6, h: 0, line: { color: K.navy, width: 1.25, dashType: 'sysDot' } });
  });
  source(s, 'Note: Illustrative value bridge only, with entry between the INIT and IVU multiples. Assumptions on model sheet Returns and in appendix A4. Sources: Hitachi Q1 FY2026 results, IVU Q3 2026 report, trading data as of 6 Nov 2026, FTA NTD RY2025, 2016-26 ITS award dataset, analysis');

  const out = path.join(OUT_DIR, 'Public_ITS_Market_Case.pptx');
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log('wrote', out);

  // ====================================================================== APPENDIX DECK
  const ap = newDeck('Public ITS Market Case: Appendix', false);
  const AS = 'Appendix';
  ap.addSection({ title: AS });
  s = ap.addSlide({ masterName: 'COVER', sectionTitle: AS });
  R(s, 0, 2.3, CW, 2.1, K.navy);
  T(s, 'APPENDIX: SUPPORTING ANALYSIS', { x: 0.7, y: 2.5, w: 11.8, h: 0.9, fontFace: HEAD, fontSize: 44, bold: true, color: 'FFFFFF', valign: 'middle' });
  T(s, 'PUBLIC ITS MARKET CASE: ROADWAY (BUS) AND RAILWAY', { x: 0.7, y: 3.4, w: 11.8, h: 0.7, fontFace: HEAD, fontSize: 24, bold: true, color: K.lblue, valign: 'middle' });
  T(s, 'A1 Segmentation framework  |  A2 Market build  |  A3 Growth scenarios\nA4 Exit multiples and returns  |  A5 Incumbency and entry window  |  A6 Player directory', { x: 0.7, y: 4.65, w: 11.8, h: 0.7, fontSize: 12.5, color: K.navy });

  // ---------------------------------------------------------------- A1 segmentation framework (0 numbers)
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A1 SEGMENTATION FRAMEWORK', color: K.navy }]);
  pageCode(s, 'A1');
  title(s, 'Segmentation Framework: ', 'Public ITS is cut by mode, functional domain and component layer, with fare collection and road traffic management excluded');
  hbar(s, 'PUBLIC ITS SEGMENTATION: MODE x FUNCTIONAL DOMAIN x COMPONENT LAYER', 0, CW, K.navy);
  const fc = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 10, color: '1A1A1A', valign: 'middle', margin: 0.06 }, o) });
  const fh2 = t => fc(t, { bold: true, color: 'FFFFFF', fill: { color: K.navy }, fontSize: 11, align: 'center' });
  const fl = t => fc(t, { bold: true, color: 'FFFFFF', fill: { color: '1E9FE0' }, fontFace: HEAD, fontSize: 12.5 });
  const fw = [
    [fh2('Functional domain'), fh2('Roadway (bus, BRT, paratransit)'), fh2('Railway (metro, LRT, commuter, mainline passenger)')],
    [fl('A. Operations and fleet management'), fc('Hardware: onboard computer, MDT, radio\nSoftware: CAD/AVL, scheduling, dispatch | Services: integration, hosting'), fc('Hardware: train tracking, control-centre systems\nSoftware: traffic and crew management, timetabling')],
    [fl('B. Passenger information'), fc('Hardware: onboard and stop displays, annunciators\nSoftware: real-time prediction, GTFS-Realtime, apps'), fc('Hardware: platform and onboard displays, PA\nSoftware: real-time and disruption information')],
    [fl('C. Safety, security and surveillance'), fc('Hardware: cameras, collision sensors\nSoftware: bus-lane enforcement, AI incident detection'), fc('Hardware: onboard and station CCTV, intrusion sensors\nSoftware: video analytics, obstacle detection')],
    [fl('D. Asset, telematics and condition monitoring'), fc('Hardware: APC, vehicle-health telematics\nSoftware: asset, energy and charge management'), fc('Hardware: APC, trackside detectors (hot box, wheel impact)\nSoftware: predictive maintenance, digital twins')],
    [fl('E. Train control and signalling'), fc('Not applicable (transit signal priority is a road adjacency)', { color: K.grey, italic: true }), fc('Hardware: interlockings, wayside and onboard ETCS / CBTC / PTC\nSoftware: ATO, ATS | Services: long-term maintenance')],
    [fc('Adjacent, excluded', { bold: true, color: 'FFFFFF', fill: { color: K.grey }, fontFace: HEAD, fontSize: 12.5 }), fc('Fare collection and ticketing, road traffic management and tolling', { fill: { color: K.lgrey } }), fc('Fare collection, rolling stock and TCMS, civil works, freight rail', { fill: { color: K.lgrey } })],
  ];
  s.addTable(fw, { x: 0.45, y: 2.48, w: 12.4, colW: [2.6, 4.9, 4.9], rowH: [0.36, 0.52, 0.52, 0.52, 0.52, 0.52, 0.48], border: { type: 'solid', pt: 0.75, color: 'C7D3DA' }, autoPage: false });
  T(s, paras([[['Geography: ', true, K.mblue], ['bus is sized for Europe and North America (Berg Insight) and scaled to the rest of the world (GMI regional mix), while rail is sized globally']], [['Component layer: ', true, K.mblue], ['hardware, software and services. The open pool is the software and services of bus and other rail ITS']]], { paraSpaceAfter: 3 }), { x: 0.45, y: 6.22, w: 12.4, h: 0.55, fontSize: 10.5, color: '1A1A1A' });
  source(s, 'Sources: Berg Insight (2026), Global Market Insights (2026), UNIFE World Rail Market Study 2026, analysis');

  // ---------------------------------------------------------------- A2 market build (20 numbers)
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A2 MARKET BUILD', color: K.navy }]);
  pageCode(s, 'A2');
  title(s, 'Market Build: ', 'Each segment starts from a published estimate with stated adjustments, and the two analyst-estimated segments sit outside the North American thesis');
  hbar(s, 'HOW THE 2025 MARKET IS BUILT, BILLIONS USD', 0, CW, K.navy);
  const tc = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 10, color: '1A1A1A', valign: 'middle', margin: 0.06 }, o) });
  const th3 = (t, o = {}) => tc(t, Object.assign({ bold: true, color: 'FFFFFF', fill: { color: K.navy }, fontSize: 10.5 }, o));
  const conf = t => tc(t, { bold: true, color: 'FFFFFF', fill: { color: t === 'LOW' ? K.grey : K.mblue }, align: 'center', fontFace: HEAD, fontSize: 12 });
  const seg = t => tc(t, { bold: true, color: K.navy });
  const val = v => tc(bn1(v), { bold: true, align: 'center', fontSize: 11 });
  const less = 'Less ' + p0(D.haircut) + ' for fare collection';
  const td = [
    [th3('Segment'), th3('Published anchor'), th3('Adjustment'), th3('2025', { align: 'center' }), th3('Confidence', { align: 'center' })],
    [seg('Bus and tram ITS, Europe'), tc('Berg Insight (2026): ' + eur(D.berg_eu, 2) + ', fare-inclusive'), tc(less), val(D.bus_eu), conf('MID')],
    [seg('Bus and tram ITS, North America'), tc('Berg Insight (2026): ' + eur(D.berg_na, 2) + ', fare-inclusive'), tc(less), val(D.bus_na), conf('MID')],
    [seg('Bus and tram ITS, rest of world'), tc('Scaled from Europe and North America'), tc('Rest of world = ' + p0(D.row_share) + ' of the global market (GMI regional mix)'), val(D.bus_row), conf('LOW')],
    [seg('Urban signalling (metro, light rail)'), tc('UNIFE World Rail Market Study 2026: rail control ' + eur(D.unife, 1) + ', incl. freight'), tc(p0(D.pax_share) + ' passenger, ' + p0(D.urban_share) + ' of that urban'), val(D.urban), conf('MID')],
    [seg('Mainline and commuter signalling'), tc('Same anchor'), tc('The rest of passenger signalling'), val(D.mainline), conf('MID')],
    [seg('Other rail ITS (passenger information, CCTV, monitoring)'), tc('GMI APTS (2026): ' + bn1(D.gmi_apts) + ', all modes'), tc('Rail share less ticketing, plus analyst estimates for condition monitoring and trackside detection'), val(D.ro), conf('LOW')],
    [tc('Total', { bold: true, color: K.navy, fill: { color: K.lgrey } }), tc('', { fill: { color: K.lgrey } }), tc('', { fill: { color: K.lgrey } }), tc(bn1(D.market), { bold: true, align: 'center', fontSize: 11, fill: { color: K.lgrey } }), tc('', { fill: { color: K.lgrey } })],
  ];
  s.addTable(td, { x: 0.45, y: 2.48, w: 12.4, colW: [2.6, 3.4, 4.0, 1.1, 1.3], rowH: [0.36, 0.44, 0.44, 0.44, 0.44, 0.44, 0.5, 0.38], border: { type: 'solid', pt: 0.75, color: 'C7D3DA' }, autoPage: false });
  // three bottom lines in the A1 style (bullets, same indent); the table ends at y 5.92, so the box starts 0.14in below it
  T(s, paras([
    [['Open pool: ', true, K.mblue], ['software and services of bus ITS (GMI: ' + p0(D.bus_hw_2025) + ' hardware) and other rail ITS (' + p0(D.ro_hw) + ' hardware, analyst) = ' + bn1(D.open) + ', of which North American bus ' + bn1(D.open_na_bus)]],
    [['Cross-checks: ', true, K.mblue], ["SCI Verkehr's independent signalling estimate is " + CITED.sci_vs_unife_words + " of UNIFE's. GMI's CBTC-only market sits below our urban signalling, which also covers light rail"]],
    [['Bottom-up: ', true, K.mblue], ['buses and vehicles \u00D7 price per unit across 11 spending pools gives ' + bn1(D.bu_total / 1000) + ' for North American bus ITS, ' + p0(D.bu_ratio) + ' of the top-down ' + bn1(D.bu_topdown / 1000)]],
  ], { paraSpaceAfter: 3 }), { x: 0.45, y: 6.06, w: 12.4, h: 0.82, fontSize: 10.5, color: '1A1A1A' });
  source(s, "Note: Nominal USD at 2025 average FX. Figures may not sum due to rounding. Model: sheets Market and Bottom-up, where every input carries its source and confidence. Sources: Berg Insight (2026), UNIFE World Rail Market Study 2026, SCI Verkehr (2026), Global Market Insights (2026), analysis");

  // ---------------------------------------------------------------- A3 growth scenarios (22 numbers)
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A3 GROWTH SCENARIOS', color: K.green }]);
  pageCode(s, 'A3');
  title(s, 'Growth Scenarios: ', 'Two-thirds of the increase to 2031 is signalling, and 2031 ranges from ~' + bn0(MP.low_2031) + ' to ~' + bn0(MP.high_2031) + ', mostly on the pace of signalling modernisation', K.green);
  hbar(s, 'GROWTH BRIDGE 2025 TO 2031E, BASE CASE, BILLIONS USD', 0, 6.2, K.dgreen);
  hbar(s, 'SCENARIOS: CAGR 2025-31E BY SEGMENT', 6.26, CW - 6.26, K.dgreen);
  const brL = ['Bus and tram ITS', 'Rail signalling', 'Other rail ITS'];
  // one non-zero value per series so each bar takes its segment colour
  s.addChart(ap.ChartType.bar, [
    { name: 'Bus and tram ITS', labels: brL, values: [BP.increase, 0, 0] },
    { name: 'Rail signalling', labels: brL, values: [0, SP.increase, 0] },
    { name: 'Other rail ITS', labels: brL, values: [0, 0, RP.increase] },
  ], { x: 0.35, y: 2.5, w: 5.8, h: 3.3, barDir: 'bar', barGrouping: 'clustered', barOverlapPct: 100, catAxisOrientation: 'maxMin', showValue: true, dataLabelPosition: 'outEnd', dataLabelColor: K.navy, dataLabelFontFace: HEAD, dataLabelFontBold: true, dataLabelFontSize: 13, dataLabelFormatCode: '+"$"0.0"B";;', showLegend: false, valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisLabelFontFace: BODY, catAxisLabelFontSize: 11, catAxisLabelColor: '1A1A1A', catAxisLineShow: false, valAxisMinVal: 0, valAxisMaxVal: 8, barGapWidthPct: 45, chartColors: [K.sBus, K.sMain, K.sOther] });
  T(s, '+' + bn1(MP.increase) + ' in total, 2025 to 2031E', { x: 0.35, y: 5.95, w: 5.8, h: 0.4, fontFace: HEAD, fontSize: 16, bold: true, color: K.navy, align: 'center' });
  const gc = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 9.5, color: '1A1A1A', valign: 'middle', margin: 0.05 }, o) });
  const gh = (t, o = {}) => gc(t, Object.assign({ bold: true, color: 'FFFFFF', fill: { color: K.navy }, fontSize: 10, align: 'center' }, o));
  const scen = (lab, r, basis) => [gc(lab, { bold: true, color: K.navy }), gc(p1(r.cagr_low), { align: 'center' }), gc(p1(r.cagr_base), { align: 'center', bold: true }), gc(p1(r.cagr_high), { align: 'center' }), gc(basis, { fontSize: 9 })];
  const sc = [
    [gh('Segment', { align: 'left' }), gh('Low'), gh('Base'), gh('High'), gh('Basis of the base and range', { align: 'left' })],
    // each range marker is tied to its value with non-breaking spaces ('low = ...'), so a marker never ends a line
    scen('Bus and tram ITS, Europe', D.bus_eu_path, "Berg Insight forecast,\nlow = zero-emission bus capex crowds out ITS,\nhigh = earlier edition's pace plus enforcement"),
    scen('Bus and tram ITS, North America', D.bus_na_path, 'Berg Insight forecast,\nlow = FY2027 federal funding reset,\nhigh = a partial return toward the 2022-25 pace'),
    scen('Bus and tram ITS, rest of world', D.bus_row_path, 'GMI Asia-Pacific growth, blended with slower Latin America, Middle East and Africa'),
    scen('Rail signalling (urban and mainline)', SP, "Just above SCI Verkehr's nominal forecast and in line with UNIFE's real outlook plus inflation, low = ETCS slippage and the UK cut, high = FRMCS and driverless-metro conversions"),
    scen('Other rail ITS', RP, 'Between rail asset-management and telematics forecasts (MarketsandMarkets, Mordor)'),
    [gc('Market, 2031E', { bold: true, color: K.navy, fill: { color: K.lgrey } }), gc(bn1(MP.low_2031), { bold: true, align: 'center', fill: { color: K.lgrey } }), gc(bn1(MP.values[6]), { bold: true, align: 'center', fill: { color: K.lgrey } }), gc(bn1(MP.high_2031), { bold: true, align: 'center', fill: { color: K.lgrey } }), gc('', { fill: { color: K.lgrey } })],
  ];
  s.addTable(sc, { x: 6.4, y: 2.48, w: 6.5, colW: [1.8, 0.62, 0.62, 0.62, 2.84], rowH: [0.34, 0.56, 0.56, 0.48, 0.86, 0.48, 0.4], border: { type: 'solid', pt: 0.75, color: 'C7D3DA' }, autoPage: false });
  source(s, "Note: Nominal USD at constant 2025 FX. Low and high use each segment's own low or high rate. Model: sheet Growth. Sources: Berg Insight (2026), UNIFE World Rail Market Study 2026, SCI Verkehr (2023, 2026), Global Market Insights (2026), MarketsandMarkets, Mordor Intelligence, FTA, analysis");

  // ---------------------------------------------------------------- A4 exit multiples and returns (17 numbers)
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A4 EXIT MULTIPLES AND RETURNS', color: K.navy }]);
  pageCode(s, 'A4');
  title(s, 'Exit Multiples: ', 'The Clever precedent (~' + x1(D.bm_clever) + " revenue) barely returns capital, so the thesis needs IVU's ~" + x1(D.bm_ivu) + ', a multiple earned by software-led, majority-recurring revenue');
  hbar(s, 'EV / REVENUE, TRANSACTIONS AND TRADING', 0, 6.2, K.navy);
  hbar(s, 'ILLUSTRATIVE VALUE BRIDGE, USD M', 6.26, CW - 6.26, K.navy);
  // one non-zero value per series so each bar takes its own colour: Clever grey and IVU light blue as on slide 7, the other benchmarks muted
  const bmL = ['Conduent transit to Modaxo (2026)', 'INIT (trading)', 'Clever Devices to Hitachi (2026)', 'IVU (trading)', 'Via (trading, LTM revenue)'];
  const bmV = [D.bm_conduent, D.bm_init, D.bm_clever, D.bm_ivu, D.bm_via];
  s.addChart(ap.ChartType.bar, bmL.map((n, i) => ({ name: n, labels: bmL, values: bmV.map((v, j) => (j === i ? v : 0)) })),
    { x: 0.35, y: 2.5, w: 5.8, h: 3.9, barDir: 'bar', barGrouping: 'clustered', barOverlapPct: 100, catAxisOrientation: 'maxMin', showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0"x";;', dataLabelFontFace: HEAD, dataLabelFontBold: true, dataLabelFontSize: 13, dataLabelColor: K.navy, showLegend: false, valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisLabelFontFace: BODY, catAxisLabelFontSize: 10.5, catAxisLabelColor: '1A1A1A', catAxisLineShow: false, valAxisMinVal: 0, valAxisMaxVal: 6.6, barGapWidthPct: 45, chartColors: ['C9D3DD', 'C9D3DD', K.mgrey, K.lblue, 'C9D3DD'] });
  const vc = (t, o = {}) => ({ text: t, options: Object.assign({ fontFace: BODY, fontSize: 11, color: '1A1A1A', valign: 'middle', align: 'center', margin: 0.05 }, o) });
  const vh = t => vc(t, { bold: true, color: 'FFFFFF', fill: { color: K.navy } });
  const vb = [
    [vh(''), vh('Entry'), vh('Exit A: Clever multiple'), vh('Exit B: IVU multiple')],
    [vc('Revenue', { align: 'left', bold: true, color: K.navy }), vc(usd0(D.rev0)), vc(usd0(D.rev1)), vc(usd0(D.rev1))],
    [vc('EV / revenue', { align: 'left', bold: true, color: K.navy }), vc(x1(D.entry_mult)), vc(x1(D.exit_a_mult)), vc(x1(D.exit_b_mult))],
    [vc('Gross MOIC', { align: 'left', bold: true, color: K.navy, fill: { color: K.lgrey } }), vc('', { fill: { color: K.lgrey } }), vc(x1(D.moic_a), { bold: true, fill: { color: K.lgrey } }), vc(x1(D.moic_b), { bold: true, fill: { color: K.lgrey } })],
  ];
  s.addTable(vb, { x: 6.4, y: 2.55, w: 6.5, colW: [1.6, 1.4, 1.75, 1.75], rowH: 0.5, border: { type: 'solid', pt: 0.75, color: 'C7D3DA' }, autoPage: false });
  T(s, paras([
    [['Entry: ', true, K.mblue], ["between INIT and IVU, below IVU's software multiple"]],
    [['If entry is at the Clever multiple instead: ', true, K.mblue], ['MOIC ' + x1(D.moic_a_at_a) + ' (exit A) and ' + x1(D.moic_b_at_a) + ' (exit B)']],
    [['Assumptions: ', true, K.mblue], [p0(D.growth) + ' organic growth, $' + usd0(D.bolt_rev) + 'M of bolt-on revenue bought at ' + x1(D.bolt_mult) + ', entry debt ' + x1(D.leverage) + ' EBITDA (half repaid by exit) and a ' + usd0(D.hold) + '-year hold']],
  ], { paraSpaceAfter: 8 }), { x: 6.4, y: 4.85, w: 6.5, h: 1.5, fontSize: 11, color: '1A1A1A', valign: 'top' });
  source(s, 'Note: Clever = consideration plus debt repaid, on projected 2026 revenue (Hitachi Q1 FY2026 results). Trading multiples as of 6 Nov 2026, with Via on LTM revenue. Model: sheet Returns. Sources: Hitachi Q1 FY2026 results, Conduent 8-K (Oct 2026), IVU Q3 2026 report, stockanalysis, analysis');

  // ---------------------------------------------------------------- A5 incumbency and entry window (11 numbers: cited, and the NTD CSV)
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A5 INCUMBENCY AND ENTRY WINDOW', color: K.navy }]);
  pageCode(s, 'A5');
  title(s, 'Incumbency: ', 'Systems are ~' + CITED.tenure_median + ' years old at a decision point, challengers win most competitive rebids, and mid-size agencies run over half the US fleet');
  hbar(s, CITED.dp_total + ' DECISION POINTS ON INCUMBENT-HELD SYSTEMS, 2016-26', 0, 6.45, K.navy);
  hbar(s, 'US FULL-SIZE BUS FLEET BY AGENCY SIZE, 2025', 6.51, CW - 6.51, K.navy);
  s.addShape('line', { x: 6.48, y: 2.45, w: 0, h: 4.3, line: { color: K.navy, width: 1.5 } });
  // 100% bar of the decision points (segment widths: chart geometry on the CITED counts)
  const bx = 0.45, bw = 5.8, by0 = 2.85, bh = 0.6;
  const dps = [
    [CITED.dp_extended, K.mgrey, 'Kept without a documented rebid'],
    [CITED.dp_rebid_kept, K.navy, 'Incumbent kept'],
    [CITED.dp_rebid_lost, K.lblue, 'Challenger won'],
  ];
  let bxx = bx;
  const segX = [];
  dps.forEach(([n, col]) => {
    const w = bw * n / CITED.dp_total;
    R(s, bxx, by0, w, bh, col);
    T(s, String(n), { x: bxx, y: by0, w, h: bh, fontFace: HEAD, fontSize: 14, bold: true, color: col === K.mgrey ? K.navy : 'FFFFFF', align: 'center', valign: 'middle' }); // navy on the light grey segment for contrast
    segX.push([bxx, w]);
    bxx += w;
  });
  // segment names under the bar, one line each, bold, colour-matched and centred on their segments (at least 1.5in wide, so the narrow navy segment's label overhangs it evenly)
  [K.grey, K.navy, '0F7EC2'].forEach((col, i) => { const lw2 = Math.max(1.5, segX[i][1] - 0.1); T(s, dps[i][2], { x: segX[i][0] + (segX[i][1] - lw2) / 2, y: by0 + bh + 0.06, w: lw2, h: 0.4, fontSize: 9, color: col, bold: true, align: 'center' }); });
  // bracket over the two competitive-rebid segments
  bracketH(s, segX[1][0] + 0.02, bx + bw - 0.02, by0 - 0.12, 0.1, K.navy);
  T(s, 'Competitive rebids: challengers won most', { x: segX[1][0], y: by0 - 0.4, w: bx + bw - segX[1][0], h: 0.26, fontSize: 9.5, bold: true, color: K.navy, align: 'center', valign: 'bottom' });
  // tenure tile
  s.addShape('roundRect', { x: 0.45, y: 4.05, w: 5.8, h: 1.05, rectRadius: 0.1, fill: { color: K.paler }, line: { color: K.mblue, width: 1.25 } });
  T(s, '~' + CITED.tenure_median + ' years', { x: 0.6, y: 4.05, w: 2.1, h: 1.05, fontFace: HEAD, fontSize: 30, bold: true, color: K.mblue, valign: 'middle' });
  T(s, 'median age of an incumbent system when it reaches a decision point (n=' + CITED.tenure_n + ')', { x: 2.7, y: 4.05, w: 3.4, h: 1.05, fontSize: 10.5, color: '1A1A1A', valign: 'middle' });
  // caveat
  R(s, 0.45, 5.3, 5.8, 0.9, K.lgrey);
  T(s, [{ text: 'Sample: ', options: { bold: true } }, { text: CITED.dp_total + ' decisions on incumbent-held systems in the US, Canada and the UK, from agency board records. In bus CAD/AVL, incumbents lost every competitive rebid in the sample, but every winner was an established vendor (Clever, INIT, Equans, Vontas).' }], { x: 0.6, y: 5.3, w: 5.5, h: 0.9, fontSize: 10, color: '1A1A1A', valign: 'middle' });
  // fleet by agency tier (bar lengths: chart geometry on the CSV shares)
  const tiers = ['4: 1000+', '3: 250-999', '2: 50-249', '1: 1-49'].map(t => NTD.find(r => r.tier === t));
  const tx = 8.3, tScale = 2.4 / 35, ty0 = 2.75, tPitch = 0.72, tH = 0.5;
  tiers.forEach((r, i) => {
    const yy = ty0 + i * tPitch, mid = i === 1 || i === 2;
    T(s, TIER_LABEL[r.tier], { x: 6.68, y: yy, w: 1.5, h: tH, fontSize: 10.5, bold: true, color: K.navy, align: 'right', valign: 'middle' });
    R(s, tx, yy, r.pct * tScale, tH, mid ? K.lblue : K.mgrey);
    T(s, Math.round(r.pct) + '%', { x: tx + r.pct * tScale + 0.08, y: yy, w: 0.6, h: tH, fontFace: HEAD, fontSize: 14, bold: true, color: K.navy, valign: 'middle' });
  });
  const brX = tx + 35 * tScale + 0.40; // clear of the longest bar's label, and leaves the label box 1.68in wide
  bracketV(s, brX, ty0 + tPitch + 0.02, ty0 + 2 * tPitch + tH - 0.02, 0.1, K.navy);
  T(s, 'Mid-size (50-999 buses): over half the fleet and the core customers', { x: brX + 0.12, y: ty0 + tPitch, w: 12.9 - brX - 0.12, h: tPitch + tH, fontSize: 9.5, bold: true, color: K.navy, valign: 'middle' });
  T(s, 'Share of active full-size buses in the US, by size of the operating agency (may not sum due to rounding)', { x: 6.68, y: ty0 + 4 * tPitch - 0.08, w: 6.2, h: 0.25, fontSize: 9, italic: true, color: K.grey });
  T(s, [{ text: 'Refresh wave: ', options: { bold: true, color: K.mblue } }, { text: 'CAD/AVL platforms installed in 2009-16 now serve about ' + CITED.refresh_cohort.toLocaleString('en-US') + ' buses in the US and Canada (TriMet, Denver RTD, NJ Transit, Miami-Dade, TTC, TransLink and others)' }], { x: 6.68, y: 6.1, w: 6.2, h: 0.6, fontSize: 10, color: '1A1A1A', valign: 'top' });
  source(s, 'Sources: 2016-26 ITS award dataset (agency board records), FTA NTD RY2025 Revenue Vehicle Inventory, agency CAD/AVL records, analysis');

  // ---------------------------------------------------------------- A6 player directory (parents, their subsidiaries and brands, owners)
  // Rows from research notes 08, 09, 10, 22 (gap), 26 (gap), 32 (gap), 34 (gap); register C59. Two panels: groups 1-3 left, 4-6 right.
  const DIRECTORY = [["Signalling majors", [["Siemens", "Siemens Mobility, Hacon (HAFAS), Sqills, eos.uptrade, Padam, MERMEC units (bought 2026)", "Siemens AG (listed)"], ["Hitachi", "Hitachi Rail, ex-Thales GTS (2024), ex-Ansaldo STS, SelTrac CBTC, HMAX", "Hitachi, Ltd. (listed, Tokyo)"], ["Alstom", "Urbalis, Atlas, HealthHub, Nomad Digital,\nex-Bombardier (2021), 49% of CASCO", "Listed (Euronext Paris)"], ["CRSC", "CASCO Signal (51%, JV with Alstom)", "State-owned, listed (Shanghai, Hong Kong)"]]], ["Bus ITS consolidators", [["Modaxo", "Trapeze, Vontas, Routeward (ex-Conduent), Novvan (fare), TripSpark (incl. Routematch), TransLoc, SISCOG, FARA", "Constellation Software (listed, TSX)"], ["Hitachi Rail", "Clever Devices (now Hitachi Mobility Multimodal Solutions), incl. MAIOR scheduling", "Hitachi, Ltd. (listed), bought Clever Jul 2026"]]], ["Listed pure plays (Cubic also competes)", [["INIT", "DILAX, iris-GmbH (majority),\nMOBILE-ITCS, MOBILE-PLAN, MOBILEvario", "Listed (XETRA),\nfounder-controlled"], ["IVU", "IVU.suite", "Listed (Frankfurt Prime Standard)"], ["Cubic", "Cubic Transportation Systems, Umo (NextBus brand retired)", "Veritas Capital, Elliott (private, distressed)"]]], ["Mid-market privates", [["Avail", "myAvail", "Private, employee-owned (ESOP)"], ["GIRO", "HASTUS, GeoRoute", "Private, founder-led"], ["ETA Transit Systems", "-", "Private, founder-led"], ["Passio (Transit Technologies)", "Passio, ParaPlan. Sister brands Ecolane, TripMaster (CTS Software), Vestige", "Private (Transit Technologies LLC)"]]], ["SaaS / AI challengers", [["Swiftly", "Hopthru, TextMarks", "VC/growth equity (Cove Hill, JMI)"], ["Optibus", "-", "VC-backed (Insight, Bessemer)"], ["Via", "Remix, Citymapper, Downtowner", "Listed (NYSE: VIA)"], ["Hayden AI", "-", "VC-backed (TPG Rise Fund)"]]], ["Also active, not on the competitive landscape", [["Luminator", "LTG Sweden (ex-Mobitec)", "Audax Private Equity (since 2014)"], ["Hanover Displays", "-", "Private, family-owned"], ["Equans", "Ineo Systrans, Icomera", "Bouygues (since 2022)"]]]];
  s = ap.addSlide({ masterName: 'CONTENT', sectionTitle: AS });
  crumb(s, [{ text: 'APPENDIX', color: K.lblue }, { text: 'A6 PLAYER DIRECTORY', color: K.navy }]);
  pageCode(s, 'A6');
  title(s, 'Player Directory: ', 'The parent companies behind the logos on the competitive landscape, with the subsidiaries and brands they sell under');
  hbar(s, 'PUBLIC ITS PLAYERS BY GROUP: SUBSIDIARIES, BRANDS AND OWNERSHIP', 0, CW, K.navy);
  const dirPanel = (gs, x) => {
    const hc = (txt) => ({ text: txt, options: { bold: true, color: 'FFFFFF', fill: { color: K.navy }, fontSize: 9, valign: 'middle' } });
    const rows = [[hc('Company'), hc('Subsidiaries and brands'), hc('Ownership')]];
    gs.forEach(([g, rs]) => {
      rows.push([{ text: g.toUpperCase(), options: { colspan: 3, bold: true, color: K.navy, fill: { color: K.pale }, fontSize: 8.5, valign: 'middle' } }]);
      rs.forEach(([co, units, owner]) => rows.push([
        { text: co, options: { bold: true, color: K.navy, fontSize: 8.5, valign: 'middle' } },
        { text: units, options: { fontSize: 8.5, color: '1A1A1A', valign: 'middle' } },
        { text: owner, options: { fontSize: 8.5, color: '1A1A1A', valign: 'middle' } }]));
    });
    s.addTable(rows, { x, y: 2.48, w: 6.1, colW: [1.25, 3.15, 1.7], border: { type: 'solid', pt: 0.5, color: 'C7D3DA' }, margin: 0.04, autoPage: false });
  };
  dirPanel(DIRECTORY.slice(0, 3), 0.45);
  dirPanel(DIRECTORY.slice(3), 6.75);
  source(s, 'Note: Logos on the competitive landscape show these parent companies only. Sources: company reports and websites, statutory filings, deal announcements (Hitachi, Constellation Software, Siemens, Bouygues), analysis');

  const out2 = path.join(OUT_DIR, 'Public_ITS_Market_Case_Appendix.pptx');
  await ap.writeFile({ fileName: out2 });
  await applyTheme(out2, THEME);
  console.log('wrote', out2);
})();
