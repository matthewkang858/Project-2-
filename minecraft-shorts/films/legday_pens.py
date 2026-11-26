"""Leg Day, sequence PENS: the chicken pen and the cow pen at the village edge, golden light. Beats 4, 5, 6, 17
(shots pn04_farms, pn05_milk, pn06_told, pn17_cows), sky "gold". One function per shot; the contract is in
films/legday_common.py (tags "pn...", C.actor / C.narrator / C.cow / C.hen, C.cam, C.lights, st.use / st.hero).

STATUS: STUBS written by the lead (camera from the set builder's suggestion, cast placed, the beat's action roughly
keyed so the film builds and renders end to end). Every docstring carries the beat, its words with their frames,
what must be seen on which word, the neighbours, the risks and the measured notes. The acting is yours.

THE PLACE (films/legday_set.py, "THE PENS"; engine.animals pen_set): west of the exit road, south of the anvil wall.
  chicken_pen  ring x -23..-17, y 20..26, gate (-20, 20) on its south side; inside x -22..-18, y 21..25
  cow_pen      ring x -14..-7, y 20..26, gate (-11, 20); inside x -13..-8, y 21..25
  Anchors: kai_chickens (-19.6, 22.6); zuri_cow (-11.3, 22.5); cow_milk_target (-10.0, 23.3) (the milked cow);
  narrator_fence (-10.55, 19.35) facing north (outside the cow pen's south fence); hide_1..4 (-10.3, 21.9) (-10.45,
  23.3) (-10.3, 24.75) (-11.45, 23.95) facing EAST (the road), behind hide_cow_1..3_target (-8.7, 21.65 / 23.3 /
  24.95) (three cows end to end along the east fence); arrow_post_target (-6.55, 22.45) (the east fence post's road
  face); chicken_pen_center / _gate, cow_pen_center / _gate. The ground south of the pens (x -24..-6, y 17..19) is
  clear of tufts (beat 4's track rides there) and so is the strip between the cow pen and the road.
  A fence is 1.0 high as drawn: a cow looks over it, hens need the lens above the top rail (animals' notes). The
  players face EAST (the road and the sun) in all four: their faces are lit.
THE MILK LOOP IS ONE CLOCK (the review): a drink takes the game's 32 ticks = 38 frames (players.drink's default),
  the empty bucket is used on the cow at once after, and the full one goes straight up again: pn04 drink 265-303
  (the bucket empties on 303, inside pn05), "fill" 323 the tap, 325-363 the next drink (at her face on "up" 334,
  still drinking over the cut into pn06), 368 the next tap, from 370 the next drink. The first stubs ended drinks
  after 7-34 frames and tapped while a drink was running. Keep it on this clock (DRINK, DRINK_ENDS).
THE SKY: "gold" (sun due east, 27 degrees). In b04-b06 the camera looks north at the pens: the sun 90 degrees off
  its axis; in pn17 the camera on the road side looks west: the sun behind it (front light: the set builder's note).
ANIMALS (engine.animals): cow 1.56 tall (back 1.375), chicken 0.94; walk / wander(animals, f0, f1, area) / look_at
  (head clamped to 75 yaw / 40 pitch) / idle(f0, f1, watch=player); animals.milk(player, frame, f0, f1) = the empty
  bucket used on the cow ON frame (the arm swings) and a milk bucket from then (f1 = the shot's frame_end + 1,
  required); animals.hand_item(player, item, f0, f1) for any held item with its own visibility (a hand holds one
  thing: a later hand_item takes over). Key heroes first, wander last.
TAGS (twins): the stubs use one tag per shot (pn04: kai_pn, zuri_pn, hen_pn4h0..3, cow_pn4c0..1; pn05: zuri_pn2,
  cow_pn5; pn06: efe_pn, zuri_pn3, cow_pn6; pn17: steve/kai/zuri/ari_pn17, cow_pn17c0..2) so that held items never
  leak from one shot into another (Character.hold stays on its instance). Merge them where it helps.
LIGHT: C.lights(s, "gold", near=<point>, radius=8..10).
PREVIEW samples for render.py previews: 6 (legday_common.PREVIEW_SAMPLES).
"""
from engine import animals
from films import legday_common as LC

