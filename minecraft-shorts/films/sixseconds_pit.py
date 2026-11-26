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
import math

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

# ---- pt06: the three run for the lure ingot (the game: a piglin goes for gold it sees within 9 blocks at its
#      chase speed, 5.4 blocks/s: GoToWantedItem 1.0) from their places at the gold, over the rim and down. (points,
#      frame it steps off the rim, drift in the air: None = the game's from a chase, 1.10 block). A and B step off
#      the EAST rim running west and land in the west half; C steps off the north rim (a shorter drift so that it
#      lands in the east half, clear of A and B)
RUNS6 = (
    ([(7.3, 9.6, 0.0), (6.9, 6.5, 0.0), (5.7, 6.5, 0.0)], 398, None),
    ([(6.3, 13.4, 0.0), (6.6, 7.5, 0.0), (5.7, 7.5, 0.0)], 408, None),
    ([(7.0, 15.5, 0.0), (5.45, 9.2, 0.0), (5.45, 7.7, 0.0)], 418, 0.7),
)
LURE_TAKE = 2              # pt06: the first to land takes the lure this many frames after its landing

# ---- pt07: above his right shoulder, looking down into the pit from the south rim side (the set's six_over_pit, from
#      the south-west, put his reaching right hand and the ingot in it right over the piglin next to the rim: from
#      here his hand and that piglin's face are apart), a slow push
CAM7 = dict(pos=(3.6, 4.4, 3.8), target=(4.85, 7.3, -1.2), lens=26.0, fstop=4.0,
            pos1=(3.66, 4.52, 3.74), target1=(4.85, 7.3, -1.2))
TOSS7 = 442                # "threw" 441: he drops one ingot into the pit (the game's Q: one item, the arm swings)
TOSS7_AIM = (4.75, 6.75, -1.6)         # into the open south-west quarter, within the thrower's reach
PEARL_THROW = 472          # "they" 468 / "threw back" 471-484: piglin A's admire ends, the pearl is lobbed
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
#      him: the brute 1.0 north-east of the puff, facing it, the axe coming down to rest; his drops round the puff
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
            ((4.32, 6.32, -2.0), (5.5, 6.32, -2.0)))
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
    """BEAT 5 (1 of 2)."""
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
    """BEAT 6."""
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
    C.memo["pt_lands6"] = lands


def pt07_pearl(st, s, C, nar):
    """BEAT 7."""
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
    """BEAT 8."""
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
    """BEAT 9."""
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
    """BEAT 10."""
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
    """BEAT 20."""
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
