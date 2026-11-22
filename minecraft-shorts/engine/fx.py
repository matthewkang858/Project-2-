"""Block breaking and placing, particles, profession change, held trade items and the enchantment glint.

Everything here is transcribed from the Java Edition 26.3 client (class names are given next to the numbers) and
drawn with the game's own textures through engine.mcassets. Nothing in the other engine files is touched: the
module works on the built Village and on engine.characters rigs from outside.

PUBLIC API (frames are film frames at 24 fps; the game runs 20 ticks per second: 1 tick = 1.2 frames)

  extract_block(village, where, name=None) -> Block
      Take one placed block out of the static village meshes and make it its own object. `where` = a cell
      (x, y, z), a point, or an anchor name ('cell_1' resolves to 'cell_1_station', the job block of hall cell 1).
      Works for any block model, full cubes too: the faces of its neighbours that the mesher culled against it
      come back as "patches" that are shown while the block is gone (under the lectern: the floor's top face).
  hall_job_block(village, n=1) -> Block     the workstation in front of trading-hall cell n (cell 1 = the lectern).
  Block.show(frame, visible=True)           keyed visibility (the patches get the opposite state).
  Block.crack(frame, stage)                 the destroy_stage_<stage> cracks from `frame` on; stage -1 = none.
  Block.stage_at(frame) / .object / .cell / .center / .top / .patches / .particle_texture / .shape / .stats

  break_block(block, frame_start, frame_end, camera=None, hit_from=None, seed=0, particles=True, glow=0.0) -> Burst
      The game's breaking: crack stages 0..9 spread evenly over [frame_start, frame_end), then ON frame_end the
      block is gone and the block-break particles fly (ClientLevel.addDestroyBlockEffect; a lectern gives 112).
      hit_from = the player (Character) or a point: also the one crumb per tick that flies off the face being hit
      while mining. camera = the Shot that films it (see emit).
  break_frames(block_id='lectern', tool='hand') -> int     how long the game takes: lectern by hand 90 frames,
                                            wooden axe 46, stone 23, copper 18, iron 16, diamond 12, netherite 11,
                                            golden 8.
  place_block(block, frame)                 the block is simply there from `frame` on, uncracked (the game has no
                                            placing animation and no particles). The player's arm swing is
                                            Character.swing_arm(frame - 2): the arm is furthest forward 2 frames in.
                                            Character.swing_arm is ADDITIVE: two of them less than 8 frames apart
                                            (or one inside a mining span) leave the arm displaced for good. For
                                            swings in quick succession use arm_swings(steve, [frame - 2]).
  mining_swings(player, frame_start, frame_end, every=None) -> [frames]
      The arm while mining, as the game plays it: a swing request every tick, so the swing restarts every 4 ticks
      = 4.8 frames; the last swing is finished after the block broke (at rest at most 9 frames after frame_end,
      exactly in the pose of frame_start). Call it after place() / look_at(). Returns the frames swings start on.
  arm_swings(player, frames) -> [frames]
      One swing request per frame listed (place, use, hit), by the game's rule: a request during the first half
      of a running swing is ignored, a later one restarts the swing. Absolute keys: any number of calls and any
      spacing come back to the rest pose. The arm starts to move 1.2 frames after a request, highest after 2.4.

  emit(kind, pos, frame, camera=None, count=None, seed=0, village=None, glow=None, size=(0.6, 1.95),
       in_air=False) -> Burst
      A burst of the game's particles. pos = a Character (its feet at that frame) or the feet point of the entity.
      kinds: 'happy_villager' (entity event 14: green glints), 'angry_villager' (event 13), 'heart' (event 12),
      'splash' (event 42). 5 particles around the entity, exactly as AbstractVillager.addParticlesAroundSelf.
      camera = the Shot that films it (or the Film; both mean "whichever shot of that film is on"): particles are
      camera-facing quads, as in the game, and after a cut they face the next shot's camera, also when that shot
      is created later. A bare camera object is followed as it is. seed picks where they start. in_air=True (with
      village=) keeps them out of solid blocks; glow = self-light (default 0.6 for these sprites, 0 for crumbs).
  Burst.objects / .particles / .frame / .frame_end      what was made; frame_end = last frame anything is visible.
  Burst.stop(frame)                         nothing of that burst is visible from `frame` on (returns how many ended).
  stop_particles(frame)                     the same for every burst made so far: call it for the first frame of a
                                            shot that jumps in time, or old crumbs and sprites still hang there.
  bind_cameras(film)                        re-bind the particles to the film's shot cameras. Automatic (on every
                                            emit / break_block and inside film.finalize()); only needed by hand
                                            when shots are added or re-timed AFTER finalize().

  make_job_villager(name, professions=('librarian', 'none'), level=1, ...) -> JobVillager
      A villager that can change profession: ONE rig (a characters.Character: place, walk, look_at, idle, nod,
      head, show ... all work) wearing several outfits, of which one is visible. Put it in the Stage's cast
      yourself: st.cast[name] = fx.make_job_villager(name).
  JobVillager.set_profession(frame, 'none')            cut to another outfit on that frame.
  JobVillager.gain_profession(frame, 'librarian', camera, seed=0, **emit_kw) -> Burst
                                                       outfit + the 5 green particles on the same frame (event 14).
  JobVillager.lose_profession(frame)                   back to the unemployed outfit; the game shows NO particles.
  JobVillager.profession_at(frame) / .outfits / .professions / .heads (the head object of every outfit)

  hold_out(villager, item, frame_start, frame_end=None, enchanted=False) -> Object
      A villager shows a trade item where CrossedArmsItemLayer draws it; visible on [frame_start, frame_end).
      item = 'enchanted_book' / 'emerald' ... or an object from props.make_item. enchanted=True adds glint().
      (Character.hold was checked against the layer class: it puts the item in exactly the same place. hold_out
      only adds the timing, and keeps the item out of Character.show so a shot cut cannot switch it on early.)
  glint(item_obj, frame_start=1, frame_end=None, strength=1.0, light=0.75, phase=0.0) -> Material
      The enchantment glint (misc/enchanted_glint_item.png, scrolling as TextureTransform.GLINT_TEXTURING does)
      as an animated emissive layer on a flat item.
  held_item_point(character, frame=None) -> Vector     world centre of an item held on the crossed arms.
  crossed_arms_matrix() / block_shape(block_id, props)  the transcribed layer matrix / the game's outline boxes.
  build_proof(scene) -> dict                           the worked example below as a whole 4-shot film (self-test).

WORKED EXAMPLE (build_proof films exactly this in the real trading hall; st = films.lookdev.Stage)

    lec = fx.hall_job_block(v, 1)                                    # once, after village.build_village(...)
    lib = st.cast["lib"] = fx.make_job_villager("lib", ("librarian", "none"))
    lib.place(f0, v.anchors["cell_1"], v.yaws["cell_1"]); lib.idle(f0, f1 + 1)
    s.move(...)                                                      # s = st.shot("cell", 6.0)
    steve.place(f0, stand, yaw); steve.look_at(f0, lec.center, ease=0)   # BEFORE the swings: they read his pose
    fx.mining_swings(steve, 24, 48)                                  # if Steve is in the picture
    fx.break_block(lec, 24, 48, camera=s, hit_from=steve)            # cracks 24..47, gone + 112 particles on 48
    lib.lose_profession(54)                                          # a few ticks later: plain villager, no particles
    fx.arm_swings(steve, [94]); fx.place_block(lec, 96)
    lib.gain_profession(108, "librarian", camera=s, seed=9)          # green glints + librarian again
    book = fx.hold_out(lib, "enchanted_book", h0, h1 + 1, enchanted=True)   # in the close shot of the book
    fx.stop_particles(t0)                                            # first frame of a shot that jumps in time

WHAT THE GAME DOES (read from the classes; _GAME_NOTES at the end of the file has all the numbers)
  - break a villager's job block: block-break particles only. ai.behavior.ResetProfession then sets the profession to
    NONE without any entity event, so NO particles; and only for a villager with level 1 (stone badge) and 0 xp.
  - place it again: ai.behavior.AssignProfessionFromJobSite broadcasts entity event 14 on the tick the villager
    takes the job: 5 'happy_villager' particles around the VILLAGER (not the block), outfit changes the same tick.
  - event 14 also after a trade and when he claims a bed or the bell; event 13 ('angry_villager') when a player
    hits him, and on both villagers when a breeding attempt finds no free bed they can reach (VillagerMakeLove
    .tryToGiveBirth); 42 ('splash') during a raid; 12 ('heart') while breeding. 'poof' is never used for a
    profession change (not implemented).
  - mining: Minecraft.continueAttack asks for a swing on every tick; LivingEntity$SwingState starts one when none
    runs or the running one (6 ticks) is more than half done: up in one tick, down over two, back in the fourth,
    every 4 ticks. Placing a block asks for one swing on the tick the block appears.

MEASURED (trading hall, cell 1: lectern cell (-6, -31, 0), villager anchor cell_1 = (-5.5, -31.3, 0) facing north)
  - the lectern's slanted top rises ABOVE its unit cube: Block.top = 1.153; its high edge is on the villager's side.
  - break particles: quads 0.10-0.20 block wide showing a quarter of block/lectern_sides at 0.6 of its display
    brightness (clearly darker than the lectern), 112 of them; half are gone after about 10 frames, the last
    after at most 50; they land on the floor and on the pier beside the cell.
  - the mining arm: 65-85 degrees forward at the top of each swing (less the further down he looks), a full cycle
    in 4.8 frames, so with the 0.5-frame shutter the arm is a blur on most frames; the body twists +-0.2 rad.
  - happy_villager: 5 sprites 0.10-0.44 wide, x and y within +-0.6 of the villager, 1.0-2.95 above his feet, each
    lasting 25-121 frames, almost motionless. In a 1x1 cell about half start inside the walls: choose a seed
    (9 shows four in cell 1) or pass village=v, in_air=True (and count=8 for more than the game shows).
  - angry_villager / heart: 0.3-0.6 wide, start 1.5-3.45 (heart 1.0-2.95) above the feet, rise 0.65, last 20 frames.
  - a held item: centre 1.225 above the feet and 0.40 in front of the villager, 0.50 wide, upright, facing the
    customer. At the anchor cell_1 the book stands 3 cm behind the lectern's high edge (1.153): from the aisle its
    lower third is hidden. Place him 0.22 further back (the middle of his cell, where the game keeps him) and a
    camera at 1.8-1.95 sees all of it but the bottom row of texels.
  - cameras that worked (offsets from the cell_1 anchor): cell, lectern and floor: 35 mm f/3.4 from
    (+0.78, +3.62, 1.56) aimed at (+0.03, +0.50, 0.97); the book: 45 mm f/3.4 from (+0.45, +3.03, 1.95) aimed at
    (0, +0.18, 1.12) with him 0.22 back: the book lands at y 37-53 % of the frame, his face at 11-39 %, the
    lectern fills the bottom third under the caption (from 2 blocks away the book sat IN the caption band);
    Steve mining, seen past his right shoulder: 24 mm f/3.4 from (+0.05, +3.95, 1.60) aimed at (+0.45, +0.80,
    1.10), Steve standing at (+0.72, +2.25) facing the lectern, the librarian looking at the lens. Lights as
    lookdev.shot_hall: st.lights(s, scale=0.0, groups={"hall": 0.8}, inside="hall"); tools.palette_check then
    measures lit stone at G/R 0.92-0.94, right on its 0.92 limit.
  - cell 1 has ONE key: the lantern on the pier at the villager's east (-4.5, -30.5, 2.3). His west cheek is nearly
    black. A camera in the north-west corner of the aisle (-0.70, +3.88), or a head turned east of the lens (he
    looks at a Steve standing east of the camera; an idle turn of 25 degrees), shows that cheek and fails
    palette_check's face saturation (0.55-0.62 against 0.52). Keep the lens north or north-east of him and let
    him look at it.

CONVENTIONS / GOTCHAS
  - Blender +X east, +Y north, +Z up, 1 block = 1 unit. Visibility, outfit and crack changes are CONSTANT keys on
    integer frames (safe with the 0.5-frame shutter that opens on the frame).
  - Particles appear ON `frame`, stand still for the first tick (the game draws a new particle at its spawn point
    until its first tick: on the break frame the crumbs still fill the block's shape), then move piecewise-linearly
    through the game's tick positions (LINEAR keys every 1.2 frames), so motion blur follows the true path.
    They collide with full cubes, slabs and lecterns of the village; other shapes (bars, fences, stairs) do not
    stop them.
  - Particle quads copy the rotation of the camera (SingleQuadParticle.LOOKAT_XYZ) through one empty per film
    (camera_proxy) that follows the camera of the shot that is on; it is re-bound whenever shots are added, last
    inside film.finalize(). They are shaded like an up-facing surface whatever their direction (the game lights a
    particle with the light level only). Crumbs take the set's light; sprites get glow 0.6 by default (use about
    0.2 in a dark exterior).
  - Bursts are world objects with their own lifetimes (green sprites up to 121 frames, crumbs up to 50): a cut to
    another angle keeps them, correctly turned; a cut that jumps in TIME needs stop_particles(first frame).
  - arm_swings / mining_swings write absolute keys on the player's arm_r, arm_l (x), body (z) and head (z) for
    the span of the swings; key place() and look_at() before them and nothing on those channels inside the span.
    Do not mix them with Character.swing_arm inside 9 frames.
  - Each call sets the state "from that frame on": call break_block / place_block / show / set_profession in
    increasing frame order per block / villager. extract_block edits the village meshes: call it once per block.
  - JobVillager owns the visibility of its parts: use its show() (Stage.finish does); never key hide_render on them.
    For the composition check name him with st.hero(shot, "librarian", *lib.heads): st.hero(shot, ..., lib) means
    the first outfit's head only and reports "not in the picture" while he wears another outfit.
    make_job_villager(level=1) is the stone badge, the only level at which the game lets a villager lose his job.
  - Not covered: 'poof' and other particle kinds; collision with non-cube shapes; fluids and props (doors, bell)
    cannot be extracted; the glint is for flat item sprites (props.make_item), not for block models or armour.
"""
import math

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import blocks as _blocks
from . import characters
from . import mcassets as mc
from . import props

FPS = 24
TICK = FPS / 20.0                    # frames per game tick
COLLECTION = "fx"
CRACK_UV = "fx_crack"
VILLAGER_SIZE = (0.6, 1.95)          # EntityTypes.VILLAGER: sized(0.6F, 1.95F), the bounding box (width, height)


# ----------------------------------------------------------------------------------------------------
# keyframe plumbing
# ----------------------------------------------------------------------------------------------------
def _collection(collection=None):
    """The collection fx objects live in (created and linked to the scene on first use)."""
    if collection is not None:
        return collection
    col = bpy.data.collections.get(COLLECTION)
    if col is None:
        col = bpy.data.collections.new(COLLECTION)
    scene = bpy.context.scene
    if col.name not in scene.collection.children:
        scene.collection.children.link(col)
    return col


def _fcurve(idb, path, index=0):
    """F-curve idb.<path>[index], creating action, slot and curve as needed (Blender 5 layered actions)."""
    ad = idb.animation_data or idb.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(idb.name + "_fx")
    return ad.action.fcurve_ensure_for_datablock(idb, path, index=index)


def _write(idb, path, index, frames, values, interp="LINEAR"):
    """Replace a channel by the given keys (all with one interpolation mode)."""
    fc = _fcurve(idb, path, index)
    kps = fc.keyframe_points
    while len(kps):
        kps.remove(kps[len(kps) - 1], fast=True)
    n = len(frames)
    kps.add(n)
    co = np.empty(2 * n, dtype=np.float32)
    co[0::2] = frames
    co[1::2] = values
    kps.foreach_set("co", co)
    for kp in kps:
        kp.interpolation = interp
    fc.update()
    return fc


def _step(idb, path, frame, value, index=0, before=None):
    """One CONSTANT key: the channel has `value` from `frame` on. On the first key of a channel the state it had
    until now (`before`, default: the property's current value) is pinned one frame earlier."""
    fc = _fcurve(idb, path, index)
    kps = fc.keyframe_points
    if not len(kps):
        if before is None:
            cur = idb.path_resolve(path)
            before = float(cur[index]) if hasattr(cur, "__len__") else float(cur)
        if abs(float(before) - float(value)) > 1e-9:
            kp = kps.insert(float(frame) - 1.0, float(before))
            kp.interpolation = "CONSTANT"
    kp = kps.insert(float(frame), float(value))
    kp.interpolation = "CONSTANT"
    fc.update()
    return fc


def _show(ob, frame, visible, before=None):
    """Keyed render + viewport visibility of one object from `frame` on."""
    for path in ("hide_render", "hide_viewport"):
        _step(ob, path, frame, 0.0 if visible else 1.0,
              before=None if before is None else (0.0 if before else 1.0))


