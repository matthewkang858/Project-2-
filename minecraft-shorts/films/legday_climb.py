"""Leg Day, sequence CLIMB: the anvil wall seen from the road and from its stair: the daily climb with the anvils
(beats 11, 12, golden) and its exact repeat before dark (beats 22, 23, dusk). Shots cl11_climb, cl12_legday,
cl22_dusk, cl23_legday. One function per shot; the contract is in films/legday_common.py (tags "cl...", C.actor,
C.cam, C.lights, st.use / st.hero).

STATUS: STUBS written by the lead (the SHARED cameras, the climbers placed and climbing, the anvils in their hands)
so the film builds and renders end to end. Every docstring carries the beat, its words with their frames, what must
be seen on which word, the neighbours, the risks and the measured notes. The acting is yours.

WHY ONE SEQUENCE FOR BOTH SKIES: cl22 / cl23 must be recognised as cl11 / cl12 again ("Keep lens, height and step
count identical and change only the light": the story's risk). One director makes both, from ONE camera each
(CLIMB_CAM and LEGS_CAM below: they start as the lead's CAMS "climb" / "legs"; yours to change, as long as each
stays ONE constant used by both of its shots) and ONE staging function each (_climb, _legs below): the dusk shots
call the same function with the same constants. Change a constant and both change together.
MEASURED ON THE STUB (tools.legday_palette, the heroes): cl11 704 the climbers x 27-47 %, y 23-29 % (inside; small
and bunched, 1.3 steps apart); cl12 755 the legs x 1-55 %, y 12-98 % (Kai, the nearer, fills the lower frame: TO
FIX, by the staging or LEGS_CAM).

THE PLACE (films/legday_set.py, "THE ANVIL WALL"): the wall's road face (x = -1) looks EAST into the morning sun; the
stair: 18 stone-brick stairs on the road face at its south end, ascending north, step k at (-1, 27 + k, k), the top
step (-1, 44, 17) level with the walkway (z 18); one wide, no rail, open air on its east side. stair_z(y) (LS) = the
game's half-step heights (front half k + 0.5, back half k + 1). WALKING UP: Player.walk on a 3D polyline measures its
speed along the 3D line, so half-step nodes either float the feet between treads (the set's paths "stair_climb" /
"stair_ramp": up to a quarter or half block) or stall at every riser. The stubs walk the straight ramp (slope 1,
within a quarter block of every tread) and key the root's delta_location z per frame to put the feet exactly ON the
treads (_on_treads: a half-block pop in one frame at each riser, as the game steps up). Keep it or do better.
Anchors stair_foot (-0.5, 26.3), stair_top (-0.5, 44.75, 18), wall_top_south.
The shelf: planks at (0, 46..57, 17) two blocks out from the face, anvils on them at (0, y, 18): the lead's SHELF
puts eight of the day set (planks 3..10) on it in cl11 / cl12 and eight of the DUSK set in cl22 / cl23 (do not st.use
anvils). The face lanterns hang at (-1, 31, 9) (-1, 37, 14) (-1, 49, 11) (-1, 55, 11) (group legday_wall).
THE SKIES: cl11 / cl12 "gold" (the face lit by the sun in the east); cl22 / cl23 "dusk" (the sun down in the west,
  behind the wall: the face lit by its lanterns at 1.4, an indigo sky with the first stars). The cut INTO cl22 dips
  to black (films/legday.py DIPS: black on 1373 and 1374, back by 1377); the lead re-arms the row inside the black
  (the planks are OUT again from 1375: C.rearm). Nothing important on 1370-1376.
THE PACE (after review): the story bounds the climb: "a step shorter than seven frames hops: use a slow climb". The
  first stub read "slow" as a quarter of a walk (0.84 blocks/s, a step every 29 frames, legs +-19 degrees: the legs
  of "leg day" barely moved). Now CLIMB_PACE = 3.0 blocks/s HORIZONTAL = a step every 8 frames (the story's
  minimum is 7; a vanilla walk is 5.6), walked along the straight ramp at 3.0 x 1.414 = 4.24 blocks/s. The legs then
  swing about +-68 degrees, a full walk (engine.players measures the limb speed along the 3D ramp; the game uses the
  horizontal speed, which would give about +-50: the engine's is the bigger, more readable "pumping"). Keep every
  step at 7 frames or more, and keep the legs moving like a walk.
THE REPEATS (after review): each walk is planned over a FIXED length (CLIMB_FRAMES / LEGS_FRAMES, not the shot's)
  and at speed at both ends (ramp (False, False): nobody slows down for the cut), so cl22's first 70 frames are
  cl11's frame for frame and cl23 is cl12. The narration was re-spoken so that the words of cl23 fall on the same
  shot frames as cl12's (They +2, call +7, it +13, leg +16, day +22 in BOTH): key a word-synced action from cl12's
  offsets (C.T["cl12_legday"].at("leg") - C.T["cl12_legday"].frame_start) and apply the same offset in cl23.
THE ANVILS IN HAND: whole in the morning (C.carry_anvil(p)), CHIPPED at dusk (C.carry_anvil(p, dusk=True)): the
  dusk anvils are the same ones that fell (legday_common THE CHIPPED ANVILS); the shelf's dusk set is chipped too.
TAGS (twins): steve / kai / zuri / ari _cl (cl11), _cl2 (cl12), _cl3 (cl22), _cl4 (cl23): each holds an anvil
  (C.carry_anvil), placed on its shot's first frame (no pre-roll).
LIGHT: C.lights(s, "gold" | "dusk", near=(-1.0, 40.0, 8.0), radius=26.0) (the stair's lanterns and the face's).
PREVIEW samples for render.py previews: 7 (legday_common.PREVIEW_SAMPLES).
"""
from engine import shots
from films import legday_common as LC
from films import legday_set as LS

