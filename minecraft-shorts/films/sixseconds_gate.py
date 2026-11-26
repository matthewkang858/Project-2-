"""Six Seconds, sequence GATE: the guard landing, THE GATE FRAME, the gateway seen from the corridor. Beats 1, 3, 4,
17, 18, 19 (shots gt01_landing, gt03_guard, gt04_runin, gt17_waits, gt18_nocome, gt19_older), sky "wastes" (the home
bastion's dark red; gt19 is "the older version of the world": the SAME sky and set, block for block). One function
per shot; the contract is in films/sixseconds_common.py (tags "gt...", C.actor, C.cam, C.lights, st.use / st.hero).

STATUS: STUBS by the lead director. Each function puts the shot's camera on its place and its cast roughly where the
story wants them (no acting beyond what a still needs); the docstrings say what the shot must become. Everything
here may be rewritten except what SHARED below names.

THE PLACE (engine/nether.py HOME; out/test/nether_map_home.png): the courtyard x 0..8, y -2..17, floor z 0; the
GATEWAY x 3..5 in the north wall (y 18..20), 5 high, the entrance corridor y 21..32 beyond it with lava channels and
a lava wall at y 33 (the orange glow; bas.lava_flicker); the GUARD STAIR x 0..1 along the west wall (y 6..9) up to
the LANDING x 0..2, y 10..17, standing height 4, beside the gateway's west jamb; the GOLD WALL x 9, y 9..15 with its
step at x 8. Lanterns: home_landing, home_gate (two, either side of the gateway), home_gold, home_pit.
SHARED (films/sixseconds_common.py): CAMS["gate"] in gt03, gt18 and gt19 EXACTLY, its handheld and seed included
  (the drift runs on across the 18 -> 19 match cut); PLACES "gold_1".."gold_3" (the three piglins at the gold, also
  pt05's starting places) IDENTICAL in gt18 and gt19; PLACES "landing" (gt03, gt04), "gateway" (gt17, gt18).
THE WORLD'S RULES that bite here: the floor is WHOLE in every one of these shots (no C.pit); the brute is ABSENT
  from gt19 (NO_BRUTE_SHOTS); the runner wears the golden boots and holds the iron pickaxe.
TAGS TAKEN by the stubs: brute_gt (gt01, gt03, gt04, gt17, gt18), piglin_gt1 / piglin_gt2 / piglin_xbow_gt3 (gt01,
  gt03, gt17, gt18, gt19), runner_gt (gt04, gt19). A new twin: gt4, gt5 ...
PREVIEW samples of this sequence: 5 (films/sixseconds_common.py PREVIEW_SAMPLES).
"""
GOLD = ("gold_1", "gold_2", "gold_3")


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
    NOW (stub): the set's camera six_landing (26 mm f/2.8 at eye level on the landing's north-west corner, a slow
      push in to its pos1), the brute at PLACES "landing_edge" (six_landing_brute) looking at "landing_look" (just
      past the lens), dead still (ears only); the three piglins at six_b1_pig_1..3 facing the gold; the lead's fill
      C.key_landing(s) (his own key: x 2.41 against the blackstone, 1.23 without it). Hero: the brute.
    MEASURED (films/sixseconds_set.py b01_landing, out/test/sixseconds_set_b01_landing_zones.png): brute x 2-49 %,
      y 15-36 %, 92 % inside the safe area (his far ear at the LEFT EDGE: move the brute or the lens a little so the
      whole head is inside x 8 %); piglin heads y 52-55 %; gold hue 46.
    FALLBACKS TAKEN (the set's): not the scripted LOW LONG lens (the landing is 3 blocks wide; a lower lens loses
      the piglins behind its edge: nether's note, ray-checked); the "lantern as key" is the film-local fill
      KEY_LANDING (the Bastion has no edit hook for a lantern block). Lava glow from below: only the look's
      under-light; no lava is in this frame.
    NEIGHBOURS: the film's first shot; after, rw02_ingots (the ingot row, the brothers admiring).
    """
    brute = C.actor("brute", "gt")
    C.stand(s, brute, "landing_edge", look="landing_look", idle=False)
    pigs = [C.actor("piglin", "gt1"), C.actor("piglin", "gt2"), C.actor("piglin_xbow", "gt3")]
    for k, p in enumerate(pigs, 1):
        C.stand(s, p, "six_b1_pig_%d" % k, look="gold_target", seed=k)
    C.cam(s, "set:six_landing", focus=brute.head, ease="linear")
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
    NOW (stub): exactly that; the piglins idle; the brute dead still but his ears. Hero: the brute.
    MEASURED (engine/nether.py and out/test/sixseconds_set_b03_gate.png): brute head x 20-24 %, y 32-36 % (10 % of
      the frame height), gold hue 43, piglin skin hue 21 s 0.60.
    NEIGHBOURS: before, rw02_ingots; after, gt04_runin (inside the gateway, the runner comes at the lens).
    """
    brute = C.actor("brute", "gt")
    C.stand(s, brute, "landing", look="landing_look_gate", idle=False)
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
      frame 240       the runner already sprinting in the corridor / gateway (at speed on frame 1)
      "player" 254    he comes through the gateway at the lens, golden boots flashing, pickaxe in hand
      "ran in" 263-276  he passes the lens (out of frame before the last 3 frames); the brute on the landing turns his
                      whole body to follow him (Piglin.place with a new yaw keyed as a turn, or walk a step)
    NOW (stub): the set's six_inside_gate camera (24 mm f/4 on the floor inside the gateway, nether's inside_gate
      pulled back 2.2 blocks); the runner sprinting from the corridor (4.5, 24) toward the lens; the brute on
      "landing" looking at the gateway. Hero: the runner.
    MEASURED (out/test/sixseconds_set_b04_inside_gate.png, the runner standing at home_gateway): his head x 62-67 %,
      y 54-57 %; he grows UP the frame as he nears the low lens; the brute small at the upper left.
    NEIGHBOURS: before, gt03_guard; after, pt05_boots (the boot shot: his legs sprint in and skid; the pit
      sequence's runner_pt is pre-rolled into it).
    """
    f0 = s.frame_start
    runner = C.actor("runner", "gt")
    a, b = (4.5, 24.0, 0.0), (4.6, 10.5, 0.0)
    C.put(runner, f0, a, toward=b)
    runner.walk(f0, [a, b], sprint=True, ramp=(False, False))
    st.use(s, runner)
    brute = C.actor("brute", "gt")
    C.stand(s, brute, "landing", look="gateway", idle=False)
    C.cam(s, "set:six_inside_gate", focus=runner.head)
    st.hero(s, "runner", runner)
    C.lights(s, "home")


def gt17_waits(st, s, C, nar):
    """BEAT 17  "I started waiting at the gate."   frames 1066-1114 (49 f, 2.04 s), sky wastes.
    Words: I 1068, started 1071, waiting 1081, at 1091, the 1094, gate 1096 (ends 1106).

    STORY: Frontal portrait from the entrance corridor outside, slow push in: the brute steps into the middle of the
    gateway and plants himself there, facing out past the lens, axe lowered at his side, not raised. He stands frame
    left, as in the first shot of the film. Soft behind him, through the gateway, his brothers face their gold.
    Cast: piglin brute, three piglins (soft background). Effects: golden axe held low, one slow step into position
    (at least seven frames), gateway as a frame around him, corridor lava glow as his key light, slow push in.

    MUST BE SEEN, ON WHICH WORD
      frame 1066      the push already moving; the brute one step short of his place (Piglin.walk: a step of 7+
                      frames, speed about 1.2, gait planted: a slow heavy step, not a hop)
      "waiting" 1081  planted in the middle of the gateway, axe LOW (never aggro), settled: the story's risk is
                      that this reads as an ambush; a slow, calm stance answers it
    SHARED: PLACES "gateway" (where he plants himself, facing out: yaw pi; gt18 has him there too), "gold_1".."3".
    NOW (stub): engine/nether.py's corridor camera (35 mm f/2.4 from the corridor, no push yet), the brute standing
      on "gateway" facing out, the piglins at the gold. Hero: the brute.
    MEASURED (out/test/sixseconds_set_b17_corridor.png): brute x 26-42 %, y 42-49 %, 4.19 x the blackstone with the
      corridor lava as his key; the brothers soft beyond.
    NEIGHBOURS: before, fl16_home (the home flash: the brute at home_flash with the gateway behind him, a puff);
      after, gt18_nocome (THE GATE FRAME: he waits small in the gateway, his back to us).
    """
    brute = C.actor("brute", "gt")
    C.stand(s, brute, "gateway", look=(4.5, 26.0, 1.9), idle=False)
    _gold_piglins(st, s, C)
    C.cam(s, "set:corridor", focus=brute.head)
    st.hero(s, "brute", brute)
    C.lights(s, "home")


def gt18_nocome(st, s, C, nar):
    """BEAT 18  "One day, he didn't come."   frames 1115-1172 (58 f, 2.42 s), sky wastes.
    Words: One 1117, day 1123, he 1130, didn't 1133, come 1139 (ends 1149: 23 frames of hold, a full second).

    STORY: The gate frame from sentence three, same camera: the guard landing is empty. The brute stands small in the
    gateway with his back to us, a still silhouette with ears and axe against the glow of the empty corridor. His
    brothers face the gold. No pit. Hold a full second after the words. Nothing moves but the flicker of the lava
    glow.
    Cast: piglin brute (silhouette in the gateway), three piglins. Effects: gate frame camera preset, empty guard
    landing, lava glow flicker, hold after the line.

    MUST BE SEEN, ON WHICH WORD
      the whole shot  THE GATE FRAME; the landing EMPTY; the brute a silhouette in the gateway (back to us)
      "come" 1139 .. 1172   the hold: nothing moves but the flicker (bas.lava_flicker) and, at most, the ears
    SHARED: CAMS["gate"] exactly; PLACES "gateway", "gold_1".."gold_3".
    THE MATCH CUT INTO gt19 (the story's turn: "the match cut must be pixel-exact so the brute pops out of an
      otherwise identical frame"): on 1173 only the brute is gone. So the piglins must stand in the same places in
      the same pose on 1172 and 1173 (the same instances piglin_gt1..3: place() them in gt19 where they are, and
      either no idle in either shot or one that does not change across the cut), the camera drifts on (one seed),
      and the lava light does not jump: one bas.lava_flicker(f0 of gt18, f1 of gt19) over both shots, or one that
      ends at its base level before the cut. Check frames 1172 and 1173 side by side.
    NOW (stub): the gate camera, the brute on "gateway" facing out (back to the lens), still; the piglins at the gold
      without glances (ears only: the same pose on both sides of the cut); ONE bas.lava_flicker over gt18 AND gt19.
      Hero: the brute.
    MEASURED (out/test/sixseconds_set_b18_gate.png): brute x 35-40 %, y 54-55 %, 1.59 x the blackstone (rule 1.5:
      at the limit; the flicker's dark phase may drop him under it: measure the darkest frame).
    NEIGHBOURS: before, gt17_waits; after, gt19_older (the match cut).
    """
    brute = C.actor("brute", "gt")
    C.stand(s, brute, "gateway", look=(4.5, 26.0, 1.9), idle=False)
    _gold_piglins(st, s, C, idle=False)
    C.bas.lava_flicker(s.frame_start, C.T["gt19_older"].frame_end)       # one flicker over both: no jump at the cut
    C.cam(s, "gate")
    st.hero(s, "brute", brute)
    C.lights(s, "home")


def gt19_older(st, s, C, nar):
    """BEAT 19  "He found an older version of the world, from before they added me."   frames 1173-1282 (110 f,
    4.58 s), sky wastes. Words: He 1175, found 1177, an 1188, older 1191, version 1202, of 1215, the 1218,
    world 1220, from 1240, before 1244, they 1253, added 1258, me 1268 (ends 1273).

    STORY: Hard match cut on the identical camera, not one block of the set changed: on the cut the brute is simply
    gone from the gateway. The player in golden boots sprints in through the gateway, straight through the spot where
    he stood, without slowing, and runs out of the bottom of the frame. The camera holds on the empty gateway and
    the empty landing.
    Location: the older version of the world: the home bastion set with no brute. Cast: the player (Steve skin,
    golden boots), three piglins (facing the gold). Effects: match cut with the gate frame camera preset, golden
    boots, iron pickaxe, sprint cycle, empty gateway and landing held at the end.

    MUST BE SEEN, ON WHICH WORD
      frame 1173      THE SAME FRAME as 1172 without the brute (see gt18's MATCH CUT note)
      "older version" 1191-1215   the runner comes through the gateway, through his spot, without slowing
      by "before" 1244  he is out of the frame (the bottom or the right edge: engine/nether.py's home_run_past
                      passes the gate camera's right side); then the empty gateway and the empty landing held
    SHARED: CAMS["gate"] exactly; PLACES "gold_1".."gold_3" (identical to gt18's); the path bas.paths
      ["home_run_past"] (lava wall -> gateway -> past the camera's right side).
    THE WORLD'S RULES: NO BRUTE (C.actor("brute", ...) must not be in this shot); the floor whole.
    NO HIDDEN START (ray-checked by the lead): the gate camera sees the whole corridor walkway (x 3..6 between the lava
      channels at x 2 and 6, up to the lava wall at y 33), so on 1173 the runner is already a figure in the corridor.
      Deep enough (y 27 or more: 26 blocks from the lens, small against the lava wall's glow) the gateway itself
      reads empty on the cut. Speedrunners sprint-JUMP (Player.sprint_jump: about 7 blocks/s against the sprint's
      5.6): from y 27 he passes the brute's spot about 1200 ("older version") and leaves the frame's right side
      about 1250, which leaves a hold on the empty gateway and landing.
    NOW (stub): the gate camera, the runner sprint-jumping from (4.5, 27) along home_run_past from the first frame,
      the piglins at the gold without glances (as in gt18). Hero: the runner.
    MEASURED (out/test/sixseconds_set_b19_gate.png, the runner standing at (5.6, 15.0)): x 45-51 %, y 54-56 %.
    NEIGHBOURS: before, gt18_nocome (the match cut); after, pt20_likes (the pit camera: in that bastion, everyone
      likes gold).
    """
    f0 = s.frame_start
    runner = C.actor("runner", "gt")
    path = [(4.5, 27.0, 0.0)] + [p for p in C.bas.paths["home_run_past"] if p[1] < 27.0]
    C.put(runner, f0, path[0], toward=path[1])
    end = runner.sprint_jump(f0, path, ramp=False)
    C.memo["gt_runner_out"] = end
    st.use(s, runner)
    _gold_piglins(st, s, C, idle=False)
    C.cam(s, "gate")
    st.hero(s, "runner", runner)
    C.lights(s, "home")
