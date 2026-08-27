// Console API built on top of the shared core. Everything here is scoped to the
// page you are currently looking at — a page navigation clears it, which is why
// multi-page automation lives in the Chrome extension instead.

const C = globalThis.SPB_CORE;
const CAPTURE_KEY = 'spb-captured-answers';

const readCaptured = () => {
  try {
    return JSON.parse(sessionStorage.getItem(CAPTURE_KEY) || '[]');
  } catch {
    return [];
  }
};
const writeCaptured = (v) => {
  try {
    sessionStorage.setItem(CAPTURE_KEY, JSON.stringify(v));
  } catch {}
};

const spb = {
  core: C,
  config: {},

  // What the bot sees on this page.
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

  // Answer every question on the page. Override by question name:
  //   spb.fill({ S1: 2 })            -> option index 2
  //   spb.fill({ S1: /55 or older/ })-> first option whose label/value matches
  //   spb.fill({ Q3: 'some text' })  -> text answer
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
    const m = C.readPage(this.config.selectors);
    return C.clickNext(m);
  },

  step(overrides) {
    const chosen = this.fill(overrides);
    this.next();
    return chosen;
  },

  // Record the answers currently selected on this page, so a pathway you walk
  // by hand can be turned into a scripted test. Run it on each page, then call
  // spb.scenario('name') at the end.
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
    const all = readCaptured();
    all.push({ url: location.href, fingerprint: m.fingerprint, answers });
    writeCaptured(all);
    console.log(`captured ${answers.length} answer(s) on ${m.fingerprint} (${all.length} page(s) so far)`);
    return answers;
  },

  // Print the captured pages as a paths.json scenario.
  scenario(name = 'Captured pathway') {
    const all = readCaptured();
    const answers = all.flatMap((p) => p.answers);
    const seen = [...new Set(all.flatMap((p) => p.fingerprint))];
    const out = { name, answers, expect: { outcome: 'complete' }, _pages: seen };
    console.log(JSON.stringify(out, null, 2));
    return out;
  },

  clear() {
    writeCaptured([]);
    console.log('capture buffer cleared');
  },
};

function escapeRe(s) {
  return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

globalThis.spb = spb;
console.log('%csurvey pathway bot loaded', 'font-weight:bold');
console.log('spb.inspect()  spb.fill({S1: 2})  spb.step()  spb.capture()  spb.scenario("name")');
