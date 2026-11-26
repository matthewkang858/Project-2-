"""Two Apples: stills of single shots, one build per sky, and a contact sheet with one tile per shot.

    $BPY -m tools.twoapples_shots plan                  # shots, frames, sky of each tile (no build)
    $BPY -m tools.twoapples_shots build --sky dusk      # build ONE sky: timing, cast per shot, the wall's state, the
                                                        #   stand-ins (exit 1 if any shot is a stand-in); the strict
                                                        #   build is TWOAPPLES_STRICT=1 in front of it
    $BPY -m tools.twoapples_shots render --shots tu10_hug,tu11_hard [--at 0.5] [--frame N[,M...]] [--res 540x960]
                               [--samples 16] [--zones] [--name twoapples_scout_x] [--dir out/test]
                               [--move "x,y,z:tx,ty,tz[:lens]/..."] (camera variants v0, v1 ... for scouting; a spec
                               that starts with a minus sign must be given as --move=-3.5,...)
                               [--energy "ta_slot_strip_bx24_kept=40,..."] (scouting: set these lights' watts for
                               this call; a light of C.glow is named ta_<glow>_<shot>, of C.fill twoapples_fill_<name>)
        renders the frame at fraction `at` of each shot (or frame N; one per shot, comma-separated) in ONE build of
        the sky those shots are filmed under (shots of two skies in one call are refused: render.py's rule, a frame
        is rendered in the build of its own sky); writes <dir>/<name or twoapples_shot>_<shot>[_<frame>].png
        (+ _zones.png with --zones: the Reels UI zones, the caption band, the safe area).
    $BPY -m tools.twoapples_shots tiles --sky under [--shots a,b,...] [--at 0.5] [--res 270x480] [--tile-samples 8]
                                                        # sheet tiles of the shots of that sky ->
                                                        #   out/test/twoapples_tiles/ (a few per call: see below)
    $BPY -m tools.twoapples_shots sheet                 # the tiles, in film order, captioned and labelled ->
                                                        #   out/test/twoapples_shots_sheet.png
Each call must finish inside the command time limit: a build is about 20-50 s on a shared machine (the village, the
underground set with its baked light, the cast), a 540x960 16-sample still 40-150 s (the hall is the slowest set), a
270x480 8-sample tile 10-40 s. Prefix with `nice -n 15 timeout 290` (The Hello's final render has priority).
TWOAPPLES_STRICT=1 in the environment makes a broken shot fatal (hand in only when
`TWOAPPLES_STRICT=1 $BPY -m tools.twoapples_shots build --sky <each of your skies>` prints no "!!!" line).
Nothing here writes a meta.json or touches out/frames.
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

TILE_DIR = os.path.join(ROOT, "out", "test", "twoapples_tiles")


def _plan():
    """(Narration, [ShotInfo]) without a scene (narration + timeline only)."""
    from engine import narration
    from films import twoapples as TA
    nar = narration.load("twoapples", TA.NARRATION, fps=TA.FPS)
    return nar, TA.timeline(nar)


def _frame_of(row, at=None, frame=None):
    """The frame of a shot to render: `frame` itself, or the fraction `at` of the shot."""
    if frame is not None:
        return int(frame)
    at = 0.5 if at is None else float(at)
    return int(round(row.frame_start + at * (row.frames - 1)))


def _session(sky):
    """A render.Session of the film built with `sky`."""
    import render
    t = time.time()
    ses = render.Session("twoapples", sky=sky)
    print("[twoapples_shots] built sky %s in %.1f s" % (sky, time.time() - t))
    return ses


def cmd_plan(args):
    """Print shots with the frame and sky of their middle tile."""
    nar, rows = _plan()
    for r in rows:
        f = _frame_of(r, args.at)
        print("%-14s %-8s %4d-%4d  tile %4d  sky %s" % (r.name, r.sequence, r.frame_start, r.frame_end, f, r.sky))
    return 0


def cmd_build(args):
    """Build one sky and print who is in which shot, and the wall's state at each shot's ends."""
    ses = _session(args.sky)
    from films import twoapples as TA
    st, C = ses.result["stage"], ses.result["context"]
    for s in ses.film.shots:
        wall = "%s/%s" % ("open" if C.wall_is_open(s.frame_start) else "shut",
                          "open" if C.wall_is_open(s.frame_end) else "shut")
        print("%-14s %4d-%4d  %-5s  wall %-9s  %s" % (s.name, s.frame_start, s.frame_end, st.sky_at(s.frame_start),
                                                     wall, ", ".join(sorted(st.in_shot.get(s.name, ())))))
    print("[twoapples_shots] sky %s: %d frames; stand-ins: %s" % (args.sky, ses.film.frame_end,
                                                                  ", ".join(TA.BROKEN) or "none"))
    return 1 if TA.BROKEN else 0


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
        if not r.frame_start <= f <= r.frame_end:
            print("[twoapples_shots] frame %d is not in %s (%d-%d)" % (f, r.name, r.frame_start, r.frame_end))
            return 2
        jobs.append((r, f, r.sky))
    skies = sorted({sky for _r, _f, sky in jobs})
    if len(skies) != 1:
        print("[twoapples_shots] these shots need skies %s: one sky per call" % skies)
        return 2
    ses = _session(skies[0])
    res = args.res or (540, 960)
    ses.configure(res, args.samples, args.threads, True)
    if args.energy:                                 # scouting variants: other strengths for film-local lights
        import bpy
        for spec in args.energy.split(","):
            name, watts = spec.split("=")
            ob = bpy.data.objects.get(name.strip())
            if ob is None or ob.type != "LIGHT":
                print("[twoapples_shots] no light %r" % name)
                return 2
            ob.data.energy = float(watts)
            print("[twoapples_shots] %s set to %.1f W for this call" % (name, float(watts)))
    variants = [None]
    if args.move:                                  # scouting variants: other cameras for the same shots
        variants = []
        for spec in args.move.split("/"):
            pos, tgt, *rest = spec.split(":")
            variants.append((tuple(float(v) for v in pos.split(",")), tuple(float(v) for v in tgt.split(",")),
                             float(rest[0]) if rest else None))
    os.makedirs(args.dir, exist_ok=True)
    shots = {s.name: s for s in ses.film.shots}
    for r, f, _sky in jobs:
        for vi, var in enumerate(variants):
            base = "%s_%s" % (args.name or "twoapples_shot", r.name)
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
            print("[twoapples_shots] %s frame %d %s-> %s  %.1f s" % (r.name, f, "%s " % (var,) if var else "", path,
                                                                    time.time() - t))
            if args.zones:
                with Image.open(path) as im:
                    post.draw_zones(im).save(path[:-4] + "_zones.png")
    return 0


def cmd_tiles(args):
    """Sheet tiles of the shots of one sky."""
    nar, rows = _plan()
    ses = _session(args.sky)
    ses.configure(args.res or (270, 480), args.tile_samples, args.threads, True)
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
        print("[twoapples_shots] tile %s frame %d  %.1f s" % (r.name, f, time.time() - t), flush=True)
    return 0


def cmd_sheet(args):
    """Put the tiles together in film order with labels and the caption of their frame."""
    from PIL import Image

    from engine import captions as cap
    from engine import post
    from films import twoapples as TA
    nar, rows = _plan()
    caps = nar.captions(cuts=TA.caption_cuts(nar, rows))
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
    print("[twoapples_shots] %d tiles -> %s" % (len(tiles), out))
    return 0


def main(argv):
    """Parse the command line (see the module docstring)."""
    ap = argparse.ArgumentParser(prog="tools.twoapples_shots")
    ap.add_argument("cmd", choices=("plan", "build", "render", "tiles", "sheet"))
    ap.add_argument("--sky", default="dusk", choices=("dusk", "under"))
    ap.add_argument("--shots")
    ap.add_argument("--at", type=float)
    ap.add_argument("--frame", help="a frame number, or one per shot (comma-separated)")
    ap.add_argument("--res", type=lambda t: tuple(int(v) for v in t.lower().split("x")))
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--tile-samples", type=int, default=8, help="tiles: samples (default 8; --res sets their size)")
    ap.add_argument("--zones", action="store_true")
    ap.add_argument("--move", help="render: camera variants 'x,y,z:tx,ty,tz[:lens]/...' (scouting only; v0, v1 ...)")
    ap.add_argument("--energy", help="render: 'light=watts,...' for this call (scouting only)")
    ap.add_argument("--name")
    ap.add_argument("--dir", default=os.path.join(ROOT, "out", "test"))
    ap.add_argument("--out", default="twoapples_shots_sheet.png")
    ap.add_argument("--columns", type=int, default=8)
    args = ap.parse_args(argv)
    return {"plan": cmd_plan, "build": cmd_build, "render": cmd_render, "tiles": cmd_tiles,
            "sheet": cmd_sheet}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
