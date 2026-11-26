"""Viewer-eye review probe, round 2: per-shot contact strips from the new mp4.

Reads out/test/check_hello_review_viewer/r2/all/m_####.jpg (every frame of
the encoded preview, captions burned in, film frame numbering) and
r2/timeline.json, writes r2/strip_<shot>_s<step>.png with the Reels zones
(x 8-82 %, y 14-60 % green, caption band 62-72 % magenta, 86 % red).

usage: python3 tools/check_hello_review_viewer_r2strips.py step [shot|a-b ...]
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), "..", "out", "test",
                    "check_hello_review_viewer", "r2")
TL = json.load(open(os.path.join(ROOT, "timeline.json")))
STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 6
ARGS = sys.argv[2:]
W, H = 240, 427


def word_at(f):
    w, s = "", ""
    for shot in TL:
        if shot["frame_start"] <= f <= shot["frame_end"]:
            s = shot["shot"]
        for word, wf in shot["words"]:
            if wf <= f:
                w = word
    return s, w


def zones(d, x0, y0):
    d.rectangle([x0 + 0.08 * W, y0 + 0.14 * H, x0 + 0.82 * W, y0 + 0.60 * H],
                outline=(0, 255, 0))
    for y in (0.62, 0.72):
        d.line([x0, y0 + y * H, x0 + W, y0 + y * H], fill=(255, 0, 255))
    d.line([x0, y0 + 0.86 * H, x0 + W, y0 + 0.86 * H], fill=(255, 0, 0))


def sheet(name, frames, cols=6):
    cols = min(len(frames), cols)
    rows = (len(frames) + cols - 1) // cols
    im_s = Image.new("RGB", (cols * W, rows * (H + 16)), (20, 20, 20))
    d = ImageDraw.Draw(im_s)
    for i, f in enumerate(frames):
        im = Image.open(os.path.join(ROOT, "all", "m_%04d.jpg" % f))
        im = im.resize((W, H), Image.LANCZOS)
        x0, y0 = (i % cols) * W, (i // cols) * (H + 16)
        im_s.paste(im, (x0, y0))
        zones(d, x0, y0)
        s, w = word_at(f)
        d.text((x0 + 3, y0 + H + 2), "%d %s %s" % (f, s[:5], w),
               fill=(255, 255, 0))
    out = os.path.join(ROOT, "strip_%s_s%d.png" % (name, STEP))
    im_s.save(out)
    print(out, len(frames))


for shot in TL:
    if ARGS and shot["shot"] not in ARGS:
        continue
    a, b = shot["frame_start"], shot["frame_end"]
    frames = list(range(a, b + 1, STEP))
    if frames[-1] != b:
        frames.append(b)
    sheet(shot["shot"], frames)
for arg in ARGS:
    if "-" in arg and arg[0].isdigit():
        a, b = (int(x) for x in arg.split("-"))
        frames = list(range(a, b + 1, STEP))
        if frames[-1] != b:
            frames.append(b)
        sheet("r%d_%d" % (a, b), frames)
