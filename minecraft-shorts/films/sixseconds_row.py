"""Six Seconds, sequence ROW: the gold wall. The ingot row of beat 2, the brothers' look at the boots (beat 5's second
shot) and the six-second stare at the end: beats 2, 5, 21, 22, 23 (shots rw02_ingots, rw05_family, rw21_stare,
rw22_six, rw23_nothing), sky "wastes". One function per shot; the contract is in films/sixseconds_common.py (tags
"rw...", C.actor, C.item, C.cam, C.lights, st.use / st.hero).

STATUS: SHOT by the row director (Nov 26) from the lead's stubs. Each shot's docstring has its NOW and MEASURED lines;
the stills are out/test/rw_<shot>_<frame>[_zones].png (540x960, 16 samples), the palette checks out/test/
sixseconds_pal_<shot>_<frame>.png, the motion out/test/sixseconds_row_motion.mp4 (270x480, 6 samples, every frame).
THE SEQUENCE NOW
  rw02  the ingot row frame (shared, unchanged): the brothers frozen over their ingots, the focus on the near
        brother's ingot (the only one the frame shows broad: brother 2's lies edge-on along his hand); the brute's soft
        shoulder at the right edge, alive (weight shift, arm bob: his eyes stay at x 121 %, off the frame)
  rw05  from the boots' height, a slow creep along the floor: the three at the gold, backs to us; from "so my" they
        turn round a beat apart (body and head together, 14 frames), faces tipped down into the lens 345-355, and turn
        back from "family" two frames apart, done by 371
  rw21  the ingot row frame again, the brute between them, head down (ears only for six seconds); the focus opens on
        the near brother as beat 2 left it and pulls back to the brute on "I'm staring"
  rw22  from above on his line of sight, 28 mm, a level push: the ingot turning sharp in the middle, broad side on
        "Six" and again at the end of the stare (1494), his face soft above it
  rw23  the reverse angle on his line to the gateway at eye height, 2.7 blocks off: his head comes up from the ingot
        and round into the lens on "Nothing" (18 frames), held to the black; the gold wall soft at the left, brother 2
        a soft head-down sliver and his sword's hilt at the right edge
TOOLS: tools/sixseconds_row_probe.py (the row director's own: frame boxes of every part and held item for any
  camera, the step ingot's angle to the lens frame by frame, the head angles of the cast frame by frame).

THE PLACE (engine/nether.py HOME, films/sixseconds_set.py beats 2 and 21-23): the GOLD WALL, 21 gold blocks in the
east wall's inner face (x 9, y 9..15, z 0..2), basalt-framed, the one-block blackstone STEP in front of it (x 8,
y 9..15, top z 1), two lanterns over the step (group home_gold). The brothers at "brother_1" (7.0, 13.2) and
"brother_2" (6.3, 10.8), the brute at "brute_gold" (7.6, 10.0), all facing north-east (yaw 2.356, the gold
diagonally); his ingot on the step at "step_ingot" (8.16, 11.71, 1.0): in front of his chest, 17 degrees left of
straight ahead, 1.8 away, head pitch 21 (a brute cannot look below 40, nor turn his head more than 75). The
layout exists for rw22 (the only camera spot beyond the ingot on his line of sight) and rw23 (his head reaches the
gateway's mouth at 65 of 75 degrees). For rw05 the three piglins of the gate frame stand at PLACES gold_1..3
(7.3, 9.6), (6.3, 11.2), (7.3, 12.8) facing east, as in gt03 / pt05.
SHARED (films/sixseconds_common.py): CAMS["ingot_row"] in rw02 and rw21 EXACTLY (the frame returns: "the ingot row
  frame"; its focus is free); PLACES brother_1 / brother_2 / brute_gold / step_ingot / brute_turned / gateway_mouth;
  PLACES gold_1..3 and boot_mark (rw05: pt05's runner stands on boot_mark, his boots are what they look at). Not
  shared (this file's own constants): FAMILY (rw05), INGOT_CLOSE (rw22), REVERSE (rw23; the stand-in of a failed row
  shot is CAMS["ingot_row"]).
THE WORLD'S RULES that bite here: floor whole (no C.pit); the brute 0.7 block or more from either brother; the
  brothers admire with the ingot in the LEFT hand, golden sword in the right (C.admire); the brute keeps the golden
  axe in his hand; piglins' heads within 75 degrees of yaw and 40 of pitch from their bodies (rw05 turns the
  bodies).
THE SIX SECONDS: rw21 (58 frames) + rw22 (86) = 144 frames exactly from the first frame of rw21 (1358) to the cut into
  rw23 (1502) (films/sixseconds.py asserts it): the stare starts on rw21's first frame and the ingot turns through
  all three shots. ONE ingot entity (C.memo["rw_ingot"]) turns without a break from rw21 to the end; its spin is
  phased (C.broadside toward INGOT_CLOSE) so its broad side faces rw22's lens 2 frames after "Six" (1420; the stub's
  own phase had it 73 degrees off, nearly edge-on, on "Six": tools/sixseconds_row_probe ingot). It turns once in 151
  frames (the game's age / 20 radians a tick): edge-on at 1458, broad again at 1494, just before the cut.
TAGS TAKEN by the stubs: piglin_rw1, piglin_rw2 (rw02, rw21, rw23: the brothers), piglin_rw3 / piglin_rw4 /
  piglin_xbow_rw5 (rw05: the three of the gate frame), brute_rw (rw02, rw21-rw23), gold_ingot_rw (rw21-rw23).
PREVIEW samples of this sequence: 6.
"""
from mathutils import Vector

