"""THE SETS OF "LEG DAY" (stories/redstoner.json): a film-local set module, built INTO the seed-1 village through
village.build_village(edit=...) exactly as engine/sets.py builds hello_set. Nothing in engine/ is changed.

    from films import legday_set as LS
    v = LS.build_set(scene)                 # = village.build_village(scene, seed=1, edit=LS.legday_set)
    P = LS.make_parts(v)                    # the moving parts, AFTER the build, in their armed state (see make_parts)
    LS.SKIES                                # the two skies the set was lit and scouted under (copy into films/legday.py)
    LS.CAMERAS["b19"]                       # a suggested camera per beat: dict(pos, target, lens, fstop[, pos1, target1],
                                            #   sky, what); still out/test/legday_set_<beat>_<what>.png (+ _zones.png)
    v.anchors[...], v.yaws[...], v.paths[...], v.sets["legday"]    # see ANCHORS and _paths below

    $BPY -m films.legday_set                 # the self-test (numbers, 10 s): anchors on solid ground with the body free,
                                             #   cameras outside every block and every moving part, the anvils' landing
                                             #   cells / fall / damage, the march window, the dust's power, the paths
    $BPY -m films.legday_set b19 b20 ...     # the proof stills of these beats (one fresh build each, 540x960, 16
                                             #   samples, 2 threads, zones, tools/palette_check report; 10-30 s each)
    $BPY -m films.legday_set b19 --dry       # stage only: where each hero point lands in the frame, what hides it
    $BPY -m films.legday_set view NAME x,y,z tx,ty,tz LENS [FSTOP SKY WxH SAMPLES]   # a plain view of the set

THE SKIES (Blender azimuth: degrees counter-clockwise from east)
    gold  dict(preset="golden", az=0, el=27, bloom=1.0, grade="warm")   beats 1-21. THE SUN IS DUE EAST (the game's sun
          path: it rises in the east), the wall's road face looks east INTO it: lit face, its shadow falls west, away
          from the road. Pillagers walking south and runners going north are both lit on their east halves; cameras
          looking north or south along the road / the wall have the sun 90 degrees off their axis. The square's and
          the pens' cameras were placed for this sun. (Under the look-dev sun az 62 beat 15 is backlit; the Hello's
          az 215 lights the wall's back.) Faces turned EAST are lit; anything facing west is in shade.
    dusk  dict(preset="dusk", az=185, el=5, bloom=1.3, grade="warm")    beats 22-24: the sun has gone round to the west,
          behind the wall as seen from the road: the face in shadow, lit by its lanterns (DUSK_LIGHTS 1.4, the look-dev
          dusk level); the glow sits over the wall top in b22 and behind the narrator in b24.

WHERE EVERY BEAT IS FILMED (Blender blocks: +X east, +Y north, +Z up; ground z 0; a dirt path 1/16 lower)
    THE SQUARE (beats 1, 2, 3, 7, 8, 9, 10), golden
      squats       the plaza south of the well (the well x -3..2, y -3..2, the bell on its south side, the two bell
                   lamps at (-4, -4) and (0, -4) behind the squatters); Kai's lap = a ring round the well (the
                   village's own square_loop is wider; b01 used (1.3,-5.3)->(2.9,-3.0)->(3.6,0.4)->(2.4,3.6))
      stone row    STONE_ROW: eight stone blocks (5, -16..-9, 0) on the grass between the south street and house_a's
                   west front; engine.breaking Breakables, NOT in the World (crumbs land on the grass); P.stones[0] is
                   the south one (mined first, the camera at the south end). The oak at (4, -21) and the village lamp
                   post at (3, -19) are taken out (they stood in front of both cameras). Grass round the row cleared.
      bench        BENCH_BOX x -7..-5, y 4..8: a smooth-stone floor on the plaza's NW corner, a line north -> south:
                   torch spot (-6, 8, 0), dust (-6, 7, 0) (-6, 6, 0), repeater (-6, 5, 0) toward south, a stone block
                   (-6, 4, 0) (World) with the LAMP on it (-6, 4, 1), the PISTON east of that block (-5, 4, 0) facing
                   east (head into (-4, 4, 0)). The repeater powers the block, the block the lamp and the piston:
                   redstone.signal(torch.plant(f, player=efe), wire, repeater, (lamp, piston)) is the honest circuit.
                   house_c's door (west, (-10.5, 6.5)) is the backdrop of b07.
      column       COLUMN: upward piston (-4, 9, 0) on the grass north of the plaza, twelve iron blocks (-4, 9, 1..12),
                   one free cell above (it rises one block: the push limit is 12, exactly); its PIER (-4, 10, 0)
                   north of it with a floor LEVER on top (-4, 10, 1) facing north (handle 1.3 above the narrator's
                   feet: a plain swing meets it). 14 high, above every roof; the lamp post (-7, 9) beside it.
    THE PENS (beats 4, 5, 6, 17), golden: west of the exit road, north of house_e, south of the wall
      chicken_pen  ring x -23..-17, y 20..26, gate (-20, 20) (south side); inside x -22..-18, y 21..25
      cow_pen      ring x -14..-7, y 20..26, gate (-11, 20); inside x -13..-8, y 21..25. Both from engine.animals
                   pen_set (anchors <name>_center / _gate). Plants cleared south of the pens (x -24..-6, y 17..19:
                   where beat 4's track rides) and between the cow pen and the road. The players face EAST (the road
                   and the sun) in beats 4-6 and 17: their faces are lit.
    THE ANVIL WALL (beats 11-16, 18-24): west of the exit road, north of the exit gate (0.5, 24.5)
      wall         stone bricks, x -4..-2 (3 thick), y 27..60 (34 long), z 0..17 (the walkway is z 18); its ROAD FACE is
                   the plane x = -1.0 and looks east. The exit road's dirt path (x -1..1) runs along it.
      stair        18 stone-brick stairs on the road face at its south end, ascending north: step k at (-1, 27+k, k),
                   a solid ramp under it; the top step (-1, 44, 17) is level with the walkway; the climbers turn west
                   onto the wall top there. stair_z(y) = the game's half-step heights; path "stair_climb" follows
                   them (vertical half-step nodes: a player "pops" up as in the game), "stair_ramp" is one straight
                   ramp (floats up to 0.25 above the steps). The stair is 1 wide, no rail; open air on its east side.
      the row      twelve STICKY PISTONS in the top course, (-2, 46..57, 17), facing east (kit parts: the cells are
                   empty in the World); extended: head (-1, y, 17), PLANK (0, y, 17) = 2 blocks out from the face;
                   retracted: the plank at (-1, y, 17) against the face. ANVILS on the planks: (0, y, 18), facing east
                   (gaps between them along the row). Piston 0 is the south one, piston 11 the north one = "the
                   twelfth" (beats 13, 14, 24: next to the lever).
      dust/lever   redstone dust on the blocks behind the pistons, (-3, 46..59, 18) (14 cells: one behind each piston,
                   two more to the lever's pier); the PIER (-3, 60, 18) at the wall top's NORTH end with the floor
                   LEVER (-3, 60, 19) on it, facing east; the narrator stands east of it (lever_narrator, Lever.stand()).
                   Lever on -> pier strongly powered -> dust power 15 at y 59 .. 2 at y 46 (bright at the lever, dull at
                   the far end) -> each dust powers the block under it -> the piston beside that block. Lever off ->
                   the whole line dark in one frame, the twelve retract on the same tick, the sticky heads pull the
                   planks one block in: t = P.lever.flip(f); redstone.unsignal(t, P.wire, P.row).
                   WHY THE NORTH END: from there the road beyond the wall's end, where the patrol comes from, is in
                   view (beat 18); two blocks of wall top between the last plank and the lever keep a figure there
                   visible from the road (beat 21: further south the retracted planks hide him from below).
      strip        cobblestone paving x -1..1, y 45..57 (top z 0) under the shelf: every anvil lands as a block in
                   (0, y, 0) after a fall of 18 (fixtures.landing_cell, checked): 34 damage, 25.5 to the captain with
                   the banner (health 24): all five die. The road north of y 57 is the meadow (z 1 from y 58, 2 from
                   y 71-72, 3 from y 78): the patrol's path "patrol_road" (sets.ground_path) has its hops.
      lanterns     WALL_LANTERNS on the wall top (front edge over the stair, the key lantern (-4, 60, 18) beside the
                   lever, the back edge over the shelf; group "legday_wall"); FACE_LANTERNS hanging under stone-brick
                   corbels on the road face (-1, 31, 9) (-1, 37, 14) (-1, 49, 11) (-1, 55, 11): the ones a road camera
                   sees (clear of the climbers' heads and of the anvils' column x 0).
      meadow       the terrain is carried on north to y 150 (b.extend_terrain, 8,975 columns; the village's disc ended
                   at y 84 and a camera on the wall top looking north saw the void); a small oak LONE_OAK (3, 81) on
                   the meadow up the road behind the patrol (beat 15). 108,519 faces with the parts (village 77,391).

THE PARTS (make_parts(v) -> Parts, a dict; register what a shot shows with the Stage: st.cast[p.name] = p; st.use(s, p);
           an unregistered part is in every shot). Built in the ARMED state: lever on, the wall's dust lit from frame
           `armed_from` (1), the row extended with its planks, twelve anvils on them; bench dark, column down.
    P.kit                     engine.redstone kit of the village
    P.row                     PistonRow "wall_row": .pistons[0..11], .blocks[0..11] (the planks); retract(f) / extend(f)
    P.wire, P.lever           "wall_dust" (source = the pier), "wall_lever"
    P.anvils, P.anvils_dusk   12 + 12 fixtures.Block anvils (0, 46..57, 18) "anvil_1..12" / "anvil_dusk_1..12": the
                              first set falls in beat 19 and lies on the road after it; the dusk twin set is the one
                              that is "back up" in beats 22-24. Show each set in its own shots only (they coincide).
    P.stones                  8 Breakables "stone_row_1..8" (breaking.mine(steve, P.stones[0], f, duration=48, camera=s))
    P.bench                   dict(torch, wire, repeater, lamp, piston) ("bench_*"); the torch is there unless plant()ed
    P.column                  dict(piston (up), blocks (12 iron, kit movables), lever) ("column_*"): t = lever.flip(f);
                              piston.power(t) lifts all twelve one block in 2 ticks
  Sequencing notes (the directors'): the twelfth piston (beat 13) is built extended with the row: pistons[11].
  retract(early, pull=None); .place(f, player=efe); .extend(f) (checked: short head ON f, long head f+1, out by f+3,
  the dust being lit); its plank P.row.blocks[11].show(1, False) and show(f_set, True) when he sets it;
  release in beat 19 = fixtures.release(P.anvils, f_retract, world=v): ANVILS LAND 41 frames after the release (2.4
  hang + 33 ticks); illagers.crush_patrol(patrol, drops, camera=s, stage=st, knockback=False, village=v, spots=
  [bottle_spot, banner_spot]) kills all five when the captain's feet are at y 45.71..50.29 (x 0.5) on the landing
  frame (march_window(); b19 used 47.0: march start y 50.74 on the shot's first frame with the release on frame +6).
  Before beat 22 the row must be out again (row.extend(f) takes 2.4 frames: key it between beats).

ANCHORS (v.anchors[name] = (x, y, z); v.yaws[name] = the facing; 2D entries were put on the ground)
    square   squat_steve (-0.55,-5.55) squat_zuri (-1.75,-6.45) squat_ari (0.75,-6.35) facing S; narrator_far (-6.0,3.2);
             mine_1 (4.22,-15.5) / mine_2 (4.22,-14.5) facing E (beside stones 1 and 2); pickaxe_target (1.25,-14.5)
             (3 blocks behind his back: out of pick-up reach); bench_narrator (-7.3,6.6) facing E (beside the dust);
             arms_narrator (-5.98,3.15) / arms_steve (-5.02,3.15) facing S (in front of the lamp, the lamp's centre
             x -5.5 between their near arms); column_steve (-5.25,9.45) facing E (at its west foot); column_narrator
             (-2.95,11.25) (NE of the lever's pier); column_walk_end (-2.8,5.4) (beat 10: toward the well)
    pens     kai_chickens (-19.6,22.6); zuri_cow (-11.3,22.5); cow_milk_target (-10.0,23.3) (the milked cow);
             narrator_fence (-10.55,19.35) facing N (outside the cow pen's south fence); hide_1..4 (-10.3,21.9)
             (-10.45,23.3) (-10.3,24.75) (-11.45,23.95) facing E, behind hide_cow_1..3_target (-8.7, 21.65 / 23.3 /
             24.95) (three cows end to end along the east fence); arrow_post_target (-6.55,22.45) (east fence post)
    wall     stair_foot (-0.5,26.3) N; stair_top (-0.5,44.75,18) W; wall_top_south (-1.5,44.6,18); lever_narrator
             (-1.7,60.28,18) W; narrator_edge (-1.25,60.5,18) (at the front edge: seen from the road, beat 21);
             place_12th (-2.55,57.55,18) E (beside the twelfth gap (-2,57,17)); set_anvil_12th (-2.6,58.45,18) SE;
             wall_top_north (-2.5,59.4,18); wall_top_lever_cam (camera spot, beat 14); plank_1..12_target (0.5, y+0.5,
             18) where each anvil stands; land_1..12_target (0.5, y+0.5, 0) where it lands
    road     road_shelf_south (0.5,44); road_shelf_north (0.5,58.6); runners_stop (0.55,39.2); steve_among_anvils
             (1.45,48.15) (2+ blocks short of the drops); banner_spot_target (1.5,50.7), bottle_spot_target (1.5,51.5)
             (drops() spots, outside the anvil cells); patrol_far (0.5,82)
  PATHS: stair_climb, stair_ramp, wall_top (x -1.5, over the pistons), wall_top_dust (x -2.5, on the dust),
         patrol_road (0.5, 84 -> 40, with the meadow's hops at y 78, 71, 57), run_out (0.6, 18 -> 40); the village's
         own (square_loop, exit_road ...) are unchanged.
  CUTAWAYS: none (no interior is filmed).

THE SUGGESTED CAMERAS (CAMERAS; every one rendered with stand-ins posed as the beat says, at 540x960 / 16 samples under
its sky, and looked at; palette_check passes on all but b24, see LIGHT)
    b01 squats      low south of the trio, the well and bell behind; faces y 45 %, anvils 54 %; the narrator small at
                    the left edge (x 12 %: further right he is behind the well); Kai mid-jump at the right
    b02 punch       from the row's south-east end, 24 mm: Steve in profile (lit face), the cracked stone, the row
                    receding to its right; the column and the wall's south end in the background
    b03 row         the pull-back from the south street: Steve at stone 2, stone 1 gone, the row as a low line, the
                    pickaxe on the path at the left (3 blocks behind him, same distance from the lens)
    b04 pens        a 3.6 s linear track west -> east along the south fences at 1.45 (above the top rail: hens):
                    _a Kai eating among four hens, _b Zuri drinking beside the cow
    b05 milk        Zuri and the cow both toward the lens over the south fence (bucket low: 65 %)
    b06 fence       over the narrator's right shoulder (his torch's glow soft at the left), Zuri drinking, the cow at
                    the lens
    b07 bench       from the east: the lit lamp left, repeater and dust on the bench floor, the narrator facing the
                    lens in front of house_c's door, the planted torch right. (Front light: the sun is behind the lens)
    b08 arms        frontal 50 mm, 3.85 away: the slim near arm (3 px) beside Steve's (4 px), each over an eighth of the
                    frame wide, the lit lamp between their heads behind; heads at x 20 / 82 % (Steve's at the edge)
    b09 column      16..18 mm low SE, tilting up (target -> target1): _a Steve at the foot (47 %), the narrator at the
                    pier; _b the column's top against the sky
    b10 cheating    low from the well side, 16 mm: Steve walking at the lens, the whole column up against the sky, the
                    narrator small at the lever; the wall's south end shows behind (it is in every northward square view)
    b11 climb       low SE of the wall: the face, the stair with four climbers, the hanging lanterns; the shelf seen
                    from below: THE ANVILS ON IT SHOW ONLY AS A SLIVER over the planks (the planks in front of each
                    anvil hide it from any camera below and south of the shelf). b11e (from across the road, east):
                    the whole wall, the anvils read on the planks, the climbers small at the left edge
    b12 legs        beside the stair's open edge at knee height: Steve's legs and anvil climbing past (Kai below,
                    entering later)
    b13 twelfth     above the road beyond the north end, looking back along the row: the narrator at the twelfth gap,
                    the sticky head out (green face), eleven planks with anvils receding, the lit dust, lanterns
    b14 dust        on the wall top by the lever, the glowing dust leading away: Steve walking at the lens over it
                    with his anvil, the narrator soft beyond
    b15 patrol      85 mm from 3.9 above the strip, over the meadow's steps (a lower camera sees them as dirt bands):
                    the file staggered, the captain's banner, the lone oak, a clean horizon
    b16 run         low on the east verge ahead of the runners (the stair ramp on the right); three arrows stuck in the
                    road in front of them (y 62 %)
    b17 cows        from the road side through the east fence, 1.1 high: the four STANDING (the story's fallback:
                    crouched, their eyes are below the cows' backs from any camera under 1.8), the cows covering them
                    to the neck, the near cow at the lens, the arrows in the fence post (y 64 %)
    b18 lever       behind the lever on the wall top, looking NNE and down: the lever big, the narrator's arm in from
                    the right, the dust, and far below the patrol on the meadow road (tiny: about 20 blocks away)
    b19 drop        low on the road south of the shelf, 16 mm, looking along the wall foot: the file under the shelf
                    (faces 50-55 %), the near anvils above the frame top at release, entering as they fall, the far
                    ones in frame; the pillagers' shadows on the face. All five struck, all lethal (printed)
    b20 drops       the push in: _a the twelve anvils on the strip, _b the banner and the bottle filling the middle
    b21 cheating    low 16 mm 3 blocks from Steve among the anvils, up the face: the narrator tiny at the wall top's
                    north-east corner (narrator_edge; from lever_narrator he is hidden by the edge)
    b22 climb       = b11 at dusk (the narrator by the lever is NOT visible from here: behind the shelf and the edge)
    b23 legs        = b12 at dusk
    b24 reloading   above the road south-east of the lever: the armed row of anvils (dusk set) receding to Steve
                    setting the twelfth and the narrator at the lever with his arm up, the dusk sky behind

LIGHT
    Daylight: torches at 1.0 (Stage.lights). Dusk: DUSK_LIGHTS 1.4 for every lantern; the narrator's key in b24 is his
    held redstone torch (B24_TORCH_WATTS = HELD_TORCH_KEY_WATTS). palette_check FAILS "stone not magenta" in b24 at G/R
    0.90 (rgb 123,111,105: warm, B under G, not magenta; with the lanterns OFF it is 0.87): it is the dusk sky on the
    wall top, not the lamps (the rule cannot tell warm from magenta: fixtures' notes). b22 / b23 pass (0.94-0.96).

NOT VERIFIED / LEFT TO THE DIRECTORS: no animation was rendered (stills only: walks, climbs, the fall, the retraction
are numbers); the stand-ins' poses are single frames; the sky change between beat 21 and 22 and the re-extension of
the row are not keyed; nothing was rendered at final settings through render.py (this is no film yet).
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from engine import animals, breaking, fixtures, redstone, sets, village   # noqa: E402

# ------------------------------------------------------------------------------------------------------------------
# the skies the set was built for (degrees counter-clockwise from east; see the docstring)
# ------------------------------------------------------------------------------------------------------------------
SKIES = {
    "gold": dict(preset="golden", az=0.0, el=27.0, bloom=1.0, grade="warm"),
    "dusk": dict(preset="dusk", az=185.0, el=5.0, bloom=1.3, grade="warm"),
}

# ------------------------------------------------------------------------------------------------------------------
# THE ANVIL WALL (beats 11-16, 18-24), west of the exit road, north of the exit gate; its road face looks EAST
# ------------------------------------------------------------------------------------------------------------------
WALL_BLOCK = "stone_bricks"
STAIR_BLOCK = "stone_brick_stairs"
WALL_X = (-4, -2)                 # the wall's three columns (x cells); its road face is the plane x = -1.0
WALL_Y = (27, 60)                 # its south and north end cells (34 blocks long)
TOP_Z = 17                        # the top course (pistons, the blocks under the dust); the walkway is z 18
WALK_Z = TOP_Z + 1.0              # the wall top a character stands on
STAIR_X, STAIR_Y0, STEPS = -1, 27, 18     # step k = (x -1, y 27 + k, z k), facing north, solid under it
ROW_Y = tuple(range(46, 58))      # the twelve sticky pistons: (-2, y, 17), facing east, y 46 (south) .. 57 (north)
PISTON_X, HEAD_X, PLANK_X = -2, -1, 0     # piston, its head, the plank on its arm (extended); retracted: plank x -1
DUST_X = -3                       # the line of dust on the wall top (on the blocks behind the pistons), z 18
DUST_Y = tuple(range(46, 60))     # 14 cells: one behind every piston (46..57), 58, and 59 beside the lever's pier
PIER = (-3, 60, 18)               # the block at the NORTH end of the wall top the lever stands on, in line with the
#                                   dust (handle 1.3 above the walkway); from there the road beyond the wall's end is
#                                   in view, where the patrol comes from (beat 18)
LEVER = (-3, 60, 19)              # the floor lever (facing east): it powers the pier, the pier the dust beside it
#                                   (power 15 at y 59 .. 2 at y 46: the far end is the dullest). Two blocks of wall
#                                   top between the last plank (y 57) and the lever: seen from the road, a figure
#                                   by the lever is not hidden behind the retracted planks (beat 21)
STRIP_X, STRIP_Y = (-1, 1), (45, 57)      # cobblestone paving at the wall's foot under the shelf (top z 0)
ANVIL_Z = TOP_Z + 1               # the anvils stand on the planks: cells (0, y, 18); they land in (0, y, 0)
WALL_LANTERNS = [(-2, 31, 18), (-2, 35, 18), (-2, 39, 18), (-2, 43, 18),          # front edge over the stair
                 (-4, 60, 18),                                                    # beside the lever: the face key
                 (-4, 49, 18), (-4, 53, 18), (-4, 57, 18)]                        # back edge over the shelf
NORTH_MEADOW = (-60, 70, 60, 150)   # extend_terrain box (only columns without terrain are added)
# lanterns hanging under stone-brick corbels on the road face (seen from the road: the wall-top ones are not), clear of
# the climbers' heads on the stair and of the anvils' fall (x 0): (corbel cell; the lantern hangs in the cell below)
FACE_LANTERNS = [(-1, 31, 10), (-1, 37, 15), (-1, 49, 12), (-1, 55, 12)]
LONE_OAK = (3, 81)                # a small oak on the meadow's horizon up the road, behind the patrol (beat 15)
FOOT_LANTERNS = []                # (none on the road: a post on the verge stood in the money shot's view)
B24_TORCH_WATTS = redstone.HELD_TORCH_KEY_WATTS   # beat 24: the held redstone torch as the key on his face
DUSK_LIGHTS = 1.4                 # every lantern at dusk: the look-dev dusk level (not more: lit stone beside a lantern
#                                   sits on palette_check's limit; see the docstring, LIGHT)

# ------------------------------------------------------------------------------------------------------------------
# THE PENS (beats 4-6, 17), west of the exit road between house_e and the wall
# ------------------------------------------------------------------------------------------------------------------
CHICKEN_PEN = dict(box=(-23, 20, -17, 26), gates=[(-20, 20)], name="chicken_pen")
COW_PEN = dict(box=(-14, 20, -7, 26), gates=[(-11, 20)], name="cow_pen")

# ------------------------------------------------------------------------------------------------------------------
# THE SQUARE (beats 1-3, 7-10)
# ------------------------------------------------------------------------------------------------------------------
STONE_ROW = [(5, y, 0) for y in range(-16, -8)]          # eight stone blocks on the grass south-east of the plaza
STONE_ROW_LAMP = (3, -19)                                # the village lamp post taken out (beats 2-3 look past it)
BENCH_BOX = (-7, 4, -5, 8)                               # the smooth-stone floor of the open-air bench (NW corner)
# a line north -> south: the torch's spot at its head, two dust, a repeater, the stone block with the lamp on it,
# the piston east of that block (the repeater powers the block, the block the lamp above it and the piston)
BENCH = dict(torch=(-6, 8, 0), dust=[(-6, 7, 0), (-6, 6, 0)], repeater=(-6, 5, 0), repeater_toward="south",
             block=(-6, 4, 0), lamp=(-6, 4, 1), piston=(-5, 4, 0), piston_facing="east")
COLUMN = dict(piston=(-4, 9, 0), pier=(-4, 10, 0), lever=(-4, 10, 1), lever_facing="north", blocks=12)


def _box_cells(x0, y0, x1, y1):
    return [(x, y) for x in range(min(x0, x1), max(x0, x1) + 1) for y in range(min(y0, y1), max(y0, y1) + 1)]


def stair_z(y):
    """The walking height on the wall's stair at y (the game's half steps: front half k + 0.5, back half k + 1)."""
    k = math.floor(y - STAIR_Y0)
    if k < 0:
        return 0.0
    if k >= STEPS:
        return WALK_Z
    return k + (0.5 if (y - STAIR_Y0 - k) < 0.5 else 1.0)


# ------------------------------------------------------------------------------------------------------------------
# the hook: everything the story adds INTO the village's World (meshed, lit and checked like the village's own)
# ------------------------------------------------------------------------------------------------------------------
def _clear_column(b, x, y, z0, z1):
    """Plants off the column and nothing but air in cells z0..z1 (refuses to take out a building block)."""
    b.clear_plants(x, y)
    for z in range(z0, z1 + 1):
        st = b.w.get(x, y, z)
        if st is not None:
            raise ValueError("legday_set: cell %s holds %s: the set piece would cut into the village" % ((x, y, z), st[0]))


def anvil_wall(b):
    """The anvil wall (see the constants and the docstring): stone-brick wall 3 thick, 18 high, 32 long; stair up its
    south end on the road face; top course open for the twelve sticky pistons (kit parts); the lever's pier; the
    cobblestone strip under the shelf; lanterns. Returns its dict (also Village.sets['legday']['wall'])."""
    w = b.w
    (x0, x1), (y0, y1) = WALL_X, WALL_Y
    b.allow((x0 - 1, y0 - 1, STRIP_X[1] + 2, y1 + 1))            # the exit road's dirt path runs under the stair
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            g = b.ground(x, y)
            _clear_column(b, x, y, int(g), TOP_Z + 3)
            for z in range(min(0, int(g)), TOP_Z + 1):
                w.set(x, y, z, WALL_BLOCK)
            b.reserved.add((x, y))
    # the top course: the piston cells stay empty (engine.redstone draws them); the cells behind them are the wall
    for y in ROW_Y:
        w.set(PISTON_X, y, TOP_Z, None)
    # the stair: 18 stone-brick stairs up the road face, ascending north, a solid stone-brick ramp under them
    for k in range(STEPS):
        y = STAIR_Y0 + k
        _clear_column(b, STAIR_X, y, 0, k + 3)
        for z in range(0, k):
            w.set(STAIR_X, y, z, WALL_BLOCK)
        w.set(STAIR_X, y, k, STAIR_BLOCK, {"facing": "north", "half": "bottom", "shape": "straight",
                                            "waterlogged": "false"})
        b.reserved.add((STAIR_X, y))
    # the lever's pier on the wall top (the lever itself is a kit part on top of it)
    w.set(PIER[0], PIER[1], PIER[2], WALL_BLOCK)
    # cobblestone paving at the foot under the shelf: a falling anvil lands on a full block (a dirt path breaks it)
    for x in range(STRIP_X[0], STRIP_X[1] + 1):
        for y in range(STRIP_Y[0], STRIP_Y[1] + 1):
            g = int(b.ground(x, y))
            if g != 0:
                b.set_ground(x, y, 0)
            _clear_column(b, x, y, 0, TOP_Z - 1)
            w.set(x, y, -1, "cobblestone")
            b.reserved.add((x, y))
    # what the falling anvils and the moving planks pass through must be empty (above the strip: checked above)
    for y in ROW_Y:
        for x in (HEAD_X, PLANK_X):
            for z in (TOP_Z, TOP_Z + 1):
                if w.get(x, y, z) is not None:
                    raise ValueError("legday_set: (%d, %d, %d) must stay empty for the shelf" % (x, y, z))
    for c in WALL_LANTERNS:
        b.torch(c, "lantern", {}, group="legday_wall")
    for x, y, z in FACE_LANTERNS:
        if w.get(x, y, z) is not None or w.get(x, y, z - 1) is not None:
            raise ValueError("legday_set: the face lantern at %s needs two empty cells" % ((x, y, z),))
        w.set(x, y, z, WALL_BLOCK)
        b.torch((x, y, z - 1), "lantern", {"hanging": "true"}, group="legday_wall")
    for c in FOOT_LANTERNS:
        g = int(b.ground(c[0], c[1]))
        b.clear_plants(c[0], c[1])
        w.set(c[0], c[1], g, "cobblestone_wall", {"up": "true"})
        b.torch((c[0], c[1], g + 1), "lantern", {}, group="legday_road")
        b.reserved.add((c[0], c[1]))
    return dict(x=WALL_X, y=WALL_Y, top_z=TOP_Z, walk_z=WALK_Z, face_x=float(WALL_X[1] + 1), stair=dict(
        x=STAIR_X, y0=STAIR_Y0, steps=STEPS, foot=(STAIR_X + 0.5, STAIR_Y0 - 0.6, 0.0),
        top=(STAIR_X + 0.5, STAIR_Y0 + STEPS - 0.3, WALK_Z)), row_y=ROW_Y, pier=PIER, lever=LEVER,
        strip=(STRIP_X, STRIP_Y), lanterns=list(WALL_LANTERNS), face_lanterns=list(FACE_LANTERNS))


def pens(b):
    """The chicken pen and the cow pen (engine.animals.pen_set), side by side west of the exit road."""
    out = {}
    for spec in (CHICKEN_PEN, COW_PEN):
        x0, y0, x1, y1 = spec["box"]
        out[spec["name"]] = animals.pen_set(b, x0, y0, x1, y1, gates=spec["gates"], name=spec["name"])
    # the ground between the pens and south of them is where the tracking camera of beat 4 rides: no tufts there
    for x in range(CHICKEN_PEN["box"][0] - 1, COW_PEN["box"][2] + 2):
        for y in range(CHICKEN_PEN["box"][1] - 3, CHICKEN_PEN["box"][1]):
            if b.ground(x, y) is not None:
                b.clear_plants(x, y)
                b.reserved.add((x, y))
    for x in range(COW_PEN["box"][2] + 1, WALL_X[0]):            # between the cow pen and the road: open ground
        for y in range(COW_PEN["box"][1], COW_PEN["box"][3] + 1):
            b.clear_plants(x, y)
    return out


def square(b):
    """The square's pieces: the bench floor (engine.redstone.bench) with the stone block under the lamp and the
    upward piston's pier; the stone row's and the column's cells cleared (they are parts, drawn after the build)."""
    w = b.w
    x0, y0, x1, y1 = BENCH_BOX
    b.allow((x0, y0, x1, y1))                                     # it is laid on the plaza (dirt path)
    bench = redstone.bench(b, x0, y0, x1, y1, block="smooth_stone", name="legday_bench", level=0)
    w.set(*BENCH["block"], "stone")
    # the column: piston + 12 iron blocks + 1 block of rise, all parts; the pier with the lever on top
    cx, cy, cz = COLUMN["piston"]
    b.allow((cx - 1, cy - 1, cx + 1, cy + 1))
    _clear_column(b, cx, cy, cz, cz + COLUMN["blocks"] + 2)
    px, py, pz = COLUMN["pier"]
    _clear_column(b, px, py, pz, pz + 2)
    w.set(px, py, pz, "stone")
    for c in ((cx, cy), (px, py)):
        b.reserved.add(c)
    # the oak south of the row (trunk at (4, -21)) and the village lamp post at (3, -19) stand where the cameras of
    # beats 2 and 3 look along the row: both taken out (this corner is the film's own)
    tree = b.tree_at(4, -21, radius=1.5)
    if tree is not None:
        sets.remove_tree(b, tree)
    lx, ly = STONE_ROW_LAMP
    b.allow((lx - 1, ly - 1, lx + 1, ly + 1))
    for x in range(lx - 1, lx + 2):
        for y in range(ly - 1, ly + 2):
            for z in range(0, 6):
                if b.w.block_id(x, y, z) in ("oak_fence", "stripped_oak_wood", "wall_torch", "torch", "oak_log"):
                    b.w.set(x, y, z, None)
    # the stone row: cells cleared (the blocks are engine.breaking Breakables, drawn after the build)
    for x, y, z in STONE_ROW:
        _clear_column(b, x, y, z, z + 2)
        b.reserved.add((x, y))
    for x in range(STONE_ROW[0][0] - 3, STONE_ROW[0][0] + 2):    # bare grass round the row (an absence must read)
        for y in range(STONE_ROW[0][1] - 1, STONE_ROW[-1][1] + 2):
            if b.ground(x, y) is not None:
                b.clear_plants(x, y)
    return dict(bench=bench, bench_parts=dict(BENCH), column=dict(COLUMN), stone_row=list(STONE_ROW))


