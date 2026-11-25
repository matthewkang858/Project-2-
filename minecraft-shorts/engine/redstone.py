"""REDSTONE PARTS THAT WORK ON CAMERA (docstring completed at the end of this file's development; see __doc__ below)."""
import math

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import blocks as _blocks
from . import mcassets as mc
from . import props as _props

FPS = 24
TICK = FPS / 20.0                    # film frames per game tick (1.2)

# ---- numbers transcribed from the 26.x client classes ------------------------------------------------------------
PISTON_TICKS = 2                     # PistonMovingBlockEntity.TICKS_TO_EXTEND; tick(): progress += 0.5F per tick
PISTON_STEP = 0.5                    # blocks the head and every moved block travel per tick (progress 0 -> 0.5 -> 1)
PISTON_FRAMES = PISTON_TICKS * TICK  # 2.4 film frames from the start of a move to its end
PISTON_START_TICKS = 0               # PistonBaseBlock.checkIfExtend: level.blockEvent(...) runs in the same tick
SHORT_ARM_UNTIL = 0.5                # PistonHeadRenderer.extractRenderState: the head is drawn with SHORT=true while
                                     # it is 0.5 block or less out of the base (progress <= 0.5 extending, >= 0.5
                                     # retracting), with the long arm beyond
PUSH_LIMIT = 12                      # PistonStructureResolver.MAX_PUSH_DEPTH
PLATFORM_PX = 4                      # PistonBaseBlock.PLATFORM_THICKNESS: the head plate, 4 pixels
REPEATER_TICKS_PER_DELAY = 2         # RepeaterBlock.getDelay: DELAY * 2 (on and off; DiodeBlock.checkTickOnNeighbor)
LAMP_ON_TICKS = 0                    # RedstoneLampBlock.neighborChanged: lit at once (setBlock in the same call)
LAMP_OFF_TICKS = 4                   # ... scheduleTick(pos, this, 4) when it loses power, then tick() turns it off
TORCH_TOGGLE_TICKS = 2               # RedstoneTorchBlock.TOGGLE_DELAY (the torch is an inverter)
WIRE_TICKS = 0                       # RedstoneWireBlock: a whole line updates in the tick its source changes
LEVER_TICKS = 0                      # LeverBlock.pull: setBlock in the tick of the click (no delay)
SWING_REACH = (0.58, 0.22, 1.25)     # MEASURED on engine.players attack(): the hand's far point of the swing is 0.58
                                     # in front of the feet, 0.22 to the right, 1.1-1.35 up (2.5-4 frames after the
                                     # swing starts)
LEVER_SHOW_TICKS = 1                 # the client draws the new lever after the server's block update (LeverBlock
                                     # .useWithoutItem only cycles a copy on the client): about one tick after the click
FALL_DELAY_TICKS = 2                 # FallingBlock.getDelayAfterPlace: an anvil starts falling 2 ticks after its
                                     # support has gone (for whoever drops the anvils: engine/fixtures.py)
LIGHT_LEVEL = {"redstone_lamp": 15, "redstone_torch": 7}     # Blocks: litBlockEmission(15) / litBlockEmission(7)
LIGHT_LEVEL_TORCH = 14               # the wall torch the village is lit with (game value; its lambda not traced here)
# RedstoneWireBlock COLORS (static init): f = power / 15; r = f * 0.6 + (0.4 if f > 0 else 0.3);
# g = clamp(f^2 * 0.7 - 0.5, 0, 1); b = clamp(f^2 * 0.6 - 0.7, 0, 1); ARGB.colorFromFloat -> floor(x * 255)
# (single precision). BlockTintSources$10 multiplies it into tintindex 0 of the dust models.


def _wire_colors():
    out = []
    for i in range(16):
        f = np.float32(i) / np.float32(15.0)
        r = f * np.float32(0.6) + (np.float32(0.4) if f > 0 else np.float32(0.3))
        g = min(max(f * f * np.float32(0.7) - np.float32(0.5), 0.0), 1.0)
        b = min(max(f * f * np.float32(0.6) - np.float32(0.7), 0.0), 1.0)
        out.append(tuple(int(math.floor(np.float32(c) * np.float32(255.0))) for c in (r, g, b)))
    return tuple(out)


WIRE_COLORS = _wire_colors()        # power 0..15 -> (r, g, b) 0..255: 0 = (76, 0, 0), 15 = (255, 51, 0)

# ---- film choices (NOT the game; each one stated in the docstring) ----------------------------------------------
DUST_GLOW = 0.6                      # emission of lit dust at power 15 (x power / 15): a shader pack's subtle glow
TORCH_GLOW = (1.4, 0.65, 0.12)       # redstone torch texture: (strength, only texels brighter than V, the rest)
REPEATER_GLOW = (0.8, 0.9, 0.0)      # lit repeater: the bright red texels of its top; its torches as TORCH_GLOW
LAMP_WATTS = 122.0                   # = 1.11 x the village torch (props: 110 W): the game's brightness ratio of light
                                     # 15 to 14 at two blocks (lightmap.fsh through sets.lightmap: 0.799 / 0.719)
REDSTONE_TORCH_WATTS = 37.0          # = 0.34 x the torch: level 7 against 14 at two blocks (0.243 / 0.719)
REDSTONE_TORCH_COLOR = (1.0, 0.62, 0.5)   # the game has one block-light colour; a shader pack tints it by the source
LAMP_RADIUS = 0.45                   # soft-shadow radius of the lamp's light (it is a glowing cube, not a flame)
HELD_TORCH_WATTS = 30.0              # the redstone torch in a hand (a little less: it is half a block from a face)

HORIZONTAL = ("north", "east", "south", "west")
DIRS6 = ("north", "east", "south", "west", "up", "down")
OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}
VEC = {k: Vector(v) for k, v in mc.DIR_BLENDER.items()}      # Blender unit steps: north = +Y, up = +Z


def _cell(c):
    return tuple(int(math.floor(float(v) + 1e-6)) for v in c)


def _add(c, d, k=1):
    v = VEC[d]
    return (c[0] + int(v.x) * k, c[1] + int(v.y) * k, c[2] + int(v.z) * k)


def at(frame, ticks):
    """The film time `ticks` game ticks after `frame` (1 tick = 1.2 frames; may be fractional)."""
    return float(frame) + float(ticks) * TICK


def frame_of(t):
    """The first whole frame that DRAWS a state that changes at film time t: the frame whose exposure middle
    (f + 0.25, the shutter is open over [f, f + 0.5]) is at or after t."""
    return int(math.ceil(float(t) - 0.25 - 1e-6))


# ----------------------------------------------------------------------------------------------------
# keyframe plumbing
# ----------------------------------------------------------------------------------------------------
def _fcurve(idb, path, index=0):
    """F-curve idb.<path>[index], creating action, slot and curve as needed (Blender 5 layered actions)."""
    ad = idb.animation_data or idb.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(idb.name + "_rs")
    return ad.action.fcurve_ensure_for_datablock(idb, path, index=index)


def _keys(idb, path, frames, values, interp="CONSTANT", index=0):
    """Replace a channel by the given keys (all with one interpolation mode)."""
    fc = _fcurve(idb, path, index)
    kps = fc.keyframe_points
    while len(kps):
        kps.remove(kps[len(kps) - 1], fast=True)
    n = len(frames)
    if n:
        kps.add(n)
        co = np.empty(2 * n, dtype=np.float32)
        co[0::2] = frames
        co[1::2] = values
        kps.foreach_set("co", co)
        for kp in kps:
            kp.interpolation = interp
            kp.handle_left_type = kp.handle_right_type = "VECTOR"
    fc.update()
    return fc


def _at(history, frame, default):
    """Value of a {frame: value} history at `frame` (the latest entry at or before it)."""
    best, out = None, default
    for f, v in history.items():
        if f <= frame + 1e-9 and (best is None or f > best):
            best, out = f, v
    return out


class _Looks:
    """Visibility of a part's alternative models: exactly one look (a list of objects) is rendered at a time,
    chosen per whole frame from a history; plus the Stage's per-shot visibility. Keys are rewritten from the
    whole history every time, so calls can come in any order."""

    def __init__(self, looks, initial):
        self.looks = dict(looks)        # look -> [Object]
        self.initial = initial
        self.hist = {}                  # whole frame -> look
        self.shown = {}                 # whole frame -> bool
        self.extra = []                 # objects that follow the part's shown state only (lights follow `lit`)
        self.rekey()

    def add(self, look, objects):
        self.looks[look] = list(objects)

    def set(self, frame, look):
        self.hist[int(frame)] = look

    def at(self, frame):
        return _at(self.hist, frame, self.initial)

    def show(self, frame, visible=True):
        self.shown[int(frame)] = bool(visible)
        self.rekey()

    def clear(self, frame_start, frame_end):
        for f in [f for f in self.hist if frame_start <= f < frame_end]:
            del self.hist[f]

    def rekey(self):
        frames = sorted(set(self.hist) | set(self.shown))
        times = [(frames[0] if frames else 1) - 1] + frames
        states = [(self.initial, True)] + [(self.at(f), _at(self.shown, f, True)) for f in frames]
        now = bpy.context.scene.frame_current
        cur, shown_now = self.at(now), _at(self.shown, now, True)
        member = {}                     # object -> the looks it belongs to (a piston's base is in two of them)
        for look, obs in self.looks.items():
            for ob in obs:
                member.setdefault(ob.name, (ob, set()))[1].add(look)
        for ob, looks in member.values():
            vals = [0.0 if (shown and c in looks) else 1.0 for c, shown in states]
            for path in ("hide_render", "hide_viewport"):
                _keys(ob, path, times, vals)
            ob.hide_render = ob.hide_viewport = not (shown_now and cur in looks)


class _Track:
    """Location keys of one object rebuilt from its rest location and a list of straight moves
    (t0, t1, delta): value(t) = rest + sum(clamp((t - t0) / (t1 - t0), 0, 1) * delta)."""

    def __init__(self, ob):
        self.ob = ob
        self.rest = Vector(ob.location)
        self.moves = {}                 # key -> (t0, t1, delta)

    def offset(self, t):
        o = Vector((0.0, 0.0, 0.0))
        for t0, t1, d in self.moves.values():
            u = 1.0 if t >= t1 else (0.0 if t <= t0 else (t - t0) / (t1 - t0))
            o += d * u
        return o

    def rekey(self):
        if not self.moves:
            for i in range(3):
                _keys(self.ob, "location", [], [], index=i)
            self.ob.location = self.rest
            return
        times = sorted({t for t0, t1, _d in self.moves.values() for t in (t0, t1)})
        for i in range(3):
            _keys(self.ob, "location", times, [self.rest[i] + self.offset(t)[i] for t in times], "LINEAR", index=i)
        self.ob.location = self.rest + self.offset(bpy.context.scene.frame_current)


# ----------------------------------------------------------------------------------------------------
# materials and models
# ----------------------------------------------------------------------------------------------------
def lightmap(level):
    """The game's brightness 0..1 for a light level (lightmap.fsh at the default Brightness, as engine.sets)."""
    b = max(0.0, min(15.0, float(level))) / 15.0
    f = b / (4.0 - 3.0 * b)
    return f + (1.0 - (1.0 - f) ** 4 - f) * 0.5


def _material(texture, tint=None, shade=None, glow=None, dim=None):
    """The material of a part's face. No glow and no dim: exactly engine.blocks' material for that texture (the set's
    own). glow = (strength, above, base): an emissive copy (mcassets.material). dim = a sky-light brightness 0..1
    multiplied in like a tint (engine.sets' baked sky light), for parts in a dark set."""
    if dim is not None and dim < 0.999:
        t = tint or (255, 255, 255)
        tint = tuple(int(round(c * dim)) for c in t)
    if glow is None:
        return _blocks.block_material(texture, tint, None, None, shade)
    strength, above, base = (tuple(glow) + (None, 0.0))[:3]
    mat = mc.material(texture, tint=tint, emission=strength, emit_above=above, emit_base=base or 0.0, shade=shade)
    mat.cycles.emission_sampling = "NONE"          # the glow is seen; the light comes from the part's point light
    return mat


def _quads(block_id, props):
    """Every baked Quad of a block state (the game's models, blockstate rotations, uvlock)."""
    return mc.bake_block(block_id, props, 0)


def _object(kit, name, quads, mat_for, location, collection=None):
    """One mesh object from baked quads; origin = the min corner of the cell the quads were baked for."""
    base, k = name, 1
    while bpy.data.objects.get(name) is not None:
        k += 1
        name = "%s_%d" % (base, k)
    ob = mc.quads_object(name, quads, mat_for, collection or kit.collection, origin=(0.0, 0.0, 16.0))
    ob.location = Vector(location)
    ob["mc_redstone"] = base
    return ob


def _plain(block_id, dim=None, glow_for=None):
    """quad -> material as engine.blocks gives it (tint by the block's tintindex), dimmed / glowing on request."""
    def f(q):
        g = glow_for(q) if glow_for else None
        return _material(q.texture, mc.block_tint(block_id, q.tintindex), getattr(q, "shade", None), g,
                         None if g else dim)
    return f


# ----------------------------------------------------------------------------------------------------
# the kit: one per set (Village or World), holds the parts and answers "what is in this cell"
# ----------------------------------------------------------------------------------------------------
class RedstoneError(ValueError):
    """A request the game would not carry out (13 blocks pushed, a cell taken, a piston extended twice ...)."""


