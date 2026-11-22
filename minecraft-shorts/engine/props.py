"""Small box-model props in the same pixel style as the blocks (all original, generated in code).

Every `make_*` returns ONE object whose origin is the bottom centre of the block cell it stands in
(exceptions, as the contract says: the bell's origin is its swing pivot at the top; the door's origin is
its hinge). Objects are linked to `collection` if given, otherwise to a "props" collection of the current
scene, so they always render. Children (lantern light, bell clapper) are linked alongside.

Facing convention: a prop with a "front" (lectern, blast furnace, smithing table) shows it toward -Y,
i.e. a villager working at it stands on the -Y side looking +Y.
"""
import math

import bpy
import numpy as np

from . import pix
from .blocks import ALL_FACES, ATLAS, BLOCKS, MeshBuilder, T, fence_parts, from_ascii, pane_parts, rot_xf, \
    shape_parts, tex_planks, tex_wool, _c, _jitter, _noise, _out, OAK, SPRUCE, DARKWOOD

C = (-8, -8, 0)  # UV origin: min corner of the prop's own block cell (prop origin = bottom centre of that cell)

BELL_PIVOT_Z = 2.0  # height of the bell's hang point above the bell-frame origin
BED_TOP = 9.5 / 16  # height of the top of the blanket above the bed origin
LANTERN_COLOR = (1.0, 0.66, 0.34)
LANTERN_ENERGY = 45.0  # default watts of a lantern's point light
BED_COLORS = {"red": "#b8322b", "blue": "#3a5cc0", "green": "#55903a", "yellow": "#dba824", "white": "#e9e9e6",
              "purple": "#7c429c", "cyan": "#2f9ca6", "orange": "#dc7630"}

# --------------------------------------------------------------------------------------------------
# prop textures
# --------------------------------------------------------------------------------------------------


def tex_bell():
    """Bronze-gold bell skin, lit from the left: rows are hanger, crown, shoulder, engraved body, bright rim."""
    r = pix.rng(301)
    gold = np.array([_c(h) for h in ("#fff3b0", "#fbd75c", "#e9b637", "#c98f22", "#9a6a17", "#6b470f")])
    col = [3, 3, 3, 2, 1, 0, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4]
    a = np.empty((T, T, 3), np.int16)
    for px in range(T):
        a[:, px] = gold[col[px]]
    a[2:4] = gold[np.minimum(5, np.array(col) + 1)]      # crown, a tone darker
    a[9] = gold[np.minimum(5, np.array(col) + 2)]        # engraved band
    a[11] = gold[np.minimum(5, np.array(col) + 2)]       # shadow line above the rim
    a[12:14] = gold[np.maximum(0, np.array(col) - 1)]    # rim, a tone brighter
    a[0:2] = _c("#3b342c")
    a[14:16] = _c("#3b342c")
    return _out(_jitter(r, a, 2))


def tex_bell_top():
    """Top of the bell parts: plain gold with a darker rim line."""
    r = pix.rng(302)
    a = _noise(r, ["#e9b637", "#e2ad30", "#efbf42"], [4, 3, 2])
    yy, xx = np.mgrid[0:T, 0:T]
    ring = np.maximum(np.abs(xx - 7.5), np.abs(yy - 7.5))
    a[(ring > 4) & (ring < 5.5)] = _c("#c98f22")
    return _out(a)


def tex_iron(seed=303, base=("#4a433c", "#3b342c", "#5a5148")):
    """Dark wrought iron."""
    r = pix.rng(seed)
    return _out(_noise(r, list(base), [4, 3, 2]))


def tex_lantern():
    """Lantern parts packed in one 16x16 tile: side (0,0,6,7), top (6,0,12,6), cap side (12,0,16,2),
    cap top (12,2,16,6), chain (12,6,15,9), glowing bottom (6,6,12,12)."""
    pal = {"k": "#2b2622", "K": "#4a423a", "L": "#5f564c", "y": "#ffae42", "Y": "#ffd76e", "W": "#fff7cf",
           ".": "#2b2622"}
    rows = [
        "kKKKKkkKKKKkKLLK",
        "KyYYyKKLLLLKkKKk",
        "KYWWYKKLkkLKKKKK",
        "KYWWYKKLkkLKKLLK",
        "KYWWYKKLLLLKKLLK",
        "KyYYyKkKKKKkKKKK",
        "kKKKKkkKKKKkKLK.",
        "......KyYYyKLkL.",
        "......KYWWYKKLK.",
        "......KYWWYK....",
        "......KyYYyK....",
        "......kKKKKk....",
        "................",
        "................",
        "................",
        "................",
    ]
    return from_ascii(rows, pal)


def tex_bed_blanket(color):
    """16x24 quilt: folded-back light band at the pillow end (top rows), stitched border, soft weave."""
    base = tex_wool(311, color)[..., :3].astype(np.int16)
    a = np.concatenate([base, base[:8]], 0)
    a[0:2] = np.clip(a[0:2] + 38, 0, 255)
    a[2] = (a[2] * 0.72).astype(np.int16)
    a[3:, 1] = (a[3:, 1] * 0.82).astype(np.int16)
    a[3:, 14] = (a[3:, 14] * 0.82).astype(np.int16)
    a[22] = (a[22] * 0.82).astype(np.int16)
    for y in range(7, 22, 5):
        a[y, 2:14] = (a[y, 2:14] * 0.9).astype(np.int16)
    return _out(a)


def tex_bed_pillow():
    """12x7 white pillow with a soft grey edge."""
    r = pix.rng(313)
    a = _noise(r, ["#f4f4f0", "#ebebe6", "#fbfbf8"], [4, 3, 2], (7, 12))
    a[0, :] = a[:, 0] = _c("#fdfdfb")
    a[-1, :] = a[:, -1] = _c("#c9c9c3")
    a[0, 0] = a[0, -1] = a[-1, 0] = a[-1, -1] = _c("#b5b5ae")
    return _out(a)


