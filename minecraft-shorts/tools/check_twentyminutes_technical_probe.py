"""Independent technical probe of "Twenty Minutes" (checker's tool; writes nothing but its log on stdout).

    $BPY -m tools.check_twentyminutes_technical_probe [--no-keys]

1. builds the film strict, wrapping every shot function to diff ALL keyframes before / after it: keys a shot writes
   outside its own frames (leaks into other shots) or removes / changes there;
2. visibility of every cast member at the first, middle and last frames of every shot vs st.in_shot;
3. Mom's head on the zombie (keyed yaw / pitch vs the bearing to C.zombie_eye) every frame of every pod shot;
4. cameras: the block at the lens, solid blocks within the clip distance, the heroes' head boxes in the frame;
5. things that change on camera: bed2, the top step, the door of house_c, the golem, the items, the swap;
6. the zombie / the pod's people visible from shots that do not use them.
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    import importlib

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    from engine import shots as SH
    from films import twentyminutes as TM
    from tools.twentyminutes_geo import first_hit, head_box

    os.environ["TWENTYMINUTES_STRICT"] = "1"
    TM.STRICT = True
    do_keys = "--no-keys" not in argv

    def snap():
        out = {}
        for ob in bpy.data.objects:
            ids = [ob]
            if ob.data is not None and getattr(ob.data, "animation_data", None) is not None:
                ids.append(ob.data)
            for idb in ids:
                for fc in SH.fcurves_of(idb):
                    key = (ob.name if idb is ob else "data:" + ob.name, fc.data_path, fc.array_index)
                    out[key] = {round(k.co.x, 3): round(k.co.y, 4) for k in fc.keyframe_points}
        return out

    records = {}
    if do_keys:
        seq_of = {name: seq for name, _b, seq, _sky, _st in TM.SHOTS}
        for name, seq in seq_of.items():
            m = importlib.import_module(TM.SEQUENCE_FILES[seq])
            fn = getattr(m, name)

            def wrapped(st, s, C, nar, fn=fn, name=name):
                a = snap()
                fn(st, s, C, nar)
                b = snap()
                lo, hi = s.frame_start - 0.5, s.frame_end + 1.0
                out = []
                for key in set(a) | set(b):
                    ka, kb = a.get(key, {}), b.get(key, {})
                    for f in set(ka) | set(kb):
                        if f <= 1.0 or lo <= f <= hi:
                            continue
                        if ka.get(f) != kb.get(f):
                            out.append((key, f, ka.get(f), kb.get(f)))
                records[name] = out
            setattr(m, name, wrapped)

    import render
    t = time.time()
    ses = render.Session("twentyminutes")
    print("[probe] built in %.1f s" % (time.time() - t))
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = list(ses.film.shots)
    byname = {s.name: s for s in shots}

    def shot_of(f):
        for s in shots:
            if s.frame_start <= f <= s.frame_end + 0.999:
                return s
        return None

    owner = {}
    for cname, c in st.cast.items():
        obs = c.objects() if callable(getattr(c, "objects", None)) else []
        for ob in obs:
            owner[ob.name] = cname
            for ch in getattr(ob, "children_recursive", []):
                owner.setdefault(ch.name, cname)

    # ---------------------------------------------------------------- 1. key leaks
    if do_keys:
        print("\n== 1. keys written / changed by a shot function OUTSIDE its own frames (frames > 1)")
        for s in shots:
            out = records.get(s.name, [])
            if not out:
                continue
            groups = {}
            for (obn, path, idx), f, va, vb in out:
                who = owner.get(obn.replace("data:", ""), obn)
                tgt = shot_of(f)
                tname = tgt.name if tgt else "none"
                used = tgt is not None and who in st.in_shot.get(tname, ())
                g = groups.setdefault((who, path, tname, used), [])
                g.append((f, va, vb))
            print("  %s (%d-%d): %d keys" % (s.name, s.frame_start, s.frame_end, len(out)))
            for (who, path, tname, used), fl in sorted(groups.items(), key=lambda kv: min(x[0] for x in kv[1])):
                fs = sorted(x[0] for x in fl)
                print("     %-28s %-34s frames %7.2f..%7.2f (%3d) in %-12s %s" % (
                    who[:28], path[:34], fs[0], fs[-1], len(fs), tname,
                    "<-- USED THERE" if used else ""))

    # ---------------------------------------------------------------- 2. visibility
    print("\n== 2. visibility (rendered meshes) vs st.in_shot at first / middle / last frames")

    def visible(c):
        obs = c.objects() if callable(getattr(c, "objects", None)) else []
        meshes = [o for o in obs if o.type == "MESH"]
        return any(not o.hide_render for o in meshes) if meshes else None

    probe_frames = {}
    for s in shots:
        probe_frames[s.name] = sorted({s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end})
    mism = []
    for s in shots:
        for f in probe_frames[s.name]:
            scene.frame_set(f)
            for cname, c in st.cast.items():
                v = visible(c)
                if v is None:
                    continue
                want = cname in st.in_shot.get(s.name, ())
                if v != want:
                    mism.append((s.name, f, cname, v, want))
    for m in mism:
        print("  %-12s f %4d  %-22s visible %s, in_shot %s" % m)
    print("  %d mismatches" % len(mism))

    # ---------------------------------------------------------------- 3. Mom's head on the zombie
    print("\n== 3. Mom's head vs the bearing to the zombie's eyes (keyed values, every frame)")
    from engine import characters as ch
    ze = Vector(C.zombie_eye)
    pod_shots = [s for s in shots if s.frame_start >= byname["sq04_hat"].frame_start]
    for s in pod_shots:
        for cname in sorted(st.in_shot.get(s.name, ())):
            if not cname.startswith("mom_"):
                continue
            c = st.cast[cname]
            worst = (0.0, None, 0.0)
            for f in range(s.frame_start, s.frame_end + 1):
                eye = c.eye_point(f)
                d = ze - eye
                bearing = math.atan2(d.x, -d.y)
                yaw = c.yaw_at(f) + ch._val(c.head, "rotation_euler", 2, f)
                err = abs(((bearing - yaw) + math.pi) % (2 * math.pi) - math.pi)
                pitch = -ch._val(c.head, "rotation_euler", 0, f)
                want_p = math.atan2(d.z, math.hypot(d.x, d.y))
                if math.degrees(err) > worst[0]:
                    worst = (math.degrees(err), f, math.degrees(pitch - want_p))
            print("  %-12s %-8s worst yaw error %5.1f deg at %s (pitch error there %5.1f)" % (
                s.name, cname, worst[0], worst[1], worst[2]))

    # ---------------------------------------------------------------- 4. cameras
    print("\n== 4. cameras: block at the lens / within 0.06; heroes in the frame (x 8-82, y 14-60)")
    w = C.v.world

    def solid(p):
        b = w.block_id(int(math.floor(p[0])), int(math.floor(p[1])), int(math.floor(p[2])))
        return b

    for s in shots:
        for f in probe_frames[s.name]:
            scene.frame_set(f)
            cam = s.camera
            scene.camera = cam
            cp = cam.matrix_world.translation.copy()
            b0 = solid(cp)
            near = set()
            for dx in (-0.06, 0.06):
                for dy in (-0.06, 0.06):
                    for dz in (-0.06, 0.06):
                        bb = solid((cp.x + dx, cp.y + dy, cp.z + dz))
                        if bb:
                            near.add(bb)
            heroes = []
            for label, obs in st.heroes.get(s.name, []):
                for ob in obs:
                    pts = []
                    for o in [ob] + list(ob.children_recursive):
                        if o.type != "MESH":
                            continue
                        for corner in o.bound_box:
                            pts.append(o.matrix_world @ Vector(corner))
                    if not pts:
                        continue
                    pr = [world_to_camera_view(scene, cam, p) for p in pts]
                    xs = [p.x * 100 for p in pr]
                    ys = [(1 - p.y) * 100 for p in pr]
                    hid = all(o.hide_render for o in [ob] + list(ob.children_recursive) if o.type == "MESH")
                    flag = ""
                    if min(xs) < 8 or max(xs) > 82 or min(ys) < 14 or max(ys) > 60:
                        flag = " OUT"
                    if hid:
                        flag += " HIDDEN"
                    heroes.append("%s x%3.0f-%3.0f y%3.0f-%3.0f%s" % (label, min(xs), max(xs), min(ys), max(ys), flag))
            print("  %-12s f %4d cam (%6.2f,%6.2f,%5.2f) %4.0fmm block %-10s near %-14s | %s" % (
                s.name, f, cp.x, cp.y, cp.z, cam.data.lens, b0, ",".join(sorted(near)) or "-", "; ".join(heroes)))

    # ---------------------------------------------------------------- 5. parts that change
    print("\n== 5. parts that change on camera")
    P = C.P_

    def vis_of(obj_list, f):
        scene.frame_set(f)
        return [not o.hide_render for o in obj_list if o.type == "MESH"]

    bed2 = P.bed2.objects()
    for f in (485, 1033, 1255, 1256, 1290, 1303, 1304, 1305, 1338, 1400, 1473, 1542):
        print("  bed2 f %4d (%s): rendered %s" % (f, shot_of(f).name, vis_of(bed2, f)))
    ts = P.top_step
    tso = ts.objects() if callable(getattr(ts, "objects", None)) else []
    for f in (1, 772, 900, 1210, 1256, 1337, 1338, 1344, 1350, 1356, 1360, 1399, 1400, 1473):
        print("  top_step f %4d (%s): rendered %s" % (f, shot_of(f).name, vis_of(tso, f)))
    try:
        doors = C.v._door_sets["house_c"]
        for f in (1, 20, 30, 40, 45, 50, 55, 60, 70, 87, 187, 229):
            scene.frame_set(f)
            print("  house_c door f %3d: yaw %s" % (f, [round(math.degrees(d.rotation_euler[2]), 1) for d in doors]))
    except Exception as e:
        print("  door: %r" % e)
    g = st.cast.get("golem")
    if g is not None:
        for s in shots:
            if not s.name.startswith("gm"):
                continue
            row = []
            for f in range(s.frame_start, s.frame_end + 1):
                scene.frame_set(f)
                v = visible(g)
                p = g.pos_at(f)
                row.append((f, v, round(p.x, 2), round(p.y, 2), round(p.z, 2)))
            # print changes only
            last = None
            out = []
            for f, v, x, y, z in row:
                state = (v, x, y, z)
                if last is None or v != last[0] or (abs(x - last[1]) > 0.3) or abs(z - last[3]) > 0.3 \
                        or f in (s.frame_start, s.frame_end):
                    out.append("%d:%s(%.2f,%.2f,%.2f)" % (f, "V" if v else "h", x, y, z))
                    last = state
            print("  golem %s: %s" % (s.name, " ".join(out)))
    for cname in ("baby_gr", "narrator_gr"):
        c = st.cast[cname]
        vs = []
        for f in (1143, 1176, 1177, 1178, 1179, 1209):
            scene.frame_set(f)
            vs.append("%d:%s" % (f, visible(c)))
        print("  swap %s: %s" % (cname, " ".join(vs)))
    for cname in sorted(n for n in st.cast if n.startswith(("iron_ingot", "poppy"))):
        c = st.cast[cname]
        vs = []
        for f in (707, 708, 712, 718, 724, 730, 740, 750, 760, 771, 772):
            scene.frame_set(f)
            vs.append("%d:%s" % (f, "V" if visible(c) else "h"))
        print("  item %-14s %s" % (cname, " ".join(vs)))

    # ---------------------------------------------------------------- 6. who is missing from the picture
    print("\n== 6. the zombie and the pod's places seen from shots that do not use them (mid frame)")
    spots = {"zombie_eye": tuple(ze), "mom": tuple(Vector(C.P("mom")) + Vector((0, 0, 1.6))),
             "back_1": tuple(Vector(C.P("back_1")) + Vector((0, 0, 1.6))),
             "row_2": tuple(Vector(C.P("row_2")) + Vector((0, 0, 1.6))),
             "mom_glass": tuple(Vector(C.P("mom_glass")) + Vector((0, 0, 1.6)))}
    for s in shots:
        f = (s.frame_start + s.frame_end) // 2
        scene.frame_set(f)
        cam = s.camera
        scene.camera = cam
        dg = bpy.context.evaluated_depsgraph_get()
        cp = cam.matrix_world.translation.copy()
        used = st.in_shot.get(s.name, ())
        zomb = any(n.startswith("zombie_") for n in used)
        anyone = [n for n in used if n.split("_")[0] in ("mom", "cleric", "librarian", "narrator", "baby")]
        out = []
        for label, p in spots.items():
            co = world_to_camera_view(scene, cam, Vector(p))
            if co.z <= 0 or not (0 <= co.x <= 1 and 0 <= co.y <= 1):
                continue
            hit = first_hit(scene, dg, cp, Vector(p))
            out.append("%s x%3.0f y%3.0f d%4.1f %s" % (label, co.x * 100, (1 - co.y) * 100, (Vector(p) - cp).length,
                                                     hit or "CLEAR"))
        if out:
            print("  %-12s f %4d zombie used %-5s pod people used %-30s | %s" % (
                s.name, f, zomb, ",".join(sorted(anyone))[:30], "; ".join(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
