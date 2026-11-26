"""Twenty Minutes: measure the BUILT film without rendering it (the lead's probe; after the two reviews of the plan).
One strict build of the one sky, then:

    $BPY -m tools.twentyminutes_probe                 # every section
    $BPY -m tools.twentyminutes_probe looks heroes    # some of them: events looks heroes cams missing

  events   things that change on camera, as built: the golem's visibility and position in every gm shot (the frames
           where it changes), the dropped items (first / last visible frame), the second bed's first frame, the swap
           (baby_gr / narrator_gr), the top step, house_c's door
  looks    every villager in a pod shot (sq04_hat on) whose head must be on the zombie (Mom always; everybody C.pod
           placed): the worst angle between where its head REALLY points (the evaluated head, tremble and clamp
           included) and the zombie's eyes, every frame of the shot
  heroes   every hero's head box at the first, middle and last frame, in % of the frame (x 8-82, y 14-60 is the safe
           area; OUT marks a box outside it; the caption band is y 62-72)
  cams     the camera's heading / pitch (degrees) and what it is aimed at, at five frames of every shot that moves
  missing  the zombie's eyes and the pod's places projected into shots that do not use them (CLEAR = nothing in
           front of it: someone should be there)
Nothing is written. Prefix with `nice -n 15 timeout 290`. (Sections 3-6 of the technical review's
tools/check_twentyminutes_technical_probe.py, re-done with the evaluated head instead of the keyed values.)
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SECTIONS = ("events", "looks", "heroes", "cams", "missing")


def main(argv):
    want = [a for a in argv if a in SECTIONS] or list(SECTIONS)
    os.environ["TWENTYMINUTES_STRICT"] = "1"

    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    import render
    from tools.twentyminutes_geo import first_hit

    ses = render.Session("twentyminutes")
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    shots = list(ses.film.shots)
    by = {s.name: s for s in shots}

    def shot_of(f):
        return next((s for s in shots if s.frame_start <= f <= s.frame_end), None)

    def visible(c):
        obs = c.objects() if callable(getattr(c, "objects", None)) else []
        meshes = [o for o in obs if o.type == "MESH"]
        return any(not o.hide_render for o in meshes) if meshes else None

    def proj(cam, p):
        co = world_to_camera_view(scene, cam, Vector(p))
        return co.x * 100.0, (1.0 - co.y) * 100.0, co.z

    if "events" in want:
        print("\n== events")
        g = st.cast.get("golem")
        for s in shots:
            if g is None or not s.name.startswith("gm"):
                continue
            out, last = [], None
            for f in range(s.frame_start, s.frame_end + 1):
                scene.frame_set(f)
                v, p = visible(g), g.pos_at(f)
                if last is None or v != last[0] or abs(p.x - last[1]) > 0.3 or abs(p.z - last[2]) > 0.3 \
                        or f == s.frame_end:
                    out.append("%d:%s(%.2f,%.2f,%.2f)" % (f, "V" if v else "h", p.x, p.y, p.z))
                    last = (v, p.x, p.z)
            print("  golem %-12s %s" % (s.name, " ".join(out)))
        items = sorted(n for n in st.cast if n.startswith(("iron_ingot", "poppy")))
        seen = {n: [] for n in items}
        for f in range(700, 775):
            scene.frame_set(f)
            for n in items:
                if visible(st.cast[n]):
                    seen[n].append(f)
        for n in items:
            print("  item %-14s visible %s" % (n, "%d-%d" % (seen[n][0], seen[n][-1]) if seen[n] else "never (700-774)"))
        if "gm_deliver" in C.memo:
            print("  gm12 deliver plans (landed, gone): %s" % (C.memo["gm_deliver"],))
        bed2 = [o for o in C.P_.bed2.objects() if o.type == "MESH"]
        rows = []
        for f in (1, 485, 1033, 1255, 1256, 1300, 1302, 1303, 1304, 1305, 1337, 1338, 1400, 1473, 1542):
            scene.frame_set(f)
            rows.append("%d:%s" % (f, "V" if any(not o.hide_render for o in bed2) else "h"))
        print("  bed2 %s" % " ".join(rows))
        for name in ("baby_gr", "narrator_gr"):
            c = st.cast.get(name)
            if c is None:
                continue
            vs = []
            for f in (1176, 1177, 1178, 1179):
                scene.frame_set(f)
                vs.append("%d:%s" % (f, "V" if visible(c) else "h"))
            print("  swap %-12s %s" % (name, " ".join(vs)))

    if "looks" in want:
        print("\n== looks: the head's real direction vs the zombie's eyes (worst over the shot; degrees)")
        ze = Vector(C.zombie_eye)
        for s in shots:
            if s.frame_start < by["sq04_hat"].frame_start:
                continue
            names = [n for n in sorted(st.in_shot.get(s.name, ()))
                     if n.split("_")[0] in ("mom", "cleric", "librarian", "narrator", "baby")]
            worst = {n: (0.0, None) for n in names}
            for f in range(s.frame_start, s.frame_end + 1, 2):
                scene.frame_set(f)
                for n in names:
                    c = st.cast[n]
                    if not visible(c):
                        continue
                    m = c.head.matrix_world
                    fwd = (m.to_3x3() @ Vector((0.0, -1.0, 0.0)))
                    fwd.z = 0.0
                    d = ze - m.translation
                    d.z = 0.0
                    if fwd.length < 1e-6 or d.length < 1e-6:
                        continue
                    a = math.degrees(fwd.angle(d))
                    if a > worst[n][0]:
                        worst[n] = (a, f)
            for n in names:
                flag = "  <-- off the zombie" if worst[n][0] > 12 and n.startswith("mom_") else ""
                print("  %-12s %-14s worst %5.1f at %s%s" % (s.name, n, worst[n][0], worst[n][1], flag))

    if "heroes" in want:
        print("\n== heroes: head boxes x / y %% at the first, middle and last frame (safe x 8-82, y 14-60)")
        for s in shots:
            frames = sorted({s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end})
            rows = []
            for f in frames:
                scene.frame_set(f)
                cam = s.camera
                scene.camera = cam
                cells = []
                for label, obs in st.heroes.get(s.name, []):
                    pts = []
                    for ob in obs:
                        for o in [ob] + list(ob.children_recursive):
                            if o.type == "MESH" and not o.hide_render:
                                pts += [o.matrix_world @ Vector(cn) for cn in o.bound_box]
                    if not pts:
                        cells.append("%s hidden" % label)
                        continue
                    pr = [proj(cam, p) for p in pts]
                    xs, ys = [p[0] for p in pr], [p[1] for p in pr]
                    out = min(xs) < 8 or max(xs) > 82 or min(ys) < 14 or max(ys) > 60
                    cells.append("%s x%.0f-%.0f y%.0f-%.0f%s" % (label, min(xs), max(xs), min(ys), max(ys),
                                                                 " OUT" if out else ""))
                rows.append("%d: %s" % (f, "; ".join(cells)))
            print("  %-12s %s" % (s.name, " | ".join(rows)))

    if "cams" in want:
        print("\n== cams: heading (degrees ccw from east) / pitch at five frames of every moving shot")
        for s in shots:
            frames = [s.frame_start + int(round(k * (s.frame_end - s.frame_start) / 4.0)) for k in range(5)]
            vals = []
            for f in frames:
                scene.frame_set(f)
                m = s.camera.matrix_world
                d = m.to_3x3() @ Vector((0.0, 0.0, -1.0))
                vals.append((f, math.degrees(math.atan2(d.y, d.x)), math.degrees(math.asin(max(-1, min(1, d.z))))))
            if max(v[1] for v in vals) - min(v[1] for v in vals) < 1.0 and \
                    max(v[2] for v in vals) - min(v[2] for v in vals) < 1.0:
                continue
            print("  %-12s %s" % (s.name, "  ".join("%d: %.1f / %+.1f" % v for v in vals)))

    if "missing" in want:
        print("\n== missing: the zombie / the pod's places in shots that do not use them (middle frame)")
        ze = Vector(C.zombie_eye)
        spots = {"zombie_eye": ze}
        for p in ("mom", "back_1", "back_3", "row_2", "mom_glass", "bed_side"):
            spots[p] = Vector(C.P(p)) + Vector((0, 0, 1.6))
        for s in shots:
            f = (s.frame_start + s.frame_end) // 2
            scene.frame_set(f)
            cam = s.camera
            scene.camera = cam
            dg = bpy.context.evaluated_depsgraph_get()
            cp = cam.matrix_world.translation.copy()
            used = st.in_shot.get(s.name, ())
            out = []
            for label, p in spots.items():
                if label == "zombie_eye" and any(n.startswith("zombie_") for n in used):
                    continue
                x, y, z = proj(cam, p)
                if z <= 0 or not (0 <= x <= 100 and 0 <= y <= 100):
                    continue
                hit = first_hit(scene, dg, cp, p)
                out.append("%s x%.0f y%.0f %s" % (label, x, y, hit or "CLEAR"))
            if out:
                print("  %-12s f %4d  %s" % (s.name, f, "; ".join(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
