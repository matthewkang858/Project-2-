"""Leg Day, sequence ROAD: the exit road at the foot of the anvil wall and the meadow beyond it, golden light: the
patrol, the charge, THE DROP, what was left, Steve among the anvils. Beats 15, 16, 19, 20, 21 (shots rd15_pillagers,
rd16_punch, rd19_drop, rd20_banner, rd21_still), sky "gold". One function per shot; the contract is in
films/legday_common.py (tags "rd...", C.actor / C.narrator / C.patrol, C.cam, C.lights, C.stuck_arrow, st.use /
st.hero).

STATUS: STUBS written by the lead (camera from the set builder's suggestion, cast placed, the beat's action keyed:
the march, the retraction, the release, the crush and the drops so that the film builds and renders end to end).
Every docstring carries the beat, its words with their frames, what must be seen on which word, the neighbours, the
risks and the measured notes. The acting is yours.

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
# this sequence's own cameras (starts: the set builder's suggestions; yours to change)
# ---------------------------------------------------------------------------------------------------------------
RD15_CAM = dict(LC._set_cam("b15"), pos1=(4.95, 44.3, 3.9))
RD16_CAM = dict(LC._set_cam("b16"), pos1=(3.0, 42.4, 0.45))
RD19_CAM = LC._set_cam("b19")                    # LOCKED (the story): only the tiniest handheld
RD20_CAM = dict(pos=(3.7, 45.3, 0.6), target=(1.45, 49.65, 0.3), pos1=(2.75, 47.65, 0.42), target1=(1.45, 49.65, 0.3),
                lens=35.0, fstop=2.8)            # a push in to the banner and the bottle (the set's b20, re-aimed on the
#                                                  lead's drop spots: PLACES banner_spot / bottle_spot)
RD21_CAM = dict(LC._set_cam("b21"), pos1=(4.1, 45.75, 0.3))
# the release word ("back" 1169) and the captain's landing y (49.6) are the LEAD'S: legday_common RELEASE /
# CAPTAIN_LAND_Y (the patrol clock of rd15, tp18 and rd19 hangs on them): C.release_frame(), C.land_frame()
RUNNERS = (("steve", (1.0, 29.2), (1.0, 39.2)), ("kai", (2.3, 27.7), (2.3, 37.7)),
           ("zuri", (0.35, 26.7), (0.35, 36.7)))          # (role, from, to): staggered 1.3 sideways, 1.5-2.5 back
ARROWS_16 = ((0.35, 41.0), (1.15, 41.4), (2.0, 40.8))     # three arrows into the road in front of the runners
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
    NOW (stub): RD15_CAM (+ a creep), C.march_patrol("rd15") (the clock). Hero: the captain.
    """
    f0, f1 = s.frame_start, s.frame_end
    pat = C.march_patrol("rd15")
    st.use(s, *pat)
    C.cam(s, None, focus=pat[0].head, **RD15_CAM)
    st.hero(s, "captain", pat[0])
    C.lights(s, "gold", near=(0.5, 60.0, 1.0), radius=12.0)


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
    NOW (stub): RD16_CAM (+ a slow creep back), the three sprinting north from 945, staggered 1.3 sideways, Steve's
      right fist up; three arrows into the road on "them" (982, 984, 986); the runners stop by about 988. Hero:
      Steve.
    """
    f0, f1 = s.frame_start, s.frame_end
    runners = []
    for role, a, b in RUNNERS:
        p = C.actor(role, "rd")
        pa, pb = C.stand(a), C.stand(b)
        p.place(f0, pa, LC.yaw_to(pa, pb))
        p.walk(f0, [pa, pb], sprint=True, ramp=(False, True))
        runners.append(p)
    runners[0].raise_arm(f0, angle=70.0, ease=4)
    hit = C.at(s, "them")
    for i, (x, y) in enumerate(ARROWS_16):
        C.stuck_arrow(s, (x, y, 0.0), ARROW_DOWN, frame=hit - 2 + 2 * i, scale=1.25)
    st.use(s, *runners)
    C.cam(s, None, focus=runners[0].head, **RD16_CAM)
    st.hero(s, "steve", runners[0])
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
    NOW (stub): RD19_CAM locked (handheld 0.002), C.march_patrol("rd19") (the clock: the captain at y 55.0 on 1142,
      49.9 on the landing frame); the row retracts and the anvils are released on C.release_frame() ("back" 1169);
      crush_patrol kills all five on their anvils' landing frames (knockback False: they tip over in place), the
      bottle and the banner dropped on their spots (C.memo["rd_drops"]). Heroes: the captain, the file.
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
    res = illagers.crush_patrol(pat, drops, camera=s, stage=st, knockback=False, village=C.v,
                                spots=[C.P("bottle_spot"), C.P("banner_spot")], face=cam)
    C.memo["rd_drops"] = list(res.get(pat[0].name, {}).get("items", []))
    C.memo["rd_crush"] = dict(land=land, struck=sorted(res), start=start)
    st.use(s, *pat)
    C.cam(s, None, handheld=0.002, **RD19_CAM)
    st.hero(s, "captain", pat[0])
    C.lights(s, "gold", near=(0.0, 50.0, 4.0), radius=14.0)


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
    NOW (stub): RD20_CAM (the set's b20 re-aimed on the lead's drop spots, the push ease_out), rd19's drops (or a
      fresh pair). Heroes: the banner and the bottle.
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
    NOW (stub): RD21_CAM (+ a drift), steve_rd2 walking out from 1307 to steve_among_anvils, looking up at efe_rd
      (with his torch at narrator_edge) from "still", turning away on "cheating"; the drops on their spots. Heroes:
      Steve.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "rd2")
    b = C.P("steve_among_anvils")
    a = (b[0] + 0.6, b[1] - 2.2, b[2])
    steve.place(f0, a, LC.yaw_to(a, b))
    stop = steve.walk(f0, [a, b], speed=2.0, ramp=(False, True))
    efe = C.narrator("rd")
    C.put(efe, f0, "narrator_edge")
    efe.look_at(f0, steve.eye_point(f0), ease=0)
    steve.look_at(f0, (b[0] - 1.0, b[1] + 3.0, 1.0), ease=0)
    steve.look_at(max(stop - 4, C.at(s, "still")), efe.eye_point(f0), ease=8)
    steve.look_at(C.at(s, "cheating"), (b[0] - 0.5, b[1] + 1.5, 0.4), ease=8)
    steve.look_at(C.at(s, "cheating") + 12, (-0.5, 40.0, 4.0), ease=10)
    items = _drops(st, s, C, "rd21")
    st.use(s, steve, efe)
    C.cam(s, None, focus=steve.head, **RD21_CAM)
    st.hero(s, "steve", steve)
    C.lights(s, "gold", near=(0.0, 47.0, 6.0), radius=16.0)
    del items
