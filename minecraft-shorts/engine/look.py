"""Lighting, sky and final-render look for the films (owned by role LOOK).

    look.setup_render(scene)                      # Cycles CPU, denoise, motion blur, colour management
    sky = look.set_time(scene, "golden", sun_azimuth=200)   # world gradient, real sun/moon, stars, clouds, haze
    look.setup_compositor(scene, grade="warm")    # haze mix, bloom, grade, vignette (scene.compositing_node_group)

Sky pieces come from the game files: the sun and moon are `textures/environment/celestial/sun.png` and
`moon/full_moon.png` drawn additively on a far quad (opposite each other, as in the game), the clouds are the
game's `textures/environment/clouds.png` bitmap extruded into 12x12x4-block slabs, and the stars are generated
with the game's own star algorithm (1500 stars, seed 10842). Only the sky colours and the light are art-directed.

Azimuth convention: degrees, counter-clockwise seen from above, 0 = +X (Minecraft east), 90 = +Y (Minecraft
north), 180 = -X (west), 270 = -Y (south). `sun_azimuth` is where the KEY body sits in the sky: the sun for
'day' / 'golden' / 'dusk', the moon for 'night' (the other body is opposite, below the horizon, and hidden).

Colour pipeline: the scene is rendered and composited in scene-linear, shown through the plain 'Standard' sRGB
view, and the only tone mapping is the highlight shoulder at the end of setup_compositor() (hue-preserving roll-off
above 0.76, Khronos PBR Neutral's, WITHOUT that transform's black offset and with a slower drift to white). Below the shoulder a pixel is
texture x light and nothing else, so the game's palette survives; the light colours are kept pale and the sky FILL
almost neutral for the same reason (the visible sky keeps its colour: camera rays see another map than the fill).

Practical numbers under these presets (exposure 0):
- a torch / lantern POINT light of 150-300 W is a warm pool about 4-6 blocks wide at dusk and night and is
  invisible by day; give glowing texels emission strength 2-4.5 (engine.blocks.EMISSIVE): the bloom (threshold
  1.0) catches them and only the flame's core reaches the highlight shoulder, so the glow stays the game's orange;
- the sky quads sit 2400 blocks away: cameras need clip_end > 2500 (engine.shots cameras use 20000);
- haze reaches its full amount about 230-270 blocks away. It is mixed over GEOMETRY only (the world writes a 'sky'
  AOV = sky coverage, and the compositor uses Mist - sky); the sky has its own horizon haze baked into the map, so
  the zenith stays the blue (or indigo) of the preset instead of being washed by the haze colour.
"""
import math
import os

import bpy
import numpy as np
from mathutils import Vector

from . import pix

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKY_COLLECTION = "look_sky"
SKY_RADIUS = 2400.0        # distance of the sun / moon quads and the star shell (cameras need clip_end > this)
CLOUD_CELL = 12.0          # one pixel of clouds.png = 12 x 12 blocks, 4 blocks thick, as in the game
CLOUD_THICK = 4.0
COMP_GROUP = "look_compositor"

# View transform. AgX / Filmic wash the saturated Minecraft palette out. Khronos PBR Neutral (the first choice here)
# keeps hues but SUBTRACTS an offset of min(r, g, b) - 6.25 min^2 (0.04 above 0.08) from every channel: under dim
# light (dusk, torches, anything in shade) the smallest channel of every colour lands near zero, which is what
# turned the brown robes wine-red, oak planks orange (s 0.52 -> 0.9), skin s 0.42 -> 0.7 and Steve's trousers from
# (67, 58, 143) to (48, 2, 144). So: plain 'Standard', and the same highlight shoulder as Khronos, without the
# offset, as the last compositor step (setup_compositor: look_tonemap_*).
VIEW_TRANSFORM = "Standard"
VIEW_LOOK = "None"
SHOULDER_START = 0.76       # scene-linear peak where the highlight roll-off starts (Khronos: 0.8 - 0.04)
# How fast a blown-out pixel drifts toward white. Khronos uses 0.15: a lantern's orange glow texel (240, 145, 73)
# at emission 3 then lost half its saturation and rendered salmon pink (253, 188, 154). At 0.06 it stays the game's
# orange (the 2x2 core of the flame still burns out to a pale yellow), and nothing below a peak of about 1.5 changes.
SHOULDER_DESATURATION = 0.06
SKY_AOV = "sky"             # world AOV: 1 where a camera ray reaches the sky (coverage, filtered like the image)


def _lin(hex_str, mul=1.0):
    """'#rrggbb' (sRGB) -> scene-linear (r, g, b) tuple, optionally multiplied."""
    h = hex_str.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        c = c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        out.append(c * mul)
    return tuple(out)