# rw05: the brothers' look at the golden boots, from the boots' height: a lens on the floor 1.8 block east of the
# boot mark (from the mark itself gold_2 and gold_3 stand on one line and gold_1 falls outside x 82 %: the lead's geo)
# looking up at the three piglins at the gold; they turn and tip their heads down INTO the lens (the boots' point of
# view: the boots were the last shot). A slow creep along the floor toward them (0.15 block, linear): the picture
# moves on frame 1 while they still face the gold
FAMILY = dict(pos=(5.35, 5.7, 0.3), target=(7.25, 10.9, 1.5), lens=28.0, fstop=2.8, pos1=(5.4, 5.84, 0.3))
# rw05: when each of the three turns round to the lens (frames from the shot's first frame: a beat apart, the first
# on "so my", the last on "brothers"), how long the about-face takes (the head swings about 176 degrees in the world:
# body and head together, 14 frames = 12.6 degrees a frame, a brisk mob turn), when each turns back (from "family",
# two frames apart) and how long that takes. All three faces are on the lens from 345 to 355 ("thought he was").
FAMILY_TURN, FAMILY_TURN_FRAMES = (3, 6, 9), 14
FAMILY_BACK, FAMILY_BACK_FRAMES = (1, 3, 5), 12
# rw22: on his line of sight beyond the ingot, as the set's six_ingot_close, but at z 2.15 (0.36 over his eyes) and
# 0.6 block nearer: the ingot sits in the middle under his face instead of across his snout (the technical check:
# from z 1.62 the ingot covered his snout and tusks on every frame; the lead's three variants on renders: z 1.75 with
# 0.5 to the side, z 1.95 with 0.3 to the side, z 2.15 on the line: out/test/sixseconds_scout_rw22var_*.png; on the
# line from above is the story's "face just above it", and he reads as looking DOWN at it). The geometry (the row
# director's check): on his line the ingot's top (z 1.69 at the top of its bob) clears his snout (z 1.40) only for a
# lens above z 1.69 + 0.19 x its distance to the ingot, so "from below eye height" cannot put the face above the
# ingot. 28 mm (the stub's 32 mm put the broadside ingot's lower edge at y 64-68 %, in the caption band, under "Six"
# and "seconds", and his scalp at y 9-13 %) aimed 0.05 lower; a slow linear push of 0.15 block, LEVEL along his line
# (a level push steepens the view: the gap between snout and ingot opens as it goes; the stub's 0.1 block along the
# aim changed his head by 1 % of the frame in 86 frames, not seen)
INGOT_CLOSE = dict(pos=(8.6, 13.25, 2.15), target=(8.05, 11.3, 1.2), pos1=(8.559, 13.106, 2.15), lens=28.0,
                   fstop=2.8)
