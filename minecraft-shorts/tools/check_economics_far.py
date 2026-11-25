"""Checker probe for tools/render_economics.py: the shot type the FIRST film depends on and the study did not test.
"The Hello" shows the watcher as a SMALL far figure in beats 7, 9, 10, 13, 15 and 17 (a face under about ten
pixels, white eye texels that must or must not show). A short film-like shot in the real village through the real
look (films.lookdev.Stage, motion blur, depth of field, handheld drift), rendered at the current final (REF,
720x1280 at 24 samples) or at the study's recommendation (E, 540x960 at 16, adaptive minimum 5 as
render.Session.configure sets it), consecutive frames.

    $BPY -m tools.check_economics_far night|golden E|REF FRAME [FRAME ...]
    -> out/test/check_economics_far_<sky>_<mode>_<frame>.png
"""
import math
import os
import sys

import bpy

from engine import look, shots, village
from engine import players as pl
from films import lookdev

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build(sky):
    """The probe film: one shot of 1.5 s under `sky`; returns the scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(720, 1280), samples=24, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1)
    skyd = look.set_time(scene, sky)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = lookdev.Stage(scene, film, v, skyd)
    s = st.shot("far", 1.5)
    f0 = s.frame_start
    kid = st.actor("kid", "none", child=True)
    if sky == "night":
        # he stands 20 blocks from a 35 mm lens and is the subject (in focus); left: eyes glowing (default),
        # right: plain white texels (glow 0); a child crosses the foreground
        hb = pl.add_player(st, "herobrine", "herobrine")
        hb.place(f0, (-0.6, 44.0, 0.0), 0.0)
        hb2 = pl.add_player(st, "herobrine0", "herobrine", glow=0.0)
        hb2.place(f0, (1.6, 44.0, 0.0), 0.0)
        kid.place(f0, (5.5, 30.0, 0.0), math.radians(90))
        kid.walk(f0, [(5.5, 30.0, 0.0), (-4.0, 30.0, 0.0)], speed=2.0)
        hb.watch(f0, s.frame_end, kid)
        hb2.watch(f0, s.frame_end, kid)
        st.use(s, hb, hb2, kid)
        s.lens(35, 4.0)
        s.move((0.4, 24.0, 1.3), (0.5, 44.0, 1.5))
        s.focus(hb.head)
    else:
        # beat 7: the road from the exit gate, low wide lens; the child sharp in the foreground with its back to
        # the lens, he small at the far end, beyond focus. Left: plain Steve, right: the white-eyed skin, no glow
        steve = pl.add_player(st, "steve_far", "steve")
        steve.place(f0, (-0.8, 46.0, 0.0), 0.0)
        hb = pl.add_player(st, "herobrine0", "herobrine", glow=0.0)
        hb.place(f0, (1.8, 46.0, 0.0), 0.0)
        kid.place(f0, (1.3, 25.6, 0.0), math.radians(180))
        kid.idle(f0, s.frame_end + 1, seed=2)
        st.use(s, steve, hb, kid)
        s.lens(28, 3.2)
        s.move((0.2, 22.0, 0.7), (0.5, 46.0, 1.3))
        s.focus(kid.head)
    s.handheld(0.02, seed=3)
    st.lights(s, scale=1.0)
    st.finish()
    return scene


def main(argv):
    sky, mode = argv[0], argv[1]
    frames = [int(a) for a in argv[2:]] or [12]
    scene = build(sky)
    r, c = scene.render, scene.cycles
    if mode == "E":
        r.resolution_x, r.resolution_y = 540, 960
        c.samples = 16
    else:
        r.resolution_x, r.resolution_y = 720, 1280
        c.samples = 24
    c.adaptive_min_samples = max(4, c.samples // 3)          # render.Session.configure
    r.threads_mode, r.threads = "FIXED", 2
    print("[check] %s %s: %dx%d, %d samples, min %d, seed %d, animated seed %s" % (
        sky, mode, r.resolution_x, r.resolution_y, c.samples, c.adaptive_min_samples, c.seed, c.use_animated_seed), flush=True)
    for f in frames:
        scene.frame_set(f)
        r.filepath = os.path.join(ROOT, "out", "test", "check_economics_far_%s_%s_%03d" % (sky, mode, f))
        r.use_file_extension = True
        bpy.ops.render.render(write_still=True)
        print("[check] wrote", r.filepath + ".png", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