def tex_door():
    """16x32 oak door: framed, a four-pane window with real holes on top, two sunk panels below, iron fittings."""
    r = pix.rng(321)
    a = np.empty((32, T, 3), np.int16)
    a[:] = _c(OAK["base"])
    for x in (5, 10):
        a[:, x] = _c(OAK["dark"])
    a = _jitter(r, a, 3)
    alpha = np.full((32, T), 255, np.uint8)
    seam, dark, light = _c(OAK["seam"]), _c(OAK["dark"]), _c(OAK["light"])
    a[0, :] = a[31, :] = a[:, 0] = a[:, 15] = seam
    a[1, 1:15] = light
    a[2:14, 2] = a[2:14, 13] = dark
    a[2, 2:14] = a[13, 2:14] = dark
    a[3:13, 3:13] = seam
    for (x0, x1) in ((4, 7), (9, 12)):
        for (y0, y1) in ((4, 8), (9, 12)):
            alpha[y0:y1, x0:x1] = 0
    a[8, 3:13] = dark
    a[3:13, 7:9] = dark
    for (x0, x1) in ((3, 7), (9, 13)):
        a[17:28, x0:x1] = _c(OAK["dark"]) - 6
        a[17, x0:x1] = seam
        a[17:28, x0] = seam
        a[27, x0:x1] = light
        a[17:28, x1 - 1] = light
    a[15:17, 12:14] = _c("#3b342c")
    a[15, 12] = _c("#8a8078")
    for y in (5, 26):
        a[y : y + 2, 0:2] = _c("#3b342c")
    return _out(a, alpha)


def tex_trapdoor():
    """Oak hatch: thick frame, cross bars and four open holes, iron hinge on the top edge."""
    r = pix.rng(331)
    a = tex_planks(332, OAK)[..., :3].astype(np.int16)
    alpha = np.full((T, T), 255, np.uint8)
    seam, light = _c(OAK["seam"]), _c(OAK["light"])
    a[0, :] = a[15, :] = a[:, 0] = a[:, 15] = seam
    for (x0, x1) in ((3, 7), (9, 13)):
        for (y0, y1) in ((3, 7), (9, 13)):
            alpha[y0:y1, x0:x1] = 0
            a[y0 - 1, x0 - 1 : x1 + 1] = seam
            a[y1, x0 - 1 : x1 + 1] = light
            a[y0 - 1 : y1 + 1, x0 - 1] = seam
            a[y0 - 1 : y1 + 1, x1] = light
    a[0:2, 3:5] = a[0:2, 11:13] = _c("#3b342c")
    return _out(_jitter(r, a, 2), alpha)


def tex_composter_side():
    """Slatted bin side: dark corner posts, three pale slats with gaps."""
    r = pix.rng(341)
    a = np.empty((T, T, 3), np.int16)
    a[:] = _c("#a8834e")
    for y in range(T):
        k = y % 5
        if k == 4:
            a[y] = _c("#3a2816")
        elif k == 0:
            a[y] = _c("#bd9a62")
        elif k == 3:
            a[y] = _c("#8f6d3d")
    a[:, 0:2] = _c("#6a4a28")
    a[:, 14:16] = _c("#6a4a28")
    a[:, 1] = a[:, 14] = _c("#7c5a34")
    a[0] = _c("#7c5a34")
    return _out(_jitter(r, a, 3))


def tex_compost():
    """Rotting plant matter: dark browns flecked with greens."""
    r = pix.rng(342)
    return _out(_noise(r, ["#4a3a22", "#5a4a2a", "#3d5a26", "#6a7a30", "#33281a"], [4, 3, 2, 1, 2]))


def tex_blast_front(lit=True):
    """Furnace face: riveted iron bands, a slotted vent and a fire door (glowing when lit)."""
    r = pix.rng(351)
    a = _noise(r, ["#5c5c62", "#54545a", "#66666c"], [4, 3, 2])
    iron, rivet, black = _c("#35353b"), _c("#9a9aa2"), _c("#141416")
    for y in (0, 1, 14, 15):
        a[y] = iron
    a[1, ::4] = rivet
    a[14, 2::4] = rivet
    a[2:14, 0] = a[2:14, 15] = iron
    a[3:7, 3:13] = _c("#7a7a82")
    a[3, 3:13] = _c("#9a9aa2")
    a[4, 4:12] = black
    a[6, 4:12] = black
    a[8:14, 3:13] = iron
    a[8, 3:13] = _c("#4c4c54")
    if lit:
        fire = from_ascii(["oOYYOooO", "OYWWYOOY", "YWWWWYYW", "YWWWWWWY"],
                          {"o": "#e4571a", "O": "#ff8a1e", "Y": "#ffc53c", "W": "#fff2a8"})[..., :3]
        a[9:13, 4:12] = fire
    else:
        a[9:13, 4:12] = black
        a[12, 5:11] = _c("#2a2a2e")
    return _out(a)


def tex_blast_side():
    """Furnace flank: dark masonry strapped with iron."""
    r = pix.rng(352)
    a = _noise(r, ["#5c5c62", "#54545a", "#66666c"], [4, 3, 2])
    iron, rivet = _c("#35353b"), _c("#9a9aa2")
    for y in (0, 1, 14, 15):
        a[y] = iron
    a[1, 1::4] = rivet
    a[14, 3::4] = rivet
    a[7] = _c("#44444a")
    a[8] = _c("#6e6e76")
    a[2:14, 7:9] = iron
    a[4, 7] = a[11, 8] = rivet
    return _out(a)


