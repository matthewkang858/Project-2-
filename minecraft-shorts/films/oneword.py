"""One Word: a 13 s vertical short in the trading hall, six shots, told by the librarian of cell 1.

    "He breaks my lectern. / I forget everything. / He puts it back. / I learn again. /
     He's looking for one word. / Mending."

The trade re-roll every player knows: break the librarian's lectern, he loses his job and his trades; put it back,
he is a librarian again with new trades; repeat until he offers the Mending book.

    shot      words                         picture
    mine      He breaks my lectern.         Steve mines the lectern by hand in front of the librarian: the arm swings,
                                            the cracks grow (stages 6..9), the block bursts 3 frames into "lectern"
    forget    I forget everything.          the librarian close; on "forget" hat and glasses are gone (no particles,
                                            as in the game); on "everything" he looks down at the empty place
    place     He puts it back.              Steve's use swing, the lectern is there again on "back"
    learn     I learn again.                close again: his eyes come up from the lectern, and on "learn" the five
                                            green sparkles and the librarian's outfit are there
    loop      He's looking for one word.    one locked framing over Steve's arm, jump cuts in time: break, plain,
                                            place, green, four times (20, 10, 10, 8 frames); then he stops clicking
    mending   Mending.                      stillness: he holds out the enchanted book, the glint moving over it

    $BPY -m render oneword --sheet 12 --threads 2
    $BPY -m render oneword --still 1.5 --res 720x1280 --samples 24 --zones --captioned --threads 2
    $BPY -m films.oneword plan                     # the caption clock: the frame every word and every event is on
    $BPY -m films.oneword check 1.5 3.0 ...        # tools.palette_check on out/test/oneword_<S>.png (no rendering)

The film is planned from the captions outward: CLOCK is the whole timing in frames, every word starts on a frame,
the five cuts are the first frames of the sentences, and every action a word names is keyed from that word's frame
(the dict `at`). Camera, lens, staging and lantern levels are the reviewed set-ups of engine/fx.py (cell 1 of the
hall: "Steve mining", "cell, lectern and floor", "the book") under the hall light of films/lookdev.py shot_hall.

Game truth kept here (engine/fx.py has the class names): a lectern takes 90 frames by hand and the film opens two
thirds of the way through; breaking it gives the burst of crumbs; the villager loses his job a moment later
without any particle; placing has no animation but the player's arm swing; taking the job gives 5 happy_villager
sparkles and the outfit on the same tick; a villager shows his trade item on his crossed arms.
Game truth left out: the lectern item that a broken lectern drops (and that Steve would hold to place it again).
"""
import math
import sys

from engine import captions, fx, look, shots, village
from films.lookdev import Stage, yaw_to

FPS = 24
TITLE = "One Word"
SCRIPT = ("He breaks my lectern. I forget everything. He puts it back. I learn again. "
          "He's looking for one word. Mending.")

# the caption clock, in frames (24 fps): the first word, every word, the extra hold after a sentence, and how long
# the last picture stays once the last word has gone. 2 + 20 x 10 + 6 x 14 + 26 = 312 frames = 13.0 s.
CLOCK = dict(start=2, word=10, period=14, tail=26)

SKY = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")     # the look-dev hall shot's sky
HALL = dict(scale=0.0, groups={"hall": 0.8}, inside="hall")                # ... and its lantern levels (never boosted)

HAND = 90            # fx.break_frames("lectern", "hand"): frames the game needs for a lectern with the bare hand
BREAK_LAG = 3        # the lectern bursts this many frames after the word "lectern" appears
# The loop of shot 5: (frames after "He's", break, plain villager, lectern placed, green + librarian) per cycle, every
# number counted from the cycle's first frame, which is a jump in time. The first cycle is slow enough to follow,
# the 2nd, 3rd and 4th start on "for", "one" and "word" and are shorter (20, 10, 10, 8 frames: every picture of a
# cycle stays up at least two frames, so each one still reads as break / forget / place / learn). After the
# fourth Steve stops clicking, and the shot lands on 16 quiet frames under the held "word" before "Mending".
LOOP = ((0, 3, 8, 13, 16), (20, 1, 3, 5, 7), (30, 1, 3, 5, 7), (40, 1, 2, 4, 6))
# fx.emit seeds for the five happy_villager sprites of each "takes the job": in a 1x1 cell about half of them start
# inside the walls, so each seed was chosen (by projecting the simulated sprites through the shot camera) to show
# four or five of them, around his head and not across his face
SPARKLE_SEEDS = dict(learn=143, loop=(1, 18, 36, 35))


