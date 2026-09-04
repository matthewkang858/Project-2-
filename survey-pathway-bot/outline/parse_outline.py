#!/usr/bin/env python3
"""Parse a Word questionnaire into outline-spec.json — the machine-readable
expectation that compare.mjs checks a live survey against.

    python3 outline/parse_outline.py questionnaire.docx outline/outline-spec.json

Question numbering is reconstructed from Word's list structure: questions are
the level-0 items of the questionnaire's own numbering lists, everything else
in between is that question's options. The numbering is validated against the
document's own cross-references ("[Display if a is selected for Q10]") — if
those do not line up, the parse is wrong and the script says so.
"""
import json
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
LETTERS = 'abcdefghijklmnopqrstuvwxyz'
ROMAN = [(10, 'x'), (9, 'ix'), (5, 'v'), (4, 'iv'), (1, 'i')]
CATCH_ALL = re.compile(r"^(none of the above|other|i am not sure|not sure|i do not know|don'?t know|no role)", re.I)


def roman(n):
    out, i = '', n
    for value, sym in ROMAN:
        while i >= value:
            out += sym
            i -= value
    return out
TYPE_TAGS = ('SP', 'MP', 'Open', 'Numeric', 'Grid', 'Rank', 'Slider')


def text_of(el):
    return ''.join(t.text or '' for t in el.iter(W + 't')).strip()


def on(rpr, tag):
    """Is this run property switched on (Word omits w:val when it means true)?"""
    if rpr is None:
        return False
    el = rpr.find(W + tag)
    return el is not None and el.get(W + 'val') not in ('0', 'false', 'none')


def runs_of(el):
    """Text runs with their bold/underline/italic state, merged where adjacent
    runs share formatting. Emphasis carries meaning in this questionnaire —
    underlined phrases are what piped questions insert — so it is part of the
    spec, not decoration."""
    out = []
    for r in el.iter(W + 'r'):
        text = ''.join(t.text or '' for t in r.findall(W + 't'))
        if not text:
            continue
        rpr = r.find(W + 'rPr')
        mark = (on(rpr, 'b'), on(rpr, 'u'), on(rpr, 'i'))
        if out and out[-1]['mark'] == mark:
            out[-1]['text'] += text
        else:
            out.append({'text': text, 'mark': mark})
    return [{'text': o['text'], 'b': o['mark'][0], 'u': o['mark'][1], 'i': o['mark'][2]} for o in out]


def emphasis(runs):
    """The bold and underlined phrases of a paragraph, tags stripped."""
    def phrases(key):
        return [re.sub(r'\s+', ' ', r['text']).strip() for r in runs
                if r[key] and re.sub(r'\s*\[[^\]]*\]', '', r['text']).strip()]
    return {'bold': phrases('b'), 'underline': phrases('u'), 'italic': phrases('i')}


def numbering(el):
    ppr = el.find(W + 'pPr')
    if ppr is None:
        return None
    npr = ppr.find(W + 'numPr')
    if npr is None:
        return None
    lvl = npr.find(W + 'ilvl')
    nid = npr.find(W + 'numId')
    return (lvl.get(W + 'val') if lvl is not None else '0', nid.get(W + 'val') if nid is not None else None)


def tags(s):
    return re.findall(r'\[([^\]]+)\]', s)


def strip_tags(s):
    return re.sub(r'\s*\[[^\]]*\]', '', s).strip()


def question_lists(body):
    """The numIds whose level-0 items are the questionnaire's questions.

    Identified by content rather than hard-coded: a question list is one whose
    level-0 items mostly carry a question-type tag ([SP], [MP], [Grid]…).
    """
    counts = {}
    for el in body.iter(W + 'p'):
        num = numbering(el)
        t = text_of(el)
        if not num or not t or num[0] != '0':
            continue
        typed = any(re.match('|'.join(TYPE_TAGS), tag) for tag in tags(t))
        c = counts.setdefault(num[1], [0, 0])
        c[0] += 1
        c[1] += 1 if typed else 0
    return {nid for nid, (total, typed) in counts.items() if total >= 3 and typed / total > 0.5}


