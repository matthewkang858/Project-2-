"""The Crammys, sequence ROAD: the village road at night. Beats 7, 9, 17 (shots rd07_chased, rd09_torch,
rd17_run_back), sky "night". One function per shot; the contract is in films/crammys_common.py (tags "rd...",
C.actor, C.cam, C.lights, C.hold, C.arrows, st.use / st.hero). STUB by the lead director, RE-STAGED after the two
checks of the plan: every shot builds and renders; rd07 and rd17 run on the WEST side of the road through the
RAISED lane camera (see THE LANE), rd09 is the set builder's stage_b09 with Steve in frame on frame 1. Make it a film.

THE PLACE: the exit road runs north from the square (x -1..1, a dirt path). THE LANE (beats 7, 17): Kai's doorstep
in front of house_f (its west wall x 4, door (4, 16)): his gold block + note block column at (1, 15) (blocks z 0-2),
his lantern on a fence post at (1, 17); across the road the narrator's house_e, its oak door at (-5, 15) (block
x -5..-4, z 1-3, facing east; shut, its panel lies at the block's WEST face, x -5.0 .. -4.81), the cobblestone stairs
before it at (-4, 15), poppy planters at (-4, 14) and (-4, 16). Kai stands at C.P("kai_lane") (2.05, 16.85), in the
gap between his column and his post, facing west (C.yaw("lane_kai")).
THE LANE CAMERA (CAMS["lane"], films/crammys_common.py: SHARED by rd07 and rd17, EXACTLY): 16 mm f/2.8 from Kai's
doorstep RAISED to z 3.1 (3.84, 16.5, 3.1) looking down the lane at the door, a slow drift. Why raised: engine/music's
lane camera (z 1.7) saw the road only between Kai's column and y 14.4: in the first stub the column hid Steve through
"chased" and "home" and the zombie through 546 (the story check: Steve clear only on 550-552, from behind). From z 3.1
it looks over the column: a figure on the WEST side of the road (x -1.5) is seen eyes and chest from x 5 % (y 12.2)
to the door (x 50 %), knees hidden behind the note block from y 13 to 15 (tools.crammys_geo spots). The cost: Kai's
head sits LOW, x 58-85 %, y 62-82 % (eyes 73-76 %, y 72 %): in the caption band (a soft foreground shape, the back of
his head; it reads by its turn, the caption word sits over its left edge); his lantern at the right edge (x 88-100 %,
y 47-58 %); the column at the left (x 5-48 %, y 52-90 %); house_e's door at x 52 %, y 37-50 %, the starry sky above
its roof (the top 13 %). Kai's back of head shows the kai skin's red hair clip (not a face).
THE EXIT GATE (beat 9): the two plains lamp posts at (-3, 24) and (3, 24): the last torches; north of them the night
meadow. Path C.v.paths["crammys_walk_out"] (0.3, 19.6) -> ... -> (5.0, 35.6) (beat 9 and on to the creeper).
THE SKY "night": the moon due EAST, low (az 0, el 21): the lane camera looks west with the moon behind it
(house_e's front moonlit); the gate camera looks north, the moon at its right. C.lights(s, "night") (x 1.3).
SHARED: CAMS["lane"] in rd07 AND rd17, EXACTLY (the story: "the same camera as the zombie chase"): ONE camera
(C.cam(s, "lane", focus=LANE_FOCUS, handheld=LANE_HANDHELD)) for both, the same focus and handheld (0.004). THE DOOR:
house_e opens and shuts in rd07 only. THE DISC and THE ARROWS in rd17 (C.hold(steve, "music_disc_11", s);
C.arrows(steve, s)).
TAGS TAKEN: steve_rd (rd07, rd09, rd17: never in two consecutive shots of the film), kai_rd, zombie_rd.
MEASURE BEFORE YOU RENDER: `$BPY -m tools.crammys_probe track rd07_chased 509-564:3` (where everybody is, frame by
frame, in the frame and seen or hidden; the door's angle; the arrows' fletching in rd17), `... memo` (the event
frames the stubs leave in C.memo: rd07_frames).
"""
import math

