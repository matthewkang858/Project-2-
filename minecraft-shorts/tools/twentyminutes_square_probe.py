"""Twenty Minutes, sequence SQUARE: measure the square's shots in the BUILT film, frame by frame, without a render
(the square director's probe; one strict build of the one sky).

    $BPY -m tools.twentyminutes_square_probe sq01_afraid[:STEP] sq02_imnot:2 ...   # default step 4
    $BPY -m tools.twentyminutes_square_probe sq01_afraid --who baby_sq,steve_sq

Per frame and cast member in the shot (st.in_shot): visible or not, eyes x / y (% of the 540x960 frame, y from the
top), the head's box, `off3` = the angle between where the head's nose REALLY points (the evaluated head: pitch,
clamp and all) and the lens (0 = facing it; past about 80 a villager's face is a blank box), `off` = the same flat
(yaw only), and for a player his LEGS' box (sq02: the legs that cross the foreground). Then the camera's heading /
pitch and focus distance, and the gaps that matter for the shot (sq03: the baby's feet to Steve's feet).
Nothing is written. Prefix with `nice -n 12 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="tools.twentyminutes_square_probe")
    ap.add_argument("queries", nargs="+", help="SHOT[:STEP] or SHOT@F1,F2,...")
    ap.add_argument("--who", help="cast names (default: everybody in the shot)")
    args = ap.parse_args(argv)
    os.environ["TWENTYMINUTES_STRICT"] = "1"

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    ses = render.Session("twentyminutes")
    scene, st = ses.scene, ses.result["stage"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = {s.name: s for s in ses.film.shots}
    C = ses.result["context"]
    print("[sq] memo: %s" % {k: v for k, v in C.memo.items() if k.startswith("sq")})

    def proj(cam, p):
        co = world_to_camera_view(scene, cam, Vector(p))
        return co.x * 100.0, (1.0 - co.y) * 100.0, co.z

    def box(cam, obs):
        pts = []
        for ob in obs:
            for o in [ob] + list(ob.children_recursive):
                if o.type == "MESH" and not o.hide_render:
                    pts += [o.matrix_world @ Vector(cn) for cn in o.bound_box]
        if not pts:
            return None
        pr = [proj(cam, p) for p in pts]
        return (min(p[0] for p in pr), max(p[0] for p in pr), min(p[1] for p in pr), max(p[1] for p in pr))

    def visible(c):
        obs = c.objects() if callable(getattr(c, "objects", None)) else []
        meshes = [o for o in obs if o.type == "MESH"]
        return any(not o.hide_render for o in meshes) if meshes else None

    for q in args.queries:
        frames = None
        if "@" in q:
            name, fl = q.split("@")
            frames = [int(v) for v in fl.split(",")]
            step = 1
        else:
            name, _, step = q.partition(":")
            step = int(step or 4)
        s = shots[name]
        if frames is None:
            frames = list(range(s.frame_start, s.frame_end + 1, step))
            if frames[-1] != s.frame_end:
                frames.append(s.frame_end)
        names = [n.strip() for n in args.who.split(",")] if args.who else sorted(st.in_shot.get(name, ()))
        print("\n[sq] %s %d-%d  cast: %s" % (name, s.frame_start, s.frame_end, ", ".join(names)))
        for f in frames:
            scene.frame_set(f)
            cam = s.camera
            scene.camera = cam
            m = cam.matrix_world
            cp = m.translation.copy()
            d = m.to_3x3() @ Vector((0.0, 0.0, -1.0))
            fd = cam.data.dof.focus_distance if cam.data.dof.focus_object is None else \
                (cam.data.dof.focus_object.matrix_world.translation - cp).length
            print("  f %4d  cam (%.2f, %.2f, %.2f) heading %.1f pitch %+.1f  focus %.2f" % (
                f, cp.x, cp.y, cp.z, math.degrees(math.atan2(d.y, d.x)),
                math.degrees(math.asin(max(-1.0, min(1.0, d.z)))), fd))
            for n in names:
                c = st.cast.get(n)
                if c is None or not hasattr(c, "head") or c.head is None:
                    continue
                if not visible(c):
                    print("      %-14s hidden" % n)
                    continue
                eye = Vector(c.eye_point(f))
                x, y, _z = proj(cam, eye)
                hb = box(cam, [c.head])
                hm = c.head.matrix_world
                nose = hm.to_3x3() @ Vector((0.0, -1.0, 0.0))
                to_cam = (cp - hm.translation)
                off3 = math.degrees(nose.angle(to_cam)) if to_cam.length > 1e-6 else 0.0
                n2, t2 = Vector((nose.x, nose.y)), Vector((to_cam.x, to_cam.y))
                off = math.degrees(n2.angle(t2)) if n2.length > 1e-6 and t2.length > 1e-6 else 0.0
                pitch = math.degrees(math.asin(max(-1.0, min(1.0, nose.z / max(nose.length, 1e-9)))))
                p = c.pos_at(f)
                line = "      %-14s eyes %5.1f/%5.1f  head x %5.1f..%5.1f y %5.1f..%5.1f  off3 %5.1f off %5.1f " \
                       "pitch %+5.1f  feet (%.2f, %.2f, %.2f) dist %.2f" % (
                           n, x, y, hb[0], hb[1], hb[2], hb[3], off3, off, pitch, p.x, p.y, p.z, (eye - cp).length)
                legs = [getattr(c, k, None) for k in ("leg_l", "leg_r")]
                legs = [o for o in legs if o is not None]
                if n.startswith("steve") and legs:
                    lb = box(cam, legs)
                    bb = box(cam, [c.root])
                    if lb:
                        line += "  legs x %.0f..%.0f y %.0f..%.0f" % lb
                    if bb:
                        line += "  all x %.0f..%.0f y %.0f..%.0f" % bb
                print(line)
            if name.startswith("sq03"):
                b, sv = st.cast.get("baby_sq"), st.cast.get("steve_sq")
                for bn in [k for k in names if k.startswith("baby")]:
                    b = st.cast[bn]
                    if b is not None and sv is not None:
                        pb, ps = b.pos_at(f), sv.pos_at(f)
                        print("      gap %s-steve %.2f (centres; feet clear = minus 0.55)" % (
                            bn, math.hypot(pb.x - ps.x, pb.y - ps.y)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