def kit(where, collection=None, sky_light=None):
    """The redstone kit of a set: where = the Village (or a blocks.World). The same kit comes back for the same set.
    collection: where the parts go (default: a collection 'redstone' in the scene). sky_light = default sky light
    level (0..15) baked into the colours of every part (None: none; for parts in a dark set, see engine.sets)."""
    k = getattr(where, "_redstone_kit", None)
    if k is not None and k._alive():
        if sky_light is not None:
            k.sky_light = sky_light
        return k
    k = Kit(where, collection, sky_light)
    try:
        where._redstone_kit = k
    except AttributeError:
        pass
    return k


class Kit:
    """The parts of one set. Build parts with its methods (see the module docstring)."""

    def __init__(self, where, collection=None, sky_light=None):
        self.where = where
        self.world = getattr(where, "world", where) if where is not None else None
        if collection is None:
            collection = _blocks.new_collection(bpy.context.scene, "redstone")
        self.collection = collection
        self.sky_light = sky_light
        self.parts = []                 # every part, in creation order
        self.static = {}                # cell -> part that sits there (lever, torch, repeater, lamp, piston base, wire)
        self.movables = []              # _Movable blocks (moved by pistons)
        self.tracks = {}                # object name -> _Track
        self.rides = []                 # (thing, on, frame_start, frame_end)

    def _alive(self):
        try:
            return bool(self.collection.name) and self.collection.name in bpy.data.collections
        except ReferenceError:
            return False

    def _dim(self, sky_light):
        level = self.sky_light if sky_light is None else sky_light
        return None if level is None else lightmap(level)

    # ---- what is where ----------------------------------------------------------------------------------
    def world_block(self, cell):
        """(block_id, props) the set's World holds at a cell (None: air)."""
        if self.world is None or not hasattr(self.world, "get"):
            return None
        return self.world.get(*cell)

    def movable_at(self, cell, t):
        """The kit's movable block in `cell` at film time t (None)."""
        for m in self.movables:
            if m.there(t) and m.cell_at(t) == tuple(cell):
                return m
        return None

    def occupied(self, cell, t, ignore=()):
        """What fills a cell at time t: 'world', a part, a movable, or None."""
        if self.world_block(cell) is not None:
            return "world"
        p = self.static.get(tuple(cell))
        if p is not None and p not in ignore:
            return p
        m = self.movable_at(cell, t)
        if m is not None and m not in ignore:
            return m
        return None

    def _claim(self, cell, part, allow_world=False):
        cell = _cell(cell)
        if not allow_world and self.world_block(cell) is not None:
            raise RedstoneError("redstone: cell %s holds %s in the set's World: leave it empty in the hook "
                                "(redstone.carve(b, cells)), the part is drawn as its own object"
                                % (cell, self.world_block(cell)[0]))
        other = self.static.get(cell)
        if other is not None and other is not part:
            raise RedstoneError("redstone: cell %s is taken by %s" % (cell, other))
        self.static[cell] = part
        return cell

    def track(self, ob):
        t = self.tracks.get(ob.name)
        if t is None:
            t = self.tracks[ob.name] = _Track(ob)
        return t

    # ---- parts ------------------------------------------------------------------------------------------
    def block(self, block_id, cell, props=None, frame=None, name=None, sky_light=None):
        """A movable block of its own (engine.breaking.place_block: a Breakable) that pistons push and pull."""
        from . import breaking

        cell = _cell(cell)
        if self.world_block(cell) is not None:
            raise RedstoneError("redstone.block: cell %s holds %s in the set's World: carve it in the hook"
                                % (cell, self.world_block(cell)[0]))
        b = breaking.place_block(self.collection, block_id, cell, props, world=self.world, name=name, frame=frame)
        dim = self._dim(sky_light)
        if dim is not None:
            me = b.object.data = b.object.data.copy()
            for i, m in enumerate(list(me.materials)):
                tex = m.get("mc_texture")
                if tex:
                    me.materials[i] = _material(tex, None, m.get("mc_shade"), None, dim)
        m = _Movable(self, b, cell)
        self.movables.append(m)
        return m

    def lever(self, cell, face="floor", facing="north", powered=False, name=None, sky_light=None):
        """A lever (face floor / wall / ceiling; facing as the game's: for a wall lever the side it sticks out to)."""
        return Lever(self, cell, face, facing, powered, name, sky_light)

    def piston(self, cell, facing="north", sticky=False, extended=False, name=None, sky_light=None):
        """A piston / sticky piston in any of the six facings (the side its head comes out of)."""
        return Piston(self, cell, facing, sticky, extended, name, sky_light)

    def wire(self, cells, power=0, dots=(), source=None, name=None, sky_light=None):
        """A line of redstone dust over `cells` (each the cell the dust lies IN, on top of the block below)."""
        return Wire(self, cells, power, dots, source, name, sky_light)

    def repeater(self, cell, toward="north", delay=1, powered=False, name=None, sky_light=None):
        """A repeater whose signal travels `toward` (the game's FACING is the opposite side: its input)."""
        return Repeater(self, cell, toward, delay, powered, name, sky_light)

    def lamp(self, cell, lit=False, name=None, sky_light=None, watts=None):
        """A redstone lamp (off / on); on = its own point light (LAMP_WATTS)."""
        return Lamp(self, cell, lit, name, sky_light, watts)

    def torch(self, cell, wall=None, lit=True, frame=None, name=None, sky_light=None, watts=None):
        """A redstone torch standing in `cell` (wall=None) or on a wall (wall = the side it leans out to, the
        game's FACING of redstone_wall_torch); frame = the frame it appears on (None: there from the start)."""
        return Torch(self, cell, wall, lit, frame, name, sky_light, watts)

    def piston_door(self, cells, side, block="stone", closed=True, name="piston_door", sky_light=None):
        """A door of blocks pulled sideways into a wall by sticky pistons (one per door cell): see PistonDoor."""
        return PistonDoor(self, cells, side, block, closed, name, sky_light)

    def piston_row(self, cells, facing, carry="oak_planks", extended=True, sticky=True, name="piston_row",
                   sky_light=None):
        """Pistons in a row, each carrying one block on its arm: see PistonRow."""
        return PistonRow(self, cells, facing, carry, extended, sticky, name, sky_light)

    def ride(self, thing, on, frame_start=None, frame_end=None):
        """`thing` (a movable block, a Breakable, an Object, a Character) moves with the movable block `on` for
        every move of `on` that starts in [frame_start, frame_end). NOT the game for blocks (an anvil on a plank
        that is pushed away falls) nor for anything on a sideways push (entities ride only an upward push)."""
        self.rides.append((thing, on, frame_start, frame_end))
        on.riders_changed()

    def extend_all(self, pistons, frame):
        """Every piston extends on `frame` (one tick), each pushing what is in front of it. Returns the end time."""
        return max([p.extend(frame) for p in pistons] or [float(frame)])

    def retract_all(self, pistons, frame):
        """Every piston retracts on `frame`, the sticky ones pulling their blocks. Returns the end time."""
        return max([p.retract(frame) for p in pistons] or [float(frame)])

    def show(self, frame, visible=True):
        """Per-shot visibility of every part of the kit."""
        for p in self.parts:
            p.show(frame, visible)
        for m in self.movables:
            m.show(frame, visible)

    # ---- the dust's view of the world (RedstoneWireBlock.getConnectingSide) -----------------------------------
    def _is_wire(self, cell):
        p = self.static.get(tuple(cell))
        return isinstance(p, Wire)

    def _conductor(self, cell):
        """isRedstoneConductor: an opaque full cube (stone, planks, lamps, pistons are; glass, slabs, parts are not)."""
        p = self.static.get(tuple(cell))
        if p is not None:
            return isinstance(p, Lamp)          # pistons, levers, torches, repeaters, dust: never conductors
        if self.movable_at(cell, 0.0) is not None:
            return self.movable_at(cell, 0.0).full_cube
        w = self.world
        return bool(w is not None and hasattr(w, "is_full_cube") and w.is_full_cube(*cell))

    def _sturdy(self, cell, face):
        """isFaceSturdy: the face of the block in `cell` covers the whole side (full cubes; a slab's flat side)."""
        if self._conductor(cell):
            return True
        p = self.static.get(tuple(cell))
        if isinstance(p, Piston) and not p.extended0 and p.cell == tuple(cell):
            return True                         # a retracted piston is a full cube (not a conductor)
        st = self.world_block(cell)
        if st is None:
            return False
        bid, props = st
        if bid.endswith("_slab"):
            t = props.get("type", "bottom")
            return t == "double" or (face == "up" and t == "top") or (face == "down" and t == "bottom")
        return False

    def _connects(self, cell, direction):
        """shouldRedstoneWireConnectTo of what is in `cell`, seen from a wire `direction` away (None: above/below)."""
        p = self.static.get(tuple(cell))
        if isinstance(p, Wire):
            return True
        if isinstance(p, Repeater):
            return direction is not None and direction in (p.facing, OPPOSITE[p.facing])
        if isinstance(p, (Lever, Torch)):
            return direction is not None
        m = self.movable_at(cell, 0.0)
        if m is not None and m.block_id == "redstone_block":
            return direction is not None
        st = self.world_block(cell)
        if st is not None and st[0] in ("redstone_block", "lever", "redstone_torch", "redstone_wall_torch"):
            return direction is not None
        return False

    def _side(self, cell, d, climb):
        """RedstoneWireBlock.getConnectingSide(level, pos, dir, canClimbUp) -> 'up' | 'side' | 'none'."""
        n = _add(cell, d)
        if climb and self._sturdy(n, "up") and self._connects(_add(n, "up"), None):
            return "up" if self._sturdy(n, OPPOSITE[d]) else "side"
        if self._connects(n, d) or (not self._conductor(n) and self._connects(_add(n, "down"), None)):
            return "side"
        return "none"

    def wire_state(self, cell, dot=False):
        """The connections the game gives a dust in `cell` (getConnectionState after getMissingConnections):
        {'north': 'side' | 'up' | 'none', ...}. An unconnected dust is a cross, or a dot when dot=True (the
        player's right click); a dust with connections on one axis only runs across the whole block."""
        climb = not self._conductor(_add(cell, "up"))
        s = {d: self._side(cell, d, climb) for d in HORIZONTAL}
        if all(v == "none" for v in s.values()) and dot:
            return s
        n, e, so, w = (s[d] != "none" for d in HORIZONTAL)
        ns_not, ew_not = not n and not so, not e and not w
        if not w and ns_not:
            s["west"] = "side"
        if not e and ns_not:
            s["east"] = "side"
        if not n and ew_not:
            s["north"] = "side"
        if not so and ew_not:
            s["south"] = "side"
        return s


class _Part:
    """Common to every part: name, cell, looks, show()."""

    kind = "part"

    def __init__(self, kit_, cell, name):
        self.kit = kit_
        self.cell = _cell(cell)
        base = name or "%s_%d_%d_%d" % (self.kind, self.cell[0], self.cell[1], self.cell[2])
        self.name = base
        self.looks = None
        self.lights = []
        kit_.parts.append(self)

    def __repr__(self):
        return "<redstone.%s %s at %s>" % (type(self).__name__, self.name, self.cell)

    def show(self, frame, visible=True):
        """Per-shot visibility (films.lookdev.Stage.finish calls it for everything in st.cast)."""
        if self.looks is not None:
            self.looks.show(frame, visible)
        self._rekey_lights()

    def _rekey_lights(self):
        pass

    @property
    def objects(self):
        out = []
        if self.looks is not None:
            for obs in self.looks.looks.values():
                out.extend(obs)
        return out + list(self.lights)

    @property
    def center(self):
        return Vector((self.cell[0] + 0.5, self.cell[1] + 0.5, self.cell[2] + 0.5))


class _Movable:
    """A block that pistons move: a Breakable (engine.breaking.place_block) with the kit's move record."""

    def __init__(self, kit_, breakable, cell):
        self.kit, self.breakable, self.cell0 = kit_, breakable, tuple(cell)
        self.block_id = breakable.block_id
        self.full_cube = bool(getattr(breakable, "full_cube", True))
        self.name = breakable.name
        self.object = breakable.object
        self.moves = {}                 # t0 -> (t1, step direction)

    def __repr__(self):
        return "<redstone block %s at %s>" % (self.block_id, self.cell0)

    def there(self, t):
        return self.breakable.there_at(t) if hasattr(self.breakable, "there_at") else True

    def cell_at(self, t):
        """The cell the block is in (or moving into) at film time t."""
        c = self.cell0
        for t0, (t1, d) in sorted(self.moves.items()):
            if t0 <= t + 1e-9:
                c = _add(c, d)
        return c

    def move(self, t0, d):
        self.moves[float(t0)] = (float(t0) + PISTON_FRAMES, d)
        self._rekey()

    def unmove(self, t0):
        self.moves.pop(float(t0), None)
        self._rekey()

    def riders_changed(self):
        self._rekey()

    def _rekey(self):
        tr = self.kit.track(self.object)
        tr.moves = {("self", t0): (t0, t1, VEC[d].copy()) for t0, (t1, d) in self.moves.items()}
        tr.rekey()
        for thing, on, fs, fe in self.kit.rides:
            if on is self:
                _ride_rekey(self.kit, thing, self, fs, fe)

    def show(self, frame, visible=True):
        self.breakable.show(frame, visible)

    @property
    def center(self):
        return Vector(self.object.location) + Vector((0.5, 0.5, 0.5))


