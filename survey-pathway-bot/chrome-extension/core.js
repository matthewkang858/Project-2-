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
    '#NextButton',
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
  // Every label that could stand in for this control. A control can carry more
  // than one `label[for]` — Qualtrics pairs an empty, 0-box styled radio
  // overlay with a second label that holds the visible answer text — so the
  // stand-in is whichever label actually renders on screen, not just the first.
  const labelsFor = (el) => {
    const labs = el.id ? [...doc.querySelectorAll(`label[for="${CSS.escape(el.id)}"]`)] : [];
    const wrap = el.closest('label');
    if (wrap && !labs.includes(wrap)) labs.push(wrap);
    return labs;
  };
  const visibleLabel = (el) => labelsFor(el).find((l) => visible(l) && onScreen(l)) || null;
  const standIn = (el) => {
    const lab = visibleLabel(el) || labelsFor(el)[0];
    if (lab) return lab;
    let node = el.parentElement;
    for (let up = 0; node && up < 4; up++, node = node.parentElement) {
      if (node.querySelectorAll('input, select, textarea').length === 1 && visible(node) && onScreen(node)) return node;
    }
    return null;
  };
  const answerable = (el) => {
    if (visible(el) && onScreen(el)) return true;
    // Otherwise answerable exactly when something visible stands in for it: a
    // label carrying the answer text, or a styled wrapper. A carousel card
    // waiting its turn (whole subtree hidden) and a honeypot (parked off
    // screen, nothing visible around it) both have no such stand-in.
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
      .replace(/(~TEXT)$/i, '')      // Qualtrics other-specify: QR~QID12~5~TEXT
      .replace(/([._~-]\d+)+$/, '')  // ans32645.0.8 -> ans32645, QR~QID12~5 -> QR~QID12
      .replace(/[rc]\d+$/i, '')      // Q1r1 -> Q1
      || key;

    // Whether the respondent (or the bot) has already answered it — used to
    // avoid re-answering questions that stay on screen as a carousel reveals
    // more, and to explain validation stalls.
    q.answered =
      kind === 'radio' || kind === 'checkbox'
        ? els.some((e) => e.checked)
        : kind === 'select'
          // a placeholder option can carry a real value (Qualtrics: "QR~…~null"),
          // so "answered" means a non-blank, non-placeholder option is selected
          ? !!first.value && !/~null$/.test(first.value) && !!clean(first.selectedOptions?.[0]?.text ?? '')
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
      // Qualtrics names the write-in after its own choice: QR~QID12~5~TEXT
      // belongs to choice 5 of QR~QID12 (radio group) or QR~QID12~5 (checkbox).
      if (!owner) {
        const qm = key.match(/^(.*)~(\d+)~TEXT$/i);
        if (qm)
          owner = [...doc.querySelectorAll('input')].find(
            (e) =>
              (e.type === 'radio' || e.type === 'checkbox') &&
              ((e.name === qm[1] && String(e.value) === qm[2]) || e.name === `${qm[1]}~${qm[2]}` || e.id === `${qm[1]}~${qm[2]}`)
          );
      }
      if (owner) q.ownedBy = { key: owner.name || owner.id, value: owner.value ?? '' };
    }

    // A free-text box that actually wants a number: type=number, a numeric
    // inputmode/pattern, or wording that asks for money/count/percentage.
    // Typing a word into it is an instant validation error, so mark it and
    // remember any ceiling the field or its wording states.
    if (kind === 'text' || kind === 'number') {
      const im = (first.getAttribute('inputmode') || '').toLowerCase();
      const pat = first.getAttribute('pattern') || '';
      q.numeric =
        kind === 'number' ||
        ['numeric', 'decimal', 'tel'].includes(im) ||
        /\[?0-9/.test(pat) ||
        /how much|how many|number of|percentage|\bamount|dollars?|\bspen[dt]|budget|\bprice|\bcost\b|\bvalue\b|\$|per (?:month|year|week)/i.test(q.label || '');
      const maxAttr = first.getAttribute('max');
      if (maxAttr && !isNaN(+maxAttr)) q.numMax = Number(maxAttr);
      const minAttr = first.getAttribute('min');
      if (minAttr && !isNaN(+minAttr)) q.numMin = Number(minAttr);
    }

    if (kind === 'select') {
      q.options = [...first.options]
        // Qualtrics gives its blank placeholder a real value ("QR~…~null"),
        // so empty text must disqualify too — selecting it is a non-answer.
        .filter((o) => o.value !== '' && !o.disabled && clean(o.text) && !/~null$/.test(o.value))
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
  // A numeric-entry instruction near the question ("You cannot enter a value
  // over $300", 'please write "300" in the box') is a strong signal even when
  // the ask is phrased as a scenario with no money words in the stem itself.
  const pageTxt = clean(doc.body ? doc.body.innerText : '').slice(0, 4000);
  const numCue = /cannot enter a value|value over \$?\d|no more than \$?\d|writ(?:e|ing)\s+["“']?\s*\d|enter a (?:value|number|amount|dollar)/i.test(pageTxt);
  const pageCap = pageTxt.match(/(?:over|exceed|more than|greater than|maximum(?: of)?|no more than|up to)\s*\$?\s*([\d,]{1,12})/i);
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
    // A numeric write-in the stem alone did not flag.
    if ((q.kind === 'text' || q.kind === 'number') && !q.numeric && numCue) q.numeric = true;
    // A max stated in wording or a validation/instruction banner ("You cannot
    // enter a value over $10,000"), whether beside the field or page-level.
    if (q.numeric && q.numMax == null) {
      const m = scope.match(/(?:over|exceed|more than|greater than|maximum(?: of)?|no more than|up to)\s*\$?\s*([\d,]{1,12})/i) || pageCap;
      if (m) q.numMax = Number(m[1].replace(/,/g, ''));
    }
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
    const BWD = /^(back|previous|prev|return|cancel|exit|←|«|<<|‹|<)$/i;
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
    const forward = cfg.nextText ? new RegExp(cfg.nextText, 'i') : /^(continue|next|start|begin|proceed|submit|go on|ok|done)\b|^(→|»|>>)$/i;
    const backward = /^(back|previous|prev|return|cancel|exit)\b|^(←|«|<<)$/i;
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
  // A numeric write-in gets a modest number, clamped to any stated bounds —
  // never the word "Test", which fails a number field's validation.
  if (q.numeric) {
    let v = 30;
    if (q.numMax != null) v = Math.min(v, q.numMax);
    if (q.numMin != null) v = Math.max(v, q.numMin);
    return [{ kind: 'value', value: String(v) }];
  }
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
    // Set through the prototype's native value setter so frameworks that wrap
    // the property — and watchers (Qualtrics' QWatchTimer) that compare against
    // their last-seen value — actually observe the change, then drive the full
    // typing event sequence a plain `el.value =` skips.
    const proto = el.tagName === 'TEXTAREA' ? win.HTMLTextAreaElement : win.HTMLInputElement;
    const setter = proto && Object.getOwnPropertyDescriptor(proto.prototype, 'value')?.set;
    if (setter) setter.call(el, candidate.value);
    else el.value = candidate.value;
    const lastCh = String(candidate.value).slice(-1) || '0';
    el.dispatchEvent(new win.KeyboardEvent('keydown', { key: lastCh, bubbles: true }));
    try {
      el.dispatchEvent(new win.InputEvent('input', { bubbles: true, data: String(candidate.value), inputType: 'insertText' }));
    } catch {
      el.dispatchEvent(new win.Event('input', { bubbles: true }));
    }
    el.dispatchEvent(new win.KeyboardEvent('keyup', { key: lastCh, bubbles: true }));
    fire(el, ['change', 'blur']);
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
  // it — a <label>, or just a styled <div>. Some engines (Qualtrics) re-render
  // the control from their own runtime state after every change, wiping a
  // synthetic `.checked`; that state only updates from a full event sequence,
  // so drive the visible stand-in the way a real click would, like the
  // button path does.
  const box = el.getBoundingClientRect();
  const hidden = box.width <= 2 || box.height <= 2 || (doc.defaultView || window).getComputedStyle(el).opacity === '0';
  // Prefer the label that a person actually sees/clicks. A `for`-linked label
  // that renders empty (Qualtrics' styled q-radio overlay) is a poor target,
  // so take a non-empty labelled one when there is a choice.
  const labelled = el.id ? [...doc.querySelectorAll(`label[for="${CSS.escape(el.id)}"]`)] : [];
  const hasText = (l) => (l.innerText || l.textContent || '').trim() !== '';
  const wrapper =
    labelled.find(hasText) || labelled[0] || el.closest('label') || wrapperFor(el);
  const Pointer = win.PointerEvent || win.MouseEvent;
  const clickLike = (target) => {
    if (!target) return;
    for (const type of ['pointerdown', 'mousedown', 'pointerup', 'mouseup'])
      target.dispatchEvent(new (type.startsWith('pointer') ? Pointer : win.MouseEvent)(type, { bubbles: true, cancelable: true, view: win }));
    target.click();
  };
  if (hidden && wrapper) clickLike(wrapper);
  if (!el.checked) clickLike(el);
  if (!el.checked) {
    el.checked = true;
    fire(el, ['input', 'change']);
  }
  const marked = wrapper
    ? wrapper.getAttribute('aria-checked') === 'true' || /\b(selected|checked|active|q-checked)\b/i.test(wrapper.className || '')
    : false;
  return el.checked || marked;
}

// Click the forward button described by a page model. Some engines (Qualtrics
// JFE) bind their Next control through their own event system and ignore a bare
// synthetic click, so drive it the way a person would — a full pointer/mouse/
// click sequence — and fall back to focus + Enter.
function clickNext(model, doc) {
  if (!model.next) return false;
  doc = doc || document;
  const win = doc.defaultView || window;
  const el = doc.querySelector(model.next.selector);
  if (!el) return false;
  const Pointer = win.PointerEvent || win.MouseEvent;
  for (const type of ['pointerover', 'pointerenter', 'pointerdown', 'mousedown', 'pointerup', 'mouseup'])
    el.dispatchEvent(new (type.startsWith('pointer') ? Pointer : win.MouseEvent)(type, { bubbles: true, cancelable: true, view: win }));
  el.focus?.();
  el.click();
  for (const type of ['keydown', 'keypress', 'keyup'])
    el.dispatchEvent(new win.KeyboardEvent(type, { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true }));
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
