"""Voxel world built from the real Minecraft block models (engine/mcassets.py) and meshed for Blender.

World stores block states (block_id, props) at integer BLENDER grid coordinates: block (x, y, z) occupies
[x, x+1] x [y, y+1] x [z, z+1], Z up, Minecraft north (-z) = Blender +Y, east = +X.
build() draws every block with the game's own model for its state (blockstate variants / multipart, rotations,
uvlock, per-face uv / rotation / tint), drops faces the game would cull, and merges everything into one mesh per
material.
"""
import math

import bpy

from . import mcassets as mc

HORIZ = ("north", "east", "south", "west")  # clockwise seen from above
_OFFSET = mc.DIR_BLENDER

# glow: texture -> (emission strength, only texels brighter than this HSV value glow[, self-illumination of the
# other texels]). The strengths put only the 2x2 core of a flame above the highlight shoulder (engine/look.py): at
# 7-9 the whole flame clipped and the shoulder's drift to white turned the game's orange into salmon. The third
# value stands in for the game drawing the block itself at light level 15: its point light sits inside the model
# and reaches none of its own faces, so the lantern's iron, its chain and the torch's stick would stay black.
EMISSIVE = {
    "block/torch": (4.5, 0.82, 0.45),
    "block/lantern": (3.0, 0.6, 0.6),
    "block/soul_torch": (3.5, 0.8, 0.45),
    "block/soul_lantern": (3.0, 0.6, 0.6),
    "block/lava_still": (3.0, None),
    "block/lava_flow": (3.0, None),
    "block/furnace_front_on": (3.0, 0.6),
    "block/blast_furnace_front_on": (3.0, 0.6),
    "block/smoker_front_on": (3.0, 0.6),
    "block/campfire_fire": (3.5, None),
    "block/campfire_log_lit": (2.5, 0.6),
    "block/glowstone": (2.0, None),
    "block/sea_lantern": (2.0, None),
    "block/jack_o_lantern": (2.5, 0.7),
    "block/redstone_lamp_on": (2.0, None),
    "block/fire_0": (3.5, None),
}

# blocks you can walk through (no collision)
_NONSOLID = {
    "air", "short_grass", "tall_grass", "fern", "large_fern", "dead_bush", "poppy", "dandelion", "oxeye_daisy",
    "cornflower", "azure_bluet", "allium", "blue_orchid", "red_tulip", "orange_tulip", "white_tulip", "pink_tulip",
    "lily_of_the_valley", "torch", "wall_torch", "wheat", "carrots", "potatoes", "beetroots", "ladder", "water",
    "lava", "vine", "sugar_cane", "lever", "rail", "redstone_wire", "sunflower", "lilac", "rose_bush", "peony",
    "brown_mushroom", "red_mushroom", "soul_torch", "soul_wall_torch",
}
_NONSOLID_SUFFIX = ("_carpet", "_pressure_plate", "_sign", "_button", "_sapling", "_banner")

# plants the game shifts by a per-column random offset: id -> also shift down (XYZ offset type)
_RANDOM_OFFSET = {
    "short_grass": True, "fern": True, "tall_grass": False, "large_fern": False, "poppy": False, "dandelion": False,
    "oxeye_daisy": False, "cornflower": False, "azure_bluet": False, "allium": False, "blue_orchid": False,
    "red_tulip": False, "orange_tulip": False, "white_tulip": False, "pink_tulip": False,
    "lily_of_the_valley": False,
}

WATER_HEIGHT = 16.0 * 8.0 / 9.0  # a source block's surface, in model pixels


def pos_hash(x, y, z, salt=0):
    """Deterministic 32-bit hash of a block position (used wherever the game picks a random variant by position)."""
    x, y, z = int(x), int(y), int(z)
    h = (x * 3129871) ^ (y * 116129781) ^ (z * 42317861) ^ (salt * 1013904223)
    h = (h * h * 42317861 + h * 11) & 0xFFFFFFFFFFFF
    return (h >> 16) & 0xFFFFFFFF


