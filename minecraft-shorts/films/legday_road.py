"""Leg Day, sequence ROAD: the exit road at the foot of the anvil wall and the meadow beyond it, golden light: the
patrol, the charge, THE DROP, what was left, Steve among the anvils. Beats 15, 16, 19, 20, 21 (shots rd15_pillagers,
rd16_punch, rd19_drop, rd20_banner, rd21_still), sky "gold". One function per shot; the contract is in
films/legday_common.py (tags "rd...", C.actor / C.narrator / C.patrol, C.cam, C.lights, C.stuck_arrow, st.use /
st.hero).

STATUS: SHOT by the road director (the lead's stubs replaced; each docstring has its NOW and MEASURED lines):
  rd15  the file from the meadow's east verge, 40 mm, 22 degrees off its line: five pillagers read as five, the
        captain in front with the banner at the left third, the lone oak at the right edge; his eyes find the lens
        on "pillagers"; a creep back and a pan with them
  rd16  the three sprint at a low 28 mm that tracks back: Kai left, Steve centre, Zuri right (1.1 apart sideways,
        1.1 / 2.1 back); Steve's attack swings into the air on the way, the last ON "punch"; on "them" three arrows
        thud into the road a block in front of them, each lets go of the sprint and stops dead in 3 ticks, looks
        down at his arrow, then up the road at the patrol
  rd19  LOCKED 14 mm low on the road's east half, 5.7 blocks short of the captain's death: the file walks at the
        lens under the shelf, the planks snap in on "back", the captain's eyes go up, the anvils fall as one dark
        receding line, the impact on "fell", red, the five tip east (toward the lens's side), the poofs
  rd20  the push in to the drops (the lead's camera), their spin phased so the banner is broad-side between
        "banner" and the end, the bottle just after "bottle"
  rd21  low 24 mm south-south-east of Steve: he walks in from the left, stops on "still" with his back to us and
        looks up at the narrator (a figure at the wall top's corner, the focus racks to him), and on "cheating"
        looks down at the anvil beside him and turns round to the stairs: his face comes to the lens (sq10's turn)
TOOLS: tools/legday_road_probe.py (ground heights, positions, the runners' speeds, Steve's head per 3 frames).

THE PLACE (films/legday_set.py, "THE ANVIL WALL"): the exit road (dirt path x -1..1) runs north along the wall's road
  face (x = -1, looking EAST into the morning sun). Under the shelf, x -1..1, y 45..57: COBBLESTONE paving (top z 0):
  every anvil of the shelf lands there as a block, in (0, y, 0) under its plank, after a fall of 18 (34 damage; the
  captain, with the banner on his head, 25.5: health 24: all five die). North of y 57 the road is the meadow (z 1
  from y 58, 2 from y 71-72, 3 from y 78): the path C.v.paths["patrol_road"] (0.5, 84 -> 40) has its hops. A lone
  oak LONE_OAK (3, 81) on the meadow's horizon up the road (beat 15). Anchors: road_shelf_south (0.5, 44),
  road_shelf_north (0.5, 58.6), runners_stop (0.55, 39.2), patrol_far (0.5, 82); the path run_out (0.6, 18 -> 40).
  THE DROPS AND STEVE (SHARED, the lead's: one name = one point, C.P(name) = C.A[set anchor]): banner_spot (1.45,
  49.25) and bottle_spot (1.45, 50.05), 1.0 block east of the captain's feet on the landing frame (within the game's
  1.35-block toss; crush_patrol spots=[C.P("bottle_spot"), C.P("banner_spot")]); steve_among_anvils (1.45, 46.9),
  2.35 blocks short of the banner (a player collects an item within about one block: keep him 2 or more away the
  WHOLE shot, tools.legday_state measures his real position). The road between the stair and the east verge is
  only x 0..3 wide.
THE PATROL (engine.illagers): C.patrol(tag) = [captain (the ominous banner on his head), 2..5], crossbows held. EVERY
  patrol of this sequence is C.march_patrol(tag): THE PATROL CLOCK (legday_common), one march on the whole
  patrol_road (0.5, 84 -> 40, with its hops) from one frame (757) for rd15, tp18 and rd19 alike, so that the
  captain's feet are at y 49.6 when the anvils land (1210): rd15 903 -> 72.9, 944 -> 70.2; rd19 1142 -> 55.0, "back"
  1169 -> 52.9, 1210 -> 49.9 (all five on the strip: crushed). Do not march a patrol any other way (tp18 shows the
  same clock from the wall top). The file walks 2.0 apart at the leader's 1.911 blocks/s, gait "vanilla" (the
  game's short swing, for wide and long-lens shots). A dying pillager tips over to ITS OWN LEFT: walking south, that
  is EAST, toward a camera on the road's east side (rd19's): the illagers builder's measurement. Damage x 0.75 while
  the banner is on: a fall of 17 or more kills the captain (the shelf's 18 does).
THE WORLD STATE IN YOUR HANDS (legday_common "THE WORLD STATE"): rd19 retracts the row and releases the day set ON
  C.release_frame() ("back" 1169: FIXED, the patrol clock hangs on it): C.row.retract(f); fixtures.release(C.anvils,
  f, world=C.v, chip=list(LC.CHIPPED)) (the frozen draw: 10 of 12 chip; the dusk set carried back up is chipped the
  same way); the anvils then lie on the road through rd21 (the release's keys carry on; the lead's SHELF "twelve"
  shows them). The lever and the dust were switched off in tp18 (not yours); the re-arm before dusk is the lead's.
  THE WORLD REMEMBERS THE LANDED ANVILS for the whole film (fixtures.release writes them into the World, which has no
  time): on the strip x 0..1, y 46..57 do not use C.stand() (it gives z 1, on an anvil, in every shot once rd19 has
  been built): give z 0.0 (the cobblestone) explicitly.
THE SKY: "gold", the sun due EAST: the patrol walking south and the runners going north are lit on their east
  halves; cameras looking north or south along the road have the sun 90 degrees off their axis.
TAGS (twins): patrol_rd15_1..5 (rd15), patrol_rd19_1..5 (rd19), both on the patrol clock; steve / kai / zuri _rd
  (rd16), steve_rd2 (rd21), efe_rd (rd21, his torch); the banner and the bottle: crush_patrol's drops in rd19,
  handed on to rd20 / rd21 through C.memo["rd_drops"].
LIGHT: C.lights(s, "gold", near=<point>, radius=12..16).
PREVIEW samples for render.py previews: 10 (legday_common.PREVIEW_SAMPLES).
"""
from engine import fixtures, illagers
from films import legday_common as LC

