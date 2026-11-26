"""Six Seconds: engine.nether.check_still on single frames at final quality (540x960, 16 samples), one build of one
sky. (The Hello's tools/hello_palette.py, with the Nether's rules.)

    $BPY -m tools.sixseconds_palette --sky wastes 49 1452        # renders out/test/sixseconds_pal_<shot>_<frame>.png
    $BPY -m tools.sixseconds_palette --sky soul 780              # and prints the report: heroes = st.hero's of the
                                                                # shot (with their red hurt twins), gold hue 38-58 with
                                                                # s >= 0.45, the brute >= 1.5 x the blackstone where he
                                                                # is a hero, piglin skin hue 0-30 with s <= 0.62,
                                                                # Steve's shirt and trousers, heroes in the safe area
Every frame given must be filmed under the sky named (render.py's rule: tools.sixseconds_timeline lists the skies).
Exit 1 if any check fails. Prefix with `nice -n 15 timeout 290` (a still is 10-30 s on the shared machine).
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _with_hurt(heroes):
    """st.hero's heroes plus each part's red hurt twin ('<part>_hurt', drawn during a hurt flash): the check looks
    for the heroes' own object names only (tools/hello_palette.py, for the same reason)."""
    out = []
    for label, obs in heroes:
        names = [getattr(o, "name", o) for o in obs]
        out.append((label, names + [n + "_hurt" for n in names]))
    return out


def main(argv):
    """See the module docstring."""
    ap = argparse.ArgumentParser(prog="tools.sixseconds_palette")
    ap.add_argument("--sky", default="wastes")
    ap.add_argument("frames", nargs="+", type=int)
    args = ap.parse_args(argv)
    import render
    from engine import nether
    ses = render.Session("sixseconds", sky=args.sky)
    st = ses.result["stage"]
    ses.configure((540, 960), 16, 2, True)
    bad = 0
    for f in args.frames:
        shot = next(s for s in ses.film.shots if s.frame_start <= f <= s.frame_end)
        if st.sky_at(f) not in (None, args.sky):
            print("[sixseconds_palette] frame %d (%s) is filmed under sky %r: run it with --sky %s"
                  % (f, shot.name, st.sky_at(f), st.sky_at(f)))
            bad += 1
            continue
        path = os.path.join(ROOT, "out", "test", "sixseconds_pal_%s_%d.png" % (shot.name, f))
        ses.render_frame(f, path)
        rep = nether.check_still(ses.scene, path, heroes=_with_hurt(st.heroes.get(shot.name, ())), report=True)
        bad += 1 if rep["failed"] else 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
