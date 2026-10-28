#!/usr/bin/env python3
"""Parse a PDF questionnaire into outline-spec.json — the same spec
parse_outline.py builds from a Word file, so compare.mjs, gen_config.py and
the QA fillers work unchanged.

    python3 outline/parse_outline_pdf.py questionnaire.pdf surveys/<id>/outline-spec.json

A PDF has no list structure, so it is rebuilt from the page: a line opening
with "12." is a question, "a." / "bb." an answer option, "[Columns]" /
"[Rows]" switch a grid's option blocks. Emphasis comes from the fonts (bold)
and from the thin rules drawn under underlined words; programmer logic is the
blue text and quotas the red, as the document's own key says.

Everything after the questionnaire (an earlier outline with its own 1..N
numbering, parameters, notes) is ignored: the body ends at the first page
title once the questions have started.

Requires PyMuPDF:  python3 -m pip install pymupdf
"""
import json
import re
import sys

import pymupdf

import gates

from parse_outline import (LETTERS, audit, audit_scales, audit_syntax, emphasis,
                           rules, strip_tags, tags, write_report)

ZW = '​'
Q_MARK = re.compile(r'^(\d{1,3})\.' + ZW + r'?\s*')
OPT_MARK = re.compile(r'^([a-z]{1,2}|[ivx]{3,5})\.' + ZW + r'?\s*')  # a. … cc., and nested roman iii. viii.
BULLET = re.compile(r'^[●○■•▪]' + ZW + r'?\s*')
GRID_MARK = re.compile(r'^\[(Columns|Rows|Dropdowns)\]', re.I)
ATTENTION = re.compile(r'^ATTENTION CHECK\s*#?\s*(\d+)', re.I)
OPTION_TAG = re.compile(r'(Exclusive|Anchor|TERMINATE|Numeric write-in|Write-in|Specify|If |Display|Show|.*quota)', re.I)

# fill colours of highlight boxes drawn behind text
HIGHLIGHTS = {
    'heading': (0.851, 0.918, 0.827),   # green: section headings
    'terminate': (0.957, 0.8, 0.8),     # pink: [TERMINATE]
    'orange': (1.0, 0.6, 0.0),          # orange: options flagged for review
}


def nearest_highlight(fill):
    best, dist = None, 1e9
    for name, rgb in HIGHLIGHTS.items():
        d = sum((a - b) ** 2 for a, b in zip(fill, rgb))
        if d < dist:
            best, dist = name, d
    return best if dist < 0.02 else 'other'


def rgb_int(c):
    return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255


