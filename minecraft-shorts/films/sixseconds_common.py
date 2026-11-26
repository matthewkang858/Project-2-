"""Six Seconds: everything the film (films/sixseconds.py) and its five sequence files share.

    films/sixseconds.py         the narration, the skies, the shot plan, build()              (lead director)
    films/sixseconds_common.py  THIS FILE: the set, the places, the cameras, the cast, the helpers, the contract
    films/sixseconds_set.py     the bastion sets (engine/nether.py) + this film's anchors and camera suggestions
    films/sixseconds_gate.py    gt01 gt03 gt04 gt17 gt18 gt19   the guard, the gate frame, the corridor  (one
    films/sixseconds_row.py     rw02 rw21 rw22 rw23             the gold wall: the ingot row, the stare   director
    films/sixseconds_pit.py     pt05-pt10 pt20                  the boots, the trap, the axe, the smoke   per file)
    films/sixseconds_bridge.py  br11-br15                       the second bastion's bridge and pillar
    films/sixseconds_flash.py   fl16_bridge fl16_treasure fl16_home   the three flash cuts of beat 16

    $BPY -m tools.sixseconds_timeline [--check]   the shot plan: frames, words, skies (no scene is built); captions
    $BPY -m tools.sixseconds_shots render ...     stills of single shots (its docstring): THE scouting tool
    $BPY -m tools.sixseconds_geo --sky S SHOT:F   where every head lands in the frame, face size, facing, what hides it
                                                  (--pts points, --boots the golden boots' box, --track a figure)
    $BPY -m tools.sixseconds_palette --sky S F    nether.check_still on one frame at final quality (gold, brute vs
                                                  blackstone, piglin skin, Steve's clothes, heroes in the safe area)
    $BPY -m render sixseconds --still S [--zones] one frame through render.py (each sky is one build)

A sequence file exposes ONE FUNCTION PER SHOT, named like the shot:  def pt09_axe(st, s, C, nar)
    st   engine.nether.Stage (films.lookdev.Stage: st.use / st.hero / st.lights / st.key; st.v = the Bastion)
    s    the engine.shots.Shot (s.frame_start .. s.frame_end inclusive; s.lens / move / follow / focus / handheld)
    C    the Six object below: set, places, cameras, cast, helpers; C.T[shot name] = the shot's row of the plan
         (frames, words with their frames, sky, neighbours)
    nar  the engine.narration.Narration (nar.at("word", sentence="b09") = the frame the word's caption appears on;
         C.at(s, "word") = the same within shot s)
build() in films/sixseconds.py calls these functions IN TIMELINE ORDER, each exactly once, after every shot exists.
FIVE PEOPLE EDIT AT ONCE: build() imports each sequence file, and calls each shot function, inside a guard. A file
that does not import, or a shot that raises, is printed as "[sixseconds] !!! ..." with its traceback and gets a
plain stand-in (its location's camera, nobody in it); the other files still build. SIXSECONDS_STRICT=1 in the
environment turns the guard off: hand in only when
    SIXSECONDS_STRICT=1 $BPY -m tools.sixseconds_shots build --sky wastes     (and --sky soul for bridge / flash)
runs without a "!!!" line. Scout with tools/sixseconds_shots.py / _geo.py / _palette.py (they write no meta.json).
If you also preview through render.py, use YOUR OWN sample count (PREVIEW_SAMPLES below) so no two directors share a
preview directory (out/preview/sixseconds/270x480_<N>spp): gate 5, row 6, pit 7, bridge 9, flash 10. A preview of
one shot: $BPY -m render sixseconds --frames pt09_axe --res 270x480 --samples 7 --threads 2 (ONE shot name).

THE SEQUENCE CONTRACT (what a sequence director may and must do)
  MAY   edit his own file only: the bodies of its shot functions, its docstrings, private helpers and constants.
        Make further twins of the shared cast with his own tags (C.actor("piglin", "pt4")). Add a film-local light
        with C.fill("<prefix>_<name>", ...) (the name starts with his prefix; hidden outside the shots he names).
        Move a camera of his own shots freely, unless SHARED below names a camera or place for it.
  MUST  keep every shot function's name and signature;
        give every shot a camera (C.cam: lens, move, focus, handheld; nothing is ever dead still: something already
        moving on its first frame), its cast (st.use: everybody else is hidden), what it is about (st.hero, inside
        x 8-82 %, y 14-60 % of the frame, clear of the caption band y 62-72 %; the golden boots: C.boots_of(runner))
        and its lantern levels (C.lights once per shot);
        take characters only through C.actor(role, tag) and dropped items only through C.item(item_id, tag), with a
        tag that starts with HIS prefix (gt, rw, pt, br, fl): no other sequence can then disturb his keys;
        key each character in frame order; place() everybody on the first frame of a shot before any look_at();
        call look_at(f0, ..., ease=0) BEFORE idle() (Character.idle puts a head key on its first frame);
        key nobody before a shot starts unless that instance is NOT in the shot before (pre-roll: use a twin);
        use the SHARED places and cameras below where the plan names them, unchanged;
        keep the story's continuity rules (THE WORLD'S RULES below);
        nothing important in the last 3 frames before a cut, no word or action that needs the shot after it;
        render what he changed (tools/sixseconds_shots.py at 540x960, 16 samples, --zones) and LOOK at it; run
        tools/sixseconds_palette on one frame per shot (nether.check_still: gold hue, brute 1.5 x the blackstone
        where he is a hero, piglin skin, Steve's clothes, heroes in the safe area); check faces at 360x640.
  MUST NOT  touch films/sixseconds.py, this file, films/sixseconds_set.py, another sequence file or anything in
        engine/, render.py, tools/ (his own new tools/sixseconds_<seq>_*.py excepted); change the narration, the
        cuts, a sky or the film's length; make anything depend on which sky is being built (no `if sky ...`: every
        build keys the same things); call st.shot / st.sky_change / st.dip / st.finish (the film does); key
        hide_render on a character, its armor or its items (st.use does it); boost lanterns beyond LIGHTS without
        nether.check_still; build a character with piglins.add_piglin / players.add_player directly (it would escape
        the twin rule); call bas.pit_open / bas.pillar_in directly (C.pit / C.pillar check the continuity); start a
        final render (render.py --frames without --res / --samples).
  If a shared place or camera is wrong for his shot, he says so in his result; he does not move it.

THE WORLD'S RULES (the story's continuity; C.pit and C.pillar enforce the first two)
  * THE PIT exists only in pt06 (dug but its last block, which he breaks on camera), pt07, pt08, pt09, pt10 and
    pt20 (PIT_SHOTS). Every other home shot shows the floor WHOLE (worlds the runner never reached, or reaches fresh).
  * THE NETHERRACK PILLAR stands only in br13, br14 and br15 (PILLAR_SHOTS). Not in fl16_bridge: tested by the
    lead, from the flash camera its top block sits right on the brute's head (a tangent; out/test/
    sixseconds_tiles/fl16_bridge.png of the first stub film).
  * THE BRUTE is absent from gt19 and pt20 (the older version of the world, from before brutes: NO_BRUTE_SHOTS);
    the side of pt20's frame where he walked in in pt09 stays empty.
  * THE RUNNER wears golden boots in every shot he is in (C.actor("runner", ...) puts them on), and holds the iron
    pickaxe unless a shot gives him a gold ingot (Player.hold("gold_ingot", frame=...)).
  * Every ordinary piglin holds a golden sword (role "piglin") or a crossbow ("piglin_xbow"); the brute alone has the
    golden axe; he stands 0.7 block or more from any brother in every shot (the story's risk: he must read as a
    different kind at a glance).
  * A piglin admires with the ingot in its LEFT hand, golden sword in the right (Piglin.admire; C.admire holds it
    for a whole shot). Head limits: 75 degrees of yaw, 40 of pitch (the step ingot of 21-23 needs 21).
  * The death of the runner is a white puff (C.puff), never a body: pt10 and the three flash cuts.
  * Particles never live across a change of place: build() ends them at every change of sequence (C.time_jump).

SHARED (decided once, used by two shots or two sequences; every camera was rendered with its cast: see the
films/sixseconds.py docstring for the stills)
  CAMS["gate"]        THE GATE FRAME: gt03, gt18, gt19 EXACTLY (position, aim, lens, f-stop, handheld amount AND
                      seed: the drift is a function of the frame, so gt18 -> gt19 drifts on across the match cut).
                      The story's 4th use (beat 23) is replaced by its own fallback (rw23, CAMS["reverse"]).
  CAMS["ingot_row"]   THE INGOT ROW FRAME: rw02 and rw21 exactly                                    row
  CAMS["pit"]         THE PIT CAMERA: pt06 and pt20 exactly                                         pit
  CAMS["boot"], CAMS["bridge_boot"]   THE BOOT FRAMING: pt05 (home) and br11 (bridge) are one framing on two sets:
                      the boots land where BOOT_FRAME says in both (measured on renders of the stub film; see
                      there): the same box to 1 % of the frame                                   pit, bridge
  CAMS["flash_bridge"], ["flash_treasure"], ["flash_home"]: one offset from the brute in all three (fl16_*)
  PLACES["gold_1".."gold_3"]  the three piglins at the gold in the gate frame and the corridor: gt03, gt17, gt18,
                      gt19 (and pt05's piglins at the gold turn from there); IDENTICAL on both sides of gt18 -> gt19
  PLACES["brother_1"], ["brother_2"], ["brute_gold"], ["step_ingot"]: the gold row of beats 2 and 21-23     row
  PLACES["landing"], ["gateway"]: the brute on guard (gt03, gt04) and in the gateway (gt17, gt18)            gate
  PLACES["boot_mark"], ["rim_w"], ["strike"]: the runner's skid, his place at the rim, the brute's     pit
  The skies (films/sixseconds.py SKIES), the light recipes LIGHTS, the lead's fill KEY_LANDING (gt01).

Coordinates (films/sixseconds_set.py and engine/nether.py have the plans): Blender blocks, +X east, +Y north, +Z up;
every floor z 0; the pit floor z -2; the landing top z 4; the gold step's top z 1. A character faces -Y at yaw 0
(nether.yaw_to(src, dst)). HOME at the origin: courtyard x 0..8, y -2..17; gateway x 3..5 in the north wall (y 18..
20), the corridor y 21..32 with the lava wall at y 33; guard stair x 0..1, y 6..9, landing x 0..2, y 10..17; gold
wall x 9, y 9..15 with the step x 8; pit cells x 4..5, y 6..7. BRIDGE at (400, 0, 0): deck x -1..1 (world 399..401),
y -8..44; the netherrack pillar at (400, 19). TREASURE corner at (-400, 0, 0).
"""

