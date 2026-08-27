#!/usr/bin/env node
// End-to-end check of the toolkit against mock/server.mjs. No network needed.
//
//   node selftest.mjs
//
// Asserts that exploration finds all three end states, that it discovers the
// conditional page being skipped, and that the scripted scenarios in
// paths.example.json all pass.

import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const PORT = 8123;
const URL = `http://127.0.0.1:${PORT}/`;
const out = mkdtempSync(join(tmpdir(), 'spb-selftest-'));
const fails = [];
const check = (ok, msg) => { console.log(`${ok ? 'ok  ' : 'FAIL'}  ${msg}`); if (!ok) fails.push(msg); };

const run = (args) =>
  new Promise((resolve) => {
    const p = spawn(process.execPath, args, { stdio: ['ignore', 'pipe', 'pipe'] });
    let so = '', se = '';
    p.stdout.on('data', (d) => (so += d));
    p.stderr.on('data', (d) => (se += d));
    p.on('close', (code) => resolve({ code, stdout: so, stderr: se }));
  });

const server = spawn(process.execPath, ['mock/server.mjs', String(PORT)], { stdio: 'ignore' });
await new Promise((r) => setTimeout(r, 700));

try {
  const explore = await run(['explore.mjs', '--url', URL, '--out', out, '--max-runs', '14']);
  check(explore.code === 0, 'explore.mjs exits 0');
  const traces = readdirSync(join(out, 'runs')).map((f) => JSON.parse(readFileSync(join(out, 'runs', f), 'utf8')));
  const outcomes = new Set(traces.map((t) => t.outcome?.type));
  check(traces.length === 14, `14 traversals recorded (got ${traces.length})`);
  for (const want of ['terminate', 'quota', 'complete'])
    check(outcomes.has(want), `discovered the "${want}" end state`);
  check(!outcomes.has('error') && !outcomes.has('stalled'), 'no run errored or stalled');
  check(
    traces.some((t) => t.steps.some((s) => s.questionKeys.includes('Q2r1'))) &&
      traces.some((t) => t.steps.length === 5 && !t.steps.some((s) => s.questionKeys.includes('Q2r1'))),
    'found both branches of the conditional rating grid'
  );
  const report = readFileSync(join(out, 'REPORT.md'), 'utf8');
  check(report.includes('flowchart TD'), 'report contains a pathway map');
  check(/`S3`.*select.*\| 3 \| 3 \|/.test(report), 'report shows full option coverage for the dropdown');
  check(report.includes('18–34'), 'option labels are read as UTF-8');

  // A welcome page whose only forward control is a plain <button>Continue</button>,
  // and the same survey embedded in a host page — the two shapes that made a
  // field run stop on page one.
  for (const [path, label] of [['intro', 'welcome page with a text-only Continue button'], ['framed', 'survey inside an iframe']]) {
    const o = join(out, path);
    const r = await run(['explore.mjs', '--url', URL + path, '--out', o, '--max-runs', '4']);
    const ts = readdirSync(join(o, 'runs')).map((f) => JSON.parse(readFileSync(join(o, 'runs', f), 'utf8')));
    check(r.code === 0 && ts.some((t) => t.decisions.length >= 8), `walks past a ${label}`);
    check(ts.some((t) => ['complete', 'quota', 'terminate'].includes(t.outcome?.type)), `reaches a real end state through the ${label}`);
  }

  const paths = await run(['run-paths.mjs', '--url', URL, '--paths', 'paths.example.json', '--out', out]);
  process.stdout.write(paths.stdout.replace(/^/gm, '      '));
  check(paths.code === 0, 'all scripted scenarios in paths.example.json pass');
} finally {
  server.kill();
}

console.log(fails.length ? `\n${fails.length} check(s) failed` : '\nall checks passed');
process.exit(fails.length ? 1 : 0);
