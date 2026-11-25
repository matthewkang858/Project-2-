"""The Hello, sequence INTERIOR: the child's house (house_a) at night. Beats 3, 16, 17 (shots in03_bed, in16_empty,
in17_window); sky "night", and beat 3 turns "gold" inside the shot ON the word "ended". Beat 17 is filmed from
OUTSIDE, through the window (the story's own fallback, see in17_window). One function per shot; the contract is in
films/hello_common.py (tags "in...", C.actor, C.cam, C.lights, C.fill, st.use / st.hero).

THE ROOM (hello_common's docstring has it block by block): the bed wing x 15..20, y -14..-8; the beds along the
  east wall, pillows east: Steve's RED bed is the SOUTH one, HC.RED_BED = "house_a_bed_1" (anchor (19.0, -11.5,
  1.56)), the child's white bed the NORTH one, HC.CHILD_BED = "house_a_bed_2" (19.0, -9.5, 1.56); the two-pane
  window of the north wall (17..18, -8, 2) is right behind the child's bed; a wall torch between the pillows
  (19, -11, 2); ONE night stand, at (19, -9) beside the child's bed (the film takes the other one out: it hid
  Steve's head from every lens along the south wall). The west wing: the one pane facing the plaza at (10, -11, 2);
  the film moves house_a's chair RIGHT UNDER it (oak stairs facing east at (11, -11): the seat is its west half, z
  1.5; PLACES "window_chair") and the table beside it at (11, -10) (hello_common._edit).
THE CAMERA of beats 3 and 16: CAMS["bed"] is the start, and both shots are yours: keep them IDENTICAL to each other
  (if you change it, write one constant in this file and use it in both). Now: from outside the south wall of the
  bed wing (st.see_through(s, "house_a_south"): invisible to the camera only, it still keeps the light out), 2.5
  blocks south of it, 32 mm, across Steve's bed in front to the child's bed and the north window.
  MEASURED (projection, out/test/hello_scout_night_in03_bed_160_zones.png): the child's head x 50-63 %, y 46-54 %;
  Steve's head x 62-80 %, y 49-59 % (nothing between: ray cast); the north window x 12-31 %; the wall torch between
  the pillows above them. palette_check in03@160 and in16@1020: heroes 100 % inside the safe area, stone, planks,
  skin and Steve's trousers pass; ONE FAIL at night: Steve's shirt hue 213 (26, 35, 47; 170-196 wanted): the cool
  night grade on a dark teal. A warm shadowless light over the beds (200 W) did not move it and made the night
  brighter, so it was taken out: try lighting his torso from the torch's side, or accept and say so.
  The window shows, at night, the dark village north of the house with the lit block of the lamp post at (16, -3)
  (an orange square in the right pane); in gold, daylit houses. No sky with stars is reachable from a camera that
  holds both heads (every line through the panes ends on a block: tools.hello_geo --through).
THE SKIES: "night" (moon in the west, azimuth 176, elevation 21) and, from the word "ended" in beat 3, "gold"
  (sun azimuth 215, elevation 24). The film calls st.sky_change; the shot keys the light on both sides:
  C.lights(s, "night_room", **room) and, from the change, C.lights(s, "gold_room", at=change, **room) (the SAME
  near / radius: Stage.lights at= sets every light again) + C.morning(s, change) (hello_common.MORNING: a warm
  shadowless 1300 W light inside the north window, behind the child's bed).
  MEASURED at the snap (mean luminance, the same camera, 160 night against 195 gold): window 79 -> 132 (x1.7),
  walls 113 -> 186 (x1.65), floor 46 -> 96 (x2.1), beds 58 -> 77 (x1.33: their sides face the camera, away from the
  window), whole frame 44 -> 112. The first plan (torches 1.3 -> 0.7, nothing else) made the room DARKER (x0.8).
  palette_check in03@195: every check passes (stone G/R 0.94).
LIGHT: house_a's torches and its room fill are one group ("house_a"): raise them only together (LIGHTS
  "night_room"); lit cobblestone and villager skin are at the palette limit in there (CONTRACT.md). Film-local
  lights: C.fill("in_<name>", ...) (the name must start with "in").
"""
import math