# ---------------------------------------------------------------------------------------------------------------
# this sequence's own cameras (C.cam(s, None, **CAM)); every one measured with tools.legday_geo and on stills
# ---------------------------------------------------------------------------------------------------------------
# beat 15: on the meadow's east verge, 13 blocks short of the captain and 22 degrees off the file's line, 40 mm:
# the five read as five (the 85 mm from 28 blocks stacked them into one shape), a slow creep back and a pan with them
RD15_CAM = dict(pos=(5.8, 59.4, 3.0), target=(1.2, 75.2, 3.55), pos1=(6.0, 58.6, 2.95), target1=(1.05, 73.6, 3.4),
                lens=40.0, fstop=2.8)
# beat 16: low on the east half of the road ahead of the runners (the wall and its stair on the right), 28 mm,
# tracking back as they come (at speed on the first frame, slowing)
RD16_CAM = dict(pos=(2.2, 43.3, 0.28), target=(1.2, 33.5, 1.0), pos1=(2.4, 45.2, 0.3), target1=(1.3, 35.0, 1.05),
                lens=28.0, fstop=2.8)
# beat 19: LOCKED (the story: only the tiniest handheld), 14 mm f/5.6 at knee height (0.15) on the road right beside
# the strip (x 1.9, 0.9 east of the anvils' cells), 2.4 blocks short of where the captain dies, looking north along
# the wall's foot and up at 25 degrees. The file walks at the lens under the plank row (the row at the top of the
# frame), the captain grows to a big low angle, his head and banner tip back as the anvils come down the face, the
# near anvils slam in from above on "fell" and he tips toward the lens's side. Scouted against the set's b19 (2.3,
# 42.5: the file small at the centre-right) and eight others (out/test/legday_rd19var*_rd19_drop_*: from 5 to 10
# blocks back the file stays small, and the planks hide the anvils standing on them from any low camera)
RD19_CAM = dict(pos=(1.9, 47.5, 0.15), target=(0.16, 57.35, 4.81), lens=14.0, fstop=5.6)
RD20_CAM = dict(pos=(3.7, 45.3, 0.6), target=(1.45, 49.65, 0.3), pos1=(2.75, 47.65, 0.42), target1=(1.45, 49.65, 0.3),
                lens=35.0, fstop=2.8)            # a push in to the banner and the bottle (the set's b20, re-aimed on the
#                                                  lead's drop spots: PLACES banner_spot / bottle_spot)
# the frame on which each drop shows rd20's lens its broad side (it turns a radian a second, like the game's):
# the banner 21 frames after "banner" and 20 before the push ends (50 degrees off at both: 64 % of its width), the
# bottle 8 frames after "bottle"
RD20_FACE = {"banner": ("banner", 21), "bottle": ("bottle", 8)}      # (word of rd20, frames after it)
# beat 21: low (0.22), 3.4 blocks south-south-east of steve_among_anvils, 24 mm f/4, looking up the face at 26
# degrees: Steve big in the lower left third, the narrator at narrator_edge above him at the wall top's north-east
# corner against the sky (the retracted plank row runs up to him); a slow push in. Scouted: 22 mm from 3.5 (Steve
# right under the narrator, 11 px), 28 mm from 3.0 (his back fills the frame), this (13-14 px, Steve's eyes 54 %)
RD21_CAM = dict(pos=(3.15, 43.96, 0.22), target=(-0.68, 53.2, 5.21), pos1=(3.07, 44.1, 0.23),
                target1=(-0.64, 53.2, 5.15), lens=24.0, fstop=4.0)
