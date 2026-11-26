"""Six Seconds, sequence GATE: the guard landing, THE GATE FRAME, the gateway seen from the corridor. Beats 1, 3, 4,
17, 18, 19 (shots gt01_landing, gt03_guard, gt04_runin, gt17_waits, gt18_nocome, gt19_older), sky "wastes" (the home
bastion's dark red; gt19 is "the older version of the world": the SAME sky and set, block for block). One function
per shot; the contract is in films/sixseconds_common.py (tags "gt...", C.actor, C.cam, C.lights, st.use / st.hero).

STATUS: SHOT by the gate director (Nov 26) on the lead's stubs. What each shot now does (its docstring has the NOW
and MEASURED lines, the stills and the palette checks):
  gt01  the hook portrait: his own camera in the landing's corner at 20 mm, a linear push straight at the brute (his
        ear no longer leaves the frame: head x 10-54 %), the brothers re-spaced at the gold to his right
  gt03  THE GATE FRAME: his eyes on the brothers on the cut, his head up to the gateway ON "guard" (clean profile)
  gt04  the lead's run; the brute's head follows the runner down, then his body turns after him; the focus racks
        from the runner to the brute once he is past the lens; a neutral fill keeps the shirt teal
  gt17  one slow heavy step into the gateway (pre-rolled, planted by "waiting"), axe low, a slow push in
  gt18  THE GATE FRAME: the silhouette in the gateway, the flicker, the ears (the piglins placed once for gt19 too)
  gt19  the match cut; the runner far down the corridor's east side on the cut, through the brute's spot under
        "older version", out of the frame's LEFT edge along the landing's foot by "before"; the crossbow piglin's head
        follows him and goes back to the gold
MOTION: out/test/sixseconds_gate_motion.mp4 (every frame of the six shots, 270x480, 5 samples, 24 fps).

THE PLACE (engine/nether.py HOME; out/test/nether_map_home.png): the courtyard x 0..8, y -2..17, floor z 0; the
GATEWAY x 3..5 in the north wall (y 18..20), 5 high, the entrance corridor y 21..32 beyond it with lava channels and
a lava wall at y 33 (the orange glow; bas.lava_flicker); the GUARD STAIR x 0..1 along the west wall (y 6..9) up to
the LANDING x 0..2, y 10..17, standing height 4, beside the gateway's west jamb; the GOLD WALL x 9, y 9..15 with its
step at x 8. Lanterns: home_landing, home_gate (two, either side of the gateway), home_gold, home_pit.
SHARED (films/sixseconds_common.py): CAMS["gate"] in gt03, gt18 and gt19 EXACTLY, its handheld and seed included
  (the drift runs on across the 18 -> 19 match cut); PLACES "gold_1".."gold_3" (the three piglins at the gold, also
  pt05's and rw05's places) IDENTICAL in gt18 and gt19 (the stub places them ONCE in gt18 for both shots); PLACES
  "landing" (gt03, gt04), "gateway" (gt17, gt18).
THE WORLD'S RULES that bite here: the floor is WHOLE in every one of these shots (no C.pit); the brute is ABSENT
  from gt19 (NO_BRUTE_SHOTS); the runner wears the golden boots and holds the iron pickaxe.
SPEEDS (players.py, for the runs of gt04 and gt19): sprint 5.61 blocks/s (0.234 a frame), sprint-jump 7.13 (0.297
  a frame; 4.28-block hops 1.25 high, ramp=False = already at speed): 42 frames hold at most 9.8 / 12.5 blocks.
TAGS TAKEN: brute_gt (gt01, gt03, gt04, gt17 (pre-rolled 8 frames: not in fl16_home), gt18), piglin_gt1 /
  piglin_gt2 / piglin_xbow_gt3 (gt01, gt03, gt17, gt18, gt19; C.memo["gt_gold_piglins"]), runner_gt (gt04, gt19).
  Fills: "gt_runin" (gt04). A new twin: gt4, gt5 ...
PREVIEW samples of this sequence: 5 (films/sixseconds_common.py PREVIEW_SAMPLES).
"""
from mathutils import Vector

GOLD = ("gold_1", "gold_2", "gold_3")
# gt01: this shot's own camera (the set's six_landing moved into the landing's north-west corner, 20 mm) and the
# brute's own spot near the landing's north-east corner, facing the lens; he looks just past it (LANDING_LOOK)
LANDING_CAM = dict(pos=(0.15, 17.8, 5.8), target=(6.14, 14.17, 3.6), lens=20.0, fstop=2.8,
                   pos1=(0.456, 17.675, 5.79), target1=(6.14, 14.17, 3.6))