from engine import characters, shots
from films import crammys_common as CC

# rd07 and rd17 film through the SHARED camera C.cam(s, "lane", ...) (films/crammys_common.py CAMS["lane"]: 16 mm f/2.8
# from Kai's doorstep, raised to z 3.1), with ONE focus and ONE handheld for both
LANE_FOCUS = (-1.5, 15.2, 1.3)          # the west side of the road where Steve runs (Kai's head soft in front)
LANE_HANDHELD = 0.004


RD17_RUN = ((-1.3, 24.0), (-1.4, 18.5), (-1.5, 15.7), (-1.6, 13.0), (-1.4, 9.0), (-1.0, 6.5))   # rd17: back down
#                                        the WEST side of the road (in view over Kai's column from x 90 % at y 18.5
#                                        to x 3 % at y 12); its point RD17_MID (-1.5, 15.7) is mid-frame
RD17_MID = 2
RD17_EARLY = 1.15                       # on "arrows" he is this far short of RD17_MID (x 65 %): his arrows stick out
#                                        to his front right, so they show while he comes in from the right
RD09_D0 = 1.2                           # rd09: Steve's distance along RD09_WALK on frame 1 (in frame, walking)
# rd09: low behind him at the gate (the set's b09, 20 mm from (-1.5, 18.8, 0.55), static there), re-aimed 0.25 to the
# right so that his head is inside the safe area on frame 1 (x 64-83 %), with a slow rise (0.55 -> 0.7) and tilt up
# drifting a touch left: the last torch comes further into the top left as he gets small in the middle
RD09_CAM = dict(pos=(-1.5, 18.8, 0.55), target=(1.45, 34.0, 1.6), pos1=(-1.5, 18.72, 0.7),
                target1=(1.2, 34.0, 1.85), lens=20.0, fstop=2.8)
RD09_WALK = ((-0.35, 20.6), (0.45, 25.5), (0.6, 30.0), (1.7, 31.9), (1.9, 32.1), (2.6, 33.4), (5.0, 35.6))
#                                         his way out: up the WEST half of the exit road between the gate's lamp
#                                         posts, then crammys_walk_out from (0.6, 30) on to the creeper (md10)
# THE CHASE (rd07; measured with tools/crammys_probe track rd07_chased 509-564:3)
RD07_RUN = ((-1.4, 8.5), (-1.5, 12.0), (-1.75, 14.4), (-2.4, 15.45), (-2.7, 15.5),
            (-4.5, 15.5), (-5.9, 15.5))      # Steve's way home: up the WEST side of the road (lane_home's x 0.3 is
#                                              behind Kai's column), over his stairs, through the door, inside.
#                                              Walked FLAT (Player.walk measures a path in 3D: risers in the path
#                                              slowed his sprint by 2 frames to the door), then the height re-keyed
#                                              by _step_up with RD07_STEPS
RD07_STEPS = ((-2.7, 0.5), (-3.2, 1.0))     # house_e's cobblestone stairs ((-4, 15), facing west: the low step
#                                              x -3.5..-3 tops at z 0.5, the high one x -4..-3.5 at z 1, the house
#                                              floor z 1): the game steps a player up a riser of 0.6 or less at once
#                                              when his 0.6-wide box meets it, i.e. when his centre is 0.3 short of
#                                              it (x -2.7 and -3.2); the lead's 1-block ramp from x -3 sank his feet
#                                              into the stair. (x where the step-up starts, the height after it)
RD07_STEP_FRAMES = 0.8                  # the rise of one step-up (a fraction of a tick, blurred)
RD07_STEVE_D0 = 3.0                     # Steve's distance along RD07_RUN on frame 1 (sprinting; at the left edge)
RD07_ZOMBIE_GAP = 0.45                  # the zombie this far behind him on frame 1 (it falls back: 2.33 vs 5.61 b/s)
RD07_DOOR_X = -3.9                      # the door's threshold (the step's west edge is x -4.0)
RD07_CLEAR_X = -5.35                    # past the shut door's panel (x -5.0 .. -4.81) by half his width
RD07_OPEN_LEAD = 6                      # his right-click opens the door this many frames before he reaches it
RD07_TURN = 3                           # frames of his turn back to the door inside (a player turns with the mouse)
RD07_SHUT_AFTER_NIGHT = 1               # his right-click that shuts the door: this many frames after "night" appears
#                                         (the door is shut one frame later, in the middle of the word)
RD07_KAI_LOOK = 4                       # Kai's head leaves his note block for the road this many frames after the cut
RD07_KAI_TAP = 2                        # Kai taps his note block this many frames before the cut (the note one tick
#                                         later: in the air on frame 1; the swing at its top 2.4 frames after the tap)
RD07_KAI_HAND = "left"                  # his near hand: turned to the block (south-south-west), his right arm is on
#                                         the far side of his body from the lens and its swing was not seen
#                                         (crammys_road_rd07_chased_510: a left-handed player, the game's "Main
#                                         Hand: Left" option, swings the left arm)


