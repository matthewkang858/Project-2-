"""Checker's probe 4 for "Twenty Minutes": blocks along every walking route of the set and the stubs (sampled every
0.1 block at knee and head height), and the top step's crack stages frame by frame. Prints only."""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

PASSABLE = (None, "air", "short_grass", "tall_grass", "poppy", "dandelion", "fern", "water", "torch", "wall_torch")


def main(argv):
    import bpy

    import render
    ses = render.Session("twentyminutes")
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    w = C.v.world

    def check(label, pts, z=None, heights=(0.3, 1.5)):
        bad = {}
        for a, b in zip(pts, pts[1:]):
            a, b = [float(v) for v in a], [float(v) for v in b]
            n = max(1, int(math.dist(a[:2], b[:2]) / 0.1))
            for i in range(n + 1):
                t = i / float(n)
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                base = (a[2] + (b[2] - a[2]) * t) if len(a) > 2 and z is None else (z if z is not None
                                                                                    else C.v.ground(x, y))
                for h in heights:
                    bid = w.block_id(int(math.floor(x)), int(math.floor(y)), int(math.floor(base + h)))
                    if bid not in PASSABLE and "door" not in str(bid) and "flower" not in str(bid):
                        bad.setdefault((int(math.floor(x)), int(math.floor(y)), int(math.floor(base + h)), bid), 0)
                        bad[(int(math.floor(x)), int(math.floor(y)), int(math.floor(base + h)), bid)] += 1
        print("%-26s %s" % (label, "clear" if not bad else "; ".join("%s at %s" % (k[3], k[:3]) for k in bad)))

    paths = C.v.paths
    for key in ("tm_steve_square", "tm_steve_past", "tower_push_square", "tm_flee_armorer", "tm_flee_shepherd"):
        if key in paths:
            check(key, paths[key])
        else:
            print("%-26s missing" % key)
    A = C.A
    p = A["chest_steve"]
    check("gm12 steve walk", [tuple(p), (p[0] + 3.0, p[1] + 2.0, p[2])])
    gs = A["gap_side"]
    check("gp15 cleric", [(gs[0], gs[1] - 1.7, gs[2]), tuple(gs)])
    ts = A["top_step"]
    check("gp15 baby run", [(ts[0], ts[1] + 0.4, ts[2]), tuple(A["gap_in"]), tuple(A["bed_side"])], heights=(0.3, 0.8))
    ga = A["gap_adult"]
    check("gp20 narrator", [(ga[0], ga[1] - 1.6, ga[2]), tuple(ga)])
    pb = A["push_baby"]
    check("sq03 baby run (approx)", [tuple(C.P("push_baby")), (pb[0] - 1.6, pb[1], 0.0)], heights=(0.3, 0.8))
    stairs = C.fm.set["stairs"]
    print("stairs:", [tuple(round(v, 2) for v in s) for s in stairs])
    for i, s in enumerate(stairs):
        below = w.block_id(int(math.floor(s[0])), int(math.floor(s[1])), int(round(s[2])) - 1)
        head = w.block_id(int(math.floor(s[0])), int(math.floor(s[1])), int(round(s[2])) + 1)
        print("  step %d at %s: under %s, head-height %s" % (i, tuple(round(v, 2) for v in s), below, head))

    # the top step's crack stages: which of its objects render, frame by frame
    obs = C.P_.top_step.objects
    obs = obs() if callable(obs) else obs
    for f in range(1340, 1366, 2):
        scene.frame_set(f)
        vis = [o.name.replace("block_dirt_-19_24_9", "B") for o in obs if o.type == "MESH" and not o.hide_render]
        print("top step f %d: %s" % (f, vis or "NOTHING"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
