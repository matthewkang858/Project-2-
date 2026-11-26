"""Twenty Minutes: everything the film (films/twentyminutes.py) and its five sequence files share.

    films/twentyminutes.py          the narration, the sky, the shot plan, the second bed, build()   (lead director)
    films/twentyminutes_common.py   THIS FILE: the set, the parts, the places, the cameras, the cast, the helpers,
                                    the contract
    films/twentyminutes_set.py      the set (the set builder's: engine/towers.py's iron farm in the village, the
                                    film's anchors tm_*, one scouted camera per beat TS.CAMERAS["b01"..."b24p"] with
                                    its still out/test/twentyminutes_set_<key>_<what>.png, stage_bNN = a worked
                                    staging of every beat)
    films/twentyminutes_square.py   sq01 sq02 sq03 sq04_tilt sq04_hat sq05   the square and the foot of the tower
    films/twentyminutes_cell.py     ce06 ce07 ce08 ce23                      the pod: the bed, the zombie, the fear
    films/twentyminutes_golem.py    gm09 gm10 gm11 gm12 gm24                 the platform, the slot, the hopper
    films/twentyminutes_gap.py      gp13 gp14 gp15 gp20 gp22                 the staircase and the gap
    films/twentyminutes_grow.py     gr16 gr17 gr18 gr19 gr21                 Mom and the baby: growing up, the count

    $BPY -m tools.twentyminutes_timeline [--check|--json]   the shot plan: frames, words (no scene); caption proof
    $BPY -m tools.twentyminutes_shots render ...            stills of single shots (its docstring): THE scouting tool
    $BPY -m tools.twentyminutes_geo SHOT:F                  where every head lands in the frame, face size, facing,
                                                            what blocks it (a baby's face is measured at its own width)
    $BPY -m tools.twentyminutes_palette F                   tools/palette_check on one frame at final quality
    $BPY -m render twentyminutes --still S [--zones]        one frame through render.py
    $BPY -m films.twentyminutes_set [bNN ...]               the set's self-test and its own proof stills

A sequence file exposes ONE FUNCTION PER SHOT, named like the shot:  def gm11_lava(st, s, C, nar)
    st   films.lookdev.Stage (st.use / st.hero / st.lights / st.see_through / st.key; st.v = the Village)
    s    the engine.shots.Shot (s.frame_start .. s.frame_end inclusive; s.lens / move / focus / handheld)
    C    the TwentyMinutes object below: set, parts, places, cameras, cast, helpers; C.T[shot name] = the shot's row
         of the plan (frames, words with their frames, sky, neighbours)
    nar  the engine.narration.Narration (nar.at("word", sentence="b19") = the frame the word's caption appears on;
         C.at(s, "word") = the same within shot s)
build() in films/twentyminutes.py calls these functions IN TIMELINE ORDER, each exactly once, after every shot exists.
FIVE PEOPLE EDIT AT ONCE: build() imports each sequence file, and calls each shot function, inside a guard. A file that
does not import, or a shot that raises, is printed as "[twentyminutes] !!! ..." with its traceback and gets a plain
stand-in (its location's camera, nobody in it); the other files still build. TWENTYMINUTES_STRICT=1 in the
environment turns the guard off: hand in only when `TWENTYMINUTES_STRICT=1 $BPY -m tools.twentyminutes_shots build`
runs without a "!!!" line. Scout with tools/twentyminutes_shots.py / _geo.py / _palette.py (they write no meta.json).
If you also preview through render.py, use YOUR OWN sample count so no two directors share a preview directory
(out/preview/twentyminutes/270x480_<N>spp): PREVIEW_SAMPLES below (square 5, cell 6, golem 7, gap 9, grow 10; the
lead's whole-film previews 8).

THE SEQUENCE CONTRACT (what a sequence director may and must do)
  MAY   edit his own file only: the bodies of its shot functions, its docstrings, private helpers and constants.
        Make further twins of the shared cast with his own tags (C.actor("baby", "gp2")). Add a film-local light with
        C.fill("<prefix>_<name>", ...) (the name starts with his prefix; hidden outside the shots he names). Move a
        camera of his own shots freely, unless the shot's docstring names a SHARED camera or place for it.
  MUST  keep every shot function's name and signature;
        give every shot a camera (C.cam: lens + move + focus + handheld; nothing is ever dead still; something
        already moving on its first frame: C.cam moves with ease "ease_out", at speed on frame 1), its cast (st.use:
        everybody else is hidden), what it is about (st.hero, inside x 8-82 %, y 14-60 % of the frame, clear of the
        caption band y 62-72 %) and its torch levels (C.lights once per shot: "square" on the plaza, "tower"
        everywhere else);
        take characters only through C.actor(role, tag) with a tag that starts with HIS prefix (sq, ce, gm, gp, gr),
        dropped items through C.item(item_id, tag, ...); the golem only through C.golem() (golem sequence only: ONE
        golem for every spawn, engine/towers.py); no other sequence can then disturb his keys;
        key each character in frame order; place() everybody on the first frame of a shot before any look_at()
        (look_at(f0, target, ease=0) BEFORE idle(): Character.idle puts a head key on its first frame);
        key nobody before a shot starts unless that instance is NOT in the shot before (pre-roll: use a twin);
        use the shared places and cameras where the shot's docstring names them (SHARED below), unchanged;
        keep MOM'S HEAD ON THE ZOMBIE (C.zombie_eye) in every shot from the moment she is in the pod (sq04_hat on):
        "Mom never looks at me, only at the zombie" is only true if no frame shows her looking elsewhere; in sq03
        (on the plaza, before the pod) she may look where the push takes her;
        keep the Minecraft truth: villagers keep their arms crossed, have no fingers and no facial animation; a baby
        hops (towers.hop), runs, bounces on a bed (fm.bounce); players walk, sneak, swing, look; the golem spawns in
        one frame with no effect, steps, slides in the water, drops; nothing that is not a vanilla block, item, mob
        or particle;
        render what he changed (tools/twentyminutes_shots.py at 540x960, 16 samples) and LOOK at it; run
        tools/twentyminutes_palette on one frame per shot.
  MUST NOT  touch films/twentyminutes.py, this file, films/twentyminutes_set.py, another sequence file or anything in
        engine/, render.py, tools/ (his own new tools/twentyminutes_<seq>_*.py excepted); change the narration, the
        cuts, the sky or the film's length; make anything depend on which sky is being built; call st.shot /
        st.sky_change / st.dip / st.finish (the film does); key hide_render on a character, its items, the golem or
        a part (st.use, undead.vanish / appear and the farm's calls do it); register P.top_step with the Stage (it is
        there until gp22 breaks it, and gone after: the film's order); st.use P.bed2 or call P.bed2.place_at directly
        (the film shows it from gr21 on: C.bed2_at in gr21 only); boost torches beyond LIGHTS without
        tools/palette_check; build a character with st.actor / players.make_player / undead.add_zombie /
        mobs.make_iron_golem directly (it would escape the twin rule); start a final render (render.py --frames
        without --res / --samples).
  If a shared place or camera is wrong for his shot, he says so in his result; he does not move it.

SHARED (decided once, used by two shots or two sequences: ONE definition each, below)
  CAMS["plaza"]     beat 1 (sq01) and the END of beat 4's tilt (sq04_tilt ends exactly on it): the set's b01
  CAMS["tilt"]      sq04_tilt: from the well (towers' square_start) to CAMS["plaza"] (built from it: cannot diverge)
  CAMS["window"]    beat 23 (ce23) and, as CAMS["window_08"] (the same position, lens and stop, aimed 0.35 further
                    north: the set's b08w), beat 8 (ce08): the lens in the pod's east column 0.13 from the zombie's
                    right arm ("This camera position returns for the last two lines"); keep the zombie's arms FORWARD
                    (C.zombie(..., aggro=False)) in both: raised, they leave the frame
  CAMS["platform"]  beats 9, 10 and 24 (gm09, gm10 = the jump cut on an identical framing, gm24 = the story's own
                    fallback for the last line: "cut on that word to the low-angle platform framing of line 9")
  CAMS["grow"]      beats 17 and 19 (gr17, gr19: the locked framing, Mom as the height ruler), exactly
  PLACES["baby_square"]  the baby on the plaza: sq01, sq02, sq04_tilt (tm_baby_square)
  THREE             Mom, the cleric and the librarian backed against the far glass: ce08, gm09, gm10 (they tremble
                    behind the glass while the golem comes)
  FOUR              the four of the last lines: ce23 and gm24 (the narrator and Mom side by side, the librarian
                    between and behind them, the cleric on back_2)
  PANIC_SEED        Mom's and the narrator's tremble, matched frame for frame (ce23, and gm24 behind the glass)
  the second bed    P.bed2 is in every shot from gr21_count on (films/twentyminutes.py BED2_FROM), never before;
                    it appears ON the frame gr21 gives C.bed2_at(frame)
  the top step      P.top_step stands until gp22_step breaks it (fm.break_top_step); never registered with the Stage
  the sky           films/twentyminutes.py SKIES (one sky: "gold") and the light recipes LIGHTS below

Coordinates: Blender blocks, +X east, +Y north, +Z up; the plaza's ground 0.0 (a dirt path -1/16); the pod's floor top
z 10. The tower (engine/towers.py LAYOUT; films/twentyminutes_set.py WHERE EVERY BEAT IS FILMED): the pod inside
x -23..-19, y 18..22, z 10..11 (glass ring x -24..-18, y 17..23, glass roof z 12); the zombie's cell (-18, 19) in the
east wall (sill (-19, 19, 10), the zombie at (-17.7, 19.5), eyes C.zombie_eye z 11.74); the lantern (-23, 18, 10); the
cell's wall torch (-19, 18, 10); beds (pillows north) white (-23, 21), white (-22, 21), Mom's red (-21, 21), the second
red bed (-20, 21..22) from gr21; the gap (-19, 23, 10) under the cobblestone plug (-19, 23, 11); the platform x -28..-25,
y 17..23 (stone z 9, water sheet z 10) with the kill slot x -30..-29 west of it (lava 1.1 under the rim); the hopper
(-29, 23, 1) on the chest (-29, 23, 0); ten dirt steps up the back from (-17, 23, 0) to the top step (-19, 24, 9).
"""
import math

