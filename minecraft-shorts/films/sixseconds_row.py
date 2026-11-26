"""Six Seconds, sequence ROW: the gold wall. The ingot row of beat 2 and the six-second stare at the end: beats 2, 21,
22, 23 (shots rw02_ingots, rw21_stare, rw22_six, rw23_nothing), sky "wastes". One function per shot; the contract is
in films/sixseconds_common.py (tags "rw...", C.actor, C.cam, C.lights, st.use / st.hero).

STATUS: STUBS by the lead director. Each function puts the shot's camera on its place and its cast roughly where the
story wants them; the docstrings say what the shot must become. Everything may be rewritten except what SHARED names.

THE PLACE (engine/nether.py HOME, films/sixseconds_set.py beats 2 and 21-23): the GOLD WALL, 21 gold blocks in the
east wall's inner face (x 9, y 9..15, z 0..2), basalt-framed, the one-block blackstone STEP in front of it (x 8,
y 9..15, top z 1), two lanterns over the step (group home_gold). The brothers at "brother_1" (7.0, 13.2) and
"brother_2" (6.3, 10.8), the brute at "brute_gold" (7.6, 10.0), all facing north-east (yaw 2.356, the gold
diagonally); his ingot on the step at "step_ingot" (8.16, 11.71, 1.0): in front of his chest, 17 degrees left of
straight ahead, 1.8 away, head pitch 21 (a brute cannot look below 40, nor turn his head more than 75). The
layout exists for rw22 (the only camera spot beyond the ingot on his line of sight) and rw23 (his head reaches the
gateway's mouth at 65 of 75 degrees).
SHARED (films/sixseconds_common.py): CAMS["ingot_row"] in rw02 and rw21 EXACTLY (the frame returns: "the ingot row
  frame"); PLACES brother_1 / brother_2 / brute_gold / step_ingot / brute_turned / gateway_mouth; CAMS["reverse"] for
  rw23 (beat 23's fallback; also the stand-in of a failed row shot is CAMS["ingot_row"]).
THE WORLD'S RULES that bite here: floor whole (no C.pit); the brute 0.7 block or more from either brother; the
  brothers admire with the ingot in the LEFT hand, golden sword in the right (C.admire); the brute keeps the golden
  axe in his hand.
THE SIX SECONDS: rw21 (58 frames) + rw22 (86) = 144 frames exactly from the first frame of rw21 to the cut into rw23
  (films/sixseconds.py asserts it): the stare starts on rw21's first frame and the ingot turns through all three
  shots. The stub keeps ONE ingot entity (C.memo["rw_ingot"]) turning without a break from rw21 to the end.
TAGS TAKEN by the stubs: piglin_rw1, piglin_rw2 (rw02, rw21, rw23), brute_rw (all four), gold_ingot_rw (rw21-rw23).
PREVIEW samples of this sequence: 6.
"""
from mathutils import Vector


def _brothers(st, s, C):
    """The two brothers on their places, admiring (ingot in the left hand at the snout) through the whole shot."""
    b1, b2 = C.actor("piglin", "rw1"), C.actor("piglin", "rw2")
    for b, place in ((b1, "brother_1"), (b2, "brother_2")):
        C.put(b, s.frame_start, place)
        C.admire(s, b)
    st.use(s, b1, b2)
    return b1, b2


def _ingot(st, s, C):
    """The ingot on the step, ONE entity turning from rw21's first frame to the film's end (in this shot)."""
    it = C.memo.get("rw_ingot")
    if it is None:
        it = C.memo["rw_ingot"] = C.item("gold_ingot", "rw")
        f0 = C.T["rw21_stare"].frame_start
        it.place(f0, C.P("step_ingot"))
        it.animate(f0, C.T["rw23_nothing"].frame_end + 1)
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
    b1, _b2 = _brothers(st, s, C)
    brute = C.actor("brute", "rw")
    C.stand(s, brute, "brute_turned", idle=False)
    C.cam(s, "ingot_row", focus=b1.head)
    st.hero(s, "piglin", b1)
    C.lights(s, "home")


