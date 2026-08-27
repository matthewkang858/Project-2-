// Report rendering — shared by the CLI (report.mjs) and the Chrome extension's
// "Download report" button, so both produce the same Markdown.
//
// Plain script, no imports: it is loaded as a content/popup script in the
// extension and eval'd by lib/report-core.mjs in Node.

const esc = (s) => String(s ?? '').replace(/\|/g, '\\|').replace(/\n+/g, ' ').trim();
const trunc = (s, n) => (String(s ?? '').length > n ? String(s).slice(0, n - 1) + '…' : String(s ?? ''));
// djb2 — a stable id for a Mermaid node, without Buffer (this file runs in the
// browser too).
const nodeId = (fp) => {
  let h = 5381;
  for (const ch of String(fp)) h = ((h * 33) ^ ch.charCodeAt(0)) >>> 0;
  return 'N' + h.toString(16);
};

function buildReport(traces, summary = {}) {
  const L = [];
  L.push('# Survey pathway test report', '');
  if (summary.url) L.push(`Survey: \`${summary.url}\``);
  L.push(`Generated: ${summary.generatedAt ?? new Date().toISOString()}`);
  L.push(`Traversals: **${traces.length}**` + (summary.plansQueuedButNotRun ? `  ·  untried branches still queued: **${summary.plansQueuedButNotRun}**` : ''));
  L.push('');

  // --- outcomes -----------------------------------------------------------
  const byOutcome = new Map();
  for (const t of traces) {
    const k = t.outcome?.type ?? 'unknown';
    if (!byOutcome.has(k)) byOutcome.set(k, []);
    byOutcome.get(k).push(t);
  }
  L.push('## Outcomes', '');
  L.push('| Outcome | Runs | Example ending text |', '|---|---:|---|');
  for (const [k, list] of [...byOutcome.entries()].sort((a, b) => b[1].length - a[1].length)) {
    L.push(`| ${k} | ${list.length} | ${esc(trunc(list[0].outcome?.heading || list[0].outcome?.text, 90))} |`);
  }
  L.push('');

  // --- runs ---------------------------------------------------------------
  L.push('## Traversals', '');
  L.push('| Run | Pages | Outcome | Decisions taken |', '|---|---:|---|---|');
  for (const t of traces) {
    const path = t.decisions.map((d) => `${d.key}=${esc(trunc(d.chosen, 28))}`).join(' → ');
    L.push(`| ${t.runId} | ${t.steps.length} | ${t.outcome?.type ?? '?'} | ${esc(trunc(path, 240)) || '—'} |`);
  }
  L.push('');

  // --- flow graph ---------------------------------------------------------
  // Nodes are pages (identified by the questions they ask), edges are the
  // answers that moved the bot from one page to the next.
  const nodes = new Map();
  const edges = new Map();
  for (const t of traces) {
    for (let i = 0; i < t.steps.length; i++) {
      const s = t.steps[i];
      if (!nodes.has(s.fingerprint)) {
        const label = s.questionKeys.length
          ? s.questionKeys.join(', ')
          : trunc(s.outcome ? `${s.outcome.toUpperCase()}: ${s.heading}` : s.heading || 'page', 40);
        nodes.set(s.fingerprint, { label, questions: s.questionKeys, outcome: s.outcome, count: 0 });
      }
      nodes.get(s.fingerprint).count++;
      const nxt = t.steps[i + 1];
      if (!nxt) continue;
      const via = (s.decisions ?? [])
        .filter((d) => d.candidateCount > 1)
        .map((d) => `${d.key}=${trunc(d.chosen, 18)}`)
        .join(', ');
      const key = `${s.fingerprint}|${nxt.fingerprint}|${via}`;
      edges.set(key, (edges.get(key) ?? 0) + 1);
    }
  }
  L.push('## Pathway map', '');
  L.push('Nodes are pages (labelled with the questions they ask); edge labels are the answers that led there.', '');
  L.push('```mermaid', 'flowchart TD');
  for (const [fp, n] of nodes) {
    const shape = n.outcome ? ['([', '])'] : ['[', ']'];
    L.push(`  ${nodeId(fp)}${shape[0]}"${n.label.replace(/"/g, "'")}"${shape[1]}`);
  }
  for (const [key, count] of edges) {
    const [from, to, via] = key.split('|');
    const lbl = (via || '(no branching answer)') + (count > 1 ? ` ×${count}` : '');
    L.push(`  ${nodeId(from)} -->|"${lbl.replace(/"/g, "'")}"| ${nodeId(to)}`);
  }
  L.push('```', '');

  // --- coverage -----------------------------------------------------------
  // Every option the bot ever saw, and whether any run actually selected it.
  const qs = new Map(); // key -> {label, kind, options: Map<label, {seen, chosen}>}
  for (const t of traces) {
    for (const s of t.steps) {
      for (const q of s.questions ?? []) {
        // Survey engines name each checkbox of one question separately
        // (Q7r1, Q7r2 …). Reporting them as separate questions buries the
        // report in near-identical rows, so they collapse back into the group.
        const id = q.kind === 'checkbox' && q.group && q.group !== q.key ? q.group : q.key;
        if (!qs.has(id)) qs.set(id, { label: q.label, kind: q.kind, options: new Map(), grouped: id !== q.key });
        const rec = qs.get(id);
        for (const o of q.options ?? []) {
          const k = o.label || o.value;
          if (!rec.options.has(k)) rec.options.set(k, { chosen: 0 });
        }
        // Under a group, each box is one selectable answer; the option label is
        // the box's own text.
        if (rec.grouped)
          for (const o of q.options ?? []) {
            const k = o.label || q.key;
            if (!rec.options.has(k)) rec.options.set(k, { chosen: 0 });
          }
        else if (q.kind === 'checkbox' && (q.options ?? []).length === 1 && !rec.options.has('(left unchecked)'))
          rec.options.set('(left unchecked)', { chosen: 0 });
      }
      for (const d of s.decisions ?? []) {
        const q = (s.questions ?? []).find((x) => x.key === d.key);
        const id = q && q.kind === 'checkbox' && q.group && q.group !== q.key ? q.group : d.key;
        const rec = qs.get(id);
        if (!rec) continue;
        const lbl = String(d.chosen ?? '').replace(/\s*\[[^\]]*\]$/, '');
        for (const [k, v] of rec.options) {
          if (k === lbl || d.chosen?.includes(`[${k}]`)) { v.chosen++; break; }
        }
      }
    }
  }
  L.push('## Answer-option coverage', '');
  L.push('| Question | Type | Options | Exercised | Never selected |', '|---|---|---:|---:|---|');
  const untested = [];
  for (const [key, rec] of qs) {
    const total = rec.options.size;
    const hit = [...rec.options.values()].filter((v) => v.chosen > 0).length;
    const missed = [...rec.options.entries()].filter(([, v]) => v.chosen === 0).map(([k]) => k);
    if (total && missed.length) untested.push({ key, missed });
    L.push(
      `| \`${key}\` — ${esc(trunc(rec.label, 60))} | ${rec.kind} | ${total || '—'} | ${total ? hit : '—'} | ${esc(trunc(missed.join(', '), 80)) || '—'} |`
    );
  }
  L.push('');

  // --- findings -----------------------------------------------------------
  L.push('## Findings to check', '');
  const findings = [];
  for (const t of traces) {
    const manual = (t.steps ?? []).filter((s) => s.manual);
    if (manual.length)
      findings.push(`**${t.runId} needed a hand** on ${manual.length} page(s) — ${manual.map((s) => `\`${s.fingerprint}\`${s.manualReason ? ` (${esc(trunc(s.manualReason, 60))})` : ''}`).join(', ')}. Those widgets (sliders, carousels, custom controls) are worth teaching the bot, or scripting with a \`fixed\` rule.`);
    if (t.outcome?.type === 'looping')
      findings.push(`**${t.runId} looped** on \`${t.outcome.atFingerprint ?? '?'}\` — ${esc(trunc(t.outcome.text, 160))}. Usually a validation the bot is not satisfying; the page's own error message is the place to look.`);
    if (t.outcome?.type === 'stuck')
      findings.push(`**${t.runId} got stuck** on \`${t.outcome.atFingerprint ?? '?'}\` — the page was answered but offered no way forward. ${esc(trunc(t.outcome.text, 160))}`);
    if (t.outcome?.type === 'stopped')
      findings.push(`**${t.runId} was stopped by hand** — the report covers the traversals completed before that.`);
    if (t.outcome?.type === 'stalled')
      findings.push(`**${t.runId} stalled** on page \`${t.outcome.atFingerprint}\` — the page did not advance after submitting. Message: ${esc(trunc(t.outcome.text, 200))}`);
    if (t.outcome?.type === 'error') findings.push(`**${t.runId} errored**: ${esc(trunc(t.outcome.text, 200))}`);
    if (t.outcome?.type === 'maxsteps') findings.push(`**${t.runId} hit the page limit** — possible loop, or a longer survey than \`maxSteps\` allows.`);
    for (const d of t.decisions) if (d.error) findings.push(`**${t.runId}**: could not answer \`${d.key}\` (${esc(d.error)}).`);
  }
  for (const u of untested) findings.push(`\`${u.key}\`: ${u.missed.length} option(s) never selected in any run — ${esc(trunc(u.missed.join(', '), 120))}. Raise \`--max-runs\` or target them with a scripted path.`);
  if (!findings.length) findings.push('None — every traversal reached an end state and every option was exercised.');
  for (const f of findings) L.push(`- ${f}`);
  L.push('');
  return L.join('\n');
}

globalThis.SPB_REPORT = { buildReport };
