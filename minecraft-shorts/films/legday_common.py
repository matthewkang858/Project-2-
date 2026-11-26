"""Leg Day: everything the film (films/legday.py) and its five sequence files share.

    films/legday.py          the narration, the skies, the shot plan, the shelf per shot, the re-arm, build()  (lead)
    films/legday_common.py   THIS FILE: the set, the parts, the places, the cameras, the cast, the helpers, the contract
    films/legday_set.py      the set (the set builder's: anvil wall, pens, bench, column, stone row; anchors, paths,
                             one suggested camera per beat LS.CAMERAS["b01"..."b24"] with its proof still)
    films/legday_square.py   sq01 sq02 sq07 sq08 sq09 sq10    the square: squats, stone row, bench, arms, column
    films/legday_pens.py     pn04 pn05 pn06 pn17              the chicken and cow pens
    films/legday_climb.py    cl11 cl12 cl22 cl23              the wall from the road and the stair (gold and dusk)
    films/legday_top.py      tp13 tp14 tp18 tp24              the wall top: the twelfth piston, the dust, the lever
    films/legday_road.py     rd15 rd16 rd19 rd20 rd21         the road and the meadow: patrol, charge, drop, drops

    $BPY -m tools.legday_timeline [--check|--json]   the shot plan: frames, words, skies (no scene); caption proof
    $BPY -m tools.legday_shots render ...           stills of single shots (see its docstring): THE scouting tool
    $BPY -m tools.legday_geo --sky S SHOT:F          where every head lands in the frame, face size, facing, blockers
    $BPY -m tools.legday_palette --sky S F           tools/palette_check on one frame at final quality
    $BPY -m tools.legday_state [--sky S]             THE WORLD STATE checked on a build (crush, drops, planks, the
                                                     twelfth piston and anvils, shelf per shot, dust, lever)
    $BPY -m render legday --still S [--zones]        one frame through render.py (each sky is one build)
    $BPY -m films.legday_set [b19 ...]               the set's self-test and its own proof stills

A sequence file exposes ONE FUNCTION PER SHOT, named like the shot:  def rd19_drop(st, s, C, nar)
    st   films.lookdev.Stage (st.use / st.hero / st.lights / st.key; st.v = the Village)
    s    the engine.shots.Shot (s.frame_start .. s.frame_end inclusive; s.lens / move / focus / handheld)
    C    the LegDay object below: set, parts, places, cameras, cast, helpers; C.T[shot name] = the shot's row of the
         plan (frames, words with their frames, sky, neighbours, shelf state)
    nar  the engine.narration.Narration (nar.at("word", sentence="b19") = the frame the word's caption appears on;
         C.at(s, "word") = the same within shot s)
build() in films/legday.py calls these functions IN TIMELINE ORDER, each exactly once, after every shot exists, and
before each one: C.shelf(s, <the shot's SHELF state>) (the anvils on the shelf) and, before cl22_dusk, C.rearm().
FIVE PEOPLE EDIT AT ONCE: build() imports each sequence file, and calls each shot function, inside a guard. A file
that does not import, or a shot that raises, is printed as "[legday] !!! ..." with its traceback and gets a plain
stand-in (its location's camera, nobody in it); the other files still build. LEGDAY_STRICT=1 in the environment
turns the guard off: hand in only when `LEGDAY_STRICT=1 $BPY -m tools.legday_shots build --sky <each of your skies>`
runs without a "!!!" line. Scout with tools/legday_shots.py / legday_geo.py / legday_palette.py (they write no
meta.json). If you also preview through render.py, use YOUR OWN sample count so no two directors share a preview
directory (out/preview/legday/270x480_<N>spp): PREVIEW_SAMPLES below (square 5, pens 6, climb 7, top 9, road 10).

THE SEQUENCE CONTRACT (what a sequence director may and must do)
  MAY   edit his own file only: the bodies of its shot functions, its docstrings, private helpers and constants.
        Make further twins of the shared cast with his own tags (C.actor("steve", "rd2"), C.patrol("rd19b")). Add
        a film-local light with C.fill("<prefix>_<name>", ...) (the name starts with his prefix; hidden outside the
        shots he names). Move a camera of his own shots freely, unless the row below names a SHARED camera or place.
        Key the set's moving parts (C.row, C.wire, C.lever, C.bench, C.column, C.stones, the anvils' fall) INSIDE
        HIS OWN SHOTS as the plan below gives them to him (THE WORLD STATE).
  MUST  keep every shot function's name and signature;
        give every shot a camera (C.cam: lens + move + focus + handheld; nothing is ever dead still; something
        already moving on its first frame: C.cam moves with ease "ease_out", at speed on frame 1), its cast
        (st.use: everybody else is hidden), what it is about (st.hero, inside x 8-82 %, y 14-60 % of the frame,
        clear of the caption band y 62-72 %) and its torch levels (C.lights once per shot: "gold" or "dusk");
        take characters only through C.actor(role, tag) / C.narrator(tag) / C.patrol(tag) / C.cow(tag) /
        C.hen(tag) with a tag that starts with HIS prefix (sq, pn, cl, tp, rd), dropped items through
        C.item(item_id, tag), stuck arrows through C.stuck_arrow(s, ...) (or hostiles.fire(..., until=
        s.frame_end + 1)): no other sequence can then disturb his keys, and nothing leaks into other shots;
        key each character in frame order; place() everybody on the first frame of a shot before any look_at()
        (look_at(f0, target, ease=0) BEFORE idle(): Character.idle puts a head key on its first frame);
        key nobody before a shot starts unless that instance is NOT in the shot before (pre-roll: use a twin);
        use the shared places and cameras where the plan names them (SHARED below), unchanged;
        keep the players' Minecraft truth: players crouch (sneak), swing, look, jump, sprint, eat / drink; nothing
        that is not a vanilla block, item, mob or particle; dropped items out of a player's pick-up reach (a
        player within about 1 block of a dropped item collects it);
        render what he changed (tools/legday_shots.py at 540x960, 16 samples) and LOOK at it; run
        tools/legday_palette on one frame per shot (tp24 at dusk fails "stone not magenta" at G/R 0.90: known,
        accepted, see films/legday.py SKIES).
  MUST NOT  touch films/legday.py, this file, films/legday_set.py, another sequence file or anything in engine/,
        render.py, tools/ (his own new tools/legday_<seq>_*.py excepted); change the narration, the cuts, a sky or
        the film's length; make anything depend on which sky is being built (no `if sky ...`: every build keys
        the same things); call st.shot / st.sky_change / st.dip / st.finish (the film does); st.use an anvil of
        the shelf (the lead's SHELF does it; the one he SETS in his shot goes through C.appear); key hide_render on
        a character, its items, an anvil or a kit part (st.use / C.appear / part.show do it); key a part outside
        his own shots' frames, except the one pre-roll the plan names (THE WORLD STATE); boost torches beyond
        LIGHTS without tools/palette_check; build a character with players.add_player / illagers.add_patrol /
        animals.add_cow directly (it would escape the twin rule); start a final render (render.py --frames without
        --res / --samples).
  If a shared place or camera is wrong for his shot, he says so in his result; he does not move it.

THE WORLD STATE OF THE ANVIL WALL (one row of twelve sticky pistons, one dust line, one lever, two anvil sets: one
object each for the whole film, so every key on them is placed ONCE, by the one who owns that moment)
  before the film   (this file, LegDay.__init__) everything ARMED (legday_set.make_parts): lever on, dust lit
                    (power 15 by the lever .. 2 at the far end), pistons out with their planks, EXCEPT the twelfth
                    (C.row.pistons[11], the north one beside the lever): retracted before frame 1 and not placed
                    (it is invisible until its place() call), its plank C.row.blocks[11] hidden from frame 1
  tp13_sticky       (top) the narrator places it: C.row.pistons[11].place(f, player=efe); .extend(f) (it fires at
                    once: the dust is lit); he sets its plank: C.row.blocks[11].show(f_set, True)
  tp14_why          (top) Steve sets the twelfth anvil: C.appear(s, C.anvils[11], f_set)
  tp18_lever        (top) the narrator flips the lever OFF: t = C.lever.flip(f) (or redstone.flip_by(efe, C.lever,
                    f, ...)); C.wire.unpower(t) (the whole line dark in one frame). NOT the row (see rd19)
  rd19_drop         (road) the overlapping action of the edit: the row snaps back IN THIS SHOT (the lever was seen
                    in tp18; the row is not in tp18's frame and the lever is not in rd19's): f = C.release_frame()
                    (FIXED: "back" 1169, RELEASE below); C.row.retract(f); drops = fixtures.release(C.anvils, f,
                    world=C.v, chip=list(CHIPPED)); illagers.crush_patrol(...). The anvils land 41 frames after the
                    release: C.land_frame() = 1210 ("fell" 1209)
  rd20 / rd21       (road) the day set lies on the road (the release's keys carry on); the banner and the bottle.
                    NOTE: fixtures.release writes the landed anvils into the World (cells (0, 46..57, 0)), which has
                    no time: after rd19's function has run, C.stand() / v.ground() on the strip x 0..1, y 46..57 gives
                    z 1 (on an anvil) in EVERY shot, and a World-based check sees anvils there before 1210 too. On the
                    strip give z explicitly (0.0: the cobblestone) and treat those cells as empty before the landing
  REARM             (films/legday.py, before cl22_dusk) C.rearm(1373): the row extends at 1372.5 (inside the dip's
                    black frames 1373-1374), the lever on and the dust lit from 1373
  tp24_reloading    (top) Steve sets the twelfth anvil of the dusk set: C.appear(s, C.anvils_dusk[11], f_set); the
                    narrator's free arm lifts to the lever (no flip)
  The anvils on the shelf per shot are the lead's (films/legday.py SHELF, applied by build() through C.shelf).
  The square's parts (C.bench, C.column, C.stones) are the square director's alone (sq02, sq07-sq10). One pre-roll
  is planned: sq02 clicks stone 1 on frame -50 (the game's 180 frames for stone by hand; the stone row is in no
  frame before sq02); stone 2 is only begun in sq02, never broken (its cracks clear on 205, off-screen).

THE CHIPPED ANVILS (frozen: CHIPPED below). The day set chips as it lands in rd19: release(..., chip=list(CHIPPED))
  (the draw "game" with seed 3, frozen as indices: 10 of 12 chip; 3 and 4 stay whole). The dusk set is the SAME
  anvils carried back up: anvils_dusk[i] is built as chipped_anvil for i in CHIPPED. What the climbers carry at dusk
  (planks 0, 1, 2 and the twelfth: all in CHIPPED) is chipped too: C.carry_anvil(p, dusk=True) (stage 1); in the
  morning (cl11, cl12, tp14, sq01) every anvil is whole: C.carry_anvil(p) (stage 0). tools.legday_state checks it.

THE PATROL CLOCK (one timetable for every shot that shows the patrol: rd15, tp18, rd19). C.march_patrol(tag) marches
  a twin of the patrol on the WHOLE road C.v.paths["patrol_road"] (0.5, 84 -> 40, with the meadow's hops) from ONE
  frame, C.patrol_clock()["start"] (about 745), so that the captain's feet are at CAPTAIN_LAND_Y (49.6) when the
  anvils land (C.land_frame(), 1210): the same pillagers at the same place on the same frame in every shot. Where
  the captain is (feet y, from the clock, measured on the build): rd15 903 -> 73.5, 944 -> 70.2; tp18 1103 -> 57.6
  (just short of the shelf's north end, plank 12 is y 57-58), "flipped" 1108 -> 57.4, its followers at 59.4,
  61.4, 63.4, 65.4: past the wall's north end (y 60), on the open road); rd19 1142 -> 55.0, "back" 1169 -> 52.9,
  landing 1210 -> 49.9. Time runs straight through the cuts tp18 -> rd19 (an overlapping action, never compressed):
  the lever goes off on 1108 and the row answers on 1169 in the edit. Do not march a patrol any other way.

SHARED (decided once, used by two shots or two sequences)
  CAMS["climb"]   cl11_climb and cl22_dusk, EXACTLY (position, aim, lens, f-stop, handheld seed): the second is the
                  first at dusk (the story: "the low angle of the first wall shot, now at dusk")
  CAMS["legs"]    cl12_legday and cl23_legday, EXACTLY: "same lens, height and step count" (the story); the step
                  plan is one constant of films/legday_climb.py used by both
  PLACES "lever_narrator" (tp18, tp24: the narrator at the lever), "set_anvil_12th" (tp14, tp24: Steve setting the
                  twelfth anvil), "narrator_edge" (rd21: seen from the road, at the wall top's front edge by the
                  lever), "steve_among_anvils" (rd21), "banner_spot" / "bottle_spot" (rd19's drops: rd20, rd21:
                  the lead's, within the game's toss of the captain's feet; NOT the set's *_spot_target anchors)
  The skies (films/legday.py SKIES), the light recipes LIGHTS, the shelf states SHELF, THE PATROL CLOCK
  (C.march_patrol), the release word RELEASE ("back"), CHIPPED (C.carry_anvil).
  Every other camera is a constant of its sequence file, given whole to C.cam(s, None, **CAM) (the set builder's
  suggestion for each beat is C.cam(s, "set:b05"): a start, measured on stills, never final).

Coordinates: Blender blocks, +X east, +Y north, +Z up; ground 0.0, dirt path -1/16. The wall: stone bricks x -4..-2,
y 27..60, top course z 17 (the walkway z 18), its road face x = -1 looking EAST into the morning sun; the stair up its
south end on the road face (step k at (-1, 27 + k, k), k 0..17); the twelve pistons (-2, 46..57, 17) facing east,
planks out at (0, y, 17), anvils on them at (0, y, 18), landing at (0, y, 0) on the cobblestone strip x -1..1, y
45..57 after a fall of 18 (34 damage, 25.5 to the captain: all five die); dust (-3, 46..59, 18); the lever on its
pier at (-3, 60, 19), the wall top's NORTH end. The pens west of the road (chicken x -23..-17, cow x -14..-7, y
20..26). The square: the well x -3..2, y -3..2; the stone row (5, -16..-9); the bench x -7..-5, y 4..8; the column
(-4, 9). Every anchor, path and suggested camera: films/legday_set.py (its docstring, ANCHORS, CAMERAS).
"""
import math

