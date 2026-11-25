"""FILM SETS: what a story adds to the village, built INTO the village (one World, one mesh, one set of checks).

A film passes a hook to the village builder and calls set pieces inside it:

    from engine import sets, village

    def edit(b):                                  # b = the village builder (engine/village.py: FILM SETS)
        sets.hello_set(b)                         # everything "The Hello" needs beyond the exit gate
    v = village.build_village(scene, seed=1, edit=edit)
    A = v.anchors                                 # A["forest_gap"], A["floating_oak_under"], A["pyramid_beside"] ...
    hello = v.sets["hello"]                       # what hello_set returned: cameras, trees, numbers
    road = v.paths["road_to_forest"]              # exit_gate -> the gap -> out of sight behind a trunk

PUBLIC API (every set piece is called inside the hook with the builder first, puts its blocks into b.w, registers
its anchors / yaws / paths on the Village, stores its result in Village.sets[name] and returns it)

    hello_set(b, layout=None, forest=None) -> dict
        The whole meadow of "The Hello" (positions: HELLO; layout={...} moves a piece, forest={...} are keyword
        arguments for dark_forest): the dark forest across the end of the exit road, the floating oak west of the
        road, three bare oaks on the east bank and the sand pyramid in front of them as seen from the road. The
        three small pieces stand outside a 28-35 mm frame from the exit gate (beat 6 is before any of them).
        Keys: forest, floating, bare, pyramid (the dicts below), cameras (name -> dict(pos, target, lens, fstop):
        the framings of the proof stills gate / side / inside / floating / bare / pyramid: a start, not a rule;
        the ground between each camera and its subject carries no plants), path = 'road_to_forest'.
    dark_forest(b, gap=(0.5, 58), half_width=26, depth=22, rows=4, name="forest", ...) -> dict
        A dark oak forest edge: the game's own dark oaks (DarkOakTrunkPlacer / DarkOakFoliagePlacer: 2x2 trunks 6-9
        high, bent tops, hanging branches, the 3-4 layer canopy) in `rows` rows that curve toward the village at
        both ends; the floor climbs behind the second row; plain oaks, tufts and tall grass along the edge; a thin
        dirt trail from the end of the village road to a 3-block gap between two trunks; a level corridor behind
        it. The wood is dark forest BIOME (darker grass, greener leaves, blended over 5 columns as in the game)
        and carries the game's own SKY LIGHT baked into its blocks (see Environment): that, not the scene's light,
        is what makes it a black wall under this look. Options in its own docstring.
        Anchors: <name>_gap (he stands here, on the tree line, facing the village), <name>_gap_in (the end of a
        walk in: 3 blocks in and behind the east trunk of the gap, hidden from every camera on the road),
        <name>_deep (the far end of the corridor, 6 blocks in), <name>_approach (3.5 blocks short of the gap),
        <name>_inside_cam (a camera spot in the corridor, looking out). Path road_to_<name>: exit_gate -> gap ->
        gap_in. Dict: those points, trees / oaks (records), tree_line, road_z, bounds, top, counts.
    floating_oak(b, tree, air=3, logs=2, name="floating_oak", stump="dirt", clear=4.5) -> dict
        The lazy player's tree: a vanilla small oak whose trunk is gone, the top `logs` logs left in the canopy
        over `air` clear blocks of air. tree = a record (b.trees, b.tree_at(x, y)) or an (x, y) spot. A small oak's
        leaves start 3 below its top, so the tree is re-grown air + 3 logs high first (6 for air 3: the game's
        tallest). With logs=2 the cut end sits one block up inside the leaves and shows only from almost below;
        logs=3 leaves it flush with the underside of the canopy. stump: the block under the trunk ('dirt' as the
        game leaves it, or 'grass'). Plants within `clear` blocks are removed (a tuft is as tall as a baby villager).
        Anchors <name>_under (stand here), <name>_target (the hanging logs). Dict: tree, under, canopy,
        leaf_bottom, top, base.
    bare_oak(b, tree) -> record                  an oak stripped to its logs, not one leaf left
    bare_oaks(b, spots, heights=(6, 5, 4), name="bare_oaks", level=True) -> dict
        Leafless oaks together, planted at `spots` [(x, y), ...] (or the oaks that stand there) on ground levelled
        for them. Anchors <name>_among (between the trunks, facing the village), <name>_center (look target).
    sand_pyramid(b, center, base=5, layers=3, name="pyramid") -> dict
        The legend's pyramid: square layers of sand, 5x5 / 3x3 / 1, on levelled, cleared grass. Anchors
        <name>_beside (1.5 blocks off the middle of its south side), <name>_target (its apex); path <name>_round
        (half way round it by the west); dict: sides (standing spots south / west / north / east), cells, top.
    plant_oak(b, x, y, rng, height=None, where="set") -> record       one vanilla small oak, 4-6 logs or `height`
    plant_dark_oak(b, x, y, rng, height=None, where="set", accept=None) -> record
        One vanilla dark oak; (x, y) = the south-west cell of its 2x2 trunk; accept(shape) picks a variation.
    remove_tree(b, tree)                         take a tree out, leaves and all
    clear_view(b, a, c, width=1.6)               no plants on the ground line from a to c (a low camera's view)
    oak_shape(rng, height=None) / dark_oak_shape(rng, height=None) -> dict(height, logs, leaves, ...)
        The pure shapes as cell offsets (Blender axes) from the trunk's base cell (dark oak: its south-west log).
    env(b) -> Environment                        biome colours and baked sky light of the builder's World:
        .set_biome(columns)                      these (x, y) columns are dark forest (5x5 blend around them)
        .bake_sky_light(b.ground, x0, y0, x1, y1)    compute the game's sky light in a box of columns and draw
                                                 every block face there as dark as the game would
        .level_at(x, y, z)                       sky light 0..15 at a point (15 = open sky)
    lightmap(level) -> 0..1                      the game's brightness for a sky light level (lightmap.fsh)
    dark_forest_colors() -> (grass, foliage)     (80, 122, 50), (89, 174, 48), from the game's colormaps

FOR THE DIRECTOR OF "THE HELLO" (measured on the proof stills, 540x960, look-dev golden sun azimuth 62 / elevation 27)
    - Tree line at y 58: 33.5 blocks beyond exit_gate. From the 'gate' camera (32 mm, 0.75 above the road at y
      22.6) the wall spans the whole width and stands between 28 % and 56 % of the frame height; a player at
      forest_gap is 45 px tall at 540x960 (60 px at 720x1280; 53 px with 28 mm): shirt, bare arms and head read,
      the face does not, but the eye whites of the plain Steve skin still show as two pale dots.
    - How dark the wall is from the gate is set by the look's haze, not by the wood: measured mean luminance of
      the trunk zone 62 / 255 against 104 for the sunlit meadow and 165 for the sky. For a blacker wall lower the
      haze of that film (look.setup_compositor(..., haze=...)); dark_forest(brightness=0.0) (the game's "Moody")
      blackens the wood in close shots (side, inside) and changes almost nothing from the gate.
    - The sun belongs in the northern half of the sky (azimuth 20-160: behind or beside the wood). The wall is then
      in its own shade and the last 20 blocks of road lie in the wood's shadow. A sun in the south lights the
      trunk fronts; the baked sky light keeps the inside dark either way.
    - Characters are not blocks: inside the wood a figure is lit by the scene like anywhere else (sun shadow yes,
      but the look's fill and bounce lamps are shadowless). He does not go black in there; he goes out of sight:
      walk him along road_to_forest, whose last leg turns behind the east trunk (forest_gap_in), and hide him
      there (show(frame, False)). At night the look's haze greys the far inside of the wood: trunks are darker
      than what lies behind them (out/test/sets_night.png).
    - Camera spots that are kept free of plants: the road and the lane west of it up to the gap (x -3..3), a bay
      west of the road in front of the tree line (x -11..-4, y 50..57: the 'side' camera), and the ground between
      each camera of hello_set(...)["cameras"] and its subject. Everywhere else along the tree line tall grass
      stands as high as a baby villager.
    - tools/palette_check.py does not know the darkened / dark-forest tints of the wood's blocks: its plant and
      ground checks are meaningless inside the wood.

HOW TO ADD A SET PIECE (the five later films)
    One function per piece: def iron_farm(b, at, name="iron_farm", ...) -> dict.
    1. Take a random generator of your own: rng = b.rng_for(name) (never b.rng: that is the village's sequence).
    2. Prepare the ground: b.extend_terrain(...) where the piece reaches beyond the disc of terrain,
       b.set_ground(x, y, z) to level, b.clear_plants / b.sow for what grows, b.pave for paths. Then put blocks
       into b.w (b.w.set / fill). Torches: b.torch(cell, ...) or a plain b.w.set of a torch block: either way they
       get a light. Beds and doors that must be used: b.bed(...), b.door(...). A piece dug in under the ground
       calls b.show_undersides(box).
    3. Mark the columns you built on in b.reserved (nothing is sown or planted there afterwards). If the piece is
       MEANT to change a house or a street say so, b.allow("house_a") / b.allow("streets"): otherwise the build
       stops with the list of what was changed where.
    4. Register what the director needs: b.anchor(name + "_x", (x, y), yaw) for standing spots (2D = on the
       ground), b.path(name + "_y", [...]) for walks. Village.validate() treats every anchor as a place where a
       figure stands unless its name ends in _target, _center, _cam or _station: name look targets and camera
       spots that way, or keep them in the returned dict only.
    5. A piece that must be dark inside (a hall under the ground, a wood): env(b).bake_sky_light(...) LAST, when
       all its blocks are placed. b.v.sets[name] = result; return result, with counts in it.
    The hook is the only way in: when build_village returns, the world is one mesh per material and nothing can
    be added to it (separate props after the fact are engine/props.py and engine/fx.py).

WHAT THE GAME DOES (transcribed from the 26.3 client jar; no game file is copied)
    dark oak   data/minecraft/worldgen/feature/dark_oak.json: dark_oak_trunk_placer base_height 6, height_rand_a
               2, height_rand_b 1 (TrunkPlacer.getTreeHeight: 6 + nextInt(3) + nextInt(2) = 6..9), foliage placer
               radius 0 offset 0. DarkOakTrunkPlacer.placeTrunk: a 2x2 trunk (origin, east, south, south-east);
               from layer height - nextInt(4) on, up to 2 - nextInt(3) layers step sideways in one random
               horizontal direction (the bent top); the main canopy attaches at the top of the bent trunk; each of
               the 12 cells around the ORIGINAL 2x2 gets, with chance 1/3, a branch: 2 + nextInt(3) logs hanging
               down from one below the top, with a small canopy of its own. DarkOakFoliagePlacer: main canopy =
               rows at y -1 (6x6), y 0 (8x8 without its corners: 1 cell at the low corner, 2, 2 and 4 at the
               others: the shape is not symmetric), y +1 (6x6 with the corners cut on the diagonal), and with
               chance 1/2 a 2x2 cap at y +2; branch canopy = 5x5 without corners at y -1 and 3x3 at y 0.
    oak        feature/oak.json: straight_trunk_placer 4 + nextInt(3); blob_foliage_placer radius 2, height 3:
               rows of radius 1, 1, 2, 2 from one above the top log downward, a corner left out with chance
               1/2 (always on the top row). Soil: soil_beneath_tree puts dirt under a trunk unless the block is in
               the tag cannot_replace_below_tree_trunk (dirt, coarse dirt, rooted dirt, mud, moss, podzol): a
               grass block under a trunk becomes dirt, so a felled trunk leaves a dirt block.
    dark forest  worldgen/feature/dark_forest_vegetation.json (16 tries per chunk): huge brown mushroom 2.5 %,
               huge red 5 %, then dark oak 2/3, birch 20 %, fancy oak 10 %, else plain oak: of all trees about
               62 % dark oaks, 22 % plain oaks. Biome colours (Biome.getGrassColor / getFoliageColor, colormaps at
               temperature 0.7, downfall 0.8; GrassColorModifier DARK_FOREST = ((c & 0xFEFEFE) + 0x28340A) >> 1):
               grass (80, 122, 50), foliage (89, 174, 48); the plains village has (145, 189, 89) and (119, 171, 47).
    light      sky light 15 under open sky, minus 1 per block in any direction, also through leaves; brightness
               from assets/minecraft/shaders/core/lightmap.fsh (see Environment below).
    Sand, logs, leaves, mushrooms are the game's own block models and textures (engine.blocks / engine.mcassets).

Self-test:  $BPY -m engine.sets                    numbers only (the shapes against the classes' rules, hello_set
                                                   built into the village: anchors, paths, light, counts): 10 s
            $BPY -m engine.sets gate gap side ...  the proof stills out/test/sets_<name>.png through the real look
                                                   (films/_sets_proof.py: gate gap side inside floating bare
                                                   pyramid night map; about 40 s each, at most 3 per call)
            $BPY -m tools.check_sets_hook --film   the village without a hook is unchanged (digests + the stamps
                                                   of the finished film "The Nitwit"); --hook: the hook's promises
            $BPY -m tools.check_sets_stamp         the set is in the frame fingerprints (engine/stamp.py)
"""
import math

