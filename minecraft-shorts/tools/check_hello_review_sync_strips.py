"""Review probe (sound lens): sheets of ENCODED frames (captions included) around the words that name an action,
each tile labelled with its frame number, the word being spoken on it (narration/hello.json) and the caption shown.

    $BPY -m tools.check_hello_review_sync_strips [name ...]      -> out/test/check_hello_review_sync_strip_<name>.png
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
    "dn02": [74, 76, 80, 84, 88, 92, 94, 97, 100, 103, 106, 110, 113, 117, 122, 128],
    "dg04": [213, 220, 226, 230, 232, 234, 236, 238, 240, 243, 246, 248, 252, 256, 262, 270],
    "dg05": [272, 276, 279, 282, 284, 286, 288, 290, 293, 296, 300, 304, 308, 312, 316, 318],
    "me06": [321, 330, 340, 348, 356, 362, 372, 380, 388, 391, 396, 404, 410, 414, 416, 418],
    "me07": [419, 420, 421, 422, 423, 424, 425, 426, 427, 430, 436, 442, 450, 457, 467, 484],
    "me08": [485, 490, 494, 497, 501, 505, 509, 512, 516, 520, 524, 528, 532, 536, 538, 540],
    "sq": [543, 558, 567, 579, 591, 600, 608, 625, 634, 641, 649, 660, 679, 691, 705, 716],
    "me12": [719, 741, 766, 774, 787, 792, 795, 812, 823, 836, 843, 846, 867, 877, 895, 914],
    "dg15": [917, 932, 936, 946, 947, 954, 961, 967, 968, 975, 988, 997, 1000, 1010, 1020, 1046],
    "dn18": [1049, 1073, 1100, 1103, 1111, 1125, 1132, 1138, 1142, 1147, 1153, 1162, 1170, 1180, 1188, 1192],
    "dn19": [1193, 1195, 1198, 1202, 1205, 1210, 1216, 1219, 1222, 1228, 1236, 1240, 1244, 1248, 1252, 1257],
    "dg20": [1258, 1264, 1270, 1280, 1284, 1293, 1300, 1308, 1315, 1324, 1328, 1334, 1340, 1346, 1352, 1357],
    "dg21": [1358, 1360, 1363, 1366, 1369, 1372, 1374, 1380, 1388, 1393, 1401, 1410, 1416, 1424, 1436, 1447],
    "dg22": [1448, 1453, 1463, 1467, 1471, 1475, 1482, 1490, 1500, 1510, 1520, 1530, 1537, 1538, 1539, 1544],
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
    shown = {}
    for r in sync["words"]:
        for f in range(r["caption_first_frame"], r["caption_last_frame"] + 1):
            shown[f] = r["word"]
    for name in names:
        frames = sorted(STRIPS[name])
        ims = grab(frames)
        rows = (len(frames) + COLS - 1) // COLS
        sheet = Image.new("RGB", (COLS * TW, rows * (TH + 30)), (20, 20, 20))
        d = ImageDraw.Draw(sheet)
        for k, (f, im) in enumerate(zip(frames, ims)):
            x, y = (k % COLS) * TW, (k // COLS) * (TH + 30)
            sheet.paste(im, (x, y + 30))
            d.text((x + 3, y + 2), "%d  say:%s" % (f, word_at(nar["words"], nar["fps"], f)), fill=(255, 255, 120))
            d.text((x + 3, y + 15), "cap:%s" % shown.get(f, "-"), fill=(150, 220, 255))
        dst = os.path.join(ROOT, "out", "test", "check_hello_review_sync_strip_%s.png" % name)
        sheet.save(dst)
        print(dst, len(ims), "frames")


if __name__ == "__main__":
    main()
