"""UNDERGROUND: the player's trading hall of "Two Apples", lit by the game's BLOCK LIGHT. (Docstring: see the end of
this file's first section, DOC, which is assembled into __doc__ below.)"""
import math

import bpy
import numpy as np
from mathutils import Vector

from . import blocks as _blocks
from . import mcassets as mc
from . import sets
from .village import yaw_of, yaw_to

FPS = 24
TICK = FPS / 20.0                      # film frames per game tick (1.2)

# =====================================================================================================================
# THE GAME'S LIGHT (transcribed from the 26.3 client jar; no game file is copied)
# =====================================================================================================================
# lightmap.fsh (assets/minecraft/shaders/core): block_level = floor(u * 16) / 15, sky_level likewise;
#   brightness(l) = l / (4 - 3 l); colour = max(AmbientColor, NightVision) + SkyLightColor * brightness(sky) * SkyFactor
#   + mix(BlockLightTint, white, 0.9 * (2 l - 1)^2) * brightness(block) * BlockFactor; clamp 0..1; then
#   mix(colour, notGamma(colour), BrightnessFactor) with notGamma(c) = c * (1 - (1 - max(c))^4) / max(c).
BLOCK_FACTOR = 1.4                     # LightmapRenderStateExtractor.extract: blockFactor = blockLightFlicker + 1.4F
                                       # (tick(): flicker += (r1 - r2) * r3 * r4 * 0.1, then * 0.9: it averages 0)
BLOCK_LIGHT_TINT = (255, 216, 140)     # EnvironmentAttributes.BLOCK_LIGHT_TINT default ARGB.vector3fFromRGB24(-10100)
                                       # = #FFD88C (no dimension or timeline overrides it in the overworld)
AMBIENT_LIGHT = 10.0 / 255.0           # data/minecraft/dimension_type/overworld.json visual/ambient_light_color #0a0a0a
GAMMA = 0.5                            # Options.gamma default (the Brightness slider at 50 %, "Moody" = 0)
# timeline/day.json at the film's dusk (sun 5 degrees up = DimensionType celestial angle ~0.236 = tick ~12480):
# visual/sky_light_factor keyframes 11270 -> 1.0, 13140 -> 0.24; visual/sky_light_color #ffffff -> #7a7aff
DUSK_TICK = 12480
DUSK_SKY_FACTOR = 1.0 - (DUSK_TICK - 11270) / (13140.0 - 11270.0) * (1.0 - 0.24)          # 0.508
_k = (DUSK_TICK - 11270) / (13140.0 - 11270.0)
DUSK_SKY_COLOR = (1.0 - _k * (1.0 - 0x7a / 255.0), 1.0 - _k * (1.0 - 0x7a / 255.0), 1.0)   # (0.66, 0.66, 1.0)
del _k
# CardinalLighting.DEFAULT (down, up, north, south, west, east) = (0.5, 1.0, 0.8, 0.8, 0.6, 0.6): the shade the game
# multiplies into a block face by its direction (Blender: north = +Y, east = +X)
CARDINAL = {"down": 0.5, "up": 1.0, "north": 0.8, "south": 0.8, "west": 0.6, "east": 0.6}
# Blocks static init, the lightLevel of each block (lambdas read in the bytecode): TORCH lambda$static$71 -> 14,
# WALL_TORCH lambda$static$73 -> 14, LANTERN lambda$static$324 -> 15 (both hanging states), GLOWSTONE
# lambda$static$155 -> 15, LAVA lambda$static$15 -> 15, REDSTONE_TORCH / REDSTONE_WALL_TORCH litBlockEmission(7)
LIGHT_EMISSION = {"torch": 14, "wall_torch": 14, "lantern": 15, "glowstone": 15, "lava": 15, "redstone_torch": 7,
                  "redstone_wall_torch": 7}
# BlockLightEngine.propagateIncrease: a neighbour gets level - LightEngine.getOpacity(state) = level -
# max(1, getLightDampening()); BlockBehaviour.getLightDampening = 15 for isSolidRender (opaque full cubes), 0 for
# propagatesSkylightDown, else 1; so: minus one per block step through anything that is not an opaque full cube,
# stopped by opaque full cubes. (shapeOccludes of slabs / stairs is not modelled: they pass light here.)
# SkyLightEngine: 15 straight down through open columns, then the same minus one per step.
OCCLUDING = ("dirt_path", "farmland")  # not full cubes, but useShapeForLightOcclusion with a full bottom face: the
                                       # light of the sky does not go down through the plaza's path blocks

# ---- film choices (NOT the game; see NOT THE GAME in the docstring)
WARMTH = 0.5                           # the block-light tint used: halfway from white to #FFD88C (the palette rule)
EMIT = 1.0                             # baked light drawn as emission x this (1 = the game's brightness exactly)
DOOR_KEEPS_DARK = True                 # the zombie box is baked as sealed: the open doorway stays black

# =====================================================================================================================
# THE SET (Blender cells; ground z = 0; the hall floor's walking surface is z = F)
# =====================================================================================================================
F = -10                                # hall floor walking surface (floor blocks at F - 1, air F .. F + 2, ceiling F + 3)
MOUTH_X = (4, 5)                       # the stair's two columns, east of the well (the well's stone is x -3 .. 2)
STEPS = 10                             # stone stairs at y = 0 .. -9 (step k: block z = -1 - k, top -k / -k - 0.5)
HEADROOM = 3                           # air above every step (the stairwell is 3 high, its ceiling steps down)
LANDING_Y = -10                        # the landing at the foot of the stairs (floor F)
AISLE_Y = (-12, -11)
AISLE_X = (-8, 17)                     # the aisle runs east-west; x -8 .. 3 is its unlit west stretch
LEG_X = (16, 17)                       # the aisle turns south past the end of the cell row ...
LEG_Y = (-16, -13)                     # ... to the back corner beside the zombie box
FRONT_Y, CELL_Y, BACK_Y, BOX_Y = -13, -14, -15, -16
CELL_X = {"farmer": 7, "fletcher": 9, "cleric": 11, "dad": 14}
JOB = {"farmer": ("composter", {"level": "0"}), "fletcher": ("fletching_table", {}),
       "cleric": ("brewing_stand", {"has_bottle_0": "false", "has_bottle_1": "false", "has_bottle_2": "false"}),
       "dad": ("lectern", {"facing": "north", "has_book": "false", "powered": "false"})}
