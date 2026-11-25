"""Independent checker: the pen's fence and gates as blocks (one still), a hen and a cow beside them for scale.
Run:  $BPY -m tools.check_animals_probe_gate   ->  out/test/check_animals_p_gate.png, check_animals_p_gate_open.png"""
import math
import sys

import bpy


def main():
    from engine import animals, quick

    for tag, is_open in (("", False), ("_open", True)):
        scene = quick.reset()
        quick.setup(scene, res=(720, 540), samples=16, threads=2)
        lamp = quick.light(scene, "day")
        lamp.rotation_euler[2] = math.radians(-150.0)
        pen = animals.make_pen(scene, 0, 0, 5, 4, z=0, gates=[(2, 0), (5, 2), (3, 4), (0, 2)], ground="grass_block",
                               name="gatepen", open_gates=is_open)
        print("area", pen["area"], "gates", pen["gates"], [(c, pen["world"].get(c[0], c[1], 0)) for c in pen["gates"]])
        cow = animals.make_cow("cow")
        cow.place(1, (3.6, 2.6, 0), math.radians(200))
        hen = animals.make_chicken("hen")
        hen.place(1, (1.6, 1.4, 0), math.radians(160))
        scene.frame_set(1)
        quick.camera(scene, (1.2, -5.2, 3.6), (2.9, 2.0, 0.4), lens=28)
        print("wrote", quick.render(scene, "check_animals_p_gate" + tag))


if __name__ == "__main__":
    sys.exit(main())
