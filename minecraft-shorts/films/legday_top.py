"""Leg Day, sequence TOP: the top of the anvil wall: the twelve sticky pistons, the dust line, the lever. Beats 13,
14, 18 (golden) and 24 (dusk, the film's last shot). Shots tp13_sticky, tp14_why, tp18_lever, tp24_reloading. One
function per shot; the contract is in films/legday_common.py (tags "tp...", C.actor / C.narrator / C.patrol, C.cam,
C.lights, C.appear, st.use / st.hero).

STATUS: STUBS written by the lead (camera from the set builder's suggestion, cast placed, the beat's action roughly
keyed so the film builds and renders end to end). Every docstring carries the beat, its words with their frames,
what must be seen on which word, the neighbours, the risks and the measured notes. The acting is yours.

THE PLACE (films/legday_set.py, "THE ANVIL WALL"): the walkway is z 18 (the wall's three columns x -4..-2, y 27..60).
  The row: twelve sticky pistons in the top course (-2, 46..57, 17) facing EAST over the road; extended, the head at
  (-1, y, 17) and the plank on it at (0, y, 17), two blocks out from the face; the anvils on the planks (0, y, 18).
  C.row.pistons[i] / C.row.blocks[i] (planks) / C.anvils[i] / C.anvils_dusk[i]: i 0 = the south one (y 46), 11 =
  the north one (y 57), next to the lever: "THE TWELFTH". The dust (-3, 46..59, 18) on the blocks behind the
  pistons, lit from the lever: power 15 by the lever .. 2 at the far (south) end. The lever: a floor lever on its
  pier (-3, 60, 19) at the wall top's NORTH end, facing east; lever_narrator (-1.7, 60.28, 18) facing west (east
  of the lever: Lever.stand()), narrator_edge (-1.25, 60.5, 18). place_12th (-2.55, 57.55, 18) facing east (beside
  the twelfth gap), set_anvil_12th (-2.6, 58.45, 18) facing south-east (Steve on the dust, setting anvil 12 on plank
  12), wall_top_north (-2.5, 59.4, 18), wall_top_south (-1.5, 44.6, 18), stair_top (-0.5, 44.75, 18). Paths
  wall_top (x -1.5, over the pistons) and wall_top_dust (x -2.5, on the dust). Lanterns on the wall top: the front
  edge over the stair, (-4, 60, 18) beside the lever (the face key), the back edge over the shelf.
  The terrain north of the wall is carried on to y 150 (a camera on the wall top looking north sees meadow, not
  void); the patrol's road "patrol_road" (0.5, 84 -> 40) comes from there.
THE WORLD STATE IN YOUR HANDS (legday_common "THE WORLD STATE"): the twelfth piston (tp13: place + extend, then its
  plank), the twelfth anvil of the day set (tp14: C.appear), the lever OFF and the dust dark (tp18), the twelfth
  anvil of the dusk set (tp24: C.appear). NOT the row's retraction (rd19's) nor the re-arm (the lead's, before
  cl22). Before tp13 the twelfth piston is retracted and invisible and its plank hidden (the lead keys that in
  LegDay.__init__); Piston.place(f) makes it appear ON f, "a piston placed where it is powered extends in the same
  tick": p.place(f, player=efe); p.extend(f) (the set builder checked: short head ON f, long head f + 1, out by f + 3).
THE SKIES: tp13 / tp14 / tp18 "gold" (the sun due east, low: the wall top's road edge is lit); tp24 "dusk" (the sun
  down in the west, behind the wall top's back: the narrator's face keyed by his own redstone torch at
  LS.B24_TORCH_WATTS (120 W), the redstone "a weak light in the game ... key his face with a boosted lantern beside
  the lever and let the torch be the red accent": the story's alternative, if the torch key is not enough).
  tools/palette_check failed "stone not magenta" on the dusk wall top from the set's b24 (G/R 0.90, warm); the stub's
  TP24_CAM from the east passes (0.95 on 1545, the row hero 80 % inside the safe area): if yours fails, known and accepted
  (films/legday.py SKIES). Do not boost lanterns to fix it.
THE PATROL CLOCK (legday_common, after review): the patrol of tp18 is C.march_patrol("tp18"), the same march as rd15's
  and rd19's. On "flipped" (1108) the captain's feet are at y 57.4, just short of the shelf's north end (plank 12 is
  y 57-58), his file behind him at 59.4 .. 65.4 on the open road past the wall's north end (y 61): THE STORY'S
  PICTURE, "on the open road just short of the shelf". FROM ANY CAMERA OVER THE WALL TOP THE WALL ITSELF HIDES THEM
  (measured: out/test/legday_tp18var_tp18_lever_1110_v0.png, the set's b18 view: the meadow beyond, empty). Only a
  camera hanging out past the wall top's north-east corner (x > -1.3, y > 60.5) sees the lever and the file below in
  one frame (out/test/legday_scout_tp18_lever_1110[_zones].png). The first stub marched a far patrol of its own 20
  blocks up the road (23 blocks behind rd19's at the same frames): the lever was flipped with nobody near the trap.
  The anvils in hand (C.carry_anvil): whole in tp14 (the morning), CHIPPED in tp24 (the same anvils, carried back
  up after the fall: legday_common THE CHIPPED ANVILS; the dusk set on the shelf is chipped too).
TAGS (twins): efe_tp (tp13: the piston and the plank), efe_tp2 (tp14, soft, his torch), efe_tp3 (tp18: empty right
  hand for the lever), efe_tp4 (tp24: the torch in his LEFT hand, as his key, the right arm for the lever),
  steve_tp (tp14, a whole anvil), steve_tp2 (tp24, a chipped anvil), the patrol patrol_tp18_1..5 (the clock).
LIGHT: C.lights(s, "gold" | "dusk", near=(-2.0, 52.0, 18.0), radius=12..14).
PREVIEW samples for render.py previews: 9 (legday_common.PREVIEW_SAMPLES).
"""
from engine import redstone
from films import legday_common as LC
from films import legday_set as LS