def timing():
    """The captions and the frames they imply: (captions, at) with at[key] = the frame a word appears on (keys are
    the words in lower case without apostrophes, a repeated word numbered: he, breaks, my, lectern, i, forget,
    everything, he2, puts, it, back, i2, learn, again, hes, looking, for, one, word, mending), at['gone'] = the
    first frame without a caption and at['out'] = the first frame after the film."""
    c = CLOCK
    # (a quarter frame early: autotime rounds to 4 decimals, and a frame shows the word whose t0 <= its own time)
    caps = captions.autotime(SCRIPT, start=(c["start"] - 0.25) / FPS, per_word=c["word"] / FPS, comma=0.0,
                             period=c["period"] / FPS)
    at, seen = {}, {}
    for word, t0, _t1 in caps:
        key = "".join(ch for ch in word.lower() if ch.isalpha())
        seen[key] = seen.get(key, 0) + 1
        frame = int(round(t0 * FPS + 0.25)) + 1
        at[key if seen[key] == 1 else "%s%d" % (key, seen[key])] = frame
        # the rounding, checked: the word is on that frame and was not on the one before
        assert captions.caption_at(caps, (frame - 1) / FPS) == word, (word, frame)
        assert captions.caption_at(caps, (frame - 2) / FPS) != word, (word, frame)
    at["gone"] = int(round(caps[-1][2] * FPS + 0.25)) + 1
    assert captions.caption_at(caps, (at["gone"] - 1) / FPS) is None
    assert captions.caption_at(caps, (at["gone"] - 2) / FPS) == caps[-1][0]
    at["out"] = at["gone"] + c["tail"]
    return caps, at


CUTS = ("i", "he2", "i2", "hes", "mending")      # the first word of sentences 2..6: where the five cuts are


class Cell:
    """What the six shots share: cell 1 of the trading hall, its lectern as an fx.Block, the librarian (a villager
    who can lose and regain his profession), Steve, and the villagers of the next two cells."""

    def __init__(self, st):
        v = st.v
        self.st, self.v = st, v
        self.spot = v.anchors["cell_1"]                       # (-5.5, -31.3, 0): he stands against his lectern
        self.yaw = v.yaws["cell_1"]                           # facing north, into the aisle
        self.lec = fx.hall_job_block(v, 1)
        stamp_every_frame(self.lec.object)                    # (its material carries the keyed crack stage)
        self.lib = st.cast["lib"] = fx.make_job_villager("lib", ("librarian", "none"))
        self.steve = st.actor("steve", "steve")
        self.others = [st.actor("cell%d" % i, v.cell_professions[i - 1]) for i in (2, 3)]
        self.stand = self.p(0.72, 2.25, 0.0)                  # Steve in the aisle, east of the line lens - librarian
        self.top = (self.lec.center.x, self.lec.center.y, self.lec.top - 0.2)      # what Steve looks at and hits

    def p(self, dx, dy, z):
        """A point given as an offset from the cell_1 anchor (the way engine/fx.py records its set-ups)."""
        return (self.spot[0] + dx, self.spot[1] + dy, z)

    def neighbours(self, s):
        """The villagers of cells 2 and 3 in their places for shot s (they are seen, if at all, at a frame edge)."""
        A, v = self.v.anchors, self.v
        for i, c in zip((2, 3), self.others):
            c.place(s.frame_start, A["cell_%d" % i], v.yaws["cell_%d" % i])
            c.idle(s.frame_start, s.frame_end + 1, seed=30 + i)
        self.st.use(s, *self.others)

    def librarian(self, s, look, lowered=0.0, back=0.0, seed=6):
        """The librarian in his cell from the first frame of shot s, eyes on `look` (or `lowered` degrees below the
        horizontal in that direction). He breathes and shifts his weight (Character.idle), but his head is the
        film's to move: every turn of it is keyed by the shot."""
        lib, f0 = self.lib, s.frame_start
        lib.place(f0, (self.spot[0], self.spot[1] - back, self.spot[2]), self.yaw)
        if lowered:
            look = below(lib, f0, look, lowered)
        lib.look_at(f0, look, ease=0)                         # (one key per head and frame: see Character._cut)
        lib.idle(f0, s.frame_end + 1, seed=seed)
        lib.look_at(f0 + 1, look, ease=1)                     # (ends idle's random glances: they start later than this)
        self.st.use(s, lib)
        return lib

    def player(self, s, frame=None, look=None):
        """Steve at his place in the aisle from `frame` (default: the shot's first), eyes on `look` (default: the
        lectern's top, which is also what he hits)."""
        steve = self.steve
        f = s.frame_start if frame is None else frame
        steve.place(f, self.stand, yaw_to(self.stand, self.lec.center))
        steve.look_at(f, self.top if look is None else look, ease=0)
        self.st.use(s, steve)
        return steve


