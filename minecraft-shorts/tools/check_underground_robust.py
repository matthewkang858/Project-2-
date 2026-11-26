"""Checker: robustness of engine/underground.py (no rendering).

    $BPY -m tools.check_underground_robust

1. importing the module leaves the scene / bpy.data untouched;
2. the village outside the set's footprint is the same as the plain seed-1 village (blocks, anchors, paths, lights);
3. building it twice in one process gives the same World and anchors (with a factory reset between, and twice into
   the same scene without one);
4. what the set's objects are and which of them a Stage can hide.
"""
import math
import sys

import bpy


def counts():
    return {k: len(getattr(bpy.data, k)) for k in ("objects", "meshes", "materials", "images", "lights", "collections",
                                                    "actions", "node_groups")}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def main():
    scene = reset()
    c0 = counts()
    from engine import underground as U   # noqa: F401
    c1 = counts()
    print("import: bpy.data counts unchanged:", c0 == c1, c0 if c0 != c1 else "")

    from engine import village
    v0 = village.build_village(scene, seed=1)
    w0 = dict((p, v0.world._states[s]) for p, s in v0.world.blocks.items())
    a0, p0 = dict(v0.anchors), {k: list(x) for k, x in v0.paths.items()}
    l0 = sorted((round(o.location.x, 2), round(o.location.y, 2), round(o.location.z, 2), o.get("group", ""))
                for o in v0.lantern_lights)
    f0 = v0.face_count

    scene = reset()
    v1, ug = U.build_village(scene, seed=1)
    w1 = dict((p, v1.world._states[s]) for p, s in v1.world.blocks.items())
    x0, y0, z0, x1, y1, z1 = U.ROCK

    def in_set(p):
        if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and z0 <= p[2] <= z1:
            return True
        return False

    diff = [p for p in set(w0) | set(w1) if w0.get(p) != w1.get(p)]
    outside = [p for p in diff if not in_set(p)]
    print("blocks changed: %d, outside the ROCK box: %d" % (len(diff), len(outside)))
    by = {}
    for p in outside:
        key = (w0.get(p, ("air",))[0], w1.get(p, ("air",))[0])
        by.setdefault(key, []).append(p)
    for k, ps in sorted(by.items(), key=lambda kv: -len(kv[1])):
        xs = [p[0] for p in ps]
        ys = [p[1] for p in ps]
        zs = [p[2] for p in ps]
        print("   %-40s %3d cells  x %d..%d y %d..%d z %d..%d" % ("%s -> %s" % k, len(ps), min(xs), max(xs), min(ys),
                                                                   max(ys), min(zs), max(zs)))
    # anchors / paths of the plain village
    moved = {k: (a0[k], v1.anchors.get(k)) for k in a0 if v1.anchors.get(k) is None or
             math.dist(a0[k], v1.anchors[k]) > 1e-6}
    print("village anchors moved or gone: %d %s" % (len(moved), list(moved.items())[:6]))
    pm = [k for k in p0 if k not in v1.paths or len(p0[k]) != len(v1.paths[k]) or
          any(math.dist(a, b) > 1e-6 for a, b in zip(p0[k], v1.paths[k]))]
    print("village paths changed: %s" % pm)
    l1 = sorted((round(o.location.x, 2), round(o.location.y, 2), round(o.location.z, 2), o.get("group", ""))
                for o in v1.lantern_lights)
    new_l = [l for l in l1 if l not in l0]
    gone_l = [l for l in l0 if l not in l1]
    print("lights: %d plain, %d with the set (%d new, %d gone)" % (len(l0), len(l1), len(new_l), len(gone_l)))
    print("faces: plain %d, with the set %d (+%d)" % (f0, v1.face_count, v1.face_count - f0))
    # what the set adds as objects and whether a Stage can hide them
    sets_objs = [o for o in bpy.data.objects if o.name.startswith(("ug_", "light_ug"))]
    print("objects named ug_*: %d" % len(sets_objs), sorted(o.name for o in sets_objs)[:30])
    cut = {k: len(v1.cutaways.get(k, [])) for k in U.CUTAWAYS}
    print("cutaway objects:", cut)

    # twice in one process, with a reset
    scene = reset()
    v2, ug2 = U.build_village(scene, seed=1)
    w2 = dict((p, v2.world._states[s]) for p, s in v2.world.blocks.items())
    print("rebuilt after reset: same World %s, same anchors %s, same faces %s" % (
        w2 == w1, dict(v2.anchors) == dict(v1.anchors), v2.face_count == v1.face_count))
    mats = sorted(m.name for m in bpy.data.materials if "|ug" in m.name)
    print("baked materials after rebuild: %d (names unique: %s)" % (len(mats), len(mats) == len(set(mats))))
    # twice into the same scene without a reset
    try:
        v3, ug3 = U.build_village(scene, seed=1)
        w3 = dict((p, v3.world._states[s]) for p, s in v3.world.blocks.items())
        print("second build into the same scene: same World %s, faces %d vs %d, door objects %s / %s" % (
            w3 == w1, v3.face_count, v1.face_count, [o.name for o in ug3.door.objects][:3],
            [o.name for o in ug2.door.objects][:3]))
    except Exception as ex:                     # noqa: BLE001
        print("second build into the same scene FAILED: %r" % ex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
