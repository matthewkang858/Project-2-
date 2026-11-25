"""Checker probe for The Hello (technical angle): build one sky in this process, time it, inspect, render.

    $BPY -m tools.check_hello_technical_probe gold [--render F,F] [--inspect]
"""
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")


def cell(p):
    return (int(math.floor(p[0])), int(math.floor(p[1])), int(math.floor(p[2])))


def main(argv):
    sky = argv[0]
    render_frames = []
    if "--render" in argv:
        render_frames = [int(v) for v in argv[argv.index("--render") + 1].split(",")]
    import bpy
    import render
    from mathutils import Vector
    t = time.time()
    ses = render.Session("hello", sky=sky)
    tb = time.time() - t
    print("[probe] BUILD sky=%s %.1f s; base=%s; segments=%s" % (sky, tb, ses.base, ses.segments))
    res = ses.result
    st, C = res["stage"], res["context"]
    scene = ses.scene
    print("[probe] fades:", [tuple(round(x, 4) for x in r) for r in st.fades])
    if "--inspect" in argv:
        inspect(bpy, Vector, ses, st, C, scene)
    for f in render_frames:
        if not ses.owns(f):
            print("[probe] frame %d not in sky %s, skipped" % (f, sky))
            continue
        ses.configure((270, 480), 4, 2, True)
        path = os.path.join(OUT, "check_hello_technical_%s_%d.png" % (sky, f))
        t = time.time()
        ses.render_frame(f, path)
        print("[probe] rendered %s in %.1f s" % (path, time.time() - t))
    return 0