from mathutils import Vector

from engine import fx, nether, piglins, players, props
from films import lookdev as L
from films import sixseconds_set as SS

FPS = 24
FINAL_RES, FINAL_SAMPLES = (540, 960), 16      # this film's final quality (set on the scene by films/sixseconds.py)
STARE_FRAMES = 144                              # rw21 + rw22: the six-second stare, first frame to the cut into rw23

SEQUENCES = {"gt": "gate", "rw": "row", "pt": "pit", "br": "bridge", "fl": "flash"}
PREFIX = {v: k for k, v in SEQUENCES.items()}
PREVIEW_SAMPLES = {"gate": 5, "row": 6, "pit": 7, "bridge": 9, "flash": 10}   # a preview directory per sequence

PIT_SHOTS = ("pt06_dig", "pt07_pearl", "pt08_gravel", "pt09_axe", "pt10_smoke", "pt20_likes")
PILLAR_SHOTS = ("br13_pillar", "br14_zero", "br15_wait")
NO_BRUTE_SHOTS = ("gt19_older", "pt20_likes")


def build_set(scene):
    """The bastion sets of "Six Seconds" (films/sixseconds_set.py: engine.nether.build_bastion + this film's anchors
    and camera suggestions). Returns the Bastion."""
    return SS.build_set(scene)


