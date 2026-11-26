"""SIX SECONDS (film six, stories/piglin.json): THE SETS. Film-local; wraps engine/nether.py, edits nothing there.

    from films import sixseconds_set as SS
    bas = SS.build_set(scene)            # nether.build_bastion(scene) + this film's anchors and cameras
    six = bas.sets["sixseconds"]          # dict(anchors, cameras, beats, parts, cutaways, fills, skies)
    A, Y = bas.anchors, bas.yaws          # every anchor of engine/nether.py plus this file's "six_..." ones
    c = bas.cameras[SS.BEAT_CAMERA[22]]   # dict(pos, target, lens, fstop[, pos1, target1], focus, set, sees, ...)
    SS.beat("b22_ingot_close")            # the staging the scouting still was rendered with (cast, pit, lights, ...)

    $BPY -m films.sixseconds_set                  # self-test, no rendering (~3 s): anchors on solid ground, cameras
                                                  #   clear of blocks, what each camera must see in frame and
                                                  #   unhidden (ray-cast), every beat's camera and cast known
    $BPY -m films.sixseconds_set b22_ingot_close b23_gate_reverse      # scouting stills by name (540x960, 16
                                                  #   samples, 2 threads, through render.Session and the Nether
                                                  #   look) -> out/test/sixseconds_set_<key>.png + _zones.png, each
                                                  #   measured by nether.check_still (gold, brute vs blackstone,
                                                  #   piglin skin, Steve's clothes, hero in the safe area)
    $BPY -m films.sixseconds_set group home_a     # a named group (GROUPS: home_a home_b bridge end last); each fits
                                                  #   under `nice -n 15 timeout 290` (10-28 s a still on a busy machine)
    $BPY -m films.sixseconds_set report [keys]    # where each beat's cast lands in its frame (projected), no render
    ... --lo                                      # 270x480, 8 samples, tag _lo (exploring only; no measurements)

WHAT THIS IS. engine/nether.py builds the three bastion sets of this story into one World (home courtyard at
(0, 0, 0) with gateway, guard stair and landing, gold wall and step, the 2 x 2 pit in two states; the bridge at
(400, 0, 0); the treasure corner at (-400, 0, 0)) with anchors and camera suggestions; its docstring is the manual
of the sets (layout, anchors, the pit, the pillar, the flicker, the lights). Nothing in the story needs a block
that set does not have, so nothing is added to the World (a Bastion has no edit hook; extra blocks would be a
second mesh): this file adds what the BEATS need on top of it, as data:
    - anchors "six_..." (bas.anchors / bas.yaws): where each beat's characters and items stand;
    - camera suggestions "six_..." (bas.cameras, same fields as nether's, so nether's check_cameras ray-checks
      them) where nether's suggestion did not give its beat's picture, and for beats 7, 8 and 22, which had none;
    - BEATS: the staging of one scouting still per beat (who stands where facing what, pit / pillar state,
      lights, a film-local key), each rendered at the film's final quality with --zones and looked at;
    - BEAT_CAMERA {beat: camera name} (16 -> the three flash cuts; 23 -> the story's fallback).
The films/hello.py structure (NARRATION, SKIES, SHOTS, the common module and the sequence files) is the lead
director's; this file only builds and describes the set.

COORDINATES. Blender blocks, +X east, +Y north, +Z up; every floor z 0; the pit floor z -2; the landing top z 4;
the gold step's top z 1. Yaw: a character faces -Y at yaw 0 (nether.yaw_to(src, dst)); "NE" = 2.356.

SKY. All scouting stills were made under SUGGESTED_SKIES: preset "nether", biome nether_wastes, for every set (the
story's "dark red haze"). The home bastion and "the older version of the world" (beats 19, 20) MUST share one sky
entry: beat 19 is a pixel match cut on the gate frame. A different biome per world is the lead's choice (fog
colour beyond 10 blocks and the void behind the bridge): crimson_forest looks the same as nether_wastes, soul
sand valley turns the void teal (side by side: out/test/nether_sky_wastes / _crimson / _soul.png); not scouted here.

THE BEATS (camera = bas.cameras[name]; numbers measured on the stills by nether.check_still: hero x / y range in
% of the frame, "brute x" = his median luminance over the blackstone's, >= 1.5 asked; gold hue 43-46 wherever gold
is lit; Steve's shirt hue 172-174 and pants not clipped in every still with Steve; pit, pillar as staged)
   1 six_landing (eye level on the landing's NW corner, 26 mm f/2.8, push in to pos1): the brute at
     six_landing_brute (2.62, 16.4, 4) big at frame left looking just past the lens (six_landing_look), the gold
     wall with its lantern beyond, three piglins' backs at six_b1_pig_1..3 (7.4, 11.7), (7.0, 11.0), (7.3, 9.6)
     small at the gold (heads y 52-55 %), floor whole. brute x 2-49 % y 15-36 % (92 % in the safe area, his far
     ear at the left edge); brute x 2.41 WITH the film-local key "six_key_landing" (shadowless, warm white
     (1.0, 0.95, 0.88), 160 W at (1.45, 17.15, 6.35), this shot only); without it x 1.23 (FAILS 1.5). Not the
     story's LOW LONG lens: the landing is 3 blocks wide (nether's note); a lower lens loses the piglins.
     Lava glow from below: only as the look's under-light, no lava is in this frame.
   2 six_ingot_row (5.0, 17.0, 1.65) -> (7.5, 10.4, 1.45), 36 mm f/2.2: brothers admiring (ingot in the LEFT
     hand at the snout, golden sword in the right) at six_brother_1 (7.0, 13.2) and six_brother_2 (6.3, 10.8),
     yaw NE, the gold wall and its lantern behind; the brute's soft shoulder at the right edge (six_brute_turned
     (4.97, 15.4), facing west). Hero piglin x 8-41 % y 37-54 %.
   3 gate (nether, unchanged): as nether's docstring says; brute on the landing x 20-24 % y 32-36 %, in profile.
   4 six_inside_gate (4.9, 11.0, 0.3) -> (3.6, 18.5, 2.3), 24 mm f/4: nether's inside_gate pulled back 2.2 blocks
     (from there the brute's head on the landing sat under the top icons, y 11-27 %, and the runner's head at the
     gateway in the caption band, y 57-62 %). Runner at home_gateway: head x 62-67 % y 54-57 %; he grows UP the
     frame as he comes at the low lens; the brute small at the upper left (home_landing).
   5 boot (nether, unchanged): boots x 28-69 % y 43-57 % (hero = the boot armor objects, not his head).
   6 pit (nether, pit dug but the last block, cracked): runner at home_rim_w x 15-34 % y 36-46 %, the three
     piglins on home_pit_approach_1..3, the lure ingot at six_pit_lure (5.4, 7.3, -2) on the pit floor. Do not
     put the lure at home_pit_1 (nether's own cast does): that point is inside the kept last block (4, 6, -2).
   7 six_over_pit (2.6, 4.9, 3.3) -> (4.9, 7.0, -0.6), 26 mm f/4 (NEW): behind and above his right shoulder,
     down into the open pit: three piglins admiring at home_pit_2..4 (x 58-80 % y 40-53 %), his shoulder and head
     at the left edge, the pearl resting at six_pearl_rest (3.85, 6.55, 0) beside his boots (y ~55 %).
   8 six_boots_rim (1.75, 4.75, 1.0) -> (3.55, 6.95, 0.05), 40 mm f/2.8 (NEW): the boots at the rim mid-frame
     (x 31-70 % y 38-54 %), gravel at six_gravel_1..7 round his feet, the pearl from beat 7 still at six_pearl_pile
     (= six_pearl_rest). Gravel reads as grey cubes on blackstone: the gilded-rim fallback was NOT needed.
   9 six_rim_side (3.4, 0.8, 1.45) -> (3.1, 7.6, 1.0), 35 mm f/3 (nether's rim_side panned west: there the
     brute at home_strike was at x 10 %): brute with the axe up x 23-38 % y 34-42 %, x 2.59; runner in profile.
  10 six_rim_wide: the same position, 28 mm: brute x 23-40 % y 36-45 %, x 2.79, the puff at home_rim_w, the drops
     at six_drop_boots / _pickaxe / _gravel / _pearl, pit piglins low at the right.
  11 six_bridge_boot (401.55, 3.1, 0.28) -> (400.65, 6.7, 0.15), 45 mm f/2 (NEW; nether's bridge_boot looks
     across the walkway at the void, no bridge in it): along the bridge; the empty frame (still b11_bridge_empty)
     shows the deck receding past the basalt pillars with their gold caps to the lantern on its chain; then the
     boots at bridge_boot_mark x 17-56 % y 43-56 % (the same size as beat 5's). The runner comes from behind the
     lens's left (bridge_run_in passes 1.05 west of the lens). THE LAVA CANNOT BE SEEN from deck level (24 below,
     under the deck's edge): the story's "over an orange lava glow" is not in this picture; nether's bridge_wide
     and beats 13 / 15 show it.
  12 bridge_shoulder (nether): brute x 40-59 % y 39-47 %, x 1.74, under his lantern.
  13 bridge_pillar (nether, pillar in): brute x 30-42 % y 39-46 %, x 2.84; lava at the bottom edge.
  14 bridge_profile (nether, pillar in): brute in profile, head up, x 33-58 % y 18-32 %, x 2.69; ingots at
     six_bridge_ingot_1 / _2 at his feet.
  15 bridge_top (nether, pillar in): brute x 41-51 % y 40-50 %, x 2.48, three ingots at six_bridge_ingot_1..3.
  16 three flash cuts, one camera each, the SAME offset from the brute (5 blocks in front at 1.45, aimed 0.5 above
     his feet, 35 mm f/2.8: nether's 'flash' cameras aim at 1.3 and put his feet and the drops in the caption
     band): six_flash_bridge / six_flash_treasure / six_flash_home. The brute at bridge_flash / treasure_flash /
     home_flash x 38-62 % y 20-30 % in all three (locked), x 1.65 / 3.08 / 1.74; puff at six_flash_puff_<set>,
     golden boots at six_flash_boots_<set>, the extra drop at six_flash_extra_<set> (gravel / pearl / pickaxe).
  17 corridor (nether): brute in the gateway x 26-42 % y 42-49 %, x 4.20 (the corridor lava is his key).
  18 gate: brute at home_gateway (back to us) x 35-40 % y 54-55 %, x 1.59; bas.lava_flicker on the shot.
  19 gate: no brute; the runner on home_run_past through his spot (still: at (5.6, 15.0)) x 45-51 % y 54-56 %.
  20 pit (pit dug): four piglins admiring at home_pit_1..4, runner at home_rim_w, gravel and a pearl at his feet.
  21 six_ingot_row (the frame of beat 2): brothers as in beat 2, the brute at six_brute_gold (7.6, 10.0) yaw NE
     between them, head down at six_step_ingot (8.16, 11.71, 1.0) on the step: brute x 40-59 % y 42-50 %, x 2.93.
     THE INGOT ITSELF IS HIDDEN behind brother 1 in this frame (searched: no camera spot free in this courtyard
     holds the brute, both brothers AND his ingot apart; the near brother always covers it or the frame needs a
     lens under 20 mm). He visibly looks down at something; beat 22 shows it.
  22 six_ingot_close (8.84, 13.8, 1.62) -> (8.0, 11.2, 1.3), 35 mm f/2, push in to pos1 (NEW): on the step, on his
     line of sight beyond the ingot: the ingot sharp in the middle (y 44-58 %), his whole face (eyes, snout,
     tusks) right above it (brute x 35-66 % y 28-45 %), x 3.17, the gold lantern over the step on his snout.
     Below his eye height (1.79). The brothers are outside the frame. The layout of 21-23 exists for this shot:
     the step is one block wide, so only a brute facing NE with the ingot NNE of him (bearing 18 deg, 1.8 away,
     head pitch 21 deg) leaves room for a camera beyond the ingot.
  23 six_gate_reverse (3.5, 17.5, 0.45) -> (7.2, 10.4, 1.3), 36 mm f/2.8: THE STORY'S FALLBACK ("reverse angle
     from the gateway, floor level, the empty blackstone in the foreground under the caption word and the brute's
     face lifting toward the lens"): the brute at six_brute_gold looks at six_gateway_mouth (head turn 65 deg of
     the piglin's 75) and so nearly into the lens: x 40-53 % y 43-48 %, x 2.69; brother 2 heads-down beside him,
     brother 1 soft at the left edge, the gold wall and its lantern, empty floor under the caption band.
     The scripted picture (the gate frame, ending in "clean profile, snout against the glow") cannot be had:
     from any camera in the courtyard's south part the gateway lies behind a brute at the gold, and his body to
     the gold plus the 75 deg head limit cannot turn his face to it (still b23_gate: x 77-88 %, 39 % in the safe
     area, the back of his head, x 1.26: FAILS). The gate frame stays for beats 3, 18 and 19.

ANCHORS ADDED (bas.anchors, yaw in bas.yaws where it is a standing place)
    six_landing_brute (2.62, 16.4, 4) facing the six_landing lens; six_landing_look (0.15, 16.7, 5.55);
    six_b1_pig_1..3 (7.4, 11.7) (7.0, 11.0) (7.3, 9.6) facing east;
    six_brother_1 (7.0, 13.2), six_brother_2 (6.3, 10.8), six_brute_gold (7.6, 10.0): yaw NE (2.356);
    six_brute_turned (4.97, 15.4) facing west; six_step_ingot (8.16, 11.71, 1.0); six_gateway_mouth (4.5, 18.6, 1.8);
    six_pit_lure (5.4, 7.3, -2); six_pearl_rest = six_pearl_pile (3.85, 6.55); six_gravel_1..7 round home_rim_w
    (3.6, 7.0), all on the floor west of the pit's edge (x <= 3.85); six_drop_boots (2.9, 7.6), _pickaxe (3.3,
    8.1), _gravel (2.6, 8.0), _pearl (3.8, 7.9); six_pillar_brute = bridge_pillar_foot + PILLAR_BRUTE_SHIFT (0.5, 0)
    = (401.0, 18.25) facing north (the brute at the pillar in beats 13-15); six_bridge_ingot_1..3 = six_pillar_brute +
    PILLAR_INGOTS (0.75, -0.1), (0.6, -0.4), (0.45, -0.65) (on his east side: seen from the east cameras of beats 13 /
    14 and from beat 15's high camera); six_flash_puff_<set> = <set>_flash + FLASH_OFFSETS puff (0.95, 0.3), _boots_
    (-0.85, -0.35), _extra_ (0.55, -0.15) for set in home, bridge, treasure (the boots on the brute's left, clear of
    the puff). The lead director's review pass moved these three groups (the first spots: the ingots south of the
    foot, behind his body; the boots at (0.7, 0.1) under the puff at (1.2, -0.2)); the beat stills below were made
    with the first ones.
    Items are dropped items (piglins.add_item): an item's spot is where it RESTS (pass it as an explicit floor
    point to piglins.barter(lob=True, toward=...) and throw_item: toward=<the runner> at the rim rests over the
    open pit, an engine.piglins issue noted by the nether module).

PARTS (what changes on camera; all engine/nether.py's): bas.pit_blocks / bas.pit_last / bas.pit_open(shot,
keep=[bas.pit_last.cell]) / bas.pit_drop / bas.pit_fill; bas.pillar_in(shot) / pillar_from(frame) (absent
otherwise); bas.lava_flicker(f0, f1); bas.chests (the treasure corner's two). parts(bas) lists them.
CUTAWAYS (nether's): home_corridor_roof, home_south_parapet, treasure_west_wall. None is used by a scouted beat.
PIT CONTINUITY: every scouted home beat outside 6-10 and 20 has no pit_open call: the floor is whole (stills 1-5,
16c, 17-19, 21-23 show it whole).
FILMS-LOCAL LIGHT: FILLS {name: (pos, watts)}: only "six_key_landing" (beat 1). Lantern levels per beat: BEATS
"lights" (st.lights(s, 1.0, groups=..., **bas.lights_for(set))): home_pit x 2 in beats 6-10 and 20 (as nether's
pit camera; without it the pit piglins' skin went to saturation 0.62 in beat 9), everything else 1.0.

STAGING NOTES FOR THE DIRECTORS (facts found while scouting; not fixed here)
    - Beat 9: home_strike is due west of home_rim_w, so the brute's hit knocks the runner EAST, over the open pit
      (players.hurt knock-back 1.99 blocks). Use a small knockback / max_back, or cut on the knock-back as written.
    - Beats 21-23: the brute faces NE (not east) so that his head can reach the gateway in 23; his ingot is in front
      of his chest 17 deg to his left. The brothers stand where beat 2 has them.
    - Beat 22's close-up sees nothing of the brothers; nothing needs hiding.
    - A piglin's / brute's head pitch stops at 40 deg: the step ingot needs 21 (fine); a brute at home_gold_4 with
      the nether's step item would need the head yaw 0 and pitch 33.

NOT VERIFIED: motion (every still is one frame of a static 1-second staging; the pushes of beats 1 and 22 were seen
at their middle only; walks, the dig, the drops, the throws, pit_drop, the flicker over time were not animated
here); the final 720x1280 quality (not this film's final; 540x960 / 16 is); palette_check at 360x640 phone size;
other biomes; the beat-13 / -15 composition with the falling ingot in the air.
"""
import math
import os
import sys
import types

