"""Two Apples: everything the film (films/twoapples.py) and its five sequence files share.

    films/twoapples.py           the narration, the skies, the shot plan, the wall plan, build()     (lead director)
    films/twoapples_common.py    THIS FILE: the set, the places, the cameras, the cast, the light, the helpers, the
                                 contract
    films/twoapples_set.py       the set (the set builder's: engine/underground.py's trading hall under the seed-1
                                 village, the film's anchors ta_*, one scouted camera per beat TS.CAMERAS["b01".."b24"]
                                 with its still out/test/twoapples_set_<beat>_<what>[_<tag>].png, stage_bNN = a worked
                                 staging of every beat: READ IT before you stage your beat)
    films/twoapples_square.py    sq01 sq02 sq03 sq20          the square at dusk, the stair mouth by the well
    films/twoapples_evening.py   ev04 ev05 ev06               dad's bedroom (dusk in the window) and the stairwell
    films/twoapples_turn.py      tu07 tu09 tu10 tu11 tu12     the hall from above, the lever, dad hit and turned
    films/twoapples_cure.py      cu13 cu14 cu15 cu16 cu17 cu18 cu19    the potion, the apple, the wait, the trade,
                                                              dad who never looks behind him
    films/twoapples_box.py       bx08 bx21 bx22 bx23 bx24     the slot (twice), the flashback at the stair foot, the box

    $BPY -m tools.twoapples_timeline [--check|--json]   the shot plan: frames, words (no scene); the caption proof
    $BPY -m tools.twoapples_shots render ...            stills of single shots (its docstring): THE scouting tool
    $BPY -m tools.twoapples_shots build --sky under     one build: who is in which shot, the wall's state, stand-ins
    $BPY -m tools.twoapples_geo SHOT:F                  where every head lands in the frame, face size, angle to the
                                                        lens, what blocks it (a baby's face at its own width)
    $BPY -m tools.twoapples_palette F                   tools/palette_check on one frame at final quality
    $BPY -m render twoapples --still S [--zones]        one frame through render.py (each sky is one build)
    $BPY -m films.twoapples_set [bNN ...]               the set's self-test and its own proof stills

A sequence file exposes ONE FUNCTION PER SHOT, named like the shot:  def tu10_hug(st, s, C, nar)
    st   films.lookdev.Stage (st.use / st.hero / st.lights / st.see_through / st.key; st.v = the Village)
    s    the engine.shots.Shot (s.frame_start .. s.frame_end inclusive; s.lens / move / focus / handheld)
    C    the TwoApples object below: set, parts, places, cameras, cast, light, helpers; C.T[shot name] = the shot's
         row of the plan (frames, words with their frames, sky, neighbours, the wall's planned change)
    nar  the engine.narration.Narration (nar.at("word", sentence="b10") = the frame the word's caption appears on;
         C.at(s, "word") = the same within shot s)
build() in films/twoapples.py calls these functions IN TIMELINE ORDER, each exactly once, after every shot exists
(bx08 is called between tu07 and tu09: the order of the film, not of the files).
FIVE PEOPLE EDIT AT ONCE: build() imports each sequence file, and calls each shot function, inside a guard. A file that
does not import, or a shot that raises, is printed as "[twoapples] !!! ..." with its traceback and gets a plain
stand-in (its location's camera and light, nobody in it); the other files still build. TWOAPPLES_STRICT=1 in the
environment turns the guard off: hand in only when `TWOAPPLES_STRICT=1 $BPY -m tools.twoapples_shots build --sky S`
runs without a "!!!" line for EACH sky your shots use (square, evening: dusk; turn, cure, box: under).
Scout with tools/twoapples_shots.py / _geo.py / _palette.py (they write no meta.json). If you also preview through
render.py, use YOUR OWN sample count so no two directors share a preview directory (out/preview/twoapples/
270x480_<N>spp): PREVIEW_SAMPLES below (square 5, evening 6, turn 7, cure 9, box 10; the lead's whole-film
previews 8). `--frames` takes ONE shot name per call.

THE SEQUENCE CONTRACT (what a sequence director may and must do)
  MAY   edit his own file only: the bodies of its shot functions, its docstrings, private helpers and constants.
        Make further twins of the shared cast with his own tags (C.actor("steve", "cu2")). Add a film-local light
        with C.fill("<prefix>_<name>", ...) (the name starts with his prefix; hidden outside the shots he names).
        Move a camera of his own shots freely, unless the shot's docstring names a SHARED camera or place for it.
  MUST  keep every shot function's name and signature;
        give every shot a camera (C.cam: lens + move + focus + handheld; nothing is ever dead still; something
        already moving on its first frame: C.cam moves with ease "ease_out", at speed on frame 1; a camera that must
        hold first: C.cam_hold), its cast (st.use: everybody else is hidden), what it is about (st.hero, inside x
        8-82 %, y 14-60 % of the frame, clear of the caption band y 62-72 %) and its light (C.lights once per shot:
        LIGHTS below; under the ground the lever is st.use'd by C.lights unless lever=False: leave it out of a shot
        that sees through "ug_end_pier", cu13, cu16, cu19);
        take characters only through C.actor(role, tag) with a tag that starts with HIS prefix (sq, ev, tu, cu, bx),
        dropped items through C.item(item_id, tag): no other sequence can then disturb his keys;
        key each character in frame order; place() everybody on the first frame of a shot before any look_at()
        (look_at(f0, target, ease=0) BEFORE idle(): Character.idle puts a head key on its first frame);
        key nobody before a shot starts unless that instance is NOT in the shot before (pre-roll: use a twin);
        use the shared places and cameras where the shot's docstring names them (SHARED below), unchanged;
        FOLLOW THE WALL PLAN (films/twoapples.py WALL): dad's back wall is shut until tu09 opens it with the lever,
        open through tu10-cu14, shut by cu15 on its last word ("two"), shut again in cu16-bx23, and bx24 opens it
        from inside the box. Only the shot the plan names may move it, through C.wall_open / C.wall_shut (they check
        the state: engine/redstone raises on opening an open door); build() checks the state after every shot and
        forces the plan with a "!!!" line if a shot broke it;
        KEEP THE TWIST: the narrator is not in the picture from tu07 to bx21 except as the baby zombie villager of
        bx08, whose FACE NEVER READS there (a soft green shape and two tiny hands: U.hands_in_slot face="away" +
        U.shade_face, focus on the boots); bx21 shows the slot black and empty; the first time his green face reads
        is bx24, framed as the child in sq02 (CAMS "lip" / "box");
        keep the Minecraft truth: villagers keep their arms crossed (zombie villagers hold theirs out), have no
        fingers and no facial animation; dad's head stays front in tu09-tu12 (as the story says) and is turned up the
        aisle to its stop in cu18-cu19; a pushed villager slides (U.push), a baby jumps on a bed as the game does
        (U.bed_bounce); players walk, sprint, jump, sneak, swing, look; a cure / an infection is an instant swap with
        no puff (undead.infect / cure; in a capped cell U.hurt_in_cell / U.infect_in_cell, never undead.hurt with an
        attacker: that hop goes through the cap); swirls: weakness dark grey (the splash), strength yellow (the
        cure), nausea dark purple (after it); nothing that is not a vanilla block, item, mob or particle;
        render what he changed (tools/twoapples_shots.py at 540x960, 16 samples) and LOOK at it; run
        tools/twoapples_palette on one frame per shot.
  MUST NOT  touch films/twoapples.py, this file, films/twoapples_set.py, another sequence file or anything in
        engine/, render.py, tools/ (his own new tools/twoapples_<seq>_*.py excepted); change the narration, the
        cuts, a sky or the film's length; make anything depend on which sky is being built (no `if sky ...`);
        call st.shot / st.sky_change / st.dip / st.finish (the film does); key hide_render on a character, its
        items, the lever or the door (st.use, undead.vanish / appear and the set's calls do it); move dad's wall
        outside the shot the wall plan names; boost torches beyond LIGHTS without tools/palette_check (lit stone
        next to a torch sits on the palette's limit); build a character with st.actor / players.add_player /
        undead.add_* directly (it would escape the twin rule); open a see-through cutaway in the film's first shot
        (Stage.see_through loses it there: sq01 has none); start a final render (render.py --frames without --res /
        --samples).
  If a shared place or camera is wrong for his shot, he says so in his result; he does not move it.

SHARED (decided once, used by two shots or two sequences: ONE definition each, below)
  CAMS["lip"] + CAMS["box"]  THE MIRROR PAIR: sq02 (the child at the lip, staring down into the glow) and bx24
                    (the baby zombie villager in the box, framed where the child stood: "the last shot of the film
                    repeats it"). Same lens 50 mm f/2.0, the same 2.4 blocks from the head, the same eye height, the
                    head at x 50 / y 44-46 %, the same three-quarter look down to frame right; lit from below in both.
                    Neither director changes lens, stop, distance, height or the screen direction of the look.
  CAMS["slot"]      bx08 (locked, focus on the boot point) and bx21 (the same, focus on the slot, the slow push to
                    pos1): one camera on the floor of the back corner, square on to the slot.
  PLACES / anchors  ug_lip (sq02 the child; sq03's push ends there), ug_cell_dad (dad and zombie dad, tu07-cu17, bx24),
                    ug_cell_dad_mid (cu18, cu19: a head turned west to its stop), ug_cell_farmer / _fletcher / _cleric
                    (every hall shot that shows the row: C.cells), ug_aisle_dad (Steve at the counter: cu14, cu17),
                    ug_stair_foot (bx22, bx23), ta_box_baby (bx24)
  THE WALL          films/twoapples.py WALL: opened in tu09, shut in cu15, opened in bx24 (C.wall_open / C.wall_shut)
  DAD'S STATES      a villager (librarian, book hat, level 2) up to tu12's last blow; the zombie villager from that
                    frame (U.infect_in_cell) to the swap inside cu17 (undead.cure ... the swap "between one frame and
                    the next"); the villager again from there (cu17 after the swap, cu18, cu19, bx24)
  THE SKIES         films/twoapples.py SKIES ("dusk", "under") and the light recipes LIGHTS / GLOWS / BOOSTS below

THE LESSONS OF THE HELLO'S SHOOT (each cost a re-render there; they hold here)
  - A villager's head turned more than about 26 degrees beyond profile from the lens reads as a blank box (at 100-118
    degrees a brown box): cheat a look at something beyond him to at most 78 degrees off the lens (C.cheat(...,
    max_off=65..78), C.to_lens). tools/twoapples_geo prints `off` (the head's nose to the lens).
  - Character.idle(f0, ...) puts a head key on f0: look_at(f0, ..., ease=0) BEFORE idle. place() every character on a
    shot's first frame before any look_at.
  - A held item: Player.hold("golden_apple") for Steve, fx.hold_out (C.book) for a villager's trade item; a dropped item
    is C.item (the rotten flesh).
  - Two render.py --frames processes writing the same preview directory lose each other's stamps: your own sample
    count (PREVIEW_SAMPLES). --frames takes ONE shot name.
  - A cut is only as good as the frames on both sides: nothing important in the last 3 frames before a cut; a word
    never straddles a cut (the plan guarantees it); something is already moving on frame 1 of every shot.
  - A small thing is seen only if it is what is in focus (the lever, the hands at the slot, the apple, the emerald).
  - The face-width column of tools/twoapples_geo knows a baby's head is half an adult's.
  - Lit stone next to a torch sits on the palette limit (tools/palette_check): do not boost a torch beyond BOOSTS.
FROM THE SET BUILDER AND THE ENGINE (measured; films/twoapples_set.py docstring, engine/underground.py GOTCHAS)
  - During the 12 red hurt frames Stage.hero finds a hurt head hidden: stills before or after a blow.
  - Walking legs smear with motion blur (bx08: the boots are sharp on the legs-together frames only).
  - cu18: the book's glint in the distance and dad's face are not in one frame (Steve walks under the lens).
  - jump_loop keys the open-air jump (1.252): under the aisle's ceiling his head clips 0.05 into it for about 2 frames
    at each top (cu16: not looked for yet).
  - fx.hold_out without frame_end keeps the item visible in every later shot: C.book gives it its end.
  - The see-through end pier and end wall still cast shadows: a character behind them is in their shade (cu13's
    COUNTER_BOUNCE and the dad-side glow).

SCOUTED (look at these before you stage a beat)
  the set builder's   out/test/twoapples_set_<beat>_<what>[_<tag>].png (+ _zones.png): one per beat camera, staged as
                      the beat says (films/twoapples_set.py stage_bNN), each with its numbers in that file's docstring
  the stub film       out/test/twoapples_shots_sheet.png: one tile per shot (180x320, 6 samples, the middle frame, its
                      caption); out/test/twoapples_0.1.png (render.py --still 0.1, 270x480, 4 samples)
  the lead's stills   (540x960, 16 samples, the stub cast in place, _zones.png beside each)
    twoapples_scout_bx24_kept_1480.png        the hold with the engine's 6 W strip: black (p95 luma 16)
    twoapples_scout_s40_bx24_kept_1480.png    40 W: still dark (p95 40)
    twoapples_scout_s120_bx24_kept_1480.png   120 W: ADOPTED (GLOWS slot_strip): the green face reads (p95 69)
    twoapples_scout_s120_bx24_kept_1500.png   the wall open, doorway glow 180 W: ADOPTED: lit fully (p95 130)
    twoapples_scout_bx24_kept_1545.png        the pan's end: dad's back at the right edge, the baby out of the frame
    twoapples_scout_s40_bx08_slot_516.png     the slot on "zombie": a green head shape and a hand, no face
    twoapples_scout_tu09_lever_592.png        on "wall": the doorway open and black beside dad
    twoapples_scout_cu17_emerald_1092.png     on "emerald": dad cured with the glinting book over the emerald
    twoapples_scout_sq20_grow_1222.png        the children invisible behind the well at 16 blocks (MEASURED PROBLEM)
    twoapples_scout_ev06_stairs_358.png       the first stub: his head under the lens (fixed: RUN_PRE 28)
    twoapples_pal_bx24_kept_1484.png / _1500.png   tools/twoapples_palette in the film build: no failure
  Side by side (the lead's scratch composites, not kept): sq02 (the set's b02 still, the stub's own staging) against
  bx24's hold: the mirror holds (eyes x 49 / y 44 against x 50 / y 46, 138 against 130 px).

Coordinates: Blender blocks, +X east, +Y north, +Z up; the square's ground 0.0 (a dirt path 1/16 lower), the hall's
floor F = -10. The well's stone x -3..2, y -3..2; the stair mouth x 4..5, y -3..0 (ug_lip (4.85, 1.42, 0)); house_a's
bed wing x 15..19, y -13..-9, floor z 1, dad's red bed house_a_bed_2 (18..19, -10), pillow east; the stairwell x 4..5,
y 0..-9, the landing y -10; the aisle x -8..19, y -12..-11 (dark west of x 5); the cells face north from y -14 (front
row y -13): farmer x 7, fletcher 9, cleric 11, the 2-wide pier 12..13, DAD 14 (lectern), the end pier 15 with the
LEVER on its north face (15, -12, F+1); dad's back wall = the piston door (14, -15, F / F+1); the zombie box (14, -16)
with the floor-level slot of bars (15, -16, F) facing the back corner x 16..19, y -17..-13 (its one torch (19, -14)).
"""
import math

