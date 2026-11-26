"""Leg Day, sequence CLIMB: the anvil wall seen from the road and from its stair: the daily climb with the anvils
(beats 11, 12, golden) and its exact repeat before dark (beats 22, 23, dusk). Shots cl11_climb, cl12_legday,
cl22_dusk, cl23_legday. One function per shot; the contract is in films/legday_common.py (tags "cl...", C.actor,
C.cam, C.lights, st.use / st.hero).

STATUS: STUBS written by the lead (the SHARED cameras, the climbers placed and climbing, the anvils in their hands)
so the film builds and renders end to end. Every docstring carries the beat, its words with their frames, what must
be seen on which word, the neighbours, the risks and the measured notes. The acting is yours.

WHY ONE SEQUENCE FOR BOTH SKIES: cl22 / cl23 must be recognised as cl11 / cl12 again ("Keep lens, height and step
count identical and change only the light": the story's risk). One director makes both, from ONE camera each
(legday_common CAMS "climb" and "legs", shared: unchanged) and ONE staging function each (_climb, _legs below):
the dusk shots call the same function with the same constants. Change a constant and both change together.

THE PLACE (films/legday_set.py, "THE ANVIL WALL"): the wall's road face (x = -1) looks EAST into the morning sun; the
stair: 18 stone-brick stairs on the road face at its south end, ascending north, step k at (-1, 27 + k, k), the top
step (-1, 44, 17) level with the walkway (z 18); one wide, no rail, open air on its east side. stair_z(y) (LS) = the
game's half-step heights (front half k + 0.5, back half k + 1). WALKING UP: Player.walk on a 3D polyline measures its
speed along the 3D line, so half-step nodes either float the feet between treads (the set's paths "stair_climb" /
"stair_ramp": up to a quarter or half block) or stall at every riser. The stubs walk the straight ramp (slope 1,
within a quarter block of every tread) and key the root's delta_location z per frame to put the feet exactly ON the
treads (_on_treads: a half-block pop in one frame at each riser, as the game steps up). Keep it or do better. Anchors stair_foot (-0.5, 26.3), stair_top (-0.5, 44.75, 18), wall_top_south.
The shelf: planks at (0, 46..57, 17) two blocks out from the face, anvils on them at (0, y, 18): the lead's SHELF
puts eight of the day set (planks 3..10) on it in cl11 / cl12 and eight of the DUSK set in cl22 / cl23 (do not st.use
anvils). The face lanterns hang at (-1, 31, 9) (-1, 37, 14) (-1, 49, 11) (-1, 55, 11) (group legday_wall).
THE SKIES: cl11 / cl12 "gold" (the face lit by the sun in the east); cl22 / cl23 "dusk" (the sun down in the west,
  behind the wall: the face lit by its lanterns at 1.4, an indigo sky with the first stars). The cut INTO cl22 dips
  to black (films/legday.py DIPS: black on 1369 and 1370, back by 1373); the lead re-arms the row inside the black
  (the planks are OUT again from 1371: C.rearm). Nothing important on 1366-1372.
TAGS (twins): steve / kai / zuri / ari _cl (cl11), _cl2 (cl12), _cl3 (cl22), _cl4 (cl23): each holds an anvil
  (fixtures.hold_anvil), placed on its shot's first frame (no pre-roll).
LIGHT: C.lights(s, "gold" | "dusk", near=(-1.0, 40.0, 8.0), radius=26.0) (the stair's lanterns and the face's).
PREVIEW samples for render.py previews: 7 (legday_common.PREVIEW_SAMPLES).
"""
from engine import fixtures, shots
from films import legday_common as LC
from films import legday_set as LS

