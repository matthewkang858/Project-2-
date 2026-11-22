"""Throwaway pipeline demo (role LOOK): 3 shots of 0.5 s on a stand-in stage made of real block textures.

Only proves that look / shots / captions / post / render.py work end to end; the real films replace it.
    $BPY -m render _demo --still 0.25,0.75,1.25
    $BPY -m render _demo --frames all --step 2 --sheet 6 --encode --allow-holds     # a preview: out/preview/_demo/...
"""
from engine import captions, look, shots


def build(scene):
    """Stand-in stage at golden hour, three shots (wide push-in, long-lens rack focus, low lamp close-up)."""
    look.standin_scene(scene)
    look.set_time(scene, "golden", sun_azimuth=118.0)
    look.setup_compositor(scene, grade="warm")

    film = shots.Film(scene, fps=24)
    a = film.shot("wide", 0.0, 0.5)
    a.lens(35, 2.8)
    a.move((1.6, -9.0, 1.0), (0.3, 3.0, 2.2), (1.2, -7.6, 1.0))
    a.handheld(0.02, seed=1)

    b = film.shot("bricks", 0.5, 1.0)
    b.lens(85, 1.8)
    b.move((-1.2, -9.5, 0.7), (-3.0, 1.5, 1.15), (-0.7, -9.5, 0.7), ease="linear")
    b.focus((-3.0, 1.0, 1.2))
    b.focus((-9.0, 14.0, 3.0), at_s=0.6, rack_s=0.3)

    c = film.shot("lamp", 1.0, 1.5)
    c.lens(50, 1.4)
    c.move((0.9, -1.6, 0.45), (-1.75, 2.35, 1.6), (0.6, -1.9, 0.5))
    c.focus((-1.75, 2.35, 1.7))
    c.handheld(0.015, seed=4)
    film.finalize()

    caps = captions.autotime("Real blocks, real font.", start=0.1, per_word=0.27, comma=0.08, period=0.4)
    return {"film": film, "captions": caps}