def _thing_object(thing):
    """The Object that carries a thing's position: a movable / Breakable's .object, a Character's .root, an Object."""
    if isinstance(thing, _Movable):
        return thing.object, False
    if hasattr(thing, "root") and hasattr(thing, "head"):
        return thing.root, True
    if hasattr(thing, "object") and isinstance(getattr(thing, "object"), bpy.types.Object):
        return thing.object, False
    return thing, False


def _ride_rekey(kit_, thing, on, fs, fe):
    """Give a rider the moves of the block it stands on (only those starting in [fs, fe))."""
    ob, character = _thing_object(thing)
    moves = [(t0, t1, VEC[d].copy()) for t0, (t1, d) in on.moves.items()
             if (fs is None or t0 >= fs) and (fe is None or t0 < fe)]
    if not character:
        tr = kit_.track(ob)
        for k in [k for k in tr.moves if k[0] == ("ride", on.name)]:
            del tr.moves[k]
        for t0, t1, d in moves:
            tr.moves[(("ride", on.name), t0)] = (t0, t1, d)
        tr.rekey()
        return
    done = ob.get("_rs_ridden", [])
    for t0, t1, d in moves:
        key = "%s@%.3f" % (on.name, t0)
        if key in done:
            continue
        _shift_character(ob, t0, t1, d)
        done = list(done) + [key]
    ob["_rs_ridden"] = done


def _shift_character(root, t0, t1, d):
    """A character's root carried by delta d over [t0, t1]: every location key after t0 moves by d, and two keys
    make the carry itself (a character keyed later than this call is not carried: ride after keying him)."""
    for i in range(3):
        if abs(d[i]) < 1e-9:
            continue
        fc = _fcurve(root, "location", i)
        v0 = fc.evaluate(t0) if len(fc.keyframe_points) else root.location[i]
        v1 = (fc.evaluate(t1) if len(fc.keyframe_points) else root.location[i]) + d[i]
        for kp in fc.keyframe_points:
            if kp.co.x > t0 + 1e-6:
                kp.co.y += d[i]
                kp.handle_left.y += d[i]
                kp.handle_right.y += d[i]
        for t, v in ((t0, v0), (t1, v1)):
            kp = fc.keyframe_points.insert(t, v)
            kp.interpolation = "LINEAR"
        fc.update()


# ----------------------------------------------------------------------------------------------------
# lever
# ----------------------------------------------------------------------------------------------------
class Lever(_Part):
    """A lever (LeverBlock): the cobblestone base and the handle, which the game swaps between two models (no
    in-between frames). flip / set; hand_point() is where a hand must reach, stand() where to stand."""

    kind = "lever"

    def __init__(self, kit_, cell, face="floor", facing="north", powered=False, name=None, sky_light=None):
        super().__init__(kit_, cell, name)
        if face not in ("floor", "wall", "ceiling") or facing not in HORIZONTAL:
            raise RedstoneError("lever: face floor | wall | ceiling, facing north | east | south | west")
        kit_._claim(self.cell, self)
        self.face, self.facing, self.powered0 = face, facing, bool(powered)
        self.hist = {}                  # frame -> (powered, ease frames)
        dim = kit_._dim(sky_light)
        props = {"face": face, "facing": facing, "powered": "true"}
        part = mc.resolve_blockstate("lever", props)[0]          # powered=true: model block/lever (handle at -45)
        self.part = part
        quads = mc.bake_part(part)
        base_q = [q for q in quads if q.texture != "block/lever"]
        hand_q = [q for q in quads if q.texture == "block/lever"]
        mat = _plain("lever", dim)
        self.base = _object(kit_, self.name + "_base", base_q, mat, self.cell)
        # the handle pivots on the model point (8, 1, 8) about the model's X axis (lever.json element rotation),
        # carried through the blockstate rotation: build it around that point
        piv_m = mc.rotate_point((8.0, 1.0, 8.0), part.x, part.y)
        ax_m = Vector(mc.rotate_point((16.0, 1.0, 8.0), part.x, part.y)) - Vector(piv_m)
        piv_b = Vector(mc.to_blender(piv_m))
        ax_b = Vector((ax_m[0], -ax_m[2], ax_m[1])).normalized()
        shifted = []
        for q in hand_q:
            pts = [(p[0] - piv_m[0], p[1] - piv_m[1], p[2] - piv_m[2] + 16.0) for p in q.pts]
            shifted.append(mc.Quad(pts, q.uvs, q.texture, q.tintindex, q.overlay, None, None, q.thin,
                                   getattr(q, "shade", None)))
        self.handle = _object(kit_, self.name + "_handle", shifted, mat, Vector(self.cell) + piv_b)
        self.handle.rotation_mode = "AXIS_ANGLE"
        self.pivot = Vector(self.cell) + piv_b
        self.axis = ax_b
        # which way +90 degrees turns the 'lever' handle into the 'lever_on' handle (checked against the bake)
        off = mc.bake_part(mc.resolve_blockstate("lever", dict(props, powered="false"))[0])
        want = np.mean([mc.to_blender(p) for q in off if q.texture == "block/lever" for p in q.pts], axis=0)
        here = np.mean([mc.to_blender(p) for q in hand_q for p in q.pts], axis=0)
        best = None
        for sign in (1.0, -1.0):
            R = Matrix.Rotation(sign * math.pi / 2, 3, ax_b)
            got = R @ (Vector(here) - piv_b) + piv_b
            err = (got - Vector(want)).length
            if best is None or err < best[0]:
                best = (err, sign)
        self.off_angle = best[1] * math.pi / 2       # handle angle of the UNPOWERED model
        self.check_error = best[0]
        pts = sorted((Vector(mc.to_blender(p)) - piv_b for q in hand_q for p in q.pts), key=lambda v: -v.length)
        self.tip = sum(pts[:4], Vector()) / 4.0      # pivot -> the middle of the handle's top face (powered model)
        self._rekey()

    def angle(self, powered):
        return 0.0 if powered else self.off_angle

    def state_at(self, frame):
        """Powered at `frame` (the state drawn on that frame)."""
        return bool(_at({f: v[0] for f, v in self.hist.items()}, frame, self.powered0))

    def set(self, frame, powered, ease=0):
        """The lever is in state `powered` from `frame` on. ease=0: the game's model swap; ease=2: the handle swings
        over 2 frames ending ON frame (a film ease). Returns frame (LEVER_TICKS = 0: what it drives changes now)."""
        self.hist[int(round(frame))] = (bool(powered), int(ease))
        self._rekey()
        return float(frame)

    def flip(self, frame, ease=0):
        """Toggle on `frame` (see set). Returns frame."""
        return self.set(frame, not self.state_at(frame - 1), ease)

    def power(self, t):
        """(chain helper) a lever is a source: switches on at t. Returns t."""
        return self.set(frame_of(t), True)

    def unpower(self, t):
        return self.set(frame_of(t), False)

    def _rekey(self):
        frames = sorted(self.hist)
        times, vals = [], []
        cur = self.angle(self.powered0)
        times.append(float((frames[0] if frames else 1) - 1))
        vals.append(cur)
        for f in frames:
            on, ease = self.hist[f]
            a = self.angle(on)
            if ease > 0:
                times.append(float(f - ease))
                vals.append(cur)
            else:
                times.append(float(f) - 0.25)     # a step keyed inside (f - 0.5, f]: drawn from frame f, no smear
                vals.append(cur)
            times.append(float(f))
            vals.append(a)
            cur = a
        fc = _keys(self.handle, "rotation_axis_angle", times, vals, "LINEAR", index=0)
        for i in range(3):
            _keys(self.handle, "rotation_axis_angle", [times[0]], [self.axis[i]], "CONSTANT", index=i + 1)
        self.handle.rotation_axis_angle = (fc.evaluate(bpy.context.scene.frame_current),) + tuple(self.axis)

    def hand_point(self, frame=None, along=0.8):
        """World point on the handle `along` of the way from its pivot to its tip (1.0 = the tip) at `frame`
        (default: the current state): where a hand that flips it must be."""
        on = self.state_at(frame if frame is not None else bpy.context.scene.frame_current)
        v = Matrix.Rotation(self.angle(on), 3, self.axis) @ (self.tip * along)
        return self.pivot + v

    def stand(self, distance=SWING_REACH[0], side=None, lateral=SWING_REACH[1], along=0.5):
        """((x, y, z), yaw) where a player stands so that his right hand, at the far end of an arm swing
        (engine.players attack: SWING_REACH, measured), is at hand_point(along=along): `distance` blocks in front
        of the lever (wall lever: on the side it sticks out to; floor / ceiling: side=, default its facing),
        turned to it, the lever `lateral` blocks to his right. z = the top of the solid block under that spot
        (searched from the lever's height down). The swing passes 1.1-1.35 above his feet: a wall lever in the
        block above the floor (handle 1.15-1.85 high) meets it; anything else is a near miss (as in the game,
        where the hand never touches the lever)."""
        front = side or self.facing
        f = VEC[front]
        hp = self.hand_point(None, along)
        yaw = math.atan2(-f.x, f.y)                     # facing back toward the lever (-Y at yaw 0)
        look = Vector((-f.x, -f.y, 0.0))
        right = Vector((look.y, -look.x, 0.0))
        p = Vector((hp.x, hp.y, 0.0)) + Vector((f.x, f.y, 0.0)) * distance - right * lateral
        z = self._floor(p)
        return (p.x, p.y, z), yaw

    def _floor(self, p):
        w = self.kit.world
        x, y = int(math.floor(p.x)), int(math.floor(p.y))
        z0 = self.cell[2] + (1 if self.face == "ceiling" else 0)
        if w is not None and hasattr(w, "is_solid"):
            for z in range(z0, z0 - 8, -1):
                if w.is_solid(x, y, z):
                    st = w.get(x, y, z)
                    if st and st[0].endswith("_slab") and st[1].get("type", "bottom") == "bottom":
                        return z + 0.5
                    if st and st[0] in ("dirt_path", "farmland"):
                        return z + 15.0 / 16.0
                    return float(z + 1)
        return float(self.cell[2])

    @property
    def objects(self):
        return [self.base, self.handle]

    def show(self, frame, visible=True):
        for ob in (self.base, self.handle):
            _vis_key(ob, frame, visible)


def _vis_key(ob, frame, visible):
    """One CONSTANT visibility key (render and viewport) on an object."""
    for path in ("hide_render", "hide_viewport"):
        setattr(ob, path, not visible)
        ob.keyframe_insert(path, frame=int(frame))
        fc = _fcurve(ob, path)
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"


def _part_matrix(part):
    """The blockstate rotation of a ModelPart as a 3x3 matrix in Blender axes (acting on directions)."""
    o = Vector(mc.to_blender(mc.rotate_point((8.0, 8.0, 8.0), part.x, part.y)))
    cols = []
    for p in ((24.0, 8.0, 8.0), (8.0, 8.0, -8.0), (8.0, 24.0, 8.0)):      # Blender +X, +Y (MC -z), +Z (MC +y)
        cols.append(Vector(mc.to_blender(mc.rotate_point(p, part.x, part.y))) - o)
    return Matrix((cols[0], cols[1], cols[2])).transposed()


def flip_by(player, lever, frame, sync="game", look=True, ease=0):
    """A player flips a lever: his arm swing (engine.players attack) starts ON `frame` (the click) and the lever
    changes LEVER_SHOW_TICKS later (sync="game": the frame after), or on the frame his hand is nearest the handle
    (sync="hand": a film choice that reads in a close-up). look=True turns his head to the handle (6-frame ease
    ending on the click). Call after his place() / walk. Returns the frame the lever changes on."""
    hp = lever.hand_point(frame - 1, 0.5)
    if look:
        player.look_at(frame - 6, hp, ease=6)
    player.attack(frame)
    if sync == "hand":
        best = None
        for f in range(int(frame), int(frame) + 10):
            d = (Vector(player.item_point("right", f)) - hp).length
            if best is None or d < best[0]:
                best = (d, f)
        f_flip = best[1]
    else:
        f_flip = frame_of(at(frame, LEVER_SHOW_TICKS))
    lever.flip(f_flip, ease)
    return f_flip


