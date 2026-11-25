"""The Hello: everything the film (films/hello.py) and its five sequence files share.

    films/hello.py             the narration, the skies, the shot plan, build()          (lead director)
    films/hello_common.py      THIS FILE: the set, the places, the cameras, the cast, the helpers
    films/hello_square.py      beats 1, 9, 10, 11     village square, golden hour        (one director per file)
    films/hello_door_night.py  beats 2, 18, 19        the child's door at night, the zombie
    films/hello_interior.py    beats 3, 16, 17        inside the child's house (night; beat 3 ends in gold)
    films/hello_door_gold.py   beats 4, 5, 15, 20-22  the child's door in golden light
    films/hello_meadow.py      beats 6-8, 12-14       exit gate, meadow road, forest wall, the three signs

    $BPY -m tools.hello_timeline              the shot plan: frames, words, skies (no scene is built)
    $BPY -m tools.hello_shots render ...      stills of single shots (see its docstring): the scouting tool
    $BPY -m render hello --still S [--zones]  one frame through render.py (each sky is one build)

A sequence file exposes ONE FUNCTION PER SHOT, named like the shot:  def dn02_fight(st, s, C, nar)
    st   films.lookdev.Stage (st.use / st.hero / st.lights / st.see_through / st.remove / st.key; st.v = the Village)
    s    the engine.shots.Shot (s.frame_start .. s.frame_end inclusive; s.lens / move / follow / focus / handheld)
    C    the Hello object below: set, places, cameras, cast, helpers; C.T[shot name] = the shot's row of the plan
         (frames, words with their frames, sky, neighbours)
    nar  the engine.narration.Narration (nar.at("word", sentence="b04") = the frame the word's caption appears on;
         C.at(s, "word") = the same within shot s)
build() in films/hello.py calls these functions IN TIMELINE ORDER, each exactly once, after every shot exists.

THE SEQUENCE CONTRACT (what a sequence director may and must do)
  MAY   edit his own file only: the bodies of its shot functions, its docstrings, private helpers and constants.
        Make further twins of the shared cast with his own tags (C.actor("child", "dg2")). Add a film-local light
        with C.fill(...) (hidden outside the shots he names). Move a camera of his own shots freely, unless the
        row below names a SHARED camera or place for it.
  MUST  keep every shot function's name and signature;
        give every shot a camera (s.lens + s.move or s.follow, s.focus, s.handheld: nothing is ever dead still;
        something already moving on its first frame), its cast (st.use: everybody else is hidden), what it is
        about (st.hero, inside x 8-82 %, y 14-60 % of the frame, clear of the caption band y 62-72 %) and its torch
        levels (C.lights once per shot; beat 3 a second time with at=);
        take characters only through C.actor(role, tag) with a tag that starts with HIS prefix (sq, dn, in, dg,
        me), and items through C.item(item_id, tag): no other sequence can then disturb his keys;
        key each character in frame order; place() everybody on the first frame of a shot before any look_at();
        key nobody before a shot starts unless that instance is NOT in the shot before (pre-roll: use a twin);
        use the shared places and cameras where the plan names them (SHARED below), unchanged;
        keep the watcher's face unreadable before dg22 (from behind, cropped above the mouth, or out of focus with
        the face under about ten pixels at 540x960) and keep his body dead still (C.actor("watcher", ...) is built
        still: place() him once per shot and turn nothing but, at most, his head);
        render what he changed (tools/hello_shots.py at 540x960, 16 samples) and LOOK at it.
  MUST NOT  touch films/hello.py, this file, another sequence file or anything in engine/, render.py, tools/
        (his own new tools/hello_<seq>_*.py excepted); change the narration, the cuts, a sky or the film's length;
        make anything depend on which sky is being built (no `if sky ...`: every build keys the same things);
        call st.shot / st.sky_change / st.dip / st.finish (the film does); key hide_render on a character, its
        armor or its items (st.use does it); boost torches beyond LIGHTS without tools/palette_check; build a
        character with st.actor / players.make_player directly (it would escape the twin rule).
  If a shared place or camera is wrong for his shot, he says so in his result; he does not move it.

SHARED (decided once, used by two shots or two sequences)
  CAMS["door_front"]  beats 2 and 18, exactly (zombie at the door, night)            door_night
  CAMS["beside"]      beat 19: their two backs from the north-west, drifting left     door_night
  CAMS["two_shot"]    beats 4 and 22, exactly, with C.doorstep_fill(s) in both       door_gold
  CAMS["bed"]         beats 3 and 16, exactly (both beds, the north window)          interior
  CAMS["gate"]        beats 6 and 7, exactly (hello_set's gate camera, 22 mm)        meadow
  PLACES["watch_door"] + WATCH_YAW: where the watcher stands by the door and which way he faces (the door): beats
                      19, 20, 21, 22; Steve stands exactly there, facing the same way, in beat 4 (so beat 22 can
                      repeat beat 4's picture). Beat 15c (the third jump: the corner of the child's own house)
                      uses the PLACE but he faces the house fronts there (in profile to its camera: no face)
  PLACES["hello_child"]  the child at his feet: beats 4, 5 (start), 20 (end), 21, 22
  PLACES["step"]      the zombie's place on the step (breaking.stand_point): beats 2, 18, 19; the rotten flesh
                      lies there in beat 20
  RED_BED / CHILD_BED the beds of Steve and the child: beats 3 and 16 (the red one is Steve's, in front)

Coordinates: Blender blocks, +X east, +Y north, +Z up; ground 0.0, dirt path -1/16, house_a's floor +1.0.
house_a (the child's house; plains_medium_house_1), checked block by block with tools/hello_probe.py layers:
  an L: the west wing x 10..15, y -14..-6 (the door's side), the east wing x 15..20, y -14..-8 (the beds).
  WEST FRONT (x = 10, facing the plaza): oak door in cell (10, -8) (spans y -8..-7, centre y -7.5); one oak
  stairs step at (9, -8, 0): its high half (x 9.5..10) is at floor height z 1.0, its low half (x 9..9.5) at
  z 0.5; wall torches at (9, -7, 2) and (9, -9, 2) (flames (9.71, -6.5, 2.89) and (9.71, -8.5, 2.89): head
  height of a zombie on the step, one block either side of the door); north of the door ONE block of wall
  (y -7) and the corner log (y -6): the house's north-west corner is at (10, -5); south of the door the wall
  runs to y -14 with the ONE glass pane of this front at (10, -11, 2).
  INSIDE: the table (fence + pressure plate) at (11, -11) under the pane, oak-stairs chairs at (11, -10) (faces
  north, seat z 1.5) and (11, -12); the beds along the east wall, pillows east: house_a_bed_2 at y -10 (the north
  one), house_a_bed_1 at y -12 (the south one), each cells x 18..19; night stands (fence + plate) at (19, -9) and
  (19, -13); a wall torch between the pillows at (19, -11, 2); two-pane windows in the north wall of the bed wing
  (17..18, -8, 2: right behind the north bed), in its south wall (17..18, -14, 2) and in the west wing's south
  wall (12..13, -14, 2) and north wall (12..13, -6, 2); a gable pane at (20, -11, 4).
  Cutaways (Village.cutaways, Stage.see_through / remove): house_a_east (east end), house_a_south (south wall
  above its lowest row), house_a_roof.
"""
import math

