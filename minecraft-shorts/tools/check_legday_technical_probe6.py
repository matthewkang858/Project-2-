"""Checker probe 6: the buckets of pn05 / pn06 (animals.hand_item / milk) frame by frame."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bpy
import render
ses = render.Session("legday", sky="gold")
scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
for name, frames in (("zuri_pn2", range(299, 349, 3)), ("zuri_pn3", range(349, 390, 4))):
    c = st.cast[name]
    obs = [o for o in bpy.data.objects if ("bucket" in o.name) and (name in o.name or (o.parent and name in o.parent.name))]
    print(name, sorted(o.name for o in obs))
    for f in frames:
        scene.frame_set(f)
        print("  %d %s" % (f, [o.name.replace(name, "") for o in obs if not o.hide_render]))
