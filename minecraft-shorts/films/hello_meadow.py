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
  "dawn" (me07, me08: "He came back at sunrise"): the same, the sun low behind the wood (azimuth 75, elevation 9),
  no haze: the glow sits on the tree line, the road is in soft shade, the wall stays black. After the dip it is
  plainly another light than beat 6's afternoon (out/test/hello_scout_dawn_me07_return_470.png against
  hello_scout_meadow_me07_return_470.png; hello_scout_dawn_me08_nohello_520.png). The story's risk "if it still
  feels like the same afternoon" is answered by the sky, since its night insert cannot be had (fixed cuts).
TAGS TAKEN (twins): child_me (me06, me07, me12, me13), child_me2 (me08: pre-rolled from frame 473, i.e. INSIDE
  me07: never use it in me07), child_me3 (me14: pre-rolled), watcher_me (me07, me08, me13), steve_diamond_me (me06).
  A new twin: the next free tag, me4, me5 ...
THE WATCHER (beats 7, 8, 13): C.actor("watcher", "me") = plain Steve, dead still; never his face (beat 7: 30 px tall
  at the gap with the 22 mm gate lens, face unreadable but his eye whites are two pale dots: keep him soft).
LIGHT: C.lights(s, "gold", near=<point>, radius=12) (daylight; the village's torches are far away: keep them off).
"""
from films import hello_common as HC


def _road(C, y0, y1):
    """The points of road_to_forest between y0 and y1 (on the ground: the path follows the terrain)."""
    pts = [p for p in C.v.paths["road_to_forest"] if y0 <= p[1] <= y1]
    return pts


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
      (keep it tiny: 0.004). PLACES "gate_child" (the child's block in both shots). Cast: C.actor("steve_diamond",
      "me"), C.actor("child", "me").
    NEIGHBOURS: before, dg05_nod (the doorstep, the child runs off); after, me07_return: the same frame after a dip
      to black (the night that passed).
    RISKS (story): "He came back at sunrise without it": at distance diamond armor and the teal shirt are both in
      the cyan family: keep Steve near enough while the armor must read (he walks 4.3 blocks a second). The glint:
      players.equip(enchanted=True) is on (C.actor did it, and the stamp work-around).
    SCOUTED (out/test/hello_scout_meadow_me06_leave_340.png, _410.png): the wall is black across the frame, Steve
      in diamond is big enough for the armor at 340 and small and bright against the trunks at 410, before the
      tree line. The child on "gate_child" is dead centre and seen from BEHIND (a brown box on a pink box): turn
      it to a three-quarter profile (body toward the meadow, look cheated toward the lens) and/or move it off the
      road's axis so he walks past it.
    MEASURED (stub, tools.hello_geo, projection and ray casts): the child's eyes x 31 %, y 56 %, 168 degrees off
      the lens (from BEHIND); Steve's head 19 px wide on "armor" (356), 12 px at 410: small; the armor reads by its
      colour and the glint more than its shape.
    STUB: Steve walks the road from about y 31 to y 50 in the shot; the child on "gate_child" facing up the road.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_diamond", "me")
    kid = C.actor("child", "me")
    road = _road(C, 24.0, 53.0)
    steve.place(f0 - 40, road[0], HC.yaw_to(road[0], road[1]))
    steve.walk(f0 - 40, road, ramp=(True, False))
    C.put(kid, f0, "gate_child", toward=(-1.6, 34.0))
    kid.look_at(f0, steve, ease=0)
    kid.track(f0 + 2, f1, steve, step=6)
    st.use(s, steve, kid)
    C.cam(s, "gate", focus=kid.head, handheld=0.004)
    st.hero(s, "child", kid)
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
    SHARED: CAMS "gate" exactly as in me06 (the same handheld seed is fine). PLACES "gate_child", C.A["forest_gap"]
      (he stands there facing the village; yaw 0 faces south). Cast: C.actor("watcher", "me"), and the child: the
      child of me06 is in the shot before: place it on f0 (no pre-roll needed: the frame is black until 422), or a
      FRESH twin C.actor("child", "me4"). NOT "me2": me08 pre-rolls child_me2 from frame 473, inside this shot.
    SKY: "dawn" (the module docstring): the same camera, another light.
    NEIGHBOURS: before, me06_leave; after, me08_nohello (the same road from the side: the child runs up to him).
    RISKS (story): the golden sky plays both evening and morning: answered by the "dawn" sky, the dip and the
      figure large enough that bare arms and a bare head show; beat 8's teal shoulder confirms it. The night insert
      the story offers is not available (the narration fixes every cut). Plain Steve skin (sets notes: his eye
      whites are two pale dots at 30 px: the white-eyed skin would be brighter).
    SCOUTED (out/test/hello_scout_meadow_me07_return_470.png): he reads as a small teal figure in the gap; the
      child is the same brown box from behind as in me06 (fix both the same way).
    MEASURED (stub, tools.hello_geo, projection and ray casts): him at forest_gap: face 8 px (unreadable, as
      wanted), x 50 %, y 52 %; the child as in me06 (from behind).
    STUB: he stands at forest_gap facing the village, the child on gate_child looks up the road.
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "me")
    him = C.watcher(s, "me", place=C.A["forest_gap"], yaw=0.0)
    C.put(kid, f0, "gate_child", toward=(-1.6, 34.0))
    kid.look_at(f0, (0.5, 40.0, 0.6), ease=0)
    kid.look_at(nar.at("sunrise", sentence="b07"), him, ease=10)
    st.use(s, kid)
    C.cam(s, "gate", focus=kid.head, handheld=0.004)
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
    SCOUTED (out/test/hello_scout_meadow_me08_nohello_520.png): his teal shoulder soft at the left edge, the child
      facing the lens on the road, the village beyond: the story's frame. The child stands in the caption band
      (y 62-72 %): raise it in the frame (camera lower, or the child further off).
    MEASURED (stub, tools.hello_geo, projection and ray casts): the child's eyes x 53 %, y 61 % (head y 49-66 %:
      its chin in the caption band), 10 degrees off the lens; his head soft at the left edge (x -101..15 %), 150
      degrees off his nose (no face).
    STUB: the child runs from y 51 to road_stop and nods; the camera behind his left shoulder looks down the road.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "me", place=C.A["forest_gap"], yaw=0.0)
    kid = C.actor("child", "me2")
    stop = C.P("road_stop")
    a = (stop[0] + 0.1, stop[1] - 3.2, stop[2])
    kid.place(f0 - 12, a, HC.yaw_to(a, stop))
    end = kid.walk(f0 - 12, [a, stop], run=True)
    kid.look_at(end, him, ease=4)
    C.hello_nod(kid, end + 5)
    st.use(s, kid)
    C.cam(s, "gate", pos=(-0.3, 59.0, 1.55), target=(0.55, 54.6, 0.95), lens=50.0, fstop=2.2, focus=kid.head)
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
    SCOUTED (out/test/hello_scout_meadow_me12_floating_780.png): the canopy and its hanging log against the sky,
      the child small under it, low in the frame (in the caption band): bring it up or closer.
    MEASURED (stub, tools.hello_geo, projection and ray casts): the child's eyes x 50 %, y 65 % (in the caption
      band), face 37 px: too small and too low.
    STUB: the child under the tree looking up; hello_set's floating camera with a small push.
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "me")
    under = C.A["floating_oak_under"]
    cam = C.set["cameras"]["floating"]["pos"]
    C.put(kid, f0, (under[0], under[1]), toward=(cam[0], cam[1]))
    kid.look_at(f0, C.A["floating_oak_target"], ease=0)
    st.use(s, kid)
    c = C.camera_spec("set:floating")
    p1 = (c["pos"][0] - 0.5, c["pos"][1] - 0.15, c["pos"][2])
    C.cam(s, "set:floating", pos1=p1, target1=c["target"], focus=kid.head)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near=under, radius=12.0)


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
    SCOUTED (out/test/hello_scout_meadow_me13_bare_830.png): the bare trunks, his back among them; the child is at
      the LEFT edge, seen from behind: turn it to profile.
    MEASURED (stub, tools.hello_geo, projection and ray casts): him among the bare oaks x 48 %, y 58 %, 165 degrees
      off his nose (his back, good); the child's eyes x 12 %, y 72 % (in the caption band, at the edge, 157 degrees
      off the lens: from behind).
    STUB: he stands among the bare oaks facing south, the child at the edge looking at him.
    """
    f0, f1 = s.frame_start, s.frame_end
    among = C.A["bare_oaks_among"]
    him = C.watcher(s, "me", place=(among[0], among[1]), yaw=0.0)
    kid = C.actor("child", "me")
    kp = (among[0] + 2.2, among[1] + 4.6)
    C.put(kid, f0, kp, toward=(among[0], among[1]))
    kid.look_at(f0, him, ease=0)
    st.use(s, kid)
    c = C.camera_spec("set:bare")
    C.cam(s, "set:bare", pos1=(c["pos"][0] - 0.3, c["pos"][1] - 0.2, c["pos"][2]), target1=c["target"], focus=him.head)
    st.hero(s, "watcher", him)
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
    SCOUTED (out/test/hello_scout_meadow_me14_pyramid_900.png): the pyramid and the bare trunks behind it read; on
      frame 900 the child is out of sight behind the pyramid: time the walk so it stops in view.
    MEASURED (stub, tools.hello_geo, projection and ray casts): child_me3 is OUTSIDE the frame the whole shot (eyes
      x 116 % at 877, 124 % at 905), and at 905 a grass tuft stands between it and the lens.
    STUB: the child walks the first part of pyramid_round; the camera tracks sideways a little.
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "me3")
    path = C.v.paths["pyramid_round"]
    kid.place(f0 - 6, path[0], HC.yaw_to(path[0], path[1]))
    kid.walk(f0 - 6, path[:3], speed=1.3)
    st.use(s, kid)
    c = C.camera_spec("set:pyramid")
    C.cam(s, "set:pyramid", pos1=(c["pos"][0] - 0.6, c["pos"][1] + 0.5, c["pos"][2]), target1=c["target"],
          focus=kid.head)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near=C.A["pyramid_beside"], radius=12.0)
