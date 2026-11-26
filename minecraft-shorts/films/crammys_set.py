"""THE SETS OF "THE CRAMMYS" (stories/crammys.json): a film-local set module, built INTO the seed-1 village through
village.build_village(edit=...) exactly as engine/sets.py builds hello_set. Nothing in engine/ is changed.

    from films import crammys_set as CS
    v = CS.build_set(scene)                 # = village.build_village(scene, seed=1, edit=CS.crammys_set)
    P = CS.make_parts(v)                    # band, notes, jukebox, last_lantern, totem, door 'house_e', oak (AFTER the build)
    A = CS.anchors(v)                       # every named place: key -> (point, yaw) (bandstand, lane, meadow)
    CS.SKIES                                # the two skies the stills were made under (copy into films/crammys.py)
    CS.CAMERAS["b11"]                       # a suggested camera per beat: dict(pos, target, lens, fstop[, pos1, target1,
                                            #   focus], sky, what); still out/test/crammys_set_<beat>_<what>.png (+ _zones)
    CS.arrows(steve, f)                     # the two arrows of beats 13 / 14, already in him (stills of later beats)
    CS.moon_key(st, shot, at, watts)        # a film-local shadowless cool light that only `shot` sees (not needed so far)

    $BPY -m films.crammys_set               # the self-test (numbers, ~10 s): standing anchors on solid ground with the
                                            #   body free, path nodes free, every camera (pos, pos1) outside every
                                            #   block and above the ground, the oak, the beat-12 line vs the fuse range
    $BPY -m films.crammys_set b11 b12 ...   # the proof stills of these beats (one fresh build each, 540x960, 16
                                            #   samples, 2 threads, zones, tools/palette_check; 80-140 s each on the
                                            #   shared machine: two per call under `timeout 290`)
    $BPY -m films.crammys_set b07 --frames 34 --res 270x480 --samples 8     # other frames / quick framing tests
    CRAMMYS_CAMS='{"b11": {"lens": 35}}' CRAMMYS_SKIES='{"night": {"az": 176}}' ...    # scouting overrides
    $BPY -m films.crammys_set view NAME x,y,z tx,ty,tz LENS [FSTOP SKY WxH SAMPLES]   # a plain view, no cast

THE SKIES (Blender azimuth: degrees counter-clockwise from east)
    gold   dict(preset="golden", az=240, el=27, bloom=1.0, grade="warm")   beats 1-6: engine/music.py's own golden
           sky (sun in the south-west, in front of the west-facing stage, 120 degrees off the stage cameras).
    night  dict(preset="night", az=0, el=21, bloom=1.3, grade="cool")      beats 7-24, ONE moon for the whole night.
           THE MOON IS DUE EAST, low: on the game's own east-west arc, opposite the sun that has just set (the
           music module's proofs had it in the west, az 176: a moon about to set, and with it beat 11's "moon
           behind the branches" needs the skeleton's oak west of the line, on the creeper's side). What it does:
             - the bandstand faces west: the moon stands BEHIND it, over the well, and the stage front is in the
               well's moonshadow. The lanterns are the key on every face (palette_check passes on every night stage
               still: lit stone G/R 0.96-0.97, Steve's trousers min channel 14-51), the sky behind the stage is the
               bright side of the night gradient and in the frontal wide (b22) the MOON STANDS OVER THE BANDSTAND
               (x 62 %, y 16 %); in b24's first frame it is at the top edge.
             - the lane (beats 7, 17): the camera looks west, the moon is behind it: house_e's front is moonlit.
             - the meadow: cameras look north (beats 9, 10, 12, 15): the moon at their right, out of frame; figures
               side-lit, standing against the northern sky. Beat 11 looks EAST: the moon peeks from under the edge of
               the skeleton's oak (the story's "moon behind the branches"), see b11.
           Compared with the music module's own night proofs under the west moon (out/test/music_cams_night.png):
           the stage is darker around the faces and warmer; the same faces read. Haze: the preset's (0.45): the
           meadow's far rises fade into a mauve band, the figures at 8-13 blocks stay crisp. No second night entry
           is needed.
    Torches: Band.lights(st, s, scale=1.0) at gold, scale=NIGHT_TORCHES (1.3) at night (the music proofs' levels;
    the meadow shots too: the exit gate's lamps light beat 9, the others are 15+ blocks away). Never above 1.6 near
    the well's cobblestone (music GOTCHAS).

WHERE EVERY BEAT IS FILMED (Blender blocks: +X east, +Y north, +Z up; ground z 0; stage floor z 1; path 1/16 lower)
    THE BANDSTAND (engine/music.py: west side of the square, facing west down the west street), beats 1-6 gold,
    8 and 18-24 night: the red wool platform x -8..-5, y -3..5; back wall x -4; the front row of note blocks at
    x -8 (Sunny's on a PUMPKIN at y -2, Kai's on GOLD at y 1, Zuri's on WHITE WOOL at y 2, dressing at -1, 4, 5);
    the jukebox (-7, 0, 1) behind the gap at y 0; lantern posts (-8, -3) and (-8, 3) (the north lantern is placed
    on camera in beat 5: P.last_lantern); wall lanterns (-4, +-3, 4); the trophy pedestal (oak fence + gold block)
    at (-9, -1), its top (-8.5, -0.5, 2.0). Unchanged from engine/music.py.
    THE LANE (engine/music.py lane_set), beats 7 and 17, night: Kai's gold block + note block column at (1, 15)
    and his lantern post at (1, 17) in front of house_f's door (4.5, 16.5); the narrator's door = house_e's
    (-4.5, 15.5), facing east across the exit road (x -1..1); paths lane_home (up the road from the square, in at
    house_e's door) and lane_to_square (down the road from the north to the square).
    THE EXIT GATE, beat 9, night: the gate's two plains_lamp_1 posts at (-3, 24) and (3, 24) (the last torches;
    light group 'lamp'); the road runs north from there into the meadow.
    THE NIGHT MEADOW (this module, night_meadow), beats 10-16: flat grass (z 0) north of the gate to y 50 (then a
    1-block rise every ~11 blocks), a low hill east of x 16. Built into the World:
      - plants off x -4..15, y 30..47 (the line, the walk, the low cameras' ground) and on every low camera's view
        (sets.clear_view, 2 blocks wide);
      - THE SKELETON'S OAK: a vanilla small oak, 6 logs, trunk at (13, 44) (sets.plant_oak: canopy z 3..7, leaves
        from z 3, a skeleton's head at 1.99 fits under them), east of the line: the skeleton found under it in beat
        11 stands on the right of the line in beat 12, as the oak is (seen at the right edge of b12 / b15);
      - two of the village's lone oaks taken out: (6, 74) stood right behind Steve's head in the middle of the
        beat-12 line, (-7, 63) behind the creeper; the north horizon is clean (the village keeps (-13, 47),
        (15, 55), (24, 69)).
      THE LINE (beat 12) runs east-west at y 40: creeper (1.8, 40), Steve in the middle (5.0, 40), skeleton
      (8.2, 40): 3.2 blocks either side (the creeper's fuse range is 3), 3.2 blocks of flight for the arrows.

ANCHORS (v.anchors["crammys_<key>"], v.yaws[...]; CS.anchors(v) gives them without the prefix, with the music
module's bandstand ones (bd.A: zuri, kai, sunny, noor, alex_post, alex_eject, zuri_watch, kai_watch, steve_wing,
three_*, steve_jukebox, alex, alex_beside, ring_*, kai_step, steve_front, steve_kai, steve_foot, steve_watch,
line_1..5 and the *_target look points) and the lane's (lane_kai, lane_from_south, lane_from_north). Facing in
brackets.)
    walk_start (0.3, 19.6) [north]                 beat 9: Steve starts here, behind the lens's right shoulder
    steve_found (5.0, 36.0) [the creeper]          beat 10
    creeper_found (5.0, 41.0) [Steve]              beat 10: it faces him; cr.step(f0 + 30, steve) = its one step
    skeleton_oak (12.45, 44.24) [the b11 lens]     beat 11: against the oak's trunk (west face x 13), under the leaves
    steve_enter (5.2, 35.0) -> middle (5.0, 40.0)  beat 12: path crammys_into_middle (back to the lens, 2.2 b/s)
    creeper_line (1.8, 40.0) [east]  skeleton_line (8.2, 40.0) [west]     beats 12-14 (the skeleton shoots from here)
    steve_shot (5.0, 40.0) [yaw 135: north-east, the skeleton 45 degrees to his front right]   beats 13-14
    creeper_behind_from (2.6, 40.4) -> creeper_behind_to (3.9, 40.3)     beats 13-14: it closes in behind him
    beat 15: creeper_turn (4.4, 40.2) [toward steve_round_to]; Steve on path crammys_round (4.6, 39.0) ->
             (3.6, 39.1) -> steve_round_to (2.6, 39.9) (passing in front of it: the cut on action); skeleton_close
             (6.9, 40.0) [the creeper] (it came 1.3 blocks closer than in beat 12: the three fit a 24 mm frame)
    beat 16: disc_rest (3.79, 40.5) (where music.creeper_disc(creeper_turn, f, seed=5, world=v) lands: re-aim on
             item.rest_pos when the creeper dies elsewhere); steve_disc_from (6.32, 40.01) -> steve_disc (4.30,
             41.30) [the lens]: he walks in from the right and stops just behind the disc
    PATHS: crammys_walk_out (0.3, 19.6) -> (0.5, 24.5) -> (0.6, 30) -> (2.6, 33.4) -> (5.0, 35.6) (beat 9 and the
           way to beat 10), crammys_into_middle, crammys_round (sets.ground_path: on the ground); music's
           bandstand_steve_cross, bandstand_wing_to_three, lane_home, lane_to_square.
    THE ARROWS: CS.arrows(steve, f) / ARROW_FLIGHT: the chest arrow of beat 13 is shot with align=True (its shaft
           back along the flight); the unaligned "chest" spot points 24 degrees up and from a lens beside the line of
           fire put the fletching over his mouth. The second (beat 14) is hostiles' "shoulder_r" (mostly up: from
           b13's lens its shaft crosses his right eye; a director may prefer align=True there too).

THE PARTS (make_parts(v)): band (music.Band: lights, kicker, tap, totem), notes, jukebox (play / insert / eject),
    last_lantern (beat 5; keep it OUT of st.cast), totem (Band.totem, per shot), door "house_e" (the narrator's:
    v.door_open("house_e", f[, open=False])), kai_door "house_f", oak (the oak's record). No levers, pistons or
    cutaways: no interior is filmed.

THE SUGGESTED CAMERAS (CAMERAS[beat]: pos, target[, pos1, target1, focus], lens, fstop, sky, what). Every one rendered
at 540x960 / 16 samples, 2 threads, motion blur, under its sky, with --zones (out/test/crammys_set_<beat>_<what>
[_f<N>].png and _zones.png) and tools/palette_check (every check passes on every still; b02's first frame fails only
"hero in the safe area": Zuri's head is cut by the top before the tilt reaches her), with stand-ins staged as the beat
says: beats 1-8 and 17-24 by tools/music_proof's own staging of engine/music.py BEATS (filmed through THIS table),
plus the zombie of beat 7, the two arrows from beat 13 on, and no lantern on the north post before beat 5; beats
9-16 by the engine/hostiles recipe on this set (stage_b09 .. stage_b16). Positions are x %, y % of the frame.
    b01 gold   music b1 (35 mm f/2, push in 0.6) AIMED 0.25 LOWER (z 1.65): with music's aim Steve's chin sat at 61 %,
               on the caption band. Steve 61, 54.5 (face y 50-59 %); Zuri 15, Kai 32, Noor 50 (horn), Sunny 74, all
               at y 42; their three notes at 16 / 31 / 78 %
    b02 gold   music b2 (40 mm, tilt and rise): first frame the note block on white wool big (its note at 52, 19), Zuri's
               head cut by the top; last frame her face x 37-65 %, y 40-54 %. The north post's two fences stand in
               front of her shoulder at x 10-30 % (no lantern on them yet)
    b03 gold   music b3: Kai's face 54, 30 (screen left), the gold block's sunlit face 38, 59, Steve's shoulder soft at
               the right edge. No sun rim on the gold (impossible on this set: music's report)
    b04 gold   music b4 (28 mm static wide): Zuri 14, Kai 31, Sunny 72 (y 45), his note 77, 48; Steve below the stage
               looking down at the ground at x ~75 %, beside the pedestal
    b05 gold   music b5: the totem 50, 43 (x 22-80 %) on the first frame; at the end the whole bandstand, the placed
               north lantern at 18 %, Alex 27 %, the totem 65, 50
    b06 gold   music b6 (dolly): Zuri's held note block 29, 39 and her face 49, 40 on the first frame; on the last Steve
               at the end of the line holding out his empty hand, looking down at it
    b07 night  music "lane" (16 mm from Kai's doorstep): Kai's back of head 74, 52, his lantern at 90 %; Steve at his
               door 42, 49 with the zombie, arms out, about two blocks behind him at 41 % (f34); the door shut and the
               zombie at its step 44, 48 (f54). KNOWN LIMIT: the frame sees the road only north of y 14.4 and Kai's
               gold / note column hides it south of y 15.9: Steve appears 1.5 blocks before his door, so "sprints
               across the lane" lasts about half a second, and the zombie (stage_b07: it reaches the step on the frame
               the door has shut, B07_ARRIVE) is two blocks behind him there, not four (four behind, it would still be
               hidden behind the column when he goes in)
    b08 night  music b8: the disc above the jukebox 44, 37; the jukebox top 52, 49; Alex 56, 37; Steve's head soft below
    b09 night  20 mm f/4 from (-1.5, 18.8, 0.55): the gate's west lamp post big at the left (x 8-17 %), Steve walking
               away up the road past it (x 80 % on f18 -> 56 % on f44, small against the clean horizon), the warm
               pool of the lamps on the road, the skeleton's oak at the right
    b10 night  40 mm f/4 low over Steve's left shoulder: the creeper's head against the night sky (58, 41)
    b11 night  40 mm f/2.8 from (2.5, 41.8, 0.35) looking east: the skeleton pale against the dark trunk (26, 53), the
               canopy over it, the MOON half behind the canopy's south edge (74, 26)
    b12 night  24 mm f/5.6 from (5.0, 27.0, 0.45): creeper 21, Steve 50, skeleton 79 (bow drawn) at y 46-48, all three
               against the sky above a clean horizon (a wide: figures 12 % of the frame high)
    b13 / b14  45 mm f/2.8 from (8.19, 41.16, 1.05), 1.2 blocks north of the skeleton (the arrow comes from beside the
               lens): Steve's face three-quarter 56-61, 42-43, the chest arrow's fletching on his upper chest, the
               creeper soft at the right edge; in b14 the shoulder arrow's shaft crosses his right eye
    b15 night  24 mm f/4 from (4.75, 31.0, 0.45): Steve 30, creeper 42 (swelling), skeleton 78 (a wide)
    b16 night  40 mm f/2.8 from (2.39, 38.3, 0.3), 2.6 blocks from the disc: a black disc against the haze (50, 42),
               Steve's legs and his arrows walking in at the right
    b17 night  music "lane": Steve sprinting right to left past the doorstep with the disc (motion-blurred, mid-frame)
    b18 night  music b18: Sunny 23, Steve 47 (both arrows in the lantern light), Noor 72, all at y 46
    b19 night  music b19: Kai 61, Zuri 50, Sunny 38, Noor 29 (y 44-48); Steve's back at the bottom right (x 85-100 %)
    b20 night  music b20: disc 11 at 20, 44 (a third of the frame), cat at 72, 45, Steve's face between
    b21 night  music b21: the jukebox top 50, 53 (its slot), Steve beside it with both arrows plain
    b22 night  music b22 (24 mm frontal wide): six faces x 24-63 %, y 48 %; THE MOON over the stage at 62, 16
    b23 night  music b23: Noor 12, Sunny 24, Zuri 36, Kai 48 -> 53 (his step), Alex 62, Steve 76 (y 44-47)
    b24 night  music b24: the totem 41, 47 and the empty pedestal below on the first frame; at the end of the pull
               back all six heads x 11-80 % (Steve 80 %, at the edge), y 47-49 %

NOT VERIFIED / KNOWN LIMITS
    - Stills only (one or two frames a beat): walks, the creeper's step and fuse, the arrows' flights, the poof, the
      disc's drop, the jukebox notes are the engine modules' numbers here, not watched in motion. Nothing went
      through render.py at final settings (this is no film yet); the stills use the same Village, Stage and look.
    - The east moon is new: the music module's night proofs were made under az 176. Every night still here passes
      palette_check, but the stage faces are now lantern-keyed (the well's moonshadow): Steve's trousers measured
      min channel 14 in b13 / b14 / b16 (limit 12). moon_key() is offered for a face that goes under; not rendered.
    - Beat 16's disc lands where music.creeper_disc puts it (seed 5 from creeper_turn: disc_rest); a creeper killed
      elsewhere drops it elsewhere: aim b16 at item.rest_pos (stage_b16 does).
    - Beat 15: Steve ends 1.8 blocks from the creeper; two arrows at knockback=0.1 push it 0.6 toward him (hostiles'
      numbers; not measured on this staging). Keep knockback=0.1 or max_back.
    - The wides (b04, b12, b15, b22, b23, b24's end) have small faces; that is the stage's and the line's width in a
      9:16 frame. b11's skeleton is 22 % of the frame high (the moon at the canopy's edge needs that width).
    - b07: see the camera table (the lane camera sees the road only by the door).
    - The golden sun (az 240) is music's: off the game's east-west arc, kept because every gold camera was placed
      for it.
"""
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from engine import music, sets, village   # noqa: E402