from mathutils import Vector

from engine import breaking, characters, fx, mobs, players, props, sets, undead, village
from films import lookdev as L

FPS = 24
PATH_Z = -0.0625                       # a dirt path lies one pixel below the grass
FINAL_RES, FINAL_SAMPLES = (540, 960), 16      # this film's final quality (set on the scene by films/hello.py)

SEQUENCES = {"sq": "square", "dn": "door_night", "in": "interior", "dg": "door_gold", "me": "meadow"}

# ----------------------------------------------------------------------------------------------------------------
# the set
# ----------------------------------------------------------------------------------------------------------------
# Beats 3 and 16 look NORTH across both beds from outside the south wall (house_a_south is see-through for the
# camera): the south bed is in front, the north bed beyond it, the north window right behind it. So Steve's red bed
# is the SOUTH one (house_a_bed_1) and the child sleeps in the north one (house_a_bed_2).
RED_BED, CHILD_BED = "house_a_bed_1", "house_a_bed_2"
BED_COLORS = {RED_BED: "red"}


def _edit(b):
    """The village's edit hook: everything the story adds to the set (engine/sets.py hello_set, as it is)."""
    sets.hello_set(b)


def build_set(scene):
    """The village of "The Hello": seed 1, Steve's bed red, the meadow of engine.sets.hello_set. Returns the Village."""
    return village.build_village(scene, seed=1, bed_colors=BED_COLORS, edit=_edit)


