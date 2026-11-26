"""The Crammys, road sequence: a top-down character map of the crammys village (films/crammys_set.py built in) for a
box, with the anchors, doors and lights inside it. No rendering, no film build (the set only).

    $BPY -m tools.crammys_road_map [x0 y0 x1 y1]          (default: the lane and the exit gate, -10 5 8 30)

Legend as tools/music_scout: . path , grass ' tuft C cobble P planks L log f fence * lantern t torch D door
s stairs r poppy; a digit = the height of the highest block above the ground (2-9), # higher.
"""
import sys

from engine import quick
from films import crammys_set as CS
from tools.music_scout import CODES


def main(argv):
    box = [int(a) for a in argv[:4]] if len(argv) >= 4 else [-10, 5, 8, 30]
    x0, y0, x1, y1 = box
    scene = quick.reset()
    quick.setup(scene)
    v = CS.build_set(scene)
    w = v.world
    for y in range(y1, y0 - 1, -1):
        row = []
        for x in range(x0, x1 + 1):
            g = int(round(v.ground(x + 0.5, y + 0.5)))
            top = None
            for z in range(14, -3, -1):
                bid = w.block_id(x, y, z)
                if bid is not None:
                    top = (z, bid)
                    break
            if top is None:
                row.append(" ")
                continue
            z, bid = top
            h = z - g + 1
            if h >= 2 and bid not in ("tall_grass",):
                row.append(str(h) if h <= 9 else "#")
            else:
                row.append(CODES.get(bid, "?"))
        print("%4d %s" % (y, "".join(row)))
    print("     " + "".join(str(abs(x) % 10) for x in range(x0, x1 + 1)))
    print("     x from %d" % x0)
    for k in sorted(v.anchors):
        p = v.anchors[k]
        if x0 <= p[0] <= x1 + 1 and y0 <= p[1] <= y1 + 1:
            print("anchor %-30s (%.2f, %.2f, %.3f) yaw %s" % (k, p[0], p[1], p[2], v.yaws.get(k)))
    for name, d in v.doors.items():
        p = d.matrix_world.translation
        if x0 <= p[0] <= x1 + 1 and y0 <= p[1] <= y1 + 1:
            print("door", name, tuple(round(c, 2) for c in p))
    for g, obs in v.lights.items():
        for ob in obs:
            p = ob.location
            if x0 <= p[0] <= x1 + 1 and y0 <= p[1] <= y1 + 1:
                print("light %-10s (%.2f, %.2f, %.2f) %.1f W" % (g, p[0], p[1], p[2], ob.data.energy))
    for name, pts in v.paths.items():
        if any(x0 <= p[0] <= x1 + 1 and y0 <= p[1] <= y1 + 1 for p in pts):
            print("path %-22s %s" % (name, " ".join("(%.1f,%.1f)" % (p[0], p[1]) for p in pts)))
    cols = {}
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(-1, 5):
                bid = w.block_id(x, y, z)
                if bid and bid not in CODES:
                    cols.setdefault(bid, []).append((x, y, z))
    for bid, where in sorted(cols.items()):
        print("other %-24s %s" % (bid, " ".join("(%d,%d,%d)" % c for c in where[:8])))


if __name__ == "__main__":
    main(sys.argv[1:])
