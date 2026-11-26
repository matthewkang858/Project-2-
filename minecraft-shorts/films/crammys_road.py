"""The Crammys, sequence ROAD: the village road at night. Beats 7, 9, 17 (shots rd07_chased, rd09_torch,
rd17_run_back), sky "night". One function per shot; the contract is in films/crammys_common.py (tags "rd...",
C.actor, C.cam, C.lights, C.hold, C.arrows, st.use / st.hero). STUB by the lead director: every shot builds and
renders; rd07 / rd17 are engine/music's 'lane' staging (tools/music_proof shot_lane / shot_lane17) plus the zombie
(films/crammys_set.py stage_b07), rd09 the set builder's stage_b09. Make it a film.

THE PLACE: the exit road runs north from the square (x -1..1). THE LANE (beats 7, 17): Kai's doorstep in front of
house_f (east side, door (4.5, 16.5)): his gold block + note block column at (1, 15), his lantern on a post at
(1, 17); across the road the narrator's door, house_e (-4.5, 15.5), facing east, its cobblestone step at (-4, 15).
Paths: C.v.paths["lane_home"] (up the road from the square and in at house_e's door: beat 7), "lane_to_square" (down
the road from the north toward the square: beat 17). Kai's spot: C.P("lane_kai") (2.35, 16.85, facing west).
THE EXIT GATE (beat 9): the two plains lamp posts at (-3, 24) and (3, 24): the last torches; north of them the night
meadow. Path C.v.paths["crammys_walk_out"] (0.3, 19.6) -> ... -> (5.0, 35.6) (beat 9 and on to the creeper).
THE SKY "night": the moon due EAST, low (az 0, el 21): the lane camera looks west with the moon behind it
(house_e's front moonlit); the gate camera looks north, the moon at its right. C.lights(s, "night") (x 1.3).
SHARED: CAMS["lane"] in rd07 AND rd17, EXACTLY (the story: "the same camera as the zombie chase"): ONE camera
(C.cam(s, "lane", focus=LANE_FOCUS, handheld=LANE_HANDHELD)) for both, the same handheld (0.004). THE DOOR: house_e opens and shuts in rd07 only. THE DISC and THE
ARROWS in rd17 (C.hold(steve, "music_disc_11", s); C.arrows(steve, s)).
TAGS TAKEN: steve_rd (rd07, rd09, rd17: never in two consecutive shots of the film), kai_rd, zombie_rd.
"""
import math

from films import crammys_common as CC

# rd07 and rd17 film through the SHARED camera C.cam(s, "lane", ...) (films/crammys_common.py CAMS["lane"] = engine/music
# 'lane', 16 mm f/2.8 from Kai's doorstep), with ONE focus and ONE handheld for both
LANE_FOCUS = (-1.5, 15.2, 1.3)          # the west side of the road where Steve runs (Kai's head soft in front)
LANE_HANDHELD = 0.004
B07_ARRIVE = CC.CS.B07_ARRIVE           # the set builder's: the zombie reaches the door step 54 frames into the shot


RD17_RUN = ((-1.3, 24.0), (-1.4, 18.5), (-1.5, 15.7), (-1.6, 13.0), (-1.4, 9.0), (-1.0, 6.5))   # rd17: back down
#                                        the WEST side of the road (in view over Kai's column from x 90 % at y 18.5
#                                        to x 3 % at y 12); its point RD17_MID (-1.5, 15.7) is mid-frame
RD17_MID = 2
RD17_EARLY = 0.7                        # on "arrows" he is this far short of RD17_MID (x 60 %): his arrows stick out
#                                        to his front right, so they show while he comes in from the right
RD09_D0 = 2.6                           # rd09: Steve's distance along crammys_walk_out on frame 1 (in frame, walking)
# THE CHASE (rd07; measured with tools/crammys_probe track rd07_chased 509-564:3)
RD07_RUN = ((-1.4, 8.5), (-1.5, 12.0), (-1.75, 14.4), (-2.4, 15.45), (-3.0, 15.5, 0.0), (-4.0, 15.5, 1.0),
            (-4.5, 15.5, 1.0), (-5.9, 15.5, 1.0))      # Steve's way home: up the WEST side of the road (lane_home's
#                                                    x 0.3 is behind Kai's column), the step, the door, inside
RD07_STEVE_D0 = 3.0                     # Steve's distance along RD07_RUN on frame 1 (sprinting; at the left edge)
RD07_ZOMBIE_GAP = 0.45                  # the zombie this far behind him on frame 1 (it falls back: 2.33 vs 5.61 b/s)
RD07_DOOR_X = -3.9                      # the door's threshold (the step's west edge is x -4.0)
RD07_CLEAR_X = -5.35                    # past the shut door's panel (x -5.0 .. -4.81) by half his width
RD07_OPEN_LEAD = 6                      # the door opens this many frames before he reaches it


