"""The Bell: an 11.3 s vertical short at dusk, four shots, one caption word at a time.

    "When the bell rings, / we run home. / We count who made it. / He rings it because he likes the sound."

    1 bell      the village bell swinging on its bar, close: an alarm, rung on a steady beat that lands on "rings"
    2 run       villagers sprint across the square for house_a's door, the camera running backwards ahead of them
    3 interior  inside house_a: the last one is in, the door swings shut (in focus), heads turn to the one empty bed
    4 steve     Steve alone in the empty square, ringing the bell again and again

    $BPY -m render bell --sheet 12
    $BPY -m render bell --still 1.7083,2.75,4.125,5.5834,9.75 --res 720x1280 --samples 24 --zones --captioned
                                                  # (4.125 = the door of shot 3 half shut; 5.5834 = the empty bed)
    $BPY -m render bell --frames all --step 2 --res 360x640 --samples 8 --max-seconds 240      # preview, resumable

The film is planned from the captions outward: CLOCK below is the whole timing, in frames. Every word starts on a
frame, the three cuts are the first frames of "we", "We" and "He" (the pause after a sentence is the last picture of
its shot), and the film holds TAIL frames on Steve and the swinging bell after "sound" has gone.

Camera, lens, staging and torch levels of every shot are the look-dev setups of films/lookdev.py (shot_bell,
shot_run, shot_interior, shot_steve_bell: palette- and safe-area-checked there); this file adds the time: who
moves when, and what each word sees.
"""
import math

from engine import captions, characters, look, shots, village
from films.lookdev import Stage, up, yaw_to

FPS = 24
TITLE = "The Bell"
SCRIPT = "When the bell rings, we run home. We count who made it. He rings it because he likes the sound."

# the caption clock, in frames (24 fps): first word, every word, extra hold after a comma / after a sentence, and
# how long the last picture stays once the last word has gone
CLOCK = dict(start=3, word=11, comma=4, period=8, tail=24)

SKY = dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm")     # the look-dev dusk, unchanged
BEDS = {"house_a_bed_2": "red"}            # the bed nobody came home to: the red one everybody knows

RUN = characters.RUN_SPEED / FPS           # blocks per frame of a sprinting villager

# the people who live in house_a: name, profession, sideways offset on the square (+ = north), frames behind the
# farmer in the run, make_villager arguments. (The shepherd runs wide on the north side: at 0.6 / 17 frames he was
# behind the farmer's body for the whole shot, and then came from nowhere as the last one in.)
FAMILY = [("ada", "farmer", 0.0, 0, {}), ("kid", "farmer", 0.85, 5, dict(child=True)),
          ("bo", "librarian", -0.8, 9, {}), ("cy", "shepherd", 1.5, 13, {})]


def timing():
    """The captions and the cut frames they imply: (captions, {word index: frame}, [frame count of each shot])."""
    c = CLOCK
    # (a quarter frame early: autotime rounds its times to 4 decimals and a frame shows the word whose t0 <= its
    # own time, so a start such as 1.0417 s, rounded UP past frame 26, came on one frame late)
    caps = captions.autotime(SCRIPT, start=(c["start"] - 0.25) / FPS, per_word=c["word"] / FPS,
                             comma=c["comma"] / FPS, period=c["period"] / FPS)
    frame = {i: int(round(t0 * FPS)) + 1 for i, (_w, t0, _t1) in enumerate(caps)}
    words = [w for w, _a, _b in caps]
    cuts = [frame[words.index("we")], frame[words.index("We")], frame[words.index("He")]]
    end = int(round(caps[-1][2] * FPS)) + 1 + c["tail"]          # first frame AFTER the film
    edges = [1] + cuts + [end]
    return caps, frame, [b - a for a, b in zip(edges, edges[1:])]


def _bell_curve(v):
    """The F-curve of the bell's swing (rotation about its bar), or None before the first ring."""
    for fc in shots.fcurves_of(v.bell):
        if fc.data_path == "rotation_euler" and fc.array_index == 0:
            return fc
    return None


