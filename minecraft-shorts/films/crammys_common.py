"""The Crammys: everything the film (films/crammys.py) and its five sequence files share.

    films/crammys.py           the narration, the skies, the shot plan, build()                       (lead director)
    films/crammys_common.py    THIS FILE: the set, the places, the cameras, the cast, the continuity, the helpers,
                               the sequence contract
    films/crammys_set.py       the set (the set builder's: engine/music's bandstand and lane + the night meadow;
                               anchors, paths, one suggested camera per beat CS.CAMERAS["b01"..."b24"] with its
                               proof still out/test/crammys_set_<beat>_<what>.png)
    films/crammys_gold.py      gd01 gd02 gd03 gd04 gd05 gd06          the bandstand in golden light (beats 1-6)
    films/crammys_road.py      rd07 rd09 rd17                         the lane and the exit gate at night (7, 9, 17)
    films/crammys_meadow.py    md10 md11 md12 md13 md15 md16          the night meadow (beats 10-16; 13+14 one take)
    films/crammys_jukebox.py   jb08 jb18 jb19 jb20                    the bandstand at night: the eject, the arrival,
                                                                      disc eleven into the jukebox (8, 18, 19, 20)
    films/crammys_finale.py    fn21 fn22 fn23 fn24                    the bandstand at night: the song, nobody moved,
                                                                      Kai, Best Vocals (21-24)

    $BPY -m tools.crammys_timeline [--check|--json]  the shot plan: frames, words, skies (no scene); caption proof
    $BPY -m tools.crammys_shots render ...           stills of single shots (see its docstring): THE scouting tool
    $BPY -m tools.crammys_geo --sky S SHOT:F         where every head lands in the frame, face size, facing, blockers
    $BPY -m tools.crammys_palette --sky S F          tools/palette_check on one frame at final quality
    $BPY -m tools.crammys_probe track SHOT A-B:N     where the cast IS frame by frame: world position, eyes / chest /
                                                     knees in the frame and seen or hidden, held items, stuck arrows
    $BPY -m tools.crammys_probe memo | hands | notes  event frames the stubs leave in C.memo; what each hand holds and
                                                     renders; the jukebox's note frames (no render; one build)
    $BPY -m render crammys --still S [--zones]       one frame through render.py (each sky is one build)
    $BPY -m films.crammys_set [b13 ...]              the set's self-test and its own proof stills
    $BPY -m tools.check_music_zones [gold|night]     engine/music's zone + occlusion check of ITS staging (no render)

A sequence file exposes ONE FUNCTION PER SHOT, named like the shot:  def md13_shot(st, s, C, nar)
    st   films.lookdev.Stage (st.use / st.hero / st.key; st.v = the Village)
    s    the engine.shots.Shot (s.frame_start .. s.frame_end inclusive; s.lens / move / focus / handheld)
    C    the Crammys object below: set, band, places, cameras, cast, continuity helpers; C.T[shot name] = the shot's
         row of the plan (frames, words with their frames, sky, neighbours)
    nar  the engine.narration.Narration (nar.at("word", sentence="b13") = the frame the word's caption appears on;
         C.at(s, "word") = the same within shot s)
build() in films/crammys.py calls these functions IN TIMELINE ORDER (gd01..gd06, rd07, jb08, rd09, md10..md16,
rd17, jb18..jb20, fn21..fn24), each exactly once, after every shot exists. FIVE PEOPLE EDIT AT ONCE: build()
imports each sequence file, and calls each shot function, inside a guard. A file that does not import, or a shot
that raises, is printed as "[crammys] !!! ..." with its traceback and gets a plain stand-in (its location's camera,
nobody in it); the other files still build. CRAMMYS_STRICT=1 in the environment turns the guard off: hand in only
when `CRAMMYS_STRICT=1 $BPY -m tools.crammys_shots build --sky <each of your skies>` runs without a "!!!" line.
Scout with tools/crammys_shots.py / crammys_geo.py / crammys_palette.py (they write no meta.json). If you also
preview through render.py, use YOUR OWN sample count so no two directors share a preview directory
(out/preview/crammys/270x480_<N>spp): PREVIEW_SAMPLES below (gold 5, road 6, meadow 7, jukebox 9, finale 11).

THE SEQUENCE CONTRACT (what a sequence director may and must do)
  MAY   edit his own file only: the bodies of its shot functions, its docstrings, private helpers and constants.
        Make further twins of the shared cast with his own tags (C.actor("steve", "md2")). Add a film-local light
        with C.fill("<prefix>_<name>", ...) or C.kicker("<prefix>_<name>", s, at, watts) (the name starts with his
        prefix; it is on in the shots he names only). Move a camera of his own shots freely, unless the shot's
        docstring names a SHARED camera or place (SHARED below).
  MUST  keep every shot function's name and signature;
        give every shot a camera (C.cam: lens + move + focus + handheld; nothing is ever dead still; something
        already moving on its first frame: C.cam moves with ease "ease_out", at speed on frame 1), its cast
        (st.use: everybody else is hidden), what it is about (st.hero, inside x 8-82 %, y 14-60 % of the frame,
        clear of the caption band y 62-72 %) and its torch levels (C.lights once per shot: "gold" or "night");
        take characters only through C.actor(role, tag) with a tag that starts with HIS prefix (gd, rd, md, jb,
        fn), dropped items through C.item(item_id, tag) / C.disc_drop(...) / C.totem(s), held items through
        C.hold(p, item, s) (KEYED PER SHOT), the arrows in Steve through C.shoot_steve (md13) and C.arrows(steve, s)
        (md15 on): no
        other sequence can then disturb his keys, and nothing leaks into other shots;
        key each character in frame order; place() everybody on the first frame of a shot before any look_at()
        (look_at(f0, target, ease=0) BEFORE idle(): Character.idle puts a head key on its first frame);
        key nobody before a shot starts unless that instance is NOT in the shot before (pre-roll: use a twin);
        use the shared places, cameras and continuity rules where the plan names them (SHARED below), unchanged;
        keep Minecraft truth: players crouch (sneak), swing, look, jump, sprint, toot the horn; mobs move as their
        classes do (engine.hostiles / undead); nothing that is not a vanilla block, item, mob or particle; a held
        flat item shows its face only with C.present (the arm straight at the lens); a player within about one
        block of a dropped item collects it (keep feet 1.5 blocks or more from a disc or totem you want seen);
        render what he changed (tools/crammys_shots.py at 540x960, 16 samples) and LOOK at it; run
        tools/crammys_palette on one frame per shot.
  MUST NOT  touch films/crammys.py, this file, films/crammys_set.py, another sequence file or anything in engine/,
        render.py, tools/ (his own new tools/crammys_<seq>_*.py excepted); change the narration, the cuts, a sky or
        the film's length; make anything depend on which sky is being built (no `if sky ...`: every build keys the
        same things); call st.shot / st.sky_change / st.dip / st.finish (the film does); key hide_render on a
        character, its items, its arrows or a set part (st.use does it); call bd.last_lantern.place outside gd05,
        Jukebox.insert outside jb20, Jukebox.eject outside jb08, or Jukebox.play directly after jb20 (C.song does
        it); boost torches beyond LIGHTS without tools/palette_check (lit stone next to a lantern is at its limit);
        build a character with players.add_player / hostiles.add_creeper / undead.add_zombie directly (it would
        escape the twin rule); start a final render (render.py --frames without --res / --samples).
  If a shared place, camera or rule is wrong for his shot, he says so in his result; he does not change it.

LESSONS THAT EACH COST A RE-RENDER (The Hello, Leg Day; read them before the first still)
  - The head alone turns at most 70 degrees and pitches at most 35 (engine/characters.py clamps WITHOUT a warning):
    a look further than that needs the body: C.turn_to(p, f, target) = face() + look_at() (engine/music's work-
    around; present() for an arm). Looking down at a hand reads only with the hand held out (C.present).
  - Character.idle(f0, ...) puts a head key on f0: look_at(f0, ..., ease=0) BEFORE idle. place() every character on
    a shot's first frame before any look_at.
  - Something must already be moving on frame 1 of every shot (a pre-rolled twin, a camera at speed: C.cam's
    ease_out); nothing important in the last 3 frames before a cut; a word never straddles a cut (the plan is
    built so; tools/crammys_timeline --check proves it).
  - A small thing is seen only if it is in focus (the discs, the arrows, the totem, a note particle).
  - A step of less than 7 frames is a hop that stops dead (Character.walk is linear): use a low speed; two
    figures 0.2 block apart are one two-headed shape: stagger by 0.7 block.
  - Held items are keyed per shot (C.hold(p, item, s)); a hold without frame is for the whole film. C.hold's END is
    keyed when your shot function returns (build() calls C.close_holds), so a toot, a draw, an insert or a second
    hold in that hand after C.hold works as the engine documents it (the first skeleton keyed it at once: jb20's disc
    stayed in Steve's hand after the insert, Noor's gd01 horn reappeared from frame 86 to the end).
  - A players walk's end frame is the end of the game's FRICTION SLIDE (about 10 frames after the key is let go):
    to the eye he stops about 5 frames earlier. C.walk_lead(f0, arrive) places a walker (at speed on frame 1) so that
    he stops on a word; C.walk_frames(distance, f0) gives the stop frame of a walk.
  - A camera move that starts ON A WORD: C.cam(..., timing=C.timing_hold_move(a, b, f0=s.frame_start, creep=0.03))
    (held or creeping until a, the move a -> b 'smooth', held after b): fn24's pull back from "Best".
  - Particles live on across cuts (notes, the poof): the film calls C.time_jump at every change of sequence; inside
    a sequence a shot that jumps in time calls it itself before emitting its own.
  - A cut is only as good as the frames on both sides: look at the last frame of the shot before yours.
  - Lit stone next to a lantern sits on the palette limit: no lamp above LIGHTS (tools/crammys_palette).

SHARED (decided once, used by two shots or two sequences)
  CAMS["lane"]       rd07_chased and rd17_run_back, EXACTLY (position, aim, move, lens, f-stop; the road file's
                     LANE_FOCUS and handheld 0.004 in both): "the same camera as the zombie chase" (beat 17). 16 mm
                     from Kai's doorstep RAISED to z 3.1 (engine/music's 'lane' was at z 1.7: Kai's column hid the
                     chase; the story check). The road sequence's alone; ONE constant for both shots.
  THE ARROWS         beats 13 and 14 put two arrows in Steve (md13_shot: the skeleton shoots them with C.shoot_steve,
                     ARROW_HITS below: the chest, then the right shoulder, BOTH ALIGNED with their flight: the
                     shafts stick out toward his FRONT RIGHT, where the skeleton stood); from md15 to the end EVERY
                     Steve in the picture carries the same two: C.arrows(steve, s) (idempotent per twin). They stay
                     until the film ends (hostiles.hit until=None). They read best from his right side or front
                     right (in profile, the two fletchings as two crosses); from his left they hide behind him.
                     The lead's scout: crammys_scout_aligned_md13_shot_921 (both clear, his face free) against
                     crammys_scout_md13_shot_915 (the unaligned shoulder arrow lay across his face).
  THE DISC           music disc 11 (the broken one) drops where the creeper dies (md15, C.disc_drop: one item for
                     md15 and md16), is in Steve's right hand in rd17, jb18, jb19, jb20 (C.hold(steve,
                     "music_disc_11", s)) and goes into the jukebox in jb20 ON THE WORD "one" (INSERT below; the
                     disc leaves his hand one tick later, the first note one tick after the click).
  THE SONG           from the insert to the last frame the jukebox plays disc 11: one note every 24 frames in phase
                     with the insert. Every shot after jb20 that sees the jukebox calls C.song(s) (the notes born in
                     that shot, facing its camera); nobody else calls Jukebox.play after jb20.
  THE CAT DISC       Alex's green disc (music_disc_cat): played and ejected in jb08 (Jukebox.eject, the jukebox
                     sequence's), held by Alex in gd06 (the line) and jb20 (beside disc 11).
  THE TOTEM          on the pedestal's gold block (C.totem(s): the one dropped item, turning) in every shot that sees
                     the pedestal up to fn23; in Steve's right hand in fn24 (C.hold + C.present), the pedestal EMPTY.
  THE LAST LANTERN   placed ONCE, by Alex, in gd05 (bd.last_lantern.place(f, player=alex)); before that the north
                     post has none (gd01-gd04). If gd05 is a stand-in, build() places it on gd05's 0.9.
  THE DOOR           house_e (the narrator's) opens and shuts in rd07 only (v.door_open('house_e', f[, open=False]));
                     shut for the rest of the film.
  PLACES             the lead's own: zombie_stop (-2.85, 15.5: the foot of house_e's stairs; the set's B07_STOP was
                     inside them) and kai_lane (2.05, 16.85: Kai in the gap between his column and his post); and
                     every anchor of the set by name (C.P("ring_kai"), C.yaw("ring_kai")): the bandstand's (music: zuri,
                     kai, sunny, noor, alex_post, steve_front, line_1..5, three_*, ring_*, steve_jukebox, ...), the
                     lane's (lane_kai) and the meadow's (crammys_set MEADOW_ANCHORS without the prefix: middle,
                     creeper_line, skeleton_line, steve_shot, creeper_turn, ...). THE NIGHT STAGE LAYOUT (jb19 to fn24):
                     Steve at steve_jukebox, Alex Kai Zuri Sunny Noor at ring_<name> (Kai's step ends at kai_step):
                     the same spots in every shot, so the cuts match.
  The skies (films/crammys.py SKIES), the light recipes LIGHTS, ARROW_HITS / ARROW_SCALE, INSERT.
  Every other camera is a constant of its sequence file, given whole to C.cam(s, None, **CAM) (the set builder's
  suggestion for each beat is C.cam(s, "set:b05"): a start, measured on stills, never final).

Coordinates: Blender blocks, +X east, +Y north, +Z up; ground 0.0, dirt path -1/16, the stage floor z 1.0.
THE BANDSTAND (engine/music.py) on the west side of the square, facing WEST down the west street (the cameras stand
west of it looking east): red wool platform x -8..-5, y -3..5, top z 1; back wall x -4; the front row of note blocks
at x -8 (Sunny's on a pumpkin y -2, Kai's on gold y 1, Zuri's on white wool y 2, dressing at -1, 4, 5); the jukebox
cell (-7, 0, 1) behind the gap at y 0 (its top, the slot, reads only from 0.8 block above it within 4 blocks); lantern
posts (-8, -3) and (-8, 3) (the north one gets its lantern in gd05); the pedestal (oak fence + gold block) at (-9, -1),
its top (-8.5, -0.5, 2.0); the village lamp post at (-17.3 / -15.7, 2.5) stands in the corridor before the stage.
THE LANE: Kai's gold + note block column (1, 15), his lantern post (1, 17), house_f's door (4.5, 16.5); the
narrator's door house_e (-4.5, 15.5) across the exit road (x -1..1). THE EXIT GATE: lamp posts (-3, 24), (3, 24).
THE NIGHT MEADOW north of the gate: flat grass to y 50; the line of beat 12 at y 40 (creeper 1.8, Steve 5.0,
skeleton 8.2); the skeleton's oak at (13, 44). Everything else: films/crammys_set.py (its docstring).
"""
import math

