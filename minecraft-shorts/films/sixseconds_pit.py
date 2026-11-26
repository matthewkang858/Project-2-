"""Six Seconds, sequence PIT: the runner's trap. The golden boots, the pit, the barter, the gravel, the axe, the smoke,
and the older world's pit: beats 5, 6, 7, 8, 9, 10, 20 (shots pt05_boots, pt06_dig, pt07_pearl, pt08_gravel,
pt09_axe, pt10_smoke, pt20_likes), sky "wastes". One function per shot; the contract is in
films/sixseconds_common.py (tags "pt...", C.actor, C.item, C.cam, C.lights, C.pit, st.use / st.hero).

STATUS: STUBS by the lead director. Each function puts the shot's camera on its place and its cast roughly where the
story wants them (the stub's runner sprints in and the piglins drop: the rest is still); the docstrings say what
each shot must become. Everything may be rewritten except what SHARED names.

THE PLACE (engine/nether.py HOME, THE PIT): the pit's cells x 4..5, y 6..7, two deep (floor z -2), in a patch of
plain blackstone (x 1..7, y 2..9: never gilded, never gold). Its eight blocks are engine.breaking Breakables
(C.bas.pit_blocks); C.pit(s) digs it for one shot (and keys its 9 W fill on), C.pit(s, keep_last=True) leaves the
last block (C.bas.pit_last, cell (4, 6, -2)) for the runner to break on camera. Physics: world=C.bas sees the pit
dug; in pt05 (floor whole) pass world=C.bas.whole. Anchors: home_rim_w (3.6, 7) the runner at the west rim facing
the pit; home_strike (2.35, 7) the brute behind him; home_pit_1..4 the pit floor's four places; home_pit_approach_k
/ home_pit_drop_k and C.bas.pit_drop(piglins, f) (each steps off 14 frames after its start and lands 9 later: f+23,
+35, +47); home_boot_mark (3.65, 6.75) the skid; six_pit_lure, six_pearl_rest, six_gravel_1..7, six_drop_*.
Lanterns: LIGHTS "pit" (home_pit x 2) in every pit shot; pt05 "home".
SHARED (films/sixseconds_common.py): CAMS["pit"] in pt06 and pt20 EXACTLY; CAMS["boot"] for pt05 with BOOT_FRAME
  (br11 on the bridge repeats this framing: keep the skid ON boot_mark and the boots where BOOT_FRAME says); PLACES
  "gold_1".."gold_3" (pt05's piglins start at the gold, as the gate frame has them), "boot_mark", "rim_w", "strike",
  "pit_lure", "pearl_rest".
THE WORLD'S RULES that bite here: THE PIT only in pt06 (last block kept, broken on camera), pt07-pt10, pt20 (C.pit
  refuses elsewhere: pt05's floor is WHOLE); NO BRUTE in pt20 (the side of its frame where he walked in in pt09 stays
  empty); the runner wears the golden boots in every shot; a piglin admires with the ingot in its LEFT hand
  (C.admire); the pearl is never the answer to the ingot thrown in pt07 (the story: "the pearl comes from one who has
  been staring since the previous shot"); the runner's death is the white puff (C.puff), never a body.
ENGINE NOTES (engine/piglins.py, players.py, breaking.py): piglins.barter(lob=True, toward=<a Character>) keys the
  result floating over the OPEN pit (the rest spot 0.45 from his feet lies over it): pass an explicit floor point as
  toward (six_pearl_rest, six_gravel_k: all west of the pit's edge, x <= 3.85). A brute's swing: Piglin.attack(f)
  (7.2 frames, lowest at +3.6), damage on f: runner.hurt(f, from_point=..., knockback=...). home_strike is due WEST
  of home_rim_w: a full knock-back (1.99 blocks) throws the runner EAST over the open pit: use a small knockback or
  cut on the knock-back, as the story asks. breaking.mine(runner, C.bas.pit_last, f, camera=s) (iron pickaxe on
  blackstone: 7 ticks).
TAGS TAKEN by the stubs: runner_pt (pt05-pt10, pt20), piglin_pt1 / piglin_pt2 / piglin_xbow_pt3 (pt05-pt07, pt09,
  pt10), piglin_pt4 (pt20), brute_pt (pt09, pt10), gold_ingot_pt1 (pt06), ender_pearl_pt7 / _pt8 / _pt10 / _pt20,
  gravel_pt8_1..7 / pt10 / pt20_k, golden_boots_pt10, iron_pickaxe_pt10.
PREVIEW samples of this sequence: 7.
"""
from mathutils import Vector

