"""The village set: a real plains village composed from vanilla structure templates, built like a film set.

Layout (Blender block coordinates, +X = east, +Y = north = Minecraft -z, ground surface z = 0):

                                  open meadow, rising gently (meadow_far)
                                             |  exit_road
                          house_e  (-9..-3,  |  house_f (big house)
                           12..18) door E -> | <- door W   (3..9, 11..21)
   library                                   |
   (-36..-26,   house_d      house_c         |          house_b        smithy (weaponsmith, open forge porch
    -8..8)      door S       door E  ->  [ WELL + BELL ]  <- door W     facing S onto the street) (17..27, 3..11)
   door E  ===  W street ================  plaza  ================ E street =========
                farm (composters)            |          house_a (roomy, 2 beds; door W onto the plaza)
                (-23..-11, -12..-4)          | S street  (9..21, -15..-5)
                          house_g  door E -> |
                          (-9..-3, -24..-12) |
                                    [ trading hall ]  (-7..5, -33..-27), aisle runs east-west

Every building is an unmodified vanilla template (engine/structures.py) placed at the height its own
building_entrance jigsaw dictates (so floors sit one block above the path with the vanilla step at the door);
part of the cobblestone is mossy as the game's village processors make it; only the trading hall is
"player-built" from vanilla blocks.

Use build_village(scene); everything a film needs is on the returned Village:
  anchors / yaws / paths / doors / bell / lantern_lights / lights (by group) / beds / buildings / cutaways
  door_open(), set_door(), ring_bell(), set_lantern_energy(), only_lights_near(), cutaway(), ground(), validate()
Walking surfaces: grass 0.0, dirt_path -1/16, house floors +1.0 (vanilla houses are raised one block; the entry
polylines climb the door step), house_f floor 0.0, farmland +15/16 above the farm's log frame.

FILM SETS: build_village(scene, seed=1, bed_colors=None, edit=None). With edit=None the village is exactly the one
of the finished films (tools/check_sets_hook.py proves it). `edit(b)` is called once with the builder when every
block of the village is in the World and its anchors and paths exist, BEFORE the mesh, the door / bell props and the
lights are made: whatever the hook puts into the World (or takes out of it) is meshed, lit and checked like the
village's own. engine/sets.py holds the set pieces that are built this way. What `b` offers the hook:

  b.w                      the World (blocks.World: set / get / fill / block_id / is_solid, Blender grid coordinates)
  b.v                      the Village being built (anchors, yaws, paths, beds, buildings, sets)
  b.seed, b.rng_for(tag)   a numpy Generator of its own for a set piece (seeded by the village seed and the tag)
  b.ground(x, y)           terrain surface z of a column (top of its grass block; floats are floored), None = no terrain
  b.walk_z(x, y)           height a character stands at there (grass z, dirt_path z - 1/16, a slab z + 0.5)
  b.trees                  the village's own oaks as data: dict(kind, x, y, base, height, logs=[cells], leaves=[cells],
                           where='village' | 'ring' | 'meadow' | 'set'); b.tree_at(x, y) finds one by its trunk
  b.tree(x, y, rng, where) plant one more vanilla small oak (the village's own generator); returns its record
  b.anchor(name, pos, yaw=None) / b.path(name, points)       register a standing spot / a walkable polyline (2D points
                           get the walking height); an existing name is refused unless replace=True
  b.extend_terrain(x0, y0, x1, y1, plants=True, rise=1/11)   grass terrain for every column of the box that has none
                           (the set is a disc of radius 83 inside [-84, 84)): the village's own relief where its height
                           field reaches, beyond it the edge carried on with gentle seeded noise and the meadow's rise;
                           the same short grass / tall grass / flowers as the far meadow. Returns the new columns.
  b.natural_height(x, y)   the height that terrain has or would get at a column (what extend_terrain uses)
  b.set_ground(x, y, z)    re-level one column (grass top at z; whatever grew on it is removed; dirt sides are refilled)
  b.clear_plants(x, y) / b.sow(x, y, rng, edge=None)         remove / grow the meadow's plants on one column
  b.pave(x, y)             turn a column's surface into dirt_path
  b.reserved, b.path_cells sets of (x, y) columns: where nothing is sown or planted / what is paved. Add yours.
  b.show_undersides(x0, y0, x1, y1)     draw the terrain's underside there again (a set dug in under the ground)
  b.torch(cell, block_id='torch', props=None, group='set')   a torch / lantern block WITH its point light, in a light
                           group of its own (Village.lights[group]). Torch blocks set with b.w.set(...) get one too.
  b.bed(name, foot_cell, facing, color='white') / b.door(name, cell, facing, hinge='left', block_id='oak_door')
                           a bed with its anchor and Village.beds entry / a door that becomes an animated prop
                           (Village.doors[name], door_open(name, ...)), like the houses' own
  b.allow(what)            permit changes inside a building ('house_a', 'hall', ...), on the 'streets', or in a box
                           (x0, y0, x1, y1); without it a block changed inside a house or on a street is a problem
  b.changed()              the cells the hook has changed so far; b.strict = False turns problems into warnings
After the hook: torches it removed lose their light, beds and doors it removed lose their anchors and props, and the
build stops with a ValueError (b.strict) if a block was changed inside a building or on a street without b.allow, if
a path is blocked or an anchor stands inside a block (Village.validate(): every anchor is taken as a standing spot
unless it is a bed's or its name ends in _target, _center, _cam, _station or _door). The list is also in
Village.edit_problems. If the hook re-levels ground under one of the village's own paths, register that path again
(b.path(name, points_2d, replace=True)): its heights were taken before the hook ran.
The look's fill light is shadowless (engine/look.py): a roofed or dug-in set piece is NOT dark by itself.
engine/sets.py can bake the game's own sky light into the blocks (sets.env(b).bake_sky_light).
"""
import math

import bpy
import numpy as np

from . import mcassets as mc
from . import props, structures
from .blocks import HORIZ, World, new_collection, pos_hash, rotate_facing

R = 84                      # terrain half-size in blocks (terrain covers [-R, R) in x and y)
MEADOW_FLAT_TO = 50.0       # the meadow is flat (z = 0) up to about this y: 30 blocks beyond exit_gate (y = 24.5)
MEADOW_STEP = 11.0          # then it rises one block about every this many blocks
MEADOW_OAKS = [(-13, 47), (15, 55), (-7, 63), (24, 69), (6, 74)]     # a few lone oaks in the meadow, for scale
VILLAGE_BOUNDS = (-36, -33, 28, 26)  # built-up area (x0, y0, x1, y1)

# name, template, footprint min corner (x, y), clockwise quarter turns
LAYOUT = [
    ("well", "town_centers/plains_meeting_point_1", (-5, -5), 0),
    ("house_a", "houses/plains_medium_house_1", (9, -15), 0),
    ("house_b", "houses/plains_small_house_1", (9, 3), 0),
    ("house_c", "houses/plains_small_house_4", (-16, 3), 2),
    ("house_d", "houses/plains_small_house_2", (-24, 3), 3),
    ("house_e", "houses/plains_small_house_6", (-9, 12), 2),
    ("house_f", "houses/plains_big_house_1", (3, 11), 0),
    ("house_g", "houses/plains_medium_house_2", (-9, -24), 2),
    ("library", "houses/plains_library_1", (-36, -8), 2),
    ("smithy", "houses/plains_weaponsmith_1", (17, 3), 3),
    ("farm", "houses/plains_large_farm_1", (-23, -12), 0),
]
HOUSES = ["house_a", "house_b", "house_c", "house_d", "house_e", "house_f", "house_g"]
LAMPS = [(6, 9), (-7, 9), (-8, -6), (7, -3), (16, -3), (-17, 2), (-3, 24), (3, 24), (3, -19), (-3, -25)]
# player-built lamps (cobblestone foot, two oak fence posts, a lantern) flanking the bell two blocks to its south-west
# and south-east: (cell x, cell y, light group)
BELL_LAMPS = [(-4, -4, "bell_w"), (0, -4, "bell_e")]
# the verge columns west of the exit road that stay plain grass from the last houses into the meadow (x cells, y range):
# a camera that tracks somebody up the road from behind rides there, and a tuft one block from the lens covers him
CAMERA_LANE = ((-3, -2), (22, 58))
HALL = dict(x0=-7, y0=-33, cells=6)
HALL_JOBS = ["lectern", "fletching_table", "smithing_table", "cartography_table", "blast_furnace", "stonecutter"]
HALL_PROFESSIONS = ["librarian", "fletcher", "toolsmith", "cartographer", "armorer", "mason"]

REQUIRED_ANCHORS = (
    ["bell", "bell_ringer", "square_n", "square_e", "square_s", "square_w",
     "house_a_door_out", "house_a_door_in", "house_a_cam"]
    + ["house_a_inside_%d" % i for i in (1, 2, 3)] + ["house_a_bed_%d" % i for i in (1, 2)]
    + ["farm_work", "farm_station", "library_work", "library_station", "smithy_work", "smithy_station"]
    + ["cell_%d" % i for i in range(1, 7)] + ["hall_aisle_start", "hall_aisle_end"]
    + ["exit_gate", "meadow_far", "nitwit_idle"]
)
REQUIRED_PATHS = ["square_to_house_a", "square_to_house_b", "square_to_house_c", "exit_road"]
REQUIRED_DOORS = ["house_a", "house_b", "house_c"]

_VEC = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}


def yaw_to(src, dst):
    """Yaw (radians about Z) that makes a character standing at src (who faces -Y at yaw 0) face dst."""
    return math.atan2(dst[0] - src[0], -(dst[1] - src[1]))


def yaw_of(direction):
    """Yaw for a character facing a compass direction name."""
    dx, dy = _VEC[direction]
    return math.atan2(dx, -dy)


