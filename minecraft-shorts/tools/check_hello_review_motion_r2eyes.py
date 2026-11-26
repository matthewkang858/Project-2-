"""Review probe (motion lens, round 2): x-centroid of a villager's green eye pixels in a crop, per frame.

    python3 tools/check_hello_review_motion_r2eyes.py A B x0,y0,x1,y1 [--src DIR]

Green eye pixels: G > R + 30 and G > B + 20 and G > 60. Prints the centroid x, y and pixel count per frame and the
frame-to-frame step of x, so a head turn's progression (and any stale or popped frame) shows as numbers.
"""
import argparse
import os

import numpy as np
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument("a", type=int)
p.add_argument("b", type=int)
p.add_argument("crop")
p.add_argument("--src", default="out/preview/hello/360x640_8spp")
a = p.parse_args()
x0, y0, x1, y1 = [int(v) for v in a.crop.split(",")]
prev = None
for f in range(a.a, a.b + 1):
    im = np.asarray(Image.open(os.path.join(a.src, "f_%04d.png" % f)).convert("RGB"), dtype=np.int32)[y0:y1, x0:x1]
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    m = (g > r + 30) & (g > b + 20) & (g > 60)
    n = int(m.sum())
    if n:
        ys, xs = np.nonzero(m)
        cx, cy = xs.mean() + x0, ys.mean() + y0
        step = "" if prev is None else "%+.2f" % (cx - prev)
        print("%d  x %.2f  y %.2f  n %d  %s" % (f, cx, cy, n, step))
        prev = cx
    else:
        print("%d  no eye pixels" % f)
        prev = None