from engine import breaking

PIGS = (("piglin", "pt1"), ("piglin", "pt2"), ("piglin_xbow", "pt3"))


def _pigs(C):
    """The three piglins of the trap (the third with a crossbow)."""
    return [C.actor(role, tag) for role, tag in PIGS]


def _in_pit(st, s, C, pigs, places=(2, 3, 4), yaw=None):
    """Piglins standing on the pit floor (home_pit_k), facing west (toward the rim where the runner is), admiring
    their ingots through the whole shot."""
    west = C.Y.get("home_rim_e", -1.571) if yaw is None else yaw
    for p, k in zip(pigs, places):
        C.put(p, s.frame_start, "home_pit_%d" % k, yaw=west)
        C.admire(s, p)
    st.use(s, *pigs)


def pt05_boots(st, s, C, nar):
    """BEAT 5  "He wore golden boots, so my brothers thought he was family."   frames 282-378 (97 f, 4.04 s), sky
    wastes. Words: He 284, wore 287, golden 295, boots 307, so 324, my 328, brothers 333, thought 343, he 348,
    was 350, family 354 (ends 366).

    STORY: The boot shot (returns on the bridge): camera on the blackstone floor, long lens, looking across the
    courtyard at the gold wall. The legs sprint in from the gateway side and skid to a stop with the golden boots
    bright in the middle of the frame, above the caption band. Behind them three piglins turn from the gold, tip their
    heads down at the boots, hold, then turn back to the gold. Rack focus from the boots to the piglins and back so
    the look at the boots is sharp.
    Cast: the player (legs and boots), three piglins. Effects: golden boots keyed by a warm-white lantern, piglins
    holding golden swords and a crossbow, skid stop, rack focus, floor-level boot shot camera preset re-used in
    sentence eleven.

    MUST BE SEEN, ON WHICH WORD
      frame 282       the legs already sprinting (runner_pt is pre-rolled: he is not in gt04, runner_gt is)
      "golden boots" 295-318   the skid: boots stopped, bright, mid-frame (BOOT_FRAME), above the caption band
      "brothers thought" 333-348   the rack focus to the piglins: they have turned from the gold, heads tipped down
                      at the boots (head pitch at most 40)
      "family" 354 .. 378   back to the boots; the piglins turn back to the gold
    SHARED: CAMS["boot"] exactly, BOOT_FRAME (br11 repeats it); PLACES "boot_mark", "gold_1".."gold_3".
    RISKS (story): golden boots in orange lava light turn the colour of everything else: "light the boots with a
      warm-white lantern, keep the blackstone behind them at half brightness, hold the first boot shot half a second
      longer" (the pause after this line was opened to 0.6 s for it). A film-local warm-white fill on the boots is
      C.fill("pt_boots", ...) (measure gold hue 38-58 with nether.check_still).
    NOW (stub): the boot camera; the runner sprinting in from (4.5, 13) (pre-rolled 12 frames) and stopping on
      boot_mark facing south; the three piglins at the gold looking at the boot mark. Hero: the boots.
    MEASURED (out/test/sixseconds_set_b05_boot.png; the lead's projection): boots x 28-69 %, y 40-57 %; piglin heads
      at 19-25 % (the legs hide one); gold reads as gold.
    NEIGHBOURS: before, gt04_runin (he sprints at the lens through the gateway); after, pt06_dig (the pit camera).
    """
    f0 = s.frame_start
    runner = C.actor("runner", "pt")
    mark = C.P("boot_mark")
    a = (4.5, 13.0, 0.0)
    fs = f0 - 12
    C.put(runner, fs, a, toward=mark)
    runner.walk(fs, [a, (4.3, 10.0, 0.0), mark], sprint=True, ramp=(False, True))
    st.use(s, runner)
    for k, p in enumerate(_pigs(C), 1):
        C.stand(s, p, "gold_%d" % k, look="boot_mark", seed=k)
    C.cam(s, "boot", focus=Vector(mark) + Vector((0.0, 0.0, 0.2)))
    st.hero(s, "boots", *C.boots_of(runner))
    C.lights(s, "home")


