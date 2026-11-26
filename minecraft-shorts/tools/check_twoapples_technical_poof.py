"""Checker's probe: bx23's death poof living into bx24 (is it seen?) and ev06 rendered under both skies.

    $BPY -m tools.check_twoapples_technical_poof poof
    $BPY -m tools.check_twoapples_technical_poof ev06 dusk|under FRAME
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    import bpy
    from bpy_extras.object_utils import world_to_camera_view

    import render
    if argv[0] == "poof":
        ses = render.Session("twoapples", sky="under")
        scene = ses.scene
        s = {x.name: x for x in ses.film.shots}["bx24_kept"]
        for f in (1465, 1466, 1468, 1470, 1474):
            scene.frame_set(f)
            cam = s.camera
            dg = bpy.context.evaluated_depsgraph_get()
            cp = cam.matrix_world.translation.copy()
            vis = [o for o in bpy.data.objects if o.name.startswith("undead_poof") and not o.hide_render
                   and o.type == "MESH"]
            inframe, seen = 0, 0
            for o in vis:
                p = o.matrix_world.translation
                co = world_to_camera_view(scene, cam, p)
                if 0 <= co.x <= 1 and 0 <= co.y <= 1 and co.z > 0:
                    inframe += 1
                    d = (p - cp)
                    hit, loc, _n, _i, ob, _m = scene.ray_cast(dg, cp, d.normalized(), distance=d.length + 0.05)
                    if hit and (ob.original if hasattr(ob, "original") else ob).name == o.name:
                        seen += 1
            print("f%d poof meshes visible %d, in bx24's frame %d, unoccluded %d; e.g. %s" % (
                f, len(vis), inframe, seen, [(o.name, tuple(round(v, 2) for v in o.matrix_world.translation))
                                             for o in vis[:2]]))
        return 0
    sky, frame = argv[1], int(argv[2])
    ses = render.Session("twoapples", sky=sky)
    scene = ses.scene
    s = {x.name: x for x in ses.film.shots}["ev06_stairs"]
    scene.frame_set(frame)
    scene.camera = s.camera
    scene.render.resolution_x, scene.render.resolution_y = 270, 480
    scene.cycles.samples = 8
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 2
    out = os.path.join(ROOT, "out", "test", "check_twoapples_technical_ev06_%s_%d.png" % (sky, frame))
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("[probe] wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
