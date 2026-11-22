"""Render ad-hoc check views of the village set.

Usage (project root):  $BPY -m tools.village_probe name preset lens x,y,z tx,ty,tz [open_doors] [light_scale] ...
Several views can be given one after another (groups of 5-7 arguments separated by '--').
Writes out/test/set_probe_<name>.png
"""
import sys

from engine import quick, village


def main(argv):
    scene = quick.reset()
    quick.setup(scene)
    v = village.build_village(scene, seed=1)
    print("problems:", v.validate())
    groups, cur = [], []
    for a in argv:
        if a == "--":
            groups.append(cur)
            cur = []
        else:
            cur.append(a)
    if cur:
        groups.append(cur)
    import bpy

    for g in groups:
        name, preset, lens = g[0], g[1], float(g[2])
        pos = tuple(float(c) for c in g[3].split(","))
        tgt = tuple(float(c) for c in g[4].split(","))
        doors = g[5] if len(g) > 5 else "closed"
        scale = float(g[6]) if len(g) > 6 else 1.0
        for ob in [o for o in scene.objects if o.name.startswith("quick_")]:
            bpy.data.objects.remove(ob)
        quick.light(scene, preset)
        for d in v.doors:
            v.set_door(d, doors == "open")
        v.set_lantern_energy(scale)
        if len(g) > 7:
            for c in v.cutaways:
                v.cutaway(c, c in g[7].split(","))
        quick.camera(scene, pos, tgt, lens=lens)
        print("wrote", quick.render(scene, "set_probe_" + name))


if __name__ == "__main__":
    main(sys.argv[1:])
