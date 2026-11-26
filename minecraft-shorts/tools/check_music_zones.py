"""Zones and occlusion check of engine/music.py's beats, staged as its BEATS docstring says (tools/music_proof.py
builds every shot that way and declares, per shot and frame, which faces and props must read). No rendering.

    $BPY -m tools.check_music_zones                   # both skies, every declared shot
    $BPY -m tools.check_music_zones gold b1 b3         # one sky, some shots
    MUSIC_CAMS='{"b1": {"pos": [-17, 0.4, 1.9]}}' $BPY -m tools.check_music_zones gold b1     # try a camera

For every declared frame it prints each face / prop as (x %, y %) of the frame, how much of it the camera sees
(rays from the lens to five points on the face, or to the prop's centre: a ray that first hits another player or a
block counts as hidden), and for faces the angle between the look and the lens (0 = straight at the lens, 90 =
profile). A face is OK when its centre is inside the Reels safe area (x 8-82 %, y 14-60 %, CONTRACT.md "Composition
rule"), at least 4 of 5 rays reach it, and it turns no more than 75 degrees from the lens; a prop when its centre is
in the safe area and its ray reaches it; 'head' = a face without the angle test (a profile is wanted); 'wide' =
inside x 10-90 %, y 5-95 % and seen; 'frame' things need only be inside the frame (x 5-95 %, y 0-100 %) and seen.
Exit code 1 when anything fails.
"""
import math
import sys

import bpy
from mathutils import Vector

SAFE = (8.0, 82.0, 14.0, 60.0)
INFRAME = (5.0, 95.0, 0.0, 100.0)
WIDE = (10.0, 90.0, 5.0, 95.0)
TRANSIENT = ("music_note_", "fx_")                        # particles: they pass in front for a few frames            # 'wide': inside the frame's width less the phone crop and a margin


def _root(ob):
    while ob is not None and ob.parent is not None:
        ob = ob.parent
    return ob


def _center(ob, dg):
    ev = ob.evaluated_get(dg)
    if ev.type == "MESH" and len(ev.data.vertices):
        pts = [ev.matrix_world @ v.co for v in ev.data.vertices]
        return sum(pts, Vector()) / len(pts)
    return ev.matrix_world.translation.copy()


def _project(scene, cam, p):
    from bpy_extras.object_utils import world_to_camera_view

    q = world_to_camera_view(scene, cam, p)
    return 100.0 * q.x, 100.0 * (1.0 - q.y), q.z


def _ray(scene, dg, origin, point, owner_roots, slack=0.12):
    """True when the first thing the ray from `origin` to `point` hits belongs to `owner_roots` (or nothing is hit
    before the point). Returns (seen, name of what was hit first)."""
    d = point - origin
    dist = d.length
    hit, loc, _n, _i, ob, _m = scene.ray_cast(dg, origin, d.normalized(), distance=dist + 0.6)
    if not hit:
        return True, ""
    if (loc - origin).length >= dist - slack:
        return True, ""
    if _root(ob) in owner_roots or ob in owner_roots:
        return True, ob.name
    if ob.name.startswith(TRANSIENT):                    # a note particle passing in front: seen a moment later
        return True, ob.name + "(passing)"
    return False, "%s@(%.1f,%.1f,%.1f)" % (ob.name, loc.x, loc.y, loc.z)


def _inside(x, y, z, box):
    return z > 0 and box[0] <= x <= box[1] and box[2] <= y <= box[3]


def check(scene, film, zones, only=None):
    """Evaluate the declared zones {shot: [(frame, [(label, thing, kind), ...]), ...]}. Returns the failures."""
    from engine import players

    bad = []
    for shot, entries in zones.items():
        if only and shot not in only:
            continue
        for frame, items in entries:
            film.goto(frame)
            dg = bpy.context.evaluated_depsgraph_get()
            cam = scene.camera
            cpos = cam.matrix_world.translation.copy()
            right = (cam.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
            upv = (cam.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
            row = []
            for label, thing, kind in items:
                if isinstance(thing, players.Player) or hasattr(thing, "eye_point"):
                    eye = thing.eye_point(frame)
                    lv = thing.look_vector(frame) if hasattr(thing, "look_vector") else Vector((0, -1, 0))
                    front = eye + lv * 0.18
                    owners = {thing.root}
                    pts = [front] + [front + right * a + upv * b for a, b in ((0.15, 0.1), (-0.15, 0.1),
                                                                           (0.15, -0.1), (-0.15, -0.1))]
                    seen = []
                    first = ""
                    for q in pts:
                        s, nm = _ray(scene, dg, cpos, q, owners)
                        seen.append(s)
                        if (not s or "(passing)" in nm) and not first:
                            first = nm
                    x, y, z = _project(scene, cam, eye)
                    ang = math.degrees(lv.angle((cpos - eye).normalized())) if lv.length > 0 else 0.0
                    nseen = sum(seen)
                    if kind == "face":
                        ok = _inside(x, y, z, SAFE) and nseen >= 4 and ang <= 75.0
                    elif kind == "head":
                        ok = _inside(x, y, z, SAFE) and nseen >= 4
                    elif kind == "frame":
                        ok = _inside(x, y, z, INFRAME) and nseen >= 3
                    else:
                        ok = True
                    txt = "%s(%.0f,%.0f) %d/5 %.0fdeg%s" % (label, x, y, nseen, ang, (" <" + first) if first else "")
                else:
                    if hasattr(thing, "sprite"):                     # engine.mobs DroppedItem
                        ob, owners = thing.sprite, {thing.root, thing.sprite}
                    elif isinstance(thing, bpy.types.Object):
                        ob, owners = thing, {thing, _root(thing)}
                    else:
                        ob, owners = None, set()
                    if ob is not None:
                        p = _center(ob, dg)
                        hidden = ob.evaluated_get(dg).hide_render if hasattr(ob, "hide_render") else False
                    else:
                        p = Vector(thing(frame) if callable(thing) else thing)
                        hidden = False
                    x, y, z = _project(scene, cam, p)
                    size = ""
                    if ob is not None and ob.type == "MESH":
                        ev = ob.evaluated_get(dg)
                        xs = [_project(scene, cam, ev.matrix_world @ v.co)[0] for v in ev.data.vertices]
                        size = " w%.0f%%" % (max(xs) - min(xs))
                    s, nm = _ray(scene, dg, cpos, p, owners, slack=0.3)
                    box = SAFE if kind == "prop" else (WIDE if kind == "wide" else INFRAME)
                    ok = (kind == "info") or (_inside(x, y, z, box) and s and not hidden)
                    txt = "%s(%.0f,%.0f)%s%s%s" % (label, x, y, size, "" if s else " <" + nm, " HIDDEN" if hidden else "")
                row.append(("" if ok else "!!") + txt)
                if not ok:
                    bad.append((shot, frame, label))
            print("[zones] %-11s f%-4d %s" % (shot, frame, "  ".join(row)), flush=True)
    return bad


def main(argv):
    from tools import music_proof as mp

    skies = [a for a in argv if a in ("gold", "night")] or ["gold", "night"]
    only = [a for a in argv if a not in ("gold", "night")] or None
    bad = []
    for sky in skies:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = bpy.context.scene
        names = None
        if only:
            names = [n for n in only if mp.SKY_OF.get(n) == sky]
            if not names:
                continue
        b = mp.build(scene, sky, res=(540, 960), samples=1, only=names)
        bad += check(scene, b["film"], b["h"].get("zones", {}), only)
    print("[zones] %d failed: %s" % (len(bad), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
