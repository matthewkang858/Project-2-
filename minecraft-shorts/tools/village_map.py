"""Top-down orthographic map of the village set with anchor / path overlays (layout check).

Usage (project root):  $BPY -m tools.village_map [half_extent]   -> out/test/village_map.png
"""
import math
import sys

import bpy

from engine import quick, village


def main(half=40.0):
    scene = quick.reset()
    quick.setup(scene, res=(1080, 1080), samples=8)
    v = village.build_village(scene, seed=1)
    quick.light(scene, "day")
    cam = bpy.data.cameras.new("map")
    cam.type = "ORTHO"
    cam.ortho_scale = half * 2
    ob = bpy.data.objects.new("map", cam)
    ob.location = (-2.0, -3.0, 120.0)
    scene.collection.objects.link(ob)
    scene.camera = ob
    path = quick.render(scene, "village_map")
    from PIL import Image, ImageDraw

    img = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(img)
    s = 1080 / (half * 2)

    def px(p):
        return ((p[0] + 2.0 + half) * s, (half - (p[1] + 3.0)) * s)

    for name, pts in v.paths.items():
        d.line([px(p) for p in pts], fill=(255, 60, 60), width=2)
    for name, p in v.anchors.items():
        x, y = px(p)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 255, 0), outline=(0, 0, 0))
        d.text((x + 4, y - 5), name, fill=(255, 255, 255))
    for ob in v.lantern_lights:
        x, y = px(ob.location)
        d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=(255, 150, 0))
    img.save(path)
    print("wrote", path, "problems:", v.validate())


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 40.0)
