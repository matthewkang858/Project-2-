"""The Hello, sequence SQUARE: the village square with the well and the bell, golden hour. Beats 1, 9, 10, 11
(shots sq01_guard, sq09_watches, sq10_grownups, sq11_stare), sky "gold". One function per shot; the contract is in
films/hello_common.py (read it first: tags "sq...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE: the well at (-0.5, -0.5), the bell at (-1.5, -2.5, 1.6) with its two player-built lamps at (-3.5, -3.5)
  and (0.5, -3.5); square_center (0.5, -6.0); the south street runs south from (0.4, -9); the exit road (the
  "path" of the story) runs north from (0.5, 6) to the gate at (0.5, 24.5). C.A has every village anchor.
THE SKY: "gold" = a golden sun at azimuth 215 (west-south-west, 35 degrees south of west), elevation 24. Stage each
  camera so the sun is 60-120 degrees off its axis (CONTRACT.md): cameras looking north-west to north are right.
THE WATCHER (beats 9, 10, 11): C.actor("watcher", "sq") is Steve's plain skin, no armor, empty hands, dead still.
  His face must never be readable here: far and out of focus with the face under about ten pixels at 540x960
  (an 85 mm lens at 19 blocks still gives a 58-pixel face: blur it hard or take him further up the road), or seen
  from behind / cropped at the hip (beat 11). If his eye whites read as dots, take him further away.
  AS SHOT: he stands at SQ_WATCH = PLACES["watch_square"] (1.5, 14.0) in all three shots, facing south (this
  file's own spot first; the lead made it the shared place, the stub's (0.5, 9.6) is gone: the comment at
  SQ_WATCH). The cameras are this file's own constants (C.cam(s, None, **SQxx_CAM): the stub CAMS "guard",
  "grownups" and "hip" are gone; CAMS "square_long" is sq09's start, the square's stand-in). Beat 9: face
  25 px, beat 10: 33 px, each under a blur 0.7-0.8 as wide as the face (focus never on him, f/0.95-1.2); beat
  11: from behind, his head above the frame. Rule of thumb used: blur / face width = lens * (D - focus) /
  (140 * fstop * focus) for Shot.lens's f-stop (DOF_FSTOP_SCALE 0.28), D = his distance; keep it near 1 (at
  0.36 two white eye patches showed; 0.63-0.8 rendered a skin blob with no eyes in 3x crops).
THE FARMER (beats 9, 10): one instance, twin "sq9" (_wheat_farmer), wheat on his crossed arms in both shots.
  NOTE for the reviewers' cut check: render.py's preview stamps live in one meta.json per directory; two render.py
  processes writing the same preview directory at once lose each other's stamps (frames re-render, no harm).
LIGHT: C.lights(s, "gold", near=<place>, radius=16) (daylight: the torches at their own level; far ones off);
  beat 11 adds the film-local fill "sq_stare" (palette-checked).
MOTION CHECK: tools/hello_square_motion.py (mp4 of the square's preview frames, contact strips of frames).
"""
from engine import characters as CH
from films import hello_common as HC

# ---- beat 1 (sq01): Steve on guard south of the bell, the child BEHIND his left leg looking up at him; a low
# long lens from the south-south-east, looking north-north-west (azimuth 115: the sun at 215 is 100 degrees off
# the axis and keys both faces from frame left). The child stands a block further from the lens than he does, so
# its look up at him comes back toward the lens (its face, not the back of its head). The bell lamp post west of
# the bell is at the left edge (at azimuth 135 its lantern sat on his hair; at 145-150 its post stood behind the
# child's head).
SQ01_STEVE = (-1.2, -6.3)                   # = PLACES["guard"]
# his body turned toward the lens (only his head looks down the street): the sword points forward out of his
# right hand, and with the body 37 degrees to frame left (yaw to (-2.4, -12.0), the first version) more than half
# of the blade was outside the frame's left edge (x -17..20 %); now it is at x 7-22 %, pointing up-left
SQ01_STEVE_YAW = HC.yaw_to((-1.2, -6.3), (0.5, -13.0))
SQ01_CHILD = (-0.9, -5.06)                  # 1.0 block behind him (from the lens), 0.8 to his left
SQ01_STREET = (-1.2, -12.3, 1.35)           # where he looks: down the street, 25 degrees off the lens
SQ01_SCAN = (0.05, -12.17, 1.4)             # ... and a little further round toward the lens (15 degrees off it)
SQ01_CAM = dict(pos=(2.18, -13.55, 0.8), target=(-1.07, -5.58, 0.6), lens=60.0, fstop=1.6,
                pos1=(1.93, -13.01, 0.8), target1=(-1.07, -5.58, 0.6))


# ---- the watcher in beats 9, 10, 11: one spot for all three shots, on the exit road between the first two houses
# (house_e west, house_f east), 2.5 blocks out from house_f's front. PLACES["watch_square"] (0.5, 9.6) put him in
# front of the gate's west lamp post in beat 9 (its lantern on his head) and 22 blocks from that lens, where a
# rendered face of 27 px with the focus on a villager 11 blocks out still showed two white eye patches. Here he is
# 26.6 blocks from the beat 9 lens with the gate's two lanterns either side of him (x 33 / 74 %).
SQ_WATCH = HC.PLACES["watch_square"]        # (1.5, 14.0): the shared place since the lead's pass (it was this
#                                           file's own spot, PLACES held the stub's (0.5, 9.6))