def parse(path):
    z = zipfile.ZipFile(path)
    body = ET.fromstring(z.read('word/document.xml')).find(W + 'body')
    qlists = question_lists(body)

    questions, section, started, table_role = [], None, False, None
    for el in body:
        if el.tag == W + 'tbl':
            if questions:
                grid = []
                for row in el.findall(W + 'tr'):
                    cells = [' '.join(text_of(p) for p in c.findall(W + 'p')).strip() for c in row.findall(W + 'tc')]
                    if any(cells):
                        grid.append(cells)
                questions[-1].setdefault('tables', []).append({'role': table_role, 'cells': grid})
            table_role = None
            continue
        if el.tag != W + 'p':
            continue
        t = text_of(el)
        if not t:
            continue
        if t.upper() == 'SURVEY QUESTIONS':
            started = True
            continue
        num = numbering(el)
        if not started:
            # Not every questionnaire carries a SURVEY QUESTIONS marker — the
            # first level-0 item of a question list starts the survey body,
            # and the section heading seen just before it still counts.
            if t.isupper() and len(t) < 60:
                section = t
            if num and num[0] == '0' and num[1] in qlists:
                started = True
            else:
                continue

        if num and num[0] == '0' and num[1] in qlists:
            questions.append({
                'q': f'Q{len(questions) + 1}',
                'numId': num[1],
                'section': section,
                'text': strip_tags(t),
                'raw': t,
                'type': next((tag.split()[0] for tag in tags(t) if re.match('|'.join(TYPE_TAGS), tag)), 'unspecified'),
                'tags': tags(t),
                'runs': runs_of(el),
                'emphasis': emphasis(runs_of(el)),
                'options': [],
            })
            continue

        if num and questions:
            # Items in the question's own list are its answer options. Items in a
            # *different* list (a "This can include any of the following:" block)
            # are illustrative bullets and must not consume option letters — they
            # would shift every letter the routing rules refer to.
            q = questions[-1]
            entry = {'text': strip_tags(t), 'tags': tags(t), 'numId': num[1], 'ilvl': num[0],
                     'runs': runs_of(el), 'emphasis': emphasis(runs_of(el))}
            # A grid question lists its columns (the scale) and its rows as two
            # blocks introduced by [Columns] / [Rows] markers. They are numbered
            # with roman numerals in this document's own routing rules, so they
            # must not be lettered in with the flat options.
            marker = next((x for x in entry['tags'] if x.lower().startswith(('rows', 'columns'))), None)
            if marker and not entry['text']:
                q['grid'] = True
                q['_mode'] = 'rows' if marker.lower().startswith('rows') else 'columns'
                q.setdefault('gridTags', []).extend(entry['tags'])
                continue
            target = q.get('_mode')
            if num[1] != q['numId'] and not target:
                q.setdefault('aside', []).append(entry)
            elif target:
                q.setdefault(target, []).append(entry)
            else:
                q['options'].append(entry)
            continue

        if re.match(r'^\[(Rows|Columns)\]', t):
            table_role = 'rows' if 'Rows' in t else 'columns'
            if questions:
                questions[-1].setdefault('notes', []).append(t)
        elif t.isupper() and len(t) < 60:
            section = t
        elif questions and t.startswith('['):
            questions[-1].setdefault('notes', []).append(t)

    for q in questions:
        q.pop('_mode', None)
        if not q['options'] and q.get('aside'):
            q['options'] = q.pop('aside')
        for i, o in enumerate(q['options']):
            o['letter'] = LETTERS[i] if i < 26 else f'#{i + 1}'
        for key in ('rows', 'columns'):
            for i, o in enumerate(q.get(key, [])):
                o['letter'] = roman(i + 1)
        for o in q['options'] + q.get('rows', []) + q.get('columns', []) + q.get('aside', []):
            o.pop('numId', None)
            o.pop('ilvl', None)
    return questions