import bpy  # noqa: F401  (makes mathutils importable)
from mathutils import Vector

from engine import nether

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL_RES, FINAL_SAMPLES = (540, 960), 16
SET_NAME = "sixseconds"
NE = math.atan2(1.0, 1.0) + math.pi / 2.0          # yaw facing north-east (nether._yaw((1, 1)) = 2.356)

# the skies every scouting still was made under (a suggestion for films/sixseconds.py SKIES)
SUGGESTED_SKIES = {
    "home": dict(preset="nether", biome="nether_wastes"),
    "bridge": dict(preset="nether", biome="nether_wastes"),
    "treasure": dict(preset="nether", biome="nether_wastes"),
}

# film-local lights: name -> (position, watts); warm white, shadowless, keyed on only in the shots that use them
KEY_COLOR = (1.0, 0.95, 0.88)
FILLS = {"six_key_landing": ((1.45, 17.15, 6.35), 160.0)}      # beat 1: the brute's key (x 1.23 -> 2.41)


# beats 13-15: the brute's place at the pillar = bridge_pillar_foot + this; the ingots he ignores = that place + these
PILLAR_BRUTE_SHIFT = (0.5, 0.0)
PILLAR_INGOTS = ((0.75, -0.1), (0.6, -0.4), (0.45, -0.65))
# beat 16: the puff, the golden boots and the extra drop beside the brute's flash place (the same in every world)
FLASH_OFFSETS = {"puff": (0.95, 0.3), "boots": (-0.85, -0.35), "extra": (0.55, -0.15)}