def below(c, frame, toward, degrees):
    """The point 2 blocks from character c's eyes in the direction of `toward`, `degrees` below the horizontal: a
    look_at target for lowered eyes. (Aiming at a thing at his feet would pitch the head to its 35-degree stop and
    show the lens his scalp.)"""
    e = c.eye_point(frame)
    dx, dy = toward[0] - e.x, toward[1] - e.y
    n = math.hypot(dx, dy) or 1.0
    return (e.x + 2.0 * dx / n, e.y + 2.0 * dy / n, e.z - 2.0 * math.tan(math.radians(degrees)))


def down(c, frame, toward, degrees, ease=8):
    """Lower character c's eyes over `ease` frames: toward the point `toward`, `degrees` below the horizontal."""
    return c.look_at(frame, below(c, frame + max(0, ease), toward, degrees), ease=ease)


def stamp_every_frame(*objects):
    """Work-around for engine/stamp.py, which is frozen: it caches the digest of a mesh, and that digest contains
    the digests of the mesh's materials. For a mesh whose material is animated (the lectern's crack stage, the
    book's glint) the fingerprint of every frame that shows it then depends on which frame the process happened to
    fingerprint first, so a rebuild after any edit of this file declares hundreds of good frames stale. A keyed
    custom property on the mesh makes the Fingerprinter treat it as animated and take its digest afresh at every
    frame (Fingerprinter.is_dynamic). It changes no pixel."""
    for ob in objects:
        ob.data["stamp_every_frame"] = 1.0
        ob.data.keyframe_insert('["stamp_every_frame"]', frame=1)


def smash(lec, cracked_from, frame, shot, seed):
    """The lectern at the last crack stage from `cracked_from`, broken ON `frame` in the game's burst of crumbs
    (cracked_from == frame: whole until it bursts). For the jump cuts of the loop, which join each break at its
    end: fx.break_block spreads stages 0..9 over its span, and hand mining shows stage 9 for its last 9 frames."""
    first = min(cracked_from, frame - 1)
    burst = fx.break_block(lec, first, frame, camera=shot, seed=seed)
    for f in range(first, frame):
        lec.crack(f, 9 if f >= cracked_from else -1)
    return burst


def clear_block(burst, block, frame, until, margin=0.10):
    """End the crumbs of `burst` that are inside or against `block` when it is put back on `frame`, and those that
    fall into it on the frames up to `until` (exclusive): they were simulated for the hole, so they would pass
    through the block that stands there again and stick out of it. The crumbs on the floor around it stay. Returns
    how many it ended."""
    x0, y0, z0 = block.cell

    def touches(p, f):
        loc = list(p["object"].location)
        for fc in shots.fcurves_of(p["object"]):
            if fc.data_path == "location":
                loc[fc.array_index] = fc.evaluate(f)
        x, y, z = loc[0] - x0, loc[1] - y0, loc[2] - z0
        return any(b[0] - margin < x < b[3] + margin and b[1] - margin < y < b[4] + margin
                   and b[2] - margin < z < b[5] + margin for b in block.shape)

    every, end, ended = burst.particles, burst.frame_end, 0
    for f in range(int(frame), int(until)):
        burst.particles = [p for p in every if p["first"] <= f < p["last"] and touches(p, f)]
        ended += burst.stop(f)                               # (Burst.stop ends what is in .particles)
    burst.particles, burst.frame_end = every, end
    return ended


