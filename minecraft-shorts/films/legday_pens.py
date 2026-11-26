"""Leg Day, sequence PENS: the chicken pen and the cow pen at the village edge, golden light. Beats 4, 5, 6, 17
(shots pn04_farms, pn05_milk, pn06_told, pn17_cows), sky "gold". One function per shot; the contract is in
films/legday_common.py (tags "pn...", C.actor / C.narrator / C.cow / C.hen, C.cam, C.lights, st.use / st.hero).

STATUS: SHOT by the pens director (from the lead's stubs). Each shot's docstring has its NOW (what it does) and
MEASURED (tools.legday_geo, the 540x960 / 16-sample stills with --zones, tools.legday_palette, the 270x480 / 6-sample
motion preview) lines. The sequence in one sentence each:
  pn04  from a block above eye height over the south fences: Kai among four hens, the cooked chicken at his mouth on
        "chicken" and the hens' heads up to him; between "farm" and "cow" the camera trucks east and pans to the cow
        pen; Zuri beside her cow tips the milk bucket up on "protein shakes" (drinking over the cut)
  pn05  the two-shot from the south: the bucket at her face on the cut, lowered EMPTY, one swing at the cow on
        "fill", FULL and straight back up on "up"; the cow's head round to the lens
  pn06  behind the narrator's right shoulder (his head and slim arm at the left, the torch glowing at his hand): the
        loop goes on (the tap on 368, up again on 370), on "them" his head turns to the village and he walks off left
  pn17  low through the east fence from the road side: the arrow in the post sharp (rack to the heads on "so"), the
        four heads over the backs of two cows standing rump to rump, the nearest cow looking at the lens; on "hid" the
        second arrow thuds in and all four duck (the sneak), on "cows" they peek up again one after another

THE PLACE (films/legday_set.py, "THE PENS"; engine.animals pen_set): west of the exit road, south of the anvil wall.
  chicken_pen  ring x -23..-17, y 20..26, gate (-20, 20) on its south side; inside x -22..-18, y 21..25
  cow_pen      ring x -14..-7, y 20..26, gate (-11, 20); inside x -13..-8, y 21..25
  Anchors used: zuri_cow (-11.3, 22.5) (Zuri in pn04-pn06); the facing of hide_1 (east) for the four in pn17. Places
  of this file's own (the set's anchors kai_chickens, cow_milk_target, narrator_fence, hide_1..4, hide_cow_*_target
  are not SHARED; each move is explained at its constant): KAI_04, COW_MILK, EFE_06, COWS_17, HIDERS_17, ARROW_1/2.
  house_e stands at x -9..-4, y 12..18 (south-east of the cow pen): no camera east of x -9.2 south of y 18.5.
  (tools/legday_pens_map.py prints the blocks round the pens from above.)
  A fence is 1.0 high as drawn: a cow looks over it, hens need the lens above the top rail (animals' notes).
THE ANVIL WALL (x -4..-2, y 27..60, 18 high) stands north-east of the cow pen: every view of the cow pen from the
  south-west has it behind the cows (pn04's end: the top 30 % of the frame, soft); from due south it is out of frame.
THE MILK LOOP IS ONE CLOCK (the review): a drink takes the game's 32 ticks = 38 frames (players.drink's default),
  the empty bucket is used on the cow at once after, and the full one goes straight up again: pn04 drink 265-303
  (the bucket empties on 303, inside pn05), "fill" 323 the tap, 325-363 the next drink (at her face on "up" 334,
  still drinking over the cut into pn06), 368 the next tap, from 370 the next drink (DRINK, DRINK_ENDS). Each twin of
  Zuri pre-rolls its drink 6 frames (zuri_pn2 / _pn3 are in no shot before), so the bucket is at her face on 299 and
  on 349, as on the frame before the cut.
  A DRINK FOLLOWS THE HEAD: players.drink poses the arm from the head's keys as they are when drink() is called; a
  look_at keyed after it leaves the bucket beside the ear (seen on a still: pn05 334). Key the head first.
  A HELD BUCKET IS A FLAT SPRITE: at rest in the hand it faces sideways (it reads from her side, an edge-on sliver
  from the front); at the mouth it faces forward (it reads within about 60 degrees of her facing). Hence ZURI_FACE
  (east-south-east, her right side to the lenses in the south) and ZURI_FACE_04 (south-east, for pn04's camera).
THE SKY: "gold" (sun due east, 27 degrees). pn04-pn06 look north to north-east (the sun 60-90 degrees off the axis,
  from the right); pn17 looks west from the road (the sun behind the lens: front light on the faces turned to the
  road, the set builder's choice, kept).
CAMERAS: pn05 / pn06 / pn17 are C.cam moves (pos -> pos1, ease_out: at speed on frame 1, the shot's own handheld).
  pn04 is _keyed_cam: Film.finalize bakes a camera's own location again from pos / pos1 and one ease, so a move with
  its own speed profile is a camera at the local origin (its keys = the handheld drift) parented to a keyed rig, and
  the aim an object target (engine.shots follows one). Both empties are named pn_rig_pn04_farms / pn_aim_pn04_farms.
TAGS (twins): one tag per shot (pn04: kai_pn, zuri_pn, hen_pn4h0..3, cow_pn4c0..1; pn05: zuri_pn2, cow_pn5; pn06:
  efe_pn, zuri_pn3, cow_pn6; pn17: steve/kai/zuri/ari_pn17, cow_pn17c0..2): held items never leak between shots.
LIGHT: C.lights(s, "gold", near=<point>, radius=8..10). No fill lights.
TOOLS (this sequence's own): tools/legday_pens_map.py (the blocks round the pens from above), tools/legday_pens_sheet.py
  (stills side by side). PREVIEW samples for render.py previews: 6 (legday_common.PREVIEW_SAMPLES).
"""

