"""Independent checker probe for engine/players.py (numbers only, no rendering).

    $BPY -m tools.check_players_numbers
"""
import math
import sys

import bpy
import numpy as np
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)


def counts():
    return {k: len(getattr(bpy.data, k)) for k in ("objects", "meshes", "materials", "images", "actions", "collections",
                                                   "node_groups", "lights", "cameras")}


before = counts()
from engine import players as pl                      # noqa: E402
from engine import characters as ch                   # noqa: E402

after = counts()
print("IMPORT leaves the scene untouched:", before == after, before, after)

scene = bpy.context.scene
U = 0.9375 / 16.0
FAIL = []


def bad(msg):
    FAIL.append(msg)
    print("  !!", msg)


def bbox(ob):
    bpy.context.view_layer.update()
    pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo / U, hi / U


# ------------------------------------------------------------------ 1. geometry (pixels, feet at 0, facing -Y)
print("\n== geometry (px; x: + = character's left, y: + = back, z: up)")
for skin, slim in (("steve", False), ("alex", True), ("alex", False)):
    p = pl.make_player("g_%s_%d" % (skin, slim), skin, slim=slim)
    p.place(1, (0, 0, 0), 0.0)
    scene.frame_set(1)
    for k in ("head", "torso", "arm_r", "arm_l", "leg_r", "leg_l"):
        lo, hi = bbox(p.parts[k])
        print("  %-6s %-5s slim=%d  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f   pivot %s" % (
            skin, k, slim, lo.x, hi.x, lo.y, hi.y, lo.z, hi.z,
            tuple(round(c / U, 2) for c in p.parts[k].matrix_world.translation)))

# expected base boxes (px) from HumanoidModel/PlayerModel.createMesh, model (x, y down, z) -> (x, z, 24 - y)
p = pl.make_player("g2", "steve")
p.place(1, (0, 0, 0), 0.0)
scene.frame_set(1)
exp = {"head": ((-4, -4, 24), (4, 4, 32)), "torso": ((-4, -2, 12), (4, 2, 24)),
       "arm_r": ((-8, -2, 12), (-4, 2, 24)), "arm_l": ((4, -2, 12), (8, 2, 24)),
       "leg_r": ((-3.9, -2, 0), (0.1, 2, 12)), "leg_l": ((-0.1, -2, 0), (3.9, 2, 12))}
for k, (elo, ehi) in exp.items():
    lo, hi = bbox(p.parts[k])
    # arms carry ARM_SPLAY? check rotation
    for a, b, name in ((lo, elo, "lo"), (hi, ehi, "hi")):
        d = [a[i] - b[i] for i in range(3)]
        if max(abs(x) for x in d) > 0.6:
            bad("geometry %s %s differs from the class by %s px" % (k, name, [round(x, 2) for x in d]))
print("  arm rest rotations:", tuple(round(a, 4) for a in p.arm_r.rotation_euler), tuple(round(a, 4) for a in p.arm_l.rotation_euler))


# ------------------------------------------------------------------ 2. UV spot checks
def face_uv(ob, normal, sheet=(64, 64), tol=0.9, where=None):
    """Texel rectangle (u0, v0, u1, v1) covered by the faces of `ob` whose local normal is `normal`, and the texel
    under the corner (min x or y, max z)."""
    us, vs = [], []
    me = ob.data
    uvl = me.uv_layers[0].data
    corner = []
    for poly in me.polygons:
        if poly.normal.dot(Vector(normal)) < tol:
            continue
        if where is not None and not where(poly.center):
            continue
        for li in poly.loop_indices:
            uv = uvl[li].uv
            co = me.vertices[me.loops[li].vertex_index].co
            us.append(uv[0] * sheet[0])
            vs.append((1 - uv[1]) * sheet[1])
            corner.append((co.copy(), uv[0] * sheet[0], (1 - uv[1]) * sheet[1]))
    return (min(us), min(vs), max(us), max(vs)), corner