# ------------------------------------------------------------------------------------------------------------------
# the skies (Blender azimuth: degrees counter-clockwise from east; 90 = north, 180 = west)
# ------------------------------------------------------------------------------------------------------------------
SKIES = {
    "gold": dict(preset="golden", az=240.0, el=27.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=0.0, el=21.0, bloom=1.3, grade="cool"),
}
GOLD_TORCHES, NIGHT_TORCHES = 1.0, 1.3

# ------------------------------------------------------------------------------------------------------------------
# THE NIGHT MEADOW (beats 9-16), north of the exit gate (0.5, 24.5): flat grass (z 0) to y 50, a hill east of x 16
# ------------------------------------------------------------------------------------------------------------------
LINE_Y = 40.0
MEADOW_CLEAR = (-4, 30, 15, 47)          # plants taken off (the line, the walk in, the low cameras' ground)
OAK = (13, 44)                           # the skeleton's lone oak (beat 11): planted, 6 logs (canopy z 3..7)
OAK_HEIGHT = 6
# the village's lone oaks that stand right behind the beat-12 line from its camera (village.MEADOW_OAKS): (6, 74) was
# behind Steve's head in the middle, (-7, 63) behind the creeper's; taken out, the north horizon is clean
OAKS_OUT = ((6, 74), (-7, 63))

