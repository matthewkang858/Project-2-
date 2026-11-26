"""The Crammys: measure a frame without rendering it: where every head lands in the picture, how big the face is,
which way it faces the lens, and what (if anything) stands between the lens and it. One build of one sky.

    $BPY -m tools.crammys_geo --sky night md13_shot:600 fn23_kai:1400
    $BPY -m tools.crammys_geo --sky night "md13_shot:600:8.19,41.16,1.05>5.0,40.0,1.35>45"   # another camera (pos>target>lens)
    $BPY -m tools.crammys_geo --sky night md12_middle:500 --spots "5.0,40.0;4.6,39.0"    # candidate standing places:
                                                       # visibility of knees / chest / eyes of a figure standing there
    $BPY -m tools.crammys_geo --sky night jb20_eleven:1100 --pts "-6.5,0.5,2.02"            # any 3D points (the slot)
Columns: x / y in % of the frame (y from the top, as the Reels zones), the head's box (top..bottom), the face width
in pixels at 540x960 (a player's face is half a block wide (a creeper's and a skeleton's too: the same 8-pixel head)), `off` = degrees between the body's nose direction and the lens (0 = facing it, 90 = profile,
180 = from behind), `blocked` = the first rendered object on the line from the lens to the eyes ("clear" = none;
the character's own meshes are looked through: the eye point lies inside its own head).
Mobs (zombie, creeper, skeleton) are listed with players; dropped items and particles are not (use --pts).
Nothing is written. Prefix with `nice -n 15 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def first_hit(scene, dg, a, b, own=()):
    """Name of the first rendered (camera-visible) object between a and b, or None when the line is clear. Objects
    named in `own` (the measured character's own meshes: its head holds the eye point) are looked through."""
    d = b - a
    length = d.length
    d.normalize()
    o, gone = a.copy(), 0.0
    for _ in range(60):
        hit, loc, _n, _i, ob, _m = scene.ray_cast(dg, o, d, distance=length - gone - 0.04)
        if not hit:
            return None
        orig = ob.original if hasattr(ob, "original") else ob
        if (orig.hide_render or not orig.visible_camera or "glass" in orig.name      # (glass: looked through)
                or orig.name in own):
            step = (loc - o).length + 0.01
            o = loc + d * 0.01
            gone += step
            continue
        return "%s@%.2f" % (orig.name.replace("village_block_", ""), (loc - a).length)
    return "?"


def _own(c):
    """Names of every object of a character (its rig parts and what hangs on them): the eye point lies inside its
    own head, so the first version reported every face as 'blocked' by its own head (the technical review)."""
    obs = set()
    try:
        for ob in (c.objects() if callable(getattr(c, "objects", None)) else c.objects):
            obs.add(ob.name)
            obs.update(ch.name for ch in ob.children_recursive)
    except Exception:
        pass
    root = getattr(c, "root", None)
    if root is not None:
        obs.add(root.name)
        obs.update(ch.name for ch in root.children_recursive)
    return obs


def head_box(c):
    """World-space bounding box corners of a character's head (its meshes)."""
    from mathutils import Vector
    pts = []
    obs = [c.head] + list(c.head.children_recursive)
    for ob in obs:
        if ob.type != "MESH" or ob.hide_render:
            continue
        for corner in ob.bound_box:
            pts.append(ob.matrix_world @ Vector(corner))
    return pts


def main(argv):
    """See the module docstring."""
    import argparse
    ap = argparse.ArgumentParser(prog="tools.crammys_geo")
    ap.add_argument("--sky", default="gold")
    ap.add_argument("--who", help="cast names (default: everybody in the shot)")
    ap.add_argument("--pts", help="extra 3D points 'x,y,z;x,y,z'")
    ap.add_argument("--spots", help="candidate standing places 'x,y;x,y' (a figure 1.8 tall)")
    ap.add_argument("--through", help="points 'x,y,z;...' (a window): what the lens sees before and beyond each")
    ap.add_argument("queries", nargs="+", help="SHOT:FRAME[:x,y,z>tx,ty,tz[>lens]]")
    args = ap.parse_args(argv)

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    ses = render.Session("crammys", sky=args.sky)
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = {s.name: s for s in ses.film.shots}

    def proj(cam, p):
        co = world_to_camera_view(scene, cam, p)
        return co.x * 100.0, (1.0 - co.y) * 100.0, co.z

    for q in args.queries:
        parts = q.split(":")
        sname, f = parts[0], int(parts[1])
        s = shots[sname]
        if len(parts) > 2:
            bits = parts[2].split(">")
            pos = tuple(float(v) for v in bits[0].split(","))
            tgt = tuple(float(v) for v in bits[1].split(","))
            if len(bits) > 2:
                s.lens(float(bits[2]), s._fstop)
            s.move(pos, tgt)
        scene.frame_set(f)
        cam = s.camera
        scene.camera = cam
        dg = bpy.context.evaluated_depsgraph_get()
        cp = cam.matrix_world.translation.copy()
        print("\n[geo] %s frame %d  sky %s  camera (%.2f, %.2f, %.2f)  lens %.0f mm" % (
            sname, f, st.sky_at(f), cp.x, cp.y, cp.z, cam.data.lens))
        names = [n.strip() for n in args.who.split(",")] if args.who else sorted(st.in_shot.get(sname, ()))
        for n in names:
            c = st.cast.get(n)
            if c is None or not hasattr(c, "eye_point") or not hasattr(c, "head") or c.head is None:
                continue
            eye = Vector(c.eye_point(f))
            x, y, depth = proj(cam, eye)
            box = [proj(cam, p) for p in head_box(c)]
            top = min(b[1] for b in box) if box else float("nan")
            bot = max(b[1] for b in box) if box else float("nan")
            xl = min(b[0] for b in box) if box else float("nan")
            xr = max(b[0] for b in box) if box else float("nan")
            d = eye - cp
            # half the face's width: an adult's (villager or player) head is 8 game pixels = 0.5 block wide, a baby
            # villager's half that (Character.child); the first version measured every face as an adult's
            half = 0.125 if getattr(c, "child", False) else 0.25
            side = d.cross(Vector((0, 0, 1)))
            side = side.normalized() * half if side.length > 1e-6 else Vector((half, 0, 0))
            a, b = proj(cam, eye - side), proj(cam, eye + side)
            face = abs(a[0] - b[0]) / 100.0 * 540
            yaw = c.root.matrix_world.to_euler().z
            hy = c.head.matrix_world.to_euler().z
            nose = Vector((math.sin(hy), -math.cos(hy), 0.0))
            to_cam = Vector((cp.x - eye.x, cp.y - eye.y, 0.0))
            off = math.degrees(math.acos(max(-1.0, min(1.0, nose.dot(to_cam.normalized()))))) if to_cam.length else 0
            print("  %-18s eyes x %5.1f y %5.1f  head x %5.1f..%5.1f y %5.1f..%5.1f  face %4.0f px  off %5.1f  "
                  "dist %5.2f  blocked %s" % (n, x, y, xl, xr, top, bot, face, off, d.length,
                                              first_hit(scene, dg, cp, eye, own=_own(c)) or "clear"))
        for spec in (args.pts or "").split(";"):
            if not spec.strip():
                continue
            p = Vector(tuple(float(v) for v in spec.split(",")))
            x, y, depth = proj(cam, p)
            print("  point %-22s x %5.1f y %5.1f  dist %5.2f  blocked %s" % (spec, x, y, (p - cp).length,
                                                                          first_hit(scene, dg, cp, p)))
        for spec in (args.through or "").split(";"):
            if not spec.strip():
                continue
            p = Vector(tuple(float(v) for v in spec.split(",")))
            x, y, _ = proj(cam, p)
            far = cp + (p - cp).normalized() * 200.0
            print("  through %-20s x %5.1f y %5.1f  before it: %s  beyond it: %s" % (
                spec, x, y, first_hit(scene, dg, cp, p), first_hit(scene, dg, p + (p - cp).normalized() * 0.3, far)
                or "sky"))
        for spec in (args.spots or "").split(";"):
            if not spec.strip():
                continue
            g = C.stand(tuple(float(v) for v in spec.split(",")))
            res = []
            for dz, label in ((0.5, "knees"), (1.2, "chest"), (1.62, "eyes")):
                p = Vector((g[0], g[1], g[2] + dz))
                x, y, _ = proj(cam, p)
                res.append("%s x %4.1f y %4.1f %s" % (label, x, y, first_hit(scene, dg, cp, p) or "clear"))
            print("  spot (%5.2f, %5.2f) ground %.2f  %s" % (g[0], g[1], g[2], " | ".join(res)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
