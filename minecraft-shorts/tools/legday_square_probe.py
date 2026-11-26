"""Leg Day, sequence SQUARE (films/legday_square.py): measure the square's frames without rendering them. One build.

    $BPY -m tools.legday_square_probe sq08_arms:450 sq08_arms:500          # the arms gate + heads
    $BPY -m tools.legday_square_probe sq02_reps:190 --obs iron_pickaxe_sq   # any object (cast name or Blender name)
    $BPY -m tools.legday_square_probe sq09_lifts:557 --pts "-3.5,9.5,0.5;-3.5,9.5,14"
    $BPY -m tools.legday_square_probe --sweep sq08_arms:431-519:4           # the arms gate over a span (every 4th)

For every query: the camera, each cast member of the shot (eyes x / y in % of the frame, the head's box, degrees of
the BODY and of the HEAD off the lens), the objects asked for (their projected box in %, and px at 540 x 960) and
the points asked for. sq08 also prints THE ARMS GATE: the projected width of efe_sq's left arm (the slim one, three
game pixels) and steve_sq3's right arm (four), each from the arm mesh's own vertices (the outer layer included), in
px at 540 and at 360, with their ratio and the 1/8-of-the-frame test (68 px at 540, 45 at 360).
Nothing is written. Prefix with `nice -n 12 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _box(scene, cam, obs, world_to_camera_view):
    """Projected box (x0, x1, y0, y1 in % of the frame, y from the top) of the vertices of the given mesh objects."""
    xs, ys = [], []
    for ob in obs:
        if ob.type != "MESH":
            continue
        dg_ob = ob
        mw = dg_ob.matrix_world
        for v in dg_ob.data.vertices:
            co = world_to_camera_view(scene, cam, mw @ v.co)
            xs.append(co.x * 100.0)
            ys.append((1.0 - co.y) * 100.0)
    if not xs:
        return None
    return min(xs), max(xs), min(ys), max(ys)


def _off(c, f, cp, head=False):
    """Degrees between the body's (or the head's) nose direction and the lens, in plan."""
    from mathutils import Vector
    ob = c.head if head else c.root
    yaw = ob.matrix_world.to_euler().z
    nose = Vector((math.sin(yaw), -math.cos(yaw), 0.0))
    p = c.pos_at(f)
    to_cam = Vector((cp.x - p.x, cp.y - p.y, 0.0))
    if to_cam.length < 1e-6:
        return 0.0
    return math.degrees(math.acos(max(-1.0, min(1.0, nose.dot(to_cam.normalized())))))


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="tools.legday_square_probe")
    ap.add_argument("--sky", default="gold")
    ap.add_argument("--obs", help="objects: cast names or Blender object names, comma-separated")
    ap.add_argument("--pts", help="3D points 'x,y,z;x,y,z'")
    ap.add_argument("--sweep", action="store_true", help="queries are SHOT:A-B:STEP; print one line per frame")
    ap.add_argument("queries", nargs="+")
    args = ap.parse_args(argv)

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    ses = render.Session("legday", sky=args.sky)
    scene, st = ses.scene, ses.result["stage"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = {s.name: s for s in ses.film.shots}

    def proj(cam, p):
        co = world_to_camera_view(scene, cam, Vector(p))
        return co.x * 100.0, (1.0 - co.y) * 100.0

    def arms(cam, f):
        efe, steve = st.cast["efe_sq"], st.cast["steve_sq3"]
        a = _box(scene, cam, [efe.parts["arm_l"]], world_to_camera_view)
        b = _box(scene, cam, [steve.parts["arm_r"]], world_to_camera_view)
        wa, wb = (a[1] - a[0]) * 5.4, (b[1] - b[0]) * 5.4
        cp = cam.matrix_world.translation
        return ("slim %5.1f px (x %4.1f-%4.1f, y %4.1f-%4.1f) wide %5.1f px (x %4.1f-%4.1f, y %4.1f-%4.1f)  "
                "ratio %.2f  at 360: %4.1f / %4.1f px  1/8: %s  bodies off %4.1f / %4.1f  heads off %4.1f / %4.1f"
                % (wa, a[0], a[1], a[2], a[3], wb, b[0], b[1], b[2], b[3], wb / wa, wa * 2 / 3, wb * 2 / 3,
                   "ok" if min(wa, wb) >= 67.5 else "UNDER", _off(efe, f, cp), _off(steve, f, cp),
                   _off(efe, f, cp, True), _off(steve, f, cp, True)))

    if args.sweep:
        for q in args.queries:
            sname, span, step = q.split(":")
            a, b = (int(v) for v in span.split("-"))
            s = shots[sname]
            for f in range(a, b + 1, int(step)):
                scene.frame_set(f)
                cam = s.camera
                scene.camera = cam
                line = "%s %4d  " % (sname, f)
                if sname == "sq08_arms":
                    line += arms(cam, f)
                for n in sorted(st.in_shot.get(sname, ())):
                    c = st.cast.get(n)
                    if c is None or not hasattr(c, "eye_point"):
                        continue
                    x, y = proj(cam, c.eye_point(f))
                    line += "  %s eyes %4.1f,%4.1f" % (n, x, y)
                print(line)
        return 0

    for q in args.queries:
        sname, f = q.split(":")[0], int(q.split(":")[1])
        s = shots[sname]
        scene.frame_set(f)
        cam = s.camera
        scene.camera = cam
        cp = cam.matrix_world.translation.copy()
        print("\n[probe] %s frame %d  camera (%.2f, %.2f, %.2f)  lens %.0f mm  focus %s" % (
            sname, f, cp.x, cp.y, cp.z, cam.data.lens,
            tuple(round(v, 2) for v in cam.data.dof.focus_object.matrix_world.translation)
            if cam.data.dof.focus_object else None))
        for n in sorted(st.in_shot.get(sname, ())):
            c = st.cast.get(n)
            if c is None:
                continue
            if hasattr(c, "eye_point") and getattr(c, "head", None) is not None:
                x, y = proj(cam, c.eye_point(f))
                hb = _box(scene, cam, [c.head], world_to_camera_view)
                bb = _box(scene, cam, [ob for ob in c.root.children_recursive if ob.type == "MESH"
                                       and not ob.hide_render], world_to_camera_view)
                print("  %-16s eyes x %5.1f y %5.1f  head x %5.1f..%5.1f y %5.1f..%5.1f (%3.0f px)  body x %5.1f..%5.1f "
                      "y %5.1f..%5.1f  off body %5.1f head %5.1f  dist %.2f" % (
                          n, x, y, hb[0], hb[1], hb[2], hb[3], (hb[1] - hb[0]) * 5.4, bb[0], bb[1], bb[2], bb[3],
                          _off(c, f, cp), _off(c, f, cp, True), (Vector(c.eye_point(f)) - cp).length))
        if sname == "sq08_arms":
            print("  ARMS " + arms(cam, f))
        for name in (args.obs or "").split(","):
            name = name.strip()
            if not name:
                continue
            thing = st.cast.get(name)
            obs = []
            if thing is not None:
                for attr in ("objects", "obs"):
                    v = getattr(thing, attr, None)
                    if v is not None:
                        obs = list(v() if callable(v) else v)
                        break
                if not obs and getattr(thing, "root", None) is not None:
                    obs = [thing.root] + list(thing.root.children_recursive)
                if not obs and getattr(thing, "object", None) is not None:
                    obs = [thing.object] + list(thing.object.children_recursive)
            else:
                ob = bpy.data.objects.get(name)
                obs = [ob] + list(ob.children_recursive) if ob is not None else []
            obs = [o for o in obs if o is not None]
            b = _box(scene, cam, obs, world_to_camera_view)
            if b is None:
                print("  object %-20s (no mesh found: %s)" % (name, [o.name for o in obs][:6]))
                continue
            print("  object %-20s x %5.1f..%5.1f y %5.1f..%5.1f  (%3.0f x %3.0f px at 540x960)" % (
                name, b[0], b[1], b[2], b[3], (b[1] - b[0]) * 5.4, (b[3] - b[2]) * 9.6))
        for spec in (args.pts or "").split(";"):
            if spec.strip():
                p = tuple(float(v) for v in spec.split(","))
                x, y = proj(cam, p)
                print("  point %-24s x %5.1f y %5.1f  dist %.2f" % (spec, x, y, (Vector(p) - cp).length))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
