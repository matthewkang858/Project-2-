"""Six Seconds, sequence FLASH: "I ended a full stack of worlds." Three flash cuts with a snap to black between them,
one per world: beat 16 (shots fl16_bridge, fl16_treasure, fl16_home). Skies: fl16_bridge "soul" (the bridge's world:
teal), fl16_treasure and fl16_home "wastes". One function per shot; the contract is in films/sixseconds_common.py
(tags "fl...", C.actor, C.item, C.rest, C.cam, C.lights, C.puff, st.use / st.hero).

STATUS: SHOT by the flash director (Nov 26), on the lead's stubs: the three cuts are one function (_flash) with
three tables (WORLDS, PUFF, the look GLANCE / TURN_AT / TURN), so the three worlds can only differ where the story
wants them to (the bastion behind him, the extra drop, the puff's random draw).

THE DEVICE (story): "Three flash cuts of about a second each with a snap to black between them. The brute is locked
in the same spot of the frame every time, a white puff beside him and a pair of golden boots spinning as a dropped
item at his feet. Only the bastion behind him changes: the bridge, then a treasure corner with a chest and a pile of
gold blocks, then the home gateway (floor whole, no pit)." Different extra drops in each cut: gravel, ender pearl,
iron pickaxe.
  THE CUTS (films/sixseconds.py): fl16_bridge 999-1020 (22 f) starts 10 frames before "I" (in the silence after
  "can't": the first world is seen before it is named); fl16_treasure 1021-1039 (19 f) on "full"; fl16_home
  1040-1072 (33 f) on "worlds", then the line's pause. THE SNAPS: the encoder shows black on 1021-1022 and 1040-1041
  (the first two frames of the 2nd and 3rd cut: SNAPS); the caption of "full" / "worlds" is drawn on the black.
  Words: I 1009, ended 1012, a 1019 | full 1021, stack 1028, of 1037 | worlds 1040 (ends 1053).
SHARED (films/sixseconds_common.py): CAMS["flash_bridge"], ["flash_treasure"], ["flash_home"]: one offset from the
  brute in all three (5 blocks in front at 1.45, aimed 0.5 above his feet, 35 mm f/2.8): he is LOCKED in the same
  spot of the frame. Use them exactly, no move (a tiny handheld; the focus is free). PLACES "flash_bridge" /
  "flash_treasure" / "flash_home" (his place in each world, facing the lens), and the set's six_flash_puff_<set>,
  six_flash_boots_<set>, six_flash_extra_<set> (films/sixseconds_set.py FLASH_OFFSETS, the same in every world:
  each flash camera looks north at him, +x is frame right): puff (+0.95, +0.3), boots (-0.85, -0.35), extra drop
  (+0.55, -0.15).
THE LEAD'S REVIEW PASS (the story check, confirmed on the stills: out/test/sixseconds_scout_fl16_bridge_1006.png,
  _treasure_1020.png, _home_1040.png of the first stub): the golden boots, which say "the same runner died in every
  world", lay at (+0.7, +0.1), UNDER the puff (+1.2, -0.2) in two of the three cuts (a gold sliver behind white
  blocks; in the treasure cut not seen at all). Moved: the boots to his LEFT, the extra drop and the puff to his
  right (the puff a little behind). And a flat item spinning on the ground is EDGE-ON twice a turn (the boots were a
  thin gold sliver on 1023-1027): the stub phases the boots and the extra drop with C.rest(..., face=<the lens>,
  face_at=first picture frame + 3) so they show the lens their broad side on the cut's first picture frames (they
  turn about 40 degrees over a cut; the boots read as boots on every frame looked at). FIX PASS (review, motion):
  phased on first + 3 they turned up to 64 degrees off by the END of the long home cut (1072: a gold sliver), so
  they are now phased on the MIDDLE picture frame of each cut (face_at = (first + last) // 2: 1009, 1031, 1057):
  at most 26 / 19 / 36 degrees off broadside on any picture frame (81 % of their width or more). Stills after the pass:
  out/test/sixseconds_scout_fl16_bridge_1002_zones.png, _fl16_treasure_1025.png, _fl16_home_1045.png (boots clear at
  the bottom left, x about 18-28 %, y 55-60 %; the extra drop at the right edge of the puff).
  STILL OPEN (the lead's; answered in THE PUFF below): the puff stands at x 75-100 % (its particles rise and
  spread; part of it outside x 82 %) and in the treasure cut it covers the right part of the gold pile (the pile
  still reads as gold above and left of it): a later puff start (f0 - 4) or a smaller burst is the director's call;
  keep the boots clear of it.
THE WORLD'S RULES that bite here: fl16_home's floor is WHOLE (no pit); the runner is only a puff (C.puff from a frame
  BEFORE the shot: the puffs already in the air on its first frame) and his drops; NO netherrack pillar in
  fl16_bridge (the lead tried it: from this camera its top block sits right on the brute's head; C.pillar refuses
  it); the brute's axe low or coming to rest.
THE LOOK (this pass): the same small action in every world, at the same offset from the cut's first picture frame,
  so the three cuts rhyme ("a full stack": the same thing again and again). On the first picture frame his head is
  turned 24 degrees to his left and 16 down (GLANCE): toward the puff at frame right, where the runner just was; from
  first + 2 it comes round to the lens over 7 frames (TURN_AT, TURN) and holds there to the cut. Bridge: turning
  1001-1008, on the lens on 1008, the frame before "I" (he looks up at us as he starts to speak); treasure 1025-1032
  (through "stack"); home 1044-1051, then 21 frames of the stare into gt17. The body never moves (C.put on his place,
  facing the lens; no idle(): idle's random glances would break the lock); the ears flop (flop_ears) and the axe
  hangs low in his right hand (a brute that has lost its target drops the attack pose; the kill was a second before
  the poof, LivingEntity.tickDeath: the puff comes 20 ticks after the killing blow, so the swing is long over).
  A head turn on its neck does not move the head in the frame: the lock holds (MEASURED below).
THE PUFF (this pass; the lead's STILL OPEN above): the anchor six_flash_puff_<world> is SHARED and sits at about x
  84 % of the frame, and the game's poof spawns its 20 puffs anywhere within +-0.6 block of it (getRandomX(1.0) with
  a player's width): about half of ANY burst there lies past x 82 %, whatever its start. Neither a later start (the
  spread is the spawn box, not the drift) nor fewer puffs (the game's 20) cures that, so this file picks the burst's
  RANDOM DRAW instead: tools/sixseconds_flash_probe.py simulates engine.piglins.poof exactly (a mirror of its random
  draws, checked against it: same stages and frames, positions within 3e-5) for every seed 0-399 at 6, 8, 10 and 12
  frames before the cut, projects every puff's sprite into the flash camera on every picture frame and scores it
  (puff seen inside the safe area, minus what a phone hides, minus 3 x what crosses the brute or the drops, minus
  the gold pile it covers: 1.5 x at first, which picked sparse draws that read as white specks on the gold, so the
  treasure's was chosen at 0.4 x: --gold 0.4); tools/sixseconds_flash_puffs.py rendered the best ones side by side
  (out/test/sixseconds_flash_puffs_fl16_bridge_999_1010_1018.png, _treasure_1023_1027_1033.png,
  _home_1042_1053_1066.png). Chosen (PUFF): bridge seed 204 from 12 frames before the cut, treasure 308 from 8,
  home 332 from 10: in all three a column of puffs at x 65-90 % beside his left arm, clear of his face, rising and
  thinning over the cut (the same place in every world, which the lock wants). Against the stub's draws (probe,
  per picture frame, in frame-% squared): puff seen 122 -> 262 (bridge), 167 -> 330 (treasure), 73 -> 331 (home);
  hidden by the phone's crop and icons 109 -> 27, 112 -> 67, 245 -> 56. What is left: part of each puff is still
  at x 82-92 % (the anchor), mostly above y 45 % where the icon column is not; in the treasure cut the puffs stand
  in front of the gold pile (the anchor is on it: every draw covers it; the pile reads as gold blocks around and
  through them, gold hue 45).
THE LOCK, MEASURED (tools.sixseconds_geo, this pass): his eyes at x 50.0 %, y 24.6 % in all three cuts on every
  frame measured; head x 32.3-68.1 %, y 19.1-32.3 % on the first picture frames (turned 24 degrees, pitch -16),
  x 31.4-68.5 %, y 19.8-31.0 % on the lens (0 degrees); face 120 px. Palette (tools.sixseconds_palette, this pass):
  fl16_bridge 1009 brute x 1.63 the blackstone (soul; the stub's 1.56 was on another frame), fl16_treasure 1030
  x 3.17, gold hue 45 s 0.85, fl16_home 1053 x 1.87; hero 100 % inside the safe area in all three.
RISK (story): "three cuts must read as many worlds": the bridge world is teal (sky "soul"), the treasure corner is
  gold and enclosed, home is red with the gateway's glow. Fallback: "four cuts of twenty frames each".
TAGS TAKEN: brute_fl (all three: no pre-roll, nothing is keyed before a cut), golden_boots_fl1..3, gravel_fl1,
ender_pearl_fl2, iron_pickaxe_fl3. No fill light (the palette passes in all three without one).
TOOLS (this sequence's own): tools/sixseconds_flash_probe.py (the puff's draw: `puffs`, `one`, `check`),
tools/sixseconds_flash_puffs.py (candidate puffs rendered side by side). PREVIEW samples of this sequence: 10
(out/preview/sixseconds/270x480_10spp); the motion: out/test/sixseconds_flash_motion.mp4.
"""