MEADOW_ANCHORS = {        # key -> ((x, y), facing point or yaw in degrees (characters face -Y at yaw 0))
    "walk_start": ((0.3, 19.6), (0.5, 30.0)),
    "steve_found": ((5.0, 36.0), (5.0, 41.0)),
    "creeper_found": ((5.0, 41.0), (5.0, 36.0)),
    "skeleton_oak": ((12.45, 44.24), (2.5, 41.8)),
    "creeper_line": ((1.8, LINE_Y), (5.0, LINE_Y)),
    "skeleton_line": ((8.2, LINE_Y), (5.0, LINE_Y)),
    "skeleton_close": ((6.9, LINE_Y), (4.4, 40.2)),
    "steve_enter": ((5.2, 35.0), (5.0, LINE_Y)),
    "middle": ((5.0, LINE_Y), (5.0, 50.0)),
    "steve_shot": ((5.0, LINE_Y), 135.0),
    "creeper_behind_from": ((2.6, 40.4), (5.0, LINE_Y)),
    "creeper_behind_to": ((3.9, 40.3), (5.0, LINE_Y)),
    "creeper_turn": ((4.4, 40.2), (2.2, 39.9)),
    "steve_round_from": ((4.6, 39.0), (3.4, 39.1)),
    "steve_round_to": ((2.6, 39.9), (4.4, 40.2)),
    "disc_rest": ((3.79, 40.5), (2.39, 38.3)),
    "steve_disc": ((4.30, 41.30), (2.39, 38.3)),
    "steve_disc_from": ((6.32, 40.01), (4.30, 41.30)),
}
MEADOW_PATHS = {
    "walk_out": [(0.3, 19.6), (0.5, 24.5), (0.6, 30.0), (2.6, 33.4), (5.0, 35.6)],
    "into_middle": [(5.2, 35.0), (5.0, LINE_Y)],
    "round": [(4.6, 39.0), (3.6, 39.1), (2.6, 39.9)],
}


def _yaw(p, toward):
    """Yaw of a character at p facing `toward` (a point) or `toward` degrees."""
    if isinstance(toward, (int, float)):
        return math.radians(float(toward))
    return village.yaw_to(p, toward)


def night_meadow(b):
    """The meadow of beats 9-16: plants off the action and camera ground, the skeleton's lone oak, anchors, paths."""
    x0, y0, x1, y1 = MEADOW_CLEAR
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            b.clear_plants(x, y)
            b.reserved.add((x, y))
    oak = sets.plant_oak(b, OAK[0], OAK[1], b.rng_for("crammys oak"), height=OAK_HEIGHT)
    removed = []
    for x, y in OAKS_OUT:
        t = b.tree_at(x, y)
        if t is not None:
            sets.remove_tree(b, t)
            removed.append((x, y))
    for key, (p, toward) in MEADOW_ANCHORS.items():
        b.anchor("crammys_" + key, p, _yaw(p, toward), replace=True)
    for key, pts in MEADOW_PATHS.items():
        sets.ground_path(b, "crammys_" + key, pts, replace=True)
    return dict(clear=MEADOW_CLEAR, oak=oak, oaks_out=removed)