def rules(questions):
    out = []
    for q in questions:
        blob = ' '.join([q['raw']] + q.get('notes', []))
        for m in re.finditer(r'\[Terminate ([^\]]+)\]', blob, re.I):
            out.append({'type': 'terminate', 'q': q['q'], 'rule': m.group(1).strip()})
        for m in re.finditer(r'\[TERMINATE if([^\]]*)\]?', blob):
            out.append({'type': 'terminate', 'q': q['q'], 'rule': ('if' + m.group(1)).strip(' :')})
        # Two gate phrasings exist across questionnaires: "[Display if a is
        # selected for Q10]" and the terser "[If a selected in Q5]" (with
        # AND/OR/NOT compounds). Both make display rules.
        for m in re.finditer(r'\[(?:(?:Display|Show|Ask) if|If) ([^\]]+)\]', blob, re.I):
            rule = m.group(1).strip()
            clauses = re.findall(
                r'([a-z0-9](?:\s*[-–]\s*[a-z0-9])?(?:\s*(?:,|OR)\s*[a-z0-9])*)\s+'
                r'(?:is\s+|are\s+)?((?:NOT\s+)?(?:displayed\s+and\s+)?(?:NOT\s+)?)selected[^Q]*?(Q\d+)',
                rule, re.I)
            if clauses:
                for letters, negation, dep in clauses:
                    # letters of a NOT-selected clause are not qualifying
                    # answers — carry the clause but leave letters unset
                    out.append({'type': 'display', 'q': q['q'], 'rule': rule, 'dependsOn': dep,
                                'letters': None if re.search(r'NOT', negation, re.I) else letters.strip()})
            else:
                dep = re.search(r'(Q\d+)', rule)
                out.append({'type': 'display', 'q': q['q'], 'rule': rule, 'dependsOn': dep.group(1) if dep else None})
        for m in re.finditer(r'select up to (\w+)', q['raw'], re.I):
            out.append({'type': 'limit', 'q': q['q'], 'rule': f'select up to {m.group(1)}'})
        if re.search(r'\[Randomize\]', blob, re.I):
            out.append({'type': 'randomize', 'q': q['q'], 'rule': 'randomize'})
        for part, kind in ((q['options'], 'option'), (q.get('rows', []), 'row'), (q.get('columns', []), 'column')):
            for o in part:
                for tag in o['tags']:
                    if re.match(r'TERMINATE', tag):
                        out.append({'type': 'terminate', 'q': q['q'], 'option': o['letter'],
                                    'rule': f"if {o['letter']} ({o['text'][:40]}) is selected" + (
                                        '' if tag.strip() == 'TERMINATE' else f' — {tag}')})
                        continue
                    if re.match(r'(Show if|Display if|Display all|If |Exclusive|Anchor)', tag, re.I):
                        dep = re.search(r'(Q\d+)', tag)
                        letters = re.search(r'([a-z](?:\s*[-–]\s*[a-z])?)\s+(?:is\s+|are\s+)?(?:NOT\s+)?selected', tag)
                        out.append({'type': kind, 'q': q['q'], kind: o['letter'], 'rule': tag,
                                    'dependsOn': dep.group(1) if dep else None,
                                    'letters': letters.group(1).strip() if letters else None})
    # both terminate phrasings can match the same bracket — keep one of each
    seen, unique = set(), []
    for r in out:
        key = json.dumps(r, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


WORD_NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}


