"""Six Seconds, sequence BRIDGE: the second bastion, in another world. The boot shot again, the brute blocking the
bridge, the pillar: beats 11, 12, 13, 14, 15 (shots br11_boots, br12_blocks, br13_pillar, br14_zero, br15_wait), sky
"soul" (soul_sand_valley: the fog and the void of this world are TEAL; the lead's choice, films/sixseconds.py
SKIES). One function per shot; the contract is in films/sixseconds_common.py (tags "br...", C.actor, C.item, C.cam,
C.lights, C.pillar, st.use / st.hero).

STATUS: STUBS by the lead director. Each function puts the shot's camera on its place and its cast roughly where the
story wants them; the docstrings say what each shot must become. Everything may be rewritten except what SHARED
names.

THE PLACE (engine/nether.py BRIDGE, origin (400, 0, 0); out/test/nether_map_bridge.png): a deck 5 wide (walkway
x 399..401 of polished blackstone bricks, low broken brick walls on the edges, no edge wall at y 16..21 beside the
pillar nor at x 402, y 3..5, the boot camera's spot), y -8..44, between pairs of basalt pillars (y 2, 15, 28, 41)
with gold caps, rising from the lava sea 24 below (a lit lava glow: seen from deck level only over the edge, from
the pillar's height and side-on: br13, br15); ONE lantern on chains over bridge_brute (group bridge_lantern), four
under the deck's edges (bridge_under). Anchors: bridge_boot_mark (400.5, 6.5), bridge_player (400.5, 10.6) facing
north, bridge_brute (400.5, 16.5) facing south, bridge_pillar_foot (400.5, 18.25), bridge_pillar_top (400.5, 19.5, 3),
bridge_pillar_top_target (his head), six_bridge_ingot_1..3 (at the pillar's foot); path bridge_run_in.
THE NETHERRACK PILLAR (C.bas.pillar: three Breakables at (400, 19, 0..2)) stands only where C.pillar(s) says: br13,
br14, br15; br11, br12 and the flash sequence's fl16_bridge have none.
SHARED (films/sixseconds_common.py): CAMS["bridge_boot"] for br11 with BOOT_FRAME: THE BOOT FRAMING of pt05 (home)
  repeated on this set: 50 mm f/2, 3.8 blocks from the boots, the boots in the same place at the same size (x
  28-69 %, y 40-57 %). Keep the skid ON bridge_boot_mark; the lead turned the set's suggestion (45 mm aimed at x
  400.65, boots at x 17-56 %) to match. PLACES "bridge_boot_mark", "bridge_player", "bridge_brute", "pillar_foot",
  "pillar_top".
THE WORLD'S RULES that bite here: the runner wears the golden boots; the brute keeps the golden axe, never raised
  here (he waits); the pillar only where C.pillar allows; the ingots he ignores are dropped items (C.item) lying or
  landing on explicit floor points.
TAGS TAKEN by the stubs: runner_br (br11, br12, br13, br15), brute_br (br12-br15), gold_ingot_br14_k, _br15_k.
PREVIEW samples of this sequence: 9.
"""
from mathutils import Vector


def br11_boots(st, s, C, nar):
    """BEAT 11  "New world, different bastion, same boots."   frames 668-733 (66 f, 2.75 s), sky soul. OUT OF BLACK:
    the frames before 668 are the reset's black. Words: New 670, world 675, different 684, bastion 691, same 706,
    boots 714 (ends 725).

    STORY: Out of black, the boot shot again on a different set: a long blackstone bridge between basalt pillars over
    an orange lava glow, empty for one beat. Then the same legs sprint in and skid to a stop, golden boots mid-frame,
    exactly as before.
    Location: second bastion bridge, another world. Cast: the player (legs and boots). Effects: cut up from black,
    blackstone bridge, basalt pillars, gilded blackstone, lava glow far below, golden boots, skid stop, boot shot
    framing matched to sentence five.

    MUST BE SEEN, ON WHICH WORD
      frame 668       the EMPTY bridge (the new world: teal void, the deck receding past the pillars to the lantern),
                      already moving (a slow handheld drift at least)
      "different bastion" 684-706   the legs sprint in (from behind the lens's left: bridge_run_in passes 1.15 west
                      of the lens)
      "same boots" 706-725   the skid: the boots stopped on bridge_boot_mark, where BOOT_FRAME says (as in pt05)
    SHARED: CAMS["bridge_boot"] exactly, BOOT_FRAME; PLACES "bridge_boot_mark".
    KNOWN (the set builder): THE LAVA CANNOT BE SEEN from deck level here (24 below, under the deck's edge): "over an
      orange lava glow" is shown by br13 and br15.
    NOW (stub): the bridge boot camera; the runner enters at f0 + 14 from (400.5, -3) and sprints to the boot mark
      (arrives about 723). Hero: the boots.
    MEASURED (projection, the lead's scouting still out/test/sixseconds_scout_boots_br11.png): boots x 28-69 %, y
      40-56 %.
    NEIGHBOURS: before, pt10_smoke (black from "ended"); after, br12_blocks.
    """
    f0 = s.frame_start
    runner = C.actor("runner", "br")
    mark = C.P("bridge_boot_mark")
    a = (400.5, -3.0, 0.0)
    fs = f0 + 14
    C.put(runner, f0, a, toward=mark)
    runner.walk(fs, [a, mark], sprint=True, ramp=(False, True))
    st.use(s, runner)
    C.cam(s, "bridge_boot", focus=Vector(mark) + Vector((0.0, 0.0, 0.2)))
    st.hero(s, "boots", *C.boots_of(runner))
    C.lights(s, "bridge")