PROFESSION = {"farmer": "farmer", "fletcher": "fletcher", "cleric": "cleric", "dad": "librarian"}
END_X = 15                             # the end wall of the cell row (its front pier holds the lever)
BOX = (14, BOX_Y)                      # the zombie box: one cell behind dad's, 2 high, smooth stone lid
SLOT = (15, BOX_Y, F)                  # its only opening: iron bars at floor level in its east wall
DOOR = [(14, BACK_Y, F), (14, BACK_Y, F + 1)]       # dad's back wall: two stone blocks on sticky pistons ...
DOOR_SIDE = "west"                     # ... that slide sideways (west) into the back wall behind the 2-wide pier
LEVER = (15, -12, F + 1)               # a wall lever on the north face of the end pier (15, -13, F + 1)
ROCK = (-11, -19, F - 2, 20, 3, -2)    # the solid earth around all of it (x0, y0, z0, x1, y1, z1)
HOUSE = "house_a"                      # dad's house (the roomiest vanilla house: two beds, torches, windows)
BED = "house_a_bed_2"                  # dad's bed, dyed red
STAIR = {"facing": "north", "half": "bottom", "shape": "straight", "waterlogged": "false"}
BARS_NS = {"north": "true", "south": "true", "east": "false", "west": "false", "waterlogged": "false"}
BARS_EW = {"north": "false", "south": "false", "east": "true", "west": "true", "waterlogged": "false"}
# (cell, block, props, light group): every light of the set, with its point light (village.build b.torch)
LIGHTS = [
    ((4, -2, -1), "wall_torch", {"facing": "east"}, "ug_mouth"),     # just under the rim: the glow from below
    ((5, -3, -2), "wall_torch", {"facing": "west"}, "ug_mouth"),
    ((4, -6, -5), "wall_torch", {"facing": "east"}, "ug_stairs"),
    ((5, -9, -8), "wall_torch", {"facing": "west"}, "ug_stairs"),
    ((5, LANDING_Y, F + 1), "wall_torch", {"facing": "west"}, "ug_foot"),        # the foot: beat 22's rim light
    ((9, -11, F + 1), "wall_torch", {"facing": "south"}, "ug_hall"),             # facing the farmer / fletcher
    ((14, -11, F + 1), "wall_torch", {"facing": "south"}, "ug_dad"),             # facing dad's cell
    ((10, -12, F + 2), "lantern", {"hanging": "true"}, "ug_hall"),               # the one hanging lantern
    ((17, -13, F + 1), "wall_torch", {"facing": "west"}, "ug_corner"),           # the back corner
]
LIGHT_GROUPS = ("ug_mouth", "ug_stairs", "ug_foot", "ug_hall", "ug_dad", "ug_corner")


def _rock(x, y, z):
    """What the earth is at a depth: dirt under the grass, then stone, deepslate from z -8 (z -7 is mixed)."""
    if z >= -4:
        return "dirt", None
    if z >= -6:
        return "stone", None
    if z == -7 and _blocks.pos_hash(x, y, z, 11) % 3:
        return "stone", None
    return "deepslate", {"axis": "y"}


# =====================================================================================================================
# light: the lightmap and the flood fill
# =====================================================================================================================

def _bright(level):
    """lightmap.fsh get_brightness for a level 0..15."""
    b = max(0.0, min(15.0, float(level))) / 15.0
    return b / (4.0 - 3.0 * b)


def lightmap_rgb(block=0, sky=0, sky_factor=1.0, sky_color=(1.0, 1.0, 1.0), tint=BLOCK_LIGHT_TINT, gamma=GAMMA,
                 ambient=AMBIENT_LIGHT, block_factor=BLOCK_FACTOR):
    """The colour (r, g, b) 0..1 the game multiplies into a texel at block light `block` and sky light `sky`
    (lightmap.fsh with the overworld's ambient #0a0a0a, BlockFactor 1.4, the Brightness option `gamma`)."""
    bl = max(0, min(15, int(block))) / 15.0
    c = [ambient] * 3
    sb = _bright(sky) * float(sky_factor)
    mixf = 0.9 * (2.0 * bl - 1.0) ** 2
    bb = _bright(block) * block_factor
    for i in range(3):
        t = tint[i] / 255.0
        c[i] += sky_color[i] * sb + (t + (1.0 - t) * mixf) * bb
        c[i] = min(1.0, max(0.0, c[i]))
    m = max(c)
    if m <= 0.0:
        return (0.0, 0.0, 0.0)
    scaled = 1.0 - (1.0 - m) ** 4
    return tuple(ci + (ci * scaled / m - ci) * gamma for ci in c)


def film_tint(warmth=WARMTH):
    """The block-light tint the set is baked with: #FFD88C pulled toward white (warmth 1 = the game's own)."""
    return tuple(255.0 - warmth * (255.0 - t) for t in BLOCK_LIGHT_TINT)


