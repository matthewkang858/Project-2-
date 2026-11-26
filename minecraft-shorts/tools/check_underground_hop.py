"""Checker: where dad's head goes in the b11 portrait and the b12 frontal camera when he is hit in his cell with the
docstring's recipe (undead.hurt(dad, f, attacker=A["ug_door_target"], max_back=0.05)). No rendering.

    $BPY -m tools.check_underground_hop
"""
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


def main():
    from engine import characters, shots, undead
    from engine import underground as U

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    v, ug = U.build_village(scene, seed=1)
    A = v.anchors
    film = shots.Film(scene, fps=24)
    out = {}
    for name in ("b11_portrait", "b12_cell"):
        s = film.shot(name, len(out) * 2.0, len(out) * 2.0 + 2.0)
        c = U.CAMERAS[name]
        s.lens(c["lens"], c["fstop"])
        s.move(c["pos"], c["target"])
        dad = characters.make_villager("hop_" + name, "librarian")
        dad.place(s.frame_start, A["ug_cell_dad"], v.yaws["ug_cell_dad"])
        f = s.frame_start + 6
        undead.hurt(dad, f, attacker=A["ug_door_target"], max_back=0.05)
        out[name] = (s, dad, f)
    film.finalize()
    for name, (s, dad, f) in out.items():
        rows = []
        for fr in range(f - 1, f + 14):
            scene.frame_set(fr)
            dg = bpy.context.evaluated_depsgraph_get()
            ev = dad.head.evaluated_get(dg)
            pts = [ev.matrix_world @ Vector(cc) for cc in ev.bound_box]
            ctr = sum(pts, Vector()) / 8.0
            top = max(p.z for p in pts)
            p = world_to_camera_view(scene, scene.camera, ctr)
            rows.append("f%+d head centre y %5.1f %% (from top), head top z F+%.2f" % (fr - f, (1 - p.y) * 100,
                                                                                    top - U.F))
        print("[hop] %s (hit on frame %d):" % (name, f))
        for r in rows:
            print("      " + r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