def _yaw(direction):
    """Yaw of a character facing a compass direction ('north' ...) or an (dx, dy) vector."""
    return nether._yaw(direction)


def _add(p, d):
    return (p[0] + d[0], p[1] + d[1], p[2] + (d[2] if len(d) > 2 else 0.0))


# ---------------------------------------------------------------------------------------------------------------
# anchors (bas.anchors / bas.yaws; every name starts with "six_")
# ---------------------------------------------------------------------------------------------------------------
def _anchors(bas):
    A, Y = bas.anchors, bas.yaws
    out = {}

    def put(name, p, yaw=None):
        p = tuple(float(v) for v in p)
        A[name] = p
        out[name] = p
        if yaw is not None:
            Y[name] = float(yaw)

    # beat 1: the brute on the landing left of the line from six_landing to the gold, three piglins clear of him
    put("six_landing_brute", (2.62, 16.4, 4.0), nether.yaw_to((2.62, 16.4), (0.4, 17.4)))
    put("six_landing_look", (0.15, 16.7, 5.55))                 # just past the six_landing lens
    for k, xy in enumerate(((7.4, 11.7), (7.0, 11.0), (7.3, 9.6)), 1):
        put("six_b1_pig_%d" % k, (xy[0], xy[1], 0.0), _yaw("east"))
    # beats 2 and 21-23: the gold row. The brute at its SOUTH end facing NE, his ingot on the step NNE of him (in
    # front of his chest, 17 deg left of straight ahead, 1.8 away, head pitch 21 deg); the brothers where the
    # ingot-row frame keeps them apart from him and the reverse angle of beat 23 keeps them off his face
    put("six_brute_gold", (7.6, 10.0, 0.0), NE)
    put("six_step_ingot", (8.16, 11.71, 1.0))
    put("six_brother_1", (7.0, 13.2, 0.0), NE)
    put("six_brother_2", (6.3, 10.8, 0.0), NE)
    put("six_brute_turned", (4.97, 15.4, 0.0), _yaw("west"))    # beat 2: his soft shoulder at the right edge
    put("six_gateway_mouth", (4.5, 18.6, 1.8))                  # beat 23: what he turns his head to
    # the pit (beats 6-10, 20)
    rim = A["home_rim_w"]
    put("six_pit_lure", (5.4, 7.3, -2.0))                       # beat 6: the lure on the pit floor (not in the kept
    #                                                               last block's cell (4, 6))
    put("six_pearl_rest", _add(rim, (0.25, -0.45)))             # beat 7: the pearl lands beside the boots
    gravel = [(-0.45, 0.2), (-0.35, -0.35), (0.15, -0.45), (0.2, 0.45), (-0.2, 0.5), (-0.55, -0.1), (0.22, -0.28)]
    for k, d in enumerate(gravel, 1):                           # beats 8, 20: round his boots, west of the pit edge
        put("six_gravel_%d" % k, _add(rim, d))
    put("six_pearl_pile", A["six_pearl_rest"])                  # beat 8: beat 7's pearl, still lying there
    drops = {"boots": (-0.7, 0.6), "pickaxe": (-0.3, 1.1), "gravel": (-1.0, 1.0), "pearl": (0.2, 0.9)}
    for k, d in drops.items():                                  # beat 10: what the runner drops
        put("six_drop_%s" % k, _add(rim, d))
    # the bridge (beats 13-15): the brute's place at the pillar and the ingots he ignores. The lead's review pass:
    # he stands 0.5 EAST of bridge_pillar_foot in all three pillar shots (from bridge_top the pillar's top block cut
    # his face in half at the foot), and his ingots lie on his EAST side, between him and the deck's open edge (the
    # first spots, south of the foot, were behind his body from both the east and the high north-east camera)
    foot = A["bridge_pillar_foot"]
    pb = _add(foot, PILLAR_BRUTE_SHIFT)
    put("six_pillar_brute", pb, Y["bridge_pillar_foot"])
    for k, d in enumerate(PILLAR_INGOTS, 1):
        put("six_bridge_ingot_%d" % k, _add(pb, d))
    # beat 16: the same three spots in every flash cut (each flash camera looks north at him: +x is frame right).
    # The lead's review pass: the golden boots on the LEFT of him, the puff behind his right side, the extra drop in
    # front of the puff (the first spots put the boots under the puff: hidden in two of the three cuts)
    for s in ("home", "bridge", "treasure"):
        f = A["%s_flash" % s]
        put("six_flash_puff_%s" % s, _add(f, FLASH_OFFSETS["puff"]))
        put("six_flash_boots_%s" % s, _add(f, FLASH_OFFSETS["boots"]))
        put("six_flash_extra_%s" % s, _add(f, FLASH_OFFSETS["extra"]))
    return out


