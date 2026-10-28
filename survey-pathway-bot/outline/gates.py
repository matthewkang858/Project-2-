"""Display-gate expressions as questionnaires write them, parsed and evaluated.

    [If a-bb selected in Q15]
    [If b-j, l-m, or o-p selected in Q13 OR a-k or m-p selected in Q14]
    [If i selected in Q13 AND h NOT selected in Q15]
    [If a-d selected for 1+ row in Q62]
    [If a-c selected for row a or b in Q71 or Q72]

Upper-case AND / OR join clauses; a lower-case "or" stays inside a clause
(a letter list, a row list, a question list). Option letters run a … z,
aa … cc, so ranges are resolved against the target question's own letters,
never the alphabet.
"""
import re

CLAUSE = re.compile(
    r'^(?P<letters>[a-z]{1,2}(?:\s*[-–]\s*[a-z]{1,2})?(?:\s*(?:,|,?\s*\bor\b)\s*[a-z]{1,2}(?:\s*[-–]\s*[a-z]{1,2})?)*)'
    r'\s+(?:is\s+|are\s+)?(?P<neg>not\s+)?selected'
    r'(?:\s+for\s+(?P<rows>1\+\s*rows?|rows?\s+[a-z]{1,2}(?:\s*(?:,|\bor\b|\band\b)\s*[a-z]{1,2})*))?'
    r'\s+(?:in|for)\s+(?P<qs>Q\d+(?:\s*(?:,|\bor\b)\s*Q\d+)*)\s*$', re.I)


def parse(text):
    """-> {'op': 'AND'|'OR'|None, 'clauses': [...]} or None if not understood."""
    text = re.sub(r'^\s*\[?\s*(?:display\s+|show\s+|ask\s+)?if\s+', '', text.strip(), flags=re.I).rstrip('] ')
    parts = re.split(r'\s+(AND|OR)\s+', text)  # case-sensitive: lower-case "or" is in-clause
    clauses, ops = [], set()
    for k, part in enumerate(parts):
        if k % 2:
            ops.add(parts[k])
            continue
        m = CLAUSE.match(part.strip())
        if not m:
            return None
        rows = m.group('rows')
        clauses.append({
            'letters': m.group('letters'),
            'neg': bool(m.group('neg')),
            'rows': None if not rows else ('any' if rows.lstrip().startswith('1') else
                                           re.findall(r'\b[a-z]{1,2}\b', re.sub(r'\b(or|and)\b', ' ', re.sub(r'^rows?\s+', '', rows, flags=re.I)))),
            'qs': re.findall(r'Q\d+', m.group('qs')),
        })
    if len(ops) > 1:
        return None  # mixed AND/OR without brackets: refuse to guess precedence
    return {'op': ops.pop() if ops else None, 'clauses': clauses}


def expand(spec, pool):
    """'b-j, l-m, or o-p' against the letters a question actually has."""
    out = []
    for part in re.split(r'\s*,\s*(?:or\s+)?|\s+or\s+', spec.replace('–', '-')):
        part = part.strip()
        if not part:
            continue
        ends = [e.strip() for e in part.split('-')]
        if len(ends) == 2 and ends[0] in pool and ends[1] in pool:
            out += pool[pool.index(ends[0]):pool.index(ends[1]) + 1]
        elif len(ends) == 1:
            out.append(ends[0])
        else:
            out += [e for e in ends if e in pool]
    return out


def evaluate(gate, answers, pools):
    """answers[q] = set of letters (flat) or {row: set of letters} (grid);
    pools[q] = the letters the target's options (or columns) carry."""
    results = []
    for c in gate['clauses']:
        hit = False
        for q in c['qs']:
            want = set(expand(c['letters'], pools.get(q, [])))
            got = answers.get(q)
            if got is None:
                continue
            if isinstance(got, dict):
                rows = got if c['rows'] in (None, 'any') else {r: v for r, v in got.items() if r in c['rows']}
                hit = hit or any(v & want for v in rows.values())
            else:
                hit = hit or bool(got & want)
        results.append(not hit if c['neg'] else hit)
    return all(results) if gate['op'] == 'AND' else any(results)
