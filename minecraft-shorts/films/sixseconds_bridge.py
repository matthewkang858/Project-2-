"""Six Seconds, sequence BRIDGE: the second bastion, in another world. The boot shot again, the brute blocking the
bridge, the pillar: beats 11, 12, 13, 14, 15 (shots br11_boots, br12_blocks, br13_pillar, br14_zero, br15_wait), sky
"soul" (soul_sand_valley: the fog and the void of this world are TEAL; the lead's choice, films/sixseconds.py
SKIES). One function per shot; the contract is in films/sixseconds_common.py (tags "br...", C.actor, C.item, C.rest,
C.cam, C.rack, C.lights, C.pillar, st.use / st.hero).

STATUS: STUBS by the lead director, revised in the lead's review pass (two independent checks). Each function puts
the shot's camera on its place and its cast roughly where the story wants them; the docstrings say what each shot
must become. Everything may be rewritten except what SHARED names.

THE PLACE (engine/nether.py BRIDGE, origin (400, 0, 0); out/test/nether_map_bridge.png): a deck 5 wide (walkway
x 399..401 of polished blackstone bricks, low broken brick walls on the edges, no edge wall at y 16..21 beside the
pillar nor at x 402, y 3..5, the boot camera's spot), y -8..44, between pairs of basalt pillars (y 2, 15, 28, 41)
with gold caps, rising from the lava sea 24 below (a lit lava glow: seen from deck level only over the edge, from
the pillar's height and side-on: br13, br15); ONE lantern on chains over bridge_brute (group bridge_lantern), four
under the deck's edges (bridge_under). Anchors: bridge_boot_mark (400.5, 6.5), bridge_player (400.5, 10.6) facing
north, bridge_brute (400.5, 16.5) facing south, bridge_pillar_foot (400.5, 18.25), bridge_pillar_top (400.5, 19.5, 3)
facing south, bridge_pillar_top_target (his head); this film's six_pillar_brute (401.0, 18.25) facing north (THE
BRUTE'S PLACE AT THE PILLAR in br13, br14 and br15) and six_bridge_ingot_1..3 = six_pillar_brute + (0.75, -0.1),
(0.6, -0.4), (0.45, -0.65) (films/sixseconds_set.py PILLAR_BRUTE_SHIFT, PILLAR_INGOTS); path bridge_run_in.
THE NETHERRACK PILLAR (C.bas.pillar: three Breakables at (400, 19, 0..2)) stands only where C.pillar(s) says: br13,
br14, br15; br11, br12 and the flash sequence's fl16_bridge have none.
SHARED (films/sixseconds_common.py): CAMS["bridge_boot"] for br11 with BOOT_FRAME: THE BOOT FRAMING of pt05 (home)
  repeated on this set: 50 mm f/2, 3.8 blocks from the boots, the boots in the same place at the same size (x
  27-71 %, y 42-59 %: measured on both sets); its FOCUS is free (the stub holds it far, then racks). Keep the skid ON
  bridge_boot_mark. PLACES "bridge_boot_mark", "bridge_player", "bridge_brute", "pillar_brute" (the same in all three
  pillar shots, with the ingots at six_bridge_ingot_k: move them together or not at all), "pillar_top".
THE LEAD'S REVIEW PASS, what changed here and why (each measured; the stills are named in the shots):
  * br11: the runner stopped only on 726-728 of the old timeline, after "same boots", and the empty bridge was a dark
    blur (f/2 focused 3.8 blocks off). Now he sprints from behind the lens from 683, enters the frame's left edge on
    "bastion" (699), the boots stop by about 716 and hold to the cut; the focus holds the pillars far, racks to the
    boots as his legs come in.
  * br13-br15: the brute stood on pillar_foot in br13 / br14 and 0.5 east of it in br15 (the pillar cut his face from
    bridge_top), standing ON one of the br14 ingots across the cut, and every ingot lay behind his body or in the
    caption band from br15's camera (the story check). Now: one place for all three (six_pillar_brute, the br15
    one), the ingots on his east side (seen from the east cameras of br13 / br14 and from br15's), br15's camera
    aimed 1.5 block lower (BR15_CAM).
  * the runner's hand is set on the first frame of every shot (pickaxe in br11 / br12, gold in br13 / br15).
THE WORLD'S RULES that bite here: the runner wears the golden boots; the brute keeps the golden axe, never raised
  here (he waits); the pillar only where C.pillar allows; the ingots he ignores are dropped items (C.item / C.rest)
  lying or landing on explicit floor points; nothing from an engine call that is not registered (ENGINE SIDE DOORS).
TAGS TAKEN by the stubs: runner_br (br11, br12, br13, br15), brute_br (br12-br15), gold_ingot_br14_k, _br15_k.
PREVIEW samples of this sequence: 9.
"""
from mathutils import Vector

