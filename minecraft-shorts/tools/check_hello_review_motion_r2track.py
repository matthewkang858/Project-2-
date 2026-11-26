"""Review probe (motion lens, round 2): sub-pixel image motion of a region, frame to frame, by phase correlation.

    python3 tools/check_hello_review_motion_r2track.py A B [--crop x0,y0,x1,y1] [--src DIR] [--pat f_%04d.png]
            [--ref first|prev]

For every frame f in A+1..B prints dx, dy (px, 360x640 source) of the region against frame f-1 (prev) or against
frame A (first), with the peak strength. The region should be static scenery (camera motion) or one subject.
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageFilter


BLUR = [0.0]


def load(src, pat, f, crop):
    im = Image.open(os.path.join(src, pat % f)).convert("L")
    if BLUR[0] > 0:
        im = im.filter(ImageFilter.GaussianBlur(BLUR[0]))
    a = np.asarray(im, dtype=np.float64)
    if crop:
        x0, y0, x1, y1 = crop
        a = a[y0:y1, x0:x1]
    return a


def phase(a, b):
    """Shift (dx, dy) such that b(x) ~ a(x - d); sub-pixel by a parabolic fit around the peak."""
    h, w = a.shape
    win = np.outer(np.hanning(h), np.hanning(w))
    fa = np.fft.fft2((a - a.mean()) * win)
    fb = np.fft.fft2((b - b.mean()) * win)
    r = fb * np.conj(fa)
    r /= np.abs(r) ** 0.6 + 1e-9  # partial whitening: a fixed-seed grain pattern must not win
    c = np.real(np.fft.ifft2(r))
    iy, ix = np.unravel_index(np.argmax(c), c.shape)
    peak = c[iy, ix]

    def sub(cm, c0, cp):
        den = cm - 2 * c0 + cp
        return 0.0 if abs(den) < 1e-12 else 0.5 * (cm - cp) / den

    dy = iy + sub(c[(iy - 1) % h, ix], peak, c[(iy + 1) % h, ix])
    dx = ix + sub(c[iy, (ix - 1) % w], peak, c[iy, (ix + 1) % w])
    if dy > h / 2:
        dy -= h
    if dx > w / 2:
        dx -= w
    return dx, dy, peak


def main():
    p = argparse.ArgumentParser()
    p.add_argument("a", type=int)
    p.add_argument("b", type=int)
    p.add_argument("--crop", default=None)
    p.add_argument("--src", default="out/preview/hello/360x640_8spp")
    p.add_argument("--pat", default="f_%04d.png")
    p.add_argument("--ref", default="prev")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--blur", type=float, default=1.5, help="Gaussian blur radius before matching (kills grain)")
    a = p.parse_args()
    crop = [int(v) for v in a.crop.split(",")] if a.crop else None
    BLUR[0] = a.blur
    first = load(a.src, a.pat, a.a, crop)
    prev = first
    cx = cy = 0.0
    rows = []
    for f in range(a.a + 1, a.b + 1):
        cur = load(a.src, a.pat, f, crop)
        ref = prev if a.ref == "prev" else first
        dx, dy, pk = phase(ref, cur)
        if a.ref == "prev":
            cx += dx
            cy += dy
        else:
            cx, cy = dx, dy
        rows.append((f, dx, dy, pk, cx, cy))
        prev = cur
    if not a.quiet:
        for f, dx, dy, pk, cx, cy in rows:
            print("%4d  d(%+6.2f,%+6.2f)  cum(%+7.2f,%+7.2f)  peak %.2f" % (f, dx, dy, cx, cy, pk))
    dxs = np.array([r[1] for r in rows])
    dys = np.array([r[2] for r in rows])
    sp = np.hypot(dxs, dys)
    acc = np.hypot(np.diff(dxs), np.diff(dys)) if len(rows) > 1 else np.zeros(1)
    print("speed px/f: min %.2f med %.2f max %.2f | accel px/f2: med %.2f max %.2f at %d | total (%+.1f,%+.1f)"
          % (sp.min(), np.median(sp), sp.max(), np.median(acc), acc.max(), rows[int(acc.argmax()) + 1][0],
             rows[-1][4], rows[-1][5]))


if __name__ == "__main__":
    main()