from mathutils import Vector

from engine import characters, fixtures, fx, mobs, players, props, towers, undead
from films import lookdev as L
from films import twentyminutes_set as TS

FPS = 24
PATH_Z = -0.0625                       # a dirt path lies one pixel below the grass
FINAL_RES, FINAL_SAMPLES = (540, 960), 16      # this film's final quality (set on the scene by films/twentyminutes.py)

SEQUENCES = {"sq": "square", "ce": "cell", "gm": "golem", "gp": "gap", "gr": "grow"}
PREFIX = {v: k for k, v in SEQUENCES.items()}
PREVIEW_SAMPLES = {"square": 5, "cell": 6, "golem": 7, "gap": 9, "grow": 10}     # one preview directory each (lead: 8)
X, Y, F = TS.X, TS.Y, TS.F             # (-23, 18, 10): the pod's south-west inside cell and its floor top


def build_set(scene):
    """The village of "Twenty Minutes": seed 1 with engine/towers.py's iron farm built in (films/twentyminutes_set.py).
    Returns the Village."""
    return TS.build_set(scene)


# ----------------------------------------------------------------------------------------------------------------
# places: a name of PLACES, a towers anchor by its short name ("mom", "back_1", "golem_spawn": C.fm.A), or a village
# anchor ("tm_baby_square"); C.P(name) gives the 3D point (2D entries on the ground), C.yaw(name) its facing
# ----------------------------------------------------------------------------------------------------------------
PLACES = {
    # ---- the square (beats 1-4)
    "baby_square": TS.BABY_SQUARE,        # (6.38, 1.16): the baby on the plaza path east of the well, facing NNE
    #                                       (tm_baby_square = towers' square_baby): sq01, sq02, sq04_tilt
    # ---- the pod: the film's own spots (towers' are by short name: mom, mom_glass, baby_glass, bed_side,
    #      bed_beside, back_1..3, row_1..4, gap_in, gap_adult, gap_side, watch_22, top_step, one_down ...)
    "narrator_23": (X + 2.45, Y + 1.7, float(F)),     # (-20.55, 19.7)  FOUR: the narrator ...
    "mom_23": (X + 2.45, Y + 0.7, float(F)),          # (-20.55, 18.7)  ... and Mom side by side, 1.0 apart
    "librarian_23": (X + 1.2, Y + 0.75, float(F)),    # (-21.8, 18.75)  the librarian between and behind them
    "watch_22_out": (X + 2.4, Y + 2.45, float(F)),    # (-20.6, 20.45)  the narrator in gp22 (seen from outside)
}
# THREE: ce08 (CAMS "window"), gm09 and gm10 (CAMS "platform", small behind the west glass). (role, place)
THREE = (("cleric", "back_1"), ("librarian", "back_2"), ("mom", "back_3"))
# FOUR: ce23 (CAMS "window") and gm24 (CAMS "platform"): the four of the last lines, where they stood in b23w.
FOUR = (("cleric", "back_2"), ("librarian", "librarian_23"), ("mom", "mom_23"), ("narrator", "narrator_23"))
PANIC_SEED = 7                         # Mom's and the narrator's tremble (towers.panic): the same seed = the same
#                                        tremble frame for frame ("same height, same pose": beat 23)
PANIC_SEEDS = {"cleric": 61, "librarian": 23, "mom": PANIC_SEED, "narrator": PANIC_SEED}

