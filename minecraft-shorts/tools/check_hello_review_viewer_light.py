"""Viewer-eye review probe: brightness, clipping and darkness per shot.

Reads the preview's source frames (no captions) every STEP frames and prints,
per shot: mean luma, luma of the 5th/50th/95th percentile, % of pixels with
any channel >= 250 (clipped), % of pixels with luma < 25 (crushed), and the
same for the face/hero zone (x 8-82 %, y 14-60 %).

usage: python3 tools/check_hello_review_viewer_light.py [step]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "..", "out", "preview", "hello", "360x640_8spp")
TL = json.load(open(os.path.join(HERE, "..", "out", "test",
                                 "check_hello_review_viewer", "timeline.json")))
STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 6

print("%-14s %5s %5s %5s %5s %6s %6s | zone %5s %6s %6s" % (
    "shot", "mean", "p5", "p50", "p95", "clip%", "dark%", "mean", "clip%",
    "dark%"))
for shot in TL:
    a, b = shot["frame_start"], shot["frame_end"]
    rows = []
    for f in range(a, b + 1, STEP):
        im = np.asarray(Image.open(os.path.join(SRC, "f_%04d.png" % f))
                        .convert("RGB")).astype(float)
        if im.mean() < 3:
            continue
        lum = im @ np.array([0.2126, 0.7152, 0.0722])
        h, w = lum.shape
        z = lum[int(0.14 * h):int(0.60 * h), int(0.08 * w):int(0.82 * w)]
        zc = im[int(0.14 * h):int(0.60 * h), int(0.08 * w):int(0.82 * w)]
        rows.append((lum.mean(), np.percentile(lum, 5), np.percentile(lum, 50),
                     np.percentile(lum, 95),
                     100 * (im.max(axis=2) >= 250).mean(),
                     100 * (lum < 25).mean(), z.mean(),
                     100 * (zc.max(axis=2) >= 250).mean(),
                     100 * (z < 25).mean()))
    r = np.array(rows).mean(axis=0)
    print("%-14s %5.0f %5.0f %5.0f %5.0f %6.2f %6.1f | zone %5.0f %6.2f %6.1f"
          % ((shot["shot"],) + tuple(r)))