def _socket_step(node_tree, socket, frame, value):
    """CONSTANT key on a node socket's default_value (the node tree becomes 'dynamic' for engine.stamp)."""
    from .shots import fcurves_of

    path = socket.path_from_id("default_value")
    if not any(fc.data_path == path for fc in fcurves_of(node_tree)):
        before = socket.default_value                     # first key: pin the state it had until now
        if abs(float(before) - float(value)) > 1e-9:
            socket.keyframe_insert("default_value", frame=frame - 1)
    socket.default_value = value
    socket.keyframe_insert("default_value", frame=frame)
    for fc in fcurves_of(node_tree):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
            fc.update()


def _point(target, frame):
    """World point of a Character (feet), an Object or a plain (x, y, z) at `frame`."""
    if isinstance(target, characters.Character):
        return Vector(target.pos_at(frame))
    if isinstance(target, bpy.types.Object):
        return Vector(target.matrix_world.translation)
    t = tuple(target)
    return Vector((float(t[0]), float(t[1]), float(t[2]) if len(t) > 2 else 0.0))


# ----------------------------------------------------------------------------------------------------
# block shapes (the OUTLINE shape decides how many break particles a block gives and where they start)
# ----------------------------------------------------------------------------------------------------
def _merge_boxes(boxes):
    """VoxelShape.forAllBoxes of the union of `boxes`: the game's own merge of a voxel shape into boxes
    (BitSetDiscreteVoxelShape.forAllBoxes with mergeNeighbors: y outer, x, z inner; grow z run, then x, then y)."""
    xs = sorted({round(v, 6) for b in boxes for v in (b[0], b[3])})
    ys = sorted({round(v, 6) for b in boxes for v in (b[1], b[4])})
    zs = sorted({round(v, 6) for b in boxes for v in (b[2], b[5])})
    nx, ny, nz = len(xs) - 1, len(ys) - 1, len(zs) - 1
    full = np.zeros((nx, ny, nz), dtype=bool)
    for b in boxes:
        ix = [i for i in range(nx) if b[0] - 1e-6 <= xs[i] and xs[i + 1] <= b[3] + 1e-6]
        iy = [i for i in range(ny) if b[1] - 1e-6 <= ys[i] and ys[i + 1] <= b[4] + 1e-6]
        iz = [i for i in range(nz) if b[2] - 1e-6 <= zs[i] and zs[i + 1] <= b[5] + 1e-6]
        if ix and iy and iz:
            full[ix[0]:ix[-1] + 1, iy[0]:iy[-1] + 1, iz[0]:iz[-1] + 1] = True
    out = []
    for y in range(ny):
        for x in range(nx):
            z0 = -1
            for z in range(nz + 1):
                if z < nz and full[x, y, z]:
                    if z0 == -1:
                        z0 = z
                elif z0 != -1:
                    x1, y1 = x, y
                    full[x, y, z0:z] = False
                    while x1 + 1 < nx and full[x1 + 1, y, z0:z].all():
                        full[x1 + 1, y, z0:z] = False
                        x1 += 1
                    while y1 + 1 < ny and full[x:x1 + 1, y1 + 1, z0:z].all():
                        full[x:x1 + 1, y1 + 1, z0:z] = False
                        y1 += 1
                    out.append((xs[x], ys[y], zs[z0], xs[x1 + 1], ys[y1 + 1], zs[z]))
                    z0 = -1
    return out


def _or(*shapes):
    """Shapes.or(a, b, ...): reduce with join + optimize (each step re-merged into boxes)."""
    acc = list(shapes[0])
    for s in shapes[1:]:
        acc = _merge_boxes(acc + list(s))
    return acc


def _rotate_y(boxes, y):
    """Boxes after a blockstate y rotation (model pixels, Minecraft axes)."""
    if not y:
        return list(boxes)
    out = []
    for b in boxes:
        p, q = mc.rotate_point(b[:3], 0, y), mc.rotate_point(b[3:], 0, y)
        out.append(tuple(min(a, c) for a, c in zip(p, q)) + tuple(max(a, c) for a, c in zip(p, q)))
    return out


_FULL = [(0.0, 0.0, 0.0, 16.0, 16.0, 16.0)]
# LecternBlock: SHAPE_COLLISION = or(column(16, 0, 2), column(8, 2, 14)); SHAPE (facing north) = or(boxZ(16, 10, 14,
# 1, 5.333333), boxZ(16, 12, 16, 5.333333, 9.666667), boxZ(16, 14, 18, 9.666667, 14), SHAPE_COLLISION)
_LECTERN_COLLISION = [(0.0, 0.0, 0.0, 16.0, 2.0, 16.0), (4.0, 2.0, 4.0, 12.0, 14.0, 12.0)]
_LECTERN_TOP = [(0.0, 10.0, 1.0, 16.0, 14.0, 5.333333), (0.0, 12.0, 5.333333, 16.0, 16.0, 9.666667),
                (0.0, 14.0, 9.666667, 16.0, 18.0, 14.0)]
_FACING_Y = {"north": 0, "east": 90, "south": 180, "west": 270}


def block_shape(block_id, props=None):
    """The game's outline shape of a block state as merged boxes (x0, y0, z0, x1, y1, z1) in model pixels, Minecraft
    axes: lectern (exact, any facing), slabs, stonecutter; every other block is treated as a full cube."""
    props = props or {}
    if block_id == "lectern":
        col = _or(_LECTERN_COLLISION[:1], _LECTERN_COLLISION[1:])
        shape = _or(_LECTERN_TOP[0:1], _LECTERN_TOP[1:2], _LECTERN_TOP[2:3], col)
        return _merge_boxes(_rotate_y(shape, _FACING_Y.get(props.get("facing", "north"), 0)))
    if block_id.endswith("_slab"):
        t = props.get("type", "bottom")
        return [(0.0, 8.0, 0.0, 16.0, 16.0, 16.0)] if t == "top" else (
            list(_FULL) if t == "double" else [(0.0, 0.0, 0.0, 16.0, 8.0, 16.0)])
    if block_id == "stonecutter":
        return [(0.0, 0.0, 0.0, 16.0, 9.0, 16.0)]
    return list(_FULL)


def _collision_shape(block_id, props):
    """Boxes a particle collides with (model pixels, Minecraft axes) for the block kinds this module knows."""
    if block_id == "lectern":
        return list(_LECTERN_COLLISION)
    return block_shape(block_id, props)


def _to_blender_box(b):
    """Model-pixel box (Minecraft axes) -> Blender block-local box (x0, y0, z0, x1, y1, z1) in block units."""
    return (b[0] / 16.0, 1.0 - b[5] / 16.0, b[1] / 16.0, b[3] / 16.0, 1.0 - b[2] / 16.0, b[4] / 16.0)


# ----------------------------------------------------------------------------------------------------
# 1. a block that can be taken out of the set
# ----------------------------------------------------------------------------------------------------
def _resolve_cell(village, where):
    if isinstance(where, str):
        name = where + "_station" if where + "_station" in village.anchors else where
        if name not in village.anchors:
            raise KeyError("fx.extract_block: no anchor %r in the village" % where)
        where = village.anchors[name]
    p = tuple(where)
    if len(p) != 3:
        raise ValueError("fx.extract_block: a cell is (x, y, z)")
    return tuple(int(math.floor(float(c) + 1e-6)) for c in p)


def _random_offset(block_id, cell):
    """The per-column offset blocks.World.build gives plants (same hash), else zero."""
    table = getattr(_blocks, "_RANDOM_OFFSET", {})
    if block_id not in table:
        return (0.0, 0.0, 0.0)
    h = _blocks.pos_hash(cell[0], cell[1], 0, 7)
    ox = ((h & 15) / 15.0 - 0.5) * 0.5
    oy = (((h >> 8) & 15) / 15.0 - 0.5) * 0.5
    oz = (((h >> 4) & 15) / 15.0 - 1.0) * 0.2 if table[block_id] else 0.0
    return (ox, oy, oz)


def _quad_key(pts):
    return tuple(sorted((int(round(p[0] * 4096.0)), int(round(p[1] * 4096.0)), int(round(p[2] * 4096.0)))
                        for p in pts))


class _MeshPool:
    """The static meshes of a village by material, with a polygon lookup near one cell."""

    def __init__(self, village, cell, reach=2.6):
        self.by_mat = {}
        objs = list(village.objects)
        for group in village.cutaways.values():
            objs.extend(group)
        for ob in objs:
            if ob.type != "MESH" or not ob.data.materials:
                continue
            self.by_mat.setdefault(ob.data.materials[0].name, []).append(ob)
        self.centre = np.array([cell[0] + 0.5, cell[1] + 0.5, cell[2] + 0.5], dtype=np.float32)
        self.reach = reach
        self._index = {}
        self.doomed = {}

    def _lookup(self, ob):
        table = self._index.get(ob.name)
        if table is None:
            me = ob.data
            n = len(me.polygons)
            centres = np.empty(n * 3, dtype=np.float32)
            me.polygons.foreach_get("center", centres)
            centres = centres.reshape(n, 3)
            if tuple(ob.location) != (0.0, 0.0, 0.0):
                centres = centres + np.array(ob.location, dtype=np.float32)
            near = np.nonzero(np.abs(centres - self.centre).max(axis=1) <= self.reach)[0]
            table = {}
            loc = Vector(ob.location)
            for i in near:
                poly = me.polygons[int(i)]
                table[_quad_key([me.vertices[v].co + loc for v in poly.vertices])] = int(i)
            self._index[ob.name] = table
        return table

    def find(self, material, pts):
        """(object, polygon index) of the static face with these corners, or None."""
        key = _quad_key(pts)
        for ob in self.by_mat.get(material.name, ()):
            i = self._lookup(ob).get(key)
            if i is not None and i not in self.doomed.get(ob.name, ()):
                return ob, i
        return None

    def take(self, hit):
        """Mark a found face for removal (and hide it from later finds)."""
        self.doomed.setdefault(hit[0].name, set()).add(hit[1])

    def commit(self):
        """Delete the taken polygons from their meshes. Returns {object name: faces removed}."""
        import bmesh

        done = {}
        for name, idx in self.doomed.items():
            me = bpy.data.objects[name].data
            bm = bmesh.new()
            bm.from_mesh(me)
            bm.faces.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[bm.faces[i] for i in sorted(idx)], context="FACES")
            bm.to_mesh(me)
            bm.free()
            me.update()
            done[name] = len(idx)
        return done


def _decal_uv(direction, p):
    """SheetedDecalTextureGenerator: the crack texture coordinate (u, v down) of a block-local point p (Minecraft
    axes, 0..1) on a face whose nearest axis is `direction` (position rotated Y 180, X -90, then Direction
    .getRotation(); u = -x', v = -y'; texture scale 1, wrap = repeat)."""
    x, y, z = p
    if direction == "up":
        return (x, z)
    if direction == "down":
        return (x, 1.0 - z)
    if direction == "north":
        return (1.0 - x, 1.0 - y)
    if direction == "south":
        return (x, 1.0 - y)
    if direction == "west":
        return (1.0 - z, 1.0 - y)
    return (z, 1.0 - y)


def _nearest_dir(n):
    """Direction.getApproximateNearest of a normal given in Minecraft axes."""
    best, name = -1e9, "up"
    for d in ("down", "up", "north", "south", "west", "east"):
        v = mc.DIR_VEC[d]
        dot = n[0] * v[0] + n[1] * v[1] + n[2] * v[2]
        if dot > best + 1e-6:
            best, name = dot, d
    return name