def legday_set(b):
    """THE HOOK PIECE of "Leg Day": the anvil wall, the pens, the square's bench, column and stone row, the anchors
    and paths. Call it inside village.build_village(scene, seed=1, edit=...). Returns the dict stored as
    Village.sets['legday'] (wall, pens, square, cameras)."""
    sets._new_name(b, "legday")
    res = dict(wall=anvil_wall(b), pens=pens(b), square=square(b))
    _anchors(b)
    _paths(b)
    res["lone_oak"] = sets.plant_oak(b, LONE_OAK[0], LONE_OAK[1], b.rng_for("legday lone oak"), height=5)
    # the meadow carried on north beyond the village's disc of terrain (it ends at y 84): a camera on the wall top
    # looking north saw the void (the sky's horizon colour) below the horizon (beats 18, 24)
    res["meadow_north"] = len(b.extend_terrain(*NORTH_MEADOW))
    for c in CAMERAS.values():                                     # no tuft between a low camera and its subject
        if c["pos"][2] < 3.0 and b.ground(c["pos"][0], c["pos"][1]) is not None:
            sets.clear_view(b, c["pos"], c.get("target1", c["target"]), 2.4)
            sets.clear_view(b, c["pos"], c["target"], 2.4)
    res["cameras"] = {k: dict(v) for k, v in CAMERAS.items()}
    b.v.sets["legday"] = res
    return res


