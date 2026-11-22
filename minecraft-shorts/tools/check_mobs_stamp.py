"""Independent checker: is the scene fingerprint (engine/stamp.py) of a film that uses engine/mobs.py stable from
one process to the next?  Run twice:  $BPY -m tools.check_mobs_stamp"""
import sys


def main():
    from engine import quick, stamp
    from tools import check_mobs_film

    scene = quick.reset()
    film, st, cast = check_mobs_film.build(scene)
    fp = stamp.Fingerprinter(scene, film)
    for f in (1, 40, 85, 100, 150, 173, 180, 220):
        r = fp.frame(f)
        print("FP", f, r["fp"], r["parts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
