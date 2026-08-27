// One traversal of the survey, start to finish.
//
// The run is driven by a `plan`: an array of choice indices consumed in order,
// one per decision the bot has to make. A short plan is fine — once it runs out
// the bot takes choice 0 at every remaining decision. That property is what the
// explorer in explore.mjs relies on: "replay these choices, then take the first
// option forever" is a deterministic, resumable description of a pathway.

import { readPage, DEFAULT_SELECTORS } from './extract.mjs';
import { candidates, apply, describe, scopeOf } from './answer.mjs';
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function advance(page, model, timeout) {
  const before = model.fingerprint + '|' + model.url;
  await scopeOf(page, model.docPath).locator(model.next.selector).click({ timeout: 5000 }).catch(() => {});
  const deadline = Date.now() + timeout;
  let last = null;
  while (Date.now() < deadline) {
    await sleep(250);
    try {
      last = await readPage(page);
    } catch {
      continue; // mid-navigation
    }
    if (last.fingerprint + '|' + last.url !== before) return { moved: true, model: last };
  }
  return { moved: false, model: last };
}

export async function runOnce(page, opts) {
  const {
    startUrl,
    plan = [],
    config = {},
    runId = 'run',
    outDir = null,
    screenshots = false,
    stepTimeout = 20000,
    maxSteps = 60,
    delay = 0,
    selectors = DEFAULT_SELECTORS,
  } = opts;

  if (outDir && screenshots) mkdirSync(outDir, { recursive: true });

  const trace = { runId, plan: [...plan], startedAt: new Date().toISOString(), steps: [], decisions: [], outcome: null };
  await page.goto(startUrl, { waitUntil: 'domcontentloaded' });

  let di = 0; // decision index — indexes into `plan`
  for (let step = 0; step < maxSteps; step++) {
    let model = await readPage(page, selectors);
    const record = {
      step,
      url: model.url,
      fingerprint: model.fingerprint,
      heading: model.heading,
      questionKeys: model.questions.map((q) => q.key),
      questions: model.questions.map((q) => ({
        key: q.key,
        kind: q.kind,
        label: q.label,
        options: q.options.map((o) => ({ value: o.value, label: o.label })),
      })),
      outcome: model.outcome,
      decisions: [],
    };

    if (screenshots && outDir) {
      const file = join(outDir, `${runId}-s${String(step).padStart(2, '0')}.png`);
      await page.screenshot({ path: file, fullPage: true }).catch(() => {});
      record.screenshot = file;
    }

    if (model.isTerminal) {
      trace.steps.push(record);
      trace.outcome = {
        type: model.outcome ?? (model.questions.length ? 'stuck' : 'end'),
        heading: model.heading,
        text: model.bodyText.slice(0, 600),
        url: model.url,
      };
      break;
    }

    for (const q of model.questions) {
      const cands = candidates(q, config);
      const wanted = plan[di];
      const idx = Number.isInteger(wanted) && wanted < cands.length ? wanted : 0;
      const chosen = cands[idx];
      try {
        await apply(page, q, chosen, model.docPath);
      } catch (err) {
        // Still counts as a decision slot so that replay plans stay aligned.
        const failed = { di, step, key: q.key, kind: q.kind, label: q.label, candidateCount: 1, chosenIndex: 0, chosen: '(failed)', error: String(err.message ?? err) };
        record.decisions.push(failed);
        trace.decisions.push(failed);
        di++;
        continue;
      }
      const dec = {
        di,
        step,
        key: q.key,
        kind: q.kind,
        label: q.label,
        candidateCount: cands.length,
        chosenIndex: idx,
        chosen: describe(q, chosen),
        planned: Number.isInteger(wanted),
      };
      record.decisions.push(dec);
      trace.decisions.push(dec);
      di++;
    }

    if (delay) await sleep(delay);
    const moved = await advance(page, model, stepTimeout);
    trace.steps.push(record);
    if (!moved.moved) {
      // Same page after clicking Next: almost always a validation message. That
      // is a finding, not a crash — record what the page is complaining about.
      const err = moved.model?.bodyText?.match(/[^.]*(required|please|must|error|invalid)[^.]*\./i)?.[0];
      trace.outcome = {
        type: 'stalled',
        heading: moved.model?.heading ?? '',
        text: (err ?? moved.model?.bodyText ?? '').slice(0, 600),
        url: moved.model?.url ?? model.url,
        atFingerprint: model.fingerprint,
      };
      break;
    }
  }

  if (!trace.outcome) trace.outcome = { type: 'maxsteps', text: `stopped after ${maxSteps} pages` };
  trace.finishedAt = new Date().toISOString();
  trace.pathKey = trace.decisions.map((d) => `${d.key}=${d.chosenIndex}`).join('>');
  trace.pageKey = trace.steps.map((s) => s.fingerprint).join('>');
  return trace;
}
