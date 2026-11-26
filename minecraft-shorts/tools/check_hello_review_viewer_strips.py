"""Viewer-eye review probe: per-shot contact strips from the encoded preview.

Reads out/test/check_hello_review_viewer/v/v_####.png (frames pulled from the
mp4, captions burned in) and timeline.json, and writes one strip per shot
with every Nth frame labelled with its frame number and the word on screen.
Also draws the Reels zones (x 8-82 %, y 14-60 %, caption band 62-72 %, 86 %).

usage: python3 tools/check_hello_review_viewer_strips.py [step] [shot ...]
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), "..", "out", "test",
                    "check_hello_review_viewer")
TL = json.load(open(os.path.join(ROOT, "timeline.json")))
STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 6
ONLY = set(sys.argv[2:])
W, H = 240, 427
ZONES = True


def word_at(shot, f):
    w = ""
    for word, wf in shot["words"]:
        if wf <= f:
            w = word
    return w


def zones(d, x0, y0):
    d.rectangle([x0 + 0.08 * W, y0 + 0.14 * H, x0 + 0.82 * W, y0 + 0.60 * H],
                outline=(0, 255, 0))
    for y in (0.62, 0.72):
        d.line([x0, y0 + y * H, x0 + W, y0 + y * H], fill=(255, 0, 255))
    d.line([x0, y0 + 0.86 * H, x0 + W, y0 + 0.86 * H], fill=(255, 0, 0))


for shot in TL:
    if ONLY and shot["shot"] not in ONLY:
        continue
    a, b = shot["frame_start"], shot["frame_end"]
    frames = list(range(a, b + 1, STEP))
    if frames[-1] != b:
        frames.append(b)
    cols = min(len(frames), 6)
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W, rows * (H + 16)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(frames):
        im = Image.open(os.path.join(ROOT, "v", "v_%04d.png" % f))
        im = im.resize((W, H), Image.LANCZOS)
        x0, y0 = (i % cols) * W, (i // cols) * (H + 16)
        sheet.paste(im, (x0, y0))
        if ZONES:
            zones(d, x0, y0)
        d.text((x0 + 3, y0 + H + 2), "%d %s" % (f, word_at(shot, f)),
               fill=(255, 255, 0))
    out = os.path.join(ROOT, "strip_%s_s%d.png" % (shot["shot"], STEP))
    sheet.save(out)
    print(out, len(frames))
