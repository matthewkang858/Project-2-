// Page model extraction (Playwright side).
//
// The actual reading of the DOM lives in chrome-extension/core.js so that the
// CLI, the Chrome extension and the console snippet all model a page the same
// way. This module just makes sure that file is present in the page and calls
// into it.

import { CORE_SOURCE, DEFAULT_SELECTORS } from './core.mjs';

export { DEFAULT_SELECTORS };
export { fingerprint } from './fingerprint.mjs';

export async function readPage(page, selectors = DEFAULT_SELECTORS) {
  const present = await page.evaluate(() => typeof globalThis.SPB_CORE !== 'undefined').catch(() => false);
  if (!present) await page.evaluate(CORE_SOURCE);
  return page.evaluate((cfg) => globalThis.SPB_CORE.readPage(cfg), selectors);
}
