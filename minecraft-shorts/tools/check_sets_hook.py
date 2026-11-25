"""Proof that village.build_village(scene, seed=1) WITHOUT a hook (edit=None) is still exactly the village of the
four finished films, after engine/village.py got its `edit=` hook (engine/sets.py builds film sets through it).

    $BPY -m tools.check_sets_hook                 # digests of the village as built now, against BASELINE below
    $BPY -m tools.check_sets_hook --film          # ... and frames of the finished film "The Nitwit": their scene
                                                  #   fingerprints (engine/stamp.py) against the stamps the FINAL
                                                  #   render wrote into out/frames/nitwit/meta.json
    $BPY -m tools.check_sets_hook --reference /path/to/old_village.py
                                                  # A/B inside one process against another copy of village.py
    $BPY -m tools.check_sets_hook --record        # print the digests (how BASELINE was made, before the hook)
    $BPY -m tools.check_sets_hook --hook          # what the hook promises, tested on a small camp built beyond the
                                                  #   old edge of the terrain: new terrain, a torch and a lantern
                                                  #   with their lights, a bed, an animated door, anchors, a path;
                                                  #   a village torch and a village bed taken away; and the check
                                                  #   that stops a block put into a house or onto a street;
                                                  #   a required door removed with and without b.allow; the
                                                  #   village's anchors / paths following paved or lowered ground
                                                  #   (--hook --still also renders out/test/sets_hook_camp.png)

What is compared (every part is a sha1 over a sorted, rounded text form):
    blocks     every block state of the World: (x, y, z, block id, properties)
    hidden     World.hidden_sides and World.passable (faces never drawn, walkable door cells)
    anchors    Village.anchors and Village.yaws          paths     Village.paths
    beds       Village.beds                              doors     door props: name, place, rotation, closed/open
    lights     every torch / lantern light: group, kind, place, energy
    meshes     every mesh object of the set: vertices, loops, polygons, uv, materials by name
    buildings  the placement boxes of the vanilla templates, the cutaway sections, the face count
Exit code 1 if anything differs.
"""
import hashlib
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Recorded with the village.py of commit 1642205 (sha1 56d0a0f29c88770d4540e3481dadf3694a0fa840), BEFORE the hook
# was added, by `$BPY -m tools.check_sets_hook --record`.
BASELINE = {
    "anchors": "95:1ed4f734cd6f43da5230",
    "beds": "28fd94e7f1555e3bcad3",
    "bell": "4d50b855b124d1d91c19",
    "blocks": "33508:a15110d443a348f8c54d",
    "buildings": "240d4f464e15d4501e08",
    "doors": "9:8143cebf125437fcea9b",
    "hidden": "1d80662a501242575bf5",
    "lights": "63:ccf8012f88adf66d59c1",
    "meshes": "132:e2707a143cddff940b79",
    "paths": "15:b94477d4cc002a48acd2",
}

FILM = "nitwit"
FILM_FRAMES = (1, 50, 80, 157, 240, 303)      # villager, smith, nitwit, hall, meadow (exit road), meadow


def _h(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:20]


def _r(v):
    if isinstance(v, (tuple, list)):
        return "(" + ",".join(_r(x) for x in v) + ")"
    if isinstance(v, float):
        return "%.5f" % (v + 0.0)
    if isinstance(v, dict):
        return "{" + ",".join("%s:%s" % (k, _r(v[k])) for k in sorted(v)) + "}"
    return str(v)


