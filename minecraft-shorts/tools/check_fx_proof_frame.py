"""Checker's probe: render arbitrary frames of the author's own proof film (fx.build_proof)."""
import os
import sys
import time

import bpy


def main(argv):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    from engine import fx, look

    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2)
    proof = fx.build_proof(scene)
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "test")
    for a in argv:
        f = int(a)
        t = time.time()
        proof["film"].goto(f)
        scene.render.filepath = os.path.join(out, "check_fx_proof_f%03d.png" % f)
        bpy.ops.render.render(write_still=True)
        print("[proof] frame %d -> %s %.1f s" % (f, scene.render.filepath, time.time() - t), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
