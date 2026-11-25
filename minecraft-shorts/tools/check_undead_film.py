"""Checker's film-like probe of engine/undead.py in the real village, through the real look and films.lookdev.Stage.

Run:  $BPY -m tools.check_undead_film street|hall [frame offsets ...]
Writes out/test/check_undead_<scenario>_<label>.png (540x960, 16 samples, 2 threads, motion blur).
"""
import math
import os
import sys
import time

import bpy


def build(which):
    from films import lookdev

    from engine import characters as ch
    from engine import fx, look, props, quick, shots, village
    from engine import undead as U

    scene = quick.reset()
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1)
    marks = {}
    if which == "street":
        sky = look.set_time(scene, "night", sun_azimuth=176.0, sun_elevation=21.0)
        look.setup_compositor(scene, bloom=1.3, grade="cool")
        film = shots.Film(scene, fps=24)
        st = lookdev.Stage(scene, film, v, sky)
        s1 = st.shot("attack", 4.0)
        s2 = st.shot("kill", 2.5)
        f0 = s1.frame_start
        Z = -0.0625
        z = U.add_zombie(st, "zombie")
        vil = st.actor("farmer", "farmer")
        zv = U.add_zombie_villager(st, "farmer_z", "farmer")
        # the zombie walks east along the lane to the farmer, who stands facing him
        w0 = f0 - 24
        z.place(w0, (-21.85, 1.2, Z), math.radians(90))
        z.aggro(w0, True, ease=0)
        arrive = z.walk(w0, [(-21.85, 1.2, Z), (-16.35, 1.2, Z)])
        vil.place(f0, (-15.1, 1.2, Z), math.radians(-90))
        vil.look_at(f0, z, ease=0)
        z.track(f0, arrive, vil)
        blow1 = arrive + 1
        z.attack(blow1, target=vil, max_back=0.9)
        z.aggro(blow1, False, ease=0)
        z.aggro(blow1 + 12, True, ease=0)
        blow2 = blow1 + 24
        z.attack(blow2)
        end = U.infect(vil, zv, blow2, attacker=z, max_back=0.6)
        z.aggro(blow2, False, ease=0)
        st.use(s1, z, vil, zv)
        s1.lens(28, 4.0)
        s1.move((-12.8, -2.7, 0.9), (-15.6, 1.2, 1.15))
        s1.focus((-15.6, 1.2, 1.3))
        st.hero(s1, "zombie", z)
        st.lights(s1, scale=1.3)
        # shot 2: Steve kills the zombie (the farmer and the zombie villager are not in this shot)
        f1 = s2.frame_start
        steve = st.actor("steve", "steve")
        z.place(f1, (-16.4, 1.0, Z), math.radians(90))
        steve.place(f1, (-15.1, 1.0, Z), math.radians(-90))
        steve.look_at(f1, z, ease=0)
        z.look_at(f1, steve, ease=0)
        hit1 = f1 + 6
        fx.arm_swings(steve, [hit1 - 1, hit1 + 17])
        z.hurt(hit1, attacker=steve)
        kill = hit1 + 18
        gone = z.die(kill, camera=s2, attacker=steve, village=v, seed=3, glow=0.25)
        st.use(s2, z, steve)
        s2.lens(26, 4.0)
        s2.move((-12.8, -2.7, 1.1), (-16.6, 1.0, 1.0))
        s2.focus((-16.5, 1.0, 1.2))
        st.hero(s2, "zombie", z)
        st.lights(s2, scale=1.3)
        marks = dict(f0=f0, w0=w0, arrive=arrive, blow1=blow1, blow2=blow2, infect_end=end, f1=f1, hit1=hit1, kill=kill, gone=gone)
    else:
        sky = look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0)
        look.setup_compositor(scene, bloom=1.0, grade="warm")
        film = shots.Film(scene, fps=24)
        st = lookdev.Stage(scene, film, v, sky)
        s1 = st.shot("cure", 5.0)
        f0 = s1.frame_start
        A = v.anchors
        cell = A["cell_3"]
        spot = (cell[0], cell[1] - 0.25, cell[2])
        zv = U.add_zombie_villager(st, "lib_z", "librarian")
        lib = st.actor("lib", "librarian")
        steve = st.actor("steve", "steve")
        apple = props.make_item("golden_apple")
        steve.hold(apple)
        # Steve stands in the aisle in front of the cell, a little to the side so the camera sees both
        sp = (cell[0] - 0.9, cell[1] + 2.6, 0.0)
        steve.place(f0, sp, 0.0)
        zv.place(f0, spot, v.yaws["cell_3"])
        steve.face(f0, zv, ease=0)
        steve.look_at(f0, zv, ease=0)
        zv.look_at(f0, steve, ease=0)
        throw = f0 + 8
        hit = U.throw_potion(steve, zv, throw, camera=s1, village=v, seed=5)
        use = int(hit) + 22
        res = U.cure(zv, lib, use, use + 60, camera=s1, player=steve, weakness_from=int(hit), seed=2, nausea=60)
        st.use(s1, zv, lib, steve)
        s1.lens(30, 4.0)
        cam0 = (cell[0] - 3.3, cell[1] + 2.9, 1.5)
        s1.move(cam0, (cell[0] - 0.2, cell[1] + 0.9, 1.25))
        s1.focus(zv.head)
        st.hero(s1, "zombie villager", zv)
        st.lights(s1, scale=0.0, groups={"hall": 0.8}, inside="hall")
        marks = dict(f0=f0, throw=throw, hit=int(hit), use=use, cured=res["frame_end"], speed=hit.speed)
    st.finish()
    return scene, film, marks


def main(argv):
    which = argv[0]
    t0 = time.time()
    scene, film, marks = build(which)
    print("MARKS", marks, "built in %.1f s" % (time.time() - t0))
    from engine import quick

    for spec in argv[1:]:
        if time.time() - t0 > 215:
            print("SKIPPED (time):", spec)
            continue
        if "+" in spec or "-" in spec[1:]:
            key, off = (spec.split("+") + ["0"])[:2] if "+" in spec else spec.rsplit("-", 1)
            frame = marks[key] + (int(off) if "+" in spec else -int(off))
        elif spec in marks:
            frame = marks[spec]
        else:
            frame = int(spec)
        film.goto(frame)
        path = os.path.join(quick.TEST_DIR, "check_undead_%s_%s.png" % (which, spec.replace("+", "p").replace("-", "m")))
        scene.render.filepath = path
        t1 = time.time()
        bpy.ops.render.render(write_still=True)
        print("WROTE", path, "frame", frame, "%.1f s" % (time.time() - t1))


if __name__ == "__main__":
    main(sys.argv[1:])
