"""Access to the real Minecraft game files under assets/mc: textures, materials, block models, blockstates.

This is the only module that reads assets/mc. Nothing here is hand-drawn: textures are the game's PNGs (first
frame of animated strips), models are the game's JSON block models with parent chains resolved, and blockstates
are resolved the way the game does (variants / multipart, x/y rotation, uvlock).

Coordinates: model space is Minecraft's 0..16 block space (x east, y up, z south). `to_blender()` maps a model
point to Blender block-local units (x, 1 - z/16, y) so that Minecraft (x, y, z) -> Blender (x, -z, y).
UVs are kept in Minecraft's 0..16 texture units with v pointing DOWN (row 0 = top of the PNG).
"""
import json
import math
import os

import bpy
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC_DIR = os.path.join(ROOT, "assets", "mc")
ASSET_DIR = os.path.join(MC_DIR, "assets", "minecraft")
TEXTURE_DIR = os.path.join(ASSET_DIR, "textures")
MODEL_DIR = os.path.join(ASSET_DIR, "models")
BLOCKSTATE_DIR = os.path.join(ASSET_DIR, "blockstates")

DIRS = ("down", "up", "north", "south", "west", "east")
DIR_VEC = {"down": (0, -1, 0), "up": (0, 1, 0), "north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0),
           "east": (1, 0, 0)}
VEC_DIR = {v: k for k, v in DIR_VEC.items()}
OPPOSITE = {"down": "up", "up": "down", "north": "south", "south": "north", "west": "east", "east": "west"}
# Minecraft direction -> Blender unit vector (x, -z, y)
DIR_BLENDER = {"down": (0, 0, -1), "up": (0, 0, 1), "north": (0, 1, 0), "south": (0, -1, 0), "west": (-1, 0, 0),
               "east": (1, 0, 0)}
FULL_MASK = (1 << 256) - 1


# --------------------------------------------------------------------------------------------------
# biome tint (plains: temperature 0.8, downfall 0.4), sampled from the game's colormaps
# --------------------------------------------------------------------------------------------------

def _colormap(name, temperature=0.8, downfall=0.4, fallback=(145, 189, 89)):
    try:
        arr = texture_array("colormap/" + name)
        x = int((1.0 - temperature) * 255)
        y = int((1.0 - downfall * temperature) * 255)
        return tuple(int(c) for c in arr[y, x, :3])
    except Exception:
        return fallback


_TINTS = {}


def biome_tint(kind):
    """Plains biome colour as (r, g, b) 0-255 for kind 'grass' | 'foliage' | 'water' | 'birch' | 'spruce' | 'lily'."""
    if not _TINTS:
        _TINTS["grass"] = _colormap("grass", fallback=(145, 189, 89))
        _TINTS["foliage"] = _colormap("foliage", fallback=(119, 171, 47))
        _TINTS["water"] = (63, 118, 228)
        _TINTS["birch"] = (128, 167, 85)
        _TINTS["spruce"] = (97, 153, 97)
        _TINTS["lily"] = (32, 128, 48)
    return _TINTS[kind]


_GRASS_TINTED = {"grass_block", "short_grass", "tall_grass", "fern", "large_fern", "sugar_cane", "potted_fern"}
_FOLIAGE_TINTED = {"oak_leaves", "jungle_leaves", "acacia_leaves", "dark_oak_leaves", "mangrove_leaves", "vine"}
_WATER_TINTED = {"water", "water_cauldron", "bubble_column"}


def block_tint(block_id, tintindex):
    """The colour the game multiplies onto a face with this tintindex for this block (plains biome), or None."""
    if tintindex is None:
        return None
    if block_id in _GRASS_TINTED:
        return biome_tint("grass")
    if block_id in _FOLIAGE_TINTED:
        return biome_tint("foliage")
    if block_id in _WATER_TINTED:
        return biome_tint("water")
    if block_id == "birch_leaves":
        return biome_tint("birch")
    if block_id == "spruce_leaves":
        return biome_tint("spruce")
    if block_id == "lily_pad":
        return biome_tint("lily")
    return None


# --------------------------------------------------------------------------------------------------
# textures
# --------------------------------------------------------------------------------------------------

_ARRAYS = {}


def _norm(path):
    path = path.replace("minecraft:", "")
    if path.startswith("textures/"):
        path = path[len("textures/"):]
    if path.endswith(".png"):
        path = path[:-4]
    return path


def texture_path(path):
    """Absolute file path of a game texture, e.g. texture_path('block/oak_planks')."""
    return os.path.join(TEXTURE_DIR, _norm(path) + ".png")