def rotate_facing(facing, rot):
    """A horizontal direction name after `rot` clockwise quarter turns (north -> east -> south -> west)."""
    if facing not in HORIZ:
        return facing
    return HORIZ[(HORIZ.index(facing) + rot) % 4]


def rotate_props(props, rot):
    """Block state properties after `rot` clockwise quarter turns: facing, axis, sign rotation and the
    north/east/south/west connection flags all turn with the block (hinge, half, shape, type stay)."""
    rot %= 4
    if not rot or not props:
        return dict(props or {})
    out = {}
    for k, v in props.items():
        if k in HORIZ:
            out[rotate_facing(k, rot)] = v
        elif k == "facing":
            out[k] = rotate_facing(v, rot)
        elif k == "axis":
            out[k] = {"x": "z", "z": "x"}.get(v, v) if rot % 2 else v
        elif k == "rotation":
            out[k] = str((int(v) + 4 * rot) % 16)
        else:
            out[k] = v
    return out


class Placement:
    """Where a template landed: converts template (Minecraft) coordinates and directions to the Blender grid."""

    def __init__(self, template, origin, rot):
        self.template, self.origin, self.rot = template, tuple(origin), rot % 4
        sx, sy, sz = template.size
        self.size = (sz, sx, sy) if self.rot % 2 else (sx, sz, sy)  # Blender extent (x, y, z)
        self.blocks = []  # (bx, by, bz, block_id, props) after rotation

    def pos(self, tx, ty, tz):
        """Template block (x, y, z) in Minecraft axes -> Blender grid cell (x, y, z)."""
        sx, sy, sz = self.template.size
        r = self.rot
        if r == 0:
            x, z, depth = tx, tz, sz
        elif r == 1:
            x, z, depth = sz - 1 - tz, tx, sx
        elif r == 2:
            x, z, depth = sx - 1 - tx, sz - 1 - tz, sz
        else:
            x, z, depth = tz, sx - 1 - tx, sx
        return (self.origin[0] + x, self.origin[1] + depth - 1 - z, self.origin[2] + ty)

    def facing(self, facing):
        """A template direction name ('north' ...) after this placement's rotation."""
        return rotate_facing(facing, self.rot)

    def find(self, block_id, **props):
        """Blender cells of every placed block with this id (and matching props), sorted."""
        out = []
        for bx, by, bz, b, p in self.blocks:
            if b == block_id and all(p.get(k) == v for k, v in props.items()):
                out.append((bx, by, bz))
        return sorted(out)

    @property
    def bounds(self):
        """Inclusive Blender cell bounds (x0, y0, z0, x1, y1, z1)."""
        o, s = self.origin, self.size
        return (o[0], o[1], o[2], o[0] + s[0] - 1, o[1] + s[1] - 1, o[2] + s[2] - 1)


class _State:
    """A baked block state: quads in Blender block-local space with material keys, plus its occlusion masks."""
    __slots__ = ("quads", "cover", "block_id")

    def __init__(self, block_id, quads):
        self.block_id = block_id
        self.cover = mc.cover_masks(quads)
        self.quads = []
        for q in quads:
            tint = mc.block_tint(block_id, q.tintindex)
            ov, ov_tint = None, None
            if q.overlay is not None:
                ov = q.overlay[0]
                ov_tint = mc.block_tint(block_id, q.overlay[1])
            key = (q.texture, tint, ov, ov_tint, q.shade)
            pts = [mc.to_blender(p) for p in q.pts]
            off = _OFFSET[q.cull] if q.cull else None
            self.quads.append((pts, q.uvs, key, q.cull, off, q.mask))


def is_glass_like(block_id):
    """Blocks whose touching faces vanish against the same block (glass, panes, bars)."""
    return block_id.endswith("glass") or block_id.endswith("glass_pane") or block_id == "iron_bars"