def _srgb_to_lin(c):
    c = max(0.0, float(c))
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def face_light(block, sky, warmth=WARMTH, emit=EMIT):
    """(D, E) for a face that looks into a cell with these levels: D = the grey factor (0..1, sRGB) baked into the
    texture (it dims whatever scene light reaches the face), E = (r, g, b) 0..1 sRGB the face shows by itself
    (the game's light drawn as emission, without the face's cardinal shade). Underground (sky 0) E is the game's
    whole lightmap colour; where the sky reaches, the scene's sky lights the face and E is only what block light
    adds on top of it at the film's dusk."""
    block, sky = int(block), int(sky)
    tint = film_tint(warmth)
    D = max(lightmap_rgb(block, sky, 1.0, (1, 1, 1), tint))
    if sky <= 0:
        E = lightmap_rgb(block, 0, 1.0, (1, 1, 1), tint)
    else:
        with_block = lightmap_rgb(block, sky, DUSK_SKY_FACTOR, DUSK_SKY_COLOR, tint)
        sky_only = lightmap_rgb(0, sky, DUSK_SKY_FACTOR, DUSK_SKY_COLOR, tint)
        floor = lightmap_rgb(0, 0)
        base = sky_only if sky >= 15 else tuple(s - f for s, f in zip(sky_only, floor))
        E = tuple(max(0.0, a - b) for a, b in zip(with_block, base))
        if block <= 0 and sky >= 15:
            E = (0.0, 0.0, 0.0)
    return D, tuple(emit * e for e in E)


def _dilate(m):
    out = np.zeros_like(m)
    out[1:] |= m[:-1]
    out[:-1] |= m[1:]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    out[:, :, 1:] |= m[:, :, :-1]
    out[:, :, :-1] |= m[:, :, 1:]
    return out


def flood(opaque, sources):
    """The game's light flood fill on a grid: sources (level array, 0 = none) spread minus one per step into every
    cell that is not opaque (BlockLightEngine / SkyLightEngine propagateIncrease). Returns the level array."""
    level = sources.astype(np.int16).copy()
    clear = ~opaque
    for lv in range(14, 0, -1):
        src = level == lv + 1
        if not src.any():
            continue
        grow = _dilate(src) & clear & (level < lv)
        level[grow] = lv
    return level


