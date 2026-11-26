"""The Hello, sequence MEADOW: the exit gate, the meadow road, the dark forest wall at its end and the three signs
(the floating oak, the bare oaks, the sand pyramid). Beats 6, 7, 8, 12, 13, 14 (shots me06_leave, me07_return,
me08_nohello, me12_floating, me13_bare, me14_pyramid), sky "meadow" (me07 and me08: "dawn"). One function per
shot; the contract is in
films/hello_common.py (tags "me...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE (engine/sets.py hello_set, built into the village: read its docstring, "FOR THE DIRECTOR OF THE HELLO"):
  exit_gate (0.5, 24.5); the road runs north to the forest; the tree line at y 58, the gap at forest_gap
  (0.5, 57.6) (he stands there facing the village); forest_approach (0.5, 54.5); the path road_to_forest (exit_gate
  -> gap -> forest_gap_in, behind the east trunk). The floating oak at (-12.5, 47.5) (floating_oak_under: stand
  here; floating_oak_target: the hanging log); the bare oaks at (17, 44), (20, 46), (17, 48) (bare_oaks_among,
  bare_oaks_center); the pyramid at (12, 45) (pyramid_beside; path pyramid_round, half way round by the west;
  C.set["pyramid"]["sides"]). hello_set's proof cameras are C.set["cameras"] (C.cam(s, "set:floating") etc.):
  gate, side, inside, deep, floating, bare, pyramid; proof stills out/test/sets_sheet_a.png, sets_sheet_b.png.
  Plant-free for cameras: the road and the lane west of it (x -3..3) up to the gap, the bay x -11..-4, y 50..57,
  and the ground between each set camera and its subject. Thick grass 3-7 blocks in front of the trunks.
THE SKIES: "meadow" = the look-dev golden sun (azimuth 62: north-east, behind the wood; elevation 27) with NO haze,
  so the gaps between the trunks are black (with the village's haze the wall is dark brown). Every proof still of
  hello_set was made under exactly this sky. Keep the wood behind the subjects.
  "dawn" (me07, me08: "He came back at sunrise"): since the lead's pass dict(preset="dusk", az=75.0, el=4.0,
  bloom=1.0, grade="warm", haze=0.0, cloud_offset=(9, -6)) (this sequence's request, tested with
  tools/hello_meadow_dawn_test.py): a pink horizon over the wood, an indigo top with the last stars, the clouds pink
  and in new places, the wall still black; looking west (me08) a deep blue sky with pink clouds over the village,
  its lanterns lit. The first dawn ('golden', elevation 9) read as beat 6's afternoon side by side with me06 (the
  same blue sky, every cloud in the same place: both reviews). Stills: out/test/hello_lead_me07_return_470_zones.png,
  hello_lead_me08_nohello_505_zones.png; palette_check passes on 460 and 505 (lead's pass). The story's risk "if it
  still feels like the same afternoon" is answered by the sky, since its night insert cannot be had (fixed cuts).
TAGS TAKEN (twins): child_me (me06, me07, me12, me13: placed on each shot's first frame, never pre-rolled),
  child_me2 (me08: pre-rolled from frame 475, i.e. INSIDE me07: never use it in me07), child_me3 (me14: pre-rolled
  from 782), watcher_me (me07, me08, me13), steve_diamond_me (me06: pre-rolled from 287). A new twin: me4, me5 ...
THIS SEQUENCE'S OWN PLACES AND CAMERAS are the constants below (GATE_CHILD, STEVE_IN, ME08_CAM, ME12_*, ME13_*,
  ME14_*); the only shared camera is CAMS "gate" (me06 = me07: position, aim, lens and handheld unchanged; me07
  opens it to f/2.0, ME07_FSTOP: accepted by the lead and noted at CAMS "gate"). hello_common's PLACES "gate_child"
  (since the lead's pass (0.1, 25.9), this file's spot: GATE_CHILD reads it; the stub's (0.15, 26.6) was dead centre
  on the road's axis, the child a brown box from behind) and "road_stop" (me08). me08's camera is its own:
  C.cam(s, None, **ME08_CAM).
LOOKS: _cheat keeps a villager that watches something beyond itself turned at most MAX_OFF (65) degrees from the
  lens (rendered: at 100-118 degrees the nose hides behind the head and the child is a brown box; at 78 only a 2 px
  nose and part of one eye; at 65 the nose stands out and both eyes show, and the look still points at what it
  watches; at 55 it looks at the camera's side instead); _gaze follows a moving target with such a cheated look.
THE WATCHER (beats 7, 8, 13): C.actor("watcher", "me") = plain Steve, dead still; never his face (beat 7: 30 px tall
  at the gap with the 22 mm gate lens; at f/4 his 8 px face showed two pale eye whites, so me07 is at f/2.0: an even
  skin-coloured smudge).
LIGHT: C.lights(s, "gold", near=<point>, radius=12) (daylight; the village's torches are far away: keep them off).
"""
import math

from engine import characters as CH
from films import hello_common as HC