def rw21_stare(st, s, C, nar):
    """BEAT 21  "So today I'm staring at an ingot."   frames 1351-1408 (58 f, 2.42 s), sky wastes. THE SIX SECONDS
    START ON 1351. Words (spoken a tenth slower): So 1353, today 1357, I'm 1368, staring 1373, at 1386, an 1389,
    ingot 1392 (ends 1401).

    STORY: Back in the brute's bastion, floor whole, no pit: the ingot row frame from sentence two, side-on at snout
    height. Two brothers each hold an ingot up to his snout. Beside them, 0.7 block clear of the nearest, now stands
    the brute, head tilted down at a single ingot turning on the blackstone step in front of his chest, because he
    cannot pick it up. The golden axe is still in his hand. The six-second stare starts on the first frame of this
    shot.
    Cast: piglin brute, two piglins. Effects: two gold ingots held in the admire pose, one gold ingot as a spinning
    dropped item on the one-block blackstone step, golden axe, ingot row camera preset.

    MUST BE SEEN, ON WHICH WORD
      frame 1351      THE INGOT ROW FRAME again, now with the brute between the brothers, head down: the stare has
                      begun (his head does not move for six seconds: no idle glances; ears only)
      "ingot" 1392    he visibly looks down at something on the step
    SHARED: CAMS["ingot_row"] exactly; PLACES brother_1 / brother_2 / brute_gold / step_ingot.
    KNOWN (the set builder, searched): from this frame his ingot is HIDDEN behind brother 1: no camera spot in the
      courtyard holds the brute, both brothers AND his ingot apart. Accepted: beat 22 reveals it. The near brother
      must not cover the brute's face.
    NOW (stub): exactly that; the ingot is C.memo["rw_ingot"] (one entity turning from here to the end). Hero: the
      brute.
    MEASURED (out/test/sixseconds_set_b21_ingot_row.png): brute x 40-59 %, y 42-50 %, 2.93 x the blackstone.
      THE LEAD'S GEO / STILL (rw21_stare:1392, out/test/sixseconds_scout_rw21_stare_1392_zones.png): brute eyes x 51 %,
      y 45 % (head x 38-61 %, 80 px, 38 degrees off the lens, pitched 24 down: he reads as looking down); brother 1
      big at the left (head x 4-41 %, its left edge outside x 8 %), brother 2 x 61-88 %; the step ingot spot behind
      brother 1's arm (as the set builder found).
    NEIGHBOURS: before, pt20_likes (the older world's pit: everyone likes gold); after, rw22_six.
    """
    _brothers(st, s, C)
    ingot = _ingot(st, s, C)
    brute = C.actor("brute", "rw")
    C.stand(s, brute, "brute_gold", look="step_ingot", idle=False)
    C.cam(s, "ingot_row", focus=brute.head)
    st.hero(s, "brute", brute)
    C.memo["rw_ingot"] = ingot
    C.lights(s, "home")


