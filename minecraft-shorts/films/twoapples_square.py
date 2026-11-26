"""Two Apples, sequence SQUARE: the village square at dusk, the stair mouth by the well. Beats 1, 2, 3 and 20 (shots
sq01_base, sq02_lip, sq03_push, sq20_grow), sky "dusk". One function per shot; the contract is in
films/twoapples_common.py (tags "sq...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE (films/twoapples_set.py "THE SQUARE", engine/underground.py "mouth"): the well's stone x -3..2, y -3..2
  (a 1-high rim, a 2-high core, posts and roof), the bell on its south side, the bell lamps at (-4, -4) and (0, -4), the
  village lamp post at (7, -3). THE STAIR MOUTH: 2 wide (x 4..5), open over y -3..0 east of the well, its rim turned to
  grass (x 3..6, y -4..1), two wall torches just under the rim (group ug_mouth: the glow from below). ug_lip (4.85,
  1.42, 0) is its lip (facing south into it); ug_lip_target (5, -1.5, -1.2) the stairs below; ug_mouth_target (5, -1,
  0.2) the glowing hole; ug_push_start (5, 3.4) dad before the push; path ug_down (the square -> the stairs -> the
  aisle, with the steps' heights), ug_push (to the lip); ta_round_well / ta_round_well_on (sq20).
THE SKY: "dusk" (films/twoapples.py SKIES): the sun just under the western houses; looking west (sq01, sq20) the well
  stands against the orange-pink horizon and the indigo top with the first stars.
LIGHT: C.lights(s, "square") (the village's lamps at the look-dev dusk level, the stairwell's torches at 1); sq02
  C.lights(s, "lip") + C.glow(s, "mouth_glow") (the warm glow from below is his key); sq03 C.lights(s, "push").
TAGS: child_sq (sq02, sq03: placed on each shot's first frame, never pre-rolled), steve_sq01, steve_sq03, dad_sq
  (sq03: pre-rolled, in no shot before), kid_sq20a, kid_sq20b, grownup_sq20 (sq20: pre-rolled, in no shot before).
  A new twin: any further "sq..." tag.
SHARED: CAMS["lip"] (sq02) is the mirror of CAMS["box"] (bx24, the last shot of the film): see films/twoapples_common.py
  SHARED. Keep its lens, stop, distance, eye height and the screen direction of the look.
"""
import math

from engine import players
from engine import underground as U
from films import twoapples_common as TC


def sq01_base(st, s, C, nar):
    """BEAT 1  "In this town, the player has an underground base."
    frames 1-83 (83 f, 3.46 s), sky dusk, the wall shut. Words: In 8, this 10, town 16, the 30, player 31, has 40, an
    45, underground 48, base 63. The last word is spoken until 74; after it 9 frames to the cut.

    STORY: Dusk on the square, lamp posts lit. From a child's eye height beside the well: a two-wide stone stair cut
    into the grass, torchlight glowing up out of it. Steve crosses in profile and walks down into it without slowing
    until his head sinks below the grass. Slow push in on the glowing hole.
    Cast: Steve (the player). Effects: stair mouth cut into the grass with wall torches, torch glow and bloom from
    below, lit lamp posts, well in soft foreground.

    MUST BE SEEN, ON WHICH WORD
      frame 1         Steve already walking (the FILM'S FIRST FRAME: nothing can be pre-rolled before it; he is placed
                      a few steps north of the mouth on frame 1 and walks from there), the glowing hole, the dusk sky
      "player"        Steve in profile at the lip, in the safe area (x 8-82 %, y 14-60 %)
      "underground"   his head sinking below the grass; the camera pushing in on the glow
      "base" .. end   the empty glowing hole (nothing important in the last 3 frames)
    NO SEE-THROUGH CUTAWAY in this shot: it is the film's first (Stage.see_through loses it there).
    SHARED: none (the set's b01: C.cam(s, "set:b01", target=steve.head): the aim rides on his head, then eases onto
      the hole while the camera pushes in from pos0 to pos).
    NEIGHBOURS: none before (the film opens here); after, sq02_lip (the child alone at the same lip).
    MEASURED (engine/underground.py BEATS 1 and the set's still out/test/twoapples_set_b01_mouth.png): with the walk
      from (5, 6.5) his head is in the picture on frames 0-60 of the shot and in the safe area on 0-53; at the lip
      (frame 36) head x 67 / y 35 in profile, the well and the sunset behind; the hole with its torch at x 25 / y 63
      on that frame (in the caption band: the push-in ends on it, lower).
    MEASURED BY THE LEAD (render.py --still 0.1 = frame 3: out/test/twoapples_0.1.png; tools/twoapples_geo): on the
      film's first frames the aim is on Steve walking TOWARD the lens among the houses (frontal), the well and the
      mouth are not in the frame yet; at the lip ("player" 31) his eyes x 67 / y 40 in profile (47 degrees off the
      lens: three-quarter), the well and the sunset behind (sheet tile at 42); on frame 60 his head is at y 62-77 %
      (sinking, in the caption band). The hook is Steve and the dusk; the director may open on the glowing hole first.
    STUB NOW: exactly that recipe (Steve from PLACES["steve_in"] down ug_down[1:10] at players.WALK_SPEED, the set's
      camera, smooth ease as measured). Hero: Steve.
    """
    f0 = s.frame_start
    steve = C.actor("steve", "sq01")
    start = C.P("steve_in")
    path = [start] + list(C.paths["ug_down"][1:10])
    steve.place(f0, start, math.pi)
    steve.walk(f0, path, speed=players.WALK_SPEED)
    st.use(s, steve)
    C.cam(s, "set:b01", target=steve.head, focus=(5.0, 0.6, 0.9), ease="smooth", handheld=0.004)
    st.hero(s, "steve", steve)
    C.lights(s, "square")


