"""Checker probe (story, words and time) for Twenty Minutes: text vs story, sentence timing, word frames, shots.
Pure Python except the optional --build (needs bpy). Run: python -m tools.check_twentyminutes_story_words"""
import ast
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import narration  # noqa

story = json.load(open(os.path.join(ROOT, "stories", "ironfarm.json")))
spec = narration.read_spec("twentyminutes")

# (1) text
print("== TEXT ==")
lines = [l["text"] if isinstance(l, dict) else (l[0] if isinstance(l, (list, tuple)) else l) for l in spec["lines"]]
beats = [b["line"] for b in story["beats"]]
print("sentences: spec %d, story beats %d" % (len(lines), len(beats)))
bad = 0
for i, (a, b) in enumerate(zip(lines, beats)):
    if a != b:
        bad += 1
        print("DIFF beat %d:\n  spec : %r\n  story: %r" % (i + 1, a, b))
joined = " ".join(lines)
print("joined == story narration:", joined == story["narration"])
if joined != story["narration"]:
    for i, (x, y) in enumerate(zip(joined, story["narration"])):
        if x != y:
            print("first diff at char", i, repr(joined[i - 20:i + 20]), repr(story["narration"][i - 20:i + 20]))
            break
print("words:", len(joined.split()), "story word_count", story.get("word_count"))
print("non-ascii chars in spec:", [c for c in joined if ord(c) > 127])

nar = narration.load("twentyminutes", spec)
print("\n== SENTENCES == frames %d, %.3f s, fps %d" % (nar.frames, nar.duration, nar.fps))
prev_end = None
for i, s in enumerate(nar.sentences):
    nxt = nar.sentences[i + 1].start if i + 1 < len(nar.sentences) else None
    gap = (nxt - s.end) if nxt is not None else (nar.duration - s.end)
    print("%s %6.2f-%6.2f (f%4d-%4d cut %4d) dur %.2f  pause_after %.2f  %d w  %s" % (
        s.id, s.start, s.end, s.frame, s.frame_end, s.cut, s.end - s.start, gap, len(s.words), s.text))
speech = sum(s.end - s.start for s in nar.sentences)
print("speech %.2f s; first word at %.2f; last word end %.2f; tail %.2f" % (
    speech, nar.words[0].start, nar.words[-1].end, nar.duration - nar.words[-1].end))

if "--words" in sys.argv:
    print("\n== WORDS ==")
    for w in nar.words:
        print("%3d s%02d %-12s %7.3f-%7.3f f%4d-%4d %s" % (w.index, w.sentence, w.caption, w.start, w.end, w.frame,
                                                             w.frame_end, w.source))
caps = None
