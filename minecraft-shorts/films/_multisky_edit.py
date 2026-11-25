"""Written by tools/multisky_editfilm.py for tools/multisky_selftest.py: a film of a few frames on a bare set,
rewritten between commands to play a director's edits. Not a film to look at."""
import types

import bpy

from engine import shots
from films import lookdev as L

SKIES = {'gold': {'preset': 'golden', 'az': 215.0, 'el': 24.0, 'bloom': 1.0, 'grade': 'warm'}, 'night': {'preset': 'night', 'az': 176.0, 'el': 21.0, 'bloom': 1.3, 'grade': 'cool'}}
SHOTS = [('a', 6, 'gold'), ('b', 6, 'night'), ('c', 6, 'gold'), ('d', 12, 'night')]
CHANGE = (25, 'gold')
LENS = {'b': 51}
WORD = 'one'


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
