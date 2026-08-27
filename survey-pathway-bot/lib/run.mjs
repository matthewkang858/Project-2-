// One traversal of the survey, start to finish.
//
// The run is driven by a `plan`: an array of choice indices consumed in order,
// one per decision the bot has to make. A short plan is fine — once it runs out
// the bot takes choice 0 at every remaining decision. That property is what the
// explorer in explore.mjs relies on: "replay these choices, then take the first
// option forever" is a deterministic, resumable description of a pathway.

import { readPage, DEFAULT_SELECTORS } from './extract.mjs';
import { apply, describe, scopeOf } from './answer.mjs';
import { core } from './core.mjs';
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
    maxSteps = 200,
    delay = 0,
    manualTimeout = 0,
    settleTimeout = 4000,
    selectors = DEFAULT_SELECTORS,
  } = opts;

  if (outDir && screenshots) mkdirSync(outDir, { recursive: true });

  const trace = { runId, plan: [...plan], startedAt: new Date().toISOString(), steps: [], decisions: [], outcome: null };
  await page.goto(startUrl, { waitUntil: 'domcontentloaded' });

  let di = 0; // decision index — indexes into `plan`
  const answered = new Set(); // keys this run has already dealt with
  for (let step = 0; step < maxSteps; step++) {
    let model = await readPage(page, selectors);
    // Players that fetch their question body after the page loads look empty
    // for a moment; give them a beat before calling the survey over.
    const settleUntil = Date.now() + (model.stuck ? settleTimeout : Math.min(settleTimeout, 2000));
    while (!model.questions.length && Date.now() < settleUntil) {
      await sleep(250);
      model = await readPage(page, selectors).catch(() => model);
    }
    const record = {
      step,
      url: model.url,
      fingerprint: model.fingerprint,
      heading: model.heading,
      questionKeys: model.questions.map((q) => q.key),
      questions: model.questions.map((q) => ({
        key: q.key,
        group: q.group,
        kind: q.kind,
        label: q.label,
        limit: q.limit ?? undefined,
        sumTo: q.sumTo ?? undefined,
        emphasis: q.emphasis,
        options: q.options.map((o) => ({ value: o.value, label: o.label, emphasis: o.emphasis })),
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

    // One plan for the whole page, so "select up to two" and "must total 100"
    // are honoured across the questions that share a group.
    const planned = core.planPage(model, plan, di, config, answered);
    for (const d of planned.decisions) {
      const dec = {
        di: d.di,
        step,
        key: d.q.key,
        kind: d.q.kind,
        label: d.q.label,
        candidateCount: d.candidateCount,
        chosenIndex: d.chosenIndex,
        chosen: describe(d.q, d.candidate),
        note: d.note ?? undefined,
        planned: Number.isInteger(plan[d.di]),
      };
      try {
        await apply(page, d.q, d.candidate, model.docPath);
      } catch (err) {
        // A page that re-renders under us invalidates the selector; re-read and
        // try the same question once more before giving up on it.
        let retried = false;
        try {
          const fresh = await readPage(page, selectors);
          const again = fresh.questions.find((x) => x.key === d.q.key);
          if (again) {
            await apply(page, again, d.candidate, fresh.docPath);
            retried = true;
          }
        } catch {
          /* fall through to recording the failure */
        }
        if (!retried) {
          dec.chosen = '(failed)';
          dec.error = String(err.message ?? err);
        }
      }
      answered.add(d.q.key);
      record.decisions.push(dec);
      trace.decisions.push(dec);
    }
    di = planned.di;

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
      if (after) {
        // Players that repaint their answer list can wipe a selection the
        // moment after it is made. Check each answer took, and redo the ones
        // that did not.
        const lost = planned.decisions.filter((d) => {
          if (!d.candidate || d.candidate.kind === 'noop') return false;
          const fresh = after.questions.find((x) => x.key === d.q.key);
          return fresh && fresh.answered === false;
        });
        for (const d of lost) {
          const fresh = after.questions.find((x) => x.key === d.q.key);
          await apply(page, fresh, d.candidate, after.docPath).catch(() => {});
          const dec = record.decisions.find((x) => x.key === d.q.key);
          if (dec) dec.reapplied = true;
        }
        current = lost.length ? (await readPage(page, selectors).catch(() => after)) : after;
      }
    }

    if (current.pager && !current.pager.atEnd) {
      const before = current.fingerprint + '|' + current.url;
      await scopeOf(page, current.docPath)
        .locator(current.pager.selector)
        .click({ timeout: 5000 })
        .catch(() => {});
      const deadline = Date.now() + stepTimeout;
      let advanced = false;
      while (Date.now() < deadline) {
        await sleep(200);
        const now = await readPage(page, selectors).catch(() => null);
        if (now && now.fingerprint + '|' + now.url !== before) { advanced = true; break; }
      }
      if (advanced) {
        record.pager = `${current.pager.index}/${current.pager.total}`;
        trace.steps.push(record);
        continue;
      }
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