class BlockLight(sets.Environment):
    """engine.sets' Environment (biome colours, baked SKY light) with the game's BLOCK light as well, for the cells
    of one set piece (`owned`): every block face there is drawn with the lightmap of the cell it looks into, as the
    game draws it with Smooth Lighting off. The grey brightness D is baked into the texture (it dims the scene's
    own light: sky fill, bounce lamps, the torches' point lights), the colour E of the game's light is added as
    emission (see face_light). Faces of cells outside `owned` are left to engine.sets (unchanged village).
    One per World: underground.env(b)."""

    def __init__(self, world):
        super().__init__(world)
        self.sky = {}               # cell -> sky light 0..15 (absent: 15), for owned cells
        self.block = {}             # cell -> block light 0..15 (absent: 0)
        self.solid = set()          # cells opaque for light when the bake ran (absent from the World later or not)
        self.owned = set()          # cells whose faces are relit
        self.keep = {}              # cell -> (block, sky) forced for faces that look INTO that cell (door cells)
        self.warmth = WARMTH
        self.emit = EMIT
        self.registry = {}          # material key -> emission multiplier (r, g, b) linear, relative to the texture
        self._used = {}             # material key -> its (D, E) signature
        self._relit_cache = {}
        self._normals = {}

    # ---- the bake
    def bake(self, box, emitters, owned, opaque_extra=()):
        """Compute sky and block light in the box (x0, y0, z0, x1, y1, z1) of cells: `emitters` {cell: level},
        `owned` the cells whose faces will be relit, `opaque_extra` cells that count as opaque although nothing is
        in the World there (the piston door, closed). Returns (cells with block light, cells darker than sky 15)."""
        w = self.w
        x0, y0, z0, x1, y1, z1 = box
        nx, ny, nz = x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1
        opaque = np.zeros((nx, ny, nz), dtype=bool)
        extra = set(opaque_extra)
        for (x, y, z), sid in w.blocks.items():
            if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1 and (
                    w.is_full_cube(x, y, z) or w._states[sid][0] in OCCLUDING):
                opaque[x - x0, y - y0, z - z0] = True
        for (x, y, z) in extra:
            if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
                opaque[x - x0, y - y0, z - z0] = True
        # sky: open where nothing opaque is above, up to the highest block of the column in the whole World
        tops = {}
        for (x, y, z) in w.blocks:
            if x0 <= x <= x1 and y0 <= y <= y1 and z > z1 and w.is_full_cube(x, y, z):
                tops[(x, y)] = max(tops.get((x, y), -999), z)
        blocked = np.logical_or.accumulate(opaque[:, :, ::-1], axis=2)[:, :, ::-1]
        for (x, y), _z in tops.items():
            blocked[x - x0, y - y0, :] = True
        sky_src = np.where(~blocked & ~opaque, 15, 0)
        sky = flood(opaque, sky_src)
        src = np.zeros((nx, ny, nz), dtype=np.int16)
        for (x, y, z), lv in emitters.items():
            src[x - x0, y - y0, z - z0] = max(int(lv), src[x - x0, y - y0, z - z0])
        blk = flood(opaque, src)
        self.sky.clear()
        self.block.clear()
        self.solid = set()
        for i, j, k in np.argwhere(opaque):
            self.solid.add((int(i) + x0, int(j) + y0, int(k) + z0))
        for i, j, k in np.argwhere(~opaque & (sky < 15)):
            self.sky[(int(i) + x0, int(j) + y0, int(k) + z0)] = int(sky[i, j, k])
        for i, j, k in np.argwhere(~opaque & (blk > 0)):
            self.block[(int(i) + x0, int(j) + y0, int(k) + z0)] = int(blk[i, j, k])
        self.box = box
        self.owned = set(owned)
        for c in self.owned:
            self.columns.add((c[0], c[1]))
        self._cache.clear()
        self._relit_cache.clear()
        return len(self.block), len(self.sky)

    def levels(self, cell):
        """(block, sky) of a cell; an opaque cell answers with its brightest open neighbour (a face that looks into
        it is only seen when a cutaway removes it)."""
        cell = tuple(cell)
        if cell in self.keep:
            return self.keep[cell]
        if cell not in self.solid:
            return self.block.get(cell, 0), self.sky.get(cell, 15)
        best = None
        for _d, o in self._offsets:
            n = (cell[0] + o[0], cell[1] + o[1], cell[2] + o[2])
            if n in self.solid:
                continue
            lv = (self.block.get(n, 0), self.sky.get(n, 15))
            if best is None or _rank(lv) > _rank(best):
                best = lv
        return best if best is not None else (0, 0)

    def level_at(self, x, y, z):
        """Sky light 0..15 at a point (as engine.sets: 15 = open sky)."""
        c = (int(math.floor(x)), int(math.floor(y)), int(math.floor(z)))
        return self.sky.get(c, 15) if c not in self.solid else 0

    def block_at(self, x, y, z):
        """Block light 0..15 at a point."""
        return self.block.get((int(math.floor(x)), int(math.floor(y)), int(math.floor(z))), 0)

    def brightness_at(self, point):
        """The game's brightness (max channel of the lightmap, 0..1) at a point, at the film's dusk."""
        c = (int(math.floor(point[0])), int(math.floor(point[1])), int(math.floor(point[2])))
        b, s = self.levels(c)
        return max(lightmap_rgb(b, s, DUSK_SKY_FACTOR, DUSK_SKY_COLOR))

    # ---- what World.build gets
    def state_at(self, pos):
        return self.relit(self._inner, pos)

    def relit(self, inner, pos):
        """The state World.build draws at pos: relit with the baked light for owned cells."""
        if pos not in self.owned:
            return sets.Environment.state_at(self, pos) if inner is self._inner else inner(pos)
        st = inner(pos)
        if st is None:
            return None
        if any(q[2][0] in _blocks.EMISSIVE for q in st.quads):
            return st                                      # torches and lanterns glow by themselves
        own = self.levels(pos) if pos not in self.solid else None
        sig = []
        for pts, uvs, key, cull, off, mask in st.quads:
            if cull is not None:
                n = (pos[0] + off[0], pos[1] + off[1], pos[2] + off[2])
                lv = self.levels(n)
                d = cull
            else:
                lv = own if own is not None else self.levels(pos)
                d = self._normal_dir(pts)
            sig.append((lv, d))
        sig = tuple(sig)
        ck = (id(st), sig)
        hit = self._relit_cache.get(ck)
        if hit is None:
            hit = self._relit_cache[ck] = self._relight(st, sig)
        return hit

    def _normal_dir(self, pts):
        key = tuple(tuple(round(c, 4) for c in p) for p in pts[:3])
        d = self._normals.get(key)
        if d is None:
            a, b, c = (Vector(p) for p in pts[:3])
            n = (b - a).cross(c - a)
            if n.length < 1e-9:
                d = "up"
            else:
                n.normalize()
                ax = max(range(3), key=lambda i: abs(n[i]))
                d = (("west", "east"), ("south", "north"), ("down", "up"))[ax][1 if n[ax] > 0 else 0]
            self._normals[key] = d
        return d

    def _relight(self, st, sig):
        out = sets._LitState()
        out.cover, out.block_id = st.cover, st.block_id
        out.quads = []
        for (pts, uvs, key, cull, off, mask), (lv, d) in zip(st.quads, sig):
            tex, tint, ov, ov_tint, shade = key
            b, s = lv
            if b <= 0 and s >= 15:
                out.quads.append((pts, uvs, key, cull, off, mask))
                continue
            D, E = face_light(b, s, self.warmth, self.emit)
            if shade is not None:                          # cut-out plants (two-sided material): dimmed only
                E = (0.0, 0.0, 0.0)
            cs = CARDINAL.get(d, 0.8)
            E = tuple(e * cs for e in E)
            base = tint if tint is not None else (255, 255, 255)
            t2 = tuple(int(round(c * D)) for c in base)
            ov2 = None if ov_tint is None else tuple(int(round(c * D)) for c in ov_tint)
            if ov is not None and ov2 is None:
                ov2 = tuple(int(round(255 * D)) for _ in range(3))
            Dl = max(_srgb_to_lin(D), 1e-4)
            er = tuple(round(_srgb_to_lin(e) / Dl, 4) for e in E)
            if max(er) < 1e-3 and D >= 0.999:
                out.quads.append((pts, uvs, key, cull, off, mask))
                continue
            sig_de = (round(D, 4), er)
            k2 = self._unique((tex, t2, ov, ov2, shade), sig_de, base, key)
            if max(er) >= 1e-3:
                self.registry[k2] = er
            out.quads.append((pts, uvs, k2, cull, off, mask))
        return out

    def _unique(self, key, sig_de, base, orig):
        """A material key of our own for this (D, E): never the plain village key, never another face's."""
        tex, t2, ov, ov2, shade = key
        k = 0
        while True:
            cand = (tex, t2, ov, ov2, shade)
            if cand != tuple(orig) and t2 != tuple(base):
                got = self._used.get(cand)
                if got is None:
                    self._used[cand] = sig_de
                    return cand
                if got == sig_de:
                    return cand
            k += 1
            ch_ = k % 3
            step = (k + 2) // 3
            t2 = tuple(max(0, min(255, c + (-step if i == ch_ else 0))) for i, c in enumerate(key[1]))


def _rank(lv):
    b, s = lv
    return max(lightmap_rgb(b, s, DUSK_SKY_FACTOR, DUSK_SKY_COLOR))


def env(b):
    """The BlockLight environment of the builder's World (made on first use; an engine.sets Environment made
    earlier is turned into one, keeping what it baked)."""
    e = getattr(b.w, "sets_environment", None)
    if isinstance(e, BlockLight):
        return e
    if e is None:
        e = b.w.sets_environment = BlockLight(b.w)
        return e
    e.__class__ = BlockLight                                       # keep its sky bake and biome columns
    for name, val in (("sky", {}), ("block", {}), ("solid", set()), ("owned", set()), ("keep", {}),
                      ("warmth", WARMTH), ("emit", EMIT), ("registry", {}), ("_used", {}), ("_relit_cache", {}),
                      ("_normals", {})):
        setattr(e, name, val)
    return e