class Village:
    """Handle to the built set (see the module docstring and CONTRACT.md)."""

    def __init__(self):
        self.world = None
        self.collection = None
        self.anchors = {}         # name -> (x, y, z): standing spots (z = walking surface) and look targets
        self.paths = {}           # name -> [(x, y, z), ...] walkable polylines on the ground
        self.doors = {}           # name -> door prop (hinge pivot); see door_open()
        self.bell = None          # swinging bell body (rotate about local X); bell.parent carries the frame
        self.lantern_lights = []  # every torch / lantern point light
        self.lights = {}          # group name ('well', 'lamp', 'house_a', 'hall', 'bell_w', 'bell_e', ...) -> [light objects]
        self.yaws = {}            # anchor name -> suggested facing yaw for a character standing there
        self.beds = {}            # anchor name -> dict(pos, head, foot, yaw, facing); yaw/facing point foot -> pillow
        self.buildings = {}       # name -> blocks.Placement of the vanilla template
        self.cutaways = {}        # cutaway name -> [objects] hidden by cutaway()
        self.objects = []         # the world mesh objects
        self.cell_professions = list(HALL_PROFESSIONS)
        self.bounds = VILLAGE_BOUNDS
        self.terrain_bounds = (-R, -R, R, R)
        self.face_count = 0
        self._height = None
        self._door_sets = {}
        self._ext = {}            # (x, y) -> terrain height of columns a film's edit hook added beyond the height field
        self.trees = []           # the oaks as data (see the module docstring: FILM SETS)
        self.sets = {}            # set piece name -> whatever its function returned (engine/sets.py), for the film
        self.edit_problems = []   # what the check after a film's edit hook found (empty = all good)

    def ground(self, x, y):
        """Height of the terrain surface (z) at world position (x, y)."""
        if self._ext:             # terrain a film's edit hook added outside the height field
            h = self._ext.get((int(math.floor(x)), int(math.floor(y))))
            if h is not None:
                return float(h)
        ix = int(np.clip(math.floor(x), -R, R - 1)) + R
        iy = int(np.clip(math.floor(y), -R, R - 1)) + R
        return float(self._height[ix, iy])

    def door_open(self, name, frame, open=True, frames=5):
        """Keyframe door `name` swinging open (or shut with open=False) from `frame` over `frames` frames."""
        for d in self._door_sets[name]:
            closed = d["closed_yaw"]
            opened = closed + d["open_angle"]
            a, b = (closed, opened) if open else (opened, closed)
            d.rotation_euler[2] = a
            d.keyframe_insert("rotation_euler", index=2, frame=frame)
            d.rotation_euler[2] = b
            d.keyframe_insert("rotation_euler", index=2, frame=frame + max(1, frames))

    def set_door(self, name, open=True):
        """Set a door open or shut immediately, without keyframes."""
        for d in self._door_sets[name]:
            d.rotation_euler[2] = d["closed_yaw"] + (d["open_angle"] if open else 0.0)

    def ring_bell(self, frame, strength=1.0, swings=5):
        """Keyframe the bell swinging from `frame` (decaying, ~1 s per full swing). Returns the rest frame."""
        fps = bpy.context.scene.render.fps if bpy.context.scene else 24
        return props.ring_bell(self.bell, frame, strength=strength, swings=swings, fps=fps)

    def set_lantern_energy(self, scale=1.0, groups=None):
        """Scale every torch / lantern light relative to its built-in energy (optionally only some groups, e.g.
        ['house_a']). scale=0 also removes the lights from the render, which makes daylight shots faster."""
        for group, lights in self.lights.items():
            if groups is None or group in groups:
                for ob in lights:
                    ob.data.energy = ob["base_energy"] * scale
                    ob.hide_render = scale <= 0.0
                    ob.hide_viewport = scale <= 0.0

    def only_lights_near(self, point, radius=24.0):
        """Keep only the torch / lantern lights within `radius` blocks of `point` in the render (fewer lights =
        faster, cleaner frames); radius=None switches every light back on. Returns the lights left on."""
        on = []
        for ob in self.lantern_lights:
            far = radius is not None and math.dist(ob.location, point) > radius
            ob.hide_render = far
            ob.hide_viewport = far
            if not far:
                on.append(ob)
        return on

    def cutaway(self, name, hide=True, frame=None):
        """Hide (or show again) a removable section so a camera can see or sit inside a building.

        Names: 'house_a_east' (the whole east end behind the beds, gable included), 'house_a_roof' (everything
        above the 2-block walls), 'house_a_south' (south wall), 'library_roof', 'library_south'.
        With `frame` the visibility is keyframed (constant) from that frame on, for cut-based films.
        """
        for ob in self.cutaways[name]:
            ob.hide_render = hide
            ob.hide_viewport = hide
            if frame is not None:
                ob.keyframe_insert("hide_render", frame=frame)
                ob.keyframe_insert("hide_viewport", frame=frame)

    def path_clear(self, points, step=0.2):
        """List of (x, y, z) samples along a polyline where a 0.6 x 1.95 character would hit a solid block."""
        w = self.world
        bad = []
        for a, b in zip(points[:-1], points[1:]):
            n = max(1, int(math.dist(a, b) / step))
            for i in range(n + 1):
                t = i / n
                x, y, z = (a[k] + (b[k] - a[k]) * t for k in range(3))
                cx, cy = int(math.floor(x)), int(math.floor(y))
                for cz in range(int(math.floor(z + 0.2)), int(math.floor(z + 1.9)) + 1):
                    if w.is_solid(cx, cy, cz):
                        bid = w.block_id(cx, cy, cz)
                        if cz == int(math.floor(z + 0.2)) and (bid.endswith("_stairs") or bid.endswith("_slab")
                                                               or bid in ("dirt_path", "farmland")):
                            continue
                        bad.append((round(x, 2), round(y, 2), round(z, 2), bid))
        return bad

    def validate(self):
        """Problems with the set: missing required anchors / paths / doors and blocked paths (empty = all good)."""
        out = ["missing anchor " + a for a in REQUIRED_ANCHORS if a not in self.anchors]
        out += ["missing path " + p for p in REQUIRED_PATHS if p not in self.paths]
        out += ["missing door " + d for d in REQUIRED_DOORS if d not in self.doors]
        if self.bell is None:
            out.append("missing bell")
        if not self.lantern_lights:
            out.append("no lantern lights")
        for name, pts in self.paths.items():
            hits = self.path_clear(pts)
            if hits:
                out.append("path %s blocked at %s" % (name, hits[:3]))
        w = self.world
        for ob in self.lantern_lights:
            c = tuple(int(math.floor(a)) for a in ob.location)
            if ob.get("mc_light") != "fill" and w.is_solid(*c) and w.is_full_cube(*c):
                out.append("light %s buried in %s" % (ob.name, w.block_id(*c)))
        for name, (x, y, z) in self.anchors.items():
            if name.endswith(("_station", "_station_2", "_cam", "_cam_beds", "_door", "_target", "_center")) \
                    or "_bed_" in name or name in self.beds \
                    or name in ("bell", "well") or name.startswith("bell_lamp_"):
                continue
            cx, cy = int(math.floor(x)), int(math.floor(y))
            for cz in (int(math.floor(z + 0.2)), int(math.floor(z + 1.2))):
                if w.is_solid(cx, cy, cz):
                    bid = w.block_id(cx, cy, cz)
                    if not (bid.endswith("_stairs") or bid.endswith("_slab") or bid in ("dirt_path", "farmland")):
                        out.append("anchor %s inside %s" % (name, bid))
        return out


# --------------------------------------------------------------------------------------------------
# builder
# --------------------------------------------------------------------------------------------------

def _value_noise(rng, n, cell):
    g = int(n / cell) + 3
    lat = rng.random((g, g))
    xs = np.arange(n) / cell
    i = xs.astype(int)
    f = xs - i
    f = f * f * (3 - 2 * f)
    a = lat[i][:, i] * (1 - f)[:, None] * (1 - f)[None, :]
    b = lat[i + 1][:, i] * f[:, None] * (1 - f)[None, :]
    c = lat[i][:, i + 1] * (1 - f)[:, None] * f[None, :]
    d = lat[i + 1][:, i + 1] * f[:, None] * f[None, :]
    return a + b + c + d


def _distance(mask):
    """Chebyshev-ish distance (in blocks) of every cell to the nearest True cell (two-pass chamfer)."""
    n = mask.shape[0]
    big = 1e6
    d = np.where(mask, 0.0, big)
    for _ in range(2):
        for i in range(1, n):
            d[i, :] = np.minimum(d[i, :], d[i - 1, :] + 1)
            d[:, i] = np.minimum(d[:, i], d[:, i - 1] + 1)
        for i in range(n - 2, -1, -1):
            d[i, :] = np.minimum(d[i, :], d[i + 1, :] + 1)
            d[:, i] = np.minimum(d[:, i], d[:, i + 1] + 1)
    return d


def _hash_noise(x, y, cell, seed):
    """Smooth value noise 0..1 at (x, y) from a hashed lattice of pitch `cell` (defined everywhere, unlike
    _value_noise, which fills one array): the relief of terrain a film's edit hook adds beyond the height field."""
    gx, gy = x / cell, y / cell
    ix, iy = int(math.floor(gx)), int(math.floor(gy))
    fx, fy = gx - ix, gy - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

    def lat(i, j):
        return (pos_hash(i, j, seed, 77) & 0xFFFF) / 65535.0

    return (lat(ix, iy) * (1 - fx) + lat(ix + 1, iy) * fx) * (1 - fy) + (lat(ix, iy + 1) * (1 - fx)
                                                                         + lat(ix + 1, iy + 1) * fx) * fy


def _jigsaws(template, name):
    out = []
    raw = template.raw
    for b in raw["blocks"]:
        st = raw["palette"][b["state"]]
        if (st.get("id") or st.get("Name")) != "minecraft:jigsaw":
            continue
        if b.get("nbt", {}).get("name") == name:
            pr = st.get("properties") or st.get("Properties") or {}
            out.append((tuple(b["pos"]), pr.get("orientation", "north_up").split("_")[0]))
    return out


