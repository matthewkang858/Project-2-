"""Checker probe: gm12 item visibility vs the words, and sq04_tilt's focus distance at the end of the rack."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bpy  # noqa
import render  # noqa
ses = render.Session("twentyminutes")
st, scene = ses.result["stage"], ses.scene
for name in ("iron_ingot_gm", "poppy_gm"):
    it = st.cast[name]
    obs = [o for o in it.objects() if o.type == "MESH"] if hasattr(it, "objects") else []
    seq = []
    for f in range(708, 772):
        scene.frame_set(f)
        seq.append("1" if any(not o.hide_render for o in obs) else ".")
    print("%-14s 708..771 %s" % (name, "".join(seq)))
for f in list(range(212, 232)):
    scene.frame_set(f)
    cam = scene.camera
    d = cam.data.dof
    fo = d.focus_object
    dist = (fo.matrix_world.translation - cam.matrix_world.translation).length if fo else d.focus_distance
    print("f%d cam %s focus %.2f" % (f, cam.name, dist))
