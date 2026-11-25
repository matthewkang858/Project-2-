"""Checker's probe (pure Python, any interpreter): the engine.narration API used the way a director would, on the
one-minute probe narration (out/test/check_narration_dir/check_minute.*; made by tools/check_narration_minute.py)."""
import copy
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
before = set(sys.modules)
from engine import narration as N                                    # noqa: E402
print("importing engine.narration loaded bpy:", "bpy" in sys.modules, "| new modules:",
      sorted(m for m in set(sys.modules) - before if not m.startswith(("encodings", "_")))[:12])
from tools.check_narration_minute import SPEC, DIR, NAME            # noqa: E402  (imports numpy + tools.narrate)

N.NARRATION_DIR = DIR
nar = N.load(NAME, SPEC, fps=24)
nar2 = N.load(NAME, SPEC, fps=24)
assert nar.captions() == nar2.captions() and nar.frames == nar2.frames
print(nar.summary().splitlines()[0])
r = N.prove(nar)
print("prove:", r)
r1 = N.prove(nar, min_frames=1)
print("prove strict:", {k: r1[k] for k in ("early_ms_max", "shortest_caption_frames")})

# shots on every sentence, through the same float arithmetic as lookdev.Stage.shot / shots.Film.frame
lengths = nar.shot_frames(nar.sentences[1:])
t, starts = 0.0, []
for n in lengths:
    starts.append(int(round(t * 24)) + 1)
    t += nar.seconds(n)
end = int(round(t * 24))
assert starts == [1] + [s.cut for s in nar.sentences[1:]], (starts, [s.cut for s in nar.sentences])
assert end == nar.frames, (end, nar.frames)
print("22 shots through Stage.shot arithmetic start exactly on the cuts; film ends on frame", end)

# stale checks
def expect(label, fn):
    try:
        fn()
    except N.NarrationError as e:
        print("  refused (%s): %s" % (label, str(e)[:150]))
        return
    raise SystemExit("NOT refused: " + label)

s2 = copy.deepcopy(SPEC); s2["lines"][3] = "But I'm a piglin brute, and I do not trade."
expect("text", lambda: N.load(NAME, s2))
s2 = copy.deepcopy(SPEC); s2["lines"][2] = (SPEC["lines"][2][0], 0.7)
expect("pause", lambda: N.load(NAME, s2))
s2 = copy.deepcopy(SPEC); s2["voice"] = "bm_george"
expect("voice", lambda: N.load(NAME, s2))
s2 = copy.deepcopy(SPEC); s2["say"] = {"Crammys": "grammies"}
expect("say", lambda: N.load(NAME, s2))
s2 = copy.deepcopy(SPEC); s2["tail"] = 2.0
expect("tail", lambda: N.load(NAME, s2))
expect("fps", lambda: N.load(NAME, SPEC, fps=30))
# a comment-only / whitespace change must NOT make it stale
s2 = copy.deepcopy(SPEC); s2["lines"][0] = "In this bastion,   I'm the only one who doesn't like gold."
N.load(NAME, s2); print("  whitespace change accepted")
s2 = copy.deepcopy(SPEC); s2["say"] = {"crammys": "crammies"}       # key case
try:
    N.load(NAME, s2); print("  say key in another case accepted")
except N.NarrationError as e:
    print("  say key case -> stale:", str(e)[:80])
# another wav beside the json
alt = os.path.join(ROOT, "out", "test", "check_narration_dir2")
os.makedirs(alt, exist_ok=True)
shutil.copy(os.path.join(DIR, NAME + ".json"), alt)
with open(os.path.join(DIR, NAME + ".wav"), "rb") as f:
    data = bytearray(f.read())
data[5000] ^= 1
with open(os.path.join(alt, NAME + ".wav"), "wb") as f:
    f.write(data)
N.NARRATION_DIR = alt
expect("wav changed", lambda: N.load(NAME, SPEC))
N.NARRATION_DIR = DIR

# look-ups
print("sentence('armor').cut", nar.sentence("armor").cut, "| at('Mending')", nar.at("Mending"), nar.at("Mending", 1),
      "| at('64')", nar.at("64"), "| at('herobrine')", nar.at("herobrine"))
try:
    nar.sentence("He doesn't")
except KeyError as e:
    print("  ambiguous prefix refused:", e)
c = nar.cut_before("somebody")
caps = nar.captions(cuts=[s.cut for s in nar.sentences[1:]] + [c])
N.prove(nar)
cf = nar.caption_frames(cuts=[s.cut for s in nar.sentences[1:]] + [c])
i = [w.caption for w in nar.words].index("somebody")
print("mid-sentence cut before 'somebody': cut", c, "word frame", nar.at("somebody"), "previous caption", cf[i - 1], "this", cf[i])

# the long pause (1.5 s after 'me.'): the caption clears
i = [w.index for w in nar.sentence("armor").words][-1]
cf = nar.caption_frames()
w = nar.words[i]
print("long pause: %r spoken to frame %d, caption on %d-%d, next word %r from %d (cut %d)"
      % (w.caption, w.frame_end, cf[i][1], cf[i][2], cf[i + 1][0], cf[i + 1][1], nar.sentences[w.sentence + 1].cut))
# short pause: stays to the cut
w = nar.sentences[0].words[-1]
print("short pause: %r spoken to frame %d, caption on %d-%d, next sentence cut %d, first word %d"
      % (w.caption, w.frame_end, cf[w.index][1], cf[w.index][2], nar.sentences[1].cut, nar.sentences[1].frame))

# two modules
cut = nar.sentence("armor").cut
a, b = nar.part(1, cut - 1), nar.part(nar.sentence("armor"))
N.prove(a); N.prove(b)
off = (cut - 1) / 24.0
joined = a.captions() + [(w_, round(t0 + off, 5), round(t1 + off, 5)) for w_, t0, t1 in b.captions()]
whole = nar.captions()
diff = [(x, y) for x, y in zip(joined, whole) if x[0] != y[0] or abs(x[1] - y[1]) > 1e-4 or abs(x[2] - y[2]) > 1e-4]
print("parts: %d + %d frames = %d; captions that differ from the whole film's: %s" % (a.frames, b.frames, nar.frames, diff))

# captions the font cannot draw / odd tokens
from engine import captions as cap                                   # noqa: E402
odd = [w.caption for w in nar.words if not w.caption.replace("'", "").replace("-", "").isalnum()]
print("captions with other characters:", odd)
for tok in ("'Not", "again!'", "—", "pearls...", "14:07,", "100%", "(really?)", "“Run,”", "'em", "rock'n'roll", "I'M"):
    print("   caption_form(%r) = %r" % (tok, N.caption_form(tok)))
widths = []
for w in sorted({w.caption for w in nar.words}, key=len)[-4:]:
    im = cap.draw_caption(w, (1080, 1920))
    bb = im.getbbox()
    widths.append((w, round((bb[2] - bb[0]) / 1080.0, 2)))
print("widest captions (share of the frame width):", widths)
