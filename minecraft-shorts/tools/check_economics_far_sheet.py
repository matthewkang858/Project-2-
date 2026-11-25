"""Checker probe: sheets and numbers for tools/check_economics_far.py. Per mode (REF above, E below) the consecutive
frames as DELIVERED (Lanczos to 1080x1920, engine.post.upscale), a window around the far figures enlarged 3 times
with nearest neighbour; and the brightest pixel and its position inside each head window per frame (do the white
eye texels hold from frame to frame?).

    $BPY -m tools.check_economics_far_sheet night|golden X0 Y0 X1 Y1 [FRAME ...]   # window in 1080x1920 pixels
"""
import os
import sys

import numpy as np
from PIL import Image

from engine import post

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST = os.path.join(ROOT, "out", "test")


def main(argv):
    sky = argv[0]
    box = tuple(int(a) for a in argv[1:5])
    frames = [int(a) for a in argv[5:]] or [10, 11, 12, 13]
    zoom = 3
    w, h = (box[2] - box[0]) * zoom, (box[3] - box[1]) * zoom
    rows = []
    for mode in ("REF", "E"):
        tiles = []
        for f in frames:
            p = os.path.join(TEST, "check_economics_far_%s_%s_%03d.png" % (sky, mode, f))
            if not os.path.exists(p):
                continue
            with Image.open(p) as im:
                up = post.upscale(im)
            crop = up.crop(box)
            a = np.asarray(crop).astype(np.float32)
            lum = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
            half = lum.shape[1] // 2
            msg = []
            for name, part, off in (("left", lum[:, :half], 0), ("right", lum[:, half:], half)):
                y, x = np.unravel_index(int(part.argmax()), part.shape)
                msg.append("%s max %.0f at (%d,%d)" % (name, part.max(), x + off, y))
            print("[check] %s %-3s frame %d: %s" % (sky, mode, f, "; ".join(msg)))
            tiles.append(crop.resize((w, h), Image.NEAREST))
        if tiles:
            rows.append(tiles)
    if not rows:
        return 1
    n = max(len(r) for r in rows)
    sheet = Image.new("RGB", (n * (w + 6), len(rows) * (h + 6)), (60, 0, 60))
    for j, r in enumerate(rows):
        for i, t in enumerate(r):
            sheet.paste(t, (i * (w + 6), j * (h + 6)))
    out = os.path.join(TEST, "check_economics_far_%s_sheet.png" % sky)
    sheet.save(out)
    print("[check] wrote", out, "(rows: REF, E; columns: frames %s)" % frames)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
