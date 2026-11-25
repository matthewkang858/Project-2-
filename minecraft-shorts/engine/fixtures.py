"""FIXTURES (docstring is written at the end of the build: see the bottom of the work order)."""
import math
import types

import bpy
import numpy as np

from . import blocks as _blocks
from . import mcassets as mc

FPS = 24
TICK = FPS / 20.0                    # film frames per game tick

# ---- ChestModel.createSingleBodyLayer / createDoubleBody*Layer, ChestRenderer.submit, ChestLidController.tickLid
CHEST_TEX = (64, 64)                 # LayerDefinition.create(mesh, 64, 64); entity/chest/normal[_left|_right].png
CHEST_BASE = (1.0, 0.0, 1.0, 14.0, 10.0, 14.0, 0, 19)     # "bottom": addBox(1, 0, 1, 14, 10, 14), texOffs(0, 19)
CHEST_LID = (1.0, 9.0, 1.0, 14.0, 5.0, 14.0, 0, 0)        # "lid": addBox(1, 0, 0, 14, 5, 14) at offset(0, 9, 1)
CHEST_LOCK = (7.0, 7.0, 15.0, 2.0, 4.0, 1.0, 0, 0)        # "lock": addBox(7, -2, 14, 2, 4, 1) at offset(0, 9, 1)
CHEST_PIVOT = (8.0, 9.0, 1.0)        # the lid's PartPose.offset(0, 9, 1): the hinge line y = 9, z = 1 (model pixels)
CHEST_LID_STEP = 0.1                 # ChestLidController.tickLid: openness +- 0.1 per tick
CHEST_OPEN_TICKS = 10                # so 10 ticks = 12 frames from shut to open
CHEST_LID_ANGLE = math.pi / 2.0      # ChestModel.setupAnim: lid.xRot = -(open * 1.5707964)
CHEST_SEAM = 0.02                    # model pixels the lid's sides stand proud of the base (see NOT THE GAME)
# ---- Hopper.SUCK_AABB, HopperBlockEntity.MOVE_ITEM_SPEED, HopperBlock shape, ItemEntity
HOPPER_COOLDOWN_TICKS = 8            # HopperBlockEntity.MOVE_ITEM_SPEED: setCooldown(8) after any transfer
HOPPER_SUCK = (11.0 / 16.0, 2.0)     # Hopper.SUCK_AABB = Block.column(16, 11, 32): from the bowl's floor to the top
#                                      of the block ABOVE the hopper, the whole column wide
HOPPER_BOWL_FLOOR = 11.0 / 16.0      # models/block/hopper.json: the bowl's floor is the top of box (0, 10, 0)-(16, 11, 16)
HOPPER_BOWL_HALF = 6.0 / 16.0        # ... and its walls are 2 px thick: the hollow is 12 px wide
ITEM_SIZE = 0.25                     # EntityType.ITEM: 0.25 x 0.25
ITEM_GRAVITY, ITEM_DRAG = 0.04, 0.98     # ItemEntity.getDefaultGravity; tick(): velocity * 0.98 after the move
# ---- FallingBlock, FallingBlockEntity, AnvilBlock
FALL_DELAY_TICKS = 2                 # FallingBlock.getDelayAfterPlace: ticks from losing its support to becoming an entity
FALL_GRAVITY, FALL_DRAG = 0.04, 0.98     # FallingBlockEntity.getDefaultGravity; Entity.getAirDrag (velocity * 0.98 per tick)
ANVIL_DAMAGE_PER_BLOCK = 2.0         # AnvilBlock.FALL_DAMAGE_PER_DISTANCE (falling(): setHurtsEntities(2.0f, 40))
ANVIL_DAMAGE_MAX = 40                # AnvilBlock.FALL_DAMAGE_MAX
ANVIL_CHIP = (0.05, 0.05)            # FallingBlockEntity.causeFallDamage: nextFloat() < 0.05 + ceil(fall - 1) * 0.05
ANVIL_STAGES = ("anvil", "chipped_anvil", "damaged_anvil", None)     # AnvilBlock.damage(state); None = it breaks
FALLING_ENTITY_WIDTH = 0.98          # EntityType.FALLING_BLOCK: 0.98 x 0.98
# ---- FluidRenderer, FlowingFluid, WaterFluid, Entity
FLUID_SOURCE_HEIGHT = 8.0 / 9.0      # FluidRenderer.MAX_FLUID_HEIGHT 0.8888889 = FluidState.getOwnHeight of amount 8
FLUID_INSET = 0.001                  # FluidRenderer: tops are lowered and sides moved in by 0.001
FLUID_HEAVY = (0.8, 10.0)            # addWeightedHeight: a neighbour 0.8 or higher counts ten times in a corner's mean
WATER_PUSH = 0.014                   # Entity.WATER_FLOW_SCALE: blocks per tick^2 a current adds to a mob standing in it
WATER_DRAG = 0.8                     # LivingEntity.getWaterSlowDown: horizontal velocity * 0.8 per tick in water
WATER_SLIDE_SPEED = WATER_PUSH / (1.0 - WATER_DRAG) * 20.0     # 1.4 blocks/s: where push and drag balance
# ---- this module's look choices (see MEASURED in the docstring)
WATER_ROUGHNESS, WATER_SPECULAR = 0.12, 0.5      # the values engine.blocks gives its own (static) water
LAVA_EMISSION = 3.0                  # engine.blocks.EMISSIVE["block/lava_still"]
LAVA_LIGHT_COLOR = (1.0, 0.60, 0.30)
LAVA_WATTS_PER_BLOCK = 60.0          # area-light watts per block of lava surface
LAVA_LIGHT_LIFT = 0.02               # the light sits this far above the lava surface

_DIR = mc.DIR_BLENDER
HORIZ = ("north", "east", "south", "west")           # clockwise seen from above
_YAW = {"south": 0.0, "east": math.pi / 2.0, "north": math.pi, "west": -math.pi / 2.0}   # model front = south = -Y


# ----------------------------------------------------------------------------------------------------
# where things are built: the village builder (inside an edit hook), a built Village, or site(...)
# ----------------------------------------------------------------------------------------------------
def site(collection, world=None):
    """A stand-alone place to build fixtures in (no village): site(collection, blocks.World()).world / .collection."""
    return types.SimpleNamespace(collection=collection, world=world if world is not None else _blocks.World(),
                                 cutaways={}, sets={}, anchors={}, lights={})


def _where(where):
    """(world, collection, village-like, builder | None) of a builder (edit hook), a Village or a site()."""
    if hasattr(where, "w") and hasattr(where, "v"):
        return where.w, where.v.collection, where.v, where
    if hasattr(where, "world") and hasattr(where, "collection"):
        return where.world, where.collection, where, None
    raise TypeError("fixtures: expected the village builder (inside an edit hook), a Village or fixtures.site(), "
                    "not %r" % (where,))


def claim(world, cells):
    """Cells that stay in the World (solid: particles, falls and paths know them) but that World.build() must not
    draw, because an object of this module draws them. Harmless after the mesh is built."""
    skip = getattr(world, "_fixtures_skip", None)
    if skip is None:
        skip = world._fixtures_skip = set()
        inner = world.build

        def build(collection, name="world", skip=()):
            return inner(collection, name, skip=set(skip) | world._fixtures_skip)

        world.build = build
    skip.update(tuple(int(c) for c in cell) for cell in cells)


def _cell(cell):
    return tuple(int(math.floor(c + 1e-9)) for c in cell)


def _unique(name):
    base, n = name, 1
    while bpy.data.objects.get(name) is not None:
        n += 1
        name = "%s_%d" % (base, n)
    return name


# ----------------------------------------------------------------------------------------------------
# keyframe plumbing: every channel is rewritten whole from a record, so calls can be made in any order
# ----------------------------------------------------------------------------------------------------
def _fcurve(idb, path, index=0):
    ad = idb.animation_data or idb.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(idb.name + "_fix")
    return ad.action.fcurve_ensure_for_datablock(idb, path, index=index)


def _keys(idb, path, frames, values, interp="CONSTANT", index=0, cycle=False):
    """Replace a channel by these keys (one interpolation mode, or a list of modes); cycle repeats them for ever."""
    fc = _fcurve(idb, path, index)
    kps = fc.keyframe_points
    while len(kps):
        kps.remove(kps[len(kps) - 1], fast=True)
    for m in list(fc.modifiers):
        fc.modifiers.remove(m)
    n = len(frames)
    if n:
        kps.add(n)
        co = np.empty(2 * n, dtype=np.float32)
        co[0::2] = frames
        co[1::2] = values
        kps.foreach_set("co", co)
        for i, kp in enumerate(kps):
            kp.interpolation = interp if isinstance(interp, str) else interp[i]
        if cycle:
            mod = fc.modifiers.new(type="CYCLES")
            mod.mode_before = mod.mode_after = "REPEAT"
    fc.update()
    return fc


def _state_at(events, frame, default):
    """Value of [(frame, value), ...] at `frame` (the latest entry at or before it; later entries win ties)."""
    best, out = None, default
    for f, v in events:
        if f <= frame + 1e-9 and (best is None or f >= best):
            best, out = f, v
    return out


class _Presence:
    """Which of some objects is rendered when: `state` (a key of `objects`, or None = nothing) AND `shown` (the
    per-shot switch a films.lookdev.Stage flips through show()). CONSTANT keys on integer frames."""

    def __init__(self, objects, initial):
        self.objects = dict(objects)          # state key -> Object
        self.initial = initial                # the state before the first event
        self.states = []                      # [(frame, key | None)]
        self.shown = []                       # [(frame, bool)]

    def set(self, frame, key):
        frame = int(math.ceil(frame - 1e-6))
        self.states = [s for s in self.states if s[0] != frame] + [(frame, key)]
        self.rekey()

    def forget(self, frame_from):
        self.states = [s for s in self.states if s[0] < frame_from]

    def show(self, frame, visible=True):
        frame = int(frame)
        self.shown = [s for s in self.shown if s[0] != frame] + [(frame, bool(visible))]
        self.rekey()

    def state_at(self, frame):
        return _state_at(self.states, frame, self.initial)

    def rekey(self):
        frames = sorted({f for f, _k in self.states} | {f for f, _v in self.shown})
        for key, ob in self.objects.items():
            first = self.initial == key
            for path in ("hide_render", "hide_viewport"):
                if not frames:
                    setattr(ob, path, not first)
                    if ob.animation_data is not None and ob.animation_data.action is not None:
                        _keys(ob, path, [], [])
                    continue
                fs = [min(frames[0], 1) - 1] + frames
                vals = [0.0 if first else 1.0]
                for f in frames:
                    on = _state_at(self.shown, f, True) and self.state_at(f) == key
                    vals.append(0.0 if on else 1.0)
                setattr(ob, path, not first)
                _keys(ob, path, fs, vals, "CONSTANT")


# ----------------------------------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------------------------------
def _material_for(block_id):
    def f(q):
        return _blocks.block_material(q.texture, mc.block_tint(block_id, q.tintindex), shade=getattr(q, "shade", None))
    return f


def _entity_material(texture):
    return mc.material(texture, alpha="OPAQUE")


