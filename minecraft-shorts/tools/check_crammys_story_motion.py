"""Checker probe: where the stub's characters are on the words that matter (md12, md13, md15, fn24). No render."""
import os, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import render
ses = render.Session("crammys", sky="night")
C = ses.result["context"]
st = C.st
cast = st.cast
def get(name):
    for k, v in cast.items():
        if k == name or getattr(v, "name", None) == name:
            return v
    return None
print(sorted(k for k in cast if k.startswith(("steve", "creeper", "skeleton"))))
sv = get("steve_md")
cr = get("creeper_md")
print("md12 path", C.v.paths["crammys_into_middle"])
for f in (797, 803, 813, 818, 827, 835, 843):
    p = sv.pos_at(f)
    print("md12 steve_md f%d pos (%.2f, %.2f) yaw %.1f" % (f, p.x, p.y, math.degrees(sv.yaw_at(f))))
for f in (797, 830, 843):
    p = cr.pos_at(f); print("md12 creeper f%d (%.2f, %.2f)" % (f, p.x, p.y))
