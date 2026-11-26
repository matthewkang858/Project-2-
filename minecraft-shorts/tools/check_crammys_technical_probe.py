"""Independent technical check of The Crammys' skeleton (checker's probe; writes nothing but stdout).

    $BPY -m tools.check_crammys_technical_probe [--sky night] [vis|cams|events|paths|lights|all]
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def hidden(ob, f):
    """hide_render of ob at frame f from its F-curve (or its static value)."""
    from engine import shots
    for fc in shots.fcurves_of(ob):
        if fc.data_path == "hide_render":
            return fc.evaluate(f) > 0.5
    return bool(ob.hide_render)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sky", default="night")
    ap.add_argument("parts", nargs="*", default=["all"])
    a = ap.parse_args(argv)
    parts = set(a.parts)
    if "all" in parts:
        parts = {"vis", "cams", "events", "paths", "lights"}

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    import render
    from engine import hostiles, shots as SH
    from tools.crammys_geo import first_hit

    ses = render.Session("crammys", sky=a.sky)
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    film = ses.film
    print("[probe] render settings after build: %dx%d, %d samples, fps %d, frames %d-%d" % (
        scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples, scene.render.fps,
        scene.frame_start, scene.frame_end))
    shots = sorted(film.shots, key=lambda s: s.frame_start)
    W = C.v.world

    def shot_at(f):
        for s in shots:
            if s.frame_start <= f <= s.frame_end:
                return s
        return None

    # ------------------------------------------------------------------ visibility
    if "vis" in parts:
        print("\n[probe] VISIBILITY: every cast member and every object hanging on it, at first/mid/last frame of "
              "every shot")
        roots = {}
        for name, c in st.cast.items():
            r = getattr(c, "root", None) or getattr(c, "sprite", None)
            if r is not None:
                roots.setdefault(r.name, []).append(name)
        dup = {k: v for k, v in roots.items() if len(v) > 1}
        print("  cast members: %d; shared root objects: %s" % (len(st.cast), dup or "none"))
        bad = 0
        for name, c in sorted(st.cast.items()):
            obs = []
            if hasattr(c, "objects"):
                try:
                    obs = list(c.objects())
                except TypeError:
                    obs = list(c.objects)
            root = getattr(c, "root", None)
            extra = []
            if root is not None:
                extra = [o for o in root.children_recursive if o not in obs]
            att = [x.ob for x in getattr(c, "_attached", [])]
            book = c.__dict__.get(hostiles._BOOK) if hasattr(c, "__dict__") else None
            arrows = [d["object"] for d in book["arrows"]] if book else []
            for s in shots:
                want = name in st.in_shot.get(s.name, ())
                for f in (s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end):
                    rh = [o for o in obs if o.type == "MESH" and not hidden(o, f)]
                    # anything that hangs on it visible while the character is not wanted
                    hang = [o for o in extra + att + arrows if o.type == "MESH" and not hidden(o, f)]
                    if not want and (rh or hang):
                        bad += 1
                        if bad < 40:
                            print("  !! %s visible outside its shots: %s f%d: %s" % (
                                name, s.name, f, ", ".join(o.name for o in (rh + hang)[:4])))
                    if want and obs and not rh:
                        bad += 1
                        if bad < 40:
                            print("  !! %s wanted in %s but no mesh visible on f%d" % (name, s.name, f))
            if arrows:
                spans = []
                for ob in arrows:
                    on = [s.name for s in shots if not hidden(ob, (s.frame_start + s.frame_end) // 2)]
                    spans.append("%s from f%d in %s" % (ob.name, [d["frame"] for d in book["arrows"] if
                                                                  d["object"] is ob][0], ",".join(on)))
                print("  arrows %s: %s" % (name, "; ".join(spans)))
            hands = getattr(c, "_hands", None)
            if hands:
                for side, lst in hands.items():
                    for h in lst:
                        for vn, at in h.variants.items():
                            on = [s.name for s in shots if not hidden(at.ob, (s.frame_start + s.frame_end) // 2)]
                            # frames where visible just outside its span
                            leak = [f for f in range(1, film.frame_end + 1, 1)
                                    if not hidden(at.ob, f) and (h.start is not None and f < h.start or
                                                                 h.end is not None and f >= h.end)]
                            print("  held %-10s %-18s %-6s start %s end %s visible mid-shot in: %s%s" % (
                                name, h.item_id, vn or "-", h.start, h.end, ",".join(on) or "-",
                                ("  LEAK frames %d..%d (%d)" % (leak[0], leak[-1], len(leak))) if leak else ""))
        print("  visibility problems: %d" % bad)
        # non-cast objects of the film: the last lantern, kicker, fills, totem
        for ob in bpy.data.objects:
            if any(k in ob.name for k in ("kicker", "crammys_fill", "last_lantern", "totem", "music_disc",
                                         "cat_jb", "crammys_disc")):
                on = [s.name for s in shots if not hidden(ob, (s.frame_start + s.frame_end) // 2)]
                if len(on) < len(shots):
                    print("  object %-40s visible mid-shot in: %s" % (ob.name, ",".join(on) or "-"))

    # ------------------------------------------------------------------ cameras
    if "cams" in parts:
        print("\n[probe] CAMERAS: position inside a solid block?  hero in frame / safe area / blocked (first, mid,"
              " last frame)")
        scene.render.resolution_x, scene.render.resolution_y = 540, 960
        for s in shots:
            cam = s.camera
            scene.camera = cam
            rows = []
            for f in (s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end):
                scene.frame_set(f)
                dg = bpy.context.evaluated_depsgraph_get()
                p = cam.matrix_world.translation.copy()
                bx, by, bz = (int(math.floor(v)) for v in p)
                solid = W.is_solid(bx, by, bz)
                bid = W.block_id(bx, by, bz)
                gz = C.v.ground(p.x, p.y)
                hs = []
                for label, obs in st.heroes.get(s.name, []):
                    for ob in obs[:1]:
                        q = ob.matrix_world.translation
                        co = world_to_camera_view(scene, cam, q)
                        x, y = co.x * 100, (1 - co.y) * 100
                        safe = 8 <= x <= 82 and 14 <= y <= 60
                        blk = first_hit(scene, dg, p, q, own={ob.name} | {c.name for c in ob.children_recursive}
                                        | ({ob.parent.name} if ob.parent else set())
                                        | set(o.name for o in (ob.parent.children_recursive if ob.parent else [])))
                        hs.append("%s %.0f,%.0f%s%s" % (label, x, y, "" if safe else " OUT", "" if blk is None
                                                         else " blocked:" + blk))
                rows.append("f%d cam(%.2f,%.2f,%.2f) %s%s ground %.2f | %s" % (
                    f, p.x, p.y, p.z, bid or "air", " SOLID" if solid else "", gz if gz is not None else -99,
                    "; ".join(hs)))
            print("  %-18s lens %.0f\n     %s" % (s.name, cam.data.lens, "\n     ".join(rows)))

    # ------------------------------------------------------------------ events
    if "events" in parts:
        print("\n[probe] EVENTS")
        T = C.T

        def pos(c, f):
            return tuple(round(v, 2) for v in c.pos_at(f))

        # rd07
        s = C.shots["rd07_chased"]
        steve, z, kai = st.cast["steve_rd"], st.cast["zombie_rd"], st.cast["kai_rd"]
        scene.camera = s.camera
        inframe = []
        for f in range(s.frame_start, s.frame_end + 1):
            scene.frame_set(f)
            co = world_to_camera_view(scene, s.camera, Vector(steve.eye_point(f)))
            cz = world_to_camera_view(scene, s.camera, Vector(z.eye_point(f)) if hasattr(z, "eye_point") else
                                      z.head.matrix_world.translation)
            inframe.append((f, round(co.x * 100), round((1 - co.y) * 100), round(cz.x * 100), round((1 - cz.y) * 100)))
        print("  rd07 steve eyes / zombie eyes (x%, y%) per frame:")
        print("   " + " ".join("%d:%d,%d|%d,%d" % r for r in inframe[::3]))
        door = C.v._door_sets["house_e"]
        for d in door:
            ob = d.get("object") or d.get("ob")
            print("  house_e door part keys:", ob.name if ob else d.keys(),
                  [(round(k.co[0], 1), round(k.co[1], 2)) for fc in SH.fcurves_of(ob) for k in fc.keyframe_points]
                  if ob else "")
        print("  rd07 steve pos f509 %s f530 %s f550 %s f564 %s" % (pos(steve, 509), pos(steve, 530), pos(steve, 550),
                                                                 pos(steve, 564)))
        print("  rd07 zombie pos f509 %s f564 %s; B07_STOP %s" % (pos(z, 509), pos(z, 564), C.P("zombie_stop")))
        # jb18 walk end
        s = C.shots["jb18_nobody_asked"]
        p = st.cast["steve_jb"]
        prev, stop = None, None
        for f in range(s.frame_start, s.frame_end + 1):
            q = p.pos_at(f)
            if prev is not None and (q - prev).length < 1e-4 and stop is None:
                stop = f
            if prev is not None and (q - prev).length >= 1e-4:
                stop = None
            prev = q
        print("  jb18 steve stops on f%s (Nobody %d, asked %d), pos f%d %s, three_steve %s" % (
            stop, T["jb18_nobody_asked"].at("Nobody"), T["jb18_nobody_asked"].at("asked"), s.frame_end,
            pos(p, s.frame_end), C.P("three_steve")))
        # jb18 -> jb19 position jump
        print("  steve_jb f1148 %s -> f1149 %s ; f1200 %s -> f1201 %s" % (pos(p, 1148), pos(p, 1149), pos(p, 1200),
                                                                         pos(p, 1201)))
        # md
        cr, sk, sm = st.cast["creeper_md"], st.cast["skeleton_md"], st.cast["steve_md"]
        print("  md13 steve_md pos f844 %s f870 %s f910 %s f930 %s" % (pos(sm, 844), pos(sm, 870), pos(sm, 910),
                                                                     pos(sm, 930)))
        print("  md15 steve_md pos f931 %s f995 %s; md16 f996 %s f1036 %s" % (pos(sm, 931), pos(sm, 995),
                                                                            pos(sm, 996), pos(sm, 1036)))
        print("  creeper_md f931 %s f960 %s; swelling 931..995: %s" % (
            pos(cr, 931), pos(cr, 960), [round(cr.swelling_at(f), 2) for f in range(931, 996, 5)]))
        print("  md_kill memo %s, md disc rest %s land %s" % (C.memo.get("md_kill"), getattr(C.memo.get("md_disc"),
              "rest_pos", None), getattr(C.memo.get("md_disc"), "land_frame", None)))
        print("  skeleton_md pos f906 %s f920 %s f931 %s; bow %s" % (pos(sk, 906), pos(sk, 920), pos(sk, 931),
              [(f, sk.bow_at(f)) for f in (840, 850, 858, 880, 904, 910, 920, 930, 931, 960, 990)]))
        print("  md12 skeleton bow %s" % [(f, sk.bow_at(f)) for f in (797, 815, 830, 843, 844)])
        # gd05 last lantern
        ll = C.bd.last_lantern
        print("  last lantern placed %s" % (ll.placed,))
        # insert
        print("  insert frame %d; song notes fn21..fn24: %s" % (C.insert_frame(), [
            [round(f, 1) for f in C.song_note_frames(C.shots[n].frame_start, C.shots[n].frame_end)]
            for n in ("jb20_eleven", "fn21_running", "fn22_nobody_moved", "fn23_kai", "fn24_vocals")]))
        # rd17 steve crossing
        s = C.shots["rd17_run_back"]
        p = st.cast["steve_rd"]
        scene.camera = s.camera
        xs = []
        for f in range(s.frame_start, s.frame_end + 1, 2):
            scene.frame_set(f)
            co = world_to_camera_view(scene, s.camera, Vector(p.eye_point(f)))
            xs.append("%d:%d,%d" % (f, round(co.x * 100), round((1 - co.y) * 100)))
        print("  rd17 steve eyes: " + " ".join(xs))

    # ------------------------------------------------------------------ paths
    if "paths" in parts:
        print("\n[probe] PATHS: solid blocks on the body column (feet+0.1 .. +1.8) along every path the stubs walk")
        for pname in ("lane_home", "lane_to_square", "crammys_walk_out", "crammys_into_middle", "crammys_round",
                      "bandstand_wing_to_three", "bandstand_steve_cross"):
            pts = C.v.paths.get(pname)
            if not pts:
                print("  %s: MISSING" % pname)
                continue
            hits = []
            for a_, b_ in zip(pts, pts[1:]):
                n = max(2, int(math.dist(a_[:2], b_[:2]) / 0.1))
                for i in range(n + 1):
                    t = i / n
                    x, y = a_[0] + (b_[0] - a_[0]) * t, a_[1] + (b_[1] - a_[1]) * t
                    z0 = a_[2] + (b_[2] - a_[2]) * t
                    for dz in (0.1, 0.9, 1.7):
                        for ox, oy in ((0.3, 0), (-0.3, 0), (0, 0.3), (0, -0.3)):
                            cx, cy, cz = (int(math.floor(v)) for v in (x + ox, y + oy, z0 + dz))
                            if W.is_solid(cx, cy, cz):
                                hits.append((round(x, 2), round(y, 2), round(z0 + dz, 2), W.block_id(cx, cy, cz)))
            uniq = sorted(set((h[3], int(math.floor(h[0])), int(math.floor(h[1])), int(math.floor(h[2]))) for h in hits))
            print("  %-24s %d pts %s -> %s : %s" % (pname, len(pts), tuple(round(v, 2) for v in pts[0]),
                                                   tuple(round(v, 2) for v in pts[-1]),
                                                   ("SOLID " + str(uniq[:8])) if uniq else "clear"))

    # ------------------------------------------------------------------ lights
    if "lights" in parts:
        print("\n[probe] LIGHTS: an energy key on every shot's first frame for every lantern light")
        lls = list(C.v.lantern_lights)
        miss = {}
        for ob in lls:
            keys = set()
            for fc in SH.fcurves_of(ob.data):
                if fc.data_path == "energy":
                    keys |= {int(round(k.co[0])) for k in fc.keyframe_points}
            for s in shots:
                if s.frame_start not in keys:
                    miss.setdefault(s.name, 0)
                    miss[s.name] += 1
        print("  %d lantern lights; shots missing keys: %s" % (len(lls), miss or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
