"""Six Seconds, sequence PIT: the runner's trap. The golden boots, the pit, the barter, the gravel, the axe, the smoke,
and the older world's pit: beats 5, 6, 7, 8, 9, 10, 20 (shots pt05_boots, pt06_dig, pt07_pearl, pt08_gravel,
pt09_axe, pt10_smoke, pt20_likes), sky "wastes". One function per shot; the contract is in
films/sixseconds_common.py (tags "pt...", C.actor, C.item, C.cam, C.lights, C.pit, st.use / st.hero).

STATUS: SHOT by the pit director (Nov 26) from the lead's stubs. Each shot's docstring has its NOW and MEASURED lines;
the stills of record are out/test/sixseconds_pit_<shot>_<frame>.png (+ _zones), the palette checks
out/test/sixseconds_pal_pt*_<frame>.png, the motion preview out/test/sixseconds_pit_motion.mp4 (every frame of the seven
shots at 270x480, 7 samples). Tool: tools/sixseconds_pit_probe.py (items and bodies of one shot over a span, no
render). BEAT 5 IS TWO SHOTS (the lead's decision): pt05_boots here, rw05_family in the row sequence.

THE SEQUENCE NOW
  pt05  the shared boot framing: his legs sprint in from the frame's left (pre-rolled), skid, the golden boots still
        mid-frame from 300 to the cut; the three piglins soft at the gold, backs to him (idle, ears)
  pt06  the shared pit camera: he breaks the last block on "dug" (cracks 381-388, gone 389, crumbs, no item); the
        three piglins RUN for the lure (the game's chase speed for wanted gold) from the gold, a beat apart, over the
        rim and down (landing 406 / 417 / 427); the first takes the lure on landing and stares; his head follows them
  pt07  above his right shoulder from the south rim side: the three frozen over their ingots; "threw gold" he drops
        one ingot into the pit (442); "threw back" piglin_pt2 (north-west corner, next to his rim) ends its stare and
        lobs the pearl out (472), which lands spinning beside his boots by 486 ("pearls" 489); at 490 that piglin takes
        his new ingot and stares again; his head follows the pearl
  pt08  low from the south along the rim: the golden boots mid-frame, the gravel pile on their west side, the pearl
        alone on their right, the pit's edge at the right, the lava corridor beyond; three more stacks pop out of the
        pit and land (517 / 524 / 538: one per pit piglin), then the pile bobbing to the cut
  pt09  from the south-south-east, high: THE STRIKE FROM THE NORTH RIM. The brute charges from the gateway he guards
        (pre-rolled, axe high, the game's chase speed), ONE swing on "axe" (587), the red flash and the game's full
        knock-back (0.4): the runner flies south-south-west along the west rim, in the air at the cut (597)
  pt10  the same angle pulled back: the puff already rising where the second (unseen) blow left him, the brute's axe
        coming down to rest (600), his head lowering to where the runner was; the boots and the pickaxe on the
        blackstone, the gravel and the pearl at the rim, the three in the pit still over their ingots; black 655-667
  pt20  the shared pit camera, the older world: four piglins over their ingots round a stack of gold in the pit, one
        result already in the air on 1290, three more lobbed round his boots on "everyone likes gold", each piglin
        taking the next ingot off the stack; the runner at ease with gold in his hand; the north side (the brute's
        way in, pt09) empty

THE PLACE (engine/nether.py HOME, THE PIT): the pit's cells x 4..5, y 6..7, two deep (floor z -2), in a patch of
plain blackstone (x 1..7, y 2..9). Its eight blocks are engine.breaking Breakables (C.bas.pit_blocks); C.pit(s) digs it
for one shot, C.pit(s, keep_last=True) leaves the last block (C.bas.pit_last, cell (4, 6, -2)) for him to break on
camera. Physics: world=C.bas sees the pit dug. Anchors: home_rim_w (3.6, 7) the runner at the west rim facing the pit;
home_boot_mark (3.65, 6.75) the skid; six_pit_lure, six_pearl_rest. This file's own places (constants below): PIT_AT
(the trap piglins), PILE (the gravel), STRIKE_N (the brute's blow), PUFF10 / BRUTE10 / DROPS10, PIT20_AT, STACK20.
Lanterns: LIGHTS "pit" (home_pit x 2) in every pit shot; pt05 "home".
SHARED (films/sixseconds_common.py): CAMS["pit"] in pt06 and pt20 EXACTLY (the focus is free); CAMS["boot"] for pt05
  with BOOT_FRAME (br11 repeats it: the skid ends ON boot_mark); PLACES "gold_1".."gold_3" (pt05), "boot_mark",
  "rim_w", "pit_lure", "pearl_rest". "strike" (home_strike) is NOT used any more: see THE STRIKE below.
THE STRIKE (the lead's KNOWN CONFLICT, decided here): home_strike is due west of rim_w, so the game's knock-back threw
  the runner east over the open pit (he would have fallen in among the piglins, and pt10's puff on the rim could not
  be). The brute now strikes from STRIKE_N (4.05, 8.32), on the floor beyond the pit's north-west corner, 1.39 from
  rim_w (the brute's reach is 1.43): the blow throws the runner south-south-west ALONG the west rim, his box never
  over the pit (x <= 3.9 all the way), landing at (2.96, 5.12) with the game's full 0.4. From the old south camera the
  brute would stand behind the runner, so pt09 / pt10 are filmed from the south-south-east, where the brute faces the
  lens three-quarter and the pit with its piglins lies between. STRIKE_N is a point in this file (C.P takes points);
  the lead may add it to the set as an anchor (common_requests).
THE WORLD'S RULES that bite here: THE PIT only in pt06 (last block kept, broken on camera), pt07-pt10, pt20 (C.pit
  refuses elsewhere: pt05's floor is WHOLE); NO BRUTE in pt20; golden boots always; a piglin admires with the ingot in
  its LEFT hand (C.admire / piglins.barter); the pearl is never the answer to the ingot thrown in pt07 (piglin_pt2 has
  been staring since before the cut; it takes the new ingot afterwards); the runner's death is the white puff (C.puff).
ENGINE SIDE DOORS: breaking.mine(..., drop=None); every barter result and lob is a C.item(...) object (never an id).
MINECRAFT TRUTH, and where this file bends it: piglins go for gold at their chase speed (pt06 runs), a brute attacks a
  player on sight at its chase speed with the axe high (pt09), the brute's knock-back is the game's 0.4, a barter is
  one item entity per result (gravel 8-16 drawn as cubes, pearls 2-4), a thrown ingot cannot be taken for 40 ticks
  (pt07: taken on 490 = 442 + 48). Bent: (1) the barters are lobbed with piglins.barter(lob=True) / launch +
  lob_velocity (the director's cheat the engine offers: the game's own throw from a two-deep 2 x 2 pit mostly hits
  the wall), and pt08's and pt20's lobs also come from the east half of the pit; (2) the pile lies round his boots
  although a player picks up items within about 1.3 blocks (a full inventory is the only game reason: not shown);
  (3) the admire stares are shortened (the game's 119 ticks) where a throw falls inside a shot.
TAGS: runner_pt (pt05-pt09, pt20), piglin_pt1 / piglin_pt2 / piglin_xbow_pt3 (pt05-pt07, pt09, pt10, pt20), piglin_pt4
  (pt20), brute_pt (pt09, pt10), gold_ingot_pt1 (pt06 lure), gold_ingot_pt7 (pt07), ender_pearl_pt7 (pt07-pt10:
  C.memo["pt_pearl"]), gravel_pt8_1..7 (pt08-pt10: C.memo["pt_pile"]), golden_boots_pt10, iron_pickaxe_pt10,
  gold_ingot_pt20_stack, gold_ingot_pt20_take_1..4, gravel_pt20_1 / _2 / _3, ender_pearl_pt20_4.
PREVIEW samples of this sequence: 7.
"""
from mathutils import Vector

