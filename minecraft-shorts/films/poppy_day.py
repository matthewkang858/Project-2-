"""Poppy, part 2 of 2 (golden hour): 8.9 s, three shots, one caption word at a time.

    "He holds out a flower to the children. / One day, / the flower was all we found."

    1 offer   the square, south of the well: a child toddles up to the golem, the golem's arm comes up with the
              poppy ("holds out"), the child looks up at it ("flower"), two more children run in ("children")
    2 empty   the same frame, the camera still on its slow way in: nobody. Only a poppy lies where he held it out,
              turning its flat side to the lens as the shot goes on.
    3 found   low and close on that poppy, turning and bobbing as dropped items do; a farmer, a librarian and the
              child stand around it out of focus, the child nearest, and their heads sink toward it. One second
              on it after "found".
    (The brief's optional Steve walking off with an iron ingot is left out: from this low lens the only free
    background is the frame's right edge, where a blurred figure would be cropped by tall phones and would pull
    the eye off the flower in the last second.)

    $BPY -m render poppy_day --sheet 12
    $BPY -m render poppy_day --still 1.75,4.375,5.5 --res 720x1280 --samples 24 --zones --captioned
    $BPY -m render poppy_day --frames all --step 2 --res 360x640 --samples 8 --max-seconds 240     # preview

Part 1 is films/poppy_night.py; the orchestrator joins the two mp4 files, so frame 1 here follows the night's last
frame as a hard cut and carries the caption "He". The timeline is planned from the captions outward
(poppy_common.Clock, whole frames): the cuts are the first frames of "One" and of the second "the", so the pause
after "children." is the last breath of the offer and the pause after "day," is the empty square.

The golem and the dropped poppy are engine.mobs: the offer pose is the game's (straight right arm, the real poppy
block model in the fist); the eased raise is a film choice (the game snaps). The children are baby villagers, who
have no profession; nobody has fingers or a changing face: everything is said with heads, steps and the camera.
"""
import math

from mathutils import Vector

from engine import look, shots, village
from films.lookdev import Stage, yaw_to
from films.poppy_common import FPS, PATH_Z, SCRIPT_DAY, TITLE, Clock, add_golem, add_item, aside, forward, right

# A warm sun from the south-east at 31 degrees: it comes over the low corner of house_a and lights the south of the
# square, the golem's face (he looks east) and the side of everybody that the camera sees (it looks north).
SKY = dict(preset="golden", az=305.0, el=31.0, bloom=1.0, grade="warm")
# the caption clock, in frames: "He" on frame 1 (the cut from the night), 10 frames a word, 10 more after the comma
# and at the end of a sentence, and one second on the last picture after "found" has gone
CLOCK = dict(start=0, word=10, comma=10, period=10, tail=24)

GOLEM = Vector((2.0, -6.3, PATH_Z))        # where he stands, south of the well, facing east
YAW = math.pi / 2.0
KID = GOLEM + 1.90 * forward(YAW) + 0.62 * right(YAW)        # the child: under the flower, just beyond the fist
LEFT = GOLEM + 0.93 * forward(YAW) + 0.55 * right(YAW)       # where the poppy is found: under the hand that held it
# the camera of shots 1 and 2: one straight, slow push from the south, low; it goes on through the cut, so the
# empty square is the same picture, still closing in on the place where the flower was. (The whole group has to fit
# x 8-82 % to the last frame, the golem's back included: he is 0.9 deep and the push must not carry him out.)
CAM_A, AIM_A = Vector((3.30, -13.30, 0.50)), Vector((3.30, -6.60, 0.47))
CAM_B, AIM_B = Vector((3.30, -12.80, 0.50)), Vector((3.30, -6.60, 0.47))
HAND = (0.008, 61)                         # the same handheld drift in both shots: it does not jump at the match cut