LANDING_BRUTE = (2.72, 16.75, 4.0)
LANDING_LOOK = (-0.1, 17.2, 5.6)
LANDING_PIGS = ((7.35, 12.4, 0.0), (6.95, 11.8, 0.0), (7.35, 10.45, 0.0))  # the brothers at the gold, facing east
# gt03: on the cut the brute looks down at his brothers at the gold (their heads), then to the gateway's mouth
GUARD_DOWN = (6.6, 11.4, 1.7)
# gt17: nether's corridor camera (35 mm f/2.4 from the corridor) with a slow push in; the brute's one slow, heavy step
# from just inside the courtyard into the middle of the gateway (PLACES "gateway", facing out), pre-rolled
WAIT_CAM = dict(pos=(3.6, 25.5, 1.55), target=(3.9, 19.0, 1.45), lens=35.0, fstop=2.4,
                pos1=(3.66, 24.75, 1.53), target1=(3.9, 19.0, 1.45))
WAIT_FROM = (4.5, 18.0, 0.0)
WAIT_SPEED = 1.2              # piglins.py: "slow heavy brute: speed=1.2, swing=0.5"
WAIT_PREROLL = 8
WAIT_LOOK = (4.5, 26.0, 1.9)  # just past the lens's right side
# gt04: the runner is already sprint-jumping in the corridor on 240 (ramp off: at speed), comes through the gateway
# and passes the lens 1.0 block WEST of it (the camera is at x 4.9): he leaves the frame's left edge before the lens
# instead of running into it (the technical check: the first stub's line ran straight at the lens).
RUN_IN = [(4.5, 21.6, 0.0), (4.4, 18.5, 0.0), (3.9, 11.0, 0.0), (3.7, 8.0, 0.0)]
RUN_IN_WATCH = (248, 266)     # gt04: the brute's head follows the runner from the gateway to past the lens ...
RUN_IN_TURN = 10              # ... then his body turns after him (266-276), still before the cut's last 3 frames
RUN_IN_RACK = 268             # the focus leaves the runner (gone past the left edge on 269-270) for the brute
# gt04: a neutral shadowless fill east of his line and above it, so that his teal shirt keeps its hue in the warm
# lantern and lava light (without it: hue 169 on 256, the check wants 170-196)
RUN_IN_FILL = dict(pos=(5.8, 13.5, 2.6), watts=60.0, color=(0.95, 0.98, 1.0))
# gt19: on the match cut the runner is a small figure far down the corridor on its EAST side (the gate camera sees
# the whole corridor: nowhere to hide him; every figure in it lands at x 43-48 % of the frame, right of the brute's
# former silhouette at x 33-42 %), sprint-jumping already (ramp off). He goes through the brute's spot (4.5, 19) under
# "older version" and then turns down the WEST side of the courtyard, along the landing's foot (x >= 3.25 beside it: its
# body is solid to x 3.0), and out of the frame's LEFT edge by 1250 (during "from"): the gold piglins are on the east
# side, and the right edge is reached only near the lens (the stub's right exit took 49 frames from the spot, this one
# 43), so "before they added me" plays over the empty gateway and landing. NOT nether's home_run_past (its leg
# (4.5, 19) -> (6.4, 9) runs through piglin_gt2 at gold_2: the technical check). He ends behind the camera's plane.
RUN_PAST = [(5.65, 26.4, 0.0), (4.5, 19.0, 0.0), (3.55, 10.2, 0.0), (2.45, 6.0, 0.0), (2.4, -1.2, 0.0)]
GLANCE = (1216, 1238)     # piglin_xbow_gt3 (gold_3) follows the runner with its head on these frames


def _gold_piglins(st, s, C, look="gold_target", idle=True):
    """The three piglins at the gold (PLACES gold_1..3, the third with a crossbow), facing it, alive (idle=False: no
    glances, only the ears, whose flop follows the frame: the same pose on both sides of the gt18 / gt19 cut)."""
    pigs = [C.actor("piglin", "gt1"), C.actor("piglin", "gt2"), C.actor("piglin_xbow", "gt3")]
    for k, (p, place) in enumerate(zip(pigs, GOLD), 1):
        C.stand(s, p, place, look=look, seed=k, idle=idle)
    return pigs


