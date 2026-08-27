#!/usr/bin/env node
// Compares what the bot actually saw in the live survey against the
// questionnaire outline.
//
//   node compare.mjs --spec outline/outline-spec.json --traces out/runs
//   node compare.mjs --spec outline/outline-spec.json --traces spb-traces.json
//
// Writes COMPARE.md next to the traces: which outline questions never appeared,
// which live questions are not in the outline, option-list mismatches, and any
// routing rule the traces contradict.

import { readdirSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';

const args = {};
for (let i = 2; i < process.argv.length; i++) {
  const a = process.argv[i];
  if (!a.startsWith('--')) continue;
  const next = process.argv[i + 1];
  if (next && !next.startsWith('--')) { args[a.slice(2)] = next; i++; } else args[a.slice(2)] = true;
}
if (!args.spec || !args.traces) {
  console.error('usage: node compare.mjs --spec outline/outline-spec.json --traces <out/runs | traces.json>');
  process.exit(1);
}

const spec = JSON.parse(readFileSync(args.spec, 'utf8'));
const traces = loadTraces(args.traces);

function loadTraces(path) {
  if (statSync(path).isDirectory()) {
    return readdirSync(path).filter((f) => f.endsWith('.json')).sort()
      .map((f) => JSON.parse(readFileSync(join(path, f), 'utf8')));
  }
  const parsed = JSON.parse(readFileSync(path, 'utf8'));
  return Array.isArray(parsed) ? parsed : parsed.traces ?? [];
}

// ---- text matching -------------------------------------------------------
const norm = (s) => String(s ?? '').toLowerCase().replace(/\s+/g, ' ').replace(/[^\w %$.-]/g, '').trim();
const tokens = (s) => new Set(norm(s).split(' ').filter((w) => w.length > 3));

function dice(a, b) {
  const A = tokens(a), B = tokens(b);
  if (!A.size || !B.size) return 0;
  let hit = 0;
  for (const t of A) if (B.has(t)) hit++;
  return (2 * hit) / (A.size + B.size);
}

// Every distinct live question the bot saw, keyed by its form name.
const live = new Map();
for (const t of traces) {
  for (const s of t.steps ?? []) {
    for (const q of s.questions ?? []) {
      if (!live.has(q.key)) live.set(q.key, { ...q, seenIn: new Set() });
      live.get(q.key).seenIn.add(t.runId);
    }
  }
}

// Match outline questions to live questions one-to-one: score every pair, then
// take the best pairs first. Without the one-to-one constraint several outline
// questions latch onto the same live question and every comparison downstream
// is nonsense.
const matches = new Map(); // outline q -> { key, score }
const usedKeys = new Set();
const pairs = [];
for (const oq of spec.questions) {
  for (const [key, lq] of live) {
    const score = dice(oq.text, lq.label);
    if (score >= 0.6) pairs.push({ q: oq.q, key, score, label: lq.label });
  }
}
pairs.sort((a, b) => b.score - a.score);
for (const p of pairs) {
  if (matches.has(p.q) || usedKeys.has(p.key)) continue;
  matches.set(p.q, p);
  usedKeys.add(p.key);
}

// ---- checks --------------------------------------------------------------
const findings = [];
const add = (severity, area, text) => findings.push({ severity, area, text });

const notSeen = spec.questions.filter((q) => !matches.has(q.q));
const unknown = [...live.keys()].filter((k) => !usedKeys.has(k));

// Programmer syntax that must never reach a respondent's screen.
const LEAK = /\[(SP|MP|Display if|Show if|Ask if|Randomize|Anchor|Exclusive|INSERT ANSWER|Terminate|Rows|Columns|Write in|Pipe)/i;
for (const [key, q] of live) {
  const texts = [q.label, ...(q.options ?? []).map((o) => o.label)];
  for (const t of texts) {
    const m = String(t ?? '').match(LEAK);
    if (m) add('error', 'syntax', `\`${key}\`: programmer instruction is visible to respondents — "${String(t).slice(0, 90)}"`);
  }
}
const pipeLeft = /\[INSERT ANSWER|\{\{|\$\{|\bPIPE\b|__[A-Z]+__/;
for (const [key, q] of live)
  if (pipeLeft.test(q.label ?? '')) add('error', 'syntax', `\`${key}\`: a piped answer was not substituted — "${(q.label ?? '').slice(0, 90)}"`);

// Word-level difference between two strings, for reporting wording drift.
const words = (s) => norm(s).split(' ').filter(Boolean);
function wordDiff(a, b) {
  const A = words(a), B = new Set(words(b));
  const Bw = words(b), As = new Set(words(a));
  return {
    missing: A.filter((w) => !B.has(w)),
    extra: Bw.filter((w) => !As.has(w)),
  };
}

const phraseIn = (phrase, list) => (list ?? []).some((x) => dice(phrase, x) > 0.6 || norm(x).includes(norm(phrase)));

// Per-question comparison. `perQuestion` drives the report; findings drive the
// summary.
const perQuestion = [];
for (const [oq, m] of matches) {
  const outline = spec.questions.find((q) => q.q === oq);
  const lq = live.get(m.key);
  const issues = [];

  // 1. wording
  const wd = wordDiff(outline.text, lq.label ?? '');
  if (wd.missing.length || wd.extra.length)
    issues.push({
      severity: wd.missing.length > 2 || wd.extra.length > 2 ? 'error' : 'warn',
      area: 'wording',
      text: `wording differs — outline has ${wd.missing.length ? `"${wd.missing.join(' ')}"` : 'nothing extra'}, live has ${wd.extra.length ? `"${wd.extra.join(' ')}"` : 'nothing extra'}`,
    });

  // 2. type
  if (outline.type === 'SP' && lq.kind === 'checkbox')
    issues.push({ severity: 'error', area: 'type', text: 'outline says [SP] but the live question is multi-punch (checkboxes)' });
  if (outline.type === 'MP' && lq.kind === 'radio')
    issues.push({ severity: 'error', area: 'type', text: 'outline says [MP] but the live question is single-punch (radios)' });

  // 3. options / grid columns, in order
  const oOpts = (outline.options.length ? outline.options : outline.columns ?? []);
  const lOpts = lq.options ?? [];
  const rowTable = [];
  if (oOpts.length && lOpts.length) {
    const usedLive = new Set();
    oOpts.forEach((o, i) => {
      let best = null;
      lOpts.forEach((l, j) => {
        const score = dice(o.text, l.label);
        if (!best || score > best.score) best = { j, score, label: l.label };
      });
      if (!best || best.score < 0.6) {
        rowTable.push({ letter: o.letter, outline: o.text, live: '—', note: 'missing live' });
        issues.push({ severity: 'error', area: 'options', text: `option ${o.letter} "${o.text.slice(0, 60)}" is not in the live survey` });
        return;
      }
      usedLive.add(best.j);
      const note = best.j !== i ? `order: live position ${best.j + 1}` : best.score < 0.95 ? 'text differs' : '';
      rowTable.push({ letter: o.letter, outline: o.text, live: best.label, note });
      if (best.j !== i && !outline.tags.some((t) => /randomi/i.test(t)))
        issues.push({ severity: 'warn', area: 'options', text: `option ${o.letter} appears at position ${best.j + 1} live but ${i + 1} in the outline (question is not tagged [Randomize])` });
      if (best.score < 0.95 && best.score >= 0.6)
        issues.push({ severity: 'warn', area: 'options', text: `option ${o.letter} wording differs — outline "${o.text.slice(0, 50)}" vs live "${best.label.slice(0, 50)}"` });
      // 4. emphasis, per option
      for (const kind of ['bold', 'underline']) {
        for (const phrase of o.emphasis?.[kind] ?? []) {
          if (!phraseIn(phrase, lOpts[best.j].emphasis?.[kind]))
            issues.push({ severity: 'warn', area: 'emphasis', text: `option ${o.letter}: "${phrase.slice(0, 40)}" is ${kind} in the outline but not live` });
        }
      }
    });
    lOpts.forEach((l, j) => {
      if (usedLive.has(j)) return;
      rowTable.push({ letter: '—', outline: '—', live: l.label, note: 'extra live' });
      issues.push({ severity: 'warn', area: 'options', text: `live option "${l.label.slice(0, 60)}" is not in the outline` });
    });
    if (oOpts.length !== lOpts.length)
      issues.push({ severity: 'error', area: 'options', text: `${lOpts.length} options live, ${oOpts.length} in the outline` });
  }

  // 5. emphasis on the stem
  for (const kind of ['bold', 'underline']) {
    for (const phrase of outline.emphasis?.[kind] ?? []) {
      if (!phraseIn(phrase, lq.emphasis?.[kind]))
        issues.push({ severity: 'warn', area: 'emphasis', text: `"${phrase.slice(0, 45)}" is ${kind} in the outline but not live` });
    }
  }

  // 6. grid shape
  if (outline.rows?.length) {
    const liveRows = [...live.values()].filter((x) => dice(outline.text, x.label) > 0.35);
    if (liveRows.length && liveRows.length !== outline.rows.length)
      issues.push({ severity: 'error', area: 'structure', text: `grid has ${outline.rows.length} rows in the outline but ${liveRows.length} live` });
  }

  for (const i of issues) add(i.severity, i.area, `${oq} (\`${m.key}\`): ${i.text}`);
  perQuestion.push({ q: oq, key: m.key, outline, live: lq, issues, rowTable });
}

// Routing: a gated question must never appear in a run whose answer to the
// gate question was outside the allowed letters.
const letterSpan = (letters) => {
  const out = [];
  for (const part of String(letters).split(/\s*,\s*/)) {
    const ends = part.match(/[a-z]/g) ?? [];
    if (ends.length > 1) {
      const A = 'abcdefghijklmnopqrstuvwxyz';
      out.push(...A.slice(A.indexOf(ends[0]), A.indexOf(ends[ends.length - 1]) + 1));
    } else out.push(...ends);
  }
  return out;
};

for (const rule of spec.rules.filter((r) => r.type === 'display' && r.dependsOn && r.letters)) {
  const gated = matches.get(rule.q);
  const gate = matches.get(rule.dependsOn);
  if (!gated || !gate) continue;
  const allowed = letterSpan(rule.letters);
  const gateQ = spec.questions.find((q) => q.q === rule.dependsOn);
  const allowedText = allowed.map((l) => gateQ.options.find((o) => o.letter === l)?.text).filter(Boolean);

  for (const t of traces) {
    const sawGated = (t.steps ?? []).some((s) => (s.questionKeys ?? []).includes(gated.key));
    if (!sawGated) continue;
    const answers = (t.decisions ?? []).filter((d) => d.key === gate.key).map((d) => d.chosen ?? '');
    if (!answers.length) continue;
    const ok = answers.some((a) => allowedText.some((txt) => dice(a, txt) > 0.6));
    if (!ok)
      add('error', 'routing', `${t.runId}: ${rule.q} (\`${gated.key}\`) was shown, but ${rule.dependsOn} was answered ${answers.map((a) => `"${a}"`).join(', ')} — the outline shows it only for ${rule.letters} (${allowedText.map((x) => `"${x.slice(0, 40)}"`).join(', ')})`);
  }
}

// Terminates: a run answering outside the qualifying letters must end.
for (const rule of spec.rules.filter((r) => r.type === 'terminate')) {
  const m = matches.get(rule.q);
  if (!m) continue;
  const letters = letterSpan((rule.rule.match(/select\s+(.+)$/i) ?? [, ''])[1]);
  const q = spec.questions.find((x) => x.q === rule.q);
  const qualifying = letters.map((l) => q.options.find((o) => o.letter === l)?.text).filter(Boolean);
  for (const t of traces) {
    const answers = (t.decisions ?? []).filter((d) => d.key === m.key).map((d) => d.chosen ?? '');
    if (!answers.length) continue;
    const qualified = answers.some((a) => qualifying.some((txt) => dice(a, txt) > 0.6));
    const ended = ['terminate', 'quota'].includes(t.outcome?.type);
    if (!qualified && !ended)
      add('error', 'routing', `${t.runId}: answered ${rule.q} as ${answers.map((a) => `"${a}"`).join(', ')} — outside the qualifying options (${rule.rule}) — but the run continued to ${t.outcome?.type}`);
  }
}

for (const f of spec.documentFindings ?? [])
  add(f.severity === 'error' ? 'error' : 'warn', 'outline', `${f.q}: ${f.issue}${f.detail ? ` — _${f.detail}_` : ''}`);

// ---- report --------------------------------------------------------------
const L = [];
L.push('# Survey vs. outline comparison', '');
L.push(`Outline: \`${spec.source}\` — ${spec.questionCount} questions`);
L.push(`Traces: ${traces.length} traversal(s), ${live.size} distinct question(s) seen live`);
L.push('');

if (!live.size) {
  L.push('> **No questions were captured in these traces.** The bot never reached the questionnaire, so nothing below can be checked. Fix the capture first (log in to the survey host in the same browser, confirm the first question renders, then re-run).', '');
}

L.push('## Summary', '');
L.push('| Check | Result |', '|---|---|');
L.push(`| Outline questions seen live | ${matches.size} / ${spec.questionCount} |`);
L.push(`| Outline questions never reached | ${notSeen.length} |`);
L.push(`| Live questions not in the outline | ${unknown.length} |`);
L.push(`| Mismatches found | ${findings.filter((f) => f.severity === 'error').length} error(s), ${findings.filter((f) => f.severity === 'warn').length} warning(s) |`);
L.push('');

const bySeverity = (s) => findings.filter((f) => f.severity === s);
for (const [sev, title] of [['error', 'Mismatches'], ['warn', 'Worth a look']]) {
  const list = bySeverity(sev);
  if (!list.length) continue;
  L.push(`## ${title}`, '');
  for (const f of list) L.push(`- **[${f.area}]** ${f.text}`);
  L.push('');
}

if (notSeen.length) {
  L.push('## Outline questions never reached', '');
  L.push('Each of these is either genuinely unreachable, or simply not covered by the pathways run so far — check the gate column before treating it as a bug.', '');
  L.push('| Q | Gated on | Question |', '|---|---|---|');
  for (const q of notSeen) {
    const gate = spec.rules.find((r) => r.type === 'display' && r.q === q.q);
    L.push(`| ${q.q} | ${gate ? gate.rule.slice(0, 60) : '—'} | ${q.text.slice(0, 90).replace(/\|/g, '\\|')} |`);
  }
  L.push('');
}

if (unknown.length) {
  L.push('## Live questions with no outline match', '');
  L.push('| Name | Type | Question as rendered |', '|---|---|---|');
  for (const k of unknown) {
    const q = live.get(k);
    L.push(`| \`${k}\` | ${q.kind} | ${(q.label ?? '').slice(0, 90).replace(/\|/g, '\\|')} |`);
  }
  L.push('');
}

L.push('## Question by question', '');
for (const p of perQuestion) {
  const bad = p.issues.filter((i) => i.severity === 'error').length;
  const warn = p.issues.filter((i) => i.severity === 'warn').length;
  L.push(`### ${p.q} — \`${p.key}\` — ${bad ? `**${bad} error(s)**` : ''}${bad && warn ? ', ' : ''}${warn ? `${warn} warning(s)` : ''}${!bad && !warn ? 'matches' : ''}`);
  L.push('');
  L.push(`> ${p.outline.text.slice(0, 220)}`);
  L.push('');
  if (p.issues.length) {
    for (const i of p.issues) L.push(`- ${i.severity === 'error' ? '**' : ''}[${i.area}]${i.severity === 'error' ? '**' : ''} ${i.text}`);
    L.push('');
  }
  if (p.rowTable.length && p.issues.some((i) => i.area === 'options')) {
    L.push('| # | Outline | Live | |', '|---|---|---|---|');
    for (const r of p.rowTable)
      L.push(`| ${r.letter} | ${String(r.outline).slice(0, 60).replace(/\|/g, '\\|')} | ${String(r.live).slice(0, 60).replace(/\|/g, '\\|')} | ${r.note} |`);
    L.push('');
  }
}

L.push('## Matched questions', '');
L.push('| Outline | Live name | Match | Question |', '|---|---|---:|---|');
for (const [oq, m] of matches) {
  const outline = spec.questions.find((q) => q.q === oq);
  L.push(`| ${oq} | \`${m.key}\` | ${m.score.toFixed(2)} | ${outline.text.slice(0, 80).replace(/\|/g, '\\|')} |`);
}
L.push('');

const out = join(dirname(args.traces), 'COMPARE.md');
writeFileSync(out, L.join('\n'));

// Structured form of the same findings, for qa/fill_qa.py to turn into the QA
// workbook's per-question columns.
const asJson = {
  survey: traces.find((t) => t.steps?.[0]?.url)?.steps?.[0]?.url ?? null,
  generatedAt: new Date().toISOString(),
  traces: traces.length,
  matched: Object.fromEntries([...matches].map(([q, m]) => [q, { key: m.key, score: Number(m.score.toFixed(2)) }])),
  notSeen: notSeen.map((q) => q.q),
  unknownLive: unknown,
  perQuestion: perQuestion.map((p) => ({
    q: p.q,
    key: p.key,
    liveKind: p.live.kind,
    liveLabel: p.live.label,
    optionCount: (p.live.options ?? []).length,
    limit: p.live.limit ?? null,
    issues: p.issues,
  })),
  findings,
};
writeFileSync(join(dirname(args.traces), 'compare.json'), JSON.stringify(asJson, null, 2));
console.log(`${matches.size}/${spec.questionCount} outline questions seen live · ${findings.filter((f) => f.severity === 'error').length} mismatch(es)`);
console.log(`wrote ${out} and ${join(dirname(args.traces), 'compare.json')}`);