# ---------------------------------------------------------------------------------------------------------------
# this sequence's own places and cameras (the SHARED ones are hello_common's: CAMS "gate" in me06 / me07)
# ---------------------------------------------------------------------------------------------------------------
# the child's block at the gate, beats 6 and 7 (the same in both): left of the road's axis, so that Steve walks past
# it on its right and the lens sees it in three-quarter (hello_common's "gate_child", (0.15, 26.6), is dead centre:
# the child was a brown box from behind)
GATE_CHILD = HC.PLACES["gate_child"]        # (0.1, 25.9): the shared place since the lead's pass
# Steve's walk in beat 6: from the village, past the lens's right shoulder and the child, onto the road's axis and
# up the meadow road (road_to_forest's own nodes from y 35 on: they follow the terrain)
STEVE_IN = ((1.55, 19.6), (1.5, 23.0), (1.3, 26.5), (0.9, 29.5), (0.6, 32.5))
STEVE_PRE = 32                   # he starts this many frames before beat 6 (in no shot before: a pre-roll is allowed)
ME07_FSTOP = 2.0                 # beat 7's depth of field on the gate camera (beat 6 keeps its f/4): the watcher soft
# beat 8: in the forest gap behind his right shoulder (he faces the village, so his right is west), a little below
# his shoulder, 28 mm tilted 4 degrees down: his teal shoulder and the back of his head soft at the left edge, the
# child down the road in the middle of the frame; a slow push
ME08_STOP_AFTER = 3              # the child stops this many frames after "didn't" (490 + 3; "crouch" is 497)
ME08_CAM = dict(pos=(-0.6, 59.0, 1.2), target=(0.5, 54.6, 0.88), pos1=(-0.52, 58.72, 1.18),
                target1=(0.5, 54.6, 0.86), lens=28.0, fstop=2.0)
# beat 12: low in the meadow east-north-east of the floating oak (the side of hello_set's own 'floating' proof
# camera: the ground behind falls away, sky and clouds under the canopy; from due east a grassy bank filled the gap
# and the wood's south-west trunk stood under the canopy's edge like its own trunk), looking west-south-west; a slow
# linear push from the whole floating canopy and its hanging log to the child under its east edge, lit by the sun
# behind the lens
ME12_CHILD = (-9.5, 48.35)
ME12_CAM = dict(pos=(-4.2, 50.2, 0.3), target=(-12.0, 47.5, 2.0), pos1=(-6.0, 49.6, 0.3),
                target1=(-12.0, 47.3, 1.4), lens=24.0, fstop=2.8)
# beat 13: from the forest edge north-north-east of the bare oaks (hello_set's 'bare' camera, lower, pushing in
# half a block and drifting left), his back among the trunks, the village roofs beyond him; the child at the left edge, east of him
ME13_FACING = (14.0, 30.0)               # where he looks: the village's north-east roofs
ME13_CHILD = (19.3, 46.0)               # between the left trunk and him (at (19.6, 45.7) the trunk cut it in half
#                                         and a dandelion sat behind its crossed arms)
ME13_CHILD_TOWARD = (19.85, 47.35)      # its body faces north-north-east, about at the lens: both its looks (up the
#                                         trunk on its right, him on its left) lie inside the head's 70 degrees
ME13_TURN = 14                          # frames of its head turn from the trunk to him ("takes" - 3 .. "leaves")
ME13_CAM = dict(pos=(21.1, 55.0, 1.9), target=(18.3, 46.5, 2.35), pos1=(21.2, 54.42, 1.9),
                target1=(18.4, 46.5, 2.35), lens=30.0, fstop=3.2)
# beat 14: from the meadow west of the pyramid (the bare trunks behind it), low, a slow sideways track north with
# the child, who walks round the south-west corner and along the west face and stops past the north-west corner
ME14_WALK = ((9.3, 41.4), (7.7, 42.4), (7.7, 46.6))
ME14_STOP = "in"                 # the word on which the child stops (it walks on "Nobody built the sand pyramid")
ME14_SPEED = 1.35
ME14_OFF = 65.0                  # its head on the wood, cheated to at most this far from the lens (walk and stop)
ME14_CAM = dict(pos=(2.6, 44.6, 0.75), target=(12.0, 45.2, 0.95), pos1=(2.6, 45.7, 0.75),
                target1=(12.0, 45.7, 0.95), lens=26.0, fstop=2.8)
MAX_OFF = 65.0           # a villager watching something beyond itself is turned at most this far from the
#                                  lens (degrees between its nose and the lens): its nose stands out and both eyes
#                                  show, never the brown box from behind (CONTRACT: villagers from behind; at 78 only
#                                  a 2 px nose and part of one eye showed, review: check_hello_meadow_me06_off65/78)


def _road(C, y0, y1):
    """The points of road_to_forest between y0 and y1 (on the ground: the path follows the terrain)."""
    pts = [p for p in C.v.paths["road_to_forest"] if y0 <= p[1] <= y1]
    return pts


def _bearing(a, b):
    """Compass bearing (degrees clockwise from north, +Y) from a to b."""
    return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))


