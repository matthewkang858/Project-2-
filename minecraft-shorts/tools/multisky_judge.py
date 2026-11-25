"""Judge the frames of a film against the scene as it builds NOW, and write nothing (not meta.json, not a frame).

    $BPY -m tools.multisky_judge bell                       # final frames: status of every frame + seconds per frame
    $BPY -m tools.multisky_judge bell --save A.json         # also store {frame: fingerprint, parts} in a file
    $BPY -m tools.multisky_judge bell --compare A.json      # ... and compare with a stored run (exit 1 if any differs)
    $BPY -m tools.multisky_judge _multisky_demo --sky night --res 360x640 --samples 8   # one sky of a multi-sky film
    $BPY -m tools.multisky_judge bell --every 12            # every 12th frame only (a quick check)

What it is for:
  * the proof that an edit to render.py / engine/post.py / films/lookdev.py changed no picture of a finished film:
    run it before and after, --save / --compare (the SCENE FINGERPRINT of every frame must be the same), and read the
    status counts ('engine' = other engine sources, same picture; 'engine+scene' or 'scene' = the picture changed);
  * the measurement of what judging costs: seconds for the build, seconds per fingerprint.
A multi-sky film is judged one sky per call (--sky), exactly as render.py judges it: a frame is only ever
fingerprinted in a build whose active sky is its own.
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv=None):
    """Entry point of `python -m tools.multisky_judge`; returns the exit code."""
    import render as R

    ap = argparse.ArgumentParser(prog="tools.multisky_judge")
    ap.add_argument("film")
    ap.add_argument("--sky", help="the sky of a multi-sky film to build and judge (default: its first)")
    ap.add_argument("--res", type=R._parse_res)
    ap.add_argument("--samples", type=int)
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--every", type=int, default=1, help="judge only every K-th frame")
    ap.add_argument("--save", metavar="JSON", help="store the fingerprints of the judged frames")
    ap.add_argument("--compare", metavar="JSON", help="compare the fingerprints with a stored run")
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)

    t = time.time()
    ses = R.Session(args.film, sky=args.sky) if args.sky else R.Session(args.film)
    t_build = time.time() - t
    ses.configure(args.res, args.samples, R.FINAL_THREADS, None)
    variant = R.variant_of(args.res, args.samples, args.step)
    book = R.Stamps(ses, args.film, variant)
    book.cur_fp = {}                                           # never trust the stored expectation here
    owns = getattr(ses, "owns", lambda f: True)
    frames = [f for f in range(ses.film.frame_start, ses.film.frame_end + 1, max(1, args.every)) if owns(f)]
    t = time.time()
    fps = {str(f): ses.fingerprint(f) for f in frames}
    t_fp = time.time() - t
    for k, d in fps.items():
        book.cur_fp[k] = d["fp"]
    counts = {}
    for f in frames:
        st = book.status(f)
        counts.setdefault(st, []).append(f)
    sky = getattr(ses, "sky", None)
    print("[judge] %s%s: build %.1f s, %d frames fingerprinted in %.1f s = %.0f ms per frame"
          % (args.film, " [sky %s]" % sky if sky else "", t_build, len(frames), t_fp, 1000.0 * t_fp / max(1, len(frames))))
    print("[judge] %s -> %s" % (args.film, {k: "%d (%s)" % (len(v), R._ranges(v)) for k, v in sorted(counts.items())}))
    out = {k: {"fp": d["fp"], "parts": d["parts"]} for k, d in fps.items()}
    code = 0
    if args.compare:
        with open(args.compare, encoding="utf-8") as fh:
            old = json.load(fh)
        both = [k for k in out if k in old]
        diff = [int(k) for k in both if old[k]["fp"] != out[k]["fp"]]
        parts = sorted({p for k in both for p in "gcol" if old[k]["parts"].get(p) != out[k]["parts"].get(p)})
        print("[judge] compared with %s: %d frames in both, %d fingerprints differ%s"
              % (args.compare, len(both), len(diff), " (%s; parts %s)" % (R._ranges(diff), "".join(parts)) if diff else ""))
        code = 1 if diff or not both else 0
    if args.save:
        with open(args.save, "w", encoding="utf-8") as fh:
            json.dump(out, fh)
        print("[judge] fingerprints ->", args.save)
    return code


if __name__ == "__main__":
    sys.exit(main())
