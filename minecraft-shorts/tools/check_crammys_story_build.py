"""Checker probe: build the film (one sky) and compare its real shots and captions with the plan. No render."""
import os, sys, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import render
sky = sys.argv[1] if len(sys.argv) > 1 else "night"
t = time.time()
ses = render.Session("crammys", sky=sky)
print("built", sky, "%.1f s" % (time.time() - t))
res = ses.result
film, nar, caps, C = res["film"], res["narration"], res["captions"], res["context"]
from films import crammys
plan = crammys.timeline(nar)
print("film shots", len(film.shots), "plan", len(plan), "film end", film.shots[-1].frame_end, "nar.frames", nar.frames)
import bpy
sc = bpy.context.scene
print("scene frames", sc.frame_start, sc.frame_end, "res", sc.render.resolution_x, sc.render.resolution_y, "samples", sc.cycles.samples)
bad = 0
for s, r in zip(film.shots, plan):
    ok = (s.name == r.name and s.frame_start == r.frame_start and s.frame_end == r.frame_end)
    if not ok:
        bad += 1
    print("%s %-18s %4d-%4d  plan %-18s %4d-%4d sky %s" % ("OK" if ok else "XX", s.name, s.frame_start, s.frame_end, r.name, r.frame_start, r.frame_end, getattr(s, 'sky', '?')))
print("shot mismatches", bad)
# captions as frames
fps = 24.0
import math
EPS = 1e-6
cf = [(c, int(math.ceil(t0 * fps - EPS)) + 1, int(math.ceil(t1 * fps - EPS))) for c, t0, t1 in caps]
print("captions", len(cf), "words", len([w for w in nar.words if w.caption]))
rows = {r.name: r for r in plan}
def shot_of(f):
    for r in plan:
        if r.frame_start <= f <= r.frame_end:
            return r
for (c, a, b), w in zip(cf, [w for w in nar.words if w.caption]):
    r = shot_of(a); r2 = shot_of(b)
    flag = ""
    if r is not r2: flag += " STRADDLE"
    if b - a + 1 < 3: flag += " short(%d)" % (b - a + 1)
    if c != w.caption: flag += " MISMATCH"
    print("%-12s %4d-%4d  word %4d-%4d  %s%s" % (c, a, b, w.frame, w.frame_end, r.name, flag))
json.dump(cf, open(os.path.join(ROOT, "out/test/check_crammys_story_captions_%s.json" % sky), "w"))