def br12_blocks(st, s, C, nar):
    """BEAT 12  "Every world has a bastion, and every bastion has me."   frames 734-827 (94 f, 3.92 s), sky soul.
    Words: Every 736, world 743, has 752, a 756, bastion 758, and 783, every 786, bastion 794, has 809, me 815
    (ends 820).

    STORY: Over the player's shoulder, third person: his back and shoulder fill the near edge of the frame. Down the
    bridge the brute stands square in the middle of it, blocking it, axe at his side, perfectly still, already facing
    him, under his own lantern.
    Cast: piglin brute, the player (back, foreground). Effects: golden axe, bridge with lava glow below, lantern on a
    chain as the brute's key light.

    MUST BE SEEN, ON WHICH WORD
      frame 734       the runner's back and shoulder at the near edge (soft), the brute down the bridge, still
      "has me" 809-820   the brute's face sharp under his lantern (focus on him from the start, or a rack to him on
                      "every bastion" 786)
    NOW (stub): engine/nether.py's bridge_shoulder (50 mm f/2.6 over the runner's shoulder at bridge_player), the
      runner at bridge_player looking at the brute, the brute at bridge_brute facing him, dead still. Hero: the brute.
    MEASURED (out/test/sixseconds_set_b12_bridge_shoulder.png under nether_wastes; out/test/
      sixseconds_scout_sky_b12_bridge_shoulder_soul_sand_valley.png under this film's sky): brute x 40-59 %, y
      39-47 %, 1.74 x the blackstone; the teal void behind him.
    NEIGHBOURS: before, br11_boots; after, br13_pillar.
    """
    f0 = s.frame_start
    runner = C.actor("runner", "br")
    brute = C.actor("brute", "br")
    C.put(brute, f0, "bridge_brute")
    C.stand(s, runner, "bridge_player", look="bridge_player_look")
    brute.look_at(f0, Vector(C.P("bridge_brute_look")), ease=0)
    brute.flop_ears(f0, s.frame_end + 1)
    st.use(s, brute)
    C.cam(s, "set:bridge_shoulder", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")


def br13_pillar(st, s, C, nar):
    """BEAT 13  "He hid on a pillar and threw gold at me."   frames 828-890 (63 f, 2.62 s), sky soul.
    Words: He 830, hid 832, on 837, a 840, pillar 841, and 857, threw 859, gold 867, at 876, me 879 (ends 885).

    STORY: Tall static composition made for the vertical frame, all of it between 14 and 60 percent of the height:
    the player crouches on top of a three-block netherrack pillar at the top of that zone. Directly below, the brute
    stands at its foot looking straight up. The player tosses a gold ingot and it drops the whole height of the
    pillar, past the brute's snout.
    Cast: the player (crouched on the pillar), piglin brute. Effects: three-block netherrack pillar, crouch pose, gold
    ingot tossed down (long fall), brute head pitched up, golden axe.

    MUST BE SEEN, ON WHICH WORD
      frame 828       the pillar with the runner crouched on top, the brute at its foot looking up
      "threw gold" 859-876   the toss (Player.throw or swing_arm + piglins.throw_item / launch toward
                      six_bridge_ingot_1) and the ingot's fall past the brute's snout, inside y 14-60 %
    RISK (story): "a face pitched straight up is the underside of a snout from most angles, and the tall tableau
      makes both figures small. Fallback: keep the brute in strict side profile for 13 and 14 and shorten the pillar
      to two blocks in frame by cropping its base behind him." (a piglin's pitch stops at 40 degrees)
    NOW (stub): engine/nether.py's bridge_pillar (30 mm f/4, side-on from the east over the void), C.pillar(s), the
      runner crouched on pillar_top with an ingot in his hand, the brute at pillar_foot looking up at the top. Hero:
      the brute.
    MEASURED (out/test/sixseconds_set_b13_bridge_pillar.png; under this film's sky
      out/test/sixseconds_scout_sky_b13_bridge_pillar_soul_sand_valley.png): brute x 30-42 %, y 39-46 %, 2.84 x;
      runner on the top at 13-29 % of the height; the lava at the bottom edge. Under the teal fog his teal shirt
      separates from the void by brightness only: check it at 360x640.
    NEIGHBOURS: before, br12_blocks; after, br14_zero.
    """
    f0 = s.frame_start
    C.pillar(s)
    runner = C.actor("runner", "br")
    C.put(runner, f0, "pillar_top")
    runner.hold("gold_ingot", frame=f0)
    runner.sneak(f0)
    st.use(s, runner)
    brute = C.actor("brute", "br")
    C.stand(s, brute, "pillar_foot", look="bridge_pillar_top_target", idle=False)
    C.cam(s, "set:bridge_pillar", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")


def br14_zero(st, s, C, nar):
    """BEAT 14  "I looked at it for zero seconds."   frames 891-945 (55 f, 2.29 s), sky soul.
    Words: I 893, looked 896, at 902, it 906, for 910, zero 914, seconds 923 (ends 937).

    STORY: Side-on medium on the brute in clean profile, head tilted up at the pillar top, feet no lower than 60
    percent of the frame height. The ingot falls past his snout and lands spinning at his feet. A second lands beside
    it. His head never dips.
    Cast: piglin brute. Effects: two gold ingots landing and spinning, golden axe, foot of the netherrack pillar at
    frame edge.

    MUST BE SEEN, ON WHICH WORD
      frame 891       the first ingot falling past his snout (in the air on the first frame: launched before the
                      shot, or the one of br13 continuing: a new item entity per shot)
      "it" 906        it lands spinning at his feet (six_bridge_ingot_1); "zero" 914 the second lands beside it
                      (six_bridge_ingot_2); his head NEVER dips (no idle glances: ears only)
    NOW (stub): engine/nether.py's bridge_profile (35 mm f/2.4 from 5.3 blocks), C.pillar(s), the brute at
      pillar_foot looking up, two ingots already lying at his feet. Hero: the brute.
    MEASURED (out/test/sixseconds_set_b14_bridge_profile.png): brute in profile, head up, x 33-58 %, y 18-32 %,
      2.69 x; his feet above 60 %; the pillar at the right edge.
    NEIGHBOURS: before, br13_pillar; after, br15_wait.
    """
    brute = C.actor("brute", "br")
    C.pillar(s)
    C.stand(s, brute, "pillar_foot", look="bridge_pillar_top_target", idle=False)
    for k in (1, 2):
        C.rest(s, "gold_ingot", "br14_%d" % k, "six_bridge_ingot_%d" % k)
    C.cam(s, "set:bridge_profile", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")


def br15_wait(st, s, C, nar):
    """BEAT 15  "I can wait, and he can't."   frames 946-991 (46 f, 1.92 s), sky soul.
    Words: I 948, can 951, wait 955, and 965, he 968, can't 970 (ends 982); the flash cuts start on 992, 10 frames
    before "I ended".

    STORY: High angle from just behind the player on the pillar top, third person: his back and head are the big
    foreground shape in the lower part of the frame, sneak-bobbing up and down and snapping left and right. Above his
    shoulder, far below on the bridge, the brute's upturned face, perfectly still, three ingots turning ignored at
    his feet. Slow push down toward the brute.
    Cast: the player (back, sneak-bobbing), piglin brute. Effects: sneak-bob (crouch spam) animation, head snaps left
    and right, three gold ingots spinning on the bridge, slow push in.

    MUST BE SEEN, ON WHICH WORD
      frame 946       the runner already sneak-bobbing (Player.sneak on / off every 3-4 frames: the game's crouch
                      spam), the push already moving
      "I can wait" 948-965   the brute's upturned face perfectly still (no idle), three ingots at his feet
      "he can't" 968-982     the runner's head snapping left and right (look_at with ease 0..2)
    NOW (stub): engine/nether.py's bridge_top (30 mm f/3, high behind the runner on the pillar), C.pillar(s), the
      runner crouched on pillar_top, the brute at pillar_foot looking up at him, three ingots lying at his feet.
      Hero: the brute.
    MEASURED (out/test/sixseconds_set_b15_bridge_top.png): brute x 41-51 %, y 40-50 %, 2.48 x; the runner's back
      the big shape at the right; the lava visible below.
    NEIGHBOURS: before, br14_zero; after, fl16_bridge (the flash cut in this world: the brute, a puff, the boots).
    """
    f0 = s.frame_start
    C.pillar(s)
    runner = C.actor("runner", "br")
    C.put(runner, f0, "pillar_top")
    runner.sneak(f0)
    st.use(s, runner)
    brute = C.actor("brute", "br")
    C.stand(s, brute, "pillar_foot", look=(400.5, 19.6, 4.6), idle=False)
    for k in (1, 2, 3):
        C.rest(s, "gold_ingot", "br15_%d" % k, "six_bridge_ingot_%d" % k)
    C.cam(s, "set:bridge_top", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")