def build_set(scene):
    """The village of "Leg Day": seed 1 with legday_set built in. Returns the Village (v.sets['legday'])."""
    return village.build_village(scene, seed=1, edit=legday_set)


# ------------------------------------------------------------------------------------------------------------------
# anchors and paths (registered on the Village; 2D = on the ground there, 3D = exactly there)
# ------------------------------------------------------------------------------------------------------------------
def _yaw(facing):
    """Yaw of a character facing a compass direction (characters face -Y at yaw 0); also the four diagonals."""
    if facing in ("northeast", "northwest", "southeast", "southwest"):
        dx = 1.0 if "east" in facing else -1.0
        dy = 1.0 if "north" in facing else -1.0
        return math.atan2(dx, -dy)
    return village.yaw_of(facing)


def _row_cell(i):
    """(x, y, z) of piston i (0 = the south one, by the lever) of the wall's row."""
    return (PISTON_X, ROW_Y[i], TOP_Z)


ANCHORS = {
    # ---- the square: beat 1 (the squats in front of the well, facing south; the narrator far back by his bench)
    "squat_steve": ((-0.55, -5.55), "south"), "squat_zuri": ((-1.75, -6.45), "south"),
    "squat_ari": ((0.75, -6.35), "south"), "narrator_far": ((-6.0, 3.2), "south"),
    # ---- beats 2-3: Steve punching the stone row (he stands west of it, facing east, the camera at its south end)
    "mine_1": ((4.22, -15.5), "east"), "mine_2": ((4.22, -14.5), "east"),
    "pickaxe_target": ((1.25, -14.5), None),                    # the dropped iron pickaxe: 3 blocks behind his back
    # ---- beats 7-8: the bench (the narrator south of it facing north; the two-shot in front of the lamp, facing south)
    "bench_narrator": ((-7.3, 6.6), "east"),
    "arms_narrator": ((-5.98, 3.15), "south"), "arms_steve": ((-5.02, 3.15), "south"),
    # ---- beats 9-10: the column (Steve at its south foot looking down at the piston; the narrator east of the pier)
    "column_steve": ((-5.25, 9.45), "east"), "column_narrator": ((-2.95, 11.25), "southwest"),
    "column_walk_end": ((-2.8, 5.4), None),                     # beat 10: where Steve's walk to the well ends
    # ---- the pens (pen_set adds chicken_pen_center / _gate, cow_pen_center / _gate)
    "kai_chickens": ((-19.6, 22.6), "south"), "zuri_cow": ((-11.3, 22.5), "south"),
    "cow_milk_target": ((-10.0, 23.3), None),                   # where the milked cow stands (beats 4-6)
    "narrator_fence": ((-10.55, 19.35), "north"),               # outside the cow pen's south fence (beat 6)
    "hide_1": ((-10.3, 21.9), "east"), "hide_2": ((-10.45, 23.3), "east"), "hide_3": ((-10.3, 24.75), "east"),
    "hide_4": ((-11.45, 23.95), "east"),                        # beat 17: behind the cows, heads toward the road
    "hide_cow_1_target": ((-8.7, 21.65), None), "hide_cow_2_target": ((-8.7, 23.3), None),
    "hide_cow_3_target": ((-8.7, 24.95), None),                 # three cows end to end along the east fence
    "arrow_post_target": ((-6.55, 22.45), None),                # the east fence post (x -7, y 22), its road face
    # ---- the wall: road, stair, top
    "stair_foot": ((-0.5, 26.3), "north"),
    "stair_top": ((-0.5, 44.75, WALK_Z), "west"),               # the back half of the top step: as high as the walkway
    "wall_top_south": ((-1.5, 44.6, WALK_Z), "north"),
    "lever_narrator": ((-1.7, 60.28, WALK_Z), "west"),          # redstone Lever.stand() of the lever (checked later)
    "place_12th": ((-2.55, 57.55, WALK_Z), "east"),             # beat 13: he sets the 12th piston into (-2, 57, 17)
    "set_anvil_12th": ((-2.6, 58.45, WALK_Z), "southeast"),     # beat 14 / 24: Steve sets the 12th anvil on plank 12
    #                                                             (on the dust: from the road side he is then not in
    #                                                             front of the narrator at the lever)
    "wall_top_north": ((-2.5, 59.4, WALK_Z), "south"),
    "wall_top_lever_cam": ((-2.45, 59.75, WALK_Z + 0.22), None),   # (a camera spot: beat 14, on the walkway)
    # ---- the road under the shelf and beyond
    "road_shelf_south": ((0.5, 44.0), "north"), "road_shelf_north": ((0.5, 58.6), "south"),
    "runners_stop": ((0.55, 39.2), "north"),                    # beat 16: the three stop dead here (Steve)
    "steve_among_anvils": ((1.45, 48.15), "north"),             # beat 21: 2 blocks short of the drops
    "narrator_edge": ((-1.25, 60.5, WALK_Z), "southeast"),      # beat 21: at the front edge by the lever, looking
    #                                                             down (0.7 further back the edge hides him from below)
    "banner_spot_target": ((1.5, 50.7), None), "bottle_spot_target": ((1.5, 51.5), None),
    "patrol_far": ((0.5, 82.0), "south"),
}