def inspect(bpy, Vector, ses, st, C, scene):
    from engine import breaking, characters, players
    from films import hello_common as HC
    v, w = C.v, C.v.world
    film = ses.film
    shots = {s.name: s for s in film.shots}
    order = sorted(film.shots, key=lambda s: s.frame_start)

    # ---------------- cast per shot, distinct objects
    print("\n[probe] CAST PER SHOT")
    for s in order:
        print("  %-14s %4d-%4d %-6s %s" % (s.name, s.frame_start, s.frame_end, st.sky_at(s.frame_start),
                                          sorted(st.in_shot.get(s.name, ()))))
    names = list(st.cast)
    roots = {}
    for n, c in st.cast.items():
        r = getattr(c, "root", None)
        roots.setdefault(r.name if r else None, []).append(n)
    dup = {k: v_ for k, v_ in roots.items() if len(v_) > 1}
    print("[probe] cast %d: %s" % (len(names), names))
    print("[probe] duplicate roots:", dup)

    # ---------------- visibility: inside / outside shots
    print("\n[probe] VISIBILITY")
    bad = 0
    for n, c in st.cast.items():
        obs = list(c.objects()) if hasattr(c, "objects") else []
        att = [a.ob for a in getattr(c, "_attached", [])]
        for s in order:
            want = n in st.in_shot.get(s.name, ())
            f = (s.frame_start + s.frame_end) // 2
            scene.frame_set(f)
            vis = [not o.hide_render for o in obs]
            avis = [not o.hide_render for o in att]
            if want and not all(vis):
                bad += 1
                print("  %s IN %s but hidden parts %s" % (n, s.name, [o.name for o in obs if o.hide_render][:4]))
            if not want and any(vis):
                bad += 1
                print("  %s NOT in %s but visible parts %s" % (n, s.name, [o.name for o in obs if not o.hide_render][:4]))
            if not want and any(avis):
                bad += 1
                print("  %s NOT in %s but attached visible %s" % (n, s.name, [o.name for o in att if not o.hide_render]))
    print("[probe] visibility problems:", bad)

    # ---------------- armor and items
    print("\n[probe] ARMOR / ITEMS")
    for n, c in st.cast.items():
        if isinstance(c, players.Player):
            s0 = next(s for s in order if n in st.in_shot.get(s.name, ())) if any(
                n in st.in_shot.get(s.name, ()) for s in order) else None
            f = (s0.frame_start + s0.frame_end) // 2 if s0 else 1
            scene.frame_set(f)
            att = [(a.ob.name, a.ob.parent.name if a.ob.parent else None, not a.ob.hide_render) for a in c._attached]
            mats = set()
            for a in c._attached:
                for slot in getattr(a.ob, "material_slots", []):
                    if slot.material:
                        mats.add(slot.material.name)
            print("  %s skin=%s still=%s frame %d attached=%s" % (n, getattr(c, "skin", "?"), getattr(c, "still", None),
                                                               f, att))
            gl = [m for m in mats if "glint" in m.lower() or "enchant" in m.lower()]
            print("     materials with glint:", gl[:6], " stamp_every_frame:",
                  [a.ob.name for a in c._attached if a.ob.type == "MESH" and "stamp_every_frame" in a.ob.data])
            # eye emission (herobrine)
            for o in c.objects():
                for slot in getattr(o, "material_slots", []):
                    m = slot.material
                    if m and m.node_tree:
                        for nd in m.node_tree.nodes:
                            if nd.type == "BSDF_PRINCIPLED" and nd.inputs["Emission Strength"].default_value > 0:
                                print("     emission %s on %s: %.2f" % (m.name, o.name, nd.inputs["Emission Strength"].default_value))
    for n, c in st.cast.items():
        if not hasattr(c, "_attached") and not isinstance(c, characters.Character):
            print("  non-character cast:", n, type(c).__name__)

    # ---------------- places
    print("\n[probe] PLACES (feet cell, cell above, two above)")
    for k, p in HC.PLACES.items():
        pts = p if isinstance(p[0], tuple) else (p,)
        for q in pts:
            P = C.stand(q)
            c0 = cell((P[0], P[1], P[2] + 0.05))
            ids = [w.block_id(c0[0], c0[1], c0[2] + dz) for dz in (-1, 0, 1, 2)]
            print("  %-14s %s -> %s  below/feet/+1/+2 = %s" % (k, q, tuple(round(x, 3) for x in P), ids))
    for k in ("forest_gap", "floating_oak_under", "bare_oaks_among", "pyramid_beside", "exit_gate", "house_a_center",
              HC.RED_BED, HC.CHILD_BED):
        P = C.A[k]
        c0 = cell((P[0], P[1], P[2] + 0.05))
        print("  A %-18s %s  feet/+1 = %s" % (k, tuple(round(x, 3) for x in P),
                                             [w.block_id(c0[0], c0[1], c0[2] + dz) for dz in (0, 1)]))

    # ---------------- ascii map of the door / house_a area
    print("\n[probe] MAP x 2..21, y -3..-16 (rows north->south), layers z=0,1,2 ; '.'=air")
    sym = {}
    for z in (0, 1, 2):
        print("  z=%d   x: %s" % (z, "".join(str(abs(x) % 10) for x in range(2, 22))))
        for y in range(-3, -17, -1):
            row = ""
            for x in range(2, 22):
                b = w.block_id(x, y, z)
                if b is None:
                    ch = "."
                else:
                    ch = sym.setdefault(b, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789#$%&*"[len(sym)])
                row += ch
            print("  y%4d %s" % (y, row))
    print("  legend:", {v_: k for k, v_ in sym.items()})
    for c_ in ((9, -8, 0), (10, -8, 1), (10, -8, 2), (9, -7, 2), (9, -9, 2), (10, -11, 2), (11, -10, 1), (11, -11, 1),
               (11, -12, 1), (15, -13, 2), (15, -12, 2), (14, -13, 2), (18, -14, 2), (17, -14, 2), (17, -8, 2),
               (18, -8, 2)):
        print("  block", c_, w.get(*c_))

    # ---------------- cameras of every shot: inside blocks? line of sight to the heroes
    print("\n[probe] CAMERAS")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for s in order:
        for f in (s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end):
            scene.frame_set(f)
            scene.camera = s.camera
            cam = s.camera
            pos = cam.matrix_world.translation.copy()
            cc = cell(pos)
            inside = w.get(*cc)
            msg = "  %-14s f%4d cam (%.2f, %.2f, %.2f) lens %.0f cell %s=%s" % (
                s.name, f, pos.x, pos.y, pos.z, cam.data.lens, cc, inside[0] if inside else None)
            heroes = st.heroes.get(s.name, [])
            depsgraph = bpy.context.evaluated_depsgraph_get()
            for label, obs in heroes:
                for ob in obs:
                    tgt = ob.matrix_world.translation + Vector((0, 0, 0.25))
                    hit = first_visible_hit(scene, depsgraph, pos, tgt, f)
                    own = ob.name.split(".")[0].rsplit("_", 1)[0]
                    msg += " | %s->%s" % (label, hit)
                    # projected position
                    from bpy_extras.object_utils import world_to_camera_view
                    co = world_to_camera_view(scene, cam, tgt)
                    msg += " (x%.0f%% y%.0f%% d%.1f)" % (co.x * 100, (1 - co.y) * 100, co.z)
            print(msg)

    # ---------------- door crack stage and open state across the dn / dg shots
    print("\n[probe] DOOR")
    door = C.door
    for f in (72, 100, 144, 145, 1101, 1192, 1193, 1257, 1258, 1260, 1266, 1272, 1300, 1358, 1445, 1531, 211, 271, 915, 997):
        scene.frame_set(f)
        print("  f%4d crack stage %s door rot z %.3f hide_render %s" % (f, breaking.stage_at(door, f),
                                                                       door.rotation_euler.z, door.hide_render))

    # ---------------- lights at sample frames
    print("\n[probe] LIGHTS")
    fills = [o for o in bpy.data.objects if o.name.startswith("hello_fill_")]
    for f in (40, 100, 160, 182, 195, 226, 290, 370, 560, 900, 930, 1020, 1075, 1150, 1225, 1300, 1400, 1480):
        scene.frame_set(f)
        on = [o for o in C.v.lantern_lights if not o.hide_render and o.data.energy > 0]
        dt = [(round(o.data.energy, 1), o.hide_render) for o in C.door_torches]
        fl = [(o.name, o.hide_render, round(o.data.energy, 1)) for o in fills]
        print("  f%4d torches on %3d  door torches %s  fills %s" % (f, len(on), dt, fl))

    # ---------------- crouch / nod helpers on scratch instances (after everything else)
    print("\n[probe] HELPERS on scratch instances")
    p = C.actor("steve_iron", "dgzz")
    p.place(2000, (30.0, 30.0, 0.0), 0.0)
    end = C.crouch_twice(p, 2010)
    row = []
    for f in range(2008, 2034):
        row.append("%d:%s" % (f, "C" if p.crouching_at(f) else "-"))
    hz = []
    for f in range(2008, 2034, 1):
        scene.frame_set(f)
        hz.append(round(p.head.matrix_world.translation.z, 3))
    print("  crouch_twice(2010) returned", end)
    print("  crouching_at:", " ".join(row))
    print("  head z:", hz)
    q = C.actor("watcher", "dgzz")
    q.place(2100, (32.0, 30.0, 0.0), 0.0)
    down = C.crouch_slow(q, 2110, frames=24)
    hz = []
    for f in (2105, 2110, 2116, 2122, 2128, 2134, 2140, 2160):
        scene.frame_set(f)
        hz.append((f, round(q.head.matrix_world.translation.z, 3), q.crouching_at(f)))
    print("  crouch_slow(2110) returned", down, hz)
    r = C.actor("steve_iron", "dgzy")
    r.place(2200, (34.0, 30.0, 0.0), 0.0)
    r.sneak(2210, True)
    scene.frame_set(2215)
    print("  Player.sneak head z %.3f vs crouch_slow end head z %s" % (r.head.matrix_world.translation.z, hz[-1]))
    k = C.actor("child", "dgzz")
    k.place(2300, (36.0, 30.0, 0.0), 0.0)
    k.look_at(2300, (36.0, 28.0, 3.0), ease=0)
    e = C.hello_nod(k, 2310)
    pit = []
    for f in range(2308, 2328, 2):
        scene.frame_set(f)
        pit.append(round(k.head.rotation_euler.x, 3))
    print("  hello_nod(2310) returned", e, "head pitch:", pit)
    # lie_down then place (child_in: in16 lying, in17 standing)
    ci = st.cast.get("child_in")
    for f in (1046, 1047, 1060):
        scene.frame_set(f)
        print("  child_in f%d root %s rot %s hips rot x %.3f" % (f, tuple(round(x, 2) for x in ci.root.location),
                                                                 tuple(round(x, 2) for x in ci.root.rotation_euler),
                                                                 ci.hips.rotation_euler.x if hasattr(ci, "hips") else -9))
    # watcher arms straight / idle
    wd = st.cast.get("watcher_dg")
    for f in (1260, 1300, 1350):
        scene.frame_set(f)
        print("  watcher_dg f%d arm_r rot %s arm_l rot %s head rot %s" % (
            f, tuple(round(x, 3) for x in wd.arm_r.rotation_euler), tuple(round(x, 3) for x in wd.arm_l.rotation_euler),
            tuple(round(x, 3) for x in wd.head.rotation_euler)))
    print("[probe] render settings after build: %s x %s, %s spp" % (ses.base[0], ses.base[1], ses.base[2]))


def first_visible_hit(scene, depsgraph, a, b, f):
    """Name of the first rendered object between a and b (None = clear)."""
    from mathutils import Vector
    d = (b - a)
    L = d.length
    d.normalize()
    o = a.copy()
    gone = 0.0
    for _ in range(40):
        hit, loc, nrm, idx, ob, mat = scene.ray_cast(depsgraph, o, d, distance=L - gone - 0.05)
        if not hit:
            return None
        orig = ob.original if hasattr(ob, "original") else ob
        if orig.hide_render or not orig.visible_camera:
            step = (loc - o).length + 0.01
            o = loc + d * 0.01
            gone += step
            continue
        return "%s@%.2f" % (orig.name, (loc - a).length)
    return "?"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
