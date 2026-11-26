"""Checker probe 4: where cl11 and cl22 climbers differ (frame by frame), root keyed vs delta."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import render
ses = render.Session("legday", sky="gold")
scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
a, b = C.T["cl11_climb"], C.T["cl22_dusk"]
for role in ("steve", "ari"):
    ca, cb = st.cast[role + "_cl"], st.cast[role + "_cl3"]
    rows = []
    for k in range(a.frames):
        scene.frame_set(a.frame_start + k); pa = ca.root.matrix_world.translation.copy(); da = ca.root.delta_location[2]
        scene.frame_set(b.frame_start + k); pb = cb.root.matrix_world.translation.copy(); db = cb.root.delta_location[2]
        d = (pa - pb).length
        if d > 0.01:
            rows.append((k, round(pa.y, 3), round(pb.y, 3), round(pa.z, 3), round(pb.z, 3), round(da, 3), round(db, 3)))
    print(role, len(rows), rows[:12])