# ---------------------------------------------------------------------------------------------------------------
# the staging, ONE constant each for the gold shot and its dusk repeat
# ---------------------------------------------------------------------------------------------------------------
CLIMB_SEED = 31               # the handheld seed of CAMS "climb" in cl11 AND cl22 (the same drift in both)
LEGS_SEED = 47                # the handheld seed of CAMS "legs" in cl12 AND cl23
CLIMBERS = (("steve", 3.75), ("kai", 5.75), ("zuri", 7.75), ("ari", 9.75))   # (role, step: y = 27 + step) at the
#                                                                             shot's first frame, staggered by 2
CLIMB_SPEED = 1.2             # blocks / s along the stair (slow: no step shorter than seven frames)
LEGGERS = (("steve", 4.1), ("kai", 2.5))       # cl12 / cl23: Steve first past the lens, Kai right behind
LEGS_SPEED = 1.3


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


def _climbers(C, s, tag, cast, speed):
    """Players of `cast` [(role, step)] placed on the stair at their steps on s's first frame, an anvil in hand,
    climbing at `speed` (blocks / s along the ramp) to the shot's end (at speed on frame 1), their feet on the
    treads (_on_treads). Returns them."""
    f0, f1 = s.frame_start, s.frame_end
    out = []
    for role, step in cast:
        p = C.actor(role, tag)
        y0 = LS.STAIR_Y0 + step
        y1 = min(LS.STAIR_Y0 + LS.STEPS - 0.3, y0 + speed / 1.4142 * (f1 - f0 + 1) / 24.0)
        a, b = (-0.5, y0, _ramp_z(y0)), (-0.5, y1, _ramp_z(y1))
        p.place(f0, a, LC.yaw_to(a, b))
        fixtures.hold_anvil(p)
        p.walk(f0, [a, b], speed=speed, ramp=(False, True))
        _on_treads(p, f0, f1)
        out.append(p)
    return out


def _climb(st, s, C, tag, sky):
    """cl11 and cl22: CAMS "climb", the four climbers, the lights of the sky."""
    cl = _climbers(C, s, tag, CLIMBERS, CLIMB_SPEED)
    st.use(s, *cl)
    C.cam(s, "climb", seed=CLIMB_SEED, handheld=0.004)
    st.hero(s, "climbers", *cl)
    C.lights(s, sky, near=(-1.0, 40.0, 8.0), radius=26.0)
    return cl