def gt01_landing(st, s, C, nar):
    """BEAT 1  "In this bastion, I'm the only one who doesn't like gold."   frames 1-97 (97 f, 4.04 s), sky wastes.
    Words: In 8, this 10, bastion 15, I'm 39, the 43, only 46, one 55, who 60, doesn't 63, like 70, gold 77. The
    film's first frame: something must already be moving on frame 1 (the push).

    STORY: Low long-lens portrait from the guard landing, slow push in. The piglin brute stands dead still at frame
    left on blackstone, looking just past the lens, a golden axe in his hand that nobody ever mentions. Far behind
    and below him, soft and glowing under a lantern, three piglins stand with their backs to him, facing a wall of
    gold blocks. Lava glow from below. The courtyard floor is whole: no pit yet.
    Cast: piglin brute (narrator), three piglins. Effects: golden axe (held), wall of gold blocks, lantern as key
    light on the brute, lava glow from below, slow push in.

    MUST BE SEEN, ON WHICH WORD
      frame 1         the brute big at frame left, already in the push; the gold wall and three backs beyond
      "gold" 77       the gold wall readable as gold (hue 38-58, nether.check_still), the brothers' backs to him
    NOW: this shot's own camera LANDING_CAM (the set's six_landing moved into the landing's north-west corner,
      (0.15, 17.8, 5.8), 20 mm f/2.8 at eye level), a slow LINEAR push of 0.33 block straight at the brute (his face
      grows 129 -> 147 px over the shot: moving on frame 1); the brute at LANDING_BRUTE (2.72, 16.75) near the
      landing's north-east corner, facing the lens, looking just past it (LANDING_LOOK), dead still but his ears;
      the three piglins re-spaced along the gold (LANDING_PIGS (7.35, 12.4), (6.95, 11.8), (7.35, 10.45), facing east,
      idle) so they stand clear to the right of his body; the lead's fill C.key_landing(s). Hero: the brute.
      THE FIX (the ear): from the stub's spot 2.4 blocks off a 26 mm lens, his head with its ears (1.0 block wide) and
      the three piglins did not both fit inside x 8-82 %; the camera went back into the corner (2.77 blocks from him),
      to 20 mm, and the push now runs along the line to him instead of across it (it carried him left).
    MEASURED (tools.sixseconds_geo gt01_landing:1 / :97; still out/test/sixseconds_gate_gt01_landing_77_zones.png):
      his head (ears included) x 14.4..52.6 % on frame 1 and x 10.3..53.7 % on 97, y 26-41 %; eyes x 33 %, y 32-33 %;
      face 129 -> 147 px, 13 degrees off the lens. The piglins' heads x 54-77 %, y 52.5-59 % (backs and profiles,
      83-140 degrees off), the gold wall beside his right arm and behind the piglins (x 50-80 %, y 40-55 %), the
      golden axe at his right hand (x 15-20 %, y 52-65 %). Preview frames 1-97: the push reads (1 against 97).
      Palette 77 (out/test/sixseconds_pal_gt01_landing_77.png): brute x 19-49 %, y 27-40 %, 100 % in the safe area,
      x 2.43 the blackstone (with KEY_LANDING), gold hue 45 s 0.80: all pass.
    FALLBACKS TAKEN (the set's): not the scripted LOW LONG lens (the landing is 3 blocks wide; a lower lens loses
      the piglins behind its edge: nether's note, ray-checked); the "lantern as key" is the film-local fill
      KEY_LANDING (the Bastion has no edit hook for a lantern block). Lava glow from below: only the look's
      under-light; no lava is in this frame.
    NEIGHBOURS: the film's first shot; after, rw02_ingots (the ingot row, the brothers admiring).
    """
    brute = C.actor("brute", "gt")
    C.stand(s, brute, LANDING_BRUTE, toward=LANDING_CAM["pos"], look=LANDING_LOOK, idle=False)
    pigs = [C.actor("piglin", "gt1"), C.actor("piglin", "gt2"), C.actor("piglin_xbow", "gt3")]
    for k, (p, place) in enumerate(zip(pigs, LANDING_PIGS), 1):
        C.stand(s, p, place, yaw=C.yaw("six_b1_pig_%d" % k), look="gold_target", seed=k)
    C.cam(s, None, focus=brute.head, ease="linear", **LANDING_CAM)
    C.key_landing(s)
    st.hero(s, "brute", brute)
    C.lights(s, "home")


