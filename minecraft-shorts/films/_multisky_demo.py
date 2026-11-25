"""Multi-sky demo: 8.5 narrated seconds in the real village under TWO skies, five sky segments, one module, one
frame directory, one mp4. THE TEMPLATE for a film whose story alternates between day and night.

    "Our house at sunset. / Our house at night. / Then it is morning. / When he sleeps, the night just ends."

    shot          sky              what it proves
    front_gold    gold             house_a's front in golden light, the farmer strolling past its door
    front_night   night            THE SAME PLACE, lit by its door torch and the lamp post: a hard cut between two skies,
                                   and the farmer walks straight through it (one walk() keyed across both shots)
    morning       gold             after a DIP TO BLACK (the encoder's, on the cut): the librarian at the well
    street        night, then gold ONE continuous shot: the camera pushes up the east street, the shepherd walks
                                   toward it, and on the word "ends" the night is over (Stage.sky_change): moon, stars
                                   and torch glow are gone between two frames while camera and walker carry on

The commands a director types (render.py runs each sky in a process of its own and builds only the skies that
have work; every command is resumable and may be interrupted at any frame):

    $TTS tools/narrate.py _multisky_demo                 # the voice: narration/_multisky_demo.wav + .json
    $BPY -m render _multisky_demo --sheet 10             # out/test/_multisky_demo_sheet.png (both skies, the dip)
    $BPY -m render _multisky_demo --still 1.0,3.0 --captioned         # one still per sky: two builds
    $BPY -m render _multisky_demo --frames all --res 360x640 --samples 8 --threads 2 --max-seconds 200
                                                         # preview frames, sky by sky; repeat until "0 to render"
    $BPY -m render _multisky_demo --frames street --res 360x640 --samples 8 --threads 2      # one shot (two skies)
    $BPY -m render _multisky_demo --res 360x640 --samples 8 --encode
                                                         # -> out/preview/_multisky_demo_360x640_8spp.mp4 with sound
  (a final film: the same without --res / --samples / --threads -> out/frames/_multisky_demo/, out/_multisky_demo.mp4)

What to copy into a real film: SKIES at module level, build(scene, sky=None), Stage(..., skies=SKIES, sky=sky), a sky
on every shot, Stage.sky_change for a change inside a shot, Stage.dip for a dip to black, and NOTHING else that
depends on `sky`: every shot, actor, key, torch level and caption exists in both builds (films/lookdev.py Stage).
"""
from engine import narration, shots, village
from films import lookdev as L

FPS = 24

NARRATION = {
    "tail": 1.3,
    "lines": [
        {"text": "Our house at sunset.", "id": "sunset"},
        {"text": "Our house at night.", "id": "night", "pause": 0.6},      # a breath of night before the dip
        {"text": "Then it is morning.", "id": "morning", "pause": 0.5},
        {"text": "When he sleeps, the night just ends.", "id": "sleeps"},
    ],
}