# ----------------------------------------------------------------------------------------------------------------
# places: (x, y) = on the ground there (C.P gives the standing height, a pixel lower on a dirt path),
#         (x, y, z) = exactly there
# ----------------------------------------------------------------------------------------------------------------
PLACES = {
    # ---- the child's door (house_a, west front)
    "door": (10.0, -7.5, 2.0),            # middle of the door's outer face (focus / look target)
    "door_in": (11.9, -7.5, 1.0),         # just inside the door, on the floor (the child starts beat 20 here)
    "step": (9.7, -7.5, 1.0),             # on the step's high half, against the door: the zombie's place
    #                                       (breaking.stand_point(house_a)); the rotten flesh lies here in beat 20
    "step_child": (9.72, -7.28, 1.0),     # the child on the step's high half (beat 15); its low half is z 0.5
    "step_foot": (8.55, -7.5),            # on the path at the foot of the step
    "fight_from": (8.9, -10.6),           # beat 2: Steve comes in from here (frame right) ...
    "fight_to": (9.05, -8.35),            # ... and ends here, planted in front of the door
    "watch_door": (8.9, -5.4),            # THE WATCHER'S PLACE BY THE DOOR, facing WATCH_YAW: two blocks along the
    #                                       wall north of the step (2.2 from the zombie's place), 1.1 out from the
    #                                       wall, at the corner of the child's own house. Beats 15c, 19, 20, 21, 22;
    #                                       Steve stands exactly here, facing the same way, in beat 4. Chosen on
    #                                       stills: from (8.45, -5.35) a lamp post stood behind his head in beat 4.
    "watch_face": (9.75, -7.2, 1.6),      # the point he faces from watch_door: THE DOOR (65 degrees south of east).
    #                                       The two-shot camera is then 27 degrees off his nose (his face, his sword
    #                                       arm clear of it), CAMS "beside" (beat 19) 15-40 degrees off his back.
    "hello_child": (9.25, -6.41),         # the child at his feet for the hello (beats 4, 5, 20 end, 21, 22): a
    #                                       block in front of him toward the door, right of the two-shot's line
    "run_off": (4.6, -3.2),               # beat 5: the child runs off along the plaza toward here
    # ---- "one house closer" (beat 15): the three places, far to near, seen north along the house fronts
    "watch_far": (8.3, 14.6),             # beyond the next house (house_b), at the corner of house_f
    "watch_mid": (8.4, 5.2),              # at the next house: in front of house_b
    #   (the third is "watch_door")
    # ---- the plaza seen through the west window (beat 17)
    "watch_plaza": (3.4, -6.7),           # on the plaza north of the door, 7 blocks out, facing the house: on the
    #                                       line from CAMS "window" through the pane
    "window": (10.5, -10.5, 2.5),         # middle of the one glass pane of the west wall
    "window_chair": (11.5, -9.5, 1.5),    # the seat of the oak-stairs chair north of the table: the child stands here
    # ---- the square (beats 1, 9, 10, 11)
    "guard": (-1.2, -6.3),                # beat 1: Steve on guard south of the bell, looking down the south street
    "guard_child": (-0.45, -6.0),         # ... the child at his leg
    "watch_square": (0.5, 9.6),           # beats 9, 10, 11: the watcher at the mouth of the exit road, facing south
    "grownups": ((4.0, 3.0), (5.3, 3.8)),     # beat 10: the farmer and the toolsmith, facing each other, north-east
    #                                       of the well (which fills x -2..2, y -2..2 with its roof posts)
    "grownups_child": (5.4, 1.6),         # ... the child in front of them, left of the line to the gap
    "stare_child": (0.5, 6.4),            # beat 11: the child alone in the middle of the path, staring up at him
    # ---- the meadow (beats 6, 7, 8, 12, 13, 14): hello_set's anchors are in C.A (forest_gap, floating_oak_under,
    #      bare_oaks_among, pyramid_beside, ...); these are the film's own
    "gate_child": (0.15, 26.6),           # beats 6, 7: the child on the last full path block (sets proof still)
    "road_stop": (0.5, 54.6),             # beat 8: the child stops here, three blocks short of him at forest_gap
}
WATCH_YAW = L.yaw_to(PLACES["watch_door"], PLACES["watch_face"])     # his body's yaw at watch_door

