"""Six Seconds, PIT sequence: measure figures and dropped items of one shot over frames without rendering (one build
of the "wastes" sky). Where each one is in the world and in the shot's frame (x / y in % from the top left, as the
Reels zones), whether it is hidden that frame, and the closest approach between figures. The pit director's own
tool (tools/sixseconds_geo.py measures heads and faces; this one follows items and bodies through a span).

    $BPY -m tools.sixseconds_pit_probe pt07_pearl:436-510:6 [--who ender_pearl_pt7,piglin_pt1] [--near]
        every STEP frames: each named cast member (default: the whole cast of the shot): feet / item position,
        x / y in the frame, hidden or shown; --near: the closest distance between any two figures of the shot
        over the span (piglins, brute, runner: their boxes are 0.6 wide)
Nothing is written. Prefix with `nice -n 12 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    """See the module docstring."""
    import argparse
    ap = argparse.ArgumentParser(prog="tools.sixseconds_pit_probe")
    ap.add_argument("span", help="SHOT:F0-F1[:STEP]")
    ap.add_argument("--who", help="cast names (default: the shot's whole cast)")
    ap.add_argument("--near", action="store_true", help="closest approach between figures")
    ap.add_argument("--sky", default="wastes")
    args = ap.parse_args(argv)

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    ses = render.Session("sixseconds", sky=args.sky)
    scene, st = ses.scene, ses.result["stage"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = {s.name: s for s in ses.film.shots}
    bits = args.span.split(":")
    s = shots[bits[0]]
    f0, f1 = (int(v) for v in bits[1].split("-"))
    step = int(bits[2]) if len(bits) > 2 else 6
    names = [n.strip() for n in args.who.split(",")] if args.who else sorted(st.in_shot.get(s.name, ()))
    frames = list(range(f0, f1 + 1, step)) + ([f1] if (f1 - f0) % step else [])
    figs = [n for n in names if hasattr(st.cast.get(n), "eye_point")]
    closest = {}
    for f in frames:
        scene.frame_set(f)
        cam = s.camera
        print("[probe] %s frame %d" % (s.name, f))
        for n in names:
            c = st.cast.get(n)
            if c is None:
                print("  %-22s not in the cast" % n)
                continue
            if hasattr(c, "spinner"):                                   # a dropped item: its spinner's world point
                ob = c.spinner
                p = ob.matrix_world.translation.copy()
                shown = not any(not cp.hide_render for cp in c.copies) and False or any(
                    not cp.hide_render for cp in c.copies)
            else:
                p = Vector(c.pos_at(f))
                ob = c.root
                shown = not c.root.hide_render if hasattr(c.root, "hide_render") else True
                parts = [o for o in ob.children_recursive if o.type == "MESH"]
                shown = any(not o.hide_render for o in parts) if parts else shown
            co = world_to_camera_view(scene, cam, p)
            extra = ""
            if hasattr(c, "eye_point"):
                e = world_to_camera_view(scene, cam, Vector(c.eye_point(f)))
                extra = "  eyes x %5.1f y %5.1f" % (e.x * 100, (1 - e.y) * 100)
            print("  %-22s (%6.2f, %6.2f, %6.2f)  x %5.1f y %5.1f  %s%s" % (
                n, p.x, p.y, p.z, co.x * 100, (1 - co.y) * 100, "shown" if shown else "hidden", extra))
        if args.near:
            for i, a in enumerate(figs):
                for b in figs[i + 1:]:
                    pa, pb = Vector(st.cast[a].pos_at(f)), Vector(st.cast[b].pos_at(f))
                    d = math.hypot(pa.x - pb.x, pa.y - pb.y)
                    if abs(pa.z - pb.z) < 1.5 and (closest.get((a, b)) is None or d < closest[(a, b)][0]):
                        closest[(a, b)] = (d, f)
    if args.near:
        print("[probe] closest approach (same level):")
        for (a, b), (d, f) in sorted(closest.items(), key=lambda kv: kv[1][0]):
            print("  %-20s %-20s %.2f at %d" % (a, b, d, f))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
