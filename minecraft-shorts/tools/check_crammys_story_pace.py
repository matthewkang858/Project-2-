"""Checker probe: the spoken narration's pacing (sentences, pauses, words), no render."""
import json, sys
sys.path.insert(0, '.')
from engine import narration
import re
src = open('films/crammys.py').read()
m = re.search(r'^NARRATION = (\{.*?^\})', src, re.S | re.M)
ns = {}; exec('NARRATION = ' + m.group(1), ns)
nar = narration.load('crammys', ns['NARRATION'], fps=24)
print(nar.summary())
print('frames', nar.frames, 'duration', nar.frames / 24.0)
fps = 24.0
prev_end = None
for s in nar.sentences:
    ws = s.words
    st, en = ws[0].start, ws[-1].end
    gap = None
    print("%s cut=%4d  %6.2f-%6.2f (%4.2fs, %d w, %4.2f w/s) gap_before=%s | %s" % (
        s.id, s.cut, st, en, en - st, len(ws), len(ws) / (en - st),
        ('%.2f' % (st - prev_end)) if prev_end is not None else '-', s.text))
    prev_end = en
print('tail after last word: %.2f s' % (nar.frames / fps - prev_end))
d = json.load(open('narration/crammys.json'))
print(json.dumps(d['loudness']))
# gaps inside sentences > 0.25 s
for i, (a, b) in enumerate(zip(nar.words, nar.words[1:])):
    g = b.start - a.end
    if g > 0.25 and a.sentence == b.sentence:
        print('intra-sentence gap %.2f after %r (frame %d)' % (g, a.text, a.frame))
# short words
for w in nar.words:
    if w.frame_end - w.frame < 3:
        print('short word', w.text, w.frame, w.frame_end, '%.3f' % (w.end - w.start))
