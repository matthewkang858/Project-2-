"""The Hello, sequence INTERIOR: the child's house (house_a) at night. Beats 3, 16, 17 (shots in03_bed, in16_empty,
in17_window); sky "night", and beat 3 turns "gold" inside the shot ON the word "ended". Beat 17 is filmed from
OUTSIDE, through the window (the story's own fallback, see in17_window). One function per shot; the contract is in
films/hello_common.py (tags "in...", C.actor, C.cam, C.lights, C.fill, st.use / st.hero).

THE ROOM (hello_common's docstring has it block by block): the bed wing x 15..20, y -14..-8; the beds along the
  east wall, pillows east: Steve's RED bed is the SOUTH one, HC.RED_BED = "house_a_bed_1" (anchor (19.0, -11.5,
  1.56)), the child's white bed the NORTH one, HC.CHILD_BED = "house_a_bed_2" (19.0, -9.5, 1.56); a wall torch
  between the pillows (19, -11, 2); above it, in the east gable, ONE glass pane (20, -11, 4) (the bed wing has no
  ceiling: the roof's ridge is at z 6, so the pane is seen from inside); the two-pane window of the north wall
  (17..18, -8, 2) behind the child's bed. The west wing: the one pane facing the plaza at (10, -11, 2); the film
  moves house_a's chair RIGHT UNDER it (oak stairs facing east at (11, -11): the seat is its west half, z 1.5, the
  back its east half, z 2.0) and the table beside it at (11, -10) (hello_common._edit).
THE BED CAMERA of beats 3 and 16 (BED_CAM, ONE constant used by both shots, with the same linear push speed, so
  in16 is exactly the first 49 frames of in03's camera path): inside the room, high at the west end of the bed wing
  and a little toward Steve's side, 21 mm, looking east down both beds to the pillows. The red bed with Steve in
  iron is at the right and nearer, the child's white bed at the left, the wall torch between the pillows, and the
  gable pane above it, through which the camera sees SKY: purple night with stars, then (from "ended") blue sky
  with white clouds. (The plan's camera stood outside the south wall, 32 mm: both heads were 60-80 px blobs
  touching each other in a small lit box in the middle of a dark frame, and its north window showed the lamp-post
  block, never a sky: every line through those panes from a camera that holds both heads ends on a block.)
  MEASURED (tools.hello_geo, 540x960): at 146 the child's head x 19-34 %, y 50-58 %, face 58 px (eyes y 53 %);
  Steve's head x 62-75 %, y 52-61 %, face 64 px (eyes y 55 %); a quarter of the frame width between the heads; the
  pane about x 42-64 %, y 10-25 % (sky through its middle and top: ray casts --through; its lowest row shows the
  canopy of a tree east of the house). At 210 (end of the push): child 17-35 %, Steve 63-77 %, faces 61 / 67 px.
THE SKIES: "night" (since the lead's pass the moon in the north-east behind the house, azimuth 35, elevation 21;
  it was in the west, azimuth 176: inside the room nothing changed, in03@160 mean luma 80.0 -> 80.1, the pane still
  purple night with stars) and, from the word "ended" in beat 3, "gold"
  (sun azimuth 215, elevation 24). The film calls st.sky_change; the shot keys the light on both sides:
  C.lights(s, "night_room", **room) and, from the change, C.lights(s, "gold_room", at=change, **room) (the SAME
  near / radius: Stage.lights at= sets every light again) + C.morning(s, change) (hello_common.MORNING: a warm
  shadowless 1300 W light inside the north window, behind the child's bed).
  MEASURED at the snap with BED_CAM (mean luminance of 540x960 stills, 181 night against 195 gold,
  out/test/hello_in_t5_in03_bed_181.png / _195.png): the pane 84 -> 156 (x1.85), walls 117 -> 183 (x1.56), floor
  72 -> 140 (x1.93), the child's bed 127 -> 188 (x1.48), the red bed 92 -> 116 (x1.26), whole frame 80 -> 142
  (x1.77). palette_check in03@160 (night), in03@195 (gold), in16@1020 pass every check they make (night ones
  re-run under the lead's moon: stone G/R 0.97, planks s 0.48 / 0.49, heroes 100 % inside).
LIGHT: house_a's torches and its room fill are one group ("house_a"): raise them only together (LIGHTS
  "night_room"); lit cobblestone and villager skin are at the palette limit in there (CONTRACT.md). Film-local
  lights: C.fill("in_<name>", ...) (the name must start with "in"): only "in_pane" (beat 17).
"""
import math

from mathutils import Vector