# ---------------------------------------------------------------------------------------------------------------
# this sequence's own cameras (starts: the set builder's suggestions; yours to change)
# ---------------------------------------------------------------------------------------------------------------
TP13_CAM = dict(LC._set_cam("b13"), pos1=(0.75, 62.6, 19.9))
TP14_CAM = dict(LC._set_cam("b14"), pos1=(-2.45, 59.6, 18.22))
# tp18: hanging out past the wall top's NORTH-EAST corner, looking back down at the lever and the corner of the wall:
# the only camera family (scouted, out/test/legday_tp18var*) that sees the lever AND the file on the road at the
# wall's foot on "flipped" (THE PATROL CLOCK: from any camera over the wall top the wall itself hides it)
TP18_CAM = dict(pos=(-0.6, 62.0, 21.0), target=(-2.0, 59.6, 13.0), pos1=(-0.7, 61.9, 20.9),
                target1=(-2.0, 59.55, 13.0), lens=16.0, fstop=5.6)
TP18_CAM_LEVER = dict(LC._set_cam("b18"), pos1=(-3.55, 58.05, 20.25))   # the set's b18: the lever big, NO patrol
# tp24: from the EAST, over the road, looking back WNW and down at the row: every anvil of the re-armed row reads as
# standing on its plank, receding to the narrator at the lever (out/test/legday_scout_tp24_*): the row is the hero
TP24_CAM = dict(pos=(5.9, 50.6, 20.6), target=(-1.6, 58.2, 17.6), pos1=(5.5, 51.2, 20.5),
                target1=(-1.6, 58.4, 17.7), lens=24.0, fstop=4.0)


def _hold(p, item, frame=None):
    """p.hold(item) when engine.players knows the item (a block item it cannot build raises ValueError)."""
    try:
        return p.hold(item, frame=frame)
    except ValueError as e:
        print("[legday_top] %s cannot hold %s: %s" % (p.name, item, e))
        return None


