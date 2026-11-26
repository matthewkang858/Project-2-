"""THE IRON FARM TOWER of "Twenty Minutes" (film three, stories/ironfarm.json). DOCSTRING IS REWRITTEN AT THE END."""
import math

import numpy as np

from . import characters as ch
from .village import yaw_of, yaw_to

FPS = 24
TICK = FPS / 20.0                    # film frames per game tick

# ---- numbers from the game (Java Edition 26.x client classes and data files, named next to each) -------------------
GOLEM_SPAWN_TRIES = 10               # Villager.spawnGolemIfNeeded -> SpawnUtil.trySpawnMob(IRON_GOLEM, MOB_SUMMONED,
GOLEM_SPAWN_XZ = 8                   #   level, villager.blockPosition(), 10, 8, 6, Strategy.LEGACY_IRON_GOLEM, false):
GOLEM_SPAWN_Y = 6                    #   10 tries, x and z +-8 around the villager, each column scanned from y+6 down to y-6
GOLEM_SPAWN_VILLAGERS = 3            # VillagerPanicTrigger.tick: every 100 game ticks spawnGolemIfNeeded(level, t, 3):
GOLEM_SPAWN_EVERY_TICKS = 100        #   at least 3 villagers in the box inflated by 10 that want a golem
GOLEM_SPAWN_BOX = 10.0
GOLEM_SENSOR_TICKS = 200             # GolemSensor: senses every 200 ticks (golems within its 16-block list) ...
GOLEM_DETECTED_TICKS = 599           # ... and sets GOLEM_DETECTED_RECENTLY with an expiry of 599 ticks
SLEPT_WITHIN_TICKS = 24000           # Villager.golemSpawnConditionsMet: LAST_SLEPT less than 24000 ticks ago (beds!)
GOLEM_HEADROOM = 3                   # IronGolem.checkSpawnObstruction: the feet cell (water allowed: it is checked with
#                                      Fluids.EMPTY) and the two cells above it (no fluid, no full collision block)
NO_GOLEM_ON = ("cobweb", "cactus", "glass_pane", "conduit", "ice", "tnt", "glowstone", "beacon", "sea_lantern",
               "frosted_ice", "tinted_glass", "glass")    # SpawnUtil.Strategy.LEGACY_IRON_GOLEM (+ every stained glass
NO_GOLEM_ON_SUFFIX = ("_stained_glass", "_stained_glass_pane", "_leaves")   # block or pane, and LeavesBlock)
ZOMBIE_SCARE = 8.0                   # VillagerHostilesSensor: ZOMBIE 8.0 blocks (and line of sight: glass blocks it)
GOLEM_LOOT = (("iron_ingot", 3, 5), ("poppy", 0, 2))      # loot_table/entities/iron_golem.json: two pools, uniform
GOLEM_SIZE = (1.4, 2.7)              # EntityType.IRON_GOLEM
GOLEM_HEALTH = 100.0                 # IronGolem.createAttributes MAX_HEALTH
LAVA_DAMAGE = 4.0                    # Entity.lavaHurt: hurtServer(lava, 4.0)
HURT_COOLDOWN_TICKS = 10             # LivingEntity: a second hit only lands 10 ticks after the first (invulnerableTime 20)
LAVA_DEATH_TICKS = int(math.ceil(GOLEM_HEALTH / LAVA_DAMAGE) - 1) * HURT_COOLDOWN_TICKS   # 240 ticks = 12 s in lava
JUMP = 0.42                          # LivingEntity.jumpFromGround (Attributes.JUMP_STRENGTH default)
GRAVITY = 0.08                       # LivingEntity default gravity
AIR_DRAG_V = 0.98                    # LivingEntity.travelInAir: vertical speed x 0.98 per tick
GROUND_FRICTION = 0.546              # block friction 0.6 x 0.91: horizontal speed kept per tick on the ground
PUSH = 0.05                          # Entity.push(Entity): 0.05 x the normalised offset (x sqrt of it under 1 block)
PLAYER_WALK = 4.317                  # blocks/s (engine.players WALK_SPEED): input that holds it against GROUND_FRICTION
BED_BOUNCE = 0.75                    # Blocks: every bed has bounceRestitution(0.75) (Entity.getBlockBounciness: living
#                                      entities keep it, anything else x 0.8)
BED_JUMPS = (3, 6)                   # JumpOnBed.MIN_JUMPS / MAX_JUMPS: a baby jumps 3..6 times ...
BED_JUMP_COOLDOWN_TICKS = 5          # ... with COOLDOWN_BETWEEN_JUMPS 5 ticks on the mattress between them
BED_TOP = 9.0 / 16.0                 # BedBlock: the bed's shape is 9 px high
BABY_TICKS = 24000                   # AgeableMob.BABY_START_AGE = -24000: a baby grows up after 20 minutes (no
#                                      particles: those only come with a forced age, i.e. feeding)
VILLAGER_HEIGHT, BABY_HEIGHT = 1.95, 0.975    # EntityType.VILLAGER 0.6 x 1.95, babies at scale 0.5
ZOMBIE_REACH = math.sqrt(2.04) - 0.6     # Mob.getAttackBoundingBox: the hit box inflated by this (0.83) sideways

# ---- the set (Blender block coordinates; see LAYOUT in the module docstring) --------------------------------------
AT = (-23, 18)                       # the pod's south-west INSIDE cell: the inside is AT .. AT + (4, 4)
FLOOR = 10                           # z of the pod's floor top (the pillar + floor are 10 blocks of stone)
LAVA_LEVEL = 8.0 / 9.0               # fixtures.FLUID_SOURCE_HEIGHT


