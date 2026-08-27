// Survey pathway bot — console snippet. Built by build-snippet.mjs; do not edit here.
// Paste into the DevTools console on a survey page, or save as a DevTools Snippet
// (Sources ▸ Snippets ▸ New) and press Ctrl/Cmd+Enter to re-run it on each page.
(() => {
// Shared core — the only copy of "what is on this page and how do I answer it".
//
// Loaded three ways, so keep it dependency-free, ES5-ish and side-effect-free
// apart from the SPB_CORE assignment at the bottom:
//   1. the Chrome extension  (a content script, listed in manifest.json)
//   2. the console snippet   (dist/console-snippet.js is this file + a wrapper)
//   3. the Node/Playwright CLIs (injected into the page by lib/extract.mjs)
//
// Questions are found by grouping the visible form controls by their `name`
// attribute, which is how every hosted survey engine (Decipher/Forsta,
// Qualtrics, Confirmit, Alchemer, SurveyMonkey) renders radios, checkboxes,
// dropdowns, grids and open ends.

const DEFAULT_SELECTORS = {
  // Containers used to find a question's wording. Decipher-first, then generic.
  questionContainers: ['div.question', 'div.q', 'fieldset', 'div[role="group"]', 'div[class*="question"]'],
  // Candidates for the forward button, best first.
  nextButtons: [
    '#continue',
    'input[name="continue"]',
    'button[name="continue"]',
    'input[type="submit"]',
    'button[type="submit"]',
    '.btn-primary',
    'button.next',
    'a.next',
  ],
  // Page text that means "this run is over".
  terminalPatterns: {
    complete: ['thank you for completing', 'survey is complete', 'thanks for taking', 'your responses have been recorded', 'completed the survey'],
    quota: ['quota', 'we have enough', 'group is full'],
    terminate: ['do not qualify', "don't qualify", 'not qualify', 'screened out', 'unfortunately', "we're sorry", 'we are sorry', 'no longer available'],
  },
};

function pageModel(cfg, doc) {
  doc = doc || document;
  const win = doc.defaultView || window;
  const visible = (el) => {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    const s = win.getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0' && (r.width > 0 || r.height > 0);
  };
  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();

  // A selector that is *verified* to resolve back to this exact element.
  // Survey engines routinely put id="Q3" on the wrapper div and name="Q3" on
  // the control inside it, so an unchecked `#Q3` would target the wrapper.
  let stamp = 0;
  const resolves = (sel, el) => {
    try { return doc.querySelector(sel) === el; } catch { return false; }
  };
  const cssFor = (el) => {
    if (el.id && /^[A-Za-z][\w:.-]*$/.test(el.id)) {
      const sel = `#${CSS.escape(el.id)}`;
      if (resolves(sel, el)) return sel;
    }
    const tag = el.tagName.toLowerCase();
    if (el.name) {
      const attrs = [`[name="${CSS.escape(el.name)}"]`];
      if (el.tagName === 'INPUT' && el.getAttribute('value') != null)
        attrs.push(`[value="${CSS.escape(el.getAttribute('value'))}"]`);
      const sel = tag + attrs.join('');
      if (resolves(sel, el)) return sel;
    }
    // Last resort: mark the element so the selector cannot be ambiguous.
    const mark = el.getAttribute('data-spb') ?? String(++stamp);
    el.setAttribute('data-spb', mark);
    return `[data-spb="${mark}"]`;
  };

  // Which phrases inside an element are bold or underlined. Emphasis is part of
  // the questionnaire spec (underlined phrases are what piped questions insert),
  // so it is captured, not ignored. Only leaf nodes are inspected, otherwise a
  // bold container would report every phrase inside it.
  const marksOf = (el) => {
    const out = { bold: [], underline: [] };
    if (!el) return out;
    const nodes = [el, ...el.querySelectorAll('*')];
    for (const node of nodes) {
      if (node.children.length) continue;
      const t = clean(node.innerText || node.textContent || '');
      if (!t || t.length > 160) continue;
      let s;
      try { s = win.getComputedStyle(node); } catch { continue; }
      const weight = parseInt(s.fontWeight, 10) || (s.fontWeight === 'bold' ? 700 : 400);
      const deco = `${s.textDecorationLine || ''} ${s.textDecoration || ''}`;
      if (weight >= 600 && out.bold.length < 8) out.bold.push(t);
      if (deco.includes('underline') && out.underline.length < 8) out.underline.push(t);
    }
    return out;
  };

  // Text of the label attached to a single control.
  const optionLabelEl = (el) => {
    if (el.id) {
      const lab = doc.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (lab && clean(lab.innerText)) return lab;
    }
    const wrap = el.closest('label');
    if (wrap && clean(wrap.innerText)) return wrap;
    const cell = el.closest('td, th, li, div');
    if (cell && clean(cell.innerText) && clean(cell.innerText).length < 120) return cell;
    return null;
  };
  const optionLabel = (el) => {
    const lab = optionLabelEl(el);
    if (lab) return clean(lab.innerText);
    return clean(el.getAttribute('aria-label') || el.value || '');
  };

  // Wording of the question a control belongs to. For a grid, the row header
  // is appended, since that is what distinguishes Q2r1 from Q2r2.
  const questionLabel = (el, sink) => {
    let stem = '';
    for (const sel of cfg.questionContainers) {
      const box = el.closest(sel);
      if (!box) continue;
      const head = box.querySelector('legend, .qtitle, .question-text, .question-title, h1, h2, h3, h4, .title, p');
      stem = clean(head?.innerText || '') || clean(box.innerText).slice(0, 300);
      if (stem) {
        if (sink) sink.el = head || box;
        break;
      }
    }
    const row = el.closest('tr');
    if (row) {
      const cell = row.querySelector('th') ?? row.querySelector('td');
      const rowLabel = clean(cell?.innerText || '');
      // Only a header cell, not the cell holding this very control.
      if (rowLabel && !cell.contains(el) && rowLabel.length < 120)
        return (stem ? `${stem} — ${rowLabel}` : rowLabel).slice(0, 300);
    }
    return stem.slice(0, 300);
  };

  const controls = [...doc.querySelectorAll('input, select, textarea')].filter((el) => {
    const type = (el.type || '').toLowerCase();
    if (['hidden', 'submit', 'button', 'image', 'reset', 'file'].includes(type)) return false;
    if (el.disabled) return false;
    return visible(el);
  });

  const groups = new Map();
  for (const el of controls) {
    const key = el.name || el.id || cssFor(el);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(el);
  }

  const questions = [];
  for (const [key, els] of groups) {
    const first = els[0];
    const tag = first.tagName.toLowerCase();
    const type = (first.type || '').toLowerCase();
    let kind;
    if (tag === 'select') kind = 'select';
    else if (type === 'radio') kind = 'radio';
    else if (type === 'checkbox') kind = 'checkbox';
    else if (tag === 'textarea') kind = 'textarea';
    else if (type === 'number' || type === 'range') kind = 'number';
    else kind = 'text';

    const stemSink = {};
    const q = {
      key,
      kind,
      label: questionLabel(first, stemSink),
      required: els.some((e) => e.required || e.getAttribute('aria-required') === 'true'),
      selector: cssFor(first),
      emphasis: marksOf(stemSink.el),
      options: [],
    };

    if (kind === 'select') {
      q.options = [...first.options]
        .filter((o) => o.value !== '' && !o.disabled)
        .map((o) => ({ value: o.value, label: clean(o.text), selector: q.selector }));
    } else if (kind === 'radio' || kind === 'checkbox') {
      q.options = els.map((e) => ({
        value: e.value ?? '',
        label: optionLabel(e),
        selector: cssFor(e),
        emphasis: marksOf(optionLabelEl(e)),
      }));
    }
    questions.push(q);
  }

  // Forward button.
  let next = null;
  for (const sel of cfg.nextButtons) {
    const el = [...doc.querySelectorAll(sel)].find((e) => visible(e) && !e.disabled);
    if (el) {
      next = { selector: cssFor(el), label: clean(el.innerText || el.value || ''), matched: sel };
      break;
    }
  }

  const bodyText = clean(doc.body?.innerText || '');
  const lower = bodyText.toLowerCase();
  let outcome = null;
  for (const [name, pats] of Object.entries(cfg.terminalPatterns)) {
    if (pats.some((p) => lower.includes(p))) { outcome = name; break; }
  }

  const heading = clean(
    doc.querySelector('h1, h2, .page-title, .survey-title')?.innerText || doc.title || ''
  ).slice(0, 200);

  return {
    url: doc.location.href,
    title: doc.title,
    heading,
    questions,
    next,
    outcome,
    bodyText: bodyText.slice(0, 4000),
  };
}

function fingerprint(model) {
  const keys = model.questions.map((q) => q.key).sort();
  if (keys.length) return `Q:${keys.join(',')}`;
  const kind = model.outcome ?? 'page';
  return `${kind.toUpperCase()}:${(model.heading || model.bodyText.slice(0, 60)).toLowerCase().replace(/\s+/g, '-').slice(0, 40)}`;
}

const DEFAULT_VALUES = {
  text: 'Test response',
  textarea: 'Automated pathway-test response.',
  number: '30',
};

function ruleFor(q, config) {
  for (const rule of config.answers ?? []) {
    const re = new RegExp(rule.match, rule.flags ?? 'i');
    if (re.test(q.key) || (q.label && re.test(q.label))) return rule;
  }
  return null;
}

function branchable(q, config) {
  if (config.branchOn) {
    const re = new RegExp(config.branchOn, 'i');
    if (!re.test(q.key) && !(q.label && re.test(q.label))) return false;
  }
  if (config.noBranch) {
    const re = new RegExp(config.noBranch, 'i');
    if (re.test(q.key) || (q.label && re.test(q.label))) return false;
  }
  return true;
}

// -> [{ kind: 'option', index, value, label } | { kind: 'value', value }]
function candidates(q, config = {}) {
  const rule = ruleFor(q, config);

  if (q.kind === 'radio' || q.kind === 'checkbox' || q.kind === 'select') {
    let opts = q.options.map((o, index) => ({ kind: 'option', index, value: o.value, label: o.label }));
    if (rule?.options) {
      const re = new RegExp(rule.options, 'i');
      const filtered = opts.filter((o) => re.test(o.value) || re.test(o.label));
      if (filtered.length) opts = filtered;
    }
    if (rule?.skip) return [{ kind: 'noop', label: '(left unchecked)' }];
    if (rule?.fixed != null) {
      const re = new RegExp(rule.fixed, 'i');
      const hit = opts.find((o) => re.test(o.value) || re.test(o.label));
      return hit ? [hit] : opts.slice(0, 1);
    }
    // A lone checkbox is a two-way branch: ticked, or deliberately left blank.
    // (Decipher and friends name each checkbox of a multi-select separately, so
    // this is the common case, not an edge case.)
    if (q.kind === 'checkbox' && opts.length === 1 && rule?.fixed == null) {
      return branchable(q, config) ? [opts[0], { kind: 'noop', label: '(left unchecked)' }] : [opts[0]];
    }
    if (!branchable(q, config)) opts = opts.slice(0, 1);
    const cap = config.maxOptionsPerQuestion ?? 0;
    if (cap > 0 && opts.length > cap) opts = opts.slice(0, cap);
    return opts.length ? opts : [{ kind: 'noop' }];
  }

  // Free-text style.
  if (rule?.values?.length) return rule.values.map((v) => ({ kind: 'value', value: String(v) }));
  if (rule?.value != null) return [{ kind: 'value', value: String(rule.value) }];
  const fallback = config.values?.[q.kind] ?? DEFAULT_VALUES[q.kind] ?? 'Test';
  return [{ kind: 'value', value: String(fallback) }];
}

function describe(q, candidate) {
  if (candidate.kind === 'value') return `"${candidate.value}"`;
  if (candidate.kind === 'noop') return candidate.label ?? '(no answer)';
  const opt = q.options[candidate.index];
  return opt?.label ? `${opt.label} [${opt.value}]` : `[${opt?.value ?? candidate.index}]`;
}

// DOM-native answering, used by the Chrome extension and the console snippet.
// (The Node/Playwright build answers through Playwright's own APIs instead, so
// that it waits for the engine's own visibility and enabled checks.)
function applyAnswer(q, candidate, doc) {
  doc = doc || document;
  const win = doc.defaultView || window;
  if (!candidate || candidate.kind === 'noop') return true;
  const fire = (el, types) => {
    for (const t of types) el.dispatchEvent(new win.Event(t, { bubbles: true }));
  };
  if (candidate.kind === 'value') {
    const el = doc.querySelector(q.selector);
    if (!el) return false;
    el.focus?.();
    el.value = candidate.value;
    fire(el, ['input', 'change', 'blur']);
    return true;
  }
  const opt = q.options[candidate.index];
  if (!opt) return false;
  if (q.kind === 'select') {
    const el = doc.querySelector(q.selector);
    if (!el) return false;
    el.value = opt.value;
    fire(el, ['input', 'change']);
    return true;
  }
  const el = doc.querySelector(opt.selector);
  if (!el) return false;
  el.click();
  if (!el.checked) {
    el.checked = true;
    fire(el, ['input', 'change']);
  }
  return true;
}

// Click the forward button described by a page model.
function clickNext(model, doc) {
  if (!model.next) return false;
  const el = (doc || document).querySelector(model.next.selector);
  if (!el) return false;
  el.click();
  return true;
}

// Everything a caller needs to read the current page in one call.
function readPage(cfg, doc) {
  const c = cfg || DEFAULT_SELECTORS;
  const model = pageModel({
    questionContainers: c.questionContainers || DEFAULT_SELECTORS.questionContainers,
    nextButtons: c.nextButtons || DEFAULT_SELECTORS.nextButtons,
    terminalPatterns: c.terminalPatterns || DEFAULT_SELECTORS.terminalPatterns,
  }, doc);
  model.fingerprint = fingerprint(model);
  model.isTerminal = !model.next || (model.questions.length === 0 && !!model.outcome);
  return model;
}

globalThis.SPB_CORE = {
  DEFAULT_SELECTORS,
  pageModel,
  readPage,
  fingerprint,
  candidates,
  describe,
  applyAnswer,
  clickNext,
};

// Report rendering — shared by the CLI (report.mjs) and the Chrome extension's
// "Download report" button, so both produce the same Markdown.
//
// Plain script, no imports: it is loaded as a content/popup script in the
// extension and eval'd by lib/report-core.mjs in Node.

const esc = (s) => String(s ?? '').replace(/\|/g, '\\|').replace(/\n+/g, ' ').trim();
const trunc = (s, n) => (String(s ?? '').length > n ? String(s).slice(0, n - 1) + '…' : String(s ?? ''));
// djb2 — a stable id for a Mermaid node, without Buffer (this file runs in the
// browser too).
const nodeId = (fp) => {
  let h = 5381;
  for (const ch of String(fp)) h = ((h * 33) ^ ch.charCodeAt(0)) >>> 0;
  return 'N' + h.toString(16);
};

function buildReport(traces, summary = {}) {
  const L = [];
  L.push('# Survey pathway test report', '');
  if (summary.url) L.push(`Survey: \`${summary.url}\``);
  L.push(`Generated: ${summary.generatedAt ?? new Date().toISOString()}`);
  L.push(`Traversals: **${traces.length}**` + (summary.plansQueuedButNotRun ? `  ·  untried branches still queued: **${summary.plansQueuedButNotRun}**` : ''));
  L.push('');

  // --- outcomes -----------------------------------------------------------
  const byOutcome = new Map();
  for (const t of traces) {
    const k = t.outcome?.type ?? 'unknown';
    if (!byOutcome.has(k)) byOutcome.set(k, []);
    byOutcome.get(k).push(t);
  }
  L.push('## Outcomes', '');
  L.push('| Outcome | Runs | Example ending text |', '|---|---:|---|');
  for (const [k, list] of [...byOutcome.entries()].sort((a, b) => b[1].length - a[1].length)) {
    L.push(`| ${k} | ${list.length} | ${esc(trunc(list[0].outcome?.heading || list[0].outcome?.text, 90))} |`);
  }
  L.push('');

  // --- runs ---------------------------------------------------------------
  L.push('## Traversals', '');
  L.push('| Run | Pages | Outcome | Decisions taken |', '|---|---:|---|---|');
  for (const t of traces) {
    const path = t.decisions.map((d) => `${d.key}=${esc(trunc(d.chosen, 28))}`).join(' → ');
    L.push(`| ${t.runId} | ${t.steps.length} | ${t.outcome?.type ?? '?'} | ${esc(trunc(path, 240)) || '—'} |`);
  }
  L.push('');

  // --- flow graph ---------------------------------------------------------
  // Nodes are pages (identified by the questions they ask), edges are the
  // answers that moved the bot from one page to the next.
  const nodes = new Map();
  const edges = new Map();
  for (const t of traces) {
    for (let i = 0; i < t.steps.length; i++) {
      const s = t.steps[i];
      if (!nodes.has(s.fingerprint)) {
        const label = s.questionKeys.length
          ? s.questionKeys.join(', ')
          : trunc(s.outcome ? `${s.outcome.toUpperCase()}: ${s.heading}` : s.heading || 'page', 40);
        nodes.set(s.fingerprint, { label, questions: s.questionKeys, outcome: s.outcome, count: 0 });
      }
      nodes.get(s.fingerprint).count++;
      const nxt = t.steps[i + 1];
      if (!nxt) continue;
      const via = (s.decisions ?? [])
        .filter((d) => d.candidateCount > 1)
        .map((d) => `${d.key}=${trunc(d.chosen, 18)}`)
        .join(', ');
      const key = `${s.fingerprint}|${nxt.fingerprint}|${via}`;
      edges.set(key, (edges.get(key) ?? 0) + 1);
    }
  }
  L.push('## Pathway map', '');
  L.push('Nodes are pages (labelled with the questions they ask); edge labels are the answers that led there.', '');
  L.push('```mermaid', 'flowchart TD');
  for (const [fp, n] of nodes) {
    const shape = n.outcome ? ['([', '])'] : ['[', ']'];
    L.push(`  ${nodeId(fp)}${shape[0]}"${n.label.replace(/"/g, "'")}"${shape[1]}`);
  }
  for (const [key, count] of edges) {
    const [from, to, via] = key.split('|');
    const lbl = (via || '(no branching answer)') + (count > 1 ? ` ×${count}` : '');
    L.push(`  ${nodeId(from)} -->|"${lbl.replace(/"/g, "'")}"| ${nodeId(to)}`);
  }
  L.push('```', '');

  // --- coverage -----------------------------------------------------------
  // Every option the bot ever saw, and whether any run actually selected it.
  const qs = new Map(); // key -> {label, kind, options: Map<label, {seen, chosen}>}
  for (const t of traces) {
    for (const s of t.steps) {
      for (const q of s.questions ?? []) {
        if (!qs.has(q.key)) qs.set(q.key, { label: q.label, kind: q.kind, options: new Map() });
        const rec = qs.get(q.key);
        for (const o of q.options ?? []) {
          const k = o.label || o.value;
          if (!rec.options.has(k)) rec.options.set(k, { chosen: 0 });
        }
        // Leaving a standalone checkbox blank is a branch of its own.
        if (q.kind === 'checkbox' && (q.options ?? []).length === 1 && !rec.options.has('(left unchecked)'))
          rec.options.set('(left unchecked)', { chosen: 0 });
      }
      for (const d of s.decisions ?? []) {
        const rec = qs.get(d.key);
        if (!rec) continue;
        const lbl = String(d.chosen ?? '').replace(/\s*\[[^\]]*\]$/, '');
        for (const [k, v] of rec.options) {
          if (k === lbl || d.chosen?.includes(`[${k}]`)) { v.chosen++; break; }
        }
      }
    }
  }
  L.push('## Answer-option coverage', '');
  L.push('| Question | Type | Options | Exercised | Never selected |', '|---|---|---:|---:|---|');
  const untested = [];
  for (const [key, rec] of qs) {
    const total = rec.options.size;
    const hit = [...rec.options.values()].filter((v) => v.chosen > 0).length;
    const missed = [...rec.options.entries()].filter(([, v]) => v.chosen === 0).map(([k]) => k);
    if (total && missed.length) untested.push({ key, missed });
    L.push(
      `| \`${key}\` — ${esc(trunc(rec.label, 60))} | ${rec.kind} | ${total || '—'} | ${total ? hit : '—'} | ${esc(trunc(missed.join(', '), 80)) || '—'} |`
    );
  }
  L.push('');

  // --- findings -----------------------------------------------------------
  L.push('## Findings to check', '');
  const findings = [];
  for (const t of traces) {
    if (t.outcome?.type === 'stalled')
      findings.push(`**${t.runId} stalled** on page \`${t.outcome.atFingerprint}\` — the page did not advance after submitting. Message: ${esc(trunc(t.outcome.text, 200))}`);
    if (t.outcome?.type === 'error') findings.push(`**${t.runId} errored**: ${esc(trunc(t.outcome.text, 200))}`);
    if (t.outcome?.type === 'maxsteps') findings.push(`**${t.runId} hit the page limit** — possible loop, or a longer survey than \`maxSteps\` allows.`);
    for (const d of t.decisions) if (d.error) findings.push(`**${t.runId}**: could not answer \`${d.key}\` (${esc(d.error)}).`);
  }
  for (const u of untested) findings.push(`\`${u.key}\`: ${u.missed.length} option(s) never selected in any run — ${esc(trunc(u.missed.join(', '), 120))}. Raise \`--max-runs\` or target them with a scripted path.`);
  if (!findings.length) findings.push('None — every traversal reached an end state and every option was exercised.');
  for (const f of findings) L.push(`- ${f}`);
  L.push('');
  return L.join('\n');
}

globalThis.SPB_REPORT = { buildReport };

// Console API on top of the shared core — the zero-install way to run this.
//
// Three ways to use it, in order of preference:
//
//   spb.auto()   full automatic exploration, no install, no keystrokes. Loads
//                the survey in a same-origin iframe on the page you are already
//                on, so the parent page never navigates and this script keeps
//                running. Blocked only if the survey refuses to be framed.
//   spb.plan()   step-through exploration for when framing is blocked: it keeps
//                the run queue in sessionStorage, so re-running this snippet on
//                each page (DevTools ▸ Snippets ▸ Ctrl/Cmd+Enter) advances one
//                page and picks up exactly where it left off.
//   spb.inspect() / spb.fill() / spb.step() / spb.capture()
//                manual, one page at a time.
//
// Results from any mode: spb.report() prints Markdown, spb.download() saves it.

const C = globalThis.SPB_CORE;
const CAPTURE_KEY = 'spb-captured-answers';
const STEP_KEY = 'spb-step-state';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const escapeRe = (s) => String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const readJSON = (key, fallback) => {
  try {
    return JSON.parse(sessionStorage.getItem(key)) ?? fallback;
  } catch {
    return fallback;
  }
};
const writeJSON = (key, v) => {
  try {
    sessionStorage.setItem(key, JSON.stringify(v));
  } catch {}
};

// ---- breadth-first branch expansion (same rule as the CLI and extension) ----
function planKey(plan) {
  const p = [...plan];
  while (p.length && p[p.length - 1] === 0) p.pop(); // trailing zeros are implicit
  return p.join(',');
}

function expand(state, trace) {
  for (let i = 0; i < trace.decisions.length; i++) {
    const d = trace.decisions[i];
    if (!d || d.candidateCount <= 1) continue;
    const prefix = trace.decisions.slice(0, i).map((x) => x.chosenIndex ?? 0);
    for (let alt = 0; alt < d.candidateCount; alt++) {
      if (alt === d.chosenIndex) continue;
      const plan = [...prefix, alt];
      const key = planKey(plan);
      if (state.seen.includes(key)) continue;
      state.seen.push(key);
      state.queue.push(plan);
    }
  }
}

// Answer every question on `doc`, returning the page record.
function answerPage(model, plan, di, cfg, doc) {
  const record = {
    url: model.url,
    fingerprint: model.fingerprint,
    heading: model.heading,
    outcome: model.outcome,
    questionKeys: model.questions.map((q) => q.key),
    questions: model.questions.map((q) => ({
      key: q.key,
      kind: q.kind,
      label: q.label,
      options: q.options.map((o) => ({ value: o.value, label: o.label })),
    })),
    decisions: [],
  };
  for (const q of model.questions) {
    const cands = C.candidates(q, cfg);
    const wanted = plan[di];
    const idx = Number.isInteger(wanted) && wanted < cands.length ? wanted : 0;
    const chosen = cands[idx];
    const ok = C.applyAnswer(q, chosen, doc);
    record.decisions.push({
      di,
      key: q.key,
      kind: q.kind,
      label: q.label,
      candidateCount: cands.length,
      chosenIndex: idx,
      chosen: C.describe(q, chosen),
      error: ok ? undefined : 'could not set answer',
    });
    di++;
  }
  return { record, di };
}

function makeTrace(runId, plan, steps, decisions, type, text) {
  const last = steps[steps.length - 1] || {};
  return {
    runId,
    plan,
    steps: steps.map((s, i) => ({ step: i, ...s })),
    decisions,
    outcome: {
      type,
      heading: last.heading || '',
      text: text || '',
      url: last.url || '',
      atFingerprint: type === 'stalled' ? last.fingerprint : undefined,
    },
    pathKey: decisions.map((d) => `${d.key}=${d.chosenIndex}`).join('>'),
    pageKey: steps.map((s) => s.fingerprint).join('>'),
  };
}

const spb = {
  core: C,
  config: {},
  traces: [],

  help() {
    console.log(`spb.auto({ maxRuns: 20 })   explore every pathway automatically (iframe mode)
spb.plan({ maxRuns: 20 })   step-through mode: re-run this snippet on each page
spb.status()                where the current exploration is up to
spb.report()                print the Markdown report   ·  spb.download() saves it
spb.inspect()               what the bot sees on this page
spb.fill({ S1: 2 })         answer this page  ·  spb.step() answer + Next
spb.capture()               record answers you picked  ·  spb.scenario('name') export them
spb.reset()                 clear stored state`);
  },

  // ---- automatic mode ------------------------------------------------------
  async auto(opts = {}) {
    const startUrl = opts.url || location.href;
    const maxRuns = opts.maxRuns ?? 20;
    const cfg = { ...this.config, ...(opts.config || {}) };
    const delay = Number(cfg.delay ?? 300);
    const timeout = Number(cfg.stepTimeout ?? 20000);
    const maxSteps = Number(cfg.maxSteps ?? 60);

    const frame = document.createElement('iframe');
    frame.setAttribute('sandbox', 'allow-forms allow-scripts allow-same-origin');
    frame.style.cssText =
      'position:fixed;right:12px;bottom:12px;width:460px;height:620px;z-index:2147483647;' +
      'border:2px solid #333;border-radius:6px;background:#fff;box-shadow:0 8px 30px rgba(0,0,0,.35)';
    document.body.appendChild(frame);
    this._frame = frame;

    const load = (url) =>
      new Promise((resolve, reject) => {
        const t = setTimeout(() => reject(new Error('iframe load timed out')), timeout);
        frame.onload = () => {
          clearTimeout(t);
          resolve();
        };
        frame.src = url;
      });

    const docOf = () => {
      const d = frame.contentDocument;
      if (!d) throw new Error('framing blocked');
      return d;
    };

    try {
      await load(startUrl);
      docOf().querySelector('body');
    } catch (e) {
      frame.remove();
      console.error(
        `Could not drive the survey in an iframe (${e.message}). The survey refuses to be framed — ` +
          `use step-through mode instead:  spb.plan({ maxRuns: 20 })`
      );
      return null;
    }

    const state = { queue: [[]], seen: [''], traces: [] };
    let runs = 0;
    while (state.queue.length && runs < maxRuns) {
      const plan = state.queue.shift();
      const runId = `run-${String(++runs).padStart(3, '0')}`;
      const steps = [];
      const decisions = [];
      let di = 0;
      let type = 'maxsteps';
      let text = '';

      try {
        if (runs > 1) await load(startUrl);
        for (let step = 0; step < maxSteps; step++) {
          const doc = docOf();
          const model = C.readPage(cfg.selectors, doc);
          if (model.isTerminal) {
            steps.push({
              url: model.url, fingerprint: model.fingerprint, heading: model.heading, outcome: model.outcome,
              questionKeys: [], questions: [], decisions: [],
            });
            type = model.outcome || 'end';
            text = model.bodyText.slice(0, 600);
            break;
          }
          const answered = answerPage(model, plan, di, cfg, doc);
          di = answered.di;
          steps.push(answered.record);
          decisions.push(...answered.record.decisions);

          await sleep(delay);
          const before = model.fingerprint + '|' + model.url;
          C.clickNext(model, doc);
          const deadline = Date.now() + timeout;
          let moved = false;
          while (Date.now() < deadline) {
            await sleep(200);
            try {
              const m = C.readPage(cfg.selectors, docOf());
              if (m.fingerprint + '|' + m.url !== before) {
                moved = true;
                break;
              }
            } catch {
              /* mid-navigation */
            }
          }
          if (!moved) {
            type = 'stalled';
            try {
              const now = C.readPage(cfg.selectors, docOf());
              text = (now.bodyText.match(/[^.]*(required|please|must|error|invalid)[^.]*\./i) || [
                'page did not advance after submitting',
              ])[0];
            } catch {
              text = 'page did not advance after submitting';
            }
            break;
          }
        }
      } catch (e) {
        type = e.message === 'framing blocked' ? 'left-origin' : 'error';
        text = e.message;
      }

      const trace = makeTrace(runId, plan, steps, decisions, type, text);
      state.traces.push(trace);
      expand(state, trace);
      console.log(
        `${runId}  plan=[${plan.join(',')}]  pages=${trace.steps.length}  outcome=${type}  ` +
          `${trace.decisions.map((d) => `${d.key}:${d.chosenIndex}`).join(' > ')}`
      );
    }

    this.traces = state.traces;
    this._summary = { url: startUrl, generatedAt: new Date().toISOString(), plansQueuedButNotRun: state.queue.length };
    frame.remove();
    console.log(
      `%cdone — ${state.traces.length} traversal(s), ${state.queue.length} branch(es) untried. spb.report() / spb.download()`,
      'font-weight:bold'
    );
    return state.traces;
  },

  // ---- step-through mode ---------------------------------------------------
  plan(opts = {}) {
    const state = {
      active: true,
      startUrl: opts.url || location.href,
      cfg: { ...this.config, ...(opts.config || {}) },
      maxRuns: opts.maxRuns ?? 20,
      maxSteps: opts.maxSteps ?? 60,
      queue: [[]],
      seen: [''],
      traces: [],
      runs: 0,
      current: null,
    };
    writeJSON(STEP_KEY, state);
    console.log('step mode armed. Re-run this snippet (Ctrl/Cmd+Enter) on each page; it advances one page per run.');
    return this.go();
  },

  go() {
    const state = readJSON(STEP_KEY, null);
    if (!state || !state.active) {
      console.log('step mode is not armed — run spb.plan() first.');
      return null;
    }

    const startNext = () => {
      if (state.runs >= state.maxRuns || !state.queue.length) {
        state.active = false;
        writeJSON(STEP_KEY, state);
        this.traces = state.traces;
        this._summary = { url: state.startUrl, generatedAt: new Date().toISOString(), plansQueuedButNotRun: state.queue.length };
        console.log(
          `%cdone — ${state.traces.length} traversal(s), ${state.queue.length} branch(es) untried. spb.report() / spb.download()`,
          'font-weight:bold'
        );
        return null;
      }
      const plan = state.queue.shift();
      state.runs += 1;
      state.current = { runId: `run-${String(state.runs).padStart(3, '0')}`, plan, di: 0, steps: [], decisions: [] };
      writeJSON(STEP_KEY, state);
      console.log(`starting ${state.current.runId} plan=[${plan.join(',')}] — reloading the survey…`);
      location.href = state.startUrl;
      return null;
    };

    if (!state.current) return startNext();

    const cfg = state.cfg;
    const model = C.readPage(cfg.selectors);
    const c = state.current;

    if (model.isTerminal) {
      c.steps.push({ url: model.url, fingerprint: model.fingerprint, heading: model.heading, outcome: model.outcome, questionKeys: [], questions: [], decisions: [] });
      const trace = makeTrace(c.runId, c.plan, c.steps, c.decisions, model.outcome || 'end', model.bodyText.slice(0, 600));
      state.traces.push(trace);
      expand(state, trace);
      state.current = null;
      writeJSON(STEP_KEY, state);
      console.log(`${trace.runId} finished: ${trace.outcome.type} after ${trace.steps.length} page(s)`);
      return startNext();
    }

    if (c.steps.length >= state.maxSteps) {
      const trace = makeTrace(c.runId, c.plan, c.steps, c.decisions, 'maxsteps', `stopped after ${state.maxSteps} pages`);
      state.traces.push(trace);
      expand(state, trace);
      state.current = null;
      writeJSON(STEP_KEY, state);
      return startNext();
    }

    const answered = answerPage(model, c.plan, c.di, cfg, document);
    c.di = answered.di;
    c.steps.push(answered.record);
    c.decisions.push(...answered.record.decisions);
    writeJSON(STEP_KEY, state);
    console.table(Object.fromEntries(answered.record.decisions.map((d) => [d.key, d.chosen])));
    C.clickNext(model);
    console.log(`${c.runId} · page ${c.steps.length} answered — press Ctrl/Cmd+Enter again on the next page.`);
    return answered.record;
  },

  status() {
    const state = readJSON(STEP_KEY, null);
    if (state?.active) {
      console.log(
        `step mode: ${state.runs} run(s) started, ${state.traces.length} finished, ${state.queue.length} queued` +
          (state.current ? `, currently ${state.current.runId} on page ${state.current.steps.length + 1}` : '')
      );
      return state;
    }
    console.log(`${this.traces.length} traversal(s) recorded in this tab.`);
    return { traces: this.traces };
  },

  allTraces() {
    const state = readJSON(STEP_KEY, null);
    return this.traces.length ? this.traces : state?.traces ?? [];
  },

  report() {
    const traces = this.allTraces();
    if (!traces.length) return console.log('no traversals recorded yet.');
    const md = globalThis.SPB_REPORT.buildReport(traces, this._summary || { url: location.href, generatedAt: new Date().toISOString() });
    console.log(md);
    return md;
  },

  download(name = 'survey-pathway-REPORT.md') {
    const md = this.report();
    if (!md) return;
    const url = URL.createObjectURL(new Blob([md], { type: 'text/markdown' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
    console.log(`saved ${name}`);
  },

  reset() {
    writeJSON(STEP_KEY, null);
    writeJSON(CAPTURE_KEY, []);
    this.traces = [];
    console.log('cleared');
  },

  // ---- manual, one page at a time -----------------------------------------
  inspect() {
    const m = C.readPage(this.config.selectors);
    console.log(`%c${m.heading || document.title}`, 'font-weight:bold');
    console.log(`page id: ${m.fingerprint}   next: ${m.next ? m.next.selector : 'none'}   end state: ${m.outcome || '—'}`);
    console.table(
      m.questions.map((q) => ({
        name: q.key,
        type: q.kind,
        question: (q.label || '').slice(0, 60),
        options: q.options.length || '',
        labels: q.options.map((o) => o.label).join(' | ').slice(0, 80),
        branches: C.candidates(q, this.config).length,
      }))
    );
    return m;
  },

  // spb.fill({ S1: 2 })            option index
  // spb.fill({ S1: /55 or older/ }) first option whose label or value matches
  // spb.fill({ Q3: 'some text' })   text answer
  fill(overrides = {}) {
    const m = C.readPage(this.config.selectors);
    const chosen = {};
    for (const q of m.questions) {
      const cands = C.candidates(q, this.config);
      let pick = cands[0];
      const o = overrides[q.key];
      if (o != null) {
        if (typeof o === 'number') pick = cands[o] || pick;
        else if (o instanceof RegExp) pick = cands.find((c) => o.test(c.label || '') || o.test(c.value || '')) || pick;
        else pick = { kind: 'value', value: String(o) };
      }
      C.applyAnswer(q, pick);
      chosen[q.key] = C.describe(q, pick);
    }
    console.table(chosen);
    return chosen;
  },

  next() {
    return C.clickNext(C.readPage(this.config.selectors));
  },

  step(overrides) {
    const chosen = this.fill(overrides);
    this.next();
    return chosen;
  },

  // Record the answers currently selected, so a pathway walked by hand can
  // become a scripted test.
  capture() {
    const m = C.readPage(this.config.selectors);
    const answers = [];
    for (const q of m.questions) {
      const el = document.querySelector(q.selector);
      if (q.kind === 'radio' || q.kind === 'checkbox') {
        for (const o of q.options) {
          const input = document.querySelector(o.selector);
          if (input && input.checked) answers.push({ match: `^${q.key}$`, fixed: escapeRe(o.label || o.value) });
        }
      } else if (q.kind === 'select') {
        const opt = q.options.find((o) => o.value === (el && el.value));
        if (opt) answers.push({ match: `^${q.key}$`, fixed: escapeRe(opt.label || opt.value) });
      } else if (el && el.value) {
        answers.push({ match: `^${q.key}$`, value: el.value });
      }
    }
    const all = readJSON(CAPTURE_KEY, []);
    all.push({ url: location.href, fingerprint: m.fingerprint, answers });
    writeJSON(CAPTURE_KEY, all);
    console.log(`captured ${answers.length} answer(s) on ${m.fingerprint} (${all.length} page(s) so far)`);
    return answers;
  },

  scenario(name = 'Captured pathway') {
    const all = readJSON(CAPTURE_KEY, []);
    const out = { name, answers: all.flatMap((p) => p.answers), expect: { outcome: 'complete' }, _pages: all.map((p) => p.fingerprint) };
    console.log(JSON.stringify(out, null, 2));
    return out;
  },
};

globalThis.spb = spb;

// Re-running the snippet while step mode is armed advances the run, so the
// whole loop is one keystroke per page.
const stepState = readJSON(STEP_KEY, null);
if (stepState && stepState.active) {
  console.log('%csurvey pathway bot — step mode active', 'font-weight:bold');
  spb.go();
} else {
  console.log('%csurvey pathway bot loaded', 'font-weight:bold');
  console.log('spb.auto()  explore everything automatically   ·   spb.help()  all commands');
}

})();
