"""Leg Day, sequence SQUARE: the village square in golden light. Beats 1, 2+3 (one take), 7, 8, 9, 10 (shots sq01_squats,
sq02_reps, sq07_bench, sq08_arms, sq09_lifts, sq10_cheating), sky "gold". One function per shot; the contract is in
films/legday_common.py (tags "sq...", C.actor / C.narrator, C.cam, C.lights, st.use / st.hero).

STATUS: STUBS written by the lead (camera from the set builder's suggestion, cast placed, the beat's action roughly
keyed so the film builds and renders end to end). Every docstring carries the beat, its words with their frames,
what must be seen on which word, the neighbours, the risks and the measured notes. The acting is yours.

THE PLACE (films/legday_set.py, its docstring "THE SQUARE"; anchors C.A[...], facings C.Y[...]):
  squats      the plaza south of the well (the well x -3..2, y -3..2; the bell on its south side; the two bell lamps
              at (-4, -4) and (0, -4) behind the squatters): squat_steve (-0.55,-5.55), squat_zuri (-1.75,-6.45),
              squat_ari (0.75,-6.35), all facing SOUTH (the lens); narrator_far (-6.0, 3.2) by his bench. Kai's lap: a
              ring round the well (the set builder's (1.3,-5.3)->(2.9,-3.0)->(3.6,0.4)->(2.4,3.6); the village's
              square_loop is wider).
  stone row   C.stones: eight engine.breaking Breakables (5, -16..-9, 0) on bare grass; [0] = the south one, mined
              first; mine_1 (4.22,-15.5) / mine_2 (4.22,-14.5) facing EAST (Steve west of the row); pickaxe_target
              (1.25,-14.5): 3 blocks behind his back, out of pick-up reach. The oak and the lamp post that stood in
              front of the row are gone. The stones are NOT registered with the Stage: they are part of the set in
              every shot, and stone 1 stays gone after sq02 (do not st.use them; their break keys persist).
  bench       C.bench (engine.redstone parts): torch spot (-6, 8, 0), dust (-6, 7..6, 0), repeater (-6, 5, 0) toward
              south, the lamp (-6, 4, 1) on a stone block, the piston (-5, 4, 0) facing east. bench_narrator
              (-7.3, 6.6) facing east. The honest circuit: t = C.bench["torch"].plant(f, player=efe);
              redstone.signal(t, C.bench["wire"], C.bench["repeater"], (C.bench["lamp"], C.bench["piston"])). From then
              on the lamp is lit (sq08 stands in front of it): key it ONCE, in sq07.
  arms        arms_narrator (-5.98, 3.15) / arms_steve (-5.02, 3.15) facing SOUTH, the lamp's centre (x -5.5) between
              their near arms
  column      C.column: piston up (-4, 9, 0), twelve iron blocks (-4, 9, 1..12) (kit movables), the floor lever on
              its pier (-4, 10, 1) facing north; t = redstone.flip_by(efe, C.column["lever"], f); C.column["piston"]
              .power(t) lifts the twelve one block in 2 ticks (key it ONCE, in sq09; it stays up after).
              column_steve (-5.25, 9.45) facing east, column_narrator (-2.95, 11.25), column_walk_end (-2.8, 5.4).
              redstone's Lever.stand() puts a body INTO the pier for this lever (the set builder's bug report): use
              column_narrator, checked clear.
THE SKY: "gold" (films/legday.py SKIES): the sun due EAST at 27 degrees: faces turned east or south are lit; a
  camera looking north or south has it 90 degrees off its axis. The anvil wall's south end is a grey slab beyond the
  houses in every northward view from the square (b02, b10): it is the set, keep it soft.
TAGS (twins): the stubs use steve_sq (sq01, with the anvil), steve_sq2 (sq02: pre-rolled, mining from frame -50),
  steve_sq3 (sq08 pre-rolled 8 frames, sq09, sq10: empty-handed; a held item stays on its instance),
  zuri_sq, ari_sq, kai_sq (sq01), efe_sq (the narrator with his torch: sq01, sq07, sq08, sq09, sq10), pickaxe
  iron_pickaxe_sq. A new twin: sq3, sq4 ...
LIGHT: C.lights(s, "gold", near=<point>, radius=10..14) (daylight; the bench lamp is a kit light, untouched by it).
PREVIEW samples for render.py previews: 5 (legday_common.PREVIEW_SAMPLES).
"""
import math