def ring(v, frame, strength=1.0):
    """Ring the bell at `frame` (Village.ring_bell). When it is still swinging from the ring before, the 'at rest'
    key that ring_bell puts on the frame before is taken out again: the bell is pushed on out of its swing instead
    of stopping dead for a frame."""
    fc = _bell_curve(v)
    moving = fc is not None and abs(fc.evaluate(frame - 2)) > math.radians(0.5)
    end = v.ring_bell(frame, strength=strength, swings=5)
    if moving:
        fc = _bell_curve(v)
        for kp in list(fc.keyframe_points):
            if abs(kp.co.x - (frame - 1)) < 1e-3:
                fc.keyframe_points.remove(kp)
        fc.update()
    return end


def _aside(c, frame, degrees, dz=0.0, dist=3.0):
    """A point `degrees` to the left (+) or right (-) of where character c faces at `frame`, at its eye height + dz:
    a look_at target for a glance that still shows the face (beyond about 55 degrees a villager seen from the front
    is a blank cheek)."""
    yaw, a = c.yaw_at(frame), math.radians(degrees)
    fx, fy = math.sin(yaw), -math.cos(yaw)
    p = c.pos_at(frame)
    return (p.x + dist * (fx * math.cos(a) - fy * math.sin(a)), p.y + dist * (fx * math.sin(a) + fy * math.cos(a)),
            p.z + c.eye_height + dz)


def _surface(v, x, y):
    """Walking height on the square at (x, y): a dirt path is one pixel lower than grass."""
    return -1.0 / 16.0 if v.world.block_id(int(math.floor(x)), int(math.floor(y)), -1) == "dirt_path" else 0.0


def _run_path(v, base, side, back):
    """The run to house_a's door for one villager: the square_to_house_a path shifted `side` blocks sideways while it
    crosses the square (funnelling into the door), and starting `back` blocks before its first point, on the same line."""
    (x0, y0, _z0), (x1, y1, _z1) = base[0], base[1]
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    pts = [(p[0], p[1] + side * (1.0 if p[0] < 8.0 else 0.15), p[2]) for p in base]
    sx, sy = x0 - ux * back, y0 - uy * back + side
    return [(sx, sy, _surface(v, sx, sy))] + pts


# ----------------------------------------------------------------------------------------------------
# 1. "When the bell rings,"
# ----------------------------------------------------------------------------------------------------

def shot_bell(st, s, at):
    """The bell, close, on the long lens of the look-dev (seen from the south-east, the west lamp its key). It is
    an alarm: rung on the 22-frame beat Steve keeps in the last shot, the third hit on the frame the word "rings"
    appears. The first hit was 8 frames before the film starts, so frame 1 is high in its swing and moving, and the
    swing never dies away (13-17 degrees throughout)."""
    v, A = st.v, st.v.anchors
    f0 = s.frame_start
    beat = 2 * CLOCK["word"]
    for k in (2, 1, 0):
        ring(v, at["rings"] - k * beat)
    bell = A["bell"]
    s.lens(105, 1.4)
    s.move((1.06, -9.50, 0.915), up(bell, -0.13), (0.93, -9.10, 0.94), ease="ease_out")     # a slow push-in
    s.focus(up(bell, 0.0))
    s.handheld(0.012, seed=3)
    st.hero(s, "bell", v.bell)
    st.lights(s, scale=0.9, groups={"bell_w": 2.4, "bell_e": 0.0, "well": 0.7},
              near=(bell[0], bell[1] + 6.0, bell[2]), radius=20.0)


# ----------------------------------------------------------------------------------------------------
# 2. "we run home."
# ----------------------------------------------------------------------------------------------------