# ----------------------------------------------------------------------------------------------------
# the layout as numbers (no Blender): every cell the set puts into the World
# ----------------------------------------------------------------------------------------------------
def layout(at=AT, floor=FLOOR, ground=0):
    """Every block of the tower as {cell: (block id, props)} plus the named cells and spots (pure numbers, no
    Blender): the source of truth for iron_farm() and for the self-test. Cells are Blender block cells."""
    X, Y = int(at[0]), int(at[1])
    F, g = int(floor), int(ground)
    if F - g < 8:
        raise ValueError("towers.layout: the floor must be at least 8 blocks above the ground (a golem may spawn "
                         "6 blocks below a villager): floor %d, ground %d" % (F, g))
    cells = {}

    def put(c, bid, props=None):
        cells[tuple(int(a) for a in c)] = (bid, dict(props or {}))

    def fill(x0, y0, z0, x1, y1, z1, bid, props=None):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    put((x, y, z), bid, props)

    def air(c):
        cells[tuple(int(a) for a in c)] = None

    # the pillar under the inside of the pod, and the floor (7 x 7, one block over the pillar on every side)
    fill(X, Y, g, X + 4, Y + 4, F - 2, "stone")
    fill(X - 1, Y - 1, F - 1, X + 5, Y + 5, F - 1, "stone")
    # the zombie cell: a 1 x 1, 2-high cobblestone alcove in the pod's east wall at row Y + 1, a stone slab roof;
    # it opens into the pod over a cobblestone block at foot level (the sill, on the pod's floor), open air at head
    # height: the zombie's arms reach out over the sill and stop in the air
    zc = (X + 5, Y + 1)
    for c in ((X + 5, Y), (X + 5, Y + 2), (X + 6, Y + 1)):
        fill(c[0], c[1], F, c[0], c[1], F + 1, "cobblestone")
    put((X + 6, Y + 1, F - 1), "stone")                                       # the back wall's footing
    for c in ((X + 5, Y), (X + 5, Y + 1), (X + 5, Y + 2), (X + 6, Y + 1)):
        put((c[0], c[1], F + 2), "stone_slab", {"type": "bottom", "waterlogged": "false"})
    put((X + 4, Y + 1, F), "cobblestone")                                     # the sill
    win = (X + 4, Y + 1)
    # the back-wall doorway: a cobblestone plug at head height over a one-block gap
    gap = (X + 4, Y + 5)
    put((gap[0], gap[1], F + 1), "cobblestone")
    # the golem platform west of the pod (water on it), its rims, the 2-wide kill slot at its outer (west) edge
    px0, px1, py0, py1 = X - 5, X - 2, Y - 1, Y + 5
    fill(px0, py0, F - 1, px1, py1, F - 1, "stone")
    for ry in (py0 - 1, py1 + 1):                                              # rims along the long sides
        fill(px0, ry, F - 1, px1, ry, F - 1, "stone")
        fill(px0, ry, F, px1, ry, F, "glass")
    sx0, sx1 = X - 7, X - 6                                                    # the slot: 4 deep below the rim
    fill(sx0, py0, F - 5, sx1, py1, F - 5, "stone")                            # its floor
    fill(X - 8, py0 - 1, F - 5, X - 8, py1 + 1, F - 1, "stone")                # its outer wall ...
    fill(X - 8, py0 - 1, F, X - 8, py1 + 1, F, "glass")                        # ... with a glass rim on top
    for ey in (py0 - 1, py1 + 1):                                              # its ends: glass, the glow shows
        fill(sx0, ey, F - 5, sx1, ey, F - 5, "stone")
        fill(sx0, ey, F - 4, sx1, ey, F, "glass")
    # the collection column under the slot's north-east corner: a 3 x 3 stone column, a 1 x 1 chute down its middle
    # from a hole in the slot floor, the hopper on the chest at its foot, open to the north (back) below a lintel
    chute = (sx1, py1)
    fill(chute[0] - 1, chute[1] - 1, g, chute[0] + 1, chute[1] + 1, F - 6, "stone")
    for z in range(g, F - 4):
        air((chute[0], chute[1], z))
    for z in range(g, g + 4):
        air((chute[0], chute[1] + 1, z))                                       # the niche's opening
    # the dirt staircase up the back: one up and one along, zigzagging (row Y+5 east to west against the pillar,
    # then back east in row Y+6 to the top step outside the gap); a few stray blocks at its foot
    steps = []
    n_low = F - 3 - g                                                          # steps in the lower flight
    for i in range(n_low):
        steps.append((X + 2 + (n_low - 1 - i), Y + 5, g + i))
    steps += [(X + 2, Y + 6, F - 3), (X + 3, Y + 6, F - 2), (X + 4, Y + 6, F - 1)]
    for c in steps:
        put(c, "dirt")
    top_step = steps[-1]
    rough = [(steps[2][0], Y + 6, steps[2][2]), (steps[-4][0] + 1, Y + 5, steps[-4][2] - 1)] if n_low >= 4 else []
    stray = [(steps[0][0] + 1, Y + 6, g), (steps[0][0] + 2, Y + 7, g), (steps[0][0] + 2, Y + 4, g),
             (steps[0][0] + 1, Y + 7, g)]
    for c in rough + stray:
        if c not in cells:
            put(c, "dirt")
    put((steps[0][0] + 1, Y + 7, g + 1), "dirt")                               # one left on top of another
    # inside: the lantern on the floor, the wall torch at the cell, the beds (pillows to the north wall)
    lantern = (X, Y, F)
    torch = (X + 4, Y + 2, F + 1)                                              # on the cell frame's west face
    beds = dict(white_1=(X, Y + 3, F), white_2=(X + 1, Y + 3, F), mom=(X + 2, Y + 3, F))
    bed2 = (X + 3, Y + 3, F)                                                   # the free space: the second red bed
    chest = (chute[0], chute[1], g)
    lava_cells = [(x, y, F - 2) for x in (sx0, sx1) for y in range(py0, py1 + 1)]
    return dict(cells=cells, X=X, Y=Y, F=F, g=g, window=(win[0], win[1], F + 1), sill=(win[0], win[1], F),
                cell=(zc[0], zc[1], F), gap=(gap[0], gap[1], F), plug=(gap[0], gap[1], F + 1),
                platform=(px0, py0, px1, py1), slot=(sx0, py0, sx1, py1), slot_floor=F - 4, rim=F,
                lava_cells=lava_cells, lava_z=F - 2 + LAVA_LEVEL, chute=(chute[0], chute[1]), chest=chest,
                hopper=(chest[0], chest[1], g + 1), chute_mouth=g + 4.0, steps=steps, top_step=top_step,
                stray=stray + rough, lantern=lantern, torch=torch, beds=beds, bed2=bed2,
                inside=(X, Y, F, X + 4, Y + 4, F + 1), pod=(X - 1, Y - 1, F, X + 5, Y + 5, F + 2),
                footprint=(X - 8, Y - 2, max(X + 7, steps[0][0] + 2), Y + 7))


# ----------------------------------------------------------------------------------------------------
# the game's golem spawn rule (Villager.spawnGolemIfNeeded / SpawnUtil / IronGolem.checkSpawnObstruction)
# ----------------------------------------------------------------------------------------------------
def _no_golem_on(bid):
    return bid in NO_GOLEM_ON or bid.endswith(NO_GOLEM_ON_SUFFIX)


def spawn_cell(world, x, y, villager_z, fluids=()):
    """Where a golem spawn attempt in column (x, y) for a villager standing at block height `villager_z` lands, by
    the game's rule, or None. SpawnUtil.moveToPossibleSpawnPosition scans down from villager_z + 6 to - 6 and takes
    the FIRST cell whose block below is solid and not glass / leaves / ice ... (LEGACY_IRON_GOLEM) and which itself
    holds air or a fluid; IronGolem.checkSpawnObstruction then wants something to stand on, no full block in that
    cell and no full block and no fluid in the two cells above it. fluids = extra fluid cells the World does not
    hold (a lava_glow). Returns the (x, y, z) cell the golem's feet are in."""
    fl = set(tuple(c) for c in fluids)

    def fluid(c):
        return c in fl or world.block_id(*c) in ("water", "lava")

    def empty_or_fluid(c):
        return world.block_id(*c) is None or fluid(c) or not world.is_solid(*c)

    def full(c):
        bid = world.block_id(*c)
        return bid is not None and (world.is_full_cube(*c) or bid == "glass" or bid.endswith("_glass"))

    z0 = int(villager_z)
    above = (x, y, z0 + GOLEM_SPAWN_Y)
    for z in range(z0 + GOLEM_SPAWN_Y - 1, z0 - GOLEM_SPAWN_Y - 2, -1):
        below = (x, y, z)
        bid = world.block_id(*below)
        ok_above = world.block_id(*above) is None or fluid(above)
        if bid is not None and world.is_solid(*below) and not _no_golem_on(bid) and ok_above:
            feet = above
            if full(feet):
                return None
            for k in (1, 2):
                c = (feet[0], feet[1], feet[2] + k)
                if full(c) or fluid(c) or (world.block_id(*c) is not None and world.is_solid(*c)):
                    return None
            return feet
        above = below
    return None