from mathutils import Vector

from engine import characters, fx, mobs, players, props, undead
from engine import underground as U
from films import lookdev as L
from films import twoapples_set as TS

FPS = 24
F = U.F                                # the hall floor's walking surface (z -10)
PATH_Z = -0.0625                       # a dirt path lies one pixel below the grass
FINAL_RES, FINAL_SAMPLES = (540, 960), 16      # this film's final quality (set on the scene by films/twoapples.py)

SEQUENCES = {"sq": "square", "ev": "evening", "tu": "turn", "cu": "cure", "bx": "box"}
PREFIX = {v: k for k, v in SEQUENCES.items()}
PREVIEW_SAMPLES = {"square": 5, "evening": 6, "turn": 7, "cure": 9, "box": 10}    # one preview directory each (lead 8)


def build_set(scene):
    """The village of "Two Apples": seed 1 with engine/underground.py's set and the film's additions
    (films/twoapples_set.py). Returns (Village, UndergroundSet)."""
    return TS.build_set(scene)


# ----------------------------------------------------------------------------------------------------------------
# places: a name of PLACES, or any anchor of the set by its full name (ug_* of engine/underground.py, ta_* of
# films/twoapples_set.py, the village's own); C.P(name) gives the 3D point (2D entries on the ground), C.yaw(name)
# the anchor's facing
# ----------------------------------------------------------------------------------------------------------------
PLACES = {
    # ---- the square (sq01-03, sq20)
    "steve_in": (5.0, 6.5, 0.0),          # sq01: Steve's start, north of the mouth (walks ug_down into it)
    # ---- the house (ev04, ev05): the red bed's foot (ta_kid_bed_foot = ta_kid_bed_door, z 1.56 on the mattress)
    "door_in": TS.DOOR_IN,                # house_a's door at a child's look height (ev05: he faces it)
    "gable_pane": TS.GABLE_PANE,          # the gable window over the bed wall (the indigo dusk in it)
    # ---- the hall
    "dad_torch": (14.5, -10.6, F + 1.9),  # the wall torch facing dad's cell (group ug_dad): BOOSTS key on it
    "seam": TS.SEAM,                      # cu19: the seam between the piston wall's two blocks, on dad's side
    "box_look": TS.BOX_LOOK,              # bx24: where the baby zombie villager stares (the foot of the door)
    "zombie_out": (2.4, -11.0, float(F)),  # bx22: = ta_zombie_out, the zombie stepping out of the dark west aisle
}
LOOK_FRONT_DZ = 1.5                    # a villager in his cell "staring straight ahead": at the aisle point in front of
#                                        his cell (ug_aisle_<name>), this high (C.cells)

