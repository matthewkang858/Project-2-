"""Reviewer's close-up probe of engine.hostiles at night through the real look (540x960, 16 samples, motion blur):

    $BPY -m tools.check_hostiles_close flash     the creeper in its strongest white flash beside the skeleton at
                                                 full draw (bow_pulling_2), 2.4 blocks from the lens
    $BPY -m tools.check_hostiles_close chest     Steve's two stuck arrows from 1.1 blocks (fletching, shaft, entry)
Output: out/test/check_hostiles_close_<name>.png
"""
import math
import os
import sys

import bpy
from mathutils import Vector

from engine import hostiles, look, players, quick, shots, village
from films import lookdev as L

Y = 40.0


def _clear(b):
    for x in range(-4, 13):
        for y in range(30, 47):
            b.clear_plants(x, y)


def setup():
    scene = quick.reset()
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1, edit=_clear)
    sky = look.set_time(scene, "night", sun_azimuth=176.0, sun_elevation=21.0)
    look.setup_compositor(scene, bloom=1.3, grade="cool")
    film = shots.Film(scene, fps=24)
    st = L.Stage(scene, film, v, sky)
    s = st.shot("close", 3.0)
    st.lights(s, scale=1.3)
    return scene, v, film, st, s


def render(scene, film, frame, name):
    film.goto(int(frame))
    path = os.path.join(quick.TEST_DIR, "check_hostiles_close_%s.png" % name)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("wrote", path, "frame", frame, flush=True)


def flash():
    scene, v, film, st, s = setup()
    f0 = s.frame_start
    cr = hostiles.add_creeper(st, "creeper")
    sk = hostiles.add_skeleton(st, "skeleton")
    steve = players.add_player(st, "steve", "steve")
    cr.place(f0, (4.0, Y, 0.0), math.radians(-25.0))
    sk.place(f0, (5.3, Y + 0.8, 0.0), math.radians(-150.0))
    steve.place(f0, (2.0, Y - 3.0, 0.0), 0.0)
    cr.look_at(f0, steve, ease=0)
    sk.aim(f0, steve, ease=0)
    d0 = f0 + 10
    sk.draw(d0, release=d0 + 40, target=steve)
    fs = d0 + 22 - 31                                    # the 5th flash (+31..33) lands on d0 + 22 (pulling_2)
    cr.fuse(fs)
    want = d0 + 23
    print("frame", want, "white", cr.white_at(want), "swelling", cr.swelling_at(want), "bow", sk.bow_at(want))
    s.lens(35, 4.0)
    mid = Vector((4.6, Y + 0.3, 0.0))
    s.move(tuple(mid + Vector((-0.6, -2.9, 1.2))), tuple(mid + Vector((0.0, 0.0, 1.1))))
    s.focus(cr.head)
    st.use(s, cr, sk)
    st.finish()
    render(scene, film, want, "flash")


def chest():
    scene, v, film, st, s = setup()
    f0 = s.frame_start
    steve = players.add_player(st, "steve", "steve")
    sk = hostiles.add_skeleton(st, "skeleton")
    steve.place(f0, (5.0, Y, 0.0), math.radians(60.0))
    sk.place(f0, (8.5, Y, 0.0), -math.pi / 2.0)
    sk.aim(f0, steve, ease=0)
    fl1 = sk.shoot(f0 + 2, steve, part="chest", knockback=0.1)
    fl2 = sk.shoot(fl1.frames[0] + 1, steve, part="shoulder_l", knockback=0.1)
    m = Vector((5.0, Y, 0.0))
    s.lens(35, 2.8)
    s.move(tuple(m + Vector((0.95, -0.7, 1.55))), tuple(m + Vector((0.0, 0.0, 1.35))))
    s.focus(fl1.stuck)
    st.use(s, steve)
    st.finish()
    render(scene, film, int(fl2) + 16, "chest")


if __name__ == "__main__":
    {"flash": flash, "chest": chest}[sys.argv[1]]()