def texture_array(path, frame=0):
    """Game texture as an HxWx4 uint8 array (row 0 = top). Animated strips (.mcmeta) return one frame (default first)."""
    path = _norm(path)
    key = (path, frame)
    if key not in _ARRAYS:
        from PIL import Image

        fp = texture_path(path)
        arr = np.array(Image.open(fp).convert("RGBA"), dtype=np.uint8)
        meta = fp + ".mcmeta"
        if os.path.exists(meta):
            try:
                with open(meta, encoding="utf-8") as f:
                    anim = json.load(f).get("animation")
            except Exception:
                anim = None
            if anim is not None:
                h, w = arr.shape[:2]
                side = min(w, h)
                fw = int(anim.get("width", side))
                fh = int(anim.get("height", side))
                n = max(1, h // fh)
                order = anim.get("frames")
                idx = frame % n
                if order:
                    f = order[frame % len(order)]
                    idx = f["index"] if isinstance(f, dict) else int(f)
                arr = arr[idx * fh:(idx + 1) * fh, 0:fw]
        arr.setflags(write=False)
        _ARRAYS[key] = arr
    return _ARRAYS[key]


def texture_meta(path):
    """The parsed .png.mcmeta of a game texture ({} when it has none), e.g. the villager 'hat' rule."""
    meta = texture_path(path) + ".mcmeta"
    try:
        with open(meta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def list_textures(folder):
    """Sorted names (no extension) of the PNGs in a texture folder, e.g. list_textures('entity/villager/profession')."""
    d = os.path.join(TEXTURE_DIR, _norm(folder))
    return sorted(f[:-4] for f in os.listdir(d) if f.endswith(".png")) if os.path.isdir(d) else []


def alpha_mode(path):
    """'OPAQUE' | 'CLIP' (only fully clear / fully solid pixels) | 'BLEND' (partial alpha) for a game texture."""
    a = texture_array(path)[..., 3]
    if a.min() == 255:
        return "OPAQUE"
    if np.all((a == 0) | (a == 255)):
        return "CLIP"
    return "BLEND"


def image_from_array(name, arr):
    """HxWx4 uint8 (sRGB, straight alpha, row 0 = top) -> packed in-memory bpy Image (reused if `name` exists)."""
    img = bpy.data.images.get(name)
    arr = np.asarray(arr, dtype=np.uint8)
    h, w = arr.shape[:2]
    if img is not None and tuple(img.size) == (w, h):
        return img
    if img is not None:
        bpy.data.images.remove(img)
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.alpha_mode = "STRAIGHT"
    img.pixels.foreach_set((np.flipud(arr).astype(np.float32) / 255.0).ravel())
    img.pack()
    return img


def _tinted(arr, tint):
    out = arr.astype(np.float32)
    out[..., 0] *= tint[0] / 255.0
    out[..., 1] *= tint[1] / 255.0
    out[..., 2] *= tint[2] / 255.0
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def composed_array(path, tint=None, overlay=None, overlay_tint=None):
    """Texture pixels with the game's tint multiplied in and an optional (tinted) overlay texture alpha-blended on top."""
    arr = texture_array(path)
    if tint is not None:
        arr = _tinted(arr, tint)
    if overlay is not None:
        top = texture_array(overlay)
        if overlay_tint is not None:
            top = _tinted(top, overlay_tint)
        a = top[..., 3:4].astype(np.float32) / 255.0
        out = arr.astype(np.float32)
        out[..., :3] = out[..., :3] * (1 - a) + top[..., :3].astype(np.float32) * a
        out[..., 3:4] = np.maximum(out[..., 3:4], top[..., 3:4].astype(np.float32))
        arr = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    return arr


def _hex(rgb):
    return "%02x%02x%02x" % tuple(int(c) for c in rgb[:3])


def _image_name(path, tint=None, overlay=None, overlay_tint=None):
    name = "mc/" + _norm(path)
    if tint is not None:
        name += "#" + _hex(tint)
    if overlay is not None:
        name += "+" + _norm(overlay).split("/")[-1]
        if overlay_tint is not None:
            name += "#" + _hex(overlay_tint)
    return name


def texture(path, tint=None, overlay=None, overlay_tint=None):
    """Game texture as a packed bpy Image, e.g. texture('block/oak_planks'); first frame of animated strips.

    tint=(r, g, b) multiplies the biome colour in; overlay composites a second (optionally tinted) texture on top.
    """
    name = _image_name(path, tint, overlay, overlay_tint)
    img = bpy.data.images.get(name)
    if img is not None:
        return img
    return image_from_array(name, composed_array(path, tint, overlay, overlay_tint))


def _emission_strength(nt, tex, emission, emit_above=None, emit_base=0.0):
    """Per-texel emission strength for a texture node: `emission` for texels brighter than `emit_above` (HSV value,
    None = every texel) and `emit_base` for the others. Returns a float, or the output socket of the node chain."""
    if emit_above is None:
        return float(emission)
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    sep.mode = "HSV"
    sep.location = (-250, -150)
    nt.links.new(tex.outputs["Color"], sep.inputs[0])
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = emit_above
    gt.location = (-100, -150)
    nt.links.new(sep.outputs[2], gt.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY_ADD"                       # glow texels: emission, the rest: emit_base
    mul.inputs[1].default_value = float(emission) - float(emit_base)
    mul.inputs[2].default_value = float(emit_base)
    mul.location = (50, -150)
    nt.links.new(gt.outputs[0], mul.inputs[0])
    return mul.outputs[0]


def _shade_up_thin_material(mname, img, alpha, emission=0.0, emit_above=None, emit_base=0.0):
    """Material for the two coincident faces of a zero-thickness "shade_direction_override": "up" element (cross
    plants, crops, vines, the chain of a hanging lantern): together they are lit exactly like an UP-FACING surface
    from every side, as in the game.

    The mesh gives these faces up-pointing normals (MeshBuilder.mesh(up_normals=True)). A face hit from its front
    reflects the light of its own half-space weighted by the up normal and lets the ray pass on to its twin
    (Diffuse + Transparent); the twin, hit from behind, adds the light of the other half-space (Translucent, whose
    flipped default normal weights it by 'up' too) and ends the ray. Shadow rays are stopped by the back-facing face,
    so plants still cast their cut-out shadows. Without this a backlit plant renders black: its far face shadows it.
    A glow (emission / emit_above / emit_base, see material()) is added once, on the front face.
    """
    mat = bpy.data.materials.new(mname)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    tex = N("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    tex.extension = "REPEAT"
    geo = N("ShaderNodeNewGeometry")
    diff = N("ShaderNodeBsdfDiffuse")
    trans = N("ShaderNodeBsdfTranslucent")
    clear = N("ShaderNodeBsdfTransparent")
    L(tex.outputs["Color"], diff.inputs["Color"])
    L(tex.outputs["Color"], trans.inputs["Color"])
    front = N("ShaderNodeAddShader")
    L(diff.outputs[0], front.inputs[0])
    L(clear.outputs[0], front.inputs[1])
    if emission > 0 or emit_base > 0:
        em = N("ShaderNodeEmission")
        L(tex.outputs["Color"], em.inputs["Color"])
        strength = _emission_strength(nt, tex, emission, emit_above, emit_base)
        if isinstance(strength, float):
            em.inputs["Strength"].default_value = strength
        else:
            L(strength, em.inputs["Strength"])
        glow = N("ShaderNodeAddShader")
        L(front.outputs[0], glow.inputs[0])
        L(em.outputs[0], glow.inputs[1])
        front = glow
    side = N("ShaderNodeMixShader")
    L(geo.outputs["Backfacing"], side.inputs[0])
    L(front.outputs[0], side.inputs[1])
    L(trans.outputs[0], side.inputs[2])
    surface = side.outputs[0]
    if alpha in ("CLIP", "BLEND"):
        gt = N("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = 0.5
        L(tex.outputs["Alpha"], gt.inputs[0])
        cut = N("ShaderNodeMixShader")
        L(gt.outputs[0], cut.inputs[0])
        L(clear.outputs[0], cut.inputs[1])
        L(surface, cut.inputs[2])
        surface = cut.outputs[0]
    L(surface, out.inputs["Surface"])
    return mat


def material(path, tint=None, alpha=None, emission=0.0, overlay=None, overlay_tint=None, emit_above=None,
             roughness=0.9, specular=0.08, name=None, shade=None, emit_base=0.0):
    """Cached Principled material showing a game texture with Closest (hard pixel) filtering.

    tint: biome colour multiplied in. alpha: 'OPAQUE' | 'CLIP' | 'BLEND' (None = decide from the texture's alpha).
    emission: glow strength using the texture colour; emit_above=v limits the glow to pixels brighter than v (0..1),
    e.g. only the flame of the torch texture, and emit_base is then the (much weaker) self-illumination of the other
    texels: the game draws a torch or lantern block at light level 15, while here its own point light sits INSIDE
    the model and cannot reach its faces. shade='up_thin' builds the two-sided "lit like an up-facing surface"
    variant for zero-thickness shade_direction_override elements (see _shade_up_thin_material).
    """
    path = _norm(path)
    if alpha is None:
        alpha = alpha_mode(path)
    mname = name or _image_name(path, tint, overlay, overlay_tint)
    if name is None:
        if alpha != alpha_mode(path):
            mname += "~" + alpha.lower()
        if emission > 0:
            mname += "*e%g" % emission
            if emit_above is not None:
                mname += ">%g" % emit_above
                if emit_base > 0:
                    mname += "+%g" % emit_base
        if shade == "up_thin":
            mname += "^up"
    mat = bpy.data.materials.get(mname)
    if mat is not None:
        return mat
    img = texture(path, tint, overlay, overlay_tint)
    if shade == "up_thin":
        mat = _shade_up_thin_material(mname, img, alpha, emission, emit_above, emit_base)
        mat["mc_texture"] = path
        mat["mc_alpha"] = alpha
        mat["mc_shade"] = shade
        return mat
    mat = bpy.data.materials.new(mname)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    tex.extension = "REPEAT"
    tex.location = (-500, 200)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Specular IOR Level"].default_value = specular
    if emission > 0:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        strength = _emission_strength(nt, tex, emission, emit_above, emit_base)
        if isinstance(strength, float):
            bsdf.inputs["Emission Strength"].default_value = strength
        else:
            nt.links.new(strength, bsdf.inputs["Emission Strength"])
    if alpha == "CLIP":
        gt = nt.nodes.new("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = 0.5
        gt.location = (-250, 0)
        nt.links.new(tex.outputs["Alpha"], gt.inputs[0])
        nt.links.new(gt.outputs[0], bsdf.inputs["Alpha"])
    elif alpha == "BLEND":
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    mat["mc_texture"] = path
    mat["mc_alpha"] = alpha
    return mat


# --------------------------------------------------------------------------------------------------
# block models
# --------------------------------------------------------------------------------------------------

class Face:
    """One face of a model element: resolved texture path, uv rect (u1, v1, u2, v2), rotation, cullface, tintindex,
    and `shade`: the element's "shade_direction_override" (None | 'up' | 'down' | 'north' ...)."""
    __slots__ = ("direction", "texture", "uv", "rotation", "cullface", "tintindex", "overlay", "shade")

    def __init__(self, direction, texture, uv, rotation=0, cullface=None, tintindex=None, overlay=None, shade=None):
        self.direction, self.texture, self.uv, self.rotation = direction, texture, uv, rotation
        self.cullface, self.tintindex, self.overlay, self.shade = cullface, tintindex, overlay, shade


class Element:
    """One box of a block model (from/to in 0..16 model space, optional rotation, faces by direction)."""
    __slots__ = ("frm", "to", "rotation", "faces")

    def __init__(self, frm, to, rotation, faces):
        self.frm, self.to, self.rotation, self.faces = frm, to, rotation, faces


class Model:
    """A block model with its parent chain merged and texture variables resolved."""
    __slots__ = ("name", "elements", "textures")

    def __init__(self, name, elements, textures):
        self.name, self.elements, self.textures = name, elements, textures


_RAW = {}
_MODELS = {}


def _model_name(name):
    name = name.replace("minecraft:", "")
    return name


def _raw_model(name):
    name = _model_name(name)
    if name not in _RAW:
        with open(os.path.join(MODEL_DIR, name + ".json")) as f:
            _RAW[name] = json.load(f)
    return _RAW[name]


def default_uv(direction, frm, to):
    """The uv rect the game derives from an element's from/to when a face has no explicit 'uv'."""
    x0, y0, z0 = frm
    x1, y1, z1 = to
    if direction == "down":
        return (x0, 16 - z1, x1, 16 - z0)
    if direction == "up":
        return (x0, z0, x1, z1)
    if direction == "north":
        return (16 - x1, 16 - y1, 16 - x0, 16 - y0)
    if direction == "south":
        return (x0, 16 - y1, x1, 16 - y0)
    if direction == "west":
        return (z0, 16 - y1, z1, 16 - y0)
    return (16 - z1, 16 - y1, 16 - z0, 16 - y0)


def _resolve_texture(value, textures, depth=0):
    if isinstance(value, dict):
        value = value.get("sprite")
    if value is None or depth > 16:
        return None
    if value.startswith("#"):
        return _resolve_texture(textures.get(value[1:]), textures, depth + 1)
    return _norm(value)


def load_model(name):
    """Resolved block/item model, e.g. load_model('block/oak_stairs'): parents merged, '#variables' resolved,
    every face carrying texture path, uv rect, texture rotation, cullface and tintindex."""
    name = _model_name(name)
    if name in _MODELS:
        return _MODELS[name]
    chain = []
    cur = name
    while cur:
        raw = _raw_model(cur)
        chain.append(raw)
        cur = raw.get("parent")
        if cur and cur.replace("minecraft:", "").startswith("builtin/"):
            cur = None
    textures = {}
    for raw in reversed(chain):
        textures.update(raw.get("textures", {}))
    raw_elements = next((raw["elements"] for raw in chain if "elements" in raw), [])
    elements = []
    for e in raw_elements:
        frm = tuple(float(c) for c in e["from"])
        to = tuple(float(c) for c in e["to"])
        rot = e.get("rotation")
        if rot is not None:
            if "axis" in rot:
                rot = {"origin": tuple(float(c) for c in rot.get("origin", (8, 8, 8))), "axis": rot["axis"],
                       "angle": float(rot.get("angle", 0)), "rescale": bool(rot.get("rescale", False))}
                if rot["angle"] == 0:
                    rot = None
            else:
                rot = None
        faces = {}
        shade = e.get("shade_direction_override")     # 26.x: the game lights these faces as if they faced this way
        for d, f in e.get("faces", {}).items():
            tex = _resolve_texture(f.get("texture"), textures)
            if tex is None:
                continue
            uv = tuple(float(c) for c in f["uv"]) if "uv" in f else default_uv(d, frm, to)
            faces[d] = Face(d, tex, uv, int(f.get("rotation", 0)) % 360, f.get("cullface"), f.get("tintindex"),
                            shade=f.get("shade_direction_override", shade))
        elements.append(Element(frm, to, rot, faces))
    # an element that exactly repeats an earlier box with see-through textures (grass_block's tinted side overlay)
    # is folded into the earlier face as an overlay, so one opaque quad carries the composited pixels
    merged = []
    for e in elements:
        base = next((b for b in merged if b.frm == e.frm and b.to == e.to and b.rotation == e.rotation), None)
        if base is not None:
            for d in list(e.faces):
                f, bf = e.faces[d], base.faces.get(d)
                if bf is not None and bf.overlay is None and bf.uv == f.uv and bf.rotation == f.rotation \
                        and alpha_mode(f.texture) != "OPAQUE":
                    bf.overlay = (f.texture, f.tintindex)
                    del e.faces[d]
            if not e.faces:
                continue
        merged.append(e)
    model = Model(name, merged, {k: _resolve_texture(v, textures) for k, v in textures.items()})
    _MODELS[name] = model
    return model


# --------------------------------------------------------------------------------------------------
# blockstates
# --------------------------------------------------------------------------------------------------

class ModelPart:
    """One model of a block state with its blockstate rotation: model name, x, y (degrees), uvlock."""
    __slots__ = ("model", "x", "y", "uvlock")

    def __init__(self, model, x=0, y=0, uvlock=False):
        self.model, self.x, self.y, self.uvlock = model, x, y, uvlock

    def key(self):
        """Hashable identity of this part."""
        return (self.model, self.x, self.y, self.uvlock)

    def __repr__(self):
        return "ModelPart(%s, x=%d, y=%d, uvlock=%s)" % self.key()


DEFAULT_PROPS = {
    "waterlogged": "false", "powered": "false", "open": "false", "lit": "false", "snowy": "false", "half": "bottom",
    "shape": "straight", "type": "bottom", "axis": "y", "facing": "north", "hinge": "left", "part": "foot",
    "occupied": "false", "north": "false", "east": "false", "south": "false", "west": "false", "up": "true",
    "age": "0", "level": "0", "moisture": "0", "attachment": "floor", "in_wall": "false", "hanging": "false",
    "has_book": "false", "face": "wall", "persistent": "false", "distance": "7", "has_bottle_0": "false",
    "has_bottle_1": "false", "has_bottle_2": "false", "extended": "false", "layers": "1", "rotation": "0",
}
_BLOCK_DEFAULTS = {
    "door": {"half": "lower"}, "tall_grass": {"half": "lower"}, "wall": {"north": "none", "east": "none",
                                                                           "south": "none", "west": "none"},
    "chest": {"type": "single"},
}

_STATES = {}


def _blockstate(block_id):
    block_id = block_id.replace("minecraft:", "")
    if block_id not in _STATES:
        with open(os.path.join(BLOCKSTATE_DIR, block_id + ".json")) as f:
            _STATES[block_id] = json.load(f)
    return _STATES[block_id]


def has_blockstate(block_id):
    """True if the game has a blockstate file for this block id."""
    return os.path.exists(os.path.join(BLOCKSTATE_DIR, block_id.replace("minecraft:", "") + ".json"))


def full_props(block_id, props):
    """props with the game's usual defaults filled in for anything missing (all values as strings)."""
    out = dict(DEFAULT_PROPS)
    for suffix, extra in _BLOCK_DEFAULTS.items():
        if block_id.endswith(suffix):
            out.update(extra)
    if props:
        out.update({k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in props.items()})
    return out


def _when(cond, props):
    if "OR" in cond:
        return any(_when(c, props) for c in cond["OR"])
    if "AND" in cond:
        return all(_when(c, props) for c in cond["AND"])
    for k, want in cond.items():
        have = props.get(k)
        if have is None or have not in str(want).split("|"):
            return False
    return True


def _apply(entry, seed):
    if isinstance(entry, list):
        total = sum(int(e.get("weight", 1)) for e in entry)
        pick = seed % total
        for e in entry:
            pick -= int(e.get("weight", 1))
            if pick < 0:
                entry = e
                break
    return ModelPart(_model_name(entry["model"]), int(entry.get("x", 0)) % 360, int(entry.get("y", 0)) % 360,
                     bool(entry.get("uvlock", False)))


def variant_count(block_id, props=None):
    """How many random variants the matching blockstate entry offers (1 if it is not a list)."""
    state = _blockstate(block_id)
    if "variants" not in state:
        return 1
    entry = _match_variant(state["variants"], full_props(block_id, props))
    return sum(int(e.get("weight", 1)) for e in entry) if isinstance(entry, list) else 1


def _match_variant(variants, props):
    for key, entry in variants.items():
        if key == "" or all(props.get(k) == v for k, v in (kv.split("=") for kv in key.split(","))):
            return entry
    return next(iter(variants.values()))


def resolve_blockstate(block_id, props=None, seed=0):
    """Models the game draws for a block state: handles 'variants' (list entries picked by `seed`, e.g. a position
    hash) and 'multipart' (when / AND / OR / 'a|b'), each with its x / y rotation and uvlock flag."""
    state = _blockstate(block_id)
    props = full_props(block_id, props)
    if "variants" in state:
        return [_apply(_match_variant(state["variants"], props), seed)]
    parts = []
    for case in state.get("multipart", []):
        if "when" not in case or _when(case["when"], props):
            parts.append(_apply(case["apply"], seed))
    return parts


# --------------------------------------------------------------------------------------------------
# baking: model parts -> quads in block space
# --------------------------------------------------------------------------------------------------

class Quad:
    """A baked face: 4 points in 0..16 block space (Minecraft axes), 4 uvs (0..16, v down), texture, tintindex,
    overlay (texture, tintindex) or None, `cull` (direction whose neighbour can hide it) and `facing`."""
    __slots__ = ("pts", "uvs", "texture", "tintindex", "overlay", "cull", "facing", "mask", "thin", "shade")

    def __init__(self, pts, uvs, texture, tintindex=None, overlay=None, cull=None, facing=None, thin=False,
                 shade=None):
        self.pts, self.uvs, self.texture, self.tintindex, self.overlay = pts, uvs, texture, tintindex, overlay
        self.cull, self.facing, self.thin = cull, facing, thin
        self.shade = shade      # None | 'up' (lit like an up-facing surface) | 'up_thin' (same, zero-thickness twin)
        self.mask = _rect_mask(pts, cull, outward=True) if cull else 0


_QUARTER = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}


def rotate_point(p, x=0, y=0, center=(8.0, 8.0, 8.0)):
    """Apply a blockstate rotation (x then y, degrees, multiples of 90) to a point about the block centre."""
    px, py, pz = p[0] - center[0], p[1] - center[1], p[2] - center[2]
    if x:
        c, s = _QUARTER[x % 360]
        py, pz = py * c + pz * s, -py * s + pz * c
    if y:
        c, s = _QUARTER[y % 360]
        px, pz = px * c - pz * s, px * s + pz * c
    return (px + center[0], py + center[1], pz + center[2])


def rotate_dir(d, x=0, y=0):
    """Direction name after a blockstate rotation."""
    if d is None:
        return None
    v = rotate_point(DIR_VEC[d], x, y, center=(0, 0, 0))
    return VEC_DIR[(int(round(v[0])), int(round(v[1])), int(round(v[2])))]


def _element_rotate(p, rot):
    ox, oy, oz = rot["origin"]
    x, y, z = p[0] - ox, p[1] - oy, p[2] - oz
    a = math.radians(rot["angle"])
    c, s = math.cos(a), math.sin(a)
    k = 1.0
    if rot["rescale"]:
        k = 1.0 / math.cos(math.radians(22.5)) if abs(abs(rot["angle"]) - 22.5) < 1e-6 else math.sqrt(2.0)
    if rot["axis"] == "x":
        y, z = (y * c - z * s) * k, (y * s + z * c) * k
    elif rot["axis"] == "y":
        x, z = (x * c + z * s) * k, (-x * s + z * c) * k
    else:
        x, y = (x * c - y * s) * k, (x * s + y * c) * k
    return (x + ox, y + oy, z + oz)


def _face_points(d, frm, to):
    x0, y0, z0 = frm
    x1, y1, z1 = to
    if d == "down":
        return [(x0, y0, z1), (x0, y0, z0), (x1, y0, z0), (x1, y0, z1)]
    if d == "up":
        return [(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)]
    if d == "north":
        return [(x1, y1, z0), (x1, y0, z0), (x0, y0, z0), (x0, y1, z0)]
    if d == "south":
        return [(x0, y1, z1), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1)]
    if d == "west":
        return [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)]
    return [(x1, y1, z1), (x1, y0, z1), (x1, y0, z0), (x1, y1, z0)]


def _proj(d, p):
    x, y, z = p
    if d == "down":
        return (x, 16 - z)
    if d == "up":
        return (x, z)
    if d == "north":
        return (16 - x, 16 - y)
    if d == "south":
        return (x, 16 - y)
    if d == "west":
        return (z, 16 - y)
    return (16 - z, 16 - y)


def _unproj(d, uv):
    u, v = uv
    if d == "down":
        return (u, 8.0, 16 - v)
    if d == "up":
        return (u, 8.0, v)
    if d == "north":
        return (16 - u, 16 - v, 8.0)
    if d == "south":
        return (u, 16 - v, 8.0)
    if d == "west":
        return (8.0, 16 - v, u)
    return (8.0, 16 - v, 16 - u)


def _plane_axes(d):
    """Indices of the two block-space axes spanning the cell boundary in direction d (shared by both neighbours)."""
    if d in ("west", "east"):
        return (2, 1)
    if d in ("down", "up"):
        return (0, 2)
    return (0, 1)


def _rect_mask(pts, d, outward):
    """256-bit mask of the 16x16 boundary cells a quad covers when projected along direction d."""
    a, b = _plane_axes(d)
    a0, a1 = min(p[a] for p in pts), max(p[a] for p in pts)
    b0, b1 = min(p[b] for p in pts), max(p[b] for p in pts)
    e = 1e-4
    if outward:
        ia0, ia1 = int(math.floor(a0 + e)), int(math.ceil(a1 - e))
        ib0, ib1 = int(math.floor(b0 + e)), int(math.ceil(b1 - e))
    else:
        ia0, ia1 = int(math.ceil(a0 - e)), int(math.floor(a1 + e))
        ib0, ib1 = int(math.ceil(b0 - e)), int(math.floor(b1 + e))
    ia0, ia1, ib0, ib1 = max(ia0, 0), min(ia1, 16), max(ib0, 0), min(ib1, 16)
    if ia1 <= ia0 or ib1 <= ib0:
        return 0
    row = ((1 << (ia1 - ia0)) - 1) << ia0
    mask = 0
    for r in range(ib0, ib1):
        mask |= row << (16 * r)
    return mask


THIN_EPS = 0.02  # model pixels; separates the two sides of zero-thickness elements (cross plants, lantern chain)

_PART_CACHE = {}


def bake_part(part):
    """All faces of one ModelPart as Quads in block space, with the blockstate rotation and uvlock applied."""
    key = part.key()
    if key in _PART_CACHE:
        return _PART_CACHE[key]
    model = load_model(part.model)
    quads = []
    for e in model.elements:
        size = [e.to[i] - e.frm[i] for i in range(3)]
        for d, f in e.faces.items():
            axis = 1 if d in ("down", "up") else (2 if d in ("north", "south") else 0)
            thin = abs(size[axis]) < 1e-6 and OPPOSITE[d] in e.faces
            pts = _face_points(d, e.frm, e.to)
            if thin:
                n = DIR_VEC[d]
                pts = [(p[0] + n[0] * THIN_EPS, p[1] + n[1] * THIN_EPS, p[2] + n[2] * THIN_EPS) for p in pts]
            u1, v1, u2, v2 = f.uv
            corners = [(u1, v1), (u1, v2), (u2, v2), (u2, v1)]
            r = (f.rotation // 90) % 4
            uvs = [corners[(i + r) % 4] for i in range(4)]
            if e.rotation is not None:
                pts = [_element_rotate(p, e.rotation) for p in pts]
            facing = d
            if part.x or part.y:
                facing = rotate_dir(d, part.x, part.y)
                if part.uvlock:
                    uvs = [_proj(facing, rotate_point(_unproj(d, uv), part.x, part.y)) for uv in uvs]
                pts = [rotate_point(p, part.x, part.y) for p in pts]
            cull = rotate_dir(f.cullface, part.x, part.y) if f.cullface in DIR_VEC else None
            shade = None
            if f.shade == "up":
                shade = "up_thin" if thin else "up"
            quads.append(Quad(pts, uvs, f.texture, f.tintindex, f.overlay, cull,
                              facing if e.rotation is None else None, thin, shade))
    _PART_CACHE[key] = quads
    return quads


def bake_block(block_id, props=None, seed=0):
    """Every Quad of a block state (all of its blockstate models), ready to be offset to a block position."""
    quads = []
    for part in resolve_blockstate(block_id, props, seed):
        quads.extend(bake_part(part))
    return quads


def cover_masks(quads):
    """For each direction, the 256-bit mask of the cell boundary that opaque faces of these quads fully cover."""
    cover = dict.fromkeys(DIRS, 0)
    for q in quads:
        d = q.facing
        if d is None or q.thin:
            continue
        axis = 1 if d in ("down", "up") else (2 if d in ("north", "south") else 0)
        want = 16.0 if d in ("up", "south", "east") else 0.0
        if any(abs(p[axis] - want) > 1e-4 for p in q.pts):
            continue
        if alpha_mode(q.texture) != "OPAQUE":
            continue
        cover[d] |= _rect_mask(q.pts, d, outward=False)
    return cover


def to_blender(p):
    """Model-space point (0..16, Minecraft axes) -> Blender block-local units (x east, y north, z up)."""
    return (p[0] / 16.0, 1.0 - p[2] / 16.0, p[1] / 16.0)


# --------------------------------------------------------------------------------------------------
# entity-style boxes (bell body, chest): exact vanilla box unwrap
# --------------------------------------------------------------------------------------------------

def entity_box(x, y, z, w, h, d, u, v, tex_w, tex_h, texture_path_, flip_y=False, height=None):
    """Quads of a vanilla ModelPart cube: min corner (x, y, z), size (w, h, d) in pixels, texture offset (u, v) on a
    tex_w x tex_h sheet, using the game's standard box unwrap. Points are in the same pixel space as the arguments.

    flip_y=True mirrors the box in Y about `height`/2 (entities are modelled Y-down; block entities like the bell
    and chest are not flipped).
    """
    x2, y2, z2 = x + w, y + h, z + d
    p = {1: (x, y, z), 2: (x2, y, z), 3: (x2, y2, z), 4: (x, y2, z), 5: (x, y, z2), 6: (x2, y, z2), 7: (x2, y2, z2),
         8: (x, y2, z2)}
    l_, m, n, o = u, u + d, u + d + w, u + d + w + w
    pp, q = u + d + w + d, u + d + w + d + w
    r, s, t = v, v + d, v + d + h
    polys = [
        ((6, 5, 1, 2), (m, r, n, s), "down"),
        ((3, 4, 8, 7), (n, s, o, r), "up"),
        ((1, 5, 8, 4), (l_, s, m, t), "west"),
        ((2, 1, 4, 3), (m, s, n, t), "north"),
        ((6, 2, 3, 7), (n, s, pp, t), "east"),
        ((5, 6, 7, 8), (pp, s, q, t), "south"),
    ]
    su, sv = 16.0 / tex_w, 16.0 / tex_h
    quads = []
    for idx, (u1, v1, u2, v2), facing in polys:
        pts = [p[i] for i in idx]
        uvs = [(u2 * su, v1 * sv), (u1 * su, v1 * sv), (u1 * su, v2 * sv), (u2 * su, v2 * sv)]
        if flip_y:
            pts = [(a, height - b, c) for a, b, c in pts]
            facing = {"down": "up", "up": "down"}.get(facing, facing)
        else:
            pts, uvs = pts[::-1], uvs[::-1]  # the game's winding is for Y-down space; keep normals outward
        quads.append(Quad(pts, uvs, _norm(texture_path_), facing=facing))
    return quads


def bell_body_quads():
    """The swinging bell body exactly as the game's BellModel: 6x7x6 body (texture 0,0) and 8x2x8 lip (0,13) on the
    32x32 entity/bell/bell_body.png, in block space (the body hangs from y=13, pivot at (8, 12, 8))."""
    tex = "entity/bell/bell_body"
    return entity_box(5, 6, 5, 6, 7, 6, 0, 0, 32, 32, tex) + entity_box(4, 4, 4, 8, 2, 8, 0, 13, 32, 32, tex)


BELL_PIVOT = (8.0, 12.0, 8.0)  # model-space pivot of the bell body (vanilla PartPose.offset(8, 12, 8))


def chest_quads(facing="north"):
    """A closed single chest exactly as the game's chest model (entity/chest/normal.png, 64x64), lock toward `facing`."""
    tex = "entity/chest/normal"
    quads = entity_box(1, 0, 1, 14, 10, 14, 0, 19, 64, 64, tex)
    quads += entity_box(1, 9, 1, 14, 5, 14, 0, 0, 64, 64, tex)
    quads += entity_box(7, 7, 15, 2, 4, 1, 0, 0, 64, 64, tex)
    y = {"south": 0, "west": 90, "north": 180, "east": 270}.get(facing, 180)
    if y:
        for q in quads:
            q.pts = [rotate_point(p, 0, y) for p in q.pts]
            q.facing = rotate_dir(q.facing, 0, y)
    return quads


# --------------------------------------------------------------------------------------------------
# mesh helpers
# --------------------------------------------------------------------------------------------------

class MeshBuilder:
    """Collects quads per material and turns them into mesh objects (4 own vertices per quad, one UV layer)."""

    def __init__(self):
        self.verts = {}
        self.uvs = {}

    def add(self, key, pts, uvs):
        """Add one quad: 4 Blender-space points and 4 uvs in 0..16 (v down) under material key `key`."""
        self.verts.setdefault(key, []).extend(pts)
        self.uvs.setdefault(key, []).extend(uvs)

    def count(self, key=None):
        """Number of quads (for one key or in total)."""
        if key is not None:
            return len(self.verts.get(key, ())) // 4
        return sum(len(v) for v in self.verts.values()) // 4

    def mesh(self, key, name, up_normals=None):
        """Build the bpy Mesh for one key. up_normals: True (every quad) or a per-quad list of bools: those quads get
        custom normals pointing straight up, which is how "shade_direction_override": "up" is rendered (the game
        lights such faces as if they faced the sky; Cycles then weights their light by the up direction)."""
        co = np.asarray(self.verts[key], dtype=np.float32)
        uv = np.asarray(self.uvs[key], dtype=np.float32)
        n = len(co) // 4
        me = bpy.data.meshes.new(name)
        me.vertices.add(n * 4)
        me.loops.add(n * 4)
        me.polygons.add(n)
        me.vertices.foreach_set("co", co.ravel())
        me.loops.foreach_set("vertex_index", np.arange(n * 4, dtype=np.int32))
        me.polygons.foreach_set("loop_start", np.arange(0, n * 4, 4, dtype=np.int32))
        me.polygons.foreach_set("loop_total", np.full(n, 4, dtype=np.int32))
        layer = me.uv_layers.new(name="UVMap")
        uv2 = np.empty_like(uv)
        uv2[:, 0] = uv[:, 0] / 16.0
        uv2[:, 1] = 1.0 - uv[:, 1] / 16.0
        layer.data.foreach_set("uv", uv2.ravel())
        me.update()
        me.validate()
        if up_normals is True or (up_normals is not None and any(up_normals)):
            flags = np.ones(n, dtype=bool) if up_normals is True else np.asarray(up_normals, dtype=bool)
            if len(me.polygons) == n:                      # (validate() dropped nothing)
                normals = np.zeros((n, 3), dtype=np.float32)
                me.polygons.foreach_get("normal", normals.ravel())
                normals[flags] = (0.0, 0.0, 1.0)
                me.polygons.foreach_set("use_smooth", flags.tolist())
                me.normals_split_custom_set(np.repeat(normals, 4, axis=0).tolist())
                me.update()
        return me


def quads_object(name, quads, material_for, collection=None, origin=(0.0, 0.0, 0.0)):
    """One mesh object (a material slot per texture) from baked Quads; `origin` is in model pixels (0..16 space) and
    becomes the object's origin. material_for(quad) -> Material."""
    mb = MeshBuilder()
    mats = {}
    ups = {}
    for q in quads:
        mat = material_for(q)
        mats[mat.name] = mat
        pts = [((p[0] - origin[0]) / 16.0, -(p[2] - origin[2]) / 16.0, (p[1] - origin[1]) / 16.0) for p in q.pts]
        mb.add(mat.name, pts, q.uvs)
        ups.setdefault(mat.name, []).append(getattr(q, "shade", None) is not None)
    names = sorted(mats)
    co, uv, mat_index, up = [], [], [], []
    for i, n in enumerate(names):
        co.extend(mb.verts[n])
        uv.extend(mb.uvs[n])
        mat_index.extend([i] * (len(mb.verts[n]) // 4))
        up.extend(ups[n])
    one = MeshBuilder()
    one.verts["all"], one.uvs["all"] = co, uv
    me = one.mesh("all", name, up_normals=up)
    for n in names:
        me.materials.append(mats[n])
    me.polygons.foreach_set("material_index", np.asarray(mat_index, dtype=np.int32))
    me.update()
    ob = bpy.data.objects.new(name, me)
    if collection is not None:
        collection.objects.link(ob)
    return ob


# --------------------------------------------------------------------------------------------------
# items
# --------------------------------------------------------------------------------------------------

def item_texture(item_id):
    """Texture path of an item's flat sprite (layer0 of its generated model), e.g. 'emerald' -> 'item/emerald'."""
    item_id = item_id.replace("minecraft:", "")
    model = None
    fp = os.path.join(ASSET_DIR, "items", item_id + ".json")
    if os.path.exists(fp):
        def find(node):
            if isinstance(node, dict):
                if isinstance(node.get("model"), str):
                    return node["model"]
                for v in node.values():
                    r = find(v)
                    if r:
                        return r
            elif isinstance(node, list):
                for v in node:
                    r = find(v)
                    if r:
                        return r
            return None
        with open(fp, encoding="utf-8") as f:
            model = find(json.load(f))
    model = _model_name(model or ("item/" + item_id))
    try:
        tex = load_model(model).textures.get("layer0")
    except Exception:
        tex = None
    return tex or ("item/" + item_id)


def item_object(item_id, collection=None, thickness=1.0):
    """Held item as the game draws it: the item texture extruded one pixel thick. 16 px = 1 unit, origin at the
    sprite centre, sprite in the local XZ plane (front faces -Y)."""
    tex = item_texture(item_id)
    arr = texture_array(tex)
    h, w = arr.shape[:2]
    solid = arr[..., 3] >= 128
    mb = MeshBuilder()
    s = 1.0 / 16.0
    t = thickness * s / 2.0
    su, sv = 16.0 / w, 16.0 / h

    def px_uv(c, r):
        e = 0.02
        return [((c + e) * su, (r + e) * sv), ((c + e) * su, (r + 1 - e) * sv), ((c + 1 - e) * su, (r + 1 - e) * sv),
                ((c + 1 - e) * su, (r + e) * sv)]

    for r in range(h):
        for c in range(w):
            if not solid[r, c]:
                continue
            x0, x1 = (c - w / 2.0) * s, (c + 1 - w / 2.0) * s
            z1, z0 = (h / 2.0 - r) * s, (h / 2.0 - r - 1) * s
            uv = px_uv(c, r)
            mb.add("m", [(x0, -t, z1), (x0, -t, z0), (x1, -t, z0), (x1, -t, z1)], uv)
            mb.add("m", [(x1, t, z1), (x1, t, z0), (x0, t, z0), (x0, t, z1)], [uv[3], uv[2], uv[1], uv[0]])
            if c == 0 or not solid[r, c - 1]:
                mb.add("m", [(x0, t, z1), (x0, t, z0), (x0, -t, z0), (x0, -t, z1)], uv)
            if c == w - 1 or not solid[r, c + 1]:
                mb.add("m", [(x1, -t, z1), (x1, -t, z0), (x1, t, z0), (x1, t, z1)], uv)
            if r == 0 or not solid[r - 1, c]:
                mb.add("m", [(x0, t, z1), (x0, -t, z1), (x1, -t, z1), (x1, t, z1)], uv)
            if r == h - 1 or not solid[r + 1, c]:
                mb.add("m", [(x0, -t, z0), (x0, t, z0), (x1, t, z0), (x1, -t, z0)], uv)
    me = mb.mesh("m", "item_" + item_id)
    me.materials.append(material(tex, alpha="OPAQUE"))
    ob = bpy.data.objects.new("item_" + item_id, me)
    if collection is not None:
        collection.objects.link(ob)
    return ob


if __name__ == "__main__":
    # asset sanity check without rendering: resolve every block used by the plains village templates
    from . import structures

    seen = set()
    for n in structures.list_templates("village/plains"):
        if "zombie" in n:
            continue
        for x, y, z, b, p in structures.load_template(n).blocks:
            seen.add((b, tuple(sorted(p.items()))))
    bad = 0
    for b, p in sorted(seen):
        if not has_blockstate(b):
            print("no blockstate:", b)
            bad += 1
            continue
        try:
            quads = bake_block(b, dict(p))
            if not quads and b not in ("water", "lava", "chest"):
                print("empty:", b, dict(p))
        except Exception as ex:  # noqa
            print("FAILED", b, dict(p), repr(ex))
            bad += 1
    print("states checked:", len(seen), "problems:", bad)
    print("grass", biome_tint("grass"), "foliage", biome_tint("foliage"))
    print("emerald texture:", item_texture("emerald"))