from engine import animals, shots
from films import legday_common as LC

# ---------------------------------------------------------------------------------------------------------------
# this sequence's own cameras, places and clocks
# ---------------------------------------------------------------------------------------------------------------
# beat 5: the two-shot from the south, 40 mm (the set's b05 at 50 mm had her at x 26 % and the cow's head at 82-90 %),
# a block above the pen's top rail, a slow push (at speed on 299)
PN05_CAM = dict(pos=(-10.6, 17.7, 1.75), pos1=(-10.62, 17.98, 1.73), target=(-10.85, 22.45, 1.1), lens=40.0,
                fstop=2.4)
# beat 6: behind the narrator's right shoulder from further back than the set's b06 (there his head was off the
# frame's left edge, x -67..14 %): his head and shoulder at the left, Zuri in the middle, the cow at the right
PN06_CAM = dict(pos=(-10.15, 17.2, 1.45), pos1=(-10.2, 17.4, 1.45), target=(-11.3, 22.3, 1.35), lens=30.0,
                fstop=2.4)
EFE_06 = (-11.05, 19.25)                  # the narrator at the cow pen's gate (narrator_fence is 0.5 east: from any
EFE_06_FACE = (-10.6, 22.4)               # lens behind his right shoulder Zuri stood right behind his head there)
# beat 17: from the road side through the east fence, low (1.1: the cows' backs cover the four to the chin), a slow
# push; the post with its arrows in the foreground, the row of four heads beyond, between two cows' heads
PN17_CAM = dict(pos=(-4.1, 22.7, 1.1), pos1=(-4.3, 22.7, 1.1), target=(-10.4, 22.48, 1.4), lens=26.0, fstop=2.8)
# THE COWS: a cow's head is as high as a face, and three cows end to end facing one way put a head every 1.65 blocks:
# there is room for two players between two heads, never four (hide_1..4 put Zuri behind cow 2's head). So the two
# in front of the four stand RUMP TO RUMP along the fence (cow B facing south, cow C north): 3.1 blocks of backs with
# no head, a head at each end (B's looks at the lens). Cow A stands north of C, facing north, its rump at the frame's
# right edge. (x, y, facing toward x, y)
COWS_17 = ((-8.7, 25.1, -8.7, 27.0), (-8.7, 22.0, -8.7, 20.0), (-8.7, 23.3, -8.7, 25.0))      # A, B, C
HIDERS_17 = (("steve", -10.05, 21.85), ("kai", -10.75, 22.45), ("zuri", -10.05, 23.05), ("ari", -10.75, 23.65))
ARROW_1 = (-6.55, 22.4, 0.93)             # the arrows' points on the east fence post's road face (the x -7, y 22
ARROW_2 = (-6.55, 22.6, 0.86)             # post: arrow_post_target), high on it: the arrows above the caption band
ARROW_DIR = (-0.55, -0.78, -0.30)         # the way the arrows flew: from up the road to the NORTH-EAST (where the
ARROW_DIR_2 = (-0.62, -0.72, -0.31)       # patrol is) into the east fence post: the shafts stand 60-70 degrees off
#                                           the lens axis and read as arrows (the first stub's flew from due east,
#                                           straight at the lens: two white X shapes, the fletching end-on)
COW_MILK = (-10.3, 23.25)                 # the milked cow (pn04-pn06): cow_milk_target (-10.0, 23.3) moved 0.3 west,
COW_MILK_FACE = (-11.0, 20.5)             # its head beside her right shoulder, facing south-south-west
DRINK = 38                                # frames of one drink: the game's 32 ticks (players.drink's default)
DRINK_ENDS = 303                          # the milk loop ON THE GAME'S CLOCK across pn04 -> pn05 -> pn06: the drink
#                                           begun in pn04 (265) empties the bucket on 303; tap on "fill" 323, drink
#                                           325-363, tap 368, drink from 370

