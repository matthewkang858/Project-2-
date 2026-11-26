"""Viewer-eye review probe, round 2: per-shot light on the preview PNGs.

Prints, for the middle frame of each shot (and named extra frames), mean luma,
the 1st/99th percentile, the share of pixels with any channel >= 250 (clipped)
and the share with luma < 25 (crushed). Reads the preview PNGs and r2/timeline.json.

usage: python3 tools/check_hello_review_viewer_r2light.py [frame ...]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "..", "out", "preview", "hello", "360x640_8spp")
TL = json.load(open(os.path.join(HERE, "..", "out", "test",
                                 "check_hello_review_viewer", "r2",
                                 "timeline.json")))


def stats(f):
    a = np.asarray(Image.open(os.path.join(SRC, "f_%04d.png" % f)).convert("RGB"),
                   dtype=np.float32)
    a = a[: int(a.shape[0] * 0.86)]
    y = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    clip = float(np.mean(a.max(axis=2) >= 250)) * 100
    crush = float(np.mean(y < 25)) * 100
    return y.mean(), np.percentile(y, 1), np.percentile(y, 99), clip, crush


frames = [(s["shot"], (s["frame_start"] + s["frame_end"]) // 2) for s in TL]
frames += [("extra", int(x)) for x in sys.argv[1:]]
for name, f in frames:
    m, lo, hi, clip, crush = stats(f)
    print("%-14s %5d mean %5.1f p1 %5.1f p99 %5.1f clip%% %5.2f crush%% %5.1f"
          % (name, f, m, lo, hi, clip, crush))