def _legs(st, s, C, tag, sky):
    """cl12 and cl23: CAMS "legs", Steve and Kai climbing past the lens."""
    cl = _climbers(C, s, tag, LEGGERS, LEGS_SPEED)
    st.use(s, *cl)
    C.cam(s, "legs", seed=LEGS_SEED, focus=(-0.5, 31.6, 5.3), handheld=0.004)
    st.hero(s, "legs", *cl)
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
    SHARED: CAMS "climb" (= cl22_dusk exactly; handheld seed CLIMB_SEED), CLIMBERS / CLIMB_SPEED (= cl22).
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
      "climb" and out/test/legday_scout_climb_*.png. If you need another camera for this shot, it changes cl22
      too: say so in your result (a shared camera).
    NOW (stub): CAMS "climb" (b11), the four on steps 3.75 / 5.75 / 7.75 / 9.75 climbing at 1.2 blocks/s. Hero: the
      climbers.
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
    SHARED: CAMS "legs" (= cl23 exactly; handheld seed LEGS_SEED), LEGGERS / LEGS_SPEED (= cl23).
    NEIGHBOURS: before, cl11_climb; after, tp13_sticky (the wall top).
    MEASURED (the set builder, out/test/legday_set_b12_legs[_zones].png): beside the stair's open east edge at knee
      height, 24 mm: Steve's legs and anvil climbing past the lens; Kai below, out of frame at that instant (he must
      come in: start him nearer).
    NOW (stub): CAMS "legs", Steve from step 4.1 and Kai from 2.5 climbing at 1.3 blocks/s. Hero: the legs.
    """
    _legs(st, s, C, "cl2", "gold")


def cl22_dusk(st, s, C, nar):
    """BEAT 22  "But they carried all twelve back up before dark."   frames 1369-1441 (73 f, 3.04 s), sky DUSK.
    Words: But 1371, they 1373, carried 1377, all 1387, twelve 1395, back 1406, up 1412, before 1416, dark 1424.
    THE DIP: black on 1369 and 1370 (fading out over rd21's 1366-1368), back by 1373 (DIPS); the lead's C.rearm puts
    the twelve planks out again inside the black (they are out from 1371) and the dust lit.

    STORY: About 3.0 s. The low angle of the first wall shot, now at dusk, orange into purple, lanterns glowing along
    the wall: the four climb the stairs in a staggered line, an anvil in every hand. On top the narrator waits by the
    lever, the dust line lit again, the sticky pistons pushed out with their planks and eight anvils already back in
    place. Never show the anvils being picked up off the road.
    Cast: Steve, Kai, Zuri, Ari, Narrator (Efe, slim-arm model). Effects: four anvils as held items, eight anvils as
    blocks on the planks, sticky pistons extended with planks, lit redstone dust line, lanterns as light, dusk sky.

    MUST BE SEEN, ON WHICH WORD
      1373 on         (the picture is back) THE SAME FRAME AS cl11 under the dusk sky, the face lanterns glowing
      "carried" 1377 .. "twelve" 1395   the four climbing with anvils, as in cl11
      "dark" 1424     the planks out with eight anvils of the DUSK set on them (SHELF "dusk_eight"), the indigo sky
      the road        empty: the day set that fell is NOT shown (the lead's SHELF; never the anvils picked up)
    SHARED: CAMS "climb" exactly as cl11 (seed CLIMB_SEED), CLIMBERS / CLIMB_SPEED exactly as cl11.
    NEIGHBOURS: before, rd21_still (gold, the road after the drop: a dip to black between); after, cl23_legday.
    RISKS (story): "The second They call it leg day must be recognised as the same shot as the first ... Fallback if
      the dusk module is dropped: keep the golden sky" (not needed: the dusk sky is in this film's SKIES).
    MEASURED (the set builder, out/test/legday_set_b22_climb[_zones].png): the dusk sky, face lanterns, climbers;
      palette passes (0.94). THE NARRATOR BY THE LEVER IS NOT VISIBLE from this camera (behind the shelf and the
      edge, the lever at the wall top's north end): the story's "on top the narrator waits by the lever" is carried by
      tp24 (the lever at dusk); the shared camera stays. (He could stand at the wall top's front edge to be seen, but
      that is not "by the lever".)
    NOW (stub): _climb exactly as cl11 under the dusk lights (1.4). Hero: the climbers.
    """
    _climb(st, s, C, "cl3", "dusk")


def cl23_legday(st, s, C, nar):
    """BEAT 23  "They call it leg day."   frames 1442-1486 (45 f, 1.88 s), sky DUSK.
    Words: They 1444, call 1448, it 1454, leg 1457, day 1463. The pause after it (0.7 s) comes before the last line.

    STORY: About 2.0 s. Exactly the set-up of the first They call it leg day, same lens, height and step count, now in
    lantern light: the same legs pump up the same steps past the lens, Steve's first and Kai's right behind, an anvil
    in each hand.
    Cast: Steve, Kai. Effects: two anvils as held items, stone stairs, lantern light.

    MUST BE SEEN, ON WHICH WORD: as cl12, frame for frame (the same 45 frames, the same word frames relative to the
      shot: They +2, call +6, it +12, leg +15, day +21), in lantern light.
    SHARED: CAMS "legs" exactly as cl12 (seed LEGS_SEED), LEGGERS / LEGS_SPEED exactly as cl12.
    NEIGHBOURS: before, cl22_dusk; after, tp24_reloading (the wall top at last light: the film's last shot).
    MEASURED (the set builder, out/test/legday_set_b23_legs[_zones].png): the same set-up in lantern light; palette
      passes.
    NOW (stub): _legs exactly as cl12 under the dusk lights. Hero: the legs.
    """
    _legs(st, s, C, "cl4", "dusk")
