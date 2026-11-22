"""The village set: one continuous voxel village built like a film set (square with bell, five houses,
workstations, trading hall, lantern posts, exit road into a rising meadow).

Layout (block coordinates, +Y = north, ground z = 0 in the village core):

                         hill + oaks (backdrop)
      library corner      HOUSE A (big, door S)        wheat farm
      (-15..-8, 8..14)    (-4..3, 8..17)               (8..16, 8..16)
   HOUSE C  (door E) ---- SQUARE 9x9, bell at (0.5, 0.5) ---- HOUSE B (door W) --- lane --- TRADING HALL
   (-14..-9, -3..2)       (-4..4, -4..4)                (9..14, -3..3)          (20..26, -7..5), aisle N-S
      smithy              exit road (x -1..1)           well
      (-10..-6,-10..-6)   HOUSE E (door E) | HOUSE D (door W)
                          gate at y = -22, then open meadow rising to the south (meadow_far at y = -46)

Use `build_village(scene)`; everything a film needs is on the returned `Village` (anchors, paths, doors,
bell, lantern lights, yaws).
"""
import math

import bpy
import numpy as np

from . import pix, props
from .blocks import ATLAS, BLOCKS, World, pos_hash

# terrain extents (blocks, inclusive)
X0, X1, Y0, Y1 = -46, 46, -70, 42
VILLAGE_BOUNDS = (-28, -28, 28, 28)  # the built-up area (x0, y0, x1, y1)

REQUIRED_ANCHORS = (
    ["bell", "bell_ringer", "square_n", "square_e", "square_s", "square_w",
     "house_a_door_out", "house_a_door_in", "house_a_cam"]
    + ["house_a_inside_%d" % i for i in (1, 2, 3)] + ["house_a_bed_%d" % i for i in (1, 2, 3)]
    + ["farm_work", "farm_station", "library_work", "library_station", "smithy_work", "smithy_station"]
    + ["cell_%d" % i for i in range(1, 7)] + ["hall_aisle_start", "hall_aisle_end"]
    + ["exit_gate", "meadow_far", "nitwit_idle"]
)
REQUIRED_PATHS = ["square_to_house_a", "square_to_house_b", "square_to_house_c", "exit_road"]
REQUIRED_DOORS = ["house_a", "house_b", "house_c", "house_d", "house_e"]

_SIDE_YAW = {"s": 0.0, "e": math.pi / 2, "n": math.pi, "w": -math.pi / 2}  # door/prop rotation for an outside dir
_SIDE_VEC = {"s": (0, -1), "n": (0, 1), "e": (1, 0), "w": (-1, 0)}


def yaw_to(src, dst):
    """Yaw (radians about Z) that makes a character standing at src (who faces -Y at yaw 0) face dst."""
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    return math.atan2(dx, -dy)


class Village:
    """Handle to the built set. See the module docstring and CONTRACT.md."""

    def __init__(self):
        self.collection = None
        self.anchors = {}        # name -> (x, y, z): standing spots (z = ground) and look targets
        self.paths = {}          # name -> [(x, y, z), ...] walkable polylines
        self.doors = {}          # name -> door hinge Object
        self.bell = None         # swing pivot Object (rotate about local X)
        self.bell_frame = None
        self.lantern_lights = []  # point-light Objects of every lantern
        self.lanterns = {}       # name -> lantern Object (its light is named "lantern_light.<name>")
        self.fire_lights = []    # small orange lights of lit furnaces
        self.yaws = {}           # name -> suggested facing yaw for a character on that anchor
        self.beds = {}           # name -> dict(pos=centre on top of the blanket, head=pillow centre, yaw=lying yaw)
        self.objects = []        # every Object of the set
        self.bounds = VILLAGE_BOUNDS
        self.terrain_bounds = (X0, Y0, X1 + 1, Y1 + 1)
        self.face_count = 0
        self._height = None

    def ground(self, x, y):
        """Ground height (z of the walkable surface) at world position (x, y)."""
        ix = int(np.clip(math.floor(x), X0, X1)) - X0
        iy = int(np.clip(math.floor(y), Y0, Y1)) - Y0
        return float(self._height[ix, iy])

    def door_open(self, name, frame, open=True, frames=5):
        """Keyframe door `name` swinging open (or shut with open=False) from `frame` over `frames` frames."""
        d = self.doors[name]
        closed, opened = d["closed_rz"], d["open_rz"]
        a, b = (closed, opened) if open else (opened, closed)
        d.rotation_euler[2] = a
        d.keyframe_insert("rotation_euler", index=2, frame=frame)
        d.rotation_euler[2] = b
        d.keyframe_insert("rotation_euler", index=2, frame=frame + max(1, frames))

    def set_door(self, name, open=True):
        """Set a door open or shut immediately, without keyframes."""
        d = self.doors[name]
        d.rotation_euler[2] = d["open_rz"] if open else d["closed_rz"]

    def ring_bell(self, frame, strength=1.0, swings=5):
        """Keyframe a decaying bell swing starting at `frame` (first swing goes toward +Y, away from the ringer)."""
        bell = self.bell
        clapper = bell.children[0] if bell.children else None
        period = 20.0
        amp = math.radians(27.0) * strength
        decay = 0.72

        def key(f, a):
            bell.rotation_euler[0] = a
            bell.keyframe_insert("rotation_euler", index=0, frame=f)
            if clapper is not None:
                clapper.rotation_euler[0] = max(-0.24, min(0.24, -0.55 * a))
                clapper.keyframe_insert("rotation_euler", index=0, frame=f + 2)

        key(frame, 0.0)
        n = max(1, int(swings)) * 2
        for k in range(n):
            f = frame + period * (0.25 + 0.5 * k)
            key(f, amp * (decay ** k) * (1 if k % 2 == 0 else -1))
        key(frame + period * (0.25 + 0.5 * n), 0.0)
        return int(frame + period * (0.25 + 0.5 * n))

    def set_lantern_energy(self, watts, names=None):
        """Set the power of all lantern lights (or only those whose lantern name is in `names`)."""
        for name, lan in self.lanterns.items():
            if names is None or name in names:
                light = props.lantern_light(lan)
                if light is not None:
                    light.data.energy = watts

    def validate(self):
        """Return a list of missing required anchors / paths / doors (empty when the set is complete)."""
        missing = ["anchor:" + a for a in REQUIRED_ANCHORS if a not in self.anchors]
        missing += ["path:" + p for p in REQUIRED_PATHS if p not in self.paths]
        missing += ["door:" + d for d in REQUIRED_DOORS if d not in self.doors]
        if self.bell is None:
            missing.append("bell")
        if not self.lantern_lights:
            missing.append("lantern_lights")
        return missing


# --------------------------------------------------------------------------------------------------
# builder
# --------------------------------------------------------------------------------------------------


def _smooth_noise(r, nx, ny, cell):
    """Tile-free smooth value noise in 0..1 on an nx x ny grid with features about `cell` blocks wide."""
    gx, gy = nx // cell + 3, ny // cell + 3
    g = r.random((gx, gy))
    xs = np.arange(nx) / cell
    ys = np.arange(ny) / cell
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    fx = xs - x0
    fy = ys - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    a = g[np.ix_(x0, y0)]
    b = g[np.ix_(x0 + 1, y0)]
    c = g[np.ix_(x0, y0 + 1)]
    d = g[np.ix_(x0 + 1, y0 + 1)]
    fx = fx[:, None]
    fy = fy[None, :]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


