"""Checker probe: Mom's head vs the zombie's eyes frame by frame in gr21 (and the row's facings)."""
import math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bpy  # noqa
import render  # noqa
from mathutils import Vector  # noqa
ses = render.Session("twentyminutes")
res = ses.result
st, C, scene = res["stage"], res["context"], ses.scene
eye = Vector(C.zombie_eye)
for name in ("mom_gr", "narrator_gr", "librarian_gr", "cleric_gr"):
    c = st.cast[name]
    out = []
    for f in (1256, 1257, 1258, 1260, 1270, 1290, 1310, 1337):
        scene.frame_set(f)
        h = c.head
        fwd = h.matrix_world.to_3x3() @ Vector((0, -1, 0))
        to = eye - h.matrix_world.translation
        f2, t2 = Vector((fwd.x, fwd.y)), Vector((to.x, to.y))
        out.append("%d:%.0f" % (f, math.degrees(f2.angle(t2))))
    p = c.pos_at(1256)
    print(name, "pos %.2f %.2f yaw %.0f" % (p.x, p.y, math.degrees(c.yaw_at(1256))), " ".join(out))
