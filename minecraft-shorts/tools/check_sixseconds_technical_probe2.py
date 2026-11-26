"""Independent checker's second probe of films/sixseconds (no render): places, routes, the mine's blackstone drop,
the lava flicker frame by frame, the ears across the match cut, and the shared helpers keyed on SCRATCH instances
(read back from the channels). $BPY -m tools.check_sixseconds_technical_probe2
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def seg_blocked(W, a, b, heights=(0.3, 1.0, 1.6), half=0.3):
    """Cells a 0.6-wide figure walking a -> b would pass through (full cubes or anything solid), with the point."""
    hits = []
    n = max(1, int(math.dist(a[:2], b[:2]) / 0.1))
    for i in range(n + 1):
        t = i / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        z0 = a[2] + (b[2] - a[2]) * t
        for dx in (-half, 0.0, half):
            for dy in (-half, 0.0, half):
                for h in heights:
                    c = (int(math.floor(x + dx)), int(math.floor(y + dy)), int(math.floor(z0 + h)))
                    bid = W.block_id(*c)
                    if bid and W.is_solid(*c):
                        hits.append(((round(x, 2), round(y, 2)), c, bid))
    # floor under the centre line
    holes = []
    for i in range(n + 1):
        t = i / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        z0 = a[2] + (b[2] - a[2]) * t
        c = (int(math.floor(x)), int(math.floor(y)), int(math.floor(z0 - 0.5)))
        bid = W.block_id(*c)
        if not bid or not W.is_solid(*c):
            holes.append(((round(x, 2), round(y, 2)), c, bid))
    return hits, holes


def main():
    import bpy
    from mathutils import Vector
    import render
    from films import sixseconds_common as SC
    ses = render.Session("sixseconds", sky="wastes")
    res = ses.result
    st, C, film, nar = res["stage"], res["context"], res["film"], res["narration"]
    scene = ses.scene
    bas = C.bas
    W = bas.world
    shots = {s.name: s for s in film.shots}

    # ---- places
    bad = []
    for k in SC.PLACES:
        try:
            p = C.P(k)
        except Exception as e:
            bad.append((k, str(e)))
            continue
        cell = tuple(int(math.floor(v)) for v in (p[0], p[1], p[2] + 0.05))
        if W.block_id(*cell) and W.is_solid(*cell) and not k.endswith(("_look", "_target")):
            bad.append((k, "inside %s at %s" % (W.block_id(*cell), cell)))
    print("PLACES", len(SC.PLACES), "problems:", bad)
    for k in ("six_b1_pig_1", "six_b1_pig_2", "six_b1_pig_3", "home_pit_1", "home_pit_2", "home_pit_3", "home_pit_4",
              "home_pit_center", "home_rim_e", "home_rim_n", "bridge_player_look", "bridge_brute_look",
              "bridge_pillar_top_target", "six_gravel_1", "six_drop_boots", "six_flash_puff_home",
              "six_flash_boots_bridge", "six_flash_extra_treasure", "six_bridge_ingot_3", "home_landing_look"):
        print("   anchor %-26s %s yaw %s" % (k, C.A.get(k), C.Y.get(k)))
    print("   home_run_past", bas.paths.get("home_run_past"))

    # ---- routes of the stubs
    routes = {
        "gt04 runner": [(4.5, 24.0, 0.0), (4.6, 10.5, 0.0)],
        "gt19 runner": [(5.7, 29.5, 0.0)] + [tuple(p) for p in bas.paths["home_run_past"] if p[1] < 20.0],
        "pt05 runner": [(4.5, 13.0, 0.0), (4.3, 10.0, 0.0), tuple(C.P("boot_mark"))],
        "br11 runner": [(400.5, -3.0, 0.0), tuple(C.P("bridge_boot_mark"))],
    }
    for k, pts in routes.items():
        allh, allholes = [], []
        for a, b in zip(pts[:-1], pts[1:]):
            h, holes = seg_blocked(W if k != "pt05 runner" else bas.whole.world, a, b)
            allh += h
            allholes += holes
        print("ROUTE %-12s %s\n    blocked: %d %s\n    no floor: %d %s" % (k, pts, len(allh), allh[:4], len(allholes),
                                                                       allholes[:4]))
    # corridor blocks around the run-past start (lava channel)
    rows = []
    for y in (29, 25, 21):
        row = []
        for x in range(1, 8):
            row.append("%d:%s/%s" % (x, (W.block_id(x, y, -1) or "-")[:10], (W.block_id(x, y, 0) or "-")[:10]))
        rows.append((y, row))
    for y, row in rows:
        print("   corridor y=%d (z-1 / z0): %s" % (y, "  ".join(row)))

    # ---- the blackstone dropped by breaking.mine in pt06
    drop = bpy.data.objects.get("drop_blackstone_1")
    if drop is not None:
        for f in (389, 395, 410, 436, 500, 600, 700, 1100, 1300, 1400):
            scene.frame_set(f)
            print("   drop_blackstone_1 f%d at %s hidden=%s" % (f, tuple(round(v, 2) for v in drop.matrix_world.translation),
                                                              drop.hide_render))
        print("   in st.cast:", any(getattr(c, "object", None) is drop for c in st.cast.values()))

    # ---- lava flicker frame by frame
    lw = bas.lava["home_lava_wall_light"]
    vals = []
    for f in range(1110, 1290):
        scene.frame_set(f)
        vals.append(round(lw.data.energy, 1))
    exact = [1110 + i for i, v in enumerate(vals) if v == 1100.0]
    print("FLICKER 1110-1289: min %.1f max %.1f; frames exactly at base 1100: %d (%s ...)" % (
        min(vals), max(vals), len(exact), exact[:12]))
    print("   1110-1125:", vals[:16])
    print("   1166-1180:", vals[56:71])

    # ---- the match cut ears: per-frame change 1170..1176
    for name in ("piglin_gt1",):
        c = st.cast[name]
        obs = [c.root] + list(c.root.children_recursive)
        prev = None
        for f in range(1168, 1178):
            scene.frame_set(f)
            cur = {o.name: o.matrix_world.to_euler() for o in obs}
            if prev:
                d = max(max(abs(x - y) for x, y in zip(prev[n], cur[n])) for n in cur)
                print("   %s part rot change %d->%d: %.4f rad" % (name, f - 1, f, d))
            prev = cur

    # ---- helpers on scratch instances (keys read back)
    s = shots["gt03_guard"]
    f0, f1 = s.frame_start, s.frame_end
    pig = C.actor("piglin", "gt99")
    C.stand(s, pig, "gold_2", look="gold_target", idle=True, seed=3)
    scene.frame_set(f0)
    eye = Vector(pig.eye_point(f0)) if hasattr(pig, "eye_point") else pig.head.matrix_world.translation
    tgt = Vector(C.P("gold_target"))
    fwd = pig.head.matrix_world.to_3x3() @ Vector((0.0, -1.0, 0.0))
    ang = math.degrees(fwd.angle(tgt - eye))
    print("SCRATCH stand: head forward vs gold_target on f0: %.1f deg; root at %s" % (
        ang, tuple(round(v, 2) for v in pig.root.matrix_world.translation)))
    heads = set()
    for f in range(f0, f1 + 1, 3):
        scene.frame_set(f)
        heads.add(tuple(round(v, 3) for v in pig.head.matrix_world.to_euler()))
    print("   idle head poses over the shot:", len(heads), "| in_shot:", pig.name in st.in_shot[s.name])
    # visibility outside: finish() already ran, so a scratch actor added now is NOT hidden by Stage.finish
    scene.frame_set(100)
    print("   scratch actor visible on frame 100 (a shot it is not in; finish() ran before):", not pig.root.hide_render)

    # admire: the ingot in the LEFT hand
    s2 = shots["rw02_ingots"]
    b1 = st.cast["piglin_rw1"]
    scene.frame_set(s2.frame_start + 10)
    held = [o for o in b1.root.children_recursive if "ingot" in o.name.lower() and not o.hide_render]
    print("ADMIRE rw1 visible ingot objects:", [(o.name, o.parent.name if o.parent else None) for o in held][:4])
    if hasattr(b1, "item_point"):
        try:
            print("   item_point off-hand:", tuple(round(v, 2) for v in b1.item_point(s2.frame_start + 10, "off")),
                  "head:", tuple(round(v, 2) for v in b1.head.matrix_world.translation))
        except Exception as e:
            print("   item_point:", e)
    # world's rules guards
    for fn, arg in ((C.pit, shots["gt19_older"]), (C.pillar, shots["fl16_bridge"])):
        try:
            fn(arg)
            print("GUARD", fn.__name__, "did NOT refuse", arg.name)
        except ValueError as e:
            print("GUARD", fn.__name__, "refuses:", str(e)[:80])
    for role, tag in (("brute", "xx1"), ("wolf", "gt9")):
        try:
            C.actor(role, tag)
            print("ACTOR", role, tag, "accepted")
        except KeyError as e:
            print("ACTOR", role, tag, "refused:", e)
    # a fill with the same name and other numbers
    try:
        C.fill("gt_x", (1, 1, 1), 10, [shots["gt03_guard"]])
        C.fill("gt_x", (1, 1, 2), 10, [shots["gt04_runin"]])
        print("FILL same name, other pos: accepted (BAD)")
    except ValueError:
        print("FILL same name, other pos: refused (good)")
    # brute weapon / runner equipment objects
    for name in ("brute_gt", "piglin_gt1", "piglin_xbow_gt3", "runner_pt", "runner_br"):
        c = st.cast[name]
        kids = [o.name for o in c.root.children_recursive if any(k in o.name.lower() for k in (
            "axe", "sword", "crossbow", "boots", "pickaxe", "ingot", "item"))]
        print("EQUIP %-16s %s" % (name, kids[:8]))
    print("BOOTS of runner_pt:", [o.name for o in C.boots_of(st.cast["runner_pt"])])
    # what does the runner hold in pt09 / pt20 (after pt07's hold)?
    for f in (300, 440, 520, 575, 1300):
        scene.frame_set(f)
        r = st.cast["runner_pt"]
        vis = [o.name for o in bpy.data.objects if o.name.startswith(("held_", "item_")) and "runner_pt" in o.name
               and not o.hide_render]
        hv = getattr(r, "holding_at", None)
        try:
            h = hv(f) if hv else None
        except Exception as e:
            h = "err %s" % e
        print("   runner_pt f%d holding_at %s %s" % (f, h, vis[:3]))
    for f in (830, 900, 960):
        r = st.cast["runner_br"]
        try:
            print("   runner_br f%d holding_at %s crouching_at %s" % (f, r.holding_at(f), r.crouching_at(f)))
        except Exception as e:
            print("   runner_br", f, e)


if __name__ == "__main__":
    main()
