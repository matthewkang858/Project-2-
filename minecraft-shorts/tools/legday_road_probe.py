"""Leg Day, sequence ROAD: numbers for staging the road shots on one gold build (nothing rendered, nothing written).

    $BPY -m tools.legday_road_probe ground "x0,y0;x1,y1;..."       # ground height and top block at points
    $BPY -m tools.legday_road_probe grid X0 X1 Y0 Y1                 # ground height map (one row per y)
    $BPY -m tools.legday_road_probe where NAME F[,F...]              # a character's feet, yaw and eyes at frames
    $BPY -m tools.legday_road_probe runners                          # rd16: runners' feet, speed and the arrows
    $BPY -m tools.legday_road_probe steve                            # rd21: steve_rd2 feet / head yaw-pitch per 3 f
Prefix with `nice -n 12 timeout 290`. The road director's own scouting tool (films/legday_road.py).
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _session():
    import render
    return render.Session("legday", sky="gold")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    ses = _session()
    st, C = ses.result["stage"], ses.result["context"]
    v = C.v
    W = v.world
    scene = ses.scene if hasattr(ses, "scene") else None
    import bpy
    scene = scene or bpy.context.scene
    if cmd == "ground":
        for part in argv[1].split(";"):
            x, y = (float(t) for t in part.split(","))
            z = v.ground(x, y)
            top = W.block_id(int(math.floor(x)), int(math.floor(y)), int(round(z)) - 1)
            above = [W.block_id(int(math.floor(x)), int(math.floor(y)), int(round(z)) + k) for k in range(0, 3)]
            print("ground (%.2f, %.2f): z %.2f top %s above %s" % (x, y, z, top, above))
    elif cmd == "grid":
        x0, x1, y0, y1 = (int(t) for t in argv[1:5])
        print("      " + "".join("%4d" % x for x in range(x0, x1 + 1)))
        for y in range(y1, y0 - 1, -1):
            row = []
            for x in range(x0, x1 + 1):
                z = v.ground(x + 0.5, y + 0.5)
                top = W.block_id(x, y, int(round(z)))
                mark = "*" if top and top not in ("air", "cave_air") else " "
                row.append("%3d%s" % (int(round(z)), mark))
            print("%4d  %s" % (y, "".join(row)))
    elif cmd == "where":
        c = st.cast[argv[1]]
        for f in (int(t) for t in argv[2].split(",")):
            scene.frame_set(f)
            p = c.pos_at(f)
            e = c.eye_point(f) if hasattr(c, "eye_point") else None
            print("%s %d: feet (%.2f, %.2f, %.2f) yaw %.1f eyes %s" % (
                c.name, f, p.x, p.y, p.z, math.degrees(c.yaw_at(f)),
                "(%.2f, %.2f, %.2f)" % tuple(e) if e is not None else "-"))
    elif cmd == "runners":
        r = C.T["rd16_punch"]
        for n in ("steve_rd", "kai_rd", "zuri_rd"):
            c = st.cast.get(n)
            if c is None:
                continue
            line = []
            for f in range(r.frame_start, r.frame_end + 1, 3):
                p, q = c.pos_at(f), c.pos_at(f + 1)
                line.append("%d:%.2f,%.2f(%.1f)" % (f, p.x, p.y, (q - p).length * 24))
            print(n, " ".join(line))
    elif cmd == "steve":
        r = C.T["rd21_still"]
        c = st.cast["steve_rd2"]
        for f in range(r.frame_start, r.frame_end + 1, 3):
            scene.frame_set(f)
            p = c.pos_at(f)
            hy = math.degrees(c.head.rotation_euler[2])
            hp = math.degrees(c.head.rotation_euler[0])
            print("%d feet (%.2f, %.2f, %.2f) body yaw %.1f head yaw %.1f pitch %.1f" % (
                f, p.x, p.y, p.z, math.degrees(c.yaw_at(f)), hy, hp))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