def _cheat(c, frame, target, cam_pos, max_off=MAX_OFF):
    """The point c looks at instead of `target` so that its nose is never more than `max_off` degrees from the lens:
    the target itself while it is within that, otherwise the same point turned toward the camera (about the eyes)."""
    eye = c.eye_point(frame)
    t = (target[0], target[1], target[2]) if len(target) == 3 else (target[0], target[1], eye.z)
    to_t = _bearing(eye, t)
    to_cam = _bearing(eye, cam_pos)
    off = (to_t - to_cam + 180.0) % 360.0 - 180.0          # signed: target relative to the camera direction
    if abs(off) <= max_off:
        return t
    b = math.radians(to_cam + math.copysign(max_off, off))
    flat = math.hypot(t[0] - eye.x, t[1] - eye.y)
    return (eye.x + flat * math.sin(b), eye.y + flat * math.cos(b), t[2])


def _gaze(c, f0, f1, target_of, step=3):
    """Keep c's head on target_of(frame) from f0 to f1 (re-aimed every `step` frames, smooth: Character.track with
    a target that is a function of the frame). The head is already on target_of(f0) at f0 (no ease-in)."""
    yk, pk = [], []
    f = int(f0)
    while True:
        yaw, pitch = c._aim(target_of(f), f)
        yk.append((f, yaw))
        pk.append((f, -pitch))
        if f >= f1:
            break
        f = min(int(f1), f + step)
    CH._segment(c.head, "rotation_euler", 2, yk, "BEZIER")
    CH._segment(c.head, "rotation_euler", 0, pk, "BEZIER")
    return f1


