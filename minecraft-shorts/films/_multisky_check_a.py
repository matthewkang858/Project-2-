"""Checker's tiny multi-sky film (bookkeeping attacks): 30 frames in the real village, two skies.

    shot     frames  sky
    a_gold   1-6     gold
    b_night  7-12    night
    c2_gold   13-18   gold
    d_mixed  19-30   night, gold from frame 25 on (Stage.sky_change)

populate() is shared with the single-sky reference films films/_multisky_check_ref_gold.py / _ref_night.py (the same
scene built the OLD way: look.set_time + look.setup_compositor + Stage(scene, film, v, sky), no SKIES anywhere).
"""
from engine import shots, village
from films import lookdev as L

FPS = 24

SKIES = {
    "dusk": dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm"),
    "gold": dict(preset="golden", az=215.0, el=24.0, bloom=1.0, grade="warm"),
    "moon": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
}

# ---- the knobs the checker turns between scenarios
SHOT_SKY = {"a_gold": "gold", "b_night": "moon", "c2_gold": "gold", "d_mixed": "moon", "e_new": "dusk"}
CHANGE_TO = "gold"
N_SHOTS = 5
B_LENS = 34
WORD = "Dark"
DIP = (2, 1, 2)

FRONT_CAM = ((5.0, -2.4, 1.45), (9.4, -7.9, 1.9), (5.3, -2.8, 1.45))
WALK = [(7.9, -8.5, -0.06), (7.7, -3.0, -0.06)]


def populate(scene, make_stage, multi=True):
    """The whole film; make_stage(scene, film, v) -> Stage builds the sky. multi=False: no sky tags (one sky)."""
    v = village.build_village(scene, seed=1)
    film = shots.Film(scene, fps=FPS)
    st = make_stage(scene, film, v)
    names = ["a_gold", "b_night", "c2_gold", "d_mixed", "e_new"][:N_SHOTS]
    made = {}
    for n in names:
        if multi:
            made[n] = st.shot(n, 0.5 if n == "d_mixed" else 0.25, sky=SHOT_SKY[n])
        else:
            made[n] = st.shot(n, 0.5 if n == "d_mixed" else 0.25)
    ada = st.actor("ada", "farmer")
    ada.place(1 - 20, WALK[0], L.yaw_to(*WALK))
    ada.walk(1 - 20, WALK, speed=1.15)
    p0, aim, p1 = FRONT_CAM
    for n, s in made.items():
        if n == "d_mixed":
            s.lens(30, 2.8)
            s.move((24.6, 0.9, 0.95), (6.0, -0.2, 5.6), (23.3, 0.85, 1.0), (6.0, -0.2, 4.9), ease="linear")
            s.focus((14.0, 0.0, 1.5))
            st.lights(s, scale=1.3)
            st.lights(s, scale=1.0, at=s.frame_start + 6)
            if multi:
                st.sky_change(s.frame_start + 6, CHANGE_TO)
        else:
            s.lens(B_LENS if n == "b_night" else 30, 3.2)
            s.move(p0, aim, p1, ease="linear")
            s.focus(v.anchors["house_a_door"])
            st.use(s, ada)
            st.lights(s, scale=1.5 if SHOT_SKY[n] in ("night", "moon", "dusk") else 1.0, near=v.anchors["house_a_door"], radius=24.0)
    if "c2_gold" in made:
        st.dip(made["c2_gold"].frame_start, out=DIP[0], hold=DIP[1], back=DIP[2])
    st.finish()
    caps = [("Gold", 0.0, 0.25), (WORD, 0.25, 0.5), ("Again", 0.5, 0.75)]
    return {"film": film, "captions": caps, "stage": st}


def build(scene, sky=None):
    """Build the film with `sky` active."""
    return populate(scene, lambda sc, film, v: L.Stage(sc, film, v, skies=SKIES, sky=sky))
# a comment added by the checker while the first sky was rendering