def _anchors(b):
    """Register ANCHORS (2D on the ground; names ending in _target are look targets) and the row's per-anvil points."""
    for name, (p, facing) in ANCHORS.items():
        yaw = _yaw(facing) if facing else None
        b.anchor(name, p, yaw)
    for i, y in enumerate(ROW_Y):
        b.anchor("plank_%d_target" % (i + 1), (PLANK_X + 0.5, y + 0.5, float(TOP_Z + 1)))     # an anvil stands here
        b.anchor("land_%d_target" % (i + 1), (PLANK_X + 0.5, y + 0.5, 0.0))                 # ... and lands here


def _paths(b):
    """Walks the beats need: the climb (road -> stair -> walkway), the wall top, the patrol's road (with the
    meadow's hops), the runners' road, Kai's lap round the well (the village's square_loop)."""
    climb = [(-0.5, 22.5, b.walk_z(-0.5, 22.5)), (-0.5, 26.2, b.walk_z(-0.5, 26.2))]
    for k in range(STEPS):                                      # one node per half step: the game's step heights
        y = STAIR_Y0 + k
        climb += [(-0.5, y + 0.02, k + 0.5), (-0.5, y + 0.52, k + 1.0)]
    climb += [(-0.5, STAIR_Y0 + STEPS - 0.25, WALK_Z), (-1.5, STAIR_Y0 + STEPS - 0.25, WALK_Z)]
    b.path("stair_climb", climb)
    b.path("stair_ramp", [(-0.5, 22.5), (-0.5, 26.5, 0.0)] +       # the same climb as one straight ramp (floats
           [(-0.5, STAIR_Y0 + STEPS - 0.5, WALK_Z)])                #   at most 0.25 above the steps; see stair_z)
    b.path("wall_top", [(-1.5, 44.6, WALK_Z), (-1.5, 57.4, WALK_Z)])
    b.path("wall_top_dust", [(-2.5, 44.6, WALK_Z), (-2.5, 57.4, WALK_Z)])
    sets.ground_path(b, "patrol_road", [(0.5, 84.0), (0.5, 66.0), (0.5, 58.6), (0.5, 40.0)])
    sets.clear_view(b, (0.5, 84.0), (0.5, 56.0), 1.6)            # the patrol's legs in the meadow grass
    sets.ground_path(b, "run_out", [(0.6, 18.0), (0.6, 26.0), (0.55, 40.0)])


# ------------------------------------------------------------------------------------------------------------------
# the parts: what changes on camera (built AFTER build_village, into the cells the hook left empty)
# ------------------------------------------------------------------------------------------------------------------
class Parts(dict):
    """The film's moving parts (a dict with attribute access): see make_parts()."""

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)


def make_parts(v, armed_from=1):
    """Build every moving part of the set, after build_village, in its ARMED state (the state of most beats):
    lever on, the wall's dust lit from frame `armed_from`, the twelve sticky pistons out with their planks, twelve
    anvils on the planks; the bench dark (its torch not yet planted: plant() it), the column down, the stone row
    whole. Returns Parts:
      kit                       engine.redstone kit of the Village
      row                       PistonRow: 12 sticky pistons (-2, 46..57, 17) facing east, .blocks = their planks
                                (index 0 = the south one, beside the lever: "the twelfth", placed in beat 13)
      wire / lever              the wall's dust (-3, 45..57, 18) (power 15 beside the pier .. 3 at the north end)
                                and the floor lever on the pier (-4, 45, 19), facing east
      anvils, anvils_dusk       12 fixtures.Block anvils on the planks (0, 46..57, 18), facing east (gaps between
                                them along the row); the dusk set is a twin in the same cells for beats 22-24 (the
                                first set lies on the road after beat 19): show each in its own shots
      stones                    8 engine.breaking Breakables (5, -16..-9, 0): STONE_ROW (index 0 = the south one)
      bench                     dict(torch, wire, repeater, lamp, piston): engine.redstone parts of beat 7
      column                    dict(piston (up), blocks (12 iron), lever (on the pier, facing east))
    Register what a shot shows with its Stage (st.cast[p.name] = p; st.use(shot, p)); a part nobody registers is in
    every shot."""
    from engine import breaking as _br

    k = redstone.kit(v)
    P = Parts(kit=k)
    # ---- the wall
    P["row"] = k.piston_row([_row_cell(i) for i in range(len(ROW_Y))], "east", carry="oak_planks",
                            extended=True, sticky=True, name="wall_row")
    P["lever"] = k.lever(LEVER, "floor", "east", powered=True, name="wall_lever")
    P["wire"] = k.wire([(DUST_X, y, TOP_Z + 1) for y in DUST_Y], source=PIER, name="wall_dust")
    P["wire"].power(armed_from, source=PIER)
    P["anvils"] = [fixtures.block(v, "anvil", (PLANK_X, y, ANVIL_Z), {"facing": "east"}, name="anvil_%d" % (i + 1))
                   for i, y in enumerate(ROW_Y)]
    P["anvils_dusk"] = [fixtures.block(v, "anvil", (PLANK_X, y, ANVIL_Z), {"facing": "east"},
                                       name="anvil_dusk_%d" % (i + 1)) for i, y in enumerate(ROW_Y)]
    # ---- the square
    P["stones"] = [_br.place_block(v.collection, "stone", c, world=v, name="stone_row_%d" % (i + 1))
                   for i, c in enumerate(STONE_ROW)]
    B = BENCH
    torch = k.torch(B["torch"], name="bench_torch")
    P["bench"] = dict(torch=torch,
                      wire=k.wire(B["dust"], source=B["torch"], name="bench_dust"),
                      repeater=k.repeater(B["repeater"], B["repeater_toward"], delay=1, name="bench_repeater"),
                      lamp=k.lamp(B["lamp"], name="bench_lamp"),
                      piston=k.piston(B["piston"], B["piston_facing"], name="bench_piston"))
    cx, cy, cz = COLUMN["piston"]
    P["column"] = dict(piston=k.piston(COLUMN["piston"], "up", name="column_piston"),
                       blocks=[k.block("iron_block", (cx, cy, cz + i), name="column_iron_%d" % i)
                               for i in range(1, COLUMN["blocks"] + 1)],
                       lever=k.lever(COLUMN["lever"], "floor", COLUMN["lever_facing"], name="column_lever"))
    return P


# ------------------------------------------------------------------------------------------------------------------
# A SUGGESTED CAMERA FOR EVERY BEAT: dict(pos, target, lens, fstop[, pos1, target1: a move], sky, still = the
# proof still out/test/legday_set_<beat>_<what>.png). Each was rendered at 540x960 / 16 samples under its sky with
# stand-ins placed as the beat says (stage_<beat> below) and looked at; the notes say what was measured.
# ------------------------------------------------------------------------------------------------------------------
CAMERAS = {
    "b01": dict(pos=(-0.55, -12.6, 0.32), target=(-0.5, -5.6, 0.75), lens=22.0, fstop=2.8, sky="gold",
                what="squats"),
    "b02": dict(pos=(7.0, -20.4, 0.8), target=(5.79, -15.55, 0.8), lens=24.0, fstop=2.4, sky="gold",
                what="punch"),
    "b03": dict(pos=(0.2, -23.2, 1.3), target=(3.73, -13.85, 0.7), lens=28.0, fstop=3.2, sky="gold",
                what="row"),
    "b04": dict(pos=(-21.0, 18.3, 1.45), target=(-20.2, 23.0, 1.0), pos1=(-11.8, 18.3, 1.45),
                target1=(-11.0, 23.0, 1.0), lens=32.0, fstop=2.8, sky="gold", what="pens", seconds=3.6),
    "b05": dict(pos=(-10.2, 17.6, 1.45), target=(-10.81, 22.46, 1.35), lens=50.0, fstop=2.4, sky="gold",
                what="milk"),
    "b06": dict(pos=(-9.4, 18.2, 1.2), target=(-11.27, 22.84, 1.3), lens=32.0, fstop=2.4, sky="gold",
                what="fence"),
    "b07": dict(pos=(-0.6, 7.0, 1.4), target=(-6.6, 6.48, 0.8), lens=18.0, fstop=2.8, sky="gold",
                what="bench"),
    "b08": dict(pos=(-5.52, -0.7, 1.12), target=(-5.52, 3.15, 1.12), lens=50.0, fstop=2.8, sky="gold",
                what="arms"),
    "b09": dict(pos=(-1.3, 5.9, 0.4), target=(-4.5, 9.4, 0.95), pos1=(-1.3, 5.9, 0.4), target1=(-3.8, 9.4, 12.0),
                lens=18.0, fstop=4.0, sky="gold", what="column"),
    "b10": dict(pos=(-1.7, 3.2, 0.45), target=(-3.86, 7.71, 2.47), lens=16.0, fstop=4.0, sky="gold",
                what="cheating"),
    "b11": dict(pos=(6.0, 25.0, 0.8), target=(-0.94, 42.2, 8.3), lens=28.0, fstop=4.0, sky="gold",
                what="climb"),
    # b11's alternative from across the road (east): the anvils on the shelf read above their planks (from b11's
    # spot south-east of the wall, below the shelf, the planks in front of each anvil hide all but a sliver)
    "b11e": dict(pos=(16.5, 31.0, 0.9), target=(0.5, 40.5, 9.0), lens=18.0, fstop=5.6, sky="gold", what="climb_east",
                 stage="b11"),
    "b12": dict(pos=(0.45, 30.6, 5.55), target=(-0.5, 33.2, 5.7), lens=24.0, fstop=2.4, sky="gold", what="legs"),
    "b13": dict(pos=(0.6, 63.0, 20.0), target=(-2.7, 52.6, 16.4), lens=24.0, fstop=4.0, sky="gold",
                what="twelfth"),
    "b14": dict(pos=(-2.45, 59.75, 18.22), target=(-2.5, 51.0, 18.05), lens=24.0, fstop=2.8, sky="gold",
                what="dust"),
    "b15": dict(pos=(5.0, 44.0, 3.9), target=(1.45, 80.8, 4.25), lens=85.0, fstop=2.8, sky="gold",
                what="patrol"),
    "b16": dict(pos=(3.0, 42.8, 0.45), target=(0.9, 33.0, 1.3), lens=32.0, fstop=2.8, sky="gold",
                what="run"),
    "b17": dict(pos=(-4.2, 21.8, 1.1), target=(-10.5, 23.4, 1.35), lens=32.0, fstop=2.8, sky="gold",
                what="cows"),
    "b18": dict(pos=(-3.6, 57.9, 20.3), target=(-1.99, 62.84, 17.3), lens=28.0, fstop=5.6, sky="gold",
                what="lever"),
    "b19": dict(pos=(2.3, 42.5, 0.3), target=(-0.07, 51.99, 2.38), lens=16.0, fstop=5.6, sky="gold",
                what="drop"),
    "b20": dict(pos=(3.6, 45.0, 0.6), target=(1.5, 51.1, 0.3), pos1=(2.35, 49.2, 0.42), target1=(1.5, 51.1, 0.3),
                lens=35.0, fstop=2.8, sky="gold", what="drops"),
    "b21": dict(pos=(4.2, 45.6, 0.3), target=(1.16, 49.94, 3.12), lens=16.0, fstop=4.0, sky="gold",
                what="cheating"),
    "b22": dict(pos=(6.0, 25.0, 0.8), target=(-0.94, 42.2, 8.3), lens=28.0, fstop=4.0, sky="dusk",
                what="climb"),
    "b23": dict(pos=(0.45, 30.6, 5.55), target=(-0.5, 33.2, 5.7), lens=24.0, fstop=2.4, sky="dusk", what="legs"),
    "b24": dict(pos=(1.6, 48.5, 19.9), target=(-1.2, 59.6, 19.0), lens=35.0, fstop=2.8, sky="dusk",
                what="reloading"),
}