def _crack_atlas():
    """The ten destroy_stage textures as one strip of MULTIPLIERS (slot 0 = no crack). The game draws the crack
    over the block with blend (DST_COLOR, SRC_COLOR) = 2 x crack x block in display space, texels below alpha 0.1
    discarded (RenderPipelines.CRUMBLING, core/rendertype_crumbling.fsh); in scene-linear that is x (2c)^2.2."""
    name = "fx/crack_atlas"
    img = bpy.data.images.get(name)
    if img is not None:
        return img
    arr = np.ones((16, 16 * 11, 4), dtype=np.float32)
    for s in range(10):
        a = np.asarray(mc.texture_array("block/destroy_stage_%d" % s), dtype=np.float32) / 255.0
        if a.shape[:2] != (16, 16):
            raise ValueError("fx: destroy_stage_%d is not 16x16" % s)
        tile = np.ones((16, 16, 4), dtype=np.float32)
        m = a[..., 3] >= 0.1
        tile[m, :3] = np.power(2.0 * a[..., :3][m], 2.2)
        arr[:, 16 * (s + 1):16 * (s + 2)] = tile
    img = bpy.data.images.new(name, 16 * 11, 16, alpha=True, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    img.alpha_mode = "STRAIGHT"
    img.pixels.foreach_set(np.flipud(arr).ravel())
    img.pack()
    return img


def _crack_material(base, tag):
    """Copy of a block material whose texture colour is multiplied by the crack of the keyed stage (Value node
    'fx_stage': -1 none, 0..9), looked up through the mesh's second UV layer (the game's decal projection)."""
    mat = base.copy()
    mat.name = "fx/%s/%s" % (tag, base.name)
    nt = mat.node_tree
    N, L = nt.nodes.new, nt.links.new
    own = [n for n in nt.nodes if n.type == "TEX_IMAGE"]
    uv = N("ShaderNodeUVMap")
    uv.uv_map = CRACK_UV
    sep = N("ShaderNodeSeparateXYZ")
    L(uv.outputs[0], sep.inputs[0])
    stage = N("ShaderNodeValue")
    stage.name = "fx_stage"
    stage.outputs[0].default_value = -1.0

    def wrap(sock):
        """fract(u): the crack texture repeats, like the game's."""
        m = N("ShaderNodeMath")
        m.operation = "MULTIPLY_ADD"                 # keep Closest sampling off the texel borders
        m.inputs[1].default_value = 0.9996
        m.inputs[2].default_value = 0.0002
        L(sock, m.inputs[0])
        f = N("ShaderNodeMath")
        f.operation = "FRACT"
        L(m.outputs[0], f.inputs[0])
        return f.outputs[0]

    add = N("ShaderNodeMath")
    add.operation = "ADD"
    L(wrap(sep.outputs[0]), add.inputs[0])
    slot = N("ShaderNodeMath")
    slot.operation = "ADD"
    slot.inputs[1].default_value = 1.0
    L(stage.outputs[0], slot.inputs[0])
    L(slot.outputs[0], add.inputs[1])
    div = N("ShaderNodeMath")
    div.operation = "DIVIDE"
    div.inputs[1].default_value = 11.0
    L(add.outputs[0], div.inputs[0])
    comb = N("ShaderNodeCombineXYZ")
    L(div.outputs[0], comb.inputs[0])
    L(wrap(sep.outputs[1]), comb.inputs[1])
    tex = N("ShaderNodeTexImage")
    tex.name = "fx_crack"
    tex.image = _crack_atlas()
    tex.interpolation = "Closest"
    tex.extension = "EXTEND"
    L(comb.outputs[0], tex.inputs[0])
    pairs = [(ln.from_socket, ln.to_socket) for ln in nt.links
             if ln.from_node in own and ln.from_socket.name == "Color"]
    for src, to in pairs:
        mul = N("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs[0].default_value = 1.0
        L(src, mul.inputs[6])
        L(tex.outputs["Color"], mul.inputs[7])
        L(mul.outputs[2], to)
    mat["fx_crack"] = 1
    return mat


class Block:
    """One block taken out of the static village meshes (extract_block).

    object            the mesh object (origin = the cell's min corner; all of the block's faces that were drawn)
    cell              (x, y, z) Blender grid cell;  block_id, props: its state
    center            centre of the cell;  top: highest point of the model (the lectern rises to z + 1.153)
    patches           objects holding the neighbours' faces that the block hid (shown only while it is gone)
    particle_texture  (texture path, tint) of the model's 'particle' texture: what its break particles show
    shape             the game's outline boxes, Blender block-local units (x0, y0, z0, x1, y1, z1)
    """

    def __init__(self, village, cell, block_id, props, ob, patches, materials, stats):
        self.village, self.cell, self.block_id, self.props = village, cell, block_id, dict(props)
        self.object, self.patches, self.materials, self.stats = ob, patches, materials, stats
        self.name = ob.name
        self.center = Vector((cell[0] + 0.5, cell[1] + 0.5, cell[2] + 0.5))
        self.top = cell[2] + max(v.co.z for v in ob.data.vertices)
        self.shape = [_to_blender_box(b) for b in block_shape(block_id, props)]
        self.collision = [_to_blender_box(b) for b in _collision_shape(block_id, props)]
        tex = None
        try:
            parts = mc.resolve_blockstate(block_id, props)
            tex = mc.load_model(parts[0].model).textures.get("particle")
        except Exception:                                   # noqa: BLE001 - odd models: fall back to a face texture
            tex = None
        if not tex or tex.startswith("#"):
            tex = materials[0][0]
        self.particle_texture = (mc._norm(tex), mc.block_tint(block_id, 0))
        self._visible = True

    def __repr__(self):
        return "<fx.Block %s at %s>" % (self.block_id, (self.cell,))

    def show(self, frame, visible=True):
        """The block is there (or gone) from `frame` on; the neighbour patches get the opposite state."""
        _show(self.object, frame, visible)
        for p in self.patches:
            _show(p, frame, not visible)
        self._visible = bool(visible)

    def crack(self, frame, stage):
        """Show crack stage 0..9 (destroy_stage_N.png over every face) from `frame` on; -1 removes the cracks."""
        stage = int(max(-1, min(9, stage)))
        for _tex, mat in self.materials:
            nt = mat.node_tree
            _socket_step(nt, nt.nodes["fx_stage"].outputs[0], frame, float(stage))

    def stage_at(self, frame):
        """The keyed crack stage at `frame` (-1 = none)."""
        from .shots import fcurves_of

        nt = self.materials[0][1].node_tree
        for fc in fcurves_of(nt):
            if "fx_stage" in fc.data_path:
                return int(round(fc.evaluate(frame)))
        return int(round(nt.nodes["fx_stage"].outputs[0].default_value))


def _mesh_from_quads(name, quads, materials):
    """Mesh from [(material index, 4 points, 4 uvs in 0..16 v-down, shade up?, crack uvs or None)]."""
    me = bpy.data.meshes.new(name)
    n = len(quads)
    me.vertices.add(n * 4)
    me.loops.add(n * 4)
    me.polygons.add(n)
    co = np.array([p for q in quads for p in q[1]], dtype=np.float32)
    me.vertices.foreach_set("co", co.ravel())
    me.loops.foreach_set("vertex_index", np.arange(n * 4, dtype=np.int32))
    me.polygons.foreach_set("loop_start", np.arange(0, n * 4, 4, dtype=np.int32))
    me.polygons.foreach_set("loop_total", np.full(n, 4, dtype=np.int32))
    uv = np.array([(u / 16.0, 1.0 - v / 16.0) for q in quads for (u, v) in q[2]], dtype=np.float32)
    me.uv_layers.new(name="UVMap").data.foreach_set("uv", uv.ravel())
    if any(q[4] is not None for q in quads):
        cuv = np.array([(u, 1.0 - v) for q in quads for (u, v) in (q[4] or [(0.0, 0.0)] * 4)], dtype=np.float32)
        me.uv_layers.new(name=CRACK_UV).data.foreach_set("uv", cuv.ravel())
    for m in materials:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", np.array([q[0] for q in quads], dtype=np.int32))
    me.update()
    me.validate()
    ups = [bool(q[3]) for q in quads]
    if any(ups) and len(me.polygons) == n:
        normals = np.zeros((n, 3), dtype=np.float32)
        me.polygons.foreach_get("normal", normals.ravel())
        normals[np.array(ups)] = (0.0, 0.0, 1.0)
        me.polygons.foreach_set("use_smooth", ups)
        me.normals_split_custom_set(np.repeat(normals, 4, axis=0).tolist())
        me.update()
    return me


def extract_block(village, where, name=None):
    """Turn one placed block of the built village into its own object (see the module docstring); returns a Block.

    Works for non-full blocks (lectern, composter, ...) and for full cubes alike: the faces of the six neighbours
    that the mesher culled against this block are rebuilt as patch objects and shown whenever the block is hidden.
    Raises ValueError for air, fluids, and blocks that are already props (doors, the bell)."""
    w = village.world
    cell = _resolve_cell(village, where)
    registry = village.__dict__.setdefault("_fx_blocks", {})
    if cell in registry:
        return registry[cell]
    st = w.get(*cell)
    if st is None:
        raise ValueError("fx.extract_block: no block at %s" % (cell,))
    block_id, props = st
    if block_id in ("water", "lava"):
        raise ValueError("fx.extract_block: %s at %s is a fluid, not a block model" % (block_id, cell))
    state = w._state_at(cell)
    off = _random_offset(block_id, cell)
    pool = _MeshPool(village, cell)
    mats, mat_index, quads = [], {}, []
    expected = 0
    for pts, uvs, key, _cull, _off, _mask in state.quads:
        expected += 1
        base = _blocks.block_material(*key)
        world = [(p[0] + cell[0] + off[0], p[1] + cell[1] + off[1], p[2] + cell[2] + off[2]) for p in pts]
        hit = pool.find(base, world)
        if hit is None:
            continue                                         # culled by a neighbour: stays hidden behind it
        pool.take(hit)
        if base.name not in mat_index:
            mat_index[base.name] = len(mats)
            mats.append((key[0], base))
        local = [(p[0] + off[0], p[1] + off[1], p[2] + off[2]) for p in pts]
        a, b, c = Vector(local[0]), Vector(local[1]), Vector(local[2])
        nb = (b - a).cross(c - a)
        direction = _nearest_dir((nb.x, nb.z, -nb.y))        # Blender normal -> Minecraft axes
        cuv = [_decal_uv(direction, (p[0], p[2], 1.0 - p[1])) for p in local]
        quads.append((mat_index[base.name], local, uvs, key[4] is not None, cuv))
    if not quads:
        raise ValueError("fx.extract_block: %s at %s has no faces in the village meshes (it is built as a separate "
                         "prop, or was extracted before)" % (block_id, cell))
    # the neighbours' faces that were culled against this block
    patch_quads, patch_mats, patch_index = [], [], {}
    for d in mc.DIRS:
        o = mc.DIR_BLENDER[d]
        npos = (cell[0] + o[0], cell[1] + o[1], cell[2] + o[2])
        if npos not in w.blocks or npos in registry:
            continue
        nid = w.block_id(*npos)
        if nid in ("water", "lava"):
            continue
        if npos in w.passable or nid == "bell" or nid.endswith("_door"):
            continue                                         # doors and the bell are props, not static faces
        nst = w._state_at(npos)
        noff = _random_offset(nid, npos)
        back = mc.OPPOSITE[d]
        missing = []
        for pts, uvs, key, cull, _off, _mask in nst.quads:
            if cull != back:
                continue
            if cull == "down" and w.cull_below is not None and npos[2] <= w.cull_below:
                continue
            if w.hidden_sides and (npos, cull) in w.hidden_sides:
                continue
            world = [(p[0] + npos[0] + noff[0], p[1] + npos[1] + noff[1], p[2] + npos[2] + noff[2]) for p in pts]
            if pool.find(_blocks.block_material(*key), world) is None:
                missing.append((key, world, uvs))           # culled against this block: needed while it is gone
        for key, world, uvs in missing:
            base = _blocks.block_material(*key)
            if base.name not in patch_index:
                patch_index[base.name] = len(patch_mats)
                patch_mats.append(base)
            patch_quads.append((patch_index[base.name], world, uvs, key[4] is not None, None))
    removed = pool.commit()
    col = village.collection
    tag = name or "%s_%d_%d_%d" % (block_id, cell[0], cell[1], cell[2])
    crack_mats = [(tex, _crack_material(base, tag)) for tex, base in mats]
    me = _mesh_from_quads("fx_block_" + tag, quads, [m for _t, m in crack_mats])
    ob = bpy.data.objects.new("fx_block_" + tag, me)
    ob.location = (float(cell[0]), float(cell[1]), float(cell[2]))
    col.objects.link(ob)
    patches = []
    if patch_quads:
        pme = _mesh_from_quads("fx_patch_" + tag, patch_quads, patch_mats)
        pob = bpy.data.objects.new("fx_patch_" + tag, pme)
        col.objects.link(pob)
        pob.hide_render = pob.hide_viewport = True
        patches.append(pob)
    stats = {"faces": len(quads), "model_faces": expected, "patch_faces": len(patch_quads), "removed": removed}
    block = Block(village, cell, block_id, props, ob, patches, crack_mats, stats)
    registry[cell] = block
    return block


def hall_job_block(village, n=1):
    """The workstation in front of trading-hall cell n as a Block (cell 1 = the librarian's lectern)."""
    return extract_block(village, "cell_%d_station" % n)


# ----------------------------------------------------------------------------------------------------
# 4. particles
# ----------------------------------------------------------------------------------------------------
_BURSTS = []       # every Burst of this Blender session (stop_particles walks it; bursts of a reset scene drop out)


class Burst:
    """What emit() / break_block() made: .kind, .frame, .objects (one quad per particle), .particles (dicts with
    the simulated tick positions 'pos', 'lifetime' in ticks, 'size' = half the quad's side, 'spawn' frame,
    'first' / 'last' = the frames it is visible on, first..last-1, 'object'), .frame_end (the last frame on which
    any of them is visible). stop(frame) ends it early."""

    def __init__(self, kind, frame):
        self.kind, self.frame = kind, frame
        self.objects, self.particles = [], []
        self.frame_end = frame
        _BURSTS.append(self)

    def __repr__(self):
        return "<fx.Burst %s x%d frames %s-%s>" % (self.kind, len(self.objects), self.frame, self.frame_end)

    def extend(self, other):
        """Merge another burst into this one."""
        self.objects.extend(other.objects)
        self.particles.extend(other.particles)
        self.frame_end = max(self.frame_end, other.frame_end)
        if other in _BURSTS:
            _BURSTS.remove(other)
        return self

    def stop(self, frame):
        """Nothing of this burst is visible from `frame` on (a CONSTANT visibility key on every particle that
        would outlive it): for a cut that jumps in time while crumbs or sprites still hang in the air. Returns the
        number of particles it ended."""
        frame = int(frame)
        ended = 0
        for p in self.particles:
            if p["last"] <= frame:
                continue
            if p["first"] >= frame:                           # it would only have appeared after the stop
                frames, values = [p["first"] - 1], [1.0]
            else:
                frames, values = [p["first"] - 1, p["first"], frame], [1.0, 0.0, 1.0]
            for path in ("hide_render", "hide_viewport"):
                _write(p["object"], path, 0, frames, values, "CONSTANT")
            p["last"] = max(frame, p["first"])
            ended += 1
        seen = [p["last"] - 1 for p in self.particles if p["last"] > p["first"]]
        self.frame_end = max(seen) if seen else min(self.frame_end, frame - 1)
        return ended


def stop_particles(frame, bursts=None):
    """End every particle that would still be visible on `frame`: all bursts made so far (emit, break_block,
    gain_profession), or only the given ones. Call it for the first frame of a shot that jumps in time, before
    emitting that shot's own particles. Returns the number of particles ended."""
    ended = 0
    for b in list(_BURSTS if bursts is None else bursts):
        if b.objects and not _alive(b.objects[0]):            # its objects went with a scene that was reset
            if b in _BURSTS:
                _BURSTS.remove(b)
            continue
        ended += b.stop(frame)
    return ended


# kind -> sprites (textures/particle, as listed in assets/minecraft/particles/<kind>.json of the client jar)
_SPRITES = {"happy_villager": ("glint",), "angry_villager": ("angry",), "heart": ("heart",),
            "splash": ("splash_0", "splash_1", "splash_2", "splash_3")}
KINDS = tuple(_SPRITES)


def _particle_material(texture, tint=None, colour=1.0, glow=0.0):
    """Material of a particle quad: the game texture (Closest, through mcassets) x colour, cut out at alpha 0.1,
    plain diffuse: the quad's custom normals make it lit like an up-facing surface."""
    name = "fx/particle/%s%s*%g%s" % (texture, "#%02x%02x%02x" % tuple(tint) if tint else "", colour,
                                      "+%g" % glow if glow else "")
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    tex = N("ShaderNodeTexImage")
    tex.image = mc.texture(texture, tint=tint)
    tex.interpolation = "Closest"
    tex.extension = "EXTEND"
    mul = N("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    mul.inputs[7].default_value = (colour, colour, colour, 1.0)
    L(tex.outputs["Color"], mul.inputs[6])
    diff = N("ShaderNodeBsdfDiffuse")
    L(mul.outputs[2], diff.inputs["Color"])
    surface = diff.outputs[0]
    if glow > 0.0:
        em = N("ShaderNodeEmission")
        em.inputs["Strength"].default_value = glow
        L(mul.outputs[2], em.inputs["Color"])
        add = N("ShaderNodeAddShader")
        L(surface, add.inputs[0])
        L(em.outputs[0], add.inputs[1])
        surface = add.outputs[0]
    if mc.alpha_mode(texture) != "OPAQUE":
        clear = N("ShaderNodeBsdfTransparent")
        gt = N("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = 0.1
        L(tex.outputs["Alpha"], gt.inputs[0])
        cut = N("ShaderNodeMixShader")
        L(gt.outputs[0], cut.inputs[0])
        L(clear.outputs[0], cut.inputs[1])
        L(surface, cut.inputs[2])
        surface = cut.outputs[0]
    L(surface, out.inputs["Surface"])
    try:
        mat.cycles.emission_sampling = "NONE"
    except (AttributeError, TypeError):
        pass
    mat["mc_texture"] = texture
    return mat


def _quad_mesh(name, rect, material):
    """A 2 x 2 quad in the local XY plane facing +Z (the game's (+-1, +-1) particle quad) showing the texture
    rectangle rect = (u at x=-1, u at x=+1, v at the top, v at the bottom), v measured downward as in the game.
    Custom normals point along local +Y: after copying the camera's rotation that is the camera's up vector, so
    the quad is shaded like a surface facing up, whatever the light direction (in-plane normal, as blocks.py does
    for 'shade up' plants)."""
    u0, u1, v0, v1 = rect
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0), (1.0, 1.0, 0.0), (-1.0, 1.0, 0.0)], [], [(0, 1, 2, 3)])
    layer = me.uv_layers.new(name="UVMap")
    layer.data.foreach_set("uv", [u0, 1.0 - v1, u1, 1.0 - v1, u1, 1.0 - v0, u0, 1.0 - v0])
    me.materials.append(material)
    me.polygons.foreach_set("use_smooth", [True])
    me.normals_split_custom_set([(0.0, 1.0, 0.0)] * 4)
    me.update()
    return me


def _film_of(camera):
    """The shots.Film behind a camera argument (a Film, or a Shot of one), else None."""
    if hasattr(camera, "shots") and hasattr(camera, "finalize"):
        return camera
    film = getattr(camera, "film", None)
    if film is not None and hasattr(camera, "camera") and hasattr(film, "shots"):
        return film
    return None


def _alive(idb):
    """True for a datablock reference that still exists (False after the scene it lived in was reset)."""
    try:
        return idb is not None and bool(idb.name)
    except ReferenceError:
        return False


def camera_proxy(film):
    """The empty every particle of `film` copies its rotation from: it always has the rotation of the camera
    of the shot that is on (see bind_cameras). Made on first use."""
    proxy = film.__dict__.get("_fx_proxy")
    if not _alive(proxy):
        proxy = bpy.data.objects.new("fx_camera", None)
        proxy.empty_display_size = 0.1
        _collection().objects.link(proxy)
        film.__dict__["_fx_proxy"] = proxy
        film.__dict__["_fx_bound"] = None
    return proxy


def bind_cameras(film):
    """Bind the particles of `film` to its shot cameras as the shots stand NOW: on every frame they face the camera
    of the shot that is on, whatever shot they were emitted in and whichever shots were added afterwards.

    Nobody has to call this in a film built the usual way: emit / break_block do it for the shots that exist, and
    Film.finalize() (Stage.finish(), render.py) does it again when the shot list is complete, because the first
    Shot or Film passed as `camera` wraps that film's finalize. Call it yourself only if you add or re-time shots
    after finalize(). Returns the proxy empty (camera_proxy)."""
    proxy = camera_proxy(film)
    shots = sorted(film.shots, key=lambda s: s.frame_start)
    state = tuple((s.camera.name, int(s.frame_start)) for s in shots)
    if film.__dict__.get("_fx_bound") != state:
        for con in list(proxy.constraints):
            proxy.constraints.remove(con)
        ad = proxy.animation_data
        if ad is not None:
            act = ad.action
            proxy.animation_data_clear()
            if act is not None and act.users == 0:
                bpy.data.actions.remove(act)
        for i, s in enumerate(shots):                       # later constraints win: one per shot, on from its cut
            con = proxy.constraints.new("COPY_ROTATION")
            con.name = "fx_shot%d" % i
            con.target = s.camera
            if i:
                _step(proxy, 'constraints["%s"].influence' % con.name, int(s.frame_start), 1.0, before=0.0)
        film.__dict__["_fx_bound"] = state
    if not film.__dict__.get("_fx_hooked"):                 # bind once more when the film is finalized
        inner = film.finalize

        def finalize(*args, **kwargs):
            """shots.Film.finalize, then fx.bind_cameras (particles face the camera of every shot)."""
            out = inner(*args, **kwargs)
            bind_cameras(film)
            return out

        film.finalize = finalize
        film.__dict__["_fx_hooked"] = True
    return proxy


def _camera_arg(camera):
    """The object particle quads copy their rotation from: for a Shot or a Film the film's camera proxy (the
    active camera of every shot, bound late), for a camera object that camera, for None the scene camera."""
    film = _film_of(camera)
    if film is not None:
        return bind_cameras(film)
    if camera is None:
        camera = bpy.context.scene.camera
        if camera is None:
            raise ValueError("fx: particles face the camera - pass camera=<Shot | Film | camera object>")
    if isinstance(camera, bpy.types.Object):
        return camera
    if isinstance(getattr(camera, "camera", None), bpy.types.Object):
        return camera.camera
    raise TypeError("fx: camera must be a Shot, a Film or a camera object")


def _face_camera(ob, target):
    """Copy the camera's rotation, as SingleQuadParticle.FacingCameraMode.LOOKAT_XYZ does."""
    con = ob.constraints.new("COPY_ROTATION")
    con.name = "fx_face"
    con.target = target


class _Solids:
    """Collision boxes of the village world around a burst (full cubes, slabs, lecterns)."""

    def __init__(self, village, ignore=()):
        self.world = village.world if village is not None else None
        self.ignore = set(ignore)
        self.cache = {}

    def at(self, cell):
        """World-space collision boxes of one grid cell."""
        boxes = self.cache.get(cell)
        if boxes is None:
            boxes = []
            w = self.world
            if w is not None and cell in w.blocks and cell not in self.ignore:
                bid, bprops = w.get(*cell)
                if bid == "lectern" or bid.endswith("_slab") or bid == "stonecutter":
                    shape = _collision_shape(bid, bprops)
                elif w.is_full_cube(*cell):
                    shape = _FULL
                elif bid in ("dirt_path", "farmland"):
                    shape = [(0.0, 0.0, 0.0, 16.0, 15.0, 16.0)]
                else:
                    shape = []
                for b in shape:
                    bb = _to_blender_box(b)
                    boxes.append((bb[0] + cell[0], bb[1] + cell[1], bb[2] + cell[2],
                                  bb[3] + cell[0], bb[4] + cell[1], bb[5] + cell[2]))
            self.cache[cell] = boxes
        return boxes

    def inside(self, p):
        """True when point p lies inside a collision box."""
        cell = (int(math.floor(p[0])), int(math.floor(p[1])), int(math.floor(p[2])))
        return any(b[0] <= p[0] <= b[3] and b[1] <= p[1] <= b[4] and b[2] <= p[2] <= b[5] for b in self.at(cell))

    def near(self, lo, hi):
        """Collision boxes of every cell touched by the box lo..hi."""
        out = []
        for x in range(int(math.floor(lo[0] - 1e-3)), int(math.floor(hi[0] + 1e-3)) + 1):
            for y in range(int(math.floor(lo[1] - 1e-3)), int(math.floor(hi[1] + 1e-3)) + 1):
                for z in range(int(math.floor(lo[2] - 1e-3)), int(math.floor(hi[2] + 1e-3)) + 1):
                    out.extend(self.at((x, y, z)))
        return out

    def collide(self, pos, move, width):
        """Entity.collideBoundingBox for a particle box (bottom centre at pos, width x width x width): the
        movement that is possible, resolved up/down first, then the larger horizontal axis."""
        if self.world is None:
            return move
        h = width / 2.0
        lo = [pos[0] - h, pos[1] - h, pos[2]]
        hi = [pos[0] + h, pos[1] + h, pos[2] + width]
        boxes = self.near([min(lo[i], lo[i] + move[i]) for i in range(3)],
                          [max(hi[i], hi[i] + move[i]) for i in range(3)])
        if not boxes:
            return move
        out = [move[0], move[1], move[2]]
        order = (2, 1, 0) if abs(move[0]) < abs(move[1]) else (2, 0, 1)
        eps = 1e-7
        for ax in order:
            d = out[ax]
            if d == 0.0:
                continue
            a, b = [i for i in range(3) if i != ax]
            for bx in boxes:
                if hi[a] <= bx[a] + eps or lo[a] >= bx[a + 3] - eps or hi[b] <= bx[b] + eps or lo[b] >= bx[b + 3] - eps:
                    continue
                if d > 0.0 and hi[ax] <= bx[ax] + eps:
                    d = min(d, bx[ax] - hi[ax])
                elif d < 0.0 and lo[ax] >= bx[ax + 3] - eps:
                    d = max(d, bx[ax + 3] - lo[ax])
            out[ax] = d
            lo[ax] += d
            hi[ax] += d
        return out


def _base_velocity(rng, va):
    """Particle(level, x, y, z, xa, ya, za): the randomised start velocity (Blender axes, blocks per tick)."""
    v = np.array(va, dtype=np.float64) + (rng.random(3) * 2.0 - 1.0) * 0.4
    speed = (rng.random() + rng.random() + 1.0) * 0.15
    v = v / max(float(np.linalg.norm(v)), 1e-9) * speed * 0.4
    v[2] += 0.1
    return v


def _simulate(pos, vel, lifetime, gravity, friction, solids, width, rng, ground_kill=0.0):
    """Particle.tick() `lifetime` times. gravity is subtracted from the upward speed per tick. Returns the list of
    positions after 0..n ticks (n < lifetime if it died on the ground, as SplashParticle can)."""
    p = [float(c) for c in pos]
    v = [float(c) for c in vel]
    out = [tuple(p)]
    stopped = on_ground = False
    for _k in range(lifetime):
        v[2] -= gravity
        if not stopped:
            want = (v[0], v[1], v[2])
            got = solids.collide(p, want, width) if solids is not None else want
            p = [p[i] + got[i] for i in range(3)]
            if abs(want[2]) >= 1e-5 and abs(got[2]) < 1e-5:
                stopped = True                               # Particle.move: stoppedByCollision
            on_ground = want[2] != got[2] and want[2] < 0.0
            if want[0] != got[0]:
                v[0] = 0.0
            if want[1] != got[1]:
                v[1] = 0.0
        v = [c * friction for c in v]
        if on_ground:
            if ground_kill and rng.random() < ground_kill:
                out.append(tuple(p))
                break
            v[0] *= 0.7
            v[1] *= 0.7
        out.append(tuple(p))
    return out


def _particle_object(burst, name, mesh, positions, spawn, size, cams, collection, grow=0.0):
    """One particle quad with the game's timing: it appears on the spawn frame, stands still for one tick, then
    reaches tick position k at spawn + (k + 1) ticks, and is removed one tick after its last move."""
    ob = bpy.data.objects.new(name, mesh)
    collection.objects.link(ob)
    n = len(positions) - 1
    frames = [spawn] + [spawn + (k + 1) * TICK for k in range(n + 1)]
    pts = [positions[0]] + list(positions)
    for i in range(3):
        _write(ob, "location", i, frames, [p[i] for p in pts], "LINEAR")
    ob.location = positions[0]
    if grow > 0.0:
        for i in range(3):
            _write(ob, "scale", i, [spawn, spawn + grow], [0.0005, size], "LINEAR")
    ob.scale = (size, size, size)
    first = int(math.ceil(spawn - 1e-6))
    last = int(math.ceil(spawn + (n + 1) * TICK - 1e-6))       # first frame on which it is gone
    last = max(last, first + 1)
    for path in ("hide_render", "hide_viewport"):
        _write(ob, path, 0, [first - 1, first, last], [1.0, 0.0, 1.0], "CONSTANT")
    ob.hide_render = ob.hide_viewport = True
    ob.visible_shadow = False
    _face_camera(ob, cams)
    burst.objects.append(ob)
    burst.particles.append({"object": ob, "pos": positions, "lifetime": n, "size": size, "spawn": spawn,
                            "first": first, "last": last})
    burst.frame_end = max(burst.frame_end, last - 1)
    return ob


def _rng(seed, *salt):
    return np.random.default_rng([int(seed) & 0x7FFFFFFF] + [int(s) & 0x7FFFFFFF for s in salt])


SPRITE_GLOW = 0.6     # default self-light of the entity-event sprites (see emit)


def emit(kind, pos, frame, camera=None, count=None, seed=0, village=None, glow=None, size=VILLAGER_SIZE,
         collection=None, in_air=False):
    """Particle burst of an entity event around a Character or the feet point `pos`, starting on `frame`.

    kind 'happy_villager' | 'angry_villager' | 'heart' | 'splash' (see the module docstring for the events).
    count = number of particles (the game: 5 per event). size = the entity's (width, height) bounding box.
    glow = self-light, 0..1 of the sprite's own colour (default SPRITE_GLOW 0.6: the game draws a particle at the
    light level of the place, with no shading by direction, so in a lit room it is nearly as bright as its
    texture; plain diffuse sprites came out near black in the hall's corners).
    village = the Village: needed for splash (it collides) and for in_air=True, which draws again every start
    position that lies inside a solid block. The game does not do that: in a 1x1 trading cell about half of the 5
    particles start inside the walls and are never seen. Returns a Burst."""
    if kind not in _SPRITES:
        raise ValueError("fx.emit: unknown kind %r (use one of %s; block particles come from break_block)"
                         % (kind, ", ".join(KINDS)))
    frame = int(frame)
    feet = _point(pos, frame)
    rng = _rng(seed, frame, KINDS.index(kind), int(feet.x * 16), int(feet.y * 16))
    col = _collection(collection)
    burst = Burst(kind, frame)
    cams = _camera_arg(camera)
    solids = _Solids(village) if (kind == "splash" or in_air) and village is not None else None
    glow = SPRITE_GLOW if glow is None else float(glow)
    n = 5 if count is None else int(count)                   # AbstractVillager.addParticlesAroundSelf: 5
    w, h = size
    for i in range(n):
        va = rng.normal(0.0, 1.0, 3) * 0.02                  # nextGaussian() * 0.02 per axis
        for _try in range(30):
            p = np.array([feet.x + w * (2.0 * rng.random() - 1.0),      # getRandomX(1.0)
                          feet.y + w * (2.0 * rng.random() - 1.0),      # getRandomZ(1.0)
                          feet.z + h * rng.random() + 1.0])             # getRandomY() + 1.0
            if not (in_air and solids is not None and solids.inside(p)):
                break
        quad = 0.1 * (rng.random() * 0.5 + 0.5) * 2.0        # SingleQuadParticle: quadSize
        grow = 0.0
        sprite = _SPRITES[kind][int(rng.integers(0, len(_SPRITES[kind])))]
        if kind == "happy_villager":                         # SuspendedTownParticle + HappyVillagerProvider
            v = _base_velocity(rng, va) * 0.02
            quad *= rng.random() * 0.6 + 0.5
            life = int(20.0 / (rng.random() * 0.8 + 0.2))
            path = _simulate(p, v, life, 0.0, 0.99, None, 0.02, rng)
        elif kind in ("angry_villager", "heart"):            # HeartParticle (+ AngryVillagerProvider: y + 0.5)
            if kind == "angry_villager":
                p[2] += 0.5
            v = _base_velocity(rng, (0.0, 0.0, 0.0)) * 0.01
            v[2] += 0.1
            quad *= 1.5
            life = 16
            grow = 0.5 * TICK                                # getQuadSize: full size after lifetime / 32 ticks
            path = _simulate(p, v, life, 0.0, 0.86, None, 0.2, rng)
        else:                                                # SplashParticle extends WaterDropParticle
            v = _base_velocity(rng, (0.0, 0.0, 0.0))
            v[0] *= 0.3
            v[1] *= 0.3
            v[2] = rng.random() * 0.2 + 0.1
            life = int(8.0 / (rng.random() * 0.8 + 0.2))
            path = _simulate(p, v, life, 0.04, 0.98, solids if kind == "splash" else None, 0.01, rng,
                             ground_kill=0.5)
        mat = _particle_material("particle/" + sprite, glow=glow)
        mname = "fx_quad_%s%s" % (sprite, "+%g" % glow if glow else "")
        mesh = bpy.data.meshes.get(mname) or _quad_mesh(mname, (0.0, 1.0, 0.0, 1.0), mat)
        _particle_object(burst, "fx_%s_%d_%d" % (kind, frame, i), mesh, path, float(frame), quad, cams, col, grow)
    return burst


# TerrainParticle: rCol = gCol = bCol = 0.6 (x tint). The game multiplies that onto the texel in DISPLAY space
# (core/particle.fsh: texture x vertex colour x light map), so in scene-linear it is 0.6 ^ 2.2 = 0.325: the crumbs are
# clearly darker than the block they came from.
TERRAIN_COLOUR = 0.6 ** 2.2


def _terrain_particle(burst, block, rng, p, va, spawn, cams, col, solids, glow, hit=False):
    """One TerrainParticle of `block` at world point p with velocity argument va (Blender axes)."""
    v = _base_velocity(rng, va)
    life = int(4.0 / (rng.random() * 0.9 + 0.1))            # Particle: lifetime 4..40 ticks
    quad = 0.1 * (rng.random() * 0.5 + 0.5) * 2.0 / 2.0     # SingleQuadParticle, halved by TerrainParticle
    width = 0.2
    if hit:                                                  # ClientLevel.addBreakingParticles: setPower(0.2).scale(0.6)
        v[0] *= 0.2
        v[1] *= 0.2
        v[2] = (v[2] - 0.1) * 0.2 + 0.1
        quad *= 0.6
        width *= 0.6
    uo, vo = rng.random() * 3.0, rng.random() * 3.0
    path = _simulate(p, v, life, 0.04, 0.98, solids, width, rng)   # gravity 1.0 x 0.04 per tick, friction 0.98
    tex, tint = block.particle_texture
    mat = _particle_material(tex, tint=tint, colour=TERRAIN_COLOUR, glow=glow)
    # getU0 = (uo + 1) / 4, getU1 = uo / 4 (mirrored), getV0 = vo / 4, getV1 = (vo + 1) / 4: a quarter of the sprite
    i = len(burst.objects)
    mesh = _quad_mesh("fx_crumb_%s_%d" % (block.name, i), ((uo + 1.0) / 4.0, uo / 4.0, vo / 4.0, (vo + 1.0) / 4.0), mat)
    return _particle_object(burst, "fx_crumb_%s_%s_%d" % (block.name, ("h%d" if hit else "%d") % int(spawn), i),
                            mesh, path, spawn, quad, cams, col)


def _destroy_particles(block, frame, camera, seed, glow, collection=None):
    """ClientLevel.addDestroyBlockEffect: for every box of the outline shape, max(2, ceil(size / 0.25)) particles
    per axis on a regular grid, each thrown away from the middle of its box."""
    burst = Burst("block", frame)
    cams = _camera_arg(camera)
    col = _collection(collection)
    solids = _Solids(block.village, ignore=[block.cell])
    cx, cy, cz = block.cell
    for bi, b in enumerate(block.shape):
        d = [min(1.0, b[3 + i] - b[i]) for i in range(3)]
        n = [max(2, int(math.ceil(d[i] / 0.25 - 1e-9))) for i in range(3)]
        for i in range(n[0]):
            for j in range(n[1]):
                for k in range(n[2]):
                    f = ((i + 0.5) / n[0], (j + 0.5) / n[1], (k + 0.5) / n[2])
                    # Blender y runs against Minecraft z: the box's min-z corner is its max-y corner
                    p = (cx + b[0] + f[0] * d[0], cy + b[4] - f[1] * d[1], cz + b[2] + f[2] * d[2])
                    va = (f[0] - 0.5, -(f[1] - 0.5), f[2] - 0.5)
                    rng = _rng(seed, frame, bi, i * 64 + j * 8 + k, cx * 31 + cy)
                    _terrain_particle(burst, block, rng, p, va, float(frame), cams, col, solids, glow)
    return burst


def _hit_particles(block, frame_start, frame_end, hit_from, camera, seed, glow, collection=None):
    """ClientLevel.addBreakingParticles: one small crumb per tick, 0.1 off the face that is being hit."""
    burst = Burst("block_hit", frame_start)
    cams = _camera_arg(camera)
    col = _collection(collection)
    solids = _Solids(block.village)
    lo = [min(b[i] for b in block.shape) for i in range(3)]
    hi = [max(b[3 + i] for b in block.shape) for i in range(3)]
    d = _point(hit_from, frame_start) - block.center
    axis = 0 if abs(d.x) > abs(d.y) else 1
    if math.hypot(d.x, d.y) < 0.5:
        axis = 2
    side = 1.0 if d[axis] > 0.0 else -1.0
    ticks = int(math.floor((frame_end - frame_start) / TICK + 1e-6))
    for t in range(ticks):
        rng = _rng(seed, frame_start, 7919, t)
        p = [block.cell[i] + rng.random() * (hi[i] - lo[i] - 0.2) + 0.1 + lo[i] for i in range(3)]
        p[axis] = block.cell[axis] + (hi[axis] + 0.1 if side > 0 else lo[axis] - 0.1)
        _terrain_particle(burst, block, rng, p, (0.0, 0.0, 0.0), frame_start + t * TICK, cams, col, solids, glow,
                          hit=True)
    return burst


# ----------------------------------------------------------------------------------------------------
# 2. + 3. breaking and placing
# ----------------------------------------------------------------------------------------------------
# ToolMaterial: speed of WOOD 2, STONE 4, COPPER 5, IRON 6, DIAMOND 8, NETHERITE 9, GOLD 12; the empty hand is 1.
# The lectern is in the block tag mineable/axe, so an axe's speed applies to it.
_TOOL_SPEED = {"hand": 1.0, "wooden_axe": 2.0, "stone_axe": 4.0, "copper_axe": 5.0, "iron_axe": 6.0,
               "diamond_axe": 8.0, "netherite_axe": 9.0, "golden_axe": 12.0}
_HARDNESS = {"lectern": 2.5}                                  # Blocks.LECTERN: strength(2.5F)


def break_frames(block_id="lectern", tool="hand", hardness=None):
    """Frames the game needs to mine a block: progress per tick = tool speed / hardness / 30 (BlockBehaviour
    .getDestroyProgress), broken on the first tick it reaches 1. Lectern (hardness 2.5): hand 90 frames, wooden
    axe 46, stone 23, copper 18, iron 16, diamond 12, netherite 11, golden 8."""
    hardness = _HARDNESS.get(block_id, 2.5) if hardness is None else hardness
    ticks = int(math.ceil(hardness * 30.0 / _TOOL_SPEED[tool] - 1e-9))
    return int(round(ticks * TICK))


def break_block(block, frame_start, frame_end, camera=None, hit_from=None, seed=0, particles=True, glow=0.0):
    """Mine `block` from frame_start and break it ON frame_end (see the module docstring). Returns the Burst of the
    break particles (with the mining crumbs merged in when hit_from is given); Burst.frame_end is the last frame a
    particle is visible. camera = the Shot / camera object / Film that films it."""
    f0, f1 = int(frame_start), int(frame_end)
    if f1 <= f0:
        raise ValueError("fx.break_block: frame_end must be after frame_start")
    block.show(f0, True)
    last = None
    for f in range(f0, f1):
        stage = min(9, int(10.0 * (f - f0) / float(f1 - f0)))    # MultiPlayerGameMode.getDestroyStage: (int)(progress * 10)
        if stage != last:
            block.crack(f, stage)
            last = stage
    block.crack(f1, -1)
    block.show(f1, False)
    burst = Burst("block", f1)
    if particles:
        burst.extend(_destroy_particles(block, f1, camera, seed, glow))
        if hit_from is not None:
            burst.extend(_hit_particles(block, f0, f1, hit_from, camera, seed, glow))
    return burst


def place_block(block, frame):
    """The block is back from `frame` on, uncracked. The game has no placing animation and no particles: swing the
    player's arm with Character.swing_arm(frame - 2), or with arm_swings(player, [frame - 2]) when another swing or
    a mining span ends less than 9 frames earlier (Character.swing_arm must not overlap another swing)."""
    block.crack(int(frame), -1)
    block.show(int(frame), True)
    return block


# ----------------------------------------------------------------------------------------------------
# the player's arm swing, played by the game's own state machine (mining, placing in quick succession)
# ----------------------------------------------------------------------------------------------------
SWING_TICKS = 6          # SwingAnimation.DEFAULT = (SwingAnimationType.WHACK, 6 ticks): the hand, blocks, axes
_SWING_KEYS = 4          # keys per game tick (the pose is a curve in the animation value)
_SWING_LIMIT = 1.95      # as Character.swing_arm: never past overhead


def _swing_run(requests):
    """LivingEntity$SwingState for one run of swings. requests = the ticks (ints, the first one 0) on which
    LivingEntity.swing() is called; the entity ticks after it, as on the client (Minecraft.continueAttack runs
    before the entities tick). Returns (starts, shown, end): the ticks on which a swing really started
    (startIfAble: none running, or more than half of it done), per tick k the two animation values the client
    draws between during [k, k + 1) (getAnimation: lerp(partial, oldAnimation, animation), animation + 1 when
    it wrapped), and the first tick at which the run is over (requests from there on belong to the next run)."""
    want = set(int(r) for r in requests)
    starts, shown = [], []
    swinging, ticks, anim = False, 0, 0.0
    k = 0
    while True:
        if k in want and (not swinging or ticks > SWING_TICKS // 2 or ticks <= 0):
            swinging, ticks = True, 0                         # start(): the same SwingDescription keeps `animation`
            starts.append(k)
        old = anim
        if swinging:
            anim = min(ticks / float(SWING_TICKS), 1.0)
            ticks += 1
            if ticks - 1 > SWING_TICKS:
                swinging, anim = False, 0.0
        else:
            anim = 0.0
        shown.append((old, anim if anim >= old else anim + 1.0))
        k += 1
        if not swinging and anim == 0.0 and k not in want:
            return starts, shown, k


def _swing_pose(t, head_pitch):
    """HumanoidModel.setupAttackAnimation (WHACK) at animation value t, as offsets from the rest pose in model
    terms: (body yRot, swinging arm xRot, the arm's extra yRot, its zRot). Zero at t = 0 and at t = 1."""
    if t <= 0.0 or t >= 1.0:
        return 0.0, 0.0, 0.0, 0.0
    body = math.sin(math.sqrt(t) * 2.0 * math.pi) * 0.2
    g = math.sin((1.0 - (1.0 - t) ** 4) * math.pi)            # Ease.outQuart
    h = math.sin(t * math.pi) * (0.7 - head_pitch) * 0.75     # -(head.xRot - 0.7) * 0.75
    return body, -(g * 1.2 + h), 2.0 * body, -0.4 * math.sin(t * math.pi)


def _swing_channels(character):
    """(object, euler index, pose term, sign) of the channels a swing moves. Model x, y, z rotations are the
    rig's euler x, -z, y; the arms hang on the body, so the body's turn carries them (rightArm.yRot += body.yRot,
    and the shoulder pivots); the head does not turn with the body in the game, so it is turned back."""
    c = character
    return ((c.body, 2, 0, -1.0),          # body.yRot
            (c.head, 2, 0, 1.0),           # head stays where it looks
            (c.arm_r, 0, 1, 1.0),          # rightArm.xRot -= g * 1.2 + h
            (c.arm_r, 2, 2, -1.0),         # rightArm.yRot += body.yRot * 2
            (c.arm_r, 1, 3, 1.0),          # rightArm.zRot += sin(t * pi) * -0.4
            (c.arm_l, 0, 0, 1.0))          # leftArm.xRot += body.yRot


def arm_swings(character, frames):
    """The player's right-arm swing (mine, place, use, hit) for a swing request on each of `frames`, played by the
    game's own rule: a request starts a swing when none is running or the running one is more than half done
    (LivingEntity$SwingState.startIfAble; a swing is 6 ticks = 7.2 frames), otherwise it is ignored. Returns the
    frames on which a swing really starts.

    Unlike Character.swing_arm (an additive 8-frame gesture that must not overlap another one) this writes
    ABSOLUTE keys from the pose the player has at the first request, so swings may follow each other as closely
    as the game allows and the arm, body and head always come back exactly to that pose. The arm starts to move
    one tick (1.2 frames) after a request and is highest about 2.4 frames after it, as on the client (which draws
    between the last two tick states). Keys: LINEAR, four per tick, on arm_r (x, y, z), arm_l (x), body (z) and
    head (z); call place() and look_at() BEFORE this, not inside the span."""
    C = characters
    if character.arm_r is None:
        raise ValueError("fx.arm_swings / mining_swings are for the player rig (a villager has no free arm)")
    reqs = sorted(float(f) for f in frames)
    if not reqs:
        return []
    chans = _swing_channels(character)
    rot = "rotation_euler"
    run = character.__dict__.get("_fx_swing")
    if run is not None:                                       # is the last fx run still swinging at the new request,
        fc = C._find(character.arm_r, rot, 0)                 # and still whole (no place() cut it short)?
        keys = [] if fc is None else [(kp.co.x, kp.interpolation) for kp in fc.keyframe_points]
        whole = (any(abs(x - run["end"]) < 1e-3 for x, _i in keys)
                 and not any(run["f0"] + 1e-3 < x < run["end"] - 1e-3 and i == "CONSTANT" for x, i in keys))
        if not (whole and run["f0"] - 1e-6 <= reqs[0] < run["end"] - 1e-6):
            run = None
    started = []
    while reqs:
        if run is not None:                                   # go on with that run: same tick grid, same rest pose
            f0, base = run["f0"], run["base"]
            reqs = sorted(set(run["requests"]) | set(reqs))
            run = None
        else:
            f0 = reqs[0]
            base = [C._val(ob, rot, index, f0) for ob, index, _term, _sign in chans]
        ticks = [int(round((f - f0) / TICK)) for f in reqs]
        starts, shown, end = _swing_run(ticks)
        mine = [f for f, k in zip(reqs, ticks) if k < end]
        reqs = [f for f, k in zip(reqs, ticks) if k >= end]
        while len(shown) > 1 and shown[-1][0] in (0.0, 1.0) and shown[-1][1] in (0.0, 1.0):
            shown.pop()                                       # at rest again: the run ends here
        times, poses = [], []
        for k, (a, b) in enumerate(shown):
            for j in range(_SWING_KEYS):
                u = j / float(_SWING_KEYS)
                f = f0 + (k + u) * TICK
                times.append(f)
                poses.append(_swing_pose(a + (b - a) * u, C._val(character.head, rot, 0, f)))
        f_end = f0 + len(shown) * TICK
        for (ob, index, term, sign), rest in zip(chans, base):
            keys = [(times[0], None)]
            for f, pose in zip(times[1:], poses[1:]):
                keys.append((f, max(-_SWING_LIMIT, min(_SWING_LIMIT, rest + sign * pose[term]))))
            keys.append((f_end, rest))
            C._segment(ob, rot, index, keys, "LINEAR")
        character.__dict__["_fx_swing"] = {"f0": f0, "end": f_end, "requests": mine, "base": base}
        started.extend(f0 + k * TICK for k in starts)
    return started


def mining_swings(character, frame_start, frame_end, every=None):
    """The player's arm while he mines from frame_start until the block breaks on frame_end: a swing request on
    every game tick, as Minecraft.continueAttack makes while the button is held, so the arm repeats every 4 ticks
    = 4.8 frames (up in one tick, down over two, back in the fourth). The swing that is running when the block
    breaks is finished: the arm is back at rest at most 9 frames after frame_end, exactly in the pose it had at
    frame_start. every = frames between requests instead (8 or more gives separate complete swings).
    Returns the frames on which a swing starts. See arm_swings."""
    f0, f1 = float(frame_start), float(frame_end)
    n = max(0, int(math.floor((f1 - f0) / TICK + 1e-6)))
    step = 1 if every is None else max(1, int(round(float(every) / TICK)))
    return arm_swings(character, [f0 + k * TICK for k in range(0, n + 1, step)])


# ----------------------------------------------------------------------------------------------------
# 5. profession change
# ----------------------------------------------------------------------------------------------------
class JobVillager(characters.Character):
    """A villager with several profession outfits on one rig (make_job_villager).

    The rig of the first profession is the Character itself; every other outfit is a second set of part meshes
    (other texture sheet, other cut-outs) parented one-to-one to the rig's parts, so all of them share every
    transform and every keyframe. Exactly one outfit is rendered. `outfits` = {profession: [part objects]}."""

    def __init__(self, name, professions=("librarian", "none"), level=1, biome="plains", collection=None):
        C = characters
        profs = []
        for p in professions:
            p = C.PROFESSION_ALIASES.get(p, p)
            if p not in C.villager_professions():
                raise ValueError("unknown profession %r" % p)
            if p not in profs:
                profs.append(p)
        spec = C._villager_spec()
        col = C._collection(collection)
        key, sheet = C.villager_sheet(profs[0], biome=biome, level=level)
        parts = C._build_rig(name, spec, sheet, C._sheet_material(key, sheet), col,
                             C._sheet_material_two_sided(key, sheet))
        super().__init__(name, "villager", parts, spec, profession=profs[0], child=False)
        names = [p["name"] for p in spec["parts"]]
        self._spec_parts = spec["parts"]
        self.outfits = {profs[0]: [parts[n] for n in names]}
        unit = spec["scale"] / 16.0
        for prof in profs[1:]:
            key, sheet = C.villager_sheet(prof, biome=biome, level=level)
            mat, rim = C._sheet_material(key, sheet), C._sheet_material_two_sided(key, sheet)
            obs = []
            for part in spec["parts"]:
                me = C._part_mesh("%s_%s_%s" % (name, prof, part["name"]), part, sheet, unit, mat, rim)
                ob = bpy.data.objects.new(me.name, me)
                col.objects.link(ob)
                ob.parent = parts[part["name"]]
                ob.matrix_parent_inverse = Matrix.Identity(4)
                ob.hide_render = ob.hide_viewport = True
                obs.append(ob)
            self.outfits[prof] = obs
        self.professions = tuple(profs)
        self._jobs = [(None, profs[0])]           # (frame or None = from the beginning, profession)
        self._shown = [(None, True)]              # (frame or None, visible)

    @property
    def heads(self):
        """The head object of every outfit (the rig's own first): st.hero(shot, label, *villager.heads) names the
        face whatever he wears; Stage.hero(shot, label, villager) alone means the first outfit's head."""
        return [obs[[p["name"] for p in self._spec_parts].index("head")] for obs in self.outfits.values()]

    def objects(self):
        """All objects of the rig: empties, every outfit's parts, the held item."""
        obs = super().objects()
        for prof in self.professions[1:]:
            obs.extend(self.outfits[prof])
        return obs

    @staticmethod
    def _at(keys, frame):
        value = keys[0][1]
        for f, v in keys:
            if f is None or f <= frame + 1e-6:
                value = v
        return value

    def profession_at(self, frame):
        """The profession worn at `frame`."""
        return self._at(self._jobs, frame)

    def _rekey(self):
        frames = sorted({f for f, _v in self._jobs + self._shown if f is not None})
        for prof, obs in self.outfits.items():
            start = self._at(self._shown, -1e9) and self._at(self._jobs, -1e9) == prof
            keys = [(min(frames[0], 1) - 1 if frames else 0, start)]
            for f in frames:
                keys.append((f, self._at(self._shown, f) and self.profession_at(f) == prof))
            for ob in obs:
                for path in ("hide_render", "hide_viewport"):
                    _write(ob, path, 0, [k[0] for k in keys], [0.0 if k[1] else 1.0 for k in keys], "CONSTANT")
                ob.hide_render = ob.hide_viewport = not keys[0][1]
        if self.held is not None and frames:
            keys = [(min(frames[0], 1) - 1, self._at(self._shown, -1e9))] + [(f, self._at(self._shown, f)) for f in frames]
            for path in ("hide_render", "hide_viewport"):
                _write(self.held, path, 0, [k[0] for k in keys], [0.0 if k[1] else 1.0 for k in keys], "CONSTANT")

    def show(self, frame, visible=True):
        """Key the visibility of the whole villager from `frame` on (the outfit that is worn stays the only one)."""
        self._shown = [k for k in self._shown if k[0] != frame] + [(frame, bool(visible))]
        self._shown.sort(key=lambda k: -1e18 if k[0] is None else k[0])
        self._rekey()

    def set_profession(self, frame, profession):
        """Wear another profession's outfit from `frame` on (a cut, as in the game)."""
        profession = characters.PROFESSION_ALIASES.get(profession, profession)
        if profession not in self.outfits:
            raise ValueError("%s has no %r outfit (made with %s)" % (self.name, profession, ", ".join(self.outfits)))
        frame = int(frame)
        self._jobs = [k for k in self._jobs if k[0] != frame] + [(frame, profession)]
        self._jobs.sort(key=lambda k: -1e18 if k[0] is None else k[0])
        self.profession = self._jobs[-1][1]
        self._rekey()

    def lose_profession(self, frame):
        """Become the unemployed villager on `frame` (ResetProfession: no entity event, so no particles)."""
        self.set_profession(frame, "none")

    def gain_profession(self, frame, profession, camera=None, seed=0, **emit_kw):
        """Take a job on `frame`: the outfit changes and the 5 green 'happy_villager' particles appear on the same
        frame (AssignProfessionFromJobSite: entity event 14). emit_kw goes to emit() (count, glow, village,
        in_air). Returns the Burst."""
        self.set_profession(frame, profession)
        return emit("happy_villager", self, frame, camera=camera, seed=seed, **emit_kw)


def make_job_villager(name, professions=("librarian", "none"), level=1, biome="plains", collection=None):
    """A villager who can change profession (JobVillager): starts as professions[0]; set_profession(frame, p)
    switches. level=1 is the stone badge: the only level at which the game lets a villager lose his job."""
    return JobVillager(name, professions, level=level, biome=biome, collection=collection)


# ----------------------------------------------------------------------------------------------------
# 6. a villager showing a trade item
# ----------------------------------------------------------------------------------------------------
def crossed_arms_matrix(model_scale=characters.MODEL_SCALE):
    """Matrix of a flat item (engine.props.make_item: sprite in its local XZ plane, front -Y, 16 px = 1 unit)
    relative to a villager's `arms` part, transcribed independently of engine.characters from
    CrossedArmsItemLayer.applyTranslation (after VillagerModel.translateToArms: rotate X 0.75, scale 1.07,
    translate (0, 0.13, -0.34), rotate X pi) and the GROUND display transform of models/item/generated.json
    (translation [0, 2, 0] / 16, scale 0.5) that HoldingEntityRenderState asks for."""
    axes = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))      # model (x, y, z) -> Blender (x, z, -y)
    chain = (Matrix.Rotation(0.75, 4, "X") @ Matrix.Diagonal((1.07, 1.07, 1.07, 1.0))
             @ Matrix.Translation((0.0, 0.13, -0.34)) @ Matrix.Rotation(math.pi, 4, "X")
             @ Matrix.Translation((0.0, 2.0 / 16.0, 0.0)) @ Matrix.Diagonal((0.5, 0.5, 0.5, 1.0)))
    return Matrix.Diagonal((model_scale, model_scale, model_scale, 1.0)) @ axes @ chain @ axes