def gt03_guard(st, s, C, nar):
    """BEAT 3  "Somebody has to guard the place."   frames 179-239 (61 f, 2.54 s), sky wastes.
    Words: Somebody 181, has 196, to 201, guard 204, the 213, place 215 (ends 226: 13 frames of hold).

    STORY: The gate frame (returns three times): static wide from low at the near end of the courtyard, composed for
    the tall frame. Far and high, the gateway with the glow of the entrance corridor beyond it. On the guard landing
    beside it the brute stands alone in profile, axe in hand, facing the open gateway. Nearer and lower, every piglin
    faces the gold wall, backs to the door. No pit. Hold long enough for the frame to be learned.
    Cast: piglin brute, three piglins. Effects: golden axe, blackstone gateway, guard stair and landing, gold-block
    wall, static gate frame camera preset re-used in sentences eighteen, nineteen (and twenty-three: replaced by the
    story's fallback, rw23).

    MUST BE SEEN, ON WHICH WORD
      the whole shot  THE GATE FRAME learned: gateway and glow, the brute in profile on the landing, the piglins'
                      backs to the door at the gold, the floor whole
      "guard" 204     the brute on guard, still (ears, a breath: not a statue)
    SHARED: CAMS["gate"] exactly (C.cam(s, "gate")); PLACES "landing" (+ look "landing_look_gate": the gateway's
      mouth: his head 88 degrees off the lens, a clean profile); "gold_1".."gold_3".
    NOW: the gate frame exactly; the piglins idle (glances, arm bob, ears). The brute's one action is the beat's:
      on the cut ("Somebody") his eyes are down on his brothers at the gold (GUARD_DOWN: his face turns toward the
      lens, three-quarter), on "has" (196) his head turns up to the gateway's mouth and arrives ON "guard" (204): the
      clean profile, then dead still but his ears to the cut (the brothers are busy with gold, so he watches the
      door). Something moves on frame 1: the piglins' ears and arms, the lava's animated surface in the gateway.
      Hero: the brute.
    MEASURED (stills out/test/sixseconds_gate_gt03_guard_183.png (eyes down, face to the lens) and _212.png (profile);
      preview frames 179-239): the turn reads at phone size on the 196-204 frames; brute head x 20-24 %, y 32-36 %
      (10 % of the frame height). Palette 212 (out/test/sixseconds_pal_gt03_guard_212.png): brute x 20-24 %,
      y 32-36 %, 100 % in the safe area, gold hue 44 s 0.79, piglin skin hue 21 s 0.59: all pass.
    NEIGHBOURS: before, rw02_ingots; after, gt04_runin (inside the gateway, the runner comes at the lens).
    """
    f0, f1 = s.frame_start, s.frame_end
    brute = C.actor("brute", "gt")
    C.put(brute, f0, "landing")
    brute.look_at(f0, Vector(GUARD_DOWN), ease=0)            # on the cut: his eyes on the brothers at the gold ...
    turn = C.at(s, "has")
    brute.look_at(turn, Vector(C.P("landing_look_gate")), ease=C.at(s, "guard") - turn)    # ... to the gateway
    brute.flop_ears(f0, f1 + 1)
    st.use(s, brute)
    _gold_piglins(st, s, C)
    C.cam(s, "gate")
    st.hero(s, "brute", brute)
    C.lights(s, "home")