# ----------------------------------------------------------------------------------------------------------------
# cameras: name -> dict(pos, target, lens, fstop[, pos1, target1, ease]); C.cam(s, name) puts one on a shot.
# "set:<key>" = the set builder's scouted camera TS.CAMERAS[key] (b01 ... b24p, b08w, b22o, b23w, b24w); None = the
# shot's OWN camera, a constant of its sequence file given whole as keywords.
# ----------------------------------------------------------------------------------------------------------------
def _cam(key, **over):
    c = {k: v for k, v in TS.CAMERAS[key].items() if k in ("pos", "target", "lens", "fstop", "pos1", "target1", "ease")}
    c.update(over)
    return c


CAMS = {
    # beat 1 (sq01) and the end of beat 4's tilt: low on the plaza path east of the well (9.3, -0.6, 0.75), 40 mm
    # f/2.8, looking north-west over the well at the tower above the roofs, house_c's door at the left
    # (out/test/twentyminutes_set_b01_afraid.png, _afraid_door.png)
    "plaza": _cam("b01"),
    # beat 9 / 10 / 24: over the slot's south end at the platform's level, 16 mm f/4: the golem big against the low sun
    # and its gold halo, the pod's west glass with the villagers small behind it (twentyminutes_set_b09_golem.png)
    "platform": _cam("b09"),
    # beats 8 and 23: in the pod's east column just north of the cell's window, 18 mm f/2.8, 0.13 from the zombie's
    # right arm (a dark green blur down the left edge), looking west-south-west across the pod at the far glass
    # (twentyminutes_set_b23w_window.png; b08w was the same position aimed 0.35 further north)
    "window": _cam("b23w"),
    # beats 17 and 19: the locked side view against the front glass, 20 mm f/4 (twentyminutes_set_b17_twenty.png,
    # _b19_ended.png): Mom in profile at the front glass, the baby / the grown narrator 0.9 west of her
    "grow": _cam("b17"),
    # beat 4's second shot: 200 mm f/2.8 from the plaza at the straw hat behind the front glass (C.panes hides the
    # panes on the lines to her head and face) (twentyminutes_set_b04_long_hat.png)
    "hat": _cam("b04_long"),
}
# beat 8: the SAME lens position, lens and stop as CAMS "window" (built from it: cannot diverge), aimed 0.35 further
# north (the set's b08w): with b23w's aim the three of THREE land at x 32 / 58 / 79 % and the librarian's head reaches
# x 84.5 % (into the icon column; tools.twentyminutes_geo ce08_scared:480); with this aim 20 / 46 / 66 % (the set's
# still twentyminutes_set_b08w_window.png). The story's "This camera position returns for the last two lines": the
# position does; a 4-degree pan between two shots 38 s apart is not seen.
CAMS["window_08"] = dict(CAMS["window"], target=TS.CAMERAS["b08w"]["target"])
# beat 4's tilt: from the well's east side (towers' square_start target) up to the plaza framing EXACTLY
CAMS["tilt"] = dict(CAMS["plaza"], target=TS.CAMERAS["b04"]["target"], pos1=CAMS["plaza"]["pos"],
                    target1=CAMS["plaza"]["target"])
