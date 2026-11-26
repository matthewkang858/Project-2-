"""Checker probe: sq08_arms body yaws against the lens (the arm comparison needs both bodies square to the lens).

    $BPY -m tools.check_legday_story_arms
"""
import math
import sys


def main(argv):
    import render
    ses = render.Session("legday", sky="gold")
    scene = ses.scene
    st = ses.result["stage"]
    for f in (431, 438, 450, 470, 500, 519):
        scene.frame_set(f)
        cam = scene.camera.matrix_world.translation
        for name in ("efe_sq", "steve_sq3"):
            c = st.cast[name]
            p = c.pos_at(f)
            yaw = c.yaw_at(f)
            # a character faces -Y at yaw 0 (legday_common.yaw_to); its facing vector:
            fx, fy = math.sin(yaw) * -1.0, -math.cos(yaw)
            fx2, fy2 = -math.sin(-yaw), -math.cos(-yaw)
            to = (cam.x - p.x, cam.y - p.y)
            n = math.hypot(*to)
            a1 = math.degrees(math.acos(max(-1, min(1, (fx * to[0] + fy * to[1]) / n))))
            a2 = math.degrees(math.acos(max(-1, min(1, (fx2 * to[0] + fy2 * to[1]) / n))))
            print("f%d %-10s pos (%.2f, %.2f) yaw %.1f deg; body off the lens %.1f (or %.1f with the other sign), dist %.2f"
                  % (f, name, p.x, p.y, math.degrees(yaw), a1, a2, n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