# ----------------------------------------------------------------------------------------------------
# 1. "He breaks my lectern."
# ----------------------------------------------------------------------------------------------------

def shot_mine(st, s, at, cell):
    """Steve mining the lectern, seen past his right shoulder from the aisle (fx set-up "Steve mining"): Steve
    frame-left, the arm that swings toward the lectern, the librarian behind it watching the lens. The film opens
    60 % of the way through the 90 frames a lectern takes by hand, so the cracks are at stage 6 on frame 1 and grow
    through 7, 8 and 9; the block bursts 3 frames after "lectern" appears. Then the librarian looks down at the hole
    and Steve up at him."""
    lec = cell.lec
    hit = at["lectern"] + BREAK_LAG
    cam0, cam1 = cell.p(0.11, 3.95, 1.60), cell.p(-0.05, 3.93, 1.60)     # a slow slide west: Steve drifts off the cell
    lib = cell.librarian(s, cam0)
    steve = cell.player(s, hit - HAND)                       # (new to the film: he has been at it for 2.2 s)
    fx.mining_swings(steve, hit - HAND, hit)                 # after place() and look_at(): it reads his pose
    fx.break_block(lec, hit - HAND, hit, camera=s, hit_from=steve, seed=1)
    down(lib, hit + 3, lec.center, 14, ease=7)               # ... it is gone: his eyes go down to where it stood
    steve.look_at(hit + 10, lib, ease=7)                     # (the arm is at rest 9 frames after the break)
    cell.neighbours(s)
    s.lens(24, 3.4)
    s.move(cam0, cell.p(0.45, 0.80, 1.10), cam1, cell.p(0.40, 0.80, 1.10), ease="linear")
    s.focus(lec.object)
    s.handheld(0.006, seed=7)
    st.hero(s, "librarian", *lib.heads)
    st.hero(s, "steve", steve)
    st.lights(s, **HALL)


# ----------------------------------------------------------------------------------------------------
# 2. "I forget everything."
# ----------------------------------------------------------------------------------------------------

def shot_forget(st, s, at, cell):
    """The librarian, close, from where Steve stands (Steve is not in this picture: it is what he sees). His eyes
    come up from the hole to the lens; on "forget" the hat and the glasses are gone: a plain villager, no particles,
    as in the game. Under his folded arms is the empty place where the lectern stood, the last crumbs settling in
    it; on "everything" his eyes go down to it again, and in the pause they come back to the lens. The camera
    pushes in a quarter of a block."""
    f0 = s.frame_start
    cam0, cam1 = cell.p(0.78, 3.62, 1.56), cell.p(0.72, 3.40, 1.57)
    lib = cell.librarian(s, cell.lec.center, lowered=14)     # as shot 1 left him: eyes on the hole ...
    lib.look_at(f0 + 2, cam0, ease=7)                        # ... and now they come up to the lens
    lib.lose_profession(at["forget"])
    down(lib, at["everything"], cell.lec.center, 20, ease=9)
    lib.look_at(at["everything"] + 15, cam1, ease=8)
    s.lens(50, 3.4)
    s.move(cam0, cell.p(0.03, 0.30, 1.22), cam1)
    s.focus(lib.head)
    s.handheld(0.004, seed=5)
    st.hero(s, "librarian", *lib.heads)
    st.lights(s, **HALL)


# ----------------------------------------------------------------------------------------------------
# 3. "He puts it back."
# ----------------------------------------------------------------------------------------------------