# ----------------------------------------------------------------------------------------------------
# piston
# ----------------------------------------------------------------------------------------------------
class Piston(_Part):
    """A piston or sticky piston (PistonBaseBlock + PistonMovingBlockEntity + PistonHeadRenderer).

    Looks: 'R' the retracted block model (piston / sticky_piston, extended=false); 'S' the extended base
    (piston_base) with the head drawn SHORT (piston_head short=true); 'L' the base with the long head. The head
    objects move; the look is chosen per frame from the head's travel over that frame's exposure."""

    kind = "piston"

    def __init__(self, kit_, cell, facing="north", sticky=False, extended=False, name=None, sky_light=None):
        super().__init__(kit_, cell, name)
        if facing not in DIRS6:
            raise RedstoneError("piston: facing is one of %s" % (DIRS6,))
        self.facing, self.sticky, self.extended0 = facing, bool(sticky), bool(extended)
        self.dir = VEC[facing].copy()
        self.head_cell = _add(self.cell, facing)
        kit_._claim(self.cell, self)
        if extended:
            kit_._claim(self.head_cell, self)
        dim = kit_._dim(sky_light)
        bid = "sticky_piston" if sticky else "piston"
        mat = _plain(bid, dim)
        self.retracted_ob = _object(kit_, self.name + "_block", _quads(bid, {"facing": facing, "extended": "false"}),
                                    mat, self.cell)
        self.base_ob = _object(kit_, self.name + "_base", _quads(bid, {"facing": facing, "extended": "true"}),
                               mat, self.cell)
        typ = "sticky" if sticky else "normal"
        self.head_long = _object(kit_, self.name + "_head", _quads("piston_head", {
            "facing": facing, "short": "false", "type": typ}), mat, self.head_cell)
        self.head_short = _object(kit_, self.name + "_head_short", _quads("piston_head", {
            "facing": facing, "short": "true", "type": typ}), mat, self.head_cell)
        self.looks = _Looks({"R": [self.retracted_ob], "S": [self.base_ob, self.head_short],
                             "L": [self.base_ob, self.head_long]}, "L" if extended else "R")
        self.moves = {}                 # t0 -> 'extend' | 'retract'
        self.pushed = {}                # t0 -> [movables]
        self._rekey()

    # ---- state over time
    def travel(self, t):
        """How far the head is out of the base at film time t (0 = retracted, 1 = extended): linear over the
        2 ticks of a move (progress += 0.5 per tick, rendered with the partial tick)."""
        d = 1.0 if self.extended0 else 0.0
        for t0, kind in sorted(self.moves.items()):
            if t < t0:
                break
            u = min(1.0, (t - t0) / PISTON_FRAMES)
            d = u if kind == "extend" else 1.0 - u
        return d

    def extended_at(self, t):
        """True when the piston is (becoming) extended at time t (its last move started was an extension)."""
        st = self.extended0
        for t0, kind in sorted(self.moves.items()):
            if t0 <= t + 1e-9:
                st = kind == "extend"
        return st

    def look_at_frame(self, f):
        """The look drawn on whole frame f (exposure [f, f + 0.5])."""
        ds = [self.travel(f + k * 0.125) for k in range(5)]
        if max(ds) <= 1e-6:
            return "R"
        return "S" if self.travel(f + 0.25) <= SHORT_ARM_UNTIL + 1e-9 else "L"

    def _rekey(self):
        self.looks.hist.clear()
        if self.moves:
            lo = int(math.floor(min(self.moves))) - 2
            hi = int(math.ceil(max(self.moves) + PISTON_FRAMES)) + 2
            prev = self.looks.initial
            for f in range(lo, hi + 1):
                lk = self.look_at_frame(f)
                if lk != prev:
                    self.looks.set(f, lk)
                    prev = lk
        self.looks.rekey()
        times = sorted({t for t0 in self.moves for t in (t0, t0 + PISTON_FRAMES)})
        for ob in (self.head_long, self.head_short):
            tr = self.kit.track(ob)
            tr.rest = Vector(self.head_cell)
            tr.moves = {}
            for t0, kind in self.moves.items():
                d = self.dir.copy() * (1.0 if kind == "extend" else -1.0)
                tr.moves[t0] = (t0, t0 + PISTON_FRAMES, d)
            # the head rests extended; when the piston starts retracted, its head sits one block back
            if not self.extended0:
                tr.rest = Vector(self.cell)
            tr.rekey()
        _ = times

    def _check_time(self, t0, kind):
        for t, k in self.moves.items():
            if abs(t - t0) < 1e-9:
                continue
            if abs(t - t0) < PISTON_FRAMES - 1e-6:
                raise RedstoneError("%s: a %s at %.2f overlaps the %s at %.2f (a move takes 2 ticks = %.1f frames)"
                                    % (self.name, kind, t0, k, t, PISTON_FRAMES))
        if self.extended_at(t0 - 1e-6) == (kind == "extend"):
            raise RedstoneError("%s: cannot %s at %.2f, it is already %s" % (
                self.name, kind, t0, "extended" if kind == "extend" else "retracted"))

    # ---- moves
    def extend(self, t, push="auto", ride=()):
        """Extend at film time t (the tick the piston is powered; PISTON_START_TICKS = 0). The head and every block
        in front of it travel one block in 2 ticks (2.4 frames), linear. push="auto": the kit's movable blocks in a
        line from the cell in front (at most PUSH_LIMIT = 12, else RedstoneError and nothing moves); push=[...] the
        same blocks given (movables, Breakables or cells, checked against the line). ride = things carried
        (kit.ride for one move). Returns the time the move ends (t + 2.4)."""
        t = float(t)
        old = self.pushed.pop(t, None)
        if old is not None:
            for m in old:
                m.unmove(t)
            self.moves.pop(t, None)
        self._check_time(t, "extend")
        line = self._line(t, push)
        end = _add(self.cell, self.facing, len(line) + 1)
        what = self.kit.occupied(end, t, ignore=line)
        if what is not None and not (isinstance(what, _Part) and what is self):
            raise RedstoneError("%s: cannot extend at %.2f: %s is in the way at %s (only the kit's movable blocks "
                                "are pushed)" % (self.name, t, what if what != "world" else "a block of the set",
                                                 end))
        self.moves[t] = "extend"
        self.pushed[t] = line
        for m in line:
            m.move(t, self.facing)
        for thing in ride:
            ob, character = _thing_object(thing)
            if character:
                _shift_character(ob, t, t + PISTON_FRAMES, self.dir.copy())
            else:
                tr = self.kit.track(ob)
                tr.moves[("ride", self.name, t)] = (t, t + PISTON_FRAMES, self.dir.copy())
                tr.rekey()
        self._rekey()
        return t + PISTON_FRAMES

    def retract(self, t, pull="auto"):
        """Retract at film time t: the head comes back in 2 ticks; a sticky piston pulls the block in front of its
        head with it (pull="auto": the kit's movable block there, if any; None: nothing). Returns t + 2.4."""
        t = float(t)
        old = self.pushed.pop(t, None)
        if old is not None:
            for m in old:
                m.unmove(t)
            self.moves.pop(t, None)
        self._check_time(t, "retract")
        pulled = []
        if self.sticky and pull is not None:
            front = _add(self.cell, self.facing, 2)
            if pull == "auto":
                m = self.kit.movable_at(front, t)
                pulled = [m] if m is not None else []
            else:
                m = _as_movable(self.kit, pull, t)
                if m.cell_at(t) != front:
                    raise RedstoneError("%s: a sticky piston pulls the block at %s, not %s" % (self.name, front,
                                                                                               m.cell_at(t)))
                pulled = [m]
        self.moves[t] = "retract"
        self.pushed[t] = pulled
        for m in pulled:
            m.move(t, OPPOSITE[self.facing])
        self._rekey()
        return t + PISTON_FRAMES

    def cancel(self, t):
        """Take back the move that starts at film time t (and the moves of the blocks it pushed or pulled)."""
        t = float(t)
        for m in self.pushed.pop(t, []):
            m.unmove(t)
        self.moves.pop(t, None)
        self._rekey()

    def _line(self, t, push):
        if push is None:
            push = []
        if push == "auto":
            line, c = [], _add(self.cell, self.facing)
            while True:
                m = self.kit.movable_at(c, t)
                if m is None:
                    break
                line.append(m)
                c = _add(c, self.facing)
                if len(line) > PUSH_LIMIT:
                    break
            if self.kit.world_block(_add(self.cell, self.facing)) is not None:
                raise RedstoneError("%s: the block in front of it at %s is part of the set's mesh: carve it in the "
                                    "hook and make it kit.block(...)" % (self.name, _add(self.cell, self.facing)))
        else:
            line = [_as_movable(self.kit, p, t) for p in push]
            for k, m in enumerate(line):
                want = _add(self.cell, self.facing, k + 1)
                if m.cell_at(t) != want:
                    raise RedstoneError("%s: pushed block %d is at %s, the line needs it at %s" % (
                        self.name, k + 1, m.cell_at(t), want))
        if len(line) > PUSH_LIMIT:
            raise RedstoneError("%s: %d blocks in front of it at %.2f: the game pushes at most %d "
                                "(PistonStructureResolver.MAX_PUSH_DEPTH) and the piston does not extend at all"
                                % (self.name, len(line), t, PUSH_LIMIT))
        return line

    def power(self, t):
        """(chain helper) powered at t: extends at t (no start delay). Returns t (what powers on from it)."""
        if not self.extended_at(t):
            self.extend(t)
        return float(t)

    def unpower(self, t):
        if self.extended_at(t):
            self.retract(t)
        return float(t)

    @property
    def objects(self):
        return [self.retracted_ob, self.base_ob, self.head_long, self.head_short]

    def head_point(self, t):
        """World centre of the head plate's face at time t."""
        return Vector(self.cell) + Vector((0.5, 0.5, 0.5)) + self.dir * (self.travel(t) + 0.5)


def _as_movable(kit_, p, t):
    if isinstance(p, _Movable):
        return p
    for m in kit_.movables:
        if m.breakable is p or m.object is p:
            return m
    if isinstance(p, (tuple, list)) and len(p) == 3:
        m = kit_.movable_at(_cell(p), t)
        if m is None:
            raise RedstoneError("redstone: no movable block at %s (make it with kit.block(...))" % (tuple(p),))
        return m
    if hasattr(p, "object") or isinstance(p, bpy.types.Object):       # a foreign Breakable or plain object
        b = p if hasattr(p, "object") else _Foreign(p)
        cell = _cell(b.object.location)
        m = _Movable(kit_, b, cell)
        kit_.movables.append(m)
        return m
    raise RedstoneError("redstone: %r cannot be pushed" % (p,))


class _Foreign:
    """A plain Object given to a piston: what _Movable needs of it."""

    def __init__(self, ob):
        self.object, self.name = ob, ob.name
        self.block_id = ob.get("mc_block", "object")
        self.full_cube = True

    def show(self, frame, visible=True):
        _vis_key(self.object, frame, visible)


class PistonDoor:
    """Door blocks (stacked or side by side) that sticky pistons pull sideways into a wall: for every door cell c a
    sticky piston at c + 2 * side facing back toward c, its head cell c + side inside the wall. closed=True: the
    pistons stand extended holding the blocks in the door cells (the doorway is shut). open(f) pulls them into
    the wall, close(f) pushes them back. The door cells, the head cells and the piston cells must be empty in the
    set's World (redstone.door_cells(cells, side) lists them for the hook)."""

    def __init__(self, kit_, cells, side, block="stone", closed=True, name="piston_door", sky_light=None):
        if side not in DIRS6:
            raise RedstoneError("piston_door: side is one of %s" % (DIRS6,))
        self.kit, self.name, self.side = kit_, name, side
        self.cells = [_cell(c) for c in cells]
        self.pistons, self.blocks = [], []
        for i, c in enumerate(self.cells):
            p = kit_.piston(_add(c, side, 2), OPPOSITE[side], sticky=True, extended=closed,
                            name="%s_piston_%d" % (name, i), sky_light=sky_light)
            b = kit_.block(block, c if closed else _add(c, side), name="%s_block_%d" % (name, i),
                           sky_light=sky_light)
            self.pistons.append(p)
            self.blocks.append(b)
        kit_.parts.append(self)

    def open(self, frame):
        """The pistons retract on `frame`, pulling the blocks into the wall. Returns the end time."""
        return self.kit.retract_all(self.pistons, frame)

    def close(self, frame):
        """The pistons extend on `frame`, pushing the blocks back into the doorway. Returns the end time."""
        return self.kit.extend_all(self.pistons, frame)

    def is_open(self, t):
        return not self.pistons[0].extended_at(t)

    def show(self, frame, visible=True):
        for p in self.pistons:
            p.show(frame, visible)
        for b in self.blocks:
            b.show(frame, visible)

    @property
    def objects(self):
        return [o for p in self.pistons for o in p.objects] + [b.object for b in self.blocks]

    def seam(self):
        """World point in the middle of the door's face on the side away from the pistons' wall... the doorway."""
        c = Vector(self.cells[0]) + Vector((0.5, 0.5, 0.5))
        return c


def door_cells(cells, side):
    """Every cell a piston_door needs empty in the World: the door cells, the head cells, the piston cells."""
    out = []
    for c in cells:
        c = _cell(c)
        out += [c, _add(c, side), _add(c, side, 2)]
    return out


class PistonRow:
    """Pistons side by side, each with one block on its arm (extended: at cell + 2 * facing; retracted: at
    cell + facing). retract(f) / extend(f) move all of them on the same tick."""

    def __init__(self, kit_, cells, facing, carry="oak_planks", extended=True, sticky=True, name="piston_row",
                 sky_light=None):
        self.kit, self.name = kit_, name
        self.pistons, self.blocks = [], []
        for i, c in enumerate(cells):
            c = _cell(c)
            p = kit_.piston(c, facing, sticky=sticky, extended=extended, name="%s_%d" % (name, i),
                            sky_light=sky_light)
            self.pistons.append(p)
            if carry:
                b = kit_.block(carry, _add(c, facing, 2 if extended else 1), name="%s_%s_%d" % (name, carry, i),
                               sky_light=sky_light)
                self.blocks.append(b)
        kit_.parts.append(self)

    def retract(self, frame):
        """Every piston retracts on `frame` (the sticky ones pull their blocks one block in). Returns end time."""
        return self.kit.retract_all(self.pistons, frame)

    def extend(self, frame):
        """Every piston extends on `frame`, pushing its block out. Returns the end time."""
        return self.kit.extend_all(self.pistons, frame)

    def show(self, frame, visible=True):
        for p in self.pistons:
            p.show(frame, visible)
        for b in self.blocks:
            b.show(frame, visible)


