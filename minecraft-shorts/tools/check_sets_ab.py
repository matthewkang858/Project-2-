"""Independent checker probe (not the author's): village with edit=None against the PRE-HOOK village.py.

    $BPY -m tools.check_sets_ab ab /path/to/village_prehook.py     exact A/B in one process (no digests)
    $BPY -m tools.check_sets_ab film <film> f1 f2 ...              fingerprints now vs the final render's meta.json
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(path):
    spec = importlib.util.spec_from_file_location("engine._village_prehook_chk", path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "engine"
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _snapshot(v):
    import numpy as np

    w = v.world
    out = {}
    out["blocks"] = {c: (w._states[sid][0], tuple(sorted(w._states[sid][1].items()))) for c, sid in w.blocks.items()}
    out["hidden"] = set(map(str, w.hidden_sides))
    out["passable"] = set(map(str, w.passable))
    out["anchors"] = dict(v.anchors)
    out["yaws"] = dict(v.yaws)
    out["paths"] = {k: [tuple(p) for p in pts] for k, pts in v.paths.items()}
    out["beds"] = json.dumps(v.beds, sort_keys=True, default=str)
    lights = []
    for ob in v.lantern_lights:
        d = ob.data
        lights.append((ob.get("group", ""), ob.get("mc_light", ""), tuple(round(a, 6) for a in ob.matrix_world.translation),
                       d.type, round(d.energy, 6), tuple(round(c, 6) for c in d.color), round(d.shadow_soft_size, 6),
                       bool(d.use_shadow), round(float(ob.get("base_energy", -1)), 6), bool(ob.hide_render)))
    out["lights"] = sorted(lights)
    out["light_groups"] = {k: len(g) for k, g in v.lights.items()}
    meshes = {}
    for ob in v.collection.all_objects:
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
        mi = np.empty(len(me.polygons), dtype=np.int32)
        me.polygons.foreach_get("material_index", mi)
        meshes[ob.name] = (co.tobytes(), li.tobytes(), uv.tobytes(), mi.tobytes(),
                           tuple(m.name if m else "-" for m in me.materials),
                           tuple(round(a, 6) for row in ob.matrix_world for a in row), bool(ob.hide_render),
                           ob.parent.name if ob.parent else None)
    out["meshes"] = meshes
    out["doors"] = {k: (tuple(round(a, 6) for row in d.matrix_world for a in row), d.get("closed_yaw"),
                        d.get("open_angle")) for k, d in v.doors.items()}
    out["misc"] = (v.face_count, tuple(v.bounds), tuple(v.terrain_bounds), sorted(v.buildings),
                   {k: tuple(pl.bounds) for k, pl in v.buildings.items()}, sorted(v.cutaways),
                   v._height.tobytes())
    out["objects"] = sorted((o.name, o.type) for o in v.collection.all_objects)
    return out


def ab(path):
    from engine import quick, village

    old = _load(path)
    scene = quick.reset()
    quick.setup(scene)
    a = _snapshot(old.build_village(scene, seed=1))
    scene = quick.reset()
    quick.setup(scene)
    b = _snapshot(village.build_village(scene, seed=1))
    scene = quick.reset()
    quick.setup(scene)
    c = _snapshot(village.build_village(scene, seed=1, bed_colors={"house_a_bed_2": "red"}))
    scene = quick.reset()
    quick.setup(scene)
    d = _snapshot(old.build_village(scene, seed=1, bed_colors={"house_a_bed_2": "red"}))
    bad = 0
    for label, p, q in (("default", a, b), ("red bed", d, c)):
        for k in sorted(p):
            same = p[k] == q[k]
            bad += not same
            size = len(p[k]) if hasattr(p[k], "__len__") else 1
            print("%-4s [%s] %-12s %s items" % ("OK" if same else "FAIL", label, k, size))
            if not same and isinstance(p[k], dict):
                ka, kb = set(p[k]), set(q[k])
                print("     only old:", sorted(ka - kb)[:5], "only new:", sorted(kb - ka)[:5],
                      "differ:", [x for x in sorted(ka & kb, key=str) if p[k][x] != q[k][x]][:5])
    print("[check_sets_ab] %s" % ("IDENTICAL to the pre-hook village" if not bad else "%d DIFFERENCES" % bad))
    return bad


def film(name, frames):
    import render as R

    meta = json.load(open(os.path.join(ROOT, "out", "frames", name, "meta.json")))
    ses = R.Session(name)
    ses.configure(R.FINAL_RES, R.FINAL_SAMPLES, R.FINAL_THREADS, None)
    bad = 0
    for f in frames:
        rec = meta["frames"].get(str(f))
        if rec is None:
            print("no stamp for frame", f)
            continue
        if rec["s"] != ses.settings_key():
            print("frame %d stamped at other settings %s" % (f, rec["s"]))
            bad += 1
            continue
        now = ses.fingerprint(f)
        diff = "".join(k for k in "gcol" if now["parts"][k] != rec["parts"][k])
        ok = now["fp"] == rec["fp"]
        bad += not ok
        print("%-4s %s frame %3d now %s stamped %s %s" % ("OK" if ok else "FAIL", name, f, now["fp"], rec["fp"],
                                                        "" if ok else "differs in: " + diff))
    print("[check_sets_ab] film %s: %s" % (name, "fingerprints unchanged" if not bad else "%d DIFFER" % bad))
    return bad


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "ab":
        sys.exit(1 if ab(a[1]) else 0)
    if a and a[0] == "film":
        sys.exit(1 if film(a[1], [int(x) for x in a[2:]]) else 0)
    print(__doc__)