def gt04_runin(st, s, C, nar):
    """BEAT 4  "One day, a player ran in."   frames 240-281 (42 f, 1.75 s), sky wastes.
    Words: One 242, day 248, a 253, player 254, ran 263, in 270 (ends 276).

    STORY: Ground-level wide lens just inside the gateway: the player (Steve skin, no armor except golden boots,
    iron pickaxe in hand) sprints through the gateway straight at the camera and past it. Small on the landing above
    and behind him, the brute turns his whole body to follow.
    Cast: the player (Steve skin, golden boots), piglin brute (background). Effects: golden boots (worn), iron
    pickaxe (held), sprint cycle, golden axe, body turn on the brute.

    MUST BE SEEN, ON WHICH WORD
      frame 240       the runner already moving at speed in the corridor, just beyond the gateway
      "player" 254    he is through the gateway, coming at the lens, golden boots, pickaxe in hand
      "ran in" 263-276  he passes the lens on its LEFT side and is out of the frame by about 273 (never in the last 3
                      frames); the brute on the landing turns his whole body to follow him (Character.face on "ran")
    NOW: the set's six_inside_gate camera (24 mm f/4 on the floor inside the gateway at (4.9, 11.0, 0.3)); the runner
      SPRINT-JUMPING from 240 (ramp=False: at speed) on RUN_IN (4.5, 21.6) -> (4.4, 18.5) -> (3.9, 11.0) -> (3.7, 8.0):
      through the gateway and past the lens 1.0 block west of it, iron pickaxe in hand from 240. The brute on
      "landing" looking at the gateway; his HEAD picks the runner up as he comes through the gateway under the landing
      and follows him down (RUN_IN_WATCH 248-266, clamped at 40 degrees down), then his whole BODY turns after him
      (Character.face 266-276, RUN_IN_TURN): the head leads, the body follows, as a mob's does. Focus on the runner's
      head, then racked to the brute's head on 268-271 (RUN_IN_RACK; on the runner's head the focus went behind the
      lens on 271-273: the whole frame a blur in the first preview). A neutral shadowless fill "gt_runin" (60 W at
      (5.8, 13.5, 2.6), RUN_IN_FILL) keeps his teal shirt teal in the lanterns' and lava's warm light. Hero: runner.
    THE TWO CHECKS: the first stub's sprint (5.6 blocks/s from (4.5, 24)) was still 3.6 blocks short of the lens on
      the last frame, and its line ran straight at the lens (a body and an arm through the camera). The lead kept the
      camera (from 3 blocks nearer the gateway the brute on the landing leaves the frame) and made the run fit:
      sprint-jump speed and a start 2.4 blocks nearer.
    MEASURED (tools.sixseconds_geo --track runner_gt:240-281:2; preview frames 240-281 looked at one by one; still
      out/test/sixseconds_gate_gt04_runin_256_zones.png): on 240 he is small in the gateway's glow (eyes x 66 %,
      y 59 %, feet in the caption band), in the gateway on 248-250 ("a player" 253-254: through it, eyes y 47-53 %),
      big at the top of the frame on 262-266 ("ran" 263), out of the left edge on 269-270 ("in" 270); 270-281 the
      landing alone, sharp, the brute settling into his turn (his face to the lens, 8-13 degrees off, 51 px).
      Brute: 112 degrees off the lens on 240 (looking at the gateway), 34 on 256, 1-13 after the turn.
      Palette 248 / 256 / 262 (sixseconds_pal_gt04_runin_*.png): shirt hue 173 / 173 / 172 (170-196; 169 without the
      fill, a FAIL), trousers min channel 12 (>= 12), the runner 100 % in the safe area: all pass.
    NEIGHBOURS: before, gt03_guard; after, pt05_boots (the boot shot: his legs sprint in and skid; the pit
      sequence's runner_pt is pre-rolled into it).
    """
    f0 = s.frame_start
    runner = C.actor("runner", "gt")
    C.put(runner, f0, RUN_IN[0], toward=RUN_IN[1])
    runner.hold("iron_pickaxe", frame=f0)
    runner.sprint_jump(f0, RUN_IN, ramp=False)
    st.use(s, runner)
    brute = C.actor("brute", "gt")
    C.stand(s, brute, "landing", look="gateway", idle=False)
    # his head picks the runner up as he comes through the gateway under the landing and follows him down (clamped
    # at 40 degrees down: the game's limit); once the runner has passed the lens the whole body turns after him
    a, b = RUN_IN_WATCH
    brute.track(a, b, runner, step=2, ease=6)
    brute.face(b, Vector(RUN_IN[-1]), ease=RUN_IN_TURN)
    C.cam(s, "set:six_inside_gate", focus=runner.head)
    # once he is past the lens the focus is on the brute turning on the landing (on the runner's head it went to a
    # few centimetres behind the lens on 271-273: the whole frame a blur)
    C.rack(s, brute.head, RUN_IN_RACK, frames=3)
    C.fill("gt_runin", RUN_IN_FILL["pos"], RUN_IN_FILL["watts"], [s], color=RUN_IN_FILL["color"])
    st.hero(s, "runner", runner)
    C.lights(s, "home")