# the release word ("back" 1169) and the captain's landing y (49.6) are the LEAD'S: legday_common RELEASE /
# CAPTAIN_LAND_Y (the patrol clock of rd15, tp18 and rd19 hangs on them): C.release_frame(), C.land_frame()

# beat 16: the three runners, sprinting at speed from the first frame (ramp in False) and letting go of the sprint
# key a frame after their arrow lands (the game's ground friction then stops them dead in about 3 ticks: 0.34 block
# of slide). Their
# stops are staggered 1.1 sideways and 1.1 / 2.1 back (the CONTRACT: 0.7 block at least, or two runners read as
# one two-headed shape). (role, x, y where they stand still, frame the sprint key is let go, from "them")
RUNNERS = (("steve", 2.0, 39.0, -1), ("kai", 3.1, 37.9, 1), ("zuri", 0.55, 36.9, 2))
SPRINT_TICK = 5.612 / 20.0                        # engine.players SPRINT_SPEED in blocks per game tick
SLIDE = SPRINT_TICK * 0.546 / (1.0 - 0.546)       # the slide to a halt after the key is let go (GROUND_FRICTION)
# three arrows from the patrol up the road (north) into the road 1.15 in front of each runner's stop, on "them"
# (-2, 0, +1): (dx, dy from the runner's stop, frame offset from "them")
ARROWS_16 = ((-0.1, 1.15, -2), (0.1, 1.1, 0), (-0.05, 1.15, 1))
ARROW_DOWN = (0.05, -0.55, -0.83)                         # from the patrol to the north, down into the road


def rd15_pillagers(st, s, C, nar):
    """BEAT 15  "Then the pillagers came."   frames 903-944 (42 f, 1.75 s), sky gold.
    Words: Then 905, the 912, pillagers 913, came 927.

    STORY: About 2.0 s. Ground-level long lens from the road, looking out to the meadow and a lone oak on a clean
    horizon: five pillagers walk up the road toward the lens in single file, crossbows held, the captain in front with
    the ominous banner standing over its head.
    Cast: five pillagers, one of them the patrol captain. Effects: five crossbows held, ominous banner on the
    captain's head, pillager walk cycle.

    MUST BE SEEN, ON WHICH WORD
      frame 903       the file already walking (C.march_patrol: on the patrol clock since 757; the captain's
                      feet at y 72.9 on 903, 70.2 on 944; the last follower 8 blocks behind him, on the real road)
      "pillagers" 913 the five in single file, crossbows, the CAPTAIN in front with the banner over his head (the
                      banner must read: it is the drop of beat 20)
      the horizon     clean, the lone oak (3, 81) behind them
    SHARED: none (patrol_road, LONE_OAK).
    NEIGHBOURS: before, tp14_why (the wall top: "Nobody asked why."); after, rd16_punch (the runners).
    MEASURED: the illagers builder: under the look-dev sun (az 62) this beat as written (camera on the road looking
      north, the patrol walking south toward the lens) is BACKLIT; with this film's sun due east (SKIES "gold") their
      faces are lit from the east (the set builder's still). The set builder (out/test/legday_set_b15_patrol
      [_zones].png): 85 mm from 3.9 above the strip, over the meadow's 1-block rises (from ground level they read as
      dirt bands): the file staggered, the captain's banner, the lone oak, a clean horizon, faces lit from the east.
      FALLBACK CHOSEN by the set: the camera 3.9 high, not "ground-level".
      THE REVIEW (technical): the first stub marched from y 76 with only 12 frames of pre-roll: three followers walked
      a full block INSIDE the meadow's rise (z 2 in grass, the ground z 3 at y 78), hidden by the captain in the 85 mm
      frame. Fixed by the patrol clock (the whole road, its hops, from 757); tools.legday_state now checks
      every body against the World (no character inside a solid block in its shots).
    NOW: RD15_CAM, 40 mm f/2.8 from the meadow's east verge (5.8, 59.4, 3.0: 2 above the meadow), 13-14 blocks from
      the captain and 22 degrees off the file's line, creeping back 0.8 and panning left with the file (ease_out: at
      speed on 903), focus on the captain's head. The patrol is C.march_patrol("rd15") untouched (the clock); the
      captain's head turns to the lens from "pillagers" - 5 (908, over 8 frames) and tracks it to the end (a patrol
      mob's look-around: eye contact on the word). Heroes: the captain, the file. Lights gold near (0.5, 66).
      WHY NOT THE SET'S b15 (85 mm from 28 blocks, 9 degrees off the line): the five stacked into one shape.
    MEASURED (tools.legday_geo, the road director): on "pillagers" 913 the five eyes at x 32 / 41 / 49 / 54 / 58 %,
      y 45-49 %, faces 38 / 33 / 30 / 27 / 25 px, the captain 6.5 degrees off the lens (his look), the others 15-20;
      nothing blocks any face. On 940 the captain at x 28 %, eyes y 56 % (head box 41-58 %: inside 60), 41 px.
      Stills: out/test/legday_rd_rd15_pillagers_913_zones.png (the banner above his head at y 35-46 %, the oak at
      the right edge, the file's legs behind the meadow's 1-block rise and its grass).
    """
    f0, f1 = s.frame_start, s.frame_end
    pat = C.march_patrol("rd15")                  # THE PATROL CLOCK: marching since 757 (positions untouched here)
    cap = pat[0]
    cam = RD15_CAM["pos"]
    # the captain's eyes find the lens on "pillagers" (a patrol mob's random look-around), and stay on it
    cap.look_at(C.at(s, "pillagers") - 5, cam, ease=8)
    cap.track(C.at(s, "pillagers") + 3, f1, cam, step=4, ease=2)
    st.use(s, *pat)
    C.cam(s, None, focus=cap.head, **RD15_CAM)
    st.hero(s, "captain", cap)
    st.hero(s, "the file", *pat[1:])
    C.lights(s, "gold", near=(0.5, 66.0, 2.0), radius=14.0)