def audit(questions, rules_):
    """Internal consistency of the document itself, before any live survey."""
    index = {q['q']: q for q in questions}
    order = {q['q']: i for i, q in enumerate(questions)}
    findings = []

    for r in rules_:
        if r['type'] not in ('display', 'option', 'row', 'column') or not r.get('dependsOn'):
            continue
        dep = r['dependsOn']
        if dep not in index:
            findings.append({'severity': 'error', 'q': r['q'],
                             'issue': f"references {dep}, which does not exist (survey has {len(questions)} questions)",
                             'detail': r['rule']})
            continue
        if order[dep] >= order[r['q']]:
            findings.append({'severity': 'error', 'q': r['q'],
                             'issue': f"is shown based on {dep}, which is asked later ({dep} is question {order[dep] + 1}, this is question {order[r['q']] + 1})",
                             'detail': r['rule']})
        pool = index[dep]['options'] or index[dep].get('columns', [])
        have = [o['letter'] for o in pool]
        if not have or not r.get('letters'):
            continue
        # Ranges are expressed in whatever the target question uses — letters
        # for a flat list, roman numerals for a grid's columns — so resolve the
        # range against that question's own sequence rather than the alphabet.
        span, unknown = [], []
        for part in re.split(r'\s*,\s*', r['letters']):
            ends = re.findall(r'[a-z]+', part)
            if not ends:
                continue
            if all(e in have for e in ends):
                span += have[have.index(ends[0]):have.index(ends[-1]) + 1] if len(ends) > 1 else [ends[0]]
            else:
                unknown += [e for e in ends if e not in have]
        # "a-z" is this questionnaire's shorthand for "any option"
        if unknown and not (r['letters'].replace(' ', '') == 'a-z' and len(have) >= 20):
            findings.append({'severity': 'error', 'q': r['q'],
                             'issue': f"refers to {dep} option(s) {', '.join(sorted(set(unknown)))}, which {dep} does not have (it has {have[0]}–{have[-1]})",
                             'detail': r['rule']})

    for q in questions:
        limits = [r for r in rules_ if r['type'] == 'limit' and r['q'] == q['q']]
        for lim in limits:
            n = WORD_NUM.get(lim['rule'].split()[-1].lower())
            if n and q['type'] not in ('MP',):
                findings.append({'severity': 'warn', 'q': q['q'],
                                 'issue': f"is tagged [{q['type']}] but says '{lim['rule']}' — a multi-punch limit on a single-punch question",
                                 'detail': q['text'][:100]})
        note_blob = ' '.join(q.get('notes', []) + [o['text'] for o in q['options'][:1]])
        if q['type'] == 'unspecified' and re.search(r'write[- ]in|sliding scale|sum to 100', note_blob, re.I):
            continue
        if q['type'] == 'unspecified' and q['options']:
            findings.append({'severity': 'warn', 'q': q['q'],
                             'issue': 'has answer options but no [SP]/[MP]/[Grid] tag for the programmer',
                             'detail': q['text'][:100]})
        if not q['options'] and not q.get('tables') and not q.get('rows') and not q.get('columns') and q['type'] in ('SP', 'MP'):
            findings.append({'severity': 'warn', 'q': q['q'],
                             'issue': f"is tagged [{q['type']}] but no answer options were found under it",
                             'detail': q['text'][:100]})
    return findings


def audit_quotas(refs, questions):
    """A quota that names a question must name one whose options can express it.

    The quota block says things like "B2B: ... [Captured through responses a & c
    for Q6]" — if Q6's options never mention B2B, the reference points at the
    wrong question.
    """
    findings = []
    index = {q['q']: q for q in questions}
    for ref in refs:
        q = index.get(ref['q'])
        if not q:
            findings.append({'severity': 'error', 'q': ref['q'],
                             'issue': f"quota references {ref['q']}, which does not exist",
                             'detail': ref['text']})
            continue
        label = re.split(r'[:\[]', ref.get('label') or '')[0].strip()
        keyword = label if label else ''
        if not keyword:
            continue
        opts = ' '.join(o['text'] for o in q['options']).lower()
        if keyword.lower() in opts:
            continue
        better = [x['q'] for x in questions
                  if keyword.lower() in ' '.join(o['text'] for o in x['options']).lower()]
        if not better:
            continue  # nothing to compare against — the label is prose, not an option value
        findings.append({'severity': 'error', 'q': ref['q'],
                         'issue': f"quota for \"{keyword}\" points at {ref['q']} ({q['text'][:50]}…), whose options never mention it — {better[0]} does",
                         'detail': ref['text']})
    return findings