def digests(v):
    """{part: digest} of a built Village (see the module docstring)."""
    import numpy as np

    w = v.world
    out = {}
    rows = []
    for (x, y, z), sid in w.blocks.items():
        bid, props = w._states[sid]
        rows.append("%d,%d,%d,%s,%s" % (x, y, z, bid, sorted(props.items())))
    rows.sort()
    out["blocks"] = "%d:%s" % (len(rows), _h("\n".join(rows)))
    out["hidden"] = _h(_r(sorted(map(str, w.hidden_sides))) + _r(sorted(map(str, w.passable))))
    out["anchors"] = "%d:%s" % (len(v.anchors), _h(_r(v.anchors) + _r(v.yaws)))
    out["paths"] = "%d:%s" % (len(v.paths), _h(_r({k: [tuple(p) for p in pts] for k, pts in v.paths.items()})))
    out["beds"] = _h(_r(v.beds))
    doors = []
    for name in sorted(v.doors):
        d = v.doors[name]
        doors.append((name, tuple(d.matrix_world.translation), tuple(d.rotation_euler), d["closed_yaw"], d["open_angle"]))
    out["doors"] = "%d:%s" % (len(doors), _h(_r(doors)))
    lights = sorted((ob.get("group", ""), ob.get("mc_light", ""), tuple(ob.location), float(ob.data.energy),
                     float(ob["base_energy"])) for ob in v.lantern_lights)
    out["lights"] = "%d:%s" % (len(lights), _h(_r(lights)))
    meshes = []
    for ob in v.collection.objects:
        if ob.type != "MESH":
            continue
        me = ob.data
        co = np.empty(len(me.vertices) * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        li = np.empty(len(me.loops), dtype=np.int32)
        me.loops.foreach_get("vertex_index", li)
        uv = np.empty(len(me.loops) * 2, dtype=np.float32)
        if me.uv_layers:
            me.uv_layers[0].data.foreach_get("uv", uv)
        meshes.append("%s|%d|%s|%s|%s|%s|%s" % (
            ob.name, len(me.polygons), hashlib.sha1(co.tobytes()).hexdigest()[:12],
            hashlib.sha1(li.tobytes()).hexdigest()[:12], hashlib.sha1(uv.tobytes()).hexdigest()[:12],
            ",".join(m.name if m else "-" for m in me.materials), _r(tuple(ob.matrix_world.translation))))
    meshes.sort()
    out["meshes"] = "%d:%s" % (len(meshes), _h("\n".join(meshes)))
    b = {k: pl.bounds for k, pl in v.buildings.items()}
    cut = {k: sorted(o.name for o in obs) for k, obs in v.cutaways.items()}
    out["buildings"] = _h(_r(b) + _r(cut) + str(v.face_count) + _r(v.bounds) + _r(v.terrain_bounds))
    out["bell"] = _h(_r(tuple(v.bell.parent.location)) + v.bell.name)
    return out


def build(module=None):
    """Build the village with no hook in an empty scene (module = another village module to build with)."""
    from engine import quick, village

    scene = quick.reset()
    quick.setup(scene)
    return (module or village).build_village(scene, seed=1)


def load_reference(path):
    """Import another copy of village.py as engine._village_reference (it uses the same engine package)."""
    spec = importlib.util.spec_from_file_location("engine._village_reference", path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "engine"
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def film_frames():
    """Scene fingerprints of FILM_FRAMES of the finished film, now, against the stamps of its final render."""
    import render as R

    meta = json.load(open(os.path.join(ROOT, "out", "frames", FILM, "meta.json")))
    ses = R.Session(FILM)
    ses.configure(R.FINAL_RES, R.FINAL_SAMPLES, R.FINAL_THREADS, None)
    bad = 0
    for f in FILM_FRAMES:
        rec = meta["frames"][str(f)]
        if rec["s"] != ses.settings_key():
            print("frame %d was stamped at other settings (%s)" % (f, rec["s"]))
            bad += 1
            continue
        now = ses.fingerprint(f)
        diff = "".join(k for k in "gcol" if now["parts"][k] != rec["parts"][k])
        ok = now["fp"] == rec["fp"]
        bad += not ok
        print("%-4s %s frame %3d  fingerprint now %s  stamped by the final render %s%s" % (
            "OK" if ok else "FAIL", FILM, f, now["fp"], rec["fp"], "" if ok else "  differing parts: " + diff))
    return bad


def hook_test(still=False):
    """The promises of build_village(edit=...) (engine/village.py: FILM SETS), one by one. Returns failures.
    still=True also renders the camp to out/test/sets_hook_camp.png (quick stage, dusk-like light) to look at."""
    from engine import props, quick, village

    bad = []

    def check(label, ok, detail=""):
        print("%-4s %s%s" % ("OK" if ok else "FAIL", label, (" " + str(detail)) if detail and not ok else ""))
        if not ok:
            bad.append(label)

    seen = {}

    def camp(b):
        seen["trees"] = [(t["kind"], t["where"], len(t["logs"]), len(t["leaves"])) for t in b.trees]
        seen["rng"] = (float(b.rng_for("a").random()), float(b.rng_for("a").random()), float(b.rng_for("b").random()))
        seen["before"] = (b.ground(64, 78), b.ground(64, 90), b.ground(200, 0))
        new = b.extend_terrain(56, 70, 72, 96)                # across the disc's rim, the square's edge (y 84) and beyond
        seen["new"] = len(new)
        seen["plants"] = sum(1 for (x, y) in new if b.w.get(x, y, b.ground(x, y)) is not None)
        z = b.ground(64, 90)
        for x in range(60, 69):                               # a level pad of 9 x 5 beyond the square
            for y in range(88, 93):
                b.set_ground(x, y, z)
        seen["pad"] = {b.ground(x, y) for x in range(60, 69) for y in range(88, 93)} == {z}
        b.torch((64, 90, z), "torch", group="camp")
        b.w.set(66, 90, z, "lantern", {"hanging": "false"})   # a plain set: the hook finds it and lights it
        b.bed("camp_bed", (62, 90, z), "north", "red")
        b.w.fill(60, 92, z, 60, 92, z + 1, "oak_planks")
        b.w.fill(62, 92, z, 62, 92, z + 1, "oak_planks")
        b.door("camp_door", (61, 92, z), "south")
        b.anchor("camp", (63.5, 88.5), yaw=0.0)
        b.path("to_camp", [(60.5, 80.5), (63.5, 88.5)])
        seen["tree"] = b.tree(70, 74, b.rng_for("camp tree"), "camp")
        # take one lamp-post torch and house_b's bed away (meant: allowed)
        lamp = next(t for t in b.torches if t[0] == "lamp")
        seen["lamp"] = lamp
        b.w.set(lamp[3][0], lamp[3][1], lamp[3][2], None)
        bed = b.v.beds["house_b_bed_1"]
        for k in ("foot", "head"):
            c = tuple(int(a // 1) for a in bed[k])
            b.w.set(c[0], c[1], c[2], None)
        b.allow("house_b")
        seen["z"] = z
        seen["b"] = b

    scene = quick.reset()
    quick.setup(scene)
    plain = village.build_village(scene, seed=1)
    n_lights, n_lamp = len(plain.lantern_lights), len(plain.lights["lamp"])
    scene = quick.reset()
    quick.setup(scene)
    v = village.build_village(scene, seed=1, edit=camp)
    b, z = seen["b"], seen["z"]
    places = [t[1] for t in seen["trees"]]
    check("b.trees lists the village's oaks (8 in the village, 70 in the ring around it, 5 in the meadow)",
          (places.count("village"), places.count("ring"), places.count("meadow"), len(places)) == (8, 70, 5, 83)
          and all(t[0] == "oak" and 4 <= t[2] <= 6 and t[3] > 30 for t in seen["trees"]), len(seen["trees"]))
    check("b.rng_for(tag): the same tag gives the same numbers, another tag others",
          seen["rng"][0] == seen["rng"][1] != seen["rng"][2])
    check("b.ground is None beyond the terrain before, a height after extend_terrain",
          seen["before"][1] is None and seen["before"][2] is None and v.ground(64, 90) == z, seen["before"])
    check("extend_terrain made %d new columns, %d of them with a plant" % (seen["new"], seen["plants"]),
          seen["new"] > 150 and 5 < seen["plants"] < seen["new"] // 2)
    check("set_ground levelled the pad", seen["pad"])
    w = v.world
    holes = [(x, y) for x in range(56, 73) for y in range(70, 97) if b.ground(x, y) is not None
             and w.block_id(x, y, b.ground(x, y) - 1) not in ("grass_block", "dirt", "dirt_path")]
    gaps = []
    for x in range(56, 73):                                    # no see-through steps: every column is filled down to
        for y in range(70, 97):                                # its lowest neighbour
            h = b.ground(x, y)
            if h is None:
                continue
            for ax, ay in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                a = b.ground(ax, ay)
                if a is not None and a < h and any(w.get(x, y, zz) is None for zz in range(a, h)):
                    gaps.append((x, y))
    check("the new terrain has a surface block everywhere and no holes in its steps", not holes and not gaps,
          (holes[:3], gaps[:3]))
    camp_l, set_l = v.lights.get("camp", []), v.lights.get("set", [])
    check("b.torch: one torch light in group 'camp' at the flame",
          len(camp_l) == 1 and camp_l[0]["mc_light"] == "torch"
          and tuple(round(a, 3) for a in camp_l[0].location) == tuple(round(a, 3) for a in
                                                                       props.flame_position((64, 90, z), "torch", {})))
    check("a lantern block set with b.w.set got its light too (group 'set', kind lantern)",
          len(set_l) == 1 and set_l[0]["mc_light"] == "lantern")
    check("the lamp-post torch that was taken out lost its light (lamp group %d -> %d or the same if it was unlit)"
          % (n_lamp, len(v.lights["lamp"])), len(v.lights["lamp"]) in (n_lamp - 1, n_lamp)
          and w.get(*seen["lamp"][3]) is None)
    check("lights in all: %d + 2 new - the lamp's" % n_lights, len(v.lantern_lights) in (n_lights + 1, n_lights + 2))
    check("b.bed: anchor, yaw and Village.beds entry", "camp_bed" in v.beds and "camp_bed" in v.anchors
          and "camp_bed" in v.yaws and w.block_id(62, 90, z) == "red_bed" and w.block_id(62, 91, z) == "red_bed")
    check("house_b's bed was taken out: its anchor and beds entry are gone",
          "house_b_bed_1" not in v.beds and "house_b_bed_1" not in v.anchors)
    d = v.doors.get("camp_door")
    ok = d is not None
    if ok:
        v.door_open("camp_door", 10, open=True, frames=5)
        scene.frame_set(10)
        a0 = d.rotation_euler[2]
        scene.frame_set(15)
        ok = abs(d.rotation_euler[2] - a0) > 1.0
    check("b.door: an animated door prop that door_open() swings (and the houses' doors are all still there)",
          ok and all(k in v.doors for k in plain.doors), sorted(v.doors))
    check("b.anchor / b.path: on the ground of the new terrain",
          v.anchors.get("camp") == (63.5, 88.5, float(z)) and v.paths["to_camp"][-1] == (63.5, 88.5, float(z))
          and v.yaws.get("camp") == 0.0)
    check("b.tree planted a recorded oak", seen["tree"] is not None and seen["tree"]["where"] == "camp"
          and w.block_id(70, 74, seen["tree"]["base"]) == "oak_log")
    check("no problems reported, validate() clean", v.edit_problems == [] and v.validate() == [],
          (v.edit_problems, v.validate()))
    if still:
        v.set_door("camp_door", True)
        sun = quick.light(scene, "night")
        sun.data.energy = 1.2
        quick.camera(scene, (57.5, 83.0, z + 4.5), (64.0, 90.5, z + 0.6), lens=26)
        print("wrote", quick.render(scene, "sets_hook_camp"))

    def raises(label, edit, text):
        scene = quick.reset()
        quick.setup(scene)
        try:
            village.build_village(scene, seed=1, edit=edit)
            check(label, False, "no error")
        except ValueError as e:
            check(label, text in str(e), str(e)[:200])

    raises("a block put on the exit road stops the build", lambda b: b.w.set(0, 15, 0, "sand"), "on the streets")
    raises("a block put inside house_a stops the build", lambda b: b.w.set(14, -10, 2, "sand"), "inside house_a")
    raises("a tree planted across a path stops the build (path blocked)",
           lambda b: b.tree(0, 40, b.rng_for("x"), "x"), "blocked")
    def buried(b):
        w = b.w
        c = next(c for c, sid in sorted(w.blocks.items()) if w._states[sid][0] == "cobblestone"
                 and w.is_solid(c[0], c[1], c[2] + 1))
        b.anchor("oops", (c[0] + 0.5, c[1] + 0.5, float(c[2])))

    raises("an anchor inside a block stops the build", buried, "anchor oops")
    raises("a duplicate anchor name is refused", lambda b: _dup(b), "exists")

    def meant(b):
        b.allow("streets")
        b.allow((10, -14, 20, -6))
        b.w.set(0, 15, -1, "dirt")                             # the road's own block replaced (still walkable)
        b.w.set(14, -10, 4, "sand")
        b.strict = False

    scene = quick.reset()
    quick.setup(scene)
    v2 = village.build_village(scene, seed=1, edit=meant)
    check("with b.allow the same edits pass", v2.edit_problems == [], v2.edit_problems)

    # a required door taken out on purpose: its prop is gone and nothing is "missing"; without b.allow it is a problem
    def door_cells(b):
        return [c for c in b.entries["house_b"]["doors"] for c in ((c[0], c[1], c[2]), (c[0], c[1], c[2] + 1))]

    def no_door(b):
        b.allow("house_b")
        for c in door_cells(b):
            b.w.set(c[0], c[1], c[2], None)

    scene = quick.reset()
    quick.setup(scene)
    v3 = village.build_village(scene, seed=1, edit=no_door)
    check("a required door removed with b.allow: no prop, not 'missing', the other doors untouched",
          "house_b" not in v3.doors and v3.edit_problems == [] and v3.validate() == []
          and v3.removed_doors == {"house_b"} and "house_a" in v3.doors and "house_c" in v3.doors,
          (sorted(v3.doors), v3.edit_problems, v3.removed_doors))
    raises("the same door removed without b.allow stops the build",
           lambda b: [b.w.set(c[0], c[1], c[2], None) for c in door_cells(b)], "inside house_b")

    # the village's own anchors and paths follow ground the hook paves or re-levels under them
    def worn(b):
        b.pave(0, 46)                                          # under meadow_far and a node of exit_road
        b.set_ground(0, 54, -1)                                # one block down under the last node of exit_road
        for c in ((-1, 54), (1, 54), (0, 53), (0, 55)):
            b.set_ground(c[0], c[1], -1)
        b.path("nitwit_leaves", [(p[0], p[1]) for p in b.v.paths["nitwit_leaves"]], replace=True)
        seen["walk"] = (b.walk_z(0.5, 46.0), b.walk_z(0.8, 54.0))
        b.strict = False

    scene = quick.reset()
    quick.setup(scene)
    v4 = village.build_village(scene, seed=1, edit=worn)
    far, last = v4.anchors["meadow_far"], v4.paths["exit_road"][-1]
    check("meadow_far and exit_road follow a paved / lowered column (and say so)",
          abs(far[2] - seen["walk"][0]) < 1e-6 and abs(far[2] + 0.0625) < 1e-6 and abs(last[2] - seen["walk"][1]) < 1e-6
          and abs(last[2] + 1.0) < 1e-6 and "meadow_far" in v4.regrounded and "path exit_road" in v4.regrounded,
          (far, last, seen["walk"], v4.regrounded))
    check("a path the hook registers again is not touched twice, and anchors off the ground stay",
          "path nitwit_leaves" not in v4.regrounded and abs(v4.paths["nitwit_leaves"][-1][2] + 1.0) < 1e-6
          and all(v4.anchors[k] == plain.anchors[k] for k in plain.anchors if k != "meadow_far"),
          v4.regrounded)
    return bad


def _dup(b):
    try:
        b.anchor("bell", (0.5, 0.5))
    except KeyError as e:
        raise ValueError(str(e))


def main(argv):
    bad = 0
    if "--hook" in argv:
        bad = len(hook_test("--still" in argv))
        print("[check_sets_hook] hook promises: %s" % ("all kept" if not bad else "%d FAILED" % bad))
        return 1 if bad else 0
    if "--reference" in argv:
        ref = load_reference(argv[argv.index("--reference") + 1])
        a = digests(build(ref))
        b = digests(build())
        for k in sorted(a):
            ok = a[k] == b[k]
            bad += not ok
            print("%-4s %-10s reference %s  now %s" % ("OK" if ok else "FAIL", k, a[k], b[k]))
    else:
        d = digests(build())
        if "--record" in argv:
            print("BASELINE = " + json.dumps(d, indent=4, sort_keys=True))
            return 0
        for k in sorted(d):
            ok = BASELINE.get(k) == d[k]
            bad += not ok
            print("%-4s %-10s recorded %s  now %s" % ("OK" if ok else "FAIL", k, BASELINE.get(k), d[k]))
    if "--film" in argv:
        bad += film_frames()
    print("[check_sets_hook] %s" % ("the village without a hook is unchanged" if not bad else "%d DIFFERENCES" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
