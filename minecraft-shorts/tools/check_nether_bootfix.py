"""Reviewer's probe: the 'boot' camera suggestion moved out of the guard stair (x 0.35 -> 2.3), same aim and lens."""
import os
import sys


def main():
    import render as R
    from tools import check_nether_film as P

    P.register()
    ses = R.Session(P.FILM)
    bas = P.INFO["bas"]
    s = next(x for x in ses.film.shots if x.name == "b5_boot")
    cam = s.camera
    c = bas.cameras["boot"]
    from mathutils import Vector
    pos = Vector((2.3, c["pos"][1], c["pos"][2]))
    # re-aim the shot camera (one static shot)
    s.move(tuple(pos), c["target"])
    ses.configure((540, 960), 16, 2, None)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ses.render_frame(s.frame_start + 6, os.path.join(root, "out", "test", "check_nether_b5_fixed.png"))
    print("[bootfix] rendered", tuple(round(v, 2) for v in pos), "camera", cam.name)


if __name__ == "__main__":
    main()
