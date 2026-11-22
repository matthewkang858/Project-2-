"""Independent checker: world-space travel of the STANCE sole of engine.mobs' planted gait (roll, ramps and a
corner included), measured on the evaluated meshes.  Run:  $BPY -m tools.check_mobs_feet"""
import math
import sys

import bpy
import numpy as np
from mathutils import Vector


def main():
    from engine import mobs, quick

    scene = quick.reset()

    def ev(f):
        w = int(math.floor(f))
        scene.frame_set(w, subframe=float(f) - w)
        bpy.context.view_layer.update()

    def sole_points(leg):
        zs = [v.co.z for v in leg.data.vertices]
        lo = min(zs)
        pts = [v.co.copy() for v in leg.data.vertices if v.co.z < lo + 1e-5]
        c = sum(pts, Vector()) / len(pts)
        return c

    for label, kw, path in (("straight walk", {}, [(0, 0, 0), (0, -8, 0)]),
                            ("straight run", dict(run=True), [(0, 0, 0), (0, -14, 0)]),
                            ("walk speed 0.6", dict(speed=0.6), [(0, 0, 0), (0, -5, 0)]),
                            ("corner", {}, [(0, 0, 0), (0, -4, 0), (4, -4, 0)])):
        g = mobs.make_iron_golem("f_" + label.replace(" ", "_"))
        g.place(1, path[0], 0.0)
        end = g.walk(1, path, **kw)
        cl, cr = sole_points(g.leg_l), sole_points(g.leg_r)
        rows = []
        for f in np.arange(1.0, end + 0.001, 0.25):
            ev(f)
            rows.append((f, g.leg_l.matrix_world @ cl, g.leg_r.matrix_world @ cr, g.leg_l.rotation_euler.x,
                         g.root.matrix_world.translation.copy()))
        # stance leg = the one whose angle is moving backward (rotation_euler.x: + is back for these rigs?) -> decide
        # by which sole moves less over the ground in each quarter frame
        worst = 0.0
        run_start = None
        cur = None
        lifts = []
        for a, b in zip(rows, rows[1:]):
            dl = (b[1].xy - a[1].xy).length
            dr = (b[2].xy - a[2].xy).length
            body = (b[4].xy - a[4].xy).length
            if body < 1e-6:
                continue
            st = "l" if dl < dr else "r"
            if st != cur:
                cur, run_start = st, (a[1] if st == "l" else a[2]).copy()
            p = b[1] if st == "l" else b[2]
            worst = max(worst, (p.xy - run_start.xy).length)
            lifts.append(p.z)
        print("%-15s %3d frames, swing %.3f rad, cycle %.1f frames: stance sole strays at most %.4f block over the ground; "
              "its height ranges %.3f .. %.3f" % (label, end - 1, g.last_walk["swing"], g.last_walk["cycle_frames"], worst,
                                                 min(lifts), max(lifts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
