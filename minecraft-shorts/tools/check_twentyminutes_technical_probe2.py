"""Checker's probe 2 for "Twenty Minutes": particles across cuts, the top step, the water at the gr16 lens, the
gr21 row's facings, the narrator's head in ce23 / gm24, the tilt's angles. Prints only."""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    import bpy
    from mathutils import Vector

    import render
    from engine import characters as ch
    ses = render.Session("twentyminutes")
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    shots = {s.name: s for s in ses.film.shots}

    def rendered(prefix, frames):
        obs = [o for o in bpy.data.objects if o.name.startswith(prefix) and o.type == "MESH"]
        out = []
        for f in frames:
            scene.frame_set(f)
            out.append("%d:%d/%d" % (f, sum(1 for o in obs if not o.hide_render and o.visible_camera), len(obs)))
        return " ".join(out)

    if "--rest" in argv:
        return rest(ses, scene, st, C, shots)
    print("poof_* rendered (gm11 -> gm12):", rendered("poof_", (690, 700, 707, 708, 709, 715, 730, 760)))
    print("fx_crumb_* rendered (gp22 -> ce23):", rendered("fx_crumb", (1355, 1360, 1380, 1399, 1400, 1402, 1406)))
    allfx = [o for o in bpy.data.objects if o.name.startswith(("fx_", "poof", "crumb", "particle"))]
    print("fx-like objects:", len(allfx), sorted({o.name.split("_")[0] + "_" + o.name.split("_")[1] for o in allfx})[:20])
    for f in (1338, 1399, 1400, 1401, 1410, 1473, 1474):
        scene.frame_set(f)
        vis = [o.name for o in allfx if o.type == "MESH" and not o.hide_render and o.visible_camera]
        print("  f %d: %d fx meshes rendered %s" % (f, len(vis), vis[:6]))

    # the top step
    ts = C.P_.top_step
    print("top_step:", type(ts).__name__, [a for a in dir(ts) if not a.startswith("_")][:30])
    obs = []
    for name in ("objects", "obj", "ob", "block"):
        v = getattr(ts, name, None)
        if v is not None:
            print("  .%s = %r" % (name, v() if callable(v) else v))
    cand = [o for o in bpy.data.objects if "dirt_-19_24_9" in o.name]
    print("  objects named *dirt_-19_24_9*:", [o.name for o in cand][:10])
    for f in (1, 772, 1256, 1337, 1338, 1350, 1354, 1355, 1356, 1360, 1399, 1400, 1542):
        scene.frame_set(f)
        print("   f %4d: %s" % (f, [(o.name[-22:], o.type, o.hide_render, o.visible_camera) for o in cand][:4]))

    # the water at the gr16 lens
    s = shots["gr16_mom"]
    for f in (955, 994, 1033):
        scene.frame_set(f)
        cp = s.camera.matrix_world.translation
        print("gr16 camera f %d: (%.4f, %.4f, %.4f)" % (f, cp.x, cp.y, cp.z))
    waters = [o for o in bpy.data.objects if "water" in o.name.lower() and o.type == "MESH"]
    for o in waters[:10]:
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        print("  water mesh %-40s x %.2f..%.2f y %.2f..%.2f z %.4f..%.4f" % (
            o.name, min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts),
            min(p.z for p in pts), max(p.z for p in pts)))
        # top surface height near the lens
        mw = o.matrix_world
        zs = [(mw @ v.co).z for v in o.data.vertices
              if abs((mw @ v.co).x + 24.7) < 0.75 and abs((mw @ v.co).y - 20.9) < 0.75]
        if zs:
            print("     vertices near the lens: z %.4f..%.4f (n %d)" % (min(zs), max(zs), len(zs)))

    # gr21: the row's facings vs the zombie
    ze = Vector(C.zombie_eye)
    for name in ("librarian_gr", "cleric_gr", "narrator_gr", "mom_gr"):
        c = st.cast[name]
        f = shots["gr21_count"].frame_start
        e = c.eye_point(f)
        d = ze - e
        bearing = math.degrees(math.atan2(d.x, -d.y))
        body = math.degrees(c.yaw_at(f))
        head = math.degrees(ch._val(c.head, "rotation_euler", 2, f))
        print("gr21 %-13s body yaw %7.1f head %6.1f -> looks %7.1f; zombie bearing %7.1f" % (
            name, body, head, body + head, bearing))

    return rest(ses, scene, st, C, shots)


def rest(ses, scene, st, C, shots):
    import math
    from mathutils import Vector
    from engine import characters as ch
    ze = Vector(C.zombie_eye)
    # ce23 / gm24: every pod character's head vs the zombie (FOUR with towers.panic)
    for sname in ("ce08_scared", "ce23_afraid", "gm09_golem", "gm24_counts"):
        s = shots[sname]
        for name in sorted(st.in_shot[sname]):
            c = st.cast[name]
            if not hasattr(c, "eye_point") or name.startswith(("golem", "zombie")):
                continue
            worst = 0.0
            for f in range(s.frame_start, s.frame_end + 1):
                e = c.eye_point(f)
                d = ze - e
                bearing = math.atan2(d.x, -d.y)
                yaw = c.yaw_at(f) + ch._val(c.head, "rotation_euler", 2, f)
                err = abs(((bearing - yaw) + math.pi) % (2 * math.pi) - math.pi)
                worst = max(worst, math.degrees(err))
            print("%s %-14s worst head error vs zombie %.1f deg" % (sname, name, worst))

    # the tilt: camera yaw / pitch at the first and last frames of sq04_tilt
    s = shots["sq04_tilt"]
    for f in (s.frame_start, s.frame_start + 10, s.frame_end):
        scene.frame_set(f)
        m = s.camera.matrix_world
        fwd = m.to_3x3() @ Vector((0, 0, -1))
        print("sq04_tilt f %d: heading %.1f deg, pitch %.1f deg" % (
            f, math.degrees(math.atan2(fwd.x, fwd.y)), math.degrees(math.asin(fwd.z))))
    s = shots["sq01_afraid"]
    scene.frame_set(s.frame_end)
    fwd = s.camera.matrix_world.to_3x3() @ Vector((0, 0, -1))
    print("sq01 last frame: heading %.1f, pitch %.1f" % (math.degrees(math.atan2(fwd.x, fwd.y)),
                                                         math.degrees(math.asin(fwd.z))))
    # the jump cut gm09 -> gm10 and gr17 / gr19
    for a, b in ((591, 592), (1091, 1143)):
        mats = []
        for f in (a, b):
            scene.frame_set(f)
            cam = ses.film.shot_at(f).camera
            mats.append((cam.matrix_world.translation.copy(), cam.matrix_world.to_3x3() @ Vector((0, 0, -1))))
        print("camera %d vs %d: moved %.4f, turned %.3f deg" % (a, b, (mats[0][0] - mats[1][0]).length,
                                                                math.degrees(mats[0][1].angle(mats[1][1]))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
