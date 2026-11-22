"""Vanilla Minecraft villagers and the player (Steve) as box rigs animated with plain object keyframes. Role CAST.

Nothing here is drawn by hand. Geometry is the game's own entity models (Java Edition 26.3), transcribed
box for box from the model definitions in the client (VillagerModel.createBodyModel, BabyVillagerModel.createBodyModel,
HumanoidModel.createMesh + PlayerModel.createMesh) and unwrapped exactly like ModelPart.Cube does (same face
regions, same mirroring, same 0.9375 model scale). Textures are the game's PNGs: a villager sheet is
entity/villager/villager.png + type/<biome>.png + profession/<p>.png + profession_level/<badge>.png layered the
way VillagerProfessionLayer draws them (cut-out at alpha 0.1, hats combined per the .mcmeta "hat" rules).
Transparent texels are cut out of the geometry itself, so the materials are plain opaque (no alpha shading).

Rig (no armature, only parented objects with their origins at the vanilla pivots):

    root (Empty, feet)            location = position, rotation_euler.z = yaw (0 faces -Y)
      hips (Empty, hip joint)     walk bob, weight shift, lying pose
        leg_l, leg_r (mesh)       rotation_euler.x swings the leg (negative = forward)
        body (mesh)               body + robe/jacket overlay; .x = lean (positive = forward), .y = sway, .z = twist
          head (mesh, neck)       head + hat layer + hat rim + nose; .z = yaw, .x = pitch (positive = down), .y = roll
          arms (villager)         the crossed arms, rest rotation_euler.x = -0.75 rad as in the game
          arm_l, arm_r (player)   .x swings the arm (negative = forward / up), .y splays it sideways

    "left"/"right" are the CHARACTER's left (+X) and right (-X). Part objects use Euler order 'XZY', which is the
    game's ZYX part rotation expressed in Blender axes (model x, y, z rot -> euler x, -z, y).

Animation model: every helper writes ONE "segment" per channel: a run of eased keys that ends in a CONSTANT
key, so a finished move holds its last value and never drifts into whatever is keyed later. Starting a new
move while an older one is still running throws the rest of the older one away, so "stroll, then get
interrupted" just works. Call the helpers in increasing frame order per character.

Hard cuts (place, lie_down, a walk that starts somewhere else, look_at(..., ease=0)) are keyed CUT_LEAD = a quarter
of a frame early. engine.look renders with a 0.5-frame shutter that OPENS on the frame, so frame f-1 is exposed over
[f-1, f-0.5] and frame f over [f, f+0.5]: a cut for frame f must be keyed strictly inside (f-0.5, f], or the last
frame before the cut samples the new value and the character turns into a ghost.

    v = make_villager("ada", "farmer")
    v.place(1, (3, 4, 0), yaw=0.0)                 # shot cut: stand here, neutral pose
    v.idle(1, 60, seed=2)                          # alive while waiting
    end = v.walk(60, path, run=True, from_current=True)   # panic: drops the rest of the idle
    v.look_at(end, bell_point)
"""
import math
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import pix

FPS = 24
WALK_SPEED = 1.6          # units / second, walk() default
RUN_SPEED = 4.4           # walk(run=True) default
MODEL_SCALE = 0.9375      # the game renders adult villagers and players at 15/16 of their model size
HEAD_YAW_MAX = math.radians(70)
HEAD_PITCH_MAX = math.radians(35)
ARMS_FOLD = -0.75         # vanilla rest pitch of the adult villager's crossed arms (radians)
ARM_SPLAY = 0.05          # vanilla resting sideways angle of the player's arms (AnimationUtils.bobArms)
ITEM_ARM_PITCH = -math.pi / 10.0   # vanilla ArmPose.ITEM: a hand that holds an item is carried 18 degrees forward
CUT_LEAD = 0.25           # hard cuts are keyed this many frames early: inside (f - 0.5, f], see the module docstring
SHUTTER = 0.5             # look.setup_render: motion_blur_shutter 0.5, position START (exposure [f, f + 0.5])
ALPHA_CUTOUT = 26         # the game's cut-out render types discard texels with alpha < 0.1
LEVEL_BADGES = ("stone", "iron", "gold", "emerald", "diamond")   # villager level 1..5 (belt buckle gem)
PROFESSION_ALIASES = {"plain": "none", "unemployed": "none", "smith": "toolsmith"}

_LOC, _ROT = "location", "rotation_euler"


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


# ----------------------------------------------------------------------------------------------------
# game textures
# ----------------------------------------------------------------------------------------------------
def _game_texture(path):
    """Game texture 'entity/villager/villager' as HxWx4 uint8 (row 0 = top), read through engine.mcassets."""
    from . import mcassets

    return np.array(mcassets.texture_array(path), dtype=np.uint8)


def _hat_rule(path):
    """The 'villager.hat' rule of a texture's .mcmeta: 'none' | 'partial' | 'full' (the game's VillagerMetadataSection)."""
    from . import mcassets

    return str(mcassets.texture_meta(path).get("villager", {}).get("hat", "none")).lower()


def villager_professions():
    """Every profession the game ships a texture for (textures/entity/villager/profession), plus 'none'."""
    from . import mcassets

    return tuple(mcassets.list_textures("entity/villager/profession")) + ("none",)


def _over(sheet, layer, skip=()):
    """Draw one cut-out layer over the sheet like the game does: texels with alpha >= 0.1 replace what is below."""
    mask = layer[..., 3] >= ALPHA_CUTOUT
    for (u0, v0, u1, v1) in skip:
        mask[v0:v1, u0:u1] = False
    sheet[mask, :3] = layer[mask, :3]
    sheet[mask, 3] = 255


def _cube_uv_rect(c):
    """Texture rectangle (u0, v0, u1, v1) that a cube's unwrap occupies."""
    w, h, d = c["size"]
    return (int(c["u"]), int(c["v"]), int(c["u"] + 2 * (w + d)), int(c["v"] + d + h))


def villager_sheet(profession="none", biome="plains", level=1, child=False):
    """(key, HxWx4 uint8) the villager texture layers of the game composited into one sheet.

    Adult: villager.png, then type/<biome>.png (without its head parts when the profession hat hides the type hat:
    profession hat 'full', or 'partial' over a 'full' type hat), then profession/<p>.png, then the level badge
    profession_level/<stone|iron|gold|emerald|diamond>.png (not for 'none' and 'nitwit').
    Baby: villager_baby.png, then baby/<biome>.png (babies show no profession).
    """
    if child:
        key = "villager_baby_%s" % biome
        sheet = np.zeros_like(_game_texture("entity/villager/villager_baby"))
        _over(sheet, _game_texture("entity/villager/villager_baby"))
        _over(sheet, _game_texture("entity/villager/baby/%s" % biome))
        return key, sheet
    badge = LEVEL_BADGES[int(_clamp(level, 1, len(LEVEL_BADGES))) - 1]
    has_badge = profession not in ("none", "nitwit")
    key = "villager_%s_%s%s" % (biome, profession, "_" + badge if has_badge else "")
    sheet = np.zeros_like(_game_texture("entity/villager/villager"))
    _over(sheet, _game_texture("entity/villager/villager"))
    type_hat = _hat_rule("entity/villager/type/%s" % biome)
    prof_hat = _hat_rule("entity/villager/profession/%s" % profession) if profession != "none" else "none"
    type_hat_shown = prof_hat == "none" or (prof_hat == "partial" and type_hat != "full")
    skip = ()
    if not type_hat_shown:                                # the game draws the type layer with the "no hat" model: no head
        head = next(p for p in _villager_spec()["parts"] if p["name"] == "head")
        skip = [_cube_uv_rect(c) for _chain, cubes in head["groups"] for c in cubes]
    _over(sheet, _game_texture("entity/villager/type/%s" % biome), skip)
    if profession != "none":
        _over(sheet, _game_texture("entity/villager/profession/%s" % profession))
        if has_badge:
            _over(sheet, _game_texture("entity/villager/profession_level/%s" % badge))
    return key, sheet


def player_sheet(skin="steve"):
    """(key, HxWx4 uint8) a wide-armed player skin from textures/entity/player/wide (alpha cut at 0.1)."""
    arr = _game_texture("entity/player/wide/%s" % skin)
    sheet = np.zeros_like(arr)
    _over(sheet, arr)
    return "player_%s" % skin, sheet


