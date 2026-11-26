"""Two Apples: tools/palette_check on single frames at final quality (540x960, 16 samples), one build of one sky.

    $BPY -m tools.twoapples_palette 120 160          # renders out/test/twoapples_pal_<shot>_<frame>.png and prints
                                                     # palette_check's report (heroes = st.hero's, with their red hurt
                                                     # twins: a mob in its red flash counts as visible)
The sky is the frames' own (every frame given must be filmed under the same sky: one build per call; render.py's
rule). KNOWN (films/twoapples_set.py): the check does not see the hall's baked stone (its stone rule says nothing
under the ground), and its "robe hue" rule fails on near-black robe pixels (rgb about 24, 16, 19) where no torch
reaches: read that line against the picture. Prefix with `nice -n 15 timeout 290`.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _with_hurt(heroes):
    """st.hero's heroes plus each part's red hurt twin (engine/undead.py draws a hurt mob with '<part>_hurt' twin
    meshes during the flash): tools/palette_check (frozen) looks for the heroes' own object names only."""
    out = []
    for label, obs in heroes:
        names = [getattr(o, "name", o) for o in obs]
        out.append((label, names + [n + "_hurt" for n in names]))
    return out


def main(argv):
    """See the module docstring."""
    ap = argparse.ArgumentParser(prog="tools.twoapples_palette")
    ap.add_argument("frames", nargs="+", type=int)
    args = ap.parse_args(argv)
    import render
    from engine import narration
    from films import twoapples as TA
    from tools import palette_check
    rows = TA.timeline(narration.load("twoapples", TA.NARRATION, fps=TA.FPS))
    skies = sorted({next(r.sky for r in rows if r.frame_start <= f <= r.frame_end) for f in args.frames})
    if len(skies) != 1:
        print("[twoapples_palette] these frames are filmed under skies %s: one sky per call" % skies)
        return 2
    ses = render.Session("twoapples", sky=skies[0])
    st = ses.result["stage"]
    ses.configure((540, 960), 16, 2, True)
    bad = 0
    for f in args.frames:
        shot = next(s for s in ses.film.shots if s.frame_start <= f <= s.frame_end)
        path = os.path.join(ROOT, "out", "test", "twoapples_pal_%s_%d.png" % (shot.name, f))
        ses.render_frame(f, path)
        rec = palette_check.probe(ses.scene)
        rep = palette_check.evaluate(rec, path, heroes=_with_hurt(st.heroes.get(shot.name, ())))
        palette_check.print_report("%s@%d" % (shot.name, f), rep)
        bad += 1 if rep["failed"] else 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