import numpy as np

from .village import yaw_to

# ---- numbers from the game -------------------------------------------------------------------------------------
DARK_OAK_HEIGHT = (6, 2, 1)           # dark_oak.json trunk_placer: base_height, height_rand_a, height_rand_b
OAK_HEIGHT = (4, 2, 0)                # oak.json trunk_placer (straight_trunk_placer)
OAK_FOLIAGE = (2, 3)                  # oak.json blob_foliage_placer: radius, height
LEAF_PROPS = {"persistent": "false", "distance": "1", "waterlogged": "false"}
LOG_PROPS = {"axis": "y"}
# Direction.Plane.HORIZONTAL as (east, south) steps in the game's axes: north, east, south, west
_HORIZONTAL = ((0, -1), (1, 0), (0, 1), (-1, 0))
# the dark forest's mix after the mushrooms (dark_forest_vegetation.json): dark oak 2/3, then of the rest birch 20 %,
# fancy oak 10 %, plain oak otherwise
DARK_FOREST_OAK_SHARE = (1 - 2 / 3.0) * (1 - 0.2) * (1 - 0.1)       # 0.24 of the trees are plain oaks
PLANTS = ("short_grass", "tall_grass", "poppy", "dandelion", "oxeye_daisy", "cornflower", "brown_mushroom",
          "red_mushroom", "fern")


# ---- tree shapes -----------------------------------------------------------------------------------------------

def oak_shape(rng, height=None):
    """A vanilla small oak as cell offsets from the base of its trunk: dict(height, logs, leaves).
    StraightTrunkPlacer + BlobFoliagePlacer with the numbers of feature/oak.json (see the module docstring)."""
    base, rand_a, rand_b = OAK_HEIGHT
    h = int(height) if height else base + int(rng.integers(0, rand_a + 1)) + int(rng.integers(0, rand_b + 1))
    radius, fol_h = OAK_FOLIAGE
    logs = [(0, 0, i) for i in range(h)]
    leaves = []
    for yo in range(0, -fol_h - 1, -1):                    # BlobFoliagePlacer.createFoliage: yo = offset .. offset - height
        r = max(radius - 1 - int(yo / 2), 0)               # (Java's integer division rounds toward zero: int(yo / 2))
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                # BlobFoliagePlacer.shouldSkipLocation: a corner, and (nextInt(2) == 0 or the top row)
                if abs(dx) == r and abs(dy) == r and (rng.random() < 0.5 or yo == 0):
                    continue
                c = (dx, dy, h + yo)                       # the attachment is one above the top log
                if c not in logs:
                    leaves.append(c)
    return dict(height=h, logs=logs, leaves=leaves)


def _dark_oak_skip(dx, y, dz, r, double):
    """DarkOakFoliagePlacer.shouldSkipLocationSigned -> FoliagePlacer.shouldSkipLocationSigned -> shouldSkipLocation."""
    if y == 0 and double and (dx == -r or dx >= r) and (dz == -r or dz >= r):
        return True
    if double:
        mx, mz = min(abs(dx), abs(dx - 1)), min(abs(dz), abs(dz - 1))
    else:
        mx, mz = abs(dx), abs(dz)
    if y == -1 and not double:
        return mx == r and mz == r
    if y == 1:
        return mx + mz > r * 2 - 2
    return False


def dark_oak_shape(rng, height=None):
    """A vanilla dark oak as cell offsets (Blender axes) from the SOUTH-WEST cell of its 2x2 trunk at ground level:
    dict(height, logs, leaves, bend, branches, cap). DarkOakTrunkPlacer.placeTrunk + DarkOakFoliagePlacer with the
    numbers of feature/dark_oak.json; the random calls are made in the game's order."""
    base, rand_a, rand_b = DARK_OAK_HEIGHT
    h = int(height) if height else base + int(rng.integers(0, rand_a + 1)) + int(rng.integers(0, rand_b + 1))
    logs, leaves = {}, {}                                  # game axes: (x east, y up, z south), origin = north-west log
    sx, sz = _HORIZONTAL[int(rng.integers(0, 4))]
    bend_from = h - int(rng.integers(0, 4))
    bend_left = 2 - int(rng.integers(0, 3))
    x = z = 0
    top = h - 1
    for i in range(h):
        if i >= bend_from and bend_left > 0:
            x += sx
            z += sz
            bend_left -= 1
        for ax, az in ((0, 0), (1, 0), (0, 1), (1, 1)):
            logs[(x + ax, i, z + az)] = True
    attach = [((x, top, z), True)]
    branches = 0
    for dx in range(-1, 3):
        for dz in range(-1, 3):
            if 0 <= dx <= 1 and 0 <= dz <= 1:
                continue
            if int(rng.integers(0, 3)) > 0:
                continue
            for k in range(int(rng.integers(0, 3)) + 2):
                logs[(dx, top - k - 1, dz)] = True
            attach.append(((dx, top, dz), False))
            branches += 1

    def row(pos, r, y, double):                            # FoliagePlacer.placeLeavesRow
        off = 1 if double else 0
        for dx in range(-r, r + off + 1):
            for dz in range(-r, r + off + 1):
                if _dark_oak_skip(dx, y, dz, r, double):
                    continue
                c = (pos[0] + dx, pos[1] + y, pos[2] + dz)
                if c not in logs:                          # tryPlaceLeaf: only into air / leaves
                    leaves[c] = True

    cap = False
    for pos, double in attach:                             # DarkOakFoliagePlacer.createFoliage, leaf radius 0
        if double:
            row(pos, 2, -1, True)
            row(pos, 3, 0, True)
            row(pos, 2, 1, True)
            if rng.random() < 0.5:
                row(pos, 0, 2, True)
                cap = True
        else:
            row(pos, 2, -1, False)
            row(pos, 1, 0, False)

    def conv(c):                                           # game (x, y, z) from the north-west log -> Blender offset
        return (c[0], 1 - c[2], c[1])                      # from the south-west log: north is +Y, the origin row is y + 1

    return dict(height=h, logs=[conv(c) for c in logs], leaves=[conv(c) for c in leaves],
                bend=(x, -z), branches=branches, cap=cap)


# ---- planting and felling --------------------------------------------------------------------------------------

def _other_leaves_beside(w, cell, block_id):
    for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        nb = w.block_id(cell[0] + dx, cell[1] + dy, cell[2] + dz)
        if nb is not None and nb.endswith("_leaves") and nb != block_id:
            return True
    return False