def tp13_sticky(st, s, C, nar):
    """BEAT 13  "Under each anvil, I put a sticky piston."   frames 784-852 (69 f, 2.88 s), sky gold.
    Words: Under 786, each 793, anvil 800, I 816, put 819, a 822, sticky 824, piston 833.

    STORY: About 3.0 s. Camera just outside the top of the wall, looking back along the row: sticky pistons in the top
    course, each with its arm out over the drop, one oak plank on the end of each arm and an anvil standing on each
    plank, eleven in all. In the last gap the narrator sets the twelfth sticky piston, slime-green face showing for an
    instant. The dust behind it is already lit, so its arm shoots out at once, bare, and he sets one oak plank on the
    end. Behind the pistons a lit line of redstone dust runs to one lever, bright at the lever and duller toward the
    far end.
    Cast: Narrator (Efe, slim-arm model). Effects: twelve sticky pistons, eleven already extended; sticky piston
    placed and extending at once, slime-green face visible; oak plank blocks on the piston arms, one placed in shot;
    eleven anvils as blocks; lit redstone dust line fading with distance from the lever; lever; block placing.

    MUST BE SEEN, ON WHICH WORD
      frame 784       the row of eleven armed pistons with planks and anvils (SHELF "eleven"), the narrator at the
                      twelfth gap, moving
      "anvil" 800     the anvils on their planks, read as standing ON the planks held out by the arms
      "put" 819       the twelfth sticky piston placed (the green slime face toward the lens for an instant), its arm
                      shooting out at once, BARE (the dust is lit)
      "piston" 833 .. ~845   he sets one oak plank on the end of the arm (C.row.blocks[11].show(f, True), a swing)
      the dust        lit, bright by the lever, duller toward the far end (power 15 .. 2: the set does it)
    SHARED: place_12th. THE WORLD STATE: you key C.row.pistons[11].place / extend and C.row.blocks[11].show here.
    NEIGHBOURS: before, cl12_legday (the legs on the stair); after, tp14_why (Steve brings the twelfth anvil).
    RISKS (story): "the viewer must understand that each anvil stands on a plank held out by a piston arm, or the drop
      makes no sense. The green face going in, the arm shooting out and the plank going on must all be in the one
      shot. Fallback: cut the plank placing and show the twelfth piston already carrying its plank; he only places
      the green-faced piston behind it in a first take from the wall top."
    MEASURED (the set builder, out/test/legday_set_b13_twelfth[_zones].png): above the road beyond the north end,
      24 mm, looking back along the row: the narrator at the twelfth gap, its green sticky head shooting out (a soft
      green blur in the still: it is close to the lens), eleven planks with anvils receding, lit dust, lanterns;
      palette passes. The narrator's hand item: players.hold("sticky_piston") (the stub tries it).
    NOW (stub): TP13_CAM (+ a drift), efe_tp at place_12th with a sticky piston in hand: place + extend on "put"
      (819), the plank in his hand after, set on "piston" + 6 (839). Hero: the narrator, the twelfth piston.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.actor("efe", "tp")
    C.put(efe, f0, "place_12th")
    efe.look_at(f0, (-1.5, 57.5, 17.5), ease=0)
    _hold(efe, "sticky_piston")
    p12 = C.row.pistons[11]
    f_put = C.at(s, "put")
    p12.place(f_put, player=efe)
    p12.extend(f_put)
    _hold(efe, "oak_planks", frame=f_put + 2)
    f_set = C.at(s, "piston") + 6
    efe.attack(f_set - 1)
    C.row.blocks[11].show(f_set, True)
    efe.hold(None, frame=f_set + 1)
    efe.look_at(f_set + 4, (0.5, 57.5, 17.5), ease=8)
    st.use(s, efe)
    C.cam(s, None, focus=efe.head, **TP13_CAM)
    st.hero(s, "narrator", efe)
    C.lights(s, "gold", near=(-1.0, 52.0, 18.0), radius=12.0)


def tp14_why(st, s, C, nar):
    """BEAT 14  "Nobody asked why."   frames 853-902 (50 f, 2.08 s), sky gold.
    Words: Nobody 855, asked 867, why 876. The pause after it (0.8 s) is the story's turn: the patrol comes next.

    STORY: About 2.0 s. Ground-level on the wall top beside the lever, the glowing dust line leading away from the
    lens. Steve's feet step right over the lit dust, past the lever and the piston backs. He sets his anvil down on
    the last bare plank and walks on, never once looking down. Soft in the background the narrator stands and
    watches him go.
    Cast: Steve, Narrator (Efe, slim-arm model). Effects: anvil held, then placed as the twelfth block; sticky pistons
    extended with planks; lit redstone dust line in the foreground; lever.

    MUST BE SEEN, ON WHICH WORD
      frame 853       Steve already walking over the dust toward the lens, the anvil in his hand
      "Nobody" 855 .. "asked" 867   his feet stepping right over the lit dust (the answer under his feet)
      "why" 876       he sets the anvil on the last bare plank (plank 12, beside the lever): C.appear(s,
                      C.anvils[11], f) with his swing on f - 1 and his hand empty from f (hold(None, frame=f))
      to ~900         he walks on, never once looking down; the narrator soft in the background, watching him go
    SHARED: set_anvil_12th (= tp24's), the lever.
    THE WORLD STATE: you key the twelfth anvil's appearance (C.appear); SHELF "eleven" shows the other eleven.
    NEIGHBOURS: before, tp13_sticky; after, rd15_pillagers (the meadow: the patrol).
    MEASURED (the set builder, out/test/legday_set_b14_dust[_zones].png): on the walkway by the lever, 24 mm, looking
      south: the glowing dust leading away from the lens, Steve walking over it toward the lens with an anvil, the
      narrator soft beyond.
    NOW (stub): TP14_CAM (+ a creep back), steve_tp with an anvil walking north over the dust to set_anvil_12th
      (arrives ~872), sets the anvil on "why" (876), turns and walks back south; efe_tp2 (torch) soft at
      (-3.45, 47.2) watching. Hero: Steve.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "tp")
    a = (-2.55, 53.6, LS.WALK_Z)
    e = C.P("set_anvil_12th")
    steve.place(f0, a, LC.yaw_to(a, e))
    C.carry_anvil(steve)                                   # the morning: whole
    steve.walk(f0, [a, e], speed=2.2, ramp=(False, True))
    f_set = C.at(s, "why")
    steve.attack(f_set - 1)
    C.appear(s, C.anvils[11], f_set)
    steve.hold(None, frame=f_set)
    back = (-2.45, 54.5, LS.WALK_Z)
    steve.walk(f_set + 6, [e, back], speed=2.0)
    efe = C.narrator("tp2")
    efe.place(f0, (-3.45, 47.2, LS.WALK_Z), LC.yaw_to((-3.45, 47.2), (-3.45, 50.0)))
    efe.look_at(f0, steve.eye_point(f0), ease=0)
    efe.look_at(f0 + 2, steve.eye_point(f_set), ease=f_set - f0 - 4)
    st.use(s, steve, efe)
    C.cam(s, None, focus=(-2.45, 55.6, 18.4), **TP14_CAM)
    st.hero(s, "steve", steve)
    C.lights(s, "gold", near=(-2.5, 52.0, 18.0), radius=12.0)


