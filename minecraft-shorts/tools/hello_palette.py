"""The Hello: tools/palette_check on single frames at final quality (540x960, 16 samples), one build of one sky.

    $BPY -m tools.hello_palette --sky gold 195 226            # renders out/test/hello_pal_<shot>_<frame>.png and
                                                             # prints palette_check's report (heroes = st.hero's)
Every frame given must be filmed under the sky named (render.py's rule). Prefix with `nice -n 5 timeout 290`.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    """See the module docstring."""
    ap = argparse.ArgumentParser(prog="tools.hello_palette")
    ap.add_argument("--sky", default="gold")
    ap.add_argument("frames", nargs="+", type=int)
    args = ap.parse_args(argv)
    import render
    from tools import palette_check
    ses = render.Session("hello", sky=args.sky)
    st = ses.result["stage"]
    ses.configure((540, 960), 16, 2, True)
    bad = 0
    for f in args.frames:
        shot = next(s for s in ses.film.shots if s.frame_start <= f <= s.frame_end)
        path = os.path.join(ROOT, "out", "test", "hello_pal_%s_%d.png" % (shot.name, f))
        ses.render_frame(f, path)
        rec = palette_check.probe(ses.scene)
        rep = palette_check.evaluate(rec, path, heroes=st.heroes.get(shot.name, ()))
        palette_check.print_report("%s@%d" % (shot.name, f), rep)
        bad += 1 if rep["failed"] else 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
