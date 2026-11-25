"""Written by tools/multisky_editfilm.py: a film with ONE sky that still binds the name SKIES (empty only at run time)."""
import bpy

from engine import look, shots

SKIES = dict(())


def build(scene):
    """Four frames under one sky, built the way every finished film builds its sky."""
    me = bpy.data.meshes.new("floor")
    me.from_pydata([(-9, -9, 0), (9, -9, 0), (9, 9, 0), (-9, 9, 0)], [], [(0, 1, 2, 3)])
    scene.collection.objects.link(bpy.data.objects.new("floor", me))
    look.set_time(scene, "golden", sun_azimuth=215.0, sun_elevation=24.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    s = film.shot("only", 0.0, 4 / 24.0)
    s.lens(35, 4.0)
    s.move((7.0, -7.0, 2.2), (0.0, 0.0, 1.0))
    film.finalize()
    return {"film": film, "captions": [("one", 0.0, 0.1)]}