import math

from mathutils import Vector

WORLDS = {"fl16_bridge": ("bridge", "gravel", "flash_bridge", "bridge"),
          "fl16_treasure": ("treasure", "ender_pearl", "flash_treasure", "treasure"),
          "fl16_home": ("home", "iron_pickaxe", "flash_home", "home")}

# THE RUNNER'S PUFF of each world: (seed, frames before the cut it started). The anchor six_flash_puff_<world> is
# SHARED (x about 84 % of the frame: half of any burst there lies past x 82 %); the seed and the start are this
# file's. Chosen with tools/sixseconds_flash_probe.py (every seed 0-399 at 6, 8, 10 and 12 frames, scored on the
# picture frames of the cut: puff seen inside the safe area minus what a phone hides, three times what crosses the
# brute's face / armband or the drops, 0.4 times what covers the treasure's gold pile) and rendered side by side
# with tools/sixseconds_flash_puffs.py; see the module docstring (THE PUFF).
PUFF = {"fl16_bridge": (204, 12), "fl16_treasure": (308, 8), "fl16_home": (332, 10)}

# THE LOOK, the same in every world: on the cut's first picture frame his head is turned GLANCE degrees to his left
# (frame right: toward the puff, where the runner just was) and down; from the first picture frame + TURN_AT it
# comes round to the lens over TURN frames and holds there to the cut. (The bridge: on the lens on 1008, the frame
# before "I".) The lock is the head's place in the frame, which a turn of the head on its neck does not move.
GLANCE = (24.0, -16.0)
TURN_AT, TURN = 2, 7


