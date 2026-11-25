"""The film tools/multisky_selftest.py edits: writes films/_multisky_edit*.py, tiny films with several skies on a
bare set (a floor and a box: built in a tenth of a second), whose timeline, skies and form the self-test rewrites
between commands to play a director's edits (a new shot, a longer film, a renamed sky, a re-tagged shot, SKIES
arriving through a star import or not visible in the source at all, an empty SKIES).

    from tools import multisky_editfilm as E
    E.write()                                   # films/_multisky_edit.py, the base film (30 frames, gold / night)
    E.write(shots=E.SHOTS + [("e", 6, "night")])        # ... with one more shot
    E.remove_all()                              # every film and frame directory this module made

Not a film to look at, and not a template: the template for a real film is films/_multisky_demo.py.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILM = "_multisky_edit"
OTHERS = ("_multisky_edit_star", "_multisky_edit_hidden", "_multisky_edit_empty", "_multisky_edit_none")

SKIES = {"gold": dict(preset="golden", az=215.0, el=24.0, bloom=1.0, grade="warm"),
         "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool")}
SHOTS = [("a", 6, "gold"), ("b", 6, "night"), ("c", 6, "gold"), ("d", 12, "night")]      # (name, frames, sky)
CHANGE = (25, "gold")                           # a sky change inside 'd'

TEMPLATE = '''"""Written by tools/multisky_editfilm.py for tools/multisky_selftest.py: a film of a few frames on a bare set,
rewritten between commands to play a director's edits. Not a film to look at."""
import types

import bpy

from engine import shots
from films import lookdev as L

%(skies_line)s
SHOTS = %(shots)r
CHANGE = %(change)r
LENS = %(lens)r
WORD = %(word)r


def _set(scene):
    """A floor and a box."""
    for name, verts, faces in (
            ("floor", [(-9, -9, 0), (9, -9, 0), (9, 9, 0), (-9, 9, 0)], [(0, 1, 2, 3)]),
            ("box", [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0), (-1, -1, 2), (1, -1, 2), (1, 1, 2), (-1, 1, 2)],
             [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])):
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        scene.collection.objects.link(bpy.data.objects.new(name, me))


def build(scene, sky=None):
    """The film with `sky` active."""
    _set(scene)
    film = shots.Film(scene, fps=24)
    v = types.SimpleNamespace(lantern_lights=[], cutaways={}, anchors={})
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    for name, n, k in SHOTS:
        s = st.shot(name, n / 24.0, sky=k)
        s.lens(LENS.get(name, 35), 4.0)
        s.move((7.0, -7.0, 2.2), (0.0, 0.0, 1.0), (6.0, -7.6, 2.2), ease="linear")
    if CHANGE:
        st.sky_change(*CHANGE)
    st.finish()
    return {"film": film, "captions": [(WORD, 0.0, 0.2)], "stage": st}
%(tail)s'''

ONE_SKY = '''"""Written by tools/multisky_editfilm.py: a film with ONE sky that still binds the name SKIES (%(how)s)."""
import bpy

from engine import look, shots

SKIES = %(skies)s


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
'''


def path(film=FILM):
    return os.path.join(ROOT, "films", film + ".py")


def _put(film, text):
    tmp = path(film) + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path(film))
    return path(film)


def write(skies=None, shots=None, change=CHANGE, lens=None, word="one", skies_line=None, tail="", film=FILM):
    """Write the film with these knobs. skies_line = the source line(s) that bind SKIES (default: a plain
    module-level assignment of `skies`)."""
    skies = SKIES if skies is None else skies
    return _put(film, TEMPLATE % dict(skies_line=skies_line or "SKIES = %r" % (skies,),
                                     shots=SHOTS if shots is None else shots, change=change, lens=lens or {},
                                     word=word, tail=tail))


def write_star():
    """films/_multisky_edit_star.py: SKIES and build arrive through a star import."""
    return _put(OTHERS[0], '"""Written by tools/multisky_editfilm.py: the edit film through a star import."""\n'
                           'from films.%s import *        # noqa: F401,F403  (SKIES, build)\n' % FILM)


def write_hidden():
    """films/_multisky_edit_hidden.py: SKIES exists only once the module has run (nothing in the source binds the name)."""
    return _put(OTHERS[1], '"""Written by tools/multisky_editfilm.py: the edit film, its SKIES not visible in the source."""\n'
                           'import films.%s as _m\n\nglobals().update({"SK" + "IES": _m.SKIES, "build": _m.build})\n' % FILM)


def write_empty():
    """films/_multisky_edit_empty.py: one sky, and `SKIES = {}` in the source."""
    return _put(OTHERS[2], ONE_SKY % dict(how="an empty literal", skies="{}"))


def write_none():
    """films/_multisky_edit_none.py: one sky, and a SKIES that is empty only once the module has run."""
    return _put(OTHERS[3], ONE_SKY % dict(how="empty only at run time", skies="dict(())"))


def frame_dirs(film):
    """Every frame directory of a film that exists (final and previews)."""
    out = [os.path.join(ROOT, "out", "frames", film)]
    prev = os.path.join(ROOT, "out", "preview", film)
    if os.path.isdir(prev):
        out += [os.path.join(prev, d) for d in sorted(os.listdir(prev))]
    return [d for d in out if os.path.isdir(d)]


def clear(film=FILM):
    """Delete the frame directories, preview mp4s and encode parts of one of this module's films, file by file."""
    if film != FILM and film not in OTHERS:
        raise ValueError("not a film of this module: %r" % film)
    for d in frame_dirs(film):
        for root, dirs, files in os.walk(d, topdown=False):
            for fn in files:
                os.remove(os.path.join(root, fn))
            os.rmdir(root)
    prev = os.path.join(ROOT, "out", "preview")
    if os.path.isdir(prev):
        for fn in sorted(os.listdir(prev)):
            if fn.startswith(film + "_") and fn.endswith(".mp4") and not any(
                    fn.startswith(o + "_") for o in OTHERS if o != film and len(o) > len(film)):
                os.remove(os.path.join(prev, fn))
        if os.path.isdir(os.path.join(prev, film)) and not os.listdir(os.path.join(prev, film)):
            os.rmdir(os.path.join(prev, film))


def remove_all():
    """Delete every film module and frame directory this module made."""
    for film in (FILM,) + OTHERS:
        clear(film)
        if os.path.exists(path(film)):
            os.remove(path(film))