def gt17_waits(st, s, C, nar):
    """BEAT 17  "I started waiting at the gate."   frames 1073-1121 (49 f, 2.04 s), sky wastes.
    Words: I 1075, started 1078, waiting 1088, at 1098, the 1101, gate 1103 (ends 1113).

    STORY: Frontal portrait from the entrance corridor outside, slow push in: the brute steps into the middle of the
    gateway and plants himself there, facing out past the lens, axe lowered at his side, not raised. He stands frame
    left, as in the first shot of the film. Soft behind him, through the gateway, his brothers face their gold.
    Cast: piglin brute, three piglins (soft background). Effects: golden axe held low, one slow step into position
    (at least seven frames), gateway as a frame around him, corridor lava glow as his key light, slow push in.

    MUST BE SEEN, ON WHICH WORD
      frame 1073      the push already moving; the brute one step short of his place (Piglin.walk: a step of 7+
                      frames, speed about 1.2, gait planted: a slow heavy step, not a hop)
      "waiting" 1088  planted in the middle of the gateway, axe LOW (never aggro), settled: the story's risk is
                      that this reads as an ambush; a slow, calm stance answers it
    SHARED: PLACES "gateway" (where he plants himself, facing out: yaw pi; gt18 has him there too), "gold_1".."3".
    NOW: this shot's own camera WAIT_CAM (nether's corridor camera, 35 mm f/2.4 from (3.6, 25.5, 1.55) in the
      corridor) with a slow push in of 0.75 block (ease out: at speed on 1073); the brute's ONE SLOW STEP into the
      gateway: brute_gt is not in fl16_home (brute_fl is), so his walk is pre-rolled 8 frames: placed on 1065 at
      WAIT_FROM (4.5, 18.0) facing out, Piglin.walk to PLACES "gateway" (4.5, 19.0) at 1.2 blocks/s with swing 0.5
      (piglins.py's slow heavy brute, planted gait: the feet do not slide); his head on WAIT_LOOK, just past the lens's
      right side; the axe low at his side (never aggro); ears from the end of the walk. The piglins at gold_1..3 idle,
      soft through the gateway at the left. Hero: the brute.
    MEASURED (tools.sixseconds_geo --track brute_gt:1066-1094:2; stills out/test/sixseconds_gate_gt17_waits_1073.png,
      _1095_zones.png; preview frames 1073-1121): on 1073 he is mid-step at y 18.3 (0.3 block short), planted on
      1089-1090 (y 18.99 on "waiting" 1088: the brake), then still; head x 24-49 % -> 16-48 %, y 40-50 %, eyes x
      36 -> 32 %, face 81 -> 102 px, 7-8 degrees off the lens; the axe at x 15-20 %, y 56-66 %. Brothers: piglin_gt1
      x 11-21 % and the crossbow piglin at the left edge (x -2..13 %), soft; piglin_gt2 hidden behind his head.
      Palette 1095 (out/test/sixseconds_pal_gt17_waits_1095.png): brute x 23-41 %, y 41-49 %, 100 % in the safe
      area, x 4.59 the blackstone (the corridor lava is his key): pass.
    NEIGHBOURS: before, fl16_home (the home flash: the brute at home_flash with the gateway behind him, a puff);
      after, gt18_nocome (THE GATE FRAME: he waits small in the gateway, his back to us).
    """
    f0, f1 = s.frame_start, s.frame_end
    brute = C.actor("brute", "gt")
    # brute_gt is not in fl16_home (brute_fl is): his one slow step is pre-rolled so that it is under way on 1073
    pre = f0 - WAIT_PREROLL
    C.put(brute, pre, WAIT_FROM, yaw=C.yaw("gateway"))
    brute.look_at(pre, Vector(WAIT_LOOK), ease=0)
    end = brute.walk(pre, [WAIT_FROM, C.P("gateway")], speed=WAIT_SPEED, swing=0.5)
    C.memo["gt_wait_planted"] = end
    brute.flop_ears(end, f1 + 1)
    st.use(s, brute)
    _gold_piglins(st, s, C)
    C.cam(s, None, focus=brute.head, **WAIT_CAM)
    st.hero(s, "brute", brute)
    C.lights(s, "home")