def page_lines(page):
    """Visual lines of a page: spans grouped by baseline, left to right, each
    span carrying bold / underline / colour / highlight."""
    rules_, fills = [], []
    for d in page.get_drawings():
        r = d['rect']
        if d.get('type') == 's' and r.height < 1.5 and r.width > 2:
            rules_.append((r, d.get('color') or (0, 0, 0)))
        elif d.get('fill') and d['fill'] != (1.0, 1.0, 1.0) and r.height < 30:
            fills.append((r, d['fill']))

    # underlines: thin rules in the text's colour; the grey dividers between
    # sections are not underlines
    unders = [r for r, c in rules_
              if not (abs(c[0] - c[1]) < 0.05 and abs(c[1] - c[2]) < 0.05 and 0.3 < c[0] < 0.8)]

    def underlined(cx, y1):
        return any(y1 - 4.5 <= r.y0 <= y1 + 1 and r.x0 - 0.5 <= cx <= r.x1 + 0.5 for r in unders)

    def highlight(cx, cy):
        for r, f in fills:
            if r.y0 - 1 <= cy <= r.y1 + 1 and r.x0 <= cx <= r.x1:
                return nearest_highlight(f)
        return None

    # Character-level, because one span ("live sports in person") can be only
    # partly underlined or highlighted; consecutive characters with the same
    # marks are regrouped into spans.
    spans = []
    for b in page.get_text('rawdict')['blocks']:
        for line in b.get('lines', []):
            for s in line['spans']:
                chars = s.get('chars') or []
                if not chars:
                    continue
                color = rgb_int(s['color'])
                bold = bool(s['flags'] & 16) or 'bold' in s['font'].lower()
                ital = bool(s['flags'] & 2) or 'italic' in s['font'].lower()
                y0, y1 = s['bbox'][1], s['bbox'][3]
                cur = None
                for ch in chars:
                    cx0, _, cx1, _ = ch['bbox']
                    cx = (cx0 + cx1) / 2
                    # a space takes the marks of the text around it, so an
                    # underlined phrase is not split at every word gap
                    u = underlined(cx, y1) if ch['c'].strip() else (cur['u'] if cur else False)
                    hl = highlight(cx, (y0 + y1) / 2) if ch['c'].strip() else (cur['hl'] if cur else None)
                    if cur and cur['u'] == u and cur['hl'] == hl:
                        cur['text'] += ch['c']
                        cur['x1'] = cx1
                        continue
                    cur = {'text': ch['c'], 'x0': cx0, 'x1': cx1, 'y0': y0, 'y1': y1,
                           'base': s['origin'][1], 'b': bold, 'i': ital, 'u': u, 'color': color, 'hl': hl}
                    spans.append(cur)
    spans.sort(key=lambda s: (round(s['base']), s['x0']))
    lines = []
    for s in spans:
        if lines and abs(lines[-1]['base'] - s['base']) < 2.5:
            lines[-1]['spans'].append(s)
        else:
            lines.append({'base': s['base'], 'spans': [s]})
    for ln in lines:
        ln['spans'].sort(key=lambda s: s['x0'])
        ln['text'] = ''.join(s['text'] for s in ln['spans'])
        ln['x0'] = ln['spans'][0]['x0']
        ln['y0'] = min(s['y0'] for s in ln['spans'])
        ln['y1'] = max(s['y1'] for s in ln['spans'])
    return [ln for ln in lines if ln['text'].replace(ZW, '').strip()]


def merge_runs(spans):
    out = []
    for s in spans:
        text = s['text'].replace(ZW, '')
        if not text:
            continue
        mark = (s['b'], s['u'], s['i'])
        if out and out[-1]['mark'] == mark:
            out[-1]['text'] += text
        else:
            out.append({'text': text, 'mark': mark})
    for o in out:
        o['text'] = re.sub(r'\s+', ' ', o['text'])
    return [{'text': o['text'], 'b': o['mark'][0], 'u': o['mark'][1], 'i': o['mark'][2]} for o in out]


def heading_text(t):
    """Section headings and page titles: short, upper-case, not a list item."""
    return (len(t) < 70 and not t.startswith('[') and t == t.upper() and re.search(r'[A-Z]{3}', t)
            and not Q_MARK.match(t) and not OPT_MARK.match(t))