def _along(path, d):
    """The polyline `path` from distance d along it on."""
    return CC.CS._along(path, d)


def _frame_x(c, a, b, x):
    """The first frame in a..b on which character c's x is at or west of `x` (b when never)."""
    for f in range(int(a), int(b) + 1):
        if c.pos_at(f).x <= x:
            return f
    return int(b)


def _step_up(c, f_from, f_to, steps, rise=RD07_STEP_FRAMES):
    """Re-key the height of a walk west along y (c.walk(f_from, flat route) ending on f_to) so that it steps up each
    riser as the game does: the height holds until the root's x passes the riser's `edge` (a fractional frame),
    then rises to `z_after` over `rise` frames while he runs on at full speed. Returns the step-up frames."""
    z = c.pos_at(f_from).z
    keys, out, f = [(float(f_from), None, "LINEAR")], [], int(f_from)
    for edge, z_after in steps:
        while f < f_to and c.pos_at(f + 1).x > edge:
            f += 1
        a, b = c.pos_at(f).x, c.pos_at(f + 1).x
        t = f + (a - edge) / (a - b) if abs(a - b) > 1e-6 else float(f)
        keys += [(t, z, "LINEAR"), (t + rise, z_after, "LINEAR")]
        out.append(t)
        z = z_after
    keys.append((float(f_to), z))
    characters._segment(c.root, "location", 2, keys)
    return out


def _door_snap(C, name, a, b):
    """A door changes state AT ONCE in the game (no swing): v.door_open(..., frames=1) keys each change over one
    frame, and the motion blur of that frame showed a ghosted half-open panel (The Hello, dg20). Hold every key of
    the door's swing channel from frame a to b CONSTANT (films/hello_door_gold.py's fix)."""
    for d in C.v._door_sets[name]:
        for fc in shots.fcurves_of(d):
            if fc.data_path == "rotation_euler" and fc.array_index == 2:
                for k in fc.keyframe_points:
                    if a <= k.co.x <= b:
                        k.interpolation = "CONSTANT"
                fc.update()


