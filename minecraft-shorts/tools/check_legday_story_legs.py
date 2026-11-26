"""Checker probe: how much the legs move in the leg-day shots (cl11, cl12; the dusk repeats are the same) against a
player walking (4.317 blocks/s), and the frames per stair step.

    $BPY -m tools.check_legday_story_legs
"""
import math
import sys


def main(argv):
    import render
    ses = render.Session("legday", sky="gold")
    scene = ses.scene
    st = ses.result["stage"]
    for name, a, b in (("steve_cl", 669, 738), ("steve_cl2", 739, 783), ("kai_cl2", 739, 783),
                       ("steve_rd", 945, 996), ("steve_tp", 853, 902)):
        c = st.cast[name]
        leg = c.parts["leg_r"]
        vals = []
        for f in range(a, b + 1):
            scene.frame_set(f)
            vals.append(math.degrees(leg.rotation_euler[0]))
        p0, p1 = c.pos_at(a), c.pos_at(b)
        dist = (p1 - p0).length
        hor = math.hypot(p1.x - p0.x, p1.y - p0.y)
        print("%-10s %d-%d: leg swing %.1f .. %.1f deg (peak-to-peak %.1f); moved %.2f blocks (%.2f horizontal) = %.2f b/s horizontal; "
              "frames per stair step %.1f" % (name, a, b, min(vals), max(vals), max(vals) - min(vals), dist, hor,
                                             hor / ((b - a) / 24.0), (b - a) / max(hor, 1e-6)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