from engine import characters
from films import hello_common as HC

PANE_FILL = dict(pos=(11.05, -10.85, 2.95), watts=260.0, color=(1.0, 0.88, 0.72))    # in17: on the child's face
# beat 17: the child stands on the HIGH back half of the chair under the pane (oak stairs facing east: x 11.5..12,
# top z 2.0), at the north side of the chair, so the camera from the south-west sees it centred in the pane. On
# the seat ((11.25, -10.5, 1.5), the first PLACES "window_chair") its eyes are at z 2.16, 0.16 above the sill:
# only the eyes showed.
KID_WINDOW = HC.PLACES["window_chair"]     # (11.75, -10.15, 2.0): the shared place since the lead's pass

# THE BED CAMERA of beats 3 and 16 (one constant, both shots): inside the room, high at the west end of the bed
# wing, a little toward Steve's side, looking east down the two beds to their pillows: the red bed and Steve at the
# right and nearer, the child's white bed at the left, the wall torch between the pillows, and the east gable's
# glass pane above it, through which the camera sees SKY (night: stars; from "ended": day). A slow linear dolly in
# (BED_PUSH blocks a frame, the same speed in both shots, so in16 is the first 49 frames of in03's path).
BED_CAM = dict(pos=(15.5, -11.95, 3.75), target=(19.6, -10.65, 2.15), lens=21.0, fstop=2.8)
BED_PUSH = 0.0035
BED_SEED = 31
CHILD_TURN = math.radians(35.0)     # the child's head turned toward Steve's pillow (about the body's long axis)

# beat 17 (the story's fallback, from outside): low behind his right shoulder, below his eyes, looking up: the
# starry sky over the roof, his head beside the lit pane, a slow push in (ease_out: at speed on the first frame)
WINDOW_CAM = dict(pos=(4.8, -12.6, 1.1), target=(10.0, -10.6, 2.7), lens=30.0, fstop=2.0,
                  pos1=(5.3, -12.42, 1.2), target1=(10.0, -10.6, 2.7))
WINDOW_EASE = "linear"   # the push at one speed to the cut: with ease_out it came to a full stop, and 1088-1100 changed
#                          by only 0.08-0.22 grey levels a frame (the whole-film preview): a paused picture before dn18


def _beds(C):
    """(Steve's red bed, the child's bed): anchor points and the yaw a sleeper needs (Character.lie_down)."""
    A, Y = C.A, C.v.yaws
    return (A[HC.RED_BED], Y[HC.RED_BED]), (A[HC.CHILD_BED], Y[HC.CHILD_BED])


def _bed_cam(C, s, focus):
    """BED_CAM on shot s with its linear push (the same speed in every shot that uses it)."""
    p0, t0 = Vector(BED_CAM["pos"]), Vector(BED_CAM["target"])
    d = (t0 - p0).normalized() * (BED_PUSH * (s.frame_end + 1 - s.frame_start))
    return C.cam(s, "bed", focus=focus, handheld=0.003, seed=BED_SEED, ease="linear", lens=BED_CAM["lens"],
                 fstop=BED_CAM["fstop"], pos=tuple(p0), target=tuple(t0), pos1=tuple(p0 + d), target1=tuple(t0 + d))


def _turn_head(c, f0, f1, angle):
    """A lying character's head turned about the body's long axis to `angle` (radians) from f0 to f1 (f1 <= f0:
    already turned on f0). Character.look_at aims with the STANDING yaw, which means nothing for a sleeper."""
    characters._ease(c.head, "rotation_euler", 2, f0, f1, angle)


