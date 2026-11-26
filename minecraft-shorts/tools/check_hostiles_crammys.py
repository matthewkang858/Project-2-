"""The Crammys meadow beats 10, 12, 13-14, 15 and the lane of 17, keyed line by line from engine.hostiles' docstring
recipe (the corrected one), through films.lookdev.Stage with two skies, rendered through render.py. A check of the
recipe, not a film: nothing is written under films/ (the module registers itself as films.check_hostiles_crammys).

    $BPY -m tools.check_hostiles_crammys info               build; print what a director would check (positions,
                                                            arm aim and bow stage at the beat-15 cut, spot facing)
    $BPY -m tools.check_hostiles_crammys still F [F ...]    render.py --still (sky night) of film FRAMES F
                                                            -> out/test/check_hostiles_crammys_<seconds>.png
    $BPY -m tools.check_hostiles_crammys sheet NAME F ...   the same frames tiled into out/test/hostiles_<NAME>.png
    $BPY -m tools.check_hostiles_crammys fp                 fingerprints of the night frames (run twice: same digest)
"""
import hashlib
import math
import os
import sys

import bpy  # noqa: F401
from mathutils import Vector

from engine import hostiles, players, shots, village
from films import lookdev as L

FPS = 24
NAME = "check_hostiles_crammys"
SKIES = {
    "gold": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
}
Y = 40.0                                   # the line on the flat meadow north of the exit gate
CREEPER_AT, SKELETON_AT, MIDDLE = (1.5, Y, 0.0), (8.5, Y, 0.0), (5.0, Y, 0.0)
INFO = {}


def _clear(b):
    for x in range(-4, 13):
        for y in range(30, 47):
            b.clear_plants(x, y)