# ----------------------------------------------------------------------------------------------------
# redstone dust
# ----------------------------------------------------------------------------------------------------
def wire_color(power):
    """The colour the game tints dust with at a power level 0..15 (RedstoneWireBlock COLORS), 0..255."""
    return WIRE_COLORS[max(0, min(15, int(power)))]


def dust_shape(state):
    """The name of the shape a dust state is drawn as: dot, cross, line, corner, t, end ... (for checks)."""
    con = [d for d in HORIZONTAL if state[d] != "none"]
    ups = [d for d in HORIZONTAL if state[d] == "up"]
    n = len(con)
    if n == 0:
        name = "dot"
    elif n == 4:
        name = "cross"
    elif n == 3:
        name = "t"
    elif n == 2:
        name = "line" if OPPOSITE[con[0]] == con[1] else "corner"
    else:
        name = "end"
    return name + ("+up:" + ",".join(ups) if ups else "")


DUST_LAYER_PX = 0.05                 # the dust models stack coplanar quads (dot + four half lines at y 0.25): each
                                     # multipart piece is lifted this much above the one before it (Cycles skips a
                                     # coplanar quad behind a cut-out texel: arms vanished under the dot's square)


def dust_quads(props):
    """The quads of a redstone_wire state, as the game draws it, made safe for a ray tracer: the multipart pieces in
    their order, each flat piece DUST_LAYER_PX above the previous one, the downward twins of the flat pieces
    dropped (dust always lies on a block: they are never seen). The pieces that climb a wall are kept as they are."""
    out = []
    for k, part in enumerate(mc.resolve_blockstate("redstone_wire", props)):
        for q in mc.bake_part(part):
            ys = {round(p[1], 4) for p in q.pts}
            if len(ys) == 1:                                  # a flat piece (y 0.25 +- the thin offset)
                if next(iter(ys)) < 0.25:
                    continue                                   # its underside
                pts = [(p[0], p[1] + k * DUST_LAYER_PX, p[2]) for p in q.pts]
                q = mc.Quad(pts, q.uvs, q.texture, q.tintindex, q.overlay, q.cull, q.facing, q.thin,
                            getattr(q, "shade", None))
            out.append(q)
    return out


class Wire(_Part):
    """Redstone dust over a set of cells: the game's shape in each cell (redstone_wire multipart from the
    connections), tinted by its power level, one object per (cell, level) shown when that level is keyed."""

    kind = "wire"

    def __init__(self, kit_, cells, power=0, dots=(), source=None, name=None, sky_light=None):
        cells = [_cell(c) for c in cells]
        if not cells:
            raise RedstoneError("wire: no cells")
        super().__init__(kit_, cells[0], name)
        self.cells = cells
        for c in cells:
            kit_._claim(c, self)
        self.dots = {_cell(c) for c in dots}
        self.source = _cell(source) if source is not None else cells[0]
        self.dim = kit_._dim(sky_light)
        self.states = {c: kit_.wire_state(c, c in self.dots) for c in cells}
        self.looks_by_cell = {}
        self.hist = {c: {} for c in cells}           # cell -> {frame: level}
        p0 = power if isinstance(power, dict) else {c: int(power) for c in cells}
        self.level0 = {c: int(p0.get(c, 0)) for c in cells}
        for c in cells:
            self._ensure(c, self.level0[c])
        self.links = self._links()
        self._rekey_all()

    def _links(self):
        """Which dust cells the game treats as connected: a neighbour at the same height, one block up a side
        ('up') or one block down past the edge of the block it lies on ('side' toward a dust below)."""
        out = {c: set() for c in self.cells}
        cs = set(self.cells)
        for c in self.cells:
            for d in HORIZONTAL:
                s = self.states[c][d]
                if s == "none":
                    continue
                n = _add(c, d)
                cands = [n] + ([_add(n, "up")] if s == "up" else [_add(n, "down")])
                for cand in cands:
                    if cand in cs:
                        out[c].add(cand)
                        out[cand].add(c)
        return out

    def _ensure(self, c, level):
        lk = self.looks_by_cell.get(c)
        if lk is None:
            lk = self.looks_by_cell[c] = _Looks({}, self.level0.get(c, 0) if hasattr(self, "level0") else level)
        if level not in lk.looks:
            props = dict(self.states[c])
            props["power"] = str(level)
            quads = dust_quads(props)
            tint = wire_color(level)
            glow = (DUST_GLOW * level / 15.0, None, 0.0) if level > 0 and DUST_GLOW > 0 else None

            def mat(q, tint=tint, glow=glow):
                return _material(q.texture, tint, getattr(q, "shade", None), glow, None if glow else self.dim)

            ob = _object(self.kit, "%s_%d_%d_%d_p%d" % (self.name, c[0], c[1], c[2], level), quads, mat, c)
            ob.visible_shadow = False                  # dust is a flat overlay: it casts no shadow worth tracing
            lk.add(level, [ob])
        return lk

    def _rekey_all(self):
        for c in self.cells:
            lk = self._ensure(c, self.level0[c])
            for f, lev in self.hist[c].items():
                self._ensure(c, lev)
            lk.hist = dict(self.hist[c])
            lk.rekey()

    def distances(self, source=None):
        """Steps along the dust from the source cell to every cell (None: not connected)."""
        src = _cell(source) if source is not None else self.source
        if src not in self.links:
            # a source BESIDE the line (a lever, a torch): the dust cells next to it are 0 steps away
            starts = [c for c in self.cells if sum(abs(a - b) for a, b in zip(c, src)) == 1]
        else:
            starts = [src]
        dist = {c: None for c in self.cells}
        todo = list(starts)
        for c in starts:
            dist[c] = 0
        while todo:
            c = todo.pop(0)
            for n in self.links[c]:
                if dist[n] is None:
                    dist[n] = dist[c] + 1
                    todo.append(n)
        return dist

    def levels(self, frame, source=None, level=15):
        """{cell: power} the game gives the line at `frame` from that source: level - steps (>= 0)."""
        dist = self.distances(source)
        return {c: (max(0, int(level) - d) if d is not None else 0) for c, d in dist.items()}

    def set_levels(self, frame, levels):
        """Key explicit power levels {cell: 0..15} from `frame` on."""
        f = int(frame)
        for c, lev in levels.items():
            c = _cell(c)
            if c not in self.hist:
                raise RedstoneError("%s: %s is not one of its cells" % (self.name, c))
            self.hist[c][f] = max(0, min(15, int(lev)))
        self._rekey_all()

    def power(self, frame, source=None, level=15, ripple=0):
        """The line lit from `source` (default: the wire's source cell; a cell beside the line = a lever / torch
        there) at power `level`, falling by one per block of dust. All on one frame (the game: one tick), or
        ripple=N: block by block away from the source over N frames (a film choice). Returns frame."""
        f0 = frame_of(frame)
        dist = self.distances(source)
        far = max([d for d in dist.values() if d is not None] or [0])
        for c, d in dist.items():
            lev = max(0, int(level) - d) if d is not None else 0
            f = f0
            if ripple and far and d is not None:
                f = f0 + int(round(float(ripple) * d / float(far)))
            for ff in [k for k in self.hist[c] if f0 <= k < f]:      # a ripple: nothing stale before its turn
                del self.hist[c][ff]
            self.hist[c][f] = lev
        self._rekey_all()
        return float(frame)

    def unpower(self, frame):
        """The whole line dark (power 0) on one frame, as the game updates it within one tick. Returns frame."""
        f = frame_of(frame)
        for c in self.cells:
            self.hist[c][f] = 0
        self._rekey_all()
        return float(frame)

    def level_at(self, cell, frame):
        c = _cell(cell)
        return _at(self.hist[c], frame, self.level0[c])

    def show(self, frame, visible=True):
        for lk in self.looks_by_cell.values():
            lk.show(frame, visible)

    @property
    def objects(self):
        return [o for lk in self.looks_by_cell.values() for obs in lk.looks.values() for o in obs]


# ----------------------------------------------------------------------------------------------------
# repeater, lamp, torch
# ----------------------------------------------------------------------------------------------------
def _glow_for_texture(texture):
    if texture == "block/redstone_torch":
        return TORCH_GLOW
    if texture == "block/repeater_on":
        return REPEATER_GLOW
    return None


class Repeater(_Part):
    """A repeater (RepeaterBlock) with its delay 1..4, unlit / lit (models repeater_<n>tick[_on])."""

    kind = "repeater"

    def __init__(self, kit_, cell, toward="north", delay=1, powered=False, name=None, sky_light=None):
        super().__init__(kit_, cell, name)
        if toward not in HORIZONTAL or int(delay) not in (1, 2, 3, 4):
            raise RedstoneError("repeater: toward north | east | south | west, delay 1..4")
        kit_._claim(self.cell, self)
        self.toward, self.delay = toward, int(delay)
        self.facing = OPPOSITE[toward]                      # the game's FACING: the input side
        dim = kit_._dim(sky_light)
        obs = {}
        for on in (False, True):
            props = {"facing": self.facing, "delay": str(self.delay), "locked": "false",
                     "powered": "true" if on else "false"}
            glow = (lambda q: _glow_for_texture(q.texture)) if on else None
            obs[on] = _object(kit_, "%s_%s" % (self.name, "on" if on else "off"), _quads("repeater", props),
                              _plain("repeater", dim, glow), self.cell)
        self.looks = _Looks({False: [obs[False]], True: [obs[True]]}, bool(powered))

    @property
    def delay_ticks(self):
        return REPEATER_TICKS_PER_DELAY * self.delay

    def set(self, frame, powered):
        """Lit / unlit from whole frame `frame` on."""
        self.looks.set(int(frame), bool(powered))
        self.looks.rekey()

    def power(self, t):
        """Its input powered at film time t: the output (and the lit model) comes delay x 2 ticks later. Returns
        that time."""
        t1 = at(t, self.delay_ticks)
        self.set(frame_of(t1), True)
        return t1

    def unpower(self, t):
        t1 = at(t, self.delay_ticks)
        self.set(frame_of(t1), False)
        return t1


def _point_light(kit_, name, location, watts, color, radius):
    ob = _props.make_light("lantern", kit_.collection)
    ob.name = name
    ob.data.name = name
    ob.data.energy = watts
    ob.data.color = color
    ob.data.shadow_soft_size = radius
    ob["base_energy"] = watts
    ob["mc_light"] = "redstone"
    ob.location = location
    return ob


class _Lit(_Part):
    """A part with a lit look and a point light that is on exactly while the lit look is shown."""

    def _rekey_lights(self):
        lk = self.looks
        frames = sorted(set(lk.hist) | set(lk.shown))
        times = [(frames[0] if frames else 1) - 1] + frames
        states = [(lk.initial, True)] + [(lk.at(f), _at(lk.shown, f, True)) for f in frames]
        now = bpy.context.scene.frame_current
        for L in self.lights:
            vals = [0.0 if (shown and self._lit_look(c)) else 1.0 for c, shown in states]
            for path in ("hide_render", "hide_viewport"):
                _keys(L, path, times, vals)
            L.hide_render = L.hide_viewport = not (_at(lk.shown, now, True) and self._lit_look(lk.at(now)))

    def _lit_look(self, look):
        return bool(look)


class Lamp(_Lit):
    """A redstone lamp (RedstoneLampBlock): off / on; on is a light source (LAMP_WATTS at its centre; the lamp's
    own faces do not block it: shadow linking)."""

    kind = "lamp"

    def __init__(self, kit_, cell, lit=False, name=None, sky_light=None, watts=None):
        super().__init__(kit_, cell, name)
        kit_._claim(self.cell, self)
        dim = kit_._dim(sky_light)
        off = _object(kit_, self.name + "_off", _quads("redstone_lamp", {"lit": "false"}), _plain("redstone_lamp", dim),
                      self.cell)
        on = _object(kit_, self.name + "_on", _quads("redstone_lamp", {"lit": "true"}), _plain("redstone_lamp"),
                     self.cell)
        self.looks = _Looks({False: [off], True: [on]}, bool(lit))
        L = _point_light(kit_, self.name + "_light", self.center, LAMP_WATTS if watts is None else watts,
                         _props.TORCH_COLOR, LAMP_RADIUS)
        blk = bpy.data.collections.new(self.name + "_blockers")
        blk.objects.link(on)
        blk.objects.link(off)
        L.light_linking.blocker_collection = blk
        for co in blk.collection_objects:
            co.light_linking.link_state = "EXCLUDE"
        self.lights = [L]
        self.light = L
        self._rekey_lights()

    def set(self, frame, lit):
        """On / off from whole frame `frame` on (the light with it)."""
        self.looks.set(int(frame), bool(lit))
        self.looks.rekey()
        self._rekey_lights()

    def power(self, t):
        """Powered at t: lit at once (LAMP_ON_TICKS = 0). Returns t."""
        self.set(frame_of(t), True)
        return float(t)

    def unpower(self, t):
        """Unpowered at t: dark LAMP_OFF_TICKS = 4 ticks later (4.8 frames). Returns that time."""
        t1 = at(t, LAMP_OFF_TICKS)
        self.set(frame_of(t1), False)
        return t1

    def lit_at(self, frame):
        return bool(self.looks.at(frame))


