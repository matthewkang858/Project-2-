"""Six Seconds, sequence PIT: the runner's trap. The golden boots, the pit, the barter, the gravel, the axe, the smoke,
and the older world's pit: beats 5, 6, 7, 8, 9, 10, 20 (shots pt05_boots, pt06_dig, pt07_pearl, pt08_gravel,
pt09_axe, pt10_smoke, pt20_likes), sky "wastes". One function per shot; the contract is in
films/sixseconds_common.py (tags "pt...", C.actor, C.item, C.cam, C.lights, C.pit, st.use / st.hero).

STATUS: STUBS by the lead director, revised in the lead's review pass (two independent checks). Each function puts
the shot's camera on its place and its cast roughly where the story wants them (the runner sprints in, the last
block breaks, the piglins drop, the pearl and the gravel are lobbed, the brute strides in and swings once); the
docstrings say what each shot must become. Everything may be rewritten except what SHARED names.
BEAT 5 IS TWO SHOTS (the lead's decision after the technical check): pt05_boots here ("He wore golden boots,") and
rw05_family in the ROW sequence ("so my brothers thought he was family": the brothers turn from the gold to the
boots, from the boots' height). From the boot framing's lens the runner's torso and arms cover x 17-83 % at the
height of the piglins' heads wherever they stand, so the story's rack focus to them had no picture.

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
  "gold_1".."gold_3" (pt05's piglins stand at the gold, as the gate frame and rw05 have them), "boot_mark" (rw05 is
  the boots' point of view from beside it), "rim_w", "strike", "pit_lure", "pearl_rest".
THE WORLD'S RULES that bite here: THE PIT only in pt06 (last block kept, broken on camera), pt07-pt10, pt20 (C.pit
  refuses elsewhere: pt05's floor is WHOLE); NO BRUTE in pt20 (the side of its frame where he walked in in pt09 stays
  empty); the runner wears the golden boots in every shot; a piglin admires with the ingot in its LEFT hand
  (C.admire); the pearl is never the answer to the ingot thrown in pt07 (the story: "the pearl comes from one who has
  been staring since the previous shot"); the runner's death is the white puff (C.puff), never a body.
ENGINE NOTES (engine/piglins.py, players.py, breaking.py): piglins.barter(lob=True, toward=<a Character>) keys the
  result floating over the OPEN pit (the rest spot 0.45 from his feet lies over it): pass an explicit floor point as
  toward (six_pearl_rest, six_gravel_k: all west of the pit's edge, x <= 3.85), and a C.item(...) as the result,
  never an item id (ENGINE SIDE DOORS in films/sixseconds_common.py). piglins.launch(item, f, start,
  piglins.lob_velocity(start, point, world=C.bas), world=C.bas) lobs an item out of the pit to a floor point (the
  stub's pearl and gravel: 21-24 frames of flight). A brute's swing: Piglin.attack(f) (7.2 frames, the axe lowest at
  +3.6); the game deals the damage on the swing's FIRST tick: runner.hurt(f, from_point=..., knockback=...)
  (Player.hurt has no max_back). home_strike is due WEST of home_rim_w: a full knock-back (0.4: 1.99 blocks, 12
  frames in the air) throws the runner EAST over the open pit; 0.25 flies him 0.9 block in 8 frames.
  breaking.mine(runner, C.bas.pit_last, f, camera=s, drop=None) (iron pickaxe on blackstone: 7 ticks; drop='auto',
  its default, leaves a blackstone item in the pit for the rest of the film: the technical check).
TAGS TAKEN by the stubs: runner_pt (pt05-pt09, pt20), piglin_pt1 / piglin_pt2 / piglin_xbow_pt3 (pt05-pt07, pt09,
  pt10, pt20), piglin_pt4 (pt20), brute_pt (pt09, pt10), gold_ingot_pt1 (pt06), ender_pearl_pt7 (pt07 AND pt08:
  C.memo["pt_pearl"]), ender_pearl_pt10 / _pt20, gravel_pt8_1..7 / pt9_k / pt10 / pt20_k, golden_boots_pt10,
  iron_pickaxe_pt10.
PREVIEW samples of this sequence: 7.
"""
from mathutils import Vector