def gt18_nocome(st, s, C, nar):
    """BEAT 18  "One day, he didn't come."   frames 1122-1179 (58 f, 2.42 s), sky wastes.
    Words: One 1124, day 1130, he 1137, didn't 1140, come 1146 (ends 1156: 23 frames of hold, a full second).

    STORY: The gate frame from sentence three, same camera: the guard landing is empty. The brute stands small in the
    gateway with his back to us, a still silhouette with ears and axe against the glow of the empty corridor. His
    brothers face the gold. No pit. Hold a full second after the words. Nothing moves but the flicker of the lava
    glow.
    Cast: piglin brute (silhouette in the gateway), three piglins. Effects: gate frame camera preset, empty guard
    landing, lava glow flicker, hold after the line.

    MUST BE SEEN, ON WHICH WORD
      the whole shot  THE GATE FRAME; the landing EMPTY; the brute a silhouette in the gateway (back to us)
      "come" 1146 .. 1179   the hold: nothing moves but the flicker (bas.lava_flicker) and, at most, the ears
    SHARED: CAMS["gate"] exactly; PLACES "gateway", "gold_1".."gold_3".
    THE MATCH CUT INTO gt19 (the story's turn: "the match cut must be pixel-exact so the brute pops out of an
      otherwise identical frame"): on 1180 only the brute is gone (and the runner is a small figure in the corridor:
      see gt19). So the piglins stand in the same places in the same pose on 1179 and 1180: the stub places the SAME
      instances piglin_gt1..3 ONCE, here, and keys their ears (flop_ears) from 1122 through gt19's last frame; gt19
      only st.use()s them (the technical check: placing them again in gt19 restarted flop_ears, the ears jumped
      0.07 rad on the cut against 0.002-0.003 a frame before it). The camera drifts on (one seed), and the lava light
      does not jump: one bas.lava_flicker(1122, 1289) over both shots.
    NOW: the gate camera exactly; the brute on "gateway" facing out (back to the lens), the same pose and look as at
      the end of gt17, still but his ears; the piglins at the gold looking at it, ears only, placed ONCE here for both
      shots (C.memo["gt_gold_piglins"]); ONE bas.lava_flicker over gt18 AND gt19. Moves on 1122: the flicker, the
      ears, the lava's surface, the handheld. Hero: the brute.
    MEASURED (out/test/sixseconds_set_b18_gate.png): brute x 35-40 %, y 54-55 %, 1.59 x the blackstone (rule 1.5:
      at the limit; the flicker's dark phase may drop him under it: measure the darkest frame).
      THE LEAD (old timeline, 7 frames earlier: 1166 / 1172 there = 1173 / 1179 here): the flicker runs on across
      the cut and is NOT reset by gt19's C.lights call; its darkest frame in gt18 was 1166 (now 1173): brute x 1.69 /
      x 1.75 the blackstone, gold hue 44, piglin skin s 0.58: all pass (out/test/sixseconds_pal_gt18_nocome_1166.png,
      _1172.png).
      THE REVIEW PASS (stills out/test/sixseconds_scout_gt18_nocome_1179.png | sixseconds_scout_gt19_older_1180.png):
      outside the gateway's column (x 25-55 %) the two frames differ by a mean of 0.18 / 255 (max 25: the handheld's
      sub-pixel drift), over the piglins 0.21 / 255: the frame holds; the brute's body was at x 33.2-42.1 % on 1179.
    NEIGHBOURS: before, gt17_waits; after, gt19_older (the match cut).
    """
    brute = C.actor("brute", "gt")
    C.stand(s, brute, "gateway", look=(4.5, 26.0, 1.9), idle=False)
    # the three piglins are placed ONCE for gt18 AND gt19, their ears flop on through the match cut (the technical
    # check: gt19 placing them again restarted flop_ears, the ears jumped 0.07 rad on the cut); gt19 only uses them
    end19 = C.T["gt19_older"].frame_end
    pigs = [C.actor("piglin", "gt1"), C.actor("piglin", "gt2"), C.actor("piglin_xbow", "gt3")]
    for p, place in zip(pigs, GOLD):
        C.put(p, s.frame_start, place)
        p.look_at(s.frame_start, Vector(C.P("gold_target")), ease=0)
        p.flop_ears(s.frame_start, end19 + 1)
    st.use(s, *pigs)
    C.memo["gt_gold_piglins"] = pigs
    C.bas.lava_flicker(s.frame_start, end19)       # one flicker over both: no jump at the cut
    C.cam(s, "gate")
    st.hero(s, "brute", brute)
    C.lights(s, "home")


