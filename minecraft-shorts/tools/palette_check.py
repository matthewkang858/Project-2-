"""Does a rendered still keep the game's palette, and are the hero subjects where a Reels viewer can see them?

The look stage (engine/look.py: sky fill, torch colour, grade) is the only place where a real Minecraft texture can
be pushed off-model, so every look-dev still is measured against the textures it was made from:

    rec = probe(scene)                         # after film.goto(frame): what does every pixel of the frame show?
    report = evaluate(rec, "out/test/lookdev_bell.png", heroes=[bell_object])
    print_report("bell", report)               # one line per check; report["failed"] lists the broken ones

probe() casts one ray per cell of a coarse grid through the shot camera (scene.ray_cast, cut-out texels and
camera-invisible cutaway walls are passed through) and looks up, for every hit, the object, the material and the
texel of the game texture under it. evaluate() then compares the picture with those texels, class by class:

    stone     neutral stone (cobblestone, stone, stone bricks)   lit pixels must not go magenta:  G >= 0.92 R
    robe      the villagers' brown robe texels                  hue must stay 0..30 degrees (texture: 11)
    planks    oak planks                                        lit pixels: saturation <= 0.68 (texture: 0.52)
    face      villager skin                                     saturation <= 0.52 (texture: 0.42)
    pants     Steve's indigo trousers                           no channel below 12 (nothing crushed to black)
    shirt     Steve's teal shirt (red is 0-2 in steve.png)      hue stays 170..196 (texture: 184)
    plants    grass / flowers / crops (cut-out cross models)    not darker than 0.55 x the lit ground they stand on

and checks the composition rule for the hero objects a shot names (faces, the bell, the emerald): most of what is
visible of them must lie inside the safe area of a Reel (see engine/post.py: side crop, icon column, caption band).
Only pixels whose neighbours show the same class are used (depth of field and motion blur mix the edges), and a
class needs MIN_PIXELS samples to be judged at all.
"""
import colorsys
import math

import bpy
import numpy as np
from mathutils import Vector
from mathutils.interpolate import poly_3d_calc

GRID = (72, 128)            # rays across / down the frame
MIN_PIXELS = 12
STONE = ("mc/block/cobblestone", "mc/block/stone", "mc/block/stone_bricks", "mc/block/smooth_stone",
         "mc/block/andesite")
PLANKS = ("mc/block/oak_planks",)
GROUND = ("mc/block/grass_block_top",)
PLANT_HINTS = ("short_grass", "tall_grass", "poppy", "dandelion", "oxeye_daisy", "cornflower", "wheat_stage")

_PIXELS = {}


def _image_pixels(img):
    """HxWx4 float array of a Blender image, row 0 = bottom (cached)."""
    key = img.name
    arr = _PIXELS.get(key)
    if arr is None or arr.shape[:2] != (img.size[1], img.size[0]):
        arr = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
        img.pixels.foreach_get(arr)
        arr = arr.reshape(img.size[1], img.size[0], 4)
        _PIXELS[key] = arr
    return arr


def _material_image(mat):
    """The game texture a material shows (its first Image Texture node), or None."""
    if mat is None or mat.node_tree is None:
        return None
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image is not None:
            return node.image
    return None


def _texel(ob, index, world_point, matrix):
    """(material name, rgba of the texture under a hit) for face `index` of mesh object `ob`."""
    me = ob.data
    if index < 0 or index >= len(me.polygons):
        return None, None
    poly = me.polygons[index]
    mat = me.materials[poly.material_index] if me.materials else None
    img = _material_image(mat)
    if img is None or not me.uv_layers:
        return (mat.name if mat else None), None
    local = matrix.inverted() @ world_point
    cos = [me.vertices[v].co for v in poly.vertices]
    weights = poly_3d_calc(cos, local)
    uvs = me.uv_layers.active.data
    u = sum(w * uvs[li].uv[0] for w, li in zip(weights, poly.loop_indices))
    v = sum(w * uvs[li].uv[1] for w, li in zip(weights, poly.loop_indices))
    px = _image_pixels(img)
    h, w = px.shape[:2]
    return mat.name, px[int(math.floor((v % 1.0) * h)) % h, int(math.floor((u % 1.0) * w)) % w]