def pt06_dig(st, s, C, nar):
    """BEAT 6  "He dug a hole, and they fell in."   frames 379-435 (57 f, 2.38 s), sky wastes.
    Words: He 381, dug 384, a 390, hole 391, and 403, they 406, fell 409, in 416 (ends 422).

    STORY: High three-quarter angle on the courtyard: the player breaks the last block of a pit two blocks deep and
    two wide, with cracks and crumbs. The pit is in plain blackstone, never gilded blackstone or gold. A gold ingot is
    already spinning at the bottom. Three piglins walk to it, step off the rim one after another, 0.7 block and a
    beat apart, and drop in.
    Cast: the player, three piglins. Effects: iron pickaxe swing, block breaking with cracks and blackstone crumbs,
    gold ingot (dropped, spinning) as the lure, piglins stepping off the rim and dropping, staggered, pit camera
    preset re-used in sentence twenty.

    MUST BE SEEN, ON WHICH WORD
      "dug" 384 .. "hole" 391   the last block cracks and breaks (crumbs), the lure ingot spinning on the pit floor
      "they fell in" 406-422   the three piglins step off the rim a beat apart and drop; the third lands by 426,
                      at least 3 frames before the cut (436)
    SHARED: CAMS["pit"] exactly (pt20 repeats it); PLACES "rim_w", "pit_lure" (NOT home_pit_1: inside the kept
      block).
    NOW (stub): C.pit(s, keep_last=True); the runner at rim_w breaking C.bas.pit_last from f0 + 2 (breaking.mine:
      7 ticks with the iron pickaxe); the lure on pit_lure; C.bas.pit_drop(the three, f0): they land on f0 + 23 / 35
      / 47 = 402 / 414 / 426. Hero: the runner.
    MEASURED (out/test/sixseconds_set_b06_pit.png): runner x 15-34 %, y 36-46 %; the piglins at the approach
      points; the lure on the pit floor.
    NEIGHBOURS: before, pt05_boots; after, pt07_pearl (over his shoulder into the pit).
    """
    f0 = s.frame_start
    C.pit(s, keep_last=True)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(C.bas.pit_last.center), ease=0)
    breaking.mine(runner, C.bas.pit_last, f0 + 2, camera=s)
    st.use(s, runner)
    C.rest(s, "gold_ingot", "pt1", "pit_lure")
    pigs = _pigs(C)
    C.bas.pit_drop(pigs, f0)
    st.use(s, *pigs)
    C.cam(s, "pit")
    st.hero(s, "runner", runner)
    C.lights(s, "pit")