def rd07_chased(st, s, C, nar):
    """BEAT 7  "I just get chased home every night."   frames 509-564 (56 f, 2.33 s), sky night.
    Words: I 511, just 513, get 517, chased 522, home 530, every 540, night 547. The voice ends on 555; the shot runs on
    9 frames after it (0.38 s).

    STORY (beat 7): Hard cut from gold to moonlit blue. From Kai's doorstep: the back of Kai's head and shoulder soft in
    the foreground beside a lantern, his gold block and note block. Steve sprints across the lane left to right, a
    zombie four blocks behind with its arms out. Kai's head turns to follow him. Steve goes through his front door and
    it shuts in the zombie's face.
    Cast: Steve, zombie, Kai. Effects: zombie walking with arms out, oak door opening and shutting, lantern, gold block
    and note block on Kai's doorstep, lamp post as key light, player sprint.

    MUST BE SEEN, ON WHICH WORD
      frame 1          THE HARD CUT FROM GOLD TO MOONLIT BLUE ("the first night frame must be clearly moonlit blue"):
                       the starry sky over house_e's roof, Kai's lantern, his column, the back of his head soft in the
                       foreground, ALREADY TURNING toward the road (the camera drifting too)
      "chased"         Steve sprinting up the lane toward his door, the zombie behind him with its arms out
      "home"           Steve at his door step; Kai's head following him
      "every night"    the door shuts in the zombie's face: shut by "night", the zombie walking up to it
    SHARED: CAMS["lane"] EXACTLY (rd17 repeats it: position, aim, move, lens, focus LANE_FOCUS, handheld); THE DOOR
      (house_e: v.door_open here only). Places: kai_lane, zombie_stop (the foot of the stairs, (-2.85, 15.5)).
    NEIGHBOURS: before, gd06_line (the last gold frame: Steve's empty hand); after, jb08_eject (the party at night).
    THE STAGING (re-staged after the checks; the first stub played the chase backwards: the zombie started 3.6 blocks
      AHEAD of Steve and he overtook it at 539 behind Kai's column, the door opened only on 561-566 and shut inside
      jb08, he went through it shut). Now: Steve sprints (5.61 b/s, at speed on frame 1) up the WEST side of the road
      (RD07_RUN, at the frame's left edge on frame 1), the stairs, straight through his door (opened by his
      right-click RD07_OPEN_LEAD = 6 frames before he reaches it: a door opens at once in the game; the engine swings
      it over 5 frames), inside he turns and right-clicks it shut once he is past its panel; the zombie (2.33 b/s,
      arms out from frame 1) follows 0.45 block behind him on the same way and FALLS BACK (the game's speeds: a
      sprinting player outruns a zombie), then walks on up to the foot of the stairs. Kai's head tracks Steve, then
      turns to the zombie at the shut door. This is the only order that is true to the game: a zombie that reached the
      door as it shut would have had to be AHEAD of Steve when both were in view.
    MEASURED (tools.crammys_probe track rd07_chased; memo rd07_frames):
      509  Kai's head turning (eyes x 73 %, y 72 %); Steve just beyond the left edge (eyes x -4 %), the zombie behind
      512  Steve in the frame (eyes x 5 %, y 49 %, chest seen over the column)
      519  the zombie in the frame (x 2 %), arms out; 2.2 blocks behind Steve
      522  "chased": Steve x 35 %, the zombie x 6 %, both eyes and chest seen
      529  his right-click: the door opens 529-534 (90 degrees on 534); 530 "home": Steve at the foot of the stairs,
           x 50 %; the zombie x 16 %
      536  his feet at the threshold (x -3.9); 542 inside, past the panel (x -5.35)
      543  the door starts to shut; SHUT ON 548 ("night" 547: 9 degrees); the zombie at x 38 %, 2 blocks off
      561  the zombie at the foot of the stairs (zombie_stop), standing at the shut door, arms out, to the cut (564)
      Stills (540x960, 16 spp, zones): out/test/crammys_scout_lane_rd07_chased_509 / _522 / _530 / _547_zones.png.
      Steve's and the zombie's faces are 36-43 px (a 16 mm wide: figures about 9 % of the frame high).
    FALLBACKS (story): "Night shots on a dark lane: Steve and the zombie can sink into the background": they run in
      front of house_e's moonlit front (warm door torch above them); keep the background no brighter than them. An
      optional kicker on the back of Kai's head: C.kicker("rd_kai", s, C.P("lane_kicker_target"), 40) (music:
      documented, never rendered). The story's "four blocks behind": 2.2 on "chased", 3.4 on "home" (it falls back).
    """
    f0, f1 = s.frame_start, s.frame_end
    kai = C.actor("kai", "rd")
    bells = C.bd.notes["lane"]                                 # his note block on gold at the top of his column
    steve = C.actor("steve", "rd")
    z = C.actor("zombie", "rd")
    path = [C.stand(p) if len(p) == 2 else p for p in RD07_RUN]
    # Kai on his doorstep, turned to his note block (a player faces the block he plays), playing his bells as the
    # night shot opens: the swing ON the cut, the note one tick later, rising over the block (frame 1 moves); the
    # same Kai of beat 3 ("he plays bells") at his own door
    # (kai_rd is in no shot before this one: he is placed RD07_KAI_TAP frames before the cut, so that the note is
    # already in the air on frame 1 and his arm is at the top of its swing)
    C.put(kai, f0 - RD07_KAI_TAP, "kai_lane", toward=bells.center[:2])
    # the zombie, arms out, BEHIND him on the same way at the game's 2.33 blocks/s (he sprints at 5.61: it falls
    # back), walking on up to the foot of his stairs after the door has shut, and standing there facing it
    zp = list(path[:5]) + [C.P("zombie_stop")]
    zp = [p for p in zp if p[0] > C.P("zombie_stop")[0] - 1e-6]
    zrun = _along(zp, max(0.0, RD07_STEVE_D0 - RD07_ZOMBIE_GAP))
    z.place(f0, zrun[0], CC.yaw_to(zrun[0], zrun[1]))
    z.aggro(f0, ease=0)
    zend = z.walk(f0, zrun)
    z.look_at(zend, C.P("lane_door_target"), ease=6)           # its head up at the shut door
    # Steve: already sprinting on frame 1 (at the frame's left edge), up the west side of the road where the lens
    # sees him over Kai's column, up his stairs, through his door (his right-click opens it as he comes: a player
    # reaches a door from up to 4.5 blocks) into the house; inside he turns back and right-clicks it shut
    run = _along(path, RD07_STEVE_D0)
    steve.place(f0, run[0], CC.yaw_to(run[0], run[1]))
    in_end = steve.walk(f0, run, sprint=True, ramp=(False, True))
    ups = _step_up(steve, f0, in_end, RD07_STEPS)              # his two step-ups onto the stairs
    fd = _frame_x(steve, f0, in_end, RD07_DOOR_X)              # his feet at the door's threshold
    fin = _frame_x(steve, f0, in_end, RD07_CLEAR_X)            # clear of the shut door's panel (x -5.0, his half width)
    opens = fd - RD07_OPEN_LEAD
    steve.attack(opens, "right")                               # the right-click that opens it: the door is open one
    C.v.door_open("house_e", opens, frames=1)                  # tick later (the server's block update), at once
    turned = steve.turn(fin - 1, CC.yaw_to((-5.9, 15.5), (-4.0, 15.5)), ease=RD07_TURN)   # back round to the door
    #                                                            (still sliding west: he let go of the keys) ...
    steve.look_at(turned, z, ease=3)                           # ... a look back out at the zombie coming ...
    shut = max(turned + 2, C.at(s, "night") + RD07_SHUT_AFTER_NIGHT)
    steve.attack(shut, "right")                                # ... and the right-click that shuts it on "night"
    C.v.door_open("house_e", shut, open=False, frames=1)       # (shut one tick later, at once)
    _door_snap(C, "house_e", opens, shut + 2)
    # Kai: the tap on the cut, his eyes on the note; then his head goes to the road as Steve comes in (512), follows
    # him up to his door, and his body comes round after it to the zombie at the shut door (the head alone turns
    # at most 70 degrees)
    kai.look_at(f0 - RD07_KAI_TAP, bells.center, ease=0)      # his eyes on the block's face
    bells.tap(kai, f0 - RD07_KAI_TAP, use=False, camera=s, seed=7, hand=RD07_KAI_HAND)    # a left-click: the block
    #                                                            plays its note again (no re-tuning)
    look = f0 + RD07_KAI_LOOK
    kai.track(look, fin, steve, step=3, ease=6)
    C.turn_to(kai, fin + 2, z, ease=10)
    kai.track(fin + 12, f1, z, step=4, ease=4)
    C.memo["rd07_frames"] = dict(click=opens, open=opens + 1, steps=[round(t, 1) for t in ups], door=fd,
                                 inside=fin, turned=turned, click_shut=shut, shut=shut + 1, walk_end=in_end,
                                 zombie_stop=zend)
    st.use(s, kai, steve, z)
    st.hero(s, "steve", steve)
    st.hero(s, "zombie", z)
    C.cam(s, "lane", focus=LANE_FOCUS, handheld=LANE_HANDHELD)
    C.lights(s, "night")


