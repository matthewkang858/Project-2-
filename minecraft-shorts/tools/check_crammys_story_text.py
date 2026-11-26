"""Checker probe: the NARRATION literal against stories/crammys.json, character by character."""
import json, re, sys, difflib
sys.path.insert(0, '.')
import importlib.util
src = open('films/crammys.py').read()
# extract NARRATION literal without importing bpy
m = re.search(r'^NARRATION = (\{.*?^\})', src, re.S | re.M)
ns = {}
exec('NARRATION = ' + m.group(1), ns)
N = ns['NARRATION']
lines = [l['text'] for l in N['lines']]
joined = ' '.join(lines)
story = json.load(open('stories/crammys.json'))['narration']
print('equal:', joined == story, len(joined), len(story))
if joined != story:
    for i, s in enumerate(difflib.ndiff([story], [joined])):
        print(s)
# sentence split of story
ss = re.findall(r'[^.]+\.', story)
ss = [s.strip() for s in ss]
print(len(ss), len(lines))
for a, b in zip(ss, lines):
    print('OK ' if a == b else 'XX ', repr(a), '|', repr(b))
print('words', len(story.split()), len(joined.split()))
print('ids', [l['id'] for l in N['lines']])
print('pauses', [(l['id'], l.get('pause')) for l in N['lines']])
print({k: v for k, v in N.items() if k != 'lines'})
