#!/usr/bin/env node
// Pathway discovery.
//
//   node explore.mjs --url "<survey test link>" [--config config.json] [options]
//
// Walks the survey once taking the first option everywhere, then repeatedly
// re-walks it flipping one earlier decision at a time (breadth-first), so each
// run explores a branch no previous run took. Every run is written to
// <out>/runs/*.json and summarised by report.mjs.
//
// Options:
//   --url URL            survey start URL (required)
//   --config FILE        JSON config: answer rules, branching limits, selectors
//   --out DIR            output directory (default ./out)
//   --max-runs N         stop after N complete traversals (default 25)
//   --screenshots        full-page PNG of every page of every run
//   --headed             show the browser
//   --delay MS           pause before each page submit (default 0)
//   --manual SECONDS     when a page cannot be driven, wait this long for you to
//                        handle it by hand (use with --headed), then carry on

import { mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { launch, newContext } from './lib/browser.mjs';
import { runOnce } from './lib/run.mjs';
import { buildReport } from './report.mjs';

function args(argv) {
  const out = { _: [] };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) { out[key] = next; i++; } else out[key] = true;
    } else out._.push(a);
  }
  return out;
}

const a = args(process.argv);
if (!a.url) {
  console.error('usage: node explore.mjs --url "<survey url>" [--config config.json] [--max-runs 25]');
  process.exit(1);
}

const outDir = a.out ?? './out';
const runsDir = join(outDir, 'runs');
const shotsDir = join(outDir, 'screenshots');
mkdirSync(runsDir, { recursive: true });

const config = a.config && existsSync(a.config) ? JSON.parse(readFileSync(a.config, 'utf8')) : {};
const maxRuns = Number(a['max-runs'] ?? config.maxRuns ?? 25);

const browser = await launch({ headless: !a.headed, slowMo: a.headed ? 120 : 0 });

const queue = [[]];               // plans still to try, breadth-first
const seenPlans = new Set(['']);  // plan keys already queued
const traces = [];

let n = 0;
while (queue.length && n < maxRuns) {
  const plan = queue.shift();
  const runId = `run-${String(++n).padStart(3, '0')}`;
  const ctx = await newContext(browser);
  const page = await ctx.newPage();
  let trace;
  try {
    trace = await runOnce(page, {
      startUrl: a.url,
      plan,
      config,
      runId,
      outDir: shotsDir,
      screenshots: !!a.screenshots,
      delay: Number(a.delay ?? config.delay ?? 0),
      manualTimeout: Number(a.manual ?? config.manualTimeout ?? 0) * 1000,
      stepTimeout: Number(config.stepTimeout ?? 20000),
      maxSteps: Number(config.maxSteps ?? 60),
    });
  } catch (err) {
    trace = { runId, plan, decisions: [], steps: [], outcome: { type: 'error', text: String(err.message ?? err) } };
  }
  await ctx.close();

  writeFileSync(join(runsDir, `${runId}.json`), JSON.stringify(trace, null, 2));
  traces.push(trace);
  console.log(
    `${runId}  plan=[${plan.join(',')}]  pages=${trace.steps.length}  ` +
      `outcome=${trace.outcome?.type}  path=${trace.decisions.map((d) => `${d.key}:${d.chosenIndex}`).join(' > ') || '(none)'}`
  );

  // Enqueue "same prefix, different choice here" for every decision that had
  // more than one candidate. Breadth-first, so shallow branches (screeners,
  // where most survey logic lives) are covered first.
  for (let i = 0; i < trace.decisions.length; i++) {
    const d = trace.decisions[i];
    if (!d || d.candidateCount <= 1) continue;
    const prefix = trace.decisions.slice(0, i).map((x) => x.chosenIndex ?? 0);
    for (let alt = 0; alt < d.candidateCount; alt++) {
      if (alt === d.chosenIndex) continue;
      const p = [...prefix, alt];
      // Trailing zeros are implicit (an unplanned decision takes option 0), so
      // normalise before dedup or the same pathway gets walked twice.
      const norm = [...p];
      while (norm.length && norm[norm.length - 1] === 0) norm.pop();
      const key = norm.join(',');
      if (seenPlans.has(key)) continue;
      seenPlans.add(key);
      queue.push(p);
    }
  }
}

await browser.close();

const summary = {
  url: a.url,
  generatedAt: new Date().toISOString(),
  runs: traces.length,
  plansQueuedButNotRun: queue.length,
  maxRuns,
};
writeFileSync(join(outDir, 'summary.json'), JSON.stringify(summary, null, 2));
writeFileSync(join(outDir, 'REPORT.md'), buildReport(traces, summary));
console.log(`\n${traces.length} run(s). ${queue.length} untried branch(es) left in the queue.`);
console.log(`Report: ${join(outDir, 'REPORT.md')}`);