def held_item_point(character, frame=None):
    """World centre of an item on the crossed arms of a villager at `frame` (None = the current frame): for a
    villager standing upright it is 1.225 above his feet and 0.40 in front of his centre line."""
    scene = bpy.context.scene
    cur, sub = scene.frame_current, scene.frame_subframe
    if frame is not None:
        scene.frame_set(int(math.floor(frame)), subframe=float(frame) - math.floor(frame))
    else:
        bpy.context.view_layer.update()
    point = (character.arms.matrix_world @ crossed_arms_matrix(character.model_scale)).translation.copy()
    if frame is not None:
        scene.frame_set(cur, subframe=sub)
    return point


def hold_out(villager, item, frame_start, frame_end=None, enchanted=False, collection=None, **glint_kw):
    """A villager shows a trade item on his crossed arms from frame_start (until frame_end, exclusive), as the
    game's ShowTradesToPlayer does. item = an item id ('enchanted_book', 'emerald') or a props.make_item object.
    The item is parented to the arms but is NOT villager.held: its visibility is its own, so the film's per-shot
    show() calls cannot switch it on early. enchanted=True adds the glint. Returns the item object."""
    if villager.arms is None:
        raise ValueError("fx.hold_out is for villagers (crossed arms); the player uses Character.hold")
    if isinstance(item, str):
        ob = props.make_item(item, collection if collection is not None else _collection())
    else:
        ob = item
    ob.parent = villager.arms
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = crossed_arms_matrix(villager.model_scale)
    f0 = int(frame_start)
    keys = [(min(f0, 1) - 1, 1.0), (f0, 0.0)]
    if frame_end is not None:
        keys.append((int(frame_end), 1.0))
    for path in ("hide_render", "hide_viewport"):
        _write(ob, path, 0, [k[0] for k in keys], [k[1] for k in keys], "CONSTANT")
    ob.hide_render = ob.hide_viewport = True
    if enchanted:
        glint(ob, f0, frame_end, **glint_kw)
    return ob