# ----------------------------------------------------------------------------------------------------------------
# cameras: name -> dict(pos, target, lens, fstop[, pos1, target1, see]); C.cam(s, name) puts one on a shot.
# "set:<beat>" = the set builder's scouted camera TS.CAMERAS["b01".."b24"] (its pos0 / target0 -> pos / target form is
# read as a move from pos0 to pos); None = the shot's OWN camera, a constant of its sequence file given whole as
# keywords. `see` = the cutaways the camera looks through (C.cam keys them for the shot).
# ----------------------------------------------------------------------------------------------------------------
_KEEP = ("pos", "target", "lens", "fstop", "pos1", "target1", "see", "boot", "look")


def _norm(c):
    """A camera dict in the form C.cam takes: pos / target = the START, pos1 / target1 = the end of a move (the set
    writes some moves as pos0 / target0 -> pos / target)."""
    c = dict(c)
    if "pos0" in c or "target0" in c:
        start = (c.pop("pos0", c["pos"]), c.pop("target0", c["target"]))
        c["pos1"], c["target1"] = c["pos"], c["target"]
        c["pos"], c["target"] = start
    return {k: v for k, v in c.items() if k in _KEEP}


CAMS = {
    # THE MIRROR PAIR (sq02 and bx24): the set builder's b02 and b24, built as mirrors (50 mm f/2.0, 2.4 from the
    # head, eye height; head x 50 / y 44 in sq02, x 50 / y 46 in bx24; the look down to frame right in both)
    "lip": _norm(TS.CAMERAS["b02"]),      # from the child's right over the rim, 38 degrees off his facing
    "box": _norm(TS.CAMERAS["b24"]),      # inside the box through its see-through side; the pan (pos1 / target1)
    #                                       to dad's back after his first step: C.cam_hold (U.hold_then_move)
    # bx08 and bx21: on the floor of the back corner, square on to the slot 3.75 away (the set's b08; "boot" = the
    # focus point of bx08, where Steve's boots cross; bx21 focuses on U.SLOT_FACE and pushes to pos1)
    "slot": _norm(TS.CAMERAS["b08"]),
}
CAMS["slot_locked"] = {k: v for k, v in CAMS["slot"].items() if k not in ("pos1", "target1")}      # bx08 (no push)
# the stand-ins of a failed shot (films/twoapples.py): its location's camera
STAND_IN = {"square": ("set:b20", "square"), "evening": ("set:b05", "room"), "turn": ("set:b12", "hall"),
            "cure": ("set:b12", "hall"), "box": ("slot_locked", "box")}

