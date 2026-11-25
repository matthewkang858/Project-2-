"""Checker probe 2 for The Hello: every cast member of every shot (projection, occlusion, face size), the map
north of house_a, dropped item object types.   $BPY -m tools.check_hello_technical_probe2
"""
import math
import sys


def main(argv):
    import bpy
    import render
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    from tools.check_hello_technical_probe import first_visible_hit
    ses = render.Session("hello", sky="gold")
    st, C, scene = ses.result["stage"], ses.result["context"], ses.scene
    w = C.v.world
    fl = st.cast["rotten_flesh_dg"]
    print("[p2] flesh objects:", [(o.name, o.type) for o in fl.objects()])
    order = sorted(ses.film.shots, key=lambda s: s.frame_start)
    for s in order:
        for f in (s.frame_start + 2, (s.frame_start + s.frame_end) // 2, s.frame_end):
            scene.frame_set(f)
            cam = s.camera
            scene.camera = cam
            dg = bpy.context.evaluated_depsgraph_get()
            pos = cam.matrix_world.translation.copy()
            out = []
            for n in sorted(st.in_shot.get(s.name, ())):
                c = st.cast[n]
                if not hasattr(c, "head"):
                    continue
                try:
                    eye = Vector(c.eye_point(f))
                except Exception:
                    eye = c.head.matrix_world.translation + Vector((0, 0, 0.25))
                co = world_to_camera_view(scene, cam, eye)
                hit = first_visible_hit(scene, dg, pos, eye, f)
                # face size in px at 540x960: half a block head (player/villager head 8 px = 0.5) projected
                d = (eye - pos).length
                sensor = cam.data.sensor_width
                # vertical frame (fit AUTO on the larger side = height): px per unit at distance d
                ppu = 960 * cam.data.lens / (sensor * d)
                own = hit is None or hit.startswith(n)
                out.append("%s x%.0f y%.0f d%.1f face%dpx %s" % (n, co.x * 100, (1 - co.y) * 100, co.z,
                                                                   int(0.5 * ppu), "clear" if own else "BLOCKED by " + hit))
            print("[p2] %-14s f%4d  %s" % (s.name, f, " | ".join(out)))
    print("\n[p2] MAP x -2..14, y 0..20 (north at top), z=0 and z=1")
    sym = {}
    for z in (0, 1):
        print("  z=%d x: %s" % (z, "".join(str(abs(x) % 10) for x in range(-2, 15))))
        for y in range(20, -1, -1):
            row = ""
            for x in range(-2, 15):
                b = w.block_id(x, y, z)
                row += "." if b is None else sym.setdefault(b, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop"[len(sym)])
            print("  y%3d %s" % (y, row))
    print("  legend:", {v: k for k, v in sym.items()})
    # candidate spots for watch_far: clear feet / head cells and line of sight from house_fronts
    s = next(x for x in order if x.name == "dg15_a")
    scene.frame_set(930)
    dg = bpy.context.evaluated_depsgraph_get()
    pos = s.camera.matrix_world.translation.copy()
    for cand in ((8.3, 14.6), (7.6, 14.6), (7.4, 14.0), (7.0, 15.0), (8.0, 13.2), (7.5, 12.5), (8.4, 5.2), (8.9, -5.4)):
        z = C.stand(cand)[2]
        cells = [w.block_id(int(math.floor(cand[0] + dx)), int(math.floor(cand[1] + dy)), int(math.floor(z + 0.05)) + dz)
                 for dx in (-0.3, 0.3) for dy in (-0.3, 0.3) for dz in (0, 1)]
        eye = Vector((cand[0], cand[1], z + 1.62))
        co = world_to_camera_view(scene, s.camera, eye)
        print("[p2] watch candidate %s z %.3f cells %s  view x%.0f y%.0f  hit %s" % (
            cand, z, sorted(set(str(c) for c in cells)), co.x * 100, (1 - co.y) * 100,
            first_visible_hit(scene, dg, pos, eye, 930)))
    # in17: where would the watcher have to stand to be seen through the pane
    s = next(x for x in order if x.name == "in17_window")
    for f in (1050, 1075, 1100):
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        pos = s.camera.matrix_world.translation.copy()
        for cand in ((3.4, -6.7), (0.0, -5.0), (-4.0, -3.0)):
            z = C.stand(cand)[2]
            for hz in (0.3, 1.0, 1.62):
                p = Vector((cand[0], cand[1], z + hz))
                co = world_to_camera_view(scene, s.camera, p)
                print("[p2] in17 f%d spot %s +%.2f view x%.0f y%.0f hit %s" % (f, cand, hz, co.x * 100, (1 - co.y) * 100,
                                                                         first_visible_hit(scene, dg, pos, p, f)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
