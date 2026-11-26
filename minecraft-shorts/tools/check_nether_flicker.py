"""Reviewer's probe: how much the documented beat-18 flicker (bas.lava["home_channels"].flicker) changes the gate frame."""
import os
import sys


def main():
    import render as R
    from tools import check_nether_film as P

    P.register()
    ses = R.Session(P.FILM)
    bas = P.INFO["bas"]
    f0, f1 = P.INFO["b18"]
    sc = ses.scene
    ch = bas.lava["home_channels"]
    lights = list(getattr(ch, "lights", []))
    wall = bas.lava["home_lava_wall_light"]
    rows = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        rows.append((f, sum(o.data.energy for o in lights), wall.data.energy))
    e = [r[1] for r in rows]
    print("[flicker] channel lights: %d, energy %.0f..%.0f W; lava wall light %.0f W (constant: %s)"
          % (len(lights), min(e), max(e), wall.data.energy, len({r[2] for r in rows}) == 1))
    lo = min(rows, key=lambda r: r[1])[0]
    hi = max(rows, key=lambda r: r[1])[0]
    print("[flicker] min at frame", lo, "max at frame", hi)
    if "render" in sys.argv:
        ses.configure((540, 960), 16, 2, None)
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for tag, f in (("lo", lo), ("hi", hi)):
            ses.render_frame(f, os.path.join(root, "out", "test", "check_nether_flicker_%s.png" % tag))
        print("[flicker] rendered")


if __name__ == "__main__":
    main()
