"""Checker probe: where the watcher / Steve's eyes land in the frame, how big the face is, and whether anything
blocks the line from the lens to the eyes (ray cast through the evaluated scene, ignoring the cast)."""
import math
import bpy  # noqa
import render
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

S = render.Session("hello")
scene, film = S.scene, S.film
st = S.result["stage"]
cast = st.cast
CASES = [("dg15_a", 936, "watcher_dg"), ("dg15_a", 945, "watcher_dg"), ("dg15_b", 958, "watcher_dg"),
         ("dg15_c", 975, "watcher_dg"), ("in17_window", 1051, "watcher_in"), ("in17_window", 1073, "watcher_in"),
         ("sq09_watches", 558, "watcher_sq"), ("sq10_grownups", 645, "watcher_sq"), ("sq11_stare", 690, "watcher_sq"),
         ("me07_return", 450, "watcher_me"), ("me13_bare", 820, "watcher_me"), ("dn19_beside", 1222, "watcher_dn"),
         ("dg20_walkup", 1300, "watcher_dg"), ("dg21_crouch", 1400, "watcher_dg"),
         ("dg04_hello", 219, "steve_iron_dg"), ("dg04_hello", 233, "steve_iron_dg"), ("dg22_eyes", 1462, "watcher_eyes_dg")]
cast_obs = set()
for c in cast.values():
    for name in ("root", "body", "head", "hips"):
        ob = getattr(c, name, None)
        if ob is not None:
            for o in [ob] + list(ob.children_recursive):
                cast_obs.add(o.name)
rx, ry = scene.render.resolution_x, scene.render.resolution_y
for shot, f, who in CASES:
    c = cast.get(who)
    cam = film.goto(f)
    dg = __import__("bpy").context.evaluated_depsgraph_get()
    eye = c.eye_point(f)
    v = world_to_camera_view(scene, cam, eye)
    cam_pos = cam.matrix_world.translation.copy()
    # face width: 0.5 block across the view direction
    d = (eye - cam_pos)
    side = d.cross(Vector((0, 0, 1))).normalized() * 0.25
    a = world_to_camera_view(scene, cam, eye - side); b = world_to_camera_view(scene, cam, eye + side)
    face_px = abs(a.x - b.x) * rx
    # occlusion: cast rays, skipping cast members
    origin, dist, hit_name = cam_pos.copy(), d.length, None
    direction = d.normalized()
    travelled = 0.0
    for _ in range(12):
        ok, loc, nrm, idx, ob, mat = scene.ray_cast(dg, origin, direction, distance=dist - travelled - 0.3)
        if not ok:
            break
        if ob.name in cast_obs or ob.name.startswith(who):
            step = (loc - origin).length + 0.01
            origin = loc + direction * 0.01; travelled += step
            continue
        hit_name = "%s at %.1f of %.1f" % (ob.name, travelled + (loc - origin).length, dist)
        break
    # facing: angle between his nose (body yaw) and the camera
    yaw = c.yaw_at(f) if hasattr(c, "yaw_at") else 0.0
    nose = Vector((math.sin(yaw), -math.cos(yaw), 0))
    to_cam = Vector((cam_pos.x - eye.x, cam_pos.y - eye.y, 0)).normalized()
    ang = math.degrees(math.acos(max(-1, min(1, nose.dot(to_cam)))))
    print("%-14s f%4d %-16s eyes x %5.1f%% y %5.1f%% (from top)  depth %5.1f  face %4.0f px  body-nose-to-lens %5.1f deg  blocked: %s"
          % (shot, f, who, v.x * 100, (1 - v.y) * 100, v.z, face_px, ang, hit_name))
