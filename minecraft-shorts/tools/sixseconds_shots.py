"""Six Seconds: stills of single shots, one build per sky, and a contact sheet with one tile per shot.

    $BPY -m tools.sixseconds_shots plan                              # shots, frames, sky of each tile (no build)
    $BPY -m tools.sixseconds_shots build [--sky soul]                # build one sky only: who is in which shot (the
                                                                     #   strict build: SIXSECONDS_STRICT=1 in front)
    $BPY -m tools.sixseconds_shots render --shots pt09_axe,pt10_smoke [--at 0.5] [--frame N[,M...]] [--res 540x960]
                               [--samples 16] [--zones] [--name sixseconds_scout_pit] [--dir out/test]
                               [--move x,y,z:tx,ty,tz[:lens]/...]
        renders the frame at fraction `at` of each shot (or frame N) in ONE process for the sky the shots need;
        writes <dir>/<name or sixseconds_shot>_<shot>[_<frame>].png (+ _zones.png). Shots of the other sky are
        refused: give the shots of one sky per call (render.py's rule: a frame is rendered in the build of its sky).
        --move renders camera variants v0, v1 ... of the same shots (scouting only).
    $BPY -m tools.sixseconds_shots tiles --sky wastes [--at 0.5] [--shots a,b]   # sheet tiles (270x480, 8 samples)
                                                                     #   -> out/test/sixseconds_tiles/
    $BPY -m tools.sixseconds_shots sheet                             # the tiles in film order, captioned and
                                                                     #   labelled, the encoder's black applied ->
                                                                     #   out/test/sixseconds_shots_sheet.png
The two skies: "wastes" (every shot but these) and "soul" (br11-br15, fl16_bridge). Each call must finish inside the
command time limit: a build is about 5-10 s, a 540x960 16-sample still 10-60 s on the shared machine, a 270x480
8-sample tile 4-15 s. Prefix with `nice -n 15 timeout 290`.
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

FILM = "sixseconds"
TILE_DIR = os.path.join(ROOT, "out", "test", "sixseconds_tiles")


def _plan():
    """(Narration, [ShotInfo]) without a scene (narration + timeline only)."""
    from engine import narration
    from films import sixseconds as F
    nar = narration.load(FILM, F.NARRATION, fps=F.FPS)
    return nar, F.timeline(nar)


def _frame_of(row, at=None, frame=None):
    """The frame of a shot to render: `frame` itself, or the fraction `at` of the shot (never on its black)."""
    if frame is not None:
        return int(frame)
    at = 0.5 if at is None else float(at)
    last = row.frame_end
    first = row.frame_start
    if row.black is not None:
        a, b = row.black
        if a == first:
            first = b + 1
        else:
            last = a - 1
    return int(round(first + at * (last - first)))


def _session(sky):
    """A render.Session of the film built with `sky`."""
    import render
    t = time.time()
    ses = render.Session(FILM, sky=sky)
    print("[sixseconds_shots] built sky %s in %.1f s" % (sky, time.time() - t))
    return ses


def cmd_plan(args):
    """Print shots with the frame and sky of their middle tile."""
    nar, rows = _plan()
    for r in rows:
        f = _frame_of(r, args.at)
        print("%-14s %4d-%4d  tile %4d  sky %s%s" % (r.name, r.frame_start, r.frame_end, f, r.sky,
                                                    "  black %d-%d" % r.black if r.black else ""))
    return 0


def cmd_build(args):
    """Build one sky and print who is in which shot (and any '!!!' of the guarded build)."""
    ses = _session(args.sky)
    st = ses.result["stage"]
    for s in ses.film.shots:
        print("%-14s %4d-%4d  %-6s  %s" % (s.name, s.frame_start, s.frame_end, st.sky_at(s.frame_start),
                                          ", ".join(sorted(st.in_shot.get(s.name, ())))))
    from films import sixseconds as F
    if F.BROKEN:
        print("[sixseconds_shots] !!! built as stand-ins: %s" % ", ".join(F.BROKEN))
        return 1
    return 0


def cmd_render(args):
    """Render chosen shots (see the module docstring)."""
    from PIL import Image

    from engine import post
    nar, rows = _plan()
    by = {r.name: r for r in rows}
    want = [n.strip() for n in args.shots.split(",") if n.strip()]
    frames = [int(v) for v in str(args.frame).split(",")] if args.frame is not None else None
    jobs = []
    for i, n in enumerate(want):
        r = by[n]
        f = _frame_of(r, args.at, frames[min(i, len(frames) - 1)] if frames else None)
        jobs.append((r, f))
    skies = sorted({r.sky for r, _f in jobs})
    if len(skies) != 1:
        print("[sixseconds_shots] these shots need skies %s: one sky per call" % skies)
        return 2
    ses = _session(skies[0])
    res = args.res or (540, 960)
    ses.configure(res, args.samples, args.threads, True)
    variants = [None]
    if args.move:                                   # scouting variants: other cameras for the same shots
        variants = []
        for spec in args.move.split("/"):
            pos, tgt, *rest = spec.split(":")
            variants.append((tuple(float(v) for v in pos.split(",")), tuple(float(v) for v in tgt.split(",")),
                             float(rest[0]) if rest else None))
    os.makedirs(args.dir, exist_ok=True)
    shots = {s.name: s for s in ses.film.shots}
    for r, f in jobs:
        for vi, var in enumerate(variants):
            base = "%s_%s" % (args.name or "sixseconds_shot", r.name)
            if args.frame is not None or args.at is not None:
                base += "_%d" % f
            if var is not None:
                s = shots[r.name]
                if var[2]:
                    s.lens(var[2], s._fstop)
                s.move(var[0], var[1])
                base += "_v%d" % vi
            path = os.path.join(args.dir, base + ".png")
            t = time.time()
            ses.render_frame(f, path)
            print("[sixseconds_shots] %s frame %d %s-> %s  %.1f s" % (r.name, f, "%s " % (var,) if var else "",
                                                                     path, time.time() - t))
            if args.zones:
                with Image.open(path) as im:
                    post.draw_zones(im).save(path[:-4] + "_zones.png")
    return 0


def cmd_tiles(args):
    """Sheet tiles of every shot of one sky."""
    nar, rows = _plan()
    ses = _session(args.sky)
    ses.configure((270, 480), 8, args.threads, True)
    os.makedirs(TILE_DIR, exist_ok=True)
    only = set(n.strip() for n in (args.shots or "").split(",") if n.strip())
    for r in rows:
        if only and r.name not in only:
            continue
        if r.sky != args.sky:
            continue
        f = _frame_of(r, args.at)
        path = os.path.join(TILE_DIR, "%s.png" % r.name)
        t = time.time()
        ses.render_frame(f, path)
        with open(path[:-4] + ".json", "w") as fh:
            json.dump({"frame": f, "sky": args.sky}, fh)
        print("[sixseconds_shots] tile %s frame %d  %.1f s" % (r.name, f, time.time() - t), flush=True)
    return 0


def cmd_sheet(args):
    """Put the tiles together in film order with labels, the caption of their frame and the encoder's black."""
    from PIL import Image

    from engine import captions as cap
    from engine import post
    from tools import sixseconds_timeline as TL
    nar, rows = _plan()
    caps = nar.captions(cuts=[r.frame_start for r in rows[1:]])
    fades = TL.fades(rows, nar.fps)
    tiles, labels, words, gains = [], [], [], []
    for r in rows:
        path = os.path.join(TILE_DIR, "%s.png" % r.name)
        if not os.path.exists(path):
            continue
        meta = json.load(open(path[:-4] + ".json"))
        with Image.open(path) as im:
            tiles.append(im.convert("RGB"))
        t = (meta["frame"] - 1) / float(nar.fps)
        labels.append("%s %d %s" % (r.name, meta["frame"], meta["sky"]))
        words.append(cap.caption_at(caps, t))
        gains.append(post.fade_gain(fades, t))
    out = os.path.join(ROOT, "out", "test", args.out)
    post.contact_sheet(tiles, labels, words, out, columns=args.columns, gains=gains)
    print("[sixseconds_shots] %d tiles -> %s" % (len(tiles), out))
    return 0


def main(argv):
    """Parse the command line (see the module docstring)."""
    ap = argparse.ArgumentParser(prog="tools.sixseconds_shots")
    ap.add_argument("cmd", choices=("plan", "build", "render", "tiles", "sheet"))
    ap.add_argument("--sky", default="wastes")
    ap.add_argument("--shots")
    ap.add_argument("--at", type=float)
    ap.add_argument("--frame", help="a frame number, or one per shot (comma-separated)")
    ap.add_argument("--res", type=lambda t: tuple(int(v) for v in t.lower().split("x")))
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--zones", action="store_true")
    ap.add_argument("--move", help="render: camera variants 'x,y,z:tx,ty,tz[:lens]/...' (scouting only; v0, v1 ...)")
    ap.add_argument("--name")
    ap.add_argument("--dir", default=os.path.join(ROOT, "out", "test"))
    ap.add_argument("--out", default="sixseconds_shots_sheet.png")
    ap.add_argument("--columns", type=int, default=9)
    args = ap.parse_args(argv)
    return {"plan": cmd_plan, "build": cmd_build, "render": cmd_render, "tiles": cmd_tiles,
            "sheet": cmd_sheet}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