# ---------------------------------------------------------------------------------------------------------------
# camera suggestions (bas.cameras, nether's fields; every name starts with "six_")
# ---------------------------------------------------------------------------------------------------------------
NEW_CAMERAS = {
    # beat 1: eye level on the landing's NW corner; a slow push in to pos1
    "six_landing": dict(pos=(0.4, 17.4, 5.8), target=(6.0, 13.6, 3.4), lens=26.0, fstop=2.8, beats=(1,),
                        pos1=(0.62, 17.25, 5.76), set="home", focus="six_landing_brute",
                        sees=("six_landing_brute:head", "six_b1_pig_1:head", "six_b1_pig_2:head",
                              "six_b1_pig_3:head")),
    # beats 2 and 21 (the ingot row frame): snout height from the north-west along the gold wall
    "six_ingot_row": dict(pos=(5.0, 17.0, 1.65), target=(7.5, 10.4, 1.45), lens=36.0, fstop=2.2, beats=(2, 21),
                          set="home", focus="six_step_ingot",
                          sees=("six_brother_1:head", "six_brother_2:head", "six_brute_gold:head")),
    # beat 4: nether's inside_gate pulled back 2.2 blocks
    "six_inside_gate": dict(pos=(4.9, 11.0, 0.3), target=(3.6, 18.5, 2.3), lens=24.0, fstop=4.0, beats=(4,),
                            set="home", focus="home_gateway", sees=("home_landing:head", "home_gateway")),
    # beat 7: behind and above the runner's right shoulder at the west rim, down into the pit
    "six_over_pit": dict(pos=(2.6, 4.9, 3.3), target=(4.9, 7.0, -0.6), lens=26.0, fstop=4.0, beats=(7,),
                         set="home", pit="open", focus="home_pit_center", lights={"home_pit": 2.0},
                         sees=("home_pit_2:head", "home_pit_3:head", "home_pit_4:head")),
    # beat 8: low on the floor south-west of the boots at the rim
    "six_boots_rim": dict(pos=(1.75, 4.75, 1.0), target=(3.55, 6.95, 0.05), lens=40.0, fstop=2.8, beats=(8,),
                          set="home", pit="open", focus="home_rim_w", lights={"home_pit": 2.0},
                          sees=("home_rim_w:shins",)),
    # beats 9 and 10: nether's rim_side moved 0.2 west and panned west; 10 = the same place, wider
    "six_rim_side": dict(pos=(3.4, 0.8, 1.45), target=(3.1, 7.6, 1.0), lens=35.0, fstop=3.0, beats=(9,),
                         set="home", pit="open", focus="home_rim_w", lights={"home_pit": 2.0},
                         sees=("home_rim_w", "home_strike")),
    "six_rim_wide": dict(pos=(3.4, 0.8, 1.45), target=(3.3, 7.6, 0.85), lens=28.0, fstop=3.2, beats=(10,),
                         set="home", pit="open", focus="home_rim_w", lights={"home_pit": 2.0},
                         sees=("home_rim_w", "home_strike")),
    # beat 11: the boot shot on the bridge, along it
    "six_bridge_boot": dict(pos=(401.55, 3.1, 0.28), target=(400.65, 6.7, 0.15), lens=45.0, fstop=2.0, beats=(11,),
                            set="bridge", focus="bridge_boot_mark", sees=("bridge_boot_mark:shins",)),
    # beat 16: the three flash cuts, the same offset from the brute in every world
    "six_flash_home": dict(pos=(4.5, 9.5, 1.45), target=(4.5, 14.5, 0.5), lens=35.0, fstop=2.8, beats=(16,),
                           set="home", focus="home_flash", sees=("home_flash",)),
    "six_flash_bridge": dict(pos=(400.5, 11.5, 1.45), target=(400.5, 16.5, 0.5), lens=35.0, fstop=2.8, beats=(16,),
                             set="bridge", focus="bridge_flash", sees=("bridge_flash",)),
    "six_flash_treasure": dict(pos=(-396.0, -4.2, 1.45), target=(-396.0, 0.8, 0.5), lens=35.0, fstop=2.8,
                               beats=(16,), set="treasure", focus="treasure_flash", sees=("treasure_flash",)),
    # beat 22: on the step beyond the ingot, on his line of sight; a slow push in to pos1
    "six_ingot_close": dict(pos=(8.84, 13.8, 1.62), target=(8.0, 11.2, 1.3), lens=35.0, fstop=2.0, beats=(22,),
                            pos1=(8.8, 13.68, 1.61), set="home", focus="six_step_ingot",
                            sees=("six_brute_gold:head",)),
    # beat 23 (the story's fallback): reverse angle from the gateway's west jamb, floor level
    "six_gate_reverse": dict(pos=(3.5, 17.5, 0.45), target=(7.2, 10.4, 1.3), lens=36.0, fstop=2.8, beats=(23,),
                             set="home", focus="six_brute_gold", sees=("six_brute_gold",)),
}