INGOT_BROADSIDE = 2     # rw22: the step ingot shows the lens its broad side this many frames after "Six"
# rw23: beat 23's reverse angle (the story's fallback): ON the line from the brute to the gateway's mouth (what he
# turns to), 2.7 blocks from him, at his eye height. Brother 1 (the lead's REVERSE had him 2.5 blocks from the lens,
# a big soft shape over the left third) is 0.6 block BEHIND this lens; from eye height brother 2's golden sword passes
# under the brute's waist into the lower right corner instead of across his chest (the lead's floor-level lens put it
# at y 50-62 %, across him); brother 2 is a soft head-down sliver at the right edge, the gold wall soft at the left.
# 28 mm: his face about 170 px; a slow push in (ease out). He lifts his head from the ingot straight into the lens.
REVERSE = dict(pos=(6.68, 12.54, 1.72), target=(7.6, 10.0, 1.5), lens=28.0, fstop=2.8,
               pos1=(6.73, 12.41, 1.71), target1=(7.6, 10.0, 1.5))
NOTHING_LIFT = 18       # rw23: frames of the head lift and turn from the ingot into the lens, from "Nothing"
# rw23: a film-local shadowless near-neutral fill beside the lens (C.fill, this shot only): under the gold wall's
# lanterns alone brother 2's skin at the right edge measured s 0.63 (nether.check_still's limit 0.62)
NOTHING_FILL = dict(pos=(6.35, 12.25, 2.0), watts=60.0, color=(1.0, 0.98, 0.96))


def _brothers(st, s, C):
    """The two brothers on their places, admiring (ingot in the left hand at the snout) through the whole shot."""
    b1, b2 = C.actor("piglin", "rw1"), C.actor("piglin", "rw2")
    for b, place in ((b1, "brother_1"), (b2, "brother_2")):
        C.put(b, s.frame_start, place)
        C.admire(s, b)
    st.use(s, b1, b2)
    return b1, b2


def _ingot(st, s, C):
    """The ingot on the step, ONE entity turning from rw21's first frame to the film's end (in this shot). Its spin
    is phased so that it shows rw22's lens its broad side INGOT_BROADSIDE frames after "Six" (C.broadside)."""
    it = C.memo.get("rw_ingot")
    if it is None:
        it = C.memo["rw_ingot"] = C.item("gold_ingot", "rw")
        f0 = C.T["rw21_stare"].frame_start
        it.place(f0, C.P("step_ingot"))
        six = C.T["rw22_six"].at("Six") + INGOT_BROADSIDE
        it.animate(f0, C.T["rw23_nothing"].frame_end + 1, phase=C.broadside(it, INGOT_CLOSE["pos"], six))
    st.use(s, it)
    return it


def rw02_ingots(st, s, C, nar):
    """BEAT 2  "My brothers will stare at one ingot for six seconds."   frames 98-178 (81 f, 3.38 s), sky wastes.
    Words: My 100, brothers 105, will 115, stare 119, at 127, one 131, ingot 138, for 147, six 151, seconds 159
    (ends 171).

    STORY: The ingot row frame (returns in the last scene): side-on close shot at snout height in front of the gold
    wall. A piglin holds a gold ingot up in his left hand in front of his snout, head tilted down to it, frozen, his
    golden sword still in his right hand. A second piglin beside him does exactly the same. The brute's dark shoulder
    is soft at the edge of the foreground, turned away from them.
    Cast: two piglins, piglin brute (shoulder only). Effects: two gold ingots held in the admire pose (left hand),
    golden swords in the right hands, gold-block wall and its one-block blackstone step, lantern light, ingot row
    camera preset re-used in sentence twenty-one.

    MUST BE SEEN, ON WHICH WORD
      frame 98        the two brothers already frozen over their ingots; something moving (a slow drift, the ears)
      "ingot" 138     the near brother's ingot sharp at his snout (focus on it: a small thing is seen only if it is
                      what is in focus)
      the whole shot  the brute's dark shoulder soft at the right edge, turned away (never his face)
    SHARED: CAMS["ingot_row"] exactly; PLACES brother_1 / brother_2, brute_turned.
    NOW (stub): exactly that, focus on brother 1's head. Hero: brother 1.
    MEASURED (out/test/sixseconds_set_b02_ingot_row.png): hero piglin x 8-41 %, y 37-54 % (at the left edge of the
      safe area); gold hue 46, piglin skin hue 22 s 0.57.
    NEIGHBOURS: before, gt01_landing; after, gt03_guard (the gate frame).
    """
    f0 = s.frame_start
    b1, _b2 = _brothers(st, s, C)
    brute = C.actor("brute", "rw")
    C.stand(s, brute, "brute_turned", idle=True, seed=2)      # alive: weight shift, arm bob, glances (eyes off frame)
    near = b1.item_point(f0 + 2, "off")                       # the near brother's ingot: the one shown broad
    C.cam(s, "ingot_row", focus=near)                         # (brother 2's lies edge-on along his hand)
    st.hero(s, "piglin", b1)
    C.lights(s, "home")


