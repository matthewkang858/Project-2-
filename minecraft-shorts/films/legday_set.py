"""(docstring written at the end: see the bottom of this draft)"""
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
WALL_Y = (27, 58)                 # its south and north end cells (32 blocks long)
TOP_Z = 17                        # the top course (pistons, the blocks under the dust); the walkway is z 18
WALK_Z = TOP_Z + 1.0              # the wall top a character stands on
STAIR_X, STAIR_Y0, STEPS = -1, 27, 18     # step k = (x -1, y 27 + k, z k), facing north, solid under it
ROW_Y = tuple(range(46, 58))      # the twelve sticky pistons: (-2, y, 17), facing east, y 46 (south) .. 57 (north)
PISTON_X, HEAD_X, PLANK_X = -2, -1, 0     # piston, its head, the plank on its arm (extended); retracted: plank x -1
DUST_X = -3                       # the line of dust on the wall top (on the blocks behind the pistons), z 18
DUST_Y = tuple(range(45, 58))     # 13 cells: the first one beside the lever's pier, then one behind every piston
PIER = (-4, 45, 18)               # the block on the wall top the lever stands on (handle 1.3 above the walkway)
LEVER = (-4, 45, 19)              # the floor lever (facing east): it powers the pier, the pier the first dust
STRIP_X, STRIP_Y = (-1, 1), (45, 57)      # cobblestone paving at the wall's foot under the shelf (top z 0)
ANVIL_Z = TOP_Z + 1               # the anvils stand on the planks: cells (0, y, 18); they land in (0, y, 0)
WALL_LANTERNS = [(-2, 31, 18), (-2, 35, 18), (-2, 39, 18), (-2, 43, 18),          # front edge over the stair
                 (-4, 44, 18),                                                    # beside the lever: the face key
                 (-4, 49, 18), (-4, 53, 18), (-4, 57, 18)]                        # back edge over the shelf
FOOT_LANTERNS = [(2, 27, 1), (2, 37, 1)]  # on cobblestone-wall posts on the east verge (road light at dusk)

# ------------------------------------------------------------------------------------------------------------------
# THE PENS (beats 4-6, 17), west of the exit road between house_e and the wall
# ------------------------------------------------------------------------------------------------------------------
CHICKEN_PEN = dict(box=(-23, 20, -17, 26), gates=[(-20, 20)], name="chicken_pen")
COW_PEN = dict(box=(-14, 20, -7, 26), gates=[(-11, 20)], name="cow_pen")

# ------------------------------------------------------------------------------------------------------------------
# THE SQUARE (beats 1-3, 7-10)
# ------------------------------------------------------------------------------------------------------------------
STONE_ROW = [(5, y, 0) for y in range(-16, -8)]          # eight stone blocks on the grass south-east of the plaza
BENCH_BOX = (-9, 4, -3, 6)                               # the smooth-stone floor of the open-air bench (NW corner)
BENCH = dict(torch=(-8, 5, 0), dust=[(-7, 5, 0), (-6, 5, 0)], repeater=(-5, 5, 0), block=(-4, 5, 0),
             lamp=(-4, 5, 1), piston=(-3, 5, 0), piston_facing="east")
COLUMN = dict(piston=(-4, 9, 0), pier=(-5, 9, 0), lever=(-5, 9, 1), lever_facing="west", blocks=12)


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
    for c in FOOT_LANTERNS:
        g = int(b.ground(c[0], c[1]))
        b.clear_plants(c[0], c[1])
        w.set(c[0], c[1], g, "cobblestone_wall", {"up": "true"})
        b.torch((c[0], c[1], g + 1), "lantern", {}, group="legday_road")
        b.reserved.add((c[0], c[1]))
    return dict(x=WALL_X, y=WALL_Y, top_z=TOP_Z, walk_z=WALK_Z, face_x=float(WALL_X[1] + 1), stair=dict(
        x=STAIR_X, y0=STAIR_Y0, steps=STEPS, foot=(STAIR_X + 0.5, STAIR_Y0 - 0.6, 0.0),
        top=(STAIR_X + 0.5, STAIR_Y0 + STEPS - 0.3, WALK_Z)), row_y=ROW_Y, pier=PIER, lever=LEVER,
        strip=(STRIP_X, STRIP_Y), lanterns=list(WALL_LANTERNS), road_lanterns=list(FOOT_LANTERNS))


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
    """Yaw of a character facing a compass direction (characters face -Y at yaw 0)."""
    return village.yaw_of(facing)


def _row_cell(i):
    """(x, y, z) of piston i (0 = the south one, by the lever) of the wall's row."""
    return (PISTON_X, ROW_Y[i], TOP_Z)