def rd16_punch(st, s, C, nar):
    """BEAT 16  "Everyone ran out to punch them."   frames 945-996 (52 f, 2.17 s), sky gold.
    Words: Everyone 947, ran 961, out 968, to 973, punch 976, them 984.

    STORY: About 2.2 s. Low tracking shot from the verge: Steve sprints down the road at the lens with a bare fist
    raised, Kai and Zuri staggered behind him, the wall running along one side. On the last beat three arrows thud
    into the ground in front of them and all three stop dead.
    Cast: Steve, Kai, Zuri. Effects: sprint cycle with a raised fist, three arrows sticking into the ground, runners
    staggered by at least 0.7 block.

    MUST BE SEEN, ON WHICH WORD
      frame 945       the three already sprinting (placed on 945, at speed: walk(..., sprint=True, ramp=(False, ..)))
      "ran" 961 .. "punch" 976   Steve at the lens with a bare fist raised, Kai and Zuri staggered (at least 0.7 block
                      apart: two runners 0.2 apart are one two-headed shape), the wall along one side
      "them" 984      three arrows THUD into the road in front of them (they shake 7 ticks) and all three stop dead
      the arrows      ARE THE LINK to pn17 (arrows in the fence post): the story's risk for the jump of place
    SHARED: runners_stop.
    NEIGHBOURS: before, rd15_pillagers; after, pn17_cows (they hid behind the cows).
    MEASURED (the set builder, out/test/legday_set_b16_run[_zones].png): low on the east verge ahead of the runners
      (the stair ramp on the right), 32 mm: the runners coming at the lens, three arrows stuck in the road in front of
      them (y 62 %: the top of the caption band); Kai overlapped Steve (x 64 / 66 %): stagger them more sideways.
    NOW: RD16_CAM, 28 mm f/2.8 low (0.28) on the road's east half, tracking back 1.9 blocks north (ease_out: at speed
      on 945, slowing), the wall and the stair on the right, a village house on the left. Kai (x 3.1), Steve (2.0)
      and Zuri (0.55) sprint north at the game's 5.61 blocks/s from 945 (placed at speed, ramp in False), staggered
      1.1 sideways and 1.1 / 2.1 back. Steve's attack swings (the game has no raised-fist pose: a player who wants to
      punch clicks) on 950, 959, 968 and ON "punch" 976; Kai swings once on 977. On "them": an arrow thuds into the
      road 1.1-1.15 in front of each (982 Steve's, 984 Kai's, 985 Zuri's; C.stuck_arrow, quivering 7 ticks, 56
      degrees down from the patrol up the road, scale 1.25); each lets go of the sprint a frame later (983, 985,
      986) and the game's ground friction stops him dead within 3 ticks (0.34 block); each looks down at his arrow
      the frame after it lands, then up the road at the patrol (behind the lens) 6 frames after stopping. Heroes:
      Steve; Kai and Zuri. Lights gold near (0.5, 36).
    MEASURED (tools.legday_geo): on "punch" 976 eyes Kai x 25 %, Steve 42 %, Zuri 58 % (y 43-47 %), faces 40 / 47 /
      34 px, all within 10 degrees of the lens, none blocked; on 990 (stopped) Kai 22 %, Steve 44 %, Zuri 65 %, faces
      52 / 60 / 44 px (the stub had Zuri behind Steve's arm at x 62 / 65 %). Stills: out/test/legday_rd_rd16_punch_985
      _zones.png (the first staging), out/test/legday_rdsc_rd16_punch_977 / _990_zones.png (this one).
    """
    f0, f1 = s.frame_start, s.frame_end
    them = C.at(s, "them")
    look_n = (0.6, 66.0, 2.6)                     # up the road: the patrol (behind the lens)
    runners, stops = [], []
    for role, x, y, off in RUNNERS:
        p = C.actor(role, "rd")
        release = them + off
        run = SPRINT_TICK * (release - f0) / 1.2 + SLIDE      # sprinting from f0, the key let go on `release`
        a, b = C.stand((x, y - run)), C.stand((x, y))          # (south of the strip: the World has no anvils here)
        p.place(f0, a, LC.yaw_to(a, b))
        p.look_at(f0, (x, y + 8.0, 1.4), ease=0)               # eyes up the road
        p.walk(f0, [a, b], sprint=True, ramp=(False, True))
        runners.append(p)
        stops.append((b, release))
    steve, kai, zuri = runners
    # Steve punches the air as he runs (a player's attack swing; the game has no raised-fist pose): one swing
    # every 8-9 frames, the last ON "punch"; Kai swings once with him on "punch"
    punch = C.at(s, "punch")
    for f in (punch - 26, punch - 17, punch - 8, punch):
        steve.attack(f)
    kai.attack(punch + 1)
    # three arrows thud into the road just in front of them on "them" (they quiver 7 ticks): each runner lets go of
    # the sprint a frame after his arrow lands and stops dead within 3 ticks, head down to the arrow, then up the
    # road at the patrol (behind the lens)
    for p, (b, release), (dx, dy, df) in zip(runners, stops, ARROWS_16):
        hit = them + df
        point = (b[0] + dx, b[1] + dy, 0.0)
        C.stuck_arrow(s, point, ARROW_DOWN, frame=hit, scale=1.25)
        p.look_at(hit + 1, (point[0], point[1], 0.2), ease=3)
        p.look_at(release + 6, look_n, ease=6)
    st.use(s, *runners)
    C.cam(s, None, focus=steve.head, **RD16_CAM)
    st.hero(s, "steve", steve)
    st.hero(s, "kai and zuri", kai, zuri)
    C.lights(s, "gold", near=(0.5, 36.0, 1.0), radius=12.0)