# ---------------------------------------------------------------------------------------------------------------
# the staging, ONE constant each for the gold shot and its dusk repeat
# ---------------------------------------------------------------------------------------------------------------
# THE TWO CAMERAS OF THE REPEATS: ONE constant each, used by the gold shot AND its dusk repeat. They start as the
# lead's CAMS "climb" / "legs" (legday_common); they are THIS sequence's to change (both shots change together:
# tools.legday_state checks that cl22 = cl11 and cl23 = cl12, cameras included, frame for frame).
CLIMB_CAM = dict(LC.CAMS["climb"], pos1=(5.6, 25.6, 0.85), target1=(-0.94, 42.4, 8.5))   # + a slow creep in,
#                                                       planned over CLIMB_FRAMES (_repeat_cam: the same rate in both)
LEGS_CAM = dict(LC.CAMS["legs"])                       # its track planned over LEGS_CAM_FRAMES
LEGS_CAM_FRAMES = 45
# NO HANDHELD IN THE REPEATS: engine.shots draws the handheld drift from FILM time (frame / fps), so the same seed
# gives another drift 700 frames later (measured: 5.6 mm and 8.7 mm apart). The moves carry the life (linear: at
# speed on frame 1), planned per frame so a 70- and a 73-frame shot share their first 70 frames.
CLIMB_SEED = 31               # (kept for a director who adds a drift of his own that repeats; unused by the stub)
LEGS_SEED = 47
CLIMB_PACE = 3.0              # blocks / s HORIZONTAL up the stair: one step every 8 frames (the story: never under
#                               7); walked along the slope-1 ramp at CLIMB_PACE * sqrt(2) (legs about +-68 degrees)
CLIMBERS = (("steve", 4.0), ("kai", 5.3), ("zuri", 6.6), ("ari", 7.9))   # (role, step: y = 27 + step) on the
#                                                       shot's first frame, 1.3 apart: Ari reaches step 17.4 (of 17.7)
#                                                       on CLIMB_FRAMES, nobody tops out inside cl22's 73 frames
CLIMB_FRAMES = 76             # the length every climb walk is planned for (>= cl22's 73): cl11 = cl22's first 70
LEGGERS = (("steve", 5.6), ("kai", 4.4))       # cl12 / cl23: the camera tracks up the stair beside them (LEGS_CAM,
#                                                0.4 block/s slower): Steve 2.0 steps ahead of the lens, his legs in
#                                                the frame's middle all along; Kai 1.2 behind him, entering the frame
#                                                beside the lens by "leg" (+16)
LEGS_FRAMES = 48              # the length of the legs walk (>= 45)


def _ramp_z(y):
    """The straight ramp up the stair (slope 1): never more than a quarter block off the game's half steps."""
    return (y - LS.STAIR_Y0) + 0.25