# br11: the runner sprints in from behind the lens (at speed, unseen: the lens is at y 2.9) on RUN_FROM, so that the
# bridge is EMPTY for a beat out of black, his legs enter from the frame's left on "bastion" and the boots stop on the
# mark before "same boots" (the story check: the first stub stopped them only on 726-728, after the words)
BR11_RUN_FROM = (400.5, 0.0, 0.0)
BR11_RUN_START = 683
# br11's focus: far on the empty bridge (the pillars, the lantern over bridge_brute) out of black, racked to the boot
# mark as the legs come in (the shared camera's focus is free; its f/2 at 3.8 blocks left the empty bridge a blur)
BR11_FAR = (400.5, 15.0, 1.6)
# br15: bridge_top aimed 1.5 block lower (the story check: from the set's aim his feet were at y 60 % and every ingot
# that his body did not hide lay in the caption band)
BR15_CAM = dict(pos=(402.3, 21.4, 5.4), target=(400.2, 17.4, -1.2), lens=30.0, fstop=3.0)


def br11_boots(st, s, C, nar):
    """BEAT 11  "New world, different bastion, same boots."   frames 668-740 (73 f, 3.04 s), sky soul. OUT OF BLACK:
    the frames before 668 are the reset's black ("ended" held on it); the picture comes up in silence, 9 frames before
    the first word. Words: New 677, world 682, different 691, bastion 699, same 714, boots 721 (ends 732).

    STORY: Out of black, the boot shot again on a different set: a long blackstone bridge between basalt pillars over
    an orange lava glow, empty for one beat. Then the same legs sprint in and skid to a stop, golden boots mid-frame,
    exactly as before.
    Location: second bastion bridge, another world. Cast: the player (legs and boots). Effects: cut up from black,
    blackstone bridge, basalt pillars, gilded blackstone, lava glow far below, golden boots, skid stop, boot shot
    framing matched to sentence five.

    MUST BE SEEN, ON WHICH WORD
      668 .. 698      the EMPTY bridge: the teal void, basalt pillars with gold caps, sharp (focus far), already moving
                      (the handheld drift at least) under "New world, different"
      "bastion" 699   the legs sprint in from the frame's LEFT edge (from behind the lens: he passes 1.15 west of it)
      by about 716    the skid done: the boots stopped on bridge_boot_mark where BOOT_FRAME says (as in pt05), and
                      held to the cut (about 25 frames: pt05 holds them 22) under "same boots" (714-732)
    SHARED: CAMS["bridge_boot"] exactly (its focus is free), BOOT_FRAME; PLACES "bridge_boot_mark".
    KNOWN (the set builder): THE LAVA CANNOT BE SEEN from deck level here (24 below, under the deck's edge): "over an
      orange lava glow" is shown by br13 and br15.
    NOW (stub): the runner waits behind the lens at BR11_RUN_FROM (400.5, 0.0), sprints from 683 at speed (sprint,
      ramp out: the skid) to the mark; the focus holds BR11_FAR (the pillars 15 blocks off) and racks to the mark over
      10 frames from "bastion" + 2 (C.rack). Hero: the boots.
    MEASURED (the lead's review pass; tools.sixseconds_geo --sky soul br11_boots:716 / :725 --boots runner_br, the
      probe of his track; stills out/test/sixseconds_scout_br11_boots_685.png (the empty bridge, focus far: the
      basalt pillars and their gold caps against the teal void read), _703.png (his leg entering, soft), _725_zones.png
      (the boots stopped)): he is behind the lens to about 696, his body enters the frame's left edge on 699-702, the
      feet come to rest by about 716-718 (6.24 on 714, 6.47 on 718, 6.50 on 722); boots x 27.7-69.8 %, y 42.7-58.6 %
      on 725 (pt05 on 318: x 27.7-70.1 %, y 43.1-58.9 %): THE BOOT FRAMING holds. Palette 725: shirt hue 171, pants
      min channel 14, boots 100 % inside the safe area. His back is to the lens here (he runs north, toward br12's
      brute); in pt05 he faces it (he came from the gateway): each is right for its neighbours.
    NEIGHBOURS: before, pt10_smoke (black from "ended"); after, br12_blocks.
    """
    f0 = s.frame_start
    runner = C.actor("runner", "br")
    mark = C.P("bridge_boot_mark")
    a = BR11_RUN_FROM
    C.put(runner, f0, a, toward=mark)
    runner.hold("iron_pickaxe", frame=f0)
    runner.walk(BR11_RUN_START, [a, mark], sprint=True, ramp=(False, True))
    st.use(s, runner)
    C.cam(s, "bridge_boot", focus=Vector(BR11_FAR))
    C.rack(s, Vector(mark) + Vector((0.0, 0.0, 0.2)), C.at(s, "bastion") + 2, 10)
    st.hero(s, "boots", *C.boots_of(runner))
    C.lights(s, "bridge")


