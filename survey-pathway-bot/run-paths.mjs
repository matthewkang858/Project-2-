#!/usr/bin/env node
// Scripted pathway tests — the regression half of the toolkit.
//
//   node run-paths.mjs --url "<survey url>" --paths paths.json [--screenshots] [--headed]
//
// Each scenario in paths.json pins specific answers ("age = Under 18") and
// asserts what should happen ("outcome is a terminate, and Q1 is never shown").
// Every scenario is one traversal; the run exits non-zero if any assertion
// fails, so it drops straight into CI.

import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { launch, newContext } from './lib/browser.mjs';
import { runOnce } from './lib/run.mjs';

function args(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) continue;
    const next = argv[i + 1];
    if (next && !next.startsWith('--')) { out[a.slice(2)] = next; i++; } else out[a.slice(2)] = true;
  }
  return out;
}

const a = args(process.argv);
if (!a.url || !a.paths) {
  console.error('usage: node run-paths.mjs --url "<survey url>" --paths paths.json');
  process.exit(1);
}

const spec = JSON.parse(readFileSync(a.paths, 'utf8'));
const outDir = a.out ?? './out';
mkdirSync(join(outDir, 'paths'), { recursive: true });

const browser = await launch({ headless: !a.headed, slowMo: a.headed ? 120 : 0 });
const results = [];

for (const scenario of spec.scenarios ?? []) {
  const slug = scenario.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
  // Scenario answers come first so they win over the file-level defaults.
  const config = { ...spec, answers: [...(scenario.answers ?? []), ...(spec.answers ?? [])] };
  const ctx = await newContext(browser);
  const page = await ctx.newPage();
  let trace;
  try {
    trace = await runOnce(page, {
      startUrl: a.url,
      plan: [],
      config,
      runId: slug,
      outDir: join(outDir, 'screenshots'),
      screenshots: !!a.screenshots,
      delay: Number(a.delay ?? spec.delay ?? 0),
      stepTimeout: Number(spec.stepTimeout ?? 20000),
      maxSteps: Number(spec.maxSteps ?? 60),
    });
  } catch (err) {
    trace = { runId: slug, steps: [], decisions: [], outcome: { type: 'error', text: String(err.message ?? err) } };
  }
  await ctx.close();

  const seen = new Set(trace.steps.flatMap((s) => s.questionKeys ?? []));
  const failures = [];
  const e = scenario.expect ?? {};
  if (e.outcome && trace.outcome?.type !== e.outcome)
    failures.push(`expected outcome "${e.outcome}", got "${trace.outcome?.type}"`);
  for (const q of e.sees ?? []) if (![...seen].some((k) => new RegExp(q, 'i').test(k))) failures.push(`expected to be asked ${q}, was not`);
  for (const q of e.notSees ?? []) if ([...seen].some((k) => new RegExp(q, 'i').test(k))) failures.push(`expected NOT to be asked ${q}, but it was shown`);
  if (e.textContains) {
    const txt = (trace.outcome?.text ?? '') + ' ' + (trace.outcome?.heading ?? '');
    if (!new RegExp(e.textContains, 'i').test(txt)) failures.push(`end page did not contain /${e.textContains}/`);
  }
  if (e.maxPages && trace.steps.length > e.maxPages) failures.push(`took ${trace.steps.length} pages, expected at most ${e.maxPages}`);

  trace.scenario = scenario.name;
  trace.failures = failures;
  writeFileSync(join(outDir, 'paths', `${slug}.json`), JSON.stringify(trace, null, 2));
  results.push({ name: scenario.name, slug, pass: failures.length === 0, failures, trace });
  console.log(`${failures.length ? 'FAIL' : 'PASS'}  ${scenario.name}  (${trace.steps.length} pages, ${trace.outcome?.type})`);
  for (const f of failures) console.log(`        ↳ ${f}`);
}

await browser.close();

const md = [
  '# Scripted pathway tests', '',
  `Survey: \`${a.url}\``,
  `Run: ${new Date().toISOString()}`,
  `Result: **${results.filter((r) => r.pass).length}/${results.length} passed**`, '',
  '| Scenario | Result | Pages | Outcome | Questions shown | Failures |',
  '|---|---|---:|---|---|---|',
  ...results.map((r) => {
    const seen = [...new Set(r.trace.steps.flatMap((s) => s.questionKeys ?? []))].join(', ');
    return `| ${r.name} | ${r.pass ? 'PASS' : '**FAIL**'} | ${r.trace.steps.length} | ${r.trace.outcome?.type ?? '?'} | ${seen || '—'} | ${r.failures.join('; ') || '—'} |`;
  }),
  '',
].join('\n');
writeFileSync(join(outDir, 'PATHS.md'), md);
console.log(`\nReport: ${join(outDir, 'PATHS.md')}`);
process.exit(results.some((r) => !r.pass) ? 1 : 0);
