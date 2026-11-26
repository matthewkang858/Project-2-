"""Independent technical probe of the "Two Apples" skeleton (checker's script: reads only, writes nothing).

    $BPY -m tools.check_twoapples_technical_probe under|dusk [section ...]
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    sky = argv[0] if argv else "under"
    want = set(argv[1:])
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    from tools.twoapples_geo import first_hit, _own

    ses = render.Session("twoapples", sky=sky)
    scene, st, C, nar = ses.scene, ses.result["stage"], ses.result["context"], ses.result["narration"]
    film = ses.film
    shots = {s.name: s for s in film.shots}
    rows = C.T
    print("[probe] sky", sky, "res", scene.render.resolution_x, scene.render.resolution_y,
          "samples", scene.cycles.samples, "frames", scene.frame_start, scene.frame_end,
          "film end", film.shots[-1].frame_end, "nar.frames", nar.frames)
    w = C.v.world

    def on(sec):
        return not want or sec in want

    def proj(cam, p):
        co = world_to_camera_view(scene, cam, Vector(p))
        return co.x * 100.0, (1.0 - co.y) * 100.0, co.z

    def _obs(c):
        if hasattr(c, "sprite") or hasattr(c, "copies"):
            obs = c.objects() if callable(getattr(c, "objects", None)) else c.objects
            return [o for o in obs if getattr(o, "type", "") == "MESH"]
        for a in ("head", "ob", "obj", "object"):
            o = getattr(c, a, None)
            if o is not None and hasattr(o, "hide_render"):
                return [o]
        obs = getattr(c, "objects", None)
        if callable(obs):
            obs = obs()
        if obs:
            return [o for o in obs if hasattr(o, "hide_render")]
        if hasattr(c, "hide_render"):
            return [c]
        return []

    def visible(c, f):
        obs = _obs(c)
        if not obs:
            return None
        return any(not o.hide_render for o in obs)

    # --------------------------------------------------------------- cast: identity, registration, hidden outside
    if on("cast"):
        print("\n== CAST ==")
        roots = {}
        for name, c in sorted(st.cast.items()):
            r = getattr(c, "root", c)
            if r.name in roots:
                print("  !! shared root", name, roots[r.name])
            roots[r.name] = name
        print("  cast members:", len(st.cast), sorted(st.cast))
        bad = []
        for name, c in sorted(st.cast.items()):
            sh = [s for s in film.shots if name in st.in_shot.get(s.name, ())]
            print("  %-22s shots %s" % (name, ",".join(x.name for x in sh)))
        for s in film.shots:
            for f in (s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end):
                scene.frame_set(f)
                for name, c in st.cast.items():
                    inn = name in st.in_shot.get(s.name, ())
                    if not inn and visible(c, f):
                        bad.append((name, s.name, f))
        print("  visible outside its shots:", bad[:20], "count", len(bad))

    # --------------------------------------------------------------- cameras: inside blocks, heroes, blocked
    if on("cams"):
        print("\n== CAMERAS / HEROES ==")
        for r in rows.values():
            if r.sky != sky:
                continue
            s = shots[r.name]
            frames = sorted({s.frame_start, s.frame_start + 1, s.frame_end - 3, s.frame_end}
                            | {f for _w, f in r.words})
            print("\n -- %s %d-%d" % (r.name, s.frame_start, s.frame_end))
            for f in frames:
                scene.frame_set(f)
                cam = s.camera
                scene.camera = cam
                dg = bpy.context.evaluated_depsgraph_get()
                cp = cam.matrix_world.translation.copy()
                cell = (int(math.floor(cp.x)), int(math.floor(cp.y)), int(math.floor(cp.z)))
                blk = w.get(*cell)
                word = ",".join(wd for wd, ff in r.words if ff == f)
                line = "   f%4d %-10s cam (%6.2f,%6.2f,%6.2f) in %s" % (f, word, cp.x, cp.y, cp.z,
                                                                       blk[0] if blk else "air")
                for label, obs in st.heroes.get(r.name, []):
                    pts = []
                    for ob in obs:
                        if ob is None:
                            continue
                        pts.append(ob.matrix_world.translation.copy())
                    if not pts:
                        continue
                    hidden = all(ob.hide_render for ob in obs if ob is not None)
                    c = sum(pts, Vector()) / len(pts)
                    x, y, z = proj(cam, c)
                    hit = first_hit(scene, dg, cp, c, own={o.name for o in obs if o is not None} |
                                    {ch.name for o in obs if o is not None for ch in o.children_recursive})
                    flag = "" if (8 <= x <= 82 and 14 <= y <= 60 and z > 0) else " OUT"
                    line += " | %s x%5.1f y%5.1f%s%s blk=%s" % (label, x, y, flag, " HIDDEN" if hidden else "",
                                                                hit or "clear")
                print(line)

    # --------------------------------------------------------------- the wall, the lever, the door objects
    if on("wall"):
        print("\n== WALL ==")
        door, lever = C.ug.door, C.ug.lever
        print("  wall_log", C.wall_log)
        for f in [550, 560, 566, 570, 575, 578, 580, 582, 585, 590, 594, 602, 623, 940, 946, 948, 950, 955, 971,
                  1465, 1480, 1490, 1491, 1492, 1493, 1494, 1496, 1500, 1557]:
            scene.frame_set(f)
            obs = [o for o in bpy.data.objects if o.name.startswith(getattr(door, "name", "piston_door"))]
            locs = ["%s(%.2f,%.2f,%.2f)%s" % (o.name[-12:], o.matrix_world.translation.x, o.matrix_world.translation.y,
                                              o.matrix_world.translation.z, "H" if o.hide_render else "")
                    for o in obs[:4]]
            print("  f%4d open=%s  %s" % (f, door.is_open(f), " ".join(locs)))
        print("  door attrs:", [a for a in dir(door) if not a.startswith("__")][:40])
        print("  lever attrs:", [a for a in dir(lever) if not a.startswith("__")][:40])

    # --------------------------------------------------------------- see-through keys
    if on("see"):
        print("\n== SEE-THROUGH ==")
        from engine import shots as SH
        for cut, obs in sorted(C.v.cutaways.items()):
            if not obs:
                continue
            ob = obs[0]
            keys = []
            for fc in SH.fcurves_of(ob):
                if fc.data_path in ("visible_camera", "hide_render"):
                    keys.append((fc.data_path, [(int(k.co[0]), int(k.co[1])) for k in fc.keyframe_points]))
            print("  %-16s %s" % (cut, keys))

    # --------------------------------------------------------------- moves: positions of key actors over frames
    if on("moves"):
        print("\n== MOVES ==")

        def track(name, frames, extra=""):
            c = st.cast.get(name)
            if c is None:
                print("  no", name)
                return
            out = []
            for f in frames:
                scene.frame_set(f)
                p = c.root.matrix_world.translation
                hz = c.head.matrix_world.translation.z if getattr(c, "head", None) else float("nan")
                out.append("f%d(%.2f,%.2f,%.2f h%.2f%s)" % (f, p.x, p.y, p.z, hz, "" if visible(c, f) else " H"))
            print("  %-16s %s" % (name, " ".join(out)))

        r = rows
        if sky == "dusk":
            track("steve_sq01", [1, 10, 20, 31, 40, 48, 55, 63, 70, 80, 83])
            track("dad_sq", [130, 138, 150, 167, 180, 187, 190, 193, 197, 200, 215, 228])
            track("steve_sq03", [138, 167, 193, 228])
            track("child_ev", [225, 229, 235, 240, 251, 256, 261, 275, 292, 293, 320, 350])
            track("child_ev6", [351, 360, 368, 377, 386, 401])
            track("kid_sq20a", [1210, 1220, 1230, 1240, 1247, 1260, 1277])
            track("kid_sq20b", [1210, 1220, 1230, 1240, 1247, 1260, 1277])
            track("grownup_sq20", [1210, 1230, 1245, 1260, 1270, 1277])
        else:
            track("steve_bx08", [490, 495, 502, 516, 534, 550])
            track("zchild_bx", [490, 516, 550])
            track("steve_tu09", [551, 560, 566, 570, 590, 623])
            track("dad_tu", [624, 655, 656, 657, 660, 676, 682, 690, 726, 742, 743, 744, 780])
            track("zdad_tu", [726, 742, 743, 744, 750, 780])
            track("zdad_cu", [781, 800, 806, 868, 917, 972, 1023, 1030, 1031, 1032, 1103])
            track("dad_cu", [1023, 1030, 1031, 1032, 1103, 1104, 1154, 1155, 1209])
            track("steve_cu16", [966, 972, 975, 980, 985, 990, 995, 1000, 1010, 1022])
            track("steve_cu18", [1104, 1120, 1140, 1154])
            track("steve_bx21", [1278, 1284, 1292, 1300, 1318])
            track("child_bx", [1319, 1340, 1359, 1381, 1401])
            track("zombie_bx22", [1309, 1319, 1325, 1330, 1340, 1359, 1381, 1401])
            track("zombie_bx23", [1402, 1425, 1430, 1440, 1449, 1450, 1455, 1464])
            track("rotten_flesh_bx", [1402, 1448, 1449, 1450, 1460, 1464]) if False else None
            for nm in ("rotten_flesh_bx", "ug_lever"):
                it = st.cast.get(nm)
                vv = []
                for f in (1402, 1448, 1449, 1450, 1460, 1464, 1465):
                    scene.frame_set(f)
                    vv.append("f%d %s" % (f, visible(it, f)))
                print("  %s visible: %s (attrs %s)" % (nm, vv, [a for a in dir(it) if not a.startswith("_")][:25]))
            track("zchild_bx24", [1465, 1490, 1493, 1500, 1505, 1510, 1520, 1557])
            track("dad_bx", [1465, 1540])
            # Steve's head top vs the aisle's ceiling in cu16 (ceiling underside at F + 3 = -7)
            c = st.cast["steve_cu16"]
            tops = []
            for f in range(972, 1023):
                scene.frame_set(f)
                zmax = max((ob.matrix_world @ Vector(co)).z for ob in [c.head] + list(c.head.children_recursive)
                           if ob.type == "MESH" for co in ob.bound_box)
                tops.append((f, round(zmax, 3)))
            over = [t for t in tops if t[1] > -7.0]
            print("  cu16 Steve head top max %.3f; frames over the ceiling (-7): %s" % (max(t[1] for t in tops), over))
    # --------------------------------------------------------------- bodies inside blocks
    if on("bodies"):
        print("\n== BODIES IN BLOCKS ==")
        door_cells = {(14, -15, -10), (14, -15, -9)}
        for r in rows.values():
            if r.sky != sky:
                continue
            s = shots[r.name]
            hits = {}
            for f in range(s.frame_start, s.frame_end + 1, 2):
                scene.frame_set(f)
                for name in st.in_shot.get(r.name, ()):
                    c = st.cast[name]
                    if not hasattr(c, "height") or not hasattr(c, "root"):
                        continue
                    if not visible(c, f) and not name.startswith("zombie_bx23"):
                        continue
                    p = c.root.matrix_world.translation
                    hw = 0.15 if getattr(c, "child", False) or "zchild" in name or "kid" in name else 0.28
                    for dz in (0.15, c.height * 0.5, c.height - 0.1):
                        for dx, dy in ((0, 0), (hw, 0), (-hw, 0), (0, hw), (0, -hw)):
                            q = (p.x + dx, p.y + dy, p.z + dz)
                            cell = (int(math.floor(q[0])), int(math.floor(q[1])), int(math.floor(q[2])))
                            if cell in door_cells and C.ug.door.is_open(f):
                                continue
                            if w.is_solid(*cell):
                                b = w.get(*cell)
                                hits.setdefault(name, []).append((f, round(dz, 2), cell, b[0] if b else None))
            for name, hh in hits.items():
                fr = sorted({h[0] for h in hh})
                print("  %-12s %-16s %d frames in blocks (%d..%d): e.g. %s" % (r.name, name, len(fr), fr[0], fr[-1],
                                                                             hh[:3]))
        for q in [(2, -13, -10), (2, -13, -9), (2, -12, -10), (3, -12, -10), (2, -12, -7), (3, -13, -10)]:
            print("  block", q, w.get(*q), "solid", w.is_solid(*q))
        for shot in ("cu13_potion", "cu16_shakes", "cu19_behind", "cu14_apple", "bx24_kept"):
            scene.frame_set(shots[shot].frame_start + 3)
            print("  lever visible in %s: %s" % (shot, visible(C.ug.lever, 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