from engine import breaking, fx, redstone
from films import legday_common as LC

# ---------------------------------------------------------------------------------------------------------------
# this sequence's own cameras (starts: the set builder's suggestions, films/legday_set.py CAMERAS; yours to change)
# ---------------------------------------------------------------------------------------------------------------
SQ01_CAM = dict(LC._set_cam("b01"), pos1=(-0.55, -12.3, 0.34))          # + a slow push in (moving on frame 1)
# beats 2 and 3, one take: close on Steve punching the first stone (b02), then drifting back and round to the
# whole row with the pickaxe behind him (b03's pull-back)
SQ02_CAM = dict(pos=(7.0, -20.4, 0.8), target=(5.79, -15.55, 0.8), pos1=(1.4, -23.0, 1.25),
                target1=(3.9, -13.9, 0.7), lens=24.0, fstop=2.8)
SQ07_CAM = dict(LC._set_cam("b07"), pos1=(-1.0, 7.0, 1.35))
SQ08_CAM = dict(LC._set_cam("b08"), pos1=(-5.52, -0.45, 1.12))
SQ09_CAM = LC._set_cam("b09")                                             # a tilt up the column (target -> target1)
SQ10_CAM = dict(LC._set_cam("b10"), pos1=(-1.85, 3.5, 0.45))
KAI_LAP = [(1.3, -5.3, -0.06), (2.9, -3.0, -0.06), (3.6, 0.4, -0.06), (2.4, 3.6, -0.06)]
MINE_BREAK = "drops"          # the first stone bursts on this word (sq02): "It DROPS nothing"
MINE_FRAMES = breaking.break_frames("stone")   # click -> break of stone by hand: THE GAME'S 180 frames (7.5 s; the
#                               review: the first stub compressed it to 114, and punching stone being slow is the joke
#                               of the beat). The click is on frame -50 (a pre-roll before the film: the stone row is
#                               in no earlier frame); on frame 73 the cracks are at stage 6 of 10


def _stone(C, i):
    return C.stones[i]


def _begin_mining(player, block, f0, f_end):
    """A block only BEGUN: the player clicks it on f0 and holds the button to f_end (the game's crack stages for
    block and hand, the mining arm), then lets go off-screen: the cracks clear on f_end + 1 and the block stays (a
    block nobody breaks inside the shot is never keyed broken outside it)."""
    track = breaking.progress_track(block.block_id, "hand")
    cur = None
    for f in range(int(f0), int(f_end) + 1):
        done = min(int((f - f0) / breaking.TICK + 1e-6) + 1, len(track) - 1)
        stage = -1 if done < 1 else min(9, int(track[done - 1] * 10.0))
        if stage != cur:
            block.crack(f, stage)
            cur = stage
    block.crack(int(f_end) + 1, -1)
    return fx.mining_swings(player, f0, f_end)


