"""Box-rig characters (villagers and the player) animated with plain object keyframes. Role CAST.

Everything here is original procedural pixel art: each character gets its own small texture sheet painted
with numpy and every box face is UV-mapped to its own region of that sheet (Closest filtering).

Rig (no armature, only parented objects with pivots at the joints):

    root (Empty, feet)            location = position, rotation_euler.z = yaw (0 faces -Y)
      hips (Empty, hip joint)     walk bob, weight shift, lying pose
        leg_l, leg_r (mesh)       rotation_euler.x swings the leg (negative = forward)
        body (mesh)               rotation_euler.x = lean (positive = forward), .y = sway, .z = twist
          head (mesh, neck)       rotation_euler.z = yaw, .x = pitch (negative = look up)
            lids (mesh)           eyelids; scale.z 1 = closed, ~0 = open
          arms (villager)         one folded-arm bar, rest rotation_euler.x = -43 deg
          arm_l, arm_r (player)   rotation_euler.x swings the arm (negative = forward / up)

Animation model: every helper writes ONE "segment" per channel: a run of eased keys that ends in a
CONSTANT key, so a finished move holds its last value and never drifts into whatever is keyed later.
Starting a new move while an older one is still running throws the rest of the older one away, so
"stroll, then get interrupted" just works. Call the helpers in increasing frame order per character.

Hard cuts (place, lie_down, a walk that starts somewhere else, look_at(..., ease=0)) are keyed half a
frame early, so a frame rendered with motion blur never smears across a cut.

    v = make_villager("ada", "farmer")
    v.place(1, (3, 4, 0), yaw=0.0)                 # shot cut: stand here, neutral pose
    v.idle(1, 60, seed=2)                          # alive while waiting
    end = v.walk(60, path, run=True, from_current=True)   # panic: drops the rest of the idle
    v.look_at(end, bell_point)
"""
import math
import sys
import zlib

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import pix

FPS = 24
WALK_SPEED = 1.6          # units / second, the contract default for walk()
RUN_SPEED = 4.4           # used by walk(run=True) when speed is left at its default
PROFESSIONS = ("farmer", "librarian", "smith", "cleric", "shepherd", "plain", "nitwit")
VILLAGER_HEIGHT = 1.95
PLAYER_HEIGHT = 1.90
HEAD_YAW_MAX = math.radians(70)
HEAD_PITCH_MAX = math.radians(35)
ARMS_FOLD = math.radians(-43)
LID_OPEN, LID_CLOSED = 0.001, 1.0
CUT_LEAD = 0.5            # hard cuts are keyed this many frames early so motion blur never spans them

_LOC, _ROT, _SCL = "location", "rotation_euler", "scale"


# ----------------------------------------------------------------------------------------------------
# small maths helpers
# ----------------------------------------------------------------------------------------------------
def _vec3(p, z=0.0):
    p = tuple(p)
    return Vector((float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else float(z)))


def _wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _seed(*parts):
    return zlib.crc32("|".join(str(p) for p in parts).encode()) & 0x7FFFFFFF


# ----------------------------------------------------------------------------------------------------
# pixel painting helpers (float RGBA canvases, row 0 = top)
# ----------------------------------------------------------------------------------------------------
def _c(hex_str):
    return np.array(pix.rgba(hex_str), dtype=np.float32)


def _mul(col, f):
    out = np.array(col, dtype=np.float32).copy()
    out[:3] = np.clip(out[:3] * f, 0, 255)
    return out


def _mix(a, b, t):
    return np.asarray(a, dtype=np.float32) * (1.0 - t) + np.asarray(b, dtype=np.float32) * t


def _canvas(w, h, col):
    a = np.empty((h, w, 4), dtype=np.float32)
    a[:] = col
    return a


def _grain(a, r, amount=0.035):
    a[..., :3] *= r.uniform(1.0 - amount, 1.0 + amount, a.shape[:2])[..., None]


def _rows(a, top, bottom):
    a[..., :3] *= np.linspace(top, bottom, a.shape[0])[:, None, None]


def _cols(a, left, right):
    a[..., :3] *= np.linspace(left, right, a.shape[1])[None, :, None]


def _boxtex(w, h, d, col, r, grain=0.035):
    """Six plain shaded faces for a w x h x d pixel box: front/back (w x h), side (d x h, column 0 = front), top/bottom (w x d)."""
    f = {
        "front": _canvas(w, h, col), "back": _canvas(w, h, col), "side": _canvas(d, h, col),
        "top": _canvas(w, d, col), "bottom": _canvas(w, d, col),
    }
    for k in ("front", "back", "side"):
        _rows(f[k], 1.05, 0.9)
    f["back"][..., :3] *= 0.96
    f["side"][..., :3] *= 0.97
    f["top"][..., :3] *= 1.07
    f["bottom"][..., :3] *= 0.62
    for a in f.values():
        _grain(a, r, grain)
    return f


# ----------------------------------------------------------------------------------------------------
# texture sheet + box mesh builder
# ----------------------------------------------------------------------------------------------------
class _Sheet:
    """Collects small face textures and shelf-packs them into one sheet with 1 px extruded gutters."""

    def __init__(self, name, width=64):
        self.name, self.width = name, width
        self.tiles, self.rects, self.size = [], {}, (width, 16)

    def add(self, arr):
        """Register one face texture (HxWx4, any numeric type); returns its tile id."""
        self.tiles.append(np.clip(np.rint(np.asarray(arr, dtype=np.float32)), 0, 255).astype(np.uint8))
        return len(self.tiles) - 1

    def pack(self):
        """Lay the tiles out on shelves and return the finished sheet as a packed bpy Image."""
        order = sorted(range(len(self.tiles)), key=lambda i: (-self.tiles[i].shape[0], -self.tiles[i].shape[1], i))
        x = y = shelf = 0
        for i in order:
            h, w = self.tiles[i].shape[:2]
            if x + w + 2 > self.width:
                x, y, shelf = 0, y + shelf, 0
            self.rects[i] = (x + 1, y + 1, w, h)
            x += w + 2
            shelf = max(shelf, h + 2)
        height = int(math.ceil((y + shelf) / 16.0)) * 16
        sheet = np.zeros((height, self.width, 4), dtype=np.uint8)
        for i, (tx, ty, w, h) in self.rects.items():
            sheet[ty - 1:ty + h + 1, tx - 1:tx + w + 1] = np.pad(self.tiles[i], ((1, 1), (1, 1), (0, 0)), mode="edge")
        self.size = (self.width, height)
        return pix.image_from_array(self.name, sheet)

    def uv(self, tile):
        """UVs for the corners BL, BR, TR, TL of a tile (inset a hair so Closest never samples the gutter)."""
        x, y, w, h = self.rects[tile]
        sw, sh = self.size
        e = 0.02
        u0, u1 = (x + e) / sw, (x + w - e) / sw
        v1, v0 = 1.0 - (y + e) / sh, 1.0 - (y + h - e) / sh
        return ((u0, v0), (u1, v0), (u1, v1), (u0, v1))


# corner selectors (0 = lo, 1 = hi per axis) in the order BL, BR, TR, TL as seen from OUTSIDE the box
# with the image upright.  "right"/"left" are the CHARACTER's right (-X) and left (+X).
_FACE_CORNERS = {
    "front": ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)),     # -Y, image left = -X
    "back": ((1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)),      # +Y, image left = +X
    "right": ((0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)),     # -X, image left = back, image right = front
    "left": ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)),      # +X, image left = front, image right = back
    "top": ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)),       # +Z, image bottom = front, image left = -X
    "bottom": ((1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)),    # -Z, image bottom = front, image left = +X
}


class _Rig:
    """Accumulates parts (pivot + textured boxes), then builds the parented objects."""

    def __init__(self, name, unit):
        self.name, self.unit = name, unit
        tex, n = "char_" + name, 1
        while tex in bpy.data.materials or tex in bpy.data.images:
            n += 1
            tex = "char_%s_%d" % (name, n)
        self.sheet = _Sheet(tex)
        self.parts = {}

    def part(self, name, parent, pivot, rot=(0.0, 0.0, 0.0), k=1.0, mesh=True):
        """Declare a part whose origin sits at `pivot` (pixels, in the parent's frame); k scales its own geometry."""
        self.parts[name] = dict(name=name, parent=parent, pivot=pivot, rot=rot, k=k, mesh=mesh, quads=[])
        return name

    def box(self, part, lo, hi, faces):
        """Add a box lo..hi (pixels, part-local). faces: front, back, top, bottom and either side or left+right."""
        f = dict(faces)
        if "side" in f:
            f.setdefault("left", f["side"])
            f.setdefault("right", f["side"][:, ::-1])
        for fname, sel in _FACE_CORNERS.items():
            corners = [(hi[0] if s[0] else lo[0], hi[1] if s[1] else lo[1], hi[2] if s[2] else lo[2]) for s in sel]
            self.parts[part]["quads"].append((corners, self.sheet.add(f[fname])))

    def quad(self, part, corners, tex):
        """Add one free quad (corners BL, BR, TR, TL in pixels, part-local)."""
        self.parts[part]["quads"].append((list(corners), self.sheet.add(tex)))

    def build(self, collection):
        """Create the texture sheet, material, meshes and parented objects; returns ({part: Object}, material)."""
        image = self.sheet.pack()
        mat = pix.pixel_material(self.sheet.name, image)
        root = bpy.data.objects.new(self.name + "_root", None)
        root.empty_display_size = 0.25
        collection.objects.link(root)
        objs, scale = {"root": root}, {"root": 1.0}
        for p in self.parts.values():
            if p["mesh"]:
                me = bpy.data.meshes.new(self.name + "_" + p["name"])
                verts, faces, uvs = [], [], []
                s = self.unit * p["k"]
                for corners, tile in p["quads"]:
                    n = len(verts)
                    verts.extend((c[0] * s, c[1] * s, c[2] * s) for c in corners)
                    faces.append((n, n + 1, n + 2, n + 3))
                    uvs.extend(self.sheet.uv(tile))
                me.from_pydata(verts, [], faces)
                layer = me.uv_layers.new(name="UVMap")
                for i, uv in enumerate(uvs):
                    layer.data[i].uv = uv
                me.materials.append(mat)
                me.update()
                ob = bpy.data.objects.new(self.name + "_" + p["name"], me)
            else:
                ob = bpy.data.objects.new(self.name + "_" + p["name"], None)
                ob.empty_display_size = 0.12
            collection.objects.link(ob)
            ob.parent = objs[p["parent"]]
            ps = self.unit * scale[p["parent"]]
            ob.location = (p["pivot"][0] * ps, p["pivot"][1] * ps, p["pivot"][2] * ps)
            ob.rotation_euler = p["rot"]
            objs[p["name"]], scale[p["name"]] = ob, p["k"]
        return objs, mat