# beat 4: Kai at the EAST side of the chicken pen; Zuri and her cow on their pn05 places (zuri_cow, cow_milk_target)
KAI_04 = (-18.35, 22.7)
KAI_04_FACE = (-16.9, 21.0)               # toward the track's start: the cooked chicken face-on at his mouth (in
#                                           profile it is edge-on, a brown stick: scouted, legday_pens_pn04_farms_214)
ZURI_FACE = (-9.6, 21.7)                  # Zuri at zuri_cow faces east-south-east in pn04-pn06: the sun, the cow's head
#                                           in front of her (the tap), and her RIGHT side (the bucket hand) to the lenses
#                                           in the south: a held bucket's sprite faces sideways, so it reads from her
#                                           side (frontal, the lowered empty bucket was an edge-on sliver: _pn05_312)
# the four hens round Kai: (x, y, body facing toward x, y): beside and behind him, their faces or profiles to the
# lens as they look up at him (a hen between him and the lens shows it its back)
HENS_04 = ((-19.45, 22.45, -18.35, 22.7), (-19.35, 23.6, -18.35, 22.7), (-17.4, 23.85, -18.35, 22.7),
           (-17.25, 22.85, -18.35, 22.7))
ZURI_FACE_04 = (-9.4, 20.6)               # in pn04 she faces south-east: the high camera is south-WEST of her, and the
#                                           bucket at her mouth is a flat sprite facing forward: from 80 degrees off her
#                                           facing (ZURI_FACE) it was an edge-on sliver (preview frames 269-298)
COW_B = (-8.6, 24.6, -11.0, 24.2)         # the second cow (pn04), at the back of the pen facing west
# THE TRACK: from a block above eye height (2.5) over the south fences, west -> east, the camera and its aim on keyed
# paths (_keyed_cam): slow on Kai and his hens through "chicken farm"; between "farm" and "cow" a truck of 3 blocks
# with a pan of about 50 degrees to the cow pen; slow on Zuri and her cow from "cow farm" to the end. WHY HIGH: from
# eye height or lower the top rail hides the hens and the anvil wall (x -4, y 27-60, 18 high) fills every view of the
# cow pen from the south-west (legday_pens_pn04_farms_250 / _281: grey stone over 60-85 % of the frame); from 2.5
# looking down on them the hens stand on the grass, the pen's grass is behind the faces and the wall is a strip at
# the top right (legday_pensvar_pn04_farms_214_v0 / _281_v0). WHY KEYED: a linear track was still between the pens on
# "cow" (the lead's note); with the camera on one ease the pan alone was 67 degrees in 28 frames.
PN04_PATH = (
    (205, (-17.1, 18.25, 2.5)),
    (228, (-16.55, 18.25, 2.5)),
    (254, (-13.4, 18.35, 2.5)),
    (299, (-12.25, 18.4, 2.5)),
)
PN04_AIM = (
    (205, (-18.4, 22.7, 0.9)),
    (228, (-18.1, 22.7, 0.9)),
    (254, (-11.2, 22.7, 0.9)),
    (299, (-10.95, 22.8, 0.85)),
)
PN04_LENS = (32.0, 2.6)


def _pchip(xs, ys, x):
    """Monotone cubic (Fritsch-Carlson) through (xs, ys) at x: no overshoot between keys, and the end slopes are
    the end segments' own (a path keyed this way is at speed on its first frame)."""
    n = len(xs)
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [d[0]] + [0.0] * (n - 2) + [d[-1]]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    i = max(j for j in range(n - 1) if xs[j] <= x)
    t = (x - xs[i]) / h[i]
    t2, t3 = t * t, t * t * t
    return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1]
            + (t3 - t2) * h[i] * m[i + 1])


def _keyed_empty(s, what, keys):
    """An empty "pn_<what>_<shot>" keyed on every frame of shot s (and one past its end) along keys = [(frame,
    point)], each coordinate a monotone cubic through them. Never rendered."""
    import bpy
    ob = bpy.data.objects.new("pn_%s_%s" % (what, s.name), None)
    s.film.collection.objects.link(ob)
    fr = [k[0] for k in keys]
    for f in range(s.frame_start, s.frame_end + 2):
        ob.location = [_pchip(fr, [k[1][i] for k in keys], f) for i in range(3)]
        ob.keyframe_insert("location", frame=f)
    shots._linearize(ob)
    ob.hide_render = True
    return ob


