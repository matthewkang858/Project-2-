"""The Hello, door_gold sequence: scouting probes that never touch the film's files.

    $BPY -m tools.hello_door_gold_probe door                      # house_a's door: crack stage and swing keys
    $BPY -m tools.hello_door_gold_probe variant --frames 226,1480 --exec "CODE" [--res 540x960] [--samples 16]
        builds the film (sky gold), runs CODE with C (the Hello context), st (the Stage), S (shots by name) and
        the sequence module G (films.hello_door_gold) in scope (e.g. re-key a head), then renders the frames to
        the scratch directory given by --dir (default out/test, prefix hello_dg_var).

One build per call (sky gold). Prefix with `nice -n 5 timeout 290`. Nothing in films/ or engine/ is written.
"""
import argparse
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _session():
    import render
    t = time.time()
    ses = render.Session("hello", sky="gold")
    print("[dg_probe] built in %.1f s" % (time.time() - t))
    return ses


def cmd_door(args):
    """Print the door's crack stage around dg20 and its rotation keys."""
    from engine import breaking
    ses = _session()
    C = ses.result["context"]
    for f in (1250, 1257, 1258, 1266, 1268, 1274, 1300):
        print("[dg_probe] door crack stage at %d: %d" % (f, breaking.stage_at(C.door, f)))
    for d in C.v._door_sets["house_a"]:
        ad = d.animation_data
        if ad and ad.action:
            for fc in getattr(ad.action, "fcurves", []):
                if fc.data_path == "rotation_euler":
                    keys = [(round(k.co.x, 2), round(k.co.y, 3)) for k in fc.keyframe_points if 1240 <= k.co.x <= 1360]
                    print("[dg_probe] %s rotation[%d] keys 1240-1360: %s" % (d.name, fc.array_index, keys))
    return 0


def cmd_variant(args):
    """Run a snippet on the built film, then render frames."""
    from films import hello_door_gold as G
    ses = _session()
    C, st = ses.result["context"], ses.result["stage"]
    S = {s.name: s for s in ses.film.shots}
    if args.exec:
        exec(args.exec, dict(C=C, st=st, S=S, G=G, HC=sys.modules["films.hello_common"]))
    res = tuple(int(v) for v in args.res.lower().split("x"))
    ses.configure(res, args.samples, args.threads, True)
    os.makedirs(args.dir, exist_ok=True)
    for f in [int(v) for v in args.frames.split(",")]:
        path = os.path.join(args.dir, "%s_%d.png" % (args.name, f))
        t = time.time()
        ses.render_frame(f, path)
        print("[dg_probe] frame %d -> %s  %.1f s" % (f, path, time.time() - t))
        if args.zones:
            from PIL import Image
            from engine import post
            with Image.open(path) as im:
                post.draw_zones(im).save(path[:-4] + "_zones.png")
    return 0