# ----------------------------------------------------------------------------------------------------------------
# cameras: name -> dict(pos, target, lens, fstop[, pos1, target1]); C.cam(s, name) puts one on a shot
# ----------------------------------------------------------------------------------------------------------------
CAMS = {
    # beats 2 and 18 (EXACTLY the same): low from the plaza, the door with about a block of wall either side, seen
    # 27 degrees off its axis from the side of its free edge, so that the cracks and the shudder show past the
    # zombie (engine.breaking DOOR_CAM["side"], its proof stills breaking_zombie_film_s*.png). Frame left = north.
    "door_front": dict(pos=(4.4, -10.4, 0.75), target=(10.0, -7.6, 1.5), lens=47.0, fstop=4.0),
    # beat 19 (the story's fallback, after the cut from beat 18: "a wider shot ... with both of them from behind"):
    # from the north-west of the plaza, the zombie centred at the door and him just outside the left edge; the
    # camera drifts a block and a half to the left and he comes into the frame: their two backs, the torches on
    # the wall in front of them (him 15 degrees off his back at the end, the zombie 56)
    "beside": dict(pos=(5.3, -3.5, 1.15), target=(9.7, -7.5, 1.4), lens=47.0, fstop=3.2,
                   pos1=(6.31, -2.39, 1.15), target1=(9.3, -6.45, 1.4)),
    # beats 4 and 22 (EXACTLY the same, nothing moves but the handheld): beside the doorstep (the door behind the
    # lens's right shoulder), at the child's height, 3 blocks south of him looking north up at his face; the child
    # soft in the lower right foreground, the house front at the right edge. Chosen so that no lamp post stands
    # within a third of the frame of his head (the posts at (7, -3) and (6, 9) are on every line from the door).
    # (projected: his eyes standing y 37 %, crouched y 51 %, x 50 %; the child's head x 63-100 %, y 58-80 %)
    "two_shot": dict(pos=(8.8, -8.4, 1.35), target=(8.9, -5.4, 1.2), lens=40.0, fstop=2.4),
    # beat 15: locked frame from the step's south end, looking north along the house fronts over the child
    "house_fronts": dict(pos=(9.25, -9.9, 1.25), target=(8.6, 3.0, 1.6), lens=50.0, fstop=2.4),
    # beats 3 and 16: from just outside the south wall of the bed wing (house_a_south see-through), across both
    # beds: Steve's red bed in front, the child's bed beyond, the north window right behind it
    "bed": dict(pos=(18.15, -14.75, 2.55), target=(18.75, -9.0, 1.85), lens=24.0, fstop=3.2),
    # beat 17: inside, from the room's south-east, at the west window: the child's profile on the chair (right),
    # the pane beyond it (left), the plaza outside through the glass; a slow push toward the window
    "window": dict(pos=(15.0, -12.9, 2.3), target=(12.17, -10.84, 2.25), lens=40.0, fstop=2.8,
                   pos1=(14.6, -12.6, 2.3), target1=(12.17, -10.84, 2.25)),
    # beats 6 and 7 (the same frame): hello_set's gate camera, 22 mm (the figure at the gap is 30 px at 540x960)
    "gate": dict(pos=(0.9, 22.6, 0.75), target=(0.5, 57.6, 2.5975), lens=22.0, fstop=4.0),
    # beat 1: Steve and the child at the bell from the south-east, child height, a slow push in
    "guard": dict(pos=(1.75, -9.1, 0.8), target=(-1.0, -6.2, 1.25), lens=40.0, fstop=2.6,
                  pos1=(1.5, -8.85, 0.82), target1=(-1.0, -6.2, 1.28)),
    # beat 9: long lens from the south-east corner of the square up to the mouth of the exit road, east of the
    # well (a line from the south side of the square straight up the road goes through it)
    "square_long": dict(pos=(5.5, -8.5, 1.35), target=(0.5, 9.6, 1.5), lens=85.0, fstop=2.0),
    # beat 10: low, north-east of the well, on the line from watch_square through the gap between the adults
    "grownups": dict(pos=(6.6, 0.5, 0.6), target=(4.65, 3.4, 1.45), lens=32.0, fstop=2.6,
                     pos1=(6.5, 0.62, 0.62), target1=(4.65, 3.4, 1.45)),
    # beat 11: 2 blocks behind him and just west of his right hip (his right is west): the line to the child passes
    # 0.17 block beside his body, so his hip and hand fill the left quarter of the frame, soft
    "hip": dict(pos=(-0.3, 11.6, 1.0), target=(0.55, 6.4, 0.8), lens=66.0, fstop=2.6,
                pos1=(-0.27, 11.3, 1.0), target1=(0.55, 6.4, 0.82)),
}

# torch levels (C.lights(s, key)); every one looked at on stills. Near the palette limit: do not raise them without
# tools/palette_check (CONTRACT.md: lit cobblestone next to a torch is at the G/R limit).
LIGHTS = {
    "gold": dict(scale=1.0),                                   # daylight: torches at their own level
    "night_door": dict(scale=1.3, door=2.0),                   # look-dev night level; BOTH door torches x 2: the key
    "night_room": dict(scale=1.2, groups={"house_a": 1.3}, inside="house_a"),   # the room at night: its torches
    #                                                            and its fill together (never one alone)
    "gold_room": dict(scale=1.0, groups={"house_a": 0.7}, inside="house_a"),    # the same room once the night ended
}