# ----------------------------------------------------------------------------------------------------------------
# light: C.lights(s, key). The set builder's recipes (films/twoapples_set.py LIGHTS: each rendered and looked at,
# palette-checked). Torches below the ground are the underground set's point lights (groups U.LIGHT_GROUPS) at
# TS.UNDER 1.0 over the baked block light (drawn at TS.HALL_EMIT 0.45 of the game's brightness: the torch pools and
# the dark between them read); "hall" turns the hall's cool shadowless fill on (inside="ug_hall"), "box" leaves it
# off (it passes walls: it would light the box and the dark west aisle).
# ----------------------------------------------------------------------------------------------------------------
_UG = tuple(U.LIGHT_GROUPS)


def _groups(k):
    return {g: k for g in _UG}


LIGHTS = {
    "square": dict(scale=1.3, groups=_groups(1.0), near="ug_mouth_target", radius=22.0),   # sq01, sq20 (near "well")
    "push": dict(scale=1.0, groups=_groups(1.0), near="ug_lip", radius=20.0),              # sq03
    "lip": dict(scale=1.0, groups=_groups(1.0), near="ug_lip", radius=18.0, boost="mouth"),   # sq02 + GLOWS mouth
    "room": dict(scale=1.2, groups={U.HOUSE: 1.5}, near="house_a_center", radius=14.0, inside=()),  # ev04, ev05 +
    #                                                    GLOWS room_cool (house_a's own fill OFF: a flat grey box)
    "stairs": dict(scale=0.0, groups=_groups(1.0)),                                        # ev06
    "hall": dict(scale=0.0, groups=_groups(TS.UNDER), inside="ug_hall"),                   # tu07, tu09-cu19, bx22-23
    "box": dict(scale=0.0, groups=_groups(TS.UNDER)),                                      # bx08, bx21, bx24
}
UNDER_KEYS = ("stairs", "hall", "box")     # keys under the ground: C.lights st.use's the lever there (lever=False: not)
# torch boosts (Stage.lights extra=: the torch nearest the point x factor): the set builder's, each palette-checked
BOOSTS = {
    "mouth": list(TS.MOUTH_KEY),                         # sq02: the stairwell's two top torches x 2.2 (his key below)
    "corner": list(TS.CORNER_KEY),                       # bx08: the back corner's torch x 1.8 on the baby's hands
    "dad13": [((14.5, -10.6, F + 1.9), 1.8)],            # cu13: the torch facing dad's cell x 1.8
    "dad17": [((14.5, -10.6, F + 1.9), 1.6)],            # cu17
    "dad24": [((14.5, -10.6, F + 1.9), 2.5)],            # bx24: the light that falls into the box when it opens
}
# THE REVEAL'S LIGHT (bx24; the lead's scouting, out/test/twoapples_scout_s120_bx24_kept_1480.png / _1500.png against
# twoapples_scout_bx24_kept_1480.png): with the engine's strip (U.SLOT_STRIP_WATTS 6) the baby zombie villager in the
# hold was black (face box mean rgb 7 / 11 / 3, p95 luma 16 of 255; 40 W: p95 40): the story's named risk for the
# ending ("if the small green figure in the dark box does not read as the narrator, the ending is lost"). At 120 W
# the green face, the red eyes and the brown robe read in the hold (p95 69; sq02's lit child 189), still a dark box
# lit from below through the bars; at the wall's opening the doorway glow at 180 W (the engine's 60) "lights him
# fully" (p95 130 on frame 1500), as the story's fallback asks.
SLOT_STRIP_WATTS = 120.0
DOORWAY_WATTS = 180.0
# film-local lights for one shot (C.glow(s, name[, start])): engine.underground.bounce, hidden outside the shot
# (hidden objects are in no frame's stamp). (position, watts, colour, kind): kind "torch" = a shadowed point with the
# torches' near field, "fill" = shadowless (it reaches little near a face: engine note on props.make_light("fill"))
GLOWS = {
    "mouth_glow": (TS.MOUTH_GLOW, TS.MOUTH_GLOW_WATTS, U.POINT_COLOR, "torch"),       # sq02: his face lit from below
    "room_cool": (TS.ROOM_COOL, TS.ROOM_COOL_WATTS, TS.ROOM_COOL_COLOR, "fill"),      # ev04, ev05: skin under 0.52
    "down_fill": (TS.DOWN_FILL, TS.DOWN_FILL_WATTS, (0.95, 0.97, 1.0), "fill"),       # tu07: the open pockets
    "counter_bounce": (U.COUNTER_BOUNCE, TS.COUNTER_WATTS, (1.0, 0.95, 0.88), "fill"),  # cu13: Steve's lens side
    "dad_side": (TS.DAD_SIDE_FILL, TS.DAD_SIDE_WATTS, U.POINT_COLOR, "torch"),        # cu13, cu19: dad's lens side
    "slot_strip": (U.SLOT_STRIP, SLOT_STRIP_WATTS, U.POINT_COLOR, "torch"),           # bx24: the strip through the
    #                                                                                   slot, his only light at first
    "doorway_glow": (U.DOORWAY_GLOW, DOORWAY_WATTS, U.POINT_COLOR, "torch"),          # bx24 from the wall's opening
}