# ---- beat 9 (sq09): long lens from the south-east corner of the square, past the well's east side, up the road.
# The aim is 0.4 block east of him (he stands at x 42-51 % of the frame), and the farmer walks a lane 1.7 blocks
# further back than the first version's, so a gap of 4.6-6.4 % of the frame stays between them for the whole shot
# (the first farmer grew into him: his shoulder over his arm on "watches", half of him hidden at the cut).
# The focus is a FIXED point at the end of the farmer's walk, 8.0 blocks out (on the farmer himself it went out to
# 10 blocks with this lane, and the watcher's face sharpened into two lighter eye patches): blur / face width =
# lens * (D - focus) / (140 * fstop * focus) with D = 26.6 gives 0.69, as in the passed first version (0.63-0.74).
SQ09_CAM = dict(pos=(5.5, -12.3, 1.3), target=(1.9, 14.0, 1.2), lens=50.0, fstop=1.2,
                pos1=(5.36, -12.25, 1.3), target1=(1.9, 14.0, 1.2))
SQ09_LIBRARIAN = ((6.6, -6.75), (2.4, -7.5))   # crosses the foreground right to left, 5.5 blocks from the lens
SQ09_FARMER = ((4.82, 0.3), (4.97, -4.0))      # carries the wheat down past the well's east side, toward us
SQ09_FOCUS = (4.95, -4.3, 1.5)                 # where the farmer's walk ends (8.0 blocks from the lens)
SQ09_KID_A = ((8.0, -4.85), (-4.0, -4.85))     # the two children run right to left in front of the well, 7.8
SQ09_KID_B = ((8.0, -4.2), (-4.0, -4.2))       # blocks out (their heads below his feet in the frame), 0.65 apart
SQ09_KID_LEADS = (22, 14)                      # pre-roll frames: kid B has passed under him before "stands" (558)
SQ09_KID_LOOK = (-6.0, -12.0, 0.7)             # where the running children glance: toward the lens's side
# the farmer walks straight at the lens: with his head along the walk both green eyes were on the lens from 571 to
# the cut, the sharpest face in the frame right over "watches us", so he read as the "he" who watches (review of the
# whole-film preview). His head is turned to frame left, toward the well and the children running past it, cheated
# to SQ09_FARMER_OFF degrees from the lens and a little down: brow, one eye and the nose in profile for the whole
# walk; the watcher is the only figure that faces the camera
SQ09_FARMER_OFF = 65.0                         # degrees from the lens toward frame RIGHT (negative: frame left)
SQ09_FARMER_DOWN = -8.0                        # degrees above level (negative: down, at the well's rim)


# ---- beat 10 (sq10): low (0.72, the child's eyes) from just north-east of the well, on the line from him through
# the middle of the two adults; 35 mm, f/0.95, focus on the child 3.8 blocks out (his face 14 blocks out: blur
# about 0.8 of its width; at f/1.1 a faint pair of lighter eye patches was left in the blur). The gate's two
# lanterns stand behind the adults' heads (a lantern beside his head is a halo).
# A constant-speed push (0.0053 block a frame to the last frame: the first version's ease_out slowed to 0.0008, a
# freeze-frame under "sometimes"); the aim and the child 0.2 block further to frame left, so the child's head
# keeps clear of him (it covered his left arm and shoulder, then touched him).
SQ10_CAM = dict(pos=(5.0, 0.4, 0.72), target=(2.04, 10.06, 0.32), lens=35.0, fstop=0.95,
                pos1=(4.91, 0.748, 0.72), target1=(2.04, 10.06, 0.32), ease="linear")
SQ10_FARMER, SQ10_TOOLSMITH = (3.0, 5.57), (4.26, 5.89)     # 5.5 blocks out, 0.65 either side of the line to him
SQ10_CHILD = (3.45, 3.99)                                   # 3.8 blocks out, 0.6 left of the line


# ---- beat 11 (sq11): behind him and just east of his LEFT hip, 66 mm, looking south down the road at the child
# 1.41 blocks in front of him (close enough for its head to tip all the way back, 35 degrees, to his eyes). His hip
# and hanging hand are at the right edge, soft; his head is far above the frame. The camera is on the same side of
# the child-to-him line as beat 10's (east of it), so the child looks screen-right at him in both shots (from the
# west side, the first version, it looked right in beat 10 and left in beat 11: a crossed line on the cut).
SQ11_CHILD = (2.15, 12.75)                  # at the east edge of the road (the road is x -1..2 here)
SQ11_CAM = dict(pos=(3.2, 18.0, 0.95), target=(2.15, 12.75, 0.5), lens=66.0, fstop=2.0,
                pos1=(3.12, 17.62, 0.95), target1=(2.15, 12.75, 0.52))