def shot_place(st, s, at, cell):
    """The picture of shot 1 again, on a steady push (a third of a block: on 24 mm less than that reads as a locked
    frame, and it ends tighter on villager and lectern, toward the close-up that follows), the cell front empty and
    a plain villager behind it. Steve looks
    him over, looks down at the empty place, and on "back" the lectern is there: the game has no placing animation,
    only the arm's use swing, which is furthest forward two frames after it starts. The villager looks down at his
    job block, and Steve up at the villager."""
    f0 = s.frame_start
    lec = cell.lec
    put = at["back"]
    # From where shot 1 ended, a push of 0.35 toward the cell, a touch east and panning with it. (Pushing while
    # sliding on west, as the slow push did, takes Steve's head out of the safe area once he turns it to the
    # villager: 67 % inside on frames 146-154 against the 70 % of tools/palette_check; this way 75 % and more.)
    cam0, cam1 = cell.p(-0.05, 3.93, 1.60), cell.p(0.02, 3.59, 1.60)
    lib = cell.librarian(s, cam0)
    steve = cell.player(s, look=lib)                         # (the librarian is placed first: Steve looks at where he is)
    steve.idle(f0, put - 4, seed=2)                          # (breathing; over before the swing reads his pose)
    steve.look_at(at["puts"] - 4, cell.top, ease=8)
    fx.arm_swings(steve, [put - 2])
    fx.place_block(lec, put)
    down(lib, put + 3, lec.center, 16, ease=7)               # the villager finds his job block ...
    steve.look_at(put + 9, lib, ease=8)                      # ... and Steve watches him (the swing is over by then)
    cell.neighbours(s)
    s.lens(24, 3.4)
    s.move(cam0, cell.p(0.40, 0.80, 1.10), cam1, cell.p(0.45, 0.80, 1.10), ease="linear")
    s.focus(lec.object)
    s.handheld(0.006, seed=11)
    st.hero(s, "librarian", *lib.heads)
    st.hero(s, "steve", steve)
    st.lights(s, **HALL)


# ----------------------------------------------------------------------------------------------------
# 4. "I learn again."
# ----------------------------------------------------------------------------------------------------

def shot_learn(st, s, at, cell):
    """The close picture of shot 2, a little wider, with the lectern back under his arms. He is still looking down at
    it; during "I" his eyes come up to the lens (under the hat a lowered face is half hidden, so he is level when it
    comes), and on "learn" the five green sparkles of the game appear around him and he wears the librarian's hat
    and glasses again, on the same frame. He goes on looking at us while the sparkles go out one by one."""
    cam0, cam1 = cell.p(0.74, 3.62, 1.56), cell.p(0.70, 3.40, 1.57)
    lib = cell.librarian(s, cell.lec.center, lowered=16)
    lib.look_at(at["learn"] - 7, cam1, ease=7)               # his eyes come up from the lectern and meet the lens ...
    lib.gain_profession(at["learn"], "librarian", camera=s, seed=SPARKLE_SEEDS["learn"])     # ... as he takes the job
    s.lens(40, 3.4)
    s.move(cam0, cell.p(0.03, 0.40, 1.15), cam1)
    s.focus(lib.head)
    s.handheld(0.004, seed=13)
    st.hero(s, "librarian", *lib.heads)
    st.lights(s, **HALL)


# ----------------------------------------------------------------------------------------------------
# 5. "He's looking for one word."
# ----------------------------------------------------------------------------------------------------

