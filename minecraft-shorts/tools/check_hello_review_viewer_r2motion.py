"""Viewer-eye review probe, round 2: per-frame motion on the preview PNGs.

For each frame range, prints mean grey-level change to the previous frame and
the global image shift (phase correlation, px at 360x640) so camera sway or a
stall can be judged.  Reads out/preview/hello/360x640_8spp/f_####.png, writes
nothing.

usage: python3 tools/check_hello_review_viewer_r2motion.py a-b [a-b ...]
"""
import os
import sys

import numpy as np
from PIL import Image

SRC = os.path.join(os.path.dirname(__file__), "..", "out", "preview", "hello",
                   "360x640_8spp")


def grey(f):
    im = Image.open(os.path.join(SRC, "f_%04d.png" % f)).convert("L")
    return np.asarray(im, dtype=np.float32)


def shift(a, b):
    # phase correlation on the top 60 % (no caption) with a Hann window
    h = int(a.shape[0] * 0.6)
    a, b = a[:h], b[:h]
    win = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    fa, fb = np.fft.fft2(a * win), np.fft.fft2(b * win)
    r = fa * np.conj(fb)
    r /= np.abs(r) + 1e-9
    c = np.abs(np.fft.ifft2(r))
    # upsample around the peak by parabolic fit
    y, x = np.unravel_index(np.argmax(c), c.shape)

    def sub(cm, c0, cp):
        d = cm - 2 * c0 + cp
        return 0.0 if d == 0 else 0.5 * (cm - cp) / d
    dy = y + sub(c[(y - 1) % c.shape[0], x], c[y, x], c[(y + 1) % c.shape[0], x])
    dx = x + sub(c[y, (x - 1) % c.shape[1]], c[y, x], c[y, (x + 1) % c.shape[1]])
    if dy > c.shape[0] / 2:
        dy -= c.shape[0]
    if dx > c.shape[1] / 2:
        dx -= c.shape[1]
    return dx, dy


for arg in sys.argv[1:]:
    a, b = (int(x) for x in arg.split("-"))
    prev = grey(a)
    print("== %s" % arg)
    rows = []
    for f in range(a + 1, b + 1):
        cur = grey(f)
        d = float(np.mean(np.abs(cur - prev)))
        dx, dy = shift(prev, cur)
        rows.append((f, d, dx, dy))
        prev = cur
    for f, d, dx, dy in rows:
        print("%5d diff %5.2f shift %+6.2f %+6.2f" % (f, d, dx, dy))
    ds = np.array([r[1] for r in rows])
    print("   diff min %.2f med %.2f max %.2f" % (ds.min(), np.median(ds), ds.max()))