from mathutils import Vector

from engine import animals, fixtures, fx, hostiles, illagers, mobs, players, redstone
from films import legday_set as LS
from films import lookdev as L

FPS = 24
PATH_Z = -0.0625                       # a dirt path lies one pixel below the grass
FINAL_RES, FINAL_SAMPLES = (540, 960), 16      # this film's final quality (set on the scene by films/legday.py)

SEQUENCES = {"sq": "square", "pn": "pens", "cl": "climb", "tp": "top", "rd": "road"}
PREFIX = {v: k for k, v in SEQUENCES.items()}
PREVIEW_SAMPLES = {"square": 5, "pens": 6, "climb": 7, "top": 9, "road": 10}     # one preview directory each


def build_set(scene):
    """The village of "Leg Day": seed 1 with films/legday_set.py built in (anvil wall, pens, square pieces)."""
    return LS.build_set(scene)


# ----------------------------------------------------------------------------------------------------------------
# places: a name of the set's ANCHORS (films/legday_set.py: C.A[name] is its 3D point, C.Y[name] its facing), or
# (x, y) = on the ground there, (x, y, z) = exactly there. C.P(name) gives either as a 3D point.
# ----------------------------------------------------------------------------------------------------------------
PLACES = {
    # ---- the wall top (top)
    "lever_narrator": "lever_narrator",       # tp18, tp24: the narrator at the lever, east of it (Lever.stand), W
    "set_anvil_12th": "set_anvil_12th",       # tp14, tp24: Steve setting the twelfth anvil on plank 12 (on the dust)
    "place_12th": "place_12th",               # tp13: the narrator setting the twelfth piston (beside its gap)
    # ---- the road (road)
    "narrator_edge": "narrator_edge",         # rd21: at the wall top's front edge by the lever (seen from below;
    #                                           0.7 further back the edge hides him)
    # THE DROPS (the lead's, measured on the build): the captain dies with his feet at (0.5, 49.6) (legday_road
    # CAPTAIN_LAND_Y, inside LAND_WINDOW) and the game tosses a dying mob's drops at most 1.35 blocks
    # (engine.illagers prints a line beyond it): the banner and the bottle land 1.0 block east of his feet, on the
    # cobblestone beside the anvils' cells (x 1), side by side along the road. The set's own anchors
    # banner_spot_target (1.5, 50.7) / bottle_spot_target (1.5, 51.5) were 3.6 and 4.4 blocks from a captain at
    # y 47 (the set builder's march), out of any toss.
    # ONE NAME = ONE POINT: these three are the set's anchors (films/legday_set.py ANCHORS, moved there by the lead
    # after review), so C.P(name), C.A[...] and C.yaw(name) agree.
    "banner_spot": "banner_spot_target",      # (1.45, 49.25) rd19's drops (illagers spots=[bottle, banner]); rd20/21
    "bottle_spot": "bottle_spot_target",      # (1.45, 50.05)
    "steve_among_anvils": "steve_among_anvils",   # (1.45, 46.9) rd21: among the anvils, 2.35 blocks short of the
    #                                           banner (a player collects an item within about one block of his box:
    #                                           never closer than 2)
    "runners_stop": "runners_stop",           # rd16: where the three stop dead (Steve)
}
LAND_WINDOW = LS.march_window()       # (lowest, highest) y of the captain's feet (x 0.5, walking south) on the anvils'
#                                       landing frame for all five to be struck: (45.71, 50.29); the stub uses 49.6
#                                       (the drops then land within the game's toss of his feet: PLACES)
LAND_AFTER = 41                       # frames from fixtures.release(...) to the anvils' landing (fall of 18)
RELEASE = ("rd19_drop", "back")       # the row snaps back and the anvils are released on this word (1169): they
#                                       land on "fell" (1210). FIXED: the patrol clock of three sequences hangs on it
CAPTAIN_LAND_Y = 49.6                 # the captain's feet on the landing frame (the patrol clock aims at it; the
#                                       walk's start from rest puts him at 49.86: inside LAND_WINDOW, the drops within
#                                       the game's 1.35 toss)
PATROL_GAIT = "vanilla"               # illagers.march gait of every patrol twin (wide and long-lens shots)
CHIPPED = (0, 1, 2, 5, 6, 7, 8, 9, 10, 11)    # the anvils that chip as they land in rd19 (fixtures.release chip=
#                                               "game", seed 3, frozen); the dusk set's chipped_anvils