def sq01_squats(st, s, C, nar):
    """BEAT 1  "In this town, everyone wants to get ripped."   frames 1-72 (72 f, 3.00 s), sky gold.
    Words: In 8, this 10, town 16, everyone 32, wants 42, to 49, get 51, ripped 57. The film's first frame: the
    HOOK (the Reel's thumbnail is near here).

    STORY: HOOK, about 2.8 s. Ground-level wide lens at the foot of the well, sun from the side. Steve, Zuri and Ari
    stand in a staggered row facing the lens, an anvil in each one's hand, and do squats in unison: the player sneak
    pose, down, up, down, exactly like players spamming crouch. Kai sprint-jumps a lap around the well behind them.
    Far back at the edge of the square, soft, the narrator stands perfectly still with a glowing redstone torch, the
    only one not moving. Steve's face upper middle of frame, anvils above the caption band.
    Cast: Steve, Zuri, Ari, Kai, Narrator (Efe, slim-arm model). Effects: three anvils as held items, redstone torch
    held and glowing, player sneak pose cycled as squats, sprint-jump cycle.

    MUST BE SEEN, ON WHICH WORD
      frame 1         already moving: the squat cycle under way (down on frame 1 or 2), Kai mid-hop, the camera on
                      its way (ease_out)
      "everyone" 32   all three squatters' faces readable (y 14-60 %, x 8-82 %), the anvils in their hands above the
                      caption band (y < 62 %)
      "ripped" 57     the squat in unison still going; the narrator soft and still at the back with the torch's glow
      the whole shot  the narrator NOT moving (he is placed, nothing else: no idle)
    SHARED: none. Anchors squat_steve / squat_zuri / squat_ari (facing south), narrator_far.
    NEIGHBOURS: the film's first shot; after, sq02_reps (Steve at the stone row: a new place, the same Steve).
    RISKS (story): "the sneak pose for players (squats in the hook ...) is new. Fallback for the hook: Draft 3's
      sprint-jump laps around the well with one anvil carrier walking at the lens." Players.sneak is built and
      proved (out/test/players_sneak_poses.png): the fallback is not needed unless the squat reads weakly from the
      front (the set builder: "the crouch reads weakly from the front": consider a camera a little higher, or 20-30
      degrees off the front, so the bend at the hips shows).
    MEASURED (the set builder, out/test/legday_set_b01_squats[_zones].png, stand-ins, sky gold): faces y 45 %, anvils
      54 %; the narrator small at x 12 % (further right the well hides him); Kai mid-jump at the right. THE LEAD:
      the lower half of that frame is empty dirt path (the camera at z 0.32 looking level from 7 blocks): fill it,
      lower the trio in the frame or come closer; the bell lamps stand behind the squatters' heads (tangents).
      THE LEAD'S SCOUT of the stub: out/test/legday_scout_sq01_squats_36[_zones].png (the same: faces y 38-42 %,
      the anvils at y 48 %, the lower 45 % empty path).
    NOW (stub): SQ01_CAM (b01 + a slow push), squats every 12 frames (down 6), Kai sprint-jumping the lap from
      frame 1 (at speed), the narrator still at narrator_far with the torch. Heroes: Steve, Zuri, Ari.
    """
    f0, f1 = s.frame_start, s.frame_end
    trio = []
    for role in ("steve", "zuri", "ari"):
        p = C.actor(role, "sq")
        C.put(p, f0, "squat_" + role)
        C.carry_anvil(p)                                 # the morning: whole anvils
        trio.append(p)
    for p in trio:
        p.look_at(f0, SQ01_CAM["pos"], ease=0)
        for f in range(f0 + 1, f1 - 6, 12):            # squats in unison (crouch spam): down 6 frames, up 6
            p.sneak(f, True)
            p.sneak(f + 6, False)
    kai = C.actor("kai", "sq")
    kai.place(f0, KAI_LAP[0], LC.yaw_to(KAI_LAP[0], KAI_LAP[1]))
    kai.sprint_jump(f0, KAI_LAP, ramp=(False, False))
    efe = C.narrator("sq")
    C.put(efe, f0, "narrator_far")
    st.use(s, *trio, kai, efe)
    C.cam(s, None, focus=trio[0].head, **SQ01_CAM)
    st.hero(s, "squatters", *trio)
    C.lights(s, "gold", near=(0.0, -3.0, 1.0), radius=14.0)