def spawn_cells(world, villagers, fluids=()):
    """Every cell where the game could put a golem for villagers standing at the block positions `villagers`
    [(x, y, z), ...]: the columns within +-8 of any of them, each scanned as spawn_cell() does. Returns a set."""
    out = set()
    for vx, vy, vz in villagers:
        for dx in range(-GOLEM_SPAWN_XZ, GOLEM_SPAWN_XZ + 1):
            for dy in range(-GOLEM_SPAWN_XZ, GOLEM_SPAWN_XZ + 1):
                c = spawn_cell(world, int(vx) + dx, int(vy) + dy, int(vz), fluids)
                if c is not None:
                    out.add(c)
    return out


def golem_loot(seed=0):
    """The drops of one iron golem by loot_table/entities/iron_golem.json: {'iron_ingot': 3..5, 'poppy': 0..2}
    (two pools, one roll each, set_count uniform, both ends included), drawn from `seed`."""
    rng = np.random.default_rng([int(seed), 7193])
    return {item: int(rng.integers(lo, hi + 1)) for item, lo, hi in GOLEM_LOOT}


# ----------------------------------------------------------------------------------------------------
# small physics: a jump, a bed bounce, a push (per game tick)
# ----------------------------------------------------------------------------------------------------
def jump_track(up=1.0, max_ticks=60):
    """Heights after each tick of a jump (0.42 per tick up, gravity 0.08, vertical drag 0.98) that lands `up`
    blocks higher (negative: lower). The last entry is the landing. A jump up one block: apex 1.25 after 6 ticks,
    landed on the block after 9 ticks (10.8 frames)."""
    y, v, out = 0.0, JUMP, [0.0]
    for _t in range(max_ticks):
        y += v
        if v <= 0.0 and y <= up:
            out.append(float(up))
            return out
        v = (v - GRAVITY) * AIR_DRAG_V
        out.append(y)
    raise ValueError("a jump of %r blocks does not land" % (up,))


def bounce_track(jumps=2, min_bounce=0.2, max_ticks=400):
    """Heights above the mattress after each tick of a baby villager jumping on a bed (JumpOnBed): `jumps` jumps
    of 0.42; every landing on the bed throws it up again at 0.75 of its landing speed (BED_BOUNCE); a bounce under
    `min_bounce` blocks per tick ends it (a film cut-off: the game's discrete bounce dies away in a few more
    tiny hops); it then stands 5 ticks (the behaviour's cooldown) and jumps again. Returns [height per tick]."""
    y, v, out, left = 0.0, JUMP, [0.0], int(jumps) - 1
    rest = 0
    for _t in range(max_ticks):
        if rest:
            rest -= 1
            out.append(0.0)
            if rest == 0:
                if left <= 0:
                    return out
                left -= 1
                v = JUMP
            continue
        y += v
        if y <= 0.0 and v < 0.0:
            y = 0.0
            v = -v * BED_BOUNCE
            if v < min_bounce:
                v = 0.0
                rest = BED_JUMP_COOLDOWN_TICKS
            out.append(0.0)
            continue
        v = (v - GRAVITY) * AIR_DRAG_V
        out.append(y)
    return out