# Sky ramps are lists of (sine of elevation, '#srgb'); 'toward' is the side of the key body, 'away' the opposite.
# 'bounce' = (colour, strength) of the light the lit ground throws back up, as four shadowless sun lamps shining
# upwards at 27 degrees from the four diagonals: an underside receives `strength`, a wall or a face half of it, a
# floor nothing. Fast GI (setup_render) drops real bounce light, and without this every underside (hat brims,
# eaves, crossed arms) renders pure black and faces turned away from the sun go muddy.
PRESETS = {
    # ambient_tint x (sky desaturated to ambient_sat) is the FILL every surface receives from the sky. It is kept
    # within a few percent of neutral (a touch cool): a violet or magenta fill multiplied into the game's browns
    # is what makes robes and dark oak go wine-red. The mood comes from the visible sky, the low warm key, the
    # glow around the sun and the torches, not from tinting the textures.
    # 'sky_haze' = (amount, scale): horizon haze baked into the visible sky, amount * exp(-sin(elevation) / scale).
    "day": dict(
        elevation=48.0, azimuth=215.0, key="sun",
        key_color="#fff3dc", key_energy=4.2, key_angle=1.6,
        toward=[(0.0, "#cfe2ff"), (0.10, "#b4d1ff"), (0.35, "#8db6ff"), (1.0, "#6f9ef5")],
        away=[(0.0, "#c3daff"), (0.10, "#a8c8ff"), (0.35, "#82adfb"), (1.0, "#6f9ef5")],
        below="#b9d0f2", sky_strength=1.0, ambient=1.2, ambient_tint="#f6f8ff", ambient_sat=0.20,
        glow=("#fff1c8", 0.35, 40.0), glow_wide=("#ffe9c0", 0.10, 6.0),
        sun_emit=7.0, moon_emit=0.0, stars=0.0,
        cloud="#ffffff", cloud_strength=1.0, cloud_alpha=0.85,
        haze="#c4dbff", haze_amount=0.30, sky_haze=(0.30, 0.10), mist=(12.0, 260.0), bounce=("#c2cc94", 0.80),
    ),
    "golden": dict(
        elevation=17.0, azimuth=215.0, key="sun",
        key_color="#ffe9cc", key_energy=3.6, key_angle=3.0,
        # peach only in the lowest 10-15 degrees; above that the game's own afternoon blue
        toward=[(0.0, "#ffdfb0"), (0.06, "#f6d2b2"), (0.16, "#c9c8de"), (0.34, "#8fa9e8"), (0.62, "#6b8fe3"), (1.0, "#5177dc")],
        away=[(0.0, "#dcd2d8"), (0.06, "#bcc4e2"), (0.16, "#9bb0e8"), (0.34, "#7d9ae6"), (0.62, "#6388e0"), (1.0, "#5177dc")],
        below="#d9bfa8", sky_strength=1.0, ambient=2.6, ambient_tint="#f7f8ff", ambient_sat=0.08,
        # The halo is MIXED in (the sky turns cream around the sun), not added: orange light added to this blue
        # leaves green as the smallest channel, which is the lilac / pink ring the first version had around the sun
        # (hue 280-340). Mixed, the sky goes blue -> neutral -> cream (hue 35-45) toward the sun.
        halo=("#ffe7a4", ((0.55, 40.0), (0.36, 10.0))),
        glow=("#ffc777", 0.45, 60.0), glow_wide=("#ffb070", 0.0, 5.0),
        sun_emit=8.0, moon_emit=0.0, stars=0.0,
        cloud="#fff3e6", cloud_strength=1.15, cloud_alpha=0.85,
        haze="#eccfb8", haze_amount=0.16, sky_haze=(0.55, 0.075), mist=(10.0, 240.0), bounce=("#d6cfa8", 0.50),
    ),
    "dusk": dict(
        elevation=2.5, azimuth=215.0, key="sun",
        key_color="#ffcda6", key_energy=3.6, key_angle=7.0,
        # orange and pink stay within 20 degrees of the horizon on the sun side; the zenith is indigo, not magenta
        toward=[(0.0, "#ffa25e"), (0.05, "#f98a6c"), (0.14, "#cf7c98"), (0.30, "#6a5aa6"), (0.60, "#353d8e"), (1.0, "#262f7a")],
        away=[(0.0, "#8f89b6"), (0.05, "#7b7ab4"), (0.14, "#6064aa"), (0.30, "#454c9c"), (0.60, "#2f3786"), (1.0, "#262f7a")],
        below="#86708a", sky_strength=1.0, ambient=3.6, ambient_tint="#eef2ff", ambient_sat=0.10,
        glow=("#ff9050", 1.0, 26.0), glow_wide=("#ff7850", 0.26, 4.5),
        sun_emit=7.0, moon_emit=0.0, stars=0.30,
        cloud="#f7b29e", cloud_strength=0.9, cloud_alpha=0.85,
        haze="#b08e9e", haze_amount=0.20, sky_haze=(0.35, 0.07), mist=(8.0, 220.0), bounce=("#d2c2b8", 0.55),
    ),
    "night": dict(
        elevation=30.0, azimuth=35.0, key="moon",
        key_color="#d8dcf6", key_energy=1.7, key_angle=3.0,
        toward=[(0.0, "#b894b8"), (0.06, "#9c84ba"), (0.2, "#7068b2"), (0.5, "#4a56a4"), (1.0, "#34489a")],
        away=[(0.0, "#a388b2"), (0.06, "#8676b2"), (0.2, "#5f5fac"), (0.5, "#434f9e"), (1.0, "#34489a")],
        below="#766a94", sky_strength=1.0, ambient=1.1, ambient_tint="#dde8ff", ambient_sat=0.10,
        glow=("#aab6ff", 0.42, 70.0), glow_wide=("#8f96e8", 0.12, 7.0),
        sun_emit=0.0, moon_emit=3.2, stars=0.85,
        cloud="#8f98c8", cloud_strength=0.75, cloud_alpha=0.8,
        # short, strong mist: houses 20-40 blocks away fade into the mauve horizon in layers (reference 3)
        haze="#837aa8", haze_amount=0.45, sky_haze=(0.30, 0.08), mist=(4.0, 90.0), bounce=("#9a9ec4", 0.10),
    ),
}


# --------------------------------------------------------------------------------------------------------------
# render settings
# --------------------------------------------------------------------------------------------------------------