from mathutils import Vector

from engine import fx, hostiles, mobs, music, players, undead
from films import crammys_set as CS
from films import lookdev as L

FPS = 24
PATH_Z = -0.0625                       # a dirt path lies one pixel below the grass
FINAL_RES, FINAL_SAMPLES = (540, 960), 16      # this film's final quality (set on the scene by films/crammys.py)

SEQUENCES = {"gd": "gold", "rd": "road", "md": "meadow", "jb": "jukebox", "fn": "finale"}
PREFIX = {v: k for k, v in SEQUENCES.items()}
PREVIEW_SAMPLES = {"gold": 5, "road": 6, "meadow": 7, "jukebox": 9, "finale": 11}     # one preview directory each


def build_set(scene):
    """The village of "The Crammys": seed 1 with films/crammys_set.py built in (bandstand, lane, night meadow)."""
    return CS.build_set(scene)


# ----------------------------------------------------------------------------------------------------------------
# places: any anchor name of the set (CS.anchors(v): the bandstand's, the lane's, the meadow's without 'crammys_'),
# or (x, y) = on the ground there, (x, y, z) = exactly there. C.P(name) gives a 3D point, C.yaw(name) its facing.
# ----------------------------------------------------------------------------------------------------------------
PLACES = {
    # the lead's own names for spots two shots share (each is an anchor of the set)
    "steve_center": "steve_jukebox",        # the night stage: Steve at the jukebox's south-east corner (jb19-fn24)
    # rd07: the zombie stops at the foot of the narrator's door step (the set builder's B07_STOP (-3.45, 15.5) is
    # inside the cobblestone stairs at (-4, 15): this is in front of them, on the dirt path)
    "zombie_stop": (-2.85, 15.5),
    # rd07: Kai on his doorstep in the gap between his gold / note block column (1, 15) and his lantern post (1, 17),
    # 0.4 block west of engine/music's lane_kai: further from the raised lane camera, his head higher in its frame
    "kai_lane": (2.05, 16.85),
}
NIGHT_STAGE = ("alex", "kai", "zuri", "sunny", "noor")        # at ring_<name> from jb19 (Alex from jb20's end) to fn24