def br12_blocks(st, s, C, nar):
    """BEAT 12  "Every world has a bastion, and every bastion has me."   frames 741-834 (94 f, 3.92 s), sky soul.
    Words: Every 743, world 750, has 759, a 764, bastion 765, and 790, every 794, bastion 801, has 816, me 822
    (ends 827).

    STORY: Over the player's shoulder, third person: his back and shoulder fill the near edge of the frame. Down the
    bridge the brute stands square in the middle of it, blocking it, axe at his side, perfectly still, already facing
    him, under his own lantern.
    Cast: piglin brute, the player (back, foreground). Effects: golden axe, bridge with lava glow below, lantern on a
    chain as the brute's key light.

    MUST BE SEEN, ON WHICH WORD
      frame 741       the runner's back and shoulder at the near edge (soft), the brute down the bridge, still
      "has me" 816-827   the brute's face sharp under his lantern (focus on him from the start, or a rack to him on
                      "every bastion" 794)
    NOW (stub): engine/nether.py's bridge_shoulder (50 mm f/2.6 over the runner's shoulder at bridge_player), the
      runner at bridge_player looking at the brute (iron pickaxe), the brute at bridge_brute facing him, dead still.
      Hero: the brute.
    MEASURED (out/test/sixseconds_set_b12_bridge_shoulder.png under nether_wastes; out/test/
      sixseconds_scout_sky_b12_bridge_shoulder_soul_sand_valley.png under this film's sky): brute x 40-59 %, y
      39-47 %, 1.74 x the blackstone; the teal void behind him.
      UNDER THIS FILM'S SKY "soul" (the lead: tools.sixseconds_palette --sky soul on the old timeline's 780, still
      out/test/sixseconds_pal_br12_blocks_780.png; out/test/sixseconds_scout_br12_blocks_815_zones.png): brute x
      1.52 the blackstone (46 vs 30: AT the 1.5 limit; 1.74 under nether_wastes), gold hue 46, shirt hue 171. Give
      him more of his lantern (C.lights(s, "bridge", groups={"bridge_lantern": k}) with k up to about 1.5, measured)
      or a film-local key C.fill("br_key", ...) before anything else; re-measure. (Not changed by the review pass:
      the frames named in those stills are the old timeline's, 7 frames earlier.)
    NEIGHBOURS: before, br11_boots; after, br13_pillar.
    """
    f0 = s.frame_start
    runner = C.actor("runner", "br")
    brute = C.actor("brute", "br")
    C.put(brute, f0, "bridge_brute")
    C.stand(s, runner, "bridge_player", look="bridge_player_look")
    runner.hold("iron_pickaxe", frame=f0)
    brute.look_at(f0, Vector(C.P("bridge_brute_look")), ease=0)
    brute.flop_ears(f0, s.frame_end + 1)
    st.use(s, brute)
    C.cam(s, "set:bridge_shoulder", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")


def br13_pillar(st, s, C, nar):
    """BEAT 13  "He hid on a pillar and threw gold at me."   frames 835-897 (63 f, 2.62 s), sky soul.
    Words: He 837, hid 840, on 844, a 847, pillar 849, and 864, threw 867, gold 874, at 883, me 886 (ends 892).

    STORY: Tall static composition made for the vertical frame, all of it between 14 and 60 percent of the height:
    the player crouches on top of a three-block netherrack pillar at the top of that zone. Directly below, the brute
    stands at its foot looking straight up. The player tosses a gold ingot and it drops the whole height of the
    pillar, past the brute's snout.
    Cast: the player (crouched on the pillar), piglin brute. Effects: three-block netherrack pillar, crouch pose, gold
    ingot tossed down (long fall), brute head pitched up, golden axe.

    MUST BE SEEN, ON WHICH WORD
      frame 835       the pillar with the runner crouched on top, the brute at its foot looking up
      "threw gold" 867-883   the toss (Player.throw or swing_arm + piglins.throw_item / launch to
                      six_bridge_ingot_1: the ingot that lies there in br14) and the ingot's fall past the brute's
                      snout, inside y 14-60 %
    SHARED: PLACES "pillar_brute" (the brute's place in all three pillar shots), "pillar_top", six_bridge_ingot_1..3.
    RISK (story): "a face pitched straight up is the underside of a snout from most angles, and the tall tableau
      makes both figures small. Fallback: keep the brute in strict side profile for 13 and 14 and shorten the pillar
      to two blocks in frame by cropping its base behind him." (a piglin's pitch stops at 40 degrees)
    NOW (stub): engine/nether.py's bridge_pillar (30 mm f/4, side-on from the east over the void), C.pillar(s), the
      runner crouched on pillar_top with an ingot in his hand, the brute at pillar_brute looking up at the top. Hero:
      the brute.
    MEASURED after the review pass (tools.sixseconds_geo --sky soul br13_pillar:840 / :870): brute eyes x 38 %,
      y 41.6 %, head x 27-44 %, y 38-47 %, 63 px, in profile (107 degrees off the lens), pitched to the game's 40;
      the runner's head x 56-66 %, y 12.4-18.7 %: its top is UNDER the Reels top icons (y < 13-14 %): aim the camera
      a little higher or pull back (the story wants the whole tableau inside y 14-60 %); the ingot spots
      six_bridge_ingot_1..3 x 35 / 29.5 / 25 %, y 60-61 % (on the caption band's top edge: the same tilt fixes both).
      Earlier (set still b13, the brute on pillar_foot): 2.84 x the blackstone; under the teal fog his teal shirt
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
    C.stand(s, brute, "pillar_brute", look="bridge_pillar_top_target", idle=False)
    C.cam(s, "set:bridge_pillar", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")


def br14_zero(st, s, C, nar):
    """BEAT 14  "I looked at it for zero seconds."   frames 898-952 (55 f, 2.29 s), sky soul.
    Words: I 900, looked 904, at 910, it 913, for 917, zero 921, seconds 931 (ends 944).

    STORY: Side-on medium on the brute in clean profile, head tilted up at the pillar top, feet no lower than 60
    percent of the frame height. The ingot falls past his snout and lands spinning at his feet. A second lands beside
    it. His head never dips.
    Cast: piglin brute. Effects: two gold ingots landing and spinning, golden axe, foot of the netherrack pillar at
    frame edge.

    MUST BE SEEN, ON WHICH WORD
      frame 898       the first ingot falling past his snout (in the air on the first frame: launched before the
                      shot, or the one of br13 continuing: a new item entity per shot)
      "it" 913        it lands spinning at his feet (six_bridge_ingot_1); "zero" 921 the second lands beside it
                      (six_bridge_ingot_2); his head NEVER dips (no idle glances: ears only)
    SHARED: PLACES "pillar_brute", six_bridge_ingot_1..3 (br15 shows all three where br14 leaves two).
    NOW (stub): engine/nether.py's bridge_profile (35 mm f/2.4 from 5.3 blocks), C.pillar(s), the brute at
      pillar_brute looking up, two ingots already lying at his feet. Hero: the brute.
    MEASURED after the review pass (tools.sixseconds_geo --sky soul br14_zero:913): brute in profile (112 degrees off
      the lens), head x 29-63 %, y 15.5-32.7 %, 125 px, pitched up 40; the ingot spots six_bridge_ingot_1 / _2 / _3 at
      x 46 / 34 / 25 %, y 61.7 / 60.7 / 59.8 %: ON the caption band's top edge (his feet are at y 60 %): aim the
      camera a little lower (about 0.3 block) so the feet and the ingots sit at y 55-58 %. Earlier (set still b14,
      the brute on pillar_foot): 2.69 x the blackstone; the pillar at the right edge.
    NEIGHBOURS: before, br13_pillar; after, br15_wait.
    """
    brute = C.actor("brute", "br")
    C.pillar(s)
    C.stand(s, brute, "pillar_brute", look="bridge_pillar_top_target", idle=False)
    for k in (1, 2):
        C.rest(s, "gold_ingot", "br14_%d" % k, "six_bridge_ingot_%d" % k)
    C.cam(s, "set:bridge_profile", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")


def br15_wait(st, s, C, nar):
    """BEAT 15  "I can wait, and he can't."   frames 953-998 (46 f, 1.92 s), sky soul.
    Words: I 955, can 958, wait 963, and 972, he 975, can't 978 (ends 990); the flash cuts start on 999, 10 frames
    before "I ended".

    STORY: High angle from just behind the player on the pillar top, third person: his back and head are the big
    foreground shape in the lower part of the frame, sneak-bobbing up and down and snapping left and right. Above his
    shoulder, far below on the bridge, the brute's upturned face, perfectly still, three ingots turning ignored at
    his feet. Slow push down toward the brute.
    Cast: the player (back, sneak-bobbing), piglin brute. Effects: sneak-bob (crouch spam) animation, head snaps left
    and right, three gold ingots spinning on the bridge, slow push in.

    MUST BE SEEN, ON WHICH WORD
      frame 953       the runner already sneak-bobbing (Player.sneak on / off every 3-4 frames: the game's crouch
                      spam), the push already moving
      "I can wait" 955-972   the brute's upturned face perfectly still (no idle), three ingots at his feet
      "he can't" 975-990     the runner's head snapping left and right (look_at with ease 0..2)
    SHARED: PLACES "pillar_brute", six_bridge_ingot_1..3.
    NOW (stub): BR15_CAM (engine/nether.py's bridge_top, 30 mm f/3 high behind the runner on the pillar, aimed 1.5
      block lower), C.pillar(s), the runner crouched on pillar_top (gold in his hand), the brute at pillar_brute
      looking up at him, three ingots lying at his feet. Hero: the brute.
    MEASURED after the review pass (tools.sixseconds_geo --sky soul br15_wait:963 / :968 --pts the ingots;
      tools.sixseconds_palette --sky soul 968; still out/test/sixseconds_scout_br15_wait_968_zones.png): brute eyes
      x 40.5 %, y 37 %, head x 23-52 %, y 30-43 %, 102 px, NOT blocked (43 degrees off the lens, pitched up 40: the
      upturned face reads); the three ingots x 25-27 %, y 48.6 / 51.7 / 55.5 %, none hidden (the story check had all
      three blocked or in the caption band: fixed); brute x 3.25 the blackstone, shirt hue 174, pants min channel
      16: all pass. The runner's back is the big shape on the RIGHT (x 50-100 %, from the top to about y 60 %); his
      head sits at the top right corner (x 72-122 %, y -15..13 %: outside the frame and under the top icons), not
      "in the lower part of the frame" as the story has it: from any camera above and behind him the brute is BELOW
      him in the frame unless the lens looks nearly straight down (measured: from (400.7, 20.6, 6.5) his arm hides
      the brute's eyes; from (401.2, 21.0, 6.3) 28 mm the brute is clear, 88 px, his head at the right edge). The
      director chooses; keep the brute's eyes and the three ingots clear (geo --pts) and inside y 14-60 %.
      Earlier MEASURED PROBLEM (fixed): with the brute ON pillar_foot (400.5, 18.25) the pillar's top block cut his
      face in half from bridge_top (his eyes behind bridge_pillar_2, 3.7 blocks from the lens).
    NEIGHBOURS: before, br14_zero; after, fl16_bridge (the flash cut in this world: the brute, a puff, the boots).
    """
    f0 = s.frame_start
    C.pillar(s)
    runner = C.actor("runner", "br")
    C.put(runner, f0, "pillar_top")
    runner.hold("gold_ingot", frame=f0)
    runner.sneak(f0)
    st.use(s, runner)
    brute = C.actor("brute", "br")
    C.stand(s, brute, "pillar_brute", look=(400.5, 19.6, 4.6), idle=False)
    for k in (1, 2, 3):
        C.rest(s, "gold_ingot", "br15_%d" % k, "six_bridge_ingot_%d" % k)
    C.cam(s, None, focus=brute.head, **BR15_CAM)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")
