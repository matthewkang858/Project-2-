"""Leg Day, sequence SQUARE: the village square in golden light. Beats 1, 2+3 (one take), 7, 8, 9, 10 (shots sq01_squats,
sq02_reps, sq07_bench, sq08_arms, sq09_lifts, sq10_cheating), sky "gold". One function per shot; the contract is in
films/legday_common.py (tags "sq...", C.actor / C.narrator, C.cam, C.lights, st.use / st.hero).

STATUS: SHOT by the square director (from the lead's stubs). Each shot's docstring keeps the beat, its words, what
must be seen on which word, the neighbours and the risks, and now ends its NOW (what the shot does) with a MEASURED
line (tools.legday_square_probe / legday_geo numbers, pixels on the stills, tools.legday_palette).

THE SEQUENCE NOW (stills out/test/legday_sq_<shot>_<frame>[_zones].png, 540x960, 16 samples; motion
out/test/legday_square_motion.mp4):
  sq01  a wedge at the foot of the well, 18 mm at chest height from the south: Steve big in front with his anvil,
        Zuri and Ari squatting behind him on either side, all three in unison (crouch every 12 frames), faces to the
        lens; the two bell lanterns stand clear beside their heads (the fixed line the crouch drops against); Kai
        sprint-jumps a lap round the well behind them (in at the right on frame 1, out at the left by 64); the
        narrator stands still at the square's east edge beyond the well (x 88 %), his torch glowing; a slow push in
  sq02  ONE take: close from the south-east on Steve's lit three-quarter face and fist and the cracked stone; the
        burst on "drops" (crumbs, nothing dropped), the bare grass, Steve looks down at it; on "he counts" one block
        north, square to stone 2 and punching it; the camera pulls back to the south (re-timed: slow, then the
        pull 152-184): Steve in profile at the row, the iron pickaxe turning on the path three blocks behind his back
  sq07  from the north-east, down onto the bench: the narrator (face 3/4, lit) looks up the dust to the torch spot,
        his swing goes off the frame's right edge (the spot is beyond it); the red line lights from there on "a" 400,
        the repeater and the lamp beside him on "redstoner" 402; his head turns to the lamp, then to us
  sq08  frontal two-shot, a push in re-timed to arrive by "three": both faces while Steve steps in and squares up
        (431-447; the torch's glow at the left edge), then the two near arms side by side over the lamp's glow,
        three texels against four, each more than an eighth of the frame; Steve's head tilts to the thin arm on
        "three", the narrator's turns to the wide one on "four"
  sq09  from the east-south-east, low: Steve at the column's south-west foot looking at the piston (a glance at
        the narrator on "asked"), the column, the pier with the lever beside it, the narrator behind the lever
        facing us; on "said" he flips it, the column rises one block, Steve's head tips back and the camera tilts up
        (re-timed: held to 589, up 589-616) to the top against the sky on "blocks"
  sq10  low beside the well: Steve walks at the lens, the column up against the sky behind him, the narrator small
        at the lever following him with his head; on "cheating" Steve turns his head 60 degrees away, nose up,
        held to the end
NEW PLACES (this file's constants; the set's anchors are unchanged): SQUATS (the wedge), NARRATOR_FAR (4.6, 2.6),
  BENCH_NARRATOR (-7.25, 6.25), COLUMN_STEVE (-5.0, 8.6), LEVER_NARRATOR (-3.5, 11.6), KAI_LAP; each says why.
CAMERA TIMING: _ease(s, KEYS) registers a monotone curve of (frame, fraction of the move) in engine.shots.EASES at run
  time under "legday_<shot>" and C.cam bakes the move with it (Film.finalize re-bakes every camera, so keys edited
  after C.cam would be lost). Used by sq02, sq08, sq09.
TOOL: $BPY -m tools.legday_square_probe SHOT:F ... [--sweep SHOT:A-B:STEP] [--obs NAME] [--pts=...]: heads, bodies,
  objects and points in the frame without rendering; for sq08 the arms gate (each arm's projected width).

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
TAGS (twins): steve_sq (sq01, with the anvil), steve_sq2 (sq02: pre-rolled, mining from frame -50),
  steve_sq3 (sq08 pre-rolled 21 frames (410), sq09, sq10: empty-handed; a held item stays on its instance),
  zuri_sq, ari_sq, kai_sq (sq01), efe_sq (the narrator with his torch: sq01, sq07, sq08, sq09, sq10), pickaxe
  iron_pickaxe_sq. A new twin: sq3, sq4 ...
LIGHT: C.lights(s, "gold", near=<point>, radius=10..14) (daylight; the bench lamp is a kit light, untouched by it).
PREVIEW samples for render.py previews: 5 (legday_common.PREVIEW_SAMPLES).
"""
import math

