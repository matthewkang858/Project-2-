"""Separately animatable set pieces built from the same real game models and textures as the block world.

make_bell   - the bell: static frame from the block model + the swinging body (entity/bell/bell_body.png)
make_door   - both halves of a door from the real door models, pivoting on its hinge
make_item   - a held item (thin extruded sprite of the item texture)
make_light  - the warm point light for a torch / lantern

Blender axes: Minecraft east = +X, north = +Y, up = +Z. 1 block = 1 unit.
"""
import math

import bpy

from . import mcassets as mc
from .blocks import block_material

# yaw (rotation about +Z, radians) that turns a model authored facing EAST / with blockstate y=0 to each direction
YAW_FROM_EAST = {"east": 0.0, "north": math.pi / 2, "west": math.pi, "south": -math.pi / 2}
_Y_ROT = {"floor": {"north": 0, "east": 90, "south": 180, "west": 270},
          "ceiling": {"north": 0, "east": 90, "south": 180, "west": 270},
          "single_wall": {"east": 0, "south": 90, "west": 180, "north": 270},
          "double_wall": {"east": 0, "south": 90, "west": 180, "north": 270}}

# Light colours are scene-linear. The torch is a PALE warm white: multiplied into oak planks (162, 130, 78) it must
# leave them oak (saturation <= 0.68), not orange; the orange of a torch comes from its glowing flame texels and
# their bloom. 'fill' is the weak, cool, shadowless light that stands in for bounce light inside a torch-lit room
# (Fast GI drops real bounces), so the far side of a face or a bed is not just black-orange.
TORCH_COLOR = (1.0, 0.88, 0.72)
FILL_COLOR = (0.61, 0.67, 1.0)      # #cdd6ff
LIGHT_ENERGY = {"torch": 110.0, "lantern": 140.0, "fill": 14.0}     # watts of the point light (films may rescale)
LIGHT_RADIUS = {"torch": 0.25, "lantern": 0.25, "fill": 1.2}       # soft-shadow radius
# Light Falloff 'Smooth': intensity = W / (d^2 + smooth) instead of W / d^2. A wall torch's flame is 0.29 block from
# its own wall and a lamp post's from its log: unsmoothed, those faces get 12x the light of a surface one block away
# and clip to white (the block reads as glowstone). With smooth = 1 the block a torch sits on is lit like a surface
# one block away and keeps its texture, as in the game; beyond 2 blocks nothing changes.
LIGHT_SMOOTH = {"torch": 1.0, "lantern": 1.0, "fill": 4.0}
# where the flame sits inside its block cell, in model pixels (x east, y up, z south), for blockstate y = 0
FLAME_POS = {
    "torch": (8.0, 11.0, 8.0),
    "wall_torch": (4.6, 14.2, 8.0),     # facing east (attached to the block on its west side)
    "lantern": (8.0, 4.5, 8.0),
    "lantern_hanging": (8.0, 5.5, 8.0),
}


def _link(obj, collection):
    if collection is None:
        collection = bpy.context.scene.collection
    collection.objects.link(obj)
    return obj


def _material_for(block_id):
    def f(q):
        tint = mc.block_tint(block_id, q.tintindex)
        return block_material(q.texture, tint, shade=getattr(q, "shade", None))
    return f


def make_bell(attachment="floor", facing="north", collection=None):
    """The village bell as an animatable prop. Returns the swinging BODY object: its origin is the hinge pivot and
    rotation_euler.x (local X = along the bar) swings it. `body.parent` is an Empty at the bottom centre of the
    bell's block cell that also carries the static frame: move/place that parent, never the body."""
    props = {"attachment": attachment, "facing": facing}
    root = bpy.data.objects.new("bell", None)
    root.empty_display_size = 0.3
    _link(root, collection)
    frame = mc.quads_object("bell_frame", mc.bake_block("bell", props), _material_for("bell"), collection,
                            origin=(8.0, 0.0, 8.0))
    frame.parent = root
    body = mc.quads_object("bell_body", mc.bell_body_quads(), _material_for("bell"), collection,
                           origin=mc.BELL_PIVOT)
    body.parent = root
    body.location = (0.0, 0.0, mc.BELL_PIVOT[1] / 16.0)
    body.rotation_mode = "XYZ"
    body.rotation_euler = (0.0, 0.0, -math.radians(_Y_ROT.get(attachment, _Y_ROT["floor"]).get(facing, 0)))
    root["mc_block"] = "bell"
    return body


