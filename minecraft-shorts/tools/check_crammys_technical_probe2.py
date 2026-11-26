"""Checker's probe 2 for The Crammys: door keys, the pedestal in shots without the totem, the double goat horn,
jb18's walk end, helper read-backs on a scratch instance. Prints only."""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    import render
    from engine import shots as SH
    from tools.check_crammys_technical_probe import hidden
    from tools.crammys_geo import first_hit

    ses = render.Session("crammys", sky="night")
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    film = ses.film
    shots = sorted(film.shots, key=lambda s: s.frame_start)

    # door keys
    for d in C.v._door_sets["house_e"]:
        ks = [(round(k.co[0], 1), round(math.degrees(k.co[1]), 1)) for fc in SH.fcurves_of(d)
              for k in fc.keyframe_points if fc.data_path == "rotation_euler"]
        print("[probe2] house_e door %s keys (frame, deg): %s" % (d.name, ks))
    for d in C.v._door_sets.get("house_f", []):
        ks = [(round(k.co[0], 1), round(math.degrees(k.co[1]), 1)) for fc in SH.fcurves_of(d)
              for k in fc.keyframe_points]
        print("[probe2] house_f door %s keys: %s" % (d.name, ks))

    # the pedestal top (with the totem height) in every shot: in frame? the totem shown?
    top = Vector(C.bd.pedestal_top) if getattr(C.bd, "pedestal_top", None) is not None else Vector((-8.5, -0.5, 2.0))
    tot = st.cast.get("music_totem")
    print("[probe2] pedestal top %s" % (tuple(top),))
    for s in shots:
        cam = s.camera
        scene.camera = cam
        out = []
        for f in range(s.frame_start, s.frame_end + 1, max(1, (s.frame_end - s.frame_start) // 6)):
            scene.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            p = top + Vector((0, 0, 0.35))
            co = world_to_camera_view(scene, cam, p)
            x, y = co.x * 100, (1 - co.y) * 100
            if co.z > 0 and -5 <= x <= 105 and -5 <= y <= 105:
                blk = first_hit(scene, dg, cam.matrix_world.translation.copy(), p,
                                own={o.name for o in tot.objects()} if tot is not None and hasattr(tot, "objects")
                                else ())
                vis = (tot is not None and any(not hidden(o, f) for o in tot.objects())) if tot is not None and hasattr(
                    tot, "objects") else None
                out.append("f%d %.0f,%.0f %s totem %s" % (f, x, y, "clear" if blk is None else "blocked " + blk,
                                                          "shown" if vis else "HIDDEN"))
        if out:
            print("  %-18s %s" % (s.name, " | ".join(out)))

    # Noor's horns in gd06
    no = st.cast["noor_gd"]
    f = 470
    scene.frame_set(f)
    for h in no._hands["r"]:
        for vn, at in h.variants.items():
            print("[probe2] noor_gd %s %s start %s end %s visible@470 %s matrix %s" % (
                h.item_id, vn or "-", h.start, h.end, not hidden(at.ob, f),
                tuple(round(v, 3) for v in at.ob.matrix_world.translation)))

    # jb18: where is Steve on "Nobody" / when does his walk end
    p = st.cast["steve_jb"]
    s = C.shots["jb18_nobody_asked"]
    path = C.v.paths["bandstand_wing_to_three"][2:]
    L = sum(math.dist(a[:2], b[:2]) for a, b in zip(path, path[1:]))
    print("[probe2] jb18 path from point 2: %s, length %.2f -> walk %.1f frames at 1.6 b/s (shot %d frames); pos on "
          "Nobody %s" % ([tuple(round(v, 2) for v in q) for q in path], L, L / 1.6 * 24, s.frame_end - s.frame_start + 1,
                         tuple(round(v, 2) for v in p.pos_at(C.T["jb18_nobody_asked"].at("Nobody")))))

    # helper read-backs on a scratch instance (registered under a scratch tag, never in a shot)
    sc = C.actor("steve", "fnzz")
    s = C.shots["fn24_vocals"]
    sc.place(s.frame_start, (-30.0, -30.0, 0.0), 0.0)
    ob = C.hold(sc, "music_disc_11", s)
    vis = [(f, not hidden(ob, f)) for f in (s.frame_start - 1, s.frame_start, s.frame_end, s.frame_end + 1)]
    print("[probe2] C.hold scratch (player hidden in every shot): disc visible at %s (expected all False: the twin "
          "is in no shot)" % vis)
    ok = C.arrows(sc, s)
    ok2 = C.arrows(sc, s)
    print("[probe2] C.arrows first call %s, second call %s (idempotent)" % (ok, ok2))
    try:
        C.actor("steve", "xx")
    except KeyError as e:
        print("[probe2] bad tag refused:", e)
    try:
        C.fill("zz_bad", (0, 0, 0), 10, [s])
    except KeyError as e:
        print("[probe2] bad fill name refused:", e)
    lamp = C.fill("fn_test", (-30, -30, 3), 5.0, [s])
    print("[probe2] fill hidden before/in/after fn24: %s" % [hidden(lamp, f) for f in (s.frame_start - 1,
                                                                                       s.frame_start, s.frame_end)])
    # C.turn_to on a scratch: body yaw after the ease
    sc2 = C.actor("steve", "fnzy")
    sc2.place(s.frame_start, (-30.0, -30.0, 0.0), 0.0)
    e = C.turn_to(sc2, s.frame_start + 2, (-30.0, -20.0, 1.6), ease=10)
    print("[probe2] turn_to: body yaw at %d = %.1f deg (target due +Y: 180)" % (
        e, math.degrees(sc2.yaw_at(e)) % 360))
    # time_jump: do particles born after it survive? (song notes of fn21 exist after time_jump(1265))
    from engine import fx
    print("[probe2] fx.stop_particles doc: %s" % (fx.stop_particles.__doc__ or "").strip()[:400])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