def in03_bed(st, s, C, nar):
    """BEAT 3  "When he slept, the night just ended."   frames 145-210 (66 f, 2.75 s): sky night on 145-181, GOLD
    from 182 (the word "ended") to 210 (29 frames). Words: When 147, he 149, slept 152, the 165, night 168,
    just 176, ended 182. The pause after it is 0.8 s: the morning is seen.

    STORY: Inside the house, locked off from beside the foot of the nearer bed, looking across both beds to the
    side wall, whose two-pane window sits just behind the far bed. Steve lies in the red bed in the foreground, the
    baby villager in the far bed with its head turned toward him and the lens. The window is moonlit blue with
    stars. On the word ended the window and the light in the room snap to golden morning inside the same frame.
    Neither of them has moved. About 3 seconds.
    Cast: Steve, baby villager (narrator). Effects: red hero bed in the foreground and the white bed beyond, Steve
    and the child in the lying pose, one camera rendered under the night sky and the golden sky, hard cut between
    them on a word boundary, wall torch scaled down so the window carries the change.

    WHAT IT NOW DOES (BED_CAM, module docstring): from the west end of the bed wing, high, looking east down both
    beds: Steve in iron (chestplate, leggings, boots, no helmet, empty hands) asleep on the red bed at the right,
    nearer; the child in its white bed at the left; the wall torch between the pillows; above it the gable pane,
    the room's window to the sky. A slow linear dolly in (0.0035 block a frame, 0.23 block over the shot) and a
    tiny handheld: moving on frame 145.
      145 .. 149      both lie still, the child's face up (only its brow and eyes reach the lens)
      "slept" 152     the child turns its head 35 degrees toward him (150 .. 162, about the body's long axis): its
                      face comes round to him and to the lens and stays there to the end of the shot
      145 .. 181      night: purple sky with stars in the pane, the torch-lit cobblestone wall, warm floor
      "ended" 182     the SAME frame in gold (the film's st.sky_change): blue sky and white clouds in the pane, the
                      torches down to 0.35 (C.lights "gold_room", at=182, same near / radius) and C.morning on: the
                      whole room brighter (whole frame x1.77, pane x1.85, floor x1.93, walls x1.56, the child's bed
                      x1.48, the red bed x1.26). Nobody moves: the push and the handheld go on through the change.
    WHY IRON: the brief has him in iron in beats 1 to 5 and a player sleeps in his armor; with this camera his face
      reads on the pillow (64 px, eyes y 55 %), and the plain teal shirt stays the watcher's sign (beats 7 onward).
      The sword is taken out of his hand for the night (Player.hold(None)).
    SHARED: BED_CAM is the bed camera of in16_empty too (same constant, same push speed, same handheld seed); the
      night light ("night_room", near house_a_center, radius 14) is in16's. HC.RED_BED / HC.CHILD_BED.
      Cast: C.actor("steve_iron", "in"), C.actor("child", "in"). Player.sleep = Character.lie_down.
    NEIGHBOURS: before, dn02_fight (the door at night); after, dg04_hello (the doorstep in golden morning: he is up
      and crouches at the child). Hard cuts.
    RISK (story): the hard change from night to gold inside one frame can read as a glitch: the camera keeps moving
      through it and nobody moves, so only the light changes; the "four-frame dissolve" is not available (one sky
      per frame).
    MEASURED: hello_geo at 146: child's head x 19-34 %, y 50-58 %, face 58 px; Steve's head x 62-75 %, y 52-61 %,
      face 64 px; at 210: 17-35 % / 63-77 %, 61 / 67 px. palette_check in03@160 (night): stone G/R 0.98, planks
      s 0.48, heroes steve and child 100 % inside the safe area; in03@195 (gold): stone G/R 0.94, planks s 0.54, robe
      hue 18, heroes 100 % inside. (The shirt check of the plan's night still is not made any more: the chestplate
      covers the shirt.) Stills: out/test/hello_in_final_in03_bed_175_zones.png (night, after the head turn),
      hello_in_final_in03_bed_195_zones.png (gold), hello_in_t5_in03_bed_181.png (the last night frame).
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_iron", "in")
    steve.hold(None)                                      # asleep with an empty hand (no sword in bed)
    kid = C.actor("child", "in")
    (red, red_yaw), (mine, my_yaw) = _beds(C)
    steve.sleep(f0, red, red_yaw)
    kid.lie_down(f0, mine, my_yaw)
    a = C.at(s, "slept")
    _turn_head(kid, a - 2, a + 10, CHILD_TURN)            # on "slept" the child turns its head to him
    st.use(s, steve, kid)
    _bed_cam(C, s, focus=steve.head)
    st.hero(s, "steve", steve)
    st.hero(s, "child", kid)
    room = dict(near=C.A["house_a_center"], radius=14.0)
    C.lights(s, "night_room", **room)
    change = C.T[s.name].change
    C.lights(s, "gold_room", at=change, **room)          # the torches nearly out from "ended" ...
    C.morning(s, change)                                  # ... and the morning light in through the north window


def in16_empty(st, s, C, nar):
    """BEAT 16  "He doesn't sleep anymore."   frames 998-1046 (49 f, 2.04 s), sky night.
    Words: He 1000, doesn't 1002, sleep 1010, anymore 1020. The pause after it is 0.7 s.

    STORY: Night inside the house, the exact camera of beat 3. The red bed in the foreground is empty. Beyond it the
    baby villager lies in its own bed with its head turned toward the empty one. The window behind stays moonlit
    blue. Locked off, nothing moves. About 2.2 seconds.
    Cast: baby villager (narrator). Effects: red hero bed, empty; same camera as beat 3, night only; moonlit window
    that does not change.

    WHAT IT NOW DOES: BED_CAM exactly as in03 (the same start, the same linear push speed and handheld seed: these
    49 frames are in03's first 49), the same night light. The red bed at the right is EMPTY and made; the child
    lies in its bed at the left with its head already turned 35 degrees to the empty pillow (and so to the lens) from
    the first frame, held to the last: in03's pose after "slept", without him. The pane above the torch shows the
    purple night sky with stars for the whole shot. Moving on frame 998: the push and the handheld.
    SHARED: BED_CAM, the night light of in03 ("night_room", near house_a_center, radius 14), CHILD_TURN.
      Cast: C.actor("child", "in") (placed again on 998: lie_down is a cut).
    MEASURED: hello_geo at 998: the child's head x 18-36 %, y 49-59 %, face 58 px; at 1046: 17-36 %, 61 px.
      palette_check in16@1020: stone G/R 0.97, planks s 0.49, hero child 100 % inside the safe area.
      Still: out/test/hello_in_final_in16_empty_1020_zones.png.
    NEIGHBOURS: before, dg15_c (late gold at the door: he is at the corner of the house); after, in17_window (the same
      night, the child at the window). Hard cuts.
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "in")
    _red, (mine, my_yaw) = _beds(C)
    kid.lie_down(f0, mine, my_yaw)
    _turn_head(kid, f0, f0, CHILD_TURN)                  # already turned to the empty pillow
    st.use(s, kid)
    _bed_cam(C, s, focus=kid.head)
    st.hero(s, "child", kid)
    C.lights(s, "night_room", near=C.A["house_a_center"], radius=14.0)


