"""Checker B: decode chosen frames of an mp4 (frame NUMBERS, 1-based) and paste them side by side.

    $BPY -m tools.check_multisky_b_extract MP4 OUT.png SCALE F1,F2,...   # SCALE = fraction of 1080x1920 per tile
Prints per frame: mean of the picture (whole frame), mean of the caption band's brightest pixels.
"""
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw


def frames_of(mp4, numbers, size=(1080, 1920)):
    """{frame number: HxWx3 uint8} decoded by ffmpeg (select by index, exact)."""
    w, h = size
    sel = "+".join("eq(n\\,%d)" % (f - 1) for f in numbers)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "select='%s'" % sel, "-vsync", "0",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, check=True).stdout
    n = len(raw) // (w * h * 3)
    arr = np.frombuffer(raw, np.uint8).reshape(n, h, w, 3)
    return {f: arr[i] for i, f in enumerate(sorted(numbers))}


def main(argv):
    mp4, out, scale = argv[0], argv[1], float(argv[2])
    numbers = [int(x) for x in argv[3].split(",")]
    got = frames_of(mp4, numbers)
    tw, th = int(1080 * scale), int(1920 * scale)
    cols = min(len(numbers), int(argv[4]) if len(argv) > 4 else 8)
    rows = (len(numbers) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 4), rows * (th + 18)), (30, 30, 34))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(numbers):
        a = got[f]
        im = Image.fromarray(a).resize((tw, th), Image.LANCZOS)
        x, y = (i % cols) * (tw + 4), (i // cols) * (th + 18)
        sheet.paste(im, (x, y + 16))
        d.text((x + 3, y + 2), "f%d" % f, fill=(255, 255, 255))
        band = a[int(1920 * 0.62):int(1920 * 0.72)]
        print("frame %4d  mean %6.2f  top-quarter %6.2f  caption-band max %3d  band white px %6d"
              % (f, a.mean(), a[:480].mean(), band.max(), int((band.min(axis=2) >= 250).sum())))
    sheet.save(out)
    print("->", out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1:])
