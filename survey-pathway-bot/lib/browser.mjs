// Browser launch helper. Uses the pre-installed Chromium when one is present
// (Claude Code remote sessions ship it at /opt/pw-browsers/chromium), otherwise
// Playwright's own download.
import { chromium } from 'playwright';
import { existsSync } from 'node:fs';

export async function launch({ headless = true, slowMo = 0, proxy = null } = {}) {
  const opts = { headless, slowMo };
  if (existsSync('/opt/pw-browsers/chromium')) opts.executablePath = '/opt/pw-browsers/chromium';
  const server = proxy ?? process.env.SURVEY_BOT_PROXY ?? null;
  if (server) opts.proxy = { server };
  return chromium.launch(opts);
}

export async function newContext(browser, { viewport = { width: 1400, height: 950 }, userAgent } = {}) {
  return browser.newContext({
    viewport,
    locale: 'en-US',
    userAgent:
      userAgent ??
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  });
}
