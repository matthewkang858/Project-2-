"""Leg Day, the climb sequence's own state check: the tools.legday_state checks that concern cl11 / cl12 / cl22 /
cl23, alone (the whole of legday_state needs more than the 300 s a command may take on the loaded machine), plus the
feet on the treads. One build (any sky: every shot is built in every build).

    $BPY -m tools.legday_climb_check [--sky gold]
Checks: the repeats frame for frame, cameras included (cl22 = cl11 over 70 frames, cl23 = cl12 over 45: every
climber, not only Steve and Kai); the legs (swing 50 degrees or more, a step every 7 frames or more); no climber
inside a solid block (every frame); every climber's feet ON a tread (the root's world z = the game's half step under
it, within 0.01) on every frame; nobody tops out. Exit 1 on a failure.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SHOTS = ("cl11_climb", "cl12_legday", "cl22_dusk", "cl23_legday")
REPEATS = (("cl11_climb", "cl22_dusk", 70), ("cl12_legday", "cl23_legday", 45))


def main(argv):
    """See the module docstring."""
    import argparse
    ap = argparse.ArgumentParser(prog="tools.legday_climb_check")
    ap.add_argument("--sky", default="gold")
    args = ap.parse_args(argv)
    import render
    ses = render.Session("legday", sky=args.sky)
    from films import legday_set as LS
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    T = C.T
    W = C.v.world
    bad = []

    def check(ok, text):
        print("[climb_check] %s %s" % ("ok  " if ok else "FAIL", text))
        if not ok:
            bad.append(text)

    def climbers(shot):
        return sorted(n for n in st.in_shot.get(shot, ()) if n.split("_")[-1].startswith("cl"))

    # one pass over every frame of the four shots: positions, cameras, legs, blocks, treads
    rec = {}
    inside, off_tread, worst_tread = {}, {}, 0.0
    for shot in SHOTS:
        r = T[shot]
        names = climbers(shot)
        rec[shot] = []
        for f in range(r.frame_start, r.frame_end + 1):
            scene.frame_set(f)
            cam = scene.camera
            row = {"cam": cam.matrix_world.copy(), "lens": cam.data.lens}
            for n in names:
                c = st.cast[n]
                p = c.root.matrix_world.translation.copy()
                row[n.rsplit("_", 1)[0]] = (p, math.degrees(c.parts["leg_r"].rotation_euler[0]))
                for h in (0.15, 0.9, 1.5):
                    if LS._solid_at(W, p.x, p.y, p.z + h):
                        inside.setdefault((shot, n), []).append(f)
                        break
                if LS.STAIR_Y0 <= p.y <= LS.STAIR_Y0 + LS.STEPS:
                    d = abs(p.z - LS.stair_z(p.y))
                    worst_tread = max(worst_tread, d)
                    if d > 0.01:
                        off_tread.setdefault((shot, n), []).append((f, round(d, 3)))
            rec[shot].append(row)
        print("[climb_check] %s: %s, frames %d-%d" % (shot, ", ".join(names), r.frame_start, r.frame_end))
    for (shot, n), fs in sorted(inside.items()):
        check(False, "%s: %s inside a solid block on frames %s" % (shot, n, fs[:6]))
    check(not inside, "no climber inside a solid block (every frame of the four shots)")
    for (shot, n), fs in sorted(off_tread.items()):
        check(False, "%s: %s's feet off the treads: %s" % (shot, n, fs[:6]))
    check(not off_tread, "every climber's feet on a tread on every frame (largest gap %.4f)" % worst_tread)
    for shot in SHOTS:
        r = T[shot]
        for n in climbers(shot):
            role = n.rsplit("_", 1)[0]
            sw = [abs(row[role][1]) for row in rec[shot][6:]]
            p0, p1 = rec[shot][0][role][0], rec[shot][-1][role][0]
            per_step = (r.frame_end - r.frame_start) / max(abs(p1.y - p0.y), 1e-6)
            check(max(sw) >= 50.0 and per_step >= 7.0,
                  "%s: %s's legs swing up to %.0f degrees, a step every %.1f frames; feet y %.2f -> %.2f (step %.2f "
                  "-> %.2f of %d)" % (shot, n, max(sw), per_step, p0.y, p1.y, p0.y - LS.STAIR_Y0,
                                      p1.y - LS.STAIR_Y0, LS.STEPS))
            check(p1.y - LS.STAIR_Y0 < LS.STEPS - 0.25, "%s: %s does not top out" % (shot, n))
    for a, b, n in REPEATS:
        dev = 0.0
        roles = [k for k in rec[a][0] if k not in ("cam", "lens")]
        check(sorted(roles) == sorted(k for k in rec[b][0] if k not in ("cam", "lens")),
              "%s has the same climbers as %s (%s)" % (b, a, ", ".join(sorted(roles))))
        for k in range(n):
            ra, rb = rec[a][k], rec[b][k]
            for role in roles:
                dev = max(dev, (ra[role][0] - rb[role][0]).length, abs(ra[role][1] - rb[role][1]) / 100.0)
            ca, cb = ra["cam"], rb["cam"]
            dev = max(dev, (ca.translation - cb.translation).length,
                      max(abs(ca[i][j] - cb[i][j]) for i in range(3) for j in range(3)), abs(ra["lens"] - rb["lens"]))
        check(dev < 1e-3, "%s repeats %s frame for frame over %d frames, every climber and the camera (largest "
              "difference %.5f)" % (b, a, n, dev))
    print("[climb_check] %d failure(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
