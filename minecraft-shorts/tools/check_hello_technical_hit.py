"""Checker: where exactly the bed camera's line to the sleeping Steve's eyes is blocked (cell and block)."""
import math
import sys


def main(argv):
    import bpy
    import render
    from mathutils import Vector
    ses = render.Session("hello", sky="night")
    st, C, scene = ses.result["stage"], ses.result["context"], ses.scene
    s = next(x for x in ses.film.shots if x.name == "in03_bed")
    for pos in ((18.15, -14.75, 2.55), (19.2, -14.75, 2.9)):
        s.move(pos, (18.7, -9.5, 1.7))
        scene.frame_set(160)
        dg = bpy.context.evaluated_depsgraph_get()
        a = s.camera.matrix_world.translation.copy()
        steve = st.cast["steve_bed_in"]
        for label, b in (("eye", Vector(steve.eye_point(160))), ("head", steve.head.matrix_world.translation.copy())):
            d = (b - a).normalized()
            hit, loc, n, i, ob, m = scene.ray_cast(dg, a, d, distance=(b - a).length - 0.05)
            cell = tuple(int(math.floor(c)) for c in loc) if hit else None
            print("[hit] cam %s %s %s -> hit %s at %s cell %s block %s" % (
                pos, label, tuple(round(c, 2) for c in b), ob.name if hit else None,
                tuple(round(c, 2) for c in loc) if hit else None, cell, C.v.world.get(*cell) if cell else None))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
