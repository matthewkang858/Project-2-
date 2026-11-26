"""Checker probe (engine/towers.py review): re-render two of the author's golden proof frames under my own name and
run tools.palette_check on them (heroes from the proof's Stage)."""
import os
import sys

import bpy

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "test")


def main(names):
    from tools import palette_check as pc
    from tools import towers_proof as tp
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    b = tp.build(scene)
    for n in names:
        f = b["frames"][n][0]
        b["film"].goto(f)
        p = os.path.join(OUT, "check_towers_palette_%s" % n)
        scene.render.filepath = p
        scene.render.use_file_extension = True
        bpy.ops.render.render(write_still=True)
        heroes = [ob for _l, obs in b["stage"].heroes.get(n, []) for ob in obs]
        rep = pc.evaluate(pc.probe(scene), p + ".png", heroes=heroes)
        pc.print_report(n, rep)


if __name__ == "__main__":
    main(sys.argv[1:])