def rd19_drop(st, s, C, nar):
    """BEAT 19  "Twelve pistons pulled back, and twelve anvils fell on the road."   frames 1142-1249 (108 f, 4.50 s),
    sky gold. THE MONEY SHOT. Words: Twelve 1144, pistons 1151, pulled 1162, back 1169, and 1186, twelve 1189,
    anvils 1198, fell 1209, on 1216, the 1219, road 1221. The pause after it (0.8 s) lets the poofs bloom.

    STORY: About 3.8 s, the money shot. Locked low wide angle from the road, looking along the foot of the wall and
    up, the five pillagers marching in a clean file on the cobblestone strip directly under the shelf. All twelve
    sticky pistons snap back at once and pull their planks one block in against the wall. Twelve anvils hang on air
    for two frames, then drop in a receding line. The captain tips its head up. On impact each pillager flashes red
    and tips over, and the road fills with white puffs of smoke.
    Cast: five pillagers, one of them the patrol captain. Effects: twelve sticky pistons retracting with their planks,
    twelve anvils as falling blocks, red hurt flash and tip-over on five pillagers, white smoke puffs, ominous banner
    on the captain's head, cobblestone paving under the shelf.

    MUST BE SEEN, ON WHICH WORD
      frame 1142      the file marching in a clean line on the strip under the shelf, the planks out with the anvils
      "back" 1169     ALL TWELVE pistons snap back at once, the planks one block in (C.row.retract(f)); the anvils hang
                      on air for two frames (fixtures.release(C.anvils, f, world=C.v): they stand still on f, f+1,
                      f+2), then drop in a receding line; the captain tips his head up
      "fell" 1209-1210   IMPACT (41 frames after the release): each pillager flashes red and tips over (to his own
                      left: east, toward this camera's side); the anvils stand on the cobblestones
      ~1234-1249      the white death puffs (24 frames after the kill) fill the road; the captain's drops (the ominous
                      bottle and the banner) on their spots
    SHARED: banner_spot / bottle_spot (the drops: they lie there in rd20 and rd21). THE WORLD STATE: the row's
      retraction and the release are yours, here only.
    NEIGHBOURS: before, tp18_lever (the flip seen on the wall top: this shot replays that instant from the road, the
      overlapping action of the edit); after, rd20_banner (the smoke thinning: NO time jump between them, the poofs
      carry on: do not call fx.stop_particles in rd20).
    RISKS (story): "twelve falling blocks, five mobs and smoke in under four seconds can turn to mush. Keep the camera
      locked, the pillagers in a clean file, the two-frame hang before the drop. Fallback: two cuts inside the
      sentence, the planks snapping in seen from the wall top, then the impact from the road with only six anvils in
      frame on a longer lens."
    MEASURED (the set builder, out/test/legday_set_b19_drop[_zones].png, and its self-test): low on the road south
      of the shelf, 16 mm, looking along the wall's foot: a clean file on the strip (faces 50-55 %), the far anvils
      mid-fall in frame, the near ones entering from above, the pillagers' shadows on the face. All five struck, all
      lethal (captain 25.5). The march window: the captain's feet at y 45.71 .. 50.29 (x 0.5) on the landing frame.
      THE LEAD (the stub, measured by tools.legday_state): the anvils land on 1210 ("fell" 1209), all five crushed,
      the captain's feet at y 49.86, the drops within the toss; out/test/legday_scout_rd19_drop_1206[_zones].png
      (4 frames before the impact): the twelve anvils a motion-blurred line falling along the face over the file;
      the file small at the centre-right (x 50-60 %, y 47-60 %).
    THE CHIPS: release(..., chip=list(LC.CHIPPED)): the frozen draw (10 of 12 chip, 3 and 4 stay whole); the dusk
      set that "came back up" is chipped the same way (legday_common THE CHIPPED ANVILS). Do not change it.
    NOW: RD19_CAM LOCKED (handheld 0.002), 14 mm f/5.6 at knee height beside the strip, 2.4 blocks short of the
      captain's death, looking north along the wall's foot and up at 25 degrees (see RD19_CAM for the scouting);
      focus on the captain's head. C.march_patrol("rd19") (the clock: the captain at y 55.0 on 1142, 52.9 on "back"
      1169, 49.86 on the landing 1210), all five on the strip in a clean file walking at the lens under the planks.
      On C.release_frame() ("back" 1169) the row retracts (C.row.retract) and the day set is released
      (fixtures.release, chip=list(CHIPPED): they hang 2.4 frames, then drop); the captain's eyes go up to the anvil
      over him from 1170 (5 frames; the pillager's head stops at 40 degrees up: his banner tips back with it). The
      anvils come down the face as one dark line over the file and land on 1210 ("fell" 1209), the near ones
      slamming in from the top of the frame: illagers.crush_patrol (knockback False) kills all five on their anvils'
      frames, red, each tips over to its left = EAST = toward the lens's side; the poofs 24 frames later (1231-1236)
      and the captain's bottle and banner on bottle_spot / banner_spot, big in the foreground
      (C.memo["rd_drops"]), their spin phased for rd20 (RD20_FACE). Heroes: the captain, the file. Lights gold near
      (0, 50, 4).
    """
    f0, f1 = s.frame_start, s.frame_end
    f_back = C.release_frame()
    C.row.retract(f_back)
    drops = fixtures.release(C.anvils, f_back, world=C.v, chip=list(LC.CHIPPED))
    land = int(drops[0]["frame_land"])
    C.memo["rd_falls"] = drops                    # (tools.legday_state reads which anvils chipped)
    pat = C.march_patrol("rd19")
    start = C.patrol_clock()["start"]
    cam = RD19_CAM["pos"]
    # "the captain tips its head up" (the story): on the planks' snap his eyes go up to the anvil over him (the
    # pillager's head stops at 40 degrees up) and stay there until it lands
    cap = pat[0]
    above = cap.pos_at(f_back + 3)
    cap.look_at(f_back + 1, (above.x, above.y - 1.0, 18.0), ease=5)
    res = illagers.crush_patrol(pat, drops, camera=s, stage=st, knockback=False, village=C.v,
                                spots=[C.P("bottle_spot"), C.P("banner_spot")], face=cam)
    C.memo["rd_drops"] = list(res.get(pat[0].name, {}).get("items", []))
    # the drops spin as the game spins them (a radian a second): choose their phase so that each shows rd20's lens
    # its broad side at the moment its word needs it (the banner face-on between "banner" and the push's end, the
    # bottle just after "bottle"); without it the banner was edge-on ON "banner" (the scout of 1266)
    kill = res[pat[0].name]["frame"] if pat[0].name in res else None
    for it in C.memo["rd_drops"]:
        word, off = RD20_FACE["banner" if "banner" in it.name else "bottle"]
        f_face = C.T["rd20_banner"].at(word) + off
        it.face(f_face, _rd20_cam_at(C, f_face))
        it.animate(kill, kill + 320)
    C.memo["rd_crush"] = dict(land=land, struck=sorted(res), start=start)
    st.use(s, *pat)
    C.cam(s, None, focus=cap.head, handheld=0.002, **RD19_CAM)
    st.hero(s, "captain", pat[0])
    C.lights(s, "gold", near=(0.0, 50.0, 4.0), radius=14.0)


