"""Leg Day, the climb sequence's own probe: where the climbers, their legs and their anvils land in the frame over a
whole shot, for the shot's own camera or for candidate cameras, WITHOUT rendering. One build of one sky.

    $BPY -m tools.legday_climb_probe --sky gold --shot cl11_climb [--every 6]
    $BPY -m tools.legday_climb_probe --sky gold --shot cl11_climb --cam "6,25,0.8>-0.9,42,8.3>28>7,26,1>-0.9,43,9>76"
            a candidate camera: pos>target>lens[>pos1>target1>planned frames] (linear, as _repeat_cam plans it);
            several --cam give v0, v1, ...
    $BPY -m tools.legday_climb_probe ... --set 'CLIMBERS=(("steve", 3.0), ...)'    module constants of
            films/legday_climb.py replaced BEFORE the build (staging variants without editing the file)
Per frame: each climber's head box and face px, his legs' box (feet to hips), his anvil's box, all in % of the frame
(y from the top), and whether the head / the anvil is blocked; then the union box of the heroes the shot declares
(st.hero) and the shelf's anvils (the SHELF set of the shot: centre in %, how much of each is seen: rays to 9 points).
Nothing is written.
"""
import argparse
import ast
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _box(scene, cam, obs, proj):
    """(x0, x1, y0, y1) in % of the frame of the meshes in obs (and their children), or None."""
    from mathutils import Vector
    xs, ys = [], []
    for ob in obs:
        for o in [ob] + list(ob.children_recursive):
            if o.type != "MESH" or o.hide_render:
                continue
            for c in o.bound_box:
                x, y, z = proj(o.matrix_world @ Vector(c))
                if z > 0:
                    xs.append(x)
                    ys.append(y)
    if not xs:
        return None
    return min(xs), max(xs), min(ys), max(ys)


def _fmt(b):
    return "--" if b is None else "x %5.1f..%5.1f y %5.1f..%5.1f" % b


def _union(boxes):
    boxes = [b for b in boxes if b is not None]
    if not boxes:
        return None
    return (min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes))


def _inside(b):
    """Share (0..1) of the box's area inside the safe area x 8-82, y 14-60."""
    if b is None:
        return 0.0
    w = max(0.0, min(b[1], 82) - max(b[0], 8)) * max(0.0, min(b[3], 60) - max(b[2], 14))
    a = max(1e-6, (b[1] - b[0]) * (b[3] - b[2]))
    return w / a