# the camera of each beat (16: the three flash cuts in story order; 23: the fallback, the gate frame cannot give it)
BEAT_CAMERA = {1: "six_landing", 2: "six_ingot_row", 3: "gate", 4: "six_inside_gate", 5: "boot", 6: "pit",
               7: "six_over_pit", 8: "six_boots_rim", 9: "six_rim_side", 10: "six_rim_wide",
               11: "six_bridge_boot", 12: "bridge_shoulder", 13: "bridge_pillar", 14: "bridge_profile",
               15: "bridge_top", 16: ("six_flash_bridge", "six_flash_treasure", "six_flash_home"),
               17: "corridor", 18: "gate", 19: "gate", 20: "pit", 21: "six_ingot_row", 22: "six_ingot_close",
               23: "six_gate_reverse"}

# ---------------------------------------------------------------------------------------------------------------
# THE BEATS: the staging of each scouting still. cast entries (kind, where, look, opts):
#   kind  brute | piglin | piglin_admire | steve (golden boots, iron pickaxe) | steve_ingot (holds an ingot) |
#         steve_crouch | item:<id> (a dropped item resting there) | poof (a death puff 8 frames old)
#   where / look  an anchor name or a point; opts dict(yaw=, aggro=True)
# other keys: cam, sky, set, pit None|'open'|'keep', pillar, flicker, lights {group: scale}, fills [FILLS names],
#   hero brute|piglin|steve|boots|None (what nether.check_still keeps in the safe area)
# ---------------------------------------------------------------------------------------------------------------
G3 = [("piglin", "home_gold_%d" % k, "home_gold_target", {}) for k in (1, 2, 3)]
PIT = {"home_pit": 2.0}
ROW = [("piglin_admire", "six_brother_1", None, {}), ("piglin_admire", "six_brother_2", None, {})]
WEST = _yaw("west")

BEATS = [
    dict(key="b01_landing", beat=1, cam="six_landing", sky="home", set="home",
         cast=[("brute", "six_landing_brute", "six_landing_look", {})] +
              [("piglin", "six_b1_pig_%d" % k, "home_gold_target", {}) for k in (1, 2, 3)],
         fills=["six_key_landing"], hero="brute"),
    dict(key="b02_ingot_row", beat=2, cam="six_ingot_row", sky="home", set="home",
         cast=ROW + [("brute", "six_brute_turned", None, {})], hero="piglin"),
    dict(key="b03_gate", beat=3, cam="gate", sky="home", set="home",
         cast=[("brute", "home_landing", "home_landing_look", {})] + G3, hero="brute"),
    dict(key="b04_inside_gate", beat=4, cam="six_inside_gate", sky="home", set="home",
         cast=[("steve", "home_gateway", None, dict(yaw=_yaw("south"))), ("brute", "home_landing", "home_gateway", {})],
         hero="steve"),
    dict(key="b05_boot", beat=5, cam="boot", sky="home", set="home",
         cast=[("steve", "home_boot_mark", None, {})] +
              [("piglin", "home_gold_%d" % k, "home_boot_mark", {}) for k in (1, 2, 3)], hero="boots"),
    dict(key="b06_pit", beat=6, cam="pit", sky="home", set="home", pit="keep",
         cast=[("steve", "home_rim_w", "home_pit_center", {}), ("item:gold_ingot", "six_pit_lure", None, {})] +
              [("piglin", "home_pit_approach_%d" % k, "home_pit_center", {}) for k in (1, 2, 3)],
         lights=PIT, hero="steve"),
    dict(key="b07_over_pit", beat=7, cam="six_over_pit", sky="home", set="home", pit="open",
         cast=[("steve_ingot", "home_rim_w", "home_pit_center", {}), ("item:ender_pearl", "six_pearl_rest", None, {})] +
              [("piglin_admire", "home_pit_%d" % k, None, dict(yaw=WEST)) for k in (2, 3, 4)],
         lights=PIT, hero="piglin"),
    dict(key="b08_boots_rim", beat=8, cam="six_boots_rim", sky="home", set="home", pit="open",
         cast=[("steve", "home_rim_w", "home_pit_center", {}), ("item:ender_pearl", "six_pearl_pile", None, {})] +
              [("item:gravel", "six_gravel_%d" % k, None, {}) for k in range(1, 8)],
         lights=PIT, hero="boots"),
    dict(key="b09_rim_side", beat=9, cam="six_rim_side", sky="home", set="home", pit="open",
         cast=[("steve", "home_rim_w", "home_pit_center", {}), ("brute", "home_strike", "home_rim_w", dict(aggro=True))] +
              [("piglin_admire", "home_pit_%d" % k, None, dict(yaw=WEST)) for k in (2, 3, 4)],
         lights=PIT, hero="brute"),
    dict(key="b10_rim_wide", beat=10, cam="six_rim_wide", sky="home", set="home", pit="open",
         cast=[("brute", "home_strike", "home_rim_w", {}), ("poof", "home_rim_w", None, {}),
               ("item:golden_boots", "six_drop_boots", None, {}), ("item:iron_pickaxe", "six_drop_pickaxe", None, {}),
               ("item:gravel", "six_drop_gravel", None, {}), ("item:ender_pearl", "six_drop_pearl", None, {})] +
              [("piglin_admire", "home_pit_%d" % k, None, dict(yaw=WEST)) for k in (2, 3, 4)],
         lights=PIT, hero="brute"),
    dict(key="b11_bridge_empty", beat=11, cam="six_bridge_boot", sky="bridge", set="bridge", cast=[], hero=None),
    dict(key="b11_bridge_boot", beat=11, cam="six_bridge_boot", sky="bridge", set="bridge",
         cast=[("steve", "bridge_boot_mark", None, {})], hero="boots"),
    dict(key="b12_bridge_shoulder", beat=12, cam="bridge_shoulder", sky="bridge", set="bridge",
         cast=[("steve", "bridge_player", "bridge_player_look", {}), ("brute", "bridge_brute", "bridge_brute_look", {})],
         hero="brute"),
    dict(key="b13_bridge_pillar", beat=13, cam="bridge_pillar", sky="bridge", set="bridge", pillar=True,
         cast=[("steve_crouch", "bridge_pillar_top", None, {}),
               ("brute", "six_pillar_brute", "bridge_pillar_top_target", {})], hero="brute"),
    dict(key="b14_bridge_profile", beat=14, cam="bridge_profile", sky="bridge", set="bridge", pillar=True,
         cast=[("brute", "six_pillar_brute", "bridge_pillar_top_target", {}),
               ("item:gold_ingot", "six_bridge_ingot_1", None, {}), ("item:gold_ingot", "six_bridge_ingot_2", None, {})],
         hero="brute"),
    dict(key="b15_bridge_top", beat=15, cam="bridge_top", sky="bridge", set="bridge", pillar=True,
         cast=[("steve_crouch", "bridge_pillar_top", None, {}), ("brute", "six_pillar_brute", (400.5, 19.6, 4.6), {})] +
              [("item:gold_ingot", "six_bridge_ingot_%d" % k, None, {}) for k in (1, 2, 3)], hero="brute"),
    dict(key="b16a_bridge_flash", beat=16, cam="six_flash_bridge", sky="bridge", set="bridge",
         cast=[("brute", "bridge_flash", None, {}), ("poof", "six_flash_puff_bridge", None, {}),
               ("item:golden_boots", "six_flash_boots_bridge", None, {}),
               ("item:gravel", "six_flash_extra_bridge", None, {})], hero="brute"),
    dict(key="b16b_treasure_flash", beat=16, cam="six_flash_treasure", sky="treasure", set="treasure",
         cast=[("brute", "treasure_flash", None, {}), ("poof", "six_flash_puff_treasure", None, {}),
               ("item:golden_boots", "six_flash_boots_treasure", None, {}),
               ("item:ender_pearl", "six_flash_extra_treasure", None, {})], hero="brute"),
    dict(key="b16c_home_flash", beat=16, cam="six_flash_home", sky="home", set="home",
         cast=[("brute", "home_flash", None, {}), ("poof", "six_flash_puff_home", None, {}),
               ("item:golden_boots", "six_flash_boots_home", None, {}),
               ("item:iron_pickaxe", "six_flash_extra_home", None, {})], hero="brute"),
    dict(key="b17_corridor", beat=17, cam="corridor", sky="home", set="home",
         cast=[("brute", "home_gateway", None, {})] + G3, hero="brute"),
    dict(key="b18_gate", beat=18, cam="gate", sky="home", set="home", flicker=True,
         cast=[("brute", "home_gateway", None, {})] + G3, hero="brute"),
    dict(key="b19_gate", beat=19, cam="gate", sky="home", set="home",
         cast=[("steve", (5.6, 15.0, 0.0), None, dict(yaw=nether.yaw_to((4.5, 19.0), (6.4, 9.0))))] + G3,
         hero="steve"),
    dict(key="b20_pit", beat=20, cam="pit", sky="home", set="home", pit="open",
         cast=[("steve", "home_rim_w", "home_pit_center", {})] +
              [("piglin_admire", "home_pit_%d" % k, None, dict(yaw=WEST if k in (2, 4) else _yaw("south")))
               for k in (1, 2, 3, 4)] +
              [("item:gravel", "six_gravel_%d" % k, None, {}) for k in (1, 3, 5)] +
              [("item:ender_pearl", "six_pearl_rest", None, {})],
         lights=PIT, hero="piglin"),
    dict(key="b21_ingot_row", beat=21, cam="six_ingot_row", sky="home", set="home",
         cast=ROW + [("brute", "six_brute_gold", "six_step_ingot", {}), ("item:gold_ingot", "six_step_ingot", None, {})],
         hero="brute"),
    dict(key="b22_ingot_close", beat=22, cam="six_ingot_close", sky="home", set="home",
         cast=[("brute", "six_brute_gold", "six_step_ingot", {}), ("item:gold_ingot", "six_step_ingot", None, {})],
         hero="brute"),
    dict(key="b23_gate_reverse", beat=23, cam="six_gate_reverse", sky="home", set="home",
         cast=[("brute", "six_brute_gold", "six_gateway_mouth", {}), ("item:gold_ingot", "six_step_ingot", None, {})]
         + ROW, hero="brute"),
    dict(key="b23_gate", beat=23, cam="gate", sky="home", set="home",       # the scripted frame: shows why not
         cast=[("brute", "six_brute_gold", "six_gateway_mouth", {}), ("item:gold_ingot", "six_step_ingot", None, {})]
         + ROW, hero="brute"),
]
BEAT_KEYS = [b["key"] for b in BEATS]
GROUPS = {   # render groups that fit one `nice -n 15 timeout 290` command each (measured 6-28 s a still)
    "home_a": ["b01_landing", "b02_ingot_row", "b03_gate", "b04_inside_gate", "b05_boot", "b06_pit"],
    "home_b": ["b07_over_pit", "b08_boots_rim", "b09_rim_side", "b10_rim_wide", "b16c_home_flash"],
    "bridge": ["b11_bridge_empty", "b11_bridge_boot", "b12_bridge_shoulder", "b13_bridge_pillar",
               "b14_bridge_profile", "b15_bridge_top", "b16a_bridge_flash"],
    "end": ["b16b_treasure_flash", "b17_corridor", "b18_gate", "b19_gate", "b20_pit"],
    "last": ["b21_ingot_row", "b22_ingot_close", "b23_gate_reverse", "b23_gate"],
}


