"""Reviewer's probe of engine.hostiles: the Crammys meadow beats 12-15 and the sprint of beat 17, written from the
module docstring only, through films.lookdev.Stage with SKIES (gold + night), rendered through render.py.

    $BPY -m tools.check_hostiles_film info                 build, print the numbers a director would check
    $BPY -m tools.check_hostiles_film still F [F ...]      render.py --still (sky night) of film frames F
    $BPY -m tools.check_hostiles_film fp                   fingerprints of the night frames (run twice: same digest)

The module registers itself as films.check_hostiles_film in sys.modules so that render.py's Session can import it
(no file is written under films/). Output: out/test/check_hostiles_film_<seconds>.png.
"""
import hashlib
import math
import os
import sys

import bpy  # noqa: F401  (pip bpy: mathutils comes with it)
from mathutils import Vector

from engine import hostiles, players, shots, village
from films import lookdev as L

FPS = 24
NAME = "check_hostiles_film"

SKIES = {
    "gold": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
}

Y = 40.0                                   # the line on the flat meadow north of the exit gate
CREEPER_AT = (1.5, Y, 0.0)
SKELETON_AT = (8.5, Y, 0.0)
MIDDLE = (5.0, Y, 0.0)
INFO = {}


def _clear(b):
    for x in range(-4, 13):
        for y in range(30, 47):
            b.clear_plants(x, y)


