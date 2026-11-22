"""Voxel blocks: original 16x16 pixel-art textures, a shared texture atlas, a box-mesh builder and the World grid.

Everything here is generated in code (numpy). Nothing is downloaded or copied.

Conventions
- Block (x, y, z) occupies [x, x+1] x [y, y+1] x [z, z+1]; +Y is "north", +X is "east", Z is up.
- All textures live in one 512x512 atlas image (`ATLAS`). Faces pick their material from the *kind* of
  the tile they use: 'opaque', 'cutout' (alpha clip), 'blend' (glass), 'water', 'emit' (glowing pixels), 'metal', 'gem'.
- `MeshBuilder` emits axis-aligned boxes in pixel units (1/16 block) with automatic "UV-lock" mapping:
  a face shows the part of its 16x16 tile that it covers inside its block cell, upright and unmirrored.
- `World` is a sparse dict of named blocks. `World.build` culls hidden faces and returns one object per
  material kind.
"""
from dataclasses import dataclass

import bpy
import numpy as np

from . import pix

T = 16  # texture pixels per block

# --------------------------------------------------------------------------------------------------
# small pixel-art helpers
# --------------------------------------------------------------------------------------------------


def _c(h):
    """'#rrggbb' -> int16 RGB array."""
    return np.array(pix.rgba(h)[:3], dtype=np.int16)


def _noise(r, pal, w=None, shape=(T, T)):
    """Random picks from a small palette (list of hex strings), optionally weighted."""
    cols = np.array([_c(h) for h in pal])
    p = None if w is None else np.array(w, float) / float(np.sum(w))
    return cols[r.choice(len(cols), size=shape, p=p)]


def _jitter(r, rgb, amt=3):
    """Slight per-pixel value variation so flat areas stay alive."""
    return rgb + r.integers(-amt, amt + 1, rgb.shape[:2] + (1,))


def _out(rgb, alpha=None):
    """int RGB (+ optional alpha array/scalar) -> uint8 RGBA."""
    h, w = rgb.shape[:2]
    out = np.empty((h, w, 4), np.uint8)
    out[..., :3] = np.clip(rgb, 0, 255)
    out[..., 3] = 255 if alpha is None else alpha
    return out


def from_ascii(rows, palette):
    """Build an RGBA tile from rows of characters; palette maps char -> '#rrggbb' or (hex, alpha); '.' is transparent."""
    h, w = len(rows), len(rows[0])
    out = np.zeros((h, w, 4), np.uint8)
    for y, row in enumerate(rows):
        assert len(row) == w, "ragged ascii art row %d" % y
        for x, ch in enumerate(row):
            if ch == "." and "." not in palette:
                continue
            v = palette[ch]
            if isinstance(v, str):
                out[y, x] = pix.rgba(v)
            else:
                out[y, x] = pix.rgba(v[0], v[1])
    return out


# --------------------------------------------------------------------------------------------------
# texture generators (row 0 = top)
# --------------------------------------------------------------------------------------------------

DIRT = ["#8b6344", "#7d583b", "#99704e", "#6b4a31"]
GRASS = ["#6f9f3c", "#618f33", "#7dae47", "#52822d"]
PATH = ["#b59859", "#a68a4e", "#c3a86c", "#957944"]
STONE = ["#828282", "#787878", "#8e8e8e", "#6c6c6c"]
OAK = dict(base="#b9945b", light="#caa66d", dark="#a17e4b", seam="#70532e")
SPRUCE = dict(base="#7a5932", light="#8b693f", dark="#684a28", seam="#432f18")
DARKWOOD = dict(base="#5a4028", light="#6a4d31", dark="#4b3420", seam="#2e1f12")


def tex_dirt(seed=1, coarse=False):
    """Brown soil with clods and a few pale pebbles; coarse=True adds grey gravel bits."""
    r = pix.rng(seed)
    a = _noise(r, DIRT, [5, 4, 2, 2])
    for _ in range(6):
        x, y = r.integers(0, T, 2)
        a[y, x] = a[y, (x + 1) % T] = _c("#5a3d28")
    for _ in range(4):
        x, y = r.integers(0, T, 2)
        a[y, x] = _c("#b0906f")
        a[(y + 1) % T, x] = _c("#5a3d28")
    if coarse:
        for _ in range(11):
            x, y = r.integers(0, T, 2)
            col = _c(["#8f8a84", "#77726d", "#a39d96"][int(r.integers(0, 3))])
            for i in range(int(r.integers(1, 3))):
                a[y, (x + i) % T] = col
            a[(y + 1) % T, x] = _c("#4d3422")
    return _out(_jitter(r, a))


def tex_grass_top(seed=1):
    """Speckled green turf with light blade tips over dark roots."""
    r = pix.rng(seed)
    a = _noise(r, GRASS, [5, 4, 2, 2])
    for _ in range(8):
        x, y = r.integers(0, T, 2)
        a[y, x] = _c("#93c05a")
        a[(y + 1) % T, x] = _c("#47752a")
    return _out(_jitter(r, a))


def tex_grass_side(seed=1):
    """Dirt body with a ragged green fringe hanging from the top edge."""
    r = pix.rng(seed)
    a = tex_dirt(seed + 100)[..., :3].astype(np.int16)
    d = 3
    for x in range(T):
        d = int(np.clip(d + r.integers(-1, 2), 2, 5))
        a[:d, x] = _noise(r, GRASS, [5, 4, 2, 2], (d,))
        a[0, x] = _c("#7dae47") if r.random() < 0.6 else _c("#93c05a")
        a[d - 1, x] = _c("#47752a")
        a[d, x] = (a[d, x] * 0.8).astype(np.int16)
    return _out(_jitter(r, a, 2))


def tex_grass_bank(seed=1):
    """All-green turf side for meadow slopes: grass colours that darken toward the foot of the step."""
    r = pix.rng(seed)
    a = _noise(r, GRASS, [5, 4, 2, 2])
    shade = np.linspace(1.0, 0.74, T)[:, None, None]
    a = (a * shade).astype(np.int16)
    a[0] = _noise(r, ["#7dae47", "#93c05a"], None, (T,))
    for _ in range(7):
        x = int(r.integers(0, T))
        y = int(r.integers(3, T - 3))
        n = int(r.integers(2, 5))
        a[y : y + n, x] = (a[y : y + n, x] * 0.82).astype(np.int16)
        a[y - 1, x] = _c("#86b64e")
    return _out(_jitter(r, a, 2))


def tex_path_top(seed=1):
    """Worn, sandy-tan trodden earth with pale scuffs and small stones."""
    r = pix.rng(seed)
    a = _noise(r, PATH, [5, 4, 2, 2])
    for _ in range(5):
        x, y = r.integers(0, T, 2)
        n = int(r.integers(2, 5))
        a[y, (x + np.arange(n)) % T] = _c("#d0b77d")
    for _ in range(6):
        x, y = r.integers(0, T, 2)
        a[y, x] = _c("#7e6437")
    for _ in range(3):
        x, y = r.integers(0, T, 2)
        a[y, x] = _c("#9c968c")
        a[(y + 1) % T, x] = _c("#7e6437")
    return _out(_jitter(r, a))


def tex_path_side(seed=1):
    """Dirt with a thin tan crust on top."""
    r = pix.rng(seed)
    a = tex_dirt(seed + 200)[..., :3].astype(np.int16)
    a[0:2] = _noise(r, PATH, [5, 4, 2, 2], (2, T))
    a[2] = _noise(r, ["#7e6437", "#6b4a31"], None, (T,))
    return _out(a)


def tex_farmland(seed=1):
    """Dark tilled soil with furrows running along the texture rows."""
    r = pix.rng(seed)
    a = _noise(r, ["#5b3e27", "#4f3520", "#684830"], [4, 3, 2])
    for y in range(T):
        if y % 4 == 3:
            a[y] = _noise(r, ["#3a2616", "#43301c"], None, (T,))
        elif y % 4 == 0:
            a[y] = _noise(r, ["#76532f", "#684830"], None, (T,))
    return _out(_jitter(r, a, 2))


def tex_stone(seed=1):
    """Smooth grey stone with short horizontal strata."""
    r = pix.rng(seed)
    a = _noise(r, STONE, [5, 4, 2, 2])
    for _ in range(8):
        x, y = r.integers(0, T, 2)
        n = int(r.integers(3, 7))
        a[y, (x + np.arange(n)) % T] = _c("#929292") if r.random() < 0.5 else _c("#686868")
    return _out(_jitter(r, a, 2))


