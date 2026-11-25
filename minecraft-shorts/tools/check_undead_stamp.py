"""Checker: scene fingerprints (engine.stamp) of the street probe are deterministic across processes and change
with the flash / swap / poof.  Run twice:  $BPY -m tools.check_undead_stamp"""
import sys
import time


def main():
    from tools import check_undead_film as F
    from engine import stamp

    scene, film, marks = F.build(sys.argv[1] if len(sys.argv) > 1 else "street")
    fp = stamp.Fingerprinter(scene, film)
    keys = sorted(marks, key=lambda k: marks[k] if isinstance(marks[k], int) else 0)
    frames = []
    for k in keys:
        if isinstance(marks[k], int) and marks[k] >= 1:
            frames += [marks[k] - 1, marks[k], marks[k] + 3]
    frames = sorted(set(f for f in frames if f >= 1))
    t0 = time.time()
    for f in frames:
        r = fp.frame(f)
        print("FP %4d %s o=%s" % (f, r["fp"][:16], r["parts"]["o"][:12]))
    print("time per frame %.3f s for %d frames" % ((time.time() - t0) / len(frames), len(frames)))


if __name__ == "__main__":
    main()
