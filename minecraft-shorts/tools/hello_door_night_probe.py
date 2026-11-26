"""The Hello, door_night sequence: per-frame measurements of its shots without rendering (one build of the night
sky). For each asked frame: every cast member of the shot with its root position, the head's box in the frame
(x / y in %, y from the top as the Reels zones), the angle between its nose and the lens, and whether any part of
its body is inside the frame at all; the door's crack stage and shudder angle.

    $BPY -m tools.hello_door_night_probe dn02_fight 72-144:4
    $BPY -m tools.hello_door_night_probe dn19_beside 1193,1198,1222
Writes nothing. Prefix with `nice -n 5 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _frames(spec):
    out = []
    for part in spec.split(","):
        step = 1
        if ":" in part:
            part, step = part.split(":")
            step = int(step)
        if "-" in part:
            a, b = (int(v) for v in part.split("-"))
            out += list(range(a, b + 1, step))
        else:
            out.append(int(part))
    return out


def main(argv):
    """See the module docstring."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    from engine import breaking
    shot_name, frames = argv[0], _frames(argv[1])
    ses = render.Session("hello", sky="night")
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    s = {x.name: x for x in ses.film.shots}[shot_name]
    cam = s.camera
    scene.camera = cam
    names = sorted(st.in_shot.get(shot_name, ()))

    def box(obs):
        pts = []
        for ob in obs:
            if ob.type != "MESH":
                continue
            for corner in ob.bound_box:
                co = world_to_camera_view(scene, cam, ob.matrix_world @ Vector(corner))
                pts.append((co.x * 100.0, (1.0 - co.y) * 100.0))
        if not pts:
            return None
        return (min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts))

    for line in C.memo.get("dn_log", []):
        print("[dn] " + line)
    door = C.door
    for f in frames:
        scene.frame_set(f)
        cp = cam.matrix_world.translation.copy()
        line = ["%5d" % f]
        for n in names:
            c = st.cast[n]
            if not hasattr(c, "head"):
                continue
            hb = box([c.head] + [o for o in c.head.children_recursive if not o.hide_render])
            root = c.parts["root"] if hasattr(c, "parts") else c.root
            body = box([o for o in [root] + list(root.children_recursive) if not o.hide_render])
            p = c.pos_at(f)
            hy = c.head.matrix_world.to_euler().z
            nose = Vector((math.sin(hy), -math.cos(hy), 0.0))
            eye = Vector(c.eye_point(f))
            to_cam = Vector((cp.x - eye.x, cp.y - eye.y, 0.0)).normalized()
            off = math.degrees(math.acos(max(-1.0, min(1.0, nose.dot(to_cam)))))
            inside = body is not None and body[1] > 0 and body[0] < 100 and body[3] > 0 and body[2] < 100
            hs = "head x %5.1f..%5.1f y %5.1f..%5.1f" % hb if hb else "head -"
            arm = getattr(c, "arm_r", None)
            arm_s = " armR %4.0f" % math.degrees(arm.rotation_euler.x) if arm is not None else ""
            line.append("%s @(%.2f,%.2f,%.2f) %s off %3.0f %s%s" % (n[:6], p.x, p.y, p.z, hs, off,
                                                                   "IN" if inside else "out", arm_s))
        line.append("crack %d rot %.4f" % (breaking.stage_at(door, f), door.rotation_euler[2]))
        print("  ".join(line))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