def paragraphs(doc):
    """Group visual lines into paragraphs. A paragraph starts at a list marker,
    a grid marker, an attention-check heading, or after a blank line; a page
    break alone does not end one (options wrap across pages). Headings and page
    titles always stand alone — otherwise a heading swallows the line under it,
    or the next page's title is read as the wrap of the last option."""
    paras = []
    prev_heading = False
    for pno, page in enumerate(doc):
        lines = page_lines(page)
        prev = None
        for ln in lines:
            text = ln['text'].replace(ZW, '').strip()
            marker = (Q_MARK.match(ln['text']) or OPT_MARK.match(ln['text']) or BULLET.match(ln['text'])
                      or GRID_MARK.match(text) or ATTENTION.match(text))
            heading = not marker and (heading_text(text) or any(s['hl'] == 'heading' for s in ln['spans']))
            height = ln['y1'] - ln['y0']
            gap = (ln['y0'] - prev['y1']) if prev else 0
            # a line opening with a programmer tag starts its own paragraph: a
            # subsection label above "[Link to Cosm description]" or "[Text]"
            # must not swallow it (wrapped tags are re-attached in parse())
            new = (not paras or marker or heading or prev_heading or text.startswith('[')
                   or (prev is not None and gap > 0.7 * height)
                   # a line that starts left of the paragraph's text column is not its wrap
                   or (paras and ln['x0'] < paras[-1]['indent'] - 8 and not BULLET.match(paras[-1]['lines'][0])))
            prev_heading = heading
            if new:
                paras.append({'page': pno + 1, 'spans': [], 'lines': [], 'x0': ln['x0'],
                              'indent': ln['spans'][-1]['x0'] if marker and len(ln['spans']) > 1 else ln['x0']})
                if marker:
                    # text column = first span after the marker (and its zero-width space)
                    rest = [s for s in ln['spans'] if s['text'].replace(ZW, '').strip()]
                    if len(rest) > 1:
                        paras[-1]['indent'] = rest[1]['x0']
            else:
                # keep a space between wrapped lines
                if paras[-1]['spans'] and not paras[-1]['spans'][-1]['text'].endswith(' '):
                    paras[-1]['spans'].append(dict(ln['spans'][0], text=' ', u=False))
            paras[-1]['spans'].extend(ln['spans'])
            paras[-1]['lines'].append(ln['text'])
            prev = ln
    for p in paras:
        p['text'] = re.sub(r'\s+', ' ', ''.join(s['text'] for s in p['spans']).replace(ZW, '')).strip()
        p['highlights'] = sorted({s['hl'] for s in p['spans'] if s['hl']})
        p['blue'] = [s['text'].strip() for s in p['spans'] if s['color'][2] > 0.8 and s['color'][0] < 0.3]
    return paras


def is_heading(p):
    return bool(heading_text(p['text']))


def is_subheading(p):
    t = p['text']
    return (len(t) < 60 and not re.search(r'[\[?]', t) and not re.search(r'[.:,;]$', t)
            and len(t.split()) <= 7 and t[:1].isupper() and not is_heading(p))


def strip_marker(p, pat):
    """Drop the list marker from a paragraph's text and spans."""
    m = pat.match(p['text'])
    if not m:
        return p['text'], p['spans']
    want = len(m.group(0).rstrip())
    out, eaten = [], 0
    for s in p['spans']:
        t = s['text'].replace(ZW, '')
        if eaten < want:
            take = min(len(t), want - eaten)
            eaten += take
            t = t[take:]
            if not t.strip():
                continue
            s = dict(s, text=t)
        out.append(s)
    return p['text'][m.end():].strip(), out


def entry(text, spans, p):
    runs = merge_runs(spans)
    e = {'text': strip_tags(text), 'tags': tags(text), 'runs': runs, 'emphasis': emphasis(runs)}
    if 'orange' in p['highlights']:
        e['highlight'] = 'orange'
    return e


def question_type(raw):
    ts = tags(raw)
    for t in ts:
        m = re.match(r'(SP|MP)\b', t)
        if m:
            return m.group(1)
    for t in ts:
        if re.match(r'Numeric', t, re.I):
            return 'Numeric'
        if re.match(r'(Write-in|Open)', t, re.I):
            return 'Open'
        if re.match(r'(Rank|Slider|Grid)', t, re.I):
            return t.split()[0]
        if re.match(r'Dropdown', t, re.I):
            return 'SP'  # one choice per dropdown
    return 'unspecified'