# ----------------------------------------------------------------------------------------------------------------
# cameras: name -> dict(pos, target, lens, fstop[, pos1, target1]); C.cam(s, name) puts one on a shot
# ----------------------------------------------------------------------------------------------------------------
def _set_cam(beat, **over):
    """The set builder's suggested camera for a beat (CS.CAMERAS) as a CAMS entry (without its bookkeeping)."""
    c = {k: v for k, v in CS.CAMERAS[beat].items() if k in ("pos", "target", "pos1", "target1", "lens", "fstop")}
    c.update(over)
    return c


CAMS = {
    # rd07_chased and rd17_run_back, EXACTLY: 16 mm f/2.8 from Kai's doorstep looking west down the lane at the
    # narrator's door (house_e), RAISED to z 3.1 over Kai's gold / note column (engine/music's 'lane' camera was at
    # z 1.7: the column hid the road between y 14.4 and 15.9, so in the first stub Steve and the zombie were never
    # seen running: the story check). From here a runner on the WEST side of the road (x -1.5) is seen eyes and chest
    # from x 5 % to the door (x 50 %); Kai's head sits low (x 58-85 %, y 62-82 %: in the caption band; the back of
    # his head), his lantern at the right edge, the column at the left (films/crammys_road.py: THE LANE CAMERA).
    "lane": dict(pos=(3.84, 16.5, 3.1), target=(-4.5, 15.3, 0.8), pos1=(3.84, 16.42, 3.06),
                 target1=(-4.5, 15.25, 0.8), lens=16.0, fstop=2.8),
    # the stand-ins of a failed shot (films/crammys.py STAND_IN), one per place
    "gold_wide": _set_cam("b04"),
    "gate": _set_cam("b09"),
    "meadow_line": _set_cam("b12"),
    "jukebox": _set_cam("b21"),
    "stage_wide": _set_cam("b22"),
}

