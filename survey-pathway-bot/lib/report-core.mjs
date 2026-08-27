// Loads chrome-extension/report-core.js for the Node side.
import { readFileSync } from 'node:fs';

const SOURCE = readFileSync(new URL('../chrome-extension/report-core.js', import.meta.url), 'utf8');
export const { buildReport } = new Function(`${SOURCE}\nreturn globalThis.SPB_REPORT;`)();
