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