# role -> how TwoApples.actor builds it
ROLES = ("child", "kid", "grownup", "dad", "zdad", "farmer", "fletcher", "cleric", "steve", "zombie", "zchild")
MAX_OFF = 65.0         # a villager watching something beyond itself: its nose at most this far from the lens
#                        (The Hello's meadow: at 100-118 degrees a brown box; 78 a 2 px nose; 65 nose and both eyes)
CELL_ROLES = ("farmer", "fletcher", "cleric", "dad")


def yaw_to(src, dst):
    """Yaw that makes a character at src (facing -Y at yaw 0) face dst."""
    return L.yaw_to(src, dst)


def up(p, dz):
    """Point p raised by dz."""
    return (p[0], p[1], p[2] + dz)


class ShotInfo:
    """One row of the film's shot plan with its frames: C.T[shot name].

    name, beat, sequence, sky, sentence (the engine.narration Sentence spoken in it), frame_start, frame_end
    (inclusive), frames, seconds, words = [(caption, frame it appears on)], wall = the change of dad's wall this
    shot makes ("open" / "shut" / None: films/twoapples.py WALL), dip (an encoder dip on its first frame), prev /
    next = the neighbouring shots' names (or None)."""

    def __init__(self, **kw):
        self.change, self.sky_after, self.dip, self.prev, self.next, self.wall = None, None, False, None, None, None
        self.__dict__.update(kw)

    def at(self, word, n=0):
        """Frame on which the n-th `word` spoken in this shot appears (case-insensitive caption text)."""
        hits = [f for w, f in self.words if w.lower().strip(".,'") == word.lower()]
        return hits[n]

    def __repr__(self):
        return "<%s beat %d %s %s %d-%d>" % (self.name, self.beat, self.sequence, self.sky, self.frame_start,
                                            self.frame_end)