def _memory_image(name, arr):
    """HxWx4 uint8 (row 0 = top) -> packed in-memory bpy Image with every texel opaque (nothing is written to disk)."""
    h, w = arr.shape[:2]
    old = bpy.data.images.get(name)
    if old is not None:
        bpy.data.images.remove(old)
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.alpha_mode = "STRAIGHT"
    rgba = np.asarray(arr, dtype=np.float32) / 255.0
    rgba[..., 3] = 1.0                                     # cut-outs are geometry; never let filtering see clear texels
    img.pixels.foreach_set(np.flipud(rgba).ravel())
    try:
        img.pack()
    except RuntimeError:
        pass
    return img


def _sheet_material(key, sheet):
    """Opaque Closest-filtered material for a composited sheet; one per distinct sheet, shared between characters."""
    name = "cast_" + key
    mat = bpy.data.materials.get(name)
    if mat is not None and mat.get("cast_sheet") == key:
        return mat
    mat = pix.pixel_material(name, _memory_image(name, sheet), alpha="OPAQUE", roughness=0.95)
    mat["cast_sheet"] = key
    return mat


def _sheet_material_two_sided(key, sheet):
    """The same sheet for single-quad, no-cull parts (the straw hat's brim): seen from behind, the quad shows the
    light that falls on its FRONT (Translucent, whose flipped normal weights the far side's light exactly like the
    front face does), so the underside of the brim is as bright as its top, as in the game. A plain two-sided quad
    is lit from below only there and renders near-black: the brim then reads as dark hair."""
    name = "cast_" + key + "_rim"
    mat = bpy.data.materials.get(name)
    if mat is not None and mat.get("cast_sheet") == key:
        return mat
    base = _sheet_material(key, sheet)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    tex = N("ShaderNodeTexImage")
    tex.image = base.node_tree.nodes["Image Texture"].image
    tex.interpolation = "Closest"
    tex.extension = "REPEAT"
    front = N("ShaderNodeBsdfDiffuse")
    back = N("ShaderNodeBsdfTranslucent")
    geo = N("ShaderNodeNewGeometry")
    mix = N("ShaderNodeMixShader")
    L(tex.outputs["Color"], front.inputs["Color"])
    L(tex.outputs["Color"], back.inputs["Color"])
    L(geo.outputs["Backfacing"], mix.inputs[0])
    L(front.outputs[0], mix.inputs[1])
    L(back.outputs[0], mix.inputs[2])
    L(mix.outputs[0], out.inputs["Surface"])
    mat["cast_sheet"] = key
    return mat


# ----------------------------------------------------------------------------------------------------
# vanilla entity models (pixels, the game's model space: x toward the character's left, y DOWN, z toward the
# back; the feet stand on y = 24)
# ----------------------------------------------------------------------------------------------------
def _cube(u, v, x, y, z, w, h, d, grow=0.0, mirror=False, two_sided=False):
    """CubeListBuilder.texOffs(u, v).addBox(x, y, z, w, h, d, CubeDeformation(grow)) (mirror = .mirror()).

    two_sided marks a cube that is really a flat no-cull sheet (the villager's hat rim): only one of its big faces
    has texels and the game shows that quad from both sides at the same brightness, so its faces get the
    back-lit material variant (see _sheet_material)."""
    return dict(u=u, v=v, pos=(x, y, z), size=(w, h, d), grow=grow, mirror=mirror, two_sided=two_sided)


def _pose(x=0.0, y=0.0, z=0.0, rx=0.0, ry=0.0, rz=0.0):
    """PartPose.offsetAndRotation(x, y, z, rx, ry, rz)."""
    return ((x, y, z), (rx, ry, rz))


def _villager_spec():
    """net.minecraft.client.model.npc.VillagerModel.createBodyModel(), drawn at MeshTransformer.scaling(0.9375)."""
    return dict(
        tex=(64, 64), scale=MODEL_SCALE, hip=12.0, top=-10.0, eye=-3.5, back=3.5, sleep_eye=1.62,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 12, 0), groups=[([_pose(0, -12, 0)], [
                _cube(16, 20, -4, 0, -3, 8, 12, 6),                         # body
                _cube(0, 38, -4, 0, -3, 8, 20, 6, grow=0.5)])]),            # jacket (the robe)
            dict(name="head", parent="body", pivot=(0, 0, 0), groups=[
                ([], [_cube(0, 0, -4, -10, -4, 8, 10, 8),                   # head
                      _cube(32, 0, -4, -10, -4, 8, 10, 8, grow=0.51)]),     # hat
                ([_pose(rx=-math.pi / 2.0)], [_cube(30, 47, -8, -8, -6, 16, 16, 1, two_sided=True)]),   # hat_rim
                ([_pose(0, -2, 0)], [_cube(24, 0, -1, -1, -6, 2, 4, 2)])]),             # nose
            dict(name="arms", parent="body", pivot=(0, 3, -1), rot=(ARMS_FOLD, 0, 0), groups=[([], [
                _cube(44, 22, -8, -2, -2, 4, 8, 4),
                _cube(44, 22, 4, -2, -2, 4, 8, 4, mirror=True),
                _cube(40, 38, -4, 2, -2, 8, 4, 4)])]),
            dict(name="leg_r", parent="hips", pivot=(-2, 12, 0), groups=[([], [_cube(0, 22, -2, 0, -2, 4, 12, 4)])]),
            dict(name="leg_l", parent="hips", pivot=(2, 12, 0),
                 groups=[([], [_cube(0, 22, -2, 0, -2, 4, 12, 4, mirror=True)])]),
        ])


def _baby_villager_spec():
    """net.minecraft.client.model.npc.BabyVillagerModel.createBodyModel() (the dedicated baby model, drawn unscaled)."""
    fold = -1.0472
    return dict(
        tex=(64, 64), scale=1.0, hip=21.5, top=8.0, eye=13.5, back=1.7, sleep_eye=0.81,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 21.5, 0), groups=[
                ([_pose(0, 18.75 - 21.5, 0)], [_cube(0, 15, -2, -2.75, -1.5, 4, 5, 3)]),               # body
                ([_pose(0.5, 24 - 21.5, 0)], [_cube(16, 21, -2.5, -8, -1.5, 4, 6, 3, grow=0.2)])]),    # bb_main (robe)
            dict(name="head", parent="body", pivot=(0, 16, 0), groups=[
                ([], [_cube(0, 0, -4, -8, -3.5, 8, 8, 7)]),
                ([_pose(0, -4, 0)], [_cube(0, 30, -4, -4, -3.5, 8, 8, 7, grow=0.3)]),                   # hat
                ([_pose(0, -4.5, 0)], [_cube(0, 45, -7, -0.5, -6, 14, 1, 12, two_sided=True)]),         # hat_rim
                ([_pose(0, -2, -4)], [_cube(23, 0, -1, 0, -0.5, 2, 2, 1)])]),                           # nose
            dict(name="arms", parent="body", pivot=(0, 17.5, 0), groups=[
                ([_pose(-3, 1.4025, -0.9599, rx=fold)], [_cube(36, 15, -1, -2.4925, -1.8401, 2, 4, 2),
                                                         _cube(16, 15, 5, -2.4925, -1.8401, 2, 4, 2)]),
                ([_pose(0, 0.9024, -1.8175, rx=fold)], [_cube(24, 17, -2, -0.9924, -0.9825, 4, 2, 2)])]),
            dict(name="leg_r", parent="hips", pivot=(-1, 21.5, 0), groups=[([], [_cube(8, 23, -1, -0.5, -1, 2, 3, 2)])]),
            dict(name="leg_l", parent="hips", pivot=(1, 21.5, 0), groups=[([], [_cube(0, 23, -1, -0.5, -1, 2, 3, 2)])]),
        ])


