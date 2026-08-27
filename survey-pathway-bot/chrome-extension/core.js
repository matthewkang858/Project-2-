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