SQ11_FILL = dict(pos=(2.9, 13.4, 1.5), watts=120.0, color=(1.0, 0.93, 0.82))
# ONE child runs past behind it: up the road's east side, then off east toward house_f, out of the frame's left
# edge by frame 697, so the stare holds alone on "back" (691) and in the pause. (Two runners, the first version,
# ran straight at the lens: one stuck out from behind the child's head, the other ended half out of the frame.)
SQ11_KID_A = ((2.0, 5.0), (2.6, 8.6), (5.2, 10.6))
SQ11_KID_LEAD = 32                          # pre-roll frames: at the turn on the cut (21: ran at the lens 673-687)
SQ11_KID_LOOK = (9.0, 5.0, 0.7)             # its head turned away east-south-east: a profile, never a 2nd stare


def _wheat_farmer(C):
    """The farmer of beats 9 and 10 (one instance, twin "sq9"), with wheat on his crossed arms: the game draws a
    villager's held item there (C.held_item: Character.hold of props.make_item; C.item makes a dropped item on the
    ground, not a held one). st.use shows and hides the wheat with him (541-672)."""
    return C.held_item(C.actor("farmer", "sq9"), "wheat")


def _look_dir(c, frame, cam_pos, right, up, dist=3.0):
    """A look point for villager `c` that turns its head `right` degrees from the lens toward FRAME RIGHT (negative:
    frame left) and `up` degrees above level. The adults of beat 10 and the watcher stand behind the child, and a
    true eyeline would show the lens the back of its head; a cheated one is a head turn that reads, with its face
    (or, at 60 degrees, its nose in profile) toward the side of the frame the one it looks at stands on."""
    import math
    eye = c.eye_point(frame)
    a = math.atan2(cam_pos[1] - eye.y, cam_pos[0] - eye.x) + math.radians(right)
    return (eye.x + dist * math.cos(a), eye.y + dist * math.sin(a), eye.z + dist * math.tan(math.radians(up)))


def _aside(c, f0, f1, cam_pos, right, up, step=3):
    """Keep c's head turned `right` degrees from the lens toward frame right (negative: frame left) and `up` above
    level from f0 to f1 while it walks (_look_dir re-aimed every `step` frames, smooth; already turned on f0)."""
    yk, pk = [], []
    f = int(f0)
    while True:
        yaw, pitch = c._aim(_look_dir(c, f, cam_pos, right, up), f)
        yk.append((f, yaw))
        pk.append((f, -pitch))
        if f >= f1:
            break
        f = min(int(f1), f + step)
    CH._segment(c.head, "rotation_euler", 2, yk, "BEZIER")
    CH._segment(c.head, "rotation_euler", 0, pk, "BEZIER")
    return f1


