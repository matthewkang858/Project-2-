// Choosing an answer for a question, and applying it through Playwright.
//
// The candidate list (what makes pathway exploration finite: a radio with 5
// options is 5 branches, a text box is 1) comes from the shared core in
// chrome-extension/core.js, so the CLI and the in-browser tools branch
// identically. Only the "click it" half is Playwright-specific.

import { core } from './core.mjs';

export const candidates = core.candidates;
export const describe = core.describe;

export async function apply(page, q, candidate) {
  if (candidate.kind === 'noop') return;
  if (candidate.kind === 'value') {
    await page.fill(q.selector, candidate.value);
    return;
  }
  const opt = q.options[candidate.index];
  if (!opt) throw new Error(`option ${candidate.index} missing on ${q.key}`);
  if (q.kind === 'select') {
    await page.selectOption(q.selector, opt.value);
    return;
  }
  // Radio / checkbox. Some engines overlay a styled span on the real input, so
  // fall back to a DOM click + change event when the normal check is blocked.
  try {
    await page.check(opt.selector, { timeout: 3000 });
  } catch {
    await page.evaluate((sel) => {
      const el = document.querySelector(sel);
      if (!el) return;
      el.click();
      if (!el.checked) {
        el.checked = true;
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }, opt.selector);
  }
}