EYE_GLOW = 1.5                         # emission of the white eyes in beat 22 (players.HEROBRINE_GLOW is 3.0, made
#                                        for dusk and night; in golden light 1.5 is "faintly glowing")

# role -> how Hello.actor builds it
ROLES = ("child", "kid", "farmer", "librarian", "toolsmith", "steve_iron", "steve_bed", "steve_diamond", "watcher",
         "watcher_eyes", "zombie")


def yaw_to(src, dst):
    """Yaw that makes a character at src (facing -Y at yaw 0) face dst."""
    return L.yaw_to(src, dst)


class ShotInfo:
    """One row of the film's shot plan with its frames: C.T[shot name].

    name, beat, sequence, sky, sentence (the engine.narration Sentence spoken in the shot), frame_start,
    frame_end (inclusive), frames, seconds, words = [(caption, frame it appears on)], change = the frame on which
    the sky changes inside the shot (beat 3) or None, sky_after = the sky from that frame on, dip = True when the
    encoder dips to black on the shot's first frame, prev / next = the neighbouring shots' names (or None)."""

    def __init__(self, **kw):
        self.change, self.sky_after, self.dip, self.prev, self.next = None, None, False, None, None
        self.__dict__.update(kw)

    def at(self, word, n=0):
        """Frame on which the n-th `word` spoken in this shot appears (case-insensitive caption text)."""
        hits = [f for w, f in self.words if w.lower().strip(".,") == word.lower()]
        return hits[n]

    def __repr__(self):
        return "<%s beat %d %s %s %d-%d>" % (self.name, self.beat, self.sequence, self.sky, self.frame_start,
                                            self.frame_end)