class _Builder:
    def __init__(self, scene, seed):
        self.scene = scene
        self.r = pix.rng(seed)
        self.w = World()
        self.v = Village()
        coll = bpy.data.collections.new("village")
        scene.collection.children.link(coll)
        self.v.collection = coll
        self.coll = coll
        self.reserved = set()   # (x, y) columns where no grass / flowers / trees may be scattered
        self.H = None

    # ---- small helpers ---------------------------------------------------------------------------

    def h(self, x, y):
        """Terrain height at block column (x, y)."""
        return int(self.H[x - X0, y - Y0])

    def reserve(self, x0, y0, x1, y1):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                self.reserved.add((x, y))

    def anchor(self, name, x, y, z=None, yaw=None, face=None):
        if z is None:
            z = self.h(int(math.floor(x)), int(math.floor(y)))
        self.v.anchors[name] = (float(x), float(y), float(z))
        if face is not None:
            yaw = yaw_to((x, y), face)
        if yaw is not None:
            self.v.yaws[name] = float(yaw)

    def place(self, obj, x, y, z=0.0, rot=0.0, name=None):
        obj.location = (x, y, z)
        obj.rotation_euler = (0, 0, rot)
        if name:
            obj.name = name
        return obj

    def lantern(self, name, x, y, z, hanging=True):
        """Lantern in block cell (x, y, z)."""
        lan = props.make_lantern(hanging, self.coll)
        self.place(lan, x + 0.5, y + 0.5, z, name="lantern." + name)
        light = props.lantern_light(lan)
        light.name = "lantern_light." + name
        light.data.name = "lantern_light." + name
        self.v.lanterns[name] = lan
        self.v.lantern_lights.append(light)
        return lan

    def lantern_post(self, name, x, y, arm="e"):
        """Stone-footed fence post with an arm and a hanging lantern (arm = n/e/s/w)."""
        w = self.w
        dx, dy = _SIDE_VEC[arm]
        w.set(x, y, 0, "cobble_wall")
        w.set(x, y, 1, "dark_fence")
        w.set(x, y, 2, "dark_fence")
        w.set(x, y, 3, "dark_fence")
        w.set(x + dx, y + dy, 3, "dark_fence")
        self.lantern(name, x + dx, y + dy, 2)
        self.reserve(x, y, x, y)
        self.reserve(x + dx, y + dy, x + dx, y + dy)

    def door(self, name, x, y, side, mirror=False):
        """Door in wall cell (x, y) whose outside is `side`; cleared two blocks high."""
        w = self.w
        w.set(x, y, 0, None)
        w.set(x, y, 1, None)
        th = _SIDE_YAW[side]
        d = props.make_door(mirror=mirror, collection=self.coll)
        lx, ly = (0.5 if mirror else -0.5), -0.5 + 3 / 16
        c, s = math.cos(th), math.sin(th)
        self.place(d, x + 0.5 + lx * c - ly * s, y + 0.5 + lx * s + ly * c, 0.0, th, "door." + name)
        d["closed_rz"] = th
        d["open_rz"] = th + d["open_angle"]
        self.v.doors[name] = d
        ox, oy = _SIDE_VEC[side]
        self.anchor(name + "_door_out", x + 0.5 + ox * 1.1, y + 0.5 + oy * 1.1, 0.0, face=(x + 0.5, y + 0.5))
        self.anchor(name + "_door_in", x + 0.5 - ox * 1.2, y + 0.5 - oy * 1.2, 0.0,
                    face=(x + 0.5 - ox * 3, y + 0.5 - oy * 3))
        return d

    def bed(self, name, x, y, head, color):
        """Bed whose FOOT is in cell (x, y) and whose pillow end lies one cell toward `head` (n/e/s/w)."""
        rot = {"n": 0.0, "w": math.pi / 2, "s": math.pi, "e": -math.pi / 2}[head]
        b = props.make_bed(color, self.coll)
        self.place(b, x + 0.5, y + 0.5, 0.0, rot, "bed." + name)
        hx, hy = _SIDE_VEC[head]
        cx, cy = x + 0.5 + hx * 0.5, y + 0.5 + hy * 0.5
        self.v.anchors[name] = (cx, cy, props.BED_TOP)
        self.v.anchors[name + "_head"] = (x + 0.5 + hx * 1.1, y + 0.5 + hy * 1.1, props.BED_TOP)
        # a sleeper lies with the head on the pillow, feet pointing away from it
        self.v.beds[name] = dict(pos=(cx, cy, props.BED_TOP), head=self.v.anchors[name + "_head"],
                                 foot=(x + 0.5 - hx * 0.4, y + 0.5 - hy * 0.4, props.BED_TOP),
                                 yaw=yaw_to((0, 0), (hx, hy)), head_dir=(hx, hy))
        self.v.yaws[name] = self.v.beds[name]["yaw"]
        return b

    # ---- terrain ----------------------------------------------------------------------------------

    def terrain(self):
        r = self.r
        nx, ny = X1 - X0 + 1, Y1 - Y0 + 1
        xs = np.arange(X0, X1 + 1)[:, None] * np.ones((1, ny))
        ys = np.arange(Y0, Y1 + 1)[None, :] * np.ones((nx, 1))
        flat = np.zeros((nx, ny), bool)
        rects = [(-6, -6, 6, 7), (-3, -38, 3, -5), (-6, 7, 5, 19), (7, -5, 16, 5), (-16, -5, -7, 4),
                 (1, -18, 10, -8), (-10, -21, -1, -12), (15, -11, 29, 9), (4, 3, 19, 8), (6, 6, 18, 18),
                 (-17, 6, -6, 16), (-12, -12, -4, -4), (4, -9, 11, -4), (-18, -24, -12, -15)]
        for (a, b, c, d) in rects:
            flat[a - X0 : c - X0 + 1, b - Y0 : d - Y0 + 1] = True
        dist = np.where(flat, 0, 99).astype(float)
        for _ in range(14):
            m = dist.copy()
            for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                sh = np.roll(np.roll(dist, sx, 0), sy, 1) + 1
                m = np.minimum(m, sh)
            dist = m
        f = np.clip((dist - 1.0) / 6.0, 0, 1)
        n1 = _smooth_noise(r, nx, ny, 13)
        n2 = _smooth_noise(r, nx, ny, 6)
        bumps = np.clip(2.6 * n1 + 1.1 * n2 - 1.25, 0, None)
        north = np.clip((ys - 21) / 4.5, 0, 4.2)
        south = np.clip((-34 - ys) / 5.5, 0, 3.2)
        sides = np.clip((np.abs(xs) - 31) / 6.0, 0, 2.0)
        corridor = (np.abs(xs - 0.5) <= 4.5) & (ys < -20)
        calm = np.where(ys < -21, np.clip((np.abs(xs - 0.5) - 9.0) / 9.0, 0, 1), 1.0)  # wide flat meadow floor
        raw = f * (bumps * calm + north + sides) + south
        raw = np.where(corridor, south, raw)
        H = np.floor(raw + 0.35).astype(int)
        for _ in range(3):  # no cliffs: neighbours differ by at most one block
            m = H.copy()
            for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                m = np.minimum(m, np.roll(np.roll(H, sx, 0), sy, 1) + 1)
            H = m
        H[flat] = 0
        H[0, :] = np.minimum(H[0, :], H[1, :])
        self.H = H
        self.v._height = H
        w = self.w
        for ix in range(nx):
            for iy in range(ny):
                x, y, hh = ix + X0, iy + Y0, int(H[ix, iy])
                lo = hh
                for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    jx, jy = ix + sx, iy + sy
                    if 0 <= jx < nx and 0 <= jy < ny:
                        lo = min(lo, int(H[jx, jy]))
                    else:
                        lo = min(lo, 0)
                zb = min(hh - 1, lo)
                top = "grass" if dist[ix, iy] <= 1 else "meadow"
                for z in range(zb, hh):
                    w.set(x, y, z, top if z == hh - 1 else "dirt")
                w.skip_bottom.add((x, y, zb))

    def ground_set(self, x, y, name, z=-1):
        self.w.set(x, y, z, name)

    def path_rect(self, x0, y0, x1, y1, ragged=0.0):
        r = self.r
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                edge = x in (x0, x1) or y in (y0, y1)
                if edge and ragged and r.random() < ragged:
                    continue
                self.path_cell(x, y)

    def path_cell(self, x, y):
        z = self.h(x, y) - 1
        k = pos_hash(x, y, 7) % 100
        name = "path" if k < 93 else ("coarse_dirt" if k < 98 else "gravel")
        self.w.set(x, y, z, name)
        self.reserved.add((x, y))

    # ---- square -----------------------------------------------------------------------------------

    def square(self):
        w = self.w
        self.path_rect(-4, -4, 4, 4)
        for cx, cy in ((-4, -4), (4, -4), (-4, 4), (4, 4)):
            w.set(cx, cy, -1, "grass")
            self.reserved.discard((cx, cy))
        for x in range(-1, 2):
            for y in range(-1, 2):
                k = pos_hash(x, y, 3) % 10
                w.set(x, y, -1, "mossy_cobble" if k < 3 else "cobble")
        w.set(0, 0, -1, "stone_bricks")
        self.reserve(-4, -4, 4, 4)
        frame = props.make_bell_frame(self.coll)
        self.place(frame, 0.5, 0.5, 0.0, name="bell_frame")
        bell = props.make_bell(self.coll)
        self.place(bell, 0.5, 0.5, props.BELL_PIVOT_Z, name="bell")
        self.v.bell = bell
        self.v.bell_frame = frame
        self.anchor("bell", 0.5, 0.5, props.BELL_PIVOT_Z - 0.5)
        self.anchor("bell_base", 0.5, 0.5, 0.0)
        self.anchor("bell_ringer", 0.5, -0.5, 0.0, face=(0.5, 0.5))
        self.anchor("square_n", 0.5, 3.5, 0.0, face=(0.5, 0.5))
        self.anchor("square_s", 0.5, -2.5, 0.0, face=(0.5, 0.5))
        self.anchor("square_e", 3.5, 0.5, 0.0, face=(0.5, 0.5))
        self.anchor("square_w", -2.5, 0.5, 0.0, face=(0.5, 0.5))
        # roads
        self.path_rect(-1, 5, 1, 7)
        self.path_rect(5, -1, 8, 1)
        self.path_rect(-8, -1, -5, 1)
        self.path_rect(-1, -24, 1, -5)
        # the exit road frays into the meadow
        r = self.r
        for y in range(-37, -24):
            t = (-24 - y) / 13.0
            for x in range(-1, 2):
                if r.random() > t * (1.15 if x else 0.8):
                    self.path_cell(x, y)
        # lane to the trading hall and the east lane in front of it
        self.path_rect(5, 5, 18, 6, ragged=0.12)
        self.path_rect(17, -9, 18, 7, ragged=0.1)
        self.path_rect(19, -9, 19, -8)
        self.path_rect(6, 2, 7, 4)
        # short spurs
        self.path_rect(-6, 5, -5, 8, ragged=0.2)
        self.path_rect(-8, 8, -7, 9, ragged=0.2)
        self.path_rect(-6, -6, -5, -5)
        self.path_rect(2, -13, 2, -12)
        self.path_rect(-2, -16, -2, -15)
        self.path_rect(12, 7, 12, 7)

    # ---- houses -----------------------------------------------------------------------------------

    def gable_roof(self, x0, y0, x1, y1, wall_h, ridge, mat, fill):
        """Stair roof with one block of overhang. ridge = 'x' or 'y' (the axis the ridge runs along)."""
        w = self.w
        if ridge == "y":
            c0, c1, a0, a1 = x0 - 1, x1 + 1, y0 - 1, y1 + 1
        else:
            c0, c1, a0, a1 = y0 - 1, y1 + 1, x0 - 1, x1 + 1
        width = c1 - c0 + 1
        top = 0
        for c in range(c0, c1 + 1):
            i = min(c - c0, c1 - c)
            z = wall_h - 1 + i
            top = max(top, z)
            mid = width % 2 == 1 and (c - c0) == (c1 - c)
            if mid:
                name = mat + "_slab"
            elif ridge == "y":
                name = mat + "_stairs_" + ("e" if (c - c0) < (c1 - c) else "w")
            else:
                name = mat + "_stairs_" + ("n" if (c - c0) < (c1 - c) else "s")
            for a in range(a0, a1 + 1):
                if ridge == "y":
                    w.set(c, a, z, name)
                else:
                    w.set(a, c, z, name)
            lo_c, hi_c = (x0, x1) if ridge == "y" else (y0, y1)
            if lo_c <= c <= hi_c:
                for z2 in range(wall_h, z):
                    if ridge == "y":
                        w.set(c, y0, z2, fill)
                        w.set(c, y1, z2, fill)
                    else:
                        w.set(x0, c, z2, fill)
                        w.set(x1, c, z2, fill)
        return top

    def hip_roof(self, x0, y0, x1, y1, wall_h, mat):
        """Stepped hip roof of half slabs rising half a block per ring, one block of overhang."""
        w = self.w
        ax0, ay0, ax1, ay1 = x0 - 1, y0 - 1, x1 + 1, y1 + 1
        k = 0
        while ax0 <= ax1 and ay0 <= ay1:
            z = wall_h - 1 + (k + 1) // 2
            name = mat + ("_slab_top" if k % 2 == 0 else "_slab")
            thin = (ax1 - ax0) < 2 or (ay1 - ay0) < 2
            for x in range(ax0, ax1 + 1):
                for y in range(ay0, ay1 + 1):
                    if thin or x in (ax0, ax1) or y in (ay0, ay1):
                        w.set(x, y, z, name)
            ax0, ay0, ax1, ay1 = ax0 + 1, ay0 + 1, ax1 - 1, ay1 - 1
            k += 1

    def house_shell(self, x0, y0, x1, y1, wall_h=3, base="cobble", wall="oak_planks", post="oak_log",
                    floor="oak_planks", top_beam=False, mid_posts=False):
        """Floor, walls and corner posts of a rectangular house (no roof, no openings)."""
        w = self.w
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                border = x in (x0, x1) or y in (y0, y1)
                corner = x in (x0, x1) and y in (y0, y1)
                w.set(x, y, -1, "cobble" if border else floor)
                if not border:
                    continue
                along_x = y in (y0, y1)
                for z in range(wall_h):
                    if corner:
                        name = post
                    elif z == 0:
                        name = base
                        if base == "cobble" and pos_hash(x, y, z, 5) % 100 < 22:
                            name = "mossy_cobble"
                    elif top_beam and z == wall_h - 1:
                        name = "oak_log_x" if along_x else "oak_log_y"
                    elif mid_posts and ((x - x0) % 3 == 0 if along_x else (y - y0) % 3 == 0):
                        name = post
                    else:
                        name = wall
                    w.set(x, y, z, name)
        self.reserve(x0 - 1, y0 - 1, x1 + 1, y1 + 1)

    def windows(self, cells, name="glass_pane"):
        for (x, y, z) in cells:
            self.w.set(x, y, z, name)

    def house_a(self):
        """The big house north of the square: interior 6 x 8, three beds on the east wall, door south."""
        w = self.w
        x0, y0, x1, y1 = -4, 8, 3, 17
        self.house_shell(x0, y0, x1, y1, wall_h=3, mid_posts=False)
        self.gable_roof(x0, y0, x1, y1, 3, "y", "dark", "oak_planks")
        # front gable trim: a log tie-beam across the front and back walls
        for x in range(x0 + 1, x1):
            w.set(x, y0, 2, "oak_log_x")
            w.set(x, y1, 2, "oak_log_x")
        self.windows([(-2, 8, 1), (2, 8, 1), (-4, 11, 1), (-4, 14, 1), (3, 11, 1), (3, 13, 1), (-1, 17, 1),
                      (-1, 8, 4), (0, 8, 4)])
        self.door("house_a", 0, 8, "s")
        # tie beams and lanterns
        for y in (11, 14):
            for x in range(x0 + 1, x1):
                w.set(x, y, 3, "oak_log_x")
        self.lantern("house_a_in", -1, 11, 2)
        self.lantern("house_a_in_2", -1, 14, 2)
        self.lantern("house_a_eave", 2, 7, 2)   # hangs under the front roof overhang, right of the door
        w.set(2, 7, 3, "dark_fence")
        # beds: feet at x = 1, pillows against the east wall
        colors = ("red", "blue", "yellow")
        for i, y in enumerate((10, 12, 14)):
            self.bed("house_a_bed_%d" % (i + 1), 1, y, "e", colors[i])
        self.anchor("house_a_inside_1", -0.4, 10.4, 0.0, face=(0.5, 8.5))
        self.anchor("house_a_inside_2", -1.6, 12.2, 0.0, face=(0.5, 8.5))
        self.anchor("house_a_inside_3", 0.2, 13.5, 0.0, face=(0.5, 8.5))
        self.anchor("house_a_cam", 2.45, 16.45, 0.0, face=(0.5, 8.5))
        self.anchor("house_a_cam_door", 0.5, 9.3, 0.0, face=(1.5, 14.5))
        self.anchor("house_a_center", -0.5, 12.5, 0.0)
        # furniture on the west side
        self.place(props.make_barrel(self.coll), -1.5, 16.5, 0.0, name="house_a_barrel")
        w.set(-3, 15, 0, "bookshelf")
        w.set(-3, 15, 1, "bookshelf")
        w.set(-3, 16, 0, "bookshelf")
        w.set(-3, 9, 0, "oak_fence")
        w.set(-3, 9, 1, "oak_plate")
        w.set(-2, 12, 0, "carpet_red")
        w.set(-1, 12, 0, "carpet_red")
        w.set(-2, 13, 0, "carpet_red")
        w.set(-1, 13, 0, "carpet_red")
        self.v.paths["square_to_house_a"] = [(1.6, 1.9, 0.0), (0.5, 4.5, 0.0), (0.5, 7.2, 0.0), (0.5, 9.9, 0.0)]
        self.v.paths["house_a_in_1"] = [(0.5, 7.2, 0.0), (0.5, 9.6, 0.0), (-0.4, 10.4, 0.0)]
        self.v.paths["house_a_in_2"] = [(0.5, 7.2, 0.0), (0.4, 9.6, 0.0), (-1.6, 12.2, 0.0)]
        self.v.paths["house_a_in_3"] = [(0.5, 7.2, 0.0), (0.3, 9.6, 0.0), (0.2, 13.5, 0.0)]

    def house_b(self):
        """Tall cobble-and-plank house east of the square, door west under the eave."""
        w = self.w
        x0, y0, x1, y1 = 9, -3, 14, 3
        self.house_shell(x0, y0, x1, y1, wall_h=5, wall="oak_planks")
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                border = x in (x0, x1) or y in (y0, y1)
                corner = x in (x0, x1) and y in (y0, y1)
                if border and not corner:
                    w.set(x, y, 1, "mossy_cobble" if pos_hash(x, y, 1, 9) % 100 < 18 else "cobble")
                    w.set(x, y, 2, "oak_log_x" if y in (y0, y1) else "oak_log_y")
        self.gable_roof(x0, y0, x1, y1, 5, "y", "spruce", "oak_planks")
        self.windows([(9, -2, 1), (9, 2, 1), (9, -1, 3), (9, 1, 3), (14, 0, 1), (14, -1, 3), (14, 1, 3),
                      (11, -3, 3), (12, -3, 3), (11, 3, 3), (12, 3, 3), (12, 3, 1)])
        self.door("house_b", 9, 0, "w")
        for x in range(x0 + 1, x1):
            w.set(x, 0, 5, "oak_log_x")
        self.lantern("house_b_in", 12, 0, 4)
        self.lantern("house_b_eave", 8, -1, 3)
        self.bed("house_b_bed", 13, 1, "n", "green")
        self.anchor("house_b_inside", 11.5, -0.8, 0.0, face=(9.5, 0.5))
        self.place(props.make_barrel(self.coll), 13.5, -1.5, 0.0, name="house_b_barrel")
        w.set(10, 2, 0, "bookshelf")
        self.v.paths["square_to_house_b"] = [(2.2, -1.2, 0.0), (5.0, 0.5, 0.0), (7.8, 0.5, 0.0), (10.9, 0.5, 0.0)]

    def house_c(self):
        """White-plastered timber cottage west of the square, gable and door facing east."""
        w = self.w
        x0, y0, x1, y1 = -14, -3, -9, 2
        self.house_shell(x0, y0, x1, y1, wall_h=3, wall="terracotta_white", top_beam=True)
        self.gable_roof(x0, y0, x1, y1, 3, "x", "dark", "terracotta_white")
        self.windows([(-9, -2, 1), (-9, 1, 1), (-12, -3, 1), (-11, 2, 1), (-14, 0, 1), (-9, -1, 4), (-9, 0, 4)])
        self.door("house_c", -9, 0, "e")
        w.set(-9, -1, 2, "oak_log_y")
        for y in range(y0 + 1, y1):
            w.set(-12, y, 3, "oak_log_y")
        self.lantern("house_c_in", -12, -1, 2)
        self.lantern("house_c_eave", -8, 1, 2)
        w.set(-8, 1, 3, "dark_fence")
        self.bed("house_c_bed", -13, 0, "n", "cyan")
        self.anchor("house_c_inside", -11.2, -0.8, 0.0, face=(-8.5, 0.5))
        w.set(-13, -2, 0, "hay")
        self.place(props.make_barrel(self.coll), -10.5, -1.5, 0.0, name="house_c_barrel")
        self.v.paths["square_to_house_c"] = [(-1.2, 1.7, 0.0), (-4.0, 0.5, 0.0), (-6.8, 0.5, 0.0), (-9.9, 0.5, 0.0)]

    def house_d(self):
        """Squat oak house with a stepped slab roof, south-east on the exit road, door west."""
        w = self.w
        x0, y0, x1, y1 = 3, -16, 8, -10
        self.house_shell(x0, y0, x1, y1, wall_h=3, wall="spruce_planks", base="stone_bricks")
        self.hip_roof(x0, y0, x1, y1, 3, "cobble")
        self.windows([(3, -15, 1), (3, -11, 1), (6, -10, 1), (8, -13, 1), (5, -16, 1)])
        self.door("house_d", 3, -13, "w")
        self.lantern("house_d_in", 6, -13, 2)
        for x in range(4, 8):
            w.set(x, -13, 3, "oak_log_x")
        w.set(2, -11, 0, "cobble_wall")
        self.lantern("house_d_eave", 2, -11, 1, hanging=False)
        self.reserve(2, -11, 2, -11)
        self.bed("house_d_bed", 7, -12, "n", "orange")
        self.anchor("house_d_inside", 5.5, -13.5, 0.0, face=(3.5, -12.5))
        self.place(props.make_cartography_table(self.coll), 4.5, -14.5, 0.0, name="house_d_table")
        self.v.paths["square_to_house_d"] = [(1.5, -2.0, 0.0), (0.9, -8.0, 0.0), (1.0, -12.4, 0.0),
                                             (2.0, -12.5, 0.0), (4.9, -12.5, 0.0)]

    def house_e(self):
        """Cobblestone cottage with an oak stair roof, south-west on the exit road, door east."""
        w = self.w
        x0, y0, x1, y1 = -8, -19, -3, -14
        self.house_shell(x0, y0, x1, y1, wall_h=3, wall="cobble", base="cobble")
        for x in range(x0 + 1, x1):
            for y in (y0, y1):
                for z in (1, 2):
                    if pos_hash(x, y, z, 4) % 100 < 20:
                        w.set(x, y, z, "mossy_cobble")
        self.gable_roof(x0, y0, x1, y1, 3, "x", "oak", "oak_planks")
        self.windows([(-3, -18, 1), (-3, -15, 1), (-8, -17, 1), (-6, -14, 1), (-5, -19, 1), (-3, -17, 4),
                      (-3, -16, 4)])
        self.door("house_e", -3, -16, "e", mirror=True)
        for y in range(y0 + 1, y1):
            w.set(-6, y, 3, "oak_log_y")
        self.lantern("house_e_in", -6, -16, 2)
        self.lantern("house_e_eave", -2, -18, 2)
        w.set(-2, -18, 3, "dark_fence")
        self.bed("house_e_bed", -7, -17, "n", "purple")
        self.anchor("house_e_inside", -5.4, -16.6, 0.0, face=(-2.5, -15.5))
        self.place(props.make_barrel(self.coll), -4.5, -17.5, 0.0, name="house_e_barrel")
        self.v.paths["square_to_house_e"] = [(-0.6, -2.2, 0.0), (0.1, -9.0, 0.0), (-0.2, -15.3, 0.0),
                                             (-1.9, -15.5, 0.0), (-4.9, -15.5, 0.0)]

    # ---- workstations -----------------------------------------------------------------------------

    def farm(self):
        w = self.w
        fx0, fy0, fx1, fy1 = 8, 8, 16, 16
        for x in range(fx0, fx1 + 1):
            for y in range(fy0, fy1 + 1):
                if x in (fx0, fx1) or y in (fy0, fy1):
                    w.set(x, y, 0, "oak_fence")
        w.set(12, 8, 0, None)  # gate gap
        r = self.r
        for x in range(9, 16):
            w.set(x, 9, -1, "path" if pos_hash(x, 9, 2) % 5 else "coarse_dirt")
            for y in range(10, 16):
                if y == 13:
                    w.set(x, y, -1, "water")
                    w.set(x, y, -2, "dirt")
                    self.w.skip_bottom.add((x, y, -2))
                    continue
                w.set(x, y, -1, "farmland")
                near = 3 - abs(y - 13)
                stage = int(np.clip(7 - r.integers(0, 3) - (1 if near < 1 and r.random() < 0.3 else 0), 2, 7))
                if x >= 14 and y >= 14:
                    stage = int(r.integers(1, 4))
                w.set(x, y, 0, "wheat_%d" % stage)
        self.reserve(fx0 - 1, fy0 - 1, fx1 + 1, fy1 + 1)
        comp = props.make_composter(0.7, self.coll)
        self.place(comp, 10.5, 9.5, 0.0, name="farm_composter")
        self.anchor("farm_station", 10.5, 9.5, 0.9)
        self.anchor("farm_work", 11.6, 9.5, 0.0, face=(10.5, 9.5))
        self.anchor("farm_gate", 12.5, 7.5, 0.0)
        w.set(14, 9, 0, "hay")
        w.set(15, 9, 0, "hay")
        w.set(15, 9, 1, "hay")
        w.set(17, 9, 0, "hay")
        self.place(props.make_barrel(self.coll), 17.5, 10.5, 0.0, name="farm_barrel")
        self.lantern_post("farm", 13, 7, "e")
        self.v.paths["square_to_farm"] = [(3.5, 3.0, 0.0), (6.5, 5.6, 0.0), (12.5, 5.8, 0.0), (12.5, 8.4, 0.0),
                                          (11.6, 9.5, 0.0)]

    def library(self):
        """Open-sided reading corner: bookshelf walls on the north and west, roof on posts, lectern, carpet."""
        w = self.w
        x0, y0, x1, y1 = -14, 9, -9, 13
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                w.set(x, y, -1, "spruce_planks")
        for x in range(x0, x1 + 1):
            for z in range(3):
                w.set(x, y1, z, "cobble" if z == 0 else "oak_planks")
        for y in range(y0, y1 + 1):
            for z in range(3):
                w.set(x0, y, z, "cobble" if z == 0 else "oak_planks")
        for cx, cy in ((x0, y0), (x0, y1), (x1, y1), (x1, y0)):
            for z in range(3):
                w.set(cx, cy, z, "oak_log")
        for x in range(x0 + 1, x1):
            w.set(x, y1 - 1, 0, "bookshelf")
            w.set(x, y1 - 1, 1, "bookshelf")
            if x % 2:
                w.set(x, y1 - 1, 2, "bookshelf")
        for y in range(y0 + 1, y1 - 1):
            w.set(x0 + 1, y, 0, "bookshelf")
            w.set(x0 + 1, y, 1, "bookshelf")
        w.set(x0, y0 + 2, 1, "glass_pane")
        # lean-to roof of half slabs rising to the north; walls are carried up to meet it
        roof = {y0 - 1: (3, "spruce_slab"), y0: (3, "spruce_slab_top"), y0 + 1: (4, "spruce_slab"),
                y0 + 2: (4, "spruce_slab_top"), y0 + 3: (5, "spruce_slab"), y0 + 4: (5, "spruce_planks"),
                y0 + 5: (5, "spruce_slab_top")}
        for y, (z, name) in roof.items():
            for x in range(x0 - 1, x1 + 2):
                w.set(x, y, z, name)
        for x in range(x0, x1 + 1):
            for z in (3, 4):
                w.set(x, y1, z, "oak_planks")
        for y in range(y0, y1):
            z, name = roof[y]
            for z2 in range(3, z):
                w.set(x0, y, z2, "oak_planks")
            if name.endswith("slab_top"):
                w.set(x0, y, z, "spruce_planks")
        w.set(x1, y0, 3, "oak_log")
        for z in (3, 4):
            w.set(x1, y1, z, "oak_log")
            w.set(x0, y1, z, "oak_log")
        for x, y in ((-12, 10), (-11, 10), (-12, 11), (-10, 10), (-10, 11)):
            w.set(x, y, 0, "carpet_red")
        lect = props.make_lectern(self.coll)
        self.place(lect, -10.5, 11.5, 0.0, name="library_lectern")
        self.anchor("library_station", -10.5, 11.5, 1.0)
        self.anchor("library_work", -10.5, 10.45, 0.0, face=(-10.5, 11.5))
        self.lantern("library", -12, 10, 3)
        self.reserve(x0 - 1, y0 - 1, x1 + 1, y1 + 1)
        self.v.paths["square_to_library"] = [(-2.5, 3.0, 0.0), (-5.5, 6.5, 0.0), (-7.5, 8.6, 0.0),
                                             (-10.5, 9.2, 0.0), (-10.5, 10.45, 0.0)]

    def smithy(self):
        """Open smithy shelter: cobble floor, stone back walls and chimney, furnace, smithing table."""
        w = self.w
        x0, y0, x1, y1 = -10, -10, -6, -6
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                k = pos_hash(x, y, 11) % 10
                w.set(x, y, -1, "stone_bricks" if k < 4 else ("cobble" if k < 9 else "mossy_cobble"))
        for x in range(x0, x1 + 1):
            for z in range(3):
                w.set(x, y0, z, "cobble" if (z or pos_hash(x, y0, z, 2) % 4) else "mossy_cobble")
        for y in range(y0, y1 + 1):
            for z in range(2 if y > y0 + 2 else 3):
                w.set(x0, y, z, "cobble" if pos_hash(x0, y, z, 2) % 5 else "mossy_cobble")
        w.set(x0, y1, 0, None)
        w.set(x0, y1, 1, None)
        for z in range(3):
            w.set(x1, y1, z, "oak_log")
            w.set(x0, y1, z, "oak_log")
            w.set(x1, y0, z, "oak_log")
        for z in range(3, 7):
            w.set(x0, y0, z, "cobble")
            if z < 5:
                w.set(x0 + 1, y0, z, "cobble")
        w.set(x0, y0, 7, "cobble_wall")
        for x in range(x0 - 1, x1 + 2):
            for y in range(y0 - 1, y1 + 2):
                if w.get(x, y, 3) is None:
                    inner = x0 <= x <= x1 and y0 <= y <= y1
                    w.set(x, y, 3, "stone_bricks_slab" if not inner else "spruce_slab")
        fur = props.make_blast_furnace(True, self.coll)
        self.place(fur, -8.5, -8.5, 0.0, math.pi, "smithy_furnace")
        for ch in fur.children:
            if ch.type == "LIGHT":
                self.v.fire_lights.append(ch)
        self.place(props.make_smithing_table(self.coll), -7.5, -8.5, 0.0, math.pi, "smithy_table")
        self.place(props.make_barrel(self.coll), -6.5, -8.5, 0.0, name="smithy_barrel")
        self.anchor("smithy_station", -8.5, -8.5, 0.9)
        self.anchor("smithy_work", -8.3, -7.35, 0.0, face=(-8.5, -8.5))
        self.lantern("smithy", -7, -7, 2)
        self.reserve(x0 - 1, y0 - 1, x1 + 1, y1 + 1)
        self.v.paths["square_to_smithy"] = [(-2.5, -2.0, 0.0), (-5.2, -5.2, 0.0), (-7.0, -6.6, 0.0),
                                            (-8.3, -7.35, 0.0)]

    def well(self):
        w = self.w
        x0, y0 = 7, -7
        for x in range(x0, x0 + 3):
            for y in range(y0, y0 + 3):
                edge = not (x == x0 + 1 and y == y0 + 1)
                if edge:
                    w.set(x, y, -1, "cobble")
                    w.set(x, y, 0, "mossy_cobble" if pos_hash(x, y, 0, 6) % 3 == 0 else "cobble")
                else:
                    w.set(x, y, -1, "water")
                    w.set(x, y, 0, "water")
                    w.set(x, y, -2, "cobble")
                    w.skip_bottom.add((x, y, -2))
        for cx, cy in ((x0, y0), (x0 + 2, y0 + 2), (x0, y0 + 2), (x0 + 2, y0)):
            w.set(cx, cy, 1, "oak_fence")
            w.set(cx, cy, 2, "oak_fence")
        for x in range(x0, x0 + 3):
            for y in range(y0, y0 + 3):
                w.set(x, y, 3, "spruce_slab")
        w.set(x0 + 1, y0 + 1, 3, "spruce_planks")
        self.reserve(x0 - 1, y0 - 1, x0 + 3, y0 + 3)
        self.anchor("well", x0 + 1.5, y0 - 0.6, 0.0, face=(x0 + 1.5, y0 + 1.5))

    # ---- trading hall -----------------------------------------------------------------------------

    def hall(self):
        """Roofed row of six 1x1 cells (x = 25) behind workstations (x = 24), aisle x = 21..23, open colonnade."""
        w = self.w
        ya, yb = -7, 5          # first and last divider
        for x in range(20, 27):
            for y in range(ya - 1, yb + 2):
                k = pos_hash(x, y, 13) % 10
                w.set(x, y, -1, "stone_bricks" if k < 6 else ("cobble" if k < 9 else "mossy_cobble"))
        # back wall and dividers
        for y in range(ya, yb + 1):
            for z in range(4):
                w.set(26, y, z, "mossy_cobble" if pos_hash(26, y, z, 8) % 100 < 22 else "cobble")
            divider = (y - ya) % 2 == 0
            if divider:
                for z in range(2):
                    w.set(25, y, z, "stone_bricks")
            w.set(25, y, 2, "spruce_planks")
            w.set(25, y, -1, "oak_planks")
        # loft above the cells
        for y in range(ya, yb + 1):
            k = pos_hash(25, y, 3, 21) % 10
            if k < 4:
                w.set(25, y, 3, "hay")
            if k == 1:
                w.set(25, y, 4, "hay")
        # colonnade and tie beams
        for y in (ya, ya + 4, ya + 8, yb):
            for z in range(3):
                w.set(20, y, z, "oak_log")
            for x in range(20, 27):
                if w.get(x, y, 3) in (None, "hay"):
                    w.set(x, y, 3, "oak_log_x")
        for y in range(ya - 1, yb + 2):
            if w.get(20, y, 3) is None:
                w.set(20, y, 3, "oak_log_y")
        for y in list(range(ya + 1, ya + 4)) + list(range(ya + 9, yb)):
            w.set(20, y, 0, "oak_fence")
        # roof: ridge along Y over x = 23
        for y in range(ya - 1, yb + 2):
            for i, x in enumerate(range(19, 23)):
                w.set(x, y, 3 + i, "spruce_stairs_e")
                w.set(46 - x, y, 3 + i, "spruce_stairs_w")
            w.set(23, y, 7, "spruce_slab")
        for y in (ya, yb):   # pediments
            for z, (xa, xb) in ((4, (21, 25)), (5, (22, 24)), (6, (23, 23))):
                for x in range(xa, xb + 1):
                    w.set(x, y, z, "oak_planks")
        # cells: trapdoor below, pane above, workstation in front
        stations = [props.make_lectern, props.make_composter, props.make_blast_furnace, props.make_smithing_table,
                    props.make_barrel, props.make_cartography_table]
        rot = -math.pi / 2
        for i in range(6):
            cy = ya + 1 + 2 * i
            n = i + 1
            td = props.make_trapdoor(True, self.coll)
            self.place(td, 25.5, cy + 0.5, 0.0, rot, "cell_%d_trapdoor" % n)
            gp = props.make_glass_pane(edge=True, collection=self.coll)
            self.place(gp, 25.5, cy + 0.5, 1.0, rot, "cell_%d_pane" % n)
            st = stations[i](collection=self.coll)
            self.place(st, 24.5, cy + 0.5, 0.0, rot, "cell_%d_station" % n)
            for ch in st.children:
                if ch.type == "LIGHT":
                    ch.data.energy = 6.0
                    self.v.fire_lights.append(ch)
            self.anchor("cell_%d" % n, 25.58, cy + 0.5, 0.0, yaw=-math.pi / 2)
            self.anchor("cell_%d_front" % n, 23.45, cy + 0.5, 0.0, yaw=math.pi / 2)
            self.anchor("cell_%d_station" % n, 24.5, cy + 0.5, 0.95)
        for j, y in enumerate((ya, ya + 4, ya + 8, yb)):
            self.lantern("hall_%d" % (j + 1), 22, y, 2)
        self.anchor("hall_aisle_start", 22.5, ya - 1.5, 0.0, yaw=math.pi)
        self.anchor("hall_aisle_end", 22.5, yb + 2.5, 0.0, yaw=0.0)
        self.anchor("hall_entrance", 19.5, -0.5, 0.0)
        self.v.paths["hall_aisle"] = [(22.5, ya - 1.5, 0.0), (22.5, yb + 2.5, 0.0)]
        self.v.paths["square_to_hall"] = [(3.5, 2.5, 0.0), (6.5, 5.5, 0.0), (17.5, 5.6, 0.0), (18.0, -0.5, 0.0),
                                          (21.5, -0.5, 0.0), (22.5, -0.5, 0.0)]
        self.reserve(18, ya - 3, 28, yb + 3)
        # crates and barrels at the ends
        self.place(props.make_barrel(self.coll), 24.5, ya - 0.5, 0.0, name="hall_barrel_1")
        w.set(24, yb + 1, 0, "hay")
        self.lantern_post("lane_s", 18, -10, "n")
        self.lantern_post("lane_n", 16, 7, "e")

    # ---- edges, exit, nature ----------------------------------------------------------------------

    def exit_and_edges(self):
        w = self.w
        # boundary fence along the south edge with a wide gap for the road
        for x in list(range(-13, -2)) + list(range(3, 13)):
            if self.h(x, -22) == 0 and pos_hash(x, -22, 0, 17) % 9:
                w.set(x, -22, 0, "oak_fence")
                self.reserved.add((x, -22))
        for y in range(-22, -13):
            if self.h(12, y) == 0 and pos_hash(12, y, 0, 17) % 7:
                w.set(12, y, 0, "oak_fence")
                self.reserved.add((12, y))
        for y in range(-22, -17):
            if pos_hash(-13, y, 0, 17) % 6:
                w.set(-13, y, 0, "oak_fence")
                self.reserved.add((-13, y))
        self.lantern_post("gate_w", -3, -22, "e")
        self.lantern_post("gate_e", 3, -22, "w")
        self.lantern_post("road_1", 2, -8, "w")
        self.lantern_post("road_2", -2, -12, "e")
        self.lantern_post("square_nw", -5, 5, "e")
        self.lantern_post("square_ne", 5, 4, "w")
        self.lantern_post("square_sw", -5, -4, "e")
        self.lantern_post("square_se", 5, -5, "w")
        self.anchor("exit_gate", 0.5, -21.5, 0.0, yaw=0.0)
        self.anchor("exit_road_start", 0.5, -5.0, 0.0, yaw=0.0)
        self.anchor("meadow_mid", 0.5, -32.0, yaw=0.0)
        self.anchor("meadow_far", 0.5, -46.0, yaw=0.0)
        self.anchor("nitwit_idle", -15.5, -19.5, face=(-22.0, -30.0))
        # road polyline: flat to the meadow, then short ramps at each one-block rise
        pts = [(0.5, -3.0, 0.0), (0.5, -21.5, 0.0)]
        prev = 0
        for y in range(-22, -47, -1):
            hh = self.h(0, y)
            if hh != prev:
                pts.append((0.5, y + 1.35, float(prev)))
                pts.append((0.5, y + 0.85, float(hh)))
                prev = hh
        pts.append((0.5, -46.0, float(self.h(0, -46))))
        self.v.paths["exit_road"] = pts
        # details near the nitwit's spot: a broken bit of fence and a hay bale
        w.set(-17, -18, 0, "oak_fence")
        w.set(-17, -17, 0, "oak_fence")
        w.set(-14, -16, 0, "hay")
        self.reserve(-17, -21, -13, -16)

    def tree(self, x, y, height=5, seed=0):
        """Oak tree with its trunk in column (x, y)."""
        w = self.w
        base = self.h(x, y)
        top = base + height
        for z in range(base, top):
            w.set(x, y, z, "oak_log")
        for dz, rad in ((-2, 2), (-1, 2), (0, 1), (1, 1)):
            z = top + dz
            for dx in range(-rad, rad + 1):
                for dy in range(-rad, rad + 1):
                    if dx == 0 and dy == 0 and dz < 0:
                        continue
                    corner = abs(dx) == rad and abs(dy) == rad
                    if corner and (rad == 1 and dz == 1 or pos_hash(x + dx, y + dy, z, seed) % 3 != 0):
                        continue
                    if w.get(x + dx, y + dy, z) is None:
                        w.set(x + dx, y + dy, z, "oak_leaves")
        self.reserve(x - 1, y - 1, x + 1, y + 1)

    def nature(self):
        w = self.w
        r = self.r
        trees = [(-8, 6, 5), (7, -20, 5), (-19, 3, 6), (-21, -9, 5), (-23, -25, 6), (15, -19, 5), (19, 12, 6),
                 (4, 22, 6), (-9, 22, 5), (-18, 19, 6), (12, 24, 5), (-2, 27, 6), (22, 21, 5), (-27, 12, 5),
                 (30, -14, 6), (31, 6, 5), (-30, -4, 6), (9, -33, 6), (-11, -37, 5), (16, -45, 6), (-19, -50, 6),
                 (-33, -34, 5), (30, -36, 6), (8, 31, 6), (-14, 33, 5), (-25, 28, 6), (27, 31, 6), (18, 36, 5),
                 (-6, 36, 6), (36, 18, 5), (-37, 20, 6), (-36, -18, 5), (38, -24, 5)]
        for i, (x, y, hgt) in enumerate(trees):
            if (x, y) not in self.reserved:
                self.tree(x, y, hgt, seed=i)
        flowers = ["poppy", "poppy", "poppy", "dandelion", "cornflower", "daisy"]
        for x in range(X0 + 1, X1):
            for y in range(Y0 + 1, Y1):
                if (x, y) in self.reserved:
                    continue
                hh = self.h(x, y)
                if w.get(x, y, hh - 1) not in ("grass", "meadow") or w.get(x, y, hh) is not None:
                    continue
                meadow = y < -23 or abs(x) > 26 or y > 20
                p_grass = 0.30 if meadow else 0.10
                p_flower = 0.035 if meadow else 0.012
                u = r.random()
                if u < p_grass:
                    w.set(x, y, hh, "tall_grass" if r.random() < 0.72 else "short_grass")
                elif u < p_grass + p_flower:
                    w.set(x, y, hh, flowers[int(r.integers(0, len(flowers)))])
        # a drift of poppies on the meadow beside the road
        for _ in range(46):
            x = int(np.clip(round(r.normal(7, 3.2)), 3, 16))
            y = int(np.clip(round(r.normal(-31, 3.0)), -40, -25))
            hh = self.h(x, y)
            if (x, y) not in self.reserved and w.get(x, y, hh - 1) in ("grass", "meadow") and w.get(x, y, hh) in (
                    None, "tall_grass", "short_grass"):
                w.set(x, y, hh, "poppy")

    def far_ground(self):
        """Big grass-coloured skirt around the terrain so the world never ends in a void."""
        img = pix.image_from_array("far_grass", ATLAS.get("grass_top_0"))
        mat = pix.pixel_material("far_grass", img)
        size = 600.0
        x0, y0, x1, y1 = X0, Y0, X1 + 1, Y1 + 1
        quads = [(-size, -size, size, y0), (-size, y1, size, size), (-size, y0, x0, y1), (x1, y0, size, y1)]
        verts, faces, uvs = [], [], []
        for (a, b, c, d) in quads:
            i = len(verts)
            verts += [(a, b, -0.02), (c, b, -0.02), (c, d, -0.02), (a, d, -0.02)]
            faces.append((i, i + 1, i + 2, i + 3))
            uvs += [(a, b), (c, b), (c, d), (a, d)]
        mesh = bpy.data.meshes.new("far_ground")
        mesh.from_pydata(verts, [], faces)
        uv = mesh.uv_layers.new(name="UVMap")
        uv.data.foreach_set("uv", np.asarray(uvs, np.float32).reshape(-1))
        mesh.materials.append(mat)
        mesh.update()
        obj = bpy.data.objects.new("village_far_ground", mesh)
        self.coll.objects.link(obj)
        return obj

    def build(self):
        self.terrain()
        self.square()
        self.house_a()
        self.house_b()
        self.house_c()
        self.house_d()
        self.house_e()
        self.farm()
        self.library()
        self.smithy()
        self.well()
        self.hall()
        self.exit_and_edges()
        self.nature()
        objs = self.w.build(self.coll, "village")
        self.far_ground()
        v = self.v
        v.objects = list(self.coll.objects)
        v.face_count = sum(len(o.data.polygons) for o in v.objects if o.type == "MESH")
        return v


