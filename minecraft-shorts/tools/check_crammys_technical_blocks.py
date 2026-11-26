"""Checker's probe: block lookups in the built Crammys set for what each beat needs. Prints only."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    import bpy
    from films import crammys_set as CS
    scene = bpy.context.scene
    v = CS.build_set(scene)
    W = v.world
    q = {
        "zuri note (-8,2,1) / under (-8,2,0)": [(-8, 2, 1), (-8, 2, 0)],
        "kai note (-8,1,1) / under": [(-8, 1, 1), (-8, 1, 0)],
        "sunny note (-8,-2,1) / under": [(-8, -2, 1), (-8, -2, 0)],
        "front row y -1,0,3,4,5 at z1": [(-8, -1, 1), (-8, 0, 1), (-8, 3, 1), (-8, 4, 1), (-8, 5, 1)],
        "jukebox (-7,0,1) / under": [(-7, 0, 1), (-7, 0, 0)],
        "pedestal (-9,-1,0..2)": [(-9, -1, 0), (-9, -1, 1), (-9, -1, 2)],
        "north post (-8,3,1..4)": [(-8, 3, 1), (-8, 3, 2), (-8, 3, 3), (-8, 3, 4)],
        "south post (-8,-3,1..4)": [(-8, -3, 1), (-8, -3, 2), (-8, -3, 3), (-8, -3, 4)],
        "stage floor (-6,0,0) (-5,4,0) back wall (-4,0,1)": [(-6, 0, 0), (-5, 4, 0), (-4, 0, 1), (-4, 0, 2)],
        "lane column (1,15,0..1)": [(1, 15, 0), (1, 15, 1)],
        "lane lantern post (1,17,0..3)": [(1, 17, 0), (1, 17, 1), (1, 17, 2), (1, 17, 3)],
        "house_e door cells (-5,15,1..2) (-5,15,0)": [(-5, 15, 0), (-5, 15, 1), (-5, 15, 2), (-4, 15, 0)],
        "gate posts (-3,24,0..4) (3,24,0..4)": [(-3, 24, z) for z in range(0, 5)] + [(3, 24, z) for z in range(0, 5)],
        "oak (13,44,0..6)": [(13, 44, z) for z in range(0, 7)],
        "line ground y40 x1..8 z0/-1": [(x, 40, 0) for x in range(1, 9)] + [(x, 40, -1) for x in (1, 5, 8)],
    }
    for k, cells in q.items():
        print("%-48s %s" % (k, ", ".join("%s=%s" % (c, W.block_id(*c)) for c in cells)))
    try:
        print("pumpkin props:", W.get(-8, -2, 0))
    except Exception as e:
        print("pumpkin get failed", e)
    print("ground at line:", [round(v.ground(x, 40.0), 2) for x in (1.8, 5.0, 8.2)])
    print("ground at meadow cams:", [round(v.ground(x, y), 2) for x, y in ((5.85, 34.1), (2.5, 41.8), (5.0, 27.0),
                                                                         (8.19, 41.16), (4.75, 31.0), (2.39, 38.3))])
    # plants in the low cameras' view: anything non-air at z 0 between camera and subject (meadow)
    import math
    for name, a, b in (("b10", (5.85, 34.1), (5.0, 41.0)), ("b11", (2.5, 41.8), (12.45, 44.24)),
                       ("b12", (5.0, 27.0), (5.0, 40.0)), ("b15", (4.75, 31.0), (4.75, 40.0)),
                       ("b16", (2.39, 38.3), (3.49, 40.53))):
        hits = set()
        n = int(math.dist(a, b) / 0.2)
        for i in range(n + 1):
            x = a[0] + (b[0] - a[0]) * i / n
            y = a[1] + (b[1] - a[1]) * i / n
            bid = W.block_id(int(math.floor(x)), int(math.floor(y)), 0)
            if bid:
                hits.add((int(math.floor(x)), int(math.floor(y)), bid))
        print("view %s plants/blocks at z0 on the line: %s" % (name, sorted(hits) or "none"))


main()