def build(scene, sky=None):
    v = village.build_village(scene, seed=1, edit=_clear)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16
    steve = players.add_player(st, "steve", "steve")
    cr = hostiles.add_creeper(st, "creeper")
    sk = hostiles.add_skeleton(st, "skeleton")

    s0 = st.shot("square", 1.0, sky="gold")                 # the other sky: none of the hostiles may show here
    st.lights(s0, scale=1.0)
    sq = v.anchors["square_s"]
    steve.place(s0.frame_start, sq, 0.0)
    s0.lens(35, 3.2)
    s0.move((sq[0] + 1.0, sq[1] - 4.0, 1.5), (sq[0], sq[1], 1.2))
    st.use(s0, steve)

    # 10 "I found a creeper.": low over Steve's shoulder; it faces him, still, then ONE slow step
    s10 = st.shot("creeper_found", 2.5, sky="night")
    st.lights(s10, scale=1.3)
    f0 = s10.frame_start
    me, it = Vector((5.0, Y - 4.0, 0.0)), Vector((5.0, Y + 1.0, 0.0))
    steve.place(f0, tuple(me), 0.0 + math.pi)                # facing north, at the creeper
    cr.place(f0, tuple(it), 0.0)                             # facing south, at Steve
    cr.look_at(f0, steve, ease=0)
    step_end = cr.step(f0 + 30, steve)                       # recipe beat 10
    s10.lens(40, 4.0)
    s10.move(tuple(me + Vector((0.85, -1.9, 0.9))), tuple(it + Vector((-0.3, 0.0, 0.9))))
    s10.focus(cr.head)
    st.use(s10, steve, cr)
    st.hero(s10, "creeper", cr)
    INFO["step"] = (f0 + 30, step_end, dict(cr.last_walk))

    # 12 "I stood in the middle.": creeper left, skeleton right with its bow drawn and held
    s1 = st.shot("line", 2.5)
    st.lights(s1, scale=1.3)
    f0, f1 = s1.frame_start, s1.frame_end
    cr.place(f0, CREEPER_AT, math.pi / 2.0)
    sk.place(f0, SKELETON_AT, -math.pi / 2.0)
    start = (MIDDLE[0] + 0.2, Y - 5.0, 0.0)
    steve.place(f0, start, math.pi)
    sk.aim(f0, steve, ease=0)                                # recipe beat 12
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

    # 13 + 14: medium on Steve, three-quarter front from the skeleton's side (he faces north-east: the skeleton,
    # due east, is on his right), one shot for both arrows
    s2 = st.shot("shot", 4.0)
    st.lights(s2, scale=1.3)
    f0, f1 = s2.frame_start, s2.frame_end
    steve.place(f0, MIDDLE, math.radians(135.0))             # facing north-east
    cr_from = (MIDDLE[0] - 2.4, Y + 0.4, 0.0)
    cr.place(f0, cr_from, math.pi / 2.0)
    sk.place(f0, SKELETON_AT, -math.pi / 2.0)
    sk.aim(f0, steve, ease=0)                                # recipe beats 13 and 14
    fl1 = sk.shoot(f0, steve, part="chest", knockback=0.1)
    fl2 = sk.shoot(fl1.frames[0] + 1, steve, part="shoulder_r", knockback=0.1)
    steve.look_at(f0, sk, ease=0)
    look_down = int(fl2) + 8
    chest = steve.pos_at(look_down) + Vector((0.0, 0.0, 1.0))
    steve.look_at(look_down, chest + Vector((0.3, 0.3, 0.0)), ease=6)
    steve.look_at(look_down + 18, sk, ease=6)
    cr.walk(f0 + 30, [cr_from, (MIDDLE[0] - 1.1, Y + 0.3, 0.0)], speed=0.8)
    cr.look_at(f0 + 30, steve, ease=8)
    m = Vector(MIDDLE)
    s2.lens(50, 2.8)
    s2.move(tuple(m + Vector((2.6, 1.2, 1.45))), tuple(m + Vector((0.0, 0.0, 1.25))))
    s2.focus(steve.head)
    st.use(s2, steve, cr)
    st.hero(s2, "steve", steve)
    INFO["shot"] = (f0, f1, fl1, fl2)

    # 15 "Then it shot the creeper.": Steve, creeper, skeleton; swell + white, two arrows ~20 frames apart, poof
    s3 = st.shot("creeper", 3.5)
    st.lights(s3, scale=1.3)
    f0, f1 = s3.frame_start, s3.frame_end
    c_at = (4.4, Y + 0.2, 0.0)
    s_from, s_to = (4.6, Y - 1.0, 0.0), (2.2, Y - 0.1, 0.0)
    cr.place(f0, c_at, -math.pi / 2.0)                       # recipe beat 15: place first ...
    steve.place(f0, s_from, -math.pi / 2.0)
    sk.place(f0, SKELETON_AT, -math.pi / 2.0)
    sk.aim(f0, cr, ease=0)
    steve.walk(f0, [s_from, (3.4, Y - 0.9, 0.0), s_to], speed=2.6)
    cr.face(f0 + 1, steve, ease=6)
    cr.look_at(f0 + 1, steve, ease=4)
    end = cr.fuse(f0)
    a = sk.shoot(f0 - 24, cr, knockback=0.1)
    k = sk.shoot(a.frames[0] + 1, cr, release=a.frames[0] + 20, kill=True, knockback=0.1, camera=s3)
    sk.lower(int(k) + 12)
    steve.look_at(int(a) - 4, cr, ease=6)
    s3.lens(22, 5.6)
    mid = Vector((4.5, Y, 0.0))
    s3.move(tuple(mid + Vector((0.0, -10.0, 0.75))), tuple(mid + Vector((0.0, 0.0, 0.95))))
    s3.focus(cr.head)
    st.use(s3, steve, cr, sk)
    st.hero(s3, "creeper", cr)
    INFO["creeper"] = (f0, f1, end, a, k)

    # 17: the sprint with the two arrows
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

    st.finish()
    INFO.update(steve=steve, cr=cr, sk=sk, st=st, film=film)
    return {"film": film, "captions": [], "stage": st}


def _register():
    sys.modules["films." + NAME] = sys.modules[__name__]
    import films

    setattr(films, NAME, sys.modules[__name__])


def _r(v):
    return tuple(round(c, 2) for c in v)


