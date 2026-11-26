"""Checker probe (story angle): narration literal vs story file; sentence timing; pauses; timeline vs words.
Run: $BPY tools/check_twoapples_story_nar.py   (from the project root; no render, no edit)"""
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
from engine import narration  # noqa: E402

story = json.load(open("stories/underground.json"))
import films.twoapples as T  # noqa: E402

# 1. text, character by character
lit = " ".join(l["text"] for l in T.NARRATION["lines"])
src = story["narration"]
print("TEXT IDENTICAL:", lit == src, len(lit), len(src))
if lit != src:
    for i, (a, b) in enumerate(zip(lit, src)):
        if a != b:
            print("first diff at", i, repr(lit[i - 20:i + 20]), repr(src[i - 20:i + 20]))
            break
beats = [b["line"] for b in story["beats"]]
lines = [l["text"] for l in T.NARRATION["lines"]]
print("BEATS == LINES:", beats == lines, len(beats), len(lines))
for i, (a, b) in enumerate(zip(lines, beats)):
    if a != b:
        print("  beat", i + 1, repr(a), "!=", repr(b))
print("word count literal:", len(lit.split()), "story says", story["word_count"])
print("ids:", [l.get("id") for l in T.NARRATION["lines"]])

# 2. timing
nar = narration.load("twoapples", T.NARRATION, fps=24)
print(nar.summary())
print("duration %.3f s frames %d" % (nar.duration, nar.frames))
js = json.load(open("narration/twoapples.json"))
print("json keys:", sorted(js.keys()))
print("\n%-4s %7s %7s %6s %6s  %s" % ("id", "start", "end", "pause", "dur", "text"))
S = nar.sentences
for i, s in enumerate(S):
    pause = (S[i + 1].start - s.end) if i + 1 < len(S) else (nar.duration - s.end)
    print("%-4s %7.3f %7.3f %6.3f %6.3f  %s" % (s.id, s.start, s.end, pause, s.end - s.start, s.text))
print("lead (first word start): %.3f" % S[0].start)
print("tail after last word: %.3f s = %.1f frames" % (nar.duration - S[-1].end, (nar.duration - S[-1].end) * 24))
speech = sum(s.end - s.start for s in S)
print("speech %.2f s, words %d, %.2f w/s" % (speech, len(nar.words), len(nar.words) / speech))
# internal gaps between words (longer than 0.25 s inside a sentence)
print("\nINTRA-SENTENCE GAPS > 0.2 s:")
for w0, w1 in zip(nar.words, nar.words[1:]):
    if w0.sentence == w1.sentence and w1.start - w0.end > 0.2:
        print("  %s: %r -> %r gap %.3f" % (S[w0.sentence].id, w0.caption, w1.caption, w1.start - w0.end))
print("\nWORDS (caption, start, end, frame, frame_end, estimated, source):")
for w in nar.words:
    print("  %3d s%-2d %-12s %7.3f %7.3f f%4d-%4d %s %s" % (w.index, w.sentence, w.caption, w.start, w.end, w.frame,
                                                       w.frame_end, "EST" if w.estimated else "", w.source))
for k in ("onset_check", "guarded_words", "loudness"):
    if k in js:
        print(k, json.dumps(js[k])[:3000])