# ----------------------------------------------------------------------------------------------------
# THE SET (inside the village's edit hook)
# ----------------------------------------------------------------------------------------------------
def iron_farm(b, at=AT, floor=FLOOR, name="tower", water="sheet", lava_watts=40.0):
    """Build the iron farm tower into the village (call it inside build_village(scene, edit=hook)). Returns its dict
    (also Village.sets[name]); after the build call farm(v, name) for the parts that change on camera."""
    from . import fixtures, sets

    if name in b.v.sets:
        raise KeyError("a set piece called %r exists already" % name)
    L0 = layout(at, floor, 0)
    x0, y0, x1, y1 = L0["footprint"]
    grounds = {b.ground(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    if None in grounds:
        raise ValueError("towers.iron_farm: no terrain under part of the tower at %s" % (at,))
    g = min(grounds)
    if max(grounds) - g > 1:
        raise ValueError("towers.iron_farm: the ground under the tower at %s varies by %d blocks: choose a flatter "
                         "place" % (at, max(grounds) - g))
    L = layout(at, floor, g)
    w = b.w
    # the ground: level, no plants, nothing grows here afterwards; trees that would stand in the tower go
    pad = 3
    for x in range(x0 - pad, x1 + pad + 1):
        for y in range(y0 - pad, y1 + pad + 1):
            if b.ground(x, y) != g and x0 <= x <= x1 and y0 <= y <= y1:
                b.set_ground(x, y, g)
            b.clear_plants(x, y)
            b.reserved.add((x, y))
    gone = []
    for t in list(b.trees):
        cells = [(t["x"], t["y"])] + [(c[0], c[1]) for c in t.get("leaves", ())]
        if any(x0 - 2 <= cx <= x1 + 2 and y0 - 2 <= cy <= y1 + 2 for cx, cy in cells):
            sets.remove_tree(b, t)
            gone.append((t["x"], t["y"]))
    busy = [(c, w.block_id(*c)) for c in L["cells"] if w.block_id(*c) is not None]
    if busy:
        raise ValueError("towers.iron_farm: the tower at %s would replace %s" % (at, busy[:4]))
    for c, st in sorted(L["cells"].items()):
        if st is not None:
            w.set(c[0], c[1], c[2], st[0], st[1])
    X, Y, F = L["X"], L["Y"], L["F"]
    # parts that change on camera are drawn by their own objects (claimed cells stay in the World)
    fixtures.claim(w, [L["top_step"]])
    # lights: the lantern on the floor (group <name>_pod), the wall torch at the zombie's window (<name>_cell)
    b.torch(L["lantern"], "lantern", {"hanging": "false", "waterlogged": "false"}, group=name + "_pod")
    b.torch(L["torch"], "wall_torch", {"facing": "west"}, group=name + "_cell")
    # beds: white, white, Mom's red one (village mesh) and the second red bed that appears on a frame (its own object)
    for key, foot in L["beds"].items():
        b.bed("%s_bed_%s" % (name, key), foot, "north", "red" if key == "mom" else "white")
    bed2 = fixtures.bed(b, L["bed2"], "north", "red", name=name + "_bed2")
    hopper, chest = fixtures.hopper_on_chest(b, L["chest"], "north", animated=True)
    # the glass last but the fluids: the pod (the plug, the window frame and the gap are left as they are)
    pod = fixtures.glass_box(b, *L["pod"], openings=[L["gap"], L["cell"], (L["cell"][0], L["cell"][1], F + 1)],
                             name=name + "_pod")
    px0, py0, px1, py1 = L["platform"]
    if water == "sheet":
        wat = fixtures.water_sheet(b, px0, py0, px1, py1, F, toward="west", amount=2, name=name + "_water")
    elif water == "game":
        wat = fixtures.water(b, [(x, y, F) for x in range(px0, px1 + 1) for y in range(py0, py1 + 1)],
                             sources=[(px1, y, F) for y in range(py0, py1 + 1)], name=name + "_water")
    else:
        raise ValueError("towers.iron_farm: water is 'sheet' (a level 2/9 sheet drawn flowing west) or 'game' "
                         "(sources along the pod, the game's spread), not %r" % (water,))
    sx0, sy0, sx1, sy1 = L["slot"]
    lava = fixtures.lava_glow(b, sx0, sy0, sx1, sy1, L["lava_z"], name=name + "_lava", watts_per_block=lava_watts)
    # anchors (standing spots with yaws; look targets end in _target) -----------------------------------------
    A = {}

    def anchor(key, pos, yaw=None):
        A[key] = b.anchor("%s_%s" % (name, key), pos, yaw)

    zombie_pos = (L["cell"][0] + 0.3, L["cell"][1] + 0.5, float(F))          # pressed against the sill
    zombie_eye = (zombie_pos[0], zombie_pos[1], F + 1.74)
    anchor("zombie", zombie_pos, -math.pi / 2.0)
    anchor("zombie_target", zombie_eye)
    east = math.pi / 2.0
    # Mom one whole empty block (column X + 3) from the zombie's arms, which reach out over the sill (column X + 4)
    anchor("mom", (X + 2.5, Y + 1.5, float(F)), yaw_to((X + 2.5, Y + 1.5), zombie_eye))
    anchor("mom_glass", (X + 2.5, Y + 0.45, float(F)), yaw_to((X + 2.5, Y + 0.45), zombie_eye))
    anchor("baby_glass", (X + 1.6, Y + 0.45, float(F)), east)
    anchor("bed_side", (X + 2.5, Y + 2.45, float(F)), yaw_to((X + 2.5, Y + 2.45), zombie_eye))
    for i, yy in enumerate((1.15, 1.9, 2.65)):
        p = (X + 0.42, Y + yy, float(F))
        anchor("back_%d" % (i + 1), p, yaw_to(p, zombie_eye))
    for i in range(4):
        anchor("row_%d" % (i + 1), (X + 0.5 + i, Y + 2.4, float(F)), math.pi)
    anchor("gap_in", (L["gap"][0] + 0.5, Y + 4.66, float(F)), math.pi)
    anchor("gap_side", (L["gap"][0] + 0.0, Y + 4.66, float(F)), math.pi)
    anchor("gap_target", (L["gap"][0] + 0.5, L["gap"][1] + 0.5, F + 0.5))
    ts = L["top_step"]
    anchor("top_step", (ts[0] + 0.5, ts[1] + 0.5, float(F)), 0.0)
    anchor("one_down", (ts[0] - 0.5, ts[1] + 0.5, float(F - 1)), east)
    s0 = L["steps"][0]
    anchor("stairs_foot", (s0[0] + 1.6, s0[1] + 0.5, float(g)), -math.pi / 2.0)
    anchor("stairs_target", (X + 4.5, Y + 6.0, F - 3.0))
    anchor("foot_front", (X + 2.5, Y - 1.55, float(g)), math.radians(20.0))
    anchor("pod_target", (X + 2.5, Y + 2.5, F + 1.0))
    ch_ = L["chest"]
    anchor("chest_front", (ch_[0] + 1.45, ch_[1] + 2.0, float(g)), math.radians(-140.0))
    anchor("poppies", (ch_[0] + 1.8, ch_[1] + 2.9, float(g)), yaw_of("south"))
    anchor("hopper_target", (ch_[0] + 0.5, ch_[1] + 0.5, g + 1.7))
    anchor("golem_spawn", (px0 + 1.5, Y + 2.5, float(F)), east)
    anchor("slot_target", ((sx0 + sx1) / 2.0 + 0.5, Y + 2.5, F - 0.5))
    # the square: the baby's spot on the path south-east of the well, the tower above the roofs to the north-west
    sq = (7.4, -0.4)
    anchor("square_baby", sq, yaw_to(sq, (X + 2.5, Y + 2.5)))
    lu = (X + 1.0, Y - 6.0)
    anchor("lineup", lu, math.pi / 2.0)
    route = [(X + 12.5, Y - 3.5), (X + 6.5, Y - 3.5)]
    # no plants on the ground lines of the cameras near the ground, the lineup and the push route
    for c in cameras(L).values():
        if c["pos"][2] < g + 3.5 and math.dist(c["pos"][:2], c["target"][:2]) < 30.0:
            sets.clear_view(b, c["pos"], c["target"], 2.2)
    sets.clear_view(b, route[0], route[-1], 2.4)
    sets.clear_view(b, (lu[0], lu[1] - 2.0), (lu[0], lu[1] + 2.0), 2.4)
    res = dict(name=name, layout=L, ground=g, pod=pod, bed2=bed2, hopper=hopper, chest=chest, water=wat, lava=lava,
               anchors=A, trees_removed=gone, at=(X, Y), floor=F, lights=(name + "_pod", name + "_cell"),
               zombie=zombie_pos, zombie_eye=zombie_eye, push_route=[(p[0], p[1], b.walk_z(*p)) for p in route],
               stairs=[(c[0] + 0.5, c[1] + 0.5, c[2] + 1.0)
                                                                for c in L["steps"]])
    b.v.sets[name] = res
    return res


# ----------------------------------------------------------------------------------------------------
# AFTER THE BUILD: the Farm (parts that change on camera, and the farm at work)
# ----------------------------------------------------------------------------------------------------
class Farm:
    """The built tower: .v (Village), .set (iron_farm's dict), .L (layout), .A (anchors by short name), .pod
    (GlassBox), .bed2 (fixtures Bed), .hopper / .chest, .water / .lava (Fluids), .top_step (breaking Breakable),
    .cameras {name: dict(pos, target, lens, fstop)}. Methods: see the module docstring."""

    def __init__(self, v, res):
        from . import breaking

        self.v, self.set, self.L, self.name = v, res, res["layout"], res["name"]
        self.A = {k: v.anchors["%s_%s" % (self.name, k)] for k in res["anchors"]}
        self.yaw = {k: v.yaws.get("%s_%s" % (self.name, k)) for k in res["anchors"]}
        self.pod, self.bed2, self.hopper, self.chest = res["pod"], res["bed2"], res["hopper"], res["chest"]
        self.water, self.lava = res["water"], res["lava"]
        self.top_step = breaking.place_from_world(v.collection, v.world, [self.L["top_step"]])[0]
        self.beds = {k: v.beds["%s_bed_%s" % (self.name, k)] for k in self.L["beds"]}
        self.cameras = cameras(self.L)
        self._golem_events = []

    # ---- where things are
    @property
    def zombie_eye(self):
        """The zombie's eye point in its cell (look target of every villager in the pod)."""
        return self.set["zombie_eye"]

    def pane(self, cell):
        """The glass block object at `cell` (to hide a single pane with fixtures.see_through)."""
        return self.pod.panes[tuple(int(c) for c in cell)]

    def see_through(self, st, shot, camera=None, n=1, cells=None):
        """Hide the pod's glass blocks nearest a camera outside for one shot (camera only; fixtures.see_through):
        camera = a cameras() entry or dict(pos, target) (the `n` panes its line of sight crosses first), or
        cells = [(x, y, z), ...] named. Returns the pane objects hidden."""
        from . import fixtures

        panes = [self.pane(c) for c in cells] if cells else self.panes_toward(camera["pos"], camera["target"], n)
        fixtures.see_through(st, shot, panes)
        return panes

    def panes_toward(self, camera_pos, target, n=1, walls=("north", "east", "south", "west", "roof")):
        """The `n` glass blocks of the pod nearest to the line from a camera at `camera_pos` to `target` that the
        line crosses first: the panes to hide (fixtures.see_through(st, shot, panes)) for a camera outside."""
        a, c = np.array(camera_pos, float), np.array(target, float)
        hits = []
        for wall in walls:
            for cell in self.pod.walls.get(wall, ()):
                if cell not in self.pod.panes:
                    continue
                lo = np.array(cell, float)
                t = _segment_box(a, c, lo, lo + 1.0)
                if t is not None:
                    hits.append((t, cell))
        hits.sort()
        return [self.pod.panes[cl] for _t, cl in hits[:n]]

    # ---- the zombie
    def zombie_in_cell(self, zombie, frame, aggro=False, look=None, ease=0):
        """Place an engine.undead zombie in its cell ON `frame`: pressed against the sill, facing the pod, arms out
        (their slow sway runs by itself). aggro=True: the raised, aggressive arms (ease 0 = the game's snap).
        look = a Character / point its head turns to."""
        zombie.place(frame, self.set["zombie"], -math.pi / 2.0)
        if aggro:
            zombie.aggro(frame, ease=ease)
        if look is not None:
            zombie.look_at(frame, look, ease=0)
        return frame

    # ---- the golem
    def golem_spawn(self, golem, frame, pos=None, yaw=None, look=None, look_after=6, look_ease=6):
        """The golem APPEARS on the platform ON `frame`, in one frame, standing (the game's spawn: no effect at
        all): placed at `pos` (default the golem_spawn anchor) facing `yaw` (default: north-east, across the
        platform), not rendered before `frame` (since its last slide). look = a point / Character its head turns to
        `look_after` frames later. Use ONE engine.mobs IronGolem for every spawn. Returns `frame`."""
        from . import undead

        pos = self.A["golem_spawn"] if pos is None else pos
        yaw = math.radians(-135.0) if yaw is None else yaw
        if not self._golem_events or self._golem_events[0][0] > frame:
            undead.vanish(golem, None)                                      # nothing before the first spawn
        golem.place(frame, pos, yaw)
        undead.appear(golem, frame)
        self._golem_events.append((frame, "spawn"))
        if look is not None:
            golem.look_at(frame + look_after, look, ease=look_ease)
        return frame

    def golem_step(self, golem, frame, toward=None, distance=0.45):
        """One heavy step toward `toward` (default the pod, east) against the current. Returns its end frame."""
        here = golem.pos_at(frame)
        if toward is None:
            d = (1.0, 0.0)
        else:
            t = ch._vec3(toward)
            d = (t.x - here.x, t.y - here.y)
            n = math.hypot(*d) or 1.0
            d = (d[0] / n, d[1] / n)
        to = (here.x + d[0] * distance, here.y + d[1] * distance, here.z)
        return golem.walk(frame, [tuple(here), to], ramp=(4, 6))

    def golem_slide(self, golem, frame, start=None):
        """The current carries the golem west (sideways when it faces the pod) to the slot and it drops 4 blocks out
        of sight into it (fixtures.slide: 0.014 per tick along the current, x 0.8 in water; a 1.4-wide golem falls
        when its middle is 0.7 past the rim). It is gone (not rendered) from the frame its head is below the rim.
        Returns fixtures.slide's dict (frame, edge, frame_end, gone, track) + 'drop' (4.0)."""
        from . import fixtures, undead

        here = golem.pos_at(frame) if start is None else ch._vec3(start)
        rim_x = float(self.L["platform"][0])                                # the platform's west edge
        distance = (here.x - rim_x) + GOLEM_SIZE[0] / 2.0
        drop = float(self.L["rim"] - self.L["slot_floor"])
        r = fixtures.slide(golem, frame, "west", distance, drop=drop, start=start, vanish=False)
        gone = r["gone"] if r["gone"] is not None else r["frame_end"]
        undead.vanish(golem, gone)
        self._golem_events.append((gone, "gone"))
        r.update(drop=drop, vanish=gone)
        return r

    def golem_death(self, golem, slide, camera=None, delay=0, seed=0, flicker=True, glow=None):
        """The white death puff out of the slot and the lava glow flicker for a golem that slid in: the puff
        (engine.animals.poof, 20 particles in the golem's 1.4 x 2.7 box) where its head goes under the rim, ON
        slide['gone'] + delay, rising out of the slot. delay=0 is the film's (the puff as it drops); the game's golem
        burns 240 ticks (12 s: 100 health, 4 per lava hit, one hit per 10 ticks) before it dies: delay=288.
        flicker: the lava light is smothered on gone and flares (fixtures Fluid.flicker). Returns dict(frame, burst)."""
        from . import animals

        f = int(slide["gone"] or slide["frame_end"]) + int(delay)
        x, y = slide["track"][-1][1][0], slide["track"][-1][1][1]
        feet = (x, y, float(self.L["rim"]) - GOLEM_SIZE[1] + 0.6)
        burst = animals.poof(feet, f, camera=camera, seed=seed, village=None, size=GOLEM_SIZE, glow=glow)
        if flicker:
            self.lava.flicker(slide["edge"] or slide["frame"], f + 40, at=slide["gone"] or f)
        return dict(frame=f, burst=burst)

    # ---- the drops at the foot
    def deliver(self, items, frame, every=6, seed=0, land=True, spread=0.15):
        """Dropped items (engine.mobs make_dropped_item: 'iron_ingot', 'poppy') fall out of the chute's mouth, one
        every `every` frames from `frame` on, land on the hopper and vanish into it one per 8 ticks
        (fixtures Hopper.stream). Register the items with the Stage. Returns the plans (['landed'], ['frame'] =
        the frame each is gone)."""
        h = self.hopper
        start_z = self.L["chute_mouth"] + 0.35                              # inside the dark chute
        return h.stream(items, frame, every=every, height=start_z - h.bowl, spread=spread, seed=seed, land=land)

    def strew(self, items, frame, frame_end, seed=0, spots=None, face=None):
        """Dropped items lying on the grass around the chest from `frame` on, bobbing and spinning (the poppies he
        threw out): spots = [(x, y)], default seeded spots north and east of the chest, clear of the column and
        the staircase. face = a camera position the sprites face at `frame`. Returns the spots used."""
        rng = np.random.default_rng([int(seed), 3881])
        cx, cy = self.L["chest"][0] + 0.5, self.L["chest"][1] + 0.5
        g = float(self.set["ground"])
        out = []
        for i, it in enumerate(items):
            if spots is not None:
                x, y = spots[i]
            else:
                for _try in range(40):
                    ang = rng.uniform(-0.15 * math.pi, 1.1 * math.pi)
                    r = rng.uniform(1.8, 3.4)
                    x, y = cx + r * math.cos(ang), cy + 1.5 + r * math.sin(ang) * 0.8
                    if all(math.dist((x, y), q) > 0.55 for q in out) and not self._blocked(x, y):
                        break
            out.append((x, y))
            it.place(frame, (x, y, g), age=float(rng.uniform(40, 400)))
            if face is not None:
                it.face(frame, face)
            it.animate(frame, frame_end)
        return out

    def _blocked(self, x, y):
        w, g = self.v.world, self.set["ground"]
        return w.block_id(int(math.floor(x)), int(math.floor(y)), g) is not None

    # ---- the staircase
    def break_top_step(self, player, frame, camera=None, duration=None, drop=None, seed=0):
        """The player breaks the top dirt step by hand (engine.breaking.mine: the game's 14 ticks = 17 frames from
        the click to the break, ten crack stages, arm swings, crumbs, then 64 dirt particles; drop='auto' drops the
        dirt item, None (default) drops nothing). Place him on the 'one_down' anchor facing it first. Returns
        mine()'s dict ('frame' = the frame the block is gone)."""
        from . import breaking

        return breaking.mine(player, self.top_step, frame, tool="hand", duration=duration, camera=camera,
                             drop=drop, seed=seed)

    def climb(self, c, frame, first=0, last=None, pause=3, approach=True):
        """A villager (or baby) hops up the dirt steps first..last (0 = the bottom step) one block at a time
        (hop()), `pause` frames on each. approach=True: it walks to the edge of the first step from where it
        stands first. Returns the frame it stands on the last step."""
        steps = self.set["stairs"]
        last = len(steps) - 1 if last is None else last
        f = int(frame)
        here = c.pos_at(f)
        if approach and first == 0:
            s = steps[0]
            edge = (s[0] + 0.9, s[1], here.z)
            if math.dist((here.x, here.y), edge[:2]) > 0.05:
                f = c.walk(f, [tuple(here), edge], speed=1.2)
        for i in range(first, last + 1):
            f = hop(c, f, steps[i]) + pause
        return f - pause


def farm(v, name="tower"):
    """The built tower as a Farm (call after build_village(..., edit=hook) with iron_farm in the hook)."""
    if name not in v.sets:
        raise KeyError("no iron farm %r in this village: call towers.iron_farm(b) inside the build_village hook" % name)
    res = v.sets[name]
    if "_farm" not in res:
        res["_farm"] = Farm(v, res)
    return res["_farm"]


def _segment_box(a, c, lo, hi):
    """Parameter t in [0, 1] where the segment a -> c enters the box [lo, hi], or None."""
    d = c - a
    t0, t1 = 0.0, 1.0
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if a[i] < lo[i] or a[i] > hi[i]:
                return None
            continue
        ta, tb = (lo[i] - a[i]) / d[i], (hi[i] - a[i]) / d[i]
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
        if t0 > t1:
            return None
    return t0


# ----------------------------------------------------------------------------------------------------
# THE VILLAGERS (engine.characters rigs): panic, hop, bounce, push, grow up
# ----------------------------------------------------------------------------------------------------
_LOC, _ROT = "location", "rotation_euler"


def panic(c, frame_start, frame_end, threat, seed=0, amount=1.0, turns=True, turn_deg=(14.0, 32.0),
          every=(9, 17), look=True):
    """Trapped panic: the tremble (body hunched 5 degrees, a quick +-2.4 degree twist and a sideways shiver every
    2 frames, the crossed arms pulled in) and, turns=True, quick turns ON THE SPOT (3 frames each, `turn_deg`
    either way of facing the threat, one every `every` frames), with the head kept on `threat` (a point,
    Character or Object: clamped to 70 degrees) the whole time. Two villagers with the same seed tremble frame for
    frame alike (beat 23). Not the game: there a trapped villager tries to run away from the zombie (the brain's
    PANIC activity) and jostles about its cell; this is the film's reading of that. Returns frame_end."""
    f0, f1 = int(frame_start), int(frame_end)
    if f1 - f0 < 8:
        return f1
    rng = np.random.default_rng([int(seed), 6151])
    k = float(amount)
    # body yaw: face the threat, then quick turns either side of it
    tp = c._point(threat, f0)
    here = c.pos_at(f0)
    base = math.atan2(tp.x - here.x, -(tp.y - here.y))
    y0 = c.yaw_at(f0)
    base = y0 + ch._wrap(base - y0)
    if turns:
        keys = [(f0, None), (f0 + 3, base)]
        t, side = f0 + 3 + int(rng.integers(*every)), 1.0 if rng.random() < 0.5 else -1.0
        while t + 3 < f1 - 4:
            side = -side
            keys += [(t, keys[-1][1]), (t + 3, base + side * math.radians(rng.uniform(*turn_deg)))]
            t += 3 + int(rng.integers(*every))
        keys += [(max(keys[-1][0] + 1, f1 - 4), keys[-1][1]), (f1, base)]
        ch._segment(c.root, _ROT, 2, keys)
    # the tremble (as Character.shiver, without its head tuck: the head is on the threat)
    ramp = min(6, (f1 - f0) // 3)
    b0 = ch._val(c.body, _ROT, 0, f0)
    ch._segment(c.body, _ROT, 0, [(f0, None), (f0 + ramp, b0 + math.radians(5.0) * k),
                                  (f1 - ramp, b0 + math.radians(5.0) * k), (f1, b0)])
    if c.arms is not None:
        a0 = ch._val(c.arms, _ROT, 0, f0)
        ch._segment(c.arms, _ROT, 0, [(f0, None), (f0 + ramp, a0 - 0.08 * k), (f1 - ramp, a0 - 0.08 * k), (f1, a0)])
    twist, slide = [(f0, None)], [(f0, None)]
    for n, f in enumerate(range(f0 + 2, f1 - 1, 2)):
        sgn = 1.0 if n % 2 else -1.0
        twist.append((f, sgn * rng.uniform(0.5, 1.0) * math.radians(2.4) * k))
        slide.append((f, sgn * rng.uniform(0.4, 1.0) * 0.009 * c.stride * k))
    twist.append((f1, 0.0))
    slide.append((f1, 0.0))
    ch._segment(c.body, _ROT, 2, twist, "BEZIER")
    ch._segment(c.hips, _LOC, 0, slide, "BEZIER")
    # the head on the threat, re-aimed every 2 frames against the turning body
    if look:
        yk, pk = [(f0, None)], [(f0, None)]
        f = f0 + 2
        while f < f1:
            yaw, pitch = c._aim(threat, f)
            yk.append((f, yaw))
            pk.append((f, -pitch))
            f += 2
        yaw, pitch = c._aim(threat, f1)
        yk.append((f1, yaw))
        pk.append((f1, -pitch))
        ch._segment(c.head, _ROT, 2, yk, "BEZIER")
        ch._segment(c.head, _ROT, 0, pk, "BEZIER")
    return f1


def hop(c, frame, to, face=True):
    """A villager (or baby) jumps from where it stands to the point `to` one block up (or level, or down): the
    game's jump (0.42 up, gravity 0.08, drag 0.98: up one block in 9 ticks = 11 frames, apex 1.25), travelling in a
    straight line, legs stepping as in a walk. Returns the landing frame."""
    f0 = int(round(frame))
    here = c.pos_at(f0)
    there = ch._vec3(to, here.z)
    d = there - here
    if face and math.hypot(d.x, d.y) > 1e-3:
        want = math.atan2(d.x, -d.y)
        if abs(ch._wrap(want - c.yaw_at(f0))) > math.radians(10.0):
            f0 = c.turn(f0, want, ease=4)
    heights = jump_track(there.z - here.z)
    n = len(heights) - 1
    span = math.hypot(d.x, d.y)
    f1 = f0 + n * TICK
    if span > 1e-3:
        c.walk(f0, [tuple(here), (there.x, there.y, here.z)], speed=span / (n * TICK / FPS))
    keys = [(f0 + i * TICK, here.z + h, "LINEAR") for i, h in enumerate(heights)]
    ch._segment(c.root, _LOC, 2, keys, "LINEAR")
    for i in (0, 1):                                                       # the walk's end frame is rounded: exact
        ch._segment(c.root, _LOC, i, [(f0, here[i], "LINEAR"), (f1, there[i])], "LINEAR")
    return int(math.ceil(f1 - 1e-6))


def bounce(c, frame, bed, jumps=2, place=True):
    """A baby villager jumping on a bed (JumpOnBed: babies do this by themselves): it stands on the mattress
    (place=True puts it on the bed's middle ON `frame`, facing the pillow's left), jumps 0.42 up, and each landing
    on the bed throws it back up at 0.75 of the speed (bounceRestitution 0.75) until the bounce dies; 5 ticks
    later the next of `jumps` jumps (the game: 3 to 6). bed = a Village.beds entry, a fixtures Bed or a point on
    the mattress. Returns the frame it stands still again."""
    if isinstance(bed, dict):
        pos, yaw = bed["pos"], bed.get("yaw", 0.0)
    elif hasattr(bed, "pos"):
        pos, yaw = bed.pos, bed.yaw
    else:
        pos, yaw = bed, c.yaw_at(frame)
    f0 = int(frame)
    if place:
        c.place(f0, pos, yaw + math.pi / 2.0)
    z0 = c.pos_at(f0).z
    hs = bounce_track(jumps)
    keys = [(f0 + i * TICK, z0 + h, "LINEAR") for i, h in enumerate(hs)]
    ch._segment(c.root, _LOC, 2, keys, "LINEAR")
    # the legs dangle straight, the folded arms jolt on every take-off
    for i, (a, b2) in enumerate(zip(hs, hs[1:])):
        if a == 0.0 and b2 > 0.0:
            c.swing_arm(int(f0 + i * TICK))
    return int(math.ceil(keys[-1][0]))


def _along(pts, s):
    """Point at distance s along the polyline pts (before 0 / past the end: carried on along the end segments)."""
    if s <= 0.0:
        d = (pts[1] - pts[0]).normalized()
        return pts[0] + d * s
    acc = 0.0
    for a, c in zip(pts, pts[1:]):
        seg = (c - a).length
        if s <= acc + seg or c is pts[-1]:
            return a + (c - a).normalized() * (s - acc)
        acc += seg
    return pts[-1]


SNEAK = 1.295                        # blocks/s, a sneaking player's walk (engine.players SNEAK_SPEED)


def push_route(total, gap0=1.5, mode="tap", release=0.45, rest_ticks=3, max_ticks=4000):
    """The per-tick distances along a route of `total` blocks of a player pushing a villager ahead of him with the
    game's entity push (Entity.push, see push()). mode="tap": he walks (4.317 blocks/s input) into her back and lets go of the
    key when their centres are `release` apart (held on, he would walk through her: the push weakens as the boxes
    overlap), both slide to a stop, he waits `rest_ticks` and walks on: she goes in surges of 0.7-1.1 blocks,
    about 0.9 blocks/s over all (the step-by-step way players move villagers). mode="sneak": he sneaks into her
    (1.295 blocks/s input) and holds it: a slow continuous shuffle. Returns [(tick, player along, villager
    along)] (she starts at 0 and stops at `total`)."""
    if mode not in ("tap", "sneak"):
        raise ValueError("push_route mode is 'tap' or 'sneak', not %r" % (mode,))
    a = (PLAYER_WALK if mode == "tap" else SNEAK) / 20.0 * (1.0 - GROUND_FRICTION)
    sp, sv, vp, vv = -float(gap0), 0.0, 0.0, 0.0
    state, count, out = "walk", 0, [(0, sp, sv)]
    done = False
    for t in range(1, max_ticks):
        d = sv - sp
        touching = 0.01 <= d < 0.6
        if state == "walk":
            if not done:
                vp += a
            if touching and mode == "tap" and d <= release:
                state, count = "coast", 0
        elif state == "coast":
            if abs(vp) < 2e-3 and abs(vv) < 2e-3:
                state, count = "rest", rest_ticks
        elif state == "rest":
            count -= 1
            if count <= 0:
                state, count = "walk", 0
        if touching:
            p = PUSH * math.sqrt(d)
            vv += 2.0 * p
            vp -= p
        sp += vp
        sv += vv
        if sv >= total:
            sv, vv, done = float(total), 0.0, True
            if state == "walk":
                state = "coast"
        vp *= GROUND_FRICTION
        vv *= GROUND_FRICTION
        out.append((t, sp, sv))
        if done and abs(vp) < 1e-3:
            return out
    raise ValueError("push_route: %r blocks are not covered in %d ticks" % (total, max_ticks))


def _runs(track, index, eps=2e-3):
    """[(first tick, last tick)] of the runs in which column `index` of a push_route track moves."""
    out, start = [], None
    for (t0, *a), (t1, *b) in zip(track, track[1:]):
        moving = abs(b[index - 1] - a[index - 1]) > eps
        if moving and start is None:
            start = t0
        elif not moving and start is not None:
            out.append((start, t0))
            start = None
    if start is not None:
        out.append((start, track[-1][0]))
    return out


def push(player, villager, frame, points, gap0=1.5, mode="tap", release=0.45, rest_ticks=3):
    """The player walks into the villager's back and pushes her along `points` (her route, her start first), the
    way players move villagers: push_route's game physics (Entity.push 0.05 x sqrt(centre distance), ground
    friction 0.546). mode="tap" (default): short shoves, she surges 0.7-1.1 blocks at a time and both stop in
    between (about 0.9 blocks/s); mode="sneak": a slow continuous shuffle. Both bodies face along the route and
    their legs walk while they move (engine.characters / engine.players walk per surge); key her head (look_at /
    track) AFTER this call. It place()s both ON `frame`: call it first for them in that stretch, in frame order.
    Returns dict(end, surges {name: [(frame, frame, blocks)]}, track)."""
    pts = [ch._vec3(p) for p in points]
    if len(pts) < 2:
        raise ValueError("push needs at least two points")
    total = sum((c - a).length for a, c in zip(pts, pts[1:]))
    track = push_route(total, gap0=gap0, mode=mode, release=release, rest_ticks=rest_ticks)
    f0 = int(frame)
    d0 = (pts[1] - pts[0]).normalized()
    yaw0 = math.atan2(d0.x, -d0.y)
    player.place(f0, tuple(_along(pts, -gap0)), yaw0)
    villager.place(f0, tuple(pts[0]), yaw0)
    surges = {}
    for who, index in ((player, 1), (villager, 2)):
        surges[who.name] = []
        for ta, tb in _runs(track, index):
            sa, sb = track[ta][index], track[tb][index]
            fa, fb = f0 + ta * TICK, f0 + tb * TICK
            pa, pb = _along(pts, sa), _along(pts, sb)
            speed = max(abs(sb - sa) / ((tb - ta) * TICK / FPS), 0.05)
            try:
                who.walk(int(round(fa)), [tuple(pa), tuple(pb)], speed=speed, ramp=(True, True))
            except TypeError:
                who.walk(int(round(fa)), [tuple(pa), tuple(pb)], speed=speed)
            for i in (0, 1):                                    # the exact surge, tick by tick
                keys = [(f0 + t * TICK, _along(pts, track[t][index])[i], "LINEAR") for t in range(ta, tb + 1)]
                ch._segment(who.root, _LOC, i, keys, "LINEAR")
            surges[who.name].append((fa, fb, sb - sa))
    return dict(end=int(math.ceil(f0 + track[-1][0] * TICK)), surges=surges, track=track)


def grow_up(baby, adult, frame, look=None):
    """The baby is replaced by the adult ON `frame`, on the same spot, facing the same way, in one frame (the game:
    a baby simply becomes an adult when its 24000 ticks are up; no particles). The adult is not rendered before
    `frame` (engine.undead.vanish / appear: independent of the Stage's shots), the baby not from it on. look = where
    the adult's head is from that frame (default: the baby's head direction). Returns `frame`."""
    from . import undead

    f = int(frame)
    pos, yaw = baby.pos_at(f), baby.yaw_at(f)
    head_yaw = ch._val(baby.head, _ROT, 2, f)
    adult.place(f, tuple(pos), yaw)
    if look is not None:
        adult.look_at(f, look, ease=0)
    else:
        ch._cut(adult.head, _ROT, 2, f, head_yaw)
    undead.vanish(adult, None)
    undead.appear(adult, f)
    undead.vanish(baby, f)
    return f


# ----------------------------------------------------------------------------------------------------
# cameras (filled in from the proof stills)
# ----------------------------------------------------------------------------------------------------
def cameras(L):
    """Camera framings for the beats, name -> dict(pos, target, lens, fstop, beat): the framings of the proof stills
    (a start, not a rule; see BEATS in the module docstring). L = layout() or a Farm."""
    L = getattr(L, "L", L)
    X, Y, F, g = L["X"], L["Y"], L["F"], L["g"]

    def cam(pos, target, lens, fstop=4.0, beat="", focus=None):
        d = dict(pos=tuple(float(a) for a in pos), target=tuple(float(a) for a in target), lens=float(lens),
                 fstop=float(fstop), beat=beat)
        if focus is not None:
            d["focus"] = tuple(float(a) for a in focus)
        return d

    return {
        "square": cam((8.7, -1.0, 0.8), (X + 2.0, Y + 2.5, F + 0.8), 70, 2.8,
                      "1, 4: from the plaza east of the well, the end of the tilt: the tower above the roofs"),
        "square_start": cam((8.7, -1.0, 0.8), (-1.5, -2.5, 1.2), 70, 2.8, "4: the start of the tilt: the bell"),
        "foot": cam((X + 3.6, Y - 4.1, g + 0.55), (X + 2.6, Y - 1.6, g + 0.75), 45, 2.8,
                    "5: the baby at the stone base, front three-quarter, at its own height"),
        "pod_out": cam((X - 3.0, Y - 5.4, F + 2.4), (X + 3.2, Y + 2.6, F + 0.6), 30, 4.0, "the pod from outside"),
        "pod_in": cam((X + 0.45, Y + 0.45, F + 1.5), (X + 4.7, Y + 3.0, F + 0.9), 20, 4.0, "6, 8: inside"),
        "two_shot": cam((X + 3.5, Y + 10.6, F + 1.62), (X + 3.5, Y + 1.5, F + 1.55), 55, 2.8,
                        "7: through the back glass (hide its pane), arms left, Mom right"),
        "high": cam((X + 5.0, Y + 9.0, F + 5.5), (X + 2.5, Y + 2.2, F + 0.8), 22, 4.0,
                    "21: over Steve's shoulder, the roof hidden"),
        "slide": cam((X - 4.8, Y - 7.5, F - 0.7), (X - 4.8, Y + 2.0, F + 0.4), 28, 4.0,
                     "9-11: from the south, a little below the rim"),
        "hopper": cam((X - 5.0, Y + 8.4, g + 2.9), (X - 5.5, Y + 5.5, g + 1.7), 35, 2.8, "11: the hopper at the foot"),
        "stairs": cam((X + 7.0, Y + 10.0, F + 0.6), (X + 4.2, Y + 6.4, F - 0.4), 30, 4.0,
                      "22 (outside view): the top step"),
        "lineup": cam((X + 6.0, Y - 6.0, g + 1.25), (X + 1.0, Y - 6.0, g + 0.95), 30, 4.0, "the narrator lineup"),
        "back": cam((X + 5.5, Y + 20.0, g + 4.0), (X + 3.5, Y + 4.0, g + 6.0), 26, 4.0, "12: the back, locked tall"),
        "gap": cam((X + 3.25, Y + 0.3, F + 0.45), (X + 4.45, Y + 5.0, F + 0.55), 24, 4.0, "14, 19: the gap inside"),
        "bounce": cam((X + 4.4, Y + 0.4, F + 1.3), (X + 2.5, Y + 3.3, F + 0.9), 24, 4.0, "17: the red bed"),
        "push": cam((X + 9.8, Y - 7.3, g + 0.75), (X + 9.8, Y - 3.5, g + 0.9), 30, 4.0, "3: side-on"),
    }


if __name__ == "__main__":
    import sys

    print("self-test not written yet")
    sys.exit(0)
