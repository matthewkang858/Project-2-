// Coursera feature-verification screenshot capture
//
// Usage:  node capture_screenshots.mjs [manifest.json] [outputDir]
//   manifest.json defaults to ./screenshot_manifest.json
//   outputDir     defaults to ./screenshots
//
// Requires: npm install playwright   (any recent version)
// If running inside a Claude Code remote session, the pre-installed Chromium at
// /opt/pw-browsers/chromium is used automatically; elsewhere Playwright's own
// browser download is used. Network egress to coursera.org must be permitted.
//
// For each manifest entry the script loads the page, scrolls to the first
// occurrence of `target_text` when one is given (so the proof text is in
// frame), and saves both a viewport shot and a full-page shot.

import { chromium } from 'playwright';
import { readFileSync, mkdirSync, existsSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const manifestPath = process.argv[2] ?? './screenshot_manifest.json';
const outDir = process.argv[3] ?? './screenshots';
mkdirSync(outDir, { recursive: true });

const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));

const launchOpts = { headless: true };
if (existsSync('/opt/pw-browsers/chromium')) {
  launchOpts.executablePath = '/opt/pw-browsers/chromium';
}
if (process.env.HTTPS_PROXY) {
  launchOpts.proxy = { server: process.env.HTTPS_PROXY };
}

const browser = await chromium.launch(launchOpts);
const ctx = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  userAgent:
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  locale: 'en-US',
});

const results = [];
const pageCache = new Map(); // url -> page kept open for entries sharing a URL

for (const entry of manifest) {
  const slug = `row${String(entry.row).padStart(2, '0')}_${entry.feature
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 60)}`;
  const record = { ...entry, slug, ok: false, error: null, files: [] };
  const page = await ctx.newPage();
  try {
    const resp = await page.goto(entry.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    record.http_status = resp?.status() ?? null;
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);

    // Dismiss cookie banner if present (OneTrust is what coursera.org uses)
    await page
      .click('#onetrust-accept-btn-handler', { timeout: 3000 })
      .catch(() => {});

    let found = false;
    if (entry.target_text) {
      found = await page.evaluate((needle) => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        const lower = needle.toLowerCase();
        while (walker.nextNode()) {
          const node = walker.currentNode;
          if (node.textContent.toLowerCase().includes(lower)) {
            node.parentElement.scrollIntoView({ block: 'center' });
            node.parentElement.style.outline = '4px solid #ff3b30';
            node.parentElement.style.outlineOffset = '2px';
            return true;
          }
        }
        return false;
      }, entry.target_text);
      record.target_text_found = found;
      await page.waitForTimeout(800);
    }

    const viewportFile = resolve(outDir, `${slug}.png`);
    await page.screenshot({ path: viewportFile });
    record.files.push(viewportFile);

    const fullFile = resolve(outDir, `${slug}_full.png`);
    await page.screenshot({ path: fullFile, fullPage: true }).catch(() => {});
    if (existsSync(fullFile)) record.files.push(fullFile);

    record.ok = true;
    console.log(`OK   row ${entry.row}  ${entry.feature}  (target text ${entry.target_text ? (found ? 'FOUND' : 'NOT FOUND — inspect manually') : 'n/a'})`);
  } catch (e) {
    record.error = e.message;
    console.error(`FAIL row ${entry.row}  ${entry.feature}: ${e.message.split('\n')[0]}`);
  } finally {
    await page.close();
  }
  results.push(record);
}

await browser.close();
writeFileSync(resolve(outDir, 'capture_results.json'), JSON.stringify(results, null, 2));
const okCount = results.filter((r) => r.ok).length;
const hitCount = results.filter((r) => r.target_text_found).length;
console.log(`\n${okCount}/${results.length} pages captured; proof text located on ${hitCount} of them.`);
console.log(`Results written to ${resolve(outDir, 'capture_results.json')}`);