# ----------------------------------------------------------------------------------------------------------------
# cameras: name -> dict(pos, target, lens, fstop[, pos1, target1]); C.cam(s, name) puts one on a shot
# ----------------------------------------------------------------------------------------------------------------
def _set_cam(beat, **over):
    """The set builder's suggested camera for a beat (LS.CAMERAS) as a CAMS entry (without its bookkeeping)."""
    c = {k: v for k, v in LS.CAMERAS[beat].items() if k in ("pos", "target", "pos1", "target1", "lens", "fstop")}
    c.update(over)
    return c


CAMS = {
    # cl11_climb and cl22_dusk (EXACTLY the same; the second is the first at dusk): low on the road south-east of
    # the wall, 28 mm: the lit face, the stair with the four climbers and their anvils, the hanging face lanterns,
    # the shelf's planks against the sky (the anvils on them show only as a sliver from below: the set builder's
    # b11; out/test/legday_set_b11_climb.png / _b22_climb.png). The lead's scouting: see the climb docstring.
    # THE LEAD'S SCOUTING (the open choice of the set builder: b11, climbers big, against b11e from across the road,
    # anvils readable, climbers small): a middle camera (11.0, 28.0, 0.9) -> (-0.5, 40.5, 9.0), 24 mm made the
    # climbers smaller and still hid the anvils behind their planks, with meadow tufts in the lens
    # (out/test/legday_scout_climbvar_cl11_climb_704_v0.png). KEPT b11: the climbers and their anvils carry "they
    # carry twelve anvils up the wall"; the anvils standing ON their planks are shown in tp13 (the wall top).
    "climb": _set_cam("b11"),
    # cl12_legday and cl23_legday (EXACTLY the same): beside the stair's open east edge at knee height, 24 mm: the
    # legs pump up the steps past the lens (out/test/legday_set_b12_legs.png / _b23_legs.png)
    "legs": _set_cam("b12"),
    # stand-ins of a failed shot (films/legday.py STAND_IN), one per place
    "square_wide": _set_cam("b01"),
    "pens_wide": _set_cam("b05"),
    "top_row": _set_cam("b13"),
    "road_shelf": _set_cam("b19"),
}