def sq02_lip(st, s, C, nar):
    """BEAT 2  "My dad got taken down there."
    frames 84-137 (54 f, 2.25 s), sky dusk, the wall shut. Words: My 86, dad 91, got 99, taken 104, down 113, there
    121. The last word is spoken until 128; after it 9 frames to the cut.

    STORY: Close on the baby villager alone at the lip of the stairs, three-quarter front with his look cheated toward
    the lens, staring down. The warm glow from below is his key light. The square behind him is empty and out of
    focus. Remember this framing: the last shot of the film repeats it.
    Cast: Baby villager (narrator). Effects: torch glow from the stairwell as key light, shallow depth of field.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. end  the child's face (nose, brow, both eyes) three-quarter, looking DOWN to frame right into the
                      glow, lit warm from below; the square soft behind; something already moving on frame 1 (the
                      handheld float and his head's slow drift down)
      "down" .. "there"  his look on the stairs below (the head tipped down a little further)
    SHARED: CAMS["lip"], exactly (the mirror of CAMS["box"], bx24: 50 mm f/2.0, 2.4 blocks, eye height, head x 50 /
      y 44 %). Place: ug_lip (the child; yaw south, into the mouth). Cast: C.actor("child", "sq").
    NEIGHBOURS: before, sq01_base (Steve gone down the same hole); after, sq03_push (the event itself, side-on).
    MEASURED (the set's still out/test/twoapples_set_b02_lip.png, frame 12 of a stand-in shot): head x 50 / y 44,
      about half the frame wide; skin s 0.43, stone G/R 0.93; the face lit warm from below by MOUTH_GLOW (240 W; the
      torches alone, under the ground, gave +2 % on the face).
    STUB NOW: the set's staging: the child at ug_lip, look at U.cheat(ug_lip_target, ug_lip, lens, 0.35) on frame 1,
      then a slow drift a little further down over the shot. Hero: the child.
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "sq")
    C.put(kid, f0, "ug_lip")
    cam = TC.CAMS["lip"]["pos"]
    look = U.cheat(C.A["ug_lip_target"], C.A["ug_lip"], cam, 0.35)
    kid.look_at(f0, look, ease=0)
    kid.look_at(f0 + 1, (look[0], look[1] - 0.3, look[2] - 0.35), ease=max(4, f1 - f0 - 6))
    st.use(s, kid)
    C.cam(s, "lip", focus=kid.head, handheld=0.006)
    st.hero(s, "child", kid)
    C.lights(s, "lip")
    C.glow(s, "mouth_glow")


def sq03_push(st, s, C, nar):
    """BEAT 3  "The player walked into him until he was downstairs."
    frames 138-228 (91 f, 3.79 s), sky dusk, the wall shut. Words: The 140, player 142, walked 152, into 161, him 167,
    until 180, he 187, was 189, downstairs 193. The last word is spoken until 215; after it 13 frames to the cut.

    STORY: The event itself, side-on and low. Dad, a librarian in the book hat, arms crossed, is shoved along the path
    by Steve, who just keeps walking into his back. Dad slides ahead of him in small smooth nudges, as pushed mobs do,
    reaches the stair mouth and bumps down the first step, his head turned back toward the lens the whole way. The
    baby's big head is soft in the bottom corner of the foreground, watching.
    Cast: Steve, Dad (librarian), Baby villager (narrator). Effects: smooth push slide (no walk cycle on dad), dad's
    head held turned back to the last frame.

    MUST BE SEEN, ON WHICH WORD
      frame 1         dad already sliding (the push is pre-rolled: dad and Steve are in no shot before), Steve at his
                      back, the child's head soft in the bottom right corner (watching dad)
      "walked into"   Steve's walk into dad's back (the taps of U.push: about 1.1 blocks/s in small nudges)
      "downstairs"    dad bumps down the first step (U.push's first drop: 59 frames after the push begins)
      the whole shot  dad's head turned back toward the lens (look_at held; never the back of his hat)
    SHARED: none of the camera (the set's b03: side-on and low from the east, the well behind them). Places:
      ug_push_start (dad), path ug_push + the lip, ta_push_kid (the child). Cast: C.actor("dad", "sq"),
      C.actor("steve", "sq03"), C.actor("child", "sq") (in sq02 before: placed on frame 1, never pre-rolled).
    NEIGHBOURS: before, sq02_lip; after, ev04_bed (that evening, the bedroom). Hard cuts.
    MEASURED (the set's still out/test/twoapples_set_b03_push.png, 10 frames before dad's drop): dad x 46 / y 38 (book
      hat, face to the lens), Steve x 72 / y 39 at his back, the child's head a soft brown block bottom right (x 88 /
      y 67). Palette ok.
    STUB NOW: U.push pre-rolled PUSH_PRE frames, so that dad drops on about "downstairs"; dad's head held on a point
      beside the lens; the child at ta_push_kid looking at dad. Locked camera with the handheld (dad's slide moves from
      frame 1). Heroes: dad, Steve.
    """
    f0 = s.frame_start
    A = C.A
    dad = C.actor("dad", "sq")
    steve = C.actor("steve", "sq03")
    kid = C.actor("child", "sq")
    fp = f0 - PUSH_PRE
    path = list(C.paths["ug_push"]) + [(A["ug_push_start"][0], -2.0, 0.0)]
    U.push(steve, dad, fp, path, C.v.world)
    cam = C.camera_spec("set:b03")
    dad.look_at(fp, (cam["pos"][0], cam["pos"][1] - 0.6, 1.4), ease=0)
    C.put(kid, f0, "ta_push_kid")
    kid.look_at(f0, dad, ease=0)
    st.use(s, dad, steve, kid)
    C.cam(s, "set:b03", focus=dad.head, handheld=0.008)
    st.hero(s, "dad", dad)
    st.hero(s, "steve", steve)
    C.lights(s, "push")


PUSH_PRE = 12          # sq03: the push begins this many frames before the shot (dad drops 59 frames after it begins)


def sq20_grow(st, s, C, nar):
    """BEAT 20  "Babies grow up in twenty minutes."
    frames 1210-1277 (68 f, 2.83 s), sky dusk, the wall shut. Words: Babies 1212, grow 1224, up 1230, in 1235, twenty
    1239, minutes 1247. The last word is spoken until 1258; after it 19 frames to the cut.

    STORY: The square at the same dusk. Two baby villagers chase each other round the well, staggered. The one in front
    runs behind the well as a baby and comes out the other side full size, and slows to a walk. The other keeps
    running, alone, past the glowing stair mouth.
    Cast: Second baby villager, Third baby villager, Adult villager (the one who grew up). Effects: baby swapped for an
    adult while hidden behind the well, lamp posts, stair mouth glow in the background.

    MUST BE SEEN, ON WHICH WORD
      frame 1         both children already running (pre-rolled: in no shot before), staggered 0.7 block (two runners
                      0.2 apart are one two-headed shape)
      "grow up"       the front child behind the well (hidden: U.swap_hidden picks the middle of its hidden run)
      "twenty minutes" the grown-up coming out at the well's other side, slowing to a walk; the other child running on,
                      alone, past the glowing mouth
    SHARED: none (the set's b20: from the east over the glowing mouth, 22 mm f/4). Paths: ta_round_well (the first),
      ta_round_well_on (the second, on past the mouth toward the lens). Cast: C.actor("kid", "sq20a"), ("kid",
      "sq20b"), ("grownup", "sq20").
    NEIGHBOURS: before, cu19_behind (the seam behind dad's back, under the ground); after, bx21_small (the slot, black).
      The only dusk shot between them: it must read as the square of sq01-03 at the same dusk (the same sky).
    RISKS (story): if the wipe behind the well is missed at phone size, do the swap in the open on a single frame
      with no effect, which is what the game does.
    MEASURED PROBLEM (the set's stills out/test/twoapples_set_b20_grow.png, _grow_grown.png, on a 5 s stand-in shot):
      the children are about 40 px tall; both are in the safe area together on 9 frames (1.6-2.0 s into the run), the
      swap 3.0 s in, the grown-up and the other child together on 8 frames (4.6-4.9 s in). THIS SHOT IS ABOUT 2.8 s:
      the whole circuit does not fit. The stub pre-rolls the run RUN_PRE frames so the shot opens on both children on
      the north side; the grown-up may come out only at the very end or after it. The director must restage: a
      shorter circuit (a path that goes behind the well's west side within the first second), the grown-up out by
      "minutes", and / or a longer lens that follows them (the story's picture is the swap, not the circuit).
    MEASURED BY THE LEAD ON THIS STUB (tools/twoapples_geo; out/test/twoapples_scout_sq20_grow_1222_zones.png and the
      sheet tile at 1244): the children are INVISIBLE at phone size: 16 blocks from the 22 mm lens, faces 9-11 px, at x
      80-83 % and from behind (160 degrees off) on frame 1210, then behind the well's stone from about 1230; the swap
      lands about 1245; the second child is ALSO hidden behind the well (ta_round_well_on is the same circuit) from
      1230 to past 1262; with the grown-up at the children's run (ADULT_SPEED 4.4; the set's 2.4 brought him out after
      the shot's end) he comes out at the well's south-west corner only on 1274 (x 14 %, facing the lens, 20 px), 3
      frames before the cut. THE DIRECTOR MUST RESTAGE: (1) a camera much nearer or a longer lens (40-60 mm) so the
      children are 25 px or more; (2) open on the front child a block or two before its hiding point, the swap early in
      the hidden run (undead.vanish / appear by hand instead of swap_hidden's middle), the grown-up out by "minutes"
      (1247) and slowing to a walk; (3) the second child on its OWN route that stays in the open and runs past the
      glowing mouth (not the same circuit). The story's fallback stands: the swap in the open on a single frame.
    STUB NOW: the set's staging pre-rolled. Heroes: the two children.
    """
    f0, f1 = s.frame_start, s.frame_end
    path = C.paths["ta_round_well"]
    p2 = C.paths["ta_round_well_on"]
    k1 = C.actor("kid", "sq20a")
    k2 = C.actor("kid", "sq20b")
    adult = C.actor("grownup", "sq20")
    fr = f0 - RUN_PRE
    k1.place(fr, path[0], TC.yaw_to(path[0], path[1]))
    k1.walk(fr, path, speed=4.4, run=True)
    k2.place(fr, p2[0], TC.yaw_to(p2[0], p2[1]))
    k2.walk(fr + 4, p2, speed=4.4, run=True)
    cam = C.cam(s, "set:b20", handheld=0.006)
    try:
        r = U.swap_hidden(k1, adult, cam["pos"], fr, f1, C.v.world, then=list(path[2:]), speed=ADULT_SPEED)
        C.memo["sq_swap"] = r
    except ValueError as e:                     # the well never hides him in this window: no swap (the director's)
        print("[twoapples] sq20_grow: %s" % e)
    st.use(s, k1, k2, adult)
    st.hero(s, "children", k1, k2)
    C.lights(s, "square", near="well", radius=24.0)


RUN_PRE = 36           # sq20: the children start running this many frames before the shot (in no shot before)
ADULT_SPEED = 4.4      # sq20: the grown-up comes out at the children's run (the set's TS.ADULT_SPEED 2.4 brought him out
#                        after the shot's end); "slows to a walk" is the director's (a second walk from his exit)