# ------------------------------------------------------------------------------------------------------------------
# scouting: one fresh build per still (build 1-3 s; a 540x960 16-sample still 30-90 s on the shared machine)
# ------------------------------------------------------------------------------------------------------------------
TEST_DIR = os.path.join(ROOT, "out", "test")


class Scout:
    """One scene: the set, its parts, a Stage with SKIES (sky = the active one), a Film. For stills only."""

    def __init__(self, sky="gold", res=(540, 960), samples=16, threads=2):
        import bpy
        from engine import look, shots
        from films import lookdev as L
        self.bpy = bpy
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.scene = bpy.context.scene
        look.setup_render(self.scene, res=res, samples=samples, threads=threads)
        self.v = build_set(self.scene)
        self.film = shots.Film(self.scene, fps=24)
        self.st = L.Stage(self.scene, self.film, self.v, skies=SKIES, sky=sky)
        self.P = make_parts(self.v)
        self.sky = sky
        for a in self.P.anvils + self.P.anvils_dusk:         # the two anvil sets: each only where it is used
            self.st.cast[a.name] = a

    def render(self, frame, name, zones=True):
        """Render `frame` to out/test/<name>.png (+ _zones.png). Returns the path."""
        from PIL import Image
        from engine import post
        os.makedirs(TEST_DIR, exist_ok=True)
        path = os.path.join(TEST_DIR, name + ".png")
        self.film.goto(frame)
        self.scene.render.filepath = path[:-4] + "_part"
        self.scene.render.use_file_extension = True
        t = time.time()
        self.bpy.ops.render.render(write_still=True)
        os.replace(path[:-4] + "_part.png", path)
        if zones:
            with Image.open(path) as im:
                post.draw_zones(im.convert("RGB")).save(path[:-4] + "_zones.png")
        print("[legday_set] %s (frame %d, sky %s) %.1f s" % (path, frame, self.sky, time.time() - t), flush=True)
        return path


def view(name, pos, target, lens=24.0, fstop=8.0, sky="gold", res=(540, 960), samples=16):
    """A plain view of the set with every part in its armed state (no cast): out/test/legday_set_view_<name>.png."""
    sc = Scout(sky, res=res, samples=samples)
    s = sc.st.shot("view", 0.5)
    s.lens(lens, fstop)
    s.move(pos, target)
    s.focus(target)
    sc.st.use(s, *sc.P.anvils)
    sc.st.lights(s, scale=1.0 if sky == "gold" else 1.6)
    sc.st.finish()
    return sc.render(s.frame_start + 2, "legday_set_view_" + name, zones=False)


def _vec(text):
    return tuple(float(c) for c in text.split(","))


# ------------------------------------------------------------------------------------------------------------------
# the proof stills: one function per beat stages stand-ins as the beat's picture says (static poses, the parts in
# the state of that moment) on a shot of its own; returns (frame to render, {label: point that must be in frame})
# ------------------------------------------------------------------------------------------------------------------
def _cam(s, beat, focus=None, **over):
    """Put CAMERAS[beat] on shot s (a move when it has pos1: linear, at speed from frame 1). Returns the spec."""
    c = dict(CAMERAS[beat], **over)
    s.lens(c["lens"], c["fstop"])
    if "pos1" in c:
        s.move(c["pos"], c["target"], c["pos1"], c.get("target1", c["target"]), ease="linear")
    else:
        s.move(c["pos"], c["target"])
    s.focus(focus if focus is not None else c["target"])
    return c


def _player(sc, name, skin, anchor=None, frame=None, pos=None, yaw=None, slim=None):
    """A stand-in player (engine.players) put on an anchor (or pos / yaw) on `frame`, in the scout's shot."""
    from engine import players
    kw = {} if slim is None else dict(slim=slim)
    p = players.add_player(sc.st, name, skin, **kw)
    if anchor is not None:
        pos = sc.v.anchors[anchor]
        yaw = sc.v.yaws.get(anchor, 0.0) if yaw is None else yaw
    p.place(frame, pos, yaw or 0.0)
    sc.st.use(sc.shot, p)
    return p


def _head(p, frame):
    return tuple(p.eye_point(frame))


def _efe(sc, anchor=None, frame=None, pos=None, yaw=None, torch=True, watts=None):
    """The narrator (Efe, slim arms) with his redstone torch in the right hand."""
    p = _player(sc, "efe", "efe", anchor, frame, pos, yaw, slim=True)
    if torch:
        redstone.hold_torch(p, "right", watts=watts or redstone.HELD_TORCH_WATTS)
    return p


def _yaw_to(a, b):
    return village.yaw_to(a, b)


def stage_b01(sc, s):
    """Squats at the well: Steve, Zuri, Ari facing the lens with anvils (sneak down), Kai jumping behind, the narrator
    far back by his bench with the glowing torch."""
    f0, st = s.frame_start, sc.st
    pp = [_player(sc, n, n, "squat_" + n, f0) for n in ("steve", "zuri", "ari")]
    for p in pp:
        fixtures.hold_anvil(p)
        p.sneak(f0 + 2, True)
    lap = [(1.3, -5.3, -0.06), (2.9, -3.0, -0.06), (3.6, 0.4, -0.06), (2.4, 3.6, -0.06)]
    kai = _player(sc, "kai", "kai", None, f0, pos=lap[0], yaw=_yaw_to(lap[0], lap[1]))
    kai.sprint_jump(f0, lap, ramp=(False, False))
    efe = _efe(sc, "narrator_far", f0)
    _cam(s, "b01", focus=pp[0].head)
    st.lights(s, scale=1.0, near=(0.0, -3.0, 1.0), radius=14.0)
    f = f0 + 6
    return f, {"steve face": _head(pp[0], f), "zuri face": _head(pp[1], f), "ari face": _head(pp[2], f),
               "steve anvil": tuple(pp[0].item_point("right", f)), "efe (far)": _head(efe, f)}


def stage_b02(sc, s):
    """Steve punching the nearest stone of the row, cracks half way (breaking.mine), seen along the row."""
    f0, st, P = s.frame_start, sc.st, sc.P
    steve = _player(sc, "steve", "steve", "mine_1", f0)
    blk = P.stones[0]
    st.cast[blk.name] = blk
    for b in P.stones:
        st.cast[b.name] = b
        st.use(s, b)
    steve.look_at(f0, blk.center, ease=0)
    r = breaking.mine(steve, blk, f0 - 20, duration=48, camera=s, drop=None)
    sc.memo["mine"] = r
    _cam(s, "b02", focus=steve.head)
    st.lights(s, scale=1.0, near=(5.0, -14.0, 1.0), radius=10.0)
    f = f0 + 8
    return f, {"steve face": _head(steve, f), "stone (cracked)": tuple(blk.center)}


def stage_b03(sc, s):
    """The pull-back: the first stone gone (bare grass), Steve at the second one, the iron pickaxe turning 3 blocks
    behind his back, the row of seven waiting."""
    from engine import mobs
    f0, st, P = s.frame_start, sc.st, sc.P
    steve = _player(sc, "steve", "steve", "mine_2", f0)
    for b in P.stones:
        st.cast[b.name] = b
        st.use(s, b)
    P.stones[0].remove(f0)
    steve.look_at(f0, P.stones[1].center, ease=0)
    breaking.mine(steve, P.stones[1], f0 - 6, duration=48, camera=s, drop=None)
    pick = mobs.make_dropped_item("iron_pickaxe", name="pickaxe")
    st.cast[pick.name] = pick
    st.use(s, pick)
    pick.place(f0, sc.v.anchors["pickaxe_target"])
    pick.animate(f0, s.frame_end + 1)
    _cam(s, "b03", focus=steve.head)
    st.lights(s, scale=1.0, near=(4.0, -13.0, 1.0), radius=10.0)
    f = f0 + 10
    pk = sc.v.anchors["pickaxe_target"]
    return f, {"steve face": _head(steve, f), "pickaxe": (pk[0], pk[1], pk[2] + 0.3),
               "bare grass": (5.5, -15.5, 0.0), "row end": (5.5, -8.5, 1.0)}


def stage_b04(sc, s):
    """The track along the pens: Kai eating a cooked chicken among four hens (start), Zuri drinking milk beside a
    cow (end of the move)."""
    f0, st = s.frame_start, sc.st
    kai = _player(sc, "kai", "kai", "kai_chickens", f0, yaw=_yaw_to(sc.v.anchors["kai_chickens"], (-18.2, 21.5)))
    kai.hold("cooked_chicken")
    kai.eat(f0 + 2, f0 + 30)
    zuri = _player(sc, "zuri", "zuri", "zuri_cow", f0, yaw=_yaw_to(sc.v.anchors["zuri_cow"], (-9.9, 21.3)))
    zuri.hold("milk_bucket")
    zuri.drink(f0 + 2, f0 + 30)
    hens = []
    for i, (x, y) in enumerate(((-21.2, 23.6), (-20.6, 21.5), (-18.6, 23.4), (-19.0, 24.6))):
        h = animals.add_chicken(st, "hen_%d" % i)
        h.place(f0, (x, y, 0.0), _yaw_to((x, y), (-19.6, 22.6)))
        h.look_at(f0, kai.eye_point(f0), ease=0)
        st.use(s, h)
        hens.append(h)
    cows = []
    for i, (x, y, tx, ty) in enumerate(((-10.2, 23.1, -10.0, 19.0), (-8.6, 24.4, -9.5, 20.0))):
        c = animals.add_cow(st, "cow_%d" % i)
        c.place(f0, (x, y, 0.0), _yaw_to((x, y), (tx, ty)))
        st.use(s, c)
        cows.append(c)
    _cam(s, "b04", focus=kai.head)
    st.lights(s, scale=1.0, near=(-15.0, 22.0, 1.0), radius=10.0)
    fa, fb = f0 + 3, s.frame_end - 2
    return [(fa, "a"), (fb, "b")], {"kai face": _head(kai, fa), "hen": tuple(hens[1].eye_point(fa)),
                                    "chicken (food)": tuple(kai.item_point("right", fa)),
                                    "zuri face (end)": _head(zuri, fb), "cow (end)": tuple(cows[0].eye_point(fb))}


