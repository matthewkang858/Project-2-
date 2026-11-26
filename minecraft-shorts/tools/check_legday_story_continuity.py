"""Checker probe (story, words, time): continuity across cuts on a built film (gold sky; keys exist in every build).

    $BPY -m tools.check_legday_story_continuity
Prints: the patrol's position in rd15 / tp18 / rd19 on the frames that matter; the chip state of the day anvils
after rd19 against the dusk set and the held anvils; the cl11 / cl22 and cl12 / cl23 repeats (camera and climbers,
frame for frame); Zuri's bucket across pn04 / pn05 / pn06.
"""
import math
import sys
import time


def main(argv):
    import render
    t = time.time()
    ses = render.Session("legday", sky=argv[0] if argv else "gold")
    print("[check] built in %.1f s" % (time.time() - t))
    scene = ses.scene
    st = ses.result["stage"]
    C = ses.result["context"]
    cast = st.cast

    def pos(c, f):
        p = c.pos_at(f)
        return (round(p.x, 2), round(p.y, 2), round(p.z, 2))

    # --- the patrol
    for tag, frames in (("rd15", (891, 903, 913, 944)), ("tp18", (1103, 1108, 1123, 1141)),
                        ("rd19", (944, 984, 1061, 1103, 1108, 1123, 1141, 1142, 1169, 1210))):
        cap = cast.get("patrol_%s_1" % tag)
        last = cast.get("patrol_%s_5" % tag)
        if cap is None:
            print("no patrol", tag)
            continue
        for f in frames:
            try:
                print("patrol %-5s f%4d captain %s  fifth %s" % (tag, f, pos(cap, f), pos(last, f)))
            except Exception as e:
                print("patrol", tag, f, "pos_at failed:", e)
    # --- the anvils' chips
    print("memo keys:", list(C.memo))
    try:
        import bpy
        for i, a in enumerate(C.anvils):
            names = []
            for ob in getattr(a, "objects", lambda: [])() if callable(getattr(a, "objects", None)) else []:
                names.append(ob.name)
            print("day anvil", i, a.name, getattr(a, "block_id", None), getattr(a, "state", None))
    except Exception as e:
        print("anvil probe:", e)
    for i, a in enumerate(C.anvils_dusk):
        print("dusk anvil", i, a.name, getattr(a, "block_id", getattr(a, "bid", None)))
    # --- repeats
    def cam_at(f):
        scene.frame_set(f)
        c = scene.camera
        return c.matrix_world.copy(), c.data.lens

    for a, b in (("cl11_climb", "cl22_dusk"), ("cl12_legday", "cl23_legday")):
        sa = next(s for s in ses.film.shots if s.name == a)
        sb = next(s for s in ses.film.shots if s.name == b)
        n = min(sa.frame_end - sa.frame_start, sb.frame_end - sb.frame_start) + 1
        worst = 0.0
        for k in range(0, n, 4):
            ma, la = cam_at(sa.frame_start + k)
            mb, lb = cam_at(sb.frame_start + k)
            d = (ma.translation - mb.translation).length
            ang = math.degrees(ma.to_quaternion().rotation_difference(mb.to_quaternion()).angle)
            worst = max(worst, d + ang / 10)
            if k in (0, 4, n - 1 - (n - 1) % 4):
                print("  %s+%d vs %s+%d: cam d %.4f, %.3f deg, lens %.1f / %.1f" % (a, k, b, k, d, ang, la, lb))
        print("repeat %s / %s: %d frames compared, worst %.4f" % (a, b, n, worst))
        ta = {"cl11_climb": "cl", "cl22_dusk": "cl3", "cl12_legday": "cl2", "cl23_legday": "cl4"}
        for role in ("steve", "kai", "zuri", "ari"):
            ca, cb = cast.get("%s_%s" % (role, ta[a])), cast.get("%s_%s" % (role, ta[b]))
            if ca is None or cb is None:
                continue
            diffs = [math.dist(pos(ca, sa.frame_start + k), pos(cb, sb.frame_start + k)) for k in range(n)]
            print("   %s: max position difference %.3f" % (role, max(diffs)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