def rw05_family(st, s, C, nar):
    """BEAT 5 (2 of 2)  "so my brothers thought he was family."   frames 322-378 (57 f, 2.38 s), sky wastes.
    Words: so 324, my 328, brothers 333, thought 343, he 348, was 350, family 354 (ends 366).

    STORY (beat 5): "... Behind them three piglins turn from the gold, tip their heads down at the boots, hold, then
    turn back to the gold. Rack focus from the boots to the piglins and back so the look at the boots is sharp."
    WHY A SHOT OF ITS OWN (the lead's decision after the technical check): in pt05's boot framing the runner's torso
      and arms cover the piglins' heads wherever they stand (pt05's docstring has the numbers); so beat 5 is cut on
      "so": pt05_boots ("He wore golden boots,") and this shot, the brothers' look, from the BOOTS' POINT OF VIEW: a
      lens at boot height (z 0.3) on the floor 1.8 block east of the boot mark, looking up at the three piglins at the
      gold; they turn from the gold and tip their heads down INTO the lens (from the boot mark itself gold_2 and
      gold_3 stand on one line and gold_1 falls outside x 82 %: the lead's geo).

    MUST BE SEEN, ON WHICH WORD
      frame 322       the three at the gold, their backs / sides to the lens, facing the gold wall (as pt05 left
                      them), something moving (the ears, a drift)
      "brothers" 333  they turn from the gold, a beat apart (a body turn of 9 frames, heads following)
      "thought he was" 343-353   held: three faces tipped down at the lens (the boots), sharp
      "family" 354 .. 378   they turn back to the gold, satisfied (by about 370; nothing new in the last 3 frames)
    SHARED: PLACES gold_1..3 (pt05 has them there), gold_target.
    NOW (stub): FAMILY (28 mm f/2.8 at (5.35, 5.7, 0.3) aimed at (7.25, 10.9, 1.5)); piglin_rw3 / rw4 / xbow_rw5 at
      gold_1..3 looking at the gold, ears flopping; from "brothers" - 2 (+3 frames each) Character.face(lens, 9
      frames, keep_head) then look_at(lens, 5 frames); on "family" (+3 each) a turn back to their places' yaw and the
      head back to the gold over 10 frames. Focus on the near one (gold_1). Hero: piglin_rw3.
    MEASURED (tools.sixseconds_geo rw05_family:322 / :350 / :376; still out/test/sixseconds_scout_rw05_family_350_
      zones.png; tools.sixseconds_palette 350): on 350 all three faces straight at the lens (0-1 degrees), pitched
      down 11-19 degrees; heads x 50-81 % (gold_1, 103 px), x 13-38 % (gold_2, 83 px), x 30-48 % (gold_3, 62 px,
      behind gold_2's shoulder but its eyes clear), y 36-55 %; on 322 / 376 they face the gold (125-176 degrees off).
      Gold hue 45, piglin skin s 0.60 (limit 0.62), hero 100 % inside the safe area. Their legs stand in the caption
      band (soft; nothing essential there). The lanterns of the gold and the gold wall read at the right.
    NEIGHBOURS: before, pt05_boots (the boots stopped, the brothers soft at the gold beyond); after, pt06_dig (the
      pit camera: he digs where he stopped).
    """
    f0, f1 = s.frame_start, s.frame_end
    gold = Vector(C.P("gold_target"))
    back = C.at(s, "family")
    pigs = [C.actor("piglin", "rw3"), C.actor("piglin", "rw4"), C.actor("piglin_xbow", "rw5")]
    for k, p in enumerate(pigs):
        C.put(p, f0, "gold_%d" % (k + 1))
        p.look_at(f0, gold, ease=0)                 # as pt05 left them: at the gold, backs to the boots
        p.flop_ears(f0, f1 + 1)
    for k, p in enumerate(pigs):
        g = f0 + FAMILY_TURN[k]
        f = g + FAMILY_TURN_FRAMES
        lens = Vector(FAMILY["pos"]).lerp(Vector(FAMILY["pos1"]), (f - f0) / float(f1 + 1 - f0))
        p.face(g, lens, ease=FAMILY_TURN_FRAMES)    # round to the boots: body and head together (the head re-centres)
        p.look_at(g + FAMILY_TURN_FRAMES - 6, lens, ease=6)    # ... the face tipping down into the lens
        b = back + FAMILY_BACK[k]                   # "family": back to the gold, two frames apart
        p.turn(b, C.yaw("gold_%d" % (k + 1)), ease=FAMILY_BACK_FRAMES)
        p.look_at(b, gold, ease=FAMILY_BACK_FRAMES)
    st.use(s, *pigs)
    C.cam(s, None, focus=pigs[0].head, ease="linear", **FAMILY)
    st.hero(s, "piglin", pigs[0])
    C.lights(s, "home")