def sq02_reps(st, s, C, nar):
    """BEATS 2 AND 3, ONE TAKE  "Steve mines stone with his fists. It drops nothing, and he counts that as one rep."
    frames 73-204 (132 f, 5.50 s: the film's one shot over 5 s, by the story's own "same take"), sky gold.
    Words: Steve 75, mines 83, stone 93, with 101, his 103, fists 107 | It 128, drops 130, nothing 140, and 157,
    he 160, counts 162, that 172, as 177, one 181, rep 187. (The caption "fists" clears on 126, the second
    sentence's own cut: no picture cut there.)

    STORY, beat 2: About 2.2 s. Close shot, long lens, looking along a row of stone blocks that stands on the grass at
    the edge of the square. Steve stands beside the nearest block in profile, nothing in his hand, and punches it:
    arm swinging, the crack overlay creeping across the block, crumbs flying. Start with the cracks already half way.
    Cast: Steve. Effects: stone block with breaking cracks and crumbs, repeated punch-mining arm swing, row of stone
    blocks soft behind.
    STORY, beat 3: About 3.3 s. The same take carries on and drifts back. The block bursts into crumbs and nothing
    drops: bare grass, hold on the empty spot for half a second. Steve steps one block sideways and starts punching
    the next. The pull-back shows about eight stone blocks waiting in a line, his whole set, and an iron pickaxe
    turning slowly as a dropped item three blocks behind his back, in his plane of focus, never touched. Three blocks
    keeps it out of pick-up reach, or he would collect it.
    Cast: Steve. Effects: block break with crumbs and no item drop, row of about eight stone blocks, iron pickaxe as
    a turning dropped item three blocks from Steve, repeated punch-mining arm swing.

    MUST BE SEEN, ON WHICH WORD
      frame 73        Steve already punching (a twin pre-rolled: steve_sq2 clicks on frame -50, the game's 180
                      frames before the burst), the cracks past half way (stage 6 of 10)
      "fists" 107     his bare fist and the cracks, in profile, lit (he faces east: the sun)
      "drops" 130     the stone BURSTS (breaking.mine: the break frame); crumbs; NOTHING drops (stone by hand drops
                      nothing: breaking.drops('stone', 'hand') is None)
      "nothing" 140 .. ~152    the empty, bare grass where it stood, held (half a second)
      "he counts" 160 Steve steps one block north (mine_2) and starts punching stone 2 (no step under 7 frames): it
                      is only BEGUN (stage 1 by 204: the game's clock); it never breaks (_begin_mining: its cracks
                      clear on 205, off-screen, where he lets go). The first stub broke it on 284, inside pn04
      "one rep" 181-196   the pull-back has revealed the row (about eight stones: seven left) and the iron pickaxe
                      turning on the grass three blocks behind his back, in focus with him, never touched
    SHARED: none. Anchors mine_1, mine_2 (facing east), pickaxe_target (1.25, -14.5).
    NEIGHBOURS: before, sq01_squats (the same Steve squatting at the well); after, pn04_farms (the pens: a new place).
    RISKS (story): "It drops nothing: an absence is hard to show. The half-second hold on bare grass and the untouched
      pickaxe in the pull-back carry it. Fallback: let Steve look down at the empty spot for a beat before he steps
      to the next block." "A small thing is seen only if it is what is in focus" (the Hello's lesson): the pickaxe
      at the end must be in the focus plane (the story says so), and big enough (the set builder's b03 still: it is
      a few pixels on the path at the left: come closer or longer).
    MEASURED (the set builder, out/test/legday_set_b02_punch / _b03_row[_zones].png): b02 Steve in profile, lit face,
      the cracked stone, the row receding to its right, the column and the wall's south end behind; b03 stone 1 gone
      (bare grass), Steve at stone 2, the pickaxe 3 blocks behind him on the path, the row a low line ("not 8
      separate blocks").
    NOW (stub): SQ02_CAM, a linear drift from b02's spot back to b03's over the take; steve_sq2 mines stone 1 from
      frame -50 (the game's 180 frames: stage 6 on 73, the burst on "drops" 130), looks down at the spot (138-150),
      walks to mine_2 (153-168, slow) and begins stone 2 from 170 (cracks and swings to 204, never broken); the iron
      pickaxe turning at pickaxe_target. Hero: Steve.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "sq2")
    burst = C.at(s, MINE_BREAK)
    start = burst - MINE_FRAMES
    a = C.P("mine_1")
    steve.place(start, a, C.yaw("mine_1"))
    steve.look_at(start, _stone(C, 0).center, ease=0)
    r = breaking.mine(steve, _stone(C, 0), start, duration=MINE_FRAMES, camera=s)
    C.memo["sq_mine1"] = r
    # nothing dropped: he looks down at the empty spot for a beat, then steps one block north to stone 2
    spot = (5.5, -15.5, 0.0)
    steve.look_at(burst + 6, spot, ease=6)
    b = C.P("mine_2")
    step = burst + 23
    steve.walk(step, [a, b], speed=1.4)
    steve.look_at(step + 2, _stone(C, 1).center, ease=8)
    _begin_mining(steve, _stone(C, 1), step + 17, f1)
    pick = C.item("iron_pickaxe", "sq")
    pick.place(f0, C.P("pickaxe_target"))
    pick.animate(f0, f1 + 1)
    st.use(s, steve, pick)
    C.cam(s, None, focus=steve.head, ease="linear", **SQ02_CAM)
    st.hero(s, "steve", steve)
    C.lights(s, "gold", near=(4.0, -14.0, 1.0), radius=10.0)


def sq07_bench(st, s, C, nar):
    """BEAT 7  "But I'm a redstoner."   frames 390-430 (41 f, 1.71 s), sky gold.
    Words: But 392, I'm 394, a 400, redstoner 402. The pause before it (0.6 s) is the story's turn.

    STORY: About 2.0 s. A corner of the square with a small open-air redstone bench. Close and warm: the narrator
    plants his redstone torch at the head of a short line of redstone dust. The dust lights up red, runs through a
    repeater, a redstone lamp switches on and lights his face, and a piston beside the lamp pushes out once. The
    planted torch is the power source, so the circuit is honest.
    Cast: Narrator (Efe, slim-arm model). Effects: redstone torch placed as a block and glowing, redstone dust
    lighting up, repeater switching on, redstone lamp switching on, piston extending, block placing.

    MUST BE SEEN, ON WHICH WORD
      frame 390       the narrator already in the frame and moving (head, arm), the bench dark
      "I'm" 394 .. "a" 400     his arm swing plants the torch at the head of the dust (C.bench["torch"].plant(f,
                      player=efe): the swing ON f, the torch there on f + 1)
      "redstoner" 402 the dust lit red, the repeater on (2 ticks), the lamp ON lighting his face, the piston out once
      the whole shot  NOTHING in the last 3 frames that a cut would lose (the lamp is on well before 428)
    SHARED: none (the bench, bench_narrator); the lamp lit here stays lit for sq08 (do not key it again there).
    NEIGHBOURS: before, pn06_told (he walked away from the cow pen); after, sq08_arms (in front of the same lamp,
      lit, with Steve).
    MEASURED (the set builder, out/test/legday_set_b07_bench[_zones].png): from the east, 18 mm: the lit lamp on the
      left, repeater and dust on the bench floor, the narrator facing the lens in front of house_c's door, the
      planted torch on the right; front-lit (the sun behind the lens); palette passes. THE LEAD: he is small (the
      story says "close and warm"): come closer.
    NOW (stub): SQ07_CAM (b07 + a slow push), efe_sq at bench_narrator with his torch, looking at the torch spot;
      plant on "I'm" (394) -> the circuit; he looks up at the lamp. Hero: the narrator.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.narrator("sq")
    C.put(efe, f0, "bench_narrator")
    B = C.bench
    efe.look_at(f0, (-5.5, 8.4, 0.2), ease=0)
    t = B["torch"].plant(C.at(s, "I'm"), player=efe)
    redstone.signal(t, B["wire"], B["repeater"], (B["lamp"], B["piston"]))
    efe.look_at(int(t) + 6, B["lamp"].center, ease=6)
    st.use(s, efe)
    C.cam(s, None, focus=efe.head, **SQ07_CAM)
    st.hero(s, "narrator", efe)
    C.lights(s, "gold", near=(-6.0, 5.0, 1.0), radius=8.0)


