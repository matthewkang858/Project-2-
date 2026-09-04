#!/usr/bin/env node
// End-to-end check of the *in-browser* tools: the Chrome extension and the
// console snippet, both driven against mock/server.mjs in a real Chromium.
//
//   node selftest-browser.mjs
//
// (node selftest.mjs covers the Playwright CLI.)

import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const PORT = 8124;
const URL_ = `http://127.0.0.1:${PORT}/`;
const EXT = resolve('./chrome-extension');
const fails = [];
const check = (ok, msg) => { console.log(`${ok ? 'ok  ' : 'FAIL'}  ${msg}`); if (!ok) fails.push(msg); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const server = spawn(process.execPath, ['mock/server.mjs', String(PORT)], { stdio: 'ignore' });
await sleep(700);

const ctx = await chromium.launchPersistentContext(mkdtempSync(join(tmpdir(), 'spb-profile-')), {
  executablePath: '/opt/pw-browsers/chromium',
  headless: true,
  args: [`--disable-extensions-except=${EXT}`, `--load-extension=${EXT}`],
});

try {
  // ---- console snippet -------------------------------------------------
  const snippet = readFileSync('./dist/console-snippet.js', 'utf8');
  const page = await ctx.newPage();
  await page.goto(URL_);
  await page.evaluate(snippet);
  const seen = await page.evaluate(() => {
    const m = spb.inspect();
    return { keys: m.questions.map((q) => q.key), next: !!m.next, options: m.questions[0].options.length };
  });
  check(seen.keys.join(',') === 'S1' && seen.next && seen.options === 4, 'snippet reads the page (S1, 4 options, next button)');
  await page.evaluate(() => spb.fill({ S1: /55 or older/ }));
  const captured = await page.evaluate(() => spb.capture());
  check(captured.length === 1 && /55 or older/.test(captured[0].fixed), 'snippet captures the answer chosen on the page');
  await page.evaluate(() => spb.next());
  await page.waitForLoadState('domcontentloaded');
  await sleep(400);
  const advanced = await page.evaluate(() => [...document.querySelectorAll('.question')].map((d) => d.id));
  check(advanced.join(',') === 'S2,S3', 'snippet advances to the next page');
  await page.close();

  // ---- snippet: automatic (iframe) mode ---------------------------------
  const auto = await ctx.newPage();
  await auto.goto(URL_);
  await auto.evaluate(snippet);
  const autoTraces = await auto.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 14, config: { delay: 0 } }), URL_);
  const autoOutcomes = new Set((autoTraces || []).map((t) => t.outcome?.type));
  check(autoTraces?.length === 14, `snippet auto mode completed 14 traversals (got ${autoTraces?.length})`);
  for (const want of ['terminate', 'quota', 'complete'])
    check(autoOutcomes.has(want), `snippet auto mode found the "${want}" end state`);
  check(!autoOutcomes.has('stalled') && !autoOutcomes.has('error'), 'no snippet auto run stalled or errored');
  check(
    (autoTraces || []).some((t) => t.outcome?.type === 'complete' && !t.steps.some((s) => s.questionKeys.includes('Q2r1'))),
    'snippet auto mode found the skipped-grid branch'
  );
  const autoMd = await auto.evaluate(() => spb.report());
  check(!!autoMd && autoMd.includes('flowchart TD'), 'snippet renders the report');
  check(await auto.evaluate(() => !document.querySelector('iframe')), 'snippet removes its iframe when finished');
  await auto.close();

  // ---- snippet: survey inside an iframe ---------------------------------
  const framed = await ctx.newPage();
  await framed.goto(URL_ + 'framed');
  await framed.evaluate(snippet);
  const framedTraces = await framed.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 4, config: { delay: 0 } }), URL_ + 'framed');
  check(
    (framedTraces || []).some((t) => t.decisions.length >= 8),
    'snippet drives a survey nested inside an iframe'
  );
  check(
    (framedTraces || []).some((t) => ['complete', 'quota', 'terminate'].includes(t.outcome?.type)),
    'snippet reads the end state from inside the frame'
  );
  await framed.close();

  // ---- snippet: sliders, carousel, and stopping mid-run ------------------
  for (const [path, keys, label] of [
    ['slider', ['SL1', 'SL2_s'], 'sliders'],
    ['carousel', ['C1', 'C2', 'C3'], 'a carousel'],
  ]) {
    const w = await ctx.newPage();
    await w.goto(URL_ + path);
    await w.evaluate(snippet);
    const ts = await w.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 2, config: { delay: 0, manualTimeout: 0 } }), URL_ + path);
    const seen = new Set((ts || []).flatMap((t) => t.decisions.map((d) => d.key)));
    check(keys.every((k) => seen.has(k)), `snippet answers ${label}`);
    check((ts || []).some((t) => t.outcome?.type === 'complete'), `snippet completes the survey through ${label}`);
    await w.close();
  }

  const cardsPage = await ctx.newPage();
  await cardsPage.goto(URL_ + 'cards');
  await cardsPage.evaluate(snippet);
  const cardTraces = (await cardsPage.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 3, config: { delay: 0 } }), URL_ + 'cards')) || [];
  check(
    cardTraces.length === 3 && cardTraces.every((t) => t.outcome?.type === 'complete'),
    'snippet completes a button-driven card carousel'
  );
  await cardsPage.close();

  const rer = await ctx.newPage();
  await rer.goto(URL_ + 'rerender');
  await rer.evaluate(snippet);
  const rerTraces = (await rer.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 3, config: { delay: 900 } }), URL_ + 'rerender')) || [];
  check(
    rerTraces.length === 3 && rerTraces.every((t) => t.outcome?.type === 'complete'),
    'snippet answers a question whose answer list is repainted'
  );
  await rer.close();

  const styled = await ctx.newPage();
  await styled.goto(URL_ + 'styled');
  await styled.evaluate(snippet);
  const styledTraces = await styled.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 4, config: { delay: 0 } }), URL_ + 'styled');
  const styledPicks = new Set((styledTraces || []).flatMap((t) => t.decisions.filter((d) => d.key === 'ST1').map((d) => d.chosenIndex)));
  check(styledPicks.size === 4, `snippet answers inputs hidden behind styled labels (${styledPicks.size}/4 options)`);
  const dbg = await styled.evaluate(() => spb.debug());
  check(typeof dbg.controlsInDom === 'number' && Array.isArray(dbg.buttonsOnPage), 'spb.debug() dumps what the page contains');
  await styled.close();

  const qx = await ctx.newPage();
  await qx.goto(URL_ + 'qualtrics');
  await qx.evaluate(snippet);
  const qxTraces = (await qx.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 3, config: { delay: 0, manualTimeout: 0 } }), URL_ + 'qualtrics')) || [];
  const qxComplete = qxTraces.filter((t) => t.outcome?.type === 'complete');
  const qxBlankPicked = qxTraces.some((t) => t.decisions.some((d) => /~null/.test(d.chosen || '')));
  const qxGroups = new Set(qxTraces.flatMap((t) => (t.steps || []).flatMap((s) => (s.questions || []).map((q) => q.key))));
  check(qxComplete.length >= 2 && !qxBlankPicked, `snippet completes Qualtrics-style markup without picking the blank placeholder (${qxComplete.length}/3 complete)`);
  check([...qxGroups].some((k) => k.startsWith('QR~QID3~')), 'snippet reads tilde-named Qualtrics checkboxes');
  await qx.close();

  // Qualtrics radio list (SAVR): opacity:0 input under an empty q-radio overlay,
  // text in a separate label, and Next gated on the engine's own change-driven
  // state rather than input.checked.
  const qr = await ctx.newPage();
  await qr.goto(URL_ + 'qradio');
  await qr.evaluate(snippet);
  const qrTraces = (await qr.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 2, config: { delay: 0, manualTimeout: 0 } }), URL_ + 'qradio')) || [];
  const qrComplete = qrTraces.filter((t) => t.outcome?.type === 'complete');
  const qrLabels = new Set(qrTraces.flatMap((t) => t.decisions.map((d) => d.chosen || '')));
  check(qrComplete.length === 2, `snippet completes a Qualtrics radio list (${qrComplete.length}/2 complete)`);
  check([...qrLabels].some((l) => /\$20,000/.test(l)), 'snippet captures Qualtrics radio option text past the empty overlay label');
  await qr.close();

  // Numeric money write-in that rejects words and over-max values.
  const qn = await ctx.newPage();
  await qn.goto(URL_ + 'qnumeric');
  await qn.evaluate(snippet);
  const qnTraces = (await qn.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 1, config: { delay: 0, manualTimeout: 0 } }), URL_ + 'qnumeric')) || [];
  const qnVals = qnTraces.flatMap((t) => t.decisions.map((d) => d.chosen || ''));
  check(qnTraces.some((t) => t.outcome?.type === 'complete'), 'snippet completes a numeric money write-in (fills a number, not "Test")');
  check(qnVals.every((v) => !/test/i.test(v)), 'snippet never types "Test" into a numeric field');
  await qn.close();

  // Single-session exploration: a survey that cannot be reloaded (ballot-box
  // wall on reload) with a Back button and a display-gated question (BQ3 shows
  // only when BQ2="Yes"). explore() must backtrack, cover both branches, and
  // never trip the reload wall.
  const bt = await ctx.newPage();
  await bt.goto(URL_); // base page, so the iframe is the only load of /backtrack (shared tab sessionStorage)
  await bt.evaluate(snippet);
  const btTraces = (await bt.evaluate(async (u) => await spb.explore({ url: u, maxRuns: 6, config: { delay: 0, manualTimeout: 0 } }), URL_ + 'backtrack')) || [];
  const btKeys = new Set(btTraces.flatMap((t) => (t.steps || []).flatMap((s) => (s.questions || []).map((q) => q.key))));
  const btComplete = btTraces.filter((t) => t.outcome?.type === 'complete').length;
  const sawGated = btTraces.some((t) => (t.steps || []).some((s) => (s.questions || []).some((q) => q.key === 'QR~BQ3')));
  const sawUngated = btTraces.some((t) => !(t.steps || []).some((s) => (s.questions || []).some((q) => q.key === 'QR~BQ3')));
  const noWall = !btTraces.some((t) => /already responded/i.test(t.outcome?.text || ''));
  check(btComplete >= 2, `explore() completes multiple paths in one session (${btComplete} complete)`);
  check(btKeys.has('QR~BQ1') && btKeys.has('QR~BQ4'), 'explore() covers the shared questions');
  check(sawGated && sawUngated, 'explore() covers both arms of a display-gated question (BQ3 shown and skipped)');
  check(noWall, 'explore() never reloads into the ballot-box wall');
  await bt.close();

  // Graceful degrade: when the thank-you page blocks Back, explore() still
  // returns the one completed path instead of erroring.
  const bd = await ctx.newPage();
  await bd.goto(URL_);
  await bd.evaluate(snippet);
  const bdTraces = (await bd.evaluate(async (u) => await spb.explore({ url: u, maxRuns: 6, config: { delay: 0, manualTimeout: 0 } }), URL_ + 'backtrack?deadend=1')) || [];
  check(bdTraces.some((t) => t.outcome?.type === 'complete'), 'explore() still captures a full path when the end blocks Back');
  await bd.close();

  // maxForward: on a dead-end-terminal survey, capping each walk before the end
  // lets exploration sweep many branches in one session without stranding.
  const cap = await ctx.newPage();
  await cap.goto(URL_);
  await cap.evaluate(snippet);
  const capTraces = (await cap.evaluate(async (u) => await spb.explore({ url: u, maxRuns: 6, maxForward: 3, config: { delay: 0, manualTimeout: 0 } }), URL_ + 'backtrack?deadend=1')) || [];
  const capKeys = new Set(capTraces.flatMap((t) => (t.steps || []).flatMap((s) => (s.questions || []).map((q) => q.key))));
  const capGatedBoth = capTraces.some((t) => (t.steps || []).some((s) => (s.questions || []).some((q) => q.key === 'QR~BQ3'))) &&
    capTraces.some((t) => !(t.steps || []).some((s) => (s.questions || []).some((q) => q.key === 'QR~BQ3')));
  check(capTraces.length >= 3, `maxForward lets explore() sweep multiple branches past a dead-end terminal (${capTraces.length} runs)`);
  check(capGatedBoth, 'maxForward run still covers both arms of the gated question without submitting the end');
  await cap.close();

  for (const [path, label, keys] of [
    ['limit', 'respects "select up to two"', null],
    ['pager', 'answers every card of a carousel grid', ['PG1r1', 'PG1r2', 'PG1r3']],
    ['sum100', 'makes a percentage group total 100', null],
  ]) {
    const w = await ctx.newPage();
    await w.goto(URL_ + path);
    await w.evaluate(snippet);
    const ts = (await w.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 2, config: { delay: 0, manualTimeout: 0 } }), URL_ + path)) || [];
    let ok = ts.some((t) => t.outcome?.type === 'complete');
    if (keys) ok = ok && ts.some((t) => keys.every((k) => t.decisions.some((d) => d.key === k)));
    if (path === 'limit') ok = ok && ts.every((t) => t.decisions.filter((d) => /\[1\]$/.test(d.chosen)).length <= 2);
    check(ok, `snippet ${label}`);
    await w.close();
  }

  const stopPage = await ctx.newPage();
  await stopPage.goto(URL_);
  await stopPage.evaluate(snippet);
  const stopped = await stopPage.evaluate(async (u) => {
    const running = spb.auto({ url: u, maxRuns: 40, config: { delay: 60 } });
    await new Promise((r) => setTimeout(r, 1500));
    const n = spb.stop();
    await running;
    return { stoppedAt: n, traces: spb.allTraces().length, report: (spb.report() || '').slice(0, 40) };
  }, URL_);
  check(stopped.traces > 0 && stopped.traces < 40, `spb.stop() ends the run and keeps its traversals (${stopped.traces})`);
  check(stopped.report.includes('Survey pathway test report'), 'a report is available after stopping');
  await stopPage.close();

  // ---- snippet: login-wall diagnostics ----------------------------------
  // The failure that produced an empty report in the field: a start URL that
  // renders an interstitial instead of the questionnaire.
  const wall = await ctx.newPage();
  const wallLogs = [];
  wall.on('console', (m) => wallLogs.push(m.text()));
  await wall.goto(URL_ + 'wall');
  await wall.evaluate(snippet);
  const wallResult = await wall.evaluate(async (u) => await spb.auto({ url: u, maxRuns: 5, config: { delay: 0 } }), URL_ + 'wall');
  check(wallResult === null, 'auto mode refuses to run when the start page has no questions');
  check(
    wallLogs.some((t) => /login|interstitial/i.test(t)),
    'auto mode names the login wall as the reason'
  );
  await wall.evaluate(async (u) => await spb.check({ url: u }), URL_ + 'wall');
  check(wallLogs.some((t) => /questions found: 0/.test(t)), 'spb.check() reports what it found on the page');
  await wall.close();

  // A welcome page is not a wall: check() should click through it and report on
  // the first real question instead of crying login.
  const intro = await ctx.newPage();
  const introLogs = [];
  intro.on('console', (m) => introLogs.push(m.text()));
  await intro.goto(URL_ + 'intro');
  await intro.evaluate(snippet);
  const introCheck = await intro.evaluate(async (u) => {
    const r = await spb.check({ url: u });
    return { questions: r.frame ? r.frame.questions.map((q) => q.key) : [] };
  }, URL_ + 'intro');
  check(introCheck.questions.includes('S1'), 'spb.check() clicks past the welcome page to the first question');
  check(introLogs.some((t) => /welcome \/ intro page/.test(t)), 'spb.check() calls a welcome page what it is');
  check(!introLogs.some((t) => /login \/ interstitial/.test(t)), 'spb.check() does not cry login on a working welcome page');
  await intro.close();

  // ---- snippet: step-through mode ---------------------------------------
  // Simulates the user pressing Ctrl+Enter on each page: the snippet is
  // re-evaluated after every navigation and resumes from sessionStorage.
  const stepPage = await ctx.newPage();
  await stepPage.goto(URL_);
  await stepPage.evaluate(snippet);
  await stepPage.evaluate(() => spb.plan({ maxRuns: 3, config: { delay: 0 } }));
  let active = true;
  for (let i = 0; i < 40 && active; i++) {
    await stepPage.waitForLoadState('domcontentloaded').catch(() => {});
    await sleep(150);
    try {
      await stepPage.evaluate(snippet);
    } catch {
      continue; // navigation tore down the context; the next loop re-injects
    }
    active = await stepPage
      .evaluate(() => {
        try {
          return !!JSON.parse(sessionStorage.getItem('spb-step-state'))?.active;
        } catch {
          return false;
        }
      })
      .catch(() => true); // navigating — still going
  }
  const stepTraces = await stepPage.evaluate(() => spb.allTraces());
  const stepOutcomes = new Set(stepTraces.map((t) => t.outcome?.type));
  check(stepTraces.length === 3, `snippet step mode completed 3 traversals (got ${stepTraces.length})`);
  check(stepOutcomes.has('terminate') && stepOutcomes.has('complete'), 'snippet step mode reached different end states');
  await stepPage.close();

  // ---- chrome extension ------------------------------------------------
  let sw = ctx.serviceWorkers()[0] ?? (await ctx.waitForEvent('serviceworker', { timeout: 15000 }));
  const extId = new URL(sw.url()).host;
  const popup = await ctx.newPage();
  await popup.goto(`chrome-extension://${extId}/popup.html`);
  await popup.fill('#url', URL_);
  await popup.fill('#maxRuns', '14');
  await popup.fill('#delay', '80');
  await popup.click('#start');

  const deadline = Date.now() + 120000;
  let state = null;
  while (Date.now() < deadline) {
    await sleep(1000);
    state = await sw.evaluate(async () => (await chrome.storage.local.get('spb-state'))['spb-state'] ?? null).catch(() => null);
    if (state && !state.running && state.traces?.length) break;
  }
  const traces = state?.traces ?? [];
  const outcomes = new Set(traces.map((t) => t.outcome?.type));
  check(traces.length === 14, `extension completed 14 traversals (got ${traces.length})`);
  for (const want of ['terminate', 'quota', 'complete']) check(outcomes.has(want), `extension found the "${want}" end state`);
  check(!outcomes.has('stalled') && !outcomes.has('error'), 'no extension run stalled or errored');
  check(
    traces.some((t) => t.steps.some((s) => s.questionKeys.includes('Q2r1'))) &&
      traces.some((t) => t.outcome?.type === 'complete' && !t.steps.some((s) => s.questionKeys.includes('Q2r1'))),
    'extension found both branches of the conditional rating grid'
  );
  const md = await popup.evaluate((t) => SPB_REPORT.buildReport(t, { url: 'mock' }), traces);
  check(md.includes('flowchart TD') && md.includes('Answer-option coverage'), 'extension renders the same Markdown report as the CLI');
} finally {
  await ctx.close();
  server.kill();
}

console.log(fails.length ? `\n${fails.length} check(s) failed` : '\nall checks passed');
process.exit(fails.length ? 1 : 0);