from mathutils import Vector

from engine import characters
from films import hello_common as HC

PANE_FILL = dict(pos=(11.05, -10.85, 2.95), watts=120.0, color=(1.0, 0.88, 0.72))    # in17: on the child's face
# beat 17: the child stands on the HIGH back half of the chair under the pane (oak stairs facing east: x 11.5..12,
# top z 2.0), toward the north side of the chair, so the camera from the south-west sees it centred in the pane. On the
# seat (PLACES "window_chair", z 1.5) its eyes are at z 2.16, 0.16 above the sill: only the eyes showed.
KID_WINDOW = (11.75, -10.25, 2.0)

# THE BED CAMERA of beats 3 and 16 (one constant, both shots): inside the room, high at the west end of the bed
# wing, a little toward Steve's side, looking east down the two beds to their pillows: the red bed and Steve at the
# right and nearer, the child's white bed at the left, the wall torch between the pillows, and the east gable's
# glass pane above it, through which the camera sees SKY (night: stars; from "ended": day). A slow linear dolly in
# (BED_PUSH blocks a frame, the same speed in both shots, so in16 is the first 49 frames of in03's path).
BED_CAM = dict(pos=(15.5, -11.95, 3.75), target=(19.6, -10.65, 2.15), lens=21.0, fstop=2.8)
BED_PUSH = 0.0035
BED_SEED = 31
CHILD_TURN = math.radians(35.0)     # the child's head turned toward Steve's pillow (about the body's long axis)

