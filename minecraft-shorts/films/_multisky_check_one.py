"""Checker's film: SKIES with ONE entry (a film that starts with one sky and may get a second later); shots untagged."""
from engine import shots, village
from films import lookdev as L

SKIES = {"gold": dict(preset="golden", az=215.0, el=24.0, bloom=1.0, grade="warm")}


def build(scene, sky=None):
    """Six frames under the only sky."""
    v = village.build_village(scene, seed=1)
    film = shots.Film(scene, fps=24)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    s = st.shot("only", 0.25)
    s.lens(30, 3.2)
    s.move((5.0, -2.4, 1.45), (9.4, -7.9, 1.9))
    st.lights(s, scale=1.0)
    st.finish()
    return {"film": film, "captions": [], "stage": st}
