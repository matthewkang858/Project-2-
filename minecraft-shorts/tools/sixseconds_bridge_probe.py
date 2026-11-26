"""Six Seconds, BRIDGE sequence (films/sixseconds_bridge.py): the bridge director's probe. No render, nothing written.

    $BPY -m tools.sixseconds_bridge_probe ingots
        the three thrown ingots (films/sixseconds_bridge.py _ingots): throw, first touch and still frames, where each
        comes to rest against its shared spot six_bridge_ingot_k, and whether its flight clears the netherrack pillar
        (the pillar is not in the bastion's World, so piglins.item_track does not see it) and the brute's head
    $BPY -m tools.sixseconds_bridge_probe fly br14_zero:898-925[:STEP] [--cam "x,y,z>tx,ty,tz>lens"]
        each ingot's position in the frame (x / y in % of a 540x960 frame, y from the top) and the degrees between its
        broad side and the lens (0 = broad side, 90 = edge-on) frame by frame, with the brute's eyes and the runner's
        eyes, for the shot's camera or a candidate one
    $BPY -m tools.sixseconds_bridge_probe clip
        the exact clip test of the thrown ingots: every vertex of each ingot's sprite (world space, at quarter frames
        from its throw to its landing) against every box of the brute (head, ears, arms, axe ...): the smallest
        clearance and the sub-frames where a vertex is inside a box (and how deep)
    $BPY -m tools.sixseconds_bridge_probe gap br15_wait:953-998[:STEP] [--cam "x,y,z>tx,ty,tz>lens"]
        the screen gap in px at 540x960 between the runner's whole silhouette (each mesh box, armour and held item
        included, projected and filled) and the brute's head with its ears; negative = overlap in px
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
    ap.add_argument("mode", choices=("ingots", "fly", "clip", "gap"))
    ap.add_argument("query", nargs="?", help="SHOT:A-B[:STEP] (fly, gap)")
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

    if args.mode == "clip":
        return _clip(scene, brute, ingots)

    sname, rest = args.query.split(":", 1)
    s = {x.name: x for x in ses.film.shots}[sname]
    if args.cam:
        bits = args.cam.split(">")
        s.lens(float(bits[2]) if len(bits) > 2 else s.camera.data.lens, s._fstop)
        s.move(tuple(float(v) for v in bits[0].split(",")), tuple(float(v) for v in bits[1].split(",")))
    cam = s.camera
    scene.camera = cam
    if args.mode == "gap":
        return _gap(scene, cam, brute, st.cast["runner_br"], _span(rest))
    runner = st.cast.get("runner_br")
    for f in _span(rest):
        scene.frame_set(f)
        row = ["%4d" % f]
        for g in ingots:
            it = g["item"]
            p = it.spinner.matrix_world.translation
            vis = not it.copies[0].hide_render
            co = world_to_camera_view(scene, cam, p)
            n = it.spinner.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))      # the sprite's face normal
            to = cam.matrix_world.translation - p
            n2, t2 = Vector((n.x, n.y)), Vector((to.x, to.y))
            ang = 0.0
            if n2.length > 1e-6:
                ang = math.degrees(math.acos(min(1.0, abs(n2.normalized().dot(t2.normalized())))))
            row.append("%s %5.1f %5.1f %2.0f%s" % (it.name[-1], co.x * 100, (1 - co.y) * 100, ang,
                                                 "" if vis else " (hidden)"))
        for who in (brute, runner):
            if who is None:
                continue
            co = world_to_camera_view(scene, cam, Vector(who.eye_point(f)))
            row.append("%s eyes %5.1f %5.1f" % (who.name.split("_")[0], co.x * 100, (1 - co.y) * 100))
        print("  ".join(row))
    return 0


def _boxes(obs):
    """[(object, local lo, local hi, world scale)] of the rendered meshes among obs."""
    from mathutils import Vector
    out = []
    for ob in obs:
        if ob.type != "MESH" or ob.hide_render:
            continue
        lo = Vector([min(c[i] for c in ob.bound_box) for i in range(3)])
        hi = Vector([max(c[i] for c in ob.bound_box) for i in range(3)])
        out.append((ob, lo, hi, ob.matrix_world.to_scale()))
    return out


def _clip(scene, brute, ingots):
    """See the module docstring (mode clip)."""
    import bpy
    from mathutils import Vector
    parts = [ob for ob in brute.root.children_recursive if ob.type == "MESH"]
    for g in ingots:
        it = g["item"]
        a, b = int(g["throw"]) + 1, int(g["land"]) + 2
        worst, wf, wp, inside = 9.0, None, None, {}
        for q in range(a * 4, b * 4):
            f = q / 4.0
            scene.frame_set(int(f), subframe=f - int(f))
            dg = bpy.context.evaluated_depsgraph_get()
            verts = []
            for ob in it.copies:
                if ob.type != "MESH" or ob.hide_render:
                    continue
                ev = ob.evaluated_get(dg)
                verts += [ev.matrix_world @ v.co for v in ev.data.vertices]
            if not verts:
                continue
            for ob, lo, hi, sc in _boxes(parts):
                inv = ob.matrix_world.inverted()
                for w in verts:
                    loc = inv @ w
                    d = Vector([max(lo[i] - loc[i], 0.0, loc[i] - hi[i]) * sc[i] for i in range(3)]).length
                    if d == 0.0:
                        depth = min(min(loc[i] - lo[i], hi[i] - loc[i]) * sc[i] for i in range(3))
                        key = (f, ob.name.replace(brute.name + "_", ""))
                        inside[key] = max(inside.get(key, 0.0), depth)
                        d = -depth
                    if d < worst:
                        worst, wf, wp = d, f, ob.name.replace(brute.name + "_", "")
        frames = sorted(set(f for f, _n in inside))
        print("[clip] %s  throw %d  touches %.1f  nearest vertex %.3f at %.2f (%s)  inside a box on %d quarter "
              "frames%s" % (it.name, g["throw"], g["land"], worst, wf, wp, len(frames),
                            (": %.2f-%.2f (%s, deepest %.3f)" % (frames[0], frames[-1],
                                                                 ", ".join(sorted(set(n for _f, n in inside))),
                                                                 max(inside.values()))) if frames else ""))
    return 0


def _gap(scene, cam, brute, runner, frames):
    """See the module docstring (mode gap)."""
    import numpy as np
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    from PIL import Image, ImageDraw
    W, H = 540, 960
    heads = [ob for ob in [brute.head] + list(brute.head.children_recursive) if ob.type == "MESH"]
    body = [ob for ob in [runner.root] + list(runner.root.children_recursive) if ob.type == "MESH"]

    def hull(pts):
        pts = sorted(set(pts))
        if len(pts) < 3:
            return pts

        def cross(o, p, q):
            return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
        lo, up = [], []
        for p in pts:
            while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
                lo.pop()
            lo.append(p)
        for p in reversed(pts):
            while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
                up.pop()
            up.append(p)
        return lo[:-1] + up[:-1]

    def mask(obs):
        im = Image.new("L", (W, H), 0)
        dr = ImageDraw.Draw(im)
        for ob in obs:
            if ob.hide_render:
                continue
            pts = []
            for c in ob.bound_box:
                co = world_to_camera_view(scene, cam, ob.matrix_world @ Vector(c))
                if co.z > 0:
                    pts.append((co.x * W, (1 - co.y) * H))
            hp = hull(pts)
            if len(hp) >= 3:
                dr.polygon(hp, fill=255)
            elif len(hp) == 2:
                dr.line(hp, fill=255)
        return np.array(im) > 0

    def box(m):
        ys, xs = np.nonzero(m)
        return "x %4.1f-%4.1f y %4.1f-%4.1f" % (xs.min() / W * 100, xs.max() / W * 100, ys.min() / H * 100,
                                                 ys.max() / H * 100) if len(xs) else "none"

    for f in frames:
        scene.frame_set(f)
        r, h = mask(body), mask(heads)
        if (r & h).any():
            gap = -int((r & h).sum())
        else:
            ya, xa = np.nonzero(r)
            yb, xb = np.nonzero(h)
            pa = np.stack([xa, ya], 1)[:: max(1, len(xa) // 4000)].astype(np.float32)
            pb = np.stack([xb, yb], 1)[:: max(1, len(xb) // 4000)].astype(np.float32)
            best = min(float(((pa[i:i + 500, None, :] - pb[None, :, :]) ** 2).sum(-1).min())
                       for i in range(0, len(pa), 500))
            gap = round(best ** 0.5, 1)
        print("%4d  runner to brute head %6s px   runner %s (%.0f %% of it beyond x 82 %%, %.0f %% above y 14 %%)"
              "   brute head %s" % (f, gap, box(r), 100.0 * (1 - r[:, :int(0.82 * W)].sum() / max(1, r.sum())),
                                    100.0 * r[:int(0.14 * H)].sum() / max(1, r.sum()), box(h)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