def sq08_arms(st, s, C, nar):
    """BEAT 8  "My arms are three pixels wide, and theirs are four."   frames 431-519 (89 f, 3.71 s), sky gold.
    Words: My 433, arms 438, are 447, three 450, pixels 458, wide 468, and 487, theirs 489, are 497, four 500.

    STORY: About 3.3 s. Frontal two-shot against the plain glow of the lit redstone lamp, both players facing the
    lens. The narrator stands still with his arms hanging, the redstone torch in his far hand. Steve steps in
    shoulder to shoulder, so the narrator's near arm and Steve's near arm hang side by side in the middle of the
    frame, same height, each at least an eighth of the frame wide: three pixels next to four. Steve's head tilts
    down to the thin arm, the narrator's head turns to Steve's arm. Never side-on: from the side both arms are four
    pixels deep and look the same.
    Cast: Narrator (Efe, slim-arm model), Steve. Effects: redstone torch held and glowing, redstone lamp lit behind as
    a plain backdrop, slim and wide arms hanging side by side, seen from the front.

    MUST BE SEEN, ON WHICH WORD
      frame 431       Steve already stepping in (a pre-roll of steve_sq3, the empty-handed twin, is allowed: he is
                      not in sq07; steve_sq holds sq01's anvil), the lamp lit
      by "arms" 438   BOTH BODIES SQUARE TO THE LENS (yaw within 20 degrees: tools.legday_state checks it): a player's
                      body turns along his walk, so a sideways step-in ends side-on unless he turns to the front
      "arms" 438 .. "four" 500   the two NEAR arms side by side in the middle of the frame, frontal, same height, each
                      at least an eighth of the frame wide (68 px at 540): THREE pixels next to FOUR; check the still
                      at 360x640 (the story's risk)
      "three" 450     Steve's head tilts down to the thin arm; "four" 500 the narrator's head turns to Steve's arm
      the torch       in the narrator's FAR hand (his right: he stands west of Steve facing south)
    SHARED: none (arms_narrator, arms_steve, the lamp lit in sq07).
    NEIGHBOURS: before, sq07_bench; after, sq09_lifts (the column).
    RISKS (story): "a one-pixel difference can vanish at phone size, and it does not exist at all from the side ...
      Fallback: crop tighter to just the two arms and half of each torso and let the heads go; the line carries it."
    MEASURED (the set builder, out/test/legday_set_b08_arms[_zones].png): frontal 50 mm from 3.85 blocks: the slim
      (3 px) and wide (4 px) near arms side by side, each about 14-18 % of the frame wide (computed, not measured on
      pixels); the lit lamp between the heads behind; heads at x 20 / 82 % (Steve's at the safe area's edge).
      THE REVIEW (story, measured on pixels): in the FIRST stub Steve's body ended side-on (65 degrees off the lens:
      the walk turned it west and nothing turned it back), so his near arm showed about 30 px against the
      narrator's 66-75: the viewer saw the narrator with the WIDER arm, the opposite of the line. The set's b08
      (both square to the lens) reads right: about 67 px against 88. Fixed in the stub (the step-in ends with a
      turn to the front, done by 436); THE GATE before you hand in, on a 360x640 still between "arms" and "four":
      Steve's near arm at least 4/3 the width of the narrator's, each at least 1/8 of the frame.
      THE TORCH (technical review): the narrator's far (right) hand and its torch run off the left edge (x 0). The
      two cannot both be had at the arms' depth: the arm rule wants a frame at most 1.5 blocks wide there, the
      torch hand (x -6.33) to Steve's far arm (x -4.65) is 1.7. Priority: the arms (the line); the torch's red glow
      at the left edge must read, or turn him a little so the torch comes forward.
      Measure the arm widths on pixels (tools.legday_geo --pts at the arms' edges, or the still) before you hand in.
      THE LEAD'S SCOUT of the stub (out/test/legday_scout_sq08_arms_470[_zones].png; tools.legday_geo sq08_arms:470
      --pts="-5.62,3.15,1.1;-5.40,3.15,1.1"): the narrator's eyes x 19 %, Steve's x 84 % (OUTSIDE the safe area
      82 %), faces 183 px; the slim near arm at x 43.5 %, the wide one at x 58.3 %, both at y 51 % (the hands reach
      into the caption band): come in so both heads are inside, or crop to the arms (the story's fallback).
    NOW (stub): SQ08_CAM (b08 + a slow push), efe_sq with the torch, Steve (steve_sq3) steps in from 0.8 east
      (pre-rolled from 411, arriving about 431) and turns square to the lens (done by 436), heads as the set
      builder posed them, tilting on "three" / "four". Heroes: both.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.narrator("sq")
    C.put(efe, f0, "arms_narrator")
    steve = C.actor("steve", "sq3")
    b = C.P("arms_steve")
    a = (b[0] + 0.8, b[1] + 0.25, b[2])
    front = C.yaw("arms_steve")                          # south: the lens
    steve.place(f0 - 20, a, LC.yaw_to(a, b))
    steve.look_at(f0 - 20, (b[0] - 1.0, b[1] - 1.5, 1.5), ease=0)
    arrive = steve.walk(f0 - 20, [a, b], speed=1.6)
    square = steve.turn(arrive, front, ease=5)           # square to the lens before "arms"
    assert square < C.at(s, "arms"), "sq08: Steve must be square to the lens before 'arms' (%d)" % square
    efe.look_at(f0, (-5.6, 1.0, 1.2), ease=0)
    steve.look_at(arrive, (-5.6, 1.0, 1.25), ease=5)
    steve.look_at(C.at(s, "three") - 2, (-5.38, 2.9, 1.0), ease=8)
    efe.look_at(C.at(s, "four") - 4, (-5.65, 2.9, 0.95), ease=8)
    st.use(s, efe, steve)
    C.cam(s, None, focus=(-5.52, 3.15, 1.1), **SQ08_CAM)
    st.hero(s, "narrator", efe)
    st.hero(s, "steve", steve)
    C.lights(s, "gold", near=(-3.5, 4.0, 1.0), radius=8.0)


def sq09_lifts(st, s, C, nar):
    """BEAT 9  "Steve asked how much my piston lifts, and I said twelve blocks."   frames 520-626 (107 f, 4.46 s),
    sky gold. Words: Steve 522, asked 532, how 540, much 546, my 552, piston 557, lifts 567, and 585, I 588, said 591,
    twelve 598, blocks 607.

    STORY: About 3.9 s. Tall composition made for the phone frame, low wide lens: one piston facing upward under a
    column of twelve iron blocks that stands higher than the houses. Steve stands at its foot looking down at the
    piston. The narrator flips a lever beside it, the whole column rises one block, and Steve tips his head back to
    follow it up as the camera tilts with it.
    Cast: Steve, Narrator (Efe, slim-arm model). Effects: upward piston extending, column of twelve iron blocks moving
    up one block, lever switching.

    MUST BE SEEN, ON WHICH WORD
      frame 520       Steve at the column's foot looking down at the piston, the camera already moving
      "piston" 557 .. "lifts" 567    the piston and the column's foot clear (what "my piston" is)
      "said" 591 / "twelve" 598     the narrator flips the lever (redstone.flip_by(efe, C.column["lever"], f)): the
                      whole column rises one block (C.column["piston"].power(t): 2 ticks); Steve's head tips back
                      to follow it up; the camera tilts up the column ("twelve blocks" 598-620: the top against the
                      sky)
    SHARED: none (column_steve, column_narrator; the column stays up for sq10).
    NEIGHBOURS: before, sq08_arms; after, sq10_cheating (the column up behind them).
    MEASURED (the set builder, out/test/legday_set_b09_column_a / _b[_zones].png): 18 mm from the low south-east,
      tilting (target -> target1): _a Steve at the foot (face 48 %), piston, the narrator at the pier; _b the
      column's top against the sky. The lever's own Lever.stand() is INSIDE its pier: stand at column_narrator.
    NOW (stub): SQ09_CAM (the tilt, linear over the shot), flip on "said" (591), the column up 2 ticks later, Steve
      looks down at the piston then up the column. Heroes: Steve, the narrator.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "sq3")
    C.put(steve, f0, "column_steve")
    efe = C.narrator("sq")
    C.put(efe, f0, "column_narrator", toward=(-3.5, 10.5, 1.3))
    steve.look_at(f0, (-3.5, 9.5, 0.6), ease=0)
    efe.look_at(f0, (-3.5, 10.5, 1.2), ease=0)
    t = redstone.flip_by(efe, C.column["lever"], C.at(s, "said"), look=False)
    C.column["piston"].power(t)
    steve.look_at(int(t) + 2, (-3.5, 9.5, 9.0), ease=14)
    st.use(s, steve, efe)
    C.cam(s, None, focus=steve.head, ease="linear", **SQ09_CAM)
    st.hero(s, "steve", steve)
    st.hero(s, "narrator", efe)
    C.lights(s, "gold", near=(-4.0, 9.0, 1.0), radius=10.0)