def in17_window(st, s, C, nar):
    """BEAT 17  "The nights last all night."   frames 1047-1100 (54 f, 2.25 s), sky night.
    Words: The 1049, nights 1051, last 1059, all 1068, night 1073. The pause after it is 0.9 s.

    STORY: The same room, the other end. The baby villager stands on the chair beside the table under the west
    window, the one window that faces the plaza, its big nose in profile close to the pane. Through the glass, small
    on the moonlit plaza, he stands facing the house. Very slow push toward the window. About 2.5 seconds.
    Cast: baby villager (narrator), the watcher (through the window, a dark shape eight blocks out). Effects: child
    standing on the oak stairs chair, single glass pane, moonlit plaza outside, slow push in.
    RISK (story) AND ITS FALLBACK, WHICH THIS SHOT USES: "the plaza is seen through a single glass pane past the
    child's big head. Fallback: shoot from outside instead, over his dark shoulder toward the house, with the
    child's face in the torch-lit window pane."
    WHY THE FALLBACK (measured): the pane's sill is 2 blocks above the plaza; from any camera inside at the child's
    height a standing figure out on the plaza is wholly below the sill line (rays to his knees, chest and eyes hit
    the wall or the table: out/test/hello_scout_night_in17_window_1075.png showed no figure). From outside the
    picture also keeps his progression: the corner (15c), under the window (17), beside the door (19).

    WHAT IT NOW DOES (WINDOW_CAM): low on the plaza behind his right shoulder, below his eyes (z 1.1), 30 mm f/2.0,
    looking up at the house front: the starry night sky over the roof fills the top third; the
    lit pane below the eaves with the CHILD'S WHOLE FACE in it (brow, eyes, nose, crossed arms below), looking out
    and down at him; his head (from behind, tipped up at the pane: Player.watch from the first frame) beside the
    pane at the same height, his teal shoulder and arm big and soft in the lower left; his body dead still. A slow
    LINEAR push in (WINDOW_EASE, 0.54 block over the shot, 0.01 block a frame to the cut) with the handheld on top
    (0.004). Nothing else moves: the two of them look at each other through "nights" 1051 .. "night" 1073 and the
    0.9 s after it. Since the review of the whole-film preview the push is linear: with ease_out it came to a full
    stop and 1088-1100 changed by 0.08-0.22 grey levels a frame, a paused picture before the cut (now 0.43-0.45 on
    the preview, 1047-1060 0.45; the first and last frames are the same as before).
    THE CHILD STANDS ON THE CHAIR'S BACK (KID_WINDOW (11.75, -10.15, 2.0), the high east half of the oak stairs,
      top z 2.0; PLACES "window_chair" since the lead's pass), not on its seat: on the seat (11.25, -10.5, 1.5) its
      eyes are at z 2.16 (the first PLACES comment said 2.3), 0.16 above the sill, and from any camera outside only
      the eyes and the top of the nose showed (the plan's still). On the back its eyes are at z 2.66, in the middle
      of the pane. It stands at the north side of the chair so that the camera, south-west of the pane, sees it
      centred in the opening.
    WHY LOW: the night reads at once (stars over the roof; since the lead's pass the moon is behind the house and the
      front is in its shadow: the lit pane and the child's face are the brightest warm patch), he stands under
      the window as a figure (head, shoulder, arm), and the lens sees his head from behind and below: his face is
      never seen (153-157 degrees off the lens).
    SHARED: PLACES "watch_window" (7.3, -10.95), unchanged, facing the pane; the night light of the room
      ("night_room": the torch-lit room seen through the pane). WINDOW_CAM is this shot's own camera
      (C.cam(s, None, **WINDOW_CAM); the stub CAMS "window_out" is gone). Cast: C.actor("child", "in") (in in16
      before: placed again on 1047: lie_down / place are cuts), C.actor("watcher", "in") via C.watcher.
      Film-local light PANE_FILL ("in_pane", 260 W, torch colour) in the room between the glass and the child's
      face: without it the face is a dark brown shape; at 120 W it was a muddy mauve no brighter than the logs
      around the pane (face rgb 75,59,65 against 66,55,57); at 260 W it is
      about 1.3x the logs (face rgb 99,76,75 against 74,61,59 and 78,65,60 at 1065) and the green eyes read.
    MEASURED (hello_geo; its face column measured every face as an adult's until the lead's pass: the child's face
      sizes here are twice its true 27-29 px): at 1047 the child's eyes x 54 %, y 56 %, head x 48-60 %, y 52-58 %,
      face 53 px, 9 degrees off the lens; his head x -1..32 %, y 51-66 %, 157 degrees off; at 1100: child head x 48-60
      %, y 52-59 %, face 57 px; his head x -14..28 %, y 50-69 % (the caption band crosses his head and the wall: a big
      soft foreground shape). palette_check in17@1065 (PANE_FILL 260 W): stone G/R 1.01, planks s 0.32, the child's
      skin s 0.32, Steve shirt hue 189, his trousers min channel 37, hero child x 49-59 %, y 53-58 %, 100 % inside the
      safe area; in17@1100: G/R 1.02, planks s 0.33, skin s 0.33, shirt hue 189, trousers 36, hero child 100 % inside.
      Still: out/test/hello_in_final_in17_window_1065_zones.png. UNDER THE LEAD'S MOON (north-east, behind the house):
      palette_check in17@1065 stone G/R 1.00, planks s 0.20, the child's skin rgb(115,83,78) s 0.32, shirt hue 191,
      trousers min channel 13 (limit 12: his legs are in the moon's shadow), hero child 100 % inside; whole frame luma
      59 (was 79). Still: out/test/hello_lead_in17_window_1065_zones.png. WITH THE LINEAR PUSH (review pass):
      out/test/hello_review_fix_in17_window_1100_zones.png; hello_palette in17@1065: trousers min channel 13, shirt
      hue 190, G/R 1.00, hero child 100 % inside; in17@1100: trousers min channel 12 (AT the limit 12: his legs in
      the moon's shadow), shirt hue 191, skin s 0.32, hero child x 49-59 %, y 53-58 %, 100 % inside: all pass.
    NEIGHBOURS: before, in16_empty; after, dn18_knock (outside: the zombie at the door, the same night). Hard cuts.
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "in")
    him = C.watcher(s, "in", place="watch_window", yaw=HC.yaw_to(HC.PLACES["watch_window"], HC.PLACES["window"]))
    C.put(kid, f0, KID_WINDOW, toward=(KID_WINDOW[0] - 1.0, KID_WINDOW[1]))
    kid.look_at(f0, him, ease=0)                          # out through the pane at him (and so nearly at the lens)
    him.watch(f0, f1, kid)                                # his head up at the pane from the first frame; body still
    st.use(s, kid)
    # the child's face is turned away from the room's torch (11, -8, 3): a small warm film-local light inside the
    # pane, in front of its face, stands in for the torch light the game would show on it (shadowless, invisible)
    C.fill("in_pane", PANE_FILL["pos"], PANE_FILL["watts"], [s], color=PANE_FILL["color"])
    C.cam(s, None, focus=kid.head, handheld=0.004, ease=WINDOW_EASE, **WINDOW_CAM)
    st.hero(s, "child", kid)
    C.lights(s, "night_room", near=C.A["house_a_center"], radius=14.0)