def _box(obs):
    """World bounding box [xmin, ymin, zmin, xmax, ymax, zmax] of the meshes among obs."""
    from mathutils import Vector
    pts = []
    for ob in obs:
        if ob.type == "MESH" and not ob.hide_render:
            pts += [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [min(p[i] for p in pts) for i in range(3)] + [max(p[i] for p in pts) for i in range(3)]


def _overlap(a, b, tol=0.01):
    return all(a[i] < b[i + 3] - tol and b[i] < a[i + 3] - tol for i in range(3))


def _solid_top(x, y):
    """Top of what is under (x, y) at house_a's door: the oak stairs (9, -8): low half x 9..9.5 at z 0.5, high half
    x 9.5..10 at z 1.0; the door cell and the floor x >= 10 (y -8..-7) at z 1.0; the plaza 0."""
    if -8 <= y < -7:
        if 9 <= x < 9.5:
            return 0.5
        if x >= 9.5:
            return 1.0
    return 0.0


def _hull(pts):
    """2D convex hull (monotone chain), counter-clockwise."""
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def _inside(p, poly):
    """p inside the convex counter-clockwise polygon."""
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < 0:
            return False
    return n >= 3


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def hull_gap(pa, pb):
    """Gap between the convex hulls of two 2D point sets (0 when they touch or overlap)."""
    A, B = _hull(pa), _hull(pb)
    if any(_inside(p, B) for p in A) or any(_inside(p, A) for p in B):
        return 0.0
    d = 1e9
    for P, Q in ((A, B), (B, A)):
        for p in P:
            for i in range(len(Q)):
                d = min(d, _seg_dist(p, Q[i], Q[(i + 1) % len(Q)]))
    return d


def _verts(obs):
    """World positions of the vertices of the visible meshes among obs."""
    out = []
    for ob in obs:
        if ob.type == "MESH" and not ob.hide_render:
            mw = ob.matrix_world
            out += [mw @ v.co for v in ob.data.vertices]
    return out


def cmd_check(args):
    """dg20: per frame, the walking child's feet against the step, its parts against the flesh and the door, the
    door's state; then, for candidate end positions of WALK_CAM (--cams "x,y,z>tx,ty,tz;..."), the gap in the frame
    between the silhouettes of the flesh and the child's head over 1300-1357 (pixels at 540x960); then dg21: where the flesh would be in its frame."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    from films import hello_door_gold as G
    ses = _session()
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    S = {s.name: s for s in ses.film.shots}
    kid, flesh = st.cast["child_dg2"], st.cast["rotten_flesh_dg"]
    doors = C.v._door_sets["house_a"]
    parts = {"head": [kid.head], "body": [kid.body], "legs": [kid.leg_l, kid.leg_r],
             "arms": [o for o in bpy.data.objects if o.name == "child_dg2_arms"]}
    worst, bad = 0.0, []
    for f in range(1266, 1318):
        scene.frame_set(f)
        fb = _box(flesh.copies)
        pb = {k: _box(v) for k, v in parts.items() if v}
        lb = pb["legs"]
        sink = max(_solid_top(lb[0] + u * (lb[3] - lb[0]), lb[1] + v * (lb[4] - lb[1])) - lb[2]
                   for u in (0.1, 0.5, 0.9) for v in (0.1, 0.5, 0.9))
        worst = max(worst, sink)
        fl = [k for k, b in pb.items() if _overlap(b, fb)]
        dl = [k for k, b in pb.items() for d in doors if _overlap(b, _box([d] + list(d.children_recursive)))]
        r = kid.root.matrix_world.translation
        door = math.degrees(doors[0].rotation_euler[2] - doors[0]["closed_yaw"])
        if sink > 0.02 or fl or dl:
            bad.append(f)
        print("[dg_probe] %d root (%.2f, %.2f, %.3f) feet %+.3f below the top  flesh %s  door %s  door %.0f deg"
              % (f, r.x, r.y, r.z, sink, fl, dl, door))
    print("[dg_probe] worst sink %.3f  frames with a problem: %s" % (worst, bad))

    def proj(cam, p):
        co = world_to_camera_view(scene, cam, Vector(p))
        return co.x * 100.0, (1.0 - co.y) * 100.0

    s = S["dg20_walkup"]
    base = dict(G.WALK_CAM)
    cands = [("now", base["pos1"], base["target1"])]
    for spec in (args.cams or "").split(";"):
        if spec.strip():
            a, b = spec.split(">")
            cands.append((spec, tuple(float(v) for v in a.split(",")), tuple(float(v) for v in b.split(","))))
    for label, p1, t1 in cands:
        s.move(base["pos"], base["target"], p1, t1, ease="ease_out")
        worst_gap, at, gaps = 1e9, None, []
        for f in range(1300, 1358):
            scene.frame_set(f)
            cam = s.camera
            px = lambda v: (proj(cam, v)[0] * 5.4, proj(cam, v)[1] * 9.6)      # pixels at 540x960
            gap = hull_gap([px(v) for v in _verts(flesh.copies)],
                           [px(v) for v in _verts([kid.head] + list(kid.head.children_recursive))])
            gaps.append(gap)
            if gap < worst_gap:
                worst_gap, at = gap, f
        scene.frame_set(1338)
        cam = s.camera
        eye = kid.eye_point(1338)
        hy = kid.head.matrix_world.to_euler().z
        nose = Vector((math.sin(hy), -math.cos(hy), 0.0))
        cp = cam.matrix_world.translation
        to_cam = Vector((cp.x - eye.x, cp.y - eye.y, 0.0)).normalized()
        off = math.degrees(math.acos(max(-1.0, min(1.0, nose.dot(to_cam)))))
        wb = _box([st.cast["watcher_dg"].head])
        wx = [proj(cam, (x, y, z)) for x in (wb[0], wb[3]) for y in (wb[1], wb[4]) for z in (wb[2], wb[5])]
        print("[dg_probe]   gaps 1300-1357 (px at 540x960): %s" % " ".join("%.0f" % g for g in gaps))
        print("[dg_probe] WALK_CAM end %s: smallest flesh-head gap %.1f px at %d; at 1338 child eyes x %.1f y %.1f, "
              "head %.0f deg off the lens; his head box x %.0f..%.0f y %.0f..%.0f"
              % (label, worst_gap, at, *proj(cam, eye), off, min(p[0] for p in wx), max(p[0] for p in wx),
                 min(p[1] for p in wx), max(p[1] for p in wx)))
    s = S["dg21_crouch"]
    for f in (1358, 1400, 1440):
        scene.frame_set(f)
        fb = _box(flesh.copies)
        pts = [proj(s.camera, (x, y, z)) for x in (fb[0], fb[3]) for y in (fb[1], fb[4]) for z in (fb[2], fb[5])]
        print("[dg_probe] dg21 %d: the flesh's place would be at x %.0f..%.0f y %.0f..%.0f" % (
            f, min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog="tools.hello_door_gold_probe")
    ap.add_argument("cmd", choices=("door", "variant", "check"))
    ap.add_argument("--cams", help="check: candidate WALK_CAM end positions 'x,y,z>tx,ty,tz;...'")
    ap.add_argument("--frames", default="226")
    ap.add_argument("--exec")
    ap.add_argument("--res", default="540x960")
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--zones", action="store_true")
    ap.add_argument("--name", default="hello_dg_var")
    ap.add_argument("--dir", default=os.path.join(ROOT, "out", "test"))
    args = ap.parse_args(argv)
    return {"door": cmd_door, "variant": cmd_variant, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
