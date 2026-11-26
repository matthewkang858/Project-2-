"""Checker probe (engine/towers.py review): does the lava glow's flicker read in the golden-hour slide shot?
Renders the slide shot on the frame the light is smothered (45 %) and two frames later (170 %), 270x480, and
measures the difference in the slot region."""
import os
import sys

import bpy
import numpy as np
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "test")


def main():
    from tools import towers_proof as tp
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    built = tp.build(scene, res=(270, 480), samples=16, threads=2)
    film, h = built["film"], built["h"]
    g = h["slide"]["gone"]
    ims = []
    for f in (g + 1, g + 2):
        film.goto(f)
        p = os.path.join(OUT, "check_towers_flicker_%d" % f)
        scene.render.filepath = p
        scene.render.use_file_extension = True
        bpy.ops.render.render(write_still=True)
        ims.append(np.asarray(Image.open(p + ".png").convert("RGB"), float))
    d = np.abs(ims[1] - ims[0]).sum(2)
    print("frames %d (45%%) vs %d (170%%): mean abs diff %.2f /765, max %.0f, pixels > 30: %d of %d"
          % (g + 1, g + 2, d.mean(), d.max(), int((d > 30).sum()), d.size))
    Image.fromarray(np.clip(d * 4, 0, 255).astype("uint8")).save(os.path.join(OUT, "check_towers_flicker_diff.png"))
    side = np.concatenate([ims[0], ims[1]], 1).astype("uint8")
    Image.fromarray(side).save(os.path.join(OUT, "check_towers_flicker_pair.png"))


if __name__ == "__main__":
    sys.exit(main())