def audit_syntax(questions, rules_):
    """Per-question syntax, emphasis and convention checks on the document."""
    index = {q['q']: q for q in questions}
    order = {q['q']: i for i, q in enumerate(questions)}
    findings = []

    def add(q, sev, issue, detail=''):
        findings.append({'severity': sev, 'q': q, 'issue': issue, 'detail': detail})

    # instruction phrasing + its formatting, so drift shows up as the minority style
    instr_style = {}
    for q in questions:
        for m in re.finditer(r'(Please select (?:all that apply|up to \w+))', q['raw'], re.I):
            phrase = m.group(1)
            fmt = 'plain'
            for r in q.get('runs', []):
                if phrase.lower()[:20] in r['text'].lower():
                    fmt = 'bold' if r['b'] else ('underline' if r['u'] else 'plain')
                    break
            instr_style.setdefault((phrase.lower(), fmt), []).append(q['q'])

    for q in questions:
        raw, opts = q['raw'], q['options']
        blob = ' '.join([raw] + q.get('notes', []))

        # 1. multi-punch instruction vs declared type
        says_multi = re.search(r'select (all that apply|up to \w+)', raw, re.I)
        if says_multi and q['type'] == 'SP':
            add(q['q'], 'error', f"is tagged [SP] but instructs \"{says_multi.group(0)}\"")
        if q['type'] == 'MP' and not says_multi:
            add(q['q'], 'warn', 'is tagged [MP] but carries no "select all that apply" / "select up to N" instruction')

        # 2. piped answers
        for m in re.finditer(r'\[INSERT ANSWER FROM (\d+)([^\]]*)\]', blob, re.I):
            src = f"Q{m.group(1)}"
            if src not in index:
                add(q['q'], 'error', f"pipes an answer from {src}, which does not exist")
                continue
            if order[src] >= order[q['q']]:
                add(q['q'], 'error', f"pipes an answer from {src}, which is asked later")
            if 'UNDERLINED' in m.group(2).upper():
                gate_letters = set()
                for r in rules_:
                    if r['type'] == 'display' and r['q'] == q['q'] and r.get('dependsOn') == src and r.get('letters'):
                        ends = re.findall(r'[a-z]', r['letters'])
                        gate_letters |= set(LETTERS[LETTERS.index(ends[0]):LETTERS.index(ends[-1]) + 1]) if len(ends) > 1 else set(ends)
                candidates = [o for o in index[src]['options'] if not gate_letters or o['letter'] in gate_letters]
                missing = [o['letter'] for o in candidates if not o.get('emphasis', {}).get('underline')]
                if missing:
                    add(q['q'], 'error',
                        f"pipes the underlined phrase from {src}, but {src} option(s) {', '.join(missing)} have no underlined text to pipe")
            gate = [r for r in rules_ if r['type'] == 'display' and r['q'] == q['q'] and r.get('dependsOn') == src]
            if not gate:
                add(q['q'], 'warn', f"pipes from {src} but is not gated on {src} — respondents who skipped {src} would see an empty phrase")

        # 3. anchors and exclusives
        for i, o in enumerate(opts):
            tagged = ' '.join(o['tags']).lower()
            catch_all = CATCH_ALL.match(o['text'])
            if catch_all and 'anchor' not in tagged and 'exclusive' not in tagged and q['type'] == 'MP':
                add(q['q'], 'warn', f"option {o['letter']} \"{o['text'][:40]}\" is a catch-all on a multi-punch question but is not tagged [Anchor]/[Exclusive]")
            if ('anchor' in tagged or 'exclusive' in tagged) and i != len(opts) - 1 and not any(
                    'anchor' in ' '.join(x['tags']).lower() or 'exclusive' in ' '.join(x['tags']).lower() for x in opts[i + 1:]):
                add(q['q'], 'warn', f"option {o['letter']} is tagged [{o['tags'][0]}] but is not at the end of the list")

        # 4. duplicate options
        seen = {}
        for o in opts:
            k = re.sub(r'\W+', '', o['text'].lower())[:60]
            if k and k in seen:
                add(q['q'], 'error', f"options {seen[k]} and {o['letter']} are duplicates — \"{o['text'][:50]}\"")
            seen[k] = o['letter']

        # 5. emphasis consistency — catch-all options carry no key phrase to
        #    emphasise, so they are not evidence of drift
        for label, group in (('option', opts), ('row', q.get('rows', [])), ('column', q.get('columns', []))):
            real = [o for o in group if o['text'] and not CATCH_ALL.match(o['text'])]
            if len(real) < 4:
                continue
            for key in ('underline', 'bold'):
                marked = [o for o in real if o.get('emphasis', {}).get(key)]
                if marked and len(marked) / len(real) >= 0.8 and len(marked) != len(real):
                    bare = [o['letter'] for o in real if not o.get('emphasis', {}).get(key)]
                    add(q['q'], 'warn',
                        f"{len(marked)}/{len(real)} {label}s use {key}, but {label}(s) {', '.join(bare)} do not — emphasis is inconsistent within the question")

        # 6. programmer tags that would be visible if pasted verbatim
        if re.search(r'\[(Display|Show|Ask) if', raw) and not raw.startswith('['):
            add(q['q'], 'warn', 'has its [Display if …] instruction inside the question text rather than at the start of the line')
    return findings


