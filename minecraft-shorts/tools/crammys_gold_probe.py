"""The Crammys, sequence GOLD: the gold director's measuring probe (no render). One build of the gold sky.

    $BPY -m tools.crammys_gold_probe gd01_everyone 1,40,60,85 [--set 'GD01_STEVE=(-13.8, -0.1)' ...]
                                     [--cam "x,y,z>tx,ty,tz>lens"]

Per frame of the shot: every cast member's head box (x / y in % of the 540x960 frame, y from the top as the Reels
zones), eyes, face width in px, degrees between the head's nose and the lens ('off'), and what blocks the eyes; the
TOTEM's box (its sprite) and the pedestal's GOLD BLOCK box; every NOTE particle on screen on that frame; the held
items' boxes; the last lantern's box. --set NAME=PYTHON overrides a module constant of films/crammys_gold.py before
the build (scouting a spot or a camera without editing the file). Nothing is written.
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
        part = part.strip()
        if "-" in part[1:]:
            rng, _, step = part.partition(":")
            a, b = rng.split("-")
            out.extend(range(int(a), int(b) + 1, int(step or 1)))
        elif part:
            out.append(int(part))
    return out


def _hidden(ob, f):
    ad = ob.animation_data
    if ad is not None and ad.action is not None:
        from engine import shots
        for fc in shots.fcurves_of(ob):
            if fc.data_path == "hide_render":
                return fc.evaluate(f) > 0.5
    return bool(ob.hide_render)


def _box(scene, cam, pts):
    from bpy_extras.object_utils import world_to_camera_view
    cos = [world_to_camera_view(scene, cam, p) for p in pts]
    xs = [c.x * 100 for c in cos]
    ys = [(1 - c.y) * 100 for c in cos]
    return min(xs), max(xs), min(ys), max(ys)


def _obj_pts(ob):
    from mathutils import Vector
    return [ob.matrix_world @ Vector(c) for c in ob.bound_box]


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="tools.crammys_gold_probe")
    ap.add_argument("shot")
    ap.add_argument("frames")
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--cam")
    ap.add_argument("--quiet", action="store_true", help="heads only")
    args = ap.parse_args(argv)

    import importlib

    import bpy  # noqa: F401  (mathutils comes with it)
    gd = importlib.import_module("films.crammys_gold")
    for spec in args.set:
        k, _, v = spec.partition("=")
        setattr(gd, k.strip(), eval(v.strip(), {"math": math, "dict": dict}))   # noqa: S307 (scouting values typed by the director)
        print("[gold_probe] %s = %r" % (k.strip(), getattr(gd, k.strip())))

    import bpy
    from mathutils import Vector

    import render
    from tools.crammys_geo import first_hit, _own, head_box

    ses = render.Session("crammys", sky="gold")
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    s = {x.name: x for x in ses.film.shots}[args.shot]
    if args.cam:
        bits = args.cam.split(">")
        s.move(tuple(float(v) for v in bits[0].split(",")), tuple(float(v) for v in bits[1].split(",")))
        if len(bits) > 2:
            s.lens(float(bits[2]), s._fstop)
    names = sorted(st.in_shot.get(s.name, ()))
    notes = [ob for ob in scene.objects if ob.name.startswith("music_note")]
    gold = [Vector((x, y, z)) for x in (-9.0, -8.0) for y in (-1.0, 0.0) for z in (1.0, 2.0)]
    totem = C.bd._totem if hasattr(C.bd, "_totem") else None
    totem = totem or next((c for n, c in st.cast.items() if "totem" in n), None)
    lantern = C.bd.last_lantern
    for f in _frames(args.frames):
        scene.frame_set(f)
        cam = s.camera
        scene.camera = cam
        dg = bpy.context.evaluated_depsgraph_get()
        cp = cam.matrix_world.translation.copy()
        print("f%4d  cam (%.2f, %.2f, %.2f) lens %.0f focus %s" % (
            f, cp.x, cp.y, cp.z, cam.data.lens,
            ("%.2f" % cam.data.dof.focus_distance) if cam.data.dof.focus_object is None
            else cam.data.dof.focus_object.name))
        for n in names:
            c = st.cast.get(n)
            if c is None or not hasattr(c, "eye_point") or getattr(c, "head", None) is None:
                continue
            eye = Vector(c.eye_point(f))
            xl, xr, yt, yb = _box(scene, cam, head_box(c))
            ex, _, ey, _ = _box(scene, cam, [eye])
            d = eye - cp
            side = d.cross(Vector((0, 0, 1))).normalized() * 0.25
            a, b, _, _ = _box(scene, cam, [eye - side])
            a2, b2, _, _ = _box(scene, cam, [eye + side])
            face = abs(a - a2) / 100.0 * 540
            hy = c.head.matrix_world.to_euler().z
            nose = Vector((math.sin(hy), -math.cos(hy), 0.0))
            to_cam = Vector((cp.x - eye.x, cp.y - eye.y, 0.0)).normalized()
            off = math.degrees(math.acos(max(-1.0, min(1.0, nose.dot(to_cam)))))
            print("   %-10s eyes %5.1f/%5.1f head x %5.1f..%5.1f y %5.1f..%5.1f face %4.0f px off %5.1f  %s" % (
                n, ex, ey, xl, xr, yt, yb, face, off, first_hit(scene, dg, cp, eye, own=_own(c)) or "clear"))
            if args.quiet:
                continue
            for side_, held in (getattr(c, "_hands", None) or {}).items():
                for h in held:
                    for vn, att in h.variants.items():
                        if _hidden(att.ob, f) or _hidden_any(c, f):
                            continue
                        bx = _box(scene, cam, _obj_pts(att.ob))
                        print("      holds %-26s x %5.1f..%5.1f y %5.1f..%5.1f (%4.1f %% wide)" % (
                            h.item_id + (":" + vn if vn else ""), bx[0], bx[1], bx[2], bx[3], bx[1] - bx[0]))
        if args.quiet:
            continue
        bx = _box(scene, cam, gold)
        seen = 0
        grid = [Vector((-9.0 + 0.002 if face == "w" else -9.0 + (i + 0.5) / 5.0,
                        -1.0 + (i + 0.5) / 5.0 if face == "w" else -1.0 + 0.002, 1.0 + (j + 0.5) / 5.0))
                for face in ("w", "s") for i in range(5) for j in range(5)]
        for q in grid:
            seen += first_hit(scene, dg, cp, q) in (None,) or str(first_hit(scene, dg, cp, q)).startswith("gold")
        print("   gold block      x %5.1f..%5.1f y %5.1f..%5.1f  (%s)  %d of 50 face points seen" % (
            bx[0], bx[1], bx[2], bx[3], first_hit(scene, dg, cp, Vector((-8.5, -0.5, 1.5))) or "seen", seen))
        if totem is not None and not _hidden(totem.sprite, f) and not _hidden(totem.root, f):
            pts = _obj_pts(totem.sprite)
            bx = _box(scene, cam, pts)
            q = totem.sprite.matrix_world.translation
            own = {o.name for o in totem.objects()}
            cen = sum(pts, Vector()) / len(pts)
            samples = [q] + [cen.lerp(p, 0.8) for p in pts]
            seen = sum(1 for p in samples if first_hit(scene, dg, cp, p, own=own) is None)
            print("   totem           x %5.1f..%5.1f y %5.1f..%5.1f  (%s)  %d of %d points seen" % (
                bx[0], bx[1], bx[2], bx[3], first_hit(scene, dg, cp, q, own=own) or "seen", seen, len(samples)))
        try:
            lobs = [o for o in lantern.objects() if o.type == "MESH"]
            if lobs and not _hidden(lobs[0], f):
                bx = _box(scene, cam, [p for o in lobs for p in _obj_pts(o)])
                print("   last lantern    x %5.1f..%5.1f y %5.1f..%5.1f" % bx)
        except Exception as e:                      # noqa
            print("   last lantern    ?", e)
        for ob in notes:
            if _hidden(ob, f):
                continue
            x, _, y, _ = _box(scene, cam, [ob.matrix_world.translation])
            if -5 <= x <= 105 and -5 <= y <= 105:
                print("   note %-22s x %5.1f y %5.1f  world (%.2f, %.2f, %.2f)" % (
                    ob.name, x, y, *ob.matrix_world.translation))
    return 0


def _hidden_any(c, f):
    root = getattr(c, "root", None)
    return root is not None and _hidden(root, f)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