# ----------------------------------------------------------------------------------------------------
# keyframe plumbing (Blender 5.x layered actions: one action + slot per object)
# ----------------------------------------------------------------------------------------------------
def _find(obj, path, index=0):
    """Existing F-curve for obj.<path>[index], or None."""
    ad = obj.animation_data
    if ad is None or ad.action is None or ad.action_slot is None:
        return None
    for layer in ad.action.layers:
        for strip in layer.strips:
            bag = strip.channelbag(ad.action_slot)
            if bag is not None:
                fc = bag.fcurves.find(path, index=index)
                if fc is not None:
                    return fc
    return None


def _ensure(obj, path, index=0):
    """F-curve for obj.<path>[index], creating the action, slot and curve as needed."""
    ad = obj.animation_data or obj.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(obj.name + "_anim")
    return ad.action.fcurve_ensure_for_datablock(obj, path, index=index)


def _val(obj, path, index, frame):
    """Value of a channel at `frame` (from its keys, else the object's rest value)."""
    fc = _find(obj, path, index)
    if fc is not None and len(fc.keyframe_points):
        return float(fc.evaluate(frame))
    v = getattr(obj, path)
    return float(v[index]) if hasattr(v, "__len__") else float(v)


def _put(fc, frame, value, interp):
    """Insert/replace one key. interp: CONSTANT | LINEAR | BEZIER (auto-clamped) | SMOOTH (sine ease in-out)."""
    kp = fc.keyframe_points.insert(float(frame), float(value))
    if interp == "SMOOTH":
        kp.interpolation, kp.easing = "SINE", "EASE_IN_OUT"
    else:
        kp.interpolation = interp
    kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
    return kp


def _begin(obj, path, index, f0, f1):
    """Prepare a channel for a new segment on [f0, f1]; returns its value at f0.

    Drops keys inside (f0, f1] and, when an older segment is still running at f0, the rest of that segment.
    """
    fc = _find(obj, path, index)
    if fc is None or not len(fc.keyframe_points):
        return _val(obj, path, index, f0)
    v0 = float(fc.evaluate(f0))
    kps = fc.keyframe_points
    eps = 1e-3
    running, doomed = False, []
    for i, kp in enumerate(kps):
        x = kp.co.x
        if x <= f0 + eps:
            running = kp.interpolation != "CONSTANT"
        elif running:
            doomed.append(i)
            if kp.interpolation == "CONSTANT":
                running = False
        elif x <= f1 + eps:
            doomed.append(i)
    for i in reversed(doomed):
        kps.remove(kps[i])
    return v0


def _segment(obj, path, index, keys, interp="SMOOTH"):
    """Write one segment. keys: [(frame, value[, interp])]; value None on the first key = current value.

    The last key is always CONSTANT so the channel holds afterwards. Returns the value at the first key.
    """
    f0, f1 = keys[0][0], keys[-1][0]
    v0 = _begin(obj, path, index, f0, f1)
    fc = _ensure(obj, path, index)
    last = len(keys) - 1
    for i, k in enumerate(keys):
        value = v0 if k[1] is None else k[1]
        _put(fc, k[0], value, "CONSTANT" if i == last else (k[2] if len(k) > 2 else interp))
    fc.update()
    return v0


def _ease(obj, path, index, f0, f1, value, interp="SMOOTH"):
    """Ease a channel from its current value at f0 to `value` at f1 and hold (f1 <= f0 is a hard cut at f0)."""
    if f1 <= f0:
        _cut(obj, path, index, f0, value)
    else:
        _segment(obj, path, index, [(f0, None), (f1, value)], interp)


def _offsets(obj, path, index, frame, offs, lo=None, hi=None):
    """Gesture: keys at frame + df with value base + offset (base = value at `frame`), back to hold at the end."""
    base = _val(obj, path, index, frame)
    keys = [(frame, None)]
    for df, off in offs:
        v = base + off
        if lo is not None:
            v = _clamp(v, lo, hi)
        keys.append((frame + df, v))
    _segment(obj, path, index, keys)
    return base


def _cut(obj, path, index, frame, value):
    """Hard jump to `value`, keyed CUT_LEAD frames before `frame` with CONSTANT interpolation.

    A move still running at the cut keeps its motion right up to the cut; the rest of it is discarded.
    """
    t = frame - CUT_LEAD
    fc = _ensure(obj, path, index)
    kps = fc.keyframe_points
    pre = None
    if len(kps):
        running = False
        for kp in kps:
            if kp.co.x >= t - 0.02:
                break
            running = kp.interpolation != "CONSTANT"
        if running:
            pre = float(fc.evaluate(t - 0.01))
        doomed = []
        for i, kp in enumerate(kps):
            if kp.co.x < t - 0.02 or not running:
                continue
            doomed.append(i)
            if kp.interpolation == "CONSTANT":
                running = False
        for i in reversed(doomed):
            kps.remove(kps[i])
    if pre is not None:
        _put(fc, t - 0.01, pre, "CONSTANT")
    _put(fc, t, value, "CONSTANT")
    fc.update()


def _cut_at(obj, path, index, frame):
    """True when the channel has a hard cut keyed for `frame` (a place() on that very frame)."""
    fc = _find(obj, path, index)
    if fc is None:
        return False
    t = frame - CUT_LEAD
    return any(abs(kp.co.x - t) < 1e-3 and kp.interpolation == "CONSTANT" for kp in fc.keyframe_points)


def _strict(obj, path, index, frame, value):
    """CONSTANT key at `frame`, discarding every later key on the channel (used for eyelids)."""
    fc = _ensure(obj, path, index)
    kps = fc.keyframe_points
    for i in range(len(kps) - 1, -1, -1):
        if kps[i].co.x > frame - 1e-3:
            kps.remove(kps[i])
    _put(fc, frame, value, "CONSTANT")
    fc.update()


def read_keys(obj, path, index=0):
    """Read a channel's keys back as [(frame, value, interpolation)] (for tests and debugging)."""
    fc = _find(obj, path, index)
    if fc is None:
        return []
    return [(round(k.co.x, 3), round(k.co.y, 5), k.interpolation) for k in fc.keyframe_points]


