"""Checker's probe: snapshot / compare the PNGs of a frame directory by PIXELS and modification time.

    python -m tools.check_multisky_snap snap <dir> <name>        # -> out/test/check_multisky_snap_<name>.json
    python -m tools.check_multisky_snap diff <nameA> <nameB>     # which frames were written again / changed pixels
    python -m tools.check_multisky_snap pix <dirA> <dirB> [frames A-B]   # pixel differences between two directories
    python -m tools.check_multisky_snap stamps <dir>             # the stamps and expectations of a meta.json
"""
import hashlib
import json
import os
import re
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")


def _frames(d):
    out = {}
    for n in sorted(os.listdir(d)):
        m = re.fullmatch(r"f_(\d{4,})\.png", n)
        if m:
            out[int(m.group(1))] = os.path.join(d, n)
    return out


def _pix(path):
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"), dtype=np.int16)


def _ranges(frames):
    out, frames = [], sorted(frames)
    i = 0
    while i < len(frames):
        j = i
        while j + 1 < len(frames) and frames[j + 1] == frames[j] + 1:
            j += 1
        out.append(str(frames[i]) if i == j else "%d-%d" % (frames[i], frames[j]))
        i = j + 1
    return ", ".join(out) or "-"


def snap(d, name):
    """Write the snapshot of a directory."""
    rec = {}
    for f, p in _frames(d).items():
        rec[str(f)] = [os.stat(p).st_mtime_ns, hashlib.sha1(_pix(p).tobytes()).hexdigest()[:16]]
    meta = os.path.join(d, "meta.json")
    stamps = {}
    if os.path.exists(meta):
        with open(meta, encoding="utf-8") as fh:
            m = json.load(fh)
        stamps = {k: [v.get("sky"), v.get("fp"), v.get("e")] for k, v in m.get("frames", {}).items()}
    with open(os.path.join(OUT, "check_multisky_snap_%s.json" % name), "w", encoding="utf-8") as fh:
        json.dump({"dir": d, "frames": rec, "stamps": stamps}, fh)
    print("snap %s: %d frames" % (name, len(rec)))


def diff(a, b):
    """Print what happened between two snapshots."""
    with open(os.path.join(OUT, "check_multisky_snap_%s.json" % a), encoding="utf-8") as fh:
        A = json.load(fh)
    with open(os.path.join(OUT, "check_multisky_snap_%s.json" % b), encoding="utf-8") as fh:
        B = json.load(fh)
    fa, fb = A["frames"], B["frames"]
    gone = [int(k) for k in fa if k not in fb]
    new = [int(k) for k in fb if k not in fa]
    rewritten = [int(k) for k in fa if k in fb and fa[k][0] != fb[k][0]]
    pixels = [int(k) for k in fa if k in fb and fa[k][1] != fb[k][1]]
    restamped = [int(k) for k in A["stamps"] if k in B["stamps"] and A["stamps"][k] != B["stamps"][k]]
    print("%s -> %s: PNG written again: %s | pixels changed: %s | new: %s | deleted: %s | stamp changed: %s"
          % (a, b, _ranges(rewritten), _ranges(pixels), _ranges(new), _ranges(gone), _ranges(restamped)))


def pix(da, db, spec=None):
    """Pixel differences of the frames two directories share."""
    fa, fb = _frames(da), _frames(db)
    both = sorted(set(fa) & set(fb))
    if spec:
        lo, hi = (int(x) for x in (spec.split("-") + [spec])[:2])
        both = [f for f in both if lo <= f <= hi]
    same = []
    for f in both:
        a, b = _pix(fa[f]), _pix(fb[f])
        if a.shape != b.shape:
            print("frame %d: sizes differ %s %s" % (f, a.shape, b.shape))
            continue
        d = np.abs(a - b)
        if d.max() == 0:
            same.append(f)
        else:
            print("frame %4d: DIFFERENT mean %.3f max %d, %.1f %% of pixels differ, means %.1f vs %.1f"
                  % (f, d.mean(), d.max(), 100.0 * (d.max(axis=2) > 0).mean(), a.mean(), b.mean()))
    print("pixel-identical: %s (%d of %d shared frames)" % (_ranges(same), len(same), len(both)))


def stamps(d):
    """Print a meta.json's stamps."""
    with open(os.path.join(d, "meta.json"), encoding="utf-8") as fh:
        m = json.load(fh)
    cur = m.get("current", {})
    print("segments:", m.get("sky_segments"), "| skies:", list((m.get("skies") or {})), "| fades:", m.get("fades"))
    print("current: s=%s e=%s fp for %s" % (cur.get("s"), cur.get("e"), _ranges(int(k) for k in cur.get("fp", {}))))
    by = {}
    for k, v in m.get("frames", {}).items():
        ok = v.get("fp") == cur.get("fp", {}).get(k) and v.get("e") == cur.get("e") and v.get("s") == cur.get("s")
        by.setdefault((v.get("sky"), "valid" if ok else "not-current"), []).append(int(k))
    for key in sorted(by, key=str):
        print("  stamps sky=%s %s: %s" % (key[0], key[1], _ranges(by[key])))
    print("  PNGs on disk:", _ranges(_frames(d)))


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"snap": snap, "diff": diff, "pix": pix, "stamps": stamps}[cmd](*sys.argv[2:])
