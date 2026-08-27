// Page model extraction.
//
// Reads whatever survey page is currently open and returns a normalised
// description of it: the questions on it, the answer options for each, the
// "next" button, and whether the page looks like an end state (complete /
// screen-out / quota full).
//
// Nothing here is specific to one survey platform: questions are discovered by
// grouping the visible form controls by their `name` attribute, which is how
// every hosted survey engine (Decipher/Forsta, Qualtrics, Confirmit, SurveyMonkey,
// Alchemer...) renders them. `config.questionContainers` only improves the
// *labels*, never the detection.

export const DEFAULT_SELECTORS = {
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

// Serialised into the page. Keep it dependency-free and defensive: survey
// engines produce some genuinely strange DOM.
function pageModel(cfg) {
  const visible = (el) => {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0' && (r.width > 0 || r.height > 0);
  };
  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();

  // A selector that is *verified* to resolve back to this exact element.
  // Survey engines routinely put id="Q3" on the wrapper div and name="Q3" on
  // the control inside it, so an unchecked `#Q3` would target the wrapper.
  let stamp = 0;
  const resolves = (sel, el) => {
    try { return document.querySelector(sel) === el; } catch { return false; }
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

  // Text of the label attached to a single control.
  const optionLabel = (el) => {
    if (el.id) {
      const lab = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (lab && clean(lab.innerText)) return clean(lab.innerText);
    }
    const wrap = el.closest('label');
    if (wrap && clean(wrap.innerText)) return clean(wrap.innerText);
    const cell = el.closest('td, th, li, div');
    if (cell && clean(cell.innerText) && clean(cell.innerText).length < 120) return clean(cell.innerText);
    return clean(el.getAttribute('aria-label') || el.value || '');
  };

  // Wording of the question a control belongs to. For a grid, the row header
  // is appended, since that is what distinguishes Q2r1 from Q2r2.
  const questionLabel = (el) => {
    let stem = '';
    for (const sel of cfg.questionContainers) {
      const box = el.closest(sel);
      if (!box) continue;
      const head = box.querySelector('legend, .qtitle, .question-text, .question-title, h1, h2, h3, h4, .title, p');
      stem = clean(head?.innerText || '') || clean(box.innerText).slice(0, 300);
      if (stem) break;
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

  const controls = [...document.querySelectorAll('input, select, textarea')].filter((el) => {
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

    const q = {
      key,
      kind,
      label: questionLabel(first),
      required: els.some((e) => e.required || e.getAttribute('aria-required') === 'true'),
      selector: cssFor(first),
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
      }));
    }
    questions.push(q);
  }

  // Forward button.
  let next = null;
  for (const sel of cfg.nextButtons) {
    const el = [...document.querySelectorAll(sel)].find((e) => visible(e) && !e.disabled);
    if (el) {
      next = { selector: cssFor(el), label: clean(el.innerText || el.value || ''), matched: sel };
      break;
    }
  }

  const bodyText = clean(document.body?.innerText || '');
  const lower = bodyText.toLowerCase();
  let outcome = null;
  for (const [name, pats] of Object.entries(cfg.terminalPatterns)) {
    if (pats.some((p) => lower.includes(p))) { outcome = name; break; }
  }

  const heading = clean(
    document.querySelector('h1, h2, .page-title, .survey-title')?.innerText || document.title || ''
  ).slice(0, 200);

  return {
    url: location.href,
    title: document.title,
    heading,
    questions,
    next,
    outcome,
    bodyText: bodyText.slice(0, 4000),
  };
}

export async function readPage(page, selectors = DEFAULT_SELECTORS) {
  const model = await page.evaluate(pageModel, selectors);
  model.fingerprint = fingerprint(model);
  model.isTerminal = !model.next || (model.questions.length === 0 && !!model.outcome);
  return model;
}

// Identity of a *page* for flow-graph purposes: which questions it asked.
// Deliberately ignores the answers, so the same page reached down two different
// routes collapses to one node.
export function fingerprint(model) {
  const keys = model.questions.map((q) => q.key).sort();
  if (keys.length) return `Q:${keys.join(',')}`;
  const kind = model.outcome ?? 'page';
  return `${kind.toUpperCase()}:${(model.heading || model.bodyText.slice(0, 60)).toLowerCase().replace(/\s+/g, '-').slice(0, 40)}`;
}
