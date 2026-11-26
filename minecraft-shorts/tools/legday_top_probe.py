"""Leg Day, sequence TOP (films/legday_top.py): one build, many measurements and scouting variants of the wall-top
shots tp13 / tp14 / tp18 / tp24. The top director's own tool (nothing of the film is changed; nothing is written but
the stills asked for, into the scratchpad or --dir).

    $BPY -m tools.legday_top_probe --sky gold tp18_lever:1108 tp18_lever:1123
    $BPY -m tools.legday_top_probe --sky gold "tp18_lever:1108:-3.4,63.2,21.0>-1.0,57.0,6.0>20"
    $BPY -m tools.legday_top_probe --sky gold --render 270x480x8 "tp18_lever:1108:..."   # + a quick still
    $BPY -m tools.legday_top_probe --sky gold --state                                       # the wall's parts

For each query: the shot's own camera (as built, with its move and handheld) on FRAME, or a static variant
pos>target[>lens]; every character in the shot (eyes x / y %, head box, face px at 540x960, degrees off the lens,
the first thing between the lens and the eyes), every pillager's banner top / head, and the wall's named points:
the lever's handle tip, the dust's two ends, the twelfth piston's face, the twelfth plank, anvils 8-12 (top centre).
Prefix with `nice -n 12 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.legday_geo import _own, first_hit, head_box   # noqa: E402

SCRATCH = "/tmp/claude-0/-home-user-Project-2-/be90bb9d-3fc7-572c-941a-ff79c8b6ef48/scratchpad/top"


def wall_points(C, f):
    """Named 3D points of the wall top on frame f."""
    from mathutils import Vector
    pts = {}
    try:
        pts["lever_hand"] = Vector(C.lever.hand_point(f, 1.0))
    except Exception:
        pass
    pts["dust_south"] = Vector((-2.5, 46.5, 18.05))
    pts["dust_mid"] = Vector((-2.5, 52.5, 18.05))
    pts["dust_north"] = Vector((-2.5, 59.5, 18.05))
    pts["piston12_face"] = Vector((-1.0, 57.5, 17.5))
    pts["plank12"] = Vector((0.5, 57.5, 17.5))
    pts["plank8"] = Vector((0.5, 53.5, 17.5))
    for i in (7, 9, 11):
        pts["anvil%d_top" % (i + 1)] = Vector((0.5, 46.5 + i, 19.0))
    pts["road_foot_57"] = Vector((0.5, 57.5, 0.0))
    pts["wall_ne_corner_top"] = Vector((-1.0, 61.0, 18.0))
    pts["wall_ne_corner_foot"] = Vector((-1.0, 61.0, 0.0))
    return pts


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="tools.legday_top_probe")
    ap.add_argument("--sky", default="gold")
    ap.add_argument("--render", help="WxHxSAMPLES: also render each query (static variants without handheld)")
    ap.add_argument("--dir", default=SCRATCH)
    ap.add_argument("--name", default="tpprobe")
    ap.add_argument("--pts", help="extra points 'x,y,z;...'")
    ap.add_argument("--state", action="store_true", help="print the wall parts' state per frame of each top shot")
    ap.add_argument("queries", nargs="*", help="SHOT:FRAME[:x,y,z>tx,ty,tz[>lens[>fstop]]]")
    args = ap.parse_args(argv)

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    ses = render.Session("legday", sky=args.sky)
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = {s.name: s for s in ses.film.shots}
    if args.render:
        w, h, spp = (int(v) for v in args.render.lower().split("x"))
        ses.configure((w, h), spp, 2, True)
        os.makedirs(args.dir, exist_ok=True)

    def proj(cam, p):
        co = world_to_camera_view(scene, cam, p)
        return co.x * 100.0, (1.0 - co.y) * 100.0, co.z

    if args.state:
        for name in ("tp13_sticky", "tp14_why", "tp18_lever", "tp24_reloading"):
            s = shots[name]
            for f in range(s.frame_start, s.frame_end + 1, 4):
                p12 = C.row.pistons[11]
                print("%s %d lever %s p12 %s plank12 vis %s" % (name, f, C.lever.state_at(f), p12.look_at_frame(f),
                                                              not C.row.blocks[11].objects()[0].hide_render
                                                              if callable(getattr(C.row.blocks[11], "objects", None))
                                                              else "?"))
    for vi, q in enumerate(args.queries):
        parts = q.split(":")
        sname, f = parts[0], int(parts[1])
        s = shots[sname]
        variant = len(parts) > 2
        if variant:
            bits = parts[2].split(">")
            pos = tuple(float(v) for v in bits[0].split(","))
            tgt = tuple(float(v) for v in bits[1].split(","))
            if len(bits) > 2:
                s.lens(float(bits[2]), float(bits[3]) if len(bits) > 3 else s._fstop)
            s.move(pos, tgt)
        scene.frame_set(f)
        cam = s.camera
        scene.camera = cam
        dg = bpy.context.evaluated_depsgraph_get()
        cp = cam.matrix_world.translation.copy()
        print("\n[top] %s frame %d  camera (%.2f, %.2f, %.2f)  lens %.0f mm" % (sname, f, cp.x, cp.y, cp.z,
                                                                             cam.data.lens))
        for n in sorted(st.in_shot.get(sname, ())):
            c = st.cast.get(n)
            if c is None or not hasattr(c, "eye_point") or getattr(c, "head", None) is None:
                continue
            eye = Vector(c.eye_point(f))
            x, y, _ = proj(cam, eye)
            box = [proj(cam, p) for p in head_box(c)]
            top = min(b[1] for b in box) if box else float("nan")
            bot = max(b[1] for b in box) if box else float("nan")
            d = eye - cp
            side = d.cross(Vector((0, 0, 1)))
            side = side.normalized() * 0.25 if side.length > 1e-6 else Vector((0.25, 0, 0))
            a, b = proj(cam, eye - side), proj(cam, eye + side)
            face = abs(a[0] - b[0]) / 100.0 * 540
            hy = c.head.matrix_world.to_euler().z
            nose = Vector((math.sin(hy), -math.cos(hy), 0.0))
            to_cam = Vector((cp.x - eye.x, cp.y - eye.y, 0.0))
            off = math.degrees(math.acos(max(-1.0, min(1.0, nose.dot(to_cam.normalized()))))) if to_cam.length else 0
            extra = ""
            if hasattr(c, "banner_top"):
                try:
                    bt = Vector(c.banner_top(f))
                    bx, by, _ = proj(cam, bt)
                    extra = "  banner top x %5.1f y %5.1f" % (bx, by)
                except Exception:
                    pass
            if hasattr(c, "item_point") and getattr(c, "species", None) is None:
                try:
                    lv = Vector(C.lever.hand_point(f, 0.5))
                    hr, hl = Vector(c.item_point("right", f)), Vector(c.item_point("left", f))
                    hx, hyy, _ = proj(cam, hr)
                    extra = "  hand R (%.2f, %.2f, %.2f) x %4.1f y %4.1f to lever %.2f, L to lever %.2f" % (
                        hr.x, hr.y, hr.z, hx, hyy, (hr - lv).length, (hl - lv).length)
                except Exception as e:
                    extra = "  (hands: %s)" % e
            print("  %-18s eyes x %5.1f y %5.1f  head y %5.1f..%5.1f  face %4.0f px  off %5.1f  dist %5.2f  "
                  "feet (%.2f, %.2f, %.2f)  blocked %s%s" % (
                      n, x, y, top, bot, face, off, d.length, *tuple(c.root.matrix_world.translation),
                      first_hit(scene, dg, cp, eye, own=_own(c)) or "clear", extra))
        pts = wall_points(C, f)
        for spec in (args.pts or "").split(";"):
            if spec.strip():
                pts[spec] = Vector(tuple(float(v) for v in spec.split(",")))
        for k, p in pts.items():
            x, y, depth = proj(cam, p)
            print("  point %-22s x %5.1f y %5.1f  dist %5.2f  blocked %s" % (k, x, y, (p - cp).length,
                                                                          first_hit(scene, dg, cp, p) or "clear"))
        if args.render:
            path = os.path.join(args.dir, "%s_%s_%d_v%d.png" % (args.name, sname, f, vi))
            ses.render_frame(f, path)
            print("  -> %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
