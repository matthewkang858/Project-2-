"""Checker: try concrete fixes for The Hello findings in-process (nothing in the film files is changed).
    $BPY -m tools.check_hello_technical_fixes gold|night
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    import bpy
    import render
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    from tools.check_hello_technical_probe import first_visible_hit
    sky = argv[0]
    ses = render.Session("hello", sky=sky)
    st, C, scene = ses.result["stage"], ses.result["context"], ses.scene
    shots = {s.name: s for s in ses.film.shots}

    def look(sname, f, pos, target, lens, who):
        s = shots[sname]
        s.lens(lens, s._fstop)
        s.move(pos, target)
        scene.frame_set(f)
        scene.camera = s.camera
        dg = bpy.context.evaluated_depsgraph_get()
        cp = s.camera.matrix_world.translation.copy()
        out = []
        for n in who:
            c = st.cast[n]
            eye = Vector(c.eye_point(f))
            co = world_to_camera_view(scene, s.camera, eye)
            out.append("%s x%.0f y%.0f %s" % (n, co.x * 100, (1 - co.y) * 100, first_visible_hit(scene, dg, cp, eye, f)))
        print("[fix] %s f%d cam %s -> %s lens %.0f : %s" % (sname, f, pos, target, lens, " | ".join(out)))

    if sky == "night":
        for pos, tgt in (((18.15, -14.75, 2.55), (18.75, -9.0, 1.85)),
                         ((17.6, -14.75, 2.55), (18.6, -9.0, 1.85)),
                         ((17.4, -14.75, 2.7), (18.5, -9.0, 1.7)),
                         ((17.2, -14.6, 2.6), (18.6, -9.5, 1.7)),
                         ((17.0, -14.75, 2.4), (18.4, -9.0, 1.8)),
                         ((19.2, -14.75, 2.9), (18.7, -9.5, 1.7)),
                         ((19.6, -14.6, 2.9), (18.6, -9.5, 1.7)),
                         ((19.0, -14.75, 3.1), (18.8, -9.5, 1.6)),
                         ((18.8, -14.75, 2.9), (19.0, -9.5, 1.7))):
            look("in03_bed", 160, pos, tgt, 24.0, ("steve_bed_in", "child_in"))
        ses.configure((540, 960), 16, 2, True)
        s = shots["in03_bed"]
        s.lens(24.0, s._fstop)
        s.move(tuple(float(v) for v in os.environ.get("FIXPOS", "19.2,-14.75,2.9").split(",")),
               tuple(float(v) for v in os.environ.get("FIXTGT", "18.7,-9.5,1.7").split(",")))
        path = os.path.join(ROOT, "out", "test", "check_hello_technical_fix_bed_160.png")
        ses.render_frame(160, path)
        print("[fix] rendered", path)
    elif sky == "gold":
        s = shots["dg15_a"]
        scene.frame_set(930)
        scene.camera = s.camera
        dg = bpy.context.evaluated_depsgraph_get()
        cp = s.camera.matrix_world.translation.copy()
        for cand in ((9.4, 14.4), (9.3, 13.0), (9.5, 15.5), (9.2, 11.6)):
            z = C.stand(cand)[2]
            cells = sorted({str(C.v.world.block_id(int(cand[0] + dx) if cand[0] + dx >= 0 else int(cand[0] + dx) - 1,
                                                   int(cand[1] + dy), dz)) for dx in (-0.3, 0.3) for dy in (-0.3, 0.3)
                            for dz in (0, 1)})
            res = []
            for hz in (0.4, 1.0, 1.62):
                p = Vector((cand[0], cand[1], z + hz))
                co = world_to_camera_view(scene, s.camera, p)
                res.append("+%.1f x%.0f y%.0f %s" % (hz, co.x * 100, (1 - co.y) * 100, first_visible_hit(scene, dg, cp, p, 930)))
            print("[fix] watch_far candidate %s z %.3f cells %s : %s" % (cand, z, cells, " | ".join(res)))
        # the two-shot aimed lower: where do the eyes land (render both)
        ses.configure((540, 960), 16, 2, True)
        for sname, f in (("dg04_hello", 226), ("dg22_eyes", 1475)):
            s = shots[sname]
            s.lens(40.0, s._fstop)
            s.move((8.8, -8.4, 1.35), (8.9, -5.4, 0.85))
            path = os.path.join(ROOT, "out", "test", "check_hello_technical_fix_twoshot_%s_%d.png" % (sname, f))
            ses.render_frame(f, path)
            print("[fix] rendered", path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