class World:
    """Sparse grid of Minecraft block states in Blender coordinates that meshes itself with the real block models."""

    def __init__(self):
        self.blocks = {}          # (x, y, z) -> state id
        self._states = []         # state id -> (block_id, props)
        self._state_ids = {}
        self._baked = {}          # (state id, variant) -> _State
        self._variants = {}       # state id -> number of random variants
        self.cull_below = None    # downward faces of blocks at or below this z are never drawn
        self.hidden_sides = set()  # ((x, y, z), direction) faces never drawn (e.g. the outer rim of the terrain)
        self.passable = set()     # cells treated as walkable regardless of the block there (animated doors)
        self.cull = True          # False draws every face (debugging aid to verify the culling)
        self.last_face_count = 0
        self.placements = []

    # ---- editing -------------------------------------------------------------------------------

    def _sid(self, block_id, props):
        block_id = block_id.replace("minecraft:", "")
        props = {k: (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in (props or {}).items()}
        key = (block_id, tuple(sorted(props.items())))
        sid = self._state_ids.get(key)
        if sid is None:
            sid = len(self._states)
            self._states.append((block_id, props))
            self._state_ids[key] = sid
        return sid

    def set(self, x, y, z, block_id, props=None):
        """Place block state `block_id` with `props` at integer (x, y, z); block_id None / 'air' removes it."""
        if block_id is None or block_id == "air":
            self.blocks.pop((x, y, z), None)
        else:
            self.blocks[(x, y, z)] = self._sid(block_id, props)

    def get(self, x, y, z):
        """(block_id, props) at (x, y, z) or None."""
        sid = self.blocks.get((x, y, z))
        return None if sid is None else self._states[sid]

    def block_id(self, x, y, z):
        """Block id at (x, y, z) or None."""
        sid = self.blocks.get((x, y, z))
        return None if sid is None else self._states[sid][0]

    def fill(self, x0, y0, z0, x1, y1, z1, block_id, props=None):
        """Fill the inclusive box with a block state (None clears it)."""
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, block_id, props)

    def set_door(self, x, y, z, facing="north", hinge="left", block_id="oak_door", open=False):
        """Place both halves of a door with its lower half at (x, y, z)."""
        for dz, half in ((0, "lower"), (1, "upper")):
            self.set(x, y, z + dz, block_id, {"facing": facing, "half": half, "hinge": hinge,
                                              "open": "true" if open else "false", "powered": "false"})

    def set_bed(self, x, y, z, facing="north", color="white"):
        """Place a bed with its foot at (x, y, z) and its head one block further in direction `facing`."""
        dx, dy, _ = _OFFSET[facing]
        self.set(x, y, z, color + "_bed", {"facing": facing, "part": "foot", "occupied": "false"})
        self.set(x + dx, y + dy, z, color + "_bed", {"facing": facing, "part": "head", "occupied": "false"})

    def place_template(self, template, origin, rot=0, keep=None):
        """Place a structure template with the min corner of its (rotated) footprint at Blender cell `origin`.

        Minecraft (x, y, z) maps to Blender (x, -z, y); `rot` is clockwise quarter turns seen from above
        (north -> east), applied to positions AND to facing / axis / connection properties.
        keep(block_id, props, (tx, ty, tz)) -> bool can drop blocks. Returns a Placement (pos(), facing(), find()).
        """
        pl = Placement(template, origin, rot)
        for tx, ty, tz, block_id, props in template.blocks:
            if keep is not None and not keep(block_id, props, (tx, ty, tz)):
                continue
            p = rotate_props(props, pl.rot)
            bx, by, bz = pl.pos(tx, ty, tz)
            self.set(bx, by, bz, block_id, p)
            pl.blocks.append((bx, by, bz, block_id, p))
        self.placements.append(pl)
        return pl

    # ---- queries -------------------------------------------------------------------------------

    def is_solid(self, x, y, z):
        """True if the block at (x, y, z) has collision (plants, torches, carpets, fluids and open doors do not)."""
        if (x, y, z) in self.passable:
            return False
        st = self.get(x, y, z)
        if st is None:
            return False
        block_id, props = st
        if block_id in _NONSOLID or block_id.endswith(_NONSOLID_SUFFIX):
            return False
        if props.get("open") == "true" and (block_id.endswith("_door") or block_id.endswith("_fence_gate")):
            return False
        return True

    def is_full_cube(self, x, y, z):
        """True if the block at (x, y, z) hides all six neighbouring faces (an opaque full cube)."""
        sid = self.blocks.get((x, y, z))
        if sid is None:
            return False
        cover = self._state(sid, 0).cover
        return all(cover[d] == mc.FULL_MASK for d in mc.DIRS)

    def top(self, x, y, z_from=48, z_to=-16):
        """Highest z in column (x, y) holding a solid block, or None."""
        for z in range(z_from, z_to - 1, -1):
            if self.is_solid(x, y, z):
                return z
        return None

    def surface(self, x, y, z_from=48, z_to=-16):
        """Height of the walking surface in column (x, y): top of the highest solid block (dirt_path and farmland are
        15/16 high, bottom slabs 8/16), or None."""
        z = self.top(x, y, z_from, z_to)
        if z is None:
            return None
        block_id, props = self.get(x, y, z)
        if block_id in ("dirt_path", "farmland"):
            return z + 15.0 / 16.0
        if block_id.endswith("_slab") and props.get("type", "bottom") == "bottom":
            return z + 0.5
        return z + 1.0

    # ---- meshing -------------------------------------------------------------------------------

    def _connections(self, x, y, z, block_id, props):
        """Fill in fence / pane / wall connection flags for hand-placed blocks that did not specify them."""
        fence = block_id.endswith("_fence")
        pane = block_id.endswith("_pane") or block_id == "iron_bars"
        wall = block_id.endswith("_wall")
        if not (fence or pane or wall) or any(k in props for k in HORIZ):
            return props
        out = dict(props)
        n = 0
        for d in HORIZ:
            dx, dy, _ = _OFFSET[d]
            nb = self.get(x + dx, y + dy, z)
            join = False
            if nb is not None:
                nid = nb[0]
                if self.is_full_cube(x + dx, y + dy, z) and not nid.endswith("_leaves"):
                    join = True
                elif fence and (nid.endswith("_fence") or nid.endswith("_fence_gate")):
                    join = True
                elif (pane or wall) and (nid.endswith("_pane") or nid == "iron_bars" or nid.endswith("_wall")):
                    join = True
            n += join
            out[d] = ("low" if join else "none") if wall else ("true" if join else "false")
        if wall:
            straight = (out["north"] != "none" and out["south"] != "none" and out["east"] == "none"
                        and out["west"] == "none") or (out["east"] != "none" and out["west"] != "none"
                                                       and out["north"] == "none" and out["south"] == "none")
            out["up"] = "false" if straight and self.get(x, y, z + 1) is None else "true"
        return out

    def _state(self, sid, variant, pos=None):
        key = (sid, variant)
        st = self._baked.get(key)
        if st is None:
            block_id, props = self._states[sid]
            quads = []
            if block_id in ("water", "lava"):
                quads = []
            elif block_id in ("chest", "trapped_chest"):
                quads = mc.chest_quads(props.get("facing", "north"))
            elif mc.has_blockstate(block_id):
                quads = list(mc.bake_block(block_id, props, variant))
                if block_id == "bell":
                    quads += _bell_body(props)
            else:
                print("blocks: unknown block id %r (skipped)" % block_id)
            st = _State(block_id, quads)
            self._baked[key] = st
        return st

    def _state_at(self, pos):
        sid = self.blocks.get(pos)
        if sid is None:
            return None
        block_id, props = self._states[sid]
        if not any(k in props for k in HORIZ) and (block_id.endswith(("_fence", "_pane", "_wall"))
                                                   or block_id == "iron_bars"):
            sid = self._sid(block_id, self._connections(pos[0], pos[1], pos[2], block_id, props))
        nv = self._variants.get(sid)
        if nv is None:
            nv = 1
            if block_id not in ("water", "lava", "chest") and mc.has_blockstate(block_id):
                nv = mc.variant_count(block_id, props)
            self._variants[sid] = nv
        variant = pos_hash(pos[0], pos[1], pos[2]) % nv if nv > 1 else 0
        return self._state(sid, variant)

    def build(self, collection, name="world", skip=()):
        """Mesh the world with the real block models. Faces hidden by opaque neighbours are culled (cullface is
        rotated with the model), everything is merged into one mesh object per material. `skip` = positions that
        are built separately as animated props (they are neither drawn nor allowed to hide their neighbours)."""
        skip = set(skip)
        mb = mc.MeshBuilder()
        blocks = self.blocks
        states = self._states
        cull_below = self.cull_below
        hidden = self.hidden_sides
        full = mc.FULL_MASK
        opposite = mc.OPPOSITE
        for pos, sid in list(blocks.items()):
            if pos in skip:
                continue
            x, y, z = pos
            block_id = states[sid][0]
            if block_id in ("water", "lava"):
                self._fluid(mb, pos, block_id, skip)
                continue
            st = self._state_at(pos)
            ox = oy = oz = 0.0
            if block_id in _RANDOM_OFFSET:
                h = pos_hash(x, y, 0, 7)
                ox = ((h & 15) / 15.0 - 0.5) * 0.5
                oy = (((h >> 8) & 15) / 15.0 - 0.5) * 0.5
                if _RANDOM_OFFSET[block_id]:
                    oz = (((h >> 4) & 15) / 15.0 - 1.0) * 0.2
            glassy = is_glass_like(block_id)
            leafy = block_id.endswith("_leaves")
            for pts, uvs, key, cull, off, mask in st.quads:
                if cull is not None:
                    if cull == "down" and cull_below is not None and z <= cull_below:
                        continue
                    if hidden and (pos, cull) in hidden:
                        continue
                    npos = (x + off[0], y + off[1], z + off[2])
                    if self.cull and npos in blocks and npos not in skip:
                        nb = self._state_at(npos)
                        cov = nb.cover[opposite[cull]]
                        if cov == full or (mask & ~cov) == 0:
                            continue
                        if nb.block_id == block_id and (glassy or (leafy and cull in ("down", "south", "west"))):
                            continue
                mb.add(key, [(p[0] + x + ox, p[1] + y + oy, p[2] + z + oz) for p in pts], uvs)
        objs = []
        total = 0
        for key in sorted(mb.verts, key=lambda k: (k[0], str(k[1:]))):
            tex, tint, ov, ov_tint, shade = key
            mat = block_material(tex, tint, ov, ov_tint, shade)
            # "shade_direction_override": "up" quads (plants, crops, torches, lanterns) get up-pointing normals
            me = mb.mesh(key, "%s_%s" % (name, mat.name.replace("mc/", "").replace("/", "_")),
                         up_normals=True if shade else None)
            me.materials.append(mat)
            ob = bpy.data.objects.new(me.name, me)
            collection.objects.link(ob)
            objs.append(ob)
            total += len(me.polygons)
        self.last_face_count = total
        return objs

    def _fluid(self, mb, pos, block_id, skip):
        """Water / lava are not JSON models in the game: a source block is a box whose top sits at 8/9 of a block
        (full height under more fluid), drawn with the still texture; faces against solid blocks or more fluid are
        dropped."""
        x, y, z = pos
        tex = "block/%s_still" % block_id
        tint = mc.block_tint(block_id, 0)
        key = (tex, tint, None, None, None)
        above = self.block_id(x, y, z + 1)
        h = 16.0 if above == block_id else WATER_HEIGHT
        box_from, box_to = (0.0, 0.0, 0.0), (16.0, h, 16.0)
        for d in mc.DIRS:
            off = _OFFSET[d]
            npos = (x + off[0], y + off[1], z + off[2])
            nid = self.block_id(*npos)
            if d == "up":
                if above == block_id:
                    continue
            elif nid == block_id or (nid is not None and npos not in skip and self.is_full_cube(*npos)):
                continue
            elif d == "down" and self.cull_below is not None and z <= self.cull_below:
                continue
            pts = mc._face_points(d, box_from, box_to)
            u1, v1, u2, v2 = mc.default_uv(d, box_from, box_to)
            uvs = [(u1, v1), (u1, v2), (u2, v2), (u2, v1)]
            mb.add(key, [tuple(a + b for a, b in zip(mc.to_blender(p), pos)) for p in pts], uvs)


