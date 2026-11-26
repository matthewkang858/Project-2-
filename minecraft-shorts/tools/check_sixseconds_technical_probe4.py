"""Independent checker's fourth probe: in rw22_six, where the step ingot's rendered box and the brute's head box land
in the frame (world_to_camera_view of the mesh corners), frame by frame. $BPY -m tools.check_sixseconds_technical_probe4
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def box(scene, obs):
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    xs, ys, zs = [], [], []
    for top in obs:
        for ob in [top] + list(top.children_recursive):
            if ob.type != "MESH" or ob.hide_render:
                continue
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                p = world_to_camera_view(scene, scene.camera, w)
                xs.append(p.x * 100)
                ys.append((1 - p.y) * 100)
                zs.append(w.z)
    if not xs:
        return None
    return (round(min(xs), 1), round(max(xs), 1), round(min(ys), 1), round(max(ys), 1), round(min(zs), 2),
            round(max(zs), 2))


def main():
    import bpy
    import render
    ses = render.Session("sixseconds", sky="wastes")
    st = ses.result["stage"]
    scene = ses.scene
    ingot = st.cast["gold_ingot_rw"]
    brute = st.cast["brute_rw"]
    iobs = [getattr(ingot, "object", None) or getattr(ingot, "root")]
    for f in (1411, 1419, 1420, 1440, 1452, 1470, 1490):
        scene.frame_set(f)
        print("f%d cam z %.3f | ingot x %s..%s y %s..%s z %s..%s | brute head x %s..%s y %s..%s z %s..%s" % (
            (f, scene.camera.matrix_world.translation.z) + box(scene, iobs) + box(scene, [brute.head])))


if __name__ == "__main__":
    main()
