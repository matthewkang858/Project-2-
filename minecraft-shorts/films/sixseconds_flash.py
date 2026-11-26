"""Six Seconds, sequence FLASH: "I ended a full stack of worlds." Three flash cuts with a snap to black between them,
one per world: beat 16 (shots fl16_bridge, fl16_treasure, fl16_home). Skies: fl16_bridge "soul" (the bridge's world:
teal), fl16_treasure and fl16_home "wastes". One function per shot; the contract is in films/sixseconds_common.py
(tags "fl...", C.actor, C.item, C.cam, C.lights, C.puff, st.use / st.hero).

STATUS: STUBS by the lead director: the three cuts staged as the set builder scouted them (brute, puff, boots, an
extra drop); the docstrings say what they must become. Everything may be rewritten except what SHARED names.

THE DEVICE (story): "Three flash cuts of about a second each with a snap to black between them. The brute is locked
in the same spot of the frame every time, a white puff beside him and a pair of golden boots spinning as a dropped
item at his feet. Only the bastion behind him changes: the bridge, then a treasure corner with a chest and a pile of
gold blocks, then the home gateway (floor whole, no pit)." Different extra drops in each cut: gravel, ender pearl,
iron pickaxe.
  THE CUTS (films/sixseconds.py): fl16_bridge 992-1013 (22 f) starts 10 frames before "I" (in the silence after
  "can't": the first world is seen before it is named); fl16_treasure 1014-1032 (19 f) on "full"; fl16_home
  1033-1065 (33 f) on "worlds", then the line's pause. THE SNAPS: the encoder shows black on 1014-1015 and 1033-1034
  (the first two frames of the 2nd and 3rd cut: SNAPS); the caption of "full" / "worlds" is drawn on the black.
  Words: I 1002, ended 1005, a 1012 | full 1014, stack 1021, of 1030 | worlds 1033 (ends 1046).
SHARED (films/sixseconds_common.py): CAMS["flash_bridge"], ["flash_treasure"], ["flash_home"]: one offset from the
  brute in all three (5 blocks in front at 1.45, aimed 0.5 above his feet, 35 mm f/2.8): he is LOCKED in the same
  spot of the frame (measured x 38-62 %, y 20-30 % in all three). Use them exactly, no move (a tiny handheld).
  PLACES "flash_bridge" / "flash_treasure" / "flash_home" (his place in each world, facing the lens), and the set's
  six_flash_puff_<set> (+1.2, -0.2 from him), six_flash_boots_<set> (+0.7, +0.1), six_flash_extra_<set> (-0.65, 0).
THE WORLD'S RULES that bite here: fl16_home's floor is WHOLE (no pit); the runner is only a puff (C.puff from a frame
  BEFORE the shot: the puffs already in the air on its first frame) and his drops; NO netherrack pillar in
  fl16_bridge (the lead tried it: from this camera its top block sits right on the brute's head; C.pillar refuses
  it); the brute's axe low or coming to rest.
RISK (story): "three cuts must read as many worlds": the bridge world is teal (sky "soul"), the treasure corner is
  gold and enclosed, home is red with the gateway's glow. Fallback: "four cuts of twenty frames each".
TAGS TAKEN by the stubs: brute_fl (all three), golden_boots_fl1..3, gravel_fl1, ender_pearl_fl2, iron_pickaxe_fl3.
PREVIEW samples of this sequence: 10.
"""

WORLDS = {"fl16_bridge": ("bridge", "gravel", "flash_bridge", "bridge"),
          "fl16_treasure": ("treasure", "ender_pearl", "flash_treasure", "treasure"),
          "fl16_home": ("home", "iron_pickaxe", "flash_home", "home")}


def _flash(st, s, C, n):
    """One flash cut: the brute locked on his place facing the lens, a puff beside him already in the air, the golden
    boots and the world's extra drop spinning at his feet."""
    world, extra, cam, light = WORLDS[s.name]
    brute = C.actor("brute", "fl")
    C.stand(s, brute, "flash_%s" % world, idle=False)
    C.puff(s, "six_flash_puff_%s" % world, s.frame_start - 8, seed=16 + n)
    C.rest(s, "golden_boots", "fl%d" % n, "six_flash_boots_%s" % world)
    C.rest(s, extra, "fl%d" % n, "six_flash_extra_%s" % world)
    C.cam(s, cam, focus=brute.head, handheld=0.003)
    st.hero(s, "brute", brute)
    C.lights(s, light)
    return brute


def fl16_bridge(st, s, C, nar):
    """BEAT 16, FLASH 1 of 3: the bridge (its world: teal fog).   frames 992-1013 (22 f, 0.92 s), sky soul.
    Words: I 1002, ended 1005, a 1012.

    MUST BE SEEN: on 992 the brute in his locked spot on the bridge, the teal void behind him, a puff beside him
    rising, the golden boots and a gravel spinning at his feet.
    NOW (stub): CAMS["flash_bridge"], the brute at flash_bridge, the puff from 984, the boots, gravel; no pillar.
    MEASURED (out/test/sixseconds_set_b16a_bridge_flash.png under nether_wastes; under this film's sky the lead's
    out/test/sixseconds_scout_flash_bridge.png): brute x 38-62 %, y 20-30 %, 1.65 x the blackstone (rule 1.5: near
    the limit); the drops above the caption band.
    NEIGHBOURS: before, br15_wait (the same world: the runner on the pillar); after, fl16_treasure (snap to black).
    """
    _flash(st, s, C, 1)


def fl16_treasure(st, s, C, nar):
    """BEAT 16, FLASH 2 of 3: the treasure corner of a third bastion.   frames 1014-1032 (19 f, 0.79 s; black on
    1014-1015), sky wastes. Words: full 1014, stack 1021, of 1030.

    MUST BE SEEN: on 1016 (the first frame after the snap) the brute in the SAME spot of the frame, a chest at the
    left, a pile of gold blocks at the right, a puff, the golden boots and an ender pearl at his feet.
    NOW (stub): CAMS["flash_treasure"], the brute at flash_treasure, the puff from 1006, boots, pearl.
    MEASURED (out/test/sixseconds_set_b16b_treasure_flash.png): brute in the same frame position, 3.08 x; chest left,
    gold pile right.
    NEIGHBOURS: before, fl16_bridge; after, fl16_home (snap to black).
    """
    _flash(st, s, C, 2)


def fl16_home(st, s, C, nar):
    """BEAT 16, FLASH 3 of 3: home, the gateway behind him (floor whole, no pit).   frames 1033-1065 (33 f, 1.38 s;
    black on 1033-1034), sky wastes. Word: worlds 1033 (ends 1046), then the line's pause.

    MUST BE SEEN: on 1035 the brute in the SAME spot of the frame with the gateway and its glow behind him, a puff,
    the golden boots and the iron pickaxe at his feet; the floor whole. The longest of the three: it settles into
    gt17 ("I started waiting at the gate": the corridor camera looking at this gateway from outside).
    NOW (stub): CAMS["flash_home"], the brute at flash_home, the puff from 1025, boots, pickaxe.
    MEASURED (out/test/sixseconds_set_b16c_home_flash.png): brute in the same frame position, 1.74 x; the gateway's
    glow behind him.
    NEIGHBOURS: before, fl16_treasure; after, gt17_waits.
    """
    _flash(st, s, C, 3)
