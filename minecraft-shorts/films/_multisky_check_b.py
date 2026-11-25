"""Checker B's test film, written from the documentation alone (films.lookdev.Stage docstring, render.py docstring
"Several skies in one film" / "Dips to black", engine/narration.py docstring; films/_multisky_demo.py as template).

    "Our square at sunset. / The same door at night, until morning comes. / And night again."

    shot      sky               what must be seen
    square    gold              the square in golden light, house_a's front behind the librarian
    door      night, then gold  the same house front at night, torches at 1.7, the farmer ALREADY walking; a slow
                                push-in; on the word "morning" the sky becomes gold and the torches fall to 1.0
    again     night             after a DIP TO BLACK (3 out, 1 held, 3 back): the square at night, moon over the well

    $TTS tools/narrate.py _multisky_check_b
    $BPY -m render _multisky_check_b --sheet 8
    $BPY -m render _multisky_check_b --frames all --res 360x640 --samples 8 --threads 2 --max-seconds 200
    $BPY -m render _multisky_check_b --res 360x640 --samples 8 --encode
"""
from engine import narration, shots, village
from films import lookdev as L

FPS = 24

NARRATION = {
    "tail": 1.1,
    "lines": [
        {"text": "Our square at sunset.", "id": "sunset"},
        {"text": "The same door at night, until morning comes.", "id": "door", "pause": 0.45},
        {"text": "And night again.", "id": "again"},
    ],
}

SKIES = {
    "gold": dict(preset="golden", az=208.0, el=26.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
}

DOOR_AIM = (9.6, -7.6, 1.9)
NIGHT_TORCH = 1.7


def shot_square(st, s):
    """The square in golden light: the librarian in front, house_a's front (the door of the next shot) behind."""
    f0, f1 = s.frame_start, s.frame_end
    bo = st.actor("bo", "librarian")
    spot = (3.2, -6.6, -0.06)
    cam = (-3.4, -9.0, 1.5)
    bo.place(f0, spot, L.yaw_to(spot, (cam[0], cam[1] + 2.0, 0.0)))
    bo.look_at(f0, (cam[0], cam[1] + 1.2, 1.5), ease=0)
    bo.idle(f0, f1 + 1, seed=3)
    st.use(s, bo)
    s.lens(30, 3.2)
    s.move(cam, (9.0, -7.0, 2.2), (-3.1, -8.9, 1.5))
    s.focus(bo.head)
    s.handheld(0.008, seed=7)
    st.hero(s, "librarian", bo)
    st.lights(s, scale=1.0, near=st.v.anchors["house_a_door"], radius=18.0)


def shot_door(st, s, change):
    """house_a's front, a slow push-in. Night at first (torches high); from frame `change` on the same shot is
    under the golden sky and the torches are at their day level. The farmer walks past the door all through it."""
    f0 = s.frame_start
    ada = st.actor("ada", "farmer")
    a, b = (9.0, -9.4, -0.06), (7.6, -4.0, -0.06)
    ada.place(f0 - 24, a, L.yaw_to(a, b))
    ada.walk(f0 - 24, [a, b], speed=0.8)                     # already walking on the first frame of the shot
    st.use(s, ada)
    s.lens(32, 3.2)
    s.move((4.4, -2.2, 1.45), DOOR_AIM, (5.6, -3.7, 1.45), DOOR_AIM, ease="linear")      # the push-in
    s.focus(st.v.anchors["house_a_door"])
    s.handheld(0.008, seed=19)
    st.hero(s, "farmer", ada)
    near = st.v.anchors["house_a_door"]
    st.lights(s, scale=NIGHT_TORCH, near=near, radius=22.0)
    st.lights(s, scale=1.0, near=near, radius=22.0, at=change)


def shot_again(st, s):
    """Night again: the shepherd in the square looks up at the moon over the well."""
    f0, f1 = s.frame_start, s.frame_end
    cy = st.actor("cy", "shepherd")
    spot = (2.4, -5.3, -0.06)
    cam = (6.6, -5.0, 0.9)
    cy.place(f0, spot, L.yaw_to(spot, (-4.0, -8.0, 0.0)))
    cy.look_at(f0, (-8.0, -6.5, 6.0), ease=0)
    cy.idle(f0, f1 + 1, seed=9)
    st.use(s, cy)
    s.lens(28, 2.8)
    s.move(cam, (-7.5, -4.0, 4.8), (6.3, -5.0, 0.9))
    s.focus(cy.head)
    s.handheld(0.008, seed=23)
    st.hero(s, "shepherd", cy)
    st.lights(s, scale=1.4)


def build(scene, sky=None):
    """Build the film with `sky` active: {"film", "captions", "narration", "stage"}."""
    nar = narration.load(__name__, NARRATION, fps=FPS)
    print(nar.summary())

    v = village.build_village(scene, seed=1)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)

    lengths = nar.shot_frames([nar.sentence("door"), nar.sentence("again")])
    square = st.shot("square", nar.seconds(lengths[0]), sky="gold")
    door = st.shot("door", nar.seconds(lengths[1]), sky="night")
    again = st.shot("again", nar.seconds(lengths[2]), sky="night")     # (the default would be gold: the change below)
    change = nar.at("morning")
    st.sky_change(change, "gold")

    shot_square(st, square)
    shot_door(st, door, change)
    shot_again(st, again)

    st.dip(again.frame_start, out=3, hold=1, back=3)
    st.finish()
    return {"film": film, "captions": nar.captions(), "narration": nar, "stage": st}
