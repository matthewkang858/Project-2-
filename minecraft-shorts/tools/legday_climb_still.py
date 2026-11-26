"""Leg Day, the climb sequence's own stills: frames of ONE shot under staging and camera variants, one build.

    $BPY -m tools.legday_climb_still --sky gold --shot cl11_climb --frames 669,723 [--res 270x480] [--samples 8]
            [--set 'CLIMBERS=(("steve", 3.0), ...)'] [--cam "pos>target>lens[>pos1>target1>planned frames]"] ...
            [--zones] [--name legday_climb]
--set replaces module constants of films/legday_climb.py BEFORE the build (staging variants without editing the
file); each --cam is a moving camera variant planned like _repeat_cam (linear, `planned frames` long), v0, v1, ...;
without --cam the shot's own camera. Writes out/test/<name>_<shot>_<frame>[_v<i>].png (+ _zones.png).
"""
import argparse
import ast
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    """See the module docstring."""
    ap = argparse.ArgumentParser(prog="tools.legday_climb_still")
    ap.add_argument("--sky", default="gold")
    ap.add_argument("--shot", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--res", type=lambda t: tuple(int(v) for v in t.lower().split("x")), default=(540, 960))
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--zones", action="store_true")
    ap.add_argument("--name", default="legday_climb")
    ap.add_argument("--cam", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    args = ap.parse_args(argv)

    from films import legday_climb as M
    for spec in args.set:
        k, v = spec.split("=", 1)
        setattr(M, k.strip(), ast.literal_eval(v.strip()))
        print("[climb_still] set %s = %r" % (k.strip(), getattr(M, k.strip())))
    from PIL import Image

    import render
    from engine import post
    ses = render.Session("legday", sky=args.sky)
    ses.configure(args.res, args.samples, args.threads, True)
    C = ses.result["context"]
    s = {x.name: x for x in ses.film.shots}[args.shot]
    row = C.T[args.shot]
    frames = [int(v) for v in args.frames.split(",")]
    for f in frames:
        if not s.frame_start <= f <= s.frame_end:
            raise SystemExit("frame %d is not in %s (%d-%d)" % (f, args.shot, s.frame_start, s.frame_end))
    os.makedirs(os.path.join(ROOT, "out", "test"), exist_ok=True)
    variants = [None] + args.cam if not args.cam else args.cam
    for vi, spec in enumerate(variants):
        tag = ""
        if spec is not None:
            bits = spec.split(">")
            pos = tuple(float(v) for v in bits[0].split(","))
            tgt = tuple(float(v) for v in bits[1].split(","))
            lens = float(bits[2])
            s.lens(lens, s._fstop or 2.8)
            s.handheld(0.0, 0)
            if len(bits) > 3:
                plan = float(bits[5]) if len(bits) > 5 else float(row.frames)
                k = row.frames / plan
                p1 = tuple(p + (q - p) * k for p, q in zip(pos, (float(v) for v in bits[3].split(","))))
                t1 = tuple(p + (q - p) * k for p, q in zip(tgt, (float(v) for v in bits[4].split(","))))
                s.move(pos, tgt, p1, t1, ease="linear")
            else:
                s.move(pos, tgt)
            tag = "_v%d" % vi
        for f in frames:
            path = os.path.join(ROOT, "out", "test", "%s_%s_%d%s.png" % (args.name, args.shot, f, tag))
            t = time.time()
            ses.render_frame(f, path)
            print("[climb_still] %s frame %d %s -> %s  %.1f s" % (args.shot, f, spec or "own camera", path,
                                                                time.time() - t))
            if args.zones:
                with Image.open(path) as im:
                    post.draw_zones(im).save(path[:-4] + "_zones.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
