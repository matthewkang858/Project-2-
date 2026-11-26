"""Six Seconds, BRIDGE sequence (films/sixseconds_bridge.py): the bridge director's probe. No render, nothing written.

    $BPY -m tools.sixseconds_bridge_probe ingots
        the three thrown ingots (films/sixseconds_bridge.py _ingots): throw, first touch and still frames, where each
        comes to rest against its shared spot six_bridge_ingot_k, and whether its flight clears the netherrack pillar
        (the pillar is not in the bastion's World, so piglins.item_track does not see it) and the brute's head
    $BPY -m tools.sixseconds_bridge_probe fly br14_zero:898-925[:STEP] [--cam "x,y,z>tx,ty,tz>lens"]
        each ingot's position in the frame (x / y in % of a 540x960 frame, y from the top) frame by frame, with the
        brute's eyes and the runner's eyes, for the shot's camera or a candidate one
Prefix with `nice -n 12 timeout 290`. One build of the sky "soul".
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _span(text):
    """'a-b[:step]' or 'a' -> list of frames."""
    bits = text.split(":")
    step = int(bits[1]) if len(bits) > 1 else 1
    if "-" in bits[0]:
        a, b = (int(v) for v in bits[0].split("-"))
        return list(range(a, b + 1, step))
    return [int(bits[0])]


def main(argv):
    """See the module docstring."""
    import argparse
    ap = argparse.ArgumentParser(prog="tools.sixseconds_bridge_probe")
    ap.add_argument("mode", choices=("ingots", "fly"))
    ap.add_argument("query", nargs="?", help="SHOT:A-B[:STEP] (fly)")
    ap.add_argument("--cam", help="pos>target>lens: a candidate camera instead of the shot's")
    args = ap.parse_args(argv)

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    from films import sixseconds_bridge as B
    ses = render.Session("sixseconds", sky="soul")
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    ingots = C.memo["br_ingots"]
    brute = st.cast["brute_br"]

    if args.mode == "ingots":
        x0, x1, y0, y1, top = 400.0, 401.0, 19.0, 20.0, 3.0          # the pillar's three blocks (cells z 0..2)
        half = 0.125                                                  # the item entity's box: 0.25
        for g in ingots:
            rest = Vector(g["track"][-1][1])
            spot = Vector(C.P(g["spot"]))
            clash = [(t, p) for t, p in g["track"]
                     if x0 - half < p[0] < x1 + half and y0 - half < p[1] < y1 + half and p[2] < top - 1e-6]
            heads = [ob for ob in [brute.head] + list(brute.head.children_recursive) if ob.type == "MESH"]
            body = [ob for ob in brute.root.children_recursive if ob.type == "MESH" and ob not in heads]

            def gap(q, obs):
                """Distance from the point q to the nearest of the objects' own (local) boxes, in blocks."""
                out = 9.0
                for ob in obs:
                    if ob.hide_render:
                        continue
                    loc = ob.matrix_world.inverted() @ q
                    lo = Vector([min(c[i] for c in ob.bound_box) for i in range(3)])
                    hi = Vector([max(c[i] for c in ob.bound_box) for i in range(3)])
                    d = Vector([max(lo[i] - loc[i], 0.0, loc[i] - hi[i]) for i in range(3)])
                    sc = ob.matrix_world.to_scale()
                    out = min(out, Vector((d.x * sc.x, d.y * sc.y, d.z * sc.z)).length)
                return out

            near_h, near_b = [], []
            for t, p in g["track"]:
                f = g["throw"] + t * 1.2
                if p[2] < 0.3:                                           # on the deck: past the brute
                    break
                scene.frame_set(int(round(f)))
                q = Vector(p) + Vector((0.0, 0.0, 0.125))                # the middle of the item's box
                near_h.append((gap(q, heads), f, p))
                near_b.append((gap(q, body), f, p))
            dh, fh, ph = min(near_h)
            db, fb, pb = min(near_b)
            print("[bridge] %s  pitch %+.0f  throw %d  touches %.1f  still %d  rest (%.3f, %.3f, %.3f)  spot %s"
                  "  miss %.3f  pillar %s  item centre to the brute's head %.2f at %.1f (z %.2f), to his body / "
                  "axe %.2f at %.1f (z %.2f)  (a dropped ingot's opaque half-width is 0.22)" % (
                      g["item"].name, math.degrees(g["pitch"]), g["throw"], g["land"], g["still"], rest.x, rest.y,
                      rest.z, g["spot"], (rest - spot).length,
                      "CLEAR" if not clash else "HITS at tick %d" % clash[0][0], dh, fh, ph[2], db, fb, pb[2]))
        return 0

    sname, rest = args.query.split(":", 1)
    s = {x.name: x for x in ses.film.shots}[sname]
    if args.cam:
        bits = args.cam.split(">")
        s.lens(float(bits[2]) if len(bits) > 2 else s.camera.data.lens, s._fstop)
        s.move(tuple(float(v) for v in bits[0].split(",")), tuple(float(v) for v in bits[1].split(",")))
    cam = s.camera
    scene.camera = cam
    runner = st.cast.get("runner_br")
    for f in _span(rest):
        scene.frame_set(f)
        row = ["%4d" % f]
        for g in ingots:
            it = g["item"]
            p = it.spinner.matrix_world.translation
            vis = not it.copies[0].hide_render
            co = world_to_camera_view(scene, cam, p)
            row.append("%s %5.1f %5.1f%s" % (it.name[-1], co.x * 100, (1 - co.y) * 100, "" if vis else " (hidden)"))
        for who in (brute, runner):
            if who is None:
                continue
            co = world_to_camera_view(scene, cam, Vector(who.eye_point(f)))
            row.append("%s eyes %5.1f %5.1f" % (who.name.split("_")[0], co.x * 100, (1 - co.y) * 100))
        print("  ".join(row))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