def crammys_set(b):
    """THE HOOK of "The Crammys": music.crammys_set (bandstand, lane) + the night meadow."""
    sets._new_name(b, "crammys")
    res = dict(music=music.crammys_set(b), meadow=night_meadow(b))
    for c in CAMERAS.values():                                     # no tuft between a low camera and its subject
        if c["pos"][2] < 1.5 and b.ground(c["pos"][0], c["pos"][1]) is not None and c.get("clear", True):
            sets.clear_view(b, c["pos"], c.get("target1", c["target"]), 2.0)
            sets.clear_view(b, c["pos"], c["target"], 2.0)
    b.v.sets["crammys"] = res
    return res


def build_set(scene):
    """The village of "The Crammys": seed 1 with crammys_set built in. Returns the Village."""
    return village.build_village(scene, seed=1, edit=crammys_set)


def anchors(v):
    """Every named place of this film in one dict, key -> (point, yaw or None): the bandstand's (music: 'zuri',
    'steve_jukebox', 'ring_kai', ... and their look targets), the lane's ('lane_kai', ...), the meadow's (without
    the 'crammys_' prefix: 'middle', 'skeleton_oak', ...)."""
    bd = music.band(v)
    out = {k: (tuple(p), bd.yaw.get(k)) for k, p in bd.A.items()}
    for k, p in v.anchors.items():
        if k.startswith("crammys_"):
            out[k[len("crammys_"):]] = (tuple(p), v.yaws.get(k))
    return out


class Parts(dict):
    """The things of the set that change on camera (make_parts(v)); also reachable as attributes."""

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)


def make_parts(v):
    """The parts after the build (call once; music.band(v) is cached, so a second call returns the same handles):
    band (music.Band), notes ({'zuri', 'kai', 'sunny', 'row_1..3', 'lane'}: NoteBlock), jukebox (play / insert /
    eject), last_lantern (place on camera, beat 5; keep it OUT of st.cast), totem (Band.totem: the dropped item on
    the pedestal, per shot), door ('house_e': the narrator's front door, v.door_open('house_e', f[, open=False])),
    kai_door ('house_f'), oak (the skeleton's oak record)."""
    bd = music.band(v)
    return Parts(band=bd, notes=bd.notes, jukebox=bd.jukebox, last_lantern=bd.last_lantern, totem=bd.totem,
                 door="house_e", kai_door="house_f", oak=v.sets["crammys"]["meadow"]["oak"])


# ------------------------------------------------------------------------------------------------------------------
# A SUGGESTED CAMERA FOR EVERY BEAT
# ------------------------------------------------------------------------------------------------------------------
def _mc(name, **over):
    """music.CAMERAS[name] (the bandstand / lane camera) with overrides."""
    c = dict(music.CAMERAS[name])
    c.update(over)
    return c


CAMERAS = {
    # b01: music's b1 tilted down 0.25 at the stage (aim z 1.9 -> 1.65): with music's aim Steve's chin was at 61 % of
    # the frame on the first frames (the caption band starts at 62 %), before the push in makes him bigger
    "b01": _mc("b1", target=(-6.8, 0.35, 1.65), target1=(-6.8, 0.35, 1.65), sky="gold", what="everyone",
               proof="b1"),
    "b02": _mc("b2", sky="gold", what="zuri", proof="b2"),
    "b03": _mc("b3", sky="gold", what="kai", proof="b3"),
    "b04": _mc("b4", sky="gold", what="sunny", proof="b4"),
    "b05": _mc("b5", sky="gold", what="trophy", proof="b5"),
    "b06": _mc("b6", sky="gold", what="line", proof="b6"),
    "b07": _mc("lane", sky="night", what="chased", proof="lane"),
    "b08": _mc("b8", sky="night", what="eject", proof="b8"),
    "b09": dict(pos=(-1.5, 18.8, 0.55), target=(1.2, 34.0, 1.6), lens=20.0, fstop=4.0, sky="night", what="torch"),
    "b10": dict(pos=(5.85, 34.1, 0.9), target=(4.7, 41.0, 0.9), lens=40.0, fstop=4.0, sky="night", what="creeper"),
    "b11": dict(pos=(2.5, 41.8, 0.35), target=(12.43, 43.0, 2.02), lens=40.0, fstop=2.8, sky="night",
                what="skeleton"),
    "b12": dict(pos=(5.0, 27.0, 0.45), target=(5.0, 40.0, 1.0), lens=24.0, fstop=5.6, sky="night", what="middle"),
    "b13": dict(pos=(8.19, 41.16, 1.05), target=(5.0, 40.0, 1.35), lens=45.0, fstop=2.8, sky="night", what="shot"),
    "b14": dict(pos=(8.19, 41.16, 1.05), target=(5.0, 40.0, 1.35), lens=45.0, fstop=2.8, sky="night", what="again"),
    "b15": dict(pos=(4.75, 31.0, 0.45), target=(4.75, 40.0, 1.0), lens=24.0, fstop=4.0, sky="night",
                what="creeper_shot"),
    "b16": dict(pos=(2.39, 38.3, 0.3), target=(3.79, 40.5, 0.15), lens=40.0, fstop=2.8, sky="night", what="disc"),
    "b17": _mc("lane", sky="night", what="run_back", proof="lane17"),
    "b18": _mc("b18", sky="night", what="nobody_asked", proof="b18"),
    "b19": _mc("b19", sky="night", what="to_jukebox", proof="b19"),
    "b20": _mc("b20", sky="night", what="disc11", proof="b20"),
    "b21": _mc("b21", sky="night", what="jukebox", proof="b21"),
    "b22": _mc("b22", sky="night", what="nobody_moved", proof="b22"),
    "b23": _mc("b23", sky="night", what="kai", proof="b23"),
    "b24": _mc("b24", sky="night", what="vocals", proof="b24"),
}


# ------------------------------------------------------------------------------------------------------------------
# film-local lights
# ------------------------------------------------------------------------------------------------------------------
MOON_KEY_COLOR = (0.84, 0.87, 1.0)


def moon_key(st, shot, at, watts=60.0, color=MOON_KEY_COLOR, name=None, collection=None):
    """A film-local SHADOWLESS cool point light at `at` that only `shot` sees (keyed visible on its frames, hidden
    everywhere else: no other frame's stamp changes): the stand-in for moonlight on a face the moon cannot reach.
    Returns the light."""
    from engine import props

    ob = props.make_light("fill", collection or st.v.collection)
    ob.name = name or "crammys_moonkey_%s" % shot.name
    ob.location = tuple(float(c) for c in at)
    ob.data.color = tuple(float(c) for c in color)
    ob.data.energy = float(watts)
    ob.visible_camera = False
    f0, f1 = shot.frame_start, shot.frame_end
    for f, hidden in ((min(1, f0) - 1, True), (f0, False), (f1 + 1, True)):
        st.key(ob, "hide_render", f, hidden)
        st.key(ob, "hide_viewport", f, hidden)
    return ob