# ----------------------------------------------------------------------------------------------------------------
# places: name -> an anchor of the set (bas.anchors, with its yaw in bas.yaws when it is a standing place) or a point.
# C.P(name) gives the 3D point, C.yaw(name) the anchor's yaw. C.P also takes any anchor name of the set directly
# (C.P("home_pit_3")); these names are the ones TWO shots or two sequences share.
# ----------------------------------------------------------------------------------------------------------------
PLACES = {
    # ---- the guard (gate)
    "landing_edge": "six_landing_brute",   # gt01: the brute at the landing's edge, big at frame left (facing the lens)
    "landing_look": "six_landing_look",    # gt01: what he looks at: just past the lens
    "landing": "home_landing",             # gt03, gt04: on guard at the landing's NE corner, facing east; he watches
    "landing_look_gate": "home_landing_look",   # the gateway's mouth (gt03: a clean profile in the gate frame)
    "gateway": "home_gateway",             # gt17, gt18: planted in the middle of the gateway, facing OUT (north, yaw pi)
    "gateway_target": "home_gateway_target",
    "corridor": "home_corridor",           # (4.5, 27) in the entrance corridor; "entry" (4.5, 31.5) by the lava wall
    "entry": "home_entry",
    # ---- the piglins at the gold (gt01 has its own three: six_b1_pig_1..3)
    "gold_1": "home_gold_1", "gold_2": "home_gold_2", "gold_3": "home_gold_3",    # gt03 gt17 gt18 gt19, pt05
    "gold_target": "home_gold_target",     # the gold wall they face (9, 12.5, 1.5)
    # ---- the gold row (row)
    "brother_1": "six_brother_1",          # (7.0, 13.2) yaw NE: rw02, rw21, rw23 (admiring)
    "brother_2": "six_brother_2",          # (6.3, 10.8) yaw NE
    "brute_gold": "six_brute_gold",        # (7.6, 10.0) yaw NE: rw21, rw22, rw23 (1.1 from brother 2's feet line)
    "step_ingot": "six_step_ingot",        # (8.16, 11.71, 1.0): the ingot turning on the step (rw21-rw23)
    "brute_turned": "six_brute_turned",    # (4.97, 15.4) facing west: rw02, his soft dark shoulder at the right edge
    "gateway_mouth": "six_gateway_mouth",  # (4.5, 18.6, 1.8): what he turns his head to on "Nothing" (rw23)
    # ---- the trap (pit)
    "boot_mark": "home_boot_mark",         # (3.65, 6.75): the skid stops here (pt05), facing south; he digs here
    "rim_w": "home_rim_w",                 # (3.6, 7.0) facing east into the pit: pt06-pt09, pt20
    "strike": "home_strike",               # (2.35, 7.0) facing east: the brute hits the runner at rim_w (pt09, pt10)
    "pit_lure": "six_pit_lure",            # (5.4, 7.3, -2): the lure ingot on the pit floor (pt06; NOT home_pit_1:
    #                                        that point is inside the kept last block)
    "pearl_rest": "six_pearl_rest",        # (3.85, 6.55): the pearl lands beside the boots (pt07) and lies there (pt08)
    # ---- the bridge (bridge)
    "bridge_boot_mark": "bridge_boot_mark",   # (400.5, 6.5): the skid (br11)
    "bridge_player": "bridge_player",      # (400.5, 10.6) facing north (br12)
    "bridge_brute": "bridge_brute",        # (400.5, 16.5) facing south under his lantern (br12)
    "pillar_foot": "bridge_pillar_foot",   # (400.5, 18.25) facing the pillar (br13-br15)
    "pillar_top": "bridge_pillar_top",     # (400.5, 19.5, 3) the runner crouched on the pillar (br13, br15)
    # ---- the flash cuts (flash): the brute's place in each world; the puff, the boots, the extra drop beside him
    "flash_bridge": "bridge_flash", "flash_treasure": "treasure_flash", "flash_home": "home_flash",
}

