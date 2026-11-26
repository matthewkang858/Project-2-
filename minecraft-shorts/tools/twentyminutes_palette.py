"""Twenty Minutes: tools/palette_check on single frames at final quality (540x960, 16 samples), one build.

    $BPY -m tools.twentyminutes_palette 600 1450          # renders out/test/twentyminutes_pal_<shot>_<frame>.png and
                                                             # prints palette_check's report (heroes = st.hero's,
                                                             # with their hurt twins: a mob in its red flash counts)
Every frame given must be filmed under the sky named (render.py's rule). Prefix with `nice -n 15 timeout 290`.
KNOWN (films/twentyminutes_set.py PALETTE): the set's b09 still (CAMS "platform", the golem against the low sun) fails
"stone not magenta" at G/R 0.90: the platform's stone lip in the low sun beside its gold halo, rgb(203, 183, 155), warm,
B under G, not magenta (the rule tests G/R only; legday's dusk wall top has the same). Do not "fix" it with light.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _with_hurt(heroes):
    """st.hero's heroes plus each part's red hurt twin (engine/undead.py draws a hurt mob with '<part>_hurt' twin
    meshes during the flash): tools/palette_check (frozen) looks for the heroes' own object names only, and calls a
    mob in its red flash 'not visible' (The Hello's dn02 94-105)."""
    out = []
    for label, obs in heroes:
        names = [getattr(o, "name", o) for o in obs]
        out.append((label, names + [n + "_hurt" for n in names]))
    return out


def main(argv):
    """See the module docstring."""
    ap = argparse.ArgumentParser(prog="tools.twentyminutes_palette")
    ap.add_argument("--sky", default="gold")
    ap.add_argument("frames", nargs="+", type=int)
    args = ap.parse_args(argv)
    import render
    from tools import palette_check
    ses = render.Session("twentyminutes", sky=args.sky)
    st = ses.result["stage"]
    ses.configure((540, 960), 16, 2, True)
    bad = 0
    for f in args.frames:
        shot = next(s for s in ses.film.shots if s.frame_start <= f <= s.frame_end)
        path = os.path.join(ROOT, "out", "test", "twentyminutes_pal_%s_%d.png" % (shot.name, f))
        ses.render_frame(f, path)
        rec = palette_check.probe(ses.scene)
        rep = palette_check.evaluate(rec, path, heroes=_with_hurt(st.heroes.get(shot.name, ())))
        palette_check.print_report("%s@%d" % (shot.name, f), rep)
        bad += 1 if rep["failed"] else 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