# ---------------------------------------------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------------------------------------------
def _cameras(bas):
    """Add NEW_CAMERAS to bas.cameras (nether's fields; the cast of the first beat that uses each, in nether's
    (kind, anchor, look[, yaw]) form, for nether's own tools)."""
    out = {}
    for name, c in NEW_CAMERAS.items():
        first = next((b for b in BEATS if b["cam"] == name), None)
        cast = []
        for kind, where, look, opts in (first["cast"] if first else ()):
            k = "ingot" if kind == "item:gold_ingot" else "steve" if kind == "steve_ingot" else kind
            if k in ("brute", "piglin", "piglin_admire", "steve", "steve_crouch", "ingot") and isinstance(where, str):
                entry = (k, where, look if isinstance(look, str) else None)
                cast.append(entry + ((opts["yaw"],) if "yaw" in opts else ()))
        d = dict(pos=tuple(c["pos"]), target=tuple(c["target"]), lens=float(c["lens"]), fstop=c["fstop"],
                 beats=tuple(c["beats"]), note=c.get("note", ""), set=c["set"], cast=tuple(cast),
                 sees=tuple(c.get("sees", ())), pit=c.get("pit"), pillar=bool(c.get("pillar")),
                 focus=c.get("focus"), lights=dict(c.get("lights") or {}))
        for k in ("pos1", "target1"):
            if k in c:
                d[k] = tuple(c[k])
        bas.cameras[name] = d
        out[name] = d
    return out


def build_set(scene, layout=None):
    """The bastion sets of "Six Seconds" (engine.nether.build_bastion) with this film's anchors and camera
    suggestions added. Returns the Bastion; bas.sets['sixseconds'] = dict(anchors, cameras, beats, beat_camera,
    parts, cutaways, fills, skies)."""
    bas = nether.build_bastion(scene, layout=layout)
    anchors = _anchors(bas)
    cams = _cameras(bas)
    bas.sets[SET_NAME] = dict(anchors=anchors, cameras=cams, beats={b["key"]: b for b in BEATS},
                              beat_camera=dict(BEAT_CAMERA), parts=parts(bas), cutaways=sorted(bas.cutaways),
                              fills=dict(FILLS), skies=dict(SUGGESTED_SKIES))
    return bas


def parts(bas):
    """What changes on camera: name -> what it is and how a film drives it (all of them engine/nether.py's)."""
    return {
        "pit_blocks": "bas.pit_blocks: 8 engine.breaking Breakables, cells x 4..5, y 6..7, z -1 / -2; "
                      "bas.pit_open(shot[, keep=[bas.pit_last.cell]]): dug in that shot only",
        "pit_last": "bas.pit_last (cell %s): breaking.mine(runner, bas.pit_last, f, camera=s) (beat 6)"
                    % (bas.pit_last.cell,),
        "pit_drop": "bas.pit_drop(piglins, f): three piglins step off the rim, land at f + 23 / 35 / 47",
        "pit_fill": "bas.pit_fill: 9 W shadowless, keyed on by pit_open only",
        "pillar": "bas.pillar (3 netherrack Breakables at %s): bas.pillar_in(shot) / bas.pillar_from(frame)"
                  % ([b.cell for b in bas.pillar],),
        "lava_flicker": "bas.lava_flicker(f0, f1): the corridor's lava light (beat 18)",
        "chests": "bas.chests: %s (engine.fixtures Chest: open / close)" % sorted(bas.chests),
    }


