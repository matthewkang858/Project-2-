"""Six Seconds, sequence GATE: the guard landing, THE GATE FRAME, the gateway seen from the corridor. Beats 1, 3, 4,
17, 18, 19 (shots gt01_landing, gt03_guard, gt04_runin, gt17_waits, gt18_nocome, gt19_older), sky "wastes" (the home
bastion's dark red; gt19 is "the older version of the world": the SAME sky and set, block for block). One function
per shot; the contract is in films/sixseconds_common.py (tags "gt...", C.actor, C.cam, C.lights, st.use / st.hero).

STATUS: STUBS by the lead director, revised in the lead's review pass (two independent checks: gt04's run, gt18 /
gt19's piglins over the match cut, gt19's path and exit). Each function puts the shot's camera on its place and its
cast roughly where the story wants them (no acting beyond what a still needs); the docstrings say what the shot must
become. Everything here may be rewritten except what SHARED below names.

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
TAGS TAKEN by the stubs: brute_gt (gt01, gt03, gt04, gt17, gt18), piglin_gt1 / piglin_gt2 / piglin_xbow_gt3 (gt01,
  gt03, gt17, gt18, gt19; C.memo["gt_gold_piglins"]), runner_gt (gt04, gt19). A new twin: gt4, gt5 ...
PREVIEW samples of this sequence: 5 (films/sixseconds_common.py PREVIEW_SAMPLES).
"""
from mathutils import Vector