def _on_treads(p, f0, f1):
    """Put the feet of a player walking the straight ramp exactly ON the treads: the root's delta_location z
    (unused by the engine) keyed CONSTANT on every frame to LS.stair_z(y) - the ramp's z. The step up is a pop of
    half a block in one frame, as the game's step-up (the player's position, not his legs). Back to 0 after f1."""
    root = p.root
    for f in range(int(f0), int(f1) + 1):
        pos = p.pos_at(f)
        dz = LS.stair_z(pos.y) - pos.z if LS.STAIR_Y0 <= pos.y <= LS.STAIR_Y0 + LS.STEPS else 0.0
        root.delta_location[2] = dz
        root.keyframe_insert("delta_location", index=2, frame=f)
    root.delta_location[2] = 0.0
    root.keyframe_insert("delta_location", index=2, frame=int(f1) + 1)
    for fc in shots.fcurves_of(root):
        if fc.data_path == "delta_location":
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def _climbers(C, s, tag, cast, frames, dusk):
    """Players of `cast` [(role, step)] placed on the stair at their steps on s's first frame, an anvil in hand
    (chipped at dusk: C.carry_anvil), climbing at CLIMB_PACE (horizontal) over a walk planned for `frames` frames
    (a constant: the gold shot and its dusk repeat get the same walk), at speed on both ends, their feet on the
    treads (_on_treads) for the shot's frames. Returns them."""
    f0, f1 = s.frame_start, s.frame_end
    top = LS.STAIR_Y0 + LS.STEPS - 0.3
    out = []
    for role, step in cast:
        p = C.actor(role, tag)
        y0 = LS.STAIR_Y0 + step
        y1 = y0 + CLIMB_PACE * frames / 24.0
        if y1 > top:
            raise ValueError("%s_%s would top out (step %.1f): lower his start" % (role, tag, y1 - LS.STAIR_Y0))
        a, b = (-0.5, y0, _ramp_z(y0)), (-0.5, y1, _ramp_z(y1))
        p.place(f0, a, LC.yaw_to(a, b))
        C.carry_anvil(p, dusk=dusk)
        p.walk(f0, [a, b], speed=CLIMB_PACE * 2 ** 0.5, ramp=(False, False))
        _on_treads(p, f0, f1)
        out.append(p)
    return out


def _repeat_cam(C, s, spec, frames, focus=None):
    """A camera whose move runs at the same rate in a shot and its repeat: spec's move (pos -> pos1, target ->
    target1) is planned over `frames` frames and cut to this shot's length (linear: the first N frames of two shots
    of different lengths are the same camera). No handheld (see above)."""
    c = dict(spec)
    k = (s.frame_end - s.frame_start + 1) / float(frames)
    for a, b in (("pos", "pos1"), ("target", "target1")):
        if b in c:
            c[b] = tuple(p + (q - p) * k for p, q in zip(c[a], c[b]))
    return C.cam(s, None, focus=focus, handheld=0, ease="linear", **c)


def _climb(st, s, C, tag, sky):
    """cl11 and cl22: CLIMB_CAM, the four climbers, the lights of the sky."""
    cl = _climbers(C, s, tag, CLIMBERS, CLIMB_FRAMES, dusk=(sky == "dusk"))
    st.use(s, *cl)
    _repeat_cam(C, s, CLIMB_CAM, CLIMB_FRAMES)
    st.hero(s, "climbers", *cl)
    C.lights(s, sky, near=(-1.0, 40.0, 8.0), radius=26.0)
    return cl


def _legs(st, s, C, tag, sky):
    """cl12 and cl23: LEGS_CAM, Steve and Kai climbing past the lens."""
    cl = _climbers(C, s, tag, LEGGERS, LEGS_FRAMES, dusk=(sky == "dusk"))
    st.use(s, *cl)
    _repeat_cam(C, s, LEGS_CAM, LEGS_CAM_FRAMES, focus=cl[0].parts["leg_r"])
    st.hero(s, "legs", *[p.parts[k] for p in cl for k in ("leg_r", "leg_l")])    # the LEGS (a Character = its head)
    C.lights(s, sky, near=(-1.0, 33.0, 6.0), radius=16.0)
    return cl


