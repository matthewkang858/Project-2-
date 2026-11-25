"""Independent checker's film probe of engine/animals.py: a five-shot farm film written from the module docstring
only, in the real village through films.lookdev.Stage, engine.shots and engine.look (daylight, motion blur, depth of
field), 540x960 / 16 samples / 2 threads.

Run:  $BPY -m tools.check_animals_probe_film                  build, print the beats and where things land in frame
      $BPY -m tools.check_animals_probe_film walk:30 hens:28  also render stills (shot:frames into the shot)
Stills: out/test/check_animals_p_<shot>_<offset>.png
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector

COW_PEN = (3, 27, 12, 36)
COOP = (-12, 28, -5, 36)


def yaw_to(src, dst):
    return math.atan2(dst[0] - src[0], -(dst[1] - src[1]))


def build(scene):
    from engine import animals, fx, look, shots, village
    from films.lookdev import Stage

    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, "day", sun_azimuth=235.0, sun_elevation=40.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    v.set_lantern_energy(0.0)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sky)
    info = {}

    pen = animals.make_pen(scene, *COW_PEN, gates=[(7, 27)], name="p_cow_pen")
    coop = animals.make_pen(scene, *COOP, gates=[(-9, 28)], name="p_coop")
    area, carea = pen["area"], coop["area"]
    herd = [animals.add_cow(st, "cow%d" % i) for i in range(3)]
    daisy = animals.add_cow(st, "daisy")
    calf = animals.add_cow(st, "calf", baby=True)
    hens = [animals.add_chicken(st, "hen%d" % i) for i in range(4)]
    henny = animals.add_chicken(st, "henny")
    pip = animals.add_chicken(st, "pip", baby=True)
    layer = animals.add_chicken(st, "layer")
    lucky = animals.add_chicken(st, "lucky")
    steve = st.actor("steve", "steve")

    # ---- 1. walk: a cow crosses the pen in a medium shot, her calf after her, three more behind
    s = st.shot("walk", 3.0)
    f0, f1 = s.frame_start, s.frame_end
    a, b = (4.6, 31.4, 0.0), (10.4, 31.4, 0.0)
    daisy.place(f0, a, yaw_to(a, b))
    end = daisy.walk(f0, [a, b])
    daisy.idle(end, f1 + 1, seed=2)
    calf.place(f0, (4.3, 33.0, 0.0), yaw_to((4.3, 33.0), a))
    animals.follow(calf, daisy, f0, f1 + 1, stop=2.2)
    back = (area[0], 33.4, area[2], area[3])
    info["walk"] = animals.wander(herd, f0, f1 + 1, back, seed=5)
    s.lens(30, 2.8)
    s.move((7.3, 28.25, 0.8), (7.0, 31.4, 0.72), (7.9, 28.25, 0.8), (7.9, 31.4, 0.72))
    s.focus(daisy.head)
    st.use(s, daisy, calf, *herd)
    st.hero(s, "cow", daisy)
    st.lights(s, scale=0.0)
    info["walk_beats"] = dict(end=end, last=dict(daisy.last_walk))

    # ---- 2. hens: a hen comes toward the lens at the game's speed, a chick after her; four more wander
    s = st.shot("hens", 2.5)
    f0, f1 = s.frame_start, s.frame_end
    a, b = (-10.6, 33.3, 0.0), (-7.5, 30.6, 0.0)
    henny.place(f0, a, yaw_to(a, b))
    end = henny.walk(f0, [a, b])
    henny.idle(end, f1 + 1, seed=1)
    pip.place(f0, (-10.9, 34.1, 0.0), yaw_to((-10.9, 34.1), a))
    animals.follow(pip, henny, f0, f1 + 1, stop=0.9)
    info["hens"] = animals.wander(hens, f0, f1 + 1, (carea[0], 33.9, carea[2], carea[3]), seed=3)
    s.lens(40, 2.8)
    s.move((-6.9, 29.5, 0.45), (-8.6, 31.5, 0.38))
    s.focus(henny.head)
    st.use(s, henny, pip, *hens)
    st.hero(s, "hen", henny)
    st.lights(s, scale=0.0)
    info["hens_beats"] = dict(end=end)

    # ---- 3. feed: Steve holds wheat, the cow comes, he feeds her: hearts
    s = st.shot("feed", 4.0)
    f0, f1 = s.frame_start, s.frame_end
    sp = Vector((6.0, 29.4, 0.0))
    cp = Vector((9.6, 33.0, 0.0))
    d = (cp - sp).normalized()
    right = Vector((d.y, -d.x, 0.0))
    steve.place(f0, tuple(sp), yaw_to(sp, cp))
    wheat = animals.hand_item(steve, "wheat", f0, f1 + 1)
    steve.raise_arm(f0, 40, ease=0)
    daisy.place(f0, tuple(cp), yaw_to(cp, sp))
    calf.place(f0, (10.6, 32.2, 0.0), yaw_to((10.6, 32.2), sp))
    steve.look_at(f0, daisy, ease=0)
    rest = animals.follow(daisy, steve, f0, f0 + 40, look=wheat)
    animals.follow(calf, daisy, f0 + 5, rest + 14, stop=1.8)
    steve.track(f0, rest, daisy)
    fed = rest + 8
    steve.swing_arm(fed - 2)
    hearts = animals.love(daisy, fed, camera=s, frame_end=f1 + 1, seed=4)
    herd_area = (area[0], 34.0, area[2], area[3])
    animals.wander(herd, f0, f1 + 1, herd_area, seed=6, place=False)
    cam = sp - d * 1.2 + right * 1.5 + Vector((0, 0, 2.2))
    aim = sp + d * 1.35 + Vector((0, 0, 1.05))
    s.lens(26, 3.2)
    s.move(tuple(cam), tuple(aim))
    s.focus(daisy.head)
    st.use(s, steve, daisy, calf, *herd)
    st.hero(s, "cow", daisy)
    st.lights(s, scale=0.0)
    info["feed_beats"] = dict(rest=rest, fed=fed, gap=(steve.pos_at(rest) - daisy.pos_at(rest)).length, wheat=wheat,
                              hearts=hearts)

    # ---- 4. milk: the bucket becomes a milk bucket
    s = st.shot("milk", 2.5)
    f0, f1 = s.frame_start, s.frame_end
    fx.stop_particles(f0)
    cpos = (7.5, 31.0, 0.0)
    daisy.place(f0, cpos, math.radians(-90))
    spos = (7.95, 32.25, 0.0)
    steve.place(f0, spos, yaw_to(spos, (7.95, 31.0)))
    steve.look_at(f0, (7.9, 31.0, 0.75), ease=0)
    use = f0 + 24
    bucket, full = animals.milk(steve, use, f0, f1 + 1)
    steve.raise_arm(f0, 30, ease=0)
    daisy.idle(f0, f1 + 1, seed=7, watch=steve)
    calf.place(f0, (5.4, 30.2, 0.0), 1.0)
    animals.wander(herd, f0, f1 + 1, herd_area, seed=7, place=False)
    s.lens(24, 3.2)
    s.move((7.2, 33.08, 2.0), (7.75, 31.55, 0.8))
    s.focus(bucket)
    st.use(s, steve, daisy, calf, *herd)
    st.hero(s, "bucket", bucket)
    st.lights(s, scale=0.0)
    info["milk_beats"] = dict(use=use, bucket=bucket, full=full)

    # ---- 5. coop: an egg, a blow, a second blow that kills
    s = st.shot("coop", 5.0)
    f0, f1 = s.frame_start, s.frame_end
    info["coop"] = animals.wander(hens, f0, f1 + 1, (carea[0], 33.2, carea[2], carea[3]), seed=9)
    lp = (-9.6, 29.9, 0.0)
    layer.place(f0, lp, math.radians(140))
    layer.idle(f0, f1 + 1, seed=3)
    egg = animals.lay_egg(layer, f0 + 6, seed=5, until=f1 + 1, stage=st)
    sp2, hp = (-6.2, 30.6, 0.0), (-7.3, 30.9, 0.0)
    steve.place(f0, sp2, yaw_to(sp2, hp))
    lucky.place(f0, hp, math.radians(170))
    lucky.idle(f0, f0 + 20, seed=2)
    steve.look_at(f0, lucky, ease=0)
    hit1 = f0 + 20
    steve.swing_arm(hit1 - 2)
    up = lucky.hurt(hit1, attacker=steve)
    steve.track(hit1, up + 6, lucky)
    hit2 = up + 8
    step = steve.walk(hit1 + 6, [sp2, tuple(lucky.pos_at(up) + Vector((1.25, -0.3, 0.0)))], speed=3.4)
    steve.look_at(step, lucky)
    steve.swing_arm(hit2 - 2)
    gone = lucky.die(hit2, camera=s, attacker=steve, max_back=1.2, seed=3, village=v)
    loot = animals.drop_loot(lucky, hit2, seed=2, stage=st)
    s.lens(24, 3.2)
    s.move((-9.2, 26.6, 3.0), (-9.2, 30.9, 0.3))
    s.focus(lucky.head)
    st.use(s, steve, lucky, layer, egg, *hens, *loot)
    st.hero(s, "hen", lucky)
    st.lights(s, scale=0.0)
    info["coop_beats"] = dict(egg=f0 + 6, hit1=hit1, up=up, step=step, hit2=hit2, gone=gone)

    st.finish()
    return film, st, dict(herd=herd, hens=hens, daisy=daisy, calf=calf, henny=henny, pip=pip, layer=layer, lucky=lucky,
                          steve=steve, egg=egg, loot=loot, info=info, v=v, pen=pen, coop=coop)


def report(scene, film, st, cast):
    """Where things are, in numbers, before anything is rendered."""
    from bpy_extras.object_utils import world_to_camera_view

    from engine import animals

    info = cast["info"]
    shots = {s.name: s for s in film.shots}

    def view(point, frame):
        film.goto(frame)
        bpy.context.view_layer.update()
        c = world_to_camera_view(scene, scene.camera, Vector(point))
        return "(x %.0f%% y %.0f%% %.1f away)" % (c.x * 100, (1 - c.y) * 100, c.z)

    print("shots:", [(s.name, s.frame_start, s.frame_end) for s in film.shots])
    print("beats:", {k: {kk: vv for kk, vv in v.items() if isinstance(vv, (int, float))} for k, v in info.items() if k.endswith("beats")})
    daisy, henny, lucky, steve = cast["daisy"], cast["henny"], cast["lucky"], cast["steve"]
    s = shots["walk"]
    for off in (24, 30, 36):
        f = s.frame_start + off
        print("walk +%d: daisy head %s feet %s" % (off, view(daisy.eye_point(f), f), view(daisy.pos_at(f), f)))
    s = shots["hens"]
    for off in (20, 28, 36):
        f = s.frame_start + off
        print("hens +%d: henny head %s, pip %s" % (off, view(henny.eye_point(f), f), view(cast["pip"].pos_at(f), f)))
    s = shots["feed"]
    b = info["feed_beats"]
    f = b["fed"] + 6
    film.goto(f)
    bpy.context.view_layer.update()
    print("feed fed+6 (shot +%d): daisy head %s, wheat %s, steve head %s; gap %.2f" % (
        f - s.frame_start, view(daisy.eye_point(f), f), view(b["wheat"].matrix_world.translation, f),
        view(steve.eye_point(f), f), b["gap"]))
    s = shots["milk"]
    b = info["milk_beats"]
    f = b["use"] + 6
    film.goto(f)
    bpy.context.view_layer.update()
    print("milk use+6 (shot +%d): milk bucket %s, daisy head %s" % (f - s.frame_start, view(b["full"].matrix_world.translation, f),
                                                                 view(daisy.eye_point(f), f)))
    s = shots["coop"]
    b = info["coop_beats"]
    for label, f in (("hit1+5", b["hit1"] + 5), ("hit2+10", b["hit2"] + 10), ("gone+2", b["gone"] + 2), ("gone+14", b["gone"] + 14)):
        print("coop %s (shot +%d): lucky %s z %.2f, steve %s, egg %s, loot %s" % (
            label, f - s.frame_start, view(lucky.pos_at(f), f), lucky.pos_at(f).z, view(steve.eye_point(f), f),
            view(cast["egg"].rest_pos, f), [view(it.rest_pos, f) for it in cast["loot"]]))
    print("coop: frames left after gone: %d" % (s.frame_end - b["gone"]))
    gap, edge = animals.pen_report(cast["herd"], shots["walk"].frame_start, shots["milk"].frame_end, cast["pen"]["area"])
    print("herd over walk..milk: gap %.2f edge %.2f" % (gap, edge))
    # is anybody standing in anybody: daisy / calf / steve against the herd in every shot they share
    worst = (9.0, None)
    for s in film.shots:
        names = st.in_shot[s.name]
        group = [c for n, c in st.cast.items() if n in names and isinstance(c, animals.Animal)]
        for f in range(s.frame_start, s.frame_end + 1, 2):
            live = [(a, a.pos_at(f), a.yaw_at(f)) for a in group if not a.gone_at(f)]
            for i, (a, pa, ya) in enumerate(live):
                for bb, pb, yb in live[i + 1:]:
                    g = animals._gap(a, pa, ya, bb, pb, yb)
                    if g < worst[0]:
                        worst = (g, (s.name, f - s.frame_start, a.name, bb.name))
    print("smallest gap between any two animal bodies in a shot: %.2f %s" % worst)


def main(argv):
    from engine import quick

    scene = quick.reset()
    t0 = time.time()
    film, st, cast = build(scene)
    print("built in %.1f s" % (time.time() - t0))
    report(scene, film, st, cast)
    for arg in argv:
        if ":" not in arg:
            continue
        name, off = arg.split(":")
        shot = next(s for s in film.shots if s.name == name)
        frame = shot.frame_start + int(off)
        film.goto(frame)
        bpy.context.view_layer.update()
        path = os.path.join(quick.TEST_DIR, "check_animals_p_%s_%s.png" % (name, off))
        scene.render.filepath = path
        t1 = time.time()
        bpy.ops.render.render(write_still=True)
        print("wrote %s (frame %d) in %.0f s" % (path, frame, time.time() - t1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