def tex_blast_top():
    """Furnace top: iron plate with a square flue."""
    r = pix.rng(353)
    a = _noise(r, ["#4a4a50", "#424248", "#54545a"], [4, 3, 2])
    a[0, :] = a[15, :] = a[:, 0] = a[:, 15] = _c("#2c2c31")
    a[1, 1:15] = _c("#6e6e76")
    a[5:11, 5:11] = _c("#2c2c31")
    a[6:10, 6:10] = _c("#141416")
    for x, y in ((2, 2), (13, 2), (2, 13), (13, 13)):
        a[y, x] = _c("#9a9aa2")
    return _out(a)


def tex_smith_top():
    """Smithing table top: dark slate plate with a pale chamfer and tool scratches."""
    r = pix.rng(361)
    a = _noise(r, ["#3f4046", "#38393f", "#484950"], [4, 3, 2])
    a[0, :] = a[:, 0] = _c("#62636c")
    a[15, :] = a[:, 15] = _c("#26272b")
    for _ in range(4):
        x, y = r.integers(2, 12, 2)
        for i in range(int(r.integers(2, 4))):
            a[y + i, x + i] = _c("#62636c")
    return _out(a)


def tex_smith_side(front=False):
    """Smithing table flank: slate lip, stout legs and a dark recess (front: hammer and tongs hung inside)."""
    r = pix.rng(362 + int(front))
    a = np.empty((T, T, 3), np.int16)
    a[:] = _c("#49321f")
    a[:, 0:4] = _c("#7a5836")
    a[:, 12:16] = _c("#7a5836")
    a[:, 3] = a[:, 15] = _c("#5d4126")
    a[:, 0] = a[:, 12] = _c("#8d6a44")
    a[13:16, 4:12] = _c("#2e1f12")
    a = _jitter(r, a, 3)
    a[0:3] = _c("#3f4046")
    a[0] = _c("#62636c")
    a[3] = _c("#26272b")
    if front:
        a[5:7, 5:9] = _c("#9a9aa2")
        a[5, 5:9] = _c("#c2c2ca")
        a[7:13, 7] = _c("#c9a56c")
        a[5:12, 10] = _c("#77777f")
        a[5, 10] = _c("#c2c2ca")
        a[12, 9:12] = _c("#77777f")
    return _out(a)


def tex_barrel_side():
    """Barrel staves bound by two iron hoops."""
    r = pix.rng(371)
    a = np.empty((T, T, 3), np.int16)
    for x in range(T):
        k = x % 4
        tone = int(r.integers(-5, 6)) if k == 0 else tone
        a[:, x] = _c(SPRUCE["light"]) + tone if k in (0, 1) else _c(SPRUCE["base"]) + tone
        if k == 3:
            a[:, x] = _c(SPRUCE["seam"])
    a = _jitter(r, a, 3)
    for y in (2, 12):
        a[y] = _c("#6c6c74")
        a[y + 1] = _c("#3a3a40")
        a[y, ::5] = _c("#a2a2aa")
    return _out(a)


def tex_barrel_top():
    """Barrel head: stave-end rim around a planked lid with a bung."""
    r = pix.rng(372)
    a = tex_planks(373, SPRUCE)[..., :3].astype(np.int16) + 14
    yy, xx = np.mgrid[0:T, 0:T]
    ring = np.maximum(np.abs(xx - 7.5), np.abs(yy - 7.5))
    a[ring > 6] = _c(SPRUCE["dark"])
    a[(ring > 5) & (ring < 6.6)] = _c(SPRUCE["seam"])
    a[ring > 7] = _c("#3a3a40")
    a[7:9, 7:9] = _c("#2e1f12")
    return _out(_jitter(r, a, 2))


def tex_carto_top():
    """Cartography table top: parchment map with coast, sea, route dots and a red cross."""
    rows = [
        "wwwwwwwwwwwwwwww",
        "wppppppppppppppw",
        "wppggppppbbbbppw",
        "wpgggggppbbbbbpw",
        "wpgggggpppbbbbpw",
        "wppgggppppppbbpw",
        "wpppgppkpppppppw",
        "wppppppppkpppppw",
        "wpbbppppppkpgppw",
        "wbbbbpppppppggpw",
        "wbbbbbpprpprgggw",
        "wpbbbpppprrpgggw",
        "wppbppppprrpggpw",
        "wpppppppr.prpppw",
        "wppppppppppppppw",
        "wwwwwwwwwwwwwwww",
    ]
    pal = {"w": "#6a4c2a", "p": "#dccb9c", "g": "#86a85a", "b": "#6f9fca", "k": "#5a4a36", "r": "#c0392b",
           ".": "#dccb9c"}
    return from_ascii(rows, pal)


def tex_carto_side():
    """Cartography table flank: spruce boards under a rolled paper edge."""
    a = tex_planks(381, SPRUCE)[..., :3].astype(np.int16)
    a[0:3] = _c("#dccb9c")
    a[2] = _c("#b3a274")
    a[3] = _c(SPRUCE["seam"])
    a[0:3, 5] = a[0:3, 11] = _c("#b3a274")
    return _out(a)


def tex_book():
    """10x8 open book: two cream pages with lines of writing, a gutter and a red cover edge."""
    rows = [
        "rrrrrrrrrr",
        "rwwwwgwwwr",
        "rwkkwgkkwr",
        "rwwwwgwwwr",
        "rwkkwgkwwr",
        "rwwwwgwwwr",
        "rwkwwgkkwr",
        "rrrrrrrrrr",
    ]
    return from_ascii(rows, {"r": "#8e2f2a", "w": "#f3ecd6", "k": "#6b6252", "g": "#c9bf9f"})