def cl11_climb(st, s, C, nar):
    """BEAT 11  "Every day they carry twelve anvils up the wall."   frames 669-738 (70 f, 2.92 s), sky gold.
    Words: Every 671, day 677, they 683, carry 686, twelve 695, anvils 705, up 717, the 720, wall 723.

    STORY: About 3.0 s. Low angle from the road: a tall stone wall beside the road into the village with a long stair
    up its end. Steve, Kai, Zuri and Ari climb the stairs in a staggered line, each holding an anvil. Along the top,
    eight anvils already stand on a shelf of oak planks that hangs out over the road, receding against the gold sky.
    Cast: Steve, Kai, Zuri, Ari. Effects: four anvils as held items, eight anvils as blocks on the plank shelf, tall
    stone wall with a long stair, walking up stairs.

    MUST BE SEEN, ON WHICH WORD
      frame 669       the four already climbing (placed on 669, walking at speed from it), the camera drifting
      "carry" 686 .. "anvils" 705   the anvils in their hands (held items: they read from the side and below)
      "wall" 723      the whole height of the wall, the stair, the shelf hanging out over the road against the sky
      the shelf       EIGHT anvils on it (the lead's SHELF "eight": planks 3..10; the 12th piston at the north end is
                      not there yet: the narrator sets it in tp13); 8 up + 4 carried = 12
    SHARED: CLIMB_CAM (= cl22_dusk exactly; no handheld: _repeat_cam), CLIMBERS / CLIMB_PACE / CLIMB_FRAMES (=
      cl22).
    NEIGHBOURS: before, sq10_cheating (the square); after, cl12_legday (on the stair, their legs).
    RISKS (story): "A wall 18 blocks high throws a long shadow at golden hour and is hard to hold in one frame with the
      road. Build it so its road face looks at the sun and shoot the wall shots tall and low." (done: the face looks
      east into the sun). "Walking up stairs with a held anvil is a new move, and a step shorter than seven frames
      hops. Use a slow climb ... Fallback: a ground-level side view in which the climbers cross the frame behind the
      stair's edge, seen from the waist up."
    MEASURED (the set builder, out/test/legday_set_b11_climb[_zones].png and the alternative _b11e_climb_east): from
      the road south-east (b11, 28 mm): the face, the stair, four climbers, the face lanterns all read; THE SHELF'S
      ANVILS SHOW ONLY AS A SLIVER over the planks from below. From across the road (b11e, 18 mm): the anvils read,
      the climbers small at the left edge. The lead's scouting of the choice: see films/legday_common.py CAMS
      "climb". THE LEAD'S SCOUT (the stubs, 540x960, 16 samples): out/test/legday_scout_cl11_climb_704.png and
      legday_scout_cl22_dusk_1408.png (the same frame + 35 under both skies: they read as two times of day; re-rendered after review: _1408);
      a middle camera from (11.0, 28.0, 0.9), 24 mm (legday_scout_climbvar_cl11_climb_704_v0.png) made the climbers
      smaller, still hid the anvils behind their planks and put meadow tufts in the lens: not adopted. In the stub
      In the first stub Steve (step 3.75, walking at a quarter pace) was cut by the left edge on 704. If you need
      another camera for this shot, it changes cl22 too: say so in your result (a shared camera).
    THE PACE (the review): a step every 8 frames (CLIMB_PACE 3.0), not 29: see the module docstring.
    NOW (stub): CLIMB_CAM (b11 + a slow linear creep), the four from steps 4.0 / 5.3 / 6.6 / 7.9 climbing a step every 8 frames
      (anvils whole: the morning). Hero: the climbers.
    """
    _climb(st, s, C, "cl", "gold")


def cl12_legday(st, s, C, nar):
    """BEAT 12  "They call it leg day."   frames 739-783 (45 f, 1.88 s), sky gold.
    Words: They 741, call 746, it 752, leg 755, day 761. The pause after it (0.7 s) makes this shot exactly as long as
    cl23 (45 frames): the repeat is frame for frame.

    STORY: About 2.0 s. Ground-level close shot on the stairs: Steve's legs pump up the steps past the lens with an
    anvil in his hand, Kai's legs right behind him. This exact set-up comes back at dusk for the second They call it
    leg day.
    Cast: Steve, Kai. Effects: two anvils as held items, stone stairs, walking up stairs, no step shorter than seven
    frames.

    MUST BE SEEN, ON WHICH WORD
      frame 739       Steve's legs already climbing into the frame
      "leg" 755 .. "day" 761   his legs pumping up the steps past the lens, the anvil in his hand; Kai's legs right
                      behind him
      the steps       the game's half steps (stair_z): the feet land on the treads, never in the air or in the stone
    SHARED: LEGS_CAM (= cl23 exactly; no handheld: _repeat_cam), LEGGERS / CLIMB_PACE / LEGS_FRAMES (= cl23). Key
      any word-synced action by its offset in THIS shot and apply the same offset in cl23 (identical: +2 +7 +13 +16
      +22).
    NEIGHBOURS: before, cl11_climb; after, tp13_sticky (the wall top).
    MEASURED (the set builder, out/test/legday_set_b12_legs[_zones].png): beside the stair's open east edge at knee
      height, 24 mm: Steve's legs and anvil climbing past the lens; Kai below, out of frame at that instant (he must
      come in: start him nearer).
    NOW (stub): LEGS_CAM tracking up the stair with them (linear), focus on Steve's leg, Steve from step 5.6
      (2 ahead of the lens), Kai from 4.4 (entering beside the lens by "leg"), a step every 8 frames. Hero: the
      legs.
    """
    _legs(st, s, C, "cl2", "gold")


