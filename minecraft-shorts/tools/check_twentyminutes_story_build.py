"""Checker probe (story, words and time): build Twenty Minutes through render.Session and measure, frame by frame,
the story events against the words: shot table and captions vs the plan, golem visibility / position, the swap, the
second bed, the top step, the door, the end in black, Mom's head on the zombie. No render.
    $BPY -m tools.check_twentyminutes_story_build"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import bpy  # noqa
import render  # noqa
from mathutils import Vector  # noqa

ses = render.Session("twentyminutes")
res = ses.result
nar, st, C, film = res["narration"], res["stage"], res["context"], ses.film
scene = ses.scene
from films import twentyminutes as TM  # noqa

rows = TM.timeline(nar)
print("\n== SHOTS: built vs plan ==")
bad = 0
for r, s in zip(rows, film.shots):
    ok = (r.name, r.frame_start, r.frame_end) == (s.name, s.frame_start, s.frame_end)
    bad += not ok
    if not ok:
        print("MISMATCH", r, s.name, s.frame_start, s.frame_end)
print("shots built %d, plan %d, mismatches %d, film end %d, nar.frames %d" % (len(film.shots), len(rows), bad,
                                                                         film.shots[-1].frame_end, nar.frames))
caps = res["captions"]
want = nar.captions(cuts=TM.caption_cuts(nar, rows))
print("captions from build == plan captions:", [tuple(c) for c in caps] == [tuple(c) for c in want], len(caps))
print("session captions == build captions:", ses.captions == [(str(w), float(a), float(b)) for w, a, b in caps])
print("fades:", ses.fades)


def vis(obj, f):
    scene.frame_set(f)
    return not obj.hide_render


class _Meshes:
    def __init__(self, c):
        self.obs = [o for o in c.objects() if o.type == "MESH"]

    @property
    def hide_render(self):
        return all(o.hide_render for o in self.obs)


def root(c):
    return _Meshes(c)


g = st.cast.get("golem")
print("\n== GOLEM (visible, x y z, head z) ==")
spans = [(540, 600), (600, 618), (636, 710), (1470, 1542)]
for a, b in spans:
    last = None
    for f in range(a, b + 1):
        v = vis(root(g), f)
        p = g.pos_at(f)
        line = "%d %s x=%.2f y=%.2f z=%.2f" % (f, "VIS" if v else "---", p.x, p.y, p.z)
        key = (v, round(p.x, 1), round(p.z, 1))
        if key != last or f in (a, b):
            print("  " + line)
        last = key

print("\n== SWAP (baby_gr / narrator_gr visible) ==")
baby, adult = st.cast["baby_gr"], st.cast["narrator_gr"]
for f in range(1172, 1184):
    print("  %d baby %s narrator %s" % (f, vis(root(baby), f), vis(root(adult), f)))

print("\n== SECOND BED ==")
bed2 = C.P_.bed2
obs = bed2.objects()
for f in (1, 400, 1255, 1256, 1300, 1303, 1304, 1305, 1316, 1337, 1338, 1400, 1440, 1473, 1500):
    print("  %d bed2 visible %s" % (f, vis(obs[0], f)))
print("  C.bed2_frame", C.bed2_frame)

print("\n== TOP STEP ==")
ts = C.P_.top_step
tob = ts.ob if hasattr(ts, "ob") else None
print("  top_step", ts, tob)
if tob is not None:
    for f in (772, 834, 902, 1210, 1338, 1344, 1350, 1355, 1360, 1362, 1365, 1399, 1400):
        print("  %d visible %s" % (f, vis(tob, f)))

print("\n== MOM'S HEAD vs THE ZOMBIE (degrees between head forward and the zombie's eyes) ==")
eye = Vector(C.zombie_eye)
for r in rows:
    if r.frame_end < 230:
        continue
    for name in sorted(n for n in st.in_shot.get(r.name, ()) if n.startswith("mom_")):
        mom = st.cast[name]
        worst = (0, None)
        for f in range(r.frame_start, r.frame_end + 1, 2):
            scene.frame_set(f)
            h = mom.head
            fwd = (h.matrix_world.to_3x3() @ Vector((0, -1, 0)))
            fwd.z = 0
            to = eye - h.matrix_world.translation
            to.z = 0
            if fwd.length < 1e-6 or to.length < 1e-6:
                continue
            ang = math.degrees(fwd.angle(to))
            if ang > worst[0]:
                worst = (ang, f)
        print("  %-14s %-8s worst %.1f deg at %s" % (r.name, name, worst[0], worst[1]))

print("\n== DOOR house_c ==")
door = [o for o in scene.objects if "house_c" in o.name and "door" in o.name.lower()]
print("  ", [o.name for o in door][:6])
for o in door[:2]:
    for f in (1, 20, 30, 40, 45, 50, 52, 55, 58, 60, 63, 67, 80, 87):
        scene.frame_set(f)
        print("   %s f%d rotz %.1f" % (o.name, f, math.degrees(o.matrix_world.to_euler().z)))