def info():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    build(scene, sky="night")
    steve, cr, sk, film = INFO["steve"], INFO["cr"], INFO["sk"], INFO["film"]
    for s in film.shots:
        print("shot %-14s %4d-%4d" % (s.name, s.frame_start, s.frame_end))
    a0, a1, lw = INFO["step"]
    print("beat 10 step %d-%d: %.2f blocks, legs +-%.1f deg" % (a0, a1, lw["blocks"], math.degrees(lw["swing"])))
    angles = []
    for f in range(a0, a1 + 1):
        scene.frame_set(f)
        angles.append(math.degrees(cr.leg_r.rotation_euler.x))
    print("  right hind leg (deg) per frame:", [round(x) for x in angles])
    f0, f1, fl1, fl2 = INFO["shot"]
    print("beat 13/14: arrow 1 loosed %d impact %d spot %s; arrow 2 loosed %d impact %d spot %s" % (
        fl1.frames + (fl1.spot,) + fl2.frames + (fl2.spot,)))
    for fl in (fl1, fl2):
        scene.frame_set(int(fl))
        tip = fl.stuck.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
        print("  %s: shaft %.0f deg off the way back to the shooter" % (fl.stuck.name, math.degrees(tip.angle(fl.direction))))
    print("  steve at", [(f, _r(steve.pos_at(f))) for f in (int(fl1) - 1, int(fl1) + 12, int(fl2) + 12)])
    f0, f1, end, a, k = INFO["creeper"]
    print("beat 15 (shot %d-%d): fuse would explode %d; arrow 1 loosed %d impact %d; arrow 2 loosed %d impact %d"
          " (%d frames apart)" % ((f0, f1, end) + a.frames + k.frames + (int(k) - int(a),)))
    for f in range(f0 - 1, f0 + 4):
        print("  skeleton frame %d: aiming %.2f bow %s" % (f, sk.aiming_at(f), sk.bow_at(f)))
    gap = []
    for f in range(f0, int(k) + 25):
        c, s_ = cr.pos_at(f), steve.pos_at(f)
        gap.append((round(math.hypot(c.x - s_.x, c.y - s_.y), 2), f))
    print("  creeper at", [(f, _r(cr.pos_at(f))) for f in (f0, int(a), int(a) + 6, int(a) + 12, int(k), int(k) + 12,
                                                          int(k) + 24)])
    print("  steve at", [(f, _r(steve.pos_at(f))) for f in (f0, int(a), int(k), int(k) + 24)])
    print("  closest creeper - steve (centres, horizontal): %.2f on frame %d (hit boxes 0.6 wide: touch below 0.6)"
          % min(gap))


def fingerprints():
    import render

    _register()
    ses = render.Session(NAME, sky="night")
    h = hashlib.sha1()
    frames = [f for f in range(ses.film.frame_start, ses.film.frame_end + 1) if ses.sky_of(f) == "night"]
    for f in frames:
        h.update(str(ses.fingerprint(f)).encode())
    print("night frames %d-%d: digest %s" % (frames[0], frames[-1], h.hexdigest()))


def stills(frames, res="540x960"):
    import render

    _register()
    secs = ["%.6f" % ((int(f) - 1) / FPS) for f in frames]
    return render.main([NAME, "--still", ",".join(secs), "--sky", "night", "--res", res])


def sheet(name, frames):
    from PIL import Image, ImageDraw

    rc = stills(frames, res="360x640")
    paths = [os.path.join("out", "test", "%s_%.6f.png" % (NAME, (int(f) - 1) / FPS)) for f in frames]
    have = [p for p in paths if os.path.exists(p)]
    if not have:
        print("no stills found:", paths)
        return rc
    ims = [Image.open(p).convert("RGB") for p in have]
    w, h = ims[0].size
    out = Image.new("RGB", (len(ims) * (w + 4) - 4, h), (20, 20, 24))
    d = ImageDraw.Draw(out)
    for i, (im, f) in enumerate(zip(ims, frames)):
        out.paste(im, (i * (w + 4), 0))
        d.rectangle((i * (w + 4), 0, i * (w + 4) + 60, 16), fill=(0, 0, 0))
        d.text((i * (w + 4) + 4, 2), "f%s" % f, fill=(255, 255, 255))
    path = os.path.join("out", "test", "hostiles_%s.png" % name)
    out.save(path)
    print("wrote", path)
    return rc


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "info"
    if what == "info":
        info()
    elif what == "fp":
        fingerprints()
    elif what == "still":
        sys.exit(stills(sys.argv[2:]))
    elif what == "sheet":
        sys.exit(sheet(sys.argv[2], sys.argv[3:]))
