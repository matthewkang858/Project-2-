#!/usr/bin/env node
// Rehearse a survey's coverage paths end to end before touching the live link:
// serve the parsed questionnaire as a Qualtrics-style mock (mock/spec-survey.mjs),
// run each path's exact config through the real console snippet in Chromium,
// and compare the questions the bot actually saw with what the path dry-run
// (outline/simulate_paths.py) predicts.
//
//   node mock-walk.mjs surveys/are01            all paths
//   node mock-walk.mjs surveys/are01 P1 P3      just these
//   node mock-walk.mjs surveys/are01 --alt      against the variant build: bracketed
//     ages, "What is your ZIP code?", "select the number 4", "2–3 times", Q84/Q88 as
//     a multiple-answer question with the amount box inside its choice, and the
//     "would not attend" column of Q83/Q99 as radios

import { chromium } from 'playwright';
import { spawn, execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, basename } from 'node:path';

const args = process.argv.slice(2);
const variant = args.includes('--alt') ? 'alt' : '';
const [dir = 'surveys/are01', ...only] = args.filter((a) => !a.startsWith('--'));
const id = basename(dir);
const PORT = 8131;
const base = JSON.parse(readFileSync(join(dir, 'survey-config.json'), 'utf8'));
const paths = JSON.parse(readFileSync(join(dir, 'paths.json'), 'utf8')).paths.filter((p) => !only.length || only.includes(p.id));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const tmp = mkdtempSync(join(tmpdir(), 'spb-walk-'));
const predicted = join(tmp, 'predicted.json');
try {
  execFileSync('python3', ['outline/simulate_paths.py', join(dir, 'outline-spec.json'), join(dir, 'survey-config.json'), join(dir, 'paths.json'), '--json', predicted], { stdio: 'ignore' });
} catch { /* the dry run exits 1 on its own findings; the JSON is still written */ }
const want = JSON.parse(readFileSync(predicted, 'utf8'));
const checks = JSON.parse(readFileSync(join(dir, 'outline-spec.json'), 'utf8')).attentionChecks || [];

const server = spawn(process.execPath, ['mock/server.mjs', String(PORT)], { stdio: 'ignore' });
await sleep(700);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', headless: true });
const snippet = readFileSync('./dist/console-snippet.js', 'utf8');
let failed = 0;
const out = {};
try {
  for (const p of paths) {
    const page = await browser.newPage();
    await page.goto(`http://127.0.0.1:${PORT}/spec/${id}${variant ? `?variant=${variant}` : ''}`);
    // attention checks as this build words them (the variant rewords AC2)
    const served = await page.evaluate(() => (window.SPEC?.checks || []).map((c) => ({ q: c.q, text: c.text })));
    await page.evaluate(snippet);
    const config = { delay: 0, manualTimeout: 0, maxSteps: base.maxSteps || 400, answers: [...p.answers, ...base.answers] };
    const t0 = Date.now();
    const traces = (await page.evaluate(async (cfg) => { await spb.explore({ maxRuns: 1, config: cfg }); return spb.allTraces(); }, config)) || [];
    const tr = traces[0] || { steps: [] };
    writeFileSync(join(tmp, `${p.id}-traces.json`), JSON.stringify({ traces }));
    const seen = [];
    for (const s of tr.steps || [])
      for (const q of s.questions || []) {
        const m = (q.label || '').match(/^Q(\d+)\./);
        const k = m ? `Q${m[1]}` : ((served.length ? served : checks).find((c) => (q.label || '').startsWith(c.text.trim()))?.q);
        if (k && !seen.includes(k)) seen.push(k);
      }
    const shown = seen.filter((k) => /^Q/.test(k));
    const acs = seen.filter((k) => /^AC/.test(k));
    const exp = want[p.id]?.shown || [];
    const missing = exp.filter((q) => !shown.includes(q));
    const extra = shown.filter((q) => !exp.includes(q));
    const outcome = tr.outcome?.type || 'none';
    const ok = outcome === 'complete' && !missing.length && !extra.length && acs.length === checks.length;
    if (!ok) failed++;
    out[p.id] = { outcome, pages: (tr.steps || []).length, shown, attentionChecks: acs, missing, extra, seconds: Math.round((Date.now() - t0) / 1000) };
    console.log(`${ok ? 'ok  ' : 'FAIL'}  ${p.id} ${p.name}: ${outcome}, ${(tr.steps || []).length} pages, ${shown.length} questions, ` +
      `${acs.length}/${checks.length} attention checks${missing.length ? `; predicted but not reached: ${missing.join(' ')}` : ''}` +
      `${extra.length ? `; reached but not predicted: ${extra.join(' ')}` : ''}${tr.outcome?.text && outcome !== 'complete' ? ` — ${String(tr.outcome.text).slice(0, 140)}` : ''}`);
    if (!ok) {
      const last = (tr.steps || []).slice(-2).map((s) => (s.questions || []).map((q) => q.label?.slice(0, 80)).join(' | '));
      console.log('      last pages:', JSON.stringify(last));
    }
    await page.close();
  }
} finally {
  await browser.close();
  server.kill();
}
writeFileSync(join(tmp, 'walk.json'), JSON.stringify(out, null, 1));
console.log(`\n${failed ? `${failed} path(s) failed` : 'every path completed and matched its dry run'}  (details: ${join(tmp, 'walk.json')})`);
process.exit(failed ? 1 : 0);