# ----------------------------------------------------------------------------------------------------------------
# cameras: name -> dict(pos, target, lens, fstop[, pos1, target1][, handheld, seed]); C.cam(s, name) puts one on a
# shot. The SHARED ones are here; every other camera is its sequence's own: C.cam(s, "set:<name>") takes the set's
# suggestion (bas.cameras, films/sixseconds_set.py NEW_CAMERAS or engine/nether.py), C.cam(s, None, **SPEC) a
# constant of the sequence file.
# ----------------------------------------------------------------------------------------------------------------
GATE_SEED = 17
CAMS = {
    # THE GATE FRAME (beats 3, 18, 19): engine/nether.py's 'gate', 30 mm f/4 from the near (south) end of the
    # courtyard: the gateway and the corridor glow in the middle, the brute on the landing upper left in profile
    # (gt03), the three piglins at the gold nearer and lower on the right, apart, the gold wall at the right edge.
    # gt18: the brute small in the gateway, a silhouette against the glow (back to us); gt19: the same frame without
    # him (the match cut). A barely moving handheld with ONE seed for all three: it drifts on across the 18/19 cut.
    "gate": dict(pos=(5.2, 1.0, 1.8), target=(5.94, 18.0, 2.6), lens=30.0, fstop=4.0, handheld=0.003, seed=GATE_SEED),
    # THE INGOT ROW (beats 2, 21): films/sixseconds_set.py six_ingot_row, snout height from the north-west along
    # the gold wall, 36 mm f/2.2: the brothers at brother_1 / brother_2 admiring (ingots in the left hand at the
    # snout, swords in the right), the gold wall and its lantern behind; rw02 the brute's dark shoulder soft at the
    # right edge (brute_turned), rw21 the brute between them at brute_gold, head down (his ingot is hidden behind
    # brother 1 from here: rw22 shows it).
    "ingot_row": dict(pos=(5.0, 17.0, 1.65), target=(7.5, 10.4, 1.45), lens=36.0, fstop=2.2),
    # THE PIT CAMERA (beats 6, 20): engine/nether.py's 'pit', 28 mm f/4, high from the south-west over the pit: the
    # runner at rim_w, the pit with the piglins, the gold wall above.
    "pit": dict(pos=(2.1, 3.4, 5.4), target=(5.4, 7.5, -1.2), lens=28.0, fstop=4.0),
    # THE BOOT FRAMING (beats 5 and 11; BOOT_FRAME): on the floor, long lens, the golden boots mid-frame above the
    # caption band. Home: nether's 'boot' (50 mm f/2, south-west of the boot mark looking north-east across the
    # courtyard at the gold wall). Bridge: the set's six_bridge_boot turned so the boots land where they land at home
    # (lead's scouting; see BOOT_FRAME): along the bridge to the pillars and the lantern.
    "boot": dict(pos=(1.2, 3.8, 0.25), target=(5.06, 8.4, 0.12), lens=50.0, fstop=2.0),
    "bridge_boot": dict(pos=(401.65, 2.9, 0.28), target=(400.45, 6.7, 0.15), lens=50.0, fstop=2.0),
    # THE FLASH CUTS (beat 16): 5 blocks in front of the brute at 1.45, aimed 0.5 above his feet, 35 mm f/2.8, in
    # every world: he is locked in the same spot of the frame, only the bastion behind him changes
    "flash_bridge": dict(pos=(400.5, 11.5, 1.45), target=(400.5, 16.5, 0.5), lens=35.0, fstop=2.8),
    "flash_treasure": dict(pos=(-396.0, -4.2, 1.45), target=(-396.0, 0.8, 0.5), lens=35.0, fstop=2.8),
    "flash_home": dict(pos=(4.5, 9.5, 1.45), target=(4.5, 14.5, 0.5), lens=35.0, fstop=2.8),
    # the stand-ins of a failed shot (films/sixseconds.py STAND_IN) that are not shared above: the set's suggestions
    "landing": dict(pos=(0.4, 17.4, 5.8), target=(6.0, 13.6, 3.4), lens=26.0, fstop=2.8, pos1=(0.62, 17.25, 5.76)),
    "bridge_shoulder": dict(pos=(401.15, 8.7, 1.95), target=(400.5, 16.5, 1.35), lens=50.0, fstop=2.6),
    # beat 23: the story's own fallback (films/sixseconds_set.py six_gate_reverse), reverse angle from the gateway's
    # west jamb, floor level: the empty blackstone under the caption, the brute at the gold lifting his face toward
    # the lens (the gate frame cannot give "a clean profile against the glow": the gateway lies behind him)
    "reverse": dict(pos=(3.5, 17.5, 0.45), target=(7.2, 10.4, 1.3), lens=36.0, fstop=2.8),
}
# THE BOOT FRAMING: the box of the golden boots in % of the frame, measured on the stub film by the lead after the
# restart (tools.sixseconds_geo --boots; stills out/test/sixseconds_scout_boots_pt05_boots_318.png and
# out/test/sixseconds_scout_boots_br11_boots_728.png, side by side: the same picture on two sets): both cameras are
# 50 mm f/2, 3.8-4.0 blocks from the boots, 0.25-0.28 above the floor; pt05 x 27.7-70.2, y 43.0-58.8 and br11
# x 27.7-69.5, y 42.5-58.5. Keep the runner's skid ON boot_mark / bridge_boot_mark, entering from the frame's LEFT
# edge in both (the stubs do), and the boots inside this box (the set builder's br11 suggestion, 45 mm aimed at
# x 400.65, had them at x 17-56 %: CAMS["bridge_boot"] is that camera turned to match).
BOOT_FRAME = dict(x=(27.0, 71.0), y=(42.0, 59.0))

