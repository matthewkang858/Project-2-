"""Review probe (motion lens): frame-to-frame difference over the whole preview.

    python3 tools/check_hello_review_motion_diff.py [src_dir] [out_json]

For every frame f > 1: the mean absolute difference to f-1 (whole frame, on a 4x box-downsample so the 8-sample
grain averages out), and the same for the 3x3 zone grid. Writes JSON with one row per frame.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else "out/preview/hello/360x640_8spp"
OUT = sys.argv[2] if len(sys.argv) > 2 else "out/test/check_hello_review_motion/diff.json"


def load(f):
    im = Image.open(os.path.join(SRC, "f_%04d.png" % f)).convert("RGB")
    a = np.asarray(im, dtype=np.float32)
    h, w, _ = a.shape
    a = a[: h // 4 * 4, : w // 4 * 4].reshape(h // 4, 4, w // 4, 4, 3).mean(axis=(1, 3))
    return a


def main():
    n = len([x for x in os.listdir(SRC) if x.startswith("f_") and x.endswith(".png")])
    rows = []
    prev = load(1)
    rows.append({"f": 1, "d": 0.0, "luma": float(prev.mean()), "zones": [0.0] * 9})
    for f in range(2, n + 1):
        cur = load(f)
        d = np.abs(cur - prev).mean(axis=2)
        h, w = d.shape
        zones = []
        for zy in range(3):
            for zx in range(3):
                zones.append(float(d[zy * h // 3:(zy + 1) * h // 3, zx * w // 3:(zx + 1) * w // 3].mean()))
        rows.append({"f": f, "d": float(d.mean()), "luma": float(cur.mean()), "zones": zones})
        prev = cur
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(rows, fh)
    print("wrote", OUT, len(rows))


if __name__ == "__main__":
    main()