def gt19_older(st, s, C, nar):
    """BEAT 19  "He found an older version of the world, from before they added me."   frames 1180-1289 (110 f,
    4.58 s), sky wastes. Words: He 1182, found 1185, an 1195, older 1198, version 1209, of 1222, the 1225,
    world 1227, from 1247, before 1251, they 1260, added 1266, me 1275 (ends 1280).

    STORY: Hard match cut on the identical camera, not one block of the set changed: on the cut the brute is simply
    gone from the gateway. The player in golden boots sprints in through the gateway, straight through the spot where
    he stood, without slowing, and runs out of the bottom of the frame. The camera holds on the empty gateway and
    the empty landing.
    Location: the older version of the world: the home bastion set with no brute. Cast: the player (Steve skin,
    golden boots), three piglins (facing the gold). Effects: match cut with the gate frame camera preset, golden
    boots, iron pickaxe, sprint cycle, empty gateway and landing held at the end.

    MUST BE SEEN, ON WHICH WORD
      frame 1180      THE SAME FRAME as 1179 without the brute (see gt18's MATCH CUT note)
      "older" 1198 .. "version" 1209   the runner through the gateway, through the brute's spot, without slowing
      by "before" 1251  he is out of the frame (its LEFT edge: "the bottom of the frame" would take a run within a
                      block of the lens); then the empty gateway and the empty landing held under "before they added
                      me" (1250-1289, 40 frames)
    SHARED: CAMS["gate"] exactly; PLACES "gold_1".."gold_3" (the gt18 instances, untouched here).
    THE WORLD'S RULES: NO BRUTE (C.actor("brute", ...) must not be in this shot); the floor whole.
    NO HIDDEN START (ray-checked; seen on the stills): the gate camera sees the whole corridor walkway (x 3..6 between
      the lava channels, up to the lava wall at y 33) through the gateway, and behind the jambs there is only lava,
      so on 1180 the runner is already a figure in the corridor. ACCEPTED by the lead (the technical check left it to
      him), and judged by the gate director in the preview: every figure in the corridor lands at x 43-48 % of the
      frame (its vanishing point is x 43.6 %), right of the brute's former silhouette (x 33-42 %), so the only choice
      is its size: the further back, the smaller, the more it reads as somebody far away coming in, and the later he
      leaves. With the faster left exit (below) he starts 0.9 block further back than the lead's stub and still
      leaves sooner. On the preview the cut reads: a dark silhouette with ears gone, a small teal figure hopping far
      down the corridor. The invisible split (two shots on CAMS["gate"]) is not open to a sequence director (no
      st.shot); it stays the lead's option if a viewer still reads it as a transformation.
    NOW: the gate camera exactly; the runner SPRINT-JUMPING from 1180 (ramp off: at speed) on RUN_PAST (5.65, 26.4)
      -> the brute's spot (4.5, 19) -> (3.55, 10.2) -> (2.45, 6.0) -> (2.4, -1.2), iron pickaxe in hand from 1180: on
      the cut a small figure far down the corridor's east side, through the brute's spot without slowing, then down
      the courtyard's WEST side along the landing's foot and out of the frame's LEFT edge, ending behind the camera's
      plane. The piglins of gt18 (nothing re-keyed on the cut); from 1216 the crossbow piglin's head follows him over
      its shoulder (its face to the lens, clamped at 75 degrees: piglins look at a player near them, and this one wears
      gold) and is back on the gold by 1247 (GLANCE). Hero: the runner.
      WHY THE LEFT EXIT (the story check asked for the exit by about 1244, with "from before they added me" over the
      empty frame): the right edge is reached only near the lens (the gold piglins stand on that side), so the stub's
      right exit took 49 frames from the spot; the left one takes 43, which let the start move 0.9 block further down
      the corridor (smaller on the cut) and still clear the frame a little sooner (1250 against 1251-1252). pt20 (the pit camera) then
      finds him at the pit's west rim, the way he was running.
    MEASURED (tools.sixseconds_geo --sky wastes gt19_older:1180 --track runner_gt:1180-1252:1; preview frames
      1176-1289 looked at; stills out/test/sixseconds_gate_gt18_nocome_1179.png | sixseconds_gate_gt19_older_1180.png,
      _1240_zones.png): on 1180 his head x 44.6-47.7 %, y 53.7-55.2 % (16 px, 25.4 blocks off), beside the brute's
      former silhouette (x 33-42 % on 1179), not in it; in the brute's spot on 1206-1207 (between "older" 1198 and
      "version" 1209); eyes x 26 % on 1229, x 8.7 % on 1242; his body leaves the left edge on 1246-1247 and nothing of
      him is in the frame from 1250 (measured on the preview frames, motion blur included: his trailing leg is a
      sliver at the left edge on 1248-1249), during "from" (1247-1250): "before they added me" plays over the empty
      gateway and landing, 40 frames to the cut. Closest to a gold piglin: about 2.6 blocks (gold_2). The match cut (1179 against 1180, 540x960 16 samples): outside the gateway's
      column (x 25-55 %) the frames differ by a mean of 0.18 / 255 (piglins 0.23): only the brute is gone.
      Palette 1240 (out/test/sixseconds_pal_gt19_older_1240.png, the final run: he is leaving by the left edge, the
      crossbow piglin's face turned to him): shirt hue 173, trousers min channel 21, runner 89 % in the safe area (he is
      on his way out), gold hue 44 s 0.79, piglin skin hue 21 s 0.57: all pass.
    NEIGHBOURS: before, gt18_nocome (the match cut); after, pt20_likes (the pit camera: in that bastion, everyone
      likes gold).
    """
    f0 = s.frame_start
    runner = C.actor("runner", "gt")
    C.put(runner, f0, RUN_PAST[0], toward=RUN_PAST[1])
    runner.hold("iron_pickaxe", frame=f0)
    end = runner.sprint_jump(f0, RUN_PAST, ramp=False)
    C.memo["gt_runner_out"] = end
    st.use(s, runner)
    pigs = C.memo["gt_gold_piglins"]               # placed in gt18 for both shots: nothing re-keyed on the cut ...
    st.use(s, *pigs)
    # ... but as he runs past, the crossbow piglin turns its head over its shoulder after him (piglins look at a
    # player near them; one in gold boots is one of them), its face to the lens, and goes back to the gold before
    # "from": the hold on the empty gateway is still again (flicker and ears). (piglin_gt2's head would turn away
    # from the lens: its back stays to us.)
    a, b = GLANCE
    pigs[2].track(a, b, runner, step=2, ease=8)
    pigs[2].look_at(b + 1, Vector(C.P("gold_target")), ease=8)
    C.cam(s, "gate")
    st.hero(s, "runner", runner)
    C.lights(s, "home")