def tp18_lever(st, s, C, nar):
    """BEAT 18  "I flipped one lever."   frames 1103-1141 (39 f, 1.62 s), sky gold.
    Words: I 1105, flipped 1108, one 1117, lever 1123.

    STORY: About 2.0 s. Close on the lever on the wall top: the narrator's thin arm reaches in and flips it. The whole
    glowing line of redstone dust goes dark in the same instant, as it does in the game. Soft and far below, on the
    open road just short of the shelf, the captain's banner moves toward it.
    Cast: Narrator (Efe, slim-arm model), patrol captain far below, out of focus. Effects: lever switching off,
    redstone dust line going dark all at once, ominous banner on the captain's head.

    MUST BE SEEN, ON WHICH WORD
      frame 1103      the lever big, the dust lit, the narrator's thin arm coming in
      "flipped" 1108  the lever flips (redstone.flip_by(efe, C.lever, f, ...): the game's model swap) and the WHOLE
                      dust line goes dark on that frame (C.wire.unpower(t))
      the patrol      ON THE CLOCK (C.march_patrol("tp18"): never another march): on "flipped" 1108 the captain at
                      y 57.4 entering under the shelf's north end (the shelf may hide him: that is the truth), his
                      file behind him at 59.4 .. 65.4 on the open road past the wall's north end, walking toward the
                      trap; at 1141 the captain at 55.1
    SHARED: lever_narrator; THE PATROL CLOCK. THE WORLD STATE: you key the lever off and the dust dark; NOT the row:
      the pistons snap back IN rd19 (the overlapping action of the cut: the row is not in this frame, the lever not
      in rd19's). TIME RUNS STRAIGHT THROUGH THE CUT (never compressed): the lever goes off on 1108, the patrol walks
      on, the row answers on "back" 1169 in rd19 (the edit's overlap: rd19 replays the moment from the road).
    NEIGHBOURS: before, pn17_cows; after, rd19_drop (the money shot from the road).
    THE REVIEW (story, the patrol clock; confirmed on the build): the first stub's patrol walked 20 blocks up the road
      at the flip, 23 blocks behind rd19's twin on the same frames, and its docstring called the patrol's position
      "free (time compressed across the cut)" while the plan calls the same cut an overlapping action (time
      EXPANDED: flip 1108, retraction 1169). The trap read as fired early and saved by the edit. Now one clock.
    THE CAMERA (measured, the lead's scouting; out/test/legday_tp18var*_tp18_lever_1110_v*.png): from the lever's
      side of the wall top (the set's b18, TP18_CAM_LEVER) the lever is big but the wall hides the road at its foot:
      no patrol in the frame. The stub hangs the camera out past the NORTH-EAST corner, 16 mm, looking back down
      (TP18_CAM; out/test/legday_scout_tp18_lever_1110[_zones].png): the narrator at the lever from above and behind,
      his arm on it, the dust line dark along the wall top, the corner of the wall dropping 18 blocks, and the file
      on the road at its foot walking into the trap. TO FIX: the file sits at y 55-75 % (in the caption band) and is
      small (the banner does not read at this size; "soft and far below" as written); the narrator's face is not
      seen (the story asks for his thin arm only). Choose between the two (the lever big, or the lever and the file),
      or find a third, but keep the clock.
    NOW (stub): TP18_CAM (+ a drift), efe_tp3 at lever_narrator (empty-handed) flips on "flipped" (1108), the dust
      dark at once; the patrol on the clock (patrol_tp18). Heroes: the lever, the file.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.actor("efe", "tp3")
    C.put(efe, f0, "lever_narrator")
    t = redstone.flip_by(efe, C.lever, C.at(s, "flipped"), look=True, reach=True)
    C.wire.unpower(t)
    pat = C.march_patrol("tp18")                           # THE PATROL CLOCK (legday_common): never another march
    st.use(s, efe, *pat)
    C.cam(s, None, focus=C.lever.hand_point(f0), **TP18_CAM)
    st.hero(s, "lever", *C.lever.objects)          # (a property of the kit parts)
    st.hero(s, "the file", *pat[2:])
    C.lights(s, "gold", near=(-3.0, 56.0, 18.0), radius=10.0)


def tp24_reloading(st, s, C, nar):
    """BEAT 24  "I call it reloading."   frames 1491-1572 (82 f, 3.42 s), sky DUSK. The film's last shot.
    Words: I 1493, call 1498, it 1507, reloading 1510 (spoken to about 1524; its caption holds about a second, to
    1536). Then the last image holds to 1566 and the last 6 frames (1567-1572) are black (END_BLACK): the story's cut
    to black.

    STORY: About 3.0 s. Wall top at last light, looking along the row: Steve sets the twelfth anvil on the last plank
    and walks off without a glance. The narrator stays beside the lever, the redstone torch lighting his face, his
    free arm lifting to the lever and stopping there, looking out over the armed row of twelve anvils and the empty
    road below. Hold one second after the last word, then cut to black.
    Cast: Narrator (Efe, slim-arm model), Steve. Effects: twelve anvils as blocks on planks, the last one placed in
    shot; sticky pistons extended; lit redstone dust line; lever; redstone torch held and glowing as the key light on
    his face; lanterns as light.

    MUST BE SEEN, ON WHICH WORD
      frame 1491      the armed row (SHELF "dusk_eleven": eleven of the DUSK set, chipped as they landed), Steve
                      with the twelfth anvil (chipped), the narrator at the lever with his torch, the dusk sky
      "call" 1498 .. "it" 1507   Steve sets the twelfth anvil on the last plank (C.appear(s, C.anvils_dusk[11], f))
                      and walks off without a glance
      "reloading" 1510 .. 1566   the narrator's free arm lifts to the lever and stops there; he looks out over the
                      armed row and the empty road below; his face lit by his torch; HOLD (1.75 s), then black
                      from 1567
      THE ROW IS THE HERO (the review): the anvils standing on their planks must be INSIDE y 14-60 % and clear of
                      the caption band (y 62-72 %, where "reloading" sits 1510-1536) together with the torch-lit face
                      at the lever: st.hero(s, "row", ...) is declared, so --zones / palette_check flag it. PRIORITY:
                      the row first, then the narrator's face size
    SHARED: lever_narrator (= tp18), set_anvil_12th (= tp14). THE WORLD STATE: the twelfth dusk anvil (C.appear).
      The lever is ON again (the lead's re-arm, 1373): no flip here.
    NEIGHBOURS: before, cl23_legday (the legs at dusk); after, the end (the Reel loops to sq01).
    RISKS (story): "At dusk the narrator's face is only as bright as his practical. The redstone torch is a weak light
      in the game: key his face with a boosted lantern beside the lever and let the torch be the red accent."
      "Long caption words (... reloading) need the reduced letter size ... Check that reloading with its full stop
      fits inside the caption width and hold it a full second." (The lead: the caption system draws long words
      smaller by itself; "reloading" is on screen 1510-1536, see tools/legday_timeline.)
    MEASURED (the set builder, out/test/legday_set_b24_reloading[_zones].png): above the road south-east of the lever,
      35 mm: the armed row (dusk set) receding to Steve setting the twelfth and the narrator at the lever with his
      arm up, the dusk sky behind. palette_check fails "stone not magenta" at G/R 0.90: the warm dusk sky on the
      wall top, not the lanterns (0.87 with them off): ACCEPTED (films/legday.py SKIES).
    THE REVIEW (story, confirmed on the lead's first stub still, out/test/legday_scout_tp24_reloading_1530): the
      set's b24 camera put the anvil row at y 52-100 % (under the caption and the Reels UI) and the road out of the
      frame; "come closer to the narrator" would have dropped the row. THE LEAD'S SCOUTING (out/test/legday_tp24var*
      _tp24_reloading_1535_v*.png: from the south end along the row the row hides the narrator, the anvils overlap;
      at the anvils' height the near ones block him; from the EAST over the road, looking back WNW and down, every
      anvil reads as standing on its plank): TP24_CAM from the east, 24 mm (out/test/legday_scout_tp24_reloading_
      1500 / _1545[_zones].png): five chipped anvils on their planks receding to the narrator at the lever, y 43-58 %;
      the planks in the caption band; the lanterns; the dusk sky. TO FIX: the narrator's face is 28 px (tools.
      legday_geo tp24_reloading:1545: eyes x 63 %, y 37 %, 23 degrees off the lens): once Steve has gone the push may
      end closer on him, as long as the last anvils stay inside y 14-60 %. The empty road below is not in this frame.
    THE STAGING: the torch in his LEFT hand (C.narrator(..., hand="left"): toward this camera, the key on his face),
      his body toward the south-west (the lever at his front right), his head on the row; his RIGHT arm lifts to
      the lever on "reloading" (raise_arm side "r"). Check on stills that the hand reaches the lever.
    NOW (stub): TP24_CAM (+ a slow push), efe_tp4 at lever_narrator facing south-west, his torch (left hand) at
      LS.B24_TORCH_WATTS (the key), looking out over the row; his right arm up to the lever from "reloading";
      steve_tp2 sets the dusk twelfth anvil (chipped) on "call" (1498) and walks off south over the dust (out of the
      frame's left edge by about 1553). Heroes: the row, the narrator.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.narrator("tp4", watts=LS.B24_TORCH_WATTS, hand="left")    # the torch on the camera's side: his key
    p = C.P("lever_narrator")
    C.put(efe, f0, "lever_narrator", toward=(p[0] - 1.0, p[1] - 1.0))   # south-west: the lever at his front right
    efe.look_at(f0, (0.5, 52.0, 18.5), ease=0)                           # out over the row (and the road below)
    efe.raise_arm(C.at(s, "reloading"), angle=60.0, side="r")           # his free (right) arm to the lever
    steve = C.actor("steve", "tp2")
    a = C.P("set_anvil_12th")
    steve.place(f0, a, C.yaw("set_anvil_12th"))
    C.carry_anvil(steve, dusk=True, index=11)              # the twelfth, carried back up: chipped (CHIPPED)
    steve.look_at(f0, (0.5, 57.5, 18.2), ease=0)
    f_set = C.at(s, "call")
    steve.attack(f_set - 1)
    C.appear(s, C.anvils_dusk[11], f_set)
    steve.hold(None, frame=f_set)
    away = (-2.5, 50.0, LS.WALK_Z)
    steve.walk(f_set + 8, [a, away])                                    # walking (4.3/s): out of the frame's left
    #                                                                     edge before the black (about 1553)
    st.use(s, efe, steve)
    C.cam(s, None, focus=efe.head, **TP24_CAM)
    st.hero(s, "row", *[an.objects()[0] for an in C.anvils_dusk[7:11]])  # THE PAYOFF: the re-armed row first
    st.hero(s, "narrator", efe)
    C.lights(s, "dusk", near=(-2.0, 52.0, 18.0), radius=14.0)