def shot_run(st, s, at):
    """The family sprints across the square for its door: farmer first, the child at his side, the librarian and the
    shepherd behind. The camera runs backwards ahead of them at ground level, a little slower than they are, so the
    farmer grows from a figure in the group to a face over the lens; behind them the well with the bell (still
    swinging), its two lamps and the dusk sky."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    base = v.paths["square_to_house_a"]
    pre = 6                                   # frames of run before the cut: everybody is at full speed in frame 1
    lead_at_cut = 1.56                        # blocks the farmer still is short of the path's first point at the cut
    lead = None
    st.walks = {}
    for name, prof, side, behind, kw in FAMILY:
        c = st.actor(name, prof, **kw)
        pts = _run_path(v, base, side, lead_at_cut + (pre + behind) * RUN)
        c.place(f0 - pre, pts[0], yaw_to(pts[0], pts[1]))
        c.walk(f0 - pre, pts, run=True)
        st.walks[name] = pts
        st.use(s, c)
        lead = lead or c
    cast = st.cast
    # panic is in the heads: the child looks up at the farmer as they go, the librarian throws a glance across at him
    # (26 degrees: at 52 his face went behind the farmer's shoulder and he was a red hat on a blank pink box)
    cast["kid"].look_at(f0 + 2, lead, ease=5)
    cast["kid"].look_at(at["home"] - 3, None, ease=5)
    cast["bo"].look_at(at["run"] - 5, _aside(cast["bo"], at["run"], 26.0), ease=5)
    cast["bo"].look_at(at["run"] + 9, None, ease=5)
    for f in (at["rings"] + 24, at["rings"] + 48):          # the bell is still being rung behind them
        ring(v, f)
    v.door_open("house_a", f1 - 1, open=True, frames=1)     # (behind the camera) open for the next shot
    a, b = lead.pos_at(f0), lead.pos_at(f1 + 1)             # the farmer when the shot starts and when it ends
    s.lens(24, 2.8)
    # (the aim sinks a little as they close in: the child's face stays clear of the caption band to the last frame)
    s.move((a.x + 4.3, a.y - 0.62, 0.30), (a.x - 2.7, a.y + 0.82, 1.30),
           (b.x + 2.05, b.y - 0.50, 0.36), (b.x - 2.64, b.y + 0.87, 1.25), ease="linear")
    s.focus(lead.head)
    s.handheld(0.02, seed=5)
    st.hero(s, "lead villager", lead)
    # the torches by the door they run for light their faces (x 3, not the look-dev's 4: with 4 the lit stone sat
    # exactly on the palette limit, G/R 0.920, and passed or failed with the sampling noise)
    st.lights(s, scale=1.4, groups={"house_a": 2.0}, near=A["square_center"], radius=24.0,
              extra=[((9.7, -7.5, 2.9), 3.0)])


# ----------------------------------------------------------------------------------------------------
# 3. "We count who made it."
# ----------------------------------------------------------------------------------------------------

def shot_interior(st, s, at):
    """Inside house_a, over the pillow of the one bed nobody came home to (the look-dev composition: empty bed in
    front, faces above it, the door in the far wall). The shepherd, last in the run, is two steps inside and the
    door swings shut behind him on the lamps of the square: the shot opens FOCUSED on the open doorway, the door
    shuts in focus once he is clear of it, and the focus comes forward to the faces as they turn from it, to each
    other ("count") and one after another to the empty bed ("who made it"), where the camera follows their eyes."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    bed = v.beds["house_a_bed_2"]                            # the north bed: foot toward the room, pillow at the east wall
    head, foot = bed["head"], bed["foot"]
    door = A["house_a_door"]
    st.see_through(s, "house_a_east")
    # (the shepherd here is a twin of the one in the run: the twin can be pre-rolled, so that on the first frame he
    # is leaning and mid-stride, not an upright figure sliding in at sprint speed)
    ada, bo, cy = st.actor("ada", "farmer"), st.actor("bo", "librarian"), st.actor("cy_in", "shepherd")
    kid = st.actor("kid", "farmer", child=True)
    pillow = (head[0] + 0.1, head[1], head[2] + 0.1)
    # (everybody ran in the previous shot, so nothing here may be keyed before f0: a pre-roll would cut that run short)
    spots = [(bo, (foot[0] - 1.25, foot[1] - 0.07, 1.0)), (ada, (foot[0] - 2.05, foot[1] - 0.92, 1.0)),
             (kid, (foot[0] - 1.50, foot[1] - 0.80, 1.0))]         # clear of the librarian's arm and leg: the face must read
    for i, (c, pos) in enumerate(spots):
        c.place(f0, pos, yaw_to(pos, pillow))
    # the shepherd, last in, is two steps inside the door as the shot starts (left of it from here, so that the
    # doorway and the door are in the clear) and runs on to join the others on the right
    way = [(12.3, -8.3, 1.0), (13.2, -8.95, 1.0), (15.3, -9.0, 1.0), (15.9, -8.80, 1.0)]
    stop = (16.3, -8.65, 1.0)                                # (0.3 further south clears the wall torch behind his hat but hides him behind the librarian)
    pre = 6                                                  # frames of run before the cut
    dx, dy = way[1][0] - way[0][0], way[1][1] - way[0][1]
    d = math.hypot(dx, dy)
    start = (way[0][0] - dx / d * pre * RUN, way[0][1] - dy / d * pre * RUN, way[0][2])
    cy.place(f0 - pre, start, yaw_to(start, way[0]))
    arrive = cy.walk(f0 - pre, [start] + way, run=True)
    arrive = cy.walk(arrive, [stop], speed=2.4, from_current=True)       # two short steps to a stop
    cy.face(arrive, pillow, ease=6)
    st.walks["cy_in"] = way + [stop]
    # ... and the door swings shut behind him: frames f0+5 .. f0+12, shut as "count" appears. (Not earlier: for the
    # first three frames after the cut he is in front of the opening; not later: he runs across it again from f0+17.)
    v.door_open("house_a", f0 + 5, open=False, frames=7)

    # "We": heads round toward the door (their left, the right of the frame), as far as a face still reads
    bo.look_at(f0, _aside(bo, f0, 50.0), ease=0)
    ada.look_at(f0, _aside(ada, f0, 42.0), ease=0)
    kid.look_at(f0, _aside(kid, f0, 30.0, dz=1.4), ease=0)   # the child: up at the librarian beside him
    for i, (c, pos) in enumerate(spots):
        c.shiver(f0, f1 + 1, seed=i)
    cy.shiver(arrive + 6, f1 + 1, seed=5)
    # "count": the door is shut, and the heads leave it for each other (long eases: a head that swings 98 degrees
    # in 6 frames is twice as fast as the game turns one, and a smear exactly while the word is read)
    n = at["count"] + 2
    bo.look_at(n, _aside(bo, n, -48.0, dz=-0.1), ease=10)    # toward the farmer beside him
    ada.look_at(n + 2, bo, ease=6)
    kid.look_at(n + 4, _aside(kid, n, -40.0, dz=0.9), ease=8)
    # "who": one after another, at the empty bed
    n = at["who"]
    ada.look_at(n + 1, pillow, ease=7)
    bo.look_at(n + 5, pillow, ease=8)
    kid.look_at(n + 8, pillow, ease=7)
    cy.look_at(max(arrive + 6, at["made"]), pillow, ease=6)
    # "it": nobody looks up again. (The child's look up at the librarian turned what shows of his face away.)

    st.use(s, ada, bo, cy, kid)
    # the look-dev frame while the door shuts; then the camera eases back and down with their eyes, onto the bed:
    # by "who made it" its pillow has come up into the picture, above the Reels description
    cam0 = (head[0] + 1.20, head[1] + 0.02, 2.42)
    cam1 = (head[0] + 1.32, head[1] + 0.00, 2.50)
    s.lens(26, 2.6)
    s.move(cam0, (foot[0] - 2.8, foot[1] + 0.04, 1.74), cam1, (foot[0] - 2.8, foot[1] + 0.04, 1.05))
    # the doorway is small in this frame and 8 blocks off: it is seen shutting only if it is what is sharp. The
    # focus starts on it and comes forward to the librarian over frames f0+9 .. f0+17, as the door meets its frame
    s.focus((door[0] + 0.3, door[1], door[2]))
    s.focus(bo.head, at_s=s.start_s + 9 / float(FPS), rack_s=8 / float(FPS))
    s.handheld(0.008, seed=7)
    st.hero(s, "librarian", bo)
    st.hero(s, "farmer", ada)
    # (the room as in the look-dev; the lamps of the square stay on too: they are what the doorway shows until it shuts)
    # (and the torch outside the door x 4, as bright as the run shot had it: the door shuts on warm light)
    st.lights(s, scale=1.2, groups={"house_a": 1.5, "bell_e": 2.5, "bell_w": 2.5}, near=door, radius=16.0,
              inside="house_a", extra=[((9.7, -7.5, 2.9), 4.0)])