def rd09_torch(st, s, C, nar):
    """BEAT 9  "So I walked out past the last torch."   frames 655-715 (61 f, 2.54 s), sky night.
    Words: So 657, I 661, walked 664, out 671, past 676, the 684, last 686, torch 694. The voice ends on 706; the shot
    runs on 9 frames after it (0.38 s).

    STORY (beat 9): From behind and low on the exit road. Steve walks away from the lens past the last lamp post, hands
    empty, no sword. The warm light slides off his back and he goes on into the blue meadow. The camera stays at the
    torch and lets him get small.
    Cast: Steve. Effects: last lamp post with torches, warm pool of torch light against moonlight.

    MUST BE SEEN, ON WHICH WORD
      frame 1          Steve already walking, already in the frame (the stub: RD09_D0 = 2.6 blocks along
                       crammys_walk_out, ramp in off: at walking speed on frame 1)
      "walked out"     from behind and low: Steve passing the last lamp post, its torches big beside the lens, the
                       warm light sliding off his back, hands empty (no sword)
      "last torch"     he goes on into the blue meadow, getting small against a clean horizon; the camera stays at
                       the torch
    SHARED: path crammys_walk_out (it leads on to md10's steve_found). Steve's clothes: plain Steve, empty hands.
    NEIGHBOURS: before, jb08_eject (the party: Steve turns away from the stage toward the dark end of the square);
      after, md10_creeper (the meadow).
    MEASURED (crammys_set_b09_torch*.png, 20 mm f/4 from (-1.5, 18.8, 0.55)): the west lamp post with its torches big
      at the left (x 8-17 %); Steve walking away past it from x 80 % (f18) to 56 % (f44), small against a clean
      horizon; the road warm, the meadow blue, the skeleton's oak at the right. The technical check: from the path's
      start (0.3, 19.6) he was at x 190 % on 655 and first in the frame about 670 (nothing moving for 0.6 s): the
      stub now starts him 2.6 blocks along it (the lead's still out/test/crammys_scout_rd09_torch_656_zones.png).
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "rd")
    # already walking on frame 1 and already in the frame (x about 80 %): RD09_D0 along crammys_walk_out (from
    # its start, (0.3, 19.6), he was at x 190 %, out of the frame for the first 15 frames: the technical review)
    pts = _along([C.stand(p) for p in RD09_WALK], RD09_D0)
    steve.place(f0, pts[0], CC.yaw_to(pts[0], pts[1]))
    steve.walk(f0, pts, ramp=(False, True))
    st.use(s, steve)
    st.hero(s, "steve", steve)
    C.cam(s, None, focus=steve.head, handheld=0.004, **RD09_CAM)
    C.lights(s, "night")


def rd17_run_back(st, s, C, nar):
    """BEAT 17  "I ran to the stage with arrows still in me."   frames 1037-1102 (66 f, 2.75 s), sky night.
    Words: I 1039, ran 1042, to 1048, the 1050, stage 1052, with 1064, arrows 1067, still 1078, in 1085, me 1089. The
    voice ends on 1095; the shot runs on 7 frames after it (0.29 s).

    STORY (beat 17): The same camera as the zombie chase, from Kai's doorstep, now empty: only his lantern, gold block
    and note block. Steve sprints the other way, right to left, toward the lantern glow of the square, two arrows
    sticking out of him, the disc in his hand (it may be edge-on here; the arrows are the subject).
    Cast: Steve. Effects: two arrows stuck in the player, held music disc, player sprint, party glow at the end of the
    lane, camera reused from beat seven.

    MUST BE SEEN, ON WHICH WORD
      frame 1          the lane EXACTLY as in rd07 (CAMS["lane"], the same drift), now EMPTY of Kai: only his lantern,
                       gold block and note block, the door shut (the story's "now empty" is this shot's first picture)
      "ran to the stage"   Steve comes in from the right, sprinting right to left toward the lantern glow of the
                       square, the disc in his hand (edge-on allowed)
      "arrows still in me"  the TWO ARROWS plain on him (C.arrows: the same two as md13's) as he crosses the frame
    SHARED: CAMS["lane"] EXACTLY (the same focus LANE_FOCUS and handheld as rd07); THE DISC (C.hold(steve,
      "music_disc_11", s)); THE ARROWS (C.arrows(steve, s)).
    NEIGHBOURS: before, md16_disc (ground level in the meadow: his feet stop at the disc); after, jb18_nobody_asked.
    THE STAGING (re-staged with the raised lane camera): back down the WEST side of the road (RD17_RUN, x -1.5: in view
      over Kai's column), sprinting at speed from beyond the right edge, timed to be RD17_EARLY = 0.7 block short of
      mid-frame on "arrows" (x 60 %). The aligned arrows stick out to his FRONT RIGHT (toward where the skeleton
      stood): running south past an east lens they show while he comes in from the right and hide behind his head
      once he is past the middle.
    MEASURED (tools.crammys_probe track rd17_run_back; 'arrow' rows = the fletching end, 'ok' = the lens sees it):
      1037-1056 the empty lane (the camera's drift is the only movement: the story's "now empty")
      1057  Steve in at the right (eyes x 85 %), behind the lantern post until about 1057
      1058-1069  BOTH FLETCHINGS SEEN (12 frames, 0.5 s), x 75 -> 50 %, y 48-52 %; Steve's eyes x 81 -> 52 %
      1067  "arrows": eyes x 60 %, y 51 %, face 58 px; the fletchings at x 57 / 54 %
      1070-1073  the shoulder arrow hidden behind his head, the chest arrow from 1072; 1083 he is out at the left
      (the first stub's run on x 0.4 was behind Kai's column on "arrows": out/test/crammys_pal_rd17_run_back_1067.png)
      Still: out/test/crammys_scout_rd17_run_back_1064_zones.png.
    RISKS (story): "Kai said it sounded just like me coming home" only works if this camera is identical to rd07's:
      it is the same constant. "Arrows stuck in Steve are thin at phone size": he passes 4-6 blocks from a 16 mm lens:
      the fletching crosses are about 10-15 px; sharp (LANE_FOCUS is on his way, (-1.5, 15.2, 1.3)).
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "rd")
    # timed so that he crosses the middle of the frame (RD17_RUN's point RD17_MID) on "arrows", sprinting at speed from
    # a point up the road beyond the frame's right edge
    pts = [C.stand(p) for p in RD17_RUN]
    d_mid = sum(math.dist(a, b) for a, b in zip(pts[:RD17_MID + 1], pts[1:RD17_MID + 1]))
    lead = d_mid - RD17_EARLY - CC.players.SPRINT_SPEED * (C.at(s, "arrows") - f0) / 24.0     # along the way on f0
    run = _along(pts, max(0.0, lead))
    steve.place(f0, run[0], CC.yaw_to(run[0], run[1]))
    C.arrows(steve, s)
    C.hold(steve, "music_disc_11", s)
    steve.walk(f0, run, sprint=True, ramp=(False, True))
    st.use(s, steve)
    st.hero(s, "steve", steve)
    C.cam(s, "lane", focus=LANE_FOCUS, handheld=LANE_HANDHELD)
    C.lights(s, "night")