class Torch(_Lit):
    """A redstone torch (standing or on a wall), lit / unlit, with its weak light (REDSTONE_TORCH_WATTS)."""

    kind = "torch"

    def __init__(self, kit_, cell, wall=None, lit=True, frame=None, name=None, sky_light=None, watts=None):
        super().__init__(kit_, cell, name)
        if wall is not None and wall not in HORIZONTAL:
            raise RedstoneError("torch: wall = north | east | south | west (the side it leans out to) or None")
        kit_._claim(self.cell, self)
        self.wall = wall
        dim = kit_._dim(sky_light)
        bid = "redstone_torch" if wall is None else "redstone_wall_torch"
        looks = {}
        for on in (False, True):
            props = {"lit": "true" if on else "false"}
            if wall:
                props["facing"] = wall
            quads = _quads(bid, props)
            glow = (lambda q: _glow_for_texture(q.texture)) if on else None
            looks[on] = [_object(kit_, "%s_%s" % (self.name, "lit" if on else "unlit"), quads,
                                 _plain(bid, None if on else dim, glow), self.cell)]
            if on:
                top = max(p[1] for q in quads for p in q.pts)
                pts = [mc.to_blender(p) for q in quads for p in q.pts if p[1] >= top - 3.0]
                self.head = Vector(self.cell) + Vector(np.mean(pts, axis=0))
        looks[None] = []
        self.looks = _Looks(looks, None if frame is not None else bool(lit))
        for ob in looks[True]:
            ob.visible_shadow = False                    # the flame's halo must not shadow its own light
        L = _point_light(kit_, self.name + "_light", self.head, REDSTONE_TORCH_WATTS if watts is None else watts,
                         REDSTONE_TORCH_COLOR, 0.15)
        self.lights = [L]
        self.light = L
        if frame is not None:
            self.looks.set(int(frame), bool(lit))
        self.looks.rekey()
        self._rekey_lights()

    def _lit_look(self, look):
        return look is True

    def set(self, frame, lit):
        """Lit / unlit from whole frame `frame` on."""
        self.looks.set(int(frame), bool(lit))
        self.looks.rekey()
        self._rekey_lights()

    def remove(self, frame):
        """Gone from `frame` on (broken / picked up)."""
        self.looks.set(int(frame), None)
        self.looks.rekey()
        self._rekey_lights()

    def plant(self, frame, player=None, hand="right", consume=False):
        """Placed: with a player, his arm swing starts ON `frame` (engine.players attack) and the torch appears ON
        the frame after (the game predicts the placement in the tick of the click); without one, it appears ON
        `frame`. consume=True empties his hand from that frame. Returns the frame it appears on (the time its
        signal starts: chain on from it)."""
        f = int(frame)
        self.looks.initial = None                    # not there before it is planted
        if player is not None:
            player.attack(f, hand)
            f += 1
            if consume:
                player.hold(None, hand, frame=f)
        self.looks.set(f, True)
        self.looks.rekey()
        self._rekey_lights()
        return float(f)

    def power(self, t):
        """(chain helper) the block it stands on powered at t: the torch goes OUT 2 ticks later (an inverter).
        Returns that time."""
        t1 = at(t, TORCH_TOGGLE_TICKS)
        self.set(frame_of(t1), False)
        return t1

    def unpower(self, t):
        t1 = at(t, TORCH_TOGGLE_TICKS)
        self.set(frame_of(t1), True)
        return t1


def hold_torch(player, hand="right", frame=None, glow=True, watts=HELD_TORCH_WATTS):
    """engine.players hold("redstone_torch") with its glow: the head texels emissive (TORCH_GLOW) and a small
    point light at the torch head that is on exactly while the item is shown. Returns the item object."""
    ob = player.hold("redstone_torch", hand, frame=frame)
    if ob is None or not glow:
        return ob
    ob.data = ob.data.copy()
    tex = ob.data.materials[0].get("mc_texture", "block/redstone_torch") if ob.data.materials else \
        "block/redstone_torch"
    strength, above, base = TORCH_GLOW
    mat = mc.material(tex, alpha="OPAQUE", emission=strength, emit_above=above, emit_base=base)
    mat.cycles.emission_sampling = "NONE"
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    if watts:
        L = _props.make_light("torch", ob.users_collection[0] if ob.users_collection else None)
        L.name = ob.name + "_glow"
        L.data.energy = watts
        L.data.color = REDSTONE_TORCH_COLOR
        L.data.shadow_soft_size = 0.1
        L["base_energy"] = watts
        L["mc_light"] = "redstone"
        L.parent = ob
        L.location = (0.0, 0.0, 0.1)            # the torch head: sprite rows 4..8 lie above the sprite centre
        for path in ("hide_render", "hide_viewport"):
            fc = L.driver_add(path)
            drv = fc.driver
            drv.type = "SCRIPTED"
            var = drv.variables.new()
            var.name = "h"
            var.type = "SINGLE_PROP"
            var.targets[0].id = ob
            var.targets[0].data_path = path
            drv.expression = "h"
        ob["redstone_glow_light"] = L.name
    return ob


# ----------------------------------------------------------------------------------------------------
# sequencing: "powered from frame f"
# ----------------------------------------------------------------------------------------------------
def signal(frame, *steps):
    """Play a small circuit in the game's order: each step's input is powered when the step before it puts out its
    signal. A step is a part (wire, repeater, lamp, piston, torch, lever) or a tuple of parts powered together.
    Returns the time the last step puts out its signal.
        t = torch.plant(f, player=efe); redstone.signal(t, wire, repeater, (lamp, piston))"""
    t = float(frame)
    for step in steps:
        if isinstance(step, (tuple, list)):
            t = max(p.power(t) for p in step)
        else:
            t = step.power(t)
    return t


def unsignal(frame, *steps):
    """The same circuit switched off (repeaters keep their delay, lamps go out 4 ticks late)."""
    t = float(frame)
    for step in steps:
        if isinstance(step, (tuple, list)):
            t = max(p.unpower(t) for p in step)
        else:
            t = step.unpower(t)
    return t


# ----------------------------------------------------------------------------------------------------
# hook-time helpers (inside build_village(edit=...))
# ----------------------------------------------------------------------------------------------------
def carve(b, cells):
    """Inside the village hook: take these cells out of the World (they become parts drawn as their own objects).
    Returns {cell: (block_id, props) | None} of what was there."""
    w = getattr(b, "w", b)
    out = {}
    for c in cells:
        c = _cell(c)
        out[c] = w.get(*c)
        w.set(c[0], c[1], c[2], None)
    return out


