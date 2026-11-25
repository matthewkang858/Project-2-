"""Checker B's ONE-MINUTE probe: 1,440 frames, two skies, FIVE sky segments (gold, night, gold, night, gold), one
sky change inside a shot, three dips (one centred on an encode-part boundary), a fade-in and a fade-out, 150
plain caption words. Meant to be rendered TINY (108x192, 1 sample) to drive the real chunk loop and the long-film
encode (engine.post.encode_parts) end to end:

    $BPY -m render _multisky_check_b5 --frames all --res 108x192 --samples 1 --threads 2 --max-seconds 45   # repeat
    $BPY -m render _multisky_check_b5 --res 108x192 --samples 1 --encode --audio narration/_narrated_demo.wav

    shot  frames      sky            shot  frames       sky
    s01      1- 144   gold           s06   721- 864    gold   (dip ON 721: the boundary of encode parts 3 | 4)
    s02    145- 288   gold           s07   865-1008    night
    s03    289- 432   night (dip)    s08  1009-1152    night, gold from frame 1105 on (in-shot change)
    s04    433- 576   night          s09  1153-1296    gold
    s05    577- 720   gold  (dip)    s10  1297-1440    gold
"""
from engine import shots, village
from films import lookdev as L

FPS = 24
SKIES = {
    "gold": dict(preset="golden", az=208.0, el=26.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
}
SHOT_SKY = ("gold", "gold", "night", "night", "gold", "gold", "night", "night", "gold", "gold")
CHANGE = 1105                     # inside s08: from this frame on the film is gold again
WORDS = ("one two three four five six seven eight nine ten night day door moon sun star well bell torch gold "
         "home walk sleep wake HELLO").split()

DOOR_AIM = (9.6, -7.6, 1.9)
CAMS = (((4.4, -2.2, 1.45), DOOR_AIM, (5.6, -3.7, 1.45), DOOR_AIM, 32),
        ((6.6, -5.0, 0.9), (-7.5, -4.0, 4.8), (5.6, -5.0, 0.9), (-7.5, -4.0, 4.8), 28))


def build(scene, sky=None):
    """Ten 6-second shots; {"film", "captions", "stage"}."""
    v = village.build_village(scene, seed=1)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)
    made = [st.shot("s%02d" % (i + 1), 6.0, sky=k) for i, k in enumerate(SHOT_SKY)]
    st.sky_change(CHANGE, "gold")

    ada = st.actor("ada", "farmer")
    a, b = (9.0, -9.4, -0.06), (7.6, -4.0, -0.06)
    for i, s in enumerate(made):
        p0, t0, p1, t1, mm = CAMS[i % 2]
        s.lens(mm, 3.2)
        s.move(p0, t0, p1, t1, ease="linear")
        s.focus(v.anchors["house_a_door"])
        if i % 2 == 0:                                       # the farmer walks past the door in every other shot
            ada.place(s.frame_start, a, L.yaw_to(a, b))
            ada.walk(s.frame_start, [a, b], speed=0.8)
            st.use(s, ada)
        st.lights(s, scale=1.6 if SHOT_SKY[i] == "night" else 1.0)
    st.lights(made[7], scale=1.0, at=CHANGE)

    st.fade(1, 7, 0.0, 1.0)                                  # the film opens from black
    st.dip(made[2].frame_start, out=3, hold=0, back=3)       # 289: gold -> night
    st.dip(made[4].frame_start, out=4, hold=4, back=4)       # 577: night -> gold
    st.dip(made[5].frame_start, out=5, hold=1, back=5)       # 721: ON the boundary of two encode parts
    st.fade(1434, 1440, 1.0, 0.0)                            # ... and ends in black
    st.finish()

    caps = [(WORDS[i % len(WORDS)], 0.4 * i, 0.4 * i + 0.36) for i in range(150)]
    return {"film": film, "captions": caps, "stage": st}
