"""The Hello, sequence MEADOW: try another "dawn" sky for me07 / me08 IN MEMORY (films/hello.py is the lead's and is
not edited: its SKIES["dawn"] is replaced in this process only, before the build). For a request to the lead.

    $BPY -m tools.hello_meadow_dawn_test --spec '{"preset": "dusk", "az": 75, "el": 4, "cloud_offset": [9, -6]}'
                                         --label dusk4 --frames 470[,505] [--res 540x960] [--samples 16] [--palette]
writes out/test/check_hello_meadow_dawn_<label>_<frame>.png (nothing else: no preview, no stamp); --palette also
prints tools/hello_palette's report of each frame (palette_check, heroes = st.hero's).
The spec REPLACES the whole entry (give every key: preset, az, el, bloom, grade, haze, ...).
Prefix with `nice -n 5 timeout 290`.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    ap = argparse.ArgumentParser(prog="tools.hello_meadow_dawn_test")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--res", default="540x960")
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--palette", action="store_true", help="also print tools/hello_palette's check of each frame")
    args = ap.parse_args(argv)
    spec = json.loads(args.spec)
    if "cloud_offset" in spec:
        spec["cloud_offset"] = tuple(int(v) for v in spec["cloud_offset"])
    import bpy  # noqa: F401
    from films import hello
    print("[dawn_test] SKIES['dawn'] was %r" % (hello.SKIES["dawn"],))
    hello.SKIES["dawn"] = spec                      # in this process only
    print("[dawn_test] SKIES['dawn'] now %r" % (spec,))
    import render
    ses = render.Session("hello", sky="dawn")
    w, h = (int(v) for v in args.res.split("x"))
    ses.configure((w, h), args.samples, args.threads, True)
    st = ses.result["stage"]
    bad = 0
    for f in (int(v) for v in args.frames.split(",")):
        path = os.path.join(ROOT, "out", "test", "check_hello_meadow_dawn_%s_%d.png" % (args.label, f))
        ses.render_frame(f, path)
        print("[dawn_test] rendered", path)
        if args.palette:                        # tools/hello_palette's check, on this frame of the trial sky
            from tools import palette_check
            shot = next(s for s in ses.film.shots if s.frame_start <= f <= s.frame_end)
            rec = palette_check.probe(ses.scene)
            rep = palette_check.evaluate(rec, path, heroes=st.heroes.get(shot.name, ()))
            palette_check.print_report("%s@%d" % (shot.name, f), rep)
            bad += 1 if rep["failed"] else 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