# lantern levels (C.lights(s, key)): Stage.lights(scale, groups, **bas.lights_for(set)); every one looked at on
# stills (films/sixseconds_set.py BEATS). Do not raise a lantern without nether.check_still on the frame.
LIGHTS = {
    "home": dict(set="home", scale=1.0),                               # the home bastion, floor whole
    "pit": dict(set="home", scale=1.0, groups={"home_pit": 2.0}),      # pit shots: the pit's lantern x 2 (without
    #                                                                    it the piglins in the pit go dull: 0.62 skin)
    "bridge": dict(set="bridge", scale=1.0),                           # the bridge world
    "treasure": dict(set="treasure", scale=1.0),                       # the treasure corner (fl16_treasure)
}
# gt01: the brute's own key on the landing (warm white, shadowless, this shot only): 1.23 -> 2.41 x the blackstone
# (films/sixseconds_set.py FILLS "six_key_landing"; the story's risk "give him his own lantern as key")
KEY_LANDING = dict(pos=SS.FILLS["six_key_landing"][0], watts=SS.FILLS["six_key_landing"][1], color=SS.KEY_COLOR)

# role -> how Six.actor builds it
ROLES = ("brute", "piglin", "piglin_xbow", "runner")
ITEMS = ("gold_ingot", "ender_pearl", "gravel", "golden_boots", "iron_pickaxe")


def yaw_to(src, dst):
    """Yaw that makes a character at src (facing -Y at yaw 0) face dst."""
    return L.yaw_to(src, dst)


class ShotInfo:
    """One row of the film's shot plan with its frames: C.T[shot name].

    name, beat, sequence, sky, sentence (the engine.narration Sentence spoken in the shot), frame_start, frame_end
    (inclusive), frames, seconds, words = [(caption, frame it appears on)], black = (first, last) frames the encoder
    shows black in this shot (the reset of pt10, the snaps of the flash cuts, the end) or None, prev / next = the
    neighbouring shots' names (or None)."""

    def __init__(self, **kw):
        self.black, self.prev, self.next = None, None, None
        self.__dict__.update(kw)

    def at(self, word, n=0):
        """Frame on which the n-th `word` spoken in this shot appears (case-insensitive caption text)."""
        hits = [f for w, f in self.words if w.lower().strip(".,") == word.lower()]
        return hits[n]

    def __repr__(self):
        return "<%s beat %d %s %s %d-%d>" % (self.name, self.beat, self.sequence, self.sky, self.frame_start,
                                            self.frame_end)