def _bell_body(props):
    """Static bell body quads for a bell block that is not replaced by the animated prop."""
    quads = mc.bell_body_quads()
    y = {"north": 0, "east": 90, "south": 180, "west": 270}.get(props.get("facing", "north"), 0)
    if props.get("attachment") in ("single_wall", "double_wall"):
        y = (y + 270) % 360
    for q in quads:
        q.pts = [mc.rotate_point(p, 0, y) for p in q.pts]
        q.facing = None
    return quads


def block_material(texture, tint=None, overlay=None, overlay_tint=None, shade=None):
    """The material used for a block texture: Closest filtering, alpha mode from the texture, flames glow.
    shade = a Quad's shade flag ('up_thin' selects the two-sided plant material, see mcassets.material)."""
    emission, above, base = (tuple(EMISSIVE.get(texture, (0.0, None))) + (0.0,))[:3]
    kw = {}
    if texture in ("block/water_still", "block/water_flow"):
        kw = dict(roughness=0.12, specular=0.5)
    elif texture.startswith("entity/bell/") or texture.startswith("block/bell_"):
        kw = dict(roughness=0.55, specular=0.35)
    mat = mc.material(texture, tint=tint, overlay=overlay, overlay_tint=overlay_tint, emission=emission,
                      emit_above=above, emit_base=base, shade=shade, **kw)
    if emission > 0 and "lava" not in texture:
        # flames glow for the camera, but the lighting comes from the point lights (props.make_light): keeping
        # these tiny emitters out of light sampling avoids noise
        mat.cycles.emission_sampling = "NONE"
    return mat


