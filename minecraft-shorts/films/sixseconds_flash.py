"""Six Seconds, sequence FLASH: "I ended a full stack of worlds." Three flash cuts with a snap to black between them,
one per world: beat 16 (shots fl16_bridge, fl16_treasure, fl16_home). Skies: fl16_bridge "soul" (the bridge's world:
teal), fl16_treasure and fl16_home "wastes". One function per shot; the contract is in films/sixseconds_common.py
(tags "fl...", C.actor, C.item, C.rest, C.cam, C.lights, C.puff, st.use / st.hero).

STATUS: STUBS by the lead director: the three cuts staged as the set builder scouted them (brute, puff, boots, an
extra drop), the drops moved and phased in the lead's review pass; the docstrings say what they must become.
Everything may be rewritten except what SHARED names.

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
  turn about 40 degrees over a cut; the boots read as boots on every frame looked at). Stills after the pass:
  out/test/sixseconds_scout_fl16_bridge_1002_zones.png, _fl16_treasure_1025.png, _fl16_home_1045.png (boots clear at
  the bottom left, x about 18-28 %, y 55-60 %; the extra drop at the right edge of the puff).
  STILL OPEN: the puff stands at x 75-100 % (its particles rise and spread; part of it outside x 82 %) and in the
  treasure cut it covers the right part of the gold pile (the pile still reads as gold above and left of it): a
  later puff start (f0 - 4) or a smaller burst is the director's call; keep the boots clear of it.
THE WORLD'S RULES that bite here: fl16_home's floor is WHOLE (no pit); the runner is only a puff (C.puff from a frame
  BEFORE the shot: the puffs already in the air on its first frame) and his drops; NO netherrack pillar in
  fl16_bridge (the lead tried it: from this camera its top block sits right on the brute's head; C.pillar refuses
  it); the brute's axe low or coming to rest.
THE LOCK, MEASURED by the lead (tools.sixseconds_geo; stills above): his head x 32.4-67.7 %, y 19.4-30.6 % in all
  three, face 120 px, straight at the lens (0 degrees): the same spot of the frame to a pixel. Palette
  (tools.sixseconds_palette after the pass): fl16_bridge (soul) brute x 1.56 the blackstone (rule 1.5: AT the
  limit: do not darken him), fl16_treasure x 3.10, gold hue 45, fl16_home x 1.71; hero 100 % inside the safe area.
RISK (story): "three cuts must read as many worlds": the bridge world is teal (sky "soul"), the treasure corner is
  gold and enclosed, home is red with the gateway's glow. Fallback: "four cuts of twenty frames each".
TAGS TAKEN by the stubs: brute_fl (all three), golden_boots_fl1..3, gravel_fl1, ender_pearl_fl2, iron_pickaxe_fl3.
PREVIEW samples of this sequence: 10.
"""

import math

from mathutils import Vector

WORLDS = {"fl16_bridge": ("bridge", "gravel", "flash_bridge", "bridge"),
          "fl16_treasure": ("treasure", "ender_pearl", "flash_treasure", "treasure"),
          "fl16_home": ("home", "iron_pickaxe", "flash_home", "home")}

# THE RUNNER'S PUFF of each world: (seed, frames before the cut it started). The anchor six_flash_puff_<world> is
# SHARED (x about 84 % of the frame: half of any burst there lies past x 82 %); the seed and the start are this
# file's. Chosen with tools/sixseconds_flash_probe.py (every seed 0-119 at 8 and 12 frames, scored on the picture
# frames of the cut: puff seen inside the safe area minus what a phone hides, three times what crosses the brute's
# face / armband or the drops, one and a half times what covers the treasure's gold pile); see the module docstring.
PUFF = {"fl16_bridge": (204, 12), "fl16_treasure": (132, 10), "fl16_home": (332, 10)}

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
    # the boots and the extra drop show the lens their broad side on the cut's first picture frames (edge-on they
    # are a gold sliver)
    C.rest(s, "golden_boots", "fl%d" % n, "six_flash_boots_%s" % world, face=lens, face_at=first + 3)
    C.rest(s, extra, "fl%d" % n, "six_flash_extra_%s" % world, face=lens, face_at=first + 3)
    C.cam(s, cam, focus=brute.head, handheld=0.003)
    st.hero(s, "brute", brute)
    C.lights(s, light)
    return brute


def fl16_bridge(st, s, C, nar):
    """BEAT 16, FLASH 1 of 3: the bridge (its world: teal fog).   frames 999-1020 (22 f, 0.92 s), sky soul.
    Words: I 1009, ended 1012, a 1019 (running on into "full" on 1021).

    MUST BE SEEN: on 999 the brute in his locked spot on the bridge, the teal void behind him, a puff beside him
    rising (at his right), the golden boots (at his left, broad side to the lens) and a gravel at his feet.
    NOW (stub): CAMS["flash_bridge"], the brute at flash_bridge, the puff from 991, the boots and the gravel phased to
    the lens; no pillar.
    MEASURED after the review pass (out/test/sixseconds_scout_fl16_bridge_1002_zones.png; tools.sixseconds_palette
      --sky soul 1002): brute x 1.56 the blackstone (rule 1.5: AT the limit), hero x 40-62 %, y 20-30 %, 100 %
      inside; the boots read at the bottom left; re-measure after any change of light.
    NEIGHBOURS: before, br15_wait (the same world: the runner on the pillar); after, fl16_treasure (snap to black).
    """
    _flash(st, s, C, 1)


def fl16_treasure(st, s, C, nar):
    """BEAT 16, FLASH 2 of 3: the treasure corner of a third bastion.   frames 1021-1039 (19 f, 0.79 s; black on
    1021-1022), sky wastes. Words: full 1021, stack 1028, of 1037.

    MUST BE SEEN: on 1023 (the first frame after the snap) the brute in the SAME spot of the frame, a chest at the
    left, a pile of gold blocks at the right, a puff, the golden boots and an ender pearl at his feet.
    NOW (stub): CAMS["flash_treasure"], the brute at flash_treasure, the puff from 1013, boots and pearl phased.
    MEASURED after the review pass (out/test/sixseconds_scout_fl16_treasure_1023.png / _1025.png / _1027.png): the
      boots broad side at the bottom left (in front of the chest), the pearl at his right half under the puff's
      edge; brute x 3.10, gold hue 45; the puff covers the right part of the gold pile (see the module docstring).
    NEIGHBOURS: before, fl16_bridge; after, fl16_home (snap to black).
    """
    _flash(st, s, C, 2)


def fl16_home(st, s, C, nar):
    """BEAT 16, FLASH 3 of 3: home, the gateway behind him (floor whole, no pit).   frames 1040-1072 (33 f, 1.38 s;
    black on 1040-1041), sky wastes. Word: worlds 1040 (ends 1053), then the line's pause.

    MUST BE SEEN: on 1042 the brute in the SAME spot of the frame with the gateway and its glow behind him, a puff,
    the golden boots and the iron pickaxe at his feet; the floor whole. The longest of the three: it settles into
    gt17 ("I started waiting at the gate": the corridor camera looking at this gateway from outside).
    NOW (stub): CAMS["flash_home"], the brute at flash_home, the puff from 1032, boots and pickaxe phased.
    MEASURED after the review pass (out/test/sixseconds_scout_fl16_home_1042.png / _1045.png / _1046.png): the boots
      broad side at the bottom left, the pickaxe at his right under the puff's edge; brute x 1.71.
    NEIGHBOURS: before, fl16_treasure; after, gt17_waits.
    """
    _flash(st, s, C, 3)