def _head_point(c, frame, yaw_deg, pitch_deg, dist=3.0):
    """A look target that turns c's head `yaw_deg` from its body (+ = to its left) and `pitch_deg` up (+ = up)."""
    eye = c.eye_point(frame)
    yaw = c.yaw_at(frame) + math.radians(yaw_deg)
    return Vector((eye.x + math.sin(yaw) * dist, eye.y - math.cos(yaw) * dist,
                   eye.z + math.tan(math.radians(pitch_deg)) * dist))


def _flash(st, s, C, n):
    """One flash cut: the brute locked on his place facing the lens, his head coming round from the puff to the lens,
    the puff beside him already in the air, the golden boots and the world's extra drop spinning at his feet."""
    world, extra, cam, light = WORLDS[s.name]
    f0, f1 = s.frame_start, s.frame_end
    first = C.black(s)[1] + 1 if C.black(s) else f0                 # the first frame with a picture
    lens = C.camera_spec(cam)["pos"]
    brute = C.actor("brute", "fl")
    C.put(brute, f0, "flash_%s" % world)                             # the place's own yaw: facing the lens
    brute.look_at(f0, _head_point(brute, f0, *GLANCE), ease=0)
    brute.look_at(first + TURN_AT, Vector(lens), ease=TURN)
    brute.flop_ears(f0, f1 + 1)
    st.use(s, brute)
    seed, before = PUFF[s.name]
    C.puff(s, "six_flash_puff_%s" % world, f0 - before, seed=seed)
    # the boots and the extra drop show the lens their broad side in the MIDDLE of the cut's picture frames, so
    # they turn as far off it at the start as at the end (the game's 2.39 degrees a frame: at most 26 / 19 / 36
    # degrees off in the three cuts; phased on first + 3 the home boots were 64 degrees off, a gold sliver, by 1072)
    mid = (first + f1) // 2
    C.rest(s, "golden_boots", "fl%d" % n, "six_flash_boots_%s" % world, face=lens, face_at=mid)
    C.rest(s, extra, "fl%d" % n, "six_flash_extra_%s" % world, face=lens, face_at=mid)
    C.cam(s, cam, focus=brute.head, handheld=0.003)
    st.hero(s, "brute", brute)
    C.lights(s, light)
    return brute