def me06_leave(st, s, C, nar):
    """BEAT 6  "One day he put on his best armor and walked into the woods."   frames 319-420 (102 f, 4.25 s), sky
    meadow. Words: One 321, day 327, he 334, put 337, on 341, his 344, best 348, armor 356, and 372, walked 375,
    into 384, the 388, woods 391. The pause after it is 0.8 s; the encoder dips to black around frame 421 (it is
    fading from 417).

    STORY: Golden hour at the exit gate, low wide lens, camera still. Steve in full enchanted diamond armor, the
    glint sliding over it, diamond sword in hand, walks away from the camera down the meadow road toward the black
    wall of dark oak trunks at its far end, getting small and bright against it. In the foreground the baby
    villager stands on the last path block in three-quarter profile, watching him go. About 4 seconds. The next
    shot repeats this framing.
    Cast: Steve, baby villager (narrator). Effects: full diamond armor with enchantment glint, diamond sword, dark
    oak forest wall at the end of the road.

    MUST BE SEEN, ON WHICH WORD
      frame 319       Steve already walking away (pre-rolled: he is in no shot before), the glint on the armor
      "best" 348 .. "armor" 356    Steve still big enough for the diamond armor to read (cyan, helmet, sword)
      "woods" 391 .. 420   Steve small and bright against the black trunks, NOT yet past the tree line (y 58): the
                      sets notes: a figure inside the wood stays fully lit, so the shot ends before he reaches it
      the whole shot  the child on the last path block in three-quarter profile (its nose against the meadow:
                      cheat its look toward the lens, C.to_lens; never the brown box from behind)
    SHARED: CAMS "gate" (= hello_set's gate camera), EXACTLY the same in me07_return: no move, only the handheld
      (keep it tiny: 0.004); me07 only opens it to f/2.0 (ME07_FSTOP, see there). The child's block in both shots:
      GATE_CHILD (replaces PLACES "gate_child").
      Cast: C.actor("steve_diamond", "me"), C.actor("child", "me").
    NEIGHBOURS: before, dg05_nod (the doorstep, the child runs off); after, me07_return: the same frame after a dip
      to black (the night that passed).
    RISKS (story): "He came back at sunrise without it": at distance diamond armor and the teal shirt are both in
      the cyan family: keep Steve near enough while the armor must read (he walks 4.3 blocks a second). The glint:
      players.equip(enchanted=True) is on (C.actor did it, and the stamp work-around).
    NOW: CAMS "gate" exactly (22 mm f/4, no move, handheld 0.004), focus on Steve's head (it follows him). Steve
      (pre-rolled from 287 in the village) is at speed on frame 319, 2.8 blocks from the lens, past its right shoulder
      and past the child, his back filling the right half (diamond helmet and glint at y 25-41 %); he walks up the
      road's axis at the player's 4.32 blocks/s and is 9 blocks off on "armor" (the suit reads cyan, helmet, sword),
      16 on "woods", 20.6 at 420: small and bright against the black trunks, 17 blocks short of the tree line
      (never inside the wood). The child on GATE_CHILD (its own block, left of the axis), body toward the road
      ahead: its head is on Steve as he passes (three-quarter face, looking up at him, 319-325), then follows him
      up the road cheated to MAX_OFF, 65 degrees (nose in profile toward him, both eyes), and sinks a little from
      "woods" (395-411): beat 7 finds it with its head down. Hero: Steve.
    MEASURED (tools.hello_geo; stills out/test/hello_meadow_final_me06_leave_320/356/395[_zones].png): Steve's head
      x 57-87 %, y 25-41 % at 320 (111 px wide), x 45-53 %, y 45-49 % on "armor" (356, 32 px), 18 px at 395, 14 px at
      420, 167-178 degrees off his nose (his back, always); the child's eyes x 25 %, y 56 %, head y 48-62 %, face
      45 px (hello_geo prints an adult's 91), 49 degrees off the lens at 320, 65 from 325 on. palette_check
      me06_leave@356 passes everything (hero steve 100 % inside the safe area).
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_diamond", "me")
    kid = C.actor("child", "me")
    cam = C.camera_spec("gate")["pos"]
    # Steve: pre-rolled from the village, at speed on frame 1, past the lens's right shoulder and the child, then
    # up the road's axis toward the wall (never past the tree line: the walk is cut by the dip long before)
    pts = [C.stand(p) for p in STEVE_IN] + list(_road(C, 34.0, 53.0))
    fs = f0 - STEVE_PRE
    steve.place(fs, pts[0], HC.yaw_to(pts[0], pts[1]))
    steve.walk(fs, pts, ramp=(True, False))
    # the child on its block, body toward the road ahead of it; its head on Steve as he passes, then following him
    # up the road, turned no further from the lens than MAX_OFF (its nose in profile against the meadow)
    C.put(kid, f0, GATE_CHILD, yaw=HC.yaw_to(GATE_CHILD, (GATE_CHILD[0] + 0.94, GATE_CHILD[1] + 0.34)))
    look = lambda f: _cheat(kid, f, steve.eye_point(f), cam)
    kid.look_at(f0, look(f0), ease=0)
    down = C.at(s, "woods") + 3
    _gaze(kid, f0, down, look, step=3)
    # as he reaches the black wall ("woods") the child's head sinks a little: it is how beat 7 finds it at dawn
    d = look(down + 14)
    kid.look_at(down, (d[0], d[1], d[2] - 2.2), ease=16)
    st.use(s, steve, kid)
    C.cam(s, "gate", focus=steve.head, handheld=0.004)
    st.hero(s, "steve", steve)
    C.lights(s, "gold", near=C.A["exit_gate"], radius=12.0)


def me07_return(st, s, C, nar):
    """BEAT 7  "He came back at sunrise without it."   frames 421-484 (64 f, 2.67 s), sky dawn; the encoder dips
    to black ON frame 421 (dip out 4, hold 1, back 4: black on 421-422, up again by 426).
    Words: He 423, came 426, back 433, at 439, sunrise 442, without 457, it 467.

    STORY: A six-frame dip to black, then the identical framing. The road is empty except for one figure in
    Steve's plain teal shirt, no armor, empty hands, standing dead still at the far end where the trees begin,
    facing the village. He is out of focus and too small for a face to be read, but large enough that bare arms
    and a bare head show. The child, on the same path block, lifts its head. No camera move. About 3 seconds.
    Cast: the watcher (far, face unreadable), baby villager (narrator). Effects: dip to black to mark the night
    that passed, same camera as beat 6, focus held on the child.

    MUST BE SEEN, ON WHICH WORD
      frame 426 on    (the picture is back) the same frame as me06: the empty road, him at forest_gap
      "sunrise" 442   the child lifts its head toward him (a slow look_at up, held)
      "without" 457 .. "it" 467    bare arms, bare head, teal shirt: no armor, no sword
    SHARED: CAMS "gate" exactly as in me06 (the same handheld seed is fine; f/2.0 instead of f/4, which only
      changes the depth of field: reported to the lead). GATE_CHILD, C.A["forest_gap"]
      (he stands there facing the village; yaw 0 faces south). Cast: C.actor("watcher", "me"), and the child: the
      child of me06 is in the shot before: place it on f0 (no pre-roll needed: the frame is black until 422), or a
      FRESH twin C.actor("child", "me4"). NOT "me2": me08 pre-rolls child_me2 from frame 475, inside this shot.
    SKY: "dawn" (the module docstring): the same camera, another light.
    NEIGHBOURS: before, me06_leave; after, me08_nohello (the same road from the side: the child runs up to him).
    RISKS (story): the golden sky plays both evening and morning: answered by the "dawn" sky, the dip and the
      figure large enough that bare arms and a bare head show; beat 8's teal shoulder confirms it. The night insert
      the story offers is not available (the narration fixes every cut). Plain Steve skin (sets notes: his eye
      whites are two pale dots at 30 px: the white-eyed skin would be brighter).
    NOW: CAMS "gate" exactly as me06 (the same position, aim, lens and handheld) but at f/2.0 (ME07_FSTOP; behind
      the dip, the frame is the same), focus on the child (he is soft at 35 blocks). He stands at
      forest_gap, yaw 0 (facing the village), dead still, nothing keyed but his place. The child on GATE_CHILD (the
      same block as me06), its body turned back toward the gate, head down toward the ground (its face, looking
      down, three-quarter to the lens): it waited all night. Its head drifts a little from 423 (alive as the dip lets
      the picture back), and from 440 to 454 ("sunrise" 442) it lifts and turns up the road to him, cheated to
      MAX_OFF (nose in profile, both eyes); then it keeps peering at him, the head rising about 7 degrees and turning
      4 more to the cut (456-482: the tail is not a freeze frame). Hero: the child.
    MEASURED (tools.hello_geo; stills out/test/hello_meadow_final_me07_return_432/470[_zones].png under the first
      dawn, out/test/hello_lead_me07_return_470_zones.png under the dusk-preset dawn of the lead's pass): him x 50 %,
      y 52 %, face 8 px, 35 blocks: at f/2.0 an even skin-coloured smudge (brightest face pixel rgb(132,98,87) against
      a face mean of (92,71,62); at f/4 the eye whites were two dots of (169,145,143)); bare teal arms, bare head and
      blue legs read; the child's eyes x 25 %, y 56 %, 39 degrees off the lens at 426 (head down), 65 at 454, 69 at
      484. palette_check me07_return@460 (lead's pass, new dawn) passes everything (robe hue 7, skin s 0.44, plants
      0.87 of the grass, hero child x 15-34 %, y 50-59 %, 100 % inside).
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "me")
    cam = C.camera_spec("gate")["pos"]
    him = C.watcher(s, "me", place=C.A["forest_gap"], yaw=0.0)
    # the child waited on its block all night: body turned back toward the gate, head down; it drifts a little
    # (alive from the first frame the dip lets through), and on "sunrise" it lifts its head and turns it up the road
    # to him (cheated toward the lens: the nose in profile)
    C.put(kid, f0, GATE_CHILD, yaw=HC.yaw_to(GATE_CHILD, (GATE_CHILD[0] + 0.87, GATE_CHILD[1] - 0.5)))
    gx, gy = GATE_CHILD
    kid.look_at(f0, (gx + 1.1, gy - 0.9, 0.0), ease=0)
    up = C.at(s, "sunrise")
    kid.look_at(f0 + 2, (gx + 1.3, gy - 0.35, 0.0), ease=up - 4 - f0 - 2)
    lift = kid.look_at(up - 2, _cheat(kid, up + 12, him.eye_point(up), cam), ease=14)
    # then it keeps peering at him: a slow settle of the head, a few degrees higher and nearer him, to the cut (the
    # locked gate camera gives the tail no other life)
    e = him.eye_point(f1)
    kid.look_at(lift + 2, _cheat(kid, f1, (e.x, e.y, e.z + 3.5), cam, max_off=MAX_OFF + 4.0), ease=f1 - lift - 4)
    st.use(s, kid)
    # the gate camera exactly (position, aim, lens, handheld), but at f/2.0: at f/4 his 8 px face showed two pale eye
    # whites 35 blocks off; at f/2.0 it is an even smudge (the frame is the same; the dip hides the change)
    C.cam(s, "gate", focus=kid.head, handheld=0.004, fstop=ME07_FSTOP)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near=C.A["exit_gate"], radius=12.0)