# torch / lantern levels (C.lights(s, key)); every one looked at on stills. Near the palette limit: do not raise
# them without tools/palette_check (lit stone next to a lantern is at the G/R limit).
LIGHTS = {
    "gold": dict(scale=1.0),                         # daylight: torches and lanterns at their own level
    "dusk": dict(scale=LS.DUSK_LIGHTS),              # 1.4: the look-dev dusk level for every lantern (the set's)
}

# the anvils on the shelf (films/legday.py SHELF names one per shot): (set, plank indices); 0 = south, 11 = north
SHELF = {
    "eight": ("anvils", range(3, 11)),
    "eleven": ("anvils", range(0, 11)),
    "twelve": ("anvils", range(0, 12)),
    "dusk_eight": ("anvils_dusk", range(3, 11)),
    "dusk_eleven": ("anvils_dusk", range(0, 11)),
}

# role -> skin (engine.players; the narrator is Efe on the SLIM model: three-pixel arms)
ROLES = {"steve": "steve", "zuri": "zuri", "ari": "ari", "kai": "kai", "efe": "efe"}
SLIM = {"efe": True}


def yaw_to(src, dst):
    """Yaw that makes a character at src (facing -Y at yaw 0) face dst."""
    return L.yaw_to(src, dst)


def arc_to_y(path, y):
    """Arc length along a polyline (3D points, monotonic in y) from its start to the point where it crosses `y`."""
    total = 0.0
    for a, b in zip(path, path[1:]):
        if b[1] <= y <= a[1] or a[1] <= y <= b[1]:
            if abs(b[1] - a[1]) > 1e-9:
                t = (a[1] - y) / (a[1] - b[1])
                return total + t * math.dist(a, b)
        total += math.dist(a, b)
    raise ValueError("y %.2f is not on the path" % y)