# =====================================================================================================================
# the set, built into the village through build_village(edit=hook)
# =====================================================================================================================

def _cells_of(x0, y0, z0, x1, y1, z1):
    return [(x, y, z) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1) for z in range(z0, z1 + 1)]


def door_cells():
    """The cells the piston door needs empty in the World: door blocks, piston heads, piston bases."""
    from . import redstone

    return redstone.door_cells(DOOR, DOOR_SIDE)


def layout():
    """{cell: (block_id, props) | None (air)} of everything this set puts under the square (the ROCK box) and the
    cells left empty for the piston door. Pure data: no World, no Blender."""
    x0, y0, z0, x1, y1, z1 = ROCK
    L = {}
    for c in _cells_of(x0, y0, z0, x1, y1, z1):
        L[c] = _rock(*c)

    def air(x, y, z):
        L[(x, y, z)] = None

    def put(x, y, z, bid, props=None):
        L[(x, y, z)] = (bid, props)

    # the stairwell: two wide, ten stone stairs down to the south, three blocks of headroom over every step
    for k in range(STEPS):
        y = -k
        for x in MOUTH_X:
            if -1 - k >= z0:
                put(x, y, -1 - k, "stone_stairs", dict(STAIR))
            for z in range(-k, -k + HEADROOM):
                if z0 <= z <= z1:
                    air(x, y, z)
    for x in MOUTH_X:                                        # the landing at the foot
        for z in range(F, F + 3):
            air(x, LANDING_Y, z)
        put(x, LANDING_Y, F - 1, "deepslate_bricks")
    # the aisle (east-west), its unlit west stretch, and the leg south to the back corner
    for x in range(AISLE_X[0], AISLE_X[1] + 1):
        for y in range(AISLE_Y[0], AISLE_Y[1] + 1):
            for z in range(F, F + 3):
                air(x, y, z)
            put(x, y, F - 1, "deepslate_bricks")
    for x in range(LEG_X[0], LEG_X[1] + 1):
        for y in range(LEG_Y[0], LEG_Y[1] + 1):
            for z in range(F, F + 3):
                air(x, y, z)
            put(x, y, F - 1, "deepslate_bricks")
    # the cell block, in stone (the piston door's blocks are stone): floor, front row, cells, back wall, box
    for x in range(6, END_X + 1):
        for y in range(BOX_Y - 1, FRONT_Y + 1):
            put(x, y, F - 1, "stone")
    jobs = {x: n for n, x in CELL_X.items()}
    for x in range(6, END_X + 1):
        # front row (job blocks, windows over them, a row of bars at the top)
        if x in jobs:
            bid, p = JOB[jobs[x]]
            put(x, FRONT_Y, F, bid, dict(p))
            air(x, FRONT_Y, F + 1)
            put(x, FRONT_Y, F + 2, "iron_bars", dict(BARS_EW))
        elif x in (8, 10):
            put(x, FRONT_Y, F, "stone")
            air(x, FRONT_Y, F + 1)
            put(x, FRONT_Y, F + 2, "iron_bars", dict(BARS_EW))
        else:
            for z in range(F, F + 3):
                put(x, FRONT_Y, z, "stone")
        # cell row: one-block cells, iron bars between the first three, a solid pier before dad's
        for z in range(F, F + 3):
            if x in jobs:
                air(x, CELL_Y, z)
            elif x in (8, 10):
                put(x, CELL_Y, z, "iron_bars", dict(BARS_NS))
            else:
                put(x, CELL_Y, z, "stone")
        # back wall
        for z in range(F, F + 3):
            put(x, BACK_Y, z, "stone")
    for c in door_cells():
        air(*c)
    # the zombie box behind dad's cell: 1 x 1 x 2 inside, a smooth stone lid, the slot of bars in its east wall
    bx, by = BOX
    for z in (F, F + 1):
        air(bx, by, z)
        put(bx - 1, by, z, "stone")
        put(bx, by - 1, z, "stone")
        put(bx + 1, by - 1, z, "stone")
        put(bx - 1, by - 1, z, "stone")
    put(bx, by, F + 2, "smooth_stone")
    put(*SLOT, "iron_bars", dict(BARS_NS))
    put(SLOT[0], SLOT[1], F + 1, "stone")
    put(SLOT[0], SLOT[1], F + 2, "stone")
    air(*LEVER)                                              # (the aisle is air there anyway: the lever's cell)
    return L


def _hole():
    """The stair's opening in the square: the ground blocks taken out (steps 0..3 have open sky above)."""
    out = []
    for k in range(STEPS):
        if -k + HEADROOM - 1 >= -1:                          # the step's headroom reaches the ground layer
            for x in MOUTH_X:
                out.append((x, -k))
    return out


CUTAWAYS = {
    # name: cells (solid ones only are kept); see_through for the camera, remove for the light too
    "ug_ceiling": lambda: _cells_of(6, BOX_Y - 1, F + 3, LEG_X[1], LANDING_Y, ROCK[5]),
    "ug_end_wall": lambda: _cells_of(END_X, BACK_Y, F, END_X, CELL_Y, F + 2),
    "ug_box_side": lambda: [(SLOT[0], SLOT[1], F + 1), (SLOT[0], SLOT[1], F + 2)],
    "ug_slot": lambda: [SLOT],
}