def shot_loop(st, s, at, cell):
    """The loop, on ONE locked framing: over Steve's arm, the lectern and the librarian's face. Four times the
    lectern bursts, the hat is gone, the lectern is back, green sparkles and the hat again; every cycle starts with
    a jump in time (the particles of the cycle before are stopped there) and they get shorter: 20, 10, 10, 8
    frames, the 2nd, 3rd and 4th starting on "for", "one" and "word". The first cycle plays in one piece; from the
    second on each is two pictures, "gone" (crumbs, no hat) and "back" (lectern, sparkles, hat), with a second jump
    between them, and Steve's arm does not stop. After the fourth placing it does: the arm comes to rest, he looks
    up at the librarian, and the last sparkles drift over 16 quiet frames. He has stopped clicking, and the cut
    says why."""
    f0, f1 = s.frame_start, s.frame_end
    lec = cell.lec
    cam = cell.p(0.05, 3.95, 1.60)
    lib = cell.librarian(s, cam)
    steve = cell.player(s, f0 - 14)                          # (he is not in shot 4: the pre-roll is hidden)
    first = LOOP[0]
    fx.mining_swings(steve, f0 - 14, f0 + first[1] - 2)      # cycle 1: he is mining as the shot opens ...
    fx.arm_swings(steve, [f0 + first[3] - 2])                # ... one use swing puts it back ...
    last = f0 + LOOP[-1][0] + LOOP[-1][3]                    # the frame the lectern is put back for the last time
    fx.mining_swings(steve, f0 + LOOP[1][0] - 3, last - 2)   # ... and from then on he clicks without a pause ...
    steve.look_at(last + 8, lib, ease=7)                     # ... until that placing (the arm is at rest 9 frames
                                                             # after the span): then he looks at what he has got
    for n, (start, brk, plain, put, green) in enumerate(LOOP):
        j = f0 + start
        fx.stop_particles(j)                                 # a jump in time: nothing of the cycle before hangs on
        crumbs = smash(lec, j, j + brk, s, seed=10 + n)
        lib.lose_profession(j + plain)
        fx.place_block(lec, j + put)
        if n:                                                # the fast cycles jump again here: "gone" / "back", and
            crumbs.stop(j + put)                             # no crumbs fly across the lectern that is back
        else:                                                # the first plays in one piece: the crumbs on the floor
            nxt = f0 + LOOP[1][0] if len(LOOP) > 1 else f1 + 1   # go on settling, those in the lectern's place end
            clear_block(crumbs, lec, j + put, nxt)
        lib.gain_profession(j + green, "librarian", camera=s, seed=SPARKLE_SEEDS["loop"][n])
    cell.neighbours(s)
    s.lens(35, 3.4)
    s.move(cam, cell.p(0.15, 0.80, 1.10))
    s.focus(lec.object)
    s.handheld(0.002, seed=17)
    st.hero(s, "librarian", *lib.heads)
    st.lights(s, **HALL)


# ----------------------------------------------------------------------------------------------------
# 6. "Mending."
# ----------------------------------------------------------------------------------------------------

def shot_mending(st, s, at, cell):
    """Stillness. The librarian, a hand's width back from his lectern (so the book clears its high edge), holds out
    the enchanted book on his crossed arms and looks at the lens (fx set-up "the book"). Nothing moves but the
    enchantment glint over the book, his breathing and a slow push-in; the picture holds a second after the word."""
    f0, f1 = s.frame_start, s.frame_end
    back = 0.22
    cam0, cam1 = cell.p(0.45, 3.20, 1.95), cell.p(0.42, 3.03, 1.95)
    fx.stop_particles(f0)                                    # later in the story: no sparkles left over
    # The lone iron-bars post two cells above the lectern ends at z 2.0, the height of his hat: from this camera
    # (1.95) it stands on the hat like an antenna, wherever the lens goes sideways. Taken out for this shot only.
    lec = cell.lec.cell
    fx.extract_block(st.v, (lec[0], lec[1], lec[2] + 2)).show(f0, False)
    lib = cell.librarian(s, cam0, back=back, seed=9)
    book = fx.hold_out(lib, "enchanted_book", f0, f1 + 1, enchanted=True)
    stamp_every_frame(book)                                  # (its material carries the scrolling glint)
    s.lens(45, 3.4)
    s.move(cam0, cell.p(0.0, 0.18, 1.16), cam1)
    s.focus(book)
    s.handheld(0.003, seed=6)
    st.hero(s, "book", book)
    st.hero(s, "librarian", *lib.heads)
    st.lights(s, **HALL)


SHOTS = (("mine", shot_mine), ("forget", shot_forget), ("place", shot_place), ("learn", shot_learn),
         ("loop", shot_loop), ("mending", shot_mending))