def new_collection(scene, name):
    """Create (or reuse) a collection linked to the scene."""
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        scene.collection.children.link(coll)
    return coll


# --------------------------------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------------------------------

def _ground(w, x0, y0, x1, y1, block="grass_block"):
    w.fill(x0, y0, -1, x1, y1, -1, block)
    w.cull_below = -1


def _swatch():
    from . import quick

    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, "day")
    w = World()
    _ground(w, -4, -4, 10, 14, "smooth_stone")
    items = [
        ("grass_block", None), ("dirt", None), ("dirt_path", None),
        ("cobblestone", None), ("mossy_cobblestone", None), ("oak_planks", None),
        ("oak_log", {"axis": "y"}), ("oak_log", {"axis": "x"}), ("oak_log", {"axis": "z"}),
        ("stripped_oak_log", {"axis": "y"}), ("stone_bricks", None), ("glass", None),
        ("bookshelf", None), ("hay_block", {"axis": "y"}), ("farmland", {"moisture": "7"}),
        ("water", None), ("white_terracotta", None), ("oak_leaves", None),
    ]
    for i, (b, p) in enumerate(items):
        cx, cy = (i % 3) * 2 + (i // 3) % 2, (5 - i // 3) * 2
        w.set(cx, cy, 0, b, p)
        if b == "farmland":
            w.set(cx, cy, 1, "wheat", {"age": "7"})
        if b == "water":
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                w.set(cx + dx, cy + dy, 0, "cobblestone")
            w.set(cx, cy, -1, "cobblestone")
    coll = new_collection(scene, "set")
    w.build(coll)
    print("blocks_swatch faces:", w.last_face_count)
    quick.camera(scene, (8.2, -8.8, 15.0), (3.0, 4.3, 0.2), lens=35)
    print("wrote", quick.render(scene, "blocks_swatch"))


def _shapes():
    from . import quick

    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, "day")
    w = World()
    _ground(w, -4, -4, 11, 22, "grass_block")
    # row A: straight stairs facing east, south, west, north
    for i, f in enumerate(("east", "south", "west", "north")):
        w.set(i * 2, 0, 0, "oak_stairs", {"facing": f, "half": "bottom", "shape": "straight"})
    # row B: upside-down stairs, corner stairs, slabs
    w.set(0, 2, 0, "oak_stairs", {"facing": "north", "half": "top", "shape": "straight"})
    w.set(2, 2, 0, "cobblestone_stairs", {"facing": "north", "half": "bottom", "shape": "inner_left"})
    w.set(4, 2, 0, "oak_slab", {"type": "bottom"})
    w.set(5, 2, 0, "oak_slab", {"type": "top"})
    w.set(6, 2, 0, "smooth_stone_slab", {"type": "bottom"})
    # row C: connected fences, glass panes two high
    for x in (0, 1, 2):
        w.set(x, 4, 0, "oak_fence")
    w.set(2, 5, 0, "oak_fence")
    for x in (4, 5, 6):
        w.set(x, 4, 0, "glass_pane")
        w.set(x, 4, 1, "glass_pane")
    # row D: oak door in a plank wall, white bed, torch
    for x in (0, 2):
        w.fill(x, 7, 0, x, 7, 1, "oak_planks")
    w.set_door(1, 7, 0, facing="north", hinge="left")
    w.set_bed(4, 7, 0, facing="north", color="white")
    w.set(6, 7, 0, "torch")
    # row E: wall torch, lantern, lectern, composter
    w.fill(0, 11, 0, 0, 11, 1, "cobblestone")
    w.set(0, 10, 1, "wall_torch", {"facing": "south"})
    w.set(2, 10, 0, "lantern", {"hanging": "false"})
    w.set(4, 10, 0, "lectern", {"facing": "south", "has_book": "false"})
    w.set(6, 10, 0, "composter", {"level": "3"})
    # row F: smithing table, trapdoors (open / closed), bell, chest
    w.set(0, 13, 0, "smithing_table")
    w.set(2, 13, 0, "oak_trapdoor", {"facing": "south", "half": "bottom", "open": "true"})
    w.set(3, 13, 0, "oak_trapdoor", {"facing": "south", "half": "bottom", "open": "false"})
    w.set(5, 13, 0, "bell", {"attachment": "floor", "facing": "north"})
    w.set(7, 13, 0, "chest", {"facing": "south"})
    # row G: more workstations
    w.set(0, 16, 0, "blast_furnace", {"facing": "south", "lit": "false"})
    w.set(2, 16, 0, "barrel", {"facing": "up"})
    w.set(4, 16, 0, "cartography_table")
    w.set(6, 16, 0, "grindstone", {"face": "floor", "facing": "south"})
    # row H
    w.set(0, 19, 0, "stonecutter", {"facing": "south"})
    w.set(2, 19, 0, "loom", {"facing": "south"})
    w.set(4, 19, 0, "fletching_table")
    w.set(6, 19, 0, "cobblestone_wall")
    w.set(7, 19, 0, "cobblestone_wall")
    for x, b in ((1, "short_grass"), (3, "poppy"), (5, "dandelion"), (7, "tall_grass")):
        w.set(x, -2, 0, b, {"half": "lower"} if b == "tall_grass" else None)
    w.set(7, -2, 1, "tall_grass", {"half": "upper"})
    coll = new_collection(scene, "set")
    w.build(coll)
    print("blocks_shapes faces:", w.last_face_count)
    quick.camera(scene, (9.4, -14.0, 20.5), (3.6, 7.6, 0.3), lens=31)
    print("wrote", quick.render(scene, "blocks_shapes"))


def _closeup(name, cam, target, lens=50, preset="day"):
    """Scratch close-up of the shapes layout from a chosen camera (for checking details)."""
    from . import quick

    scene = bpy.context.scene
    quick.camera(scene, cam, target, lens=lens)
    print("wrote", quick.render(scene, name))


if __name__ == "__main__":
    import sys

    which = sys.argv[1:] or ["swatch", "shapes"]
    if "swatch" in which:
        _swatch()
    if "shapes" in which or "close" in which:
        _shapes()
    if "close" in which:
        _closeup("set_dbg_a", (3.2, -5.5, 3.2), (3.2, 1.0, 0.5), lens=30)
        _closeup("set_dbg_b", (4.0, 2.0, 3.5), (3.2, 8.5, 0.6), lens=30)
        _closeup("set_dbg_c", (4.5, 7.5, 3.6), (3.6, 12.5, 0.5), lens=30)
        _closeup("set_dbg_d", (4.0, 12.5, 4.5), (3.6, 18.5, 0.3), lens=30)