def main(argv):
    """See the module docstring."""
    ap = argparse.ArgumentParser(prog="tools.legday_climb_probe")
    ap.add_argument("--sky", default="gold")
    ap.add_argument("--shot", required=True)
    ap.add_argument("--every", type=int, default=6)
    ap.add_argument("--frames", help="explicit frames 'a,b,c' (absolute)")
    ap.add_argument("--cam", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--shelf", action="store_true", help="also measure the shelf's anvils")
    ap.add_argument("--brief", action="store_true", help="only the union box and the heads")
    args = ap.parse_args(argv)

    from films import legday_climb as M
    for spec in args.set:
        k, v = spec.split("=", 1)
        setattr(M, k.strip(), ast.literal_eval(v.strip()))
        print("[probe] set %s = %r" % (k.strip(), getattr(M, k.strip())))

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    from tools.legday_geo import _own, first_hit
    ses = render.Session("legday", sky=args.sky)
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    s = {x.name: x for x in ses.film.shots}[args.shot]
    row = C.T[args.shot]
    cast = [st.cast[n] for n in sorted(st.in_shot.get(args.shot, ())) if hasattr(st.cast.get(n), "leg_r")]
    heroes = st.heroes.get(args.shot, [])
    if args.frames:
        frames = [int(v) for v in args.frames.split(",")]
    else:
        frames = list(range(s.frame_start, s.frame_end + 1, args.every))
        if frames[-1] != s.frame_end:
            frames.append(s.frame_end)
    shelf = []
    if args.shelf:
        from films import legday_common as LC
        which, idx = LC.SHELF[row.shelf]
        shelf = [getattr(C, which)[i] for i in idx]

    cams = [None] + args.cam
    for ci, spec in enumerate(cams):
        if spec is not None:
            bits = spec.split(">")
            pos = tuple(float(v) for v in bits[0].split(","))
            tgt = tuple(float(v) for v in bits[1].split(","))
            lens = float(bits[2])
            c = dict(pos=pos, target=tgt, lens=lens, fstop=s._fstop or 2.8)
            if len(bits) > 3:
                c["pos1"] = tuple(float(v) for v in bits[3].split(","))
                c["target1"] = tuple(float(v) for v in bits[4].split(","))
                plan = float(bits[5]) if len(bits) > 5 else float(row.frames)
                k = row.frames / plan
                c["pos1"] = tuple(p + (q - p) * k for p, q in zip(c["pos"], c["pos1"]))
                c["target1"] = tuple(p + (q - p) * k for p, q in zip(c["target"], c["target1"]))
            s.lens(lens, c["fstop"])
            s.handheld(0.0, 0)
            if "pos1" in c:
                s.move(c["pos"], c["target"], c["pos1"], c["target1"], ease="linear")
            else:
                s.move(c["pos"], c["target"])
            print("\n[probe] v%d %s" % (ci - 1, spec))
        else:
            print("\n[probe] the shot's own camera")
        cam = s.camera
        scene.camera = cam

        def proj(p):
            co = world_to_camera_view(scene, cam, p)
            return co.x * 100.0, (1.0 - co.y) * 100.0, co.z

        worst = 1.0
        for f in frames:
            scene.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            cp = cam.matrix_world.translation.copy()
            words = [w for w, wf in row.words if wf <= f]
            print(" f %d (+%d) %s  cam (%.2f, %.2f, %.2f)" % (f, f - s.frame_start, words[-1] if words else "",
                                                              cp.x, cp.y, cp.z))
            for p in cast:
                hb = _box(scene, cam, [p.head], proj)
                eye = Vector(p.eye_point(f))
                d = eye - cp
                side = d.cross(Vector((0, 0, 1)))
                side = side.normalized() * 0.25 if side.length > 1e-6 else Vector((0.25, 0, 0))
                face = abs(proj(eye - side)[0] - proj(eye + side)[0]) / 100.0 * 540
                hy = p.head.matrix_world.to_euler().z
                nose = Vector((math.sin(hy), -math.cos(hy), 0.0))
                tc = Vector((cp.x - eye.x, cp.y - eye.y, 0.0))
                off = math.degrees(math.acos(max(-1.0, min(1.0, nose.dot(tc.normalized()))))) if tc.length else 0
                if args.brief:
                    print("   %-10s head %s face %3.0f px off %3.0f %s" % (
                        p.name, _fmt(hb), face, off, first_hit(scene, dg, cp, eye, own=_own(p)) or "clear"))
                    continue
                lb = _box(scene, cam, [p.leg_r, p.leg_l], proj)
                it = p.item("right", f)
                ab = _box(scene, cam, [it], proj) if it is not None else None
                ap_ = it.matrix_world.translation.copy() if it is not None else None
                print("   %-10s head %s face %3.0f px off %3.0f %-14s | legs %s | anvil %s %s" % (
                    p.name, _fmt(hb), face, off, first_hit(scene, dg, cp, eye, own=_own(p)) or "clear", _fmt(lb),
                    _fmt(ab), (first_hit(scene, dg, cp, ap_, own=_own(p) | {it.name}) or "clear") if ap_ else ""))
            for label, obs in heroes:
                u = _box(scene, cam, obs, proj)
                share = _inside(u)
                worst = min(worst, share)
                print("   HERO %-8s %s  inside %3.0f %%" % (label, _fmt(u), 100 * share))
            if shelf:
                seen = []
                for a in shelf:
                    obs = [a.object] if hasattr(a, "object") and a.object is not None else [a]
                    try:
                        obs = list(a.objects()) if callable(getattr(a, "objects", None)) else obs
                    except Exception:
                        pass
                    b = _box(scene, cam, obs, proj)
                    loc = obs[0].matrix_world.translation
                    pts = [Vector((loc.x + dx, loc.y + dy, loc.z + dz)) for dx in (0.2, 0.5, 0.8)
                           for dy in (0.5,) for dz in (0.3, 0.6, 0.9)]
                    vis = sum(1 for q in pts if first_hit(scene, dg, cp, q, own={o.name for o in obs}) is None)
                    seen.append("%s:%s %d/9" % (a.name[-6:], "--" if b is None else "%2.0f,%2.0f" % (
                        (b[0] + b[1]) / 2, (b[2] + b[3]) / 2), vis))
                print("   SHELF " + "  ".join(seen))
        print(" [probe] worst hero share inside the safe area: %3.0f %%" % (100 * worst))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