def build(scene, sky=None):
    """The probe film: gold establishing shot, then the night meadow (beats 12, 13-14, 15) and the lane (17)."""
    v = village.build_village(scene, seed=1, edit=_clear)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16

    steve = players.add_player(st, "steve", "steve")
    cr = hostiles.add_creeper(st, "creeper")
    sk = hostiles.add_skeleton(st, "skeleton")

    # 0 gold: Steve in the square (the other sky; nothing of the hostiles may show here)
    s0 = st.shot("square", 1.0, sky="gold")
    st.lights(s0, scale=1.0)
    sq = v.anchors["square_s"]
    steve.place(s0.frame_start, sq, 0.0)
    s0.lens(35, 3.2)
    s0.move((sq[0] + 1.0, sq[1] - 4.0, 1.5), (sq[0], sq[1], 1.2))
    st.use(s0, steve)

    # 12 "I stood in the middle": low wide side view, creeper left, skeleton right with its bow drawn and held
    s1 = st.shot("line", 2.5, sky="night")
    st.lights(s1, scale=1.3)
    f0, f1 = s1.frame_start, s1.frame_end
    cr.place(f0, CREEPER_AT, math.pi / 2.0)                  # facing east, at the middle
    sk.place(f0, SKELETON_AT, -math.pi / 2.0)                # facing west
    start = (MIDDLE[0] + 0.2, Y - 5.0, 0.0)
    steve.place(f0, start, math.pi)                          # back to the lens, walking north
    sk.aim(f0, steve, ease=0)
    sk.draw(f0, release=f1 + 1, target=steve)
    e = steve.walk(f0, [start, MIDDLE], speed=2.2)
    steve.look_at(e + 2, cr, ease=6)
    steve.look_at(e + 14, sk, ease=6)
    cr.look_at(f0, steve, ease=0)
    cr.walk(f1 - 16, [CREEPER_AT, (CREEPER_AT[0] + 0.6, Y, 0.0)], speed=0.8)
    s1.lens(24, 5.6)
    s1.move((MIDDLE[0], Y - 8.6, 0.55), (MIDDLE[0], Y, 1.0))
    s1.focus(steve.head)
    st.use(s1, steve, cr, sk)
    st.hero(s1, "steve", steve)
    INFO["line"] = (f0, f1, e)

    # 13 + 14 "The skeleton shot me. Then it shot me again.": medium on Steve, three-quarter front from the skeleton's
    # side, the creeper soft behind him, one shot for both arrows
    s2 = st.shot("shot", 4.0)
    st.lights(s2, scale=1.3)
    f0, f1 = s2.frame_start, s2.frame_end
    steve.place(f0, MIDDLE, math.radians(60.0))              # turned toward the skeleton (east-south-east)
    cr_from = (MIDDLE[0] - 2.4, Y + 0.4, 0.0)
    cr.place(f0, cr_from, math.pi / 2.0)
    sk.place(f0, SKELETON_AT, -math.pi / 2.0)
    sk.aim(f0, steve, ease=0)
    fl1 = sk.shoot(f0 + 2, steve, part="chest", knockback=0.1)          # docstring beat 13
    fl2 = sk.shoot(fl1.frames[0] + 1, steve, part="shoulder_l", knockback=0.1)   # docstring beat 14
    steve.look_at(f0, sk, ease=0)
    look_down = int(fl2) + 8
    chest = steve.pos_at(look_down) + Vector((0.0, 0.0, 1.0))
    steve.look_at(look_down, chest + Vector((0.4, -0.2, 0.0)), ease=6)
    steve.look_at(look_down + 18, sk, ease=6)
    cr.walk(f0 + 30, [cr_from, (MIDDLE[0] - 1.1, Y + 0.3, 0.0)], speed=0.8)
    cr.look_at(f0 + 30, steve, ease=8)
    m = Vector(MIDDLE)
    s2.lens(50, 2.8)
    s2.move(tuple(m + Vector((2.3, -2.2, 1.45))), tuple(m + Vector((0.0, 0.0, 1.25))))
    s2.focus(steve.head)
    st.use(s2, steve, cr)                                    # the skeleton is beside the lens, out of frame
    st.hero(s2, "steve", steve)
    INFO["shot"] = (f0, f1, fl1, fl2)

    # 15 "Then it shot the creeper.": side view, tighter; Steve, creeper, skeleton; swell + white, two arrows, poof
    s3 = st.shot("creeper", 3.5)
    st.lights(s3, scale=1.3)
    f0, f1 = s3.frame_start, s3.frame_end
    c_at = (4.4, Y + 0.2, 0.0)
    cr.place(f0, c_at, -math.pi / 2.0)                       # facing west, after Steve: its back to the skeleton
    s_from, s_to = (4.6, Y - 1.0, 0.0), (2.2, Y - 0.1, 0.0)
    steve.place(f0, s_from, -math.pi / 2.0)
    sk.place(f0, SKELETON_AT, -math.pi / 2.0)
    steve.walk(f0, [s_from, (3.4, Y - 0.9, 0.0), s_to], speed=2.6)
    cr.face(f0 + 2, steve, ease=6)
    cr.look_at(f0 + 2, steve, ease=4)
    end = cr.fuse(f0 + 4)                                    # docstring beat 15
    if not os.environ.get("RECIPE"):                     # RECIPE=1: the docstring's beat-15 lines only
        sk.aim(f0, cr, ease=0)
    a = sk.shoot(f0 + 4 - 24, cr)                            # docstring: sk.shoot(f0 - 24, cr) (f0 = fuse start)
    k = sk.shoot(a.frames[0] + 1, cr, kill=True, camera=s3)
    sk.lower(int(k) + 12)
    steve.look_at(int(a) - 4, cr, ease=6)
    s3.lens(22, 5.6)
    mid = Vector((4.5, Y, 0.0))
    s3.move(tuple(mid + Vector((0.0, -10.0, 0.75))), tuple(mid + Vector((0.0, 0.0, 0.95))))
    s3.focus(cr.head)
    st.use(s3, steve, cr, sk)
    st.hero(s3, "creeper", cr)
    INFO["creeper"] = (f0, f1, end, a, k)

    # 17 "I ran to the stage with arrows still in me.": a sprint down the exit road by the houses, at night
    s4 = st.shot("lane", 2.0)
    st.lights(s4, scale=1.3)
    f0, f1 = s4.frame_start, s4.frame_end
    p0, p1 = (0.5, 21.0, -0.06), (0.4, 9.0, -0.1)
    steve.place(f0, p0, 0.0)
    steve.walk(f0, [p0, p1], sprint=True, ramp=(False, False))
    s4.lens(32, 3.2)
    s4.follow(steve.root, (3.2, -0.6, 1.2), look_offset=(0.0, 0.0, 1.1))
    s4.focus(steve.head)
    st.use(s4, steve)
    st.hero(s4, "steve", steve)
    INFO["lane"] = (f0, f1)

    st.finish()
    INFO.update(steve=steve, cr=cr, sk=sk, st=st, film=film)
    return {"film": film, "captions": [], "stage": st}


