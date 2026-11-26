"""Checker probe: world positions of Steve and the zombie in rd07 (and Steve in rd17). No render."""
import os, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import render
ses = render.Session("crammys", sky="night")
C = ses.result["context"]
cast = C.st.cast
sv, zb = cast["steve_rd"], cast["zombie_rd"]
print("lane_home", C.v.paths["lane_home"])
for f in range(509, 565, 3):
    p, q = sv.pos_at(f), zb.pos_at(f)
    print("f%d steve (%.2f, %.2f)  zombie (%.2f, %.2f)  gap %.2f" % (f, p.x, p.y, q.x, q.y, (p - q).length))