def _cow_pen_cast(sc, s, f0, zuri_anchor="zuri_cow", drink=True):
    st = sc.st
    zuri = _player(sc, "zuri", "zuri", zuri_anchor, f0, yaw=_yaw_to(sc.v.anchors[zuri_anchor], (-9.7, 20.6)))
    zuri.hold("milk_bucket")
    if drink:
        zuri.drink(f0 + 2, f0 + 30)
    cow = animals.add_cow(st, "cow_0")
    cp = sc.v.anchors["cow_milk_target"]
    cow.place(f0, cp, _yaw_to(cp, (-11.0, 20.5)))
    st.use(s, cow)
    return zuri, cow


def stage_b05(sc, s):
    """Portrait of Zuri and one cow, both cheated toward the lens: she lowers the bucket (empty), taps the cow."""
    f0, st = s.frame_start, sc.st
    zuri, cow = _cow_pen_cast(sc, s, f0, drink=False)
    zuri.hold("bucket")
    cam = CAMERAS["b05"]["pos"]
    cow.look_at(f0, cam, ease=0)
    zuri.look_at(f0, cow.eye_point(f0), ease=0)
    _cam(s, "b05", focus=zuri.head)
    st.lights(s, scale=1.0, near=(-11.0, 22.0, 1.0), radius=8.0)
    f = f0 + 8
    return f, {"zuri face": _head(zuri, f), "cow face": tuple(cow.eye_point(f)), "bucket":
               tuple(zuri.item_point("right", f))}


def stage_b06(sc, s):
    """Over the narrator's shoulder at the cow pen fence: his thin arm and the torch's glow in the foreground, Zuri
    drinking with the cow beyond."""
    f0, st = s.frame_start, sc.st
    zuri, cow = _cow_pen_cast(sc, s, f0)
    cow.look_at(f0, CAMERAS["b06"]["pos"], ease=0)
    efe = _efe(sc, "narrator_fence", f0)
    efe.look_at(f0, zuri.eye_point(f0), ease=0)
    _cam(s, "b06", focus=zuri.head)
    st.lights(s, scale=1.0, near=(-11.0, 21.0, 1.0), radius=8.0)
    f = f0 + 12
    return f, {"zuri face": _head(zuri, f), "efe torch": tuple(efe.item_point("right", f)),
               "cow face": tuple(cow.eye_point(f))}


def stage_b07(sc, s):
    """The bench: the narrator has planted his torch; the dust, the repeater, the lamp lit, the piston out."""
    f0, st, B = s.frame_start, sc.st, sc.P.bench
    efe = _efe(sc, "bench_narrator", f0, torch=False)
    efe.look_at(f0, (-5.5, 8.4, 0.2), ease=0)
    t = B["torch"].plant(f0 + 2, player=efe)
    redstone.signal(t, B["wire"], B["repeater"], (B["lamp"], B["piston"]))
    efe.look_at(f0 + 10, B["lamp"].center, ease=4)
    _cam(s, "b07", focus=efe.head)
    st.lights(s, scale=1.0, near=(-6.0, 5.0, 1.0), radius=8.0)
    f = f0 + 16
    return f, {"efe face": _head(efe, f), "lamp": tuple(B["lamp"].center), "torch": (-5.5, 8.5, 0.4),
               "repeater": (-5.5, 5.5, 0.1)}


def _bench_lit(sc, f):
    B = sc.P.bench
    B["torch"].plant(f)
    redstone.signal(float(f), B["wire"], B["repeater"], (B["lamp"], B["piston"]))


def stage_b08(sc, s):
    """Frontal two-shot against the lit lamp: the narrator's slim near arm beside Steve's wide one."""
    f0, st = s.frame_start, sc.st
    _bench_lit(sc, f0 - 20)
    efe = _efe(sc, "arms_narrator", f0, torch=False)
    redstone.hold_torch(efe, "right")
    steve = _player(sc, "steve", "steve", "arms_steve", f0)
    efe.look_at(f0, (-5.38, 2.9, 1.0), ease=0)
    steve.look_at(f0, (-5.65, 2.9, 0.95), ease=0)
    _cam(s, "b08", focus=(-5.52, 3.15, 1.1))
    st.lights(s, scale=1.0, near=(-3.5, 4.0, 1.0), radius=8.0)
    f = f0 + 8
    return f, {"efe arm (slim)": (-5.64, 3.15, 1.1), "steve arm": (-5.40, 3.15, 1.1),
               "efe face": _head(efe, f), "steve face": _head(steve, f)}


def stage_b09(sc, s):
    """The column: Steve at its foot looking down at the piston; the narrator flips the lever north of it; the twelve
    iron blocks rise one block (the still is the moment after)."""
    f0, st, C = s.frame_start, sc.st, sc.P.column
    steve = _player(sc, "steve", "steve", "column_steve", f0)
    efe = _efe(sc, "column_narrator", f0)
    steve.look_at(f0, (-3.5, 9.5, 0.6), ease=0)
    t = redstone.flip_by(efe, C["lever"], f0 + 4, look=False)
    C["piston"].power(t)
    steve.look_at(f0 + 8, (-3.5, 9.5, 9.0), ease=10)
    _cam(s, "b09", focus=steve.head)
    st.lights(s, scale=1.0, near=(-4.0, 9.0, 1.0), radius=10.0)
    f = f0 + 14
    return [(f0 + 2, "a"), (s.frame_end - 2, "b")], {"steve face": _head(steve, f), "column top": (-3.5, 9.5, 14.0), "piston": (-3.5, 9.5, 0.5),
               "lever": (-3.5, 10.5, 1.3)}


def stage_b10(sc, s):
    """'That's cheating': the column up against the sky; Steve walks away toward the well, his head in profile
    toward the lens; the narrator small at the lever."""
    f0, st, C = s.frame_start, sc.st, sc.P.column
    C["lever"].set(f0 - 30, True)
    C["piston"].power(f0 - 30)
    a, e = (-4.6, 8.0, 0.0), sc.v.anchors["column_walk_end"]
    steve = _player(sc, "steve", "steve", None, f0, pos=a, yaw=_yaw_to(a, e))
    steve.walk(f0, [a, e], ramp=(False, True))
    steve.look_at(f0, CAMERAS["b10"]["pos"], ease=0)
    efe = _efe(sc, "column_narrator", f0)
    efe.look_at(f0, steve.eye_point(f0 + 10), ease=0)
    _cam(s, "b10", focus=steve.head)
    st.lights(s, scale=1.0, near=(-4.0, 6.0, 1.0), radius=10.0)
    f = f0 + 12
    return f, {"steve face": _head(steve, f), "efe face": _head(efe, f), "column top": (-3.5, 9.5, 15.0)}


def _climbers(sc, s, f0, anvils=True, steps=(3, 5, 7, 9), names=("steve", "kai", "zuri", "ari")):
    out = []
    for n, k in zip(names, steps):
        y = STAIR_Y0 + k + 0.75
        p = _player(sc, n, n, None, f0, pos=(STAIR_X + 0.5, y, stair_z(y)), yaw=_yaw("north"))
        if anvils:
            fixtures.hold_anvil(p)
        out.append(p)
    return out


def _use_anvils(sc, s, which="anvils", only=None):
    """Show the anvils of the set `which` on shot s: all, or the indices in `only` (0 = the south one)."""
    for i, a in enumerate(sc.P[which]):
        if only is None or i in only:
            sc.st.use(s, a)


def stage_b11(sc, s, dusk=False, cam=None):
    """Low angle from the road: the wall, the long stair, four climbers with anvils, eight anvils on the shelf."""
    f0, st = s.frame_start, sc.st
    cl = _climbers(sc, s, f0)
    for p in cl:
        y = p.pos_at(f0)[1]
        p.walk(f0, [(-0.5, y, stair_z(y)), (-0.5, y + 1.0, stair_z(y + 1.0))], speed=1.2)
    _use_anvils(sc, s, "anvils_dusk" if dusk else "anvils", only=range(4, 12))
    heroes = {}
    if dusk:
        efe = _efe(sc, "lever_narrator", f0, watts=redstone.HELD_TORCH_KEY_WATTS)
        heroes["efe (lever)"] = _head(efe, f0 + 8)
    _cam(s, cam or ("b22" if dusk else "b11"))
    st.lights(s, scale=DUSK_LIGHTS if dusk else 1.0, near=(-1.0, 40.0, 8.0), radius=26.0)
    f = f0 + 8
    heroes.update({"climber %d" % (i + 1): _head(p, f) for i, p in enumerate(cl)})
    heroes["shelf far end"] = (0.5, 57.5, 18.5)
    heroes["shelf near end"] = (0.5, 46.5, 18.5)
    return f, heroes


def stage_b12(sc, s, dusk=False):
    """Close on the stair, ground level: Steve's legs pump up past the lens, Kai right behind (anvils in hand)."""
    f0, st = s.frame_start, sc.st
    cl = _climbers(sc, s, f0, steps=(4.1, 2.5), names=("steve", "kai"))
    for p in cl:
        y = p.pos_at(f0)[1]
        pts = [(-0.5, y, stair_z(y))]
        for k in range(1, 5):
            pts.append((-0.5, y + 0.5 * k, stair_z(y + 0.5 * k)))
        p.walk(f0, pts, speed=1.3)
    _cam(s, "b23" if dusk else "b12", focus=(-0.5, 31.6, 5.3))
    st.lights(s, scale=DUSK_LIGHTS if dusk else 1.0, near=(-1.0, 33.0, 6.0), radius=16.0)
    f = f0 + 6
    return f, {"steve legs": tuple(cl[0].pos_at(f)), "kai legs": tuple(cl[1].pos_at(f)),
               "steve anvil": tuple(cl[0].item_point("right", f))}


def stage_b13(sc, s):
    """From just outside the wall top's south end, back along the row: eleven pistons out with planks and anvils;
    the narrator sets the twelfth (the south gap), its arm out at once."""
    f0, st, P = s.frame_start, sc.st, sc.P
    efe = _efe(sc, "place_12th", f0, torch=False)
    p12 = P.row.pistons[11]
    p12.retract(2.0, pull=None)                     # built extended with the row: in before it is placed ...
    p12.place(f0 + 6, player=efe)                   # ... placed on a powered spot it fires at once (PistonBaseBlock)
    p12.extend(f0 + 6)
    P.row.blocks[11].show(1, False)                 # its plank: he sets it after (not in this still)
    _use_anvils(sc, s, only=range(0, 11))
    efe.look_at(f0, (-1.5, 57.5, 17.5), ease=0)
    _cam(s, "b13", focus=efe.head)
    st.lights(s, scale=1.0, near=(-1.0, 52.0, 18.0), radius=12.0)
    f = f0 + 7
    return f, {"efe face": _head(efe, f), "12th piston": (-1.0, 57.5, 17.5), "row far": (0.5, 46.5, 18.5)}


def stage_b14(sc, s):
    """Ground level on the wall top by the lever, the lit dust leading away: Steve's feet step over it, anvil in
    hand; the narrator soft beyond."""
    f0, st = s.frame_start, sc.st
    a, e = (-2.55, 53.6, WALK_Z), (-2.3, 56.9, WALK_Z)
    steve = _player(sc, "steve", "steve", None, f0, pos=a, yaw=_yaw("north"))
    fixtures.hold_anvil(steve)
    steve.walk(f0, [a, e], ramp=(False, True))
    efe = _efe(sc, None, f0, pos=(-3.45, 47.2, WALK_Z), yaw=_yaw("north"))
    _use_anvils(sc, s, only=range(0, 11))
    _cam(s, "b14", focus=(-2.45, 55.6, 18.4))
    st.lights(s, scale=1.0, near=(-2.5, 52.0, 18.0), radius=12.0)
    f = f0 + 8
    return f, {"steve feet": tuple(steve.pos_at(f)), "dust near": (-2.5, 57.5, 18.05), "efe face": _head(efe, f),
               "lever": (-2.5, 59.5, 19.4)}


def _patrol(sc, s, frame, path=None, gait="vanilla"):
    from engine import illagers
    pat = illagers.add_patrol(sc.st, 5)
    illagers.march(pat, path or sc.v.paths["patrol_road"], frame, gait=gait)
    for p in pat:
        sc.st.use(s, p)
    return pat


def stage_b15(sc, s):
    """Long lens up the road to the meadow: the patrol walks toward the lens, the captain in front with the banner."""
    f0, st = s.frame_start, sc.st
    road = [p for p in sc.v.paths["patrol_road"] if p[1] <= 76.0]
    road = [(0.5, 76.0, 2.0)] + road
    pat = _patrol(sc, s, f0, road)
    _cam(s, "b15", focus=pat[0].head)
    st.lights(s, scale=1.0, near=(0.5, 60.0, 1.0), radius=12.0)
    f = f0 + 8
    return f, {"captain": _head(pat[0], f), "banner top": tuple(pat[0].banner_top(f)) if hasattr(pat[0], "banner_top")
               else _head(pat[0], f), "last": _head(pat[-1], f)}