def pt07_pearl(st, s, C, nar):
    """BEAT 7  "He threw gold, and they threw back ender pearls."   frames 436-510 (75 f, 3.12 s), sky wastes.
    Words: He 438, threw 441, gold 447, and 465, they 468, threw 471, back 477, ender 484, pearls 489 (ends 505).

    STORY: From behind and above the player's shoulder at the rim, third person, looking down into the pit: all three
    piglins already stand frozen, each with an ingot held up in front of his snout. The player tosses one more ingot
    down. A piglin who has been staring since the last shot lowers his hand, and an ender pearl pops up out of the pit
    and lands spinning beside the golden boots. The pearl is never the answer to the ingot thrown in this shot.
    Cast: the player (shoulder, arm, boots), three piglins in the pit. Effects: gold ingot tossed down (item arc),
    three ingots in the admire pose, ender pearl popping up and landing as a spinning item, golden boots.

    MUST BE SEEN, ON WHICH WORD
      frame 436       the three already frozen with their ingots (admire from the first frame)
      "threw gold" 441-459   his toss (Player.throw / swing; the ingot's arc: piglins.throw_item into the pit)
      "threw back" 471-484   one piglin's pose ends (stop_admiring or its admire running out) and the pearl is lobbed
      "pearls" 489    the pearl lands spinning beside his boots: on PLACES "pearl_rest" (an explicit floor point:
                      piglins.barter(lob=True, toward=C.P("pearl_rest")) or piglins.launch with lob_velocity)
    NOW (stub): the set's six_over_pit (26 mm f/4 behind and above his right shoulder, down into the open pit), the
      pit dug, the runner at rim_w with a gold ingot in his hand, the three admiring on home_pit_2..4 facing west, the
      pearl already lying on pearl_rest. Hero: a piglin.
    MEASURED (out/test/sixseconds_set_b07_over_pit.png): piglins x 58-80 %, y 40-53 %; his shoulder and head at the
      left edge; the pearl at y ~55 % (just above the caption band).
    NEIGHBOURS: before, pt06_dig; after, pt08_gravel (the boots at the rim).
    """
    f0 = s.frame_start
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(C.P("home_pit_center")), ease=0)
    runner.hold("gold_ingot", frame=f0)
    st.use(s, runner)
    pigs = _pigs(C)
    _in_pit(st, s, C, pigs)
    C.rest(s, "ender_pearl", "pt7", "pearl_rest")
    C.cam(s, "set:six_over_pit", focus=pigs[1].head)
    st.hero(s, "piglin", pigs[1])
    C.lights(s, "pit")


def pt08_gravel(st, s, C, nar):
    """BEAT 8  "Mostly gravel."   frames 511-559 (49 f, 2.04 s), sky wastes. Words: Mostly 513, gravel 526 (ends 540:
    19 frames of hold).

    STORY: Close on the golden boots at the rim of the pit: gravel pops out of the hole piece after piece and piles up
    around his feet, bobbing and spinning, with one lonely ender pearl among it. Boots and pile sit between 14 and 60
    percent of the frame height. Hold a full beat after the words.
    Cast: the player (boots only). Effects: six to eight gravel items popping up (block items, small cubes), one ender
    pearl item, lantern light on the pile, hold after the line.

    MUST BE SEEN, ON WHICH WORD
      frame 511       a piece of gravel already in the air (a lob started before the shot: frame - 8, as a flash
                      cut's puff; or the first one landing)
      "Mostly" 513 .. "gravel" 526   piece after piece lands round his boots on six_gravel_1..7 (explicit floor
                      points; piglins.barter(lob=True, toward=point) or piglins.launch), beat 7's pearl among them
      to 559          the pile bobbing and turning; nothing else moves (the boots still)
    NOW (stub): the set's six_boots_rim (40 mm f/2.8 low on the floor south-west of the boots), the pit dug, the
      runner at rim_w, seven gravel items and the pearl already lying there. Hero: the boots.
    MEASURED (out/test/sixseconds_set_b08_boots_rim.png): boots x 31-70 %, y 38-54 %; gravel reads as grey cubes on
      blackstone (the story's gilded-rim fallback was NOT needed).
    NEIGHBOURS: before, pt07_pearl; after, pt09_axe (the brute strides in behind him).
    """
    f0 = s.frame_start
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(C.P("home_pit_center")), ease=0)
    st.use(s, runner)
    for k in range(1, 8):
        C.rest(s, "gravel", "pt8_%d" % k, "six_gravel_%d" % k)
    C.rest(s, "ender_pearl", "pt8", "pearl_rest")
    C.cam(s, "set:six_boots_rim", focus=Vector(C.P("rim_w")) + Vector((0.0, 0.0, 0.15)))
    st.hero(s, "boots", *C.boots_of(runner))
    C.lights(s, "pit")


