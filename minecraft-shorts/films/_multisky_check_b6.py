"""Checker B's fourth probe: a ONE-sky film written from a shared template that carries an EMPTY `SKIES = {}`
(what a director gets who copies the multi-sky template for a story that has only one sky and empties the table).
render.declares_skies() sees the name; the module has no skies: what does render.py do?"""
from engine import look, shots, village
from films import lookdev as L

SKIES = {}                                   # this story has one sky: built below, as every finished film does


def build(scene, sky=None):
    """One 4-frame shot of house_a's front under the golden sky."""
    v = village.build_village(scene, seed=1)
    sk = look.set_time(scene, "golden", sun_azimuth=208.0, sun_elevation=26.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = L.Stage(scene, film, v, sk)
    s = st.shot("a", 4 / 24.0)
    s.lens(30, 3.2)
    s.move((4.4, -2.2, 1.45), (9.6, -7.6, 1.9))
    s.focus(v.anchors["house_a_door"])
    st.lights(s, scale=1.0)
    st.finish()
    return {"film": film, "captions": [("one", 0.0, 0.16)], "stage": st}
