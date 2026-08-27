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
          visit.count = visit.answered === answered.size ? visit.count + 1 : 1;
          visit.answered = answered.size;
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
          if (current.pager && !current.pager.atEnd) {
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
    const nav = model.pager && !model.pager.atEnd ? { next: { selector: model.pager.selector } } : model;
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
  console.log('%csurvey pathway bot loaded', 'font-weight:bold');
  console.log('spb.auto()  explore everything automatically   ·   spb.help()  all commands');
}