def _place_tree(b, kind, x, y, base, shape, where):
    """Put a tree shape into the World: logs replace whatever is there, leaves go into free cells only, and never
    face to face with another kind of leaves (two different cut-out textures in one plane would flicker)."""
    w = b.w
    log, leaf = kind + "_log", kind + "_leaves"
    rec = dict(kind=kind, x=x, y=y, base=base, height=shape["height"], logs=[], leaves=[], where=where)
    for dx, dy, dz in shape["logs"]:
        c = (x + dx, y + dy, base + dz)
        w.set(c[0], c[1], c[2], log, LOG_PROPS)
        rec["logs"].append(c)
    for dx, dy, dz in shape["leaves"]:
        c = (x + dx, y + dy, base + dz)
        if w.get(*c) is None and not _other_leaves_beside(w, c, leaf):
            w.set(c[0], c[1], c[2], leaf, LEAF_PROPS)
            rec["leaves"].append(c)
    for k in ("bend", "branches", "cap"):
        if k in shape:
            rec[k] = shape[k]
    b.trees.append(rec)
    return rec


def plant_oak(b, x, y, rng, height=None, where="set"):
    """Plant one vanilla small oak with its trunk in column (x, y), `height` logs high (None: the game's 4-6).
    Returns its record (as b.tree does) or None where there is no ground."""
    base = b.ground(x, y)
    if base is None:
        return None
    b.clear_plants(x, y)
    b.w.set(x, y, base - 1, "dirt")                        # soil_beneath_tree: grass under a trunk becomes dirt
    rec = _place_tree(b, "oak", x, y, base, oak_shape(rng, height), where)
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            b.reserved.add((x + dx, y + dy))
    return rec


def plant_dark_oak(b, x, y, rng, height=None, where="set", accept=None):
    """Plant one vanilla dark oak whose 2x2 trunk has its south-west cell in column (x, y). The four columns are
    levelled to the highest of them first (the game would leave part of the trunk hanging). accept(shape) -> bool
    picks among the game's own variations (up to 40 are drawn until one is accepted). Returns its record."""
    cols = ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1))
    hs = [b.ground(*c) for c in cols]
    if any(h is None for h in hs):
        return None
    base = max(hs)
    for c in cols:
        b.set_ground(c[0], c[1], base)
        b.clear_plants(*c)
        b.w.set(c[0], c[1], base - 1, "dirt")
    shape = dark_oak_shape(rng, height)
    for _ in range(40):
        if accept is None or accept(shape):
            break
        shape = dark_oak_shape(rng, height)
    rec = _place_tree(b, "dark_oak", x, y, base, shape, where)
    for dx in range(-1, 3):
        for dy in range(-1, 3):
            b.reserved.add((x + dx, y + dy))
    return rec


def _strip(b, tree, what):
    """Remove the logs and / or leaves a tree record still owns. Returns the number of blocks removed."""
    w = b.w
    n = 0
    for key in what:
        want = tree["kind"] + ("_log" if key == "logs" else "_leaves")
        for c in tree[key]:
            if w.block_id(*c) == want:
                w.set(c[0], c[1], c[2], None)
                n += 1
        tree[key] = []
    return n


def remove_tree(b, tree):
    """Take a tree out of the set, leaves and all; the dirt under its trunk becomes grass again."""
    w = b.w
    cols = {(c[0], c[1]) for c in tree["logs"] if c[2] == tree["base"]}
    _strip(b, tree, ("logs", "leaves"))
    for x, y in cols:
        if w.block_id(x, y, tree["base"] - 1) == "dirt":
            w.set(x, y, tree["base"] - 1, "grass_block", {"snowy": "false"})
    if tree in b.trees:
        b.trees.remove(tree)


def _tree_arg(b, tree, rng, height=None, where="set"):
    """A tree record from a record, or from an (x, y) spot: the tree that stands there, else a newly planted oak."""
    if isinstance(tree, dict):
        return tree
    x, y = int(tree[0]), int(tree[1])
    return b.tree_at(x, y) or plant_oak(b, x, y, rng, height, where)


def clear_view(b, a, c, width=1.6):
    """Remove every plant on the columns within `width` blocks of the ground line from a to c ((x, y) points): a
    low camera at a sees c, not a grass tuft one block from the lens."""
    ax, ay, cx, cy = float(a[0]), float(a[1]), float(c[0]), float(c[1])
    n = max(1, int(math.hypot(cx - ax, cy - ay) * 2))
    done = set()
    r = int(math.ceil(width))
    for i in range(n + 1):
        px, py = ax + (cx - ax) * i / n, ay + (cy - ay) * i / n
        for x in range(int(math.floor(px)) - r, int(math.floor(px)) + r + 1):
            for y in range(int(math.floor(py)) - r, int(math.floor(py)) + r + 1):
                if (x, y) not in done and math.hypot(x + 0.5 - px, y + 0.5 - py) <= width:
                    done.add((x, y))
                    b.clear_plants(x, y)
    return done


def _new_name(b, name):
    """A set piece's name must be new in this village: the same piece built twice would stand in itself."""
    if name in b.v.sets:
        raise ValueError("set piece %r exists already in this village: give the second one another name=" % name)


def _columns_along(a, c):
    """[(s0, s1, (cx, cy))]: the columns the ground line a -> c passes through, with the distances from a."""
    length = math.hypot(c[0] - a[0], c[1] - a[1])
    ts = {0.0, 1.0}
    for k in (0, 1):
        d = c[k] - a[k]
        if abs(d) > 1e-9:
            lo, hi = min(a[k], c[k]), max(a[k], c[k])
            for g in range(int(math.floor(lo)) + 1, int(math.ceil(hi))):
                ts.add((g - a[k]) / d)
    ts = sorted(t for t in ts if 0.0 <= t <= 1.0)
    out = []
    for t0, t1 in zip(ts, ts[1:]):
        if (t1 - t0) * length < 1e-6:
            continue
        tm = 0.5 * (t0 + t1)
        col = (int(math.floor(a[0] + (c[0] - a[0]) * tm)), int(math.floor(a[1] + (c[1] - a[1]) * tm)))
        out.append((t0 * length, t1 * length, col))
    return out


STEP_RUN = 0.6          # a 1-block step is climbed (or dropped) over this much ground, clear of the block's edge
STEP_CLEAR = 0.3        # ... by half a body's width


def ground_path(b, name, points, replace=False, check=True):
    """Register the walkable polyline `name` through the (x, y) `points` so that it FOLLOWS THE GROUND between
    them, not only at them (b.path takes the height at its nodes and a walker cuts through whatever lies between).
    Where the walking height changes from one column to the next a pair of nodes is put in: grass <-> dirt_path
    (1/16) over 0.3 block, and a 1-block step of the terrain as the hop the game makes of it: the walker rises
    over STEP_RUN (0.6) block of ground and is up before his body reaches the higher block (down: the other way
    round). Character.walk moves in straight lines, so at 3 blocks/s a hop is 5 frames. A step of 2 blocks or more
    cannot be walked: ValueError; so is a path that runs into a block (check=False skips that test). Returns the
    3D points; the number of hops is len(b.v.sets['paths'][name]['hops'])."""
    pts2 = [(float(p[0]), float(p[1])) for p in points]
    if len(pts2) < 2:
        raise ValueError("ground_path %r needs two points or more" % name)
    out, hops = [], []
    for a, c in zip(pts2, pts2[1:]):
        length = math.hypot(c[0] - a[0], c[1] - a[1])
        if length < 1e-6:
            continue
        cols = _columns_along(a, c)
        hs = [b.walk_z(col[0] + 0.5, col[1] + 0.5) for _s0, _s1, col in cols]
        if any(h is None for h in hs):
            raise ValueError("ground_path %r: no terrain at column %s" % (name, cols[hs.index(None)][2]))
        nodes = [(0.0, hs[0])]                               # (distance along the leg, height)
        for i in range(1, len(cols)):
            s, h0, h1 = cols[i][0], hs[i - 1], hs[i]
            dh = h1 - h0
            if abs(dh) < 1e-6:
                continue
            if abs(dh) > 1.2:
                raise ValueError("ground_path %r: a step of %.1f blocks at column %s" % (name, dh, cols[i][2]))
            if abs(dh) < 0.3:
                nodes += [(s - 0.15, h0), (s + 0.15, h1)]
            elif dh > 0:
                nodes += [(s - STEP_CLEAR - STEP_RUN, h0), (s - STEP_CLEAR, h1)]
                hops.append((round(a[0] + (c[0] - a[0]) * s / length, 2), round(a[1] + (c[1] - a[1]) * s / length, 2), 1))
            else:
                nodes += [(s + STEP_CLEAR, h0), (s + STEP_CLEAR + STEP_RUN, h1)]
                hops.append((round(a[0] + (c[0] - a[0]) * s / length, 2), round(a[1] + (c[1] - a[1]) * s / length, 2), -1))
        nodes.append((length, hs[-1]))
        keep = [nodes[0]]
        for s, h in nodes[1:-1]:                             # in order along the leg, inside it, no two on one spot
            s = min(max(s, keep[-1][0] + 0.02), length - 0.02)
            if s > keep[-1][0] + 0.01:
                keep.append((s, h))
        if length > keep[-1][0] + 1e-6:
            keep.append(nodes[-1])
        for s, h in keep:
            p = (a[0] + (c[0] - a[0]) * s / length, a[1] + (c[1] - a[1]) * s / length, float(h))
            if not out or math.dist(out[-1], p) > 1e-4:
                out.append(p)
    old = b.v.paths.get(name)
    path = b.path(name, out, replace=replace)
    if check:
        hits = b.v.path_clear(path)
        if hits:
            if old is None:
                del b.v.paths[name]
            else:
                b.v.paths[name] = old
            raise ValueError("ground_path %r runs into %s" % (name, hits[:2]))
    b.v.sets.setdefault("paths", {})[name] = dict(hops=hops, points=pts2)
    return path