# ---------------------------------------------------------------------------------------------------------------
# this sequence's own cameras (starts: the set builder's suggestions; yours to change)
# ---------------------------------------------------------------------------------------------------------------
PN04_CAM = LC._set_cam("b04")             # a linear track west -> east along the south fences (3.6 s in the set's
#                                           proof; this shot is 3.92 s: the track is slower)
PN05_CAM = dict(LC._set_cam("b05"), pos1=(-10.25, 17.85, 1.43))
PN06_CAM = dict(LC._set_cam("b06"), pos1=(-9.5, 18.35, 1.2))
PN17_CAM = dict(LC._set_cam("b17"), pos1=(-4.45, 21.85, 1.1))
HENS = ((-21.2, 23.6), (-20.6, 21.5), (-18.6, 23.4), (-19.0, 24.6))
COWS_04 = ((-10.2, 23.1, -10.0, 19.0), (-8.6, 24.4, -9.5, 20.0))     # (x, y, facing toward x, y)
ARROW_DIR = (-0.55, -0.78, -0.30)         # the way the arrows flew: from up the road to the NORTH-EAST (where the
ARROW_DIR_2 = (-0.62, -0.72, -0.31)       # patrol is) into the east fence post: the shafts stand 60-70 degrees off
#                                           the lens axis and read as arrows (the first stub's flew from due east,
#                                           straight at the lens: two white X shapes, the fletching end-on)
DRINK = 38                                # frames of one drink: the game's 32 ticks (players.drink's default)
DRINK_ENDS = 303                          # the milk loop ON THE GAME'S CLOCK across pn04 -> pn05 -> pn06: the drink
#                                           begun in pn04 (265) empties the bucket on 303; tap on "fill" 323, drink
#                                           325-363, tap 368, drink from 370


def pn04_farms(st, s, C, nar):
    """BEAT 4  "There's a chicken farm, and a cow farm for protein shakes."   frames 205-298 (94 f, 3.92 s), sky gold.
    Words: There's 207, a 211, chicken 213, farm 223, and 242, a 245, cow 246, farm 256, for 265, protein 269,
    shakes 280.

    STORY: About 3.6 s. One slow low sideways track along the fences. First the chicken pen: Kai stands among four
    chickens and lifts a cooked chicken to his face while the live chickens turn their heads up to watch him. The move
    carries on to the cow pen: Zuri stands beside a cow and tips a milk bucket up to her face. Both players in profile
    cheated toward the lens.
    Cast: Kai, Zuri, four chickens, two cows. Effects: cooked chicken held, milk bucket held, eat and drink arm pose,
    oak fences and fence gates, chicken head turns.

    MUST BE SEEN, ON WHICH WORD
      frame 205       the track already moving (linear: at speed on frame 1), Kai among the hens
      "chicken" 213 .. "farm" 223   Kai lifting the cooked chicken to his face, the hens' heads turned up to him
      "cow" 246 .. "farm" 256       the move reaching the cow pen (the STORY'S ORDER: the cow farm on its words)
      "protein shakes" 269-292      Zuri tipping the milk bucket up to her face beside the cow
      both players in profile cheated toward the lens (C.to_lens: a face in strict profile shows a blank cheek)
    SHARED: none (kai_chickens, zuri_cow, cow_milk_target; the cow pen's cow and Zuri come back in pn05 / pn06:
      keep their places so the three shots cut together).
    NEIGHBOURS: before, sq02_reps (the stone row); after, pn05_milk (Zuri and the cow, close).
    MEASURED (the set builder, out/test/legday_set_b04_pens_a / _b[_zones].png): _a Kai eating a cooked chicken among
      four hens; _b Zuri drinking beside the cow. The top rail crosses the lower frame. The track speed (2.6 blocks/s
      over 3.6 s) is for the director. THE LEAD: a linear track reaches the cow pen only at the end (x -16 on
      "cow"): ease it or start further east so "cow farm" is on the cows.
    NOW (stub): PN04_CAM linear over the shot, Kai eating (kai_pn), four hens looking up at him (hen_pn4h0..3), Zuri
      drinking milk (zuri_pn) beside two cows. Heroes: Kai, Zuri.
    """
    f0, f1 = s.frame_start, s.frame_end
    kai = C.actor("kai", "pn")
    C.put(kai, f0, "kai_chickens", toward=(-18.2, 21.5))
    kai.hold("cooked_chicken")
    kai.eat(f0 + 4, C.at(s, "and") - 2)
    zuri = C.actor("zuri", "pn")
    C.put(zuri, f0, "zuri_cow", toward=(-9.9, 21.3))
    zuri.hold("milk_bucket")
    zuri.drink(DRINK_ENDS - DRINK)                # 265: the game's 38 frames, ending in pn05 (on its clock)
    hens = []
    for i, (x, y) in enumerate(HENS):
        h = C.hen("pn4h%d" % i)
        h.place(f0, (x, y, 0.0), LC.yaw_to((x, y), (-19.6, 22.6)))
        h.look_at(f0, kai.eye_point(f0), ease=0)
        hens.append(h)
    cows = []
    for i, (x, y, tx, ty) in enumerate(COWS_04):
        c = C.cow("pn4c%d" % i)
        c.place(f0, (x, y, 0.0), LC.yaw_to((x, y), (tx, ty)))
        c.idle(f0, f1, seed=i)
        cows.append(c)
    st.use(s, kai, zuri, *hens, *cows)
    C.cam(s, None, focus=kai.head, ease="linear", **PN04_CAM)
    st.hero(s, "kai", kai)
    st.hero(s, "zuri", zuri)
    C.lights(s, "gold", near=(-15.0, 22.0, 1.0), radius=10.0)