class Hello:
    """The film's shared context, handed to every shot function as C.

    C.st / C.v / C.A      the Stage, the Village, its anchors (C.A["exit_gate"], C.A["forest_gap"], ...)
    C.set                 v.sets["hello"]: forest, floating, bare, pyramid, cameras, path (engine/sets.py)
    C.nar, C.T            the Narration; the shot plan: C.T["dn02_fight"] -> ShotInfo
    C.P(name)             a place of PLACES as a 3D point (on the ground for 2D entries)
    C.cam(s, name, ...)   one of CAMS (or of hello_set's cameras, "set:floating") on a shot
    C.actor(role, tag)    a cast member, built once per tag: roles in ROLES, tag starts with the sequence prefix
    C.item(id, tag)       a dropped item (rotten flesh), registered like a cast member
    C.watcher(s, tag, frame=None, place="watch_door", yaw=WATCH_YAW)   the plain watcher put on his place, still
    C.door, C.door_torches    house_a's door prop and its two torch lights (split by breaking.door_torches)
    C.shots, C.memo       every Shot of the film by name; a dict for handing things from one shot function to a
                          later one of the SAME sequence (key prefixed with it: C.memo["dn_bang"])
    """

    def __init__(self, st, nar=None, timeline=None):
        self.st, self.v, self.A = st, st.v, st.v.anchors
        self.set = st.v.sets["hello"]
        self.nar = nar
        self.T = dict(timeline or {})
        self.door = self.v.doors["house_a"]
        # one light per wall torch instead of the village's merged one (inside the head of whoever stands on the
        # step): once, before any Stage.lights call
        self.door_torches = breaking.door_torches(self.v, "house_a")
        self.shots = {}            # shot name -> engine.shots.Shot (filled by films/hello.py before any shot function)
        self.memo = {}             # what one shot function leaves for a later one of ITS OWN sequence
        self._fills = {}

    # ------------------------------------------------------------------ places and cameras
    def stand(self, p):
        """(x, y) -> the point a character stands on there: ground height, a pixel lower on a dirt path. A 3D
        point is returned as it is."""
        if len(p) == 3:
            return (float(p[0]), float(p[1]), float(p[2]))
        x, y = float(p[0]), float(p[1])
        z = self.v.ground(x, y)
        top = self.v.world.block_id(int(math.floor(x)), int(math.floor(y)), int(round(z)) - 1)
        return (x, y, z + (PATH_Z if top == "dirt_path" else 0.0))

    def P(self, name):
        """A named place of PLACES as a 3D point (2D entries are put on the ground)."""
        return self.stand(PLACES[name])

    def camera_spec(self, name):
        """CAMS[name], or hello_set's camera "set:<name>" (gate, side, inside, deep, floating, bare, pyramid)."""
        if name.startswith("set:"):
            return dict(self.set["cameras"][name[4:]])
        return dict(CAMS[name])

    def cam(self, s, name, focus=None, handheld=0.008, seed=None, move=True, **over):
        """Put a shared camera on shot s: lens, position / aim (with its move when it has one and move=True),
        focus (default: its target) and a gentle handheld. over = entries to replace (lens=, pos=, pos1= ...).
        Returns the spec used."""
        c = dict(self.camera_spec(name), **over)
        s.lens(c["lens"], c.get("fstop", 2.8))
        if move and "pos1" in c:
            s.move(c["pos"], c["target"], c["pos1"], c.get("target1", c["target"]))
        else:
            s.move(c["pos"], c["target"])
        s.focus(focus if focus is not None else c["target"])
        if handheld:
            s.handheld(handheld, seed=sum(ord(ch) for ch in s.name) % 89 if seed is None else seed)
        return c

    # ------------------------------------------------------------------ the cast
    def actor(self, role, tag):
        """The cast member "<role>_<tag>", built on first use and registered with the Stage (st.cast).

        role   child          the narrator: a plain plains baby villager (babies wear no profession in the game)
               kid            the same model: the other children of the square
               farmer / librarian / toolsmith     the adults of the square (plains, level 1)
               steve_iron     Steve, iron chestplate, leggings and boots, no helmet, iron sword   (beats 1 to 5)
               steve_bed      plain Steve, no armor, empty hands: asleep in the red bed           (beat 3)
                              (in iron armor he read as a grey block on the bed: hello_scout_night_in03_bed_160)
               steve_diamond  Steve, full enchanted diamond armor, diamond sword                  (beat 6)
               watcher        Steve's own skin, no armor, empty hands, built dead still (no idle, no arm sway,
                              arms straight): every shot before the last
               watcher_eyes   the same figure with the blank white eyes, glowing EYE_GLOW: BEAT 22 ONLY
               zombie         the zombie of engine.undead
        tag    starts with your sequence prefix (sq, dn, in, dg, me); a further twin is just another tag:
               C.actor("child", "dg"), C.actor("child", "dg2"), C.actor("watcher", "me3").
        Twins exist because a character that is in two consecutive shots cannot be keyed before the second one
        starts: whoever must already be walking on the first frame of a shot is a twin that is not in the shot
        before."""
        if role not in ROLES:
            raise KeyError("no role %r (roles: %s)" % (role, ", ".join(ROLES)))
        if tag[:2] not in SEQUENCES:
            raise KeyError("tag %r must start with a sequence prefix: %s" % (tag, ", ".join(SEQUENCES)))
        st, name = self.st, "%s_%s" % (role, tag)
        c = st.cast.get(name)
        if c is not None:
            return c
        if role in ("child", "kid"):
            c = st.actor(name, "none", child=True)
        elif role in ("farmer", "librarian", "toolsmith"):
            c = st.actor(name, role)
        elif role == "zombie":
            c = undead.add_zombie(st, name)
        elif role == "steve_iron":
            c = players.add_player(st, name, "steve")
            players.equip(c, chestplate="iron", leggings="iron", boots="iron")
            c.hold("iron_sword")
        elif role == "steve_bed":
            c = players.add_player(st, name, "steve")             # no armor: in iron he is a grey block on the bed
        elif role == "steve_diamond":
            c = players.add_player(st, name, "steve")
            players.equip(c, "diamond", enchanted=True)
            c.hold("diamond_sword")
            self.stamp_glint(c)
        elif role == "watcher":
            c = players.add_player(st, name, "steve")
            self._stillness(c)
        elif role == "watcher_eyes":
            c = players.add_player(st, name, "herobrine", glow=EYE_GLOW)       # (still by itself)
        return c

    @staticmethod
    def _stillness(p):
        """What engine.players gives its 'herobrine' skin, for the plain skin: no idle sway, arms dead straight."""
        p.still = True
        for arm in (p.arm_r, p.arm_l):
            p._set_rest(arm, "rotation_euler", 1, 0.0)

    @staticmethod
    def stamp_glint(player):
        """The stamp work-around for animated materials (films/oneword.py stamp_every_frame): the enchant glint
        animates the materials of the armor boxes, and engine/stamp.py caches a mesh's digest with its materials',
        so chunked renders would declare good frames stale. A keyed custom property on each mesh makes the
        fingerprinter take it afresh at every frame. It changes no pixel. Called for steve_diamond by actor()."""
        for att in player._attached:
            ob = att.ob
            if ob.type == "MESH" and "stamp_every_frame" not in ob.data:
                ob.data["stamp_every_frame"] = 1.0
                ob.data.keyframe_insert('["stamp_every_frame"]', frame=1)

    def item(self, item_id, tag):
        """A dropped item of engine.mobs ("rotten_flesh"), registered with the Stage like a cast member:
        flesh = C.item("rotten_flesh", "dg"); flesh.place(f0, C.P("step")); flesh.animate(f0, s.frame_end + 1);
        st.use(s, flesh)."""
        if tag[:2] not in SEQUENCES:
            raise KeyError("tag %r must start with a sequence prefix: %s" % (tag, ", ".join(SEQUENCES)))
        name = "%s_%s" % (item_id, tag)
        it = self.st.cast.get(name)
        if it is None:
            it = self.st.cast[name] = mobs.make_dropped_item(item_id, name=name)
        return it

    def put(self, c, frame, place, toward=None, yaw=None):
        """place() a character on a named place (or a point), facing `toward` (a place name or a point) or `yaw`.
        Returns the 3D point."""
        pos = self.P(place) if isinstance(place, str) else self.stand(place)
        if yaw is None:
            aim = self.P(toward) if isinstance(toward, str) else (toward if toward is not None else (pos[0], pos[1] - 1.0))
            yaw = L.yaw_to(pos, aim)
        c.place(frame, pos, yaw)
        return pos

    def watcher(self, s, tag, frame=None, place="watch_door", yaw=None, role="watcher"):
        """The watcher (role "watcher", or "watcher_eyes" in dg22) placed on `place` on `frame` (default: the shot's
        first frame), facing WATCH_YAW at watch_door (else `yaw`, default: facing the child's door), dead still,
        in shot s (st.use). Returns him."""
        him = self.actor(role, tag)
        f = s.frame_start if frame is None else int(frame)
        if yaw is None:
            yaw = WATCH_YAW if place == "watch_door" else None
        if yaw is None:
            self.put(him, f, place, toward="door")
        else:
            self.put(him, f, place, yaw=yaw)
        self.st.use(s, him)
        return him

    # ------------------------------------------------------------------ the acting the story needs more than once
    @staticmethod
    def hello_nod(child, frame):
        """The child's hello: two quick nods, the only hello a villager has (Character.nod, 14 frames). Give the
        head its tipped-back look_at BEFORE this (the nods are offsets from the pose on `frame`). Returns the end
        frame."""
        return child.nod(frame)

    @staticmethod
    def crouch_twice(player, frame, down=6, up=6):
        """The player's hello: the sneak pose for `down` frames, up for `up` frames, twice (as players do it: the
        pose snaps, as in the game). Starts ON `frame`; returns the frame he is up again for good (frame + 18 with
        the defaults: down 6, up 6, down 6, up)."""
        f = int(frame)
        for _ in range(2):
            player.sneak(f, True)
            player.sneak(f + down, False)
            f += down + up
        return f - up

    @staticmethod
    def crouch_slow(player, frame, frames=24):
        """Beat 21: he sinks into the sneak pose over `frames` frames and STAYS down. The game snaps this pose; the
        slow descent is the story's one deliberate untruth about him (a player cannot do it). The pose reached on
        frame + frames is exactly Player.sneak's, and the player counts as crouching from then on (eye_point,
        crouching_at). Returns the frame he is down."""
        f0, f1 = int(frame), int(frame) + int(frames)
        cr, u = players.CROUCH, player.unit
        rot, loc = "rotation_euler", "location"
        seg = characters._segment
        targets = [(player.torso, rot, 0, cr["torso_x"]),
                   (player.hips, loc, 2, player._rest(player.hips, loc, 2) - cr["offset"]),
                   (player.body, loc, 2, player._rest(player.body, loc, 2) - cr["body_down"] * u),
                   (player.head, loc, 2, player._rest(player.head, loc, 2) - (cr["head_down"] - cr["body_down"]) * u),
                   (player.leg_l, loc, 1, player._rest(player.leg_l, loc, 1) + cr["leg_back"] * u),
                   (player.leg_r, loc, 1, player._rest(player.leg_r, loc, 1) + cr["leg_back"] * u)]
        for side in "rl":
            arm = player._arm(side)
            targets.append((arm, rot, 0, characters._val(arm, rot, 0, f0) + cr["arm_x"]))
        for ob, path, index, value in targets:
            seg(ob, path, index, [(f0, None), (f1, value)], "SMOOTH")
        # the head sinks a pixel into the torso, which is exactly as wide (players.CROUCH_HEAD_TIE): no depth tie
        characters._cut(player.head, "scale", 0, f0, players.CROUCH_HEAD_TIE)
        player._crouch = [c for c in player._crouch if c[0] < f1] + [(f1, True)]
        return f1

    @staticmethod
    def crouch_held(player, frame):
        """Already down on `frame` (a snap): the pose beat 22 opens in, the continuation of beat 21's crouch.
        Call it right after the player's place() on that frame."""
        return player.sneak(int(frame), True)

    @staticmethod
    def to_lens(c, frame, target, cam_pos, degrees=21.0):
        """A look target cheated `degrees` toward the camera: a child in profile that looks at something beyond
        itself shows the lens a blank cheek (films/poppy_day.py _to_lens). Returns the point to look_at."""
        eye = c.eye_point(frame)
        t = Vector(target if len(target) == 3 else (target[0], target[1], eye.z))
        d = t - eye
        to_cam = Vector(cam_pos) - eye
        a0 = math.atan2(d.y, d.x)
        a1 = math.atan2(to_cam.y, to_cam.x)
        da = (a1 - a0 + math.pi) % (2.0 * math.pi) - math.pi
        a = a0 + math.copysign(min(abs(da), math.radians(degrees)), da)
        flat = math.hypot(d.x, d.y)
        return (eye.x + flat * math.cos(a), eye.y + flat * math.sin(a), t.z)

    # ------------------------------------------------------------------ light
    def lights(self, s, key="gold", near=None, radius=None, at=None, **over):
        """The torch levels of LIGHTS[key] for shot s (Stage.lights once per shot; at= a frame inside the shot from
        which they hold, for the end of the night in beat 3). "night_door" boosts BOTH door torches (door=k).
        near / radius leave far torches out of the render (a place name or a point); over = Stage.lights
        arguments to replace."""
        spec = dict(LIGHTS[key], **over)
        k = spec.pop("door", None)
        extra = list(spec.pop("extra", ()))
        if k is not None and k != 1.0:
            extra += [(tuple(lamp.location), k) for lamp in self.door_torches]
        kw = dict(spec, extra=extra)
        if near is not None:
            kw.update(near=self.P(near) if isinstance(near, str) else near, radius=radius or 20.0)
        if at is not None:
            kw["at"] = at
        self.st.lights(s, **kw)

    def fill(self, name, pos, watts, shots, color=(1.0, 0.98, 0.95)):
        """A film-local shadowless fill light (props.make_light("fill")) that is on in the given shots only and
        hidden everywhere else (a hidden object is in no frame's stamp). `shots` = Shots and / or (first frame,
        last frame) spans: beat 3 can light the room from its sky change on with C.fill("morning", pos, W,
        [(C.T[s.name].change, s.frame_end)], color=(1.0, 0.85, 0.65)) (keyed by frame, so the same in every
        build: allowed). One name = one light with one strength: the doorstep fill of beats 4 and 22 is
        C.doorstep_fill(s), called in both shots."""
        lamp = self._fills.get(name)
        if lamp is None:
            lamp = self._fills[name] = props.make_light("fill", self.v.collection)
            lamp.name = "hello_fill_" + name
            lamp.location = pos
            lamp.data.color = color
            lamp.data.energy = watts
            lamp.visible_camera = False                 # a light, never a thing in the picture
            self.st.key(lamp, "hide_render", 1, True)
        for s in shots:
            a, b = (s.frame_start, s.frame_end) if hasattr(s, "frame_start") else (int(s[0]), int(s[1]))
            self.st.key(lamp, "hide_render", a, False)
            self.st.key(lamp, "hide_render", b + 1, True)
        return lamp

    DOORSTEP_FILL = dict(pos=(9.25, -7.9, 1.45), watts=260.0)      # beside the lens of "two_shot", on his face

    def doorstep_fill(self, s):
        """The near-neutral fill on his face for the two shots that compare the eyes: beat 4 and beat 22, the same
        light at the same strength (he faces the house; the golden sun that lights its front is behind him)."""
        return self.fill("doorstep", self.DOORSTEP_FILL["pos"], self.DOORSTEP_FILL["watts"], [s])

    # ------------------------------------------------------------------ time jumps
    @staticmethod
    def time_jump(frame):
        """End every particle still in the air on `frame` (engine.fx.stop_particles): call it on the first frame of
        a shot that jumps in time from a shot with particles (door crumbs, break bursts) BEFORE emitting that
        shot's own. The film calls it at every change of sequence already."""
        return fx.stop_particles(int(frame))

    # ------------------------------------------------------------------ words
    def words(self, s):
        """[(caption, frame)] of the words spoken in shot s (also C.T[s.name].words)."""
        return list(self.T[s.name].words)

    def at(self, s, word, n=0):
        """Frame on which the n-th `word` of shot s appears."""
        return self.T[s.name].at(word, n)