def parse(path):
    doc = pymupdf.open(path)
    paras = paragraphs(doc)

    questions, checks, blocks = [], [], []
    section, subsection = None, None
    started = False
    cur = None          # question or attention check receiving options
    mode = None         # None | 'rows' | 'columns'
    pending = []        # bracket-only paragraphs waiting for the next question
    prev_opt = None     # the option the previous paragraph produced, if any
    group = None        # current option-group label ("Weekdays")
    block = None        # open [Text] block

    def next_is_question(i):
        for p in paras[i + 1:]:
            return bool(Q_MARK.match(p['text']))
        return False

    for i, p in enumerate(paras):
        t = p['text']
        if not started:
            # the first section heading after the title, key and contents opens
            # the body; the contents' own "1. Screeners (Q1-11)" lines are skipped
            if is_heading(p) and not re.match(r'(KEY|TABLE OF CONTENTS)\b', t) \
                    and not re.search(r'QUESTIONNAIRE|OUTLINE', t):
                started = True
                section = t
            continue

        if is_heading(p) and re.search(r'(SURVEY OUTLINE|SURVEY PARAMETERS|TIMELINE)', t) and questions:
            break  # the questionnaire is over; what follows is supporting material

        m = ATTENTION.match(t)
        if m:
            cur = {'q': f'AC{m.group(1)}', 'afterQ': questions[-1]['q'] if questions else None,
                   'section': section, 'page': p['page'], 'text': '', 'raw': '',
                   'tags': [], 'runs': [], 'emphasis': {}, 'options': []}
            checks.append(cur)
            mode, block = None, None
            continue

        if is_heading(p):
            section, subsection, block = t, None, None
            continue

        qm = Q_MARK.match(t)
        if qm:
            text, spans = strip_marker(p, Q_MARK)
            raw = ' '.join(pending + [text]).strip()
            runs = merge_runs(spans)
            cur = {'q': f'Q{qm.group(1)}', 'number': int(qm.group(1)), 'section': section,
                   'subsection': subsection, 'page': p['page'], 'text': strip_tags(raw), 'raw': raw,
                   'type': question_type(raw), 'tags': tags(raw), 'runs': runs, 'emphasis': emphasis(runs),
                   'options': []}
            if pending:
                cur['leadTags'] = [x.strip('[]') for x in pending]
            questions.append(cur)
            pending, mode, block, group = [], None, None, None
            continue

        gm = GRID_MARK.match(t)
        if gm and cur:
            mode = gm.group(1).lower()  # columns | rows | dropdowns (a dropdown grid's cell definitions)
            cur['grid'] = True
            cur.setdefault('gridTags', []).extend(tags(t))
            continue

        om = OPT_MARK.match(t)
        if om and cur:
            text, spans = strip_marker(p, OPT_MARK)
            e = entry(text, spans, p)
            e['letter'] = om.group(1)
            if group:
                e['group'] = group
            # nesting is judged on the text column, not the marker: roman
            # numerals are right-aligned, so "viii." starts left of "i."
            e['_x'] = p['indent']
            target = cur.setdefault(mode, []) if mode else cur['options']
            if target and p['indent'] > target[-1]['_x'] + 10:
                # indented under the previous item: one of its own choices
                # (a dropdown cell's values), not a sibling option
                target[-1].setdefault('choices', []).append(e)
            else:
                target.append(e)
            prev_opt = e
            continue

        if BULLET.match(t):
            item = BULLET.sub('', t)
            if block is not None:
                block['text'] += '\n' + item
            elif cur and not cur['options'] and not mode:
                # a bulleted list inside the question text ("It offers: • Early
                # ticket access • …") is shown to respondents — part of the stem
                cur['text'] = (cur['text'] + ' • ' + strip_tags(item)).strip()
                cur['raw'] = (cur['raw'] + ' • ' + item).strip()
                cur['runs'] += [{'text': ' • ', 'b': False, 'u': False, 'i': False}] + merge_runs(p['spans'][1:])
                cur['emphasis'] = emphasis(cur['runs'])
            elif cur:
                cur.setdefault('notes', []).append(t)
            continue

        last_opt, prev_opt = prev_opt, None
        bracket_only = re.fullmatch(r'(\[[^\]]+\]\s*)+', t)
        if bracket_only and re.match(r'\[(TEXT|CAPTCHA)\]', t, re.I):
            block = {'kind': re.match(r'\[(\w+)\]', t).group(1).lower(), 'afterQ': questions[-1]['q'] if questions else None,
                     'section': section, 'page': p['page'], 'text': ''}
            blocks.append(block)
            continue
        if re.match(r'\[(TEXT|CAPTCHA)\]', t, re.I):
            block = {'kind': re.match(r'\[(\w+)\]', t).group(1).lower(), 'afterQ': questions[-1]['q'] if questions else None,
                     'section': section, 'page': p['page'], 'text': strip_tags(t)}
            blocks.append(block)
            continue
        if bracket_only:
            if next_is_question(i):
                pending.append(t)
            elif cur:
                # a programmer tag that wrapped onto its own line: option-level
                # tags go back on the option they wrapped from, the rest
                # (types, "[Allow $0-$10,000]") belong to the question
                if last_opt is not None and all(OPTION_TAG.match(x) for x in tags(t)):
                    last_opt['tags'] += tags(t)
                    last_opt['text'] = last_opt['text'].strip()
                else:
                    cur['raw'] += ' ' + t
                    cur['tags'] += tags(t)
                    if cur.get('type') == 'unspecified':
                        cur['type'] = question_type(cur['raw'])
            continue

        if block is not None:
            block['text'] += ('\n' if block['text'] else '') + t
            continue

        if is_subheading(p) and i + 1 < len(paras) and (
                Q_MARK.match(paras[i + 1]['text']) or paras[i + 1]['text'].startswith('[')):
            subsection = t  # "Visit Patterns & Novelty", "Content Interest" …
            continue

        if cur and len(t.split()) <= 3 and not re.search(r'[\[?.:]', t) and i + 1 < len(paras) \
                and OPT_MARK.match(paras[i + 1]['text']):
            # a label over a run of options ("Weekdays" / "Weekends"): a choice
            # group, not stem text
            group = t
            cur.setdefault('optionGroups', []).append(t)
            continue

        if cur and not cur['options'] and not cur.get('rows') and not cur.get('columns') and not mode:
            # stem continues in a second paragraph (a preamble, then the question)
            cur['text'] = (cur['text'] + ' ' + strip_tags(t)).strip()
            cur['raw'] = (cur['raw'] + ' ' + t).strip()
            cur['tags'] += tags(t)
            cur['runs'] += merge_runs(p['spans'])
            cur['emphasis'] = emphasis(cur['runs'])
            if cur.get('type') == 'unspecified':
                cur['type'] = question_type(cur['raw'])
            continue

        if cur:
            cur.setdefault('notes', []).append(t)

    for q in questions + checks:
        q['tags'] = list(dict.fromkeys(q['tags']))
        for key in ('options', 'rows', 'columns', 'dropdowns'):
            for o in q.get(key, []):
                o.pop('_x', None)
                for c in o.get('choices', []):
                    c.pop('_x', None)
    return questions, checks, blocks


