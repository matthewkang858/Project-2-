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

  // Survey players routinely hide the real control (opacity:0, a 1px box, or
  // clipped off-screen) and style a label in its place. The question is on
  // screen and answerable through that input, so a control counts as present
  // when either it or the label standing in for it is visible.
  const answerable = (el) => {
    if (visible(el)) return true;
    const host = el.closest('label, .answer, .option, .choice, [class*="option"], [class*="answer"], li, td');
    return !!host && visible(host);
  };

  const controls = [...doc.querySelectorAll('input, select, textarea')].filter((el) => {
    const type = (el.type || '').toLowerCase();
    if (['hidden', 'submit', 'button', 'image', 'reset', 'file'].includes(type)) return false;
    if (el.disabled) return false;
    return answerable(el);
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
    else if (type === 'range') kind = 'slider';
    else if (type === 'number') kind = 'number';
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
    if (kind === 'slider')
      q.range = {
        min: Number(first.min === '' ? 0 : first.min),
        max: Number(first.max === '' ? 100 : first.max),
        step: Number(first.step || 1),
      };

    // Whether the respondent (or the bot) has already answered it — used to
    // avoid re-answering questions that stay on screen as a carousel reveals
    // more, and to explain validation stalls.
    q.answered =
      kind === 'radio' || kind === 'checkbox'
        ? els.some((e) => e.checked)
        : kind === 'select'
          ? !!first.value
          : String(first.value ?? '') !== '';

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

  // Sliders that are not <input type=range>: a focusable element carrying the
  // slider role and aria-value* attributes, driven by keyboard or drag. They
  // hold no form control, so the grouping above cannot see them.
  for (const el of doc.querySelectorAll('[role="slider"]')) {
    if (!visible(el) || el.tagName === 'INPUT') continue;
    const stemSink = {};
    const key = el.id || el.getAttribute('aria-label') || cssFor(el);
    if (questions.some((q) => q.key === key)) continue;
    questions.push({
      key,
      kind: 'slider',
      label: questionLabel(el, stemSink),
      required: el.getAttribute('aria-required') === 'true',
      selector: cssFor(el),
      emphasis: marksOf(stemSink.el),
      aria: true,
      answered: Number(el.getAttribute('aria-valuenow') ?? 0) !== Number(el.getAttribute('aria-valuemin') ?? 0),
      range: {
        min: Number(el.getAttribute('aria-valuemin') ?? 0),
        max: Number(el.getAttribute('aria-valuemax') ?? 100),
        step: Number(el.getAttribute('aria-valuestep') || 1),
        now: Number(el.getAttribute('aria-valuenow') ?? 0),
      },
      options: [],
    });
  }

  // Forward button. Selector matches first (precise), then anything that reads
  // like a forward control — modern survey players render a plain
  // <button>Continue</button> that matches none of the classic selectors, and
  // mistaking that for "no way forward" ends the run on the welcome page.
  let next = null;
  for (const sel of cfg.nextButtons) {
    const el = [...doc.querySelectorAll(sel)].find((e) => visible(e) && !e.disabled);
    if (el) {
      next = { selector: cssFor(el), label: clean(el.innerText || el.value || ''), matched: sel };
      break;
    }
  }
  if (!next) {
    const forward = cfg.nextText ? new RegExp(cfg.nextText, 'i') : /^(continue|next|start|begin|proceed|submit|go on|ok|done|→|»|>>)\b/i;
    const backward = /^(back|previous|prev|return|cancel|exit|«|<<)\b/i;
    const clickable = [...doc.querySelectorAll('button, input[type="button"], input[type="submit"], a[role="button"], a.btn, [role="button"], .button, .btn')];
    const el = clickable.find((e) => {
      if (!visible(e) || e.disabled) return false;
      const label = clean(e.innerText || e.value || e.getAttribute('aria-label') || '');
      return label && forward.test(label) && !backward.test(label);
    });
    if (el) next = { selector: cssFor(el), label: clean(el.innerText || el.value || ''), matched: 'text' };
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

  if (q.kind === 'slider') {
    const { min = 0, max = 100, step = 1 } = q.range || {};
    const at = (fraction) => {
      const raw = min + (max - min) * fraction;
      return String(Math.round(raw / step) * step);
    };
    if (rule?.values?.length) return rule.values.map((v) => ({ kind: 'slide', value: String(v) }));
    if (rule?.value != null) return [{ kind: 'slide', value: String(rule.value) }];
    const wanted = config.sliderValues ?? ['mid'];
    const points = { min: at(0), low: at(0.25), mid: at(0.5), high: at(0.75), max: at(1) };
    return wanted.map((w) => ({ kind: 'slide', value: points[w] ?? String(w) }));
  }

  // Free-text style.
  if (rule?.values?.length) return rule.values.map((v) => ({ kind: 'value', value: String(v) }));
  if (rule?.value != null) return [{ kind: 'value', value: String(rule.value) }];
  const fallback = config.values?.[q.kind] ?? DEFAULT_VALUES[q.kind] ?? 'Test';
  return [{ kind: 'value', value: String(fallback) }];
}

function describe(q, candidate) {
  if (candidate.kind === 'slide') return `slider → ${candidate.value}`;
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
  if (candidate.kind === 'slide') {
    const el = doc.querySelector(q.selector);
    if (!el) return false;
    const target = Number(candidate.value);
    el.focus?.();
    if (!q.aria) {
      el.value = String(target);
      fire(el, ['input', 'change']);
      return Number(el.value) === target;
    }
    // A custom slider: nudge it with the arrow keys it listens for, then fall
    // back to a drag to the right spot on its track.
    const now = () => Number(el.getAttribute('aria-valuenow') ?? 0);
    const { min = 0, max = 100, step = 1 } = q.range || {};
    const key = (name) => {
      for (const type of ['keydown', 'keyup'])
        el.dispatchEvent(new win.KeyboardEvent(type, { key: name, bubbles: true }));
    };
    for (let i = 0; i < Math.abs(max - min) / step + 2 && now() !== target; i++)
      key(now() < target ? 'ArrowRight' : 'ArrowLeft');
    if (now() === target) return true;
    const box = el.getBoundingClientRect();
    const x = box.left + (box.width * (target - min)) / (max - min || 1);
    const y = box.top + box.height / 2;
    for (const type of ['mousedown', 'mousemove', 'mouseup'])
      el.dispatchEvent(new win.MouseEvent(type, { clientX: x, clientY: y, bubbles: true }));
    return now() === target;
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
  // With a hidden input the player listens on the styled label, so click that
  // first and only fall back to forcing the input's state.
  const box = el.getBoundingClientRect();
  const hidden = box.width <= 2 || box.height <= 2 || (doc.defaultView || window).getComputedStyle(el).opacity === '0';
  const label = hidden
    ? (el.id && doc.querySelector(`label[for="${CSS.escape(el.id)}"]`)) || el.closest('label')
    : null;
  if (label) label.click();
  if (!el.checked) el.click();
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
//
// Survey players often render the questionnaire inside an iframe on the host
// page. When the document handed in holds neither questions nor a way forward,
// the same-origin frames below it are searched, and `docPath` records the route
// so answers land in the right document.
function readPage(cfg, doc, depth) {
  const c = cfg || DEFAULT_SELECTORS;
  const root = doc || document;
  const model = pageModel({
    questionContainers: c.questionContainers || DEFAULT_SELECTORS.questionContainers,
    nextButtons: c.nextButtons || DEFAULT_SELECTORS.nextButtons,
    terminalPatterns: c.terminalPatterns || DEFAULT_SELECTORS.terminalPatterns,
    nextText: c.nextText,
  }, root);
  model.docPath = [];

  const empty = !model.questions.length && !model.next;
  if (empty && (depth || 0) < 3) {
    const frames = [...root.querySelectorAll('iframe, frame')];
    let fallback = null; // the frame with the most text, for end-state detection
    for (let i = 0; i < frames.length; i++) {
      let inner;
      try {
        inner = frames[i].contentDocument;
      } catch {
        continue; // cross-origin
      }
      if (!inner || !inner.body) continue;
      const selector = frames[i].id ? `#${CSS.escape(frames[i].id)}` : `iframe:nth-of-type(${i + 1})`;
      const sub = readPage(c, inner, (depth || 0) + 1);
      sub.docPath = [selector, ...sub.docPath];
      if (sub.questions.length || sub.next) return sub;
      if (!fallback || sub.bodyText.length > fallback.bodyText.length) fallback = sub;
    }
    // The questionnaire ends inside the frame too: without this the "thank you"
    // or screen-out text would be invisible and every run would end as "end".
    if (fallback && fallback.bodyText.length > model.bodyText.length) return fallback;
  }

  model.fingerprint = fingerprint(model);
  // Terminal means "nothing left to do here": no questions and no way forward.
  // A page with unanswered questions but no visible button is a carousel or a
  // validation state, not the end of the survey.
  model.isTerminal = !model.next && !model.questions.length;
  model.needsAnswerFirst = !model.next && model.questions.length > 0;
  if (model.isTerminal && !model.outcome) model.stuck = true;
  return model;
}

// The document a model's selectors belong to.
function docFor(model, root) {
  let d = root || document;
  for (const sel of model.docPath || []) {
    const frame = d.querySelector(sel);
    let inner = null;
    try {
      inner = frame && frame.contentDocument;
    } catch {
      inner = null;
    }
    if (!inner) return d;
    d = inner;
  }
  return d;
}

globalThis.SPB_CORE = {
  DEFAULT_SELECTORS,
  pageModel,
  readPage,
  docFor,
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
    const manual = (t.steps ?? []).filter((s) => s.manual);
    if (manual.length)
      findings.push(`**${t.runId} needed a hand** on ${manual.length} page(s) — ${manual.map((s) => `\`${s.fingerprint}\`${s.manualReason ? ` (${esc(trunc(s.manualReason, 60))})` : ''}`).join(', ')}. Those widgets (sliders, carousels, custom controls) are worth teaching the bot, or scripting with a \`fixed\` rule.`);
    if (t.outcome?.type === 'stuck')
      findings.push(`**${t.runId} got stuck** on \`${t.outcome.atFingerprint ?? '?'}\` — the page was answered but offered no way forward. ${esc(trunc(t.outcome.text, 160))}`);
    if (t.outcome?.type === 'stopped')
      findings.push(`**${t.runId} was stopped by hand** — the report covers the traversals completed before that.`);
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
const AUTO_KEY = 'spb-auto-traces';

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
function answerPage(model, plan, di, cfg, doc, answered) {
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
    // A carousel keeps answered cards on screen; re-answering them would
    // consume plan slots and skew the branch numbering.
    if (answered && answered.has(q.key) && q.answered) continue;
    const cands = C.candidates(q, cfg);
    const wanted = plan[di];
    const idx = Number.isInteger(wanted) && wanted < cands.length ? wanted : 0;
    const chosen = cands[idx];
    const ok = C.applyAnswer(q, chosen, doc);
    if (answered) answered.add(q.key);
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
    console.log(`spb.check()                 is this page the survey, and can it be framed?
spb.auto({ maxRuns: 20 })   explore every pathway automatically (iframe mode)
spb.plan({ maxRuns: 20 })   step-through mode: re-run this snippet on each page
spb.stop()                  end the run now and keep what was recorded
spb.debug()                 what the bot can and cannot see on this page
spb.status()                where the current exploration is up to
spb.report()                print the Markdown report   ·  spb.download() saves it
spb.inspect()               what the bot sees on this page
spb.fill({ S1: 2 })         answer this page  ·  spb.step() answer + Next
spb.capture()               record answers you picked  ·  spb.scenario('name') export them
spb.reset()                 clear stored state`);
  },

  // Preflight: is this page the survey, can it be framed, and does the
  // questionnaire actually render once you click past the welcome page?
  async check(opts = {}) {
    const url = opts.url || location.href;
    const here = C.readPage(this.config.selectors);
    console.log(`%cpage: ${location.href}`, 'font-weight:bold');
    console.log(
      `  questions found: ${here.questions.length}   forward button: ${here.next ? `yes ("${here.next.label}")` : 'no'}   end state: ${here.outcome || '—'}`
    );
    if (here.docPath?.length) console.log(`  (the survey is inside an iframe: ${here.docPath.join(' > ')})`);
    if (!here.questions.length && here.next)
      console.log('  this is a welcome / intro page — no questions yet, but there is a way forward. That is fine: spb.auto() clicks through it.');
    if (!here.questions.length && !here.next)
      console.warn(
        /log ?in|sign ?in|password|not authorized|session expired/i.test(here.bodyText.slice(0, 400))
          ? '  ⚠ no questions and no way forward, and the page mentions signing in — log in first, then reopen the survey link.'
          : '  ⚠ no questions and no way forward on this page.'
      );

    const frame = document.createElement('iframe');
    frame.setAttribute('sandbox', 'allow-forms allow-scripts allow-same-origin');
    frame.style.cssText = 'position:fixed;left:-9999px;width:900px;height:700px';
    document.body.appendChild(frame);
    const load = (target) =>
      new Promise((resolve) => {
        const timer = setTimeout(() => resolve(false), 15000);
        frame.onload = () => { clearTimeout(timer); resolve(true); };
        frame.src = target;
      });
    const read = () => {
      try {
        return frame.contentDocument ? C.readPage(this.config.selectors, frame.contentDocument) : null;
      } catch {
        return null;
      }
    };

    const ok = await load(url);
    let inner = ok ? read() : null;
    if (!inner) {
      frame.remove();
      console.warn(`  ⚠ ${url} cannot be driven in an iframe (the host refuses framing) — use step mode: spb.plan()`);
      return { page: here, frame: null };
    }
    console.log(`  iframe of ${url}: ${inner.questions.length} question(s), forward button: ${inner.next ? 'yes' : 'no'}`);

    // Click through up to three question-free pages, so the check reports on
    // the first real question rather than on the welcome screen.
    let clicked = 0;
    while (inner && !inner.questions.length && inner.next && clicked < 3) {
      const before = inner.fingerprint + '|' + inner.url;
      C.clickNext(inner, C.docFor(inner, frame.contentDocument));
      clicked++;
      const deadline = Date.now() + 15000;
      let moved = null;
      while (Date.now() < deadline) {
        await sleep(300);
        const now = read();
        if (now && now.fingerprint + '|' + now.url !== before) { moved = now; break; }
      }
      inner = moved ?? inner;
      if (!moved) break;
      console.log(`  after clicking "${'forward'}" (${clicked}): ${inner.questions.length} question(s) — ${(inner.heading || inner.bodyText.slice(0, 60)).slice(0, 70)}`);
    }
    frame.remove();

    if (inner && inner.questions.length) {
      console.log('%c  ready — run spb.auto({ maxRuns: 20 })', 'font-weight:bold');
      console.table(
        inner.questions.map((q) => ({ name: q.key, type: q.kind, question: (q.label || '').slice(0, 60), options: q.options.length }))
      );
    } else if (inner) {
      console.warn('  ⚠ clicked forward but still no questions — the survey may need a login, or the link may not start at page one.');
    }
    return { page: here, frame: inner };
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
    this._lastFrame = frame;

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

    let first = C.readPage(cfg.selectors, docOf());
    const firstSettle = Date.now() + Number(cfg.settleTimeout ?? 4000);
    while (first.stuck && !first.next && Date.now() < firstSettle) {
      await sleep(300);
      first = C.readPage(cfg.selectors, docOf());
    }
    // A welcome page legitimately has no questions — what matters is whether
    // there is any way forward from it.
    if (!first.questions.length && !first.next) {
      frame.remove();
      const wall = /log ?in|sign ?in|password|testing options|not authorized|session/i.test(first.bodyText.slice(0, 400));
      console.error(
        `%cnothing to work with at ${startUrl} — no questions and no way forward.` +
          (wall ? ' The page looks like a login / interstitial wall: sign in first, open the survey so its first question is on screen, then run spb.auto() again.' : ' Check the start URL is the first page of the survey.'),
        'font-weight:bold'
      );
      console.log('Run spb.check() for details.');
      return null;
    }

    const state = { queue: [[]], seen: [''], traces: [] };
    let runs = 0;
    this._abort = false;
    while (state.queue.length && runs < maxRuns && !this._abort) {
      const plan = state.queue.shift();
      const runId = `run-${String(++runs).padStart(3, '0')}`;
      const steps = [];
      const decisions = [];
      let di = 0;
      let type = 'maxsteps';
      let text = '';

      try {
        if (runs > 1) await load(startUrl);
        const answered = new Set();
        for (let step = 0; step < maxSteps; step++) {
          if (this._abort) { type = 'stopped'; text = 'stopped by spb.stop()'; break; }
          const doc = docOf();
          let model = C.readPage(cfg.selectors, doc);
          // A player that fetches its question body after the page loads looks
          // empty for a moment; give it a beat before calling the survey over.
          const full = Number(cfg.settleTimeout ?? 4000);
          const settleUntil = Date.now() + (model.stuck ? full : Math.min(full, 2000));
          while (!model.questions.length && Date.now() < settleUntil) {
            await sleep(250);
            model = C.readPage(cfg.selectors, docOf());
          }
          if (model.isTerminal) {
            steps.push({
              url: model.url, fingerprint: model.fingerprint, heading: model.heading, outcome: model.outcome,
              questionKeys: [], questions: [], decisions: [],
            });
            type = model.outcome || (model.stuck ? 'stuck' : 'end');
            text = model.bodyText.slice(0, 600);
            break;
          }
          const target = C.docFor(model, doc);
          const ans = answerPage(model, plan, di, cfg, target, answered);
          di = ans.di;
          steps.push(ans.record);
          decisions.push(...ans.record.decisions);
          await sleep(delay);

          // Answering can move the survey on by itself — a carousel revealing
          // its next card, or a page that advances on the last answer. Re-read
          // before clicking, or the click skips a card.
          let current = model;
          if (model.questions.length) {
            const after = C.readPage(cfg.selectors, docOf());
            if (after.fingerprint !== model.fingerprint) continue;
            current = after;
          }

          if (!current.next) {
            const helped = await this._waitForHuman(frame, current, cfg, 'this page has no forward button the bot can find');
            if (helped) { ans.record.manual = true; continue; }
            type = 'stuck';
            text = 'answered the page but found no way forward';
            break;
          }

          const before = current.fingerprint + '|' + current.url;
          C.clickNext(current, C.docFor(current, docOf()));
          const deadline = Date.now() + timeout;
          let moved = false;
          while (Date.now() < deadline) {
            await sleep(200);
            try {
              const m = C.readPage(cfg.selectors, docOf());
              if (m.fingerprint + '|' + m.url !== before) { moved = true; break; }
            } catch {
              /* mid-navigation */
            }
          }
          if (!moved) {
            let why = 'the page did not advance';
            try {
              const now = C.readPage(cfg.selectors, docOf());
              why = (now.bodyText.match(/[^.]*(required|please|must|error|invalid)[^.]*\./i) || [why])[0];
            } catch {}
            const helped = await this._waitForHuman(frame, current, cfg, why);
            if (helped) { ans.record.manual = true; continue; }
            type = 'stalled';
            text = why;
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
      // Keep the report available at all times: stopping the run, or losing the
      // tab, should never cost the traversals already walked.
      this.traces = state.traces;
      this._summary = { url: startUrl, generatedAt: new Date().toISOString(), plansQueuedButNotRun: state.queue.length };
      writeJSON(AUTO_KEY, { summary: this._summary, traces: state.traces });
      console.log(
        `${runId}  plan=[${plan.join(',')}]  pages=${trace.steps.length}  outcome=${type}  ` +
          `${trace.decisions.map((d) => `${d.key}:${d.chosenIndex}`).join(' > ')}`
      );
    }

    this.traces = state.traces;
    this._summary = { url: startUrl, generatedAt: new Date().toISOString(), plansQueuedButNotRun: state.queue.length };
    frame.remove();
    if (this._abort) console.log(`%cstopped after ${state.traces.length} traversal(s).`, 'font-weight:bold');
    if (!state.traces.some((t) => t.decisions.length)) {
      console.error(
        '%cno questions were answered in any run — the report would be empty. The bot never reached the questionnaire.',
        'font-weight:bold'
      );
      return state.traces;
    }
    console.log(
      `%cdone — ${state.traces.length} traversal(s), ${state.queue.length} branch(es) untried. spb.report() / spb.download()`,
      'font-weight:bold'
    );
    return state.traces;
  },

  // Hand the wheel to the user for a widget the bot cannot drive — a drag-only
  // slider, a carousel with custom controls, anything unexpected. The frame is
  // enlarged so the page is actually usable, and the run resumes the moment the
  // page moves.
  async _waitForHuman(frame, model, cfg, why) {
    const wait = Number(cfg.manualTimeout ?? 120000);
    if (!wait) return null;
    const before = model.fingerprint + '|' + model.url;
    const style = frame.style.cssText;
    frame.style.cssText =
      'position:fixed;right:12px;bottom:12px;width:min(900px,92vw);height:min(760px,86vh);z-index:2147483647;' +
      'border:3px solid #d97706;border-radius:6px;background:#fff;box-shadow:0 8px 40px rgba(0,0,0,.45)';
    console.warn(
      `%c⏸ over to you (${Math.round(wait / 1000)}s): ${why}\n` +
        `   page: ${model.heading || model.url}\n` +
        `   answer it in the panel and move to the next page — the run continues by itself.`,
      'font-weight:bold'
    );
    const deadline = Date.now() + wait;
    while (Date.now() < deadline) {
      await sleep(500);
      if (this._abort) break;
      let now = null;
      try {
        now = C.readPage(cfg.selectors, frame.contentDocument);
      } catch {
        /* navigating */
      }
      if (now && now.fingerprint + '|' + now.url !== before) {
        frame.style.cssText = style;
        console.log('%c▶ thanks — carrying on.', 'font-weight:bold');
        this._manualAssists = (this._manualAssists || 0) + 1;
        return now;
      }
    }
    frame.style.cssText = style;
    return null;
  },

  // What the bot can and cannot see on a page — paste the output when a survey
  // page defeats it.
  debug(doc) {
    let framed = null;
    try {
      framed = this._lastFrame && this._lastFrame.contentDocument;
    } catch {
      framed = null;
    }
    const d = doc || framed || document;
    const win = d.defaultView || window;
    const vis = (el) => {
      const r = el.getBoundingClientRect();
      const s = win.getComputedStyle(el);
      return s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0' && (r.width > 0 || r.height > 0);
    };
    const controls = [...d.querySelectorAll('input, select, textarea')];
    const model = C.readPage(this.config.selectors, d);
    const out = {
      url: d.location?.href,
      title: d.title,
      heading: model.heading,
      questionsDetected: model.questions.length,
      forwardButton: model.next ? `${model.next.label} (${model.next.matched})` : 'none',
      insideIframe: model.docPath?.length ? model.docPath.join(' > ') : 'no',
      iframes: [...d.querySelectorAll('iframe')].map((f) => {
        let same = false;
        try { same = !!f.contentDocument; } catch { same = false; }
        return { src: (f.src || '').slice(0, 80), sameOrigin: same };
      }),
      controlsInDom: controls.length,
      controlsVisible: controls.filter(vis).length,
      controlsHiddenButLabelled: controls.filter((el) => !vis(el) && el.closest('label, .choice, .option, .answer')).length,
      buttonsOnPage: [...d.querySelectorAll('button, input[type="submit"], input[type="button"], [role="button"], a.btn')]
        .filter(vis)
        .map((b) => (b.innerText || b.value || '').trim().slice(0, 30))
        .slice(0, 10),
      sampleControls: controls.slice(0, 12).map((el) => ({
        name: el.name || el.id || '(none)',
        type: (el.type || el.tagName).toLowerCase(),
        visible: vis(el),
        labelled: !!el.closest('label, .choice, .option, .answer'),
      })),
      bodyStart: (d.body?.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 300),
    };
    console.log(JSON.stringify(out, null, 1));
    return out;
  },

  // Stop the current exploration. Whatever has been recorded stays available
  // to spb.report() / spb.download().
  stop() {
    this._abort = true;
    const state = readJSON(STEP_KEY, null);
    if (state?.active) {
      state.active = false;
      writeJSON(STEP_KEY, state);
    }
    const n = this.allTraces().length;
    console.log(`%cstopping — ${n} traversal(s) recorded. spb.report() / spb.download()`, 'font-weight:bold');
    return n;
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

    const target = C.docFor(model, document);
    const answered = answerPage(model, c.plan, c.di, cfg, target);
    c.di = answered.di;
    c.steps.push(answered.record);
    c.decisions.push(...answered.record.decisions);
    writeJSON(STEP_KEY, state);
    console.table(Object.fromEntries(answered.record.decisions.map((d) => [d.key, d.chosen])));
    C.clickNext(model, target);
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
    if (this.traces.length) return this.traces;
    const step = readJSON(STEP_KEY, null);
    if (step?.traces?.length) return step.traces;
    return readJSON(AUTO_KEY, {})?.traces ?? [];
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
    const doc = C.docFor(m, document);
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
      C.applyAnswer(q, pick, doc);
      chosen[q.key] = C.describe(q, pick);
    }
    console.table(chosen);
    return chosen;
  },

  next() {
    const m = C.readPage(this.config.selectors);
    return C.clickNext(m, C.docFor(m, document));
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
    const doc = C.docFor(m, document);
    const answers = [];
    for (const q of m.questions) {
      const el = doc.querySelector(q.selector);
      if (q.kind === 'radio' || q.kind === 'checkbox') {
        for (const o of q.options) {
          const input = doc.querySelector(o.selector);
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