def _voronoi(r, n=11):
    """Tileable squarish Voronoi cells on a 16x16 torus -> (cell index, gap to second-nearest seed)."""
    pts = []
    tries = 0
    while len(pts) < n and tries < 4000:
        tries += 1
        p = r.random(2) * T
        ok = True
        for q in pts:
            dx = abs(p[0] - q[0])
            dy = abs(p[1] - q[1])
            dx, dy = min(dx, T - dx), min(dy, T - dy)
            if max(dx, dy) < 3.6:
                ok = False
                break
        if ok:
            pts.append(p)
    pts = np.array(pts)
    yy, xx = np.mgrid[0:T, 0:T]
    dx = np.abs(xx[None] + 0.5 - pts[:, 0, None, None])
    dy = np.abs(yy[None] + 0.5 - pts[:, 1, None, None])
    dx, dy = np.minimum(dx, T - dx), np.minimum(dy, T - dy)
    d = np.maximum(dx, dy) * 0.6 + (dx + dy) * 0.3
    order = np.argsort(d, axis=0)
    ds = np.sort(d, axis=0)
    return order[0], ds[1] - ds[0]


def _cobble_arrays(seed):
    """Shared cobble painter -> (rgb int16, mortar mask)."""
    r = pix.rng(seed)
    cell, gap = _voronoi(r)
    mortar = gap < 0.75
    tones = np.array([_c("#8d8d8d"), _c("#7c7c7c"), _c("#9b9b9b"), _c("#868079")])
    base = r.choice(len(tones), size=int(cell.max()) + 1, p=[0.35, 0.3, 0.2, 0.15])
    a = tones[base[cell]].copy()
    hi = (np.roll(mortar, 1, 0) | np.roll(mortar, 1, 1)) & ~mortar
    lo = (np.roll(mortar, -1, 0) | np.roll(mortar, -1, 1)) & ~mortar & ~hi
    a[hi] += 22
    a[lo] -= 26
    a[mortar] = _c("#474747")
    a[mortar & (r.random((T, T)) < 0.3)] = _c("#3b3b3b")
    return _jitter(r, a, 3), mortar


def tex_cobble(seed=1):
    """Irregular rounded stones, lit from the top-left, set in dark mortar."""
    return _out(_cobble_arrays(seed)[0])


def tex_mossy_cobble(seed=1):
    """Cobblestone with moss creeping out of the joints in soft patches."""
    a, mortar = _cobble_arrays(seed)
    r = pix.rng(seed + 500)
    yy, xx = np.mgrid[0:T, 0:T]
    f = np.zeros((T, T))
    for _ in range(5):
        cx, cy = r.random(2) * T
        s = r.uniform(1.7, 3.0)
        dx = np.abs(xx - cx)
        dy = np.abs(yy - cy)
        dx, dy = np.minimum(dx, T - dx), np.minimum(dy, T - dy)
        f += np.exp(-(dx * dx + dy * dy) / (2 * s * s))
    f += r.random((T, T)) * 0.4 + mortar * 0.3
    moss = f > 0.8
    greens = _noise(r, ["#5f9438", "#4c7d2d", "#76ab46"], [4, 3, 2])
    a[moss] = greens[moss]
    a[moss & mortar] = _c("#3b6824")
    edge = moss & ~np.roll(moss, -1, 0)
    a[edge] = _c("#4c7d2d")
    return _out(a)


def tex_stone_bricks(seed=1):
    """Two courses of large dressed bricks, half-offset, with dark joints and a light top edge."""
    r = pix.rng(seed)
    a = _noise(r, ["#848484", "#7b7b7b", "#8d8d8d"], [4, 3, 2])
    for row, off in ((0, 0), (8, 8)):
        a[row] += 18
        a[row + 6] -= 14
        a[row : row + 7, off % T] += 12
        a[row + 7] = _c("#4a4a4a")
        a[row : row + 7, (off + 15) % T] = _c("#4a4a4a")
    for _ in range(4):
        x, y = r.integers(0, T, 2)
        if (a[y, x] > 100).all():
            a[y, x] -= 20
    return _out(_jitter(r, a, 2))


def tex_planks(seed=1, pal=OAK):
    """Four long horizontal boards: soft seams, two butt joints, streaky grain and a couple of nail heads."""
    r = pix.rng(seed)
    a = np.empty((T, T, 3), np.int16)
    joints = {int(r.integers(0, 2)): int(r.integers(2, 7)), 2 + int(r.integers(0, 2)): int(r.integers(9, 14))}
    seam = _c(pal["seam"])
    for b in range(4):
        y0 = b * 4
        tone = int(r.integers(-6, 7))
        a[y0 : y0 + 4] = _c(pal["base"]) + tone
        a[y0] = _c(pal["light"]) + tone
        for _ in range(4):
            x = int(r.integers(0, T))
            n = int(r.integers(4, 10))
            yy = y0 + int(r.integers(1, 3))
            a[yy, (x + np.arange(n)) % T] = _c(pal["dark"]) + tone
        a[y0 + 3] = (seam + _c(pal["dark"])) // 2
        a[y0 + 3, r.random(T) < 0.35] = seam
        if b in joints:
            j = joints[b]
            a[y0 : y0 + 3, j] = seam
            a[y0 + 1, (j + 2) % T] = seam
            a[y0 + 1, (j - 2) % T] = seam
    return _out(_jitter(r, a, 2))


def tex_log_side(seed=1):
    """Bark: vertical ridges in four browns with deep dark cracks."""
    r = pix.rng(seed)
    pal = ["#6e5536", "#5e482c", "#7c6242", "#4b3820"]
    a = np.empty((T, T, 3), np.int16)
    for x in range(T):
        k = int(r.choice(4, p=[0.4, 0.3, 0.2, 0.1]))
        y = 0
        while y < T:
            n = int(r.integers(3, 9))
            a[y : y + n, x] = _c(pal[k])
            y += n
            k = (k + int(r.integers(1, 3))) % 4
    for _ in range(5):
        x, y = r.integers(0, T, 2)
        n = int(r.integers(4, 10))
        a[(y + np.arange(n)) % T, x] = _c("#3a2b18")
    return _out(_jitter(r, a, 2))


def tex_log_end(seed=1):
    """Cut log end: bark rim and concentric square growth rings."""
    r = pix.rng(seed)
    yy, xx = np.mgrid[0:T, 0:T]
    ring = np.minimum(np.minimum(xx, 15 - xx), np.minimum(yy, 15 - yy))
    cols = ["#5e482c", "#6e5536", "#c4a26a", "#a98652", "#c4a26a", "#b3905a", "#a98652", "#8f6c3d"]
    a = np.array([_c(h) for h in cols])[ring]
    return _out(_jitter(r, a, 3))


def tex_leaves(seed=1):
    """Leaf mass in four greens with see-through gaps, dark under each gap for depth."""
    r = pix.rng(seed)
    a = _noise(r, ["#3d7c2b", "#4b9034", "#5ca43e", "#2e6220"], [4, 4, 2, 2])
    hole = r.random((T, T)) < 0.055
    hole |= np.roll(hole, 1, 1) & (r.random((T, T)) < 0.4)
    below = np.roll(hole, 1, 0) & ~hole
    above = np.roll(hole, -1, 0) & ~hole
    a[below] = _c("#2e6220")
    a[above] = _c("#5ca43e")
    alpha = np.where(hole, 0, 255)
    return _out(_jitter(r, a, 3), alpha)