# ----------------------------------------------------------------------------------------------------
# 7. enchantment glint
# ----------------------------------------------------------------------------------------------------
GLINT_SCALE = 8.0             # TextureTransform.GLINT_TEXTURING: setupGlintTexturing(8.0F)
GLINT_ROTATION = 0.17453292   # rotateZ: 10 degrees
GLINT_SPEED = 0.5             # Options.glintSpeed default
GLINT_STRENGTH = 0.75         # Options.glintStrength default (the shader's GlintAlpha)
GLINT_PERIOD_U = 110000.0 / (GLINT_SPEED * 8.0) / 1000.0      # 27.5 s per texture width, toward +u
GLINT_PERIOD_V = 30000.0 / (GLINT_SPEED * 8.0) / 1000.0       # 7.5 s per texture height
ITEM_ATLAS = 512.0            # the items atlas: 895 sprites of 16 px stitch into 512 x 512 (counted, not read from
#                               a running game); item UVs span 16 / 512, so one glint texture covers 4 item widths


def _glint_image():
    name = "fx/enchanted_glint_item"
    img = bpy.data.images.get(name)
    if img is None:
        arr = np.array(mc.texture_array("misc/enchanted_glint_item"), dtype=np.uint8)
        img = mc.image_from_array(name, arr)
        img.colorspace_settings.name = "Non-Color"         # the shader works on display values, as the game does
    return img


