"""Checker probe (story angle): NARRATION vs story file, sentence timings, pauses, captions. Run with $BPY -m."""
import json, ast, sys
from engine import narration

src = open("films/hello.py").read()
tree = ast.parse(src)
NAR = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "NARRATION":
        NAR = ast.literal_eval(node.value)
story = json.load(open("stories/herobrine.json"))
lines = [l["text"] for l in NAR["lines"]]
beats = [b["line"] for b in story["beats"]]
print("n lines", len(lines), "n beats", len(beats))
for i, (a, b) in enumerate(zip(lines, beats)):
    if a != b:
        print("DIFF", i + 1, repr(a), repr(b))
print("join == narration:", " ".join(lines) == story["narration"])
print("words", sum(len(l.split()) for l in lines), story["word_count"])

nar = narration.load("films.hello", NAR, fps=24)
print(nar.summary())
print("frames", nar.frames, "seconds", nar.frames / 24.0)
S = nar.sentences
prev_end = None
for i, s in enumerate(S):
    ws = s.words
    a, b = ws[0], ws[-1]
    nxt = S[i + 1].words[0] if i + 1 < len(S) else None
    gap = (nxt.start - b.end) if nxt else (nar.frames / 24.0 - b.end)
    print("%s  start %6.2f (f%4d)  end %6.2f (f%4d)  dur %5.2f  gap-after %5.2f  cut f%d  | %s" % (
        s.id, a.start, a.frame, b.end, b.frame_end, b.end - a.start, gap, s.cut, s.text))
