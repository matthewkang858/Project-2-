"""The Hello, sequence INTERIOR: inside the child's house (house_a) at night. Beats 3, 16, 17 (shots in03_bed,
in16_empty, in17_window); sky "night", and beat 3 turns "gold" inside the shot ON the word "ended". One function
per shot; the contract is in films/hello_common.py (tags "in...", C.actor, C.cam, C.lights, st.use / st.hero).

THE ROOM (hello_common's docstring has it block by block): the bed wing x 15..20, y -14..-8; the beds along the
  east wall, pillows east: Steve's RED bed is the SOUTH one, HC.RED_BED = "house_a_bed_1" (anchor (19.0, -11.5,
  1.56)), the child's white bed the NORTH one, HC.CHILD_BED = "house_a_bed_2" (19.0, -9.5, 1.56); the two-pane
  window of the north wall (17..18, -8, 2) is right behind the child's bed; a wall torch between the pillows
  (19, -11, 2). The west wing: the one pane facing the plaza at (10, -11, 2) with the table under it (11, -11)
  and an oak-stairs chair north of it at (11, -10) (seat z 1.5, PLACES "window_chair").
THE CAMERA of beats 3 and 16 is CAMS["bed"], exactly, in both: from just outside the south wall of the bed wing
  (st.see_through(s, "house_a_south"): the wall is invisible to the camera only and still keeps the light out),
  24 mm, across Steve's bed in front to the child's bed and the north window behind it.
THE SKIES: "night" (moon in the west, azimuth 176, elevation 21: the north window shows the night sky with stars)
  and, from the word "ended" in beat 3, "gold" (sun azimuth 215, elevation 24, in the south-west: it comes in
  through the south windows). The film calls st.sky_change; the shot keys the torch levels on both sides:
  C.lights(s, "night_room", ...) and C.lights(s, "gold_room", ..., at=C.T[s.name].change) with the SAME near /
  radius (Stage.lights at= sets every light again).
LIGHT: house_a's torches and its room fill are one group ("house_a"): raise them only together (LIGHTS
  "night_room"); lit cobblestone and villager skin are at the palette limit in there (CONTRACT.md).
"""
from films import hello_common as HC


