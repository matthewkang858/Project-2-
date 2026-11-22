"""Shared pixel-art helpers (images + materials). STABLE API - do not change signatures.

These helpers only wrap pixel arrays into Blender images / materials. Everything VISIBLE in the films comes from
the real game files through engine/mcassets.py; nothing here draws art (the first, procedural pass was rejected).
Row 0 of every array is the TOP row of the texture.
"""
import os

import bpy
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_DIR = os.path.join(ROOT, "assets", "tex")


def rng(seed):
    """Deterministic random generator. Always seed explicitly so builds are reproducible."""
    return np.random.default_rng(seed)


def rgba(hex_str, a=255):
    """'#7fb238' -> (127, 178, 56, a)"""
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def image_from_array(name, arr):
    """uint8 array HxWx4 (sRGB, straight alpha, row 0 = top) -> packed bpy Image, also saved to assets/tex/<name>.png."""
    arr = np.asarray(arr, dtype=np.uint8)
    assert arr.ndim == 3 and arr.shape[2] == 4, "expected HxWx4 uint8"
    h, w = arr.shape[:2]
    old = bpy.data.images.get(name)
    if old is not None:
        bpy.data.images.remove(old)
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.alpha_mode = "STRAIGHT"
    img.pixels.foreach_set((np.flipud(arr).astype(np.float32) / 255.0).ravel())
    os.makedirs(TEX_DIR, exist_ok=True)
    img.filepath_raw = os.path.join(TEX_DIR, name + ".png")
    img.file_format = "PNG"
    img.save()
    img.pack()
    return img


def pixel_material(name, image, emission=0.0, alpha="OPAQUE", roughness=0.9):
    """Material that shows `image` with hard (Closest) pixels.

    emission: strength of self-glow using the texture colour (0 = none).
    alpha: 'OPAQUE' | 'CLIP' (cut-out where alpha < 0.5) | 'BLEND' (soft transparency, e.g. glass).
    """
    old = bpy.data.materials.get(name)
    if old is not None:
        bpy.data.materials.remove(old)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Closest"
    tex.extension = "REPEAT"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Specular IOR Level"].default_value = 0.1
    if emission > 0:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emission
    if alpha == "CLIP":
        gt = nt.nodes.new("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = 0.5
        nt.links.new(tex.outputs["Alpha"], gt.inputs[0])
        nt.links.new(gt.outputs[0], bsdf.inputs["Alpha"])
    elif alpha == "BLEND":
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    return mat


def flat_material(name, color, emission=0.0, roughness=0.9):
    """Single-colour material. color = (r, g, b, a) in 0-255 sRGB."""
    arr = np.zeros((1, 1, 4), dtype=np.uint8)
    arr[0, 0] = color
    return pixel_material(name, image_from_array("flat_" + name, arr), emission=emission, roughness=roughness)


if __name__ == "__main__":
    from . import quick

    scene = quick.reset()
    quick.setup(scene)
    quick.light(scene, "golden")
    r = rng(7)
    arr = np.zeros((16, 16, 4), dtype=np.uint8)
    arr[..., :3] = np.array([110, 160, 70]) + r.integers(-18, 18, (16, 16, 1))
    arr[..., 3] = 255
    arr[0, :, :3] = (255, 60, 60)  # top row red, to verify orientation
    mat = pixel_material("test", image_from_array("test", arr))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.5, 0.5, 0.5))
    bpy.context.object.data.materials.append(mat)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    bpy.context.object.data.materials.append(flat_material("ground", rgba("#8a7a55")))
    quick.camera(scene, (3, -3.5, 1.8), (0.5, 0.5, 0.5), lens=50, fstop=1.4)
    print("wrote", quick.render(scene, "pix_test"))