from engine import breaking, mobs, piglins
from films import sixseconds_common as SC

PIGS = (("piglin", "pt1"), ("piglin", "pt2"), ("piglin_xbow", "pt3"))

# ---- the trap piglins on the pit floor (pt07-pt10), and the way each faces. The ADMIRED INGOT is held 0.59 in front
#      of the snout, 0.74 under the rim: a piglin that faces the west wall holds it against that wall, where the rim
#      hides it from every camera on the runner's side. So they stand in three corners facing into the open
#      south-west quarter (where the ingots then are, mid-pit, seen from above), their faces toward the runner's
#      side: piglin_pt2 in the north-west corner facing south (it is next to the rim where he stands: its barter
#      comes out), piglin_xbow_pt3 north-east facing south-west, piglin_pt1 south-east facing west.
#      (position, a point it faces); boxes 0.6 wide, 0.3 clear of the pit's walls (x 4..6, y 6..8)
PIT_AT = (((5.4, 6.5, -2.0), (4.0, 6.5, -2.0)),        # piglin_pt1: south-east, facing west
          ((4.6, 7.5, -2.0), (4.6, 6.0, -2.0)),        # piglin_pt2: north-west, facing south
          ((5.4, 7.5, -2.0), (4.4, 6.5, -2.0)))        # piglin_xbow_pt3: north-east, facing south-west
THROWER = 1                # pt07: piglin_pt2 throws the pearl (north-west: next to the rim)

# ---- pt06: the three RUN for the lure ingot (the game: a piglin goes for gold it sees within 9 blocks at its
#      chase speed, 5.4 blocks/s: GoToWantedItem 1.0) from their places at the gold, over the rim and down. (points,
#      frame it steps off the rim, drift in the air: None = the game's from a chase, 1.10 block). A and B step off
#      the EAST rim running west and land in the west half; C steps off the north rim (a shorter drift so that it
#      lands in the east half, clear of A and B)
RUNS6 = (
    ([(7.3, 9.6, 0.0), (6.9, 6.5, 0.0), (5.7, 6.5, 0.0)], 398, None),
    ([(6.3, 13.4, 0.0), (6.6, 7.5, 0.0), (5.7, 7.5, 0.0)], 408, None),
    ([(7.2, 16.4, 0.0), (5.45, 9.2, 0.0), (5.45, 7.7, 0.0)], 418, 0.7),
)
LURE_TAKE = 2              # pt06: the first to land takes the lure this many frames after its landing
# (every run starts before 379 so that nobody shows his pt05 place on the first frames: starts 377 / 377 / 376)

# ---- pt07: above his right shoulder, looking down into the pit from the south rim side (the set's six_over_pit, from
#      the south-west, put his reaching right hand and the ingot in it right over the piglin next to the rim: from
#      here his hand and that piglin's face are apart), a slow push
CAM7 = dict(pos=(3.6, 4.4, 3.8), target=(4.85, 7.3, -1.2), lens=26.0, fstop=4.0,
            pos1=(3.66, 4.52, 3.74), target1=(4.85, 7.3, -1.2))
TOSS7 = 442                # "threw" 441: he drops one ingot into the pit (the game's Q: one item, the arm swings)
TOSS7_AIM = (4.75, 6.75, -1.6)         # into the open south-west quarter, within the thrower's reach
PEARL_THROW = 472          # "threw back" 471-484: piglin_pt2's stare ends, the pearl is lobbed (rests by 486)
PEARL_COUNT = 3            # a pearl barter gives 2-4 (one item entity, drawn as two sprites)

