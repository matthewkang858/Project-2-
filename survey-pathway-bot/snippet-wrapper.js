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
    console.log(`spb.check()                 is this page the survey, and can it be framed?
spb.auto({ maxRuns: 20 })   explore every pathway automatically (iframe mode)
spb.plan({ maxRuns: 20 })   step-through mode: re-run this snippet on each page
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

    const first = C.readPage(cfg.selectors, docOf());
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
          const target = C.docFor(model, doc);
          const answered = answerPage(model, plan, di, cfg, target);
          di = answered.di;
          steps.push(answered.record);
          decisions.push(...answered.record.decisions);

          await sleep(delay);
          const before = model.fingerprint + '|' + model.url;
          C.clickNext(model, target);
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