def _beds(C):
    """(Steve's red bed, the child's bed): anchor points and the yaw a sleeper needs (Character.lie_down)."""
    A, Y = C.A, C.v.yaws
    return (A[HC.RED_BED], Y[HC.RED_BED]), (A[HC.CHILD_BED], Y[HC.CHILD_BED])


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
      "ended" 182     the SAME frame in gold: the window bright, sunlight in the room; nobody moves. The change is
                      the film's (st.sky_change); the torches step with it (C.lights(..., at=change))
    SHARED: CAMS["bed"] exactly as in16_empty. HC.RED_BED / HC.CHILD_BED. Cast: Steve asleep = C.actor("steve_bed",
      "in") (plain Steve, no armor, empty hands: in iron armor he was a grey block on the bed, as scouted), C.actor("child", "in").
      Player.sleep = Character.lie_down(frame, bed anchor, yaw): see _beds().
    NEIGHBOURS: before, dn02_fight (the door at night); after, dg04_hello (the doorstep in golden morning: he is up
      and crouches at the child). Hard cuts.
    RISKS (story): a hard cut from night to gold inside one frame can read as a glitch, and the join sits inside a
      sentence: keep the beds and the window large and locked so only the light changes; the join is exactly on the
      first frame of "ended" (done). The "four-frame dissolve with the window going first" is NOT available (the
      sky is per frame; a dissolve would need both skies in one frame). If the side window is too small from this
      camera, the story's fallback is the bed camera between the pillows looking down the room to the west window.
      THE ROOM HARDLY CHANGES AT THE SNAP (scouted: hello_scout_night_in03_bed_160.png against
      hello_scout_gold_in03_bed_195.png: the window goes from dark to bright daylight, the room a touch lighter):
      add a warm film-local light keyed on from the change, C.fill("morning", pos, W, [(change, s.frame_end)],
      color=...), e.g. a patch of "sun" from the south window over the beds, and/or lower the torches harder at
      the change. The child's head turned toward Steve while lying: Character.look_at on a lying figure turns the head about the
      body's long axis (check the sign on a still); "Steve lying in the bed ... test one still first".
    SCOUTED (out/test/hello_scout_night_in03_bed_160.png, hello_scout_gold_in03_bed_195.png): the composition is the
      story's (red bed and Steve in front, the child's head on the far pillow, the two-pane window right behind it,
      the torch on the east wall at the right); plain Steve reads at once (in iron armor he was a grey block). Open:
      through the north window the camera sees the lit block of the lamp post at (16, -3) five blocks away, an
      orange square, not "moonlit blue with stars": a lower camera (z 2.0) shows more sky in the panes
      (hello_scout_bedlow_in03_bed_160_v0.png) but Steve then hides the child; or move the camera a little in x so
      the lamp block leaves the panes. The child's head is not yet turned to him (Character.look_at on a lying
      figure: check the sign).
    STUB: both asleep, CAMS "bed", the night torches, then the gold levels from the change.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_bed", "in")
    kid = C.actor("child", "in")
    (red, red_yaw), (mine, my_yaw) = _beds(C)
    steve.sleep(f0, red, red_yaw)
    kid.lie_down(f0, mine, my_yaw)
    st.see_through(s, "house_a_south")
    st.use(s, steve, kid)
    C.cam(s, "bed", focus=kid.head, handheld=0.003)
    st.hero(s, "steve", steve)
    st.hero(s, "child", kid)
    room = dict(near=C.A["house_a_center"], radius=14.0)
    C.lights(s, "night_room", **room)
    C.lights(s, "gold_room", at=C.T[s.name].change, **room)


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
    NEIGHBOURS: before, dg15_c (late gold at the door: he is at the corner of the house); after, in17_window (the same
      night, the child at the window). Hard cuts.
    CUT PRIORITY (story): the second cut would drop this line and play "The nights last all night" over beat 3's
      camera; not needed (the film is 63.8 s).
    STUB: the child in its bed, CAMS "bed", the night torches.
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "in")
    _red, (mine, my_yaw) = _beds(C)
    kid.lie_down(f0, mine, my_yaw)
    st.see_through(s, "house_a_south")
    st.use(s, kid)
    C.cam(s, "bed", focus=kid.head, handheld=0.003)
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

    MUST BE SEEN, ON WHICH WORD
      frame 1047      the push already moving; the child on the chair, nose in profile toward the pane
      "nights" 1051 .. "night" 1073   through the pane, him standing on the plaza facing the house, small, dark,
                      out of focus: a figure, never a face
    SHARED: PLACES "window_chair", "window", "watch_plaza" (his place outside), CAMS "window" (a start). Cast:
      C.actor("child", "in") (in the shot before: place it on f0), C.actor("watcher", "in").
    NEIGHBOURS: before, in16_empty; after, dn18_knock (outside: the zombie at the door, the same night). Hard cuts.
    RISKS (story): the plaza is seen through a single glass pane past the child's big head. Fallback: shoot from
      outside instead, over his dark shoulder toward the house, with the child's face in the torch-lit window
      pane. The chair stands NORTH of the table, the pane above the table: the child looks out diagonally (it is a
      block from the pane, not at it).
    SCOUTED (out/test/hello_scout_night_in17_window_1075.png): from the room's south-east the child on the chair is
      at the right, the pane at the left with the lit plaza beyond; the child shows the side of its head, not its
      nose (cheat its look toward the lens, C.to_lens), and he is too small to find through the pane: frame him.
    STUB: the child on the chair facing the pane, him on the plaza facing the house, CAMS "window".
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "in")
    him = C.watcher(s, "in", place="watch_plaza", yaw=HC.yaw_to(HC.PLACES["watch_plaza"], (10.0, -10.6)))
    C.put(kid, f0, "window_chair", toward=(10.3, -10.8))
    kid.look_at(f0, C.P("watch_plaza")[:2] + (1.6,), ease=0)
    st.use(s, kid)
    C.cam(s, "window", focus=kid.head, handheld=0.004)
    st.hero(s, "child", kid)
    C.lights(s, "night_room", near=C.A["house_a_center"], radius=14.0)