# ---- pt08: low on the floor SOUTH of the boots, looking north along the west rim: the pit's edge at the right, the
#      pile on the boots' west side (left), the pearl alone at their right, between them and the pit's edge. The
#      set's six_boots_rim (south-west) saw the lobs pass BEHIND his legs and put the pearl at x 83 %; from here the
#      lobs come out of the pit at the right and cross in front of his shins to the left
CAM8 = dict(pos=(3.0, 3.6, 0.8), target=(3.5, 7.0, 0.05), lens=32.0, fstop=2.8,
            pos1=(3.02, 3.72, 0.79), target1=(3.5, 7.0, 0.05))
PILE = ((2.95, 7.35), (2.75, 7.15), (3.2, 7.55), (3.45, 7.8), (3.1, 6.55), (3.0, 6.95), (2.8, 6.7))
PILE_COUNT = (12, 9, 14, 10, 11, 13, 8)                # one barter = one entity of 8-16 gravel
PILE_LYING = (0, 1, 2, 3)                              # already there on 511 (the barters of the time skipped)
PILE_LOBS = ((4, 0, 518), (5, 2, 526), (6, 1, 540))    # (pile spot, from pit piglin, frame it lies still): one each

# ---- pt09 / pt10: THE STRIKE FROM THE NORTH RIM (the knock-back along the rim, onto the floor, never over the pit).
#      The brute charges from the gateway he guards (the game: a brute attacks every player within 12 blocks, at its
#      chase speed, axe held high) and strikes from STRIKE_N, 1.39 north-north-east of rim_w: the full knock-back
#      (0.4, the game's) throws the runner 2 blocks south-south-west along the west rim (his box stays west of x 4)
STRIKE_N = (4.05, 8.32, 0.0)
BRUTE_RUN = ((4.5, 18.4, 0.0), (4.35, 12.0, 0.0))     # the gateway, then down the courtyard to STRIKE_N
HIT9 = 587                                             # inside "axe" (580-593): in the air 587-599, the cut on 597
KNOCK9 = 0.4
CAM9 = dict(pos=(6.6, -1.0, 2.5), target=(3.8, 7.2, 0.0), lens=32.0, fstop=2.8,
            pos1=(6.48, -0.75, 2.47), target1=(3.8, 7.2, 0.0))
# pt10: the same angle pulled back and a little higher; the second blow (unseen) found him where the first one threw
#      him and its knock-back slid him on south-west: the puff there, the brute 1.6 north-east of it, facing it, the
#      axe coming down to rest; his drops on the blackstone
PUFF10 = (2.4, 4.85, 0.0)
BRUTE10 = (3.5, 5.95, 0.0)
CAM10 = dict(pos=(6.8, -1.5, 3.0), target=(3.7, 6.6, -0.4), lens=26.0, fstop=3.2,
             pos1=(6.62, -1.15, 2.95), target1=(3.7, 6.6, -0.4))
DROPS10 = (("golden_boots", (4.6, 5.6, 0.0)), ("iron_pickaxe", (3.1, 4.3, 0.0)))    # the boots clear of him and the puff
AXE_DOWN = 600             # "turned" 601: the axe comes down to rest (the target is gone)

# ---- pt20: the older world. Four piglins on the pit floor, an ingot stack lying in the pit; each admire runs out in
#      turn, the result is lobbed to the runner's boots and the piglin takes one more ingot off the stack
# The four stand in the pit's corners like a pinwheel, each facing along a wall, so that every admired ingot is held
# out in the open middle of the pit (seen from the high pit camera) and the stack lies in the centre between them.
# (position, a point it faces) for piglin_pt1 (south-east, facing north), piglin_pt2 (north-west, facing south),
# piglin_xbow_pt3 (north-east, facing west), piglin_pt4 (south-west, facing east)
PIT20_AT = (((5.68, 6.32, -2.0), (5.68, 7.5, -2.0)),
            ((4.32, 7.68, -2.0), (4.32, 6.5, -2.0)),
            ((5.68, 7.68, -2.0), (4.5, 7.68, -2.0)),
            ((4.35, 6.5, -2.0), (5.5, 6.5, -2.0)))
STACK20 = (5.0, 7.0, -2.0)
# (piglin, frame its admire ends and it throws, result, count, where the result comes to rest: round his boots on the
# lens's side, inside the safe area of the pit camera)
THROWS20 = ((1, 1283, "gravel", 11, (3.0, 7.12, 0.0)),        # already in the air on 1290
            (3, 1300, "ender_pearl", 3, (3.85, 6.55, 0.0)),
            (0, 1310, "gravel", 14, (3.2, 6.62, 0.0)),
            (2, 1322, "gravel", 9, (3.55, 6.4, 0.0)))


def _pigs(C):
    """The three piglins of the trap (the third with a crossbow)."""
    return [C.actor(role, tag) for role, tag in PIGS]


def _yaw_to(src, dst):
    """Yaw that faces src to dst (a character faces -Y at yaw 0)."""
    return SC.yaw_to(src, dst)


def _in_pit(st, s, C, pigs, admire=True):
    """The trap piglins on their places on the pit floor (PIT_AT), facing into the open quarter, in the admire pose
    for the whole shot (ingot in the LEFT hand at the snout) unless admire=False."""
    for p, (at, faces) in zip(pigs, PIT_AT):
        p.place(s.frame_start, at, _yaw_to(at, faces))
        if admire:
            C.admire(s, p)
    st.use(s, *pigs)


def _run_start(points, step_off, speed=piglins.CHASE_SPEED, ramp_in=4.0):
    """The frame a piglin's walk(run=True, ramp=(ramp_in, 0)) along `points` must start so that it ends (and steps
    off the rim) on `step_off`: Piglin.walk's own count of frames (its route with the corners rounded)."""
    route = mobs._Route([Vector(p) for p in points], piglins.CORNER_RADIUS, 0.0)
    n = max(2, int(round(route.total / (speed / SC.FPS) + ramp_in / 2.0)))
    return step_off - n