def rw21_stare(st, s, C, nar):
    """BEAT 21  "So today I'm staring at an ingot."   frames 1358-1415 (58 f, 2.42 s), sky wastes. THE SIX SECONDS
    START ON 1358. Words (spoken a tenth slower): So 1360, today 1365, I'm 1375, staring 1380, at 1393, an 1396,
    ingot 1399 (ends 1408).

    STORY: Back in the brute's bastion, floor whole, no pit: the ingot row frame from sentence two, side-on at snout
    height. Two brothers each hold an ingot up to his snout. Beside them, 0.7 block clear of the nearest, now stands
    the brute, head tilted down at a single ingot turning on the blackstone step in front of his chest, because he
    cannot pick it up. The golden axe is still in his hand. The six-second stare starts on the first frame of this
    shot.
    Cast: piglin brute, two piglins. Effects: two gold ingots held in the admire pose, one gold ingot as a spinning
    dropped item on the one-block blackstone step, golden axe, ingot row camera preset.

    MUST BE SEEN, ON WHICH WORD
      frame 1358      THE INGOT ROW FRAME again, now with the brute between the brothers, head down: the stare has
                      begun (his head does not move for six seconds: no idle glances; ears only)
      "ingot" 1399    he visibly looks down at something on the step
    SHARED: CAMS["ingot_row"] exactly; PLACES brother_1 / brother_2 / brute_gold / step_ingot.
    KNOWN (the set builder, searched): from this frame his ingot is HIDDEN behind brother 1: no camera spot in the
      courtyard holds the brute, both brothers AND his ingot apart. Accepted: beat 22 reveals it. The near brother
      must not cover the brute's face.
    NOW (stub): exactly that; the ingot is C.memo["rw_ingot"] (one entity turning from here to the end). Hero: the
      brute.
    MEASURED (out/test/sixseconds_set_b21_ingot_row.png): brute x 40-59 %, y 42-50 %, 2.93 x the blackstone.
      THE LEAD'S GEO / STILL (old timeline: rw21_stare:1392 = 1399 here, out/test/sixseconds_scout_rw21_stare_1392_
      zones.png): brute eyes x 51 %, y 45 % (head x 38-61 %, 80 px, 38 degrees off the lens, pitched 24 down: he
      reads as looking down); brother 1 big at the left (head x 4-41 %, its left edge outside x 8 %), brother 2
      x 61-88 %; the step ingot spot behind brother 1's arm (as the set builder found).
    NEIGHBOURS: before, pt20_likes (the older world's pit: everyone likes gold); after, rw22_six.
    """
    b1, _b2 = _brothers(st, s, C)
    _ingot(st, s, C)
    brute = C.actor("brute", "rw")
    C.stand(s, brute, "brute_gold", look="step_ingot", idle=False)     # the stare: ears only, for six seconds
    C.cam(s, "ingot_row", focus=b1.head)              # beat 2's frame as we left it: the near brother sharp ...
    C.rack(s, brute.head, C.at(s, "I'm") - 6, frames=14)   # ... "I'm staring": the focus pulls back to him
    st.hero(s, "brute", brute)
    C.lights(s, "home")