def bench(b, x0, y0, x1, y1, block="smooth_stone", name="redstone_bench", level=None):
    """Inside the village hook: a level stone floor for redstone parts (the grass top of every column replaced by
    `block`, plants cleared, the columns reserved). Returns dict(z = the floor's top = the z of the cells the
    parts stand in, cells, name)."""
    zs = [b.ground(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    zs = [z for z in zs if z is not None]
    z = int(round(level if level is not None else max(set(zs), key=zs.count)))
    cells = []
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if b.ground(x, y) != z:
                b.set_ground(x, y, z)
            b.clear_plants(x, y)
            b.w.set(x, y, z - 1, block)
            cells.append((x, y, z - 1))
            b.reserved.add((x, y))
    res = dict(z=z, cells=cells, name=name, box=(x0, y0, x1, y1))
    b.v.sets[name] = res
    return res



# ----------------------------------------------------------------------------------------------------
# PROOF: the parts in the real village, through the real look (golden hour, the look-dev sun)
# ----------------------------------------------------------------------------------------------------
SKY = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")
# where the proof areas sit (Blender cells; z 0 = the first cell above the levelled ground). Clear grass north-east
# of house_f and along the meadow east of the exit road (out of every finished film's frame).
AREAS = {
    "sheet_a": (9, 22, 16, 28),      # pistons and levers
    "sheet_b": (17, 22, 25, 31),     # repeaters, lamps, torches, redstone block
    "dust": (3, 31, 12, 40),         # dust shapes and the 16 power levels
    "bench": (17, 16, 24, 21),       # beat 7 of "Leg Day": torch, dust, repeater, lamp, piston
    "lever": (5, 23, 8, 26),         # a stone pier with a wall lever, flipped by a player
    "column": (30, 12, 34, 16),      # beat 9: an upward piston under twelve iron blocks
    "door": (4, 42, 10, 49),         # "Two Apples": the one-block cell whose back wall opens on sticky pistons
    "row": (11, 41, 22, 52),         # beats 13 / 19: sticky pistons in a wall top with planks and anvils
}
DOOR = dict(cells=[(7, 47, 0), (7, 47, 1)], side="east", cell=(7, 46), villager=(7.5, 46.45, 0.0))
COLUMN = dict(piston=(32, 14, 0), lever=(33, 14, 0), blocks=12)
ROW = dict(cells=[(x, 43, 3) for x in (14, 15, 16, 17)], facing="north", lever=(13, 42, 4),
           dust=[(x, 42, 4) for x in (14, 15, 16, 17)])
BENCH = dict(torch=(19, 18, 0), dust=[(20, 18, 0), (21, 18, 0)], repeater=(22, 18, 0), lamp=(23, 18, 1),
             block=(23, 18, 0), piston=(23, 17, 0), piston_facing="south", player=(20.6, 19.55, 0.0))
LEVER = dict(pier=(7, 24), lever=(7, 25, 1), facing="north")


def proof_set(b):
    """The village hook of the proof: stone floors and the static blocks the parts stand on, in AREAS."""
    for name in ("sheet_a", "sheet_b", "dust", "bench", "column", "row"):
        x0, y0, x1, y1 = AREAS[name]
        bench(b, x0, y0, x1, y1, name="redstone_" + name, level=0)
    w = b.w
    for x0, y0, x1, y1 in AREAS.values():                    # no tufts between the proof cameras and the parts
        for x in range(x0 - 4, x1 + 5):
            for y in range(y0 - 4, y1 + 7):
                if b.ground(x, y) is not None:
                    b.clear_plants(x, y)
    # sheet A: blocks for the wall and ceiling levers
    for x in (12, 13):
        w.set(x, 22, 0, "stone")
    for x in (10, 11):
        w.set(x, 23, 2, "stone")
    # sheet B: blocks for the wall torches
    for x in (20, 21):
        w.fill(x, 23, 0, x, 23, 1, "stone")
    # dust: the block a dust climbs
    w.set(7, 35, 0, "stone")
    # bench: the block under the lamp (the repeater powers it, it powers the lamp and the piston)
    w.set(BENCH["block"][0], BENCH["block"][1], BENCH["block"][2], "stone")
    # the lever pier
    for x0, y0, x1, y1 in (AREAS["lever"],):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                b.clear_plants(x, y)
                b.reserved.add((x, y))
    w.fill(LEVER["pier"][0], LEVER["pier"][1], 0, LEVER["pier"][0], LEVER["pier"][1], 1, "stone")
    # the row: a 2-thick stone wall 4 high, the pistons' course left open (they are parts), dust on the back
    w.fill(13, 42, 0, 18, 43, 3, "stone")
    for c in ROW["cells"]:
        w.set(c[0], c[1], c[2], None)
    # the door: a closed stone box with the aisle, the cell, the door cells, the pistons' wall and the box behind
    x0, y0, x1, y1 = AREAS["door"]
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            b.clear_plants(x, y)
            b.reserved.add((x, y))
    w.fill(x0, y0, -1, x1, y1, 2, "stone")
    hollow = [(x, y, z) for x in range(5, 10) for y in range(43, 46) for z in (0, 1)]           # the aisle
    hollow += [(7, 46, z) for z in (0, 1)] + [(7, 48, z) for z in (0, 1)]                        # cell, box
    hollow += door_cells(DOOR["cells"], DOOR["side"])
    hollow += [(x, 46, z) for x in (8, 9) for z in (0, 1)]      # the end wall's aisle side, open for the camera
    for c in hollow:
        w.set(c[0], c[1], c[2], None)
    b.torch((6, 45, 1), "wall_torch", {"facing": "south"}, group="rs_door")
    b.torch((5, 44, 1), "wall_torch", {"facing": "east"}, group="rs_door")
    b.allow(AREAS["door"])
    b.v.sets["redstone_proof"] = dict(areas=AREAS)
    return b.v.sets["redstone_proof"]


def build_proof(scene, sky=None):
    """The proof film: one shot per proof (see PROOFS), every part built in the village by proof_set + a Kit.
    Returns dict(film, stage, village, kit, shots, frames: {still name: frame})."""
    from films import lookdev

    from . import look, players, shots, village

    cfg = dict(SKY, **(sky or {}))
    v = village.build_village(scene, seed=1, edit=proof_set)
    skyobj = look.set_time(scene, cfg["preset"], sun_azimuth=cfg["az"], sun_elevation=cfg["el"])
    look.setup_compositor(scene, bloom=cfg["bloom"], grade=cfg["grade"])
    film = shots.Film(scene, fps=FPS)
    st = lookdev.Stage(scene, film, v, skyobj)
    k = kit(v)
    out = dict(film=film, stage=st, village=v, kit=k, shots={}, frames={}, parts={})
    P = out["parts"]

    def cam(s, pos, target, lens, fstop=5.6, focus=None):
        s.lens(lens, fstop)
        s.move(pos, target)
        s.focus(focus if focus is not None else target)

    # ---- sheet A: pistons and levers (camera from the north: the faces the parts turn north catch the sun)
    k.piston((15, 27, 0), "north")
    k.piston((13, 27, 0), "north", sticky=True)
    k.piston((11, 27, 0), "up", sticky=True)
    k.piston((16, 25, 0), "west", extended=True)
    k.piston((13, 25, 0), "west", sticky=True, extended=True)
    k.piston((10, 25, 0), "up", extended=True)
    P["lever_floor_off"] = k.lever((15, 23, 0), "floor", "north")
    P["lever_floor_on"] = k.lever((14, 23, 0), "floor", "north", powered=True)
    P["lever_wall_off"] = k.lever((13, 23, 0), "wall", "north")
    P["lever_wall_on"] = k.lever((12, 23, 0), "wall", "north", powered=True)
    P["lever_ceiling_off"] = k.lever((11, 23, 1), "ceiling", "north")
    P["lever_ceiling_on"] = k.lever((10, 23, 1), "ceiling", "north", powered=True)
    s = st.shot("sheet_a", 0.5)
    cam(s, (12.9, 31.4, 5.2), (12.9, 25.3, 0.4), 25, 11.0)
    out["frames"]["sheet_a"] = s.frame_start + 2
    st.lights(s, scale=1.0, near=(12.5, 25.0, 1.0), radius=6.0)

    # ---- sheet B: repeaters, lamps, torches, redstone block
    for i, d in enumerate((1, 2, 3, 4)):
        k.repeater((24 - i, 28, 0), "south", delay=d)
    k.repeater((19, 28, 0), "south", delay=1, powered=True)
    k.repeater((18, 28, 0), "south", delay=4, powered=True)
    k.lamp((24, 26, 0))
    k.lamp((22, 26, 0), lit=True)
    k.block("redstone_block", (20, 26, 0))
    k.torch((24, 24, 0), lit=True)
    k.torch((23, 24, 0), lit=False)
    k.torch((21, 24, 1), wall="north", lit=True)
    k.torch((20, 24, 1), wall="north", lit=False)
    s = st.shot("sheet_b", 0.5)
    cam(s, (21.1, 32.5, 5.0), (21.1, 26.3, 0.4), 25, 11.0)
    out["frames"]["sheet_b"] = s.frame_start + 2

    # ---- dust: shapes, and the 16 power levels along a U from a lever
    u = [(x, 40, 0) for x in range(4, 12)] + [(11, 39, 0)] + [(x, 38, 0) for x in range(11, 3, -1)]
    P["lever_dust"] = k.lever((3, 40, 0), "floor", "west", powered=True)
    P["dust_u"] = wu = k.wire(u, source=(3, 40, 0))
    wu.power(1, source=(3, 40, 0))
    P["dust_cross"] = k.wire([(4, 36, 0)], power=15)
    P["dust_dot"] = k.wire([(6, 36, 0)], power=15, dots=[(6, 36, 0)])
    P["dust_t"] = k.wire([(9, 35, 0), (10, 35, 0), (11, 35, 0), (10, 36, 0)], power=15)
    P["dust_corner"] = k.wire([(4, 34, 0), (5, 34, 0), (5, 35, 0)], power=9)
    P["dust_climb"] = k.wire([(7, 34, 0), (7, 35, 1)], power=15)
    s = st.shot("dust", 0.5)
    cam(s, (7.6, 28.8, 9.4), (7.6, 36.0, 0.1), 30, 8.0)
    out["frames"]["dust"] = s.frame_start + 2

    # ---- bench: beat 7 (the narrator plants the torch; the line, the repeater, the lamp, the piston)
    s = st.shot("bench", 1.0)
    f0 = s.frame_start
    efe = players.add_player(st, "efe", "efe", slim=True)
    efe.place(f0, BENCH["player"], 0.0)
    hold_torch(efe, "right")
    torch = P["bench_torch"] = k.torch(BENCH["torch"])                        # not there until plant()
    wire = P["bench_wire"] = k.wire(BENCH["dust"], source=BENCH["torch"])
    rep = P["bench_repeater"] = k.repeater(BENCH["repeater"], "east", delay=1)
    lamp = P["bench_lamp"] = k.lamp(BENCH["lamp"])
    pis = P["bench_piston"] = k.piston(BENCH["piston"], BENCH["piston_facing"])
    efe.look_at(f0, Vector(BENCH["torch"]) + Vector((0.5, 0.5, 0.3)), ease=0)
    t = torch.plant(f0 + 4, player=efe)
    end = signal(t, wire, rep, (lamp, pis))
    out["bench_times"] = dict(click=f0 + 4, torch=t, repeater_out=at(t, rep.delay_ticks), end=end)
    efe.look_at(f0 + 9, lamp.center, ease=6)
    st.use(s, efe)
    cam(s, (21.5, 14.6, 1.3), (21.5, 18.9, 1.0), 24, 3.2, focus=efe.head)
    st.hero(s, "narrator", efe)
    out["frames"]["bench"] = [f0 + 3, f0 + 5, f0 + 7, f0 + 8, f0 + 9, f0 + 13]

    # ---- the lever, flipped by a player's hand
    s = st.shot("lever", 0.75)
    f0 = s.frame_start
    lev = P["lever_pier"] = k.lever(LEVER["lever"], "wall", LEVER["facing"])
    steve = players.add_player(st, "steve", "steve")
    pos, yaw = lev.stand()
    steve.place(f0, pos, yaw)
    steve.look_at(f0, lev.hand_point(f0, 0.5), ease=0)
    ff = flip_by(steve, lev, f0 + 4, sync="hand", look=False)
    out["lever_flip"] = ff
    out["lever_reach"] = min(((Vector(steve.item_point("right", f / 2.0)) - lev.hand_point(f0, 0.5)).length, f / 2.0)
                             for f in range(2 * f0 + 8, 2 * f0 + 28))
    st.use(s, steve)
    cam(s, (5.0, 28.3, 2.2), (7.45, 25.7, 1.45), 30, 4.0, focus=lev.hand_point(f0))
    out["frames"]["lever"] = [f0 + 3, ff - 1, ff, f0 + 14]

    # ---- the column: an upward piston and twelve iron blocks; the narrator's lever beside it
    s = st.shot("column", 1.0)
    f0 = s.frame_start
    cp = P["column_piston"] = k.piston(COLUMN["piston"], "up")
    x, y, z = COLUMN["piston"]
    P["column_blocks"] = [k.block("iron_block", (x, y, z + i)) for i in range(1, COLUMN["blocks"] + 1)]
    cl = P["column_lever"] = k.lever(COLUMN["lever"], "floor", "east")
    t = cl.flip(f0 + 6)
    cp.power(t)
    cam(s, (36.6, 8.4, 0.55), (32.4, 14.4, 6.6), 18, 8.0, focus=(32.5, 14.5, 4.0))
    out["frames"]["column"] = [f0 + 5, f0 + 6, f0 + 7, f0 + 10]

    # ---- the row: four sticky pistons in a wall top, planks on their arms, anvils on the planks
    s = st.shot("row", 1.0)
    f0 = s.frame_start
    row = P["row"] = k.piston_row(ROW["cells"], ROW["facing"], carry="oak_planks", extended=True)
    P["row_anvils"] = [k.block("anvil", (c[0], c[1] + 2, c[2] + 1), {"facing": "west"}) for c in ROW["cells"]]
    rl = P["row_lever"] = k.lever(ROW["lever"], "floor", "east", powered=True)
    rw = P["row_wire"] = k.wire(ROW["dust"], source=ROW["lever"])
    rw.power(1, source=ROW["lever"])
    t = rl.flip(f0 + 6)
    rw.unpower(t)
    row.retract(t)
    cam(s, (20.6, 50.4, 6.2), (15.4, 43.6, 3.5), 24, 8.0)
    out["frames"]["row"] = [f0 + 5, f0 + 7, f0 + 10]

    # ---- the door of "Two Apples": the librarian in his cell, the back wall opening behind him
    s = st.shot("door", 2.0)
    f0 = s.frame_start
    door = P["door"] = k.piston_door(DOOR["cells"], DOOR["side"], block="stone", closed=True)
    dad = st.actor("dad", "librarian")
    dad.place(f0, DOOR["villager"], 0.0)
    t_open = f0 + 8
    door.open(t_open)
    door.close(f0 + 30)
    st.use(s, dad)
    cam(s, (9.55, 43.6, 1.3), (7.7, 47.1, 0.95), 18, 5.6, focus=(8.0, 47.0, 1.0))
    st.lights(s, scale=1.0, groups={"rs_door": 1.4}, near=(7.5, 45.0, 1.0), radius=4.0)
    out["frames"]["door"] = [f0 + 7, f0 + 9, f0 + 12, f0 + 29, f0 + 31, f0 + 34]
    st.finish()
    return out


PROOFS = ("sheet_a", "sheet_b", "dust", "bench", "lever", "column", "row", "door")
STRIP_RES = {"bench": (640, 360), "row": (640, 360), "door": (360, 640), "column": (360, 640),
             "lever": (360, 640)}     # tiles of the strips: landscape for the subjects that lie along a line
SHEET_RES = (960, 540)               # the two part sheets are landscape (the same pixels as a 540x960 still)


def _out_dir():
    import os

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "test")
    os.makedirs(path, exist_ok=True)
    return path


def _fresh(res=(540, 960), samples=16, motion_blur=True):
    from . import look

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=res, samples=min(samples, 16), threads=2, motion_blur=motion_blur)
    scene.cycles.adaptive_min_samples = max(4, scene.cycles.samples // 3)
    return scene


def _render(scene, film, frame, name, res=None):
    import os
    import time

    t = time.time()
    if res is not None:
        scene.render.resolution_x, scene.render.resolution_y = res
    film.goto(frame)
    path = os.path.join(_out_dir(), "redstone_%s.png" % name)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("[redstone] %-22s frame %4d -> %s  %.1f s" % (name, frame, path, time.time() - t), flush=True)
    return path


def _sheet(paths, name, cols, labels=None):
    import os

    from PIL import Image, ImageDraw

    tiles = [Image.open(p).convert("RGB") for p in paths]
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(tiles):
        x, y = (i % cols) * w, (i // cols) * h
        sheet.paste(im, (x, y))
        if labels:
            d.rectangle([x, y, x + 7 * len(labels[i]) + 6, y + 14], fill=(0, 0, 0))
            d.text((x + 3, y + 1), labels[i], fill=(255, 255, 255))
    path = os.path.join(_out_dir(), "redstone_%s.png" % name)
    sheet.save(path)
    print("[redstone] sheet %s (%dx%d)" % (path, sheet.size[0], sheet.size[1]), flush=True)
    return path


def _stills(names, samples=16):
    """Render the proof stills named (PROOFS): sheets at 540x960, strips as tiles at STRIP_RES."""
    scene = _fresh(samples=samples)
    out = build_proof(scene)
    film = out["film"]
    paths = []
    for name in names:
        fr = out["frames"][name]
        if isinstance(fr, int):
            paths.append(_render(scene, film, fr, name, res=SHEET_RES if name.startswith("sheet") else (540, 960)))
            continue
        tiles = [_render(scene, film, f, "%s_f%d" % (name, f), res=STRIP_RES[name]) for f in fr]
        labels = ["frame %d" % f for f in fr]
        w, h = STRIP_RES[name]
        paths.append(_sheet(tiles, name + "_strip", 3 if w > h else len(tiles), labels))
    return paths


# ----------------------------------------------------------------------------------------------------
# self-test (numbers; no rendering)
# ----------------------------------------------------------------------------------------------------
def arm_inside(piston, frame, samples=9):
    """True when, at every moment of whole frame `frame`'s exposure [f, f + 0.5], the head drawn on that frame
    neither pokes out of the back of the base nor leaves a gap at its inner face (and no head shows while the
    retracted model is drawn while the head is out)."""
    look = piston.look_at_frame(frame)
    for k in range(samples):
        d = piston.travel(frame + 0.5 * k / (samples - 1))
        if look == "R":
            if d > 1e-6:
                return False
            continue
        arm_end = d - (1.0 if look == "S" else 1.25)      # head plate front at d, arm 16 (short) / 20 (long) px
        if arm_end < -1.0 - 1e-6 or arm_end > -PLATFORM_PX / 16.0 + 1e-6:
            return False
    return True


def _check():
    """Numeric checks of the module; returns the number of failures."""
    from . import quick

    failed = []

    def ok(label, cond, detail=""):
        if not cond:
            failed.append(label)
        print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)

    ok("dust colours (RedstoneWireBlock COLORS, float32): power 0 (76, 0, 0), 1 (112, 0, 0), 15 (255, 50, 0)",
       WIRE_COLORS[0] == (76, 0, 0) and WIRE_COLORS[1] == (112, 0, 0) and WIRE_COLORS[15] == (255, 50, 0),
       "%s %s %s" % (WIRE_COLORS[0], WIRE_COLORS[1], WIRE_COLORS[15]))
    ok("dust colours rise with power", all(WIRE_COLORS[i][0] < WIRE_COLORS[i + 1][0] for i in range(15)))
    ok("a piston move takes 2 ticks = 2.4 frames, 0.5 block per tick", PISTON_FRAMES == 2.4 and PISTON_STEP == 0.5)
    ok("delays in frames: repeater 1..4 = 2.4 / 4.8 / 7.2 / 9.6, lamp off 4.8, torch 2.4",
       [round(at(0, REPEATER_TICKS_PER_DELAY * d), 3) for d in (1, 2, 3, 4)] == [2.4, 4.8, 7.2, 9.6]
       and round(at(0, LAMP_OFF_TICKS), 3) == 4.8 and round(at(0, TORCH_TOGGLE_TICKS), 3) == 2.4)
    ok("frame_of: a change at t is drawn from the first frame whose exposure middle is at or after t",
       [frame_of(t) for t in (10.0, 10.25, 10.26, 12.4, 14.8)] == [10, 10, 11, 13, 15])

    scene = quick.reset()
    w = _blocks.World()
    w.fill(-2, -2, -1, 40, 40, -1, "smooth_stone")
    k = kit(w)

    # ---- piston: travel, looks, the arm inside the base over every exposure, pushed blocks in contact
    worst = []
    for i, frac in enumerate((0.0, 0.3, 0.6, 0.9)):
        p = k.piston((2 * i, 0, 0), "north", sticky=True)
        b = k.block("stone", (2 * i, 1, 0))
        t0 = 10.0 + frac
        p.extend(t0)
        p.retract(t0 + 12.0)
        for f in range(8, 30):
            if not arm_inside(p, f):
                worst.append((frac, f, p.look_at_frame(f)))
        # the pushed block touches the head plate at every sampled moment (no gap, no overlap)
        trb = k.track(b.object)
        for s in range(0, 61):
            t = t0 - 1.0 + s * 0.25
            plate = p.cell[1] + 1.0 + p.travel(t)
            block_back = trb.rest[1] + trb.offset(t)[1]
            if abs(plate - block_back) > 1e-6:
                worst.append(("gap", frac, t, plate, block_back))
    ok("piston (4 start phases, extend + sticky retract): on every frame the head drawn stays inside the base "
       "over the whole exposure, and the pulled / pushed block touches the head plate at every moment",
       not worst, str(worst[:3]))
    p = k.piston((0, 10, 0), "up")
    ok("looks around an extension at t=10: frames 8-9 retracted model, 10 short head, 11+ long head",
       [p.look_at_frame(f) for f in range(8, 14)] == ["R", "R", "R", "R", "R", "R"])
    p.extend(10.0)
    ok("... after extend(10.0)", [p.look_at_frame(f) for f in range(8, 14)] == ["R", "R", "S", "L", "L", "L"],
       str([p.look_at_frame(f) for f in range(8, 14)]))
    col = [k.block("iron_block", (0, 12, z)) for z in range(1, 13)]
    p2 = k.piston((0, 12, 0), "up")
    end = p2.extend(20.0)
    zs = [round(k.track(m.object).offset(end)[2], 6) for m in col]
    ok("upward piston pushes the 12 iron blocks one block up, all on the same 2.4 frames", zs == [1.0] * 12 and
       abs(end - 22.4) < 1e-9 and abs(k.track(col[-1].object).offset(21.2)[2] - 0.5) < 1e-6, str(zs[:3]))
    col13 = [k.block("iron_block", (2, 12, z)) for z in range(1, 14)]
    p3 = k.piston((2, 12, 0), "up")
    try:
        p3.extend(20.0)
        ok("13 blocks: RedstoneError (the game's push limit is 12)", False)
    except RedstoneError as e:
        ok("13 blocks: RedstoneError (the game's push limit is 12) and nothing moved",
           not any(m.moves for m in col13) and not p3.moves, str(e)[:60])
    w.set(4, 12, 2, "stone")
    p4 = k.piston((4, 12, 0), "up")
    k.block("stone", (4, 12, 1))
    try:
        p4.extend(5.0)
        ok("a block of the set's own mesh in the way: RedstoneError", False)
    except RedstoneError:
        ok("a block of the set's own mesh in the way: RedstoneError", True)
    try:
        p.extend(30.0)
        ok("extending an extended piston: RedstoneError", False)
    except RedstoneError:
        ok("extending an extended piston: RedstoneError", True)
    # a normal piston leaves the block; a sticky one pulls it
    pn = k.piston((6, 10, 0), "east")
    bn = k.block("stone", (7, 10, 0))
    pn.extend(5.0)
    pn.retract(15.0)
    ok("a normal piston pushes and leaves its block 2 out", bn.cell_at(30.0) == (8, 10, 0))
    # the door and the row: one call each
    door = k.piston_door([(20, 5, 0), (20, 5, 1)], "east", closed=True)
    door.open(40.0)
    opened = [b.cell_at(43.0) for b in door.blocks]
    door.close(60.0)
    shut = [b.cell_at(63.0) for b in door.blocks]
    ok("piston door: open() pulls both blocks one block into the wall, close() pushes them back",
       opened == [(21, 5, 0), (21, 5, 1)] and shut == [(20, 5, 0), (20, 5, 1)], "%s %s" % (opened, shut))
    row = k.piston_row([(x, 20, 3) for x in range(20, 32)], "north", carry="oak_planks")
    row.retract(50.0)
    ok("12 sticky pistons in one call: every plank pulled from 2 out to 1 out on the same tick",
       all(b.cell_at(53.0) == (20 + i, 21, 3) for i, b in enumerate(row.blocks))
       and all(abs(k.track(b.object).offset(51.2)[1] + 0.5) < 1e-6 for b in row.blocks))
    # riders
    anvil = k.block("anvil", (20, 22, 4), {"facing": "west"})
    row.blocks[0].riders_changed()
    k.ride(anvil, row.blocks[0])
    ok("kit.ride: an anvil registered on a plank moves with it (a film choice; the game drops it)",
       abs(k.track(anvil.object).offset(53.0)[1] + 1.0) < 1e-6)

    # ---- lever
    errs = []
    for face in ("floor", "wall", "ceiling"):
        for i, f in enumerate(HORIZONTAL):
            lv = k.lever((30 + 2 * i, 30 + ("floor", "wall", "ceiling").index(face) * 2, 1), face, f)
            errs.append(lv.check_error)
    ok("lever: the handle turned by the module lands exactly on the game's other model (12 placements)",
       max(errs) < 1e-4, "max %.2e" % max(errs))
    lv = k.lever((38, 38, 0), "floor", "north")
    lv.flip(20)
    fc = _fcurve(lv.handle, "rotation_axis_angle", 0)
    vals = [round(fc.evaluate(t), 6) for t in (19.0, 19.25, 19.5, 20.0, 20.25, 20.5)]
    ok("lever flip on frame 20: frame 19's exposure all old, frame 20's all new (no in-between, no smear)",
       vals[:3] == [round(lv.off_angle, 6)] * 3 and vals[3:] == [0.0] * 3, str(vals))
    lv.set(30, False, ease=2)
    ok("lever ease=2: the handle swings over frames 28-30", abs(fc.evaluate(29.0) - lv.off_angle / 2) < 1e-6)

    # ---- dust
    sh = {}
    k2 = kit(_blocks.World())
    k2.world.fill(0, 0, -1, 20, 20, -1, "stone")
    k2.world.set(10, 2, 0, "stone")
    k2.lever((0, 0, 0), "floor", "north")
    cases = {"cross": [(5, 5, 0)], "dot": [(8, 5, 0)], "line": [(1, 8, 0), (2, 8, 0), (3, 8, 0)],
             "corner": [(1, 12, 0), (2, 12, 0), (2, 13, 0)], "t": [(6, 12, 0), (7, 12, 0), (8, 12, 0), (7, 13, 0)],
             "climb": [(9, 2, 0), (10, 2, 1)], "lever": [(1, 0, 0)]}
    for name, cells in cases.items():
        wr = k2.wire(cells, dots=cells if name == "dot" else ())
        sh[name] = [dust_shape(wr.states[c]) for c in cells]
    want = {"cross": ["cross"], "dot": ["dot"], "line": ["line", "line", "line"],
            "corner": ["line", "corner", "line"], "t": ["line", "t", "line", "line"],
            "climb": ["line+up:east", "line"], "lever": ["line"]}
    ok("dust shapes chosen as the game does (unconnected = cross, right-clicked = dot, one connection runs "
       "across, corner, T, climbing a block side, toward a lever)", sh == want, str(sh))
    lw = k2.wire([(x, 16, 0) for x in range(1, 19)], source=(0, 16, 0))
    lw.power(10, source=(0, 16, 0))
    lv16 = [lw.level_at((x, 16, 0), 10) for x in range(1, 19)]
    ok("power falls by one per block from the source: 15 .. 0, then 0", lv16 == list(range(15, -1, -1)) + [0, 0],
       str(lv16))
    lw.unpower(20)
    ok("unpower: the whole line dark on one frame", all(lw.level_at(c, 20) == 0 for c in lw.cells)
       and all(lw.level_at(c, 19) == lv16[i] for i, c in enumerate(lw.cells)))
    lw.power(30, source=(0, 16, 0), ripple=8)
    rip = [min(f for f in lw.hist[c] if f >= 30) for c in lw.cells]
    ok("ripple=8: the line lights block by block away from the source, the last block 8 frames after the first",
       rip[0] == 30 and rip[-1] == 38 and all(a <= b for a, b in zip(rip, rip[1:])), str(rip))

    # ---- sequencing
    k3 = kit(_blocks.World())
    k3.world.fill(0, 0, -1, 10, 10, -1, "stone")
    k3.world.set(6, 0, 0, "stone")
    tch = k3.torch((1, 0, 0))
    wr = k3.wire([(2, 0, 0), (3, 0, 0)], source=(1, 0, 0))
    rep = k3.repeater((4, 0, 0), "east", delay=2)
    lamp = k3.lamp((5, 0, 0))
    pis = k3.piston((5, 1, 0), "north")
    t = tch.plant(10)
    end = signal(t, wr, rep, (lamp, pis))
    ok("signal(): torch planted on frame 10 lights the dust at once, the repeater (delay 2) puts out 4 ticks later "
       "(14.8: drawn from frame 15), the lamp is lit and the piston starts on that tick",
       t == 10.0 and abs(end - 14.8) < 1e-9 and lamp.lit_at(15) and not lamp.lit_at(14)
       and wr.level_at((2, 0, 0), 10) == 15 and wr.level_at((3, 0, 0), 10) == 14
       and pis.look_at_frame(15) == "S" and pis.look_at_frame(14) == "R", "end %.2f" % end)
    off = unsignal(30, wr, rep, lamp)
    ok("unsignal(): the lamp goes out 4 ticks after the repeater (30 + 4.8 + 4.8 = 39.6 -> frame 40)",
       abs(off - 39.6) < 1e-9 and lamp.lit_at(39) and not lamp.lit_at(40))
    ok("the lamp's light is on exactly while it is lit, and its own faces do not block it",
       lamp.light.light_linking.blocker_collection is not None
       and all(co.light_linking.link_state == "EXCLUDE"
               for co in lamp.light.light_linking.blocker_collection.collection_objects))
    print("[redstone] %d failed%s" % (len(failed), ": " + "; ".join(failed) if failed else ""))
    return len(failed)


def _check_village():
    """The proof film in the real village: the hook is accepted, the parts build, the lever is in reach, the
    held torch's light follows the item."""
    failed = []

    def ok(label, cond, detail=""):
        if not cond:
            failed.append(label)
        print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)

    scene = _fresh()
    out = build_proof(scene)
    v = out["village"]
    ok("the proof set goes through the village hook with no problem and validates", not v.edit_problems
       and not v.validate(), "%s %s" % (v.edit_problems, v.validate()))
    reach, f = out["lever_reach"]
    ok("a player at lever.stand() brings his swinging right hand within 0.45 block of the handle's middle "
       "(%.2f at frame %g; the swing tops out 1.33 above his feet)" % (reach, f), reach < 0.45)
    efe = out["stage"].cast["efe"]
    item = efe.item("right")
    L = bpy.data.objects.get(item.get("redstone_glow_light", "")) if item is not None else None
    states = []
    for fr, want_shown in ((out["shots"].get("x", 0) or out["frames"]["bench"][0], True),
                           (out["frames"]["sheet_a"], False)):
        scene.frame_set(fr)
        states.append((item.hide_render, L.hide_render if L else None))
    ok("held redstone torch: its light is on in its shot and off where the player is hidden (driver)",
       L is not None and all(a == b for a, b in states) and states[0][0] is False and states[1][0] is True,
       str(states))
    print("[redstone village] %d failed" % len(failed))
    return len(failed)


def _main(argv):
    if argv and argv[0] == "stills":
        names = argv[1:] or list(PROOFS)
        bad = [n for n in names if n not in PROOFS]
        if bad:
            print("unknown still(s) %s; names: %s" % (bad, ", ".join(PROOFS)))
            return 2
        _stills(names)
        return 0
    n = _check()
    if not argv or argv[0] != "quick":
        n += _check_village()
    return 1 if n else 0


if __name__ == "__main__":
    import sys

    sys.exit(_main(sys.argv[1:]))