# torch / lantern levels (C.lights(s, key)): the music proofs' and the set builder's levels, every still checked by
# tools/palette_check. Never raise the bandstand's lanterns above 1.6 (the well's cobblestone behind the wall).
LIGHTS = {
    "gold": dict(scale=CS.GOLD_TORCHES),       # 1.0: daylight, every lamp at its own level
    "night": dict(scale=CS.NIGHT_TORCHES),     # 1.3: the look-dev night level (stage, lane, gate and meadow alike)
}

# ----------------------------------------------------------------------------------------------------------------
# continuity: the arrows, the disc, the song
# ----------------------------------------------------------------------------------------------------------------
# THE TWO ARROWS of beats 13 and 14 (md13_shot shoots them with C.shoot_steve: sk.shoot(f, steve, **ARROW_HITS[n],
# knockback=0.1, scale=ARROW_SCALE), and every later Steve twin gets the same two from C.arrows). BOTH ARE ALIGNED
# with their flight (the shaft back toward the skeleton, which stood 45 degrees to his front right: films/crammys_set.py
# ARROW_FLIGHT): the unaligned "chest" spot points 24 degrees up and, from a lens beside the line of fire, put the
# fletching over his mouth (the set builder: crammys_set_b13_shot.png, first pass); the unaligned "shoulder_r" spot
# points mostly UP and its shaft and fletching lay across his face (the lead's scout:
# out/test/crammys_scout_md13_shot_915_zones.png, and the set builder's b14: "its shaft crosses his right eye"). The
# spots stay hostiles' "chest" and "shoulder_r" (the skeleton stands on his right in beats 12-14).
ARROW_HITS = (dict(part="chest", align=True), dict(part="shoulder_r", align=True))
ARROW_SCALE = 1.0                      # one size in every shot (they are the same two arrows); the story's
#                                        fallback "a quarter larger in the wides" would change them between cuts
# THE INSERT: Steve puts disc 11 into the jukebox ON the caption frame of this word (jb20): the arm swing on it, the
# disc gone one tick later, the first note one tick after the click; THE SONG runs from there to the film's end
INSERT = ("jb20_eleven", "one")
SONG_DISC = "music_disc_11"


# role -> skin (engine.players; Alex is the slim model, as in the game)
ROLES = {"steve": "steve", "alex": "alex", "zuri": "zuri", "kai": "kai", "sunny": "sunny", "noor": "noor"}
MOBS = ("zombie", "creeper", "skeleton")


def yaw_to(src, dst):
    """Yaw that makes a character at src (facing -Y at yaw 0) face dst."""
    return L.yaw_to(src, dst)


def _end_hold(p, held, end):
    """End one engine.players held item on `end` (its model variants off from there), leaving every other hold of
    that hand alone (Player.hold(None, frame) also ends holds that start after `frame`)."""
    held.end = int(end)
    for att in held.variants.values():
        att.set(int(end), False)
    p._refresh()


class ShotInfo:
    """One row of the film's shot plan with its frames: C.T[shot name].

    name, beat, beats (every beat it carries: md13_shot (13, 14)), sequence, sky, sentence (the engine.narration
    Sentence spoken first in the shot), frame_start, frame_end (inclusive), frames, seconds, words = [(caption,
    frame it appears on)], change / sky_after (a sky change inside the shot: none in this film), dip = True when
    the encoder dips to black on the shot's first frame, prev / next = the neighbouring shots' names (or None)."""

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