def fl16_bridge(st, s, C, nar):
    """BEAT 16, FLASH 1 of 3: the bridge (its world: teal fog).   frames 999-1020 (22 f, 0.92 s), sky soul.
    Words: I 1009, ended 1012, a 1019 (running on into "full" on 1021).

    MUST BE SEEN: on 999 the brute in his locked spot on the bridge, the teal void behind him, a puff beside him
    rising (at his right), the golden boots (at his left, broad side to the lens) and a gravel at his feet.
    NOW: CAMS["flash_bridge"] unchanged (handheld 0.003, focus on his head), the brute at flash_bridge facing the
      lens; on 999 his head turned 24 degrees to the puff and down, coming round 1001-1008, on the lens from 1008
      (the frame before "I") to the cut; the runner's puff (seed 204, from 987) a column of puffs beside his left arm
      rising and thinning; the boots (frame left) and the gravel (at his left foot) phased to the lens on 1009 (the
      middle picture frame: 24 degrees off on 999, 26 on 1020); no pillar.
    MEASURED (out/test/sixseconds_fl_fl16_bridge_999_zones.png, _1009_zones.png; tools.sixseconds_geo
      fl16_bridge:999/1009/1020; tools.sixseconds_palette --sky soul 1009): eyes x 50.1 %, y 24.6 % on all three
      frames, head x 32.5-68.0 % / y 19.1-32.3 % turned, x 32.6-67.4 % / y 19.8-30.9 % on the lens, face 120 px;
      brute x 1.63 the blackstone (rule 1.5; the stub measured 1.56 on 1002); hero x 38-62 %, y 20-31 %, 100 %
      inside; the puff x 64-98 %, y 14-57 % on 999 (most of it inside x 82 %; its edge on the right side of his
      turned head, cheek and ear, on 999-1002: the probe's turned-head box scores it brute 16.8; the draws with less
      face overlap, 123:10 / 123:12, spill three times as far past x 82 % or hide three times as much: kept),
      x 67-92 %, y 14-40 % on 1009; boots x 12-27 %, y 50-57 %; gravel x 64-74 %, y 52-58 %. Motion: preview
      frames 999-1020 looked at (out/test/sixseconds_flash_motion.mp4, frames 0-21).
    NEIGHBOURS: before, br15_wait (the same world: the runner on the pillar); after, fl16_treasure (snap to black).
    """
    _flash(st, s, C, 1)


