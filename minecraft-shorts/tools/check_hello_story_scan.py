"""Checker probe: candidate places for the watcher that the lens can see (dg15_a far position; in17 through the pane)."""
import math
import bpy
import render
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

S = render.Session("hello")
scene, film = S.scene, S.film
st = S.result["stage"]
C = S.result["context"]
cast_obs = set()
for c in st.cast.values():
    for name in ("root",):
        ob = getattr(c, name, None)
        if ob is not None:
            for o in [ob] + list(ob.children_recursive):
                cast_obs.add(o.name)


def clear(cam_pos, p, dg):
    d = p - cam_pos
    direction, origin, left = d.normalized(), cam_pos.copy(), d.length - 0.2
    for _ in range(12):
        ok, loc, nrm, idx, ob, mat = scene.ray_cast(dg, origin, direction, distance=left)
        if not ok:
            return None
        if ob.name in cast_obs:
            step = (loc - origin).length + 0.02
            origin = loc + direction * 0.02
            left -= step
            continue
        return ob.name
    return None


def scan(shot_frame, pts, label):
    cam = film.goto(shot_frame)
    dg = bpy.context.evaluated_depsgraph_get()
    cp = cam.matrix_world.translation.copy()
    for (x, y) in pts:
        g = C.stand((x, y))
        okc = 0
        res = []
        for dz in (1.62, 1.2, 0.6):            # eyes, chest, knees
            p = Vector((g[0], g[1], g[2] + dz))
            hit = clear(cp, p, dg)
            res.append("ok" if hit is None else hit.replace("village_block_", ""))
        v = world_to_camera_view(scene, cam, Vector((g[0], g[1], g[2] + 1.62)))
        print("%s (%5.1f,%5.1f) ground %.2f  eyes x %5.1f%% y %5.1f%%  eyes/chest/knees: %s" % (
            label, x, y, g[2], v.x * 100, (1 - v.y) * 100, " / ".join(res)))


scan(936, [(8.3, 14.6), (7.8, 14.6), (7.4, 14.6), (7.0, 14.6), (8.3, 13.0), (7.6, 13.0), (8.0, 16.0), (7.2, 16.0)], "dg15_a f936")
scan(1051, [(3.4, -6.7), (5.0, -7.5), (6.0, -8.0), (6.5, -8.3), (7.0, -8.6), (5.5, -8.6), (4.0, -8.0), (6.0, -9.0)], "in17 f1051")
scan(1073, [(3.4, -6.7), (5.0, -7.5), (6.0, -8.0), (6.5, -8.3), (7.0, -8.6), (5.5, -8.6), (4.0, -8.0), (6.0, -9.0)], "in17 f1073")
