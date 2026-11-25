"""Checker B's second probe film: THREE skies, and the film sets its OWN final quality in build() (the way
tools/render_economics.py recommends for the one-minute films: scene.render.resolution_x / _y and
scene.cycles.samples set by the film; render.py takes them as the film's final settings).

16 frames, four shots of 4 frames: gold, night, dusk, gold. Tiny on purpose (270x480, 8 samples).

    $BPY -m render _multisky_check_b2 --frames all --threads 2        # -> out/frames/_multisky_check_b2/
    $BPY -m render _multisky_check_b2 --encode                        # -> out/_multisky_check_b2.mp4
"""
from engine import shots, village
from films import lookdev as L

SKIES = {
    "gold": dict(preset="golden", az=208.0, el=26.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
    "dusk": dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm"),
}
OWN_RES, OWN_SAMPLES = (270, 480), 8


def build(scene, sky=None):
    """Four 4-frame shots of house_a's front under gold, night, dusk, gold."""
    v = village.build_village(scene, seed=1)
    film = shots.Film(scene, fps=24)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    for i, (name, k) in enumerate((("a", "gold"), ("b", "night"), ("c", "dusk"), ("d", "gold"))):
        s = st.shot(name, 4 / 24.0, sky=k)
        s.lens(30, 3.2)
        s.move((4.4 + 0.2 * i, -2.2, 1.45), (9.6, -7.6, 1.9))
        s.focus(v.anchors["house_a_door"])
        st.lights(s, scale=1.0 if k == "gold" else 1.6)
    st.fade(1, 3, 0.0, 1.0)                                  # the film opens from black over two frames
    st.finish()
    sc = film.scene
    sc.render.resolution_x, sc.render.resolution_y = OWN_RES     # the film's own FINAL quality
    sc.cycles.samples = OWN_SAMPLES
    caps = [("one", 0.0, 0.16), ("two", 0.17, 0.33), ("three", 0.34, 0.49), ("four", 0.5, 0.66)]
    return {"film": film, "captions": caps, "stage": st}