def audit_scales(questions):
    """Scale wording that drifts between questions using the same scale."""
    findings, groups = [], {}
    for q in questions:
        if len(q['options']) < 3:
            continue
        key = len(q['options'])
        groups.setdefault(key, []).append(q)
    for size, qs in groups.items():
        for i, a in enumerate(qs):
            for b in qs[i + 1:]:
                at = [re.sub(r'\W+', ' ', o['text'].lower()).strip() for o in a['options']]
                bt = [re.sub(r'\W+', ' ', o['text'].lower()).strip() for o in b['options']]
                same = sum(1 for x, y in zip(at, bt) if x == y)
                if same and same == size - 1:
                    diff = [(a['options'][k]['letter'], a['options'][k]['text'], b['options'][k]['text'])
                            for k in range(size) if at[k] != bt[k]]
                    for letter, x, y in diff:
                        findings.append({'severity': 'warn', 'q': b['q'],
                                         'issue': f"uses the same scale as {a['q']} except option {letter}: \"{y[:45]}\" vs {a['q']}'s \"{x[:45]}\"",
                                         'detail': ''})
    return findings


def quota_refs(path, questions):
    """Cross-references in the Survey Guide's quota section (before SURVEY QUESTIONS)."""
    z = zipfile.ZipFile(path)
    body = ET.fromstring(z.read('word/document.xml')).find(W + 'body')
    out, last_label = [], ''
    for el in body.iter(W + 'p'):
        t = text_of(el)
        if t.upper() == 'SURVEY QUESTIONS':
            break
        if not t.startswith('['):
            last_label = t  # the line the bracketed reference belongs to
        for m in re.finditer(r'responses?\s+([a-z])\s*(?:[-&]|and)\s*([a-z])\s+for\s+(Q\d+)', t, re.I):
            out.append({'text': t, 'label': last_label, 'from': m.group(1), 'to': m.group(2), 'q': m.group(3)})
    return out