def glint(item_obj, frame_start=1, frame_end=None, strength=1.0, light=0.75, phase=0.0, fps=FPS):
    """Give a flat item (props.make_item) the enchantment glint between frame_start and frame_end (None = for good).

    The game (core/item.fsh with GLINT): colour += (GlintAlpha x glint texel)^2, added in display space AFTER the
    light map, with the glint texture looked up at TextureMat x item UV: scale 8, rotated 10 degrees, scrolling one
    texture width per 27.5 s and one height per 7.5 s (glint speed 0.5), linear filtering. Here it is an emission
    equal to the linear difference between the item's display colour with and without the added glint, for an
    item lit at `light` (0..1 of full brightness): the same purple shimmer over the book, which stays readable.
    strength scales the game's default (0.75). phase = seconds added to the scroll clock. Returns the material."""
    me = item_obj.data
    base = me.materials[0]
    if base.get("fx_glint"):
        mat = base
    else:
        mat = base.copy()
        mat.name = "fx/glint/%s" % item_obj.name
        mat["fx_glint"] = 1
        me.materials[0] = mat
        nt = mat.node_tree
        N, L = nt.nodes.new, nt.links.new
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
        uv = N("ShaderNodeUVMap")
        mp = N("ShaderNodeMapping")
        mp.name = "fx_glint_scroll"
        mp.vector_type = "POINT"
        k = GLINT_SCALE * 16.0 / ITEM_ATLAS                 # glint texture units per item width: 0.25
        mp.inputs["Scale"].default_value = (k, k, 1.0)
        mp.inputs["Rotation"].default_value = (0.0, 0.0, -GLINT_ROTATION)    # +10 degrees in v-down texture space
        L(uv.outputs[0], mp.inputs[0])
        g = N("ShaderNodeTexImage")
        g.name = "fx_glint"
        g.image = _glint_image()
        g.interpolation = "Linear"                          # enchanted_glint_item.png.mcmeta: "blur": true
        g.extension = "REPEAT"
        L(mp.outputs[0], g.inputs[0])
        amp = N("ShaderNodeVectorMath")                     # GlintAlpha x texel
        amp.name = "fx_glint_alpha"
        amp.operation = "SCALE"
        amp.inputs["Scale"].default_value = GLINT_STRENGTH * strength
        L(g.outputs["Color"], amp.inputs[0])
        sq = N("ShaderNodeVectorMath")                      # ... squared: BlendFunction.GLINT (SRC_COLOR, ONE)
        sq.operation = "MULTIPLY"
        L(amp.outputs[0], sq.inputs[0])
        L(amp.outputs[0], sq.inputs[1])
        disp = N("ShaderNodeGamma")                         # the item's own colour as a display value ...
        disp.inputs["Gamma"].default_value = 1.0 / 2.2
        L(tex.outputs["Color"], disp.inputs["Color"])
        lit = N("ShaderNodeVectorMath")                     # ... under the assumed light
        lit.name = "fx_glint_light"
        lit.operation = "SCALE"
        lit.inputs["Scale"].default_value = light
        L(disp.outputs[0], lit.inputs[0])
        total = N("ShaderNodeVectorMath")
        total.operation = "ADD"
        L(lit.outputs[0], total.inputs[0])
        L(sq.outputs[0], total.inputs[1])
        clip = N("ShaderNodeVectorMath")
        clip.operation = "MINIMUM"
        clip.inputs[1].default_value = (1.0, 1.0, 1.0)
        L(total.outputs[0], clip.inputs[0])
        lin1 = N("ShaderNodeGamma")
        lin1.inputs["Gamma"].default_value = 2.2
        L(clip.outputs[0], lin1.inputs["Color"])
        lin0 = N("ShaderNodeGamma")
        lin0.inputs["Gamma"].default_value = 2.2
        L(lit.outputs[0], lin0.inputs["Color"])
        diff = N("ShaderNodeVectorMath")
        diff.operation = "SUBTRACT"
        L(lin1.outputs[0], diff.inputs[0])
        L(lin0.outputs[0], diff.inputs[1])
        on = N("ShaderNodeValue")
        on.name = "fx_glint_on"
        on.outputs[0].default_value = 0.0
        L(diff.outputs[0], bsdf.inputs["Emission Color"])
        L(on.outputs[0], bsdf.inputs["Emission Strength"])
        try:
            mat.cycles.emission_sampling = "NONE"
        except (AttributeError, TypeError):
            pass
    nt = mat.node_tree
    nt.nodes["fx_glint_alpha"].inputs["Scale"].default_value = GLINT_STRENGTH * strength
    nt.nodes["fx_glint_light"].inputs["Scale"].default_value = light
    # scroll: uv' = R x (k x uv) + (-f, +g) in the game's v-down space = (-f, -g) in Blender's v-up UV space
    loc = nt.nodes["fx_glint_scroll"].inputs["Location"]
    f0 = int(frame_start)
    span = 2400
    from .shots import fcurves_of

    for f in (f0, f0 + span):
        t = (f - f0) / float(fps) + phase
        loc.default_value = (-t / GLINT_PERIOD_U, -t / GLINT_PERIOD_V, 0.0)
        loc.keyframe_insert("default_value", frame=f)
    path = loc.path_from_id("default_value")
    for fc in fcurves_of(nt):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
            fc.extrapolation = "LINEAR"
            fc.update()
    on = nt.nodes["fx_glint_on"].outputs[0]
    _socket_step(nt, on, f0 - 1, 0.0)
    _socket_step(nt, on, f0, 1.0)
    if frame_end is not None:
        _socket_step(nt, on, int(frame_end), 0.0)
    return mat


_GAME_NOTES = """
Numbers transcribed from the 26.3 client (javap), by class:
  Particle                 lifetime = (int)(4 / (rand * 0.9 + 0.1)) ticks (4..40); start velocity = normalize(arg +
                           (rand * 2 - 1) * 0.4) * (rand + rand + 1) * 0.15 * 0.4, then + 0.1 upward; per tick:
                           vy -= 0.04 * gravity, move with collision (box 0.2), v *= friction 0.98, on the ground
                           vx, vz *= 0.7; a particle whose fall is stopped never moves again.
  SingleQuadParticle       quadSize = 0.1 * (rand * 0.5 + 0.5) * 2 = HALF the side of the quad; the quad is the
                           square (+-1, +-1) rotated by the camera's rotation (LOOKAT_XYZ).
  TerrainParticle          gravity 1, colour 0.6 x texture (x tint), quadSize / 2 (side 0.1..0.2 block), shows a
                           quarter of the block's 'particle' texture at a random offset (mirrored in u).
                           core/particle.fsh + .vsh: texel x colour x light map, in display space.
  ClientLevel              addDestroyBlockEffect: per outline box max(2, ceil(size / 0.25)) particles per axis
                           (full cube 4 x 4 x 4 = 64), velocity argument = position in the box - 0.5.
                           addBreakingParticles: while mining, one per tick 0.1 off the hit face,
                           setPower(0.2).scale(0.6).
  MultiPlayerGameMode      crack stage = (int)(progress * 10); BlockBehaviour.getDestroyProgress = speed / hardness
                           / 30 per tick.
  RenderPipelines.CRUMBLING  blend DST_COLOR, SRC_COLOR (2 x crack x block), discard alpha < 0.1;
                           SheetedDecalTextureGenerator projects the crack by block position per face direction.
  SuspendedTownParticle    happy_villager: velocity x 0.02 (it hovers), quadSize x (rand * 0.6 + 0.5) (side
                           0.1..0.44), lifetime (int)(20 / (rand * 0.8 + 0.2)) = 20..100 ticks, friction 0.99, no
                           gravity, no collision, colour white, sprite particle/glint.
  HeartParticle            angry_villager / heart: starts 0.5 higher (angry), velocity x 0.01 then + 0.1 up,
                           friction 0.86, lifetime 16 ticks, quadSize x 1.5, grows in over half a tick.
  SplashParticle           splash: vx, vz x 0.3, vy = rand * 0.2 + 0.1, minus 0.04 per tick, lifetime
                           (int)(8 / (rand * 0.8 + 0.2)), dies on the ground with probability 1/2 per tick.
  AbstractVillager         addParticlesAroundSelf: 5 particles at x, z +- width, y + 1 + rand * height, velocity
                           argument gaussian * 0.02. Villager.handleEntityEvent: 12 heart, 13 angry_villager,
                           14 happy_villager, 42 splash.
  Villager / behaviours    event 14: AssignProfessionFromJobSite (within 2 blocks of the job block), AcquirePoi for
                           HOME and MEETING_POINT, after a trade. Event 13: Villager.setLastHurtByMob by a player,
                           and VillagerMakeLove.tryToGiveBirth on both villagers when no free bed can be reached.
                           Event 12: VillagerMakeLove (randomly while breeding, and at the birth). Event 42:
                           during a raid. ResetProfession: no event; needs level <= 1 and xp == 0.
  LivingEntity$SwingState  startIfAble: start when no swing runs, or ticks > duration / 2 (or ticks <= 0); a restart
                           with the same hand and animation keeps `animation`. tick: animation = min(ticks /
                           duration, 1), ticks++, over once ticks passed the duration. getAnimation(partial) =
                           lerp(partial, oldAnimation, animation), + 1 on the new value when it wrapped.
                           SwingAnimation.DEFAULT = (WHACK, 6 ticks). Minecraft.continueAttack: player.swing() on
                           every tick while continueDestroyBlock is true (before the entities tick).
  HumanoidModel            setupAttackAnimation (WHACK), t = the swing animation: body.yRot = sin(sqrt(t) * 2 pi) *
                           0.2; both arms turn and their shoulders move with it, leftArm.xRot += body.yRot;
                           swinging arm: xRot -= sin(outQuart(t) * pi) * 1.2 + sin(t * pi) * -(head.xRot - 0.7) *
                           0.75, yRot += body.yRot * 2, zRot += sin(t * pi) * -0.4.
  ToolMaterial             speed: WOOD 2, STONE 4, COPPER 5, IRON 6, DIAMOND 8, NETHERITE 9, GOLD 12 (lectern: block
                           tag mineable/axe).
  CrossedArmsItemLayer     translateToArms, rotate X 0.75, scale 1.07, translate (0, 0.13, -0.34), rotate X pi;
                           item drawn with ItemDisplayContext.GROUND.
  TextureTransform         glint: translation(-f, g) x rotateZ(10 deg) x scale(8); f = t / 27.5 s, g = t / 7.5 s
                           at glint speed 0.5. core/item.fsh: rgb += (GlintAlpha x glint)^2, GlintAlpha 0.75.
"""


# ----------------------------------------------------------------------------------------------------
# self-test: numeric checks and the proof stills (shot in the real trading hall with the look applied)
# ----------------------------------------------------------------------------------------------------
PROOF = {            # still name -> frame of the proof film
    "librarian": 12, "crack_2": 30, "crack_5": 37, "crack_9": 47, "break_0": 48, "break_3": 51, "break_8": 56,
    "unemployed": 80, "happy_1": 110, "happy_2": 130, "book_1": 150, "book_2": 174, "steve": 230,
    "steve_rest": 256, "kinds": 275, "cut": 309,
}