def validate(questions):
    """The printed numbering must run 1..N without gaps or repeats, and every
    lettered list must run a, b, c … — otherwise the page was misread."""
    problems = []
    nums = [q['number'] for q in questions]
    for want, got in zip(range(1, len(nums) + 1), nums):
        if want != got:
            problems.append(f'question numbering breaks at Q{want} (found Q{got})')
            break
    for q in questions:
        for key in ('options', 'rows', 'columns', 'dropdowns'):
            letters = [o['letter'] for o in q.get(key, [])]
            expect = [LETTERS[k] if k < 26 else LETTERS[k - 26] * 2 for k in range(len(letters))]
            if letters != expect:
                problems.append(f"{q['q']} {key} lettered {''.join(letters)[:40]}")
    return problems


def audit_pdf(questions, rules_):
    """Checks this document family needs beyond parse_outline's audits."""
    findings = []
    index = {q['q']: q for q in questions}
    pool = lambda q: [o['letter'] for o in (index[q]['options'] or index[q].get('columns', []))] if q in index else []
    for q in questions:
        stem_gates = [gates.parse(r['rule']) for r in rules_ if r['q'] == q['q'] and r['type'] == 'display']
        # a grid whose rows are piped from Qn but which is shown on a different
        # answer set of that same Qn: it can appear with rows it never asks
        for o in q.get('rows', []) + q.get('options', []):
            for t in o['tags']:
                m = re.match(r'Populate with rows (?:where )?(.+?) selected in (Q\d+)', t, re.I)
                if not m:
                    continue
                piped = set(gates.expand(m.group(1), pool(m.group(2))))
                for g in filter(None, stem_gates):
                    if len(g['clauses']) != 1 or g['clauses'][0]['qs'] != [m.group(2)] or g['clauses'][0]['rows']:
                        continue
                    shown = set(gates.expand(g['clauses'][0]['letters'], pool(m.group(2))))
                    if shown != piped:
                        findings.append({'severity': 'warn', 'q': q['q'],
                                         'issue': f"is shown when {g['clauses'][0]['letters']} is selected in {m.group(2)} but populates its "
                                                  f"rows from {m.group(1)} selected in {m.group(2)} — the gate and the row list disagree",
                                         'detail': t})
        # text glued to a programmer tag ("[Exclusive]i") is a stray keystroke
        for key in ('options', 'rows', 'columns'):
            for o in q.get(key, []):
                for r in o.get('runs', []):
                    m = re.search(r'\]([A-Za-z0-9])', r['text'])
                    if m:
                        findings.append({'severity': 'warn', 'q': q['q'],
                                         'issue': f"{key[:-1]} {o['letter']} has a stray \"{m.group(1)}\" right after a programmer tag "
                                                  f"(\"…{r['text'].strip()[-20:]}\") — it may show up in the answer text",
                                         'detail': o['text'][:60]})
    return findings


