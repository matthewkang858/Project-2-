"""Checker probe for tools/render_economics.py: re-measure the recommended setting (E, 540x960 at 16 samples) and
the current final (REF, 720x1280 at 24) on one study shot inside ONE process, and compare the pixels with what the
study stored. Writes only out/test/check_economics_*.

    $BPY -m tools.check_economics_remeasure SHOT        # SHOT = dusk | hall | sun | night | face
"""
import json
import os
import sys

from tools import render_economics as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")


def main(argv):
    shot = argv[0]
    threads = 2
    ses = E._session(shot)
    f = E.SHOTS[shot]["frame"]
    tiny = E._v(res=(90, 160), samples=1, cycles=dict(use_denoising=False))
    warm = os.path.join(OUT, "check_economics_warm_%s.png" % shot)
    E.measure(ses, shot, tiny, threads=threads, frame=f - 1, tag="warm", path=warm)
    if os.path.exists(warm):
        os.remove(warm)
    rows = []
    for label, variant in (("E", "r540s16"), ("REF", "base"), ("E_after24", "r540s16")):
        p = os.path.join(OUT, "check_economics_%s_%s.png" % (shot, label))
        rec = E.measure(ses, shot, variant, 0, False, threads, path=p)
        rows.append((label, rec, p))
        print("[check] %-10s %dx%d %2dspp  cpu %6.1f  trace %6.1f  wall %6.1f  load %.1f  seed %d animated %s"
              % (label, rec["res"][0], rec["res"][1], rec["samples"], rec["cpu"], rec["trace_cpu"], rec["wall"],
                 rec["load"], ses.scene.cycles.seed, ses.scene.cycles.use_animated_seed), flush=True)
    by = {k: (r, p) for k, r, p in rows}
    print("[check] E / REF cpu ratio %.3f" % (by["E"][0]["cpu"] / by["REF"][0]["cpu"]))
    fin = os.path.join(ROOT, "out", "frames", E.SHOTS[shot]["film"], "f_%04d.png" % f)
    print("[check] REF == finished film frame %s: %s" % (os.path.relpath(fin, ROOT), E.same_pixels(by["REF"][1], fin)))
    res = E.load_results()
    for key, rec in res.items():
        if rec.get("kind") is None and rec.get("shot") == shot and rec.get("variant") == "r540s16" and not rec.get("border") \
                and rec.get("seed") == 0 and rec.get("frame") == f:
            q = os.path.join(ROOT, rec["path"])
            if os.path.exists(q):
                print("[check] my E (first of process) == stored %-44s %s   | my E_after24 == it: %s"
                      % (key, E.same_pixels(by["E"][1], q), E.same_pixels(by["E_after24"][1], q)))
    print("[check] E == E_after24: %s" % E.same_pixels(by["E"][1], by["E_after24"][1]))
    with open(os.path.join(OUT, "check_economics_remeasure_%s.json" % shot), "w", encoding="utf-8") as fh:
        json.dump({k: r for k, r, _p in rows}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