from engine import breaking, fx, redstone
from films import legday_common as LC

# ---------------------------------------------------------------------------------------------------------------
# this sequence's own cameras (C.cam(s, None, **CAM)); a move's timing per shot: _ease (KEYS)
# ---------------------------------------------------------------------------------------------------------------
SQ01_CAM = dict(pos=(-0.42, -10.45, 0.95), target=(-0.55, -6.6, 0.42), pos1=(-0.47, -9.85, 0.93),
                target1=(-0.55, -6.6, 0.42), lens=18.0, fstop=2.8)
SQUATS = {"steve": (-0.55, -7.5), "zuri": (-1.72, -5.85), "ari": (0.6, -5.8)}   # a wedge: Steve forward
NARRATOR_FAR = (4.6, 2.6)     # sq01: at the square's east edge beyond the well: the one spot of the far square the
#                               trio does not cover from SQ01_CAM (narrator_far (-6.0, 3.2) is behind Zuri's anvil)
SQ02_CAM = dict(pos=(6.45, -19.0, 1.25), target=(4.85, -15.45, 0.85), pos1=(3.45, -20.5, 1.8),
                target1=(3.1, -14.2, 0.7), lens=22.0, fstop=2.8)
SQ02_KEYS = [(73, 0.0), (128, 0.08), (145, 0.2), (188, 0.92), (205, 1.0)]
BENCH_NARRATOR = (-7.25, 6.25)  # sq07: bench_narrator (-7.3, 6.6) 0.35 south: nearer the lamp (2.5 blocks), so lamp
#                                 and face share the frame from the north-east; the torch spot is 2.9 away (in reach)
SQ07_CAM = dict(pos=(-3.05, 8.35, 1.7), target=(-6.4, 5.6, 0.45), pos1=(-3.35, 8.1, 1.62),
                target1=(-6.4, 5.6, 0.45), lens=18.0, fstop=2.4)
SQ08_CAM = dict(pos=(-5.5, -1.66, 1.12), target=(-5.5, 3.15, 1.12), pos1=(-5.52, -0.33, 0.92),
                target1=(-5.52, 3.15, 0.92), lens=50.0, fstop=2.8)
SQ08_KEYS = [(431, 0.0), (437, 0.25), (447, 0.80), (455, 0.93), (520, 1.0)]
SQ09_CAM = dict(pos=(0.6, 7.2, 0.5), target=(-3.6, 9.7, 1.1), pos1=(0.45, 7.05, 0.45),
                target1=(-3.55, 9.6, 11.5), lens=18.0, fstop=4.0)
COLUMN_STEVE = (-5.0, 8.6)    # sq09: at the column's SOUTH-WEST foot (column_steve (-5.25, 9.45) is behind the column
#                               from any camera that sees the lever beside it), facing the piston
LEVER_NARRATOR = (-3.5, 11.6)  # sq09 / sq10: on the north side of the lever's pier, facing south onto the handle (1.1
#                               in front of him: the plain swing meets a floor lever on a pier), his face to SQ09_CAM
SQ09_KEYS = [(520, 0.0), (589, 0.05), (598, 0.28), (616, 0.96), (627, 1.0)]
SQ10_CAM = dict(pos=(-0.8, 3.4, 0.6), target=(-3.7, 7.8, 2.3), pos1=(-0.98, 3.68, 0.6),
                target1=(-3.75, 7.85, 2.3), lens=16.0, fstop=4.0)
