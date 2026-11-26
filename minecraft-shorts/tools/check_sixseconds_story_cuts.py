"""Checker probe: each cut against the word frames, and the captions the encoder shows (pure python)."""
import sys, os, ast
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import narration
nar = narration.load("sixseconds")
src = open(os.path.join(ROOT, "films/sixseconds.py")).read()
tree = ast.parse(src)
g = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) in ("SHOTS", "RESETS", "SNAPS", "END_BLACK"):
        g[node.targets[0].id] = ast.literal_eval(node.value)
def start(st):
    if isinstance(st, str):
        s = nar.sentence(st); return s.cut
    sid, what = st
    s = nar.sentence(sid)
    if isinstance(what, str):
        return nar.cut_before(nar.word(what, sentence=s))
    return s.cut + int(what)
cuts = [start(r[4]) for r in g["SHOTS"]]
ends = [c - 1 for c in cuts[1:]] + [nar.frames]
print("film frames", nar.frames)
for (name, beat, seq, sky, st), a, b in zip(g["SHOTS"], cuts, ends):
    # word in progress at the cut?
    inside = [w for w in nar.words if w.frame < a <= w.frame_end]
    prev = [w for w in nar.words if w.frame_end < a]
    nxt = [w for w in nar.words if w.frame >= a]
    pw = prev[-1] if prev else None
    nw = nxt[0] if nxt else None
    gap_before = (a - 1 - pw.frame_end) if pw else None
    lead = (nw.frame - a) if nw else None
    print("%-14s %4d-%4d %3d f %.2f s | prev %-8s ends %4s (%s fr silent before cut) | next %-8s at %4s (+%s) %s"
          % (name, a, b, b - a + 1, (b - a + 1) / 24., pw.caption if pw else "-", pw.frame_end if pw else "-",
             gap_before, nw.caption if nw else "-", nw.frame if nw else "-", lead,
             "!!! WORD INSIDE CUT: %r" % inside if inside else ""))
    # words actually spoken in range
    spoken = [w for w in nar.words if a <= w.frame <= b]
    tail_words = [w for w in spoken if w.frame_end > b]
    if tail_words:
        print("    word runs past shot end:", tail_words, [w.frame_end for w in tail_words])
    # last 3 frames before cut: any word starting?
    late = [w for w in spoken if w.frame > b - 3]
    if late:
        print("    word STARTS in the last 3 frames of the shot:", [(w.caption, w.frame) for w in late])
caps = nar.caption_frames(cuts=cuts[1:])
print("captions", len(caps))
short = [(c, a, b) for c, a, b in caps if b - a + 1 < 3]
print("captions on screen < 3 frames:", len(short), short)
# captions spanning a cut
for c, a, b in caps:
    for k in cuts[1:]:
        if a < k <= b:
            print("!!! caption across cut", c, a, b, k)
# captions in black ranges
for c, a, b in caps:
    if 1014 <= a <= 1015 or 1033 <= a <= 1034 or 655 <= a <= 667 or a >= 1564:
        print("caption on black:", c, a, b)
print([x for x in caps if x[1] > 1490])
print([x for x in caps if 640 < x[1] < 680])
print([x for x in caps if 995 < x[1] < 1070])