def pn05_milk(st, s, C, nar):
    """BEAT 5  "Milk doesn't even fill you up."   frames 299-348 (50 f, 2.08 s), sky gold.
    Words: Milk 301, doesn't 309, even 317, fill 323, you 330, up 334.

    STORY: About 2.4 s. Portrait of Zuri and one cow, both cheated toward the lens. She lowers the bucket from her face
    and it is empty. She taps the cow with it once, one arm swing, and the bucket is full of milk again and goes
    straight back up to her face. One bucket, one cow, no end. The cow turns its head and looks into the lens.
    Nothing lies on the ground.
    Cast: Zuri, one cow. Effects: held bucket swapping between milk bucket and empty bucket, drink arm pose, one arm
    swing at the cow, cow head turn to the lens.

    MUST BE SEEN, ON WHICH WORD
      frame 299       the milk bucket at her face (drinking, moving)
      "doesn't" 309   the bucket lowered: EMPTY (the swap from milk_bucket to bucket as she finishes drinking)
      "fill" 323      one arm swing at the cow: the bucket is FULL again (animals.milk: the swing ON its frame)
      "up" 334        the full bucket straight back up to her face
      the cow         turns its head and looks into the lens (by "up"); nothing lies on the ground
    SHARED: none (zuri_cow, cow_milk_target: the same places as pn04 and pn06).
    NEIGHBOURS: before, pn04_farms; after, pn06_told (the same loop over the narrator's shoulder).
    RISKS (story): "the empty and full bucket are two small held sprites. Stage the bucket toward the lens in the
      portrait and make the swap on the tap. Fallback: put Kai behind her in the frame eating a cooked chicken, the
      one who is actually being fed." A flat item lies along the hand: edge-on from the side, readable from behind or
      above (CONTRACT).
    MEASURED (the set builder, out/test/legday_set_b05_milk[_zones].png): Zuri and the cow both toward the lens over
      the fence, 50 mm; the bucket sits low (y 65 %, in the caption band): raise it or the camera. THE LEAD'S SCOUT
      of the stub (out/test/legday_scout_pn05_milk_324[_zones].png, on "fill"): the tap reads (the bucket blurred
      in the swing at the centre), Zuri's face y 35-48 %; the cow's head at the right edge (x 82-90 %): reframe.
    NOW (stub): PN05_CAM (+ a slow push), zuri_pn2 ending pn04's drink (the milk bucket, hand_item) on 303, the empty
      bucket lowered from 303, tapping the cow on "fill" 323 (animals.milk), drinking again 325-363 (the game's 38
      frames: at her face on "up" 334, still drinking at the cut); the cow's head to the lens from "you". Heroes:
      Zuri, the cow.
    """
    f0, f1 = s.frame_start, s.frame_end
    zuri = C.actor("zuri", "pn2")
    C.put(zuri, f0, "zuri_cow", toward=(-9.7, 20.6))
    cow = C.cow("pn5")
    cp = C.P("cow_milk_target")
    cow.place(f0, cp, LC.yaw_to(cp, (-11.0, 20.5)))
    zuri.look_at(f0, cow.eye_point(f0), ease=0)
    empty = DRINK_ENDS                            # 303: pn04's drink ends (the game's clock): the bucket is empty
    animals.hand_item(zuri, "milk_bucket", f0, empty)
    zuri.drink(f0, empty - 4)
    fill = C.at(s, "fill")
    animals.milk(zuri, fill, empty, f1 + 1)
    zuri.drink(fill + 2)                          # 325-363: straight back up, at her face on "up" 334
    cow.look_at(f0, zuri.eye_point(f0), ease=0)
    cow.look_at(C.at(s, "you"), PN05_CAM["pos"], ease=8)
    st.use(s, zuri, cow)
    C.cam(s, None, focus=zuri.head, **PN05_CAM)
    st.hero(s, "zuri", zuri)
    st.hero(s, "cow", cow)
    C.lights(s, "gold", near=(-11.0, 22.0, 1.0), radius=8.0)