# The two skies of this film (arguments of look.set_time / look.setup_compositor, see films.lookdev.Stage).
# gold: a low sun in the south-west, so that house_a's west front is lit and the camera of the front shots has it
# 100 degrees off its axis. night: the look-dev night (moon in the west, over the far end of the east street).
SKIES = {
    "gold": dict(preset="golden", az=215.0, el=24.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
}

FRONT_CAM = ((5.0, -2.4, 1.45), (9.4, -7.9, 1.9), (5.3, -2.8, 1.45))       # position, aim, position at the end
WALK = [(7.9, -10.5, -0.06), (7.7, -3.0, -0.06)]                           # past house_a's door, toward the lens
NIGHT_TORCHES = 1.5


def _front(st, s, part):
    """house_a's front from the north-west: the door between its two wall torches, the step, the cobblestone base.
    One camera move, split over the two shots (part 0 = its first half under the golden sky, part 1 = its second
    half at night), so the place is the same and the camera keeps drifting in across the cut."""
    p0, aim, p1 = FRONT_CAM
    mid = tuple((a + b) / 2.0 for a, b in zip(p0, p1))
    s.lens(30 if part == 0 else 32, 3.2)                     # the night half is a touch tighter
    s.move(*((p0, aim, mid) if part == 0 else (mid, aim, p1)), ease="linear")
    s.focus(st.v.anchors["house_a_door"])
    s.handheld(0.008, seed=41)
    st.use(s, st.cast["ada"])
    st.hero(s, "farmer", st.cast["ada"])
    if part == 0:
        st.lights(s, scale=1.0, near=st.v.anchors["house_a_door"], radius=16.0)
    else:
        st.lights(s, scale=NIGHT_TORCHES, groups={"house_a": 1.8}, near=st.v.anchors["house_a_door"], radius=24.0)


def shot_morning(st, s):
    """The librarian at the well in the morning sun, seen from the south-east: the sun 80 degrees off the lens."""
    f0, f1 = s.frame_start, s.frame_end
    bo = st.actor("bo", "librarian")
    spot = (2.4, -4.6, -0.06)
    cam = (5.3, -7.6, 1.35)
    bo.place(f0, spot, L.yaw_to(spot, (cam[0] + 1.5, cam[1] + 2.2, 0.0)))
    bo.look_at(f0, (cam[0] + 2.0, cam[1] + 2.6, 1.5), ease=0)
    bo.idle(f0, f1 + 1, seed=5)
    bo.nod(f0 + 14)
    st.use(s, bo)
    s.lens(50, 2.6)
    s.move(cam, L.up(spot, 1.45), (cam[0] - 0.2, cam[1] + 0.1, cam[2]))
    s.focus(bo.head)
    s.handheld(0.01, seed=13)
    st.hero(s, "librarian", bo)
    st.lights(s, scale=1.0, near=spot, radius=14.0)


def shot_street(st, s, change):
    """The east street from its far end (the look-dev night view): the lamp posts, the well behind, the moon over
    it. The shepherd walks up the street toward the lens, the camera pushes in to meet him. ONE shot: at frame
    `change` the sky becomes the golden one and the torches fall back to their daylight level; nothing else
    happens at that frame."""
    f0 = s.frame_start
    cy = st.actor("cy", "shepherd")
    a, b = (12.5, -0.2, -0.06), (21.5, 0.4, -0.06)
    cy.place(f0 - 30, a, L.yaw_to(a, b))
    cy.walk(f0 - 30, [a, b], speed=1.25)                     # in stride on the first frame, and on the change
    st.use(s, cy)
    s.lens(30, 2.8)
    s.move((24.6, 0.9, 0.95), (6.0, -0.2, 5.6), (23.3, 0.85, 1.0), (6.0, -0.2, 4.9), ease="linear")
    s.focus(cy.head)
    s.handheld(0.01, seed=31)
    st.hero(s, "shepherd", cy)
    st.lights(s, scale=1.3)                                  # the night level of the look-dev street ...
    st.lights(s, scale=1.0, at=change)                       # ... and daylight from the change on


def build(scene, sky=None, street=("night", "gold")):
    """Build the demo with `sky` active (None: the first of SKIES): {"film", "captions", "narration", "stage"}.
    street = the skies of the last shot before and after its change (the proof films films/_multisky_uncut_*.py
    pass the same sky twice: the same shot without a sky change, to compare its frames with)."""
    nar = narration.load(__name__, NARRATION, fps=FPS)
    print(nar.summary())

    v = village.build_village(scene, seed=1)
    film = shots.Film(scene, fps=FPS)
    st = L.Stage(scene, film, v, skies=SKIES, sky=sky)        # the active sky and its compositor are built here

    # the cuts are the sentences; every shot names the sky it is filmed under
    lengths = nar.shot_frames([nar.sentence("night"), nar.sentence("morning"), nar.sentence("sleeps")])
    front_gold = st.shot("front_gold", nar.seconds(lengths[0]), sky="gold")
    front_night = st.shot("front_night", nar.seconds(lengths[1]), sky="night")
    morning = st.shot("morning", nar.seconds(lengths[2]), sky="gold")
    last = st.shot("street", nar.seconds(lengths[3]), sky=street[0])
    change = nar.at("ends")                                   # "... the night just ENDS": on that word's frame
    st.sky_change(change, street[1])                          # from here on the same shot is under the golden sky

    # the farmer walks past the door through the cut between the two skies: ONE walk, keyed before the first shot
    ada = st.actor("ada", "farmer")
    f0 = front_gold.frame_start
    ada.place(f0 - 20, WALK[0], L.yaw_to(*WALK))
    ada.walk(f0 - 20, WALK, speed=1.15)                       # she is in front of the door on the cut (frame 43)
    ada.look_at(f0, (FRONT_CAM[0][0] + 1.6, FRONT_CAM[0][1] + 0.4, 1.5), ease=0)
    _front(st, front_gold, 0)
    _front(st, front_night, 1)
    shot_morning(st, morning)
    shot_street(st, last, change)

    st.dip(morning.frame_start, out=3, hold=0, back=3)        # the night passes: black ON the first frame of 'morning'
    st.finish()
    return {"film": film, "captions": nar.captions(), "narration": nar, "stage": st}