def tex_emerald():
    """16x16 cut-gem sprite (transparent background)."""
    rows = [
        "................",
        "................",
        ".....oooooo.....",
        "....oHHLLLMo....",
        "...oHWHLLMMMo...",
        "...oHHLLMMMDo...",
        "...oHLLLMMDDo...",
        "...oLLLMMMDDo...",
        "...oLLMMMMDDo...",
        "...oLMMMMDDSo...",
        "...oMMMMDDSSo...",
        "...oMMMDDDSSo...",
        "....oMDDDSSo....",
        ".....oooooo.....",
        "................",
        "................",
    ]
    pal = {"o": "#0b5a2a", "W": "#eafff0", "H": "#9ff5c0", "L": "#4fe08a", "M": "#22c064", "D": "#14994a",
           "S": "#0e7438"}
    return from_ascii(rows, pal)


def _register():
    A = ATLAS.add
    A("bell", tex_bell(), "metal")
    A("bell_top", tex_bell_top(), "metal")
    A("bell_inner", _out(_noise(pix.rng(304), ["#5f3f0e", "#4a300a", "#6e4b12"], [4, 3, 2])), "metal")
    A("iron", tex_iron())
    A("lantern", tex_lantern(), "emit")
    A("bed_sheet", tex_wool(312, "#f6f6f2"))
    A("bed_pillow", tex_bed_pillow())
    for name, col in BED_COLORS.items():
        A("bed_blanket_" + name, tex_bed_blanket(col))
        A("bed_wool_" + name, tex_wool(311, col))
    A("door_oak", tex_door(), "cutout")
    A("trapdoor", tex_trapdoor(), "cutout")
    A("composter_side", tex_composter_side())
    A("compost", tex_compost())
    A("blast_front_lit", tex_blast_front(True), "emit")
    A("blast_front", tex_blast_front(False))
    A("blast_side", tex_blast_side())
    A("blast_top", tex_blast_top())
    A("smith_top", tex_smith_top())
    A("smith_side", tex_smith_side(False))
    A("smith_front", tex_smith_side(True))
    A("barrel_side", tex_barrel_side())
    A("barrel_top", tex_barrel_top())
    A("carto_top", tex_carto_top())
    A("carto_side", tex_carto_side())
    A("book", tex_book())
    A("emerald", tex_emerald(), "gem")


_register()

# --------------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------------


def props_collection():
    """The fallback "props" collection of the current scene (created on demand)."""
    scene = bpy.context.scene
    coll = scene.collection.children.get("props")
    if coll is None:
        coll = bpy.data.collections.new("props")
        scene.collection.children.link(coll)
    return coll


def link(obj, collection=None):
    """Link an object and all its children to `collection` (default: the scene's "props" collection)."""
    coll = collection or props_collection()
    stack = [obj]
    while stack:
        o = stack.pop()
        if o.name not in coll.objects:
            coll.objects.link(o)
        stack.extend(o.children)
    return obj


def _finish(mb, name, collection, children=()):
    obj = mb.to_object(name)
    for ch in children:
        ch.parent = obj
    return link(obj, collection)


def _cell(parts):
    """Shift shape parts from 0..16 cell coordinates to prop coordinates (origin at the bottom centre)."""
    return [((lo[0] - 8, lo[1] - 8, lo[2]), (hi[0] - 8, hi[1] - 8, hi[2]), f) for lo, hi, f in parts]


def _block_tex(material):
    bd = BLOCKS[material]
    return {"top": bd.top[0], "side": bd.side[0], "bottom": bd.bottom[0]}


def _cube(name, tex, collection):
    mb = MeshBuilder()
    mb.box((-8, -8, 0), (8, 8, 16), tex, uv_origin=C)
    return _finish(mb, name, collection)


# --------------------------------------------------------------------------------------------------
# bell
# --------------------------------------------------------------------------------------------------


def make_bell(collection=None):
    """Golden bell hanging from its origin (the swing pivot at the top); rotate about local X to swing.
    About 0.63 wide and 0.84 tall. A child object "bell_clapper" hangs inside and can be keyed separately."""
    o = (-8, -8, -16)
    mb = MeshBuilder()
    side = {"side": "bell", "top": "bell_top", "bottom": "bell_inner"}
    mb.box((-1, -1, -2), (1, 1, 0), side, "nsew", uv_origin=o)        # hanger loop
    mb.box((-2, -2, -4), (2, 2, -2), side, "nsewt", uv_origin=o)      # crown
    mb.box((-3, -3, -6), (3, 3, -4), side, "nsewt", uv_origin=o)      # shoulder
    mb.box((-4, -4, -11.5), (4, 4, -6), side, "nsewt", uv_origin=o)   # body
    mb.box((-5, -5, -13.5), (5, 5, -11.5), side, uv_origin=o)         # flared rim
    bell = mb.to_object("bell")
    cb = MeshBuilder()
    cb.box((-0.75, -0.75, -8.5), (0.75, 0.75, 0), "iron", uv_origin=(-8, -8, -16))
    cb.box((-1.5, -1.5, -10.5), (1.5, 1.5, -8.5), "iron", uv_origin=(-8, -8, -16))
    clapper = cb.to_object("bell_clapper")
    clapper.parent = bell
    clapper.location = (0, 0, -4.5 / 16)
    return link(bell, collection)


def make_bell_frame(collection=None):
    """Timber frame for the bell: two bark posts on stone footings, a dark crossbeam along X and a small cap.
    Hang the bell at local (0, 0, BELL_PIVOT_Z); it then swings along Y."""
    mb = MeshBuilder()
    for sx in (-1, 1):
        x0, x1 = (10, 14) if sx > 0 else (-14, -10)
        mb.box((x0 - 1, -3, 0), (x1 + 1, 3, 3), "cobble_0", uv_origin=C)
        mb.box((x0, -2, 3), (x1, 2, 32), "log_side_0", "nsew", uv_origin=C)
        b0, b1 = (7, 10) if sx > 0 else (-10, -7)
        mb.box((b0, -1.5, 29), (b1, 1.5, 32), "dark_planks_0", "nsewb", uv_origin=C)
    mb.box((-17, -2.5, 32), (17, 2.5, 36), "dark_planks_0", uv_origin=C)
    mb.box((-18, -4, 36), (18, 4, 38), "spruce_planks_0", uv_origin=C)
    mb.box((-18, -2, 38), (18, 2, 39.5), "spruce_planks_1", "nsewt", uv_origin=C)
    return _finish(mb, "bell_frame", collection)