class Six:
    """The film's shared context, handed to every shot function as C.

    C.st / C.bas / C.A / C.Y   the Stage, the Bastion, its anchors and yaws (C.A["home_pit_3"], C.Y["home_gold_1"])
    C.nar, C.T                 the Narration; the shot plan: C.T["pt09_axe"] -> ShotInfo
    C.P(name), C.yaw(name)     a place of PLACES (or any anchor) as a 3D point; its yaw (a standing place)
    C.cam(s, name, ...)        one of CAMS, "set:<camera>" (the set's suggestions) or None + a spec, on a shot
    C.actor(role, tag)         a cast member, built once per tag: roles in ROLES, tag starts with the sequence prefix
    C.item(id, tag)            a dropped item (resting, bobbing, spinning), registered like a cast member
    C.boots_of(runner)         the runner's golden boots (armor objects: st.hero of a boot shot)
    C.put / C.admire / C.puff / C.pit / C.pillar / C.lights / C.fill / C.key_landing / C.time_jump / C.at
    C.shots, C.memo            every Shot of the film by name; a dict for handing things from one shot function to a
                               later one of the SAME sequence (key prefixed with it: C.memo["pt_pearl"])
    """

    def __init__(self, st, nar=None, timeline=None):
        self.st, self.bas = st, st.v
        self.A, self.Y = st.v.anchors, st.v.yaws
        self.nar = nar
        self.T = dict(timeline or {})
        self.shots = {}            # shot name -> engine.shots.Shot (filled by films/sixseconds.py before any function)
        self.memo = {}             # what one shot function leaves for a later one of ITS OWN sequence
        self._fills = {}
        self._boots = {}

    # ------------------------------------------------------------------ places and cameras
    def P(self, name):
        """A named place (PLACES, or any anchor of the set) as a 3D point; a point is returned as it is (an (x, y)
        point is put on the ground there)."""
        if not isinstance(name, str):
            p = tuple(float(v) for v in name)
            return p if len(p) == 3 else (p[0], p[1], float(self.bas.ground(p[0], p[1]) or 0.0))
        a = PLACES.get(name, name)
        if isinstance(a, str):
            if a not in self.A:
                raise KeyError("no place or anchor %r" % name)
            return tuple(float(v) for v in self.A[a])
        return self.P(a)

    def yaw(self, name, default=0.0):
        """The yaw of a standing place (bas.yaws of its anchor), or `default`."""
        a = PLACES.get(name, name)
        return float(self.Y.get(a, default)) if isinstance(a, str) else default

    def camera_spec(self, name):
        """CAMS[name], the set's camera "set:<name>" (bas.cameras: films/sixseconds_set.py and engine/nether.py), or
        {} for None (a shot's own camera, given whole to C.cam as keywords)."""
        if name is None:
            return {}
        if name.startswith("set:"):
            c = self.bas.cameras[name[4:]]
            return {k: c[k] for k in ("pos", "target", "lens", "fstop", "pos1", "target1") if k in c}
        return dict(CAMS[name])

    def cam(self, s, name, focus=None, handheld=None, seed=None, move=True, ease="ease_out", **over):
        """Put a camera on shot s: lens, position / aim (with its move when it has one and move=True), focus
        (default: its target) and a gentle handheld (default: the spec's, else 0.004). name = one of CAMS (a shared
        camera: use it unchanged), "set:<name>" or None (the shot's OWN camera, a constant of its sequence file
        given whole as keywords: pos, target, lens[, fstop, pos1, target1]). over = entries to replace or give.
        ease: of the move; default 'ease_out' = AT SPEED ON THE FIRST FRAME, slowing to the last ('linear' for a
        constant drift). The handheld drift is a function of the FRAME and the seed (default: from the shot's name;
        the shared gate frame has its own): two shots with one seed drift on across their cut. Returns the spec."""
        c = dict(self.camera_spec(name), **over)
        if "pos" not in c or "target" not in c or "lens" not in c:
            raise KeyError("camera %r for %s needs pos, target and lens" % (name, s.name))
        s.lens(c["lens"], c.get("fstop", 2.8))
        if move and "pos1" in c:
            s.move(c["pos"], c["target"], c["pos1"], c.get("target1", c["target"]), ease=ease)
        else:
            s.move(c["pos"], c["target"])
        s.focus(focus if focus is not None else c["target"])
        amount = c.get("handheld", 0.004) if handheld is None else handheld
        if seed is None:
            seed = c.get("seed", sum(ord(ch) for ch in s.name) % 89)
        if amount:
            s.handheld(amount, seed=seed)
        return c

    # ------------------------------------------------------------------ the cast
    def actor(self, role, tag):
        """The cast member "<role>_<tag>", built on first use and registered with the Stage (st.cast).

        role   brute        the narrator: a piglin brute (the game's model and texture, dark tunic, gold armband)
                            with the golden axe
               piglin       an ordinary piglin with a golden sword (his "brothers")
               piglin_xbow  an ordinary piglin with a crossbow (the story: "golden swords and a crossbow")
               runner       the speedrunner: Steve's skin, NO armor but golden boots (players.equip), the iron
                            pickaxe in his hand (Player.hold("gold_ingot", frame=f) to throw gold)
        tag    starts with your sequence prefix (gt, rw, pt, br, fl); a further twin is just another tag:
               C.actor("piglin", "pt1"), C.actor("piglin", "pt2"), C.actor("runner", "pt2").
        Twins exist because a character that is in two consecutive shots cannot be keyed before the second one
        starts: whoever must already be moving on the first frame of a shot is a twin that is not in the shot
        before."""
        if role not in ROLES:
            raise KeyError("no role %r (roles: %s)" % (role, ", ".join(ROLES)))
        if tag[:2] not in SEQUENCES:
            raise KeyError("tag %r must start with a sequence prefix: %s" % (tag, ", ".join(SEQUENCES)))
        st, name = self.st, "%s_%s" % (role, tag)
        c = st.cast.get(name)
        if c is not None:
            return c
        if role == "brute":
            c = piglins.add_piglin(st, name, "brute")
        elif role == "piglin":
            c = piglins.add_piglin(st, name, "piglin")
        elif role == "piglin_xbow":
            c = piglins.add_piglin(st, name, "piglin", weapon="crossbow")
        elif role == "runner":
            c = players.add_player(st, name, "steve")
            self._boots[name] = players.equip(c, boots="golden")
            c.hold("iron_pickaxe")
        return c

    def boots_of(self, runner):
        """The golden boots (armor objects) of a runner made by C.actor: what st.hero names in a boot shot."""
        return list(self._boots[runner.name])

    def item(self, item_id, tag):
        """A dropped item of engine.mobs (gold_ingot, ender_pearl, gravel, golden_boots, iron_pickaxe ...),
        registered with the Stage like a cast member: it = C.item("gravel", "pt3"); it.place(f0, C.P("...")) (it
        rests there, bobbing and turning) or piglins.barter / throw_item / launch (it flies); it.animate(f0, f1 + 1);
        st.use(s, it). One tag = one item entity; give each item of a shot its own tag."""
        if tag[:2] not in SEQUENCES:
            raise KeyError("tag %r must start with a sequence prefix: %s" % (tag, ", ".join(SEQUENCES)))
        return piglins.add_item(self.st, item_id, name="%s_%s" % (item_id, tag))

    def rest(self, s, item_id, tag, place, frame=None):
        """A dropped item lying (bobbing, turning) on `place` for the rest of shot s, from `frame` (default: its first
        frame), in the shot (st.use). Returns it."""
        it = self.item(item_id, tag)
        f = s.frame_start if frame is None else int(frame)
        p = self.P(place)
        it.place(f, p)
        it.animate(f, s.frame_end + 1)
        self.st.use(s, it)
        return it

    def put(self, c, frame, place, toward=None, yaw=None):
        """place() a character on a named place (or a point), facing `toward` (a place name or a point), `yaw`, or
        the place's own yaw. Returns the 3D point."""
        pos = self.P(place)
        if yaw is None:
            if toward is not None:
                aim = self.P(toward)
                yaw = L.yaw_to(pos, aim)
            else:
                yaw = self.yaw(place) if isinstance(place, str) else 0.0
        c.place(frame, pos, yaw)
        return pos

    def stand(self, s, c, place, look=None, toward=None, yaw=None, idle=True, seed=0):
        """A figure standing on `place` for the whole of shot s: placed on its first frame, its head on `look` (a
        place, a point, a Character) with no ease, alive (piglins: idle glances and the ears; players: idle), in the
        shot (st.use). Returns it. For a stare that must not glance, idle=False (piglins still flop their ears)."""
        f0, f1 = s.frame_start, s.frame_end
        self.put(c, f0, place, toward=toward, yaw=yaw)
        if look is not None:
            tgt = look if hasattr(look, "eye_point") else Vector(self.P(look))
            c.look_at(f0, tgt, ease=0)
        if isinstance(c, piglins.Piglin):
            if idle:
                c.idle(f0, f1 + 1, seed=seed)
            else:
                c.flop_ears(f0, f1 + 1)
        elif idle and hasattr(c, "idle"):
            c.idle(f0, f1 + 1, seed=seed)
        self.st.use(s, c)
        return c

    def admire(self, s, c, frame=None, item="gold_ingot"):
        """A piglin in the game's admire pose (ingot in the LEFT hand at the snout, head bowed to it, sword in the
        right) from `frame` (default: the shot's first frame) through the end of shot s (no idle / look_at during
        it). Returns the frame the pose ends (after the shot)."""
        f = s.frame_start if frame is None else int(frame)
        ticks = (s.frame_end + 2 - f) / 1.2
        end = c.admire(f, item, ticks=max(ticks, 2.0))
        c.flop_ears(f, s.frame_end + 1)
        return end

    def puff(self, s, place, frame, seed=0, **kw):
        """The runner's death: the game's white poof (20 puffs, a player's box 0.6 x 1.8) standing on `place`,
        from `frame` (a frame before the shot starts = puffs already in the air on its first frame: a flash cut),
        seen in shot s only (engine.piglins.poof with camera=s). Returns the fx Burst."""
        return piglins.poof(Vector(self.P(place)), int(frame), camera=s, size=(0.6, 1.8), seed=seed, **kw)

    # ------------------------------------------------------------------ the world's rules
    def pit(self, s, keep_last=False):
        """THE PIT dug in shot s (bas.pit_open: its eight blocks gone, its fill light on); keep_last=True leaves its
        last block (bas.pit_last, cell (4, 6, -2)) for the runner to break on camera (pt06: breaking.mine(runner,
        C.bas.pit_last, frame, camera=s)). Only in PIT_SHOTS: anywhere else the floor stays whole (ValueError)."""
        if s.name not in PIT_SHOTS:
            raise ValueError("the pit is dug only in %s, not in %s (the story's pit continuity)"
                             % (", ".join(PIT_SHOTS), s.name))
        return self.bas.pit_open(s, keep=[self.bas.pit_last.cell] if keep_last else ())

    def pillar(self, s):
        """THE NETHERRACK PILLAR stands in shot s (bas.pillar_in). Only in PILLAR_SHOTS (ValueError elsewhere)."""
        if s.name not in PILLAR_SHOTS:
            raise ValueError("the pillar stands only in %s, not in %s" % (", ".join(PILLAR_SHOTS), s.name))
        return self.bas.pillar_in(s)

    # ------------------------------------------------------------------ light
    def lights(self, s, key="home", at=None, **over):
        """The lantern levels of LIGHTS[key] for shot s (Stage.lights once per shot, only the lanterns of that set
        on). over = Stage.lights arguments to replace (groups=..., scale=...)."""
        spec = dict(LIGHTS[key], **over)
        where = spec.pop("set")
        kw = dict(self.bas.lights_for(where))
        kw.update(spec)
        if at is not None:
            kw["at"] = at
        self.st.lights(s, **kw)

    SHARED_FILLS = ("key_landing",)            # the lead's own fill (C.key_landing)

    def fill(self, name, pos, watts, shots, color=(1.0, 0.95, 0.88)):
        """A film-local shadowless light (props.make_light("fill")) that is on in the given shots only and hidden
        everywhere else (a hidden object is in no frame's stamp). `shots` = Shots and / or (first frame, last frame)
        spans. The NAME starts with your sequence prefix ("pt_boots", "fl_key": KeyError otherwise), and one name =
        one light: calling it again with the same name adds shots, and raises ValueError if pos, watts or color
        differ (two sequences can never share a light by accident). Default colour: the set's warm white."""
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
            lamp = self._fills[name] = props.make_light("fill", self.bas.collection)
            lamp.name = "six_fill_" + name
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

    def key_landing(self, s):
        """gt01: the brute's own key on the landing (KEY_LANDING: warm white, shadowless, 160 W over his head)."""
        return self.fill("key_landing", KEY_LANDING["pos"], KEY_LANDING["watts"], [s], color=KEY_LANDING["color"])

    # ------------------------------------------------------------------ time jumps
    @staticmethod
    def time_jump(frame):
        """End every particle still in the air on `frame` (engine.fx.stop_particles): the film calls it at every
        change of sequence; call it on the first frame of a shot that jumps in time inside your sequence BEFORE
        emitting that shot's own particles."""
        return fx.stop_particles(int(frame))

    # ------------------------------------------------------------------ words
    def words(self, s):
        """[(caption, frame)] of the words spoken in shot s (also C.T[s.name].words)."""
        return list(self.T[s.name].words)

    def at(self, s, word, n=0):
        """Frame on which the n-th `word` of shot s appears."""
        return self.T[s.name].at(word, n)

    def black(self, s):
        """(first, last) frames of shot s that the encoder shows black (the reset of pt10, the snaps of the flash cuts,
        the end of rw23), or None: nothing there is seen; the caption is."""
        return self.T[s.name].black


def project(cam, point):
    """Where a point lands in a 9:16 frame for a camera spec (u, v in 0..1 from the top left; None behind it):
    engine.nether.project."""
    return nether.project(cam["pos"], cam["target"], cam["lens"], point)