# ------------------------------------------------------------------------------------------------------------------
# scouting
# ------------------------------------------------------------------------------------------------------------------
TEST_DIR = os.path.join(ROOT, "out", "test")


def _skies():
    """SKIES, or a test override (CRAMMYS_SKIES='{"night": {"az": 176}}' merges into the entries)."""
    out = {k: dict(v) for k, v in SKIES.items()}
    over = os.environ.get("CRAMMYS_SKIES")
    if over:
        for k, d in json.loads(over).items():
            out.setdefault(k, {}).update(d)
    return out


class Scout:
    """One scene: the set, the band, a Stage with SKIES (sky = the active one), a Film. For stills only."""

    def __init__(self, sky="gold", res=(540, 960), samples=16, threads=2):
        import bpy
        from engine import look, shots
        from films import lookdev as L
        self.bpy = bpy
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.scene = bpy.context.scene
        look.setup_render(self.scene, res=res, samples=samples, threads=threads)
        self.v = build_set(self.scene)
        self.bd = music.band(self.v)
        self.film = shots.Film(self.scene, fps=24)
        self.st = L.Stage(self.scene, self.film, self.v, skies=_skies(), sky=sky)
        self.sky = sky
        self.h = dict(sky=sky)

    def render(self, frame, name, zones=True):
        """Render `frame` to out/test/<name>.png (+ _zones.png). Returns the path."""
        from PIL import Image
        from engine import post
        os.makedirs(TEST_DIR, exist_ok=True)
        path = os.path.join(TEST_DIR, name + ".png")
        self.film.goto(frame)
        self.scene.render.filepath = path[:-4] + "_part"
        self.scene.render.use_file_extension = True
        t = time.time()
        self.bpy.ops.render.render(write_still=True)
        os.replace(path[:-4] + "_part.png", path)
        if zones:
            with Image.open(path) as im:
                post.draw_zones(im.convert("RGB")).save(path[:-4] + "_zones.png")
        print("[crammys_set] %s (frame %d, sky %s) %.1f s" % (path, frame, self.sky, time.time() - t), flush=True)
        return path


def view(name, pos, target, lens=24.0, fstop=8.0, sky="night", res=(540, 960), samples=16):
    """A plain view of the set (no cast): out/test/crammys_set_view_<name>.png."""
    sc = Scout(sky, res=res, samples=samples)
    s = sc.st.shot("view", 0.5, sky=sky)
    s.lens(lens, fstop)
    s.move(pos, target)
    s.focus(target)
    sc.bd.lights(sc.st, s, scale=GOLD_TORCHES if sky == "gold" else NIGHT_TORCHES)
    sc.st.finish()
    return sc.render(s.frame_start + 2, "crammys_set_view_" + name, zones=False)


def _vec(text):
    return tuple(float(c) for c in text.split(","))


# ------------------------------------------------------------------------------------------------------------------
# the proof stills: one staging per beat (the bandstand and lane beats are tools/music_proof's shot_<name>, staged
# exactly as engine/music.py BEATS says, plus what this film adds: the zombie of beat 7, the two arrows in Steve from
# beat 13 on); returns (frames to render, {label: point or thing that must be in the safe area})
# ------------------------------------------------------------------------------------------------------------------
def _cam_over(beat):
    """CRAMMYS_CAMS='{"b11": {"pos": [...], "lens": 35}}': a scouting override of CAMERAS (nothing is written)."""
    over = os.environ.get("CRAMMYS_CAMS")
    if not over:
        return {}
    d = json.loads(over).get(beat, {})
    return {k: (tuple(v) if isinstance(v, list) else v) for k, v in d.items()}


def _cam(s, beat, focus=None, ease="linear", **over):
    """Put CAMERAS[beat] on shot s (a move when it has pos1 / target1). Returns the spec."""
    c = dict(CAMERAS[beat], **over)
    c.update(_cam_over(beat))
    s.lens(c["lens"], c["fstop"])
    if "pos1" in c or "target1" in c:
        s.move(c["pos"], c["target"], c.get("pos1", c["pos"]), c.get("target1", c["target"]), ease=ease)
    else:
        s.move(c["pos"], c["target"])
    s.focus(focus if focus is not None else c.get("focus", c["target"]))
    return c


# the flight of beat 13's arrow in Steve's own frame (forward, right, up): from the skeleton 45 degrees to his front
# right at skeleton_line, its eyes 0.34 above his chest. hit(..., align=True) turns the chest arrow's shaft back along
# it: from a lens beside the line of fire the unaligned "chest" spot (its shaft 24 degrees up) put the fletching over
# his mouth (out/test/crammys_set_b13_shot.png, first scouting pass)
ARROW_FLIGHT = (-0.700, -0.700, -0.105)


def arrow_direction(steve, frame):
    """The world direction of beat 13's flight for Steve as he stands on `frame` (ARROW_FLIGHT turned with him)."""
    yaw = steve.yaw_at(frame)
    f = (math.sin(yaw), -math.cos(yaw))
    r = (f[1], -f[0])
    a, b_, c = ARROW_FLIGHT
    return (a * f[0] + b_ * r[0], a * f[1] + b_ * r[1], c)


def arrows(steve, frame, scale=1.0):
    """The two arrows of beats 13 and 14 already in him from `frame` on (no hurt): the chest one aligned as beat 13
    leaves it (ARROW_FLIGHT), the right-shoulder one as hostiles' "shoulder_r" spot. For proof stills of beats 15-24;
    in the film they are the two arrows beat 13 / 14 shoot (hostiles keeps them in him to the end)."""
    from engine import hostiles
    hostiles.hit(steve, frame, part="chest", hurt=False, scale=scale, align=True,
                 direction=arrow_direction(steve, frame))
    hostiles.hit(steve, frame, part="shoulder_r", hurt=False, scale=scale)


_arrows = arrows


def _music_stage(sc, s, beat):
    """A bandstand / lane beat staged by tools/music_proof (its own shot function), on this film's set."""
    from tools import music_proof as MP
    name = CAMERAS[beat]["proof"]
    cam = {k: v for k, v in CAMERAS[beat].items() if k not in ("sky", "what", "proof")}
    cam.update(_cam_over(beat))
    sc.bd.cameras[name] = cam                          # the staging films THIS film's camera for the beat
    MP._EMPTY.clear()
    MP.BUILDERS[name](sc.st, s, sc.bd, sc.h)
    offs = dict((n, o) for n, _sk, _sec, o in MP.SHOTS)[name]
    offs = offs if offs is not None else sc.h[name]
    frames = [s.frame_start + o for o in offs]
    heroes = {}
    for f, items in sc.h.get("zones", {}).get(s.name, []):
        if f in frames or not heroes:
            for label, thing, kind in items:
                if kind in ("face", "head", "prop"):
                    heroes[label] = thing
    return frames, heroes


def _proof_seconds(beat):
    from tools import music_proof as MP
    return dict((n, sec) for n, _sk, sec, _o in MP.SHOTS)[CAMERAS[beat]["proof"]]


def stage_music(sc, s, beat):
    """Beats 1-6, 8, 18-24 and the lane: tools/music_proof's staging (+ the arrows from beat 13 on)."""
    frames, heroes = _music_stage(sc, s, beat)
    if int(beat[1:]) < 5:
        # beats 1-4 come before Alex places the last lantern (beat 5): in the film the north post has no lantern
        # yet (LastLantern stands there from the start unless place() is called)
        sc.bd.last_lantern.place(s.frame_end + 1)
    steve = sc.st.cast.get("steve")
    if steve is not None and int(beat[1:]) >= 13:
        _arrows(steve, s.frame_start)
    return frames, heroes