GOLD = ("gold_1", "gold_2", "gold_3")
# gt04: the runner is already sprint-jumping in the corridor on 240 (ramp off: at speed), comes through the gateway
# and passes the lens 1.0 block WEST of it (the camera is at x 4.9): he leaves the frame's left edge before the lens
# instead of running into it (the technical check: the first stub's line ran straight at the lens).
RUN_IN = [(4.5, 21.6, 0.0), (4.4, 18.5, 0.0), (3.9, 11.0, 0.0), (3.7, 8.0, 0.0)]
# gt19: on the match cut the runner is a small figure on the corridor's EAST side (the gate camera sees the whole
# corridor: nowhere to hide him), sprint-jumping already; he is in the brute's spot (4.5, 19) on "older", then runs
# down the courtyard between the gold piglins and the pit side and out of the frame's right edge by "before" (1251),
# so "they added me" plays over the empty gateway. The path after the spot is NOT nether's home_run_past (its leg
# (4.5, 19) -> (6.4, 9) runs through piglin_gt2 at gold_2 (6.3, 11.2): the technical check, frames 1235-1238):
# (5.0, 12) -> (6.9, 3.5) keeps clear of gold_1..3 and turns him out of the frame's right edge sooner; the last leg
# runs past the gate camera's right side, 2 blocks clear of it, behind its plane.
RUN_PAST = [(5.7, 25.5, 0.0), (4.5, 19.0, 0.0), (5.0, 12.0, 0.0), (6.9, 3.5, 0.0), (7.4, -1.0, 0.0)]


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
      y 15-36 %, 92 % inside the safe area at the push's middle; piglin heads y 52-55 %; gold hue 46.
      THE LEAD'S GEO (tools.sixseconds_geo gt01_landing:2 / :77, the stub as it is): his head x -3.4..54.5 % on frame
      2 and x -9.9..55.6 % on "gold" (77): the push carries his far ear OUT of the left edge (face 195 -> 215 px,
      18 degrees off the lens, eyes x 24-26 %, y 23-25 %). Fix before anything else: put him a little further from
      the lens's left edge (or end the push earlier / aim it a little left) so his whole head stays inside x 8 % to
      the last frame. The three piglins: heads x 54-85 %, y 50-59 %, 9.7-11.2 blocks off (backs and profiles, 72-114
      degrees off the lens: no faces), the step ingot spot hidden behind piglin_gt1 (no ingot is in this shot).
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
      frame 240       the runner already moving at speed in the corridor, just beyond the gateway
      "player" 254    he is through the gateway, coming at the lens, golden boots, pickaxe in hand
      "ran in" 263-276  he passes the lens on its LEFT side and is out of the frame by about 273 (never in the last 3
                      frames); the brute on the landing turns his whole body to follow him (Character.face on "ran")
    NOW (stub): the set's six_inside_gate camera (24 mm f/4 on the floor inside the gateway at (4.9, 11.0, 0.3),
      nether's inside_gate pulled back 2.2 blocks); the runner SPRINT-JUMPING from 240 (ramp=False: at speed) on
      RUN_IN (4.5, 21.6) -> (4.4, 18.5) -> (3.9, 11.0) -> (3.7, 8.0): through the gateway and past the lens 1.0 block
      west of it; the brute on "landing", his body turned toward the courtyard on "ran". Hero: the runner.
    THE TWO CHECKS: the first stub's sprint (5.6 blocks/s from (4.5, 24)) was still 3.6 blocks short of the lens on
      the last frame, and its line ran straight at the lens (a body and an arm through the camera). The lead kept the
      camera (from 3 blocks nearer the gateway the brute on the landing leaves the frame: 36 degrees left of the
      lens's axis, measured on paper) and made the run fit: sprint-jump speed and a start 2.4 blocks nearer.
    MEASURED (the lead's probe of the run; still out/test/sixseconds_scout_gt04_runin_262_zones.png): his feet at
      y 18.3 on 250 (in the gateway on "a player"), y 17.2 on 254 ("player"), y 12.8 on 268; his body fills the
      frame on 266-270 (mid-hop, close to the low lens) and has left the frame's left edge by 273-274; nothing of him
      after 274. On 240 his body is at x 60-72 %, y 57-67 % (small, in the gateway's glow: his feet in the caption
      band); on 262 he is big at the top right, mid-hop, head under the top icons. The brute on the landing is small
      at the upper left (check his turn reads: his body turns about 80 degrees on 263-273).
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
    brute.face(C.at(s, "ran"), Vector((3.9, 11.0, 1.0)), ease=10)      # his whole body turns to follow
    C.cam(s, "set:six_inside_gate", focus=runner.head)
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
    NOW (stub): engine/nether.py's corridor camera (35 mm f/2.4 from the corridor, no push yet), the brute standing
      on "gateway" facing out, the piglins at the gold. Hero: the brute.
    MEASURED (out/test/sixseconds_set_b17_corridor.png; the lead's out/test/sixseconds_scout_gt17_waits_1096.png on
      the old timeline, 7 frames earlier): brute x 26-42 %, y 42-49 %, 4.19 x the blackstone with the corridor lava
      as his key; the brothers soft beyond.
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
    NOW (stub): the gate camera, the brute on "gateway" facing out (back to the lens), still; the piglins at the gold
      looking at it, ears only, for both shots (C.memo["gt_gold_piglins"]); ONE bas.lava_flicker over gt18 AND gt19.
      Hero: the brute.
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
      by "before" 1251  he is out of the frame (its RIGHT edge: the gate camera's floor is out of reach of "the
                      bottom of the frame": it would take a run within a block of the lens); then the empty gateway
                      and the empty landing held under "before they added me" (1251-1289, 39 frames)
    SHARED: CAMS["gate"] exactly; PLACES "gold_1".."gold_3" (the gt18 instances, untouched here).
    THE WORLD'S RULES: NO BRUTE (C.actor("brute", ...) must not be in this shot); the floor whole.
    NO HIDDEN START (ray-checked; seen on the stills): the gate camera sees the whole corridor walkway (x 3..6 between
      the lava channels, up to the lava wall at y 33) through the gateway, and behind the jambs there is only lava,
      so on 1180 the runner is already a figure in the corridor. ACCEPTED by the lead (the technical check left it to
      him): he is on the corridor's EAST side, his body at x 43-50 % on 1180, beside the brute's former silhouette
      (x 33-42 % on 1179), not in it; he is moving at speed (mid-hop), and a teal shirt is not a brute. The start
      trades size against the exit: from (5.7, 29.5) (the first stub's, x 45-47.5 %, smaller) he left the frame only
      about 1258, on "they"; from RUN_PAST's (5.7, 25.5) he is out by 1250-1251, on "before". If the cut reads as
      "the brute turned into Steve" in the preview, start him further back (a later exit) or split gt19 at about
      1186 into two shots on CAMS["gate"] with the same seed (invisible: the drift follows the frame) and let him
      enter the corridor in the second only (he then appears 30 blocks off: check that it is not a pop).
    NOW (stub): the gate camera; the runner SPRINT-JUMPING from 1180 (ramp off: at speed) on RUN_PAST (5.7, 25.5) ->
      the brute's spot (4.5, 19) -> (5.0, 12) -> (6.9, 3.5) -> (7.4, -1.0), iron pickaxe in hand; the piglins of gt18
      (nothing re-keyed). Hero: the runner. NOT nether's home_run_past (its leg (4.5, 19) -> (6.4, 9) runs THROUGH
      piglin_gt2 at gold_2 (6.3, 11.2) on 1235-1238 of the old timeline: the technical check; the stub's first fix
      had it).
    MEASURED (the lead's probe of the run; stills out/test/sixseconds_scout_gt19_older_1180_zones.png and the match
      pair above): in the brute's spot on 1201 (0.15 from it; "older" 1198, "version" 1209); closest to a gold
      piglin 1.1 block (gold_2, about 1226; about 1.7 from gold_1, 2.3 from gold_3); his body leaves the right edge
      on 1249-1251 (the left edge of his box at x 84 % on 1249, out of the frame on 1252); the last leg passes 2
      blocks from the gate camera, behind its plane. Track: $BPY -m tools.sixseconds_geo --sky wastes gt19_older:1180
      --track runner_gt:1180-1289:3.
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
    st.use(s, *C.memo["gt_gold_piglins"])          # placed in gt18 for both shots: nothing re-keyed on the cut
    C.cam(s, "gate")
    st.hero(s, "runner", runner)
    C.lights(s, "home")