def _register():
    sys.modules["films." + NAME] = sys.modules[__name__]
    import films

    setattr(films, NAME, sys.modules[__name__])


def info():
    import bpy

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    build(scene, sky="night")
    steve, cr, sk, film = INFO["steve"], INFO["cr"], INFO["sk"], INFO["film"]
    for s in film.shots:
        print("shot %-8s %4d-%4d" % (s.name, s.frame_start, s.frame_end))
    print("line", INFO["line"])
    f0, f1, fl1, fl2 = INFO["shot"]
    print("shot: arrow 1 loosed %d impact %d ; arrow 2 loosed %d impact %d" % (fl1.frames + fl2.frames))
    for fl in (fl1, fl2):
        imp = int(fl)
        scene.frame_set(imp)
        m = fl.stuck.matrix_world
        tip = m.to_3x3() @ Vector((1.0, 0.0, 0.0))
        fly = fl.direction
        ang = math.degrees(tip.angle(fly))
        print("  stuck arrow (%s): tip direction vs flight direction %.0f deg (0 = the shaft points back at the "
              "shooter); shaft points to %s" % (fl.stuck.name, ang, tuple(round(c, 2) for c in -tip.normalized())))
        p_before = fl.point_at(imp - 1)
        print("  flying arrow at impact-1:", tuple(round(c, 2) for c in p_before), "visible:",
              (scene.frame_set(imp - 1), not fl.arrow.hide_render)[1])
    for f in (fl1, int(fl1) + 12, int(fl2) + 12, f1):
        print("  steve at", int(f), tuple(round(c, 2) for c in steve.pos_at(int(f))))
    f0, f1, end, a, k = INFO["creeper"]
    print("creeper: fuse would explode on %d, arrow 1 loosed %d impact %d, arrow 2 loosed %d impact %d" %
          ((end,) + a.frames + k.frames))
    for f in (f0, int(a), int(a) + 6, int(a) + 12, int(k), int(k) + 12, int(k) + 24):
        print("  creeper at %d %s swell %.2f white %.2f; steve %s" % (f, tuple(round(c, 2) for c in cr.pos_at(f)),
              cr.swelling_at(f), cr.white_at(f), tuple(round(c, 2) for c in steve.pos_at(f))))
    for f in range(f0 - 2, f0 + 8):
        print("  skel frame %d bow %s aiming %.2f" % (f, sk.bow_at(f), sk.aiming_at(f)))
    # what is rendered in shots it should not be in
    names = {"creeper": cr, "skeleton": sk}
    for s in film.shots:
        for f in (s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end):
            scene.frame_set(f)
            vis = []
            for ob in scene.objects:
                if ob.type != "MESH" or ob.hide_render:
                    continue
                n = ob.name
                if any(n.startswith(p) for p in ("creeper", "skeleton", "steve_arrow", "arrow_", "hostiles_")):
                    vis.append(n)
            short = sorted({n.split("_")[0] if not n.startswith("steve_arrow") else n for n in vis})
            print("  frame %d (%s): rendered hostiles objects: %s" % (f, s.name, short))


def fingerprints():
    import render

    _register()
    ses = render.Session(NAME, sky="night")
    h = hashlib.sha1()
    frames = [f for f in range(ses.film.frame_start, ses.film.frame_end + 1) if ses.sky_of(f) == "night"]
    for f in frames:
        h.update(str(ses.fingerprint(f)).encode())
    print("night frames %d-%d: digest %s" % (frames[0], frames[-1], h.hexdigest()))


def stills(frames):
    import render

    _register()
    secs = ["%.6f" % ((int(f) - 1) / FPS) for f in frames]
    res = ["--res", "540x960"]
    return render.main([NAME, "--still", ",".join(secs), "--sky", "night"] + res)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "info"
    if what == "info":
        info()
    elif what == "fp":
        fingerprints()
    elif what == "still":
        sys.exit(stills(sys.argv[2:]))