# the stand-ins of a failed shot (films/twentyminutes.py STAND_IN): its location's camera, nobody in it
STAND_IN = {"square": "plaza", "cell": "window", "golem": "platform", "gap": "set:b14", "grow": "grow"}

# ----------------------------------------------------------------------------------------------------------------
# light: C.lights(s, key). Every shot: the pod's lantern and the cell's wall torch at 1.0 (POD_LIGHTS), as in every
# scouting still of the set. "tower" leaves out the village's torches more than 22 blocks from the tower (they light
# nothing a tower shot sees, and cost render time); "square" keeps every torch (the plaza's lamps are in frame).
# Lit stone next to a lantern sits on tools/palette_check's limit: do not raise them.
# ----------------------------------------------------------------------------------------------------------------
POD_LIGHTS = dict(TS.POD_LIGHTS)
TOWER_CENTRE = (-21.0, 20.5, 5.0)
LIGHTS = {
    "square": dict(scale=1.0, groups=POD_LIGHTS),
    "tower": dict(scale=1.0, groups=POD_LIGHTS, near=TOWER_CENTRE, radius=22.0),
}

# role -> how TwentyMinutes.actor builds it
ROLES = ("baby", "narrator", "mom", "cleric", "librarian", "armorer", "shepherd", "steve", "zombie")
MAX_OFF = 65.0         # a villager watching something beyond itself: its nose at most this far from the lens
#                        (The Hello's meadow: at 100-118 degrees a brown box; 78 a 2 px nose; 65 nose and both eyes)