def beat(key):
    """The BEATS entry `key` ('b07_over_pit')."""
    for b in BEATS:
        if b["key"] == key:
            return b
    raise KeyError("no beat %r (beats: %s)" % (key, ", ".join(BEAT_KEYS)))


def beat_camera(bas, number):
    """The camera spec(s) of story beat `number` (1..23): a dict, or a tuple of three for beat 16."""
    name = BEAT_CAMERA[int(number)]
    return tuple(bas.cameras[n] for n in name) if isinstance(name, tuple) else bas.cameras[name]


# ---------------------------------------------------------------------------------------------------------------
# checks (no rendering)
# ---------------------------------------------------------------------------------------------------------------
def check(bas, verbose=True):
    """Problems (empty = all good): an anchor with nothing solid under it, or inside a block, or off the ground;
    a camera within 0.12 of a block; what a camera `sees` out of its frame or hidden (nether's check_cameras);
    a beat whose camera or cast anchor does not exist."""
    out = []
    w = bas.world
    pit_cols = {(c[0], c[1]) for c in bas.pit_blocks}
    pillar_cols = {(b.cell[0], b.cell[1]) for b in bas.pillar}
    for name, p in sorted(bas.anchors.items()):
        if name.endswith(("_target", "_center", "_cam", "_look", "_mouth")) or "_look" in name:
            continue
        x, y, z = p
        cx, cy = int(math.floor(x)), int(math.floor(y))
        below = int(math.floor(z - 0.01))
        support = w.block_id(cx, cy, below)
        if (cx, cy) in pit_cols and z > -1.5:
            support = support or "pit block"
        if (cx, cy) in pillar_cols and z > 0.5:
            support = support or "netherrack pillar"
        if not support:
            out.append("anchor %s at %s: nothing under it (cell %s)" % (name, p, (cx, cy, below)))
        elif support in ("lantern", "iron_chain", "chain"):
            out.append("anchor %s at %s stands on a %s" % (name, p, support))
        g = bas.ground(x, y)
        if (cx, cy) not in pit_cols | pillar_cols and (g is None or abs(g - z) > 0.02):
            out.append("anchor %s at z %.2f, the ground there is %s" % (name, z, g))
        for cz in (int(math.floor(z + 0.2)), int(math.floor(z + 1.2))):
            bid = w.block_id(cx, cy, cz)
            if bid and w.is_solid(cx, cy, cz) and not bid.endswith(("_stairs", "_slab")):
                out.append("anchor %s inside %s" % (name, bid))
    for name, c in sorted(bas.cameras.items()):
        px, py, pz = c["pos"]
        near = sorted({(int(math.floor(px + dx)), int(math.floor(py + dy)), int(math.floor(pz + dz)))
                       for dx in (-0.12, 0.12) for dy in (-0.12, 0.12) for dz in (-0.12, 0.12)})
        hit = [cell for cell in near if w.is_full_cube(*cell) or w.is_solid(*cell)]
        if hit:
            out.append("camera %s within 0.12 of %s at %s" % (name, w.block_id(*hit[0]), hit[0]))
    out += bas.check_cameras()
    for b in BEATS:
        if b["cam"] not in bas.cameras:
            out.append("beat %s: no camera %s" % (b["key"], b["cam"]))
        for _kind, where, look, _o in b["cast"]:
            for a in (where, look):
                if isinstance(a, str) and a not in bas.anchors:
                    out.append("beat %s: no anchor %s" % (b["key"], a))
        for f in b.get("fills", ()):
            if f not in FILLS:
                out.append("beat %s: no fill %s" % (b["key"], f))
    for n, name in BEAT_CAMERA.items():
        for nm in (name if isinstance(name, tuple) else (name,)):
            if nm not in bas.cameras:
                out.append("beat %d: no camera %s" % (n, nm))
    if verbose:
        for o in out:
            print("[sixseconds_set] PROBLEM", o)
    return out


def report(bas, key):
    """Where the cast of a beat lands in its camera's frame: [(kind, where, feet (u, v), head (u, v))], u v 0..1
    from the top left (nether.project; no render)."""
    b = beat(key)
    c = bas.cameras[b["cam"]]
    rows = []
    for kind, where, _look, _o in b["cast"]:
        p = bas.anchors[where] if isinstance(where, str) else where
        h = {"brute": 2.0, "piglin": 2.0, "piglin_admire": 2.0, "steve": 1.875, "steve_ingot": 1.875,
             "steve_crouch": 1.5}.get(kind, 0.25)
        feet = nether.project(c["pos"], c["target"], c["lens"], p)
        head = nether.project(c["pos"], c["target"], c["lens"], (p[0], p[1], p[2] + h))
        rows.append((kind, where if isinstance(where, str) else tuple(round(v, 2) for v in where),
                     None if feet is None else tuple(round(v, 2) for v in feet),
                     None if head is None else tuple(round(v, 2) for v in head)))
    return rows


# ---------------------------------------------------------------------------------------------------------------
# scouting film (in memory: films.sixseconds_set_scout), one 1-second shot per beat still
# ---------------------------------------------------------------------------------------------------------------
SCOUT_FILM = "sixseconds_set_scout"
SCOUT_FRAME = 12                 # the still is this frame of its 24-frame shot (a push is half way)
_SCOUT = []                      # the beat keys the scout film is built with


def _pos(bas, where):
    return Vector(bas.anchors[where]) if isinstance(where, str) else Vector(where)


def fill(st, bas, s, name):
    """The film-local light FILLS[name] (shadowless, warm white KEY_COLOR) on in shot s only, hidden in every other
    frame (as films/hello_common.py Hello.fill: a hidden light is in no frame's stamp). One name = one light."""
    from engine import props

    pos, watts = FILLS[name]
    lamp = bpy.data.objects.get(name)
    if lamp is None:
        lamp = props.make_light("fill", bas.collection)
        lamp.name = name
        lamp.location = pos
        lamp.data.color = KEY_COLOR
        lamp.data.energy = watts
        lamp.visible_camera = False
        st.key(lamp, "hide_render", 1, True)
    st.key(lamp, "hide_render", s.frame_start, False)
    st.key(lamp, "hide_render", s.frame_end + 1, True)
    return lamp