def animation_of(texture):
    """(number of images in the strip, the order they are shown in, game ticks each is shown) of an animated game
    texture, from its .png.mcmeta: block/water_still (32, 0..31, 2), block/lava_still (20, 0..19..1, 2)."""
    arr = mc.texture_array(texture)
    side = arr.shape[1]
    from PIL import Image

    full = Image.open(mc.texture_path(texture))
    count = max(1, full.size[1] // side)
    anim = mc.texture_meta(texture).get("animation") or {}
    time = int(anim.get("frametime", 1))
    order = anim.get("frames")
    if order:
        order = [int(f["index"]) if isinstance(f, dict) else int(f) for f in order]
    else:
        order = list(range(count))
    return count, order, time


def _strip_frame(texture, index):
    """Image number `index` of an animated strip as an HxWx4 uint8 array."""
    from PIL import Image

    full = np.array(Image.open(mc.texture_path(texture)).convert("RGBA"), dtype=np.uint8)
    side = full.shape[1]
    return full[index * side:(index + 1) * side, :side]


def _fluid_material(kind, texture, index, tint=None):
    """The material of one image of an animated fluid texture (cached by name)."""
    name = "fx/%s#%02d" % (texture.split("/")[-1], index)
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    arr = _strip_frame(texture, index)
    if tint is not None:
        out = arr.astype(np.float32)
        for c in range(3):
            out[..., c] *= tint[c] / 255.0
        arr = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    img = mc.image_from_array(name, arr)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    tex.extension = "REPEAT"
    tex.location = (-500, 200)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if kind == "lava":
        bsdf.inputs["Roughness"].default_value = 0.9
        bsdf.inputs["Specular IOR Level"].default_value = 0.08
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = LAVA_EMISSION
        mat.cycles.emission_sampling = "NONE"        # it glows for the camera; the lighting is the lava light's
    else:
        bsdf.inputs["Roughness"].default_value = WATER_ROUGHNESS
        bsdf.inputs["Specular IOR Level"].default_value = WATER_SPECULAR
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    mat["mc_texture"] = texture
    mat["mc_alpha"] = "OPAQUE" if kind == "lava" else "BLEND"
    return mat


def texture_schedule(order, frametime):
    """(period in film frames, [image index shown on frame 1, 2, ... period]) of an animated texture at 24 fps:
    frame f shows the game tick floor((f - 1) * 5 / 6), and tick t shows order[(t // frametime) % len(order)]."""
    ticks = len(order) * frametime
    total = ticks * 5 // math.gcd(ticks, 5)            # game ticks until tick grid and frame grid line up again
    period = total * 6 // 5
    return period, [order[(((f - 1) * 5 // 6) // frametime) % len(order)] for f in range(1, period + 1)]


def _cycle_visibility(objects, shown):
    """objects[i] is rendered on the frames whose entry in `shown` is i; the list repeats for ever."""
    period = len(shown)
    for i, ob in objects.items():
        frames, values = [], []
        last = None
        for f in range(1, period + 1):
            hide = 0.0 if shown[f - 1] == i else 1.0
            if hide != last:
                frames.append(f)
                values.append(hide)
                last = hide
        frames.append(period + 1)
        values.append(values[0])
        for path in ("hide_render", "hide_viewport"):
            setattr(ob, path, bool(values[0]))
            _keys(ob, path, frames, values, "CONSTANT", cycle=True)


# ----------------------------------------------------------------------------------------------------
# CHEST
# ----------------------------------------------------------------------------------------------------
def chest_parts(kind="single"):
    """(base quads, lid + lock quads, texture) of a chest half in model pixels, front toward SOUTH (+z), as
    ChestModel builds it. kind: 'single' | 'right' (open on its east side: the WEST block of a south-facing double
    chest) | 'left' (open on its west side)."""
    tex = "entity/chest/normal" + {"single": "", "left": "_left", "right": "_right"}[kind]
    tw, th = CHEST_TEX
    if kind == "single":
        x, w, lx, lw, skip, free = 1.0, 14.0, 7.0, 2.0, None, (1.0, 15.0)
    elif kind == "right":            # createDoubleBodyRightLayer: boxes (1 .. 16), no EAST faces, lock at x 15 .. 16
        x, w, lx, lw, skip, free = 1.0, 15.0, 15.0, 1.0, "east", (1.0,)
    else:                            # createDoubleBodyLeftLayer: boxes (0 .. 15), no WEST faces, lock at x 0 .. 1
        x, w, lx, lw, skip, free = 0.0, 15.0, 0.0, 1.0, "west", (15.0,)
    _bx, by, bz, _bw, bh, bd, bu, bv = CHEST_BASE
    _lx, ly, lz, _lw, lh, ld, lu, lv = CHEST_LID
    _kx, ky, kz, _kw, kh, kd, ku, kv = CHEST_LOCK
    base = [q for q in mc.entity_box(x, by, bz, w, bh, bd, bu, bv, tw, th, tex) if q.facing != skip]
    lid = [q for q in mc.entity_box(x, ly, lz, w, lh, ld, lu, lv, tw, th, tex) if q.facing != skip]
    e = CHEST_SEAM
    for q in lid:                    # the lid's free sides stand a hair proud of the base (they share 1 px of height)
        pts = []
        for px, py, pz in q.pts:
            for fx_ in free:
                if abs(px - fx_) < 1e-6:
                    px += e if fx_ > 8.0 else -e
            if abs(pz - 1.0) < 1e-6:
                pz -= e
            elif abs(pz - 15.0) < 1e-6:
                pz += e
            pts.append((px, py, pz))
        q.pts = pts
    lock = [q for q in mc.entity_box(lx, ky, kz, lw, kh, kd, ku, kv, tw, th, tex) if q.facing != skip]
    return base, lid + lock, tex


def lid_openness(openness):
    """ChestRenderer.submit: the drawn openness of a lid whose controller is at `openness` (0..1): 1 - (1 - o)^3."""
    o = 1.0 - max(0.0, min(1.0, openness))
    return 1.0 - o * o * o


def _shift(quads, dx):
    out = []
    for q in quads:
        out.append(mc.Quad([(p[0] + dx, p[1], p[2]) for p in q.pts], q.uvs, q.texture, facing=q.facing))
    return out


class Chest:
    """A chest block entity: .object (the base; origin = bottom centre of its first cell), .lid (hinged child, None
    for a static chest), .cells, .facing, .kind ('single' | 'double'), .name."""

    def __init__(self, name, base, lid, cells, facing, kind):
        self.name, self.object, self.lid, self.cells, self.facing, self.kind = name, base, lid, cells, facing, kind
        self.cell = cells[0]
        self._events = []                 # [(frame, should be open)]
        self._initial = False

    def __repr__(self):
        return "<Chest %s %s facing %s at %s>" % (self.kind, self.name, self.facing, self.cells)

    @property
    def center(self):
        """World point in the middle of the chest (a look / focus target)."""
        n = float(len(self.cells))
        return tuple(sum(c[i] for c in self.cells) / n + (0.5 if i < 2 else 0.45) for i in range(3))

    def _need_lid(self):
        if self.lid is None:
            raise ValueError("%s is a static chest (animated=False): it has no lid to move" % self.name)

    def openness_at(self, frame):
        """The lid controller's openness (0 shut .. 1 open, linear) at `frame`, from the open() / close() calls."""
        o = 1.0 if self._initial else 0.0
        t = None
        for f, want in sorted(self._events):
            if f > frame:
                break
            if t is not None:
                o = max(0.0, min(1.0, o + (1.0 if target else -1.0) * (f - t) / (CHEST_OPEN_TICKS * TICK)))
            t, target = f, want
        if t is not None:
            o = max(0.0, min(1.0, o + (1.0 if target else -1.0) * (frame - t) / (CHEST_OPEN_TICKS * TICK)))
        return o

    def angle_at(self, frame):
        """The lid's angle in radians (0 shut, pi / 2 open) at `frame`."""
        return lid_openness(self.openness_at(frame)) * CHEST_LID_ANGLE

    def _rekey(self):
        ev = sorted(self._events)
        if not ev:
            return
        span = int(math.ceil(CHEST_OPEN_TICKS * TICK)) + 1
        frames = set()
        for f, _w in ev:
            frames.update(range(int(math.floor(f)) - 1, int(math.floor(f)) + span + 1))
            frames.add(f)
        frames = sorted(frames)
        _keys(self.lid, "rotation_euler", frames, [-self.angle_at(f) for f in frames], "LINEAR", index=0)

    def open(self, frame):
        """The lid starts to open ON `frame` (the game: +0.1 openness per tick, drawn as 1 - (1 - o)^3: it flies up
        and settles). Returns the frame it is fully open (frame + 12)."""
        self._need_lid()
        self._events = [e for e in self._events if e[0] != frame] + [(float(frame), True)]
        self._rekey()
        return frame + int(math.ceil(CHEST_OPEN_TICKS * TICK))

    def close(self, frame):
        """The lid starts to close ON `frame` (it lingers open, then drops shut). Returns the frame it is shut."""
        self._need_lid()
        self._events = [e for e in self._events if e[0] != frame] + [(float(frame), False)]
        self._rekey()
        return frame + int(math.ceil(CHEST_OPEN_TICKS * TICK))

    def set_open(self, is_open=True):
        """The chest is open (or shut) from before the film starts: no movement."""
        self._need_lid()
        self._initial = bool(is_open)
        self.lid.rotation_euler[0] = -(CHEST_LID_ANGLE if is_open else 0.0)
        self._rekey()

    def objects(self):
        """Every object of the chest."""
        return [self.object] + ([self.lid] if self.lid is not None else [])


_CHEST_MESHES = {}


def _alive(idb):
    try:
        return idb is not None and bool(idb.name)
    except ReferenceError:
        return False


def chest(where, cell, facing="south", animated=True, partner=None, name=None):
    """A chest at `cell` with its latch toward `facing`, as the game's chest model draws it (entity/chest/normal.png).
    partner = the neighbouring cell of a DOUBLE chest (to the left or right of the front). animated=False: one
    static object (the mesh is shared by all static chests of that kind: use it for set dressing in quantity).
    Returns a Chest: open(frame) / close(frame) / set_open()."""
    world, coll, _v, _b = _where(where)
    if facing not in _YAW:
        raise ValueError("chest facing must be north / east / south / west, not %r" % (facing,))
    a = _cell(cell)
    cells = [a]
    parts = [("single", 0.0)]
    if partner is not None:
        p = _cell(partner)
        ccw = HORIZ[(HORIZ.index(facing) - 1) % 4]              # ChestBlock: a RIGHT half joins counter-clockwise
        d = tuple(p[i] - a[i] for i in range(3))
        if d == _DIR[ccw]:
            cells = [a, p]
        elif d == tuple(-c for c in _DIR[ccw]):
            cells = [p, a]
        else:
            raise ValueError("a double chest facing %s needs its two cells side by side along its front, not %s and %s"
                             % (facing, a, p))
        parts = [("right", 0.0), ("left", 16.0)]
    kind = "double" if partner is not None else "single"
    name = _unique(name or ("chest_%d_%d_%d" % cells[0]))
    base_q, lid_q = [], []
    for part, dx in parts:
        b, l, _tex = chest_parts(part)
        base_q += _shift(b, dx)
        lid_q += _shift(l, dx)

    def material_for(q):
        return _entity_material(q.texture)

    lid = None
    if animated:
        base = mc.quads_object(name, base_q, material_for, coll, origin=(8.0, 0.0, 8.0))
        lid = mc.quads_object(name + "_lid", lid_q, material_for, coll, origin=CHEST_PIVOT)
        lid.parent = base
        lid.location = ((CHEST_PIVOT[0] - 8.0) / 16.0, -(CHEST_PIVOT[2] - 8.0) / 16.0, CHEST_PIVOT[1] / 16.0)
        lid.rotation_mode = "XYZ"
    else:
        me = _CHEST_MESHES.get(kind)
        if not _alive(me):
            tmp = mc.quads_object("chest_static_" + kind, base_q + lid_q, material_for, None, origin=(8.0, 0.0, 8.0))
            me = _CHEST_MESHES[kind] = tmp.data
            bpy.data.objects.remove(tmp)
        base = bpy.data.objects.new(name, me)
        coll.objects.link(base)
    base.location = (cells[0][0] + 0.5, cells[0][1] + 0.5, float(cells[0][2]))
    base.rotation_mode = "XYZ"
    base.rotation_euler = (0.0, 0.0, _YAW[facing])
    base["mc_block"] = "chest"
    for c, part in zip(cells, ("right", "left") if kind == "double" else ("single",)):
        world.set(c[0], c[1], c[2], "chest", {"facing": facing, "type": part})
    claim(world, cells)
    return Chest(name, base, lid, cells, facing, kind)


# ----------------------------------------------------------------------------------------------------
# single blocks as their own objects (what moves, appears or falls)
# ----------------------------------------------------------------------------------------------------
_BLOCK_MESHES = {}


def _block_object(block_id, props, cell, collection, name):
    """One block as an object (origin = the cell's min corner), with the model, random variant, texture and tint
    engine.blocks gives that state at that cell; meshes are shared between equal blocks."""
    block_id = block_id.replace("minecraft:", "")
    props = {k: (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in (props or {}).items()}
    if not mc.has_blockstate(block_id):
        raise ValueError("no block called %r in the game files" % (block_id,))
    nv = mc.variant_count(block_id, props)
    variant = _blocks.pos_hash(cell[0], cell[1], cell[2]) % nv if nv > 1 else 0
    key = (block_id, tuple(sorted(props.items())), variant)
    me = _BLOCK_MESHES.get(key)
    if not _alive(me):
        quads = list(mc.bake_block(block_id, props, variant))
        if not quads:
            raise ValueError("%r has no block model (the game draws it with an entity model): fixtures.block cannot "
                             "build it" % (block_id,))
        tmp = mc.quads_object("fx_" + block_id, quads, _material_for(block_id), None, origin=(0.0, 0.0, 16.0))
        me = _BLOCK_MESHES[key] = tmp.data
        bpy.data.objects.remove(tmp)
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    ob.location = (float(cell[0]), float(cell[1]), float(cell[2]))
    ob["mc_block"] = block_id
    return ob


class Block:
    """One block as its own object: .object (origin = the min corner of its cell), .block_id, .props, .cell (where
    it stands now: the landing cell after fall()), .name; show(frame, visible) for a Stage's per-shot switch
    (st.cast[blk.name] = blk; st.use(shot, blk)); place_at(frame) / remove(frame); .drop = the dict of its fall()."""

    def __init__(self, name, ob, block_id, props, cell, world, collection, frame=None):
        self.name, self.object, self.block_id, self.props = name, ob, block_id, dict(props or {})
        self.cell, self.start_cell, self.world, self.collection = cell, cell, world, collection
        self.drop = None
        self._variants = {block_id: ob}
        self._presence = _Presence(self._variants, block_id if frame is None else None)
        if frame is not None:
            self._presence.set(frame, block_id)
        else:
            self._presence.rekey()

    def __repr__(self):
        return "<Block %s %s at %s>" % (self.block_id, self.name, self.cell)

    @property
    def center(self):
        """World point in the middle of the cell it stands in now."""
        return (self.cell[0] + 0.5, self.cell[1] + 0.5, self.cell[2] + 0.5)

    def objects(self):
        """Every object that draws this block (its states after a fall included)."""
        return list(self._variants.values())

    def show(self, frame, visible=True):
        """Per-shot visibility (what Stage.finish() calls); the block's own appearing / changing still applies."""
        self._presence.show(frame, visible)

    def place_at(self, frame):
        """The block is there from `frame` on (not rendered before): a block that is placed during a shot."""
        self._presence.states = [s for s in self._presence.states if s[0] >= frame]
        self._presence.initial = None
        self._presence.set(frame, self.block_id)

    def remove(self, frame):
        """The block is gone from `frame` on."""
        self._presence.set(frame, None)

    def state_at(self, frame):
        """Block id it is drawn as at `frame` ('anvil', then 'chipped_anvil' after a chipping landing), or None."""
        return self._presence.state_at(frame)

    def _variant(self, block_id, cell):
        ob = self._variants.get(block_id)
        if ob is None:
            ob = _block_object(block_id, self.props, cell, self.collection, _unique(self.name + "_" + block_id))
            self._variants[block_id] = ob
            self._presence.objects[block_id] = ob
        ob.location = (float(cell[0]), float(cell[1]), float(cell[2]))
        return ob


def block(where, block_id, cell, props=None, frame=None, name=None):
    """One block as its own object at `cell`, drawn exactly as engine.blocks would draw it there (model, variant,
    tint, facing ...). frame=None: there from the start; frame=f: it appears ON f (a block placed in shot: the
    twelfth anvil, the second bed). Use it only for what moves, appears or falls: static blocks belong in the
    village mesh (b.w.set in the edit hook). Returns a Block."""
    world, coll, _v, _b = _where(where)
    cell = _cell(cell)
    block_id = block_id.replace("minecraft:", "")
    name = _unique(name or ("%s_%d_%d_%d" % ((block_id,) + cell)))
    ob = _block_object(block_id, props, cell, coll, name)
    world.set(cell[0], cell[1], cell[2], block_id, props)
    claim(world, [cell])
    return Block(name, ob, block_id, props, cell, world, coll, frame=frame)


def bed(where, foot_cell, facing="north", color="red", frame=None, name=None):
    """A bed as two Block objects (foot at `foot_cell`, pillow one cell further in `facing`) that can appear ON a
    frame: the second bed that is suddenly there. Returns dict(foot, head (Blocks), pos, yaw, show(frame, visible))
    with pos / yaw as Village.beds gives them (Character.lie_down(frame, pos, yaw))."""
    world, _coll, _v, _b = _where(where)
    fx_, fy, fz = _cell(foot_cell)
    dx, dy, _dz = _DIR[facing]
    name = name or ("bed_%d_%d_%d" % (fx_, fy, fz))
    foot = block(where, color + "_bed", (fx_, fy, fz), {"facing": facing, "part": "foot", "occupied": "false"},
                 frame=frame, name=name + "_foot")
    head = block(where, color + "_bed", (fx_ + dx, fy + dy, fz), {"facing": facing, "part": "head",
                                                                 "occupied": "false"}, frame=frame, name=name + "_head")

    def show(f, visible=True):
        foot.show(f, visible)
        head.show(f, visible)

    top = fz + 9.0 / 16.0
    return dict(foot=foot, head=head, pos=(fx_ + 0.5 + dx * 0.5, fy + 0.5 + dy * 0.5, top),
                yaw=math.atan2(dx, -dy), facing=facing, show=show, name=name)


# ----------------------------------------------------------------------------------------------------
# FALLING BLOCKS AND ANVILS
# ----------------------------------------------------------------------------------------------------
def fall_track(height, max_ticks=2000):
    """FallingBlockEntity.tick for a drop of `height` blocks: [(entity tick, distance fallen)] from (0, 0) to the
    tick it lands (the last entry is clipped to `height`). Per tick: velocity -= 0.04, move, velocity *= 0.98."""
    v, d = 0.0, 0.0
    out = [(0, 0.0)]
    for n in range(1, max_ticks + 1):
        v -= FALL_GRAVITY
        d -= v
        if d >= height - 1e-9:
            out.append((n, float(height)))
            return out
        out.append((n, d))
        v *= FALL_DRAG
    raise ValueError("a fall of %r blocks does not end" % (height,))


def fall_ticks(height):
    """Entity ticks a falling block needs for `height` blocks (15 blocks: 30 ticks = 1.5 s; 18: 33)."""
    return fall_track(height)[-1][0]


def fall_speed(height):
    """Blocks per tick it moves on the tick BEFORE it lands (the smear a landing frame shows): 15 blocks: 0.89."""
    tr = fall_track(height)
    return tr[-2][1] - tr[-3][1] if len(tr) > 2 else tr[-1][1]


def anvil_damage(height):
    """Half hearts a falling anvil deals to what it lands on after `height` blocks: min(floor(ceil(h - 1) * 2), 40);
    0 for a fall of one block or less. A pillager has 24: 13 blocks kill it; 17 when it wears a banner or a helmet
    (headgear takes a quarter off: not transcribed here, the story's own number)."""
    n = int(math.ceil(height - 1.0 - 1e-9))
    return 0 if n <= 0 else int(min(math.floor(n * ANVIL_DAMAGE_PER_BLOCK), ANVIL_DAMAGE_MAX))


def anvil_chip_chance(height):
    """Chance that a falling anvil is one stage more damaged when it lands: 0.05 + 0.05 * ceil(h - 1), only when it
    deals damage at all (a fall of more than one block). 15 blocks: 0.75; 18: 0.90; from 20 up: certain."""
    n = int(math.ceil(height - 1.0 - 1e-9))
    return 0.0 if anvil_damage(height) <= 0 else min(1.0, ANVIL_CHIP[0] + ANVIL_CHIP[1] * n)


_PARTIAL = ("dirt_path", "farmland", "soul_sand", "mud", "honey_block")


def landing_cell(world, cell_from):
    """(cell a falling block released at `cell_from` comes to rest in, block id it lands on): the cell above the
    first solid block under it. ValueError if there is none, or if that block is not a full block high (a dirt
    path, a slab, a chest ...: in the game a falling block that ends on one BREAKS and drops as an item)."""
    x, y, z0 = _cell(cell_from)
    for z in range(z0 - 1, z0 - 400, -1):
        if world.is_solid(x, y, z):
            bid, props = world.get(x, y, z)
            full = world.is_full_cube(x, y, z) or bid.endswith("glass") or bid.endswith("_leaves")
            if not full and not (bid.endswith("_slab") and props.get("type") in ("top", "double")):
                raise ValueError("a block falling from %s lands on %s at %s, which is not a full block high: in the "
                                 "game it breaks and drops as an item. Pave the landing (cobblestone) or pass land="
                                 % ((x, y, z0), bid, (x, y, z)))
            return (x, y, z + 1), bid
    raise ValueError("nothing solid under %s: the block would fall out of the world" % ((x, y, z0),))


def _as_block(thing, cell_from, where, props, frame_visible=None):
    if isinstance(thing, Block):
        return thing
    if isinstance(thing, str):
        if where is None or cell_from is None:
            raise ValueError("fall('%s', ...) needs cell_from and world= (the builder, the Village or a site)" % thing)
        return block(where, thing, cell_from, props, frame=frame_visible)
    if hasattr(thing, "object") and hasattr(thing, "cell") and hasattr(thing, "block_id"):
        raise TypeError("fall() moves fixtures.Block objects (fixtures.block / the id of a block); a %s keeps its own "
                        "visibility: make the block with fixtures.block instead" % type(thing).__name__)
    raise TypeError("fall(): expected a block id or a fixtures.Block, not %r" % (thing,))


def fall(block_or_id, cell_from=None, frame=1, world=None, hang=FALL_DELAY_TICKS, chip=None, seed=0, props=None,
         land=None, head=1.95):
    """A block falls as the game's falling-block entity. block_or_id = a fixtures.Block (it falls from where it
    stands) or a block id ('anvil', 'sand', 'gravel', 'chipped_anvil' ...: built at cell_from). frame = the frame it
    LOSES ITS SUPPORT (the plank is pulled away ON that frame): it hangs `hang` game ticks (the game: 2 = 2.4
    frames), then drops with the entity's gravity and drag, and stands as a block again in the first free cell
    above the solid block under it in `world` (the builder, the Village or a site; land=(x, y, z) names the
    landing cell yourself). chip: None / False = it lands as it was; True = an anvil lands one stage more damaged
    (anvil -> chipped_anvil -> damaged_anvil -> gone); 'game' = the game's own chance for that height, drawn from
    `seed`. Returns dict(block, frame_release, frame_drop (first frame it is seen lower), frame_land (first frame
    it stands: key hurt() / die() of what is under it HERE, the game deals the damage on landing), time_land (the
    exact, fractional frame), cell (where it stands), from_cell, height, ticks, speed (blocks per frame at the
    end), state (block id it lands as, None = broke), chipped, damage (half hearts), chance, head_frame (first
    frame its underside is at or below landing floor + `head`: 1.95 = a pillager's or player's head top),
    frame_at(z) (exact frame its underside passes height z), track [(frame, z of its underside)])."""
    where = world
    w = None
    if where is not None:
        w = where if isinstance(where, _blocks.World) else _where(where)[0]
    blk = _as_block(block_or_id, cell_from, where if not isinstance(where, _blocks.World) else None, props)
    start = blk.cell
    if land is None:
        if w is None:
            raise ValueError("fall() needs world= (to find where the block lands) or land=(x, y, z)")
        land_cell, _under = landing_cell(w, start)
    else:
        land_cell = _cell(land)
    height = float(start[2] - land_cell[2])
    if height <= 0:
        raise ValueError("%s at %s has nothing to fall into (it would land at %s)" % (blk.name, start, land_cell))
    track = fall_track(height)
    f0 = float(frame) + (hang - 1) * TICK                 # entity tick 0: the last tick it is still in place
    keys = [(f0 + n * TICK, start[2] - d) for n, d in track]
    time_land = keys[-1][0]
    frame_land = int(math.ceil(time_land - 1e-6))
    ob = blk.object
    frames = [k[0] for k in keys]
    if frames[0] > frame - 1:
        frames, values = [float(frame) - 1.0] + frames, [float(start[2])] + [k[1] for k in keys]
    else:
        values = [k[1] for k in keys]
    _keys(ob, "location", frames, values, "LINEAR", index=2)
    # what it lands as
    state = blk.block_id
    chance = anvil_chip_chance(height) if "anvil" in blk.block_id else 0.0
    chipped = False
    if chip == "game":
        chipped = bool(np.random.default_rng([int(seed), start[0] & 0xFFFF, start[1] & 0xFFFF, start[2] & 0xFFFF])
                       .random() < chance)
    elif chip:
        chipped = True
    if chipped:
        if blk.block_id not in ANVIL_STAGES:
            raise ValueError("only anvils chip when they land (%s does not)" % blk.block_id)
        state = ANVIL_STAGES[ANVIL_STAGES.index(blk.block_id) + 1]
    blk._presence.forget(frame_land)
    if state != blk.block_id:
        if state is not None:
            blk._variant(state, land_cell)
        blk._presence.set(frame_land, state)
    else:
        blk._presence.rekey()
    if w is not None:
        if w.block_id(*start) == blk.block_id:
            w.set(start[0], start[1], start[2], None)
        if state is not None:
            w.set(land_cell[0], land_cell[1], land_cell[2], state, blk.props)
            claim(w, [land_cell])
    blk.cell = land_cell

    def frame_at(z):
        if z >= keys[0][1]:
            return keys[0][0]
        for (fa, za), (fb, zb) in zip(keys, keys[1:]):
            if zb <= z <= za and za > zb:
                return fa + (fb - fa) * (za - z) / (za - zb)
        return keys[-1][0]

    drop_frame = int(math.ceil(keys[1][0] - 1e-6)) if len(keys) > 1 else frame_land
    out = dict(block=blk, frame_release=int(frame), frame_drop=drop_frame, frame_land=frame_land, time_land=time_land,
               cell=land_cell, from_cell=start, height=height, ticks=track[-1][0],
               speed=fall_speed(height) / TICK, state=state, chipped=chipped, damage=anvil_damage(height)
               if "anvil" in blk.block_id else 0, chance=chance, frame_at=frame_at,
               head_frame=int(math.ceil(frame_at(land_cell[2] + head) - 1e-6)), track=keys)
    blk.drop = out
    return out


def release(blocks, frame, world=None, chip=None, seed=0, hang=FALL_DELAY_TICKS, head=1.95):
    """Several blocks lose their support ON THE SAME FRAME (the twelve anvils when the pistons pull their planks
    back): each hangs `hang` ticks, then they drop together, every one its own object. blocks = fixtures.Block
    objects (fixtures.block(...) or shelf(...)). chip: None, True (all), 'game' (each by the game's chance, drawn
    from seed), a number (that many of them, chosen by seed), or a list: indices of the ones that chip, or one
    True / False per block. Returns the list of fall() dicts, in the order of `blocks`."""
    blocks = list(blocks)
    n = len(blocks)
    if chip is None or chip is False:
        flags = [False] * n
    elif chip is True:
        flags = [True] * n
    elif chip == "game":
        flags = ["game"] * n
    elif isinstance(chip, (int, np.integer)) and not isinstance(chip, bool):
        pick = set(np.random.default_rng([int(seed), 7919]).permutation(n)[:int(chip)].tolist())
        flags = [i in pick for i in range(n)]
    else:
        chip = list(chip)
        if len(chip) == n and all(isinstance(c, (bool, np.bool_)) for c in chip):
            flags = [bool(c) for c in chip]
        else:
            flags = [i in set(int(c) for c in chip) for i in range(n)]
    return [fall(b, frame=frame, world=world, hang=hang, chip=flags[i], seed=seed + i, head=head)
            for i, b in enumerate(blocks)]


def shelf(where, cells, block_id="anvil", props=None, frame=None):
    """Blocks standing in a row as their own objects (the anvils on their planks): [Block, ...] in the order of
    `cells`, ready for release(). props: one dict for all, or a list with one per cell."""
    cells = list(cells)
    out = []
    for i, c in enumerate(cells):
        p = props[i] if isinstance(props, (list, tuple)) else props
        out.append(block(where, block_id, c, p, frame=frame))
    return out


def strikes(drops, spots, half_width=0.3, height=1.95):
    """Who is under which falling block. drops = fall() dicts; spots = {name: (x, y, z feet)} (or a list of points).
    A mob of hit-box half width `half_width` is hit by a block whose 0.98-wide entity box overlaps its own when it
    lands (FallingBlockEntity.causeFallDamage: everything alive in its bounding box). Returns {name: dict(drop,
    frame_land (the game's damage frame), head_frame (first frame the block's underside is at or below the top of
    its head: z feet + height), damage)}; names that nothing lands on are left out."""
    items = spots.items() if isinstance(spots, dict) else enumerate(spots)
    out = {}
    reach = FALLING_ENTITY_WIDTH / 2.0 + half_width
    for name, p in items:
        best = None
        for d in drops:
            cx, cy = d["cell"][0] + 0.5, d["cell"][1] + 0.5
            if abs(p[0] - cx) < reach and abs(p[1] - cy) < reach and p[2] < d["from_cell"][2]:
                if best is None or d["time_land"] < best["time_land"]:
                    best = d
        if best is not None:
            z_head = (p[2] if len(p) > 2 else best["cell"][2]) + height
            out[name] = dict(drop=best, frame_land=best["frame_land"],
                             head_frame=int(math.ceil(best["frame_at"](z_head) - 1e-6)), damage=best["damage"])
    return out


def hold_anvil(player, stage=0, hand="right", frame=None):
    """Put an anvil in an engine.players Player's hand, as the game holds a block item (the block model at 0.375,
    turned 75 / 45 degrees: models/block/block.json display.thirdperson_righthand). stage 0 / 1 / 2 = anvil /
    chipped_anvil / damaged_anvil. The same as player.hold('anvil', hand, frame); returns the item object."""
    return player.hold(ANVIL_STAGES[int(stage)], hand=hand, frame=frame)


# ----------------------------------------------------------------------------------------------------
# HOPPER
# ----------------------------------------------------------------------------------------------------
def item_fall(height, velocity=(0.0, 0.0, 0.0), max_ticks=400):
    """ItemEntity.tick in free fall: [(tick, (east, north, up) offset)] until it has dropped `height` blocks (the
    last entry is clipped to -height: it lies there). Gravity 0.04, then the move, then velocity * 0.98."""
    vx, vy, vz = (float(c) for c in velocity)
    x = y = z = 0.0
    out = [(0, (0.0, 0.0, 0.0))]
    for tick in range(1, max_ticks + 1):
        vz -= ITEM_GRAVITY
        x, y, z = x + vx, y + vy, z + vz
        if z <= -height + 1e-9:
            out.append((tick, (x, y, -float(height))))
            return out
        out.append((tick, (x, y, z)))
        vx, vy, vz = vx * ITEM_DRAG, vy * ITEM_DRAG, vz * ITEM_DRAG
    raise ValueError("an item falling %r blocks never lands" % (height,))


class Hopper:
    """A hopper block and its 8-tick beat: .cell, .facing, .rim (z of its top), .bowl (z of the bowl's floor, where
    an item lies), .mouth (the point in the middle of the bowl's floor), .object (None when the block is part of the
    village mesh), .takes [(frame, item name)]."""

    def __init__(self, cell, facing, ob=None):
        self.cell, self.facing, self.object = cell, facing, ob
        self.rim = cell[2] + 1.0
        self.bowl = cell[2] + HOPPER_BOWL_FLOOR
        self.mouth = (cell[0] + 0.5, cell[1] + 0.5, self.bowl)
        self.takes = []
        self._free_at = -1e18              # film time (frames) from which the hopper can take the next item

    def __repr__(self):
        return "<Hopper facing %s at %s>" % (self.facing, self.cell)

    def busy(self, frame, ticks=HOPPER_COOLDOWN_TICKS):
        """The hopper moved an item ON `frame` (into the chest under it, say): it takes nothing for `ticks` game
        ticks (the game: 8). A hopper that still holds items does this every 8 ticks; an item that arrives during
        the pause LANDS in the bowl and lies there until the pause is over."""
        self._free_at = max(self._free_at, float(frame) + ticks * TICK)

    def _inside(self, pos):
        """Is an item entity at `pos` (the bottom centre of its 0.25 box) in the hopper's suck box?"""
        cx, cy, cz = self.cell
        half = ITEM_SIZE / 2.0
        return (cx - half < pos[0] < cx + 1.0 + half and cy - half < pos[1] < cy + 1.0 + half
                and pos[2] < cz + HOPPER_SUCK[1] and pos[2] + ITEM_SIZE > cz + HOPPER_SUCK[0])

    def _floor(self, x, y):
        """Height an item at (x, y) comes to rest on: the bowl's floor, or the rim when it overlaps a wall."""
        cx, cy = self.cell[0] + 0.5, self.cell[1] + 0.5
        reach = HOPPER_BOWL_HALF - ITEM_SIZE / 2.0
        return self.bowl if abs(x - cx) <= reach + 1e-9 and abs(y - cy) <= reach + 1e-9 else self.rim

    def plan(self, drops):
        """What the hopper does with item entities released over it. drops = [(release frame, (x, y, z) start,
        (vx, vy, vz) blocks per tick)]. Each game tick an item moves (ItemEntity) and then, if the hopper's pause is
        over and the item's box is in the suck box (from the bowl's floor to the top of the block above the hopper),
        it is taken: ONE item entity per 8 ticks. Returns one dict per drop: track [(frame, (x, y, z))] up to the
        frame it is taken, frame (the first film frame it is gone), time (exact), landed (frame it came to rest in
        the bowl, None when it was taken in the air), waited (ticks it lay there), taken_at (x, y, z)."""
        sims = []
        for i, (f0, start, vel) in enumerate(drops):
            sims.append(dict(i=i, f0=float(f0), pos=[float(c) for c in start], vel=[float(c) for c in vel], tick=0,
                             track=[(float(f0), tuple(float(c) for c in start))], done=False, landed=None, rest=0))
        out = [None] * len(sims)
        free = self._free_at
        guard = 0
        while any(not s["done"] for s in sims):
            guard += 1
            if guard > 20000:
                raise RuntimeError("hopper plan does not end (an item never reaches the hopper at %s)" % (self.cell,))
            # the next game tick of whichever item is earliest in film time
            s = min((s for s in sims if not s["done"]), key=lambda s: s["f0"] + (s["tick"] + 1) * TICK)
            s["tick"] += 1
            t = s["f0"] + s["tick"] * TICK
            p, v = s["pos"], s["vel"]
            floor = self._floor(p[0], p[1])
            on_ground = s["landed"] is not None
            if not on_ground:
                v[2] -= ITEM_GRAVITY
                p[0], p[1], p[2] = p[0] + v[0], p[1] + v[1], p[2] + v[2]
                inside_column = self.cell[0] < p[0] < self.cell[0] + 1 and self.cell[1] < p[1] < self.cell[1] + 1
                if inside_column and p[2] <= floor:
                    p[2], v[2] = floor, 0.0
                    s["landed"] = t
                    v[0] = v[1] = 0.0
                elif p[2] < self.cell[2] - 8:
                    raise ValueError("an item released at %s misses the hopper at %s" % (drops[s["i"]][1], self.cell))
                else:
                    v[0], v[1], v[2] = v[0] * ITEM_DRAG, v[1] * ITEM_DRAG, v[2] * ITEM_DRAG
            else:
                s["rest"] += 1
            s["track"].append((t, (p[0], p[1], p[2])))
            if t >= free - 1e-6 and self._inside(p):
                s["done"] = True
                free = t + HOPPER_COOLDOWN_TICKS * TICK
                out[s["i"]] = dict(track=s["track"], time=t, frame=int(math.ceil(t - 1e-6)),
                                   landed=None if s["landed"] is None or s["landed"] >= t - 1e-6
                                   else int(math.ceil(s["landed"] - 1e-6)),
                                   waited=s["rest"], taken_at=(p[0], p[1], p[2]), tick=s["tick"])
        self._free_at = free
        return out

    def _apply(self, item, plan):
        """Key an engine.mobs DroppedItem along a plan: it appears at the release, falls, lies, and is gone."""
        track = plan["track"]
        f0 = int(round(track[0][0]))
        item.place(f0, track[0][1], age=0.0)
        root = item.root
        frames = [t for t, _p in track]
        for i in range(3):
            fc = _fcurve(root, "location", i)
            for kp in list(fc.keyframe_points):
                if kp.co.x > f0 - 0.2:
                    fc.keyframe_points.remove(kp, fast=True)
            for t, p in zip(frames, track):
                if t > f0 - 0.2:
                    kp = fc.keyframe_points.insert(float(t), float(p[1][i]))
                    kp.interpolation = "LINEAR"
            fc.update()
        item.rest_pos = None
        item.animate(f0, plan["frame"])
        item.pick_up(plan["frame"])
        self.takes.append((plan["frame"], item.name))
        return plan

    def absorb(self, item, frame, start=None, height=2.5, velocity=(0.0, 0.0, 0.0), offset=(0.0, 0.0)):
        """An engine.mobs DroppedItem is released ON `frame` over the hopper and is taken in the way the game
        takes it. start = (x, y, z) where it appears, default `height` blocks above the bowl's floor, `offset`
        (east, north) from the middle. velocity in blocks per tick. Returns the plan() dict of that item plus
        item=...: ["frame"] is the frame it is gone, ["landed"] the frame it touched down (None: taken in the air).
        Call it in film order: each take starts the hopper's 8-tick pause (see busy())."""
        if start is None:
            start = (self.mouth[0] + offset[0], self.mouth[1] + offset[1], self.bowl + float(height))
        plan = self.plan([(int(frame), start, velocity)])[0]
        plan["item"] = item
        return self._apply(item, plan)

    def stream(self, items, frame, every=5, height=2.5, start=None, spread=0.2, seed=0, land=True):
        """Several DroppedItems released one after the other from a point above the hopper: the first ON `frame`,
        the next every `every` FRAMES, each `spread` blocks or less off the middle (seeded), falling `height` blocks
        to the bowl (or from `start`). They are taken one per 8 ticks, so they pile up in the bowl and vanish in
        turn. land=True: the hopper is in its pause when the first one arrives (it has just passed an item on:
        busy()), so that one lands too; land=False: the hopper is idle and the first item is gone in the air, a
        block above the rim, as the game does it. Returns the plan() dicts (+ item) in order."""
        items = list(items)
        rng = np.random.default_rng([int(seed), 4421])
        drops = []
        reach = min(float(spread), HOPPER_BOWL_HALF - ITEM_SIZE / 2.0)
        for i, _it in enumerate(items):
            ox, oy = (rng.uniform(-reach, reach) for _k in range(2)) if reach > 0 else (0.0, 0.0)
            p = (self.mouth[0] + ox, self.mouth[1] + oy, self.bowl + float(height)) if start is None else \
                (start[0] + ox, start[1] + oy, start[2])
            drops.append((int(frame) + int(round(i * every)), p, (0.0, 0.0, 0.0)))
        if land:
            h = drops[0][1][2] - self.bowl
            ticks = item_fall(h)[-1][0]
            self.busy(drops[0][0] + (ticks + 1) * TICK - HOPPER_COOLDOWN_TICKS * TICK + 2 * TICK)
        plans = self.plan(drops)
        for it, plan in zip(items, plans):
            plan["item"] = it
            self._apply(it, plan)
        return plans


def hopper(where, cell, facing="down"):
    """A hopper block at `cell` (facing 'down' or the side its spout points to). Inside an edit hook it is part of
    the village mesh (engine.blocks draws the game's own model); on a built Village or a site it is its own
    object. Returns a Hopper: absorb(item, frame) / stream(items, frame) / busy(frame)."""
    world, coll, _v, b = _where(where)
    cell = _cell(cell)
    if facing not in ("down",) + HORIZ:
        raise ValueError("hopper facing must be down / north / east / south / west, not %r" % (facing,))
    props = {"facing": facing, "enabled": "true"}
    ob = None
    if b is not None:
        world.set(cell[0], cell[1], cell[2], "hopper", props)
    else:
        ob = block(where, "hopper", cell, props).object
    return Hopper(cell, facing, ob)


def hopper_on_chest(where, cell, facing="south", animated=True, partner=None):
    """The collection point of a farm: a chest at `cell` (latch toward `facing`) and a hopper on top of it, spout
    down. Returns (Hopper, Chest)."""
    c = chest(where, cell, facing, animated=animated, partner=partner)
    x, y, z = _cell(cell)
    return hopper(where, (x, y, z + 1), "down"), c


# ----------------------------------------------------------------------------------------------------
# WATER AND LAVA (FluidRenderer.tesselate)
# ----------------------------------------------------------------------------------------------------
def flow_amounts(cells, sources, world=None):
    """Fluid amounts as the game spreads water over a floor: 8 in every source cell, one less per step from the
    nearest source through `cells` (WaterFluid.getDropOff = 1; a cell further than 7 steps stays dry and is left
    out). Returns {cell: amount}. (Lava in the overworld loses 2 per step.)"""
    cells = {_cell(c) for c in cells}
    amount = {}
    front = []
    for s in sources:
        s = _cell(s)
        amount[s] = 8
        front.append(s)
    while front:
        nxt = []
        for c in front:
            a = amount[c] - 1
            if a < 1:
                continue
            for d in HORIZ:
                dx, dy, _dz = _DIR[d]
                n = (c[0] + dx, c[1] + dy, c[2])
                if n in cells and amount.get(n, 0) < a:
                    amount[n] = a
                    nxt.append(n)
        front = nxt
    return amount


class _FluidField:
    """The geometry rules of FluidRenderer for one fluid over a World."""

    def __init__(self, world, kind, amounts, falling=()):
        self.world, self.kind, self.amounts, self.falling = world, kind, dict(amounts), set(falling)

    def same(self, c):
        return c in self.amounts

    def own(self, c):
        """FluidState.getOwnHeight: amount / 9."""
        return self.amounts[c] / 9.0

    def height(self, c):
        """FluidRenderer.getHeight: 1 under more of the same fluid, else its own height; -1 = solid, 0 = open."""
        if c in self.amounts:
            return 1.0 if (c[0], c[1], c[2] + 1) in self.amounts else self.own(c)
        return -1.0 if self.world.is_solid(*c) else 0.0

    def corner(self, c, sx, sy):
        """FluidRenderer.calculateAverageHeight for the corner of cell c toward (sx, sy) (each -1 or +1)."""
        own = self.height(c)
        if own >= 1.0:
            return 1.0
        s1 = self.height((c[0] + sx, c[1], c[2]))
        s2 = self.height((c[0], c[1] + sy, c[2]))
        if s1 >= 1.0 or s2 >= 1.0:
            return 1.0
        acc = [0.0, 0.0]

        def add(h):
            if h >= FLUID_HEAVY[0]:
                acc[0] += h * FLUID_HEAVY[1]
                acc[1] += FLUID_HEAVY[1]
            elif h >= 0.0:
                acc[0] += h
                acc[1] += 1.0

        if s1 > 0.0 or s2 > 0.0:
            dg = self.height((c[0] + sx, c[1] + sy, c[2]))
            if dg >= 1.0:
                return 1.0
            add(dg)
        add(own)
        add(s1)
        add(s2)
        return acc[0] / acc[1]

    def flow(self, c):
        """FlowingFluid.getFlow in Blender axes: the unit vector (east, north) the fluid in cell c runs along, or
        (0, 0). It points from high to low; toward a neighbour that is open with fluid under it."""
        own = self.own(c)
        fx_, fy = 0.0, 0.0
        for d in HORIZ:
            dx, dy, _dz = _DIR[d]
            n = (c[0] + dx, c[1] + dy, c[2])
            diff = 0.0
            if n in self.amounts:
                diff = own - self.own(n)
            elif not self.world.is_solid(*n):
                below = (n[0], n[1], n[2] - 1)
                if below in self.amounts:
                    diff = own - (self.own(below) - FLUID_SOURCE_HEIGHT)
            fx_ += dx * diff
            fy += dy * diff
        length = math.hypot(fx_, fy)
        return (fx_ / length, fy / length) if length > 1e-9 else (0.0, 0.0)


def _fluid_mesh(field, flow_override=None):
    """Quads of a fluid body: {'still': [...], 'flow': [...], 'overlay': [...]} as (4 points, 4 uvs)."""
    w = field.world
    out = {"still": [], "flow": [], "overlay": []}
    e = FLUID_INSET
    tops = {}
    for c in sorted(field.amounts):
        x, y, z = c
        above = (x, y, z + 1)
        h = {(sx, sy): field.corner(c, sx, sy) for sx in (-1, 1) for sy in (-1, 1)}
        hmin = min(h.values())
        tops[c] = sum(h.values()) / 4.0
        up_block = w.block_id(*above)
        render_up = above not in field.amounts and not (up_block is not None and w.is_full_cube(*above) and hmin >= 1.0)
        below = (x, y, z - 1)
        render_down = below not in field.amounts and not (w.block_id(*below) is not None and w.is_full_cube(*below))
        # corners in the order north-west, south-west, south-east, north-east (the game's NW, SW, SE, NE)
        hn_w, hs_w, hs_e, hn_e = h[(-1, 1)], h[(-1, -1)], h[(1, -1)], h[(1, 1)]
        if render_up:
            pts = [(x, y + 1, z + hn_w - e), (x, y, z + hs_w - e), (x + 1, y, z + hs_e - e), (x + 1, y + 1, z + hn_e - e)]
            fl = flow_override if flow_override is not None else field.flow(c)
            if abs(fl[0]) < 1e-9 and abs(fl[1]) < 1e-9:
                uvs = [(0.0, 0.0), (0.0, 16.0), (16.0, 16.0), (16.0, 0.0)]
                out["still"].append((pts, uvs))
            else:
                # Minecraft's flow vector is (x, z) = (east, -north); angle = atan2(z, x) - pi / 2
                a = math.atan2(-fl[1], fl[0]) - math.pi / 2.0
                s, co = math.sin(a) * 0.25, math.cos(a) * 0.25
                uvs = [(16.0 * (0.5 + (-co - s)), 16.0 * (0.5 + (-co + s))),
                       (16.0 * (0.5 + (-co + s)), 16.0 * (0.5 + (co + s))),
                       (16.0 * (0.5 + (co + s)), 16.0 * (0.5 + (co - s))),
                       (16.0 * (0.5 + (co - s)), 16.0 * (0.5 + (-co - s)))]
                out["flow"].append((pts, uvs))
        if render_down:
            pts = [(x, y, z + e), (x, y + 1, z + e), (x + 1, y + 1, z + e), (x + 1, y, z + e)]
            out["still"].append((pts, [(0.0, 16.0), (0.0, 0.0), (16.0, 0.0), (16.0, 16.0)]))
        zb = z + (e if render_down else 0.0)
        # sides: (direction, first corner (x, y, h), second corner), seen from outside left to right
        sides = (("north", (x + 1, y + 1 - e, hn_e), (x, y + 1 - e, hn_w)),
                 ("south", (x, y + e, hs_w), (x + 1, y + e, hs_e)),
                 ("west", (x + e, y + 1, hn_w), (x + e, y, hs_w)),
                 ("east", (x + 1 - e, y, hs_e), (x + 1 - e, y + 1, hn_e)))
        for d, a_, b_ in sides:
            dx, dy, _dz = _DIR[d]
            n = (x + dx, y + dy, z)
            if n in field.amounts:
                continue
            nid = w.block_id(*n)
            if nid is not None and w.is_full_cube(*n):
                continue                                         # isFaceOccludedByNeighbor: a full opaque face
            ha, hb = a_[2], b_[2]
            if max(ha, hb) <= 0.0:
                continue
            pts = [(a_[0], a_[1], z + ha), (a_[0], a_[1], zb), (b_[0], b_[1], zb), (b_[0], b_[1], z + hb)]
            # u 0 .. 0.5 of the sprite, v (1 - h) / 2 .. 0.5
            uvs = [(0.0, 8.0 * (1.0 - ha)), (0.0, 8.0), (8.0, 8.0), (8.0, 8.0 * (1.0 - hb))]
            see_through = field.kind == "water" and nid is not None and (
                nid.endswith("glass") or nid.endswith("_leaves") or nid in ("ice", "slime_block", "honey_block"))
            out["overlay" if see_through else "flow"].append((pts, uvs))
    return out, tops


class Fluid:
    """A body of water or lava: .kind, .cells {cell: amount (8 = a source, 7..1 flowing)}, .objects (every
    object, one per image of the animated textures), .lights (lava), .name; top(cell), flow(cell), surface."""

    def __init__(self, name, kind, field, tops):
        self.name, self.kind, self._field, self._tops = name, kind, field, tops
        self.cells = dict(field.amounts)
        self.objects = []
        self.lights = []
        self.flow_override = None
        self._levels = []                   # [(frame, scale)] of the lights
        self._flickers = []                 # [(f0, f1, at, amount, seed)]

    def __repr__(self):
        return "<Fluid %s %s, %d cells>" % (self.kind, self.name, len(self.cells))

    def top(self, cell):
        """z of the fluid's surface in the middle of `cell` (the mean of its four corner heights)."""
        c = _cell(cell)
        return c[2] + self._tops[c]

    @property
    def surface(self):
        """z of the highest point of the surface."""
        return max(c[2] + t for c, t in self._tops.items())

    def flow(self, cell):
        """(east, north) unit vector the fluid in `cell` flows along, as the game computes it; (0, 0) = still."""
        if self.flow_override is not None:
            return self.flow_override
        return self._field.flow(_cell(cell))

    # ---- the lava light
    def level(self, frame, scale=1.0):
        """The lava light is `scale` x its base strength from `frame` on (a step, like Stage.lights per shot)."""
        self._levels = [l for l in self._levels if l[0] != int(frame)] + [(int(frame), float(scale))]
        self._relight()

    def flicker(self, f0, f1, at=None, amount=None, seed=0):
        """The lava light flickers on frames f0..f1. at=None: a slow, small unrest (amount 0.08 = +-8 %). at=frame:
        something falls in ON that frame: the light is smothered to about 45 % for two frames, flares to about
        170 % and settles over the next second with a decaying wobble; before `at` it is steady. amount scales the
        swing. The lava's own glow (its texture) does not change: only the light it throws."""
        self._flickers = [f for f in self._flickers if (f[0], f[1]) != (int(f0), int(f1))]
        self._flickers.append((int(f0), int(f1), None if at is None else int(at),
                               (0.08 if at is None else 1.0) if amount is None else float(amount), int(seed)))
        self._relight()

    def light_factor(self, frame):
        """What the lava light's strength is multiplied by at `frame` (level x flicker)."""
        k = _state_at(self._levels, frame, 1.0)
        for f0, f1, at, amount, seed in self._flickers:
            if not f0 <= frame <= f1:
                continue
            if at is None:
                t = frame / float(FPS)
                n = (math.sin(2 * math.pi * (0.9 * t + 0.13 * seed)) * 0.5 + math.sin(2 * math.pi * (2.3 * t + 0.37 * seed))
                     * 0.3 + math.sin(2 * math.pi * (5.1 * t + 0.71 * seed)) * 0.2)
                k *= 1.0 + amount * n
            elif frame >= at:
                dt = frame - at
                if dt < 2:
                    f = -0.55
                else:
                    u = (dt - 2) / float(FPS)
                    f = 0.7 * math.exp(-u * 4.0) * math.cos(2 * math.pi * 3.2 * u)
                k *= max(0.05, 1.0 + amount * f)
        return k

    def _relight(self):
        frames = {f for f, _s in self._levels}
        for f0, f1, _at, _a, _s in self._flickers:
            frames.update(range(f0, f1 + 2))
        frames = sorted(frames)
        for ob in self.lights:
            base = ob["base_energy"]
            if not frames:
                ob.data.energy = base
                continue
            fs = [min(frames[0], 1) - 1] + frames
            vals = [base * _state_at(self._levels, fs[0], 1.0)] + [base * self.light_factor(f) for f in frames]
            _keys(ob.data, "energy", fs, vals, "CONSTANT")
            ob.data.energy = vals[0]


def _rectangles(cells):
    """Cover a set of (x, y) columns with a few rectangles (x0, y0, x1, y1), greedily row by row."""
    left = set(cells)
    out = []
    while left:
        x0, y0 = min(left, key=lambda c: (c[1], c[0]))
        x1 = x0
        while (x1 + 1, y0) in left:
            x1 += 1
        y1 = y0
        while all((x, y1 + 1) in left for x in range(x0, x1 + 1)):
            y1 += 1
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                left.discard((x, y))
        out.append((x0, y0, x1, y1))
    return out


def lava_light(collection, rect, z, watts_per_block=LAVA_WATTS_PER_BLOCK, color=LAVA_LIGHT_COLOR, name="lava_light",
               max_watts=None):
    """The light lava throws: an AREA light the size of the lava surface (x0, y0, x1, y1 in block edges) at height
    z, shining up, `watts_per_block` per block of surface. Its strength per block of lava is constant, so a slot
    and a lake light what is right above them alike; a lake's reach grows with its size."""
    x0, y0, x1, y1 = (float(c) for c in rect)
    data = bpy.data.lights.new(name, "AREA")
    data.shape = "RECTANGLE"
    data.size, data.size_y = max(x1 - x0, 0.05), max(y1 - y0, 0.05)
    data.color = color
    watts = float(watts_per_block) * (x1 - x0) * (y1 - y0)
    data.energy = min(watts, max_watts) if max_watts else watts
    try:
        data.spread = math.pi
    except (AttributeError, TypeError):
        pass
    ob = bpy.data.objects.new(_unique(name), data)
    ob.location = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, float(z))
    ob.rotation_euler = (math.pi, 0.0, 0.0)              # an area light shines along its -Z: turn it to face up
    ob["mc_light"] = "lava"
    ob["base_energy"] = data.energy
    collection.objects.link(ob)
    return ob


def _fluid(where, kind, cells, sources, flow, animated, name, light, watts_per_block, falling=()):
    world, coll, v, _b = _where(where)
    if isinstance(cells, dict):
        amounts = {_cell(c): int(a) for c, a in cells.items()}
    else:
        cells = [_cell(c) for c in cells]
        amounts = flow_amounts(cells, sources, world) if sources is not None else {c: 8 for c in cells}
    if not amounts:
        raise ValueError("%s: no cells" % kind)
    bad = [a for a in amounts.values() if not 1 <= a <= 8]
    if bad:
        raise ValueError("fluid amounts are 8 (a source) or 1..7 (flowing), not %s" % sorted(set(bad)))
    name = _unique(name or kind)
    for c, a in amounts.items():
        world.set(c[0], c[1], c[2], kind, {"level": str(8 - a)})
    claim(world, amounts)
    field = _FluidField(world, kind, amounts, falling)
    quads, tops = _fluid_mesh(field, flow)
    fl = Fluid(name, kind, field, tops)
    fl.flow_override = flow
    tint = mc.biome_tint("water") if kind == "water" else None
    groups = (("still", "block/%s_still" % kind), ("flow", "block/%s_flow" % kind),
              ("overlay", "block/water_overlay"))
    for group, texture in groups:
        if not quads[group]:
            continue
        mb = mc.MeshBuilder()
        for pts, uvs in quads[group]:
            mb.add("m", pts, uvs)
        base = mb.mesh("m", "%s_%s" % (name, group))
        if group == "overlay" or not animated:
            images, shown = [0], None
        else:
            count, order, time = animation_of(texture)
            _period, shown = texture_schedule(order, time)
            images = sorted(set(shown))
        variants = {}
        for k, index in enumerate(images):
            me = base if k == 0 else base.copy()
            me.materials.append(_fluid_material(kind, texture, index, tint))
            ob = bpy.data.objects.new("%s_%s_%02d" % (name, group, index), me)
            coll.objects.link(ob)
            ob.visible_shadow = kind != "water"           # the game's water casts no shadow on what lies under it
            ob["mc_fluid"] = kind
            variants[index] = ob
            fl.objects.append(ob)
        if shown is not None and len(variants) > 1:
            _cycle_visibility(variants, shown)
    if kind == "lava" and light:
        by_z = {}
        for c in amounts:
            if (c[0], c[1], c[2] + 1) not in amounts:
                by_z.setdefault(c[2], set()).add((c[0], c[1]))
        for z, cols in sorted(by_z.items()):
            for (x0, y0, x1, y1) in _rectangles(cols):
                top = max(z + tops[(x, y, z)] for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))
                fl.lights.append(lava_light(coll, (x0, y0, x1 + 1, y1 + 1), top + LAVA_LIGHT_LIFT,
                                            watts_per_block=watts_per_block, name=name + "_light"))
    if hasattr(v, "sets") and isinstance(v.sets, dict):
        v.sets.setdefault("fixtures", {})[name] = fl
    return fl


def water(where, cells, sources=None, flow=None, animated=True, name=None):
    """Water as the game draws it, in the plains biome's blue. cells = the cells it fills: a list (all sources, or
    with sources=[...] the game's own spread from those: 8, 7, 6 ... one less per step), or a dict {cell: amount}
    (8 = a source block, 7..1 = flowing: amount / 9 of a block high). Surface heights, sloping corners, the still
    texture on still cells and the flow texture turned along the current on flowing ones and on every side face,
    faces toward solid blocks left out, the water_overlay texture against glass: FluidRenderer's rules. flow =
    (east, north): force that current on every top face (a film cheat for a level sheet). animated: the textures
    run at the game's speed (water_still 2 ticks per image, water_flow 1). Returns a Fluid."""
    return _fluid(where, "water", cells, sources, flow, animated, name, False, 0.0)


def lava(where, cells, sources=None, flow=None, animated=True, name=None, light=True,
         watts_per_block=LAVA_WATTS_PER_BLOCK):
    """Lava: the same geometry rules as water with block/lava_still (20 images, back and forth, 2 ticks each) and
    lava_flow, glowing, opaque, and with light=True an orange area light over every flat stretch of its surface
    (Fluid.lights; Fluid.level(frame, scale), Fluid.flicker(f0, f1, at=...)). Returns a Fluid."""
    return _fluid(where, "lava", cells, sources, flow, animated, name, light, watts_per_block)


def water_sheet(where, x0, y0, x1, y1, z, toward=None, amount=1, name=None, animated=True):
    """A level sheet of water over the floor cells x0..x1, y0..y1 at height z (the cells ABOVE the floor blocks).
    amount = how thick: 1 = the thinnest flowing water, 1/9 block (2 px), ... 7; 8 = source blocks (8/9).
    toward = 'north' | 'east' | 'south' | 'west' | None: the current drawn on it (None: the still texture).
    NOT a state the game reaches by itself (flowing water thins by one step per block): see water(sources=...)
    for the game's own slope. Returns a Fluid."""
    cells = {(x, y, int(z)): int(amount) for x in range(min(x0, x1), max(x0, x1) + 1)
             for y in range(min(y0, y1), max(y0, y1) + 1)}
    flow = None
    if toward is not None:
        d = _DIR[toward]
        flow = (float(d[0]), float(d[1]))
    return _fluid(where, "water", cells, None, flow, animated, name or "water_sheet", False, 0.0)


def lava_glow(where, x0, y0, x1, y1, z, strip=True, animated=True, name=None, watts_per_block=LAVA_WATTS_PER_BLOCK):
    """Lava as a glow only: the lava light over the rectangle of block columns x0..x1, y0..y1 at height z, and with
    strip=True a flat lava-textured, glowing surface just under it (no lava blocks, no sides): for a slot whose
    lava is out of sight and for a far lake. Returns a Fluid (its .cells are empty; .lights, level(), flicker())."""
    world, coll, v, _b = _where(where)
    name = _unique(name or "lava_glow")
    xa, xb, ya, yb = min(x0, x1), max(x0, x1) + 1, min(y0, y1), max(y0, y1) + 1
    field = _FluidField(world, "lava", {})
    fl = Fluid(name, "lava", field, {})
    if strip:
        mb = mc.MeshBuilder()
        for x in range(xa, xb):
            for y in range(ya, yb):
                mb.add("m", [(x, y + 1, z), (x, y, z), (x + 1, y, z), (x + 1, y + 1, z)],
                       [(0.0, 0.0), (0.0, 16.0), (16.0, 16.0), (16.0, 0.0)])
        base = mb.mesh("m", name + "_still")
        texture = "block/lava_still"
        if animated:
            _count, order, time = animation_of(texture)
            _period, shown = texture_schedule(order, time)
            images = sorted(set(shown))
        else:
            images, shown = [0], None
        variants = {}
        for k, index in enumerate(images):
            me = base if k == 0 else base.copy()
            me.materials.append(_fluid_material("lava", texture, index))
            ob = bpy.data.objects.new("%s_still_%02d" % (name, index), me)
            coll.objects.link(ob)
            variants[index] = ob
            fl.objects.append(ob)
        if shown is not None and len(variants) > 1:
            _cycle_visibility(variants, shown)
    fl.lights.append(lava_light(coll, (xa, ya, xb, yb), z + LAVA_LIGHT_LIFT, watts_per_block=watts_per_block,
                                name=name + "_light"))
    if hasattr(v, "sets") and isinstance(v.sets, dict):
        v.sets.setdefault("fixtures", {})[name] = fl
    return fl


# ----------------------------------------------------------------------------------------------------
# GLASS
# ----------------------------------------------------------------------------------------------------
def _glass_quads(world, cell, block_id, own):
    """The faces of one glass block at `cell` that the game draws: none toward another block of the same glass
    (connected glass has no inner faces), none toward a full opaque cube."""
    out = []
    for q in mc.bake_block(block_id):
        if q.cull is not None:
            off = _DIR[q.cull]
            n = (cell[0] + off[0], cell[1] + off[1], cell[2] + off[2])
            nid = world.block_id(*n)
            if nid == block_id or n in own:
                continue
            if nid is not None and world.is_full_cube(*n):
                continue
        out.append(q)
    return out


class GlassBox:
    """What glass_box built: .name, .walls {wall: [cells]}, .panes {cell: Object} (every glass block is its own
    object), .groups {cutaway name: [objects]} as registered in Village.cutaways, .inside (x0, y0, z0, x1, y1, z1:
    the cells of the room), .bounds; objects(wall=None, cells=None) picks panes."""

    def __init__(self, name, bounds):
        self.name, self.bounds = name, bounds
        self.walls, self.panes, self.groups = {}, {}, {}
        x0, y0, z0, x1, y1, z1 = bounds
        self.inside = (x0 + 1, y0 + 1, z0, x1 - 1, y1 - 1, z1 - 1)

    def objects(self, wall=None, cells=None, x=None, y=None, z=None):
        """Pane objects: of one wall ('north' ... 'roof'), of the cells listed, and / or with that x, y or z."""
        chosen = set(self.panes) if wall is None else set(self.walls[wall])
        if cells is not None:
            chosen &= {_cell(c) for c in cells}
        for axis, want in enumerate((x, y, z)):
            if want is not None:
                want = set(want) if isinstance(want, (list, tuple, set, range)) else {want}
                chosen = {c for c in chosen if c[axis] in want}
        return [self.panes[c] for c in sorted(chosen)]


def glass_box(where, x0, y0, z0, x1, y1, z1, walls=("north", "east", "south", "west", "roof"), openings=(),
              block_id="glass", name="glass"):
    """A room of glass BLOCKS: walls on the outer columns of the box of cells (x0, y0, z0)..(x1, y1, z1) and, with
    'roof' in walls, a roof filling its top layer z1 (walls then reach to z1 - 1). Cells in `openings`, and cells
    that already hold another block (a cobblestone plug, a door), get no glass. Every glass block is its own small
    object, drawn as the game draws connected glass (no faces between two glass blocks, none against opaque
    cubes), and the walls are registered as camera cutaways the way the village registers its own:
    Village.cutaways['<name>_north' | '_east' | '_south' | '_west' | '_roof' | '_all'], so
        st.see_through(shot, 'pod_south')            # films.lookdev.Stage: invisible to the camera only for one shot
        fixtures.see_through(st, shot, box.objects(wall='south', x=[3, 4]))     # single panes
    The corner columns belong to the north and south walls. Returns a GlassBox."""
    world, coll, v, _b = _where(where)
    x0, x1 = sorted((int(x0), int(x1)))
    y0, y1 = sorted((int(y0), int(y1)))
    z0, z1 = sorted((int(z0), int(z1)))
    unknown = set(walls) - {"north", "east", "south", "west", "roof"}
    if unknown:
        raise ValueError("glass_box walls are north / east / south / west / roof, not %s" % sorted(unknown))
    for key in ["%s_%s" % (name, w_) for w_ in list(walls) + ["all"]]:
        if key in v.cutaways:
            raise KeyError("cutaway %r exists already: give this glass box another name" % key)
    box = GlassBox(name, (x0, y0, z0, x1, y1, z1))
    skip = {_cell(c) for c in openings}
    top = z1 - 1 if "roof" in walls else z1
    members = {}
    for wall in ("roof", "north", "south", "east", "west"):
        if wall not in walls:
            continue
        if wall == "roof":
            cells = [(x, y, z1) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
        elif wall in ("north", "south"):
            yy = y1 if wall == "north" else y0
            cells = [(x, yy, z) for x in range(x0, x1 + 1) for z in range(z0, top + 1)]
        else:
            xx = x1 if wall == "east" else x0
            cells = [(xx, y, z) for y in range(y0 + 1, y1) for z in range(z0, top + 1)]
        for c in cells:
            if c in skip or c in members:
                continue
            have = world.block_id(*c)
            if have is not None and have != block_id:
                continue
            members[c] = wall
    for c in members:
        world.set(c[0], c[1], c[2], block_id)
    claim(world, members)
    own = set(members)
    mat_for = _material_for(block_id)
    for c, wall in sorted(members.items()):
        quads = _glass_quads(world, c, block_id, own)
        box.walls.setdefault(wall, []).append(c)
        if not quads:
            continue
        ob = mc.quads_object("%s_%s_%d_%d_%d" % ((name, wall) + c), quads, mat_for, coll, origin=(0.0, 0.0, 16.0))
        ob.location = (float(c[0]), float(c[1]), float(c[2]))
        ob["mc_block"] = block_id
        box.panes[c] = ob
    for wall, cells in box.walls.items():
        box.groups["%s_%s" % (name, wall)] = [box.panes[c] for c in cells if c in box.panes]
    box.groups["%s_all" % name] = list(box.panes.values())
    v.cutaways.update(box.groups)
    if hasattr(v, "sets") and isinstance(v.sets, dict):
        v.sets.setdefault("fixtures", {})[name] = box
    return box


def see_through(stage, shot, objects):
    """Make these objects invisible to the CAMERA only for one shot (what Stage.see_through does for a registered
    cutaway): they still block and catch light. objects = e.g. GlassBox.objects(wall='south', x=[3, 4])."""
    nxt = shot.frame_end + 1
    for ob in objects:
        stage.key(ob, "visible_camera", stage.film.frame_start, True)
        stage.key(ob, "visible_camera", shot.frame_start, False)
        stage.key(ob, "visible_camera", nxt, True)


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _check():
    """Numbers only (no rendering). Returns the number of failed checks."""
    failed = []

    def ok(label, cond, detail=""):
        if not cond:
            failed.append(label)
        print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    coll = _blocks.new_collection(scene, "set")
    st = site(coll)
    w = st.world
    w.fill(-2, -2, -1, 30, 12, -1, "cobblestone")

    # ---- chest
    base, lid, tex = chest_parts("single")
    ok("chest: 6 base faces, 12 lid + latch faces on entity/chest/normal", len(base) == 6 and len(lid) == 12
       and tex == "entity/chest/normal")
    b, l, t = chest_parts("left")
    ok("double chest halves have no face on the joined side (5 + 10 faces, normal_left / normal_right)",
       len(b) == 5 and len(l) == 10 and t.endswith("_left") and chest_parts("right")[2].endswith("_right"))
    ys = [p[1] for q in base for p in q.pts] + [p[1] for q in lid for p in q.pts]
    ok("chest is 14 px high with a 16 px latch (y 0..14, z up to 16)", min(ys) == 0 and max(ys) == 14
       and max(p[2] for q in lid for p in q.pts) == 16)
    c = chest(st, (0, 0, 0), "south")
    done = c.open(10)
    ok("chest.open(10) is fully open on frame 22 (10 ticks)", done == 22 and abs(c.openness_at(22) - 1.0) < 1e-9)
    ok("lid easing 1 - (1 - o)^3: half the time = 87.5 % of the angle", abs(c.angle_at(16) / CHEST_LID_ANGLE - 0.875)
       < 1e-9, "%.4f" % (c.angle_at(16) / CHEST_LID_ANGLE))
    shut = c.close(40)
    ok("chest.close(40) is shut on frame 52 and still 87.5 % open... no: 12.5 % of the way after half the time",
       shut == 52 and abs(c.angle_at(46) / CHEST_LID_ANGLE - 0.875) < 1e-9 and c.angle_at(52) < 1e-9,
       "%.4f" % (c.angle_at(46) / CHEST_LID_ANGLE))
    scene.frame_set(16)
    ok("the lid object is keyed: rotation x = -angle on frame 16", abs(c.lid.rotation_euler[0] + c.angle_at(16)) < 1e-4,
       "%.4f" % c.lid.rotation_euler[0])
    scene.frame_set(1)
    d = chest(st, (3, 0, 0), "south", partner=(4, 0, 0))
    ok("double chest facing south: the RIGHT half is the west cell", d.cells == [(3, 0, 0), (4, 0, 0)]
       and w.get(3, 0, 0)[1]["type"] == "right" and w.get(4, 0, 0)[1]["type"] == "left")
    d2 = chest(st, (7, 0, 0), "north", partner=(6, 0, 0))
    ok("double chest facing north: the RIGHT half is the east cell", d2.cells == [(7, 0, 0), (6, 0, 0)])
    try:
        chest(st, (9, 0, 0), "south", partner=(9, 1, 0))
        ok("a double chest across its own depth is refused", False)
    except ValueError:
        ok("a double chest across its own depth is refused", True)
    s1, s2 = chest(st, (11, 0, 0), "east", animated=False), chest(st, (12, 0, 0), "west", animated=False)
    ok("static chests share one mesh and have no lid", s1.object.data is s2.object.data and s1.lid is None)
    ok("chest cells are in the World and claimed (World.build leaves them out)", w.block_id(0, 0, 0) == "chest"
       and (0, 0, 0) in w._fixtures_skip)

    # ---- falling blocks
    tr = fall_track(15.0)
    ok("a 15-block fall takes 30 entity ticks, 18 blocks 33", tr[-1][0] == 30 and fall_ticks(18.0) == 33,
       "%d / %d" % (tr[-1][0], fall_ticks(18.0)))
    ok("first tick 0.04, second 0.0792 more (gravity 0.04, drag 0.98)", abs(tr[1][1] - 0.04) < 1e-12
       and abs(tr[2][1] - 0.1192) < 1e-12)
    ok("anvil damage: 13 blocks = 24 half hearts (a pillager), 12 = 22, 1 = 0, cap 40",
       anvil_damage(13) == 24 and anvil_damage(12) == 22 and anvil_damage(1) == 0 and anvil_damage(60) == 40)
    ok("chip chance: 15 blocks 0.75, 18 blocks 0.90, 1 block 0", abs(anvil_chip_chance(15) - 0.75) < 1e-9
       and abs(anvil_chip_chance(18) - 0.90) < 1e-9 and anvil_chip_chance(1.0) == 0.0)
    w.fill(0, 5, 0, 5, 5, 0, "dirt_path")
    try:
        landing_cell(w, (2, 5, 9))
        ok("landing on a dirt path is refused", False)
    except ValueError:
        ok("landing on a dirt path is refused", True)
    row = shelf(st, [(x, 3, 15) for x in range(20, 26)], "anvil", {"facing": "west"})
    drops = release(row, 20, world=st, chip=[1, 4])
    r = drops[0]
    ok("release on frame 20: lands in cell z 0 after 15 blocks, 2 + 30 - 1 ticks later", r["cell"] == (20, 3, 0)
       and r["height"] == 15.0 and abs(r["time_land"] - (20 + 31 * TICK)) < 1e-9, "%.2f" % r["time_land"])
    ok("frame_land is the first whole frame it stands (58), head_frame is before it", r["frame_land"] == 58
       and r["head_frame"] < r["frame_land"], "land %d head %d" % (r["frame_land"], r["head_frame"]))
    ok("only the chosen anvils chip", [d_["chipped"] for d_ in drops] == [False, True, False, False, True, False]
       and drops[1]["state"] == "chipped_anvil")
    ok("the World has the anvils where they landed (chipped ones as chipped)", w.block_id(20, 3, 0) == "anvil"
       and w.block_id(21, 3, 0) == "chipped_anvil" and w.block_id(20, 3, 15) is None)

    def z_at(blk, f):
        scene.frame_set(int(math.floor(f)), subframe=f - math.floor(f))
        return blk.object.matrix_world.translation.z

    b0 = row[0]
    ok("it hangs for 2 ticks: still at z 15 on frame 21, lower on frame 23", abs(z_at(b0, 21.0) - 15.0) < 1e-6
       and z_at(b0, 23.0) < 15.0 - 0.03, "%.4f / %.4f" % (z_at(b0, 21.0), z_at(b0, 23.0)))
    ok("it stands at z 0 on frame_land and after", abs(z_at(b0, 58.0)) < 1e-6 and abs(z_at(b0, 80.0)) < 1e-6)
    b1 = row[1]
    scene.frame_set(57)
    before = (b1._variants["anvil"].hide_render, b1._variants["chipped_anvil"].hide_render)
    scene.frame_set(58)
    after = (b1._variants["anvil"].hide_render, b1._variants["chipped_anvil"].hide_render)
    ok("a chipping anvil is the anvil until frame 57 and the chipped anvil from 58", before == (False, True)
       and after == (True, False), "%s -> %s" % (before, after))
    hit = strikes(drops, {"a": (20.5, 3.5, 0.0), "far": (27.5, 3.5, 0.0), "edge": (21.7, 3.5, 0.0)})
    ok("strikes: a mob under an anvil is hit, one 2 blocks off is not, one between two is", "a" in hit
       and "far" not in hit and "edge" in hit and hit["a"]["damage"] == 28)
    scene.frame_set(1)

    # ---- hopper
    w.set(15, 0, 0, "chest", {"facing": "south"})
    h = hopper(st, (15, 0, 1))
    ok("hopper: bowl floor 11/16 above its cell, rim at the top", abs(h.bowl - (1 + 11 / 16.0)) < 1e-9 and h.rim == 2.0)
    p = h.plan([(100, (15.5, 0.5, 1 + 11 / 16.0 + 2.5), (0, 0, 0))])[0]
    ok("an idle hopper takes a falling item in the air, the tick it enters the block above the hopper",
       p["landed"] is None and p["taken_at"][2] < 3.0 and p["taken_at"][2] > 2.0, "z %.3f, tick %d"
       % (p["taken_at"][2], p["tick"]))
    p2 = h.plan([(100 + 3, (15.5, 0.5, 1 + 11 / 16.0 + 2.5), (0, 0, 0))])[0]
    ok("the next item lands and waits out the 8-tick pause", p2["landed"] is not None
       and abs(p2["time"] - (p["time"] + 8 * TICK)) < TICK + 1e-6 and abs(p2["taken_at"][2] - h.bowl) < 1e-9,
       "landed %s, taken %.1f (first %.1f)" % (p2["landed"], p2["time"], p["time"]))
    h2 = hopper(st, (17, 0, 1))
    plans = h2.plan([(200 + 5 * i, (17.5, 0.5, h2.bowl + 2.5), (0, 0, 0)) for i in range(4)])
    gaps = [round((b_["time"] - a_["time"]) / TICK) for a_, b_ in zip(plans, plans[1:])]
    ok("four items, one every 5 frames: taken 8 ticks apart", all(g >= 8 for g in gaps) and gaps[0] == 8, str(gaps))

    # ---- fluids
    fw = _blocks.World()
    fw.fill(0, 0, -1, 6, 6, -1, "stone")
    f1 = _FluidField(fw, "water", {(3, 3, 0): 8})
    ok("a lone source block: corners at 8/9 * 10 / 12 = 0.741", abs(f1.corner((3, 3, 0), 1, 1) - (8 / 9.0) * 10 / 12)
       < 1e-9, "%.4f" % f1.corner((3, 3, 0), 1, 1))
    f2 = _FluidField(fw, "water", {(x, y, 0): 8 for x in range(1, 6) for y in range(1, 6)})
    ok("inside a pool of sources every corner is 8/9", abs(f2.corner((3, 3, 0), 1, 1) - 8 / 9.0) < 1e-9
       and f2.flow((3, 3, 0)) == (0.0, 0.0))
    am = flow_amounts([(x, y, 0) for x in range(0, 7) for y in range(1, 4)], [(0, y, 0) for y in range(1, 4)])
    ok("water spreading from a row of sources: 8 7 6 5 4 3 2", [am[(x, 2, 0)] for x in range(7)] == [8, 7, 6, 5, 4, 3, 2])
    f3 = _FluidField(fw, "water", am)
    ok("it flows east, away from the sources", f3.flow((3, 2, 0)) == (1.0, 0.0), str(f3.flow((3, 2, 0))))
    n, order, time = animation_of("block/water_still")
    period, shown = texture_schedule(order, time)
    ok("water_still: 32 images, 2 ticks each, the 24 fps pattern repeats after 384 frames", (n, time, period) ==
       (32, 2, 384) and shown[:6] == [0, 0, 0, 1, 1, 2], str(shown[:8]))
    n, order, time = animation_of("block/lava_still")
    ok("lava_still: 20 images shown back and forth (38 steps of 2 ticks)", n == 20 and len(order) == 38 and time == 2
       and animation_of("block/water_flow")[2] == 1 and animation_of("block/lava_flow")[2] == 3)
    ok("a mob in a current slides at 1.4 blocks / s", abs(WATER_SLIDE_SPEED - 1.4) < 1e-9)
    fl = water(st, {(x, 8, 0): 8 for x in range(0, 3)}, name="t_water")
    vis = []
    for f in (1, 2, 3, 4, 385):
        scene.frame_set(f)
        vis.append([o.name for o in fl.objects if not o.hide_render and "_still_" in o.name])
    ok("exactly one image of the water is rendered per frame, and frame 385 = frame 1",
       all(len(v_) == 1 for v_ in vis) and vis[0] == vis[1] == vis[2] != vis[3] and vis[4] == vis[0], str(vis))
    lv = lava(st, [(x, 10, 0) for x in range(0, 5)], name="t_lava")
    ok("lava: one area light over the 5 x 1 surface, %g W per block" % LAVA_WATTS_PER_BLOCK, len(lv.lights) == 1
       and abs(lv.lights[0].data.energy - 5 * LAVA_WATTS_PER_BLOCK) < 1e-6 and lv.lights[0].data.type == "AREA")
    lv.flicker(1, 60, at=20)
    ok("flicker(at=20): steady before, smothered on 20-21, flaring on 22", lv.light_factor(19) == 1.0
       and lv.light_factor(20) < 0.6 and lv.light_factor(22) > 1.5, "%.2f %.2f %.2f" % (
           lv.light_factor(19), lv.light_factor(20), lv.light_factor(22)))
    scene.frame_set(22)
    ok("the light's energy is keyed", abs(lv.lights[0].data.energy / lv.lights[0]["base_energy"] - lv.light_factor(22))
       < 1e-4)
    scene.frame_set(1)

    # ---- glass
    gw = site(coll)
    gw.world.fill(0, 0, -1, 6, 6, -1, "stone")
    gw.world.set(3, 0, 1, "cobblestone")
    box = glass_box(gw, 0, 0, 0, 6, 6, 2, name="pod", openings=[(3, 0, 0)])
    ok("glass box 7 x 7 x 3: roof 49 panes, north 14, east 10, the opening and the plug left out of south (12)",
       len(box.walls["roof"]) == 49 and len(box.walls["north"]) == 14 and len(box.walls["east"]) == 10
       and len(box.walls["south"]) == 12, str({k: len(v_) for k, v_ in box.walls.items()}))
    ok("cutaways registered like the village's: pod_north / east / south / west / roof / all",
       sorted(gw.cutaways) == ["pod_all", "pod_east", "pod_north", "pod_roof", "pod_south", "pod_west"])
    mid = box.panes[(3, 6, 0)]
    ok("a pane in the middle of a wall has 2 faces (out and in): none toward its glass neighbours, none toward the "
       "stone floor", len(mid.data.polygons) == 2, str(len(mid.data.polygons)))
    ok("box.objects(wall='south', x=[1, 2]) picks 4 panes", len(box.objects(wall="south", x=[1, 2])) == 4)

    # ---- the World wrapper
    w2 = _blocks.World()
    w2.fill(0, 0, 0, 2, 0, 0, "stone")
    claim(w2, [(1, 0, 0)])
    objs = w2.build(coll, "claimtest")
    ok("a claimed cell is left out of World.build and its neighbours get their faces toward it",
       sum(len(o.data.polygons) for o in objs) == 12, str(sum(len(o.data.polygons) for o in objs)))
    print("[fixtures] %d failed%s" % (len(failed), (": " + "; ".join(failed)) if failed else ""))
    return len(failed)


def _selftest(argv):
    if argv and argv[0] == "stills":
        from tools import fixtures_proof

        return fixtures_proof.main(argv[1:])
    return 1 if _check() else 0


if __name__ == "__main__":
    import sys

    sys.exit(_selftest(sys.argv[1:]))