def probe(scene, grid=GRID):
    """What the active camera sees at the current frame: {'grid', 'object', 'material', 'albedo'} arrays over a
    coarse grid (row 0 = TOP of the frame). object / material are names ('' = sky), albedo is the sRGB texel
    (0..1, NaN where there is none)."""
    cam = scene.camera
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    cam_eval = cam.evaluated_get(dg)
    mw = cam_eval.matrix_world
    frame = [mw @ v for v in cam_eval.data.view_frame(scene=scene)]      # top-right, bottom-right, bottom-left, top-left
    tr, br, bl, tl = frame
    origin = mw.translation.copy()
    gx, gy = grid
    objects = np.full((gy, gx), "", dtype=object)
    materials = np.full((gy, gx), "", dtype=object)
    albedo = np.full((gy, gx, 3), np.nan, dtype=np.float32)
    for j in range(gy):
        fy = (j + 0.5) / gy
        left = tl.lerp(bl, fy)
        right = tr.lerp(br, fy)
        for i in range(gx):
            d = (left.lerp(right, (i + 0.5) / gx) - origin).normalized()
            o = origin.copy()
            for _ in range(24):                                          # pass cut-outs and camera-invisible walls
                hit, loc, _n, index, ob, matrix = scene.ray_cast(dg, o, d)
                if not hit:
                    break
                orig = ob.original
                o = loc + d * 2e-4
                if orig.type != "MESH" or orig.hide_render or not orig.visible_camera or orig.name.startswith("look_"):
                    if orig.name.startswith("look_"):
                        break                                            # sky sprites: nothing but sky behind them
                    continue
                mname, texel = _texel(orig, index, loc, matrix)
                if texel is not None and texel[3] < 0.5:
                    continue
                objects[j, i] = orig.name
                materials[j, i] = mname or ""
                if texel is not None:
                    albedo[j, i] = texel[:3]
                break
    return {"grid": grid, "object": objects, "material": materials, "albedo": albedo}


def _hsv(rgb):
    h, s, v = colorsys.rgb_to_hsv(*[float(c) for c in rgb])
    return h * 360.0, s, v


def _interior(mask):
    """Cells whose four neighbours are in the mask too."""
    m = mask.copy()
    m[1:, :] &= mask[:-1, :]
    m[:-1, :] &= mask[1:, :]
    m[:, 1:] &= mask[:, :-1]
    m[:, :-1] &= mask[:, 1:]
    m[0, :] = m[-1, :] = False
    m[:, 0] = m[:, -1] = False
    return m


def _classes(rec):
    """Boolean masks per palette class from a probe() record."""
    obj, mat, alb = rec["object"], rec["material"], rec["albedo"]
    gy, gx = obj.shape
    hue = np.zeros((gy, gx))
    sat = np.zeros((gy, gx))
    val = np.zeros((gy, gx))
    for j in range(gy):
        for i in range(gx):
            if not np.isnan(alb[j, i, 0]):
                hue[j, i], sat[j, i], val[j, i] = _hsv(alb[j, i])
    is_mat = lambda names: np.isin(mat, names)                           # noqa: E731
    name_has = lambda arr, parts: np.array([[any(p in s for p in parts) for s in row] for row in arr])   # noqa: E731
    villager = name_has(mat, ("cast_villager",))
    steve = name_has(mat, ("cast_player",))
    out = {
        "stone": is_mat(STONE) & (sat < 0.12) & (val > 0.35),
        "planks": is_mat(PLANKS),
        "robe": villager & name_has(obj, ("_body", "_arms")) & ((hue <= 30) | (hue >= 350)) & (sat > 0.18) & (sat < 0.5)
        & (val > 0.25) & (val < 0.6),
        "face": villager & name_has(obj, ("_head",)) & (hue >= 8) & (hue <= 28) & (sat > 0.28) & (sat < 0.56) & (val > 0.6),
        "shirt": steve & (hue > 165) & (hue < 195) & (sat > 0.5),
        "pants": steve & (hue > 225) & (hue < 255) & (sat > 0.4),
        "ground": is_mat(tuple(m for m in set(mat.ravel()) if any(g in m for g in GROUND))),
        "plants": name_has(mat, PLANT_HINTS),
    }
    return out


def _median(img, mask, grid):
    """Median sRGB (0..255) of the picture over the grid cells of `mask`, and the per-cell colours."""
    gx, gy = grid
    w, h = img.shape[1], img.shape[0]
    js, is_ = np.nonzero(mask)
    if not len(js):
        return None, np.zeros((0, 3))
    ys = np.clip(((js + 0.5) / gy * h).astype(int), 0, h - 1)
    xs = np.clip(((is_ + 0.5) / gx * w).astype(int), 0, w - 1)
    cols = img[ys, xs, :3].astype(np.float32)
    return np.median(cols, axis=0), cols


