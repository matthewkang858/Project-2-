"""Review probe (motion lens, round 2): camera trajectory of a region against the first frame, and its velocity.

    python3 tools/check_hello_review_motion_r2traj.py A B x0,y0,x1,y1 [--src DIR] [--pat f_%04d.png] [--blur 1.5]

Prints per-frame velocity (px/frame, 360x640) of the region measured against frame A (cumulative, so sub-pixel
motion is not lost), the velocity's mean and spread, and the largest frame-to-frame change of velocity.
"""
import argparse
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "tr", os.path.join(os.path.dirname(__file__), "check_hello_review_motion_r2track.py"))
tr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tr)

p = argparse.ArgumentParser()
p.add_argument("a", type=int)
p.add_argument("b", type=int)
p.add_argument("crop")
p.add_argument("--src", default="out/preview/hello/360x640_8spp")
p.add_argument("--pat", default="f_%04d.png")
p.add_argument("--blur", type=float, default=1.5)
p.add_argument("--rolling", action="store_true", help="re-anchor every 8 frames (for pushes)")
a = p.parse_args()
tr.BLUR[0] = a.blur
crop = [int(v) for v in a.crop.split(",")]
xs, ys = [0.0], [0.0]
anchor_f, ax, ay = a.a, 0.0, 0.0
ref = tr.load(a.src, a.pat, a.a, crop)
for f in range(a.a + 1, a.b + 1):
    cur = tr.load(a.src, a.pat, f, crop)
    dx, dy, _ = tr.phase(ref, cur)
    xs.append(ax + dx)
    ys.append(ay + dy)
    if a.rolling and f - anchor_f >= 8:
        anchor_f, ax, ay, ref = f, xs[-1], ys[-1], cur
x, y = np.array(xs), np.array(ys)
vx, vy = np.diff(x), np.diff(y)
line = []
for i in range(len(vx)):
    line.append("%d:%+.2f,%+.2f" % (a.a + 1 + i, vx[i], vy[i]))
for i in range(0, len(line), 8):
    print("  ".join(line[i:i + 8]))
ax_ = np.hypot(np.diff(vx), np.diff(vy))
print("v mean (%+.2f,%+.2f) std (%.2f,%.2f) | max dv %.2f at %d | total (%+.1f,%+.1f)"
      % (vx.mean(), vy.mean(), vx.std(), vy.std(), ax_.max(), a.a + 2 + int(ax_.argmax()), x[-1], y[-1]))