def me08_nohello(st, s, C, nar):
    """BEAT 8  "He didn't crouch."   frames 485-540 (56 f, 2.33 s), sky dawn (the morning of beat 7).
    Words: He 487, didn't 490, crouch 497. The pause after it is 1.3 s (frames ~510-540: nothing comes back).

    STORY: The same road from the side, at child height. The shot opens on the child's last two running steps. It
    stops three blocks short of him, tips its head back and nods twice. His teal shoulder and the back of his head
    sit out of focus at the edge of the foreground. Nothing comes back. Hold on the child with its head still tipped
    up. About 2.5 seconds.
    Cast: baby villager (narrator), the watcher (shoulder and back of head only). Effects: baby villager run and
    stop, nod twice, unanswered, strong defocus on the foreground figure.

    MUST BE SEEN, ON WHICH WORD
      frame 485       the child running (two last steps: a twin pre-rolled, C.actor("child", "me2"))
      "didn't" 490    it stops at "road_stop", three blocks short of him
      "crouch" 497 .. about 520   head tipped back (look_at his face), two nods (C.hello_nod)
      to frame 540    hold: the head still tipped up; he does not move at all
      the whole shot  his teal shoulder and the back of his head soft at the foreground edge; NEVER his face
    SHARED: C.A["forest_gap"] (his place, as in me07), PLACES "road_stop". Cast: C.actor("watcher", "me"),
      C.actor("child", "me2") (a twin: the "me" child is in me07, the shot before, and this one must already run).
    NEIGHBOURS: before, me07_return (the gate camera); after, sq09_watches (the square). Hard cuts.
    NOTES: the last 20 blocks of road lie in the wood's shadow under this sky (sun in the north-east): the child
      at road_stop is in shade; a camera from the west side of the road ("from the side") puts the low sun behind
      the lens's left shoulder. The 'side' proof camera (C.set["cameras"]["side"]) is a start.
    NOW: ME08_CAM: in the forest gap behind his right shoulder, at his shoulder height (z 1.2), 28 mm f/2.0 tilted
      4 degrees down, a slow push (0.3 block); focus on the child. His head (back and ear side) and teal shoulder
      soft at the left edge, his head turned to the child (only his head: he is placed once, still). The child
      (child_me2, pre-rolled from 475) runs the last 3.3 blocks of the road toward him, running on frame 485, stops
      on road_stop at 493 ("didn't" 490), its head goes up to his face (491-497) and nods twice on "crouch" (497-511);
      then holds, head up, to 540. Nothing comes back. The village beyond in the low sun, the child in the wood's
      shade. Hero: the child.
    MEASURED (tools.hello_geo; stills out/test/hello_meadow_final_me08_nohello_487/505[_zones].png, and under the
      lead's dusk-preset dawn out/test/hello_lead_me08_nohello_505_zones.png): the child's eyes x 50-56 %, y 53-55 %,
      head y 48-58 %, face 33-43 px, 10-14 degrees off the lens; his head x -71..18 %, y -4..41 % (the edge of the
      frame), 138-142 degrees off his nose: never his face. palette_check me08_nohello@505 (new dawn) passes
      everything (stone G/R 0.94, skin rgb(72,47,39) s 0.46: darker in the wood's shade, its face and eyes still read;
      steve shirt hue 181, pants min channel 15; hero child x 41-59 %, y 48-57 %, 100 % inside).
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "me", place=C.A["forest_gap"], yaw=0.0)
    kid = C.actor("child", "me2")
    stop = C.P("road_stop")
    # the child's last running steps (a twin, pre-rolled: the "me" child is in me07): it stops on "didn't"
    a = (stop[0] + 0.1, stop[1] - 3.3, stop[2])
    run = int(round(3.3 / 4.4 * 24))                      # frames of the run (Character's run speed 4.4)
    fr = C.at(s, "didn't") + ME08_STOP_AFTER - run        # pre-rolled from before the shot: running on frame 1
    kid.place(fr, a, HC.yaw_to(a, stop))
    end = kid.walk(fr, [a, stop], run=True)
    kid.look_at(end - 2, him, ease=6)                     # the head goes back to his face as it stops ...
    C.hello_nod(kid, C.at(s, "crouch"))                   # ... and nods twice on "crouch": nothing comes back
    him.look_at(f0, kid, ease=0)                          # his head on the child (only his head: dead still)
    st.use(s, kid)
    C.cam(s, None, focus=kid.head, handheld=0.006, **ME08_CAM)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near=C.A["forest_gap"], radius=12.0)


def me12_floating(st, s, C, nar):
    """BEAT 12  "He used to take the trunk and leave the tree floating."   frames 719-792 (74 f, 3.08 s), sky
    meadow. Words: He 721, used 723, to 729, take 732, the 738, trunk 741, and 755, leave 758, the 764, tree 766,
    floating 774.

    STORY: Meadow, low wide shot against a clean horizon. A lone oak with its lower trunk gone: the leafy canopy and
    its last two logs hang in mid-air three blocks above the grass. The baby villager stands in the gap underneath,
    looking straight up at it. About 3.5 seconds.
    Cast: baby villager (narrator). Effects: floating oak (canopy plus top logs, air below), clean sky visible
    through the gap.

    MUST BE SEEN, ON WHICH WORD
      frame 719       already alive: a slow drift or push, the child's head moving
      "trunk" 741     the gap under the canopy: clean sky through it, the hanging log
      "floating" 774  the child under it looking straight up (its face toward the lens, head tipped back)
    SHARED: none. C.A["floating_oak_under"], C.A["floating_oak_target"]; camera "set:floating" (hello_set's: 26 mm
      from 10 blocks east-north-east, 0.5 above the grass; proof still sets_floating in sets_sheet_b.png).
    NOTES (sets): hello_set's oak has air=3, logs=4: one log hangs under the canopy over two blocks of air, the
      canopy three blocks up ("two logs over three blocks of air" cannot both be seen on a vanilla oak).
    RISKS (story): the canopy must read as hanging in the air, not as a tree behind a rise: three clear blocks of
      sky under it, the camera low, the child in the gap for scale.
    NEIGHBOURS: before, sq11_stare (the square); after, me13_bare. Hard cuts.
    NOW: ME12_CAM: low (z 0.3) in the meadow east-north-east of the oak (the side of hello_set's own 'floating'
      proof camera), looking west-south-west, 24 mm f/2.8, a slow LINEAR push of 1.9 blocks from the whole floating
      canopy (sky and clouds above and under it, the hanging log over the gap, the ground behind falling away) to
      the child under the canopy's east edge (ME12_CHILD), the hanging log above and behind its head; focus on the
      child. The child faces the lens and looks up at the leaves over it (pitch at the head's 35-degree stop: its
      face tipped back), turning to its right on "trunk", and on "floating" (768-780) about 12 degrees back toward
      the lens and higher, still some 30 degrees off it in yaw: tipped up and away, looking up at the leaves (at
      8-15 degrees off, from this low lens, it stared into the camera with a black slot under its nose). The sun is
      behind the lens: its face is lit. Hero: the child.
    MEASURED (tools.hello_geo, tools.hello_meadow_probe keys; stills
      out/test/hello_meadow_final_me12_floating_719/741/778[_zones].png): on frame 719 the whole canopy (y 9-50 %),
      the hanging log and sky with clouds under it; the child's eyes x 50 %, y 59 %, face 28 px at 719; x 51 %,
      y 58 %, 32 px, its head turned 41 degrees from its body on "trunk" (741: 55 off the lens with the tip); x 52 %,
      y 56 %, 38 px, turned 29 degrees on "floating" (779 on: 48-49 off the lens with the tip; both eyes and the nose
      show), always tipped back 35 degrees. The aim lowers during the push (target z 2.0 -> 1.4), so the tipped-back
      chin, at 62 % (the top of the caption band) on the first frames, is clear of it from "trunk" on (61 % at 778).
      A leaf block of another tree at x 93-100 %, y 26-40 % (under the Reels icon column). palette_check
      me12_floating@778 passes everything (hero child x 44-63 %, y 50-61 %, 99 % inside).
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "me")
    c = ME12_CAM
    # the child under the canopy's east edge, body toward the lens; it looks up at the leaves over it (the head's
    # pitch stops at 35 degrees: its face tipped back toward the lens), and a little higher on "floating"
    C.put(kid, f0, ME12_CHILD, toward=(c["pos1"][0], c["pos1"][1]))
    kx, ky = ME12_CHILD
    kid.look_at(f0, (kx + 0.6, ky + 0.25, 2.6), ease=0)
    kid.look_at(f0 + 1, (kx + 0.5, ky - 0.2, 3.2), ease=C.at(s, "trunk") - f0 - 1)
    # on "floating" the head comes back about 12 degrees toward the lens but stays some 30 degrees off it in yaw (its
    # right): 8-15 degrees off, from the low lens, the tipped-back face stared into the camera with a black slot under
    # its nose; 30 off it reads as looking up at the leaves (review: check_hello_meadow_me12_look_y30_778.png)
    kid.look_at(C.at(s, "floating") - 6, (kx + 0.3, ky - 0.05, 4.0), ease=12)
    st.use(s, kid)
    C.cam(s, "set:floating", pos=c["pos"], target=c["target"], pos1=c["pos1"], target1=c["target1"],
          lens=c["lens"], fstop=c["fstop"], focus=kid.head, handheld=0.006, ease="linear")
    st.hero(s, "child", kid)
    C.lights(s, "gold", near=C.A["floating_oak_under"], radius=12.0)


