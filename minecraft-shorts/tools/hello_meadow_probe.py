"""The Hello, sequence MEADOW: the meadow director's own probe (no render, nothing written).

    $BPY -m tools.hello_meadow_probe info                 # anchors, set cameras, paths, set pieces (one build)
    $BPY -m tools.hello_meadow_probe blocks X0 Y0 X1 Y1   # top block and ground height of every column there
    $BPY -m tools.hello_meadow_probe keys SHOT            # per frame: every cast member's feet, yaw, head yaw /
                                                          #   pitch, eye point, and the camera (one build)
Prefix with `nice -n 5 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _session(sky):
    import render
    return render.Session("hello", sky=sky)


def cmd_info(args):
    ses = _session(args.sky)
    C = ses.result["context"]
    v = C.v
    print("ANCHORS")
    for k in sorted(C.A):
        if any(w in k for w in ("forest", "float", "bare", "pyramid", "exit", "meadow", "gate")):
            print("  %-24s %s" % (k, tuple(round(c, 3) for c in C.A[k])))
    print("SET CAMERAS")
    for k, c in C.set["cameras"].items():
        print("  %-10s %s" % (k, c))
    print("PATHS")
    for k in ("road_to_forest", "pyramid_round"):
        print("  %s: %s" % (k, [tuple(round(c, 2) for c in p) for p in v.paths[k]]))
    for k in ("floating", "bare", "pyramid"):
        d = C.set.get(k)
        if isinstance(d, dict):
            print("SET %s: %s" % (k, {kk: vv for kk, vv in d.items() if kk not in ("blocks",)}))
    return 0


def cmd_blocks(args):
    ses = _session(args.sky)
    C = ses.result["context"]
    w = C.v.world
    x0, y0, x1, y1 = [int(a) for a in args.rest]
    for y in range(y1, y0 - 1, -1):
        row = []
        for x in range(x0, x1 + 1):
            top, zt = None, None
            for z in range(12, -3, -1):
                b = w.block_id(x, y, z)
                if b and b not in ("air", "cave_air"):
                    top, zt = b, z
                    break
            g = C.v.ground(x + 0.5, y + 0.5)
            row.append("%s%d" % ((top or "-")[:6], zt if zt is not None else -9))
        print("y %4d  %s" % (y, " ".join("%-9s" % r for r in row)))
    print("columns x %d..%d" % (x0, x1))
    return 0


def cmd_keys(args):
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    ses = _session(args.sky)
    scene, st = ses.scene, ses.result["stage"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shot = next(s for s in ses.film.shots if s.name == args.rest[0])
    step = int(args.rest[1]) if len(args.rest) > 1 else 4
    names = sorted(st.in_shot.get(shot.name, ()))
    for f in list(range(shot.frame_start, shot.frame_end + 1, step)) + [shot.frame_end]:
        scene.frame_set(f)
        cam = shot.camera
        cp = cam.matrix_world.translation
        line = ["f %4d cam (%.2f %.2f %.2f)" % (f, cp.x, cp.y, cp.z)]
        for n in names:
            c = st.cast.get(n)
            if c is None or not hasattr(c, "eye_point"):
                continue
            p = c.root.matrix_world.translation
            hy = c.head.matrix_world.to_euler()
            e = c.head.matrix_world.translation
            co = world_to_camera_view(scene, cam, Vector(c.eye_point(f)))
            line.append("%s (%.2f %.2f %.2f) yaw %4.0f head %4.0f/%3.0f eye %4.1f%%,%4.1f%%" % (
                n, p.x, p.y, p.z, math.degrees(c.root.matrix_world.to_euler().z), math.degrees(hy.z),
                math.degrees(hy.x), co.x * 100, (1 - co.y) * 100))
        print("  ".join(line))
    return 0


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="tools.hello_meadow_probe")
    ap.add_argument("cmd", choices=("info", "blocks", "keys"))
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--sky", default="meadow")
    args = ap.parse_args(argv)
    return {"info": cmd_info, "blocks": cmd_blocks, "keys": cmd_keys}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
