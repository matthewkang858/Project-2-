// Content script: answers whatever survey page it lands on, then advances.
//
// One instance per page load. It asks the background worker whether this tab is
// part of an active run; if so it takes the answers the run's plan calls for,
// reports the page back, and clicks the forward button. A full-page navigation
// kills this instance and the next page's instance picks up where it left off,
// which is what makes the whole thing survive multi-page surveys.

(() => {
  const send = (msg) =>
    new Promise((resolve) => {
      try {
        chrome.runtime.sendMessage(msg, (reply) => {
          void chrome.runtime.lastError;
          resolve(reply);
        });
      } catch {
        resolve(null);
      }
    });

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  async function waitForChange(before, sel, timeout) {
    const deadline = Date.now() + timeout;
    while (Date.now() < deadline) {
      await sleep(250);
      try {
        const m = SPB_CORE.readPage(sel);
        if (m.fingerprint + '|' + location.href !== before) return true;
      } catch {
        return true; // context tearing down = navigation happened
      }
    }
    return false;
  }

  async function drive(session) {
    const cfg = session.config || {};
    const sel = cfg.selectors || SPB_CORE.DEFAULT_SELECTORS;
    const delay = Number(cfg.delay ?? 400);
    const timeout = Number(cfg.stepTimeout ?? 20000);
    let di = Number(session.di ?? 0);
    const plan = session.plan || [];
    const answered = new Set(); // keys this run has already dealt with

    for (;;) {
      let model = SPB_CORE.readPage(sel);
      const full = Number(cfg.settleTimeout ?? 4000);
      const settleUntil = Date.now() + (model.stuck ? full : Math.min(full, 2000));
      while (!model.questions.length && Date.now() < settleUntil) {
        await sleep(250);
        model = SPB_CORE.readPage(sel);
      }
      const record = {
        url: model.url,
        fingerprint: model.fingerprint,
        heading: model.heading,
        outcome: model.outcome,
        questionKeys: model.questions.map((q) => q.key),
        questions: model.questions.map((q) => ({
          key: q.key,
          kind: q.kind,
          label: q.label,
          options: q.options.map((o) => ({ value: o.value, label: o.label })),
        })),
        decisions: [],
      };

      if (model.isTerminal) {
        await send({ type: 'terminal', record, text: model.bodyText.slice(0, 600) });
        return;
      }

      const target = SPB_CORE.docFor(model, document);
      for (const q of model.questions) {
        // A carousel keeps answered cards on screen — re-answering them would
        // consume plan slots and skew the branch numbering.
        if (answered.has(q.key) && q.answered) continue;
        const cands = SPB_CORE.candidates(q, cfg);
        const wanted = plan[di];
        const idx = Number.isInteger(wanted) && wanted < cands.length ? wanted : 0;
        const chosen = cands[idx];
        const ok = SPB_CORE.applyAnswer(q, chosen, target);
        answered.add(q.key);
        record.decisions.push({
          di,
          key: q.key,
          kind: q.kind,
          label: q.label,
          candidateCount: cands.length,
          chosenIndex: idx,
          chosen: SPB_CORE.describe(q, chosen),
          error: ok ? undefined : 'could not set answer',
        });
        di++;
      }

      const ack = await send({ type: 'step', record, di });
      if (!ack || !ack.continue) return;

      await sleep(delay);

      // Answering can move the survey on by itself (a carousel revealing its
      // next card); re-read before clicking so a card is not skipped.
      let current = model;
      if (model.questions.length) {
        const after = SPB_CORE.readPage(sel);
        if (after.fingerprint !== model.fingerprint) continue;
        current = after;
      }

      const before = current.fingerprint + '|' + location.href;
      if (!current.next || !SPB_CORE.clickNext(current, SPB_CORE.docFor(current, document))) {
        await send({ type: 'stalled', record, text: 'no forward button could be clicked' });
        return;
      }
      // If the page navigates, this instance dies here and the next one resumes.
      const moved = await waitForChange(before, sel, timeout);
      if (!moved) {
        const now = SPB_CORE.readPage(sel);
        const msg = (now.bodyText.match(/[^.]*(required|please|must|error|invalid)[^.]*\./i) || [''])[0];
        await send({ type: 'stalled', record, text: msg || 'page did not advance after submitting' });
        return;
      }
    }
  }

  send({ type: 'page', url: location.href }).then((reply) => {
    if (reply && reply.act) drive(reply.session);
  });
})();
