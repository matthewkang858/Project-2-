"""Checker probe: Herobrine at NIGHT (the look's night preset has the short strong mist), 20 blocks from a 35 mm
lens, default glow (left) beside glow 7 (right); and the head at the first frames of a watch().

    $BPY -m tools.check_players_night
"""
import math
import os
import sys

import bpy
from mathutils import Vector

from engine import look, shots, village
from engine import players as pl
from films import lookdev

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, "night")
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = lookdev.Stage(scene, film, v, sky)
    s = st.shot("night", 1.0)
    f0 = s.frame_start
    cam = Vector((0.4, 24.0, 1.3))
    hb = pl.add_player(st, "herobrine", "herobrine")
    hb.place(f0, (-0.6, 44.0, 0.0), 0.0)
    hb2 = pl.add_player(st, "herobrine7", "herobrine", glow=7.0)
    hb2.place(f0, (1.6, 44.0, 0.0), 0.0)
    kid = st.actor("kid", "none", child=True)
    kid.place(f0, (5.5, 30.0, 0.0), math.radians(90))
    kid.walk(f0, [(5.5, 30.0, 0.0), (-4.0, 30.0, 0.0)], speed=2.0)
    hb.watch(f0, s.frame_end, kid)
    hb2.watch(f0, s.frame_end, kid)
    for f in (f0, f0 + 2, f0 + 4, f0 + 8, f0 + 12):
        print("frame %d: head yaw %.1f deg, wanted %.1f" % (f, math.degrees(pl.ch._val(hb.head, "rotation_euler", 2, f)),
                                                         math.degrees(hb._aim(kid, f)[0])), flush=True)
    st.use(s, hb, hb2, kid)
    s.lens(35, 4.0)
    s.move(tuple(cam), (0.5, 44.0, 1.5))
    s.focus(hb.head)
    st.lights(s, scale=1.0)
    st.finish()
    print("distance to the lens %.1f blocks" % (Vector((-0.6, 44.0, 1.6)) - cam).length)
    for f in [int(a) for a in argv] or [12]:
        scene.frame_set(f)
        scene.render.filepath = os.path.join(ROOT, "out", "test", "check_players_night_%03d.png" % f)
        bpy.ops.render.render(write_still=True)
        print("wrote", scene.render.filepath, flush=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
