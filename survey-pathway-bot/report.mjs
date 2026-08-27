#!/usr/bin/env node
// Turns run traces into a QA report: pathway flow graph, per-option coverage,
// and the list of things that went wrong. The rendering itself lives in
// chrome-extension/report-core.js so the Chrome extension emits the same file.
//
//   node report.mjs [outDir]                 # re-render <outDir>/REPORT.md from <outDir>/runs
//   node report.mjs --traces spb-traces.json # render traces exported by the Chrome extension

import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { buildReport } from './lib/report-core.mjs';

export { buildReport };

if (import.meta.url === `file://${process.argv[1]}`) {
  const traceArg = process.argv.indexOf('--traces');
  if (traceArg !== -1) {
    const file = process.argv[traceArg + 1];
    const parsed = JSON.parse(readFileSync(file, 'utf8'));
    const traces = Array.isArray(parsed) ? parsed : parsed.traces ?? [];
    const summary = Array.isArray(parsed) ? {} : parsed.summary ?? {};
    const out = join(dirname(file), 'REPORT.md');
    writeFileSync(out, buildReport(traces, summary));
    console.log(`wrote ${out} from ${traces.length} run(s)`);
  } else {
    const outDir = process.argv[2] ?? './out';
    const runsDir = join(outDir, 'runs');
    const traces = readdirSync(runsDir)
      .filter((f) => f.endsWith('.json'))
      .sort()
      .map((f) => JSON.parse(readFileSync(join(runsDir, f), 'utf8')));
    const summary = existsSync(join(outDir, 'summary.json'))
      ? JSON.parse(readFileSync(join(outDir, 'summary.json'), 'utf8'))
      : {};
    writeFileSync(join(outDir, 'REPORT.md'), buildReport(traces, summary));
    console.log(`wrote ${join(outDir, 'REPORT.md')} from ${traces.length} run(s)`);
  }
}