def setup_render(scene, res=(720, 1280), samples=24, fps=24, motion_blur=True, threads=4):
    """Final-quality Cycles CPU settings: denoised, adaptive, clamped, motion blur, colour management, mist pass."""
    r = scene.render
    r.engine = "CYCLES"
    r.resolution_x, r.resolution_y = int(res[0]), int(res[1])
    r.resolution_percentage = 100
    r.pixel_aspect_x = r.pixel_aspect_y = 1.0
    r.fps, r.fps_base = int(fps), 1.0
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.image_settings.color_depth = "8"
    r.image_settings.compression = 15
    r.threads_mode = "FIXED"
    r.threads = int(threads)
    r.use_motion_blur = bool(motion_blur)
    r.motion_blur_shutter = 0.5
    # shutter opens ON the frame: a hard cut (objects / cameras jumping at an integer frame) never smears
    r.motion_blur_position = "START"
    r.use_persistent_data = True
    r.film_transparent = False
    r.use_compositing = True
    r.use_sequencer = False
    try:
        r.compositor_device = "CPU"
    except (AttributeError, TypeError):
        pass

    c = scene.cycles
    c.device = "CPU"
    c.samples = int(samples)
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.1                   # the denoiser cleans the rest; smooth areas stop early
    c.adaptive_min_samples = max(4, int(samples) // 3)
    c.use_denoising = True
    try:
        c.denoiser = "OPENIMAGEDENOISE"
        c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
        c.denoising_prefilter = "ACCURATE"    # FAST leaves grain in defocused areas
        c.denoising_quality = "BALANCED"      # indistinguishable from HIGH here, ~1.5 s faster per frame
    except (AttributeError, TypeError):
        pass
    c.max_bounces = 4
    c.diffuse_bounces = 2
    # Measured on the real village (4 cores, 720x1280, 24 samples): full bounce light costs 24-31 s per frame in
    # shots where every pixel is geometry. Fast GI keeps direct light and the first bounce and replaces the rest
    # with sky-tinted ambient occlusion: 12-16 s, and stone and wool keep their own colour under torch light
    # instead of going orange from the oak around them. AO distance: world.light_settings.distance (_build_world).
    try:
        c.use_fast_gi = True
        c.fast_gi_method = "REPLACE"
        c.ao_bounces = 1
        c.ao_bounces_render = 1
    except (AttributeError, TypeError):
        pass
    c.glossy_bounces = 2
    c.transmission_bounces = 2
    c.volume_bounces = 0
    c.transparent_max_bounces = 12       # stacked cut-out plants, panes, additive sky quads
    c.sample_clamp_direct = 0.0
    c.sample_clamp_indirect = 3.0
    c.caustics_reflective = False
    c.caustics_refractive = False
    c.blur_glossy = 1.0
    c.pixel_filter_type = "BLACKMAN_HARRIS"
    c.filter_width = 1.3                # (default 1.5) keeps texel edges and the square stars crisp
    c.use_light_tree = True

    scene.display_settings.display_device = "sRGB"
    vs = scene.view_settings
    vs.view_transform = VIEW_TRANSFORM
    vs.look = VIEW_LOOK
    vs.exposure = 0.0
    vs.gamma = 1.0
    for vl in scene.view_layers:
        vl.use_pass_mist = True
    scene["look_setup"] = 1
    return scene


# --------------------------------------------------------------------------------------------------------------
# small builders
# --------------------------------------------------------------------------------------------------------------

def _load_tex(rel, name=None, tint=None):
    """Game texture (path under textures/, no extension) -> packed Blender image; first frame of animated strips
    (read through engine.mcassets, which follows the texture's .mcmeta)."""
    from . import mcassets

    name = name or "look_" + rel.replace("/", "_")
    arr = np.array(mcassets.texture_array(rel))
    if tint is not None:
        arr[..., :3] = (arr[..., :3].astype(np.float32) * (np.array(tint, dtype=np.float32) / 255.0)).astype(np.uint8)
    return pix.image_from_array(name, arr)


def _camera_only(ob):
    """Make an object visible to camera rays only (no shadows, no bounce light)."""
    ob.visible_camera = True
    ob.visible_diffuse = False
    ob.visible_glossy = False
    ob.visible_transmission = False
    ob.visible_volume_scatter = False
    ob.visible_shadow = False


def _new_material(name):
    old = bpy.data.materials.get(name)
    if old is not None:
        bpy.data.materials.remove(old)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    try:
        mat.cycles.emission_sampling = "NONE"       # sky pieces glow for the camera only, never sampled as lights
    except (AttributeError, TypeError):
        pass
    return mat


def _additive_material(name, image=None, color=(1, 1, 1), strength=1.0):
    """Emission added on top of whatever is behind (the game draws sun, moon and stars with additive blending)."""
    mat = _new_material(name)
    nt = mat.node_tree
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    add = nt.nodes.new("ShaderNodeAddShader")
    em = nt.nodes.new("ShaderNodeEmission")
    em.name = "look_emit"
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em.inputs["Strength"].default_value = strength
    em.inputs["Color"].default_value = (*color, 1.0)
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        tex.interpolation = "Closest"
        tex.extension = "EXTEND"
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs[0].default_value = 1.0
        mul.inputs[6].default_value = (*color, 1.0)
        nt.links.new(tex.outputs["Color"], mul.inputs[7])
        nt.links.new(mul.outputs[2], em.inputs["Color"])
    nt.links.new(em.outputs[0], add.inputs[0])
    nt.links.new(tr.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    return mat


def _cloud_material(name, color, strength, alpha):
    """Unlit translucent cloud face (the game shades cloud faces with fixed factors, not with the sun)."""
    mat = _new_material(name)
    nt = mat.node_tree
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = strength
    mix.inputs[0].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return mat


def _mesh_object(name, verts, faces, collection, uvs=None, mat_ids=None, materials=()):
    """Mesh from python lists; uvs = one (u, v) per face corner in face order."""
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    if uvs is not None:
        layer = me.uv_layers.new(name="UVMap")
        layer.data.foreach_set("uv", np.asarray(uvs, dtype=np.float32).ravel())
    for m in materials:
        me.materials.append(m)
    if mat_ids is not None:
        me.polygons.foreach_set("material_index", np.asarray(mat_ids, dtype=np.int32))
    me.update()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    return ob


def _clear_sky(scene):
    """Remove everything a previous set_time() created."""
    col = bpy.data.collections.get(SKY_COLLECTION)
    if col is not None:
        for ob in list(col.objects):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data is not None and data.users == 0:
                if isinstance(data, bpy.types.Mesh):
                    bpy.data.meshes.remove(data)
                elif isinstance(data, bpy.types.Light):
                    bpy.data.lights.remove(data)
        bpy.data.collections.remove(col)
    col = bpy.data.collections.new(SKY_COLLECTION)
    scene.collection.children.link(col)
    return col


def _direction(azimuth_deg, elevation_deg):
    """Unit vector from the scene toward a point in the sky."""
    a, e = math.radians(azimuth_deg), math.radians(elevation_deg)
    return Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))


# --------------------------------------------------------------------------------------------------------------
# world (sky gradient)
# --------------------------------------------------------------------------------------------------------------

def _ramp_points(stops, below):
    """Gradient stops over f = 0.5 + 0.5 * sin(elevation); everything under the horizon fades to `below`."""
    pts = [(0.0, _lin(below, 0.8)), (0.47, _lin(below)), (0.5, _lin(stops[0][1]))]
    pts += [(0.5 + 0.5 * z, _lin(h)) for z, h in stops[1:]]
    return pts


def _eval_ramp(pts, f):
    xs = np.array([p[0] for p in pts])
    cols = np.array([p[1] for p in pts])
    return np.stack([np.interp(f, xs, cols[:, c]) for c in range(3)], axis=-1)


def _sky_arrays(P, key_dir, ambient_mul=1.0, width=512, height=512):
    """Evaluate the sky for every direction of an equirectangular map -> (camera sky, bounce-light fill), linear RGB.

    Two elevation gradients ('toward' / 'away' from the key body) blended by the horizontal angle, plus an optional
    mixed-in halo and two additive glow lobes around the key body. The fill is the same sky, desaturated, tinted and scaled for lighting.
    """
    u = (np.arange(width) + 0.5) / width
    v = (np.arange(height) + 0.5) / height
    lon, lat = np.meshgrid((u - 0.5) * 2.0 * math.pi, (v - 0.5) * math.pi)      # row 0 = straight down
    # Cycles' equirectangular mapping: u = 0.5 - atan2(y, x) / 2pi, v = 0.5 + asin(z) / pi
    x, y, z = np.cos(lat) * np.cos(lon), -np.cos(lat) * np.sin(lon), np.sin(lat)
    f = 0.5 + 0.5 * z
    toward = _eval_ramp(_ramp_points(P["toward"], P["below"]), f)
    away = _eval_ramp(_ramp_points(P["away"], P["below"]), f)
    hd = Vector((key_dir.x, key_dir.y, 0.0))
    hd = hd.normalized() if hd.length > 1e-6 else Vector((1.0, 0.0, 0.0))
    hl = np.maximum(np.sqrt(x * x + y * y), 1e-6)
    t = np.clip(((x * hd.x + y * hd.y) / hl + 0.55) / 1.55, 0.0, 1.0)
    t = (t * t * (3.0 - 2.0 * t))[..., None]
    col = away * (1.0 - t) + toward * t
    k = np.maximum(x * key_dir.x + y * key_dir.y + z * key_dir.z, 0.0)
    if P.get("halo"):                                 # (colour, ((amount, power), ...)): the sky MIXED toward a colour
        hexcol, lobes = P["halo"]
        w = np.clip(sum(a * k ** p for a, p in lobes), 0.0, 0.9)[..., None]
        col = col * (1.0 - w) + np.array(_lin(hexcol)) * w
    for hexcol, strength, power in (P["glow"], P["glow_wide"]):
        if strength > 0:
            col = col + np.array(_lin(hexcol)) * (strength * k ** power)[..., None]
    cam = col * P["sky_strength"]
    amount, scale = P.get("sky_haze", (0.0, 0.1))
    if amount > 0:                                    # horizon haze: full at and below the horizon, gone by ~15 degrees
        hz = (amount * np.exp(-np.maximum(z, 0.0) / scale))[..., None]
        cam = cam * (1.0 - hz) + np.array(_lin(P["haze"])) * hz
    lum = (col * np.array([0.2126, 0.7152, 0.0722])).sum(axis=-1, keepdims=True)
    fill = (lum + (col - lum) * P.get("ambient_sat", 0.55)) * np.array(_lin(P["ambient_tint"])) * P["ambient"] * ambient_mul
    return cam.astype(np.float32), fill.astype(np.float32)


