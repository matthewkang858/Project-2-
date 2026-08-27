// Orchestrator. Owns the run queue and every trace; the content script only
// ever handles one page.
//
// Exploration strategy is the same as the CLI's: run 1 takes the first option
// everywhere, then each queued run replays a previous run's answers up to one
// decision, flips that decision, and continues — breadth-first, so screener
// logic gets covered first.
//
// All state lives in chrome.storage.local because an MV3 service worker can be
// shut down between two messages.

const KEY = 'spb-state';
const BLANK = {
  running: false,
  tabId: null,
  startUrl: '',
  config: {},
  maxRuns: 20,
  maxSteps: 200,
  clearCookies: false,
  queue: [[]],
  seen: [''],
  runs: 0,
  current: null,
  traces: [],
  status: 'idle',
};

const getState = async () => ({ ...BLANK, ...((await chrome.storage.local.get(KEY))[KEY] || {}) });
const setState = (s) => chrome.storage.local.set({ [KEY]: s });

// Serialise handlers so two messages can't interleave a read-modify-write.
let chain = Promise.resolve();
const queued = (fn) => (chain = chain.then(fn, fn));

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

async function startRun(state) {
  const plan = state.queue.shift();
  state.runs += 1;
  state.current = {
    runId: `run-${String(state.runs).padStart(3, '0')}`,
    plan,
    di: 0,
    steps: [],
    decisions: [],
    startedAt: new Date().toISOString(),
  };
  state.status = `running ${state.current.runId} (plan [${plan.join(',')}])`;
  await setState(state);

  if (state.clearCookies) {
    try {
      await chrome.browsingData.remove({ origins: [new URL(state.startUrl).origin] }, { cookies: true, localStorage: true });
    } catch (e) {
      console.warn('cookie clear failed', e);
    }
  }
  await chrome.tabs.update(state.tabId, { url: state.startUrl });
}

async function finishRun(state, type, extra = {}) {
  const c = state.current;
  if (!c) return;
  const last = c.steps[c.steps.length - 1] || {};
  const trace = {
    runId: c.runId,
    plan: c.plan,
    startedAt: c.startedAt,
    finishedAt: new Date().toISOString(),
    steps: c.steps,
    decisions: c.decisions,
    outcome: {
      type,
      heading: last.heading || '',
      text: extra.text || '',
      url: last.url || '',
      atFingerprint: type === 'stalled' ? last.fingerprint : undefined,
    },
    pathKey: c.decisions.map((d) => `${d.key}=${d.chosenIndex}`).join('>'),
    pageKey: c.steps.map((s) => s.fingerprint).join('>'),
  };
  state.traces.push(trace);
  state.current = null;
  expand(state, trace);

  if (state.running && state.runs < state.maxRuns && state.queue.length) {
    await startRun(state);
  } else {
    state.running = false;
    state.status = `finished — ${state.traces.length} run(s), ${state.queue.length} branch(es) untried`;
    await setState(state);
  }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  queued(async () => {
    const state = await getState();

    // ---- popup ----------------------------------------------------------
    if (msg.type === 'start') {
      const fresh = {
        ...BLANK,
        running: true,
        startUrl: msg.startUrl,
        config: msg.config || {},
        maxRuns: Number(msg.maxRuns || 20),
        maxSteps: Number(msg.config?.maxSteps || 200),
        clearCookies: !!msg.clearCookies,
        traces: msg.keepTraces ? state.traces : [],
        runs: msg.keepTraces ? state.runs : 0,
      };
      const tab = await chrome.tabs.create({ url: 'about:blank', active: true });
      fresh.tabId = tab.id;
      await setState(fresh);
      await startRun(await getState());
      sendResponse({ ok: true });
      return;
    }
    if (msg.type === 'stop') {
      state.running = false;
      state.current = null;
      state.status = `stopped — ${state.traces.length} run(s) recorded`;
      await setState(state);
      sendResponse({ ok: true });
      return;
    }
    if (msg.type === 'status') {
      sendResponse({
        running: state.running,
        status: state.status,
        runs: state.traces.length,
        queued: state.queue.length,
        maxRuns: state.maxRuns,
        traces: msg.withTraces ? state.traces : undefined,
        startUrl: state.startUrl,
      });
      return;
    }

    // ---- content script -------------------------------------------------
    const fromRunTab = sender.tab && sender.tab.id === state.tabId;
    if (!state.running || !fromRunTab || !state.current) {
      sendResponse({ act: false });
      return;
    }

    if (msg.type === 'page') {
      sendResponse({ act: true, session: { plan: state.current.plan, di: state.current.di, config: state.config } });
      return;
    }
    if (msg.type === 'step') {
      state.current.steps.push({ step: state.current.steps.length, ...msg.record });
      state.current.decisions.push(...(msg.record.decisions || []));
      state.current.di = msg.di;
      if (state.current.steps.length >= state.maxSteps) {
        await finishRun(state, 'maxsteps', { text: `stopped after ${state.maxSteps} pages` });
        sendResponse({ continue: false });
        return;
      }
      await setState(state);
      sendResponse({ continue: true });
      return;
    }
    if (msg.type === 'terminal') {
      state.current.steps.push({ step: state.current.steps.length, ...msg.record });
      await finishRun(state, msg.record.outcome || 'end', { text: msg.text });
      sendResponse({ ok: true });
      return;
    }
    if (msg.type === 'stalled') {
      state.current.steps.push({ step: state.current.steps.length, ...msg.record });
      await finishRun(state, 'stalled', { text: msg.text });
      sendResponse({ ok: true });
      return;
    }
    sendResponse({ act: false });
  });
  return true; // async response
});

chrome.tabs.onRemoved.addListener((tabId) => {
  queued(async () => {
    const state = await getState();
    if (state.tabId !== tabId || !state.running) return;
    state.running = false;
    state.current = null;
    state.status = `stopped — run tab was closed (${state.traces.length} run(s) recorded)`;
    await setState(state);
  });
});