def _player_spec():
    """HumanoidModel.createMesh + PlayerModel.createMesh(slim=false), drawn at AvatarRenderer's 0.9375 scale."""
    return dict(
        tex=(64, 64), scale=MODEL_SCALE, hip=12.0, top=-8.0, eye=-3.5, back=2.0, sleep_eye=1.62,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 12, 0), groups=[([_pose(0, -12, 0)], [
                _cube(16, 16, -4, 0, -2, 8, 12, 4),
                _cube(16, 32, -4, 0, -2, 8, 12, 4, grow=0.25)])]),          # jacket
            dict(name="head", parent="body", pivot=(0, 0, 0), groups=[([], [
                _cube(0, 0, -4, -8, -4, 8, 8, 8),
                _cube(32, 0, -4, -8, -4, 8, 8, 8, grow=0.5)])]),            # hat
            dict(name="arm_r", parent="body", pivot=(-5, 2, 0), groups=[([], [
                _cube(40, 16, -3, -2, -2, 4, 12, 4),
                _cube(40, 32, -3, -2, -2, 4, 12, 4, grow=0.25)])]),         # right_sleeve
            dict(name="arm_l", parent="body", pivot=(5, 2, 0), groups=[([], [
                _cube(32, 48, -1, -2, -2, 4, 12, 4),
                _cube(48, 48, -1, -2, -2, 4, 12, 4, grow=0.25)])]),         # left_sleeve
            # the vanilla legs overlap by 0.2 px at the centre line; xclip trims each at x = 0 (no coplanar faces)
            dict(name="leg_r", parent="hips", pivot=(-1.9, 12, 0), xclip=(None, 1.9), groups=[([], [
                _cube(0, 16, -2, 0, -2, 4, 12, 4),
                _cube(0, 32, -2, 0, -2, 4, 12, 4, grow=0.25)])]),           # right_pants
            dict(name="leg_l", parent="hips", pivot=(1.9, 12, 0), xclip=(-1.9, None), groups=[([], [
                _cube(16, 48, -2, 0, -2, 4, 12, 4),
                _cube(0, 48, -2, 0, -2, 4, 12, 4, grow=0.25)])]),           # left_pants
        ])


def _pose_matrix(pose):
    """4x4 of a PartPose in model space: translate, then rotate Z*Y*X (ModelPart.translateAndRotate)."""
    (x, y, z), (rx, ry, rz) = pose
    return (Matrix.Translation((x, y, z)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(ry, 4, "Y")
            @ Matrix.Rotation(rx, 4, "X"))


def _cube_faces(c):
    """The six textured quads of a cube exactly as ModelPart.Cube builds them: [[(model xyz, (u px, v px)) x 4]]."""
    x, y, z = c["pos"]
    w, h, d = c["size"]
    g = c["grow"]
    x0, y0, z0, x1, y1, z1 = x - g, y - g, z - g, x + w + g, y + h + g, z + d + g
    if c["mirror"]:
        x0, x1 = x1, x0
    v0, v1, v2, v3 = (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)
    v4, v5, v6, v7 = (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
    u, v = c["u"], c["v"]
    u0, u1, u2, u3, u4, u5 = u, u + d, u + d + w, u + d + w + w, u + d + w + d, u + d + w + d + w
    t0, t1, t2 = v, v + d, v + d + h
    polys = (
        ((v5, v4, v0, v1), u1, t0, u2, t1),       # DOWN  (model -y: the visible TOP of the box)
        ((v2, v3, v7, v6), u2, t1, u3, t0),       # UP    (model +y: the underside)
        ((v0, v4, v7, v3), u0, t1, u1, t2),       # WEST  (-x: the character's right)
        ((v1, v0, v3, v2), u1, t1, u2, t2),       # NORTH (-z: the front)
        ((v5, v1, v2, v6), u2, t1, u4, t2),       # EAST  (+x: the character's left)
        ((v4, v5, v6, v7), u4, t1, u5, t2),       # SOUTH (+z: the back)
    )
    out = []
    for verts, ua, va, ub, vb in polys:           # ModelPart.Polygon: the corners get (ub,va) (ua,va) (ua,vb) (ub,vb)
        out.append(list(zip(verts, ((ub, va), (ua, va), (ua, vb), (ub, vb)))))
    return out


def _rects(mask):
    """Greedy cover of the True cells of a 2-D mask by rectangles (c0, r0, c1, r1), ends exclusive."""
    h, w = mask.shape
    used = np.zeros_like(mask)
    out = []
    for r in range(h):
        c = 0
        while c < w:
            if not mask[r, c] or used[r, c]:
                c += 1
                continue
            c1 = c
            while c1 < w and mask[r, c1] and not used[r, c1]:
                c1 += 1
            r1 = r + 1
            while r1 < h and mask[r1, c:c1].all() and not used[r1, c:c1].any():
                r1 += 1
            used[r:r1, c:c1] = True
            out.append((c, r, c1, r1))
            c = c1
    return out


def _part_mesh(name, part, sheet, unit, material, material_two_sided=None):
    """Mesh of one rig part in its own Blender frame: every cube face, with clear texels cut out of the geometry.
    Faces of cubes flagged two_sided use `material_two_sided` (slot 1)."""
    sh, sw = sheet.shape[:2]
    opaque = sheet[..., 3] >= ALPHA_CUTOUT
    lo, hi = part.get("xclip", (None, None))
    verts, faces, uvs, slots = [], [], [], []

    def to_local(m, p):
        """Cube-space point -> part-local Blender coordinates (model x, y, z -> x, z, -y)."""
        q = m @ Vector(p)
        x = q.x
        if lo is not None:
            x = max(x, lo)
        if hi is not None:
            x = min(x, hi)
        return Vector((x, q.z, -q.y)) * unit

    for chain, cubes in part["groups"]:
        m = Matrix.Identity(4)
        for pose in chain:
            m = m @ _pose_matrix(pose)
        for c in cubes:
            x, y, z = c["pos"]
            w, h, d = c["size"]
            centre = to_local(m, (x + w / 2.0, y + h / 2.0, z + d / 2.0))
            for quad in _cube_faces(c):
                pts = [to_local(m, p) for p, _uv in quad]
                if c["grow"] and any(k is not None and all(abs(p.x - k * unit) < 1e-9 for p in pts) for k in (lo, hi)):
                    continue                                             # overlay face flattened onto the clip plane
                tex = [uv for _p, uv in quad]
                ua, va = tex[0]
                b = next(i for i in (1, 3) if tex[i][1] == va)          # shares the v of corner 0
                dd = 4 - b                                               # shares the u of corner 0
                ub, vd = tex[b][0], tex[dd][1]
                if ua == ub or va == vd:
                    continue
                du, dv = (pts[b] - pts[0]) / (ub - ua), (pts[dd] - pts[0]) / (vd - va)
                u_lo, u_hi = int(round(min(ua, ub))), int(round(max(ua, ub)))
                v_lo, v_hi = int(round(min(va, vd))), int(round(max(va, vd)))
                if u_lo < 0 or v_lo < 0 or u_hi > sw or v_hi > sh:
                    continue
                outward = sum(pts, Vector()) / 4.0 - centre
                for (c0, r0, c1, r1) in _rects(opaque[v_lo:v_hi, u_lo:u_hi]):
                    c0, c1, r0, r1 = c0 + u_lo, c1 + u_lo, r0 + v_lo, r1 + v_lo
                    corners = [(c0, r0), (c1, r0), (c1, r1), (c0, r1)]
                    ps = [pts[0] + du * (cu - ua) + dv * (cv - va) for cu, cv in corners]
                    e = 0.02                                             # keep Closest sampling off the texel borders
                    tu = [(c0 + e, r0 + e), (c1 - e, r0 + e), (c1 - e, r1 - e), (c0 + e, r1 - e)]
                    if (ps[1] - ps[0]).cross(ps[3] - ps[0]).dot(outward) < 0.0:
                        ps.reverse()
                        tu.reverse()
                    n = len(verts)
                    verts.extend(tuple(p) for p in ps)
                    faces.append((n, n + 1, n + 2, n + 3))
                    uvs.extend((tx / sw, 1.0 - ty / sh) for tx, ty in tu)
                    slots.append(1 if c.get("two_sided") and material_two_sided is not None else 0)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    layer = me.uv_layers.new(name="UVMap")
    layer.data.foreach_set("uv", [x for uv in uvs for x in uv])
    me.materials.append(material)
    if any(slots):
        me.materials.append(material_two_sided)
        me.polygons.foreach_set("material_index", slots)
    me.update()
    return me


def _build_rig(name, spec, sheet, material, collection, material_two_sided=None):
    """Create root, hips and the mesh parts of a model spec; returns {part name: Object}."""
    unit = spec["scale"] / 16.0
    root = bpy.data.objects.new(name + "_root", None)
    root.empty_display_size = 0.25
    collection.objects.link(root)
    hips = bpy.data.objects.new(name + "_hips", None)
    hips.empty_display_size = 0.12
    collection.objects.link(hips)
    hips.parent = root
    hips.location = (0.0, 0.0, (24.0 - spec["hip"]) * unit)
    objs = {"root": root, "hips": hips}
    pivots = {"root": (0.0, 24.0, 0.0), "hips": (0.0, spec["hip"], 0.0)}
    for part in spec["parts"]:
        me = _part_mesh(name + "_" + part["name"], part, sheet, unit, material, material_two_sided)
        ob = bpy.data.objects.new(name + "_" + part["name"], me)
        collection.objects.link(ob)
        ob.parent = objs[part["parent"]]
        px, py, pz = (a - b for a, b in zip(part["pivot"], pivots[part["parent"]]))
        ob.location = (px * unit, pz * unit, -py * unit)
        ob.rotation_mode = "XZY"
        rx, ry, rz = part.get("rot", (0.0, 0.0, 0.0))
        ob.rotation_euler = (rx, rz, -ry)
        objs[part["name"]] = ob
        pivots[part["name"]] = part["pivot"]
    return objs


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


def _offsets(obj, path, index, frame, offs, lo=None, hi=None, interp="SMOOTH"):
    """Gesture: keys at frame + df with value base + offset (base = value at `frame`), back to hold at the end."""
    base = _val(obj, path, index, frame)
    keys = [(frame, None)]
    for df, off in offs:
        v = base + off
        if lo is not None:
            v = _clamp(v, lo, hi)
        keys.append((frame + df, v))
    _segment(obj, path, index, keys, interp)
    return base


def _cut(obj, path, index, frame, value, hold_rest=True):
    """Hard jump to `value`, keyed CUT_LEAD frames before `frame` with CONSTANT interpolation.

    A move still running at the cut keeps its motion right up to the cut; the rest of it is discarded.
    hold_rest: when this is the channel's very first key, also key the value it had until now just before the cut,
    so the jump does not reach back in time (a lone key holds for ALL frames: a head turned by look_at(ease=0) in
    shot 3 would already be turned in shot 1). place() passes False for the root: nobody is anywhere before that.
    """
    t = frame - CUT_LEAD
    gap = 0.03        # the hold key sits this far before the cut: keyframe_points.insert() MERGES keys closer than 0.01
    fresh = _find(obj, path, index)
    fresh = fresh is None or not len(fresh.keyframe_points)
    rest = None
    if fresh and hold_rest:
        cur = getattr(obj, path)
        rest = float(cur[index]) if hasattr(cur, "__len__") else float(cur)
    fc = _ensure(obj, path, index)
    kps = fc.keyframe_points
    pre = None
    if rest is not None and abs(rest - float(value)) > 1e-9:
        pre = rest
    if len(kps):
        running = False
        for kp in kps:
            if kp.co.x >= t - gap - 0.01:
                break
            running = kp.interpolation != "CONSTANT"
        if running:
            pre = float(fc.evaluate(t - gap))
        doomed = []
        for i, kp in enumerate(kps):
            if kp.co.x < t - gap - 0.01 or not running:
                continue
            doomed.append(i)
            if kp.interpolation == "CONSTANT":
                running = False
        for i in reversed(doomed):
            kps.remove(kps[i])
    if pre is not None:
        _put(fc, t - gap, pre, "CONSTANT")
    _put(fc, t, value, "CONSTANT")
    fc.update()


def _cut_at(obj, path, index, frame):
    """True when the channel has a hard cut keyed for `frame` (a place() on that very frame)."""
    fc = _find(obj, path, index)
    if fc is None:
        return False
    t = frame - CUT_LEAD
    return any(abs(kp.co.x - t) < 1e-3 and kp.interpolation == "CONSTANT" for kp in fc.keyframe_points)


def read_keys(obj, path, index=0):
    """Read a channel's keys back as [(frame, value, interpolation)] (for tests and debugging)."""
    fc = _find(obj, path, index)
    if fc is None:
        return []
    return [(round(k.co.x, 3), round(k.co.y, 5), k.interpolation) for k in fc.keyframe_points]


# ----------------------------------------------------------------------------------------------------
# held items (the game's ItemInHandLayer / CrossedArmsItemLayer transforms)
# ----------------------------------------------------------------------------------------------------
_AXES = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))   # model (x, y, z) -> Blender (x, z, -y)