B07_ARRIVE = 54                  # the zombie reaches the narrator's door step (B07_STOP) on this frame of the shot:
#                                  the door has just shut (music_proof's lane: open at the walk's end - 8, shut at its
#                                  end + 4, here frames 40 and 52). It walks 2.33 blocks/s, so it is about 2.9 blocks
#                                  behind Steve as he turns in at his door. Kai's gold / note block column hides the road
#                                  south of y 15.9 from this camera: a zombie four blocks behind is not yet in the frame
#                                  when Steve goes in (see CAMERAS["b07"])
B07_STOP = (-3.45, 15.5, 0.0)    # where the zombie stops: at the foot of the door step, facing the shut door
B07_STILLS = (34, 54)            # Steve turning in at his door / the door shut in the zombie's face


def _along(path, d):
    """The polyline `path` from distance d along it on: [point at d, the following nodes]."""
    from mathutils import Vector
    pts = [Vector(p) for p in path]
    acc = 0.0
    for i, (a, b_) in enumerate(zip(pts, pts[1:])):
        seg = (b_ - a).length
        if acc + seg >= d:
            q = a + (b_ - a) * ((d - acc) / seg) if seg > 0 else a
            return [tuple(q)] + [tuple(p) for p in pts[i + 1:]]
        acc += seg
    return [tuple(pts[-2]), tuple(pts[-1])]


def _length_to(path, point):
    """Distance along `path` to its node nearest `point` (2D)."""
    import math as _m
    acc, best = 0.0, (1e9, 0.0)
    for a, b_ in zip(path, path[1:]):
        if _m.dist(a[:2], point[:2]) < best[0]:
            best = (_m.dist(a[:2], point[:2]), acc)
        acc += _m.dist(a, b_)
    if _m.dist(path[-1][:2], point[:2]) < best[0]:
        best = (0.0, acc)
    return best[1]


def stage_b07(sc, s, beat="b07"):
    """Beat 7: music_proof's lane (Steve sprinting home past Kai, Kai's head following him, the door shut after him)
    + the zombie with its arms out on the same path, reaching the door as it shuts (B07_ARRIVE)."""
    from engine import undead
    frames, heroes = _music_stage(sc, s, beat)
    steve = sc.st.cast["steve"]
    f0 = s.frame_start
    # the zombie's way: Steve's path to the foot of the narrator's door step (cobblestone stairs at (-4, 15, 0))
    pts = [tuple(p) for p in sc.v.paths["lane_home"] if p[2] < 0.5] + [B07_STOP]
    z = undead.add_zombie(sc.st, "zombie")
    total = sum(math.dist(a[:2], b_[:2]) for a, b_ in zip(pts, pts[1:]))
    d0 = total - undead.WALK_SPEED * B07_ARRIVE / 24.0
    rest = _along(pts, max(0.0, d0))
    z.place(f0, rest[0], village.yaw_to(rest[0], rest[1]))
    z.aggro(f0, ease=0)
    z.walk(f0, rest)
    sc.st.use(s, z)
    heroes["zombie"] = z
    heroes["steve"] = steve
    return [f0 + o for o in B07_STILLS], heroes


# ---- the night meadow (beats 9-16): the engine.hostiles recipe on this set ----------------------------------------
def _A(sc, key):
    return sc.v.anchors["crammys_" + key]


def _Y(sc, key):
    return sc.v.yaws["crammys_" + key]


def _steve(sc, s, key=None, frame=None):
    from engine import players
    p = players.add_player(sc.st, "steve", "steve")
    if key is not None:
        p.place(s.frame_start if frame is None else frame, _A(sc, key), _Y(sc, key))
    sc.st.use(s, p)
    return p


def _meadow_lights(sc, s):
    sc.bd.lights(sc.st, s, scale=NIGHT_TORCHES)


def stage_b09(sc, s, beat="b09"):
    """Beat 9: from behind and low at the east lamp post of the exit gate, Steve walks away up the road."""
    f0 = s.frame_start
    steve = _steve(sc, s)
    pts = sc.v.paths["crammys_walk_out"]
    steve.place(f0, pts[0], village.yaw_to(pts[0], pts[1]))
    steve.walk(f0, pts)
    _cam(s, beat, focus=steve.head)
    _meadow_lights(sc, s)
    return [f0 + 18, f0 + 44], {"steve": steve}


def stage_b10(sc, s, beat="b10"):
    """Beat 10: low over Steve's shoulder, the creeper facing him against the sky; one slow step."""
    from engine import hostiles
    f0 = s.frame_start
    steve = _steve(sc, s, "steve_found")
    cr = hostiles.add_creeper(sc.st, "creeper")
    cr.place(f0, _A(sc, "creeper_found"), _Y(sc, "creeper_found"))
    cr.look_at(f0, steve, ease=0)
    cr.step(f0 + 30, steve)
    sc.st.use(s, cr)
    _cam(s, beat, focus=cr.head)
    _meadow_lights(sc, s)
    return [f0 + 20], {"creeper": cr}


def stage_b11(sc, s, beat="b11"):
    """Beat 11: under the lone oak, the skeleton turns its skull to the lens and lifts its bow."""
    from engine import hostiles
    f0 = s.frame_start
    sk = hostiles.add_skeleton(sc.st, "skeleton")
    sk.place(f0, _A(sc, "skeleton_oak"), _Y(sc, "skeleton_oak"))
    c = CAMERAS[beat]
    sk.look_at(f0 + 4, c["pos"], ease=8)
    sk.aim(f0 + 16)
    sc.st.use(s, sk)
    _cam(s, beat, focus=sk.head)
    _meadow_lights(sc, s)
    return [f0 + 30], {"skeleton": sk}


def stage_b12(sc, s, beat="b12"):
    """Beat 12: the side view, creeper left, skeleton right with its bow drawn; Steve walks into the middle."""
    from engine import hostiles
    f0, f1 = s.frame_start, s.frame_end
    cr = hostiles.add_creeper(sc.st, "creeper")
    sk = hostiles.add_skeleton(sc.st, "skeleton")
    steve = _steve(sc, s)
    cr.place(f0, _A(sc, "creeper_line"), _Y(sc, "creeper_line"))
    sk.place(f0, _A(sc, "skeleton_line"), _Y(sc, "skeleton_line"))
    pts = sc.v.paths["crammys_into_middle"]
    steve.place(f0, pts[0], village.yaw_to(pts[0], pts[1]))
    sk.aim(f0, steve, ease=0)
    sk.draw(f0, release=f1 + 1, target=steve)
    e = steve.walk(f0, pts, speed=2.2)
    steve.look_at(e + 2, cr, ease=6)
    cr.look_at(f0, steve, ease=0)
    sc.st.use(s, cr, sk)
    _cam(s, beat, focus=steve.head)
    _meadow_lights(sc, s)
    return [e + 4], {"steve": steve, "creeper": cr, "skeleton": sk}


