"""Leg Day, sequence ROAD: draw the Reels zones (engine.post.draw_zones) on stills already rendered at final quality
by tools.legday_palette (out/test/legday_pal_<shot>_<frame>.png -> ..._zones.png), so that the palette's own render
is also the evidence still with zones (one render instead of two on a shared machine). Nothing is rendered.

    $BPY -m tools.legday_road_zones out/test/legday_pal_rd15_pillagers_913.png [...]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    from PIL import Image

    from engine import post
    for path in argv:
        with Image.open(path) as im:
            out = path[:-4] + "_zones.png"
            post.draw_zones(im).save(out)
            print("[legday_road_zones] %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