def _float_image(name, rgb):
    """HxWx3 float array (row 0 = bottom) -> packed scene-linear float image."""
    old = bpy.data.images.get(name)
    if old is not None:
        bpy.data.images.remove(old)
    h, w = rgb.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=False, float_buffer=True, is_data=True)
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = rgb
    img.pixels.foreach_set(rgba.ravel())
    try:
        os.makedirs(pix.TEX_DIR, exist_ok=True)
        img.filepath_raw = os.path.join(pix.TEX_DIR, name + ".exr")
        img.file_format = "OPEN_EXR"
        img.save()
    except RuntimeError:
        pass
    img.pack()
    return img


def _ensure_sky_aov(scene):
    """Every view layer carries the 'sky' value AOV the world shader writes (1 = this camera sample saw the sky)."""
    for vl in scene.view_layers:
        if not any(a.name == SKY_AOV for a in vl.aovs):
            a = vl.aovs.add()
            a.name = SKY_AOV
            a.type = "VALUE"


def _build_world(scene, P, key_dir, name, ambient_mul=1.0):
    """World: the sky gradient baked to a small equirectangular map looked up by view direction.

    (The same gradient as a ~30-node procedural shader cost 20 % of the render time; one texture lookup is free.)
    Camera rays see the sky itself, every other ray sees the softer 'fill' version that lights the scene.
    """
    old = bpy.data.worlds.get(name)
    if old is not None:
        bpy.data.worlds.remove(old)
    world = bpy.data.worlds.new(name)
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    cam, fill = _sky_arrays(P, key_dir, ambient_mul)
    tex = {}
    for key, arr in (("sky", cam), ("fill", fill[::4, ::4])):
        node = N("ShaderNodeTexEnvironment")
        node.name = "look_" + key
        node.image = _float_image(name + "_" + key, arr)
        node.projection = "EQUIRECTANGULAR"
        node.interpolation = "Linear"
        tex[key] = node
    lp = N("ShaderNodeLightPath")
    pick = N("ShaderNodeMix")
    pick.data_type = "RGBA"
    L(lp.outputs["Is Camera Ray"], pick.inputs[0])
    L(tex["fill"].outputs["Color"], pick.inputs[6])
    L(tex["sky"].outputs["Color"], pick.inputs[7])
    bg = N("ShaderNodeBackground")
    bg.name = "look_background"
    L(pick.outputs[2], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    out = N("ShaderNodeOutputWorld")
    L(bg.outputs[0], out.inputs["Surface"])
    aov = N("ShaderNodeOutputAOV")                  # sky coverage for the compositor: haze goes on geometry only
    aov.name = "look_sky_aov"
    aov.aov_name = SKY_AOV
    aov.inputs["Value"].default_value = 1.0
    _ensure_sky_aov(scene)

    try:                                   # AUTOMATIC rebuilds a huge importance map on every frame (~3 s);
        world.cycles.sampling_method = "MANUAL"     # this smooth gradient needs very little
        world.cycles.sample_map_resolution = 256
    except (AttributeError, TypeError):
        pass
    world.light_settings.distance = 8.0    # reach of the Fast GI occlusion rays (see setup_render), in blocks
    world.light_settings.ao_factor = 1.0
    ms = world.mist_settings
    ms.use_mist = True
    ms.start, ms.depth = P["mist"]
    ms.falloff = "INVERSE_QUADRATIC"
    scene.world = world
    return world


# --------------------------------------------------------------------------------------------------------------
# sun, moon, stars, clouds
# --------------------------------------------------------------------------------------------------------------

def _sprite(name, col, direction, half_tan, image, strength):
    """Far quad facing the origin with a game celestial texture, additive; half_tan = tan(half angular size)."""
    d = direction.normalized()
    right = d.cross(Vector((0, 0, 1)))
    right = right.normalized() if right.length > 1e-5 else Vector((1, 0, 0))
    up = right.cross(d).normalized()
    c = d * SKY_RADIUS
    h = SKY_RADIUS * half_tan
    verts = [c - right * h - up * h, c + right * h - up * h, c + right * h + up * h, c - right * h + up * h]
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    mat = _additive_material("look_" + name, image=image, strength=strength)
    ob = _mesh_object("look_" + name, [tuple(v) for v in verts], [(0, 1, 2, 3)], col, uvs=uvs, materials=[mat])
    _camera_only(ob)
    return ob


class _JavaRandom:
    """java.util.Random / Minecraft LegacyRandomSource, so the star field is the game's own."""

    def __init__(self, seed):
        self.seed = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)

    def _next(self, bits):
        self.seed = (self.seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        return self.seed >> (48 - bits)

    def next_float(self):
        return self._next(24) / float(1 << 24)

    def next_double(self):
        return ((self._next(26) << 27) + self._next(27)) / float(1 << 53)


def _star_material(name, color, strength):
    """Additive emission whose strength is `strength` x the U coordinate of the face (one brightness per star)."""
    mat = _new_material(name)
    nt = mat.node_tree
    N, L = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    uv = N("ShaderNodeUVMap")
    sep = N("ShaderNodeSeparateXYZ")
    L(uv.outputs["UV"], sep.inputs[0])
    mul = N("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = strength
    L(sep.outputs["X"], mul.inputs[0])
    em = N("ShaderNodeEmission")
    em.name = "look_emit"
    em.inputs["Color"].default_value = (*color, 1.0)
    L(mul.outputs[0], em.inputs["Strength"])
    tr = N("ShaderNodeBsdfTransparent")
    add = N("ShaderNodeAddShader")
    L(em.outputs[0], add.inputs[0])
    L(tr.outputs[0], add.inputs[1])
    L(add.outputs[0], out.inputs["Surface"])
    return mat


def _stars(col, key_dir, brightness, scale=1.6):
    """The game's star field (1500 candidates, seed 10842, quads of half-size 0.15-0.25 at radius 100).

    The quads are the game's, enlarged by `scale` so that a star is 5-9 pixels across in a 720-wide frame through a
    30 mm lens (smaller ones are rounded off by the pixel filter and the denoiser and twinkle when the camera
    drifts). Each star has its own brightness (0.45-1.0 x `brightness`); keep `brightness` below the bloom
    threshold (1.0) or the glare turns the hard squares into soft round dots.
    """
    rnd = _JavaRandom(10842)
    vary = np.random.default_rng(10842)
    # rotate the field with the key body like the game rotates it with the time of day
    az = math.atan2(key_dir.y, key_dir.x)
    ca, sa = math.cos(az), math.sin(az)
    verts, faces, uvs = [], [], []
    R = SKY_RADIUS * 1.02
    for _ in range(1500):
        g = rnd.next_float() * 2.0 - 1.0
        h = rnd.next_float() * 2.0 - 1.0
        k = rnd.next_float() * 2.0 - 1.0
        size = 0.15 + rnd.next_float() * 0.1
        m = g * g + h * h + k * k
        if m <= 0.010000001 or m >= 1.0:
            continue
        ang = rnd.next_double() * math.pi * 2.0
        level = float(0.45 + 0.55 * vary.random() ** 1.6)   # a few bright stars, many faint ones
        v = Vector((g, -k, h)).normalized()             # Minecraft (x, y, z) -> Blender (x, -z, y)
        v = Vector((v.x * ca - v.y * sa, v.x * sa + v.y * ca, v.z))
        if v.z < -0.03:
            continue                                    # below the horizon: never seen
        u = v.cross(Vector((0, 0, 1)))
        u = u.normalized() if u.length > 1e-5 else Vector((1, 0, 0))
        w = v.cross(u)
        a = u * math.cos(ang) + w * math.sin(ang)
        b = v.cross(a)
        s = size / 100.0 * R * scale
        c = v * R
        i = len(verts)
        verts += [tuple(c + a * s + b * s), tuple(c - a * s + b * s), tuple(c - a * s - b * s), tuple(c + a * s - b * s)]
        faces.append((i, i + 1, i + 2, i + 3))
        uvs += [(level, 0.0)] * 4
    mat = _star_material("look_stars", (0.92, 0.95, 1.0), brightness)
    ob = _mesh_object("look_stars", verts, faces, col, uvs=uvs, materials=[mat])
    _camera_only(ob)
    return ob


def _clouds(col, P, height, radius, offset):
    """Blocky clouds from the game's clouds.png: one 12x12x4 slab per pixel, unlit with the game's face shading."""
    from . import mcassets

    mask = np.array(mcassets.texture_array("environment/clouds"))[..., 3] > 0
    n = mask.shape[0]
    rc = int(radius // CLOUD_CELL)
    ox, oy = offset
    idx = np.arange(-rc, rc + 1)
    gx, gy = np.meshgrid(idx, idx, indexing="ij")
    cell = mask[(gy + oy) % n, (gx + ox) % n] & (gx * gx + gy * gy <= rc * rc)
    filled = {(int(a), int(b)) for a, b in zip(gx[cell], gy[cell])}
    verts, faces, mids = [], [], []
    z0, z1 = height, height + CLOUD_THICK

    def quad(p, mid):
        i = len(verts)
        verts.extend(p)
        faces.append((i, i + 1, i + 2, i + 3))
        mids.append(mid)

    for (i, j) in filled:
        x0, y0 = (i - 0.5) * CLOUD_CELL, (j - 0.5) * CLOUD_CELL
        x1, y1 = x0 + CLOUD_CELL, y0 + CLOUD_CELL
        quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], 0)             # underside
        if (i - 1, j) not in filled:
            quad([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], 1)
        if (i + 1, j) not in filled:
            quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], 1)
        if (i, j - 1) not in filled:
            quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], 2)
        if (i, j + 1) not in filled:
            quad([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], 2)
    base = _lin(P["cloud"])
    # game face shading: top 1.0, bottom 0.7, east/west 0.9, north/south 0.8
    mats = [_cloud_material("look_cloud_%s" % k, tuple(c * f for c in base), P["cloud_strength"], P["cloud_alpha"])
            for k, f in (("bottom", 0.74), ("ew", 0.92), ("ns", 0.84))]
    ob = _mesh_object("look_clouds", verts, faces, col, mat_ids=mids, materials=mats)
    _camera_only(ob)
    return ob


