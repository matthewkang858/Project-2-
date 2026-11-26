"""Checker probe (story angle): build the film strict in one sky and compare its real shots and captions with the
timeline and the narration. Run: TWOAPPLES_STRICT=1 $BPY -m tools.check_twoapples_story_build [dusk|under]
Writes nothing but out/test/check_twoapples_story_build_<sky>.json."""
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bpy  # noqa: E402

sky = sys.argv[-1] if sys.argv[-1] in ("dusk", "under") else None
t0 = time.time()
from films import twoapples as T  # noqa: E402

out = T.build(bpy.context.scene, sky=sky)
print("build %.1f s, BROKEN=%s" % (time.time() - t0, list(T.BROKEN)))
film, nar, caps, C = out["film"], out["narration"], out["captions"], out["context"]
rows = T.timeline(nar)
fps = 24.0
res = {"shots": [], "problems": []}
for r, s in zip(rows, film.shots):
    ok = (s.name if hasattr(s, "name") else None, s.frame_start, s.frame_end) == (r.name, r.frame_start, r.frame_end)
    res["shots"].append([r.name, s.frame_start, s.frame_end, getattr(s, "sky", None), r.sky])
    if not ok:
        res["problems"].append("shot mismatch %s %s" % (r.name, (getattr(s, "name", None), s.frame_start, s.frame_end)))
print("film shots", len(film.shots), "rows", len(rows), "last end", film.shots[-1].frame_end, "nar.frames", nar.frames)
print("scene frame range", bpy.context.scene.frame_start, bpy.context.scene.frame_end,
      "res", bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y,
      "samples", bpy.context.scene.cycles.samples)
# captions as frames shown by the encoder
cf = [(c, int(math.ceil(a * fps - 1e-6)) + 1, int(math.ceil(b * fps - 1e-6))) for c, a, b in caps]
words = [w.caption for w in nar.words if w.caption]
print("captions", len(cf), "words", len(words), "same order:", [c for c, _a, _b in cf] == words)
cuts = [r.frame_start for r in rows[1:]]
for (c, a, b), w in zip(cf, [w for w in nar.words if w.caption]):
    if a > w.frame or a < w.frame - 2:
        res["problems"].append("caption %r shown from %d, spoken from frame %d" % (c, a, w.frame))
    for cut in cuts:
        if a < cut <= b:
            res["problems"].append("caption %r %d-%d straddles cut %d" % (c, a, b, cut))
    if b - a + 1 < 2:
        res["problems"].append("caption %r only %d frame(s)" % (c, b - a + 1))
    sh = [r.name for r in rows if r.frame_start <= a <= r.frame_end]
    sh_spoken = [r.name for r in rows if r.frame_start <= w.frame <= r.frame_end]
    if sh != sh_spoken:
        res["problems"].append("caption %r in %s but spoken in %s" % (c, sh, sh_spoken))
# compare with the frames the encoder shows by nar.caption_frames
print("PROBLEMS:", res["problems"] or "none")
# blank stretches with no caption over 1.0 s
prev_end = 0
for c, a, b in cf:
    if a - prev_end - 1 > 24:
        print("  no caption frames %d-%d (%.2f s) before %r" % (prev_end + 1, a - 1, (a - 1 - prev_end) / fps, c))
    prev_end = b
print("  last caption ends %d; film %d" % (prev_end, nar.frames))
# wall state per shot
for r in rows:
    print("  %-13s wall open first/last %s/%s" % (r.name, C.wall_is_open(r.frame_start), C.wall_is_open(r.frame_end)))
res["captions"] = cf
json.dump(res, open(os.path.join(ROOT, "out", "test", "check_twoapples_story_build_%s.json" % (sky or "dusk")), "w"),
          indent=1)