def build(scene):
    """Build "One Word" into `scene`: {"film": Film, "captions": [(word, t0, t1), ...], "stage": Stage}."""
    caps, at = timing()
    edges = [1] + [at[k] for k in CUTS] + [at["out"]]
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, SKY["preset"], sun_azimuth=SKY["az"], sun_elevation=SKY["el"])
    look.setup_compositor(scene, bloom=SKY["bloom"], grade=SKY["grade"])
    film = shots.Film(scene, fps=FPS)
    st = Stage(scene, film, v, sky)
    cell = Cell(st)
    for (name, fn), a, b in zip(SHOTS, edges, edges[1:]):
        s = st.shot(name, (b - a) / float(FPS))
        assert s.frame_start == a and s.frame_end == b - 1, (name, s.frame_start, s.frame_end, a, b)
        fn(st, s, at, cell)
    st.finish()
    return {"film": film, "captions": caps, "stage": st, "title": TITLE, "cell": cell, "at": at}


def plan():
    """Print the caption clock: every word with its frame, the cuts and the events of the loop (no Blender scene)."""
    caps, at = timing()
    edges = [1] + [at[k] for k in CUTS] + [at["out"]]
    keys = [k for k in at if k not in ("gone", "out")]
    print("%s: %d frames = %.3f s; last word gone on frame %d, %d frames (%.2f s) of hold after it"
          % (TITLE, at["out"] - 1, (at["out"] - 1) / FPS, at["gone"], CLOCK["tail"], CLOCK["tail"] / FPS))
    for (name, _fn), a, b in zip(SHOTS, edges, edges[1:]):
        words = ["%s %d" % (w, at[k]) for k, (w, _a, _b) in zip(keys, caps) if a <= at[k] < b]
        print("  %-8s frames %3d-%3d (%4.2f s)  %s" % (name, a, b - 1, (b - a) / FPS, ", ".join(words)))
    print("  break on frame %d (mining since frame %d)" % (at["lectern"] + BREAK_LAG, at["lectern"] + BREAK_LAG - HAND))
    for n, (start, brk, plain, put, green) in enumerate(LOOP):
        j = at["hes"] + start
        nxt = at["hes"] + LOOP[n + 1][0] if n + 1 < len(LOOP) else at["mending"]
        print("  loop %d: jump %d (%2d frames)  break %d  plain %d  placed %d  green %d"
              % (n + 1, j, nxt - j, j + brk, j + plain, j + put, j + green))
    last = at["hes"] + LOOP[-1][0] + LOOP[-1][3]
    print("  after the placing on frame %d Steve stops: last swing requested by frame %d, he looks up from frame %d, "
          "cut on frame %d" % (last, last - 2, last + 8, at["mending"]))
    return 0


def check(seconds):
    """tools.palette_check on stills that are on disk: out/test/oneword_<S>.png as `render oneword --still S` wrote
    them (any resolution). The film is built, the scene is put on each still's frame and probed, and the picture is
    compared with the game texels under every pixel and with the safe area of a Reel. Returns the number of stills
    with a failed check."""
    import os

    import render as R
    from tools import palette_check

    ses = R.Session("oneword")
    stage = ses.result["stage"]
    failed = 0
    for sec in seconds:
        path = os.path.join(R.ROOT, "out", "test", "oneword_%s.png" % sec)
        if not os.path.exists(path):
            print("[check] %s: no such still (%s)" % (sec, path))
            failed += 1
            continue
        frame = min(ses.film.frame_end, max(ses.film.frame_start, ses.film.frame(float(sec))))
        shot = ses.film.shot_at(frame)
        ses.film.goto(frame)
        rep = palette_check.evaluate(palette_check.probe(ses.scene), path, heroes=stage.heroes.get(shot.name, ()))
        label = "%s@%d" % (shot.name, frame)
        if palette_check.print_report(label, rep):
            failed += 1
        if not rep["checks"]:
            print("[check] %-10s (nothing to measure)" % label)
    print("[check] %d of %d stills failed a check" % (failed, len(seconds)))
    return failed


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        sys.exit(1 if check(sys.argv[2:]) else 0)
    sys.exit(plan())
