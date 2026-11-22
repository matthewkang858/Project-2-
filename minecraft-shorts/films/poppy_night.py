"""Poppy, part 1 of 2 (night): the villagers about their iron golem. 3.9 s, two shots, one caption word at a time.

    "He doesn't sleep. / He doesn't eat."

    1 patrol   the iron golem walks his round up the east street at night, alone, toward the lens, into the
               light of a lamp post: the well behind him, the square moon, stars. He is in stride on frame 1.
    2 watch    close on head and shoulders: he stands watch at the edge of the lamp light, the moon behind him, and
               his head comes round to look down the street, past the lens. A guard, not a monster.

    $BPY -m render poppy_night --sheet 12
    $BPY -m render poppy_night --still 1.2083,3.0833 --res 720x1280 --samples 24 --zones --captioned
    $BPY -m render poppy_night --frames all --step 2 --res 360x640 --samples 8 --max-seconds 240     # preview

Part 2 is films/poppy_day.py (the sky changes, and a module has one sky); the orchestrator joins the two mp4 files,
so the last frame here cuts hard to the day. The timeline is planned from the captions outward (poppy_common.Clock,
whole frames): "He" comes up on frame 4, the cut is the first frame of the second "He", and the module ends with
the last frame of "eat" (its sentence pause is the last breath of the night).

Moon and torch level are the look-dev night (films/lookdev.py shot_night, reference 3) and shot 1 is its street
view moved in on the golem (28 mm); the golem is engine.mobs (planted gait: his feet are in frame in shot 1).
"""
import math

from engine import look, shots, village
from films.lookdev import Stage, yaw_to
from films.poppy_common import FPS, PATH_Z, SCRIPT_NIGHT, TITLE, Clock, add_golem, clear_for_golem

SKY = dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool")        # the look-dev night, unchanged
# the caption clock, in frames: "He" on frame 4, 11 frames a word, 12 more at the end of a sentence
CLOCK = dict(start=3, word=11, comma=4, period=12)
TORCHES = 1.3                              # the look-dev night level (lit stone sits near the palette limit above it)


def timing():
    """The clock and the frame count of each shot: the cut is on the second "He"."""
    clock = Clock(SCRIPT_NIGHT, **CLOCK)
    return clock, clock.lengths(clock.frame("he", 1))


# ----------------------------------------------------------------------------------------------------
# 1. "He doesn't sleep."
# ----------------------------------------------------------------------------------------------------

def shot_patrol(st, s, clock):
    """The east street from its far end, low, as in the look-dev night (reference 3): the lamp post big in the upper
    left, the well and the square behind, the moon on the right. The golem comes up the street toward the lens at
    the game's stroll, into the lamp's light, and is beside the post as the shot ends. His feet are in frame, so
    the gait is the planted one, and the walk starts on the cut at full speed (ramp=(0, 8)): frame 1 is already a
    step. Half way he turns his head to the dark side of the street and back: he is on his round. The camera
    eases toward him and tilts up as he grows."""
    v = st.v
    f0, f1 = s.frame_start, s.frame_end
    g = add_golem(st)
    a, b = (15.0, -0.35, PATH_Z), (21.0, -0.35, PATH_Z)      # east of the hay bales (x 12-13); 2.1 from the lamp post
    clear_for_golem(v, [a, b])
    g.place(f0, a, yaw_to(a, b))
    g.walk(f0, [a, b], ramp=(0, 8))                          # (he walks on past the cut; shot 2 places him anew)
    # the round: a look across at the houses on the north side (20 degrees: the face stays a face), then ahead
    fd = clock.frame("doesn't")
    here = g.pos_at(fd + 8)
    g.look_at(fd - 4, (here.x + 6.0, here.y + 2.6, 1.9), ease=12)
    g.look_at(clock.frame("sleep") + 2, (here.x + 9.0, here.y - 0.3, 1.6), ease=12)
    g.step_crumbs(f0, f1 + 1, camera=s, village=v, seed=4, glow=0.2)       # the game's crumbs under a walking golem
    s.lens(28, 2.8)
    # (from the middle of the street: the moon stands inside the safe area, at 78-83 % of the width)
    s.move((21.9, 0.15, 0.92), (14.6, -1.00, 2.40), (21.6, 0.13, 0.94), (14.6, -1.00, 2.52))
    s.focus(g.head)
    s.handheld(0.01, seed=31)
    st.use(s, g)
    st.hero(s, "golem", g)
    st.lights(s, scale=TORCHES)


# ----------------------------------------------------------------------------------------------------
# 2. "He doesn't eat."
# ----------------------------------------------------------------------------------------------------

def shot_watch(st, s, clock):
    """Head and shoulders, from below his eyes: he stands in the street where the lamp's light ends (the lamp is
    off-frame, camera-left: warm on the right side of his face, the moon cool on the other). The shot opens with his
    eyes on the houses across the street; his head comes round, slowly, as a golem's does, and from "eat" on he
    looks down the street past the lens, and stays. The camera pushes in a hand's width."""
    f0, f1 = s.frame_start, s.frame_end
    g = add_golem(st)
    spot = (15.5, 0.5, PATH_Z)
    g.place(f0, spot, math.pi / 2.0)                         # facing east, down the street
    g.look_at(f0, (19.6, 3.4, 2.1), ease=0)                  # 36 degrees to his left: the smithy's porch
    fe = clock.frame("eat")
    # ... and round to the street, slowly, as a golem turns its head: three quarters of the way on "eat", at rest
    # ten frames later, his eyes going past the lens and down the street
    g.look_at(f0 + 2, (23.0, -2.45, 1.80), ease=fe + 10 - f0 - 2)
    s.lens(40, 2.8)
    # (linear: an eased-out push was a freeze frame for the last half second before the cut to the day)
    s.move((19.45, -0.32, 1.55), (15.6, 0.47, 1.90), (19.15, -0.26, 1.57), (15.6, 0.47, 1.93), ease="linear")
    s.focus(g.head)
    s.handheld(0.008, seed=43)
    st.use(s, g)
    st.hero(s, "golem", g)
    st.lights(s, scale=TORCHES)


def build(scene):
    """Build the night half of "Poppy" into `scene`: {"film": Film, "captions": [(word, t0, t1), ...], "stage": Stage}."""
    clock, lengths = timing()
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, SKY["preset"], sun_azimuth=SKY["az"], sun_elevation=SKY["el"])
    look.setup_compositor(scene, bloom=SKY["bloom"], grade=SKY["grade"])
    film = shots.Film(scene, fps=FPS)
    st = Stage(scene, film, v, sky)
    for (name, fn), n in zip((("patrol", shot_patrol), ("watch", shot_watch)), lengths):
        fn(st, st.shot(name, n / float(FPS)), clock)
    st.finish()
    return {"film": film, "captions": clock.caps, "stage": st, "title": TITLE, "clock": clock}
