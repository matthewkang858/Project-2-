"""Review probe (motion lens): best-match whole-frame shift between two preview frames (and residual).

    python3 tools/check_hello_review_motion_shift.py A B [A B ...] [--crop x0,y0,x1,y1]
"""
import sys
import numpy as np
from PIL import Image

SRC = "out/preview/hello/360x640_8spp"


def load(f, crop):
    a = np.asarray(Image.open("%s/f_%04d.png" % (SRC, f)).convert("L"), dtype=np.float32)
    if crop:
        x0, y0, x1, y1 = crop
        a = a[y0:y1, x0:x1]
    return a


def best(a, b, r=6):
    h, w = a.shape
    res = None
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            aa = a[r + dy:h - r + dy, r + dx:w - r + dx]
            bb = b[r:h - r, r:w - r]
            d = float(np.abs(aa - bb).mean())
            if res is None or d < res[0]:
                res = (d, dx, dy)
    return res


args = sys.argv[1:]
crop = None
if "--crop" in args:
    i = args.index("--crop")
    crop = [int(v) for v in args[i + 1].split(",")]
    args = args[:i] + args[i + 2:]
pairs = [(int(args[i]), int(args[i + 1])) for i in range(0, len(args), 2)]
for fa, fb in pairs:
    a, b = load(fa, crop), load(fb, crop)
    d0 = float(np.abs(a - b).mean())
    d, dx, dy = best(a, b)
    print("%d -> %d: raw %.2f, best shift (%d, %d) px residual %.2f" % (fa, fb, d0, dx, dy, d))