def sq01_guard(st, s, C, nar):
    """BEAT 1  "In this town, the player used to protect us."   frames 1-71 (71 f, 2.96 s), sky gold.
    Words: In 8, this 10, town 16, the 30, player 32, used 42, to 48, protect 49, us 60.

    STORY: Golden hour. Steve in iron chestplate, leggings and boots, no helmet, iron sword in hand, stands guard by
    the well looking out along the path. The baby villager stands at his leg, about half his height, big head
    tipped back to look up at him. Low camera at child height from the front three-quarter, long lens, both faces
    in the upper half of the frame, two adult villagers soft in the background. Slow push in. About 3 seconds.
    Cast: baby villager (narrator), Steve, farmer (background), librarian (background). Effects: iron chestplate,
    leggings and boots on Steve, iron sword held, shallow depth of field, slow push in.

    MUST BE SEEN, ON WHICH WORD
      frame 1         already moving: the push in has begun, Steve's idle and the adults' idle are running
      "player" 32     Steve's face clearly readable (it is the hook: the player, the protector), the sword in hand
      "protect" 49    the child looking up at him (head tipped back, cheated toward the lens: C.to_lens)
      the whole shot  both faces in the upper half of the frame (y 14-60 %), the adults soft behind them
    SHARED: none with other sequences. PLACES "guard" (the torches' near point); the camera is SQ01_CAM.
      Cast: C.actor("steve_iron", "sq"), C.actor("child", "sq"), C.actor("farmer", "sq"), C.actor("librarian", "sq").
    NEIGHBOURS: the film's first shot; after it dn02_fight (night, the zombie at the child's door). Hard cut.
    NOTES: a villager's head turned more than about 26 degrees from the lens is a blank box; the child is half his
      height, so a camera at child height looks up at Steve: keep his face out of the top 14 %.
    NOW: SQ01_CAM, 60 mm f/1.6 from 8 blocks, 0.8 above the ground (the child's eye height), looking north-north-
      west: Steve in iron with the sword, full length, the bell glowing on the well behind him, the child BEHIND
      his left leg (a block further from the lens, so that its look up at him comes back toward the lens). His body
      faces the lens's side (SQ01_STEVE_YAW; only his head looks down the street), so the sword, pointing forward
      out of his right hand, is in the frame, pointing up-left against the lamp post (with the body turned 37
      degrees to frame left and a 70 mm lens, the first version, more than half the blade was off the left edge).
      A 0.6-block ease_out push, at speed on frame 1. Both head turns started before the film (keys from frame
      -11): on frame 1 the child's head is already tipping back from the street to him (pitch 12 -> 35 degrees by
      frame 14, held), and Steve is scanning down the street, his face coming round to 13 degrees off the lens by
      "player" (32) and held. Focus on Steve, pulled to the child from frame 44 for "protect" (49). Idles on both
      (Steve's arm bob, the child's breathing; their heads are keyed over them).
      THE ADULTS ARE NOT IN THE FRAME (accepted omission): from a lens 0.8 above the ground, a standing adult's head
      15-30 blocks away lands at y 33-41 % of the frame (projected), i.e. behind his chest and arms (x 8-57 %), the
      child (x 51-77 %), the lamp post (x 0-12 %) or the well (x 77-100 %); the open house front left of his head
      (y 12-30 %) would need a head 3 blocks above the ground. Nearer, an adult's head sits at his shoulder line
      (tried: renders out/test/sqB/sqC/sqD_sq01_guard_49.png); an eye-level camera (1.55) showed them, but as two
      heads tucked beside his and lost the low, heroic angle. The village is in the shot as the well, the bell,
      the lamp and the houses, soft; the adults are seen in beats 9 and 10.
    MEASURED (tools.hello_geo, frames 1 / 32 / 49; renders out/test/sqfinal_sq01_guard_32_zones.png and
      sqfinal_sq01_guard_49_zones.png at 540x960/16): Steve's eyes x 34.6-35.4 %, y 29-30.5 %, head x 22.6-46.6 %
      y 22.2-35.1 %, face 101 -> 108 px, 23 -> 13 degrees off the lens; the sword x 7.2-23.1 % y 32-59 % (it was
      x -17..22 %); the child's eyes x 61.6-62.4 %, y 50 %, head x 50.3-76.6 % y 41.8-55.5 %, face 89-94 px, 23
      degrees off the lens, head pitch 35 degrees from frame 14; nothing between the lens and either face.
      hello_palette sq01@40: every check passes (stone G/R 0.94, planks s 0.51, robe hue 15, villager skin s
      0.44; Steve x 23-45 %, child x 53-76 %: both 100 % inside the safe area).
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_iron", "sq")
    kid = C.actor("child", "sq")
    cam = SQ01_CAM
    C.put(steve, f0, SQ01_STEVE, yaw=SQ01_STEVE_YAW)
    C.put(kid, f0, SQ01_CHILD, toward=SQ01_STEVE)
    steve.idle(f0, f1 + 1, seed=11)
    kid.idle(f0, f1 + 1, seed=4)
    # the heads are keyed over the idles (a look_at segment drops the idle's head keys it covers), and both turns
    # began before the film did, so they are at speed on frame 1:
    # the child looked where he looks (down the street), and is tipping its head right back to him (frames -5..14)
    up = C.to_lens(kid, f0 + 14, tuple(steve.eye_point(f0 + 14)), cam["pos"], degrees=10.0)
    kid.look_at(f0 - 6, SQ01_STREET, ease=0)
    kid.look_at(f0 - 6, up, ease=20)
    kid.look_at(f0 + 14, up, ease=f1 + 1 - (f0 + 14))
    # Steve scans the street, slowly, his face coming round toward the lens while the narrator names him
    # ("player" 32: 15 degrees off the lens), and holds
    steve.look_at(f0 - 12, SQ01_STREET, ease=0)
    steve.look_at(f0 - 12, SQ01_SCAN, ease=44)
    steve.look_at(f0 + 32, SQ01_SCAN, ease=f1 + 1 - (f0 + 32))
    st.use(s, steve, kid)
    C.cam(s, None, focus=steve.head, handheld=0.006, **cam)
    # "protect" (49): the focus pulls from his face to the child looking up at him
    s.focus(kid.head, at_s=s.film.seconds(C.at(s, "protect") - 5), rack_s=0.4)
    st.hero(s, "steve", steve)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="guard", radius=16.0)


def sq09_watches(st, s, C, nar):
    """BEAT 9  "Now he just stands around and watches us."   frames 541-604 (64 f, 2.67 s), sky gold.
    Words: Now 543, he 550, just 553, stands 558, around 567, and 577, watches 579, us 591.

    STORY: Village square, long lens, locked off. A farmer carries wheat past the well and a librarian crosses in
    the foreground, both sharp, and two baby villagers run past playing, staggered so they do not merge. Far
    behind them at the mouth of the path he stands facing this way, small and soft, the only thing in the picture
    that does not move. Nobody looks at him. About 3 seconds.
    Cast: the watcher (far background, face unreadable), farmer, librarian, two baby villagers. Effects: wheat
    held by the farmer, focus held on the villagers, never on him.

    MUST BE SEEN, ON WHICH WORD
      frame 541       the village already busy (everybody walking or running on the first frame: pre-roll them,
                      none of them is in the shot before)
      "stands" 558    him, small and still at the mouth of the road, in a gap between the moving villagers
      "watches" 579   still there, nobody looking at him
    SHARED: PLACES "watch_square" (also beats 10 and 11: the same spot all three shots). The camera is SQ09_CAM
      (CAMS "square_long" = its start, the stand-in). Cast: C.actor("watcher", "sq"), C.actor("farmer", "sq9"),
      C.actor("librarian", "sq"), C.actor("kid", "sq_a"), C.actor("kid", "sq_b"). Wheat: C.held_item(farmer,
      "wheat") (Character.hold of props.make_item); a held flat item lies along the hand (edge-on from the side).
    NEIGHBOURS: before, me08_nohello (the meadow: the child's hello unanswered); after, sq10_grownups (the same
      square, the same watcher, from the well). Hard cuts.
    RISKS (story): "His face before the reveal": two white eye pixels can show as bright dots even at distance and
      spoil the ending: beyond focus with a face under about ten pixels, else use him further away. Two children
      0.2 block apart are one two-headed shape: stagger them by 0.7 block. The well (x -2..1, y -2..1) and the
      bell stand between the south of the square and the road: check the line of sight (CAMS "square_long" looks
      past the well's east side).
    NOW: SQ09_CAM, 50 mm f/1.2 from the square's south-east corner past the well's east side up the road, nearly
      locked (a 0.15-block linear drift and a 0.004 handheld), aimed 0.4 block east of him. He stands at SQ_WATCH
      (1.5, 14.0), facing south, 26.6 blocks out, the gate's two lanterns either side of him. Everybody is
      pre-rolled and moving on 541: the librarian crosses the foreground right to left (5.3 blocks out, sharp) and
      wipes past him by 557; the farmer (twin "sq9", wheat on his crossed arms: _wheat_farmer) walks toward us
      down the well's east side on a lane that keeps a gap of 4.6-6.4 % of the frame between him and the watcher,
      his head turned to frame RIGHT, 65 degrees off the lens and 8 down (SQ09_FARMER_OFF / _DOWN, _aside, keyed
      from his pre-roll to 604: brow, one eye and the nose in profile, looking away from the watcher's side of the
      frame; since the review of the whole-film preview: with his head along the walk both green eyes were on the
      lens from 571, the sharpest face in the frame over "watches us", and he read as the "he" who watches);
      the two children run right to left in front of the well, 7.8 blocks out (their heads below his feet in the
      frame, 0.65 apart, 8 frames apart), early enough (SQ09_KID_LEADS) that kid B has passed under him before
      "stands", glancing toward the lens's side as they run (SQ09_KID_LOOK: their faces in profile). Focus on the
      librarian, racked from 549 to SQ09_FOCUS, a fixed point 8.0 blocks out where the farmer's walk ends (he is
      10.9 -> 8.3 blocks out: soft-sharp, sharp at the end). Nobody looks at him, and he is the only figure facing
      the camera.
      HIS FACE: the first fix (focus on a farmer 11.5 blocks out, f/1.3) still rendered two white eye patches on a
      27 px face (out/test/sqA_sq09_watches_579.png): blur / face width = lens * (D - focus) / (140 * fstop *
      focus) must be near 1, so the focus stays within 8 blocks and he moved 4.4 blocks further up the road.
    MEASURED (tools.hello_geo and projected boxes at 541-604; renders out/test/sqfinal_sq09_watches_558_zones.png
      and sqfinal_sq09_watches_579_zones.png): his eyes x 46 %, y 48 %, body x 41.7-51.0 % y 46.8-56.6 %, face
      25 px, 9 degrees off his nose, blur about 0.69 of the face width: at 3x (and at 8x with the contrast
      stretched) the face is a skin-coloured blob with a darker beard band and no eye patches. The farmer's box
      (hat brim included) x 55.6-58.6 .. 81.1-85.6 %, eyes x 69.6-70.7 %, y 45-46 %. The librarian covers him
      543-556; kid A passes under him 546-548 (behind the librarian), kid B 553-556; from 557 nothing touches his
      box. hello_palette sq09@579: every check passes (stone G/R 0.96, planks s 0.49, robe hue 11, plants 1.37;
      farmer x 58-81 %, watcher x 45-48 %: both 100 % inside the safe area). The children's heads cross y 55-66 %
      (into the caption band: running extras, nothing essential); with the glance kid A is 62-69 and kid B 54-61
      degrees off the lens at 541-553 (brow, eye and nose in profile: out/test/sqfinal_sq09_watches_550.png,
      hello_square_strip_sq09kids.png); looking ahead they were 86-110, two blank pink cubes.
      THE FARMER'S HEAD (review of the whole-film preview; tools.hello_geo 541-604, stills
      out/test/hello_review_fix_sq09_watches_579_zones.png and _600.png at 540x960 / 16): 64-66 degrees off the lens
      for the whole walk (it was 0-10: both eyes on the lens), one eye and the nose toward frame right, the big
      side of his head to us; his box with the hat brim x 51.5-91 % (the brim's corner comes 2.7 % from the
      watcher's head at 604, above it: the brim is at y 37-40 %, the watcher's head at 47-49 %). Turned to frame
      LEFT (the well) his nose pointed across the frame at the watcher, 1.4 % from his head: rejected.
      hello_palette sq09@579 passes every check (stone G/R 0.96, planks s 0.49, robe hue 16, skin s 0.46, plants
      1.37; farmer x 62-81 %, watcher x 45-48 %, both 100 % inside). Preview 541-604 re-rendered.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "sq", place=SQ_WATCH, yaw=0.0)
    ada, bo = _wheat_farmer(C), C.actor("librarian", "sq")
    k1, k2 = C.actor("kid", "sq_a"), C.actor("kid", "sq_b")
    # everybody is pre-rolled (none of them is in the shot before): already walking or running on frame 541. The
    # farmer's walk ends on 604, the shot's last frame (he stands in sq10, put there on its first frame)
    lead_a, lead_b = SQ09_KID_LEADS
    for c, (p0, p1), lead, speed, run in ((bo, SQ09_LIBRARIAN, 31, 1.25, False), (ada, SQ09_FARMER, 40, 1.0, False),
                                          (k1, SQ09_KID_A, lead_a, 3.4, True), (k2, SQ09_KID_B, lead_b, 3.4, True)):
        c.place(f0 - lead, C.stand(p0), HC.yaw_to(p0, p1))
        c.walk(f0 - lead, [C.stand(p0), C.stand(p1)], speed=speed, run=run)
    # the children glance toward the lens's side while they run (54-69 degrees off the lens: brow, eye and nose in
    # profile, never at the camera); looking straight ahead they were 86-110 degrees off it, two blank pink cubes
    for c, lead in ((k1, lead_a), (k2, lead_b)):
        c.track(f0 - lead, f1 + 1, SQ09_KID_LOOK, step=3, ease=1)
    # the farmer's head off the lens to frame left (the well, the running children) for his whole walk: never a
    # stare into the lens on "watches us" (his keys end on 604: sq10 keys him from 605)
    _aside(ada, f0 - 40, f1, SQ09_CAM["pos"], SQ09_FARMER_OFF, SQ09_FARMER_DOWN)
    st.use(s, ada, bo, k1, k2)
    cam = SQ09_CAM
    C.cam(s, None, focus=bo.head, handheld=0.004, ease="linear", **cam)
    # the focus stays on the villagers: the librarian, then (once she has passed) the farmer's lane, on the fixed
    # point where his walk ends (never on him: on the farmer's head it reached 10 blocks, too near the watcher's)
    s.focus(SQ09_FOCUS, at_s=s.film.seconds(f0 + 8), rack_s=0.5)
    st.hero(s, "farmer", ada)
    st.hero(s, "watcher", him)
    C.lights(s, "gold", near=C.A["square_center"], radius=18.0)