class TwoApples:
    """The film's shared context, handed to every shot function as C.

    C.st / C.v / C.ug / C.A   the Stage, the Village, the UndergroundSet (ug.door, ug.lever, ug.open_wall ...), the
                          anchors (C.A["ug_cell_dad"]); C.D = TS.set_data(v, ug) (anchors, yaws, paths, parts,
                          cutaways, cameras, lights); C.paths = the Village's paths (ug_down, ug_push, ta_round_well)
    C.nar, C.T            the Narration; the shot plan: C.T["tu10_hug"] -> ShotInfo
    C.P(name), C.yaw(name)    a place as a 3D point / its facing (PLACES, then any anchor)
    C.cam(s, name, ...)   one of CAMS, "set:<beat>", or None with the shot's own values; C.cam_hold: hold, then move
    C.actor(role, tag)    a cast member, built once per tag: roles in ROLES, tag starts with the sequence prefix
    C.cells(s, tag, ...)  the farmer, fletcher, cleric and dad in their cells, staring straight ahead
    C.item(id, tag)       a dropped item (rotten flesh), registered like a cast member; C.book: dad's enchanted book
    C.wall_open / C.wall_shut / C.wall_is_open    dad's back wall (the piston door), by THE WALL PLAN only
    C.lights(s, key) / C.glow(s, name) / C.fill(name, ...)    the light recipes; a film-local light of your own
    C.cheat / C.to_lens   a look cheated toward the lens
    C.shots, C.memo       every Shot of the film by name; a dict for handing things from one shot function to a later
                          one of the SAME sequence (key prefixed with it: C.memo["cu_cure"])
    """

    def __init__(self, st, ug, nar=None, timeline=None):
        self.st, self.v, self.ug = st, st.v, ug
        self.A = st.v.anchors
        self.paths = st.v.paths
        self.D = TS.set_data(st.v, ug)
        self.nar = nar
        self.T = dict(timeline or {})
        self.shots = {}            # shot name -> engine.shots.Shot (filled by films/twoapples.py first)
        self.memo = {}             # what one shot function leaves for a later one of ITS OWN sequence
        self._fills = {}
        self.wall_log = []         # [(frame, "open" | "shut", who)] in the order they were keyed

    # ------------------------------------------------------------------ places and cameras
    def stand(self, p):
        """(x, y) -> the point a character stands on there: ground height (the square), a pixel lower on a dirt
        path. A 3D point is returned as it is (everything under the ground is given in 3D: the floor is F)."""
        if len(p) == 3:
            return (float(p[0]), float(p[1]), float(p[2]))
        x, y = float(p[0]), float(p[1])
        z = self.v.ground(x, y)
        top = self.v.world.block_id(int(math.floor(x)), int(math.floor(y)), int(round(z)) - 1)
        return (x, y, z + (PATH_Z if top == "dirt_path" else 0.0))

    def P(self, name):
        """A place as a 3D point: PLACES[name] (2D entries on the ground), or any anchor of the Village by its full
        name (ug_cell_dad, ta_box_baby, house_a_center ...)."""
        if name in PLACES:
            return self.stand(PLACES[name])
        return tuple(self.A[name])

    def yaw(self, name, default=None):
        """The facing of an anchor (Village.yaws; None / default when it has none)."""
        return self.v.yaws.get(name, default)

    def camera_spec(self, name):
        """CAMS[name], the set's camera "set:<beat>" (TS.CAMERAS, a pos0 -> pos move read as pos -> pos1), or {}
        for None."""
        if name is None:
            return {}
        if name.startswith("set:"):
            return _norm(TS.CAMERAS[name[4:]])
        return dict(CAMS[name])

    def cam(self, s, name, focus=None, handheld=0.006, seed=None, move=True, ease="ease_out", see=None, **over):
        """Put a camera on shot s: lens, position / aim (with its move when it has one and move=True), focus
        (default: its target) and a gentle handheld, and the cutaways it looks through (`see`, default the spec's
        own; st.see_through for this shot only). name = one of CAMS, "set:<beat>" or None (the shot's own camera
        given whole as keywords: pos, target, lens[, fstop, pos1, target1, see]). A target may be an object (a
        Character's head: the aim follows it). ease of the move: default 'ease_out' = AT SPEED ON THE FIRST FRAME,
        slowing to the last ('linear' for a constant drift; engine.shots' own 'smooth' starts from rest: a still
        for the first half second). Returns the spec used."""
        c = dict(self.camera_spec(name), **over)
        if "pos" not in c or "target" not in c or "lens" not in c:
            raise KeyError("camera %r for %s needs pos, target and lens" % (name, s.name))
        s.lens(c["lens"], c.get("fstop", 2.8))
        if move and ("pos1" in c or "target1" in c):
            s.move(c["pos"], c["target"], c.get("pos1", c["pos"]), c.get("target1", c["target"]), ease=ease)
        else:
            s.move(c["pos"], c["target"])
        s.focus(focus if focus is not None else c["target"])
        if handheld:
            s.handheld(handheld, seed=sum(ord(ch) for ch in s.name) % 89 if seed is None else seed)
        for cut in (c.get("see", ()) if see is None else see):
            self.st.see_through(s, cut)
        return c

    def cam_hold(self, s, name, frame_move, frame_end=None, focus=None, handheld=0.004, seed=None, ease="smooth",
                 see=None, **over):
        """A camera that HOLDS the spec's start until `frame_move`, then moves to its pos1 / target1 by `frame_end`
        (default: the shot's end) and holds there (engine.underground.hold_then_move: tu09's pan from the lever to
        the wall, bx24's pan with his first step). The handheld keeps the hold alive. Returns the spec used."""
        c = dict(self.camera_spec(name), **over)
        s.lens(c["lens"], c.get("fstop", 2.8))
        U.hold_then_move(s, frame_move, c["pos"], c["target"], c.get("pos1", c["pos"]), c.get("target1", c["target"]),
                         frame_end=frame_end, ease=ease)
        s.focus(focus if focus is not None else c["target"])
        if handheld:
            s.handheld(handheld, seed=sum(ord(ch) for ch in s.name) % 89 if seed is None else seed)
        for cut in (c.get("see", ()) if see is None else see):
            self.st.see_through(s, cut)
        return c

    def cam_keys(self, s, name, keys, focus=None, handheld=0.006, seed=None, see=None, **over):
        """A camera whose move from the spec's pos / target to its pos1 / target1 follows `keys` = [(frame, u), ...]
        (u = 0 the start, 1 the end; frames inside the shot, u never decreasing): a smooth monotone curve through
        them (Fritsch-Carlson: no overshoot, the speed continuous), flat before the first key and after the last.
        tu07's ride: at speed on frame 1, dad's window on "dad", settled by "room". The aim blends with the same u
        (engine.shots bakes position and aim from one curve, as U.hold_then_move re-times it). Returns the spec."""
        c = dict(self.camera_spec(name), **over)
        if "pos1" not in c and "target1" not in c:
            raise KeyError("cam_keys: camera %r for %s has no move (pos1 / target1)" % (name, s.name))
        ks = sorted((float(f), float(u)) for f, u in keys)
        xs, ys = [k[0] for k in ks], [k[1] for k in ks]
        n = len(ks)
        d = [(ys[i + 1] - ys[i]) / max(1e-9, xs[i + 1] - xs[i]) for i in range(n - 1)]
        m = [d[0]] + [0.0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2.0 for i in range(1, n - 1)] + [d[-1]]
        for i in range(n - 1):                           # Fritsch-Carlson: keep it monotone
            if abs(d[i]) < 1e-12:
                m[i] = m[i + 1] = 0.0
                continue
            a, b = m[i] / d[i], m[i + 1] / d[i]
            r = a * a + b * b
            if r > 9.0:
                t = 3.0 / math.sqrt(r)
                m[i], m[i + 1] = t * a * d[i], t * b * d[i]

        def u(frame):
            if frame <= xs[0]:
                return ys[0]
            if frame >= xs[-1]:
                return ys[-1]
            i = max(j for j in range(n - 1) if xs[j] <= frame)
            h = xs[i + 1] - xs[i]
            t = (frame - xs[i]) / h
            h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
            h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
            return min(1.0, max(0.0, h00 * ys[i] + h10 * h * m[i] + h01 * ys[i + 1] + h11 * h * m[i + 1]))
        s.lens(c["lens"], c.get("fstop", 2.8))
        s._u = u                                         # an instance attribute: Shot._bake reads self._u(frame)
        s.move(c["pos"], c["target"], c.get("pos1", c["pos"]), c.get("target1", c["target"]), ease="linear")
        s.focus(focus if focus is not None else c["target"])
        if handheld:
            s.handheld(handheld, seed=sum(ord(ch) for ch in s.name) % 89 if seed is None else seed)
        for cut in (c.get("see", ()) if see is None else see):
            self.st.see_through(s, cut)
        return c

    def rack(self, s, target, frame, frames=12):
        """Pull the focus of shot s to `target` (a Character's head / an object / a point) starting ON `frame`, over
        `frames` frames (Shot.focus takes film seconds: this converts). Call after C.cam."""
        tgt = target.head if isinstance(target, characters.Character) else target
        s.focus(tgt, at_s=(int(frame) - 1) / float(FPS), rack_s=frames / float(FPS))
        return frame + frames

    # ------------------------------------------------------------------ the cast
    @staticmethod
    def _check_tag(tag):
        if tag[:2] not in SEQUENCES:
            raise KeyError("tag %r must start with a sequence prefix: %s" % (tag, ", ".join(SEQUENCES)))

    def actor(self, role, tag):
        """The cast member "<role>_<tag>", built on first use and registered with the Stage (st.cast).

        role   child      the narrator: a plain plains baby villager (babies wear no profession in the game)
               kid        the same model: the other children of the square (sq20)
               grownup    the child who grew up (sq20): the unemployed adult, plain brown robe
               dad        the librarian in the book hat, level 2 (the set's stills); arms crossed
               zdad       dad turned: the zombie villager librarian, level 2 (engine.undead; aggro() = arms out)
               farmer / fletcher / cleric    the other three in their cells (level 2)
               steve      Steve (engine.players: walk, jump, attack, hold("golden_apple"), throw ...)
               zombie     the adult zombie of engine.undead (bx22, bx23)
               zchild     THE NARRATOR TURNED: a baby zombie villager, plains, no profession (bx08, bx24)
        tag    starts with your sequence prefix (sq, ev, tu, cu, bx); a further twin is just another tag:
               C.actor("steve", "cu"), C.actor("steve", "cu2").
        Twins exist because a character that is in two consecutive shots cannot be keyed before the second one
        starts: whoever must already be moving on the first frame of a shot is a twin that is not in the shot before.
        Every call with the same role and tag returns the same object."""
        if role not in ROLES:
            raise KeyError("no role %r (roles: %s)" % (role, ", ".join(ROLES)))
        self._check_tag(tag)
        st, name = self.st, "%s_%s" % (role, tag)
        c = st.cast.get(name)
        if c is not None:
            return c
        if role in ("child", "kid"):
            c = st.actor(name, "none", child=True)
        elif role == "grownup":
            c = st.actor(name, "none")
        elif role == "dad":
            c = st.actor(name, "librarian", level=2)
        elif role in ("farmer", "fletcher", "cleric"):
            c = st.actor(name, role, level=2)
        elif role == "zdad":
            c = undead.add_zombie_villager(st, name, "librarian", level=2)
        elif role == "zchild":
            c = undead.add_zombie_villager(st, name, "none", baby=True)
        elif role == "steve":
            c = players.add_player(st, name, "steve")
        elif role == "zombie":
            c = undead.add_zombie(st, name)
        return c

    def put(self, c, frame, place, toward=None, yaw=None):
        """place() a character on a named place (or a point), facing `toward` (a place name or a point), `yaw`, or
        (neither) the anchor's own facing, else south. Returns the 3D point."""
        pos = self.P(place) if isinstance(place, str) else self.stand(place)
        if yaw is None and toward is not None:
            aim = self.P(toward) if isinstance(toward, str) else toward
            yaw = L.yaw_to(pos, aim)
        if yaw is None and isinstance(place, str):
            yaw = self.yaw(place)
        c.place(frame, pos, 0.0 if yaw is None else yaw)
        return pos

    def cells(self, s, tag, who=CELL_ROLES, dad_role="dad", dad_at="ug_cell_dad", look=None, frame=None):
        """The villagers in their cells for shot s, each placed ON `frame` (default the shot's first) on
        ug_cell_<name> (dad on `dad_at`), facing north into the aisle, his head on look(name) (default: straight
        ahead, the aisle point in front of his cell LOOK_FRONT_DZ high), no ease. who = names of CELL_ROLES; dad is
        built as `dad_role` ("dad", or "zdad" for zombie dad: then aggro'd, arms out). st.use's them.
        Returns {name: Character} (dad under "dad" in both cases)."""
        f0 = s.frame_start if frame is None else int(frame)
        out = {}
        for n in who:
            role = dad_role if n == "dad" else n
            c = self.actor(role, tag)
            spot = dad_at if n == "dad" else "ug_cell_%s" % n
            c.place(f0, self.P(spot), self.yaw(spot, math.pi))
            target = look(n) if look is not None else up(self.A["ug_aisle_%s" % n], LOOK_FRONT_DZ)
            c.look_at(f0, target, ease=0)
            if role == "zdad":
                c.aggro(f0, ease=0)
            out[n] = c
        self.st.use(s, *out.values())
        return out

    def item(self, item_id, tag, count=1, seed=0):
        """A dropped item of engine.mobs ("rotten_flesh"), registered with the Stage like a cast member:
        flesh = C.item("rotten_flesh", "bx"); flesh.place(f, point); st.use(s, flesh)."""
        self._check_tag(tag)
        name = "%s_%s" % (item_id, tag)
        it = self.st.cast.get(name)
        if it is None:
            it = self.st.cast[name] = mobs.make_dropped_item(item_id, name=name, count=count, seed=seed)
        return it

    def book(self, villager, frame_start, frame_end):
        """Dad holds out the enchanted book on his crossed arms from frame_start to frame_end (EXCLUSIVE: give the
        shot's end + 1), with its glint (engine.fx hold_out, the game's ShowTradesToPlayer). The glint animates a
        material: the stamp work-around is applied. Returns the book object."""
        ob = fx.hold_out(villager, "enchanted_book", int(frame_start), int(frame_end), enchanted=True)
        self.stamp_glint(ob)
        return ob

    @staticmethod
    def stamp_glint(*things):
        """The stamp work-around for animated materials (films/oneword.py stamp_every_frame; CONTRACT.md known
        issues): the enchant glint animates a material, and engine/stamp.py caches a mesh's digest with its
        materials', so chunked renders would call good frames stale. A keyed custom property on each mesh makes the
        fingerprinter take it afresh at every frame; it changes no pixel. things = objects or Players (their
        attached items: Player.hold(..., enchanted=True))."""
        obs = []
        for t in things:
            if hasattr(t, "_attached"):
                obs += [att.ob for att in t._attached]
            elif t is not None:
                obs.append(t)
                obs += list(getattr(t, "children_recursive", ()))
        for ob in obs:
            if getattr(ob, "type", None) == "MESH" and "stamp_every_frame" not in ob.data:
                ob.data["stamp_every_frame"] = 1.0
                ob.data.keyframe_insert('["stamp_every_frame"]', frame=1)

    @staticmethod
    def held(player, hand="right", frame=None):
        """The object of the item a Player holds in `hand` on `frame` (default: the current frame), for st.hero
        (cu14: the golden apple itself, not his arm; = engine.players Player.item(hand, frame); Player.hold(...)
        returns the same object when it is made). frame=None: the item he holds last."""
        return player.item(hand, frame)

    @staticmethod
    def under_ceiling(c, frame_start, frame_end, ceiling=F + 3.0, margin=0.01):
        """Keep a character's head under a ceiling from frame_start to frame_end: its root's height keys are clamped
        so that the top of its head meshes stays `margin` under `ceiling` (default the aisle's, F + 3). U.jump_loop
        keys the open-air jump (1.25): under the hall's 3-high ceiling the game stops the hitbox at 1.2 and the
        model's head would still poke 0.12-0.17 into the stone (cu16, measured by the technical check). Returns the
        number of keys clamped."""
        import bpy
        from engine import shots as SH
        scene = bpy.context.scene
        fc = next((f for f in SH.fcurves_of(c.root) if f.data_path == "location" and f.array_index == 2), None)
        if fc is None:
            return 0
        keys = [k for k in fc.keyframe_points if frame_start - 1e-6 <= k.co[0] <= frame_end + 1e-6]
        if not keys:
            return 0
        top = max(keys, key=lambda k: k.co[1])
        cur = scene.frame_current
        scene.frame_set(int(round(top.co[0])))
        head_top = max((ob.matrix_world @ Vector(co)).z for ob in [c.head] + list(c.head.children_recursive)
                       if ob.type == "MESH" for co in ob.bound_box)
        offset = head_top - c.root.matrix_world.translation.z
        scene.frame_set(cur)
        zmax = ceiling - margin - offset
        n = 0
        for k in keys:
            if k.co[1] > zmax:
                k.co[1] = zmax
                n += 1
            k.handle_left[1] = min(k.handle_left[1], zmax)
            k.handle_right[1] = min(k.handle_right[1], zmax)
        fc.update()
        return n

    # ------------------------------------------------------------------ dad's wall (THE WALL PLAN only)
    def wall_is_open(self, frame):
        """Is dad's back wall (the piston door) open on `frame`?"""
        return bool(self.ug.door.is_open(frame))

    def wall_open(self, frame, who="", **kw):
        """Open dad's back wall with the lever flipped on `frame` (engine.underground open_wall: player=steve for
        his flip, repeater=4 for the 12-frame wait, sync="hand", relight=(st, s) in bx24). Only in the shot the wall
        plan names (tu09, bx24). If it is already open it does nothing and returns None (redstone raises on opening an
        open door). Returns open_wall's dict(flip, open, open_end, hand)."""
        if self.wall_is_open(frame):
            print("[twoapples] wall_open(%d) by %s: the wall is already open" % (frame, who or "?"))
            return None
        r = self.ug.open_wall(int(frame), **kw)
        self.wall_log.append((r["open"], "open", who))
        return r

    def wall_shut(self, frame, who="", lever=True):
        """Shut dad's back wall ON `frame` (the pistons push it shut; the lever goes back 2 ticks before). Only in the
        shot the wall plan names (cu15, on its last word). Nothing if it is shut already. Returns the end frame."""
        if not self.wall_is_open(frame):
            print("[twoapples] wall_shut(%d) by %s: the wall is already shut" % (frame, who or "?"))
            return None
        end = self.ug.close_wall(int(frame), lever=lever)
        self.wall_log.append((int(frame), "shut", who))
        return end

    # ------------------------------------------------------------------ looks
    @staticmethod
    def cheat(c, frame, target, cam_pos, max_off=MAX_OFF):
        """The point c looks at instead of `target` so that its nose is never more than `max_off` degrees from the
        lens (The Hello's meadow _cheat): the target itself while it is within that, otherwise the same point turned
        toward the camera (about the eyes)."""
        eye = c.eye_point(frame)
        t = (target[0], target[1], target[2]) if len(target) == 3 else (target[0], target[1], eye.z)

        def bearing(a, b):
            return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))

        to_t, to_cam = bearing(eye, t), bearing(eye, cam_pos)
        off = (to_t - to_cam + 180.0) % 360.0 - 180.0
        if abs(off) <= max_off:
            return t
        b = math.radians(to_cam + math.copysign(max_off, off))
        flat = math.hypot(t[0] - eye.x, t[1] - eye.y)
        return (eye.x + flat * math.sin(b), eye.y + flat * math.cos(b), t[2])

    @staticmethod
    def to_lens(c, frame, target, cam_pos, degrees=21.0):
        """A look target cheated `degrees` toward the camera (films/poppy_day.py _to_lens): a child in profile that
        looks at something beyond itself shows the lens a blank cheek. Returns the point to look_at."""
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
    def lights(self, s, key, at=None, lever=True, **over):
        """The torch levels of LIGHTS[key] for shot s (Stage.lights once per shot). `near` may be an anchor / place
        name; boost= a key of BOOSTS (or extra= your own list: only with tools/palette_check). Under the ground (keys
        "stairs", "hall", "box") the lever is st.use'd (lever=False: a shot that sees through ug_end_pier, where it
        would float). over = Stage.lights arguments to replace."""
        spec = dict(LIGHTS[key], **over)
        boost = spec.pop("boost", None)
        extra = list(spec.pop("extra", ()))
        if boost:
            extra += BOOSTS[boost]
        spec["extra"] = extra
        if isinstance(spec.get("near"), str):
            spec["near"] = self.P(spec["near"])
        if at is not None:
            spec["at"] = at
        self.st.lights(s, **spec)
        if key in UNDER_KEYS and lever:
            self.st.use(s, self.ug.lever)

    def glow(self, s, name, start=None):
        """A film-local light of GLOWS for shot s only (from `start`, a frame inside it, to its end): the set
        builder's recipes (mouth_glow, room_cool, down_fill, counter_bounce, dad_side, slot_strip, doorway_glow).
        Returns the light."""
        pos, watts, color, kind = GLOWS[name]
        return U.bounce(self.st, s, pos, energy=watts, color=color, kind=kind, start=start,
                        name="ta_%s_%s" % (name, s.name))

    def fill(self, name, pos, watts, shots, color=(1.0, 0.98, 0.95), kind="fill"):
        """A film-local light of your own (props.make_light(kind): "fill" shadowless, "torch" a shadowed point) that
        is on in the given shots only and hidden everywhere else (a hidden object is in no frame's stamp). `shots` =
        Shots and / or (first frame, last frame) spans. The NAME starts with your sequence prefix ("cu_apple_rim":
        KeyError otherwise), and one name = one light: calling it again with the same name adds shots, and raises
        ValueError if pos, watts or color differ (two sequences can never share a light by accident)."""
        if name[:2] not in SEQUENCES:
            raise KeyError("fill name %r must start with your sequence prefix: %s" % (name, ", ".join(SEQUENCES)))
        lamp = self._fills.get(name)
        if lamp is not None:
            same = (all(abs(a - b) < 1e-6 for a, b in zip(lamp.location, pos))
                    and abs(lamp.data.energy - watts) < 1e-6
                    and all(abs(a - b) < 1e-6 for a, b in zip(lamp.data.color, color)))
            if not same:
                raise ValueError("fill %r exists with another position, strength or colour: one name = one light"
                                 % name)
        if lamp is None:
            lamp = self._fills[name] = props.make_light(kind, self.v.collection)
            lamp.name = "twoapples_fill_" + name
            lamp.location = pos
            lamp.data.color = color
            lamp.data.energy = watts
            lamp.visible_camera = False
            self.st.key(lamp, "hide_render", 1, True)
        for s in shots:
            a, b = (s.frame_start, s.frame_end) if hasattr(s, "frame_start") else (int(s[0]), int(s[1]))
            self.st.key(lamp, "hide_render", a, False)
            self.st.key(lamp, "hide_render", b + 1, True)
        return lamp

    # ------------------------------------------------------------------ time jumps
    @staticmethod
    def time_jump(frame):
        """End every particle still in the air on `frame` (engine.fx.stop_particles): the film calls it at every
        change of sequence; call it yourself on the first frame of a shot of yours that jumps in time from one with
        particles."""
        return fx.stop_particles(int(frame))

    # ------------------------------------------------------------------ words
    def words(self, s):
        """[(caption, frame)] of the words spoken in shot s (also C.T[s.name].words)."""
        return list(self.T[s.name].words)

    def at(self, s, word, n=0):
        """Frame on which the n-th `word` of shot s appears."""
        return self.T[s.name].at(word, n)
