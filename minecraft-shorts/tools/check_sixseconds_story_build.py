"""Checker probe: build the film (one sky) and print the real shot table, sky segments, fades and caption frames."""
import os, sys, math, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bpy
sky = sys.argv[-1] if sys.argv[-1] in ("wastes", "soul") else "wastes"
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
from films import sixseconds as F
out = F.build(scene, sky=sky)
film, st, nar, caps, C = out["film"], out["stage"], out["narration"], out["captions"], out["context"]
print("BROKEN", F.BROKEN)
print("film frames", film.frame_start, film.frame_end, "nar.frames", nar.frames, "scene", scene.frame_start, scene.frame_end,
      "res", scene.render.resolution_x, scene.render.resolution_y, "samples", scene.cycles.samples)
rows = []
for s in film.shots:
    rows.append((s.name, s.frame_start, s.frame_end))
print("SHOTS", json.dumps(rows))
print("SKY SEGMENTS", st.sky_segments())
fps = 24.0
fr = lambda t: int(round(t * fps)) + 1
print("FADES (frame from, frame to, g0, g1):", [(fr(a), fr(b), g0, g1) for a, b, g0, g1 in st.fades])
# black frames as the encoder computes: gain at frame k (0-based t = k/fps)
def gain(k):
    t = k / fps
    g = 1.0
    for a, b, g0, g1 in st.fades:
        if a - 1e-6 <= t < b - 1e-6:
            g = g0 + (g1 - g0) * (t - a) / (b - a)
    return g
black = [k + 1 for k in range(nar.frames) if gain(k) < 0.01]
runs = []
for f in black:
    if runs and runs[-1][1] == f - 1:
        runs[-1][1] = f
    else:
        runs.append([f, f])
print("BLACK RUNS", runs)
cf = [(c, int(math.ceil(t0 * fps - 1e-6)) + 1, int(math.ceil(t1 * fps - 1e-6))) for c, t0, t1 in caps]
print("CAPTIONS", len(cf))
cuts = [s.frame_start for s in film.shots[1:]]
bad = [(c, a, b, k) for c, a, b in cf for k in cuts if a < k <= b]
print("captions across a cut:", bad)
words = [w.caption for w in nar.words if w.caption]
print("every word once:", [c for c, a, b in cf] == words)
print("shortest caption", min(b - a + 1 for c, a, b in cf))
print("st.use per shot:")
for s in film.shots:
    print("  %-14s %s | heroes %s" % (s.name, sorted(st.in_shot.get(s.name, ())), [l for l, _ in st.heroes.get(s.name, [])]))