def _stage_shot(sc, s, beat, second):
    from engine import hostiles
    f0 = s.frame_start
    steve = _steve(sc, s, "steve_shot")
    cr = hostiles.add_creeper(sc.st, "creeper")
    sk = hostiles.add_skeleton(sc.st, "skeleton")
    a, b_ = _A(sc, "creeper_behind_from"), _A(sc, "creeper_behind_to")
    cr.place(f0, a, _Y(sc, "creeper_behind_from"))
    sk.place(f0, _A(sc, "skeleton_line"), _Y(sc, "skeleton_line"))
    sk.aim(f0, steve, ease=0)
    fl1 = sk.shoot(f0, steve, part="chest", align=True, knockback=0.1)
    fl2 = sk.shoot(fl1.frames[0] + 1, steve, part="shoulder_r", knockback=0.1)
    steve.look_at(f0, sk, ease=0)
    cr.walk(f0 + 30, [a, b_], speed=0.8)
    cr.look_at(f0 + 30, steve, ease=8)
    sc.st.use(s, cr, sk)
    _cam(s, beat, focus=steve.head)
    _meadow_lights(sc, s)
    f = (int(fl2) + 16) if second else (int(fl1) + 14)
    return [f], {"steve": steve}


def stage_b13(sc, s, beat="b13"):
    """Beat 13: medium on Steve from the skeleton's side; the first arrow in his chest."""
    return _stage_shot(sc, s, beat, False)


def stage_b14(sc, s, beat="b14"):
    """Beat 14: the same shot held; the second arrow in his shoulder, the creeper close behind."""
    return _stage_shot(sc, s, beat, True)


def stage_b15(sc, s, beat="b15"):
    """Beat 15: the side view tighter: Steve round the creeper, it swells, two arrows, it tips over."""
    from engine import hostiles
    f0 = s.frame_start
    cr = hostiles.add_creeper(sc.st, "creeper")
    sk = hostiles.add_skeleton(sc.st, "skeleton")
    steve = _steve(sc, s)
    c_at = _A(sc, "creeper_turn")
    pts = sc.v.paths["crammys_round"]
    cr.place(f0, c_at, _Y(sc, "creeper_turn"))
    steve.place(f0, pts[0], village.yaw_to(pts[0], pts[1]))
    sk.place(f0, _A(sc, "skeleton_close"), _Y(sc, "skeleton_close"))
    _arrows(steve, f0)
    sk.aim(f0, cr, ease=0)
    steve.walk(f0, pts, speed=2.6)
    cr.face(f0 + 1, steve, ease=6)
    cr.look_at(f0 + 1, steve, ease=4)
    cr.fuse(f0)
    a = sk.shoot(f0 - 24, cr, knockback=0.1)
    k = sk.shoot(a.frames[0] + 1, cr, release=a.frames[0] + 20, kill=True, knockback=0.1, camera=s)
    sk.lower(int(k) + 12)
    steve.look_at(int(a) - 4, cr, ease=6)
    sc.st.use(s, cr, sk)
    _cam(s, beat, focus=cr.head)
    _meadow_lights(sc, s)
    sc.h["b15_kill"] = int(k)
    return [int(a) + 12], {"creeper": cr, "steve": steve, "skeleton": sk}


def stage_b16(sc, s, beat="b16"):
    """Beat 16: ground level, the disc turning above the grass where the creeper died; Steve's feet step in."""
    f0 = s.frame_start
    feet = _A(sc, "creeper_turn")
    d = music.creeper_disc(feet, f0 - 30, disc="music_disc_11", seed=5, world=sc.v, until=s.frame_end + 1,
                           name="crammys_disc", face=CAMERAS[beat]["pos"])
    sc.st.cast[d.name] = d
    sc.st.use(s, d)
    print("[crammys_set]   b16 disc: lands on frame %d at %s" % (d.land_frame, tuple(round(c, 3) for c in d.rest_pos)))
    steve = _steve(sc, s, "steve_disc_from")
    _arrows(steve, f0)
    e = steve.walk(f0 + 8, [_A(sc, "steve_disc_from"), _A(sc, "steve_disc")], speed=2.0)
    steve.face(e, d.rest_pos, ease=4)
    _cam(s, beat, focus=d.sprite)
    _meadow_lights(sc, s)
    return [f0 + 30], {"disc": d.sprite}


STAGES = {b: (globals().get("stage_" + b) or stage_music) for b in CAMERAS}
# the frames of the proof stills where the staging's own choice is not enough (offsets; "end" = the last frame)
STILL_FRAMES = {"b02": [8, "end"], "b05": [2, "end"], "b06": [3, "end"], "b24": [2, "end"]}
SECONDS = {"b09": 3.0, "b10": 2.5, "b11": 2.5, "b12": 3.0, "b13": 4.0, "b14": 4.0, "b15": 3.5, "b16": 3.0}


def project(scene, cam, point):
    """(x %, y % from the top) of a world point in the camera's frame, and whether it is in front of the lens."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    co = world_to_camera_view(scene, cam, Vector(point))
    return 100.0 * co.x, 100.0 * (1.0 - co.y), co.z > 0.0


def _point_of(thing, frame):
    """A world point for a hero: a Character's eyes, a point, a callable(frame), an object's location."""
    from engine import characters
    if isinstance(thing, characters.Character):
        return tuple(thing.eye_point(frame))
    if callable(thing):
        return tuple(thing(frame))
    if hasattr(thing, "sprite"):
        thing = thing.sprite
    if hasattr(thing, "matrix_world"):
        return tuple(thing.matrix_world.translation)
    return tuple(float(c) for c in thing)


def still(beat, sky=None, res=(540, 960), samples=16, name=None, dry=False, palette=True, frames=None):
    """Build the set, stage beat `beat` under its sky and render its proof still
    out/test/crammys_set_<beat>_<what>.png (+ _zones.png). Prints where each hero lands in the frame."""
    spec = CAMERAS[beat]
    sky = sky or spec["sky"]
    sc = Scout(sky, res=res, samples=samples)
    secs = SECONDS.get(beat) or _proof_seconds(beat)
    s = sc.st.shot(beat, secs, sky=sky)
    sc.shot = s
    fr, heroes = STAGES[beat](sc, s, beat)
    sc.st.finish()
    if frames is None and beat in STILL_FRAMES:
        frames = [s.frame_end - s.frame_start if o == "end" else o for o in STILL_FRAMES[beat]]
    if frames is not None:
        fr = [s.frame_start + int(o) for o in frames]
    out = name or "crammys_set_%s_%s" % (beat, spec["what"])
    path = None
    for i, f in enumerate(fr):
        sc.film.goto(f)
        cam = sc.scene.camera
        cell = tuple(int(math.floor(c)) for c in cam.matrix_world.translation)
        if sc.v.world.is_solid(*cell):
            print("[crammys_set]   !!! the camera of %s is inside %s at %s" % (beat, sc.v.world.block_id(*cell), cell))
        tag = "" if i == 0 else "_f%d" % (f - s.frame_start)
        path = None if dry else sc.render(f, out + tag)
        if path and palette:
            from tools import palette_check
            hero_obs = [ob for _l, obs in sc.st.heroes.get(s.name, []) for ob in obs]
            rep = palette_check.evaluate(palette_check.probe(sc.scene), path, heroes=hero_obs)
            palette_check.print_report("%s@%d" % (beat, f), rep)
        for label, thing in heroes.items():
            try:
                p = _point_of(thing, f)
            except Exception as e:                       # (a hero we cannot place: say so)
                print("[crammys_set]   %-14s ? (%s)" % (label, e))
                continue
            x, y, front = project(sc.scene, cam, p)
            flag = "" if (8 <= x <= 82 and 14 <= y <= 60 and front) else "   (outside the safe area)"
            print("[crammys_set]   %s@%d %-14s x %5.1f %%  y %5.1f %%%s" % (beat, f, label, x, y, flag))
    return path


# ------------------------------------------------------------------------------------------------------------------
# the self-test (numbers, no render): $BPY -m films.crammys_set
# ------------------------------------------------------------------------------------------------------------------
def _solid_at(w, x, y, z):
    """Is the point (x, y, z) inside a solid block (stairs and bottom slabs: their lower half only)?"""
    c = (int(math.floor(x)), int(math.floor(y)), int(math.floor(z)))
    if not w.is_solid(*c):
        return False
    bid, props = w.get(*c)
    if bid.endswith("_slab") and (props or {}).get("type", "bottom") == "bottom":
        return z - c[2] < 0.5 - 1e-6
    if bid.endswith("_stairs"):
        if z - c[2] < 0.5 - 1e-6:
            return True
        fx, fy = x - c[0], y - c[1]
        back = {"north": fy >= 0.5, "south": fy < 0.5, "east": fx >= 0.5, "west": fx < 0.5}
        return back.get((props or {}).get("facing", "north"), True)
    return True


def standing_anchors(v):
    """{name: point} of every standing spot this film uses: the meadow's (crammys_*), the bandstand's
    (bandstand_*) and the lane's (lane_kai, lane_from_south, lane_from_north)."""
    out = {}
    for k, p in v.anchors.items():
        if not k.startswith(("crammys_", "bandstand_", "lane_")):
            continue
        if k.endswith(("_target", "_cam", "_center", "_station", "_door")):
            continue
        out[k] = p
    return out