from engine import breaking, piglins

PIGS = (("piglin", "pt1"), ("piglin", "pt2"), ("piglin_xbow", "pt3"))
# pt07: the frame the pearl is lobbed out of the pit (it lands spinning beside his boots by "pearls")
PEARL_LOB = 466
# pt08: four gravel entities already lying round his boots on 511; three more lobbed out of the pit, one per pit
# piglin (the game: one barter = one item entity of 8-16 gravel, thrown once after a 6-second admire), the first
# already in the air on the shot's first frame: (launch frame, from, stack size)
GRAVEL_LYING = (1, 2, 5, 6)
GRAVEL_LOBBED = (3, 4, 7)
GRAVEL_LOBS = ((497, "home_pit_2", 11), (507, "home_pit_3", 13), (517, "home_pit_4", 8))
# pt09: the brute strides in from the frame's left (pre-rolled), swings on "my" / "axe": the blow lands on PT09_HIT and
# the small knock-back keeps the runner in the air over the rim to the cut (the full 0.4 throws him 2 blocks over
# the open pit)
BRUTE_IN = (0.95, 5.6, 0.0)
PT09_STRIDE_PRE = 6
PT09_SWING, PT09_HIT, PT09_KNOCK = 590, 590, 0.25        # the game deals the damage on the swing's first tick


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
    """BEAT 5 (1 of 2)  "He wore golden boots,"   frames 282-321 (40 f, 1.67 s), sky wastes.
    Words: He 284, wore 287, golden 295, boots 307 (ends 318); the cut into rw05_family is 2 frames before "so" (324).

    STORY: The boot shot (returns on the bridge): camera on the blackstone floor, long lens, looking across the
    courtyard at the gold wall. The legs sprint in from the gateway side and skid to a stop with the golden boots
    bright in the middle of the frame, above the caption band. Behind them three piglins turn from the gold, tip their
    heads down at the boots, hold, then turn back to the gold. Rack focus from the boots to the piglins and back so
    the look at the boots is sharp.
    Cast: the player (legs and boots), three piglins. Effects: golden boots keyed by a warm-white lantern, piglins
    holding golden swords and a crossbow, skid stop, rack focus, floor-level boot shot camera preset re-used in
    sentence eleven.
    THE LEAD'S DECISION (the technical check, confirmed with geo): from this lens (z 0.25, 3.8 blocks from a runner
      facing it) his torso and arms cover x 17-83 % at the height the piglins' heads have (y 16-32 %), wherever they
      stand in the courtyard (on 318 all three are behind his arms: piglin_pt1 behind his left, pt2 and pt3 behind his
      right); they would have to stand 14+ blocks off, beyond the gold wall, to show under his hands. So the piglins'
      look at the boots is the NEXT shot (rw05_family, the row sequence: the three at the gold turn and tip their
      heads down at the boots, from the boots' height) and this shot is the boots alone: the sprint, the skid, the
      boots held still under "golden boots" and after.

    MUST BE SEEN, ON WHICH WORD
      frame 282       the legs already sprinting (runner_pt is pre-rolled: he is not in gt04, runner_gt is)
      "golden boots" 295-318   the skid: boots stopped by about 300, bright, mid-frame (BOOT_FRAME), above the
                      caption band, and held still to the cut (22 frames: br11 holds them about 25)
      the whole shot  the piglins at the gold soft beyond, their backs to him (they have not looked yet)
    SHARED: CAMS["boot"] exactly (its focus is free), BOOT_FRAME (br11 repeats it); PLACES "boot_mark", "gold_1".."3".
    RISKS (story): golden boots in orange lava light turn the colour of everything else: "light the boots with a
      warm-white lantern, keep the blackstone behind them at half brightness, hold the first boot shot half a second
      longer" (the pause after this line was opened to 0.6 s for it). A film-local warm-white fill on the boots is
      C.fill("pt_boots", ...) (measure gold hue 38-58 with nether.check_still).
    NOW (stub): the boot camera; the runner sprinting in from (4.5, 13) (pre-rolled 12 frames, iron pickaxe) and
      stopping on boot_mark facing south; the three piglins at the gold looking at the gold. Hero: the boots.
    MEASURED (the lead; tools.sixseconds_geo pt05_boots:318 --boots runner_pt; the stills
      out/test/sixseconds_scout_boots_pt05_boots_318.png beside _br11_boots_728.png of the first stub;
      tools.sixseconds_palette 318): he enters from the frame's LEFT edge (feet x -13 % on 282, 27 % on 294) and stops
      on boot_mark by 300; boots x 27.7-70.1 %, y 43.1-58.9 % (br11 on 725: 27.7-69.8 %, 42.7-58.6 %: THE BOOT
      FRAMING holds); gold hue 44, s 0.80; piglin skin s 0.59 (limit 0.62); Steve's shirt hue 173. He faces the lens
      when he stops (28 degrees off; br11's runner has his back to it: at boot height it is the same picture).
    NEIGHBOURS: before, gt04_runin (he sprints at the lens through the gateway); after, rw05_family (the brothers
      turn to the boots: the row sequence's camera on the floor by the boot mark).
    """
    f0 = s.frame_start
    runner = C.actor("runner", "pt")
    mark = C.P("boot_mark")
    a = (4.5, 13.0, 0.0)
    fs = f0 - 12
    C.put(runner, fs, a, toward=mark)
    runner.hold("iron_pickaxe", frame=fs)
    runner.walk(fs, [a, (4.3, 10.0, 0.0), mark], sprint=True, ramp=(False, True))
    st.use(s, runner)
    for k, p in enumerate(_pigs(C), 1):        # at the gold, backs to him (rw05 turns them): soft, mostly hidden
        C.stand(s, p, "gold_%d" % k, look="gold_target", seed=k)
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
    NOW (stub): C.pit(s, keep_last=True); the runner at rim_w (iron pickaxe) breaking C.bas.pit_last from f0 + 2
      (breaking.mine with drop=None: 7 ticks; cracks on 381-388, gone on 389); the lure on pit_lure; C.bas.pit_drop
      (the three, f0): they land on f0 + 23 / 35 / 47 = 402 / 414 / 426. Hero: the runner.
    THE TECHNICAL CHECK (confirmed by the lead's probe): with breaking.mine's default drop='auto' the broken block
      left a blackstone ITEM (drop_blackstone) in the pit, unregistered, unhidden on every frame to the film's end
      (in pt20's "older world" pit too). The stub passes drop=None, and build() now stops (strict) or prints "!!!" for
      any dropped item that is not in the Stage's cast (sixseconds_common.unregistered_items).
    MEASURED (out/test/sixseconds_set_b06_pit.png): runner x 15-34 %, y 36-46 %; the piglins at the approach
      points; the lure on the pit floor.
    NEIGHBOURS: before, rw05_family (the brothers at the gold, turned back to it); after, pt07_pearl (over his
      shoulder into the pit).
    """
    f0 = s.frame_start
    C.pit(s, keep_last=True)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(C.bas.pit_last.center), ease=0)
    runner.hold("iron_pickaxe", frame=f0)
    breaking.mine(runner, C.bas.pit_last, f0 + 2, camera=s, drop=None)     # drop=None: see ENGINE SIDE DOORS
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
      "pearls" 489    the pearl lands spinning beside his boots: on PLACES "pearl_rest" (an explicit floor point)
    NOW (stub): the set's six_over_pit (26 mm f/4 behind and above his right shoulder, down into the open pit), the
      pit dug, the runner at rim_w with a gold ingot in his hand, the three admiring on home_pit_2..4 facing west;
      THE PEARL is ONE item entity for pt07 AND pt08 (C.memo["pt_pearl"]: the technical check found two entities on
      one spot, their spin jumping on the cut), lobbed from piglin_pt2's hands (home_pit_3, 1.25 up) on PEARL_LOB 466
      with piglins.launch + lob_velocity to pearl_rest. Hero: a piglin.
    MEASURED (the lead's probe): the pearl rises out of the pit from 466 and lies still on pearl_rest (3.84, 6.54) from
      487, 2 frames before "pearls"; in this frame at x 37.5 %, y 59 % (just above the caption band); from pt08's
      camera it lies at x 83 %, y 53.5 % (at the safe area's right edge). The director moves the lob to "threw back"
      (471-484: launch about 468-471 lands about 489-494) and stages the barter that throws it.
      Earlier (out/test/sixseconds_set_b07_over_pit.png): piglins x 58-80 %, y 40-53 %; his shoulder and head at the
      left edge.
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
    # THE PEARL: ONE item entity from its lob here through pt08 (the technical check: two entities on one spot jump
    # their spin on the cut). The stub lobs it from piglin_pt2's hands in the pit to pearl_rest (piglins.launch with
    # lob_velocity: the lead's cheat for barter(lob=True)); the director stages the barter that throws it.
    pearl = C.memo["pt_pearl"] = C.item("ender_pearl", "pt7")
    start = Vector(C.P("home_pit_3")) + Vector((0.0, 0.0, 1.25))
    lob = PEARL_LOB
    landed = piglins.launch(pearl, lob, start, piglins.lob_velocity(start, C.P("pearl_rest"), world=C.bas),
                            world=C.bas)
    C.memo["pt_pearl_landed"] = landed
    pearl.animate(lob, C.T["pt08_gravel"].frame_end + 1)
    st.use(s, pearl)
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
    MINECRAFT TRUTH (the story check): one barter throws its loot ONCE, after a 119-tick admire (the film's own six
      seconds), and gravel comes as ONE item entity of 8-16 (drawn as 2-3 cubes); three pit piglins give at most three
      throws in this shot. So the pile is mostly ALREADY THERE on the first frame (the barters that came back across
      the time skipped at the cut) and at most one more lands per pit piglin.

    MUST BE SEEN, ON WHICH WORD
      frame 511       four gravel stacks already round his boots, a fifth already in the air
      "Mostly" 513 .. "gravel" 526   the 2nd and 3rd lobs land (one per pit piglin), the pile grows
      to 559          the pile bobbing and turning; nothing else moves (the boots still, pt07's pearl among it)
    NOW (stub): the set's six_boots_rim (40 mm f/2.8 low on the floor south-west of the boots), the pit dug, the
      runner at rim_w (iron pickaxe back in his hand: a hold lasts), gravel stacks of 12 / 9 / 14 / 10 lying on
      six_gravel_1 / 2 / 5 / 6 (C.rest(..., count=)), three more lobbed out of the pit (GRAVEL_LOBS: from home_pit_2 /
      3 / 4 on 497 / 507 / 517, stacks of 11 / 13 / 8) to six_gravel_3 / 4 / 7, pt07's pearl. Hero: the boots.
    MEASURED (the lead's probe): the three lobs come to rest on 518, 524 and 540 (the last on the end of "gravel"),
      then nothing moves to the cut (19 frames); the pearl lies at x 83 %, y 53.5 % in this frame (at the safe area's
      right edge). Earlier (out/test/sixseconds_set_b08_boots_rim.png): boots x 31-70 %, y 38-54 %; gravel reads as
      grey cubes on blackstone (the story's gilded-rim fallback was NOT needed).
    NEIGHBOURS: before, pt07_pearl; after, pt09_axe (the brute strides in behind him).
    """
    f0 = s.frame_start
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(C.P("home_pit_center")), ease=0)
    runner.hold("iron_pickaxe", frame=f0)
    st.use(s, runner)
    # the pile: the barters that came back across the time skipped at the cut already lie there (one entity of 8-16
    # gravel each, as the game throws it), and one more per pit piglin pops out of the hole on the words
    for k, n in zip(GRAVEL_LYING, (12, 9, 14, 10)):
        C.rest(s, "gravel", "pt8_%d" % k, "six_gravel_%d" % k, count=n)
    for k, (fl, src, n) in zip(GRAVEL_LOBBED, GRAVEL_LOBS):
        g = C.item("gravel", "pt8_%d" % k, count=n)
        start = Vector(C.P(src)) + Vector((0.0, 0.0, 1.25))
        piglins.launch(g, fl, start, piglins.lob_velocity(start, C.P("six_gravel_%d" % k), world=C.bas),
                       world=C.bas)
        g.animate(fl, s.frame_end + 1)
        st.use(s, g)
    st.use(s, C.memo["pt_pearl"])               # pt07's pearl, still turning where it landed
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
      frame 560       the brute already striding in from the left (brute_pt is pre-rolled: he is in no shot before)
      "I hit him with my" 562-579   he closes in; the axe goes up (aggro)
      "axe" 580-593   ONE swing and the blow (the game deals the damage on the swing's first tick: runner.hurt on
                      the attack's frame): the red flash and the knock-back, and the CUT WHILE HE IS IN THE AIR
      the whole shot  the gravel pile at his feet; the pit piglins still admiring
    THE TIMING (the story check: a blow on "hit" 565 lands him on the floor about 577, 20 frames before the cut; the
      lead measured Player.hurt): a knock-back of 0.25 keeps him in the air 8 frames and flies him 0.9 block; 0.4
      (the default) 12 frames and 2 blocks; Player.hurt has no max_back. The stub: attack + hurt on PT09_HIT 590
      (on "axe"), knockback 0.25: in the air 591-598, the cut on 597 catches him at 0.24 above the floor.
      KNOWN CONFLICT, the director's call: home_strike is due WEST of him, so any knock-back throws him EAST, over the
      open pit: x 3.60 -> 4.33 by 596 (the pit's edge is x 4.0: from 594 he is over the pit, in the air); pt10's puff
      stands at rim_w. Options measured on paper: (a) as the stub, cut in the air over the pit's edge (the second,
      unseen blow happens off screen); (b) the brute strikes from the NORTH rim (about (4.0, 8.3), on the floor beyond
      the pit's corner): the knock-back goes south-south-west, onto the floor (he lands at about (3.3, 6.1) with
      0.25), the brute is BEHIND him in depth from this camera (a new film anchor in films/sixseconds_set.py: ask the
      lead; pt10 and pt20's "empty side" follow it).
    NOW (stub): the set's six_rim_side (35 mm f/3 from the south), the pit dug, the runner at rim_w facing the pit
      (iron pickaxe), the brute walking in from BRUTE_IN (0.95, 5.6) on 554 to strike (2.35, 7.0) by about 580, ONE
      attack on 590 with the blow on 590, the three admiring in the pit, three gravel. Hero: the brute.
    MEASURED (the lead's probe and geo; still out/test/sixseconds_scout_pt09_axe_595_zones.png): the brute enters
      the frame's left edge about 568 (body x -3..33 % on 568), at strike by 580 (head x 19-40 %, y 34-43 %, 95 px);
      the runner's eyes x 63 % on 590 -> 84 % on 596 (at the safe area's edge, red, in the air); the pit piglins'
      heads x 72-132 %, y 63-81 %: IN THE CAPTION BAND and off the right edge (tilt the camera down / pan right a
      little: it is this shot's own camera). Earlier (out/test/sixseconds_set_b09_rim_side.png): brute 2.62 x the
      blackstone; pit piglin skin saturation 0.62 (AT the limit).
    NEIGHBOURS: before, pt08_gravel; after, pt10_smoke (the same angle, a little wider).
    """
    f0 = s.frame_start
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(C.P("home_pit_center")), ease=0)
    runner.hold("iron_pickaxe", frame=f0)
    st.use(s, runner)
    brute = C.actor("brute", "pt")
    # pre-rolled (he is in no shot before): already striding in from the left on 560, at strike by about 580
    w0 = f0 - PT09_STRIDE_PRE
    C.put(brute, w0, BRUTE_IN, toward="strike")
    brute.look_at(w0, runner, ease=0)
    brute.walk(w0, [BRUTE_IN, C.P("strike")], speed=1.94, ramp=(0, 4))
    brute.flop_ears(w0, s.frame_end + 1)
    brute.attack(PT09_SWING)                                  # ONE swing; the blow lands on PT09_HIT ("axe")
    runner.hurt(PT09_HIT, from_point=Vector(C.P("strike")), knockback=PT09_KNOCK)
    st.use(s, brute)
    _in_pit(st, s, C, _pigs(C))
    for k in (1, 3, 5):
        C.rest(s, "gravel", "pt9_%d" % k, "six_gravel_%d" % k)
    C.cam(s, "set:six_rim_side", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "pit")


def pt10_smoke(st, s, C, nar):
    """BEAT 10  "He turned into smoke, and the whole world ended."   frames 597-667 (71 f, 2.96 s), sky wastes.
    Words: He 599, turned 601, into 609, smoke 614, and 632, the 635, whole 637, world 645, ended 655 (ends 665).
    THE RESET: from 655 to 667 the encoder shows BLACK with the caption "ended" held on it (films/sixseconds.py
    RESETS): nothing after 654 is seen. The voice then rests 0.5 s (the story check: with 0.2 s "ended. New world"
    ran together; the storyteller's beat after the end of a world), and br11's empty bridge comes up out of black on
    668, in the silence, 9 frames before "New" (677).

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
      THE LEAD'S GEO / STILL of the stub (pt10_smoke:626, out/test/sixseconds_scout_pt10_smoke_626_zones.png): the
      three pit piglins' heads at x 67-112 %, y 59-71 %: IN THE CAPTION BAND and partly outside the right edge, so
      "in the pit the piglins are still looking at their ingots" is not seen; the drops at y 52-60 %. Tilt the
      camera down / pan right a little (it is this shot's own camera) or accept them as soft shapes under the word.
      (pt09 at 575-578: the same: pit piglin heads y 62-81 %.)
    THE PUFF'S PLACE: pt09's knock-back throws him EAST toward the pit's edge (see pt09's KNOWN CONFLICT); the stub's
      puff stands at rim_w, where he stood. If pt09 keeps the cut in the air over the edge, put the puff where the
      second blow found him (on the rim, about (3.85, 7.0)): never inside the pit, which holds the piglins.
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
    """BEAT 20  "In that bastion, everyone likes gold."   frames 1290-1357 (68 f, 2.83 s), sky wastes.
    Words: In 1292, that 1294, bastion 1299, everyone 1319, likes 1328, gold 1334 (ends 1346).

    STORY: High shot over the pit, the camera of sentence six: four piglins each hold an ingot up and stare at it. The
    player stands on the rim, unhurried, ender pearls and gravel popping up around his golden boots. The side of the
    frame where the brute walked in for sentence nine stays empty.
    Location: the older version of the world (the home set, no brute). Cast: the player, four piglins in the pit.
    Effects: four gold ingots in the admire pose, ender pearls and gravel popping out of the pit, golden boots,
    deliberately empty space behind the player.

    MUST BE SEEN, ON WHICH WORD
      frame 1290      four piglins frozen over their ingots; a pearl or gravel already in the air
      "everyone likes gold" 1319-1346   pearls and gravel landing round his boots on explicit floor points (see
                      ENGINE NOTES; one throw per piglin, as in pt08); he stands at ease (an idle, a glance down)
      the whole shot  the brute's side of the frame (west of the rim, toward home_strike) EMPTY
    SHARED: CAMS["pit"] exactly (= pt06); PLACES "rim_w".
    THE WORLD'S RULES: NO BRUTE (NO_BRUTE_SHOTS); the pit dug (C.pit).
    NOW (stub): the pit camera, the pit dug, four piglins admiring on home_pit_1..4, the runner at rim_w with a gold
      ingot in his hand (he is trading: set on the first frame), three gravel and a pearl lying at his feet. Hero: a
      piglin.
    MEASURED (out/test/sixseconds_set_b20_pit.png): four piglins admiring in the pit, the runner at the rim.
    NEIGHBOURS: before, gt19_older (the match cut: the runner sprinted through the brute's spot); after, rw21_stare.
    """
    f0 = s.frame_start
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(C.P("home_pit_center")), ease=0)
    runner.hold("gold_ingot", frame=f0)          # he is trading: gold in his hand (set here: a hold lasts)
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
