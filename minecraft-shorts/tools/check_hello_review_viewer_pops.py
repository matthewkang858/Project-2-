"""Viewer-eye review probe: frame-to-frame jumps inside shots (pops, flicker).

Mean absolute luma difference between consecutive source frames (no captions),
flagged when it is a spike against its shot's median and not on a cut.
usage: python3 tools/check_hello_review_viewer_pops.py
"""
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "..", "out", "preview", "hello", "360x640_8spp", "f_%04d.png")
TL = json.load(open(os.path.join(HERE, "..", "out", "test", "check_hello_review_viewer",
                                 "timeline.json")))


def L(f):
    return np.asarray(Image.open(SRC % f).convert("L").resize((90, 160))).astype(float)


for shot in TL:
    a, b = shot["frame_start"], shot["frame_end"]
    prev = L(a)
    d = []
    for f in range(a + 1, b + 1):
        cur = L(f)
        d.append((f, np.abs(cur - prev).mean()))
        prev = cur
    med = np.median([x for _, x in d])
    spikes = [(f, round(x, 1)) for f, x in d if x > max(3 * med, med + 4)]
    print("%-14s median %.2f spikes %s" % (shot["shot"], med, spikes[:12]))