# --------------------------------------------------------------------------------------------------
# lantern
# --------------------------------------------------------------------------------------------------


def make_lantern(hanging=True, collection=None, energy=LANTERN_ENERGY):
    """Iron lantern with a glowing core and a real warm point light (child object "<name>_light").
    hanging=True: hangs by a chain from the top of its cell; False: stands on the floor of its cell."""
    L = "lantern"
    side = (L, 0, 0, 6, 7)
    mb = MeshBuilder()
    z0 = 3 if hanging else 0
    mb.box((-3, -3, z0), (3, 3, z0 + 7), {"side": side, "t": (L, 6, 0, 12, 6), "b": (L, 6, 6, 12, 12)})
    mb.box((-2, -2, z0 + 7), (2, 2, z0 + 9), {"side": (L, 12, 0, 16, 2), "t": (L, 12, 2, 16, 6)}, "nsewt")
    link_tex = (L, 12, 6, 15, 9)
    if hanging:
        mb.box((-1.5, -0.5, 12), (1.5, 0.5, 14), link_tex)
        mb.box((-0.5, -1.5, 13.5), (0.5, 1.5, 15), link_tex)
        mb.box((-1.5, -0.5, 14.5), (1.5, 0.5, 16), link_tex)
    else:
        mb.box((-1.5, -0.5, 9), (1.5, 0.5, 11), link_tex)
    obj = mb.to_object("lantern")
    obj.visible_shadow = False  # the light sits inside the box
    light = bpy.data.lights.new("lantern_light", "POINT")
    light.color = LANTERN_COLOR
    light.energy = energy
    light.shadow_soft_size = 0.14
    lo = bpy.data.objects.new("lantern_light", light)
    lo.parent = obj
    lo.location = (0, 0, (z0 + 3.5) / 16)
    obj["light"] = lo.name
    return link(obj, collection)


def lantern_light(lantern):
    """The point-light child of a lantern made by make_lantern."""
    for ch in lantern.children:
        if ch.type == "LIGHT":
            return ch
    return None


# --------------------------------------------------------------------------------------------------
# furniture
# --------------------------------------------------------------------------------------------------


def make_bed(color="red", collection=None):
    """Bed, 1 x 2 blocks: origin at the bottom centre of the FOOT cell, pillow end one block further at +Y.
    Top of the blanket is BED_TOP above the origin. Colours: see BED_COLORS."""
    assert color in BED_COLORS, "bed colour must be one of %s" % sorted(BED_COLORS)
    wood = "dark_planks_0"
    mb = MeshBuilder()
    for lx in (-8, 5):
        mb.box((lx, -8, 0), (lx + 3, -5, 3), wood, "nsewb", uv_origin=C)
    mb.box((-8, 22, 0), (8, 24, 14), wood, uv_origin=C)  # headboard doubles as the head legs
    mb.box((-8, -8, 3), (8, 22, 6), "oak_planks_0", "sewtb", uv_origin=C)
    mb.box((-7.5, -7.5, 6), (7.5, 22, 9), "bed_sheet", "sewt", uv_origin=C)
    bt = "bed_blanket_" + color
    mb.box((-8.3, -8.3, 4.6), (8.3, 13, 9.5), {"t": (bt, 0, 0, 16, 21), "side": "bed_wool_" + color}, "nsewt",
           uv_origin=C)
    mb.box((-6, 14.5, 9), (6, 21.5, 11.5), {"t": ("bed_pillow", 0, 0, 12, 7), "side": "bed_sheet"}, "nsewt",
           uv_origin=C)
    return _finish(mb, "bed_" + color, collection)


def make_door(mirror=False, collection=None):
    """Oak door, 1 wide and 2 tall. The origin is the hinge: the slab runs from it along local +X (mirror=True:
    along -X) and is 3 px thick toward local -Y (the outside). Rotate about Z to open: +90 deg swings it to lie
    along local +Y (mirror: -90 deg). The upper window panes are real holes."""
    mb = MeshBuilder()
    d = "door_oak"
    fwd, back = (d, 0, 0, 16, 32), (d, 16, 0, 0, 32)
    if mirror:
        fwd, back = back, fwd
    lo, hi = ((-16, -3, 0), (0, 0, 32)) if mirror else ((0, -3, 0), (16, 0, 32))
    mb.box(lo, hi, {"s": fwd, "n": back, "all": "oak_planks_1"}, uv_origin=(lo[0], -8, 0))
    obj = _finish(mb, "door", collection)
    obj["open_angle"] = -math.pi / 2 if mirror else math.pi / 2
    return obj


def make_lectern(collection=None):
    """Reading stand: plank base, a column of book spines, a sloped desk and an open book; front toward -Y."""
    mb = MeshBuilder()
    mb.box((-7, -7, 0), (7, 7, 2), "oak_planks_0", uv_origin=C)
    mb.box((-4, -4, 2), (4, 4, 12.5), {"side": "bookshelf_0"}, "nsew", uv_origin=C)
    xf = rot_xf("x", 20, (0, 0, 13.5))
    mb.box((-8, -7.5, 12), (8, 7.5, 15), "oak_planks_1", uv_origin=C, xf=xf)
    mb.box((-5, -4, 15), (5, 4, 16.5), {"t": ("book", 0, 0, 10, 8), "side": "bed_sheet"}, "nsewt", uv_origin=C,
           xf=xf)
    return _finish(mb, "lectern", collection)


