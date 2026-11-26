"""Independent checker probe 3 for "Leg Day": the shared helpers keyed on scratch instances and read back, the exact
repeats cl11 = cl22 and cl12 = cl23 (camera and climbers frame by frame), the narrator's slim arms.

    $BPY -m tools.check_legday_technical_probe3
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    import render
    ses = render.Session("legday", sky="gold")
    import bpy
    from mathutils import Vector
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    T = C.T
    # ---- 1. the exact repeats
    for a, b in (("cl11_climb", "cl22_dusk"), ("cl12_legday", "cl23_legday")):
        ra, rb = T[a], T[b]
        n = min(ra.frames, rb.frames)
        worst_cam, worst_rot = 0.0, 0.0
        for k in range(n):
            ses.film.goto(ra.frame_start + k)
            ma = scene.camera.matrix_world.copy()
            la = scene.camera.data.lens
            fa = scene.camera.data.dof.focus_distance
            ses.film.goto(rb.frame_start + k)
            mb = scene.camera.matrix_world.copy()
            lb = scene.camera.data.lens
            fb = scene.camera.data.dof.focus_distance
            worst_cam = max(worst_cam, (ma.translation - mb.translation).length)
            worst_rot = max(worst_rot, max(abs(x - y) for x, y in zip(ma.to_euler(), mb.to_euler())))
        print("[probe3] %s vs %s: %d vs %d frames; camera max pos diff %.5f, rot diff %.5f rad, lens %.1f/%.1f focus %.3f/%.3f"
              % (a, b, ra.frames, rb.frames, worst_cam, worst_rot, la, lb, fa, fb))
        ta = sorted(x for x in st.in_shot[a] if hasattr(st.cast[x], "root"))
        tb = sorted(x for x in st.in_shot[b] if hasattr(st.cast[x], "root"))
        for na in ta:
            role = na.split("_")[0]
            nb = next((x for x in tb if x.split("_")[0] == role), None)
            if nb is None:
                print("   %s has no twin in %s" % (na, b))
                continue
            ca, cb = st.cast[na], st.cast[nb]
            worst = 0.0
            for k in range(n):
                scene.frame_set(ra.frame_start + k)
                pa = ca.root.matrix_world.translation.copy()
                ha = ca.head.matrix_world.translation.copy()
                scene.frame_set(rb.frame_start + k)
                pb = cb.root.matrix_world.translation.copy()
                hb = cb.head.matrix_world.translation.copy()
                worst = max(worst, (pa - pb).length, (ha - hb).length)
            print("   %-10s = %-10s max diff %.5f" % (na, nb, worst))
    # ---- 2. slim arms
    for name in sorted(st.cast):
        c = st.cast[name]
        if not name.startswith(("efe_", "steve_", "zuri_", "kai_", "ari_")):
            continue
        arm = getattr(c, "arm_l", None)
        if arm is None:
            continue
        meshes = [arm] + [o for o in arm.children_recursive if o.type == "MESH"]
        xs = []
        for o in meshes:
            if o.type != "MESH":
                continue
            for v in o.data.vertices:
                xs.append((o.matrix_world @ v.co))
        scene.frame_set(1)
        print("   %-14s slim=%s" % (name, getattr(c, "slim", "?")), end="")
        print("" if not xs else "  arm_l local width %.3f" % (max(v.x for v in xs) - min(v.x for v in xs)), end="")
        print("  skin=%s" % getattr(c, "skin", "?"))
    # ---- 3. helpers on scratch instances
    s = C.shots["sq01_squats"]
    p = C.actor("steve", "sqprobe")
    C.put(p, s.frame_start, "squat_steve", toward=(0.0, -12.0))
    scene.frame_set(s.frame_start)
    print("[probe3] C.put squat_steve toward (0,-12): pos %s yaw %.1f deg (yaw_to %.1f)" % (
        tuple(round(v, 3) for v in p.pos_at(s.frame_start)), math.degrees(p.yaw_at(s.frame_start)),
        math.degrees(C.st and __import__("films.lookdev", fromlist=["yaw_to"]).yaw_to(C.P("squat_steve"), (0.0, -12.0)))))
    # to_lens: target due east of the head, camera due south: result 21 degrees toward the camera
    eye = p.eye_point(s.frame_start)
    tgt = (eye.x + 5.0, eye.y, eye.z)
    cam = (eye.x, eye.y - 5.0, eye.z)
    r = C.to_lens(p, s.frame_start, tgt, cam, degrees=21.0)
    ang = math.degrees(math.atan2(r[1] - eye.y, r[0] - eye.x))
    print("[probe3] to_lens: target east, camera south -> look direction %.1f deg (want -21.0), dist %.2f" % (
        ang, math.hypot(r[0] - eye.x, r[1] - eye.y)))
    # stand on a dirt path / grass
    for q in ((0.5, 30.0), (-0.55, -5.55), (-10.0, 18.0), (1.45, 46.9), (1.45, 49.25)):
        z = C.stand(q)[2]
        bid = C.v.world.block_id(int(math.floor(q[0])), int(math.floor(q[1])), int(round(C.v.ground(*q))) - 1)
        print("[probe3] stand %s -> z %.4f (block under %s)" % (q, z, bid))
    # fill: prefix, mismatch, visibility
    try:
        C.fill("xx_bad", (0, 0, 5), 10.0, [s])
        print("[probe3] fill with a bad prefix: NO ERROR")
    except KeyError:
        print("[probe3] fill with a bad prefix: KeyError (ok)")
    lamp = C.fill("sq_probe", (0.0, -6.0, 3.0), 10.0, [s])
    try:
        C.fill("sq_probe", (0.0, -6.0, 3.5), 10.0, [s])
        print("[probe3] fill mismatch: NO ERROR")
    except ValueError:
        print("[probe3] fill mismatch: ValueError (ok)")
    states = []
    for f in (1, 36, 72, 73, 200):
        scene.frame_set(f)
        states.append((f, lamp.hide_render))
    print("[probe3] fill sq_probe on sq01 (1-72) hide_render: %s" % states)
    # appear outside its shot
    try:
        C.appear(C.shots["tp14_why"], C.anvils[11], 700)
        print("[probe3] appear outside the shot: NO ERROR")
    except ValueError:
        print("[probe3] appear outside the shot: ValueError (ok)")
    # stuck arrow: visible in its shot only
    arr = C.stuck_arrow(C.shots["rd16_punch"], (0.5, 41.0, 0.0), (0.0, -0.6, -0.8), frame=980)
    obs = arr.objects() if callable(getattr(arr, "objects", None)) else (arr.objects if hasattr(arr, "objects") else [arr])
    vis = []
    for f in (945, 979, 980, 996, 997, 1100):
        scene.frame_set(f)
        vis.append((f, any(not o.hide_render for o in obs if o.type == "MESH")))
    print("[probe3] stuck_arrow rd16 from 980: visible %s" % vis)
    # cam: default handheld seed per shot name, shared seed
    print("[probe3] CAMS climb %s" % {k: v for k, v in C.camera_spec("climb").items()})
    print("[probe3] CAMS legs %s" % {k: v for k, v in C.camera_spec("legs").items()})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