def _rd20_cam_at(C, f):
    """Where RD20_CAM's lens is on frame f (C.cam's ease_out move from pos to pos1 over rd20_banner)."""
    r = C.T["rd20_banner"]
    u = min(1.0, max(0.0, (f - r.frame_start) / float(r.frame_end + 1 - r.frame_start)))
    e = 1.0 - (1.0 - u) * (1.0 - u)
    a, b = RD20_CAM["pos"], RD20_CAM["pos1"]
    return tuple(a[i] + (b[i] - a[i]) * e for i in range(3))


def _drops(st, s, C, tag):
    """The banner and the bottle on their spots in shot s: rd19's drops (C.memo["rd_drops"]), or, when rd19 did not
    build them, a fresh pair (illagers.add_dropped_banner / _bottle) placed and turning."""
    items = C.memo.get("rd_drops") or []
    if items:
        st.use(s, *items)
        return items
    ban = illagers.add_dropped_banner(st, name="ominous_banner_%s" % tag, shot=s)
    bot = illagers.add_dropped_bottle(st, name="ominous_bottle_%s" % tag, shot=s)
    for it, where in ((ban, "banner_spot"), (bot, "bottle_spot")):
        it.place(s.frame_start, C.P(where))
        it.animate(s.frame_start, s.frame_end + 1)
    return [ban, bot]


