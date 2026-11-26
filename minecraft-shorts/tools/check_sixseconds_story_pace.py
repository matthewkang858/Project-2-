"""Checker probe (story angle): sentence and word timing of narration/sixseconds.json. Pure python."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import narration
nar = narration.load("sixseconds")
print("frames", nar.frames, "duration", nar.duration, "voice", nar.voice, nar.speed)
data = nar.data
print("keys", sorted(data.keys()))
S = nar.sentences
speech = 0
for i, s in enumerate(S):
    nxt = S[i + 1].start if i + 1 < len(S) else nar.duration
    gap = nxt - s.end
    speech += s.end - s.start
    print("%2d %-4s %6.2f-%6.2f (%4.2f s, %2d w, %.2f w/s) gap-after %.2f  f%4d-%4d cut %4d | %s"
          % (i, s.id, s.start, s.end, s.end - s.start, len(s.words), len(s.words) / (s.end - s.start), gap,
             s.frame, s.frame_end, s.cut, s.text))
print("speech %.2f s, words/s speaking %.2f, words per film-second %.2f" % (speech, len(nar.words) / speech, len(nar.words) / nar.duration))
print("lead (first word start) %.3f" % nar.words[0].start)
print("tail (film end - last word end) %.3f" % (nar.duration - nar.words[-1].end))
# intra-sentence gaps > 0.25 s
for w0, w1 in zip(nar.words, nar.words[1:]):
    if w0.sentence == w1.sentence and w1.start - w0.end > 0.2:
        print("in-sentence gap %.2f after %r (f%d) before %r" % (w1.start - w0.end, w0.caption, w0.frame_end, w1.caption))
if "--words" in sys.argv:
    for w in nar.words:
        print("  %3d s%02d %-10s f%4d-%4d  %.3f-%.3f %s" % (w.index, w.sentence, w.caption, w.frame, w.frame_end, w.start, w.end, w.source))