def sq10_cheating(st, s, C, nar):
    """BEAT 10  "He said that's cheating."   frames 627-668 (42 f, 1.75 s), sky gold.
    Words: He 629, said 632, that's 637, cheating 644. The pause after it (0.6 s) leads to the wall.

    STORY: About 2.0 s. Steve turns his back on the column and walks away toward the well, his head held in profile
    toward the lens to the last frame. The narrator stays at the lever, small, his head turning to watch him go. The
    column of twelve stays up against the sky behind them.
    Cast: Steve, Narrator (Efe, slim-arm model). Effects: column of twelve iron blocks on the extended piston, lever.

    MUST BE SEEN, ON WHICH WORD
      frame 627       Steve already turning / walking (place on f0 and walk at speed from it, or a twin pre-rolled)
      "cheating" 644  Steve's head in profile toward the lens (the attitude), the column up against the sky behind
      to frame 668    his head held in profile to the last frame; the narrator small at the lever, his head turning
                      to follow him
    SHARED: none (column_walk_end; the column up since sq09).
    NEIGHBOURS: before, sq09_lifts; after, cl11_climb (the wall: a new place). The same head turn comes back in
      rd21 ("Steve still says redstone is cheating": the story's rhyme).
    MEASURED (the set builder, out/test/legday_set_b10_cheating[_zones].png): 16 mm low from the well side: Steve
      walking at the lens (frontal: the head-in-profile turn is the director's), the whole column against the sky,
      the narrator small at the lever; the wall's south end behind.
    NOW (stub): SQ10_CAM (b10 + a drift), Steve walks from the column toward column_walk_end at speed from frame 627,
      head held toward the lens's side; the narrator at the lever watching him. Heroes: Steve.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "sq3")
    a, e = (-4.6, 8.0, 0.0), C.P("column_walk_end")
    steve.place(f0, a, LC.yaw_to(a, e))
    steve.walk(f0, [a, e], ramp=(False, True))
    cam = SQ10_CAM["pos"]
    steve.look_at(f0, C.to_lens(steve, f0, (cam[0] + 3.0, cam[1] - 2.0, 1.6), cam, degrees=60.0), ease=0)
    efe = C.narrator("sq")
    C.put(efe, f0, "column_narrator")
    efe.look_at(f0, steve.eye_point(f0 + 10), ease=0)
    efe.look_at(f0 + 4, steve.eye_point(f1), ease=f1 - f0 - 8)
    st.use(s, steve, efe)
    C.cam(s, None, focus=steve.head, **SQ10_CAM)
    st.hero(s, "steve", steve)
    C.lights(s, "gold", near=(-4.0, 6.0, 1.0), radius=10.0)
