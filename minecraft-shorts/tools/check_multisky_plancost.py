"""Checker's probe: what the bookkeeping of a 1,440-frame two-sky film costs per invocation, measured on a synthetic
frame directory (out/preview/_multisky_check_fake/720x1280_24spp_fake: 1,440 small 720x1280 PNGs and a meta.json with
1,440 stamps copied from the checker's own film). No Blender."""
import argparse
import json
import os
import sys
import time

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import render as R  # noqa: E402
from engine import post  # noqa: E402

NAME, VARIANT, N = "_multisky_check_fake", "720x1280_24spp_fake", 1440


def main():
    src = post.read_meta("_multisky_check_a", "180x320_4spp")
    d = post.frames_dir(NAME, VARIANT)
    os.makedirs(d, exist_ok=True)
    img = Image.new("RGB", (720, 1280), (90, 120, 200))
    t = time.time()
    for f in range(1, N + 1):
        p = post.frame_path(NAME, f, VARIANT)
        if not os.path.exists(p):
            img.save(p)
    print("wrote/kept %d PNGs in %.1f s" % (N, time.time() - t))
    one = next(iter(src["frames"].values()))
    meta = dict(src)
    meta["film"] = NAME
    meta["frame_start"], meta["frame_end"] = 1, N
    meta["sky_segments"] = [[1, 300, "gold"], [301, 600, "moon"], [601, 900, "gold"], [901, 1200, "moon"], [1201, N, "gold"]]
    sky = lambda f: next(s for a, b, s in meta["sky_segments"] if a <= f <= b)   # noqa: E731
    meta["frames"] = {str(f): dict(one, s="720x1280|24spp|mb1", sky=sky(f)) for f in range(1, N + 1)}
    meta["current"] = dict(src["current"], s="720x1280|24spp|mb1", fp={str(f): one["fp"] for f in range(1, N + 1)})
    meta["base"] = [720, 1280, 24, 1]
    meta["shots"] = [{"name": "s%d" % i, "frame_start": a, "frame_end": b, "sky": s}
                     for i, (a, b, s) in enumerate(meta["sky_segments"])]
    meta["captions"] = [["word%d" % i, i * 0.4, i * 0.4 + 0.35] for i in range(150)]
    t = time.time()
    for _ in range(5):
        post.write_meta(NAME, meta, VARIANT)
    w = (time.time() - t) / 5
    print("meta.json: %d KB, write %.0f ms" % (os.path.getsize(os.path.join(d, "meta.json")) // 1024, 1000 * w))
    args = argparse.Namespace(res=None, samples=None, no_motion_blur=False)
    t = time.time()
    p = R.Plan(NAME, VARIANT, args)
    t1 = time.time() - t
    t = time.time()
    states = {}
    for f in range(1, N + 1):
        states[p.status(f)] = states.get(p.status(f), 0) + 1
    t2 = time.time() - t
    print("Plan(): %.0f ms (read meta, hash %d source files, list the directory); status of %d frames: %.0f ms %s; "
          "usable=%s" % (1000 * t1, len(meta["sources"]), N, 1000 * t2, states, p.usable))
    t = time.time()
    v = post.valid_frames(NAME, VARIANT)
    print("post.valid_frames: %d valid in %.0f ms" % (len(v), 1000 * (time.time() - t)))
    per_plan = t1 + t2
    print("per invocation of a 900 s chunk (about 65 frames at 14 s): 3 plans = %.2f s, 65 meta writes = %.2f s"
          % (3 * per_plan, 65 * w))


if __name__ == "__main__":
    main()