class ShotInfo:
    """One row of the film's shot plan with its frames: C.T[shot name].

    name, beat, beats (every beat it carries: sq02_reps (2, 3)), sequence, sky, sentence (the engine.narration
    Sentence spoken first in the shot), frame_start, frame_end (inclusive), frames, seconds, words = [(caption,
    frame it appears on)], shelf (the SHELF state build() applies), change / sky_after (a sky change inside the
    shot: none in this film), dip = True when the encoder dips to black on the shot's first frame, prev / next =
    the neighbouring shots' names (or None)."""

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


class LegDay:
    """The film's shared context, handed to every shot function as C.

    C.st / C.v / C.A / C.Y   the Stage, the Village, its anchors (3D) and their yaws (films/legday_set.py ANCHORS)
    C.set                    v.sets["legday"]: wall, pens, square, cameras
    C.parts                  films/legday_set.make_parts(v): the moving parts, and as attributes:
      C.row C.wire C.lever   the wall's twelve sticky pistons with planks, its dust, its lever
      C.anvils C.anvils_dusk the two anvil sets (12 each, registered with the Stage; index 0 = south, 11 = north)
      C.stones C.bench C.column   the square's stone row, redstone bench, piston column
    C.nar, C.T               the Narration; the shot plan: C.T["rd19_drop"] -> ShotInfo
    C.P(name)                a place (PLACES or an anchor name) as a 3D point
    C.cam(s, name, ...)      one of CAMS, the set builder's "set:b05", or None + a whole spec
    C.actor(role, tag)       a player of the cast, built once per tag (roles steve zuri ari kai efe)
    C.narrator(tag, torch=True, watts=None)    Efe (slim) holding his glowing redstone torch in the right hand
    C.patrol(tag)            five pillagers [captain, 2..5] (the captain wears the ominous banner)
    C.cow(tag) / C.hen(tag)  a cow / a chicken
    C.item(id, tag)          a dropped item (the iron pickaxe of sq02), registered like a cast member
    C.stuck_arrow(s, ...)    an arrow stuck in a block for shot s only
    C.march_patrol(tag)      a patrol twin marching on THE PATROL CLOCK (rd15, tp18, rd19); C.patrol_clock()
    C.release_frame() / C.land_frame()   1169 / 1210: the row's retraction and the anvils' landing (rd19)
    C.carry_anvil(p, dusk=False)          an anvil in hand: whole in the morning, chipped at dusk (CHIPPED)
    C.shelf(s, state)        (the lead's, from build()) the anvils on the shelf in shot s
    C.appear(s, thing, f)    a registered thing (an anvil) that appears ON frame f inside shot s and stays
    C.rearm(f)               (the lead's, from build()) the row out, the lever on, the dust lit again
    C.shots, C.memo          every Shot of the film by name; a dict for handing things from one shot function to a
                             later one of the SAME sequence (key prefixed with it: C.memo["rd_drops"])
    """

    def __init__(self, st, nar=None, timeline=None):
        self.st, self.v = st, st.v
        self.A, self.Y = st.v.anchors, st.v.yaws
        self.set = st.v.sets["legday"]
        self.nar = nar
        self.T = dict(timeline or {})
        self.shots = {}            # shot name -> engine.shots.Shot (filled by films/legday.py before any shot function)
        self.memo = {}             # what one shot function leaves for a later one of ITS OWN sequence
        self._fills = {}
        self._clock = None
        # the set's moving parts, ARMED (lever on, dust lit from frame 1, pistons out with planks, anvils on them)
        P = self.parts = LS.make_parts(self.v, armed_from=1, dusk_chipped=CHIPPED)
        self.kit, self.row, self.wire, self.lever = P.kit, P.row, P.wire, P.lever
        self.anvils, self.anvils_dusk = P.anvils, P.anvils_dusk
        self.stones, self.bench, self.column = P.stones, P.bench, P.column
        for a in self.anvils + self.anvils_dusk:            # the two sets coincide: each is shown per shot (SHELF)
            st.cast[a.name] = a
        # the twelfth sticky piston (the north one, beside the lever) is not there until the narrator places it in
        # tp13: retracted before the film starts (its move is over before frame 1; not pulling its plank) and not
        # placed (Piston.place in tp13 makes it appear); its plank hidden until he sets it (tp13)
        self.row.pistons[11].retract(-3.0, pull=None)
        self.row.blocks[11].show(1, False)

    # ------------------------------------------------------------------ the world state (the lead's)
    def shelf(self, s, state):
        """The anvils on the shelf in shot s: SHELF[state] (films/legday.py applies its SHELF table before every
        shot function). The day set after rd19's release is on the road: the same objects."""
        which, idx = SHELF[state]
        blocks = getattr(self, which)
        self.st.use(s, *[blocks[i] for i in idx])

    def appear(self, s, thing, frame):
        """A thing registered with the Stage (an anvil of the shelf) that is NOT in shot s's st.use and appears ON
        `frame` inside s, then stays (Stage.finish shows it from the next shot on if that shot uses it, and hides
        it otherwise). For the twelfth anvil that Steve sets (tp14: C.anvils[11]; tp24: C.anvils_dusk[11])."""
        f = int(frame)
        if not s.frame_start <= f <= s.frame_end:
            raise ValueError("appear: frame %d is not inside %s (%d-%d)" % (f, s.name, s.frame_start, s.frame_end))
        if thing.name not in self.st.cast:
            self.st.cast[thing.name] = thing
        thing.show(f, True)
        thing.show(s.frame_end + 1, False)
        return f

    def rearm(self, frame):
        """The trap reloaded between rd21 and cl22 (films/legday.py REARM): the twelve sticky pistons push their
        planks out starting half a frame before `frame` (2.4 frames of travel, inside the dip's black frames),
        the lever is on and the dust lit again (power 15 by the lever) from `frame`."""
        f = int(frame)
        self.row.extend(f - 0.5)
        self.lever.set(f, True)
        self.wire.power(f, source=LS.PIER)
        return f

    # ------------------------------------------------------------------ the patrol clock and the drop (the lead's)
    def release_frame(self):
        """The frame the row snaps back and the day set is released in rd19 (RELEASE: "back", 1169)."""
        return int(self.T[RELEASE[0]].at(RELEASE[1]))

    def land_frame(self):
        """The frame the anvils land on the road (release + LAND_AFTER: 1210, "fell")."""
        return self.release_frame() + LAND_AFTER

    def patrol_clock(self):
        """THE PATROL CLOCK: dict(road = the whole patrol_road, start = the one frame every patrol twin starts
        marching on, land = the landing frame). The captain's feet are at CAPTAIN_LAND_Y on the landing frame."""
        if self._clock is None:
            road = [tuple(p) for p in self.v.paths["patrol_road"]]
            land = self.land_frame()
            start = land - int(round(arc_to_y(road, CAPTAIN_LAND_Y) / illagers.PATROL_SPEED * FPS))
            self._clock = dict(road=road, start=start, land=land)
        return self._clock

    def march_patrol(self, tag):
        """A twin of the patrol (C.patrol(tag): [captain, 2..5]) marching on THE PATROL CLOCK: the whole road from
        patrol_clock()["start"], in a clean file 2.0 apart, gait PATROL_GAIT. Every shot that shows the patrol
        (rd15, tp18, rd19) takes its own twin this way, so they are at the same place on the same frame. Returns
        the patrol (st.use(s, *pat) is yours)."""
        pat = self.patrol(tag)
        clk = self.patrol_clock()
        illagers.march(pat, clk["road"], clk["start"], gait=PATROL_GAIT)
        return pat

    def carry_anvil(self, p, dusk=False, index=None, frame=None):
        """An anvil in p's right hand (fixtures.hold_anvil): in the morning whole (stage 0); at dusk (dusk=True) the
        SAME anvils carried back up after the fall: chipped (stage 1) when `index` (the plank it goes to) is in
        CHIPPED, and index None = one of the four carried at dusk (planks 0, 1, 2, 11: all chipped)."""
        chipped = dusk and (index is None or int(index) in CHIPPED)
        return fixtures.hold_anvil(p, stage=1 if chipped else 0, frame=frame)

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
        """A named place (PLACES, or any anchor of the set) as a 3D point (2D entries are put on the ground)."""
        p = PLACES.get(name, name)
        if isinstance(p, str):
            return tuple(self.A[p])
        return self.stand(p)

    def yaw(self, name, default=0.0):
        """The facing the set gives an anchor (C.Y), or `default`."""
        p = PLACES.get(name, name)
        return self.Y.get(p, default) if isinstance(p, str) else default

    def camera_spec(self, name):
        """CAMS[name], the set builder's suggestion "set:b05" (LS.CAMERAS), or {} for None (a shot's own camera,
        given whole to C.cam as keywords)."""
        if name is None:
            return {}
        if name.startswith("set:"):
            return _set_cam(name[4:])
        return dict(CAMS[name])

    def cam(self, s, name, focus=None, handheld=0.006, seed=None, move=True, ease="ease_out", **over):
        """Put a camera on shot s: lens, position / aim (with its move when it has one and move=True), focus
        (default: its target) and a gentle handheld. name = one of CAMS (a shared camera), "set:bNN", or None: the
        shot's OWN camera, a constant of its sequence file given whole as keywords (pos, target, lens[, fstop,
        pos1, target1]: C.cam(s, None, focus=steve.head, **SQ01_CAM)). over = entries to replace or give. ease: of
        the move; default 'ease_out' = AT SPEED ON THE FIRST FRAME, slowing to the last (engine.shots' own default
        'smooth' starts from rest: a still for the first half second). 'linear' for a constant drift / track.
        The handheld seed is the shot name's (a SHARED camera in two shots: pass the same seed= in both, e.g.
        seed=CLIMB_SEED, for an exact repeat). Returns the spec used."""
        c = dict(self.camera_spec(name), **over)
        if "pos" not in c or "target" not in c or "lens" not in c:
            raise KeyError("camera %r for %s needs pos, target and lens" % (name, s.name))
        s.lens(c["lens"], c.get("fstop", 2.8))
        if move and "pos1" in c:
            s.move(c["pos"], c["target"], c["pos1"], c.get("target1", c["target"]), ease=ease)
        else:
            s.move(c["pos"], c["target"])
        s.focus(focus if focus is not None else c["target"])
        if handheld:
            s.handheld(handheld, seed=sum(ord(ch) for ch in s.name) % 89 if seed is None else seed)
        return c

    # ------------------------------------------------------------------ the cast
    @staticmethod
    def _check_tag(tag):
        if tag[:2] not in SEQUENCES:
            raise KeyError("tag %r must start with a sequence prefix: %s" % (tag, ", ".join(SEQUENCES)))

    def actor(self, role, tag):
        """The player "<role>_<tag>", built on first use and registered with the Stage (st.cast).

        role   steve / zuri / ari / kai   the gym town (engine.players, wide arms: four pixels)
               efe                         the narrator: Efe on the SLIM model (three-pixel arms), empty-handed
                                           (C.narrator gives him his redstone torch)
        tag    starts with your sequence prefix (sq, pn, cl, tp, rd); a further twin is just another tag:
               C.actor("steve", "sq"), C.actor("steve", "sq2").
        Twins exist because a character that is in two consecutive shots cannot be keyed before the second one
        starts: whoever must already be moving on the first frame of a shot (pre-rolled) is a twin that is not in
        the shot before. Held items: p.hold("cooked_chicken" | "milk_bucket" | "bucket" ...), fixtures.hold_anvil(p),
        animals.milk(p, frame, f0, f1) (the empty bucket filled with one swing)."""
        if role not in ROLES:
            raise KeyError("no role %r (roles: %s)" % (role, ", ".join(ROLES)))
        self._check_tag(tag)
        name = "%s_%s" % (role, tag)
        c = self.st.cast.get(name)
        if c is None:
            c = players.add_player(self.st, name, ROLES[role], slim=SLIM.get(role, False))
        return c

    def narrator(self, tag, torch=True, watts=None, hand="right"):
        """The narrator (C.actor("efe", tag)) with his glowing redstone torch in the RIGHT hand (redstone.hold_torch:
        a small point light at its head, on while the item is shown; watts default HELD_TORCH_WATTS 30, at dusk as
        the key on his face LS.B24_TORCH_WATTS 120). hand="left": in the left hand (tp24: the torch on the camera's
        side, the right arm free for the lever). torch=False: empty-handed (a twin of his own: once a tag has the
        torch it keeps it)."""
        p = self.actor("efe", tag)
        if torch and getattr(p, "_legday_torch", None) is None:
            p._legday_torch = redstone.hold_torch(p, hand, watts=watts or redstone.HELD_TORCH_WATTS)
        return p

    def patrol(self, tag, count=5):
        """Five pillagers "patrol_<tag>_1..5" (engine.illagers add_patrol): [captain (ominous banner on his head),
        2..5], crossbows held. illagers.march(pat, path, frame, gait="vanilla") for wide / long-lens shots; st.use(s,
        *pat). Built once per tag."""
        self._check_tag(tag)
        prefix = "patrol_%s" % tag
        first = self.st.cast.get(prefix + "_1")
        if first is not None:
            return [self.st.cast["%s_%d" % (prefix, i + 1)] for i in range(count)]
        return illagers.add_patrol(self.st, count, prefix=prefix)

    def cow(self, tag):
        """A cow "cow_<tag>" (engine.animals), registered with the Stage."""
        self._check_tag(tag)
        return animals.add_cow(self.st, "cow_%s" % tag)

    def hen(self, tag):
        """A chicken "hen_<tag>" (engine.animals), registered with the Stage."""
        self._check_tag(tag)
        return animals.add_chicken(self.st, "hen_%s" % tag)

    def item(self, item_id, tag):
        """A dropped item of engine.mobs ("iron_pickaxe"), registered with the Stage like a cast member:
        pick = C.item("iron_pickaxe", "sq"); pick.place(f0, pos); pick.animate(f0, s.frame_end + 1); st.use(s, pick).
        (The ominous banner and bottle come from illagers: crush_patrol's drops, or add_dropped_banner / _bottle.)"""
        self._check_tag(tag)
        name = "%s_%s" % (item_id, tag)
        it = self.st.cast.get(name)
        if it is None:
            it = self.st.cast[name] = mobs.make_dropped_item(item_id, name=name)
        return it

    def stuck_arrow(self, s, point, direction, frame=None, shake=None, scale=1.0):
        """An arrow stuck in a block (engine.hostiles.stick) for shot s ONLY: from `frame` (default: the shot's first
        frame, already stuck: no shake) to the shot's end. direction = the way it flew (the shaft points back
        along it). An arrow arriving in the shot: frame inside it (it shakes for 7 ticks). scale=1.25 in wides."""
        f = s.frame_start if frame is None else int(frame)
        if shake is None:
            shake = f > s.frame_start
        return hostiles.stick(point, direction, f, until=s.frame_end + 1, shake=shake, scale=scale)

    def put(self, c, frame, place, toward=None, yaw=None):
        """place() a character on a named place (or a point), facing `toward` (a place name or a point), `yaw`, or
        the set's facing of that anchor. Returns the 3D point."""
        pos = self.P(place) if isinstance(place, str) else self.stand(place)
        if yaw is None and toward is not None:
            aim = self.P(toward) if isinstance(toward, str) else toward
            yaw = L.yaw_to(pos, aim)
        if yaw is None:
            yaw = self.yaw(place) if isinstance(place, str) else 0.0
        c.place(frame, pos, yaw)
        return pos

    @staticmethod
    def to_lens(c, frame, target, cam_pos, degrees=21.0):
        """A look target cheated `degrees` toward the camera: a head in profile that looks at something beyond
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
        """The torch levels of LIGHTS[key] ("gold" or "dusk") for shot s (Stage.lights once per shot). near / radius
        leave far torches out of the render (a place name or a point); over = Stage.lights arguments to replace
        (extra=[(point, k)] boosts the lantern nearest the point: only with tools/palette_check)."""
        kw = dict(LIGHTS[key], **over)
        if near is not None:
            kw.update(near=self.P(near) if isinstance(near, str) else near, radius=radius or 20.0)
        if at is not None:
            kw["at"] = at
        self.st.lights(s, **kw)

    def fill(self, name, pos, watts, shots, color=(1.0, 0.98, 0.95)):
        """A film-local shadowless fill light (props.make_light("fill")) that is on in the given shots only and
        hidden everywhere else (a hidden object is in no frame's stamp). `shots` = Shots and / or (first frame,
        last frame) spans. The NAME starts with your sequence prefix ("tp_face": KeyError otherwise), and one name
        = one light: calling it again with the same name adds shots, and raises ValueError if pos, watts or color
        differ (two sequences can never share a light by accident)."""
        from engine import props
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
            lamp = self._fills[name] = props.make_light("fill", self.v.collection)
            lamp.name = "legday_fill_" + name
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

    # ------------------------------------------------------------------ time jumps
    @staticmethod
    def time_jump(frame):
        """End every particle still in the air on `frame` (engine.fx.stop_particles): the film calls it at every
        change of sequence. Inside a sequence a shot that jumps in time calls it itself BEFORE emitting its own
        (rd19 -> rd20 do NOT: "the smoke thins")."""
        return fx.stop_particles(int(frame))

    # ------------------------------------------------------------------ words
    def words(self, s):
        """[(caption, frame)] of the words spoken in shot s (also C.T[s.name].words)."""
        return list(self.T[s.name].words)

    def at(self, s, word, n=0):
        """Frame on which the n-th `word` of shot s appears."""
        return self.T[s.name].at(word, n)


# re-exported for the sequence files (one import line): from films.legday_common import LS, fixtures, ...
__all__ = ["LS", "fixtures", "illagers", "animals", "hostiles", "redstone", "players", "mobs", "LegDay", "CAMS",
           "PLACES", "LIGHTS", "SHELF", "CHIPPED", "RELEASE", "CAPTAIN_LAND_Y", "yaw_to", "arc_to_y"]
