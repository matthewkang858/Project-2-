"""Checker's probe: the wrong-sky lock through the Python API, and a second build in the same process.

    $BPY -m tools.check_multisky_lock            # writes only out/test/check_multisky_lock_*.png, never meta.json
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import render as R  # noqa: E402

FILM = "_multisky_check_a"
VARIANT = "180x320_4spp"
D = os.path.join(ROOT, "out", "preview", FILM, VARIANT)
OUT = os.path.join(ROOT, "out", "test")


def refused(label, fn):
    """True when fn raises SkyError."""
    try:
        fn()
    except R.SkyError as e:
        print("OK   %-46s SkyError: %s" % (label, str(e)[:110]))
        return True
    except Exception as e:                                         # noqa: BLE001
        print("FAIL %-46s raised %s: %s" % (label, type(e).__name__, e))
        return False
    print("FAIL %-46s was NOT refused" % label)
    return False


def pix(path):
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"), dtype=np.int16)


def main():
    with open(os.path.join(D, "meta.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    seg = meta["sky_segments"]
    sky_of = lambda f: next(s for a, b, s in seg if a <= f <= b)   # noqa: E731
    bad = 0
    order = ["gold", "moon", "gold"]                               # the third build: back to the first sky
    for n, sky in enumerate(order):
        ses = R.Session(FILM, sky=sky)
        ses.configure((180, 320), 4, 2, None)
        book = R.Stamps(ses, FILM, VARIANT)
        other = next(f for f in range(1, 31) if sky_of(f) != sky)
        mine = [f for f in range(1, 37) if sky_of(f) == sky]
        tmp = os.path.join(OUT, "check_multisky_lock_wrong.png")
        for label, fn in (("render_frame(%d) in the %s build" % (other, sky), lambda: ses.render_frame(other, tmp)),
                          ("fingerprint(%d)" % other, lambda: ses.fingerprint(other)),
                          ("Stamps.status(%d)" % other, lambda: book.status(other)),
                          ("Stamps.fp(%d)" % other, lambda: book.fp(other)),
                          ("Stamps.mark(%d)" % other, lambda: book.mark(other))):
            bad += not refused(label, fn)
        if os.path.exists(tmp):
            print("FAIL a wrong-sky PNG was written")
            bad += 1
        # this process's build number n against the stamps written by FRESH processes
        diff = [f for f in mine if ses.fingerprint(f)["fp"] != meta["frames"][str(f)]["fp"]]
        print("%-4s build %d in this process (sky %s): %d of %d fingerprints equal to the fresh-process stamps%s"
              % ("OK" if not diff else "FAIL", n + 1, sky, len(mine) - len(diff), len(mine), " DIFFERENT: %s" % diff if diff else ""))
        bad += bool(diff)
        f = mine[0]                                                # the first frame of the sky: a fresh process's first render
        path = os.path.join(OUT, "check_multisky_lock_b%d_%s_f%04d.png" % (n + 1, sky, f))
        ses.render_frame(f, path)
        d = np.abs(pix(path) - pix(os.path.join(D, "f_%04d.png" % f)))
        print("%-4s build %d: frame %d rendered here vs the frame directory: mean %.4f max %d (%.1f %% of pixels)"
              % ("OK" if d.max() == 0 else "DIFF", n + 1, f, d.mean(), d.max(), 100.0 * (d.max(axis=2) > 0).mean()))
    print("failures:", bad)
    return bad


if __name__ == "__main__":
    sys.exit(main())
