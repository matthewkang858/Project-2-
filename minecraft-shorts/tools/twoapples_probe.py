"""Two Apples: one build of one sky, many measurements (no render): the lead's and the directors' probe.

    $BPY -m tools.twoapples_probe --sky under --geo bx24_kept:1490,1511,1531,1551,1561 --who zchild_bx24,dad_bx
    $BPY -m tools.twoapples_probe --sky under --bodies bx23_kill,bx24_kept --ceiling cu16_shakes
    $BPY -m tools.twoapples_probe --sky under --track zombie_bx23:1402,1416,1440 --wall --memo
    $BPY -m tools.twoapples_probe --sky dusk --geo sq03_push:138,160,193,225 --hero sq03_push:138,193

  --geo SHOT:F[,F...] (repeatable)   every cast member of the shot (or --who): eyes x / y %, head box, face px (a
                                    baby's at its own width), `off` (nose to lens, degrees), distance, what blocks it
                                    (tools/twoapples_geo's columns)
  --hero SHOT:F[,F...]              each st.hero of the shot: x / y % of its objects' centre, OUT when outside x 8-82 /
                                    y 14-60, HIDDEN when all its objects are hidden
  --track NAME:F[,F...]             root position, head height and visibility of a cast member
  --bodies SHOT[,SHOT...]           frames on which a visible cast member's body (feet, middle, head; centre and four
                                    sides) or HEAD BOX corners are inside a solid block (the open door's cells excepted)
  --ceiling SHOT[:Z]                the highest head-mesh point of every visible member per frame against the ceiling
                                    underside Z (default F + 3, the aisle's)
  --wall / --memo                   C.wall_log and the door's state on the shots' first / last frames; C.memo
Prefix with `nice -n 15 timeout 290`. Nothing is written.
"""
import argparse
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _frames(spec):
    out = []
    for part in spec.split(","):
        if "-" in part[1:]:
            a, b = part.split("-")[:2]
            step = 1
            if ":" in b:
                b, step = b.split(":")
            out += list(range(int(a), int(b) + 1, int(step)))
        elif part.strip():
            out.append(int(part))
    return out