def check(verbose=True):
    """The set's numbers: build it; every standing anchor on solid ground with the body free (feet, knee, chest, head
    height), every camera position (pos and pos1) outside every block, the paths (Village.validate), the oak, the
    meadow line's spacing (the creeper's fuse range, the arrows' room). Returns the list of failures."""
    import bpy
    from engine import hostiles, quick
    bad = []
    t = time.time()
    scene = quick.reset()
    v = build_set(scene)
    bd = music.band(v)
    w = v.world
    faces = sum(len(o.data.polygons) for o in scene.objects if o.type == "MESH")
    say = print if verbose else (lambda *a: None)
    say("[crammys_set] built in %.1f s: %d faces, %d village lights" % (time.time() - t, faces, len(v.lantern_lights)))
    for p in v.validate():
        bad.append("village: " + p)
    n_ok = 0
    for name, (x, y, z) in sorted(standing_anchors(v).items()):
        under = _solid_at(w, x, y, z - 0.05)
        body = [zz for zz in (z + 0.3, z + 1.0, z + 1.7) if _solid_at(w, x, y, zz)]
        if not under or body:
            bad.append("anchor %s at %s: %s" % (name, tuple(round(c, 2) for c in (x, y, z)),
                                               "nothing solid under it" if not under else "inside a block"))
        else:
            n_ok += 1
    say("[crammys_set] standing anchors on solid ground with the body free: %d" % n_ok)
    for name, pts in v.paths.items():
        if not name.startswith(("crammys_", "bandstand_", "lane_")):
            continue
        for p in pts:
            if _solid_at(w, p[0], p[1], p[2] + 0.3) or _solid_at(w, p[0], p[1], p[2] + 1.6):
                bad.append("path %s: node %s inside a block" % (name, tuple(round(c, 2) for c in p)))
    say("[crammys_set] paths checked: %s" % ", ".join(sorted(k for k in v.paths if k.startswith(
        ("crammys_", "bandstand_", "lane_")))))
    for beat, c in sorted(CAMERAS.items()):
        for key in ("pos", "pos1"):
            if key not in c:
                continue
            cell = tuple(int(math.floor(a)) for a in c[key])
            if _solid_at(w, *c[key]):
                bad.append("camera %s %s %s is inside %s" % (beat, key, c[key], w.block_id(*cell)))
            g = v.ground(c[key][0], c[key][1])
            if g is not None and c[key][2] < g + 0.15:
                bad.append("camera %s %s %s is %.2f above the ground" % (beat, key, c[key], c[key][2] - g))
    say("[crammys_set] cameras checked: %d beats (pos and pos1 outside every block, above the ground)" % len(CAMERAS))
    oak = v.sets["crammys"]["meadow"]["oak"]
    if oak is None or oak["height"] != OAK_HEIGHT:
        bad.append("the skeleton's oak was not planted as asked: %r" % (oak,))
    else:
        low = min(c[2] for c in oak["leaves"])
        sk = v.anchors["crammys_skeleton_oak"]
        if low < sk[2] + hostiles.SKELETON_SIZE[1]:
            bad.append("the oak's leaves start at z %d, under the skeleton's head" % low)
        say("[crammys_set] the skeleton's oak at %s: %d logs, leaves from z %d (the skeleton's head at %.2f)" % (
            OAK, OAK_HEIGHT, low, sk[2] + hostiles.SKELETON_SIZE[1]))
    A = lambda k: v.anchors["crammys_" + k]                                    # noqa: E731
    d_cr = math.dist(A("middle")[:2], A("creeper_line")[:2])
    d_sk = math.dist(A("middle")[:2], A("skeleton_line")[:2])
    if d_cr <= hostiles.FUSE_RANGE:
        bad.append("beat 12: the creeper stands %.2f from the middle, inside its fuse range %g" % (d_cr, hostiles.FUSE_RANGE))
    say("[crammys_set] beat 12 line: creeper %.2f / skeleton %.2f from the middle (fuse range %g)" % (
        d_cr, d_sk, hostiles.FUSE_RANGE))
    say("[crammys_set] band: %r; jukebox %s, pedestal top %s" % (bd, bd.jukebox.cell, bd.pedestal_top))
    for b_ in bad:
        print("[crammys_set] FAIL " + b_)
    print("[crammys_set] check %s (%d failures)" % ("ok" if not bad else "FAILED", len(bad)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bad


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "check":
        sys.exit(1 if check() else 0)
    if args[0] in CAMERAS:
        args = ["still"] + args
    if args and args[0] == "view":
        # view NAME x,y,z tx,ty,tz LENS [FSTOP] [SKY] [WxH] [SAMPLES]
        a = args[1:]
        res = tuple(int(c) for c in a[6].split("x")) if len(a) > 6 else (540, 960)
        view(a[0], _vec(a[1]), _vec(a[2]), float(a[3]), float(a[4]) if len(a) > 4 else 8.0,
             a[5] if len(a) > 5 else "night", res, int(a[7]) if len(a) > 7 else 16)
        sys.exit(0)
    if args and args[0] == "still":
        res, samples, beats, dry, frames, sky = (540, 960), 16, [], False, None, None
        it = iter(args[1:])
        for a in it:
            if a == "--dry":
                dry = True
            elif a == "--res":
                res = tuple(int(c) for c in next(it).split("x"))
            elif a == "--samples":
                samples = int(next(it))
            elif a == "--frames":
                frames = [int(c) for c in next(it).split(",")]
            elif a == "--sky":
                sky = next(it)
            else:
                beats.append(a)
        for b in beats:
            still(b, sky=sky, res=res, samples=samples, dry=dry, frames=frames)
