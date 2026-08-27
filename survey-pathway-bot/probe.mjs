import { chromium } from 'playwright';
import { readPage } from './lib/extract.mjs';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', headless: true });
const p = await (await b.newContext()).newPage();
await p.goto('http://127.0.0.1:8110/styled');
await p.waitForTimeout(1200);
const m = await readPage(p);
console.log('questions:', JSON.stringify(m.questions.map(q => ({ key: q.key, kind: q.kind, opts: q.options.map(o => o.label) }))));