def set_time(scene, preset="golden", sun_azimuth=None, sun_elevation=None, key_strength=1.0, ambient_strength=1.0,
             celestial_size=0.5, clouds=True, cloud_height=96.0, cloud_radius=1000.0, cloud_offset=(0, 0),
             star_scale=1.6):
    """Sky, key light and haze for 'day' | 'golden' | 'dusk' | 'night'; returns the created objects in a dict.

    sun_azimuth / sun_elevation (degrees) place the key body: the sun, or the moon for 'night'. Azimuth is
    counter-clockwise from +X (90 = +Y = Minecraft north). key_strength / ambient_strength scale the preset's
    key light and sky fill. celestial_size scales the sun and moon relative to the game (1.0 = game size, which
    is huge through a long lens). Calling it again replaces the previous sky.
    Returned keys: 'sun', 'moon' (Sun-lamp objects; the one below the horizon has energy 0), 'key' (the active
    lamp), 'sun_sprite', 'moon_sprite', 'stars', 'clouds', 'world', 'key_dir' (unit vector toward the key body),
    'preset', 'bounce' (the list of ground-bounce lamps).
    """
    P = PRESETS[preset]
    az = P["azimuth"] if sun_azimuth is None else float(sun_azimuth)
    el = P["elevation"] if sun_elevation is None else float(sun_elevation)
    key_dir = _direction(az, el)
    other_dir = -key_dir
    col = _clear_sky(scene)
    world = _build_world(scene, P, key_dir, "look_world_" + preset, ambient_strength)

    is_sun = P["key"] == "sun"
    sun_dir, moon_dir = (key_dir, other_dir) if is_sun else (other_dir, key_dir)
    lamps = {}
    for which, direction, active in (("sun", sun_dir, is_sun), ("moon", moon_dir, not is_sun)):
        data = bpy.data.lights.new("look_%s_light" % which, "SUN")
        data.color = _lin(P["key_color"]) if active else (1.0, 1.0, 1.0)
        data.energy = P["key_energy"] * key_strength if active else 0.0
        data.angle = math.radians(P["key_angle"])
        ob = bpy.data.objects.new("look_%s_light" % which, data)
        ob.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
        ob.hide_render = not active
        col.objects.link(ob)
        lamps[which] = ob

    bounce = []
    if P.get("bounce") and P["bounce"][1] > 0:
        rise = math.radians(27.0)
        for i in range(4):
            data = bpy.data.lights.new("look_bounce_light", "SUN")
            data.color = _lin(P["bounce"][0])
            data.energy = P["bounce"][1] * ambient_strength / (4.0 * math.sin(rise))
            data.angle = math.radians(40.0)
            data.use_shadow = False                  # it stands in for light off the ground: nothing blocks it
            try:
                data.specular_factor = 0.0
            except (AttributeError, TypeError):
                pass
            ob = bpy.data.objects.new("look_bounce_light_%d" % i, data)
            a = math.radians(45.0 + 90.0 * i)
            source = Vector((math.cos(a) * math.cos(rise), math.sin(a) * math.cos(rise), -math.sin(rise)))
            ob.rotation_euler = source.to_track_quat("Z", "Y").to_euler()      # the lamp sits below the horizon
            col.objects.link(ob)
            bounce.append(ob)

    sun_img = _load_tex("environment/celestial/sun", "look_sun")
    moon_img = _load_tex("environment/celestial/moon/full_moon", "look_moon")
    sun_sprite = _sprite("sun", col, sun_dir, 0.30 * celestial_size, sun_img, P["sun_emit"])     # game: 30 at r=100
    moon_sprite = _sprite("moon", col, moon_dir, 0.20 * celestial_size, moon_img, P["moon_emit"])  # game: 20 at r=100
    sun_sprite.hide_render = (not is_sun) or P["sun_emit"] <= 0
    moon_sprite.hide_render = is_sun or P["moon_emit"] <= 0

    stars = None
    if P["stars"] > 0:
        stars = _stars(col, key_dir, P["stars"], star_scale)
    cloud_ob = _clouds(col, P, cloud_height, cloud_radius, cloud_offset) if clouds else None

    for vl in scene.view_layers:
        vl.use_pass_mist = True
    scene["look_preset"] = preset
    scene["look_haze_color"] = list(_lin(P["haze"]))
    scene["look_haze_amount"] = float(P["haze_amount"])
    _update_haze_nodes(scene)
    return {
        "sun": lamps["sun"], "moon": lamps["moon"], "key": lamps["sun" if is_sun else "moon"],
        "sun_sprite": sun_sprite, "moon_sprite": moon_sprite, "stars": stars, "clouds": cloud_ob,
        "world": world, "key_dir": key_dir, "preset": preset, "bounce": bounce,
    }


