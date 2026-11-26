"""Leg Day, sequence TOP: tools/palette_check on a still that is ALREADY rendered at final quality (540x960, 16
samples) by tools/legday_shots or tools/legday_palette, without rendering it again (one build of one sky: the scene
is probed on the still's frame, the PNG is evaluated with st.hero's heroes, as tools/legday_palette does), and the
Reels zones drawn on it (<still>_zones.png, engine.post.draw_zones) when they are missing.

    $BPY -m tools.legday_top_palette --sky gold tp13_sticky:828:out/test/legday_top_tp13_sticky_828.png

The top director's own tool. Prefix with `nice -n 12 timeout 290`.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    ap = argparse.ArgumentParser(prog="tools.legday_top_palette")
    ap.add_argument("--sky", default="gold")
    ap.add_argument("items", nargs="+", help="SHOT:FRAME:PNG")
    args = ap.parse_args(argv)
    from PIL import Image

    import render
    from engine import post
    from tools import palette_check
    from tools.legday_palette import _with_hurt
    ses = render.Session("legday", sky=args.sky)
    st = ses.result["stage"]
    ses.configure((540, 960), 16, 2, True)
    bad = 0
    for item in args.items:
        shot, f, path = item.split(":", 2)
        f = int(f)
        path = path if os.path.isabs(path) else os.path.join(ROOT, path)
        ses.scene.frame_set(f)
        rec = palette_check.probe(ses.scene)
        rep = palette_check.evaluate(rec, path, heroes=_with_hurt(st.heroes.get(shot, ())))
        palette_check.print_report("%s@%d" % (shot, f), rep)
        bad += 1 if rep["failed"] else 0
        zones = path[:-4] + "_zones.png"
        if not os.path.exists(zones):
            with Image.open(path) as im:
                post.draw_zones(im).save(zones)
            print("[legday_top_palette] zones -> %s" % zones)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