def underground_set(b, name="underground", bed=BED, bed_color="red", rim=True):
    """IN THE HOOK (build_village(edit=...)): the stair mouth beside the well, the stairwell, the hall, the cells,
    dad's cell with its piston wall, the zombie box, dad's red bed; the lights; the game's light baked into every
    face of it. Returns the set's dict (also Village.sets[name]); call finish(v) after build_village."""
    sets._new_name(b, name)
    w = b.w
    x0, y0, z0, x1, y1, z1 = ROCK
    # 1. the ground under the square must be empty where the set goes
    taken = [c for c in w.blocks if x0 <= c[0] <= x1 and y0 <= c[1] <= y1 and z0 <= c[2] <= z1]
    if taken:
        raise ValueError("underground_set: the earth under the square is not empty at %s (%s)"
                         % (taken[0], w.block_id(*taken[0])))
    L = layout()
    for c, st in L.items():
        if st is not None:
            w.set(c[0], c[1], c[2], st[0], st[1])
    # 2. the mouth: the ground layer opened over steps 0..3, step 0 in the ground layer itself, grass round the rim
    mx0, mx1 = MOUTH_X
    b.allow((mx0 - 3, -5, mx1 + 3, 3))                       # the well's template edge and the plaza's path
    hole = set(_hole())
    for (x, y) in hole:
        if y == 0:
            w.set(x, y, -1, "stone_stairs", dict(STAIR))
        else:
            w.set(x, y, -1, None)
        for z in range(0, 3):
            if w.block_id(x, y, z) is not None:
                w.set(x, y, z, None)
    rim_cells = []
    if rim:
        for x in range(mx0 - 1, mx1 + 2):
            for y in range(-4, 2):
                if (x, y) in hole:
                    continue
                bid = w.block_id(x, y, -1)
                if bid in ("dirt_path", "grass_block"):
                    w.set(x, y, -1, "grass_block", {"snowy": "false"})
                    b.path_cells.discard((x, y))
                    rim_cells.append((x, y))
                b.clear_plants(x, y)
    for x in range(mx0 - 3, mx1 + 4):
        for y in range(-6, 4):
            b.reserved.add((x, y))
    b.show_undersides(mx0, LANDING_Y, mx1, 0)               # the ground's underside is the stairwell's ceiling
    # 3. lights (each its own point light, groups ug_*)
    for cell, bid, props, group in LIGHTS:
        b.torch(cell, bid, dict(props), group=group)
    # 4. dad's bed, red
    if bed is not None and bed_color:
        info = b.v.beds.get(bed)
        if info is None:
            raise KeyError("underground_set: the village has no bed %r" % bed)
        house = bed.rsplit("_bed_", 1)[0]
        b.allow(house)
        for part in ("foot", "head"):
            c = tuple(int(math.floor(v)) for v in info[part])
            c = (c[0], c[1], int(math.floor(info[part][2] - 0.5)))
            st = w.get(*c)
            if st is None or not st[0].endswith("_bed"):
                raise ValueError("underground_set: no bed block at %s" % (c,))
            w.set(c[0], c[1], c[2], bed_color + "_bed", dict(st[1]))
    # 5. the game's light, baked (the piston door counts as shut; the cutaways are still in the World)
    e = env(b)
    owned = set(c for c in L)
    for x in range(mx0 - 2, mx1 + 3):
        for y in range(LANDING_Y - 1, 3):
            owned.add((x, y, -1))
    for x, y in hole:
        owned.add((x, y, -1))
    emitters = {cell: LIGHT_EMISSION[bid] for cell, bid, _p, _g in LIGHTS}
    nb, ns = e.bake((x0, y0, z0, x1, y1, 4), emitters, owned, opaque_extra=door_cells())
    box_light = e.levels((BOX[0], BOX[1], F))
    if DOOR_KEEPS_DARK:
        for c in DOOR:
            e.keep[c] = box_light
    # 6. cutaways: kept out of the village mesh, meshed on their own by finish()
    cut = {}
    for cname, cells in CUTAWAYS.items():
        got = {}
        for c in cells():
            sid = w.blocks.get(c)
            if sid is not None:
                got[c] = sid
        cut[cname] = got
    for got in cut.values():
        for c in got:
            del w.blocks[c]
    # 7. anchors, paths, cameras
    res = _register(b, name)
    res.update(cut=cut, rim=rim_cells, hole=sorted(hole), counts=dict(blocks=sum(1 for s in L.values() if s),
                                                                         lit_cells=nb, dark_cells=ns),
               box_light=box_light, env=e)
    b.v.sets[name] = res
    return res