# --------------------------------------------------------------------------------------------------------------
# compositor
# --------------------------------------------------------------------------------------------------------------

GRADES = {
    # lift (shadows), gamma (mids), gain (highlights) colours + saturation; deliberately gentle
    # No lift at all: a coloured lift re-tints every shadow (the old warm grade's blue lift made dark robes purple).
    # Saturation stays at or just under 1: coloured light already raises it above the textures' own.
    "warm": dict(lift=(1.0, 1.0, 1.0), gamma=(1.01, 1.0, 0.99), gain=(1.02, 1.0, 0.97), saturation=0.97),
    "cool": dict(lift=(1.0, 1.0, 1.0), gamma=(0.99, 1.0, 1.015), gain=(0.97, 0.995, 1.04), saturation=0.97),
    "neutral": dict(lift=(1.0, 1.0, 1.0), gamma=(1.0, 1.0, 1.0), gain=(1.0, 1.0, 1.0), saturation=1.0),
}


def _set_input(node, name, value):
    """Set a node input by socket name or identifier; returns False when the socket does not exist."""
    for s in node.inputs:
        if s.name == name or s.identifier == name:
            try:
                s.default_value = value
                return True
            except (TypeError, ValueError):
                continue
    return False


def _update_haze_nodes(scene):
    """Push the haze colour / amount stored by set_time() into an existing compositor group."""
    tree = bpy.data.node_groups.get(COMP_GROUP)
    if tree is None:
        return
    haze = tree.nodes.get("look_haze")
    amount = tree.nodes.get("look_haze_amount")
    if haze is not None and "look_haze_color" in scene:
        haze.inputs[7].default_value = (*scene["look_haze_color"], 1.0)
    if amount is not None and "look_haze_amount" in scene and not tree.get("look_haze_fixed", False):
        amount.inputs[1].default_value = float(scene["look_haze_amount"])


