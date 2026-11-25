"""Independent checker probe for engine/players.py: a 3-second, two-shot film in the real village, rendered through
the real look with motion blur, a few frames at a time.

    $BPY -m tools.check_players_film 1 14 36        # frame numbers -> out/test/check_players_film_<frame>.png
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector

from engine import look, shots, village
from engine import players as pl
from films import lookdev

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = lookdev.Stage(scene, film, v, sky)
    A = v.anchors

    # ---------------- shot A: the square, six players doing six things
    a = st.shot("square", 1.5)
    f0, f1 = a.frame_start, a.frame_end
    z = A["square_s"][2]
    C = Vector((8.4, -12.9, 0.0))
    d = Vector((-0.85, 0.527, 0.0)).normalized()
    r = Vector((d.y, -d.x, 0.0))

    def at(t, u):
        q = C + d * t + r * u
        return (q.x, q.y, z)

    def to_cam(pos, off=0.0):
        return math.atan2(C.x - pos[0], -(C.y - pos[1])) + math.radians(off)

    hero = pl.add_player(st, "hero", "steve")
    pl.equip(hero, "diamond")
    hero.hold("diamond_sword")
    hero.place(f0, at(11.0, -1.2), 0.0)
    hero.walk(f0, [at(11.0, -1.2), at(4.6, 0.3)], ramp=(False, False))

    alex = pl.add_player(st, "alex", "alex")
    pl.equip(alex, boots="golden")
    alex.place(f0, at(13.0, -6.0), 0.0)
    alex.sprint_jump(f0, [at(13.0, -6.0), at(13.0, -6.0 + 4.2767 * 3)])

    kai = pl.add_player(st, "kai", "kai")
    kai.hold("torch")
    kai.place(f0, at(10.0, 2.6), 0.0)
    kai.sneak(f0)
    kai.walk(f0, [at(10.0, 2.6), at(9.0, 1.0)])

    noor = pl.add_player(st, "noor", "noor")
    noor.hold("steak")
    noor.place(f0, at(7.5, -1.3), to_cam(at(7.5, -1.3), 15))
    noor.eat(f0 + 2, f0 + 34)

    efe = pl.add_player(st, "efe", "efe")
    pl.equip(efe, helmet="iron")
    efe.hold("iron_pickaxe")
    efe.place(f0, at(8.5, 1.4), to_cam(at(8.5, 1.4), -25))
    efe.idle(f0, f1 + 1)

    zuri = pl.add_player(st, "zuri", "zuri")
    zuri.hold("shield", hand="left")
    zuri.hold("iron_sword")
    zuri.place(f0, at(6.5, 1.2), to_cam(at(6.5, 1.2), -35))
    zuri.block(f0 + 6, f0 + 30)
    st.use(a, hero, alex, kai, noor, efe, zuri)
    a.lens(30, 4.0)
    a.move((8.4, -12.9, 1.45), tuple(Vector(at(7.5, 0.0)) + Vector((0, 0, 1.1))))
    a.focus(hero.head)
    st.hero(a, "hero", hero)
    st.lights(a, scale=1.0)

    # ---------------- shot B: the exit road; the hero has changed at the cut, Herobrine watches, a fight beside
    b = st.shot("road", 1.5)
    g0, g1 = b.frame_start, b.frame_end
    hero.place(g0, (0.4, 25.0, -0.06), math.pi)
    hero.equip(helmet=None, frame=g0)                    # helmet off and the sword swapped for a torch AT the cut
    hero.hold("torch", frame=g0)
    hero.walk(g0, [(0.4, 25.0, -0.06), (0.9, 28.6, -0.06)], speed=1.7)
    hb = pl.add_player(st, "herobrine", "herobrine")
    hb.place(g0, (0.9, 34.0, -0.06), 0.0)
    hb.watch(g0, g1, hero)
    ari = pl.add_player(st, "ari", "ari")
    ari.hold("iron_sword")
    ari.place(g0, (2.4, 29.0, 0.0), math.radians(90))
    sunny = pl.add_player(st, "sunny", "sunny")
    pl.equip(sunny, chestplate="chainmail")
    sunny.hold("bow")
    sunny.place(g0, (3.7, 29.0, 0.0), math.radians(-90))
    ari.attack(g0 + 6)
    sunny.hurt(g0 + 9, from_point=ari)
    ari.attack(g0 + 20)
    info = sunny.die(g0 + 23)
    print("death info", info, flush=True)
    st.use(b, hero, hb, ari, sunny)
    b.lens(26, 4.0)
    b.move((-1.5, 18.0, 1.35), (1.6, 27.5, 1.2))
    b.focus(hero.head)
    st.hero(b, "hero", hero)
    st.lights(b, scale=1.0)
    st.finish()
    build.film = film
    return scene, (a, b), dict(hero=hero, hb=hb, alex=alex, kai=kai, noor=noor, efe=efe, zuri=zuri, ari=ari, sunny=sunny)


def main(argv):
    t = time.time()
    scene, (a, b), cast = build()
    print("built in %.1f s; shot A %d-%d, shot B %d-%d" % (time.time() - t, a.frame_start, a.frame_end, b.frame_start, b.frame_end), flush=True)
    for arg in argv:
        f = int(arg)
        scene.frame_set(f)
        names = [c.name for c in cast.values()]
        vis = {}
        for o in scene.objects:
            if o.type == "MESH" and not o.hide_render:
                for n in names:
                    if o.name.startswith(n + "_"):
                        vis[n] = vis.get(n, 0) + 1
        print("frame %d: visible meshes per player %s" % (f, vis), flush=True)
        scene.render.filepath = os.path.join(ROOT, "out", "test", "check_players_film_%03d.png" % f)
        scene.render.image_settings.file_format = "PNG"
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print("wrote %s in %.1f s" % (scene.render.filepath, time.time() - t), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