def ring_bell(body, frame, strength=1.0, swings=5, fps=24):
    """Key the bell body's swing starting at `frame`: the game's decaying sine (period ~1 s), `swings` half-swings
    long, peak angle about 20 degrees x strength. Returns the frame where it is at rest again."""
    period = 2 * math.pi * math.pi / 20.0 * fps        # the game swings with sin(ticks / pi): ~0.99 s per cycle
    half = period / 2.0
    total = int(round(half * swings))
    amp = math.radians(20.0) * strength
    body.rotation_euler[0] = 0.0
    body.keyframe_insert("rotation_euler", index=0, frame=frame - 1)
    for i in range(0, total + 1):
        t = i / half                                    # in half-swings
        decay = (1.0 - i / float(total)) ** 1.3 if total else 0.0
        body.rotation_euler[0] = amp * math.sin(math.pi * t) * decay
        body.keyframe_insert("rotation_euler", index=0, frame=frame + i)
    body.rotation_euler[0] = 0.0
    body.keyframe_insert("rotation_euler", index=0, frame=frame + total + 1)
    return frame + total + 1


def make_door(block_id="oak_door", hinge="left", collection=None):
    """Both halves of a door built from the game's door models, as one object whose origin is the hinge axis at
    floor level. Authored for facing=east (the closed door runs along -Y from a left hinge, +Y from a right hinge);
    rotate about Z to open: obj['open_angle'] is the signed fully-open angle (+90 deg left hinge, -90 deg right)."""
    quads = []
    for half, dy in (("lower", 0.0), ("upper", 16.0)):
        for q in mc.bake_block(block_id, {"facing": "east", "half": half, "hinge": hinge, "open": "false"}):
            quads.append(mc.Quad([(p[0], p[1] + dy, p[2]) for p in q.pts], q.uvs, q.texture, q.tintindex, q.overlay))
    hz = 1.5 if hinge == "left" else 14.5
    ob = mc.quads_object(block_id, quads, _material_for(block_id), collection, origin=(1.5, 0.0, hz))
    ob.rotation_mode = "XYZ"
    ob["open_angle"] = math.pi / 2 if hinge == "left" else -math.pi / 2
    ob["hinge"] = hinge
    ob["mc_block"] = block_id
    return ob


def door_transform(cell, facing="east", hinge="left"):
    """(location, yaw) that puts a make_door() prop exactly where the door block at Blender cell `cell` with this
    facing and hinge is drawn."""
    yaw = YAW_FROM_EAST[facing]
    ox, oy = -6.5 / 16.0, (6.5 if hinge == "left" else -6.5) / 16.0
    c, s = math.cos(yaw), math.sin(yaw)
    return ((cell[0] + 0.5 + ox * c - oy * s, cell[1] + 0.5 + ox * s + oy * c, float(cell[2])), yaw)


def place_door(door, cell, facing="east"):
    """Move a make_door() prop onto the door block at Blender cell `cell` (closed). Stores the closed yaw."""
    loc, yaw = door_transform(cell, facing, door.get("hinge", "left"))
    door.location = loc
    door.rotation_euler = (0.0, 0.0, yaw)
    door["closed_yaw"] = yaw
    return door


def make_item(item_id, collection=None):
    """Held item (e.g. 'emerald'): the item texture extruded one pixel thick, 16 px = 1 unit, origin at its centre,
    lying in the local XZ plane."""
    return _link(mc.item_object(item_id), collection)


def make_light(kind="torch", collection=None):
    """Warm point light sized for a 'torch' or 'lantern' (soft shadows, near field flattened so the block it sits
    on keeps its texture); kind 'fill' is the weak cool shadowless room fill used inside torch-lit buildings."""
    kind = "fill" if kind == "fill" else ("lantern" if kind.startswith("lantern") else "torch")
    data = bpy.data.lights.new(kind + "_light", "POINT")
    data.color = FILL_COLOR if kind == "fill" else TORCH_COLOR
    data.energy = LIGHT_ENERGY[kind]
    data.shadow_soft_size = LIGHT_RADIUS[kind]
    if kind == "fill":
        data.use_shadow = False
        try:
            data.specular_factor = 0.0
        except (AttributeError, TypeError):
            pass
    _smooth_falloff(data, LIGHT_SMOOTH[kind])
    ob = bpy.data.objects.new(kind + "_light", data)
    ob["mc_light"] = kind
    ob["base_energy"] = data.energy
    return _link(ob, collection)