def floating_oak(b, tree, air=3, logs=2, name="floating_oak", stump="dirt", clear=4.5):
    """The classic lazy player's tree: the trunk taken, the canopy left hanging `air` clear blocks above the grass
    with the top `logs` logs of the trunk still in it. tree = a record of b.trees or an (x, y) spot.
    air   1..3: a small oak's canopy starts 3 blocks below its top and the game's oak has 4-6 logs, so the tree is
          re-grown air + 3 logs high first if it is not (air 3 = the tallest oak there is; more is refused).
    logs  1..air + 2 logs left at the top. The top 3 are INSIDE the leaves: logs=2 shows no wood at all except from
          right below, logs=3 a cut end flush with the underside of the canopy; logs=4 leaves one log hanging
          under the leaves over air - 1 blocks of air (the picture every player knows), logs=5 two.
    stump = what is left under the trunk: 'dirt' (as the game leaves it) or 'grass' (grown over).
    Dict: tree, under, canopy, air, logs, hanging (logs below the leaves), gap (clear blocks over the stump),
    leaf_bottom, top, base."""
    _new_name(b, name)
    air, logs = int(air), int(logs)
    if not 1 <= air <= 3:
        raise ValueError("floating_oak: air=%d; the game's small oak has 4-6 logs, so 1..3 clear blocks under its "
                         "canopy" % air)
    if not 1 <= logs <= air + 2:
        raise ValueError("floating_oak: logs=%d; with air=%d there are 1..%d (the oak has %d logs and one block "
                         "of air must stay under them)" % (logs, air, air + 2, air + 3))
    rng = b.rng_for(name)
    tree = _tree_arg(b, tree, rng, air + 3, name)
    x, y, base = tree["x"], tree["y"], tree["base"]
    if tree["height"] != air + 3:
        remove_tree(b, tree)
        tree = plant_oak(b, x, y, rng, air + 3, name)
    h = tree["height"]
    w = b.w
    gone = [c for c in tree["logs"] if c[2] < base + h - logs]
    for c in gone:
        w.set(c[0], c[1], c[2], None)
    tree["logs"] = [c for c in tree["logs"] if c not in gone]
    tree["felled"] = len(gone)
    if stump == "grass":
        w.set(x, y, base - 1, "grass_block", {"snowy": "false"})
    r = int(math.ceil(clear))                              # bare grass under and around it: the gap must show sky,
    for dx in range(-r, r + 1):                            # and a tuft is as tall as a baby villager
        for dy in range(-r, r + 1):
            if math.hypot(dx, dy) <= clear:
                b.clear_plants(x + dx, y + dy)
    under = b.anchor(name + "_under", (x + 0.5, y + 0.5, float(base)), replace=True)
    canopy = (x + 0.5, y + 0.5, base + h - logs + 0.5 * logs)
    b.v.anchors[name + "_target"] = canopy
    hanging = max(0, logs - 3)
    res = dict(tree=tree, under=under, canopy=canopy, air=air, logs=logs, base=base, hanging=hanging,
               gap=air - hanging, leaf_bottom=base + h - 3, top=base + h + 1)
    b.v.sets[name] = res
    return res


def bare_oak(b, tree):
    """Strip an oak to its logs: not one leaf of its own is left. tree = a record or an (x, y) spot. Returns the
    record (leaves now empty, 'stripped' = the number of leaf blocks taken)."""
    tree = _tree_arg(b, tree, b.rng_for("bare_oak %s" % (tree if not isinstance(tree, dict) else tree["x"],)))
    tree["stripped"] = _strip(b, tree, ("leaves",))
    return tree


def bare_oaks(b, spots, heights=(6, 5, 4), name="bare_oaks", level=True):
    """Leafless oaks standing together: at each (x, y) of `spots` the oak that stands there, or a new one of the
    matching height in `heights`, is stripped to its logs. level=True first levels the ground they share (the box
    around the spots plus one block) to its most common height and clears it of plants. Anchors <name>_among
    (between the trunks, facing the village square) and <name>_center."""
    _new_name(b, name)
    rng = b.rng_for(name)
    trees = []
    if level:
        xs, ys = [int(p[0]) for p in spots], [int(p[1]) for p in spots]
        cols = [(x, y) for x in range(min(xs) - 1, max(xs) + 2) for y in range(min(ys) - 1, max(ys) + 2)
                if b.ground(x, y) is not None]
        hs = sorted(b.ground(*c) for c in cols)
        z = max(set(hs), key=hs.count)
        for c in cols:
            if not b.tree_at(*c):
                b.set_ground(c[0], c[1], z)
            b.clear_plants(*c)
            b.reserved.add(c)
    for i, (x, y) in enumerate(spots):
        t = b.tree_at(int(x), int(y)) or plant_oak(b, int(x), int(y), rng, heights[i % len(heights)], name)
        trees.append(bare_oak(b, t))
    cx = sum(t["x"] + 0.5 for t in trees) / len(trees)
    cy = sum(t["y"] + 0.5 for t in trees) / len(trees)
    among = b.anchor(name + "_among", (cx, cy), yaw_to((cx, cy), (0.5, 0.0)), replace=True)
    top = max(t["base"] + t["height"] for t in trees)
    b.v.anchors[name + "_center"] = (cx, cy, among[2] + 2.5)
    res = dict(trees=trees, among=among, center=b.v.anchors[name + "_center"], top=top,
               trunks=[(t["x"] + 0.5, t["y"] + 0.5, t["base"], t["height"]) for t in trees])
    b.v.sets[name] = res
    return res


# ---- the sand pyramid ------------------------------------------------------------------------------------------