def evaluate(rec, image_path, heroes=(), safe=None):
    """Compare a rendered still with what probe() saw. Returns {'checks': [(name, ok, text)], 'failed': [...],
    'colours': {class: (r, g, b)}, 'heroes': {...}}. heroes: objects (or names) that must sit in the safe area."""
    from PIL import Image

    from engine import post

    safe = safe or post.SAFE_AREA
    img = np.asarray(Image.open(image_path).convert("RGB"))
    grid = rec["grid"]
    classes = _classes(rec)
    checks, colours = [], {}

    def add(name, ok, text):
        checks.append((name, bool(ok), text))

    def lit(cols, floor):
        v = cols.max(axis=1) / 255.0
        return cols[v > floor]

    for name, mask in classes.items():
        med, cols = _median(img, _interior(mask), grid)
        if med is None or len(cols) < MIN_PIXELS:
            continue
        colours[name] = tuple(int(round(c)) for c in med)
        r, g, b = med
        hue, sat, val = _hsv(med / 255.0)
        if name == "stone":
            c = lit(cols, 0.25)
            if len(c) >= MIN_PIXELS:
                m = np.median(c, axis=0)
                add("stone not magenta", m[1] >= 0.92 * m[0], "lit stone rgb(%d,%d,%d): G/R %.2f (>= 0.92)"
                    % (m[0], m[1], m[2], m[1] / max(m[0], 1)))
        elif name == "robe":
            ok = hue <= 30.0 or hue >= 358.0
            add("robe hue", ok, "robe rgb(%d,%d,%d): hue %.0f (0..30, texture 11)" % (r, g, b, hue))
        elif name == "planks":
            c = lit(cols, 0.30)
            if len(c) >= MIN_PIXELS:
                m = np.median(c, axis=0)
                s = _hsv(m / 255.0)[1]
                add("planks saturation", s <= 0.68, "lit oak planks rgb(%d,%d,%d): s %.2f (<= 0.68, texture 0.52)"
                    % (m[0], m[1], m[2], s))
        elif name == "face":
            add("face saturation", sat <= 0.52, "villager skin rgb(%d,%d,%d): s %.2f (<= 0.52, texture 0.42)"
                % (r, g, b, sat))
        elif name == "pants":
            add("steve pants not clipped", min(r, g, b) >= 12, "steve pants rgb(%d,%d,%d): min channel %d (>= 12, "
                "texture (70, 58, 165))" % (r, g, b, min(r, g, b)))
        elif name == "shirt":
            # the shirt's red channel is 0-2 in steve.png itself, so "no channel below 12" cannot apply to it; the
            # look must keep it the texture's teal (hue 184) instead of pulling it green or blue
            add("steve shirt hue", 170.0 <= hue <= 196.0, "steve shirt rgb(%d,%d,%d): hue %.0f (170..196, texture 184)"
                % (r, g, b, hue))
    if "plants" in colours and "ground" in colours:
        pv, gv = max(colours["plants"]), max(colours["ground"])
        add("plants lit like the ground", pv >= 0.55 * gv, "plants rgb%s vs grass top rgb%s: value ratio %.2f (>= 0.55)"
            % (colours["plants"], colours["ground"], pv / max(gv, 1)))

    # composition: hero objects inside the safe area
    hero_out = {}
    gx, gy = grid
    (x0, x1), (y0, y1) = safe["x"], safe["y"]
    for hero in heroes:
        label, names = hero if isinstance(hero, tuple) else (getattr(hero, "name", str(hero)), [hero])
        names = [getattr(n, "name", n) for n in names]
        mask = np.isin(rec["object"], names)
        js, is_ = np.nonzero(mask)
        if not len(js):
            add("hero %s visible" % label, False, "hero '%s' is not in the picture" % label)
            continue
        xs, ys = (is_ + 0.5) / gx, (js + 0.5) / gy
        inside = (xs >= x0) & (xs <= x1) & (ys >= y0) & (ys <= y1)
        frac = float(inside.mean())
        cx, cy = float(xs.mean()), float(ys.mean())
        box = (float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max()))
        hero_out[label] = dict(centre=(cx, cy), box=box, inside=frac)
        ok = frac >= 0.7 and x0 <= cx <= x1 and y0 <= cy <= y1
        add("hero %s in safe area" % label, ok, "hero '%s': x %.0f-%.0f %%, y %.0f-%.0f %%, %.0f %% inside the safe area "
            "(x %.0f-%.0f, y %.0f-%.0f)" % (label, box[0] * 100, box[2] * 100, box[1] * 100, box[3] * 100, frac * 100,
                                            x0 * 100, x1 * 100, y0 * 100, y1 * 100))
    return {"checks": checks, "failed": [c for c in checks if not c[1]], "colours": colours, "heroes": hero_out}


def print_report(name, report):
    """One line per check of a still; returns the number of failed checks."""
    for cname, ok, text in report["checks"]:
        print("[check] %-10s %-4s %-28s %s" % (name, "ok" if ok else "FAIL", cname, text), flush=True)
    return len(report["failed"])
