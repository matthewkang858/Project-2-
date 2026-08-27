// Loads chrome-extension/core.js — the shared page logic — for the Node side.
//
// The same file is what the extension and the console snippet run, so the bot
// sees a survey page identically whichever way you drive it.

import { readFileSync } from 'node:fs';

export const CORE_SOURCE = readFileSync(new URL('../chrome-extension/core.js', import.meta.url), 'utf8');

// Instantiated once here so Node can call the pure helpers (candidates,
// describe) directly; the DOM-touching half only ever runs inside the page.
export const core = new Function(`${CORE_SOURCE}\nreturn globalThis.SPB_CORE;`)();
export const DEFAULT_SELECTORS = core.DEFAULT_SELECTORS;
