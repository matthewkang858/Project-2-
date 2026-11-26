"""The Crammys, sequence MEADOW: the night meadow north of the exit gate. Beats 10-16 (shots md10_creeper,
md11_skeleton, md12_middle, md13_shot (beats 13 AND 14: one take), md15_kill, md16_disc), sky "night". One function
per shot; the contract is in films/crammys_common.py (tags "md...", C.actor, C.cam, C.lights, C.shoot_steve, C.arrows,
C.disc_drop, st.use / st.hero). STUB by the lead director: every shot builds and renders; its staging is the
engine/hostiles recipe ("THE CRAMMYS, beat by beat" in its docstring) as the set builder staged it on this set
(films/crammys_set.py stage_b10 .. stage_b16), filmed by the set builder's cameras (CAMERAS b10-b16). Make it a film.

THE PLACE (films/crammys_set.py night_meadow): flat grass (z 0) north of the gate to y 50, plants cleared on
x -4..15, y 30..47 and on every low camera's view; THE SKELETON'S OAK (6 logs, leaves from z 3) at (13, 44), east of
the line; two village oaks taken out for a clean north horizon. THE LINE of beat 12 runs east-west at y 40: creeper
C.P("creeper_line") (1.8, 40), Steve C.P("middle") (5.0, 40), skeleton C.P("skeleton_line") (8.2, 40): 3.2 blocks
either side (the creeper's fuse range is 3). Every meadow anchor: steve_found, creeper_found (beat 10), skeleton_oak
(11), steve_enter -> middle (12, path crammys_into_middle), steve_shot (yaw 135: the skeleton 45 degrees to his front
right), creeper_behind_from -> creeper_behind_to (13-14), creeper_turn, steve_round_from -> steve_round_to (path
crammys_round), skeleton_close (15), disc_rest, steve_disc_from -> steve_disc (16).
THE SKY "night": the moon due EAST, low (az 0, el 21): the cameras that look north (md10, md12, md15) have it at
their right, out of frame: figures side-lit, standing AGAINST THE NORTHERN SKY above a clean horizon (the story's
answer to "green on green": the low camera); md11 looks east into it: the moon at the edge of the oak's canopy.
C.lights(s, "night") (x 1.3: the gate's lamps are 10-20 blocks behind; they light nothing here).
SHARED: THE ARROWS: md13 shoots them with C.shoot_steve(sk, steve, f, 0 / 1) (ARROW_HITS: the chest, then shoulder_r,
BOTH aligned with their flight; knockback 0.1); steve_md then carries them to the end, and every OTHER Steve twin from
md15 on gets C.arrows(steve, s) (both aligned with the set's ARROW_FLIGHT: the flight from skeleton_line to
steve_shot in his own frame): KEEP md13's skeleton at skeleton_line and Steve at steve_shot facing yaw 135 when the
arrows land, or the later twins' arrows will not match his (say so in your result if you must move them). THE DISC:
C.disc_drop(...) ONCE, in md15, ON the killing blow at the creeper's feet; md16 films the same item
(C.memo["md_disc"]); it must still be dropped in md16's first frames ("the smoke thins").
GAME TRUTH: knockback=0.1 (or max_back) on every arrow near other characters (characters do not collide: the game's
0.4 throws a creeper about 2 blocks along the arrow, into Steve); the creeper takes two arrows here (the game needs
five or more: the story's compression); a skeleton's kill gives NO experience orbs; the creeper dies tipped over,
still swollen, then the poof (hostiles die). Arrows are 0.045 block thin: they read from 3-4 blocks.
TAGS TAKEN: steve_md (md10, md12, md13, md15, md16), creeper_md (md10, md12, md13, md15), skeleton_md (md11, md12,
md13, md15). A twin for a pre-roll: C.actor("steve", "md2") ...
"""

import math

from films import crammys_common as CC

CS = CC.CS