def _held_matrix(kind, scale):
    """Parent-space matrix for a flat item sprite (origin at its centre, in its XZ plane, front -Y, 16 px = 1 unit).

    kind 'hand': the player's right hand, display context thirdperson_righthand of models/item/generated.json
    (translation [0, 3, 1], scale 0.55) after ItemInHandLayer's rotate X -90, rotate Y 180, translate (1, 2, -10)/16.
    kind 'arms': on a villager's crossed arms, display context ground (translation [0, 2, 0], scale 0.5) after
    CrossedArmsItemLayer's rotate X 0.75, scale 1.07, translate (0, 0.13, -0.34), rotate X pi.
    """
    if kind == "hand":
        chain = (Matrix.Rotation(math.radians(-90.0), 4, "X") @ Matrix.Rotation(math.radians(180.0), 4, "Y")
                 @ Matrix.Translation((1.0 / 16.0, 2.0 / 16.0, -10.0 / 16.0))
                 @ Matrix.Translation((0.0, 3.0 / 16.0, 1.0 / 16.0)) @ Matrix.Diagonal((0.55, 0.55, 0.55, 1.0)))
    else:
        chain = (Matrix.Rotation(0.75, 4, "X") @ Matrix.Diagonal((1.07, 1.07, 1.07, 1.0))
                 @ Matrix.Translation((0.0, 0.13, -0.34)) @ Matrix.Rotation(math.pi, 4, "X")
                 @ Matrix.Translation((0.0, 2.0 / 16.0, 0.0)) @ Matrix.Diagonal((0.5, 0.5, 0.5, 1.0)))
    return Matrix.Diagonal((scale, scale, scale, 1.0)) @ _AXES @ chain @ _AXES


# ----------------------------------------------------------------------------------------------------
# Character
# ----------------------------------------------------------------------------------------------------
_RIG_PARTS = {}            # object name -> Character, so look_at(frame, other.head) can use the keyed eye point