def _lob(C, item, src_feet, dst, land):
    """Launch `item` from the hands of a piglin standing on src_feet (0.3 under its eyes, as the game throws) so that
    it comes to rest on `dst` on about frame `land` (piglins.lob_velocity: the arc that clears the rim). Returns
    (launch frame, frame it lies still)."""
    start = Vector(src_feet) + Vector((0.0, 0.0, piglins.PIGLIN_EYE - piglins.THROW_BELOW_EYE))
    v = piglins.lob_velocity(start, dst, world=C.bas)
    ticks = piglins.item_track(start, v, world=C.bas)[-1][0]
    f = int(round(land - ticks * piglins.TICK))
    still = piglins.launch(item, f, start, v, world=C.bas)
    return f, still


def pt05_boots(st, s, C, nar):
    """BEAT 5 (1 of 2)  "He wore golden boots,"   frames 282-321 (40 f, 1.67 s), sky wastes.
    Words: He 284, wore 287, golden 295, boots 307 (ends 318); the cut into rw05_family is 2 frames before "so" (324).

    STORY: The boot shot (returns on the bridge): camera on the blackstone floor, long lens, looking across the
    courtyard at the gold wall. The legs sprint in from the gateway side and skid to a stop with the golden boots
    bright in the middle of the frame, above the caption band. (The piglins' look at the boots is rw05_family: from
    this lens his torso and arms cover their heads wherever they stand: the lead's decision.)
    NOW: CAMS["boot"] exactly (50 mm f/2 on the floor south-west of boot_mark; its handheld), focus on the boots. The
      runner (pre-rolled 12 frames: he is not in gt04, runner_gt is; iron pickaxe) sprints from (4.5, 13) south to
      boot_mark and brakes (Player.walk ramp out: the game's ground friction, the skid); his boots enter at the
      frame's left edge on 282, stop by 300 and stay still to the cut (no idle on him: the hips' weight shift would move
      the boots). The three piglins at gold_1..3 facing the gold (C.stand: idle glances, ears), soft beyond, backs to
      him (as rw05 has them). Hero: the boots. Life: the sprint, then the piglins' idle and the camera's handheld.
    MEASURED (tools.sixseconds_geo pt05_boots:318 --boots runner_pt; still out/test/sixseconds_pit_pt05_boots_318.png
      + _zones; palette out/test/sixseconds_pal_pt05_boots_318.png): boots x 27.7-70.1 %, y 43.1-58.9 % (BOOT_FRAME x
      27-71, y 42-59: the same box as br11); the piglins' heads behind his arms (as the lead measured: the reason for
      rw05). Preview 282-321 looked at frame by frame: the boots enter from the left on 282-288, stop on 300, still
      301-321. PALETTE: see the result line at the end of this docstring.
    NEIGHBOURS: before, gt04_runin (he sprints at the lens through the gateway); after, rw05_family.
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
    for k, p in enumerate(_pigs(C), 1):        # at the gold, backs to him (rw05 turns them): soft
        C.stand(s, p, "gold_%d" % k, look="gold_target", seed=k)
    C.cam(s, "boot", focus=Vector(mark) + Vector((0.0, 0.0, 0.2)))
    st.hero(s, "boots", *C.boots_of(runner))
    C.lights(s, "home")


def pt06_dig(st, s, C, nar):
    """BEAT 6  "He dug a hole, and they fell in."   frames 379-435 (57 f, 2.38 s), sky wastes.
    Words: He 381, dug 384, a 390, hole 391, and 403, they 406, fell 409, in 416 (ends 422).

    STORY: High three-quarter angle on the courtyard: the player breaks the last block of a pit two blocks deep and
    two wide, with cracks and crumbs. A gold ingot is already spinning at the bottom. Three piglins walk to it, step off
    the rim one after another, 0.7 block and a beat apart, and drop in.
    NOW: CAMS["pit"] exactly (focus free: on the last block, racked to the pit's middle on 391). C.pit(s,
      keep_last=True); the runner at rim_w (iron pickaxe) breaks C.bas.pit_last from 381 (breaking.mine, drop=None,
      crumbs with glow 0.25 so they read in the pit's dark): cracks 381-388, gone 389. The lure lies spinning on
      pit_lure. The three RUN for it (Minecraft: a piglin goes for gold it sees at its chase speed, 5.4 blocks/s) from
      the gold, pre-rolled (they are not in rw05), so all are moving on 379: piglin_pt1 from gold_1, piglin_pt2 and
      piglin_xbow_pt3 entering from the top; each runs off the rim unbraked (RUNS6) and falls two blocks with the
      game's gravity: step off 398 / 408 / 418, land 406-407 / 417 / 427 (on "they"-"fell", "in", 8 frames before the
      cut), at (4.62, 6.5), (4.58, 7.5), (5.45, 7.0). piglin_pt1 takes the lure 2 frames after it lands
      (piglins.barter, no result) and stares; the other two look at its gold. His head: down on the block, then up
      at the first piglin coming and down with them (Player.watch). Hero: the runner.
    MEASURED (tools.sixseconds_pit_probe pt06_dig:379-435 --near; geo pt06_dig:427; preview 379-435): runner eyes
      x 21.6 %, y 41.7 %; the falling piglins cross x 47-80 %, y 25-64 %; in the pit at 427 their heads x 29-65 %,
      y 42-61 % (piglin_pt1's head bottom 60.8 %); closest approach between two piglins 0.91 block (in the air), to
      the runner 1.47. The lure at x 52 %, y 54 % until it is taken. The bottom of the frame (y > 62 %) is the empty
      floor before the pit: the shared camera.
    NEIGHBOURS: before, rw05_family (the brothers at the gold); after, pt07_pearl (above his shoulder into the pit).
    """
    f0, f1 = s.frame_start, s.frame_end
    C.pit(s, keep_last=True)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    last = Vector(C.bas.pit_last.center)
    runner.look_at(f0, last, ease=0)
    runner.hold("iron_pickaxe", frame=f0)
    dug = breaking.mine(runner, C.bas.pit_last, f0 + 2, camera=s, drop=None,     # drop=None: ENGINE SIDE DOORS
                        glow=0.25)                     # the crumbs read in the pit's dark (breaking: glow at night)
    st.use(s, runner)
    lure = C.rest(s, "gold_ingot", "pt1", "pit_lure")
    pigs = _pigs(C)
    lands = []
    for p, (pts, off, drift) in zip(pigs, RUNS6):
        start = _run_start(pts, off)
        p.place(start, pts[0], _yaw_to(pts[0], pts[1]))         # pre-rolled: not in rw05, the shot before
        end = p.walk(start, pts, run=True, ramp=(4, 0))
        land = p.fall(end, -2.0, forward=drift)
        p.flop_ears(land, f1 + 1)
        lands.append(land)
    st.use(s, *pigs)
    # the first one down takes the lure and admires it; the other two land beside it and look at its gold
    piglins.barter(pigs[0], lure, lands[0] + LURE_TAKE, result_item=None, world=C.bas)
    for p, land in zip(pigs[1:], lands[1:]):
        p.look_at(land + 4, pigs[0].item_point(lands[0] + LURE_TAKE + 2, "off"), ease=6)
    # his head: down on the block he breaks, then up at the first piglin coming, down with them into the pit
    runner.watch(dug["frame"] + 2, lands[0] + 4, pigs[0], ease=6)
    runner.watch(lands[0] + 5, f1, pigs[2], ease=8)
    C.cam(s, "pit", focus=last)
    C.rack(s, Vector(C.P("home_pit_center")) + Vector((0.0, 0.0, 1.2)), dug["frame"] + 2, frames=12)
    st.hero(s, "runner", runner)
    C.lights(s, "pit")


def pt07_pearl(st, s, C, nar):
    """BEAT 7  "He threw gold, and they threw back ender pearls."   frames 436-510 (75 f, 3.12 s), sky wastes.
    Words: He 438, threw 441, gold 447, and 465, they 468, threw 471, back 477, ender 484, pearls 489 (ends 505).

    STORY: From behind and above the player's shoulder at the rim, looking down into the pit: all three piglins
    already stand frozen, each with an ingot held up in front of his snout. The player tosses one more ingot down. A
    piglin who has been staring since the last shot lowers his hand, and an ender pearl pops up out of the pit and
    lands spinning beside the golden boots. The pearl is never the answer to the ingot thrown in this shot.
    NOW: CAM7 (26 mm f/4 above his right shoulder from the south rim side, a slow push). The three stand in PIT_AT
      (three corners, each facing into the open south-west quarter, their faces to the runner's side), the runner at
      rim_w with a gold ingot. 436: all three in the admire pose. 442 ("threw" 441): he drops one ingot (Player.attack
      = the game's arm swing on Q; piglins.throw_item) into the open quarter. 472 ("threw" 471): piglin_pt2 (north-west
      corner, the half next to his rim: the game's thrower) ends its stare (piglins.barter from 436, shortened), the
      off hand swings and the pearl (ONE entity, 3 pearls drawn as two sprites, C.memo["pt_pearl"]) is lobbed out and
      comes to rest on pearl_rest by 486, broad side to the lens, before "pearls" 489. 490: the same piglin takes his
      new ingot (the 40-tick pick-up delay: 442 + 48) and stares again. His head goes to the toss, back to the pit,
      then follows the pearl down to his boots. Focus on piglin_pt2's head, racked to the pearl at 484. Hero:
      piglin_pt2.
    WHY THIS CAMERA: from the set's six_over_pit (south-west) his reaching right hand and the ingot in it lay right
      over piglin_pt2's face (geo / stills); from the south-west and west every camera has the runner between it and
      the piglin next to his rim.
    MEASURED (geo pt07_pearl:476; still out/test/sixseconds_pit_pt07_pearl_476.png, _486, _492; probe): piglin heads
      x 30-81 %, y 34-58 % (pt2 42 / 42, xbow_pt3 61 / 38, pt1 72 / 49 eyes), faces 83-90 px, 15-49 degrees off the
      lens; the runner's head at the left edge (x -5..28 %: the over-the-shoulder); the pearl rises from piglin_pt2's
      hands and rests at x 40 %, y 48 % (pt08's own frame has it at x 62-81 %: the lead's x 83 % is gone). The
      admired ingots are small from this height: the pose (bowed head, raised left arm) carries the stare.
    NEIGHBOURS: before, pt06_dig; after, pt08_gravel (a time skip: the pile has come back meanwhile).
    """
    f0, f1 = s.frame_start, s.frame_end
    C.time_jump(f0)
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    pigs = _pigs(C)
    for p, (at, faces) in zip(pigs, PIT_AT):
        p.place(f0, at, _yaw_to(at, faces))
    a = pigs[THROWER]
    a_at = Vector(PIT_AT[THROWER][0])
    runner.look_at(f0, a_at + Vector((0.0, 0.0, 1.3)), ease=0)
    runner.hold("gold_ingot", frame=f0)
    st.use(s, runner)
    # "He threw gold": one more ingot dropped into the pit (it cannot be taken for 40 ticks)
    runner.look_at(TOSS7 - 5, Vector(TOSS7_AIM), ease=4)
    runner.attack(TOSS7)
    ingot = C.item("gold_ingot", "pt7")
    landed = piglins.throw_item(ingot, TOSS7, runner, Vector(TOSS7_AIM), world=C.bas)
    ingot.animate(TOSS7, f1 + 1)
    st.use(s, ingot)
    # "they threw back ender pearls": the piglin next to the rim has been staring since before the cut; its admire
    # runs out, the off hand swings and the pearl is lobbed out of the pit to land beside his boots. ONE item
    # entity, lying there through pt08, pt09 and pt10 (C.memo["pt_pearl"])
    pearl = C.memo["pt_pearl"] = C.item("ender_pearl", "pt7", count=PEARL_COUNT)
    beats = piglins.barter(a, None, f0, pearl, toward=Vector(C.P("pearl_rest")),
                           admire_ticks=(PEARL_THROW - f0) / piglins.TICK, world=C.bas, lob=True,
                           face=CAM7["pos"], animate=C.T["pt10_smoke"].frame_end + 1 - PEARL_THROW, seed=0)
    C.memo["pt_pearl_landed"] = beats["landed"]
    st.use(s, pearl)
    # ... and once the new ingot may be taken, it takes that one and stares again (the trap goes on)
    take = max(landed + 2, TOSS7 + 48)
    if take <= f1 - 6 and piglins.in_reach(a, ingot, take):
        piglins.barter(a, ingot, take, result_item=None, world=C.bas)
    for p in pigs:
        if p is not a:
            C.admire(s, p)
    st.use(s, *pigs)
    # his head follows the pearl out of the pit and down to his boots
    runner.look_at(PEARL_THROW - 6, a_at + Vector((0.0, 0.0, 1.0)), ease=6)
    runner.track(PEARL_THROW + 2, beats["landed"] + 3, pearl.spinner, step=3, ease=4)
    C.cam(s, None, focus=a.head, **CAM7)
    C.rack(s, Vector(C.P("pearl_rest")) + Vector((0.0, 0.0, 0.2)), PEARL_THROW + 12, frames=10)
    st.hero(s, "piglin", a)
    C.lights(s, "pit")


def pt08_gravel(st, s, C, nar):
    """BEAT 8  "Mostly gravel."   frames 511-559 (49 f, 2.04 s), sky wastes. Words: Mostly 513, gravel 526 (ends 540:
    19 frames of hold).

    STORY: Close on the golden boots at the rim of the pit: gravel pops out of the hole piece after piece and piles up
    around his feet, bobbing and spinning, with one lonely ender pearl among it. Boots and pile sit between 14 and 60
    percent of the frame height. Hold a full beat after the words.
    MINECRAFT TRUTH: one barter throws its loot ONCE, after a 119-tick admire, gravel as ONE item entity of 8-16; so
      the pile is mostly already there on 511 (the barters of the time skipped at the cut) and one more lands per pit
      piglin.
    NOW: CAM8 (32 mm f/2.8 low on the floor SOUTH of the boots, looking north along the west rim, a slow push): the
      boots mid-frame, the pit's dark edge at the right, the lava corridor through the gateway beyond. PILE: four
      stacks (12 / 9 / 14 / 10) lying on the boots' west side on 511, three more lobbed out of the pit, one from each
      pit piglin's hands (launch + lob_velocity), the first already in the air on 511: they come to rest about 517,
      524, 538 (the last on "gravel"'s tail); then nothing moves but the bob and spin and the push, to 559. pt07's
      pearl lies alone at their right (pearl_rest), turning (edge-on at 511, broad side again by "gravel"). The runner
      at rim_w (iron pickaxe set), head down into the pit, no idle (the boots still). The pile entities carry on into
      pt09 and pt10 (C.memo["pt_pile"]). Hero: the boots.
    WHY THIS CAMERA: from the set's six_boots_rim (south-west) the lobs passed behind his legs and the pearl sat at
      x 83 %; with the pile on the lens's side it hid the boots (stills sixseconds_pit_pt08_gravel_512 / _545 of the
      first try).
    MEASURED (geo pt08_gravel:540 --boots; stills out/test/sixseconds_pit_pt08_gravel_513.png, _545; probe): boots
      x 45-66 %, y 41-55 %; the pile x 8-44 %, y 43-57 %; the pearl x 62-81 %, y 46-55 %; his head above the top
      (y -5..18 %: under the top icons). Preview 511-559 looked at.
    NEIGHBOURS: before, pt07_pearl; after, pt09_axe (the brute charges from the gateway).
    """
    f0, f1 = s.frame_start, s.frame_end
    C.time_jump(f0)
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(PIT_AT[THROWER][0]) + Vector((0.0, 0.0, 1.0)), ease=0)
    runner.hold("iron_pickaxe", frame=f0)
    st.use(s, runner)
    last = C.T["pt10_smoke"].frame_end + 1
    pile = []
    for k in PILE_LYING:
        g = C.item("gravel", "pt8_%d" % (k + 1), count=PILE_COUNT[k])
        g.place(f0, (PILE[k][0], PILE[k][1], 0.0), age=200.0 + 37.0 * k)
        g.animate(f0, last)
        pile.append(g)
    lobs = []
    for k, src, land in PILE_LOBS:
        g = C.item("gravel", "pt8_%d" % (k + 1), count=PILE_COUNT[k])
        fl, still = _lob(C, g, PIT_AT[src][0], (PILE[k][0], PILE[k][1], 0.0), land)
        g.animate(fl, last)
        pile.append(g)
        lobs.append((fl, still))
    C.memo["pt_pile"] = pile
    C.memo["pt_lobs8"] = lobs
    st.use(s, *pile)
    st.use(s, C.memo["pt_pearl"])               # pt07's pearl, still turning where it landed
    C.cam(s, None, focus=Vector(C.P("rim_w")) + Vector((0.0, 0.0, 0.15)), **CAM8)
    st.hero(s, "boots", *C.boots_of(runner))
    C.lights(s, "pit")


def pt09_axe(st, s, C, nar):
    """BEAT 9  "I hit him with my axe."   frames 560-596 (37 f, 1.54 s), sky wastes. Words: I 562, hit 565, him 568,
    with 571, my 575, axe 580 (ends 593).

    STORY: Side-on medium at the rim: the brute strides into frame behind the player and swings the golden axe once.
    The player flashes red and is knocked back off his feet. Cut on the knock-back. The only full swing in the film.
    NOW: THE STRIKE FROM THE NORTH RIM (module docstring). CAM9 (32 mm f/2.8 from the south-south-east, 2.5 high, a
      slow push; focus on the brute's head, following him). The brute (pre-rolled: in no shot before) runs from the
      gateway he guards (BRUTE_RUN) at the game's chase speed with the axe held high (aggro), head on the runner: far
      and small on 560 (x 79 %), at STRIKE_N on 587. ONE swing (Piglin.attack 587, the axe lowest at 590.6) and the
      blow on its first tick (the game): runner.hurt(587, from STRIKE_N, knockback 0.4) = the red flash and the
      game's full knock-back, 1.99 blocks south-south-west along the west rim, 0.96 high: in the air 587-599, 0.68 up
      on 596, so the cut on 597 is in the air. The runner at rim_w (iron pickaxe), idle, head on the pit, until the
      blow. The three in the pit admiring (PIT_AT), the pile and the pearl at his feet (from pt08). Hero: the brute.
    MEASURED (geo pt09_axe:580 / :594; probe pt09_axe:560-596 --near; preview 560-596 looked at frame by frame;
      palette out/test/sixseconds_pal_pt09_axe_580.png): the brute's head x 57-72 %, y 28-33 % (face 52-58 px,
      25-34 degrees off the lens: three-quarter), x 2.51 the blackstone; the runner's eyes x 45 % -> 26 % on 594 (in
      the air, red); the pit piglins' heads x 56-86 %, y 49-62 % (the lead's y 59-81 % / off the right edge is gone;
      piglin_xbow_pt3's head reaches x 86 %: a background figure); brute and runner 1.39 apart at the blow, never
      closer. Piglin skin s 0.61 (limit 0.62).
    NEIGHBOURS: before, pt08_gravel; after, pt10_smoke (the same angle, pulled back).
    """
    f0, f1 = s.frame_start, s.frame_end
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(PIT_AT[THROWER][0]) + Vector((0.0, 0.0, 1.0)), ease=0)
    runner.hold("iron_pickaxe", frame=f0)
    runner.idle(f0, HIT9, seed=9)
    st.use(s, runner)
    # the brute: pre-rolled (he is in no shot before), already charging from the gateway on 560, axe high
    brute = C.actor("brute", "pt")
    path = [BRUTE_RUN[0], BRUTE_RUN[1], STRIKE_N]
    route = mobs._Route([Vector(p) for p in path], piglins.CORNER_RADIUS, 0.0)
    ramp_in, ramp_out = 4.0, 4.0
    n = max(2, int(round(route.total / (piglins.CHASE_SPEED / SC.FPS) + (ramp_in + ramp_out) / 2.0)))
    w0 = HIT9 - n
    brute.place(w0, path[0], _yaw_to(path[0], path[1]))
    brute.aggro(w0)
    brute.look_at(w0, runner, ease=0)
    brute.walk(w0, path, run=True, ramp=(ramp_in, ramp_out))
    brute.track(w0 + 1, HIT9, runner, step=3, ease=3)
    brute.attack(HIT9)                                        # ONE swing; the game deals the blow on its first tick
    runner.hurt(HIT9, from_point=Vector(STRIKE_N), knockback=KNOCK9)
    brute.track(HIT9 + 1, f1, runner, step=2, ease=3)
    brute.flop_ears(HIT9, f1 + 1)
    st.use(s, brute)
    _in_pit(st, s, C, _pigs(C))
    st.use(s, *C.memo["pt_pile"])
    st.use(s, C.memo["pt_pearl"])
    C.cam(s, None, focus=brute.head, **CAM9)
    st.hero(s, "brute", brute)
    C.lights(s, "pit")


def pt10_smoke(st, s, C, nar):
    """BEAT 10  "He turned into smoke, and the whole world ended."   frames 597-667 (71 f, 2.96 s), sky wastes.
    Words: He 599, turned 601, into 609, smoke 614, and 632, the 635, whole 637, world 645, ended 655 (ends 665).
    THE RESET: from 655 to 667 the encoder shows BLACK with the caption "ended" held on it (films/sixseconds.py
    RESETS): nothing after 654 is seen; br11's empty bridge comes up out of black on 668, in the silence.

    STORY: Same angle, a little wider. The brute's axe is just coming down to rest from a second blow we did not see.
    A white puff where the player was. Gravel, the iron pickaxe, the golden boots and one ender pearl scatter and spin
    on the blackstone. In the pit the piglins are still looking at their ingots. On the word ended the picture snaps
    to black and the caption word stays on the black for half a second.
    NOW: a time skip of about two seconds (the second blow comes no sooner than 24 frames after the first, and the
      puff 24 frames after the death). CAM10 = CAM9's angle pulled back 1.5 blocks and up (26 mm f/3.2, a slow
      linear push). The puff (C.puff from 591: already rising on 597) at PUFF10, south-west along the rim from where
      the first blow threw him (the killing blow's knock-back slid him on); the brute at BRUTE10 facing it, the axe
      still up on 597 and coming down to rest from 600 (aggro off, 3 frames: "turned" 601: nobody to hit any more),
      his head lowering from the puff to the floor where the runner was (612-624). His drops lie spinning on the
      blackstone (C.rest, broad side to the lens on "smoke"): the iron pickaxe under the puff, the golden boots apart
      at his right; the gravel pile and the pearl still at the rim (one entity each since pt08 / pt07); the three in
      the pit over their ingots. Hero: the brute.
    MEASURED (geo pt10_smoke:620; probe pt10_smoke:597-654; preview 597-667 looked at; palette
      out/test/sixseconds_pal_pt10_smoke_620.png): the brute's head x 33-49 %, y 31-38 % (face 55 px), x 2.57 the
      blackstone; the pit piglins' heads x 58-82 %, y 45-54 % (above the caption band: the lead's y 59-71 % is gone);
      the boots x 54-62 %, y 47-52 %; the pickaxe x 20-30 %, y 50-54 %; the puff left of the brute (x 3-31 %).
    NEIGHBOURS: before, pt09_axe; after (out of black), br11_boots on the bridge of another world.
    """
    f0, f1 = s.frame_start, s.frame_end
    C.time_jump(f0)
    C.pit(s)
    brute = C.actor("brute", "pt")
    brute.place(f0, BRUTE10, _yaw_to(BRUTE10, PUFF10))
    brute.aggro(f0)                                           # the axe still up from the blow ...
    brute.look_at(f0, Vector(PUFF10) + Vector((0.0, 0.0, 0.6)), ease=0)
    brute.aggro(AXE_DOWN, on=False, ease=3)                   # ... coming down to rest: nobody to hit any more
    for item, where in DROPS10:
        C.rest(s, item, "pt10", where, face=CAM10["pos"], face_at=C.at(s, "smoke"))
    brute.look_at(C.at(s, "smoke") - 2, Vector(PUFF10) + Vector((0.3, -0.2, 0.1)), ease=12)  # down to where he was
    brute.flop_ears(f0, f1 + 1)
    st.use(s, brute)
    C.puff(s, PUFF10, f0 - 6, seed=10)
    _in_pit(st, s, C, _pigs(C))
    st.use(s, *C.memo["pt_pile"])
    st.use(s, C.memo["pt_pearl"])
    C.cam(s, None, focus=brute.head, ease="linear", **CAM10)
    st.hero(s, "brute", brute)
    C.lights(s, "pit")


def pt20_likes(st, s, C, nar):
    """BEAT 20  "In that bastion, everyone likes gold."   frames 1290-1357 (68 f, 2.83 s), sky wastes.
    Words: In 1292, that 1294, bastion 1299, everyone 1319, likes 1328, gold 1334 (ends 1346).

    STORY: High shot over the pit, the camera of sentence six: four piglins each hold an ingot up and stare at it. The
    player stands on the rim, unhurried, ender pearls and gravel popping up around his golden boots. The side of the
    frame where the brute walked in for sentence nine stays empty.
    NOW: CAMS["pit"] exactly (focus on the pit, 1.4 above its floor). The pit dug; four piglins (piglin_pt1, pt2,
      xbow_pt3 and pt4) in the pit's corners like a pinwheel (PIT20_AT), each facing along a wall so that its admired
      ingot is held out in the open middle, a stack of 64 ingots lying between them (STACK20). Each stare runs out in
      turn (THROWS20: 1283, pre-rolled so its gravel is already in the air on 1290; 1300 a pearl; 1310, 1322 gravel)
      and the result is lobbed out to rest round his boots on the lens's side (piglins.barter lob=True); 8 frames
      later that piglin takes one more ingot off the stack (a single ingot flies to it: piglins.barter) and stares
      again. The results come to rest about 1302, 1316, 1326, 1340 ("everyone" 1319 .. "gold" 1334). The runner at
      rim_w with gold in his hand, idle (Player.idle). No brute; the north side, where he charged in pt09, is empty.
      Hero: piglin_pt1.
    MEASURED (geo pt20_likes:1336; probe pt20_likes:1284-1357; still out/test/sixseconds_pit_pt20_likes_1336.png;
      preview 1290-1357): the four heads x 24-75 %, y 38-61 % (piglin_pt4's, the nearest, y 52-61 %), three of the
      four ingots catch the light in the pit; the runner's eyes x 21.6 %, y 41.7 %; the results rest at y 54-60 %
      (x 14-37 %), just above the caption band. The shared camera leaves the bottom third empty floor.
    NEIGHBOURS: before, gt19_older (the match cut: the runner sprinted through the brute's spot); after, rw21_stare.
    """
    f0, f1 = s.frame_start, s.frame_end
    C.pit(s)
    runner = C.actor("runner", "pt")
    C.put(runner, f0, "rim_w")
    runner.look_at(f0, Vector(STACK20) + Vector((0.0, 0.0, 1.0)), ease=0)
    runner.hold("gold_ingot", frame=f0)          # he is trading: gold in his hand (set here: a hold lasts)
    runner.idle(f0, f1 + 1, seed=20)
    st.use(s, runner)
    pigs = _pigs(C) + [C.actor("piglin", "pt4")]
    stack = C.rest(s, "gold_ingot", "pt20_stack", STACK20, count=64)
    for k, (p, (at, faces)) in enumerate(zip(pigs, PIT20_AT)):
        t = next(t for j, t, _r, _n, _w in THROWS20 if j == k)
        start = min(f0, t - 12)                  # the one already throwing on 1290 is pre-rolled (not in gt19)
        p.place(start, at, _yaw_to(at, faces))
    for j, t, res, n, where in sorted(THROWS20, key=lambda r: r[1]):
        p = pigs[j]
        start = min(f0, t - 12)
        item = C.item(res, "pt20_%d" % (j + 1), count=n)
        beats = piglins.barter(p, None, start, item, toward=Vector(where), admire_ticks=(t - start) / piglins.TICK,
                               world=C.bas, lob=True, face=SC.CAMS["pit"]["pos"], animate=f1 + 1 - t, seed=j)
        st.use(s, item)
        # ... and takes one more ingot off the stack lying in the pit: the next six seconds start
        again = beats["throw"] + 8
        if again <= f1 - 4:
            one = C.item("gold_ingot", "pt20_take_%d" % (j + 1))
            one.place(again - 1, STACK20)
            st.use(s, one)
            piglins.barter(p, one, again, result_item=None, world=C.bas)
    st.use(s, *pigs)
    st.use(s, stack)
    C.cam(s, "pit", focus=Vector(C.P("home_pit_center")) + Vector((0.0, 0.0, 1.4)))
    st.hero(s, "piglin", pigs[0])
    C.lights(s, "pit")