def sand_pyramid(b, center, base=5, layers=3, name="pyramid"):
    """The legend's small pyramid on the grass: `layers` square layers of sand, `base` blocks wide at the bottom and
    2 narrower each layer up, centred on column `center` (x, y). The ground under it is levelled to the centre
    column and cleared. Anchors <name>_beside (a standing spot 1.5 blocks off the middle of its south side),
    <name>_target; path <name>_round (half way round it, from the south side to the north side by the west; it
    follows the ground, see ground_path; where the ground around the pyramid cannot be walked the path is left
    out and dict['round'] is None). base must be odd (the pyramid has one block on top) and layers 1..(base+1)/2."""
    _new_name(b, name)
    base, layers = int(base), int(layers)
    if base < 1 or base % 2 == 0:
        raise ValueError("sand_pyramid: base=%d; an odd width is needed (5 -> 5x5, 3x3, 1)" % base)
    if not 1 <= layers <= (base + 1) // 2:
        raise ValueError("sand_pyramid: layers=%d; a base of %d has room for 1..%d" % (layers, base, (base + 1) // 2))
    cx, cy = int(center[0]), int(center[1])
    z0 = b.ground(cx, cy)
    if z0 is None:
        raise ValueError("sand_pyramid: no terrain at %s" % ((cx, cy),))
    half = base // 2
    for x in range(cx - half - 1, cx + half + 2):
        for y in range(cy - half - 1, cy + half + 2):
            inner = abs(x - cx) <= half and abs(y - cy) <= half
            if inner and b.ground(x, y) != z0:
                b.set_ground(x, y, z0)
            if inner or b.ground(x, y) == z0:
                b.clear_plants(x, y)                       # one clean block of grass all round: its foot shows
            if inner:
                b.reserved.add((x, y))
    cells = []
    for k in range(layers):
        r = half - k
        if r < 0:
            break
        for x in range(cx - r, cx + r + 1):
            for y in range(cy - r, cy + r + 1):
                b.w.set(x, y, z0 + k, "sand")
                cells.append((x, y, z0 + k))
    top = (cx + 0.5, cy + 0.5, z0 + min(layers, half + 1))
    d = half + 2.0                                         # 1.5 blocks clear of the bottom layer
    sides = {"south": (cx + 0.5, cy + 0.5 - d), "west": (cx + 0.5 - d, cy + 0.5), "north": (cx + 0.5, cy + 0.5 + d),
             "east": (cx + 0.5 + d, cy + 0.5)}
    spots = {}
    for k, p in sides.items():
        z = b.walk_z(*p)
        spots[k] = (p[0], p[1], float(z if z is not None else z0))
    beside = b.anchor(name + "_beside", spots["south"], yaw_to(spots["south"], top), replace=True)
    b.v.anchors[name + "_target"] = top
    ring = [spots["south"], (cx + 0.5 - d, cy + 0.5 - d), spots["west"], (cx + 0.5 - d, cy + 0.5 + d), spots["north"]]
    try:
        path = ground_path(b, name + "_round", [(p[0], p[1]) for p in ring], replace=True)
    except ValueError as e:                                # a tree, a wall or a 2-block bank in the way
        path = None
        print("[sets] %s: no path round it (%s)" % (name, e))
    res = dict(center=(cx, cy), ground=z0, base=base, layers=layers, cells=cells, top=top, beside=beside,
               sides=spots, round=path, height=min(layers, half + 1))
    b.v.sets[name] = res
    return res


# ---- the game's own light and biome colours, baked into the blocks ----------------------------------------------
#
# The village's look (engine/look.py) fills every shadow with shadowless bounce lamps and a strong sky fill: right
# for streets and faces, but a wood stays as bright inside as the meadow in front of it. The game itself draws a
# block darker the less sky light reaches it, and that is what makes a dark forest dark. So a set piece may bake
# the game's sky light into the colour of its blocks (and give its ground and leaves the colours of its biome):
#   sky light   15 under open sky, straight down through air; minus 1 for every step in any direction, also
#               through leaves (LeavesBlock: light dampening 1); nothing passes a full block (LightEngine)
#   brightness  shaders/core/lightmap.fsh: b = level / 15, f = b / (4 - 3 b), colour = mix(f, 1 - (1 - f)^4, gamma),
#               gamma = the Brightness option (default 0.5): level 15 -> 1.00, 13 -> 0.80, 11 -> 0.64, 9 -> 0.50,
#               7 -> 0.36, 5 -> 0.24, 3 -> 0.14. The game multiplies it into the texel like a tint: so does this.
#   face        a face takes the light of the cell it looks into (the game with Smooth Lighting off); below level
#               11 the levels are used in pairs (9, 7, 5, 3) to keep the number of materials down.
#   biome       grass / foliage colour = the average over the 5x5 columns around (the game's default Biome Blend).
# Characters are not blocks: a figure in the wood is lit by the scene's lights like anywhere else.

BIOME_BLEND = 2                       # columns to either side: Biome Blend 5x5
LIGHT_GAMMA = 0.5                     # the game's Brightness option at its default
LIGHT_FLOOR = 3                       # darker cells are drawn as level 3


def lightmap(level, gamma=LIGHT_GAMMA):
    """Brightness 0..1 the game draws a block with at sky light `level` (0..15) by day: lightmap.fsh."""
    b = max(0.0, min(15.0, float(level))) / 15.0
    f = b / (4.0 - 3.0 * b)
    return f + (1.0 - (1.0 - f) ** 4 - f) * gamma


def dark_forest_colors():
    """(grass, foliage) of the dark forest biome as (r, g, b): the colormaps at temperature 0.7, downfall 0.8, the
    grass through BiomeSpecialEffects.GrassColorModifier DARK_FOREST."""
    from . import mcassets as mc

    g = mc._colormap("grass", 0.7, 0.8, fallback=(121, 192, 90))
    f = mc._colormap("foliage", 0.7, 0.8, fallback=(89, 174, 48))
    v = ((((g[0] << 16) | (g[1] << 8) | g[2]) & 0xFEFEFE) + 0x28340A) >> 1
    return ((v >> 16) & 255, (v >> 8) & 255, v & 255), f


class _LitState:
    """A baked block state (blocks._State) with other tints: what World.build reads, nothing more."""
    __slots__ = ("quads", "cover", "block_id")


class Environment:
    """Biome colours and baked sky light for part of a World (see the comment above). One per World: env(b)."""

    def __init__(self, world):
        from . import mcassets as mc

        self.w = world
        self.biome_columns = set()    # columns that are dark forest
        self.share = {}               # (x, y) -> share of dark forest in the 5x5 around it, in fifths (1..5)
        self.light = {}               # (x, y, z) -> sky light 0..14 of a cell (absent: 15)
        self.columns = set()          # columns where anything differs from the plain village
        self.gamma = LIGHT_GAMMA      # the game's Brightness option for the baked light (0 = Moody, 1 = Bright)
        self._cache = {}
        self._plain = (mc.biome_tint("grass"), mc.biome_tint("foliage"))
        self._forest = dark_forest_colors()
        self._kinds = (mc._GRASS_TINTED, mc._FOLIAGE_TINTED)
        self._offsets = [(d, mc.DIR_BLENDER[d]) for d in mc.DIRS]
        self._inner = world._state_at
        world._state_at = self.state_at          # World.build asks the instance: only this World is affected

    # -- biome
    def set_biome(self, columns):
        """Make these (x, y) columns dark forest; the colours blend over 5x5 columns as in the game."""
        self.biome_columns |= set(columns)
        r = BIOME_BLEND
        count = {}
        for x, y in self.biome_columns:
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    c = (x + dx, y + dy)
                    count[c] = count.get(c, 0) + 1
        n = float((2 * r + 1) ** 2)
        self.share = {c: int(round(5.0 * k / n)) for c, k in count.items() if int(round(5.0 * k / n)) > 0}
        self.columns |= set(self.share)
        self._cache.clear()

    def color(self, kind, share):
        """Grass (kind 0) or foliage (kind 1) colour for a share of dark forest in fifths."""
        a, c = self._plain[kind], self._forest[kind]
        t = share / 5.0
        return tuple(int(round(a[i] + (c[i] - a[i]) * t)) for i in range(3))

    # -- sky light
    def bake_sky_light(self, ground, x0, y0, x1, y1):
        """Compute the game's sky light for the box of columns and remember every cell darker than 15.
        ground(x, y) -> terrain surface z or None. Call it when every block of the set piece is placed."""
        w = self.w
        nx, ny = x1 - x0 + 1, y1 - y0 + 1
        zs = [c[2] for c in w.blocks if x0 <= c[0] <= x1 and y0 <= c[1] <= y1]
        if not zs:
            return 0
        z0, z1 = min(zs) - 1, max(zs) + 2
        nz = z1 - z0 + 1
        opaque = np.zeros((nx, ny, nz), dtype=bool)
        leafy = np.zeros((nx, ny, nz), dtype=bool)
        for (x, y, z), sid in w.blocks.items():
            if x0 <= x <= x1 and y0 <= y <= y1:
                bid = w._states[sid][0]
                if bid.endswith("_leaves"):
                    leafy[x - x0, y - y0, z - z0] = True
                elif w.is_full_cube(x, y, z):
                    opaque[x - x0, y - y0, z - z0] = True
        for x in range(x0, x1 + 1):                             # the terrain is a shell: nothing is lit below it
            for y in range(y0, y1 + 1):
                g = ground(x, y)
                if g is not None and g - 1 - z0 >= 0:
                    opaque[x - x0, y - y0, :g - z0] = True
        level = np.zeros((nx, ny, nz), dtype=np.int8)
        blocked = opaque | leafy
        open_above = np.logical_not(np.logical_or.accumulate(blocked[:, :, ::-1], axis=2)[:, :, ::-1])
        level[open_above] = 15
        clear = np.logical_not(opaque)
        for lv in range(14, 0, -1):
            src = level == lv + 1
            if not src.any():
                break
            spread = np.zeros_like(src)
            spread[1:, :, :] |= src[:-1, :, :]
            spread[:-1, :, :] |= src[1:, :, :]
            spread[:, 1:, :] |= src[:, :-1, :]
            spread[:, :-1, :] |= src[:, 1:, :]
            spread[:, :, 1:] |= src[:, :, :-1]
            spread[:, :, :-1] |= src[:, :, 1:]
            spread &= clear & (level < lv)
            level[spread] = lv
        dark = np.argwhere(clear & (level < 15))
        for i, j, k in dark:
            c = (int(i) + x0, int(j) + y0, int(k) + z0)
            self.light[c] = int(level[i, j, k])
            self.columns.add((c[0], c[1]))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):   # the blocks beside a dark cell have a dark face
                self.columns.add((c[0] + dx, c[1] + dy))
        self._cache.clear()
        return len(dark)

    def level_at(self, x, y, z):
        """Sky light 0..15 of the cell that holds the point (x, y, z)."""
        return self.light.get((int(math.floor(x)), int(math.floor(y)), int(math.floor(z))), 15)

    # -- what World.build gets
    @staticmethod
    def _step(level):
        """The level a cell is drawn with: every level down to 11 (one block of shade is one step, as soft as flat
        faces get), pairs below (9, 7, 5), nothing darker than LIGHT_FLOOR."""
        if level >= 11:
            return min(level, 15)
        return max(LIGHT_FLOOR, level - 1 + (level % 2))

    def state_at(self, pos):
        st = self._inner(pos)
        if st is None or (pos[0], pos[1]) not in self.columns:
            return st
        x, y, z = pos
        light = self.light
        levels = tuple(self._step(light.get((x + o[0], y + o[1], z + o[2]), 15)) for _d, o in self._offsets)
        own = self._step(light.get(pos, 15))
        share = self.share.get((x, y), 0)
        if not share and own == 15 and min(levels) == 15:
            return st
        key = (id(st), share, levels, own)
        hit = self._cache.get(key)
        if hit is None:
            hit = self._cache[key] = self._relit(st, share, dict(zip((d for d, _o in self._offsets), levels)), own)
        return hit

    def _relit(self, st, share, by_dir, own):
        kind = 0 if st.block_id in self._kinds[0] else (1 if st.block_id in self._kinds[1] else None)
        out = _LitState()
        out.cover, out.block_id = st.cover, st.block_id
        out.quads = []
        for pts, uvs, key, cull, off, mask in st.quads:
            tex, tint, ov, ov_tint, shade = key
            f = lightmap(by_dir[cull] if cull is not None else own, self.gamma)
            if kind is not None and share:
                if tint is not None:
                    tint = self.color(kind, share)
                if ov_tint is not None:
                    ov_tint = self.color(kind, share)
            if f < 0.999:
                base = tint if tint is not None else (255, 255, 255)
                tint = tuple(int(round(c * f)) for c in base)
                if ov is not None:
                    ob = ov_tint if ov_tint is not None else (255, 255, 255)
                    ov_tint = tuple(int(round(c * f)) for c in ob)
            out.quads.append((pts, uvs, (tex, tint, ov, ov_tint, shade), cull, off, mask))
        return out


def env(b):
    """The Environment (biome colours, baked sky light) of the builder's World, made on first use."""
    e = getattr(b.w, "sets_environment", None)
    if e is None:
        e = b.w.sets_environment = Environment(b.w)
    return e


# ---- the dark forest -------------------------------------------------------------------------------------------

def _noise(x, seed, pitch):
    """Smooth 1D value noise in -1..1 (hashed lattice)."""
    from .blocks import pos_hash

    g = x / pitch
    i = int(math.floor(g))
    f = g - i
    f = f * f * (3 - 2 * f)
    a = (pos_hash(i, seed, 5, 91) & 0xFFFF) / 32767.5 - 1.0
    c = (pos_hash(i + 1, seed, 5, 91) & 0xFFFF) / 32767.5 - 1.0
    return a * (1 - f) + c * f


def dark_forest(b, gap=(0.5, 58), half_width=26, depth=22, rows=4, name="forest", spacing=6.0, bay=4.0,
                climb=4, corridor=6, oaks=7, trail_from=45, mushrooms=6, biome=True, shade=True, side_bay=11,
                keep_clear=(), brightness=LIGHT_GAMMA):
    """THE WOODS: a dark oak forest edge across the far end of the meadow (see the module docstring).

    gap         (x, y): the middle of the 3-block gap between two trunks, on the tree line. The trunks beside it
                stand at y .. y + 1; a figure at <name>_gap stands just in front of them.
    half_width  the wall reaches this far to either side of the gap; depth = how far it goes back; rows = rows of
                trees (the first is the tree line), `spacing` blocks apart along a row (canopies are 8 wide).
    bay         the tree line curves toward the village by this many blocks at its two ends (the road runs into a
                bay of the forest, and the wall fills more of a frame).
    climb       the forest floor rises this many blocks more than the meadow would between the second row and the
                back: a low camera then sees shaded ground between the trunks, not the sky behind the wood.
    corridor    level blocks behind the gap where a figure walks out of sight.
    keep_clear  [(x, y, radius), ...]: no edge oak is planted within these circles (other set pieces' backgrounds).
    oaks        plain oaks along the edge; trail_from = y from which a thin dirt trail leads to the gap (None: no
                trail); mushrooms = small brown / red mushrooms on the dark floor.
    side_bay    this many columns west of the road, the 8 rows in front of the tree line carry no plants: a camera
                that films the gap from the side at child height stands there (a tuft before the lens hides it all).
    biome       the wood's columns are dark forest biome: darker grass, greener leaves, blended over 5x5 columns.
    shade       bake the game's sky light into the wood's blocks (see Environment): THIS is what makes it a black
                wall; without it the look's shadowless fill light keeps the inside as bright as the meadow.
                Call dark_forest AFTER any other piece that stands in or right beside the wood.
    brightness  the game's Brightness option for that baked light: 0.5 = the default, 0.0 = "Moody" (darker trunks
                and floor, harder steps of light on the grass), 1.0 = "Bright"."""
    w, v = b.w, b.v
    rng = b.rng_for(name)
    gx, fy = float(gap[0]), int(gap[1])
    gcx = int(math.floor(gx))                                   # the gap's middle column
    seed = int(rng.integers(0, 1 << 20))
    count0 = len(w.blocks)

    def front(x):                                               # y of the tree line at x
        t = min(1.0, abs(x - gx) / float(half_width))
        wob = _noise(x, seed, 9.0) * 1.6 * min(1.0, abs(x - gx) / 6.0)
        return fy - bay * t * t + wob

    x0, x1 = int(gx - half_width - 8), int(gx + half_width + 8)
    y0, y1 = fy - int(bay) - 4, fy + depth + 3

    def inside(x, y, margin=0.0):                               # the wood itself (trunks stand in here)
        return abs(x - gx) <= half_width + margin and front(x) - margin <= y <= fy + depth + margin

    # 1. ground: terrain where the disc ends, the corridor level with the road, the floor climbing to the back
    b.extend_terrain(x0, y0, x1, y1, plants=False, where=lambda x, y: inside(x, y, 6.0))
    road_z = b.ground(gcx, fy - 2)
    for t in list(b.trees):                                     # the meadow's own oaks that stand in the wood go
        if t["kind"] == "oak" and inside(t["x"], t["y"], 1.0) and t["where"] != name:
            remove_tree(b, t)
    target = {}
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            h = b.ground(x, y)
            if h is None or not inside(x, y, 6.0):
                continue
            fr = front(x)
            flank = min(1.0, max(0.0, (half_width + 5.0 - abs(x - gx)) / 7.0))
            back = (y - (fr + spacing)) / max(1.0, depth - spacing - 2.0)
            up = climb * min(1.0, max(0.0, back)) * flank + 0.45 * _noise(x * 1.7 + y * 0.6, seed + 3, 5.0)
            z = h + max(0, int(math.floor(up + 0.5)))
            if abs(x - gx) <= 2.6 and fr - 4 <= y <= fy + corridor + 1:
                z = road_z                                      # the way in: level with the road
            elif abs(x - gx) <= 4.6 and fr - 2 <= y <= fy + corridor + 2:
                z = min(z, road_z + 1)                          # ... between low banks
            if z != h:
                target[(x, y)] = z
    for (x, y), z in target.items():
        b.set_ground(x, y, z)

    # 2. where the trunks stand: the two at the gap, then outward along each row; odd rows are staggered
    spots = []
    row_step = (depth - 3.0) / max(1, rows - 1)
    for r in range(rows):
        xs = []
        if r == 0:
            xs = [gcx - 3, gcx + 2]                             # trunks at x -3..-2 and +2..+3: the gap is 3 wide
            for side in (-1, 1):
                x = xs[0] if side < 0 else xs[1]
                while True:
                    x += side * int(round(spacing + rng.uniform(-1.0, 1.2)))
                    if abs(x + 1 - gx) > half_width:
                        break
                    xs.append(x)
        else:
            x = gcx - half_width + (spacing / 2.0 if r % 2 else 0.0) + rng.uniform(-1.0, 1.0)
            while x <= gx + half_width - 1:
                xs.append(int(round(x)))
                x += spacing + rng.uniform(-1.0, 1.2)
        for x in xs:
            y = int(round(front(x + 1.0) + r * row_step + (rng.uniform(-1.0, 1.0) if r else 0.0)))
            if r == 0 and x in (gcx - 3, gcx + 2):
                y = fy
            spots.append((r, x, y))
    behind = (gcx - 1, fy + corridor + 1)                       # one trunk closes the corridor's far end
    spots = [s for s in spots if not (s[0] > 0 and abs(s[1] + 1 - gx) < 4.5 and s[2] <= fy + corridor + 1)]
    spots.append((1, behind[0], behind[1]))
    # thin the two ends so the wood frays out, and keep trunks from standing in each other
    trees, taken = [], []
    oak_spots = []
    for r, x, y in sorted(spots, key=lambda s: (s[0], abs(s[1] - gx))):
        if b.ground(x, y) is None or b.ground(x + 1, y + 1) is None:
            continue
        if any(abs(x - a) < 4 and abs(y - c) < 4 for a, c in taken):
            continue
        end = (abs(x + 1 - gx) - (half_width - 7.0)) / 7.0      # 0 .. 1 over the last 7 blocks of each end
        is_gap = r == 0 and x in (gcx - 3, gcx + 2)
        roll = rng.random()
        if not is_gap and (x, y) != behind and end > 0 and roll < 0.55 * end:
            oak_spots.append((x, y))                            # an end of the wood: maybe a plain oak instead
            continue
        height, accept = None, None
        if is_gap:
            height = 7 + int(rng.integers(0, 2))                # the two at the gap: tall enough for a clear arch,
            side = -1 if x < gx else 1                          # and no top bent away from the gap or toward the
            accept = lambda sh, side=side: sh["bend"][0] * side <= 0 and sh["bend"][1] >= 0   # meadow: a closed roof
        elif (x, y) == behind:
            accept = lambda sh: sh["bend"][1] <= 0              # ... nor this one's away from the corridor
        t = plant_dark_oak(b, x, y, rng, height, name, accept)
        if t is not None:
            t["row"] = r
            trees.append(t)
            taken.append((x, y))

    # 3. plain oaks along the edge and at the ends (the dark forest's own mix has them)
    edge_oaks = []
    tries = [(int(gx + s * (half_width * f) + rng.integers(-2, 3)), None) for f in (0.45, 0.95, 0.7, 1.08, 0.58, 0.83)
             for s in (-1, 1)]
    tries += [(x, y) for x, y in oak_spots]
    for x, y in tries:
        if len(edge_oaks) >= oaks:
            break
        if y is None:
            y = int(round(front(x))) - int(rng.integers(3, 6))  # a few blocks out in front of the tree line
        if abs(x - gx) < 9 or b.ground(x, y) is None or (x, y) in b.path_cells:
            continue
        if any(abs(x - a) < 3 and abs(y - c) < 3 for a, c in taken) or any(
                abs(x - t["x"]) < 7 and abs(y - t["y"]) < 7 for t in b.trees if t["kind"] == "oak"):
            continue
        if any(math.hypot(x - c[0], y - c[1]) < c[2] for c in keep_clear):
            continue
        if any(w.get(x, y, b.ground(x, y) + k) is not None for k in range(0, 4)):
            continue                                            # under a dark oak's low branch
        t = plant_oak(b, x, y, rng, None, name)
        if t is not None:
            edge_oaks.append(t)
            taken.append((x, y))

    # 4. what grows: thick tufts and tall grass in front of the tree line, little in the shade, a few mushrooms
    lane = (gcx - 3, gcx + 3)                                   # the road and the camera lane beside it stay bare
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            h = b.ground(x, y)
            if h is None or not inside(x, y, 4.0):
                continue
            b.clear_plants(x, y)
            r1, r2 = rng.random(), rng.random()
            if (x, y) in b.reserved or w.block_id(x, y, h - 1) != "grass_block" or w.get(x, y, h) is not None:
                continue
            if lane[0] <= x <= lane[1] and y <= fy + corridor + 1:
                continue
            if gcx - side_bay <= x < lane[0] and fy - 8 <= y <= fy - 1:
                continue                                        # the side camera's bay west of the road: bare grass
            d = y - front(x)                                    # < 0: in front of the wood
            ends = abs(x - gx) - half_width                     # > 0: beyond its ends
            if -3.5 <= d < 1.0 or 0.0 <= ends <= 3.5:
                if r1 < 0.34:
                    w.set(x, y, h, "short_grass")
                elif r1 < 0.52 and w.get(x, y, h + 1) is None:
                    w.set(x, y, h, "tall_grass", {"half": "lower"})
                    w.set(x, y, h + 1, "tall_grass", {"half": "upper"})
                elif r1 < 0.56:
                    w.set(x, y, h, ("poppy", "dandelion", "oxeye_daisy", "cornflower")[int(r2 * 4)])
            elif d >= 1.0 and ends < 0.0:
                if r1 < 0.07:
                    w.set(x, y, h, "short_grass")
            else:
                b.sow(x, y, rng)
    shrooms = []
    for _ in range(mushrooms * 30):
        if len(shrooms) >= mushrooms:
            break
        x = int(gx + rng.integers(-half_width + 3, half_width - 2))
        y = int(front(x) + rng.integers(2, max(3, depth - 4)))
        h = b.ground(x, y)
        if h is None or (x, y) in b.reserved or w.get(x, y, h) is not None or w.block_id(x, y, h - 1) != "grass_block":
            continue
        if abs(x - gx) <= 2.6 and y <= fy + corridor + 1:
            continue
        w.set(x, y, h, "brown_mushroom" if rng.random() < 0.6 else "red_mushroom")
        shrooms.append((x, y, h))

    # 5. the trail: the village road thins out in the meadow; a worn line of dirt_path carries it to the gap
    trail = []
    if trail_from is not None:
        for y in range(int(trail_from), fy + corridor + 1):
            near = min(1.0, max(0.0, (y - trail_from) / max(1.0, fy - trail_from)))
            for x, p in ((gcx, 0.55 + 0.35 * near), (gcx - 1, 0.10 + 0.15 * near), (gcx + 1, 0.12 + 0.15 * near)):
                if rng.random() < p and w.block_id(x, y, b.ground(x, y) - 1) == "grass_block" \
                        and w.get(x, y, b.ground(x, y)) is None:
                    b.pave(x, y)
                    trail.append((x, y))
        for y in range(int(trail_from), fy + corridor + 2):     # nothing grows in the way
            for x in range(gcx - 1, gcx + 2):
                b.clear_plants(x, y)
                b.reserved.add((x, y))

    # 6. what the director needs
    zg = b.walk_z(gx, fy - 0.6)
    stand = b.anchor(name + "_gap", (gx, fy - 0.4), yaw_to((gx, fy), (gx, fy - 30.0)), replace=True)
    deep = b.anchor(name + "_deep", (gx, fy + corridor - 0.5), yaw_to((gx, fy), (gx, fy + 30.0)), replace=True)
    hide = (gcx + 3.0, fy + 3.3)                                # right behind the east trunk of the gap (x +2..+3):
    inner = b.anchor(name + "_gap_in", hide, yaw_to((gx, fy), (gx, fy + 30.0)), replace=True)   # hidden from the road
    approach = b.anchor(name + "_approach", (gx, fy - 3.5), yaw_to((gx, fy), (gx, fy + 30.0)), replace=True)
    cam_in = (gx + 0.3, fy + corridor - 1.0, road_z + 1.5)       # inside, at eye height, looking out along the corridor
    v.anchors[name + "_inside_cam"] = cam_in
    start = v.anchors.get("exit_gate", (0.5, 24.5, 0.0))
    mids = [(0.6, 31.0), (0.4, 38.0), (gx, 46.0), (gx, 52.0), (gx, fy - 3.5), (gx, fy - 0.4), (gx, fy + 2.4), hide]
    road = b.path("road_to_" + name, [(start[0], start[1])] + [p for p in mids if p[1] > start[1] + 1.0], replace=True)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if inside(x, y, 1.0):
                b.reserved.add((x, y))
    dark_cells = 0
    if biome or shade:
        e = env(b)
        if biome:
            e.set_biome([(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
                         if inside(x, y, 1.0) and b.ground(x, y) is not None])
        if shade:
            e.gamma = float(brightness)
            dark_cells = e.bake_sky_light(b.ground, x0 - 2, y0 - 2, x1 + 2, y1 + 2)
    logs = sum(len(t["logs"]) for t in trees)
    leaves = sum(len(t["leaves"]) for t in trees)
    res = dict(name=name, gap=stand, gap_in=inner, deep=deep, approach=approach, inside_cam=cam_in,
               gap_cells=(gcx - 1, gcx + 1),
               tree_line=fy, road_z=road_z, zg=zg, trees=trees, oaks=edge_oaks, mushrooms=shrooms, trail=trail,
               path=road, bounds=(x0, y0, x1, y1), half_width=half_width, depth=depth,
               top=max(max(c[2] for c in t["leaves"] + t["logs"]) for t in trees) + 1,
               counts=dict(dark_oaks=len(trees), oaks=len(edge_oaks), logs=logs, leaves=leaves,
                           blocks_added=len(w.blocks) - count0, dark_cells=dark_cells))
    v.sets[name] = res
    return res


# ---- "The Hello" -----------------------------------------------------------------------------------------------

HELLO = dict(
    forest_gap=(0.5, 58),                 # the tree line: 33.5 blocks beyond exit_gate (0.5, 24.5)
    floating=(-13, 47),                   # the meadow's own lone oak west of the road
    bare=((17, 44), (20, 46), (17, 48)),  # three new oaks on the east bank ...
    pyramid=(12, 45),                     # ... and the pyramid in front of them as seen from the road
)


def hello_set(b, layout=None, forest=None):
    """Everything "The Hello" films beyond the exit gate, placed along the meadow road (see HELLO for where):
    the dark forest across the end of the road (beats 6-8), the floating oak west of the road against the open
    western sky (beat 12), three bare oaks on the east bank and the sand pyramid in front of them as seen from the
    road (beats 13, 14). The three small pieces stand 10 blocks or more off the road, outside a 28-35 mm frame from
    the exit gate: beat 6 happens before any of them exists. Returns dict(forest, floating, bare, pyramid, cameras,
    path); also Village.sets['hello']."""
    L = dict(HELLO)
    L.update(layout or {})
    bx = sum(p[0] for p in L["bare"]) / float(len(L["bare"]))
    by = sum(p[1] for p in L["bare"]) / float(len(L["bare"]))
    kw = dict(keep_clear=[(L["floating"][0], L["floating"][1], 13.0), (L["pyramid"][0], L["pyramid"][1], 12.0),
                          (bx, by, 13.0)])
    kw.update(forest or {})
    forest = dark_forest(b, gap=L["forest_gap"], **kw)
    floating = floating_oak(b, b.tree_at(*L["floating"], radius=1.5) or L["floating"])
    bare = bare_oaks(b, L["bare"])
    pyramid = sand_pyramid(b, L["pyramid"])
    res = dict(forest=forest, floating=floating, bare=bare, pyramid=pyramid, path="road_to_forest", layout=L)
    res["cameras"] = hello_cameras(res)
    for key in ("floating", "bare", "pyramid"):            # the ground between each of these cameras and its subject
        c = res["cameras"][key]                            # carries no plants
        clear_view(b, c["pos"], c["target"], 2.2)
    b.v.sets["hello"] = res
    return res


def hello_cameras(res):
    """The framings the proof stills were made with: name -> dict(pos, target, lens, fstop). A start, not a rule."""
    gap = res["forest"]["gap"]
    fl = res["floating"]
    py = res["pyramid"]
    ba = res["bare"]
    cams = {
        # beats 6 and 7: low on the road two blocks inside the exit gate, the forest wall across the end
        "gate": dict(pos=(0.9, 22.6, 0.75), target=(gap[0], gap[1], 2.6), lens=32.0, fstop=4.0),
        # beat 8: from the side on the road, at child height, the tree line running away to the right
        "side": dict(pos=(gap[0] - 8.6, gap[1] - 2.6, 0.7), target=(gap[0], gap[1] - 1.4, 1.0), lens=35.0,
                     fstop=2.8),
        # from inside the forest, out along the corridor to the meadow and the village
        "inside": dict(pos=res["forest"]["inside_cam"], target=(gap[0] - 0.1, gap[1] - 14.0, 0.9), lens=26.0,
                       fstop=4.0),
        # beat 12: low, from the east-north-east (the forest behind the camera), the canopy against the western sky
        "floating": dict(pos=(fl["under"][0] + 4.6, fl["under"][1] + 1.4, 0.35),
                         target=(fl["under"][0] - 0.2, fl["under"][1] - 0.1, fl["leaf_bottom"] - 0.5), lens=22.0,
                         fstop=4.0),
        # beat 13: from north of the bare oaks, the village roofs beyond
        "bare": dict(pos=(ba["among"][0] + 2.6, ba["among"][1] + 8.6, ba["among"][2] + 1.0),
                     target=(ba["among"][0] - 0.1, ba["among"][1], ba["among"][2] + 2.5), lens=30.0, fstop=4.0),
        # beat 14: from the road side, the pyramid with the bare trunks behind it
        "pyramid": dict(pos=(py["top"][0] - 10.6, py["top"][1] - 2.6, 0.8),
                        target=(py["top"][0] - 0.2, py["top"][1] - 0.4, 2.1), lens=35.0, fstop=4.0),
    }
    return cams


# ---- self-test -------------------------------------------------------------------------------------------------

def _check_shapes():
    """The shapes against the rules read from the classes. Returns a list of failures."""
    bad = []
    rng = np.random.default_rng(7)
    heights, tops, caps, branches, bends = set(), set(), 0, [], set()
    n = 400
    for _ in range(n):
        s = dark_oak_shape(rng)
        h = s["height"]
        heights.add(h)
        logs, leaves = set(s["logs"]), set(s["leaves"])
        if logs & leaves:
            bad.append("dark oak: a leaf in a log")
        base = {c for c in logs if c[2] == 0}
        if base != {(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)}:
            bad.append("dark oak: the trunk does not start as a 2x2 at the origin: %s" % sorted(base))
        if max(c[2] for c in logs) != h - 1:
            bad.append("dark oak: top log not at height - 1")
        bx, by = s["bend"]
        bends.add((bx, by))
        if abs(bx) + abs(by) > 2 or (bx and by):
            bad.append("dark oak: bend %s" % ((bx, by),))
        top = h - 1
        mid = [c for c in leaves if c[2] == top]
        # the 8x8 row of the main canopy, without its 9 corner cells, minus the 4 top logs, plus branch canopies
        main = {(bx + dx, by + 1 - dz) for dx in range(-3, 5) for dz in range(-3, 5)
                if not ((dx == -3 or dx >= 3) and (dz == -3 or dz >= 3))}
        if len(main) != 64 - 9:
            bad.append("dark oak: main row has %d cells" % len(main))
        if not {(c[0], c[1]) for c in mid} >= {m for m in main if (m[0], m[1], top) not in logs}:
            bad.append("dark oak: the 8x8 canopy row is incomplete")
        caps += s["cap"]
        branches.append(s["branches"])
        tops.add(max(c[2] for c in leaves) - top)
        if min(c[2] for c in leaves) != top - 1:
            bad.append("dark oak: lowest leaves not one below the top log")
    if heights != {6, 7, 8, 9}:
        bad.append("dark oak heights %s (the game: 6..9)" % sorted(heights))
    if tops != {1, 2}:
        bad.append("dark oak canopy tops %s above the top log (the game: 1 or, with the cap, 2)" % sorted(tops))
    if not 0.40 < caps / float(n) < 0.60:
        bad.append("dark oak cap share %.2f (the game: 1/2)" % (caps / float(n)))
    mean_br = sum(branches) / float(n)
    if not 3.5 < mean_br < 4.5:
        bad.append("dark oak branches %.2f per tree (the game: 12 cells x 1/3 = 4)" % mean_br)
    oh = set()
    for _ in range(200):
        s = oak_shape(rng)
        h = s["height"]
        oh.add(h)
        per = {}
        for c in s["leaves"]:
            per.setdefault(c[2] - h, []).append(c)
        if sorted(per) != [-3, -2, -1, 0]:
            bad.append("oak: leaf rows %s" % sorted(per))
        if len(per[0]) != 5 or not 20 <= len(per[-3]) <= 24 or not 4 <= len(per[-1]) <= 8:
            bad.append("oak: row sizes %s" % {k: len(c) for k, c in per.items()})
    if oh != {4, 5, 6}:
        bad.append("oak heights %s (the game: 4..6)" % sorted(oh))
    print("[sets] shapes: %d dark oaks (heights %s, %.2f branches, cap %.0f %%, bends %d kinds), 200 oaks (heights %s): %s"
          % (n, sorted(heights), mean_br, 100.0 * caps / n, len(bends), sorted(oh), "OK" if not bad else "FAILED"))
    return bad


def _check_set():
    """Build the village with hello_set and check what a director relies on. Returns a list of failures."""
    import time

    from . import quick, village

    bad = []
    t0 = time.time()
    scene = quick.reset()
    quick.setup(scene)
    plain = village.build_village(scene, seed=1)
    faces0, blocks0 = plain.face_count, len(plain.world.blocks)
    scene = quick.reset()
    quick.setup(scene)
    out = {}
    v = village.build_village(scene, seed=1, edit=lambda b: out.update(hello=hello_set(b), b=b))
    h, b, w, A = out["hello"], out["b"], v.world, v.anchors
    print("[sets] village %d blocks / %d faces (%d triangles); with hello_set %d blocks / %d faces (%d triangles), "
          "built in %.1f s" % (blocks0, faces0, 2 * faces0, len(w.blocks), v.face_count, 2 * v.face_count,
                               time.time() - t0))
    f = h["forest"]
    print("[sets] forest:", f["counts"], "top z %d, tree line y %d, gap columns x %d..%d" % (
        f["top"], f["tree_line"], f["gap_cells"][0], f["gap_cells"][1]))
    if v.edit_problems:
        bad.append("edit problems: %s" % v.edit_problems)
    for name in ("forest_gap", "forest_gap_in", "forest_deep", "forest_approach", "forest_inside_cam", "floating_oak_under",
                 "floating_oak_target", "bare_oaks_among", "bare_oaks_center", "pyramid_beside", "pyramid_target"):
        if name not in A:
            bad.append("missing anchor " + name)
    for name in ("road_to_forest", "pyramid_round"):
        if name not in v.paths:
            bad.append("missing path " + name)
        elif v.path_clear(v.paths[name]):
            bad.append("path %s blocked: %s" % (name, v.path_clear(v.paths[name])[:2]))
    # the gap: three clear columns between two dark oak trunks, a level corridor behind
    gx0, gx1 = f["gap_cells"]
    fy, z = f["tree_line"], f["road_z"]
    for x in range(gx0, gx1 + 1):
        for y in range(fy - 3, fy + 6):
            if b.ground(x, y) != z:
                bad.append("corridor not level at %s" % ((x, y),))
            if any(w.is_solid(x, y, z + k) for k in (0, 1)):
                bad.append("corridor blocked at %s" % ((x, y),))
    for x in (gx0 - 1, gx1 + 1):                           # the trunks stand on the low banks beside the way in
        logs = [k for k in range(0, 8) if w.block_id(x, fy, z + k) == "dark_oak_log"]
        if len(logs) < 4 or logs[0] > 1:               # (the top of a dark oak may bend sideways from layer 4 on)
            bad.append("no dark oak trunk beside the gap at x %d (%s)" % (x, logs))
    # forest_gap_in is hidden behind the east trunk from anywhere on the road and the camera lane beside it
    gi = A["forest_gap_in"]
    for cx in (-2.5, 0.5, 0.9, 3.0):
        n, hit = 400, False
        for i in range(1, n):
            px, py = cx + (gi[0] - cx) * i / n, 22.6 + (gi[1] - 22.6) * i / n
            if w.block_id(int(math.floor(px)), int(math.floor(py)), int(gi[2] + 1.0)) == "dark_oak_log":
                hit = True
        if not hit:
            bad.append("forest_gap_in is in view from x %.1f on the road" % cx)
    # the canopy closes over the gap and the corridor (it must be dark in there)
    roof = sum(1 for x in range(gx0, gx1 + 1) for y in range(fy, fy + 6)
               if any((w.block_id(x, y, z + k) or "").endswith("_leaves") for k in range(3, 14)))
    if roof < 15:
        bad.append("only %d of 18 corridor columns are under leaves" % roof)
    # the game's sky light, baked: full in the meadow, falling off under the canopy, darkest deep inside
    e = env(b)
    lv = {k: e.level_at(*p) for k, p in (("meadow", (gx0 + 1.5, fy - 12.5, z + 0.5)), ("gap", (gx0 + 1.5, fy - 0.4, z + 0.5)),
                                         ("corridor", (gx0 + 1.5, fy + 4.5, z + 0.5)),
                                         ("deep", (gx0 - 8.5, fy + 12.5, b.ground(gx0 - 9, fy + 12) + 0.5)))}
    print("[sets] sky light: %s -> brightness %s" % (lv, {k: round(lightmap(n), 2) for k, n in lv.items()}))
    if not (lv["meadow"] == 15 and 11 <= lv["gap"] <= 14 and lv["corridor"] <= 11 and lv["deep"] <= 9):   # noqa
        bad.append("sky light levels %s" % lv)
    if [round(lightmap(n), 2) for n in (15, 13, 11, 9, 7, 5, 3, 0)] != [1.0, 0.8, 0.64, 0.5, 0.36, 0.24, 0.14, 0.0]:
        bad.append("lightmap curve %s" % [round(lightmap(n), 2) for n in (15, 13, 11, 9, 7, 5, 3, 0)])
    if dark_forest_colors() != ((80, 122, 50), (89, 174, 48)):
        bad.append("dark forest colours %s" % (dark_forest_colors(),))
    # floating oak: `air` clear blocks under the canopy, `logs` logs hanging, nothing else of the trunk
    fl = h["floating"]
    t = fl["tree"]
    col = [w.block_id(t["x"], t["y"], t["base"] + k) for k in range(t["height"] + 1)]
    want = [None] * (t["height"] - fl["logs"]) + ["oak_log"] * fl["logs"] + ["oak_leaves"]
    if col != want:
        bad.append("floating oak column %s, expected %s" % (col, want))
    low = min(c[2] for c in t["leaves"]) - t["base"]
    if low != fl["air"]:
        bad.append("floating oak: %d clear blocks under the canopy, expected %d" % (low, fl["air"]))
    # bare oaks: logs only
    for t in h["bare"]["trees"]:
        near = [c for c in w.blocks if abs(c[0] - t["x"]) <= 2 and abs(c[1] - t["y"]) <= 2
                and c[2] >= t["base"] and w.block_id(*c).endswith("_leaves")]
        if near or t["leaves"]:
            bad.append("bare oak at %s still has %d leaves" % ((t["x"], t["y"]), len(near)))
        if [w.block_id(t["x"], t["y"], t["base"] + k) for k in range(t["height"])] != ["oak_log"] * t["height"]:
            bad.append("bare oak at %s has lost logs" % ((t["x"], t["y"]),))
    # pyramid: 25 + 9 + 1 sand blocks on level ground
    py = h["pyramid"]
    per = {}
    for c in py["cells"]:
        per[c[2] - py["ground"]] = per.get(c[2] - py["ground"], 0) + (w.block_id(*c) == "sand")
    if per != {0: 25, 1: 9, 2: 1}:
        bad.append("pyramid layers %s" % per)
    # the pieces beside the road are out of a 28 mm frame from the exit gate (half angle 19.9 degrees)
    gate = A["exit_gate"]
    for label, (x, y) in (("floating oak", (fl["under"][0], fl["under"][1])), ("pyramid", (py["top"][0], py["top"][1])),
                          ("bare oaks", (h["bare"]["among"][0], h["bare"]["among"][1]))):
        ang = math.degrees(math.atan2(abs(x - gate[0]) - 2.5, y - gate[1]))
        if ang < 19.9:
            bad.append("%s is %.1f degrees off the road axis from the exit gate: inside a 28 mm frame" % (label, ang))
    probs = v.validate()
    if probs:
        bad.append("validate: %s" % probs)
    print("[sets] hello_set: anchors %s" % {k: tuple(round(a, 2) for a in A[k]) for k in sorted(A) if k.startswith(
        ("forest", "floating", "bare", "pyramid"))})
    print("[sets] hello_set: %s" % ("OK" if not bad else "FAILED"))
    return bad


def _selftest(names):
    """Numbers (no names) or proof stills (names of films/_sets_proof.py PROOF, or 'all')."""
    if names:
        from films import _sets_proof

        return _sets_proof.main(names)
    bad = _check_shapes() + _check_set()
    for line in bad:
        print("FAIL", line)
    print("[sets] self-test: %s" % ("all passed" if not bad else "%d FAILED" % len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    import sys

    sys.exit(_selftest(sys.argv[1:]))