class Character:
    """A box-rig character: an Empty at the feet with parented mesh parts, animated by object keyframes."""

    def __init__(self, name, kind, parts, spec, profession=None, child=False):
        self.name, self.kind, self.profession, self.child = name, kind, profession, child
        self.parts = parts
        for ob in parts.values():
            _RIG_PARTS[ob.name] = self
        self.root, self.hips, self.body, self.head = parts["root"], parts["hips"], parts["body"], parts["head"]
        self.leg_l, self.leg_r = parts["leg_l"], parts["leg_r"]
        self.arms = parts.get("arms")
        self.arm_l, self.arm_r = parts.get("arm_l"), parts.get("arm_r")
        self.model_scale = spec["scale"]
        self.unit = unit = spec["scale"] / 16.0
        self.height = (24.0 - spec["top"]) * unit
        self.eye_height = (24.0 - spec["eye"]) * unit
        self.leg_len = (24.0 - spec["hip"]) * unit
        self.back_depth = spec["back"] * unit
        self.sleep_shift = spec["sleep_eye"] - 0.1          # LivingEntityRenderer: slide (standing eye height - 0.1) down the bed
        self.stride = self.leg_len / 0.703125               # 1.0 for the adult rigs
        self.held = None
        self._foot = 1
        self._lying = []                                    # (frame, head point or None) per place() / lie_down()
        if self.arm_r is not None:                          # the game never lets the arms hang dead straight
            self.arm_r.rotation_euler[1] = ARM_SPLAY
            self.arm_l.rotation_euler[1] = -ARM_SPLAY
        # (object, path, index, rest value) for every pose channel except root position and yaw
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
        """World point between the eyes at `frame` (standing, or lying after lie_down) - a good look/focus target."""
        lying = None
        for f, point in self._lying:
            if f <= frame + 1e-6:
                lying = point
        if lying is not None:
            return lying.copy()
        return self.pos_at(frame) + Vector((0.0, 0.0, self.eye_height))

    def _point(self, target, frame):
        """World position of a look / face target AT `frame`: a point, a Character (its eyes) or any Object."""
        if isinstance(target, Character):
            return target.eye_point(frame)
        if isinstance(target, bpy.types.Object):
            owner = _RIG_PARTS.get(target.name)
            if owner is not None and owner.head is target:             # a rig's head: the keyed eye point is exact
                return owner.eye_point(frame)
            if target.parent is None and target.animation_data is None and not target.constraints:
                return Vector(target.location)
            # parented, animated or constrained: evaluate the scene at the keyed frame (film builds sit on frame 1,
            # so the current-frame matrix would aim at where the target was at the start of the film)
            scene = bpy.context.scene
            cur, sub = scene.frame_current, scene.frame_subframe
            whole = int(math.floor(frame))
            scene.frame_set(whole, subframe=float(frame) - whole)
            point = target.matrix_world.translation.copy()
            scene.frame_set(cur, subframe=sub)
            return point
        return _vec3(target)

    def _rest(self, ob, path, index):
        for o, p, i, rest in self._pose:
            if o is ob and p == path and i == index:
                return rest
        return 0.0

    def _set_rest(self, ob, path, index, value):
        """Change a part's rest value (unkeyed pose and what place() resets to)."""
        for n, (o, p, i, _rest) in enumerate(self._pose):
            if o is ob and p == path and i == index:
                self._pose[n] = (o, p, i, float(value))
        getattr(ob, path)[index] = value

    # ------------------------------------------------------------------ placement
    def _reset_pose(self, frame):
        for ob, path, i, rest in self._pose:
            if _find(ob, path, i) is not None:
                _cut(ob, path, i, frame, rest)

    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard-set position and yaw from `frame` on (CONSTANT keys, neutral standing pose) - use at shot cuts."""
        p = _vec3(pos)
        for i in range(3):
            _cut(self.root, _LOC, i, frame, p[i], hold_rest=False)
        _cut(self.root, _ROT, 2, frame, yaw, hold_rest=False)
        if not keep_pose:
            self._reset_pose(frame)
            self._lying.append((frame, None))

    def lie_down(self, frame, bed_pos, yaw, lift=0.125):
        """Sleep on a bed from `frame` on (hard cut): flat on the back, face up, head on the pillow, as in the game.

        bed_pos = centre of the bed's top surface (where its foot and head blocks meet, z = top of the mattress,
        9/16 above the bed's floor): the Village anchors `house_*_bed_N`. yaw = the yaw of someone standing at the
        foot of the bed looking at the pillow (Village.yaws[anchor]). The game puts a sleeper's origin at the
        centre of the head block, 0.6875 above the bed's floor, and slides the model (eye height - 0.1) toward the
        foot; `lift` is that 0.6875 - 0.5625 = 0.125 between the mattress and the body's centre line.
        """
        bp = _vec3(bed_pos)
        d = Vector((math.sin(yaw), -math.cos(yaw), 0.0))                 # foot -> pillow
        hip = bp + d * (0.5 - self.sleep_shift + self.leg_len)
        self.place(frame, (hip.x, hip.y, bp.z), yaw + math.pi)
        _cut(self.hips, _ROT, 0, frame, math.radians(-90.0))
        _cut(self.hips, _LOC, 2, frame, lift)
        face = bp + d * (0.5 - self.sleep_shift + self.eye_height) + Vector((0.0, 0.0, lift + self.back_depth))
        self._lying.append((frame, face))

    def show(self, frame, visible=True):
        """Key render (and viewport) visibility of the whole rig and any held item from `frame` on."""
        for ob in self.objects():
            for path in ("hide_render", "hide_viewport"):
                fc = _ensure(ob, path, 0)
                if not len(fc.keyframe_points):                         # first key: pin the state it had until now
                    _put(fc, min(frame, 1) - 1, 1.0 if getattr(ob, path) else 0.0, "CONSTANT")
                _put(fc, frame, 0.0 if visible else 1.0, "CONSTANT")
                fc.update()

    # ------------------------------------------------------------------ locomotion
    def walk(self, frame, points, speed=None, run=False, from_current=False):
        """Travel along the polyline `points` (units/s: 1.6 walking, 4.4 with run=True) with leg cycle and bob; returns the end frame."""
        if speed is None:
            speed = RUN_SPEED if run else WALK_SPEED
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
                    _cut(self.root, _LOC, i, f0, path[0][i], hold_rest=False)
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
                _cut(self.root, _LOC, i, f0, path[0][i], hold_rest=False)
        if teleport or _cut_at(self.root, _LOC, 0, f0):
            _cut(self.root, _ROT, 2, f0, yaws[0], hold_rest=False)                    # starting on a cut: already facing the way it goes
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

        # legs: swing in opposition, whole number of half-cycles so they end neutral. The run uses the game's full
        # villager swing (0.7 rad at walk-animation speed 1) and a step that keeps the feet from sliding.
        player = self.kind == "player"
        if run:
            amp, step = (0.90 if player else 0.70), (1.10 if player else 0.92) * self.stride
        else:
            amp, step = (0.52 if player else 0.45), (0.70 if player else 0.60) * self.stride
        nh = max(1, int(round(total / step)))
        if n / nh < 2.5:
            nh = max(1, int(n / 2.5))
        hl = n / nh
        amp *= min(1.0, total / nh / step)                              # a very short hop gets a small step
        mids = [f0 + (k + 0.5) * hl for k in range(nh)]
        sign = [self._foot * (-1) ** k for k in range(nh)]
        if nh % 2:
            self._foot = -self._foot

        def cycle(ob, index, a, base=0.0):
            """One smooth swing per step around `base`, alternating sides, back to `base` at the end."""
            keys = [(f0, None)] + [(t, base + s * a) for t, s in zip(mids, sign)] + [(f1, base)]
            _segment(ob, _ROT, index, keys, "BEZIER")

        cycle(self.leg_l, 0, -amp)
        cycle(self.leg_r, 0, amp)
        cycle(self.body, 1, math.radians(2.2 if run else 1.4))          # side-to-side waddle
        if player:                                                      # arms swing against the legs (cos * 2.0 * 0.5 in game)
            a_arm = amp * (1.0 / 1.4)
            for arm, s in ((self.arm_r, -1.0), (self.arm_l, 1.0)):
                rest = self._rest(arm, _ROT, 0)
                if abs(_val(arm, _ROT, 0, f0) - rest) > 0.2:             # a raised/posed arm keeps its pose
                    continue
                holding = self.held is not None and arm is self.arm_r   # a hand with an item swings half as far
                cycle(arm, 0, s * a_arm * (0.5 if holding else 1.0), rest)

        # bob: hips drop when the legs are spread so the feet stay on the ground (never above standing height)
        rest_z = self._rest(self.hips, _LOC, 2)
        drop = self.leg_len * (1.0 - math.cos(amp)) * (0.5 if run else 0.9)
        bkeys = [(f0, None)]
        for k in range(nh):
            bkeys.append((mids[k], rest_z - drop))
            if k < nh - 1:
                bkeys.append((f0 + (k + 1) * hl, rest_z))
        bkeys.append((f1, rest_z))
        _segment(self.hips, _LOC, 2, bkeys, "BEZIER")

        if run:
            lean = math.radians(8.0)
            ramp = min(5.0, n / 3.0)
            _segment(self.body, _ROT, 0, [(f0, None), (f0 + ramp, lean), (f1 - ramp, lean), (f1, 0.0)])
            p0 = _val(self.head, _ROT, 0, f0)
            pr, wob = p0 - 0.7 * lean, math.radians(3.0)
            hkeys = [(f0, None)]
            for k in range(nh):
                hkeys.append((mids[k], pr + wob))
                if k < nh - 1:
                    hkeys.append((f0 + (k + 1) * hl, pr - wob))
            hkeys.append((f1, p0))
            _segment(self.head, _ROT, 0, hkeys, "BEZIER")
            if self.arms is not None:
                rest = self._rest(self.arms, _ROT, 0)
                akeys = [(f0, None)] + [(t, rest + s * math.radians(2.5)) for t, s in zip(mids, sign)] + [(f1, rest)]
                _segment(self.arms, _ROT, 0, akeys, "BEZIER")
        return f1

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
        """Keep the character alive between frame_start and frame_end: head glances, weight shifts, arm bob (seeded)."""
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
            return side[0] * r.uniform(0.6, 1.0) * math.radians(1.2)

        wander(self.body, _ROT, 1, roll, (4, 24), (24, 70), (16, 27))
        shift = 0.008 * self.stride
        wander(self.hips, _LOC, 0, lambda b: r.uniform(-1.0, 1.0) * shift, (4, 24), (24, 70), (16, 27))
        if self.arms is not None:                                       # crossed arms: slow breathing drift
            wander(self.arms, _ROT, 0, lambda b: b + r.uniform(-1.0, 1.0) * math.radians(1.0), (2, 12), (6, 20), (18, 30))
            return
        # player: the game's idle arm bob (AnimationUtils.bobArms), sampled every 6 frames
        phase = float(r.uniform(0.0, 40.0))
        ramp = max(1.0, min(12.0, (f1 - f0) / 3.0))
        for arm, sgn in ((self.arm_r, 1.0), (self.arm_l, -1.0)):
            by, bx = _val(arm, _ROT, 1, f0), _val(arm, _ROT, 0, f0)
            ky, kx = [(f0, None)], [(f0, None)]
            for f in range(f0 + 6, f1 - 5, 6):
                ticks = (f - f0) * 20.0 / FPS + phase
                env = min(1.0, (f - f0) / ramp, (f1 - f) / ramp)
                ky.append((f, by + sgn * 0.05 * math.cos(ticks * 0.09) * env))
                kx.append((f, bx + sgn * 0.05 * math.sin(ticks * 0.067) * env))
            ky.append((f1, by))
            kx.append((f1, bx))
            _segment(arm, _ROT, 1, ky, "BEZIER")
            _segment(arm, _ROT, 0, kx, "BEZIER")

    def shiver(self, frame_start, frame_end, seed=0, amount=1.0):
        """Frightened tremble between frame_start and frame_end: hunched, head tucked, quick small shakes (seeded)."""
        f0, f1 = int(frame_start), int(frame_end)
        if f1 - f0 < 6:
            return
        r = pix.rng(4241 * (int(seed) + 1) + 7)
        ramp = min(6, (f1 - f0) // 3)
        for ob, off in ((self.body, math.radians(5.0)), (self.head, math.radians(9.0))):
            base = _val(ob, _ROT, 0, f0)
            _segment(ob, _ROT, 0, [(f0, None), (f0 + ramp, base + off * amount), (f1 - ramp, base + off * amount), (f1, base)])
        if self.arms is not None:
            base = _val(self.arms, _ROT, 0, f0)
            _segment(self.arms, _ROT, 0, [(f0, None), (f0 + ramp, base - 0.08 * amount), (f1 - ramp, base - 0.08 * amount), (f1, base)])
        twist, slide = [(f0, None)], [(f0, None)]
        for n, f in enumerate(range(f0 + 2, f1 - 1, 2)):
            sgn = 1.0 if n % 2 else -1.0
            twist.append((f, sgn * r.uniform(0.5, 1.0) * math.radians(2.4) * amount))
            slide.append((f, sgn * r.uniform(0.4, 1.0) * 0.009 * self.stride * amount))
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
        """No-op kept for old scripts: Minecraft characters have no eyelids. Returns frame + frames."""
        return frame + frames

    def close_eyes(self, frame, closed=True):
        """No-op kept for old scripts: Minecraft characters sleep with their eyes open."""
        return frame

    def nod(self, frame):
        """Two quick nods (14 frames); returns the end frame."""
        _offsets(self.head, _ROT, 0, frame, [(3, 0.30), (7, -0.06), (10, 0.22), (14, 0.0)],
                 -HEAD_PITCH_MAX - 0.21, HEAD_PITCH_MAX + 0.21)
        return frame + 14

    def shake(self, frame):
        """Say no. Villager: the game's refusal (head bowed 0.4 rad, rolling +-0.3 rad; 25 frames). Player: left-right turn (18 frames)."""
        if self.kind != "villager":
            _offsets(self.head, _ROT, 2, frame, [(3, 0.38), (8, -0.38), (13, 0.24), (18, 0.0)],
                     -HEAD_YAW_MAX - 0.2, HEAD_YAW_MAX + 0.2)
            return frame + 18
        n = 25                                                          # three half-swings of sin(0.45 * tick)
        roll = [(frame, None)]
        for f in range(2, n, 2):
            roll.append((frame + f, 0.3 * math.sin(0.45 * f * 20.0 / FPS)))
        roll.append((frame + n, 0.0))
        _segment(self.head, _ROT, 1, roll, "BEZIER")
        base = _val(self.head, _ROT, 0, frame)
        _segment(self.head, _ROT, 0, [(frame, None), (frame + 4, 0.4), (frame + n - 5, 0.4), (frame + n, base)])
        return frame + n

    def flinch(self, frame):
        """Startled hop then duck and recover (12 frames, airborne around frame+2); returns the end frame."""
        k = self.stride
        _offsets(self.hips, _LOC, 2, frame, [(2, 0.11 * k), (5, -0.04 * k), (12, 0.0)])
        _offsets(self.body, _ROT, 0, frame, [(2, -0.10), (5, 0.13), (12, 0.0)])
        _offsets(self.head, _ROT, 0, frame, [(2, -0.26), (5, 0.20), (12, 0.0)])
        _offsets(self.leg_l, _ROT, 0, frame, [(2, 0.16), (5, -0.10), (12, 0.0)])
        _offsets(self.leg_r, _ROT, 0, frame, [(2, 0.16), (5, 0.12), (12, 0.0)])
        if self.arms is not None:
            _offsets(self.arms, _ROT, 0, frame, [(2, -0.22), (6, 0.05), (12, 0.0)])
        else:
            _offsets(self.arm_l, _ROT, 0, frame, [(2, -0.55), (6, -0.20), (12, 0.0)])
            _offsets(self.arm_r, _ROT, 0, frame, [(2, -0.55), (6, -0.20), (12, 0.0)])
            _offsets(self.arm_l, _ROT, 1, frame, [(2, -0.30), (6, -0.12), (12, 0.0)])
            _offsets(self.arm_r, _ROT, 1, frame, [(2, 0.30), (6, 0.12), (12, 0.0)])
        return frame + 12

    def swing_arm(self, frame):
        """Player: the game's right-arm swing (8 frames, arm furthest forward at frame+2). Villager: small jolt of the folded arms (9 frames)."""
        if self.arm_r is None:
            _offsets(self.arms, _ROT, 0, frame, [(2, -0.20), (5, 0.06), (9, 0.0)])
            _offsets(self.head, _ROT, 0, frame, [(3, 0.13), (9, 0.0)], -HEAD_PITCH_MAX - 0.21, HEAD_PITCH_MAX + 0.21)
            return frame + 9
        n = 8                                                           # 6 game ticks at 24 fps
        head_pitch = _val(self.head, _ROT, 0, frame)
        twist, ax, ay, az = [], [], [], []
        for f in range(1, n):
            t = f / float(n)                                            # HumanoidModel.setupAttackAnimation
            body = math.sin(math.sqrt(t) * 2.0 * math.pi) * 0.2
            g = math.sin((1.0 - (1.0 - t) ** 4) * math.pi)
            h = math.sin(t * math.pi) * (0.7 - head_pitch) * 0.75
            twist.append((f, -body))
            ax.append((f, -(g * 1.2 + h)))
            az.append((f, -2.0 * body))
            ay.append((f, -0.4 * math.sin(t * math.pi)))
        for ob, index, offs in ((self.body, 2, twist), (self.arm_r, 0, ax), (self.arm_r, 2, az), (self.arm_r, 1, ay),
                                (self.head, 2, [(f, -v) for f, v in twist])):   # the head does not turn with the body
            _offsets(ob, _ROT, index, frame, offs + [(n, 0.0)], -1.95, 1.95, interp="BEZIER")   # never past overhead
        return frame + n

    def raise_arm(self, frame, angle=65.0, ease=8, side="r"):
        """Player: ease an arm to `angle` degrees forward of hanging (0 = down, 90 = straight out) and hold it there."""
        arm = self.arm_r if side == "r" else self.arm_l
        if arm is None:
            arm = self.arms
            value = self._rest(arm, _ROT, 0) - math.radians(angle) * 0.25
        else:
            value = -math.radians(angle)
        _ease(arm, _ROT, 0, frame, frame + max(0, ease), value)
        return frame + max(0, ease)

    def hold(self, obj, offset=None, rotation=None):
        """Put an item sprite in the player's right hand (or on a villager's crossed arms) as the game does; hold(None) lets go.

        `obj` is a flat item as engine.props.make_item builds it (origin at the sprite centre, sprite in its local XZ
        plane, 16 px = 1 unit). The player then carries the right arm 18 degrees forward (the game's item pose), so
        call hold() before animating. offset / rotation override the vanilla placement (parent-space values).
        """
        if self.held is not None and self.held is not obj:
            self.held.parent = None
            self.held = None
        if self.arm_r is not None:
            self._set_rest(self.arm_r, _ROT, 0, ITEM_ARM_PITCH if obj is not None else 0.0)
        if obj is None:
            return None
        hand, kind = (self.arm_r, "hand") if self.arm_r is not None else (self.arms, "arms")
        obj.parent = hand
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = _held_matrix(kind, self.model_scale)
        if offset is not None:
            obj.location = offset
        if rotation is not None:
            obj.rotation_euler = rotation
        self.held = obj
        return obj


