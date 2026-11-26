"""Twenty Minutes: stills of single shots, one build of the film's sky, and a contact sheet with one tile per shot.

    $BPY -m tools.twentyminutes_shots plan                  # shots, frames, sky of each tile (no build)
    $BPY -m tools.twentyminutes_shots build                 # build the film (its one sky, "gold"): timing, cast per shot,
                                                            #   stand-ins (exit 1 if any shot is a stand-in)
    $BPY -m tools.twentyminutes_shots render --shots gm09_golem,ce23_afraid [--at 0.5] [--frame N[,M...]]
                               [--res 540x960] [--samples 16] [--zones] [--name twentyminutes_scout_x] [--dir out/test]
                               [--move "x,y,z:tx,ty,tz[:lens]/..."] (camera variants v0, v1 ... for scouting; a spec
                               that starts with a minus sign must be given as --move=-3.5,...: argparse reads a bare
                               "-3.5,..." as an option)
        renders the frame at fraction `at` of each shot (or frame N; one per shot, comma-separated) in ONE build;
        writes <dir>/<name or twentyminutes_shot>_<shot>[_<frame>].png (+ _zones.png with --zones: the Reels UI zones,
        the caption band, the safe area).
    $BPY -m tools.twentyminutes_shots tiles [--shots a,b,...] [--at 0.5] [--res 180x320] [--tile-samples 4]
                                                            # sheet tiles (default 270x480, 8 samples) ->
                                                            #   out/test/twentyminutes_tiles/ (a few per call: see below)
    $BPY -m tools.twentyminutes_shots sheet                 # the tiles, in film order, captioned and labelled ->
                                                            #   out/test/twentyminutes_shots_sheet.png
Each call must finish inside the command time limit: a build is about 15-40 s, a 540x960 16-sample still 40-150 s on a
shared machine, a 270x480 8-sample tile 10-30 s. Prefix with `nice -n 15 timeout 290` (The Hello's final render has
priority on this machine). TWENTYMINUTES_STRICT=1 in the environment makes a broken shot fatal (hand in only when
`TWENTYMINUTES_STRICT=1 $BPY -m tools.twentyminutes_shots build` prints no "!!!" line).
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

TILE_DIR = os.path.join(ROOT, "out", "test", "twentyminutes_tiles")


def _plan():
    """(Narration, [ShotInfo]) without a scene (narration + timeline only)."""
    from engine import narration
    from films import twentyminutes as TM
    nar = narration.load("twentyminutes", TM.NARRATION, fps=TM.FPS)
    return nar, TM.timeline(nar)


def _frame_of(row, at=None, frame=None):
    """The frame of a shot to render: `frame` itself, or the fraction `at` of the shot."""
    if frame is not None:
        return int(frame)
    at = 0.5 if at is None else float(at)
    return int(round(row.frame_start + at * (row.frames - 1)))


def _sky_of(row, f):
    """The sky of frame f of a shot (a sky change inside a shot: none in this film)."""
    if row.change is not None and f >= row.change:
        return row.sky_after
    return row.sky


def _session(sky):
    """A render.Session of the film built with `sky`."""
    import render
    t = time.time()
    ses = render.Session("twentyminutes", sky=sky)
    print("[twentyminutes_shots] built sky %s in %.1f s" % (sky, time.time() - t))
    return ses


def cmd_plan(args):
    """Print shots with the frame and sky of their middle tile."""
    nar, rows = _plan()
    for r in rows:
        f = _frame_of(r, args.at)
        print("%-14s %4d-%4d  tile %4d  sky %s" % (r.name, r.frame_start, r.frame_end, f, _sky_of(r, f)))
    return 0


def cmd_build(args):
    """Build one sky and print who is in which shot."""
    ses = _session(args.sky)
    st = ses.result["stage"]
    from films import twentyminutes as TM
    for s in ses.film.shots:
        print("%-15s %4d-%4d  %-5s  %s" % (s.name, s.frame_start, s.frame_end, st.sky_at(s.frame_start),
                                          ", ".join(sorted(n for n in st.in_shot.get(s.name, ())
                                                           if not n.startswith("tower_bed")))))
    print("[twentyminutes_shots] %d frames; stand-ins: %s" % (ses.film.frame_end, ", ".join(TM.BROKEN) or "none"))
    return 1 if TM.BROKEN else 0


def cmd_render(args):
    """Render chosen shots (see the module docstring)."""
    from PIL import Image

    from engine import post
    nar, rows = _plan()
    by = {r.name: r for r in rows}
    want = [n.strip() for n in args.shots.split(",") if n.strip()]
    jobs = []
    frames = [int(v) for v in str(args.frame).split(",")] if args.frame is not None else None
    for i, n in enumerate(want):
        r = by[n]
        f = _frame_of(r, args.at, frames[min(i, len(frames) - 1)] if frames else None)
        jobs.append((r, f, _sky_of(r, f)))
    skies = sorted({sky for _r, _f, sky in jobs})
    if len(skies) != 1:
        print("[twentyminutes_shots] these shots need skies %s: one sky per call" % skies)
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
    for r, f, _sky in jobs:
        for vi, var in enumerate(variants):
            base = "%s_%s" % (args.name or "twentyminutes_shot", r.name)
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
            print("[twentyminutes_shots] %s frame %d %s-> %s  %.1f s" % (r.name, f, "%s " % (var,) if var else "", path,
                                                               time.time() - t))
            if args.zones:
                with Image.open(path) as im:
                    post.draw_zones(im).save(path[:-4] + "_zones.png")
    return 0


def cmd_tiles(args):
    """Sheet tiles of every shot of one sky."""
    nar, rows = _plan()
    ses = _session(args.sky)
    ses.configure(args.res or (270, 480), args.tile_samples, args.threads, True)
    os.makedirs(TILE_DIR, exist_ok=True)
    only = set(n.strip() for n in (args.shots or "").split(",") if n.strip())
    for r in rows:
        if only and r.name not in only:
            continue
        f = _frame_of(r, args.at)
        if _sky_of(r, f) != args.sky:
            continue
        path = os.path.join(TILE_DIR, "%s.png" % r.name)
        t = time.time()
        ses.render_frame(f, path)
        with open(path[:-4] + ".json", "w") as fh:
            json.dump({"frame": f, "sky": args.sky}, fh)
        print("[twentyminutes_shots] tile %s frame %d  %.1f s" % (r.name, f, time.time() - t))
    return 0


def cmd_sheet(args):
    """Put the tiles together in film order with labels and the caption of their frame."""
    from PIL import Image

    from engine import captions as cap
    from engine import post
    nar, rows = _plan()
    from films import twentyminutes as TM
    caps = nar.captions(cuts=TM.caption_cuts(nar, rows))
    tiles, labels, words = [], [], []
    for r in rows:
        path = os.path.join(TILE_DIR, "%s.png" % r.name)
        if not os.path.exists(path):
            continue
        meta = json.load(open(path[:-4] + ".json"))
        with Image.open(path) as im:
            tiles.append(im.convert("RGB"))
        labels.append("%s %d %s" % (r.name, meta["frame"], meta["sky"]))
        words.append(cap.caption_at(caps, (meta["frame"] - 1) / float(nar.fps)))
    out = os.path.join(ROOT, "out", "test", args.out)
    post.contact_sheet(tiles, labels, words, out, columns=args.columns)
    print("[twentyminutes_shots] %d tiles -> %s" % (len(tiles), out))
    return 0


def main(argv):
    """Parse the command line (see the module docstring)."""
    ap = argparse.ArgumentParser(prog="tools.twentyminutes_shots")
    ap.add_argument("cmd", choices=("plan", "build", "render", "tiles", "sheet"))
    ap.add_argument("--sky", default="gold")
    ap.add_argument("--shots")
    ap.add_argument("--at", type=float)
    ap.add_argument("--frame", help="a frame number, or one per shot (comma-separated)")
    ap.add_argument("--res", type=lambda t: tuple(int(v) for v in t.lower().split("x")))
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--tile-samples", type=int, default=8, help="tiles: samples (default 8; --res sets their size)")
    ap.add_argument("--zones", action="store_true")
    ap.add_argument("--move", help="render: camera variants 'x,y,z:tx,ty,tz[:lens]/...' (scouting only; v0, v1 ...)")
    ap.add_argument("--name")
    ap.add_argument("--dir", default=os.path.join(ROOT, "out", "test"))
    ap.add_argument("--out", default="twentyminutes_shots_sheet.png")
    ap.add_argument("--columns", type=int, default=8)
    args = ap.parse_args(argv)
    return {"plan": cmd_plan, "build": cmd_build, "render": cmd_render, "tiles": cmd_tiles,
            "sheet": cmd_sheet}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