class _Builder:
    def __init__(self, scene, seed, bed_colors=None):
        self.scene = scene
        self.seed = seed
        self.bed_colors = dict(bed_colors or {})
        self.rng = np.random.default_rng(seed)
        self.v = Village()
        self.w = World()
        self.v.world = self.w
        self.v.collection = new_collection(scene, "village")
        self.path_cells = set()       # (x, y) columns paved with dirt_path
        self.reserved = set()         # (x, y) columns where no plants / trees may grow
        self.entries = {}             # building -> dict(entrance cell, outward dir, door cells, ...)
        self.skip = set()
        self.torches = []             # (group, block_id, props, cell)
        self.groups = {}              # cutaway name -> set of cells
        # the film hook (build_village(edit=...)): see the module docstring
        self.trees = self.v.trees     # every oak tree() planted, as data
        self.ext = self.v._ext        # terrain columns outside the height field: (x, y) -> height
        self.set_groups = set()       # light groups made by the hook: one point light per torch / lantern
        self.light_group = "set"      # group of torch blocks the hook places without b.torch(...)
        self.allowed = []             # building names / 'streets' / boxes the hook may change (b.allow)
        self.strict = True            # problems found after the hook stop the build
        self._before = None           # World.blocks as they were when the hook was called
        self._natural = None          # the height field as terrain() made it (set when a hook runs)
        self._streets_before = set()

    # ---- terrain ---------------------------------------------------------------------------------

    def footprints(self):
        """Placement boxes (before placing) to know where the ground must be flat."""
        flat = np.zeros((2 * R, 2 * R), dtype=bool)

        def box(x0, y0, x1, y1, m=3):
            flat[max(0, x0 - m + R):x1 + m + 1 + R, max(0, y0 - m + R):y1 + m + 1 + R] = True

        for name, tname, (ox, oy), rot in LAYOUT:
            t = structures.load_template("village/plains/" + tname)
            sx, sy, sz = t.size
            w_, d_ = (sz, sx) if rot % 2 else (sx, sz)
            box(ox, oy, ox + w_ - 1, oy + d_ - 1)
        box(-10, -10, 9, 8, 1)                       # plaza
        box(-25, -1, 30, 1, 2)                       # east-west street
        box(-3, -27, 3, 46, 2)                       # north-south street and the exit road corridor
        h = HALL
        box(h["x0"], h["y0"], h["x0"] + 12, h["y0"] + 6, 4)
        box(7, 28, 12, 32, 1)                        # nitwit's lonely spot
        return flat

    def terrain(self):
        """Gently uneven grass terrain: flat under the village, rolling and rising outside it."""
        w, rng = self.w, self.rng
        flat = self.footprints()
        d = _distance(flat)
        n = 2 * R
        noise = (_value_noise(rng, n, 17.0) - 0.5) * 2.0 + (_value_noise(rng, n, 7.0) - 0.5) * 0.9
        amp = np.clip(d / 12.0, 0, 1) * 2.4
        rise = np.clip((d - 5.0) / 13.0, 0, None) ** 1.15
        xs = np.arange(n)[:, None] - R
        ys = np.arange(n)[None, :] - R
        corridor = np.clip(1.0 - np.abs(xs) / 20.0, 0, 1) * (ys > 22)   # the meadow north of the exit: smooth
        hgt = noise * amp * (1.0 - 0.75 * corridor) + rise
        # The open meadow beyond the exit: a wedge that widens to the north (everything a camera on the exit road
        # sees), dead flat for 30 blocks past exit_gate, then single 1-block rises about 11 blocks apart whose edges
        # wander (seeded noise shifts each contour by up to +-5 blocks). The old terrain rose in concentric
        # 1-block terraces here, and their long straight dirt sides read as brick walls on the horizon.
        wrng = np.random.default_rng(self.seed + 4099)          # own generator: the rest of the village is unchanged
        wobble = (_value_noise(wrng, n, 11.0) - 0.5) * 9.0 + (_value_noise(wrng, n, 4.5) - 0.5) * 3.5
        wedge = np.clip((0.45 * (ys - 10.0) + 6.0 - np.abs(xs)) / 8.0, 0.0, 1.0) * (ys > 22)
        meadow = np.clip((ys + wobble - MEADOW_FLAT_TO) / MEADOW_STEP, 0.0, None)
        hgt = hgt * (1.0 - wedge) + meadow * wedge
        hgt = np.where(d <= 0, 0.0, hgt)
        height = np.floor(hgt + 0.35).astype(int)
        height = np.maximum(height, 0)
        self.v._height = height.astype(float)
        self.height = height
        self.dist = d
        self.wedge = wedge
        hidden = w.hidden_sides
        outside = (xs * xs + ys * ys) > (R - 1) * (R - 1)      # the terrain is a disc
        height[outside] = -99
        for ix in range(n):
            for iy in range(n):
                h = height[ix, iy]
                if h == -99:
                    continue
                x, y = ix - R, iy - R
                low = h
                for ax, ay in ((ix - 1, iy), (ix + 1, iy), (ix, iy - 1), (ix, iy + 1)):
                    if 0 <= ax < n and 0 <= ay < n and height[ax, ay] != -99:
                        low = min(low, height[ax, ay])
                w.set(x, y, h - 1, "grass_block", {"snowy": "false"})
                bottom = h - 1
                for z in range(low, h - 1):
                    w.set(x, y, z, "dirt")
                    bottom = min(bottom, z)
                hidden.add(((x, y, bottom), "down"))

    def surface_z(self, x, y):
        """Terrain block top at column (x, y)."""
        if -R <= x < R and -R <= y < R:
            return int(self.height[x + R, y + R])
        return int(self.ext.get((x, y), -99))        # (only a film's edit hook builds out there)

    def pave(self, x, y):
        """Turn the terrain surface block of a column into dirt_path."""
        h = self.surface_z(x, y)
        if h == -99:
            return
        if self.w.block_id(x, y, h - 1) in ("grass_block", "dirt"):
            self.w.set(x, y, h - 1, "dirt_path")
        self.path_cells.add((x, y))
        self.reserved.add((x, y))

    def streets(self):
        """Hand-laid dirt_path plaza and 3-wide streets (with the odd grass block, like vanilla street pieces)."""
        rng = self.rng
        # plaza: a rounded patch around the meeting point with slightly ragged edges, like vanilla paths
        for x in range(-10, 10):
            for y in range(-10, 9):
                cx, cy = abs(x + 0.5), abs(y + 0.5)
                edge = max(cx - 9.0, cy - (9.0 if y < 0 else 8.0), (cx + cy) - 15.5)
                if edge < -1.0 or (edge < 0.0 and rng.random() < 0.6):
                    self.pave(x, y)
        # streets, 3 wide with the odd grass block left in, as the game's street pieces have
        def street(x0, y0, x1, y1, ragged=0.06):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                for y in range(min(y0, y1), max(y0, y1) + 1):
                    if rng.random() >= ragged:
                        self.pave(x, y)
                    self.reserved.add((x, y))

        street(-25, -1, -10, 1)       # west street to the library
        street(9, -1, 29, 1)          # east street past the smithy
        street(-1, -26, 1, -10)       # south street to the trading hall
        street(-1, 8, 1, 30)          # exit road, full width
        for y in range(31, 45):       # ... thinning out into the meadow
            keep = 1.0 - (y - 30) / 15.0
            for x in (-1, 0, 1):
                self.reserved.add((x, y))
                if rng.random() < keep * (1.0 if x == 0 else 0.7):
                    self.pave(x, y)

    # ---- vanilla buildings -----------------------------------------------------------------------

    def buildings(self):
        """Place every vanilla template at the height its building_entrance / street jigsaw dictates."""
        w = self.w
        for name, tname, (ox, oy), rot in LAYOUT:
            t = structures.load_template("village/plains/" + tname)
            ent = _jigsaws(t, "minecraft:building_entrance")
            street = _jigsaws(t, "minecraft:street")
            jy = ent[0][0][1] if ent else (street[0][0][1] if street else 0)
            pl = w.place_template(t, (ox, oy, -jy), rot)
            self.v.buildings[name] = pl
            # the game's village processors turn part of the cobblestone mossy (10 % in houses, 20 % in the centre)
            moss = 20 if name == "well" else 10
            for i, (bx, by, bz, bid, p) in enumerate(pl.blocks):
                if bid == "cobblestone" and pos_hash(bx, by, bz, 11) % 100 < moss:
                    w.set(bx, by, bz, "mossy_cobblestone")
                    pl.blocks[i] = (bx, by, bz, "mossy_cobblestone", p)
            x0, y0, z0, x1, y1, z1 = pl.bounds
            for x in range(x0, x1 + 1):
                for y in range(y0, y1 + 1):
                    self.reserved.add((x, y))
            for bx, by, bz, bid, p in pl.blocks:
                if bid == "dirt_path":
                    self.path_cells.add((bx, by))
                # exposed dirt in a template's ground layer would have grown over long ago
                if bid == "dirt" and w.get(bx, by, bz + 1) is None and bz <= 0:
                    w.set(bx, by, bz, "grass_block", {"snowy": "false"})
                if bid in ("torch", "wall_torch", "lantern"):
                    self.torches.append((name, bid, p, (bx, by, bz)))
            if ent and name != "farm":
                (ex, ey, ez), out = ent[0]
                cell = pl.pos(ex, ey, ez)
                self.entries[name] = dict(cell=cell, out=pl.facing(out))
        # the game spreads grass over exposed dirt; do it once more now that everything is placed
        for name, pl in self.v.buildings.items():
            for bx, by, bz, bid, p in pl.blocks:
                if bid == "dirt" and bz <= 0 and w.get(bx, by, bz + 1) is None:
                    w.set(bx, by, bz, "grass_block", {"snowy": "false"})

    def entrances(self):
        """Find each building's door, pave a spur from its entrance to the street, record walk-in points."""
        w = self.w
        for name, e in self.entries.items():
            pl = self.v.buildings[name]
            cx, cy, cz = e["cell"]
            ox, oy = _VEC[e["out"]]
            doors = pl.find("oak_door", half="lower")
            e["doors"] = []
            if doors:
                # nearest ground-floor door to the entrance, plus its partner for double doors
                doors.sort(key=lambda c: abs(c[0] - cx) + abs(c[1] - cy) + 4 * abs(c[2] - cz - 1))
                first = doors[0]
                e["doors"] = [c for c in doors if c[2] == first[2] and abs(c[0] - first[0]) + abs(c[1] - first[1]) <= 1]
                for c in e["doors"]:
                    w.passable.add(c)
                    w.passable.add((c[0], c[1], c[2] + 1))
            # spur: pave outward from the entrance until an existing path is reached
            for k in range(1, 9):
                px, py = cx + ox * k, cy + oy * k
                if (px, py) in self.path_cells:
                    break
                self.pave(px, py)
            if w.get(cx, cy, cz) is None and w.block_id(cx, cy, cz - 1) in ("grass_block", "dirt"):
                self.pave(cx, cy)
            for k in range(-1, 4):
                self.reserved.add((cx + ox * k, cy + oy * k))
                self.reserved.add((cx + ox * k + oy, cy + oy * k + ox))
                self.reserved.add((cx + ox * k - oy, cy + oy * k - ox))

    def walk_surface(self, x, y, z_top):
        """Walking height in a column scanning down from z_top (stairs count as half-way up)."""
        w = self.w
        for z in range(z_top, z_top - 5, -1):
            if w.is_solid(x, y, z):
                bid, p = w.get(x, y, z)
                if bid in ("dirt_path", "farmland"):
                    return z + 15.0 / 16.0, bid
                if bid.endswith("_slab") and p.get("type", "bottom") == "bottom":
                    return z + 0.5, bid
                if bid.endswith("_stairs"):
                    return z + 0.5, bid
                return z + 1.0, bid
        return float(z_top - 4), None

    def entry_points(self, name, inside=1.4):
        """Polyline from just outside a building's entrance, up its step, through the door, to just inside."""
        e = self.entries[name]
        cx, cy, cz = e["cell"]
        ox, oy = _VEC[e["out"]]
        door = e["doors"][0] if e["doors"] else (cx - ox, cy - oy, cz)
        if len(e["doors"]) == 2:   # double door: walk through the leaf in line with the entrance if possible
            for c in e["doors"]:
                if (c[0] - cx) * oy == 0 and (c[1] - cy) * ox == 0 and ((c[0] == cx) or (c[1] == cy)):
                    door = c
        dz = door[2]
        steps = abs(door[0] - cx) + abs(door[1] - cy) if (door[0] == cx or door[1] == cy) else 1
        # line of cells from 2 outside the entrance to `inside` blocks past the door, along the door's own axis
        lx, ly = (door[0], door[1])
        pts = []
        k_out = steps + 2
        for k in range(k_out, -1, -1):
            x, y = lx + ox * k, ly + oy * k
            s, bid = self.walk_surface(x, y, dz)
            ctr = (x + 0.5, y + 0.5)
            if bid is not None and bid.endswith("_stairs"):
                lo, hi = s - 0.5, s + 0.5
                pts.append((ctr[0] + ox * 0.5, ctr[1] + oy * 0.5, lo))
                pts.append((ctr[0] - ox * 0.5, ctr[1] - oy * 0.5, hi))
            else:
                pts.append((ctr[0], ctr[1], s))
        s_in, _ = self.walk_surface(lx - ox, ly - oy, dz)
        pts.append((lx + 0.5 - ox * inside, ly + 0.5 - oy * inside, s_in))
        out_pt, in_pt = pts[0], pts[-1]
        return pts, out_pt, in_pt, door

    # ---- player-built trading hall ---------------------------------------------------------------

    def hall(self):
        """The player-built trading hall: six 1x1 cells along the south wall, job block in front of each villager,
        a trapdoor over each slot, iron-bar dividers between the cells so every villager can be seen from the aisle
        and each face sits in its window between two grilles."""
        w = self.w
        x0, y0 = HALL["x0"], HALL["y0"]
        x1 = x0 + 12
        yb, yc, yf = y0, y0 + 1, y0 + 2          # back wall, cell row, cell fronts (job blocks)
        ya0, ya1, yn = y0 + 3, y0 + 5, y0 + 6     # aisle rows, north arcade row
        for x in range(x0 - 2, x1 + 3):
            for y in range(y0 - 2, yn + 3):
                self.reserved.add((x, y))
        # floor: stone bricks under the cells, oak planks along the aisle, stone bricks under the arcade
        for x in range(x0, x1 + 1):
            for y in range(y0, yn + 1):
                w.set(x, y, -1, "oak_planks" if ya0 <= y <= ya1 else "stone_bricks")
        for i in range(13):
            x = x0 + i
            w.fill(x, yb, 0, x, yb, 2, "stone_bricks")                      # back wall
            if i % 2 == 0:
                if i in (0, 12):
                    w.fill(x, yc, 0, x, yf, 2, "stone_bricks")              # end walls of the cell block
                else:
                    # Iron bars between neighbouring cells, one block back from the fronts; in front of them every
                    # pier is just a stone-brick base, open above. (A solid pier hid the next cell from along the
                    # aisle. Bars on the pier fronts too made one pane two blocks deep beside every villager, and
                    # any camera looking along the row saw every face through that grille, a bar across each: now
                    # the faces are clear in their windows and the grilles stand BETWEEN them.)
                    w.fill(x, yc, 0, x, yc, 2, "iron_bars")
                    w.set(x, yf, 0, "stone_bricks")
                    if i in (4, 8):
                        w.set(x, yf, 2, "iron_bars")
                    else:
                        # on every other pier a lantern hangs from the ceiling: a lantern standing on the counter
                        # sat at face height, right in front of the next villager's face
                        w.set(x, yf, 2, "lantern", {"hanging": "true"})
                        self.torches.append(("hall", "lantern", {"hanging": "true"}, (x, yf, 2)))
                w.fill(x, yn, 0, x, yn, 2, "stripped_oak_log", {"axis": "y"})   # arcade posts
            else:
                n = i // 2
                job = HALL_JOBS[n]
                p = {}
                if job in ("lectern", "blast_furnace", "stonecutter"):
                    p = {"facing": "north"}
                if job == "blast_furnace":
                    p["lit"] = "false"
                w.set(x, yf, 0, job, p)
                w.set(x, yf, 2, "iron_bars")
        # flat player-style roof: planks over the cells, slabs over the aisle, a log beam on the arcade
        for x in range(x0, x1 + 1):
            for y in range(y0, yn + 1):
                if y == yn:
                    w.set(x, y, 3, "stripped_oak_log", {"axis": "x"})
                elif y >= ya0:
                    w.set(x, y, 3, "oak_slab", {"type": "top"})
                else:
                    w.set(x, y, 3, "oak_planks")
        for x in range(x0 - 1, x1 + 2):
            w.set(x, y0 - 1, 3, "stone_brick_slab", {"type": "bottom"})
            w.set(x, yn + 1, 3, "oak_slab", {"type": "bottom"})
        # the aisle ends are open archways under a stone-brick lintel
        for x in (x0, x1):
            w.fill(x, ya0, 3, x, ya1, 3, "stone_bricks")
        # railings in the arcade except the middle bays, which are the way in from the south street
        for i in range(1, 12, 2):
            x = x0 + i
            if x in (-2, 0):
                continue
            w.set(x, yn, 0, "oak_fence")
        # lanterns: two hanging over the aisle, two on the entrance posts outside
        for cell in ((x0 + 3, ya1, 2), (x0 + 9, ya1, 2), (-3, yn + 1, 2), (1, yn + 1, 2)):
            w.set(*cell, "lantern", {"hanging": "true"})
            self.torches.append(("hall", "lantern", {"hanging": "true"}, cell))
        v = self.v
        for n in range(6):
            x = x0 + 1 + 2 * n
            v.anchors["cell_%d" % (n + 1)] = (x + 0.5, yc + 0.70, 0.0)      # up against the job block, arms over it
            v.yaws["cell_%d" % (n + 1)] = yaw_of("north")
            v.anchors["cell_%d_station" % (n + 1)] = (x + 0.5, yf + 0.5, 0.5)
        v.anchors["hall_aisle_start"] = (x0 - 2.5, ya0 + 1.5, 0.0)
        v.anchors["hall_aisle_end"] = (x1 + 3.5, ya0 + 1.5, 0.0)
        v.anchors["hall_entrance"] = (0.5, yn + 2.5, -1.0 / 16.0)
        v.anchors["hall_center"] = (0.5, ya0 + 1.5, 0.0)
        for y in range(yn + 1, -26):
            for x in (-2, -1, 0):
                self.pave(x, y)

    # ---- lamps, nature ---------------------------------------------------------------------------

    def lamps(self):
        """Vanilla plains_lamp_1 posts."""
        t = structures.load_template("village/plains/plains_lamp_1")
        for i, (x, y) in enumerate(LAMPS):
            pl = self.w.place_template(t, (x - 1, y - 1, 0), 0)
            self.reserved.add((x, y))
            for bx, by, bz, bid, p in pl.blocks:
                if bid == "wall_torch":
                    self.torches.append(("lamp", bid, p, (bx, by, bz)))
        # The vanilla meeting point has no light on the bell's side: its torches sit on the well roof, which shades
        # the bell from them. Two player-built lamps (cobblestone foot, two oak fence posts, a lantern on top) flank
        # the bell, two blocks to its south-west and south-east: the practicals that key the bell's broad south face
        # and whoever rings it. Each is its own light group ('bell_w', 'bell_e'), so a shot can make either one its
        # key and keep the other as a rim, or switch its light off.
        w = self.w
        for x, y, group in BELL_LAMPS:
            w.set(x, y, -1, "cobblestone")
            w.set(x, y, 0, "oak_fence")
            w.set(x, y, 1, "oak_fence")
            w.set(x, y, 2, "lantern", {"hanging": "false"})
            self.torches.append((group, "lantern", {"hanging": "false"}, (x, y, 2)))
            self.reserved.add((x, y))
            self.v.anchors[group.replace("bell_", "bell_lamp_")] = props.flame_position(
                (x, y, 2), "lantern", {"hanging": "false"})

    def tree(self, x, y, rng, where="set"):
        """A vanilla small oak: 4-6 logs, two 5x5 leaf layers and two 3x3 layers with randomly missing corners.
        Returns its record (also appended to self.trees): dict(kind, x, y, base, height, logs, leaves, where)."""
        w = self.w
        base = self.surface_z(x, y)
        if base == -99:
            return
        h = 4 + int(rng.integers(0, 3))
        rec = dict(kind="oak", x=x, y=y, base=base, height=h, logs=[], leaves=[], where=where)
        w.set(x, y, base - 1, "dirt")
        leaf = {"persistent": "false", "distance": "1", "waterlogged": "false"}
        for i, r in ((h - 3, 2), (h - 2, 2), (h - 1, 1), (h, 1)):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) == r and abs(dy) == r and (i == h or rng.random() < 0.5):
                        continue
                    if w.get(x + dx, y + dy, base + i) is None:
                        w.set(x + dx, y + dy, base + i, "oak_leaves", leaf)
                        rec["leaves"].append((x + dx, y + dy, base + i))
        for i in range(h):
            w.set(x, y, base + i, "oak_log", {"axis": "y"})
            rec["logs"].append((x, y, base + i))
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                self.reserved.add((x + dx, y + dy))
        self.trees.append(rec)
        return rec

    def hay_pile(self, x, y, rng, n=5):
        """A small heap of hay bales with random grain, like the hay piles the game scatters in plains villages."""
        w = self.w
        cells = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1), (-1, 0, 0), (0, -1, 0)]
        for dx, dy, dz in cells[:n]:
            if w.get(x + dx, y + dy, dz) is None:
                w.set(x + dx, y + dy, dz, "hay_block", {"axis": "xyz"[int(rng.integers(0, 3))]})
            self.reserved.add((x + dx, y + dy))

    def nature(self):
        w, rng = self.w, self.rng
        self.hay_pile(12, -3, rng, 5)
        self.hay_pile(-7, -11, rng, 6)
        self.hay_pile(-26, -14, rng, 4)
        # hand-placed oaks inside the village, then a scattered ring outside (none in the meadow corridor)
        trees = [(5, -21), (25, -6), (-14, -17), (-13, 13), (13, 13), (24, -19), (-28, 13), (30, 6)]
        for x, y in trees:
            if (x, y) not in self.reserved:
                self.tree(x, y, rng, "village")
        placed = list(trees)
        tries = 0
        while len(placed) < 78 and tries < 6000:
            tries += 1
            x, y = int(rng.integers(-R + 6, R - 6)), int(rng.integers(-R + 6, R - 6))
            if x * x + y * y > (R - 8) ** 2 or self.dist[x + R, y + R] < 5:
                continue
            if y > 14 and abs(x) < 16 + (y - 14) * 0.25:
                continue
            if any(abs(x - a) < 5 and abs(y - b) < 5 for a, b in placed):
                continue
            if any((x + dx, y + dy) in self.reserved for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                continue
            self.tree(x, y, rng, "ring")
            placed.append((x, y))
        # short grass, tall grass and flowers on open grass
        for ix in range(2 * R):
            for iy in range(2 * R):
                h = self.height[ix, iy]
                if h == -99:
                    continue
                x, y = ix - R, iy - R
                if (x, y) in self.reserved or w.block_id(x, y, h - 1) != "grass_block" or w.get(x, y, h) is not None:
                    continue
                far = x * x + y * y
                if far > 62 * 62:
                    continue
                r = rng.random()
                dens = 0.16 if self.dist[ix, iy] > 0 else 0.10
                if far > 44 * 44:
                    dens *= 0.5
                if r < dens:
                    w.set(x, y, h, "short_grass")
                elif r < dens + 0.012 and w.get(x, y, h + 1) is None:
                    w.set(x, y, h, "tall_grass", {"half": "lower"})
                    w.set(x, y, h + 1, "tall_grass", {"half": "upper"})
                elif r < dens + 0.024:
                    w.set(x, y, h, "poppy" if rng.random() < 0.5 else "dandelion")
                elif r < dens + 0.028:
                    w.set(x, y, h, "oxeye_daisy" if rng.random() < 0.6 else "cornflower")
        # The meadow's lone oaks go in only now, with their own random stream: placed earlier, the columns they reserve
        # would shift the random sequence above and move every tuft and flower of the village.
        trng = np.random.default_rng(self.seed + 4100)
        for x, y in MEADOW_OAKS:
            for dz in (0, 1):
                if w.block_id(x, y, self.surface_z(x, y) + dz) in ("short_grass", "tall_grass", "poppy", "dandelion",
                                                                    "oxeye_daisy", "cornflower"):
                    w.set(x, y, self.surface_z(x, y) + dz, None)
            self.tree(x, y, trng, "meadow")
        # Second pass, from its own random stream (so everything placed above stays exactly where it was):
        # (a) the far end of the meadow, beyond the 62-block plant radius, gets its tufts too;
        # (b) tufts, tall grass and flowers crowd along every 1-block step of the terrain away from the village
        #     (thickest in the meadow), so a rise reads as a grown-over bank, not as a bare dirt wall.
        erng = np.random.default_rng(self.seed + 4101)
        flowers = ("poppy", "dandelion", "oxeye_daisy", "cornflower")
        for ix in range(1, 2 * R - 1):
            for iy in range(1, 2 * R - 1):
                h = self.height[ix, iy]
                if h == -99:
                    continue
                x, y = ix - R, iy - R
                in_meadow = self.wedge[ix, iy] > 0.3
                dist = self.dist[ix, iy]
                far = x * x + y * y
                around = self.height[ix - 1:ix + 2, iy - 1:iy + 2]
                edge = around.max() != around.min() and around.min() != -99 and \
                    ((in_meadow and dist > 7) or (dist > 9 and far <= 70 * 70))
                beyond = in_meadow and far > 62 * 62
                if not (edge or beyond):
                    continue
                r2 = erng.random()
                if (x, y) in self.reserved or w.block_id(x, y, h - 1) != "grass_block" or w.get(x, y, h) is not None:
                    continue
                if edge:
                    r2 *= 1.0 if in_meadow else 1.5
                    if r2 < 0.42:
                        w.set(x, y, h, "short_grass")
                    elif r2 < 0.58 and w.get(x, y, h + 1) is None:
                        w.set(x, y, h, "tall_grass", {"half": "lower"})
                        w.set(x, y, h + 1, "tall_grass", {"half": "upper"})
                    elif r2 < 0.66:
                        w.set(x, y, h, flowers[int(erng.integers(0, 4))])
                elif r2 < 0.10:
                    w.set(x, y, h, "short_grass")
                elif r2 < 0.115:
                    w.set(x, y, h, flowers[int(erng.integers(0, 4))])

        # the camera lane beside the exit road (see CAMERA_LANE): cleared afterwards, so no random number is skipped
        # and every other tuft and flower of the set stays where it was
        (lx0, lx1), (ly0, ly1) = CAMERA_LANE
        plants = ("short_grass", "tall_grass", "poppy", "dandelion", "oxeye_daisy", "cornflower")
        for x in range(lx0, lx1 + 1):
            for y in range(ly0, ly1 + 1):
                h = self.surface_z(x, y)
                for dz in (0, 1):
                    if w.block_id(x, y, h + dz) in plants:
                        w.set(x, y, h + dz, None)

    # ---- anchors and paths -----------------------------------------------------------------------

    def anchors(self):
        """Named standing spots, look targets and facing yaws."""
        v, w = self.v, self.w
        A, Y = v.anchors, v.yaws
        path_z = -1.0 / 16.0
        # bell
        well = v.buildings["well"]
        bell_cell = well.find("bell")[0]
        self.bell_cell = bell_cell
        A["bell"] = (bell_cell[0] + 0.5, bell_cell[1] + 0.5, bell_cell[2] + 0.6)
        A["bell_ringer"] = (bell_cell[0] + 0.5, bell_cell[1] - 1.0, path_z)
        Y["bell_ringer"] = yaw_of("north")
        A["well"] = (-0.5, -0.5, 2.0)
        A["square_n"] = (0.5, 7.0, path_z)
        A["square_e"] = (7.5, 0.5, path_z)
        A["square_s"] = (0.5, -8.0, path_z)
        A["square_w"] = (-8.0, 0.5, path_z)
        A["square_center"] = (0.5, -6.0, path_z)
        for i, (x, y) in enumerate([(2.6, -6.8), (-4.6, -7.2), (5.8, -3.4), (-6.4, -1.8), (6.2, 4.6), (-5.6, 5.4),
                                    (0.8, 6.4), (3.6, -8.4)], 1):
            A["square_%d" % i] = (x, y, path_z)
            Y["square_%d" % i] = yaw_to((x, y), A["bell"])
        A["trade_player"] = (4.4, -6.5, path_z)
        A["trade_villager"] = (6.0, -6.5, path_z)
        A["trade_nitwit"] = (5.4, 1.6, path_z)
        Y["trade_player"] = yaw_of("east")
        Y["trade_villager"] = yaw_of("west")
        Y["trade_nitwit"] = yaw_of("south")

        # houses: entry polylines, door anchors, beds
        self.entry = {}
        for name in self.entries:
            if name == "smithy":
                continue
            pts, out_pt, in_pt, door = self.entry_points(name)
            self.entry[name] = pts
            A[name + "_door_out"] = out_pt
            A[name + "_door_in"] = in_pt
            A[name + "_door"] = (door[0] + 0.5, door[1] + 0.5, door[2] + 1.0)
            Y[name + "_door_out"] = yaw_of(rotate_facing(self.entries[name]["out"], 2))
            Y[name + "_door_in"] = yaw_of(self.entries[name]["out"])
        for name in HOUSES:
            pl = v.buildings[name]
            n = 0
            for bx, by, bz, bid, p in sorted(pl.blocks, key=lambda b: (b[2], b[0], b[1])):
                if bid.endswith("_bed") and p.get("part") == "foot":
                    dx, dy = _VEC[p["facing"]]
                    n += 1
                    key = "%s_bed_%d" % (name, n)
                    color = self.bed_colors.get(key)
                    if color:                       # a film's own bed (e.g. the iconic red one): both halves re-dyed
                        w.set(bx, by, bz, color + "_bed", dict(p))
                        w.set(bx + dx, by + dy, bz, color + "_bed", dict(p, part="head"))
                    top = bz + 9.0 / 16.0
                    A[key] = (bx + 0.5 + dx * 0.5, by + 0.5 + dy * 0.5, top)
                    # facing = compass direction from the foot of the bed to its pillow; yaw = that direction as a yaw
                    v.beds[key] = dict(pos=A[key], head=(bx + 0.5 + dx, by + 0.5 + dy, top), foot=(bx + 0.5, by + 0.5, top),
                                       yaw=yaw_of(p["facing"]), facing=p["facing"])
                    Y[key] = v.beds[key]["yaw"]

        # house_a interior (medium_house_1): standing spots, camera corner
        a = v.buildings["house_a"]

        def at(pl, tx, ty, tz, dz=0.0):
            c = pl.pos(int(math.floor(tx)), int(ty), int(math.floor(tz)))
            fx, fz = tx - math.floor(tx), tz - math.floor(tz)
            # rotate the in-cell fraction with the placement
            r = pl.rot
            if r == 0:
                ux, uy = fx, 1 - fz
            elif r == 1:
                ux, uy = 1 - fz, 1 - fx
            elif r == 2:
                ux, uy = 1 - fx, fz
            else:
                ux, uy = fz, fx
            return (c[0] + ux, c[1] + uy, c[2] + dz)

        self.at = at
        A["house_a_inside_1"] = at(a, 4.5, 2, 5.5)
        A["house_a_inside_2"] = at(a, 6.5, 2, 7.2)
        A["house_a_inside_3"] = at(a, 7.6, 2, 4.8)
        A["house_a_inside_4"] = at(a, 3.4, 2, 7.6)
        door_a = A["house_a_door"]
        for i in (1, 2, 3, 4):
            Y["house_a_inside_%d" % i] = yaw_to(A["house_a_inside_%d" % i], door_a)
        A["house_a_cam"] = at(a, 10.45, 2, 8.45, dz=1.75)
        A["house_a_cam_beds"] = at(a, 10.6, 2, 6.5, dz=1.25)   # between the two bed heads, under the wall torch
        A["house_a_cam_target"] = (door_a[0], door_a[1], door_a[2] + 0.3)
        A["house_a_center"] = at(a, 6.0, 2, 6.5, dz=0.9)

        # workstations
        farm = v.buildings["farm"]
        for bx, by, bz, bid, p in farm.blocks:      # a farm that is being worked: mostly grown wheat, some young
            if bid == "wheat":
                r = pos_hash(bx, by, bz, 3) % 100
                w.set(bx, by, bz, "wheat", {"age": "7" if r < 58 else str(2 + r % 5)})
        comp = farm.pos(11, 1, 1)
        A["farm_station"] = (comp[0] + 0.5, comp[1] + 0.5, comp[2] + 0.5)
        stand = farm.pos(11, 1, 2)
        w.set(*stand, None)                                   # the farmer stands where one wheat plant was
        A["farm_work"] = (stand[0] + 0.5, stand[1] + 0.5, stand[2] - 1.0 / 16.0)
        Y["farm_work"] = yaw_to(A["farm_work"], A["farm_station"])
        comp2 = farm.pos(1, 1, 1)
        stand2 = farm.pos(1, 1, 2)
        w.set(*stand2, None)
        A["farm_station_2"] = (comp2[0] + 0.5, comp2[1] + 0.5, comp2[2] + 0.5)
        A["farm_work_2"] = (stand2[0] + 0.5, stand2[1] + 0.5, stand2[2] - 1.0 / 16.0)
        Y["farm_work_2"] = yaw_to(A["farm_work_2"], A["farm_station_2"])
        self.reserved.add((stand[0], stand[1]))

        lib = v.buildings["library"]
        lec = lib.pos(5, 1, 6)
        A["library_station"] = (lec[0] + 0.5, lec[1] + 0.5, lec[2] + 0.9)
        A["library_work"] = at(lib, 5.5, 1, 7.45)
        Y["library_work"] = yaw_to(A["library_work"], A["library_station"])
        lec2 = lib.pos(5, 1, 10)
        A["library_station_2"] = (lec2[0] + 0.5, lec2[1] + 0.5, lec2[2] + 0.9)
        A["library_work_2"] = at(lib, 5.5, 1, 9.55)
        Y["library_work_2"] = yaw_to(A["library_work_2"], A["library_station_2"])
        A["library_cam"] = at(lib, 2.6, 1, 8.5, dz=1.5)

        sm = v.buildings["smithy"]
        gr = sm.pos(2, 1, 1)
        A["smithy_station"] = (gr[0] + 0.5, gr[1] + 0.5, gr[2] + 0.6)
        A["smithy_work"] = at(sm, 3.55, 1, 1.5)
        Y["smithy_work"] = yaw_to(A["smithy_work"], A["smithy_station"])

        # exit and the edge of the village
        A["exit_gate"] = (0.5, 24.5, path_z)
        A["meadow_far"] = (0.5, 46.0, self.v.ground(0, 46))
        A["nitwit_idle"] = (9.5, 30.0, self.v.ground(9, 30))
        Y["nitwit_idle"] = yaw_of("north")
        Y["exit_gate"] = yaw_of("north")

    def paths(self):
        """Named walkable polylines (z follows the walking surface, stairs included)."""
        v = self.v
        P = v.paths
        pz = -1.0 / 16.0

        def ground(pts):
            out = []
            for x, y in pts:
                cx, cy = int(math.floor(x)), int(math.floor(y))
                h = self.surface_z(cx, cy)
                s, _ = self.walk_surface(cx, cy, h)
                out.append((x, y, s))
            return out

        starts = {
            "house_a": [(0.5, -6.5), (5.0, -7.2)],
            "house_b": [(2.5, -6.0), (6.2, -4.0), (7.6, 2.0)],
            "house_c": [(-3.5, -6.0), (-6.6, -4.0), (-8.2, 2.0)],
            "house_d": [(-5.0, -7.0), (-9.0, -0.5), (-17.0, 0.4)],
            "house_e": [(-1.5, -6.5), (-6.8, -3.0), (-7.4, 5.5), (-1.6, 9.5)],
            "house_f": [(1.5, -7.0), (6.8, -3.0), (7.0, 5.0), (1.6, 9.5)],
            "house_g": [(-0.5, -7.0), (0.4, -12.0)],
        }
        for name, lead in starts.items():
            if name not in self.entry:
                continue
            entry = self.entry[name]
            pts = ground(lead)
            # approach the door square-on: a waypoint in line with the entrance, 1 block further out
            P["square_to_" + name] = pts + entry
        P["exit_road"] = ground([(0.5, 6.0), (0.5, 12.0), (0.3, 20.0), (0.5, 24.5), (0.6, 31.0), (0.4, 38.0),
                                 (0.5, 46.0), (0.8, 54.0)])
        P["street_east"] = ground([(8.0, 0.2), (15.0, -0.3), (22.0, 0.3), (28.5, 0.0)])
        P["street_west"] = ground([(-8.5, 0.2), (-15.0, -0.2), (-21.0, 0.3), (-24.2, 0.4)])
        P["street_south"] = ground([(0.4, -9.0), (0.2, -15.0), (0.5, -21.0), (0.5, -25.2)])
        P["street_to_hall"] = P["street_south"] + [(0.5, -26.5, 0.0), (0.5, -28.5, 0.0)]
        P["hall_aisle"] = [v.anchors["hall_aisle_start"], v.anchors["hall_aisle_end"]]
        P["square_loop"] = ground([(0.5, -7.5), (6.3, -6.5), (6.9, 0.0), (6.0, 6.5), (0.0, 7.0), (-6.5, 6.0),
                                   (-7.5, 0.0), (-6.5, -6.5), (0.5, -7.5)])
        P["nitwit_leaves"] = ground([(5.4, 1.6), (1.5, 7.0), (0.5, 12.0), (0.3, 20.0), (0.5, 24.5), (0.6, 31.0),
                                     (0.4, 38.0), (0.5, 46.0), (0.8, 54.0)])

    # ---- props, mesh, lights ---------------------------------------------------------------------

    def props_and_mesh(self):
        """Animated doors and bell as props; everything else meshed (cutaway sections separately)."""
        v, w = self.v, self.w
        coll = v.collection
        skip = set()
        # animated doors
        for name, e in self.entries.items():
            objs = []
            for cell in e["doors"]:
                bid, p = w.get(*cell)
                d = props.make_door(bid, p.get("hinge", "left"), coll)
                props.place_door(d, cell, p.get("facing", "east"))
                d.name = "door_" + name + ("" if not objs else "_%d" % (len(objs) + 1))
                objs.append(d)
                for dz in (0, 1):
                    skip.add((cell[0], cell[1], cell[2] + dz))
                    w.passable.add((cell[0], cell[1], cell[2] + dz))
            if objs:
                v.doors[name] = objs[0]
                v._door_sets[name] = objs
                for i, d in enumerate(objs[1:], 2):
                    v.doors["%s_%d" % (name, i)] = d
                    v._door_sets["%s_%d" % (name, i)] = [d]
        # the bell
        bid, p = w.get(*self.bell_cell)
        body = props.make_bell(p.get("attachment", "floor"), p.get("facing", "north"), coll)
        body.parent.location = (self.bell_cell[0] + 0.5, self.bell_cell[1] + 0.5, float(self.bell_cell[2]))
        v.bell = body
        skip.add(self.bell_cell)
        w.passable.discard(self.bell_cell)
        # cutaway sections are meshed on their own so they can be hidden
        a = v.buildings["house_a"]
        lib = v.buildings["library"]
        groups = {"house_a_roof": set(), "house_a_east": set(), "house_a_south": set(), "library_roof": set(),
                  "library_south": set()}
        ta = a.template
        for tx, ty, tz, bid, p in ta.blocks:
            c = a.pos(tx, ty, tz)
            if c in skip:
                continue
            if (tx >= 11 and ty >= 1) or (tx == 10 and bid == "wall_torch" and ty < 4):
                groups["house_a_east"].add(c)        # the whole east end: wall behind the beds, gable, eave
            elif ty >= 4:
                groups["house_a_roof"].add(c)
            elif tz >= 9 and ty >= 2:
                groups["house_a_south"].add(c)
        for tx, ty, tz, bid, p in lib.template.blocks:
            c = lib.pos(tx, ty, tz)
            if c in skip:
                continue
            if ty >= 3:
                groups["library_roof"].add(c)
            elif tz >= 15 and ty >= 1:
                groups["library_south"].add(c)
        taken = set()
        for cells in groups.values():
            taken |= cells
        v.objects = w.build(coll, "village", skip=skip | taken)
        total = w.last_face_count
        for gname, cells in groups.items():
            sub = World()
            sub._states, sub._state_ids = w._states, w._state_ids
            for c in cells:
                if c in w.blocks:                # (a film's edit hook may have taken a block of the section out)
                    sub.blocks[c] = w.blocks[c]
            objs = sub.build(coll, gname)
            total += sub.last_face_count
            v.cutaways[gname] = objs
        v.face_count = total
        # flames must not shadow their own light
        for ob in coll.objects:
            if ob.type == "MESH" and any(k in ob.name for k in ("block_torch", "block_lantern")):
                ob.visible_shadow = False

    def lights(self):
        """One warm point light per torch / lantern (close groups merged, far ones dropped)."""
        v = self.v
        coll = v.collection
        by_group = {}
        for group, bid, p, cell in self.torches:
            by_group.setdefault(group, []).append((bid, p, cell))

        def add(group, kind, pos, scale=1.0):
            ob = props.make_light(kind, coll)
            ob.location = pos
            ob.data.energy *= scale
            ob["base_energy"] = ob.data.energy
            ob["group"] = group
            ob.name = "light_%s_%d" % (group, len(v.lights.get(group, [])))
            v.lights.setdefault(group, []).append(ob)
            v.lantern_lights.append(ob)

        for group, items in by_group.items():
            if group == "lamp":
                # a lamp post has four wall torches around one log: light the two that face along the street
                posts = {}
                for bid, p, cell in items:
                    dx, dy = _VEC[p["facing"]]
                    posts.setdefault((cell[0] - dx, cell[1] - dy), []).append((bid, p, cell))
                for (px, py), ts in posts.items():
                    along_x = abs(py) <= 4 and abs(px) > 4
                    for bid, p, cell in ts:
                        if (p["facing"] in ("east", "west")) == along_x:
                            add("lamp", "torch", props.flame_position(cell, bid, p), 1.15)
                continue
            if group in ("hall", "bell_w", "bell_e"):
                for bid, p, cell in items:
                    add(group, "lantern", props.flame_position(cell, bid, p))
                continue
            if group in self.set_groups:     # torches and lanterns of a film's edit hook: one light each, unmerged
                for bid, p, cell in items:
                    add(group, "lantern" if "lantern" in bid else "torch", props.flame_position(cell, bid, p))
                continue
            if group == "library":   # torches on the back wall and far corners only keep their glowing flame
                items = [it for it in items if not (it[2][0] <= -35 or (abs(it[2][1]) > 5 and it[2][2] < 4))]
            if group == "house_a":   # likewise the torch on the outside of the east wall
                items = [it for it in items if it[2][0] < 21]
            # everything else: merge torches that sit close together (door pairs, roof corners) into one light
            clusters = []
            for bid, p, cell in items:
                pos = props.flame_position(cell, bid, p)
                side = (p.get("facing"), cell[2])     # only torches on the same wall face and height are merged
                for c in clusters:
                    if c["side"] == side and math.dist(c["pos"], pos) < (6.5 if group == "well" else 2.6):
                        k = c["n"]
                        c["pos"] = tuple((c["pos"][i] * k + pos[i]) / (k + 1) for i in range(3))
                        c["n"] += 1
                        break
                else:
                    clusters.append(dict(pos=pos, n=1, side=side))
            for c in clusters:
                pos = c["pos"]
                if group == "well":
                    pos = (pos[0], pos[1], pos[2] + 0.35)
                add(group, "torch", pos, min(2.0, 1.0 + 0.45 * (c["n"] - 1)))
        # rooms that are filmed inside: one weak, cool, shadowless fill near the ceiling stands in for the light a
        # torch-lit room bounces around (Fast GI drops it), in the room's own light group so films scale it with
        # the torches. About a sixth of the room's torch light.
        for group, anchor, dz in (("house_a", "house_a_center", 1.6), ("hall", "hall_center", 2.2),
                                  ("library", "library_cam", 1.2)):
            if anchor in v.anchors and group in v.lights:
                torch_watts = sum(ob["base_energy"] for ob in v.lights[group])
                x, y, z = v.anchors[anchor]
                add(group, "fill", (x, y, z + dz), 0.16 * torch_watts / props.LIGHT_ENERGY["fill"])

    # ---- the film hook: what edit(b) may use (module docstring: FILM SETS) ------------------------

    def rng_for(self, tag):
        """A numpy random Generator of its own for one set piece, seeded by the village seed and `tag`."""
        import zlib

        return np.random.default_rng([int(self.seed), zlib.crc32(str(tag).encode("utf-8"))])

    def ground(self, x, y):
        """Terrain surface z of the column under (x, y) (the top of its grass block), or None where there is none."""
        h = self.surface_z(int(math.floor(x)), int(math.floor(y)))
        return None if h == -99 else h

    def walk_z(self, x, y):
        """Height a character stands at on the ground at (x, y) (a dirt_path is 1/16 lower than grass), or None."""
        cx, cy = int(math.floor(x)), int(math.floor(y))
        h = self.surface_z(cx, cy)
        return None if h == -99 else self.walk_surface(cx, cy, h)[0]

    def tree_at(self, x, y, radius=0.0):
        """The record (see tree()) of the oak whose trunk stands in column (x, y), or the nearest within `radius`."""
        best = None
        for t in self.trees:
            d = math.hypot(t["x"] - x, t["y"] - y)
            if d <= radius and (best is None or d < best[0]):
                best = (d, t)
        return best[1] if best else None

    def anchor(self, name, pos, yaw=None, replace=False):
        """Register a named standing spot / look target (a 2D position gets the walking height) and its facing yaw."""
        if name in self.v.anchors and not replace:
            raise KeyError("anchor %r exists already (replace=True to move it)" % name)
        if len(pos) == 2:
            z = self.walk_z(pos[0], pos[1])
            if z is None:
                raise ValueError("anchor %r: no terrain at %s" % (name, (pos,)))
            pos = (pos[0], pos[1], z)
        self.v.anchors[name] = tuple(float(a) for a in pos)
        if yaw is not None:
            self.v.yaws[name] = float(yaw)
        return self.v.anchors[name]

    def path(self, name, points, replace=False):
        """Register a named walkable polyline (2D points get the walking height there). Returns its 3D points."""
        if name in self.v.paths and not replace:
            raise KeyError("path %r exists already (replace=True to change it)" % name)
        pts = []
        for p in points:
            z = p[2] if len(p) > 2 else self.walk_z(p[0], p[1])
            if z is None:
                raise ValueError("path %r: no terrain at %s" % (name, (tuple(p),)))
            pts.append((float(p[0]), float(p[1]), float(z)))
        self.v.paths[name] = pts
        return pts

    PLANTS = ("short_grass", "tall_grass", "poppy", "dandelion", "oxeye_daisy", "cornflower")
    TERRAIN = ("grass_block", "dirt", "dirt_path")
    LIGHT_BLOCKS = ("torch", "wall_torch", "lantern")

    def _set_height(self, x, y, h):
        if -R <= x < R and -R <= y < R:
            self.height[x + R, y + R] = int(h)
            self.v._height[x + R, y + R] = float(h)
        else:
            self.ext[(x, y)] = int(h)            # (the same dict as Village._ext: Village.ground() reads it)
        tb = self.v.terrain_bounds
        self.v.terrain_bounds = (min(tb[0], x), min(tb[1], y), max(tb[2], x + 1), max(tb[3], y + 1))

    def _refill(self, x, y):
        """The rule of terrain() for one column after it or a neighbour changed height: dirt under the surface block
        down to the lowest neighbour, and the underside of the lowest block is never drawn."""
        h = self.surface_z(x, y)
        if h == -99:
            return
        w = self.w
        low = h
        for ax, ay in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            a = self.surface_z(ax, ay)
            if a != -99:
                low = min(low, a)
        bottom = h - 1
        for z in range(low, h - 1):
            if w.get(x, y, z) is None:
                w.set(x, y, z, "dirt")
            bottom = min(bottom, z)
        w.hidden_sides.add(((x, y, bottom), "down"))

    def clear_plants(self, x, y):
        """Remove the grass tuft / tall grass / flower that grows on the terrain column (x, y), if any."""
        h = self.surface_z(x, y)
        if h == -99:
            return
        for dz in (0, 1):
            if self.w.block_id(x, y, h + dz) in self.PLANTS:
                self.w.set(x, y, h + dz, None)

    def sow(self, x, y, rng, edge=None, density=1.0):
        """Let the meadow's own mix grow on the column (x, y), by chance: short grass 10 % and a flower 1.5 % on open
        ground, and the thick growth of a bank (short grass 42 %, tall grass 16 %, a flower 8 %) where the terrain
        steps (edge=None looks at the eight neighbours). Never on a path, a reserved or an occupied column.
        Returns the block id it planted, or None. One random number is drawn per call whatever happens."""
        w = self.w
        r2 = rng.random() / max(density, 1e-6)
        h = self.surface_z(x, y)
        if h == -99 or (x, y) in self.reserved or w.block_id(x, y, h - 1) != "grass_block" \
                or w.get(x, y, h) is not None:
            return None
        if edge is None:
            hs = [self.surface_z(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            edge = min(hs) != max(hs) and min(hs) != -99
        flowers = ("poppy", "dandelion", "oxeye_daisy", "cornflower")
        what = None
        if edge:
            if r2 < 0.42:
                what = "short_grass"
            elif r2 < 0.58 and w.get(x, y, h + 1) is None:
                what = "tall_grass"
            elif r2 < 0.66:
                what = flowers[int(rng.integers(0, 4))]
        elif r2 < 0.10:
            what = "short_grass"
        elif r2 < 0.115:
            what = flowers[int(rng.integers(0, 4))]
        if what == "tall_grass":
            w.set(x, y, h, "tall_grass", {"half": "lower"})
            w.set(x, y, h + 1, "tall_grass", {"half": "upper"})
        elif what:
            w.set(x, y, h, what)
        return what

    def set_ground(self, x, y, z):
        """Re-level the terrain column (x, y): its surface is at height z afterwards (a grass block, or a dirt_path
        if it was one). Plants on the old surface are removed, dirt is filled in under it and beside it; a column
        without terrain gets some. Blocks that are not terrain (a house, a tree trunk) are left alone."""
        w = self.w
        z = int(z)
        old = self.surface_z(x, y)
        if old == z:
            return
        top = ("grass_block", {"snowy": "false"})
        if old != -99:
            self.clear_plants(x, y)
            was = w.block_id(x, y, old - 1)
            if was == "dirt_path":
                top = ("dirt_path", None)
            if z < old:
                for zz in range(z, old):
                    if w.block_id(x, y, zz) in self.TERRAIN:
                        w.set(x, y, zz, None)
            elif was in self.TERRAIN:
                w.set(x, y, old - 1, "dirt")
                for zz in range(old, z - 1):
                    if w.get(x, y, zz) is None:
                        w.set(x, y, zz, "dirt")
        if w.get(x, y, z - 1) is None or w.block_id(x, y, z - 1) in self.TERRAIN:
            w.set(x, y, z - 1, top[0], top[1])
        self._set_height(x, y, z)
        for c in ((x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            self._refill(*c)

    def natural_height(self, x, y, rise=1.0 / MEADOW_STEP):
        """Height the terrain has, or would have, at column (x, y). Inside [-R, R) it is the village's own height
        field (computed for the whole square, built only inside the disc). Beyond the square the field's edge is
        carried on: plus `rise` blocks per block of distance (the meadow rises one block about every 11) and a
        gentle seeded noise that fades in over 8 blocks, so the 1-block steps wander as the meadow's do."""
        nat = self._natural if self._natural is not None else self.v._height
        if -R <= x < R and -R <= y < R:
            return int(nat[x + R, y + R])
        cx, cy = min(max(x, -R), R - 1), min(max(y, -R), R - 1)
        d = math.hypot(x - cx, y - cy)
        n = (_hash_noise(x, y, 11.0, self.seed) - 0.5) * 1.8 + (_hash_noise(x, y, 4.5, self.seed + 1) - 0.5) * 0.8
        return max(0, int(math.floor(float(nat[cx + R, cy + R]) + rise * d + n * min(1.0, d / 8.0) + 0.35)))

    def extend_terrain(self, x0, y0, x1, y1, plants=True, rise=1.0 / MEADOW_STEP, where=None):
        """Grass terrain for every column of the inclusive box that has none yet (the village's terrain is a disc of
        radius 83): heights from natural_height(), the meadow's plants on top (plants=False: bare grass), dirt
        sides filled against the old rim. where(x, y) -> bool limits the box to a shape. Returns the new columns."""
        w = self.w
        new = []
        for x in range(int(x0), int(x1) + 1):
            for y in range(int(y0), int(y1) + 1):
                if self.surface_z(x, y) != -99 or (where is not None and not where(x, y)):
                    continue
                new.append((x, y, self.natural_height(x, y, rise)))
        for x, y, h in new:
            self._set_height(x, y, h)
            if w.get(x, y, h - 1) is None:
                w.set(x, y, h - 1, "grass_block", {"snowy": "false"})
        touched = set()
        for x, y, h in new:
            touched.update(((x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
        for c in sorted(touched):
            self._refill(*c)
        if plants:
            rng = self.rng_for("extend_terrain %d %d %d %d" % (x0, y0, x1, y1))
            for x, y, h in new:                  # as nature() does: banks outside the meadow wedge grow two thirds as thick
                cx, cy = min(max(x, -R), R - 1), min(max(y, -R), R - 1)
                self.sow(x, y, rng, density=1.0 if self.wedge[cx + R, cy + R] > 0.3 else 1.0 / 1.5)
        return [(x, y) for x, y, h in new]

    def show_undersides(self, x0, y0, x1, y1):
        """Draw the underside of the terrain again inside a box of columns (terrain() never draws it: nothing could
        see it). For a set that is dug in under the ground."""
        self.w.hidden_sides = {(c, d) for (c, d) in self.w.hidden_sides
                               if not (x0 <= c[0] <= x1 and y0 <= c[1] <= y1)}

    def torch(self, cell, block_id="torch", props=None, group="set"):
        """Place a torch / wall_torch / lantern block and give it its point light, in light group `group`
        (Village.lights[group]; one light per block, never merged). A village group's name is refused."""
        if block_id not in self.LIGHT_BLOCKS:
            raise ValueError("no light is known for %r (use one of %s)" % (block_id, ", ".join(self.LIGHT_BLOCKS)))
        if group not in self.set_groups and any(t[0] == group for t in self.torches):
            raise ValueError("light group %r belongs to the village: choose another name" % group)
        p = dict(props or {})
        if block_id == "lantern":
            p.setdefault("hanging", "false")
        cell = tuple(int(c) for c in cell)
        self.w.set(cell[0], cell[1], cell[2], block_id, p)
        self.torches[:] = [t for t in self.torches if t[3] != cell]
        self.torches.append((group, block_id, p, cell))
        self.set_groups.add(group)

    def bed(self, name, foot_cell, facing="north", color="white"):
        """A bed with its foot at `foot_cell` and its pillow one block further in `facing`, with the anchor, yaw
        and Village.beds entry the houses' own beds have (Character.lie_down(frame, anchors[name], yaws[name]))."""
        bx, by, bz = (int(c) for c in foot_cell)
        dx, dy = _VEC[facing]
        self.w.set_bed(bx, by, bz, facing, color)
        top = bz + 9.0 / 16.0
        pos = (bx + 0.5 + dx * 0.5, by + 0.5 + dy * 0.5, top)
        self.v.anchors[name] = pos
        self.v.beds[name] = dict(pos=pos, head=(bx + 0.5 + dx, by + 0.5 + dy, top), foot=(bx + 0.5, by + 0.5, top),
                                 yaw=yaw_of(facing), facing=facing)
        self.v.yaws[name] = self.v.beds[name]["yaw"]
        return pos

    def door(self, name, cell, facing="north", hinge="left", block_id="oak_door"):
        """A door (lower half at `cell`) that becomes an animated prop like the houses' own: Village.doors[name],
        Village.door_open(name, frame). `facing` as in the game: the side the door was placed FROM."""
        if name in self.entries:
            raise KeyError("door %r exists already" % name)
        cell = tuple(int(c) for c in cell)
        self.w.set_door(cell[0], cell[1], cell[2], facing, hinge, block_id)
        self.entries[name] = dict(cell=cell, out=facing, doors=[cell])

    def allow(self, what):
        """Permit the hook to change blocks inside a building ('house_a' ... 'farm', 'well', 'hall'), on the
        'streets' (dirt paths and the two blocks of air above them), or anywhere in a box of columns (x0, y0, x1, y1)."""
        self.allowed.append(what)

    def changed(self):
        """{cell: ((block id, props) | None, (block id, props) | None)}: every cell whose block differs now from
        when the hook was called (before, after)."""
        w, before = self.w, self._before or {}
        out = {}
        for c, sid in w.blocks.items():
            old = before.get(c)
            if old != sid:
                out[c] = (None if old is None else w._states[old], w._states[sid])
        for c, old in before.items():
            if c not in w.blocks:
                out[c] = (w._states[old], None)
        return out

    def _after_edit(self):
        """Bring the builder's own lists in line with what the hook did to the World, and list what it changed
        where it should not have (see the module docstring)."""
        w, v = self.w, self.v
        changed = self.changed()
        if w.block_id(*self.bell_cell) != "bell":
            raise ValueError("village edit hook: the bell block is gone (the set needs it)")
        # torches: a removed one loses its light, a new one gets a light
        kept = []
        for group, bid, p, cell in self.torches:
            if cell in changed:
                st = w.get(*cell)
                if st is None or st[0] not in self.LIGHT_BLOCKS:
                    continue
                bid, p = st[0], dict(st[1])
            kept.append((group, bid, p, cell))
        self.torches[:] = kept
        have = {t[3] for t in self.torches}
        for cell in sorted(changed):
            st = w.get(*cell)
            if st is not None and st[0] in self.LIGHT_BLOCKS and cell not in have:
                self.torches.append((self.light_group, st[0], dict(st[1]), cell))
                self.set_groups.add(self.light_group)
        # doors and beds that are no longer there
        for e in self.entries.values():
            e["doors"] = [c for c in e.get("doors", []) if (w.block_id(*c) or "").endswith("_door")]
        for key in list(v.beds):
            cells = [tuple(int(math.floor(a)) for a in v.beds[key][k]) for k in ("foot", "head")]
            if any(not (w.block_id(*c) or "").endswith("_bed") for c in cells):
                del v.beds[key]
                v.anchors.pop(key, None)
                v.yaws.pop(key, None)
        # nothing inside a house or on a street by accident
        boxes = {name: pl.bounds for name, pl in v.buildings.items()}
        boxes["hall"] = (HALL["x0"], HALL["y0"], -1, HALL["x0"] + 12, HALL["y0"] + 6, 3)
        names = {a for a in self.allowed if isinstance(a, str)}
        free = [a for a in self.allowed if not isinstance(a, str)]
        hits = {}
        for (x, y, z) in sorted(changed):
            if any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in free):
                continue
            for name, (x0, y0, z0, x1, y1, z1) in boxes.items():
                if name not in names and x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
                    hits.setdefault(name, []).append((x, y, z))
            if "streets" not in names and (x, y) in self._streets_before:
                h = self.surface_z(x, y)
                if h != -99 and h - 1 <= z <= h + 1:
                    hits.setdefault("streets", []).append((x, y, z))
        return ["%d block(s) changed %s, e.g. at %s (b.allow(%r) if that is meant)" % (
            len(cells), "on the streets" if name == "streets" else "inside " + name, cells[0], name)
            for name, cells in sorted(hits.items())]

    def _report(self, problems):
        self.v.edit_problems = list(problems)
        if problems:
            text = "village edit hook: " + "; ".join(problems)
            if self.strict:
                raise ValueError(text)
            print("WARNING " + text)

    # ---- all together ----------------------------------------------------------------------------

    def build(self, edit=None):
        """Run every stage and return the Village. `edit(self)` is a film's hook (see the module docstring): it runs
        when the World, the anchors and the paths are complete and nothing has been made from them yet."""
        self.terrain()
        self.streets()
        self.buildings()
        self.entrances()
        self.hall()
        self.lamps()
        self.anchors()
        self.nature()
        self.paths()
        if edit is not None:
            self._before = dict(self.w.blocks)
            self._streets_before = set(self.path_cells)
            self._natural = self.v._height.copy()
            edit(self)
            problems = self._after_edit()
        self.props_and_mesh()
        self.lights()
        if edit is not None:
            self._report(problems + self.v.validate())
        return self.v


def build_village(scene, seed=1, bed_colors=None, edit=None):
    """Build the whole village set into `scene` and return its Village handle.

    edit (optional) is a film's set hook, edit(b): called with the builder when every block of the village is in
    the World and before anything is made from it (module docstring: FILM SETS; engine/sets.py has the set pieces).
    With edit=None the village is exactly the one of the finished films.

    bed_colors (optional) re-dyes single beds, e.g. {"house_a_bed_2": "red"}: the vanilla plains houses come with
    white (and yellow) beds, which is what you get by default; the red bed is the one everybody knows, and a film
    whose shot is ABOUT a bed (the client's reference 1 and 3 use the red one) may ask for it. Keys are the bed
    anchors (house_a_bed_1 = the south bed of house_a, house_a_bed_2 = the north one)."""
    # rows of crops, grass and leaves are many cut-out layers deep; with too few transparent bounces Cycles
    # renders them black
    try:
        scene.cycles.transparent_max_bounces = max(scene.cycles.transparent_max_bounces, 48)
    except Exception:
        pass
    return _Builder(scene, seed, bed_colors).build(edit)


# --------------------------------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------------------------------

def standin(collection, pos, color=(170, 120, 90, 255), name="standin", yaw=0.0):
    """A plain 0.6 x 0.6 x 1.95 box (villager-sized) for scale checks; a darker stripe marks its front."""
    import bmesh

    key = "standin_%02x%02x%02x" % tuple(color[:3])
    mat = bpy.data.materials.get(key)
    if mat is None:
        mat = bpy.data.materials.new(key)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = tuple((c / 255.0) ** 2.2 for c in color[:3]) + (1.0,)
        bsdf.inputs["Roughness"].default_value = 0.9
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for vtx in bm.verts:
        vtx.co.x *= 0.6
        vtx.co.y *= 0.6
        vtx.co.z = (vtx.co.z + 0.5) * 1.95
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.location = pos
    ob.rotation_euler = (0, 0, yaw)
    collection.objects.link(ob)
    return ob


def _selftest(only=None):
    import time

    from . import quick

    t0 = time.time()
    scene = quick.reset()
    quick.setup(scene)
    v = build_village(scene, seed=1)
    print("village built in %.1fs: %d faces, %d lights, %d doors, %d objects" % (
        time.time() - t0, v.face_count, len(v.lantern_lights), len(v.doors), len(v.objects)))
    problems = v.validate()
    print("validate:", problems if problems else "OK (all required anchors, paths and doors present, paths clear)")
    A = v.anchors
    coll = v.collection
    for i, name in enumerate(["bell_ringer", "house_a_inside_1", "house_a_inside_2", "house_a_inside_3", "farm_work",
                              "library_work", "smithy_work", "nitwit_idle", "trade_player", "trade_villager"]
                             + ["cell_%d" % k for k in range(1, 7)]):
        col = (60, 150, 60, 255) if name == "nitwit_idle" else ((70, 120, 170, 255) if "player" in name or
                                                                 name == "bell_ringer" else (170, 120, 90, 255))
        standin(coll, A[name], col, "standin_" + name, v.yaws.get(name, 0.0))

    def stage(preset, lights=1.0):
        for ob in [o for o in scene.objects if o.name.startswith("quick_")]:
            bpy.data.objects.remove(ob)
        quick.light(scene, preset)
        v.set_lantern_energy(lights)

    def shot(name, preset, pos, target, lens=35, fstop=None, lights=1.0):
        if only and name not in only:
            return
        stage(preset, lights)
        quick.camera(scene, pos, target, lens=lens, fstop=fstop)
        print("wrote", quick.render(scene, "village_" + name))

    bell = A["bell"]
    shot("overview", "day", (38, -62, 62), (0, -4, 0), lens=24, lights=0.3)
    shot("square", "golden", (5.5, -11.5, 1.6), (bell[0] - 0.6, bell[1] + 1.0, 1.9), lens=30, lights=0.6)
    v.set_door("house_a", True)
    shot("house_a_interior", "night", A["house_a_cam_beds"], A["house_a_cam_target"], lens=22, lights=2.0)
    v.set_door("house_a", False)
    hs, he = A["hall_aisle_start"], A["hall_aisle_end"]
    shot("hall", "golden", (hs[0] + 2.2, hs[1] + 1.1, 1.55), (he[0] - 9.0, hs[1] - 2.2, 1.2), lens=22, lights=1.0)
    shot("exit", "golden", (0.4, 6.0, 1.6), (0.5, 40, 2.6), lens=21, lights=0.6)
    shot("night", "night", (27.5, -0.4, 1.5), (4.0, 0.3, 2.8), lens=30, lights=1.0)
    # extra checks (not part of the required set)
    shot("x_house_a_day", "day", A["house_a_cam"], A["house_a_cam_target"], lens=18, lights=0.5)
    shot("x_smithy", "golden", (A["smithy_work"][0] - 1.5, -2.5, 1.5), A["smithy_station"], lens=30, lights=0.6)
    shot("x_farm", "golden", (A["farm_station"][0] + 1.5, 0.5, 1.6), A["farm_station"], lens=30, lights=0.6)
    lw = A["library_work"]
    shot("x_library", "day", A["library_cam"], (lw[0], lw[1], lw[2] + 1.3), lens=20, lights=1.0)
    shot("x_nitwit", "golden", (10.5, 36.0, 1.7), (9.3, 28.0, 1.3), lens=35, lights=0.6)
    shot("x_plaza_wide", "golden", (-9.5, -13.0, 5.5), (2.0, 2.0, 1.0), lens=22, lights=0.6)
    return v


if __name__ == "__main__":
    import sys

    _selftest(only=sys.argv[1:] or None)
