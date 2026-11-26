"""Six Seconds: measure a frame without rendering it: where every head lands in the picture, how big the face is,
which way it faces the lens, and what (if anything) stands between the lens and it. One build of one sky.
(The Hello's tools/hello_geo.py, for piglins, the brute and the runner.)

    $BPY -m tools.sixseconds_geo --sky wastes rw22_six:1440 gt03_guard:209
    $BPY -m tools.sixseconds_geo --sky wastes "gt01_landing:49:0.6,17.2,5.6>6.0,13.6,3.4>26"   # another camera
                                                       # (pos>target>lens): candidate framings without a render
    $BPY -m tools.sixseconds_geo --sky wastes pt08_gravel:530 --pts "3.85,6.55,0.1;3.6,7.0,0.2"   # any 3D points
                                                       # (items, the step ingot, the boots): x / y and what hides them
    $BPY -m tools.sixseconds_geo --sky wastes gt19_older:1173 --track runner_gt:1173-1282:6    # a figure's feet and
                                                       # head over a span (exits, passes, the match cut)
    $BPY -m tools.sixseconds_geo --sky soul br11_boots:725 --boots runner_br     # the golden boots' box in the frame
Columns: x / y in % of the frame (y from the top, as the Reels zones: faces and hero props inside x 8-82 %, y 14-60 %,
nothing essential in y 62-72 % or below 86 %), the head's box (left..right, top..bottom), the face width in pixels
at 540x960 (a piglin's or brute's head is 10 game pixels = 0.625 block wide, a player's 8 = 0.5; a baby piglin's
half a piglin's), `off` = degrees between the head's nose direction and the lens (0 = facing it, 90 = profile,
180 = from behind; a piglin's head turns at most 75 from its body), `pitch` = the head's tilt (+ = up), `blocked` =
the first rendered object on the line from the lens to the eyes (None = clear). Nothing is written. Prefix with
`nice -n 15 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def first_hit(scene, dg, a, b, own=None):
    """Name of the first rendered (camera-visible) object between a and b, or None when the line is clear. Objects
    whose name starts with `own` (the character measured: its own head around its eyes) do not count."""
    d = b - a
    length = d.length
    d.normalize()
    o, gone = a.copy(), 0.0
    for _ in range(60):
        hit, loc, _n, _i, ob, _m = scene.ray_cast(dg, o, d, distance=length - gone - 0.04)
        if not hit:
            return None
        orig = ob.original if hasattr(ob, "original") else ob
        mine = own is not None and orig.name.startswith(own)
        if mine or orig.hide_render or not orig.visible_camera or "glass" in orig.name:     # (glass: looked through)
            step = (loc - o).length + 0.01
            o = loc + d * 0.01
            gone += step
            continue
        return "%s@%.2f" % (orig.name.replace("bastion_block_", ""), (loc - a).length)
    return "?"


def box_of(obs):
    """World-space bounding box corners of the rendered meshes among `obs` and their children."""
    from mathutils import Vector
    pts = []
    for top in obs:
        for ob in [top] + list(top.children_recursive):
            if ob.type != "MESH" or ob.hide_render:
                continue
            for corner in ob.bound_box:
                pts.append(ob.matrix_world @ Vector(corner))
    return pts


def half_face(c):
    """Half the width of a character's face in blocks: piglin / brute 10 game pixels, a baby piglin 5 (its head is
    drawn at half size), a player 8."""
    from engine import piglins
    if isinstance(c, piglins.Piglin):
        return 0.15625 if c.baby else 0.3125
    return 0.25


def main(argv):
    """See the module docstring."""
    import argparse
    ap = argparse.ArgumentParser(prog="tools.sixseconds_geo")
    ap.add_argument("--sky", default="wastes")
    ap.add_argument("--who", help="cast names (default: everybody in the shot)")
    ap.add_argument("--pts", help="extra 3D points 'x,y,z;x,y,z'")
    ap.add_argument("--track", help="NAME:F0-F1[:STEP] a figure's feet and eyes over a span")
    ap.add_argument("--boots", help="a runner's cast name: where his golden boots land in the frame")
    ap.add_argument("queries", nargs="+", help="SHOT:FRAME[:x,y,z>tx,ty,tz[>lens]]")
    args = ap.parse_args(argv)

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    ses = render.Session("sixseconds", sky=args.sky)
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = {s.name: s for s in ses.film.shots}

    def proj(cam, p):
        co = world_to_camera_view(scene, cam, p)
        return co.x * 100.0, (1.0 - co.y) * 100.0, co.z

    for q in args.queries:
        parts = q.split(":")
        sname, f = parts[0], int(parts[1])
        s = shots[sname]
        if st.sky_at(f) not in (None, args.sky):
            print("[geo] %s frame %d is filmed under sky %r: run with --sky %s" % (sname, f, st.sky_at(f),
                                                                                st.sky_at(f)))
            continue
        if len(parts) > 2:
            bits = parts[2].split(">")
            pos = tuple(float(v) for v in bits[0].split(","))
            tgt = tuple(float(v) for v in bits[1].split(","))
            if len(bits) > 2:
                s.lens(float(bits[2]), s._fstop)
            s.move(pos, tgt)
        scene.frame_set(f)
        cam = s.camera
        scene.camera = cam
        dg = bpy.context.evaluated_depsgraph_get()
        cp = cam.matrix_world.translation.copy()
        print("\n[geo] %s frame %d  sky %s  camera (%.2f, %.2f, %.2f)  lens %.0f mm" % (
            sname, f, st.sky_at(f), cp.x, cp.y, cp.z, cam.data.lens))
        names = [n.strip() for n in args.who.split(",")] if args.who else sorted(st.in_shot.get(sname, ()))
        for n in names:
            c = st.cast.get(n)
            if c is None or not hasattr(c, "eye_point") or not hasattr(c, "head"):
                continue
            eye = Vector(c.eye_point(f))
            x, y, depth = proj(cam, eye)
            box = [proj(cam, p) for p in box_of([c.head])]
            top = min(b[1] for b in box) if box else float("nan")
            bot = max(b[1] for b in box) if box else float("nan")
            xl = min(b[0] for b in box) if box else float("nan")
            xr = max(b[0] for b in box) if box else float("nan")
            d = eye - cp
            half = half_face(c)
            side = d.cross(Vector((0, 0, 1)))
            side = side.normalized() * half if side.length > 1e-6 else Vector((half, 0, 0))
            a, b = proj(cam, eye - side), proj(cam, eye + side)
            face = abs(a[0] - b[0]) / 100.0 * 540
            m = c.head.matrix_world.to_3x3()
            nose = (m @ Vector((0.0, -1.0, 0.0)))                 # a head faces -Y in its own frame
            flat = Vector((nose.x, nose.y, 0.0))
            pitch = math.degrees(math.atan2(nose.z, flat.length)) if flat.length > 1e-6 else 90.0
            to_cam = Vector((cp.x - eye.x, cp.y - eye.y, 0.0))
            off = (math.degrees(math.acos(max(-1.0, min(1.0, flat.normalized().dot(to_cam.normalized())))))
                   if to_cam.length > 1e-6 and flat.length > 1e-6 else 0.0)
            print("  %-18s eyes x %5.1f y %5.1f  head x %5.1f..%5.1f y %5.1f..%5.1f  face %4.0f px  off %5.1f  "
                  "pitch %+5.1f  dist %5.2f  blocked %s" % (n, x, y, xl, xr, top, bot, face, off, pitch, d.length,
                                                            first_hit(scene, dg, cp, eye, own=n + "_")))
        for spec in (args.pts or "").split(";"):
            if not spec.strip():
                continue
            p = Vector(tuple(float(v) for v in spec.split(",")))
            x, y, depth = proj(cam, p)
            print("  point %-22s x %5.1f y %5.1f  dist %5.2f  blocked %s" % (spec, x, y, (p - cp).length,
                                                                          first_hit(scene, dg, cp, p)))
        if args.boots:
            runner = st.cast[args.boots]
            obs = C.boots_of(runner)
            box = [proj(cam, p) for p in box_of(obs)]
            if box:
                from films import sixseconds_common as SC
                bf = SC.BOOT_FRAME
                print("  boots of %-12s x %5.1f..%5.1f y %5.1f..%5.1f  (BOOT_FRAME x %g..%g y %g..%g)" % (
                    args.boots, min(b[0] for b in box), max(b[0] for b in box), min(b[1] for b in box),
                    max(b[1] for b in box), bf["x"][0], bf["x"][1], bf["y"][0], bf["y"][1]))
            else:
                print("  boots of %s: not rendered on this frame" % args.boots)
        if args.track:
            bits = args.track.split(":")
            c = st.cast[bits[0]]
            f0, f1 = (int(v) for v in bits[1].split("-"))
            step = int(bits[2]) if len(bits) > 2 else 6
            for g in list(range(f0, f1 + 1, step)) + ([f1] if (f1 - f0) % step else []):
                scene.frame_set(g)
                feet = Vector(c.pos_at(g))
                eye = Vector(c.eye_point(g))
                fx_, fy_, _ = proj(cam, feet)
                ex, ey, _ = proj(cam, eye)
                print("  track %-12s %4d  feet (%6.2f, %6.2f, %5.2f) x %5.1f y %5.1f   eyes x %5.1f y %5.1f" % (
                    bits[0], g, feet.x, feet.y, feet.z, fx_, fy_, ex, ey))
            scene.frame_set(f)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