def timing():
    """The clock and the frame count of each shot: cuts on "One" and on the second "the"."""
    clock = Clock(SCRIPT_DAY, **CLOCK)
    return clock, clock.lengths(clock.frame("one"), clock.frame("the", 1))


def _to_lens(c, frame, point, degrees=21.0):
    """The look_at target `point`, swung round child c until its face is `degrees` toward the lens (same distance,
    same height). The lens looks north at a profile: a child that looks straight at the golem's face, which is
    0.6 block beyond it, shows the lens a blank cheek (no brow, no eye); cheated 21 degrees to the camera's side
    of what it looks at, the face reads and the eyeline still goes to the golem and his flower."""
    p, t = c.pos_at(frame), Vector(point)
    r, a = math.hypot(t.x - p.x, t.y - p.y), math.radians(degrees)
    return (p.x - r * math.cos(a), p.y - r * math.sin(a), t.z)


def _run_in(c, arrive, way, speed):
    """Let a child run along `way` so that it stops on frame `arrive`; returns the frame it starts on."""
    dist = sum((Vector(b) - Vector(a)).length for a, b in zip(way, way[1:]))
    start = arrive - int(round(dist / speed * FPS))
    c.place(start, way[0], yaw_to(way[0], way[1]))
    end = c.walk(start, way, speed=speed, run=True)
    assert end == arrive, (end, arrive)
    return start


# ----------------------------------------------------------------------------------------------------
# 1. "He holds out a flower to the children."
# ----------------------------------------------------------------------------------------------------

def shot_offer(st, s, clock):
    """Profile from the golem's right, low, the well with its lantern and the big house behind them under the
    evening sky. Frame 1: a child is on its last steps up to him and his head follows it down. On "holds" the arm
    starts up, the poppy growing out of the fist; it is up, still and sharp before "flower", when the child's
    eyes go from his face to the poppy and it takes one more step toward it. On "children" two more run in from the
    square and look up at it too, and the golem's head goes to them."""
    f0, f1 = s.frame_start, s.frame_end
    g = add_golem(st)
    kid = st.actor("kid", "none", child=True)
    g.place(f0, GOLEM, YAW)
    away = forward(YAW)                                      # from the golem toward the child
    # the first child toddles in from the right: new to the film, so it may start before frame 1
    far = KID + 0.15 * away                                  # where it stops first: a small step short
    start = far + Vector((0.90, 0.10, 0.0))
    arrive = f0 + 4                                          # (inside the safe area from frame 4 of the film's day)
    kid.place(arrive - 12, start, yaw_to(start, far))
    assert kid.walk(arrive - 12, [start, far], speed=1.8) == arrive
    kid.look_at(arrive - 12, _to_lens(kid, arrive - 12, g.eye_point(arrive - 12)), ease=0)   # eyes up at the big face
    g.look_at(f0, kid, ease=0)
    g.track(f0, arrive + 4, kid, step=3, ease=3)             # his head follows the child down
    # "holds out": the arm, 22 frames up (the game snaps; this is the film's gentleness), the poppy in the fist
    # (grow=10: the poppy opens while the arm lifts, not as a pop at the hanging fist)
    up = g.offer_flower(clock.frame("holds") + 1, ease=22, grow=10)
    bloom = g.flower_point(up + 1)
    f_flower = clock.frame("flower")
    assert up <= f_flower - 6, (up, f_flower)                # up and still well before its word
    kid.look_at(f_flower - 5, _to_lens(kid, f_flower + 2, bloom), ease=7)   # "flower": its eyes come down to it
    # ... and one small step closer, under it (0.15 block in 7 frames: in 3 frames it was a hop that stopped dead)
    step = kid.walk(f_flower + 4, [far, KID], speed=0.5)
    kid.look_at(step, _to_lens(kid, step + 5, g.flower_point(step + 2)), ease=5)
    # "children": two more, running in from the square behind (new to the film: pre-rolled, out of frame). One
    # stops beyond the flower, the other under the raised arm beside the golem: both face the poppy and so the
    # lens, clear of the first child and of the Reels icons, and stand still a quarter second before the cut
    f_ch = clock.frame("children")
    k2, k3 = st.actor("kid2", "none", child=True), st.actor("kid3", "none", child=True)
    way2 = [(8.6, -4.4, PATH_Z), (5.6, -4.9, PATH_Z), (3.45, -5.50, PATH_Z)]
    way3 = [(9.4, -3.4, PATH_Z), (6.9, -4.2, PATH_Z), (2.60, -5.30, PATH_Z)]
    # (the one that runs farther arrives only a frame later, so it leads by 0.7 block all the way in: arriving 5
    # frames later it ran a head's width ahead of the other, and the two were one two-headed shape)
    stops = ((k2, f_ch + 1, way2), (k3, f_ch + 2, way3))
    for c, f, way in stops:
        _run_in(c, f, way, speed=3.4)
        c.face(f, (bloom.x, bloom.y, 0.0), ease=5)           # they turn to it as they stop ...
        c.look_at(f + 1, (bloom.x, bloom.y, bloom.z + 0.45), ease=6)     # ... and look up at the flower in the big fist
    # (the target is on the camera's side of the children: his face stays above his raised arm for the lens; turned
    # straight ahead it went behind the arm in the last picture before the match cut)
    g.look_at(f_ch + 2, (4.40, -7.10, 0.85), ease=12)        # his head lifts from the one child to all of them
    st.use(s, g, kid, k2, k3)
    s.lens(32, 1.6)
    s.move(CAM_A, tuple(AIM_A), CAM_B, tuple(AIM_B), ease="linear")
    s.focus(g.flower)
    s.handheld(*HAND)
    st.hero(s, "flower", g.flower)
    st.hero(s, "golem", g)
    st.hero(s, "child", kid)
    st.lights(s, scale=1.0, near=tuple(GOLEM), radius=18.0)  # (daylight: far torches only cost render time)
    return bloom