# ----------------------------------------------------------------------------------------------------
# 4. "He rings it because he likes the sound."
# ----------------------------------------------------------------------------------------------------

def shot_steve(st, s, at):
    """The reveal: Steve alone at the bell in the empty square, every door shut, ringing it again and again. The
    look-dev picture (from the south-east, behind the arm that swings, the east lamp his key), on a slow push-in.
    He hits the bell on "rings", "because", "likes" and "sound" and once more in the hold after it: the arm is
    furthest forward two frames into its swing, which is the frame the bell starts from."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    steve = st.actor("steve", "steve")
    spot, bell = A["bell_ringer"], A["bell"]
    steve.place(f0, spot, v.yaws["bell_ringer"])
    steve.look_at(f0, bell, ease=0)
    steve.idle(f0, f1 + 1, seed=3)
    beat = 2 * CLOCK["word"]
    ring(v, at["rings2"] - beat)                            # it is still swinging from the last time as the shot opens
    for f in (at["rings2"], at["because"], at["likes"], at["sound"], at["sound"] + beat):
        steve.swing_arm(f - 2)
        ring(v, f)
    st.use(s, steve)
    s.lens(32, 3.2)
    s.move((2.98, -8.84, 1.32), (-2.05, -2.35, 1.20), (2.42, -8.14, 1.29), ease="ease_out")
    s.focus(steve.head)
    s.handheld(0.012, seed=37)
    st.hero(s, "steve", steve)
    st.hero(s, "bell", v.bell)
    st.lights(s, scale=1.3, groups={"bell_e": 2.6, "bell_w": 1.2}, near=A["square_center"], radius=20.0)


def build(scene):
    """Build "The Bell" into `scene`: {"film": Film, "captions": [(word, t0, t1), ...], "stage": Stage}."""
    caps, frame, lengths = timing()
    words = [w for w, _a, _b in caps]
    # frame on which a word appears; "rings" and "it" occur twice (the second ones are Steve's)
    at = {w: frame[words.index(w)] for w in ("rings", "we", "run", "home", "We", "count", "who", "made", "it", "He",
                                              "because", "likes", "sound")}
    at["rings2"] = frame[len(words) - 1 - words[::-1].index("rings")]

    v = village.build_village(scene, seed=1, bed_colors=BEDS)
    sky = look.set_time(scene, SKY["preset"], sun_azimuth=SKY["az"], sun_elevation=SKY["el"])
    look.setup_compositor(scene, bloom=SKY["bloom"], grade=SKY["grade"])
    film = shots.Film(scene, fps=FPS)
    st = Stage(scene, film, v, sky)
    builders = (("bell", shot_bell), ("run", shot_run), ("interior", shot_interior), ("steve", shot_steve))
    for (name, fn), n in zip(builders, lengths):
        fn(st, st.shot(name, n / float(FPS)), at)
    st.finish()
    return {"film": film, "captions": caps, "stage": st}
