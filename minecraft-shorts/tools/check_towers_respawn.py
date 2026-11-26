"""Checker probe (engine/towers.py review): a slide cut short by the next shot, then a new spawn there."""
import bpy
from engine import mobs, quick, towers, village


def shown(scene, g, f):
    scene.frame_set(f)
    return any(not ob.hide_render for ob in g.objects() if ob.type == "MESH")


scene = quick.reset()
quick.setup(scene)
v = village.build_village(scene, seed=1, edit=lambda b: towers.iron_farm(b))
fm = towers.farm(v)
g = mobs.make_iron_golem("golem")
fm.golem_spawn(g, 3)
r = fm.golem_slide(g, 7)
print("slide A: frame %s edge %s gone %s end %s" % (r["frame"], r["edge"], r["gone"], r["frame_end"]))
fm.golem_spawn(g, 59, pos=(-26.8, 22.1, 10.0), empty_from=49)
e = fm.golem_step(g, 73)
print("events", fm._golem_events)
for f in (48, 49, 58, 59, 60, 70, 80, 86, 87, 88, 95, 100, 110):
    p = g.pos_at(f)
    print("frame %3d shown %-5s pos (%.2f, %.2f, %.2f)" % (f, shown(scene, g, f), p.x, p.y, p.z))