# ----------------------------------------------------------------------------------------------------
# factories
# ----------------------------------------------------------------------------------------------------
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


def make_villager(name, profession="farmer", child=False, collection=None, biome="plains", level=1):
    """Build a vanilla villager (feet at the origin, facing -Y) wearing the game's textures for `profession`.

    profession: any of villager_professions() (farmer, librarian, toolsmith, ..., nitwit) or 'none' (unemployed).
    child=True builds the game's baby villager model (babies show no profession). level 1..5 picks the belt badge
    (stone, iron, gold, emerald, diamond). biome picks textures/entity/villager/type/<biome>.png.
    """
    profession = PROFESSION_ALIASES.get(profession, profession)
    if profession not in villager_professions():
        raise ValueError("unknown profession %r (use one of %s)" % (profession, ", ".join(villager_professions())))
    spec = _baby_villager_spec() if child else _villager_spec()
    key, sheet = villager_sheet(profession, biome=biome, level=level, child=child)
    parts = _build_rig(name, spec, sheet, _sheet_material(key, sheet), _collection(collection),
                       _sheet_material_two_sided(key, sheet))
    return Character(name, "villager", parts, spec, profession=profession, child=child)


def make_player(name="player", skin="steve", collection=None):
    """Build the player (1.875 tall, feet at the origin, facing -Y) with textures/entity/player/wide/<skin>.png, both skin layers."""
    spec = _player_spec()
    key, sheet = player_sheet(skin)
    parts = _build_rig(name, spec, sheet, _sheet_material(key, sheet), _collection(collection))
    return Character(name, "player", parts, spec)


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _test_material(name, texture, tint=None):
    """Stand-in set material: a real block texture (tiles with REPEAT, optional biome tint) or a flat (r, g, b) colour."""
    if isinstance(texture, str):
        arr = _game_texture(texture).astype(np.float32)
    else:
        arr = np.full((1, 1, 4), 255.0, dtype=np.float32)
        arr[0, 0, :3] = texture
    if tint is not None:
        arr[..., :3] *= np.array(tint, dtype=np.float32) / 255.0
    return pix.pixel_material(name, _memory_image(name, np.clip(arr, 0, 255).astype(np.uint8)))