def setup_compositor(scene, bloom=1.0, vignette=0.35, grade="warm", haze=None):
    """Compositor: distance haze (mist pass), bloom on lights/moon/sun, gentle grade, soft vignette.

    bloom scales the glare strength (0 disables), vignette is the darkening at the corners (0 disables), grade is
    'warm' | 'cool' | 'neutral'. haze overrides the preset's haze amount (0..1 at the far distance; 0 disables).
    """
    r = scene.render
    r.use_compositing = True
    try:
        r.compositor_device = "CPU"
    except (AttributeError, TypeError):
        pass
    for vl in scene.view_layers:
        vl.use_pass_mist = True
    _ensure_sky_aov(scene)
    old = bpy.data.node_groups.get(COMP_GROUP)
    if old is not None:
        bpy.data.node_groups.remove(old)
    tree = bpy.data.node_groups.new(COMP_GROUP, "CompositorNodeTree")
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    N, L = tree.nodes.new, tree.links.new

    rl = N("CompositorNodeRLayers")
    rl.scene = scene
    image = rl.outputs["Image"]

    # 1. haze: mix toward the horizon colour with distance, on GEOMETRY only. Mist is 1 on the sky; the world's
    #    'sky' AOV is the sky coverage of the pixel, so Mist - sky is the mist of what stands in front of the sky
    #    (correct on anti-aliased and defocused edges too). The sky's own horizon haze is baked into its map.
    amount = N("ShaderNodeMath")
    amount.name = "look_haze_amount"
    amount.operation = "MULTIPLY"
    amount.use_clamp = True
    amount.inputs[1].default_value = float(scene.get("look_haze_amount", 0.3)) if haze is None else float(haze)
    tree["look_haze_fixed"] = haze is not None
    mist = rl.outputs.get("Mist")
    sky = rl.outputs.get(SKY_AOV)
    if mist is not None and sky is not None:
        geo = N("ShaderNodeMath")
        geo.name = "look_haze_geometry"
        geo.operation = "SUBTRACT"
        geo.use_clamp = True
        L(mist, geo.inputs[0])
        L(sky, geo.inputs[1])
        L(geo.outputs[0], amount.inputs[0])
    elif mist is not None:
        L(mist, amount.inputs[0])
    else:
        print("[look] warning: no Mist pass on the render layer, haze disabled")
        amount.inputs[0].default_value = 0.0
    hz = N("ShaderNodeMix")
    hz.name = "look_haze"
    hz.data_type = "RGBA"
    hz.blend_type = "MIX"
    hz.inputs[7].default_value = (*scene.get("look_haze_color", (0.6, 0.7, 0.9)), 1.0)
    L(amount.outputs[0], hz.inputs[0])
    L(image, hz.inputs[6])
    image = hz.outputs[2]

    # 2. bloom
    if bloom > 0:
        gl = N("CompositorNodeGlare")
        gl.name = "look_bloom"
        _set_input(gl, "Type", "Bloom")
        _set_input(gl, "Quality", "High")
        _set_input(gl, "Threshold", 1.0)
        _set_input(gl, "Smoothness", 0.5)
        _set_input(gl, "Clamp", True)
        _set_input(gl, "Maximum", 12.0)
        _set_input(gl, "Strength", min(1.0, 0.42 * bloom))
        _set_input(gl, "Saturation", 1.0)
        _set_input(gl, "Size", 0.62)
        L(image, gl.inputs["Image"])
        image = gl.outputs["Image"]

    # 3. grade
    g = GRADES[grade]
    cb = N("CompositorNodeColorBalance")
    cb.name = "look_grade"
    _set_input(cb, "Type", "Lift/Gamma/Gain")
    _set_input(cb, "Color Lift", (*g["lift"], 1.0))
    _set_input(cb, "Color Gamma", (*g["gamma"], 1.0))
    _set_input(cb, "Color Gain", (*g["gain"], 1.0))
    L(image, cb.inputs["Image"])
    hs = N("CompositorNodeHueSat")
    hs.name = "look_saturation"
    _set_input(hs, "Saturation", g["saturation"])
    L(cb.outputs["Image"], hs.inputs["Image"])
    image = hs.outputs["Image"]

    # 4. vignette: analytic, 1 in the middle falling smoothly to (1 - vignette) in the corners
    if vignette > 0:
        ic = N("CompositorNodeImageCoordinates")
        L(rl.outputs["Image"], ic.inputs["Image"])
        ctr = N("ShaderNodeVectorMath")             # 'Normalized' is 0..1 on both axes -> centred, corners at length 1
        ctr.operation = "MULTIPLY_ADD"
        ctr.inputs[1].default_value = (1.4142, 1.4142, 0.0)
        ctr.inputs[2].default_value = (-0.7071, -0.7071, 0.0)
        L(ic.outputs["Normalized"], ctr.inputs[0])
        ln = N("ShaderNodeVectorMath")
        ln.operation = "LENGTH"
        L(ctr.outputs["Vector"], ln.inputs[0])
        vm = N("ShaderNodeMapRange")
        vm.name = "look_vignette"
        vm.interpolation_type = "SMOOTHSTEP"
        vm.inputs["From Min"].default_value = 0.30
        vm.inputs["From Max"].default_value = 1.05
        vm.inputs["To Min"].default_value = 1.0
        vm.inputs["To Max"].default_value = 1.0 - float(vignette)
        L(ln.outputs["Value"], vm.inputs["Value"])
        mul = N("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs[0].default_value = 1.0
        L(image, mul.inputs[6])
        L(vm.outputs["Result"], mul.inputs[7])
        image = mul.outputs[2]

    # 5. highlight shoulder (the only tone mapping; the view transform is plain sRGB): below SHOULDER_START the
    #    pixel is untouched, above it the peak channel rolls off toward 1 with the hue kept, and very bright pixels
    #    drift toward white. This is Khronos PBR Neutral without its black offset (see VIEW_TRANSFORM).
    image = _shoulder(tree, image)

    out = N("NodeGroupOutput")
    L(image, out.inputs[0])
    _assign_compositor(scene, tree)
    return tree


def _shoulder(tree, image):
    """Append the highlight roll-off nodes to a compositor tree; returns the new image socket."""
    N, L = tree.nodes.new, tree.links.new
    d = 1.0 - SHOULDER_START

    def math(op, a=None, b=None, name=None, clamp=False):
        n = N("ShaderNodeMath")
        n.operation = op
        n.use_clamp = clamp
        if name:
            n.name = name
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                L(v, n.inputs[i])
        return n.outputs[0]

    sep = N("CompositorNodeSeparateColor")
    sep.name = "look_tonemap_split"
    L(image, sep.inputs[0])
    peak = math("MAXIMUM", math("MAXIMUM", sep.outputs[0], sep.outputs[1]), sep.outputs[2], name="look_tonemap_peak")
    peak = math("MAXIMUM", peak, 1e-6)
    # newPeak = 1 - d^2 / (peak + d - start)   for peak > start
    denom = math("MAXIMUM", math("ADD", peak, d - SHOULDER_START), 1e-6)
    new_peak = math("SUBTRACT", 1.0, math("DIVIDE", d * d, denom))
    over = math("GREATER_THAN", peak, SHOULDER_START)
    scale_hi = math("DIVIDE", new_peak, peak)
    # scale = 1 below the shoulder, newPeak / peak above it
    scale = math("ADD", 1.0, math("MULTIPLY", over, math("SUBTRACT", scale_hi, 1.0)), name="look_tonemap_scale")
    scaled = N("ShaderNodeMix")
    scaled.data_type = "RGBA"
    scaled.blend_type = "MULTIPLY"
    scaled.inputs[0].default_value = 1.0
    L(image, scaled.inputs[6])
    L(scale, scaled.inputs[7])
    # g = 1 - 1 / (desaturation * (peak - newPeak) + 1): how far a blown-out pixel moves toward white
    g = math("SUBTRACT", 1.0, math("DIVIDE", 1.0, math("ADD", math("MULTIPLY", math("SUBTRACT", peak, new_peak),
                                                                    SHOULDER_DESATURATION), 1.0)))
    g = math("MULTIPLY", g, over, clamp=True)
    white = N("ShaderNodeMix")
    white.name = "look_tonemap"
    white.data_type = "RGBA"
    white.blend_type = "MIX"
    L(g, white.inputs[0])
    L(scaled.outputs[2], white.inputs[6])
    L(new_peak, white.inputs[7])
    return white.outputs[2]


def _assign_compositor(scene, tree):
    """Make `tree` the scene's only compositor (Blender 5.3: scene.compositor_effects; older: compositing_node_group)."""
    effects = getattr(scene, "compositor_effects", None)
    if effects is not None and hasattr(effects, "new"):
        effects.clear()
        fx = effects.new("look")
        fx.node_group = tree
        fx.enable_for_render = True
    else:
        scene.compositing_node_group = tree


# --------------------------------------------------------------------------------------------------------------
# stand-in scene + self-test
# --------------------------------------------------------------------------------------------------------------

def _box(name, lo, hi, mat, collection, uv_scale=None):
    """Axis-aligned box with every face showing the whole texture upright (or tiled once per block)."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (3, 2, 1, 0)]
    dims = [(x1 - x0, z1 - z0), (y1 - y0, z1 - z0), (x1 - x0, z1 - z0), (y1 - y0, z1 - z0), (x1 - x0, y1 - y0), (x1 - x0, y1 - y0)]
    uvs = []
    for w, h in dims:
        if uv_scale is None:
            w = h = 1.0
        uvs += [(0, 0), (w, 0), (w, h), (0, h)]
    return _mesh_object(name, v, faces, collection, uvs=uvs, materials=[mat])


def standin_scene(scene, torch=True):
    """Small test stage made of real block textures (ground, a few blocks, far pillars, a torch-like light)."""
    col = bpy.data.collections.new("standin")
    scene.collection.children.link(col)

    def mat(tex, tint=None, emission=0.0, alpha="OPAQUE"):
        img = _load_tex("block/" + tex, "standin_" + tex, tint=tint)
        return pix.pixel_material("standin_" + tex, img, emission=emission, alpha=alpha)

    grass = mat("grass_block_top", tint=(0x91, 0xBD, 0x59))
    _box("ground", (-300, -300, -1), (300, 300, 0), grass, col, uv_scale=1)
    path = mat("dirt_path_top")
    _box("path", (-1, -40, -0.06), (1, 60, 0.004), path, col, uv_scale=1)
    planks, cobble, log, bricks = mat("oak_planks"), mat("cobblestone"), mat("oak_log"), mat("stone_bricks")
    logtop = mat("oak_log_top")
    leaves = mat("oak_leaves", tint=(0x77, 0xAB, 0x2F), alpha="CLIP")
    leaves_solid = pix.pixel_material("standin_leaves_solid", leaves.node_tree.nodes["Image Texture"].image)
    for i in range(3):                                   # a little wall: cobble base, planks, log corner
        for k in range(3):
            _box(f"wall_{i}_{k}", (2 + i, 3, k), (3 + i, 4, k + 1), cobble if k == 0 else planks, col)
    for k in range(4):
        _box(f"log_{k}", (5, 3, k), (6, 4, k + 1), log, col)
    _box("log_cap", (5, 3, 4), (6, 4, 4.001), logtop, col)
    _box("bricks_a", (-4, 1, 0), (-3, 2, 1), bricks, col)
    _box("bricks_b", (-4, 1, 1), (-3, 2, 2), bricks, col)
    _box("cobble_a", (-3, 1, 0), (-2, 2, 1), cobble, col)
    _box("planks_a", (1.5, -1.0, 0), (2.5, 0.0, 1), planks, col)
    for i, (x, y, h) in enumerate([(-9, 14, 5), (8, 22, 6), (-6, 34, 5), (12, 48, 7), (-14, 62, 6), (5, 84, 7), (-20, 110, 8), (22, 150, 9)]):
        for k in range(h):                               # trees marching into the distance, to judge the haze
            _box(f"tree_{i}_{k}", (x, y, k), (x + 1, y + 1, k + 1), log, col)
        _box(f"crown_{i}", (x - 2, y - 2, h - 1.5), (x + 3, y + 3, h + 2), leaves, col, uv_scale=1)
        _box(f"crown_core_{i}", (x - 1.5, y - 1.5, h - 1.45), (x + 2.5, y + 2.5, h + 1.5), leaves_solid, col, uv_scale=1)
    if torch:
        glow = mat("glowstone", emission=2.0)       # as engine.blocks.EMISSIVE: only the brightest texels clip
        _box("lamp_post_0", (-1.9, 2.2, 0), (-1.6, 2.5, 1.5), log, col)
        _box("lamp", (-2.0, 2.1, 1.5), (-1.5, 2.6, 2.0), glow, col)
        ld = bpy.data.lights.new("standin_torch", "POINT")
        ld.color = _lin("#ffb060")
        ld.energy = 260.0
        ld.shadow_soft_size = 0.2
        lo = bpy.data.objects.new("standin_torch", ld)
        lo.location = (-1.75, 2.0, 1.75)
        col.objects.link(lo)
    return col


def _test_camera(scene, pos, target, lens=35.0, fstop=None):
    cam = bpy.data.cameras.new("look_test_cam")
    cam.lens = lens
    cam.clip_start, cam.clip_end = 0.05, 20000.0
    ob = bpy.data.objects.new("look_test_cam", cam)
    ob.location = pos
    d = Vector(target) - Vector(pos)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if fstop:
        cam.dof.use_dof = True
        cam.dof.focus_distance = d.length
        cam.dof.aperture_fstop = fstop
    scene.collection.objects.link(ob)
    scene.camera = ob
    return ob


def _render_still(scene, name):
    path = os.path.join(ROOT, "out", "test", name + ".png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


def _selftest(presets):
    import time
    for preset in presets:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = bpy.context.scene
        setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=False)
        standin_scene(scene)
        P = PRESETS[preset]
        sky = set_time(scene, preset, sun_azimuth=101.0)          # key body ahead of the camera, a little left
        setup_compositor(scene, grade="cool" if preset == "night" else ("neutral" if preset == "day" else "warm"))
        tilt = math.radians(min(22.0, max(6.0, P["elevation"] - 22.0)))
        pos = Vector((0.6, -9.0, 0.9))
        target = pos + Vector((-0.03, math.cos(tilt), math.sin(tilt))) * 10
        _test_camera(scene, pos, target, lens=24.0, fstop=None)
        t = time.time()
        path = _render_still(scene, "look_" + preset)
        print(f"wrote {path} in {time.time() - t:.1f}s (key elevation {P['elevation']} deg)")


def _colour_management_test():
    """Render the golden stand-in once per view transform into out/test/look_cm_<name>.png for comparison."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    setup_render(scene, res=(360, 640), samples=12, threads=2, motion_blur=False)
    standin_scene(scene)
    set_time(scene, "golden", sun_azimuth=150.0)
    setup_compositor(scene, grade="neutral")
    _test_camera(scene, (0.5, -5.5, 1.4), (0.3, 3.0, 1.4), lens=28.0)
    for name, vt, lk in (("standard", "Standard", "None"), ("filmic", "Filmic", "Medium High Contrast"),
                         ("agx", "AgX", "AgX - Medium High Contrast"), ("agx_punchy", "AgX", "AgX - Punchy"),
                         ("khronos", "Khronos PBR Neutral", "None")):
        scene.view_settings.view_transform = vt
        scene.view_settings.look = lk
        print("wrote", _render_still(scene, "look_cm_" + name))


if __name__ == "__main__":
    import sys

    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args and args[0] == "cm":
        _colour_management_test()
    else:
        _selftest(args or ["day", "golden", "dusk", "night"])