# ----------------------------------------------------------------------------------------------------
# 2. "One day,"
# ----------------------------------------------------------------------------------------------------

def shot_empty(st, s, clock, bloom):
    """A match cut on absence: the same frame, the same slow push, the same hand (the camera path goes straight
    on through the cut), the same focus distance. The golem and the children are gone. On the path, under where
    the hand was, a single poppy lies as dropped items lie: upright, turning, bobbing."""
    f0 = s.frame_start
    poppy = add_item(st, "poppy")
    poppy.place(f0, LEFT)                                    # (one entity: shot 3 keys its turning for both shots)
    k = (s.frame_end + 1 - f0) / float(f0 - 1)               # this shot's length in shot-1 lengths: the same pace
    s.lens(32, 1.6)
    s.move(CAM_B, tuple(AIM_B), CAM_B + (CAM_B - CAM_A) * k, tuple(AIM_B + (AIM_B - AIM_A) * k), ease="linear")
    s.focus(tuple(bloom))
    s.handheld(*HAND)
    st.use(s, poppy)
    st.hero(s, "poppy", poppy.sprite)
    st.lights(s, scale=1.0, near=tuple(GOLEM), radius=18.0)
    return poppy, f0


# ----------------------------------------------------------------------------------------------------
# 3. "the flower was all we found."
# ----------------------------------------------------------------------------------------------------

