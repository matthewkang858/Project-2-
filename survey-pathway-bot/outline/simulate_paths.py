#!/usr/bin/env python3
"""Dry-run the coverage paths against the questionnaire before anyone opens
the live survey: does each path's config pin what it means to pin, and does
it reach (and skip) the questions it says it does?

    python3 outline/simulate_paths.py surveys/are01/outline-spec.json \\
        surveys/are01/survey-config.json surveys/are01/paths.json [--report out.md]

Answers are chosen the way the bot chooses them (chrome-extension/core.js):
the first rule whose `match` fits the question label wins; `fixed` picks the
matching option (a multi-select ticks only matching boxes, up to `limit`);
otherwise the first option — or, per grid row, the first column. Gates are
evaluated with outline/gates.py. The live survey can differ where it
randomizes an unpinned question's options; such gates are reported as
"depends on randomization" rather than silently assumed.
"""
import json
import re
import sys

import gates

WORD_NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}


def qnum(q):
    return int(re.sub(r'\D', '', q))


def expand_list(items):
    out = set()
    for it in items:
        m = re.match(r'Q(\d+)(?:-Q?(\d+))?$', it)
        if m:
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            out |= {f'Q{k}' for k in range(a, b + 1)}
    return out


def anchored(o):
    return any(re.match(r'(Anchor|Exclusive)', t, re.I) for t in o['tags'])


def limit_of(q):
    m = re.search(r'select up to (\w+)', q['raw'], re.I)
    if not m:
        return None
    return WORD_NUM.get(m.group(1).lower()) or (int(m.group(1)) if m.group(1).isdigit() else None)


