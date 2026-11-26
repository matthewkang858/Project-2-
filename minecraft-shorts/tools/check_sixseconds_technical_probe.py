"""Independent checker's probe of films/sixseconds (no render): builds one sky through render.Session and reports
visibility per shot, cameras against blocks, sight lines to heroes, pit / pillar states, lights, fills, the stare,
the match cut, the cast's objects. Writes out/test/check_sixseconds_technical/probe_<sky>.json and prints a digest.

    $BPY -m tools.check_sixseconds_technical_probe wastes|soul
"""
import json
import math
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(sky):
    import bpy
    from mathutils import Vector
    import render
    from engine import nether
    ses = render.Session("sixseconds", sky=sky)
    res = ses.result
    st, C, film, nar = res["stage"], res["context"], res["film"], res["narration"]
    scene = ses.scene
    bas = C.bas
    out = {"sky": sky}
    print("RES", scene.render.resolution_x, scene.render.resolution_y, "samples", scene.cycles.samples)
    out["res"] = (scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples)
    print("SEGMENTS", st.sky_segments())
    print("FADES", [(round(a * 24 + 1, 2), round(b * 24 + 1, 2), g0, g1) for a, b, g0, g1 in st.fades])

    shots = sorted(film.shots, key=lambda s: s.frame_start)
    # ---- 1. visibility of every object whose hide_render is animated, per shot
    animated = []
    for ob in bpy.data.objects:
        ad = ob.animation_data
        if ad and ad.action and any(fc.data_path == "hide_render" for fc in getattr(ad.action, "fcurves", [])):
            animated.append(ob)
    # Blender 5 layered actions: fall back to evaluating every object
    if not animated:
        animated = list(bpy.data.objects)
    samples = {}
    for s in shots:
        fs = sorted({s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end})
        samples[s.name] = fs
    vis = defaultdict(lambda: defaultdict(list))   # ob -> shot -> [visible at sample]
    allobs = list(bpy.data.objects)
    for s in shots:
        for f in samples[s.name]:
            scene.frame_set(f)
            for ob in allobs:
                vis[ob.name][s.name].append(not ob.hide_render)
    always, never, toggles = [], [], {}
    for name, per in vis.items():
        flat = [v for vs in per.values() for v in vs]
        if all(flat):
            always.append(name)
        elif not any(flat):
            never.append(name)
        else:
            toggles[name] = {k: vs for k, vs in per.items()}
    print("OBJECTS", len(allobs), "always visible", len(always), "never", len(never), "toggling", len(toggles))
    # map toggling objects to a cast member when possible
    owner = {}
    for cname, c in st.cast.items():
        obs = []
        for attr in ("root", "object"):
            r = getattr(c, attr, None)
            if r is not None:
                obs.append(r)
        stack = list(obs)
        while stack:
            o = stack.pop()
            owner.setdefault(o.name, cname)
            stack.extend(o.children)
    unowned = defaultdict(list)
    wrong = []
    for name, per in sorted(toggles.items()):
        shots_vis = [k for k, vs in per.items() if any(vs)]
        cname = owner.get(name)
        if cname is None:
            unowned[tuple(shots_vis)].append(name)
            continue
        expect = [s.name for s in shots if cname in st.in_shot.get(s.name, ())]
        extra = [k for k in shots_vis if k not in expect]
        if extra:
            wrong.append((name, cname, extra))
    print("CAST OBJECTS VISIBLE OUTSIDE THEIR SHOTS:", len(wrong))
    for w in wrong[:40]:
        print("   ", w)
    print("TOGGLING OBJECTS WITH NO CAST OWNER (grouped by the shots they are visible in):")
    for k, names in sorted(unowned.items(), key=lambda kv: -len(kv[1])):
        print("   %-60s %3d  e.g. %s" % (",".join(k)[:60], len(names), ", ".join(sorted(names)[:6])))
    out["unowned"] = {",".join(k): sorted(v) for k, v in unowned.items()}
    out["wrong"] = wrong

    # cast inventory: distinct objects
    roots = {}
    for cname, c in st.cast.items():
        r = getattr(c, "root", None) or getattr(c, "object", None)
        roots[cname] = r.name if r is not None else None
    dup = [n for n in roots.values() if list(roots.values()).count(n) > 1]
    print("CAST", len(st.cast), "members; duplicate roots:", sorted(set(dup)))
    out["cast"] = roots

    # ---- 2. cameras: position inside a block?, distance to nearest solid cell, sight lines to heroes
    W = bas.world
    def nearest_solid(p, r=1):
        best = 9.0
        cx, cy, cz = (int(math.floor(v)) for v in p)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    c = (cx + dx, cy + dy, cz + dz)
                    if W.block_id(*c) and W.is_full_cube(*c):
                        q = [min(max(p[k], c[k]), c[k] + 1) for k in range(3)]
                        best = min(best, math.dist(p, q))
        return best
    cams = {}
    for s in shots:
        rows = []
        for f in (s.frame_start, s.frame_end):
            scene.frame_set(f)
            cam = scene.camera
            p = tuple(cam.matrix_world.translation)
            cell = tuple(int(math.floor(v)) for v in p)
            inside = W.block_id(*cell)
            rows.append(dict(frame=f, cam=cam.name, pos=[round(v, 3) for v in p], inside=inside,
                             near=round(nearest_solid(p), 3), lens=round(cam.data.lens, 1),
                             fstop=round(cam.data.dof.aperture_fstop, 2)))
        # heroes: sight from camera to each hero object's world centre at mid frame
        mid = (s.frame_start + s.frame_end) // 2
        scene.frame_set(mid)
        cam = scene.camera
        cp = tuple(cam.matrix_world.translation)
        hs = []
        for label, obs in st.heroes.get(s.name, []):
            for ob in obs[:2]:
                hp = tuple(ob.matrix_world.translation)
                blk = nether.sight_blocked(W, cp, hp)
                hs.append((label, ob.name, [round(v, 2) for v in hp], blk))
        cams[s.name] = dict(ends=rows, heroes=hs)
        print("CAM %-14s %s f%d %s in=%s near=%.2f | f%d %s near=%.2f | %smm f/%s" % (
            s.name, rows[0]["cam"], rows[0]["frame"], rows[0]["pos"], rows[0]["inside"], rows[0]["near"],
            rows[1]["frame"], rows[1]["pos"], rows[1]["near"], rows[0]["lens"], rows[0]["fstop"]))
        for h in hs:
            if h[3]:
                print("      HERO SIGHT BLOCKED", h)
    out["cams"] = cams

    # ---- 3. pit and pillar per shot
    print("PIT / PILLAR per shot (start, mid, end):")
    pit_objs = {cell: b for cell, b in bas.pit_blocks.items()}
    for s in shots:
        states = [bas.pit_state(f) for f in samples[s.name]]
        pv = []
        for f in samples[s.name]:
            scene.frame_set(f)
            n_pit = sum(1 for b in pit_objs.values() if any(not o.hide_render for o in _objs(b)))
            n_pil = sum(1 for b in bas.pillar if any(not o.hide_render for o in _objs(b)))
            pv.append((n_pit, n_pil))
        print("   %-14s pit_state %s  visible pit blocks / pillar blocks %s" % (s.name, states, pv))
    # the last block in pt06: frame by frame
    s6 = [s for s in shots if s.name == "pt06_dig"][0]
    last = bas.pit_last
    seq = []
    for f in range(s6.frame_start - 1, s6.frame_start + 20):
        scene.frame_set(f)
        seq.append((f, [o.name for o in _objs(last) if not o.hide_render]))
    print("PIT_LAST around pt06:", [(f, len(v), v[:1]) for f, v in seq])

    # ---- 4. lights: lava wall + channels + key fill + pit fill over the gate shots
    names = [o.name for o in bas.lantern_lights]
    lw = bas.lava.get("home_lava_wall_light")
    print("lava wall light in lantern_lights:", (lw is not None and getattr(lw, "name", None) in names), type(lw))
    lights = [o for o in bpy.data.objects if o.type == "LIGHT"]
    track = [o for o in lights if "lava" in o.name.lower() or "fill" in o.name.lower() or "key" in o.name.lower()]
    print("tracked lights:", [o.name for o in track][:20])
    rows = []
    for f in (1, 50, 97, 98, 179, 1065, 1066, 1114, 1115, 1140, 1166, 1172, 1173, 1174, 1200, 1282, 1283, 1300):
        scene.frame_set(f)
        rows.append((f, [(o.name[:28], round(o.data.energy, 1), o.hide_render) for o in track[:8]]))
    for r in rows:
        print("   LIGHT f%d %s" % r)

    # ---- 5. the stare: brute_rw head world matrix over rw21 + rw22
    b = st.cast.get("brute_rw")
    if b is not None:
        hm = []
        for f in range(1351, 1496, 4):
            scene.frame_set(f)
            m = b.head.matrix_world
            hm.append((f, tuple(round(v, 4) for v in m.translation), tuple(round(v, 3) for v in m.to_euler())))
        moves = sorted({(t, e) for _f, t, e in hm})
        print("STARE brute_rw head: distinct poses over 1351-1495 (step 4):", len(moves))
        for f, t, e in hm[::6]:
            print("    f%d %s %s" % (f, t, e))
    # ---- 6. the match cut: piglin_gt* every part at 1172 vs 1173; camera 1172 vs 1173
    diffs = []
    for name in ("piglin_gt1", "piglin_gt2", "piglin_xbow_gt3"):
        c = st.cast[name]
        obs = [c.root] + list(c.root.children_recursive)
        scene.frame_set(1172)
        a = {o.name: o.matrix_world.copy() for o in obs}
        scene.frame_set(1173)
        d = max((a[o.name].translation - o.matrix_world.translation).length for o in obs)
        dr = max(max(abs(x - y) for x, y in zip(a[o.name].to_euler(), o.matrix_world.to_euler())) for o in obs)
        diffs.append((name, round(d, 5), round(dr, 5)))
    print("MATCH CUT piglins max part move 1172->1173 (blocks, rad):", diffs)
    for f in (1171, 1172, 1173, 1174):
        scene.frame_set(f)
        cam = scene.camera
        print("    cam f%d %s %s %s" % (f, cam.name, tuple(round(v, 4) for v in cam.matrix_world.translation),
                                       tuple(round(v, 4) for v in cam.matrix_world.to_euler())))
    json.dump(out, open(os.path.join(ROOT, "out", "test", "check_sixseconds_technical", "probe_%s.json" % sky), "w"),
              indent=1, default=str)


def _objs(b):
    """Every object of a Breakable (its object and crack stage copies)."""
    obs = []
    for attr in ("object",):
        o = getattr(b, attr, None)
        if o is not None:
            obs.append(o)
            obs.extend(o.children_recursive)
    for o in getattr(b, "stages", []) or []:
        if hasattr(o, "hide_render"):
            obs.append(o)
    return obs


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "wastes")