def rw22_six(st, s, C, nar):
    """BEAT 22  "Six seconds."   frames 1416-1501 (86 f, 3.58 s), sky wastes. Words: Six 1418, seconds 1426 (ends
    1441), then 60 frames (2.5 s) of silence to the cut: 1358 + 144 = 1502 is the first frame of rw23.

    STORY: Tight low close-up from below eye height, shallow focus, slow push in: the ingot turning sharp in the
    middle of the frame, the brute's unmoving face just above it, lantern light on his snout. Nothing else in the
    picture. Hold in silence after the words until exactly six seconds (144 frames) have passed since the first
    frame of the previous shot, about three seconds of hold.
    Cast: piglin brute. Effects: gold ingot spinning (sharp), lantern key on the face, slow push in, silent hold
    timed to a real six seconds.

    MUST BE SEEN, ON WHICH WORD
      the whole shot  the ingot sharp in the middle, turning; his whole face above it, unmoving (no idle; the ears
                      may flop: the game does); the push slow and linear to the last frame
      "Six" 1418      the ingot's broad face toward the lens (the stub's phase does it: the lead's stills)
      "seconds" 1426 .. 1501   the silence: nothing changes but the turning ingot and the push
    NOW (stub): INGOT_CLOSE (32 mm f/2 on his line of sight beyond the ingot, at z 2.15, a linear push of 0.1 block),
      focus on the ingot; the brute at brute_gold, head on the ingot. Hero: the brute (the ingot is the sharp
      thing: also name it, st.hero(s, "ingot", ...)).
    THE CHECKS AND THE LEAD'S FIX: from the set's six_ingot_close (z 1.62, 35 mm) the ingot covered his snout and
      tusks on every frame (the technical check; out/test/sixseconds_scout_rw22_six_1490.png: an edge-on gold sliver
      across his snout). The technical check's suggested fix (z 1.75, 0.6 nearer) does NOT separate them (geo: ingot
      top y 35.5 %, his head down to y 39.4 %): on his line of sight the ingot's top (z 1.69, 1.6 from the lens) clears
      his snout (z 1.4, 3.3 from the lens) only for a lens above about z 1.96, or with the lens moved 0.3-0.5 to the
      side. Three variants rendered side by side (out/test/sixseconds_scout_rw22var_rw22_six_1418_v0/v1/v2.png:
      z 1.75 + 0.5 aside, z 2.15 on the line, z 1.95 + 0.3 aside): all three put his face clear above the ingot; the
      stub takes z 2.15 on the line ("the ingot in the middle, his face just above it"; he reads as looking DOWN at
      it), 32 mm so his scalp stays under the top icons' edge and the ingot above the caption band. It is no longer
      "from below eye height" (0.36 above his eyes): the director may take v2 (eye height, the ingot a little left).
    MEASURED (out/test/sixseconds_scout_rw22_six_1418_zones.png, _1500.png; tools.sixseconds_palette 1418): his face
      at y 14-35 % (scalp at the top icons' edge), the ingot broad side at y 38-60 %, sharp, in the middle; brute
      x 3.15 the blackstone; hero 96 % inside the safe area.
    NEIGHBOURS: before, rw21_stare; after, rw23_nothing.
    """
    ingot = _ingot(st, s, C)
    brute = C.actor("brute", "rw")
    C.stand(s, brute, "brute_gold", look="step_ingot", idle=False)
    target = Vector(C.P("step_ingot")) + Vector((0.0, 0.0, 0.3))     # the middle of the bobbing sprite
    C.cam(s, None, focus=target, ease="linear", **INGOT_CLOSE)
    st.hero(s, "brute", brute)
    st.hero(s, "ingot", ingot.sprite)
    C.lights(s, "home")