MD12_LOOK = (2, 2)          # md12: the look left starts this many frames after he stops, the look right this many
#                             after the look left has arrived (7-frame turns)
MD12_CREEPER = 16           # md12: the creeper starts toward him this many frames after he stops
MD15_DRAW = 24              # md15: the skeleton twin's first draw (frames before the first hit)
MD15_KILL_AFTER = 20        # md15: the killing arrow lands this many frames after the first (on "shot" + 20)
MD15_FUSE = 3               # md15: the creeper starts to swell on f0 + 3 (it would explode 35 frames later)


def _cam(s, beat):
    return dict(CS.CAMERAS[beat])


def md10_creeper(st, s, C, nar):
    """BEAT 10  "I found a creeper."   frames 716-756 (41 f, 1.71 s), sky night.
    Words: I 718, found 722, a 730, creeper 731. The voice ends on 744; the shot runs on 12 frames after it (0.50 s).

    STORY (beat 10): Low over Steve's shoulder, camera at hip height so the creeper's head stands against the night sky
    above the horizon, not against the grass. It faces him, perfectly still. Then it takes one slow step toward him.
    Cast: Steve, creeper. Effects: creeper standing, one slow step, low camera with a clean horizon.

    MUST BE SEEN, ON WHICH WORD
      frame 1          low over Steve's soft shoulder, the creeper's head against the night sky above the horizon
                       (never against the grass), facing him, perfectly still; the camera already drifting
      after "creeper"  its ONE slow step toward him (hostiles Creeper.step: half a block over 14 frames), done well
                       before the cut (this shot is short: about 40 frames)
    NEIGHBOURS: before, rd09_torch (from behind at the gate, Steve walking into the meadow); after, md11_skeleton.
    MEASURED (crammys_set_b10_creeper_zones.png, 40 mm f/4 from (5.85, 34.1, 0.9)): the creeper's head against the sky
      at x 58 %, y 41 %, over Steve's soft shoulder. The set builder stepped it at f0 + 30: in this 40-frame shot that
      is too late (the step ends at f0 + 44): the stub steps it at f0 + 16.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "md")
    cr = C.actor("creeper", "md")
    C.put(steve, f0, "steve_found")
    C.put(cr, f0, "creeper_found")
    cr.look_at(f0, steve, ease=0)
    steve.look_at(f0, cr, ease=0)
    cr.step(min(f0 + 16, f1 - 18), steve)
    st.use(s, steve, cr)
    st.hero(s, "creeper", cr)
    C.cam(s, "set:b10", focus=cr.head, pos1=tuple(p + d for p, d in zip(_cam(s, "b10")["pos"], (-0.08, 0.12, 0.0))))
    C.lights(s, "night")


def md11_skeleton(st, s, C, nar):
    """BEAT 11  "I found a skeleton."   frames 757-796 (40 f, 1.67 s), sky night.
    Words: I 759, found 762, a 770, skeleton 771. The voice ends on 787; the shot runs on 9 frames after it (0.38 s).

    STORY (beat 11): Under a lone oak, the pale skeleton bright against the dark trunk, the moon behind the branches if
    the film's one moon position allows it. The skeleton turns its skull to the lens and lifts its bow.
    Cast: skeleton. Effects: skeleton with bow, skull turn, bow raised, lone oak, moon through the branches.

    MUST BE SEEN, ON WHICH WORD
      frame 1          under the lone oak, the pale skeleton bright against the dark trunk, the canopy over it
      "found"          the skeleton turns its skull to the lens ...
      "skeleton"       ... and lifts its bow (aim: a drawn bow always has its arms up; here only raised)
      the whole shot   the MOON behind the branches (the one moon of the night allows it: see SKIES)
    NEIGHBOURS: before, md10_creeper; after, md12_middle (the wide side view of the line).
    MEASURED (crammys_set_b11_skeleton_zones.png, 40 mm f/2.8 from (2.5, 41.8, 0.35) looking east): the skeleton at
      x 26 %, y 53 % against the trunk, the moon half behind the canopy's south edge (74, 26). The skeleton is 22 %
      of the frame high: keeping the moon at the canopy's edge needs that width.
    FALLBACK (story): "One moon for the whole night module": not needed (the moon is behind the branches); if the
      moon must go, the skeleton against the dark trunk under plain stars.
    """
    f0, f1 = s.frame_start, s.frame_end
    sk = C.actor("skeleton", "md")
    C.put(sk, f0, "skeleton_oak")
    cam = _cam(s, "b11")
    sk.look_at(f0, C.to_lens(sk, f0, C.P("middle"), cam["pos"], degrees=30.0), ease=0)
    sk.look_at(C.at(s, "found") + 2, cam["pos"], ease=8)
    sk.aim(C.at(s, "skeleton") + 2)
    st.use(s, sk)
    st.hero(s, "skeleton", sk)
    C.cam(s, "set:b11", focus=sk.head, pos1=tuple(p + d for p, d in zip(cam["pos"], (0.0, -0.15, 0.03))))
    C.lights(s, "night")


def md12_middle(st, s, C, nar):
    """BEAT 12  "I stood in the middle."   frames 797-843 (47 f, 1.96 s), sky night.
    Words: I 799, stood 803, in 813, the 816, middle 818. The voice ends on 827; the shot runs on 16 frames after it
    (0.67 s).

    STORY (beat 12): Low wide side view on the flat meadow, clean horizon, perfectly symmetrical: creeper on the left,
    skeleton on the right with its bow drawn, both against the sky. Steve walks in from the bottom of the frame, back to
    us, stops on the exact centre of the line, looks left, looks right. The creeper starts toward him.
    Cast: Steve, creeper, skeleton. Effects: drawn bow, symmetrical three-figure line against the sky, two head turns.

    MUST BE SEEN, ON WHICH WORD
      frame 1          the low wide side view: creeper on the left, skeleton on the right WITH ITS BOW DRAWN, both
                       against the sky; Steve already walking in from the bottom of the frame, his back to us
      "stood"          he stops on the exact centre of the line
      "middle"         he looks left (the creeper), then right (the skeleton)
      the last second  the creeper starts toward him
    NEIGHBOURS: before, md11_skeleton; after, md13_shot (medium on Steve from the skeleton's side).
    MEASURED (crammys_set_b12_middle_zones.png, 24 mm f/5.6 from (5.0, 27.0, 0.45)): creeper 21 %, Steve 50 % (his
      back), skeleton 79 % with its bow drawn, all against the sky above a clean horizon (two village oaks taken out
      for it). A wide: the figures are 12 % of the frame high.
    NOTE: the creeper's fuse starts within 3 blocks (FUSE_RANGE): it starts toward him here but must not swell
      before md15 (the story: it swells in beat 15).
    """
    f0, f1 = s.frame_start, s.frame_end
    cr = C.actor("creeper", "md")
    sk = C.actor("skeleton", "md")
    steve = C.actor("steve", "md")
    C.put(cr, f0, "creeper_line")
    C.put(sk, f0, "skeleton_line")
    # Steve: ALREADY WALKING on frame 1 (the game's walk, 4.32 blocks/s, at speed: ramp in off) on the line from
    # steve_enter to the middle, placed so that he stops ON "middle" (C.walk_lead: the players walk's own arithmetic;
    # the first stub walked 5 blocks at 2.2 b/s, 55 frames in a 47-frame shot: he never reached the middle)
    mid, ent = C.P("middle"), C.P("steve_enter")
    arrive = C.at(s, "middle")
    lead = C.walk_lead(f0, arrive)
    u = [(m - e_) for m, e_ in zip(mid, ent)]
    n = math.hypot(u[0], u[1])
    start = C.stand((mid[0] - u[0] / n * lead, mid[1] - u[1] / n * lead))
    steve.place(f0, start, CC.yaw_to(start, mid))
    sk.aim(f0, steve, ease=0)
    sk.draw(f0, release=f1 + 1, target=steve)                  # the bow drawn through the shot (loosed in md13)
    cr.look_at(f0, steve, ease=0)
    steve.look_at(f0, (mid[0], mid[1] + 6.0, 1.5), ease=0)    # straight ahead, up the line
    e = steve.walk(f0, [start, mid], ramp=(False, True))
    left = steve.look_at(e + MD12_LOOK[0], C.eyes("creeper_line", 1.3), ease=7)     # left: the creeper ...
    steve.look_at(left + MD12_LOOK[1], C.eyes("skeleton_line", 1.7), ease=7)       # ... right: the skeleton
    a_ = C.P("creeper_line")
    cr.walk(max(e + MD12_CREEPER, f0 + 1), [a_, (a_[0] + 0.6, a_[1], a_[2])], speed=CC.hostiles.CREEPER_STROLL)
    C.memo["md12_stop"] = e
    st.use(s, cr, sk, steve)
    st.hero(s, "steve", steve)
    C.cam(s, "set:b12", focus=steve.head, pos1=tuple(p + d for p, d in zip(_cam(s, "b12")["pos"], (0.0, 0.35, 0.0))))
    C.lights(s, "night")


def md13_shot(st, s, C, nar):
    """BEATS 13+14  "The skeleton shot me." / "Then it shot me again."   frames 844-930 (87 f, 3.62 s), sky night.
    Words: The 846, skeleton 849, shot 861, me 870, Then 888, it 892, shot 896, me 904, again 907. The voice ends on
    918; the shot runs on 12 frames after it (0.50 s).

    STORY (beat 13): Medium on Steve, three-quarter front from the skeleton's side, the creeper soft behind him. An
    arrow flicks in from beside the lens and sticks in his chest. Red hurt flash, he rocks back half a step. He does not
    move away.
    Cast: Steve, creeper. Effects: arrow in flight, arrow stuck in the player's chest, red hurt flash, knock-back half
    step.

    STORY (beat 14): The same shot, held without a cut. A second jolt and flash, a second arrow in his shoulder. Steve
    looks down at the two arrows, then up. The creeper is now right behind his shoulder.
    Cast: Steve, creeper. Effects: second arrow stuck in the shoulder, red hurt flash, creeper closing in, one
    continuous render with the previous beat.

    ONE TAKE FOR BEATS 13 AND 14 ("The same shot, held without a cut"; the story's timing fallback says so too).
    MUST BE SEEN, ON WHICH WORD
      frame 1          medium on Steve, three-quarter front from the skeleton's side, the creeper soft behind him;
                       something already moving (the skeleton's draw is off-screen beside the lens: the camera)
      "shot" (b13)     the first arrow flicks in from beside the lens and sticks in his CHEST (C.shoot_steve(sk,
                       steve, f, 0): ARROW_HITS[0], aligned with its flight), red hurt flash, he rocks back half a step
                       (knockback 0.1); he does not move away
      "again" (b14)    a second jolt and flash, the second arrow in his RIGHT SHOULDER (C.shoot_steve(..., 1):
                       ARROW_HITS[1], aligned too)
      after "again"    he looks down at the two arrows, then up; the creeper now right behind his shoulder
    SHARED: THE ARROWS (C.shoot_steve: ARROW_HITS, ARROW_SCALE; keep skeleton_line / steve_shot / yaw 135 when they land:
      the later twins' arrows are computed from that staging). Places: steve_shot, skeleton_line,
      creeper_behind_from -> creeper_behind_to.
    NEIGHBOURS: before, md12_middle (the wide); after, md15_kill (the side view tighter: Steve on his last step round
      the creeper: a cut on action).
    MEASURED (crammys_set_b13_shot.png / b14_again, 45 mm f/2.8 from (8.19, 41.16, 1.05), 1.2 blocks north of the
      skeleton): Steve's face three-quarter at x 56 %, y 42 %, the chest arrow's fletching on his upper chest (aligned:
      unaligned it sat over his mouth), the creeper soft at the right edge. In b14 the UNALIGNED shoulder arrow's shaft
      crossed his right eye from this lens; the lead's scout of this stub confirmed it (out/test/crammys_scout_md13_
      shot_915_zones.png: shaft and fletching across his face) and made ARROW_HITS[1] aligned too: on 921 both
      fletchings are clear crosses on his chest and shoulder and his face is free (crammys_scout_aligned_md13_shot_921
      _zones.png: face x 40-75 %, y 33-52 %; the creeper's head at the right edge, x 86 %: outside the safe area, soft
      background). 915 is still inside the second red flash (12 frames).
      The set builder measured Steve's trousers at min channel 14 here (palette limit 12): a cool moon fill
      (C.fill("md_moon", ..., color=CS.MOON_KEY_COLOR)) if they go under, never a brighter lamp.
    TIMING (hostiles): sk.shoot(f, ...) draws from f and looses on `release` (default f + 24); the arrow sticks 2-3
      frames later; the second draw may start one frame after the first release (16 frames is the shortest draw
      that reaches pulling_1). The stub: the first lands on "shot", the second on "again".
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "md")
    cr = C.actor("creeper", "md")
    sk = C.actor("skeleton", "md")
    C.put(steve, f0, "steve_shot")
    a, b = C.P("creeper_behind_from"), C.P("creeper_behind_to")
    C.put(cr, f0, "creeper_behind_from")
    C.put(sk, f0, "skeleton_line")
    sk.aim(f0, steve, ease=0)
    steve.look_at(f0, sk, ease=0)
    # the first arrow lands on "shot" (b13), the second on the SECOND "shot" (b14: "Then it shot me again."), so the
    # reaction fits before the cut: the red flash (12 frames), the look down at the two arrows, the look up
    hit1, hit2 = C.at(s, "shot", 0), C.at(s, "shot", 1)
    fl1 = C.shoot_steve(sk, steve, f0, 0, release=hit1 - 1)            # a 16-frame draw (bow at pulling_1)
    fl2 = C.shoot_steve(sk, steve, int(hit1), 1, release=hit2 - 3)
    flash_end = int(fl2) + 12
    down = steve.look_at(flash_end + 1, (steve.pos_at(flash_end)[0], steve.pos_at(flash_end)[1], 0.9), ease=8)
    up = steve.look_at(down + 2, sk, ease=8)
    C.memo["md13_frames"] = dict(hit1=int(fl1), hit2=int(fl2), down=down, up=up)
    cr.look_at(f0, steve, ease=0)
    cr.walk(f0 + 24, [a, b], speed=0.8)                         # behind his shoulder by about 907
    st.use(s, steve, cr, sk)
    st.hero(s, "steve", steve)
    C.cam(s, "set:b13", focus=steve.head, pos1=tuple(p + d for p, d in zip(_cam(s, "b13")["pos"], (-0.12, 0.05, 0.0))))
    C.lights(s, "night")


def md15_kill(st, s, C, nar):
    """BEAT 15  "Then it shot the creeper."   frames 931-995 (65 f, 2.71 s), sky night.
    Words: Then 933, it 938, shot 941, the 950, creeper 952. The voice ends on 964; the shot runs on 31 frames after it
    (1.29 s).

    STORY (beat 15): The side view from before, tighter, cut on action: Steve is on his last step round the creeper, so
    the line is now Steve, creeper, skeleton. The creeper turns after him and starts to swell and flash white. An arrow
    hits it in the back, red flash. A second arrow, red flash, it tips over and is gone in a puff of smoke. Far right,
    the skeleton lowers its bow. About three and a half seconds; the line is spoken as the first arrow lands.
    Cast: Steve, creeper, skeleton. Effects: creeper fuse swell with white flash, two arrow hits about twenty frames
    apart, each with a red flash, creeper tips over, smoke puff, no arrows left sticking in the creeper, skeleton lowers
    bow.

    MUST BE SEEN, ON WHICH WORD
      frame 1          the side view from md12, tighter, CUT ON ACTION: Steve on his last step round the creeper (the
                       line is now Steve, creeper, skeleton); the creeper turns after him and starts to swell
      "Then" .. "shot" the first arrow hits it in the back: red flash (the line is spoken as the first arrow lands)
      about 20 frames later   the second arrow, red flash, it tips over (still swollen) and is gone in a puff of
                       smoke; NO arrows left sticking in the creeper (only players show stuck arrows)
      after "creeper"  far right, the skeleton lowers its bow; THE DISC drops at the creeper's feet on the killing
                       blow (C.disc_drop: one item for md15 and md16)
    SHARED: THE ARROWS in Steve (steve_md carries them since md13; a new twin needs C.arrows); THE DISC (C.disc_drop ONCE,
      here; C.memo["md_disc"] for md16). Places: creeper_turn, crammys_round path, skeleton_close.
    NEIGHBOURS: before, md13_shot; after, md16_disc (ground level: the smoke thins, the disc turns).
    MEASURED (crammys_set_b15_creeper_shot.png, 24 mm f/4 from (4.75, 31.0, 0.45)): Steve 30 %, the creeper swelling
      42 %, the skeleton drawing 78 % (it stands at skeleton_close, 1.3 blocks nearer than in md12: the three fit a
      24 mm frame). A wide: figures small. Steve ends 1.8 blocks from the creeper; two arrows at knockback 0.1 push it
      about 0.6 toward him (hostiles' numbers, not measured on this staging).
    RISKS (story): "the switch from Steve in the middle to the creeper in the middle must read": keep md12 and md15 on
      one side-on axis (both cameras look north from the south). "two hits may look cheap": the fallbacks are a third
      arrow, or the creeper already flashing red from a hit on the first frame. The fuse is 35 frames: the kill must
      land before it ends (hostiles: shoot(f0 - 24, ...) is loosed ON f0, the second release= 20 frames later).
    """
    f0, f1 = s.frame_start, s.frame_end
    cr = C.actor("creeper", "md")
    steve = C.actor("steve", "md")
    # the skeleton is a TWIN here: its draw starts before the cut (pre-roll), and skeleton_md is in md13, the shot
    # before (its keys there would be overwritten: the technical review measured a third draw in md13)
    sk = C.actor("skeleton", "md2")
    pts = C.v.paths["crammys_round"]
    C.put(cr, f0, "creeper_turn")
    steve.place(f0, pts[0], CC.yaw_to(pts[0], pts[1]))
    C.arrows(steve, s)                                  # (steve_md has them since md13: this does nothing for him)
    first, kill = C.at(s, "shot"), C.at(s, "shot") + MD15_KILL_AFTER
    C.put(sk, first - MD15_DRAW, "skeleton_close")
    sk.aim(first - MD15_DRAW, cr, ease=0)
    steve.walk(f0, pts, ramp=(False, True))             # his last step round it: at speed on frame 1 (cut on action)
    cr.face(f0 + 1, steve, ease=6)                      # it turns after him ...
    cr.look_at(f0 + 1, steve, ease=4)
    cr.fuse(f0 + MD15_FUSE)                             # ... and swells (it would explode 35 frames later)
    a = sk.shoot(first - MD15_DRAW, cr, release=first - 3, knockback=0.1)
    k = sk.shoot(int(first) - 2, cr, release=kill - 3, kill=True, knockback=0.1, camera=s)
    sk.lower(int(k) + 12)
    steve.look_at(f0 + 2, cr, ease=6)
    lens16 = _cam(s, "b16")["pos"]
    feet = cr.pos_at(int(k))
    d = C.disc_drop(feet, int(k), until=C.T["md16_disc"].frame_end + 1, face=lens16)
    C.memo["md_disc"] = d
    C.memo["md_kill"] = int(k)
    C.memo["md15_frames"] = dict(hit1=int(a), kill=int(k), fuse=f0 + MD15_FUSE)
    st.use(s, cr, sk, steve, d)
    st.hero(s, "creeper", cr)
    C.cam(s, "set:b15", focus=cr.head, pos1=tuple(p + d_ for p, d_ in zip(_cam(s, "b15")["pos"], (0.0, 0.3, 0.0))))
    C.lights(s, "night")


def md16_disc(st, s, C, nar):
    """BEAT 16  "A disc dropped."   frames 996-1036 (41 f, 1.71 s), sky night.
    Words: A 998, disc 1000, dropped 1009. The voice ends on 1022; the shot runs on 14 frames after it (0.58 s).

    STORY (beat 16): Ground level. The smoke thins. A music disc turns and bobs just above the grass, a black shape
    against the moonlit ground, too dark to read. No experience orbs. Steve's feet step into frame and stop in front of
    it.
    Cast: Steve. Effects: music disc as a dropped item in silhouette, thinning smoke, no experience orbs.

    MUST BE SEEN, ON WHICH WORD
      frame 1          ground level; the smoke of the poof thinning (the particles of md15 live on: no time jump)
      "disc"           the music disc turning and bobbing just above the grass, a BLACK SHAPE against the moonlit
                       ground (too dark to read which disc); NO experience orbs
      "dropped" ..     Steve's feet (and his arrows) step into frame and stop in front of it
    SHARED: THE DISC (C.memo["md_disc"], dropped in md15; aim the camera at its rest_pos). THE ARROWS (steve_md).
    NEIGHBOURS: before, md15_kill; after, rd17_run_back (the lane: he runs to the stage with the disc in his hand).
    MEASURED (crammys_set_b16_disc.png, 40 mm f/2.8 from (2.39, 38.3, 0.3), 2.6 blocks from the disc): the disc a
      black shape against the haze (50, 42 %); Steve's legs and arrows walk in at the right; the ground camera shows
      more of him than his feet. The set builder's disc landed at disc_rest (3.79, 40.5) from creeper_turn (seed 5):
      if the creeper dies elsewhere, re-aim on the item's rest_pos (the stub does).
    GAME TRUTH: a player collects an item within about one block: steve_disc is 0.95 from disc_rest: the pick-up
      (item.pick_up(f): the disc jumps into him) is the story's own fallback ("let the item jump into Steve as a
      pickup after one turn, before its face catches the light"); either pick it up on camera or stop him farther.
    """
    f0, f1 = s.frame_start, s.frame_end
    d = C.memo.get("md_disc")
    rest = tuple(d.rest_pos) if d is not None and d.rest_pos is not None else C.P("disc_rest")
    steve = C.actor("steve", "md")
    C.put(steve, f0, "steve_disc_from")
    C.arrows(steve, s)
    e = steve.walk(f0 + 6, [C.P("steve_disc_from"), C.P("steve_disc")], speed=2.0)
    steve.face(e, rest, ease=4)
    st.use(s, steve, *([d] if d is not None else []))
    st.hero(s, "disc", d.sprite if d is not None else steve)
    cam = _cam(s, "b16")
    C.cam(s, None, focus=d.sprite if d is not None else rest, pos=cam["pos"], target=(rest[0], rest[1], rest[2] + 0.15),
          pos1=tuple(p + q for p, q in zip(cam["pos"], (0.1, 0.12, 0.0))), lens=cam["lens"], fstop=cam["fstop"],
          handheld=0.004)
    C.lights(s, "night")