def build_proof(scene, cells=(2, 3)):
    """The proof film: the trade-reroll loop once, in the real trading hall (also the worked example for a film).
    It is written the way a film is, shot by shot: every burst is emitted before the later shots exist.
    Returns dict(film, stage, village, block, librarian, steve, book, bursts, shots, swings)."""
    from films import lookdev

    from . import look, shots, village

    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0, key_strength=1.0,
                        ambient_strength=1.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=FPS)
    st = lookdev.Stage(scene, film, v, sky)
    A = v.anchors
    lec = hall_job_block(v, 1)
    spot = A["cell_1"]
    yaw = v.yaws["cell_1"]
    lib = st.cast["lib"] = make_job_villager("lib", ("librarian", "none"))
    steve = st.actor("steve", "steve")
    others = [st.actor("cell%d" % i, v.cell_professions[i - 1]) for i in cells]
    bursts = {}

    def neighbours(f):
        """The villagers of the next cells, standing in their places from frame f."""
        for i, c in zip(cells, others):
            c.place(f, A["cell_%d" % i], v.yaws["cell_%d" % i])

    # ---- shot 1: the cell, seen from the aisle: break, plain villager, place, librarian again ----------
    s = st.shot("cell", 6.0)
    f0, f1 = s.frame_start, s.frame_end
    cam = (spot[0] + 0.78, spot[1] + 3.62, 1.56)
    s.lens(35, 3.4)
    s.move(cam, (spot[0] + 0.03, spot[1] + 0.50, 0.97), (cam[0] - 0.10, cam[1], cam[2]))
    lib.place(f0, spot, yaw)
    lib.look_at(f0, cam, ease=0)
    lib.idle(f0, f1 + 1, seed=6)                              # a seed that never turns his dark west cheek to the lens
    neighbours(f0)
    st.use(s, lib, *others)
    aisle = (spot[0], spot[1] + 2.3, 0.0)
    bursts["break"] = break_block(lec, 24, 48, camera=s, hit_from=aisle, seed=1)
    lib.lose_profession(54)                                   # five ticks later he is a plain villager: no particles
    place_block(lec, 96)
    bursts["happy"] = lib.gain_profession(108, "librarian", camera=s, seed=PROOF_SEED)
    s.focus(lib.head)
    s.handheld(0.004, seed=5)
    st.hero(s, "librarian", *lib.heads)                      # every outfit's head: he is plain for a while
    st.lights(s, scale=0.0, groups={"hall": 0.8}, inside="hall")

    # ---- shot 2: the enchanted book, close ------------------------------------------------------------
    sb = st.shot("book", 2.0)
    h0, h1 = sb.frame_start, sb.frame_end
    mid = (spot[0], spot[1] - 0.22, spot[2])                  # the middle of his cell, where the game keeps him:
    lib.place(h0, mid, yaw)                                   # the book then clears the lectern's high edge
    book = hold_out(lib, "enchanted_book", h0, h1 + 1, enchanted=True)
    stop_particles(h0)                                        # later in the story: no green sprites left over
    bpos = (mid[0], mid[1] + 0.40, 1.225)
    camb = (mid[0] + 0.45, mid[1] + 3.25, 1.95)             # far enough for book AND face to fit y 14-60 %
    lib.look_at(h0, camb, ease=0)
    lib.idle(h0, h1 + 1, seed=9)
    neighbours(h0)
    st.use(sb, lib, *others)
    sb.lens(45, 3.4)
    sb.move(camb, (bpos[0], bpos[1], 1.12), (camb[0] - 0.06, camb[1], camb[2]))
    sb.focus(book)
    sb.handheld(0.003, seed=6)
    st.hero(sb, "book", book)
    st.hero(sb, "librarian", lib)
    st.lights(sb, scale=0.0, groups={"hall": 0.8}, inside="hall")

    # ---- shot 3: Steve in the aisle, mining the lectern -------------------------------------------------
    s2 = st.shot("steve", 3.0)
    g0, g1 = s2.frame_start, s2.frame_end
    stand = (spot[0] + 0.72, spot[1] + 2.25, 0.0)
    cam2 = (spot[0] + 0.05, spot[1] + 3.95, 1.60)             # in front of the cell: Steve stands east of the line
    steve.place(g0, stand, lookdev.yaw_to(stand, lec.center))
    steve.look_at(g0, (lec.center.x, lec.center.y, lec.top - 0.2), ease=0)
    swings = {"mining": mining_swings(steve, g0 + 4, g0 + 52)}     # after place() and look_at(): it reads the pose
    bursts["break2"] = break_block(lec, g0 + 4, g0 + 52, camera=s2, hit_from=steve, seed=2)
    lib.place(g0, spot, yaw)
    lib.look_at(g0, cam2, ease=0)                             # his lit side to the lens (key: the east pier lantern)
    neighbours(g0)
    st.use(s2, lib, steve, *others)
    s2.lens(24, 3.4)
    s2.move(cam2, (spot[0] + 0.45, spot[1] + 0.80, 1.10), (cam2[0] + 0.06, cam2[1], cam2[2]))
    s2.focus(lec.object)
    s2.handheld(0.004, seed=7)
    st.hero(s2, "steve", steve)
    st.lights(s2, scale=0.0, groups={"hall": 0.8}, inside="hall")

    # ---- shot 4: the other entity-event particles (angry, heart, splash), along the cells ---------------
    s3 = st.shot("kinds", 1.5)
    k0, k1 = s3.frame_start, s3.frame_end
    place_block(lec, k0)
    lib.place(k0, spot, yaw)
    neighbours(k0)
    cam3 = (spot[0] + 5.30, spot[1] + 3.10, 1.66)
    s3.lens(26, 3.4)
    s3.move(cam3, (spot[0] + 2.35, spot[1] + 0.30, 1.50))
    for c in [lib] + others:
        c.look_at(k0, cam3, ease=0)
    st.use(s3, lib, *others)
    bursts["angry"] = emit("angry_villager", lib, k0 + 2, camera=s3, seed=1, village=v, in_air=True)
    if others:
        bursts["heart"] = emit("heart", others[0], k0 + 2, camera=s3, seed=2, village=v, in_air=True)
    if len(others) > 1:
        bursts["splash"] = emit("splash", others[1], k0 + 2, camera=s3, seed=3, village=v, in_air=True, count=10)
    s3.focus(others[0].head if others else lib.head)
    st.lights(s3, scale=0.0, groups={"hall": 0.8}, inside="hall")
    # green sprites that are still in the air at the next cut, emitted while the next shot does not exist yet
    bursts["cross"] = emit("happy_villager", lib, k1 - 9, camera=s3, seed=4, village=v, in_air=True, count=8)

    # ---- shot 5: a cut to quite another angle while those sprites live; Steve places with one swing ------
    s4 = st.shot("cut", 1.5)
    c0, c1 = s4.frame_start, s4.frame_end
    steve.place(c0, stand, lookdev.yaw_to(stand, lec.center))
    steve.look_at(c0, (lec.center.x, lec.center.y, lec.top - 0.2), ease=0)
    swings["place"] = arm_swings(steve, [c0 + 6, c0 + 8, c0 + 11])   # the 2nd is ignored, the 3rd restarts it
    lib.place(c0, spot, yaw)
    lib.look_at(c0, cam2, ease=0)
    neighbours(c0)
    st.use(s4, lib, steve, *others)
    s4.lens(24, 3.4)
    s4.move(cam2, (spot[0] + 0.45, spot[1] + 0.80, 1.10), (cam2[0] + 0.06, cam2[1], cam2[2]))
    s4.focus(lec.object)
    st.hero(s4, "librarian", lib)
    st.lights(s4, scale=0.0, groups={"hall": 0.8}, inside="hall")
    st.finish()
    return dict(film=film, stage=st, village=v, block=lec, librarian=lib, steve=steve, book=book, bursts=bursts,
                shots=(s, sb, s2, s3, s4), swings=swings)


PROOF_SEED = 9         # of the 5 green particles, 4 start in the open part of the 1x1 cell with this seed


def _curve(idb, path, index=0):
    from .shots import fcurves_of

    for fc in fcurves_of(idb):
        if fc.data_path == path and fc.array_index == index:
            return fc
    return None


