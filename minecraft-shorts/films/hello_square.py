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
LIGHT: C.lights(s, "gold", near=<place>, radius=16) (daylight: the torches at their own level; far ones off).
"""
from films import hello_common as HC


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
    SHARED: none with other sequences. PLACES "guard", "guard_child"; CAMS "guard" (a start: change it freely).
      Cast: C.actor("steve_iron", "sq"), C.actor("child", "sq"), C.actor("farmer", "sq"), C.actor("librarian", "sq").
    NEIGHBOURS: the film's first shot; after it dn02_fight (night, the zombie at the child's door). Hard cut.
    NOTES: a villager's head turned more than about 26 degrees from the lens is a blank box; the child is half his
      height, so a camera at child height looks up at Steve: keep his face out of the top 14 %.
    SCOUTED (out/test/hello_scout_gold_sq01_guard_40.png): Steve's face reads well (golden key from the left, a
      house behind him); the child is at the right edge in the caption band, too small. The child is half his
      height: both faces in the upper half of the frame only work if the child is NEARER the lens than Steve
      (perspective), e.g. the child 2 blocks from a low lens, Steve 3.5-4 blocks, the lens just above the child's
      eyes looking up a little.
    STUB: Steve on "guard" facing south, the child at his leg looking up, two adults idling behind, CAMS "guard".
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_iron", "sq")
    kid = C.actor("child", "sq")
    ada, bo = C.actor("farmer", "sq"), C.actor("librarian", "sq")
    C.put(steve, f0, "guard", yaw=0.0)
    C.put(kid, f0, "guard_child", toward="guard")
    C.put(ada, f0, (-4.3, -2.7), toward=(-6.0, -1.0))
    C.put(bo, f0, (-6.0, -1.0), toward=(-4.3, -2.7))
    kid.look_at(f0, steve, ease=0)
    steve.idle(f0, f1 + 1)
    ada.idle(f0, f1 + 1, seed=3)
    bo.idle(f0, f1 + 1, seed=5)
    st.use(s, steve, kid, ada, bo)
    C.cam(s, "guard", focus=steve.head)
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
    SHARED: PLACES "watch_square" (also beats 10 and 11: the same spot all three shots). CAMS "square_long" (a
      start). Cast: C.actor("watcher", "sq"), C.actor("farmer", "sq"), C.actor("librarian", "sq"),
      C.actor("kid", "sq_a"), C.actor("kid", "sq_b"). Wheat: villagers hold an object with Character.hold(obj)
      (props.make_item("wheat", C.v.collection)); a held flat item lies along the hand (edge-on from the side).
    NEIGHBOURS: before, me08_nohello (the meadow: the child's hello unanswered); after, sq10_grownups (the same
      square, the same watcher, from the well). Hard cuts.
    RISKS (story): "His face before the reveal": two white eye pixels can show as bright dots even at distance and
      spoil the ending: beyond focus with a face under about ten pixels, else use him further away. Two children
      0.2 block apart are one two-headed shape: stagger them by 0.7 block. The well (x -2..1, y -2..1) and the
      bell stand between the south of the square and the road: check the line of sight (CAMS "square_long" looks
      past the well's east side).
    SCOUTED (out/test/hello_scout_gold_sq09_watches_572.png, from the square's south-east corner): he stands at the
      mouth of the road with a lamp post beside him, and HIS FACE IS READABLE (eyes and all, 85 mm f/2.0): that
      breaks the face rule and must be fixed first (much shallower focus on the villagers, f/1.2, or a shorter
      lens, so that his face is under about ten pixels and soft). The well's mossy wall fills the left 40 % of
      the frame: move the lens east or let the villagers cross in front of it. (The first stub camera, from
      (1.6, -9.8), looked straight through the well.)
    STUB: the farmer and the librarian cross, two children run, he stands at "watch_square" facing south.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "sq", place="watch_square", yaw=0.0)
    ada, bo = C.actor("farmer", "sq"), C.actor("librarian", "sq")
    k1, k2 = C.actor("kid", "sq_a"), C.actor("kid", "sq_b")
    a0, a1 = (-3.5, 2.6, 0.0), (4.0, 2.4, 0.0)
    ada.place(f0 - 20, a0, HC.yaw_to(a0, a1))
    ada.walk(f0 - 20, [a0, a1], speed=1.4)
    b0, b1 = (4.5, -4.2, -0.06), (-3.5, -4.6, -0.06)
    bo.place(f0 - 10, b0, HC.yaw_to(b0, b1))
    bo.walk(f0 - 10, [b0, b1], speed=1.5)
    for k, y, lag in ((k1, 4.6, 0), (k2, 5.3, 9)):              # north of the well (x -2..2, y -2..2)
        p0, p1 = (6.0, y, -0.06), (-6.0, y + 0.3, -0.06)
        k.place(f0 - 30 + lag, p0, HC.yaw_to(p0, p1))
        k.walk(f0 - 30 + lag, [p0, p1], run=True)
    st.use(s, ada, bo, k1, k2)
    C.cam(s, "square_long", focus=(1.0, 2.5, 1.4), handheld=0.006)
    st.hero(s, "farmer", ada)
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
    SHARED: PLACES "watch_square" (the same spot as beats 9 and 11), "grownups", "grownups_child" (a start: the
      camera, the adults and the child must line up on him: from watch_square through the middle of the two adults
      the line reaches CAMS "grownups" (6.6, 0.5), where a low camera can stand). Cast: C.actor("farmer", "sq"),
      C.actor("toolsmith", "sq"), C.actor("child", "sq"), C.actor("watcher", "sq").
    NEIGHBOURS: before, sq09_watches; after, sq11_stare (the child alone on the road, staring at him). Hard cuts.
    RISKS (story): the line is a thought with no action: keep him visible in the gap between the two adults and hold
      the child's head turn toward him to the last frame. The child stands in front of the adults, not tucked
      between them (a face tucked against a neighbour is a third hidden: CONTRACT.md).
    SCOUTED (out/test/hello_scout_gold_sq10_grownups_660.png): the farmer (left) and the toolsmith (right) frame the
      gap, he stands small and still in it, the child in front at the lower left: the story's picture. The child's
      face is low (in the caption band) and the adults face the lens more than each other: turn them to profile.
      (The first stub put the child inside the well's corner block.)
    STUB: the two adults face each other and nod, the child in front looks at the road, he stands far behind.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "sq", place="watch_square", yaw=0.0)
    ada, tom = C.actor("farmer", "sq"), C.actor("toolsmith", "sq")
    kid = C.actor("child", "sq")
    pa, pt = HC.PLACES["grownups"]
    C.put(ada, f0, pa, toward=pt)
    C.put(tom, f0, pt, toward=pa)
    C.put(kid, f0, "grownups_child", toward=HC.CAMS["grownups"]["pos"])
    ada.look_at(f0, tom, ease=0)
    tom.look_at(f0, ada, ease=0)
    kid.look_at(f0, ada, ease=0)
    ada.nod(f0 + 4)
    tom.nod(f0 + 20)
    kid.look_at(nar.at("still", sentence="b10"), him, ease=8)
    st.use(s, ada, tom, kid)
    C.cam(s, "grownups", focus=kid.head)
    st.hero(s, "child", kid)
    st.hero(s, "farmer", ada)
    C.lights(s, "gold", near=(4.6, 3.0, 0.0), radius=16.0)


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
    SHARED: PLACES "watch_square" (he stands where he stood in beats 9 and 10), "stare_child". Cast:
      C.actor("child", "sq"), C.actor("watcher", "sq"), C.actor("kid", "sq_a"), C.actor("kid", "sq_b").
    NEIGHBOURS: before, sq10_grownups (the same child, the same watcher: placed on f0, nothing keyed before);
      after, me12_floating (the meadow, the floating oak). Hard cuts.
    CUT PRIORITY (story): if the narration had to be shortened this line went first; it was kept (63.8 s).
    SCOUTED (out/test/hello_scout_gold_sq11_stare_700.png): his teal shirt and arm soft over the left 40 % of the
      frame, the child at the right in profile looking toward him; the child's head is partly in the caption band
      and not yet tipped back: lower the lens or bring the child up in the frame, and tighten on the head (the
      push). (The first stub camera stood inside his body.)
    STUB: he stands at "watch_square" facing south; the camera behind his right hip looks at the child on the road.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "sq", place="watch_square", yaw=0.0)
    kid = C.actor("child", "sq")
    k1, k2 = C.actor("kid", "sq_a"), C.actor("kid", "sq_b")
    C.put(kid, f0, "stare_child", toward=(0.9, 9.0))
    kid.look_at(f0, him, ease=0)
    for k, y, lag in ((k1, 3.6, 0), (k2, 2.9, 8)):
        p0, p1 = (-5.0, y, -0.06), (6.0, y - 0.2, -0.06)
        k.place(f0 - 24 + lag, p0, HC.yaw_to(p0, p1))
        k.walk(f0 - 24 + lag, [p0, p1], run=True)
    st.use(s, kid, k1, k2)
    C.cam(s, "hip", focus=kid.head)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="stare_child", radius=16.0)