def _keyed_cam(C, s, path, aim, lens, focus=None, handheld=0.006):
    """A camera whose position AND aim follow keyed paths [(frame, point)] (monotone cubics: _keyed_empty), for a
    move that no single ease gives (pn04: slow on the hens, the truck and pan between the pens, slow on the cows).
    engine.shots bakes a camera's own location again in Film.finalize (pos -> pos1 with one ease), so the camera is
    C.cam'd at the local origin (its own keys = the handheld drift only, seeded by the shot name as always) and
    parented to a keyed rig; the aim is an object target, which engine.shots follows. Returns the spec C.cam used."""
    rig = _keyed_empty(s, "rig", path)
    spec = C.cam(s, None, focus=focus, handheld=handheld, pos=(0.0, 0.0, 0.0), target=_keyed_empty(s, "aim", aim),
                 lens=lens[0], fstop=lens[1])
    s.camera.parent = rig
    return spec


def _path_at(keys, f):
    """A keyed path's point at frame f (as _keyed_empty keys it; no handheld)."""
    fr = [k[0] for k in keys]
    return tuple(_pchip(fr, [k[1][i] for k in keys], f) for i in range(3))


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
      frame 205       the track already moving (at speed on frame 1), Kai among the hens
      "chicken" 213 .. "farm" 223   Kai lifting the cooked chicken to his face, the hens' heads turned up to him
      "cow" 246 .. "farm" 256       the move reaching the cow pen (the STORY'S ORDER: the cow farm on its words)
      "protein shakes" 269-292      Zuri tipping the milk bucket up to her face beside the cow
      both players in profile cheated toward the lens (C.to_lens: a face in strict profile shows a blank cheek)
    SHARED: none. Zuri on zuri_cow and her cow on COW_MILK, as in pn05 / pn06 (the three shots cut together).
    NEIGHBOURS: before, sq02_reps (the stone row); after, pn05_milk (Zuri and the cow, close).
    BEFORE (the stub): the set's b04 linear track at eye height (1.45) was between the pens on "cow" 246 (Kai at x
      -88 %, Zuri at 203 %); from eye height the top rail hid the hens and, at the cow pen, the anvil wall filled the
      frame (out/test/legday_pens_pn04_farms_250 / _281: 60-85 % grey stone); Kai frontal had the cooked chicken
      over his face, in profile it was an edge-on brown stick (legday_pens_pn04_farms_214, first two versions).
    NOW: PN04_PATH / PN04_AIM through _keyed_cam, 32 mm f/2.6, a block above eye height (2.5) over the south fences:
      205-228   a slow truck east (0.6 block) on Kai at KAI_04 (the chicken pen's east side), three-quarter to the
                lens, looking down at his four hens (HENS_04: beside and behind him, faces or profiles to the lens);
                209 the cooked chicken goes up, at his mouth on "chicken" 213 (players.eat, the game's bob), lowered
                231-235 (he lets go: the game allows it); the hens' heads come up to him 208-214, one after another,
                and stay on him (track)
      228-254   the truck (3.1 blocks) with a pan of about 50 degrees to the cow pen, a monotone cubic: the motion
                blur of the pen between them on 236-243; the focus pulls from Kai to Zuri from 234 (0.5 s)
      254-298   slow (1.2 blocks) on Zuri at zuri_cow facing south-east (ZURI_FACE_04), her head turned to the lens
                from 232, the milk bucket at her hip; on "for" 265 it goes up: the game's 38-frame drink, at her
                mouth from 269 ("protein"), still drinking over the cut (it ends on 303 in pn05); her cow beside her
                (COW_MILK, idle), a second cow behind (COW_B)
      hero "farmers" = Kai and Zuri (one hero: never both in the frame).
    MEASURED: tools.legday_geo: 214 Kai eyes x 49 % y 37 %, face 91 px, 4.8 blocks; 256 Zuri eyes x 49 % y 39 %, 92
      px; 282 Zuri x 44 % y 38 %, 98 px, her cow's eyes x 69 % y 43 %. Stills (540x960, 16 samples, zones):
      out/test/legday_pens_pn04_farms_214_zones.png (the chicken face-on at his mouth among the hens),
      _240_zones (mid-pan, a blur of the pen), _256_zones (Zuri, the full bucket at her hip, the cow), _282_zones
      (the white milk bucket at her mouth, the cow; the wall soft in the top 30 %). tools.legday_palette: every check
      ok, @214 hero x 41-56 % y 32-42 %, @282 hero x 33-55 % y 32-43 %, both 100 % inside; stone G/R 0.96 @282
      (the wall). Motion (270x480, 6 samples): Kai
      eats 213-231, the pan 230-246, Zuri arrives in the frame on 246 and is centred by 250.
    """
    f0, f1 = s.frame_start, s.frame_end
    kai = C.actor("kai", "pn")
    C.put(kai, f0, KAI_04, toward=KAI_04_FACE)
    zuri = C.actor("zuri", "pn")
    C.put(zuri, f0, "zuri_cow", toward=ZURI_FACE_04)
    hens = []
    for i, (x, y, tx, ty) in enumerate(HENS_04):
        h = C.hen("pn4h%d" % i)
        h.place(f0, (x, y, 0.0), LC.yaw_to((x, y), (tx, ty)))
        hens.append(h)
    cow = C.cow("pn4c0")
    cow.place(f0, C.stand(COW_MILK), LC.yaw_to(COW_MILK, COW_MILK_FACE))
    cow_b = C.cow("pn4c1")
    cow_b.place(f0, (COW_B[0], COW_B[1], 0.0), LC.yaw_to(COW_B[:2], COW_B[2:]))
    lift = C.at(s, "chicken") - 4                 # 209: the cooked chicken at his mouth on "chicken" 213
    down = C.at(s, "farm") + 8                    # 231: lowered (he stops eating: the game lets go), his face again
    # Kai: looking down at his hens on the cut, then the chicken up to his mouth through "chicken farm", then back
    # down to the hens as the camera pans away
    kai.hold("cooked_chicken")
    kai.look_at(f0, (KAI_04[0] - 0.4, KAI_04[1] - 0.9, 0.5), ease=0)
    kai.look_at(lift - 2, C.to_lens(kai, lift, (KAI_04_FACE[0], KAI_04_FACE[1], 1.7), _path_at(PN04_PATH, lift),
                                     degrees=30), ease=6)
    kai.eat(lift, down)
    kai.look_at(down + 4, (KAI_04[0] - 0.9, KAI_04[1] + 0.6, 0.6), ease=8)
    # the hens peck-look at the ground, then their heads come up to him as the chicken goes up (one after another)
    for i, h in enumerate(hens):
        x, y = HENS_04[i][:2]
        h.look_at(f0, ((x + KAI_04[0]) / 2.0, (y + KAI_04[1]) / 2.0, 0.0), ease=0)
        h.look_at(lift - 1 + 2 * i, kai, ease=5)
        h.track(lift + 5 + 2 * i, f1, kai, step=4, ease=4)
    # Zuri with her milk bucket beside the cow, the drink on "protein shakes" on the game's clock (265-303)
    drink = DRINK_ENDS - DRINK                    # 265
    zuri.hold("milk_bucket")
    zuri.look_at(f0, cow, ease=0)                 # (out of the frame until the pan)
    turn = C.at(s, "and") - 10                    # 232: her head off the cow and round toward the lens before the pan
    zuri.look_at(turn, C.to_lens(zuri, turn, (ZURI_FACE_04[0], ZURI_FACE_04[1], 1.55),
                                 _path_at(PN04_PATH, C.at(s, "cow")), degrees=35), ease=8)
    zuri.drink(drink)                             # at her mouth from 269 ("protein"), lowered on 303 (in pn05)
    cow.look_at(f0, zuri, ease=0)
    cow.idle(f0, f1, seed=2)
    cow_b.idle(f0, f1, seed=5)
    st.use(s, kai, zuri, *hens, cow, cow_b)
    _keyed_cam(C, s, PN04_PATH, PN04_AIM, PN04_LENS, focus=kai.head)
    s.focus(zuri.head, at_s=s.film.seconds(C.at(s, "and") - 8), rack_s=0.5)     # the pull to Zuri with the pan
    st.hero(s, "farmers", kai, zuri)              # one hero: Kai until the pan, Zuri after it (never both in frame)
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
    SHARED: none (zuri_cow, COW_MILK: the same places as pn04 and pn06).
    NEIGHBOURS: before, pn04_farms; after, pn06_told (the same loop over the narrator's shoulder).
    RISKS (story): "the empty and full bucket are two small held sprites. Stage the bucket toward the lens in the
      portrait and make the swap on the tap. Fallback: put Kai behind her in the frame eating a cooked chicken, the
      one who is actually being fed." A flat item lies along the hand: edge-on from the side, readable from behind or
      above (CONTRACT).
    MEASURED (the set builder, out/test/legday_set_b05_milk[_zones].png): Zuri and the cow both toward the lens over
      the fence, 50 mm; the bucket sits low (y 65 %, in the caption band): raise it or the camera. THE LEAD'S SCOUT
      of the stub (out/test/legday_scout_pn05_milk_324[_zones].png, on "fill"): the tap reads (the bucket blurred
      in the swing at the centre), Zuri's face y 35-48 %; the cow's head at the right edge (x 82-90 %): reframe.
    NOW: PN05_CAM, 40 mm f/2.4 from the south a block above the top rail (1.75), a slow push (0.28 block, ease_out);
      Zuri (zuri_pn2) on zuri_cow facing east-south-east (ZURI_FACE: her right side, the bucket hand, toward the
      lens), her head cheated 35 degrees to the lens; the cow (cow_pn5) on COW_MILK facing south-south-west, its head
      beside her right shoulder.
      299-303   the milk bucket at her mouth on the cut (the drink pre-rolled 6 frames), lowered from 299: EMPTY from
                303 (animals.milk's bucket), a dark bucket at her hip on "doesn't" 309
      307-321   her head round to the cow; the cow on her, one glance away (idle)
      321-323   one arm swing at the cow's head: on "fill" 323 the milk bucket again (animals.milk)
      325-363   straight back up (her head turned to the lens first: the drink follows the head's keys), at her mouth
                on "up" 334, drinking over the cut (pn06 ends it on 363); the cow's head round to the lens 324-332
      heroes zuri, cow.
    MEASURED: tools.legday_geo 312: Zuri eyes x 31 % y 38 %, face 114 px; the cow's eyes x 66 % y 46 %, 112 px; 334:
      the cow 0.2 degrees off the lens (head x 54-83 %). Stills: out/test/legday_pens_pn05_milk_299_zones.png (the
      bucket at her mouth), _312_zones (the empty bucket at her hip, she looks at the cow), _324_zones (the swing:
      her arm at the cow's face; the white milk bucket flashes there on 321-323 in the motion preview), _334_zones (the full bucket at
      her mouth, the cow into the lens). tools.legday_palette @334: every check ok (zuri x 19-44 %, cow x 55-81 %,
      100 % inside). Motion: 299-348 all read in order (lowered, look, swing, up, the cow's turn).
    """
    f0, f1 = s.frame_start, s.frame_end
    zuri = C.actor("zuri", "pn2")
    C.put(zuri, f0, "zuri_cow", toward=ZURI_FACE)
    cow = C.cow("pn5")
    cow.place(f0, C.stand(COW_MILK), LC.yaw_to(COW_MILK, COW_MILK_FACE))
    cam = PN05_CAM["pos"]
    fill = C.at(s, "fill")                        # 323
    ahead = C.to_lens(zuri, f0, (ZURI_FACE[0], ZURI_FACE[1], 1.55), cam, degrees=35)
    zuri.look_at(f0, ahead, ease=0)
    empty = DRINK_ENDS                            # 303: pn04's drink ends (the game's clock): the bucket is empty
    animals.hand_item(zuri, "milk_bucket", f0, empty)
    zuri.drink(f0 - 6, empty - 4)                 # (pre-rolled: the bucket already AT her face on 299, as on 298)
    zuri.look_at(empty + 4, cow, ease=8)          # she looks at the cow with the empty bucket ("doesn't" 309) ...
    animals.milk(zuri, fill, empty, f1 + 1)       # ... one swing at it on "fill": a milk bucket again
    zuri.look_at(fill + 1, ahead, ease=6)         # (the head BEFORE the drink: the drink pose follows the head's keys)
    zuri.drink(fill + 2)                          # 325-363: straight back up, at her face on "up" 334
    # the cow: on Zuri, a glance away while she lowers the bucket, then its head round to the lens after the tap
    cow.look_at(f0, zuri, ease=0)
    cow.idle(f0, fill - 4, seed=7)
    cow.look_at(fill + 1, cam, ease=8)            # looking into the lens from 332, before "up" 334
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
    SHARED: none (EFE_06, zuri_cow, COW_MILK).
    NEIGHBOURS: before, pn05_milk; after, sq07_bench (he plants his torch at the bench: "But I'm a redstoner").
    MEASURED (the set builder, out/test/legday_set_b06_fence[_zones].png): over his right shoulder, 32 mm, his torch's
      glow soft in the foreground (y 68 %), Zuri drinking at the centre, the cow looking at the lens.
    BEFORE (the stub): from the set's b06 his head was off the frame's left edge (x -67..14 %) and the cow's head at
      the right edge (x 82 %); at narrator_fence, any lens behind his right shoulder had Zuri right behind his head.
    NOW: PN06_CAM, 30 mm f/2.4 behind his right shoulder at 1.45, a slow push (0.2 block); the narrator (efe_pn, the
      glowing redstone torch in his right hand) at EFE_06, the cow pen's gate, facing Zuri and the cow; his head and
      shoulder big and soft at the left, his slim right arm with the torch at the lower left (its glow at y 66-72 %,
      in the caption band: atmosphere, not a hero); Zuri (zuri_pn3) in the middle, the cow (cow_pn6) at the right
      looking into the lens all shot. The focus on Zuri.
      349-363   Zuri drinking (pre-rolled: at her mouth on the cut), lowered by 363 (pn05's drink, the game's clock)
      361-368   her head to the cow, the tap on 368 (animals.milk), back up from 370 (the head first)
      349-369   he watches her; on "them" 371 (369-375) his head turns over his right shoulder toward the village: his
                face in profile to the lens; from 374 he walks off south-south-west at the game's walk (4.3 blocks/s),
                past the lens on its left (1.0 block clear of it): his head is out of the frame by 381, all of him by 384
      heroes zuri, narrator.
    MEASURED: tools.legday_geo 362: his head x -5..40 % (eyes 20 %), 2.1 blocks; Zuri eyes x 51 % y 46 %, 75 px; the
      cow's eyes x 75 %, 0.4 degrees off the lens; 375: his face 48 degrees off the lens (the turn). Stills:
      out/test/legday_pens_pn06_told_362_zones.png (watching), _375_zones (the turn: his eyes to the lens in the
      blur of the head turn, Zuri drinking again). tools.legday_palette @362: every check ok, zuri x 44-59 % 100 % inside, narrator x 1-38 %
      79 % inside (an over-the-shoulder head: the frame's edge cuts it, as it should). Motion: the loop and the turn
      read; the walk re-timed after the first preview (it left a sliver of him in the frame on 386): now his face
      in profile on 372-376, a sliver of his shoulder at the left edge on 381, gone from 384 (preview frames).
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.narrator("pn")
    a = C.put(efe, f0, EFE_06, toward=EFE_06_FACE)
    zuri = C.actor("zuri", "pn3")
    C.put(zuri, f0, "zuri_cow", toward=ZURI_FACE)
    cow = C.cow("pn6")
    cow.place(f0, C.stand(COW_MILK), LC.yaw_to(COW_MILK, COW_MILK_FACE))
    cam = PN06_CAM["pos"]
    cow.look_at(f0, cam, ease=0)                  # it keeps looking at the lens (as at the end of pn05)
    ahead = C.to_lens(zuri, f0, (ZURI_FACE[0], ZURI_FACE[1], 1.55), cam, degrees=35)
    zuri.look_at(f0, ahead, ease=0)
    ends = C.T["pn05_milk"].at("fill") + 2 + DRINK            # 363: pn05's drink ends (the game's clock)
    animals.hand_item(zuri, "milk_bucket", f0, ends)
    zuri.drink(f0 - 6, ends - 4)                              # (pre-rolled: at her face on 349, as on 348)
    zuri.look_at(ends - 2, cow, ease=6)
    animals.milk(zuri, ends + 5, ends, f1 + 1)                # 368: the tap
    zuri.look_at(ends + 6, ahead, ease=6)                     # (the head first: the drink pose follows it)
    zuri.drink(ends + 7)                                      # 370: and up again
    # the narrator: watching her over the fence, then on "them" his head round to the village (south-east, over his
    # right shoulder: his face to the lens) and he walks off toward it, out past the lens on the left
    efe.look_at(f0, zuri, ease=0)
    turn = C.at(s, "them")                                    # 371
    efe.look_at(turn - 2, (a[0] + 2.5, a[1] - 3.0, 1.5), ease=6)
    away = [a, (a[0] - 0.1, a[1] - 0.9, a[2]), (a[0] - 0.3, a[1] - 3.4, a[2])]   # 1.0 clear of the lens
    efe.walk(turn + 3, away, speed=4.3)                       # the game's walk: out of the frame by 384
    st.use(s, efe, zuri, cow)
    C.cam(s, None, focus=zuri.head, **PN06_CAM)
    st.hero(s, "zuri", zuri)
    st.hero(s, "narrator", efe)
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
    SHARED: none (HIDERS_17, COWS_17, ARROW_1/2 on arrow_post_target's post).
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
    BEFORE (the stub): the arrows at x 80-100 % and soft; Zuri's eyes at x 83 % and behind cow 2's head (three cows
      end to end facing north put a head every 1.65 blocks, as high as a face).
    NOW: PN17_CAM, 26 mm f/2.8 from the road side at 1.1 (the cows' backs cover the four to the chin: the story's
      fallback "filmed from low so the cows cover them to the neck"), a slow push (0.2 block, ease_out).
      the cows   COWS_17: B (cow_pn17c1) and C (c2) RUMP TO RUMP along the east fence in front of the four: 3.1 blocks
                 of backs with no head; B's head at the left looks into the lens all shot (the nearest cow,
                 unbothered); C's head at the right edge and A (c0, north of C) idle
      the four   HIDERS_17 in two staggered rows, heads side by side over the backs, each turned up the road to the
                 north-east (where the volleys come from), re-aiming twice (alive)
      997-1036   the focus on the arrow in the post (ARROW_1: a shaft with its fletching, flown from the north-east),
                 the link to rd16's arrows; on "so" (1036-1048) the focus pulls to the heads
      1061       "hid": the second arrow thuds in beside the first (hostiles.stick, shaking 7 ticks, soft in the
                 foreground) and all four duck behind the cows 1062-1063 (the sneak), heads down
      1077-1083  "cows": they peek up again one after another (sneak off, 2 frames apart), heads up the road
      hero "hiding" = the four.
    MEASURED: tools.legday_geo 1012 / 1092: Steve x 36 %, Kai 50 %, Zuri 62 %, Ari 73 % (eyes, y 47-48 %), faces 52-61
      px, none blocked; cow B's eyes x 15 % (head 4-29 %), 32 degrees off the lens; ducked on 1068 their eyes are
      blocked by the cows' bodies. The arrows: points x 32-43 %, y 59-61 %, the first shaft rising to x 52 %, y 55 %.
      Stills: out/test/legday_pens_pn17_cows_1012_zones.png (the arrow sharp, the four heads, the cow into the lens),
      _1064_zones (ducked, the second arrow shaking), _1092_zones (peeking again). tools.legday_palette @1092: hero
      x 30-80 %, y 43-49 %, 100 % inside; planks ok. Front light (the sun behind the lens), kept.
    """
    f0, f1 = s.frame_start, s.frame_end
    cam = PN17_CAM["pos"]
    hid = C.at(s, "hid")                                                # 1061: the second arrow thuds in
    cows_word = C.at(s, "cows")                                         # 1078
    four = []
    for i, (role, x, y) in enumerate(HIDERS_17):
        p = C.actor(role, "pn17")
        C.put(p, f0, (x, y), yaw=C.yaw("hide_1"))                      # facing east (the road)
        four.append(p)
    cows = []
    for i, (x, y, tx, ty) in enumerate(COWS_17):
        c = C.cow("pn17c%d" % i)
        c.place(f0, (x, y, 0.0), LC.yaw_to((x, y), (tx, ty)))
        cows.append(c)
    # the four: heads turned up the road to the north-east, where the volleys come from, each re-aiming now and then
    # (alive); on "hid" all four duck behind the cows (the sneak, a frame apart), and on "cows" they peek up again
    for i, p in enumerate(four):
        y = HIDERS_17[i][2]
        p.look_at(f0, (0.5, y + 4.0, 1.6), ease=0)
        p.look_at(f0 + 14 + 9 * i, (0.5, y + 6.5, 1.9), ease=8)
        p.look_at(f0 + 40 + 7 * i, (0.0, y + 3.0, 1.4), ease=10)
        p.sneak(hid + 1 + (i % 2) + i // 2)
        p.look_at(hid + 3, (0.0, y + 1.5, 0.9), ease=4)               # heads down
        up = cows_word - 1 + 2 * i
        p.sneak(up, False)
        p.look_at(up, (0.5, y + 4.5, 1.7), ease=5)                    # peeking up the road again
    # cow B (the nearest, the south end) looks into the lens, unbothered; C and A idle
    cows[1].look_at(f0, cam, ease=0)
    cows[2].idle(f0, f1, seed=3)
    cows[0].idle(f0, f1, seed=4)
    C.stuck_arrow(s, ARROW_1, ARROW_DIR)
    C.stuck_arrow(s, ARROW_2, ARROW_DIR_2, frame=hid)
    st.use(s, *four, *cows)
    C.cam(s, None, focus=ARROW_1, **PN17_CAM)
    s.focus(four[1].head, at_s=s.film.seconds(C.at(s, "so") - 7), rack_s=0.5)    # the arrow, then the heads
    st.hero(s, "hiding", *four)
    C.lights(s, "gold", near=(-9.5, 22.5, 1.0), radius=10.0)