def _test_box(name, lo, hi, material, tile=1.0):
    """Stand-in box from corner lo to corner hi, its faces tiled with `material` every `tile` units."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    quads = [
        ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), 0, 2), ((x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1), 0, 2),
        ((x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1), 1, 2), ((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1), 1, 2),
        ((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), 0, 1), ((x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0), 0, 1),
    ]
    verts, faces, uvs = [], [], []
    for q in quads:
        n = len(verts)
        verts.extend(q[:4])
        faces.append((n, n + 1, n + 2, n + 3))
        uvs.extend((p[q[4]] / tile, p[q[5]] / tile) for p in q[:4])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    layer = me.uv_layers.new(name="UVMap")
    layer.data.foreach_set("uv", [x for uv in uvs for x in uv])
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _selftest(which):
    from . import quick

    mats = {}

    def stage(preset="golden"):
        """Fresh test scene with the quick light rig and a grass floor made of the real block texture."""
        scene = quick.reset()
        quick.setup(scene)
        quick.light(scene, preset)
        mats.clear()
        mats["grass"] = _test_material("cast_test_grass", "block/grass_block_top", (145, 189, 89))
        mats["stone"] = _test_material("cast_test_stone", "block/stone_bricks")
        mats["planks"] = _test_material("cast_test_planks", "block/oak_planks")
        mats["wool"] = _test_material("cast_test_wool", "block/red_wool")
        mats["white"] = _test_material("cast_test_white", "block/white_wool")
        _test_box("cast_test_ground", (-40.0, -40.0, -1.0), (40.0, 40.0, 0.0), mats["grass"])
        return scene

    def want(name):
        """True when this still was asked for (no arguments = all of them)."""
        return not which or name in which

    cast = [("farmer", "farmer", False), ("librarian", "librarian", False), ("toolsmith", "toolsmith", False),
            ("cleric", "cleric", False), ("shepherd", "shepherd", False), ("none", "none", False),
            ("nitwit", "nitwit", False), ("kid", "none", True), ("steve", None, False)]

    if want("check"):                                                   # keyframes read back, no rendering
        scene = stage()
        v = make_villager("probe", "farmer")
        v.place(1, (0.0, 0.0, 0.0), 0.0)
        end = v.walk(1, [(0.0, 0.0, 0.0), (0.0, -6.0, 0.0), (3.0, -6.0, 0.0)], run=True)
        v.look_at(end, (3.0, 0.0, 1.6))
        print("height", round(v.height, 4), "eye", round(v.eye_height, 4), "run ends", end)
        print("root x keys", read_keys(v.root, _LOC, 0))
        print("root y keys", read_keys(v.root, _LOC, 1))
        print("yaw keys", read_keys(v.root, _ROT, 2))
        print("leg_l keys", read_keys(v.leg_l, _ROT, 0)[:8])
        for f in (1, 5, 9, 13, end):
            scene.frame_set(f)
            bpy.context.view_layer.update()
            print("frame", f, "root", tuple(round(c, 3) for c in v.root.matrix_world.translation),
                  "leg_l x", round(v.leg_l.rotation_euler.x, 3), "head z", round(v.head.matrix_world.translation.z, 3))
        p = make_player("probe_player")
        p.place(1, (2.0, 0.0, 0.0), 0.0)
        p.swing_arm(10)
        print("player height", round(p.height, 4), "arm keys", read_keys(p.arm_r, _ROT, 0))
        for keys in (read_keys(v.root, _LOC, 0), read_keys(v.leg_l, _ROT, 0), read_keys(p.arm_r, _ROT, 0)):
            assert keys[-1][2] == "CONSTANT", "segments must end on a CONSTANT key"
        first = read_keys(v.root, _LOC, 0)[0]
        assert first[2] == "CONSTANT" and first[0] == 1 - CUT_LEAD, "place() must be a CONSTANT key CUT_LEAD early"
        # regression: look.setup_render exposes frame f over [f, f + SHUTTER]. A cut for frame f must not show anywhere
        # in the exposure of frame f - 1 (it did with CUT_LEAD = 0.5: the last frame before every cut was a ghost)
        # and must hold from frame f on.
        assert 0.03 < CUT_LEAD < 1.0 - SHUTTER, "CUT_LEAD must lie strictly inside (0.03, 1 - shutter)"
        c = make_villager("cutter", "farmer")
        c.place(1, (5.0, -7.0, 0.0), 0.0)
        c.walk(1, [(5.0, -7.0, 0.0), (5.0, -9.0, 0.0)])                 # still walking when the next cut comes
        c.place(13, (13.5, -9.5, 1.0), 1.0)
        c.lie_down(25, (2.0, 2.0, 0.5625), 0.0)
        c.look_at(31, (9.0, 2.0, 1.0), ease=0)

        def state():
            return (tuple(round(a, 5) for a in c.root.location), round(c.root.rotation_euler.z, 5),
                    round(c.hips.rotation_euler.x, 5), round(c.head.rotation_euler.z, 5))

        for cut in (13, 25, 31):
            scene.frame_set(cut - 1, subframe=SHUTTER)                  # the last instant frame cut-1 is exposed
            before = state()
            scene.frame_set(cut - 1, subframe=min(0.999, 1.0 - CUT_LEAD - 0.04))   # just before the hold key
            late = state()
            scene.frame_set(cut)
            after = state()
            assert after != before, "the cut at frame %d changed nothing" % cut
            moved = max(abs(a - b) for a, b in zip(before[0], late[0]))
            assert moved < 0.2 and before[1:] == late[1:], \
                "the cut keyed for frame %d is visible inside the exposure of frame %d" % (cut, cut - 1)
            scene.frame_set(cut, subframe=SHUTTER)
            assert state() == after, "the pose must hold through the exposure of frame %d" % cut
        scene.frame_set(1)
        # look_at(frame, <parented Object>) must aim at where the object is AT that frame, not at the current frame
        w1 = make_villager("passer", "farmer")
        w1.place(1, (-6.0, -3.0, 0.0), math.radians(90))
        w1.walk(1, [(-6.0, -3.0, 0.0), (6.0, -3.0, 0.0)])
        st = make_player("looker")
        st.place(1, (0.0, 0.0, 0.0), 0.0)
        scene.frame_set(1)
        by_char, by_head, by_part = st._aim(w1, 60)[0], st._aim(w1.head, 60)[0], st._aim(w1.arms, 60)[0]
        assert abs(by_char - by_head) < 1e-4 and abs(by_char - by_part) < 0.05, (by_char, by_head, by_part)
        assert scene.frame_current == 1
        print("check ok")

    if want("lineup") or want("back") or want("side"):
        scene = stage()
        tier, depth = 2.25, 1.0
        _test_box("cast_test_step1", (-2.2, 0.5, 0.0), (2.2, 3.5, tier), mats["stone"])
        _test_box("cast_test_step2", (-2.2, 0.5 + depth, tier), (2.2, 3.5, 2 * tier), mats["stone"])
        chars = []
        for n, (nm, prof, kid) in enumerate(cast):
            ch = make_player(nm) if prof is None else make_villager(nm, prof, child=kid)
            j, i = 2 - n // 3, n % 3
            ch.place(1, ((i - 1) * 1.3, j * depth, j * tier), 0.0)
            chars.append(ch)
        scene.frame_set(1)
        if want("lineup"):
            quick.camera(scene, (-5.5, -15.0, 4.3), (0.0, 1.0, 3.25), lens=52)
            print("wrote", quick.render(scene, "characters_lineup"))
        if want("side"):                                                 # same stage, everyone turned into profile
            for n, ch in enumerate(chars):
                ch.place(2, ch.pos_at(1), math.radians(90 if n % 3 != 2 else -90))
            scene.frame_set(2)
            quick.camera(scene, (-2.0, -15.8, 4.3), (0.0, 1.0, 3.25), lens=52)
            print("wrote", quick.render(scene, "characters_side"))
            scene.frame_set(1)
        if want("back"):
            for ob in list(scene.objects):
                if ob.name.startswith("cast_test_step"):
                    ob.hide_render = True
            for j in (1, 2):                                             # thin floors only, so the backs stay visible
                _test_box("cast_test_floor%d" % j, (-2.2, -0.6 + j * depth, j * tier - 0.08),
                          (2.2, 0.6 + j * depth, j * tier), mats["stone"])
            quick.camera(scene, (5.0, 17.5, 4.6), (0.0, 1.0, 3.25), lens=52)
            scene.objects["quick_sun"].rotation_euler[2] = math.radians(150)
            print("wrote", quick.render(scene, "characters_back"))

    if want("faces"):
        scene = stage()
        a = make_villager("nitwit", "nitwit")
        b = make_villager("farmer", "farmer")
        a.place(1, (-0.36, 0.0, 0.0), math.radians(-10))
        b.place(1, (0.52, 0.35, 0.0), math.radians(-30))
        cam = (-0.75, -3.7, 1.78)
        a.look_at(1, cam, ease=0)
        b.look_at(1, (-0.2, -3.0, 1.7), ease=0)
        scene.frame_set(1)
        quick.camera(scene, cam, (0.1, 0.1, 1.66), lens=38, fstop=8.0)
        print("wrote", quick.render(scene, "characters_faces"))

    if want("run"):
        scene = stage()
        _test_box("cast_test_wall", (-12.0, 3.0, 0.0), (12.0, 4.0, 3.0), mats["stone"])
        v = make_villager("runner", "farmer")
        v.place(1, (-6.0, 0.0, 0.0), math.radians(90))
        end = v.walk(1, [(-6.0, 0.0, 0.0), (6.0, 0.0, 0.0)], run=True)
        w = make_villager("walker", "librarian")
        w.place(1, (-1.5, 1.8, 0.0), math.radians(90))
        w.walk(1, [(-1.5, 1.8, 0.0), (6.0, 1.8, 0.0)])
        print("run ends at frame", end, "| leg keys:", read_keys(v.leg_l, _ROT, 0)[:6])
        off = Vector((2.6, -5.0, 0.7))                                 # low camera tracking with the runner
        cam = quick.camera(scene, v.pos_at(1) + off, v.pos_at(1) + Vector((0.3, 0.0, 1.05)), lens=40, fstop=4.0)
        for i in range(3):
            _segment(cam, _LOC, i, [(1, (v.pos_at(1) + off)[i]), (end, (v.pos_at(end) + off)[i])], "LINEAR")
        scene.render.use_motion_blur = True
        for n, f in enumerate((13, 16, 19)):
            scene.frame_set(f)
            print("wrote", quick.render(scene, "characters_run_%d" % (n + 1)))

    def emerald():
        """The real emerald item if engine.props can build it, else a flat green stand-in of the same size."""
        try:
            from . import props

            ob = props.make_item("emerald")
            if ob.name not in bpy.context.scene.collection.all_objects:
                bpy.context.scene.collection.objects.link(ob)
            return ob
        except Exception as exc:                                        # props is another role's module
            print("props.make_item unavailable (%s): using a stand-in" % exc)
            return _test_box("cast_test_gem", (-0.3, -0.03, -0.35), (0.3, 0.03, 0.35), _test_material("cast_test_gem", (23, 221, 98)))

    if want("swing"):
        scene = stage()
        pl = make_player("steve")
        pl.place(1, (0.0, 0.0, 0.0), math.radians(-35))
        pl.look_at(1, (1.5, -3.0, 1.2), ease=0)
        pl.swing_arm(10)
        v = make_villager("watcher", "toolsmith")
        v.place(1, (1.5, 1.2, 0.0), math.radians(60))
        v.look_at(1, pl, ease=0)
        scene.render.use_motion_blur = True
        scene.frame_set(12)
        quick.camera(scene, (-2.4, -5.6, 1.5), (0.4, 0.3, 1.0), lens=40, fstop=2.8)
        print("wrote", quick.render(scene, "characters_player_swing"))

    if want("hold"):
        scene = stage()
        pl = make_player("steve")
        pl.hold(emerald())
        pl.place(1, (-0.62, 0.0, 0.0), math.radians(62))
        v = make_villager("trader", "librarian")
        v.place(1, (0.72, 0.1, 0.0), math.radians(-75))
        v.hold(emerald())
        pl.raise_arm(1, 40, ease=0)
        pl.look_at(1, v, ease=0)
        v.look_at(1, pl, ease=0)
        scene.frame_set(1)
        quick.camera(scene, (-0.4, -5.4, 1.5), (0.05, 0.0, 1.05), lens=36, fstop=5.6)
        print("wrote", quick.render(scene, "characters_hold"))

    if want("sleep"):
        scene = stage()
        sleepers = (make_player("steve"), make_villager("sleeper", "cleric"))
        for i, ch in enumerate(sleepers):                                # stand-in beds: 1 x 2 x 9/16 like the game's
            x = i * 1.4
            _test_box("cast_test_bed%d" % i, (x - 0.5, -1.0, 3.0 / 16.0), (x + 0.5, 1.0, 9.0 / 16.0), mats["wool"])
            _test_box("cast_test_pillow%d" % i, (x - 0.502, 0.5, 3.0 / 16.0), (x + 0.502, 1.002, 9.0 / 16.0 + 0.002), mats["white"])
            for lx in (-0.5, 0.3125):
                for ly in (-1.0, 0.8125):
                    _test_box("cast_test_bedleg%d" % i, (x + lx, ly, 0.0), (x + lx + 0.1875, ly + 0.1875, 3.0 / 16.0), mats["planks"])
            ch.lie_down(1, (x, 0.0, 9.0 / 16.0), math.radians(180))      # pillow toward +Y
        scene.frame_set(1)
        quick.camera(scene, (-2.4, -3.9, 3.7), (0.62, 0.05, 0.45), lens=30, fstop=4.0)
        print("wrote", quick.render(scene, "characters_sleep"))


if __name__ == "__main__":
    _selftest(set(sys.argv[1:]))