def me13_bare(st, s, C, nar):
    """BEAT 13  "Now he only takes the leaves."   frames 793-843 (51 f, 2.12 s), sky meadow.
    Words: Now 795, he 802, only 805, takes 812, the 820, leaves 823.

    STORY: Three lone oaks stripped to bare logs against the sky, not one leaf block left. He stands among them with
    his back to the camera, facing the village roofs in the distance. The baby villager is small at the edge of the
    frame, nose in profile, looking at him. About 2.2 seconds.
    Cast: the watcher (from behind), baby villager (narrator). Effects: three leafless oaks, logs only.

    MUST BE SEEN, ON WHICH WORD
      "Now" 795       the bare trunks against the sky, him among them, his back to us
      "leaves" 823    the child at the frame's edge, nose in profile, looking at him (cheated toward the lens)
    SHARED: none. C.A["bare_oaks_among"] (his place, facing the village), camera "set:bare" (30 mm; proof still
      sets_bare in sets_sheet_b.png). Cast: C.actor("watcher", "me"), C.actor("child", "me").
    NEIGHBOURS: before, me12_floating; after, me14_pyramid. Hard cuts.
    NOW: ME13_CAM: hello_set's 'bare' camera lowered a little (z 1.9), 30 mm f/3.2, pushing in 0.5 block (ease_out:
      at speed on frame 1) with a slight drift left;
      focus on him. He stands at bare_oaks_among, his back to the lens, facing the village's north-east roofs
      (ME13_FACING), dead still. The child (ME13_CHILD) small at the left edge, east of him, between the left trunk
      and him, its body facing about the lens (ME13_CHILD_TOWARD: both its looks inside the head's 70 degrees; facing
      west-south-west both were past the stop and the head never moved): it looks up the nearest trunk (on its right,
      the frame's left), then on "takes" (809-823) turns its head 88 degrees to him, cheated 21 degrees toward the
      lens (nose and both eyes: three-quarter) by "leaves". Heroes: him, the child.
    MEASURED (tools.hello_geo, tools.hello_meadow_probe keys; stills out/test/hello_meadow_final_me13_bare_801/825
      [_zones].png): his eyes x 47-48 %, y 47 %, 177-178 degrees off his nose (his back); the child's eyes x 32 %,
      y 57 %, face 23-24 px, its head 50 degrees off the lens on the trunk, 36 as it turns past the lens (817), 57 on
      him; nothing between the lens and either; its body hides the dandelion on the bank. palette_check
      me13_bare@823 passes everything (heroes: watcher x 45-52 %, y 45-49 %, child x 24-37 %, y 54-59 %, both 100 %
      inside the safe area).
    """
    f0, f1 = s.frame_start, s.frame_end
    c = ME13_CAM
    among = C.A["bare_oaks_among"]
    # him among the bare trunks, his back to the lens, facing the village roofs; dead still
    him = C.watcher(s, "me", place=(among[0], among[1]), yaw=HC.yaw_to(among, ME13_FACING))
    # the child small at the frame's left edge, beside him on the rise (east of him, a little nearer the village):
    # it looks up the nearest trunk first, then turns its head to him on "takes" (nose in profile toward him, cheated
    # a little toward the lens)
    kid = C.actor("child", "me")
    C.put(kid, f0, ME13_CHILD, toward=ME13_CHILD_TOWARD)
    kid.look_at(f0, (20.3, 46.8, 4.5), ease=0)              # up the trunk's west side (its face toward the lens)
    kid.look_at(C.at(s, "takes") - 3, C.to_lens(kid, C.at(s, "the"), him.eye_point(f0), c["pos1"], degrees=21.0),
                ease=ME13_TURN)
    st.use(s, kid)
    C.cam(s, "set:bare", pos=c["pos"], target=c["target"], pos1=c["pos1"], target1=c["target1"], lens=c["lens"],
          fstop=c["fstop"], focus=him.head, handheld=0.006)
    st.hero(s, "watcher", him)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near=among, radius=12.0)