def yaw_to(src, dst):
    """Yaw that makes a character at src (facing -Y at yaw 0) face dst."""
    return L.yaw_to(src, dst)


class ShotInfo:
    """One row of the film's shot plan with its frames: C.T[shot name].

    name, beat, beats (the beats it carries: ce23 carries 23 and the start of 24), sequence, sky, sentence (the
    engine.narration Sentence its cut belongs to), frame_start, frame_end (inclusive), frames, seconds, words =
    [(caption, frame it appears on)], change / sky_after (a sky change inside the shot: none in this film), dip, prev /
    next = the neighbouring shots' names (or None)."""

    def __init__(self, **kw):
        self.change, self.sky_after, self.dip, self.prev, self.next = None, None, False, None, None
        self.beats = ()
        self.__dict__.update(kw)

    def at(self, word, n=0):
        """Frame on which the n-th `word` spoken in this shot appears (case-insensitive caption text)."""
        hits = [f for w, f in self.words if w.lower().strip(".,") == word.lower()]
        return hits[n]

    def __repr__(self):
        return "<%s beat %d %s %s %d-%d>" % (self.name, self.beat, self.sequence, self.sky, self.frame_start,
                                            self.frame_end)


class TwentyMinutes:
    """The film's shared context, handed to every shot function as C.

    C.st / C.v / C.A      the Stage, the Village, the farm's anchors by short name (C.A["mom"], C.A["golem_spawn"])
    C.fm, C.P_            the towers.Farm (every call of the farm at work: zombie_in_cell, golem_spawn / step / slide /
                          death, deliver, strew, break_top_step, climb, bounce, see_through) and the parts
                          (TS.make_parts: farm, pod, bed2, hopper, chest, water, lava, top_step, door)
    C.nar, C.T            the Narration; the shot plan: C.T["gm11_lava"] -> ShotInfo
    C.P(name), C.yaw(name)    a place as a 3D point / its facing (PLACES, towers' short names, village anchors)
    C.cam(s, name, ...)   one of CAMS, "set:<key>", or None with the shot's own values
    C.actor(role, tag)    a cast member, built once per tag: roles in ROLES, tag starts with the sequence prefix
    C.golem()             THE golem (one for every spawn; golem sequence only)
    C.item(id, tag, ...)  a dropped item (iron ingots, poppies), registered like a cast member
    C.zombie(s, tag, ...) the zombie in its cell for shot s (towers zombie_in_cell), in the shot
    C.pod(s, tag, who)    villagers on their places in the pod, heads on the zombie (trembling with panic=True)
    C.zombie_eye          the look target of every villager in the pod (Mom's head is ALWAYS on it)
    C.shots, C.memo       every Shot of the film by name; a dict for handing things from one shot function to a later
                          one of the SAME sequence (key prefixed with it: C.memo["gm_slide"])
    """

    def __init__(self, st, nar=None, timeline=None):
        self.st, self.v = st, st.v
        self.P_ = TS.make_parts(st.v)
        self.fm = self.P_.farm
        self.A = self.fm.A
        self.nar = nar
        self.T = dict(timeline or {})
        self.shots = {}            # shot name -> engine.shots.Shot (filled by films/twentyminutes.py first)
        self.memo = {}             # what one shot function leaves for a later one of ITS OWN sequence
        self._fills = {}
        self.bed2_frame = None     # the frame the second bed appears on (C.bed2_at, in gr21)
        # the second bed is shown by the film from gr21 on (films/twentyminutes.py BED2_FROM): registered here, so it
        # is hidden in every shot that does not use it (fixtures.bed without frame= would be in every shot)
        st.cast[self.P_.bed2.name] = self.P_.bed2

    # ------------------------------------------------------------------ places and cameras
    @property
    def zombie_eye(self):
        """The zombie's eye point in its cell: where every villager in the pod looks."""
        return self.fm.zombie_eye

    def stand(self, p):
        """(x, y) -> the point a character stands on there: ground height, a pixel lower on a dirt path. A 3D point
        is returned as it is."""
        if len(p) == 3:
            return (float(p[0]), float(p[1]), float(p[2]))
        x, y = float(p[0]), float(p[1])
        z = self.v.ground(x, y)
        top = self.v.world.block_id(int(math.floor(x)), int(math.floor(y)), int(round(z)) - 1)
        return (x, y, z + (PATH_Z if top == "dirt_path" else 0.0))

    def P(self, name):
        """A place as a 3D point: PLACES[name] (2D entries on the ground), a towers anchor by its short name, or a
        village anchor by its full name."""
        if name in PLACES:
            return self.stand(PLACES[name])
        if name in self.A:
            return tuple(self.A[name])
        return tuple(self.v.anchors[name])

    def yaw(self, name, default=None):
        """The facing of a towers / village anchor (None when it has none)."""
        if name in self.fm.yaw and self.fm.yaw[name] is not None:
            return self.fm.yaw[name]
        return self.v.yaws.get(name, default)

    def camera_spec(self, name):
        """CAMS[name], the set's camera "set:<key>" (TS.CAMERAS), or {} for None."""
        if name is None:
            return {}
        if name.startswith("set:"):
            c = TS.CAMERAS[name[4:]]
            return {k: v for k, v in c.items() if k in ("pos", "target", "lens", "fstop", "pos1", "target1", "ease")}
        return dict(CAMS[name])

    def cam(self, s, name, focus=None, handheld=0.006, seed=None, move=True, ease=None, **over):
        """Put a camera on shot s: lens, position / aim (with its move when it has one and move=True), focus
        (default: its target) and a gentle handheld. name = one of CAMS, "set:<key>" or None (the shot's own camera
        given whole as keywords: pos, target, lens[, fstop, pos1, target1]). ease of the move: default the spec's
        own, else 'ease_out' = AT SPEED ON THE FIRST FRAME, slowing to the last ('linear' for a constant drift).
        Returns the spec used."""
        c = dict(self.camera_spec(name), **over)
        if "pos" not in c or "target" not in c or "lens" not in c:
            raise KeyError("camera %r for %s needs pos, target and lens" % (name, s.name))
        ease = ease or c.get("ease") or "ease_out"
        s.lens(c["lens"], c.get("fstop", 2.8))
        if move and ("pos1" in c or "target1" in c):
            s.move(c["pos"], c["target"], c.get("pos1", c["pos"]), c.get("target1", c["target"]), ease=ease)
        else:
            s.move(c["pos"], c["target"])
        s.focus(focus if focus is not None else c["target"])
        if handheld:
            s.handheld(handheld, seed=sum(ord(ch) for ch in s.name) % 89 if seed is None else seed)
        return c

    def rack(self, s, target, frame, frames=12):
        """Pull the focus of shot s to `target` (a Character's head / an object / a point) starting ON `frame`, over
        `frames` frames (Shot.focus takes film seconds: this converts). Call after C.cam."""
        tgt = target.head if isinstance(target, characters.Character) else target
        s.focus(tgt, at_s=(int(frame) - 1) / float(FPS), rack_s=frames / float(FPS))
        return frame + frames

    def panes(self, s, cam_pos, points, n=3):
        """Hide from the camera, for shot s, the pod's glass blocks on the lines from `cam_pos` to each point (up to
        `n` per line: a grazing line crosses two or three): a face behind the glass without pane lines across it
        (the set's pod_panes). Points may be Characters (their eyes on the shot's first frame). Returns the panes."""
        out = []
        for p in points:
            q = p.eye_point(s.frame_start) if hasattr(p, "eye_point") else p
            for ob in self.fm.panes_toward(tuple(cam_pos), tuple(q), n):
                if ob not in out:
                    out.append(ob)
        fixtures.see_through(self.st, s, out)
        return out

    # ------------------------------------------------------------------ the cast
    @staticmethod
    def _check_tag(tag):
        if tag[:2] not in SEQUENCES:
            raise KeyError("tag %r must start with a sequence prefix: %s" % (tag, ", ".join(SEQUENCES)))

    def actor(self, role, tag):
        """The cast member "<role>_<tag>", built on first use and registered with the Stage (st.cast).

        role   baby       the narrator as a child: a plain plains baby villager (babies wear no profession)
               narrator   the narrator grown up: the unemployed adult, the plain brown robe of type/plains (no
                          profession layer; reads clearly different from the green nitwit: towers' lineup still)
               mom        the farmer in the straw hat (the hat is how the viewer knows her at the glass)
               cleric / librarian / armorer / shepherd     the other villagers (plains, level 1)
               steve      plain Steve (engine.players: walk, sneak, attack, watch, hold("iron_ingot"))
               zombie     the zombie of engine.undead (put it in its cell with C.zombie)
        tag    starts with your sequence prefix (sq, ce, gm, gp, gr); a further twin is just another tag:
               C.actor("baby", "gp"), C.actor("baby", "gp2").
        Twins exist because a character that is in two consecutive shots cannot be keyed before the second one
        starts: whoever must already be moving on the first frame of a shot is a twin that is not in the shot before."""
        if role not in ROLES:
            raise KeyError("no role %r (roles: %s)" % (role, ", ".join(ROLES)))
        self._check_tag(tag)
        st, name = self.st, "%s_%s" % (role, tag)
        c = st.cast.get(name)
        if c is not None:
            return c
        if role == "baby":
            c = st.actor(name, "none", child=True)
        elif role == "narrator":
            c = st.actor(name, "none")
        elif role == "mom":
            c = st.actor(name, "farmer")
        elif role in ("cleric", "librarian", "armorer", "shepherd"):
            c = st.actor(name, role)
        elif role == "steve":
            c = players.add_player(st, name, "steve")
        elif role == "zombie":
            c = undead.add_zombie(st, name)
        return c

    def golem(self):
        """THE iron golem (engine.mobs), one for every spawn of the film (engine/towers.py: the farm keeps its spawn /
        slide history, so a second golem would break golem_spawn's empty_from logic). Golem sequence only; register
        it in a shot with st.use(s, C.golem())."""
        g = self.st.cast.get("golem")
        if g is None:
            g = self.st.cast["golem"] = mobs.make_iron_golem("golem")
        return g

    def item(self, item_id, tag, count=1, seed=0):
        """A dropped item of engine.mobs ("iron_ingot", "poppy"), registered with the Stage like a cast member:
        ingots = C.item("iron_ingot", "gm", count=4); C.fm.deliver([ingots, poppy], f); st.use(s, ingots, poppy).
        (A stack of 2-16 is drawn as two copies, as the game draws it.)"""
        self._check_tag(tag)
        name = "%s_%s" % (item_id, tag)
        it = self.st.cast.get(name)
        if it is None:
            it = self.st.cast[name] = mobs.make_dropped_item(item_id, name=name, count=count, seed=seed)
        return it

    def put(self, c, frame, place, toward=None, yaw=None):
        """place() a character on a named place (or a point), facing `toward` (a place name or a point), `yaw`, or
        (neither) the place's own facing (towers / village anchors), else south. Returns the 3D point."""
        pos = self.P(place) if isinstance(place, str) else self.stand(place)
        if yaw is None and toward is not None:
            aim = self.P(toward) if isinstance(toward, str) else toward
            yaw = L.yaw_to(pos, aim)
        if yaw is None and isinstance(place, str):
            yaw = self.yaw(place)
        c.place(frame, pos, 0.0 if yaw is None else yaw)
        return pos

    def zombie(self, s, tag, aggro=False, look=None, frame=None):
        """The zombie in its cell for shot s ON `frame` (default its first): pressed against the sill, facing the pod,
        arms out with the slow sway; aggro=True: the raised arms (never in CAMS "window": they leave the frame).
        look = a Character / point its head turns to. st.use's it. Returns it."""
        z = self.actor("zombie", tag)
        self.fm.zombie_in_cell(z, s.frame_start if frame is None else int(frame), aggro=aggro, look=look)
        self.st.use(s, z)
        return z

    def on_zombie(self, c, frame):
        """c's head on the zombie's eyes from `frame`, no ease (Mom in every pod shot)."""
        c.look_at(int(frame), self.zombie_eye, ease=0)
        return c

    def pod(self, s, tag, who, panic=False, seeds=None, frame=None):
        """Villagers on their places in the pod for shot s: who = [(role, place), ...] (THREE, FOUR, or your own),
        each placed ON `frame` (default the shot's first) facing the zombie, its head on the zombie's eyes for the
        whole shot; panic=True: trembling with quick turns on the spot (towers.panic, the head kept on the zombie),
        each with PANIC_SEEDS[role] (seeds = {role: seed} to override). st.use's them. Returns {role: Character}."""
        f0 = s.frame_start if frame is None else int(frame)
        out = {}
        for role, place in who:
            c = self.actor(role, tag)
            p = self.P(place)
            c.place(f0, p, L.yaw_to(p, self.zombie_eye))
            out[role] = c
        for role, c in out.items():
            if panic:
                seed = (seeds or {}).get(role, PANIC_SEEDS.get(role, 3))
                towers.panic(c, f0, s.frame_end, self.zombie_eye, seed=seed)
            else:
                self.on_zombie(c, f0)
        self.st.use(s, *out.values())
        return out

    def bed2_at(self, frame):
        """THE SECOND RED BED appears ON `frame` (gr21_count only: on Steve's swing). The film shows P.bed2 in every
        shot from gr21 on (films/twentyminutes.py BED2_FROM); without this call build() makes it appear on the word
        "bed" and says so."""
        if self.bed2_frame is not None:
            raise ValueError("the second bed already appears on frame %d" % self.bed2_frame)
        self.bed2_frame = int(frame)
        self.P_.bed2.place_at(self.bed2_frame)
        return self.bed2_frame

    # ------------------------------------------------------------------ looks
    @staticmethod
    def cheat(c, frame, target, cam_pos, max_off=MAX_OFF):
        """The point c looks at instead of `target` so that its nose is never more than `max_off` degrees from the
        lens (The Hello's meadow _cheat): the target itself while it is within that, otherwise the same point turned
        toward the camera (about the eyes). A villager watching something beyond itself shows the lens a blank box
        past about 80 degrees."""
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
    def lights(self, s, key="tower", at=None, **over):
        """The torch levels of LIGHTS[key] for shot s (Stage.lights once per shot): "square" on the plaza (every
        torch), "tower" everywhere else (the far village torches left out). over = Stage.lights arguments to
        replace (extra=[(point, factor)] boosts the torch nearest that point: only with tools/palette_check)."""
        spec = dict(LIGHTS[key], **over)
        if at is not None:
            spec["at"] = at
        self.st.lights(s, **spec)

    SHARED_FILLS = ()                  # the lead's own fills (none yet)

    def fill(self, name, pos, watts, shots, color=(1.0, 0.98, 0.95)):
        """A film-local shadowless fill light (props.make_light("fill")) that is on in the given shots only and
        hidden everywhere else (a hidden object is in no frame's stamp). `shots` = Shots and / or (first frame, last
        frame) spans. The NAME starts with your sequence prefix ("gm_golem_face": KeyError otherwise), and one name
        = one light: calling it again with the same name adds shots, and raises ValueError if pos, watts or color
        differ (two sequences can never share a light by accident)."""
        if name not in self.SHARED_FILLS and name[:2] not in SEQUENCES:
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
            lamp.name = "twentyminutes_fill_" + name
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
        change of sequence; call it yourself on the first frame of a shot of yours that follows one with particles."""
        return fx.stop_particles(int(frame))

    # ------------------------------------------------------------------ words
    def words(self, s):
        """[(caption, frame)] of the words spoken in shot s (also C.T[s.name].words)."""
        return list(self.T[s.name].words)

    def at(self, s, word, n=0):
        """Frame on which the n-th `word` of shot s appears."""
        return self.T[s.name].at(word, n)
