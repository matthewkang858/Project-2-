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

// Pause for a person to deal with a widget the bot cannot drive (a drag-only
// slider, a map, a captcha) and carry on once the page moves.
async function waitForHuman(page, model, timeout, selectors, why) {
  const before = model.fingerprint + '|' + model.url;
  console.log(
    `\n  ⏸  waiting up to ${Math.round(timeout / 1000)}s for you: ${why ?? 'this page needs a hand'}\n` +
      `     page: ${model.heading || model.url}  (${model.questions.map((q) => q.key).join(', ') || 'no questions'})\n` +
      '     answer it in the browser and move to the next page — the run continues by itself.'
  );
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    await sleep(500);
    const now = await readPage(page, selectors).catch(() => null);
    if (now && now.fingerprint + '|' + now.url !== before) {
      console.log('  ▶  thanks — carrying on.');
      return now;
    }
  }
  return null;
}

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
    manualTimeout = 0,
    selectors = DEFAULT_SELECTORS,
  } = opts;

  if (outDir && screenshots) mkdirSync(outDir, { recursive: true });

  const trace = { runId, plan: [...plan], startedAt: new Date().toISOString(), steps: [], decisions: [], outcome: null };
  await page.goto(startUrl, { waitUntil: 'domcontentloaded' });

  let di = 0; // decision index — indexes into `plan`
  const answered = new Set(); // keys this run has already dealt with
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
      // A carousel keeps earlier cards on screen; re-answering them would
      // consume plan slots and skew the branch numbering.
      if (answered.has(q.key) && q.answered) continue;
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
      answered.add(q.key);
      di++;
    }

    if (delay) await sleep(delay);

    // Answering can itself move the survey on: a carousel reveals its next
    // card, or a page auto-advances once the last answer lands. Re-read before
    // reaching for the forward button, or the click would skip a card.
    let current = model;
    if (model.questions.length) {
      const after = await readPage(page, selectors).catch(() => null);
      if (after && after.fingerprint !== model.fingerprint) {
        trace.steps.push(record);
        continue;
      }
      if (after) current = after;
    }

    if (!current.next) {
      // No way forward even after answering — hand over to a human if one is
      // watching, otherwise record it.
      const helped = manualTimeout ? await waitForHuman(page, current, manualTimeout, selectors) : null;
      if (helped) {
        record.manual = true;
        record.manualReason = 'no forward button — advanced by hand';
        trace.manualAssists = (trace.manualAssists ?? 0) + 1;
        trace.steps.push(record);
        continue;
      }
      trace.steps.push(record);
      trace.outcome = {
        type: 'stuck',
        heading: current.heading,
        text: 'answered the page but found no way forward',
        url: current.url,
        atFingerprint: current.fingerprint,
      };
      break;
    }

    const moved = await advance(page, current, stepTimeout);
    trace.steps.push(record);
    if (!moved.moved) {
      const err = moved.model?.bodyText?.match(/[^.]*(required|please|must|error|invalid)[^.]*\./i)?.[0];
      const helped = manualTimeout ? await waitForHuman(page, current, manualTimeout, selectors, err) : null;
      if (helped) {
        record.manual = true;
        record.manualReason = err ?? 'page did not advance — advanced by hand';
        trace.manualAssists = (trace.manualAssists ?? 0) + 1;
        continue;
      }
      trace.outcome = {
        type: 'stalled',
        heading: moved.model?.heading ?? '',
        text: (err ?? moved.model?.bodyText ?? '').slice(0, 600),
        url: moved.model?.url ?? current.url,
        atFingerprint: current.fingerprint,
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