# beat 17 (the story's fallback, from outside): low behind his right shoulder, under the starry sky, a slow push
# that rises toward the pane so the child's face comes up over the sill
WINDOW_CAM = dict(pos=(5.0, -12.4, 1.75), target=(10.0, -10.6, 2.6), lens=28.0, fstop=2.0,
                  pos1=(5.55, -12.2, 1.85), target1=(10.0, -10.55, 2.6))


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

    MUST BE SEEN, ON WHICH WORD
      145 .. 181      night: the window dark blue with stars, the room lit by its torches; both asleep, locked off
                      (only the handheld lives, tiny)
      "ended" 182     the SAME frame in gold: the window bright, morning light in the room; nobody moves. The
                      change is the film's (st.sky_change); the torches step with it (C.lights(..., at=change)) and
                      C.morning(s, change) switches the morning light on: the room must get BRIGHTER (measured x1.65
                      on the walls, x2.1 on the floor: the module docstring)
    SHARED: the bed camera identical to in16_empty's (CAMS["bed"] or your own constant used in both); the light of
      the night part identical to in16_empty's. HC.RED_BED / HC.CHILD_BED. Cast: Steve asleep =
      C.actor("steve_bed", "in") (plain Steve, no armor, empty hands: see SCOUTED), C.actor("child", "in").
      Player.sleep = Character.lie_down(frame, bed anchor, yaw): see _beds().
    NEIGHBOURS: before, dn02_fight (the door at night); after, dg04_hello (the doorstep in golden morning: he is up
      and crouches at the child). Hard cuts.
    RISKS (story): a hard cut from night to gold inside one frame can read as a glitch, and the join sits inside a
      sentence: keep the beds and the window large and locked so only the light changes; the join is exactly on the
      first frame of "ended" (done). The "four-frame dissolve with the window going first" is NOT available (the
      sky is per frame; a dissolve would need both skies in one frame). If the side window is too small from this
      camera, the story's fallback is the bed camera between the pillows looking down the room to the west window.
      The room's change is now carried by the light (C.morning + the torches at 0.35), not only by the window; the
      beds themselves gain least (x1.33): a second warm light from the south (the side the camera is on) would
      lift their faces, if you want more. The child's head turned toward Steve while lying: Character.look_at on a
      lying figure turns the head about the body's long axis (check the sign on a still).
    SCOUTED (out/test/hello_scout_night_in03_bed_160_zones.png, hello_scout_gold_in03_bed_195_zones.png): the
      story's composition (the red bed and Steve in front, the child's head on the far pillow, the window behind,
      the torch between the pillows); at "ended" the window, the walls and the floor brighten (numbers in the module
      docstring). Steve's head and the child's head touch in the picture (Steve's x 62-80 %, the child's x 50-63 %,
      both y 46-59 %): turn the child's head toward him and the lens and check that its face stays clear.
      Plain Steve skin (no armor) on purpose: the brief asks for iron in beats 1 to 5 and a player sleeps in his
      armor, but in iron he lay on the bed as one grey block (out/test/hello_scout_bedlow_in03_bed_160_v0.png). The
      cost: in this shot he wears the look the watcher wears later. If you put the iron back (C.actor("steve_iron",
      "in") with lie_down), his face must read on the pillow toward the lens; then say so in your result.
    STUB: both asleep, CAMS "bed", the night torches; from the change the gold levels and C.morning.
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

    MUST BE SEEN, ON WHICH WORD
      the whole shot  the frame of in03's night part, the red bed EMPTY in front, the child awake in its bed, head
                      turned toward the empty bed (and so toward the lens); locked off, only a tiny handheld
    SHARED: CAMS["bed"] and the same light as in03's night part (C.lights "night_room", same near / radius), so the
      two frames match but for Steve. Cast: C.actor("child", "in").
    MEASURED (stub): the child's head x 50-63 %, y 46-54 %; palette_check in16@1020 passes every check
      (out/test/hello_scout_night_in16_empty_1020_zones.png: the empty red bed in front reads at once).
    NEIGHBOURS: before, dg15_c (late gold at the door: he is at the corner of the house); after, in17_window (the same
      night, the child at the window). Hard cuts.
    CUT PRIORITY (story): the second cut would drop this line and play "The nights last all night" over beat 3's
      camera; not needed (the film is 64.3 s).
    STUB: the child in its bed, CAMS "bed", the night torches.
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

    MUST BE SEEN, ON WHICH WORD
      frame 1047      the push already moving (C.cam's ease_out: at speed on the first frame)
      "nights" 1051 .. "night" 1073   the child's face in the pane, looking out at him; his dark head and shoulder
                      in the left foreground, from behind (never his face), soft
    SHARED: PLACES "window_chair" (the child on the seat right under the pane, eyes z 2.3), "window", "watch_window"
      (7.3, -10.95): him 2.7 blocks out, facing the pane. CAMS "window_out" (a start: 58 mm from (3.4, -12.5, 2.5)
      over his right shoulder, a slow push). Cast: C.actor("child", "in") (in in16 before: place it on f0),
      C.actor("watcher", "in").
    MEASURED (stub, out/test/hello_scout_night_in17_window_1060_zones.png): the child's eyes x 52 %, y 51 % in the
      pane (it looks out at him, 8 degrees off the lens; its nose meets the sill: a camera a little higher shows
      it); his head x -5..34 %, y 67-90 % (the caption sits on it: a big soft foreground shape, allowed). The
      child's face is lit by PANE_FILL ("in_pane", 120 W, torch colour, inside the room above-left of it): without
      it the face was a dark brown shape. palette_check in17@1060 passes (hero child 100 % inside the safe area).
    NEIGHBOURS: before, in16_empty; after, dn18_knock (outside: the zombie at the door, the same night). Hard cuts.
    STUB: the child on the chair looking out at him, him on watch_window facing the pane, CAMS "window_out".
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "in")
    him = C.watcher(s, "in", place="watch_window", yaw=HC.yaw_to(HC.PLACES["watch_window"], HC.PLACES["window"]))
    C.put(kid, f0, KID_WINDOW, toward=(KID_WINDOW[0] - 1.0, KID_WINDOW[1]))
    kid.look_at(f0, him, ease=0)                          # out through the pane at him (and so nearly at the lens)
    st.use(s, kid)
    # the child's face is turned away from the room's torch (11, -8, 3): a small warm film-local light inside the
    # pane, in front of its face, stands in for the torch light the game would show on it (shadowless, invisible)
    C.fill("in_pane", PANE_FILL["pos"], PANE_FILL["watts"], [s], color=PANE_FILL["color"])
    C.cam(s, "window_out", focus=kid.head, handheld=0.004, **WINDOW_CAM)
    st.hero(s, "child", kid)
    C.lights(s, "night_room", near=C.A["house_a_center"], radius=14.0)
