"""Reviewer's probe: the bare arrow model (tip along +X) seen from the side and from above, plus the item sprite of
the arrow (item/arrow) for comparison, rendered flat-lit. out/test/check_hostiles_arrowview.png"""
import math
import bpy
from mathutils import Vector
from engine import hostiles, quick, mcassets as mc

scene = quick.reset()
quick.setup(scene, (480, 240), 8, 2)
quick.light(scene, "day")
a = hostiles.arrow_object("a")                     # tip +X
a.location = (0, 0, 0.5)
b = hostiles.arrow_object("b")
b.location = (0, 0, -0.1)
b.rotation_euler = (math.radians(90), 0, 0)        # roll 90 about the shaft
it = mc.item_object("arrow")
it.location = (0, 0.0, -0.75)
it.rotation_euler = (math.radians(90), 0, math.radians(0))
quick.camera(scene, (0.0, -3.0, 0.0), (0.0, 0.0, 0.0), 50, 16)
print(quick.render(scene, "check_hostiles_arrowview"))
for v in (a,):
    xs = [ (a.matrix_world @ Vector(p)).x for p in a.bound_box]
    print("arrow x extent", min(xs), max(xs))
