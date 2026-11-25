"""A small farm film made with engine/animals.py the way a director would (its docstring only), in the real village
through the real pipeline (films.lookdev.Stage, engine.shots, engine.look: daylight, motion blur, depth of field),
540x960 / 16 samples / 2 threads. Four shots: a cow pen, wheat and hearts, the milking, the chicken coop (an egg, a
blow, a death).

Run:  $BPY -m tools.check_animals_film                         build + numeric checks only (no rendering)
      $BPY -m tools.check_animals_film pen:36 feed:80 ...      also render stills (shot:frames into the shot)
Stills: out/test/check_animals_<shot>_<offset>.png
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector

COW_PEN = (3, 27, 12, 36)            # fence ring cells in the meadow north of the village
COOP = (-12, 28, -5, 36)


def yaw_to(src, dst):
    """Yaw that makes a character at src face dst."""
    return math.atan2(dst[0] - src[0], -(dst[1] - src[1]))


def build(scene):
    from engine import animals, fx, look, shots, village
    from films.lookdev import Stage

    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, "day", sun_azimuth=190.0, sun_elevation=42.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    v.set_lantern_energy(0.0)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sky)
    info = {}

    cow_pen = animals.make_pen(scene, *COW_PEN, gates=[(7, 27)], name="cow_pen")
    coop = animals.make_pen(scene, *COOP, gates=[(-9, 28)], name="coop")
    cows = [animals.add_cow(st, "cow%d" % i) for i in range(4)] + [animals.add_cow(st, "calf", baby=True)]
    hens = [animals.add_chicken(st, "hen%d" % i) for i in range(5)] + [animals.add_chicken(st, "chick", baby=True)]
    daisy = animals.add_cow(st, "daisy")
    calf2 = animals.add_cow(st, "calf2", baby=True)
    lucky = animals.add_chicken(st, "lucky")
    layer = animals.add_chicken(st, "layer")
    steve = st.actor("steve", "steve")

    # ---- 1. pen: one wander() call; a low camera at the fence
    s = st.shot("pen", 3.0)
    f0, f1 = s.frame_start, s.frame_end
    info["pen"] = animals.wander(cows, f0, f1 + 1, cow_pen["area"], seed=3)
    mid = (f0 + f1) // 2
    cam = Vector((4.6, 25.7, 1.35))
    near = min(cows, key=lambda c: (c.pos_at(mid) - cam).length)
    s.lens(26, 3.2)
    s.move(tuple(cam), (8.6, 32.0, 0.8), (5.0, 25.75, 1.35))
    s.focus(near.head)
    st.use(s, *cows)
    st.hero(s, "cow", near)
    st.lights(s, scale=0.0)

    # ---- 2. feed: Steve holds wheat, a cow and her calf come; he feeds her: hearts
    s = st.shot("feed", 4.0)
    f0, f1 = s.frame_start, s.frame_end
    sp = (9.4, 23.6, 0.0)
    steve.place(f0, sp, yaw_to(sp, (13.5, 26.0)))
    wheat = animals.hand_item(steve, "wheat", f0, f1 + 1)
    daisy.place(f0, (14.2, 26.3, 0.0), yaw_to((14.2, 26.3), sp))
    calf2.place(f0, (15.2, 25.4, 0.0), yaw_to((15.2, 25.4), sp))
    steve.raise_arm(f0, 40, ease=0)
    steve.look_at(f0, daisy, ease=0)
    end = animals.follow(daisy, steve, f0, f0 + 50, look=wheat)
    animals.follow(calf2, daisy, f0 + 6, end + 12, stop=1.7)
    steve.track(f0, end, daisy)
    fed = end + 8
    steve.swing_arm(fed - 2)
    animals.love(daisy, fed, camera=s, frame_end=f1 + 1, seed=2)
    daisy.look_at(fed, steve, ease=6)
    s.lens(26, 3.2)
    s.move((7.63, 23.69, 1.72), (10.6, 24.45, 1.1), (7.8, 23.75, 1.7))
    s.focus(daisy.head)
    st.use(s, steve, daisy, calf2, *cows)
    st.hero(s, "cow", daisy)
    st.lights(s, scale=0.0)
    info["feed"] = dict(rest=end, fed=fed, gap=(steve.pos_at(end) - daisy.pos_at(end)).length, wheat=wheat)

    # ---- 3. milk: a bucket becomes a milk bucket
    s = st.shot("milk", 2.0)
    f0, f1 = s.frame_start, s.frame_end
    fx.stop_particles(f0)                                               # the hearts of the shot before
    cp = (11.3, 24.9, 0.0)
    daisy.place(f0, cp, math.radians(-90))                              # facing west
    sp = (11.75, 26.15, 0.0)                                            # at her flank, his right hand toward the lens
    steve.place(f0, sp, yaw_to(sp, (11.75, 24.9)))
    steve.look_at(f0, (11.7, 24.9, 0.75), ease=0)
    use = f0 + 20
    bucket, milk = animals.milk(steve, use, f0, f1 + 1)
    steve.raise_arm(f0, 30, ease=0)
    daisy.idle(f0, f1 + 1, seed=4, watch=steve)
    # a held item is a flat sprite that lies along the hand: edge-on from his side, readable from behind and above
    s.lens(24, 3.2)
    s.move((11.0, 26.98, 2.0), (11.55, 25.45, 0.8), (11.05, 26.98, 1.95))
    s.focus(bucket)
    st.use(s, steve, daisy, *cows)
    st.hero(s, "bucket", bucket)
    st.lights(s, scale=0.0)
    info["milk"] = dict(use=use, bucket=bucket, milk=milk)

    # ---- 4. coop: hens wander, one lays an egg, one is hit twice and dies
    s = st.shot("coop", 5.0)
    f0, f1 = s.frame_start, s.frame_end
    area = coop["area"]
    back = (area[0], area[1] + 3.3, area[2], area[3])                   # the others keep to the back of the coop
    info["coop"] = animals.wander(hens, f0, f1 + 1, back, seed=8)
    lp = (-9.9, 30.2, 0.0)
    layer.place(f0, lp, math.radians(-150))
    layer.idle(f0, f1 + 1, seed=1)
    egg = animals.lay_egg(layer, f0 + 14, seed=3, until=f1 + 1, stage=st)
    sp = (-6.6, 29.6, 0.0)
    hp = (-7.9, 30.1, 0.0)
    steve.place(f0, sp, yaw_to(sp, hp))
    lucky.place(f0, hp, math.radians(160))
    lucky.idle(f0, f0 + 30, seed=2)
    steve.look_at(f0, lucky, ease=0)
    hit1 = f0 + 36
    steve.swing_arm(hit1 - 2)
    up = lucky.hurt(hit1, attacker=steve, max_back=0.9)
    flee = lucky.walk(up, [tuple(lucky.pos_at(up)), (-9.6, 31.6, 0.0)], run=True)
    steve.track(hit1, flee, lucky)
    step = steve.walk(hit1 + 8, [sp, (-8.6, 30.6, 0.0)], speed=3.0)
    hit2 = max(flee, step) + 4
    steve.swing_arm(hit2 - 2)
    gone = lucky.die(hit2, camera=s, attacker=steve, max_back=0.8, seed=6, village=v)
    s.lens(28, 3.2)
    s.move((-6.9, 27.1, 1.3), (-8.7, 30.6, 0.55), (-7.1, 27.2, 1.3))
    s.focus(lucky.head)
    st.use(s, steve, lucky, layer, egg, *hens)
    st.hero(s, "hen", lucky)
    st.lights(s, scale=0.0)
    info["coop_beats"] = dict(egg=f0 + 14, hit1=hit1, up=up, flee=flee, hit2=hit2, gone=gone)

    st.finish()
    return film, st, dict(cows=cows, hens=hens, daisy=daisy, calf2=calf2, lucky=lucky, layer=layer, steve=steve,
                          egg=egg, info=info, v=v, cow_pen=cow_pen, coop=coop)


def check(scene, film, st, cast):
    """Numbers: who is rendered in which shot, the pens, the feet, the red flash, the death, the stamps."""
    from engine import animals, stamp

    ok = []

    def expect(label, cond, detail=""):
        ok.append(bool(cond))
        print("%s %s%s" % ("ok  " if cond else "FAIL", label, (": " + detail) if detail else ""))

    def rendered(c, f):
        film.goto(f)
        bpy.context.view_layer.update()
        ob = c.sprite if hasattr(c, "sprite") else c.body
        return not ob.hide_render

    shots = {s.name: s for s in film.shots}
    info = cast["info"]
    for name, s in shots.items():
        want = st.in_shot[name]
        got = {n for n, c in st.cast.items() if rendered(c, s.frame_start + 2)}
        if name == "coop":
            got |= {cast["egg"].name} if rendered(cast["egg"], s.frame_end) else set()
        expect("shot %-5s frames %d-%d shows %d of the cast" % (name, s.frame_start, s.frame_end, len(want)), got == want,
               "extra %s missing %s" % (sorted(got - want), sorted(want - got)))
    s = shots["pen"]
    gap, edge = animals.pen_report(cast["cows"], s.frame_start, s.frame_end, cast["cow_pen"]["area"])
    walks = sum(1 for ev in info["pen"].values() for e in ev if e[0] == "walk")
    expect("pen: %d walks in 3 s, bodies never closer than %.2f, %.2f from the fence" % (walks, gap, edge),
           walks >= 2 and gap >= 0.74 and edge >= 0.49)
    s = shots["coop"]
    gap, edge = animals.pen_report(cast["hens"], s.frame_start, s.frame_end, cast["coop"]["area"])
    walks = sum(1 for ev in info["coop"].values() for e in ev if e[0] == "walk")
    expect("coop: %d walks in 5 s, bodies never closer than %.2f, %.2f from the fence" % (walks, gap, edge),
           walks >= 4 and gap >= 0.49 and edge >= 0.24)
    daisy = cast["daisy"]
    expect("feed: the cow comes to rest %.2f blocks from Steve at frame %d, hearts from %d" % (
        info["feed"]["gap"], info["feed"]["rest"], info["feed"]["fed"]), 2.2 < info["feed"]["gap"] < 2.7)
    hearts = [q for b in daisy.bursts for q in b.particles]
    film.goto(info["feed"]["fed"] + 6)
    bpy.context.view_layer.update()
    up = [q for q in hearts if not q["object"].hide_render]
    cam = shots["feed"].camera
    turned = max((q["object"].matrix_world.to_quaternion().rotation_difference(cam.matrix_world.to_quaternion()).angle
                  for q in up), default=9.0)
    expect("feed: %d hearts in the air 6 frames after the wheat, facing the shot camera (off by %.4f rad)" % (len(up), turned),
           len(up) >= 7 and turned < 1e-3)
    b, m, use = info["milk"]["bucket"], info["milk"]["milk"], info["milk"]["use"]
    states = []
    for f in (shots["feed"].frame_end, use - 1, use, shots["milk"].frame_end, shots["coop"].frame_start):
        film.goto(f)
        bpy.context.view_layer.update()
        states.append((not b.hide_render, not m.hide_render))
    expect("milk: bucket until frame %d, milk bucket from then to the end of the shot %s" % (use - 1, states),
           states == [(False, False), (True, False), (False, True), (False, True), (False, False)])
    beats = info["coop_beats"]
    lucky = cast["lucky"]
    seen = {}
    for f in (beats["hit1"] - 1, beats["hit1"], beats["hit1"] + 11, beats["hit1"] + 12, beats["hit2"], beats["gone"] - 1,
              beats["gone"], shots["coop"].frame_end):
        film.goto(f)
        bpy.context.view_layer.update()
        seen[f] = (not lucky.body.hide_render, not lucky._twins["body"].hide_render)
    expect("coop: hit at %d (red 12 frames), flees until %d, hit again at %d, gone at %d %s" % (
        beats["hit1"], beats["flee"], beats["hit2"], beats["gone"], seen),
        [seen[f] for f in sorted(seen)] == [(True, False), (False, True), (False, True), (True, False), (False, True),
                                             (False, True), (False, False), (False, False)])
    puffs = [q for b_ in lucky.bursts for q in b_.particles]
    film.goto(beats["gone"] + 4)
    bpy.context.view_layer.update()
    live = [q for q in puffs if not q["object"].hide_render]
    expect("coop: %d poof particles on frame gone + 4" % len(live), len(live) == animals.POOF_COUNT)
    egg = cast["egg"]
    expect("coop: the egg is not there before frame %d, lies %.2f from the hen afterwards" % (
        beats["egg"], (egg.rest_pos - cast["layer"].pos_at(beats["egg"])).length),
        not rendered(egg, beats["egg"] - 1) and rendered(egg, beats["egg"]) and rendered(egg, shots["coop"].frame_end))
    # the frame stamps of render.py: the same frame twice gives the same fingerprint; a red frame differs from its neighbour
    fp = stamp.Fingerprinter(scene, film)
    a1 = fp.frame(beats["hit1"] + 3)["fp"]
    b1 = fp.frame(beats["hit1"] + 14)["fp"]
    fp2 = stamp.Fingerprinter(scene, film)
    b2 = fp2.frame(beats["hit1"] + 14)["fp"]
    a2 = fp2.frame(beats["hit1"] + 3)["fp"]
    expect("stamps: frame fingerprints do not depend on the order they are taken in", a1 == a2 and b1 == b2 and a1 != b1,
           "%s %s / %s %s" % (a1, a2, b1, b2))
    print("check:", "all %d passed" % len(ok) if all(ok) else "%d of %d FAILED" % (ok.count(False), len(ok)))
    return all(ok)


def main(argv):
    from engine import quick

    scene = quick.reset()
    t0 = time.time()
    film, st, cast = build(scene)
    print("built in %.1f s; shots:" % (time.time() - t0), [(s.name, s.frame_start, s.frame_end) for s in film.shots])
    print({k: v for k, v in cast["info"].items() if k in ("feed", "coop_beats")})
    good = True
    if not argv or "check" in argv:
        good = check(scene, film, st, cast)
    for arg in argv:
        if ":" not in arg:
            continue
        name, off = arg.split(":")
        shot = next(s for s in film.shots if s.name == name)
        frame = shot.frame_start + int(off) if int(off) >= 0 else shot.frame_end + 1 + int(off)
        film.goto(frame)
        bpy.context.view_layer.update()
        path = os.path.join(quick.TEST_DIR, "check_animals_%s_%s.png" % (name, off.replace("-", "m")))
        scene.render.filepath = path
        t1 = time.time()
        bpy.ops.render.render(write_still=True)
        print("wrote %s (frame %d) in %.0f s" % (path, frame, time.time() - t1))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