def stage_b16(sc, s):
    """Low track from the verge: Steve sprints up the road at the lens, fist up, Kai and Zuri staggered behind; three
    arrows stuck in the road in front of them."""
    from engine import hostiles
    f0, st = s.frame_start, sc.st
    runs = [("steve", (1.0, 34.6), (1.0, 39.0)), ("kai", (0.4, 33.0), (0.4, 37.4)),
            ("zuri", (1.75, 32.3), (1.75, 36.7))]
    pp = []
    for n, a, b in runs:
        p = _player(sc, n, n, None, f0, pos=(a[0], a[1], -0.06), yaw=_yaw("north"))
        p.walk(f0, [(a[0], a[1], -0.06), (b[0], b[1], -0.06)], sprint=True, ramp=(False, True))
        pp.append(p)
    pp[0].attack(f0 + 4)
    arrows = []
    for i, (x, y) in enumerate(((0.35, 37.8), (0.95, 38.3), (-0.05, 38.6))):
        ob = hostiles.stick((x, y, 0.0), (0.05, -0.55, -0.83), f0 + 4 + i)
        arrows.append(ob)
    _cam(s, "b16", focus=pp[0].head)
    st.lights(s, scale=1.0, near=(0.5, 36.0, 1.0), radius=12.0)
    f = f0 + 8
    return f, {"steve face": _head(pp[0], f), "kai face": _head(pp[1], f), "zuri face": _head(pp[2], f),
               "arrows": (0.4, 38.2, 0.2)}


def stage_b17(sc, s):
    """Through the cow pen fence: four players crouched behind three cows, heads toward the road (east), arrows in
    the corner post, the nearest cow looking at the lens."""
    from engine import hostiles
    f0, st = s.frame_start, sc.st
    cam = CAMERAS["b17"]["pos"]
    pp = []
    for i, n in enumerate(("steve", "kai", "zuri", "ari")):
        p = _player(sc, n, n, "hide_%d" % (i + 1), f0)
        p.look_at(f0, (0.5, sc.v.anchors["hide_%d" % (i + 1)][1] + 3.0, 1.5), ease=0)
        pp.append(p)
    cows = []
    for i in range(3):
        cp = sc.v.anchors["hide_cow_%d_target" % (i + 1)]
        c = animals.add_cow(st, "cow_%d" % i)
        c.place(f0, cp, _yaw("north"))
        st.use(s, c)
        cows.append(c)
    cows[0].look_at(f0, cam, ease=0)
    post = sc.v.anchors["arrow_post_target"]
    hostiles.stick((post[0], post[1] - 0.05, 0.92), (-0.97, 0.06, -0.22), f0 - 30)
    hostiles.stick((post[0], post[1] + 0.1, 0.72), (-0.97, -0.08, -0.2), f0 + 6)
    _cam(s, "b17", focus=pp[0].head)
    st.lights(s, scale=1.0, near=(-10.0, 22.0, 1.0), radius=10.0)
    f = f0 + 8
    return f, dict({"%s face" % n: _head(p, f) for n, p in zip(("steve", "kai", "zuri", "ari"), pp)},
                   **{"post arrows": (-6.3, 22.45, 0.85), "near cow": tuple(cows[0].eye_point(f))})


def stage_b18(sc, s):
    """Close on the lever on the wall top: the narrator flips it, the whole dust line dark in one frame; far below on
    the open road, short of the shelf, the captain's banner (soft)."""
    f0, st, P = s.frame_start, sc.st, sc.P
    efe = _efe(sc, "lever_narrator", f0, torch=False)
    t = redstone.flip_by(efe, P.lever, f0 + 4, look=True)
    P.wire.unpower(t)
    road = [(0.5, 81.0, 3.0), (0.5, 78.7, 3.0), (0.5, 78.1, 2.0), (0.5, 74.0, 2.0)]
    pat = _patrol(sc, s, f0, road)
    _use_anvils(sc, s)
    _cam(s, "b18", focus=P.lever.hand_point(f0))
    st.lights(s, scale=1.0, near=(-3.0, 46.0, 18.0), radius=10.0)
    f = f0 + 9
    return f, {"lever": tuple(P.lever.hand_point(f)), "efe hand": tuple(efe.item_point("right", f)),
               "captain banner": _head(pat[0], f), "dust": (-2.5, 48.5, 18.05)}


def stage_b19(sc, s, phase="fall"):
    """The money shot: the patrol in a clean file on the strip under the shelf, the pistons snap back, the anvils
    drop (phase 'fall': mid-fall; 'hit': the landing frame)."""
    from engine import illagers
    f0, st, P = s.frame_start, sc.st, sc.P
    t_flip = f0 + 6
    land_y = 47.0                                                 # the captain's feet on the landing frame
    drop_frames = fixtures.fall_track(18.0)
    path = [(0.5, 66.0, 1.0), (0.5, 58.6, 1.0), (0.5, 57.7, 1.0), (0.5, 57.1, 0.0), (0.5, 40.0, 0.0)]
    pat = illagers.add_patrol(st, 5)
    for p in pat:
        st.use(s, p)
    # start the march so the captain is at land_y on the landing frame (release on t_flip, landing ~41 frames later)
    sc.memo["patrol"] = pat
    probe = fixtures.release(P.anvils, t_flip, world=sc.v)
    land = probe[0]["frame_land"]
    walked = (land - f0) / 24.0 * illagers.PATROL_SPEED
    start_y = land_y + walked
    path = [(0.5, start_y + 9.0, 0.0 if start_y + 9.0 < 57.1 else 1.0)] if False else None
    road = [(0.5, start_y, 0.0), (0.5, 40.0, 0.0)]
    illagers.march(pat, road, f0, gait="vanilla")
    P.row.retract(t_flip)
    P.wire.unpower(t_flip)
    P.lever.set(t_flip, False)
    _use_anvils(sc, s)
    hits = fixtures.strikes(probe, {p.name: tuple(p.pos_at(land)) for p in pat})
    res = illagers.crush_patrol(pat, probe, camera=s, stage=st, knockback=False, village=sc.v,
                                spots=[sc.v.anchors["bottle_spot_target"], sc.v.anchors["banner_spot_target"]],
                                face=CAMERAS["b19"]["pos"])
    sc.memo["crush"] = (probe, hits, res, land, start_y)
    _cam(s, "b19")
    st.lights(s, scale=1.0, near=(0.0, 50.0, 4.0), radius=14.0)
    f = (t_flip + 22) if phase == "fall" else land
    return f, {"captain": _head(pat[0], f), "last": _head(pat[-1], f), "anvil 1": (0.5, 46.5, 10.0),
               "anvil 12": (0.5, 57.5, 10.0)}


def stage_b20(sc, s):
    """The road after: twelve anvils standing on the cobblestones (most chipped), the banner and the bottle turning
    side by side between them."""
    from engine import illagers
    f0, st, P = s.frame_start, sc.st, sc.P
    P.row.retract(f0 - 80)
    P.wire.unpower(f0 - 80)
    P.lever.set(f0 - 80, False)
    drops = fixtures.release(P.anvils, f0 - 80, world=sc.v, chip=8, seed=3)
    _use_anvils(sc, s)
    ban = illagers.add_dropped_banner(st, shot=s)
    bot = illagers.add_dropped_bottle(st, shot=s)
    cam = CAMERAS["b20"]["pos"]
    for it, a in ((ban, "banner_spot_target"), (bot, "bottle_spot_target")):
        it.place(f0, sc.v.anchors[a])
        if hasattr(it, "face"):
            it.face(f0, cam)
        it.animate(f0, s.frame_end + 1)
    _cam(s, "b20")
    st.lights(s, scale=1.0, near=(1.0, 51.0, 1.0), radius=10.0)
    f = f0 + 6
    return [(f0 + 6, "a"), (s.frame_end - 2, "b")], {"banner": tuple(sc.v.anchors["banner_spot_target"]), "bottle": tuple(sc.v.anchors["bottle_spot_target"])}


def stage_b21(sc, s):
    """Tall frame from the road: Steve among the anvils in front, the narrator high on the wall top by the lever."""
    from engine import illagers
    f0, st, P = s.frame_start, sc.st, sc.P
    P.row.retract(f0 - 120)
    P.wire.unpower(f0 - 120)
    P.lever.set(f0 - 120, False)
    fixtures.release(P.anvils, f0 - 120, world=sc.v, chip=8, seed=3)
    _use_anvils(sc, s)
    ban = illagers.add_dropped_banner(st, shot=s)
    bot = illagers.add_dropped_bottle(st, shot=s)
    for it, a in ((ban, "banner_spot_target"), (bot, "bottle_spot_target")):
        it.place(f0, sc.v.anchors[a])
        it.animate(f0, s.frame_end + 1)
    steve = _player(sc, "steve", "steve", "steve_among_anvils", f0)
    efe = _efe(sc, "narrator_edge", f0)
    steve.look_at(f0, efe.eye_point(f0), ease=0)
    efe.look_at(f0, steve.eye_point(f0), ease=0)
    _cam(s, "b21", focus=steve.head)
    sc.memo["occluders"] = [b.object for b in P.row.blocks]
    st.lights(s, scale=1.0, near=(0.0, 47.0, 6.0), radius=16.0)
    f = f0 + 6
    return f, {"steve face": _head(steve, f), "efe (wall top)": _head(efe, f), "banner": sc.v.anchors["banner_spot_target"]}


def stage_b22(sc, s):
    """b11 at dusk: the same frame, lanterns on, the narrator waiting by the lever, eight anvils back on the shelf."""
    return stage_b11(sc, s, dusk=True)


def stage_b23(sc, s):
    """b12 at dusk: the same set-up in lantern light."""
    return stage_b12(sc, s, dusk=True)


def stage_b24(sc, s):
    """Wall top at last light, along the armed row: Steve sets the twelfth anvil (south end); the narrator by the
    lever, the redstone torch his key, his free arm lifted to the lever."""
    f0, st, P = s.frame_start, sc.st, sc.P
    efe = _efe(sc, "lever_narrator", f0, watts=B24_TORCH_WATTS)
    efe.look_at(f0, (0.5, 50.0, 17.0), ease=0)
    efe.raise_arm(f0 + 2, angle=60.0, side="l")
    steve = _player(sc, "steve", "steve", "set_anvil_12th", f0)
    fixtures.hold_anvil(steve)
    steve.look_at(f0, (0.5, 57.5, 18.2), ease=0)
    _use_anvils(sc, s, "anvils_dusk", only=range(0, 11))
    _cam(s, "b24", focus=efe.head)
    st.lights(s, scale=DUSK_LIGHTS, near=(-2.0, 52.0, 18.0), radius=14.0)
    f = f0 + 8
    return f, {"efe face": _head(efe, f), "steve face": _head(steve, f), "anvil row": (0.5, 52.5, 18.5),
               "last plank": (0.5, 57.5, 17.9)}


STAGES = {b: globals()["stage_" + CAMERAS[b].get("stage", b)] for b in CAMERAS}


def ray_block(world, a, b, step=0.05, skip_end=0.35):
    """The first World block a straight line from a to b passes through (cell, block id), or None. Plants, torches
    and other non-solid blocks are ignored; the last `skip_end` blocks before b are not tested (b's own body)."""
    ax, ay, az = (float(c) for c in a)
    bx, by, bz = (float(c) for c in b)
    d = math.dist((ax, ay, az), (bx, by, bz))
    n = max(1, int(d / step))
    seen = set()
    for i in range(1, n):
        t = i / float(n)
        if (1.0 - t) * d < skip_end:
            break
        c = (int(math.floor(ax + (bx - ax) * t)), int(math.floor(ay + (by - ay) * t)), int(math.floor(az + (bz - az) * t)))
        if c in seen:
            continue
        seen.add(c)
        if world.is_solid(*c):
            bid = world.block_id(*c)
            if bid.endswith(("_fence", "_fence_gate", "lantern", "_wall")):
                continue                                    # (thin: posts, rails, lanterns do not hide a face)
            if (bid.endswith("_stairs") or bid.endswith("_slab")) and az + (bz - az) * t > c[2] + 0.5:
                continue                                    # (the upper half of a stair or slab: not tested)
            return c, bid
    return None