def pt09_axe(st, s, C, nar):
    """BEAT 9  "I hit him with my axe."   frames 560-596 (37 f, 1.54 s), sky wastes. Words: I 562, hit 565, him 568,
    with 571, my 575, axe 580 (ends 593).

    STORY: Side-on medium at the rim: the brute strides into frame behind the player and swings the golden axe once.
    The player flashes red and is knocked back off his feet. Cut on the knock-back. The only full swing in the film.
    Cast: piglin brute, the player. Effects: golden axe swing, red hurt flash, knock-back, gravel pile at the rim.

    MUST BE SEEN, ON WHICH WORD
      frame 560       the brute already striding in from the left (a twin pre-rolled, or brute_pt placed at the
                      frame edge and walking: he is in no shot before)
      "hit" 565 .. "axe" 580   ONE swing (Piglin.attack: the axe high, down, lowest 3.6 frames in) and the runner's
                      red flash + knock-back on the blow (runner.hurt(f, from_point=brute, knockback=small: the
                      full one throws him over the open pit, see ENGINE NOTES); the cut while he is in the air
      the whole shot  the gravel pile at his feet; the pit piglins still admiring
    NOW (stub): the set's six_rim_side (35 mm f/3 from the south), the pit dug, the runner at rim_w facing the pit,
      the brute at strike with the axe up (aggro), the three admiring in the pit, the gravel. Hero: the brute.
    MEASURED (out/test/sixseconds_set_b09_rim_side.png): brute x 23-38 %, 2.62 x the blackstone, the runner in
      profile, the gateway glow beyond; pit piglin skin saturation 0.62 (AT the limit).
    NEIGHBOURS: before, pt08_gravel; after, pt10_smoke (the same angle, a little wider).
    """
    f0 = s.frame_start
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(C.P("home_pit_center")), ease=0)
    st.use(s, runner)
    brute = C.actor("brute", "pt")
    C.stand(s, brute, "strike", look=runner, idle=False)
    brute.aggro(f0)
    _in_pit(st, s, C, _pigs(C))
    for k in (1, 3, 5):
        C.rest(s, "gravel", "pt9_%d" % k, "six_gravel_%d" % k)
    C.cam(s, "set:six_rim_side", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "pit")


def pt10_smoke(st, s, C, nar):
    """BEAT 10  "He turned into smoke, and the whole world ended."   frames 597-667 (71 f, 2.96 s), sky wastes.
    Words: He 599, turned 601, into 609, smoke 614, and 632, the 635, whole 637, world 645, ended 655. THE RESET:
    from 655 to 667 the encoder shows BLACK with the caption "ended" held on it (films/sixseconds.py RESETS): nothing
    after 654 is seen.

    STORY: Same angle, a little wider. The brute's axe is just coming down to rest from a second blow we did not see.
    A white puff where the player was. Gravel, the iron pickaxe, the golden boots and one ender pearl scatter and spin
    on the blackstone. In the pit the piglins are still looking at their ingots. On the word ended the picture snaps
    to black and the caption word stays on the black for half a second.
    Cast: piglin brute, three piglins in the pit, the player (vanishing). Effects: axe lowering (tail of a second
    blow), white smoke puff, dropped items: gravel, iron pickaxe, golden boots, ender pearl, snap to black (the
    picture for a reset), caption held on black.

    MUST BE SEEN, ON WHICH WORD
      frame 597       the axe coming down to rest (the tail of the second blow: aggro on, then lowered) and the puff
                      already rising where he was (C.puff(s, "rim_w", f0 - 6): puffs in the air on the first frame)
      "smoke" 614     the drops scattering (mobs DroppedItem.drop with a small velocity, from rim_w) and spinning
      to 654          the piglins still heads-down over their ingots
    RISK (story): "players know a brute needs two hits ... if it reads as a one-hit kill in the preview: put a
      second red flash on the first two frames of sentence ten before the puff".
    NOW (stub): the set's six_rim_wide (28 mm f/3.2, the same place as pt09), the pit dug, the brute at strike, the
      puff, the drops lying on six_drop_boots / _pickaxe / _gravel / _pearl, the three admiring. Hero: the brute.
    MEASURED (out/test/sixseconds_set_b10_rim_wide.png): brute x 23-40 %, y 36-45 %, 2.79 x the blackstone; the puff
      at rim_w; the pit piglins low at the right.
    NEIGHBOURS: before, pt09_axe; after (out of black), br11_boots on the bridge of another world.
    """
    f0 = s.frame_start
    C.pit(s)
    brute = C.actor("brute", "pt")
    C.stand(s, brute, "strike", look="rim_w", idle=False)
    C.puff(s, "rim_w", f0 - 6, seed=10)
    for item, where in (("golden_boots", "six_drop_boots"), ("iron_pickaxe", "six_drop_pickaxe"),
                        ("gravel", "six_drop_gravel"), ("ender_pearl", "six_drop_pearl")):
        C.rest(s, item, "pt10", where)
    _in_pit(st, s, C, _pigs(C))
    C.cam(s, "set:six_rim_wide", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "pit")