KAI_LAP = [(3.38, -1.3), (3.45, 0.6), (3.25, 2.95), (1.4, 3.95), (-2.6, 3.95), (-4.5, 1.6), (-4.55, -3.0),
           (-4.5, -6.0)]              # sq01: Kai's sprint-jump lap round the well, clear of its corners (legday_state)
MINE_BREAK = "drops"          # the first stone bursts on this word (sq02): "It DROPS nothing"
MINE_FRAMES = breaking.break_frames("stone")   # click -> break of stone by hand: THE GAME'S 180 frames (7.5 s; the
#                               review: the first stub compressed it to 114, and punching stone being slow is the joke
#                               of the beat). The click is on frame -50 (a pre-roll before the film: the stone row is
#                               in no earlier frame); on frame 73 the cracks are at stage 6 of 10


def _curve(keys):
    """A monotone cubic through keys [(frame, value), ...] (Fritsch-Carlson: no overshoot), held outside them:
    returns e(frame)."""
    xs = [float(k[0]) for k in keys]
    ys = [float(k[1]) for k in keys]
    n = len(xs)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [0.0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2.0 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0.0:
            m[i] = m[i + 1] = 0.0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        h = a * a + b * b
        if h > 9.0:
            t = 3.0 / math.sqrt(h)
            m[i], m[i + 1] = t * a * d[i], t * b * d[i]

    def e(f):
        if f <= xs[0]:
            return ys[0]
        if f >= xs[-1]:
            return ys[-1]
        i = max(k for k in range(n - 1) if xs[k] <= f)
        h = xs[i + 1] - xs[i]
        t = (f - xs[i]) / h
        h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
        h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
        return h00 * ys[i] + h10 * h * m[i] + h01 * ys[i + 1] + h11 * h * m[i + 1]
    return e


def _ease(s, keys):
    """A camera move of shot s timed by keys [(film frame, fraction of the move), ...] (a monotone cubic through
    them: one shot can drift, then move, then settle) instead of one of engine.shots' four eases. The curve is
    registered in engine.shots.EASES under the shot's own name (at run time: no engine file changes), so the move
    is baked with it by C.cam and again by Film.finalize. Returns that name: C.cam(s, None, ease=_ease(s, KEYS))."""
    from engine import shots as SH
    e = _curve(keys)
    span = float(max(1, s.frame_end + 1 - s.frame_start))
    name = "legday_" + s.name
    SH.EASES[name] = lambda u, e=e, f0=s.frame_start, span=span: e(f0 + u * span)
    return name


def _head_dir(c, frame, yaw_deg, pitch_deg=0.0, dist=3.0):
    """A look target that turns c's head `yaw_deg` from its body (+ = to its left) and `pitch_deg` up at `frame`."""
    eye = c.eye_point(frame)
    yaw = c.yaw_at(frame) + math.radians(yaw_deg)
    return (eye.x + math.sin(yaw) * dist, eye.y - math.cos(yaw) * dist,
            eye.z + math.tan(math.radians(pitch_deg)) * dist)


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
    NOW: SQ01_CAM, 18 mm f/2.8 at chest height (z 0.95) from 3 blocks south of Steve, tilted a little down, a slow
      push (0.6 block, ease_out: at speed on frame 1). THE WEDGE (SQUATS): Steve forward in the middle (-0.55, -7.5),
      Zuri (-1.72, -5.85) and Ari (0.6, -5.8) behind him on either side, all three facing south, whole anvils, heads
      on the lens; squats in unison from frame 2 (down 6 frames, up 6: 2, 14, 26, 38, 50, 62 down). Kai sprint-jumps
      KAI_LAP from frame 1 at speed (round the well: in at the right edge, across behind them, out at the left by
      about 64). The narrator at NARRATOR_FAR, placed only (no idle: the only one not moving), his torch glowing.
      Heroes: the three squatters. WHY: three players side by side in a 9:16 frame stay a small band with half the
      frame empty path (the stub); the wedge lets Steve fill the frame from y 26 to 65 % and puts the path under the
      caption. The lanterns of the bell sat behind Zuri's and Ari's heads in every frontal low view; from here they
      stand beside them (x 9-13 % and 66 %, y 31 %), the fixed line their heads drop against.
    MEASURED (legday_square_probe / palette, out/test/legday_sq_sq01_squats_32_zones.png): "everyone" 32 (standing):
      Steve's eyes x 49 %, y 30 %, face 109 px; Zuri x 25 %, Ari x 76 %, y 35 %, faces 64 px; crouched (62) Steve's
      eyes y 37 %; his anvil y 42-51 % standing, 50-62 % crouched (Zuri's and Ari's 45-56 %): above the caption band;
      the feet in the band, the bottom 30 % grass. Kai x 91 % on frame 1, behind Steve at 32, out at the left from about 62. The narrator x 88 %,
      y 43 %, face 22 px, clear all shot (legday_geo spots). palette_check sq01@32: all ok, hero x 20-81 %, y 26-40 %,
      100 % inside. legday_state: nobody inside a block (Kai's first lap clipped the well's corner: rerouted).
    """
    f0, f1 = s.frame_start, s.frame_end
    lens_at = SQ01_CAM["pos"]
    trio = []
    for role in ("steve", "zuri", "ari"):
        p = C.actor(role, "sq")
        C.put(p, f0, SQUATS[role], yaw=C.yaw("squat_" + role))      # facing south (the lens)
        C.carry_anvil(p)                                 # the morning: whole anvils
        trio.append(p)
    kai = C.actor("kai", "sq")
    lap = [C.stand(q) for q in KAI_LAP]
    kai.place(f0, lap[0], LC.yaw_to(lap[0], lap[1]))
    efe = C.narrator("sq")
    C.put(efe, f0, NARRATOR_FAR, toward=SQUATS["steve"])     # the only one not moving: placed, nothing else
    for p in trio:
        p.look_at(f0, lens_at, ease=0)                   # their faces to the lens
        for f in range(f0 + 1, f1 - 6, 12):             # squats in unison (crouch spam): down 6 frames, up 6
            p.sneak(f, True)
            p.sneak(f + 6, False)
    kai.sprint_jump(f0, lap, ramp=(False, False))      # already hopping at speed on frame 1
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
    NOW: SQ02_CAM 22 mm f/2.8, timed by SQ02_KEYS (_ease): close from the south-east (6.45, -19.0, 1.25), drifting
      slowly to "drops" (8 % of the move by 128), 20 % by 145, the pull-back 145-188 (to 92 %, about 1.3 blocks a
      second) and
      settling at (3.45, -20.5, 1.8) looking north: Steve in profile beside stone 2, the row receding north, the
      pickaxe on the path at the left. steve_sq2 mines stone 1 from frame -50 (the game's 180 frames: stage 6 on 73,
      the burst on "drops" 130, no drop), looks down at the spot (136-142), walks one block north at 2.6 blocks/s
      from 153 (14 frames), turns square to stone 2 (5 frames) with his head, and begins it 6 frames later (the
      fx swing run writes the head ABSOLUTE from the pose at its first request: the look must be finished before)
      to 204 (never broken). The iron pickaxe turns at pickaxe_target all shot (2.97 from mine_2). Heroes: Steve,
      the pickaxe (in the frame from about 180).
    MEASURED: 73-128 Steve's three-quarter face lit (59 degrees off the lens), eyes x 33-35 %, y 37 %, face 118-130
      px; the stone's top edge y 48 %, its front face to 66 % (the cracks mostly above the caption band). 131
      (out/test/legday_sq_sq02_reps_131_zones.png): the burst, crumbs where the stone stood. 190
      (legday_sq_sq02_reps_190_zones.png): Steve's eyes x 70 %, y 41 % (head x 65-80 %), profile (97 degrees);
      the pickaxe x 14-21 %, y 51-55 %, 35-42 px, at his depth (22 mm: sharp). palette_check sq02@190: all ok, hero
      steve x 66-77 %, y 39-43 %, 100 % inside. legday_state: stone 1 stage 6 on 73, broken on 130; stone 2 stage 1
      on 204, cleared on 205.
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
    arrive = steve.walk(step, [a, b], speed=2.6)       # one block north at an easy pace (14 frames)
    steve.look_at(step + 2, _stone(C, 1).center, ease=8)
    steve.turn(arrive, C.yaw("mine_2"), ease=5)           # square to stone 2 again (the walk turned him north)
    steve.look_at(arrive + 1, _stone(C, 1).center, ease=4)   # (and his head with it, BEFORE the swings: fx keys
    _begin_mining(steve, _stone(C, 1), arrive + 6, f1)       # the head absolute from the pose at the first one)
    pick = C.item("iron_pickaxe", "sq")
    pick.place(f0, C.P("pickaxe_target"))
    pick.animate(f0, f1 + 1)
    st.use(s, steve, pick)
    C.cam(s, None, focus=steve.head, ease=_ease(s, SQ02_KEYS), **SQ02_CAM)
    st.hero(s, "steve", steve)
    st.hero(s, "pickaxe", *pick.copies)                  # in the frame from about 180 (the pull-back's end)
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
    NOW: SQ07_CAM 18 mm f/2.4 from the north-east (-3.05, 8.35, 1.7), looking down south-west, a slow push. The
      narrator at BENCH_NARRATOR facing east; on the cut he looks down along the dust and up it to the torch spot
      (moving from frame 391); the plant swing on "a" - 2 = 398 (the torch stands on 399, the dust lit on 399, the
      repeater 2 ticks later, the lamp and the piston on 401.4: all on "redstoner" 402); his head turns to the lamp
      from 401 (its light on his face), then to the lens from 415 (by 423). Nothing new after 423. Hero: the
      narrator. WHY THIS SIDE: the circuit is 5 blocks long and he stands beside its middle, so no camera close
      enough for "close and warm" holds the torch spot, the lamp and his face at once; from the north-east the lamp
      glows beside his face (both at face height), the lit repeater and the red line lead to him, and his swing goes
      off the frame's right edge where the line comes from. The piston pushes east, off the frame's left edge.
    MEASURED (legday_sq_sq07_bench_400_zones.png, _405_zones.png): his eyes x 67 %, y 36 %, face 68-83 px; the lamp
      x 11-15 % (its glowing face x 0-30 %, y 30-45 %); the repeater y 57 %; the dust y 61-68 % (its middle under the
      caption from 402; it lights on 399 under the one-letter "a"). palette_check sq07@405: all ok, hero narrator
      x 65-78 %, y 33-39 %, 100 % inside.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.narrator("sq")
    C.put(efe, f0, BENCH_NARRATOR, yaw=C.yaw("bench_narrator"))      # facing east
    B = C.bench
    spot = (-5.5, 8.45, 0.15)                            # the torch's spot at the head of the dust
    efe.look_at(f0, (-5.6, 7.6, 0.3), ease=0)            # on the cut he looks down along the dust ...
    efe.look_at(f0 + 1, spot, ease=5)                    # ... and up it to the spot (moving on frame 1)
    plant = C.at(s, "a") - 2                             # the swing; the torch stands on the next frame
    t = B["torch"].plant(plant, player=efe)
    redstone.signal(t, B["wire"], B["repeater"], (B["lamp"], B["piston"]))
    efe.look_at(int(t) + 2, B["lamp"].center, ease=6)    # to the lamp as it lights: its light on his face
    efe.look_at(int(t) + 16, SQ07_CAM["pos1"], ease=8)   # then to us: "I'm a redstoner"
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
    NOW: SQ08_CAM 50 mm f/2.8, a push timed by SQ08_KEYS (_ease): from 4.8 blocks (both faces, frame 2 blocks
      wide at their depth) to 3.5 (1.42 wide) by about 450, then a creep to the end; the tight frame centred on the
      gap between the near arms, low enough that the hands end above the caption band. efe_sq at arms_narrator with
      his torch (right hand); steve_sq3 pre-rolled from 410 (not in sq07): 0.8 east, a step in at 1.4 blocks/s,
      arriving 430, turned square to the lens by 435. Heads: both on the lens; Steve's tilts to the thin arm on
      "three" (45 degrees round, 25 down), back to the lens from "and"; the narrator's turns to the wide arm on
      "four". Hero: the two near arms (efe arm_l, steve arm_r). THE FACES: both heads together are 1.46 blocks wide
      and the arm rule needs a frame at most 1.5 wide: in the tight part they sit at the frame's edges (eyes x 17 %
      and 84 %, above the icon column); the push gives them whole at the start. THE TORCH: its glow is at the left
      edge in the wide part (431-447); in the tight part the hand is off frame (priority: the arms).
    MEASURED (legday_square_probe --sweep; pixels of out/test/legday_sq_sq08_arms_470.png, rows at y 52-56 %):
      bodies 6-8 degrees off the lens from 439 to 519 (legday_state: within 20 from "arms" to "four"); the slim
      forearm 69-71 px, the wide 92-100 px at 540 (12.8 % and 17-18.5 % of the frame; at 360x640 46 and 61-67 px:
      both over the eighth, 45 px), ratio 1.33-1.41, a dark gap of 13 px between them; the arms x 33-70 %, y 34-61 %.
      The slim arm reaches the eighth from 439 and holds it to 519. At 360x640 (scratch crop) both faces and the
      three-against-four read. palette_check sq08@470: all ok, hero arms x 34-70 %, y 33-61 %, 95 % inside.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.narrator("sq")
    C.put(efe, f0, "arms_narrator")
    steve = C.actor("steve", "sq3")
    b = C.P("arms_steve")
    a = (b[0] + 0.8, b[1] + 0.2, b[2])
    front = C.yaw("arms_steve")                          # south: the lens
    lens_at = SQ08_CAM["pos1"]
    steve.place(f0 - 21, a, LC.yaw_to(a, b))
    steve.look_at(f0 - 21, (b[0] - 1.0, b[1] - 1.5, 1.5), ease=0)
    arrive = steve.walk(f0 - 21, [a, b], speed=1.4)
    square = steve.turn(arrive, front, ease=5)           # square to the lens before "arms"
    assert square < C.at(s, "arms"), "sq08: Steve must be square to the lens before 'arms' (%d)" % square
    efe.look_at(f0, lens_at, ease=0)
    steve.look_at(arrive, lens_at, ease=5)
    steve.look_at(C.at(s, "three") - 2, (-5.75, 2.2, 1.0), ease=8)      # down at the thin arm (a tilt: 45
    steve.look_at(C.at(s, "and") - 6, lens_at, ease=8)                  # degrees round, 25 down, not more)
    efe.look_at(C.at(s, "four") - 4, (-5.25, 2.2, 1.0), ease=8)        # at the wide arm
    st.use(s, efe, steve)
    C.cam(s, None, focus=(-5.5, 3.15, 1.1), ease=_ease(s, SQ08_KEYS), **SQ08_CAM)
    st.hero(s, "arms", efe.parts["arm_l"], steve.parts["arm_r"])     # the two near arms: three pixels and four
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
    NOW: SQ09_CAM 18 mm f/4 low from the east-south-east (0.6, 7.2, 0.5), timed by SQ09_KEYS (_ease): a slow drift
      to 589 (5 %), the tilt up the column 589-616, settled by 627 on the top against the sky. Steve at COLUMN_STEVE
      (the south-west foot) facing the piston; the narrator at LEVER_NARRATOR behind the lever's pier facing south
      onto it (his face to the lens). Steve looks at the piston on the cut, turns to the narrator from 522 (by "asked"
      531), back to the piston on "my" (550); the narrator watches Steve, flips the lever on "said" 591 (flip_by: his head to the handle over
      6 frames, the swing on 591, the lever on the next frame); the column rises one block in 2 ticks; Steve's head
      tips back after it (ease 12), the narrator looks back at Steve. Heroes: Steve, the narrator. WHY THIS SIDE:
      from the stub's south-east camera the lever is behind the column; from here it stands beside it, and Steve
      had to move round to the column's south-west foot to stay in view.
    MEASURED (legday_sq_sq09_lifts_557_zones.png, _610_zones.png): "piston" 557: the piston at y 52-60 % (above
      the caption band), Steve's eyes x 24 %, y 47 %, face 70 px, 45 degrees off the lens; the narrator's eyes x 75 %,
      y 47.5 %, 53 px; the lever's handle x 62 %, y 49 % (clear). 607-626: the column's top at y 38 % against the sky,
      the people below the frame. palette_check sq09@557: all ok, heroes steve x 20-30 %, narrator x 72-80 %, both
      100 % inside.
    """
    f0, f1 = s.frame_start, s.frame_end
    piston = (-3.5, 9.5, 0.7)
    steve = C.actor("steve", "sq3")
    C.put(steve, f0, COLUMN_STEVE, toward=piston)
    efe = C.narrator("sq")
    C.put(efe, f0, LEVER_NARRATOR, toward=(-3.5, 10.5, 1.3))
    steve.look_at(f0, piston, ease=0)
    efe.look_at(f0, steve, ease=0)
    steve.look_at(f0 + 2, efe, ease=9)                                  # he asks the narrator (by "asked") ...
    steve.look_at(C.at(s, "my") - 2, piston, ease=6)                    # ... and looks at "my piston"
    t = redstone.flip_by(efe, C.column["lever"], C.at(s, "said"))
    C.column["piston"].power(t)
    steve.look_at(int(t) + 1, (-3.5, 9.5, 9.0), ease=12)                # his head tips back with the column
    efe.look_at(int(t) + 3, steve, ease=8)
    st.use(s, steve, efe)
    C.cam(s, None, focus=steve.head, ease=_ease(s, SQ09_KEYS), **SQ09_CAM)
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
    NOW: SQ10_CAM 16 mm f/4 low beside the well's north side (-0.8, 3.4, 0.6), looking north-north-west up at the
      column, a drift. Steve walks at speed from frame 627 from (-4.6, 8.0) to column_walk_end, at the lens; his head
      a little to his left and down on the cut; on "cheating" - 3 (641) it turns 60 degrees to his left (into the
      sun) and 16 up, over 6 frames, held to 668 (the CONTRACT: a strict profile shows a blank side: at 70 degrees
      the first try showed hair only). The narrator at LEVER_NARRATOR (as in sq09) tracking Steve with his head.
      Hero: Steve. (The b10 camera had a block of the well a block from the lens, a third of the frame.)
    MEASURED (legday_sq_sq10_cheating_654_zones.png): Steve's eyes x 33 %, y 48 %, face 117 px, head 48 degrees off
      the lens from 647 (his face at an angle, nose up); the column whole against the sky (top y 4 %); the narrator's
      eyes x 73 %, y 59 %, 33 px (inside the safe area, just). palette_check sq10@654: all ok, hero steve x 22-41 %,
      y 42-51 %, 100 % inside.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "sq3")
    a, e = C.stand((-4.6, 8.0)), C.P("column_walk_end")
    steve.place(f0, a, LC.yaw_to(a, e))
    efe = C.narrator("sq")
    C.put(efe, f0, LEVER_NARRATOR, toward=(-3.5, 10.5, 1.3))   # still at the lever (as in sq09)
    steve.look_at(f0, _head_dir(steve, f0, 12.0, -6.0), ease=0)
    steve.walk(f0, [a, e], ramp=(False, True))
    away = C.at(s, "cheating") - 3                       # his head turns away, nose up, to his left (into the sun):
    steve.look_at(away, _head_dir(steve, away + 6, 60.0, 16.0), ease=6)    # the face at an angle, not a blank side
    efe.look_at(f0, steve, ease=0)
    efe.track(f0 + 1, f1, steve, step=3, ease=4)
    st.use(s, steve, efe)
    C.cam(s, None, focus=steve.head, **SQ10_CAM)
    st.hero(s, "steve", steve)
    C.lights(s, "gold", near=(-4.0, 6.0, 1.0), radius=10.0)