def me14_pyramid(st, s, C, nar):
    """BEAT 14  "Nobody built the sand pyramid in the meadow."   frames 844-914 (71 f, 2.96 s), sky meadow.
    Words: Nobody 846, built 859, the 865, sand 867, pyramid 877, in 890, the 894, meadow 895. The pause after it
    is 0.5 s.

    STORY: A neat three-layer pyramid of sand blocks sits on the grass, taller than the child, with the bare trunks
    behind it. The baby villager walks half way around it and stops, nose in profile. Slow sideways track. About
    2.7 seconds.
    Cast: baby villager (narrator). Effects: sand pyramid, five by five base, three layers, slow sideways track.

    MUST BE SEEN, ON WHICH WORD
      frame 844       the child already walking: the "me" child is in me13, the shot before, so the walker is the
                      twin C.actor("child", "me3"), pre-rolled a few frames (it is in no shot before)
      "pyramid" 877   the whole pyramid, the bare trunks behind it
      "meadow" 895 .. 914   the child stopped, nose in profile
    SHARED: none. C.A["pyramid_beside"], path C.v.paths["pyramid_round"], camera "set:pyramid" (35 mm; proof still
      sets_pyramid in sets_sheet_b.png).
    NEIGHBOURS: before, me13_bare; after, dg15_a (late gold at the child's door). Hard cuts.
    NOW: ME14_CAM: low (z 0.75) in the meadow west of the pyramid, 26 mm f/2.8, a slow LINEAR sideways track 1.1
      blocks north (the track lags the child a little, so it walks slightly away from the lens); focus on the
      child. The whole pyramid with the bare trunks above and behind it. The child (child_me3, pre-rolled from 782)
      comes round the south-west corner and walks north along the west face, right to left across the frame at a
      slow 1.35 blocks/s, its head on the wood ahead and to its left, cheated to at most ME14_OFF (65) from the lens
      for the whole walk (nose and eye in profile; with the head straight along the walk it was a blank pink box
      from 848 to 896); it stops on "in" (890) and lifts its head up the meadow toward the wood he went into (the
      forest gap: nose and eye toward the lens) for "meadow" (895-914). Hero: the child.
    MEASURED (tools.hello_geo, tools.hello_meadow_probe keys; stills out/test/hello_meadow_final_me14_pyramid_877/900
      [_zones].png): the child's eyes x 71 % (846), 35 % (877), 23 % (900), y 53 %, face 34-35 px; its head 55-70
      degrees off the lens for the whole walk (67 on "pyramid"), lifted 22 degrees on 890-902 and 67-69 off to 914;
      the pyramid x 5-97 % on "pyramid". A grass tuft one block from the lens at the left edge (x 0-10 %) at the end,
      soft. palette_check me14_pyramid@900 passes everything (hero child x 17-34 %, y 47-56 %, 100 % inside).
    """
    f0, f1 = s.frame_start, s.frame_end
    c = ME14_CAM
    kid = C.actor("child", "me3")
    # the child (a twin: the "me" child is in me13) round the pyramid's south-west corner and along its west face,
    # right to left across the frame, in profile; it stops past the north-west corner and turns to the pyramid
    pts = [C.stand(p) for p in ME14_WALK]
    stop = C.at(s, ME14_STOP)
    length = sum(math.dist(a[:2], b[:2]) for a, b in zip(pts, pts[1:]))
    fs = stop - int(round(length / ME14_SPEED * 24.0))          # pre-rolled: it stops on the word
    kid.place(fs, pts[0], HC.yaw_to(pts[0], pts[1]))
    end = kid.walk(fs, pts, speed=ME14_SPEED)
    # while it walks its head is on the wood ahead and to its left (the lens's side), cheated to at most ME14_OFF
    # from the lens: nose and eye in profile for the whole walk (with the head straight along the walk it was a blank
    # pink box from 848 on: 83-104 degrees from the lens); on "in" it stops and lifts its head to the wood he went
    # into (the forest gap)
    gap = C.A["forest_gap"]
    cam = c["pos1"]
    look = lambda f: _cheat(kid, f, (gap[0], gap[1], 1.0), cam, max_off=ME14_OFF)
    kid.look_at(fs, look(fs), ease=0)
    _gaze(kid, fs, end - 1, look, step=4)
    kid.look_at(end - 1, _cheat(kid, end + 13, (gap[0], gap[1], 6.0), cam, max_off=ME14_OFF), ease=14)
    st.use(s, kid)
    C.cam(s, "set:pyramid", pos=c["pos"], target=c["target"], pos1=c["pos1"], target1=c["target1"],
          lens=c["lens"], fstop=c["fstop"], focus=kid.head, handheld=0.006, ease="linear")
    st.hero(s, "child", kid)
    C.lights(s, "gold", near=C.A["pyramid_beside"], radius=12.0)