def _register(b, name):
    """Anchors (standing spots on the walking surface; *_target / *_cam are look targets / camera spots), paths."""
    v = b.v
    A = {}

    def anchor(key, pos, yaw=None):
        A[key] = tuple(float(c) for c in pos)
        v.anchors[key] = A[key]
        if yaw is not None:
            v.yaws[key] = float(yaw)

    mx = (MOUTH_X[0] + MOUTH_X[1] + 1) / 2.0                 # the middle of the stair's width (x 5.0)

    def gz(x, y):
        z = b.walk_z(x, y)
        return 0.0 if z is None else float(z)
    anchor("ug_lip", (mx - 0.15, 1.42, gz(mx - 0.15, 1.42)), yaw_of("south"))                  # the baby at the lip (beat 2)
    anchor("ug_lip_target", (mx, -1.5, -1.2))                                  # ... staring down into it
    anchor("ug_mouth_target", (mx, -1.0, 0.2))                                 # the glowing hole
    anchor("ug_push_start", (mx, 5.2, gz(mx, 5.2)), yaw_of("south"))                   # dad, before the push (beat 3)
    anchor("ug_push_player", (mx, 6.2, gz(mx, 6.2)), yaw_of("south"))
    anchor("ug_stair_top", (mx, 0.75, 0.0), yaw_of("south"))
    anchor("ug_stair_foot", (mx, LANDING_Y + 0.45, float(F)), yaw_of("south"))  # where the steps meet the hall
    for n, x in CELL_X.items():
        anchor("ug_cell_%s" % n, (x + 0.5, FRONT_Y - 0.30, float(F)), yaw_of("north"))
        anchor("ug_cell_%s_station" % n, (x + 0.5, FRONT_Y + 0.5, F + 0.5))
        anchor("ug_aisle_%s" % n, (x + 0.5, AISLE_Y[0] + 0.85, float(F)), yaw_of("south"))   # in front of the cell
    anchor("ug_lever_target", (LEVER[0] + 0.5, LEVER[1] + 0.3, LEVER[2] + 0.45))
    anchor("ug_lever_stand", (LEVER[0] + 0.25, LEVER[1] + 1.25, float(F)), yaw_of("south"))
    anchor("ug_door_target", (DOOR[0][0] + 0.5, DOOR[0][1] + 0.5, F + 1.0))
    anchor("ug_box", (BOX[0] + 0.5, BOX[1] + 0.5, float(F)), yaw_of("north"))    # inside the box, facing the door
    anchor("ug_slot_target", (SLOT[0] + 0.5, SLOT[1] + 0.5, F + 0.5))
    anchor("ug_slot_hands", (SLOT[0] + 0.19, SLOT[1] + 0.5, float(F)), yaw_of("east"))   # see hands_in_slot()
    anchor("ug_corner", (LEG_X[1] + 0.35, LEG_Y[0] + 0.45, float(F)), yaw_of("west"))   # the back corner
    anchor("ug_leg_north", (LEG_X[0] + 0.55, AISLE_Y[0] + 0.6, float(F)), yaw_of("south"))
    anchor("ug_aisle_west_end", (AISLE_X[0] + 0.6, AISLE_Y[0] + 1.0, float(F)), yaw_of("east"))
    anchor("ug_aisle_center", (10.5, AISLE_Y[0] + 1.0, float(F)))
    anchor("ug_jump_spot", (8.5, AISLE_Y[0] + 1.0, float(F)), yaw_of("north"))    # Steve's jump loop (beat 16)
    # paths (with their own heights: stairs)
    down = [(mx, 4.0, gz(mx, 4.0)), (mx, 1.0, gz(mx, 1.0))]
    for k in range(STEPS):
        down.append((mx, -k + 0.25, -k * 1.0))
        down.append((mx, -k - 0.25, -k - 0.5))
    down += [(mx, LANDING_Y + 0.5, float(F)), (mx, AISLE_Y[1] + 0.5, float(F))]
    v.paths["ug_down"] = _dedupe(down)                       # from the square down the stairs into the aisle
    v.paths["ug_aisle"] = [(mx, AISLE_Y[1] + 0.5, float(F)), (mx + 0.4, AISLE_Y[0] + 0.9, float(F)),
                           (14.5, AISLE_Y[0] + 0.9, float(F))]                 # stair foot to dad's cell
    v.paths["ug_leg"] = [(13.5, AISLE_Y[0] + 0.6, float(F)), (LEG_X[0] + 0.6, AISLE_Y[0] + 0.6, float(F)),
                         (LEG_X[0] + 0.6, LEG_Y[0] + 0.5, float(F))]          # past the end pier to the slot
    v.paths["ug_push"] = [(mx, 5.2, gz(mx, 5.2)), (mx, 1.0, gz(mx, 1.0))]                      # dad pushed to the lip (push())
    return dict(anchors=A, paths=["ug_down", "ug_aisle", "ug_leg", "ug_push"])


def _dedupe(pts):
    out = []
    for p in pts:
        if not out or math.dist(out[-1], p) > 1e-6:
            out.append(tuple(float(c) for c in p))
    return out


# =====================================================================================================================
# after build_village: cutaways, emission materials, the redstone parts
# =====================================================================================================================

