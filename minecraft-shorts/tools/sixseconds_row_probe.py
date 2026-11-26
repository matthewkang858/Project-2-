"""Six Seconds, ROW sequence (films/sixseconds_row.py): the row director's probe. No render, nothing written.

    $BPY -m tools.sixseconds_row_probe boxes rw23_nothing:1535 [--cam "x,y,z>tx,ty,tz>lens"] [--obs a,b,...]
        the frame box (x / y in % of a 540x960 frame, y from the top) of every rendered mesh whose name starts with
        one of --obs (default: the shot's cast: each character's parts grouped as head / body / held items, every
        item entity), for the shot's camera or a candidate one
    $BPY -m tools.sixseconds_row_probe ingot rw22_six:1410-1501:4 [--cam ...]
        the step ingot's spin (degrees between its broad face's normal and the lens: 0 = broad side, 90 = edge-on),
        its box in the frame and the brute's head box, frame by frame
    $BPY -m tools.sixseconds_row_probe heads rw05_family:322-378:2
        each cast member's yaw, head yaw / pitch relative to the body and degrees off the lens, frame by frame
    $BPY -m tools.sixseconds_row_probe step rw21_stare:1358-1415:8
        how many mesh vertices of each cast member's parts and held items are INSIDE the gold wall's blackstone step
        (x 8..9, y 9..16, z 0..1) and how far the deepest one reaches into it, frame by frame (the brute's golden axe)
Prefix with `nice -n 12 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _span(text):
    """'a-b[:step]' or 'a' -> list of frames."""
    bits = text.split(":")
    step = int(bits[1]) if len(bits) > 1 else 1
    if "-" in bits[0]:
        a, b = (int(v) for v in bits[0].split("-"))
        return list(range(a, b + 1, step))
    return [int(bits[0])]


def main(argv):
    """See the module docstring."""
    import argparse
    ap = argparse.ArgumentParser(prog="tools.sixseconds_row_probe")
    ap.add_argument("mode", choices=("boxes", "ingot", "heads", "step"))
    ap.add_argument("query", help="SHOT:FRAME or SHOT:A-B[:STEP]")
    ap.add_argument("--cam", help="pos>target>lens: a candidate camera instead of the shot's")
    ap.add_argument("--obs", help="object name prefixes")
    ap.add_argument("--sky", default="wastes")
    args = ap.parse_args(argv)

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    ses = render.Session("sixseconds", sky=args.sky)
    scene, st = ses.scene, ses.result["stage"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = {s.name: s for s in ses.film.shots}
    sname, rest = args.query.split(":", 1)
    s = shots[sname]
    frames = _span(rest)
    if args.cam:
        bits = args.cam.split(">")
        pos = tuple(float(v) for v in bits[0].split(","))
        tgt = tuple(float(v) for v in bits[1].split(","))
        if len(bits) > 2:
            s.lens(float(bits[2]), s._fstop)
        s.move(pos, tgt)
    cam = s.camera
    scene.camera = cam

    def proj(p):
        co = world_to_camera_view(scene, cam, p)
        return co.x * 100.0, (1.0 - co.y) * 100.0, co.z

    def box(obs):
        """Frame box of the mesh vertices IN FRONT of the lens (a part behind it is not drawn)."""
        pts = []
        for ob in obs:
            if ob.type != "MESH" or ob.hide_render:
                continue
            mw = ob.matrix_world
            for v in ob.data.vertices:
                q = proj(mw @ v.co)
                if q[2] > 0.05:
                    pts.append(q)
        if not pts:
            return None
        return (min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts))

    def fmt(b):
        return "hidden" if b is None else "x %6.1f..%6.1f  y %6.1f..%6.1f" % b

    cast = sorted(st.in_shot.get(sname, ()))
    if args.mode == "boxes":
        for f in frames:
            scene.frame_set(f)
            cp = cam.matrix_world.translation
            print("\n[row_probe] %s %d  camera (%.2f, %.2f, %.2f) lens %.0f" % (sname, f, cp.x, cp.y, cp.z,
                                                                               cam.data.lens))
            if args.obs:
                prefixes = [p.strip() for p in args.obs.split(",")]
                for ob in sorted(bpy.data.objects, key=lambda o: o.name):
                    if ob.type == "MESH" and not ob.hide_render and any(ob.name.startswith(p) for p in prefixes):
                        print("  %-40s %s" % (ob.name, fmt(box([ob]))))
                continue
            for n in cast:
                c = st.cast[n]
                obs = [o for o in bpy.data.objects if o.name.startswith(n)]
                head = [o for o in obs if "_head" in o.name or "_ear" in o.name or "_snout" in o.name]
                items = [o for o in obs if any(k in o.name for k in ("sword", "axe", "crossbow", "ingot", "item"))]
                body = [o for o in obs if o not in head and o not in items]
                print("  %-18s all %s" % (n, fmt(box(obs))))
                if hasattr(c, "head"):
                    print("  %-18s head %s" % ("", fmt(box(head))))
                    print("  %-18s body %s" % ("", fmt(box(body))))
                    for o in items:
                        b = box([o])
                        if b is not None:
                            print("  %-18s %-24s %s" % ("", o.name[len(n) + 1:], fmt(b)))
    elif args.mode == "ingot":
        it = st.cast.get("gold_ingot_rw")
        brute = st.cast.get("brute_rw")
        for f in frames:
            scene.frame_set(f)
            cp = cam.matrix_world.translation
            spin = it.spinner.matrix_world.to_3x3()
            normal = spin @ Vector((0.0, 1.0, 0.0))          # the sprite lies in the spinner's X-Z plane
            centre = it.sprite.matrix_world.translation
            to = (cp - centre)
            to_flat = Vector((to.x, to.y, 0.0)).normalized()
            n_flat = Vector((normal.x, normal.y, 0.0)).normalized()
            ang = math.degrees(math.acos(max(-1.0, min(1.0, abs(n_flat.dot(to_flat))))))
            hb = box([o for o in bpy.data.objects if o.name.startswith("brute_rw_head")])
            print("  %4d  ingot %5.1f deg off broadside  box %s   brute head %s   cam (%.3f, %.3f, %.3f)" % (
                f, ang, fmt(box(it.copies)), fmt(hb), cp.x, cp.y, cp.z))
    elif args.mode == "step":
        def inside(v):
            return 8.0 < v.x < 9.0 and 9.0 < v.y < 16.0 and 0.0 < v.z < 1.0

        for f in frames:
            scene.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            row = []
            for n in cast:
                for ob in sorted(bpy.data.objects, key=lambda o: o.name):
                    if ob.type != "MESH" or ob.hide_render or not ob.name.startswith(n + "_"):
                        continue
                    ev = ob.evaluated_get(dg)
                    me = ev.to_mesh()
                    vs = [ob.matrix_world @ v.co for v in me.vertices]
                    ev.to_mesh_clear()
                    hit = [v for v in vs if inside(v)]
                    if hit:
                        deep = max(min(v.x - 8.0, 1.0 - v.z) for v in hit)
                        row.append("%s %d/%d (%.2f in)" % (ob.name, len(hit), len(vs), deep))
            print("  %4d  %s" % (f, " | ".join(row) if row else "nothing inside the step"))
    else:
        for f in frames:
            scene.frame_set(f)
            cp = cam.matrix_world.translation
            row = []
            for n in cast:
                c = st.cast[n]
                if not hasattr(c, "head"):
                    continue
                m = c.head.matrix_world.to_3x3()
                nose = m @ Vector((0.0, -1.0, 0.0))
                flat = Vector((nose.x, nose.y, 0.0))
                pitch = math.degrees(math.atan2(nose.z, flat.length))
                eye = Vector(c.eye_point(f))
                to_cam = (cp - eye)
                off = math.degrees(math.acos(max(-1.0, min(1.0, nose.normalized().dot(to_cam.normalized())))))
                body_yaw = math.degrees(c.root.matrix_world.to_euler().z)
                head_rel = math.degrees(c.head.rotation_euler.z)
                row.append("%s yaw %6.1f head %+6.1f pitch %+5.1f off %5.1f" % (n.replace("piglin_", "p_"),
                                                                                 body_yaw, head_rel, pitch, off))
            print("  %4d  %s" % (f, " | ".join(row)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
