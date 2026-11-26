"""Review probe, round 2 (sound lens): sheets of ENCODED frames (captions included) of the RE-ENCODED preview
around the shots changed in round 2 and their cuts, each tile labelled with its frame number, the word being
spoken on it (narration/hello.json), the caption shown and the shot it belongs to.

    $BPY -m tools.check_hello_review_sync_r2_strips [name ...]   -> out/test/check_hello_review_sync_r2_strip_<name>.png
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MP4 = os.path.join(ROOT, "out", "preview", "hello_360x640_8spp.mp4")
TW, TH = 180, 320
COLS = 8

STRIPS = {
    "dn02": [68, 71, 72, 74, 76, 80, 85, 90, 94, 98, 101, 104, 108, 113, 118, 122, 128, 134, 140, 144, 145, 147, 150, 152],
    "me07": [414, 418, 420, 421, 422, 423, 424, 426, 430, 433, 436, 439, 442, 446, 450, 454, 457, 462, 467, 472, 477, 480,
             484, 485],
    "me08": [485, 487, 490, 494, 497, 501, 505, 509, 512, 516, 520, 524, 528, 532, 536, 540],
    "sq09": [536, 540, 541, 543, 550, 553, 558, 563, 567, 572, 577, 579, 583, 587, 591, 595, 600, 602, 604, 605, 606, 608,
             612, 620],
    "dg15": [908, 914, 915, 917, 924, 930, 932, 934, 936, 940, 944, 946, 947, 949, 951, 954, 956, 958, 961, 964, 967, 968,
             972, 977, 982, 988, 992, 997, 998, 1000, 1004, 1010],
    "in17": [1040, 1046, 1047, 1049, 1051, 1056, 1059, 1064, 1068, 1073, 1078, 1084, 1089, 1094, 1098, 1100, 1101, 1103,
             1106, 1111],
}


def word_at(words, fps, f):
    """The script word being spoken on frame number f (frame f covers [(f-1)/fps, f/fps))."""
    t = (f - 0.5) / fps
    for w in words:
        if w["start"] <= t < w["end"]:
            return w["caption"]
    return "-"


def grab(frames):
    """Frames (1-based numbers) of the mp4 as PIL images at TWxTH."""
    sel = "+".join("eq(n\\,%d)" % (f - 1) for f in frames)
    cmd = ["ffmpeg", "-v", "error", "-i", MP4, "-vf", "select='%s',scale=%d:%d" % (sel, TW, TH), "-vsync", "0",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = TW * TH * 3
    return [Image.fromarray(np.frombuffer(raw[i:i + n], dtype=np.uint8).reshape(TH, TW, 3)) for i in range(0, len(raw), n)]


def main(argv=None):
    names = (sys.argv[1:] if argv is None else argv) or list(STRIPS)
    nar = json.load(open(os.path.join(ROOT, "narration", "hello.json")))
    sync = json.load(open(os.path.join(ROOT, "out", "test", "narration_sync_hello_360x640_8spp.json")))
    tl = json.loads(subprocess.check_output([sys.executable, "-m", "tools.hello_timeline", "--json"], cwd=ROOT))
    shown = {}
    for r in sync["words"]:
        for f in range(r["caption_first_frame"], r["caption_last_frame"] + 1):
            shown[f] = r["word"]

    def shot_of(f):
        for s in tl:
            if s["frame_start"] <= f <= s["frame_end"]:
                return s["shot"].split("_")[0]
        return "?"

    for name in names:
        frames = sorted(STRIPS[name])
        ims = grab(frames)
        rows = (len(frames) + COLS - 1) // COLS
        sheet = Image.new("RGB", (COLS * TW, rows * (TH + 30)), (20, 20, 20))
        d = ImageDraw.Draw(sheet)
        for k, (f, im) in enumerate(zip(frames, ims)):
            x, y = (k % COLS) * TW, (k // COLS) * (TH + 30)
            sheet.paste(im, (x, y + 30))
            d.text((x + 3, y + 2), "%d %s say:%s" % (f, shot_of(f), word_at(nar["words"], nar["fps"], f)), fill=(255, 255, 120))
            d.text((x + 3, y + 15), "cap:%s" % shown.get(f, "-"), fill=(150, 220, 255))
        dst = os.path.join(ROOT, "out", "test", "check_hello_review_sync_r2_strip_%s.png" % name)
        sheet.save(dst)
        print(dst, len(ims), "frames")


if __name__ == "__main__":
    main()