def _emissive(base, er):
    """A copy of a block material whose texels also EMIT texel x er (linear multiplier): the baked light."""
    import hashlib

    key = "|ug%.4f,%.4f,%.4f" % tuple(er)
    name = base.name + key
    if len(name) > 63:
        name = base.name[:40] + "|ug" + hashlib.md5((base.name + key).encode()).hexdigest()[:14]
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = base.copy()
    mat.name = name
    nt = mat.node_tree
    tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    for link in list(nt.links):
        if link.to_node is bsdf and link.to_socket.name in ("Emission Color", "Emission Strength"):
            nt.links.remove(link)
    vm = nt.nodes.new("ShaderNodeVectorMath")
    vm.operation = "MULTIPLY"
    vm.location = (-250, -320)
    nt.links.new(tex.outputs["Color"], vm.inputs[0])
    vm.inputs[1].default_value = tuple(float(c) for c in er)
    nt.links.new(vm.outputs[0], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 1.0
    try:
        mat.cycles.emission_sampling = "NONE"        # seen and bounced, not sampled as a light: the torches light
    except (AttributeError, TypeError):
        pass
    mat["ug_emission"] = list(er)
    return mat


def _material_for(e, tex, tint, b, s, direction, shade=None):
    """The (tinted, emissive) block material a face with these light levels gets, as World.build would draw it."""
    D, E = face_light(b, s, e.warmth, e.emit)
    cs = CARDINAL.get(direction, 0.8)
    base = tint if tint is not None else (255, 255, 255)
    t2 = tuple(int(round(c * D)) for c in base)
    Dl = max(_srgb_to_lin(D), 1e-4)
    er = tuple(round(_srgb_to_lin(x * cs) / Dl, 4) for x in E)
    mat = _blocks.block_material(tex, None if t2 == (255, 255, 255) else t2, None, None, shade)
    return _emissive(mat, er) if max(er) >= 1e-3 else mat


def _dir_of(normal):
    ax = max(range(3), key=lambda i: abs(normal[i]))
    return (("west", "east"), ("south", "north"), ("down", "up"))[ax][1 if normal[ax] > 0 else 0]


def relight_object(ob, e, cell=None, levels=None):
    """Give a separate object (a redstone part, a prop) the baked light of the set: every face its texture's
    material tinted and emitting as a World face looking into `cell` would (levels(direction) -> (block, sky)
    picks per face direction instead). The mesh is copied first."""
    if ob.type != "MESH" or not ob.data.materials:
        return ob
    me = ob.data = ob.data.copy()
    rot = ob.matrix_world.to_3x3()
    cache = {}
    new_slots = []
    for poly in me.polygons:
        mat = me.materials[poly.material_index]
        tex = mat.get("mc_texture") if mat is not None else None
        if not tex or tex in _blocks.EMISSIVE:
            continue
        n = rot @ poly.normal
        d = _dir_of(n)
        lv = levels(d) if levels is not None else e.levels(cell)
        key = (mat.name, d, lv)
        m2 = cache.get(key)
        if m2 is None:
            m2 = cache[key] = _material_for(e, tex, None, lv[0], lv[1], d, mat.get("mc_shade"))
        if m2.name not in [m.name for m in me.materials]:
            me.materials.append(m2)
            new_slots.append(m2)
        poly.material_index = [m.name for m in me.materials].index(m2.name)
    return ob


class UndergroundSet:
    """What finish(v) returns: the built set with its parts. See the module docstring (PUBLIC API)."""

    def __init__(self, v, res, kit, door, lever):
        self.v, self.res, self.kit, self.door, self.lever = v, res, kit, door, lever
        self.env = res["env"]
        self.anchors = res["anchors"]
        self.cameras = cameras()
        self.cutaways = list(CUTAWAYS)
        self.parts = [door, lever]

    # ---- the wall
    def open_wall(self, frame, player=None, reach=True, look=True):
        """The lever is flipped on `frame` (by `player` if given: his swing starts on frame) and dad's back wall
        opens: the hidden inverter (a redstone torch behind the pier, 2 ticks) un-powers the sticky pistons,
        which pull the two stone blocks west into the wall in 2 ticks. Returns dict(flip, open, open_end) frames."""
        from . import redstone

        if player is not None:
            t = redstone.flip_by(player, self.lever, frame, look=look, reach=reach)
        else:
            t = self.lever.flip(frame)
        t_open = redstone.at(t, redstone.TORCH_TOGGLE_TICKS)
        end = self.door.open(t_open)
        return dict(flip=redstone.frame_of(t), open=redstone.frame_of(t_open), open_end=redstone.frame_of(end))

    def close_wall(self, frame, lever=True):
        """The pistons push the wall shut on `frame` (and the lever goes back first, 2 ticks earlier, if lever)."""
        from . import redstone

        if lever:
            self.lever.flip(int(math.floor(frame - redstone.TORCH_TOGGLE_TICKS * TICK)))
        end = self.door.close(frame)
        return redstone.frame_of(end)

    def brightness_at(self, point):
        """The game's brightness 0..1 at a point of the set (the lightmap of its block and sky light)."""
        return self.env.brightness_at(point)

    def register(self, st):
        """Put the door and the lever in st.cast (then st.use(shot, *ug.parts) in EVERY shot that sees them:
        unregistered they are simply always there, which is what most films want)."""
        for p in self.parts:
            st.cast[p.name] = p


def finish(v, name="underground"):
    """AFTER build_village: mesh the cutaways (Village.cutaways: ug_ceiling, ug_end_wall, ug_box_side, ug_slot),
    give the baked faces their emission, build the piston door and the lever (engine.redstone) and light them
    like the wall they sit in. Returns an UndergroundSet."""
    from . import redstone

    res = v.sets[name]
    e = res["env"]
    w = v.world
    coll = v.collection
    for cname, got in res["cut"].items():
        sub = _blocks.World()
        sub._states, sub._state_ids, sub._baked, sub._variants = w._states, w._state_ids, w._baked, w._variants
        sub.blocks = dict(got)
        hidden = set()
        for c in got:
            for d in mc.DIRS:
                o = mc.DIR_BLENDER[d]
                n = (c[0] + o[0], c[1] + o[1], c[2] + o[2])
                if n in w.blocks and w.is_full_cube(*n):
                    hidden.add((c, d))
        sub.hidden_sides = hidden
        inner = sub._state_at
        sub._state_at = (lambda pos, inner=inner: e.relit(inner, pos))
        objs = sub.build(coll, cname)
        v.cutaways[cname] = objs
        v.face_count += sub.last_face_count
    swaps = {}
    for key, er in e.registry.items():
        base = _blocks.block_material(*key)
        swaps[base.name] = (base, er)
    obs = list(v.objects) + [o for n in CUTAWAYS for o in v.cutaways.get(n, [])]
    for ob in obs:
        if ob.type != "MESH":
            continue
        me = ob.data
        for i, m in enumerate(me.materials):
            if m is not None and m.name in swaps:
                me.materials[i] = _emissive(*swaps[m.name])
    k = redstone.kit(v)
    door = k.piston_door(DOOR, DOOR_SIDE, block="stone", closed=True, name="ug_door")
    lever = k.lever(LEVER, "wall", facing="north", powered=False, name="ug_lever")
    box = e.levels((BOX[0], BOX[1], F))
    for i, blk in enumerate(door.blocks):
        z = DOOR[i][2]
        front = e.levels((DOOR[i][0], DOOR[i][1] + 1, z))
        relight_object(blk.object, e, levels=lambda d, front=front: front if d == "north" else box)
    for ob in lever.objects:
        relight_object(ob, e, cell=LEVER)
    ug = UndergroundSet(v, res, k, door, lever)
    res["set"] = ug
    return ug


def build_village(scene, seed=1, bed_colors=None, edit=None, **kw):
    """village.build_village with this set in its hook (plus `edit`, another film hook, called first), then
    finish(): returns (Village, UndergroundSet). kw go to underground_set."""
    from . import village

    def hook(b):
        if edit is not None:
            edit(b)
        underground_set(b, **kw)

    v = village.build_village(scene, seed=seed, bed_colors=bed_colors, edit=hook)
    return v, finish(v)


def cameras():
    """Suggested cameras per beat: name -> dict(pos, target, lens, fstop, note). Filled in below (CAMERAS)."""
    return {k: dict(v) for k, v in CAMERAS.items()}


CAMERAS = {}