def fl16_treasure(st, s, C, nar):
    """BEAT 16, FLASH 2 of 3: the treasure corner of a third bastion.   frames 1021-1039 (19 f, 0.79 s; black on
    1021-1022), sky wastes. Words: full 1021, stack 1028, of 1037.

    MUST BE SEEN: on 1023 (the first frame after the snap) the brute in the SAME spot of the frame, a chest at the
    left, a pile of gold blocks at the right, a puff, the golden boots and an ender pearl at his feet.
    NOW: CAMS["flash_treasure"] unchanged, the brute at flash_treasure; the same look as the bridge from the first
      picture frame: turned to the puff on 1023, coming round 1025-1032 (through "stack"), on the lens to the cut;
      the puff (seed 308, from 1013) a dense column in front of the gold pile beside his left arm; the boots (in
      front of the chest's foot) and the pearl phased to the lens on 1031 (19 degrees off on 1023 and 1039).
    MEASURED (out/test/sixseconds_fl_fl16_treasure_1023_zones.png, _1030.png; geo fl16_treasure:1023/1032;
      palette --sky wastes 1030): eyes x 50.0 %, y 24.6 % (the bridge's to 0.1 %), head x 32.3-68.1 % turned,
      x 31.4-68.5 % on the lens, face 120 px; brute x 3.17, gold hue 45 s 0.85; hero x 40-62 %, y 21-31 %, 100 %
      inside; the chest x 5-28 %, the pile x 68-100 % / y 23-48 % with the puff in front of its left half (every
      draw at the shared anchor covers it: module docstring; on 1023-1030 it stands over the part of the pile a phone
      shows, x 68-82 %, which reads as clean gold blocks from about 1031; the review's search, seeds 0-149 started
      8-20 frames before, found nothing better: 10:20 clears the pile but sits over his head, 56:20 covers it the
      same way; the chest carries "treasure" throughout), the pearl x 62-74 % / y 50-57 % clear on 1030; the top of
      the puff touches his left ear around 1030. Motion: frames 1023-1039 (mp4 frames 24-40), black 1021-1022.
    NEIGHBOURS: before, fl16_bridge; after, fl16_home (snap to black).
    """
    _flash(st, s, C, 2)


def fl16_home(st, s, C, nar):
    """BEAT 16, FLASH 3 of 3: home, the gateway behind him (floor whole, no pit).   frames 1040-1072 (33 f, 1.38 s;
    black on 1040-1041), sky wastes. Word: worlds 1040 (ends 1053), then the line's pause.

    MUST BE SEEN: on 1042 the brute in the SAME spot of the frame with the gateway and its glow behind him, a puff,
    the golden boots and the iron pickaxe at his feet; the floor whole. The longest of the three: it settles into
    gt17 ("I started waiting at the gate": the corridor camera looking at this gateway from outside).
    NOW: CAMS["flash_home"] unchanged, the brute at flash_home, the gateway and the corridor's lava glow behind his
      head, the floor whole (no C.pit); the same look: turned to the puff on 1042, coming round 1044-1051, then the
      stare at the lens for 21 frames into gt17; the puff (seed 332, from 1030) a big cloud beside his left arm that
      rises up the right side of the frame; the boots and the pickaxe phased to the lens on 1057 (36 degrees off on
      1042 and 1072, where the first + 3 phase left them 64 degrees off: a sliver).
    MEASURED (out/test/sixseconds_fl_fl16_home_1042_zones.png, _1053_zones.png; geo fl16_home:1042/1051/1072;
      palette --sky wastes 1053): eyes x 50.0 %, y 24.6 %, head x 32.3-68.1 % turned, x 32.0-67.8 % on the lens,
      face 120 px, his head against the lava of the corridor's end; brute x 1.87 the blackstone; hero x 38-62 %,
      y 20-31 %, 100 % inside; the puff x 63-95 %, y 18-52 % on 1042 (a puff over the pickaxe's head on 1042-1045),
      x 65-92 %, y 12-45 % on 1053, near the top by 1066; the pickaxe x 61-75 %, y 50-57 % clear from 1046.
      Motion: frames 1042-1072 (mp4 frames 43-73), black 1040-1041; the cut into gt17 looked at against the gate
      sequence's preview frames 1073-1075 (270x480_5spp, rendered before this pass).
    NEIGHBOURS: before, fl16_treasure; after, gt17_waits.
    """
    _flash(st, s, C, 3)