def make_composter(fill=0.6, collection=None):
    """Open slatted bin partly filled with compost (fill 0..1)."""
    mb = MeshBuilder()
    side = {"side": "composter_side", "top": "composter_side", "bottom": "dark_planks_0"}
    mb.box((-8, -8, 0), (8, 8, 2), side, "nsewb", uv_origin=C)
    mb.box((-8, -8, 2), (8, -6, 16), side, "nsewt", uv_origin=C)
    mb.box((-8, 6, 2), (8, 8, 16), side, "nsewt", uv_origin=C)
    mb.box((-8, -6, 2), (-6, 6, 16), side, "ewt", uv_origin=C)
    mb.box((6, -6, 2), (8, 6, 16), side, "ewt", uv_origin=C)
    top = 2 + max(0.0, min(1.0, fill)) * 12
    mb.box((-6, -6, 2), (6, 6, top), "compost", "t", uv_origin=C)
    return _finish(mb, "composter", collection)


def make_blast_furnace(lit=True, collection=None):
    """Iron-banded furnace; the fire door faces -Y. lit=True makes the fire glow and adds a small orange
    point light child ("<name>_light") just in front of the door."""
    front = "blast_front_lit" if lit else "blast_front"
    obj = _cube("blast_furnace", {"s": front, "side": "blast_side", "top": "blast_top", "bottom": "blast_top"},
                collection)
    if lit:
        light = bpy.data.lights.new("furnace_light", "POINT")
        light.color = (1.0, 0.45, 0.15)
        light.energy = 12.0
        light.shadow_soft_size = 0.2
        lo = bpy.data.objects.new("furnace_light", light)
        lo.parent = obj
        lo.location = (0, -0.62, 0.3)
        link(obj, collection)
    return obj


def make_smithing_table(collection=None):
    """Smithing table: slate top on stout legs, hammer and tongs hanging on the -Y face."""
    return _cube("smithing_table", {"s": "smith_front", "side": "smith_side", "top": "smith_top",
                                    "bottom": "dark_planks_0"}, collection)


def make_barrel(collection=None):
    """Upright barrel with iron hoops."""
    return _cube("barrel", {"side": "barrel_side", "top": "barrel_top", "bottom": "barrel_top"}, collection)


def make_cartography_table(collection=None):
    """Map-maker's table (extra workstation): a parchment map on spruce boards."""
    return _cube("cartography_table", {"side": "carto_side", "top": "carto_top", "bottom": "spruce_planks_0"},
                 collection)


# --------------------------------------------------------------------------------------------------
# building parts
# --------------------------------------------------------------------------------------------------


def make_stairs(material="oak_planks", facing="n", collection=None):
    """One stair block of a BLOCKS material; `facing` (n/e/s/w) is the high side."""
    mb = MeshBuilder()
    tex = _block_tex(material)
    for lo, hi, f in _cell(shape_parts("stairs_" + facing)):
        mb.box(lo, hi, tex, f, uv_origin=C)
    return _finish(mb, material + "_stairs", collection)


def make_slab(material="oak_planks", top=False, collection=None):
    """Half-height slab of a BLOCKS material (top=True: upper half of the cell)."""
    mb = MeshBuilder()
    for lo, hi, f in _cell(shape_parts("slab_top" if top else "slab")):
        mb.box(lo, hi, _block_tex(material), f, uv_origin=C)
    return _finish(mb, material + "_slab", collection)


def make_fence(connect="", material="oak_planks", collection=None):
    """Fence post; `connect` lists the sides with rails, e.g. "ns" or "ew"."""
    mb = MeshBuilder()
    for lo, hi, f in _cell(fence_parts(connect)):
        mb.box(lo, hi, _block_tex(material), f, uv_origin=C)
    return _finish(mb, "fence", collection)


def make_trapdoor(upright=True, collection=None):
    """Oak hatch with four open holes. upright=True: stands on the -Y edge of its cell (3 px thick, closing the
    lower half of an opening); False: lies flat on the floor of its cell."""
    mb = MeshBuilder()
    t = "trapdoor"
    if upright:
        mb.box((-8, -8, 0), (8, -5, 16), {"s": (t, 0, 0, 16, 16), "n": (t, 16, 0, 0, 16), "all": "oak_planks_0"},
               uv_origin=C)
    else:
        mb.box((-8, -8, 0), (8, 8, 3), {"t": (t, 0, 0, 16, 16), "b": (t, 0, 16, 16, 0), "all": "oak_planks_0"},
               uv_origin=C)
    return _finish(mb, "trapdoor", collection)


def make_glass_pane(connect="ew", edge=False, collection=None):
    """Thin glass pane through the middle of its cell; `connect` lists joined sides ("ew" runs along X).
    edge=True instead puts an X-running pane on the -Y edge of the cell (to close a cell front)."""
    mb = MeshBuilder()
    tex = {"side": "glass", "top": "glass_edge", "bottom": "glass_edge"}
    if edge:
        mb.box((-8, -8, 0), (8, -6, 16), {"s": "glass", "all": "glass_edge"}, "sewtb", uv_origin=C)
    else:
        for lo, hi, f in _cell(pane_parts(connect)):
            mb.box(lo, hi, tex, f, uv_origin=C)
    return _finish(mb, "glass_pane", collection)


# --------------------------------------------------------------------------------------------------
# plants and items
# --------------------------------------------------------------------------------------------------


def _cross(tile, name, collection, flip=False):
    mb = MeshBuilder()
    k = 8 * 0.70711
    u = (16, 0, 0, 16) if flip else (0, 0, 16, 16)
    mb.plane((-k, -k), (k, k), 0, 16, tile, u)
    mb.plane((-k, k), (k, -k), 0, 16, tile, u)
    return _finish(mb, name, collection)