# ----------------------------------------------------------------------------------------------------
# Character
# ----------------------------------------------------------------------------------------------------
class Character:
    """A box-rig character: an Empty at the feet with parented mesh parts, animated by object keyframes."""

    def __init__(self, name, kind, parts, unit, dims, profession=None, child=False):
        self.name, self.kind, self.profession, self.child = name, kind, profession, child
        self.parts = parts
        self.root, self.hips, self.body, self.head = parts["root"], parts["hips"], parts["body"], parts["head"]
        self.leg_l, self.leg_r, self.lids = parts["leg_l"], parts["leg_r"], parts["lids"]
        self.arms = parts.get("arms")
        self.arm_l, self.arm_r = parts.get("arm_l"), parts.get("arm_r")
        self.unit = unit
        self.height = dims["height"]
        self.eye_height = dims["eye"]
        self.leg_len = dims["leg"]
        self.back_depth = dims["back"]
        self.hem = dims["hem"]
        self.leg_back = 2.0 * unit
        self.held = None
        self._foot = 1
        self.lids.scale = (1.0, 1.0, LID_OPEN)
        # (object, path, index, rest value) for every pose channel except root position/yaw and eyelids
        self._pose = []
        for ob in (self.hips, self.body, self.head, self.leg_l, self.leg_r, self.arms, self.arm_l, self.arm_r):
            if ob is None:
                continue
            for i in range(3):
                self._pose.append((ob, _ROT, i, float(ob.rotation_euler[i])))
        for i in range(3):
            self._pose.append((self.hips, _LOC, i, float(self.hips.location[i])))

    def __repr__(self):
        return "<Character %s %s%s>" % (self.name, self.profession or self.kind, " child" if self.child else "")

    # ------------------------------------------------------------------ queries
    def objects(self):
        """All objects of the rig (root first), plus the held item if any."""
        obs = [self.parts["root"]] + [o for k, o in self.parts.items() if k != "root"]
        if self.held is not None:
            obs.append(self.held)
        return obs

    def pos_at(self, frame):
        """Keyed world position of the feet at `frame`."""
        return Vector([_val(self.root, _LOC, i, frame) for i in range(3)])

    def yaw_at(self, frame):
        """Keyed body yaw (radians) at `frame`."""
        return _val(self.root, _ROT, 2, frame)

    def eye_point(self, frame):
        """World point between the eyes at `frame` (standing pose) - a good look/focus target."""
        return self.pos_at(frame) + Vector((0.0, 0.0, self.eye_height))

    def _point(self, target, frame):
        if isinstance(target, Character):
            return target.eye_point(frame)
        if isinstance(target, bpy.types.Object):
            if target.parent is None:
                return Vector(target.location)
            bpy.context.view_layer.update()            # parented: needs an evaluated world matrix (current frame)
            return target.matrix_world.translation.copy()
        return _vec3(target)

    # ------------------------------------------------------------------ placement
    def _reset_pose(self, frame, eyes=True):
        for ob, path, i, rest in self._pose:
            if _find(ob, path, i) is not None:
                _cut(ob, path, i, frame, rest)
        if eyes and _find(self.lids, _SCL, 2) is not None:
            _strict(self.lids, _SCL, 2, frame - CUT_LEAD, LID_OPEN)

    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard-set position and yaw from `frame` on (CONSTANT keys, neutral standing pose) - use at shot cuts."""
        p = _vec3(pos)
        for i in range(3):
            _cut(self.root, _LOC, i, frame, p[i])
        _cut(self.root, _ROT, 2, frame, yaw)
        if not keep_pose:
            self._reset_pose(frame)

    def lie_down(self, frame, bed_pos, yaw, surface=0.594, head_at=1.36, asleep=True):
        """Lie on the back from `frame` on (hard cut), head toward the pillow; asleep=True closes the eyes.

        bed_pos = the bed's origin as engine.props.make_bed defines it: bottom centre of the FOOT cell, the
        pillow end lying one block further along +Y turned by `yaw` (= the bed's Z rotation). The body rests
        `surface` above bed_pos (top of the blanket) and the top of the head ends `head_at` from bed_pos.
        """
        tilt = math.radians(5.0)                      # shoulders a little raised so the head settles on the pillow
        bp = _vec3(bed_pos)
        d = Vector((-math.sin(yaw), math.cos(yaw), 0.0))
        hip = bp + d * (head_at - (self.height - self.leg_len) * math.cos(tilt))
        self.place(frame, (hip.x, hip.y, bp.z + surface), yaw)
        lift = max(self.back_depth * math.cos(tilt) + self.hem * math.sin(tilt),
                   self.leg_len * math.sin(tilt) + self.leg_back * math.cos(tilt))
        _cut(self.hips, _ROT, 0, frame, math.radians(-90.0) + tilt)
        _cut(self.hips, _LOC, 2, frame, lift + 0.004)
        _cut(self.head, _ROT, 0, frame, math.radians(10.0))
        if asleep:
            _strict(self.lids, _SCL, 2, frame - CUT_LEAD, LID_CLOSED)

    def show(self, frame, visible=True):
        """Key render (and viewport) visibility of the whole rig and any held item from `frame` on."""
        for ob in self.objects():
            for path in ("hide_render", "hide_viewport"):
                fc = _ensure(ob, path, 0)
                _put(fc, frame, 0.0 if visible else 1.0, "CONSTANT")
                fc.update()

    # ------------------------------------------------------------------ locomotion
    def walk(self, frame, points, speed=WALK_SPEED, run=False, from_current=False):
        """Travel along the polyline `points` at `speed` units/s with a leg cycle and bob; returns the end frame."""
        if run and speed is WALK_SPEED:
            speed = RUN_SPEED
        f0 = int(round(frame))
        here = self.pos_at(f0)
        yaw_now = self.yaw_at(f0)
        pts = [_vec3(p, here.z) for p in points]
        if from_current:
            pts.insert(0, here.copy())
        path = pts[:1]
        for p in pts[1:]:
            if (p - path[-1]).length > 1e-5:
                path.append(p)
        teleport = (path[0] - here).length > 1e-4
        if len(path) < 2:
            if teleport:
                for i in range(3):
                    _cut(self.root, _LOC, i, f0, path[0][i])
            return f0
        seg = [(b - a).length for a, b in zip(path, path[1:])]
        total = sum(seg)
        n = max(2, int(round(total / max(speed, 1e-3) * FPS)))
        f1 = f0 + n
        times, acc = [float(f0)], 0.0
        for length in seg:
            acc += length
            times.append(f0 + n * acc / total)
        times[-1] = float(f1)

        # heading per segment, unwrapped so turns always take the short way round
        yaws, prev = [], yaw_now
        for a, b in zip(path, path[1:]):
            d = b - a
            if math.hypot(d.x, d.y) > 1e-5:
                prev = prev + _wrap(math.atan2(d.x, -d.y) - prev)
            yaws.append(prev)
        if teleport:
            for i in range(3):
                _cut(self.root, _LOC, i, f0, path[0][i])
        if teleport or _cut_at(self.root, _LOC, 0, f0):
            _cut(self.root, _ROT, 2, f0, yaws[0])                       # starting on a cut: already facing the way it goes
            yaw_now = yaws[0]

        # travel: LINEAR between the polyline vertices
        for i in range(3):
            keys = [(t, p[i]) for t, p in zip(times, path)]
            _segment(self.root, _LOC, i, keys, "LINEAR")

        # yaw: short eased turns, at the start and centred on each corner
        turn = 4.0 if run else 6.0
        ykeys = [(float(f0), yaw_now, "LINEAR")]
        t_free = float(f0)
        if abs(yaws[0] - yaw_now) > 1e-4:
            d = turn * _clamp(abs(yaws[0] - yaw_now) / (math.pi / 2), 0.6, 2.0)
            d = min(d, 0.6 * (times[1] - f0))
            ykeys = [(float(f0), yaw_now, "SMOOTH"), (f0 + d, yaws[0], "LINEAR")]
            t_free = f0 + d
        for i in range(1, len(yaws)):
            if abs(yaws[i] - yaws[i - 1]) < 1e-4:
                continue
            h = min(turn / 2.0, 0.45 * (times[i] - times[i - 1]), 0.45 * (times[i + 1] - times[i]))
            ts = max(times[i] - h, t_free)
            if ts <= ykeys[-1][0] + 1e-3:
                ykeys[-1] = (ykeys[-1][0], ykeys[-1][1], "SMOOTH")
            else:
                ykeys.append((ts, yaws[i - 1], "SMOOTH"))
            ykeys.append((times[i] + h, yaws[i], "LINEAR"))
            t_free = times[i] + h
        if f1 > ykeys[-1][0] + 1e-3:
            ykeys.append((float(f1), yaws[-1]))
        _segment(self.root, _ROT, 2, ykeys)

        # legs: swing in opposition, whole number of half-cycles so they end neutral
        k_leg = self.leg_len / 0.6882
        amp = math.radians(34.0 if run else 26.0)
        step = (0.74 if run else 0.58) * k_leg
        nh = max(1, int(round(total / step)))
        if n / nh < 2.5:
            nh = max(1, int(n / 2.5))
        hl = n / nh
        amp *= min(1.0, total / nh / step)                              # a very short hop gets a small step
        mids = [f0 + (k + 0.5) * hl for k in range(nh)]
        sign = [self._foot * (-1) ** k for k in range(nh)]
        if nh % 2:
            self._foot = -self._foot

        def cycle(ob, index, a, end=None):
            """One smooth swing per step, alternating sides, back to neutral at the end."""
            keys = [(f0, None)] + [(t, s * a) for t, s in zip(mids, sign)] + [(f1, 0.0 if end is None else end)]
            _segment(ob, _ROT, index, keys, "BEZIER")

        cycle(self.leg_l, 0, -amp)
        cycle(self.leg_r, 0, amp)
        cycle(self.body, 1, math.radians(2.6 if run else 1.6))          # side-to-side waddle
        if self.kind == "player":
            a_arm = math.radians(48.0 if run else 24.0)
            for arm, s in ((self.arm_r, -1.0), (self.arm_l, 1.0)):
                base = _val(arm, _ROT, 0, f0)
                if abs(base) < 0.2:                                      # a raised/posed arm keeps its pose
                    cycle(arm, 0, s * a_arm)

        # bob: hips drop when the legs are spread so the feet stay on the ground (never above standing height)
        rest_z = self._rest(self.hips, _LOC, 2)
        drop = self.leg_len * (1.0 - math.cos(amp)) * (0.55 if run else 1.0)
        bkeys = [(f0, None)]
        for k in range(nh):
            bkeys.append((mids[k], rest_z - drop))
            if k < nh - 1:
                bkeys.append((f0 + (k + 1) * hl, rest_z))
        bkeys.append((f1, rest_z))
        _segment(self.hips, _LOC, 2, bkeys, "BEZIER")

        if run:
            lean = math.radians(15.0)
            ramp = min(5.0, n / 3.0)
            _segment(self.body, _ROT, 0, [(f0, None), (f0 + ramp, lean), (f1 - ramp, lean), (f1, 0.0)])
            p0 = _val(self.head, _ROT, 0, f0)
            pr, wob = p0 - 0.55 * lean, math.radians(4.5)
            hkeys = [(f0, None)]
            for k in range(nh):
                hkeys.append((mids[k], pr + wob))
                if k < nh - 1:
                    hkeys.append((f0 + (k + 1) * hl, pr - wob))
            hkeys.append((f1, p0))
            _segment(self.head, _ROT, 0, hkeys, "BEZIER")
            if self.arms is not None:
                rest = self._rest(self.arms, _ROT, 0)
                akeys = [(f0, None)] + [(t, rest + s * math.radians(3.0)) for t, s in zip(mids, sign)] + [(f1, rest)]
                _segment(self.arms, _ROT, 0, akeys, "BEZIER")
        return f1

    def _rest(self, ob, path, index):
        for o, p, i, rest in self._pose:
            if o is ob and p == path and i == index:
                return rest
        return 0.0

    # ------------------------------------------------------------------ looking / turning
    def _aim(self, target, frame):
        """Head (yaw, pitch-up) toward a target at `frame`, relative to the body and clamped."""
        if target is None:
            return 0.0, 0.0
        d = self._point(target, frame) - self.eye_point(frame)
        yaw = _clamp(_wrap(math.atan2(d.x, -d.y) - self.yaw_at(frame)), -HEAD_YAW_MAX, HEAD_YAW_MAX)
        pitch = _clamp(math.atan2(d.z, math.hypot(d.x, d.y)), -HEAD_PITCH_MAX, HEAD_PITCH_MAX)
        return yaw, pitch

    def look_at(self, frame, target, ease=6):
        """Turn the head to a world point / Character / Object over `ease` frames (clamped); None = straight ahead."""
        f1 = frame + max(0, ease)
        yaw, pitch = self._aim(target, f1)
        _ease(self.head, _ROT, 2, frame, f1, yaw)
        _ease(self.head, _ROT, 0, frame, f1, -pitch)
        return f1

    def track(self, frame_start, frame_end, target, step=3, ease=6):
        """Keep the head on a (moving) target from frame_start to frame_end, re-aimed every `step` frames."""
        f0, f1 = int(frame_start), int(frame_end)
        yk, pk = [(f0, None)], [(f0, None)]
        f = f0 + max(1, int(ease))
        while f < f1:
            yaw, pitch = self._aim(target, f)
            yk.append((f, yaw))
            pk.append((f, -pitch))
            f += max(1, int(step))
        yaw, pitch = self._aim(target, f1)
        yk.append((f1, yaw))
        pk.append((f1, -pitch))
        _segment(self.head, _ROT, 2, yk, "BEZIER")
        _segment(self.head, _ROT, 0, pk, "BEZIER")
        return f1

    def turn(self, frame, yaw, ease=8):
        """Ease the body to an absolute yaw (radians, 0 faces -Y) the short way round."""
        yaw0 = self.yaw_at(frame)
        _ease(self.root, _ROT, 2, frame, frame + max(0, ease), yaw0 + _wrap(yaw - yaw0))
        return frame + max(0, ease)

    def face(self, frame, target, ease=8, keep_head=False):
        """Turn the whole body toward a world point / Character / Object over `ease` frames (head re-centres)."""
        f1 = frame + max(0, ease)
        pos, yaw0 = self.pos_at(frame), self.yaw_at(frame)
        d = self._point(target, f1) - pos
        if math.hypot(d.x, d.y) < 1e-5:
            return frame
        yaw1 = yaw0 + _wrap(math.atan2(d.x, -d.y) - yaw0)
        _ease(self.root, _ROT, 2, frame, f1, yaw1)
        if not keep_head and abs(_val(self.head, _ROT, 2, frame)) > 1e-3:
            _ease(self.head, _ROT, 2, frame, f1, 0.0)
        if ease >= 6 and abs(yaw1 - yaw0) > 0.35:                       # a little shuffle step while turning
            a, m = math.radians(13.0), frame + ease / 2.0
            if abs(_val(self.leg_l, _ROT, 0, frame)) < 1e-3 and abs(_val(self.leg_r, _ROT, 0, frame)) < 1e-3:
                _segment(self.leg_l, _ROT, 0, [(frame, None), (m, -a), (f1, 0.0)], "BEZIER")
                _segment(self.leg_r, _ROT, 0, [(frame, None), (m, a), (f1, 0.0)], "BEZIER")
        return f1

    # ------------------------------------------------------------------ idle + gestures
    def idle(self, frame_start, frame_end, seed=0):
        """Keep the character alive between frame_start and frame_end: head turns, weight shifts, blinks (seeded)."""
        f0, f1 = int(frame_start), int(frame_end)
        if f1 - f0 < 16:
            return
        r = pix.rng(7919 * (int(seed) + 1) + 13)
        back = min(10, (f1 - f0) // 3)

        def wander(ob, path, index, make, first, gap, dur_range):
            """One segment of eased moves to make(base) targets with holds between, ending back on the base value."""
            base = _val(ob, path, index, f0)
            keys, cur = [(f0, None)], base
            t = f0 + int(r.integers(*first))
            while True:
                dur = int(r.integers(*dur_range))
                if t + dur > f1 - back - 2:
                    break
                tgt = make(base)
                keys += [(t, cur), (t + dur, tgt)]
                cur = tgt
                t += dur + int(r.integers(*gap))
            keys += [(f1 - back, cur), (f1, base)]
            _segment(ob, path, index, keys)

        # head: glance around the direction it already has, sometimes back to it
        def head_yaw(base):
            """Glance up to ~28 degrees either side, or back to where it was."""
            return base if r.random() < 0.3 else _clamp(base + r.uniform(-0.5, 0.5), -HEAD_YAW_MAX, HEAD_YAW_MAX)

        wander(self.head, _ROT, 2, head_yaw, (4, 16), (14, 52), (6, 13))
        wander(self.head, _ROT, 0,
               lambda b: _clamp(b + r.uniform(-0.08, 0.10), -HEAD_PITCH_MAX, HEAD_PITCH_MAX), (4, 18), (18, 56), (6, 13))
        # weight shift: tiny roll of the body plus sideways slide of the hips, alternating sides
        side = [1.0 if r.random() < 0.5 else -1.0]

        def roll(base):
            """Lean a little onto the other foot."""
            side[0] = -side[0]
            return side[0] * r.uniform(0.6, 1.0) * math.radians(1.8)

        wander(self.body, _ROT, 1, roll, (4, 24), (24, 70), (16, 27))
        shift = 0.012 * self.leg_len / 0.6882
        wander(self.hips, _LOC, 0, lambda b: r.uniform(-1.0, 1.0) * shift, (4, 24), (24, 70), (16, 27))
        # arms: slow breathing drift
        if self.arms is not None:
            wander(self.arms, _ROT, 0, lambda b: b + r.uniform(-1.0, 1.0) * math.radians(1.6), (2, 12), (6, 20), (18, 30))
        else:
            for arm in (self.arm_l, self.arm_r):
                wander(arm, _ROT, 0, lambda b: b + r.uniform(-1.0, 1.0) * math.radians(2.2), (2, 12), (6, 20), (18, 30))
        # blinks (skipped while the eyes are closed)
        if _val(self.lids, _SCL, 2, f0) < 0.5:
            _strict(self.lids, _SCL, 2, f0, LID_OPEN)
            fc = _ensure(self.lids, _SCL, 2)
            t = f0 + int(r.integers(10, 50))
            while t + 4 < f1:
                _put(fc, t, LID_CLOSED, "CONSTANT")
                _put(fc, t + 3, LID_OPEN, "CONSTANT")
                t += int(r.integers(36, 110))
            fc.update()

    def shiver(self, frame_start, frame_end, seed=0, amount=1.0):
        """Frightened tremble between frame_start and frame_end: hunched, head tucked, quick small shakes (seeded)."""
        f0, f1 = int(frame_start), int(frame_end)
        if f1 - f0 < 6:
            return
        r = pix.rng(4241 * (int(seed) + 1) + 7)
        ramp = min(6, (f1 - f0) // 3)
        k = self.leg_len / 0.6882
        for ob, off in ((self.body, math.radians(7.0)), (self.head, math.radians(9.0))):
            base = _val(ob, _ROT, 0, f0)
            _segment(ob, _ROT, 0, [(f0, None), (f0 + ramp, base + off * amount), (f1 - ramp, base + off * amount), (f1, base)])
        if self.arms is not None:
            base = _val(self.arms, _ROT, 0, f0)
            _segment(self.arms, _ROT, 0, [(f0, None), (f0 + ramp, base - 0.12 * amount), (f1 - ramp, base - 0.12 * amount), (f1, base)])
        twist, slide = [(f0, None)], [(f0, None)]
        for n, f in enumerate(range(f0 + 2, f1 - 1, 2)):
            sgn = 1.0 if n % 2 else -1.0
            twist.append((f, sgn * r.uniform(0.5, 1.0) * math.radians(2.4) * amount))
            slide.append((f, sgn * r.uniform(0.4, 1.0) * 0.009 * k * amount))
        twist.append((f1, 0.0))
        slide.append((f1, 0.0))
        _segment(self.body, _ROT, 2, twist, "BEZIER")
        _segment(self.hips, _LOC, 0, slide, "BEZIER")

    def work(self, frame_start, frame_end, target=None, seed=0):
        """Busy at a workstation from frame_start to frame_end: looks at `target`, small arm jolts and nods (seeded)."""
        f0, f1 = int(frame_start), int(frame_end)
        r = pix.rng(2713 * (int(seed) + 1) + 5)
        if target is not None:
            self.look_at(f0, target, ease=0)
        t = f0 + int(r.integers(5, 16))
        while t + 15 < f1:
            t = self.swing_arm(t) if r.random() < 0.65 else self.nod(t)
            t += int(r.integers(6, 24))
        return f1

    def blink(self, frame, frames=3):
        """Close the eyes for `frames` frames starting at `frame`."""
        _strict(self.lids, _SCL, 2, frame, LID_CLOSED)
        _put(_ensure(self.lids, _SCL, 2), frame + frames, LID_OPEN, "CONSTANT")
        return frame + frames

    def close_eyes(self, frame, closed=True):
        """Shut (or open) the eyes from `frame` on."""
        _strict(self.lids, _SCL, 2, frame, LID_CLOSED if closed else LID_OPEN)

    def nod(self, frame):
        """Two quick nods (14 frames); returns the end frame."""
        _offsets(self.head, _ROT, 0, frame, [(3, 0.30), (7, -0.06), (10, 0.22), (14, 0.0)],
                 -HEAD_PITCH_MAX - 0.21, HEAD_PITCH_MAX + 0.21)
        return frame + 14

    def shake(self, frame):
        """Shake the head left-right-left (18 frames); returns the end frame."""
        _offsets(self.head, _ROT, 2, frame, [(3, 0.38), (8, -0.38), (13, 0.24), (18, 0.0)],
                 -HEAD_YAW_MAX - 0.2, HEAD_YAW_MAX + 0.2)
        return frame + 18

    def flinch(self, frame):
        """Startled hop then duck and recover (12 frames, airborne around frame+2); returns the end frame."""
        k = self.leg_len / 0.6882
        _offsets(self.hips, _LOC, 2, frame, [(2, 0.11 * k), (5, -0.05 * k), (12, 0.0)])
        _offsets(self.body, _ROT, 0, frame, [(2, -0.14), (5, 0.17), (12, 0.0)])
        _offsets(self.head, _ROT, 0, frame, [(2, -0.26), (5, 0.20), (12, 0.0)])
        _offsets(self.leg_l, _ROT, 0, frame, [(2, 0.16), (5, -0.10), (12, 0.0)])
        _offsets(self.leg_r, _ROT, 0, frame, [(2, 0.16), (5, 0.12), (12, 0.0)])
        if self.arms is not None:
            _offsets(self.arms, _ROT, 0, frame, [(2, -0.28), (6, 0.06), (12, 0.0)])
        else:
            _offsets(self.arm_l, _ROT, 0, frame, [(2, -0.55), (6, -0.20), (12, 0.0)])
            _offsets(self.arm_r, _ROT, 0, frame, [(2, -0.55), (6, -0.20), (12, 0.0)])
            _offsets(self.arm_l, _ROT, 1, frame, [(2, 0.30), (6, 0.12), (12, 0.0)])
            _offsets(self.arm_r, _ROT, 1, frame, [(2, -0.30), (6, -0.12), (12, 0.0)])
        return frame + 12

    def swing_arm(self, frame):
        """Player: right-arm use swing (10 frames, hits at frame+5). Villager: small jolt of the folded arms (9 frames)."""
        if self.arm_r is None:
            _offsets(self.arms, _ROT, 0, frame, [(2, -0.24), (5, 0.07), (9, 0.0)])
            _offsets(self.head, _ROT, 0, frame, [(3, 0.13), (9, 0.0)], -HEAD_PITCH_MAX - 0.21, HEAD_PITCH_MAX + 0.21)
            return frame + 9
        base = _val(self.arm_r, _ROT, 0, frame)
        _segment(self.arm_r, _ROT, 0, [(frame, None), (frame + 2, min(base, -1.95)), (frame + 5, -0.45), (frame + 10, base)])
        _offsets(self.arm_r, _ROT, 2, frame, [(2, -0.10), (5, 0.30), (10, 0.0)])
        _offsets(self.body, _ROT, 2, frame, [(2, -0.09), (5, 0.14), (10, 0.0)])
        _offsets(self.body, _ROT, 0, frame, [(2, -0.03), (5, 0.07), (10, 0.0)])
        return frame + 10

    def raise_arm(self, frame, angle=65.0, ease=8, side="r"):
        """Player: ease an arm to `angle` degrees forward of hanging (0 = down, 90 = straight out) and hold it there."""
        arm = self.arm_r if side == "r" else self.arm_l
        if arm is None:
            arm = self.arms
            value = ARMS_FOLD - math.radians(angle) * 0.25
        else:
            value = -math.radians(angle)
        _ease(arm, _ROT, 0, frame, frame + max(0, ease), value)
        return frame + max(0, ease)

    def hold(self, obj, offset=None, rotation=None):
        """Put an item in the right hand (player) or on the folded hands (villager); hold(None) lets go."""
        if self.held is not None and self.held is not obj:
            self.held.parent = None
            self.held = None
        if obj is None:
            return None
        u = self.unit
        if self.arm_r is not None:
            hand, loc, rot = self.arm_r, (0.0, -2.3 * u, -9.4 * u), (math.radians(65.0), 0.0, 0.0)
        else:
            hand, loc, rot = self.arms, (0.0, -0.86 * u, -8.6 * u), (-ARMS_FOLD, 0.0, 0.0)
        obj.parent = hand
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.location = loc if offset is None else offset
        obj.rotation_euler = rot if rotation is None else rotation
        self.held = obj
        return obj


# ----------------------------------------------------------------------------------------------------
# villager art
# ----------------------------------------------------------------------------------------------------
_PAL = {
    "farmer": dict(robe="#8a673c", trim="#553c22", belt="#d9bd6c", accent="#ead9a8", legs="#4d3b29", shoes="#2b2018"),
    "librarian": dict(robe="#e8e1cf", trim="#a03a2e", belt="#cba64a", accent="#a03a2e", legs="#6d5b4b", shoes="#33261d"),
    "smith": dict(robe="#786a5d", trim="#4b4039", belt="#2e2a29", accent="#2e2a29", legs="#3b342f", shoes="#1e1a18"),
    "cleric": dict(robe="#7141a8", trim="#e2ba40", belt="#e2ba40", accent="#9363cb", legs="#3f2762", shoes="#241a2e"),
    "shepherd": dict(robe="#7c5b3c", trim="#4e3723", belt="#3a2919", accent="#f0ebdd", legs="#4d3b29", shoes="#2b2018"),
    "plain": dict(robe="#7b5b3d", trim="#523a25", belt="#3a2a1b", accent="#c9a85a", legs="#4a392b", shoes="#2b2018"),
    "nitwit": dict(robe="#5aa946", trim="#3b7f33", belt="#3b7f33", accent="#8bce6c", legs="#3a7a34", shoes="#3d2c1e"),
}
_BROW = "#3a291f"


def _villager_head(r, prof, skin):
    """Paint head and nose faces; returns (head faces, nose faces, eye rects [(x0, x1, row0, row1)], lid colour)."""
    white, iris, iris_d = _c("#f5f2e9"), _c("#2f8e3f"), _c("#1f6b2d")
    brow, mouth = _c(_BROW), _mul(skin, 0.68)
    front = _canvas(8, 10, skin)
    _rows(front, 1.07, 0.92)
    front[:, 0, :3] *= 0.94
    front[:, 7, :3] *= 0.94
    _grain(front, r, 0.03)
    front[5:10, 3:5, :3] *= 0.88
    for x in (1, 6):
        front[6, x] = _mix(front[6, x], _c("#d98a78"), 0.5 if prof == "nitwit" else 0.25)
    if prof == "nitwit":
        front[2, 2:6] = brow                      # short single brow, raised: wide-eyed and gentle
        for row in (4, 5):                        # big round eyes
            front[row, 1], front[row, 2] = white, iris
            front[row, 5], front[row, 6] = iris, white
        front[5, 2], front[5, 5] = iris_d, iris_d
        front[8, 2], front[8, 5] = mouth, mouth   # small smile either side of the nose
        front[7, 1], front[7, 6] = _mul(skin, 0.8), _mul(skin, 0.8)
        eyes = [(1, 3, 4, 6), (5, 7, 4, 6)]
    else:
        front[3, 1:7] = brow
        front[4, 1], front[4, 2] = white, iris
        front[4, 5], front[4, 6] = iris, white
        front[5, 1:3, :3] *= 0.93
        front[5, 5:7, :3] *= 0.93
        front[8, 2:6] = mouth
        eyes = [(1, 3, 4, 5), (5, 7, 4, 5)]
    if prof == "smith":                           # soot smudges
        for (y, x, t) in ((6, 5, 0.3), (7, 6, 0.22), (1, 1, 0.2)):
            front[y, x] = _mix(front[y, x], _c("#4a4340"), t)
    side = _canvas(8, 10, skin)
    _rows(side, 1.06, 0.92)
    _cols(side, 1.0, 0.9)
    _grain(side, r, 0.03)
    if prof != "nitwit":
        side[3, 0] = brow
    side[4:7, 3:5, :3] *= 0.86                    # ear
    side[5, 3, :3] *= 1.2
    back = _canvas(8, 10, _mul(skin, 0.92))
    _rows(back, 1.05, 0.88)
    _grain(back, r, 0.03)
    back[8, 1:7, :3] *= 0.93
    top = _canvas(8, 8, _mul(skin, 1.08))
    _grain(top, r, 0.03)
    top[2:5, 2:6, :3] *= 1.04
    bottom = _canvas(8, 8, _mul(skin, 0.6))
    head = dict(front=front, back=back, side=side, top=top, bottom=bottom)
    nose = _boxtex(2, 4, 2, _mix(skin, _c("#b0705c"), 0.35), r, 0.02)
    nose["front"][0, :, :3] *= 1.06
    nose["front"][3, :, :3] *= 0.9
    nose["bottom"][..., :3] *= 1.15
    return head, nose, eyes, _mul(skin, 0.74)


def _villager_robe(r, prof, p):
    """Robe faces for the 8 x 18 x 6 pixel body box."""
    robe, trim, belt, accent = _c(p["robe"]), _c(p["trim"]), _c(p["belt"]), _c(p["accent"])
    f = _boxtex(8, 18, 6, robe, r)
    front, back, side = f["front"], f["back"], f["side"]
    for a, cols in ((front, (2, 5)), (back, (1, 6)), (side, (1, 4))):          # skirt folds
        for x in cols:
            a[11:, x, :3] *= 0.87
    front[3:17, 3, :3] *= 0.95
    for a in (front, back, side):                                              # collar + hem
        a[0:2] = trim
        a[17] = _mul(trim, 0.92)
    f["top"][:] = _mul(trim, 0.9)
    if prof == "farmer":
        front[0:3, 3:5] = _mul(robe, 0.7)                                       # open collar
        for a in (front, back, side):
            a[10] = belt
        front[11:13, 5] = _mul(belt, 0.9)
        front[13:15, 1:3, :3] *= 0.88                                           # patch pocket
    elif prof == "librarian":
        front[2:17, 3:5] = accent
        front[2:17, 3, :3] *= 1.08
        for a in (front, back, side):
            a[10] = belt
        front[10, 3:5] = _mul(belt, 1.15)
        back[2:17, 3:5, :3] *= 0.95
    elif prof == "smith":
        apron = accent
        front[3:16, 1:7] = apron
        front[0:3, 1], front[0:3, 6] = apron, apron
        front[4:16, 1:7, :3] *= np.linspace(1.12, 0.92, 12)[:, None, None]
        front[10, 2:6, :3] *= 1.45                                              # pocket edge
        front[11:13, 2, :3] *= 1.25
        front[11:13, 5, :3] *= 1.25
        for a in (back, side):
            a[9] = apron
        back[0:9, 1], back[0:9, 6] = apron, apron
        back[10:12, 3:5] = apron                                                # apron ties
    elif prof == "cleric":
        front[2:17, 3:5] = accent
        front[2:17, 2], front[2:17, 5] = trim, trim
        front[15:17, 3:5] = trim
        for a in (back, side):
            a[10] = _mul(trim, 0.95)
        back[2:10, 3:5, :3] *= 1.12
    elif prof == "shepherd":
        wool = accent
        for a in (front, back, side):
            a[0:7] = wool
            a[7, ::2] = wool
            a[1:7, :, :3] *= r.uniform(0.9, 1.02, a[1:7].shape[:2])[..., None]
            a[10] = belt
        front[0:2, 3:5] = _mul(wool, 0.8)
        front[10, 3:5] = _c("#c9a85a")
    elif prof == "plain":
        for a in (front, back, side):
            a[10] = belt
        front[10, 3:5] = accent
        front[0:3, 3:5] = _mul(robe, 0.7)
    elif prof == "nitwit":
        front[0:3, 3:5] = _mul(robe, 0.72)
        for a in (front, back, side):                                           # frayed hem
            a[17] = robe
            a[17, ::2] = _mul(trim, 0.92)
            a[16, 1::2, :3] *= 0.9
        front[11:14, 5:7] = accent                                              # a mended patch
        front[11, 5], front[13, 6] = _mul(trim, 0.8), _mul(trim, 0.8)
        back[5:8, 1:3] = _mul(accent, 0.95)
        back[5, 2], back[7, 1] = _mul(trim, 0.8), _mul(trim, 0.8)
        front[6:8, 1, :3] *= 0.9
    return f


def _villager_arms(r, prof, p):
    """Faces for a sleeve (4 x 8 x 4) and for the bar across the chest (8 x 4 x 4)."""
    robe, trim = _mul(_c(p["robe"]), 0.93), _c(p["trim"])
    sleeve = _boxtex(4, 8, 4, robe, r)
    bar = _boxtex(8, 4, 4, robe, r)
    for a in (bar["front"], bar["top"], bar["bottom"]):
        a[:, 3:5] = _mul(trim, 0.95)                                            # cuffs meeting in the middle
        a[:, 2, :3] *= 0.9
        a[:, 5, :3] *= 0.9
    bar["bottom"][..., :3] *= 1.25
    sleeve["bottom"][..., :3] *= 1.25
    if prof == "shepherd":
        for k in ("front", "back", "side"):
            sleeve[k][0:3] = _mul(_c(p["accent"]), 0.97)
        sleeve["top"][:] = _c(p["accent"])
    if prof == "smith":
        for a in (bar["front"], bar["top"], bar["bottom"]):
            a[:, 2:6] = _c(p["accent"])                                         # dark gloves
    return sleeve, bar


def _leg_tex(r, cloth, shoe, cuff=9):
    f = _boxtex(4, 12, 4, cloth, r)
    for k in ("front", "back", "side"):
        f[k][10:12] = shoe
        f[k][cuff, :, :3] *= 0.85
    f["front"][10, :, :3] *= 1.25
    f["side"][11, :, :3] *= 0.8
    f["bottom"][:] = _mul(shoe, 0.7)
    return f


def _straw(w, h, r, base="#dbb955"):
    a = _canvas(w, h, _c(base))
    a[..., :3] *= r.uniform(0.9, 1.06, (h, w))[..., None]
    return a


def _add_hat(rig, head, prof, r):
    """Profession headgear, added as extra boxes on the head part (pixels, head-local, neck at z = 0)."""
    if prof == "farmer":
        top = _straw(14, 14, r)
        yy, xx = np.mgrid[0:14, 0:14]
        ring = np.maximum(np.abs(xx - 6.5), np.abs(yy - 6.5)).astype(int)
        top[..., :3] *= np.where(ring % 2 == 0, 1.0, 0.88)[..., None]
        under = top.copy()
        under[..., :3] *= 0.62
        edge = _straw(14, 1, r)
        edge[..., :3] *= 0.86
        rig.box(head, (-7, -7, 7.0), (7, 7, 8.0), dict(front=edge, back=edge, side=edge, top=top, bottom=under))
        crown = dict(front=_straw(9, 4, r), back=_straw(9, 4, r), side=_straw(9, 4, r),
                     top=_straw(9, 9, r), bottom=_straw(9, 9, r))
        for k in ("front", "back", "side"):
            crown[k][3] = _c("#6b4426")                                         # hat band
            crown[k][1, ::2, :3] *= 0.88
        crown["top"][2:7, 2:7, :3] *= 0.9
        crown["top"][3:6, 3:6, :3] *= 1.12
        rig.box(head, (-4.45, -4.45, 8.0), (4.45, 4.45, 11.6), crown)
    elif prof == "librarian":
        cover, page, gold = _c("#a2392d"), _c("#efe6cf"), _c("#d8b24a")
        book = _boxtex(9, 3, 9, cover, r, 0.02)
        for k in ("front", "side"):
            book[k][1] = page
            book[k][1, ::2, :3] *= 0.9
        book["back"][:, 2], book["back"][:, 6] = gold, gold                    # the spine sits at the back
        t = book["top"]
        t[1, 1:8], t[7, 1:8], t[1:8, 1], t[1:8, 7] = gold, gold, gold, gold
        t[3:6, 4], t[4, 3:6] = gold, gold
        rig.box(head, (-4.5, -4.5, 9.4), (4.5, 4.5, 12.2), book)
    elif prof == "shepherd":
        felt, band = _c("#5d4129"), _c("#d7c49a")
        brim = _boxtex(11, 1, 11, felt, r)
        rig.box(head, (-5.6, -5.6, 8.0), (5.6, 5.6, 8.9), brim)
        crown = _boxtex(9, 3, 9, felt, r)
        for k in ("front", "back", "side"):
            crown[k][2] = band
        crown["side"][0:2, 5] = _c("#f3efe4")                                   # a white feather
        crown["side"][0, 6] = _c("#f3efe4")
        rig.box(head, (-4.35, -4.35, 8.9), (4.35, 4.35, 11.7), crown)
    elif prof == "cleric":
        cap = _boxtex(9, 2, 9, _c("#5c3390"), r)
        for k in ("front", "back", "side"):
            cap[k][1] = _c("#e2ba40")
        cap["top"][3:6, 3:6] = _c("#e2ba40")
        cap["top"][4, 4] = _c("#7141a8")
        rig.box(head, (-4.3, -4.3, 8.7), (4.3, 4.3, 10.8), cap)
    elif prof == "smith":
        band = _boxtex(9, 2, 9, _c("#3a302b"), r)                               # leather headband / cap
        band["top"][2:7, 2:7, :3] *= 1.15
        rig.box(head, (-4.25, -4.25, 8.4), (4.25, 4.25, 10.5), band)
    elif prof == "nitwit":
        tuft = _boxtex(1, 2, 2, _c("#6a4526"), r)                               # one stubborn tuft of hair
        rig.box(head, (0.2, -0.6, 10.0), (1.3, 1.2, 11.7), tuft)
        tuft2 = _boxtex(1, 1, 1, _c("#7a5230"), r)
        rig.box(head, (-0.9, 0.2, 10.0), (0.2, 1.3, 10.9), tuft2)


def _add_lids(rig, head_part, k, eyes, face_h, y_face, lid_col, lash_col):
    """Eyelid quads just in front of the eyes; the part origin is the eyes' top edge so scale.z closes them."""
    top = face_h - min(e[2] for e in eyes)
    lids = rig.part("lids", head_part, (0.0, y_face - 0.08, top), k=k)
    for (x0, x1, r0, r1) in eyes:
        tex = _canvas(x1 - x0, r1 - r0, lid_col)
        tex[-1] = lash_col
        zb, zt = (face_h - r1) - top, (face_h - r0) - top
        xa, xb = -4 + x0, -4 + x1
        rig.quad(lids, ((xa, 0, zb), (xb, 0, zb), (xb, 0, zt), (xa, 0, zt)), tex)
    return lids


def _collection(collection):
    if collection is not None:
        return collection
    scene = bpy.context.scene
    col = bpy.data.collections.get("characters")
    if col is None:
        col = bpy.data.collections.new("characters")
    if col.name not in scene.collection.children:
        scene.collection.children.link(col)
    return col


def make_villager(name, profession="farmer", child=False, collection=None):
    """Build a villager (1.95 tall, feet at the origin, facing -Y); profession picks robe and hat, child=True a small big-headed kid."""
    if profession not in PROFESSIONS:
        raise ValueError("unknown profession %r (use one of %s)" % (profession, ", ".join(PROFESSIONS)))
    r = pix.rng(_seed("villager", name, profession))
    p = _PAL[profession]
    s = 0.5 if child else 1.0
    hk = 1.5 if child else 1.0
    u = s * VILLAGER_HEIGHT / 34.0
    skin = _mul(_c("#c4926f"), float(r.uniform(0.95, 1.04)))
    rig = _Rig(name, u)

    rig.part("hips", "root", (0, 0, 12), mesh=False)
    body = rig.part("body", "hips", (0, 0, 0))
    rig.box(body, (-4.3, -3.3, -6.0), (4.3, 3.3, 12.0), _villager_robe(r, profession, p))

    head = rig.part("head", "body", (0, 0, 12), k=hk)
    head_tex, nose_tex, eyes, lid_col = _villager_head(r, profession, skin)
    rig.box(head, (-4, -4, 0), (4, 4, 10), head_tex)
    rig.box(head, (-1, -6, -1), (1, -4, 3), nose_tex)
    _add_hat(rig, head, profession, r)
    _add_lids(rig, head, hk, eyes, 10, -4.0, lid_col, _mul(skin, 0.55))

    arms = rig.part("arms", "body", (0, 0, 10), rot=(ARMS_FOLD, 0.0, 0.0))
    sleeve, bar = _villager_arms(r, profession, p)
    rig.box(arms, (-8, -2, -6), (-4, 2, 2), sleeve)
    rig.box(arms, (4, -2, -6), (8, 2, 2), sleeve)
    rig.box(arms, (-4, -2, -6), (4, 2, -2), bar)

    leg = _leg_tex(r, _c(p["legs"]), _c(p["shoes"]))
    for nm, x in (("leg_r", -2.0), ("leg_l", 2.0)):
        rig.part(nm, "hips", (x, 0, 0))
        rig.box(nm, (-1.95, -2, -12), (1.95, 2, 0), leg)

    parts, _mat = rig.build(_collection(collection))
    dims = dict(height=(24 + 10 * hk) * u, eye=(24 + 5.5 * hk) * u, leg=12 * u, back=3.3 * u, hem=6 * u)
    return Character(name, "villager", parts, u, dims, profession=profession, child=child)


# ----------------------------------------------------------------------------------------------------
# player art (our own skin: brown hair, red hooded top, dark grey trousers, dark shoes)
# ----------------------------------------------------------------------------------------------------
def _player_head(r):
    skin, hair = _c("#e3b28e"), _c("#5c3b22")
    hair_l, hair_d, eye = _mul(hair, 1.25), _mul(hair, 0.78), _c("#2b1d15")
    front = _canvas(8, 8, skin)
    _rows(front, 1.04, 0.93)
    _grain(front, r, 0.025)
    front[0:2] = hair
    front[2, 0:3], front[2, 6:8] = hair, hair                                   # side-swept fringe
    front[3, 0], front[3, 7] = hair_d, hair_d
    front[2, 2], front[1, 4], front[0, 6], front[1, 1] = hair_l, hair_l, hair_l, hair_l
    front[2, 0] = hair_d
    for x in (2, 5):                                                            # tall dot eyes
        front[3:5, x] = eye
    for x in (1, 6):
        front[5, x] = _mix(front[5, x], _c("#e58f7d"), 0.42)
    front[6, 3:5] = _mul(skin, 0.68)
    front[7, :, :3] *= 0.95
    side = _canvas(8, 8, skin)
    _rows(side, 1.03, 0.92)
    _grain(side, r, 0.025)
    side[0:3] = hair
    side[3:6, 4:8] = hair
    side[6:8, 6:8] = hair
    side[3:5, 1] = hair                                                         # sideburn
    side[4:6, 3, :3] *= 0.86                                                    # ear
    side[1, 2], side[2, 5], side[4, 6] = hair_l, hair_l, hair_l
    side[5, 7], side[3, 4] = hair_d, hair_d
    back = _canvas(8, 8, hair)
    _grain(back, r, 0.05)
    back[7, 0], back[7, 7] = _mul(skin, 0.9), _mul(skin, 0.9)
    back[2:7, 2, :3] *= 1.15
    back[1:6, 5, :3] *= 0.85
    top = _canvas(8, 8, hair)
    _grain(top, r, 0.05)
    top[1:7, 5, :3] *= 1.22                                                     # parting
    top[2:6, 2, :3] *= 0.88
    bottom = _canvas(8, 8, _mul(skin, 0.6))
    return dict(front=front, back=back, side=side, top=top, bottom=bottom), skin


def _player_body(r):
    red, cord = _c("#b6352d"), _c("#ecdfd0")
    f = _boxtex(8, 12, 4, red, r, 0.03)
    front, back, side = f["front"], f["back"], f["side"]
    dark = _mul(red, 0.74)
    front[0] = dark
    front[0, 3:5] = _c("#4f1513")                                               # neck opening
    front[1, 3:5] = _mul(red, 0.85)
    front[1:4, 2], front[1:4, 5] = cord, cord                                   # drawstrings
    front[3, 2], front[3, 5] = _mul(cord, 0.82), _mul(cord, 0.82)
    front[7, 2:6] = dark                                                        # pouch pocket
    front[8:10, 1], front[8:10, 6] = dark, dark
    front[8:10, 2:6, :3] *= 1.07
    for a in (front, back, side):
        a[11] = _mul(red, 0.68)                                                 # ribbed hem
        a[11, ::2, :3] *= 1.12
    back[0:4, :, :3] *= 0.88
    back[4:11, 3:5, :3] *= 0.95
    f["top"][:] = dark
    hood = _boxtex(6, 4, 2, _mul(red, 0.86), r, 0.03)
    hood["back"][0, :, :3] *= 1.2
    hood["back"][1:4, 2:4, :3] *= 0.9
    hood["top"][:] = _c("#571917")
    hood["top"][0, :] = _mul(red, 0.95)
    return f, hood


def _player_arm(r, skin):
    red = _c("#b6352d")
    f = _boxtex(4, 12, 4, red, r, 0.03)
    for k in ("front", "back", "side"):
        f[k][9] = _mul(red, 0.68)
        f[k][10:12] = skin
        f[k][11, :, :3] *= 0.92
    f["top"][:] = _mul(red, 1.05)
    f["bottom"][:] = _mul(skin, 0.8)
    return f


def make_player(name="player", collection=None):
    """Build the player (1.9 tall, feet at the origin, facing -Y): brown hair, red hooded top, dark grey trousers."""
    r = pix.rng(_seed("player", name))
    u = PLAYER_HEIGHT / 32.0
    rig = _Rig(name, u)
    rig.part("hips", "root", (0, 0, 12), mesh=False)
    body = rig.part("body", "hips", (0, 0, 0))
    body_tex, hood_tex = _player_body(r)
    rig.box(body, (-4.15, -2.15, -0.6), (4.15, 2.15, 12.0), body_tex)
    rig.box(body, (-3.0, 2.0, 8.3), (3.0, 3.9, 12.0), hood_tex)

    head = rig.part("head", "body", (0, 0, 12))
    head_tex, skin = _player_head(r)
    rig.box(head, (-4, -4, 0), (4, 4, 8), head_tex)
    _add_lids(rig, head, 1.0, [(2, 3, 3, 5), (5, 6, 3, 5)], 8, -4.0, _mul(skin, 0.97), _mul(skin, 0.5))

    arm = _player_arm(r, skin)
    rig.part("arm_r", "body", (-6, 0, 10))
    rig.box("arm_r", (-2, -2, -10), (1.9, 2, 2), arm)
    rig.part("arm_l", "body", (6, 0, 10))
    rig.box("arm_l", (-1.9, -2, -10), (2, 2, 2), arm)

    leg = _leg_tex(r, _c("#3d3f47"), _c("#201e1f"))
    for nm, x in (("leg_r", -2.0), ("leg_l", 2.0)):
        rig.part(nm, "hips", (x, 0, 0))
        rig.box(nm, (-1.95, -2, -12), (1.95, 2, 0), leg)

    parts, _mat = rig.build(_collection(collection))
    dims = dict(height=32 * u, eye=28.0 * u, leg=12 * u, back=2.15 * u, hem=0.6 * u)
    return Character(name, "player", parts, u, dims)


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _test_ground(size=60.0, name="cast_test_ground"):
    """Stand-in ground: a big plane with a tiled 16x16 dirt/grass texture."""
    r = pix.rng(5)
    a = _canvas(16, 16, _c("#7d9a4a"))
    a[..., :3] *= r.uniform(0.82, 1.1, (16, 16))[..., None]
    for _ in range(14):
        y, x = r.integers(0, 16, 2)
        a[y, x] = _c("#9a7b4f")
    mat = pix.pixel_material(name, pix.image_from_array(name, np.clip(a, 0, 255).astype(np.uint8)))
    h = size / 2.0
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)])
    layer = me.uv_layers.new(name="UVMap")
    for i, uv in enumerate(((0, 0), (size, 0), (size, size), (0, size))):
        layer.data[i].uv = uv
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _test_box(name, lo, hi, color):
    """Stand-in flat-coloured box from corner lo to corner hi."""
    xs, ys, zs = (lo[0], hi[0]), (lo[1], hi[1]), (lo[2], hi[2])
    verts = [(xs[i], ys[j], zs[k]) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.materials.append(pix.flat_material(name, pix.rgba(color)))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _selftest(which):
    from . import quick

    def stage(preset="golden", ground=True):
        """Fresh test scene with the quick light rig and a stand-in ground."""
        scene = quick.reset()
        quick.setup(scene)
        quick.light(scene, preset)
        if ground:
            _test_ground()
        return scene

    def want(name):
        """True when this still was asked for (no arguments = all of them)."""
        return not which or name in which

    if want("lineup") or want("back"):
        scene = stage()
        tier, depth = 2.3, 1.0
        _test_box("cast_test_step1", (-2.1, 0.55, 0.0), (2.1, 3.2, tier), "#8c8478")
        _test_box("cast_test_step2", (-2.1, 0.55 + depth, tier), (2.1, 3.2, 2 * tier), "#7b7368")
        rows = [
            [("kid", "plain", True), ("nitwit", "nitwit", False), ("player", None, False)],
            [("farmer", "farmer", False), ("librarian", "librarian", False), ("smith", "smith", False)],
            [("cleric", "cleric", False), ("shepherd", "shepherd", False), ("plain", "plain", False)],
        ]
        for j, row in enumerate(rows):
            for i, (nm, prof, kid) in enumerate(row):
                ch = make_player(nm) if prof is None else make_villager(nm, prof, child=kid)
                ch.place(1, ((i - 1) * 1.25, j * depth, j * tier), 0.0)
        scene.frame_set(1)
        if want("lineup"):
            quick.camera(scene, (-6.0, -15.5, 4.6), (0.0, 1.0, 3.3), lens=52)
            print("wrote", quick.render(scene, "characters_lineup"))
        if want("back"):
            for ob in list(scene.objects):
                if ob.name.startswith("cast_test_step"):
                    ob.hide_render = True
            for j, nm in enumerate(("step1", "step2")):                 # thin floors only, so the backs stay visible
                _test_box("cast_test_floor_" + nm, (-2.1, -0.6 + (j + 1) * depth, (j + 1) * tier - 0.08),
                          (2.1, 0.6 + (j + 1) * depth, (j + 1) * tier), "#8c8478")
            quick.camera(scene, (5.0, 17.5, 4.9), (0.0, 1.0, 3.3), lens=52)
            scene.objects["quick_sun"].rotation_euler[2] = math.radians(150)
            print("wrote", quick.render(scene, "characters_back"))

    if want("faces"):
        scene = stage()
        a = make_villager("nitwit", "nitwit")
        b = make_villager("farmer", "farmer")
        _test_box("cast_test_step1", (-0.2, 0.3, 0.0), (1.2, 1.6, 0.95), "#8c8478")
        a.place(1, (-0.2, 0.0, 0.0), math.radians(-8))
        b.place(1, (0.3, 0.75, 0.95), math.radians(-28))
        cam = (-1.3, -4.9, 2.3)
        a.look_at(1, cam, ease=0)
        b.look_at(1, (-0.6, -3.0, 2.4), ease=0)
        scene.frame_set(1)
        quick.camera(scene, cam, (0.04, 0.3, 2.08), lens=50, fstop=5.6)
        print("wrote", quick.render(scene, "characters_faces"))

    if want("run"):
        scene = stage()
        v = make_villager("runner", "farmer")
        v.place(1, (-6.0, 0.0, 0.0), math.radians(90))
        end = v.walk(1, [(-6.0, 0.0, 0.0), (6.0, 0.0, 0.0)], run=True)
        w = make_villager("walker", "librarian")
        w.place(1, (-1.5, 2.2, 0.0), math.radians(90))
        w.walk(1, [(-1.5, 2.2, 0.0), (6.0, 2.2, 0.0)])
        print("run ends at frame", end, "| leg keys:", read_keys(v.leg_l, _ROT, 0)[:6])
        off = Vector((3.1, -5.3, 0.8))                                 # low camera tracking with the runner
        cam = quick.camera(scene, v.pos_at(1) + off, v.pos_at(1) + Vector((0.2, 0.0, 1.0)), lens=40, fstop=4.0)
        for i in range(3):
            _segment(cam, _LOC, i, [(1, (v.pos_at(1) + off)[i]), (end, (v.pos_at(end) + off)[i])], "LINEAR")
        scene.render.use_motion_blur = True
        for n, f in enumerate((14, 16, 18)):
            scene.frame_set(f)
            print("wrote", quick.render(scene, "characters_run_%d" % (n + 1)))

    if want("swing"):
        scene = stage()
        pl = make_player("player")
        pl.place(1, (0.0, 0.0, 0.0), math.radians(-35))
        gem = _test_box("cast_test_gem", (-0.11, -0.03, 0.0), (0.11, 0.03, 0.3), "#2fd16a")
        pl.hold(gem)
        pl.look_at(1, (1.5, -3.0, 1.2), ease=0)
        pl.swing_arm(10)
        v = make_villager("watcher", "smith")
        v.place(1, (1.5, 1.2, 0.0), math.radians(60))
        v.look_at(1, pl, ease=0)
        scene.render.use_motion_blur = True
        scene.frame_set(13)
        quick.camera(scene, (-2.4, -5.6, 1.5), (0.4, 0.3, 1.0), lens=40, fstop=2.8)
        print("wrote", quick.render(scene, "characters_player_swing"))

    if want("sleep"):
        scene = stage()
        beds = ((make_villager("sleeper", "cleric"), "#b23a34"), (make_player("player"), "#3b6fb5"))
        for i, (ch, col) in enumerate(beds):                             # stand-in beds shaped like props.make_bed
            x = i * 1.5
            _test_box("cast_test_bed%d" % i, (x - 0.5, -0.5, 0.19), (x + 0.5, 1.375, 0.5625), "#e4e1da")
            _test_box("cast_test_blanket%d" % i, (x - 0.52, -0.52, 0.29), (x + 0.52, 0.81, 0.594), col)
            _test_box("cast_test_pillow%d" % i, (x - 0.375, 0.906, 0.5625), (x + 0.375, 1.344, 0.719), "#f4f2ec")
            _test_box("cast_test_frame%d" % i, (x - 0.5, -0.5, 0.0), (x + 0.5, 1.5, 0.19), "#6d4d2c")
            _test_box("cast_test_board%d" % i, (x - 0.5, 1.375, 0.19), (x + 0.5, 1.5, 0.875), "#5a3e24")
            ch.lie_down(1, (x, 0.0, 0.0), 0.0)
        scene.frame_set(1)
        quick.camera(scene, (-2.6, -4.9, 4.0), (0.6, 0.42, 0.45), lens=36, fstop=4.0)
        print("wrote", quick.render(scene, "characters_sleep"))


if __name__ == "__main__":
    _selftest(set(sys.argv[1:]))