ANCHORS = {
    # ---- the square: beat 1 (the squats in front of the well, facing south; the narrator far back by his bench)
    "squat_steve": ((-0.55, -5.55), "south"), "squat_zuri": ((-1.75, -6.45), "south"),
    "squat_ari": ((0.75, -6.35), "south"), "narrator_far": ((-6.4, 3.1), "south"),
    # ---- beats 2-3: Steve punching the stone row (he stands west of it, facing east, the camera at its south end)
    "mine_1": ((4.22, -15.5), "east"), "mine_2": ((4.22, -14.5), "east"),
    "pickaxe_target": ((1.25, -14.5), None),                    # the dropped iron pickaxe: 3 blocks behind his back
    # ---- beats 7-8: the bench (the narrator south of it facing north; the two-shot in front of the lamp, facing south)
    "bench_narrator": ((-7.1, 3.62), "north"),
    "arms_narrator": ((-3.98, 4.15), "south"), "arms_steve": ((-3.02, 4.15), "south"),
    # ---- beats 9-10: the column (Steve at its south foot looking down at the piston; the narrator east of the pier)
    "column_steve": ((-3.5, 8.2), "north"), "column_narrator": ((-5.95, 9.3), "east"),
    "column_walk_end": ((-4.4, 2.6), None),                     # beat 10: where Steve's walk to the well ends
    # ---- the pens (pen_set adds chicken_pen_center / _gate, cow_pen_center / _gate)
    "kai_chickens": ((-19.6, 22.6), "south"), "zuri_cow": ((-11.6, 22.4), "south"),
    "cow_milk_target": ((-10.2, 23.1), None),                   # where the milked cow stands (beats 4-6)
    "narrator_fence": ((-10.55, 19.35), "north"),               # outside the cow pen's south fence (beat 6)
    "hide_1": ((-10.9, 21.8), "east"), "hide_2": ((-10.6, 22.9), "east"), "hide_3": ((-10.9, 24.0), "east"),
    "hide_4": ((-11.9, 23.4), "east"),                          # beat 17: behind the cows, heads toward the road
    "hide_cow_1_target": ((-8.7, 21.9), None), "hide_cow_2_target": ((-8.6, 23.4), None),
    "hide_cow_3_target": ((-8.7, 24.9), None),
    "arrow_post_target": ((-6.5, 20.5), None),                  # the cow pen's south-east corner post (x -7, y 20)
    # ---- the wall: road, stair, top
    "stair_foot": ((-0.5, 26.3), "north"),
    "stair_top": ((-0.5, 44.75, WALK_Z), "west"),               # the back half of the top step: as high as the walkway
    "wall_top_south": ((-1.5, 44.6, WALK_Z), "north"),
    "lever_narrator": ((-2.88, 45.28, WALK_Z), "west"),         # redstone Lever.stand() of the lever (checked later)
    "place_12th": ((-2.55, 46.45, WALK_Z), "east"),             # beat 13: he sets the 12th piston into (-2, 46, 17)
    "set_anvil_12th": ((-1.5, 45.45, WALK_Z), "east"),          # beat 14 / 24: Steve sets the 12th anvil on plank 0
    "wall_top_north": ((-2.5, 57.4, WALK_Z), "south"),
    "wall_top_lever_cam": ((-2.45, 44.15, WALK_Z + 0.22), None),   # (a camera spot: beat 14, on the walkway)
    # ---- the road under the shelf and beyond
    "road_shelf_south": ((0.5, 44.0), "north"), "road_shelf_north": ((0.5, 58.6), "south"),
    "runners_stop": ((0.55, 39.2), "north"),                    # beat 16: the three stop dead here (Steve)
    "steve_among_anvils": ((1.45, 48.15), "north"),             # beat 21: 2 blocks short of the drops
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
                      repeater=k.repeater(B["repeater"], "east", delay=1, name="bench_repeater"),
                      lamp=k.lamp(B["lamp"], name="bench_lamp"),
                      piston=k.piston(B["piston"], B["piston_facing"], name="bench_piston"))
    cx, cy, cz = COLUMN["piston"]
    P["column"] = dict(piston=k.piston(COLUMN["piston"], "up", name="column_piston"),
                       blocks=[k.block("iron_block", (cx, cy, cz + i), name="column_iron_%d" % i)
                               for i in range(1, COLUMN["blocks"] + 1)],
                       lever=k.lever(COLUMN["lever"], "floor", COLUMN["lever_facing"], name="column_lever"))
    return P


CAMERAS = {}
