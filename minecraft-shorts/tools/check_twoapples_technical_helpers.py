"""Checker's probe: the shared helpers of films/twoapples_common.py keyed on scratch instances, items and particles.

    $BPY -m tools.check_twoapples_technical_helpers
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    import bpy
    from mathutils import Vector

    import render
    ses = render.Session("twoapples", sky="under")
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    shots = {s.name: s for s in ses.film.shots}

    def nose_off(c, f, cam):
        scene.frame_set(f)
        eye = Vector(c.eye_point(f))
        hy = c.head.matrix_world.to_euler().z
        nose = Vector((math.sin(hy), -math.cos(hy), 0.0))
        to_cam = Vector((cam[0] - eye.x, cam[1] - eye.y, 0.0)).normalized()
        return math.degrees(math.acos(max(-1.0, min(1.0, nose.dot(to_cam)))))

    print("\n== actor / twins ==")
    a1, a2, a3 = C.actor("child", "bxzz"), C.actor("child", "bxzz"), C.actor("child", "bxzy")
    print("  same tag same object:", a1 is a2, " other tag other object:", a1 is not a3,
          " roots", a1.root.name, a3.root.name)
    try:
        C.actor("child", "zz1")
        print("  !! bad prefix accepted")
    except KeyError as e:
        print("  bad prefix refused:", e)
    names = {}
    for n, c in st.cast.items():
        for ob in (c.objects() if callable(getattr(c, "objects", None)) else getattr(c, "objects", []) or []):
            if ob.name in names and names[ob.name] != n:
                print("  !! object shared", ob.name, n, names[ob.name])
            names[ob.name] = n
    print("  objects checked:", len(names))

    print("\n== cheat / to_lens (child at origin facing -Y, camera 5 south, target 90 deg east) ==")
    f = 1600
    kid = C.actor("child", "bxzz")
    kid.place(f, (0.0, 0.0, 0.0), 0.0)
    cam = (0.0, -5.0, 0.6)
    for label, fn in (("cheat 65", lambda: C.cheat(kid, f, (5.0, 0.0, 0.5), cam)),
                      ("cheat 78", lambda: C.cheat(kid, f, (5.0, 0.0, 0.5), cam, max_off=78)),
                      ("to_lens 21", lambda: C.to_lens(kid, f, (5.0, 0.0, 0.5), cam))):
        p = fn()
        kid.look_at(f, p, ease=0)
        print("  %-10s point (%.2f, %.2f, %.2f) -> head off the lens %.1f deg" % (label, p[0], p[1], p[2],
                                                                                 nose_off(kid, f, cam)))
    # target BEHIND him (the hard case): 160 deg off
    p = C.cheat(kid, f, (2.0, 5.5, 0.5), cam)
    kid.look_at(f, p, ease=0)
    print("  cheat on a target behind him: point (%.2f, %.2f) off %.1f" % (p[0], p[1], nose_off(kid, f, cam)))

    print("\n== wall helpers on frames where the state is known ==")
    print("  wall_open(600) (open already) ->", C.wall_open(600, who="probe"))
    print("  wall_shut(1000) (shut already) ->", C.wall_shut(1000, who="probe"))
    print("  wall_log", C.wall_log)
    r = C.memo.get("tu_lever")
    print("  tu09 open_wall result", r, " words lever/wall/opens", C.at(shots["tu09_lever"], "lever"),
          C.at(shots["tu09_lever"], "wall"), C.at(shots["tu09_lever"], "opens"))

    print("\n== fill ==")
    try:
        C.fill("zz_bad", (0, 0, 0), 10, [shots["bx21_small"]])
        print("  !! bad name accepted")
    except KeyError as e:
        print("  bad name refused")
    lamp = C.fill("bx_probe", (17.0, -15.0, -9.0), 10.0, [shots["bx21_small"]])
    for fr in (1, 1277, 1278, 1300, 1318, 1319):
        scene.frame_set(fr)
        print("  bx_probe f%d hidden=%s" % (fr, lamp.hide_render))
    try:
        C.fill("bx_probe", (17.0, -15.0, -9.0), 12.0, [shots["bx22_found"]])
        print("  !! a different strength accepted")
    except ValueError:
        print("  a second definition refused")

    print("\n== held items, the book, particles: hidden outside their shots ==")
    for name in ("steve_cu13", "steve_cu14", "steve_cu17", "steve_cu18", "steve_bx23"):
        c = st.cast[name]
        obs = [att.ob for att in getattr(c, "_attached", [])]
        own = [s for s in ses.film.shots if name in st.in_shot.get(s.name, ())][0]
        out = []
        for fr in (own.frame_start, (own.frame_start + own.frame_end) // 2, own.frame_end, own.frame_end + 1,
                   own.frame_start - 1, 1, 1557):
            scene.frame_set(fr)
            vis = sorted({o.name.split(".")[0][-22:] for o in obs if not o.hide_render})
            out.append("f%d:%s" % (fr, ",".join(vis) or "-"))
        print("  %-11s %s" % (name, "  ".join(out)))
    books = [o for o in bpy.data.objects if "enchanted_book" in o.name]
    for fr in (1067, 1068, 1080, 1103, 1104, 1130, 1155, 1200):
        scene.frame_set(fr)
        print("  f%d books visible: %s" % (fr, [o.name for o in books if not o.hide_render and o.type == "MESH"]))
    parts = [o for o in bpy.data.objects if any(k in o.name.lower() for k in ("swirl", "particle", "poof", "splash",
                                                                               "spell", "effect"))]
    print("  particle-like objects:", len(parts), sorted({o.name.split("_")[0] for o in parts})[:10])
    for fr in (780, 781, 800, 868, 869, 916, 917, 971, 972, 1022, 1023, 1103, 1104, 1154, 1155, 1210, 1278, 1450,
               1465):
        scene.frame_set(fr)
        vis = [o.name for o in parts if not o.hide_render and o.type == "MESH"]
        print("  f%4d %-12s visible particle meshes %3d %s" % (fr, next(s.name for s in ses.film.shots
                                                                       if s.frame_start <= fr <= s.frame_end),
                                                                len(vis), sorted({v.rsplit("_", 1)[0] for v in vis})[:4]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