def _stage(st, s, bas, b, pool):
    """Stage beat `b` in shot s: cast on their anchors, camera, pit / pillar, lights, fills."""
    from engine import breaking, piglins

    Y = bas.yaws
    f0, f1 = s.frame_start, s.frame_end
    used, vis, hero = {}, [], []

    def take(k):
        ob = pool[k][used.get(k, 0)]
        used[k] = used.get(k, 0) + 1
        return ob

    for kind, where, look, opts in b["cast"]:
        p = _pos(bas, where)
        if kind == "poof":
            piglins.poof(p, f0 - 8, camera=s, size=(0.6, 1.8), seed=3)
            continue
        if kind.startswith("item:"):
            ob = take(kind[5:])
            ob.place(f0, p)
            ob.animate(f0, f1 + 1)
            vis.append(ob)
            continue
        k = "steve" if kind.startswith("steve") else "piglin" if kind.startswith("piglin") else kind
        ob = take(k)
        ob.place(f0, p, opts.get("yaw", Y.get(where, 0.0) if isinstance(where, str) else 0.0))
        if k == "steve":
            ob.hold("gold_ingot" if kind == "steve_ingot" else "iron_pickaxe")
        if look is not None:
            ob.look_at(f0, _pos(bas, look), ease=0)
        if kind == "steve_crouch":
            ob.sneak(f0)
        if kind == "piglin_admire":
            ob.admire(f0, "gold_ingot")
        if opts.get("aggro"):
            ob.aggro(f0)
        if k != "steve":
            ob.flop_ears(f0, f1 + 1)
        vis.append(ob)
        if b.get("hero") == k or (b.get("hero") in ("steve", "boots") and k == "steve"):
            hero.append(ob)
    c = bas.cameras[b["cam"]]
    if b.get("pit"):
        bas.pit_open(s, keep=[bas.pit_last.cell] if b["pit"] == "keep" else ())
        if b["pit"] == "keep":
            breaking.crack(bas.pit_last, f0, 6)
            st.cast[bas.pit_last.name] = bas.pit_last
            vis.append(bas.pit_last)
    if b.get("pillar"):
        bas.pillar_in(s)
    if b.get("flicker"):
        bas.lava_flicker(f0, f1)
    s.lens(c["lens"], c["fstop"] or 4.0)
    if c.get("pos1"):
        s.move(c["pos"], c["target"], c["pos1"], c.get("target1", c["target"]), ease="linear")
    else:
        s.move(c["pos"], c["target"])
    fo = c.get("focus")
    s.focus(_pos(bas, fo) if fo is not None else Vector(c["target"]))
    st.use(s, *vis)
    if hero and b.get("hero") == "boots":
        st.hero(s, "boots", *pool["boots_objs"])
    elif hero:
        st.hero(s, b["hero"], hero[0])
    for name in b.get("fills", ()):
        fill(st, bas, s, name)
    lights = dict(b.get("lights") or c.get("lights") or {})
    st.lights(s, 1.0, groups=lights or None, **bas.lights_for(b["set"]))
    return vis


def _scout_build(scene, sky=None):
    """The scouting film: one 1-second shot per beat in _SCOUT (all of BEATS by default), each under its sky."""
    from engine import piglins, players, shots

    scene.render.resolution_x, scene.render.resolution_y = FINAL_RES
    scene.cycles.samples = FINAL_SAMPLES
    bas = build_set(scene)
    film = shots.Film(scene, fps=24)
    keys = _SCOUT or BEAT_KEYS
    skies = {k: v for k, v in SUGGESTED_SKIES.items() if any(beat(b)["sky"] == k for b in keys)}
    st = nether.Stage(scene, film, bas, skies=skies, sky=sky)
    need = {}
    for key in keys:
        n = {}
        for kind, _w, _l, _o in beat(key)["cast"]:
            k = kind[5:] if kind.startswith("item:") else "steve" if kind.startswith("steve") else \
                "piglin" if kind.startswith("piglin") else kind
            n[k] = n.get(k, 0) + 1
        for k, v in n.items():
            need[k] = max(need.get(k, 0), v)
    pool = {"brute": [piglins.add_piglin(st, "six_brute", "brute")],
            "piglin": [piglins.add_piglin(st, "six_pig_%d" % i, weapon=("crossbow" if i == 3 else "default"))
                       for i in range(1, max(need.get("piglin", 0), 1) + 1)],
            "steve": [players.add_player(st, "six_runner", "steve")]}
    pool["boots_objs"] = players.equip(pool["steve"][0], boots="golden")
    for k, v in need.items():
        if k not in pool and k != "poof":
            pool[k] = [piglins.add_item(st, k, name="six_%s_%d" % (k, i)) for i in range(1, v + 1)]
    for key in keys:
        b = beat(key)
        s = st.shot(key, 1.0, sky=b["sky"])
        _stage(st, s, bas, b, pool)
    st.finish()
    return {"film": film, "captions": [], "stage": st, "bastion": bas}


def register_scout(keys=None):
    """Make the scouting film importable as films.sixseconds_set_scout (in memory) with these beats."""
    global _SCOUT
    _SCOUT = list(keys or BEAT_KEYS)
    mod = types.ModuleType("films." + SCOUT_FILM)
    mod.__file__ = os.path.abspath(__file__)
    mod.SKIES = {k: v for k, v in SUGGESTED_SKIES.items() if any(beat(b)["sky"] == k for b in _SCOUT)}
    mod.build = _scout_build
    sys.modules["films." + SCOUT_FILM] = mod
    return mod


def render_scouts(keys, res=FINAL_RES, samples=FINAL_SAMPLES, threads=2, tag="", check_colours=True):
    """Render the scouting still of each beat key through render.Session (one build per sky, in this process):
    out/test/sixseconds_set_<key>[tag].png and _zones.png, measured by nether.check_still. Returns the paths."""
    import time

    import render as R
    from PIL import Image

    from engine import post

    register_scout(keys)
    paths, by_sky = [], {}
    for k in keys:
        by_sky.setdefault(beat(k)["sky"], []).append(k)
    for sky, ks in by_sky.items():
        ses = R.Session(SCOUT_FILM, sky=sky)
        ses.configure(tuple(res), samples, threads, None)
        for k in ks:
            s = next(x for x in ses.film.shots if x.name == k)
            path = os.path.join(ROOT, "out", "test", "sixseconds_set_%s%s.png" % (k, tag))
            t = time.time()
            ses.render_frame(s.frame_start + SCOUT_FRAME, path)
            with Image.open(path) as im:
                post.draw_zones(im).save(path[:-4] + "_zones.png")
            print("[sixseconds_set] %s (sky %s) -> %s  %.1fs" % (k, sky, path, time.time() - t), flush=True)
            if check_colours:
                try:
                    nether.check_still(ses.scene, path, heroes=ses.result["stage"].heroes.get(k, ()))
                except Exception as e:          # a measurement must never stop the scouting
                    print("[sixseconds_set] check_still failed: %r" % (e,))
            paths.append(path)
    return paths


def _selftest():
    """Build the set and check it (no rendering). Returns the number of problems."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bas = build_set(bpy.context.scene)
    probs = check(bas)
    print("[sixseconds_set] %d anchors (%d of this film), %d cameras (%d of this film), %d beat stills: "
          "%d problem(s)" % (len(bas.anchors), len(bas.sets[SET_NAME]["anchors"]), len(bas.cameras),
                             len(NEW_CAMERAS), len(BEATS), len(probs)))
    return len(probs)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    code = 0
    if not args or "check" in args:
        code += _selftest()
    if "report" in args:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bas = build_set(bpy.context.scene)
        for k in [a for a in args if a in BEAT_KEYS] or BEAT_KEYS:
            print(k, beat(k)["cam"])
            for row in report(bas, k):
                print("   ", row)
    want = [a for a in args if a in BEAT_KEYS] if "report" not in args else []
    if "group" in args:
        want = [k for g in args if g in GROUPS for k in GROUPS[g]]
    if "all" in args:
        want = list(BEAT_KEYS)
        print("[sixseconds_set] 'all' takes about 8 minutes: more than one 290 s command (use the GROUPS)")
    lo = "--lo" in sys.argv
    if want:
        render_scouts(want, res=(270, 480) if lo else FINAL_RES, samples=8 if lo else FINAL_SAMPLES,
                      tag="_lo" if lo else "", check_colours=not lo)
    sys.exit(1 if code else 0)