print("\n== UV: front faces (viewer's left = character's right = Blender -x must be the LOW u)")
checks = [("head", (0, -1, 0), (8, 8, 16, 16), lambda c: abs(c.y + 4 * U) < 1e-4),
          ("torso", (0, -1, 0), (20, 20, 28, 32), lambda c: abs(c.y + 2 * U) < 1e-4),
          ("arm_r", (0, -1, 0), (44, 20, 48, 32), lambda c: abs(c.y + 2 * U) < 1e-4),
          ("arm_l", (0, -1, 0), (36, 52, 40, 64), lambda c: abs(c.y + 2 * U) < 1e-4),
          ("leg_r", (0, -1, 0), (4, 20, 8, 32), lambda c: abs(c.y + 2 * U) < 1e-4),
          ("leg_l", (0, -1, 0), (20, 52, 24, 64), lambda c: abs(c.y + 2 * U) < 1e-4),
          ("arm_r", (-1, 0, 0), (40, 20, 44, 32), lambda c: abs(c.x + 3 * U) < 1e-4),      # outer side of the right arm
          ("arm_r", (0, 1, 0), (52, 20, 56, 32), lambda c: abs(c.y - 2 * U) < 1e-4),       # back
          ("head", (0, 1, 0), (24, 8, 32, 16), lambda c: abs(c.y - 4 * U) < 1e-4),
          ("head", (0, 0, 1), (8, 0, 16, 8), lambda c: abs(c.z - 8 * U) < 1e-4)]
for part, n, want, where in checks:
    ob = p.parts[part]
    rect, corner = face_uv(ob, n, where=where)
    ok = all(abs(a - b) < 0.05 for a, b in zip(rect, want))
    # orientation: the vertex with the lowest local x (or highest y for side faces) and highest z
    if n[1] == -1:
        c = min(corner, key=lambda t: (t[0].x, -t[0].z))
        orient = abs(c[1] - want[0]) < 0.05 and abs(c[2] - want[1]) < 0.05
    elif n[1] == 1:                                       # back: seen from behind, viewer's left = character's left
        c = max(corner, key=lambda t: (t[0].x, t[0].z))
        orient = abs(c[1] - want[0]) < 0.05 and abs(c[2] - want[1]) < 0.05
    else:
        orient = True
    print("  %-6s normal %s  texels %s  want %s  %s  orientation %s" % (part, n, tuple(round(r, 2) for r in rect), want,
                                                                    "ok" if ok else "WRONG", "ok" if orient else "WRONG"))
    if not ok or not orient:
        bad("UV of %s face %s" % (part, n))

# hat / overlay texel counts of every skin (the report says: no hat-layer texels)
print("\n== opaque texels per overlay region (wide sheets)")
for skin in pl.SKINS:
    arr = np.array(ch._game_texture("entity/player/wide/" + skin))
    op = arr[..., 3] >= 26
    print("  %-7s hat %4d  jacket %4d  r_sleeve %4d  l_sleeve %4d  r_pants %4d  l_pants %4d   semi-transparent %d" % (
        skin, op[0:16, 32:64].sum(), op[32:48, 16:40].sum(), op[32:48, 40:56].sum(), op[48:64, 48:64].sum(),
        op[32:48, 0:16].sum(), op[48:64, 0:16].sum(), ((arr[..., 3] > 0) & (arr[..., 3] < 255)).sum()))

# herobrine eyes: which texels of steve.png are the eyes?
arr = np.array(ch._game_texture("entity/player/wide/steve"))
print("\n== steve.png face rows 11..13 (u 8..15):")
for v in (11, 12, 13):
    print("   v=%d " % v + " ".join("%02x%02x%02x" % tuple(arr[v, u, :3]) for u in range(8, 16)))
key, sheet, mask = pl.skin_sheet("herobrine")
diff = np.argwhere((sheet != arr).any(axis=2))
print("   herobrine changes texels (v, u):", diff.tolist())


