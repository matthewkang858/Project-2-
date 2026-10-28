#!/usr/bin/env python3
"""Write paste-ready console blocks for a survey's coverage paths.

    python3 outline/build_run_blocks.py surveys/are01 "ARE01 / COSM consumer survey"

Reads <dir>/survey-config.json (rules every path needs) and <dir>/paths.json
(each path's own pins), and writes <dir>/RUN.md: one block per path, plus the
terminate spot-checks. A path's pins go in front of the shared rules, because
the bot uses the first rule whose `match` fits a question.
"""
import json
import os
import sys


def rule_js(r):
    # keep the `_q` note (it says what the pin is for); the bot ignores it
    return json.dumps(r, ensure_ascii=False)


def block(tag, rules, base, then):
    cfg = {k: v for k, v in base.items() if not k.startswith('_') and k != 'answers'}
    lines = [f'// {tag}', 'spb.explore({ maxRuns: 1, config: {']
    for k, v in cfg.items():
        lines.append(f'  {k}: {json.dumps(v)},')
    lines.append('  answers: [')
    lines += [f'    {rule_js(r)},' for r in rules]
    lines.append('  ]')
    lines.append(f'}} }}).then(() => {{ {then} }});')
    return '\n'.join(lines)


def main(folder, title):
    base = json.load(open(os.path.join(folder, 'survey-config.json')))
    paths = json.load(open(os.path.join(folder, 'paths.json')))
    sid = os.path.basename(folder.rstrip('/')).upper()
    L = [f'# Running the bot through {title}', '']
    L += [
        'Each path is one walk through the survey in its own session (the survey has a CAPTCHA, so it cannot restart itself).',
        'For each path:',
        '',
        '1. Open the survey link in a fresh Chrome window (an incognito window is simplest — a used session resumes where it stopped).',
        '2. Click past the intro and tick the CAPTCHA, so you are on the first question.',
        '3. Open DevTools → Console, paste the whole of `dist/console-snippet.js`, press Enter. It prints its build stamp.',
        "4. Paste the path's block below and press Enter. A small panel shows the walk; leave the tab in front until it finishes.",
        '5. When it ends, two files download: the report (`…-REPORT.md`) and the full traces (`…-traces.json`). Send me both —',
        '   the traces are what wording / formatting QA needs.',
        '',
        'If a page stalls, run `spb.debug()` and send me what it prints, plus the page\'s HTML if you can.',
        '',
        '## Paths',
        '',
        '| Path | Who it plays | Opens | Closes |',
        '|---|---|---|---|',
    ]
    for p in paths['paths']:
        L.append(f"| {p['id']} | {p['name']} | {', '.join(p.get('expectShown', []))} | {', '.join(p.get('expectHidden', [])) or '—'} |")
    L.append('')
    for p in paths['paths']:
        then = f"spb.download('{sid}-{p['id']}-REPORT.md'); spb.saveTraces('{sid}-{p['id']}-traces.json');"
        L.append(f"### {p['id']} — {p['name']}")
        L.append('')
        L.append(p['purpose'])
        L.append('')
        L.append('```js')
        L.append(block(f"{sid} {p['id']}: {p['name']}", p['answers'] + base['answers'], base, then))
        L.append('```')
        L.append('')
    checks = paths.get('terminateChecks', [])
    if checks:
        L += ['## Terminate spot-checks (optional)', '',
              'Each confirms one screen-out fires. Same steps as above; the walk should end on the screen-out page '
              'within the first few pages. These need a fresh session each, so do them only if you want them on record.', '']
        for c in checks:
            then = f"spb.download('{sid}-terminate-{c['q']}-REPORT.md');"
            pin = dict(c['pin'], _q=f"{c['q']} — should terminate")
            L.append(f"**{c['q']} → {c['answer']}**")
            L.append('')
            L.append('```js')
            L.append(block(f"{sid} terminate check: {c['q']} = {c['answer']}", [pin] + base['answers'], base, then))
            L.append('```')
            L.append('')
    out = os.path.join(folder, 'RUN.md')
    open(out, 'w').write('\n'.join(L))
    print(f'{len(paths["paths"])} path block(s), {len(checks)} terminate check(s) -> {out}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.basename(sys.argv[1]))