def _smooth_falloff(light, smooth):
    """Give a point light the node tree Emission(strength = Light Falloff(1, smooth).Quadratic)."""
    try:
        light.use_nodes = True
        nt = light.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputLight")
        em = nt.nodes.new("ShaderNodeEmission")
        fall = nt.nodes.new("ShaderNodeLightFalloff")
        fall.inputs["Strength"].default_value = 1.0
        fall.inputs["Smooth"].default_value = float(smooth)
        nt.links.new(fall.outputs["Quadratic"], em.inputs["Strength"])
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    except (AttributeError, RuntimeError, KeyError) as exc:      # no light nodes in this build: plain inverse square
        print("[props] light falloff nodes unavailable (%s)" % exc)


def flame_position(cell, block_id, props=None):
    """World position of the flame of a torch / wall_torch / lantern block at Blender cell `cell`."""
    props = props or {}
    if block_id == "wall_torch":
        p = FLAME_POS["wall_torch"]
        y = {"east": 0, "south": 90, "west": 180, "north": 270}[props.get("facing", "east")]
        p = mc.rotate_point(p, 0, y)
    elif block_id == "lantern":
        p = FLAME_POS["lantern_hanging" if props.get("hanging") == "true" else "lantern"]
    else:
        p = FLAME_POS["torch"]
    b = mc.to_blender(p)
    return (cell[0] + b[0], cell[1] + b[1], cell[2] + b[2])


# --------------------------------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------------------------------

def _stage(preset="golden"):
    from . import quick
    from .blocks import World, new_collection

    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, preset)
    w = World()
    w.fill(-8, -8, -1, 8, 8, -1, "grass_block")
    w.cull_below = -1
    coll = new_collection(scene, "set")
    return scene, w, coll


def _selftest():
    from . import quick

    # the bell mid-swing on a cobblestone base, as in a village meeting point
    scene, w, coll = _stage("golden")
    w.fill(-1, -1, 0, 1, 1, 0, "cobblestone")
    w.build(coll)
    body = make_bell("floor", "north", coll)
    body.parent.location = (0.5, 0.5, 1.0)
    ring_bell(body, 1, strength=1.0, swings=5)
    scene.frame_set(7)
    light = make_light("torch", coll)
    light.location = (2.0, -1.5, 2.2)
    quick.camera(scene, (2.6, -3.4, 2.1), (0.5, 0.5, 1.55), lens=50, fstop=2.8)
    print("wrote", quick.render(scene, "props_bell"))

    # doors in a plank wall: closed, half open, fully open (left hinge) and an open right-hinged one; an emerald
    scene, w, coll = _stage("golden")
    for x in range(-4, 5):
        if x not in (-3, -1, 1, 3):
            w.fill(x, 0, 0, x, 0, 2, "oak_planks")
        else:
            w.set(x, 0, 2, "oak_planks")
    w.build(coll)
    for x, hinge, t in ((-3, "left", 0.0), (-1, "left", 0.5), (1, "left", 1.0), (3, "right", 1.0)):
        d = make_door("oak_door", hinge, coll)
        place_door(d, (x, 0, 0), "north")
        d.rotation_euler[2] = d["closed_yaw"] + d["open_angle"] * t
    item = make_item("emerald", coll)
    item.location = (-1.6, -2.4, 0.62)
    item.rotation_euler = (0.0, 0.0, math.radians(-35))
    lamp = make_light("lantern", coll)
    lamp.location = (0.0, -2.5, 2.2)
    quick.camera(scene, (-7.4, -10.4, 5.6), (0.2, -0.3, 1.0), lens=30)
    print("wrote", quick.render(scene, "props_door_open"))


if __name__ == "__main__":
    _selftest()