class Walk:
    def __init__(self, spec, answers_cfg, checkbox_limit=1):
        self.spec = spec
        self.Q = {q['q']: q for q in spec['questions']}
        self.rules = answers_cfg
        self.checkbox_limit = checkbox_limit
        self.answers, self.shown, self.log = {}, [], []
        self.rowtext = {}            # q -> [(row key, row text)] as shown
        self.rule_hits = {k: [] for k in range(len(answers_cfg))}
        self.random_defaults = {}   # q -> alternative single picks the live page could make
        self.problems = []

    def pools(self):
        return {k: [o['letter'] for o in (q['options'] or q.get('columns', []))] for k, q in self.Q.items()}

    def gate_ok(self, text):
        g = gates.parse(text)
        if g is None:
            self.problems.append(f'unparsed gate: {text}')
            return True
        return gates.evaluate(g, self.answers, self.pools())

    def rule_for(self, label):
        for k, r in enumerate(self.rules):
            if re.search(r['match'], label, re.I if 'i' in r.get('flags', 'i') else 0):
                return k, r
        return None, None

    def pick(self, q, label, choices, multi):
        """choices: [(letter, text, option)] -> chosen letters, plus whether the
        choice rests on the page's (possibly randomized) first option."""
        k, rule = self.rule_for(label)
        if k is not None:
            self.rule_hits[k].append(label[:70])
        pool = choices
        if rule and rule.get('options'):
            f = [c for c in pool if re.search(rule['options'], c[1], re.I)]
            pool = f or pool
        if rule and rule.get('skip'):
            return [], False
        if rule and rule.get('fixed') is not None:
            hits = [c for c in pool if re.search(rule['fixed'], c[1], re.I)]
            if multi:
                cap = min(rule.get('limit', self.checkbox_limit), limit_of(q) or 99)
                if not hits:
                    self.problems.append(f"{q['q']}: rule /{rule['fixed']}/ matches none of the boxes — every box is left blank ({label[:60]})")
                return [c[0] for c in hits[:cap]], False
            if hits:
                return [hits[0][0]], False
            self.problems.append(f"{q['q']}: rule /{rule['fixed']}/ matches no option, so the bot takes the first one ({label[:60]})")
        # default: first option / first column
        cap = 1
        if multi:
            cap = min(rule.get('limit', self.checkbox_limit) if rule else self.checkbox_limit, limit_of(q) or 99)
        return [c[0] for c in pool[:cap]], True

    def rows_of(self, q):
        """Grid rows as (key, text): fixed rows (with their own gates) or rows
        piped from an earlier answer."""
        out = []
        for r in q.get('rows', []):
            pipe = next((t for t in r['tags'] if t.lower().startswith('populate')), None)
            if pipe:
                m = re.match(r'Populate with rows (?:where )?(.+?) selected in (Q\d+)', pipe, re.I)
                src = self.Q.get(m.group(2)) if m else None
                got = self.answers.get(m.group(2)) if m else None
                if not src or got is None:
                    continue
                if isinstance(got, dict):  # rows of a grid where the range was chosen
                    want = set(gates.expand(m.group(1), [c['letter'] for c in src.get('columns', [])]))
                    # the rows that grid actually showed — itself possibly piped
                    for key, text in self.rowtext.get(src['q'], [(sr['letter'], sr['text']) for sr in src.get('rows', [])]):
                        if got.get(key, set()) & want:
                            out.append((key, text))
                else:
                    want = set(gates.expand(m.group(1), [o['letter'] for o in src['options']]))
                    for o in src['options']:
                        if o['letter'] in got and o['letter'] in want:
                            out.append((o['letter'], o['text']))
                continue
            gate = next((t for t in r['tags'] if t.lower().startswith('if ')), None)
            if gate and not self.gate_ok(gate):
                continue
            out.append((r['letter'], r['text']))
        return out

    def visible_options(self, q):
        out = []
        for o in q['options']:
            gate = next((t for t in o['tags'] if t.lower().startswith('if ')), None)
            if gate and not self.gate_ok(gate):
                continue
            out.append((o['letter'], o['text'], o))
        return out

    def ask(self, q):
        label = f"{q['q']}. {q['text']}"
        multi = q['type'] == 'MP' or bool(re.search(r'all that apply|select up to', q['raw'], re.I))
        randomized = 'Randomize' in q['tags']
        if q.get('columns') and q.get('rows'):
            cols = [(c['letter'], c['text'], c) for c in q['columns']]
            col_random = 'Randomize' in (q.get('gridTags') or [])
            if q['type'] == 'Numeric' or q.get('dropdowns'):
                self.answers[q['q']] = {}
                return
            grid = {}
            self.rowtext[q['q']] = self.rows_of(q)
            for key, text in self.rowtext[q['q']]:
                chosen, default = self.pick(q, f'{label} — {text}', cols, multi)
                grid[key] = set(chosen)
                if default and col_random:
                    self.random_defaults.setdefault(q['q'], True)
            self.answers[q['q']] = grid
            return
        opts = self.visible_options(q)
        if not opts or q['type'] in ('Open', 'Numeric') or 'Dropdown' in q['tags'] and len(opts) <= 2:
            self.answers[q['q']] = set()
            return
        chosen, default = self.pick(q, label, opts, multi)
        self.answers[q['q']] = set(chosen)
        if default and randomized:
            self.random_defaults[q['q']] = [c[0] for c in opts if not anchored(c[2])]

    def run(self):
        checks = {c['afterQ']: c for c in self.spec.get('attentionChecks', [])}
        for q in self.spec['questions']:
            gs = sorted({r['rule'] for r in self.spec['rules'] if r['q'] == q['q'] and r['type'] == 'display'})
            if all(self.gate_ok(g) for g in gs):
                self.shown.append(q['q'])
                self.ask(q)
            if q['q'] in checks:
                c = checks[q['q']]
                chosen, _ = self.pick(c, f"{c['text']}", [(o['letter'], o['text'], o) for o in c['options']], False)
                ok = [o['text'] for o in c['options'] if o['letter'] in chosen] == [c.get('correct')]
                if not ok:
                    self.problems.append(f"{c['q']}: attention check answered {chosen}, passing answer is {c.get('correct')!r} — TERMINATES")
        return self

    def randomization_risks(self):
        """Gates whose outcome hinges on an unpinned randomized question."""
        risks = []
        for q in self.spec['questions']:
            for r in {r['rule'] for r in self.spec['rules'] if r['q'] == q['q'] and r['type'] == 'display'}:
                g = gates.parse(r)
                if not g:
                    continue
                deps = {d for c in g['clauses'] for d in c['qs']} & set(self.random_defaults)
                for d in deps:
                    alts = self.random_defaults[d]
                    if alts is True:
                        risks.append(f"{q['q']} gate '{r}' reads {d}, whose columns are randomized and unpinned")
                        continue
                    base = self.answers.get(d)
                    outcomes = set()
                    for a in alts:
                        self.answers[d] = {a}
                        outcomes.add(gates.evaluate(g, self.answers, self.pools()))
                    self.answers[d] = base
                    if len(outcomes) > 1:
                        risks.append(f"{q['q']} is shown or not depending on which {d} option the page lists first ({d} is randomized and unpinned)")
        return risks


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    spec = json.load(open(args[0]))
    base = json.load(open(args[1]))
    paths = json.load(open(args[2]))
    report = sys.argv[sys.argv.index('--report') + 1] if '--report' in sys.argv else None
    json_out = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    exported = {}
    all_q = [q['q'] for q in spec['questions']]
    gated = {r['q'] for r in spec['rules'] if r['type'] == 'display'}
    L, ok = [], True
    shown_by, hidden_by = {q: [] for q in all_q}, {q: [] for q in all_q}
    for p in paths['paths']:
        rules = p['answers'] + base['answers']
        w = Walk(spec, rules, p.get('checkboxLimit', base.get('checkboxLimit', 1))).run()
        shown = set(w.shown)
        exported[p['id']] = {'shown': w.shown, 'answers': {k: (sorted(v) if isinstance(v, set) else {r: sorted(c) for r, c in v.items()})
                                                         for k, v in w.answers.items()}}
        for q in all_q:
            (shown_by if q in shown else hidden_by)[q].append(p['id'])
        want_s, want_h = expand_list(p.get('expectShown', [])), expand_list(p.get('expectHidden', []))
        miss_s = sorted(want_s - shown, key=qnum)
        miss_h = sorted(want_h & shown, key=qnum)
        unused = [r for k, r in enumerate(p['answers']) if not w.rule_hits[k]]
        L.append(f"## {p['id']} — {p['name']}\n")
        L.append(f"{len(shown)} of {len(all_q)} questions shown.\n")
        if miss_s:
            L.append(f"- **expected but not shown:** {', '.join(miss_s)}")
        if miss_h:
            L.append(f"- **expected hidden but shown:** {', '.join(miss_h)}")
        for u in unused:
            L.append(f"- **pin never applied:** `{u['match']}` ({u.get('_q', '')})")
        for pr in w.problems:
            L.append(f'- problem: {pr}')
        for r in w.randomization_risks():
            L.append(f'- depends on randomization: {r}')
        L.append('')
        L.append('| Pin | Applied to |')
        L.append('|---|---|')
        for k, r in enumerate(p['answers']):
            hits = w.rule_hits[k]
            L.append(f"| {r.get('_q', '')} | {len(hits)}× — {(hits[0] if hits else '—').replace('|', '/')[:80]} |")
        L.append('')
        ok &= not (miss_s or miss_h or unused or any('TERMINATES' in x or 'matches none' in x for x in w.problems))
    L.append('## Coverage across all paths\n')
    never = [q for q in all_q if not shown_by[q]]
    one_sided = [q for q in sorted(gated, key=qnum) if not hidden_by[q] or not shown_by[q]]
    L.append(f"- questions never shown on any path: {', '.join(never) or 'none'}")
    L.append(f"- gated questions not seen both shown and hidden: {', '.join(one_sided) or 'none'}")
    L.append('')
    L.append('| Q | Shown on | Hidden on |')
    L.append('|---|---|---|')
    for q in sorted(gated, key=qnum):
        L.append(f"| {q} | {', '.join(shown_by[q]) or '—'} | {', '.join(hidden_by[q]) or '—'} |")
    text = '\n'.join(L)
    if json_out:
        json.dump(exported, open(json_out, 'w'), indent=1)
    if report:
        open(report, 'w').write('# Path dry-run\n\n' + text + '\n')
    print(text)
    sys.exit(0 if ok and not never else 1)


if __name__ == '__main__':
    main()
