// Choosing an answer for a question, and applying it through Playwright.
//
// The candidate list (what makes pathway exploration finite: a radio with 5
// options is 5 branches, a text box is 1) comes from the shared core in
// chrome-extension/core.js, so the CLI and the in-browser tools branch
// identically. Only the "click it" half is Playwright-specific.

import { core } from './core.mjs';

export const candidates = core.candidates;
export const describe = core.describe;

// The survey may live inside an iframe on the host page; readPage records the
// route as `docPath`, and Playwright reaches it through frame locators.
export function scopeOf(page, docPath = []) {
  return docPath.reduce((scope, sel) => scope.frameLocator(sel), page);
}

export async function apply(page, q, candidate, docPath = []) {
  if (candidate.kind === 'noop') return;
  const scope = scopeOf(page, docPath);
  if (candidate.kind === 'value') {
    await scope.locator(q.selector).fill(candidate.value);
    return;
  }
  const opt = q.options[candidate.index];
  if (!opt) throw new Error(`option ${candidate.index} missing on ${q.key}`);
  if (q.kind === 'buttons') {
    await scope.locator(opt.selector).click({ timeout: 5000 }).catch(async () => {
      await scope.getByText(opt.label, { exact: true }).first().click({ timeout: 5000 });
    });
    return;
  }
  if (q.kind === 'select') {
    await scope.locator(q.selector).selectOption(opt.value);
    return;
  }
  // Radio / checkbox. Some engines overlay a styled span on the real input, so
  // fall back to a DOM click + change event when the normal check is blocked.
  try {
    await scope.locator(opt.selector).check({ timeout: 3000 });
  } catch {
    await scope.locator(opt.selector).evaluate((el) => {
      el.click();
      if (!el.checked) {
        el.checked = true;
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  }
}
