"""Checker probe 5: what every player visibly holds / wears in each of its shots (start, a word, end)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import render
ses = render.Session("legday", sky=sys.argv[sys.argv.index("--sky") + 1] if "--sky" in sys.argv else "gold")
scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
for s in sorted(ses.film.shots, key=lambda s: s.frame_start):
    for name in sorted(st.in_shot.get(s.name, ())):
        c = st.cast[name]
        att = getattr(c, "_attached", None)
        if att is None:
            continue
        out = []
        for f in (s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end):
            scene.frame_set(f)
            vis = sorted({a.ob.name.replace(name + "_", "") for a in att if not a.ob.hide_render and a.ob.type == "MESH"})
            out.append("%d:%s" % (f, ",".join(vis) or "-"))
        lights = [o for o in c.root.children_recursive if o.type == "LIGHT"]
        lv = []
        for f in (s.frame_start, s.frame_end):
            scene.frame_set(f)
            lv.append("%d:%s" % (f, ",".join("%s=%.0fW%s" % (o.name[-12:], o.data.energy, "" if not o.hide_render else "(off)") for o in lights) or "-"))
        print("%-15s %-12s %s | lights %s" % (s.name, name, "  ".join(out), " ".join(lv)))