def rd20_banner(st, s, C, nar):
    """BEAT 20  "That left a banner and a bottle."   frames 1250-1306 (57 f, 2.38 s), sky gold.
    Words: That 1252, left 1257, a 1263, banner 1265, and 1279, a 1282, bottle 1284. (Spoken at 0.9: the review
    measured it the fastest line of the film, 5.4 syllables a second, on the hardest picture: the bottle.)

    STORY: About 2.5 s. The smoke thins over a silent road: twelve anvils stand in a line on the cobblestones, most
    of them chipped, and between two of them the ominous banner and one ominous bottle turn slowly side by side as
    dropped items. No crossbows, no other drops. Slow push in until the pair fills the middle of the frame.
    Cast: none. Effects: twelve anvils as blocks, most in the chipped variant; ominous banner as a turning dropped
    item; ominous bottle as a turning dropped item; thinning smoke.

    MUST BE SEEN, ON WHICH WORD
      frame 1250      the last of the smoke thinning (rd19's poofs: no time jump), the anvils on the strip, moving in
      "banner" 1265   the ominous banner turning, readable
      "bottle" 1284 .. 1306   the push ends with the banner and the bottle TOGETHER filling the middle third of the
                      frame (the bottle must be recognised: "a small thing is seen only if it is what is in focus")
      no crossbows, no other drops (plain pillagers killed by an anvil drop nothing: illagers does it)
    SHARED: banner_spot / bottle_spot (rd19's drops: C.memo["rd_drops"]).
    NEIGHBOURS: before, rd19_drop; after, rd21_still (Steve among the anvils).
    RISKS (story): "the ominous bottle is a small dropped item and must be recognised. End the push-in with banner and
      bottle together filling the middle third of the frame. Fallback if it still does not read: change the line to
      They left a banner on the road (same word count) and leave the bottle in the picture" (the line is committed:
      only the picture can carry it now).
    MEASURED (the set builder, out/test/legday_set_b20_drops_a / _b[_zones].png): the push in, 35 mm: _a the twelve
      anvils on the cobblestones, _b the banner and the bottle side by side filling the middle; palette passes.
    THE LEAD'S SCOUT of the stub (out/test/legday_scout_rd20_banner_1297[_zones].png, the push's end; made before
      the line was slowed: the shot now ends on 1306): the banner and the bottle side by side filling the middle
      (x 25-75 %, y 33-55 %), the chipped anvils behind them: it reads.
    NOW: RD20_CAM (the lead's: the set's b20 re-aimed on the drop spots), 35 mm f/2.8, a push in from (3.7, 45.3,
      0.6) to (2.75, 47.65, 0.42) at speed on 1250 (ease_out), focus between the two. rd19's drops (C.memo["rd_drops"],
      no time jump: rd19's poofs still drifting on 1250). The drops turn as the game turns them (a radian a second);
      rd19 sets their phase (RD20_FACE) so that the banner shows the lens its broad side 21 frames after "banner"
      (50 degrees off on the word itself and at the push's end: 64 % of its width) and the bottle 8 frames after
      "bottle" (the scout of the stub had the banner edge-on ON "banner"). Heroes: the banner and the bottle. Lights
      gold near (1, 51).
    """
    items = _drops(st, s, C, "rd20")
    C.cam(s, None, focus=(1.45, 49.65, 0.3), **RD20_CAM)
    st.hero(s, "banner and bottle", *[getattr(it, "sprite", it) for it in items])     # their drawn meshes
    C.lights(s, "gold", near=(1.0, 51.0, 1.0), radius=10.0)