def main(argv):
    """See the module docstring."""
    ap = argparse.ArgumentParser(prog="tools.twoapples_probe")
    ap.add_argument("--sky", required=True)
    ap.add_argument("--geo", action="append", default=[])
    ap.add_argument("--who", default=None)
    ap.add_argument("--hero", action="append", default=[])
    ap.add_argument("--track", action="append", default=[])
    ap.add_argument("--bodies", default=None)
    ap.add_argument("--ceiling", action="append", default=[])
    ap.add_argument("--wall", action="store_true")
    ap.add_argument("--memo", action="store_true")
    args = ap.parse_args(argv)

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    from tools.twoapples_geo import first_hit, _own, head_box

    ses = render.Session("twoapples", sky=args.sky)
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = {s.name: s for s in ses.film.shots}
    w = C.v.world
    print("[probe] sky %s  film %d frames" % (args.sky, ses.film.shots[-1].frame_end))

    def proj(cam, p):
        co = world_to_camera_view(scene, cam, Vector(p))
        return co.x * 100.0, (1.0 - co.y) * 100.0, co.z

    def meshes(c):
        obs = []
        root = getattr(c, "root", None)
        if root is not None:
            obs = [root] + list(root.children_recursive)
        elif hasattr(c, "objects"):
            o = c.objects() if callable(c.objects) else c.objects
            obs = list(o)
        return [o for o in obs if getattr(o, "type", "") == "MESH"]

    def visible(c):
        obs = meshes(c)
        return any(not o.hide_render for o in obs) if obs else None

    for spec in args.geo:
        sname, fr = spec.split(":")
        s = shots[sname]
        names = [n.strip() for n in args.who.split(",")] if args.who else sorted(st.in_shot.get(sname, ()))
        for f in _frames(fr):
            scene.frame_set(f)
            cam = s.camera
            scene.camera = cam
            dg = bpy.context.evaluated_depsgraph_get()
            cp = cam.matrix_world.translation.copy()
            words = ",".join(wd for wd, ff in C.T[sname].words if ff == f)
            print("\n[geo] %s %d %s cam (%.2f, %.2f, %.2f) lens %.0f" % (sname, f, words, cp.x, cp.y, cp.z,
                                                                       cam.data.lens))
            for n in names:
                c = st.cast.get(n)
                if c is None or not hasattr(c, "eye_point") or getattr(c, "head", None) is None:
                    continue
                if not visible(c):
                    print("  %-18s hidden" % n)
                    continue
                eye = Vector(c.eye_point(f))
                x, y, _z = proj(cam, eye)
                box = [proj(cam, p) for p in head_box(c)]
                top = min(b[1] for b in box) if box else float("nan")
                bot = max(b[1] for b in box) if box else float("nan")
                xl = min(b[0] for b in box) if box else float("nan")
                xr = max(b[0] for b in box) if box else float("nan")
                d = eye - cp
                half = 0.125 if (getattr(c, "child", False) or getattr(c, "baby", False)) else 0.25
                side = d.cross(Vector((0, 0, 1)))
                side = side.normalized() * half if side.length > 1e-6 else Vector((half, 0, 0))
                a, b = proj(cam, eye - side), proj(cam, eye + side)
                face = abs(a[0] - b[0]) / 100.0 * 540
                hy = c.head.matrix_world.to_euler().z
                nose = Vector((math.sin(hy), -math.cos(hy), 0.0))
                to_cam = Vector((cp.x - eye.x, cp.y - eye.y, 0.0))
                off = math.degrees(math.acos(max(-1.0, min(1.0, nose.dot(to_cam.normalized()))))) \
                    if to_cam.length else 0.0
                print("  %-18s eyes x %5.1f y %5.1f  head x %5.1f..%5.1f y %5.1f..%5.1f  face %4.0f px  off %5.1f  "
                      "dist %5.2f  blocked %s" % (n, x, y, xl, xr, top, bot, face, off, d.length,
                                                  first_hit(scene, dg, cp, eye, own=_own(c)) or "clear"))

    for spec in args.hero:
        sname, fr = spec.split(":")
        s = shots[sname]
        for f in _frames(fr):
            scene.frame_set(f)
            cam = s.camera
            parts = []
            for label, obs in st.heroes.get(sname, []):
                obs = [o for o in obs if o is not None]
                if not obs:
                    continue
                pts = [o.matrix_world.translation.copy() for o in obs]
                c = sum(pts, Vector()) / len(pts)
                x, y, z = proj(cam, c)
                flag = "" if (8 <= x <= 82 and 14 <= y <= 60 and z > 0) else " OUT"
                hid = " HIDDEN" if all(o.hide_render for o in obs) else ""
                parts.append("%s x %.1f y %.1f%s%s" % (label, x, y, flag, hid))
            print("[hero] %s %d: %s" % (sname, f, " | ".join(parts) or "none"))

    for spec in args.track:
        name, fr = spec.split(":")
        c = st.cast[name]
        out = []
        for f in _frames(fr):
            scene.frame_set(f)
            p = c.root.matrix_world.translation if hasattr(c, "root") else c.matrix_world.translation
            hz = c.head.matrix_world.translation.z if getattr(c, "head", None) is not None else float("nan")
            out.append("%d(%.2f,%.2f,%.2f h%.2f%s)" % (f, p.x, p.y, p.z, hz, "" if visible(c) is not False else " H"))
        print("[track] %-16s %s" % (name, " ".join(out)))

    if args.bodies:
        door = {(14, -15, -10), (14, -15, -9)}
        for sname in args.bodies.split(","):
            s = shots[sname]
            hits = {}
            for f in range(s.frame_start, s.frame_end + 1):
                scene.frame_set(f)
                for name in st.in_shot.get(sname, ()):
                    c = st.cast[name]
                    if not hasattr(c, "root") or not hasattr(c, "height") or not visible(c):
                        continue
                    p = c.root.matrix_world.translation
                    hw = 0.15 if (getattr(c, "child", False) or getattr(c, "baby", False)) else 0.28
                    pts = [(p.x + dx, p.y + dy, p.z + dz) for dz in (0.15, c.height * 0.5)
                           for dx, dy in ((0, 0), (hw, 0), (-hw, 0), (0, hw), (0, -hw))]
                    if getattr(c, "head", None) is not None:
                        hb = head_box(c)
                        if hb:
                            mid = sum(hb, Vector()) / len(hb)
                            pts += [tuple(mid + (q - mid) * 0.9) for q in hb]
                    for q in pts:
                        cell = (int(math.floor(q[0])), int(math.floor(q[1])), int(math.floor(q[2])))
                        if cell in door and C.ug.door.is_open(f):
                            continue
                        if w.is_solid(*cell):
                            b = w.get(*cell)
                            hits.setdefault(name, []).append((f, cell, b[0] if b else None))
                            break
            if not hits:
                print("[bodies] %s: none inside a block" % sname)
            for name, hh in hits.items():
                fr = sorted({h[0] for h in hh})
                print("[bodies] %s %s: %d frames inside blocks (%d..%d) e.g. %s" % (sname, name, len(fr), fr[0],
                                                                                  fr[-1], hh[:2]))

    for spec in args.ceiling:
        bits = spec.split(":")
        sname = bits[0]
        zc = float(bits[1]) if len(bits) > 1 else float(C.ug_floor if hasattr(C, "ug_floor") else -10) + 3.0
        s = shots[sname]
        for name in sorted(st.in_shot.get(sname, ())):
            c = st.cast[name]
            if getattr(c, "head", None) is None:
                continue
            tops = []
            for f in range(s.frame_start, s.frame_end + 1):
                scene.frame_set(f)
                if not visible(c):
                    continue
                zmax = max((ob.matrix_world @ Vector(co)).z for ob in [c.head] + list(c.head.children_recursive)
                           if ob.type == "MESH" and not ob.hide_render for co in ob.bound_box)
                tops.append((f, zmax))
            over = [(f, round(z - zc, 3)) for f, z in tops if z > zc]
            if tops:
                print("[ceiling] %s %-14s highest head point %.3f (ceiling %.2f): %d frames into it %s"
                      % (sname, name, max(z for _f, z in tops), zc, len(over), over[:16]))

    if args.wall:
        print("[wall] log %s" % C.wall_log)
        for r in sorted(C.T.values(), key=lambda r: r.frame_start):
            if r.sky != args.sky:
                continue
            print("[wall] %-14s %d-%d open %s / %s" % (r.name, r.frame_start, r.frame_end,
                                                      C.wall_is_open(r.frame_start), C.wall_is_open(r.frame_end)))
    if args.memo:
        for k, v in sorted(C.memo.items()):
            print("[memo] %s = %s" % (k, v if not isinstance(v, dict) else
                                      {kk: vv for kk, vv in v.items() if not isinstance(vv, (list, tuple)) or
                                       len(vv) < 6}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