def _check(proof):
    """Numeric checks of what build_proof keyed (no rendering). Returns the number of failures."""
    bad = []

    def ok(label, cond, detail=""):
        """Print one check and remember a failure."""
        print("%-4s %s %s" % ("OK" if cond else "FAIL", label, detail))
        if not cond:
            bad.append(label)

    v, lec, lib, book = proof["village"], proof["block"], proof["librarian"], proof["book"]
    film, scene = proof["film"], proof["film"].scene
    # 1. extraction
    stt = lec.stats
    ok("lectern extracted", lec.block_id == "lectern" and stt["faces"] > 0, str(stt))
    zs = [vv.co.z for vv in lec.object.data.vertices]
    ok("lectern pokes above its unit cube (slanted top)", max(zs) > 1.0, "max z %.4f" % max(zs))
    ok("floor under the lectern was culled and is patched", stt["patch_faces"] >= 1 and len(lec.patches) == 1,
       "patch faces %d" % stt["patch_faces"])
    ok("extract_block twice returns the same Block", extract_block(v, lec.cell) is lec)
    full = block_shape("stone_bricks")
    n_full = sum(max(2, math.ceil(min(1.0, (b[3] - b[0]) / 16) / 0.25)) ** 3 for b in full)
    ok("full cube gives 64 break particles", n_full == 64)
    n_break = sum(1 for p in proof["bursts"]["break"].particles if p["spawn"] == 48.0 and p["first"] == 48)
    shape = block_shape("lectern", lec.props)
    want = 0
    for b in shape:
        want += int(np.prod([max(2, math.ceil(min(1.0, (b[3 + i] - b[i]) / 16.0) / 0.25 - 1e-9)) for i in range(3)]))
    print("     lectern outline boxes (px):", [tuple(round(c, 2) for c in b) for b in shape])
    ok("lectern break particles = game count", n_break == want, "%d particles from %d boxes" % (n_break, len(shape)))
    # 2. crack stages and visibility
    stages = {f: lec.stage_at(f) for f in (23, 24, 30, 37, 47, 48, 60)}
    ok("crack stages keyed", stages == {23: -1, 24: 0, 30: 2, 37: 5, 47: 9, 48: -1, 60: -1}, str(stages))
    hide = _curve(lec.object, "hide_render")
    vis = {f: hide.evaluate(f) < 0.5 for f in (47, 48, 95, 96)}
    ok("block gone on frame_end, back on place frame", vis == {47: True, 48: False, 95: False, 96: True}, str(vis))
    ph = _curve(lec.patches[0], "hide_render")
    ok("patch visible exactly while the block is gone",
       [ph.evaluate(f) < 0.5 for f in (47, 48, 95, 96)] == [False, True, True, False])
    # 3. particles
    b = proof["bursts"]["break"]
    main = [p for p in b.particles if p["spawn"] == 48.0]
    lifes = [p["lifetime"] for p in main]
    sizes = [p["size"] for p in main]
    ok("terrain lifetime 4..40 ticks", min(lifes) >= 4 and max(lifes) <= 40, "min %d max %d" % (min(lifes), max(lifes)))
    ok("terrain half-size 0.05..0.1", min(sizes) >= 0.05 and max(sizes) <= 0.1, "%.3f..%.3f" % (min(sizes), max(sizes)))
    lowest = min(pt[2] for p in main for pt in p["pos"])
    ok("no particle falls through the hall floor", lowest >= -1e-6, "lowest z %.4f" % lowest)
    landed = sum(1 for p in main if p["lifetime"] >= 12 and abs(p["pos"][-1][2]) < 0.01 or
                 (p["lifetime"] >= 12 and p["pos"][-1] == p["pos"][-2]))
    ok("long-lived particles come to rest", landed >= 1, "%d resting" % landed)
    p0 = main[0]
    ob = p0["object"]
    fx_, fy_, fz_ = (_curve(ob, "location", i) for i in range(3))
    at = lambda f: (fx_.evaluate(f), fy_.evaluate(f), fz_.evaluate(f))       # noqa: E731
    d0 = max(abs(a - c) for a, c in zip(at(48.0), p0["pos"][0]))
    d1 = max(abs(a - c) for a, c in zip(at(48.0 + TICK), p0["pos"][0]))
    d2 = max(abs(a - c) for a, c in zip(at(48.0 + 2 * TICK), p0["pos"][1]))
    ok("particle keys: still for one tick, then tick positions every 1.2 frames", max(d0, d1, d2) < 1e-4)
    hk = _curve(ob, "hide_render")
    ok("particle visible from the break frame, hidden before and after",
       hk.evaluate(47) > 0.5 and hk.evaluate(48) < 0.5 and hk.evaluate(p0["last"]) > 0.5
       and hk.evaluate(p0["last"] - 1) < 0.5)
    v0 = [np.linalg.norm(np.subtract(p["pos"][1], p["pos"][0])) for p in main]
    ok("first-tick travel within the game's range (<= 0.18 + 0.1 up)", max(v0) <= 0.30, "max %.3f" % max(v0))
    hits = [p for p in b.particles if p["spawn"] != 48.0 or p["first"] != 48]
    ok("one mining crumb per tick while breaking", len(hits) == 20, "%d crumbs over 24 frames" % len(hits))
    h = proof["bursts"]["happy"]
    feet = lib.pos_at(108)
    inside = all(abs(p["pos"][0][0] - feet.x) <= 0.6 + 1e-6 and abs(p["pos"][0][1] - feet.y) <= 0.6 + 1e-6
                 and 1.0 - 1e-6 <= p["pos"][0][2] - feet.z <= 2.95 + 1e-6 for p in h.particles)
    ok("happy_villager: 5 particles inside the game's box around the villager", len(h.particles) == 5 and inside)
    hl = [p["lifetime"] for p in h.particles]
    hs = [p["size"] for p in h.particles]
    drift = max(np.linalg.norm(np.subtract(p["pos"][-1], p["pos"][0])) for p in h.particles)
    ok("happy_villager: lifetime 20..100 ticks, half-size 0.05..0.22, hovering",
       min(hl) >= 20 and max(hl) <= 100 and min(hs) >= 0.05 and max(hs) <= 0.22 and drift < 0.6,
       "life %s size %s drift %.2f" % (hl, [round(x, 3) for x in hs], drift))
    cons = h.objects[0].constraints
    proxy = camera_proxy(film)
    ok("particles copy the rotation of the film's camera proxy (one constraint each)",
       len(cons) == 1 and cons[0].type == "COPY_ROTATION" and cons[0].target is proxy)
    ok("the proxy is bound to every shot of the finished film, although the bursts were emitted shot by shot",
       [c.target for c in proxy.constraints] == [sh.camera for sh in proof["shots"]]
       and film.__dict__.get("_fx_hooked") is True, "%d shots" % len(proxy.constraints))

    def apart(a, b_):
        """Degrees between the world rotations of two objects (0..180)."""
        deg = math.degrees(a.matrix_world.to_quaternion().rotation_difference(b_.matrix_world.to_quaternion()).angle)
        return min(deg, 360.0 - deg)

    def off(ob, frame, sub=0.0):
        """Degrees between a quad's world rotation and that of the camera filming `frame` (evaluated)."""
        cam = film.camera_at(frame)
        scene.camera = cam
        scene.frame_set(int(frame), subframe=sub)
        bpy.context.view_layer.update()
        return apart(ob, cam)

    s3_, s4_ = proof["shots"][3], proof["shots"][4]
    cross = proof["bursts"]["cross"]
    live = [p for p in cross.particles if p["last"] > s4_.frame_start + 6]
    scene.frame_set(s4_.frame_start)
    bpy.context.view_layer.update()
    turn = apart(s3_.camera, s4_.camera)
    errs = [max(off(p["object"], f, sub) for f, sub in ((s3_.frame_end - 4, 0.0), (s3_.frame_end, 0.0),
                                                        (s3_.frame_end, 0.5), (s4_.frame_start, 0.0),
                                                        (s4_.frame_start + 5, 0.25))) for p in live]
    ok("sprites emitted in one shot face the NEXT shot's camera after the cut (emitted before that shot existed)",
       len(live) >= 4 and max(errs) < 0.05 and turn > 30.0,
       "%d live across the cut, worst %.4f deg, the cameras differ by %.0f deg" % (len(live), max(errs or [0]), turn))
    b2 = proof["bursts"]["break2"]
    over = [p for p in b2.particles if p["last"] > s3_.frame_start + 1]
    if over:
        worst = max(max(off(p["object"], s3_.frame_start - 1), off(p["object"], s3_.frame_start)) for p in over[:12])
        ok("crumbs of a break still lying there after a cut face the new camera", worst < 0.05,
           "%d crumbs outlive the cut, worst %.4f deg" % (len(over), worst))
    direct = emit("heart", (62.0, 60.0, 0.0), 20, camera=proof["shots"][0].camera, seed=2)
    ok("a bare camera object is followed as it is (no film behind it)",
       direct.objects[0].constraints[0].target is proof["shots"][0].camera)
    crumb = main[0]["object"].data.materials[0]
    mult = [n.inputs[7].default_value[0] for n in crumb.node_tree.nodes if n.type == "MIX"]
    ok("crumbs are 0.6 x the block texture in DISPLAY space (TerrainParticle colour)",
       len(mult) == 1 and abs(mult[0] ** (1.0 / 2.2) - 0.6) < 1e-4, "linear factor %.4f" % (mult[0] if mult else -1))
    # 4. profession
    def worn(f):
        """Professions whose outfit is rendered at frame f."""
        out = []
        for prof, obs in lib.outfits.items():
            c = _curve(obs[0], "hide_render")
            if c.evaluate(f) < 0.5:
                out.append(prof)
        return out

    ok("outfits: librarian, none from 54, librarian from 108",
       worn(53) == ["librarian"] and worn(54) == ["none"] and worn(107) == ["none"] and worn(108) == ["librarian"],
       "%s %s %s %s" % (worn(53), worn(54), worn(107), worn(108)))
    film.goto(60)
    bpy.context.view_layer.update()
    twin = lib.outfits["none"][[o.name.endswith("_head") for o in lib.outfits["none"]].index(True)]
    dm = max(abs(a - c) for ra, rc in zip(twin.matrix_world, lib.head.matrix_world) for a, c in zip(ra, rc))
    ok("twin head shares the rig head's transform (idle + look_at)", dm < 1e-6, "max diff %.2e" % dm)
    ok("all parts of every outfit are in objects()", all(o in lib.objects() for obs in lib.outfits.values() for o in obs))
    # 5. held item: Character.hold against the layer class
    probe = characters.make_villager("fx_probe", "librarian")
    probe.place(1, (40.0, 40.0, 0.0), 0.0)
    item = props.make_item("emerald", _collection())
    probe.hold(item)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    mw = item.matrix_world
    c = mw.translation
    # independent hand calculation of the layer chain for an upright villager (see crossed_arms_matrix)
    exp_h = (24.0 - (3.0 + 16.0 * (0.13 - 0.125) * 1.07)) / 16.0 * 0.9375
    exp_f = (1.0 + 16.0 * 0.34 * 1.07) / 16.0 * 0.9375
    exp_s = 0.5 * 1.07 * 0.9375
    ok("Character.hold = CrossedArmsItemLayer: height above feet", abs(c.z - exp_h) < 1e-4, "%.4f vs %.4f" % (c.z, exp_h))
    ok("Character.hold = CrossedArmsItemLayer: in front of the body", abs((40.0 - c.y) - exp_f) < 1e-4,
       "%.4f vs %.4f" % (40.0 - c.y, exp_f))
    ok("Character.hold = CrossedArmsItemLayer: scale and upright", abs(mw.to_scale().x - exp_s) < 1e-4
       and abs((mw.to_3x3() @ Vector((0, 0, 1))).normalized().z - 1.0) < 1e-5
       and (mw.to_3x3() @ Vector((0, -1, 0))).normalized().y < -0.999,
       "scale %.4f, sprite front faces the customer" % mw.to_scale().x)
    dm = max(abs(a - b_) for ra, rb in zip(crossed_arms_matrix(), characters._held_matrix("arms", 0.9375))
             for a, b_ in zip(ra, rb))
    ok("fx.crossed_arms_matrix equals characters._held_matrix('arms')", dm < 1e-9)
    probe.show(1, False)
    pt = held_item_point(lib, 150)
    print("     book centre at frame 150: (%.3f, %.3f, %.3f); lectern top %.3f, cell %s" % (pt.x, pt.y, pt.z, lec.top, (lec.cell,)))
    bh = _curve(book, "hide_render")
    ok("book shown in its shot only", bh.evaluate(144) > 0.5 and bh.evaluate(145) < 0.5 and bh.evaluate(193) > 0.5)
    # 6. glint
    nt = book.data.materials[0].node_tree
    loc = nt.nodes["fx_glint_scroll"].inputs["Location"]
    path = loc.path_from_id("default_value")
    cu, cv = _curve(nt, path, 0), _curve(nt, path, 1)
    du = cu.evaluate(150 + 24) - cu.evaluate(150)
    dv = cv.evaluate(150 + 24) - cv.evaluate(150)
    ok("glint scroll: 1/27.5 and 1/7.5 texture per second", abs(du + 1 / 27.5) < 1e-5 and abs(dv + 1 / 7.5) < 1e-5,
       "du %.5f dv %.5f per second" % (du, dv))
    sc = nt.nodes["fx_glint_scroll"].inputs["Scale"].default_value[0]
    ok("glint scale: a quarter of the texture per item width", abs(sc - 0.25) < 1e-9)
    on = _curve(nt, nt.nodes["fx_glint_on"].outputs[0].path_from_id("default_value"))
    ok("glint on from the first frame of the book shot", on.evaluate(144) < 0.5 and on.evaluate(145) > 0.5)
    gm, gn = book.data.materials[0], len(nt.nodes)
    ok("glint() again on the same item reuses its material and adds no nodes",
       glint(book, 145, 193) is gm and book.data.materials[0] is gm and len(gm.node_tree.nodes) == gn
       and on.evaluate(144) < 0.5 and on.evaluate(145) > 0.5 and on.evaluate(193) < 0.5)
    # 6b. second break / place cycle, a full cube, a burst across a cut, the game's mining time
    g0 = proof["shots"][2].frame_start
    k0 = proof["shots"][3].frame_start
    ok("second cycle: cracked at 230, gone at %d, back at %d" % (g0 + 52, k0),
       lec.stage_at(230) == 6 and hide.evaluate(g0 + 51) < 0.5 and hide.evaluate(g0 + 52) > 0.5
       and hide.evaluate(k0 - 1) > 0.5 and hide.evaluate(k0) < 0.5 and lec.stage_at(k0) == -1,
       "stage %d" % lec.stage_at(230))
    ok("break_frames: lectern by hand 90 frames, diamond axe 12", break_frames("lectern", "hand") == 90
       and break_frames("lectern", "diamond_axe") == 12)
    pier = extract_block(v, (lec.cell[0] + 1, lec.cell[1], lec.cell[2]))
    ok("a full cube can be extracted too (stone-brick pier beside the lectern)",
       pier.block_id == "stone_bricks" and pier.stats["faces"] >= 2 and pier.stats["patch_faces"] >= 1
       and len(pier.shape) == 1, str(pier.stats))
    far = emit("heart", (60.0, 60.0, 0.0), 140, camera=film, seed=1)
    cut2 = proof["shots"][1].frame_start
    worst = max(max(off(o, cut2 - 1), off(o, cut2 - 1, 0.5), off(o, cut2)) for o in far.objects)
    ok("camera=Film: a burst that crosses a cut turns to the next shot's camera on the cut", worst < 0.05,
       "worst %.4f deg" % worst)
    n_live = sum(1 for p_ in far.particles if p_["first"] < 150 < p_["last"])
    ended = far.stop(150)
    hk = [_curve(p_["object"], "hide_render") for p_ in far.particles]
    ok("Burst.stop(frame): visible until the frame before, gone from it on",
       ended == n_live > 0 and all(c.evaluate(149) < 0.5 and c.evaluate(150) > 0.5 and c.evaluate(170) > 0.5 for c in hk)
       and far.frame_end == 149, "%d ended, frame_end %s" % (ended, far.frame_end))
    late = emit("heart", (60.0, 62.0, 0.0), 160, camera=film, seed=3)
    n_all = stop_particles(156, bursts=[far, late])
    ok("stop_particles: a burst that starts after the stop never shows",
       n_all == len(late.particles) and all(_curve(o, "hide_render").evaluate(f) > 0.5 for o in late.objects
                                            for f in (159, 160, 165)))
    # 6c. the player's arm: the game's swing state machine, absolute keys, back to rest
    st1, sh1, end1 = _swing_run([0])
    ok("one swing: starts on its tick, shown for 6 ticks after one tick of lag, over at tick 8",
       st1 == [0] and end1 == 8 and sh1[0] == (0.0, 0.0) and abs(sh1[1][1] - 1 / 6) < 1e-9 and sh1[6][1] == 1.0)
    st2, sh2, _e = _swing_run(range(41))
    ok("mining (a request every tick): a swing starts every 4 ticks and wraps from 0.5 to 1 in the fourth",
       st2 == list(range(0, 41, 4)) and sh2[4] == (0.5, 1.0) and sh2[5][0] == 0.0, "starts %s" % st2[:4])
    steve = proof["steve"]
    m0 = g0 + 4
    chans = [(steve.arm_r, 0), (steve.arm_r, 1), (steve.arm_r, 2), (steve.arm_l, 0), (steve.body, 2), (steve.head, 2)]
    val = characters._val
    rest = [val(ob, "rotation_euler", i, m0) for ob, i in chans]
    after = [[val(ob, "rotation_euler", i, f) for ob, i in chans] for f in (g0 + 52 + 9, g0 + 64, k0 - 1)]
    drift = max(abs(a - r) for row in after for a, r in zip(row, rest))
    ok("mining_swings: arm, body and head are back in their start pose 9 frames after the break and stay there",
       drift < 1e-6, "largest difference %.2e rad" % drift)
    xs = [val(steve.arm_r, "rotation_euler", 0, m0 + f / 10.0) for f in range(0, 600)]
    tw = [val(steve.body, "rotation_euler", 2, m0 + f / 10.0) - rest[4] for f in range(0, 600)]
    ok("mining_swings: the arm swings 65-90 degrees up and never to the clamp; the body turns +-0.2 rad at most",
       -1.6 < min(xs) < -1.15 and max(xs) <= rest[0] + 1e-6 and max(abs(t_) for t_ in tw) <= 0.2 + 1e-6,
       "arm x %.3f..%.3f, twist +-%.3f" % (min(xs), max(xs), max(abs(t_) for t_ in tw)))
    sw = proof["swings"]["mining"]
    gaps = {round(b_ - a_, 6) for a_, b_ in zip(sw, sw[1:])}
    ok("mining_swings: one swing every 4 ticks = 4.8 frames, the first on frame_start", gaps == {4.8} and sw[0] == m0
       and len(sw) == 11, "%d swings, gaps %s" % (len(sw), sorted(gaps)))
    c0 = proof["shots"][4].frame_start
    pl = proof["swings"]["place"]
    ok("arm_swings: a request inside the first half of a swing is ignored, one after it restarts the swing",
       len(pl) == 2 and abs(pl[0] - (c0 + 6)) < 1e-6 and abs(pl[1] - (c0 + 6 + 4 * TICK)) < 1e-6, str(pl))
    late_pose = [val(ob, "rotation_euler", i, c0 + 6 + 4 * TICK + 9) for ob, i in chans]
    base_pose = [val(ob, "rotation_euler", i, c0 + 5) for ob, i in chans]
    ok("arm_swings: back in the start pose 9 frames after the last swing started",
       max(abs(a - r) for a, r in zip(late_pose, base_pose)) < 1e-6)
    p2 = characters.make_player("fx_probe_player")
    p2.place(1, (44.0, 40.0, 0.0), 0.0)
    r0 = [val(ob, "rotation_euler", i, 99) for ob, i in ((p2.arm_r, 0), (p2.arm_r, 1), (p2.arm_r, 2), (p2.body, 2))]
    a1 = arm_swings(p2, [100])
    a2 = arm_swings(p2, [106])                                # a second CALL while the first swing still runs
    a3 = mining_swings(p2, 112, 160)
    r1 = [val(ob, "rotation_euler", i, 175) for ob, i in ((p2.arm_r, 0), (p2.arm_r, 1), (p2.arm_r, 2), (p2.body, 2))]
    lo = min(val(p2.arm_r, "rotation_euler", 0, 100 + f / 10.0) for f in range(0, 760))
    ok("overlapping calls (swing, swing, then mining) leave no residue: the old additive swings ended on the clamp",
       a1 == [100.0] and [round(x_, 6) for x_ in a2] == [100.0, 106.0] and max(abs(a - r) for a, r in zip(r1, r0)) < 1e-6 and lo > -1.6,
       "starts %s then %d mining swings, lowest arm x %.3f" % (a2, len(a3), lo))
    p2.show(1, False)
    spl = proof["bursts"].get("splash")
    if spl is not None:
        sl = [p["lifetime"] for p in spl.particles]
        done = [p["pos"][-1][2] < max(q[2] for q in p["pos"]) or p["pos"][-1] == p["pos"][-2] for p in spl.particles]
        ok("splash: at most 40 ticks; every drop falls back or sticks where a block stopped it (Particle.move)",
           max(sl) <= 40 and all(done), "ticks %s" % sl)
    ang = proof["bursts"].get("angry")
    if ang is not None:
        rise = [p["pos"][-1][2] - p["pos"][0][2] for p in ang.particles]
        ok("angry_villager: 16 ticks, rises about 0.65 block and slows down",
           all(p["lifetime"] == 16 for p in ang.particles) and 0.55 < min(rise) and max(rise) < 0.75,
           "rise %.2f..%.2f" % (min(rise), max(rise)))
    # 7. the frame fingerprint (engine.stamp) sees the animated materials
    from . import stamp

    fp = stamp.Fingerprinter(scene, film)
    a, b2, c2 = fp.frame(30)["parts"]["o"], fp.frame(37)["parts"]["o"], fp.frame(31)["parts"]["o"]
    ok("stamp: another crack stage is another fingerprint", a != b2)
    g1, g2 = fp.frame(160)["parts"]["o"], fp.frame(161)["parts"]["o"]
    ok("stamp: the scrolling glint changes the fingerprint every frame", g1 != g2)
    print("[fx] numeric checks: %d failed%s" % (len(bad), ": " + ", ".join(bad) if bad else ""))
    return len(bad)


def _selftest(argv):
    """`$BPY -m engine.fx` = numeric checks; `$BPY -m engine.fx stills [names]` renders proof stills (a few per
    call: each takes 20-40 s); `$BPY -m engine.fx seq A B [STEP]` renders frames A..B of the proof film as
    out/test/fx_seq_<frame>.png; `--res WxH --samples N` override the 540x960 / 16 samples. `stills ... --palette`
    also measures each still with tools.palette_check; `$BPY -m engine.fx palette [names]` measures the stills
    that are on disk without rendering."""
    import os
    import time

    from . import look

    skip = {i + 1 for i, a in enumerate(argv) if a in ("--res", "--samples")}
    modes = ("check", "stills", "seq", "palette")
    names = [a for i, a in enumerate(argv) if not a.startswith("--") and a not in modes and i not in skip]
    res, samples = (540, 960), 16
    if "--res" in argv:
        w_, h_ = argv[argv.index("--res") + 1].lower().split("x")
        res = (int(w_), int(h_))
    if "--samples" in argv:
        samples = int(argv[argv.index("--samples") + 1])
    t = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=res, samples=min(samples, 16), threads=2)
    proof = build_proof(scene)
    scene.cycles.adaptive_min_samples = max(4, scene.cycles.samples // 3)
    print("[fx] proof film built in %.1f s: frames %d-%d" % (time.time() - t, proof["film"].frame_start,
                                                             proof["film"].frame_end))
    failed = 0
    if not any(m in argv for m in ("stills", "seq", "palette")) or "check" in argv:
        failed = _check(proof)
    if any(m in argv for m in ("stills", "seq", "palette")):
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "test")
        os.makedirs(out, exist_ok=True)
        todo = [(n, PROOF[n]) for n in (names or list(PROOF))] if "seq" not in argv else []
        if "seq" in argv:                                    # seq A B [STEP]: frames A..B as fx_seq_<frame>.png
            a, b_ = int(names[0]), int(names[1])
            todo = [("seq_%03d" % f, f) for f in range(a, b_ + 1, int(names[2]) if len(names) > 2 else 1)]
        off_model = []
        for name, frame in todo:
            t = time.time()
            proof["film"].goto(frame)
            path = os.path.join(out, "fx_%s.png" % name)
            if "palette" not in argv:
                scene.render.filepath = path
                bpy.ops.render.render(write_still=True)
                print("[fx] %-10s frame %3d -> %s  %.1f s" % (name, frame, path, time.time() - t), flush=True)
            if ("palette" in argv or "--palette" in argv) and os.path.exists(path):
                # the still against the game textures it was made from, its heroes against the Reels safe area
                from tools import palette_check

                shot = proof["film"].shot_at(frame)
                rec = palette_check.probe(scene)
                report = palette_check.evaluate(rec, path, heroes=proof["stage"].heroes.get(shot.name, ()))
                if palette_check.print_report("fx_" + name, report):
                    off_model.append(name)
        if "palette" in argv or "--palette" in argv:
            print("[fx] palette / composition checks: %s" % ("all passed" if not off_model
                                                             else "FAILED in " + ", ".join(off_model)))
            failed += len(off_model)
    return failed


if __name__ == "__main__":
    import sys

    sys.exit(1 if _selftest(sys.argv[1:]) else 0)
