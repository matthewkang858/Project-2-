"""Independent checker probe for engine/sets.py + the village edit hook (numbers only, no render).

    $BPY -m tools.check_sets_probe hook      torches / doors / beds of a hook against the village's own
    $BPY -m tools.check_sets_probe hello     hello_set: twice, determinism, existing anchors and paths, instances
    $BPY -m tools.check_sets_probe digest    one line: digest of the hello village (compare across processes)
    $BPY -m tools.check_sets_probe import    importing engine.sets leaves bpy and blocks.World untouched
"""
import hashlib
import math
import sys


def _scene():
    from engine import quick

    scene = quick.reset()
    quick.setup(scene)
    return scene


def _light_sig(ob):
    d = ob.data
    return (d.type, round(d.energy, 5), tuple(round(c, 5) for c in d.color), round(d.shadow_soft_size, 5),
            bool(d.use_shadow), ob.get("mc_light"), bool(ob.visible_camera))


def _blocks_digest(v):
    w = v.world
    rows = sorted("%d,%d,%d,%s,%s" % (c[0], c[1], c[2], w._states[s][0], sorted(w._states[s][1].items()))
                  for c, s in w.blocks.items())
    return hashlib.sha1("\n".join(rows).encode()).hexdigest()[:16], len(rows)


def _mesh_digest(v):
    import numpy as np

    rows = []
    for ob in v.collection.all_objects:
        if ob.type != "MESH":
            continue
        me = ob.data
        co = np.empty(len(me.vertices) * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        # order-free: sort vertices
        co = np.sort(co.reshape(-1, 3).round(4), axis=0)
        rows.append("%d|%s|%s" % (len(me.polygons), hashlib.sha1(co.tobytes()).hexdigest()[:12],
                                  ",".join(sorted(m.name for m in me.materials if m))))
    rows.sort()
    return hashlib.sha1("\n".join(rows).encode()).hexdigest()[:16], len(rows)


def hook():
    from engine import village

    bad = []

    def check(label, ok, detail=""):
        print("%-4s %s %s" % ("OK" if ok else "FAIL", label, detail if (detail and not ok) else ""))
        if not ok:
            bad.append(label)

    plain = village.build_village(_scene(), seed=1)
    ref = {}
    for ob in plain.lantern_lights:
        ref.setdefault((ob.get("group"), ob.get("mc_light")), []).append(_light_sig(ob))
    hall_lantern = _light_sig(plain.lights["hall"][0])
    lamp_torch = _light_sig(plain.lights["lamp"][0])
    print("village lights: groups", {k: len(g) for k, g in plain.lights.items()})
    print("a lamp-post torch light:", lamp_torch)
    print("a hall lantern light:   ", hall_lantern)
    n_lamp = len(plain.lights["lamp"])
    seen = {}

    def edit(b):
        z = b.ground(-10, 40)
        seen["z"] = z
        b.clear_plants(-10, 40)
        b.clear_plants(-8, 40)
        b.torch((-10, 40, z), "torch", group="probe")
        b.w.set(-8, 40, z, "lantern", {"hanging": "false"})
        b.w.fill(-6, 40, z, -6, 40, z + 1, "cobblestone")
        b.w.set(-6, 39, z + 1, "wall_torch", {"facing": "south"})
        # a door in a little wall
        b.clear_plants(-13, 40), b.clear_plants(-12, 40), b.clear_plants(-14, 40)
        b.w.fill(-14, 40, z, -14, 40, z + 1, "oak_planks")
        b.w.fill(-12, 40, z, -12, 40, z + 1, "oak_planks")
        b.door("probe_door", (-13, 40, z), "south")
        b.clear_plants(-16, 40), b.clear_plants(-16, 41)
        b.bed("probe_bed", (-16, 40, z), "north", "red")
        # take away BOTH lit torches of one lamp post, and a village door
        lit = [t for t in b.torches if t[0] == "lamp"]
        seen["lamp_cells"] = [t[3] for t in lit]
        post = {}
        for g, bid, p, cell in lit:
            dx, dy = village._VEC[p["facing"]]
            post.setdefault((cell[0] - dx, cell[1] - dy), []).append(cell)
        first = sorted(post)[0]
        seen["post"] = (first, post[first])
        for cell in post[first]:
            b.w.set(cell[0], cell[1], cell[2], None)
        e = b.entries["house_b"]
        seen["door_cell"] = e["doors"][0]
        c = e["doors"][0]
        b.w.set(c[0], c[1], c[2], None)
        b.w.set(c[0], c[1], c[2] + 1, None)
        b.allow("house_b")
        b.allow("streets")
        b.strict = False                    # (removing a village door is reported as "missing door": see the result)
        seen["b"] = b

    v = village.build_village(_scene(), seed=1, edit=edit)
    z = seen["z"]
    pr = v.lights.get("probe", [])
    st = v.lights.get("set", [])
    check("b.torch light exists in its own group", len(pr) == 1)
    if pr:
        sig = _light_sig(pr[0])
        want = list(lamp_torch)
        base = float(pr[0]["base_energy"])
        print("     hook torch light:", sig, "base_energy", base)
        # a lamp-post torch is scaled 1.15; a plain one is 1.0
        check("hook torch = the village's torch light (same lamp type, colour, radius, shadow; energy x1.0 vs lamp x1.15)",
              sig[0] == want[0] and sig[2:] == tuple(want[2:]) and abs(sig[1] * 1.15 - want[1]) < 1e-3, (sig, want))
        check("hook torch is in Village.lantern_lights (Stage.lights scales it)", pr[0] in v.lantern_lights
              and "base_energy" in pr[0] and pr[0].get("group") == "probe")
    kinds = sorted(o.get("mc_light") for o in st)
    check("plain w.set lantern + wall_torch got lights in group 'set'", kinds == ["lantern", "torch"], kinds)
    for o in st:
        if o.get("mc_light") == "lantern":
            check("hook lantern = the village's lantern light", _light_sig(o) == hall_lantern, (_light_sig(o), hall_lantern))
    removed = len(seen["post"][1])
    check("lamp post with its %d torches removed: lamp lights %d -> %d" % (removed, n_lamp, len(v.lights["lamp"])),
          len(v.lights["lamp"]) < n_lamp)
    for ob in v.lantern_lights:
        c = tuple(int(math.floor(a)) for a in ob.location)
        if c in seen["post"][1]:
            check("no light left at the removed torch cell %s" % (c,), False)
    # doors
    check("hook door is a prop", "probe_door" in v.doors)
    check("removed house_b door has no prop any more", "house_b" not in v.doors, sorted(v.doors))
    w = v.world
    # is the hook door ALSO in the static mesh? (double geometry would z-fight): look for mesh vertices inside its cell
    import numpy as np
    inside = 0
    x0, y0 = -13, 40
    for ob in v.objects:
        me = ob.data
        co = np.empty(len(me.vertices) * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        m = (co[:, 0] > x0 + 0.01) & (co[:, 0] < x0 + 0.99) & (co[:, 1] > y0 - 0.01) & (co[:, 1] < y0 + 1.01) & \
            (co[:, 2] > z + 0.01) & (co[:, 2] < z + 1.99)
        if m.any():
            inside += int(m.sum())
            print("     static mesh %s has %d vertices inside the hook door's cells" % (ob.name, int(m.sum())))
    check("hook door is not doubled in the static mesh", inside == 0)
    check("hook door cells are passable for path checks", (-13, 40, z) in w.passable and (-13, 40, z + 1) in w.passable)
    check("hook bed registered", "probe_bed" in v.beds and "probe_bed" in v.anchors and "probe_bed" in v.yaws)
    hb = [k for k in v.beds if k.startswith("house_a")][0]
    check("hook bed entry has the keys of a village bed", sorted(v.beds["probe_bed"]) == sorted(v.beds[hb]),
          (sorted(v.beds["probe_bed"]), sorted(v.beds[hb])))
    print("     edit_problems:", v.edit_problems)
    # Stage.lights-like scaling
    v.set_lantern_energy(0.0, groups=["probe"])
    check("set_lantern_energy reaches the hook group", pr and pr[0].data.energy == 0.0 and pr[0].hide_render)
    on = v.only_lights_near((-10.5, 40.5, z), 6.0)
    print("     only_lights_near the probe: %d lights left on (%s)" % (len(on), sorted({o.get('group') for o in on})))
    print("[probe hook] %s" % ("all good" if not bad else "%d FAILED: %s" % (len(bad), bad)))
    return len(bad)


def hello():
    from engine import sets, village

    bad = []

    def check(label, ok, detail=""):
        print("%-4s %s %s" % ("OK" if ok else "FAIL", label, detail if (detail and not ok) else ""))
        if not ok:
            bad.append(label)

    plain = village.build_village(_scene(), seed=1)
    pa, pp, py_ = dict(plain.anchors), {k: list(p) for k, p in plain.paths.items()}, dict(plain.yaws)
    out = {}
    v = village.build_village(_scene(), seed=1, edit=lambda b: out.update(h=sets.hello_set(b), b=b))
    d1 = _blocks_digest(v)
    m1 = _mesh_digest(v)
    b = out["b"]
    moved = {k: (pa[k], v.anchors.get(k)) for k in pa if v.anchors.get(k) != pa[k]}
    check("every anchor of the plain village is unchanged", not moved, moved)
    movedp = [k for k in pp if v.paths.get(k) != pp[k]]
    check("every path of the plain village is unchanged", not movedp, movedp)
    # ... but do they still stand ON the ground? (the trail paves columns; set_ground re-levels)
    off = {}
    for k, p in pa.items():
        if k.endswith(("_target", "_center", "_cam", "_station", "_door")) or "bed" in k or p[1] < 24:
            continue
        wz = b.walk_z(p[0], p[1])
        if wz is not None and abs(wz - p[2]) > 1e-6:
            off[k] = (p, wz)
    check("old meadow anchors still at walking height", not off, off)
    offp = {}
    for k, pts in pp.items():
        for p in pts:
            if p[1] < 24:
                continue
            wz = b.walk_z(p[0], p[1])
            if wz is not None and abs(wz - p[2]) > 1e-6:
                offp.setdefault(k, []).append((p, wz))
    check("old path points beyond the gate still at walking height", not offp, offp)
    print("     exit_road:", [tuple(round(a, 2) for a in p) for p in v.paths.get("exit_road", [])])
    print("     meadow_far:", v.anchors.get("meadow_far"), "nitwit_idle:", v.anchors.get("nitwit_idle"))
    print("     road_to_forest:", [tuple(round(a, 2) for a in p) for p in v.paths["road_to_forest"]])
    # walking height along the new path, densely: any step up or down a character would take as a pop?
    pts = v.paths["road_to_forest"]
    steps = []
    for a, c in zip(pts, pts[1:]):
        n = max(2, int(math.dist(a[:2], c[:2]) * 4))
        for i in range(n + 1):
            x, y = a[0] + (c[0] - a[0]) * i / n, a[1] + (c[1] - a[1]) * i / n
            lin = a[2] + (c[2] - a[2]) * i / n
            wz = b.walk_z(x, y)
            if wz is None or abs(wz - lin) > 0.07:
                steps.append((round(x, 2), round(y, 2), round(lin, 3), wz))
    check("road_to_forest: the straight legs follow the ground within 1/16", not steps, steps[:6])
    pts = v.paths["pyramid_round"]
    steps = []
    for a, c in zip(pts, pts[1:]):
        n = max(2, int(math.dist(a[:2], c[:2]) * 4))
        for i in range(n + 1):
            x, y = a[0] + (c[0] - a[0]) * i / n, a[1] + (c[1] - a[1]) * i / n
            lin = a[2] + (c[2] - a[2]) * i / n
            wz = b.walk_z(x, y)
            if wz is None or abs(wz - lin) > 0.07:
                steps.append((round(x, 2), round(y, 2), round(lin, 3), wz))
    check("pyramid_round: the legs follow the ground within 1/16", not steps, steps[:6])
    print("     pyramid_round:", [tuple(round(a, 2) for a in p) for p in v.paths["pyramid_round"]])
    # CAMERA_LANE stays free of plants and blocks up to the tree line
    lane = getattr(village, "CAMERA_LANE", None)
    print("     CAMERA_LANE:", lane)
    w = v.world
    stuff = []
    for x in (-3, -2):
        for y in range(22, 58):
            g = b.ground(x, y)
            if w.get(x, y, g) is not None or w.get(x, y, g + 1) is not None:
                stuff.append((x, y, w.block_id(x, y, g), w.block_id(x, y, g + 1)))
    check("camera lane x -3..-2, y 22..57 is still empty", not stuff, stuff[:6])
    # no leaves of two kinds face to face, no plant inside a trunk column, nothing floating without reason
    mixed = 0
    for c, sid in w.blocks.items():
        bid = w._states[sid][0]
        if bid == "dark_oak_leaves":
            for dx, dy, dz in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                if w.block_id(c[0] + dx, c[1] + dy, c[2] + dz) == "oak_leaves":
                    mixed += 1
    check("no oak leaf face to face with a dark oak leaf", mixed == 0, mixed)
    # plants standing on something that is not grass / dirt (e.g. left hanging after set_ground)
    hang = []
    for c, sid in w.blocks.items():
        bid = w._states[sid][0]
        if bid in sets.PLANTS and c[1] > 24:
            props = w._states[sid][1]
            if bid == "tall_grass" and props.get("half") == "upper":
                below = w.block_id(c[0], c[1], c[2] - 1)
                if below != "tall_grass":
                    hang.append((c, bid, below))
                continue
            below = w.block_id(c[0], c[1], c[2] - 1)
            if below not in ("grass_block", "dirt", "podzol", "coarse_dirt"):
                hang.append((c, bid, below))
    check("every plant beyond the gate stands on grass or dirt", not hang, hang[:6])
    # terrain holes: every column in the set's box has a top block and is closed down to its lowest neighbour
    x0, y0, x1, y1 = out["h"]["forest"]["bounds"]
    holes = []
    for x in range(x0 - 3, x1 + 4):
        for y in range(y0 - 3, y1 + 4):
            g = b.ground(x, y)
            if g is None:
                continue
            if w.block_id(x, y, g - 1) not in ("grass_block", "dirt", "dirt_path"):
                holes.append((x, y, g, w.block_id(x, y, g - 1)))
                continue
            for ax, ay in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                a = b.ground(ax, ay)
                if a is not None and a < g and any(w.get(x, y, zz) is None for zz in range(a, g)):
                    holes.append((x, y, g, "open side to %s" % ((ax, ay),)))
    check("no holes in the terrain of the wood", not holes, holes[:6])
    # grass block under a log/sand: buried grass tops (the game turns them to dirt)
    buried = []
    for c, sid in w.blocks.items():
        if c[1] > 24 and w._states[sid][0] == "grass_block":
            up = w.block_id(c[0], c[1], c[2] + 1)
            if up in ("dark_oak_log", "oak_log", "sand", "dirt", "grass_block"):
                buried.append((c, up))
    print("     grass blocks with a full block on top (the game would show dirt): %d, e.g. %s" % (len(buried), buried[:5]))
    # determinism in-process
    out2 = {}
    v2 = village.build_village(_scene(), seed=1, edit=lambda b: out2.update(h=sets.hello_set(b)))
    check("hello_set twice in one process gives the same blocks", _blocks_digest(v2) == d1, (_blocks_digest(v2), d1))
    check("... and the same meshes", _mesh_digest(v2) == m1)
    # called twice inside one hook
    try:
        v3 = village.build_village(_scene(), seed=1, edit=lambda b: (sets.hello_set(b), sets.hello_set(b)))
        d3 = _blocks_digest(v3)
        check("hello_set called twice in one hook: same village as once", d3 == d1,
              "blocks %s vs %s, faces %d vs %d, problems %s" % (d3, d1, v3.face_count, v.face_count, v3.edit_problems))
    except Exception as e:                                    # noqa: BLE001
        check("hello_set called twice in one hook: same village or a clear refusal", False, "%s: %s" % (type(e).__name__, str(e)[:300]))
    # several instances at once
    try:
        def many(b):
            sets.hello_set(b)
            r1 = sets.sand_pyramid(b, (-20, 36), name="pyramid2")
            r2 = sets.floating_oak(b, (-30, 44), name="floating2", air=2, logs=3)
            r3 = sets.bare_oaks(b, [(30, 38), (33, 40)], name="bare2")
            out2["many"] = (r1, r2, r3)
        v4 = village.build_village(_scene(), seed=1, edit=many)
        check("a second pyramid / floating oak / bare group beside hello_set", v4.edit_problems == []
              and all(k in v4.anchors for k in ("pyramid2_beside", "floating2_under", "bare2_among"))
              and all(k in v4.sets for k in ("pyramid2", "floating2", "bare2", "pyramid", "floating_oak", "bare_oaks")),
              (v4.edit_problems, sorted(v4.sets)))
    except Exception as e:                                    # noqa: BLE001
        check("a second pyramid / floating oak / bare group beside hello_set", False, "%s: %s" % (type(e).__name__, str(e)[:300]))
    try:
        def two(b):
            sets.dark_forest(b, gap=(0.5, 58))
            sets.dark_forest(b, gap=(-55.5, 20), name="west", half_width=12, depth=12, rows=2, trail_from=None, oaks=0)
        v5 = village.build_village(_scene(), seed=1, edit=two)
        check("two forests in one village", v5.edit_problems == [] and "west_gap" in v5.anchors and "forest_gap" in v5.anchors,
              v5.edit_problems)
        print("     two forests: faces %d" % v5.face_count)
    except Exception as e:                                    # noqa: BLE001
        check("two forests in one village", False, "%s: %s" % (type(e).__name__, str(e)[:400]))
    for seed in (2, 3):
        try:
            v6 = village.build_village(_scene(), seed=seed, edit=lambda b: sets.hello_set(b))
            check("hello_set on village seed %d" % seed, v6.edit_problems == [], v6.edit_problems)
        except Exception as e:                                # noqa: BLE001
            check("hello_set on village seed %d" % seed, False, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("[probe hello] blocks %s meshes %s  %s" % (d1, m1, "all good" if not bad else "%d FAILED" % len(bad)))
    return len(bad)


def digest():
    from engine import sets, village

    v = village.build_village(_scene(), seed=1, edit=lambda b: sets.hello_set(b))
    print("DIGEST blocks %s meshes %s faces %d anchors %s" % (
        _blocks_digest(v), _mesh_digest(v), v.face_count,
        hashlib.sha1(repr(sorted(v.anchors.items())).encode()).hexdigest()[:12]))
    return 0


def imp():
    import bpy

    from engine import blocks

    before = (len(bpy.data.objects), len(bpy.data.meshes), len(bpy.data.materials), len(bpy.data.images),
              blocks.World._state_at, blocks.World.build)
    from engine import sets  # noqa: F401

    after = (len(bpy.data.objects), len(bpy.data.meshes), len(bpy.data.materials), len(bpy.data.images),
             blocks.World._state_at, blocks.World.build)
    ok = before == after
    print("%-4s importing engine.sets leaves bpy.data and blocks.World untouched %s" % ("OK" if ok else "FAIL", before[:4]))
    # building with the Environment must not patch the CLASS
    from engine import village

    cls_before = blocks.World._state_at
    village.build_village(_scene(), seed=1, edit=lambda b: sets.hello_set(b))
    ok2 = blocks.World._state_at is cls_before
    print("%-4s World._state_at on the class is unchanged after a build with baked light" % ("OK" if ok2 else "FAIL"))
    plain = village.build_village(_scene(), seed=1)
    d = _blocks_digest(plain)
    ok3 = d == ("%s" % d[0], 33508) and d[1] == 33508
    print("%-4s a plain village built AFTER a hello village in the same process: %s" % ("OK" if ok3 else "FAIL", d))
    return 0 if (ok and ok2 and ok3) else 1


if __name__ == "__main__":
    a = sys.argv[1:] or ["hook"]
    sys.exit({"hook": hook, "hello": hello, "digest": digest, "import": imp}[a[0]]())