def build_village(scene, seed=1):
    """Build the whole village set into `scene` and return its Village handle."""
    return _Builder(scene, seed).build()


# --------------------------------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------------------------------


def _standin(coll, pos, color=(170, 120, 90, 255), name="standin"):
    """A 0.6 x 0.6 x 1.95 box standing on `pos`: scale reference for a character."""
    mesh = bpy.data.meshes.new(name)
    hw = 0.3
    v = [(-hw, -hw, 0), (hw, -hw, 0), (hw, hw, 0), (-hw, hw, 0), (-hw, -hw, 1.95), (hw, -hw, 1.95), (hw, hw, 1.95),
         (-hw, hw, 1.95)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh.from_pydata(v, [], f)
    mesh.materials.append(pix.flat_material(name + "_mat_%d_%d_%d" % color[:3], color))
    obj = bpy.data.objects.new(name, mesh)
    obj.location = pos
    coll.objects.link(obj)
    return obj


def _selftest(only=None):
    from . import quick

    def stage(preset, sun_az=None, lantern=None):
        scene = quick.reset()
        quick.setup(scene)
        sun = quick.light(scene, preset)
        if sun_az is not None:
            sun.rotation_euler[2] = math.radians(sun_az)
        v = build_village(scene, seed=1)
        if lantern is not None:
            v.set_lantern_energy(lantern)
        return scene, v

    def want(name):
        return only is None or name in only

    first = True

    def report(v):
        nonlocal first
        if not first:
            return
        first = False
        miss = v.validate()
        print("village faces:", v.face_count, "objects:", len(v.objects), "lantern lights:", len(v.lantern_lights))
        print("anchors (%d):" % len(v.anchors), ", ".join(sorted(v.anchors)))
        print("paths (%d):" % len(v.paths), ", ".join(sorted(v.paths)))
        print("doors (%d):" % len(v.doors), ", ".join(sorted(v.doors)))
        print("bounds:", v.bounds, "terrain:", v.terrain_bounds)
        print("VALIDATION:", "OK - all required anchors, paths and doors exist" if not miss else "MISSING %s" % miss)
        assert not miss, miss
        assert v.face_count < 200000

    if want("overview"):
        scene, v = stage("day")
        report(v)
        quick.camera(scene, (40, -74, 60), (2, -8, 0), lens=22)
        print("wrote", quick.render(scene, "village_overview"))

    if want("square"):
        scene, v = stage("golden", sun_az=62)
        report(v)
        _standin(v.collection, v.anchors["bell_ringer"])
        quick.camera(scene, (7.4, -4.4, 1.35), (0.5, 1.2, 1.9), lens=24, fstop=2.8)
        print("wrote", quick.render(scene, "village_square"))

    if want("house_a_interior"):
        scene, v = stage("night", lantern=70)
        report(v)
        v.set_door("house_a", True)
        for i, c in enumerate(((120, 90, 70, 255), (90, 110, 80, 255))):
            _standin(v.collection, v.anchors["house_a_inside_%d" % (i + 1)], c)
        cx, cy, _ = v.anchors["house_a_cam"]
        quick.camera(scene, (cx, cy, 1.75), (0.6, 8.5, 0.95), lens=15)
        print("wrote", quick.render(scene, "village_house_a_interior"))

    if want("hall"):
        scene, v = stage("golden", sun_az=-70, lantern=60)
        report(v)
        for i in range(1, 7):
            _standin(v.collection, v.anchors["cell_%d" % i], (125, 95, 75, 255))
        sx, sy, _ = v.anchors["hall_aisle_start"]
        ex, ey, _ = v.anchors["hall_aisle_end"]
        quick.camera(scene, (sx - 0.9, sy + 0.4, 1.5), (ex + 1.6, ey - 5.0, 1.35), lens=20, fstop=2.8)
        print("wrote", quick.render(scene, "village_hall"))

    if want("exit"):
        scene, v = stage("golden", sun_az=118)
        report(v)
        _standin(v.collection, (0.5, -27.0, v.ground(0.5, -27.0)), (70, 130, 60, 255))
        quick.camera(scene, (0.3, -5.2, 1.5), (0.5, -30.0, 1.9), lens=24, fstop=4.0)
        print("wrote", quick.render(scene, "village_exit"))

    if want("night"):
        scene, v = stage("night", lantern=60)
        report(v)
        quick.camera(scene, (-0.9, -20.2, 1.2), (0.9, -3.0, 2.3), lens=22, fstop=2.8)
        print("wrote", quick.render(scene, "village_night"))

    if want("stations"):
        scene, v = stage("golden", sun_az=62)
        report(v)
        for nm in ("farm_work", "library_work", "smithy_work"):
            _standin(v.collection, v.anchors[nm])
        quick.setup(scene, res=(960, 540))
        quick.camera(scene, (-3.5, 3.0, 1.6), v.anchors["library_station"], lens=22)
        print("wrote", quick.render(scene, "village_station_library"))
        quick.camera(scene, (-3.2, -4.2, 1.6), v.anchors["smithy_station"], lens=22)
        print("wrote", quick.render(scene, "village_station_smithy"))
        quick.camera(scene, (12.5, 3.2, 1.7), (11.5, 11.5, 0.8), lens=18)
        print("wrote", quick.render(scene, "village_station_farm"))


if __name__ == "__main__":
    import sys

    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    _selftest(set(args) if args else None)