def tex_glass():
    """Clear pane: pale frame, faint tint, diagonal glints."""
    a = np.zeros((T, T, 4), np.uint8)
    a[..., :3] = _c("#d2ecf2")
    a[..., 3] = 16
    frame = np.zeros((T, T), bool)
    frame[0, :] = frame[-1, :] = frame[:, 0] = frame[:, -1] = True
    a[frame] = pix.rgba("#e6f4f7", 255)
    for x, y in ((0, 0), (15, 0), (0, 15), (15, 15), (15, 8), (15, 9), (7, 15), (8, 15)):
        a[y, x] = pix.rgba("#b4d3db", 255)
    for x, y in ((2, 4), (3, 3), (4, 2), (2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (7, 2)):
        a[y, x] = pix.rgba("#ffffff", 165)
    for x, y in ((11, 13), (12, 12), (13, 11), (12, 9), (13, 8)):
        a[y, x] = pix.rgba("#ffffff", 110)
    return a


def tex_glass_edge():
    """Solid pale strip used on the thin edges of glass panes."""
    r = pix.rng(77)
    return _out(_noise(r, ["#e6f4f7", "#cfe6ec", "#b4d3db"], [4, 3, 1]))


def tex_bookshelf(seed=1):
    """Two shelves of coloured book spines between oak boards."""
    r = pix.rng(seed)
    planks = tex_planks(seed + 3)[..., :3].astype(np.int16)
    a = np.empty((T, T, 3), np.int16)
    a[:] = _c("#2f2114")
    for rows in ((0, 1), (7, 8), (14, 15)):
        a[rows[0]] = planks[0]
        a[rows[1]] = planks[3]
    spines = ["#a5322c", "#3e7c3b", "#34548f", "#c8a454", "#6c3f86", "#d8d2c0", "#b5622a", "#2f7f85"]
    for shelf in (2, 9):
        x = 0
        last = -1
        while x < T:
            w = min(int(r.integers(1, 4)), T - x)
            k = int(r.integers(0, len(spines)))
            if k == last:
                k = (k + 1) % len(spines)
            last = k
            col = _c(spines[k])
            h = int(r.integers(3, 6))
            top = shelf + 5 - h
            a[top : shelf + 5, x : x + w] = col
            a[top, x : x + w] = col + 30
            if w >= 2:
                a[top : shelf + 5, x + w - 1] = (col * 0.72).astype(np.int16)
            if h >= 4:
                a[top + 2, x : x + max(1, w - 1)] = _c("#e7d9a0") if k not in (3, 5) else _c("#6a4a2a")
            x += w
    return _out(a)


def tex_hay_side(seed=1):
    """Straw bale side: vertical yellow stalks bound by two red-brown cords."""
    r = pix.rng(seed)
    pal = ["#c9a42b", "#b58e20", "#dbbb41", "#9a771b"]
    a = np.empty((T, T, 3), np.int16)
    for x in range(T):
        y = 0
        while y < T:
            n = int(r.integers(2, 7))
            a[y : y + n, x] = _c(pal[int(r.choice(4, p=[0.4, 0.3, 0.2, 0.1]))])
            y += n
    for y in (3, 11):
        a[y] = _c("#a04f2c")
        a[y + 1] = _c("#7a381f")
    return _out(_jitter(r, a, 2))


def tex_hay_top(seed=1):
    """Straw bale end: speckled stalk tips with a darker rim and a crossed cord."""
    r = pix.rng(seed)
    a = _noise(r, ["#c9a42b", "#b58e20", "#dbbb41", "#9a771b"], [4, 3, 2, 2])
    a[0, :] = a[-1, :] = a[:, 0] = a[:, -1] = _c("#9a771b")
    for x in (3, 11):
        a[:, x] = _c("#a04f2c")
        a[:, x + 1] = _c("#7a381f")
    return _out(_jitter(r, a, 2))


def tex_water(seed=1):
    """Translucent blue with pale ripple dashes."""
    r = pix.rng(seed)
    a = _noise(r, ["#3d74d9", "#4682e2", "#3468cb"], [4, 3, 3])
    for _ in range(7):
        x, y = r.integers(0, T, 2)
        n = int(r.integers(2, 6))
        a[y, (x + np.arange(n)) % T] = _c("#86b6f5")
    return _out(a, 180)


def tex_wool(seed=1, tint="#ffffff"):
    """Soft knitted cloth; tint multiplies the off-white base."""
    r = pix.rng(seed)
    g = r.choice([236, 226, 244, 214], size=(T, T), p=[0.4, 0.3, 0.2, 0.1]).astype(np.int16)
    yy, xx = np.mgrid[0:T, 0:T]
    g -= ((xx + yy) % 4 == 0) * 12
    g -= ((xx - yy) % 8 == 0) * 6
    a = (g[..., None] * (_c(tint) / 255.0)).astype(np.int16)
    return _out(a)


def tex_terracotta(seed=1):
    """Pale pinkish-beige fired clay with soft blotches (used as plaster)."""
    r = pix.rng(seed)
    a = _noise(r, ["#d6b8a7", "#cdad9c", "#ddc0b0"], [5, 3, 2])
    for _ in range(4):
        x, y = r.integers(0, T, 2)
        w, h = r.integers(2, 5, 2)
        ys = (y + np.arange(h)) % T
        xs = (x + np.arange(w)) % T
        a[np.ix_(ys, xs)] -= 9
    return _out(_jitter(r, a, 2))


def tex_gravel(seed=1):
    """Loose grey-brown pebbles with tiny highlights and shadows."""
    r = pix.rng(seed)
    a = _noise(r, ["#878280", "#736e6b", "#9c9692", "#5d5855", "#857667"], [4, 4, 2, 2, 1.5])
    for _ in range(9):
        x, y = r.integers(0, T, 2)
        a[y, x] = a[y, (x + 1) % T] = _c("#aaa49f")
        a[(y + 1) % T, x] = a[(y + 1) % T, (x + 1) % T] = _c("#514c49")
    return _out(_jitter(r, a, 3))


def tex_tall_grass(seed=1, short=False):
    """Tuft of blades growing from the bottom edge (cut-out)."""
    r = pix.rng(seed)
    a = np.zeros((T, T, 4), np.uint8)
    cols = ["#4f8a2c", "#5f9832", "#6ea63a", "#86bb4c"]
    xs = r.permutation(np.arange(1, 15))[: (7 if short else 10)]
    for x0 in xs:
        h = int(r.integers(4, 9)) if short else int(r.integers(7, 16))
        x = float(x0)
        lean = r.choice([-1, 0, 0, 1]) * r.uniform(0.1, 0.35)
        for i in range(h):
            xi = int(np.clip(round(x), 0, T - 1))
            y = T - 1 - i
            t = i / max(1, h - 1)
            col = cols[min(3, int(t * 3.2))]
            a[y, xi] = pix.rgba(col)
            if i < 3 and xi + 1 < T and r.random() < 0.5:
                a[y, xi + 1] = pix.rgba(cols[0])
            x += lean * (0.4 + t)
    return a


def tex_flower(kind="poppy"):
    """Small flower on a stem (cut-out). kinds: poppy, dandelion, cornflower, daisy."""
    stem = {"s": "#3f7a2a", "l": "#5c9a36", "d": "#2f5f20"}
    arts = {
        "poppy": (
            [
                "................",
                "................",
                "................",
                "................",
                "................",
                "......rRr.......",
                ".....rRRRr......",
                ".....RRkRRd.....",
                ".....dRRRd......",
                "......ddd.......",
                ".......s........",
                ".......s.l......",
                "......ls.l......",
                "......lss.......",
                ".......s........",
                ".......s........",
            ],
            {"r": "#e2483a", "R": "#c8281f", "d": "#8e1712", "k": "#2a1512"},
        ),
        "dandelion": (
            [
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "................",
                "......yYy.......",
                ".....yYYYo......",
                "......oYo.......",
                ".......s........",
                ".......s........",
                ".....l.s........",
                ".....lss.l......",
                "......lsl.......",
                ".......s........",
            ],
            {"y": "#ffe55a", "Y": "#f4c62a", "o": "#d49a1a"},
        ),
        "cornflower": (
            [
                "................",
                "................",
                "................",
                "................",
                "................",
                ".....b.b.b......",
                "......bBb.......",
                ".....bBnBb......",
                "......bBb.......",
                ".....b.s.b......",
                ".......s........",
                ".......s.l......",
                ".......sl.......",
                "......ls........",
                "......ls........",
                ".......s........",
            ],
            {"b": "#5a7df0", "B": "#3f5fd6", "n": "#27348f"},
        ),
        "daisy": (
            [
                "................",
                "................",
                "................",
                "................",
                "................",
                "......www.......",
                ".....wwywg......",
                ".....wyYyw......",
                ".....gwywg......",
                "......ggg.......",
                ".......s........",
                ".......s........",
                "......ls.l......",
                "......lsl.......",
                ".......s........",
                ".......s........",
            ],
            {"w": "#f6f6f0", "g": "#cfd3cc", "y": "#f4c62a", "Y": "#d49a1a"},
        ),
    }
    rows, pal = arts[kind]
    pal = dict(pal)
    pal.update(stem)
    return from_ascii(rows, pal)


def tex_wheat(stage=7, seed=1):
    """Wheat crop sprite for growth stage 0..7: short green shoots up to tall golden ears (cut-out)."""
    r = pix.rng(seed * 31 + stage)
    a = np.zeros((T, T, 4), np.uint8)
    t = stage / 7.0
    h_max = int(round(4 + 11 * t))
    green = np.array([_c("#4f8f2e"), _c("#6aa63a"), _c("#3f7526")])
    gold = np.array([_c("#d2ad3c"), _c("#e6c85a"), _c("#a8842a")])
    mix = np.clip((t - 0.45) / 0.45, 0, 1)
    cols = (green * (1 - mix) + gold * mix).astype(np.int16)
    for x0 in range(1, 16, 2):
        h = max(2, h_max - int(r.integers(0, 3)))
        x = min(T - 1, x0 + int(r.integers(0, 2)))
        for i in range(h):
            y = T - 1 - i
            xi = min(T - 1, x + (1 if (i > h * 0.6 and r.random() < 0.25) else 0))
            a[y, xi, :3] = np.clip(cols[0 if i % 3 else 2], 0, 255)
            a[y, xi, 3] = 255
        if stage >= 5:
            top = T - h
            for i in range(4):
                y = top + i
                if 0 <= y < T:
                    a[y, x, :3] = np.clip(cols[1], 0, 255)
                    a[y, x, 3] = 255
                    xn = x + (1 if i % 2 else -1)
                    if 0 <= xn < T:
                        a[y, xn, :3] = np.clip(cols[2] if i % 2 else cols[0], 0, 255)
                        a[y, xn, 3] = 255
    return a


# --------------------------------------------------------------------------------------------------
# atlas + materials
# --------------------------------------------------------------------------------------------------


class Atlas:
    """Shelf-packed texture atlas. Tiles are registered by name with a material kind."""

    SIZE = 512
    KINDS = ("opaque", "cutout", "blend", "water", "emit", "metal", "gem")
    IMAGE = "vox_atlas"

    def __init__(self):
        self.arr = np.zeros((self.SIZE, self.SIZE, 4), np.uint8)
        self.tiles = {}
        self._x = self._y = self._row_h = 0
        self._uploaded = -1

    def add(self, name, arr, kind="opaque"):
        """Register an HxWx4 uint8 tile under `name` (re-adding a name replaces its pixels)."""
        arr = np.asarray(arr, np.uint8)
        h, w = arr.shape[:2]
        assert kind in self.KINDS
        if name in self.tiles:
            x, y, ow, oh, _ = self.tiles[name]
            assert (ow, oh) == (w, h), "tile size changed: " + name
        else:
            if self._x + w > self.SIZE:
                self._x = 0
                self._y += self._row_h
                self._row_h = 0
            assert self._y + h <= self.SIZE, "atlas full"
            x, y = self._x, self._y
            self._x += w
            self._row_h = max(self._row_h, h)
        self.tiles[name] = (x, y, w, h, kind)
        self.arr[y : y + h, x : x + w] = arr
        self._uploaded = -1
        return name

    def has(self, name):
        """True if a tile of that name exists."""
        return name in self.tiles

    def get(self, name):
        """Return a copy of a tile's RGBA pixels."""
        x, y, w, h, _ = self.tiles[name]
        return self.arr[y : y + h, x : x + w].copy()

    def kind(self, name):
        """Material kind of a tile."""
        return self.tiles[name][4]

    def size(self, name):
        """(w, h) of a tile in pixels."""
        return self.tiles[name][2:4]

    def uv(self, name, px, py):
        """Atlas UV of the point px pixels right / py pixels down from the tile's top-left corner."""
        x, y = self.tiles[name][:2]
        return ((x + px) / self.SIZE, 1.0 - (y + py) / self.SIZE)

    def image(self):
        """The packed bpy Image of the atlas (created or refreshed on demand)."""
        img = bpy.data.images.get(self.IMAGE)
        if img is None:
            img = pix.image_from_array(self.IMAGE, self.arr)
            self._uploaded = len(self.tiles)
        elif self._uploaded != len(self.tiles):
            img.pixels.foreach_set((np.flipud(self.arr).astype(np.float32) / 255.0).ravel())
            img.update()
            img.save()
            img.pack()
            self._uploaded = len(self.tiles)
        return img

    def material(self, kind):
        """The shared material for a tile kind (created on demand, safe across scene resets)."""
        name = "vox_" + kind
        img = self.image()
        mat = bpy.data.materials.get(name)
        if mat is not None:
            return mat
        if kind == "opaque":
            mat = pix.pixel_material(name, img)
        elif kind == "cutout":
            mat = pix.pixel_material(name, img, alpha="CLIP")
        elif kind == "blend":
            mat = pix.pixel_material(name, img, alpha="BLEND", roughness=0.2)
        elif kind == "water":
            mat = pix.pixel_material(name, img, alpha="BLEND", roughness=0.12)
            mat.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.5
        elif kind == "emit":
            mat = pix.pixel_material(name, img, emission=1.0)
            _mask_emission(mat, EMIT_STRENGTH)
        elif kind == "metal":
            mat = pix.pixel_material(name, img, roughness=0.42)
            b = mat.node_tree.nodes["Principled BSDF"]
            b.inputs["Metallic"].default_value = 0.45
            b.inputs["Specular IOR Level"].default_value = 0.6
        elif kind == "gem":
            mat = pix.pixel_material(name, img, emission=0.35, roughness=0.18)
            mat.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.9
        return mat


EMIT_STRENGTH = 14.0


def _mask_emission(mat, strength):
    """Make only the bright pixels of an emissive pixel material glow (dark frame pixels stay unlit)."""
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(tex.outputs["Color"], sep.inputs[0])
    mx = nt.nodes.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    nt.links.new(sep.outputs[0], mx.inputs[0])
    nt.links.new(sep.outputs[1], mx.inputs[1])
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.25
    ramp.inputs["From Max"].default_value = 0.9
    ramp.inputs["To Min"].default_value = 0.0
    ramp.inputs["To Max"].default_value = strength
    nt.links.new(mx.outputs[0], ramp.inputs["Value"])
    nt.links.new(ramp.outputs[0], bsdf.inputs["Emission Strength"])


ATLAS = Atlas()

# --------------------------------------------------------------------------------------------------
# mesh builder
# --------------------------------------------------------------------------------------------------

# face key -> (normal axis, sign, right vector, up vector)
_FACES = {
    "s": (1, -1, (1, 0, 0), (0, 0, 1)),
    "n": (1, 1, (-1, 0, 0), (0, 0, 1)),
    "e": (0, 1, (0, 1, 0), (0, 0, 1)),
    "w": (0, -1, (0, -1, 0), (0, 0, 1)),
    "t": (2, 1, (1, 0, 0), (0, 1, 0)),
    "b": (2, -1, (1, 0, 0), (0, -1, 0)),
}
ALL_FACES = "nsewtb"
_UV_EPS = 0.02  # inset in pixels so Closest sampling never bleeds into the neighbouring atlas tile


def _tex_for(tex, f):
    """Resolve a texture spec for face key f. tex: name | dict with keys among n,s,e,w,t,b,side,top,bottom,all."""
    if isinstance(tex, (str, tuple)):
        return tex
    if f in tex:
        return tex[f]
    if f in "nsew" and "side" in tex:
        return tex["side"]
    if f == "t" and "top" in tex:
        return tex["top"]
    if f == "b":
        if "bottom" in tex:
            return tex["bottom"]
        if "top" in tex:
            return tex["top"]
    return tex.get("all") or tex.get("side") or tex.get("top")


class MeshBuilder:
    """Accumulates textured quads (pixel units, 16 px = 1 block) and turns them into a Blender mesh object."""

    def __init__(self, scale=1.0 / T):
        self.scale = scale
        self.verts = []
        self.uvs = []
        self.kinds = []

    def __len__(self):
        return len(self.kinds)

    def quad_uv(self, pts, tile, corners):
        """Add a quad. pts: 4 points CCW (pixel units). corners: 4 (px, py) texel positions inside the tile,
        measured from its top-left corner, one per point."""
        cx = sum(c[0] for c in corners) * 0.25
        cy = sum(c[1] for c in corners) * 0.25
        e = _UV_EPS
        for px, py in corners:
            px += e if cx > px else -e
            py += e if cy > py else -e
            self.uvs.append(ATLAS.uv(tile, px, py))
        s = self.scale
        for p in pts:
            self.verts.append((p[0] * s, p[1] * s, p[2] * s))
        self.kinds.append(ATLAS.kind(tile))

    def quad(self, pts, tile, uv_px=None, rot=0):
        """Add a quad showing the tile rectangle uv_px = (px0, py0, px1, py1) (default: whole tile); the
        rectangle's bottom-left lands on pts[0]. rot = quarter turns of the texture."""
        if uv_px is None:
            tw, th = ATLAS.size(tile)
            uv_px = (0, 0, tw, th)
        px0, py0, px1, py1 = uv_px
        c = [(px0, py1), (px1, py1), (px1, py0), (px0, py0)]
        if rot:
            c = [c[(i + rot) % 4] for i in range(4)]
        self.quad_uv(pts, tile, c)

    def face(self, f, lo, hi, tex, uv_origin=(0, 0, 0), rot=0, xf=None, off=(0, 0, 0)):
        """Add one face (f in 'nsewtb') of the box lo..hi (pixels). The texture is mapped "UV-locked" relative
        to uv_origin (the min corner of the block cell) unless the spec is an explicit tuple
        (tile, px0, py0, px1, py1[, rot]) which is stretched over the face. rot = quarter turns.
        xf: optional point transform; off: translation in pixels; both applied after UV mapping."""
        axis, sign, rv, uv = _FACES[f]
        spec = _tex_for(tex, f)
        if spec is None:
            return
        base = [lo[0], lo[1], lo[2]]
        base[axis] = hi[axis] if sign > 0 else lo[axis]
        ra = 0 if rv[0] else 1
        ua = 2 if uv[2] else 1
        rneg = rv[ra] < 0
        uneg = uv[ua] < 0
        r0, r1 = (hi[ra], lo[ra]) if rneg else (lo[ra], hi[ra])
        u0, u1 = (hi[ua], lo[ua]) if uneg else (lo[ua], hi[ua])
        pts = []
        for rr, uu in ((r0, u0), (r1, u0), (r1, u1), (r0, u1)):
            p = list(base)
            p[ra] = rr
            p[ua] = uu
            pts.append(p)
        if xf is not None:
            pts = [xf(p) for p in pts]
        if off != (0, 0, 0):
            pts = [(p[0] + off[0], p[1] + off[1], p[2] + off[2]) for p in pts]
        if isinstance(spec, tuple):
            self.quad(pts, spec[0], spec[1:5], (rot + (spec[5] if len(spec) > 5 else 0)) % 4)
            return
        tile = spec
        tw, th = ATLAS.size(tile)
        rot %= 4
        sw, sh = (th, tw) if rot % 2 else (tw, th)  # tile extent along the face's right / up axes
        s0 = (uv_origin[ra] + sw - r0) if rneg else (r0 - uv_origin[ra])
        s1 = (uv_origin[ra] + sw - r1) if rneg else (r1 - uv_origin[ra])
        t0 = (uv_origin[ua] + sh - u0) if uneg else (u0 - uv_origin[ua])
        t1 = (uv_origin[ua] + sh - u1) if uneg else (u1 - uv_origin[ua])
        ks = np.floor(s0 / sw + 1e-6) * sw
        kt = np.floor(t0 / sh + 1e-6) * sh
        s0, s1 = min(max(s0 - ks, 0), sw), min(max(s1 - ks, 0), sw)
        t0, t1 = min(max(t0 - kt, 0), sh), min(max(t1 - kt, 0), sh)
        st = ((s0, t0), (s1, t0), (s1, t1), (s0, t1))
        if rot == 0:
            c = [(s, th - t) for s, t in st]
        elif rot == 2:
            c = [(tw - s, t) for s, t in st]
        elif rot == 1:
            c = [(t, s) for s, t in st]
        else:
            c = [(tw - t, th - s) for s, t in st]
        self.quad_uv(pts, tile, c)

    def box(self, lo, hi, tex, faces=ALL_FACES, uv_origin=(0, 0, 0), rot=None, xf=None, off=(0, 0, 0), split=True):
        """Add a box lo..hi in pixel units. tex: tile name, explicit tuple, or dict per face (keys n,s,e,w,t,b,
        side,top,bottom,all). faces: which of 'nsewtb' to emit. Boxes that cross a 16-pixel boundary (relative to
        uv_origin) are split so auto-mapped tiles repeat cleanly. rot: dict face -> quarter turns.
        xf / off: point transform and pixel offset applied after UV mapping."""
        rot = rot or {}
        auto = []
        for f in faces:
            spec = _tex_for(tex, f)
            if spec is None:
                continue
            if isinstance(spec, tuple):
                self.face(f, lo, hi, tex, uv_origin, rot.get(f, 0), xf, off)
            else:
                auto.append(f)
        if not auto:
            return
        cuts = []
        for a in range(3):
            c = [lo[a]]
            if split:
                k = np.floor((lo[a] - uv_origin[a]) / T + 1e-6) + 1
                while uv_origin[a] + k * T < hi[a] - 1e-6:
                    c.append(uv_origin[a] + k * T)
                    k += 1
            c.append(hi[a])
            cuts.append(c)
        for ix in range(len(cuts[0]) - 1):
            for iy in range(len(cuts[1]) - 1):
                for iz in range(len(cuts[2]) - 1):
                    l = (cuts[0][ix], cuts[1][iy], cuts[2][iz])
                    h = (cuts[0][ix + 1], cuts[1][iy + 1], cuts[2][iz + 1])
                    for f in auto:
                        axis, sign = _FACES[f][0], _FACES[f][1]
                        idx = (ix, iy, iz)[axis]
                        if (sign > 0 and idx != len(cuts[axis]) - 2) or (sign < 0 and idx != 0):
                            continue  # internal face of a split box
                        self.face(f, l, h, tex, uv_origin, rot.get(f, 0), xf, off)

    def plane(self, p0, p1, z0, z1, tile, uv_px=None):
        """Vertical two-sided card from (x, y) p0 to p1 between heights z0..z1 (pixels), tile stretched over it."""
        pts = [(p0[0], p0[1], z0), (p1[0], p1[1], z0), (p1[0], p1[1], z1), (p0[0], p0[1], z1)]
        self.quad(pts, tile, uv_px)

    def kinds_used(self):
        """Material kinds present, in canonical order."""
        present = set(self.kinds)
        return [k for k in Atlas.KINDS if k in present]

    def to_mesh(self, name):
        """Create the bpy Mesh (flat shaded quads, one UV map, material slots per kind used)."""
        n = len(self.kinds)
        mesh = bpy.data.meshes.new(name)
        if n == 0:
            return mesh
        mesh.vertices.add(n * 4)
        mesh.vertices.foreach_set("co", np.asarray(self.verts, np.float32).reshape(-1))
        mesh.loops.add(n * 4)
        mesh.loops.foreach_set("vertex_index", np.arange(n * 4, dtype=np.int32))
        mesh.polygons.add(n)
        mesh.polygons.foreach_set("loop_start", np.arange(0, n * 4, 4, dtype=np.int32))
        used = self.kinds_used()
        slot = {k: i for i, k in enumerate(used)}
        mesh.polygons.foreach_set("material_index", np.array([slot[k] for k in self.kinds], np.int32))
        uv = mesh.uv_layers.new(name="UVMap")
        uv.data.foreach_set("uv", np.asarray(self.uvs, np.float32).reshape(-1))
        for k in used:
            mesh.materials.append(ATLAS.material(k))
        mesh.update(calc_edges=True)
        mesh.validate()
        return mesh

    def to_object(self, name, collection=None):
        """Create an Object from the accumulated quads and link it to `collection` if given."""
        obj = bpy.data.objects.new(name, self.to_mesh(name))
        if collection is not None:
            collection.objects.link(obj)
        return obj


def rot_xf(axis, degrees, pivot):
    """Point transform rotating about a pivot around 'x', 'y' or 'z' (for MeshBuilder xf=)."""
    a = np.radians(degrees)
    c, s = float(np.cos(a)), float(np.sin(a))
    px, py, pz = pivot

    def f(p):
        x, y, z = p[0] - px, p[1] - py, p[2] - pz
        if axis == "x":
            y, z = y * c - z * s, y * s + z * c
        elif axis == "y":
            x, z = x * c + z * s, -x * s + z * c
        else:
            x, y = x * c - y * s, x * s + y * c
        return (x + px, y + py, z + pz)

    return f


# --------------------------------------------------------------------------------------------------
# block definitions
# --------------------------------------------------------------------------------------------------


@dataclass
class BlockDef:
    """One block type. top/side/bottom are tuples of atlas tile names (several = random variants)."""

    name: str
    top: tuple
    side: tuple
    bottom: tuple
    kind: str = "opaque"
    shape: str = "cube"  # cube | slab | slab_top | stairs_n/e/s/w | fence | pane | cross | crop | plate
    height: int = 16  # top surface height in pixels (cube shape only)
    axis: str = "z"  # grain axis for logs
    rot_top: bool = False  # random quarter-turn of the top texture per block
    cull_same: bool = False  # hide faces between two blocks of this same type (glass, water, leaves)

    @property
    def full(self):
        """True for an opaque full cube (hides every neighbour face it touches)."""
        return self.kind == "opaque" and self.shape == "cube" and self.height == 16


BLOCKS = {}


def _t(x):
    return x if isinstance(x, tuple) else (x,)


def define(name, top, side=None, bottom=None, **kw):
    """Register a BlockDef (side/bottom default to top)."""
    side = top if side is None else side
    bottom = top if bottom is None else bottom
    BLOCKS[name] = BlockDef(name, _t(top), _t(side), _t(bottom), **kw)
    return BLOCKS[name]


def _register():
    A = ATLAS.add
    for i in range(3):
        A("grass_top_%d" % i, tex_grass_top(11 + i))
        A("dirt_%d" % i, tex_dirt(21 + i))
        A("grass_side_%d" % i, tex_grass_side(31 + i))
        A("leaves_%d" % i, tex_leaves(41 + i), "cutout")
        A("grass_bank_%d" % i, tex_grass_bank(45 + i))
    for i in range(2):
        A("path_top_%d" % i, tex_path_top(51 + i))
        A("path_side_%d" % i, tex_path_side(55 + i))
        A("coarse_dirt_%d" % i, tex_dirt(61 + i, coarse=True))
        A("stone_%d" % i, tex_stone(71 + i))
        A("cobble_%d" % i, tex_cobble(81 + i))
        A("mossy_cobble_%d" % i, tex_mossy_cobble(81 + i))
        A("gravel_%d" % i, tex_gravel(91 + i))
        A("oak_planks_%d" % i, tex_planks(101 + i, OAK))
        A("spruce_planks_%d" % i, tex_planks(111 + i, SPRUCE))
        A("log_side_%d" % i, tex_log_side(121 + i))
        A("bookshelf_%d" % i, tex_bookshelf(131 + i))
    A("dark_planks_0", tex_planks(141, DARKWOOD))
    A("farmland", tex_farmland(151))
    A("stone_bricks", tex_stone_bricks(161))
    A("log_end", tex_log_end(171))
    A("hay_side", tex_hay_side(181))
    A("hay_top", tex_hay_top(182))
    A("water", tex_water(191), "water")
    A("glass", tex_glass(), "blend")
    A("glass_edge", tex_glass_edge())
    A("terracotta_white", tex_terracotta(201))
    for nm, tint in (("white", "#ffffff"), ("red", "#c2392f"), ("yellow", "#f0c33c"), ("blue", "#4a66c9"),
                     ("green", "#5c9a3a")):
        A("wool_" + nm, tex_wool(211, tint))
    for i in range(4):
        A("tall_grass_%d" % i, tex_tall_grass(221 + i), "cutout")
    for i in range(2):
        A("short_grass_%d" % i, tex_tall_grass(231 + i, short=True), "cutout")
    for k in ("poppy", "dandelion", "cornflower", "daisy"):
        A(k, tex_flower(k), "cutout")
    for s in range(8):
        A("wheat_%d" % s, tex_wheat(s), "cutout")

    v3 = lambda n: tuple("%s_%d" % (n, i) for i in range(3))
    v2 = lambda n: tuple("%s_%d" % (n, i) for i in range(2))
    define("grass", v3("grass_top"), v3("grass_side"), v3("dirt"), rot_top=True)
    define("meadow", v3("grass_top"), v3("grass_bank"), v3("dirt"), rot_top=True)
    define("dirt", v3("dirt"), rot_top=True)
    define("path", v2("path_top"), v2("path_side"), v3("dirt"), rot_top=True)
    define("coarse_dirt", v2("coarse_dirt"), rot_top=True)
    define("farmland", "farmland", v3("dirt"), v3("dirt"), height=15)
    define("stone", v2("stone"))
    define("cobble", v2("cobble"), rot_top=True)
    define("mossy_cobble", v2("mossy_cobble"), rot_top=True)
    define("stone_bricks", "stone_bricks")
    define("oak_planks", v2("oak_planks"))
    define("spruce_planks", v2("spruce_planks"))
    define("dark_planks", "dark_planks_0")
    define("oak_log", "log_end", v2("log_side"))
    define("oak_log_x", "log_end", v2("log_side"), axis="x")
    define("oak_log_y", "log_end", v2("log_side"), axis="y")
    define("oak_leaves", v3("leaves"), kind="cutout", cull_same=True, rot_top=True)
    define("glass", "glass", kind="blend", cull_same=True)
    define("bookshelf", v2("oak_planks"), v2("bookshelf"))
    define("hay", "hay_top", "hay_side")
    define("water", "water", kind="water", cull_same=True, height=14)
    define("terracotta_white", "terracotta_white")
    define("gravel", v2("gravel"), rot_top=True)
    for nm in ("white", "red", "yellow", "blue", "green"):
        define("wool_" + nm, "wool_" + nm)
        define("carpet_" + nm, "wool_" + nm, shape="plate")
    # shaped variants of the building materials
    for base in ("oak_planks", "spruce_planks", "dark_planks", "cobble", "mossy_cobble", "stone_bricks", "stone"):
        b = BLOCKS[base]
        short = base.replace("_planks", "")
        for d in "nesw":
            BLOCKS["%s_stairs_%s" % (short, d)] = BlockDef("%s_stairs_%s" % (short, d), b.top, b.side, b.bottom,
                                                          shape="stairs_" + d)
        BLOCKS[short + "_slab"] = BlockDef(short + "_slab", b.top, b.side, b.bottom, shape="slab")
        BLOCKS[short + "_slab_top"] = BlockDef(short + "_slab_top", b.top, b.side, b.bottom, shape="slab_top")
    define("oak_fence", v2("oak_planks"), shape="fence")
    define("spruce_fence", v2("spruce_planks"), shape="fence")
    define("dark_fence", "dark_planks_0", shape="fence")
    define("cobble_wall", v2("cobble"), shape="wall")
    define("glass_pane", "glass_edge", "glass", kind="blend", shape="pane")
    define("oak_plate", v2("oak_planks"), shape="plate")
    define("tall_grass", tuple("tall_grass_%d" % i for i in range(4)), kind="cutout", shape="cross")
    define("short_grass", v2("short_grass"), kind="cutout", shape="cross")
    for k in ("poppy", "dandelion", "cornflower", "daisy"):
        define(k, k, kind="cutout", shape="cross")
    for s in range(8):
        define("wheat_%d" % s, "wheat_%d" % s, kind="cutout", shape="crop")


_register()

# --------------------------------------------------------------------------------------------------
# World
# --------------------------------------------------------------------------------------------------

_DIRS = {"e": (1, 0, 0), "w": (-1, 0, 0), "n": (0, 1, 0), "s": (0, -1, 0), "t": (0, 0, 1), "b": (0, 0, -1)}
_STAIR_UP = {
    "n": ((0, 8, 8), (16, 16, 16), (0, 0, 8), (16, 8, 8)),
    "s": ((0, 0, 8), (16, 8, 16), (0, 8, 8), (16, 16, 8)),
    "e": ((8, 0, 8), (16, 16, 16), (0, 0, 8), (8, 16, 8)),
    "w": ((0, 0, 8), (8, 16, 16), (8, 0, 8), (16, 16, 8)),
}


def pos_hash(x, y, z, salt=0):
    """Deterministic 32-bit hash of a block position (for texture variants and jitter)."""
    h = (int(x) * 73856093) ^ (int(y) * 19349663) ^ (int(z) * 83492791) ^ (salt * 2654435761)
    h &= 0xFFFFFFFF
    h ^= h >> 15
    h = (h * 0x2C1B3C6D) & 0xFFFFFFFF
    h ^= h >> 12
    h = (h * 0x297A2D39) & 0xFFFFFFFF
    h ^= h >> 15
    return h


def shape_parts(shape):
    """Geometry of a non-cube shape as a list of (lo, hi, faces) in cell pixels (connections not included)."""
    if shape == "slab":
        return [((0, 0, 0), (16, 16, 8), ALL_FACES)]
    if shape == "slab_top":
        return [((0, 0, 8), (16, 16, 16), ALL_FACES)]
    if shape == "plate":
        return [((1, 1, 0), (15, 15, 1), ALL_FACES)]
    if shape.startswith("stairs_"):
        ulo, uhi, tlo, thi = _STAIR_UP[shape[-1]]
        return [((0, 0, 0), (16, 16, 8), "nsewb"), (tlo, thi, "t"), (ulo, uhi, "nsewt")]
    raise KeyError(shape)


def fence_parts(conn, wall=False):
    """Fence (or thick stone wall) boxes for a set of connected directions, e.g. conn='ns'."""
    if wall:
        parts = [((4, 4, 0), (12, 12, 16), ALL_FACES)]
        arms = {"n": ((5, 12, 0), (11, 16, 13), "ewt"), "s": ((5, 0, 0), (11, 4, 13), "ewt"),
                "e": ((12, 5, 0), (16, 11, 13), "nst"), "w": ((0, 5, 0), (4, 11, 13), "nst")}
        for d in conn:
            parts.append(arms[d])
        return parts
    parts = [((6, 6, 0), (10, 10, 16), ALL_FACES)]
    for z0 in (6, 12):
        z1 = z0 + 3
        arms = {"n": ((7, 10, z0), (9, 16, z1), "ewtb"), "s": ((7, 0, z0), (9, 6, z1), "ewtb"),
                "e": ((10, 7, z0), (16, 9, z1), "nstb"), "w": ((0, 7, z0), (6, 9, z1), "nstb")}
        for d in conn:
            parts.append(arms[d])
    return parts


def pane_parts(conn):
    """Thin glass-pane boxes for a set of connected directions (no connection = a short cross). Only one skin
    per pane is emitted (south / east side) so the glints of the two sides never double up."""
    conn = "".join(sorted(conn))
    if conn == "ew":
        return [((0, 7, 0), (16, 9, 16), "sewtb")]
    if conn == "ns":
        return [((7, 0, 0), (9, 16, 16), "nsetb")]
    if not conn:
        return [((4, 7, 0), (12, 9, 16), "sewtb"), ((7, 4, 0), (9, 12, 16), "nsetb")]
    parts = [((7, 7, 0), (9, 9, 16), "tb")]
    arms = {"n": ((7, 9, 0), (9, 16, 16), "netb"), "s": ((7, 0, 0), (9, 7, 16), "setb"),
            "e": ((9, 7, 0), (16, 9, 16), "setb"), "w": ((0, 7, 0), (7, 9, 16), "swtb")}
    for d in "nsew":
        if d in conn:
            parts.append(arms[d])
    return parts


class World:
    """Sparse voxel grid of named blocks that can be meshed into a few culled, UV-mapped objects."""

    def __init__(self):
        self.blocks = {}
        self.cull_bottom_z = None  # downward faces of blocks at or below this z are never drawn
        self.skip_bottom = set()   # positions whose downward face is never drawn (e.g. the lowest terrain block)

    def set(self, x, y, z, name):
        """Place block `name` at integer (x, y, z); name=None removes it."""
        if name is None:
            self.blocks.pop((x, y, z), None)
        else:
            assert name in BLOCKS, "unknown block: %r" % (name,)
            self.blocks[(x, y, z)] = name

    def get(self, x, y, z):
        """Block name at (x, y, z) or None."""
        return self.blocks.get((x, y, z))

    def fill(self, x0, y0, z0, x1, y1, z1, name):
        """Fill the inclusive box with `name` (None clears it)."""
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, name)

    def top(self, x, y, z_from=40, z_to=-8):
        """Highest z in column (x, y) holding a full opaque cube, or None."""
        for z in range(z_from, z_to - 1, -1):
            n = self.blocks.get((x, y, z))
            if n is not None and BLOCKS[n].full:
                return z
        return None

    def _hides(self, x, y, z, d, me):
        """Does the neighbour in direction d fully hide a cell-boundary face of block `me` at (x, y, z)?"""
        dx, dy, dz = _DIRS[d]
        nb = self.blocks.get((x + dx, y + dy, z + dz))
        if nb is None:
            return False
        nd = BLOCKS[nb]
        if nd.full:
            return True
        if d == "t" and nd.kind == "opaque" and (nd.shape in ("cube", "slab") or nd.shape.startswith("stairs")):
            return True
        if d == "b" and nd.kind == "opaque" and nd.shape == "slab_top":
            return True
        if nb == me.name:
            if me.cull_same:
                return True
            s = me.shape
            if s in ("slab", "slab_top", "plate") and d in "nsew":
                return True
            if s in ("stairs_n", "stairs_s") and d in "ew":
                return True
            if s in ("stairs_e", "stairs_w") and d in "ns":
                return True
        return False

    def _connect(self, x, y, z, family):
        """Directions in which a fence / wall / pane at (x, y, z) joins its neighbours."""
        out = ""
        for d in "nsew":
            dx, dy, dz = _DIRS[d]
            nb = self.blocks.get((x + dx, y + dy, z))
            if nb is None:
                continue
            nd = BLOCKS[nb]
            if nd.full or nd.shape in family or (family[0] == "pane" and nb == "glass"):
                out += d
        return out

    def build(self, collection, name="world"):
        """Mesh the world: hidden faces culled, per-face pixel UVs. Returns one Object per material kind."""
        builders = {}

        def mb_for(kind):
            if kind not in builders:
                builders[kind] = MeshBuilder()
            return builders[kind]

        blocks = self.blocks
        for (x, y, z), bname in blocks.items():
            bd = BLOCKS[bname]
            mb = mb_for(bd.kind)
            ox, oy, oz = x * T, y * T, z * T
            org = (ox, oy, oz)
            h = pos_hash(x, y, z)
            if bd.shape == "cube":
                ht = bd.height
                for f in ALL_FACES:
                    dx, dy, dz = _DIRS[f]
                    nb = blocks.get((x + dx, y + dy, z + dz))
                    z_lo = 0
                    if f == "b":
                        if self.cull_bottom_z is not None and z <= self.cull_bottom_z:
                            continue
                        if (x, y, z) in self.skip_bottom:
                            continue
                        if nb is not None and (BLOCKS[nb].full or (nb == bname and bd.cull_same)
                                               or (BLOCKS[nb].kind == "opaque" and BLOCKS[nb].shape == "slab_top")):
                            continue
                    elif f == "t":
                        if ht == 16 and nb is not None:
                            nd = BLOCKS[nb]
                            if (nd.kind == "opaque" and nd.shape in ("cube", "slab")) or nd.shape.startswith("stairs") \
                                    or (nb == bname and bd.cull_same):
                                continue
                        if ht < 16 and nb == bname and bd.cull_same:
                            continue
                    else:
                        if nb is not None:
                            nd = BLOCKS[nb]
                            if nb == bname and (bd.cull_same or ht < 16):
                                continue
                            if nd.kind == "opaque" and nd.shape == "cube":
                                if nd.height >= ht:
                                    continue
                                z_lo = nd.height
                    if f == "t":
                        tiles, rot = bd.top, ((h >> 4) & 3 if bd.rot_top else 0)
                    elif f == "b":
                        tiles, rot = bd.bottom, 0
                    else:
                        tiles, rot = bd.side, 0
                    if bd.axis != "z":
                        ends = "ew" if bd.axis == "x" else "ns"
                        if f in ends:
                            tiles, rot = bd.top, 0
                        else:
                            tiles = bd.side
                            rot = 1 if (bd.axis == "x" or f in "ew") else 0
                    tile = tiles[(h >> 8) % len(tiles)] if len(tiles) > 1 else tiles[0]
                    lo = (ox, oy, oz + z_lo)
                    hi = (ox + T, oy + T, oz + ht)
                    mb.face(f, lo, hi, tile, org, rot)
                continue

            tex = {"top": bd.top[(h >> 8) % len(bd.top)], "side": bd.side[(h >> 8) % len(bd.side)],
                   "bottom": bd.bottom[(h >> 8) % len(bd.bottom)]}
            if bd.shape == "cross":
                tile = tex["top"]
                jx = ((h >> 3) % 9 - 4) * 0.7
                jy = ((h >> 11) % 9 - 4) * 0.7
                flip = (h >> 20) & 1
                cx, cy = ox + 8 + jx, oy + 8 + jy
                k = 8 * 0.70711
                u = (16, 0, 0, 16) if flip else (0, 0, 16, 16)
                mb.plane((cx - k, cy - k), (cx + k, cy + k), oz, oz + 16, tile, u)
                mb.plane((cx - k, cy + k), (cx + k, cy - k), oz, oz + 16, tile, u)
                continue
            if bd.shape == "crop":
                tile = tex["top"]
                zb = oz - 1
                for o in (4, 12):
                    u = (16, 0, 0, 16) if ((h >> o) & 1) else (0, 0, 16, 16)
                    mb.plane((ox, oy + o), (ox + 16, oy + o), zb, zb + 16, tile, u)
                    mb.plane((ox + o, oy), (ox + o, oy + 16), zb, zb + 16, tile, u)
                continue
            if bd.shape in ("fence", "wall"):
                parts = fence_parts(self._connect(x, y, z, ("fence", "wall")), wall=bd.shape == "wall")
            elif bd.shape == "pane":
                parts = pane_parts(self._connect(x, y, z, ("pane",)))
            else:
                parts = shape_parts(bd.shape)
            for lo, hi, faces in parts:
                for f in faces:
                    axis, sign = _FACES[f][0], _FACES[f][1]
                    edge = hi[axis] == 16 if sign > 0 else lo[axis] == 0
                    if edge and self._hides(x, y, z, f, bd):
                        continue
                    mb.face(f, (ox + lo[0], oy + lo[1], oz + lo[2]), (ox + hi[0], oy + hi[1], oz + hi[2]), tex, org)

        objs = []
        for kind in Atlas.KINDS:
            if kind in builders and len(builders[kind]):
                objs.append(builders[kind].to_object("%s_%s" % (name, kind), collection))
        return objs

    def face_count(self):
        """Number of blocks stored (not faces); handy for debugging."""
        return len(self.blocks)


