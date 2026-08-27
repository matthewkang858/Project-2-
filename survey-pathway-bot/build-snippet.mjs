#!/usr/bin/env node
// Bundles the shared core + a console wrapper into dist/console-snippet.js,
// the file you paste into Chrome's DevTools console (or save as a DevTools
// Snippet, which can be re-run on each page with one keystroke).

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';

import { execSync } from 'node:child_process';

let build = 'dev';
try {
  build = execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim() + ' ' + new Date().toISOString().slice(0, 16).replace('T', ' ');
} catch {}

const core = readFileSync(new URL('./chrome-extension/core.js', import.meta.url), 'utf8');
const report = readFileSync(new URL('./chrome-extension/report-core.js', import.meta.url), 'utf8');
const wrapper = readFileSync(new URL('./snippet-wrapper.js', import.meta.url), 'utf8');

mkdirSync(new URL('./dist/', import.meta.url), { recursive: true });
const banner = `// Survey pathway bot — console snippet. Built by build-snippet.mjs; do not edit here.
// Paste into the DevTools console on a survey page, or save as a DevTools Snippet
// (Sources ▸ Snippets ▸ New) and press Ctrl/Cmd+Enter to re-run it on each page.
`;
writeFileSync(
  new URL('./dist/console-snippet.js', import.meta.url),
  `${banner}(() => {\nconst SPB_BUILD = ${JSON.stringify(build)};\n${core}\n${report}\n${wrapper}\n})();\n`
);
console.log('wrote dist/console-snippet.js');
