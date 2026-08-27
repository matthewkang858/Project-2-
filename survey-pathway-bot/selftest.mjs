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

  // The shape a modern survey player renders: the real <input> hidden behind a
  // styled label, and the question body arriving after the page does.
  {
    const o = join(out, 'styled');
    const r = await run(['explore.mjs', '--url', URL + 'styled', '--out', o, '--max-runs', '4']);
    const ts = readdirSync(join(o, 'runs')).map((f) => JSON.parse(readFileSync(join(o, 'runs', f), 'utf8')));
    const picks = new Set(ts.flatMap((t) => t.decisions.filter((d) => d.key === 'ST1').map((d) => d.chosenIndex)));
    check(r.code === 0 && picks.size === 4, `answers a question whose inputs are hidden behind styled labels (${picks.size}/4 options tried)`);
    check(ts.every((t) => t.outcome?.type === 'complete'), 'no run gives up on the late-rendering page');
  }

  // An "Other (please specify)" box must stay empty unless its option is taken
  // — typing in it otherwise is a validation error.
  {
    const o = join(out, 'other');
    const r = await run(['explore.mjs', '--url', URL + 'other', '--out', o, '--max-runs', '3']);
    const ts = readdirSync(join(o, 'runs')).map((f) => JSON.parse(readFileSync(join(o, 'runs', f), 'utf8')));
    check(r.code === 0 && ts.every((t) => t.outcome?.type === 'complete'), 'leaves an "other, please specify" box blank unless that option is chosen');
    const blanks = ts.flatMap((t) => t.decisions.filter((d) => d.key === 'oeOT1'));
    check(blanks.some((d) => /not selected/.test(d.chosen)) && blanks.some((d) => /Test/.test(d.chosen)),
      'fills the "other" box only on the run that picks Other');
  }

  // The three shapes that made a field run need a human: "select up to two"
  // checkboxes, percentages that must total 100, and a carousel grid whose
  // cards are moved by its own pager.
  {
    const cases = [
      ['limit', 'respects "select up to two"', (ts) =>
        ts.every((t) => t.decisions.filter((d) => /\[1\]$/.test(d.chosen)).length <= 2)],
      ['sum100', 'makes a percentage group total 100', (ts) =>
        ts.some((t) => t.decisions.filter((d) => d.key.startsWith('SM1')).reduce((n, d) => n + Number((d.chosen.match(/\d+/) || [0])[0]), 0) === 100)],
      ['pager', 'answers every card of a carousel grid', (ts) =>
        ts.some((t) => ['PG1r1', 'PG1r2', 'PG1r3'].every((k) => t.decisions.some((d) => d.key === k)))],
    ];
    for (const [path, label, ok] of cases) {
      const o = join(out, path);
      const r = await run(['explore.mjs', '--url', URL + path, '--out', o, '--max-runs', '3']);
      const ts = readdirSync(join(o, 'runs')).map((f) => JSON.parse(readFileSync(join(o, 'runs', f), 'utf8')));
      check(r.code === 0 && ok(ts), label);
      check(ts.every((t) => t.outcome?.type === 'complete'), `clears validation on the ${path} page`);
      if (path === 'limit') {
        const md = readFileSync(join(o, 'REPORT.md'), 'utf8');
        check(/\| `LM1` /.test(md) && !/\| `LM1r1` /.test(md), 'coverage reports one row per question, not one per checkbox');
      }
    }
  }

  // Widgets that a plain form reader cannot drive: native + custom sliders, and
  // a carousel that reveals one question at a time without a page load.
  for (const [path, label, expectKeys] of [
    ['slider', 'sliders (native and ARIA)', ['SL1', 'SL2_s']],
    ['carousel', 'a carousel that reveals cards as you answer', ['C1', 'C2', 'C3']],
  ]) {
    const o = join(out, path);
    const r = await run(['explore.mjs', '--url', URL + path, '--out', o, '--max-runs', '2']);
    const ts = readdirSync(join(o, 'runs')).map((f) => JSON.parse(readFileSync(join(o, 'runs', f), 'utf8')));
    const keys = new Set(ts.flatMap((t) => t.decisions.map((d) => d.key)));
    check(r.code === 0 && expectKeys.every((k) => keys.has(k)), `answers ${label}`);
    check(ts.some((t) => t.outcome?.type === 'complete'), `completes the survey through ${label}`);
    check(
      !ts.some((t) => t.decisions.filter((d) => d.key === expectKeys[0]).length > 1),
      `does not re-answer the same question when it stays on screen (${path})`
    );
  }

  const paths = await run(['run-paths.mjs', '--url', URL, '--paths', 'paths.example.json', '--out', out]);
  process.stdout.write(paths.stdout.replace(/^/gm, '      '));
  check(paths.code === 0, 'all scripted scenarios in paths.example.json pass');
} finally {
  server.kill();
}

console.log(fails.length ? `\n${fails.length} check(s) failed` : '\nall checks passed');
process.exit(fails.length ? 1 : 0);