def project(scene, cam, point):
    """(x %, y % from the top) of a world point in the camera's frame, and whether it is in front of the lens."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    co = world_to_camera_view(scene, cam, Vector(point))
    return 100.0 * co.x, 100.0 * (1.0 - co.y), co.z > 0.0


def still(beat, sky=None, res=(540, 960), samples=16, name=None, dry=False, palette=True, **kw):
    """Build the set, stage beat `beat` (b01 .. b24) under its sky and render its proof still
    out/test/legday_set_<beat>_<what>.png (+ _zones.png). Prints where each hero point lands in the frame."""
    spec = CAMERAS[beat]
    sc = Scout(sky or spec["sky"], res=res, samples=samples)
    sc.memo = {}
    s = sc.st.shot(beat, spec.get("seconds", 3.0), sky=sky or spec["sky"])
    sc.shot = s
    if "stage" in spec:
        kw.setdefault("cam", beat)
    f, heroes = STAGES[beat](sc, s, **kw)
    sc.st.finish()
    frames = f if isinstance(f, list) else [(f, "")]
    out = name or "legday_set_%s_%s" % (beat, spec["what"])
    path = None
    for fr, tag in frames:
        sc.film.goto(fr)
        cam = sc.scene.camera
        cp = tuple(cam.matrix_world.translation)
        cell = tuple(int(math.floor(c)) for c in cp)
        if sc.v.world.is_solid(*cell):
            print("[legday_set]   !!! the camera of %s is inside %s at %s" % (beat, sc.v.world.block_id(*cell), cell))
        path = None if dry else sc.render(fr, out + ("_" + tag if tag else ""))
        if path and palette:                      # tools/palette_check: the picture against the game's texels
            from tools import palette_check
            rep = palette_check.evaluate(palette_check.probe(sc.scene), path)
            palette_check.print_report("%s@%d" % (beat, fr), rep)
        if dry:
            print("[legday_set] %s staged (frame %d, sky %s): not rendered (--dry)" % (beat, fr, sc.sky))
        for label, p in heroes.items():
            x, y, front = project(sc.scene, cam, p)
            blocked = ray_block(sc.v.world, cam.matrix_world.translation, p)
            flag = "" if (8 <= x <= 82 and 14 <= y <= 60 and front) else "   (outside the safe area)"
            if blocked:
                flag += "   (hidden by %s at %s)" % (blocked[1], blocked[0])
            print("[legday_set]   %-18s x %5.1f %%  y %5.1f %%%s" % (label, x, y, flag))
    if "crush" in sc.memo:
        probe, hits, res_, land, start_y = sc.memo["crush"]
        print("[legday_set]   anvils land on frame %d (fall %.1f, damage %s); patrol start y %.2f; struck: %s"
              % (land, probe[0]["height"], probe[0]["damage"], start_y, sorted(hits)))
        print("[legday_set]   crushed: %s" % {k: (round(v["damage"], 1), v["lethal"]) for k, v in res_.items()})
    return path



# ------------------------------------------------------------------------------------------------------------------
# the self-test (numbers, no render): $BPY -m films.legday_set
# ------------------------------------------------------------------------------------------------------------------
def _solid_at(w, x, y, z):
    """Is the point (x, y, z) inside a solid block (stairs and bottom slabs: their lower half only)?"""
    c = (int(math.floor(x)), int(math.floor(y)), int(math.floor(z)))
    if not w.is_solid(*c):
        return False
    bid, props = w.get(*c)
    if bid.endswith(("_fence", "_fence_gate", "lantern", "_wall")) and not bid.endswith("bricks"):
        return True
    if bid.endswith("_slab") and (props or {}).get("type", "bottom") == "bottom":
        return z - c[2] < 0.5 - 1e-6
    if bid.endswith("_stairs"):                         # a bottom stair: the lower half, and the upper half at its back
        if z - c[2] < 0.5 - 1e-6:
            return True
        fx, fy = x - c[0], y - c[1]
        back = {"north": fy >= 0.5, "south": fy < 0.5, "east": fx >= 0.5, "west": fx < 0.5}
        return back.get((props or {}).get("facing", "north"), True)
    return True


def part_cells():
    """{cell: what}: every cell a moving part fills at some time (pistons, heads, planks in both states, anvils on
    the shelf and on the road, the column and its rise, the bench's parts and the levers): no camera may sit there."""
    out = {}
    for y in ROW_Y:
        out[(PISTON_X, y, TOP_Z)] = "piston"
        out[(HEAD_X, y, TOP_Z)] = "piston head / retracted plank"
        out[(PLANK_X, y, TOP_Z)] = "plank"
        out[(PLANK_X, y, ANVIL_Z)] = "anvil (shelf)"
        out[(PLANK_X, y, 0)] = "anvil (landed)"
    out[LEVER] = "wall lever"
    cx, cy, cz = COLUMN["piston"]
    for z in range(cz, cz + COLUMN["blocks"] + 2):
        out[(cx, cy, z)] = "column"
    out[COLUMN["lever"]] = "column lever"
    for key in ("torch", "repeater", "lamp", "piston"):
        out[BENCH[key]] = "bench " + key
    for c in BENCH["dust"]:
        out[c] = "bench dust"
    bx, by, bz = BENCH["piston"]
    out[(bx + 1, by, bz)] = "bench piston head"
    for c in STONE_ROW:
        out[c] = "stone row"
    return out


def march_window():
    """Where the captain may be (his y on the road under the shelf, x 0.5) on the anvils' landing frame so that all
    five pillagers (2.0 apart, the captain in front walking south) stand under an anvil: (lowest, highest)."""
    from engine import illagers
    reach = fixtures.FALLING_ENTITY_WIDTH / 2.0 + 0.3
    lo = ROW_Y[0] + 0.5 - reach
    hi = ROW_Y[-1] + 0.5 + reach - 4 * illagers.FILE_SPACING
    return lo, hi


def check(verbose=True):
    """The set's numbers: build it, then test anchors (on solid ground, nothing solid at the feet or the head),
    cameras (not inside a block), the anvils (landing cell, fall, damage to the captain with the banner), the march
    window, the dust's power levels, the paths (Village.validate). Returns the list of failures."""
    import bpy
    from engine import illagers, quick
    bad = []
    t = time.time()
    scene = quick.reset()
    v = build_set(scene)
    P = make_parts(v)
    w = v.world
    faces = sum(len(o.data.polygons) for o in scene.objects if o.type == "MESH")
    say = print if verbose else (lambda *a: None)
    say("[legday_set] built in %.1f s: %d faces, %d terrain columns added north" % (
        time.time() - t, faces, v.sets["legday"]["meadow_north"]))
    # 1. the village's own checks (paths not blocked, anchors not in blocks)
    for p in v.validate():
        bad.append("village: " + p)
    # 2. every anchor of this set: solid under the feet, the body free
    names = list(ANCHORS) + ["%s_pen_center" % n for n in ("chicken", "cow")] + ["chicken_pen_gate", "cow_pen_gate"]
    n_ok = 0
    for name in names:
        if name.endswith(("_target", "_cam", "_center")):
            continue
        x, y, z = v.anchors[name]
        under = _solid_at(w, x, y, z - 0.05)
        body = [zz for zz in (z + 0.3, z + 1.0, z + 1.7) if _solid_at(w, x, y, zz)]
        if not under or body:
            bad.append("anchor %s at %s: %s" % (name, tuple(round(c, 2) for c in (x, y, z)),
                                               "nothing solid under it" if not under else "inside a block"))
        else:
            n_ok += 1
    say("[legday_set] anchors standing on solid ground with the body free: %d" % n_ok)
    # 3. cameras: never inside a block of the World nor inside a part (pos and pos1)
    parts = part_cells()
    for beat, c in CAMERAS.items():
        for key in ("pos", "pos1"):
            if key not in c:
                continue
            cell = tuple(int(math.floor(a)) for a in c[key])
            if _solid_at(w, *c[key]):
                bad.append("camera %s %s %s is inside %s" % (beat, key, c[key], w.block_id(*cell)))
            elif cell in parts:
                bad.append("camera %s %s %s is inside the part %s" % (beat, key, c[key], parts[cell]))
    say("[legday_set] cameras checked: %d (pos and pos1)" % len(CAMERAS))
    # 4. the anvils: each falls from (0, y, 18) to (0, y, 0) on cobblestone; 18 blocks; lethal to the captain
    for i, y in enumerate(ROW_Y):
        cell, on = fixtures.landing_cell(w, (PLANK_X, y, ANVIL_Z))
        if cell != (PLANK_X, y, 0) or on != "cobblestone":
            bad.append("anvil %d lands in %s on %s" % (i + 1, cell, on))
    h = float(ANVIL_Z)
    dmg, dmg_cap = fixtures.anvil_damage(h), fixtures.anvil_damage(h, helmet=True)
    if dmg_cap < fixtures.PILLAGER_HEALTH:
        bad.append("an anvil from %g blocks does %g to the captain (needs %d)" % (h, dmg_cap, fixtures.PILLAGER_HEALTH))
    ticks = fixtures.fall_ticks(h)
    say("[legday_set] anvils: 12 land on cobblestone at z 0 after a fall of %g blocks (%d ticks = %.1f frames after the "
        "2-tick hang); damage %g, %g to the captain with the banner (health %d)" % (
            h, ticks, ticks * fixtures.TICK, dmg, dmg_cap, fixtures.PILLAGER_HEALTH))
    lo, hi = march_window()
    say("[legday_set] march window: the captain's y on the landing frame between %.2f and %.2f (file of five, %.1f "
        "apart, walking south on x 0.5)" % (lo, hi, illagers.FILE_SPACING))
    drops = fixtures.release(P.anvils, 10, world=v)
    land = drops[0]["frame_land"]
    for yc in (lo + 0.05, (lo + hi) / 2.0, hi - 0.05):
        spots = {"p%d" % k: (0.5, yc + k * illagers.FILE_SPACING, 0.0) for k in range(5)}
        hits = fixtures.strikes(drops, spots)
        if len(hits) != 5:
            bad.append("captain at y %.2f: only %d of 5 struck" % (yc, len(hits)))
    say("[legday_set] released on frame 10: the anvils land on frame %d; strikes() hits all five at the window's ends "
        "and middle" % land)
    # 5. the dust: power at the lever's end and at the far end
    lev = [P.wire.level_at((DUST_X, y, TOP_Z + 1), 5) for y in DUST_Y]
    if min(lev) < 1:
        bad.append("dust level %d somewhere along the line" % min(lev))
    say("[legday_set] the wall's dust: power %d (y %d, by the lever) .. %d (y %d, far end)" % (
        lev[-1], DUST_Y[-1], lev[0], DUST_Y[0]))
    # 6. the column: 12 iron blocks over an upward piston (the push limit), one free cell above
    cx, cy, cz = COLUMN["piston"]
    if w.get(cx, cy, cz + COLUMN["blocks"] + 1) is not None:
        bad.append("the column has no room to rise")
    say("[legday_set] column: piston %s, %d iron blocks, lever %s on its pier" % (
        COLUMN["piston"], COLUMN["blocks"], COLUMN["lever"]))
    for b_ in bad:
        print("[legday_set] FAIL " + b_)
    print("[legday_set] check %s (%d failures)" % ("ok" if not bad else "FAILED", len(bad)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bad


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "check":
        sys.exit(1 if check() else 0)
    if args and args[0] not in ("still", "view") and all(a in CAMERAS or a.startswith("--") for a in args):
        args = ["still"] + args
    if args and args[0] == "still":
        # still b01 [b02 ...] [--res WxH] [--samples N]: the proof stills of these beats (2-3 per call)
        res, samples, beats, dry = (540, 960), 16, [], False
        it = iter(args[1:])
        for a in it:
            if a == "--dry":
                dry = True
            elif a == "--res":
                res = tuple(int(c) for c in next(it).split("x"))
            elif a == "--samples":
                samples = int(next(it))
            else:
                beats.append(a)
        for b in beats:
            still(b, res=res, samples=samples, dry=dry)
    if args and args[0] == "view":
        # view NAME x,y,z tx,ty,tz LENS [FSTOP] [SKY] [WxH] [SAMPLES]
        a = args[1:]
        res = tuple(int(c) for c in a[6].split("x")) if len(a) > 6 else (540, 960)
        view(a[0], _vec(a[1]), _vec(a[2]), float(a[3]), float(a[4]) if len(a) > 4 else 8.0,
             a[5] if len(a) > 5 else "gold", res, int(a[7]) if len(a) > 7 else 16)