def pn06_told(st, s, C, nar):
    """BEAT 6  "I haven't told them."   frames 349-389 (41 f, 1.71 s), sky gold.
    Words: I 351, haven't 354, told 362, them 371. The pause after it (0.6 s) is the story's turn ("But I'm a
    redstoner").

    STORY: About 2.0 s. Over the narrator's shoulder at the fence, his thin arm and the glow of the redstone torch in
    the foreground. In the middle distance Zuri milks the cow and drinks again, the same loop. The narrator watches
    for a beat, then turns his head away toward the village and walks out of frame. The cow keeps looking at the
    lens.
    Cast: Narrator (Efe, slim-arm model), Zuri, one cow. Effects: redstone torch held and glowing, milk bucket and
    empty bucket held, drink arm pose, oak fence.

    MUST BE SEEN, ON WHICH WORD
      frame 349       the narrator's shoulder, thin arm and torch glow in the foreground, Zuri's loop going on
      "told" 362      he watches (head on Zuri); "them" 371 he turns his head away toward the village
      ~375-389        he walks out of frame (nothing important in the last 3 frames: he is gone by 386)
      the cow         keeps looking at the lens
    SHARED: none (narrator_fence, zuri_cow, cow_milk_target).
    NEIGHBOURS: before, pn05_milk; after, sq07_bench (he plants his torch at the bench: "But I'm a redstoner").
    MEASURED (the set builder, out/test/legday_set_b06_fence[_zones].png): over his right shoulder, 32 mm, his torch's
      glow soft in the foreground (y 68 %), Zuri drinking at the centre, the cow looking at the lens.
    NOW (stub): PN06_CAM (+ a drift), efe_pn with the torch at narrator_fence watching Zuri, turning on "them" and
      walking off west out of the frame; zuri_pn3 ends pn05's drink on 363 (the game's clock), taps the cow on 368
      and drinks again from 370; the cow at the lens. Heroes: Zuri.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.narrator("pn")
    a = C.put(efe, f0, "narrator_fence")
    zuri = C.actor("zuri", "pn3")
    C.put(zuri, f0, "zuri_cow", toward=(-9.7, 20.6))
    cow = C.cow("pn6")
    cp = C.P("cow_milk_target")
    cow.place(f0, cp, LC.yaw_to(cp, (-11.0, 20.5)))
    cow.look_at(f0, PN06_CAM["pos"], ease=0)
    zuri.look_at(f0, cow.eye_point(f0), ease=0)
    ends = C.T["pn05_milk"].at("fill") + 2 + DRINK            # 363: pn05's drink ends (the game's clock)
    animals.hand_item(zuri, "milk_bucket", f0, ends)
    zuri.drink(f0, ends - 4)
    animals.milk(zuri, ends + 5, ends, f1 + 1)                # 368: the tap
    zuri.drink(ends + 7)
    efe.look_at(f0, zuri.eye_point(f0), ease=0)
    turn = C.at(s, "them")
    efe.look_at(turn, (-14.0, 14.0, 1.5), ease=6)
    away = (a[0] - 2.4, a[1] - 0.9, a[2])
    efe.walk(turn + 4, [a, away], speed=2.4)
    st.use(s, efe, zuri, cow)
    C.cam(s, None, focus=zuri.head, **PN06_CAM)
    st.hero(s, "zuri", zuri)
    C.lights(s, "gold", near=(-11.0, 21.0, 1.0), radius=8.0)


def pn17_cows(st, s, C, nar):
    """BEAT 17  "Pillagers have crossbows, so everyone hid behind the cows."   frames 997-1102 (106 f, 4.42 s), sky
    gold. Words: Pillagers 999, have 1011, crossbows 1017, so 1043, everyone 1048, hid 1061, behind 1067, the 1076,
    cows 1078.

    STORY: About 3.0 s. Low shot through the cow pen fence: Steve, Kai, Zuri and Ari packed behind three cows in the
    sneak pose, only their heads showing over the cows' backs and all turned toward the road. One arrow is stuck in
    the fence post and a second thuds in beside it. The nearest cow looks at the lens, unbothered.
    Cast: Steve, Kai, Zuri, Ari, three cows. Effects: player sneak pose, two arrows stuck in a fence post, one
    arriving in shot, oak fence.

    MUST BE SEEN, ON WHICH WORD
      frame 997       already alive: the camera moving, heads turning, the first arrow stuck in the post
      "crossbows" 1017  the arrow in the post (the link to rd16's arrows: the story's risk)
      "hid" 1061 .. "cows" 1078   the second arrow THUDS in beside the first (it shakes 7 ticks), the four heads over
                      the cows' backs, all turned to the road; the nearest cow looking at the lens
    SHARED: none (hide_1..4, hide_cow_1..3_target, arrow_post_target).
    NEIGHBOURS: before, rd16_punch (the runners stopped by three arrows in the road: a jump of place); after,
      tp18_lever (the wall top).
    RISKS (story): "The sneak pose for players ... Fallback for the cows: the four stand upright behind the cows,
      filmed from low so the cows cover them to the neck." "Everyone ran out to punch them into hid behind the cows
      is a jump of place. The three arrows that stop the runners and the arrows in the fence post link the two
      shots. Fallback: carry the arrow sound over the cut and start the cow shot on the arrow in the post."
    FALLBACK CHOSEN (the set builder, measured): STANDING. Crouched, their eyes are below the cows' backs (1.375)
      from any camera under about 1.8; the story's own fallback "filmed from low so the cows cover them to the neck"
      is what the set was scouted for. A camera above 1.8 looking down over the cows could give the sneak: try it if
      you like, and keep whichever reads.
    MEASURED (the set builder, out/test/legday_set_b17_cows[_zones].png): from the road side through the east fence,
      1.1 high, 32 mm: heads above the cows' backs, the near cow at the lens, two arrows in the post (y 64 %: in the
      caption band); Zuri at x 82 % (the edge); front light (the sun behind the lens).
      THE REVIEW (technical): the arrows flew from due east, straight at this camera (12-15 degrees off its axis):
      only their fletching showed, two white X shapes on the post. Now they come from up the road to the NORTH-EAST
      (ARROW_DIR: where the patrol is; the wall stands between the pens and the patrol on the road, so they are the
      volley of the charge, rd16's arrows' sisters): the shafts stand 60-70 degrees off the lens axis. Confirm on a
      540x960 still that they read as arrows, and keep both above y 62 %.
    NOW (stub): PN17_CAM (+ a drift), the four standing at hide_1..4 looking east, three cows end to end at
      hide_cow_1..3_target facing north, the near one looking at the lens; one arrow stuck from frame 997, the second
      arriving on "hid" (1061). Heroes: the four.
    """
    f0, f1 = s.frame_start, s.frame_end
    cam = PN17_CAM["pos"]
    four = []
    for i, role in enumerate(("steve", "kai", "zuri", "ari")):
        p = C.actor(role, "pn17")
        C.put(p, f0, "hide_%d" % (i + 1))
        y = C.A["hide_%d" % (i + 1)][1]
        p.look_at(f0, (0.5, y + 3.0, 1.5), ease=0)
        four.append(p)
    cows = []
    for i in range(3):
        cp = C.P("hide_cow_%d_target" % (i + 1))
        c = C.cow("pn17c%d" % i)
        c.place(f0, cp, LC.yaw_to(cp, (cp[0], cp[1] + 1.0)))           # facing north, along the fence
        cows.append(c)
    cows[0].look_at(f0, cam, ease=0)
    for i, c in enumerate(cows[1:]):
        c.idle(f0, f1, seed=i + 3)
    post = C.P("arrow_post_target")
    C.stuck_arrow(s, (post[0], post[1] - 0.05, 0.92), ARROW_DIR)
    C.stuck_arrow(s, (post[0], post[1] + 0.1, 0.72), ARROW_DIR_2, frame=C.at(s, "hid"))
    st.use(s, *four, *cows)
    C.cam(s, None, focus=four[0].head, **PN17_CAM)
    st.hero(s, "hiding", *four)
    C.lights(s, "gold", near=(-10.0, 22.0, 1.0), radius=10.0)
