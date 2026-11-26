"""Checker probe: the wall log and the bx24 / bx23 / sq03 key frames (no render). $BPY -m tools.check_twoapples_story_wall"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bpy  # noqa: E402
from films import twoapples as T  # noqa: E402
out = T.build(bpy.context.scene, sky="under")
C = out["context"]
print("WALL LOG", C.wall_log)
print("MEMO", {k: v for k, v in C.memo.items() if k.startswith(("tu_", "bx", "cu_"))})
for nm in ("ta_slot_strip_bx24_kept", "ta_doorway_glow_bx24_kept"):
    ob = bpy.data.objects.get(nm)
    if ob is not None and ob.data.animation_data and ob.data.animation_data.action:
        for fc in ob.data.animation_data.action.fcurves:
            print(nm, fc.data_path, [(int(k.co[0]), round(k.co[1], 1)) for k in fc.keyframe_points])
    else:
        print(nm, "static" if ob else "missing", ob.data.energy if ob else None)