def make_tall_grass(seed=0, collection=None):
    """Tuft of tall grass (two crossed cards); `seed` picks one of the blade patterns and mirrors it."""
    names = ["tall_grass_0", "tall_grass_1", "tall_grass_2", "tall_grass_3", "short_grass_0", "short_grass_1"]
    return _cross(names[seed % len(names)], "tall_grass", collection, flip=bool((seed // len(names)) % 2))


def make_flower(kind="poppy", collection=None):
    """Small flower (two crossed cards). kinds: poppy, dandelion, cornflower, daisy."""
    assert kind in ("poppy", "dandelion", "cornflower", "daisy")
    return _cross(kind, kind, collection)


def make_wheat(stage=7, collection=None):
    """Wheat crop for one farmland cell at growth stage 0..7 (7 = ripe gold)."""
    tile = "wheat_%d" % max(0, min(7, int(stage)))
    mb = MeshBuilder()
    for o in (-4, 4):
        mb.plane((-8, o), (8, o), -1, 15, tile)
        mb.plane((o, -8), (o, 8), -1, 15, tile)
    return _finish(mb, "wheat", collection)


EMERALD_SCALE = 1.0 / 30  # world units per sprite pixel


def make_emerald(collection=None):
    """Emerald as a small held item: a 1-pixel-thick extruded gem sprite, about 0.30 wide x 0.37 tall, standing
    in the XZ plane with its origin at the bottom centre of the gem. Slightly glowing and glossy."""
    spr = ATLAS.get("emerald")
    solid = spr[..., 3] > 127
    ys, xs = np.nonzero(solid)
    bottom = ys.max() + 1
    cx = (xs.min() + xs.max() + 1) / 2.0
    mb = MeshBuilder(scale=EMERALD_SCALE)
    for py, px in zip(ys, xs):
        faces = "ns"
        if px == 0 or not solid[py, px - 1]:
            faces += "w"
        if px == 15 or not solid[py, px + 1]:
            faces += "e"
        if py == 0 or not solid[py - 1, px]:
            faces += "t"
        if py == 15 or not solid[py + 1, px]:
            faces += "b"
        rect = ("emerald", px, py, px + 1, py + 1)
        mb.box((px - cx, -0.5, bottom - py - 1), (px + 1 - cx, 0.5, bottom - py), rect, faces)
    return _finish(mb, "emerald", collection)


# --------------------------------------------------------------------------------------------------
# self-test: labelled line-ups
# --------------------------------------------------------------------------------------------------

_FONT = {
    "A": "010101111101101", "B": "110101110101110", "C": "011100100100011", "D": "110101101101110",
    "E": "111100110100111", "F": "111100110100100", "G": "011100101101011", "H": "101101111101101",
    "I": "111010010010111", "J": "001001001101010", "K": "101101110101101", "L": "100100100100111",
    "M": "101111111101101", "N": "110101101101101", "O": "010101101101010", "P": "110101110100100",
    "Q": "010101101111011", "R": "110101110101101", "S": "011100010001110", "T": "111010010010010",
    "U": "101101101101111", "V": "101101101101010", "W": "101101111111101", "X": "101101010101101",
    "Y": "101101010010010", "Z": "111001010100111", " ": "000000000000000", "_": "000000000000111",
    "0": "111101101101111", "1": "010110010010111", "2": "110001010100111", "3": "110001010001110",
    "4": "101101111001001", "5": "111100110001110", "6": "011100111101111", "7": "111001010010010",
    "8": "111101111101111", "9": "111101111001110",
}


def _draw_label(img, text, cx, y, px=3):
    """Draw `text` centred at cx with our own 3x5 test font onto a PIL image (white on a dark plate)."""
    from PIL import ImageDraw

    text = text.upper()
    w = len(text) * 4 * px
    x0 = int(cx - w / 2)
    d = ImageDraw.Draw(img)
    d.rectangle([x0 - px, y - px, x0 + w, y + 5 * px + px - 1], fill=(20, 20, 24))
    for i, ch in enumerate(text):
        bits = _FONT.get(ch, _FONT[" "])
        for k, b in enumerate(bits):
            if b == "1":
                gx, gy = k % 3, k // 3
                xx, yy = x0 + (i * 4 + gx) * px, y + gy * px
                d.rectangle([xx, yy, xx + px - 1, yy + px - 1], fill=(255, 255, 255))


def _lineup(name, makers, cols=4, preset="golden", spacing=(2.3, 3.0)):
    """Render a labelled grid of props (landscape frame) to out/test/<name>.png."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    from PIL import Image

    from . import quick
    from .blocks import World

    scene = quick.reset()
    quick.setup(scene, res=(960, 540))
    quick.light(scene, preset)
    coll = bpy.data.collections.new("lineup")
    scene.collection.children.link(coll)
    rows = (len(makers) + cols - 1) // cols
    width = (cols - 1) * spacing[0] + 1
    depth = (rows - 1) * spacing[1] + 1
    w = World()
    w.cull_bottom_z = -1
    w.fill(-5, -4, -1, int(width) + 5, int(depth) + 6, -1, "grass")
    w.fill(-2, -2, -1, int(width) + 2, int(depth) + 2, -1, "stone_bricks")
    w.fill(-5, int(depth) + 4, 0, int(width) + 5, int(depth) + 4, 4, "terracotta_white")
    w.build(coll, "stage")
    labels = []
    for i, (label, fn) in enumerate(makers):
        cx = 0.5 + (i % cols) * spacing[0]
        cy = 0.5 + (rows - 1 - i // cols) * spacing[1]
        obj = fn(coll)
        obj.location = (cx + obj.location.x, cy + obj.location.y, obj.location.z)
        labels.append((label, Vector((cx, cy - 0.75, 0.0))))
    camo = quick.camera(scene, (width / 2 + 1.2, -6.2, 4.4), (width / 2, depth * 0.42, 0.6), lens=30)
    path = quick.render(scene, name)
    bpy.context.view_layer.update()
    img = Image.open(path).convert("RGB")
    W, H = img.size
    for label, p in labels:
        ndc = world_to_camera_view(scene, camo, p)
        _draw_label(img, label, ndc.x * W, int((1 - ndc.y) * H), px=2)
    img.save(path)
    return path


def _closeups():
    """Two cinematic close-ups in the reference style: the bell at golden hour and a bed under a lantern at night."""
    from . import quick
    from .blocks import World

    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, "golden")
    coll = bpy.data.collections.new("close")
    scene.collection.children.link(coll)
    w = World()
    w.cull_bottom_z = -1
    w.fill(-12, -12, -1, 12, 14, -1, "grass")
    w.fill(-4, -4, -1, 4, 4, -1, "path")
    w.fill(-8, 9, 0, 8, 9, 3, "oak_planks")
    w.fill(-8, 9, 0, 8, 9, 0, "cobble")
    w.build(coll, "stage")
    frame = make_bell_frame(coll)
    frame.location = (0.5, 0.5, 0)
    bell = make_bell(coll)
    bell.location = (0.5, 0.5, BELL_PIVOT_Z)
    bell.rotation_euler = (math.radians(24), 0, 0)
    bell.children[0].rotation_euler = (math.radians(-30), 0, 0)
    quick.camera(scene, (2.6, -1.9, 1.35), (0.5, 0.5, 1.62), lens=42, fstop=1.4)
    print("wrote", quick.render(scene, "props_bell"))

    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, "night")
    coll = bpy.data.collections.new("close")
    scene.collection.children.link(coll)
    w = World()
    w.cull_bottom_z = -1
    w.fill(-4, -4, -1, 5, 5, -1, "oak_planks")
    w.fill(-4, 5, 0, 5, 5, 3, "oak_planks")
    w.fill(5, -4, 0, 5, 5, 3, "oak_planks")
    w.fill(-4, 5, 0, 5, 5, 0, "cobble")
    w.fill(-4, -4, 4, 5, 5, 4, "spruce_planks")
    w.set(1, 5, 1, "glass_pane")
    w.set(1, 5, 2, "glass_pane")
    w.build(coll, "stage")
    bed = make_bed("red", coll)
    bed.location = (0.5, 2.5, 0)
    bed2 = make_bed("cyan", coll)
    bed2.location = (3.5, 2.5, 0)
    lan = make_lantern(True, coll)
    lan.location = (2.0, 2.5, 3)
    barrel = make_barrel(coll)
    barrel.location = (-1.5, 4.5, 0)
    quick.camera(scene, (-1.6, -1.4, 1.05), (0.9, 3.4, 0.75), lens=24, fstop=1.4)
    print("wrote", quick.render(scene, "props_bed_night"))


def _selftest():
    from .blocks import save_atlas_sheet

    print("wrote", save_atlas_sheet("props_atlas", only=lambda n: n in _PROP_TILES))

    def bell_set(coll):
        frame = make_bell_frame(coll)
        bell = make_bell(coll)
        bell.parent = frame
        bell.location = (0, 0, BELL_PIVOT_Z)
        bell.rotation_euler = (math.radians(18), 0, 0)
        return frame

    def door_set(coll):
        d = make_door(collection=coll)
        d.location = (-0.5, 0, 0)
        return d

    def door_open(coll):
        d = make_door(collection=coll)
        d.location = (-0.5, 0, 0)
        d.rotation_euler = (0, 0, math.radians(60))
        return d

    def tilt(fn, **kw):
        def f(coll):
            o = fn(collection=coll, **kw)
            return o
        return f

    def emerald(coll):
        o = make_emerald(coll)
        o.location = (0, 0, 0.3)
        o.rotation_euler = (0, 0, math.radians(-25))
        return o

    items = [
        ("bell", bell_set),
        ("lantern", tilt(make_lantern, hanging=False)),
        ("hang lantern", lambda c: _raised(make_lantern(True, c), 0.8)),
        ("door", door_set),
        ("bed red", tilt(make_bed, color="red")),
        ("bed blue", tilt(make_bed, color="blue")),
        ("bed green", tilt(make_bed, color="green")),
        ("door open", door_open),
        ("lectern", tilt(make_lectern)),
        ("composter", tilt(make_composter)),
        ("furnace", tilt(make_blast_furnace)),
        ("smithing", tilt(make_smithing_table)),
        ("barrel", tilt(make_barrel)),
        ("carto table", tilt(make_cartography_table)),
        ("stairs", tilt(make_stairs, material="cobble", facing="n")),
        ("slab", tilt(make_slab, material="spruce_planks")),
        ("fence", tilt(make_fence, connect="ew")),
        ("trapdoor", tilt(make_trapdoor)),
        ("pane", tilt(make_glass_pane)),
        ("emerald", emerald),
        ("tall grass", tilt(make_tall_grass, seed=1)),
        ("poppy", tilt(make_flower, kind="poppy")),
        ("cornflower", tilt(make_flower, kind="cornflower")),
        ("wheat 7", tilt(make_wheat, stage=7)),
    ]
    for i in range(0, len(items), 8):
        print("wrote", _lineup("props_lineup_%d" % (i // 8 + 1), items[i : i + 8]))
    _closeups()


def _raised(obj, dz):
    obj.location.z += dz
    return obj


_PROP_TILES = ("bell", "bell_top", "bell_inner", "iron", "lantern", "bed_sheet", "bed_pillow", "bed_blanket_red",
               "bed_blanket_blue", "door_oak", "trapdoor", "composter_side", "compost", "blast_front_lit",
               "blast_front", "blast_side", "blast_top", "smith_top", "smith_side", "smith_front", "barrel_side",
               "barrel_top", "carto_top", "carto_side", "book", "emerald")

if __name__ == "__main__":
    _selftest()