def rw22_six(st, s, C, nar):
    """BEAT 22  "Six seconds."   frames 1409-1494 (86 f, 3.58 s), sky wastes. Words: Six 1411, seconds 1419 (ends
    1434), then 60 frames (2.5 s) of silence to the cut: 1351 + 144 = 1495 is the first frame of rw23.

    STORY: Tight low close-up from below eye height, shallow focus, slow push in: the ingot turning sharp in the
    middle of the frame, the brute's unmoving face just above it, lantern light on his snout. Nothing else in the
    picture. Hold in silence after the words until exactly six seconds (144 frames) have passed since the first
    frame of the previous shot, about three seconds of hold.
    Cast: piglin brute. Effects: gold ingot spinning (sharp), lantern key on the face, slow push in, silent hold
    timed to a real six seconds.

    MUST BE SEEN, ON WHICH WORD
      the whole shot  the ingot sharp in the middle, turning; his whole face above it, unmoving (no idle; the ears
                      may flop: the game does); the push slow and linear to the last frame
      "seconds" 1419 .. 1494   the silence: nothing changes but the turning ingot and the push
    NOW (stub): the set's six_ingot_close (35 mm f/2 on the step beyond the ingot, on his line of sight, below his
      eye height, a slow push to its pos1), focus on the ingot; the brute at brute_gold, head on the ingot. Hero:
      the brute (the ingot is the sharp thing: also name it, st.hero(s, "ingot", *ingot objects)).
    MEASURED (out/test/sixseconds_set_b22_ingot_close.png): ingot y 44-58 %, his face (eyes, snout, tusks) above
      it at x 35-66 %, y 28-45 %, 3.16 x the blackstone, the gold lantern on his snout; the brothers out of frame.
      THE LEAD'S SCOUTING of the stub (out/test/sixseconds_scout_rw22_six_1420.png, _1490.png, 540x960, 16 samples):
      the ingot is SHARP (its pixel edges crisp at 2x) and his face soft behind it, as the story asks; a dropped item
      turns about the vertical, so on some frames it is three-quarter or edge-on (1420: a narrow gold sliver at x
      44-55 %): that is the game's look, but put a broad face of it on "Six" (1411) and on the shot's last second if
      you can (the spin's phase: engine.mobs DroppedItem.place(frame, pos, age=) / animate(f0, f1, phase=); the
      stub's one ingot is placed in _ingot() on rw21's first frame and turns without a break to the end). Its lower edge sits at y 60-62 % (geo:
      the step point (8.16, 11.71, 1.1) at y 61-62 %), right on the top of the caption band where "Six" and
      "seconds" are drawn: aim the camera a little lower (target z -0.05..-0.1) so the ingot sits at y 42-57 %.
      His face 148-152 px, straight at the lens (0 degrees), head pitched 24 degrees down at the step.
    NEIGHBOURS: before, rw21_stare; after, rw23_nothing.
    """
    ingot = _ingot(st, s, C)
    brute = C.actor("brute", "rw")
    C.stand(s, brute, "brute_gold", look="step_ingot", idle=False)
    target = Vector(C.P("step_ingot")) + Vector((0.0, 0.0, 0.15))
    C.cam(s, "set:six_ingot_close", focus=target, ease="linear")
    st.hero(s, "brute", brute)
    C.lights(s, "home")


def rw23_nothing(st, s, C, nar):
    """BEAT 23  "Nothing."   frames 1495-1571 (77 f, 3.21 s), sky wastes. Word: Nothing 1497 (ends 1514); held to
    1563; the encoder's plain cut to black on 1564-1571 (END_BLACK). The film's last image.

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
    x 77-88 %, the back of his head, 1.26 x). CAMS["reverse"] = the set's six_gate_reverse.

    MUST BE SEEN, ON WHICH WORD
      frame 1495      his head still down at the ingot (the stare's last frame continues), the brothers heads-down
      "Nothing" 1497  his head lifts and turns toward the gateway, i.e. nearly into this lens (65 of his 75 degrees):
                      a slow turn (about 15-20 frames), then held still to the black
      the whole shot  the empty blackstone floor under the caption band; the ingot turning on the step beside him
    SHARED: CAMS["reverse"]; PLACES brute_gold / brother_1 / brother_2 / step_ingot / gateway_mouth.
    NOW (stub): exactly that, the head turn on "Nothing" over 18 frames. Hero: the brute.
    MEASURED (out/test/sixseconds_set_b23_gate_reverse.png): his head at the end of the turn x 40-53 %, y 43-48 %,
      2.69 x the blackstone; brother 2 heads-down beside him, brother 1 soft at the left edge.
      THE LEAD'S GEO / STILL of the stub (rw23_nothing:1500 / :1530, out/test/sixseconds_scout_rw23_nothing_1530.png):
      on 1500 his head 44 degrees off the lens, pitched 22 down (still on the ingot); by 1530 the turn is done: 9
      degrees off the lens, level, eyes x 46 %, y 45 %, face 69 px (8.7 blocks off: small; a longer lens or a closer
      camera on the same line would make the face read bigger at phone size; check it at 360x640). Brother 1 soft at
      the left edge (head x -3..23 %), brother 2 at x 51-73 %, heads-down. The floor under the caption is empty.
    NEIGHBOURS: before, rw22_six; after: the end (the Reel loops to gt01).
    """
    _brothers(st, s, C)
    _ingot(st, s, C)
    brute = C.actor("brute", "rw")
    C.stand(s, brute, "brute_gold", look="step_ingot", idle=False)
    brute.look_at(C.at(s, "Nothing"), Vector(C.P("gateway_mouth")), ease=18)
    C.cam(s, "reverse", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "home")