def pt20_likes(st, s, C, nar):
    """BEAT 20  "In that bastion, everyone likes gold."   frames 1283-1350 (68 f, 2.83 s), sky wastes.
    Words: In 1285, that 1287, bastion 1292, everyone 1311, likes 1321, gold 1327 (ends 1339).

    STORY: High shot over the pit, the camera of sentence six: four piglins each hold an ingot up and stare at it. The
    player stands on the rim, unhurried, ender pearls and gravel popping up around his golden boots. The side of the
    frame where the brute walked in for sentence nine stays empty.
    Location: the older version of the world (the home set, no brute). Cast: the player, four piglins in the pit.
    Effects: four gold ingots in the admire pose, ender pearls and gravel popping out of the pit, golden boots,
    deliberately empty space behind the player.

    MUST BE SEEN, ON WHICH WORD
      frame 1283      four piglins frozen over their ingots; a pearl or gravel already in the air
      "everyone likes gold" 1311-1339   pearls and gravel landing round his boots on explicit floor points (see
                      ENGINE NOTES); he stands at ease (an idle, a glance down)
      the whole shot  the brute's side of the frame (west of the rim, toward home_strike) EMPTY
    SHARED: CAMS["pit"] exactly (= pt06); PLACES "rim_w".
    THE WORLD'S RULES: NO BRUTE (NO_BRUTE_SHOTS); the pit dug (C.pit).
    NOW (stub): the pit camera, the pit dug, four piglins admiring on home_pit_1..4, the runner at rim_w, three gravel
      and a pearl lying at his feet. Hero: a piglin.
    MEASURED (out/test/sixseconds_set_b20_pit.png): four piglins admiring in the pit, the runner at the rim.
    NEIGHBOURS: before, gt19_older (the match cut: the runner sprinted through the brute's spot); after, rw21_stare.
    """
    f0 = s.frame_start
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(C.P("home_pit_center")), ease=0)
    st.use(s, runner)
    pigs = _pigs(C) + [C.actor("piglin", "pt4")]
    south = C.Y.get("home_rim_n", 0.0)
    for p, k in zip(pigs, (2, 4, 1, 3)):
        C.put(p, f0, "home_pit_%d" % k, yaw=C.Y.get("home_rim_e", -1.571) if k in (2, 4) else south)
        C.admire(s, p)
    st.use(s, *pigs)
    for k in (1, 3, 5):
        C.rest(s, "gravel", "pt20_%d" % k, "six_gravel_%d" % k)
    C.rest(s, "ender_pearl", "pt20", "pearl_rest")
    C.cam(s, "pit")
    st.hero(s, "piglin", pigs[0])
    C.lights(s, "pit")
