"""Checker probe: word-level detail near every cut; caption frames per word; tight spots."""
from engine import narration
from films import hello
nar = narration.load("hello", hello.NARRATION, fps=24)
plan = hello.timeline(nar)
cuts = [r.frame_start for r in plan[1:]]
caps = nar.caption_frames(cuts=cuts)
W = nar.words
capmap = {}
ci = 0
for w in W:
    if w.caption:
        capmap[w.index] = caps[ci]; ci += 1
print("per-cut: last word before, first word after")
for r in plan[1:]:
    c = r.frame_start
    before = [w for w in W if w.frame < c][-1]
    after = [w for w in W if w.frame >= c][0]
    print("%-14s cut %4d | prev %-10s %4d-%4d (%.3f-%.3f s)  next %-10s %4d (%.3f s)  silence-before-cut %5.2f s  after-cut-to-voice %d f" % (
        r.name, c, before.text, before.frame, before.frame_end, before.start, before.end, after.text, after.frame, after.start,
        (c - 1) / 24.0 - before.end, after.frame - c))
print()
for i in range(len(W)):
    w = W[i]
    if 912 <= w.frame <= 1000 or 1355 <= w.frame <= 1490 or 140 <= w.frame <= 215 or 415 <= w.frame <= 445:
        print("%-10s f%4d-%4d  %.3f-%.3f  cap %s" % (w.text, w.frame, w.frame_end, w.start, w.end, capmap.get(i)))
print("short captions (<=4 frames):", [(c, a, b) for c, a, b in caps if b - a + 1 <= 4])
print("last caption:", caps[-1])