# --------------------------------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------------------------------

REQUIRED = ["grass", "dirt", "path", "coarse_dirt", "farmland", "stone", "cobble", "mossy_cobble", "stone_bricks",
            "oak_planks", "oak_log", "spruce_planks", "oak_leaves", "glass", "bookshelf", "hay", "water",
            "wool_white", "terracotta_white", "gravel"]


def save_atlas_sheet(name="blocks_atlas", scale=6, width=1080, only=None):
    """Write every atlas tile, enlarged and laid out in rows, to out/test/<name>.png for direct inspection."""
    import os

    from PIL import Image

    from . import quick

    os.makedirs(quick.TEST_DIR, exist_ok=True)
    names = [n for n in ATLAS.tiles if only is None or only(n)]
    gap = 4
    x = y = gap
    row_h = 0
    places = []
    for n in names:
        w, h = ATLAS.size(n)
        w, h = w * scale, h * scale
        if x + w + gap > width:
            x = gap
            y += row_h + gap
            row_h = 0
        places.append((n, x, y, w, h))
        x += w + gap
        row_h = max(row_h, h)
    sheet = np.zeros((y + row_h + gap, width, 3), np.uint8)
    yy, xx = np.mgrid[0 : sheet.shape[0], 0 : sheet.shape[1]]
    sheet[:] = np.where(((xx // 12 + yy // 12) % 2)[..., None] == 0, 96, 74)
    for n, x, y, w, h in places:
        t = ATLAS.get(n).astype(np.float32)
        t = np.repeat(np.repeat(t, scale, 0), scale, 1)
        al = t[..., 3:4] / 255.0
        sheet[y : y + h, x : x + w] = (t[..., :3] * al + sheet[y : y + h, x : x + w] * (1 - al)).astype(np.uint8)
    path = os.path.join(quick.TEST_DIR, name + ".png")
    Image.fromarray(sheet, "RGB").save(path)
    return path


def _selftest():
    from . import quick

    missing = [b for b in REQUIRED if b not in BLOCKS]
    assert not missing, missing
    save_atlas_sheet()

    # --- still 1: swatch wall of every cube block ---------------------------------------------------
    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, "golden")
    coll = bpy.data.collections.new("test")
    scene.collection.children.link(coll)
    w = World()
    w.cull_bottom_z = -1
    w.fill(-6, -8, -1, 12, 6, -1, "grass")
    cubes = [n for n, b in BLOCKS.items() if b.shape == "cube" and not n.startswith("carpet")]
    cols = 4
    for i, n in enumerate(cubes):
        cx, cz = i % cols, i // cols
        w.fill(cx * 2, 0, cz * 2, cx * 2, 0, cz * 2, n)
    objs = w.build(coll, "swatch")
    faces = sum(len(o.data.polygons) for o in objs)
    rows = (len(cubes) + cols - 1) // cols
    print("cube blocks:", len(cubes), "rows:", rows, "faces:", faces)
    quick.camera(scene, (12.0, -31.0, rows + 5.0), (3.5, 0.5, rows - 0.4), lens=46)
    print("wrote", quick.render(scene, "blocks_swatch"))

    # --- still 2: a little diorama using shapes, plants, culling ----------------------------------------
    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, "golden")
    coll = bpy.data.collections.new("test")
    scene.collection.children.link(coll)
    w = World()
    w.cull_bottom_z = -1
    w.fill(-8, -8, -1, 10, 10, -1, "grass")
    w.fill(-1, -8, -1, 0, -1, -1, "path")
    # tiny hut
    w.fill(-2, 0, 0, 3, 4, 0, "cobble")
    w.fill(-2, 0, 1, 3, 4, 2, "oak_planks")
    w.fill(-1, 1, 0, 2, 3, 2, None)
    for cx, cy in ((-2, 0), (3, 0), (-2, 4), (3, 4)):
        w.fill(cx, cy, 0, cx, cy, 2, "oak_log")
    w.set(0, 0, 0, None)
    w.set(0, 0, 1, None)
    w.set(2, 0, 1, "glass_pane")
    w.set(-1, 0, 1, "glass")
    for i in range(3):
        w.fill(-3, -1 + i, 3 + i, 4, -1 + i, 3 + i, "spruce_stairs_n")
        w.fill(-3, 5 - i, 3 + i, 4, 5 - i, 3 + i, "spruce_stairs_s")
        if i:
            w.fill(-2, i, 3, -2, 4 - i, 2 + i, "oak_planks")
            w.fill(3, i, 3, 3, 4 - i, 2 + i, "oak_planks")
    w.fill(-3, 2, 5, 4, 2, 5, "spruce_slab")
    # fence, farmland, water, wheat
    for x in range(5, 10):
        w.set(x, -2, 0, "oak_fence")
        w.set(x, 3, 0, "oak_fence")
    for y in range(-2, 4):
        w.set(5, y, 0, "oak_fence")
        w.set(9, y, 0, "oak_fence")
    w.set(5, 0, 0, None)
    w.fill(6, -1, -1, 8, 2, -1, "farmland")
    w.fill(7, -1, -1, 7, 2, -1, "water")
    for y in range(-1, 3):
        w.set(6, y, 0, "wheat_%d" % (7 - (y + 1)))
        w.set(8, y, 0, "wheat_%d" % (2 * (y + 1) + 1))
    # details
    w.set(-4, -3, 0, "hay")
    w.set(-4, -2, 0, "hay")
    w.set(-4, -3, 1, "cobble_slab")
    w.set(-5, -5, 0, "cobble_wall")
    w.set(-4, -5, 0, "cobble_wall")
    w.set(2, -3, 0, "oak_log_x")
    w.set(3, -3, 0, "oak_log_x")
    w.set(2, -5, 0, "stone_bricks_stairs_e")
    w.set(3, -5, 0, "stone_bricks")
    w.set(4, -5, 0, "stone_bricks_stairs_w")
    for i, k in enumerate(("poppy", "dandelion", "cornflower", "daisy", "tall_grass", "short_grass", "tall_grass")):
        w.set(-7 + i, -6, 0, k)
    r = pix.rng(5)
    for _ in range(40):
        x, y = int(r.integers(-8, 11)), int(r.integers(-8, 11))
        if w.get(x, y, 0) is None and w.get(x, y, -1) == "grass":
            w.set(x, y, 0, "tall_grass" if r.random() < 0.7 else "short_grass")
    # a small oak
    w.fill(-6, 6, 0, -6, 6, 3, "oak_log")
    w.fill(-8, 4, 3, -4, 8, 4, "oak_leaves")
    w.fill(-7, 5, 5, -5, 7, 6, "oak_leaves")
    w.fill(-6, 6, 3, -6, 6, 4, "oak_log")
    objs = w.build(coll, "diorama")
    print("diorama faces:", sum(len(o.data.polygons) for o in objs), [o.name for o in objs])
    quick.camera(scene, (15.0, -24.0, 12.0), (1.0, 0.5, 1.6), lens=25)
    print("wrote", quick.render(scene, "blocks_shapes"))


if __name__ == "__main__":
    _selftest()