def cl22_dusk(st, s, C, nar):
    """BEAT 22  "But they carried all twelve back up before dark."   frames 1373-1445 (73 f, 3.04 s), sky DUSK.
    Words: But 1375, they 1378, carried 1381, all 1392, twelve 1399, back 1410, up 1417, before 1421, dark 1429.
    THE DIP: black on 1373 and 1374 (fading out over rd21's 1370-1372), back by 1377 (DIPS); the lead's C.rearm puts
    the twelve planks out again inside the black (they are out from 1375) and the dust lit.

    STORY: About 3.0 s. The low angle of the first wall shot, now at dusk, orange into purple, lanterns glowing along
    the wall: the four climb the stairs in a staggered line, an anvil in every hand. On top the narrator waits by the
    lever, the dust line lit again, the sticky pistons pushed out with their planks and eight anvils already back in
    place. Never show the anvils being picked up off the road.
    Cast: Steve, Kai, Zuri, Ari, Narrator (Efe, slim-arm model). Effects: four anvils as held items, eight anvils as
    blocks on the planks, sticky pistons extended with planks, lit redstone dust line, lanterns as light, dusk sky.

    MUST BE SEEN, ON WHICH WORD
      1377 on         (the picture is back) THE SAME FRAME AS cl11 under the dusk sky, the face lanterns glowing
      "carried" 1381 .. "twelve" 1399   the four climbing with anvils (CHIPPED: the same anvils that fell), as in cl11
      "dark" 1429     the planks out with eight anvils of the DUSK set on them (SHELF "dusk_eight"; chipped as they
                      landed: CHIPPED), the indigo sky
      the road        empty: the day set that fell is NOT shown (the lead's SHELF; never the anvils picked up)
    SHARED: CLIMB_CAM exactly as cl11, CLIMBERS / CLIMB_PACE / CLIMB_FRAMES exactly as cl11
      (the first 70 frames are cl11's, frame for frame; the review found the first stub 0.01 block and a tread pop
      one frame apart, because the walk was planned over the shot's own length: fixed).
    NEIGHBOURS: before, rd21_still (gold, the road after the drop: a dip to black between); after, cl23_legday.
    RISKS (story): "The second They call it leg day must be recognised as the same shot as the first ... Fallback if
      the dusk module is dropped: keep the golden sky" (not needed: the dusk sky is in this film's SKIES).
    MEASURED (the set builder, out/test/legday_set_b22_climb[_zones].png): the dusk sky, face lanterns, climbers;
      palette passes (0.94). THE NARRATOR BY THE LEVER IS NOT VISIBLE from this camera (behind the shelf and the
      edge, the lever at the wall top's north end): the story's "on top the narrator waits by the lever" is carried by
      tp24 (the lever at dusk); the shared camera stays. (He could stand at the wall top's front edge to be seen, but
      that is not "by the lever".)
    NOW (stub): _climb exactly as cl11 under the dusk lights (1.4), the anvils in hand chipped. Hero: the climbers.
    """
    _climb(st, s, C, "cl3", "dusk")


def cl23_legday(st, s, C, nar):
    """BEAT 23  "They call it leg day."   frames 1446-1490 (45 f, 1.88 s), sky DUSK.
    Words: They 1448, call 1453, it 1459, leg 1462, day 1468. The pause after it (0.7 s) comes before the last line.

    STORY: About 2.0 s. Exactly the set-up of the first They call it leg day, same lens, height and step count, now in
    lantern light: the same legs pump up the same steps past the lens, Steve's first and Kai's right behind, an anvil
    in each hand.
    Cast: Steve, Kai. Effects: two anvils as held items, stone stairs, lantern light.

    MUST BE SEEN, ON WHICH WORD: as cl12, frame for frame (the same 45 frames, the same word frames relative to the
      shot: They +2, call +7, it +13, leg +16, day +22, in both since the narration was re-spoken in review: the
      first take had cl23's words one frame earlier from "call" on), in lantern light, the anvils chipped.
    SHARED: LEGS_CAM exactly as cl12, LEGGERS / CLIMB_PACE / LEGS_FRAMES exactly as cl12.
    NEIGHBOURS: before, cl22_dusk; after, tp24_reloading (the wall top at last light: the film's last shot).
    MEASURED (the set builder, out/test/legday_set_b23_legs[_zones].png): the same set-up in lantern light; palette
      passes.
    NOW (stub): _legs exactly as cl12 under the dusk lights, the anvils chipped. Hero: the legs.
    """
    _legs(st, s, C, "cl4", "dusk")