def rd21_still(st, s, C, nar):
    """BEAT 21  "Steve still says redstone is cheating."   frames 1307-1372 (66 f, 2.75 s), sky gold.
    Words: Steve 1309, still 1317, says 1324, redstone 1330, is 1341, cheating 1345. The pause after it (0.7 s) and
    the DIP to black into cl22 (fading out from 1370: nothing important on 1370-1372) carry the day to dusk.

    STORY: About 2.2 s. Tall frame from the road: Steve walks out and stops among the anvils in the foreground, two
    blocks short of the banner and bottle so he does not collect them. High above him on the wall top, small against
    the sky, the narrator stands by the lever with his redstone torch. Steve looks up at him and holds it for a beat,
    then turns his head away, to the anvils and then to the stairs.
    Cast: Steve, Narrator (Efe, slim-arm model). Effects: anvils as blocks on the cobblestones; banner and bottle as
    dropped items at the frame edge, out of his reach; redstone torch held and glowing; lever.

    MUST BE SEEN, ON WHICH WORD
      frame 1307      Steve walking out among the anvils (a twin, pre-rolled if he must be moving)
      "still" 1317 .. "says" 1324   he stops at steve_among_anvils (two blocks short of the drops) and looks UP at the
                      narrator high on the wall top (narrator_edge: at the front edge, so he is seen from below)
      "cheating" 1345 he turns his head away, to the anvils and then to the stairs: the same turn as sq10's "He said
                      that's cheating" (the story's rhyme)
      the drops       at the frame's edge, out of his reach
    SHARED: steve_among_anvils, narrator_edge, banner_spot / bottle_spot (rd19's drops).
    NEIGHBOURS: before, rd20_banner; after, cl22_dusk (the climb at dusk, after the dip).
    RISKS (story): "an attitude, not an action. It reads through the look up at the narrator and the head turning
      away, the same turn as He said that's cheating. Fallback: have Steve walk out of the frame with his back to the
      wall exactly as he walked away from the piston."
    FALLBACK CHOSEN (the set builder, measured): the narrator stands at the wall top's north-east FRONT corner
      (narrator_edge), not at the lever's own spot: seen from the road the edge hides anyone 0.7 further back. The
      retracted planks hide a figure further south from below.
    MEASURED (the set builder, out/test/legday_set_b21_cheating[_zones].png): low 16 mm three blocks from Steve among
      the anvils, up the face: Steve looking up (face 56 %), the wall face, the narrator TINY at the top's NE corner;
      the drops below the frame. THE LEAD: in that still Steve is seen from behind (his face away, up the wall): his
      look up and his head turning away must show his face (cheat the camera round to his side, C.to_lens).
      tools.legday_geo rd21_still:1330 on the stub (before the narration's last change; now about frame 1335):
      Steve's eyes x 7 % (the left edge), 130 degrees off the lens (from behind), face 84 px; the narrator's face
      10 px at x 64 %, y 31 % (a figure, as the story says "small against the sky", but no face).
      THE WORLD: the landed anvils are in the World (z 1 on the strip from C.stand): Steve's z is given (0.0).
    NOW: RD21_CAM, 24 mm f/4 low (0.22) 3.4 blocks south-south-east of steve_among_anvils, looking up the face at 26
      degrees, a slow push in. steve_rd2 (a twin not in rd20) walks in from the lens's left at walking speed from
      1307 (placed at speed) and lets go of the key so that he stands at steve_among_anvils (z 0: the road beside the
      strip) on "still" 1317 (2.35 from the banner: legday_state measures 2.35 or more all shot). From 1315 he looks
      up at the narrator (his head stops at 35 degrees up: the wall top) and holds it, his back to the lens, the
      narrator above him in the frame; the focus racks to the narrator from 1319 (0.5 s) and back to Steve from
      1336. On "cheating": his head drops to the anvil beside him (1340-1345), then he turns round to the stair
      (1346-1355, body and head: engine.players face / look_at) and his face comes to the lens (the rhyme of sq10's
      turn away), held to the end; nothing new in 1370-1372. efe_rd (C.narrator: his redstone torch) at
      narrator_edge tracks Steve with his head. The drops on their spots at the frame's bottom right. Heroes:
      Steve, the narrator. Lights gold near (0, 50, 8), radius 16.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "rd2")
    efe = C.narrator("rd")
    b = C.P("steve_among_anvils")                 # (1.45, 46.9): 2.35 short of the banner; z 0 (the World has the
    b = (b[0], b[1], 0.0)                         # landed anvils on the strip, not here: x 1.45 is the road beside it)
    still, cheat = C.at(s, "still"), C.at(s, "cheating")
    # he walks out from the south (from the lens's left, at walking speed on the first frame: a twin not in rd20)
    # and lets go of the key so that he stands on "still"
    run = 0.21585 * (still - f0) / 1.2 + 0.2596   # walk 4.317 blocks/s, the slide after the key (engine.players)
    a = (b[0] - 0.15, b[1] - run, 0.0)
    steve.place(f0, a, LC.yaw_to(a, b))
    C.put(efe, f0, "narrator_edge", toward=b)
    efe.look_at(f0, steve.eye_point(f0), ease=0)
    steve.look_at(f0, (b[0] - 0.2, b[1] + 6.0, 1.3), ease=0)          # where he walks: the anvils ahead
    steve.walk(f0, [a, b], ramp=(False, True))
    # on "still" he looks up at the narrator (the head stops at 35 degrees up: the wall top) and holds it
    steve.look_at(still - 2, efe.eye_point(still), ease=8)
    # on "cheating" he turns away: the head down to the anvil beside him, then the body round to the stairs (his
    # face comes round to the lens: the same turn away as sq10's "He said that's cheating")
    anvil = (0.5, b[1] + 0.3, 0.6)
    steve.look_at(cheat - 5, anvil, ease=5)
    stair = (-0.5, 37.5, 9.0)                    # the stair he carries them back up (step 10 at y 37, z 10)
    steve.face(cheat + 1, stair, ease=9)
    steve.look_at(cheat + 1, stair, ease=9)
    efe.track(f0 + 1, f1, steve, step=4, ease=4)
    items = _drops(st, s, C, "rd21")
    st.use(s, steve, efe)
    C.cam(s, None, focus=steve.head, **RD21_CAM)
    # the eye goes where Steve looks: the focus racks to the narrator while Steve looks up at him, and back to Steve
    # before he turns away (engine.shots focus(..., at_s): a 0.5 s pull)
    s.focus(efe.head, at_s=s.film.seconds(still + 2), rack_s=0.5)
    s.focus(steve.head, at_s=s.film.seconds(cheat - 9), rack_s=0.4)
    st.hero(s, "steve", steve)
    st.hero(s, "efe", efe)
    C.lights(s, "gold", near=(0.0, 50.0, 8.0), radius=16.0)
    del items
