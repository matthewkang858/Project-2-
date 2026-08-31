// Survey pathway bot — console snippet. Built by build-snippet.mjs; do not edit here.
// Paste into the DevTools console on a survey page, or save as a DevTools Snippet
// (Sources ▸ Snippets ▸ New) and press Ctrl/Cmd+Enter to re-run it on each page.
(() => {
const SPB_BUILD = "8cc57ea 2026-08-31 04:16";
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
    complete: [
      'thank you for completing', 'thanks for completing', 'survey is complete', 'survey completed',
      'thanks for taking', 'thank you for taking', 'your responses have been recorded',
      'completed the survey', 'already completed', 'please close the window',
    ],
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
    // The counter lives on the document, not this call: a counter that resets
    // per read hands the same mark to two different elements — which once made
    // "click Continue" re-click an answer button instead.
    const prior = el.getAttribute('data-spb');
    if (prior && resolves(`[data-spb="${prior}"]`, el)) return `[data-spb="${prior}"]`;
    const n = (doc.__spbStamp = (doc.__spbStamp || 0) + 1);
    el.setAttribute('data-spb', String(n));
    return `[data-spb="${n}"]`;
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
  const rendered = (node) => !!node && node.getClientRects().length > 0;
  // Where the control's visible stand-in sits on screen. Survey players park
  // the real input off-screen (left:-9999px) inside a perfectly visible label —
  // so what matters is the label's geometry, never the input's own.
  const onScreen = (node) => {
    if (!node) return false;
    const r = node.getBoundingClientRect();
    const w = win.innerWidth || 1e5;
    return r.width > 0 && r.height > 0 && r.right > -50 && r.left < w + 50;
  };
  const standIn = (el) => {
    const lab = (el.id && doc.querySelector(`label[for="${CSS.escape(el.id)}"]`)) || el.closest('label');
    if (lab) return lab;
    let node = el.parentElement;
    for (let up = 0; node && up < 4; up++, node = node.parentElement) {
      if (node.querySelectorAll('input, select, textarea').length === 1 && visible(node) && onScreen(node)) return node;
    }
    return null;
  };
  const answerable = (el) => {
    if (visible(el) && onScreen(el)) return true;
    // A control with no layout box at all is inside a hidden subtree — a
    // carousel card waiting its turn — unless a label standing in for it is on
    // screen.
    if (!rendered(el)) {
      const lab = (el.id && doc.querySelector(`label[for="${CSS.escape(el.id)}"]`)) || el.closest('label');
      return rendered(lab) && visible(lab) && onScreen(lab);
    }
    // Rendered but invisible or parked off-screen: answerable exactly when a
    // visible on-screen element stands in for it. A honeypot has no such
    // stand-in — nothing visible wraps it alone.
    const sub = standIn(el);
    return !!sub && visible(sub) && onScreen(sub);
  };

  // Survey engines carry their own machinery in the form: per-render nonce
  // fields (ra__812345), respondent ids, trackers, and offscreen honeypots.
  // Answering them is wrong — and because their names change on every render,
  // treating them as questions makes every re-render look like a new page,
  // which is how a run ends up looping on one question.
  const MACHINE_NAME = /^(ra|rvid|rid|psid|sid|uid|hid|sys|tok|csrf|honeypot)[_.]|^[a-z]{1,6}__\d+$/i;

  const controls = [...doc.querySelectorAll('input, select, textarea')].filter((el) => {
    const type = (el.type || '').toLowerCase();
    if (['hidden', 'submit', 'button', 'image', 'reset', 'file'].includes(type)) return false;
    if (el.disabled || el.readOnly) return false;
    const name = el.name || el.id || '';
    if (MACHINE_NAME.test(name) && !clean(questionLabel(el))) return false;
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

    // Decipher and friends name each row of a question separately (LM1r1,
    // LM1r2 …). The group is what carries "select up to two" and "must total
    // 100", so it has to be reconstructed.
    q.group = key
      .replace(/([._-]\d+)+$/, '')   // ans32645.0.8 -> ans32645
      .replace(/[rc]\d+$/i, '')      // Q1r1 -> Q1
      || key;

    // Whether the respondent (or the bot) has already answered it — used to
    // avoid re-answering questions that stay on screen as a carousel reveals
    // more, and to explain validation stalls.
    q.answered =
      kind === 'radio' || kind === 'checkbox'
        ? els.some((e) => e.checked)
        : kind === 'select'
          ? !!first.value
          : String(first.value ?? '') !== '';

    q.checkedValues =
      kind === 'radio' || kind === 'checkbox' ? els.filter((e) => e.checked).map((e) => e.value) : [];

    // An "Other (please specify)" box lives inside the option's own row. Typing
    // in it without selecting that option is a validation error in every survey
    // platform, so record who owns it.
    if (kind === 'text' || kind === 'textarea' || kind === 'number') {
      const row = first.closest('label, td, tr, li, .choice, .option, [class*="answer"]');
      let owner = row && [...row.querySelectorAll('input')].find(
        (e) => (e.type === 'radio' || e.type === 'checkbox') && e.name !== first.name
      );
      // Decipher names the open-end after the question it belongs to:
      // oe32645.0 is the "other, please specify" box of ans32645.*. Its owner is
      // whichever option says "other" or "please specify".
      if (!owner) {
        const stem = (key.match(/^oe[_.]?(\d+)/i) || [])[1];
        if (stem)
          owner = [...doc.querySelectorAll('input')].find(
            (e) =>
              (e.type === 'radio' || e.type === 'checkbox') &&
              new RegExp(`^ans[_.]?${stem}\\b`, 'i').test(e.name || '') &&
              /other|please specify/i.test(clean(optionLabel(e)))
          );
      }
      if (owner) q.ownedBy = { key: owner.name || owner.id, value: owner.value ?? '' };
    }

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

  // Constraints stated in the question wording (and repeated by the validation
  // message when it fires): how many boxes may be ticked, what the numbers must
  // add up to.
  const WORD_NUMBER = { one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10 };
  const numberIn = (text, re) => {
    const m = text.match(re);
    if (!m) return null;
    const raw = (m[1] || '').toLowerCase();
    return WORD_NUMBER[raw] ?? (Number(raw) || null);
  };
  for (const q of questions) {
    const scope = clean(
      [q.label, ...[...doc.querySelectorAll('.error, .alert, [class*="error"]')].map((e) => clean(e.innerText))].join(' ')
    );
    q.limit =
      numberIn(scope, /select up to (\w+)/i) ??
      numberIn(scope, /choose up to (\w+)/i) ??
      numberIn(scope, /at most (\w+) box/i) ??
      numberIn(scope, /top (\w+) /i) ??
      null;
    q.sumTo = numberIn(scope, /(?:must (?:equal|total)|sum to|add up to|total(?:s|ling)? to)\s*(\d+)/i);
  }
  // A group of numeric fields on a "what percentage…" question is a
  // sum-to-100 allocation even when the page only says so after a failed
  // submit.
  const numericPerGroup = {};
  for (const q of questions)
    if (q.kind === 'number' || q.kind === 'text') numericPerGroup[q.group] = (numericPerGroup[q.group] || 0) + 1;
  for (const q of questions)
    if (!q.sumTo && (q.kind === 'number' || q.kind === 'text') && numericPerGroup[q.group] >= 2 &&
        /percent|share of|allocat|distribut|sum to|%/i.test(q.label || ''))
      q.sumTo = 100;

  // A carousel's own pager ("1 / 8" with arrows). It moves between cards inside
  // one question, so it must not be mistaken for the page's forward button.
  let pager = null;
  const POS = /^\d+\s*\/\s*\d+$/;
  const posCandidates = [...doc.querySelectorAll('span, div, p, li, b, strong')].filter(
    (el) => visible(el) && POS.test(clean(el.innerText || ''))
  );
  // Deepest match: the smallest element whose text is the whole readout, even
  // when the number, slash and total live in separate child spans.
  const posEl = posCandidates.find((el) => !posCandidates.some((o) => o !== el && el.contains(o))) ?? null;
  if (posEl) {
    const [index, total] = clean(posEl.innerText).split('/').map((n) => Number(n.trim()));
    let scope = posEl.parentElement;
    let btn = null;
    for (let up = 0; up < 4 && scope && !btn; up++, scope = scope.parentElement) {
      btn = [...scope.querySelectorAll('button, a, [role="button"]')].find((b) => {
        if (!visible(b) || b.disabled) return false;
        const aria = b.getAttribute('aria-label') || '';
        const label = clean(b.innerText || aria || '');
        return /^(next|forward|›|>|→|»)$/i.test(label) || /next|forward/i.test(aria);
      });
    }
    if (!btn) {
      // Icon-only arrows carry no text and often no aria-label; a class name
      // is the next hint.
      scope = posEl.parentElement;
      for (let up = 0; up < 4 && scope && !btn; up++, scope = scope.parentElement)
        btn = [...scope.querySelectorAll('button, a, [role="button"]')].find(
          (b) => visible(b) && !b.disabled && /next|right|forward/i.test(b.className || '')
        );
    }
    if (!btn) {
      // Last hint is geometry: the forward arrow sits just right of the "N / M"
      // readout, on the same line.
      const pr = posEl.getBoundingClientRect();
      const near = [...doc.querySelectorAll('button, a, [role="button"]')].filter((b) => {
        if (!visible(b) || b.disabled) return false;
        const r = b.getBoundingClientRect();
        return r.left >= pr.right - 4 && Math.abs(r.top + r.height / 2 - (pr.top + pr.height / 2)) < Math.max(40, pr.height);
      });
      near.sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
      btn = near[0] ?? null;
    }
    // Even with no clickable arrow found, a "N / M" readout is a carousel:
    // answering a card advances it, so the pager needs no button of its own.
    pager = { selector: btn ? cssFor(btn) : null, index, total, atEnd: index >= total };
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

  // Button-driven carousel cards: one card at a time, a pager, and a row of
  // clickable non-form answer buttons shared by every card. There is no radio
  // or checkbox to find, so this is its own question kind.
  const hasChoiceQuestion = questions.some((q) => ['radio', 'checkbox', 'select', 'slider'].includes(q.kind));
  if (pager && !hasChoiceQuestion) {
    const FWD = /^(continue|next|start|begin|proceed|submit|go on|ok|done|→|»|>>|›|>)$/i;
    const BWD = /^(back|previous|prev|return|cancel|exit|«|<<|‹|<)$/i;
    const candidates = [...doc.querySelectorAll('button, [role="button"], a, div, li, span')].filter((el) => {
      if (!visible(el)) return false;
      // Only a RENDERED control inside disqualifies a clickable — players park
      // their display:none state radios inside the very buttons that drive
      // them, and those must still count as buttons.
      if ([...el.querySelectorAll('input, select, textarea')].some((c) => c.getClientRects().length)) return false;
      const t = clean(el.innerText || '');
      if (!t || t.length > 220 || FWD.test(t) || BWD.test(t) || POS.test(t)) return false;
      const style = win.getComputedStyle(el);
      return el.tagName === 'BUTTON' || el.getAttribute('role') === 'button' || style.cursor === 'pointer' || !!el.onclick;
    });
    // A clickable that holds candidates with DIFFERENT texts is the row
    // holding the buttons, not a button — cursor:pointer inherits, so the
    // shared container often qualifies as a candidate itself and must not
    // swallow the real buttons. A clickable whose inner candidates all carry
    // its own text is one button rendered as a tower of divs.
    const textOf = (el) => clean(el.innerText || '');
    const isContainer = (el) => {
      const texts = new Set();
      for (const o of candidates) if (o !== el && el.contains(o)) texts.add(textOf(o));
      return texts.size > 1;
    };
    const buttons = candidates.filter((el) => !isContainer(el));
    const tops = buttons.filter((el) => !buttons.some((o) => o !== el && o.contains(el)));
    // Buttons rarely share a direct parent — each one usually sits in its own
    // wrapper cell — so group by the nearest ancestor holding at least two
    // tops, and within it by the tops' own tag+class so the answer row does
    // not mix with unrelated clickables under some distant shared wrapper.
    const groups = new Map();
    for (const el of tops) {
      let anc = el.parentElement;
      while (anc && tops.filter((t) => t !== el && anc.contains(t)).length < 1) anc = anc.parentElement;
      if (!anc) continue;
      const sig = el.tagName + '|' + (el.className || '');
      if (!groups.has(anc)) groups.set(anc, new Map());
      const bySig = groups.get(anc);
      if (!bySig.has(sig)) bySig.set(sig, []);
      bySig.get(sig).push(el);
    }
    let best = null;
    let bestScore = -1;
    for (const [, bySig] of groups) {
      for (const [, els] of bySig) {
        // Q58-style card questions offer nine role buttons; radios elsewhere
        // in this questionnaire go to 22 options — the cap only exists to
        // reject page furniture, so it is generous.
        if (els.length < 2 || els.length > 26) continue;
        if (new Set(els.map((e) => clean(e.innerText))).size !== els.length) continue;
        // The answer row sits below the pager; a look-alike group above it
        // (peeking card faces, say) must not win.
        const below = els.filter((e) => posEl && posEl.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING).length;
        const score = (below >= els.length / 2 ? 100 : 0) + els.length;
        if (score > bestScore) {
          bestScore = score;
          best = els;
        }
      }
    }
    if (best && posEl) {
      // The card's own wording is the nearest text block above the pager that
      // is not the question stem and not one of the buttons.
      const stem = clean(
        doc.querySelector('h1, h2, .page-title, .qtitle, .question-text, .survey-title')?.innerText || doc.title || ''
      ).slice(0, 200);
      let title = '';
      const blocks = [...doc.querySelectorAll('div, p, span, h1, h2, h3, td, th, li')].filter((el) => {
        if (!visible(el)) return false;
        const t = clean(el.innerText || '');
        if (t.length < 5 || t.length > 200 || t === stem || POS.test(t)) return false;
        if (/^\W*\d+\s*\/\s*\d+\W*$/.test(t)) return false; // "‹ 1 / 3 ›"
        if (el.contains(posEl) || posEl.contains(el)) return false; // the pager itself
        return !best.some((b) => b === el || b.contains(el) || el.contains(b));
      });
      for (const el of blocks) {
        if (blocks.some((o) => o !== el && el.contains(o))) continue; // deepest only
        if (posEl.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_PRECEDING) title = clean(el.innerText);
      }
      const slug = (title || 'card').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50);
      questions.push({
        key: `card${pager.index}:${slug}`,
        kind: 'buttons',
        label: title ? `${stem} — ${title}` : `${stem} — card ${pager.index}/${pager.total}`,
        group: 'cards:' + clean(stem).toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 30),
        required: true,
        selector: cssFor(best[0]),
        emphasis: marksOf(
          doc.querySelector('h1, h2, .page-title, .qtitle, .question-text, .survey-title')
        ),
        answered: best.some((b) => /\b(sel|selected|active|checked)\b/i.test(b.className || '') || b.getAttribute('aria-pressed') === 'true'),
        options: best.map((b) => {
          let target = b;
          for (;;) {
            const deeper = buttons.find((o) => o !== target && target.contains(o));
            if (!deeper) break;
            target = deeper;
          }
          return { value: clean(b.innerText), label: clean(b.innerText), selector: cssFor(target), emphasis: marksOf(b) };
        }),
      });
    }
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
      if (pager && cssFor(e) === pager.selector) return false; // that is the carousel's arrow
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
    pager,
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
  // Field names are used as-is: nonce fields are filtered out before this point,
  // and normalising the digits away would make a carousel's cards (PG1r1, PG1r2)
  // indistinguishable from one another.
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

  if (q.kind === 'radio' || q.kind === 'checkbox' || q.kind === 'select' || q.kind === 'buttons') {
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
      if (hit) return [hit];
      // No match: a multi-select names each box separately, so the fixed rule
      // matches the whole group and only the named box should be ticked — the
      // others stay blank. Ticking the first box instead would answer "Canada"
      // to a rule that says "United States".
      if (q.kind === 'checkbox') return [{ kind: 'noop', label: '(not the fixed option)' }];
      return opts.slice(0, 1);
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

// What to answer on this page, as one plan: per-question choices with the
// group constraints applied — at most N boxes ticked per question, numbers
// distributed so a group totals what the question demands.
function planPage(model, plan, startDi, cfg, answered) {
  const config = cfg || {};
  const decisions = [];
  let di = startDi || 0;
  const ticked = {};
  const groups = {};
  for (const q of model.questions) (groups[q.group] = groups[q.group] || []).push(q);

  const picked = {}; // key -> values chosen on this page
  for (const q of model.questions) (picked[q.key] = picked[q.key] || []).push(...(q.checkedValues || []));

  for (const q of model.questions) {
    if (answered && answered.has(q.key) && q.answered) continue;
    const cands = candidates(q, config);
    const wanted = plan ? plan[di] : undefined;
    const idx = Number.isInteger(wanted) && wanted < cands.length ? wanted : 0;
    let chosen = cands[idx];
    let note = null;

    if (q.kind === 'checkbox' && chosen && chosen.kind === 'option') {
      // Default to a single box per question: ticking every box of a
      // "select up to two" question is the fastest way to a validation error.
      const limit = q.limit ?? config.checkboxLimit ?? 1;
      const used = ticked[q.group] || 0;
      if (used >= limit) {
        chosen = { kind: 'noop', label: `(limit of ${limit} reached)` };
        note = `limit ${limit}`;
      } else ticked[q.group] = used + 1;
    }

    if (q.sumTo && (q.kind === 'number' || q.kind === 'text')) {
      const members = groups[q.group] || [q];
      const share = Math.floor(q.sumTo / members.length);
      const first = q.sumTo - share * (members.length - 1);
      chosen = { kind: 'value', value: String(members.indexOf(q) === 0 ? first : share) };
      note = `sums to ${q.sumTo}`;
    }

    // Record what this page is choosing, so an option's own text box knows
    // whether it is in play.
    if (chosen && chosen.kind === 'option') (picked[q.key] = picked[q.key] || []).push(String(chosen.value));

    if (q.ownedBy) {
      const taken = (picked[q.ownedBy.key] || []).includes(String(q.ownedBy.value));
      if (!taken) {
        chosen = { kind: 'noop', label: '(its option was not selected)' };
        note = 'other-specify left blank';
      }
    }

    decisions.push({ q, candidate: chosen, di, candidateCount: cands.length, chosenIndex: idx, note });
    di++;
  }
  return { decisions, di };
}

// Find a control again, even when the player has repainted the page since it
// was read: by the recorded selector, then by name and value (immune to both
// re-renders and to CSS-escaping of names like "ans32477.0.0"), then by the
// option's own wording.
function findControl(doc, q, opt) {
  const tidy = (s) => (s || '').replace(/\s+/g, ' ').trim();
  let el = null;
  try {
    el = doc.querySelector(opt ? opt.selector : q.selector);
  } catch {
    el = null;
  }
  if (el && el.isConnected) return el;

  const all = [...doc.querySelectorAll('input, select, textarea')];
  if (opt) {
    el = all.find((e) => (e.name === q.key || e.id === q.key) && String(e.value) === String(opt.value));
    if (el) return el;
    if (opt.label) {
      const wrap = [...doc.querySelectorAll('label, li, td, div, span')].find(
        (w) => w.querySelectorAll('input').length === 1 && tidy(w.innerText) === tidy(opt.label)
      );
      if (wrap) return wrap.querySelector('input');
    }
    return null;
  }
  return all.find((e) => e.name === q.key || e.id === q.key) || null;
}

// The clickable thing standing in for a hidden control: the nearest wrapper
// that holds this control and no other.
function wrapperFor(el) {
  let node = el.parentElement;
  for (let up = 0; node && up < 4; up++, node = node.parentElement) {
    if (node.querySelectorAll('input, select, textarea').length === 1) {
      if (node.tagName === 'LABEL' || /ans|answer|choice|option|item|cell|row/i.test(node.className || '')) return node;
      if (up === 0) var fallback = node;
    }
  }
  return typeof fallback === 'undefined' ? null : fallback;
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
    const el = findControl(doc, q);
    if (!el) return false;
    el.focus?.();
    el.value = candidate.value;
    fire(el, ['input', 'change', 'blur']);
    return String(el.value) === String(candidate.value);
  }
  if (candidate.kind === 'slide') {
    const el = findControl(doc, q);
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
    const el = findControl(doc, q);
    if (!el) return false;
    el.value = opt.value;
    fire(el, ['input', 'change']);
    return String(el.value) === String(opt.value);
  }
  if (q.kind === 'buttons') {
    const tidy = (x) => (x || '').replace(/\s+/g, ' ').trim();
    let el = null;
    try {
      el = doc.querySelector(opt.selector);
    } catch {
      el = null;
    }
    if (!el || !el.isConnected) {
      // Re-find by wording; the DEEPEST match, so the click bubbles up
      // through every level of the button's tower of divs.
      const matches = [...doc.querySelectorAll('button, [role="button"], a, div, li, span')].filter(
        (e) => tidy(e.innerText) === tidy(opt.label) && e.getClientRects().length
      );
      el = matches.find((m) => !matches.some((o) => o !== m && m.contains(o))) ?? null;
    }
    if (!el) return false;
    // Some players listen for pointer events rather than click.
    const Pointer = win.PointerEvent || win.MouseEvent;
    for (const type of ['pointerdown', 'mousedown', 'pointerup', 'mouseup'])
      el.dispatchEvent(new (type.startsWith('pointer') ? Pointer : win.MouseEvent)(type, { bubbles: true, cancelable: true, view: win }));
    el.click();
    return true;
  }
  const el = findControl(doc, q, opt);
  if (!el) return false;
  // With a hidden input the player listens on the wrapper that stands in for
  // it — a <label>, or just a styled <div>. Click that, then fall back to
  // clicking and finally forcing the control itself.
  const box = el.getBoundingClientRect();
  const hidden = box.width <= 2 || box.height <= 2 || (doc.defaultView || window).getComputedStyle(el).opacity === '0';
  const wrapper =
    (el.id && doc.querySelector(`label[for="${CSS.escape(el.id)}"]`)) || el.closest('label') || wrapperFor(el);
  if (hidden && wrapper) wrapper.click();
  if (!el.checked) el.click();
  if (!el.checked) {
    el.checked = true;
    fire(el, ['input', 'change']);
  }
  const marked = wrapper
    ? wrapper.getAttribute('aria-checked') === 'true' || /\b(selected|checked|active)\b/i.test(wrapper.className || '')
    : false;
  return el.checked || marked;
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
  planPage,
  findControl,
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
        // Survey engines name each checkbox of one question separately
        // (Q7r1, Q7r2 …). Reporting them as separate questions buries the
        // report in near-identical rows, so they collapse back into the group.
        const id = q.kind === 'checkbox' && q.group && q.group !== q.key ? q.group : q.key;
        if (!qs.has(id)) qs.set(id, { label: q.label, kind: q.kind, options: new Map(), grouped: id !== q.key });
        const rec = qs.get(id);
        for (const o of q.options ?? []) {
          const k = o.label || o.value;
          if (!rec.options.has(k)) rec.options.set(k, { chosen: 0 });
        }
        // Under a group, each box is one selectable answer; the option label is
        // the box's own text.
        if (rec.grouped)
          for (const o of q.options ?? []) {
            const k = o.label || q.key;
            if (!rec.options.has(k)) rec.options.set(k, { chosen: 0 });
          }
        else if (q.kind === 'checkbox' && (q.options ?? []).length === 1 && !rec.options.has('(left unchecked)'))
          rec.options.set('(left unchecked)', { chosen: 0 });
      }
      for (const d of s.decisions ?? []) {
        const q = (s.questions ?? []).find((x) => x.key === d.key);
        const id = q && q.kind === 'checkbox' && q.group && q.group !== q.key ? q.group : d.key;
        const rec = qs.get(id);
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
    if (t.outcome?.type === 'looping')
      findings.push(`**${t.runId} looped** on \`${t.outcome.atFingerprint ?? '?'}\` — ${esc(trunc(t.outcome.text, 160))}. Usually a validation the bot is not satisfying; the page's own error message is the place to look.`);
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

// Answer every question on `doc`, returning the page record. The plan comes
// from the shared core so group constraints ("select up to two", "must total
// 100") are applied the same way in every runner.
function answerPage(model, plan, di, cfg, doc, answered) {
  const record = {
    url: model.url,
    fingerprint: model.fingerprint,
    heading: model.heading,
    outcome: model.outcome,
    questionKeys: model.questions.map((q) => q.key),
    questions: model.questions.map((q) => ({
      key: q.key,
      group: q.group,
      kind: q.kind,
      label: q.label,
      limit: q.limit ?? undefined,
      sumTo: q.sumTo ?? undefined,
      emphasis: q.emphasis,
      options: q.options.map((o) => ({ value: o.value, label: o.label, emphasis: o.emphasis })),
    })),
    decisions: [],
  };
  const planned = C.planPage(model, plan, di, cfg, answered);
  for (const d of planned.decisions) {
    const ok = C.applyAnswer(d.q, d.candidate, doc);
    if (answered) answered.add(d.q.key);
    record.decisions.push({
      di: d.di,
      key: d.q.key,
      kind: d.q.kind,
      label: d.q.label,
      candidateCount: d.candidateCount,
      chosenIndex: d.chosenIndex,
      chosen: C.describe(d.q, d.candidate),
      note: d.note ?? undefined,
      error: ok ? undefined : 'could not set answer',
    });
  }
  return { record, di: planned.di, planned: planned.decisions };
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
  version: typeof SPB_BUILD !== 'undefined' ? SPB_BUILD : 'dev',
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
    const maxSteps = Number(cfg.maxSteps ?? 200);

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
        const visits = new Map(); // how often each page has come round
        const validationRetried = new Set(); // pages re-answered after an error
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
          // A page coming round again is only a loop if nothing new got
          // answered in between — a carousel revisits the same page per card.
          const visit = visits.get(model.fingerprint) ?? { count: 0, answered: -1 };
          visit.count = visit.answered === di ? visit.count + 1 : 1;
          visit.answered = di;
          visits.set(model.fingerprint, visit);
          if (visit.count > 3 && !model.isTerminal) {
            type = 'looping';
            text = `the same page came round ${visit.count} times with nothing new answered`;
            break;
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
          const pageStartDi = di;
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
            // A player that repaints its answers can wipe a selection right
            // after it is made; redo any answer that did not stick.
                    // An answer the fresh read shows as taken is good — clear its error.
        for (const d of ans.planned) {
          const fresh = after.questions.find((x) => x.key === d.q.key);
          if (fresh && fresh.answered) {
            const dec = ans.record.decisions.find((x) => x.key === d.q.key);
            if (dec && dec.error) delete dec.error;
          }
        }
const lost = ans.planned.filter((d) => {
              if (!d.candidate || d.candidate.kind === 'noop') return false;
              const fresh = after.questions.find((x) => x.key === d.q.key);
              return fresh && fresh.answered === false;
            });
            for (const d of lost) {
              const fresh = after.questions.find((x) => x.key === d.q.key);
              C.applyAnswer(fresh, d.candidate, C.docFor(after, docOf()));
            }
            current = lost.length ? C.readPage(cfg.selectors, docOf()) : after;
          }

          // A carousel's own pager moves between cards inside one question.
          if (current.pager && !current.pager.atEnd && current.pager.selector) {
            const at = current.fingerprint + '|' + current.url;
            C.clickNext({ next: { selector: current.pager.selector } }, C.docFor(current, docOf()));
            const until = Date.now() + timeout;
            let advanced = false;
            while (Date.now() < until) {
              await sleep(200);
              const now = C.readPage(cfg.selectors, docOf());
              if (now.fingerprint + '|' + now.url !== at) { advanced = true; break; }
            }
            if (advanced) { ans.record.pager = `${current.pager.index}/${current.pager.total}`; continue; }
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
            // The validation message states the constraint the page withheld;
            // re-reading now detects it, so retry the page once before asking
            // for help. Plan index rewinds to keep branch numbering aligned.
            if (!validationRetried.has(current.fingerprint)) {
              validationRetried.add(current.fingerprint);
              for (const q of model.questions) answered.delete(q.key);
              di = pageStartDi;
              ans.record.validationRetry = why;
              continue;
            }
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
      if (['stuck', 'stalled', 'looping'].includes(type)) {
        // The one moment the stuck page is guaranteed to be in the frame.
        try {
          trace.outcome.debug = this.debug(docOf(), true);
        } catch {}
      }
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
      if (['stuck', 'stalled', 'looping'].includes(type) && (cfg.stopOnStuck ?? true)) {
        console.warn(
          `%c${runId} ended "${type}" — stopping so the failed page stays open in the frame. ` +
            '(pass config.stopOnStuck: false to push on instead)',
          'font-weight:bold'
        );
        if (trace.outcome.debug) {
          console.log('%cDiagnosis of the stuck page — paste this back:', 'font-weight:bold');
          try {
            console.log(JSON.stringify(trace.outcome.debug, null, 1));
          } catch {}
        }
        break;
      }
    }

    this.traces = state.traces;
    this._summary = { url: startUrl, generatedAt: new Date().toISOString(), plansQueuedButNotRun: state.queue.length };
    const lastOutcome = state.traces[state.traces.length - 1]?.outcome?.type;
    if (lastOutcome && !['complete', 'terminate', 'quota'].includes(lastOutcome)) {
      // Leave the stuck page inspectable: spb.debug() reads this frame.
      frame.style.cssText =
        'position:fixed;right:12px;bottom:12px;width:460px;height:620px;z-index:2147483647;' +
        'border:2px solid #b91c1c;border-radius:6px;background:#fff;box-shadow:0 8px 30px rgba(0,0,0,.35)';
      console.warn(
        `%cthe last run ended "${lastOutcome}" — the survey frame is left open on the stuck page.\n` +
          'Run  copy(JSON.stringify(spb.debug(), null, 1))  and paste the result to diagnose it. spb.closeFrame() removes the panel.',
        'font-weight:bold'
      );
    } else {
      frame.remove();
    }
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
  debug(doc, quiet) {
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
        .map((b) => (b.innerText || b.value || '').trim().slice(0, 30) + (b.disabled ? ' [disabled]' : ''))
        .slice(0, 10),
      detectedQuestions: (() => {
        try {
          return model.questions.map((q) => ({ key: q.key.slice(0, 40), kind: q.kind }));
        } catch {
          return [];
        }
      })(),
      sampleControls: controls.slice(0, 12).map((el) => ({
        name: el.name || el.id || '(none)',
        type: (el.type || el.tagName).toLowerCase(),
        visible: vis(el),
        labelled: !!el.closest('label, .choice, .option, .answer'),
      })),
      bodyStart: (d.body?.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 300),
      carousel: (() => {
        const tidy = (x) => (x || '').replace(/\s+/g, ' ').trim();
        const posTexts = [...d.querySelectorAll('span, div, p, li, b, strong')]
          .map((e) => tidy(e.innerText))
          .filter((t) => /^\d+\s*\/\s*\d+$/.test(t));
        const navButtons = [...d.querySelectorAll('button, [role="button"], a')]
          .filter(vis)
          .map((b) => ({ text: tidy(b.innerText).slice(0, 24), aria: b.getAttribute('aria-label') || undefined, cls: (b.className || '').slice(0, 40) }))
          .slice(0, 14);
        const groups = new Map();
        for (const el of d.querySelectorAll('button, [role="button"], a, div, li, span')) {
          if (!vis(el) || el.querySelector('input, select, textarea')) continue;
          const t = tidy(el.innerText);
          if (!t || t.length > 220) continue;
          const cur = win.getComputedStyle(el).cursor;
          if (cur !== 'pointer' && el.tagName !== 'BUTTON' && el.getAttribute('role') !== 'button') continue;
          const parent = el.parentElement;
          if (!parent) continue;
          const key = parent.tagName + '.' + (parent.className || '').split(' ')[0];
          if (!groups.has(key)) groups.set(key, new Set());
          groups.get(key).add(t);
        }
        const clickableGroups = [...groups.entries()]
          .map(([parent, labels]) => ({ parent, labels: [...labels].slice(0, 10) }))
          .filter((g) => g.labels.length >= 2)
          .slice(0, 8);
        return { detectedPager: model.pager ?? null, posTexts: [...new Set(posTexts)].slice(0, 5), navButtons, clickableGroups };
      })(),
    };
    if (!quiet) console.log(JSON.stringify(out, null, 1));
    return out;
  },

  closeFrame() {
    try {
      this._lastFrame && this._lastFrame.remove();
    } catch {}
    console.log('panel removed');
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
      maxSteps: opts.maxSteps ?? 200,
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
    const nav = model.pager && !model.pager.atEnd && model.pager.selector ? { next: { selector: model.pager.selector } } : model;
    C.clickNext(nav, target);
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
  console.log(`%csurvey pathway bot loaded — build ${typeof SPB_BUILD !== 'undefined' ? SPB_BUILD : 'dev'}`, 'font-weight:bold');
  console.log('spb.auto()  explore everything automatically   ·   spb.help()  all commands');
}

})();
