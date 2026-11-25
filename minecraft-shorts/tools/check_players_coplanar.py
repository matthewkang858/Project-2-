"""Checker probe: coplanar, overlapping, same-facing faces between the meshes of one player (Cycles has no draw
order: such a pair renders as noise or as whichever the BVH returns first).

    $BPY -m tools.check_players_coplanar
"""
import math
from collections import defaultdict

import bpy
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
from engine import players as pl          # noqa: E402

scene = bpy.context.scene
U = 0.9375 / 16.0


def audit(p, label, pose=None):
    if pose:
        pose(p)
    bpy.context.view_layer.update()
    buckets = defaultdict(list)
    obs = [o for o in scene.objects if o.type == "MESH" and o.name.startswith(p.name + "_") and not o.hide_render]
    for ob in obs:
        mw = ob.matrix_world
        rot = mw.to_3x3()
        for poly in ob.data.polygons:
            n = (rot @ poly.normal).normalized()
            pts = [mw @ ob.data.vertices[i].co for i in poly.vertices]
            d = n.dot(pts[0])
            key = (round(n.x, 3), round(n.y, 3), round(n.z, 3), round(d / U, 2))
            buckets[key].append((ob.name, pts))
    hits = defaultdict(float)
    for key, faces in buckets.items():
        n = Vector(key[:3])
        # 2D axes in the plane
        for i in range(len(faces)):
            for j in range(i + 1, len(faces)):
                if faces[i][0] == faces[j][0]:
                    continue
                # exact for two rectangles: clip rectangle j by the four edges of rectangle i (Sutherland-Hodgman)
                poly = list(faces[j][1])
                pi = faces[i][1]
                c = sum(pi, Vector()) / len(pi)
                for k in range(len(pi)):
                    e0, e1 = pi[k], pi[(k + 1) % len(pi)]
                    inward = n.cross(e1 - e0)
                    if inward.dot(c - e0) < 0:
                        inward = -inward
                    new = []
                    for m in range(len(poly)):
                        p0, p1 = poly[m], poly[(m + 1) % len(poly)]
                        d0, d1 = inward.dot(p0 - e0), inward.dot(p1 - e0)
                        if d0 >= 0:
                            new.append(p0)
                        if (d0 >= 0) != (d1 >= 0):
                            new.append(p0 + (p1 - p0) * (d0 / (d0 - d1)))
                    poly = new
                    if len(poly) < 3:
                        break
                if len(poly) >= 3:
                    area = 0.0
                    for m in range(1, len(poly) - 1):
                        area += (poly[m] - poly[0]).cross(poly[m + 1] - poly[0]).length / 2.0
                    if area / U / U > 0.01:
                        hits[(tuple(sorted((faces[i][0], faces[j][0]))), key)] += area / U / U
    print("\n%s: %d meshes" % (label, len(obs)))
    if not hits:
        print("   no coplanar same-facing overlaps")
    for (names, key), area in sorted(hits.items(), key=lambda kv: -kv[1]):
        print("   %-22s / %-22s normal (%g, %g, %g) plane at %.2f px: %.1f px^2 overlap" % (names[0], names[1], key[0], key[1], key[2], key[3], area))
    return hits


def stride(p):
    p.leg_r.rotation_euler[0] = 1.0
    p.leg_l.rotation_euler[0] = -1.0


a = pl.make_player("a", "herobrine")
pl.equip(a, "diamond")
audit(a, "herobrine + full diamond, standing")
b = pl.make_player("b", "steve")
pl.equip(b, "netherite")
b.root.location = (5, 0, 0)
audit(b, "steve + full netherite, legs apart (+-1.0 rad)", stride)
c = pl.make_player("c", "kai")
c.root.location = (10, 0, 0)
audit(c, "kai, no armor, legs apart", stride)
d = pl.make_player("d", "noor")
pl.equip(d, boots="golden")
d.root.location = (15, 0, 0)
audit(d, "noor + golden boots only, legs apart", stride)
e = pl.make_player("e", "steve")
pl.equip(e, leggings="iron")
e.root.location = (20, 0, 0)
e.sneak(1)
scene.frame_set(1)
audit(e, "steve + iron leggings, crouching")