def check_rules(questions, checks):
    """Terminates on the attention checks: every wrong answer terminates, so the
    passing answer is the one untagged option."""
    out = []
    for c in checks:
        passing = [o for o in c['options'] if not any(re.match('TERMINATE', t) for t in o['tags'])]
        c['correct'] = passing[0]['text'] if len(passing) == 1 else None
        for o in c['options']:
            if any(re.match('TERMINATE', t) for t in o['tags']):
                out.append({'type': 'terminate', 'q': c['q'], 'option': o['letter'],
                            'rule': f"if {o['letter']} ({o['text'][:40]}) is selected"})
    return out


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'questionnaire.pdf'
    dest = sys.argv[2] if len(sys.argv) > 2 else 'outline-spec.json'
    qs, acs, tbs = parse(src)
    rs = rules(qs)
    rs += check_rules(qs, acs)
    problems = validate(qs)
    findings = audit(qs, rs) + audit_syntax(qs, rs) + audit_scales(qs) + audit_pdf(qs, rs)
    findings += [{'severity': 'error', 'q': '—', 'issue': f'parse: {p}', 'detail': ''} for p in problems]
    spec = {
        'source': src.split('/')[-1],
        'questionCount': len(qs),
        'questions': qs,
        'attentionChecks': acs,
        'textBlocks': tbs,
        'rules': rs,
        'quotaRefs': [],
        'documentFindings': findings,
    }
    with open(dest, 'w') as fh:
        json.dump(spec, fh, indent=2, ensure_ascii=False)
    report_path = dest.replace('.json', '') + '-AUDIT.md'
    write_report({**spec, 'questions': qs}, report_path)
    print(f'{len(qs)} questions, {len(acs)} attention checks, {len(tbs)} text blocks, {len(rs)} rules -> {dest}')
    print(f'question-by-question audit -> {report_path}')
    for p in problems:
        print('  PARSE:', p)
    for f in findings[:40]:
        print(f"  [{f['severity']}] {f['q']}: {f['issue']}")
    if len(findings) > 40:
        print(f'  … {len(findings) - 40} more in the audit')