def _along(path, d):
    """The polyline `path` from distance d along it on."""
    return CC.CS._along(path, d)


def _frame_x(c, a, b, x):
    """The first frame in a..b on which character c's x is at or west of `x` (b when never)."""
    for f in range(int(a), int(b) + 1):
        if c.pos_at(f).x <= x:
            return f
    return int(b)


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
      frame 1          THE HARD CUT FROM GOLD TO MOONLIT BLUE (the story's risk: "the first night frame must be clearly
                       moonlit blue"): the night sky over house_e's roof, Kai's lantern, his gold block and note block,
                       the back of his head soft in the foreground; something already moving (Steve or the camera)
      "chased"         Steve sprinting across the lane to his door, the zombie behind him with its arms out
      "home"           Kai's head turning to follow him
      "every night"    the door shuts in the zombie's face (before the last 3 frames of the shot)
    SHARED: CAMS["lane"] EXACTLY (rd17 repeats it); THE DOOR (house_e: v.door_open here only).
    NEIGHBOURS: before, gd06_line (the last gold frame: Steve's empty hand); after, jb08_eject (the party at night).
    MEASURED (the set builder, out/test/crammys_set_b07_chased*.png, music 'lane' + stage_b07): Kai's back of head at
      x 74 %, y 52 %, his lantern at 90 %. KNOWN LIMIT: the frame sees the road only north of y 14.4 and Kai's gold /
      note column at (1, 15) hides it south of y 15.9: Steve appears about 1.5 blocks before his door, so the sprint
      across the lane is about HALF A SECOND on screen, and the zombie (2.33 blocks/s) can be two blocks behind him,
      not four (four behind, it would still be hidden by the column when he goes in): B07_ARRIVE = 54 frames after
      the shot's start it reaches the step on the frame the door has shut. This shot is about 56 frames: the door
      shuts and the zombie arrives in its last frames: re-time so the door is shut at least 3 frames before the cut.
      A different lane camera would need Kai's column moved (an engine/music set change: not available).
    THE LEAD'S SCOUT (out/test/crammys_scout_rd07_chased_509_zones.png, and side by side with gd06's last frame:
      crammys_scout_cut_gd06_rd07.png): the first night frame reads as night at once (mean luma 59 against 106, the sky
      band rgb (63, 75, 144) against (174, 167, 177)): the starry blue sky over house_e's moonlit roof, its door torch,
      Kai's lantern burning at the right, the back of Kai's head dark in the foreground, the gold block and note block
      at the left. BUT NOTHING MOVES ON FRAME 509 except the handheld: Steve and the zombie are both still out of view
      (behind the column / off the frame) and the lane camera has no move: give the shot motion on its first frame
      (Kai's head already turning, a slow drift of the camera, Steve already in view).
    FALLBACKS (story): "Night shots on a dark lane: Steve and the zombie can sink into the background": the lamp post
      as key on the lens side and Kai's lantern in the foreground (here: Kai's lantern beside the lens); keep the
      background no brighter than the subject. An optional kicker on the back of Kai's head:
      C.kicker("rd_kai", s, C.P("lane_kicker_target"), 40) (music: documented, never rendered).
    """
    f0, f1 = s.frame_start, s.frame_end
    kai = C.actor("kai", "rd")
    C.put(kai, f0, "kai_lane", yaw=C.yaw("lane_kai"))
    steve = C.actor("steve", "rd")
    z = C.actor("zombie", "rd")
    path = [C.stand(p) if len(p) == 2 else p for p in RD07_RUN]
    # Steve: already sprinting on frame 1 (at the frame's left edge), up the west side of the road where the lens
    # sees him over Kai's column, straight through his door (opened as he comes: a player right-clicks a door from
    # up to 4.5 blocks away) into the house
    run = _along(path, RD07_STEVE_D0)
    steve.place(f0, run[0], CC.yaw_to(run[0], run[1]))
    in_end = steve.walk(f0, run, sprint=True, ramp=(False, True))
    fd = _frame_x(steve, f0, in_end, RD07_DOOR_X)              # his feet at the door's threshold
    fin = _frame_x(steve, f0, in_end, RD07_CLEAR_X)            # clear of the shut door's panel (x -5.0, his half width)
    steve.attack(fd - RD07_OPEN_LEAD, "right")                 # the right-click that opens it ...
    C.v.door_open("house_e", fd - RD07_OPEN_LEAD)              # ... open over 5 frames, before he reaches it
    shut = fin + 1
    steve.face(in_end, (C.P("zombie_stop")[0], 15.5, 1.6), ease=4)     # inside: he turns round (hidden by then)
    steve.attack(shut, "right")                                # ... and the right-click that shuts it
    C.v.door_open("house_e", shut, open=False)                 # shut 5 frames later
    # the zombie, arms out, BEHIND him on the same way at the game's 2.33 blocks/s (he sprints at 5.61: it falls
    # back), walking on up to the foot of his door step after the door has shut
    zp = [p for p in path if p[2] < 0.5] + [C.P("zombie_stop")]
    zp = [p for p in zp if p[0] > C.P("zombie_stop")[0] - 1e-6]
    zrun = _along(zp, max(0.0, RD07_STEVE_D0 - RD07_ZOMBIE_GAP))
    z.place(f0, zrun[0], CC.yaw_to(zrun[0], zrun[1]))
    z.aggro(f0, ease=0)
    zend = z.walk(f0, zrun)
    # Kai's head follows Steve (on frame 1 it is already turning toward him, down the road to the south) and then
    # the zombie at the shut door
    kai.look_at(f0, C.to_lens(kai, f0, steve.eye_point(f0 + 6), CC.CAMS["lane"]["pos"], 0.0), ease=0)
    kai.track(f0 + 1, fin, steve, step=3, ease=5)
    kai.look_at(fin + 3, z, ease=8)
    C.memo["rd07_frames"] = dict(door=fd, inside=fin, shut=shut, walk_end=in_end, zombie_stop=zend)
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
      frame 1          Steve already walking (pre-rolled if needed: steve_rd is not in jb08, the shot before)
      "walked out"     from behind and low: Steve passing the last lamp post, its torches big beside the lens, the
                       warm light sliding off his back, hands empty (no sword)
      "last torch"     he goes on into the blue meadow, getting small against a clean horizon; the camera stays at
                       the torch
    SHARED: path crammys_walk_out (it leads on to md10's steve_found). Steve's clothes: plain Steve, empty hands.
    NEIGHBOURS: before, jb08_eject (the party: Steve turns away from the stage toward the dark end of the square);
      after, md10_creeper (the meadow).
    MEASURED (crammys_set_b09_torch*.png, 20 mm f/4 from (-1.5, 18.8, 0.55)): the west lamp post with its torches big
      at the left (x 8-17 %); Steve walking away past it from x 80 % (f18) to 56 % (f44), small against a clean
      horizon; the road warm, the meadow blue, the skeleton's oak at the right.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "rd")
    # already walking on frame 1 and already in the frame (x about 80 %): RD09_D0 along crammys_walk_out (from
    # its start, (0.3, 19.6), he was at x 190 %, out of the frame for the first 15 frames: the technical review)
    pts = _along([tuple(p) for p in C.v.paths["crammys_walk_out"]], RD09_D0)
    steve.place(f0, pts[0], CC.yaw_to(pts[0], pts[1]))
    steve.walk(f0, pts, ramp=(False, True))
    st.use(s, steve)
    st.hero(s, "steve", steve)
    C.cam(s, "set:b09", focus=steve.head, handheld=0.004)
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
      frame 1          the lane EXACTLY as in rd07 (CAMS["lane"]), now EMPTY of Kai: only his lantern, gold block
                       and note block; something already moving
      "ran to the stage"   Steve sprinting the other way, right to left, toward the lantern glow of the square, the
                       disc in his hand (it may be edge-on here, the story allows it)
      "arrows still in me"  the TWO ARROWS plain on him (C.arrows: the same two as md13's); in focus as he passes
    SHARED: CAMS["lane"] EXACTLY (the same focus and handheld as rd07); THE DISC (C.hold(steve, "music_disc_11", s));
      THE ARROWS (C.arrows(steve, s)).
    NEIGHBOURS: before, md16_disc (ground level in the meadow: his feet stop at the disc); after, jb18_nobody_asked.
    MEASURED (crammys_set_b17_run_back_zones.png): Steve sprinting right to left past the doorstep with the disc,
      mid-frame and motion-blurred. The run across the visible road is short (see rd07's KNOWN LIMIT). The lead's
      scout of the first stub (he started on frame 1 at the path's first point): on "arrows" (1067) he was already
      behind Kai's column, one leg showing (out/test/crammys_pal_rd17_run_back_1067.png; palette passes: trousers min
      channel 25). The stub now starts him up the road so that he crosses y RD17_MID_Y on "arrows" (tools.crammys_geo:
      his eyes at x 88 % on 1060, 50 % on 1067 "arrows", 9 % on 1075, then behind the note block: on screen about 16
      frames). The arrows stick out to his front RIGHT (toward the far side from this lens when he runs south):
      from here they show as shafts ahead of his chest, at best.
    RISKS (story): "Kai said it sounded just like me coming home" only works if this camera is identical to rd07's:
      it is the same constant. "Arrows stuck in Steve are thin at phone size": he passes 3-5 blocks from the lens.
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
