"""Checker's LONG multi-sky film (21 s, 504 frames: longer than post.SEGMENT_OVER, so --encode works in parts).

    g1 1-120 gold | n1 121-240 night | g2 241-372 gold | n2 373-504 night, gold from frame 433 (sky_change)
    a dip to black on frame 241 = the first frame of the second encode part (out 6, hold 2, back 6)
Meant to be rendered with --step 24 (21 frames) and encoded with --allow-holds.
"""
from engine import shots, village
from films import lookdev as L

FPS = 24
SKIES = {
    "gold": dict(preset="golden", az=215.0, el=24.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
}
PLAN = [("g1", 5.0, "gold"), ("n1", 5.0, "night"), ("g2", 5.5, "gold"), ("n2", 5.5, "night")]
CHANGE = 433
FRONT_CAM = ((5.0, -2.4, 1.45), (9.4, -7.9, 1.9), (5.3, -2.8, 1.45))


def build(scene, sky=None):
    """Build the long film with `sky` active."""
    v = village.build_village(scene, seed=1)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    p0, aim, p1 = FRONT_CAM
    made = {}
    for name, secs, tag in PLAN:
        s = made[name] = st.shot(name, secs, sky=tag)
        s.lens(30, 3.2)
        s.move(p0, aim, p1, ease="linear")
        s.focus(v.anchors["house_a_door"])
        st.lights(s, scale=1.5 if tag == "night" else 1.0, near=v.anchors["house_a_door"], radius=24.0)
    st.lights(made["n2"], scale=1.0, near=v.anchors["house_a_door"], radius=24.0, at=CHANGE)
    st.sky_change(CHANGE, "gold")
    st.dip(made["g2"].frame_start, out=6, hold=2, back=6)
    st.finish()
    caps = [("One", 0.5, 4.0), ("Night", 5.5, 9.9), ("Cut", 9.9, 10.4), ("Day", 10.5, 15.0), ("Ends", 17.5, 20.5)]
    return {"film": film, "captions": caps, "stage": st}