def rw23_nothing(st, s, C, nar):
    """BEAT 23  "Nothing."   frames 1502-1578 (77 f, 3.21 s), sky wastes. Word: Nothing 1504 (ends 1521); held to
    1570; the encoder's plain cut to black on 1571-1578 (END_BLACK). The film's last image.

    STORY: The gate frame one last time: at the gold wall, his body still to the gold, the brute lifts his head from
    the ingot and turns it to the empty gateway, ending in clean profile with his snout against the glow. The ingot
    still turns at his feet, his brothers stay heads-down over theirs, the gateway where he waited is empty. Hold two
    seconds, then a plain cut to black, not the snap that meant a reset: this world does not end.
    Cast: piglin brute, three piglins. Effects: head lift and turn to profile toward the gateway, gold ingot spinning
    on the step, gate frame camera preset, hold, then plain cut to black.
    FALLBACK TAKEN (the story's own risk: "the head turn toward the far gateway can end as the back of a dark head.
    Fallback: a reverse angle from the gateway, floor level, the empty blackstone in the foreground under the
    caption word and the brute's face lifting toward the lens behind it"): the gate frame cannot give it (from the
    courtyard's south part the gateway lies BEHIND a brute at the gold: out/test/sixseconds_set_b23_gate.png, brute
    x 77-88 %, the back of his head, 1.26 x).

    MUST BE SEEN, ON WHICH WORD
      frame 1502      his head still down at the ingot (the stare's last frame continues), the brothers heads-down
      "Nothing" 1504  his head lifts and turns toward the gateway, i.e. straight into this lens (65 of his 75
                      degrees): a slow turn (about 15-20 frames), then held still to the black
      the whole shot  the brothers heads-down either side of him
    SHARED: PLACES brute_gold / brother_1 / brother_2 / step_ingot / gateway_mouth. REVERSE is this shot's own camera.
    NOW (stub): REVERSE (40 mm f/2.8 at (5.8, 15.0, 0.45) aimed at (7.55, 10.15, 1.35)), the head turn on "Nothing"
      over 18 frames. Hero: the brute.
    THE STORY CHECK AND THE LEAD'S FIX: from the set's six_gate_reverse (8.7 blocks off, 36 mm) his face was 69 px and
      brother 2 crowded his shoulder, and CAMS["reverse"] was listed as SHARED, so the row director could not fix it.
      Now it is this file's own, and moved: ON the line from the brute to gateway_mouth (what he turns to: he ends
      looking straight into the lens), 5.5 blocks from him, between the brothers (the lead's search of the courtyard:
      brother 1 14 degrees to the left, brother 2 13 to the right).
    MEASURED (tools.sixseconds_geo rw23_nothing:1503 / :1535; still out/test/sixseconds_scout_rw23_nothing_1540_
      zones.png; tools.sixseconds_palette 1540): on 1535 his face 122 px, 0 degrees off the lens, level, eyes x 50 %,
      y 42 %, head x 32-68 %, y 36-48.5 %, clear; on 1503 still down at the ingot (38 degrees off, pitched 24 down);
      brute x 2.82 the blackstone, piglin skin s 0.58, hero 100 % inside. Brother 2's head x 66-112 % (right edge,
      clear of his face) but his golden SWORD crosses in front of the brute's chest at y 50-62 %; brother 1 a big soft
      shape at the left edge (head x -43..32 %, y -19..27 %: under the top icons; 2.5 blocks from the lens). His ingot
      is NOT in this frame (behind brother 1, as from any camera near the gateway line). The brute's legs stand in
      the caption band (from this low lens the floor under it is not empty): the director may raise the lens a little
      or accept it ("Nothing" is the only caption, 1504-1521).
    NEIGHBOURS: before, rw22_six; after: the end (the Reel loops to gt01).
    """
    f0, f1 = s.frame_start, s.frame_end
    _brothers(st, s, C)
    _ingot(st, s, C)
    brute = C.actor("brute", "rw")
    C.stand(s, brute, "brute_gold", look="step_ingot", idle=False)    # 1502: the stare's last frame goes on
    lift = C.at(s, "Nothing")
    end = lift + NOTHING_LIFT
    lens = Vector(REVERSE["pos"]).lerp(Vector(REVERSE["pos1"]), min(1.0, (end - f0) / float(f1 + 1 - f0)))
    brute.look_at(lift, lens, ease=NOTHING_LIFT)      # "Nothing": up from the ingot and round, into the lens; held
    C.cam(s, None, focus=brute.head, **REVERSE)
    C.fill("rw_nothing", NOTHING_FILL["pos"], NOTHING_FILL["watts"], [s], color=NOTHING_FILL["color"])
    st.hero(s, "brute", brute)
    C.lights(s, "home")