def write_report(spec, path):
    """Question-by-question audit of the document."""
    qs, findings = spec['questions'], spec['documentFindings']
    by_q = {}
    for f in findings:
        by_q.setdefault(f['q'], []).append(f)
    rules_by_q = {}
    for r in spec['rules']:
        rules_by_q.setdefault(r['q'], []).append(r)

    L = ['# Questionnaire audit — ' + spec['source'], '']
    L.append(f"{spec['questionCount']} questions · {len(spec['rules'])} programmed rules · "
             f"**{sum(1 for f in findings if f['severity'] == 'error')} error(s), "
             f"{sum(1 for f in findings if f['severity'] == 'warn')} warning(s)**")
    L.append('')
    L.append('This checks the document against itself — numbering, cross-references, option '
             'lettering, emphasis and programmer syntax. Comparing it to the *live* survey is '
             '`compare.mjs`, which needs a captured run.')
    L.append('')
    L.append('## Questions with issues')
    L.append('')
    L.append('| Q | Issue |')
    L.append('|---|---|')
    for q in qs:
        for f in by_q.get(q['q'], []):
            mark = '**error**' if f['severity'] == 'error' else 'warning'
            L.append(f"| {q['q']} | {mark}: {f['issue'].replace('|', chr(92) + '|')} |")
    if not by_q:
        L.append('| — | none |')
    L.append('')

    L.append('## Every question')
    L.append('')
    L.append('| Q | Section | Type | Answers | Shown when | Feeds | Emphasis | Status |')
    L.append('|---|---|---|---|---|---|---|---|')
    feeds = {}
    for r in spec['rules']:
        if r.get('dependsOn'):
            feeds.setdefault(r['dependsOn'], set()).add(r['q'])
    for q in qs:
        rs = rules_by_q.get(q['q'], [])
        gate = next((r['rule'] for r in rs if r['type'] == 'display'), '')
        if q.get('rows') or q.get('columns'):
            answers = f"grid {len(q.get('rows', []))}×{len(q.get('columns', []))}"
        else:
            answers = f"{len(q['options'])} options"
        emph = []
        if q.get('emphasis', {}).get('bold'):
            emph.append('bold stem')
        if q.get('emphasis', {}).get('underline'):
            emph.append('underlined stem')
        pool = q['options'] or q.get('columns', [])
        if pool and sum(1 for o in pool if o.get('emphasis', {}).get('underline')) >= max(2, len(pool) * 0.5):
            emph.append('underlined answers')
        issues = by_q.get(q['q'], [])
        status = 'ok' if not issues else ('**error**' if any(i['severity'] == 'error' for i in issues) else 'warning')
        fed = ', '.join(sorted(feeds.get(q['q'], []), key=lambda x: int(x[1:])))
        L.append(f"| {q['q']} | {(q['section'] or '').title()} | {q['type']} | {answers} | "
                 f"{(gate or 'always')[:48].replace('|', chr(92) + '|')} | {fed[:40]} | {', '.join(emph) or '—'} | {status} |")
    L.append('')
    with open(path, 'w') as fh:
        fh.write('\n'.join(L))


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'questionnaire.docx'
    dest = sys.argv[2] if len(sys.argv) > 2 else 'outline-spec.json'
    qs = parse(src)
    rs = rules(qs)
    qrefs = quota_refs(src, qs)
    spec = {
        'source': src.split('/')[-1],
        'questionCount': len(qs),
        'questions': qs,
        'rules': rs,
        'quotaRefs': qrefs,
        'documentFindings': audit(qs, rs) + audit_quotas(qrefs, qs) + audit_syntax(qs, rs) + audit_scales(qs),
    }
    with open(dest, 'w') as fh:
        json.dump(spec, fh, indent=2)
    report_path = dest.replace('.json', '') + '-AUDIT.md'
    write_report(spec, report_path)
    print(f'{len(qs)} questions, {len(rs)} rules -> {dest}')
    print(f'question-by-question audit -> {report_path}')
    for f in spec['documentFindings']:
        print(f"  [{f['severity']}] {f['q']}: {f['issue']}")