def sq10_grownups(st, s, C, nar):
    """BEAT 10  "The grownups say players stand still sometimes."   frames 605-672 (68 f, 2.83 s), sky gold.
    Words: The 607, grownups 608, say 620, players 625, stand 634, still 641, sometimes 649.

    STORY: By the well, camera at child height looking up. A farmer and a toolsmith face each other, heads nodding,
    arms crossed, noses in profile. The baby villager stands between and in front of them, clear of their arms,
    looks from one to the other, then turns its head past them toward the path, where he is a small still shape in
    the gap between the two adults. About 2.5 seconds.
    Cast: farmer, toolsmith, baby villager (narrator), the watcher (small in the background gap). Effects:
    villager head nods, child head turn held to the last frame.

    MUST BE SEEN, ON WHICH WORD
      "grownups" 608  the two adults nodding at each other, noses in profile
      "players" 625 .. "stand" 634    the child looks from one to the other
      "still" 641 .. the end          the child's head turned past them toward the road and HELD to the last frame
                      (cheated about 21 degrees toward the lens: C.to_lens), him small and still in the gap
    SHARED: PLACES "watch_square" (the same spot as beats 9 and 11); the camera (SQ10_CAM), the adults and the
      child are this file's (the stub's PLACES "grownups" / "grownups_child" and CAMS "grownups" are gone): they
      line up on him, from watch_square through the middle of the two adults. Cast: C.actor("farmer", "sq9"),
      C.actor("toolsmith", "sq"), C.actor("child", "sq"), C.actor("watcher", "sq").
    NEIGHBOURS: before, sq09_watches; after, sq11_stare (the child alone on the road, staring at him). Hard cuts.
    RISKS (story): the line is a thought with no action: keep him visible in the gap between the two adults and hold
      the child's head turn toward him to the last frame. The child stands in front of the adults, not tucked
      between them (a face tucked against a neighbour is a third hidden: CONTRACT.md).
    NOW: SQ10_CAM, 35 mm f/0.95, 0.72 above the ground (the child's eye height) just north-east of the well, on the
      line from him (SQ_WATCH) through the middle of the two adults; a 0.36-block push at constant speed (0.0053
      block a frame to the last frame). The farmer (beat 9's, the wheat on his crossed arms: a thin soft stalk in
      profile, as the game draws a held item edge-on) and the toolsmith stand 5.5 blocks out, 0.65 either side of
      that line, facing each other (profiles, noses toward the gap), and nod in turn on 605 (the cut frame) and
      just before "say", "stand", "sometimes"; he stands small in the gap between their noses. The child stands
      3.8 blocks out in front of the farmer, facing the lens, 0.6 left of the line (its head clear of him), and
      its looks are cheated (_look_dir): up and to frame left at the farmer, on "players" (625) across to frame
      right at the toolsmith, from "still" (641) round to frame right past them toward him (62 degrees, nose in
      profile), held to the last frame. Focus on the child; the adults are soft. Idles on all three (heads keyed
      over them).
    MEASURED (tools.hello_geo and projected boxes at 605-672; renders out/test/sqfinal_sq10_grownups_612_zones.png,
      sqfinal_sq10_grownups_650_zones.png): him eyes x 58 %, y 40 %, body x 51.7-64.6 % y 38-51.7 %, face 33-34
      px, 14 degrees off his nose, blur about 0.8 of the face width (f/0.95): at 3x a skin blob, no eyes (at f/1.1
      two faint lighter eye patches remained); the child's head x 15.1-49.9 % (605) -> 8.7-45.8 % (672), y 38-56 %:
      1.8 % clear of him at 605, 6 % from 630; the wheat x 48.7-50.4 %, 1.5 % left of his body; the adults' eyes
      y 30-31 %, farmer x 36-38 % (head 17-53 % with hat brim and nose), toolsmith x 79-80 % (head 63-90 %); the
      child's eyes x 28.5-31 %, y 49-50 %, 35 -> 61 degrees off the lens over the shot; nothing between the lens
      and any face. Frame-to-frame change of the 270x480 previews 661-672: 0.32-0.35 (0.18-0.31 with the eased
      push). hello_palette sq10@650: every check passes (planks s 0.48, robe hue 12, villager skin s 0.43, plants
      0.75; child x 10-42 %, farmer x 20-51 %: both 100 % inside the safe area).
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "sq", place=SQ_WATCH, yaw=0.0)
    # the farmer is beat 9's (same wheat on his arms: an identical farmer without it read as the same man who had
    # dropped it on the cut); his walk there ends on 604, and he is put here on 605, keys in frame order
    ada, tom = _wheat_farmer(C), C.actor("toolsmith", "sq")
    kid = C.actor("child", "sq")
    cam = SQ10_CAM
    C.put(ada, f0, SQ10_FARMER, toward=SQ10_TOOLSMITH)
    C.put(tom, f0, SQ10_TOOLSMITH, toward=SQ10_FARMER)
    C.put(kid, f0, SQ10_CHILD, toward=cam["pos"])
    pos = cam["pos"]
    at_f = _look_dir(kid, f0, pos, -35.0, 28.0)       # up at the farmer (frame left, above it)
    at_t = _look_dir(kid, f0, pos, 40.0, 26.0)        # up at the toolsmith (frame right, above it)
    at_him = _look_dir(kid, f0, pos, 62.0, 10.0)      # round past them to the road: him, right of it, small, far
    # every head is cut to its first look BEFORE the idle (the idle's head glances start from it), then held over
    # the idle by a segment from f0 (which drops the idle's head keys): the adults hold each other's eyes (profiles)
    ada.look_at(f0, tom, ease=0)
    tom.look_at(f0, ada, ease=0)
    kid.look_at(f0, at_f, ease=0)
    for c, seed in ((ada, 3), (tom, 7), (kid, 9)):
        c.idle(f0, f1 + 1, seed=seed)
    ada.look_at(f0, tom, ease=f1 + 1 - f0)
    tom.look_at(f0, ada, ease=f1 + 1 - f0)
    # (the first nod starts on the shot's first frame, 605: something moves on the cut itself)
    nods = (C.at(s, "grownups") - 3, C.at(s, "say") - 2, C.at(s, "stand") - 2, C.at(s, "sometimes") - 2)
    for i, f in enumerate(nods):
        (ada if i % 2 == 0 else tom).nod(f)
    # the child: up at the farmer (frame left), "players" (625) to "stand" (634) across to the toolsmith (frame
    # right), and from "still" (641) round past them toward the road, to him, held to the last frame. The adults are
    # behind it: every look is cheated toward the lens (its face stays 30-45 degrees off the lens: a head turn that
    # reads, never the back of its head)
    kid.look_at(f0, at_f, ease=C.at(s, "players") - f0)
    kid.look_at(C.at(s, "players"), at_t, ease=7)
    kid.look_at(C.at(s, "still") - 2, at_him, ease=9)
    kid.look_at(C.at(s, "still") + 7, at_him, ease=f1 + 1 - (C.at(s, "still") + 7))
    st.use(s, ada, tom, kid)
    C.cam(s, None, focus=kid.head, handheld=0.006, **cam)
    st.hero(s, "child", kid)
    st.hero(s, "farmer", ada)
    C.lights(s, "gold", near=(3.6, 5.6, 0.0), radius=16.0)


def sq11_stare(st, s, C, nar):
    """BEAT 11  "I watch him back."   frames 673-718 (46 f, 1.92 s), sky gold.
    Words: I 675, watch 679, him 687, back 691. The pause after it is 0.8 s (to frame 718): the stare holds.

    STORY: Portrait lens past his hip and still hand at the foreground edge of the frame. The baby villager stands
    alone in the middle of the path, three-quarter to the lens, head tipped all the way up, staring. Two children
    run past behind it. Slow push in on the big head. About 2 seconds.
    Cast: baby villager (narrator), the watcher (hip and hand only), two baby villagers (background). Effects: slow
    push in, defocused foreground hip and hand.

    MUST BE SEEN, ON WHICH WORD
      frame 673       the push in under way, the two children already running behind
      "watch" 679 .. "back" 691    the child's face, head tipped all the way up (HEAD_PITCH_MAX 35 degrees), sharp
      the whole shot  his hip and still hand soft at the foreground edge; nothing of his face (cropped at the hip)
    SHARED: PLACES "watch_square" (he stands where he stood in beats 9 and 10); the child's place SQ11_CHILD and
      the camera SQ11_CAM are this file's. Cast:
      C.actor("child", "sq"), C.actor("watcher", "sq"), C.actor("kid", "sq_a"), C.actor("kid", "sq_b").
    NEIGHBOURS: before, sq10_grownups (the same child, the same watcher: placed on f0, nothing keyed before);
      after, me12_floating (the meadow, the floating oak). Hard cuts.
    CUT PRIORITY (story): if the narration had to be shortened this line went first; it was kept (63.8 s).
    NOW: SQ11_CAM, 66 mm f/2.0, 0.95 above the ground behind him and east of his LEFT hip (the same side of the
      child-to-him line as beat 10's camera, so the child looks screen-right at him in both shots), looking south
      down the road; a 0.38-block ease_out push on the head. The child stands at the road's east edge 1.41 blocks
      in front of him, facing him, its head tipped all the way back (35 degrees) on his face from frame 673 to 718
      (3/4 to the lens). His hip, hanging hand and teal shirt are soft at the right edge; his head is above the
      frame. ONE child (kid "sq_a", pre-rolled SQ11_KID_LEAD = 32 frames, from 641: it is not in sq10) is already
      at the turn of its run on 673, soft, at the frame's left edge behind the child, its head turned away east-
      south-east (SQ11_KID_LOOK: the side of its head, never a second stare), and darts off east toward house_f out
      of the frame's left edge: half out on 679, gone by 682, so the stare holds alone from "him" (687) through the
      pause. (Pre-rolled 21 frames, the version before, it ran straight at the lens until 687, a second face
      staring at us on "I watch".) The second runner of the story is left out (only
      one fits left of the child's head, and the right side is his arm; two ran straight at the lens and one stuck
      out from behind the child's head): the two children are seen together in beat 9. A warm shadowless fill
      (C.fill "sq_stare", 120 W, out of frame in front of the child) lifts its backlit face to beat 10's level
      (skin rgb 97,66,50 -> 134,93,70).
    MEASURED (tools.hello_geo and projected boxes at 673-718; renders out/test/sqfinal_sq11_stare_688_zones.png,
      sqfinal_sq11_stare_716_zones.png): the child's eyes x 50 %, y 45 %, head x 20-73 % y 29-55 %, face 164 -> 177
      px, 39 degrees off the lens; his body's edge x 79-81 % (a 7 % gap to the child's head); his head box above
      y 19 %, seen from behind (156 degrees off his nose); the running kid's head x -2.9-18.1 % y 34-45 % (673),
      76-78 degrees off the lens 673-676 (119 from 679), x -15.4-11.2 % (679), out of the frame from 682
      (out/test/sqfinal_sq11_stare_673.png, hello_square_strip_sq11runner.png); nothing between the lens and the
      child's face. hello_palette sq11@700 (with the fill): every check passes (stone G/R 0.96, planks s 0.45,
      robe hue 16, villager skin s 0.48, Steve shirt hue 177; child x 22-69 %, 100 % inside the safe area). The
      camera looks 56 degrees off the sun (the contract asks 60-120): the child is backlit, hence the fill.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "sq", place=SQ_WATCH, yaw=0.0)
    kid = C.actor("child", "sq")
    k1 = C.actor("kid", "sq_a")
    cam = SQ11_CAM
    C.put(kid, f0, SQ11_CHILD, toward=SQ_WATCH)
    # the stare: its head right back (HEAD_PITCH_MAX), on his face, from the first frame to the last (cut before
    # the idle, held over it)
    kid.look_at(f0, him, ease=0)
    kid.idle(f0, f1 + 1, seed=12)
    kid.look_at(f0, him, ease=f1 + 1 - f0)
    # one child, pre-rolled (not in sq10, so the pre-roll may start inside sq10's frames): already at the turn on
    # frame 673, darting off east (frame left) out of the frame; beat 9's other child is not here. Started 21 frames
    # before the cut it ran straight at the lens for 15 frames, a second face staring at us on "I watch": now it
    # starts SQ11_KID_LEAD frames before, and its head is turned away east-south-east all the way (a profile)
    k1.place(f0 - SQ11_KID_LEAD, C.stand(SQ11_KID_A[0]), HC.yaw_to(SQ11_KID_A[0], SQ11_KID_A[1]))
    k1.walk(f0 - SQ11_KID_LEAD, [C.stand(p) for p in SQ11_KID_A], speed=2.4, run=True)
    k1.track(f0 - SQ11_KID_LEAD, f1 + 1, SQ11_KID_LOOK, step=3, ease=1)
    st.use(s, kid, k1)
    C.cam(s, None, focus=kid.head, handheld=0.005, **cam)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near=C.stand(SQ_WATCH), radius=16.0)
    # the sun is behind the child (it faces him, north-north-west): its face, in the shade of its own head, came out
    # 0.6 of beat 10's (skin rgb 97,66,50 against 155,110,90). A warm shadowless bounce from the sunlit road, out of
    # frame in front of it, for this shot only
    C.fill("sq_stare", SQ11_FILL["pos"], SQ11_FILL["watts"], [s], color=SQ11_FILL["color"])