# ------------------------------------------------------------------ 3. held items: my own chain from the classes
def R(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    if axis == "x":
        m[1, 1], m[1, 2], m[2, 1], m[2, 2] = c, -s, s, c
    elif axis == "y":
        m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c
    else:
        m[0, 0], m[0, 1], m[1, 0], m[1, 1] = c, -s, s, c
    return m


def T(x, y, z):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def S(x, y, z):
    return np.diag([x, y, z, 1.0])


def game_item_point(item_xyz, display, left, arm_pivot_px, arm_rot, slim=False, extra=None):
    """World (Blender) position of a point of the item cube (0..1, y up) for an entity at the origin with body yaw 0
    (facing Blender -Y), following LivingEntityRenderer + ItemInHandLayer + ItemTransform.apply."""
    rot, trans, sc = display
    s = -1.0 if left else 1.0
    px = arm_pivot_px[0] + (0.5 * s if slim else 0.0)        # PlayerModel.translateToHand (slim): RIGHT arm +0.5
    xr, yr, zr = arm_rot
    arm = T(px / 16.0, arm_pivot_px[1] / 16.0, arm_pivot_px[2] / 16.0) @ R("z", math.degrees(zr)) @ R("y", math.degrees(yr)) @ R("x", math.degrees(xr))
    layer = R("x", -90) @ R("y", 180) @ T(s * 1 / 16.0, 2 / 16.0, -10 / 16.0)
    disp = (T(s * trans[0] / 16.0, trans[1] / 16.0, trans[2] / 16.0) @ R("x", rot[0]) @ R("y", s * rot[1]) @ R("z", s * rot[2])
            @ S(*sc) @ T(-0.5, -0.5, -0.5))
    m = arm @ layer @ disp
    if extra is not None:
        m = m @ extra
    q = m @ np.array([item_xyz[0], item_xyz[1], item_xyz[2], 1.0])
    # model units (1 = 16 px, y down, origin 24 px above the feet... the renderer translates by -1.501)
    x, y, z = q[0] * 16.0, q[1] * 16.0, q[2] * 16.0
    # model px -> Blender: (x, z, 24 - y) * 0.9375 / 16
    return Vector((x, z, 24.0 - y)) * U


def mesh_local(item_xyz):
    """players' item mesh convention: item x -> x, item y (up) -> z, item +z -> -y, centred."""
    return Vector((item_xyz[0] - 0.5, -(item_xyz[2] - 0.5), item_xyz[1] - 0.5))


print("\n== held items: author's object vs my chain (max distance in px of 4 item-cube points)")
P = [(0.0, 0.0, 0.5), (1.0, 0.0, 0.5), (0.0, 1.0, 0.5), (0.5, 0.5, 1.0)]
cases = [("steve", False, "diamond_sword", "right"), ("steve", False, "diamond_sword", "left"),
         ("steve", False, "torch", "right"), ("steve", False, "torch", "left"),
         ("steve", False, "dirt", "right"), ("steve", False, "dirt", "left"), ("steve", False, "bow", "right"),
         ("steve", False, "bow", "left"), ("steve", False, "goat_horn", "right"), ("steve", False, "goat_horn", "left"),
         ("alex", True, "iron_pickaxe", "right"), ("alex", True, "iron_pickaxe", "left"),
         ("steve", False, "shield", "left"), ("steve", False, "shield", "right")]
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def raw_display(model, ctx):
    """thirdperson display by walking the parents myself, with the deserializer's rule: a JSON without a left-hand
    entry uses ITS OWN right-hand entry for the left hand."""
    name = model
    while name:
        path = os.path.join(ROOT, "assets/mc/assets/minecraft/models", name.replace("minecraft:", "") + ".json")
        if not os.path.exists(path):
            return None
        d = json.load(open(path))
        disp = d.get("display", {})
        g = disp.get(ctx)
        if g is None and ctx == "thirdperson_lefthand":
            g = disp.get("thirdperson_righthand")
        if g is not None:
            return (tuple(g.get("rotation", (0, 0, 0))), tuple(g.get("translation", (0, 0, 0))), tuple(g.get("scale", (1, 1, 1))))
        name = d.get("parent")
    return ((0, 0, 0), (0, 0, 0), (1, 1, 1))


for i, (skin, slim, item, hand) in enumerate(cases):
    q = pl.make_player("h%d" % i, skin, slim=slim)
    q.place(1, (0, 0, 0), 0.0)
    ob = q.hold(item, hand=hand)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    left = hand == "left"
    arm = q.arm_l if left else q.arm_r
    e = arm.rotation_euler
    arm_rot = (e[0], -e[2], e[1])
    model = ("block/" if item == "dirt" else "item/") + item
    disp = raw_display(model, "thirdperson_lefthand" if left else "thirdperson_righthand")
    pivot = (5.0 if left else -5.0, 2.0, 0.0)
    extra = None
    pts = P
    if item == "shield":
        extra = S(1, -1, -1)                                 # items/shield.json "transformation"; then ShieldModel px / 16
        pts = [(-6 / 16, -11 / 16, -2 / 16), (6 / 16, -11 / 16, -2 / 16), (-6 / 16, 11 / 16, -2 / 16), (0, 0, 5 / 16)]
    worst = 0.0
    for pt in pts:
        mine = game_item_point(pt, disp, left, pivot, arm_rot, slim=slim, extra=extra)
        if item == "shield":
            # author's mesh: model px p -> ((p0 - 8) / 16, (p2 + 8) / 16, (-p1 - 8) / 16)
            loc = Vector(((pt[0] * 16 - 8) / 16, (pt[2] * 16 + 8) / 16, (-pt[1] * 16 - 8) / 16))
        else:
            loc = mesh_local(pt)
        theirs = ob.matrix_world @ loc
        worst = max(worst, (mine - theirs).length / U)
    print("  %-6s slim=%d %-14s %-5s display %s  worst %.3f px   arm rot %s" % (skin, slim, item, hand, disp, worst,
                                                                              tuple(round(a, 3) for a in arm_rot)))
    if worst > 0.05:
        bad("held %s in the %s hand (%s) is %.2f px from the game's transform" % (item, hand, "slim" if slim else "wide", worst))
    if item == "diamond_sword":
        grip = ob.matrix_world @ mesh_local((3 / 16, 3 / 16, 0.5))
        tip = ob.matrix_world @ mesh_local((15 / 16, 15 / 16, 0.5))
        d = tip - grip
        print("       sword grip %s tip %s: forward %.2f up %.2f side %.2f; blade pitch %.0f deg above horizontal" % (
            tuple(round(c, 2) for c in grip), tuple(round(c, 2) for c in tip), -d.y, d.z, d.x,
            math.degrees(math.atan2(d.z, -d.y))))

# the item mesh itself: is the sprite the right way round? compare its local bbox with the texture's opaque bbox
print("\n== item sprite orientation (mesh bbox vs texture opaque bbox, px)")
from engine import mcassets as mc                      # noqa: E402

for item in ("iron_axe", "bow", "cooked_chicken", "goat_horn"):
    q = pl.make_player("o_" + item, "steve")
    ob = q.hold(item)
    arr = np.array(mc.texture_array("item/" + item))
    op = arr[..., 3] >= 128
    rows, cols = np.where(op)
    want = (cols.min() - 8, cols.max() + 1 - 8, 8 - rows.max() - 1, 8 - rows.min())
    xs = [v.co.x * 16 for v in ob.data.vertices]
    zs = [v.co.z * 16 for v in ob.data.vertices]
    got = (min(xs), max(xs), min(zs), max(zs))
    ok = all(abs(a - b) < 0.01 for a, b in zip(want, got))
    print("  %-10s mesh x %.1f..%.1f z %.1f..%.1f   texture %s   %s" % ((item,) + tuple(got) + (want, "ok" if ok else "WRONG")))
    if not ok:
        bad("sprite of %s is not the texture the right way round" % item)

print("\nFAILED:" if FAIL else "\nall geometry / UV / item checks passed")
for f in FAIL:
    print("  -", f)
sys.exit(1 if FAIL else 0)