class Crammys:
    """The film's shared context, handed to every shot function as C.

    C.st / C.v / C.A / C.Y   the Stage, the Village, every anchor of the film (3D point) and its yaw (or None)
    C.bd                     the music.Band: C.bd.notes['zuri' | 'kai' | 'sunny' | 'row_1..3' | 'lane'] (NoteBlock:
                             tap / song / played), C.bd.jukebox, C.bd.last_lantern, C.bd.kicker, C.bd.pedestal_top
    C.parts                  films/crammys_set.make_parts(v) (band, notes, jukebox, last_lantern, totem, door, oak)
    C.nar, C.T               the Narration; the shot plan: C.T["md13_shot"] -> ShotInfo
    C.P(name) / C.yaw(name)  a place (PLACES or any anchor name) as a 3D point / the set's facing of it
    C.cam(s, name, ...)      one of CAMS, the set builder's "set:b05", or None + a whole spec
    C.actor(role, tag)       a player (steve alex zuri kai sunny noor) or a mob (zombie creeper skeleton), built
                             once per tag
    C.item(id, tag)          a dropped item, registered like a cast member
    C.hold(p, item, s, hand) an item in p's hand for shot s only (engine/music hold, keyed on its first frame)
    C.present(p, s, target, f0=None, f1=None, ease=0)    the arm held straight out at target (a flat item's face)
    C.turn_to(p, f, target, ease)    body AND head toward target (the head alone stops at 70 degrees)
    C.shoot_steve(sk, steve, f, n, release=)    md13 only: the skeleton's arrow n (0 chest, 1 shoulder) into him
    C.arrows(steve, s)       the two arrows of beats 13-14 in this Steve from shot s on (beat 15 onward)
    C.disc_drop(feet, frame, until, tag, face)   disc 11 dropped by the dying creeper (md15; md16 uses the same one)
    C.totem(s)               the totem turning on the pedestal in shot s
    C.insert_frame() / C.song(s[, end])   the frame disc 11 goes in (jb20 "one") / the jukebox's notes in shot s
                             after it (none born in the shot's last 7 frames: a note would float into the next shot)
    C.walk_frames / C.walk_lead     a players walk's stop frame / where to start one to stop on a frame
    C.timing_hold_move(a, b)  a camera clock for C.cam(..., timing=): held, the move a -> b, held
    C.close_holds()          (the film calls it after each shot function: the ends of that shot's C.hold calls)
    C.lights(s, key)         the torch levels ("gold" / "night") through Band.lights (the placed lantern included)
    C.fill / C.kicker        film-local lights for the shots named (name starts with your prefix)
    C.shots, C.memo          every Shot of the film by name; a dict for handing things from one shot function to a
                             later one of the SAME sequence (key prefixed with it: C.memo["md_disc"])
    """

    def __init__(self, st, nar=None, timeline=None):
        self.st, self.v = st, st.v
        self.anchors = CS.anchors(self.v)                       # key -> (point, yaw or None)
        self.A = {k: tuple(p) for k, (p, _y) in self.anchors.items()}
        self.Y = {k: y for k, (_p, y) in self.anchors.items()}
        self.parts = CS.make_parts(self.v)
        self.bd = self.parts.band
        self.set = self.v.sets["crammys"]
        self.nar = nar
        self.T = dict(timeline or {})
        self.shots = {}            # shot name -> engine.shots.Shot (filled by films/crammys.py before any function)
        self.memo = {}             # what one shot function leaves for a later one of ITS OWN sequence
        self._fills = {}
        self._arrowed = set()      # names of the Steve twins that carry the two arrows already
        self._totem = None
        self._holds = []           # C.hold calls whose end is keyed when the shot function returns (close_holds)

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
        """A named place (PLACES, or any anchor of the film) as a 3D point (2D entries are put on the ground)."""
        p = PLACES.get(name, name)
        if isinstance(p, str):
            return tuple(self.A[p])
        return self.stand(p)

    def yaw(self, name, default=0.0):
        """The facing the set gives an anchor, or `default`."""
        p = PLACES.get(name, name)
        y = self.Y.get(p) if isinstance(p, str) else None
        return default if y is None else y

    def eyes(self, name, height=1.62):
        """A point at a standing player's eye height over a place (a look target)."""
        p = self.P(name)
        return (p[0], p[1], p[2] + height)

    def camera_spec(self, name):
        """CAMS[name], the set builder's suggestion "set:b05" (CS.CAMERAS), or {} for None (a shot's own camera,
        given whole to C.cam as keywords)."""
        if name is None:
            return {}
        if name.startswith("set:"):
            return _set_cam(name[4:])
        return dict(CAMS[name])

    def cam(self, s, name, focus=None, handheld=0.006, seed=None, move=True, ease="ease_out", timing=None, **over):
        """Put a camera on shot s: lens, position / aim (with its move when it has one and move=True), focus
        (default: its target) and a gentle handheld. name = one of CAMS (a shared camera), "set:bNN", or None: the
        shot's OWN camera, a constant of its sequence file given whole as keywords (pos, target, lens[, fstop,
        pos1, target1]: C.cam(s, None, focus=steve.head, **GD01_CAM)). over = entries to replace or give. ease: of
        the move; default 'ease_out' = AT SPEED ON THE FIRST FRAME, slowing to the last (engine.shots' own default
        'smooth' starts from rest: a still for the first half second). 'linear' for a constant drift / track.
        timing: a function frame -> fraction of the move (0..1) that REPLACES the shot's even clock and `ease`
        (C.timing_hold_move builds one: a creep, the move between two frames, a hold): a move that starts on a
        word. The handheld seed is the shot name's. Returns the spec used."""
        c = dict(self.camera_spec(name), **over)
        if "pos" not in c or "target" not in c or "lens" not in c:
            raise KeyError("camera %r for %s needs pos, target and lens" % (name, s.name))
        if timing is not None:
            # engine.shots Shot keys the camera on every frame at ease(s._u(frame)): this shot's own clock instead
            # (an instance attribute; the engine file is untouched)
            s._u = lambda frame, _t=timing: min(1.0, max(0.0, float(_t(frame))))
            ease = "linear"
        s.lens(c["lens"], c.get("fstop", 2.8))
        if move and ("pos1" in c or "target1" in c):
            s.move(c["pos"], c["target"], c.get("pos1", c["pos"]), c.get("target1", c["target"]), ease=ease)
        else:
            s.move(c["pos"], c["target"])
        s.focus(focus if focus is not None else c["target"])
        if handheld:
            s.handheld(handheld, seed=sum(ord(ch) for ch in s.name) % 89 if seed is None else seed)
        return c

    @staticmethod
    def timing_hold_move(a, b, f0=None, creep=0.0, ease="smooth"):
        """A camera clock for C.cam(..., timing=): from the shot's first frame f0 to frame `a` a slow linear creep
        (`creep` of the move: 0 = held still), from `a` to `b` the rest of the move with `ease` ('smooth': from
        rest to rest), held after `b`. fn24: hold on Steve and the totem through "I won Best", pull back from
        rest on "Best", settle before the last 1.5 s."""
        from engine.shots import EASES
        fn = EASES[ease]
        a, b = float(a), float(b)
        start = a if f0 is None else float(f0)

        def t(frame):
            if frame <= a:
                return creep * (frame - start) / max(1.0, a - start) if frame > start else 0.0
            if frame >= b:
                return 1.0
            return creep + (1.0 - creep) * fn((frame - a) / (b - a))
        return t

    # ------------------------------------------------------------------ the cast
    @staticmethod
    def _check_tag(tag):
        if tag[:2] not in SEQUENCES:
            raise KeyError("tag %r must start with a sequence prefix: %s" % (tag, ", ".join(SEQUENCES)))

    def actor(self, role, tag):
        """The cast member "<role>_<tag>", built on first use and registered with the Stage (st.cast).

        role   steve                    the narrator (players 'steve', wide arms): empty hands, no armor, no sword
               alex zuri kai sunny noor the musicians (engine.players skins; Alex on the slim model, as in the game)
               zombie                   engine.undead's zombie (aggro(f) = arms out; walk at 2.33 blocks/s)
               creeper / skeleton       engine.hostiles (place first, then step / fuse / aim / draw / shoot)
        tag    starts with your sequence prefix (gd, rd, md, jb, fn); a further twin is just another tag:
               C.actor("steve", "md"), C.actor("steve", "md2").
        Twins exist because a character that is in two consecutive shots cannot be keyed before the second one
        starts: whoever must already be moving on the first frame of a shot (pre-rolled) is a twin that is not in
        the shot before. From beat 15 on, every Steve in the picture needs C.arrows(steve, s)."""
        self._check_tag(tag)
        if role not in ROLES and role not in MOBS:
            raise KeyError("no role %r (roles: %s)" % (role, ", ".join(list(ROLES) + list(MOBS))))
        name = "%s_%s" % (role, tag)
        c = self.st.cast.get(name)
        if c is not None:
            return c
        if role == "zombie":
            return undead.add_zombie(self.st, name)
        if role == "creeper":
            return hostiles.add_creeper(self.st, name)
        if role == "skeleton":
            return hostiles.add_skeleton(self.st, name)
        return players.add_player(self.st, name, ROLES[role])

    def item(self, item_id, tag):
        """A dropped item of engine.mobs, registered with the Stage like a cast member: it = C.item("music_disc_11",
        "md"); it.place(f0, pos); it.face(f0, lens); it.animate(f0, s.frame_end + 1); st.use(s, it)."""
        self._check_tag(tag)
        name = "%s_%s" % (item_id, tag)
        it = self.st.cast.get(name)
        if it is None:
            it = self.st.cast[name] = mobs.make_dropped_item(item_id, name=name)
        return it

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

    # ------------------------------------------------------------------ acting the story needs more than once
    def hold(self, p, item, s, hand="right", frame=None, until=None):
        """An item in p's hand in shot s only: engine/music hold (block items drawn as the game draws a block in a
        hand; discs, horn, totem as flat sprites along the hand) KEYED on the shot's first frame (or `frame`), and
        emptied on `until` (default: the frame after the shot). Returns the item object (a focus target). Call it
        after p.place() on the same frame. KEY HOLDS PER SHOT: a bare players hold without a frame is for the whole
        film.

        THE END IS KEYED WHEN YOUR SHOT FUNCTION RETURNS (films/crammys.py build() calls C.close_holds after each
        one), not here: everything the shot does with that hand after C.hold works as the engine documents it:
        Jukebox.insert and LastLantern.place empty the hand on their own frame (that end then stands), toot /
        draw_bow / block switch the item's model and back, a second C.hold (or players hold) in the same hand
        replaces it on its own frame. An end keyed at once (the first version of this helper) made the players
        rig skip every later hand change in the shot: in jb20 disc eleven stayed in Steve's hand after the insert
        to the cut, and Noor's toot in gd01 left her horn on from frame 86 to the film's end (the technical
        review, measured)."""
        f = s.frame_start if frame is None else int(frame)
        end = s.frame_end + 1 if until is None else int(until)
        side = "l" if str(hand).lower().startswith("l") else "r"
        ob = music.hold(p, item, hand=hand, frame=f)
        held = p._hands[side][-1] if getattr(p, "_hands", None) else None
        if held is not None:
            self._holds.append((p, hand, held, end))
        return ob

    def close_holds(self):
        """Key the end of every C.hold of the shot just built (films/crammys.py calls it after each shot function).
        A hold that something in the shot ended EARLIER (an insert; a later hold in that hand) keeps that end; one
        that a later hold ended after the `until` asked for is cut back to it. Returns how many it closed."""
        n = 0
        for p, hand, held, end in self._holds:
            side = "l" if str(hand).lower().startswith("l") else "r"
            if held.end is None:
                later = [h for h in p._hands[side] if h is not held and h.end is None and h.start is not None
                         and h.start >= end]
                if not later:
                    p.hold(None, hand=hand, frame=end)          # the engine's own way (it also lowers the arm)
                else:                                           # (p.hold(None) would also end those later holds)
                    _end_hold(p, held, end)
                n += 1
            elif end < held.end:
                _end_hold(p, held, end)
                n += 1
        self._holds = []
        return n

    @staticmethod
    def present(p, s, target, f0=None, f1=None, hand="right", ease=0):
        """The arm held straight out at `target` (the lens: a point) from f0 to f1 (default: the whole shot), so a
        flat item in that hand shows the lens its FACE (engine/music present: a film gesture, as the story asks
        in beats 6, 20 and 24). ease=0 when the shot opens on the raised arm (a cut), else the frames it rises."""
        a = s.frame_start if f0 is None else int(f0)
        b = s.frame_end if f1 is None else int(f1)
        return music.present(p, a, b, target, hand=hand, ease=ease)

    @staticmethod
    def turn_to(p, frame, target, ease=10, head_ease=None):
        """Body AND head toward `target` from `frame` (Character.face + look_at): the head alone stops at 70
        degrees of yaw (engine/characters.py, no warning), so a look further round needs the body (engine/music's
        work-around in beat 8)."""
        p.face(frame, target, ease=ease)
        p.look_at(frame, target, ease=ease if head_ease is None else head_ease)
        return frame + ease

    @staticmethod
    def walk_frames(distance, frame, speed=None, ramp=(False, True)):
        """The frame a players walk of `distance` blocks started on `frame` ends on (engine.players Player.walk's own
        step arithmetic: the game's speed per tick, its ground friction on a ramp; default speed: the walk, 4.317
        blocks/s; players.SPRINT_SPEED to sprint). ramp=(False, True): at speed on the first frame, sliding to a
        halt at the end (a player already walking when the shot starts)."""
        speed = players.WALK_SPEED if speed is None else float(speed)
        ramp_in, ramp_out = (bool(ramp), bool(ramp)) if isinstance(ramp, (bool, int)) else ramp
        v, g = speed / 20.0, players.GROUND_FRICTION
        n, acc, d = 0, 0.0, (0.0 if ramp_in else v)
        while n < 100000:
            d = g * d + (1.0 - g) * v if ramp_in else v
            tail = d * g / (1.0 - g) if ramp_out else 0.0
            if acc + d + tail >= distance:
                break
            n += 1
            acc += d
        n += 1
        while ramp_out and d > 0.004:
            d *= g
            n += 1
        return int(math.ceil(frame + n * players.TICK - 1e-9))

    @classmethod
    def walk_lead(cls, frame, arrive, speed=None, ramp=(False, True)):
        """The distance a player walking from `frame` (at speed on it: ramp=(False, True)) covers when he stops ON
        `arrive`: where to place him on frame 1 so that he arrives on a word (md12: on "middle"). The stop frame
        is the END OF THE GAME'S FRICTION SLIDE (about 8 ticks = 10 frames after the walk key is let go, the speed
        halving each tick): to the eye he has stopped about 5 frames earlier. An `arrive` sooner than the shortest
        walk (one step at speed and the slide: about 0.45 block, 11 frames) gives that shortest walk."""
        speed_t = (players.WALK_SPEED if speed is None else float(speed)) / 20.0
        g = players.GROUND_FRICTION
        lo, hi = speed_t * (1.0 + g / (1.0 - g)), 40.0          # one step at speed + the slide (the shortest walk)
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if cls.walk_frames(mid, frame, speed, ramp) <= arrive:
                lo = mid
            else:
                hi = mid
        return lo

    @staticmethod
    def clap(p, frame, count=6, every=4, down=2):
        """The players' applause (engine/music clap: fast crouches)."""
        return music.clap(p, frame, count=count, every=every, down=down)

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

    # ------------------------------------------------------------------ continuity
    def arrows(self, steve, s):
        """The two arrows of beats 13 and 14 in this Steve twin from shot s's first frame on (to the film's end):
        for every shot from md15 on (md13_shot shoots its own with ARROW_HITS): hostiles.hit with ARROW_HITS, both
        aligned with md13's flight as it lies in his own frame (the set's ARROW_FLIGHT; the set's CS.arrows aligns
        only the chest one). Idempotent per twin: the first call
        (in timeline order, the earliest shot) puts them in; later calls do nothing. Call it after his place() on
        the shot's first frame (the chest arrow is aligned with his yaw on that frame)."""
        if steve.name in self._arrowed:
            return False
        self._arrowed.add(steve.name)
        f = s.frame_start
        flight = CS.arrow_direction(steve, f)          # md13's flight in his own frame (ARROW_FLIGHT), turned with him
        for spec in ARROW_HITS:
            kw = dict(spec)
            hostiles.hit(steve, f, hurt=False, scale=ARROW_SCALE, direction=flight if kw.get("align") else None, **kw)
        return True

    def shoot_steve(self, sk, steve, frame, n, release=None, **kw):
        """Beats 13-14 (md13_shot ONLY): the skeleton's n-th arrow into this Steve (0 = the chest, aligned with its
        flight; 1 = the right shoulder): sk.shoot(frame, steve, release=release, **ARROW_HITS[n], knockback=0.1,
        scale=ARROW_SCALE, **kw) (a draw from `frame`, loosed on `release`, default frame + 24; it sticks 2-3 frames
        later). The twin then counts as carrying the arrows: C.arrows does nothing more on it. Returns the Flight
        (int(flight) = the impact frame)."""
        spec = dict(ARROW_HITS[n])
        spec.update(knockback=0.1, scale=ARROW_SCALE)
        spec.update(kw)
        fl = sk.shoot(frame, steve, release=release, **spec)
        self._arrowed.add(steve.name)
        return fl

    def disc_drop(self, feet, frame, until, tag="md", face=None, seed=5):
        """Disc 11 as the creeper drops it when the skeleton's arrow kills it (music.creeper_disc: spawned ON the
        killing-blow frame at its feet, the item toss, landing on the terrain, then turning and bobbing) until
        `until`; registered with the Stage as "crammys_disc_<tag>" (st.use it in every shot it is seen in). The
        same tag returns the same item (md15 drops it, md16 uses it: C.disc_drop is called once, in md15; md16 gets
        it from C.memo). face = the point (a lens) it faces on landing. .rest_pos / .land_frame for the camera."""
        self._check_tag(tag)
        name = "crammys_disc_%s" % tag
        d = self.st.cast.get(name)
        if d is None:
            d = music.creeper_disc(tuple(feet), frame, disc="music_disc_11", seed=seed, world=self.v,
                                   until=until, name=name, face=face)
            self.st.cast[name] = d
        return d

    def totem(self, s):
        """The totem of undying on the pedestal's gold block, turning and bobbing, in shot s (music Band.totem: one
        dropped item for the whole film, placed again per shot; registered and st.use'd here). Every shot that sees
        the pedestal up to fn23 calls it; fn24 does NOT (the pedestal is empty, Steve holds it)."""
        t = self.bd.totem(s.frame_start, s.frame_end + 1)
        if t.name not in self.st.cast:
            self.st.cast[t.name] = t
        self.st.use(s, t)
        return t

    def insert_frame(self):
        """The frame Steve puts disc 11 into the jukebox (INSERT: the caption frame of "one" in jb20)."""
        return int(self.T[INSERT[0]].at(INSERT[1]))

    def song_note_frames(self, a, b):
        """The frames of THE SONG's notes between a and b (inclusive): first note one tick after the insert, then
        one every 24 frames (JukeboxSongPlayer: every 20 ticks)."""
        first = self.insert_frame() + music.TICK
        step = music.JUKEBOX_EVERY_TICKS * music.TICK
        k = max(0, int(math.ceil((a - first) / step - 1e-9)))
        out = []
        f = first + k * step
        while f <= b + 1e-6:
            out.append(f)
            f += step
        return out

    def song(self, s, seed=None, end=None):
        """THE SONG's notes born inside shot s (after the insert), facing s's camera: Jukebox.play over the notes of
        song_note_frames(s.frame_start, end), in phase with the insert. end (default: the shot's end less a note's
        life, 6 ticks = 7.2 frames): no note is born that would still be in the air at the cut (a particle lives on
        across a cut facing the old camera; the technical review found fn22's last note, born on 1393, in fn23's
        first 6 frames). So fn22 has notes on 1345 and 1369, not 1393. Returns the note frames."""
        last = s.frame_end + 1 - music.NOTE_LIFETIME * music.TICK if end is None else float(end)
        frames = self.song_note_frames(s.frame_start, last)
        if not frames:
            return []
        jb = self.bd.jukebox
        return jb.play(frames[0], last, disc=SONG_DISC, camera=s,
                       seed=(sum(ord(ch) for ch in s.name) % 97) if seed is None else seed, first=True)

    # ------------------------------------------------------------------ light
    def lights(self, s, key="night", at=None, **over):
        """The torch levels of LIGHTS[key] ("gold" or "night") for shot s, through music.Band.lights (Stage.lights +
        the placed last lantern). over = Stage.lights / Band.lights arguments to replace (near=, radius=, stage=,
        lane=, extra=[(point, k)]: only with tools/crammys_palette)."""
        kw = dict(LIGHTS[key], **over)
        if isinstance(kw.get("near"), str):
            kw["near"] = self.P(kw["near"])
        self.bd.lights(self.st, s, at=at, **kw)

    def fill(self, name, pos, watts, shots, color=(1.0, 0.98, 0.95)):
        """A film-local SHADOWLESS fill light (props.make_light("fill")) that is on in the given shots only and
        hidden everywhere else (a hidden object is in no frame's stamp). `shots` = Shots and / or (first frame,
        last frame) spans. The NAME starts with your sequence prefix ("md_moon": KeyError otherwise), and one name
        = one light: calling it again with the same name adds shots, and raises ValueError if pos, watts or color
        differ. A cool moon fill: color=CS.MOON_KEY_COLOR."""
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
            lamp.name = "crammys_fill_" + name
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

    def kicker(self, name, s, at, watts=30.0, color=(1.0, 0.86, 0.66)):
        """A film-local warm practical (music Band.kicker: a lantern-type point light with soft shadows) that only
        shot s sees: beat 8's fill on Steve's turned face (music: bd.A['steve_turn_kicker_target'], 30 W). The name
        starts with your prefix."""
        if name[:2] not in SEQUENCES:
            raise KeyError("kicker name %r must start with your sequence prefix: %s" % (name, ", ".join(SEQUENCES)))
        return self.bd.kicker(self.st, s, at, watts=watts, color=color, name="crammys_kicker_" + name)

    # ------------------------------------------------------------------ time jumps
    @staticmethod
    def time_jump(frame):
        """End every particle still in the air on `frame` (engine.fx.stop_particles): the film calls it at every
        change of sequence. Inside a sequence a shot that jumps in time calls it itself BEFORE emitting its own
        (md15 -> md16 do NOT: "the smoke thins")."""
        return fx.stop_particles(int(frame))

    # ------------------------------------------------------------------ words
    def words(self, s):
        """[(caption, frame)] of the words spoken in shot s (also C.T[s.name].words)."""
        return list(self.T[s.name].words)

    def at(self, s, word, n=0):
        """Frame on which the n-th `word` of shot s appears."""
        return self.T[s.name].at(word, n)


# re-exported for the sequence files (one import line): from films.crammys_common import CS, music, hostiles, ...
__all__ = ["CS", "music", "hostiles", "players", "undead", "mobs", "Crammys", "CAMS", "PLACES", "LIGHTS",
           "ARROW_HITS", "ARROW_SCALE", "INSERT", "NIGHT_STAGE", "yaw_to"]