def shot_found(st, s, clock, poppy, lying_since):
    """From the ground, a block and a half from the poppy: it is the only sharp thing, turning, its flat side to
    the lens as "flower" comes up. Around it, soft, the ones who found it: the child nearest, a farmer and a
    librarian, who is still looking round for the golem as the shot starts. The child takes half a step toward it;
    the two grown-ups look at each other ("all we"), neither has an answer, and their heads sink back to the
    flower. The camera creeps in and stays one second after "found"."""
    f0, f1 = s.frame_start, s.frame_end
    P = LEFT
    cam0 = Vector((P.x + 0.42, P.y - 1.82, 0.17))
    cam1 = Vector((P.x + 0.36, P.y - 1.56, 0.18))
    down = (P.x, P.y, 0.30)                                  # where everybody looks: the poppy
    kid = st.actor("kid", "none", child=True)
    ada, bo = st.actor("ada", "farmer"), st.actor("bo", "librarian")
    # (the frame is narrow: seen from the lens the farmer stands left and the librarian right, both behind the
    # child, which is in front of the farmer; the poppy has the path and the well's stone behind it. A third
    # grown-up between them was a hat over the child's head: left out.)
    spots = {kid: P + Vector((-0.98, 1.50, 0.0)), ada: P + Vector((-1.50, 2.30, 0.0)),
             bo: P + Vector((0.02, 2.55, 0.0))}
    for c, pos in spots.items():
        c.place(f0, pos, yaw_to(pos, P))
    kid.look_at(f0, down, ease=0)                            # the child has not taken its eyes off it
    ada.look_at(f0, down, ease=0)
    # (every glance below is 20-28 degrees: from this lens a head turned further is a blank box)
    bo.look_at(f0, aside(bo, f0, 28.0, dz=0.25), ease=0)     # the librarian is still looking round for HIM ...
    bo.look_at(clock.frame("flower", 1) - 2, down, ease=10)  # ... and then down, like the others
    f_all, f_found = clock.frame("all"), clock.frame("found")
    # "was": the child takes half a step closer to it (its eyes stay on the flower: a face turned up at one of the
    # grown-ups behind it would be turned away from the lens)
    near = P + Vector((-0.86, 1.22, 0.0))
    kid.walk(clock.frame("was") + 2, [spots[kid], near], speed=1.0)
    ada.look_at(f_all - 2, aside(ada, f_all, 19.0), ease=8)  # "all we": the farmer and the librarian look at each other;
    bo.look_at(f_all + 4, aside(bo, f_all, -21.0), ease=8)   # neither has an answer
    ada.look_at(f_found - 2, down, ease=10)                  # "found": the heads sink back to the flower, and stay
    bo.look_at(f_found + 3, down, ease=11)
    # the poppy: flat side to the lens just before "flower"; a dropped item turns one radian a second, so it is
    # edge-on during "we" and opens again through "found" and the hold
    poppy.face(clock.frame("flower", 1) - 4, cam0)
    poppy.animate(lying_since, f1 + 1)                       # (from the frame shot 2 placed it on)
    st.use(s, poppy, kid, ada, bo)
    s.lens(30, 2.2)
    s.move(cam0, (P.x, P.y, 0.24), cam1, (P.x, P.y, 0.23), ease="ease_out")
    s.focus(poppy.sprite)
    s.handheld(0.006, seed=67)
    st.hero(s, "poppy", poppy.sprite)
    st.lights(s, scale=1.0, near=tuple(P), radius=18.0)


def build(scene):
    """Build the day half of "Poppy" into `scene`: {"film": Film, "captions": [(word, t0, t1), ...], "stage": Stage}."""
    clock, lengths = timing()
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, SKY["preset"], sun_azimuth=SKY["az"], sun_elevation=SKY["el"])
    look.setup_compositor(scene, bloom=SKY["bloom"], grade=SKY["grade"])
    film = shots.Film(scene, fps=FPS)
    st = Stage(scene, film, v, sky)
    s1, s2, s3 = (st.shot(name, n / float(FPS)) for name, n in zip(("offer", "empty", "found"), lengths))
    bloom = shot_offer(st, s1, clock)
    poppy, since = shot_empty(st, s2, clock, bloom)
    shot_found(st, s3, clock, poppy, since)
    st.finish()
    return {"film": film, "captions": clock.caps, "stage": st, "title": TITLE, "clock": clock}
